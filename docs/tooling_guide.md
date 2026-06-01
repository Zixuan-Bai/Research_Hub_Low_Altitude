# 工具指南

## 常用命令

情报收集：

```powershell
python scripts/collect_weekly.py --topic all
```

读取单个 PDF：

```powershell
python scripts/read_item.py "literature/inbox/papers/example.pdf"
```

默认 `--topic auto`；无法可靠归类时进入 GUI 的 Topic 审核。

本地复核界面：

```powershell
pip install -r requirements.txt
python -m streamlit run scripts/review_app.py
```

Windows 可双击仓库根目录的 `启动研究面板.bat`。

批量读取 PDF：

```powershell
python scripts/batch_read_pdfs.py --pdf-dir literature/inbox/papers --topic auto --dry-run
python scripts/batch_read_pdfs.py --pdf-dir literature/inbox/papers --topic auto --max-items 3
```

按需综合：

```powershell
python scripts/synthesize_topic.py --topic remote_id
```

验证：

```powershell
python scripts/validate_hub.py
```

## Kimi 配置

在本地 `.env` 中放：

```text
MOONSHOT_API_KEY=...
KIMI_READING_MODEL=kimi-k2.6
```

不要把真实 key 写进 `configs/*.json`。

## Review 习惯

优先看：

```text
outputs/review_dashboard.md
topics/<topic>/research_workspace.md
```

有 Streamlit 时优先用 `scripts/review_app.py` 标记状态；没有 Streamlit 时先看 Markdown dashboard。不要把机器摘要当最终结论。需要人工复核后再进入 topic synthesis。

GUI 的 `编辑 metadata` 会直接写回 `data/items.jsonl`。补全 publisher 或 venue 后，`authority` 会自动重算。

GUI 的普通按钮只修改 `review_status`，不会覆盖 `process_status`。如果需要手动修正流程状态，需要在条目卡片的危险操作区确认。`process_status` 只保留 `unread` / `noted` / `used_in_synthesis`，阅读深度看 metadata。

`relevance` 是自动相关性粗分，不是质量分。它主要根据 topic gate 命中的关键词数量排序，帮助你先看更可能相关的条目。

`authority` 是来源权威性粗分。它根据 venue、publisher、source_type 和 URL 判断来源大致可信度，例如 IEEE Transactions、Nature / Science family、政策、标准和权威报告更高，预印本或来源不明更低。
