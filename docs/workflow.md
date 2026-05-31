# 工作流

本仓库只保留轻量研究情报主线。

```text
每周收集
-> 打开中文周报和本地 review app / review dashboard
-> 人工判断 keep / reject / download / read
-> 对选中的 PDF 生成中文笔记
-> 材料足够后手动 topic synthesis
```

## 1. 每周收集

```powershell
python scripts/collect_weekly.py --topic all
```

主要查看：

```text
outputs/weekly/YYYY-MM-DD.md
outputs/review_dashboard.md
```

## 2. 本地复核

推荐使用 Streamlit 本地界面：

```powershell
pip install -r requirements.txt
python -m streamlit run scripts/review_app.py
```

该界面直接更新 `data/items.jsonl`，并重新生成 `outputs/review_dashboard.md`。如果暂时不用 Streamlit，就打开 `outputs/review_dashboard.md` 浏览条目，再少量手动调整状态。

界面包含四个常用区：

- 复核条目：处理 `review_status` 的 keep / reject / downloaded 三类人工状态；
- 每周收集：临时补跑 `collect_weekly.py`；
- 批量读 PDF：扫描并小批量读取 `literature/inbox/papers/`；
- Topic 审批：处理 `needs_topic_review`，不自动新增方向。

每个条目卡片中的 `编辑 metadata` 会直接修改 `data/items.jsonl`。适合补全自动脚本没有拿到的 publisher、venue、authors、DOI 等字段。保存后会重新计算 `authority`。

状态分两层：`review_status` 是人工决策层，可以随时改；`process_status` 是自动流程层，通常由 Kimi 阅读和 topic synthesis 自动更新。GUI 中修改流程层需要额外确认。

复核条目的 `relevance` 只是自动相关性粗分：主要来自 topic 查询文件中 `required_terms_any` 的命中数量，最高 5 分。它不代表论文质量、创新性或可实施性，只用于排序优先 review 的条目。

复核条目的 `authority` 是来源权威性粗分：主要来自 venue、publisher、source_type 和 URL 的启发式判断。它帮助你优先看权威来源，但仍需要人工复核。

## 3. 单篇阅读

```powershell
python scripts/read_item.py "literature/inbox/papers/example.pdf" --topic remote_id
```

输出：

```text
notes/items/{论文标题}.md
```

笔记正文用中文。机器标签保留英文，用来保证证据边界清晰。

批量读取：

```powershell
python scripts/batch_read_pdfs.py --pdf-dir literature/inbox/papers --topic auto --dry-run
python scripts/batch_read_pdfs.py --pdf-dir literature/inbox/papers --topic auto --max-items 3
```

批量脚本会自动跳过已有 note 的 PDF。无法匹配现有 topic 的 PDF 会标记为 `needs_topic_review`，等待人工审批。

note 文件名与数据库中的论文标题保持一致；标题改变后，已有 note 会尝试同步重命名。

## 4. Topic synthesis

```powershell
python scripts/synthesize_topic.py --topic remote_id
```

如果已读材料不足，脚本只写 `needs-review` 提示，不生成研究 gap 或路线卡。

## 5. 不再默认做的事

- 不自动生成 route card；
- 不自动排名 feasibility；
- 不自动建议创建 Level 1 repo；
- 不要求维护多个 CSV；
- 不把 GitHub PR diff 当作主要 review 界面。
