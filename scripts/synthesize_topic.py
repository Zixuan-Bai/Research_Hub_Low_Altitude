"""Synthesize already-read Chinese item notes for one topic on demand."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import research_hub_lib as hub


def extract_note_preview(path: Path, max_chars: int = 6000) -> str:
    if not path.exists():
        return ""
    text = path.read_text(encoding="utf-8", errors="ignore")
    marker = "<!-- item_reading_metadata"
    if marker in text:
        text = text.split(marker, 1)[0].strip()
    return text[:max_chars]


def build_insufficient_outputs(topic: str, read_items: list[dict], min_notes: int) -> tuple[str, str, str]:
    titles = "\n".join(f"- {item.get('title', '未命名条目')} ({item.get('note_path', '')})" for item in read_items) or "- 暂无已读笔记"
    synthesis = f"""# {topic} 综合摘要

状态：needs-review

当前只有 {len(read_items)} 篇已读中文笔记，少于建议阈值 {min_notes} 篇。按照仓库规则，暂不形成研究 gap、route card 或最终方向判断。

## 已读材料

{titles}

## 下一步

- 继续收集和阅读该 topic 下的高相关论文、标准、政策和产业资料。
- 优先补充可验证参数、系统约束、部署背景和 baseline。
- 累积到足够材料后再重新运行 `python scripts/synthesize_topic.py --topic {topic}`。
"""
    open_questions = f"""# {topic} Open Questions

状态：needs-review

- unsupported: 当前已读材料不足，暂不稳定提炼 open questions。
- proposal: 先围绕通信模型、干扰模型、容量边界、监管/标准约束补充阅读。
"""
    directions = f"""# {topic} Possible Directions

状态：needs-review

- unsupported: 当前不生成方向建议。至少需要 {min_notes} 篇左右已读笔记，并完成人工复核后再讨论 possible directions。
"""
    return synthesis, open_questions, directions


def build_llm_prompt(topic: str, read_items: list[dict]) -> str:
    note_blocks = []
    for item in read_items:
        path = Path(item.get("note_path", ""))
        note_blocks.append(
            {
                "id": item.get("id", ""),
                "title": item.get("title", ""),
                "primary_topic": item.get("topic", ""),
                "topics": hub.item_topics(item),
                "note_path": item.get("note_path", ""),
                "note_preview": extract_note_preview(path),
            }
        )
    notes_json = json.dumps(note_blocks, ensure_ascii=False, indent=2)
    return f"""请基于以下已经生成的中文阅读笔记，为 topic `{topic}` 做一次保守综合。

严格规则：
- 只使用给定 notes，不要补充外部事实。
- 不要宣称研究 gap，除非至少三篇材料共同支持。
- 不要生成 route card、最终研究方向、创新性结论或建仓建议。
- 输出中文。

Notes:
```json
{notes_json}
```

请输出三部分：
1. synthesis.md：新兴聚类、重复假设、常见模型、证据不足点、推荐下一步阅读。
2. open_questions.md：开放问题，必须标注 paper-supported / inferred / proposal / unsupported。
3. possible_directions.md：只列 possible questions，不给最终路线判断。
"""


def write_outputs(topic: str, synthesis: str, open_questions: str, directions: str) -> None:
    topic_dir = Path("topics") / topic
    topic_dir.mkdir(parents=True, exist_ok=True)
    (topic_dir / "synthesis.md").write_text(synthesis, encoding="utf-8")
    (topic_dir / "open_questions.md").write_text(open_questions, encoding="utf-8")
    (topic_dir / "possible_directions.md").write_text(directions, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Synthesize one topic from already-read notes.")
    parser.add_argument("--topic", required=True, help="Topic key or topic slug.")
    parser.add_argument("--config", default=str(hub.DEFAULT_CONFIG), help="Pipeline config JSON.")
    parser.add_argument("--min-notes", type=int, default=10, help="Minimum read notes before LLM synthesis.")
    parser.add_argument("--timeout", type=int, default=300, help="Kimi request timeout in seconds.")
    parser.add_argument("--dry-run", action="store_true", help="Show planned synthesis without writes or API calls.")
    args = parser.parse_args()

    hub.load_env_file()
    config = hub.load_config(Path(args.config))
    topic = hub.topic_key_to_slug(config).get(args.topic, args.topic)
    items = hub.load_items()
    read_items = [
        item for item in items
        if hub.item_has_topic(item, topic) and hub.process_status(item) in {"noted", "used_in_synthesis"} and item.get("note_path")
    ]

    if args.dry_run:
        print(f"Topic: {topic}")
        print(f"Read notes: {len(read_items)}")
        print(f"Minimum notes: {args.min_notes}")
        return 0

    if len(read_items) < args.min_notes:
        synthesis, open_questions, directions = build_insufficient_outputs(topic, read_items, args.min_notes)
        write_outputs(topic, synthesis, open_questions, directions)
        print(f"Not enough notes for full synthesis: {len(read_items)}/{args.min_notes}. Wrote needs-review outputs.")
        return 0

    api_key, base_url, model = hub.kimi_config(config)
    prompt = build_llm_prompt(topic, read_items)
    data = hub.moonshot_request_json(
        f"{base_url.rstrip('/')}/chat/completions",
        api_key,
        {"model": model, "messages": [{"role": "user", "content": prompt}]},
        args.timeout,
    )
    text = hub.extract_chat_completion_text(data)
    topic_dir = Path("topics") / topic
    topic_dir.mkdir(parents=True, exist_ok=True)
    (topic_dir / "synthesis.md").write_text(text, encoding="utf-8")
    (topic_dir / "open_questions.md").write_text("# Open Questions\n\n请从 synthesis.md 中人工拆分并复核。\n", encoding="utf-8")
    (topic_dir / "possible_directions.md").write_text("# Possible Directions\n\n请从 synthesis.md 中人工拆分并复核。\n", encoding="utf-8")
    for item in read_items:
        item["process_status"] = "used_in_synthesis"
        item.setdefault("metadata", {})["used_in_synthesis_at"] = hub.now_iso()
        hub.update_item(item)
    print(f"Wrote topic synthesis with {len(read_items)} notes using {model}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
