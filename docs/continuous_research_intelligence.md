# Continuous Research Intelligence Workflow

This repository is the canonical Level 0 source of truth. External tools are
review surfaces and convenience layers; they should not overwrite human
decisions in the repo.

## Two Regular Pipelines

### Discovery

Run weekly or on demand:

```powershell
python scripts/run_discovery_pipeline.py --topic all --write-digest
```

This pipeline searches metadata sources, updates candidate and acquisition
queues, classifies obvious review needs, and writes a weekly digest. It does
not read PDFs or generate research claims.

Supported metadata providers:

- OpenAlex
- Crossref
- arXiv
- Semantic Scholar

Use incremental refresh when needed:

```powershell
python scripts/run_discovery_pipeline.py --topic remote_id --from-updated-date 2026-05-01 --write-digest
```

### Reading

Run after PDFs are downloaded into `literature/inbox/papers/` or
`literature/pdfs/open_access/`:

```powershell
python scripts/run_reading_pipeline.py --topic remote_id
```

This pipeline uses OpenAI multimodal PDF input by default. It should read both
text and visual page information, then write structured notes, figure/table
notes, claims ledgers, evidence maps, topic briefs, and watch-only route-card
drafts.

Required environment:

```powershell
$env:OPENAI_API_KEY="..."
```

Optional environment:

```powershell
$env:OPENAI_READING_MODEL="gpt-5.5"
```

Without `OPENAI_API_KEY`, the reading pipeline only queues a review item and
does not mark a PDF as read.

## Recommended External Tools

### Zotero

Use Zotero Desktop plus the browser connector as the human-facing PDF and
library manager.

Recommended role:

- save candidate papers from publisher pages;
- manually download restricted PDFs when legal access is available;
- preserve citation metadata;
- optionally export or sync metadata later.

Do not upload restricted PDFs to Git by default.

### Notion

Use Notion as the main visual review surface. The repo remains canonical.

Recommended databases or views:

- Paper Inbox: new candidates, topic, score, source, PDF status, recommended action.
- Download Queue: high-value missing PDFs with `downloaded`, `ignore`, and `unavailable` statuses.
- Reading Queue: local PDF status, note status, visual-evidence review status.
- Evidence Map Board: topic claims, supporting papers, practical sources, strength.
- Route Review Board: route-card drafts with `watch`, `keep`, `reject`, and `needs more evidence`.

For v1, scripts can run without Notion credentials. Notion sync should be added
as a later adapter that mirrors repo state to the visual interface.

### GitHub Actions

The scheduled workflow runs discovery weekly and opens a PR if metadata,
review queues, or weekly digests change.

## Human Review Is Small and Explicit

You should not review every CSV row. Focus on:

- high-value papers with missing PDFs;
- high-value papers whose venue or metadata is uncertain;
- visual evidence that the model flagged as important or ambiguous;
- route cards that might move from `watch` to `keep`;
- practical context gaps before accepting any route.

## Level 0 Boundary

Allowed in Git:

- metadata;
- structured notes;
- figure/table summaries;
- claims ledgers;
- evidence maps;
- topic briefs;
- route-card drafts;
- review queues;
- weekly digests.

Not allowed in Git by default:

- restricted PDFs;
- full-text dumps;
- datasets, checkpoints, or long experiment logs;
- Level 1 implementation code;
- final novelty claims;
- automatic repository-creation decisions.

`full-text parsed` means a model processed the PDF. It does not mean human
reviewed.
