# 持续研究情报

本仓库的持续情报目标是节省每周检索和初筛时间，而不是自动完成研究选题。

## 主输出

每周主要看一个文件：

```text
outputs/weekly/YYYY-MM-DD.md
```

辅助 review 面板：

```text
outputs/review_dashboard.md
```

## 统一数据

所有条目进入：

```text
data/items.jsonl
```

状态生命周期：

```text
review_status:
new -> kept / downloaded / rejected

process_status:
unread -> summarized -> used_in_synthesis
```

`review_status` 是人工决策层；`process_status` 是自动流程层。GUI 默认只修改 `review_status`，避免误改已经阅读或综合过的条目。

## 中文笔记

单篇 PDF 阅读输出到：

```text
notes/items/{论文标题}.md
```

笔记应默认中文，且明确标注：

- `paper-supported`
- `inferred`
- `proposal`
- `unsupported`

## Topic synthesis

只有当某个 topic 下积累了足够已读笔记时，才运行：

```powershell
python scripts/synthesize_topic.py --topic remote_id
```

材料不足时只输出 `needs-review`，不生成研究结论。
