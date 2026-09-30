---
name: using-n8n-mcp-skills
description: 在通过 n8n-mcp MCP 服务器构建、编辑、验证、测试或调试 n8n 工作流时使用——无论是设计流程、配置节点、编写表达式或 Code 节点、连接凭证，还是修复出现问题的流程。n8n-mcp-skills pack 的入口技能：它将引导你找到正确的专家技能，从第一步起就提供对每个 n8n-mcp 工具的工作知识，并阐明防止工作流在生产环境中出错的规则。在处理任何 n8n、工作流、节点或自动化任务时，务必首先查阅它——即使只是快速的一次性任务，即使用户未指定任何技能——因为 n8n 的界面在不同版本间会发生变化，而专家技能可以防止静默失败。
---

# 使用 n8n-mcp 技能

这是一个**路由器**，而不是参考。它告诉你哪些技能拥有你即将执行的操作的规则。技能体包含实际指导——使用技能工具调用它们。如有疑问，加载更多技能而不是更少。

社区 **n8n-mcp** 服务器和 n8n 本身比任何模型的训练截止日期都移动得更快。工具名称、参数、节点 `typeVersion` 和默认行为在各个版本之间会发生变化。当你发现变化——技能名称的工具不存在、参数形状与 `get_node` 返回的不匹配、行为与技能描述的不同——相信**实时工具**，告知用户，并建议更新包和实例。

## 不可协商的规则

三条没有例外的规则。每一条都防止了一类看起来正确但在生产中会出问题的流程。

1. **在执行任何 n8n 操作之前调用相关的技能**——不仅仅是 MCP 调用之前。在编写表达式、配置节点、设计工作流、连接线路或编写代码之前，调用匹配的技能。PreToolUse 钩子会在最高影响的工具调用时提醒你，但它们**仅存在于 Claude 代码插件安装中**。在其他地方——Claude.ai 技能上传，以及任何将此包加载为代理插件（Codex、Cursor、Copilot 等）的客户——没有任何提示，责任完全在于你自己。除非你看到本次会话中钩子被触发，否则假设你没有钩子。

2. **在激活之前进行验证和确认**。在激活之前运行 `validate_workflow`（或通过 ID 运行 `n8n_validate_workflow`），并在每次创建或更新后调用 `n8n_get_workflow` 来检查 `connections` 对象。仅验证会无声地遗漏掉线路、Merge 索引错误和从未连接的错误输出。验证通过意味着 JSON 格式良好——并不意味着工作流正确。绿色的测试运行也不是证明：`{{ }}` 内的 JS 错误会无声地解析为 `null`（带有损坏条件的 Filter 会丢弃每个项目但仍然显示成功），所以请检查输出值。参见 `n8n-expression-syntax`。

3. **秘密永远不会放在文本字段中**。令牌、API 密钥和密码始终通过 n8n 凭证系统传递。如果没有原生节点存在，请使用带有官方凭证类型的 HTTP Request 节点。一个持有通过 `{{ $json.token }}` 引用的令牌的 Set 节点是一个带有额外步骤的泄漏。参见 `n8n-mcp-tools-expert`。

## 依赖技能，而非训练数据

n8n 不断变化。"记住"的参数名称通常是无声错误的——它们作为普通字符串验证，然后在运行时什么也不做。相信技能和实时工具（`get_node`、`search_nodes`、`tools_documentation`）而不是记忆。如果技能与你的记忆相矛盾，相信技能。如果 `get_node` 与技能相矛盾，相信工具并标记漂移。

## 强制默认值

每个技能拥有自己的例外；这些是默认值。

- **Code 节点是最后的手段**。首先使用表达式，然后在编辑字段内使用箭头函数，只有在两者都无法完成任务时才使用 Code 节点。参见 `n8n-code-javascript`。
- **一个向 0-1 消费者提供数据的 Set 节点几乎总是错误的**。在消费者处内联表达式。参见 `n8n-expression-syntax`。
- **逐项迭代是自动的**。当默认逐项执行已经处理这种情况时，不要添加一个 Loop Over Items 节点来“让它循环”。
- **从实时模式配置，而不是从记忆中配置**。在设置参数之前使用 `get_node`。参见 `n8n-node-configuration`。

## 警报：“即将 ___” → 调用 ___

如果你发现自己想到任何这些，请停止并首先调用命名的技能。

| 思考 | 调用 |
|---|---|
| “这个工作流很简单，我直接构建它” | `n8n-workflow-patterns` — 大多数“简单”的流程都包含 10 个以上的节点 |
| “我会添加一个 Set 节点来映射这些字段” | `n8n-expression-syntax` — Set 节点向 ≤1 消费者提供数据是 #1 反模式 |
| “我直接使用一个 Code 节点，它更容易” | `n8n-code-javascript` — 标准很高；大多数尝试都是表达式或编辑字段 |
| “用户提到了数据，我会写 Python” | `n8n-code-javascript` — 默认 JS；Python (`n8n-code-python`) 仅在明确要求时使用 |
| “我正在编写 AI 代理将调用的代码” | `n8n-code-tool` — 与 Code 节点不同的运行时契约 |
| “日期计算——我会插入一个 DateTime 节点” | `n8n-expression-syntax` — Luxon 内联几乎总是正确的 |
| “我会连接一个 3 个源的 Merge” | `n8n-node-configuration` — Merge 默认为 2 个输入；第 3 个会无声地丢失 |
| “验证通过，我准备激活” | `n8n-validation-expert` + `n8n-workflow-patterns` — 运行反模式扫描 |
| “验证抛出了一个我不理解的错误” | `n8n-validation-expert` — 每个错误和警告的含义，以及哪些是必须修复的，哪些是最佳实践建议 |
| “我在这里引用 `$json.x`” | `n8n-expression-syntax` — 在分支式工作流中优先使用 `$('Node').item.json.x` |
| “这个 webhook/计划工作流只有成功路径” | `n8n-error-handling` — 在每个可能出错的节点上连接错误分支；4xx 调用方错误，5xx 是你的 |
| “我会将这个文件/图像作为 JSON 传递” | `n8n-binary-and-data` — 文件内容存储在 `$binary` 中，并且不能跨越代理工具边界 |
| “我会连接一个 AI 代理并给模型一些工具” | `n8n-agents` — 工具名称和描述是提示；内存、结构化输出和拓扑结构有陷阱 |
| “我会将这个逻辑复制到另一个工作流中” / “这个变得太大了” | `n8n-subworkflows` — 提取可重用的子工作流；在构建之前搜索 |
| “我会创建那个凭证 / 打开那个工作流”（账户有 >1 个实例） | `n8n-multi-instance` — 每个调用都针对当前目标实例；读取错误路由会无声，并且一个模糊的凭证写入会以 `INSTANCE_AMBIGUOUS` 失败关闭 |

## 技能索引

| 技能 | 在以下情况下使用 |
|---|---|
| `using-n8n-mcp-skills` | 这个路由（自动加载）。命名拥有你任务的技能。 |
| `n8n-mcp-tools-expert` | 选择或调用任何 n8n-mcp 工具；节点发现；凭证；数据表；安全审计；模板 |
| `n8n-workflow-patterns` | 设计或构建工作流；选择架构（webhook / HTTP API / 数据库 / AI 代理 / 计划 / 批处理） |
| `n8n-node-configuration` | 配置任何节点；操作感知必需字段；属性依赖；手术字段编辑 |
| `n8n-expression-syntax` | 编写 `{{ }}`，`$json`/`$node`/`$now`；在节点之间映射数据；转换门禁；Set 节点纪律 |
| `n8n-validation-expert` | 解释验证错误/警告；误报；验证循环；自动修复；审查现有工作流 |
| `n8n-code-javascript` | 任何 JavaScript 中的 Code 节点；数据访问；`this.helpers`；DateTime；SplitInBatches 循环模式 |
| `n8n-code-python` | 特定请求为 Python 的 Code 节点；原生运行时（`_items`/`_item` 仅，默认阻止导入，遗留 `_input` 代码失败） |
| `n8n-code-tool` | 可由 AI 代理调用的自定义代码工具（`toolCode`）——返回字符串，没有 `$fromAI`/`$input` |
| `n8n-error-handling` | webhook/API 或无人值守工作流；连接错误输出；重试；4xx/5xx 响应形状；无声失败 |
| `n8n-binary-and-data` | 文件、图像、PDF、附件、上传/下载、视觉；将文件传递给/从代理工具 |
| `n8n-subworkflows` | 可重用/多步构建；执行工作流；提取共享逻辑；Define-Below 输入；所有 vs 每个；将工作流作为代理工具公开 |
| `n8n-agents` | AI 代理 / LLM 带工具 / 文本分类器；工具设计 & `$fromAI`；系统提示；结构化输出；内存；RAG；人工审查；聊天机器人 |
| `n8n-multi-instance` | 多个实例的账户（`n8n_instances` 工具存在）；切换目标实例；在凭证写入之前验证；从意外的 `NOT_FOUND`、错误/空读取或 `INSTANCE_AMBIGUOUS` 凭证写入失败关闭中恢复 |
| `n8n-self-hosting` | *部署，不是工作流构建* — 在 VM 上自我托管/安装/部署 n8n（Docker Compose + Caddy，单 vs 队列模式），或更新/备份/加固它。它自己触发；不是上面构建流程的一部分。 |

## n8n-mcp 工具——从一开始就需要掌握

限定名称看起来像 `mcp__<服务器>__<工具>`（`<服务器>` 通常是 `n8n-mcp`）。这弥补了工具的完整描述直到第一次使用后才加载的差距。

**两个级别，以及如何确定你拥有哪个级别**。下面的文档和验证工具可以在离线状态下工作，并且始终存在。`n8n_*` 管理工具与实时 n8n 实例通信，并且**只有在连接后才会出现**。如果它们不存在，则没有损坏，也没有需要重试的——直截了当地告诉用户他们安装的正确修复方法：

- **托管 (`https://api.n8n-mcp.com/mcp`)** — 通过客户端在第一次使用时显示的 OAuth 提示进行登录，然后在仪表板中连接 n8n 实例。不需要环境变量，也不需要将 API 密钥粘贴到配置文件中。
- **自我托管 (`npx n8n-mcp`，Docker)** — 服务器需要在环境中具有 `N8N_API_URL` 和 `N8N_API_KEY`，在客户端启动之前导出。

`n8n_health_check` 确认工作连接并返回解析的实例。

**发现和文档**
- `tools_documentation` — 每个工具的元文档；`{topic:"ai_agents_guide", depth:"full"}` 用于代理指南。
- `search_nodes` — 通过关键字查找节点。
- `get_node` — 节点信息。接受单个 **短形式** `nodeType`（`nodes-base.httpRequest`，`nodes-langchain.agent`），加上 `detail`（最小/标准/完整）和 `mode`（info/docs/search_properties/versions）。
- `validate_node` — 独立验证一个节点的配置（配置文件：最小/运行时/对 AI 友好/严格）。
- `search_templates` / `get_template` — 模板库（通过关键字、节点、任务、元数据）。

**构建和编辑**
- `n8n_create_workflow` — 从完整的 workflow JSON 创建。
- `n8n_update_partial_workflow` — 增量差异操作（`{id, operations:[…]}`）：addNode, updateNode, patchNodeField, addConnection, setNodeGroups, activateWorkflow, 等。编辑的首选方式。
- **画布组**（n8n 2.28+）在您的编辑后无需管理即可生存：您移除的分组节点会从其组中剪裁，而 n8n 无法再接受的组会被取消分组，以便编辑仍然有效——节点和连接未受影响，每个调整都在 `details.warnings` 中报告。要创建或更改组，请使用 `setNodeGroups` 操作（完整替换；`[]` 取消所有分组）。参见 `n8n-mcp-tools-expert`。
- `n8n_update_full_workflow` — 完整替换。
- `n8n_autofix_workflow` — 自动修复常见问题。
- `n8n_deploy_template` — 将模板部署到实例。

**验证**（必要但不充分——始终与反模式扫描配对）
- `validate_workflow` — 完整 JSON 输入，错误/警告/修复输出。这里的节点类型是 **长形式** (`n8n-nodes-base.set`)。
- `n8n_validate_workflow` — 通过 `{id}` 验证已部署的工作流（不需要检查节点 JSON）。

**检查和生命周期**
- `n8n_get_workflow` — 获取工作流（完整/结构/活动/过滤/最小）。使用它来验证编辑后的 `connections`；`mode="filtered"` + `nodeNames` 读取一个重节点（例如长 Code 源）而不拉取整个工作流，这可能会截断客户端。`n8n_list_workflows` — 列出/过滤（在复制逻辑之前搜索）。
- `n8n_delete_workflow`, `n8n_workflow_versions`（历史/回滚/差异；`source: "local"` = n8n-mcp 自己的快照，`source: "native"` = n8n 自己的历史包括 UI 中人们进行的编辑——参见 `n8n-mcp-tools-expert`），`n8n_instances`（仅限多实例账户：列出/切换目标实例——参见 `n8n-multi-instance`），`n8n_health_check`（返回解析的 `instanceName`，以及一个 `officialMcp` 块，说明下方的实例级 MCP 服务器是否配置且可访问）。

**测试和运行**
- `n8n_test_workflow` — 运行真实节点（Code、HTTP、DB 写入、发送所有触发）。在存在副作用时，先询问用户再运行。`method` 选择路径：`auto`（默认）和 `trigger` 通过 HTTP 在**活动**工作流上触发 webhook/表单/聊天触发器；`prepare`/`pinned`/`direct` 通过 n8n 自己的 MCP 服务器路由，可以运行没有任何 HTTP 触发器的工作流（手动、计划、子工作流）——参见 `n8n-mcp-tools-expert`。
- `n8n_executions` — 列出/检查执行。**没有 `execute_workflow` 工具。**
- `n8n_evaluations` — 评估测试运行：列出运行、聚合指标、每个案例结果（n8n ≥ 2.30），加上 `run`/`cancel` 来启动或停止运行（n8n ≥ 2.32）。`run` 对其整个数据集执行工作流——真实节点会触发，所以先询问用户。403 可能意味着 API 密钥在创建之前就创建了该操作的最低版本（为测试运行范围重新创建它），评估在计划上未许可，或密钥的所有者缺乏对工作流的访问权限——对于 `run`/`cancel`，特别是 `workflow:execute` 范围。

**数据、文件夹、凭证、审计**
- `n8n_manage_datatable` — 数据表 CRUD、过滤、干运行。`addColumn`/`deleteColumn`/`renameColumn` 通过 n8n 的 MCP 服务器更改现有表的列（公共 API 无法更改）——`deleteColumn` 会连同列的值一起删除它。
- `n8n_manage_folders` — 工作流文件夹 CRUD，包含计数（n8n ≥ 2.19，注册社区层及以上；`projectId` 默认为 `personal`）。通过 `parentFolderId` 在 `n8n_create_workflow` 或 `moveToFolder` 操作（n8n ≥ 2.32）上放置工作流。放置是只写——通过文件夹的 `get` 计数验证，而不是通过读取工作流。没有 `transferToFolderId` 的 `delete` 将文件夹的工作流移动到项目根目录并存档它们——它们仍然存在，但已停用（`transferToFolderId: "0"` = 移动到项目根目录而不存档）。
- `n8n_manage_credentials` — 凭证 CRUD + `getSchema` 发现。
- `n8n_audit_instance` — 安全审计（硬编码的秘密、未经身份验证的 webhook、错误处理差距）。

**实例级 MCP 服务器**——公共 API 旁边的第二个端点，由 `N8N_MCP_ACCESS_TOKEN`（n8n 2.34+）控制。`n8n_health_check` 报告它是否可访问；如果没有它，这些调用会回答 `NOT_CONFIGURED` 而不是奇怪地失败。
- `n8n_manage_agents` — 持久的 n8n **代理**：一个独立的助手工件，具有自己的生命周期（模型、说明、技能、任务、内存、通道），**不是** AI 代理工作流节点。`call` 使用真实凭证实时运行它，并可能返回 `approvals[]`；`publish` 仅在用户要求时使用。参见 `n8n-agents`。
- `n8n_explore_node_resources` — 通过真实凭证解析节点的实时下拉/资源定位器值，而不是猜测 ID。参见 `n8n-node-configuration`。
- `n8n_list_catalog` — 列出 `projects`（以获取 `projectId`）或 `tags`。这里唯一的工具是它也可以在没有令牌的情况下工作。
- 同一个服务器支持 `n8n_test_workflow` `prepare`/`pinned`/`direct`，`n8n_workflow_versions` `source: "native"`，以及 `n8n_manage_datatable` 列表操作。这些在“MCP 中可用”设置上按工作流额外控制；拒绝读取 `WORKFLOW_NOT_EXPOSED`，并且打开该设置（`exposeToMcp: true`）是一个可见的持久性更改——先询问用户。

> **节点类型形式陷阱**：`get_node` / `validate_node` 接受短形式（`nodes-base.set`）；`validate_workflow` / `n8n_create_workflow` 内的工作流 JSON 使用长形式（`n8n-nodes-base.set`）。混合它们是一个常见且无声的错误——参见 `n8n-mcp-tools-expert`。

## 协议，按顺序

1. 从索引中识别匹配技能，并在**首次调用MCP之前调用它**。
2. 如果你不确定，每次会话中浏览一次`tools_documentation`以刷新工具界面。
3. 在配置任何节点之前使用`get_node`——读取实时架构，不要假设。
4. 构建/编辑后，在**激活之前使用`validate_workflow`**，并在**之后使用`n8n_get_workflow`**以检查连接。
5. 提交你注意到的任何偏差（缺少工具、参数更改、行为偏离）。

## 疑惑时

- **找不到用户在UI中构建的工作流？** 最常见的原因是每个工作流的MCP访问被关闭。请他们打开n8n，进入设置，并启用MCP访问。
- **用户说它出错了？** 相信他们。对照`get_node`重新检查参数，追踪数据引用，检查执行情况。参考`n8n-validation-expert`。
- **没有技能匹配且任务非简单？** 在猜测之前先询问。

这些都是主观的最佳实践，而非法规。不同意某个决定？所有内容都是markdown——编辑技能即可。
