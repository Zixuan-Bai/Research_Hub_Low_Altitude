"""Local Streamlit review surface for data/items.jsonl."""

from __future__ import annotations

import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

import research_hub_lib as hub


REVIEW_STATUS_OPTIONS = ["new", "kept", "downloaded", "rejected"]
PROCESS_STATUS_OPTIONS = ["unread", "noted", "used_in_synthesis"]
SOURCE_TYPE_OPTIONS = ["paper", "news", "standard", "policy", "whitepaper", "report", "industry", "dataset"]
SOURCE_TYPE_LABELS = {
    "paper": "论文",
    "standard": "标准",
    "policy": "政策",
    "whitepaper": "白皮书",
    "report": "报告",
    "industry": "产业信号",
    "news": "新闻/动态",
    "dataset": "数据集",
}
CONTEXT_SOURCE_TYPES = {"news", "standard", "policy", "whitepaper", "report", "industry"}
METADATA_STATUS_LABELS = {
    "auto": "自动元数据",
    "needs_review": "元数据待复核",
    "verified": "元数据已人工确认",
}
STATUS_LABELS = {
    "new": "新条目",
    "kept": "保留",
    "downloaded": "已下载",
    "rejected": "已拒绝",
    "unread": "未读",
    "noted": "已生成 note",
    "used_in_synthesis": "已进入主题综合",
}
ACTION_LABELS = {"kept": "Keep", "rejected": "Reject", "downloaded": "Downloaded"}
DOCUMENT_ACCESS_LABELS = hub.DOCUMENT_ACCESS_OPTIONS


def source_type_label(source_type: str) -> str:
    return SOURCE_TYPE_LABELS.get(source_type, source_type or "unknown")


def database_label(item: dict) -> str:
    source_type = str(item.get("source_type") or "")
    if source_type == "paper":
        return "论文数据库"
    if source_type in CONTEXT_SOURCE_TYPES:
        return "社会数据库"
    return "其他条目"


def require_streamlit():
    try:
        import streamlit as st
    except ImportError as exc:
        raise SystemExit(
            "Streamlit is not installed. Install it locally with `pip install -r requirements.txt`, "
            "then run `python -m streamlit run scripts/review_app.py`."
        ) from exc
    return st


def rerun(st) -> None:
    if hasattr(st, "rerun"):
        st.rerun()
    else:
        st.experimental_rerun()


def run_script(args: list[str], timeout: int = 1800) -> tuple[int, str]:
    completed = subprocess.run(
        [sys.executable, *args],
        cwd=Path.cwd(),
        text=True,
        capture_output=True,
        timeout=timeout,
    )
    output = "\n".join(part for part in [completed.stdout, completed.stderr] if part.strip())
    return completed.returncode, output


def local_pdf_path(item: dict) -> Path | None:
    metadata = item.get("metadata") or {}
    value = metadata.get("pdf_source")
    if not value:
        return None
    path = Path(str(value))
    return path if path.exists() and path.suffix.lower() == ".pdf" else None


def bind_pdf_to_item(item_id: str, pdf_path_value: str) -> bool:
    pdf_path = Path(pdf_path_value)
    if not pdf_path.exists() or pdf_path.suffix.lower() != ".pdf":
        return False
    for item in hub.load_items():
        if item.get("id") != item_id:
            continue
        metadata = item.setdefault("metadata", {})
        metadata["pdf_source"] = str(pdf_path)
        metadata["pdf_sha256"] = hub.sha256_file(pdf_path)
        metadata["pdf_fingerprint"] = metadata["pdf_sha256"]
        metadata["pdf_inbox_status"] = "registered"
        tags = set(item.get("tags") or [])
        tags.add("local-pdf")
        item["tags"] = sorted(tags)
        hub.update_item(item, apply_note_backfill=False)
        hub.write_review_dashboard(hub.load_items())
        return True
    return False


def read_item_from_gui(item: dict, mode: str, force: bool = False, upgrade: bool = False) -> tuple[int, str]:
    pdf_path = local_pdf_path(item)
    if not pdf_path:
        return 1, "没有找到本地 PDF。请先把 PDF 放入 literature/inbox/papers，或在 metadata 中补充 pdf_source。"
    topic = str(item.get("topic") or "auto")
    if topic == hub.NEEDS_TOPIC_REVIEW:
        topic = "auto"
    args = ["scripts/read_item.py", str(pdf_path), "--topic", topic, "--mode", mode]
    if force:
        args.append("--force")
    if upgrade:
        args.append("--upgrade")
    return run_script(args, timeout=7200)


def update_review_status(item_id: str, status: str) -> None:
    for item in hub.load_items():
        if item.get("id") == item_id:
            item["review_status"] = status
            item.setdefault("metadata", {})["human_decision_at"] = hub.now_iso()
            hub.update_item(item, apply_note_backfill=False)
            hub.write_review_dashboard(hub.load_items())
            return


def update_process_status(item_id: str, status: str) -> None:
    for item in hub.load_items():
        if item.get("id") == item_id:
            item["process_status"] = status
            item.setdefault("metadata", {})["manual_process_status_updated_at"] = hub.now_iso()
            hub.update_item(item, apply_note_backfill=False)
            hub.write_review_dashboard(hub.load_items())
            return


def update_topic(item_id: str, topic: str) -> None:
    topic = hub.slugify(topic)
    for item in hub.load_items():
        if item.get("id") == item_id:
            query_path, created = hub.ensure_topic_exists(topic, title_hint=str(item.get("title") or ""))
            item["topic"] = topic
            item["topics"] = hub.normalize_topic_list(item.get("topics") or [], topic)
            tags = [tag for tag in item.get("tags", []) if tag != "needs-topic-review"]
            item["tags"] = tags
            metadata = item.setdefault("metadata", {})
            metadata["topic_reviewed_at"] = hub.now_iso()
            metadata["topic_query_path"] = query_path.as_posix()
            if created:
                metadata["topic_created_from_gui"] = True
            hub.update_item(item, apply_note_backfill=False)
            hub.write_review_dashboard(hub.load_items())
            return


def register_topic(topic: str) -> tuple[Path, bool]:
    return hub.ensure_topic_exists(topic)


def topic_input_value(item: dict) -> str:
    return "\n".join(hub.item_topics(item))


def update_item_topics(item_id: str, primary_topic: str, topics_text: str) -> None:
    primary = hub.slugify(primary_topic)
    topics = hub.normalize_topic_list([topics_text], primary)
    if not primary and topics:
        primary = topics[0]
    if not primary:
        primary = hub.NEEDS_TOPIC_REVIEW
        topics = []

    query_paths: list[str] = []
    for topic in topics:
        query_path, _created = hub.ensure_topic_exists(topic)
        query_paths.append(query_path.as_posix())

    for item in hub.load_items():
        if item.get("id") != item_id:
            continue
        item["topic"] = primary
        item["topics"] = topics
        tags = [tag for tag in item.get("tags", []) if tag != "needs-topic-review"]
        if primary == hub.NEEDS_TOPIC_REVIEW and "needs-topic-review" not in tags:
            tags.append("needs-topic-review")
        item["tags"] = tags
        metadata = item.setdefault("metadata", {})
        metadata["topics_reviewed_at"] = hub.now_iso()
        metadata["topic_query_paths"] = query_paths
        hub.update_item(item, apply_note_backfill=False)
        hub.write_review_dashboard(hub.load_items())
        return


def update_metadata(item_id: str, top_level: dict, metadata_updates: dict) -> None:
    for item in hub.load_items():
        if item.get("id") != item_id:
            continue
        for key, value in top_level.items():
            item[key] = value.strip() if isinstance(value, str) else value
        metadata = item.setdefault("metadata", {})
        for key, value in metadata_updates.items():
            value = value.strip() if isinstance(value, str) else value
            if value in ("", None):
                metadata.pop(key, None)
            else:
                metadata[key] = value
        item["metadata_status"] = "verified"
        metadata["manual_metadata_updated_at"] = hub.now_iso()
        hub.update_item(item, apply_note_backfill=False)
        hub.write_review_dashboard(hub.load_items())
        return


def update_document_access(item_id: str, access: str) -> None:
    for item in hub.load_items():
        if item.get("id") != item_id:
            continue
        metadata = item.setdefault("metadata", {})
        metadata["document_access"] = access
        metadata["document_access_reviewed_at"] = hub.now_iso()
        metadata["document_access_source"] = "manual"
        hub.update_item(item, apply_note_backfill=False)
        hub.write_review_dashboard(hub.load_items())
        return


def item_matches(item: dict, review_filter: str, process_filter: str, metadata_filter: str, topic: str, source_type: str, query: str) -> bool:
    if review_filter != "all" and hub.review_status(item) != review_filter:
        return False
    if process_filter != "all" and hub.process_status(item) != process_filter:
        return False
    if metadata_filter != "all" and hub.metadata_status(item) != metadata_filter:
        return False
    if topic != "all" and not hub.item_has_topic(item, topic):
        return False
    if source_type != "all" and item.get("source_type") != source_type:
        return False
    if not query:
        return True
    haystack = " ".join(
        [
            str(item.get("title", "")),
            str(item.get("abstract_or_snippet", "")),
            str(item.get("source", "")),
            str(item.get("topic", "")),
            " ".join(hub.item_topics(item)),
        ]
    ).lower()
    return query.lower() in haystack


def compact_authors(authors: str, max_authors: int = 4) -> str:
    parts = [part.strip() for part in authors.split(";") if part.strip()]
    if not parts:
        return authors
    if len(parts) > max_authors:
        return "; ".join(parts[:max_authors]) + f"; et al. ({len(parts)} authors)"
    return "; ".join(parts)


def bibliographic_line(item: dict) -> str:
    metadata = item.get("metadata") or {}
    pieces = [
        str(metadata.get("year") or item.get("date") or "year unknown"),
        str(metadata.get("venue") or metadata.get("publisher") or item.get("source") or "source unknown"),
    ]
    authors = compact_authors(str(metadata.get("authors") or ""))
    if authors:
        pieces.append(authors)
    doi = metadata.get("doi")
    if doi:
        pieces.append(f"DOI: {doi}")
    return " | ".join(piece for piece in pieces if piece)


def render_note_preview(st, note_path_value: str) -> None:
    note_path = Path(note_path_value)
    if not note_path.exists():
        st.caption(f"note_path 已记录但文件不存在：`{note_path_value}`")
        return
    text = note_path.read_text(encoding="utf-8", errors="replace")
    with st.expander("Item Note 预览", expanded=False):
        st.markdown(text[:6000] + ("\n\n...（已截断）" if len(text) > 6000 else ""))


def has_existing_note(item: dict) -> bool:
    note_path_value = item.get("note_path")
    return bool(note_path_value and Path(str(note_path_value)).exists())


def possible_matching_pdfs(item: dict, limit: int = 8) -> list[Path]:
    title_tokens = hub.token_set(str(item.get("title") or ""))
    rows: list[tuple[float, Path]] = []
    for pdf_path in hub.discover_pdf_inbox():
        score = hub.title_similarity(str(item.get("title") or ""), pdf_path.stem)
        if title_tokens and title_tokens & hub.token_set(pdf_path.stem):
            score = max(score, 0.4)
        rows.append((score, pdf_path))
    return [path for score, path in sorted(rows, reverse=True)[:limit] if score >= 0.15]


def render_pdf_actions(st, item: dict, item_key: str, title: str) -> None:
    pdf_path = local_pdf_path(item)
    metadata = item.get("metadata") or {}
    reading_mode = str(metadata.get("reading_mode") or "")
    note_exists = has_existing_note(item)
    with st.expander("本地 PDF / note 操作", expanded=False):
        if pdf_path:
            st.caption(f"PDF: `{pdf_path}`")
        else:
            st.caption("未绑定本地 PDF。可以手动输入路径，或从 inbox 候选 PDF 中选择。")
            candidates = possible_matching_pdfs(item)
            candidate_labels = [""] + [str(path) for path in candidates]
            selected = st.selectbox("可能匹配的 inbox PDF", candidate_labels, key=f"{item_key}:pdf-candidate")
            manual = st.text_input("本地 PDF 路径", value=selected, key=f"{item_key}:pdf-bind-path")
            if st.button("绑定 PDF", key=f"{item_key}:pdf-bind", disabled=not manual.strip()):
                if bind_pdf_to_item(item["id"], manual.strip()):
                    st.session_state["last_action_message"] = f"已绑定 PDF：{title}"
                    rerun(st)
                else:
                    st.error("绑定失败：路径不存在或不是 PDF。")
            return

        if not note_exists:
            read_mode = st.selectbox("读取模式", ["metadata-only", "text-draft", "kimi"], key=f"{item_key}:read-mode")
            if st.button("生成 note / 同步 metadata", key=f"{item_key}:read-now"):
                with st.spinner("正在读取 PDF 并更新 item store..."):
                    code, output = read_item_from_gui(item, read_mode)
                st.code(output or "(no output)", language="text")
                if code == 0:
                    st.session_state["last_action_message"] = f"已处理：{title}"
                    rerun(st)
                else:
                    st.error(f"读取失败，退出码 {code}")
            return

        st.caption(f"已有 note，reading_mode=`{reading_mode or 'unknown'}`。")
        if reading_mode == "text-draft":
            columns = st.columns(2)
            if columns[0].button("升级为 Kimi note", key=f"{item_key}:upgrade-kimi"):
                with st.spinner("正在升级为 Kimi note..."):
                    code, output = read_item_from_gui(item, "kimi", upgrade=True)
                st.code(output or "(no output)", language="text")
                if code == 0:
                    st.session_state["last_action_message"] = f"已升级：{title}"
                    rerun(st)
                else:
                    st.error(f"升级失败，退出码 {code}")
            confirm_text = columns[1].checkbox("确认覆盖 text-draft", key=f"{item_key}:force-text-confirm")
            if columns[1].button("重新生成 text-draft", key=f"{item_key}:force-text", disabled=not confirm_text):
                with st.spinner("正在重新生成 text-draft..."):
                    code, output = read_item_from_gui(item, "text-draft", force=True)
                st.code(output or "(no output)", language="text")
                if code == 0:
                    rerun(st)
                else:
                    st.error(f"重读失败，退出码 {code}")
        else:
            confirm = st.checkbox("确认覆盖已有 note", key=f"{item_key}:force-confirm")
            mode = st.selectbox("重读模式", ["kimi", "text-draft", "metadata-only"], key=f"{item_key}:force-mode")
            if st.button("重读 / 覆盖 note", key=f"{item_key}:force-read", disabled=not confirm):
                with st.spinner("正在重读 PDF..."):
                    code, output = read_item_from_gui(item, mode, force=True)
                st.code(output or "(no output)", language="text")
                if code == 0:
                    st.session_state["last_action_message"] = f"已重读：{title}"
                    rerun(st)
                else:
                    st.error(f"重读失败，退出码 {code}")


def review_completed(item: dict) -> bool:
    source_type = str(item.get("source_type") or "")
    if source_type in CONTEXT_SOURCE_TYPES and hub.review_status(item) == "kept":
        access, _reason = hub.infer_document_access(item)
        if access in hub.REFERENCE_ONLY_DOCUMENT_ACCESS:
            return True
    return hub.metadata_status(item) == "verified" and has_existing_note(item)


def topic_category(item: dict) -> str:
    topic = str(item.get("topic") or hub.NEEDS_TOPIC_REVIEW)
    return "未划分 topic" if topic == hub.NEEDS_TOPIC_REVIEW else topic


def configured_topic_slugs() -> set[str]:
    return set(hub.topic_key_to_slug(hub.load_config()).values())


def render_topic_query_review_notices(st, items: list[dict]) -> None:
    config = hub.load_config()
    item_topics = sorted({topic for item in items for topic in hub.item_topics(item)})
    configured = set(hub.topic_key_to_slug(config).values())
    missing = [topic for topic in item_topics if topic not in configured]
    needs_review = [row for row in hub.topics_needing_query_review(config) if row["topic"] in item_topics]

    if not missing and not needs_review:
        return

    with st.expander(f"Topic 配置待维护 ({len(missing) + len(needs_review)})", expanded=True):
        if missing:
            st.warning("这些 topic 已出现在条目中，但还没有注册到 `configs/pipeline.json`。注册后会生成 query 模板，后续收集和 topic 选择才会把它当成正式 topic。")
            for topic in missing:
                columns = st.columns([2, 4, 1])
                columns[0].code(topic, language="text")
                columns[1].caption("缺少 `literature/queries/<topic>.yaml` 或 config 映射。")
                if columns[2].button("注册", key=f"register-topic:{topic}"):
                    query_path, created = register_topic(topic)
                    st.session_state["last_action_message"] = f"topic 已注册：{topic} -> {query_path.as_posix()} ({'created' if created else 'exists'})"
                    rerun(st)

        if needs_review:
            st.info("这些 topic 的 query 信息量偏少。你可以先人工补关键词；补完后，把下面 prompt 交给 Codex，让它按现有 topic 的信息量继续补齐。")
            for row in needs_review:
                st.markdown(f"**{row['topic']}**：`{row['query_path'].as_posix()}`；seed={row['seed_keyword_count']}，required={row['required_term_count']}")
                st.text_area(
                    "给 Codex 的补全 prompt",
                    value=row["prompt"],
                    height=260,
                    key=f"topic-prompt:{row['topic']}",
                )


def render_topic_editor(st, item: dict, item_key: str) -> None:
    primary_topic = str(item.get("topic") or "")
    current_topics = topic_input_value(item)
    known_topics = sorted(configured_topic_slugs() | {topic for row in hub.load_items() for topic in hub.item_topics(row)})
    st.markdown("**Topic 标签**")
    columns = st.columns([1.2, 2.4])
    edited_primary = columns[0].text_input("主 topic", value=primary_topic, key=f"{item_key}:primary-topic")
    edited_topics = columns[1].text_area(
        "全部 topics（逗号、空格或换行分隔；删除某行即移除标签）",
        value=current_topics,
        height=80,
        key=f"{item_key}:topics",
    )
    st.caption(f"已注册 topics：{', '.join(known_topics) if known_topics else '暂无'}")
    if st.button("保存 topic 标签", key=f"{item_key}:topics-save"):
        update_item_topics(item["id"], edited_primary, edited_topics)
        st.session_state["last_action_message"] = f"topic 标签已保存：{item.get('title', '')}"
        rerun(st)


def render_item(st, item: dict, key_prefix: str) -> None:
    metadata = item.get("metadata") or {}
    title = item.get("title") or "未命名条目"
    item_key = f"{key_prefix}:{item['id']}"
    with st.container(border=True):
        st.markdown(f"### {title}")
        st.caption(bibliographic_line(item))
        source_type = str(item.get("source_type") or "unknown")
        st.markdown(f"**{database_label(item)}** | 类型：**{source_type_label(source_type)}** (`{source_type}`)")
        st.caption(
            f"primary_topic `{item.get('topic', 'unknown')}` | topics `{', '.join(hub.item_topics(item)) or '(empty)'}` | source_type `{item.get('source_type', 'unknown')}` | "
            f"review `{hub.review_status(item)}` | process `{hub.process_status(item)}` | "
            f"metadata `{hub.metadata_status(item)}`"
        )
        st.markdown(
            f"relevance **{item.get('score', 'unknown')}** | authority **{item.get('authority_score', 'unknown')}** | "
            f"{METADATA_STATUS_LABELS.get(hub.metadata_status(item), hub.metadata_status(item))}"
        )
        if source_type in CONTEXT_SOURCE_TYPES:
            access, reason = hub.infer_document_access(item)
            st.markdown(f"文档可用性：**{DOCUMENT_ACCESS_LABELS.get(access, access)}** (`{access}`)")
            st.caption(reason)
        if item.get("url"):
            st.markdown(f"[Source]({item['url']})")
        if item.get("pdf_url"):
            st.markdown(f"[PDF]({item['pdf_url']})")
        if item.get("abstract_or_snippet"):
            st.write(str(item["abstract_or_snippet"])[:1200])
        render_topic_editor(st, item, item_key)
        if item.get("note_path"):
            st.code(str(item["note_path"]), language="text")
            render_note_preview(st, str(item["note_path"]))

        if str(item.get("source_type") or "") == "paper":
            render_pdf_actions(st, item, item_key, title)

        with st.expander("编辑 metadata", expanded=False):
            with st.form(key=f"{item_key}:metadata-form"):
                edited_title = st.text_input("Title", value=str(item.get("title", "")), key=f"{item_key}:title")
                edited_year = st.text_input("Year", value=str(metadata.get("year") or item.get("date") or ""), key=f"{item_key}:year")
                edited_venue = st.text_input("Venue / Journal / Conference", value=str(metadata.get("venue") or ""), key=f"{item_key}:venue")
                edited_publisher = st.text_input("Publisher", value=str(metadata.get("publisher") or ""), key=f"{item_key}:publisher")
                edited_authors = st.text_area("Authors (; separated)", value=str(metadata.get("authors") or ""), height=80, key=f"{item_key}:authors")
                edited_doi = st.text_input("DOI", value=str(metadata.get("doi") or ""), key=f"{item_key}:doi")
                edited_url = st.text_input("Source URL", value=str(item.get("url") or ""), key=f"{item_key}:url")
                edited_pdf_url = st.text_input("PDF URL", value=str(item.get("pdf_url") or ""), key=f"{item_key}:pdf-url")
                edited_source = st.text_input("Source provider/name", value=str(item.get("source") or ""), key=f"{item_key}:source")
                current_source_type = str(item.get("source_type") or "paper")
                source_index = SOURCE_TYPE_OPTIONS.index(current_source_type) if current_source_type in SOURCE_TYPE_OPTIONS else 0
                edited_source_type = st.selectbox("Source type", SOURCE_TYPE_OPTIONS, index=source_index, key=f"{item_key}:source-type")
                current_access, _reason = hub.infer_document_access(item)
                edited_document_access = st.selectbox(
                    "Document access（社会数据库条目）",
                    list(DOCUMENT_ACCESS_LABELS),
                    index=list(DOCUMENT_ACCESS_LABELS).index(current_access) if current_access in DOCUMENT_ACCESS_LABELS else 0,
                    format_func=lambda value: f"{DOCUMENT_ACCESS_LABELS.get(value, value)} ({value})",
                    key=f"{item_key}:document-access",
                )
                edited_snippet = st.text_area("Abstract / snippet", value=str(item.get("abstract_or_snippet") or ""), height=140, key=f"{item_key}:snippet")
                submitted = st.form_submit_button("保存 metadata 并标记 verified")
            if submitted:
                update_metadata(
                    item["id"],
                    {
                        "title": edited_title,
                        "date": edited_year,
                        "url": edited_url,
                        "pdf_url": edited_pdf_url,
                        "source": edited_source,
                        "source_type": edited_source_type,
                        "abstract_or_snippet": edited_snippet,
                    },
                    {
                        "year": edited_year,
                        "venue": edited_venue,
                        "publisher": edited_publisher,
                        "authors": edited_authors,
                        "doi": edited_doi,
                        "document_access": edited_document_access if edited_source_type in CONTEXT_SOURCE_TYPES else "",
                        "document_access_source": "manual" if edited_source_type in CONTEXT_SOURCE_TYPES else "",
                    },
                )
                st.session_state["last_action_message"] = f"metadata 已保存并标记 verified：{edited_title}"
                rerun(st)

        columns = st.columns(len(ACTION_LABELS))
        for column, (status, label) in zip(columns, ACTION_LABELS.items()):
            if column.button(label, key=f"{item_key}:review:{status}", disabled=hub.review_status(item) == status):
                update_review_status(item["id"], status)
                st.toast(f"已更新为 {STATUS_LABELS.get(status, status)}")
                rerun(st)

        with st.expander("危险操作：手动修改流程状态", expanded=False):
            selected_process = st.selectbox(
                "process_status",
                PROCESS_STATUS_OPTIONS,
                index=PROCESS_STATUS_OPTIONS.index(hub.process_status(item)),
                key=f"{item_key}:process-select",
            )
            confirmed = st.checkbox("确认覆盖 process_status", key=f"{item_key}:process-confirm")
            if st.button("覆盖 process_status", key=f"{item_key}:process-update", disabled=not confirmed):
                update_process_status(item["id"], selected_process)
                st.toast(f"流程状态已更新为 {STATUS_LABELS.get(selected_process, selected_process)}")
                rerun(st)


def render_items_tab(st, items: list[dict], filters: dict) -> None:
    render_topic_query_review_notices(st, items)
    review_items = [item for item in items if not review_completed(item)]
    needs_metadata = [item for item in review_items if hub.metadata_status(item) == "needs_review"]
    with st.expander(f"元数据待复核 ({len(needs_metadata)})", expanded=bool(needs_metadata)):
        if needs_metadata:
            for item in sorted(needs_metadata, key=lambda row: int(row.get("score") or 0), reverse=True)[:30]:
                st.markdown(f"- **{item.get('title', '未命名条目')}** | topic `{item.get('topic', 'unknown')}` | id `{item.get('id', '')}`")
        else:
            st.caption("暂无 metadata_status=needs_review 的条目。")

    filtered = [
        item
        for item in review_items
        if item_matches(
            item,
            filters["review_filter"],
            filters["process_filter"],
            filters["metadata_filter"],
            filters["topic"],
            filters["source_type"],
            filters["query"],
        )
    ]
    filtered = sorted(filtered, key=lambda row: int(row.get("score") or 0), reverse=True)
    st.caption(
        f"过滤：review={filters['review_filter']}; process={filters['process_filter']}; "
        f"metadata={filters['metadata_filter']}; topic={filters['topic']}; "
        f"source_type={filters['source_type']}; search={filters['query'] or '(empty)'}"
    )
    hidden_count = len(items) - len(review_items)
    st.write(f"{len(filtered)} / {len(review_items)} 待复核 items；已隐藏 {hidden_count} 个 metadata verified 且已有 note 的条目。")
    for item in filtered:
        render_item(st, item, key_prefix="review")


def render_paper_database_tab(st, items: list[dict]) -> None:
    papers = [item for item in items if str(item.get("source_type") or "") == "paper"]
    categories = sorted({topic for item in papers for topic in hub.item_topics(item)} | {topic_category(item) for item in papers})
    st.caption("这里显示全部论文；复核完成的论文也会保留在此查询。")

    columns = st.columns([1.2, 1.0, 1.0, 2.0])
    selected_category = columns[0].selectbox("分类", ["all", *categories], key="paper-db-category")
    selected_metadata = columns[1].selectbox("Metadata", ["all", "auto", "needs_review", "verified"], key="paper-db-metadata")
    selected_process = columns[2].selectbox("Process", ["all", *PROCESS_STATUS_OPTIONS], key="paper-db-process")
    query = columns[3].text_input("Search", key="paper-db-search")

    rows = []
    for item in papers:
        if selected_category != "all" and topic_category(item) != selected_category and not hub.item_has_topic(item, selected_category):
            continue
        if selected_metadata != "all" and hub.metadata_status(item) != selected_metadata:
            continue
        if selected_process != "all" and hub.process_status(item) != selected_process:
            continue
        if query:
            haystack = " ".join(
                [
                    str(item.get("title", "")),
                    str(item.get("topic", "")),
                    " ".join(hub.item_topics(item)),
                    str(item.get("abstract_or_snippet", "")),
                    str((item.get("metadata") or {}).get("authors", "")),
                    str((item.get("metadata") or {}).get("venue", "")),
                ]
            ).lower()
            if query.lower() not in haystack:
                continue
        rows.append(item)

    category_rows = [
        {"分类": category, "数量": sum(1 for item in papers if topic_category(item) == category or hub.item_has_topic(item, category))}
        for category in categories
    ]
    if category_rows:
        st.dataframe(category_rows, hide_index=True, width="stretch")

    rows = sorted(rows, key=lambda row: (topic_category(row), str(row.get("date") or ""), str(row.get("title") or "")), reverse=True)
    st.write(f"{len(rows)} / {len(papers)} papers")
    for item in rows:
        render_item(st, item, key_prefix="paper-db")


def render_context_database_tab(st, items: list[dict]) -> None:
    context_items = [item for item in items if str(item.get("source_type") or "") in CONTEXT_SOURCE_TYPES]
    categories = sorted({str(item.get("source_type") or "unknown") for item in context_items})
    st.caption("这里显示标准、政策、报告、白皮书、新闻和产业信号。先按文档可用性分层：直接 PDF 和网页正文优先读，门户/目录页只作为线索。")

    columns = st.columns([1.0, 1.2, 1.1, 1.0, 2.0])
    selected_type = columns[0].selectbox(
        "类型",
        ["all", *categories],
        format_func=lambda value: "all" if value == "all" else f"{source_type_label(value)} ({value})",
        key="context-db-type",
    )
    selected_topic = columns[1].selectbox("Topic", ["all", *sorted({topic for item in context_items for topic in hub.item_topics(item)})], key="context-db-topic")
    selected_access = columns[2].selectbox(
        "文档可用性",
        ["all", *DOCUMENT_ACCESS_LABELS.keys()],
        format_func=lambda value: "all" if value == "all" else f"{DOCUMENT_ACCESS_LABELS.get(value, value)} ({value})",
        key="context-db-access",
    )
    selected_review = columns[3].selectbox("Review", ["all", *REVIEW_STATUS_OPTIONS], key="context-db-review")
    query = columns[4].text_input("Search", key="context-db-search")

    type_rows = [
        {"类型": source_type_label(source_type), "source_type": source_type, "数量": sum(1 for item in context_items if item.get("source_type") == source_type)}
        for source_type in categories
    ]
    access_rows = [
        {
            "文档可用性": DOCUMENT_ACCESS_LABELS.get(access, access),
            "document_access": access,
            "数量": sum(1 for item in context_items if hub.infer_document_access(item)[0] == access),
        }
        for access in DOCUMENT_ACCESS_LABELS
    ]
    summary_columns = st.columns(2)
    if type_rows:
        summary_columns[0].dataframe(type_rows, hide_index=True, width="stretch")
    if access_rows:
        summary_columns[1].dataframe(access_rows, hide_index=True, width="stretch")

    rows = []
    for item in context_items:
        access, _reason = hub.infer_document_access(item)
        if selected_type != "all" and item.get("source_type") != selected_type:
            continue
        if selected_topic != "all" and not hub.item_has_topic(item, selected_topic):
            continue
        if selected_access != "all" and access != selected_access:
            continue
        if selected_review != "all" and hub.review_status(item) != selected_review:
            continue
        if query:
            haystack = " ".join(
                [
                    str(item.get("title", "")),
                    str(item.get("topic", "")),
                    " ".join(hub.item_topics(item)),
                    str(item.get("source", "")),
                    str(item.get("abstract_or_snippet", "")),
                    str(item.get("url", "")),
                ]
            ).lower()
            if query.lower() not in haystack:
                continue
        rows.append(item)

    rows = sorted(rows, key=lambda row: (hub.infer_document_access(row)[0], str(row.get("source_type") or ""), str(row.get("topic") or ""), str(row.get("title") or "")))
    st.write(f"{len(rows)} / {len(context_items)} signals")
    for item in rows:
        render_item(st, item, key_prefix="context-db")


def topic_counts(items: list[dict]) -> dict[str, Counter]:
    counts: dict[str, Counter] = defaultdict(Counter)
    for item in items:
        topics = hub.item_topics(item) or [str(item.get("topic") or "unknown")]
        for topic in topics:
            counts[topic][hub.review_status(item)] += 1
            counts[topic][hub.process_status(item)] += 1
            if hub.process_status(item) in {"noted", "used_in_synthesis"}:
                counts[topic]["noted_or_used"] += 1
    return counts


def topic_synthesis_exists(topic: str) -> bool:
    topic_dir = Path("topics") / topic
    return any((topic_dir / name).exists() for name in ["synthesis.md", "open_questions.md", "possible_directions.md"])


def render_topic_overview_tab(st, items: list[dict]) -> None:
    counts = topic_counts(items)
    min_notes = st.number_input("min-notes", min_value=1, max_value=50, value=10, step=1)
    headers = [
        "topic",
        "new",
        "kept",
        "downloaded",
        "noted_or_used",
        "noted",
        "used_in_synthesis",
        "min_notes",
        "ready_for_synthesis",
        "synthesis_exists",
    ]
    rows = []
    for topic in sorted(counts):
        row = {header: topic if header == "topic" else counts[topic][header] for header in headers}
        row["min_notes"] = min_notes
        row["ready_for_synthesis"] = counts[topic]["noted_or_used"] >= min_notes
        row["synthesis_exists"] = topic_synthesis_exists(topic)
        rows.append(row)
    st.dataframe(rows, hide_index=True, width="stretch")
    topics = [row["topic"] for row in rows]
    if not topics:
        st.info("暂无 topic 数据。")
        return
    selected_topic = st.selectbox("选择 topic 运行 synthesis", topics)
    dry_run = st.checkbox("只预览命令，不写文件", value=False, key="synthesis-dry-run")
    if st.button("运行 topic synthesis"):
        args = ["scripts/synthesize_topic.py", "--topic", selected_topic, "--min-notes", str(min_notes)]
        if dry_run:
            args.append("--dry-run")
        with st.spinner("正在运行 topic synthesis..."):
            code, output = run_script(args, timeout=3600)
        st.code(output or "(no output)", language="text")
        if code == 0:
            st.success("完成")
        else:
            st.error(f"失败，退出码 {code}")


def render_topic_workspace_tab(st, items: list[dict]) -> None:
    topics = sorted({topic for item in items for topic in hub.item_topics(item)})
    if not topics:
        st.info("暂无 topic 数据。")
        return
    selected_topic = st.selectbox("Topic", topics, key="workspace-topic")
    topic_items = hub.topic_items(items, selected_topic)
    noted_items = hub.noted_topic_items(items, selected_topic)
    context_items = [item for item in topic_items if str(item.get("source_type") or "") in CONTEXT_SOURCE_TYPES]
    st.caption(
        f"`{selected_topic}`：{len(topic_items)} 个条目，{len(noted_items)} 个已有 note，{len(context_items)} 个社会数据库线索。"
    )

    path = hub.topic_workspace_path(selected_topic)
    columns = st.columns([1.2, 1.2, 3.0])
    if columns[0].button("Extract related items from notes", key="topic-preview-extract"):
        extracted = hub.extract_related_items_from_notes(items, topic=selected_topic)
        if extracted:
            all_items, changed = hub.upsert_items(extracted)
            hub.write_review_dashboard(all_items)
            st.session_state["last_action_message"] = f"已抽取/更新 {len(changed)} 个推荐来源条目。"
        else:
            st.session_state["last_action_message"] = "没有发现可入库的具体推荐来源。"
        rerun(st)
    if columns[1].button("Refresh topic preview", key="topic-preview-refresh"):
        path = hub.write_topic_workspace(selected_topic, items, overwrite=True)
        st.session_state["last_action_message"] = f"Topic Preview 已刷新：{path.as_posix()}"
        rerun(st)
    columns[2].code(path.as_posix(), language="text")

    workspace_text = hub.build_topic_workspace(selected_topic, items)
    st.markdown(workspace_text)
    return


def render_collect_tab(st) -> None:
    st.subheader("情报收集")
    collect_topic = st.selectbox("收集 topic", ["all", *sorted(hub.topic_key_to_slug(hub.load_config()).keys())])
    dry_run = st.checkbox("只预览，不写文件", value=False)
    if st.button("运行收集"):
        args = ["scripts/collect_weekly.py", "--topic", collect_topic]
        if dry_run:
            args.append("--dry-run")
        with st.spinner("正在收集，可能需要几分钟..."):
            code, output = run_script(args)
        st.code(output or "(no output)", language="text")
        if code == 0:
            st.success("完成")
        else:
            st.error(f"失败，退出码 {code}")


def render_batch_tab(st) -> None:
    st.subheader("批量读取本地 PDF")
    pdf_dir = st.text_input("PDF 文件夹或单个 PDF", "literature/inbox/papers")
    batch_topic = st.selectbox("Topic", ["auto", *sorted(hub.topic_key_to_slug(hub.load_config()).keys())])
    max_items = st.number_input("本次最多读取篇数", min_value=0, max_value=100, value=3, step=1)
    mode = st.selectbox("读取模式", ["auto", "metadata-only", "text-draft", "kimi"])
    providers = st.text_input("Metadata providers", "openalex,crossref,semantic_scholar")
    force = st.checkbox("强制重读已经生成 note 的 PDF", value=False)
    preview_args = [
        "scripts/batch_read_pdfs.py",
        "--pdf-dir",
        pdf_dir,
        "--topic",
        batch_topic,
        "--providers",
        providers,
        "--max-items",
        str(max_items),
        "--mode",
        mode,
        "--dry-run",
    ]
    if force:
        preview_args.append("--force")
    if st.button("扫描待读取 PDF"):
        code, output = run_script(preview_args)
        st.code(output or "(no output)", language="text")
        if code != 0:
            st.error(f"扫描失败，退出码 {code}")
    confirm = st.checkbox("确认开始批量读取")
    if st.button("开始批量读取", disabled=not confirm):
        run_args = [arg for arg in preview_args if arg != "--dry-run"]
        with st.spinner("正在读取 PDF..."):
            code, output = run_script(run_args, timeout=7200)
        st.code(output or "(no output)", language="text")
        if code == 0:
            st.success("批量读取完成")
        else:
            st.error(f"批量读取结束但有失败，退出码 {code}")


def render_pdf_inbox_tab(st, items: list[dict]) -> None:
    st.subheader("PDF Inbox")
    st.caption("扫描 `literature/inbox/papers/`。注册只创建可复核 item，不生成 note；读取操作会另行生成或升级 note。")
    rows = hub.scan_pdf_inbox(items=items)
    if not rows:
        st.info("PDF inbox 暂无 PDF。")
        return

    st.dataframe(
        [
            {
                "filename": row["filename"],
                "registered": row["registered"],
                "item_id": row["registered_item_id"],
                "inferred_title": row["inferred_title"],
                "topic": row["inferred_topic"],
                "topic_confidence": row["topic_confidence"],
                "has_note": row["has_note"],
            }
            for row in rows
        ],
        hide_index=True,
        width="stretch",
    )

    providers = st.text_input("Metadata providers", "openalex,crossref,semantic_scholar", key="pdf-inbox-providers")
    topic = st.selectbox("Topic", ["auto", *sorted(hub.topic_key_to_slug(hub.load_config()).keys())], key="pdf-inbox-topic")
    provider_list = [provider.strip() for provider in providers.split(",") if provider.strip()]
    for row in rows:
        with st.container(border=True):
            st.markdown(f"### {row['filename']}")
            st.caption(f"`{row['path']}`")
            st.write(
                f"SHA256 `{row['sha256'][:16]}...` | inferred topic `{row['inferred_topic']}` "
                f"({row['topic_confidence']}, {row['topic_reason']})"
            )
            if row["registered"]:
                st.success(f"已注册：`{row['registered_item_id']}` {row['registered_title']}")
                if row["note_path"]:
                    st.code(row["note_path"], language="text")
                continue

            columns = st.columns(3)
            if columns[0].button("Register only", key=f"pdf-inbox-register:{row['sha256']}"):
                with st.spinner("正在注册 PDF item..."):
                    item = hub.register_pdf_item(Path(row["path"]), topic=topic, providers=provider_list)
                st.session_state["last_action_message"] = f"已注册 PDF：{item.get('title', row['filename'])}"
                rerun(st)
            if columns[1].button("Register + text-draft", key=f"pdf-inbox-text:{row['sha256']}"):
                with st.spinner("正在注册并生成 text-draft..."):
                    item = hub.register_pdf_item(Path(row["path"]), topic=topic, providers=provider_list)
                    code, output = read_item_from_gui(item, "text-draft")
                st.code(output or "(no output)", language="text")
                if code == 0:
                    st.session_state["last_action_message"] = f"已生成 text-draft：{item.get('title', row['filename'])}"
                    rerun(st)
                else:
                    st.error(f"读取失败，退出码 {code}")
            if columns[2].button("Register + Kimi note", key=f"pdf-inbox-kimi:{row['sha256']}"):
                with st.spinner("正在注册并生成 Kimi note..."):
                    item = hub.register_pdf_item(Path(row["path"]), topic=topic, providers=provider_list)
                    code, output = read_item_from_gui(item, "kimi")
                st.code(output or "(no output)", language="text")
                if code == 0:
                    st.session_state["last_action_message"] = f"已生成 Kimi note：{item.get('title', row['filename'])}"
                    rerun(st)
                else:
                    st.error(f"读取失败，退出码 {code}")


def render_topic_review_tab(st, items: list[dict]) -> None:
    pending = [item for item in items if item.get("topic") == hub.NEEDS_TOPIC_REVIEW]
    st.write(f"{len(pending)} items need topic review")
    known_topics = sorted(
        configured_topic_slugs()
        | {topic for item in items for topic in hub.item_topics(item)}
    )
    for item in pending:
        with st.container(border=True):
            st.markdown(f"### {item.get('title', '未命名条目')}")
            st.caption(f"id `{item.get('id')}` | review `{hub.review_status(item)}` | process `{hub.process_status(item)}`")
            if item.get("abstract_or_snippet"):
                st.write(str(item.get("abstract_or_snippet"))[:1000])
            if item.get("note_path"):
                st.code(str(item["note_path"]), language="text")
                render_note_preview(st, str(item["note_path"]))
            chosen = st.selectbox("分配到已有 topic", known_topics, key=f"topic-select:{item['id']}") if known_topics else ""
            custom = st.text_input("或输入新 topic slug", key=f"topic-custom:{item['id']}")
            target = custom.strip() or chosen
            if st.button("确认 topic", key=f"topic-approve:{item['id']}", disabled=not target):
                update_topic(item["id"], target)
                if custom.strip():
                    st.session_state["last_action_message"] = f"已创建或注册 topic `{hub.slugify(custom)}`，并分配条目。请在复核条目查看 query 补全提示。"
                rerun(st)


def main() -> None:
    st = require_streamlit()
    st.set_page_config(page_title="Low-Altitude Research Review", layout="wide")

    items = hub.load_items()
    topics = sorted({topic for item in items for topic in (hub.item_topics(item) or [str(item.get("topic") or "unknown")])})
    source_types = sorted({item.get("source_type", "unknown") for item in items if item.get("source_type")})

    st.title("低空研究情报工作台")
    st.caption("Canonical store: `data/items.jsonl`。界面只提供复核、预览和轻量脚本入口。")
    last_action_message = st.session_state.pop("last_action_message", "")
    if last_action_message:
        st.success(last_action_message)

    with st.sidebar:
        filters = {
            "review_filter": st.selectbox("Review status", ["all", *REVIEW_STATUS_OPTIONS], index=0),
            "process_filter": st.selectbox("Process status", ["all", *PROCESS_STATUS_OPTIONS], index=0),
            "metadata_filter": st.selectbox("Metadata status", ["all", "auto", "needs_review", "verified"], index=0),
            "topic": st.selectbox("Topic", ["all", *topics]),
            "source_type": st.selectbox(
                "Source type",
                ["all", *source_types],
                format_func=lambda value: "all" if value == "all" else f"{source_type_label(value)} ({value})",
            ),
            "query": st.text_input("Search"),
        }

    tabs = st.tabs(["情报收集", "复核条目", "Topic 审核", "PDF Inbox", "批量读 PDF", "Topic Overview", "Topic Preview", "论文数据库", "社会数据库"])
    with tabs[0]:
        render_collect_tab(st)
    with tabs[1]:
        render_items_tab(st, items, filters)
    with tabs[2]:
        render_topic_review_tab(st, items)
    with tabs[3]:
        render_pdf_inbox_tab(st, items)
    with tabs[4]:
        render_batch_tab(st)
    with tabs[5]:
        render_topic_overview_tab(st, items)
    with tabs[6]:
        render_topic_workspace_tab(st, items)
    with tabs[7]:
        render_paper_database_tab(st, items)
    with tabs[8]:
        render_context_database_tab(st, items)


if __name__ == "__main__":
    main()
