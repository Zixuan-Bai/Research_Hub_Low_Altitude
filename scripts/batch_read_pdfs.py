"""Batch-read local PDFs, skipping files that already have item notes."""

from __future__ import annotations

import argparse
from pathlib import Path

import research_hub_lib as hub


def parse_providers(value: str) -> list[str]:
    providers = [provider.strip() for provider in value.split(",") if provider.strip()]
    return [] if providers == ["none"] else providers


def discover_pdfs(pdf_dir: Path) -> list[Path]:
    if pdf_dir.is_file() and pdf_dir.suffix.lower() == ".pdf":
        return [pdf_dir]
    if not pdf_dir.exists():
        return []
    return sorted(path for path in pdf_dir.rglob("*.pdf") if path.is_file())


def choose_topic(pdf_path: Path, requested_topic: str, config: dict) -> tuple[str, float, str]:
    return hub.resolve_topic_for_pdf(pdf_path, requested_topic, config)


def main() -> int:
    parser = argparse.ArgumentParser(description="Batch read PDFs into Chinese item notes.")
    parser.add_argument("--pdf-dir", default="literature/inbox/papers", help="PDF file or directory to scan.")
    parser.add_argument("--topic", default="auto", help="Topic key/slug, or auto.")
    parser.add_argument("--config", default=str(hub.DEFAULT_CONFIG), help="Pipeline config JSON.")
    parser.add_argument("--providers", default="openalex,crossref,semantic_scholar", help="Metadata lookup providers, or none.")
    parser.add_argument("--lookup-limit", type=int, default=3, help="Metadata lookup result limit per provider.")
    parser.add_argument("--max-items", type=int, default=0, help="Maximum PDFs to read in this run. 0 means no limit.")
    parser.add_argument("--timeout", type=int, default=300, help="Kimi request timeout in seconds per PDF.")
    parser.add_argument(
        "--mode",
        choices=["auto", "metadata-only", "text-draft", "kimi"],
        default="auto",
        help="Reading mode. auto uses kimi only when a Kimi/Moonshot API key is present; otherwise text-draft.",
    )
    parser.add_argument("--force", action="store_true", help="Re-read PDFs even when an existing note is found.")
    parser.add_argument("--dry-run", action="store_true", help="List planned work without API calls or writes.")
    args = parser.parse_args()

    hub.load_env_file()
    config = hub.load_config(Path(args.config))
    mode = args.mode
    if mode == "auto":
        mode = "kimi" if hub.has_kimi_api_key(config) else "text-draft"
    providers = parse_providers(args.providers)
    pdfs = discover_pdfs(Path(args.pdf_dir))
    items = hub.load_items()

    planned: list[tuple[Path, str, float, str]] = []
    skipped = 0
    for pdf_path in pdfs:
        existing = hub.find_existing_note_for_pdf(pdf_path, items)
        if not args.force and existing:
            if not args.dry_run:
                hub.sync_existing_item_for_pdf(pdf_path, existing)
            skipped += 1
            continue
        topic, score, reason = choose_topic(pdf_path, args.topic, config)
        planned.append((pdf_path, topic, score, reason))
        if args.max_items and len(planned) >= args.max_items:
            break

    print(f"Found PDFs: {len(pdfs)}")
    print(f"Skipped existing notes: {skipped}")
    print(f"Planned reads: {len(planned)}")
    print(f"Mode: {mode}")
    for pdf_path, topic, score, reason in planned:
        print(f"- {pdf_path} -> topic `{topic}` ({score:.2f}, {reason})")

    if args.dry_run or not planned:
        return 0

    failures = 0
    for pdf_path, topic, _score, topic_reason in planned:
        try:
            item, confidence, match_reason = hub.prepare_pdf_item(pdf_path, topic, providers, args.lookup_limit)
            item.setdefault("metadata", {})["topic_inference_reason"] = topic_reason
            if mode == "metadata-only":
                item, note_path, model = hub.read_pdf_metadata_only(pdf_path, item)
            elif mode == "text-draft":
                item, note_path, model = hub.read_pdf_to_text_draft(pdf_path, item)
            else:
                item, note_path, model = hub.read_pdf_to_note(pdf_path, item, config, args.timeout)
            if note_path:
                print(f"Wrote note: {note_path} ({model}; metadata {confidence:.2f}, {match_reason})")
            else:
                print(f"Updated metadata only: {item.get('id')} ({model}; metadata {confidence:.2f}, {match_reason})")
        except Exception as exc:
            failures += 1
            print(f"Failed: {pdf_path}: {exc}")

    print(f"Completed: {len(planned) - failures}; failed: {failures}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
