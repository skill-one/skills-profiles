---
name: n8n-agents-official
description: 在构建或编辑 n8n 中的任何 AI 功能时使用：AI Agents、Text Classifier、Information Extractor、Sentiment Analysis、Summarization Chain、Basic LLM Chain、embeddings、vector stores、单个 one-shot LLM 调用，或通过原生 LangChain 提供者节点进行 AI 媒体生成（图像/音频/视频）。在任意 `@n8n/n8n-nodes-langchain.*` 节点上触发，包括“agent”、“chat assistant”、“带工具的 LLM”、“工具调用”、“fromAi”、“system prompt”、“memory window”、“结构化输出”、“outputParser”、“function calling”、“RAG”、“vector store”、“embeddings”、“AI 分类”、“使用 LLM 提取字段”、“情感分析”、“使用 LLM 摘要”、“单个 LLM 调用”、带文件的聊天触发器、AI 图像/视频/音频生成，或任何多轮或 one-shot LLM 行为。
---

# n8n 代理

n8n Agent 节点（`@n8n/n8n-nodes-langchain.agent`）是一个多轮 LLM 驱动，包含模型、内存、工具和可选输出解析器的子节点。

## 何时使用 Agent 节点与原始聊天完成

决策：

- **需要工具调用、多轮推理或内存？** Agent。此外，当你不想考虑它时这也是一个很好的默认选项：在整个工作流中统一使用 Agent 是合理的，并且使升级路径更简单。
- **想要最轻量级的单次文本输出调用？** 基础 LLM 链 (`@n8n/n8n-nodes-langchain.chainLlm`) 配合聊天模型子节点（`OpenRouter Chat Model`、`OpenAI Chat Model`、`Anthropic Chat Model` 等）。没有 Agent 循环，没有工具/内存/解析器插槽，更容易调试。注意：聊天模型节点是子节点，它们不能独立运行。它们连接到链或 Agent。如果更喜欢标准化，Agent 也适用。
- **根据自然语言输入路由到 N 个输出分支（AI 的工作是选择分支）？** 使用文本分类器节点（`@n8n/n8n-nodes-langchain.textClassifier`）。N 个输出处理，每个类别一个，下游路径直接连接到每个。每个类别都需要名称和描述（描述是模型选择的内容，仅名称不足以）。设置 `options.enableAutoFixing: true` 以便在边缘输入时具有鲁棒性。与聊天模型子节点（`OpenRouter Chat Model`、`OpenAI Chat Model` 等）配对。不要为这个使用 Agent + Switch。文本分类器是一个节点，并且是专门设计的。
- **结构化输出但没有工具？** Agent 是一个更简单的默认选项，并考虑了未来的扩展。基础 LLM 链也接受一个 `outputParserStructured` 子节点，并且在您想要轻量级节点的地方工作得很好。
- **图像 / 音频 / 视频生成？** 当直接调用它们时（OpenAI Image、Gemini Image、ElevenLabs 等）的提供商的原生单次调用节点。当通过聚合器路由时（OpenRouter、Together 等），使用 HTTP 请求，因为没有原生聚合器节点，并且原生节点在媒体操作中硬编码了提供商的基本 URL。**不要将媒体生成包装在 Agent 中**，见下文“二进制与 Agent 边界”。

有其他用于狭窄任务的 LangChain “链” / 工具节点：信息提取器（从文本中提取结构化字段）、情感分析（3 路分支）、摘要链、基础 LLM 链。

Agent 对于大多数 LLM 步骤是一个合理的默认值。当您特别想要一个没有工具、内存或迭代的单次文本调用的更精简的节点时，请使用基础 LLM 链。当其中一个专门设计的节点与任务完全匹配时，请使用信息提取器 / 情感分析 / 摘要链 / 文本分类器。

## 非协商项

1. **工具名称和描述是提示的一部分。** 模型通过名称和描述选择工具。模糊的工具节点名称（如（doStuff））或弱的描述（“用数据做事情”）会导致静默失败：模型跳过您的工具、错误选择它或幻觉参数。将两者都视为 API 设计。见 `references/TOOLS.md`。
2. **结构化输出：解析和 autoFix。** `outputParserStructured` 配合 `autoFix: true` 和一个编码能力强的修复模型（例如，Claude Sonnet 4.6）是生产模式。

## 强制默认值

- **工具描述是模块化的提示片段。** 任何特定于 *如何调用此工具* 的内容都属于工具的描述，而不是系统提示。使系统提示保持专注，并且工具可以在不同的 Agent 之间重复使用。见 `references/SYSTEM_PROMPT.md`。
- **子工作流工具（`toolWorkflow`）用于任何多步操作。** 任何工作流都成为具有类型 `fromAi()` 输入的工具，并与分支、错误处理、子工作流组合。见 `references/SUBWORKFLOW_AS_TOOL.md`。
- **将具有用户可见副作用（发送、支付、退款、账户更改）的工具包装在人工审核中。** 将它们置于 Slack / Chat / Discord / Telegram 审核节点之后，以便在工具运行之前有人签字。见 `references/HUMAN_REVIEW.md`。

## 子节点模式

Agent 节点有一个主输入（提示或用户消息）和子节点输入：

```ts
const aiAgent = node({
    type: '@n8n/n8n-nodes-langchain.agent',
    config: {
        name: 'Customer Support Agent',
        parameters: {
            promptType: 'define',
            text: '={{ $json.userMessage }}',
            options: {
                systemMessage: '...',
                passthroughBinaryImages: true,    // 用于视觉 / 多模态
            },
        },
        subnodes: {
            model: openRouterModel,
            memory: simpleMemory,
            tools: [generateImage, editImage, searchKnowledgeBase],
            outputParser: structuredParser,    // 可选
        },
    },
})
```

四个子节点插槽：

- **`model`**（必需）：语言模型。OpenAI、Anthropic、OpenRouter 等。使用聊天模型变体，而不是完成变体。
- **`memory`**（可选）：对话内存。没有它，每次调用都是无状态的。见 `references/MEMORY.md`。
- **`tools`**（可选，但使用 Agent 的要点）：Agent 可以调用的工具。见 `references/TOOLS.md`。
- **`outputParser`**（可选）：强制结构化 JSON 输出。见 `references/STRUCTURED_OUTPUT.md`。

## 触发器

不同的触发器以不同的方式塑造输入：

- **聊天触发器（`@n8n/n8n-nodes-langchain.chatTrigger`）** 配合 `availableInChat: true`：为画布聊天测试器提供动力，以便在构建它时可以戳 Agent。输入是 `{ chatInput, sessionId, files[] }`。`sessionId` 是内存键的触发器，因此将其传递到需要对话连续性的任何地方。文件通过 `files[]` 提供，见二进制部分。这不是生产界面，使用 Slack / Discord / Teams / Telegram / webhook。
- **Webhook**：任意的输入形状，默认情况下没有会话。通过在请求正文中传递会话/对话 ID 并将其转发到内存节点来管理连续性。
<!-- 临时：在发布新 Agent 范式时更新以下内容 -->
- **外部聊天界面（Slack、Discord、Teams、Telegram）**：每个聊天触发的工
作流如果发布回复，都必须过滤掉机器人自己的用户 ID，否则它可能会无限循环并可能崩溃 n8n。当界面支持时，请优先使用触发器级别的过滤（Slack 的 `options.userIds` 是排除列表）；否则在触发器之后的第一个节点中过滤。每个界面的语义不同，见 `references/CHAT_AGENT_PATTERNS.md`。除了反循环过滤器之外，在一个工作流中简单的机器人（触发器 → Agent → 回复）是没问题的。一旦您需要加载 UX、子 Agent、跨界面重复使用或健壮的错误处理，就将其拆分为“外壳”工作流 + Agent 核心子工作流。
- **手动 / 定时**：临时调用。内存很少有用，除非明确继续以前的运行。
- **执行工作流触发器**（子工作流）：当 Agent 本身是另一个 Agent 的工具时。将触发器声明的输入视为合同。

## 二进制与 Agent 边界

模型可以通过 `passthroughBinaryImages: true` *看到* 上传的文件（视觉）。但**工具不能接收二进制**，`fromAi()` 参数仅限于 JSON。Base64 也不被工具接受，即使通过非 AI 绑定。

解决方法：在工作流运行之前将上传预置到存储中，将存储键注入系统提示，工具将键作为字符串参数接收并在内部重新获取。完整模式在 `n8n-binary-and-data-official` `references/AGENT_TOOL_BINARY.md`。

在输出方面：Agent 的输出格式器是文本形状的（当连接了 `outputParser` 时为结构化文本）。当模型返回二进制（图像字节、音频字节、视频）时，Agent 不会显示它。下游没有可挖掘的内容，并且在 Agent 之后尝试通过代码或设置节点恢复它不起作用。**对于单次媒体生成，直接使用提供商的原生单次调用节点，例如 `@n8n/n8n-nodes-langchain.googleGemini` 或 `@n8n/n8n-nodes-langchain.openAi`。**

例外：当媒体步骤确实属于 Agent（几个工具之一，基于对话上下文选择，或编辑先前生成的图像）时，解决方法是工具子工作流将结果上传到存储并返回键或 URL。模式在 `n8n-binary-and-data-official` `references/AGENT_TOOL_BINARY.md`。不要默认使用此方法。上传 + 键 + 重新获取路径会增加节点和存储依赖，您不需要这些。只有在编排实际上需要 Agent 的工具选择时才使用。

## 系统提示与工具描述中包含的内容

| 属于系统提示 | 属于工具的描述 |
|---|---|
| 角色、身份、声音 | 此特定工具做什么 |
| 输出格式规则（“以 Markdown 响应”） | 何时使用此工具而不是其他工具 |
| 拒绝/安全行为 | 每个参数的含义及其预期形状 |
| 显示协议（“通过 `![]()` Markdown 显示图像”） | 好的与坏的调用的示例 |
| 通用上下文（当前日期、用户角色） | 工具特定的陷阱（速率限制、边缘情况） |
| 工具间流程（“生成后始终通过显示协议显示”） | 工具特定的输入转换 |

好处：工具变得可重用。一个描述良好的工具可以在任何将其放入的 Agent 中工作。系统提示专注于角色和共享行为。

有关更深入的指南和示例，请参阅 `references/SYSTEM_PROMPT.md` 和 `references/TOOLS.md`。

## 工具选择：四种类型

选择覆盖工作的最轻选项：

- **存在原生 n8n 工具节点？**（例如，`slackTool`、`gmailTool`、`calculatorTool`）使用它。最低配置开销。
    - **原生节点缺少操作或需要自定义参数**（例如，节点不暴露的 Notion 端点、非标准标头、不同的分页形状）？使用服务“预定义凭证类型”的 HTTP 请求工具。重用现有的 OAuth / API 密钥凭证，提供完整的 API 访问，无需自定义认证代码。
- **多步逻辑，或重用项目中已有的子工作流？** 子工作流作为工具（`toolWorkflow`）。您可以构建为工作流的任何内容都成为具有类型 `fromAi()` 输入的工具。n8n 中最强大的选项，因此当不确定时默认为此。见 `references/SUBWORKFLOW_AS_TOOL.md`。
- **Agent 应直接协调调用外部 HTTP API？** HTTP 请求工具。也适用于通过长轮询回调进行慢速异步工作。
- **工具已经作为发布的、MCP 可访问的工作流存在？** MCP 工具。用于跨工作流 Agent 功能。见 `n8n-extending-mcp-official`。

有关每个选项的更深入指南以及如何连接 `fromAi()` 参数，请参阅 `references/TOOLS.md`。

## 人工审核

在添加或跳过工具的人工审核之前，请与用户确认。是否需要签字是一个产品/政策决定（影响范围、审计要求、他们对模型的信任程度），用户比您更适合做出决定。提出问题，根据以下标准提供建议，并让他们决定。

当工具的效果需要在执行之前需要人工批准（发送、支付、退款、账户更改、面向客户的操作）时，使用审核工具节点将其包装起来：`slackHitlTool`、`discordHitlTool`、`telegramHitlTool`、`gmailHitlTool` 等（n8n 的节点名称使用 `Hitl` 表示人工回路模式，并且在 UI 中称为“人工审核”）。审核节点位于包装工具和 Agent 之间的 `ai_tool` 连接上：包装工具的 `ai_tool` 输出连接到审核节点，审核节点的 `ai_tool` 输出连接到 Agent。Agent 调用，审核节点暂停以获取批准，批准后，包装工具运行。

默认情况下，当：

- 工具发送、支付、退款或以其他方式更改用户可见状态时。
- 批准者与聊天者不同（经理批准客户操作、支持团队批准客户触发的退款）。
- 触发器是非交互式的（订单、表单、计划），但工具的效果需要人工签字。

批准消息应显示**包装工具将实际接收的参数**，而不是模型释义的文本。直接使用 `$tool.parameters.<name>`，或者迭代 `$tool.parameters` 以列出每个参数。不要通过 `fromAi()` 填充批准文本。您将批准释义，而不是字面调用。使用实际值自定义按钮标签，例如 `Approve {{ $tool.parameters.amount }} refund`。

完整配置模式、每个平台的设置以及 `references/HUMAN_REVIEW.md` 中的多渠道批准者模式。

## 输出解析：何时以及如何

当下游需要结构化数据而不是自由形式文本时，添加 `outputParser` 子节点。

```ts
const parser = outputParser({
    type: '@n8n/n8n-nodes-langchain.outputParserStructured',
    config: {
        parameters: {
            schemaType: 'manual',
            inputSchema: JSON.stringify({
                type: 'object',
                properties: {
                    score: { type: 'integer', minimum: 1, maximum: 5 },
                    category: { type: 'string', enum: ['bug', 'feature', 'question'] },
                    reason: { type: 'string' },
                    tags: { type: 'array', items: { type: 'string' } },
                },
                required: ['score', 'category', 'reason'],
            }),
            autoFix: true,
            customizeRetryPrompt: true,
            prompt: '...retry instructions...', // 通常保持默认
        },
        subnodes: {
            languageModel: fixerModel,    // 编码能力强的模型，例如 Claude Sonnet 4.6
        },
    },
})
```

1. **使用 `schemaType: 'manual'` 与一个真实的 JSON 范式，而不是 `jsonSchemaExample`。** 示例无法表达可选字段、枚举、值范围或数组约束，因此当形状变得非平凡时，您第一次就会超出它的范围。范式允许您标记字段是必需的还是可选的，定义枚举，约束数字和字符串格式，并给模型更清晰的规则遵循。仅对于您确定永远不会增长约束的临时形状，才使用 `schemaType: 'fromJson'` 与示例。
2. **`autoFix: true` 添加解析失败的重试。** 将一个编码能力强的模型作为修复子节点连接（例如，Claude Sonnet 4.6 或类似）。针对范式修复格式错误的 JSON 是一个结构化输出/编码任务，一个弱或通用的模型通常会产生另一个格式错误的重试，从而消除了这个目的。

有关完整模式，包括自定义重试提示，请参阅 `references/STRUCTURED_OUTPUT.md`。

## 内存：简要心智模型

- **无内存**：无状态。适用于单次任务（分类、摘要）。
- **`memoryBufferWindow`**：保留每个内存键的最近 N 条消息，并通过 n8n 的内部存储跨执行持久化。键是您绑定到 `sessionKey` 的任何表达式。聊天触发器自动填充 `sessionId`，但您可以键在任何地方（Slack `thread_ts`、webhook 对话 ID、多租户组合）。聊天内存的默认值。“窗口”是保持上下文的消息数量的滑动上限，而不是持久化的范围。
- **`memoryPostgres` / `memoryRedis` / 类似**：当您需要在 Agent **外部**查询或读取内存时使用这些：在您自己的 UI 中显示对话历史记录、对过去的聊天进行分析，或与另一个系统共享内存。否则 `memoryBufferWindow` 足够。

始终从触发器到内存一致地引出一个稳定的键，否则对话会交叉。见 `references/MEMORY.md`。

## RAG（检索增强生成）

n8n 有 LangChain RAG 原语：文档加载器、文本分割器、嵌入、向量存储、检索器、重新排序器。这些部分可以工作，但意见一致的端到端配方（“哪个向量存储、哪个分块、何时重新排序”）严重依赖于数据形状和规模。

这项技能保持 RAG 意见的一致性是有目的的。有关 RAG 的更多详细信息，请参阅 `references/RAG.md`。

## 参考文件

| 文件 | 何时阅读 |
|---|---|
| `references/TOOLS.md` | 向代理添加工具，选择四种工具类型，编写工具名称和描述 |
| `references/SUBWORKFLOW_AS_TOOL.md` | 通过 `toolWorkflow` 将子工作流作为代理工具连接，映射 `fromAi` 覆盖设置 |
| `references/SYSTEM_PROMPT.md` | 编写或重构系统提示，决定系统提示中包含的内容与工具描述的区别 |
| `references/STRUCTURED_OUTPUT.md` | 强制 JSON 输出，配置 autoFix 重试，验证下游 |
| `references/MEMORY.md` | 选择内存类型，持久化和 sessionId 处理 |
| `references/RAG.md` | 构建检索增强代理，有意为之的占位符 |
| `references/HUMAN_REVIEW.md` | 向工具添加人工批准，配置批准消息，多渠道审批者模式 |
| `references/CHAT_AGENT_PATTERNS.md` | 在 Slack、Discord、Teams、Telegram 或任何自定义聊天界面构建聊天代理，多工作流外壳 + 核心 + 子代理拓扑 |

## 反模式

| 反模式 | 问题所在 | 解决方法 |
|---|---|---|
| 通用工具名称（`doStuff`、`runQuery`） | 模型无法判断选择哪个工具，会跳过它们或凭空想象参数 | 动词优先的特定名称：`搜索客户数据库`、`使用Veo生成图像` |
| 空的或单行的工具描述 | 模型不清楚何时调用，选择不佳 | 编写真实描述：工具做什么，何时使用，参数含义 |
| 将所有内容都塞入系统提示 | 提示冗长，无法重用，每工具的指导被隐藏 | 将工具特定指令移至工具描述，系统提示仅保留角色 + 全局规则 |
| 代码节点工具而子工作流更合适 | 无法重用，无法独立测试，无法与分支组合 | 使用 `toolWorkflow` 并配合合适的子工作流 |
| 直接将二进制传递给工具 | 不起作用，二进制无法跨越工具边界 | 预先存入存储，通过 `fromAi` 传递密钥，工具内部获取。参见 `n8n-binary-and-data-official` |
| `outputParserStructured` 而没有 `autoFix` | 一个糟糕的模型输出导致工作流失败 | 设置 `autoFix: true` 并配合一个廉价的修复模型 |
| 硬编码 `sessionId` 或无 sessionId | 对话交叉或内存始终不匹配 | 从触发器一致传递 sessionId 至内存和工具 |
| 两个几乎相同的工具而不是一个带分支的 | 模型混淆，选择非确定性 | 一个工具通过参数驱动内部分支 |
| 硬编码在多个工作流或频繁迭代中重复使用的系统提示 | 编辑需要重新发布，无法跨工作流共享，调整发生在节点 JSON 中 | 存储在数据表中，运行时加载 |
| 将图像 / 音频 / 视频生成包装在 Agent 中 | 二进制无法通过工具或输出格式器流出，Agent 添加无益节点 | 直接使用提供者的原生单调用节点（OpenAI 图像、Gemini 图像、ElevenLabs），仅在通过聚合器时使用 HTTP 请求 |
| Agent + Switch 基于自然语言输入路由 | 两个节点加上提示样板，而 Text Classifier 是一个节点并内置 N 个输出分支 | 使用 Text Classifier（`@n8n/n8n-nodes-langchain.textClassifier`），每个类别获得自己的输出处理，直接连接下游路径 |
| 无人工审查就改变用户可见状态（发送、支付、退款）的工具 | 代理在错误推理上触发不可逆操作 | 使用适合渠道的审查工具节点（Slack/Chat/Discord/Telegram），通过 `$tool.parameters` 显示实际参数 |
| 通过 `fromAi()` 填充审查批准消息 | 模型改写，你批准文本而不是值 | 直接使用 `$tool.parameters.<name>` 以便显示字面调用 |
| 触发器触发的代理工作流在回复时不过滤掉机器人自己的用户 ID | 机器人自己的消息重新触发工作流，无限循环消耗运行和令牌，直到速率限制或 n8n 并发停止 | 优先使用触发器级别的过滤（Slack 触发器的 `options.userIds` 是排除列表，将机器人 ID 放在那里）。否则在触发器后的第一个节点过滤 `$json.user !== '<BOT_USER_ID>'`（或界面等效项）。任何发送回复的聊天触发工作流都需要（Slack、Discord、Teams、Telegram），无论其复杂性如何。参见 `references/CHAT_AGENT_PATTERNS.md` 获取每个界面的语义 |
| 代理返回 Block Kit 时将裸块数组传递给 Slack 节点的 `blocksUi` | Slack 节点静默接受输入并发布没有丰富内容的消息；无错误，无警告 | 包装为 `{ "blocks": [...] }` 并将值作为真实数组，而不是字符串化的。表达式：`={{ { "blocks": $('Agent').item.json.output.blocks } }}`。参见 `n8n-node-configuration-official` `references/COMMS_NODES.md` "Block Kit 消息" |
