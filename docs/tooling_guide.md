# Tooling Guide for Codex, MCP, and Skills

本文面向暂时不了解 MCP / skill 的使用者，说明本仓库的自动化应该如何逐步建设。

## 1. 三类工具的区别

### Repo Scripts

保存在本仓库 `scripts/` 下，可由你、Codex、GitHub Actions 在任何机器上运行。

适合：

- validate hub structure；
- search literature metadata；
- download open-access PDFs；
- import local PDFs；
- record practical context sources；
- generate route-card completeness checks。
- run the unattended pipeline and generate a compact review queue.

这是最应该优先建设的部分，因为它可复现、可审查、可提交到 GitHub。

### Skills

Skill 是 Codex 的工作说明书，告诉 Codex 遇到某类任务时应该怎么做。

适合：

- paper reading workflow；
- route review workflow；
- GitHub PR / issue workflow；
- LaTeX / document / spreadsheet generation。

Skill 本身不一定连接外部服务。它更多是“操作规程”。

### MCP Servers

MCP 是 Codex 运行时连接外部工具或数据源的方式。

适合：

- Zotero library；
- Notion database；
- local browser automation；
- specialized paper search API；
- policy / standard / industry knowledge bases；
- private knowledge base。

MCP 配置通常属于本地运行环境，不应把 API key 或 secret 放进仓库。

## 2. 当前阶段需要什么

第一阶段不强制安装 MCP。先让本地脚本跑通：

```powershell
python scripts/validate_hub.py
python scripts/run_pipeline.py --dry-run
python scripts/search_literature.py --query-file literature/queries/remote_id.yaml --dry-run
python scripts/fetch_open_access_pdfs.py --dry-run
python scripts/import_local_pdfs.py --dry-run
python scripts/rank_routes.py --dry-run
```

如果这些流程稳定，再接 MCP。

当前阶段的核心规则是：先建立 source-quality-first 和 practical-context-first 的 repo 流程，再扩大自动化范围。

日常使用优先运行 `python scripts/run_pipeline.py`，不要逐个脚本手动执行。

现在推荐把日常流程拆成两个入口：

```powershell
python scripts/run_discovery_pipeline.py --topic all --write-digest
python scripts/run_reading_pipeline.py --topic remote_id
```

`run_pipeline.py` 只是 discovery pipeline 的兼容包装。

## 3. 推荐接入顺序

### Step 1: GitHub

用途：

- push private repository；
- issue/task tracking；
- GitHub Actions 定时或手动运行 validate/search；
- 多平台同步 Markdown、CSV、open-access PDFs。

建议：

- 先私有仓库；
- PDF 默认不提交；
- open-access PDFs 可考虑 Git LFS；
- 受限 PDF 只进入 acquisition queue，不自动上传。

### Step 2: Paper Metadata Sources

优先用脚本访问公开 metadata API：

- OpenAlex；
- Crossref；
- arXiv。

这些不一定需要 MCP。脚本更可复现。

脚本只提供初始 metadata。venue tier、source trust、practical relevance 仍需要人工或后续专门工具确认。

### Step 3: Zotero MCP

适合你已经在 Zotero 中维护文献库时使用。

用途：

- 从 Zotero collection 导入 metadata；
- 对齐 citation key；
- 管理本地 PDF 路径。

注意：

- Zotero 里的受限 PDF 不应默认上传 GitHub；
- 只同步 metadata 和笔记更稳妥。
- v1 中先把 Zotero 当作人工下载和 PDF 管理界面；脚本可从 `literature/inbox/papers/` 和 `literature/pdfs/open_access/` 读取 PDF。

### Step 4: Notion MCP

适合把路线卡、阅读计划、人工审查状态同步到看板。

注意：

- 本仓库仍作为 canonical source；
- Notion 只作为展示和任务管理界面。
- 推荐视图：Paper Inbox、Download Queue、Reading Queue、Evidence Map Board、Route Review Board。
- CSV 是底层可复现数据，不应成为日常人工操作界面。

### Step 5: OpenAI Multimodal PDF Reading

用途：

- 读取完整 PDF；
- 覆盖正文、图表、系统架构图、实验曲线和参数表；
- 生成 paper notes、figure/table notes、claims ledger、evidence map、topic brief 和 route card draft。

运行：

```powershell
python scripts/run_reading_pipeline.py --topic remote_id
```

需要：

```powershell
$env:OPENAI_API_KEY="..."
```

不要把 API key 写入仓库。

## 4. Codex 如何持续工作

Codex 不会天然变成后台常驻服务。要持续自动化，需要把动作固化为脚本和工作流：

1. 你在本地或 VS Code 中让 Codex 执行脚本；
2. GitHub Actions 在 push、手动触发或 schedule 时执行脚本；
3. Codex 每次进入仓库时读取 `AGENTS.md`、`README.md`、`docs/workflow.md`；
4. 研究状态写回 repo 文件，而不是只留在聊天记录。

## 5. 安全规则

- 不把 API key 写入仓库；
- 不自动下载或上传受限论文；
- 不自动生成 novelty claim；
- 不让低分区论文或单篇论文主导路线判断；
- 不绕过 practical context review；
- 不让 MCP 输出直接覆盖人工审查结论；
- 对所有外部 metadata 保留 source。
