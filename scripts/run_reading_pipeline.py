"""Read downloaded PDFs with a multimodal model and update Level 0 artifacts.

This pipeline only processes PDFs that are already available locally. It does
not download restricted papers, commit raw PDFs, or mark anything as human
reviewed.
"""

from __future__ import annotations

import argparse
import base64
import csv
import difflib
import hashlib
import json
import os
import re
import sys
import uuid
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import search_literature as literature_search


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

DEFAULT_CONFIG = "configs/pipeline.json"
PDF_NOTE_PATTERN = re.compile(r"^【(?P<note>[^】]+)】[-_ ]*(?P<rest>.+)$")


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


def human_note_from_filename(path: Path) -> str:
    match = PDF_NOTE_PATTERN.match(path.stem)
    if not match:
        return ""
    return match.group("note").strip()


def safe_human_note(value: str) -> str:
    value = re.sub(r'[<>:"/\\|?*\r\n]+', "_", value).strip(" ._-")
    return value[:40]


def filename_without_human_note(path: Path) -> str:
    match = PDF_NOTE_PATTERN.match(path.stem)
    if not match:
        return path.stem
    return match.group("rest").strip()


def venue_short_name(venue: str) -> str:
    normalized = normalize_match_text(venue)
    known = {
        "ieee transactions on wireless communications": "IEEE_TWC",
        "ieee transactions on communications": "IEEE_TCOM",
        "ieee transactions on mobile computing": "IEEE_TMC",
        "ieee transactions on vehicular technology": "IEEE_TVT",
        "ieee transactions on intelligent transportation systems": "IEEE_TITS",
        "ieee transactions on industrial informatics": "IEEE_TII",
        "ieee internet of things journal": "IEEE_IoTJ",
        "ieee wireless communications": "IEEE_WC",
        "ieee network": "IEEE_Network",
        "ieee infocom": "IEEE_INFOCOM",
        "acm mobicom": "ACM_MobiCom",
        "acm mobihoc": "ACM_MobiHoc",
        "arxiv": "arXiv",
    }
    if normalized in known:
        return known[normalized]
    if "ieee transactions" in normalized:
        words = [word for word in normalized.split() if word not in {"ieee", "transactions", "on", "and", "the", "of"}]
        if words:
            return "IEEE_T" + "".join(word[0].upper() for word in words[:4])
    if "ieee" in normalized:
        words = [word for word in normalized.split() if word not in {"ieee", "international", "conference", "workshop", "workshops", "proceedings", "on", "and", "the", "of"}]
        if words:
            return "IEEE_" + "_".join(word[:8].upper() for word in words[:3])
    return slugify(venue)[:40] or "unknown_venue"


def safe_pdf_name(candidate: dict[str, str], human_note: str = "") -> str:
    candidate_id = candidate.get("candidate_id", "") or stable_id(candidate.get("doi", ""), candidate.get("title", ""))
    year = re.sub(r"[^0-9]", "", candidate.get("year", ""))[:4] or "unknown_year"
    venue = venue_short_name(candidate.get("venue", ""))
    title_slug = slugify(candidate.get("title", ""))[:90]
    filename = f"{year}-{venue}-{title_slug or 'unknown_title'}-{candidate_id}.pdf"
    if human_note:
        note = safe_human_note(human_note)
        if note:
            return f"【{note}】-{filename}"
    return filename


def normalize_match_text(value: str) -> str:
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def token_set(value: str) -> set[str]:
    stop = {"a", "an", "and", "for", "in", "of", "on", "the", "to", "with", "using", "use"}
    return {token for token in normalize_match_text(value).split() if len(token) > 2 and token not in stop}


def title_similarity(left: str, right: str) -> float:
    left_norm = normalize_match_text(left)
    right_norm = normalize_match_text(right)
    if not left_norm or not right_norm:
        return 0.0
    sequence_score = difflib.SequenceMatcher(None, left_norm, right_norm).ratio()
    left_tokens = token_set(left_norm)
    right_tokens = token_set(right_norm)
    overlap_score = 0.0
    if left_tokens and right_tokens:
        overlap_score = len(left_tokens & right_tokens) / len(left_tokens | right_tokens)
    return max(sequence_score, overlap_score)


def extract_pdf_metadata_title(raw_text: str) -> str:
    patterns = [
        r"/Title\s*\((?P<title>[^)]{8,300})\)",
        r"<dc:title>\s*<rdf:Alt>\s*<rdf:li[^>]*>(?P<title>[^<]{8,300})</rdf:li>",
        r"<pdf:Title>(?P<title>[^<]{8,300})</pdf:Title>",
    ]
    for pattern in patterns:
        match = re.search(pattern, raw_text, flags=re.IGNORECASE | re.DOTALL)
        if match:
            title = match.group("title")
            title = title.replace(r"\(", "(").replace(r"\)", ")")
            return re.sub(r"\s+", " ", title).strip()
    return ""


def extract_pdf_visible_text(path: Path, max_bytes: int = 2_000_000) -> str:
    data = path.read_bytes()[:max_bytes]
    decoded = data.decode("utf-8", errors="ignore")
    if len(decoded) < 500:
        decoded = data.decode("latin-1", errors="ignore")
    strings = re.findall(r"[A-Za-z][A-Za-z0-9,.:;()\- /]{8,}", decoded)
    return normalize_match_text(" ".join(strings[:1000]))


def extract_pdf_title_with_optional_library(path: Path) -> str:
    for module_name in ["pypdf", "PyPDF2"]:
        try:
            module = __import__(module_name)
            reader = module.PdfReader(str(path))
            metadata = getattr(reader, "metadata", None) or {}
            title = ""
            if hasattr(metadata, "title"):
                title = metadata.title or ""
            elif isinstance(metadata, dict):
                title = metadata.get("/Title", "") or metadata.get("Title", "")
            if title:
                return re.sub(r"\s+", " ", str(title)).strip()
            if reader.pages:
                text = reader.pages[0].extract_text() or ""
                lines = [line.strip() for line in text.splitlines() if len(line.strip()) >= 8]
                if lines:
                    return re.sub(r"\s+", " ", lines[0]).strip()
        except Exception:
            continue
    raw = path.read_bytes()[:2_000_000].decode("latin-1", errors="ignore")
    return extract_pdf_metadata_title(raw)


def extract_pdf_dois(path: Path) -> set[str]:
    text = path.read_bytes()[:2_000_000].decode("latin-1", errors="ignore")
    dois = re.findall(r"10\.\d{4,9}/[-._;()/:A-Za-z0-9]+", text)
    return {doi.rstrip(").,;").lower() for doi in dois}


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


def load_env_file(path: Path) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def write_csv(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def load_config(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def parse_query_topic(path: Path) -> str:
    if not path.exists():
        return ""
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        stripped = raw_line.strip()
        if stripped.startswith("topic:"):
            return stripped.split(":", 1)[1].strip()
    return path.stem


def topic_key_to_slug(config: dict) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for key, query_file in (config.get("topics") or {}).items():
        slug = parse_query_topic(Path(str(query_file)))
        if slug:
            mapping[str(key)] = slug
    return mapping


def resolve_topic_selection(topic: str, config: dict) -> tuple[set[str] | None, str]:
    if topic == "all":
        return None, ""
    mapping = topic_key_to_slug(config)
    if topic in mapping:
        return {mapping[topic]}, mapping[topic]
    if topic in mapping.values():
        return {topic}, topic
    return {topic}, topic


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
    stem = filename_without_human_note(pdf_path).lower()
    for candidate_id, row in candidates.items():
        if candidate_id and candidate_id.lower() in stem:
            return row
    return {}


def candidate_matches_existing(candidate: dict[str, str], candidates: dict[str, dict[str, str]]) -> dict[str, str]:
    candidate_id = candidate.get("candidate_id", "")
    if candidate_id and candidate_id in candidates:
        return candidates[candidate_id]
    doi = candidate.get("doi", "").lower().strip()
    title = normalize_match_text(candidate.get("title", ""))
    for row in candidates.values():
        if doi and row.get("doi", "").lower().strip() == doi:
            return row
        if title and title_similarity(title, row.get("title", "")) >= 0.96:
            return row
    return {}


def append_candidate(candidate: dict[str, str], candidates: dict[str, dict[str, str]], dry_run: bool) -> dict[str, str]:
    existing = candidate_matches_existing(candidate, candidates)
    if existing:
        return existing
    candidate = {field: candidate.get(field, "") for field in literature_search.CANDIDATE_FIELDS}
    now = now_iso()
    candidate["added_at"] = candidate.get("added_at") or now
    candidate["first_seen_at"] = candidate.get("first_seen_at") or now
    candidate["last_seen_at"] = now
    candidate["discovery_run_id"] = candidate.get("discovery_run_id") or f"reading-lookup-{now.replace(':', '').replace('+', 'Z')}"
    candidate["status"] = candidate.get("status") or "candidate"
    candidate["access_status"] = "local_pdf"
    if dry_run:
        print(f"Would add candidate metadata: {candidate.get('title', '')} [{candidate.get('candidate_id', '')}]")
        return candidate
    path = Path("literature/database/paper_candidates.csv")
    rows = read_csv(path)
    rows.append(candidate)
    write_csv(path, literature_search.CANDIDATE_FIELDS, rows)
    candidates[candidate["candidate_id"]] = candidate
    print(f"Added candidate metadata from PDF lookup: {candidate.get('title', '')} [{candidate.get('candidate_id', '')}]")
    return candidate


def infer_candidate_from_pdf(pdf_path: Path, candidates: dict[str, dict[str, str]], topic_filter: set[str] | None) -> tuple[dict[str, str], float, str]:
    scoped = [
        row for row in candidates.values()
        if topic_filter is None or row.get("topic", "") in topic_filter
    ]
    if not scoped:
        return {}, 0.0, "no scoped candidates"

    pdf_dois = extract_pdf_dois(pdf_path)
    for row in scoped:
        doi = row.get("doi", "").lower().strip()
        if doi and doi in pdf_dois:
            return row, 1.0, f"doi:{doi}"

    metadata_title = extract_pdf_title_with_optional_library(pdf_path)
    visible_text = extract_pdf_visible_text(pdf_path)
    filename_title = pdf_path.stem.replace("_", " ").replace("-", " ")

    best_row: dict[str, str] = {}
    best_score = 0.0
    best_reason = ""
    for row in scoped:
        title = row.get("title", "")
        if not title:
            continue
        scores = [
            (title_similarity(filename_title, title), "filename"),
            (title_similarity(metadata_title, title), "pdf metadata title"),
        ]
        title_tokens = token_set(title)
        if title_tokens and visible_text:
            visible_tokens = set(visible_text.split())
            visible_overlap = len(title_tokens & visible_tokens) / len(title_tokens)
            scores.append((min(visible_overlap, 0.66), "pdf visible text tokens"))
        score, reason = max(scores, key=lambda item: item[0])
        if score > best_score:
            best_row = row
            best_score = score
            best_reason = reason
    return best_row, best_score, best_reason


def pdf_lookup_query(pdf_path: Path) -> tuple[str, str]:
    dois = sorted(extract_pdf_dois(pdf_path))
    if dois:
        return dois[0], "doi"
    title = extract_pdf_title_with_optional_library(pdf_path)
    if title:
        return title, "pdf metadata title"
    visible_text = extract_pdf_visible_text(pdf_path)
    visible_words = visible_text.split()
    if len(visible_words) >= 6:
        return " ".join(visible_words[:24]), "pdf visible text"
    return filename_without_human_note(pdf_path).replace("_", " ").replace("-", " "), "filename"


def lookup_pdf_online(pdf_path: Path, topic: str, providers: list[str], limit: int, dry_run: bool) -> tuple[dict[str, str], float, str]:
    query, query_source = pdf_lookup_query(pdf_path)
    if not query.strip():
        return {}, 0.0, "no lookup query"
    if dry_run:
        print(f"Would look up PDF metadata online from {query_source}: {query[:120]}")
        return {}, 0.0, f"dry-run {query_source}"

    searchers = {
        "openalex": literature_search.search_openalex,
        "crossref": literature_search.search_crossref,
        "semantic_scholar": literature_search.search_semantic_scholar,
        "arxiv": literature_search.search_arxiv,
    }
    candidates: list[dict[str, str]] = []
    for provider in providers:
        searcher = searchers.get(provider)
        if not searcher:
            continue
        try:
            candidates.extend(searcher(query, topic, limit, ""))
        except Exception as exc:
            print(f"PDF metadata lookup failed via {provider}: {exc}", file=sys.stderr)

    if not candidates:
        return {}, 0.0, f"no online metadata match from {query_source}"

    pdf_dois = extract_pdf_dois(pdf_path)
    for row in candidates:
        doi = row.get("doi", "").lower().strip()
        if doi and doi in pdf_dois:
            return row, 1.0, f"online doi match via {row.get('source', '')}"

    best_row: dict[str, str] = {}
    best_score = 0.0
    best_reason = ""
    extracted_title = extract_pdf_title_with_optional_library(pdf_path) or filename_without_human_note(pdf_path)
    for row in candidates:
        score = title_similarity(extracted_title, row.get("title", ""))
        if score > best_score:
            best_row = row
            best_score = score
            best_reason = f"online title match via {row.get('source', '')}"
    return best_row, best_score, best_reason


def unique_pdf_target(path: Path, filename: str) -> Path:
    target = path.parent / filename
    if not target.exists() or target.resolve() == path.resolve():
        return target
    stem = target.stem
    suffix = target.suffix
    for index in range(2, 100):
        candidate = target.with_name(f"{stem}_{index}{suffix}")
        if not candidate.exists():
            return candidate
    return target.with_name(f"{stem}_{stable_id(str(path), now_iso())}{suffix}")


def rename_pdf_for_candidate(pdf_path: Path, candidate: dict[str, str], dry_run: bool, enabled: bool) -> Path:
    if not enabled or not candidate:
        return pdf_path
    candidate_id = candidate.get("candidate_id", "")
    if candidate_id and candidate_id.lower() in pdf_path.stem.lower():
        return pdf_path
    human_note = human_note_from_filename(pdf_path)
    target = unique_pdf_target(pdf_path, safe_pdf_name(candidate, human_note))
    if target == pdf_path:
        return pdf_path
    if dry_run:
        print(f"Would rename {pdf_path} -> {target}")
        return pdf_path
    pdf_path.rename(target)
    print(f"Renamed {pdf_path} -> {target}")
    return target


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


def extract_response_output_text(data: dict) -> str:
    if data.get("output_text"):
        return str(data["output_text"])
    output_parts = []
    for item in data.get("output", []):
        for content in item.get("content", []):
            if content.get("type") in {"output_text", "text"}:
                output_parts.append(content.get("text", ""))
    return "\n".join(part for part in output_parts if part).strip()


def extract_chat_completion_text(data: dict) -> str:
    choices = data.get("choices") or []
    if not choices:
        return ""
    message = choices[0].get("message") or {}
    content = message.get("content", "")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict):
                parts.append(str(item.get("text", "") or item.get("content", "")))
        return "\n".join(part for part in parts if part).strip()
    return str(content or "")


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
    return extract_response_output_text(data)


def multipart_file_body(path: Path, fields: dict[str, str]) -> tuple[bytes, str]:
    boundary = f"----low-altitude-{uuid.uuid4().hex}"
    chunks: list[bytes] = []
    for name, value in fields.items():
        chunks.extend(
            [
                f"--{boundary}\r\n".encode("utf-8"),
                f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode("utf-8"),
                value.encode("utf-8"),
                b"\r\n",
            ]
        )
    chunks.extend(
        [
            f"--{boundary}\r\n".encode("utf-8"),
            f'Content-Disposition: form-data; name="file"; filename="{path.name}"\r\n'.encode("utf-8"),
            b"Content-Type: application/pdf\r\n\r\n",
            path.read_bytes(),
            b"\r\n",
            f"--{boundary}--\r\n".encode("utf-8"),
        ]
    )
    return b"".join(chunks), boundary


def moonshot_request_json(url: str, api_key: str, payload: dict, timeout: int) -> dict:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def kimi_upload_file(pdf_path: Path, api_key: str, base_url: str, timeout: int) -> str:
    body, boundary = multipart_file_body(pdf_path, {"purpose": "file-extract"})
    request = urllib.request.Request(
        f"{base_url.rstrip('/')}/files",
        data=body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": f"multipart/form-data; boundary={boundary}",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        data = json.loads(response.read().decode("utf-8"))
    return str(data.get("id", ""))


def kimi_file_content(file_id: str, api_key: str, base_url: str, timeout: int) -> str:
    request = urllib.request.Request(
        f"{base_url.rstrip('/')}/files/{file_id}/content",
        headers={"Authorization": f"Bearer {api_key}"},
        method="GET",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read().decode("utf-8", errors="replace")


def kimi_pdf_read(pdf_path: Path, prompt: str, model: str, api_key: str, timeout: int, base_url: str) -> str:
    file_id = kimi_upload_file(pdf_path, api_key, base_url, timeout)
    if not file_id:
        raise RuntimeError("Kimi file upload did not return a file id.")
    file_content = kimi_file_content(file_id, api_key, base_url, timeout)
    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "You are Kimi, an AI assistant provided by Moonshot AI. You are particularly skilled in Chinese and English technical reading. Follow the user's evidence labeling and Level 0 research repository rules strictly.",
            },
            {
                "role": "system",
                "content": file_content,
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
    }
    data = moonshot_request_json(f"{base_url.rstrip('/')}/chat/completions", api_key, payload, timeout)
    return extract_chat_completion_text(data)


def read_pdf_with_provider(pdf_path: Path, prompt: str, provider: str, model: str, timeout: int, provider_config: dict | None = None) -> str:
    provider_config = provider_config or {}
    if provider == "openai":
        api_key_env = str(provider_config.get("api_key_env") or "OPENAI_API_KEY")
        api_key = os.environ.get(api_key_env, "")
        if not api_key:
            raise RuntimeError(f"{api_key_env} missing")
        return openai_pdf_read(pdf_path, prompt, model, api_key, timeout)
    if provider == "kimi":
        api_key_env = str(provider_config.get("api_key_env") or "MOONSHOT_API_KEY")
        fallback_api_key_env = str(provider_config.get("fallback_api_key_env") or "KIMI_API_KEY")
        api_key = os.environ.get(api_key_env, "") or os.environ.get(fallback_api_key_env, "")
        if not api_key:
            raise RuntimeError(f"{api_key_env} or {fallback_api_key_env} missing")
        base_url_env = str(provider_config.get("base_url_env") or "MOONSHOT_BASE_URL")
        fallback_base_url_env = str(provider_config.get("fallback_base_url_env") or "KIMI_BASE_URL")
        default_base_url = str(provider_config.get("default_base_url") or "https://api.moonshot.cn/v1")
        base_url = os.environ.get(base_url_env, "") or os.environ.get(fallback_base_url_env, "") or default_base_url
        return kimi_pdf_read(pdf_path, prompt, model, api_key, timeout, base_url)
    raise RuntimeError(f"Unsupported reading provider: {provider}")


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
    parser.add_argument("--config", default=DEFAULT_CONFIG, help="Pipeline JSON config.")
    parser.add_argument("--topic", default="all", help="Topic key, topic slug, or 'all'.")
    parser.add_argument("--inbox", default="literature/inbox/papers", help="Directory containing manually downloaded PDFs.")
    parser.add_argument("--open-access-dir", default="literature/pdfs/open_access", help="Directory containing open-access PDFs.")
    parser.add_argument("--provider", choices=["kimi", "openai"], default=None, help="PDF reading provider.")
    parser.add_argument("--model", default=None, help="Model for PDF reading.")
    parser.add_argument("--max-papers", type=int, default=None, help="Maximum PDFs to process in one run.")
    parser.add_argument("--timeout", type=int, default=300, help="OpenAI request timeout in seconds.")
    parser.add_argument("--force", action="store_true", help="Re-read PDFs even if the fingerprint already appears in the note.")
    parser.add_argument("--rename-threshold", type=float, default=0.72, help="Minimum candidate match confidence for automatic PDF renaming.")
    parser.add_argument("--online-lookup-threshold", type=float, default=0.82, help="Minimum confidence for adding online metadata for an unknown PDF.")
    parser.add_argument("--lookup-providers", default="openalex,crossref,semantic_scholar,arxiv", help="Comma-separated providers for unknown PDF metadata lookup.")
    parser.add_argument("--lookup-limit", type=int, default=3, help="Max online metadata results per provider for an unknown PDF.")
    parser.add_argument("--no-online-lookup", action="store_true", help="Do not query online metadata sources for unknown PDFs.")
    parser.add_argument("--no-auto-rename", action="store_true", help="Do not rename PDFs after high-confidence candidate matching.")
    parser.add_argument("--rename-only", action="store_true", help="Only identify and rename PDFs; do not call OpenAI or write reading artifacts.")
    parser.add_argument("--dry-run", action="store_true", help="Show planned work without writing or calling OpenAI.")
    args = parser.parse_args()
    load_env_file(Path(".env"))
    config = load_config(Path(args.config))
    reading_config = config.get("reading") or {}
    provider = args.provider or str(reading_config.get("provider") or "kimi")
    provider_config = (reading_config.get("providers") or {}).get(provider, {})
    model_env = str(provider_config.get("model_env") or reading_config.get("model_env") or ("KIMI_READING_MODEL" if provider == "kimi" else "OPENAI_READING_MODEL"))
    default_model = str(provider_config.get("default_model") or reading_config.get("default_model") or ("kimi-k2.6" if provider == "kimi" else "gpt-5.5"))
    model = args.model or os.environ.get(model_env) or default_model
    max_papers = args.max_papers if args.max_papers is not None else int(reading_config.get("max_papers_per_run", 5))
    topic_filter, unmatched_topic = resolve_topic_selection(args.topic, config)
    if topic_filter:
        print(f"Resolved topic '{args.topic}' to: {', '.join(sorted(topic_filter))}")

    for directory in ARTIFACT_DIRS:
        if not args.dry_run:
            Path(directory).mkdir(parents=True, exist_ok=True)

    candidates = load_candidates()
    pdfs = discover_pdfs(Path(args.inbox), Path(args.open_access_dir))
    if not pdfs:
        print("No local PDFs found. Nothing to read.")
        return 0

    processed_by_topic: dict[str, list[dict[str, str]]] = {}
    processed_count = 0

    for pdf_path in pdfs:
        if processed_count >= max_papers:
            break
        if args.rename_only:
            processed_count += 1
        candidate = match_candidate(pdf_path, candidates)
        match_score = 1.0 if candidate else 0.0
        match_reason = "candidate_id in filename" if candidate else ""
        if not candidate:
            local_candidate, local_score, local_reason = infer_candidate_from_pdf(pdf_path, candidates, topic_filter)
            candidate = local_candidate
            match_score = local_score
            match_reason = local_reason
            if local_candidate and local_score >= args.rename_threshold:
                print(f"Matched {pdf_path.name} -> {candidate.get('candidate_id', '')} by {match_reason} (confidence {match_score:.2f})")
                pdf_path = rename_pdf_for_candidate(pdf_path, candidate, args.dry_run, not args.no_auto_rename)
            elif not args.no_online_lookup:
                lookup_topic = unmatched_topic or (next(iter(topic_filter)) if topic_filter else "unknown_topic")
                lookup_providers = [provider.strip() for provider in args.lookup_providers.split(",") if provider.strip()]
                online_candidate, online_score, online_reason = lookup_pdf_online(pdf_path, lookup_topic, lookup_providers, args.lookup_limit, args.dry_run)
                if online_candidate and online_score >= args.online_lookup_threshold:
                    candidate = append_candidate(online_candidate, candidates, args.dry_run)
                    match_score = online_score
                    match_reason = online_reason
                    print(f"Matched {pdf_path.name} -> {candidate.get('candidate_id', '')} by {match_reason} (confidence {match_score:.2f})")
                    pdf_path = rename_pdf_for_candidate(pdf_path, candidate, args.dry_run, not args.no_auto_rename)
                else:
                    review_candidate = online_candidate or local_candidate
                    review_score = online_score if online_candidate else local_score
                    review_reason = online_reason if online_candidate else local_reason
                    append_review(
                        f"Low-confidence PDF metadata match ({review_score:.2f} by {review_reason})",
                        "Confirm the paper metadata manually, improve the filename, or rerun with a lower threshold only if the match is correct.",
                        pdf_path,
                        lookup_topic,
                        (review_candidate or {}).get("title", "") or pdf_path.stem,
                        args.dry_run,
                    )
                    if review_candidate:
                        print(f"Skipped low-confidence match for {pdf_path.name}: {review_candidate.get('title', '')} ({review_score:.2f})")
                    else:
                        print(f"Skipped unidentified PDF: {pdf_path.name}")
                    continue
            elif candidate:
                topic_hint = candidate.get("topic", "") or unmatched_topic or "unknown_topic"
                append_review(
                    f"Low-confidence PDF candidate match ({match_score:.2f} by {match_reason})",
                    "Rename the PDF manually or rerun with a lower --rename-threshold only if the match is correct.",
                    pdf_path,
                    topic_hint,
                    candidate.get("title", "") or pdf_path.stem,
                    args.dry_run,
                )
                print(f"Skipped low-confidence match for {pdf_path.name}: {candidate.get('title', '')} ({match_score:.2f})")
                continue
        topic = candidate.get("topic", "") or unmatched_topic or "unknown_topic"
        if topic_filter is not None and topic not in topic_filter:
            continue
        if args.rename_only:
            if not candidate:
                append_review("Could not identify PDF candidate", "Rename the PDF manually with a candidate_id prefix or add the paper to paper_candidates.csv.", pdf_path, topic, pdf_path.stem, args.dry_run)
            continue
        paper_id = paper_id_for(pdf_path, candidate)
        title = candidate.get("title", "") or pdf_path.stem
        fingerprint = sha256_file(pdf_path)
        note_path = Path("literature/notes/paper_notes") / f"{paper_id}.md"
        if not args.force and note_has_fingerprint(note_path, fingerprint):
            print(f"Skipped already-read PDF: {pdf_path}")
            continue
        if args.dry_run:
            print(f"Would read {pdf_path} -> {note_path}")
            processed_count += 1
            continue
        prompt = build_prompt(candidate, fingerprint)
        try:
            note = read_pdf_with_provider(pdf_path, prompt, provider, model, args.timeout, provider_config)
        except Exception as exc:
            append_review(f"{provider} PDF reading failed: {exc}", "Inspect the provider API key, model, PDF size limits, and network access, then rerun.", pdf_path, topic, title, args.dry_run)
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
                    "reading_model": model,
                    "reading_provider": provider,
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
        write_support_artifacts(paper_id, topic, title, note, model, fingerprint)
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
