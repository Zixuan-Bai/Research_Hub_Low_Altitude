# Prompt: Literature Search

You are helping build a Level 0 low-altitude research-intelligence hub.

Use the selected query YAML under `literature/queries/`.

## Task

Collect candidate papers for the topic.

For each candidate, record:

- title;
- authors;
- year;
- venue;
- DOI or URL if available;
- source database;
- topic relevance;
- source type;
- venue tier or source quality;
- category: regulation / architecture / communication model / capacity / interference / safety / control / networking / survey;
- practical relevance;
- reading status.

## Rules

- Do not fabricate references.
- Do not invent DOI, venue, author, year, or numerical results.
- If metadata is uncertain, mark `uncertain metadata`.
- If only metadata is available, mark `metadata only`.
- Do not summarize full-paper claims unless full text is available.
- Separate `paper-supported`, `inferred`, and `proposal`.
- Prefer high-quality venues and practical sources when selecting candidates.
- Low-tier or unclear-venue papers should be marked low confidence unless corroborated.

## Output

Create or update a candidate table. Add open questions instead of unsupported claims.
