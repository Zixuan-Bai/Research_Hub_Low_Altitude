# 外部工具路线

当前阶段不接入复杂外部系统。先把核心主线做稳定：

1. `collect_weekly.py`
2. `read_item.py`
3. `synthesize_topic.py`
4. `outputs/review_dashboard.md`

可后置考虑：

- Streamlit：作为本地 review UI；
- Notion：只做 repo state 的镜像，不做 canonical database；
- Zotero：作为人工 PDF 管理和引用管理工具；
- Obsidian：阅读长期 Markdown 笔记。

在核心流程好用之前，不新增深度集成。
