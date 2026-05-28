"""Validate the lightweight Level 0 research hub skeleton."""

from __future__ import annotations

from pathlib import Path


REQUIRED_DIRS = [
    "docs",
    "literature/inbox/papers",
    "literature/database",
    "literature/notes/paper_notes",
    "literature/notes/context_notes",
    "literature/notes/survey_notes",
    "literature/pdfs/open_access",
    "literature/queries",
    "topics/candidates",
    "topics/templates",
    "route_cards/candidates",
    "route_cards/templates",
    "prompts",
    "rubrics",
    "scripts",
    "outputs/tmp",
]

REQUIRED_FILES = [
    "README.md",
    "AGENTS.md",
    ".gitignore",
    "docs/workflow.md",
    "docs/repository_boundary.md",
    "docs/mcp_skill_roadmap.md",
    "docs/tooling_guide.md",
    "docs/automation_workflow.md",
    "literature/database/papers.csv",
    "literature/database/paper_candidates.csv",
    "literature/database/acquisition_queue.csv",
    "literature/database/review_queue.csv",
    "literature/database/context_sources.csv",
    "literature/database/papers.bib",
    "literature/database/paper_index.jsonl",
    "literature/queries/remote_id.yaml",
    "literature/queries/dtmb_broadcast.yaml",
    "literature/queries/formation_safety.yaml",
    "literature/queries/directional_networking.yaml",
    "literature/notes/paper_notes/template.md",
    "literature/notes/context_notes/template.md",
    "topics/templates/topic_candidate.md",
    "topics/templates/topic_brief.md",
    "topics/templates/evidence_map.md",
    "topics/templates/open_questions.md",
    "topics/candidates/remote_id_broadcast_capacity.md",
    "topics/candidates/dtmb_uav_control.md",
    "topics/candidates/formation_safety_boundary.md",
    "topics/candidates/dynamic_directional_networking.md",
    "route_cards/templates/route_card.md",
    "prompts/literature_search.md",
    "prompts/paper_reading.md",
    "prompts/evidence_mapping.md",
    "prompts/topic_synthesis.md",
    "prompts/route_generation.md",
    "prompts/route_review.md",
    "rubrics/paper_relevance_rubric.md",
    "rubrics/topic_potential_rubric.md",
    "rubrics/route_feasibility_rubric.md",
    "rubrics/paperability_rubric.md",
    "rubrics/source_quality_rubric.md",
    "rubrics/practical_relevance_rubric.md",
    "scripts/import_local_pdfs.py",
    "scripts/search_literature.py",
    "scripts/classify_candidates.py",
    "scripts/run_pipeline.py",
    "scripts/fetch_open_access_pdfs.py",
    "scripts/rank_routes.py",
    "scripts/validate_hub.py",
    ".github/workflows/validate.yml",
    ".github/workflows/literature_pipeline.yml",
    "configs/pipeline.json",
]

ALLOWED_EMPTY_FILES = {
    "literature/database/paper_index.jsonl",
    "literature/inbox/papers/.gitkeep",
    "literature/notes/paper_notes/.gitkeep",
    "literature/notes/context_notes/.gitkeep",
    "literature/notes/survey_notes/.gitkeep",
    "literature/pdfs/open_access/.gitkeep",
    "route_cards/candidates/.gitkeep",
    "outputs/tmp/.gitkeep",
}


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
        if ".git" in path.parts:
            continue
        if not path.is_file():
            continue
        relative = path.as_posix()
        if path.stat().st_size == 0 and relative not in ALLOWED_EMPTY_FILES:
            errors.append(f"Unexpected empty file: {relative}")

    if errors:
        print("Hub validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Hub validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
