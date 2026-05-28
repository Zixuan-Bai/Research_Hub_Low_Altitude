# Low-Altitude Research Hub

本仓库是一个 **Level 0 research-intelligence hub**，用于低空通信与自主无人机系统方向的文献管理、选题侦察、证据整理和路线评估。

它不是实验实现仓库，不承载模型训练、仿真日志、数据集、checkpoint 或论文结论。只有当某个路线卡经过文献证据、可行性和人工审查后，才考虑创建单独的 Level 1 implementation repository。

## 当前目标

第一阶段目标是建立一个轻量、可持续扩展的研究工作台：

1. 收集和标注文献候选项；
2. 为论文生成结构化阅读笔记；
3. 为研究方向维护 evidence map 和 open questions；
4. 生成 route card；
5. 用 rubric 评估 route feasibility；
6. 决定是否值得进入单独实现仓库。

## 初始候选方向

当前只把下列方向作为候选，不默认任何方向已经具备新颖性或可实现性：

- UAV broadcast capacity / Remote ID-like broadcast systems
- DTMB-based or terrestrial-broadcast-based UAV management
- Autonomous UAV formation safety and stability boundaries
- Dynamic directional networking for aerial networks

候选方向卡位于 `topics/candidates/`。每个方向卡只记录问题空间、检索入口、与既有研究基础的可能连接和待验证问题。

## 工作流

推荐工作流见 `docs/workflow.md`：

```text
literature search
-> paper note
-> evidence map
-> topic synthesis
-> route card
-> route review
-> repository proposal only if approved
```

所有研究判断都必须区分：

- paper-supported evidence；
- inference from multiple papers；
- personal proposal / speculation。

形成研究方向时还必须参考 practical context，包括 industrial systems、standards、white papers、policy documents、regulatory news 和 deployment roadmaps。高水平文献优先，低置信论文和纯概念方向不得单独支撑 route card。

## 仓库边界

仓库应该保存：

- metadata、BibTeX、候选文献表；
- white paper / policy / standard / system metadata；
- paper notes、survey notes、evidence maps；
- topic candidate cards、route cards；
- prompts、rubrics、workflow docs；
- 轻量脚本骨架。

仓库不应该保存：

- 大 PDF 或 copyrighted full-text dumps；
- datasets、checkpoints、长日志；
- 未经证据支持的论文结论；
- Level 1 实验实现代码。

更多边界规则见 `docs/repository_boundary.md`。

## 可运行检查

推荐的一键流程：

```powershell
python scripts/run_pipeline.py --dry-run
python scripts/run_pipeline.py
```

基础检查：

```powershell
python scripts/validate_hub.py
python scripts/search_literature.py --query-file literature/queries/remote_id.yaml --dry-run
python scripts/fetch_open_access_pdfs.py --dry-run
python scripts/import_local_pdfs.py --dry-run
python scripts/rank_routes.py --dry-run
```

这些脚本不会进行真实文献搜索，不会解析全文，也不会生成科学结论。

自动化使用说明见 `docs/automation_workflow.md`。

## 工具说明

初学 MCP 和 skill 时先读 `docs/tooling_guide.md`。

短期建议先使用 repo scripts 和 GitHub Actions。MCP 只在需要 Zotero、Notion 或其他外部知识库时再接入。
