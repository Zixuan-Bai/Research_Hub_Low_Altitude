# Automation Workflow

本仓库的自动化目标是：默认让机器收集和初筛，人工只处理关键 gate。

## Human Gate 最小化

你不需要逐篇手工标注所有字段。

自动处理：

- metadata search；
- candidate dedup；
- initial `venue_tier`；
- initial `source_trust`；
- initial `practical_relevance`；
- acquisition queue；
- review queue；
- GitHub Actions validation。

人工只处理：

- 受限 PDF 是否下载；
- review queue 中高价值或高风险条目；
- practical context 是否足够；
- topic synthesis 是否可信；
- route card 是否进入下一阶段。

## 两个本地入口

发现候选论文和后续阅读不要混在一个脚本里。

常态化发现入口：

```powershell
python scripts/run_discovery_pipeline.py --topic all --write-digest
```

候选 PDF 下载后的阅读入口：

```powershell
python scripts/run_reading_pipeline.py --topic remote_id
```

旧入口 `python scripts/run_pipeline.py` 仍然保留，但只是 discovery pipeline 的兼容包装。

## 本地一键运行

默认跑所有 topic，不下载 PDF：

```powershell
python scripts/run_discovery_pipeline.py
```

只跑某个 topic：

```powershell
python scripts/run_discovery_pipeline.py --topic remote_id
```

先看会执行什么：

```powershell
python scripts/run_discovery_pipeline.py --dry-run
```

如果想尝试下载 open-access PDFs：

```powershell
python scripts/run_discovery_pipeline.py --topic remote_id --download-pdfs
```

下载 PDF 后，运行：

```powershell
python scripts/run_reading_pipeline.py --topic remote_id
```

如果没有 `OPENAI_API_KEY`，阅读脚本只会把任务加入 review queue，不会伪造阅读结果。

## 你主要看哪个文件

优先看：

```text
literature/database/review_queue.csv
```

它会告诉你哪些条目需要人工处理，例如：

- venue tier unknown；
- missing practical validation；
- PDF requires user access；
- low source trust。

不要从 `paper_candidates.csv` 逐篇开始看。先看 review queue。

## GitHub Actions 自动运行

`.github/workflows/literature_pipeline.yml` 可以手动触发，也可以每周定时运行。

它会：

1. 运行 `scripts/run_discovery_pipeline.py --write-digest`；
2. 如果 CSV 有变化，创建一个自动化分支；
3. 提交变化；
4. 尝试创建 PR。

PR 是让你 review 的地方。你只需要看差异和 `review_queue.csv`。

## Codex 托管使用方式

Codex 不应该替代 deterministic pipeline。推荐分工：

- GitHub Actions：无人值守跑脚本，产生候选表和 review queue。
- Codex Cloud：读取 PR diff、review queue、paper candidates，给出筛选建议或改进脚本。
- Local Codex：处理需要本地 PDF、私有文件、人工判断的任务。

Codex Cloud 任务提示示例：

```text
Read AGENTS.md, docs/workflow.md, and docs/automation_workflow.md.
Inspect literature/database/review_queue.csv and paper_candidates.csv.
Summarize which candidates need human attention, which look high-value, and which need practical context.
Do not invent paper claims. Do not create route cards yet.
```

另一个提示：

```text
Run the validation scripts and inspect the latest automated literature pipeline PR.
If the pipeline produced low-quality candidates, improve query keywords or source-trust heuristics.
Keep changes small and open a PR.
```

## Notion 角色

不建议把 Notion 作为主数据库。GitHub repo 仍是 canonical source，Notion 是看板和 review surface。

推荐用途：

- 展示 `review_queue.csv`；
- 阅读计划；
- route card review board；
- 每周进展摘要。
- Download Queue；
- Reading Queue；
- Evidence Map Board。

主数据仍在 GitHub repo。Notion 只是看板。
