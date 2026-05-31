"""Shared utilities for the lightweight research-intelligence workflow.

The new mainline uses one JSONL item store, concise Chinese notes, weekly
digests, and on-demand topic synthesis. It deliberately avoids the older
candidate/review/acquisition CSV state machine.
"""

from __future__ import annotations

import base64
import hashlib
import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
import uuid
import xml.etree.ElementTree as ET
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Iterable


ITEMS_PATH = Path("data/items.jsonl")
MANUAL_ITEMS_PATH = Path("data/manual_items.jsonl")
DEFAULT_CONFIG = Path("configs/pipeline.json")
USER_AGENT = "low-altitude-research-hub/0.2"
NEEDS_TOPIC_REVIEW = "needs_topic_review"
ITEM_STATUSES = {
    "new",
    "kept",
    "rejected",
    "downloaded",
    "read",
    "summarized",
    "used_in_synthesis",
}
REVIEW_STATUSES = {"new", "kept", "rejected", "downloaded"}
PROCESS_STATUSES = {"unread", "read", "summarized", "used_in_synthesis"}
STATUS_RANK = {
    "new": 0,
    "kept": 1,
    "downloaded": 2,
    "read": 3,
    "summarized": 4,
    "used_in_synthesis": 5,
    "rejected": 99,
}
PROCESS_RANK = {
    "unread": 0,
    "read": 1,
    "summarized": 2,
    "used_in_synthesis": 3,
}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def today_string() -> str:
    return date.today().isoformat()


def stable_id(*parts: str) -> str:
    source = "|".join(str(part).strip().lower() for part in parts if str(part).strip())
    return hashlib.sha1(source.encode("utf-8")).hexdigest()[:12]


def slugify(value: str) -> str:
    chars: list[str] = []
    for char in value.lower():
        if char.isalnum():
            chars.append(char)
        elif chars and chars[-1] != "_":
            chars.append("_")
    return "".join(chars).strip("_") or "item"


def safe_filename(value: str, fallback: str = "item", max_length: int = 140) -> str:
    value = normalize_space(value)
    value = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", value)
    value = re.sub(r"\s+", " ", value).strip(" ._")
    if not value:
        value = fallback
    if len(value) > max_length:
        value = value[:max_length].rstrip(" ._")
    return value or fallback


def normalize_space(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def normalize_match_text(value: str) -> str:
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def token_set(value: str) -> set[str]:
    stop = {"a", "an", "and", "for", "in", "of", "on", "the", "to", "with", "using", "use"}
    return {token for token in normalize_match_text(value).split() if len(token) > 2 and token not in stop}


def title_similarity(left: str, right: str) -> float:
    import difflib

    left_norm = normalize_match_text(left)
    right_norm = normalize_match_text(right)
    if not left_norm or not right_norm:
        return 0.0
    sequence_score = difflib.SequenceMatcher(None, left_norm, right_norm).ratio()
    left_tokens = token_set(left_norm)
    right_tokens = token_set(right_norm)
    overlap_score = 0.0
    if left_tokens and right_tokens:
        overlap_score = len(left_tokens & right_tokens) / len(left_tokens | right_tokens)
    return max(sequence_score, overlap_score)


def load_env_file(path: Path = Path(".env")) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def load_config(path: Path = DEFAULT_CONFIG) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def parse_simple_query_yaml(path: Path) -> dict[str, object]:
    topic = ""
    description = ""
    lists: dict[str, list[str]] = {
        "seed_keywords": [],
        "required_terms_any": [],
        "exclude_terms_any": [],
    }
    current_list = ""
    if not path.exists():
        return {"topic": path.stem, "description": "", **lists}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        stripped = raw_line.strip()
        if stripped.startswith("topic:"):
            topic = stripped.split(":", 1)[1].strip()
            current_list = ""
        elif stripped.startswith("description:"):
            description = stripped.split(":", 1)[1].strip()
            current_list = ""
        elif stripped.endswith(":"):
            current_list = stripped[:-1] if stripped[:-1] in lists else ""
        elif current_list and stripped.startswith("- "):
            lists[current_list].append(stripped[2:].strip())
        elif current_list and stripped and not raw_line.startswith(" "):
            current_list = ""
    return {"topic": topic or path.stem, "description": description, **lists}


def topic_key_to_query_files(config: dict) -> dict[str, Path]:
    return {str(key): Path(str(value)) for key, value in (config.get("topics") or {}).items()}


def topic_key_to_slug(config: dict) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for key, query_file in topic_key_to_query_files(config).items():
        mapping[key] = str(parse_simple_query_yaml(query_file)["topic"])
    return mapping


def selected_query_files(topic: str, config: dict) -> list[Path]:
    query_files = topic_key_to_query_files(config)
    if topic == "all":
        return list(query_files.values())
    slug_map = topic_key_to_slug(config)
    if topic in query_files:
        return [query_files[topic]]
    for key, slug in slug_map.items():
        if topic == slug:
            return [query_files[key]]
    candidate = Path(f"literature/queries/{topic}.yaml")
    return [candidate]


def topic_vocabulary(config: dict) -> dict[str, set[str]]:
    vocabulary: dict[str, set[str]] = {}
    for _key, query_file in topic_key_to_query_files(config).items():
        query_data = parse_simple_query_yaml(query_file)
        topic = str(query_data["topic"])
        terms: set[str] = set()
        for field in ["topic", "description"]:
            terms.update(token_set(str(query_data.get(field, ""))))
        for field in ["seed_keywords", "required_terms_any"]:
            for value in query_data.get(field, []) or []:
                terms.update(token_set(str(value)))
        if terms:
            vocabulary[topic] = terms
    return vocabulary


def infer_topic_for_pdf(path: Path, config: dict, min_score: float = 0.08) -> tuple[str, float, str]:
    """Suggest a known topic from PDF title/text, or mark it for human review."""
    title = extract_pdf_title(path) or path.stem
    visible = extract_pdf_visible_text(path, max_bytes=700_000)
    tokens = token_set(f"{path.stem} {title} {visible[:4000]}")
    if not tokens:
        return NEEDS_TOPIC_REVIEW, 0.0, "no usable PDF text"
    scores: list[tuple[float, str, int, int]] = []
    for topic, terms in topic_vocabulary(config).items():
        if not terms:
            continue
        overlap = tokens & terms
        score = len(overlap) / max(len(terms), 1)
        scores.append((score, topic, len(overlap), len(terms)))
    if not scores:
        return NEEDS_TOPIC_REVIEW, 0.0, "no configured topic vocabulary"
    best_score, best_topic, matched, total = max(scores, key=lambda row: row[0])
    if best_score < min_score:
        return NEEDS_TOPIC_REVIEW, best_score, f"low topic match: {matched}/{total} terms"
    return best_topic, best_score, f"matched {matched}/{total} configured topic terms"


def read_jsonl(path: Path) -> list[dict]:
    if not path.exists() or path.stat().st_size == 0:
        return []
    rows: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def write_jsonl(path: Path, rows: Iterable[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = "\n".join(json.dumps(row, ensure_ascii=False, sort_keys=True) for row in rows)
    path.write_text(text + ("\n" if text else ""), encoding="utf-8")


def load_items(path: Path = ITEMS_PATH) -> list[dict]:
    return read_jsonl(path)


def load_manual_items(path: Path = MANUAL_ITEMS_PATH) -> list[dict]:
    rows = read_jsonl(path)
    normalized: list[dict] = []
    for row in rows:
        if not row.get("id"):
            row["id"] = item_id(row.get("url", ""), row.get("title", ""))
        row.setdefault("source", "manual")
        row.setdefault("source_type", "paper")
        row.setdefault("review_status", "new")
        row.setdefault("process_status", "unread")
        row = sync_status_fields(row)
        row.setdefault("created_at", now_iso())
        row["updated_at"] = now_iso()
        normalized.append(row)
    return normalized


def item_id(url: str = "", title: str = "", doi: str = "") -> str:
    return stable_id(doi, url, title)


def review_status(item: dict) -> str:
    value = item.get("review_status")
    if value in REVIEW_STATUSES:
        return value
    legacy = item.get("status")
    if legacy in REVIEW_STATUSES:
        return legacy
    metadata_value = (item.get("metadata") or {}).get("review_status")
    if metadata_value in REVIEW_STATUSES:
        return metadata_value
    return "new"


def process_status(item: dict) -> str:
    value = item.get("process_status")
    if value in PROCESS_STATUSES:
        return value
    legacy = item.get("status")
    if legacy in {"read", "summarized", "used_in_synthesis"}:
        return legacy
    metadata = item.get("metadata") or {}
    if metadata.get("summary_status") == "summarized":
        return "summarized"
    if metadata.get("reading_status") in {"read", "full-text parsed"}:
        return "read"
    return "unread"


def sync_status_fields(item: dict) -> dict:
    item["review_status"] = review_status(item)
    item["process_status"] = process_status(item)
    item["status"] = item["process_status"] if item["process_status"] != "unread" else item["review_status"]
    return item


def make_item(
    *,
    title: str,
    url: str,
    source: str,
    source_type: str,
    topic: str,
    date_value: str = "",
    abstract_or_snippet: str = "",
    pdf_url: str = "",
    score: int = 1,
    tags: list[str] | None = None,
    metadata: dict | None = None,
) -> dict:
    metadata = metadata or {}
    doi = str(metadata.get("doi", ""))
    created = now_iso()
    item = {
        "id": item_id(url, title, doi),
        "title": normalize_space(title),
        "url": url,
        "source": source,
        "source_type": source_type,
        "topic": topic,
        "date": date_value,
        "abstract_or_snippet": normalize_space(abstract_or_snippet),
        "pdf_url": pdf_url,
        "status": "new",
        "review_status": "new",
        "process_status": "unread",
        "score": score,
        "tags": tags or [],
        "created_at": created,
        "updated_at": created,
        "metadata": metadata,
    }
    authority, reason = source_authority_score(item)
    item["authority_score"] = authority
    item["metadata"]["authority_reason"] = reason
    return sync_status_fields(item)


def source_authority_score(item: dict) -> tuple[int, str]:
    """Heuristic source authority score, not a paper-quality judgment."""
    metadata = item.get("metadata") or {}
    source_type = str(item.get("source_type", "")).lower()
    text = " ".join(
        str(value)
        for value in [
            item.get("source", ""),
            item.get("url", ""),
            metadata.get("venue", ""),
            metadata.get("publisher", ""),
            metadata.get("doi", ""),
            metadata.get("provider", ""),
        ]
        if value
    ).lower()

    if source_type in {"standard", "policy"}:
        return 5, "standard/policy source type"
    if source_type in {"whitepaper", "report"}:
        if any(term in text for term in ["icao", "easa", "faa", "etsi", "3gpp", "itu", "ieee", "nist", "gov", "europa.eu"]):
            return 5, "recognized standards/government/technical report source"
        return 4, "whitepaper/report source type"
    if source_type == "news":
        if any(term in text for term in ["reuters", "associated press", "apnews", "bbc", "nature.com", "science.org"]):
            return 4, "recognized news/science outlet"
        return 2, "news source; requires corroboration"

    if any(term in text for term in ["ieee transactions", "acm transactions", "nature", "science", "cell"]):
        return 5, "top-tier journal family or transactions venue"
    if any(term in text for term in ["ieee", "acm", "usenix", "sigcomm", "mobicom", "infocom", "10.1109", "10.1145"]):
        return 4, "recognized society/conference source"
    if any(term in text for term in ["elsevier", "springer", "wiley", "taylor & francis", "sage"]):
        return 3, "established academic publisher; venue quality still needs review"
    if any(term in text for term in ["arxiv", "preprint", "mdpi", "hindawi"]):
        return 2, "preprint or mixed-confidence publisher; needs corroboration"
    return 1, "unknown or weakly characterized source"


def merge_item(existing: dict, incoming: dict) -> dict:
    existing = sync_status_fields(dict(existing))
    incoming = sync_status_fields(dict(incoming))
    merged = dict(existing)
    for key, value in incoming.items():
        if key in {"created_at", "status", "review_status", "process_status"}:
            continue
        if value not in ("", None, [], {}):
            merged[key] = value
    if review_status(existing) != "new":
        merged["review_status"] = review_status(existing)
    else:
        merged["review_status"] = review_status(incoming)
    existing_process = process_status(existing)
    incoming_process = process_status(incoming)
    merged["process_status"] = existing_process if PROCESS_RANK[existing_process] >= PROCESS_RANK[incoming_process] else incoming_process
    merged["created_at"] = existing.get("created_at") or incoming.get("created_at") or now_iso()
    merged["updated_at"] = now_iso()
    existing_tags = set(existing.get("tags") or [])
    incoming_tags = set(incoming.get("tags") or [])
    merged["tags"] = sorted(existing_tags | incoming_tags)
    metadata = dict(existing.get("metadata") or {})
    metadata.update(incoming.get("metadata") or {})
    merged["metadata"] = metadata
    authority, reason = source_authority_score(merged)
    merged["authority_score"] = max(int(merged.get("authority_score") or 0), authority)
    merged["metadata"].setdefault("authority_reason", reason)
    return sync_status_fields(merged)


def upsert_items(incoming_items: Iterable[dict], path: Path = ITEMS_PATH) -> tuple[list[dict], list[dict]]:
    existing = load_items(path)
    by_id = {row["id"]: row for row in existing if row.get("id")}
    changed_or_new: list[dict] = []
    for item in incoming_items:
        item = sync_status_fields(item)
        authority, reason = source_authority_score(item)
        item["authority_score"] = authority
        item.setdefault("metadata", {})["authority_reason"] = reason
        if not item.get("id"):
            item["id"] = item_id(item.get("url", ""), item.get("title", ""), str((item.get("metadata") or {}).get("doi", "")))
        if item["id"] in by_id:
            by_id[item["id"]] = merge_item(by_id[item["id"]], item)
        else:
            item = sync_status_fields(item)
            item.setdefault("created_at", now_iso())
            item["updated_at"] = now_iso()
            by_id[item["id"]] = item
        changed_or_new.append(by_id[item["id"]])
    rows = sorted(by_id.values(), key=lambda row: (row.get("topic", ""), row.get("date", ""), row.get("title", "")), reverse=True)
    write_jsonl(path, rows)
    return rows, changed_or_new


def update_item(item: dict, path: Path = ITEMS_PATH) -> None:
    rows = load_items(path)
    by_id = {row["id"]: row for row in rows if row.get("id")}
    item = sync_status_fields(item)
    item["updated_at"] = now_iso()
    authority, reason = source_authority_score(item)
    item["authority_score"] = authority
    item.setdefault("metadata", {})["authority_reason"] = reason
    item = sync_note_filename(item)
    by_id[item["id"]] = item
    write_jsonl(path, sorted(by_id.values(), key=lambda row: (row.get("topic", ""), row.get("date", ""), row.get("title", "")), reverse=True))


def find_existing_note_for_pdf(pdf_path: Path, items: list[dict] | None = None) -> dict | None:
    """Return an item with an existing note for this PDF path/hash, if known."""
    items = items if items is not None else load_items()
    fingerprint = ""
    try:
        fingerprint = sha256_file(pdf_path)
    except OSError:
        pass
    resolved = str(pdf_path)
    for item in items:
        note_path = item.get("note_path", "")
        if not note_path or not Path(note_path).exists():
            continue
        metadata = item.get("metadata") or {}
        if fingerprint and metadata.get("pdf_fingerprint") == fingerprint:
            return item
        if str(metadata.get("pdf_source", "")) == resolved:
            return item
    if fingerprint:
        for note_path in Path("notes/items").glob("*.md"):
            text = note_path.read_text(encoding="utf-8", errors="ignore")
            if fingerprint in text:
                return {"id": note_path.stem, "note_path": str(note_path), "metadata": {"pdf_fingerprint": fingerprint}}
    return None


def prepare_pdf_item(pdf_path: Path, topic: str, providers: list[str], lookup_limit: int) -> tuple[dict, float, str]:
    item, confidence, reason = lookup_pdf_item(pdf_path, topic, providers, lookup_limit)
    item["topic"] = topic
    item["source"] = item.get("source") or "local_pdf"
    item["source_type"] = "paper"
    item["review_status"] = "downloaded"
    item.setdefault("tags", [])
    if "local-pdf" not in item["tags"]:
        item["tags"].append("local-pdf")
    if topic == NEEDS_TOPIC_REVIEW and "needs-topic-review" not in item["tags"]:
        item["tags"].append("needs-topic-review")
    metadata = item.setdefault("metadata", {})
    metadata["pdf_source"] = str(pdf_path)
    metadata["pdf_fingerprint"] = sha256_file(pdf_path)
    metadata["metadata_match_confidence"] = round(confidence, 3)
    metadata["metadata_match_reason"] = reason
    return sync_status_fields(item), confidence, reason


def read_pdf_to_note(pdf_path: Path, item: dict, config: dict, timeout: int) -> tuple[dict, Path, str]:
    note, model = kimi_read_pdf(pdf_path, item, config, timeout)
    if not note.strip():
        raise RuntimeError("Kimi returned an empty note.")
    item["process_status"] = "summarized"
    item["updated_at"] = now_iso()
    note_path = write_item_note(item, note, pdf_path, model)
    item["note_path"] = str(note_path)
    metadata = item.setdefault("metadata", {})
    metadata["pdf_fingerprint"] = sha256_file(pdf_path)
    metadata["reading_status"] = "read"
    metadata["summary_status"] = "summarized"
    item = sync_status_fields(item)
    all_items, _ = upsert_items([item])
    write_review_dashboard(all_items)
    return item, note_path, model


def fetch_json(url: str, timeout: int = 30) -> dict:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def fetch_text(url: str, timeout: int = 30) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read().decode("utf-8")


def text_contains_any(text: str, terms: list[str]) -> bool:
    lowered = text.lower()
    return any(term.lower() in lowered for term in terms if term)


def relevance_score(item: dict, required_terms: list[str], excluded_terms: list[str]) -> tuple[int, str]:
    text = " ".join(
        [
            item.get("title", ""),
            item.get("abstract_or_snippet", ""),
            " ".join(item.get("tags") or []),
            str((item.get("metadata") or {}).get("venue", "")),
            str((item.get("metadata") or {}).get("query", "")),
        ]
    )
    if excluded_terms and text_contains_any(text, excluded_terms):
        return 0, "matched exclude terms"
    if required_terms:
        matched = [term for term in required_terms if term.lower() in text.lower()]
        if not matched:
            return 0, "no required topic term matched"
        return min(5, len(matched)), "matched: " + ", ".join(matched[:4])
    return 1, "no topic gate configured"


def apply_topic_gate(items: Iterable[dict], required_terms: list[str], excluded_terms: list[str]) -> list[dict]:
    kept: list[dict] = []
    for item in items:
        score, reason = relevance_score(item, required_terms, excluded_terms)
        if score <= 0:
            continue
        item["score"] = max(int(item.get("score") or 1), score)
        metadata = item.setdefault("metadata", {})
        metadata["relevance_reason"] = reason
        kept.append(item)
    return kept


def search_openalex(query: str, topic: str, limit: int) -> list[dict]:
    params = urllib.parse.urlencode({"search": query, "per-page": limit})
    data = fetch_json(f"https://api.openalex.org/works?{params}")
    rows: list[dict] = []
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
        primary_location = item.get("primary_location") or {}
        primary_source = primary_location.get("source") or {}
        abstract = reconstruct_openalex_abstract(item.get("abstract_inverted_index") or {})
        rows.append(
            make_item(
                title=normalize_space(item.get("title", "")),
                url=item.get("id", ""),
                source="openalex",
                source_type="paper",
                topic=topic,
                date_value=str(item.get("publication_year") or ""),
                abstract_or_snippet=abstract,
                pdf_url=pdf_url,
                metadata={
                    "authors": authors,
                    "year": str(item.get("publication_year") or ""),
                    "venue": primary_source.get("display_name", ""),
                    "doi": (item.get("doi") or "").replace("https://doi.org/", ""),
                    "query": query,
                    "provider": "openalex",
                },
            )
        )
    return rows


def reconstruct_openalex_abstract(index: dict) -> str:
    if not index:
        return ""
    positions: dict[int, str] = {}
    for word, indexes in index.items():
        for position in indexes:
            positions[int(position)] = word
    return " ".join(positions[index] for index in sorted(positions))


def search_crossref(query: str, topic: str, limit: int) -> list[dict]:
    params = urllib.parse.urlencode({"query": query, "rows": limit})
    data = fetch_json(f"https://api.crossref.org/works?{params}")
    rows: list[dict] = []
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
        rows.append(
            make_item(
                title=title,
                url=item.get("URL", ""),
                source="crossref",
                source_type="paper",
                topic=topic,
                date_value=year,
                abstract_or_snippet=normalize_space(item.get("abstract", "")),
                metadata={
                    "authors": authors,
                    "year": year,
                    "venue": normalize_space("; ".join(item.get("container-title") or [])),
                    "publisher": item.get("publisher", ""),
                    "doi": item.get("DOI", ""),
                    "query": query,
                    "provider": "crossref",
                },
            )
        )
    return rows


def search_arxiv(query: str, topic: str, limit: int) -> list[dict]:
    search_query = urllib.parse.quote(f'all:"{query}"')
    text = fetch_text(f"https://export.arxiv.org/api/query?search_query={search_query}&start=0&max_results={limit}")
    root = ET.fromstring(text)
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    rows: list[dict] = []
    for entry in root.findall("atom:entry", ns):
        title = normalize_space(entry.findtext("atom:title", default="", namespaces=ns))
        authors = "; ".join(
            normalize_space(author.findtext("atom:name", default="", namespaces=ns))
            for author in entry.findall("atom:author", ns)
        )
        published = entry.findtext("atom:published", default="", namespaces=ns)
        entry_url = entry.findtext("atom:id", default="", namespaces=ns)
        pdf_url = ""
        for link in entry.findall("atom:link", ns):
            if link.attrib.get("title") == "pdf":
                pdf_url = link.attrib.get("href", "")
        rows.append(
            make_item(
                title=title,
                url=entry_url,
                source="arxiv",
                source_type="paper",
                topic=topic,
                date_value=published[:10] if published else "",
                abstract_or_snippet=normalize_space(entry.findtext("atom:summary", default="", namespaces=ns)),
                pdf_url=pdf_url,
                metadata={"authors": authors, "year": published[:4] if published else "", "venue": "arXiv", "query": query, "provider": "arxiv"},
            )
        )
    return rows


def search_semantic_scholar(query: str, topic: str, limit: int) -> list[dict]:
    fields = "title,abstract,authors,year,venue,externalIds,url,openAccessPdf,publicationDate"
    params = urllib.parse.urlencode({"query": query, "limit": limit, "fields": fields})
    headers = {"User-Agent": USER_AGENT}
    api_key = os.environ.get("SEMANTIC_SCHOLAR_API_KEY", "")
    if api_key:
        headers["x-api-key"] = api_key
    request = urllib.request.Request(f"https://api.semanticscholar.org/graph/v1/paper/search?{params}", headers=headers)
    with urllib.request.urlopen(request, timeout=30) as response:
        data = json.loads(response.read().decode("utf-8"))
    rows: list[dict] = []
    for item in data.get("data", []):
        authors = "; ".join(normalize_space(author.get("name", "")) for author in item.get("authors", []) if author.get("name"))
        external_ids = item.get("externalIds") or {}
        pdf = item.get("openAccessPdf") or {}
        pdf_url = pdf.get("url", "") if isinstance(pdf, dict) else ""
        rows.append(
            make_item(
                title=normalize_space(item.get("title", "")),
                url=item.get("url", ""),
                source="semantic_scholar",
                source_type="paper",
                topic=topic,
                date_value=item.get("publicationDate", "") or str(item.get("year") or ""),
                abstract_or_snippet=normalize_space(item.get("abstract", "")),
                pdf_url=pdf_url,
                metadata={
                    "authors": authors,
                    "year": str(item.get("year") or ""),
                    "venue": item.get("venue", ""),
                    "doi": external_ids.get("DOI", ""),
                    "query": query,
                    "provider": "semantic_scholar",
                },
            )
        )
    return rows


SEARCHERS = {
    "openalex": search_openalex,
    "crossref": search_crossref,
    "arxiv": search_arxiv,
    "semantic_scholar": search_semantic_scholar,
}


def collect_topic_items(query_file: Path, providers: list[str], limit_per_keyword: int, max_keywords: int) -> list[dict]:
    query_data = parse_simple_query_yaml(query_file)
    topic = str(query_data["topic"])
    keywords = list(query_data.get("seed_keywords") or [])[:max_keywords]
    required_terms = list(query_data.get("required_terms_any") or [])
    excluded_terms = list(query_data.get("exclude_terms_any") or [])
    collected: list[dict] = []
    for keyword in keywords:
        for provider in providers:
            searcher = SEARCHERS.get(provider)
            if not searcher:
                continue
            try:
                collected.extend(searcher(keyword, topic, limit_per_keyword))
            except Exception as exc:
                print(f"Warning: collection failed for {provider} / {keyword}: {exc}")
    gated = apply_topic_gate(dedupe_items(collected), required_terms, excluded_terms)
    manual = [item for item in load_manual_items() if item.get("topic") == topic]
    return dedupe_items([*gated, *manual])


def dedupe_items(items: Iterable[dict]) -> list[dict]:
    seen: set[str] = set()
    unique: list[dict] = []
    for item in items:
        key = item.get("id") or item_id(item.get("url", ""), item.get("title", ""), str((item.get("metadata") or {}).get("doi", "")))
        if not key or key in seen:
            continue
        seen.add(key)
        item["id"] = key
        unique.append(item)
    return unique


def item_line(item: dict) -> str:
    title = item.get("title", "未命名条目")
    topic = item.get("topic", "unknown")
    source = item.get("source", "")
    score = item.get("score", "")
    authority = item.get("authority_score", "")
    url = item.get("url", "")
    link = f" [{source}]({url})" if url else f" [{source}]"
    return (
        f"- **{title}**{link}；主题：`{topic}`；相关性：{score}；权威性：{authority}；"
        f"人工状态：`{review_status(item)}`；流程状态：`{process_status(item)}`"
    )


def write_weekly_digest(items: list[dict], run_items: list[dict], output_date: str | None = None) -> Path:
    output_date = output_date or today_string()
    path = Path("outputs/weekly") / f"{output_date}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    papers = [item for item in run_items if item.get("source_type") == "paper" and item.get("score", 0) > 0]
    context_items = [item for item in run_items if item.get("source_type") in {"news", "standard", "policy", "whitepaper", "report"} and item.get("score", 0) > 0]
    top_items = sorted([item for item in run_items if item.get("score", 0) > 0], key=lambda row: int(row.get("score") or 0), reverse=True)[:12]
    downloadable = [item for item in papers if item.get("pdf_url")][:10]
    reading = sorted(papers, key=lambda row: int(row.get("score") or 0), reverse=True)[:10]
    topics = sorted({item.get("topic", "unknown") for item in run_items if item.get("score", 0) > 0})

    def section(title: str, rows: list[dict], empty: str) -> list[str]:
        lines = [f"## {title}", ""]
        lines.extend(item_line(item) for item in rows)
        if not rows:
            lines.append(empty)
        lines.append("")
        return lines

    lines = [
        "# 每周低空研究情报摘要",
        "",
        f"- 生成日期：{output_date}",
        f"- 本轮新增或更新条目：{len(run_items)}",
        f"- 当前 item 总数：{len(items)}",
        "",
        "> 机器生成，需人工复核。本文不包含最终研究结论、创新性判断或建仓建议。",
        "",
    ]
    lines += section("新增论文", papers[:20], "本轮没有新增通过 topic gate 的论文。")
    lines += section("新增标准 / 政策 / 报告 / 产业信号", context_items[:20], "本轮尚未接入新的标准、政策、报告或产业信号源；可通过 `data/manual_items.jsonl` 手动补充。")
    lines += section("优先 review 条目", top_items, "没有可 review 条目。")
    lines += section("值得下载 PDF 的条目", downloadable, "本轮没有发现明确 open PDF URL；受限 PDF 请通过合法访问方式自行下载。")
    lines += section("建议进入 LLM 阅读的条目", reading, "本轮没有推荐阅读条目。")
    lines += ["## 主题层观察", ""]
    if topics:
        for topic in topics:
            count = len([item for item in run_items if item.get("topic") == topic and item.get("score", 0) > 0])
            lines.append(f"- `{topic}`：本轮收集到 {count} 个候选条目。请先人工筛选，不要直接形成研究 gap。")
    else:
        lines.append("本轮没有足够 topic 信号。")
    lines += [
        "",
        "## 建议下一步",
        "",
        "1. 打开 `outputs/review_dashboard.md`，先处理相关性和权威性都较高的 `new` 条目。",
        "2. 对明确有价值的条目标记为 `kept`；对无关条目标记为 `rejected`。",
        "3. 对需要精读的 PDF 运行 `python scripts/read_item.py <pdf路径> --topic <topic>`。",
        "4. topic 下已读中文笔记达到 10 篇左右后，再运行 `python scripts/synthesize_topic.py --topic <topic>`。",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def write_review_dashboard(items: list[dict], path: Path = Path("outputs/review_dashboard.md")) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# 研究情报复核面板",
        "",
        "> 机器生成的轻量 review 面板。常规使用时优先看这里，不需要直接维护内部文件。",
        "",
        "## 建议操作",
        "",
        "- 人工状态 `review_status`：`new` / `kept` / `downloaded` / `rejected`，由你在 GUI 中修改。",
        "- 流程状态 `process_status`：`unread` / `read` / `summarized` / `used_in_synthesis`，通常由脚本自动维护。",
        "",
    ]
    lines += ["## 按人工状态", ""]
    for status in ["new", "kept", "downloaded", "rejected"]:
        rows = sorted([item for item in items if review_status(item) == status], key=lambda row: int(row.get("score") or 0), reverse=True)
        lines += [f"### {status}", ""]
        if rows:
            lines.extend(item_line(item) for item in rows[:30])
        else:
            lines.append("暂无。")
        lines.append("")
    lines += ["## 按流程状态", ""]
    for status in ["unread", "read", "summarized", "used_in_synthesis"]:
        rows = sorted([item for item in items if process_status(item) == status], key=lambda row: int(row.get("score") or 0), reverse=True)
        lines += [f"### {status}", ""]
        if rows:
            lines.extend(item_line(item) for item in rows[:30])
        else:
            lines.append("暂无。")
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def extract_pdf_dois(path: Path) -> set[str]:
    text = path.read_bytes()[:3_000_000].decode("latin-1", errors="ignore")
    dois = re.findall(r"10\.\d{4,9}/[-._;()/:A-Za-z0-9]+", text)
    return {doi.rstrip(").,;").lower() for doi in dois}


def extract_pdf_visible_text(path: Path, max_bytes: int = 2_000_000) -> str:
    data = path.read_bytes()[:max_bytes]
    decoded = data.decode("utf-8", errors="ignore")
    if len(decoded) < 500:
        decoded = data.decode("latin-1", errors="ignore")
    strings = re.findall(r"[A-Za-z][A-Za-z0-9,.:;()\- /]{8,}", decoded)
    return normalize_space(" ".join(strings[:1000]))


def extract_pdf_title(path: Path) -> str:
    for module_name in ["pypdf", "PyPDF2"]:
        try:
            module = __import__(module_name)
            reader = module.PdfReader(str(path))
            metadata = getattr(reader, "metadata", None) or {}
            title = ""
            if hasattr(metadata, "title"):
                title = metadata.title or ""
            elif isinstance(metadata, dict):
                title = metadata.get("/Title", "") or metadata.get("Title", "")
            if title:
                return normalize_space(str(title))
            if reader.pages:
                text = reader.pages[0].extract_text() or ""
                lines = [line.strip() for line in text.splitlines() if len(line.strip()) >= 8]
                if lines:
                    return normalize_space(lines[0])
        except Exception:
            continue
    text = path.read_bytes()[:1_000_000].decode("latin-1", errors="ignore")
    match = re.search(r"/Title\s*\((?P<title>[^)]{8,300})\)", text, flags=re.IGNORECASE | re.DOTALL)
    if match:
        return normalize_space(match.group("title").replace(r"\(", "(").replace(r"\)", ")"))
    return ""


def query_for_pdf(path: Path) -> tuple[str, str]:
    dois = sorted(extract_pdf_dois(path))
    if dois:
        return dois[0], "doi"
    title = extract_pdf_title(path)
    if title:
        return title, "pdf_title"
    visible_words = extract_pdf_visible_text(path).split()
    if len(visible_words) >= 6:
        return " ".join(visible_words[:24]), "pdf_text"
    return path.stem.replace("_", " ").replace("-", " "), "filename"


def lookup_pdf_item(path: Path, topic: str, providers: list[str], limit: int = 3) -> tuple[dict, float, str]:
    query, query_source = query_for_pdf(path)
    pdf_dois = extract_pdf_dois(path)
    extracted_title = extract_pdf_title(path) or path.stem
    for existing in load_items():
        metadata = existing.get("metadata") or {}
        doi = str(metadata.get("doi", "")).lower().strip()
        if doi and doi in pdf_dois:
            return existing, 1.0, "existing item doi"
        if existing.get("topic") == topic and title_similarity(extracted_title, existing.get("title", "")) >= 0.9:
            return existing, 0.9, "existing item title"

    candidates: list[dict] = []
    for provider in providers:
        searcher = SEARCHERS.get(provider)
        if not searcher:
            continue
        try:
            candidates.extend(searcher(query, topic, limit))
        except Exception:
            continue
    if not candidates:
        return make_item(title=extracted_title or path.stem, url="", source="local_pdf", source_type="paper", topic=topic, metadata={"query_source": query_source}), 0.0, "local filename fallback"
    for item in candidates:
        doi = str((item.get("metadata") or {}).get("doi", "")).lower().strip()
        if doi and doi in pdf_dois:
            return item, 1.0, "doi"
    best = max(candidates, key=lambda item: title_similarity(extracted_title, item.get("title", "")))
    score = title_similarity(extracted_title, best.get("title", ""))
    if score < 0.72:
        fallback = make_item(
            title=extracted_title or path.stem,
            url=f"https://doi.org/{sorted(pdf_dois)[0]}" if pdf_dois else "",
            source="local_pdf",
            source_type="paper",
            topic=topic,
            metadata={"doi": sorted(pdf_dois)[0] if pdf_dois else "", "query_source": query_source, "low_confidence_online_title": best.get("title", "")},
        )
        return fallback, score, f"low-confidence online match; kept local metadata from {query_source}"
    return best, score, f"title similarity from {query_source}"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def multipart_file_body(path: Path, fields: dict[str, str]) -> tuple[bytes, str]:
    boundary = f"----low-altitude-{uuid.uuid4().hex}"
    chunks: list[bytes] = []
    for name, value in fields.items():
        chunks.extend(
            [
                f"--{boundary}\r\n".encode("utf-8"),
                f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode("utf-8"),
                value.encode("utf-8"),
                b"\r\n",
            ]
        )
    chunks.extend(
        [
            f"--{boundary}\r\n".encode("utf-8"),
            f'Content-Disposition: form-data; name="file"; filename="{path.name}"\r\n'.encode("utf-8"),
            b"Content-Type: application/pdf\r\n\r\n",
            path.read_bytes(),
            b"\r\n",
            f"--{boundary}--\r\n".encode("utf-8"),
        ]
    )
    return b"".join(chunks), boundary


def provider_http_error(exc: urllib.error.HTTPError) -> RuntimeError:
    body = exc.read().decode("utf-8", errors="replace")
    detail = body.strip()
    if body:
        try:
            data = json.loads(body)
            error = data.get("error") if isinstance(data, dict) else None
            if isinstance(error, dict):
                detail = str(error.get("message") or error.get("code") or body).strip()
            elif isinstance(error, str):
                detail = error.strip()
        except json.JSONDecodeError:
            detail = body.strip()
    if len(detail) > 500:
        detail = detail[:500] + "..."
    detail = re.sub(r"\borg-[A-Za-z0-9_-]+", "org-[redacted]", detail)
    detail = re.sub(r"\bak-[A-Za-z0-9_-]+", "ak-[redacted]", detail)
    detail = re.sub(r"\bsk-[A-Za-z0-9_-]+", "sk-[redacted]", detail)
    message = f"HTTP {exc.code} {exc.reason}"
    if detail:
        message = f"{message}: {detail}"
    return RuntimeError(message)


def moonshot_request_json(url: str, api_key: str, payload: dict, timeout: int) -> dict:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raise provider_http_error(exc) from exc


def kimi_upload_file(pdf_path: Path, api_key: str, base_url: str, timeout: int) -> str:
    body, boundary = multipart_file_body(pdf_path, {"purpose": "file-extract"})
    request = urllib.request.Request(
        f"{base_url.rstrip('/')}/files",
        data=body,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raise provider_http_error(exc) from exc
    return str(data.get("id", ""))


def kimi_file_content(file_id: str, api_key: str, base_url: str, timeout: int) -> str:
    request = urllib.request.Request(f"{base_url.rstrip('/')}/files/{file_id}/content", headers={"Authorization": f"Bearer {api_key}"}, method="GET")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        raise provider_http_error(exc) from exc


def extract_chat_completion_text(data: dict) -> str:
    choices = data.get("choices") or []
    if not choices:
        return ""
    message = choices[0].get("message") or {}
    content = message.get("content", "")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict):
                parts.append(str(item.get("text", "") or item.get("content", "")))
        return "\n".join(part for part in parts if part).strip()
    return str(content or "")


def kimi_config(config: dict) -> tuple[str, str, str]:
    providers = (config.get("reading") or {}).get("providers") or {}
    kimi = providers.get("kimi") or {}
    api_key = os.environ.get(str(kimi.get("api_key_env") or "MOONSHOT_API_KEY"), "") or os.environ.get(str(kimi.get("fallback_api_key_env") or "KIMI_API_KEY"), "")
    base_url = os.environ.get(str(kimi.get("base_url_env") or "MOONSHOT_BASE_URL"), "") or os.environ.get(str(kimi.get("fallback_base_url_env") or "KIMI_BASE_URL"), "") or str(kimi.get("default_base_url") or "https://api.moonshot.cn/v1")
    model = os.environ.get(str(kimi.get("model_env") or "KIMI_READING_MODEL"), "") or str(kimi.get("default_model") or "kimi-k2.6")
    if not api_key:
        raise RuntimeError("MOONSHOT_API_KEY or KIMI_API_KEY missing")
    return api_key, base_url, model


def build_chinese_reading_prompt(item: dict, fingerprint: str) -> str:
    metadata = json.dumps(item, ensure_ascii=False, indent=2)
    return f"""请阅读这篇论文 PDF，为低空研究情报助手生成一份中文阅读笔记。

严格规则：
- 不要编造 DOI、作者、年份、venue、数据集、标准编号或数值结果。
- 区分 `paper-supported`、`inferred`、`proposal`、`unsupported`。
- 只总结论文内容，不要生成最终研究结论、创新性判断、实施仓库建议或路线卡。
- `full-text parsed` 只表示模型处理过 PDF，不等于人工审阅。
- 如果信息不足，写 `unsupported: PDF 中未提供`。

已知 metadata：
```json
{metadata}
```

PDF fingerprint: {fingerprint}

请输出 Markdown，章节必须如下：
# 条目摘要
## 元数据
## 收录原因
## 核心内容
## 方法 / 系统 / 政策细节
## 关键证据
## 图表与可视证据
## 局限性
## 与低空研究的关联
## 可复用参数 / 模型 / 基线
## 后续动作
## 可靠性说明

每个实质性 bullet 必须以 `paper-supported:`、`inferred:`、`proposal:` 或 `unsupported:` 开头。后续动作只能是继续阅读、核验参数、补充 metadata、查找政策/标准/产业背景等审查任务。
"""


def kimi_read_pdf(pdf_path: Path, item: dict, config: dict, timeout: int = 300) -> tuple[str, str]:
    api_key, base_url, model = kimi_config(config)
    file_id = kimi_upload_file(pdf_path, api_key, base_url, timeout)
    if not file_id:
        raise RuntimeError("Kimi file upload did not return a file id.")
    file_content = kimi_file_content(file_id, api_key, base_url, timeout)
    fingerprint = sha256_file(pdf_path)
    prompt = build_chinese_reading_prompt(item, fingerprint)
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "你是严谨的中英文技术文献阅读助手。请遵守证据标签规则，只做保守摘要，不做最终研究判断。"},
            {"role": "system", "content": file_content},
            {"role": "user", "content": prompt},
        ],
    }
    data = moonshot_request_json(f"{base_url.rstrip('/')}/chat/completions", api_key, payload, timeout)
    return extract_chat_completion_text(data), model


def legacy_note_path_for_item(item: dict) -> Path:
    return Path("notes/items") / f"{item['id']}.md"


def note_path_for_item(item: dict) -> Path:
    title = safe_filename(str(item.get("title", "")), fallback=str(item.get("id", "item")))
    preferred = Path("notes/items") / f"{title}.md"
    legacy = legacy_note_path_for_item(item)
    if preferred.exists() or not legacy.exists():
        return preferred
    return legacy


def preferred_note_path_for_item(item: dict) -> Path:
    title = safe_filename(str(item.get("title", "")), fallback=str(item.get("id", "item")))
    return Path("notes/items") / f"{title}.md"


def sync_note_filename(item: dict) -> dict:
    note_path_value = item.get("note_path")
    if not note_path_value:
        return item
    current = Path(note_path_value)
    if not current.exists():
        return item
    preferred = preferred_note_path_for_item(item)
    if current == preferred:
        return item
    preferred.parent.mkdir(parents=True, exist_ok=True)
    if preferred.exists():
        preferred = preferred.with_name(f"{preferred.stem}-{item['id']}{preferred.suffix}")
    current.rename(preferred)
    item["note_path"] = str(preferred)
    return item


def write_item_note(item: dict, note: str, pdf_path: Path, model: str) -> Path:
    path = preferred_note_path_for_item(item)
    path.parent.mkdir(parents=True, exist_ok=True)
    provenance = [
        "",
        "<!-- item_reading_metadata",
        json.dumps(
            {
                "item_id": item["id"],
                "reading_model": model,
                "reading_provider": "kimi",
                "read_at": now_iso(),
                "pdf_fingerprint": sha256_file(pdf_path),
                "pdf_source": str(pdf_path),
                "reading_status": "full-text parsed",
                "human_reviewed": False,
            },
            ensure_ascii=False,
            indent=2,
        ),
        "-->",
        "",
    ]
    path.write_text(note.rstrip() + "\n" + "\n".join(provenance), encoding="utf-8")
    return path
