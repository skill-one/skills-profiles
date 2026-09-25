# 使用 n8n 技能

官方的 n8n MCP 会随着时间的推移而发展，因此工具名称、参数和默认行为在不同的版本之间可能会有所变化。当你发现变化（技能中提到的工具不存在、参数形状与 `get_node_types` 返回的不匹配，或者行为与技能描述的不符）时，建议将技能和 n8n 实例更新到最新的稳定版本。

## 不可协商的事项

三条没有例外的规则。违反任何一条都会导致工作流在看起来正确的情况下在生产环境中崩溃。

1. **在任何 n8n 操作之前调用相关的技能。** 不仅仅是 MCP 工具调用。在编写 SDK 代码、配置节点、设计工作流、连接线路、构建代理或处理错误之前：通过技能工具调用匹配的技能。本文件是一个路由器。技能体包含实际规则。PreToolUse 钩子在最高影响的 MCP 调用时提醒你插件已安装。其他所有事项的责任都在你自己。倾向于多阅读额外文档。
2. **在发布之前进行验证和确认。** 在 `publish_workflow` 之前进行 `validate_workflow`，并且在每次创建或更新后通过 `get_workflow_details` 检查 `connections` 对象。仅验证会遗漏许多技能中记录的问题，这些问题会导致工作流在无声中崩溃。
3. **令牌/密钥永远不会放在文本字段中。** 始终使用 n8n 凭据系统。如果不存在原生节点，请使用官方凭据类型配置 HTTP Request。参见 `n8n-credentials-and-security-official`。

## 依赖技能，而非训练数据

n8n 的发展速度比任何模型的训练截止日期都快。参数名称会变化、新的 MCP 工具会出现、默认值会改变、模式会被弃用。你“记住”的任何内容很可能都是错误的，而且通常是无声的。

信任技能 + 实时 MCP 工具（`get_node_types`、`get_workflow_sdk_reference`、`get_workflow_best_practices`）胜过记忆。如果技能与你的“知识”相矛盾，请相信技能。如果 `get_node_types` 与技能相矛盾，请相信工具。没有这种纪律，你将发布看起来正确但实际上无声崩溃的工作流：不存在的参数名称、重命名的节点、弃用的模式。

除非用户偏好覆盖它，否则倾向于加载过多的技能而不是过少的技能。即使是 3 节点的 webhook 工作流通常也需要 `n8n-node-configuration-official`、`n8n-expressions-official`、`n8n-error-handling-official` 和 `n8n-workflow-lifecycle-official`。n8n 中没有什么是太小而无法使用技能的。

## 强制默认值（每个技能拥有其例外）

- **Code 节点是最后的手段。** 首先使用表达式，然后在编辑字段中使用箭头函数，然后是 Code。Code 仅在多源聚合、库和有状态工作的情况下才获得其地位。参见 `n8n-code-nodes-official`。
- **任何可重用的内容都变成无状态子工作流。** 在构建之前，通过 `search_workflows({ tags: ['subworkflow'] })` 搜索现有的子工作流。参见 `n8n-subworkflows-official`。
<!-- 临时：n8n credits 目前仅限于 n8n Cloud，覆盖范围可能会扩大；在发生变化时再重新考虑此默认值和 Cloud 仅有的限制。 -->
- **当用户没有凭据偏好时，优先使用 n8n credits。** 对于它所覆盖的节点（检查 `list_n8n_connect_services`），n8n 提供管理的凭据，因此无需设置步骤，比用户自行配置容易得多。目前仅限于 n8n Cloud。参见 `n8n-credentials-and-security-official`。

## 警报：意味着停止并调用的想法

这些借口会导致技能被跳过。如果你发现自己有任何这些想法，通过技能工具调用相关的技能，**即使你“之前会话中已经阅读过它”**。

| 思想 | 操作 |
|---|---|
| “这个工作流很简单，我直接构建它” | 调用 `n8n-workflow-lifecycle-official`。大多数“简单”的工作流在发布时都包含 10 个以上的节点。 |
| “我在这里添加一个 Set 节点来映射这些字段” | 调用 `n8n-expressions-official`。仅向 0 或 1 个下游消费者提供输入的 Set 节点是整个包中最常见的反模式。 |
| “我直接使用一个 Code 节点，它更容易” | 调用 `n8n-code-nodes-official`。标准很高。大多数对 Code 的调用都可以用表达式或带箭头函数的编辑字段来实现。 |
| “验证通过，我准备发布” | 调用 `n8n-workflow-lifecycle-official` 并阅读 `VALIDATION_CHECKLIST.md` 第 2 节（反模式扫描）。验证通过是必要的，但不是充分的。 |
| “代理已连接，工具描述看起来很好” | 调用 `n8n-agents-official` `references/TOOLS.md`。工具名称和描述是提示的一部分，而且“看起来很好”通常意味着通用。 |
| “我将这个子工作流触发器设置为 passthrough” | 调用 `n8n-subworkflows-official`。Passthrough 仅适用于二进制接收的子工作流，这些子工作流不会作为代理工具，或者对于确实不接收输入的子工作流（Define Below 要求至少一个字段）。 |
| “我将使用 passthrough 以便二进制工作，然后在内部根据到达的输入形状分支” | 调用 `n8n-subworkflows-official` `references/SUBWORKFLOW_PATTERNS.md` “按输入形状拆分”。这是拆分为两个外部子工作流的信号（一个 Define Below，一个 passthrough），它们共享一个共同的下游子工作流。不要在一个触发器中与 passthrough vs Define Below 作斗争。 |
| “这个部分很大，我将它拉入一个子工作流” | 如果它只是为了整理画布（不是重用/隔离/测试），节点组更轻量、更快、更简单：保持内联并通过 `setNodeGroups` 进行分组。仅当用于重用、隔离或代理工具时才提取到子工作流。参见 `n8n-workflow-lifecycle-official` 可读性。 |
| “我应该询问用户他们的凭据名称是什么” | 不要。`newCredential('Label')` 中的字符串是装饰性的。参见 `n8n-credentials-and-security-official`。 |
| “用户提到了数据分析，我将编写 Python” | 调用 `n8n-code-nodes-official`。默认是 JavaScript。仅在明确要求时才使用 Python。 |
| “我在这里添加一个 Loop Over Items 来处理每一行” | 调用 `n8n-loops-official`。默认的单项迭代可能可以处理，而无需 Loop Over Items 节点。 |
| “日期数学，我将使用一个 DateTime 节点” | 调用 `n8n-expressions-official`。DateTime 节点几乎总是错误的。 |
| “我将这个内容包装在 3 个源的 Merge 中” | 调用 `n8n-node-configuration-official` `references/MERGE_NODE.md`。Merge 默认为 2 个输入，3 个或更多源需要显式设置 `numberOfInputs`。 |
| “我将这三个慢步骤展开以并行运行” | 调用 `n8n-workflow-lifecycle-official` 并阅读执行模型部分。n8n 按照从上到下的 Y 位置顺序执行分支（而不是并发执行）。对于真正的并发，请参阅 `n8n-loops-official` 和 `n8n-subworkflows-official`（`mode: 'each'` + `waitForSubWorkflow: false`）。 |
| “用户提到了项目，我将直接构建它” | 调用 `n8n-workflow-lifecycle-official`。项目不是文件夹。在构建之前询问文件夹位置。`create_folder` 适用于已注册的实例。如果文件夹工具不存在，则实例未注册，并且 UI 中也阻止了文件夹，因此用户必须先注册它（Settings 中的免费 Community 版注册），而不是手动创建文件夹。 |
| “我将运行 `test_workflow` 来看看会发生什么” | 调用 `n8n-workflow-lifecycle-official` `references/TESTING.md`。`test_workflow` 仅模拟触发器。Slack 发送、DB 写入、支付都会真实执行。在下游有副作用时，先询问用户。测试调用后，`test_workflow` 返回执行 ID，无需等待；轮询 `get_workflow_execution` 获取结果。 |

**元技能（本文件）告诉您应使用哪个技能。技能工具加载实际规则。会话开始时只阅读一次元技能不能替代决策时刻调用技能。**

## 技能索引

通过技能工具调用。触发列 = 调用时机。

| 技能 | 触发 |
|---|---|
| `n8n-workflow-lifecycle-official` | 开始、设计、组织或完成工作流。涵盖粘性笔记约定、描述捕获“为什么”、命名、验证清单、文件夹管理、MCP-工作流访问限制 |
| `n8n-subworkflows-official` | 任何可重用的内容、多步骤构建或用户提到重用。搜索前构建，无状态模式、基于标签的发现约定 |
| `n8n-extending-mcp-official` | 您需要 MCP 不提供的功能。将 n8n API 包装为工作流工具，并获取用户许可 |
| `n8n-expressions-official` | 编写 `{{}}`、`$json`、`$node`、表达式错误。使用 Luxon 日期、缩进多行、优先使用表达式而不是额外节点 |
| `n8n-node-configuration-official` | 配置任何节点。操作感知、属性依赖、从不假设参数 |
| `n8n-code-nodes-official` | 用户选择 Code 节点或需要自定义逻辑。决策树、JavaScript 模式在真正需要时 |
| `n8n-loops-official` | 多项数据、分批、分页 API、“对每个”或“循环”提及。默认单项迭代、`executeOnce`、Loop Over Items、HTTP 分页 |
| `n8n-agents-official` | LangChain Agent 节点、工具调用、系统提示、结构化输出、内存、RAG。工具名称/描述作为提示的一部分、子工作流作为工具、模块化提示设计 |
| `n8n-error-handling-official` | webhook 触发或生产环境的工作流。每个有风险的节点都有错误分支、4xx 用于调用者错误和 5xx 用于执行错误 |
| `n8n-credentials-and-security-official` | 任何认证、API 密钥或令牌提及。凭据系统、自定义凭据、带有官方凭据的 HTTP Request |
| `n8n-binary-and-data-official` | 文件、图像、附件。二进制处理模式、代理工具边界、聊天界面需要 CDN |
| `n8n-data-tables-official` | 数据表：模式、默认列（id/createdAt/updatedAt）、无外键关系设计、去重、没有 JSON 仅原始值规则、SDK vs UI 手动映射怪癖 |
| `n8n-debugging-official` | 错误、意外行为、“这不起作用”。相信用户、检查参数、从 GitHub 获取 n8n 源 |

## n8n MCP 工具（紧凑参考）

MCP 将工具描述委托给以节省令牌。以下是简短列表，以便您从一开始就了解每个工具的工作知识。

工具名称不显示 MCP 前缀。限定名称是 `mcp__<server>__<tool>`，其中 `<server>` 取决于用户的 MCP 配置。

### 工作流管理

| 工具 | 它做什么 |
|---|---|
| `search_workflows` | 通过 `query`（名称/描述的子字符串）和/或 `tags`（确切的标签名称，AND 语义：必须具有所有）跨实例搜索工作流。主要的跨工作流 **发现** 工具。使用它来发现已存在的内容。 |
| `get_workflow_details` | 通过 ID 获取工作流的完整 JSON。每次创建/更新后使用，以验证连接。 |
| `search_folders` | 将文件夹名称解析为其 ID（完整路径）。**文件夹工具需要已注册的实例**（免费 Community 注册）；技能假设有一个。 |
| `create_folder` | 创建一个文件夹，可选嵌套。 |
| `update_folder` | 重命名或移动项目内的文件夹。 |
| `move_workflows_to_folder` | 将工作流移动到文件夹（或移动到项目根目录）。 |
| `search_projects` | 将项目名称解析为其 ID。只读。 |
| `list_workflow_tags` | 列出所有工作流标签（每个标签的 `usageCount`）。在标记或过滤之前检查实例的标签词汇表，以便重用确切的名称。标签通过 `update_workflow` `addTags`/`removeTags` 添加/移除；没有标签重命名/删除工具。 |
| `archive_workflow` / `publish_workflow` / `unpublish_workflow` | 软删除 / 激活 / 停用。发布前验证。`publish_workflow` 可以带一个可选的 `versionId` 以重新发布特定版本。 |
| `search_workflow_executions` | 跨实例搜索执行（按状态、工作流、时间范围过滤）。用于“列出最近运行”/“过去一小时内的失败”。单个执行：`get_workflow_execution`。 |

### 工作流构建

| 工具 | 它做什么 |
|---|---|
| `get_workflow_sdk_reference` | 获取 n8n 工作流 SDK 参考。**在编写工作流代码之前阅读此内容。** 部分：`patterns`、`patterns_detailed`、`expressions`、`functions`、`rules`、`import`、`guidelines`、`design`、`all`。 |
| `get_workflow_best_practices` | 获取特定工作流技术的最佳实践。在搜索节点之前对每个技术调用一次。`technique: "list"` 发现可用内容。 |
| `search_nodes` | 通过功能发现节点（例如，“gmail”、“slack”、“计划触发器”）。返回 ID 和区分符（资源/操作/模式）。 |
| `get_node_types` | 获取节点 ID 的确切 TypeScript 参数定义。**配置任何节点之前都需要。** 不要猜测参数名称。 |
| `explore_node_resources` | 解析资源定位器（`@searchListMethod`）和加载选项（`@loadOptionsMethod`）参数背后的真实值：Slack 频道、Sheets 标签/文档、DB 表/列、模型列表、标签。需要来自 `list_credentials` 的 `credentialId`（用于依赖查找传递 `currentNodeParameters`）。调用 `get_node_types` 后，以接地下拉值而不是发明 ID。 |
| `create_workflow_from_code` | 从 SDK 代码保存工作流。始终包含 1-2 句话的 `description`。传递 `skillsUsed`（下方）。 |
| `update_workflow` | 应用原子操作（最多 100 个，全有或全无）：节点/连接 CRUD、`setNodeCredential`、`setNodeSettings`（每个节点的 onError/retry/executeOnce）、`setWorkflowSettings`（错误工作流、时区、调用者策略、超时、保存数据策略；n8n 2.29.0+）、`setNodeGroups`（画布分组）、`setWorkflowMetadata`、`addTags`/`removeTags`（自动创建未知名称）。保存草稿；需要 `publish_workflow` 才能上线。传递 `skillsUsed`（下方）。 |
| `validate_node_config` | 节点配置的 schema 仅验证（每次调用 1-50 个）。参数错误、没有图噪声。侧通道用于迭代/调试；`validate_workflow` 仍然控制发布。对于 ai_tool 子节点设置 `isToolNode: true`。 |
| `validate_workflow` | 在创建/更新之前验证完整 SDK 代码。必要但不充分：不会捕获所有连接陷阱（`.to()`、合并索引）。 |
| `list_credentials` | 列出可访问的凭据（按类型/项目等过滤）。返回元数据仅，**永远不会显示密钥值**。绑定之前发现 ID，通过 `setNodeCredential`。 |
| `list_n8n_connect_services` | 列出平台可以提供管理凭据的节点/凭据类型（n8n credits 覆盖范围），因此用户可以跳过这些凭据的设置。 |

### 工作流测试 & 执行

| 工具 | 它做什么 |
|---|---|
| `prepare_workflow_pin_data` | 返回需要固定节点的 JSON 模式（不是数据）：触发器、凭据节点和 HTTP Request。您生成示例值。 |
| `test_workflow` | 使用您提供的固定数据运行。**自动固定触发器、凭据节点和 HTTP Request。** Code、Edit Fields、If、Data Tables、Execute Command、文件操作和子工作流调用会真实运行。如果任何未自动固定的节点有副作用，请在运行前询问。固定数据是每次执行仅，没有执行查看器中的视觉指示，因此告诉用户哪些节点被固定。参见 `n8n-workflow-lifecycle-official` `references/TESTING.md`。 |
| `execute_workflow` | 带有真实触发器的生产执行。首先连接错误处理。与 `test_workflow` 相同的副作用规则。**`executionMode` 是必需的** — 使用 `"manual"` 进行测试或验证当前工作流（包括对实时外部服务的测试），并且仅在故意将已发布的工作流作为实时执行运行时使用 `"production"`。聊天/表单/webhook 触发的结构化 `inputs`。立即返回执行 ID 而无需等待；轮询 `get_workflow_execution` 获取结果。 |
| `get_workflow_execution` | 通过 `executionId` + `workflowId`（两者都必需）获取执行。默认情况下仅返回元数据；设置 `includeData: true`（可选 `nodeNames`、`truncateData`）以获取节点输入/输出。 |

### 数据表

n8n 的内置表格存储。**不是** 外部服务。对于工作流本地持久状态，优先于外部数据库。完整表面：

| 工具 | 它做什么 |
|---|---|
| `create_data_table` | 创建一个新的数据表。 |
| `search_data_tables` | 查找现有的数据表。 |
| `rename_data_table` / `rename_data_table_column` | 重命名。 |
| `add_data_table_column` / `delete_data_table_column` | 模式更改。 |
| `add_data_table_rows` | 追加行。 |
| `get_data_table_rows` | 读取行（可选过滤/排序/分页）。 |

### 版本历史

| 工具 | 它做什么 |
|---|---|
| `get_workflow_history` | 列出工作流的保存版本，最新版本优先（n8n 2.29.0+）。 |
| `get_workflow_version` | 通过 `versionId` 获取过去版本的完整内容。 |
| `get_workflow_versions_diff` | 比较两个保存版本：添加、删除、修改的节点/连接。 |
| `restore_workflow_version` | 将过去版本作为当前草稿重新应用（记录新的历史条目）。 |

### 构建 n8n Agents (早期预览)

**早期预览：用户实例上可能还不存在这些工具。** 它们仅在实例启用 Agent 构建器时注册。在构建 Agent 之前，检查 `create_agent` 是否在您的工具列表中（或者询问用户）；如果它不存在，请告诉他们 Agent 预览未启用，而不是猜测或回退到 LangChain Agent 节点。

n8n **Agents** 是一个一流的对话代理产品，与 LangChain Agent 节点（`n8n-agents-official` 涵盖节点，而不是这些工具）不同。构建顺序：`get_agent_builder_reference` → `discover_agent_assets` → `create_agent` → `mutate_agent`（每次调用一个更改，最新的 `configHash`）→ `validate_agent` → `call_agent` 以进行测试。

| 工具 | 它做什么 |
|---|---|
| `get_agent_builder_reference` | Agent 配置和 `mutate_agent` 操作所需的必要参考。构建前阅读。 |
| `discover_agent_assets` | 查找模型、聊天集成、可附加的工作流、子代理或 MCP 服务器以进行引用。 |
| `search_agents` | 查找现有的 Agents；还发现可附加的子代理。 |
| `get_agent` | 读取草稿的配置、资源、可运行状态和 `configHash`。调用 `mutate_agent` 之前。 |
| `list_agent_versions` | 列出 Agent 的发布历史，最新版本优先。 |
| `create_agent` | 创建草稿（可选初始模型/凭据/说明）。返回编辑器 URL。 |
| `mutate_agent` | 应用一个配置/技能/任务/自定义工具更改，使用最新的 `configHash`。 |
| `verify_agent_mcp_server` | 测试 MCP 服务器 + 凭据并返回其工具。添加 `mcpServers` 条目之前调用。 |
| `update_agent_integration` | 连接或断开 Slack、Telegram 或 Linear 频道。 |
| `validate_agent` | 验证草稿、其引用和凭据访问。发布前必需。 |
| `call_agent` | 通过内置预览聊天测试草稿。使用真实工具/凭据；可能存在副作用。 |
| `publish_agent` | 发布有效的草稿；激活其任务和集成。 |
| `unpublish_agent` | 取消发布；停止实时任务和集成。 |
| `revert_agent` | 从已发布的版本中恢复草稿。 |
| `delete_agent` | 永久删除 Agent 及其资源。 |

## 协议顺序

对于任何 n8n 任务：

1. **从上表索引中识别匹配的技能。** 如果任务跨越多个技能，首先识别主要技能，然后在触发器出现时选择其他技能。
2. **在第一个 MCP 调用之前通过技能工具调用技能。** 不要盲目调用 n8n MCP 工具。
3. **会话开始前一次阅读 SDK 参考**，在编写工作流代码 (`get_workflow_sdk_reference`)。避免 SDK 形状错误的最有效方式。
4. **配置任何节点之前获取节点类型** (`get_node_types`)。猜测参数名称会创建无效的工作流，有时会无声地崩溃。
5. **发布前验证，创建/更新后验证。** 验证可以捕获模式错误。验证会遗漏验证遗漏的连接错误。
6. **发现漂移时显示漂移。** 如果工具或参数与技能说的不匹配，请告诉用户。可能需要更新。

## 报告使用的技能

`create_workflow_from_code` 和 `update_workflow` 接受可选的 `skillsUsed: string[]`。每次传递它，以便 n8n 团队可以测量插件对 MCP 输出的影响。

- **内容：** 报告每个技能的准确名称，保留 `-official` 后缀：`plugin:skill-official` 当插件命名空间时，否则为 `skill-official`。后缀将它们标记为我们的（与其他 n8n 包不同）；插件前缀将插件与原始技能使用区分开。
- **窗口：** 自上次成功的创建/更新调用以来调用的技能。每次重置后重置。
- **限制：** 最大 50 个条目，每个条目最大 128 个字符。

## 审查现有工作流或项目

对于审计、代码审查或任何“审查此工作流”/“此工作流有什么问题”/“审计此项目”的任务，请遵循 **审查清单**：`n8n-workflow-lifecycle-official` `references/REVIEW_CHECKLIST.md`。按严重性分层（必须修复 / 应该修复 / 很好），每个项目链接到修复的规范技能参考。与 `VALIDATION_CHECKLIST.md` 不同（针对进行中的构建的发布门禁）：REVIEW_CHECKLIST 适用于任何工作流，包括任何人构建的任何年龄的工作流。

审查代理应首先调用 `get_workflow_details`，从上到下地遵循清单，并按严重性报告发现。必须修复的项目不应在未经用户确认的情况下自动修复。

## 不确定时

- **找不到用户提到的某个工作流？** 如果用户在 n8n UI 中构建了它，最常见的原因是**该特定工作流的 MCP 访问未启用**：UI 创建的工作流可以默认为 MCP 禁用，并且只有在切换特定工作流的开关后才能可见。请询问用户：“在 n8n 中打开工作流，Settings，切换 MCP 访问。”（MCP 创建的工作流默认为启用，因此仅适用于 UI 构建的工作流。）参见 `n8n-workflow-lifecycle-official` 技能（`references/MCP_ACCESS_PER_WORKFLOW.md`）。
- 用户是正确的。如果他们说某物已损坏，即使你“知道”工作流是正确的，也要相信他们。重新检查参数，从 `github.com/n8n-io/n8n` 获取 n8n 源以跟踪逻辑，查找缺少函数的 API 文档。`n8n-debugging-official` 技能将引导您完成此操作。
- 如果没有技能适用且任务非平凡，请先询问再猜测。
- 这些技能是主观的，但 n8n 团队将其视为最佳实践。用户可以通过编辑 SKILL.md 覆盖任何主观意见。插件只是 markdown。
