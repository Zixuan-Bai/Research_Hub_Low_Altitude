"""Local Streamlit review surface for data/items.jsonl."""

from __future__ import annotations

import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

import research_hub_lib as hub


REVIEW_STATUS_OPTIONS = ["new", "kept", "downloaded", "rejected"]
PROCESS_STATUS_OPTIONS = ["unread", "read", "summarized", "used_in_synthesis"]
SOURCE_TYPE_OPTIONS = ["paper", "news", "standard", "policy", "whitepaper", "report"]
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


def latest_weekly_digest() -> Path | None:
    weekly_dir = Path("outputs/weekly")
    files = sorted(weekly_dir.glob("*.md"), reverse=True) if weekly_dir.exists() else []
    return files[0] if files else None


def update_review_status(item_id: str, status: str) -> None:
    for item in hub.load_items():
        if item.get("id") == item_id:
            item["review_status"] = status
            item.setdefault("metadata", {})["human_decision_at"] = hub.now_iso()
            hub.update_item(item)
            hub.write_review_dashboard(hub.load_items())
            return


def update_process_status(item_id: str, status: str) -> None:
    for item in hub.load_items():
        if item.get("id") == item_id:
            item["process_status"] = status
            item.setdefault("metadata", {})["manual_process_status_updated_at"] = hub.now_iso()
            hub.update_item(item)
            hub.write_review_dashboard(hub.load_items())
            return


def update_topic(item_id: str, topic: str) -> None:
    for item in hub.load_items():
        if item.get("id") == item_id:
            item["topic"] = topic
            item.setdefault("metadata", {})["topic_reviewed_at"] = hub.now_iso()
            hub.update_item(item)
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
        hub.update_item(item)
        hub.write_review_dashboard(hub.load_items())
        return


def item_matches(item: dict, review_filter: str, process_filter: str, topic: str, source_type: str, query: str) -> bool:
    if review_filter != "all" and hub.review_status(item) != review_filter:
        return False
    if process_filter != "all" and hub.process_status(item) != process_filter:
        return False
    if topic != "all" and item.get("topic") != topic:
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


def render_item(st, item: dict) -> None:
    metadata = item.get("metadata") or {}
    title = item.get("title") or "未命名条目"
    with st.container(border=True):
        st.markdown(f"### {title}")
        st.caption(bibliographic_line(item))
        st.caption(
            f"topic `{item.get('topic', 'unknown')}` | source_type `{item.get('source_type', 'unknown')}` | "
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
        if item.get("note_path"):
            st.code(str(item["note_path"]), language="text")
            render_note_preview(st, str(item["note_path"]))

        with st.expander("编辑 metadata", expanded=False):
            with st.form(key=f"metadata-form:{item['id']}"):
                edited_title = st.text_input("Title", value=str(item.get("title", "")))
                edited_year = st.text_input("Year", value=str(metadata.get("year") or item.get("date") or ""))
                edited_venue = st.text_input("Venue / Journal / Conference", value=str(metadata.get("venue") or ""))
                edited_publisher = st.text_input("Publisher", value=str(metadata.get("publisher") or ""))
                edited_authors = st.text_area("Authors (; separated)", value=str(metadata.get("authors") or ""), height=80)
                edited_doi = st.text_input("DOI", value=str(metadata.get("doi") or ""))
                edited_url = st.text_input("Source URL", value=str(item.get("url") or ""))
                edited_pdf_url = st.text_input("PDF URL", value=str(item.get("pdf_url") or ""))
                edited_source = st.text_input("Source provider/name", value=str(item.get("source") or ""))
                current_source_type = str(item.get("source_type") or "paper")
                source_index = SOURCE_TYPE_OPTIONS.index(current_source_type) if current_source_type in SOURCE_TYPE_OPTIONS else 0
                edited_source_type = st.selectbox("Source type", SOURCE_TYPE_OPTIONS, index=source_index)
                edited_snippet = st.text_area("Abstract / snippet", value=str(item.get("abstract_or_snippet") or ""), height=140)
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
                st.toast("metadata 已保存")
                rerun(st)

        columns = st.columns(len(ACTION_LABELS))
        for column, (status, label) in zip(columns, ACTION_LABELS.items()):
            if column.button(label, key=f"{item['id']}:{status}", disabled=hub.review_status(item) == status):
                update_review_status(item["id"], status)
                st.toast(f"已更新为 {STATUS_LABELS.get(status, status)}")
                rerun(st)

        with st.expander("危险操作：手动修改流程状态", expanded=False):
            selected_process = st.selectbox(
                "process_status",
                PROCESS_STATUS_OPTIONS,
                index=PROCESS_STATUS_OPTIONS.index(hub.process_status(item)),
                key=f"process-select:{item['id']}",
            )
            confirmed = st.checkbox("确认覆盖 process_status", key=f"process-confirm:{item['id']}")
            if st.button("覆盖 process_status", key=f"process-update:{item['id']}", disabled=not confirmed):
                update_process_status(item["id"], selected_process)
                st.toast(f"流程状态已更新为 {STATUS_LABELS.get(selected_process, selected_process)}")
                rerun(st)


def render_items_tab(st, items: list[dict], filters: dict) -> None:
    filtered = [
        item
        for item in items
        if item_matches(
            item,
            filters["review_filter"],
            filters["process_filter"],
            filters["topic"],
            filters["source_type"],
            filters["query"],
        )
    ]
    filtered = sorted(filtered, key=lambda row: int(row.get("score") or 0), reverse=True)
    st.caption(
        f"过滤：review={filters['review_filter']}; process={filters['process_filter']}; "
        f"topic={filters['topic']}; source_type={filters['source_type']}; search={filters['query'] or '(empty)'}"
    )
    st.write(f"{len(filtered)} / {len(items)} items")
    for item in filtered:
        render_item(st, item)


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
        topic = str(item.get("topic") or "unknown")
        counts[topic][hub.review_status(item)] += 1
        counts[topic][hub.process_status(item)] += 1
    return counts


def render_topic_overview_tab(st, items: list[dict]) -> None:
    counts = topic_counts(items)
    headers = ["topic", "new", "kept", "downloaded", "summarized", "used_in_synthesis"]
    rows = [{header: topic if header == "topic" else counts[topic][header] for header in headers} for topic in sorted(counts)]
    st.dataframe(rows, hide_index=True, use_container_width=True)
    topics = [row["topic"] for row in rows]
    if not topics:
        st.info("暂无 topic 数据。")
        return
    selected_topic = st.selectbox("选择 topic 运行 synthesis", topics)
    min_notes = st.number_input("min-notes", min_value=1, max_value=50, value=10, step=1)
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
    known_topics = sorted(set(hub.topic_key_to_slug(hub.load_config()).values()))
    for item in pending:
        with st.container(border=True):
            st.markdown(f"### {item.get('title', '未命名条目')}")
            st.caption(f"id `{item.get('id')}` | review `{hub.review_status(item)}` | process `{hub.process_status(item)}`")
            if item.get("abstract_or_snippet"):
                st.write(str(item.get("abstract_or_snippet"))[:1000])
            chosen = st.selectbox("分配到已有 topic", known_topics, key=f"topic-select:{item['id']}")
            custom = st.text_input("或输入新 topic slug", key=f"topic-custom:{item['id']}")
            target = custom.strip() or chosen
            if st.button("确认 topic", key=f"topic-approve:{item['id']}"):
                update_topic(item["id"], target)
                rerun(st)


def main() -> None:
    st = require_streamlit()
    st.set_page_config(page_title="Low-Altitude Research Review", layout="wide")

    items = hub.load_items()
    topics = sorted({item.get("topic", "unknown") for item in items if item.get("topic")})
    source_types = sorted({item.get("source_type", "unknown") for item in items if item.get("source_type")})

    st.title("低空研究情报工作台")
    st.caption("Canonical store: `data/items.jsonl`。界面只提供复核、预览和轻量脚本入口。")

    with st.sidebar:
        filters = {
            "review_filter": st.selectbox("Review status", ["all", *REVIEW_STATUS_OPTIONS], index=0),
            "process_filter": st.selectbox("Process status", ["all", *PROCESS_STATUS_OPTIONS], index=0),
            "topic": st.selectbox("Topic", ["all", *topics]),
            "source_type": st.selectbox("Source type", ["all", *source_types]),
            "query": st.text_input("Search"),
        }
        digest = latest_weekly_digest()
        if digest:
            st.markdown(f"Latest weekly digest: `{digest.as_posix()}`")

    tabs = st.tabs(["复核条目", "Weekly Digest", "Topic Overview", "每周收集", "批量读 PDF", "Topic 审核"])
    with tabs[0]:
        render_items_tab(st, items, filters)
    with tabs[1]:
        render_weekly_digest_tab(st)
    with tabs[2]:
        render_topic_overview_tab(st, items)
    with tabs[3]:
        render_collect_tab(st)
    with tabs[4]:
        render_batch_tab(st)
    with tabs[5]:
        render_topic_review_tab(st, items)


if __name__ == "__main__":
    main()
