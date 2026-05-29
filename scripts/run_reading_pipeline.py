"""Read downloaded PDFs with a multimodal model and update Level 0 artifacts.

This pipeline only processes PDFs that are already available locally. It does
not download restricted papers, commit raw PDFs, or mark anything as human
reviewed.
"""

from __future__ import annotations

import argparse
import base64
import csv
import hashlib
import json
import os
import re
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


REVIEW_FIELDS = [
    "item_id",
    "item_type",
    "topic",
    "title",
    "reason",
    "recommended_action",
    "status",
    "source_path",
    "added_at",
]


PAPER_FIELDS = [
    "paper_id",
    "title",
    "authors",
    "year",
    "venue",
    "doi",
    "url",
    "topic",
    "source_type",
    "venue_tier",
    "source_trust",
    "reading_status",
    "relevance",
    "practical_relevance",
    "metadata_confidence",
    "notes_path",
    "source",
]


ARTIFACT_DIRS = [
    "literature/notes/paper_notes",
    "literature/notes/figure_table_notes",
    "literature/notes/claims",
    "topics/evidence_maps",
    "topics/briefs",
    "route_cards/candidates",
]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def stable_id(*parts: str) -> str:
    source = "|".join(part.strip().lower() for part in parts if part)
    return hashlib.sha1(source.encode("utf-8")).hexdigest()[:12]


def slugify(value: str) -> str:
    chars = []
    for char in value.lower():
        if char.isalnum():
            chars.append(char)
        elif chars and chars[-1] != "_":
            chars.append("_")
    return "".join(chars).strip("_") or "paper"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists() or path.stat().st_size == 0:
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def append_review(reason: str, action: str, source_path: Path, topic: str, title: str, dry_run: bool) -> None:
    queue_path = Path("literature/database/review_queue.csv")
    item_id = stable_id("reading", str(source_path), reason)
    if dry_run:
        print(f"Would queue review: {title or source_path.name} [{reason}]")
        return
    rows = read_csv(queue_path)
    if any(row.get("item_id") == item_id for row in rows):
        return
    rows.append(
        {
            "item_id": item_id,
            "item_type": "reading_pipeline_item",
            "topic": topic,
            "title": title,
            "reason": reason,
            "recommended_action": action,
            "status": "pending",
            "source_path": str(source_path),
            "added_at": now_iso(),
        }
    )
    write_csv(queue_path, REVIEW_FIELDS, rows)


def load_candidates() -> dict[str, dict[str, str]]:
    return {row.get("candidate_id", ""): row for row in read_csv(Path("literature/database/paper_candidates.csv")) if row.get("candidate_id")}


def match_candidate(pdf_path: Path, candidates: dict[str, dict[str, str]]) -> dict[str, str]:
    stem = pdf_path.stem.lower()
    for candidate_id, row in candidates.items():
        if candidate_id and candidate_id.lower() in stem:
            return row
    return {}


def discover_pdfs(inbox: Path, open_access_dir: Path) -> list[Path]:
    paths: list[Path] = []
    for directory in [inbox, open_access_dir]:
        if directory.exists():
            paths.extend(sorted(directory.glob("*.pdf")))
    seen = set()
    unique = []
    for path in paths:
        resolved = path.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        unique.append(path)
    return unique


def note_has_fingerprint(note_path: Path, fingerprint: str) -> bool:
    if not note_path.exists():
        return False
    return fingerprint in note_path.read_text(encoding="utf-8", errors="ignore")


def paper_id_for(pdf_path: Path, candidate: dict[str, str]) -> str:
    return candidate.get("candidate_id") or slugify(pdf_path.stem)


def build_prompt(candidate: dict[str, str], fingerprint: str) -> str:
    metadata = json.dumps(candidate, ensure_ascii=False, indent=2)
    return f"""You are reading a PDF for a Level 0 low-altitude research-intelligence hub.

Repository rules:
- Do not fabricate DOI, authors, venue, year, datasets, standards, or numerical results.
- Separate `paper-supported`, `inferred`, `proposal`, and `unsupported`.
- The repository must not contain full-text dumps.
- `full-text parsed` means the model processed the paper; it does not mean human reviewed.
- Do not claim a research gap unless at least three relevant papers have been compared.
- Do not recommend a Level 1 implementation repository.

Use both text and visual page information from the PDF. Pay special attention to figures, tables, system diagrams, experiment curves, parameter tables, baselines, datasets, metrics, and architecture diagrams.

Known metadata:
```json
{metadata}
```

PDF fingerprint: {fingerprint}

Return one Markdown paper note with these sections exactly:
# Paper Note
## Metadata
## Reading Provenance
## Problem
## Method
## Key Assumptions
## Evidence
## Visual Evidence
## Limitations
## Reusable Knowledge
## Useful For This Hub
## Claims Ledger
## Possible Follow-up Route
## Practicality Check
## Reliability Notes

Every substantive bullet must start with one of:
- `paper-supported:`
- `inferred:`
- `proposal:`
- `unsupported:`

If the paper does not provide enough information for a section, write `unsupported: not available from the parsed PDF`.
"""


def openai_pdf_read(pdf_path: Path, prompt: str, model: str, api_key: str, timeout: int) -> str:
    encoded = base64.b64encode(pdf_path.read_bytes()).decode("ascii")
    payload = {
        "model": model,
        "input": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_file",
                        "filename": pdf_path.name,
                        "file_data": f"data:application/pdf;base64,{encoded}",
                    },
                    {
                        "type": "input_text",
                        "text": prompt,
                    },
                ],
            }
        ],
    }
    request = urllib.request.Request(
        "https://api.openai.com/v1/responses",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        data = json.loads(response.read().decode("utf-8"))
    if data.get("output_text"):
        return str(data["output_text"])
    output_parts = []
    for item in data.get("output", []):
        for content in item.get("content", []):
            if content.get("type") in {"output_text", "text"}:
                output_parts.append(content.get("text", ""))
    return "\n".join(part for part in output_parts if part).strip()


def extract_section(markdown: str, heading: str) -> str:
    pattern = re.compile(rf"^## {re.escape(heading)}\s*$", re.MULTILINE)
    match = pattern.search(markdown)
    if not match:
        return "unsupported: section not found in generated paper note."
    start = match.end()
    next_match = re.search(r"^## .+$", markdown[start:], re.MULTILINE)
    end = start + next_match.start() if next_match else len(markdown)
    return markdown[start:end].strip() or "unsupported: section was empty."


def write_support_artifacts(paper_id: str, topic: str, title: str, note: str, model: str, fingerprint: str) -> None:
    visual = extract_section(note, "Visual Evidence")
    claims = extract_section(note, "Claims Ledger")
    header = [
        f"- Paper ID: {paper_id}",
        f"- Topic: {topic}",
        f"- Title: {title}",
        f"- Reading model: {model}",
        f"- PDF fingerprint: {fingerprint}",
        f"- Generated at: {now_iso()}",
        "",
    ]
    figure_path = Path("literature/notes/figure_table_notes") / f"{paper_id}.md"
    claims_path = Path("literature/notes/claims") / f"{paper_id}.md"
    figure_path.write_text("# Figure and Table Note\n\n" + "\n".join(header) + "## Visual Evidence\n\n" + visual + "\n", encoding="utf-8")
    claims_path.write_text("# Claims Ledger\n\n" + "\n".join(header) + "## Claims\n\n" + claims + "\n", encoding="utf-8")


def upsert_paper_database(row: dict[str, str], paper_id: str, note_path: Path, pdf_path: Path) -> None:
    database = Path("literature/database/papers.csv")
    rows = read_csv(database)
    existing = {item.get("paper_id", ""): item for item in rows}
    target = existing.get(paper_id, {})
    target.update(
        {
            "paper_id": paper_id,
            "title": row.get("title", "") or pdf_path.stem,
            "authors": row.get("authors", ""),
            "year": row.get("year", ""),
            "venue": row.get("venue", ""),
            "doi": row.get("doi", ""),
            "url": row.get("url", ""),
            "topic": row.get("topic", ""),
            "source_type": row.get("source_type", "academic_paper") or "academic_paper",
            "venue_tier": row.get("venue_tier", "unknown") or "unknown",
            "source_trust": row.get("source_trust", "unknown") or "unknown",
            "reading_status": "full-text parsed",
            "relevance": row.get("auto_relevance_label", "") or row.get("relevance", ""),
            "practical_relevance": row.get("practical_relevance", ""),
            "metadata_confidence": row.get("metadata_confidence", "low") or "low",
            "notes_path": str(note_path),
            "source": str(pdf_path),
        }
    )
    if paper_id in existing:
        rows = [target if item.get("paper_id") == paper_id else item for item in rows]
    else:
        rows.append(target)
    write_csv(database, PAPER_FIELDS, rows)


def write_topic_artifacts(topic: str, processed: list[dict[str, str]], dry_run: bool) -> None:
    if not processed:
        return
    evidence_path = Path("topics/evidence_maps") / f"{topic}.md"
    brief_path = Path("topics/briefs") / f"{topic}.md"
    route_path = Path("route_cards/candidates") / f"{topic}_machine_draft.md"
    generated_at = now_iso()
    note_links = "\n".join(f"- {item['title']} - {item['note_path']}" for item in processed)
    evidence_version = stable_id(topic, generated_at, *[item["fingerprint"] for item in processed])

    evidence = f"""# Evidence Map

## Topic

{topic}

## Evidence Version

- evidence_version: {evidence_version}
- generated_at: {generated_at}
- generated_from_notes:
{note_links}

## Evidence Table

| Claim / Observation | Source Type | Supporting Academic Sources | Supporting Practical Sources | Evidence Type | Source Quality | Practical Relevance | Strength | Notes |
|---|---|---|---|---|---|---|---|---|
| Machine aggregation pending human review | inferred | {len(processed)} parsed paper notes | missing practical context unless listed in context_sources.csv | survey / model reading | medium | unknown | medium | Review paper notes and context sources before accepting any gap. |

## Gap Candidates

No gap is accepted by this machine draft. Per AGENTS.md, at least three relevant papers must be compared and practical context must be checked before a gap can support a route.

## Unsupported or Speculative Ideas

- proposal: Candidate routes may be generated from the parsed notes, but they remain watch items until human review.
"""

    brief = f"""# Topic Brief

## Topic Name

{topic}

## Evidence Version

- evidence_version: {evidence_version}
- last_refresh_at: {generated_at}

## Literature Base

{note_links}

## Source Quality Assessment

Machine draft only. Audit venue tier, source trust, and practical grounding before using this brief for route decisions.

## Practical Context

unsupported: practical context must be checked in `literature/database/context_sources.csv` and context notes.

## Possible Research Gaps

unsupported: no research gap is accepted by this draft.

## Candidate Route Cards

- route_cards/candidates/{topic}_machine_draft.md

## Decision

continue surveying
"""

    route = f"""# Route Card

## Route ID

{topic}_machine_draft

## Candidate Title

Machine draft from parsed paper notes for {topic}

## Parent Topic

{topic}

## One-sentence Claim

proposal: This is a watch-only route draft generated from parsed notes.

## Core Research Question

unsupported: requires human review and comparison against practical context.

## Why This Problem Matters

inferred: parsed paper notes suggest the topic may be relevant to low-altitude communication, but deployment relevance is not accepted yet.

## Literature Basis

{note_links}

## Practical Context Basis

unsupported: missing or unreviewed practical context.

## Gap

unsupported: no accepted gap. At least three relevant papers and practical context must be compared.

## Proposed Angle

proposal: inspect parsed notes for model assumptions, visual evidence, baselines, and parameter gaps.

## Minimal Model

unsupported: not selected.

## Possible Method

- simulation model
- analytical model
- measurement study

## Expected Evidence

unsupported: expected figures, tables, proofs, or simulations are not yet accepted.

## Deployment Reality Check

- existing system evidence: needs review
- policy or standard relevance: needs review
- industry roadmap relevance: needs review
- parameters requiring practical validation: needs review
- deployment uncertainty: high

## Baselines

unsupported: not selected.

## Feasibility

- required data: needs review
- required simulator: needs review
- required compute: needs review
- required domain knowledge: needs review
- expected time: needs review

## Risk

- novelty risk: high until literature comparison is complete
- modeling risk: high until minimal model is selected
- experiment risk: unknown
- writing risk: high until evidence map is human reviewed

## Paperability Score

0

## Decision

watch

## Repository Proposal Needed?

no

## Human Decision

needs_human_review
"""

    if dry_run:
        print(f"Would write {evidence_path}, {brief_path}, and {route_path}.")
        return
    evidence_path.parent.mkdir(parents=True, exist_ok=True)
    brief_path.parent.mkdir(parents=True, exist_ok=True)
    route_path.parent.mkdir(parents=True, exist_ok=True)
    evidence_path.write_text(evidence, encoding="utf-8")
    brief_path.write_text(brief, encoding="utf-8")
    route_path.write_text(route, encoding="utf-8")
    print(f"Wrote topic artifacts for {topic}.")


def main() -> int:
    parser = argparse.ArgumentParser(description="Read local PDFs and generate Level 0 knowledge artifacts.")
    parser.add_argument("--topic", default="all", help="Topic slug or 'all'.")
    parser.add_argument("--inbox", default="literature/inbox/papers", help="Directory containing manually downloaded PDFs.")
    parser.add_argument("--open-access-dir", default="literature/pdfs/open_access", help="Directory containing open-access PDFs.")
    parser.add_argument("--model", default=os.environ.get("OPENAI_READING_MODEL", "gpt-5.5"), help="OpenAI model for multimodal PDF reading.")
    parser.add_argument("--max-papers", type=int, default=5, help="Maximum PDFs to process in one run.")
    parser.add_argument("--timeout", type=int, default=300, help="OpenAI request timeout in seconds.")
    parser.add_argument("--force", action="store_true", help="Re-read PDFs even if the fingerprint already appears in the note.")
    parser.add_argument("--dry-run", action="store_true", help="Show planned work without writing or calling OpenAI.")
    args = parser.parse_args()

    for directory in ARTIFACT_DIRS:
        if not args.dry_run:
            Path(directory).mkdir(parents=True, exist_ok=True)

    candidates = load_candidates()
    pdfs = discover_pdfs(Path(args.inbox), Path(args.open_access_dir))
    if not pdfs:
        print("No local PDFs found. Nothing to read.")
        return 0

    api_key = os.environ.get("OPENAI_API_KEY", "")
    processed_by_topic: dict[str, list[dict[str, str]]] = {}
    processed_count = 0

    for pdf_path in pdfs:
        candidate = match_candidate(pdf_path, candidates)
        topic = candidate.get("topic", "") or "unknown_topic"
        if args.topic != "all" and topic != args.topic:
            continue
        paper_id = paper_id_for(pdf_path, candidate)
        title = candidate.get("title", "") or pdf_path.stem
        fingerprint = sha256_file(pdf_path)
        note_path = Path("literature/notes/paper_notes") / f"{paper_id}.md"
        if not args.force and note_has_fingerprint(note_path, fingerprint):
            print(f"Skipped already-read PDF: {pdf_path}")
            continue
        if processed_count >= args.max_papers:
            break
        if args.dry_run:
            print(f"Would read {pdf_path} -> {note_path}")
            processed_count += 1
            continue
        if not api_key:
            append_review("OPENAI_API_KEY missing", "Set OPENAI_API_KEY, then rerun run_reading_pipeline.py.", pdf_path, topic, title, args.dry_run)
            print(f"Queued {pdf_path}: OPENAI_API_KEY missing.")
            continue

        prompt = build_prompt(candidate, fingerprint)
        try:
            note = openai_pdf_read(pdf_path, prompt, args.model, api_key, args.timeout)
        except Exception as exc:
            append_review(f"OpenAI PDF reading failed: {exc}", "Inspect the PDF, API key, model, and size limits, then rerun.", pdf_path, topic, title, args.dry_run)
            print(f"Failed to read {pdf_path}: {exc}")
            continue
        if not note.strip():
            append_review("OpenAI returned empty note", "Rerun with a different model or inspect the PDF manually.", pdf_path, topic, title, args.dry_run)
            continue

        provenance = [
            "",
            "<!-- reading_metadata",
            json.dumps(
                {
                    "reading_model": args.model,
                    "read_at": now_iso(),
                    "pdf_fingerprint": fingerprint,
                    "pdf_source": str(pdf_path),
                    "reading_status": "full-text parsed",
                    "human_reviewed": False,
                },
                ensure_ascii=False,
                indent=2,
            ),
            "-->",
            "",
        ]
        note_path.parent.mkdir(parents=True, exist_ok=True)
        note_path.write_text(note.rstrip() + "\n" + "\n".join(provenance), encoding="utf-8")
        write_support_artifacts(paper_id, topic, title, note, args.model, fingerprint)
        upsert_paper_database(candidate, paper_id, note_path, pdf_path)
        processed_by_topic.setdefault(topic, []).append(
            {
                "title": title,
                "note_path": str(note_path),
                "fingerprint": fingerprint,
            }
        )
        processed_count += 1
        print(f"Read {pdf_path} -> {note_path}")

    for topic, processed in processed_by_topic.items():
        write_topic_artifacts(topic, processed, args.dry_run)

    print(f"Processed {processed_count} PDF(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
