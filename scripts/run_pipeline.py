"""Run the default unattended literature-discovery pipeline.

Default behavior is intentionally conservative:
- search metadata for every configured topic;
- classify source quality automatically;
- generate review_queue.csv for the small set of human decisions;
- do not download PDFs unless explicitly enabled.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


DEFAULT_CONFIG = "configs/pipeline.json"


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


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the low-altitude research hub pipeline.")
    parser.add_argument("--config", default=DEFAULT_CONFIG, help="Pipeline JSON config.")
    parser.add_argument("--topic", default="all", help="Topic key from config, or 'all'.")
    parser.add_argument("--provider", default=None, help="Override metadata provider.")
    parser.add_argument("--limit", type=int, default=None, help="Override per-keyword result limit.")
    parser.add_argument("--max-keywords", type=int, default=None, help="Override max keywords per topic.")
    parser.add_argument("--download-pdfs", action="store_true", help="Try to download open-access PDFs.")
    parser.add_argument("--dry-run", action="store_true", help="Show commands without executing them.")
    args = parser.parse_args()

    config = load_config(Path(args.config))
    provider = args.provider or config.get("default_provider", "openalex")
    limit = args.limit or int(config.get("limit_per_keyword", 10))
    max_keywords = args.max_keywords or int(config.get("max_keywords_per_topic", 4))
    topics = select_topics(config, args.topic)

    commands: list[list[str]] = [[sys.executable, "scripts/validate_hub.py"]]
    for _, query_file in topics.items():
        commands.append(
            [
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
            ]
        )
    commands.append([sys.executable, "scripts/classify_candidates.py"])

    should_download = args.download_pdfs or bool(config.get("download_open_access_pdfs", False))
    if should_download:
        commands.append([sys.executable, "scripts/fetch_open_access_pdfs.py"])

    for command in commands:
        code = run(command, dry_run=args.dry_run)
        if code != 0:
            return code
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
