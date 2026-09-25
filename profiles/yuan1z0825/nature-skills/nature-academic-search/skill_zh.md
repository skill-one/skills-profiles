# 学术搜索 — 路由

## 路由协议

对于需要完整记录的本地引文文件转换，直接加载 `references/workflows/wf4-citation-file-mgmt.md` 及其格式参考。源查找、API 设置和网络预检仅在需要检索或验证时适用；不适用于请求的离线转换。

对于新任务，加载以下核心和匹配资源。重用已加载的指导进行后续操作；仅在任务需要时才加载更多内容。

### 1. 加载清单和核心层

读取 [manifest.yaml](manifest.yaml)。它声明了 `workflow` 轴、允许的值以及每个值映射到的文件路径。

还读取 `always_load` 下列出的每个文件：

- `static/core/tools.md` — MCP 工具清单（核心搜索、扩展搜索、PubMed 实用工具）和共享模块映射。
- `static/core/routing-and-ops.md` — T1→T2→T3 源路由快速指南、环境设置、错误处理和限制。

### 2. 检测工作流

将用户需求映射到一个或多个 `workflow` 值：

- `multi-source-search` — 跨多个来源查找文献。
- `citation-verification` — 验证从文档中提取的引文。
- `mesh-strategy` — 构建MeSH/PubMed搜索策略。
- `citation-file-mgmt` — 转换/管理 `.nbib`/`.ris`/`.bib` 文件。
- `reference-mgmt` — BibTeX、相关文章发现、ID转换。
- `strict-other-citation-impact-audit` — 确定严格的独立其他引文，构建文章级引文指标表，识别高知名度引文者（学院成员、院长/副校长、人才奖获得者、研究员、领域领导者），并提取他们如何引用目标论文。

一个组合请求（例如搜索然后导出）可能需要多个。在继续之前，用简短的一行声明检测到的工作流。

### 3. 加载匹配的工作流片段

读取每个检测到的工作流（在 `references/workflows/` 下映射的文件）。**不要**读取每个工作流。每个工作流文件链接到它需要的共享模块。

### 4. 使用加载的材料运行工作流

按以下顺序应用加载的材料：

1. 核心工具和路由 (`core/tools.md`, `core/routing-and-ops.md`) — 哪个MCP工具适用于哪个需求，以及源检索的T1→T2→T3回退链。
2. 工作流片段 — 它的特定步骤。
3. 按需加载的共享模块和脚本（去重、引文解析器、搜索策略、RIS/BibTeX格式、格式转换器）。

报告特定工具失败并继续使用剩余工具；当没有结果时扩展术语；如果脚本失败两次，则从MCP获取的元数据手动生成。

### 5. 仅在需要时查找参考

`references/`（和 `scripts/`）下的文件是深度参考，不是默认值。根据清单中的 `references.on_demand` 表按需打开它们 — 例如 `references/source-tiers.md` 用于完整的可靠性分类，`references/dedup-engine.md` / `references/citation-parser.md` / `references/search-strategy.md` / `references/ris-bibtex-format.md` 用于共享模块，以及 `scripts/academic_search.py`（无MCP回退发现搜索） / `scripts/format-converter.py` / `scripts/preflight.py` 用于工具。
