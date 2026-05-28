"""Validate route cards and prepare a conservative ranking skeleton.

This script checks route-card completeness. It does not judge scientific
novelty and does not generate final research conclusions.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


REQUIRED_SECTIONS = [
    "## Route ID",
    "## Candidate Title",
    "## Parent Topic",
    "## Core Research Question",
    "## Literature Basis",
    "## Gap",
    "## Minimal Model",
    "## Expected Evidence",
    "## Baselines",
    "## Feasibility",
    "## Risk",
    "## Decision",
]


def inspect_route(path: Path) -> dict[str, object]:
    text = path.read_text(encoding="utf-8")
    missing = [section for section in REQUIRED_SECTIONS if section not in text]
    return {
        "path": str(path),
        "complete": not missing,
        "missing_sections": missing,
        "decision": "needs_human_review",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Check route-card completeness.")
    parser.add_argument("--route-dir", default="route_cards/candidates", help="Directory containing route cards.")
    parser.add_argument("--rubric", default="rubrics/route_feasibility_rubric.md", help="Route feasibility rubric.")
    parser.add_argument("--output", default="outputs/tmp/route_rank_check.json", help="Output JSON path.")
    parser.add_argument("--dry-run", action="store_true", help="Print planned output without writing.")
    args = parser.parse_args()

    route_dir = Path(args.route_dir)
    rubric = Path(args.rubric)
    output = Path(args.output)

    if not rubric.exists():
        print(f"Missing rubric: {rubric}")
        return 1

    cards = sorted(path for path in route_dir.glob("*.md") if path.name != ".gitkeep") if route_dir.exists() else []
    if not cards:
        print(f"No route cards found in {route_dir}. Nothing to rank.")
        return 0

    report = {
        "rubric": str(rubric),
        "route_dir": str(route_dir),
        "note": "Completeness check only; no scientific ranking is produced.",
        "routes": [inspect_route(path) for path in cards],
    }

    print(json.dumps(report, ensure_ascii=False, indent=2))
    if args.dry_run:
        print("Dry run only. No files were written.")
        return 0

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {output}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
