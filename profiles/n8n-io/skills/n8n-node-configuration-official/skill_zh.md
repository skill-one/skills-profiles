# n8n 节点配置

每个 n8n 节点都有自己的参数结构，通常包含条件字段（参数 X 仅在参数 Y 具有值 Z 时才有效）。结构会在不同版本之间演变。猜测会导致难以理解的验证错误。

不要猜测，使用 `get_node_types` 工具。

## 必须遵守的规则

**在配置节点之前，必须使用区分器（资源、操作、模式）调用 `get_node_types`。** 没有区分器时，你会得到通用结构，缺少特定操作的参数和必填字段。针对确切的结构进行构建。不要根据记忆进行猜测。

**实时 `get_node_types` 输出是规范的参数结构。** 此技能中的参考涵盖了模式、陷阱、安全规则和决策（何时使用哪个操作、为什么使用凭证而不是文本字段、引擎重试限制等），而不是参数名称或字段结构。如果参考示例与 `get_node_types` 返回的内容冲突，请相信工具。Markdown 会漂移；类型定义是从实时源生成的。

**永远不要猜测资源定位符或加载选项值。** 当 `get_node_types` 显示带有 `@searchListMethod` 或 `@loadOptionsMethod`（Slack 频道、Sheets 标签/文档、DB 表/列、模型列表、标签）的参数时，使用 `explore_node_resources`（传递来自 `list_credentials` 的 `credentialId`）解析实际值，并使用返回的 `value`。如果你已经知道确切的 ID，请使用它；如果多个匹配且意图不明确，请询问用户。虚构的 ID 可以验证但指向空值。例外：`toolWorkflow.workflowId` 没有搜索方法，通过 `search_workflows` 解析它，并使用 `mode: 'id'`。

## 强制性默认值

- **先配置操作。** 首先设置 `resource` 和 `operation`，条件参数就会可见。大多数“字段不存在”错误实际上是“你还没有设置父操作”。
- **不要跨操作携带参数。** 当更改 `operation` 时，重新从新结构中推导。来自先前操作的过时参数会触发验证。

## 新节点的流程

```
1. search_nodes(['<功能关键词>'])
   → 返回匹配的节点 ID + 区分器
2. 为任务选择正确的（资源、操作）。
3. get_node_types([{ name: '...', resource: '...', operation: '...' }])
   → 返回确切的参数结构，包括条件字段
4. 对于该结构中的任何 RLC / 加载选项参数，确定实际值：
   explore_node_resources({ nodeType, version, methodName, methodType, credentialType, credentialId, currentNodeParameters? })
   → 使用返回的 `value`。不要虚构 ID。
5. 根据该结构构建节点配置。
6. validate_workflow → 修复错误。
7. get_workflow_details → 检查保存的配置；确认参数已落地。
8. 使用固定数据 test_workflow → 确认运行时行为。
```

跳过任何步骤都会加剧下一个步骤的问题。最常见的跳过是步骤 3，导致“无法读取属性 X”错误，实际上是“你没有传递区分器”。

### `validate_node_config` 作为旁路

`validate_node_config([{ type, typeVersion, parameters, isToolNode? }])` 在隔离的节点配置上运行与 `validate_workflow` 相同的 Zod 模式。仅限模式级别；不会取代 `validate_workflow`（仍然是发布门）。更清晰的信号用于：

- **在构建中途迭代单个节点。** 比每次调整重新运行 `validate_workflow` 更快。
- **对现有工作流进行小修改。** 线路未更改？检查你触摸的节点；发布前进行完整验证。
- **调试配置错误的节点。** 每个参数错误，没有图噪声。

对于工具子节点（通过 `ai_tool` 连接），设置 `isToolNode: true` 以便评估正确的 `displayOptions` 分支。

## 操作感知配置

大多数节点有一个类似顶层结构的：

```ts
{
  resource: '<正在操作的实体>',   // 'message', 'spreadsheet', 'user', 等。
  operation: '<动词>',                      // 'send', 'append', 'lookup', 等。
  // ...操作特定参数
}
```

`(resource, operation)` 对决定其他参数是否存在（例如，Slack `(message, send)` 与 `(user, info)` 不同）。

模式：

1. 首先设置 `resource` 和 `operation`。
2. 如果你最初没有使用区分器，请使用这些区分器重新获取 `get_node_types`。
3. 根据操作特定结构进行配置。

## 属性依赖：微妙的陷阱

某些参数以不明显的方式依赖于其他参数：

- 只有当另一个字段具有特定值时，字段才是必需的。
- 字段的接受类型取决于模式。
- 字段的选项来自另一个字段的值。

示例：

- HTTP 请求 `authentication: 'genericCredentialType'` 需要 `genericAuthType` 和 `credentials`，但 `'predefinedCredentialType'` 需要不同的结构。
- Postgres `operation: 'executeQuery'` 需要 `query`，而 `operation: 'select'` 需要 `table` 和 `columns`。
- Slack `messageType: 'block'` 启用 `messageType: 'text'` 缺失的 block-builder 字段。

始终通过 `get_node_types` 检查特定操作。不要从不同操作复制配置并期望它通过验证。

来自另一个字段的选项是 `@loadOptionsMethod`：使用 `explore_node_resources`（`methodType: 'loadOptions'`）解析实时选项，在方法依赖于它们时通过 `currentNodeParameters` 传递先前的选择（例如，列出电子表格的标签需要 `documentId`）。

## 参考文件

按类别分类的陷阱。阅读你正在配置的节点类型的文件：

| 文件 | 何时阅读 |
|---|---|
| `references/HTTP_NODES.md` | 配置 HTTP 请求：认证、分页、查询/正文参数、重试 |
| `references/WEBHOOK_NODES.md` | 配置 Webhook 触发或 Respond to Webhook：正文解析、响应形状、异步模式 |
| `references/COMMS_NODES.md` | Slack、Gmail、Discord、电子邮件：凭证类型、消息形状、附件 |
| `references/DATABASE_NODES.md` | Postgres、MySQL、Mongo、Supabase：查询与操作、参数绑定、错误处理 |
| `references/AI_NODES.md` | AI Agent 节点配置旋钮：流式传输、视觉、`maxIterations`、模型子节点上的重试。将设计（提示、工具、内存、结构化输出）委托给 `n8n-agents-official` |
| `references/TRIGGER_NODES.md` | Webhook、计划、手动、Execute Workflow Trigger：输入模式、轮询与实时 |
| `references/SWITCH_FALLBACK.md` | 配置 Switch 节点：无名输出 / 缺失回退静默地丢弃未匹配的项目 |
| `references/MERGE_NODE.md` | 配置 Merge 节点，或你看到 `useDataOfInput`、`numberOfInputs` 或分支汇聚 |

## 反模式

| 反模式 | 问题所在 | 修复 |
|---|---|---|
| 从记忆中构建节点配置，记得去年节点的外观 | 参数结构已漂移，验证失败并出现难以理解的错误 | 每次会话每个节点始终 `get_node_types` |
| 在 `get_node_types` 中跳过区分器 | 得到通用结构，错过特定操作的必填字段 | 始终传递 `resource` + `operation`（如果存在，则 `mode`） |
| 将一个操作的节点配置复制到另一个操作并进行调整 | 过时参数触发验证，条件字段不适用 | 从新操作的形状中重新推导 |
| 在节点文本字段中硬编码令牌/凭证 | 导出时泄露。见 `n8n-credentials-and-security-official` | 始终使用凭证 |
| 配置节点后不使用 `test_workflow` 进行测试 | 运行时错误仅在真实数据上出现 | 始终在发布前使用固定数据进行测试 |
