---
name: n8n-node-configuration
description: 操作感知节点配置指南。在配置节点时使用，用于理解属性依赖关系、确定所需字段、选择获取节点详情级别，或学习按节点类型常见的配置模式。在设置节点参数时始终使用此技能——它解释了每个操作所需的字段、displayOptions如何控制字段可见性，以及何时使用patchNodeField进行精准编辑而非全节点更新。
---

# n8n 节点配置

针对具有属性依赖关系的操作感知节点配置的专业指导。

---

## 配置理念

**渐进式披露**：从最简开始，按需添加复杂度

配置最佳实践：
- 使用 `get_node` 并设置 `detail: "standard"` 是最常用的发现模式
- 平均每 56 秒进行一次配置编辑
- 使用 1-2K 个 token 的响应即可覆盖 95% 的用例

**关键洞察**：大多数配置只需要标准详情，不需要完整模式！

---

## 核心概念

### 1. 操作感知配置

**并非所有字段在所有情况下都必需** - 这取决于操作！

**示例**：Slack 节点
```javascript
// 对于 operation='post'
{
  "resource": "message",
  "operation": "post",
  "channel": "#general",  // post 操作必需
  "text": "Hello!"        // post 操作必需
}

// 对于 operation='update'
{
  "resource": "message",
  "operation": "update",
  "messageId": "123",     // update 操作必需（不同！）
  "text": "Updated!"      // update 操作必需
  // channel 对于 update 操作不是必需的
}
```

**关键**：资源 + 操作决定哪些字段是必需的！

### 2. 属性依赖

**字段的显示/隐藏取决于其他字段的值**

**示例**：HTTP 请求节点
```javascript
// 当 method='GET'
{
  "method": "GET",
  "url": "https://api.example.com"
  // sendBody 字段未显示（GET 没有请求体）
}

// 当 method='POST'
{
  "method": "POST",
  "url": "https://api.example.com",
  "sendBody": true,       // 现在可见！
  "body": {               // 当 sendBody=true 时必需
    "contentType": "json",
    "content": {...}
  }
}
```

**机制**：displayOptions 控制字段可见性

### 3. 渐进式发现

**使用正确的详情级别**：

1. **get_node({detail: "standard"})** - 默认值
   - 快速概览 (~1-2K tokens)
   - 必需字段 + 常见选项
   - **首先使用** - 覆盖 95% 的需求

2. **get_node({mode: "search_properties", propertyQuery: "..."})**（用于查找特定字段）
   - 通过名称查找属性
   - 当查找认证、请求体、头部等时使用

3. **get_node({detail: "full"})**（完整模式）
   - 所有属性 (~3-8K tokens)
   - 仅在标准详情不足时使用

---

## 配置工作流程

### 标准流程

1. 确定节点类型和操作。
2. 使用 `get_node`（默认为标准详情）。
3. 配置必需字段。
4. 验证配置。
5. 如果字段不明确 → `get_node({mode: "search_properties"})`。
6. 根据需要添加可选字段。
7. 再次验证。
8. 部署。

### 示例：配置 HTTP 请求

实际操作中的验证驱动循环：从最简配置开始（`method`、`url`、`authentication`），然后让每个 `validate_node` 错误暴露下一个必需字段（POST 的 `sendBody` → `sendBody=true` 时的 `body`），直到配置有效。完整步骤说明请参考 **[OPERATION_PATTERNS.md](OPERATION_PATTERNS.md#worked-example-configuring-http-request-step-by-step)**。

---

## get_node 详情级别

### 标准详情（默认值 - 使用此值！）

**✅ 开始配置**
```javascript
get_node({
  nodeType: "nodes-base.slack"
});
// detail="standard" 是默认值
```

**返回** (~1-2K tokens)：
- 必需字段
- 常见选项
- 操作列表
- 元数据

**使用**：95% 的配置需求

### 完整详情（谨慎使用）

**✅ 当标准值不足时**
```javascript
get_node({
  nodeType: "nodes-base.slack",
  detail: "full"
});
```

**返回** (~3-8K tokens)：
- 完整模式
- 所有属性
- 所有嵌套选项

**警告**：响应较大，仅在标准值不足时使用

### 搜索属性模式

**✅ 查找特定字段**
```javascript
get_node({
  nodeType: "nodes-base.httpRequest",
  mode: "search_properties",
  propertyQuery: "auth"
});
```

**使用**：查找认证、头部、请求体字段等

### 决策树

1. 开始新的节点配置 → `get_node`（标准值）。
2. 标准值包含所需内容 → 使用它。否则继续。
3. 查找特定字段 → `search_properties` 模式。否则继续。
4. 仍然需要更多 → `get_node({detail: "full"})`。

**动态属性**：当 `standard` 详情标记属性为 `dynamicOptions: {methodName, methodType, dependsOn}` 时，其真实值来自实时 `loadOptions`/`listSearch` 方法，而不是捆绑文档 — 不要猜测 ID。使用 `n8n_explore_node_resources`（需要 `N8N_MCP_ACCESS_TOKEN`，n8n 2.34+）解决它，并将返回的 `value` 放入配置中；`name` 仅用于显示。

所有六个参数都是必需的，彼此之间没有推断：

```javascript
n8n_explore_node_resources({
  nodeType: "n8n-nodes-base.googleSheets",  // 长形式
  version: 4.5,                              // 方法所属的节点类型版本
  methodName: "getSheets",                   // 从 dynamicOptions 复制
  methodType: "listSearch",                  // "listSearch" 用于资源定位器，"loadOptions" 用于普通下拉菜单
  credentialType: "googleSheetsOAuth2Api",
  credentialId: "c2",                        // 从 n8n_manage_credentials({action: "list"}) 获取
  currentNodeParameters: {                   // 依赖的名称，以真实形状呈现
    documentId: {__rl: true, mode: "id", value: "1AbC…"}
  }
})
```

`dependsOn` 指出方法需要的参数名称 — 将它们放入 `currentNodeParameters`，保持资源定位器值在 `{__rl: true, mode, value}` 形状中，否则方法返回无用的结果。`methodName` 对 `nodeType` + `version` 对来说是区分大小写的；不匹配返回 `OFFICIAL_MCP_ERROR` 而不是空列表。

---

## 属性依赖深入解析

字段具有 `displayOptions` 可见性规则：`show`/`hide` 块中多个条件进行 AND 运算，多个值进行 OR 运算（例如 `body` 在 `sendBody=true` AND `method IN (POST, PUT, PATCH)` 时显示）。三个常见模式是布尔切换（sendBody → body）、操作切换（post 与 update 显示不同字段）和类型选择（字符串与布尔条件）。要查找控制字段的内容，使用 `get_node({mode: "search_properties", propertyQuery: "..."})` 或 `get_node({detail: "full"})` — 特别是在验证标记了未显示字段时。

机制细节、所有四个依赖模式、复杂流程、嵌套依赖和故障排除在 **[DEPENDENCIES.md](DEPENDENCIES.md)**（快速参考摘要在 [快速参考：displayOptions 和常见依赖模式](DEPENDENCIES.md#quick-reference-displayoptions-and-common-dependency-patterns)）。

---

## 常见节点模式

### 模式 1：资源/操作节点

**示例**：Slack、Google Sheets、Airtable

**结构**：
```javascript
{
  "resource": "<实体>",      // 什么类型的对象
  "operation": "<动作>",     // 对它做什么
  // ... 操作特定字段
}
```

**如何配置**：
1. 选择资源
2. 选择操作
3. 使用 get_node 查看操作特定要求
4. 配置必需字段

### 模式 2：基于 HTTP 的节点

**示例**：HTTP 请求、Webhook

**结构**：
```javascript
{
  "method": "<HTTP_METHOD>",
  "url": "<端点>",
  "authentication": "<类型>",
  // ... 方法特定字段
}
```

**依赖关系**：
- POST/PUT/PATCH → sendBody 可用
- sendBody=true → body 必需
- authentication != "none" → 凭据必需

**关键**：凭据块、节点 id、类型版本
- **永远不要设置占位符凭据 ID**（例如 `"id": "REPLACE_ME"`）— n8n 的 UI 会为未知 ID 渲染永久禁用的凭据选择器。当真实 ID 未知时，省略 `credentials` 块；用户将获得正常的可点击下拉菜单。
- **节点 `id` 必须是 UUID v4**，而不是可读的别名 — 前端将其绑定到表单和凭据组件。
- **不要硬编码旧的 `typeVersion` 值** — 使用 `get_node` 验证当前版本（httpRequest 是 4.4+）。

### 模式 3：数据库节点

**示例**：Postgres、MySQL、MongoDB

**结构**：
```javascript
{
  "operation": "<查询|插入|更新|删除>",
  // ... 操作特定字段
}
```

**依赖关系**：
- operation="executeQuery" → 查询必需
- operation="insert" → 表 + 值必需
- operation="update" → 表 + 值 + where 必需

**关键**：写操作可能返回 0 项
- INSERT、UPDATE、DELETE 可能产生 0 个 n8n 输出项，取决于节点和操作（原始查询执行可靠地返回 0 结果行；某些数据库节点返回受影响的行数）
- 在写操作节点上设置 `alwaysOutputData: true` 以保持下游链路活跃
- 下游节点应使用 `$('UpstreamNode').all()` 而不是 `$input`，如果它们需要数据

### 模式 4：条件逻辑节点

**示例**：IF、Switch、Merge

**结构**：
```javascript
{
  "conditions": {
    "<类型>": [
      {
        "operation": "<运算符>",
        "value1": "...",
        "value2": "..."  // 仅用于二元运算符
      }
    ]
  }
}
```

**依赖关系**：
- 二元运算符（等于、包含等）→ value1 + value2
- 一元运算符（isEmpty、isNotEmpty）→ value1 仅 + singleValue: true

---

## 操作特定配置

必需字段随资源 + 操作变化：Slack `post` 需要 `channel`+`text`，但 `update` 需要 `messageId`+`text`（channel 可选）和 `channel/create` 需要 `name`。HTTP `GET` 使用 `sendQuery`+`queryParameters`；`POST` 需要 `sendBody`+`body`。IF 二元运算符（`equals`）需要 `value1`+`value2`；一元（`isEmpty`）只需要 `value1` 加上自动添加的 `singleValue: true`。每个的具体最小配置在 **[OPERATION_PATTERNS.md](OPERATION_PATTERNS.md#operation-specific-configuration-examples)**。

---

## 处理条件性需求

某些字段仅在特定条件下必需：HTTP `body` 在 `sendBody=true` AND `method IN (POST, PUT, PATCH, DELETE)` 时必需；IF `singleValue` 应该是 `true` 当运算符是一元（`isEmpty`、`isNotEmpty`、`true`、`false`）— 系统会自动设置它。通过阅读验证错误、搜索属性 (`get_node({mode: "search_properties"})`) 或从最小配置中迭代来发现条件性需求。工作示例在 **[DEPENDENCIES.md](DEPENDENCIES.md#handling-conditional-requirements)**。

---

## 节点特定配置说明

### SplitInBatches v3

```javascript
{
  "batchSize": 100,  // 每个批次的项目数量
  "options": {}
}
```

**输出连接**：
- `main[0]`（完成）→ 连接到下游处理（首先添加 Limit 1）
- `main[1]`（每个批次）→ 连接到循环体，然后循环回到 SplitInBatches 输入

查看 n8n 工作流模式技能以获取详细的循环和嵌套循环模式。

### Google Sheets 节点

**逐项执行**：每个输入项触发一个单独的 API 调用。如果你有 100 个项目并使用 Google Sheets "Append Row" 节点，它将执行 100 个 API 调用。要批量写入，请在 Code 节点中首先聚合项目，然后使用单个 HTTP 请求和 Sheets API。

**公式列**：不要在具有公式列的工作表中使用 `append` — 它会覆盖公式。相反，使用 HTTP 请求和 Google Sheets API `values.update`（PUT）方法和 `googleApi` 凭据。

---

## 配置反模式

### ❌ 不要：过早过度配置

**错误**：
```javascript
// 添加所有可能的字段
{
  "method": "GET",
  "url": "...",
  "sendQuery": false,
  "sendHeaders": false,
  "sendBody": false,
  "timeout": 10000,
  "ignoreResponseCode": false,
  // ... 20 个更多可选字段
}
```

**正确**：
```javascript
// 从最小值开始
{
  "method": "GET",
  "url": "...",
  "authentication": "none"
}
// 仅在需要时添加字段
```

### ❌ 不要：跳过验证

**错误**：
```javascript
// 配置后不验证就部署
const config = {...};
n8n_update_partial_workflow({...});  // YOLO
```

**正确**：
```javascript
// 部署前验证
const config = {...};
const result = validate_node({...});
if (result.valid) {
  n8n_update_partial_workflow({...});
}
```

### ❌ 不要：忽略操作上下文

**错误**：
```javascript
// 所有 Slack 操作使用相同配置
{
  "resource": "message",
  "operation": "post",
  "channel": "#general",
  "text": "..."
}

// 然后切换操作而不更新配置
{
  "resource": "message",
  "operation": "update",  // 改变
  "channel": "#general",  // update 不需要！
  "text": "..."
}
```

**正确**：
```javascript
// 切换操作时检查要求
get_node({
  nodeType: "nodes-base.slack"
});
// 查看更新操作需要什么（messageId，而不是 channel）
```

---

## 剪辑式字段编辑使用 patchNodeField

当你需要编辑节点字段中的特定字符串，而不是替换整个字段时，使用 `patchNodeField` 在 `n8n_update_partial_workflow` 中。这对于以下情况特别有用：
- 在 Code 节点中编辑代码，而无需重新传输整个代码块
- 更新大型 HTML 邮件模板中的 URL 或文本
- 修复 JSON 身体或长文本字段中的拼写错误

```javascript
// 而不是替换整个 jsCode 字段：
n8n_update_partial_workflow({
  id: "wf-123",
  operations: [{
    type: "patchNodeField",
    nodeName: "Code",
    fieldPath: "parameters.jsCode",
    patches: [{find: "const limit = 10;", replace: "const limit = 50;"}]
  }]
})
```

`patchNodeField` 是严格的 — 如果 find 字符串未找到或匹配多次（除非 `replaceAll: true`），它会报错。这可防止配置更新期间出现意外的静默失败。查看 n8n MCP 工具专家技能以获取完整语法和示例。

---

## 最佳实践

### 要做

1. **从 get_node（标准详情）开始**
   - ~1-2K tokens 响应
   - 覆盖 95% 的配置需求
   - 默认详情级别

2. **迭代验证**
   - 配置 → 验证 → 修复 → 重复
   - 平均 2-3 次迭代是正常的
   - 小心阅读验证错误

3. **当卡住时使用 search_properties 模式**
   - 如果字段似乎缺失，搜索它
   - 了解什么控制字段可见性
   - `get_node({mode: "search_properties", propertyQuery: "..."})`

4. **尊重操作上下文**
   - 不同操作 = 不同需求
   - 切换操作时始终检查 get_node
   - 不要假设配置可移植

5. **信任自动清理**
   - 运算符结构自动固定
   - 不要手动添加/删除 singleValue
   - IF/Switch 元数据在保存时添加

### ❌ 不要

1. **立即跳到 detail="full"**
   - 首先尝试标准详情
   - 仅在需要时升级
   - 完整模式是 3-8K tokens

2. **盲目配置**
   - 始终在部署前验证
   - 了解为什么字段是必需的
   - 使用 search_properties 查找条件字段

3. **不理解就复制配置**
   - 不同操作需要不同字段
   - 复制后验证
   - 调整新上下文

4. **手动修复自动清理问题**
   - 让自动清理处理运算符结构
   - 专注于业务逻辑
   - 保存并让系统修复结构

---

## 节点系列静默失败陷阱

某些配置通过 `validate_node` 和 `validate_workflow` 检查通过，运行时无错误，但安静地做了错误的事情 — `get_node` 显示字段存在，但不知道省略它们会发生什么。高频出现的：

- **切换** — 没有 `options.fallbackOutput` ⇒ 未匹配的项将被静默丢弃。
- **合并** — `numberOfInputs` 默认为 2（额外的源将被丢弃）；`useDataOfInput` 是 1 索引的，而 `connections.<src>.main[idx]` 插槽是 0 索引的 (`useDataOfInput: "N"` → `main[N-1]`)。
- **数据库** — 在 `parameters.query` 中使用 `{{ }}` 插值是 SQL 注入；使用 `$1/$2` 占位符 + `options.queryReplacement`。
- **Slack** — Block Kit 必须用 `={{ { "blocks": ... } }}` 包裹，否则它将作为纯文本发布。
- **Webhook / 响应** — `responseCode` 即使在错误分支中也默认为 200。
- **计划触发器** — 时区是工作流级别的（工作流设置），而不是每个规则的。

**[NODE_FAMILY_GOTCHAS.md](NODE_FAMILY_GOTCHAS.md)** 中包含完整的症状/原因/修复细节（以 JSON + `n8n_update_partial_workflow` 术语表示）。

---

## 详细参考

关于特定主题的全面指南：

- **[DEPENDENCIES.md](DEPENDENCIES.md)** - 深入了解属性依赖和 displayOptions
- **[OPERATION_PATTERNS.md](OPERATION_PATTERNS.md)** - 按节点类型划分的常见配置模式
- **[NODE_FAMILY_GOTCHAS.md](NODE_FAMILY_GOTCHAS.md)** - 各类（切换、合并、数据库、Slack、Webhook、计划）的静默运行时陷阱

---

## 概要

**配置策略**：
1. 从 `get_node` 开始（标准细节是默认的）
2. 配置操作所需的字段
3. 验证配置
4. 卡住时搜索属性
5. 迭代直到有效（平均 2-3 轮）
6. 带着信心部署

**关键原则**：
- **操作感知**：不同的操作 = 不同的要求
- **渐进式披露**：从最小配置开始，按需添加
- **依赖感知**：理解字段可见性规则
- **验证驱动**：让验证引导配置

**相关技能**：
- **n8n MCP 工具专家** - 如何正确使用发现工具
- **n8n 验证专家** - 解释验证错误
- **n8n 表达式语法** - 配置表达式字段
- **n8n 工作流模式** - 正确配置模式应用
