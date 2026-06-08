"""Extract concrete recommended sources from item notes into data/items.jsonl."""

from __future__ import annotations

import argparse
from pathlib import Path

import research_hub_lib as hub


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract concrete related sources from item notes.")
    parser.add_argument("--from-notes", action="store_true", help="Scan item notes from data/items.jsonl.")
    parser.add_argument("--topic", default="all", help="Topic slug, or all.")
    parser.add_argument("--note", default="", help="Scan one note path.")
    parser.add_argument("--providers", default="openalex,crossref,semantic_scholar", help="Metadata lookup providers for extracted papers, or none.")
    parser.add_argument("--lookup-limit", type=int, default=3, help="Metadata lookup result limit per provider.")
    parser.add_argument("--dry-run", action="store_true", help="Print extracted items without writing.")
    args = parser.parse_args()

    if not args.from_notes and not args.note:
        parser.error("Use --from-notes or --note notes/items/<id>.md")

    items = hub.load_items()
    note_path = Path(args.note) if args.note else None
    if note_path is not None and not note_path.exists():
        print(f"Note not found: {note_path}")
        return 1

    extracted = hub.extract_related_items_from_notes(items, topic=args.topic, note_path=note_path)
    providers = [provider.strip() for provider in args.providers.split(",") if provider.strip()]
    if providers != ["none"]:
        extracted = hub.enrich_related_paper_metadata(extracted, providers=providers, lookup_limit=args.lookup_limit)
    print(f"Extracted related items: {len(extracted)}")
    for item in extracted:
        metadata = item.get("metadata") or {}
        print(
            f"- {item.get('title', '')} | type={item.get('source_type', '')} | "
            f"topic={item.get('topic', '')} | confidence={metadata.get('extraction_confidence', '')}"
        )

    if args.dry_run or not extracted:
        return 0

    all_items, changed = hub.upsert_items(extracted)
    hub.write_review_dashboard(all_items)
    print(f"Inserted or updated items: {len(changed)}")
    print(f"Item store: {hub.ITEMS_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
