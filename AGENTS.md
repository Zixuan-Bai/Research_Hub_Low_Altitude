# AGENTS.md

## Project Type

This is a Level 0 research-intelligence repository, not an implementation repository and not a full custom knowledge-management platform.

The goal is to collect low-altitude research signals, review them in a local dashboard, read selected PDFs or URLs, maintain Chinese topic workspaces, and support human-led topic synthesis.

Do not automatically produce final research directions, novelty claims, route cards, feasibility rankings, or implementation repository proposals.

## Broad Research Target

The broad target is low-altitude communication and autonomous aerial systems.

Initial watch topics include:

1. UAV broadcast capacity and Remote ID-like systems;
2. DTMB-based or terrestrial-broadcast-based UAV management;
3. autonomous UAV formation safety and stability boundaries;
4. dynamic directional networking for low-altitude aerial networks.

These are watch topics only. Do not treat any direction as approved or novel until evidence and human review support it.

## Main Workflow

Use the simplified mainline:

1. Collect intelligence with `scripts/collect_weekly.py`.
2. Review `outputs/review_dashboard.md` or the Streamlit review app.
3. Read selected local PDFs with `scripts/read_item.py`.
4. Store Chinese notes under `notes/items/`.
5. Run `scripts/synthesize_topic.py` only when enough notes exist for a topic.

The canonical item store is:

```text
data/items.jsonl
```

Do not reintroduce the old multi-CSV state machine unless the user explicitly asks.

## User-Facing Language

All user-facing artifacts should be written in Chinese by default:

- review dashboards;
- topic workspaces;
- review dashboards;
- item notes;
- topic synthesis;
- open questions;
- possible directions;
- practical workflow docs.

Keep these machine-readable labels in English when useful:

- `paper-supported`
- `inferred`
- `proposal`
- `unsupported`
- `metadata only`
- `abstract only`
- `full-text parsed`
- `human reviewed`
- `needs-review`

## Non-negotiable Literature Rules

1. Do not fabricate references.
2. Do not invent DOI, venue, author, year, dataset, standard number, or numerical result.
3. If a paper has not been read, mark it as `metadata only` or keep it as a collected item.
4. If only the abstract has been read, mark it as `abstract only`.
5. If the full PDF has been parsed, mark it as `full-text parsed`.
6. Distinguish between:
   - `paper-supported`: what a source explicitly states;
   - `inferred`: what is inferred from multiple sources;
   - `proposal`: the user's or Codex's proposed extension;
   - `unsupported`: what is not supported by the available source.
7. Do not claim a research gap unless at least three relevant sources have been compared.
8. Do not write final paper claims in this repository unless they are explicitly marked as preliminary.
9. Do not recommend creating a Level 1 repository from this repo's automated outputs.

## Source Quality and Practicality Rules

Prefer high-quality sources when forming observations:

- top journals and conferences;
- IEEE Transactions / ACM Transactions;
- Nature / Science family journals;
- recognized standards, white papers, and technical reports;
- deployed or clearly planned industrial systems;
- policy, regulatory, or government documents when they define real constraints.

Treat low-tier or weakly reviewed papers as low-confidence evidence unless independently supported.

Do not let a single paper's framing dominate synthesis.

Do not infer real-world deployability from academic popularity.

Mark purely academic concepts with unclear deployment path as `deployment uncertain`.

Be especially cautious with areas that may be mostly academic speculation, such as semantic communication or RIS, unless there is concrete system evidence.

## Output Rules

Every generated user-facing artifact must mark unsupported or speculative parts.

Topic synthesis should focus on:

1. evidence base;
2. known methods;
3. common assumptions;
4. limitations of existing work;
5. source quality assessment;
6. practical context that still needs checking;
7. open questions;
8. possible directions as questions, not final route decisions;
9. recommended next readings.

Do not generate route cards by default.

If a topic has too few read notes, write `needs-review` and explain what is missing instead of forcing synthesis.

## Repository Boundary

This repository should contain:

- `data/items.jsonl`;
- lightweight manual item inputs;
- Chinese review dashboards;
- Chinese topic workspaces;
- Chinese item notes;
- topic synthesis outputs;
- workflow documentation;
- lightweight scripts and config.

This repository should not contain:

- large raw PDFs;
- copyrighted full-text dumps;
- datasets;
- checkpoints;
- long experiment logs;
- Level 1 implementation code;
- automatic final research conclusions.

## Codex Behavior

Before editing files, inspect the relevant current workflow and `codex_refactor_request_low_altitude_research_hub.md`.

Prefer small, verifiable changes, but do not preserve obsolete compatibility layers if they make the new mainline harder to use.

When uncertain, follow `codex_refactor_request_low_altitude_research_hub.md` or ask the user.

Do not overstate novelty. Do not recommend building an implementation repository unless the user explicitly asks and the evidence has been human reviewed.
