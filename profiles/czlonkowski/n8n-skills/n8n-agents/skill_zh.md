# n8n 代理

n8n AI 代理节点（`@n8n/n8n-nodes-langchain.agent`）是一个多轮 LLM 驱动，包含模型、内存、工具和可选的输出解析器子节点。这项技能是关于设计和围绕它们的 LangChain 家族的**深入**指南。关于高级别“代理在流程中的位置”图示，请参阅**n8n-workflow-patterns**的`ai_agent_workflow.md`——这项技能深入到*如何构建它*。

对于节点类型格式：在流程 JSON 中，LangChain 节点使用长格式`@n8n/n8n-nodes-langchain.*`（`.agent`、`.lmChatOpenAi`、`.memoryBufferWindow`、`.outputParserStructured`、`.toolWorkflow`、`.toolHttpRequest`、`.toolCode`）。当你调用`get_node` / `validate_node`时，使用**短**格式（`nodes-langchain.agent`）。有关格式规则，请参阅**n8n-mcp-tools-expert**。

---

## 首先选择正确的节点

当任务是一次性分类或提取时，使用代理是最常见的过度构建。在连接任何东西之前做出决定：

| 你需要做… | 使用 | 原因 |
|---|---|---|
| 调用工具、多轮推理或持内存 | **AI Agent** (`.agent`) | 完整循环：模型 + 工具 + 内存 + 可选解析器。也是当你宁愿标准化时的良好默认值。 |
| 一次性文本输入→文本输出，无工具 | **Basic LLM Chain** (`.chainLlm`) | 无代理循环，更容易调试。仍然接受一个`outputParserStructured`子节点。 |
| 将自然语言输入路由到**N个分支**之一 | **Text Classifier** (`.textClassifier`) | 一个节点，N个输出处理，下游直接连接到每个分支。不是代理+开关。 |
| 从自由文本中提取结构化字段 | **Information Extractor** (`.informationExtractor`) | 带有架构的专用于字段提取。 |
| 三向积极/中性/消极划分 | **Sentiment Analysis** (`.sentimentAnalysis`) | 内置分支输出。 |
| 精简长文档 | **Summarization Chain** (`.chainSummarization`) | 内置的映射-归约摘要。 |
| 生成图像/音频/视频 | **提供商的原生单次调用节点** (OpenAI、Gemini、ElevenLabs…) | 绝对不要将媒体生成包装在代理中——请参阅“二进制和代理边界”。 |

**Text Classifier 详细信息（代理+开关的反模式）：** 每个类别都需要**名称和描述**。模型根据描述进行路由，而不是名称——没有描述的类别由抛硬币选中。设置`options.enableAutoFixing: true`以在边缘输入时提高鲁棒性。一个节点，N个分支，搞定。选择一个“决定”然后一个“路由”的代理是两个节点加上提示模板，而Text Classifier原生就能做到。

Chat 模型节点（`.lmChatOpenAi`、`.lmChatAnthropic`、`.lmChatOpenRouter`、…）是**子节点**——它们不能独立运行。它们通过`ai_languageModel`连接线连接到链、代理、分类器或提取器。

---

## 子节点模式

代理有一个**主输入**（提示/用户消息）和最多四个**子节点插槽**，每个插槽通过自己的`ai_*`连接类型连接：

| 插槽 | 连接类型 | 是否必需 | 节点示例 |
|---|---|---|---|
| **模型** | `ai_languageModel` | 是 | `.lmChatOpenAi`、`.lmChatAnthropic`、`.lmChatOpenRouter` |
| **内存** | `ai_memory` | 可选 | `.memoryBufferWindow`、`.memoryPostgresChat` |
| **工具** | `ai_tool` | 可选（但代理的要点） | `slackTool`、`.toolWorkflow`、`.toolHttpRequest`、`.toolCode` |
| **输出解析器** | `ai_outputParser` | 可选 | `.outputParserStructured` |

子节点从自身连接到代理。在流程 JSON 中，连接存在于**子节点**上，按`ai_*`类型键入：

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

多个工具都连接到相同的`ai_tool`索引 0——它们堆叠，而不是分散到不同的索引。使用`n8n_update_partial_workflow`，你通过使用`sourceOutput: "ai_tool"`的`addConnection`操作来连接每个。代理将其最终答案放在**`$json.output`**（不是`.text`，不是`.response`）——下游节点读取`{{ $json.output }}`。

参见**EXAMPLES.md**以获取完整的无状态代理核心节点对象片段。

---

## 两个非协商项

1. **工具名称和描述是提示的一部分。** 模型通过读取工具的名称和描述来选择工具——没有其他东西。一个名为`tool1`且描述为空的工具对模型不可见：它跳过它、错误选择它或幻觉参数。通常没有错误——只是代理“不会使用我的工具”。将两者都视为 API 设计。→ **TOOLS.md**
2. **结构化输出必须解析和自动修复。** 带有`autoFix: true`和一个**能够编码的修复模型**的`outputParserStructured`是生产模式。如果没有自动修复，一个格式错误的 JSON 响应会停止整个工作流。→ **STRUCTURED_OUTPUT.md**

---

## 强制默认值

- **每个工具的使用情况放在工具描述中，而不是系统提示中。** 有关*如何调用特定工具*的任何内容都属于工具，因此它可以在代理之间传递，并使系统提示保持专注。→ **SYSTEM_PROMPT.md**
- **用于任何多步骤操作的子工作流工具（`.toolWorkflow`）。** 任何工作流都成为具有类型`$fromAI()`输入的工具，并组合分支、错误处理和重用。在不确定时使用默认值。→ **SUBWORKFLOW_AS_TOOL.md**和**n8n-subworkflows**。
- **将具有用户可见副作用的工具包装在人工审核中。** 发送、支付、退款、账户更改在人工批准节点后才会执行，以便人类在工具执行之前签字。→ **HUMAN_REVIEW.md**
- **提高`maxIterations`。** 默认工具调用限制**很低**（大多数版本上的个位数）——对于一次性工具代理足够，但对于每轮链式调用多个工具的代理来说太低了。它表现为“达到最大迭代次数”或空输出。将`options.maxIterations`设置为现实的上限（15用于专注的子代理，50-200用于广泛的协调器）。
- **将当前日期通过`{{ $now }}`（或`{{ $now.format('DDDD') }}`）放入系统提示中。** 硬编码的日期立即过时。

---

## 四种工具类型

选择最轻的选项来覆盖工作：

| 工具类型 | 节点 | 使用场景 |
|---|---|---|
| **原生工具节点** | `slackTool`、`gmailTool`、`toolCalculator`、… | 能力映射到一个现有节点+一个操作。最低开销。 |
| **子工作流作为工具** | `.toolWorkflow` | 多于一个节点、可重用逻辑或您希望独立的可测试性。n8n 的规范方法——**不确定时使用默认值**。 |
| **HTTP 请求工具** | `.toolHttpRequest` | 代理应直接协调的单个外部 HTTP API。重用服务预定义的凭证来覆盖原生节点未暴露的操作。 |
| **MCP 客户端工具** | `.mcpClientTool` | 已由维护的 MCP 服务器覆盖，或您希望一个发布的工作流为多个代理服务。 |

还有一个**自定义代码工具**（`.toolCode`）用于纯内联计算——但它的运行时合同（字符串输入/输出，没有`$fromAI`，没有`$helpers`）由**n8n-code-tool**技能拥有。在编写之前请阅读它。经验法则：如果您在代码中找到自己使用`$fromAI()`，则应使用`.toolWorkflow`。

### `$fromAI()`：代理如何填充工具参数

代理应决定工具参数被包装在`$fromAI()`中。它是一个**真实的 n8n 表达式助手**，用于工具节点的参数表达式内：

```
={{ $fromAI('paramName', 'what to put here — be specific: format, range, example', 'string') }}
```

- **paramName** — 模型内部使用的名称（蛇形或驼峰，保持一致）。
- **description** — 告诉模型要生成的值。**它是提示的一部分**——像 JSDoc 那样编写它。
- **type** (可选) — `'string'`（默认）、`'number'`、`'boolean'`、`'json'`。类型错误的值会导致调用失败。
- **defaultValue** (可选) — 当模型省略它时使用。

`$fromAI()`只携带 JSON——它**不能携带二进制**（没有 base64，没有文件字节）。并且并非每个参数都必须是`$fromAI`：从工作流上下文中稳定地连接身份、权限限制和关联 ID（`userId`、退款限制、`sessionId`），以便代理无法出错或甚至看到它们。→ **TOOLS.md**以获取完整解剖和“给代理一个按钮，而不是方向盘”的模式。

---

## 系统提示与工具描述

| 属于系统提示 | 属于工具描述 |
|---|---|
| 个性、角色、声音 | 具体工具做什么 |
| 全局输出/格式规则（“以 markdown 响应”） | 与其他工具何时使用 |
| 拒绝/安全行为 | 每个参数的含义及其形状 |
| 显示协议（`![]()`用于图像） | 良好与不良调用的示例 |
| 通用上下文（通过`$now`的用户角色） | 工具特定注意事项（速率限制、边缘情况） |
| 工具间流程（“生成后始终显示”） | 工具特定输入转换 |

为什么分割：一个良好描述的工具可以在**任何**代理中使用，工具细节仅在模型考虑使用该工具时“加载”（标记效率），并且您只需更新一个工具描述，而不是 5000 个 token 提示中隐藏的一段文字。→ **SYSTEM_PROMPT.md**

---

## 结构化输出：何时以及如何

当下游需要严格的 JSON 而不是自由文本时，添加一个`outputParserStructured`子节点（通过`ai_outputParser`连接）。两条规则：

1. **使用`schemaType: 'manual'`和一个真实的 JSON Schema，而不是`jsonSchemaExample`。** 示例无法表达必需与可选、枚举、数值范围或数组约束——一旦形状变得复杂，您就会超出它的范围。仅在形状为一次性时使用`fromJson`+示例。
2. **`autoFix: true`和一个编码能力强的修复模型。** 将另一个模型连接到解析器的`ai_languageModel`插槽。将损坏的 JSON 与架构进行协调是一项编码任务——一个弱修复器只会产生另一个格式错误的重试并消耗 token。

→ **STRUCTURED_OUTPUT.md**以获取架构模式、负载重心的“不要用 markdown 包装”重试行和解析失败的食谱。

---

## 内存：简要心智模型

内存是一个子节点（`ai_memory`）。没有它，每次调用都是无状态的——对于一次性任务（分类、摘要）是正确的。有它，代理会持有对话，通过绑定到`sessionKey`的表达式进行键控。

- **`memoryBufferWindow`** — 每个键保留最后 N 次交换并通过 n8n 的存储持久化。聊天默认。**`contextWindowLength`默认为 5，这非常低**——50 是一个更合理的起点。窗口之外的消息完全丢失。
- **`memoryPostgresChat` / `memoryRedisChat`** — 仅当内存必须在代理*外部*读取时（您自己的 UI、分析、跨系统）才需要。不需要仅仅为了在重新启动后生存；BufferWindow 已经做到了。

**始终如一地从触发器到内存和工具中连接一个稳定的键。** 聊天触发器自动填充`sessionId`；对于其他表面，请导出一个（Slack `thread_ts`、一个 webhook 会话 ID）。永远不要硬编码`sessionId: 'default'`，也永远不要将`sessionId`放在`$fromAI`后面（模型将编造一个 UUID）。→ **MEMORY.md**

---

## 二进制与代理边界

这是让许多人困惑的地方：

- **模型可以查看上传的图像**（视觉）通过代理上的`options.passthroughBinaryImages: true`。
- **工具不能接收二进制。** `$fromAI()`是 JSON 仅限的——没有 base64，没有字节，即使通过非 AI 绑定。
- **代理的输出是文本形状**（或带有解析器的结构化文本）。当模型返回图像/音频/视频字节时，代理不会显示它们——下游没有任何东西可以恢复。

**解决方法：** 在代理运行之前预阶段上传到存储，将存储键注入系统提示，并让工具作为字符串参数接收键并在内部重新获取。对于一次性媒体生成，跳过代理并直接调用提供商的原生单次调用节点。

二进制机制（哪个存储、如何预阶段、如何重新获取）由**n8n-binary-and-data**拥有——请参阅其代理-工具二进制参考。这项技能仅标记边界；不要在这里重新推导机制。

---

## 人工审核（破坏性工具的关卡）

当工具的效果需要在执行之前需要人工签字时（发送、支付、退款、账户更改），请将它们包装在人工审核工具节点中——`slackHitlTool`、`discordHitlTool`、`telegramHitlTool`、`gmailHitlTool`等（n8n 将这些命名为“Hitl” / 人工参与）。审核节点位于包装工具和代理之间的`ai_tool`连接上：包装工具→审核节点→代理。

是否需要签字是一个产品/政策决定——**将问题展示给用户**，根据影响范围提供建议，并让他们决定。

**关键规则：** 显示包装工具将接收的实际参数。在批准消息中使用字面`{{ $tool.parameters.<name> }}`，而不是`$fromAI()`释义——否则，人类批准的是模型编造的文本，而不是即将执行的调用。→ **HUMAN_REVIEW.md**

---

## 聊天代理（Slack、Discord、Teams、Telegram）

**一个非协商项，无论复杂性如何：** 任何由聊天触发的流程在回复时都必须**过滤掉机器人自己的用户 ID**，否则它的回复会重新触发它，导致无限循环，消耗运行和 token。当可用时，请优先在触发器级别进行过滤（Slack 触发器的`options.userIds`是一个**排除列表**——将机器人 ID 放在那里）；否则在触发器之后的第一个节点中过滤`$json.user !== '<BOT_USER_ID>'`。

除了过滤器之外，一个简单的机器人（触发器→代理→回复）可以很好地存在于一个工作流中。只有当您需要加载 UX、子代理、多表面重用或鲁棒错误处理时，才将其拆分为**外壳+核心+子代理**：

- **外壳**——触发器、反循环过滤器、事件类型开关、加载/错误 UX、渲染回复。没有 LLM。
- **核心**——无状态代理，`chatInput` + `threadId`输入，内存键控在`threadId`上，工具和子代理。
- **子代理**——每个子领域一个，通过`.toolWorkflow`调用，**无状态**（完整上下文在`chatInput`中）。

→ **CHAT_AGENT_PATTERNS.md**以获取每个表面的语义、线程作为会话以及完整的拓扑结构。

---

## 持久化的 n8n 代理（n8n_manage_agents）

一个**持久化的 n8n 代理**是上面介绍的 AI Agent 节点不同的工件：一个独立的助手记录——模型、指令、工具、技能、任务、内存、频道——由 n8n 本身存储和版本控制，通过`n8n_manage_agents`（n8n 的实例级 MCP 服务器）管理，而不是工作流 JSON 中的节点。

| 你需要做… | 使用 |
|---|---|
| 在工作流中的一次性推理步骤，通过`ai_*`子节点连接 | **AI Agent 节点**（这项技能，上面） |
| 一个具有自己生命周期——草稿、验证、发布、版本、频道——独立于任何单个工作流的独立助手 | **持久化代理** (`n8n_manage_agents`) |

**前提条件：** 配置`N8N_MCP_ACCESS_TOKEN`（与公共 API 密钥分开）和 n8n **2.34+**并启用代理模块。对于**每个**操作都需要此令牌，包括`reference`/`search`——没有它，任何操作都不会工作。另外，`reference`和`search`对**任何**代理都有效，无论 MCP 暴露如何；通过这项工具创建的代理会自动暴露——暴露门仅适用于这项工具之前已存在的代理。

**构建顺序：**
1. `action: "reference"` — 在进行任何其他操作之前，读取配置架构和确切的突变操作。
2. `action: "discover_assets"` — 列出代理实际上可以连接到什么。需要`projectId`（从`n8n_list_catalog({kind: "projects"})`）和`kind`: `models`（带有`provider`）、`integrations`、`workflows`、`subagents`或`mcpServers`。每个种类调用一次。
3. `action: "create"` — `projectId`、`name`、`config`。
4. `action: "mutate"` — 每个资源每调用一次（`config.patch`、`skill.upsert`/`delete`、`task.upsert`/`delete`、`customTool.upsert`/`delete`），始终传递最新的哈希值。注意两个名称：n8n 返回它作为`configHash`，并期望它作为`args.baseConfigHash`返回。`args`被逐字转发，因此任何字段名称的近似值都会返回`INVALID_ARGS`，而不是有帮助的更正——这就是为什么步骤 1 首先读取架构。陈旧的哈希值返回为`STALE_CONFIG`——重新`get`并使用最新的。

5. `action: "validate"` — 在提供`call`或`publish`之前。
6. `action: "publish"` — **仅在用户明确请求时**，从不主动。

`action: "call"`使用真实凭据和真实工具运行代理——一次实时执行，而不是干运行。结果可以携带`approvals[]`，用于需要人工决策的工具调用；**永远不要代表用户批准**——展示它们，只有在用户决定后才能继续。

**自定义工具是第三个代码运行时——不要重用其他两个。** `customTool.upsert`正文是**TypeScript**，并且它可能使用的唯一导入是`@n8n/agents`和`zod`。这不是代码节点（JavaScript/Python，返回`[{json: …}]`）也不是由**n8n-code-tool**覆盖的 AI-agent 自定义代码工具（`.toolCode`，返回字符串，没有`$fromAI()`）。在这里选择错误的合同是容易犯的错误，因为所有三个都是“写代码代理调用”。在编写之前请阅读它的形状，因为编译错误或未知`agentId`会显示为`AGENT_TOOL_ERROR`。

**凭据注意事项：** 在 n8n 2.36.x 上，代理运行时拒绝`azureOpenAiApi`和`aws`凭据（报告为`missing: ["credential"]`）；响应的`hint`命名了接受的类型。**测试时不留下垃圾**：将一次性代理命名为`[TEST] …`，完成时删除它们——持久化代理比生成它的对话寿命更长，而工作流可以保持非活动状态。

→ **n8n-mcp-tools-expert** `## 代理`以获取工具的完整操作列表和错误代码。

---

## 与其他技能的集成

- **n8n-workflow-patterns** (`ai_agent_workflow.md`) — 高级别的“代理在工作流中的位置”形状。这项技能是深入探讨；从架构开始。
- **n8n-mcp-tools-expert** — 节点类型格式（短格式用于`get_node`，长格式用于 JSON）和工具选择指南。在调用任何 MCP 之前进行咨询。
- **n8n-node-configuration** — `displayOptions`驱动的代理和子节点上的字段；Slack/Block Kit 消息形状（`NODE_FAMILY_GOTCHAS.md`，Slack 部分）。
- **n8n-expression-syntax** — `{{ }}`、`$json.output`、`$now`和`$fromAI`/`$tool.parameters`都依赖于正确的表达式语法。
- **n8n-code-tool** — 自定义代码工具的运行时合同（字符串输入/输出，没有`$fromAI`）。在编写`.toolCode`之前请阅读它。
- **n8n-subworkflows** — 子工作流原语，`.toolWorkflow`构建在其上（执行工作流触发器的输入/输出、命名、构建前搜索）。
- **n8n-binary-and-data** — 拥有代理-工具二进制边界机制（预阶段上传、返回生成的文件）。
- **n8n-validation-expert** — 解释`validate_workflow`结果，包括 AI 连接问题（工具连接到`main`而不是`ai_tool`标记为断开连接）。
- **n8n-error-handling** — 工具子工作流和代理核心调用上的`onError: 'continueErrorOutput'`；聊天外壳上的错误 UX。
- **n8n-code-javascript / n8n-code-python** — 用于工具子工作流内的代码节点逻辑（不同的沙盒与 Code 节点不同）。

---

## 快速参考清单

在发布代理之前：

- [ ] **正确的节点**：代理用于工具/内存/多轮；Text Classifier用于路由；Information Extractor用于字段；原生节点用于媒体
- [ ] **模型**通过`ai_languageModel`连接
- [ ] **每个工具**都有动词优先的特定名称和真实的描述
- [ ] **`$fromAI()`描述**是具体的（格式、范围、示例）；身份/限制/sessionId稳定地连接，不是通过`$fromAI`
- [ ] **`$now`**在系统提示中（没有硬编码的日期）
- [ ] **`maxIterations`**对于多工具代理提高
- [ ] **内存**键控在稳定的`sessionKey`上从触发器（不是`'default'`，不是`$fromAI`）；`contextWindowLength`从 5 提高到 50
- [ ] **结构化输出**：`schemaType: 'manual'` + `autoFix: true` + 编码能力强的修复模型
- [ ] **破坏性工具**包装在人工审核中；批准消息使用`$tool.parameters`，而不是`$fromAI`
- [ ] **聊天机器人**过滤掉机器人的用户 ID（触发器级别或第一个节点）
- [ ] **二进制**：模型视觉通过`passthroughBinaryImages`；工具获取存储键，而不是字节
- [ ] **验证**使用`validate_workflow`并使用`n8n_get_workflow`验证（子节点在`ai_*`上，而不是`main`）

---

**记住**：代理只有在其工具名称、描述和系统提示纪律良好的情况下才是好的。模型看不到您的连接——它看到系统提示和一组命名、描述的工具。像 API 那样设计它们，大多数“代理不会按预期工作”的问题就会消失。
