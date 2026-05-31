# Low-Altitude Research Intelligence Hub

这是一个轻量级低空研究情报助手，不是完整知识管理平台，也不是 Level 1 实现仓库。

核心目标：

- 自动收集低空通信、UAV 系统、标准、政策和产业相关信号；
- 每周生成一份可 review 的中文情报摘要；
- 对你选中的 PDF 或条目生成中文阅读笔记；
- 在材料足够时，按 topic 手动触发综合；
- 保留清晰记录：收集了什么、读了什么、哪些仍需人工判断。

本仓库不自动生成最终研究结论，不自动宣称 novelty，不自动建议创建实现仓库。

## 主工作流

### 1. 每周收集

```powershell
python scripts/collect_weekly.py --topic all
```

主要查看：

```text
outputs/weekly/YYYY-MM-DD.md
outputs/review_dashboard.md
```

底层统一数据文件：

```text
data/items.jsonl
```

常规使用时不需要直接维护旧 CSV。

### 2. 本地复核界面

推荐用一个轻量 Streamlit 面板处理你需要人工判断的状态：`keep / reject / downloaded`。

```powershell
pip install -r requirements.txt
python -m streamlit run scripts/review_app.py
```

它只读写统一数据文件 `data/items.jsonl`，并同步更新：

```text
outputs/review_dashboard.md
```

如果本地暂时没有安装 Streamlit，也可以先打开 `outputs/review_dashboard.md` 做人工浏览。

GUI 里也可以直接运行每周收集、扫描本地 PDF、批量读取 PDF、处理 `needs_topic_review` 条目。每周收集在 GitHub Actions 中也有定时任务；本地按钮主要用于临时补跑。

每个条目卡片里的 `编辑 metadata` 可以直接修改数据库字段，包括 title、year、venue、publisher、authors、DOI、URL、source type 和 abstract/snippet。保存后会重算 `authority`；如果该条目已有 note 且标题被修改，note 文件名也会随标题同步更新。

### 3. 读取单个 PDF

```powershell
python scripts/read_item.py "literature/inbox/papers/example.pdf" --topic remote_id
```

输出：

```text
notes/items/{论文标题}.md
```

阅读笔记默认用中文。少量机器标签保留英文，例如：

- `paper-supported`
- `inferred`
- `proposal`
- `unsupported`
- `full-text parsed`

这些标签用于保持证据边界清晰。

如果一次放入多篇 PDF，可以先预览：

```powershell
python scripts/batch_read_pdfs.py --pdf-dir literature/inbox/papers --topic auto --dry-run
```

再小批量读取：

```powershell
python scripts/batch_read_pdfs.py --pdf-dir literature/inbox/papers --topic auto --max-items 3
```

批量读取会跳过已经生成过 note 的 PDF。无法可靠归入现有 topic 的条目会进入 `needs_topic_review`，需要在 GUI 中审批到已有 topic 或新候选 topic。

note 文件名默认使用数据库中的论文标题。若标题包含 Windows 不允许的文件名字符，脚本会自动替换；若重名，则追加 item id 防止覆盖。

### 4. 按需 topic synthesis

只有当某个 topic 已经积累足够已读笔记时，再运行：

```powershell
python scripts/synthesize_topic.py --topic remote_id
```

输出：

```text
topics/<topic>/synthesis.md
topics/<topic>/open_questions.md
topics/<topic>/possible_directions.md
```

如果材料不足，脚本会写出 `needs-review` 提示，而不是硬生成研究 gap 或路线卡。

## Human Review Model

用户只需要做少量状态判断：

```text
review_status:
new -> kept / downloaded / rejected

process_status:
unread -> summarized -> used_in_synthesis
```

其中：

```text
review_status：由你在 GUI 中点击决定，可以随时反复修改
process_status：由自动流程维护；Kimi 读完 PDF 后标记 summarized，topic synthesis 使用后标记 used_in_synthesis
```

GUI 默认只暴露 `review_status` 的三个按钮，避免误把已经读过或综合过的条目改回普通状态。如果确实要人工修改 `process_status`，需要展开条目中的“危险操作：手动修改流程状态”，勾选确认后才能覆盖。

状态记录在 `data/items.jsonl` 中。本地 Streamlit 面板用于日常标记；`outputs/review_dashboard.md` 用作无需安装依赖时的轻量 review 面板。

GUI 按钮含义：

- `Keep`：保留观察，后续可能下载或阅读。
- `Reject`：暂不关注，不进入后续阅读队列。
- `Downloaded`：PDF 已经合法下载到本地，等待后续读取。

`relevance` 是自动相关性粗分，不是论文质量分，也不是创新性判断。当前主要根据 topic 查询文件里的 `required_terms_any` 命中数量计算，最高 5 分；如果命中排除词则不进入周报。这个分数只用于决定优先 review 顺序。

`authority` 是来源权威性粗分，也不是最终质量判断。当前根据 venue、publisher、source_type、URL 等启发式估计来源可信度：IEEE Transactions、ACM Transactions、Nature / Science family、标准、政策、政府或权威技术报告会更高；预印本、来源不明、小型新闻或混合置信出版源会更低。这个分数需要人工复核，不能单独支撑研究判断。

## 数据边界

可以进入仓库：

- `data/items.jsonl`
- 中文周报
- 中文阅读笔记
- topic synthesis / open questions / possible directions
- 轻量脚本和配置

不应进入仓库：

- 大 PDF 或受版权限制的 full-text dumps；
- datasets、checkpoints、长实验日志；
- 未经证据支持的最终论文结论；
- Level 1 实现代码。

本地 PDF 可以临时放在：

```text
literature/inbox/papers/
```

该目录默认不提交 PDF。

## 配置

topic 查询入口仍在：

```text
literature/queries/
```

Kimi/Moonshot key 放在本地 `.env`：

```powershell
MOONSHOT_API_KEY=...
KIMI_READING_MODEL=kimi-k2.6
```

`.env` 不提交到仓库。

## 验证

```powershell
python scripts/validate_hub.py
python scripts/collect_weekly.py --topic remote_id --dry-run
python scripts/read_item.py --help
python scripts/batch_read_pdfs.py --dry-run
python -m py_compile scripts/review_app.py scripts/batch_read_pdfs.py
python scripts/synthesize_topic.py --topic remote_id --dry-run
```

## 原则

不要构建完整研究平台。

优先：

```text
simple, reviewable, useful
```

而不是：

```text
complete, automated, over-engineered
```
