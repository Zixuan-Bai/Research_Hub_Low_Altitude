# 工作流

本仓库只保留轻量研究情报主线。

```text
定期收集
-> 打开本地 review app / review dashboard
-> 人工判断 keep / reject / downloaded
-> 对选中的 PDF 生成中文笔记
-> 从 note 中抽取具体推荐来源
-> 在 Topic Preview 中查看覆盖情况
-> 材料足够后手动 topic synthesis
```

## 1. 情报收集

```powershell
python scripts/collect_weekly.py --topic all
```

主要查看：

```text
outputs/review_dashboard.md
```

## 2. 本地复核

推荐使用 Streamlit 本地界面：

```powershell
pip install -r requirements.txt
python -m streamlit run scripts/review_app.py
```

该界面直接更新 `data/items.jsonl`，并重新生成 `outputs/review_dashboard.md`。如果暂时不用 Streamlit，就打开 `outputs/review_dashboard.md` 浏览条目，再少量手动调整状态。

界面按常用工作流排序：

- 情报收集：临时补跑 `collect_weekly.py`；
- 复核条目：处理 `review_status` 的 keep / reject / downloaded 三类人工状态，也可对已有本地 PDF 的条目直接生成 note；
- Topic 审核：处理 `needs_topic_review`，输入新 topic slug 时会注册为正式 topic，并在复核条目里提示补全 query；
- PDF Inbox：扫描 `literature/inbox/papers/`，可以只注册 PDF，也可以注册后生成 text-draft 或 Kimi note；
- 批量读 PDF：扫描并小批量读取 `literature/inbox/papers/`；
- Topic Overview：查看 topic 统计并按需运行 synthesis；
- Topic Preview：只读生成 `topics/<topic>/research_workspace.md`，展示覆盖情况、证据基底、社会/context 线索、推荐来源抽取结果和 synthesis readiness；
- 论文数据库：只查询论文，包括已经复核完成的 paper 条目；
- 社会数据库：只查询标准、政策、报告、白皮书、新闻和产业信号。

复核条目仍然混合显示，方便统一做 keep / reject / downloaded 判断；但每张卡片会明显标出它属于“论文数据库”还是“社会数据库”，并显示具体 source_type。标准、政策、报告和产业信号通常更接近真实约束，但仍要复核来源、时效和适用范围，不能直接当成研究结论。

每个条目卡片中的 `编辑 metadata` 会直接修改 `data/items.jsonl`。适合补全自动脚本没有拿到的 publisher、venue、authors、DOI 等字段。保存后会重新计算 `authority`。

状态分两层：`review_status` 是人工决策层，可以随时改；`process_status` 是自动流程层，当前只保留 `unread` / `noted` / `used_in_synthesis`。只要生成 note 就是 `noted`，阅读深度看 metadata 里的 `reading_status` / `reading_mode`。GUI 中修改流程层需要额外确认。

复核条目的 `relevance` 只是自动相关性粗分：主要来自 topic 查询文件中 `required_terms_any` 的命中数量，最高 5 分。它不代表论文质量、创新性或可实施性，只用于排序优先 review 的条目。

复核条目的 `authority` 是来源权威性粗分：主要来自 venue、publisher、source_type 和 URL 的启发式判断。它帮助你优先看权威来源，但仍需要人工复核。

## 3. 单篇阅读

```powershell
python scripts/read_item.py "literature/inbox/papers/example.pdf"
```

默认会自动推断 topic。你也可以先在复核条目里点击读取按钮生成 note，再到 Topic 审核里根据 note 划分 topic；只有已经确定 topic 时才需要显式加 `--topic <topic>`。

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

## 4. 推荐来源与 research atoms

note 中的 `推荐入库条目` 只应写具体来源，不写泛化后续任务。抽取推荐来源：

```powershell
python scripts/extract_related_items.py --from-notes --topic all
python scripts/extract_related_items.py --note "notes/items/<id>.md"
```

Typed semantic gap discovery 的第一步只抽取 atoms，不生成 gap 或 idea：

```powershell
python scripts/extract_research_atoms.py --topic all
python scripts/extract_research_atoms.py --topic remote_id_broadcast_capacity
python scripts/extract_research_atoms.py --note "notes/items/<id>.md"
```

输出为 `data/research_atoms.jsonl`，每条 atom 都保留 evidence label 和 source note。

## 5. Topic synthesis

```powershell
python scripts/synthesize_topic.py --topic remote_id
```

如果已读材料不足，脚本只写 `needs-review` 提示，不生成研究 gap 或路线卡。

当前运行逻辑：

- 读取 `data/items.jsonl`；
- 只选择 `item.topic == <topic>` 或 `topics` 包含该 topic、`process_status` 为 `noted` / `used_in_synthesis`、并且已有 `note_path` 的条目；
- 每篇 note 最多截取前 6000 字，交给 Kimi/Moonshot 做保守综合；
- 如果已读 note 少于 `--min-notes`，只输出 `needs-review` 占位文件。

`topic` 是主标签，`topics` 是多标签列表。复核条目和两个数据库视图中的每个条目卡片都会直接给出 topic 编辑区，可以修改主 topic，也可以用逗号、空格或换行添加/删除多个 topic。topic synthesis 按 `item.topic == x or x in item.topics` 选择 notes，因此论文、标准、政策和产业材料都可以被多个方向共同引用。

## 6. 本地原文放置

论文 PDF 放在：

```text
literature/inbox/papers/
```

社会数据库原文按类型放在：

```text
literature/inbox/social/standards/
literature/inbox/social/policies/
literature/inbox/social/reports/
literature/inbox/social/industry/
literature/inbox/social/news/
```

这些目录默认不提交原文文件。仓库只保留 metadata、URL、中文 note 和综合输出。

## 7. 不再默认做的事

- 不自动生成 route card；
- 不自动排名 feasibility；
- 不自动建议创建 Level 1 repo；
- 不要求维护多个 CSV；
- 不把 GitHub PR diff 当作主要 review 界面。
- 不维护通用 follow-up action 任务列表。
