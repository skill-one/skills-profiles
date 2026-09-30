---
name: n8n-validation-expert
description: 解释验证错误并指导如何修复它们。在遇到验证错误、验证警告、误报、操作结构问题或需要帮助理解验证结果时使用。也用于询问验证配置文件、错误类型、验证循环过程或自动修复功能。每当 validate_node 或 validate_workflow 调用返回错误或警告时，请咨询此技能——它知道哪些警告是误报，哪些错误需要真正修复。
---

# n8n 验证专家

解释和修复 n8n 验证错误的专家指南。

---

## 验证理念

**尽早验证，频繁验证**

验证通常是迭代的：
- 预期验证反馈循环
- 通常 2-3 轮验证→修复循环
- 平均：23 秒思考错误，58 秒修复它们

**关键洞察**：验证是一个迭代过程，不是一次性完成的！

---

## 错误严重级别

### 1. 错误（必须修复）
**阻止工作流执行** - 必须在激活前解决

**类型**：
- `missing_required` - 未提供必填字段
- `invalid_value` - 值不匹配允许的选项
- `type_mismatch` - 错误的数据类型（字符串而不是数字）
- `invalid_reference` - 引用的节点不存在
- `invalid_expression` - 表达式语法错误

**示例**：
```json
{
  "type": "missing_required",
  "property": "channel",
  "message": "Channel name is required",
  "fix": "提供一个 channel name（小写，无空格，1-80 个字符）"
}
```

### 2. 警告（建议修复）
**不阻止执行** - 工作流可以激活，但可能有问题

**类型**：
- `best_practice` - 推荐但不强制要求 — 仅在 `ai-friendly` / `strict` 下显示
- `deprecated` - 使用旧的 API/功能 — 在每个配置文件下显示
- `security` - 硬编码的密钥，未经身份验证的 webhook — 在每个配置文件下显示
- `performance` - 潜在的性能问题 — 建议，`ai-friendly` / `strict`

**示例**（最佳实践 — 在 `ai-friendly` / `strict` 下显示）：
```json
{
  "type": "warning",
  "nodeName": "Slack",
  "message": "Slack API 可能存在速率限制和瞬时故障"
}
```

### 3. 建议（可选）
**锦上添花** - 可以增强工作流的改进

**类型**：
- `optimization` - 可以更高效
- `alternative` - 更好地实现相同结果的方法

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

四个配置文件是**累积**的（n8n-mcp ≥ 2.63.0）：每个都会显示较低配置文件的所有内容，并附加更多内容。分界线是最佳实践*建议* — `minimal` 和 `runtime` 不显示它们；`ai-friendly` 和 `strict` 会添加它们。错误在所有配置文件中都是相同的，除了 `minimal` 会跳过一些配置级别的检查（例如显式 `operation` 的枚举验证）。安全和弃用警告在所有配置文件下都会显示。

### minimal
**使用场景**：快速检查工作流连接时的结构。

**显示**：会阻止执行的硬错误（缺少必填字段、空代码、断开连接）。跳过枚举检查和所有建议。

**最快且最宽松。**

### runtime (推荐默认)
**使用场景**：构建过程中持续验证；日常配置文件。

**显示**：错误（必填字段、值类型、允许的值、依赖关系、断开的引用）加上安全和弃用警告。**没有**最佳实践建议。

**平衡 — 捕获所有会中断执行的问题，对风格保持静默。**

### ai-friendly
**使用场景**：在部署前获取最佳实践建议。

**显示**：`runtime` 的所有内容，**加上**最佳实践建议 — 每个节点的“无错误处理”建议、`webhook` 应始终发送响应、速率限制说明、过时的 `typeVersion` 建议、`cachedResultName` 和长链提示。

**注意**：`ai-friendly` 比 `runtime` 更严格，而不是更宽松。（旧文档称它减少了误报 — 那只在配置文件门禁损坏时成立；现在已修复。）

### strict
**使用场景**：硬化关键的生产工作流。

**显示**：`ai-friendly` 的所有内容，**加上**剩余属性检查（“属性 'X' 将不会被使用 — 在当前设置下不可见”）。

**最大程度的代码检查。** 在源头上修复了误报后，其警告是值得权衡的建议，而不是需要对抗的噪音。

---

## 常见错误类型

五种核心错误类型，按频率大致排序：

- **`missing_required`** — 未提供必填字段。使用 `get_node` 查看必填字段，然后添加它。
- **`invalid_value`** — 值不匹配允许的选项（枚举区分大小写）。检查错误的允许列表或 `get_node`。
- **`type_mismatch`** — 错误的数据类型（字符串 `"100"` 而不是数字 `100`）。转换为期望的类型。
- **`invalid_expression`** — 表达式语法错误（缺少 `{{}}`，拼写错误）。查看 n8n 表达式语法技能。
- **`invalid_reference`** — 引用的节点不存在（重命名、删除或拼写错误）。修复名称或 `cleanStaleConnections`。

第六类，**`patchNodeField` 错误**（查找未找到、模糊匹配、无效/不安全的正则表达式），在 `n8n_update_partial_workflow` 期间 `patchNodeField` 操作失败时显示 — 它按设计是严格的，并报错而不是静默继续。

以上每种类型都有工作示例（损坏的配置→修复），以及 `patchNodeField` 错误案例及其修复在 **[ERROR_CATALOG.md](ERROR_CATALOG.md)** 中。

---

## 自动清理系统

**自动规范化任何工作流更新中的常见操作结构** — `n8n_create_workflow`、`n8n_update_partial_workflow` 或任何保存。信任它；不要手动修复这些。

**保存时它会规范化**：
- **二元操作符**（等于、不等于、包含、不包含、大于、小于、以...开头、以...结尾） — 移除一个 `singleValue` 属性。
- **一元操作符**（isEmpty、isNotEmpty、true、false） — 添加 `singleValue: true`。
- **IF/Switch 元数据** — 填充 `conditions.options`（IF v2.2+ 和 Switch v3.2+）。

**验证不再对这些形状报错**（n8n-mcp ≥ 2.63.0）。n8n 从操作名称派生一元性，并默认 `conditions.options` 子字段，因此 `validate_node` / `validate_workflow` 接受条件，无论 `singleValue` 和选项元数据是否存在 — 清理器只是在保存时整理规范形式。（旧服务器错误地报错未规范化形状；如果你看到这种情况，请升级。）仍然*是*真实错误的：v1 形状的 `conditions` 对象在 v2 节点上、空过滤器无条件、以及 v2 结构中的旧版 v1 操作名称（例如 `smaller`）。

**清理器无法修复**（手动处理）：到不存在节点的连接（使用 `cleanStaleConnections`）、分支计数不匹配（添加/删除连接或规则）、以及矛盾损坏状态（可能需要手动数据库干预）。

示例和完整无法修复的详细信息在 **[ERROR_CATALOG.md](ERROR_CATALOG.md)**（自动清理部分）中。

---

## 误报

验证重置（n8n-mcp ≥ 2.63.0）消除了经典的误报 — 表达式中的模板文字、可选链、省略操作默认值、Webhook → 响应 Webhook 模式、IF/Filter 旧形状，以及更多不再触发。

**已知例外**（n8n-mcp 2.85.0，已上报上游；升级后重新检查）：

- **ERROR "错误输出配置...似乎错误处理但位于 main[0]"** 在一个 fan-out 中，其中一个目标是 Respond to Webhook 或 Send Email 节点，或其名称中包含 *error / fail / catch / exception*。建议将 Respond to Webhook 移到 `main[1]`，这意味着 webhook 仅在上游节点失败时响应。将其视为误报**仅当**消息与此文本完全匹配**并且**你已经检查了 `connections` 并确认命名的节点按设计位于成功路径上。在这种情况下保留接线，在回复中说明你忽略 n8n-mcp#1111 及原因，并且**不要**使用默认修复类型运行 `n8n_autofix_workflow`（排除 `error-output-config`，否则可能会重新配置成功路径）。其他 `valid: false` 错误仍然会被修复。([n8n-mcp#1111](https://github.com/czlonkowski/n8n-mcp/issues/1111))
- **警告 "可能缺少 $ 前缀"** 在 `json`/`items` *内部字符串* 中，例如 `$jmespath$('X').all(), "[?json.country=='PL'].json.name"`。`json.` 前缀是必需的，所以忽略警告。([#1115](https://github.com/czlonkowski/n8n-mcp/issues/1115))
- **`validate_node` 在 `language: "pythonNative"` 代码节点上 → "代码不能为空" (`jsCode`)**。错误是假的；验证工作流而不是代码。([#1112](https://github.com/czlonkowski/n8n-mcp/issues/1112))
- **Python "返回值必须是字典列表"** 对于在所有项目模式下返回单个字典。n8n 接受它并发出一个项目。([#1113](https://github.com/czlonkowski/n8n-mcp/issues/1113))

**盲点**（有效工作流，运行时结果错误）：`$jmespath` 语法/引号错误在表达式中 ([#1114](https://github.com/czlonkowski/n8n-mcp/issues/1114))；*任何* `{{ }}` 内的 JS 错误，它解析为 `null` 而执行保持绿色（见 **n8n-expression-syntax**）；原生 Python 错误，如旧版 `_input`/`_json`、点访问、阻塞导入和类 ([#1113](https://github.com/czlonkowski/n8n-mcp/issues/1113)，见 **n8n-code-python**）。验证加上成功运行仍然不是证明：检查输出值。

剩下的是**最佳实践建议**（仅在 `ai-friendly` / `strict` 下显示），它们标记了真正的权衡，但在你的情况下可能是可以接受的。并非每个建议都需要修复 — 许多是上下文相关的。常见建议和何时每个建议可以接受或值得修复：

- **"...无错误处理"** — 可用于开发/测试和非关键通知；修复用于处理重要数据的生产行为。（永远不会是硬错误 — 风格不会阻止执行。）
- **"无重试逻辑"** — 可用于幂等操作、具有自身重试的 API、手动触发；修复用于不可靠的外部服务和生产自动化。
- **"...速率限制和瞬时故障"** — 可用于内部/低流量/服务器端限制的 API；修复用于公共、高流量 API。
- **"无界查询"** — 可用于小已知数据集、聚合、开发/测试；修复用于生产查询的大型表。

安全性和弃用警告与不同，它们在*每个*配置文件下显示，应被视为真实。

完整按案例指导、验证不再标记的列表、配置文件策略、“我是否应该修复这个？”决策框架以及如何记录接受的建议在 **[FALSE_POSITIVES.md](FALSE_POSITIVES.md)** 中。

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
      "fix": "提供一个 channel name（小写，无空格）"
    }
  ],
  "warnings": [
    {
      "type": "best_practice",
      "property": "errorHandling",
      "message": "Slack API 可能存在速率限制",
      "suggestion": "添加 onError: 'continueRegularOutput'"
    }
  ],
  "suggestions": [
    {
      "type": "optimization",
      "message": "考虑使用批量操作处理多个消息"
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
3. **查看 `warnings`** — 每个 `warnings` 都有 `message` 和 `suggestion`；按案例决定是否处理（见上述误报）。
4. **考虑 `suggestions`** — 可选改进，不是必须的。

---

## 工作流验证

### validate_workflow (结构)
**验证整个工作流**，而不仅仅是单个节点

**检查**：
1. **节点配置** - 每个节点有效
2. **连接** - 无断开引用
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
  "error": "从 'Transform' 到 'NonExistent' 的连接 - 目标节点未找到"
}
```

**修复**：删除陈旧连接或创建缺失节点

#### 2. 循环（警告，不是错误）
```json
{
  "warning": "工作流包含一个循环：节点 A → 节点 B → 节点 A"
}
```

循环是一个**警告**，而不是硬错误（n8n-mcp ≥ 2.63.0） — 由运行时控制的循环（错误重试、数据驱动分页、路由器反馈）执行完成并合法。**修复**仅当循环是无意中的：确保循环有真实的退出（条件节点、错误输出或有限计数器），以便它不会无限循环。

#### 3. 多个启动节点
```json
{
  "warning": "发现多个触发节点 - 仅有一个将执行"
}
```

**修复**：删除额外触发器或拆分为独立工作流

#### 4. 断开连接的节点
```json
{
  "warning": "节点 'Transform' 未连接到工作流流程"
}
```

**修复**：连接节点或如果未使用则删除

---

## 恢复策略

### 策略 1：重新开始
**使用场景**：配置严重损坏

**步骤**：
1. 从 `get_node` 记录必填字段
2. 创建最小有效配置
3. 逐步添加功能
4. 每次添加后验证

### 策略 2：二分搜索
**使用场景**：工作流验证通过但执行不正确

**步骤**：
1. 移除一半节点
2. 验证并测试
3. 如果工作：问题在已移除节点
4. 如果失败：问题在剩余节点
5. 重复直到问题隔离

### 策略 3：清理陈旧连接
**使用场景**：出现“节点未找到”错误

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
**使用场景**：可以自动解决的验证错误

**步骤**：
```javascript
// 预览修复（默认 - 不应用）
n8n_autofix_workflow({
  id: "workflow-id",
  applyFixes: false,
  confidenceThreshold: "medium"  // high, medium, low
})

// 查看修复，然后应用
n8n_autofix_workflow({
  id: "workflow-id",
  applyFixes: true
})
```

---

## 自动修复功能

`n8n_autofix_workflow` 工具可以修复以下问题类型：

1. **expression-format** - 表达式中缺少 `=` 前缀（例如，`{{ $json.field }}` → `={{ $json.field }}`）
2. **typeversion-correction** - 降级具有不支持的 typeVersions 的节点
3. **error-output-config** - 移除冲突的 onError 设置
4. **node-type-correction** - 使用相似性匹配修复未知节点类型（90%+ 置信度）
5. **webhook-missing-path** - 为缺少路径配置的 webhook 节点生成 UUID
6. **typeversion-upgrade** - 智能升级到最新节点版本并自动迁移
7. **version-migration** - 指导需要手动步骤的复杂破坏性更改

**置信度级别**：`high`（90%+，安全自动应用），`medium`（70-89%，建议审查），`low`（<70%，需要手动审查）

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

**更新后指导**：对于版本升级，请检查响应中的 `postUpdateGuidance` 字段以获取逐步迁移说明。

---

## 最佳实践

### ✅ 应该做

- 在每次重大更改后验证
- 完整阅读错误信息
- 迭代式修复错误（一次修一个）
- 部署前使用 `runtime` 配置
- 在假设成功前检查 `valid` 字段
- 信任自动清理功能处理操作符问题
- 在不确定需求时使用 `get_node`
- 记录您接受的误报

### ❌ 不应该做

- 激活前跳过验证
- 试图一次性修复所有错误
- 忽略错误信息
- 开发期间使用 `strict` 配置（噪音过多）
- 假设验证已通过（始终检查结果）
- 手动修复自动清理问题
- 在存在未解决错误的情况下部署
- 忽略所有警告（有些很重要！）

---

## 验证通过后的工作流运行

`validate_workflow` 检查结构、参数和表达式 —— 它从不运行任何内容。即使验证通过的工作流在真实数据上仍可能失败，因此在宣告完成前先运行一次。

**带有 Webhook、表单或聊天触发器时：** `n8n_test_workflow({workflowId})` — 默认的 `method: "auto"` 会检测触发器并通过 HTTP 触发（工作流必须处于激活状态）。

**没有此类触发器时**（手动触发器、计划任务、子工作流）没有 HTTP 入口点。使用固定数据路径，该路径通过 n8n 自身的 MCP 服务器运行（`N8N_MCP_ACCESS_TOKEN`，n8n 2.34+）：

1. `n8n_test_workflow({workflowId, method: "prepare"})` — 列出需要固定数据的节点。
2. 为每个列出的节点构建一个示例项，以节点**名称**为键，每个项包裹在 `{json: {...}}` 中：
   ```json
   {"When clicking 'Test workflow'": [{"json": {"orderId": "1234", "email": "a@b.com"}}]}
   ```
   将扁平对象而非 `{json}` 项数组是此处常见的错误。
3. `n8n_test_workflow({workflowId, method: "pinned", pinData})` — 使用该数据运行并等待结果。

**对于没有固定数据的快速手动运行**，`method: "direct"` 启动一次手动执行，并在启动后立即返回；轮询 `n8n_executions({action: "get", id: executionId, mode: "error"})` 获取结果。在 `direct` 运行中不固定任何数据，因此每个节点都会执行，其发出的任何外部调用都是真实的 —— 即使是 `pinned` 也仅固定触发器、凭据和 HTTP 请求节点。`executionMode: "production"` 改变执行上下文，而非是否有副作用；除非用户要求生产运行，否则保留默认值。

**`method: "auto"` 从不通过 n8n 的 MCP 服务器运行工作流。** 在没有外部触发器的工作流上，它会报告该事实并列出 `prepare`/`pinned`/`direct`；路由方法仅在您按名称请求时运行。

**首次路由运行前需征得同意。** n8n 拒绝针对“在 MCP 中可用”设置关闭的工作流的这些调用，返回 `WORKFLOW_NOT_EXPOSED`。使用 `exposeToMcp: true` 重新运行会开启该设置并重试一次。这是工作流上一个可见且持久的设置（启用它是工作流更新，因此并发 UI 编辑可能被覆盖）—— **在传递前请咨询用户**。同意流程仅开启该设置；没有任何隐式关闭机制。再次关闭是有意行为：`n8n_update_partial_workflow({id: workflowId, operations: [{type: "updateSettings", settings: {availableInMCP: false}}]})`，或在 n8n UI 中切换开关。

**读取结果：** 已启动但随后失败的运行返回 `EXECUTION_FAILED` 及 `executionId` — 使用 `n8n_executions({action: "get", id, mode: "error"})` 检查，从抛错的节点开始修复，然后重新验证并运行。

---

## 审查现有工作流

在构建过程中验证（上述循环）用于捕捉您进行中工作的模式和形状错误。**审查现有工作流** — 您自己的或被交付的 — 是另一项工作：工作流已通过 `validate_workflow` 验证，而您正在寻找验证无法发现的问题（静默连接错误、易受注入的查询、丢失项的开关节点、Set/代码反模式、缺失的错误路径）。为此，使用 `n8n_get_workflow` 获取工作流并遍历 **[REVIEW_CHECKLIST.md](REVIEW_CHECKLIST.md)** — 一个按严重级别分层的审计（必须修复 / 应该修复 / 建议优化），每一项都指向修复的规范技能。同时运行 `n8n_audit_instance` 以揭示整个实例中硬编码的密钥和未认证的 Webhook。

---

## 详细指南

关于全面的错误目录、误报和工作流审查：

- **[ERROR_CATALOG.md](ERROR_CATALOG.md)** - 包含示例的完整错误类型列表
- **[FALSE_POSITIVES.md](FALSE_POSITIVES.md)** - 何时警告可被接受
- **[REVIEW_CHECKLIST.md](REVIEW_CHECKLIST.md)** - 用于审查现有工作流的严重级别分层审计

---

## 摘要

**关键点**：
1. **验证是迭代的**（平均 2-3 个循环，23 秒 + 58 秒）
2. **必须修复错误**，警告可选
3. **自动清理** 在保存时规范化操作符结构；验证不再对原始形状报错
4. **默认使用 runtime 配置**；如需最佳实践建议，升级到 `ai-friendly`/`strict`
5. **经典误报已修复**（≥ 2.63.0） — 剩余警告是建议或安全/弃用通知，而非验证器错误
6. **阅读错误信息** - 其中包含修复指导

**验证流程**：
1. 验证 → 阅读错误 → 修复 → 再次验证
2. 重复直到有效（通常 2-3 次迭代）
3. 审查警告并判断是否可接受
4. 有信心地部署

**相关技能与工具**：
- n8n MCP 工具专家 - 正确使用验证工具
- n8n 表达式语法 - 修复表达式错误
- n8n 节点配置 - 理解必填字段
- `n8n_audit_instance` - 主动安全验证（硬编码密钥、未认证 Webhook、缺失错误处理、数据保留）
