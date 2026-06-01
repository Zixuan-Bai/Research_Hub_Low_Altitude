"""Local Streamlit review surface for data/items.jsonl."""

from __future__ import annotations

import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

import research_hub_lib as hub


REVIEW_STATUS_OPTIONS = ["new", "kept", "downloaded", "rejected"]
PROCESS_STATUS_OPTIONS = ["unread", "read", "summarized", "used_in_synthesis"]
SOURCE_TYPE_OPTIONS = ["paper", "news", "standard", "policy", "whitepaper", "report", "industry"]
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
    "read": "已生成文本草稿",
    "summarized": "已精读摘要",
    "used_in_synthesis": "已进入主题综合",
}
ACTION_LABELS = {"kept": "Keep", "rejected": "Reject", "downloaded": "Downloaded"}


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


def read_item_from_gui(item: dict, mode: str) -> tuple[int, str]:
    pdf_path = local_pdf_path(item)
    if not pdf_path:
        return 1, "没有找到本地 PDF。请先把 PDF 放入 literature/inbox/papers，或在 metadata 中补充 pdf_source。"
    topic = str(item.get("topic") or "auto")
    if topic == hub.NEEDS_TOPIC_REVIEW:
        topic = "auto"
    return run_script(
        ["scripts/read_item.py", str(pdf_path), "--topic", topic, "--mode", mode],
        timeout=7200,
    )


def latest_weekly_digest() -> Path | None:
    weekly_dir = Path("outputs/weekly")
    files = sorted(weekly_dir.glob("*.md"), reverse=True) if weekly_dir.exists() else []
    return files[0] if files else None


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


def update_follow_up_action_status(item_id: str, action_id: str, status: str) -> None:
    for item in hub.load_items():
        if item.get("id") != item_id:
            continue
        metadata = item.setdefault("metadata", {})
        actions = list(metadata.get("follow_up_actions") or [])
        for action in actions:
            if action.get("id") == action_id:
                action["status"] = status
                action["completed_at"] = hub.now_iso() if status in {"done", "skipped"} else ""
        metadata["follow_up_actions"] = actions
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


def review_completed(item: dict) -> bool:
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

        if str(item.get("source_type") or "") == "paper" and not has_existing_note(item):
            pdf_path = local_pdf_path(item)
            with st.expander("读取本地 PDF 生成 note", expanded=False):
                if pdf_path:
                    st.caption(f"PDF: `{pdf_path}`")
                else:
                    st.caption("未找到本地 PDF；请先下载 PDF，或在 metadata 中补充 `pdf_source`。")
                read_mode = st.selectbox("读取模式", ["auto", "text-draft", "kimi", "metadata-only"], key=f"{item_key}:read-mode")
                disabled = pdf_path is None
                if st.button("生成 / 同步 note", key=f"{item_key}:read-now", disabled=disabled):
                    with st.spinner("正在读取 PDF 并更新 item store..."):
                        code, output = read_item_from_gui(item, read_mode)
                    st.code(output or "(no output)", language="text")
                    if code == 0:
                        st.session_state["last_action_message"] = f"已处理：{title}"
                        rerun(st)
                    else:
                        st.error(f"读取失败，退出码 {code}")

        follow_up_actions = list(metadata.get("follow_up_actions") or [])
        if follow_up_actions:
            open_count = sum(1 for action in follow_up_actions if action.get("status") == "open")
            with st.expander(f"后续建议 ({open_count} open / {len(follow_up_actions)} total)", expanded=False):
                for action_index, action in enumerate(follow_up_actions):
                    st.markdown(f"- `{action.get('status', 'open')}` {action.get('text', '')}")
                    action_columns = st.columns(3)
                    for action_status, column in zip(["open", "done", "skipped"], action_columns):
                        if column.button(
                            action_status,
                            key=f"{item_key}:follow-up:{action_index}:{action.get('id')}:{action_status}",
                            disabled=action.get("status") == action_status,
                        ):
                            update_follow_up_action_status(item["id"], str(action.get("id")), action_status)
                            rerun(st)

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
    st.caption("这里显示标准、政策、报告、白皮书、新闻和产业信号。它们通常比普通论文更接近真实约束，但仍需要人工复核来源、时效和适用范围。")

    columns = st.columns([1.0, 1.2, 1.0, 2.0])
    selected_type = columns[0].selectbox(
        "类型",
        ["all", *categories],
        format_func=lambda value: "all" if value == "all" else f"{source_type_label(value)} ({value})",
        key="context-db-type",
    )
    selected_topic = columns[1].selectbox("Topic", ["all", *sorted({topic for item in context_items for topic in hub.item_topics(item)})], key="context-db-topic")
    selected_review = columns[2].selectbox("Review", ["all", *REVIEW_STATUS_OPTIONS], key="context-db-review")
    query = columns[3].text_input("Search", key="context-db-search")

    type_rows = [
        {"类型": source_type_label(source_type), "source_type": source_type, "数量": sum(1 for item in context_items if item.get("source_type") == source_type)}
        for source_type in categories
    ]
    if type_rows:
        st.dataframe(type_rows, hide_index=True, width="stretch")

    rows = []
    for item in context_items:
        if selected_type != "all" and item.get("source_type") != selected_type:
            continue
        if selected_topic != "all" and not hub.item_has_topic(item, selected_topic):
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

    rows = sorted(rows, key=lambda row: (str(row.get("source_type") or ""), str(row.get("topic") or ""), str(row.get("title") or "")))
    st.write(f"{len(rows)} / {len(context_items)} signals")
    for item in rows:
        render_item(st, item, key_prefix="context-db")


def render_weekly_digest_tab(st) -> None:
    digest = latest_weekly_digest()
    if not digest:
        st.info("尚未生成 weekly digest。")
        return
    st.caption(digest.as_posix())
    st.markdown(digest.read_text(encoding="utf-8", errors="replace"))


def topic_counts(items: list[dict]) -> dict[str, Counter]:
    counts: dict[str, Counter] = defaultdict(Counter)
    for item in items:
        topics = hub.item_topics(item) or [str(item.get("topic") or "unknown")]
        for topic in topics:
            counts[topic][hub.review_status(item)] += 1
            counts[topic][hub.process_status(item)] += 1
            if hub.process_status(item) in {"read", "summarized", "used_in_synthesis"}:
                counts[topic]["read_or_summarized"] += 1
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
        "read_or_summarized",
        "summarized",
        "used_in_synthesis",
        "min_notes",
        "ready_for_synthesis",
        "synthesis_exists",
    ]
    rows = []
    for topic in sorted(counts):
        row = {header: topic if header == "topic" else counts[topic][header] for header in headers}
        row["min_notes"] = min_notes
        row["ready_for_synthesis"] = counts[topic]["read_or_summarized"] >= min_notes
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


def render_collect_tab(st) -> None:
    st.subheader("每周情报收集")
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
        digest = latest_weekly_digest()
        if digest:
            st.markdown(f"Latest weekly digest: `{digest.as_posix()}`")

    tabs = st.tabs(["每周收集", "复核条目", "Topic 审核", "批量读 PDF", "Topic Overview", "Weekly Digest", "论文数据库", "社会数据库"])
    with tabs[0]:
        render_collect_tab(st)
    with tabs[1]:
        render_items_tab(st, items, filters)
    with tabs[2]:
        render_topic_review_tab(st, items)
    with tabs[3]:
        render_batch_tab(st)
    with tabs[4]:
        render_topic_overview_tab(st, items)
    with tabs[5]:
        render_weekly_digest_tab(st)
    with tabs[6]:
        render_paper_database_tab(st, items)
    with tabs[7]:
        render_context_database_tab(st, items)


if __name__ == "__main__":
    main()
