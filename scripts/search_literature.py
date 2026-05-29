"""Search public metadata sources and build a conservative candidate table.

The script only imports metadata. It does not claim novelty, parse full text, or
download restricted PDFs.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


CANDIDATE_FIELDS = [
    "candidate_id",
    "title",
    "authors",
    "year",
    "venue",
    "doi",
    "url",
    "pdf_url",
    "topic",
    "source",
    "source_type",
    "venue_tier",
    "source_trust",
    "query",
    "auto_relevance_score",
    "auto_relevance_label",
    "category",
    "relevance_reason",
    "practical_relevance",
    "practical_evidence_needed",
    "reading_status",
    "access_status",
    "metadata_confidence",
    "added_at",
    "first_seen_at",
    "last_seen_at",
    "source_updated_at",
    "discovery_run_id",
    "status",
    "human_decision",
    "notion_status",
    "zotero_key",
]

QUEUE_FIELDS = [
    "queue_id",
    "candidate_id",
    "title",
    "authors",
    "year",
    "venue",
    "doi",
    "url",
    "topic",
    "reason",
    "requested_action",
    "status",
    "added_at",
]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def stable_id(*parts: str) -> str:
    source = "|".join(part.strip().lower() for part in parts if part)
    return hashlib.sha1(source.encode("utf-8")).hexdigest()[:12]


def normalize_space(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def parse_simple_query_yaml(path: Path) -> dict[str, object]:
    topic = ""
    lists: dict[str, list[str]] = {
        "seed_keywords": [],
        "required_terms_any": [],
        "exclude_terms_any": [],
    }
    current_list = ""
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        stripped = raw_line.strip()
        if stripped.startswith("topic:"):
            topic = stripped.split(":", 1)[1].strip()
            current_list = ""
        elif stripped.endswith(":"):
            current_list = stripped[:-1] if stripped[:-1] in lists else ""
        elif current_list and stripped.startswith("- "):
            lists[current_list].append(stripped[2:].strip())
        elif current_list and stripped and not raw_line.startswith(" "):
            current_list = ""
    if not topic:
        topic = path.stem
    return {"topic": topic, **lists}


def load_csv(path: Path, fields: list[str]) -> list[dict[str, str]]:
    if not path.exists() or path.stat().st_size == 0:
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return [{field: row.get(field, "") for field in fields} for row in reader]


def write_csv(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def fetch_json(url: str) -> dict:
    request = urllib.request.Request(url, headers={"User-Agent": "low-altitude-research-hub/0.1"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def fetch_text(url: str) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": "low-altitude-research-hub/0.1"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8")


def search_openalex(query: str, topic: str, limit: int, from_updated_date: str = "") -> list[dict[str, str]]:
    params_data = {"search": query, "per-page": limit}
    if from_updated_date:
        params_data["filter"] = f"from_updated_date:{from_updated_date}"
    params = urllib.parse.urlencode(params_data)
    data = fetch_json(f"https://api.openalex.org/works?{params}")
    rows = []
    for item in data.get("results", []):
        authors = "; ".join(
            normalize_space(authorship.get("author", {}).get("display_name", ""))
            for authorship in item.get("authorships", [])
            if authorship.get("author", {}).get("display_name")
        )
        locations = item.get("locations") or []
        pdf_url = ""
        for location in locations:
            candidate_pdf = (location.get("pdf_url") or "").strip()
            if candidate_pdf:
                pdf_url = candidate_pdf
                break
        open_access = item.get("open_access") or {}
        access_status = "open" if open_access.get("is_oa") else "needs_user_pdf"
        title = normalize_space(item.get("title", ""))
        doi = (item.get("doi") or "").replace("https://doi.org/", "")
        url = item.get("id", "")
        primary_location = item.get("primary_location") or {}
        primary_source = primary_location.get("source") or {}
        venue = primary_source.get("display_name", "")
        rows.append(make_candidate(title, authors, str(item.get("publication_year") or ""), venue, doi, url, pdf_url, topic, "openalex", query, access_status, item.get("updated_date", "")))
    return rows


def search_crossref(query: str, topic: str, limit: int, from_updated_date: str = "") -> list[dict[str, str]]:
    params_data = {"query": query, "rows": limit}
    if from_updated_date:
        params_data["filter"] = f"from-update-date:{from_updated_date}"
    params = urllib.parse.urlencode(params_data)
    data = fetch_json(f"https://api.crossref.org/works?{params}")
    rows = []
    for item in data.get("message", {}).get("items", []):
        title = normalize_space(" ".join(item.get("title") or []))
        authors = "; ".join(
            normalize_space(" ".join(filter(None, [author.get("given", ""), author.get("family", "")])))
            for author in item.get("author", [])
        )
        year = ""
        date_parts = item.get("published-print", {}).get("date-parts") or item.get("published-online", {}).get("date-parts") or []
        if date_parts and date_parts[0]:
            year = str(date_parts[0][0])
        venue = normalize_space("; ".join(item.get("container-title") or []))
        doi = item.get("DOI", "")
        url = item.get("URL", "")
        indexed = item.get("indexed", {}).get("date-time", "")
        rows.append(make_candidate(title, authors, year, venue, doi, url, "", topic, "crossref", query, "needs_user_pdf", indexed))
    return rows


def search_arxiv(query: str, topic: str, limit: int, from_updated_date: str = "") -> list[dict[str, str]]:
    search_query = urllib.parse.quote(f'all:"{query}"')
    url = f"https://export.arxiv.org/api/query?search_query={search_query}&start=0&max_results={limit}"
    text = fetch_text(url)
    root = ET.fromstring(text)
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    rows = []
    for entry in root.findall("atom:entry", ns):
        title = normalize_space(entry.findtext("atom:title", default="", namespaces=ns))
        authors = "; ".join(
            normalize_space(author.findtext("atom:name", default="", namespaces=ns))
            for author in entry.findall("atom:author", ns)
        )
        published = entry.findtext("atom:published", default="", namespaces=ns)
        year = published[:4] if published else ""
        entry_url = entry.findtext("atom:id", default="", namespaces=ns)
        updated = entry.findtext("atom:updated", default="", namespaces=ns)
        pdf_url = ""
        for link in entry.findall("atom:link", ns):
            if link.attrib.get("title") == "pdf":
                pdf_url = link.attrib.get("href", "")
        rows.append(make_candidate(title, authors, year, "arXiv", "", entry_url, pdf_url, topic, "arxiv", query, "open", updated))
    return rows


def search_semantic_scholar(query: str, topic: str, limit: int, from_updated_date: str = "") -> list[dict[str, str]]:
    fields = "title,authors,year,venue,externalIds,url,openAccessPdf,publicationDate"
    params = urllib.parse.urlencode({"query": query, "limit": limit, "fields": fields})
    headers = {"User-Agent": "low-altitude-research-hub/0.1"}
    api_key = os.environ.get("SEMANTIC_SCHOLAR_API_KEY", "")
    if api_key:
        headers["x-api-key"] = api_key
    request = urllib.request.Request(
        f"https://api.semanticscholar.org/graph/v1/paper/search?{params}",
        headers=headers,
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        data = json.loads(response.read().decode("utf-8"))
    rows = []
    for item in data.get("data", []):
        publication_date = item.get("publicationDate", "")
        if from_updated_date and publication_date and publication_date < from_updated_date:
            continue
        authors = "; ".join(normalize_space(author.get("name", "")) for author in item.get("authors", []) if author.get("name"))
        external_ids = item.get("externalIds") or {}
        doi = external_ids.get("DOI", "")
        pdf = item.get("openAccessPdf") or {}
        pdf_url = pdf.get("url", "") if isinstance(pdf, dict) else ""
        access_status = "open" if pdf_url else "needs_user_pdf"
        rows.append(
            make_candidate(
                normalize_space(item.get("title", "")),
                authors,
                str(item.get("year") or ""),
                item.get("venue", ""),
                doi,
                item.get("url", ""),
                pdf_url,
                topic,
                "semantic_scholar",
                query,
                access_status,
                publication_date,
            )
        )
    return rows


def make_candidate(title: str, authors: str, year: str, venue: str, doi: str, url: str, pdf_url: str, topic: str, source: str, query: str, access_status: str, source_updated_at: str = "") -> dict[str, str]:
    title = normalize_space(title)
    candidate_id = stable_id(doi, url, title)
    added_at = now_iso()
    return {
        "candidate_id": candidate_id,
        "title": title,
        "authors": normalize_space(authors),
        "year": year,
        "venue": normalize_space(venue),
        "doi": doi,
        "url": url,
        "pdf_url": pdf_url,
        "topic": topic,
        "source": source,
        "source_type": "academic_paper",
        "venue_tier": "unknown",
        "source_trust": "medium",
        "query": query,
        "auto_relevance_score": "",
        "auto_relevance_label": "",
        "category": "",
        "relevance_reason": "",
        "practical_relevance": "",
        "practical_evidence_needed": "needs practical validation",
        "reading_status": "metadata only",
        "access_status": access_status,
        "metadata_confidence": "medium" if title and year else "low",
        "added_at": added_at,
        "first_seen_at": added_at,
        "last_seen_at": added_at,
        "source_updated_at": source_updated_at,
        "discovery_run_id": "",
        "status": "candidate",
        "human_decision": "",
        "notion_status": "",
        "zotero_key": "",
    }


def text_contains_any(text: str, terms: list[str]) -> bool:
    lowered = text.lower()
    return any(term.lower() in lowered for term in terms if term)


def relevance_score(row: dict[str, str], required_terms: list[str], excluded_terms: list[str]) -> tuple[int, str, str]:
    text = " ".join([row.get("title", ""), row.get("venue", ""), row.get("query", "")]).lower()
    if excluded_terms and text_contains_any(text, excluded_terms):
        return 0, "excluded", "matched excluded term"
    if required_terms:
        matched = [term for term in required_terms if term.lower() in text]
        if not matched:
            return 0, "off_topic", "no required topic term matched"
        score = len(matched)
    else:
        score = 1
    label = "high" if score >= 2 else "medium"
    return score, label, "auto topic gate"


def apply_relevance_gate(rows: list[dict[str, str]], required_terms: list[str], excluded_terms: list[str]) -> list[dict[str, str]]:
    kept = []
    for row in rows:
        score, label, reason = relevance_score(row, required_terms, excluded_terms)
        if label in {"excluded", "off_topic"}:
            continue
        row["auto_relevance_score"] = str(score)
        row["auto_relevance_label"] = label
        if not row.get("relevance_reason"):
            row["relevance_reason"] = reason
        kept.append(row)
    return kept


def dedupe(rows: Iterable[dict[str, str]]) -> list[dict[str, str]]:
    seen = set()
    unique = []
    for row in rows:
        key = row.get("doi") or row.get("url") or row.get("title")
        key = key.lower().strip()
        if not key or key in seen:
            continue
        seen.add(key)
        unique.append(row)
    return unique


def queue_rows(candidates: list[dict[str, str]]) -> list[dict[str, str]]:
    queued = []
    for row in candidates:
        if row.get("access_status") != "needs_user_pdf":
            continue
        queued.append(
            {
                "queue_id": stable_id("queue", row["candidate_id"]),
                "candidate_id": row["candidate_id"],
                "title": row["title"],
                "authors": row["authors"],
                "year": row["year"],
                "venue": row["venue"],
                "doi": row["doi"],
                "url": row["url"],
                "topic": row["topic"],
                "reason": "No open PDF URL was found by the metadata search.",
                "requested_action": "User should download legally if institutional or personal access is available.",
                "status": "pending",
                "added_at": row["added_at"],
            }
        )
    return queued


def main() -> int:
    parser = argparse.ArgumentParser(description="Search metadata sources for candidate papers.")
    parser.add_argument("--query-file", default="literature/queries/remote_id.yaml", help="Topic query YAML.")
    parser.add_argument("--provider", choices=["openalex", "crossref", "arxiv", "semantic_scholar"], default="openalex", help="Metadata provider.")
    parser.add_argument("--limit", type=int, default=5, help="Max results per keyword.")
    parser.add_argument("--max-keywords", type=int, default=2, help="Max seed keywords to query.")
    parser.add_argument("--output", default="literature/database/paper_candidates.csv", help="Candidate CSV.")
    parser.add_argument("--queue", default="literature/database/acquisition_queue.csv", help="Manual acquisition queue CSV.")
    parser.add_argument("--from-updated-date", default="", help="Optional provider update/publication lower bound in YYYY-MM-DD form.")
    parser.add_argument("--discovery-run-id", default="", help="Stable ID for this discovery run.")
    parser.add_argument("--dry-run", action="store_true", help="Show planned queries without network or writes.")
    args = parser.parse_args()

    query_file = Path(args.query_file)
    if not query_file.exists():
        print(f"Missing query file: {query_file}")
        return 1

    query_data = parse_simple_query_yaml(query_file)
    topic = str(query_data["topic"])
    keywords = list(query_data["seed_keywords"])
    required_terms = list(query_data["required_terms_any"])
    excluded_terms = list(query_data["exclude_terms_any"])
    selected_keywords = keywords[: args.max_keywords]
    if not selected_keywords:
        print(f"No seed keywords found in {query_file}.")
        return 1

    if args.dry_run:
        print(f"Would search {args.provider} for topic '{topic}' using {len(selected_keywords)} keywords:")
        for keyword in selected_keywords:
            print(f"- {keyword}")
        print("Dry run only. No network requests or file writes were performed.")
        return 0

    searchers = {
        "openalex": search_openalex,
        "crossref": search_crossref,
        "arxiv": search_arxiv,
        "semantic_scholar": search_semantic_scholar,
    }

    candidates: list[dict[str, str]] = []
    for keyword in selected_keywords:
        try:
            candidates.extend(searchers[args.provider](keyword, topic, args.limit, args.from_updated_date))
            time.sleep(1)
        except Exception as exc:
            print(f"Search failed for '{keyword}' via {args.provider}: {exc}", file=sys.stderr)

    candidates = apply_relevance_gate(dedupe(candidates), required_terms, excluded_terms)
    if not candidates:
        print("No candidates found.")
        return 0

    output = Path(args.output)
    existing = load_csv(output, CANDIDATE_FIELDS)
    existing_by_id = {row["candidate_id"]: row for row in existing}
    discovery_run_id = args.discovery_run_id or stable_id(args.provider, topic, now_iso())
    now = now_iso()
    new_candidates = []
    for row in candidates:
        row["discovery_run_id"] = discovery_run_id
        row["last_seen_at"] = now
        if row["candidate_id"] in existing_by_id:
            existing_row = existing_by_id[row["candidate_id"]]
            existing_row["last_seen_at"] = now
            existing_row["discovery_run_id"] = discovery_run_id
            if row.get("source_updated_at"):
                existing_row["source_updated_at"] = row["source_updated_at"]
            if row.get("pdf_url") and not existing_row.get("pdf_url"):
                existing_row["pdf_url"] = row["pdf_url"]
                existing_row["access_status"] = "open"
        else:
            row["first_seen_at"] = now
            row["added_at"] = row.get("added_at") or now
            new_candidates.append(row)

    queue_path = Path(args.queue)
    existing_queue = load_csv(queue_path, QUEUE_FIELDS)
    existing_queue_ids = {row["queue_id"] for row in existing_queue}
    new_queue = [row for row in queue_rows(new_candidates) if row["queue_id"] not in existing_queue_ids]

    write_csv(output, CANDIDATE_FIELDS, existing + new_candidates)
    write_csv(queue_path, QUEUE_FIELDS, existing_queue + new_queue)

    print(f"Added {len(new_candidates)} candidates to {output}.")
    print(f"Added {len(new_queue)} items to {queue_path}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
