---
name: n8n-agents
description: 以正确的方式设计 n8n AI 代理。在构建或编辑任何 @n8n/n8n-nodes-langchain.* AI 节点时使用——无论是 AI 代理、LLM 链、文本分类器还是信息提取器——以及每当用户提及 AI 代理、带工具的 LLM、工具调用、$fromAI、系统提示、代理内存、sessionId、结构化/JSON 输出、输出解析器、RAG、向量存储、聊天助手/机器人或人机审核时。涵盖代理-链-分类器选择、模型/内存/工具/输出解析器插槽、工具名称/描述作为提示、带自动修复的结构化输出、内存、RAG、人机审核以及聊天拓扑结构。
---

# n8n 代理

n8n AI 代理节点（`@n8n/n8n-nodes-langchain.agent`）是一个多轮 LLM 驱动，包含模型、内存、工具和可选的输出解析器等子节点。这项技能是关于设计和围绕它们构建 LangChain 家族的**深入指南**。关于“代理在工作流中处于什么位置”的高层次概览，请参阅 **n8n-workflow-patterns** 的 `ai_agent_workflow.md` — 这项技能深入到*如何构建它*的下一层。

对于节点类型格式：在工作流 JSON 中，LangChain 节点使用长格式 `@n8n/n8n-nodes-langchain.*`（`.agent`、`.lmChatOpenAi`、`.memoryBufferWindow`、`.outputParserStructured`、`.toolWorkflow`、`.toolHttpRequest`、`.toolCode`）。当你调用 `get_node` / `validate_node` 时，使用**短格式**（`nodes-langchain.agent`）。有关格式规则，请参阅 **n8n-mcp-tools-expert**。

---

## 首先选择正确的节点

当任务是一次性分类或提取时使用代理是最常见的过度构建。在连接任何东西之前做出决定：

| 你需要… | 使用 | 为什么 |
|---|---|---|
| 调用工具、多轮推理或持内存 | **AI Agent** (`.agent`) | 完整循环：模型 + 工具 + 内存 + 可选解析器。当您希望标准化时，这也是一个很好的默认选项。 |
| 一次性文本输入→文本输出，无工具 | **Basic LLM Chain** (`.chainLlm`) | 无代理循环，更容易调试。仍然接受一个 `outputParserStructured` 子节点。 |
| 将自然语言输入路由到 N 个分支之一 | **Text Classifier** (`.textClassifier`) | 一个节点，N 个输出处理，下游直接连接到每个分支。不是代理 + 开关。 |
| 从自由文本中提取结构化字段 | **Information Extractor** (`.informationExtractor`) | 带有模式的专用于字段提取。 |
| 三向正/中/负分割 | **Sentiment Analysis** (`.sentimentAnalysis`) | 内置分支输出。 |
| 概括长文档 | **Summarization Chain** (`.chainSummarization`) | 内置的 map-reduce 摘要。 |
| 生成图像/音频/视频 | **提供者的原生单次调用节点** (OpenAI、Gemini、ElevenLabs…) | **永远不要将媒体生成包装在代理中** — 请参阅“二进制和代理边界”。 |

**Text Classifier 详情（代理 + 开关的反模式）：** 每个类别都需要**名称和描述**。模型根据描述路由，而不是名称 — 没有描述的类别会通过抛硬币被选中。设置 `options.enableAutoFixing: true` 以在边缘输入时提高鲁棒性。一个节点，N 个分支，搞定。选择一个“决定”然后一个“路由”的代理是两个节点加上提示模板，而 Text Classifier 可以原生完成。

Chat 模型节点（`.lmChatOpenAi`、`.lmChatAnthropic`、`.lmChatOpenRouter`、…）是**子节点** — 它们不能独立运行。它们通过 `ai_languageModel` 连接线连接到链、代理、分类器或提取器。

---

## 子节点模式

代理有一个**主输入**（提示/用户消息）和最多四个**子节点插槽**，每个插槽通过其自己的 `ai_*` 连接类型连接：

| 插槽 | 连接类型 | 是否必需 | 节点示例 |
|---|---|---|---|
| **模型** | `ai_languageModel` | 是 | `.lmChatOpenAi`、`.lmChatAnthropic`、`.lmChatOpenRouter` |
| **内存** | `ai_memory` | 可选 | `.memoryBufferWindow`、`.memoryPostgresChat` |
| **工具** | `ai_tool` | 可选（但代理的要点） | `slackTool`、`.toolWorkflow`、`.toolHttpRequest`、`.toolCode` |
| **输出解析器** | `ai_outputParser` | 可选 | `.outputParserStructured` |

子节点从自身连接到代理。在工作流 JSON 中，连接存在于**子节点**上，按 `ai_*` 类型键入：

```json
"主 LLM": {
  "ai_languageModel": [[{ "node": "AI Agent", "type": "ai_languageModel", "index": 0 }]]
},
"简单内存": {
  "ai_memory": [[{ "node": "AI Agent", "type": "ai_memory", "index": 0 }]]
},
"搜索客户数据库": {
  "ai_tool": [[{ "node": "AI Agent", "type": "ai_tool", "index": 0 }]]
}
```

多个工具都连接到相同的 `ai_tool` index 0 — 它们堆叠，而不是分散到不同的索引。使用 `n8n_update_partial_workflow`，您可以使用 `addConnection` 操作将每个工具连接到 `sourceOutput: "ai_tool"`。代理将其最终答案放在 **`$json.output`**（不是 `.text`，不是 `.response`）— 下游节点读取 `{{ $json.output }}`。

有关完整的无状态代理核心节点对象片段，请参阅 **EXAMPLES.md**。

---

## 两个不可协商的要点

1. **工具名称和描述**是提示的一部分。模型通过读取工具的名称和描述来选择工具 — 没有其他内容。一个名为 `tool1` 且描述为空的工具对模型来说是不可见的：它跳过它、错误选择它或凭空想象参数。通常没有错误 — 只是代理“不会使用我的工具”。将两者都视为 API 设计。→ **TOOLS.md**
2. **结构化输出必须解析和 autoFix**。一个带有 `autoFix: true` 和**编码能力强的修复模型**的 `outputParserStructured` 是生产模式。如果没有 autoFix，一个格式错误的 JSON 响应会停止整个工作流。→ **STRUCTURED_OUTPUT.md**

---

## 强制默认值

- **每个工具的使用情况**放在工具描述中，而不是系统提示中。关于*如何调用这个特定工具*的任何内容都属于工具，因此它可以在代理之间传递，并使系统提示保持专注。→ **SYSTEM_PROMPT.md**
- **用于任何多步操作的工具子工作流（`.toolWorkflow`）**。任何工作流都成为具有类型 `$fromAI()` 输入的工具，并组合分支、错误处理和重用。当不确定时，这是默认选项。→ **SUBWORKFLOW_AS_TOOL.md** 和 **n8n-subworkflows**。
- **将具有用户可见副作用**的工具包装在人工审核中。发送、支付、退款、账户更改通过审批节点进行控制，以便人类在工具触发之前签字。→ **HUMAN_REVIEW.md**
- **提高 `maxIterations`**。默认工具调用限制**很低**（大多数版本上的个位数）— 对于一次使用工具的代理来说足够，但对于每次轮询都链式调用多个工具的代理来说太低了。它表现为“达到最大迭代次数”或空输出。将 `options.maxIterations` 设置为现实的上限（15 用于专注的子代理，50-200 用于广泛的协调器）。
- **通过 `{{ $now }}`（或 `{{ $now.format('DDDD') }}`）将当前日期放在系统提示中**。硬编码的日期立即过时。

---

## 四种工具类型

选择最轻的选项来完成工作：

| 工具类型 | 节点 | 使用场景 |
|---|---|---|
| **原生工具节点** | `slackTool`、`gmailTool`、`toolCalculator`、… | 功能映射到一个现有节点 + 一个操作。最低开销。 |
| **子工作流作为工具** | `.toolWorkflow` | 多于一个节点、可重用逻辑或您希望独立的可测试性。n8n 的规范方法 — **当不确定时使用**。 |
| **HTTP 请求工具** | `.toolHttpRequest` | 代理应直接协调的单个外部 HTTP API。重用服务预定义的凭证来覆盖原生节点未暴露的操作。 |
| **MCP 客户端工具** | `.mcpClientTool` | 一个已维护的 MCP 服务器已经涵盖了它，或者您希望一个发布的工作流为多个代理服务。 |

还有一个**自定义代码工具**（`.toolCode`）用于纯内联计算 — 但其运行时合同（字符串输入/字符串输出，没有 `$fromAI`，没有 `$helpers`）由 **n8n-code-tool** 技能拥有。在编写之前请阅读它。经验法则：如果您在代码中找到自己需要 `$fromAI()`，则应使用 `.toolWorkflow` 而不是。

**构建顺序：**
1. `action: "reference"` — 在任何其他操作之前，先读取配置模式以及精确的突变操作。
2. `action: "discover_assets"` — 列出代理实际可以连接的内容。需要 `projectId`（来自 `n8n_list_catalog({kind: "projects"})`）和 `kind`：`models`（带有 `provider`）、`integrations`、`workflows`、`subagents` 或 `mcpServers`。每种类型调用一次。
3. `action: "create"` — `projectId`、`name`、`config`。
4. `action: "mutate"` — 每次调用一个资源 (`config.patch`、`skill.upsert`/`delete`、`task.upsert`/`delete`、`customTool.upsert`/`delete`)，始终传递**最新**的哈希值。注意两个名称：n8n 返回它作为 `configHash`，并期望它作为 `args.baseConfigHash` 返回。`args` 被原封不动地传递给 n8n，因此任何字段名称的近似错误都会返回 `INVALID_ARGS`，而不是有帮助的纠正——这就是为什么步骤 1 先读取模式。一个过时的哈希值会返回 `STALE_CONFIG` — 重新 `get` 并使用最新的一次。
5. `action: "validate"` — 在提供 `call` 或 `publish` 之前。
6. `action: "publish"` — **仅在用户明确请求时**，从不主动。

`action: "call"` 使用真实凭证和真实工具运行代理——这是一个实时执行，不是干跑。一个结果可以携带 `approvals[]` 用于需要人工决策的工具调用；**永远不要代表用户批准**——展示它们，并在用户决定后再继续。

**自定义工具是第三个代码运行时——不要重用其他两个。** 一个 `customTool.upsert` 正文是 **TypeScript**，它可能使用的唯一导入是 `@n8n/agents` 和 `zod`。这不是代码节点（JavaScript/Python，返回 `[{json: …}]`）也不是由 **n8n-code-tool** 涵盖的 AI-agent 自定义代码工具（`@n8n/n8n-nodes-langchain.toolCode`，返回一个字符串，没有 `$fromAI()`）。这里容易犯的错误是抓错了合同，因为所有三个都是“代理调用代码”。在编写之前从 `action: "reference"` 读取形状；编译失败或未知的 `agentId` 会作为 `AGENT_TOOL_ERROR` 展现。

**凭证注意事项：** 在 n8n 2.36.x 中，代理运行时拒绝 `azureOpenAiApi` 和 `aws` 凭证（报告为 `missing: ["credential"]`）；响应的 `hint` 会命名接受的类型。

**不留下垃圾的测试：** 将一次性代理命名为 `[TEST] …` 并在用完后删除——一个持久的代理会超过创建它的对话，不像可以留置不动的流程。

→ **n8n-mcp-tools-expert** `## 代理` 用于工具的完整操作列表和错误代码。

---

## RAG（检索增强生成）

n8n 随附 LangChain RAG 基本原理（文档加载器、分割器、嵌入、向量存储、检索器）。有两个观点值得一开始就说明：

1. **首先排除更便宜的查找。** 精确查找 → 数据库或数据表查询，不是 RAG。新鲜度 → 活搜索工具。小型/结构化文档集 → 给代理列表/获取工具。只有在文档太多无法列出且查询是语义性的情况下才使用向量存储。
2. **将向量存储作为检索工具** (`mode: 'retrieve-as-tool'`，`ai_tool`)，以便代理决定何时检索并且可以自己措辞查询。使用**相同**的模型嵌入查询和文档。

→ **RAG.md**（故意保持简洁——默认值取决于数据形状和规模）。

---

## 参考文件

| 文件 | 读取时间 |
|---|---|
| **TOOLS.md** | 添加工具、在四种类型中选择、编写名称/描述、`$fromAI` 结构 |
| **SUBWORKFLOW_AS_TOOL.md** | 通过 `.toolWorkflow` 将子流程作为工具连接，映射代理填充与管道参数 |
| **SYSTEM_PROMPT.md** | 编写/重构系统提示，系统提示与工具描述的分离 |
| **STRUCTURED_OUTPUT.md** | 强制 JSON 输出，配置 autoFix、修正模型、解析失败修正 |
| **MEMORY.md** | 选择内存类型、持久化、sessionId 处理 |
| **HUMAN_REVIEW.md** | 添加人工批准、批准消息内容、多渠道批准者 |
| **CHAT_AGENT_PATTERNS.md** | 构建一个 Slack/Discord/Teams/Telegram 机器人，shell + 核心 + 子代理拓扑 |
| **RAG.md** | 检索增强代理（设计上较薄） |
| **EXAMPLES.md** | 具体的节点对象片段：无状态代理核心、Slack 路由器 shell、域子代理 |

---

## 反模式

| 反模式 | 出现问题 | 修复 |
|---|---|---|
| 通用工具名称 (`tool1`，`doStuff`，`runQuery`) | 模型无法判断选择哪个工具——会跳过它们或幻觉参数 | 动词优先的特定名称：`Search customer database`，`Generate image with Veo` |
| 空的或单行工具描述 | 模型不知道何时调用；选择不佳，无错误 | 编写真实描述：它做什么，何时使用，每个参数的含义 |
| 将每个工具的指令塞入系统提示 | 提示膨胀，无重用，每个工具的指导被隐藏 | 将工具特定指令移到工具描述中 |
| 代理 + Switch 用于自然语言路由 | 两个节点 + 提示样板，而 Text Classifier 是一个节点 | 使用 Text Classifier——每个类别都有自己的输出处理（名称**和**描述） |
| 将图像/音频/视频生成包装在代理中 | 二进制无法通过工具或代理输出 | 直接使用提供商的原生单次调用节点 |
| `outputParserStructured` 而没有 `autoFix` | 一个格式错误的响应会停止工作流程 | `autoFix: true` + 一个编码能力的修正模型 |
| 直接将二进制传递给工具 | 不起作用——二进制无法跨越工具边界 | 预先存储到存储中，传递密钥；参见 **n8n-binary-and-data** |
| 硬编码 `sessionId` / 无 sessionId / `$fromAI` 背后的 `sessionId` | 对话交叉，或模型编造一个 UUID | 从触发器到内存和工具管道一个稳定的密钥 |
| 两个几乎相同的工具 | 选择是非确定性的，模型会混淆 | 一个内部分支由参数驱动的工具 |
| 没有机器人用户过滤的聊天机器人 | 它自己的回复会重新触发它 → 无限循环 | 在触发器或第一个节点处排除机器人用户 ID |
| 在多工具代理上保留低默认值 `maxIterations` | "达到最大迭代次数" / 空输出 | 提高 `options.maxIterations` |
| 通过 `$fromAI()` 填充人工审核消息 | 批准者对释义签字，而不是真实调用 | 使用字面量 `{{ $tool.parameters.<name> }}` |

---

## 社区 MCP 无法提供的功能

| 想做 | 现实 |
|---|---|
| 交互式端到端测试工作流的 AI Agent 节点 | `n8n_test_workflow` 运行工作流，但节点上的真正多轮聊天会话是 UI 活动（画布聊天测试器）。相比之下，持久的代理可以通过 `n8n_manage_agents` `call` 实时运行——参见上面“持久的 n8n 代理”。 |
| 设置凭证的实际秘密值 | `n8n_manage_credentials` 创建/更新凭证记录，但代理提供者密钥本身是在 UI 中输入/验证的。 |
| 为工作流分配错误工作流 | 仅限 UI —— 参见 **n8n-error-handling**。构建通用的，然后将用户交给 UI 步骤。 |
| 固定每个实例的确切模型可用性 | 模型列表在版本之间变化——`search_nodes`/`get_node` 反映已安装的内容。在目标实例上验证。 |

MCP 可以做的事情：搜索和检查每个 LangChain 节点 (`search_nodes`，`get_node`)，验证节点配置和整个图 (`validate_node`，`validate_workflow`)，构建和修补代理及其子节点 (`n8n_update_partial_workflow` 在 `ai_*` 输出上使用 `addConnection`)，测试 (`n8n_test_workflow`)，以及拉取保存的 JSON 以验证连接 (`n8n_get_workflow`)。深入的 AI-agent 指南也存在于 `tools_documentation({topic: "ai_agents_guide", depth: "full"})`。

---

## 与其他技能的集成

- **n8n-workflow-patterns** (`ai_agent_workflow.md`) — 高级的“代理在流程中”形状。这个技能是深入探讨；从那里开始进行架构。
- **n8n-mcp-tools-expert** — 节点类型格式（短形式用于 `get_node`，JSON 中的长形式）和工具选择指导。在进行任何 MCP 调用之前咨询。
- **n8n-node-configuration** — 代理和子节点上的 `displayOptions` 驱动的字段；Slack/Block Kit 消息形状（`NODE_FAMILY_GOTCHAS.md`，Slack 部分）。
- **n8n-expression-syntax** — `{{ }}`，`$json.output`，`$now` 和 `$fromAI`/`$tool.parameters` 都依赖于正确的表达式语法。
- **n8n-code-tool** — 自定义代码工具的运行时合同（字符串输入/输出，没有 `$fromAI`）。在编写 `.toolCode` 之前阅读它。
- **n8n-subworkflows** — `.toolWorkflow` 基于的子流程基本原理（执行工作流触发器输入/输出，命名，构建前搜索）。
- **n8n-binary-and-data** — 拥有代理工具二进制边界机制（存储上传，返回生成文件）。
- **n8n-validation-expert** — 解释 `validate_workflow` 结果，包括 AI 连接问题（工具连接到 `main` 而不是 `ai_tool` 标记为断开连接）。
- **n8n-error-handling** — 工具子工作流和代理核心调用上的 `onError: 'continueErrorOutput'`；聊天壳中的错误 UX。
- **n8n-code-javascript / n8n-code-python** — 用于工具子工作流内的代码节点逻辑（与代码工具不同的沙盒）。

---

## 快速参考清单

在发布代理之前：

- [ ] **正确的节点**：代理用于工具/内存/多轮；Text Classifier 用于路由；信息提取器用于字段；原生节点用于媒体
- [ ] **模型** 通过 `ai_languageModel` 连接
- [ ] **每个工具** 都有一个动词优先的特定名称**和**真实描述
- [ ] **`$fromAI()` 描述** 是具体的（格式，范围，示例）；身份/限制/sessionId 确定性地管道，不是通过 `$fromAI`
- [ ] **每个工具的指导** 存在于工具描述中，不在系统提示中
- [ ] **`$now`** 在系统提示中（没有硬编码的日期）
- [ ] **`maxIterations`** 为多工具代理提高
- [ ] **内存** 通过触发器的一个稳定 `sessionKey` 键（不是 `'default'`，不是 `$fromAI`）；`contextWindowLength` 从 5 提高
- [ ] **结构化输出**：`schemaType: 'manual'` + `autoFix: true` + 一个编码能力的修正模型
- [ ] **破坏性工具** 被包裹在人工审核中；批准消息使用 `$tool.parameters`，不是 `$fromAI`
- [ ] **聊天机器人** 过滤机器人自己的用户 ID（触发器级或第一个节点）
- [ ] **二进制**：模型视觉通过 `passthroughBinaryImages`；工具获得存储密钥，从不获得字节
- [ ] **验证** 通过 `validate_workflow` 并通过 `n8n_get_workflow` 验证（子节点在 `ai_*` 上，不是 `main`）

---

**记住**：一个代理的好坏取决于它的工具名称、描述和系统提示纪律。模型看不到你的连接——它看到的是一个系统提示和一组命名的、描述的工具。像 API 一样设计它们，大多数“代理不会按预期工作”的问题都会消失。
