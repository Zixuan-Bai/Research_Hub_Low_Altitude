# MCP and Skill Roadmap

本文件记录未来可能接入的 MCP 和 skill。第一版 hub 不实现这些集成，只保留设计入口。

## Phase 0: Local Skeleton

当前阶段只使用本地 Markdown、YAML、CSV 和 dry-run 脚本。

目标：

- 稳定目录结构；
- 固化 evidence-first 工作流；
- 建立 prompts 和 rubrics；
- 避免在工具链未稳定时过早自动化。

## Phase 1: Literature Sources

当前先用 repo scripts，不强制安装 MCP：

- Semantic Scholar / Crossref / OpenAlex metadata search；
- arXiv search；
- IEEE/ACM 手动导出结果导入；
- Zotero collection export。

原则：

- 自动工具只能导入 metadata；
- DOI、venue、year 必须来自可核验 source；
- 不自动生成 novelty claim。

当前已提供：

- `scripts/run_discovery_pipeline.py`
- `scripts/run_reading_pipeline.py`
- `scripts/classify_candidates.py`
- `scripts/search_literature.py`
- `scripts/fetch_open_access_pdfs.py`
- `literature/database/paper_candidates.csv`
- `literature/database/acquisition_queue.csv`
- `literature/database/review_queue.csv`

## Phase 2: PDF and Note Workflow

候选能力：

- local PDF text extraction；
- OCR fallback；
- paper note generation；
- citation key normalization。

原则：

- 未解析全文时只能标记 `metadata only` 或 `abstract only`；
- full-text parsed 不等于 human reviewed；
- 摘要、结论、数字结果必须可追溯到原文。

## Phase 3: Knowledge Capture

候选能力：

- Notion / Obsidian / local markdown sync；
- route card review board；
- weekly research report generation。

原则：

- 本仓库仍是 canonical source；
- 外部工具只作为展示、检索或协作界面。

## Phase 4: Level 1 Repository Creation

候选能力：

- GitHub repository bootstrap；
- experiment reproducibility template；
- baseline checklist；
- result logging scaffold。

触发条件：

- route card 通过 rubric；
- human review 通过；
- repository proposal 已完成。

## Practical Recommendation

短期优先级：

1. GitHub private repository + GitHub Actions validate；
2. OpenAlex / Crossref / arXiv metadata scripts；
3. Zotero MCP；
4. Notion MCP；
5. Level 1 repository bootstrap tooling。

MCP 是运行时工具，不是仓库内容。API key、token、secret 不应提交到 GitHub。
