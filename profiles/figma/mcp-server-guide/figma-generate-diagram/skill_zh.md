# generate-diagram

**您必须在每次调用 `generate_diagram` 工具之前加载此技能。** 跳过它会导致可预防的渲染失败和低质量输出。

`generate_diagram` 接收 Mermaid.js 语法并生成可编辑的 FigJam 图表。此技能将您引导至正确的类型指导，并设置通用约束。

## 第 1 步：`generate_diagram` 是否是正确的工具？

### 支持的图表类型

`flowchart`, `sequenceDiagram`, `stateDiagram` / `stateDiagram-v2`, `gantt`, `erDiagram`。

### 不支持 — 不要调用该工具

如果用户需要以下任何类型，请直接告诉他们 `generate_diagram` 不支持，而不是调用工具并失败：
- **饼图、思维导图、维恩图、类图、旅程图、时间线、象限图、C4、git 图、需求图**

### 何时建议用户在 Figma 中编辑

该工具无法：
- 更改现有图表的字体
- 移动单个形状
- 生成后逐节点编辑图表

如果用户需要在现有图表上请求任何这些操作，建议他们在 Figma 中打开图表进行编辑。对于内容级别的更改，通常重新生成更快。

## 第 2 步：选择图表类型

轻量级路由 — 使用第一个匹配项。

| 用户需要… | 类型 | 下一步 |
|---|---|---|
| 服务 + 数据存储 + 队列 + 集成 | **架构流程图** | 阅读 [references/architecture.md](./references/architecture.md) |
| 决策树、流程图、管道、依赖图、用户旅程 | **流程图** | 阅读 [references/flowchart.md](./references/flowchart.md) |
| 各方随时间交互（API 调用、认证、消息传递） | **序列图** | 阅读 [references/sequence.md](./references/sequence.md) |
| 数据模型、表、键、基数 | **ER 图** | 阅读 [references/erd.md](./references/erd.md) |
| 命名状态及其之间的转换 | **状态图** | 阅读 [references/state.md](./references/state.md) |
| 项目进度（带日期、里程碑） | **甘特图** | 阅读 [references/gantt.md](./references/gantt.md) |

如果请求流程图且描述的是软件基础设施（服务、数据存储、队列、外部集成），则路由到 `architecture.md` — 而不是 `flowchart.md`。如有疑问，请询问用户。

## 第 3 步：通用约束（适用于所有图表类型）

1. **Mermaid 源代码的任何部分都不能包含表情符号**。该工具会拒绝它们。
2. **标签中不能包含 `\n`**。仅在绝对必要时使用换行，并且只能通过实际换行（而不是转义序列）来实现。
3. **标签中不能包含 HTML 标签**。
4. **保留字** — 不要将 `end`、`subgraph`、`graph` 用作节点 ID。
5. **节点 ID**：camelCase（`userService`），不要有空格。下划线可能会在某些处理器中破坏边缘路由。
6. **标签中的特殊字符** 必须用引号括起来：`A["处理 (主)"]`，`-->|"O(1) 查找"|`。
7. **序列图** — Mermaid 的 `Note over X` / `Note left of X` / `Note right of X` 会被渲染器静默移除；不要将它们放入源代码中。如果用户希望在序列图中添加注释，请先生成基础图表，然后通过混合工作流（[references/workflow.md](references/workflow.md)）添加便签/文本。
8. **甘特图** — `classDef`、`class` 和任何其他样式都会被预处理移除；渲染的图表将不会显示颜色。如果用户希望对阶段、里程碑或任务进行颜色编码，请先生成基础图表，然后通过混合工作流（[references/workflow.md](references/workflow.md)）添加颜色/注释 — 或者，对于根本需要样式的图表，直接使用 `use_figma` 构建（见 [references/gantt.md](references/gantt.md) §11）。
9. **在任何 `use_figma` 扩展中使用仅适用于 FigJam 的 API。** `generate_diagram` 输出将位于 FigJam 文件（`figma.com/board/...`）中，因此混合扩展必须坚持 FigJam 支持的 API。**不要调用 `figma.createPage()`** — 它仅适用于设计（`figma.com/design/...`），并且在 FigJam 中会抛出 `TypeError: figma.createPage no such property 'createPage' on the figma global object`。相反，请使用 FigJam 区域组织内容（见 [figma-use-figjam](../figma-use-figjam/SKILL.md)）。

## 第 4 步：输入垃圾，输出垃圾

生成的图表质量受限于您生成的 Mermaid 质量以及您拥有的上下文质量。在编写 Mermaid 之前，确保您有足够真实的信息来准确描述主题 — 并使用当前环境提供的一切来收集这些信息。

根据可用性，有用的上下文来源包括：

- **源代码** — 搜索/读取相关文件，以便图表反映真实的服务名称、真实的边缘标签、真实的数据存储、真实的入口点。实际路线/处理器/消费者比凭记忆重新创建更有效。
- **用户提供的文档** — PRD、规范、会议笔记、转录、研究总结、入职文档、流程说明。如果主题不是代码，请要求用户粘贴或附加。
- **现有的 Figma 或 FigJam 文件** — 如果新图表应与用户已有的图表对齐，请使用 `get_figjam` 或 `get_design_context` 读取（见 `figma-use` 和 `figma-use-figjam` 技能）。
- **其他可用的 MCP 服务器或工具** — 问题跟踪器、文档站点、CRM、分析、内部维基、设计系统、数据库模式等。如果连接的工具包含您正在图表化主题的真实信息，请从中获取而不是猜测。
- **用户本人** — 当描述模糊或不确定时（流程方向不明确、范围不明确、哪些实体重要不明确），在生成之前问一两个有针对性的问题。示例： "有哪些 3-5 个主要步骤？"、"每个步骤由谁负责？"、"什么触发了下一步？"。一个好问题胜过浪费的图表。

不要为了"完善"图表而编造边缘、标签或实体。缺失信息比幻觉信息更好 — 留下空白并标记给用户。

## 第 5 步：图表是否需要 Mermaid 无法表达的内容？

Mermaid 并非万能。与特定节点关联的便签注释、ERD 上的每节点域着色、带附加数据的标注 — 这些都需要通过 `use_figma`（通过 [figma-use-figjam](../figma-use-figjam/SKILL.md) 技能）组合 `generate_diagram`。这是**混合工作流**。

这是一个判断，不是默认行为。在用户的需求明确受益时部署它 — 当基础图表明显足够时跳过它。表明肯定的信号：用户明确要求便签、颜色、标注或"每个节点都附加 X"；他们分享了映射到特定节点的数据；图表是一个可共享的工件，而不是一个思考草图。表明否定的信号：简短/易懂的请求、小图表、用户在探索或测试。

**如果混合是合理的，在调用 `generate_diagram` 之前阅读 [references/workflow.md](./references/workflow.md)** — 它涵盖了模式、两个核心配方（注释 + 着色）、沟通风格和失败处理。如果不适用，直接进行第 6 步。

## 第 6 步：调用工具

必需：
- `name`：一个描述性的标题（显示给用户）
- `mermaidSyntax`：Mermaid 源代码

可选：
- `userIntent`：一个简短的句子描述用户试图完成的目标 — 有助于遥测和下游调整
- `useArchitectureLayoutCode`：**仅用于架构图表**；值在 `references/architecture.md` 中指定
- `fileKey`：如果用户希望图表添加到现有 FigJam 文件而不是新文件

**在 `generate_diagram` 之前不要调用 `create_new_file`** — 该工具会创建自己的文件。

## 第 7 步：生成后

- 该工具会返回一个链接（或小部件），用户可以点击以在 FigJam 中打开图表。除非客户端渲染内联小部件，否则将其显示为 Markdown 链接。
- 如果需要扩展（见第 5 步），现在与 `use_figma` 组合 — 模式和配方在 [references/workflow.md](./references/workflow.md) 中。
- 如果用户在两次尝试同一图表后仍不满意，停止重新生成。询问具体问题是什么，或者建议他们在 Figma 中手动编辑而不是浪费更多工具调用。

### 迭代或添加相关图表时重用同一文件

每次调用 `generate_diagram` 而没有 `fileKey` 都会在用户的草稿中创建一个新的 FigJam 文件。重新生成 4 次=4 个草稿文件需要清理。当以下情况发生时，请优先重用现有文件：

- 用户正在迭代同一图表（"再试一次…"、"更改标签…"）。
- 用户希望添加一个与第一个图表并排的后续图表（例如，同一系统的序列图旁边是流程图）。

如何重用：

1. **在后续 `generate_diagram` 调用中传递 `fileKey`**。从 `figma.com/board/{fileKey}/...` URL 中提取。图表将添加到现有文件而不是创建新文件。
2. 如果您希望替换之前的图表而不是将其添加到旁边，请使用 `use_figma` 工具（见 `figma-use-figjam` 技能）首先删除旧图表的节点，然后调用具有相同 `fileKey` 的 `generate_diagram`。或者保留旧图表并将新图表放在旁边 — 读者通常能从看到尝试历史中受益。

第一次迭代时询问用户他们更喜欢哪种方式 — "在旧图表上重新生成，还是并排保留两者？" — 并记住他们对后续迭代的会话中的答案。
