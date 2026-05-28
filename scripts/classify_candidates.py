"""Automatically classify candidate source quality and produce a review queue."""

from __future__ import annotations

import argparse
import csv
import hashlib
from datetime import datetime, timezone
from pathlib import Path


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
]

REVIEW_FIELDS = [
    "item_id",
    "item_type",
    "topic",
    "title",
    "reason",
    "recommended_action",
    "status",
    "source_path",
    "added_at",
]

TOP_VENUE_PATTERNS = [
    "ieee transactions",
    "acm transactions",
    "nature",
    "science",
    "proceedings of the ieee",
    "ieee journal",
]

STRONG_VENUE_PATTERNS = [
    "ieee communications",
    "ieee wireless communications",
    "ieee internet of things",
    "ieee network",
    "acm mobicom",
    "acm mobihoc",
    "usenix",
    "sigcomm",
    "infocom",
]

LOW_CONFIDENCE_PATTERNS = [
    "arxiv",
    "preprint",
    "workshop",
]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def stable_id(*parts: str) -> str:
    value = "|".join(part.strip().lower() for part in parts if part)
    return hashlib.sha1(value.encode("utf-8")).hexdigest()[:12]


def read_csv(path: Path, fields: list[str]) -> list[dict[str, str]]:
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


def classify_venue(venue: str, source: str) -> tuple[str, str]:
    text = f"{venue} {source}".lower()
    if any(pattern in text for pattern in TOP_VENUE_PATTERNS):
        return "top", "high"
    if any(pattern in text for pattern in STRONG_VENUE_PATTERNS):
        return "strong", "high"
    if any(pattern in text for pattern in LOW_CONFIDENCE_PATTERNS):
        return "unknown", "medium"
    if venue.strip():
        return "medium", "medium"
    return "unknown", "medium"


def classify_practical_relevance(row: dict[str, str]) -> tuple[str, str]:
    text = " ".join([row.get("title", ""), row.get("venue", ""), row.get("query", "")]).lower()
    practical_terms = [
        "standard",
        "remote id",
        "experiment",
        "measurement",
        "deployment",
        "policy",
        "regulation",
        "astm",
        "3gpp",
        "faa",
        "easa",
        "utm",
        "u-space",
    ]
    if any(term in text for term in practical_terms):
        return "medium", "verify parameters from practical sources"
    return "", "needs practical validation"


def queue_item(row: dict[str, str], reason: str, action: str, source_path: str) -> dict[str, str]:
    return {
        "item_id": stable_id(row.get("candidate_id", ""), reason),
        "item_type": "paper_candidate",
        "topic": row.get("topic", ""),
        "title": row.get("title", ""),
        "reason": reason,
        "recommended_action": action,
        "status": "pending",
        "source_path": source_path,
        "added_at": now_iso(),
    }


def classify_rows(rows: list[dict[str, str]], source_path: str) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    queue: list[dict[str, str]] = []
    for row in rows:
        if not row.get("source_type"):
            row["source_type"] = "academic_paper"
        if not row.get("venue_tier") or row["venue_tier"] == "unknown":
            tier, trust = classify_venue(row.get("venue", ""), row.get("source", ""))
            row["venue_tier"] = tier
            row["source_trust"] = row.get("source_trust") or trust
        if not row.get("source_trust") or row["source_trust"] == "unknown":
            _, trust = classify_venue(row.get("venue", ""), row.get("source", ""))
            row["source_trust"] = trust
        if not row.get("practical_relevance"):
            relevance, needed = classify_practical_relevance(row)
            row["practical_relevance"] = relevance
            row["practical_evidence_needed"] = needed

        if row.get("source_trust") == "low":
            queue.append(queue_item(row, "low source trust", "Do not use as route-card support unless corroborated.", source_path))
        if row.get("venue_tier") == "unknown":
            queue.append(queue_item(row, "unknown venue tier", "Audit venue quality before synthesis.", source_path))
        if row.get("practical_evidence_needed") == "needs practical validation":
            queue.append(queue_item(row, "missing practical validation", "Find standards, policy, white papers, or real-system evidence.", source_path))
        if row.get("access_status") == "needs_user_pdf":
            queue.append(queue_item(row, "PDF requires user access", "Download legally if institutional or personal access is available.", source_path))
    return rows, dedupe_queue(queue)


def dedupe_queue(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    seen = set()
    unique = []
    for row in rows:
        key = row["item_id"]
        if key in seen:
            continue
        seen.add(key)
        unique.append(row)
    return unique


def main() -> int:
    parser = argparse.ArgumentParser(description="Classify candidate source quality and generate review queue.")
    parser.add_argument("--candidates", default="literature/database/paper_candidates.csv")
    parser.add_argument("--review-queue", default="literature/database/review_queue.csv")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    candidates_path = Path(args.candidates)
    rows = read_csv(candidates_path, CANDIDATE_FIELDS)
    if not rows:
        print(f"No paper candidates found in {candidates_path}.")
        return 0

    rows, queue = classify_rows(rows, str(candidates_path))

    print(f"Classified {len(rows)} candidates.")
    print(f"Generated {len(queue)} review queue items.")

    if args.dry_run:
        for item in queue[:10]:
            print(f"- {item['topic']}: {item['title']} [{item['reason']}]")
        print("Dry run only. No files were written.")
        return 0

    write_csv(candidates_path, CANDIDATE_FIELDS, rows)
    write_csv(Path(args.review_queue), REVIEW_FIELDS, queue)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
