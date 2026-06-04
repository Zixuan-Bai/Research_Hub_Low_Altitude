# Follow-up Refactor Request: Topic Workspace and Local PDF Workflow

## 0. Context

The repository has improved significantly after recent refactors. The current direction is broadly correct:

- unified item store: `data/items.jsonl`;
- Streamlit review app;
- separate paper database and social/context database;
- local PDF reading modes;
- topic overview and topic synthesis;
- metadata status and document-access status;
- no automatic route cards.

However, two usability problems remain significant:

1. **Topic Workspace and follow-up actions are not useful enough.**
   They create manual tasks that do not feed back into the item database or item notes.

2. **Local PDFs dropped into `literature/inbox/papers/` are not visible as reviewable items until the user explicitly runs a reading pipeline.**
   Also, paper items with existing notes cannot be conveniently upgraded or re-read from the item card.

This refactor should focus only on these two problems. Do not expand the system into a generic task manager or a full research platform.

---

## 1. Product-Level Goal

The desired workflow should be:

```text
Weekly collection produces new items
-> user reviews items in GUI
-> user downloads or drops PDFs into local inbox
-> PDFs automatically appear as reviewable local PDF items
-> user can register / read / upgrade notes directly from GUI
-> note recommendations that name concrete papers/standards/reports become new candidate items
-> topic-level views show coverage and synthesis readiness
```

The user should not need to manually maintain:

- generic follow-up actions;
- per-paper task lists;
- `research_workspace.md` discussions;
- done/skipped status for vague tasks;
- manual notes about whether a suggested citation was later searched.

---

## 2. Problem A: Topic Workspace and Follow-up Actions

### 2.1 Current Problem

The current system extracts `follow_up_actions` from item notes and exposes them in the GUI as open/done/skipped tasks.

This is not useful enough because:

- many generated follow-up actions are generic, such as "continue analysis", "verify assumptions", "compare methods", or "supplement background";
- if the user actually performs a follow-up action, the result does not automatically update the original note;
- the user cannot realistically edit every paper note after doing follow-up work;
- the actions accumulate in `research_workspace.md`, which becomes another file to maintain;
- the model does not reliably gain useful new information from these open tasks;
- for research usage, the only truly valuable follow-up is often: "read this cited paper / standard / report next".

Therefore, generic follow-up actions should be deprecated or hidden from the main workflow.

---

## 3. Desired Replacement: Related Item Extraction

### 3.1 Principle

If a note recommends a specific source, the system should convert it into a candidate item.

Example note output:

```text
Recommended next source: DRIP Architecture
Recommended next source: ASTM F3411 Remote ID
Recommended next source: LoRa Remote ID multi-user interference paper
Recommended next source: 3GPP UAV aerial UE report
```

These should not become manual tasks.

They should become items in `data/items.jsonl`, with status:

```text
review_status = new
process_status = unread
source = related_item_extraction
```

The user can then review them like any other collected item:

```text
new -> kept -> downloaded -> noted
       -> rejected
```

### 3.2 Add `scripts/extract_related_items.py`

Create a new script:

```bash
python scripts/extract_related_items.py --from-notes --topic remote_id
python scripts/extract_related_items.py --from-notes --topic all
python scripts/extract_related_items.py --note notes/items/<id>.md
```

It should scan item notes and extract concrete source-like objects only.

Allowed extraction targets:

- paper titles;
- DOI;
- arXiv IDs;
- explicit URLs;
- standard names or standard numbers;
- policy/report/whitepaper names;
- named datasets or technical documents, if clearly source-like.

Do not extract generic research advice.

Ignore lines such as:

```text
continue analysis
verify assumptions
compare methods
supplement background
study limitations
check applicability
perform further investigation
```

unless the line names a concrete source.

### 3.3 Metadata Completion

For extracted paper-like items:

- use Crossref / OpenAlex / Semantic Scholar where available;
- deduplicate using DOI, URL, normalized title, and existing item IDs.

For standard/policy/report/whitepaper-like items:

- if a URL is present, register it directly;
- if no URL is present, create a low-confidence item with `metadata.extraction_status = needs_review`;
- do not invent URLs, DOIs, standard numbers, or publication facts.

### 3.4 Item Format

Extracted related items should be inserted into `data/items.jsonl` with fields similar to:

```json
{
  "title": "Extracted source title",
  "url": "",
  "source": "related_item_extraction",
  "source_type": "paper",
  "topic": "remote_id",
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

If the source was resolved by DOI or a high-confidence metadata match, `metadata_status` may be `auto`, but the item should still remain `review_status = new`.

---

## 4. Change the Note Template / Prompt

### 4.1 Replace Generic Follow-up Actions

Replace the current note section:

```markdown
## 后续建议
```

or:

```markdown
## 后续动作
```

with a more structured section:

```markdown
## 推荐入库条目

Only list concrete sources that should become candidate items in the research hub.

Each item should use this structure:

- type: paper / standard / policy / report / whitepaper / news / dataset / unknown
- title_or_name:
- doi_or_url_if_available:
- reason:
- relation_to_this_item:
- confidence: high / medium / low
```

### 4.2 Explicitly Forbid Generic Tasks

The note-generation prompt should say:

```text
Do not generate generic follow-up tasks such as:
- continue analysis;
- verify assumptions;
- compare methods;
- supplement background;
- further investigate;
- check applicability.

If no concrete source can be recommended, write:
- needs-review: no concrete source identified.
```

### 4.3 Keep Only Critical Missing Information

If necessary, keep a short section:

```markdown
## 不足信息

Only list missing information that directly affects interpretation of this item.
Do not turn missing information into a manual task list.
```

This section should not be parsed into task lists.

---

## 5. Refactor Topic Workspace

### 5.1 Current Problem

`Topic Workspace` currently mixes:

- evidence base;
- social/context signals;
- current understanding;
- uncertain information;
- possible paper ideas;
- recommended next readings;
- discussion records;
- open follow-up tasks.

This makes it feel like another file the user must maintain.

The user does not want to manually edit `research_workspace.md` or mark many tasks as done/skipped.

### 5.2 Desired Change

Downgrade Topic Workspace from a manually maintained workspace to a generated preview.

Recommended new name:

```text
Topic Brief Preview
```

or keep the file name internally but change the user-facing GUI label.

### 5.3 What It Should Contain

The generated topic preview should contain only:

```markdown
# Topic Brief Preview: <topic>

## Coverage Summary

- total items:
- paper items:
- social/context items:
- noted items:
- related items extracted from notes:
- synthesis readiness:

## Evidence Base

List already-noted items only.

## Social / Context Signals

List standard, policy, report, whitepaper, industry, and news items.

## Extracted Related Items

List candidate items produced by `extract_related_items.py`.

## Synthesis Readiness

Indicate whether the topic has enough noted items for synthesis.

## Suggested Next System Actions

Only system actions, not research tasks:
- run related-item extraction;
- review newly extracted items;
- download PDFs for kept items;
- run topic synthesis when enough notes exist.
```

### 5.4 What It Should Not Contain

Remove from Topic Workspace:

- generic follow-up task lists;
- open/done/skipped action tracking;
- manually edited discussion records;
- possible paper ideas;
- route-card-like content;
- novelty claims;
- user-maintained research notes;
- "recommended next reading" as plain text.

Recommended reading should appear as extracted related items, not as free text.

### 5.5 GUI Changes

In Streamlit:

- rename the `Topic Workspace` tab to `Topic Preview` or merge it into `Topics`;
- make it generated/read-only by default;
- remove manual free-text editor or move it behind an "advanced/manual notes" expander;
- show a button:
  - `Extract related items from notes`;
- show another button:
  - `Refresh topic preview`.

The main user action should be reviewing extracted items, not editing the workspace.

---

## 6. Problem B: Local PDF Inbox

### 6.1 Current Problem

When the user drops PDFs into:

```text
literature/inbox/papers/
```

they do not automatically appear in the review queue.

A PDF becomes visible in the GUI only after `read_item.py` or `batch_read_pdfs.py` processes it and inserts/updates an item in `data/items.jsonl`.

This is unintuitive.

The desired behavior is:

```text
drop PDF into local inbox
-> GUI shows it in a PDF Inbox
-> user can register it as an item
-> user can optionally read it with text-draft or Kimi
```

Registration and reading should be separate operations.

---

## 7. Add PDF Inbox Workflow

### 7.1 Add a GUI Section

Add a Streamlit section/tab named:

```text
PDF Inbox
```

It should scan:

```text
literature/inbox/papers/
```

and list local PDFs with:

- filename;
- path;
- SHA256 fingerprint;
- inferred title if available;
- inferred topic and confidence if available;
- whether the PDF is already registered in `data/items.jsonl`;
- whether an existing note is already linked;
- whether a possible metadata match was found.

### 7.2 Display Unregistered PDFs

PDFs that are not yet represented in `data/items.jsonl` should be shown as pending local PDFs.

For each unregistered PDF, provide buttons:

```text
Register only
Register + text-draft
Register + Kimi note
```

### 7.3 Register Only

`Register only` should:

- create or update an item in `data/items.jsonl`;
- set `source = local_pdf`;
- set `source_type = paper`;
- set `review_status = new`;
- set `process_status = unread`;
- set `metadata_status = needs_review` unless metadata matching is high confidence;
- set `metadata.pdf_source`;
- set `metadata.pdf_sha256`;
- set `metadata.pdf_inbox_status = registered`;
- do not generate a note.

This makes the PDF visible as a reviewable item before full reading.

### 7.4 Register + text-draft

This should:

- register the PDF if needed;
- generate a text-draft note;
- not commit long extracted full text;
- store raw extracted text only in ignored local cache, e.g. `.local/pdf_text_cache/`.

### 7.5 Register + Kimi note

This should:

- register the PDF if needed;
- generate a Kimi/LLM note;
- set reading metadata accordingly.

---

## 8. Always Show PDF Actions for Paper Items

### 8.1 Current Problem

The current item card only shows the "read local PDF" section when:

```python
source_type == "paper" and not has_existing_note(item)
```

This is too restrictive.

It prevents the user from conveniently upgrading a `text-draft` note to a Kimi note.

### 8.2 Desired Behavior

For every item with:

```text
source_type = paper
```

show a PDF action section.

Cases:

#### Case 1: No Local PDF Bound

Show:

- input field to bind a local PDF path;
- optional list of possible matching PDFs from `literature/inbox/papers/`;
- button: `Bind PDF`.

#### Case 2: Local PDF Bound, No Note

Show buttons:

- `metadata-only`;
- `text-draft`;
- `Kimi note`.

#### Case 3: Existing text-draft Note

Show:

- `Upgrade to Kimi note`;
- `Regenerate text-draft`;
- preserve old note or overwrite only after confirmation.

#### Case 4: Existing Kimi Note

Show:

- `Re-read / overwrite note`;
- require confirmation checkbox.

---

## 9. Add `--force` / `--upgrade` to `read_item.py`

### 9.1 Current Problem

`read_item.py` currently skips if it finds an existing note.

This is safe, but it blocks note upgrading.

### 9.2 Required Change

Add:

```bash
--force
```

or:

```bash
--upgrade
```

Behavior:

- default behavior remains safe: skip existing note;
- `--force`: regenerate note even if one exists;
- `--upgrade`: if existing note is `text-draft` and requested mode is `kimi`, generate a Kimi note;
- write metadata indicating upgrade history.

Suggested metadata:

```json
{
  "reading_mode": "kimi",
  "previous_reading_mode": "text-draft",
  "upgraded_at": "...",
  "note_version": 2
}
```

Do not silently overwrite notes unless the user explicitly requests it.

---

## 10. Add `register_pdf_item()` API

Create or expose a function:

```python
register_pdf_item(
    pdf_path: Path,
    topic: str = "auto",
    providers: list[str] = ...
) -> dict
```

This function should:

- infer or resolve topic;
- lookup metadata if possible;
- create/update the item;
- bind `pdf_source`;
- bind `pdf_sha256`;
- set appropriate review/process/metadata statuses;
- not generate a note;
- return the item.

It should be used by:

- `read_item.py`;
- `batch_read_pdfs.py`;
- Streamlit PDF Inbox;
- item-card PDF binding actions.

This separates PDF registration from PDF reading.

---

## 11. Streamlit Navigation Simplification

The current GUI has too many tabs.

Consider reducing the interface to four main sections:

```text
1. Inbox
   - weekly collection
   - new items
   - metadata needs review
   - topic needs review

2. Library
   - paper database
   - social/context database
   - filters by topic/source/status

3. Reading
   - PDF Inbox
   - local PDF binding
   - note generation / upgrade
   - item note preview

4. Topics
   - topic overview
   - synthesis readiness
   - topic preview
   - run synthesis
   - extract related items
```

If keeping the current tab structure is easier, at least:

- add PDF Inbox;
- downgrade Topic Workspace;
- avoid making the user maintain `research_workspace.md`.

---

## 12. Status Model Clarification

Keep the current simplified process status model:

```text
unread -> noted -> used_in_synthesis
```

Reading depth should remain in metadata:

```text
metadata.reading_mode = metadata-only / text-draft / kimi
metadata.reading_status = metadata_only / text_extracted / model_parsed_pdf
metadata.summary_status = none / text-draft / summarized
```

PDF registration should not imply `noted`.

Only note generation should move an item to:

```text
process_status = noted
```

---

## 13. What Not to Do

Do not:

- reintroduce automatic route cards;
- add Notion/Zotero sync in this PR;
- create a generic task manager;
- make the user maintain done/skipped follow-up tasks;
- require the user to manually edit per-paper notes after doing follow-up work;
- make `research_workspace.md` a canonical state source;
- add large extracted paper text to committed notes;
- change away from `data/items.jsonl`.

---

## 14. Definition of Done

This refactor is successful if the following are true:

1. A PDF dropped into `literature/inbox/papers/` appears in the GUI as an unregistered local PDF.
2. The user can register that PDF as a reviewable item without reading it.
3. The user can generate a text-draft or Kimi note from the GUI.
4. The user can upgrade an existing text-draft note to a Kimi note.
5. Paper note recommendations naming concrete sources become new candidate items in `data/items.jsonl`.
6. Generic follow-up actions no longer clutter Topic Workspace.
7. Topic Workspace is no longer a manually maintained task/discussion document.
8. The user can continue working primarily through keep / reject / download / register / read / synthesize actions.

The main principle is:

> Concrete recommended sources should become items. Generic advice should disappear.
