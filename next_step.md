# Follow-up Fixes for Research Hub

The recent refactor is directionally correct. Please do not add major architecture or route-card automation. Fix the remaining usability and safety issues.

## Required fixes

1. Fix `text-draft` copyright/storage risk.
   - Do not write long extracted PDF text into `notes/items/*.md`.
   - Store extracted raw text only in an ignored local cache, e.g. `.local/pdf_text_cache/`, or omit it entirely.
   - The committed note should contain only metadata, short page hints, and a clear `needs-review` message.

2. Clarify reading status semantics.
   - For `metadata-only`: `reading_status = metadata_only`.
   - For `text-draft`: `reading_status = text_extracted`, `summary_status = text-draft`, `visual_status = not_parsed`.
   - For `kimi`: `reading_status = model_parsed_pdf`, `summary_status = summarized`.

3. Update README.
   - Explain the actual process lifecycle:
     `unread -> read(text-draft) -> summarized(Kimi/LLM) -> used_in_synthesis`.
   - Explain `metadata-only`, `text-draft`, and `kimi` modes.

4. Improve Streamlit GUI.
   - Add a filter for `metadata_status`: all / auto / needs_review / verified.
   - Add a dashboard section for items whose metadata needs review.
   - In Topic Overview, show:
     - read_or_summarized count;
     - min_notes threshold;
     - ready_for_synthesis;
     - whether synthesis outputs already exist.

5. Expand `configs/context_sources.json`.
   - Add initial policy/standard/industry sources for Remote ID, UTM/U-space, UAV regulation, low-altitude economy, and aerial communication.
   - Keep it simple: RSS/manual URL only. No crawler.

## Do not do

- Do not reintroduce automatic route cards.
- Do not add Notion/Zotero sync yet.
- Do not add complex multi-agent architecture.
- Do not change the unified `data/items.jsonl` store.