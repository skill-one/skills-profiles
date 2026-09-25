# n8n 代理

n8n Agent 节点（`@n8n/n8n-nodes-langchain.agent`）是一个多轮 LLM 驱动，包含模型、内存、工具和可选输出解析器的子节点。

## 何时使用 Agent 节点与原始聊天完成

决策：

- **需要工具调用、多轮推理或内存？** 使用 Agent。当你不想考虑这些时，它也是一个很好的默认选项：在整个工作流中统一使用 Agent 是合理的，并且简化了升级路径。
- **想要最轻量级的单次文本输出调用？** 基础 LLM 链 (`@n8n/n8n-nodes-langchain.chainLlm`) 配合聊天模型子节点（`OpenRouter Chat Model`、`OpenAI Chat Model`、`Anthropic Chat Model` 等）。没有代理循环，没有工具/内存/解析器插槽，更容易调试。注意：聊天模型节点是子节点，它们不会独立运行。它们会接入链或代理。如果希望标准化，Agent 也适用。
- **根据自然语言输入路由到 N 个输出分支（AI 的工作是选择分支）？** 使用文本分类器节点（`@n8n/n8n-nodes-langchain.textClassifier`）。N 个输出处理，每个类别一个，下游路径直接接入每个。每个类别都需要名称和描述（描述是模型选择的内容，仅名称不足以说明）。设置 `options.enableAutoFixing: true` 以增强边缘输入的鲁棒性。搭配聊天模型子节点（`OpenRouter Chat Model`、`OpenAI Chat Model` 等）。不要使用 Agent + Switch 来实现这一点。文本分类器是一个节点，并且是专门为此设计的。
- **结构化输出但没有工具？** Agent 是一个更简单的默认选项，并考虑了未来的扩展。基础 LLM 链也接受 `outputParserStructured` 子节点，并且在你想要更轻量级节点时工作良好。
- **图像 / 音频 / 视频生成？** 当直接调用提供者时（OpenAI Image、Gemini Image、ElevenLabs 等）的提供者的原生单次调用节点。当通过聚合器路由时（OpenRouter、Together 等），使用 HTTP 请求，因为没有原生聚合器节点，并且原生节点在媒体操作中硬编码了提供者的基本 URL。**不要将媒体生成包装在 Agent 中**，见下文“二进制与代理边界”。

还有其他用于狭窄任务的 LangChain “链” / 工具节点：信息提取器（从文本中提取结构化字段）、情感分析（3 路分支）、摘要链、基础 LLM 链。

Agent 对于大多数 LLM 步骤是一个合理的默认选项。当你需要更轻量级的节点来执行单次文本调用，并且没有工具、内存或迭代时，请使用基础 LLM 链。当你需要其中一个专门设计的节点来匹配任务时，请使用信息提取器 / 情感分析 / 摘要链 / 文本分类器。

## 不可协商项

1. **工具名称和描述是提示的一部分。** 模型通过名称和描述选择工具。像 (`doStuff`) 这样模糊的工具节点名称或弱描述（“用数据做事情”）会导致静默失败：模型跳过你的工具、错误选择它或凭空想象参数。将两者都视为 API 设计。见 `references/TOOLS.md`。
2. **结构化输出：解析和 autoFix。** `outputParserStructured` 配合 `autoFix: true` 和一个编码能力强的修复模型（例如，Claude Sonnet 4.6）是生产模式。

## 强制默认值

- **工具描述是模块化的提示片段。** 任何特定于 *如何调用此工具* 的内容都属于工具的描述，而不是系统提示。这使系统提示保持专注，并且工具可以在不同的代理中重复使用。见 `references/SYSTEM_PROMPT.md`。
- **子工作流工具（`toolWorkflow`）用于任何多步操作。** 任何工作流都成为具有类型 `fromAi()` 输入的工具，并与分支、错误处理、子工作流组合。见 `references/SUBWORKFLOW_AS_TOOL.md`。
- **将具有用户可见副作用的工具包装在人工审核中。** 发送、支付、退款、账户更改。通过 Slack / Chat / Discord / Telegram 批准节点来控制它们，以便在工具运行之前有人签字。见 `references/HUMAN_REVIEW.md`。

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
- **`tools`**（可选，但使用 Agent 的要点）：代理可以调用的工具。见 `references/TOOLS.md`。
- **`outputParser`**（可选）：强制结构化 JSON 输出。见 `references/STRUCTURED_OUTPUT.md`。

## 触发器

不同的触发器以不同的方式塑造输入：

- **聊天触发器（`@n8n/n8n-nodes-langchain.chatTrigger`）** 配合 `availableInChat: true`：为画布聊天测试器提供动力，以便在构建它时可以“戳”代理。输入是 `{ chatInput, sessionId, files[] }`。`sessionId` 是内存键的触发器，因此将其传递到需要对话连续性的任何地方。文件通过 `files[]` 提供，见二进制部分。这不是生产界面，使用 Slack / Discord / Teams / Telegram / webhook。
- **Webhook**：任意输入形状，默认没有会话。通过在请求体中传递会话/对话 ID 并将其转发到内存节点来管理连续性。
<!-- 临时：在发布新代理范式时更新以下内容 -->
- **外部聊天界面（Slack、Discord、Teams、Telegram）**：每个由聊天触发的工具新回复都必须过滤掉机器人自己的用户 ID，否则它将无限循环，可能崩溃 n8n。当界面支持时，请优先使用触发器级别的过滤（Slack 的 `options.userIds` 是一个排除列表）；否则，在触发器之后的第一个节点中过滤。每个界面的语义不同，见 `references/CHAT_AGENT_PATTERNS.md`。除了反循环过滤器之外，一个简单的代理（触发器 → 代理 → 回复）在一个工作流中是足够的。一旦你需要加载 UX、子代理、跨界面重用或健壮的错误处理，就将其拆分为“外壳”工作流 + 代理核心子工作流。
- **手动 / 定时**：临时调用。内存很少有用，除非明确继续以前的运行。
- **执行工作流触发器**（子工作流）：当代理本身是另一个代理的工具时。将触发器声明的输入视为合同。

## 二进制与代理边界

模型可以通过 `passthroughBinaryImages: true` *看到* 上传的文件（视觉）。但**工具不能接收二进制**，`fromAi()` 参数仅限于 JSON。Base64 也不被工具接受，即使通过非 AI 绑定。

解决方法：在工作流运行之前将上传预置到存储中，将存储键注入系统提示，工具将键作为字符串参数接收并内部重新获取。完整模式在 `n8n-binary-and-data-official` `references/AGENT_TOOL_BINARY.md`。

输出端：Agent 的输出格式器是文本形状的（当连接了 `outputParser` 时为结构化文本）。当模型返回二进制（图像字节、音频字节、视频）时，Agent 不会显示它。下游没有可挖掘的内容，并且在 Agent 之后尝试通过代码或设置节点恢复它也不起作用。**对于单次媒体生成，直接使用提供者的原生单次调用节点，例如 `@n8n/n8n-nodes-langchain.googleGemini` 或 `@n8n/n8n-nodes-langchain.openAi`。**

例外：当媒体步骤确实属于代理（几个工具之一，基于对话上下文选择，或编辑先前生成的图像）时，解决方法是工具子工作流将结果上传到存储并返回键或 URL。模式在 `n8n-binary-and-data-official` `references/AGENT_TOOL_BINARY.md`。不要默认使用这种方法。上传 + 键 + 重新获取路径增加了节点和存储依赖，而您原本不需要这些。只有当编排实际上需要代理的工具选择时，才使用这种方法。

## 系统提示与工具描述的内容

| 属于系统提示 | 属于工具描述 |
|---|---|
| 个性、角色、声音 | 此特定工具的作用 |
| 输出格式规则（“以 markdown 响应”） | 何时使用此工具而不是其他工具 |
| 拒绝/安全行为 | 每个参数的含义及其预期形状 |
| 显示协议（“通过 `![]()` markdown 显示图像”） | 何时使用此工具 vs 其他工具 |
| 通用上下文（当前日期、用户角色） | 工具特定陷阱（速率限制、边缘情况） |
| 工具间流程（“生成后始终通过显示协议显示”） | 工具特定输入转换 |

优势：工具变得可重用。一个描述良好的工具可以在任何放入它的代理中工作。系统提示专注于角色和共享行为。

有关更深入的指导和示例，请参阅 `references/SYSTEM_PROMPT.md` 和 `references/TOOLS.md`。

## 工具选择：四种类型

选择覆盖工作的最轻量级选项：

- **存在原生 n8n 工具节点？**（例如，`slackTool`、`gmailTool`、`calculatorTool`）使用它。配置开销最低。
    - **原生节点缺少操作或需要自定义参数**（例如，节点不暴露的 Notion 端点、非标准标头、不同的分页形状）？使用服务器的“预定义凭证类型”的 HTTP 请求工具。重用现有的 OAuth / API 密钥凭证，提供完整的 API 访问，无需自定义认证代码。
- **多步逻辑，或重用项目中已有的子工作流？** 子工作流作为工具（`toolWorkflow`）。任何您可以构建为工作流的操作都成为具有类型 `fromAi()` 输入的工具。n8n 中最强大的选项，因此当不确定时默认为此。见 `references/SUBWORKFLOW_AS_TOOL.md`。
- **代理直接编排调用外部 HTTP API？** HTTP 请求工具。也适用于通过长轮询回调进行慢速异步工作。
- **工具已作为发布的、MCP 可访问的工作流存在？** MCP 工具。用于跨工作流的代理功能。见 `n8n-extending-mcp-official`。

有关每个选项的更深入指导和如何连接 `fromAi()` 参数，请参阅 `references/TOOLS.md`。

## 人工审核

在添加或跳过工具的人工审核之前，请与用户确认。无论是否需要签字是一个产品/策略决定（影响范围、审计要求、他们对模型的信任程度），用户比您更有能力做出决定。提出问题，根据以下标准提供建议，并让他们决定。

当工具的效果需要在执行之前获得人工批准（发送、支付、退款、账户更改、面向客户的操作）时，使用人工审核工具节点包装它：`slackHitlTool`、`discordHitlTool`、`telegramHitlTool`、`gmailHitlTool` 等（n8n 的节点名称使用 `Hitl` 表示人工回路模式，并且在 UI 中称为“人工审核”）。审核节点位于包装的工具和代理之间的 `ai_tool` 连接上：包装的工具的 `ai_tool` 输出连接到审核节点，审核节点的 `ai_tool` 输出连接到 Agent。代理调用，审核节点暂停以获取批准，批准后，包装的工具运行。

当工具发送、支付、退款或以其他方式改变用户可见状态时，默认为 / 建议人工审核：

- 审核者与聊天者不同（经理批准客户操作，支持团队批准客户触发的退款）。
- 触发器是非交互式的（订单、表单、计划），但工具的效果需要人工签字。

批准消息应显示**包装的工具将实际接收的参数**，而不是模型释义的文本。直接使用 `$tool.parameters.<name>`，或迭代 `$tool.parameters` 以列出每个参数。不要通过 `fromAi()` 填充批准文本。您将批准释义，而不是字面调用。使用实际值自定义按钮标签，例如 `Approve {{ $tool.parameters.amount }} refund`。

有关完整配置模式、每个平台的设置以及 `references/HUMAN_REVIEW.md` 中的多渠道审批者模式。

## 输出解析：何时以及如何

当下游需要结构化数据而不是自由文本时，添加 `outputParser` 子节点。

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

1. **使用 `schemaType: 'manual'` 与真实的 JSON 转换，而不是 `jsonSchemaExample`。** 示例无法表达可选字段、枚举、值范围或数组约束，因此一旦形状变得复杂，您就会超出它的范围。模式让您可以标记字段是必需的还是可选的，定义枚举，约束数字和字符串格式，并给模型更清晰的规则遵循。仅当您确信永远不会增长约束时，才使用 `schemaType: 'fromJson'` 与示例。
2. **`autoFix: true` 添加解析失败的重试。** 将编码能力强的模型作为修复子节点连接（例如，Claude Sonnet 4.6 或类似）。根据模式修复结构化输出/编码任务，弱或通用模型通常会产生另一个格式不良的重试，从而破坏了目的。

有关完整模式，包括自定义重试提示，请参阅 `references/STRUCTURED_OUTPUT.md`。

## 内存：简要心智模型

- **无内存**：无状态。适用于单次任务（分类、摘要）。
- **`memoryBufferWindow`**：保留每个内存键的最近 N 条消息，并通过 n8n 的内部存储跨执行持久化。键是您绑定到 `sessionKey` 的任何表达式。聊天触发器自动填充 `sessionId`，但您可以按任何内容键（Slack `thread_ts`、webhook 对话 ID、多租户组合）。聊天内存的默认设置。“窗口”是保持上下文的消息数量的滑动上限，而不是持久化的范围。
- **`memoryPostgres` / `memoryRedis` / 类似**：当您需要在代理**外部**查询或读取内存时使用这些：在您自己的 UI 中显示对话历史记录、对过去聊天的分析或与另一个系统共享内存。否则 `memoryBufferWindow` 足够。

始终从触发器到内存一致地引出一个稳定的键，否则对话会交叉。见 `references/MEMORY.md`。

## RAG（检索增强生成）

n8n 拥有 LangChain RAG 基础设施：文档加载器、文本分割器、嵌入、向量存储、检索器、重新排序器。这些组件可以工作，但意见一致的端到端配方（“哪个向量存储、哪个分块、何时重新排序”）严重依赖于数据形状和规模。

这项技能保持 RAG 意见的一致性是有目的的。有关 RAG 的更多详细信息，请参阅 `references/RAG.md`。

## 参考文件

| 文件 | 何时阅读 |
|---|---|
| `references/TOOLS.md` | 向代理添加工具，在四种工具类型之间进行选择，编写工具名称和描述 |
| `references/SUBWORKFLOW_AS_TOOL.md` | 通过 `toolWorkflow` 将子工作流作为代理工具连接，映射 `fromAi` 覆盖 |
| `references/SYSTEM_PROMPT.md` | 编写或重构系统提示，决定什么放入系统提示与工具描述 |
| `references/STRUCTURED_OUTPUT.md` | 强制 JSON 输出，配置 autoFix 重试，验证下游 |
| `references/MEMORY.md` | 选择内存类型，持久化和 sessionId 处理 |
| `references/RAG.md` | 构建检索增强代理，故意是一个占位符 |
| `references/HUMAN_REVIEW.md` | 向工具添加人工批准，配置批准消息，多渠道审批者模式 |
| `references/CHAT_AGENT_PATTERNS.md` | 在 Slack、Discord、Teams、Telegram 或任何自定义聊天界面构建聊天代理，多工作流外壳 + 核心 + 子代理拓扑 |

## 反模式

| 反模式 | 出现什么问题 | 修复 |
|---|---|---|
| 通用工具名称（`doStuff`、`runQuery`） | 模型无法确定选择哪个工具，跳过它们或凭空想象参数 | 动词优先的特定名称：`Search customer database`、`Generate image with Veo` |
| 空的或单行工具描述 | 模型不知道何时调用，选择不佳 | 编写真实的描述：它做什么，何时使用，参数含义 |
| 将所有内容都塞入系统提示 | 胖提示，无法重用，每工具指导被埋没 | 将工具特定指令移至工具描述，将系统提示保留为角色 + 全局规则 |
| 代码节点工具而子工作流可以工作 | 无法重用，无法独立测试，无法与分支组合 | 使用 `toolWorkflow` 并带有适当的子工作流 |
| 直接将二进制传递给 Slack 节点的 `blocksUi` 当代理返回 Block Kit | Slack 节点静默接受输入并发布消息，没有丰富的内容；没有错误，没有警告 | 包装为 `{ "blocks": [...] }` 并将值作为真实数组，而不是字符串化的一个。表达式：`={{ { "blocks": $('Agent').item.json.output.blocks } }}`。见 `n8n-node-configuration-official` `references/COMMS_NODES.md` “Block Kit 消息” |
