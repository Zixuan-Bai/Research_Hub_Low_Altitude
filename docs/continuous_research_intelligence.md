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

If downloaded PDFs have arbitrary browser filenames, normalize them first:

```powershell
python scripts/run_reading_pipeline.py --topic remote_id --rename-only --dry-run
python scripts/run_reading_pipeline.py --topic remote_id --rename-only
```

The script first checks whether the filename already contains a `candidate_id`.
If not, it tries DOI, PDF metadata title, visible PDF text, and filename/title
similarity against `paper_candidates.csv`. Only high-confidence matches are
renamed to the normalized pattern below; low-confidence matches go to the
review queue.

```text
【optional-human-note】-2026-IEEE_TWC-short_title-candidate_id.pdf
2026-IEEE_TWC-short_title-candidate_id.pdf
```

The `【optional-human-note】` prefix is for your own visual hints. You can add,
remove, or change it at any time; the pipeline ignores it during matching and
preserves it when renaming.

If a PDF is not in `paper_candidates.csv`, the reading pipeline can look up its
metadata online from the inferred DOI/title and add a conservative candidate
row before renaming:

```powershell
python scripts/run_reading_pipeline.py --topic remote_id --rename-only
```

Use `--no-online-lookup` to disable this behavior.

This pipeline uses Kimi/Moonshot file reading by default, with OpenAI kept as an
optional provider. It writes structured notes, figure/table notes, claims
ledgers, evidence maps, topic briefs, and watch-only route-card drafts.

Required environment:

```powershell
$env:MOONSHOT_API_KEY="..."
```

Recommended local setup:

```powershell
Copy-Item .env.example .env
notepad .env
```

Put the real key in `.env`, not in `configs/*.json`. The repository ignores
`.env`, `configs/*.local.json`, and `configs/secrets*.json`.

Optional environment:

```powershell
$env:KIMI_READING_MODEL="kimi-k2.6"
$env:MOONSHOT_BASE_URL="https://api.moonshot.cn/v1"
```

Without `MOONSHOT_API_KEY` or `KIMI_API_KEY`, the reading pipeline only queues a
review item and does not mark a PDF as read.

Provider override:

```powershell
python scripts/run_reading_pipeline.py --topic remote_id --provider kimi
python scripts/run_reading_pipeline.py --topic remote_id --provider openai
```

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
