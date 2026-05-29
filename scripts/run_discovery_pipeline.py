"""Run the recurring literature-discovery pipeline.

This pipeline is intentionally metadata-only. It refreshes paper candidates,
download queues, and review queues, but it does not read PDFs or generate
research conclusions.
"""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


DEFAULT_CONFIG = "configs/pipeline.json"
DEFAULT_PROVIDERS = ["openalex", "crossref", "arxiv", "semantic_scholar"]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def run(command: list[str], dry_run: bool = False) -> int:
    print("$ " + " ".join(command))
    if dry_run:
        return 0
    return subprocess.call(command)


def load_config(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def select_topics(config: dict, topic: str) -> dict[str, str]:
    topics = config.get("topics", {})
    if topic == "all":
        return topics
    if topic not in topics:
        raise SystemExit(f"Unknown topic '{topic}'. Available: {', '.join(topics)}")
    return {topic: topics[topic]}


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists() or path.stat().st_size == 0:
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_weekly_digest(path: Path, candidates_path: Path, review_queue_path: Path, run_id: str, topic: str) -> None:
    candidates = read_csv(candidates_path)
    reviews = read_csv(review_queue_path)
    new_candidates = [row for row in candidates if row.get("discovery_run_id") == run_id]
    high_value = [
        row for row in new_candidates
        if row.get("auto_relevance_label") == "high" or row.get("venue_tier") in {"top", "strong"}
    ]
    download_items = [row for row in reviews if row.get("reason") == "PDF requires user access"]

    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Weekly Literature Discovery Digest",
        "",
        f"- Generated at: {now_iso()}",
        f"- Discovery run ID: {run_id}",
        f"- Topic selector: {topic}",
        f"- New or refreshed candidates in this run: {len(new_candidates)}",
        f"- High-value candidates to inspect: {len(high_value)}",
        f"- Download queue items: {len(download_items)}",
        "",
        "## High-Value Candidates",
        "",
    ]
    if high_value:
        for row in high_value[:20]:
            lines.append(f"- [{row.get('topic', '')}] {row.get('title', '')} ({row.get('year', '')}) - {row.get('venue', '') or 'venue unknown'}")
    else:
        lines.append("- None detected in this run.")
    lines.extend(
        [
            "",
            "## Human Attention",
            "",
            "Use Notion or `literature/database/review_queue.csv` as the review surface. Focus on high-value missing PDFs, practical-context gaps, and unknown venue quality.",
            "",
            "## Level 0 Boundary",
            "",
            "This digest is metadata-only. It does not prove novelty, summarize full papers, or recommend a Level 1 repository.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {path}.")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run recurring literature discovery.")
    parser.add_argument("--config", default=DEFAULT_CONFIG, help="Pipeline JSON config.")
    parser.add_argument("--topic", default="all", help="Topic key from config, or 'all'.")
    parser.add_argument("--provider", default="", help="Backward-compatible alias for one provider.")
    parser.add_argument("--providers", default="", help="Comma-separated providers. Default: config discovery_providers or all supported providers.")
    parser.add_argument("--limit", type=int, default=None, help="Override per-keyword result limit.")
    parser.add_argument("--max-keywords", type=int, default=None, help="Override max keywords per topic.")
    parser.add_argument("--from-updated-date", default="", help="Optional incremental lower bound in YYYY-MM-DD form.")
    parser.add_argument("--download-pdfs", action="store_true", help="Try to download open-access PDFs.")
    parser.add_argument("--write-digest", action="store_true", help="Write a Markdown weekly digest under outputs/weekly.")
    parser.add_argument("--dry-run", action="store_true", help="Show commands without executing them.")
    args = parser.parse_args()

    config = load_config(Path(args.config))
    configured_providers = config.get("discovery_providers") or [config.get("default_provider", "openalex")]
    providers_arg = args.providers or args.provider
    providers = [value.strip() for value in providers_arg.split(",") if value.strip()] or configured_providers or DEFAULT_PROVIDERS
    limit = args.limit or int(config.get("limit_per_keyword", 10))
    max_keywords = args.max_keywords or int(config.get("max_keywords_per_topic", 4))
    topics = select_topics(config, args.topic)
    run_id = f"discovery-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"

    commands: list[list[str]] = [[sys.executable, "scripts/validate_hub.py"]]
    for provider in providers:
        for _, query_file in topics.items():
            command = [
                sys.executable,
                "scripts/search_literature.py",
                "--query-file",
                query_file,
                "--provider",
                provider,
                "--limit",
                str(limit),
                "--max-keywords",
                str(max_keywords),
                "--discovery-run-id",
                run_id,
            ]
            if args.from_updated_date:
                command.extend(["--from-updated-date", args.from_updated_date])
            commands.append(command)
    commands.append([sys.executable, "scripts/classify_candidates.py"])

    should_download = args.download_pdfs or bool(config.get("download_open_access_pdfs", False))
    if should_download:
        commands.append([sys.executable, "scripts/fetch_open_access_pdfs.py"])

    for command in commands:
        code = run(command, dry_run=args.dry_run)
        if code != 0:
            return code

    if args.write_digest and not args.dry_run:
        digest_path = Path("outputs/weekly") / f"{run_id}.md"
        write_weekly_digest(digest_path, Path("literature/database/paper_candidates.csv"), Path("literature/database/review_queue.csv"), run_id, args.topic)
    elif args.write_digest:
        print(f"Would write outputs/weekly/{run_id}.md")

    print(f"Discovery run ID: {run_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
