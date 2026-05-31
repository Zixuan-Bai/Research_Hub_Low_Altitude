"""Local Streamlit review surface for data/items.jsonl.

This app is intentionally thin: data/items.jsonl remains the canonical store,
and the app only helps the user make lifecycle decisions without editing JSONL.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import research_hub_lib as hub


REVIEW_STATUS_OPTIONS = ["new", "kept", "downloaded", "rejected"]
PROCESS_STATUS_OPTIONS = ["unread", "read", "summarized", "used_in_synthesis"]
ACTION_LABELS = {
    "kept": "Keep",
    "rejected": "Reject",
    "downloaded": "Downloaded",
}
ACTION_HELP = {
    "kept": "保留观察。表示这个条目值得继续跟踪，但还没有读取全文。",
    "rejected": "暂不关注。表示这个条目与当前研究情报目标不够相关。",
    "downloaded": "PDF 已经合法下载到本地，等待后续读取。",
}
STATUS_LABELS = {
    "new": "未处理",
    "kept": "保留",
    "downloaded": "已下载",
    "read": "已读取",
    "summarized": "已生成笔记",
    "used_in_synthesis": "已用于综合",
    "rejected": "已拒绝",
    "unread": "未读取",
}
SOURCE_TYPE_OPTIONS = ["paper", "news", "standard", "policy", "whitepaper", "report"]


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


def update_review_status(item_id: str, status: str) -> None:
    items = hub.load_items()
    for item in items:
        if item.get("id") == item_id:
            item["review_status"] = status
            item.setdefault("metadata", {})["human_decision_at"] = hub.now_iso()
            hub.update_item(item)
            hub.write_review_dashboard(hub.load_items())
            return


def update_process_status(item_id: str, status: str) -> None:
    items = hub.load_items()
    for item in items:
        if item.get("id") == item_id:
            item["process_status"] = status
            item.setdefault("metadata", {})["manual_process_status_updated_at"] = hub.now_iso()
            hub.update_item(item)
            hub.write_review_dashboard(hub.load_items())
            return


def update_topic(item_id: str, topic: str) -> None:
    items = hub.load_items()
    for item in items:
        if item.get("id") == item_id:
            item["topic"] = topic
            item.setdefault("metadata", {})["topic_reviewed_at"] = hub.now_iso()
            hub.update_item(item)
            hub.write_review_dashboard(hub.load_items())
            return


def update_metadata(item_id: str, top_level: dict, metadata_updates: dict) -> None:
    items = hub.load_items()
    for item in items:
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
        metadata["manual_metadata_updated_at"] = hub.now_iso()
        hub.update_item(item)
        hub.write_review_dashboard(hub.load_items())
        return


def latest_weekly_digest() -> Path | None:
    weekly_dir = Path("outputs/weekly")
    if not weekly_dir.exists():
        return None
    files = sorted(weekly_dir.glob("*.md"), reverse=True)
    return files[0] if files else None


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


def item_matches(item: dict, review_filter: str, process_filter: str, topic: str, source_type: str, query: str) -> bool:
    if review_filter != "all" and hub.review_status(item) != review_filter:
        return False
    if process_filter != "all" and hub.process_status(item) != process_filter:
        return False
    if topic != "all" and item.get("topic") != topic:
        return False
    if source_type != "all" and item.get("source_type") != source_type:
        return False
    if query:
        haystack = " ".join(
            [
                str(item.get("title", "")),
                str(item.get("abstract_or_snippet", "")),
                str(item.get("source", "")),
                str(item.get("topic", "")),
            ]
        ).lower()
        return query.lower() in haystack
    return True


def compact_authors(authors: str, max_authors: int = 4) -> str:
    if not authors:
        return ""
    parts = [part.strip() for part in authors.split(";") if part.strip()]
    if not parts:
        return authors
    if len(parts) > max_authors:
        return "; ".join(parts[:max_authors]) + f"; et al. ({len(parts)} authors)"
    return "; ".join(parts)


def bibliographic_line(item: dict) -> str:
    metadata = item.get("metadata") or {}
    year = metadata.get("year") or item.get("date") or "year unknown"
    venue = metadata.get("venue") or metadata.get("publisher") or item.get("source") or "venue/source unknown"
    authors = compact_authors(str(metadata.get("authors") or ""))
    pieces = [str(year), str(venue)]
    if authors:
        pieces.append(authors)
    doi = metadata.get("doi")
    if doi:
        pieces.append(f"DOI: {doi}")
    return " | ".join(piece for piece in pieces if piece)


def internal_state_line(item: dict) -> str:
    relevance = (item.get("metadata") or {}).get("relevance_reason", "")
    authority = item.get("authority_score", "")
    authority_reason = (item.get("metadata") or {}).get("authority_reason", "")
    pieces = [
        f"review `{hub.review_status(item)}` ({STATUS_LABELS.get(hub.review_status(item), '')})",
        f"process `{hub.process_status(item)}` ({STATUS_LABELS.get(hub.process_status(item), '')})",
        f"`{item.get('topic', 'unknown')}`",
        str(item.get("source_type", "unknown")),
        f"relevance {item.get('score', '')}",
    ]
    if authority:
        pieces.append(f"authority {authority}")
    if relevance:
        pieces.append(str(relevance))
    if authority_reason:
        pieces.append(str(authority_reason))
    return " | ".join(pieces)


def status_badge(st, item: dict) -> None:
    labels = {
        "new": ":gray[未处理]",
        "kept": ":blue[已保留]",
        "downloaded": ":green[已下载]",
        "read": ":green[已读取]",
        "summarized": ":green[已生成笔记]",
        "used_in_synthesis": ":violet[已用于综合]",
        "rejected": ":red[已拒绝]",
    }
    review = hub.review_status(item)
    process = hub.process_status(item)
    st.markdown(f"人工状态：**{labels.get(review, review)}**　流程状态：**{labels.get(process, process)}**")


def render_item(st, item: dict) -> None:
    title = item.get("title") or "未命名条目"
    with st.container(border=True):
        st.markdown(f"### {title}")
        st.caption(bibliographic_line(item))
        st.caption(internal_state_line(item))
        url = item.get("url")
        pdf_url = item.get("pdf_url")
        if url:
            st.markdown(f"[Source]({url})")
        if pdf_url:
            st.markdown(f"[PDF]({pdf_url})")
        snippet = item.get("abstract_or_snippet", "")
        if snippet:
            st.write(snippet[:1200] + ("..." if len(snippet) > 1200 else ""))
        note_path = item.get("note_path")
        if note_path:
            st.code(note_path, language="text")

        with st.expander("编辑 metadata", expanded=False):
            metadata = item.get("metadata") or {}
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
                submitted = st.form_submit_button("保存 metadata")
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

        status_badge(st, item)
        columns = st.columns(len(ACTION_LABELS))
        for column, (status, label) in zip(columns, ACTION_LABELS.items()):
            disabled = hub.review_status(item) == status
            button_type = "primary" if disabled else "secondary"
            if column.button(label, key=f"{item['id']}:{status}", help=ACTION_HELP.get(status, ""), disabled=disabled, type=button_type):
                update_review_status(item["id"], status)
                st.toast(f"已更新为 {STATUS_LABELS.get(status, status)}")
                rerun(st)

        with st.expander("危险操作：手动修改流程状态", expanded=False):
            st.warning("流程状态通常由 Kimi 阅读和 topic synthesis 自动维护。只有确认数据库状态错误时才手动修改。")
            selected_process = st.selectbox(
                "流程状态",
                PROCESS_STATUS_OPTIONS,
                index=PROCESS_STATUS_OPTIONS.index(hub.process_status(item)),
                key=f"process-select:{item['id']}",
            )
            confirmed = st.checkbox("我确认要覆盖流程状态", key=f"process-confirm:{item['id']}")
            if st.button("覆盖流程状态", key=f"process-update:{item['id']}", disabled=not confirmed):
                update_process_status(item["id"], selected_process)
                st.toast(f"流程状态已更新为 {STATUS_LABELS.get(selected_process, selected_process)}")
                rerun(st)


def main() -> None:
    st = require_streamlit()
    st.set_page_config(page_title="Low-Altitude Research Review", layout="wide")

    items = hub.load_items()
    topics = sorted({item.get("topic", "unknown") for item in items if item.get("topic")})
    source_types = sorted({item.get("source_type", "unknown") for item in items if item.get("source_type")})

    st.title("低空研究情报工作台")
    st.caption("所有状态仍写入 data/items.jsonl；界面只提供更低成本的操作入口。")

    with st.sidebar:
        review_filter = st.selectbox("Review status", ["all", *REVIEW_STATUS_OPTIONS], index=0)
        process_filter = st.selectbox("Process status", ["all", *PROCESS_STATUS_OPTIONS], index=0)
        topic = st.selectbox("Topic", ["all", *topics])
        source_type = st.selectbox("Source type", ["all", *source_types])
        query = st.text_input("Search")
        digest = latest_weekly_digest()
        if digest:
            st.markdown(f"Latest weekly digest: `{digest.as_posix()}`")
        st.markdown("Canonical store: `data/items.jsonl`")

    review_tab, collect_tab, batch_tab, topic_tab = st.tabs(["复核条目", "每周收集", "批量读 PDF", "Topic 审批"])

    with review_tab:
        with st.expander("按钮和 score 说明", expanded=False):
            st.markdown(
                """
- `Keep`：保留观察，后续可能下载或阅读。
- `Reject`：暂不关注，不进入后续阅读队列。
- `Downloaded`：PDF 已下载到本地，等待读取。

`relevance` 是自动相关性粗分，不是论文质量分。当前主要根据 topic 配置里的 `required_terms_any` 命中数量计算，最多 5 分；命中越多，越适合优先人工 review。

`authority` 是来源权威性粗分，也不是论文质量分。它根据 venue、publisher、source_type、URL 等启发式估计来源可信度，例如 IEEE Transactions / Nature / Science / 标准政策类来源会更高，预印本或来源不明会更低。

`review_status` 是人工层，可以随时改。`process_status` 是流程层，默认由自动流程更新：Kimi 读完并写出 note 后自动进入 `summarized`；topic synthesis 使用后自动进入 `used_in_synthesis`。如果要手动覆盖流程层，需要在危险操作区确认。
                """
            )
        filtered = [item for item in items if item_matches(item, review_filter, process_filter, topic, source_type, query)]
        filtered = sorted(filtered, key=lambda row: int(row.get("score") or 0), reverse=True)
        st.caption(f"当前过滤：Review={review_filter}; Process={process_filter}; Topic={topic}; Source type={source_type}; Search={query or '(empty)'}")
        st.write(f"{len(filtered)} / {len(items)} items")
        for item in filtered:
            render_item(st, item)

    with collect_tab:
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

    with batch_tab:
        st.subheader("批量读取本地 PDF")
        st.caption("默认跳过已经生成过 note 的 PDF。未知 topic 会标记为 needs_topic_review，等待人工审批。")
        pdf_dir = st.text_input("PDF 文件夹或单个 PDF", "literature/inbox/papers")
        batch_topic = st.selectbox("Topic", ["auto", *sorted(hub.topic_key_to_slug(hub.load_config()).keys())])
        max_items = st.number_input("本次最多读取篇数", min_value=0, max_value=100, value=3, step=1)
        providers = st.text_input("Metadata providers", "openalex,crossref,semantic_scholar")
        force = st.checkbox("强制重读已生成 note 的 PDF", value=False)
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
            "--dry-run",
        ]
        if force:
            preview_args.append("--force")
        if st.button("扫描待读取 PDF"):
            code, output = run_script(preview_args)
            st.code(output or "(no output)", language="text")
            if code != 0:
                st.error(f"扫描失败，退出码 {code}")

        st.warning("真正批量读取会调用 Kimi/Moonshot API，并可能产生费用。建议先扫描，再小批量读取。")
        confirm = st.checkbox("确认开始批量读取")
        if st.button("开始批量读取", disabled=not confirm):
            run_args = [arg for arg in preview_args if arg != "--dry-run"]
            with st.spinner("正在读取 PDF。每篇可能需要较长时间..."):
                code, output = run_script(run_args, timeout=7200)
            st.code(output or "(no output)", language="text")
            if code == 0:
                st.success("批量读取完成")
            else:
                st.error(f"批量读取结束但有失败，退出码 {code}")

    with topic_tab:
        st.subheader("待审批 topic")
        pending = [item for item in items if item.get("topic") == hub.NEEDS_TOPIC_REVIEW]
        st.write(f"{len(pending)} items need topic review")
        known_topics = sorted(set(hub.topic_key_to_slug(hub.load_config()).values()))
        for item in pending:
            with st.container(border=True):
                st.markdown(f"### {item.get('title', '未命名条目')}")
                st.caption(f"id `{item.get('id')}` | review `{hub.review_status(item)}` | process `{hub.process_status(item)}`")
                if item.get("abstract_or_snippet"):
                    st.write(item.get("abstract_or_snippet")[:1000])
                chosen = st.selectbox("分配到已有 topic", known_topics, key=f"topic-select:{item['id']}")
                custom = st.text_input("或输入新候选 topic slug（需人工确认后才使用）", key=f"topic-custom:{item['id']}")
                target = custom.strip() or chosen
                if st.button("确认 topic", key=f"topic-approve:{item['id']}"):
                    update_topic(item["id"], target)
                    rerun(st)


if __name__ == "__main__":
    main()
