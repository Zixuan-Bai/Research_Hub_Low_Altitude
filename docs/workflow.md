# Research Hub Workflow

本文件定义 Level 0 research-intelligence hub 的基本工作流。任何输出都应服务于选题判断，而不是直接形成论文结论。

## 1. 发现候选论文

优先从 query YAML 开始：

```powershell
python scripts/search_literature.py --query-file literature/queries/remote_id.yaml --dry-run
```

确认查询设置后，可以去掉 `--dry-run`。脚本会写入：

- `literature/database/paper_candidates.csv`
- `literature/database/acquisition_queue.csv`

候选表只表示“值得检查”，不表示论文已经读过，也不表示方向有创新性。

## 2. 获取 PDF

开放 PDF 可以用：

```powershell
python scripts/fetch_open_access_pdfs.py --dry-run
```

脚本只处理 `access_status=open` 且有 `pdf_url` 的候选项。

没有开放 PDF 的文献进入 `acquisition_queue.csv`。这表示需要你通过学校、机构、作者主页或合法个人访问手动下载。如果下载成功，将 PDF 放入 `literature/inbox/papers/`。

## 3. 添加本地 PDF

1. 将 PDF 放入 `literature/inbox/papers/`，该目录默认不提交。
2. 运行 `python scripts/import_local_pdfs.py --dry-run` 查看待登记文件。
3. 手动确认 metadata 后再写入 `literature/database/papers.csv`。
4. 不确定的字段必须留空或标为 `uncertain metadata`，禁止猜 DOI、venue、作者或年份。

## 4. 标记阅读状态

使用统一状态：

- `metadata only`
- `abstract only`
- `open PDF downloaded`
- `needs user PDF`
- `full-text parsed`
- `human reviewed`
- `uncertain metadata`

阅读状态只能反映实际读到的材料，不代表论文质量。

## 5. 创建 Paper Note

每篇论文使用 `literature/notes/paper_notes/template.md`。

笔记必须区分：

- `paper-supported`: 论文明确写出的内容；
- `inferred`: 由多篇论文比较得出的推断；
- `proposal`: 个人或 Codex 提出的延伸想法。

如果没有全文，不要写全文级总结。

## 6. 评估 Source Quality

每篇论文和每条非论文信息源都必须评估来源质量。

高优先级来源包括：

- IEEE Transactions / ACM Transactions；
- Nature / Science family；
- 顶级会议或领域公认强 venue；
- 标准组织文档；
- 政府/监管机构政策；
- 工业界白皮书、公开技术报告、实际系统文档。

低分区或弱审稿论文可以进入候选表，但在 synthesis 和 route card 中只能作为低置信证据，除非被其他高质量来源或实际系统证据支持。

## 7. 收集 Practical Context

在生成 route card 前，需要补充非论文信息源：

- white papers；
- standards；
- deployed systems；
- planned systems / industrial roadmaps；
- policy documents；
- regulatory news；
- system performance reports。

这些材料记录在 `literature/database/context_sources.csv`，必要时使用 `literature/notes/context_notes/template.md` 建立笔记。

目标不是追热点，而是防止只被论文中的假设或概念牵引。

## 8. 构建 Evidence Map

Evidence map 用于把 claim 和 supporting papers 绑定起来。

每条 claim 至少记录：

- 支持论文；
- 支持的非论文信息源；
- evidence type；
- evidence strength；
- source quality；
- practical relevance；
- 不确定性和缺口。

没有文献支撑的想法放入 `Unsupported or Speculative Ideas`，不能混入已验证结论。

## 9. 综合 Topic

topic synthesis 应从 paper notes 和 evidence map 出发，回答：

1. 该方向研究什么；
2. 已有方法和模型是什么；
3. 常见假设是什么；
4. 仍然缺什么；
5. 与低空通信的关系是什么；
6. 与用户既有基础的连接是什么；
7. 高质量文献是否支持该方向；
8. 产业、政策、标准或实际系统是否支持该方向；
9. 哪些 route card 值得生成。

不要因为方向有趣就假设它有创新性。

## 10. 生成 Route Card

route card 必须列出 supporting literature、practical context、gap、minimal model、possible method、expected evidence、baseline、risk 和 decision。

如果 supporting literature 或 practical context 不足，decision 应为 `watch` 或 `reject`，不能建议创建实现仓库。

## 11. 决定是否创建 Level 1 Repository

只有同时满足以下条件，才可提出 repository proposal：

1. clear research question；
2. 至少 10 篇相关候选论文；
3. 至少一部分核心 evidence 来自高质量来源；
4. gap 由文献比较和 practical context 共同支持；
5. minimal mathematical or simulation model 清晰；
6. baselines 可获得或可构造；
7. expected evidence 明确；
8. implementation risk 可控；
9. 人工确认该方向值得推进。

## 12. Human Review Points

以下节点需要人工审查：

1. 候选文献列表完成后；
2. paper notes 生成后；
3. source quality 和 venue tier 标注后；
4. practical context 收集后；
5. topic brief 被视为可靠前；
6. research gap 被接受前；
7. route card 排名前；
8. 创建 Level 1 repository 前；
9. 任何 manuscript claim 写入前。
