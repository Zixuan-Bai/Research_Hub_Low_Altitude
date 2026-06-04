"""Read one local PDF into a Chinese item note and update data/items.jsonl."""

from __future__ import annotations

import argparse
from pathlib import Path

import research_hub_lib as hub


def main() -> int:
    parser = argparse.ArgumentParser(description="Read one PDF and create a Chinese item note.")
    parser.add_argument("pdf", help="Path to a local PDF.")
    parser.add_argument("--topic", default="auto", help="Topic key/slug, or auto. Default: auto.")
    parser.add_argument("--config", default=str(hub.DEFAULT_CONFIG), help="Pipeline config JSON.")
    parser.add_argument("--providers", default="openalex,crossref,semantic_scholar", help="Metadata lookup providers.")
    parser.add_argument("--lookup-limit", type=int, default=3, help="Metadata lookup result limit per provider.")
    parser.add_argument("--timeout", type=int, default=300, help="Kimi request timeout in seconds.")
    parser.add_argument(
        "--mode",
        choices=["auto", "metadata-only", "text-draft", "kimi"],
        default="auto",
        help="Reading mode. auto uses kimi only when a Kimi/Moonshot API key is present; otherwise text-draft.",
    )
    parser.add_argument("--force", action="store_true", help="Regenerate a note even when one already exists.")
    parser.add_argument("--upgrade", action="store_true", help="Upgrade an existing text-draft note to Kimi when --mode kimi is selected.")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be read without API calls or writes.")
    args = parser.parse_args()

    pdf_path = Path(args.pdf)
    if not pdf_path.is_file():
        print(f"PDF not found: {pdf_path}")
        return 1

    hub.load_env_file()
    config = hub.load_config(Path(args.config))
    topic, topic_score, topic_reason = hub.resolve_topic_for_pdf(pdf_path, args.topic, config)
    providers = [provider.strip() for provider in args.providers.split(",") if provider.strip()]
    mode = args.mode
    if mode == "auto":
        mode = "kimi" if hub.has_kimi_api_key(config) else "text-draft"

    existing = hub.find_existing_note_for_pdf(pdf_path)
    if existing and not args.force:
        existing_mode = str((existing.get("metadata") or {}).get("reading_mode") or "")
        can_upgrade = args.upgrade and existing_mode == "text-draft" and mode == "kimi"
        if not can_upgrade:
            if args.dry_run:
                print(f"Existing note found, would skip: {existing.get('note_path')}")
                print(f"PDF path: {pdf_path}")
                return 0
            synced = hub.sync_existing_item_for_pdf(pdf_path, existing)
            print(f"Existing note found, synced names, skipping: {synced.get('note_path')}")
            print(f"PDF path: {(synced.get('metadata') or {}).get('pdf_source', pdf_path)}")
            print("Use --force to overwrite, or --upgrade --mode kimi to upgrade a text-draft note.")
            return 0

    registered = hub.find_registered_pdf_item(pdf_path)
    if registered:
        item = registered
        confidence = float((item.get("metadata") or {}).get("metadata_match_confidence") or 1.0)
        reason = str((item.get("metadata") or {}).get("metadata_match_reason") or "registered PDF item")
    else:
        if args.dry_run:
            item, confidence, reason = hub.prepare_pdf_item(pdf_path, topic, providers, args.lookup_limit)
        else:
            item = hub.register_pdf_item(pdf_path, topic=topic, providers=providers, lookup_limit=args.lookup_limit, config=config)
            confidence = float((item.get("metadata") or {}).get("metadata_match_confidence") or 0.0)
            reason = str((item.get("metadata") or {}).get("metadata_match_reason") or "registered PDF item")

    item.setdefault("metadata", {})["topic_inference_reason"] = topic_reason

    if args.dry_run:
        action = "Would upgrade/read" if existing and (args.force or args.upgrade) else "Would read PDF"
        print(f"{action}: {pdf_path}")
        print(f"Matched item: {item.get('title', '')}")
        print(f"Topic: {topic} ({topic_score:.2f}, {topic_reason})")
        print(f"Confidence: {confidence:.2f} ({reason})")
        print(f"Metadata status: {hub.metadata_status(item)}")
        print(f"Mode: {mode}")
        print(f"Output note: {hub.note_path_for_item(item)}")
        return 0

    if existing and (args.force or args.upgrade):
        existing_mode = str((existing.get("metadata") or {}).get("reading_mode") or "")
        print(f"Regenerating existing note: {existing.get('note_path')} ({existing_mode or 'unknown'} -> {mode})")

    try:
        if mode == "metadata-only":
            item, note_path, _model = hub.read_pdf_metadata_only(pdf_path, item)
        elif mode == "text-draft":
            item, note_path, _model = hub.read_pdf_to_text_draft(pdf_path, item)
        else:
            item, note_path, _model = hub.read_pdf_to_note(pdf_path, item, config, args.timeout)
    except RuntimeError as exc:
        print(str(exc))
        return 1
    if note_path:
        print(f"Wrote Chinese item note: {note_path}")
    else:
        print("Updated metadata only; no item note written.")
    print(f"Updated item store: {hub.ITEMS_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
