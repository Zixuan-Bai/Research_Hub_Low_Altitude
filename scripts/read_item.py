"""Read one local PDF into a Chinese item note and update data/items.jsonl."""

from __future__ import annotations

import argparse
from pathlib import Path

import research_hub_lib as hub


def main() -> int:
    parser = argparse.ArgumentParser(description="Read one PDF and create a Chinese item note.")
    parser.add_argument("pdf", help="Path to a local PDF.")
    parser.add_argument("--topic", required=True, help="Topic key or topic slug.")
    parser.add_argument("--config", default=str(hub.DEFAULT_CONFIG), help="Pipeline config JSON.")
    parser.add_argument("--providers", default="openalex,crossref,semantic_scholar", help="Metadata lookup providers.")
    parser.add_argument("--lookup-limit", type=int, default=3, help="Metadata lookup result limit per provider.")
    parser.add_argument("--timeout", type=int, default=300, help="Kimi request timeout in seconds.")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be read without API calls or writes.")
    args = parser.parse_args()

    pdf_path = Path(args.pdf)
    if not pdf_path.is_file():
        print(f"PDF not found: {pdf_path}")
        return 1

    hub.load_env_file()
    config = hub.load_config(Path(args.config))
    slug_map = hub.topic_key_to_slug(config)
    topic = slug_map.get(args.topic, args.topic)
    providers = [provider.strip() for provider in args.providers.split(",") if provider.strip()]
    existing = hub.find_existing_note_for_pdf(pdf_path)
    if existing:
        print(f"Existing note found, skipping: {existing.get('note_path')}")
        return 0

    item, confidence, reason = hub.prepare_pdf_item(pdf_path, topic, providers, args.lookup_limit)

    if args.dry_run:
        print(f"Would read PDF: {pdf_path}")
        print(f"Matched item: {item.get('title', '')}")
        print(f"Confidence: {confidence:.2f} ({reason})")
        print(f"Output note: {hub.note_path_for_item(item)}")
        return 0

    try:
        item, note_path, _model = hub.read_pdf_to_note(pdf_path, item, config, args.timeout)
    except RuntimeError as exc:
        print(str(exc))
        return 1
    print(f"Wrote Chinese item note: {note_path}")
    print(f"Updated item store: {hub.ITEMS_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
