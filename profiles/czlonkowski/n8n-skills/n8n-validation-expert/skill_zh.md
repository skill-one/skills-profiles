# n8n 验证专家

用于解释和修复 n8n 验证错误的专家指南。

---

## 验证理念

**尽早验证，频繁验证**

验证通常是迭代的：
- 预期验证反馈循环
- 通常 2-3 次验证→修复循环
- 平均：23 秒思考错误，58 秒修复它们

**关键洞察**：验证是一个迭代过程，而不是一次性操作！

---

## 错误严重程度级别

### 1. 错误（必须修复）
**阻止工作流执行** - 必须在激活前解决

**类型**：
- `missing_required` - 未提供必需字段
- `invalid_value` - 值不匹配允许的选项
- `type_mismatch` - 数据类型错误（字符串而不是数字）
- `invalid_reference` - 引用的节点不存在
- `invalid_expression` - 表达式语法错误

**示例**：
```json
{
  "type": "missing_required",
  "property": "channel",
  "message": "Channel name is required",
  "fix": "Provide a channel name (lowercase, no spaces, 1-80 characters)"
}
```

### 2. 警告（应该修复）
**不会阻止执行** - 工作流可以激活，但可能有问题

**类型**：
- `best_practice` - 推荐但不必须 — 仅在 `ai-friendly` / `strict` 下显示
- `deprecated` - 使用旧的 API/功能 — 在每个配置文件下显示
- `security` - 硬编码的密钥、未经身份验证的 webhook — 在每个配置文件下显示
- `performance` - 潜在的性能问题 — 建议，`ai-friendly` / `strict`

**示例**（最佳实践 — 仅在 `ai-friendly` / `strict` 下显示）：
```json
{
  "type": "warning",
  "nodeName": "Slack",
  "message": "Slack API can have rate limits and transient failures"
}
```

### 3. 建议（可选）
**很好** - 可以增强工作流的改进

**类型**：
- `optimization` - 可以更高效
- `alternative` - 更好的方式来实现相同结果

---

## 验证循环

### 来自遥测的模式
**7,841 次出现**这种模式：

```
1. 配置节点
   ↓
2. validate_node (23 秒思考错误)
   ↓
3. 仔细阅读错误消息
   ↓
4. 修复错误
   ↓
5. 再次 validate_node (58 秒修复)
   ↓
6. 重复直到有效（通常 2-3 次迭代）
```

### 示例
```javascript
// 迭代 1
let config = {
  resource: "channel",
  operation: "create"
};

const result1 = validate_node({
  nodeType: "nodes-base.slack",
  config,
  profile: "runtime"
});
// → 错误：缺少 "name"

// ⏱️  23 秒思考...

// 迭代 2
config.name = "general";

const result2 = validate_node({
  nodeType: "nodes-base.slack",
  config,
  profile: "runtime"
});
// → 错误：缺少 "text"

// ⏱️  58 秒修复...

// 迭代 3
config.text = "Hello!";

const result3 = validate_node({
  nodeType: "nodes-base.slack",
  config,
  profile: "runtime"
});
// → 有效！✅
```

**这是正常的！** 不要因为多次迭代而气馁。

---

## 验证配置文件

四个配置文件是**累积**的（n8n-mcp ≥ 2.63.0）：每个配置文件都会显示较低配置文件的所有内容，以及更多内容。分界线是最佳实践*建议* — `minimal` 和 `runtime` 会隐藏它们；`ai-friendly` 和 `strict` 会添加它们。错误在所有配置文件中都是相同的，除了 `minimal` 会跳过一些配置级别的检查（例如显式 `operation` 的枚举验证）。安全和弃用警告在所有配置文件中都会显示。

### minimal
**使用场景**：快速结构检查，同时连接工作流

**显示**：会导致执行停止的硬错误（缺少必需字段、空代码、断开连接）。跳过枚举检查和所有建议。

**最快且最宽松。**

### runtime (推荐默认)
**使用场景**：构建过程中的持续验证；日常配置文件

**显示**：错误（必需字段、值类型、允许的值、依赖关系、断开的引用）加上安全和弃用警告。**没有**最佳实践建议。

**平衡 — 捕获所有会导致中断的问题，对风格保持沉默。**

### ai-friendly
**使用场景**：在部署之前想要最佳实践建议

**显示**：`runtime` 做的所有事情，**加上**最佳实践建议 — 每个节点的“没有错误处理”建议、`webhook` 应始终发送响应、速率限制说明、过时的 `typeVersion` 建议、`cachedResultName` 和长链提示。

**注意**：`ai-friendly` 比 `runtime` 更严格，而不是更宽松。（旧文档描述它减少了误报 — 那只在配置文件门禁损坏时才成立；现在已修复。）

### strict
**使用场景**：硬化关键生产工作流

**显示**：`ai-friendly` 做的所有事情，**加上**剩余属性检查（“属性 'X' 将不会被使用 — 使用当前设置无法显示”）。

**最大程度的代码检查。** 由于在源头上修复了误报，它的警告是值得权衡的建议，而不是噪音。

---

## 常见错误类型

五种核心错误类型，按频率大致排序：

- **`missing_required`** — 未提供必需字段。使用 `get_node` 查看必需字段，然后添加它。
- **`invalid_value`** — 值不匹配允许的选项（枚举区分大小写）。检查错误的允许列表或 `get_node`。
- **`type_mismatch`** — 数据类型错误（字符串 `"100"` 而不是数字 `100`）。转换为期望的类型。
- **`invalid_expression`** — 表达式语法错误（缺少 `{{}}`，拼写错误）。查看 n8n 表达式语法技能。
- **`invalid_reference`** — 引用的节点不存在（重命名、删除或拼写错误）。修复名称或 `cleanStaleConnections`。

第六类，**`patchNodeField` 错误**（查找未找到、模糊匹配、无效/不安全的正则表达式），在 `n8n_update_partial_workflow` 期间 `patchNodeField` 操作失败时显示 — 它是设计上严格的，并且会报错而不是静默继续。

以上每种类型都有工作示例（损坏的配置→修复），以及 `patchNodeField` 错误案例及其修复在 **[ERROR_CATALOG.md](ERROR_CATALOG.md)** 中。

---

## 自动清理系统

**自动规范化任何工作流更新时的常见操作结构** — `n8n_create_workflow`、`n8n_update_partial_workflow` 或任何保存。信任它；不要手动修复这些。

**保存时它会规范化**：
- **二元操作符**（等于、不等于、包含、不包含、大于、小于、以...开头、以...结尾）— 移除一个 `singleValue` 属性。
- **一元操作符**（isEmpty、isNotEmpty、true、false）— 添加 `singleValue: true`。
- **IF/Switch 元数据** — 填充 `conditions.options` 用于 IF v2.2+ 和 Switch v3.2+。

**验证不再对这些形状报错**（n8n-mcp ≥ 2.63.0）。n8n 从操作符名称派生一元性，并默认 `conditions.options` 子字段，所以 `validate_node` / `validate_workflow` 接受条件，无论是否存在 `singleValue` 和选项元数据 — 清理器只是在保存时整理规范形式。（旧服务器错误地报错未规范化的形状；如果你看到这种情况，请升级。）仍然是一个真实错误：v1 形状的 `conditions` 对象在 v2 节点上，空过滤器没有任何条件，以及 v1 操作符名称（例如 `smaller`）在 v2 结构内。

**清理器无法修复**（手动处理）：连接到不存在节点的断开连接（使用 `cleanStaleConnections`），分支计数不匹配（添加/删除连接或规则），以及矛盾损坏的状态（可能需要手动数据库干预）。

示例和无法修复的详细信息在 **[ERROR_CATALOG.md](ERROR_CATALOG.md)**（自动清理部分）中。

---

## 误报

验证重置（n8n-mcp ≥ 2.63.0）消除了经典的误报 — 表达式内的模板文字、可选链、省略操作默认值、Webhook→响应 Webhook 模式、IF/Filter 旧形状，以及更多不再报错。

**已知例外**（n8n-mcp 2.85.0，已上报上游；升级后重新检查）：

- **ERROR "Incorrect error output configuration… appear to be error handlers but are in main[0]"** 在一个分支出去，其中一个目标是 Respond to Webhook 或 Send Email 节点，或者其名称中包含 *error / fail / catch / exception*。如建议的那样将 Respond to Webhook 移动到 `main[1]`，这意味着 webhook 仅在上游节点失败时才响应。将其视为误报**仅当**消息与此文本完全匹配**并且**你已经检查了 `connections` 并确认命名的节点按设计位于成功路径上。在这种情况下保留接线，在回复中说明你忽略了 n8n-mcp#1111 以及原因，并且**不要运行 `n8n_autofix_workflow` 使用默认的修复类型**（排除 `error-output-config`，否则可能会重置成功路径）。其他 `valid: false` 错误仍然会被修复。([n8n-mcp#1111](https://github.com/czlonkowski/n8n-mcp/issues/1111))
- **警告 "Possible missing $ prefix"** 在 `json`/`items` *内部字符串* 中，例如 `$jmespath$('X').all(), "[?json.country=='PL'].json.name"`。`json.` 前缀是必需的，所以忽略警告。([#1115](https://github.com/czlonkowski/n8n-mcp/issues/1115))
- **`validate_node` 在 `language: "pythonNative"` 代码节点上 → "Code cannot be empty" (`jsCode`)**。错误是假的；验证工作流而不是代码。([#1112](https://github.com/czlonkowski/n8n-mcp/issues/1112))
- **Python "Return value must be a list of dicts"** 对于在所有项目模式下返回单个字典。n8n 接受它并发出一个项目。([#1113](https://github.com/czlonkowski/n8n-mcp/issues/1113))

**盲点**（有效工作流，运行时结果错误）：`$jmespath` 语法/引号错误在表达式内 ([#1114](https://github.com/czlonkowski/n8n-mcp/issues/1114))；*任何* `{{ }}` 内的 JS 错误，它解析为 `null` 而执行保持为绿色（见 **n8n-expression-syntax**）；原生 Python 错误，例如旧的 `_input`/`_json`、点访问、阻塞的导入和类 ([#1113](https://github.com/czlonkowski/n8n-mcp/issues/1113)，见 **n8n-code-python**)。验证加上成功的运行仍然不是证明：检查输出值。

剩下的是**最佳实践建议**（仅在 `ai-friendly` / `strict` 下显示），它们标记了真实的权衡，但可能对你的情况可以接受。并非每个建议都需要修复 — 很多是上下文相关的。常见的一个以及何时可以接受与值得修复：

- **"...without error handling"** — 可用于开发/测试和非关键通知；修复用于处理重要数据的生产处理。 （永远不会是硬错误 — 风格不会阻止执行。）
- **"No retry logic"** — 可用于幂等操作、具有自身重试的 API、手动触发；修复用于不可靠的外部服务和生产自动化。
- **"...rate limits and transient failures"** — 可用于内部/低流量/服务器端限制的 API；修复用于公共、高流量 API。
- **"Unbounded query"** — 可用于小已知数据集、聚合、开发/测试；修复用于大型表的生产查询。

相比之下，安全和弃用警告在*每个*配置文件下显示，应被视为真实。

每个案例的详细指导、验证不再标记的内容、配置文件策略、“我应该修复这个吗？”决策框架以及如何记录接受的建议在 **[FALSE_POSITIVES.md](FALSE_POSITIVES.md)** 中。

---

## 验证结果结构

### 完整响应
```javascript
{
  "valid": false,
  "errors": [
    {
      "type": "missing_required",
      "property": "channel",
      "message": "Channel name is required",
      "fix": "Provide a channel name (lowercase, no spaces)"
    }
  ],
  "warnings": [
    {
      "type": "best_practice",
      "property": "errorHandling",
      "message": "Slack API can have rate limits",
      "suggestion": "Add onError: 'continueRegularOutput'"
    }
  ],
  "suggestions": [
    {
      "type": "optimization",
      "message": "Consider using batch operations for multiple messages"
    }
  ],
  "summary": {
    "hasErrors": true,
    "errorCount": 1,
    "warningCount": 1,
    "suggestionCount": 1
  }
}
```

### 如何阅读它

1. **首先检查 `valid`** — `true` 表示配置有效；`false` 表示在部署前需要修复错误。
2. **首先修复 `errors`** — 每个 `errors` 都带有 `property`、`message` 和 `fix`。必须解决这些问题。
3. **审查 `warnings`** — 每个 `warnings` 都有 `message` 和 `suggestion`；根据案例决定是否处理（见上述误报）。
4. **考虑 `suggestions`** — 可选的改进，不是必须的。

---

## 工作流验证

### validate_workflow (结构)
**验证整个工作流**，而不仅仅是单个节点

**检查**：
1. **节点配置** - 每个节点有效
2. **连接** - 没有断开的引用
3. **表达式** - 语法和引用有效
4. **流程** - 逻辑工作流结构

**示例**：
```javascript
validate_workflow({
  workflow: {
    nodes: [...],
    connections: {...}
  },
  options: {
    validateNodes: true,
    validateConnections: true,
    validateExpressions: true,
    profile: "runtime"
  }
})
```

### 常见工作流错误

#### 1. 断开连接
```json
{
  "error": "Connection from 'Transform' to 'NonExistent' - target node not found"
}
```

**修复**：删除过时的连接或创建缺失的节点

#### 2. 循环（警告，不是错误）
```json
{
  "warning": "Workflow contains a cycle: Node A → Node B → Node A"
}
```

循环是一个**警告**，而不是硬错误（n8n-mcp ≥ 2.63.0）— 受运行时控制的循环（错误重试、数据驱动分页、路由器反馈）执行完成并且是合法的。**修复**仅当循环是无意中的：确保循环有一个真实的退出（一个条件节点、一个错误输出或一个有界的计数器），这样它就不会无限循环。

#### 3. 多个启动节点
```json
{
  "warning": "Multiple trigger nodes found - only one will execute"
}
```

**修复**：删除额外的触发器或拆分为单独的工作流

#### 4. 断开连接的节点
```json
{
  "warning": "Node 'Transform' is not connected to workflow flow"
}
```

**修复**：连接节点或如果未使用则删除

---

## 恢复策略

### 策略 1：重新开始
**当**：配置严重损坏

**步骤**：
1. 从 `get_node` 记录必需字段
2. 创建最小的有效配置
3. 逐步添加功能
4. 每次添加后验证

### 策略 2：二分搜索
**当**：工作流验证但执行不正确

**步骤**：
1. 移除一半的节点
2. 验证并测试
3. 如果工作：问题在已移除的节点
4. 如果失败：问题在剩余的节点
5. 重复直到问题隔离

### 策略 3：清理过时的连接
**当**：出现“节点未找到”错误

**步骤**：
```javascript
n8n_update_partial_workflow({
  id: "workflow-id",
  operations: [{
    type: "cleanStaleConnections"
  }]
})
```

### 策略 4：使用自动修复
**当**：可以自动解决的验证错误

**步骤**：
```javascript
// 预览修复（默认 - 不应用）
n8n_autofix_workflow({
  id: "workflow-id",
  applyFixes: false,
  confidenceThreshold: "medium"  // high, medium, low
})

// 审查修复，然后应用
n8n_autofix_workflow({
  id: "workflow-id",
  applyFixes: true
})
```

---

## 自动修复功能

`n8n_autofix_workflow` 工具可以修复以下问题类型：

1. **expression-format** - 表达式缺少 `=` 前缀（例如，`{{ $json.field }}` → `={{ $json.field }}`)
2. **typeversion-correction** - 降级具有不受支持的 typeVersions 的节点
3. **error-output-config** - 移除冲突的 onError 设置
4. **node-type-correction** - 使用相似性匹配修复未知节点类型（90%+ 置信度）
5. **webhook-missing-path** - 为缺少路径配置的 webhook 节点生成 UUIDs
6. **typeversion-upgrade** - 智能升级到最新节点版本并自动迁移
7. **version-migration** - 需要手动步骤的复杂破坏性更改的指导

**置信度级别**：`high` (90%+, 可以安全自动应用), `medium` (70-89%, 建议审查), `low` (<70%, 需要手动审查)

```javascript
// 预览所有修复
n8n_autofix_workflow({id: "workflow-id"})

// 仅应用高置信度修复
n8n_autofix_workflow({
  id: "workflow-id",
  applyFixes: true,
  confidenceThreshold: "high"
})

// 针对特定修复类型
n8n_autofix_workflow({
  id: "workflow-id",
  fixTypes: ["expression-format", "typeversion-upgrade"],
  applyFixes: true
})
```

**更新后指导**：对于版本升级，检查响应中的 `postUpdateGuidance` 字段以获取逐步迁移说明。

---

## 最佳实践

### ✅ 做
- 每次重大更改后验证
- 完全阅读错误消息
- 逐步迭代修复错误（一次一个）
- 使用 `runtime` 配置文件进行预部署
- 在假设成功之前检查 `valid` 字段
- 信任自动清理器处理操作符问题
- 不清楚要求时使用 `get_node`
- 记录你接受的误报

### ❌ 不要
- 激活前跳过验证
- 尝试一次性修复所有错误
- 忽略错误消息
- 开发期间使用 `strict` 配置文件（太嘈杂）
- 假设验证通过（始终检查结果）
- 手动修复自动清理问题
- 带有未解决错误的部署
- 忽略所有警告（有些很重要！）

---

## 验证后运行工作流

`validate_workflow` 检查结构、参数和表达式 — 它从不运行任何内容。一个验证干净的工作流仍然可能在真实数据上失败，所以在调用完成之前运行它一次。

**使用 webhook、表单或聊天触发器**：`n8n_test_workflow({workflowId})` — 默认 `method: "auto"` 检测触发器并通过 HTTP 发送它（工作流必须处于活动状态）。

**没有这种触发器**（手动触发、计划、子工作流）没有 HTTP 入口。使用 pin-data 路径，它通过 n8n 自己的 MCP 服务器运行 (`N8N_MCP_ACCESS_TOKEN`, n8n 2.34+)：

1. `n8n_test_workflow({workflowId, method: "prepare"})` — 列出需要 pin 数据的节点。
2. 构建每个列出节点的一个样本项目，按节点 **名称** 键，每个项目用 `{json: {...}}` 包装：
   ```json
   {"When clicking 'Test workflow'": [{"json": {"orderId": "1234", "email": "a@b.com"}}]}
   ```
   通常是使用 `{json}` 项目的扁平对象而不是数组。
3. `n8n_test_workflow({workflowId, method: "pinned", pinData})` — 使用该数据运行它并等待结果。

**对于没有 pin 数据的快速手动运行**，`method: "direct"` 启动手动执行并立即返回；轮询 `n8n_executions({action: "get", id: executionId, mode: "error"})` 获取结果。在 `direct` 运行中不会 pin 任何内容，所以每个节点都会执行，它所做的任何外部调用都是真实的 — 并且 `pinned` 仅 pin 触发器、凭据和 HTTP 请求节点。`executionMode: "production"` 改变执行上下文，而不是是否有副作用；保持默认，除非用户要求生产运行。

**首次路由运行前的同意。** n8n 拒绝对“MCP 中可用”设置关闭的工作流的这些调用，这会返回 `WORKFLOW_NOT_EXPOSED`。重新运行 `exposeToMcp: true` 打开该设置并重试一次。它是在工作流上的一个可见的、持久的设置（关闭它是一个故意的行为：`n8n_update_partial_workflow({id: workflowId, operations: [{type: "updateSettings", settings: {availableInMCP: false}}]})`，或者 n8n UI 中的切换。**在传递它之前询问用户**。同意流程只允许启用该设置；没有任何东西会隐式禁用它。再次关闭它是一个故意的行为。

**阅读结果**：一个启动后失败的运行会返回 `EXECUTION_FAILED` 并带有 `executionId` — 使用 `n8n_executions({action: "get", id, mode: "error"})` 检查它，并从抛出错误的节点修复，然后再次验证和运行。

---

## 审查现有工作流

在构建时验证（上述循环）是为了捕获你正在进行的进行中的工作的模式和形状错误。**审查现有工作流**（你的或你接手的）是一项不同的工作：工作流已经通过 `validate_workflow` 清洁，你正在寻找验证看不到的问题（静默连接错误、易注入的查询、丢失项目的 Switch、Set/Code 反模式、缺少错误路径）。为此，使用 `n8n_get_workflow` 拉取工作流并走 **[REVIEW_CHECKLIST.md](REVIEW_CHECKLIST.md)** — 一个按严重程度分级的审计（必须修复 / 应该修复 / 很好），其中每个项目都指向修复的规范技能。

与它一起运行 `n8n_audit_instance` 来暴露整个实例的硬编码密钥和未经身份验证的 webhook，以及缺少错误处理和数据保留。

---

## 详细指南

对于完整的错误目录、误报和工作流审查：

- **[ERROR_CATALOG.md](ERROR_CATALOG.md)** - 完整的错误类型列表和示例
- **[FALSE_POSITIVES.md](FALSE_POSITIVES.md)** - 当警告可以接受时
- **[REVIEW_CHECKLIST.md](REVIEW_CHECKLIST.md)** - 用于审查现有工作流的严重程度分级的审计

---

## 总结

**要点**：
1. **验证是迭代的**（平均 2-3 个周期，23 秒 + 58 秒）
2. **错误必须修复**，警告是可选的
3. **自动清理**在保存时规范化操作结构；验证不再对原始形状报错
4. **默认使用 runtime 配置文件**；升级到 `ai-friendly`/`strict` 获取最佳实践建议
5. **经典误报已修复**（≥ 2.63.0）— 剩余警告是建议或安全和弃用通知，而不是验证错误
6. **阅读错误消息** - 它们包含修复指导

**验证过程**：
1. 验证 → 阅读错误 → 修复 → 验证再次
2. 重复直到有效（通常 2-3 次迭代）
3. 审查警告并决定是否可以接受
4. 有信心地部署

**相关技能和工具**：
- n8n MCP 工具专家 - 正确使用验证工具
- n8n 表达式语法 - 修复表达式错误
- n8n 节点配置 - 了解必需字段
- `n8n_audit_instance` - 主动安全验证（硬编码密钥、未经身份验证的 webhook、缺少错误处理、数据保留）
