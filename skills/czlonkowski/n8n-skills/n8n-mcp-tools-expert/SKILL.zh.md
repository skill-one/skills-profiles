---
name: n8n-mcp-tools-expert
description: 使用n8n-mcp MCP工具的专家指南。在搜索节点、验证配置、访问模板、管理工作流、将工作流组织到文件夹中、管理凭证、审计实例安全或使用任何n8n-mcp工具时使用。提供工具选择指南、参数格式和常见模式。重要提示——在使用任何n8n-mcp工具之前，请务必先咨询此技能——它可以防止常见的错误，如错误的nodeType格式、不正确的参数结构和不高效的工具使用。如果用户提到n8n、工作流、节点或自动化，并且您有n8n MCP工具可用，请首先使用此技能。
---

# n8n MCP Tools 专家

使用 n8n-mcp MCP 服务器工具构建工作流的终极指南。

---

## 工具类别

n8n-mcp 提供按类别组织的工具：

1. **节点发现** → [SEARCH_GUIDE.md](SEARCH_GUIDE.md)
2. **配置验证** → [VALIDATION_GUIDE.md](VALIDATION_GUIDE.md)
3. **工作流管理** → [WORKFLOW_GUIDE.md](WORKFLOW_GUIDE.md)
4. **模板库** - 搜索和部署 2,700 多个真实工作流
5. **数据表** - 管理 n8n 数据表、行和列 (`n8n_manage_datatable`)
6. **工作流文件夹** - 文件夹 CRUD + 工作流放置 (`n8n_manage_folders`)
7. **凭证管理** - 完整凭证 CRUD + 模式发现 (`n8n_manage_credentials`)
8. **安全与审计** - 使用自定义深度扫描进行实例安全审计 (`n8n_audit_instance`)
9. **文档与指南** - 工具文档、AI 代理指南、Code 节点指南
10. **代理** - 创建、配置、验证、运行和发布持久化的 n8n 代理 (`n8n_manage_agents`, 需要 `N8N_MCP_ACCESS_TOKEN`)
11. **节点资源解析** - 使用真实凭证解析实时下拉/资源定位器值 (`n8n_explore_node_resources`, 需要 `N8N_MCP_ACCESS_TOKEN`)
12. **实例目录** - 列出项目和标签 (`n8n_list_catalog`)

---

## 快速参考

### 最常用的工具（按成功率）

| 工具 | 使用场景 | 速度 |
|------|----------|-------|
| `search_nodes` | 通过关键字查找节点 | <20ms |
| `get_node` | 了解节点操作（detail="standard"） | <10ms |
| `validate_node` | 检查配置（mode="full"） | <100ms |
| `n8n_create_workflow` | 创建工作流 | 100-500ms |
| `n8n_update_partial_workflow` | 编辑工作流（MOST USED！） | 50-200ms |
| `validate_workflow` | 检查完整工作流 | 100-500ms |
| `n8n_deploy_template` | 将模板部署到 n8n 实例 | 200-500ms |
| `n8n_manage_datatable` | 管理数据表和行 | 50-500ms |
| `n8n_manage_folders` | 文件夹 CRUD + 组织工作流 | 100-500ms |
| `n8n_manage_credentials` | 凭证 CRUD + 模式发现 | 50-500ms |
| `n8n_audit_instance` | 安全审计（内置 + 自定义扫描） | 500-5000ms |
| `n8n_autofix_workflow` | 自动修复验证错误 | 200-1500ms |
| `n8n_manage_agents` | 持久化 n8n 代理 CRUD/验证/发布 | 150-400ms; `call` 操作: 5-60s |
| `n8n_explore_node_resources` | 解析实时 loadOptions/listSearch 值 | 200 ms - 5 s |
| `n8n_list_catalog` | 列出项目或标签 | 50-300ms |

---

## 工具选择指南

### 找到正确的节点

**工作流**:
```
1. search_nodes({query: "keyword"})
2. get_node({nodeType: "nodes-base.name"})
3. [可选] get_node({nodeType: "nodes-base.name", mode: "docs"})
```

**示例**:
```javascript
// 第一步：搜索
search_nodes({query: "slack"})
// 返回: nodes-base.slack

// 第二步：获取详情
get_node({nodeType: "nodes-base.slack"})
// 返回: 操作、属性、示例（标准 detail）

// 第三步：获取可读文档
get_node({nodeType: "nodes-base.slack", mode: "docs"})
// 返回: markdown 文档
```

**常见模式**: 搜索 → get_node (18s 平均)

### 验证配置

**工作流**:
```
1. validate_node({nodeType, config: {}, mode: "minimal"}) - 检查必填字段
2. validate_node({nodeType, config, profile: "runtime"}) - 完整验证
3. [重复] 修复错误，再次验证
```

**常见模式**: 验证 → 修复 → 验证 (每个循环 23s 思考，58s 修复)

### 管理工作流

**工作流**:
```
1. n8n_create_workflow({name, nodes, connections})
2. n8n_validate_workflow({id})
3. n8n_update_partial_workflow({id, operations: [...]})
4. 再次 n8n_validate_workflow({id})
5. n8n_update_partial_workflow({id, operations: [{type: "activateWorkflow"}]})
```

**常见模式**: 迭代更新 (56s 平均间隔)

### 关键：创建工作流时的节点 JSON 健康状况

在生成的节点 JSON 中，三个结构错误即使工作流验证通过也会破坏 n8n UI：

1. **永远不要发出带有占位符 ID 的 `credentials` 块。** 像 `"id": "REPLACE_ME"` 这样的假 ID 会永久禁用凭证选择器并使其不可点击，在 n8n UI 中显示为“尚未添加凭证” — 用户必须从头开始重新创建节点。如果您不知道真实的凭证 ID，**请完全省略 `credentials` 块**；缺失的块会显示一个用户可以点击的正常空下拉菜单。先使用 `n8n_manage_credentials({action: "list"})` 发现真实的凭证 ID。

```javascript
// ❌ 破坏凭证选择器
"credentials": {"httpHeaderAuth": {"id": "REPLACE_ME", "name": "My API Key"}}

// ✅ 未知 ID → 省略凭证块；用户在 UI 中选择
// ✅ 已知 ID（来自 n8n_manage_credentials 列表）→ 使用真实 ID
```

2. **为节点 `id` 生成 UUID v4 值** — 而不是像 `"http-list-node"` 这样的人类可读字符串。n8n 的前端使用节点 ID 进行表单绑定和凭证组件初始化；非 UUID ID 会导致细微的 UI 错误。

3. **为每个节点使用当前的 `typeVersion`** — 而不是硬编码记住的版本（例如 httpRequest 在 4.4+，不是 4.2）。

---

## 关键：nodeType 格式

**两种不同的格式** 用于不同的工具！

### 格式 1：搜索/验证工具
```javascript
// 使用短前缀
"nodes-base.slack"
"nodes-base.httpRequest"
"nodes-base.webhook"
"nodes-langchain.agent"
```

**使用此格式的工具**:
- search_nodes (返回此格式)
- get_node
- validate_node
- validate_workflow

### 格式 2：工作流工具
```javascript
// 使用完整前缀
"n8n-nodes-base.slack"
"n8n-nodes-base.httpRequest"
"n8n-nodes-base.webhook"
"@n8n/n8n-nodes-langchain.agent"
```

**使用此格式的工具**:
- n8n_create_workflow
- n8n_update_partial_workflow

### 转换

```javascript
// search_nodes 返回两种格式
{
  "nodeType": "nodes-base.slack",          // 用于搜索/验证工具
  "workflowNodeType": "n8n-nodes-base.slack"  // 用于工作流工具
}
```

---

## 常见错误

八个反复出现的错误。其中两个值得完整展示，因为它们会无声地破坏结构：

```javascript
// nodeType 前缀（搜索/验证工具需要短形式）
get_node({nodeType: "slack"})              // ❌ 缺少前缀 → "Node not found"
get_node({nodeType: "n8n-nodes-base.slack"}) // ❌ FULL 前缀用于工作流工具
get_node({nodeType: "nodes-base.slack"})     // ✅

// 凭证必须按类型嵌套，包含 {id, name} — 不是扁平字符串
updates: {credentials: "myApiKey"}                              // ❌
updates: {credentials: {httpHeaderAuth: {id: "abc123", name: "My API Key"}}}  // ✅
```

| # | 错误 | 修复 |
|---|---------|-----|
| 1 | 错误的 nodeType 格式 | 搜索/验证：短 `nodes-base.*`；工作流工具：完整 `n8n-nodes-base.*`（见上文） |
| 2 | `detail: "full"` 默认 | 默认 `standard` 覆盖 95%；使用 `docs`/`search_properties` 而不是 `full` |
| 3 | 无验证配置 | 明确传递 `profile: "runtime"` (`minimal`/`ai-friendly`/`strict` 用于其他阶段) |
| 4 | 忽略自动清理 | 所有节点在任意更新时都会被清理（操作结构、IF/Switch 元数据）；它无法修复断开的连接或分支计数不匹配 |
| 5 | 不使用智能参数 | 使用 `branch: "true"` / `case: 0` 而不是脆弱的 `sourceIndex` 计算 |
| 6 | 忽略 `intent` | 在 `n8n_update_partial_workflow` 上始终包含 `intent` 以获得更好的响应 |
| 7 | `parameters` 而不是 `updates` | `updateNode` 使用 `updates: {...}`，而不是 `parameters: {...}` |
| 8 | 错误的凭证格式 | 按类型嵌套，包含 `{id, name}`（见上文） |

每个的完整错误/正确示例：见 [VALIDATION_GUIDE.md → 常见错误](VALIDATION_GUIDE.md)。

---

## 工具使用模式

三种模式主导实际使用。每个模式的工作示例都存在于参考指南中。

- **模式 1 — 节点发现**（18s 平均间隔）：`search_nodes({query})` → `get_node({nodeType, includeExamples: true})`。见 [SEARCH_GUIDE.md](SEARCH_GUIDE.md)。
- **模式 2 — 验证循环**（23s 思考，58s 修复）：`validate_node({profile: "runtime"})` → 读取 `errors` → 修复配置 → 再次验证直到干净。见 [VALIDATION_GUIDE.md](VALIDATION_GUIDE.md)。
- **模式 3 — 工作流编辑**（99.0% 成功，56s 平均间隔）：迭代 `n8n_update_partial_workflow`（带 `intent`）→ `n8n_validate_workflow` → 最后 `activateWorkflow`。迭代构建，不是一次性。见 [WORKFLOW_GUIDE.md](WORKFLOW_GUIDE.md)。

---

## 详细指南

### 节点发现工具
见 [SEARCH_GUIDE.md](SEARCH_GUIDE.md) 了解：
- search_nodes
- 带有 detail 级别的 get_node（minimal, standard, full）
- get_node 模式（info, docs, search_properties, versions）

### 验证工具
见 [VALIDATION_GUIDE.md](VALIDATION_GUIDE.md) 了解：
- 验证配置解释
- validate_node 带有模式（minimal, full）
- validate_workflow 完整结构
- 自动清理系统
- 处理验证错误

### 工作流管理
见 [WORKFLOW_GUIDE.md](WORKFLOW_GUIDE.md) 了解：
- n8n_create_workflow
- n8n_update_partial_workflow（21 种操作类型，包括 patchNodeField, setNodeGroups，以及 moveToFolder！）
- 智能参数（branch, case）
- AI 连接类型（8 种类型）
- 工作流激活（activateWorkflow/deactivateWorkflow）
- n8n_deploy_template
- n8n_workflow_versions
- n8n_manage_folders（文件夹 CRUD + 工作流放置）
- n8n_manage_credentials（凭证 CRUD + 模式发现）
- n8n_audit_instance（安全审计）

### 模板、数据表与自助帮助
见 [OPERATIONS_GUIDE.md](OPERATIONS_GUIDE.md) 了解：
- search_templates / get_template / n8n_deploy_template 示例
- n8n_manage_datatable（完整操作、过滤条件、示例）
- tools_documentation, ai_agents_guide, n8n_health_check

---

## 模板使用

2,700 多个模板库有三个工具：`search_templates`（模式 `query`/`by_nodes`/`by_task`/`by_metadata`）、`get_template`（模式 `structure`/`full`）、`n8n_deploy_template`（部署到您的实例，带 `autoFix`/`autoUpgradeVersions`，返回工作流 ID + 所需凭证 + 应用修复）。

见 [OPERATIONS_GUIDE.md](OPERATIONS_GUIDE.md) 了解完整搜索/获取/部署示例。

---

## 运行工作流

`n8n_test_workflow` 有一个必需参数（`workflowId`）和一个选择路径的 `method`：

| `method` | 后端 | 它做什么 |
|---|---|---|
| `auto` (默认) | Public API | 检测 webhook/form/chat 触发器并通过 HTTP 触发它 — 工作流必须 **激活**。没有触发器 → 它报告工作流无法触发并命名下面的方法。**`auto` 从不通过 n8n 的 MCP 服务器运行任何内容。** |
| `trigger` | Public API | 相同 HTTP 路径，显式请求。 |
| `prepare` | n8n 的 MCP 服务器 | 只读：列出需要固定数据的节点。 |
| `pinned` | n8n 的 MCP 服务器 | 运行工作流，用 `pinData` 代替触发器、凭证和 HTTP 请求节点，并等待。其他节点仍然运行。一个以 `error`/`crashed`/`canceled` 结束的运行返回为 `EXECUTION_FAILED` 并带有 `executionId`。 |
| `direct` | n8n 的 MCP 服务器 | 启动运行并返回，一旦开始；没有固定，所以每个节点都运行。`message` 或 `data`/`headers` 被转发到触发器作为输入。 |

- 最后三种需要 `N8N_MCP_ACCESS_TOKEN`（n8n 2.34+）和工作流的“MCP 中可用”设置。
- `pinData` 按节点 **名称** 键，每个值都是一个作为 `{"json": {...}}` 包装的项目数组 — `{"Webhook": [{"json": {"id": "123"}}]}`，永远不会是扁平对象。它必须非空。
- `triggerNodeName` 选择要从中启动的触发节点（默认为检测到的节点；n8n 在输入给出时需要它）。
- **两种运行方法都会真实执行工作流的节点。** `direct` 运行每个节点；`pinned` 仅固定触发节点、带有凭证和 HTTP 请求的节点，所以 Code、Set、If 和无凭证的 I/O（Execute Command、文件读写）仍然运行。在运行可能写入任何内容的工作流之前，请与用户确认。
- `executionMode` 适用于 `direct`：`manual`（默认）或 `production`。它改变执行上下文，而不是运行是否具有副作用 — 生产运行通过生产执行路径，并记录为一次。仅在用户要求时传递它。
- `timeoutMs` 是官方调用的客户端截止时间（5000-600000；默认 30000 用于 `prepare`，300000 用于 `pinned`/`direct`）。
- `direct` 一旦运行开始就返回，所以它无论运行如何结束都会报告成功并带有 `executionId` — 汇报 `n8n_executions({action: "get", id: executionId})` 以获取结果。n8n 拒绝的调度直接返回为 `OFFICIAL_MCP_ERROR`，而不是 `EXECUTION_FAILED`。
- 工作流的“MCP 中可用”设置关闭会回答 `WORKFLOW_NOT_EXPOSED`；`exposeToMcp: true` 打开该设置并重试一次。这是一个可见的、持久的更改 — 在传递之前询问用户，并注意启用它本身就是一个工作流更新，所以它可以覆盖并发 UI 编辑。

成功和路由的响应会声明 `method` 和 `backend` (`public-api` 或 `official-mcp`)；一个在参数验证上被拒绝的包可能既不携带 `method` 也不携带 `backend`。

见 [WORKFLOW_GUIDE.md](WORKFLOW_GUIDE.md#n8n_test_workflow-running-workflows) 了解每种方法的可运行示例。

---

## 版本历史

`n8n_workflow_versions` 读取两个独立的版本历史，通过 `source` 选择：

- `source: "local"`（默认）— n8n-mcp 在更改工作流之前拍摄的快照。任何 n8n 版本，无需令牌，ID 是数字。对 n8n UI 中进行的编辑无感知。唯一支持 `delete` 和 `prune` 的来源。
- `source: "native"` — n8n 自己的工作流历史，与 UI 显示的相同列表，包括人们进行的编辑。需要 `N8N_MCP_ACCESS_TOKEN`（n8n 2.34+；内置 `diff` 需要 2.36，其中 `get_workflow_versions_diff` 发货）和工作流的“MCP 中可用”设置；ID 是不透明的字符串；`list` 被 50 限制，带 `offset`；`delete` 和 `prune` 拒绝，带有 `MODE_NOT_SUPPORTED_FOR_SOURCE`（n8n 拥有该保留）。内置回滚不是预先验证的 — `validateBefore` 被接受并忽略。

`mode: "diff"` 比较两个版本（`versionId` + `toVersionId`，来自相同来源和相同工作流）。本地差异（`data.format: "n8n-mcp"）报告添加/删除/修改的节点作为节点 **ID**；内置差异（`data.format: "n8n"）是 n8n 自己的负载，带有字段级之前/之后值。在 `data.format` 上分支，而不是假设字段名。

内置模式与路由运行方法相同的同意门：工作流的“MCP 中可用”设置关闭会回答 `WORKFLOW_NOT_EXPOSED`，并重新运行 `exposeToMcp: true` 打开该设置并重试一次（响应然后携带 `exposedToMcp: true`）。这是对工作流的一个可见的、持久的更改 — 在传递之前询问用户。`timeoutMs`（5000-600000）是内置调用的客户端截止时间。

见 [WORKFLOW_GUIDE.md](WORKFLOW_GUIDE.md#n8n_workflow_versions-version-control) 了解每个模式，以及两种来源的运行示例。

---

## 数据表管理

`n8n_manage_datatable` 是 MCP 工具，用于从工作流外部管理数据表和行（表操作 `createTable`/`listTables`/`getTable`/`updateTable`/`deleteTable`；行操作 `getRows`/`insertRows`/`updateRows`/`upsertRows`/`deleteRows`，带过滤、分页和 `dryRun`）。不要将其与工作流中的 `nodes-base.dataTable` 节点混淆，该节点在执行期间读取/写入行（见 [n8n-node-configuration → OPERATION_PATTERNS.md](../n8n-node-configuration/OPERATION_PATTERNS.md#data-table-nodes-basedatatable)）。经验法则：MCP 工具一次性设置表，工作流节点在每次执行时读取/写入。`deleteRows` 需要过滤器；在批量更改之前使用 `dryRun: true`。

**列操作** — `addColumn`、`deleteColumn`、`renameColumn` — 修改现有表的列，Public API 无法执行；它们通过 n8n 的 MCP 服务器运行，并需要 `N8N_MCP_ACCESS_TOKEN`（n8n 2.34+）。`addColumn` 接收 `column: {name, type}`（名称以字母开头，仅限字母/数字/下划线，最多 63 个字符；类型是 `string`、`number`、`boolean` 或 `date`）；`deleteColumn`/`renameColumn` 接收 `getTable` 的 `columnId`，`renameColumn` 将新列名称放入 `name`。它们通过项目地址表：当且仅当有一个可访问的项目时，`projectId` 会自动解析，否则调用会返回 `PROJECT_REQUIRED` 并列出候选者 — 传递 `projectId`（来自 `n8n_list_catalog({kind: "projects"})`）以跳过解析。重命名*表*不是列操作：在 Public API 上使用 `updateTable`。

**`deleteColumn` 会删除列的值以及列本身，且无法撤销。** 这在您最意想不到的地方影响最大：列的类型创建后无法更改，因此“将此列设为数字”实际上意味着删除并重新添加，这会丢弃其中的所有内容。如果它们很重要，请先用 `getRows` 读取值，并在删除填充列之前确认用户。

有关所有操作、过滤条件和示例，请参阅 [OPERATIONS_GUIDE.md](OPERATIONS_GUIDE.md)。

---

## 工作流文件夹

`n8n_manage_folders` 将工作流组织到文件夹中（操作 `create`/`list`/`get`/`rename`/`move`/`delete`；n8n 2.19+，注册免费社区版及以上）。`projectId` 默认为 `'personal'`。放置工作流发生在*工作流*工具中：`n8n_create_workflow` 上的 `parentFolderId`，或 `n8n_update_partial_workflow` 的 `moveToFolder` 操作（两者均为 n8n 2.32+；`null` = 项目根）。需要记住两件事：工作流的文件夹在 n8n API 中是**只写**的（通过文件夹的 `get` 计数验证放置，而不是读取工作流），并且没有 `transferToFolderId` 的 `delete` 会**归档**文件夹的工作流（`transferToFolderId: "0"` 将它们移动到项目根，而不是保持它们活跃）。

有关所有操作、列表过滤器/计数和删除语义，请参阅 [WORKFLOW_GUIDE.md](WORKFLOW_GUIDE.md)。

---

## 凭据管理

`n8n_manage_credentials` 是统一的凭据工具：操作 `list`、`get`、`create`、`update`、`delete`、`getSchema`。它从不返回秘密 — `get`/`create`/`update` 会剥离 `data` 字段。在 `create` 之前使用 `getSchema` 以发现必需的字段。可选的 `includeUsage: true` 标志（在 `list`/`get` 上）反向扫描工作流并附加 `usedIn: [{id, name, active}]` + `usageCount` — 在删除或轮换凭据之前使用它以查看会中断什么（它触发完整的客户端扫描，限制为 5000 个工作流，排除归档，并在失败时降级为 `usageScanError` 字段）。

有关所有操作、`includeUsage` 结构、安全说明和安全的删除/轮换工作流，请参阅 [WORKFLOW_GUIDE.md](WORKFLOW_GUIDE.md)。

---

## 代理

本节中的三个工具仅适用于 n8n 的实例级 MCP 服务器（与 Public API 是不同的端点）。`n8n_manage_agents` 和 `n8n_explore_node_resources` 需要 `N8N_MCP_ACCESS_TOKEN`；`n8n_list_catalog` 无需它，并且仅在其团队-项目回退时使用令牌。其他工具通过同一服务器路由单个操作 — `n8n_test_workflow` 的 `prepare`/`pinned`/`direct`、`n8n_workflow_versions` 的 `source: "native"`、`n8n_manage_datatable` 列操作 — 如各自部分所述；见“工具可用性”下文。

- `n8n_manage_agents` — 创建、配置、验证、运行和发布持久化的 n8n 代理（一个独立的助手工件：模型、指令、工具、技能、任务、内存、通道 — 不是 AI 代理工作流节点）。操作：`reference`、`search`、`get`、`create`、`mutate`、`validate`、`call`、`publish`、`unpublish`、`revert`、`versions`、`delete`、`discover_assets`、`verify_mcp_server`、`update_integration`。从 `action: "reference"` 开始，然后 `discover_assets` → `create` → `mutate`（一次一个资源，始终是最新哈希 — n8n 将其作为 `configHash` 返回，并期望它作为 `args.baseConfigHash` 返回；陈旧的会返回 `STALE_CONFIG`）→ `validate`。`publish` 仅在明确请求时执行；`call` 使用真实凭据和工具运行代理，并可能返回 `approvals[]` 供人类决定。`timeoutMs` 是顶级参数（默认 30000，`call` 为 180000），不是 `args` 的一部分。需要 n8n **2.34+** 及代理模块；在 2.36.x 上，代理运行时拒绝 `azureOpenAiApi`/`aws` 凭据。信封错误代码：`NOT_CONFIGURED`、`INVALID_ARGS`、`STALE_CONFIG`、`AGENT_NOT_RUNNABLE`、`AGENT_TOOL_ERROR`（一个编译失败的定制工具，或未知 `agentId`），以及共享的 `OFFICIAL_MCP_*` 系列（`AUTH_FAILED`、`NOT_ENABLED`、`RATE_LIMITED`、`TOOL_UNAVAILABLE`、`URL_REJECTED`、`TIMEOUT`、`TRANSPORT_ERROR`、`ERROR`）。有关完整工作流，请参阅 **n8n-agents** 技能的“持久化 n8n 代理”部分。
- `n8n_explore_node_resources` — 使用实时凭据解析节点 `loadOptions` 下拉菜单或资源定位器 `listSearch`（Slack 频道、Google Sheets 标签、模型列表）背后的真实值，而不是猜测 ID。当 `get_node`（`standard` 详情）在属性上显示 `dynamicOptions: {methodName, methodType, dependsOn}` 时使用它。**六个参数是必需的，没有一个被推断：** `nodeType`（长格式）、`version`（方法所属的节点 `typeVersion`）、从 `dynamicOptions` 复制的 `methodName` 和 `methodType`，以及 `credentialType` 加上 `n8n_manage_credentials({action: "list"})` 中该类型的 `credentialId`。`method dependsOn` 的任何内容都放在 `currentNodeParameters` 中，资源定位器值保持其 `{__rl: true, mode: "id", value: "…"}` 形状。每个结果的 `value` 是工作流参数中应包含的内容；`name` 仅用于显示。
- `n8n_list_catalog` — 列出实例级 `projects`（个人项目标记，提供 `projectId` 用于 `n8n_manage_agents`/`n8n_manage_datatable）或 `tags`。通过 Public API 无需令牌即可工作；配置令牌后，当 Public API 的许可证门栏拒绝时，会回退到官方 MCP 服务器用于团队项目（`teamProjectsEnabled` 报告哪些项目）。

---

## 安全与审计

`n8n_audit_instance` 结合了 n8n 的内置审计（类别 `credentials`/`database`/`nodes`/`instance`/`filesystem`）和自定义深度扫描（`hardcoded_secrets`、`unauthenticated_webhooks`、`error_handling`、`data_retention`）。所有参数可选：`categories`、`includeCustomScan`（默认 `true`）、`customChecks`、`daysAbandonedWorkflow`。检测到的秘密会被掩码（前 6 个 + 最后 4 个字符）。输出是一个可操作的 markdown 报告 — 摘要表、按工作流划分的发现，以及分为自动修复/需要审核/需要用户操作的修复手册。

有关两种扫描方法、示例和修复类型的完整说明，请参阅 [WORKFLOW_GUIDE.md](WORKFLOW_GUIDE.md)。

---

## 自助工具

- `tools_documentation()` — 所有工具的概述；`tools_documentation({topic, depth: "full"})` 用于特定工具。代码节点指南通过主题 `javascript_code_node_guide` / `python_code_node_guide`。
- **AI 代理指南** — `tools_documentation({topic: "ai_agents_guide", depth: "full"})`（没有独立工具）；返回架构、连接、工具、验证、最佳实践。
- `n8n_health_check()` — 快速检查；`n8n_health_check({mode: "diagnostic"})` 返回状态、环境变量、工具状态、API 连接性。两种模式还会返回 **`officialMcp`** 块 — `{configured, endpoint, reachable, toolCount, agentTools}` — 所有受 `N8N_MCP_ACCESS_TOKEN` 门栏限制的内容的预检：代理工具、`n8n_test_workflow` 的路由方法、原生版本历史、数据表列操作。在尝试任何它们之前读取它一次，而不是在任务中途通过 `NOT_CONFIGURED` 信封发现差距。

有关示例，请参阅 [OPERATIONS_GUIDE.md](OPERATIONS_GUIDE.md)。

---

## 工具可用性

**始终可用**（无需 n8n API）：
- search_nodes, get_node
- validate_node, validate_workflow
- search_templates, get_template
- tools_documentation（包括 ai_agents_guide 主题）

**需要 n8n API**（N8N_API_URL + N8N_API_KEY）：
- n8n_create_workflow
- n8n_update_partial_workflow, n8n_update_full_workflow
- n8n_validate_workflow (by ID)
- n8n_list_workflows, n8n_get_workflow, n8n_delete_workflow
- n8n_test_workflow
- n8n_executions
- n8n_evaluations (读取：n8n 2.30+ 创建于 2.30+；运行/取消：n8n 2.32+ 创建于 2.32+ — 较旧的密钥缺少 testRun 范围)
- n8n_deploy_template
- n8n_workflow_versions
- n8n_autofix_workflow
- n8n_manage_datatable
- n8n_manage_folders (文件夹 CRUD：n8n 2.19+，注册社区版及以上；通过 parentFolderId/moveToFolder 放置工作流：n8n 2.32+)
- n8n_manage_credentials
- n8n_audit_instance
- n8n_list_catalog (无需令牌即可工作；仅用于团队项目回退需要它)

**需要 `N8N_MCP_ACCESS_TOKEN`**（一个不同于 n8n 设置 → 实例级 MCP 的独立令牌，除了上述 Public API 凭据）：
- n8n_manage_agents
- n8n_explore_node_resources
- n8n_test_workflow with `method: "prepare"`/`"pinned"`/`"direct"`（还需要工作流的“Available in MCP”设置）
- n8n_workflow_versions with `source: "native"`（还需要工作流的“Available in MCP”设置）
- n8n_manage_datatable with `addColumn`/`deleteColumn`/`renameColumn`

如果 API 工具不可用，请使用模板和仅验证的工作流。

---

## 统一工具参考

- **`get_node`** — 详情级别（`minimal` ~200 tok / `standard` ~1-2K，推荐 / `full` ~3-8K，谨慎使用）和模式（`info` 默认，`docs`，`search_properties` + `propertyQuery`，`versions`，`compare`，`breaking`，`migrations`）。深入探讨在 [SEARCH_GUIDE.md](SEARCH_GUIDE.md)。

- **`validate_node`** — 模式 `full`（默认，错误/警告/建议）和 `minimal`（必需字段检查）；配置文件 `minimal`/`runtime`（默认，推荐）/`ai-friendly`/`strict`。深入探讨在 [VALIDATION_GUIDE.md](VALIDATION_GUIDE.md)。

---

## 性能特征

| 工具 | 响应时间 | 有效载荷大小 |
|------|---------------|--------------|
| search_nodes | <20ms | 小 |
| get_node (standard) | <10ms | ~1-2KB |
| get_node (full) | <100ms | 3-8KB |
| validate_node (minimal) | <50ms | 小 |
| validate_node (full) | <100ms | 中等 |
| validate_workflow | 100-500ms | 中等 |
| n8n_manage_folders | 100-500ms | 小 |
| n8n_manage_credentials | 50-500ms | 小-中等 |
| n8n_audit_instance | 500-5000ms | 大 |
| n8n_create_workflow | 100-500ms | 中等 |
| n8n_update_partial_workflow | 50-200ms | 小 |
| n8n_deploy_template | 200-500ms | 中等 |

---

## 最佳实践

### 做
- 对于简单的工作流（<=5 个节点），直接使用 MCP 工具 — 不要过度设计调查
- 使用 `patchNodeField` 对 Code 节点内容进行外科手术编辑，而不是替换整个节点
- 使用 `get_node({detail: "standard"})` 对于大多数用例
- 明确指定验证配置文件（`profile: "runtime"`）
- 使用智能参数（`branch`，`case`）以提高清晰度
- 在工作流更新中包含 `intent` 参数
- 遵循搜索 → `get_node` → 验证工作流
- 迭代工作流（平均 56 秒编辑间隔）
- 每次重大更改后验证
- 使用 `includeExamples: true` 用于真实配置
- 使用 `n8n_deploy_template` 进行快速启动

### 不要
- 除非必要，否则使用 `detail: "full"`（浪费令牌）
- 忘记节点类型前缀（`nodes-base.*`）
- 跳过验证配置文件
- 尝试一次性构建工作流（迭代！）
- 忽略自动清理行为
- 使用完整前缀（`n8n-nodes-base.*`）与搜索/验证工具
- 构建后忘记激活工作流

---

## 总结

**最重要**：
1. 使用 **get_node** 并带 `detail: "standard"`（默认）- 覆盖 95% 的用例
2. 节点类型格式不同：`nodes-base.*`（搜索/验证）vs `n8n-nodes-base.*`（工作流）
3. 指定 **验证配置文件**（`runtime` 推荐）
4. 使用 **智能参数**（`branch="true"`，`case=0`）
5. 在工作流更新中包含 **intent 参数**
6. **自动清理** 在更新期间在所有节点上运行
7. 工作流可以通过 API **激活**（`activateWorkflow` 操作）
8. 工作流是**迭代**构建的（平均 56 秒编辑间隔）
9. **数据表** 通过 `n8n_manage_datatable` 管理（CRUD + 过滤）
10. **文件夹** 通过 `n8n_manage_folders` 管理；工作流放置是只写的（通过文件夹计数验证，而不是工作流）
11. **凭据** 通过 `n8n_manage_credentials` 管理（CRUD + 模式发现）
12. **安全审计** 通过 `n8n_audit_instance`（内置 + 自定义深度扫描）
13. **AI 代理指南** 可通过 `tools_documentation({topic: "ai_agents_guide", depth: "full"})` 获取

**常见工作流**：
1. search_nodes → 找到节点
2. get_node → 理解配置
3. validate_node → 检查配置
4. n8n_create_workflow → 构建
5. n8n_validate_workflow → 验证
6. n8n_update_partial_workflow → 迭代
7. activateWorkflow → 上线！

有关详细信息，请参阅：
- [SEARCH_GUIDE.md](SEARCH_GUIDE.md) - 节点发现
- [VALIDATION_GUIDE.md](VALIDATION_GUIDE.md) - 配置验证 + 常见错误
- [WORKFLOW_GUIDE.md](WORKFLOW_GUIDE.md) - 工作流管理
- [OPERATIONS_GUIDE.md](OPERATIONS_GUIDE.md) - 模板、数据表、自助工具

---

**相关技能**：
- n8n 表达式语法 - 在工作流字段中编写表达式
- n8n 工作流模式 - 从模板中获取架构模式
- n8n 验证专家 - 解释验证错误
- n8n 节点配置 - 操作特定要求
- n8n 代码 JavaScript - 在 Code 节点中编写 JavaScript
- n8n 代码 Python - 在 Code 节点中编写 Python
