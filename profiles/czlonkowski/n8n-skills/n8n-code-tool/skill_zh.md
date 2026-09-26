# n8n 自定义代码工具

在 `@n8n/n8n-nodes-langchain.toolCode` 内编写代码的专家指导 —— 这是 AI 代理可以调用的工具，**不是**常规工作流代码节点。

---

## ⚠️ 这不是代码节点

自定义代码工具在编辑器中看起来像代码节点 —— 同样的 JavaScript 编辑器，相似的布局 —— 但它是一个来自不同包、具有**不同运行时契约**的**完全不同的节点**。

| | 代码节点 | 自定义代码工具 |
|---|---|---|
| **节点类型** | `n8n-nodes-base.code` | `@n8n/n8n-nodes-langchain.toolCode` |
| **包** | `n8n-nodes-base` | `@n8n/n8n-nodes-langchain` |
| **被调用** | 前一个节点（工作流流） | AI 代理（LangChain） |
| **输入** | `$input.all()` — 项目流 | `query` — 来自 LLM 的字符串或对象 |
| **返回** | `[{json: {...}}]`（项目数组） | **一个字符串** |
| **`$fromAI()`** | N/A | **不可用**（见错误） |
| **HTTP 辅助工具** | `this.helpers.httpRequest`（阻止认证辅助工具） | 未在工具沙盒中暴露 |
| **状态** | 每次运行执行数据 | 没有 `getContext`，没有 `$getWorkflowStaticData` |

**如果你将其当作代码节点来处理，它就会失败。** 本技能的其余部分涵盖了代码工具的实际契约。

---

## 快速入门

### 最小化 JavaScript 代码工具

```javascript
// `query` 是 AI 发送的内容（默认为字符串）
return `你问：${query}`;
```

### 最小化 Python 代码工具

```python
# `_query` 是 AI 发送的内容（默认为字符串）
return f"你问：{_query}"
```

### 基本规则

1. **返回一个字符串。** 数字会自动转换。任何其他内容都会抛出 `"The response property should be a string, but it is an object"`。
2. **输入变量是固定的**：`query`（JS），`_query`（Python）。你不能重命名它。
3. **不要在代码工具沙盒内使用 `$fromAI()`** —— 它会抛出 `"No execution data available"`。
4. **不要使用 `[{json: {...}}]`** 返回格式 —— 那是代码节点的。会抛出 `"Wrong output type returned"`。
5. **使用描述性的工具名称**（字母/数字/下划线，v1.1+）。代理通过其名称调用工具。
6. **编写精确的描述** —— LLM 会根据它决定是否调用工具。

---

## 两种输入模式

代码工具有两种输入形状，由 `specifyInputSchema` 控制：

### 模式 1：非结构化（默认，`specifyInputSchema: false`）

AI 将**单个字符串**作为 `query` 传递。如果你需要多个字段，AI 必须将它们放入这个字符串中，然后你解析它们。实际上，如果描述告诉它们，LLM 会很乐意传递一个 JSON 字符串。

```javascript
// 解析 AI 发送的 JSON 字符串
let params;
try {
  params = typeof query === 'string' ? JSON.parse(query) : query;
} catch (e) {
  throw new Error('期望一个 JSON 对象。解析器说：' + e.message);
}
const price = Number(params.price);
const months = Number(params.months);
// ...
return JSON.stringify({ monthly_payment: /* ... */ });
```

**优点**：设置最简单，一个字段要描述。
**缺点**：没有模式验证 —— 如果 LLM 遗漏了字段，工具在运行时会抛出错误。

**适用于**：快速原型，具有一个自然输入的工具（一个问题、一个 URL、一个文本块）。

### 模式 2：结构化（`specifyInputSchema: true`）

该工具成为 LangChain 的 `DynamicStructuredTool`。LLM 会看到一个带类型注解的参数模式，并将**经过验证的对象**作为 `query` 传递。你可以直接访问字段。

```javascript
// query 现在是一个匹配你模式的对象
const price = query.price;
const months = query.months;
const residual_percent = query.residual_percent;

const monthly = computeAnnuity(price, months, residual_percent);
return JSON.stringify({ monthly_payment: monthly });
```

模式通过以下方式定义：
- `schemaType: "fromJson"` + `jsonSchemaExample`（n8n v≥1.3）—— 粘贴一个示例 JSON，n8n 推断模式
- `schemaType: "manual"` + `inputSchema` —— 你自己编写完整的 JSON Schema

**优点**：LLM 获得类型提示，无效调用在代码运行之前被拒绝，代码更干净。
**缺点**：设置稍微复杂一点；需要带模式支持的 n8n 版本。

**适用于**：具有多个带类型参数的生产工具（计算器、API 封装器、任何 LLM 倾向于将数字字段字符串化的东西）。

**参见**：[INPUT_SCHEMA.md](INPUT_SCHEMA.md) 以获取完整的模式设置。

---

## 返回格式

**返回值必须是一个字符串。** LLM 将其作为工具的观察结果读取。

```javascript
// ✅ 字符串
return "42";

// ✅ 数字（n8n 自动转换为字符串）
return 42;

// ✅ JSON 编码的结构化结果（推荐用于丰富输出）
return JSON.stringify({ result: 42, currency: "SEK" });

// ❌ 原始对象 → "The response property should be a string, but it is an object"
return { result: 42 };

// ❌ 工作流项目格式 → "Wrong output type returned"
return [{ json: { result: 42 } }];

// ❌ 数组 → "The response property should be a string, but it is an object"
return [1, 2, 3];
```

### 最佳实践：JSON-stringify 结构化结果

当你的工具有比简单标量输出更复杂的内容时，返回一个 JSON 字符串：

```javascript
return JSON.stringify({
  monthly_payment_sek: 5405,
  loan_amount: 351920,
  total_cost_of_credit: 63295
});
```

LLM 可靠地解析 JSON，并且可以挑选它需要向用户展示的字段。

### 错误处理：代理读取你的失败

错误不会仅仅停止工作流 —— 它们会返回到 LLM，LLM 通常会纠正它的调用并重试。使用这个：

```javascript
// 选项 A：抛出错误 — n8n 将消息显示给代理
if (!isFinite(price)) throw new Error('price 必须是一个数字，例如 439900');

// 选项 B：返回一个错误字符串 — 代理像任何工具结果一样读取它
if (!isFinite(price)) return JSON.stringify({ error: 'price 必须是一个数字，例如 439900' });
```

无论哪种方式，编写错误消息**针对 LLM**：说明哪里出错了，以及有效调用的样子。一个简单的 `throw new Error('invalid input')` 浪费了重试；一个说明性的消息通常可以修复下一次调用。

---

## 工具名称和描述

这些字段**不是**文档 —— 它们是 LLM 看到的**工具契约**。将它们视为提示工程。

### 名称
- 必须匹配 `[A-Za-z0-9_]+`（v1.1+）。不能有空格、连字符、表情符号。
- 使用一个描述性的动词名称：`calculate_car_loan`，`get_weather`，`search_orders`。
- 代理通过这个名称调用工具。`Code Tool`（默认）是无用的 —— 代理不知道何时调用它。

### 描述
- 解释**何时**使用它以及**发送什么内容**。
- 如果是非结构化模式，**在描述中包含 LLM 应发送的 JSON 字符串示例**。
- 如果是结构化模式，模式本身说明了目的 —— 只需描述用途。

**非结构化示例（JSON-in-string 模式）：**
```
确定性地计算汽车贷款的月付款。使用一个 JSON 字符串调用：
{"price":439900,"down_payment":87980,"interest_rate":6.95,"months":36,"residual_percent":50}
字段：price (SEK)，down_payment (SEK)，interest_rate (% per 年)，months，residual_percent (0-99)。
```

**结构化示例（模式定义）：**
```
确定性地计算给定价格、首付、年利率、期限和残值百分比的汽车贷款月付款。每当用户询问月成本、总信贷成本或贷款明细时使用。
```

---

## 常见错误和修复

### 错误 1：`"There was an error: 'Cannot assign to read only property \"name\" of object: Error: No execution data available'"`

**原因**：你在代码工具沙盒内调用了 `$fromAI()`。

**修复**：`$fromAI()` 是用于**其他**支持工具的节点（HTTP Request Tool、SendGrid Tool、`toolWorkflow` 等）的辅助工具 —— 它没有在 `toolCode` 中暴露。直接从 `query` 读取 AI 的输入（或使用 `specifyInputSchema` 获取结构化字段）。

### 错误 2：`"Wrong output type returned"`

**原因**：你返回了一个工作流风格的数组，如 `[{ json: { ... } }]`。那是代码**节点**的契约，不是代码**工具**的契约。

**修复**：返回一个字符串。对于结构化数据，`return JSON.stringify(output)`。

### 错误 3：`"The response property should be a string, but it is an object"`

**原因**：你返回了一个普通的对象或数组。

**修复**：`JSON.stringify()` 结果，或者强制转换为字符串。

### 错误 4：AI 从不调用工具

**原因**：工具名称很通用（`Code Tool`，`My Tool`）或描述没有清楚地说明何时使用它。

**修复**：重命名为一个描述性的动词名称（`calculate_car_loan`），并重写描述以明确说明触发条件（例如，“每当用户询问月成本时使用此工具”）。

### 错误 5：AI 向 `query` 发送垃圾

**原因**：非结构化工具描述模糊。LLM 猜测格式。

**修复**：要么 (a) 在描述中包含 LLM 应发送的**具体 JSON 示例**，要么 (b) 切换到 `specifyInputSchema: true`，以便 LLM 获得一个带类型注解的模式。

**参见**：[ERROR_PATTERNS.md](ERROR_PATTERNS.md) 以获取完整目录和重现。

---

## 沙盒中不可用的内容

代码工具沙盒比代码节点沙盒**更窄**。不要假设辅助工具会自动传递：

| 辅助工具 | 代码节点 | 代码工具 |
|---|---|---|
| `$input.all()`, `$input.first()`, `$input.item` | ✅ | ❌ |
| `$node["NodeName"]` | ✅ | ❌ |
| `$json`, `$binary` | ✅ | ❌ |
| `$fromAI()` | ❌ | ❌（尽管它位于 AI 代理旁边） |
| `this.helpers.httpRequest()` | ✅ | ❌ |
| `DateTime`（Luxon） | ✅ | ✅（JS 沙盒的标准内容） |
| `$jmespath()` | ✅ | ❌ |
| `this.getContext(...)` | ✅ | ❌ |
| `$getWorkflowStaticData(...)` | ✅ | ❌ |

**影响**：代码工具用于**纯计算**。如果你需要 HTTP 调用、API 查找或跨调用状态，请使用不同的工具节点：
- HTTP Request Tool 用于外部 API 调用
- `toolWorkflow`（调用子工作流工具）用于多步逻辑并访问完整的代码节点沙盒
- MCP / 数据库工具用于持久状态

---

## 何时使用代码工具与替代方案

使用 **代码工具** 当：
- ✅ 纯确定性计算（数学、解析、格式化、验证）
- ✅ 轻量级转换，LLM 不应自行处理（精度数学、正则表达式）
- ✅ 你希望代码直接嵌入工作流，而不是在单独的子工作流中

使用 **`toolWorkflow`**（调用子工作流工具）当：
- ✅ 你需要多个参数并具有干净的 `$fromAI()` 类型注解
- ✅ 你需要访问 `this.helpers`、凭证或其他节点
- ✅ 逻辑可以在多个代理之间重用
- ✅ 你希望带类型注解的输入，而**不需要**编写 JSON Schema

使用 **HTTP Request Tool** 当：
- ✅ 工具本质上是一个 API 调用
- ✅ 你希望每个参数的 `$fromAI()` 绑定在 URL/查询/正文

**经验法则**：如果你发现自己想要 `$fromAI()`，你可能需要 `toolWorkflow` 而不是 `toolCode`。

---

## 完整工作示例

一个生产计算器工具（非结构化，JSON-in-string 模式）：

```json
{
  "parameters": {
    "name": "calculate_car_loan",
    "description": "使用年金公式计算汽车贷款月付款，考虑残值/气球。使用单个 JSON 字符串调用。示例：{\"price\":439900,\"down_payment\":87980,\"interest_rate\":6.95,\"months\":36,\"residual_percent\":50,\"setup_fee\":695,\"monthly_admin_fee\":59}。必需：price, down_payment, interest_rate, months, residual_percent。可选：setup_fee, monthly_admin_fee（默认 0）。",
    "language": "javaScript",
    "jsCode": "let params;\ntry {\n  params = typeof query === 'string' ? JSON.parse(query) : query;\n} catch (e) {\n  throw new Error('Invalid JSON: ' + e.message);\n}\n\nconst price           = Number(params.price);\nconst down_payment    = Number(params.down_payment);\nconst interest_rate   = Number(params.interest_rate);\nconst months          = Number(params.months);\nconst residual_percent= Number(params.residual_percent);\nconst setup_fee       = Number(params.setup_fee ?? 0) || 0;\nconst monthly_admin_fee = Number(params.monthly_admin_fee ?? 0) || 0;\n\nif (!isFinite(price) || price <= 0) throw new Error('price must be > 0');\nif (down_payment < 0 || down_payment >= price) throw new Error('down_payment must be in [0, price)');\n\nconst principal = price - down_payment;\nconst residual  = price * (residual_percent / 100);\nconst r = interest_rate / 100 / 12;\nconst growth = Math.pow(1 + r, months);\nconst base = r === 0\n  ? (principal - residual) / months\n  : (principal - residual / growth) * r / (1 - 1 / growth);\nconst monthly_payment = base + monthly_admin_fee;\n\nreturn JSON.stringify({\n  monthly_payment_sek: Math.round(monthly_payment),\n  loan_amount: Math.round(principal),\n  residual_value_sek: Math.round(residual),\n  total_cost_of_credit: Math.round(monthly_payment * months + residual + setup_fee - principal)\n});"
  },
  "type": "@n8n/n8n-nodes-langchain.toolCode",
  "typeVersion": 1.3,
  "name": "calculate_car_loan"
}
```

通过 `ai_tool` 连接类型将其连接到 AI 代理。

---

## 与其他技能的集成

**n8n-code-javascript**：代码**节点**技能。大多数 JavaScript 模式（数组、map/filter、DateTime）可以迁移 —— 但 I/O 契约不同。不要复制数据访问代码。

**n8n-node-configuration**：`specifyInputSchema` 是一个典型的由 `displayOptions` 驱动的条件字段。使用 `get_node({detail: "standard"})` 在 `@n8n/n8n-nodes-langchain.toolCode` 上查看与模式相关的属性。

**n8n-workflow-patterns**：代码工具位于“带工具的 AI 代理”模式内。代理通常有多个工具；代码工具是“本地计算”选项。

**n8n-validation-expert**：上面列出的三个代码工具错误具有明确的特征 —— 如果验证显示“Wrong output type returned”，你知道要切换从数组-of-items 到字符串。

---

## 快速参考清单

部署代码工具之前：

- [ ] **节点类型** 是 `@n8n/n8n-nodes-langchain.toolCode`（不是 `nodes-base.code`）
- [ ] **工具名称** 是描述性的、动词式的、蛇形命名（例如 `calculate_car_loan`）
- [ ] **描述** 说明何时使用工具以及（如果非结构化）显示 LLM 应发送的 JSON 示例
- [ ] **输入** 从 `query`（JS）或 `_query`（Python）读取
- [ ] **没有 `$fromAI()`** 在代码体内部
- [ ] **没有 `$input` / `$json` / `$helpers`** —— 那些不在沙盒中
- [ ] **返回** 是一个字符串（使用 `JSON.stringify()` 返回结构化输出）
- [ ] **连接** 通过 `ai_tool` 连接到 AI 代理
- [ ] **测试** 使用 LLM 将发送的确切输入（JSON 在字符串中，或模式验证的对象）

---

## 额外资源

- [INPUT_SCHEMA.md](INPUT_SCHEMA.md) — 深入了解结构化输入（DynamicStructuredTool）
- [ERROR_PATTERNS.md](ERROR_PATTERNS.md) — 完整错误目录，包括原因和修复

### 官方来源
- [n8n Custom Code Tool 文档](https://docs.n8n.io/integrations/builtin/cluster-nodes/sub-nodes/n8n-nodes-langchain.toolcode/)
- [ToolCode 源代码](https://github.com/n8n-io/n8n/blob/master/packages/%40n8n/nodes-langchain/nodes/tools/ToolCode/ToolCode.node.ts) — 沙盒契约
- [LangChain 工具文档](https://js.langchain.com/docs/modules/agents/tools/) — DynamicTool / DynamicStructuredTool

---

**记住**：代码工具是一个穿着代码节点 UI 的 LangChain 工具。契约是：**字符串输入，字符串输出**。其他所有内容都由此衍生。
