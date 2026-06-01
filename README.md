# Low-Altitude Research Intelligence Hub

这是一个轻量级低空研究情报助手，不是完整知识管理平台，也不是 Level 1 实现仓库。

核心目标：

- 自动收集低空通信、UAV 系统、标准、政策和产业相关信号；
- 对你选中的 PDF 或条目生成中文阅读笔记；
- 在 Topic Workspace 中基于已有 note 讨论研究认识、不确定信息和候选 idea；
- 在材料足够时，按 topic 手动触发保守综合；
- 保留清晰记录：收集了什么、读了什么、哪些仍需人工判断。

本仓库不自动生成最终研究结论，不自动宣称 novelty，不自动建议创建实现仓库。

## 主工作流

### 1. 情报收集

```powershell
python scripts/collect_weekly.py --topic all
```

主要查看：

```text
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

Windows 本地也可以直接双击仓库根目录的 `启动研究面板.bat`。

它只读写统一数据文件 `data/items.jsonl`，并同步更新：

```text
outputs/review_dashboard.md
```

如果本地暂时没有安装 Streamlit，也可以先打开 `outputs/review_dashboard.md` 做人工浏览。

GUI 里也可以直接运行情报收集、扫描本地 PDF、批量读取 PDF、处理 `needs_topic_review` 条目。自动收集在 GitHub Actions 中也有定时任务；本地按钮主要用于临时补跑。`复核条目` 会把论文、标准、政策、报告和产业信号放在一起处理，但每张卡片都会明确显示所属数据库和具体类型。`论文数据库` 只查询 paper；`社会数据库` 只查询 standard / policy / report / whitepaper / industry / news，并按文档可用性区分 direct PDF、网页正文、门户页、目录/付费入口和新闻门户。推荐顺序是：情报收集 -> 复核条目 -> Topic 审核 -> 批量读 PDF -> Topic Workspace -> 论文数据库 / 社会数据库。

每个条目卡片里的 `编辑 metadata` 可以直接修改数据库字段，包括 title、year、venue、publisher、authors、DOI、URL、source type 和 abstract/snippet。保存后会重算 `authority`；如果该条目已有 note 或本地 PDF，文件名会按当前 metadata 同步更新。

### 3. 读取单个 PDF

```powershell
python scripts/read_item.py "literature/inbox/papers/example.pdf"
```

默认 `--topic auto`。脚本会先尝试根据 PDF 标题和短文本匹配已有 topic；匹配不可靠时保留为 `needs_topic_review`，你可以先生成 note，再在 GUI 的 Topic 审核里根据 note 划分 topic。已经确定 topic 时仍可显式指定，例如 `--topic remote_id`。

输出：

```text
notes/items/【人工中文注释】-年份-来源-题目-标识id.md
```

`【人工中文注释】` 是可选前缀；当前可在 item metadata 中使用 `human_annotation_zh`、`title_annotation_zh`、`annotation_zh` 或 `note_annotation_zh`。脚本会使用 metadata 中的 year、venue/publisher/source、title 和 item id 生成文件名。本地 PDF 也会在读取后改成同一 stem，只保留 `.pdf` 后缀。若你后来手动改了 PDF 文件名，再次运行 `read_item.py` 或批量扫描时会用 PDF 指纹找到已有条目，并把 PDF 与 note 名称重新同步到规范格式。

如果 PDF 文件名以 `【中文注释】` 开头，脚本会把该注释写入 item metadata，并在后续命名中保留。Kimi/LLM note 的 `元数据` 段会被保守回填到 `data/items.jsonl`；这些字段会标记 `llm_metadata_needs_review=true`，需要人工复核后再在 GUI 中保存为 `verified`。

阅读笔记默认用中文。少量机器标签保留英文，例如：

- `paper-supported`
- `inferred`
- `proposal`
- `unsupported`
- `metadata only`
- `abstract only`
- `full-text parsed`
- `needs-review`

这些标签用于保持证据边界清晰。

如果一次放入多篇 PDF，可以先预览：

```powershell
python scripts/batch_read_pdfs.py --pdf-dir literature/inbox/papers --topic auto --dry-run
```

再小批量读取：

```powershell
python scripts/batch_read_pdfs.py --pdf-dir literature/inbox/papers --topic auto --max-items 3
```

批量读取会跳过已经生成过 note 的 PDF，并在跳过时同步 PDF/note 文件名。无法可靠归入现有 topic 的条目会进入 `needs_topic_review`，需要在 GUI 中审批到已有 topic 或新候选 topic。

若标题、来源或年份包含 Windows 不允许的文件名字符，脚本会自动替换；item id 是规范文件名的一部分，用于避免重名覆盖。

### 4. Topic Workspace

日常研究讨论优先使用 Streamlit 的 `Topic Workspace` tab。它会基于某个 topic 下已有 note 和社会数据库线索生成并维护：

```text
topics/<topic>/research_workspace.md
```

这个页面用于记录：

- `paper-supported`：已读来源明确支持的内容；
- `inferred`：多条来源之间的谨慎归纳；
- `proposal`：可能的论文 idea，必须写成问题形式；
- `unsupported` / `needs-review`：尚未被材料支持或仍需核验的信息。

Topic Workspace 是多轮讨论草稿，不是最终研究方向或 novelty claim。

### 5. 按需 topic synthesis

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
unread -> noted -> used_in_synthesis
```

其中：

```text
review_status：由你在 GUI 中点击决定，可以随时反复修改
process_status：由自动流程维护；只要生成了 note 就标记 noted，topic synthesis 使用后标记 used_in_synthesis
```

阅读模式和状态语义：

- `metadata-only`：只登记 metadata 和 PDF 指纹，`reading_status=metadata_only`，不生成 note。
- `text-draft`：用 pypdf 抽取文本并生成待复核草稿，`reading_status=text_extracted`，`summary_status=text-draft`，`visual_status=not_parsed`。长文本只写入 `.local/pdf_text_cache/`，不会进入提交区 note。
- `kimi`：上传 PDF 给 Kimi/Moonshot 生成结构化中文笔记，`reading_status=model_parsed_pdf`，`summary_status=summarized`。

`read` 和 `summarized` 不再作为流程层状态区分；二者都属于 `noted`。是否只是文本草稿、是否 Kimi 精读，看 metadata 里的 `reading_status` / `reading_mode` / `summary_status`。

成本控制建议：

- 先跑 `metadata-only` 或 `text-draft`，只对确实值得精读的 PDF 使用 `kimi`。
- Kimi 模式会把 PDF 提取内容作为上下文提交，长综述、长参考文献、扫描件 OCR 噪声都会显著增加 token；当前详细笔记要求也会增加输出 token。
- 对低相关或只是背景材料的文献，优先保留 `text-draft` 或只做 metadata，不必全部精读。
- 每次批量读取前使用 `--dry-run`，并用 `--max-items` 控制批量规模。

GUI 默认只暴露 `review_status` 的三个按钮，避免误把已经读过或综合过的条目改回普通状态。如果确实要人工修改 `process_status`，需要展开条目中的“危险操作：手动修改流程状态”，勾选确认后才能覆盖。

状态记录在 `data/items.jsonl` 中。本地 Streamlit 面板用于日常标记；`outputs/review_dashboard.md` 用作无需安装依赖时的轻量 review 面板。

每篇 note 的 `后续建议` 会进入 item metadata 的 `follow_up_actions` 列表。每条建议有 `open` / `done` / `skipped` 状态；GUI 条目卡片里可以逐条标记，默认收起，`outputs/review_dashboard.md` 会集中列出 `后续建议待处理`。

GUI 按钮含义：

- `Keep`：保留观察，后续可能下载或阅读。
- `Reject`：暂不关注，不进入后续阅读队列。
- `Downloaded`：PDF 已经合法下载到本地，等待后续读取。

`relevance` 是自动相关性粗分，不是论文质量分，也不是创新性判断。当前主要根据 topic 查询文件里的 `required_terms_any` 命中数量计算，最高 5 分；如果命中排除词则不会进入候选条目。这个分数只用于决定优先 review 顺序。

`authority` 是来源权威性粗分，也不是最终质量判断。当前根据 venue、publisher、source_type、URL 等启发式估计来源可信度：IEEE Transactions、ACM Transactions、Nature / Science family、标准、政策、政府或权威技术报告会更高；预印本、来源不明、小型新闻或混合置信出版源会更低。这个分数需要人工复核，不能单独支撑研究判断。

## 数据边界

可以进入仓库：

- `data/items.jsonl`
- 中文阅读笔记
- topic workspace / synthesis / open questions / possible directions
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

下载到本地的社会数据库原文按类型临时放在：

```text
literature/inbox/social/standards/
literature/inbox/social/policies/
literature/inbox/social/reports/
literature/inbox/social/industry/
literature/inbox/social/news/
```

这些 inbox 目录默认不提交原文文件，只保留 `.gitkeep`。标准、政策、报告、产业信号和新闻的长期记录仍以 `data/items.jsonl` metadata、URL、中文 note 和 synthesis 输出为主，避免把受版权或时效限制的全文材料放进仓库。

topic 字段现在按兼容方式处理：`topic` 是主标签，`topics` 是多标签列表。GUI 中每个条目卡片都会直接显示 topic 编辑区，可以修改主 topic，也可以用逗号、空格或换行添加/删除多个 topic。topic synthesis 会按 `item.topic == X or X in item.topics` 选取 note，因此一篇论文、一份标准或一条社会信号可以被多个方向共同引用。

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
