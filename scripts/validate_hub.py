"""Validate the lightweight research-intelligence mainline."""

from __future__ import annotations

import json
from pathlib import Path


REQUIRED_DIRS = [
    "data",
    "docs",
    "literature/inbox/papers",
    "literature/queries",
    "notes/items",
    "outputs/weekly",
    "scripts",
    "topics",
]

REQUIRED_FILES = [
    "README.md",
    "AGENTS.md",
    ".gitignore",
    ".env.example",
    "requirements.txt",
    "configs/pipeline.json",
    "codex_refactor_request_low_altitude_research_hub.md",
    "data/items.jsonl",
    "data/manual_items.jsonl",
    "literature/inbox/papers/.gitkeep",
    "literature/queries/remote_id.yaml",
    "literature/queries/dtmb_broadcast.yaml",
    "literature/queries/formation_safety.yaml",
    "literature/queries/directional_networking.yaml",
    "scripts/research_hub_lib.py",
    "scripts/batch_read_pdfs.py",
    "scripts/collect_weekly.py",
    "scripts/read_item.py",
    "scripts/review_app.py",
    "scripts/synthesize_topic.py",
    "scripts/validate_hub.py",
    ".github/workflows/validate.yml",
    ".github/workflows/literature_pipeline.yml",
]

ALLOWED_EMPTY_FILES = {
    "data/.gitkeep",
    "data/items.jsonl",
    "data/manual_items.jsonl",
    "literature/inbox/papers/.gitkeep",
    "notes/items/.gitkeep",
    "outputs/weekly/.gitkeep",
}

ITEM_STATUSES = {
    "new",
    "kept",
    "rejected",
    "downloaded",
    "read",
    "summarized",
    "used_in_synthesis",
}
REVIEW_STATUSES = {"new", "kept", "rejected", "downloaded"}
PROCESS_STATUSES = {"unread", "read", "summarized", "used_in_synthesis"}


def validate_jsonl(path: Path, errors: list[str]) -> None:
    if not path.exists() or path.stat().st_size == 0:
        return
    for index, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append(f"Invalid JSONL at {path}:{index}: {exc}")
            continue
        for field in ["id", "title", "source_type", "topic", "status", "created_at", "updated_at"]:
            if not item.get(field):
                errors.append(f"Missing item field `{field}` at {path}:{index}")
        if item.get("status") not in ITEM_STATUSES:
            errors.append(f"Invalid status `{item.get('status')}` at {path}:{index}")
        if item.get("review_status") and item.get("review_status") not in REVIEW_STATUSES:
            errors.append(f"Invalid review_status `{item.get('review_status')}` at {path}:{index}")
        if item.get("process_status") and item.get("process_status") not in PROCESS_STATUSES:
            errors.append(f"Invalid process_status `{item.get('process_status')}` at {path}:{index}")


def main() -> int:
    root = Path(".")
    errors: list[str] = []

    for directory in REQUIRED_DIRS:
        if not (root / directory).is_dir():
            errors.append(f"Missing directory: {directory}")

    for file_path in REQUIRED_FILES:
        path = root / file_path
        if not path.is_file():
            errors.append(f"Missing file: {file_path}")

    for path in root.rglob("*"):
        if ".git" in path.parts or "__pycache__" in path.parts:
            continue
        if not path.is_file():
            continue
        relative = path.as_posix()
        if path.stat().st_size == 0 and relative not in ALLOWED_EMPTY_FILES:
            errors.append(f"Unexpected empty file: {relative}")

    validate_jsonl(root / "data/items.jsonl", errors)
    validate_jsonl(root / "data/manual_items.jsonl", errors)

    if errors:
        print("Hub validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Hub validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
