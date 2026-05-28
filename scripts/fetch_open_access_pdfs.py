"""Download open-access PDFs from the candidate table.

The script only downloads rows with `access_status=open` and a `pdf_url`.
Restricted or missing PDFs stay in the acquisition queue for human handling.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import re
from datetime import datetime, timezone
import urllib.request
from pathlib import Path


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


def safe_name(value: str) -> str:
    value = re.sub(r"[^A-Za-z0-9._-]+", "_", value).strip("_")
    return value or "paper"


def read_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists() or path.stat().st_size == 0:
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_rows(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def append_queue(queue_path: Path, row: dict[str, str], reason: str) -> None:
    existing = read_rows(queue_path)
    queue_id = stable_id("queue", row.get("candidate_id", ""), reason)
    if any(item.get("queue_id") == queue_id for item in existing):
        return
    existing.append(
        {
            "queue_id": queue_id,
            "candidate_id": row.get("candidate_id", ""),
            "title": row.get("title", ""),
            "authors": row.get("authors", ""),
            "year": row.get("year", ""),
            "venue": row.get("venue", ""),
            "doi": row.get("doi", ""),
            "url": row.get("url", ""),
            "topic": row.get("topic", ""),
            "reason": reason,
            "requested_action": "User should download legally in a browser if access is available.",
            "status": "pending",
            "added_at": now_iso(),
        }
    )
    write_rows(queue_path, QUEUE_FIELDS, existing)


def download_pdf(url: str, output_path: Path) -> None:
    request = urllib.request.Request(url, headers={"User-Agent": "low-altitude-research-hub/0.1"})
    with urllib.request.urlopen(request, timeout=60) as response:
        content_type = response.headers.get("Content-Type", "")
        data = response.read()
    if b"%PDF" not in data[:1024] and "pdf" not in content_type.lower():
        raise ValueError(f"Downloaded content does not look like a PDF: {content_type}")
    output_path.write_bytes(data)


def main() -> int:
    parser = argparse.ArgumentParser(description="Download open-access PDFs from candidate metadata.")
    parser.add_argument("--candidates", default="literature/database/paper_candidates.csv", help="Candidate CSV.")
    parser.add_argument("--queue", default="literature/database/acquisition_queue.csv", help="Manual acquisition queue CSV.")
    parser.add_argument("--output-dir", default="literature/pdfs/open_access", help="Output directory for OA PDFs.")
    parser.add_argument("--limit", type=int, default=10, help="Maximum PDFs to download.")
    parser.add_argument("--dry-run", action="store_true", help="Show planned downloads without writing.")
    args = parser.parse_args()

    candidates = read_rows(Path(args.candidates))
    downloadable = [
        row for row in candidates
        if row.get("access_status") == "open" and row.get("pdf_url")
    ][: args.limit]

    if not downloadable:
        print("No open-access PDF URLs found in candidate table.")
        return 0

    output_dir = Path(args.output_dir)
    queue_path = Path(args.queue)
    for row in downloadable:
        filename = f"{row.get('candidate_id') or safe_name(row.get('title', 'paper'))}.pdf"
        output_path = output_dir / filename
        print(f"{row.get('title', '')} -> {output_path}")
        if args.dry_run:
            continue
        output_dir.mkdir(parents=True, exist_ok=True)
        if output_path.exists():
            print(f"  skipped existing {output_path}")
            continue
        try:
            download_pdf(row["pdf_url"], output_path)
            print(f"  downloaded {output_path}")
        except Exception as exc:
            reason = f"Open PDF URL was found but automatic download failed: {exc}"
            append_queue(queue_path, row, reason)
            print(f"  failed: {exc}")
            print(f"  queued for manual download in {queue_path}")

    if args.dry_run:
        print("Dry run only. No PDFs were downloaded.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
