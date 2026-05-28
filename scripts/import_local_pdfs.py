"""Dry-run friendly local PDF metadata importer.

This script scans a local PDF inbox and prepares conservative metadata stubs.
It does not parse full text and does not infer DOI, venue, author, or year
aggressively.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


CSV_FIELDS = [
    "paper_id",
    "title",
    "authors",
    "year",
    "venue",
    "doi",
    "url",
    "topic",
    "source_type",
    "venue_tier",
    "source_trust",
    "reading_status",
    "relevance",
    "practical_relevance",
    "metadata_confidence",
    "notes_path",
    "source",
]


def slugify(value: str) -> str:
    chars = []
    for char in value.lower():
        if char.isalnum():
            chars.append(char)
        elif chars and chars[-1] != "_":
            chars.append("_")
    return "".join(chars).strip("_") or "paper"


def metadata_from_pdf(path: Path, notes_dir: Path) -> dict[str, str]:
    paper_id = slugify(path.stem)
    return {
        "paper_id": paper_id,
        "title": path.stem.replace("_", " ").replace("-", " "),
        "authors": "",
        "year": "",
        "venue": "",
        "doi": "",
        "url": "",
        "topic": "",
        "source_type": "academic_paper",
        "venue_tier": "unknown",
        "source_trust": "unknown",
        "reading_status": "metadata only",
        "relevance": "",
        "practical_relevance": "",
        "metadata_confidence": "low",
        "notes_path": str(notes_dir / f"{paper_id}.md"),
        "source": str(path),
    }


def load_existing(database: Path) -> list[dict[str, str]]:
    if not database.exists() or database.stat().st_size == 0:
        return []
    with database.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_database(database: Path, rows: list[dict[str, str]]) -> None:
    database.parent.mkdir(parents=True, exist_ok=True)
    with database.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def write_note_stub(note_path: Path, row: dict[str, str]) -> None:
    note_path.parent.mkdir(parents=True, exist_ok=True)
    if note_path.exists():
        return
    note_path.write_text(
        "\n".join(
            [
                "# Paper Note",
                "",
                "## Metadata",
                "",
                f"- Paper ID: {row['paper_id']}",
                f"- Title: {row['title']}",
                "- Authors:",
                "- Year:",
                "- Venue:",
                "- DOI:",
                "- URL:",
                "- Topic:",
                "- Source type: academic_paper",
                "- Venue tier: unknown",
                "- Source trust: unknown",
                "- Reading status: metadata only",
                "- Relevance:",
                "- Practical relevance:",
                "- Metadata confidence: low",
                "",
                "## Reliability Notes",
                "",
                "- Metadata derived from local filename only; human review required.",
                "",
            ]
        ),
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare conservative metadata stubs for local PDFs.")
    parser.add_argument("--inbox", default="literature/inbox/papers", help="Directory containing local PDFs.")
    parser.add_argument("--database", default="literature/database/papers.csv", help="CSV metadata database.")
    parser.add_argument("--notes-dir", default="literature/notes/paper_notes", help="Directory for note stubs.")
    parser.add_argument("--dry-run", action="store_true", help="Print planned changes without writing.")
    args = parser.parse_args()

    inbox = Path(args.inbox)
    database = Path(args.database)
    notes_dir = Path(args.notes_dir)

    pdfs = sorted(inbox.glob("*.pdf")) if inbox.exists() else []
    if not pdfs:
        print(f"No PDFs found in {inbox}. Nothing to import.")
        return 0

    existing = load_existing(database)
    existing_ids = {row.get("paper_id", "") for row in existing}
    new_rows = [metadata_from_pdf(path, notes_dir) for path in pdfs]
    new_rows = [row for row in new_rows if row["paper_id"] not in existing_ids]

    if not new_rows:
        print("All PDFs already appear in the database.")
        return 0

    print(f"Prepared {len(new_rows)} metadata stubs:")
    for row in new_rows:
        print(f"- {row['paper_id']}: {row['title']} [{row['reading_status']}, {row['metadata_confidence']} confidence]")

    if args.dry_run:
        print("Dry run only. No files were written.")
        return 0

    rows = existing + new_rows
    write_database(database, rows)
    for row in new_rows:
        write_note_stub(Path(row["notes_path"]), row)
    print(f"Updated {database} and note stubs under {notes_dir}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
