# JavaScript 代码节点

在 n8n 代码节点中编写 JavaScript 代码的专业指导。

---

## 快速入门

```javascript
// 代码节点的基本模板
const items = $input.all();

// 处理数据
const processed = items.map(item => ({
  json: {
    ...item.json,
    processed: true,
    timestamp: new Date().toISOString()
  }
}));

return processed;
```

### 基本规则

1. **选择“为所有项目运行一次”模式**（推荐大多数用例）
2. **访问数据**：`$input.all()`、`$input.first()` 或 `$input.item`
3. **返回 `[{json: {...}}]`** — 标准的、模式便携的形式。在*为所有项目运行一次*模式下，n8n 也会自动包装一个裸的 `return {…}` 对象，所以它也能运行；真正失败的是返回原始值（字符串/数字）或 `null`。
4. **关键**：Webhook 数据位于 `$json.body`（不是直接 `$json`）
5. **内置函数可用**：`this.helpers.httpRequest()`（无认证 — 裸的 `$helpers` 全局在任务运行沙盒中是**未定义**的，所以 `$helpers.httpRequest()` 会抛出 `ReferenceError: $helpers is not defined`），DateTime（Luxon），$jmespath(). **不可用**：`this.helpers.httpRequestWithAuthentication`（已禁止），$env（当 N8N_BLOCK_ENV_ACCESS_IN_NODE=true 时），require()（除非允许）。对于超出简单未认证 GET 的任何内容（认证、分页、重试），请优先使用**HTTP 请求节点**，并将代码节点用于纯逻辑。
6. **实例允许列表的库**：自托管实例可以通过 `N8N_RUNNERS_ALLOWED_BUILT_IN_MODULES` 和 `N8N_RUNNERS_ALLOWED_EXTERNAL_MODULES` 允许模块（遗留：`NODE_FUNCTION_ALLOW_BUILTIN` / `NODE_FUNCTION_ALLOW_EXTERNAL`）。如果用户说他们的实例允许特定模块（例如 `axios`、`lodash`、`crypto`），请通过 `require()` 使用它们 — 不要拒绝。如有疑问，请询问或默认仅使用内置函数。
7. **技能错误？** 如果你为连接到 AI 代理的**自定义代码工具**（`@n8n/n8n-nodes-langchain.toolCode`）编写代码，请停止 — 该节点有不同的契约（通过 `query` 输入，必须返回字符串，没有 `$input`/`$helpers`）。使用**n8n-code-tool**技能。

---

## 模式选择指南

代码节点提供两种执行模式。根据你的用例选择：

### 为所有项目运行一次（推荐 - 默认）

**使用此模式的情况**：95% 的用例

- **工作原理**：无论输入数量如何，代码都**执行一次**
- **数据访问**：`$input.all()` 或 `items` 数组
- **适用场景**：聚合、过滤、批量处理、转换、使用所有数据的 API 调用
- **性能**：对于多个项目更快（单次执行）

```javascript
// 示例：从所有项目计算总和
const allItems = $input.all();
const total = allItems.reduce((sum, item) => sum + (item.json.amount || 0), 0);

return [{
  json: {
    total,
    count: allItems.length,
    average: total / allItems.length
  }
}];
```

**使用场景**：
- ✅ 跨数据集比较项目
- ✅ 计算总计、平均值或统计数据
- ✅ 排序或排名项目
- ✅ 去重
- ✅ 构建聚合报告
- ✅ 组合来自多个项目的数据

### 为每个项目运行一次

**仅用于特殊情况的场景**：

- **工作原理**：为每个输入项目**单独执行**代码
- **数据访问**：`$input.item` 或 `$item`
- **适用场景**：项目特定逻辑、独立操作、逐项验证
- **性能**：对于大型数据集较慢（多次执行）

```javascript
// 示例：为每个项目添加处理时间戳
const item = $input.item;

return [{
  json: {
    ...item.json,
    processed: true,
    processedAt: new Date().toISOString()
  }
}];
```

**使用场景**：
- ✅ 每个项目需要独立的 API 调用
- ✅ 需要不同错误处理的逐项验证
- ✅ 基于项目属性的项目特定转换
- ✅ 当项目必须为业务逻辑单独处理时

**决策捷径**：
- **需要查看多个项目？** → 使用“所有项目”模式
- **每个项目完全独立？** → 使用“每个项目”模式
- **不确定？** → 使用“所有项目”模式（你可以随时在内部循环）

### 为什么“所有项目”更快 — 每个项目边界

模式选择是代码节点中最大的性能杠杆。每个*逐项目*执行上下文都有设置成本（在 n8n 2.x 上测量，小记录）：

| 每个项目运行的内容 | 大约成本 |
|---|---|
| 代码 **所有项目**（对整个集合运行一次） | ~0.02 ms/项目 |
| 任何节点中的表达式（IF / Set / 等。） | ~0.2 ms/项目 |
| 代码 **每个项目**（每个项目一个完整的沙盒） | ~0.6 ms/项目 — ~25–30× 所有项目 |

所以 `Run Once for Each Item` 对于 10k 个项目是 ~6 秒的纯开销，而 `Run Once for All Items` 是 ~0.2 秒。仅在项目确实需要隔离（独立错误处理或无法批量处理的逐项 API 调用）时使用每个项目；否则在所有项目节点内部循环。表达式复杂性本身几乎是免费的（~90% 的成本是逐项目上下文，而不是你的代码），并且每个节点到节点的跳转都会重新复制所有项目 — 所以减少*逐项目边界*的数量，而不是微优化每个边界。对于几百个项目以下，这些都不重要；在热点路径（大量项目，少量 I/O）上使用它们。

**参见**：[DATA_ACCESS.md](DATA_ACCESS.md) → "模式性能" 以了解推论、跳转成本和规模检查。

---

## 数据访问模式

从上游节点获取数据的四种方式。注意 `$node["Name"]` 和 `$('Name')` 需要使用 `.first().json` 或 `.all()` — 永远不要直接 `.json`。

```javascript
const allItems = $input.all();          // 1. 所有项目 — 批量操作，聚合（最常见）
const data = $input.first().json;       // 2. 第一个项目 — 单个项目对象，API 响应
const item = $input.item;               // 3. 当前项目 — 仅在“每个项目”模式下（否则未定义）
const other = $node["Webhook"].json;    // 4. 命名节点 — 跨节点组合数据
```

始终通过 `.json` 访问字段（例如 `item.json.name`，而不是 `item.name`），并优先使用显式的 `$input.first().json.field` 而不是裸的 `$json.field`。

**参见**：[DATA_ACCESS.md](DATA_ACCESS.md) 以获取完整指南 — 每种模式附带示例、决策树和常见错误（修改原始数据、缺少长度检查、在错误模式下使用 `$input.item`）。

---

## 关键：Webhook 数据结构

**最常见错误**：Webhook 数据嵌套在 `.body` 下

```javascript
// ❌ 错误 — 将返回未定义
const name = $json.name;
const email = $json.email;

// ✅ 正确 — Webhook 数据位于 .body 下
const name = $json.body.name;
const email = $json.body.email;

// 或使用 $input
const webhookData = $input.first().json.body;
const name = webhookData.name;
```

**原因**：Webhook 节点将所有请求数据包装在 `body` 属性下。这包括 POST 数据、查询参数和 JSON 有效负载。

**参见**：[DATA_ACCESS.md](DATA_ACCESS.md) 以获取完整的 webhook 结构详细信息

---

## 返回格式要求

**标准形式**：`[{json: {...}}]` — 每个项目都有一个 `json` 属性的数组。它是明确的，并且在两种执行模式下都行为相同，所以将其作为默认值。

在*为所有项目运行一次*模式下，n8n 会自动规范化输出路径上的松散形状：单个裸对象或裸对象数组会为您包装在 `json` 下。所以 `return {foo: 1}` 可以运行。什么没有要包装的，并且在运行时真正导致“代码没有正确返回项目”错误的是原始值（字符串/数字/布尔值）或 `null`/`undefined`。（n8n-mcp ≥ 2.63.0 不再将裸对象返回标记为错误；它反映了这种自动包装行为。）

### 正确的返回格式

```javascript
// ✅ 单个结果
return [{
  json: {
    field1: value1,
    field2: value2
  }
}];

// ✅ 多个结果
return [
  {json: {id: 1, data: 'first'}},
  {json: {id: 2, data: 'second'}}
];

// ✅ 转换数组
const transformed = $input.all()
  .filter(item => item.json.valid)
  .map(item => ({
    json: {
      id: item.json.id,
      processed: true
    }
  }));
return transformed;

// ✅ 空结果（当没有要返回的数据时）
return [];

// ✅ 条件返回
if (shouldProcess) {
  return [{json: processedData}];
} else {
  return [];
}
```

### 非标准返回（自动包装 — 优先使用标准形式）

```javascript
// ⚠️ 在“所有项目”模式下自动包装 → [{json: {field: value}}]。可以运行，但优先使用数组形式。
return {
  json: {field: value}
};

// ⚠️ 自动包装 → [{json: {field: value}}]。可以运行，但添加 json 包装以增加清晰度。
return [{field: value}];

// ✅ 可以 — 输入项目已经带有 json 属性，所以返回它们不变是一个有效的传递
return $input.all();
```

### 真正错误的返回

```javascript
// ❌ 失败：原始值 — n8n 错误“代码没有正确返回项目”
return "processed";

// ❌ 失败：null / undefined — 没有要传递给下一个节点的数据
return null;
```

**为什么这很重要**：标准的 `[{json: {...}}]` 是明确的，并且在两种模式下行为相同。n8n 在“所有项目”模式下自动规范化裸对象和对象数组，但原始值或 `null` 返回没有要包装的，并且会停止执行。

**参见**：[ERROR_PATTERNS.md](ERROR_PATTERNS.md) #3 以获取详细的错误解决方案

---

## 常见模式概述

生产工作流中最有用的代码节点形状。一个快速示例 — 跨所有项目求和：

```javascript
const items = $input.all();
const total = items.reduce((sum, item) => sum + (item.json.amount || 0), 0);
return [{ json: { total, count: items.length, average: total / items.length } }];
```

完整库涵盖了 10 种模式：多源聚合、正则表达式过滤、Markdown/结构化文本解析、JSON 比较、CRM/表单转换、发布处理、带计算字段的数组转换、Slack Block Kit 格式化、前 N 名排名和字符串聚合报告 — 每种模式都有变体。

**参见**：[COMMON_PATTERNS.md](COMMON_PATTERNS.md) 以获取 10 种详细的生产行模式（以及最佳实践部分：验证输入、try-catch、早期过滤、数组方法优于循环、console.log 调试）。

---

## 错误预防 - 常见错误

代码节点中反复出现的错误，按频率排序：

1. **空代码 / 缺少返回** — 始终以 `return [...]` 结尾，并确保*每个*分支都返回。
2. **表达式语法作为代码** — 不要在 JavaScript 位置写 `{{ }}`（`return {{ $json.x }}` 是语法错误）。使用 `` `${$json.field}` `` 或 `$input.first().json.field`。`{{ }}` *在字符串字面量内部*是允许的 — 它只是 n8n 不会评估的普通文本。
3. **返回形状** — 优先 `return [{json:{...}}]`。在“所有项目”模式下，裸的 `return {…}` 会自动包装，但返回原始值（字符串/数字）或 `null` 才会真正失败。
4. **缺少空值检查** — 使用可选链：`item.json?.user?.email || 'fallback'`。
5. **Webhook 嵌套** — `$json.email` 未定义；使用 `$json.body.email`。
6. **认证帮助程序被阻止**（`httpRequestWithAuthentication`）和 `$env` 被阻止 — 通过凭证/HTTP 请求节点传递密钥，而不是代码节点沙盒。

**参见**：[ERROR_PATTERNS.md](ERROR_PATTERNS.md) 以获取全面指南 — 每种错误附带正确/错误的代码、转义规则、沙盒限制（错误 #6–#7）、预防检查清单和快速错误消息查找表。

---

## 内置函数和帮助程序

```javascript
// HTTP 请求（无认证 — 参见沙盒注释）
const res = await this.helpers.httpRequest({ method: 'GET', url: 'https://api.example.com/data' });

// DateTime（Luxon）：当前时间、格式化、算术
const now = DateTime.now();
const formatted = now.toFormat('yyyy-MM-dd');
const tomorrow = now.plus({ days: 1 });

// $jmespath() — 查询 JSON 结构
const adults = $jmespath($input.first().json, 'users[?age >= `18`]');

// $getWorkflowStaticData() — 跨执行持久化的数据
```

**沙盒（自 n8n v2.0，JsTaskRunnerSandbox）**：访问器是 `this.helpers.httpRequest()` — 裸的 `$helpers` 全局在这里是**未定义**的（`$helpers.httpRequest()` 会抛出 `ReferenceError`）。在嵌套异步函数中，如果 `this` 丢失，调用它作为 `await fn.call(this, ...)`。`this.helpers.httpRequestWithAuthentication` 和 `this.helpers.requestWithAuthenticationPaginated` 被禁止（→ `UnsupportedFunctionError`）；对于认证调用，使用带有凭证的**HTTP 请求节点**（首选）、子工作流或手动在 `this.helpers.httpRequest()` 上添加 `Authorization: Bearer ${token}` 标头（仅当令牌已经作为数据通过工作流传递时）。当 `N8N_BLOCK_ENV_ACCESS_IN_NODE=true` 时，`$env` 被阻止；`require()` 仅适用于允许列表的模块。`Buffer`、`URL` 和标准 JS 全局（Math、JSON、Object、Array）始终可用。

**参见**：[BUILTIN_FUNCTIONS.md](BUILTIN_FUNCTIONS.md) 以获取完整参考 — 完整 httpRequest 选项、所有 DateTime/Luxon 操作、JMESPath 模式、静态数据用例和沙盒限制详细信息。

---

## 最佳实践

- **首先验证输入** — 在处理之前，为空数组 / 缺少 `.json` 进行保护。
- **对风险工作使用 try-catch**（HTTP 调用）并返回错误对象，而不是崩溃。
- **优先使用数组方法**（`filter`/`map`/`reduce`）而不是手动循环。
- **早期过滤，后期转换** — 在进行昂贵工作之前缩小数据集。
- **描述性名称** 和 `console.log()` 用于调试（输出将发送到浏览器控制台）。

**参见**：[COMMON_PATTERNS.md](COMMON_PATTERNS.md) → "最佳实践" 以获取每个模式的代码示例。

---

## 生产中的常见问题

从实际部署中获得的宝贵经验 — 这里总结，代码在 [DATA_ACCESS.md](DATA_ACCESS.md) → "生产中的常见问题" 中：

- **SplitInBatches 输出难以理解**：`main[0]` = **完成**（在所有批次后触发一次），`main[1]` = **每个批次**（循环体）。在完成输出后添加一个**限制 1** 节点作为安全措施。
- **迭代计数是成本**：每个循环迭代都会重新运行整个身体通过引擎（~0.8 ms 开销每个）。`batchSize: 1` 是循环的*每个项目*等价物 — 使用你的实际约束（速率限制、页面大小、内存）允许的最大批次，或者根本不循环。
- **跨迭代累积（关键）**：循环后，`$('Node Inside Loop').all()` 仅返回最后一次迭代的项。通过 `$getWorkflowStaticData('global')` 累积（重置前，内部推，读取后）。
- **pairedItem**：当发出不 1:1 映射到输入的项目时，设置 `pairedItem: { item: i }` 或下游 Set 节点会因 `paired_item_no_info` 而失败。
- **节点引用语法**：`$('Node').first().json` 或 `$('Node').all()` — 永远不要在引用上直接 `.json`。
- **浮点精度**：在分币级别比较货币 — `Math.round(a*100) !== Math.round(b*100)` — 以避免由于浮点噪声导致的错误阳性。

---

## 何时使用代码节点

> **在触及代码节点之前，请通过 n8n 表达式语法技能中的转换门卫**：表达式 → 箭头函数 IIFE 在 Edit Fields 字段内部 → 代码节点，按此顺序。前两种路径涵盖了大多数“转换这些数据”任务，每个约 1–10ms，而代码节点的沙盒化约 500–1000ms — 在纯单项目形状上差距约 100x，功能上没有区别。代码节点只有在以下情况下才值得使用：全数据集聚合（`$input.all()`）、允许列表的库或异步工作。并且在使用代码节点为加密（HMAC、哈希、签名）或 XML/SOAP/RSS 解析之前，检查是否有**原生节点** — n8n 有一个 Crypto 节点（`nodes-base.crypto`）和一个 XML 节点（`nodes-base.xml`）可以覆盖这些，而无需任何 JavaScript。对于原生节点已经可以做的事情而使用代码节点是最常见的错误之一。

使用代码节点当：
- ✅ 复杂转换需要多个步骤
- ✅ 自定义计算或业务逻辑
- ✅ 递归操作
- ✅ 复杂结构的 API 响应解析
- ✅ 多步条件
- ✅ 跨项目数据聚合

考虑其他节点当：
- ❌ 简单字段映射 → 使用 **Set** 节点
- ❌ 基本过滤 → 使用 **Filter** 节点
- ❌ 简单条件 → 使用 **IF** 或 **Switch** 节点
- ❌ 仅 HTTP 请求 → 使用 **HTTP Request** 节点

**代码节点擅长**：需要多个简单节点链接的复杂逻辑

---

## 与其他技能的集成

### 兼容：

**n8n 表达式语法**：
- 表达式使用 `{{ }}` 语法在其他节点中
- 代码节点直接使用 JavaScript（没有 `{{ }}`）
- 何时使用表达式 vs 代码

**n8n MCP 工具专家**：
- 如何找到代码节点：`search_nodes({query: "code"})`
- 获取配置帮助：`get_node({nodeType: "nodes-base.code"})`
- 验证代码：`validate_node({nodeType: "nodes-base.code", config: {...}})`

**n8n 节点配置**：
- 模式选择（所有项目 vs 每个项目）
- 语言选择（JavaScript vs Python）
- 理解属性依赖

**n8n 工作流模式**：
- 转换步骤中的代码节点
- Webhook → 代码 → API 模式
- 工作流中的错误处理

**n8n 验证专家**：
- 验证代码节点配置
- 处理验证错误
- 自动修复常见问题

---

## 快速参考检查清单

部署代码节点之前，请验证：

- [ ] **代码不为空** - 必须有有意义的逻辑
- [ ] **存在返回语句** - 返回项目，而不是原始值/`null`
- [ ] **标准返回格式** - 每个项目：`{json: {...}}`（裸对象自动包装，但保持明确）
- [ ] **数据访问正确** - 使用 `$input.all()`、`$input.first()` 或 `$input.item`
- [ ] **未写代码作为表达式** - 使用 JavaScript 模板字面量：`` `${value}` ``
- [ ] **错误处理** - 对空/未定义输入进行保护性条款
- [ ] **Webhook 数据** - 如果来自 webhook，通过 `.body` 访问
- [ ] **模式选择** - “所有项目”
- [ ] **性能** - 优先 map/filter 而不是手动循环
- [ ] **输出一致** - 所有代码路径返回相同结构

---

## 额外资源

### 相关文件
- [DATA_ACCESS.md](DATA_ACCESS.md) - 全面数据访问模式
- [COMMON_PATTERNS.md](COMMON_PATTERNS.md) - 10 个生产测试模式
- [ERROR_PATTERNS.md](ERROR_PATTERNS.md) - 5 个常见错误和解决方案
- [BUILTIN_FUNCTIONS.md](BUILTIN_FUNCTIONS.md) - 完整内置参考

### n8n 文档
- 代码节点指南：https://docs.n8n.io/code/code-node/
- 内置方法：https://docs.n8n.io/code-examples/methods-variables-reference/
- Luxon 文档：https://moment.github.io/luxon/

---

**准备好在 n8n 代码节点中编写 JavaScript 了！** 从简单的转换开始，使用错误模式指南避免常见错误，并参考模式库以获取生产就绪的示例。
