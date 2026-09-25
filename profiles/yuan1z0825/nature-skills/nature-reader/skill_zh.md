# 全文 Markdown 阅读器 — 路由器

## 路由协议

首先区分创建阅读器与回答问题或翻译摘录。

对于源链接的问题，读取 `references/grounding-rules.md` 并仅检查相关源材料；在可用的情况下重用现有的源映射 ID。在回答问题之前，不要重新生成阅读器或要求完整的源映射。对于显式的摘录请求，将提取、翻译和 grounding 规则应用于该摘录。当用户请求阅读器或全文翻译时，适用以下完整工件工作流程。

对于新任务，加载以下核心和匹配资源。在后续任务中重用已加载的指导；仅在任务需要时加载更多。

### 1. 加载清单和核心层

读取 `[manifest.yaml](manifest.yaml)`。它声明了 `source_format` 轴、允许的值以及每个值映射到的文件路径。

还读取 `always_load` 下列出的每个文件。这些文件包含适用于每个阅读任务的核心原则、阅读工作流程和输出合同，以及用于构建重复术语表的共享术语账本。

### 2. 检测源格式

使用清单的 `detect:` 提示和用户输入决定 `source_format` 值：

- `pdf-text` — 可选择文本的 PDF。默认。
- `scanned-pdf` — 仅图像或需要 OCR 的 PDF。
- `html` — 出版商或预印本 HTML 页面。
- `doi-arxiv` — 必须首先解析的裸 DOI 或 arXiv 链接。
- `pasted-text` — 粘贴的散文或笔记，没有可检索的原始布局。

在处理之前，向用户声明检测到的值，以便他们可以廉价地纠正。源可能映射到多个值（例如解析为 PDF 的 DOI）；首先加载解析片段，然后加载解析工件的片段。

### 3. 加载匹配的片段

读取为检测到的 `source_format` 映射的文件。**不要**读取 `static/` 中的每个片段。仅加载步骤 2 选择的内容。

### 4. 使用加载的材料构建阅读器

按此优先级顺序应用加载的片段：

1. 核心原则 (`core/principles.md`) — 默认为双语阅读器，为意义而翻译，永不降级为摘要，版权警告。
2. 源格式片段 — 如何为该输入提取文本、图像和表格。
3. 阅读工作流程 (`core/workflow.md`) — 六步源映射优先过程。
4. 输出合同 (`core/output-contract.md`) — 必要文件和预响应验证清单。

在翻译时构建术语账本 (`../nature-shared/core/terminology-ledger.md`)；它成为 `paper.md` 重复术语表和 `source_map.json` 词汇表。

如果约束条件阻止完整处理，仍然创建草稿阅读器，并在 `translation_notes.md` 中标记缺失的页面、图像或低置信度的裁剪。不要切换到摘要模式。

### 5. 仅在需要时才查找参考文献

`references/` 下面的文件是深度参考文献，不是默认值。根据清单中的 `references.on_demand` 表格按需打开它们：

- 详细图像/表格裁剪和放置 → `references/figure-extraction.md`。
- `paper.md` / `source_map.json` 的确切字段模式 → `references/output-spec.md`。
- 方程式、数学表达式、化学公式或仅图像公式 → `references/equation-handling.md`。
- 使用源引用回答后续问题 → `references/grounding-rules.md`。
