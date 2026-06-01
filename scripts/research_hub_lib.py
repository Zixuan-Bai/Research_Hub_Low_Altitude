"""Shared utilities for the lightweight research-intelligence workflow.

The mainline uses one JSONL item store, concise Chinese notes, a review
dashboard, and a topic workspace for human-led synthesis. It deliberately
avoids the older candidate/review/acquisition CSV state machine.
"""

from __future__ import annotations

import base64
import html
import hashlib
import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
import uuid
import xml.etree.ElementTree as ET
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Iterable


ITEMS_PATH = Path("data/items.jsonl")
MANUAL_ITEMS_PATH = Path("data/manual_items.jsonl")
DEFAULT_CONFIG = Path("configs/pipeline.json")
DEFAULT_CONTEXT_CONFIG = Path("configs/context_sources.json")
PDF_TEXT_CACHE_DIR = Path(".local/pdf_text_cache")
USER_AGENT = "low-altitude-research-hub/0.2"
NEEDS_TOPIC_REVIEW = "needs_topic_review"
REVIEW_STATUSES = {"new", "kept", "rejected", "downloaded"}
PROCESS_STATUSES = {"unread", "noted", "used_in_synthesis"}
LEGACY_PROCESS_STATUS_MAP = {"read": "noted", "summarized": "noted"}
METADATA_STATUSES = {"auto", "needs_review", "verified"}
METADATA_RANK = {"auto": 0, "needs_review": 1, "verified": 2}
PROCESS_RANK = {
    "unread": 0,
    "noted": 1,
    "used_in_synthesis": 2,
}
SOURCE_TYPE_LABELS = {
    "paper": "论文",
    "standard": "标准",
    "policy": "政策",
    "whitepaper": "白皮书",
    "report": "报告",
    "industry": "产业信号",
    "news": "新闻/动态",
}
CONTEXT_SOURCE_TYPES = {"news", "standard", "policy", "whitepaper", "report", "industry"}
DOCUMENT_ACCESS_OPTIONS = {
    "direct_pdf": "可直接下载 PDF",
    "html_fulltext": "网页正文可读",
    "landing_page": "门户/专题入口",
    "catalog_or_paywalled": "目录或付费入口",
    "news_or_portal": "新闻/门户动态",
    "needs_document_search": "需要继续找原文",
}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def today_string() -> str:
    return date.today().isoformat()


def stable_id(*parts: str) -> str:
    source = "|".join(str(part).strip().lower() for part in parts if str(part).strip())
    return hashlib.sha1(source.encode("utf-8")).hexdigest()[:12]


def slugify(value: str) -> str:
    chars: list[str] = []
    for char in value.lower():
        if char.isalnum():
            chars.append(char)
        elif chars and chars[-1] != "_":
            chars.append("_")
    return "".join(chars).strip("_") or "item"


def normalize_topic_list(values: Iterable[object], primary_topic: str = "") -> list[str]:
    topics: list[str] = []
    for value in [primary_topic, *list(values)]:
        if value is None:
            continue
        for part in re.split(r"[,;\n，；\s]+", str(value)):
            topic = slugify(part)
            if topic and topic not in topics and topic != NEEDS_TOPIC_REVIEW:
                topics.append(topic)
    return topics


def item_topics(item: dict) -> list[str]:
    raw_topics = item.get("topics") or []
    if isinstance(raw_topics, str):
        raw_topics = re.split(r"[,;\n，；\s]+", raw_topics)
    elif not isinstance(raw_topics, list):
        raw_topics = []
    return normalize_topic_list(raw_topics, str(item.get("topic") or ""))


def item_has_topic(item: dict, topic: str) -> bool:
    topic = slugify(topic)
    return topic == str(item.get("topic") or "") or topic in item_topics(item)


def safe_filename(value: str, fallback: str = "item", max_length: int = 140) -> str:
    value = normalize_space(value)
    value = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", value)
    value = re.sub(r"\s+", " ", value).strip(" ._")
    if not value:
        value = fallback
    if len(value) > max_length:
        value = value[:max_length].rstrip(" ._")
    return value or fallback


def safe_filename_part(value: str, fallback: str, max_length: int = 60) -> str:
    return safe_filename(value, fallback=fallback, max_length=max_length)


def normalize_space(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def normalize_match_text(value: str) -> str:
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def token_set(value: str) -> set[str]:
    stop = {"a", "an", "and", "for", "in", "of", "on", "the", "to", "with", "using", "use"}
    return {token for token in normalize_match_text(value).split() if len(token) > 2 and token not in stop}


def title_similarity(left: str, right: str) -> float:
    import difflib

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


def load_env_file(path: Path = Path(".env")) -> None:
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


def load_config(path: Path = DEFAULT_CONFIG) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def write_config(config: dict, path: Path = DEFAULT_CONFIG) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def parse_simple_query_yaml(path: Path) -> dict[str, object]:
    topic = ""
    description = ""
    lists: dict[str, list[str]] = {
        "seed_keywords": [],
        "required_terms_any": [],
        "exclude_terms_any": [],
    }
    current_list = ""
    if not path.exists():
        return {"topic": path.stem, "description": "", **lists}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        stripped = raw_line.strip()
        if stripped.startswith("topic:"):
            topic = stripped.split(":", 1)[1].strip()
            current_list = ""
        elif stripped.startswith("description:"):
            description = stripped.split(":", 1)[1].strip()
            current_list = ""
        elif stripped.endswith(":"):
            current_list = stripped[:-1] if stripped[:-1] in lists else ""
        elif current_list and stripped.startswith("- "):
            lists[current_list].append(stripped[2:].strip())
        elif current_list and stripped and not raw_line.startswith(" "):
            current_list = ""
    return {"topic": topic or path.stem, "description": description, **lists}


def topic_key_to_query_files(config: dict) -> dict[str, Path]:
    return {str(key): Path(str(value)) for key, value in (config.get("topics") or {}).items()}


def topic_key_to_slug(config: dict) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for key, query_file in topic_key_to_query_files(config).items():
        mapping[key] = str(parse_simple_query_yaml(query_file)["topic"])
    return mapping


def selected_query_files(topic: str, config: dict) -> list[Path]:
    query_files = topic_key_to_query_files(config)
    if topic == "all":
        return list(query_files.values())
    slug_map = topic_key_to_slug(config)
    if topic in query_files:
        return [query_files[topic]]
    for key, slug in slug_map.items():
        if topic == slug:
            return [query_files[key]]
    candidate = Path(f"literature/queries/{topic}.yaml")
    return [candidate]


def query_file_for_topic(topic: str, config: dict | None = None) -> Path:
    config = config if config is not None else load_config()
    slug_map = topic_key_to_slug(config)
    query_files = topic_key_to_query_files(config)
    for key, slug in slug_map.items():
        if topic == slug:
            return query_files[key]
    if topic in query_files:
        return query_files[topic]
    return Path("literature/queries") / f"{slugify(topic)}.yaml"


def topic_config_key(topic_slug: str, existing: dict[str, str]) -> str:
    key = slugify(topic_slug)
    if key not in existing:
        return key
    index = 2
    while f"{key}_{index}" in existing:
        index += 1
    return f"{key}_{index}"


def write_topic_query_template(path: Path, topic_slug: str, title_hint: str = "") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    description = f"Candidate topic created from GUI review. Seed title: {title_hint}".strip()
    text = f"""topic: {topic_slug}
status: needs_keywords
description: {description}

seed_keywords:
  - {topic_slug.replace("_", " ")}

required_terms_any:
  - UAV
  - UAS
  - drone
  - low altitude

exclude_terms_any:
  - unrelated

must_extract:
  - problem setting
  - method
  - assumptions
  - evidence
  - limitations

exclude:
  - papers unrelated to low-altitude communication or autonomous aerial systems
"""
    path.write_text(text, encoding="utf-8")


def ensure_topic_exists(topic_slug: str, title_hint: str = "", config_path: Path = DEFAULT_CONFIG) -> tuple[Path, bool]:
    topic_slug = slugify(topic_slug)
    config = load_config(config_path)
    topics = dict(config.get("topics") or {})
    slug_map = topic_key_to_slug(config)
    if topic_slug in slug_map.values():
        return query_file_for_topic(topic_slug, config), False
    query_path = Path("literature/queries") / f"{topic_slug}.yaml"
    if not query_path.exists():
        write_topic_query_template(query_path, topic_slug, title_hint)
    key = topic_config_key(topic_slug, topics)
    topics[key] = query_path.as_posix()
    config["topics"] = topics
    write_config(config, config_path)
    return query_path, True


def topic_query_improvement_prompt(topic_slug: str, query_path: Path, query: dict) -> str:
    query_text = query_path.read_text(encoding="utf-8", errors="ignore") if query_path.exists() else ""
    return f"""请帮我补全低空研究情报库的 topic query 配置。

仓库定位：
- 这是 Level 0 研究情报库，不要生成最终研究方向、创新性判断或路线卡。
- topic 只用于每周收集、筛选和后续人工复核。
- 输出应保守，区分 paper-supported / inferred / proposal / unsupported。

目标：
1. 保留 topic slug：`{topic_slug}`。
2. 根据这个 topic，补充接近现有 `literature/queries/*.yaml` 信息量的 query 配置。
3. 增加足够的 `seed_keywords`、`required_terms_any`、`exclude_terms_any`、`must_extract` 和 `exclude`。
4. 关键词需要覆盖低空通信 / UAV 系统 / 监管或工程约束中的相关表达，避免把无关交通、泛 IoT、泛机器人论文大量收进来。
5. 如果信息不足，请用 `needs-review` 标出需要我人工确认的部分，不要编造标准号、论文或事实。

当前文件：`{query_path.as_posix()}`

当前内容：
```yaml
{query_text.strip()}
```

请只返回建议替换的 YAML 内容。"""


def topic_query_needs_keywords(topic_slug: str, config: dict | None = None) -> tuple[bool, Path, dict]:
    config = config if config is not None else load_config()
    query_path = query_file_for_topic(topic_slug, config)
    query = parse_simple_query_yaml(query_path)
    seed = [value for value in query.get("seed_keywords", []) or [] if value]
    required = [value for value in query.get("required_terms_any", []) or [] if value]
    status_needs = "needs_keywords" in query_path.read_text(encoding="utf-8", errors="ignore") if query_path.exists() else True
    return status_needs or len(seed) < 5 or len(required) < 5, query_path, query


def topics_needing_query_review(config: dict | None = None) -> list[dict]:
    config = config if config is not None else load_config()
    rows: list[dict] = []
    for topic in sorted(set(topic_key_to_slug(config).values())):
        needs_review, query_path, query = topic_query_needs_keywords(topic, config)
        if not needs_review:
            continue
        rows.append(
            {
                "topic": topic,
                "query_path": query_path,
                "query": query,
                "seed_keyword_count": len(query.get("seed_keywords", []) or []),
                "required_term_count": len(query.get("required_terms_any", []) or []),
                "prompt": topic_query_improvement_prompt(topic, query_path, query),
            }
        )
    return rows


def resolve_topic_for_pdf(pdf_path: Path, requested_topic: str, config: dict) -> tuple[str, float, str]:
    if requested_topic != "auto":
        topic = topic_key_to_slug(config).get(requested_topic, requested_topic)
        ensure_topic_exists(topic, title_hint=extract_pdf_title(pdf_path) or pdf_path.stem)
        return topic, 1.0, "manual topic"
    return infer_topic_for_pdf(pdf_path, config)


def topic_vocabulary(config: dict) -> dict[str, set[str]]:
    vocabulary: dict[str, set[str]] = {}
    for _key, query_file in topic_key_to_query_files(config).items():
        query_data = parse_simple_query_yaml(query_file)
        topic = str(query_data["topic"])
        terms: set[str] = set()
        for field in ["topic", "description"]:
            terms.update(token_set(str(query_data.get(field, ""))))
        for field in ["seed_keywords", "required_terms_any"]:
            for value in query_data.get(field, []) or []:
                terms.update(token_set(str(value)))
        if terms:
            vocabulary[topic] = terms
    return vocabulary


def infer_topic_for_pdf(path: Path, config: dict, min_score: float = 0.08) -> tuple[str, float, str]:
    """Suggest a known topic from PDF title/text, or mark it for human review."""
    title = extract_pdf_title(path) or path.stem
    visible = extract_pdf_visible_text(path, max_bytes=700_000)
    tokens = token_set(f"{path.stem} {title} {visible[:4000]}")
    if not tokens:
        return NEEDS_TOPIC_REVIEW, 0.0, "no usable PDF text"
    scores: list[tuple[float, str, int, int]] = []
    for topic, terms in topic_vocabulary(config).items():
        if not terms:
            continue
        overlap = tokens & terms
        score = len(overlap) / max(len(terms), 1)
        scores.append((score, topic, len(overlap), len(terms)))
    if not scores:
        return NEEDS_TOPIC_REVIEW, 0.0, "no configured topic vocabulary"
    best_score, best_topic, matched, total = max(scores, key=lambda row: row[0])
    if best_score < min_score:
        return NEEDS_TOPIC_REVIEW, best_score, f"low topic match: {matched}/{total} terms"
    return best_topic, best_score, f"matched {matched}/{total} configured topic terms"


def read_jsonl(path: Path) -> list[dict]:
    if not path.exists() or path.stat().st_size == 0:
        return []
    rows: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def write_jsonl(path: Path, rows: Iterable[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = "\n".join(json.dumps(row, ensure_ascii=False, sort_keys=True) for row in rows)
    path.write_text(text + ("\n" if text else ""), encoding="utf-8")


def load_items(path: Path = ITEMS_PATH) -> list[dict]:
    return read_jsonl(path)


def load_manual_items(path: Path = MANUAL_ITEMS_PATH) -> list[dict]:
    rows = read_jsonl(path)
    normalized: list[dict] = []
    for row in rows:
        if not row.get("id"):
            row["id"] = item_id(row.get("url", ""), row.get("title", ""))
        row.setdefault("source", "manual")
        row.setdefault("source_type", "paper")
        row.setdefault("review_status", "new")
        row.setdefault("process_status", "unread")
        row = sync_status_fields(row)
        row.setdefault("created_at", now_iso())
        row["updated_at"] = now_iso()
        normalized.append(row)
    return normalized


def item_id(url: str = "", title: str = "", doi: str = "") -> str:
    return stable_id(doi, url, title)


def review_status(item: dict) -> str:
    value = item.get("review_status")
    if value in REVIEW_STATUSES:
        return value
    return "new"


def process_status(item: dict) -> str:
    value = item.get("process_status")
    if value in LEGACY_PROCESS_STATUS_MAP:
        return LEGACY_PROCESS_STATUS_MAP[value]
    if value in PROCESS_STATUSES:
        return value
    return "unread"


def metadata_status(item: dict) -> str:
    value = item.get("metadata_status")
    if value in METADATA_STATUSES:
        return value
    return "auto"


def sync_status_fields(item: dict) -> dict:
    item["review_status"] = review_status(item)
    item["process_status"] = process_status(item)
    item["metadata_status"] = metadata_status(item)
    item.pop("status", None)
    return item


def infer_document_access(item: dict) -> tuple[str, str]:
    """Classify whether a social/context item points to a usable document."""
    metadata = item.get("metadata") or {}
    explicit = str(metadata.get("document_access") or "").strip()
    if explicit in DOCUMENT_ACCESS_OPTIONS and (metadata.get("document_access_reviewed_at") or metadata.get("document_access_source") == "manual"):
        return explicit, "manual metadata"

    url = str(item.get("url") or "").strip().lower()
    pdf_url = str(item.get("pdf_url") or "").strip().lower()
    source_type = str(item.get("source_type") or "").strip().lower()
    source = str(item.get("source") or "").strip().lower()
    title = str(item.get("title") or "").strip().lower()
    text = " ".join([url, pdf_url, source, title])

    if pdf_url or url.endswith(".pdf") or ".pdf?" in url:
        return "direct_pdf", "explicit PDF URL"
    if any(term in text for term in ["store.", "shop.", "catalog", "dynareport", "wivsspec", "standard-specification", "astm.org"]):
        return "catalog_or_paywalled", "catalog, standard store, or paywalled entry"
    if source_type == "news" or any(term in text for term in ["/news/", "/press", "news", "t20"]):
        return "news_or_portal", "news or portal-style page"
    if any(term in text for term in ["project", "program", "overview", "traffic_management", "u-space", "utm"]):
        return "landing_page", "topic or project landing page"
    if source_type in {"policy", "report", "whitepaper", "industry"}:
        return "html_fulltext", "likely readable HTML source; verify manually"
    if source_type == "standard":
        return "needs_document_search", "standard metadata without direct document"
    return "needs_document_search", "no direct document signal"


def apply_document_access_metadata(item: dict) -> dict:
    if str(item.get("source_type") or "") not in CONTEXT_SOURCE_TYPES:
        return item
    metadata = item.setdefault("metadata", {})
    access, reason = infer_document_access(item)
    metadata["document_access"] = access
    metadata["document_access_reason"] = reason
    metadata.setdefault("document_access_source", "auto")
    return item


def markdown_plain(value: str) -> str:
    value = re.sub(r"`([^`]*)`", r"\1", value or "")
    value = re.sub(r"\*\*([^*]*)\*\*", r"\1", value)
    value = re.sub(r"\*([^*]*)\*", r"\1", value)
    return normalize_space(value.strip(" -：:。；;，,"))


def strip_evidence_prefix(value: str) -> tuple[str, str]:
    text = markdown_plain(value)
    match = re.match(r"^(paper-supported|inferred|proposal|unsupported)\s*[:：]\s*(?P<body>.+)$", text)
    if not match:
        return "", text
    return match.group(1), normalize_space(match.group("body"))


def note_section(note: str, title: str) -> str:
    pattern = re.compile(rf"^#+\s*{re.escape(title)}\s*$", re.MULTILINE)
    match = pattern.search(note)
    if not match:
        return ""
    next_heading = re.search(r"^#+\s+", note[match.end() :], flags=re.MULTILINE)
    end = match.end() + next_heading.start() if next_heading else len(note)
    return note[match.end() : end].strip()


def metadata_from_note(note: str) -> dict:
    section = note_section(note, "元数据")
    result: dict[str, str] = {}
    if not section:
        return result
    for raw_line in section.splitlines():
        line = raw_line.strip()
        if not line.startswith(("-", "*")):
            continue
        evidence, body = strip_evidence_prefix(line.lstrip("-* "))
        if evidence == "unsupported" and "doi" in body.lower() and any(term in body for term in ["不一致", "错误", "不匹配"]):
            result["doi_conflict"] = body
            continue
        if evidence and evidence != "paper-supported":
            continue
        if "：" in body:
            key, value = body.split("：", 1)
        elif ":" in body:
            key, value = body.split(":", 1)
        else:
            continue
        key = markdown_plain(key)
        value = markdown_plain(value)
        if not value or any(term in value for term in ["未提供", "不一致", "unknown", "metadata only"]):
            continue
        if "标题" in key:
            result["title"] = value
        elif "作者" in key:
            result["authors"] = re.sub(r"[、,，]\s*", "; ", value)
        elif "年份" in key or key.lower() == "year":
            year = re.search(r"(19|20)\d{2}", value)
            if year:
                result["year"] = year.group(0)
        elif "doi" in key.lower():
            doi = re.search(r"10\.\d{4,9}/[-._;()/:A-Za-z0-9]+", value)
            if doi:
                result["doi"] = doi.group(0).rstrip(").,;")
        elif any(term in key.lower() for term in ["venue", "期刊", "会议", "发表信息"]):
            result["venue"] = value
            year = re.search(r"(19|20)\d{2}", value)
            if year and "year" not in result:
                result["year"] = year.group(0)
        elif "出版商" in key or "publisher" in key.lower():
            result["publisher"] = value
    return result


def follow_up_actions_from_note(note: str, item_id_value: str, existing: list[dict] | None = None) -> list[dict]:
    section = note_section(note, "后续建议") or note_section(note, "后续动作")
    if not section:
        return existing or []
    existing_by_text = {normalize_space(str(action.get("text", ""))): action for action in existing or []}
    actions: list[dict] = []
    for raw_line in section.splitlines():
        line = raw_line.strip()
        if not line.startswith(("-", "*")):
            continue
        _evidence, text = strip_evidence_prefix(line.lstrip("-* "))
        text = normalize_space(text)
        if not text:
            continue
        previous = existing_by_text.get(text, {})
        action_id = previous.get("id") or stable_id(item_id_value, text)[:10]
        actions.append(
            {
                "id": action_id,
                "text": text,
                "status": previous.get("status") or "open",
                "source": previous.get("source") or "note",
                "created_at": previous.get("created_at") or now_iso(),
                "completed_at": previous.get("completed_at") or "",
            }
        )
    return actions


def should_replace_with_note_metadata(item: dict, field: str, value: str) -> bool:
    if not value:
        return False
    current = normalize_space(str(item.get(field) or ""))
    if field == "title":
        weak_titles = {"", "general rights", "title title title title title"}
        return current.lower() in weak_titles or item.get("source") == "local_pdf" or metadata_status(item) == "needs_review"
    if field == "date":
        return current != value
    return False


def apply_note_metadata(item: dict, note: str) -> dict:
    extracted = metadata_from_note(note)
    if not extracted:
        return item
    metadata = item.setdefault("metadata", {})
    changed = False
    if extracted.get("title") and should_replace_with_note_metadata(item, "title", extracted["title"]):
        item["title"] = extracted["title"]
        changed = True
    if extracted.get("year"):
        if should_replace_with_note_metadata(item, "date", extracted["year"]):
            item["date"] = extracted["year"]
            changed = True
        if metadata.get("year") != extracted["year"]:
            metadata["year"] = extracted["year"]
            changed = True
    for key in ["authors", "venue", "publisher"]:
        if extracted.get(key) and metadata.get(key) != extracted[key]:
            metadata[key] = extracted[key]
            changed = True
    if extracted.get("doi") and (not metadata.get("doi") or metadata_status(item) == "needs_review"):
        metadata["doi"] = extracted["doi"]
        changed = True
    if extracted.get("doi_conflict") and metadata.get("doi"):
        metadata["conflicting_doi_note"] = extracted["doi_conflict"]
        metadata["conflicting_doi_value"] = metadata.pop("doi")
        if str(item.get("url", "")).startswith("https://doi.org/"):
            item["url"] = ""
        changed = True
    if changed:
        metadata["llm_metadata_extracted_at"] = now_iso()
        metadata["llm_metadata_needs_review"] = True
        item["metadata_status"] = "needs_review"
    return item


def apply_note_follow_up_actions(item: dict, note: str) -> dict:
    metadata = item.setdefault("metadata", {})
    existing = list(metadata.get("follow_up_actions") or [])
    actions = follow_up_actions_from_note(note, str(item.get("id") or ""), existing)
    if actions:
        metadata["follow_up_actions"] = actions
    return item


def apply_note_derived_fields(item: dict, note: str) -> dict:
    item = apply_note_metadata(item, note)
    item = apply_note_follow_up_actions(item, note)
    return item


def backfill_metadata_from_item_note(item: dict) -> dict:
    note_path_value = item.get("note_path")
    if not note_path_value:
        return item
    path = Path(str(note_path_value))
    if not path.exists():
        return item
    note = path.read_text(encoding="utf-8", errors="replace")
    return apply_note_derived_fields(item, note)


def item_year(item: dict) -> str:
    metadata = item.get("metadata") or {}
    return normalize_space(str(metadata.get("year") or item.get("date") or "year-unknown"))


def item_source_label(item: dict) -> str:
    metadata = item.get("metadata") or {}
    return normalize_space(
        str(
            metadata.get("venue")
            or metadata.get("publisher")
            or item.get("source")
            or item.get("source_type")
            or "source-unknown"
        )
    )


def item_human_annotation(item: dict) -> str:
    metadata = item.get("metadata") or {}
    for key in ["human_annotation_zh", "title_annotation_zh", "annotation_zh", "note_annotation_zh"]:
        value = normalize_space(str(metadata.get(key) or ""))
        if value:
            return value.strip("【】[]")
    return ""


def extract_human_annotation_from_name(value: str) -> str:
    match = re.match(r"^\s*【(?P<annotation>[^】]{1,80})】", value or "")
    if not match:
        return ""
    return normalize_space(match.group("annotation"))


def sync_human_annotation_from_pdf_name(item: dict, pdf_path: Path | None = None) -> dict:
    metadata = item.setdefault("metadata", {})
    candidates = []
    if pdf_path is not None:
        candidates.append(pdf_path.name)
    if metadata.get("pdf_source"):
        candidates.append(Path(str(metadata["pdf_source"])).name)
    if metadata.get("pdf_source_original_name"):
        candidates.append(str(metadata["pdf_source_original_name"]))
    for name in candidates:
        annotation = extract_human_annotation_from_name(name)
        if annotation:
            metadata["human_annotation_zh"] = annotation
            return item
    return item


def item_canonical_stem(item: dict) -> str:
    """Canonical local PDF/note stem: optional Chinese annotation, year, source, title, id."""
    annotation = item_human_annotation(item)
    parts = []
    if annotation:
        parts.append(f"【{annotation}】")
    parts.extend(
        [
            safe_filename_part(item_year(item), "year-unknown", 24),
            safe_filename_part(item_source_label(item), "source-unknown", 42),
            safe_filename_part(str(item.get("title") or ""), str(item.get("id") or "item"), 96),
            safe_filename_part(str(item.get("id") or item_id(title=str(item.get("title") or ""))), "id", 24),
        ]
    )
    return safe_filename("-".join(part for part in parts if part), fallback=str(item.get("id") or "item"), max_length=190)


def make_item(
    *,
    title: str,
    url: str,
    source: str,
    source_type: str,
    topic: str,
    date_value: str = "",
    abstract_or_snippet: str = "",
    pdf_url: str = "",
    score: int = 1,
    tags: list[str] | None = None,
    metadata: dict | None = None,
) -> dict:
    metadata = metadata or {}
    doi = str(metadata.get("doi", ""))
    created = now_iso()
    item = {
        "id": item_id(url, title, doi),
        "title": normalize_space(title),
        "url": url,
        "source": source,
        "source_type": source_type,
        "topic": topic,
        "date": date_value,
        "abstract_or_snippet": normalize_space(abstract_or_snippet),
        "pdf_url": pdf_url,
        "review_status": "new",
        "process_status": "unread",
        "metadata_status": "auto",
        "score": score,
        "tags": tags or [],
        "created_at": created,
        "updated_at": created,
        "metadata": metadata,
    }
    authority, reason = source_authority_score(item)
    item["authority_score"] = authority
    item["metadata"]["authority_reason"] = reason
    item = apply_document_access_metadata(item)
    return sync_status_fields(item)


def source_authority_score(item: dict) -> tuple[int, str]:
    """Heuristic source authority score, not a paper-quality judgment."""
    metadata = item.get("metadata") or {}
    source_type = str(item.get("source_type", "")).lower()
    text = " ".join(
        str(value)
        for value in [
            item.get("source", ""),
            item.get("url", ""),
            metadata.get("venue", ""),
            metadata.get("publisher", ""),
            metadata.get("doi", ""),
            metadata.get("provider", ""),
        ]
        if value
    ).lower()

    if source_type in {"standard", "policy"}:
        return 5, "standard/policy source type"
    if source_type in {"whitepaper", "report"}:
        if any(term in text for term in ["icao", "easa", "faa", "etsi", "3gpp", "itu", "ieee", "nist", "gov", "europa.eu"]):
            return 5, "recognized standards/government/technical report source"
        return 4, "whitepaper/report source type"
    if source_type == "industry":
        return 3, "industry/deployment signal; requires corroboration"
    if source_type == "news":
        if any(term in text for term in ["reuters", "associated press", "apnews", "bbc", "nature.com", "science.org"]):
            return 4, "recognized news/science outlet"
        return 2, "news source; requires corroboration"

    if any(term in text for term in ["ieee transactions", "acm transactions", "nature", "science", "cell"]):
        return 5, "top-tier journal family or transactions venue"
    if any(term in text for term in ["ieee", "acm", "usenix", "sigcomm", "mobicom", "infocom", "10.1109", "10.1145"]):
        return 4, "recognized society/conference source"
    if any(term in text for term in ["elsevier", "springer", "wiley", "taylor & francis", "sage"]):
        return 3, "established academic publisher; venue quality still needs review"
    if any(term in text for term in ["arxiv", "preprint", "mdpi", "hindawi"]):
        return 2, "preprint or mixed-confidence publisher; needs corroboration"
    return 1, "unknown or weakly characterized source"


def merge_item(existing: dict, incoming: dict) -> dict:
    existing = sync_status_fields(dict(existing))
    incoming = sync_status_fields(dict(incoming))
    merged = dict(existing)
    for key, value in incoming.items():
        if key in {"created_at", "review_status", "process_status"}:
            continue
        if value not in ("", None, [], {}):
            merged[key] = value
    if review_status(existing) != "new":
        merged["review_status"] = review_status(existing)
    else:
        merged["review_status"] = review_status(incoming)
    existing_process = process_status(existing)
    incoming_process = process_status(incoming)
    merged["process_status"] = existing_process if PROCESS_RANK[existing_process] >= PROCESS_RANK[incoming_process] else incoming_process
    existing_metadata_status = metadata_status(existing)
    incoming_metadata_status = metadata_status(incoming)
    merged["metadata_status"] = (
        existing_metadata_status
        if METADATA_RANK[existing_metadata_status] >= METADATA_RANK[incoming_metadata_status]
        else incoming_metadata_status
    )
    merged["created_at"] = existing.get("created_at") or incoming.get("created_at") or now_iso()
    merged["updated_at"] = now_iso()
    existing_tags = set(existing.get("tags") or [])
    incoming_tags = set(incoming.get("tags") or [])
    merged["tags"] = sorted(existing_tags | incoming_tags)
    metadata = dict(existing.get("metadata") or {})
    metadata.update(incoming.get("metadata") or {})
    merged["metadata"] = metadata
    authority, reason = source_authority_score(merged)
    merged["authority_score"] = max(int(merged.get("authority_score") or 0), authority)
    merged["metadata"].setdefault("authority_reason", reason)
    merged = apply_document_access_metadata(merged)
    return sync_status_fields(merged)


def upsert_items(incoming_items: Iterable[dict], path: Path = ITEMS_PATH) -> tuple[list[dict], list[dict]]:
    existing = load_items(path)
    by_id = {row["id"]: row for row in existing if row.get("id")}
    changed_or_new: list[dict] = []
    for item in incoming_items:
        item = sync_status_fields(item)
        authority, reason = source_authority_score(item)
        item["authority_score"] = authority
        item.setdefault("metadata", {})["authority_reason"] = reason
        item = apply_document_access_metadata(item)
        if not item.get("id"):
            item["id"] = item_id(item.get("url", ""), item.get("title", ""), str((item.get("metadata") or {}).get("doi", "")))
        if item["id"] in by_id:
            by_id[item["id"]] = merge_item(by_id[item["id"]], item)
        else:
            item = sync_status_fields(item)
            item.setdefault("created_at", now_iso())
            item["updated_at"] = now_iso()
            by_id[item["id"]] = item
        by_id[item["id"]] = apply_document_access_metadata(by_id[item["id"]])
        by_id[item["id"]] = sync_pdf_filename(by_id[item["id"]])
        by_id[item["id"]] = sync_note_filename(by_id[item["id"]])
        changed_or_new.append(by_id[item["id"]])
    rows = sorted(by_id.values(), key=lambda row: (row.get("topic", ""), row.get("date", ""), row.get("title", "")), reverse=True)
    write_jsonl(path, rows)
    return rows, changed_or_new


def update_item(item: dict, path: Path = ITEMS_PATH, apply_note_backfill: bool = True) -> None:
    rows = load_items(path)
    by_id = {row["id"]: row for row in rows if row.get("id")}
    item = sync_status_fields(item)
    item["updated_at"] = now_iso()
    authority, reason = source_authority_score(item)
    item["authority_score"] = authority
    item.setdefault("metadata", {})["authority_reason"] = reason
    item = apply_document_access_metadata(item)
    item = sync_human_annotation_from_pdf_name(item)
    if apply_note_backfill:
        item = backfill_metadata_from_item_note(item)
    item = sync_pdf_filename(item)
    item = sync_note_filename(item)
    by_id[item["id"]] = item
    write_jsonl(path, sorted(by_id.values(), key=lambda row: (row.get("topic", ""), row.get("date", ""), row.get("title", "")), reverse=True))


def find_existing_note_for_pdf(pdf_path: Path, items: list[dict] | None = None) -> dict | None:
    """Return an item with an existing note for this PDF path/hash, if known."""
    items = items if items is not None else load_items()
    fingerprint = ""
    try:
        fingerprint = sha256_file(pdf_path)
    except OSError:
        pass
    resolved = str(pdf_path)
    for item in items:
        note_path = item.get("note_path", "")
        if not note_path or not Path(note_path).exists():
            continue
        metadata = item.get("metadata") or {}
        if fingerprint and metadata.get("pdf_fingerprint") == fingerprint:
            return item
        if str(metadata.get("pdf_source", "")) == resolved:
            return item
    if fingerprint:
        for note_path in Path("notes/items").glob("*.md"):
            text = note_path.read_text(encoding="utf-8", errors="ignore")
            if fingerprint in text:
                return {"id": note_path.stem, "note_path": str(note_path), "metadata": {"pdf_fingerprint": fingerprint}}
    return None


def sync_existing_item_for_pdf(pdf_path: Path, item: dict) -> dict:
    """Update stored PDF path/name and note filename when a known PDF is seen again."""
    item_id_value = item.get("id")
    rows = load_items()
    current = next((row for row in rows if row.get("id") == item_id_value), None)
    if current is None:
        return item
    metadata = current.setdefault("metadata", {})
    metadata["pdf_source"] = str(pdf_path)
    metadata["pdf_fingerprint"] = sha256_file(pdf_path)
    current = sync_human_annotation_from_pdf_name(current, pdf_path)
    current = backfill_metadata_from_item_note(current)
    current = sync_pdf_filename(current, pdf_path)
    current = sync_note_filename(current)
    update_item(current)
    refreshed = next((row for row in load_items() if row.get("id") == item_id_value), current)
    return refreshed


def prepare_pdf_item(pdf_path: Path, topic: str, providers: list[str], lookup_limit: int) -> tuple[dict, float, str]:
    item, confidence, reason = lookup_pdf_item(pdf_path, topic, providers, lookup_limit)
    item["topic"] = topic
    item["source"] = item.get("source") or "local_pdf"
    item["source_type"] = "paper"
    item["review_status"] = "downloaded"
    item.setdefault("tags", [])
    if "local-pdf" not in item["tags"]:
        item["tags"].append("local-pdf")
    if topic == NEEDS_TOPIC_REVIEW and "needs-topic-review" not in item["tags"]:
        item["tags"].append("needs-topic-review")
    metadata = item.setdefault("metadata", {})
    metadata["pdf_source"] = str(pdf_path)
    metadata["pdf_fingerprint"] = sha256_file(pdf_path)
    metadata["metadata_match_confidence"] = round(confidence, 3)
    metadata["metadata_match_reason"] = reason
    item = sync_human_annotation_from_pdf_name(item, pdf_path)
    item["metadata_status"] = "needs_review" if confidence < 0.72 else metadata_status(item)
    return sync_status_fields(item), confidence, reason


def read_pdf_to_note(pdf_path: Path, item: dict, config: dict, timeout: int) -> tuple[dict, Path, str]:
    note, model = kimi_read_pdf(pdf_path, item, config, timeout)
    if not note.strip():
        raise RuntimeError("Kimi returned an empty note.")
    item = apply_note_derived_fields(item, note)
    item["process_status"] = "noted"
    item["updated_at"] = now_iso()
    metadata = item.setdefault("metadata", {})
    metadata["pdf_fingerprint"] = sha256_file(pdf_path)
    metadata["pdf_source"] = str(pdf_path)
    metadata["reading_status"] = "model_parsed_pdf"
    metadata["summary_status"] = "summarized"
    metadata.setdefault("visual_status", "not_parsed")
    item = sync_pdf_filename(item, pdf_path)
    pdf_path = Path(metadata.get("pdf_source", pdf_path))
    note_path = write_item_note(item, note, pdf_path, model, reading_status="model_parsed_pdf")
    item["note_path"] = str(note_path)
    item = sync_status_fields(item)
    all_items, _ = upsert_items([item])
    write_review_dashboard(all_items)
    return item, note_path, model


def fetch_json(url: str, timeout: int = 30) -> dict:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def fetch_text(url: str, timeout: int = 30) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read().decode("utf-8")


def text_contains_any(text: str, terms: list[str]) -> bool:
    lowered = text.lower()
    return any(term.lower() in lowered for term in terms if term)


def relevance_score(item: dict, required_terms: list[str], excluded_terms: list[str]) -> tuple[int, str]:
    text = " ".join(
        [
            item.get("title", ""),
            item.get("abstract_or_snippet", ""),
            " ".join(item.get("tags") or []),
            str((item.get("metadata") or {}).get("venue", "")),
            str((item.get("metadata") or {}).get("query", "")),
        ]
    )
    if excluded_terms and text_contains_any(text, excluded_terms):
        return 0, "matched exclude terms"
    if required_terms:
        matched = [term for term in required_terms if term.lower() in text.lower()]
        if not matched:
            return 0, "no required topic term matched"
        return min(5, len(matched)), "matched: " + ", ".join(matched[:4])
    return 1, "no topic gate configured"


def apply_topic_gate(items: Iterable[dict], required_terms: list[str], excluded_terms: list[str]) -> list[dict]:
    kept: list[dict] = []
    for item in items:
        score, reason = relevance_score(item, required_terms, excluded_terms)
        if score <= 0:
            continue
        item["score"] = max(int(item.get("score") or 1), score)
        metadata = item.setdefault("metadata", {})
        metadata["relevance_reason"] = reason
        kept.append(item)
    return kept


def search_openalex(query: str, topic: str, limit: int) -> list[dict]:
    params = urllib.parse.urlencode({"search": query, "per-page": limit})
    data = fetch_json(f"https://api.openalex.org/works?{params}")
    rows: list[dict] = []
    for item in data.get("results", []):
        authors = "; ".join(
            normalize_space(authorship.get("author", {}).get("display_name", ""))
            for authorship in item.get("authorships", [])
            if authorship.get("author", {}).get("display_name")
        )
        locations = item.get("locations") or []
        pdf_url = ""
        for location in locations:
            candidate_pdf = (location.get("pdf_url") or "").strip()
            if candidate_pdf:
                pdf_url = candidate_pdf
                break
        primary_location = item.get("primary_location") or {}
        primary_source = primary_location.get("source") or {}
        abstract = reconstruct_openalex_abstract(item.get("abstract_inverted_index") or {})
        rows.append(
            make_item(
                title=normalize_space(item.get("title", "")),
                url=item.get("id", ""),
                source="openalex",
                source_type="paper",
                topic=topic,
                date_value=str(item.get("publication_year") or ""),
                abstract_or_snippet=abstract,
                pdf_url=pdf_url,
                metadata={
                    "authors": authors,
                    "year": str(item.get("publication_year") or ""),
                    "venue": primary_source.get("display_name", ""),
                    "doi": (item.get("doi") or "").replace("https://doi.org/", ""),
                    "query": query,
                    "provider": "openalex",
                },
            )
        )
    return rows


def reconstruct_openalex_abstract(index: dict) -> str:
    if not index:
        return ""
    positions: dict[int, str] = {}
    for word, indexes in index.items():
        for position in indexes:
            positions[int(position)] = word
    return " ".join(positions[index] for index in sorted(positions))


def search_crossref(query: str, topic: str, limit: int) -> list[dict]:
    params = urllib.parse.urlencode({"query": query, "rows": limit})
    data = fetch_json(f"https://api.crossref.org/works?{params}")
    rows: list[dict] = []
    for item in data.get("message", {}).get("items", []):
        title = normalize_space(" ".join(item.get("title") or []))
        authors = "; ".join(
            normalize_space(" ".join(filter(None, [author.get("given", ""), author.get("family", "")])))
            for author in item.get("author", [])
        )
        year = ""
        date_parts = item.get("published-print", {}).get("date-parts") or item.get("published-online", {}).get("date-parts") or []
        if date_parts and date_parts[0]:
            year = str(date_parts[0][0])
        rows.append(
            make_item(
                title=title,
                url=item.get("URL", ""),
                source="crossref",
                source_type="paper",
                topic=topic,
                date_value=year,
                abstract_or_snippet=normalize_space(item.get("abstract", "")),
                metadata={
                    "authors": authors,
                    "year": year,
                    "venue": normalize_space("; ".join(item.get("container-title") or [])),
                    "publisher": item.get("publisher", ""),
                    "doi": item.get("DOI", ""),
                    "query": query,
                    "provider": "crossref",
                },
            )
        )
    return rows


def search_arxiv(query: str, topic: str, limit: int) -> list[dict]:
    search_query = urllib.parse.quote(f'all:"{query}"')
    text = fetch_text(f"https://export.arxiv.org/api/query?search_query={search_query}&start=0&max_results={limit}")
    root = ET.fromstring(text)
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    rows: list[dict] = []
    for entry in root.findall("atom:entry", ns):
        title = normalize_space(entry.findtext("atom:title", default="", namespaces=ns))
        authors = "; ".join(
            normalize_space(author.findtext("atom:name", default="", namespaces=ns))
            for author in entry.findall("atom:author", ns)
        )
        published = entry.findtext("atom:published", default="", namespaces=ns)
        entry_url = entry.findtext("atom:id", default="", namespaces=ns)
        pdf_url = ""
        for link in entry.findall("atom:link", ns):
            if link.attrib.get("title") == "pdf":
                pdf_url = link.attrib.get("href", "")
        rows.append(
            make_item(
                title=title,
                url=entry_url,
                source="arxiv",
                source_type="paper",
                topic=topic,
                date_value=published[:10] if published else "",
                abstract_or_snippet=normalize_space(entry.findtext("atom:summary", default="", namespaces=ns)),
                pdf_url=pdf_url,
                metadata={"authors": authors, "year": published[:4] if published else "", "venue": "arXiv", "query": query, "provider": "arxiv"},
            )
        )
    return rows


def search_semantic_scholar(query: str, topic: str, limit: int) -> list[dict]:
    fields = "title,abstract,authors,year,venue,externalIds,url,openAccessPdf,publicationDate"
    params = urllib.parse.urlencode({"query": query, "limit": limit, "fields": fields})
    headers = {"User-Agent": USER_AGENT}
    api_key = os.environ.get("SEMANTIC_SCHOLAR_API_KEY", "")
    if api_key:
        headers["x-api-key"] = api_key
    request = urllib.request.Request(f"https://api.semanticscholar.org/graph/v1/paper/search?{params}", headers=headers)
    with urllib.request.urlopen(request, timeout=30) as response:
        data = json.loads(response.read().decode("utf-8"))
    rows: list[dict] = []
    for item in data.get("data", []):
        authors = "; ".join(normalize_space(author.get("name", "")) for author in item.get("authors", []) if author.get("name"))
        external_ids = item.get("externalIds") or {}
        pdf = item.get("openAccessPdf") or {}
        pdf_url = pdf.get("url", "") if isinstance(pdf, dict) else ""
        rows.append(
            make_item(
                title=normalize_space(item.get("title", "")),
                url=item.get("url", ""),
                source="semantic_scholar",
                source_type="paper",
                topic=topic,
                date_value=item.get("publicationDate", "") or str(item.get("year") or ""),
                abstract_or_snippet=normalize_space(item.get("abstract", "")),
                pdf_url=pdf_url,
                metadata={
                    "authors": authors,
                    "year": str(item.get("year") or ""),
                    "venue": item.get("venue", ""),
                    "doi": external_ids.get("DOI", ""),
                    "query": query,
                    "provider": "semantic_scholar",
                },
            )
        )
    return rows


SEARCHERS = {
    "openalex": search_openalex,
    "crossref": search_crossref,
    "arxiv": search_arxiv,
    "semantic_scholar": search_semantic_scholar,
}


def load_context_source_config(path: Path = DEFAULT_CONTEXT_CONFIG) -> dict:
    if not path.exists():
        return {"rss": [], "urls": []}
    data = json.loads(path.read_text(encoding="utf-8"))
    return {
        "rss": list(data.get("rss") or data.get("rss_feeds") or []),
        "urls": list(data.get("urls") or data.get("manual_urls") or []),
    }


def normalize_source_type(value: str) -> str:
    value = (value or "news").strip().lower()
    allowed = {"news", "standard", "policy", "whitepaper", "report", "industry"}
    return value if value in allowed else "news"


def context_item_from_url(entry: dict) -> dict:
    url = normalize_space(str(entry.get("url") or ""))
    title = normalize_space(str(entry.get("title") or url or "Untitled context source"))
    topic = normalize_space(str(entry.get("topic") or NEEDS_TOPIC_REVIEW))
    source = normalize_space(str(entry.get("source") or entry.get("name") or urllib.parse.urlparse(url).netloc or "manual_context"))
    return make_item(
        title=title,
        url=url,
        source=source,
        source_type=normalize_source_type(str(entry.get("source_type") or "news")),
        topic=topic,
        date_value=normalize_space(str(entry.get("date") or "")),
        abstract_or_snippet=normalize_space(str(entry.get("snippet") or entry.get("abstract_or_snippet") or "")),
        score=int(entry.get("score") or 1),
        tags=list(entry.get("tags") or ["context-source"]),
        metadata={"provider": "context_sources", "collection_mode": "manual_url"},
    )


def rss_text(element: ET.Element, names: list[str], ns: dict[str, str]) -> str:
    for name in names:
        found = element.find(name, ns)
        if found is not None and found.text:
            return normalize_space(found.text)
    return ""


def rss_link(element: ET.Element, ns: dict[str, str]) -> str:
    link = rss_text(element, ["link", "atom:link"], ns)
    if link:
        return link
    found = element.find("atom:link", ns)
    if found is not None:
        return normalize_space(found.attrib.get("href", ""))
    return ""


def collect_rss_source(entry: dict, limit: int = 20) -> list[dict]:
    url = normalize_space(str(entry.get("url") or ""))
    if not url:
        return []
    topic = normalize_space(str(entry.get("topic") or NEEDS_TOPIC_REVIEW))
    source_name = normalize_space(str(entry.get("name") or urllib.parse.urlparse(url).netloc or "rss"))
    source_type = normalize_source_type(str(entry.get("source_type") or "news"))
    text = fetch_text(url, timeout=int(entry.get("timeout") or 30))
    root = ET.fromstring(text)
    ns = {"atom": "http://www.w3.org/2005/Atom", "dc": "http://purl.org/dc/elements/1.1/"}
    nodes = list(root.findall(".//item")) or list(root.findall("atom:entry", ns))
    rows: list[dict] = []
    for node in nodes[:limit]:
        title = rss_text(node, ["title", "atom:title"], ns)
        link = rss_link(node, ns)
        published = rss_text(node, ["pubDate", "published", "updated", "atom:published", "atom:updated", "dc:date"], ns)
        snippet = rss_text(node, ["description", "summary", "atom:summary"], ns)
        if not title and not link:
            continue
        rows.append(
            make_item(
                title=title or link,
                url=link,
                source=source_name,
                source_type=source_type,
                topic=topic,
                date_value=published[:10],
                abstract_or_snippet=html.unescape(re.sub(r"<[^>]+>", " ", snippet)),
                score=int(entry.get("score") or 1),
                tags=["context-source", "rss"],
                metadata={"provider": "context_sources", "collection_mode": "rss", "feed_url": url},
            )
        )
    return rows


def collect_context_sources(path: Path = DEFAULT_CONTEXT_CONFIG) -> list[dict]:
    config = load_context_source_config(path)
    rows = [context_item_from_url(entry) for entry in config["urls"] if entry.get("url")]
    for entry in config["rss"]:
        try:
            rows.extend(collect_rss_source(entry, limit=int(entry.get("limit") or 20)))
        except Exception as exc:
            print(f"Warning: context source failed for {entry.get('url', '')}: {exc}")
    return dedupe_items(rows)


def collect_topic_items(query_file: Path, providers: list[str], limit_per_keyword: int, max_keywords: int) -> list[dict]:
    query_data = parse_simple_query_yaml(query_file)
    topic = str(query_data["topic"])
    keywords = list(query_data.get("seed_keywords") or [])[:max_keywords]
    required_terms = list(query_data.get("required_terms_any") or [])
    excluded_terms = list(query_data.get("exclude_terms_any") or [])
    collected: list[dict] = []
    for keyword in keywords:
        for provider in providers:
            searcher = SEARCHERS.get(provider)
            if not searcher:
                continue
            try:
                collected.extend(searcher(keyword, topic, limit_per_keyword))
            except Exception as exc:
                print(f"Warning: collection failed for {provider} / {keyword}: {exc}")
    gated = apply_topic_gate(dedupe_items(collected), required_terms, excluded_terms)
    manual = [item for item in load_manual_items() if item.get("topic") == topic]
    return dedupe_items([*gated, *manual])


def dedupe_items(items: Iterable[dict]) -> list[dict]:
    seen: set[str] = set()
    unique: list[dict] = []
    for item in items:
        key = item.get("id") or item_id(item.get("url", ""), item.get("title", ""), str((item.get("metadata") or {}).get("doi", "")))
        if not key or key in seen:
            continue
        seen.add(key)
        item["id"] = key
        unique.append(item)
    return unique


def item_line(item: dict) -> str:
    title = item.get("title", "未命名条目")
    topic = item.get("topic", "unknown")
    topics = ", ".join(item_topics(item)) or str(topic)
    source = item.get("source", "")
    source_type = str(item.get("source_type") or "unknown")
    type_label = SOURCE_TYPE_LABELS.get(source_type, source_type)
    database = "论文数据库" if source_type == "paper" else "社会数据库" if source_type in CONTEXT_SOURCE_TYPES else "其他条目"
    score = item.get("score", "")
    authority = item.get("authority_score", "")
    access = ""
    if source_type in CONTEXT_SOURCE_TYPES:
        document_access, _reason = infer_document_access(item)
        access = f"；文档可用性：`{document_access}`"
    url = item.get("url", "")
    link = f" [{source}]({url})" if url else f" [{source}]"
    return (
        f"- **{title}**{link}；数据库：{database}；类型：{type_label} (`{source_type}`)；主主题：`{topic}`；topics：`{topics}`；相关性：{score}；权威性：{authority}；"
        f"review_status：`{review_status(item)}`；process_status：`{process_status(item)}`{access}；"
        f"metadata_status：`{metadata_status(item)}`"
    )


def topic_items(items: list[dict], topic: str) -> list[dict]:
    return [item for item in items if item_has_topic(item, topic)]


def noted_topic_items(items: list[dict], topic: str) -> list[dict]:
    return [
        item
        for item in topic_items(items, topic)
        if process_status(item) in {"noted", "used_in_synthesis"} and item.get("note_path")
    ]


def topic_workspace_path(topic: str) -> Path:
    return Path("topics") / slugify(topic) / "research_workspace.md"


def note_excerpt(item: dict, max_chars: int = 1800) -> str:
    path = Path(str(item.get("note_path") or ""))
    if not path.exists():
        return ""
    text = path.read_text(encoding="utf-8", errors="replace")
    text = re.sub(r"<!-- item_reading_metadata.*?-->", "", text, flags=re.DOTALL).strip()
    return text[:max_chars].strip()


def build_topic_workspace(topic: str, items: list[dict]) -> str:
    topic = slugify(topic)
    rows = topic_items(items, topic)
    noted = noted_topic_items(items, topic)
    context_rows = [item for item in rows if str(item.get("source_type") or "") in CONTEXT_SOURCE_TYPES]
    open_actions = [
        (item, action)
        for item in rows
        for action in (item.get("metadata") or {}).get("follow_up_actions") or []
        if action.get("status") == "open"
    ]
    lines = [
        f"# Topic Research Workspace: {topic}",
        "",
        f"- updated_at: {now_iso()}",
        f"- item_count: {len(rows)}",
        f"- noted_count: {len(noted)}",
        f"- context_signal_count: {len(context_rows)}",
        "",
        "> needs-review: 本页是人机共同维护的研究讨论草稿，不是最终研究结论、novelty claim 或路线卡。",
        "",
        "## 证据基底",
        "",
    ]
    if noted:
        for item in sorted(noted, key=lambda row: str(row.get("date") or ""), reverse=True):
            lines.append(item_line(item))
    else:
        lines.append("- needs-review: 该 topic 还没有已生成 note 的条目。")
    lines += ["", "## 社会数据库线索", ""]
    if context_rows:
        for item in sorted(context_rows, key=lambda row: (str((row.get("metadata") or {}).get("document_access") or ""), str(row.get("title") or ""))):
            lines.append(item_line(item))
    else:
        lines.append("- needs-review: 暂无标准、政策、报告、白皮书或产业线索。")
    lines += [
        "",
        "## 当前认识",
        "",
        "- paper-supported: needs-review",
        "- inferred: needs-review",
        "- unsupported: needs-review",
        "",
        "## 不确定信息",
        "",
    ]
    if open_actions:
        for item, action in open_actions[:30]:
            lines.append(f"- needs-review: **{item.get('title', '未命名条目')}**：{action.get('text', '')}")
    else:
        lines.append("- needs-review: 尚未从 note 中积累明确的后续核验项。")
    lines += [
        "",
        "## 可能论文 idea（问题形式）",
        "",
        "- proposal: needs-review",
        "",
        "## 推荐下一步阅读 / 检索",
        "",
        "- needs-review: 优先补齐直接 PDF/报告/标准原文，再讨论 gap。",
        "",
        "## 讨论记录",
        "",
        "- needs-review: 在 Streamlit Topic Workspace 中追加你和 LLM 的讨论结论；保留证据标签。",
        "",
    ]
    return "\n".join(lines)


def build_topic_workspace_prompt(topic: str, items: list[dict], workspace_text: str, max_notes: int = 8) -> str:
    topic = slugify(topic)
    noted = noted_topic_items(items, topic)[:max_notes]
    evidence_blocks = []
    for item in noted:
        evidence_blocks.append(
            "\n".join(
                [
                    f"### {item.get('title', '未命名条目')}",
                    f"- id: {item.get('id', '')}",
                    f"- source_type: {item.get('source_type', '')}",
                    f"- note_path: {item.get('note_path', '')}",
                    note_excerpt(item, max_chars=1600),
                ]
            )
        )
    evidence = "\n\n".join(evidence_blocks) or "暂无已生成 note 的材料。"
    return f"""请作为保守的低空研究情报助手，和我讨论 topic `{topic}` 的研究工作台草稿。

仓库规则：
- 不要自动生成最终研究方向、novelty claim、route card 或实现仓库建议。
- 所有判断必须标注 `paper-supported` / `inferred` / `proposal` / `unsupported` / `needs-review`。
- 不足三篇相关来源对比时，不要声称 research gap。
- 社会数据库的门户/目录页只能作为线索，不能当成已读证据。

当前 workspace 草稿：
```markdown
{workspace_text[:8000]}
```

可用 note 摘要：
```markdown
{evidence}
```

请输出可以直接粘贴回 `topics/{topic}/research_workspace.md` 的修改建议，重点包括：
1. 当前认识；
2. 不确定信息；
3. 可能论文 idea（必须写成问题形式）；
4. 推荐下一步阅读 / 检索。
"""


def write_topic_workspace(topic: str, items: list[dict], overwrite: bool = False) -> Path:
    path = topic_workspace_path(topic)
    path.parent.mkdir(parents=True, exist_ok=True)
    if overwrite or not path.exists():
        path.write_text(build_topic_workspace(topic, items), encoding="utf-8")
    return path


def write_review_dashboard(items: list[dict], path: Path = Path("outputs/review_dashboard.md")) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# 研究情报复核面板",
        "",
        "> 机器生成的轻量 review 面板。常规使用时优先看这里或 Streamlit，不需要直接维护内部文件。",
        "",
        "## 建议操作",
        "",
        "- 人工状态 `review_status`：`new` / `kept` / `downloaded` / `rejected`，由你在 GUI 中修改。",
        "- 流程状态 `process_status`：`unread` / `noted` / `used_in_synthesis`，通常由脚本自动维护；阅读深度看 metadata 中的 `reading_status` / `reading_mode`。",
        "- 元数据状态 `metadata_status`：`auto` / `needs_review` / `verified`，GUI 保存 metadata 后会标记为 `verified`。",
        "",
    ]
    needs_metadata = sorted([item for item in items if metadata_status(item) == "needs_review"], key=lambda row: int(row.get("score") or 0), reverse=True)
    lines += ["## 元数据待复核", ""]
    if needs_metadata:
        lines.extend(item_line(item) for item in needs_metadata[:50])
    else:
        lines.append("暂无。")
    lines.append("")
    open_actions = []
    for item in items:
        for action in (item.get("metadata") or {}).get("follow_up_actions") or []:
            if action.get("status") == "open":
                open_actions.append((item, action))
    lines += ["## 后续建议待处理", ""]
    if open_actions:
        for item, action in open_actions[:80]:
            lines.append(f"- `{action.get('id', '')}` **{item.get('title', '未命名条目')}**：{action.get('text', '')}")
    else:
        lines.append("暂无。")
    lines.append("")
    lines += ["## 按数据库视图", ""]
    database_groups = [
        ("论文数据库", [item for item in items if item.get("source_type") == "paper"]),
        ("社会数据库", [item for item in items if item.get("source_type") in CONTEXT_SOURCE_TYPES]),
    ]
    for title, rows in database_groups:
        lines += [f"### {title}", ""]
        if rows:
            sorted_rows = sorted(rows, key=lambda row: (str(row.get("source_type") or ""), int(row.get("score") or 0)), reverse=True)
            lines.extend(item_line(item) for item in sorted_rows[:50])
        else:
            lines.append("暂无。")
        lines.append("")
    context_items = [item for item in items if item.get("source_type") in CONTEXT_SOURCE_TYPES]
    lines += ["## 社会数据库文档可用性", ""]
    for access in DOCUMENT_ACCESS_OPTIONS:
        rows = [item for item in context_items if infer_document_access(item)[0] == access]
        lines += [f"### {access}", ""]
        if rows:
            lines.extend(item_line(item) for item in sorted(rows, key=lambda row: int(row.get("authority_score") or 0), reverse=True)[:30])
        else:
            lines.append("暂无。")
        lines.append("")
    lines += ["## 按人工状态", ""]
    for status in ["new", "kept", "downloaded", "rejected"]:
        rows = sorted([item for item in items if review_status(item) == status], key=lambda row: int(row.get("score") or 0), reverse=True)
        lines += [f"### {status}", ""]
        if rows:
            lines.extend(item_line(item) for item in rows[:30])
        else:
            lines.append("暂无。")
        lines.append("")
    lines += ["## 按流程状态", ""]
    for status in ["unread", "noted", "used_in_synthesis"]:
        rows = sorted([item for item in items if process_status(item) == status], key=lambda row: int(row.get("score") or 0), reverse=True)
        lines += [f"### {status}", ""]
        if rows:
            lines.extend(item_line(item) for item in rows[:30])
        else:
            lines.append("暂无。")
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def extract_pdf_dois(path: Path) -> set[str]:
    text = path.read_bytes()[:3_000_000].decode("latin-1", errors="ignore")
    dois = re.findall(r"10\.\d{4,9}/[-._;()/:A-Za-z0-9]+", text)
    return {doi.rstrip(").,;").lower() for doi in dois}


def extract_pdf_visible_text(path: Path, max_bytes: int = 2_000_000) -> str:
    data = path.read_bytes()[:max_bytes]
    decoded = data.decode("utf-8", errors="ignore")
    if len(decoded) < 500:
        decoded = data.decode("latin-1", errors="ignore")
    strings = re.findall(r"[A-Za-z][A-Za-z0-9,.:;()\- /]{8,}", decoded)
    return normalize_space(" ".join(strings[:1000]))


def extract_pdf_text_with_pypdf(path: Path, max_pages: int = 12, max_chars: int = 24000) -> str:
    for module_name in ["pypdf", "PyPDF2"]:
        try:
            module = __import__(module_name)
            reader = module.PdfReader(str(path))
            chunks: list[str] = []
            for page in reader.pages[:max_pages]:
                chunks.append(page.extract_text() or "")
            return normalize_space("\n".join(chunks))[:max_chars]
        except Exception:
            continue
    return extract_pdf_visible_text(path, max_bytes=3_000_000)[:max_chars]


def extract_pdf_title(path: Path) -> str:
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
                return normalize_space(str(title))
            if reader.pages:
                text = reader.pages[0].extract_text() or ""
                lines = [line.strip() for line in text.splitlines() if len(line.strip()) >= 8]
                if lines:
                    return normalize_space(lines[0])
        except Exception:
            continue
    text = path.read_bytes()[:1_000_000].decode("latin-1", errors="ignore")
    match = re.search(r"/Title\s*\((?P<title>[^)]{8,300})\)", text, flags=re.IGNORECASE | re.DOTALL)
    if match:
        return normalize_space(match.group("title").replace(r"\(", "(").replace(r"\)", ")"))
    return ""


def query_for_pdf(path: Path) -> tuple[str, str]:
    dois = sorted(extract_pdf_dois(path))
    if dois:
        return dois[0], "doi"
    title = extract_pdf_title(path)
    if title:
        return title, "pdf_title"
    visible_words = extract_pdf_visible_text(path).split()
    if len(visible_words) >= 6:
        return " ".join(visible_words[:24]), "pdf_text"
    return path.stem.replace("_", " ").replace("-", " "), "filename"


def lookup_pdf_item(path: Path, topic: str, providers: list[str], limit: int = 3) -> tuple[dict, float, str]:
    query, query_source = query_for_pdf(path)
    pdf_dois = extract_pdf_dois(path)
    extracted_title = extract_pdf_title(path) or path.stem
    for existing in load_items():
        metadata = existing.get("metadata") or {}
        doi = str(metadata.get("doi", "")).lower().strip()
        if doi and doi in pdf_dois:
            return existing, 1.0, "existing item doi"
        if existing.get("topic") == topic and title_similarity(extracted_title, existing.get("title", "")) >= 0.9:
            return existing, 0.9, "existing item title"

    candidates: list[dict] = []
    for provider in providers:
        searcher = SEARCHERS.get(provider)
        if not searcher:
            continue
        try:
            candidates.extend(searcher(query, topic, limit))
        except Exception:
            continue
    if not candidates:
        return make_item(title=extracted_title or path.stem, url="", source="local_pdf", source_type="paper", topic=topic, metadata={"query_source": query_source}), 0.0, "local filename fallback"
    for item in candidates:
        doi = str((item.get("metadata") or {}).get("doi", "")).lower().strip()
        if doi and doi in pdf_dois:
            return item, 1.0, "doi"
    best = max(candidates, key=lambda item: title_similarity(extracted_title, item.get("title", "")))
    score = title_similarity(extracted_title, best.get("title", ""))
    if score < 0.72:
        fallback = make_item(
            title=extracted_title or path.stem,
            url=f"https://doi.org/{sorted(pdf_dois)[0]}" if pdf_dois else "",
            source="local_pdf",
            source_type="paper",
            topic=topic,
            metadata={"doi": sorted(pdf_dois)[0] if pdf_dois else "", "query_source": query_source, "low_confidence_online_title": best.get("title", "")},
        )
        return fallback, score, f"low-confidence online match; kept local metadata from {query_source}"
    return best, score, f"title similarity from {query_source}"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


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


def provider_http_error(exc: urllib.error.HTTPError) -> RuntimeError:
    body = exc.read().decode("utf-8", errors="replace")
    detail = body.strip()
    if body:
        try:
            data = json.loads(body)
            error = data.get("error") if isinstance(data, dict) else None
            if isinstance(error, dict):
                detail = str(error.get("message") or error.get("code") or body).strip()
            elif isinstance(error, str):
                detail = error.strip()
        except json.JSONDecodeError:
            detail = body.strip()
    if len(detail) > 500:
        detail = detail[:500] + "..."
    detail = re.sub(r"\borg-[A-Za-z0-9_-]+", "org-[redacted]", detail)
    detail = re.sub(r"\bak-[A-Za-z0-9_-]+", "ak-[redacted]", detail)
    detail = re.sub(r"\bsk-[A-Za-z0-9_-]+", "sk-[redacted]", detail)
    message = f"HTTP {exc.code} {exc.reason}"
    if detail:
        message = f"{message}: {detail}"
    return RuntimeError(message)


def moonshot_request_json(url: str, api_key: str, payload: dict, timeout: int) -> dict:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raise provider_http_error(exc) from exc


def kimi_upload_file(pdf_path: Path, api_key: str, base_url: str, timeout: int) -> str:
    body, boundary = multipart_file_body(pdf_path, {"purpose": "file-extract"})
    request = urllib.request.Request(
        f"{base_url.rstrip('/')}/files",
        data=body,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raise provider_http_error(exc) from exc
    return str(data.get("id", ""))


def kimi_file_content(file_id: str, api_key: str, base_url: str, timeout: int) -> str:
    request = urllib.request.Request(f"{base_url.rstrip('/')}/files/{file_id}/content", headers={"Authorization": f"Bearer {api_key}"}, method="GET")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        raise provider_http_error(exc) from exc


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


def kimi_config(config: dict) -> tuple[str, str, str]:
    providers = (config.get("reading") or {}).get("providers") or {}
    kimi = providers.get("kimi") or {}
    api_key = os.environ.get(str(kimi.get("api_key_env") or "MOONSHOT_API_KEY"), "") or os.environ.get(str(kimi.get("fallback_api_key_env") or "KIMI_API_KEY"), "")
    base_url = os.environ.get(str(kimi.get("base_url_env") or "MOONSHOT_BASE_URL"), "") or os.environ.get(str(kimi.get("fallback_base_url_env") or "KIMI_BASE_URL"), "") or str(kimi.get("default_base_url") or "https://api.moonshot.cn/v1")
    model = os.environ.get(str(kimi.get("model_env") or "KIMI_READING_MODEL"), "") or str(kimi.get("default_model") or "kimi-k2.6")
    if not api_key:
        raise RuntimeError("MOONSHOT_API_KEY or KIMI_API_KEY missing")
    return api_key, base_url, model


def has_kimi_api_key(config: dict) -> bool:
    providers = (config.get("reading") or {}).get("providers") or {}
    kimi = providers.get("kimi") or {}
    api_key_env = str(kimi.get("api_key_env") or "MOONSHOT_API_KEY")
    fallback_api_key_env = str(kimi.get("fallback_api_key_env") or "KIMI_API_KEY")
    return bool(os.environ.get(api_key_env) or os.environ.get(fallback_api_key_env))


def build_chinese_reading_prompt(item: dict, fingerprint: str) -> str:
    metadata = json.dumps(item, ensure_ascii=False, indent=2)
    return f"""请阅读这篇论文 PDF，为低空研究情报助手生成一份中文阅读笔记。

严格规则：
- 不要编造 DOI、作者、年份、venue、数据集、标准编号或数值结果。
- 区分 `paper-supported`、`inferred`、`proposal`、`unsupported`。
- 只总结论文内容，不要生成最终研究结论、创新性判断、实施仓库建议或路线卡。
- `full-text parsed` 只表示模型处理过 PDF，不等于人工审阅。
- 如果信息不足，写 `unsupported: PDF 中未提供`。

已知 metadata：
```json
{metadata}
```

PDF fingerprint: {fingerprint}

请输出 Markdown，章节必须如下：
# 条目摘要
## 元数据
## 收录原因
## 核心内容
## 方法 / 系统 / 政策细节
## 关键证据
## 图表与可视证据
## 局限性
## 与低空研究的关联
## 可复用参数 / 模型 / 基线
## 后续建议
## 可靠性说明

每个实质性 bullet 必须以 `paper-supported:`、`inferred:`、`proposal:` 或 `unsupported:` 开头。后续建议只能是继续阅读、核验参数、补充 metadata、查找政策/标准/产业背景等审查任务。
"""


def kimi_read_pdf(pdf_path: Path, item: dict, config: dict, timeout: int = 300) -> tuple[str, str]:
    api_key, base_url, model = kimi_config(config)
    file_id = kimi_upload_file(pdf_path, api_key, base_url, timeout)
    if not file_id:
        raise RuntimeError("Kimi file upload did not return a file id.")
    file_content = kimi_file_content(file_id, api_key, base_url, timeout)
    fingerprint = sha256_file(pdf_path)
    prompt = build_chinese_reading_prompt(item, fingerprint)
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "你是严谨的中英文技术文献阅读助手。请遵守证据标签规则，只做保守摘要，不做最终研究判断。"},
            {"role": "system", "content": file_content},
            {"role": "user", "content": prompt},
        ],
    }
    data = moonshot_request_json(f"{base_url.rstrip('/')}/chat/completions", api_key, payload, timeout)
    return extract_chat_completion_text(data), model


def read_pdf_metadata_only(pdf_path: Path, item: dict) -> tuple[dict, Path | None, str]:
    metadata = item.setdefault("metadata", {})
    item = sync_human_annotation_from_pdf_name(item, pdf_path)
    metadata["pdf_fingerprint"] = sha256_file(pdf_path)
    metadata["pdf_source"] = str(pdf_path)
    metadata["reading_status"] = "metadata_only"
    metadata["summary_status"] = "metadata-only"
    metadata["visual_status"] = "not_parsed"
    metadata["reading_mode"] = "metadata-only"
    item["process_status"] = process_status(item)
    item = sync_pdf_filename(item, pdf_path)
    item = sync_status_fields(item)
    all_items, changed = upsert_items([item])
    write_review_dashboard(all_items)
    return changed[0], None, "metadata-only"


def pdf_text_cache_path(item: dict) -> Path:
    return PDF_TEXT_CACHE_DIR / f"{item_canonical_stem(item)}.txt"


def write_pdf_text_cache(item: dict, extracted_text: str) -> Path:
    path = pdf_text_cache_path(item)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(extracted_text, encoding="utf-8")
    return path


def text_page_hints(extracted_text: str, max_hints: int = 5, max_chars: int = 260) -> list[str]:
    chunks = [normalize_space(chunk) for chunk in re.split(r"\n\s*\n|(?<=\.)\s+", extracted_text) if normalize_space(chunk)]
    hints: list[str] = []
    for chunk in chunks:
        if len(chunk) < 80:
            continue
        hints.append(chunk[:max_chars].rstrip())
        if len(hints) >= max_hints:
            break
    return hints


def build_text_draft_note(pdf_path: Path, item: dict, extracted_text: str, cache_path: Path) -> str:
    metadata = item.get("metadata") or {}
    hints = text_page_hints(extracted_text)
    hint_lines = "\n".join(f"- abstract only: {hint}" for hint in hints) if hints else "- needs-review: pypdf 未抽取到可用短片段。"
    return f"""# 条目摘要

## 元数据
- 标题：{item.get("title", "")}
- 年份：{metadata.get("year") or item.get("date") or "metadata only"}
- 来源：{metadata.get("venue") or metadata.get("publisher") or item.get("source", "")}
- DOI：{metadata.get("doi") or "metadata only"}
- 状态：text_extracted；text-draft；not_parsed；needs-review
- 本地原文缓存：`{cache_path.as_posix()}`（`.local/` 下文件不提交）

## 收录原因
- inferred: 该条目由本地 PDF 读取流程导入，topic 为 `{item.get("topic", "")}`；需要人工复核相关性。

## 核心内容
- unsupported: 本草稿只使用 pypdf 提取文本，尚未调用 Kimi/LLM 进行结构化精读。

## 方法 / 系统 / 政策细节
- needs-review: 请基于 PDF 原文人工或使用 Kimi 模式补充。

## 关键证据
- needs-review: 不在笔记中保存长篇 PDF 抽取文本，避免版权与仓库存储风险。原始抽取文本仅保存在本地忽略缓存。
{hint_lines}

## 局限性
- unsupported: 短片段只用于定位阅读入口，不等于人工确认事实。
- unsupported: 本草稿不支持研究 gap、创新性或最终方向判断。

## 与低空研究的关联
- inferred: 需要人工确认该 PDF 是否支撑低空通信或自主航空系统研究。

## 可复用参数 / 模型 / 基线
- needs-review: 尚未结构化提取。

## 后续建议
- proposal: 若该条目重要，使用 GUI 的复核条目读取按钮，或运行 `python scripts/read_item.py "{pdf_path}" --mode kimi` 生成精读笔记；默认会自动推断 topic，无法确认时进入 Topic 审核。

## 可靠性说明
- text_extracted
- visual_status: not_parsed
- machine-generated
- needs-review
"""


def read_pdf_to_text_draft(pdf_path: Path, item: dict) -> tuple[dict, Path, str]:
    text = extract_pdf_text_with_pypdf(pdf_path)
    if not text.strip():
        raise RuntimeError("Could not extract readable PDF text with pypdf/PyPDF2.")
    item["process_status"] = "noted"
    item["updated_at"] = now_iso()
    metadata = item.setdefault("metadata", {})
    item = sync_human_annotation_from_pdf_name(item, pdf_path)
    metadata["pdf_fingerprint"] = sha256_file(pdf_path)
    metadata["pdf_source"] = str(pdf_path)
    metadata["reading_status"] = "text_extracted"
    metadata["summary_status"] = "text-draft"
    metadata["visual_status"] = "not_parsed"
    metadata["reading_mode"] = "text-draft"
    item = sync_pdf_filename(item, pdf_path)
    pdf_path = Path(metadata.get("pdf_source", pdf_path))
    cache_path = write_pdf_text_cache(item, text)
    metadata["pdf_text_cache"] = cache_path.as_posix()
    note = build_text_draft_note(pdf_path, item, text, cache_path)
    note_path = write_item_note(item, note, pdf_path, "text-draft", provider="pypdf", reading_status="text_extracted")
    item["note_path"] = str(note_path)
    item = sync_status_fields(item)
    all_items, _ = upsert_items([item])
    write_review_dashboard(all_items)
    return item, note_path, "text-draft"


def legacy_note_path_for_item(item: dict) -> Path:
    return Path("notes/items") / f"{item['id']}.md"


def note_path_for_item(item: dict) -> Path:
    preferred = preferred_note_path_for_item(item)
    legacy = legacy_note_path_for_item(item)
    if preferred.exists() or not legacy.exists():
        return preferred
    return legacy


def preferred_note_path_for_item(item: dict) -> Path:
    return Path("notes/items") / f"{item_canonical_stem(item)}.md"


def preferred_pdf_path_for_item(item: dict, pdf_path: Path) -> Path:
    return pdf_path.with_name(f"{item_canonical_stem(item)}{pdf_path.suffix.lower() or '.pdf'}")


def unique_path(path: Path, current: Path | None = None) -> Path:
    if current is not None:
        try:
            if path.resolve() == current.resolve():
                return path
        except OSError:
            if path == current:
                return path
    if not path.exists():
        return path
    for index in range(2, 1000):
        candidate = path.with_name(f"{path.stem}-{index}{path.suffix}")
        if not candidate.exists():
            return candidate
    raise RuntimeError(f"Could not find an available path for {path}")


def sync_pdf_filename(item: dict, pdf_path: Path | None = None) -> dict:
    metadata = item.setdefault("metadata", {})
    source_value = str(pdf_path or metadata.get("pdf_source") or "")
    if not source_value:
        return item
    current = Path(source_value)
    if not current.exists() or current.suffix.lower() != ".pdf":
        return item
    item = sync_human_annotation_from_pdf_name(item, current)
    preferred = unique_path(preferred_pdf_path_for_item(item, current), current=current)
    if current != preferred:
        preferred.parent.mkdir(parents=True, exist_ok=True)
        current.rename(preferred)
        metadata["pdf_source_original_name"] = current.name
        metadata["pdf_renamed_at"] = now_iso()
    metadata["pdf_source"] = str(preferred)
    return item


def sync_note_filename(item: dict) -> dict:
    note_path_value = item.get("note_path")
    if not note_path_value:
        return item
    current = Path(note_path_value)
    if not current.exists():
        return item
    preferred = preferred_note_path_for_item(item)
    if current == preferred:
        return item
    preferred.parent.mkdir(parents=True, exist_ok=True)
    preferred = unique_path(preferred, current=current)
    current.rename(preferred)
    item["note_path"] = str(preferred)
    return item


def write_item_note(item: dict, note: str, pdf_path: Path, model: str, provider: str = "kimi", reading_status: str = "model_parsed_pdf") -> Path:
    path = preferred_note_path_for_item(item)
    path.parent.mkdir(parents=True, exist_ok=True)
    provenance = [
        "",
        "<!-- item_reading_metadata",
        json.dumps(
            {
                "item_id": item["id"],
                "reading_model": model,
                "reading_provider": provider,
                "read_at": now_iso(),
                "pdf_fingerprint": sha256_file(pdf_path),
                "pdf_source": str(pdf_path),
                "reading_status": reading_status,
                "human_reviewed": False,
            },
            ensure_ascii=False,
            indent=2,
        ),
        "-->",
        "",
    ]
    path.write_text(note.rstrip() + "\n" + "\n".join(provenance), encoding="utf-8")
    return path
