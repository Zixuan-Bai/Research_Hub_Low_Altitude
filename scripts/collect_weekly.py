"""Collect weekly low-altitude research-intelligence items and write a Chinese digest."""

from __future__ import annotations

import argparse
from pathlib import Path

import research_hub_lib as hub


def main() -> int:
    parser = argparse.ArgumentParser(description="Collect weekly research-intelligence items.")
    parser.add_argument("--topic", default="all", help="Topic key, topic slug, or all.")
    parser.add_argument("--config", default=str(hub.DEFAULT_CONFIG), help="Pipeline config JSON.")
    parser.add_argument("--providers", default="", help="Comma-separated providers. Defaults to config discovery_providers.")
    parser.add_argument("--limit-per-keyword", type=int, default=None, help="Metadata results per keyword/provider.")
    parser.add_argument("--max-keywords", type=int, default=None, help="Maximum seed keywords per topic.")
    parser.add_argument("--context-config", default=str(hub.DEFAULT_CONTEXT_CONFIG), help="Context source JSON for RSS/manual URLs.")
    parser.add_argument("--date", default=None, help="Digest date, YYYY-MM-DD. Defaults to today.")
    parser.add_argument("--dry-run", action="store_true", help="Show planned work without network calls or file writes.")
    args = parser.parse_args()

    config = hub.load_config(Path(args.config))
    query_files = hub.selected_query_files(args.topic, config)
    providers = [provider.strip() for provider in args.providers.split(",") if provider.strip()]
    if not providers:
        providers = list(config.get("discovery_providers") or ["openalex", "crossref", "arxiv", "semantic_scholar"])
    limit = args.limit_per_keyword if args.limit_per_keyword is not None else int(config.get("limit_per_keyword", 10))
    max_keywords = args.max_keywords if args.max_keywords is not None else int(config.get("max_keywords_per_topic", 4))

    if args.dry_run:
        print("Weekly collection dry run.")
        print(f"Topics: {', '.join(str(path) for path in query_files)}")
        print(f"Providers: {', '.join(providers)}")
        print(f"Limit per keyword: {limit}")
        print(f"Max keywords per topic: {max_keywords}")
        print(f"Context sources: {args.context_config}")
        return 0

    run_items = []
    for query_file in query_files:
        topic_items = hub.collect_topic_items(query_file, providers, limit, max_keywords)
        run_items.extend(topic_items)
        query_data = hub.parse_simple_query_yaml(query_file)
        print(f"Collected {len(topic_items)} item(s) for {query_data['topic']}.")
    context_items = hub.collect_context_sources(Path(args.context_config))
    run_items.extend(context_items)
    if context_items:
        print(f"Collected {len(context_items)} context item(s) from RSS/manual URL sources.")

    all_items, changed_items = hub.upsert_items(run_items)
    digest_path = hub.write_weekly_digest(all_items, changed_items, args.date)
    dashboard_path = hub.write_review_dashboard(all_items)
    print(f"Wrote weekly digest: {digest_path}")
    print(f"Wrote review dashboard: {dashboard_path}")
    print(f"Item store: {hub.ITEMS_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
