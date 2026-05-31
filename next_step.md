# Next Refactor Task

The current refactor is directionally correct. Do not add major new architecture. Please improve usability and reliability in a small PR.

## Required changes

1. Update GitHub Actions to install `requirements.txt` before running collection.

2. Improve Streamlit review app:
   - add a "Weekly Digest" tab that renders the latest `outputs/weekly/*.md`;
   - add an "Item Note" preview inside each item card if `note_path` exists;
   - add a "Topic Overview" tab showing counts by topic:
     - new
     - kept
     - downloaded
     - summarized
     - used_in_synthesis;
   - add a button to run `scripts/synthesize_topic.py --topic <topic>` from the Topic Overview tab.

3. Add `metadata_status` to items:
   - `auto` for normal automatic metadata;
   - `needs_review` for low-confidence PDF metadata matches;
   - `verified` after user edits metadata in the GUI.
   Display this status in the GUI.

4. Add a minimal context-source collector:
   - create `configs/context_sources.json`;
   - support RSS or manually listed URLs;
   - write results into `data/items.jsonl`;
   - source_type should support `news`, `standard`, `policy`, `whitepaper`, `report`.
   Keep it simple; no complex crawler.

5. Add PDF reading modes:
   - `metadata-only`: complete metadata only;
   - `text-draft`: extract text with pypdf and write a draft note without calling Kimi;
   - `kimi`: current API-based mode.
   Keep `kimi` as the default only when API key is present.

## Do not do

- Do not reintroduce automatic route cards.
- Do not add complex Notion/Zotero sync.
- Do not add a large multi-agent architecture.
- Do not change the core data store away from `data/items.jsonl` in this PR.