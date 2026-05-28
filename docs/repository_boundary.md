# Repository Boundary

本仓库只负责研究情报组织，不负责实验实现。

## Allowed

- 文献 metadata；
- BibTeX；
- paper notes；
- white paper / policy / standard / system metadata；
- context notes；
- survey notes；
- evidence maps；
- topic candidate cards；
- route cards；
- prompts；
- rubrics；
- workflow documentation；
- 轻量脚本骨架。

## Not Allowed

- 大 PDF；
- copyrighted full-text paper dumps；
- datasets；
- model checkpoints；
- long experiment logs；
- Level 1 simulator or algorithm implementation；
- 未经证据支撑的论文结论。

## Storage Policy

`literature/inbox/papers/` 可用于本地暂存 PDF，但默认不提交。

`literature/pdfs/open_access/` 可用于保存明确开放访问的 PDF。如需跨平台同步，建议使用 private repository 和 Git LFS，并保留来源 metadata。

受限或订阅来源 PDF 不应自动上传。相关条目应记录到 `literature/database/acquisition_queue.csv`，由用户自行确认合法获取方式。

`outputs/tmp/` 可用于脚本 dry-run 或临时输出，但默认不提交。

文献数据库只记录可核验 metadata。缺失字段保持为空，不做激进推断。

## Claim Policy

任何 claim 必须标记来源类型：

- `paper-supported`
- `inferred`
- `proposal`
- `unsupported`

如果 claim 暂时无法关联文献，它只能作为 open question 或 speculative idea 保留。

## Practical Context Policy

产业、政策、标准、白皮书和实际系统材料可以作为 route card 的重要 evidence，尤其用于约束系统性能指标、参数范围、部署可能性和实际需求。

这些材料不得替代学术严谨性，但可以防止研究路线只由学术热点驱动。
