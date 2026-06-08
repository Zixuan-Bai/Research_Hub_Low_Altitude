# Codex Development Plan: Close Current Research-Intelligence MVP and Start Typed Semantic Gap Discovery

## 0. Purpose

This document defines the next development direction for `Research_Hub_Low_Altitude`.

The project should now do two things:

1. **Close the current MVP stage** by finishing the usability loop around:
   - local PDF inbox;
   - PDF registration and note generation;
   - deprecating generic follow-up actions;
   - reducing Topic Workspace maintenance burden.

2. **Start a new research-idea discovery direction** based on:
   - structured extraction from notes;
   - typed semantic atoms;
   - semantic gap candidates;
   - anchor-based idea generation.

Do not continue adding unrelated features. Do not reintroduce automatic route cards. Do not turn the repository into a general task manager.

---

## 1. Current Stage: What Should Be Closed

The repository has already moved in the right direction:

- unified item store: `data/items.jsonl`;
- Streamlit review app;
- paper database and social/context database;
- PDF reading modes: `metadata-only`, `text-draft`, `kimi`;
- topic overview and topic synthesis;
- metadata status and document-access status;
- no automatic final novelty claims.

However, several workflows are still unfinished.

### 1.1 Local PDF Inbox is not yet a natural entry point

The user expects:

```text
drop PDF into literature/inbox/papers/
-> see it in GUI
-> register it as a reviewable item
-> optionally generate text-draft or Kimi note
```

But the current workflow still requires explicit processing before the PDF appears as an item. This is unintuitive.

### 1.2 Paper items do not always expose PDF actions

A paper item should always expose a PDF action section, not only when no note exists.

The user needs to:

- bind a local PDF to an existing paper item;
- generate a note if none exists;
- upgrade a `text-draft` note to a Kimi note;
- re-read / overwrite an existing Kimi note only after explicit confirmation.

### 1.3 Topic Workspace is not useful enough

The current Topic Workspace and note-level follow-up actions create manual task lists that do not feed back into the system.

The user does not want to manually maintain:

- `research_workspace.md`;
- open/done/skipped follow-up actions;
- per-paper task lists;
- generic "continue analysis" items.

If a note recommends a concrete source, that source should become a candidate item in `data/items.jsonl`.

Generic follow-up advice should disappear.

---

## 2. Required Closeout Tasks for Current MVP

Please implement these as a small, focused refactor before starting the semantic-gap module.

### 2.1 Add PDF Inbox

Add a GUI section/tab:

```text
PDF Inbox
```

It should scan:

```text
literature/inbox/papers/
```

and display all local PDFs with:

- filename;
- path;
- SHA256 fingerprint;
- inferred title if available;
- inferred topic and confidence if available;
- whether it is already registered in `data/items.jsonl`;
- whether an item match exists;
- whether a note already exists.

For unregistered PDFs, provide buttons:

```text
Register only
Register + text-draft
Register + Kimi note
```

### 2.2 Implement `register_pdf_item()`

Expose a reusable function:

```python
register_pdf_item(
    pdf_path: Path,
    topic: str = "auto",
    providers: list[str] = ...
) -> dict
```

It should:

- infer or resolve topic;
- lookup metadata if possible;
- create/update the item;
- bind `metadata.pdf_source`;
- bind `metadata.pdf_sha256`;
- set `review_status = new`;
- set `process_status = unread`;
- set `metadata_status = needs_review` unless metadata match is high-confidence;
- not generate a note;
- return the item.

Use this function in:

- `read_item.py`;
- `batch_read_pdfs.py`;
- Streamlit PDF Inbox;
- item-card PDF binding actions.

Registration and reading should be separate operations.

### 2.3 Always show PDF actions for paper items

For every item with:

```text
source_type = paper
```

show a PDF action section.

Cases:

#### No local PDF bound

Show:

- input field to bind local PDF path;
- optional list of possible matching PDFs from `literature/inbox/papers/`;
- button: `Bind PDF`.

#### Local PDF bound, no note

Show:

- `metadata-only`;
- `text-draft`;
- `Kimi note`.

#### Existing text-draft note

Show:

- `Upgrade to Kimi note`;
- `Regenerate text-draft`;
- require confirmation before overwrite.

#### Existing Kimi note

Show:

- `Re-read / overwrite note`;
- require confirmation.

### 2.4 Add `--force` / `--upgrade` to `read_item.py`

Current safe behavior can remain:

```text
if existing note exists -> skip
```

But add explicit override:

```bash
python scripts/read_item.py paper.pdf --mode kimi --upgrade
python scripts/read_item.py paper.pdf --mode kimi --force
```

Expected behavior:

- `--force`: regenerate note even if note exists;
- `--upgrade`: allow upgrading an existing `text-draft` note to Kimi;
- write metadata:
  - `previous_reading_mode`;
  - `upgraded_at`;
  - `note_version`;
  - `overwritten_at` if applicable.

Do not silently overwrite notes.

---

## 3. Replace Generic Follow-up Actions with Related Item Extraction

### 3.1 Deprecate generic follow-up actions

Generic follow-up actions should not be shown as a major workflow.

Do not parse or preserve generic tasks such as:

```text
continue analysis
verify assumptions
compare methods
supplement background
further investigate applicability
study limitations
```

unless they name a concrete source.

### 3.2 Change note prompt

Replace note sections like:

```markdown
## 后续建议
## 后续动作
```

with:

```markdown
## 推荐入库条目

Only list concrete sources that should become candidate items.

Each item should use this structure:

- type: paper / standard / policy / report / whitepaper / news / dataset / unknown
- title_or_name:
- doi_or_url_if_available:
- reason:
- relation_to_this_item:
- confidence: high / medium / low
```

If there is no concrete source:

```markdown
- needs-review: no concrete source identified.
```

### 3.3 Add `scripts/extract_related_items.py`

Create:

```bash
python scripts/extract_related_items.py --from-notes --topic all
python scripts/extract_related_items.py --from-notes --topic remote_id
python scripts/extract_related_items.py --note notes/items/<id>.md
```

It should scan notes and extract concrete source-like objects:

- paper titles;
- DOI;
- arXiv IDs;
- explicit URLs;
- standard names/numbers;
- policy/report/whitepaper names;
- datasets or technical documents, if clearly source-like.

It should ignore generic research advice.

### 3.4 Write extracted sources into `data/items.jsonl`

For extracted items:

```json
{
  "source": "related_item_extraction",
  "source_type": "paper",
  "review_status": "new",
  "process_status": "unread",
  "metadata_status": "needs_review",
  "metadata": {
    "parent_item_id": "...",
    "parent_note_path": "notes/items/....md",
    "relation": "recommended_by_note",
    "extraction_status": "needs_review",
    "extraction_confidence": "medium",
    "extraction_reason": "mentioned in recommended sources section"
  }
}
```

For papers, use Crossref / OpenAlex / Semantic Scholar to complete metadata if possible.

For standards / policies / reports, register URL if available. If no URL is available, create a low-confidence item and leave it for review.

Do not invent URLs, DOIs, publication facts, or standard numbers.

### 3.5 Simplify Topic Workspace

Topic Workspace should not be a manually maintained task/discussion document.

Either rename it to:

```text
Topic Brief Preview
```

or keep the internal file name but change the GUI label.

It should be generated/read-only by default.

It should contain only:

```markdown
# Topic Brief Preview: <topic>

## Coverage Summary

## Evidence Base

## Social / Context Signals

## Extracted Related Items

## Synthesis Readiness

## Suggested Next System Actions
```

It should not contain:

- generic task lists;
- open/done/skipped actions;
- discussion records;
- possible paper ideas;
- route-card-like content;
- novelty claims.

Suggested system actions may include:

- run related-item extraction;
- review extracted items;
- download PDFs for kept items;
- run topic synthesis when enough notes exist.

---

## 4. After Closeout: New Direction — Typed Semantic Gap Discovery

After the PDF Inbox and related-item extraction workflows are stable, start a new module for research-idea discovery.

The goal is not to directly generate final research ideas from embeddings.

The goal is:

```text
notes -> typed research atoms -> semantic relations -> gap candidates -> human-reviewed research inspiration
```

This should be conservative, evidence-bound, and explainable.

---

## 5. Why Not Pure Embedding-Space Holes

A naive idea is:

```text
map all notes into a high-dimensional semantic space
-> find empty areas
-> treat holes as research ideas
```

This is not sufficient.

Problems:

- an empty region may just be an artifact of corpus size;
- embedding distance does not imply research value;
- a semantic gap may be meaningless or infeasible;
- low-dimensional visualization holes are often artifacts;
- the model may generate plausible but unsupported novelty claims.

Therefore, implement:

```text
typed semantic gap discovery
```

rather than pure embedding-hole discovery.

---

## 6. Core Idea: Typed Semantic Atoms

Instead of embedding whole notes as single vectors, extract structured atoms from notes.

Each note should be decomposed into typed research atoms:

```text
scenario
problem
method
model
metric
assumption
limitation
baseline
evidence
parameter
standard_constraint
open_question
```

Example:

```json
{
  "item_id": "...",
  "topic": "remote_id",
  "atom_type": "limitation",
  "text": "does not model risk-adaptive broadcast period control",
  "evidence_label": "paper-supported",
  "source_note": "notes/items/....md",
  "confidence": "medium",
  "created_at": "..."
}
```

---

## 7. Phase 1: Research Atom Extraction

Implement this first. Do not generate research ideas yet.

### 7.1 Add script

```bash
python scripts/extract_research_atoms.py --topic all
python scripts/extract_research_atoms.py --topic remote_id
python scripts/extract_research_atoms.py --note notes/items/<id>.md
```

### 7.2 Output

Write:

```text
data/research_atoms.jsonl
```

Each record should include:

```text
atom_id
item_id
topic
atom_type
text
evidence_label
source_note
confidence
created_at
```

### 7.3 Evidence labels

Preserve evidence boundary:

```text
paper-supported
inferred
proposal
unsupported
needs-review
```

If uncertain, use:

```text
needs-review
```

Do not convert uncertain text into factual atoms.

### 7.4 Atom extraction should be conservative

Only extract atoms that are present in the note.

Do not invent missing methods, baselines, metrics, or constraints.

Do not generate new research ideas in this phase.

---

## 8. Phase 2: Typed Semantic Index

After atoms are extracted, build typed semantic indexes.

### 8.1 Embedding unit

Embed atoms, not whole notes.

Separate by type:

```text
embedding(problem)
embedding(method)
embedding(metric)
embedding(limitation)
embedding(standard_constraint)
embedding(open_question)
```

### 8.2 Output

Suggested local outputs:

```text
data/semantic_index/atoms_embeddings.jsonl
data/semantic_index/index_metadata.json
```

If API-based embeddings are used, keep cost small and cache all embeddings.

Do not recompute unchanged atoms.

### 8.3 No requirement to use one provider

The first version can be provider-agnostic.

Acceptable implementation choices:

- local sentence-transformer embeddings;
- OpenAI embeddings;
- Kimi / Moonshot embeddings if available;
- simple TF-IDF fallback for dry-run.

The first version should support dry-run without paid API.

---

## 9. Phase 3: Gap Candidate Discovery

A gap candidate should not be defined as "empty space".

It should be defined as:

```text
anchor sources + typed missing relation + potential research question
```

### 9.1 Gap types

Implement several interpretable gap types.

#### Type A: Combination Gap

Two areas are separately covered but rarely connected.

Example:

```text
Remote ID broadcast congestion
+
risk-driven adaptive update
=
risk-aware Remote ID broadcast scheduling
```

#### Type B: Transfer Gap

A method is used in a neighboring domain but missing in the target low-altitude topic.

Example:

```text
V2X congestion control
-> low-altitude AAV broadcast resource control
```

#### Type C: Metric Gap

A topic is studied using common metrics but missing a key metric.

Example:

```text
Remote ID papers use PDR/range
but rarely link density-induced packet loss to safety boundary degradation
```

#### Type D: Standard-Constraint Gap

Technical papers ignore operational standards, policies, or deployment constraints.

Example:

```text
wireless broadcast studies do not align with Remote ID / U-space constraints
```

#### Type E: Limitation-to-Method Gap

A limitation in one paper may be addressed by a method from another cluster.

Example:

```text
limitation: no adaptive period control
method: risk-driven update scheduling
```

### 9.2 Output

Write:

```text
outputs/gap_candidates/<topic>.md
```

and optionally:

```text
data/gap_candidates.jsonl
```

Each candidate should contain:

```markdown
# Gap Candidate

## Candidate Question

## Gap Type

## Anchor Sources

## Missing Relation

## Why It May Matter

## Possible Minimal Model

## Required Evidence

## Possible Baselines

## Feasibility

## Risk of Triviality

## Risk of Already Existing Work

## Recommended Next Search Queries

## Status
```

Status values:

```text
idea
needs_search
supported_by_more_sources
rejected
promoted_to_topic_synthesis
```

---

## 10. Phase 4: Search-Back Verification

A gap candidate is not a research contribution.

Every candidate must trigger search-back verification.

For each gap candidate, generate search queries such as:

```text
"Remote ID" "adaptive broadcast" UAV
"drone remote identification" "congestion control"
"Remote ID" "broadcast frequency" "interference"
"UAV" "Remote ID" "density" "packet delivery"
```

Then insert these as either:

- related search tasks;
- new collection queries;
- candidate items if specific papers are found.

Do not declare novelty until search-back has been performed.

---

## 11. Phase 5: Streamlit Integration

Add a new GUI section only after the scripts work.

Suggested tab:

```text
Ideas
```

or merge into:

```text
Topics -> Semantic Gap Discovery
```

It should show:

- gap candidates;
- anchor papers;
- missing relation;
- suggested search-back queries;
- status;
- buttons:
  - `Run atom extraction`;
  - `Find gap candidates`;
  - `Mark rejected`;
  - `Mark needs search`;
  - `Promote to topic synthesis`.

Do not make this a route-card generator.

---

## 12. Guardrails

The semantic-gap module must follow these rules:

1. Do not generate final novelty claims.
2. Do not generate route cards automatically.
3. Do not claim a gap unless anchor sources and missing relation are explicit.
4. Do not treat embedding distance as proof.
5. Do not use unsupported speculative combinations as research conclusions.
6. Every gap candidate must show:
   - anchor sources;
   - typed missing relation;
   - search-back queries;
   - risk of already existing work.
7. Human review is required before any candidate enters `possible_directions.md`.

---

## 13. Recommended Development Order

Do not implement everything at once.

### PR 1: Close current MVP

- PDF Inbox;
- `register_pdf_item()`;
- always-show PDF actions for paper items;
- `--force` / `--upgrade`;
- related-item extraction;
- deprecate generic follow-up actions;
- simplify Topic Workspace into generated Topic Preview.

### PR 2: Research atoms

- `scripts/extract_research_atoms.py`;
- `data/research_atoms.jsonl`;
- conservative atom schema;
- no embeddings yet;
- no gap generation yet.

### PR 3: Typed semantic index

- atom embeddings or TF-IDF fallback;
- caching;
- per-atom-type index.

### PR 4: Gap candidates

- interpretable gap rules;
- anchor-source output;
- `outputs/gap_candidates/<topic>.md`;
- no novelty claims.

### PR 5: GUI integration

- Ideas / Semantic Gap Discovery tab;
- review statuses;
- search-back workflow.

---

## 14. Definition of Done for Current MVP Closeout

The current MVP closeout is successful if:

1. A PDF dropped into `literature/inbox/papers/` appears in GUI as an unregistered local PDF.
2. The user can register the PDF without reading it.
3. The user can generate `text-draft` or `Kimi` note from GUI.
4. The user can upgrade an existing `text-draft` note to a `Kimi` note.
5. Concrete recommended sources in notes become candidate items.
6. Generic follow-up actions no longer clutter the workflow.
7. Topic Workspace is no longer a manually maintained task/discussion document.
8. The user mostly works through:
   - keep;
   - reject;
   - download;
   - register;
   - read;
   - synthesize.

---

## 15. Definition of Done for Semantic Gap Phase 1

Phase 1 is successful if:

1. Existing notes can be converted into `data/research_atoms.jsonl`.
2. Each atom has:
   - item_id;
   - topic;
   - atom_type;
   - text;
   - evidence_label;
   - source_note;
   - confidence.
3. Extraction is conservative.
4. No research idea is generated yet.
5. Output is reviewable and easy to inspect.

---

## 16. Guiding Principle

The research hub should not automatically invent research directions.

It should help the user see:

```text
what has been read
what has been covered
what is missing
which missing relation is potentially meaningful
what should be searched next
```

Core principle:

```text
Items -> Notes -> Research Atoms -> Gap Candidates -> Human Judgment
```

Do not skip intermediate evidence layers.
