# Refactor Request: Simplify the Low-Altitude Research Hub into a Usable Research-Intelligence Tool

## 0. Current Diagnosis

The current repository is becoming too complex and difficult to use. It is drifting from a lightweight research-assistance workflow into a full custom research platform.

The intended goal is not to build a complete academic knowledge-management product from scratch. The intended goal is:

> Automatically collect relevant papers, news, standards, policies, and industrial updates in low-altitude communication / UAV systems; let LLMs read and summarize them; provide a convenient review interface; and help the user gradually identify promising research directions.

At the moment, the repository contains or plans too many functions at once:

- literature discovery;
- PDF management;
- metadata completion;
- PDF reading;
- paper-note generation;
- figure/table note generation;
- claims ledger;
- evidence map;
- topic brief;
- route card;
- feasibility ranking;
- Notion integration;
- Zotero integration;
- GitHub Actions;
- LLM API adapters;
- research decision workflow.

Each component is individually reasonable, but the total system is becoming too heavy. The development and maintenance cost is approaching or exceeding the cost of manually searching papers.

The next refactor should **reduce scope**, not add more features.

---

## 1. Core Product Goal

The repository should be reframed as:

> A lightweight research-intelligence assistant that periodically collects low-altitude research signals and generates reviewable weekly summaries. Final research-direction decisions remain human-led.

The primary user value should be:

- reduce weekly paper/news search time;
- avoid missing important new sources;
- summarize relevant material automatically;
- keep a clean trail of what was collected, read, and considered;
- help the user decide what to read next.

The repository should **not** try to automatically produce final research directions, novelty claims, or implementation repository proposals in early stages.

---

## 2. Main Problem with the Current Design

The current design is too developer-centric.

A normal usage flow requires the user to understand:

- `configs/pipeline.json`;
- topic key vs. topic slug;
- `paper_candidates.csv`;
- `review_queue.csv`;
- `acquisition_queue.csv`;
- `candidate_id`;
- PDF filename matching;
- GitHub Actions PRs;
- local Python scripts;
- OpenAI API key;
- different Markdown output folders;
- when to trust or ignore generated route cards.

This is too much cognitive overhead for a research workflow.

The system should optimize for the following interaction:

```text
Weekly summary appears
-> user reviews top items
-> user marks keep / reject / download / read
-> system reads selected items
-> system updates summaries
-> system produces topic-level observations
```

The user should not have to inspect many CSV files or understand internal pipeline mechanics during normal use.

---

## 3. Recommended Architecture After Refactor

Please refactor the repository into three simpler layers.

### Layer 1: Collector

Purpose:

- collect papers, news, standards, policies, white papers, and industrial updates.

Sources may include:

- OpenAlex;
- Crossref;
- arXiv;
- Semantic Scholar;
- selected RSS feeds;
- standards and regulatory websites;
- industry white-paper pages;
- manually added URLs or PDFs.

Output should be a **single unified item table**, preferably:

```text
data/items.jsonl
```

or a small SQLite database.

Each item should have only essential fields:

```text
id
title
url
source
source_type           # paper / news / standard / policy / whitepaper / report
topic
date
abstract_or_snippet
pdf_url
status                # new / kept / rejected / downloaded / read / summarized
score
tags
created_at
updated_at
```

Avoid overloading the first version with too many fields such as `venue_tier`, `source_trust`, `notion_status`, `human_decision`, etc. These can be added later if genuinely needed.

### Layer 2: Reader

Purpose:

- read selected papers, PDFs, webpages, standards, and reports;
- generate concise structured summaries.

Reader output should initially be simple:

```text
notes/items/{id}.md
```

Each note should contain:

```markdown
# Item Summary

## Metadata

## Why It Was Collected

## Core Content

## Method / System / Policy Details

## Key Evidence

## Limitations

## Relevance to Low-Altitude Research

## Useful Parameters / Models / Baselines

## Follow-up Actions

## Reliability Notes
```

Do not generate evidence maps or route cards for every single item.

### Layer 3: Synthesizer

Purpose:

- periodically synthesize already-read notes by topic.

Only run this when a topic has accumulated enough read items, e.g., 10+ relevant notes.

Outputs:

```text
topics/{topic}/weekly_or_monthly_synthesis.md
topics/{topic}/open_questions.md
topics/{topic}/possible_directions.md
```

The synthesizer should not create final route cards by default.

Instead, it should produce:

- emerging clusters;
- repeated assumptions;
- common models;
- missing evidence;
- possible research questions;
- recommended next readings;
- risk notes.

Route cards should be manually triggered only when the user explicitly asks.

---

## 4. What to Remove or Defer

Please do not continue expanding the system in its current direction.

### Defer or disable for now

- automatic route-card generation after every PDF read;
- automatic feasibility ranking;
- automatic repository proposal;
- complex evidence-map generation from small numbers of papers;
- deep Notion synchronization;
- deep Zotero synchronization;
- multi-provider LLM abstraction unless necessary;
- excessive CSV fields;
- multiple separate note types for every paper.

### Keep only if lightweight

- weekly digest;
- local PDF reading;
- basic metadata completion;
- basic status tracking;
- concise Markdown summaries;
- topic-level periodic synthesis.

---

## 5. GUI / Review Interface Should Be Prioritized

The current system relies too much on CSV files and GitHub PR diffs.

A convenient review surface is essential. It can be simple.

Acceptable options:

### Option A: Streamlit local app

Recommended for v1.

Features:

- show new collected items;
- filter by topic/source/type;
- buttons: keep / reject / download / read / summarize;
- show generated summaries;
- show weekly digest;
- edit status fields.

### Option B: Notion as review surface

Acceptable, but only as a mirror of repo state.

Notion should not become the canonical database.

Views:

- Paper Inbox;
- Download Queue;
- Reading Queue;
- Weekly Digest;
- Topic Watchlist.

### Option C: Obsidian vault

Good for reading and long-term notes.

The repo can generate Markdown files that are easy to open in Obsidian.

---

## 6. Recommended MVP

Please implement a smaller MVP with only the following capabilities.

### MVP 1: Weekly research-intelligence digest

Command:

```bash
python scripts/collect_weekly.py --topic all
```

Output:

```text
outputs/weekly/YYYY-MM-DD.md
```

The weekly digest should include:

```markdown
# Weekly Low-Altitude Research Intelligence Digest

## New Papers

## New Standards / Policies / Reports

## New Industry / Deployment Signals

## Top Items to Review

## PDFs Worth Downloading

## Items Recommended for LLM Reading

## Topic-Level Observations

## Suggested Next Actions
```

This should be the main output the user sees every week.

### MVP 2: Drop-in PDF reading

Command:

```bash
python scripts/read_item.py path/to/paper.pdf --topic remote_id
```

The script should:

1. detect DOI/title if possible;
2. complete metadata from Crossref / Semantic Scholar / OpenAlex;
3. assign or ask for topic;
4. generate `notes/items/{id}.md`;
5. update `data/items.jsonl`;
6. not require filename to contain `candidate_id`.

The current dependence on `candidate_id` in PDF filenames is too fragile.

### MVP 3: Topic synthesis only on demand

Command:

```bash
python scripts/synthesize_topic.py --topic remote_id
```

Output:

```text
topics/remote_id/synthesis.md
topics/remote_id/open_questions.md
topics/remote_id/possible_directions.md
```

This should summarize already-read notes, not raw metadata.

---

## 7. Human Review Model

The human review burden should be minimal.

The user should only need to make these decisions:

```text
keep
reject
download
read
summarize
promote_to_topic_synthesis
```

Avoid asking the user to manually maintain many technical fields.

Generated content should be clearly labeled:

```text
machine-generated
human-reviewed
needs-review
```

Final research judgments should not be automated.

---

## 8. Data Model Recommendation

Use one primary item store.

Preferred:

```text
data/items.jsonl
```

or:

```text
data/research_items.sqlite
```

Avoid many separate CSVs unless strictly necessary.

Each item should track its lifecycle:

```text
new -> kept -> downloaded -> read -> summarized -> used_in_synthesis
          -> rejected
```

This is easier to understand than separate candidate, review, acquisition, reading, and route-card states.

---

## 9. Revised Role of Tools

### GitHub

Use for:

- scripts;
- versioned Markdown outputs;
- weekly digests;
- configuration;
- lightweight automation.

Do not use GitHub CSVs as the main daily UI.

### Zotero

Use for:

- human-facing paper/PDF management;
- citation metadata;
- manual restricted-PDF downloads.

Zotero integration can be optional and later.

### Notion / Streamlit / Obsidian

Use as the review surface.

The user needs a convenient GUI earlier, not after the backend becomes complex.

### LLM APIs

Use for:

- reading selected PDFs;
- summarizing webpages/reports;
- generating topic synthesis from reviewed notes.

Do not use LLMs to automatically declare novelty or create final route decisions.

---

## 10. Key Refactor Tasks

Please create a refactor PR that does the following:

1. Rewrite the README to state the reduced goal:
   - automatic collection;
   - weekly digest;
   - selected item reading;
   - topic synthesis;
   - no automatic final research claims.

2. Add or refactor to a unified item model:
   - `data/items.jsonl` or SQLite;
   - minimal lifecycle states.

3. Replace or wrap current discovery scripts with:
   - `scripts/collect_weekly.py`;
   - outputs one weekly digest.

4. Replace current fragile PDF reading workflow with:
   - `scripts/read_item.py`;
   - accepts arbitrary PDF path;
   - auto-completes metadata when possible;
   - generates one concise item note.

5. Make topic synthesis separate and manually triggered:
   - `scripts/synthesize_topic.py --topic <topic>`;
   - no automatic route cards.

6. Move existing route-card/evidence-map machinery into an `archive/` or `experimental/` area unless still needed.

7. Add a simple local review interface if feasible:
   - preferably Streamlit;
   - otherwise generate a single `outputs/review_dashboard.md`.

8. Keep GitHub Actions focused only on scheduled collection and weekly digest generation.

9. Do not add more external integrations until the core workflow is usable.

---

## 11. Definition of Done

The refactored repository is successful if the user can do the following without understanding internal pipeline details:

1. Run one command or GitHub Action each week.
2. Open one weekly digest.
3. See new papers/news/standards grouped by topic.
4. Mark a small number of items as worth reading.
5. Drop a PDF into the system and get a useful summary.
6. Run topic synthesis only after enough notes accumulate.

If the user still has to inspect many CSV files, manually fix candidate IDs, or understand multiple pipelines, the refactor has not solved the problem.

---

## 12. Guiding Principle

Do not build a complete research platform.

Build a low-maintenance research-intelligence assistant that saves time every week.

Prefer:

```text
simple, reviewable, useful
```

over:

```text
complete, automated, over-engineered
```
