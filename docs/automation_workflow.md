# 自动化工作流

GitHub Actions 只负责每周收集和生成中文周报，不做最终研究判断。

当前定时任务在 `.github/workflows/literature_pipeline.yml` 中配置为每周一 UTC 02:00 运行。换算到北京时间是每周一 10:00。

## 手动运行

在 GitHub Actions 中运行 `Weekly Research Intelligence`，可选择：

```text
topic = all
topic = remote_id
topic = directional_networking
```

本地等价命令：

```powershell
python scripts/collect_weekly.py --topic all
```

## 自动输出

```text
data/items.jsonl
outputs/weekly/YYYY-MM-DD.md
outputs/review_dashboard.md
```

自动 PR 只表示“有新情报需要 review”，不表示这些条目已经被认可。

## 本地复核

GitHub Actions 不负责人工判断。拉取自动 PR 或本地运行收集后，用本地面板标记状态：

```powershell
pip install -r requirements.txt
python -m streamlit run scripts/review_app.py
```

状态仍写回 `data/items.jsonl`，不是写到外部系统。

这个界面也可以临时补跑每周收集；但长期建议让 GitHub Actions 定时生成 PR，你只 review PR 中的周报和 dashboard。

## 本地 PDF 阅读

PDF 阅读不放在 GitHub Actions 里，因为它依赖本地 PDF 和私有 API key：

```powershell
python scripts/read_item.py "literature/inbox/papers/example.pdf"
```

默认会自动推断 topic。无法可靠归类的 PDF 会进入 `needs_topic_review`，适合先生成 note，再在 GUI 的 Topic 审核里人工划分。

输出中文笔记到：

```text
notes/items/{论文标题}.md
```

批量读取建议先在 GUI 中扫描，确认后每次小批量读取。如果用命令行：

```powershell
python scripts/batch_read_pdfs.py --pdf-dir literature/inbox/papers --topic auto --dry-run
python scripts/batch_read_pdfs.py --pdf-dir literature/inbox/papers --topic auto --max-items 3
```
