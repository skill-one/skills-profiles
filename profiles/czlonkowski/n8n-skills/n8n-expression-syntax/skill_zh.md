# n8n 表达式语法

工作流中正确编写 n8n 表达式的专家指南。

---

## 表达式格式

n8n 中的所有动态内容都使用**双花括号**：

```
{{expression}}
```

**示例**：
```
✅ {{$json.email}}
✅ {{$json.body.name}}
✅ {{$node["HTTP Request"].json.data}}
❌ $json.email  (没有花括号 - 被视为纯文本)
❌ {$json.email}  (单花括号 - 无效)
```

---

## 核心变量

### $json - 当前节点输出

访问当前节点的数据：

```javascript
{{$json.fieldName}}
{{$json['field with spaces']}}
{{$json.nested.property}}
{{$json.items[0].name}}
```

### $node - 引用其他节点

访问任何先前节点的数据：

```javascript
{{$node["Node Name"].json.fieldName}}
{{$node["HTTP Request"].json.data}}
{{$node["Webhook"].json.body.email}}
```

**重要**：
- 节点名称**必须**用引号括起来
- 节点名称是**区分大小写的**
- 必须与工作流中的确切节点名称匹配

### $now - 当前时间戳

访问当前日期/时间：

```javascript
{{$now}}
{{$now.toFormat('yyyy-MM-dd')}}
{{$now.toFormat('HH:mm:ss')}}
{{$now.plus({days: 7})}}
```

### $env - 环境变量

访问环境变量：

```javascript
{{$env.API_KEY}}
{{$env.DATABASE_URL}}
```

**警告**：某些 n8n 实例启用了 `N8N_BLOCK_ENV_ACCESS_IN_NODE`，这将完全阻止 `$env` 访问。如果 `$env` 返回错误，请使用替代方法：
- 将值存储在凭证中
- 使用手动输入值的 Set 节点
- 通过 webhook 查询参数传递值

---

## 🚨 关键：Webhook 数据结构

**最常见的错误**：Webhook 数据**不在**根目录下！

### Webhook 节点输出结构

```javascript
{
  "headers": {...},
  "params": {...},
  "query": {...},
  "body": {           // ⚠️ 用户数据在这里！
    "name": "John",
    "email": "john@example.com",
    "message": "Hello"
  }
}
```

### 正确的 Webhook 数据访问

```javascript
❌ 错误: {{$json.name}}
❌ 错误: {{$json.email}}

✅ 正确: {{$json.body.name}}
✅ 正确: {{$json.body.email}}
✅ 正确: {{$json.body.message}}
```

**原因**：Webhook 节点将传入的数据包裹在 `.body` 属性下以保留 headers、params 和 query 参数。

---

## 常见模式

### 访问嵌套字段

```javascript
// 简单嵌套
{{$json.user.email}}

// 数组访问
{{$json.data[0].name}}
{{$json.items[0].id}}

// 方括号表示法用于空格
{{$json['field name']}}
{{$json['user data']['first name']}}
```

### 引用其他节点

```javascript
// 没有空格的节点
{{$node["Set"].json.value}}

// 带空格的节点（常见！）
{{$node["HTTP Request"].json.data}}
{{$node["Respond to Webhook"].json.message}}

// Webhook 节点
{{$node["Webhook"].json.body.email}}
```

### 组合变量

```javascript
// 连接（自动）
Hello {{$json.body.name}}!

// 在 URL 中
https://api.example.com/users/{{$json.body.user_id}}

// 在对象属性中
{
  "name": "={{$json.body.name}}",
  "email": "={{$json.body.email}}"
}
```

---

## 不应使用表达式的场景

### ❌ 代码节点

代码节点使用**直接的 JavaScript 访问**，而不是表达式！

```javascript
// ❌ 错误的代码节点
const email = '={{$json.email}}';
const name = '{{$json.body.name}}';

// ✅ 正确的代码节点
const email = $json.email;
const name = $json.body.name;

// 或使用代码节点 API
const email = $input.item.json.email;
const allItems = $input.all();
```

### ❌ Webhook 路径

```javascript
// ❌ 错误
path: "{{$json.user_id}}/webhook"

// ✅ 正确
path: "user-webhook"  // 仅静态路径
```

### ❌ 凭证字段

```javascript
// ❌ 错误
apiKey: "={{$env.API_KEY}}"

// ✅ 正确
使用 n8n 凭证系统，而不是表达式
```

---

## 转换门卫

在添加任何节点或编写任何代码以转换数据之前，请按以下顺序操作，并在第一个符合条件的节点处停止：

1. **表达式** (`{{ ... }}`) 在消费字段中。属性访问、方法链 (`.map().filter().join()`)、三元运算符、字符串构建、Luxon 日期数学——如果它是“取 A，生成 B”而不需要中间变量，则它是表达式。这涵盖了大多数“只需转换此内容”的情况。
   - **查询嵌套 JSON**（过滤数组、选择字段、求和、排序、展平）→ 在同一表达式中 `$jmespath()`，在您拆分为项目或链式 `.map().filter()` 之前。一个查询可以替代 Split Out → Filter → Aggregate 链。下文有规则。
2. **箭头函数 IIFE 在 Edit Fields 字段内**。当逻辑需要中间变量、分支或注释，但仍在单个项目上操作时，请将其包装在字段值中的立即调用箭头函数内：

   ```
   ={{ (() => {
       const items = $json.line_items;
       const subtotal = items.reduce((sum, it) => sum + it.price * it.qty, 0);
       const tax = subtotal * 0.08;
       return (subtotal + tax).toFixed(2);
   })() }}
   ```

   外部的 `(...)` 括号括起来函数；尾随的 `()` 调用它。删除任何一个，n8n 都会拒绝运行。在内部，您将获得完整的表达式范围 (`$json`、`$('Node')`、`$now`、Luxon) 以及 `const`/`let`、`if`/`switch`、`try`/`catch` 和 regex。没有 `require`，没有 `await`。
3. **代码节点——最后手段**。仅在您需要跨整个数据集进行多项目聚合、允许的库或异步工作时使用。

**为什么顺序很重要**。这不是风格——这是可读性和性能。代码节点在沙盒化的 VM 中运行，具有每次调用的设置和值序列化——一个冷启动成本可能达到 500–1000 毫秒，然后您的逻辑才会运行。（它在热启动、高项目数运行中摊销，因此将其视为常见情况成本，而不是通用常数。）相同的逻辑在表达式或 Edit Fields IIFE 中以单数字毫秒在进程中运行，并且完全跳过沙盒。对于纯单项目塑形来说，这是一个巨大的差距，没有功能差异，并且它在热路径（如每个请求的 webhook）上成倍增加。表达式也保留在它使用的字段中，而不是隐藏在必须打开上游节点才能理解的代码中。仅在输入或范围真正需要它时才跨越阶段。

## `$jmespath()` — 在一个表达式中查询嵌套 JSON

```
{{ $jmespath($json, "customers[?country=='PL' && revenue > `100000`].name") }}    →  ["Acme"]
```

在 n8n 2.38 上验证：这个表达式精确地返回了 Split Out → Filter → Aggregate 返回的内容，而没有额外的节点。语法是苛刻的，并且 **大多数错误会静默失败**：

| 写法 | 不是 | 错误形式会做什么 |
|---|---|---|
| `$jmespath(object, "query")`, object first | `$jmespath("query", object)` | 抛出 `expected two arguments (Object, string) for this function`（JMESPath 自己的文档显示 `search(query, data)`) |
| 字符串用单引号：`country=='PL'` | `country=="PL"` | 解析错误 → 整个表达式变为 `null`（见调试） |
| 数字/布尔值用反引号：`` revenue > `100000` `` | `revenue > 100000` | 解析错误 → 整个表达式变为 `null`（见调试） |
| `&&` `\|\|` `!` `==` | `and` `or` `=` | 解析错误 → `null` |
| 带空格的键用引号：`'customers[*].contact."first-name"'`（用单引号括住 JS 字符串） | `contact.first-name` | 解析错误 → `null` |
| 遍历项目时保留包装器：`$jmespath($('Node').all(), "[?json.country=='PL'].json.name")` 或 `$jmespath($input.all().map(i => i.json), "[?country=='PL'].name")` | `"[?country=='PL'].name"` 在 `.all()` 上 | 项目是 `{json: …}` 包装器 → `[]` |

- **结果**：缺少路径或索引 → `null`；过滤后没有匹配项 → `[]`；`sum()` 对空投影 → `0`。
- **第一个参数必须是对象或数组**。字符串（例如具有文本响应的 HTTP 请求）或 `undefined` (`$json.missingField`) 会抛出相同的 `expected two arguments` 错误。那个会失败节点。
- **有用的片段**：`length()`、`sum()`、`max_by(arr, &field)`、`sort_by(arr, &field)`、`reverse()`、`contains()`、`starts_with()`、`keys()`、`to_number()`；投影 `[*]`、展平 `[]`、管道 `| [0]`、重塑 `{name: name, email: contact.email}`。
- **它返回值，而不是项目**。使用它将结果传递给一个字段（消息文本、HTTP 正文、IF/Filter 条件）。当下游需要每个匹配项一个项目时，请使用 Edit Fields 中的 `$jmespath` 进行缩小，并随后对该字段进行一个 Split Out。
- **它存在于**表达式和 JavaScript 代码节点中（相同的参数顺序）。不在原生 Python 代码节点中。

## Set 节点的反模式与分支汇聚

### 删除只向一个消费者提供值的 Set 节点

一个 Set / Edit Fields 节点，其唯一工作是为**一个**下游节点提取值并传递给它，是冗余的。在消费者处内联其表达式。

```
❌  Webhook → Set { customer_id: {{ $json.body.customer_id }} } → Postgres: WHERE id = {{ $json.customer_id }}

✅  Webhook → Postgres: WHERE id = {{ $('Webhook').item.json.body.customer_id }}
```

Set 节点增加了跳转、画布杂乱和重构风险，而消费者本身可以完成它所做的一切。要使用 `n8n_update_partial_workflow` 干净地删除它：重新连接连接（从 Set 的源和目标删除 `removeConnection`，从源直接到消费者添加 `addConnection`），`patchNodeField` 消费者的表达式以通过节点名称引用原始源，然后 `removeNode` Set。

**快速测试**：计算每个 Set 产生的字段有多少个下游节点引用。
- **0 或 1** → 删除，在消费者处内联。
- **2+** → 它可能值得保留。

**合法例外**——当您需要保留 Set 时：
- **2+ 消费者**读取相同的派生值，并且派生是非平凡的（名称有助于可读性，并且您只计算一次）。
- **它是子工作流的最终 Return 节点**，塑造输出契约。在这里，“单个消费者”是每个调用者，因此 Set *是* API 边界——并且带有 `Include Other Fields: false` 它白名单了输出形状，因此内部临时字段不会泄漏。
- **您正在重命名或白名单字段**，并且希望在一个地方而不是跨消费者表达式显示它。

### 分支汇聚：用 NoOp 锚定

当分支汇聚（IF/Switch/Merge 之后）时，`$json` 变为“最后一个触发的分支”——非确定性，并且是错误的数据的无声来源。在汇聚处插入一个**NoOp** 节点，并为其提供描述性名称（`Combine Inputs`），下游节点通过名称引用它：

```
分支 A ──┐
           ├─→ [NoOp: Combine Inputs] ──→ 下游使用 $('Combine Inputs').item.json.x
分支 B ──┘
```

NoOp 在重构中幸存：在它和消费者之间插入转换不会破坏 `$('Combine Inputs')` 引用。（如果分支产生 *不同* 的形状，请使用 Set 节点而不是 NoOp 来将两者归一化为一个形状——见上面的例外。）

更广泛地说，在分支式流程中，**优先使用 `$('Node').item.json.x` 而不是深度 `$json.x`**。`$json` 在插入中间节点或节点清除项目上下文（Aggregate、Code 与 Run for All、分支合并）时中断；失败是静默的，下游获得错误数据而没有错误。节点名称引用无论源和消费者之间有什么，都是明确的。

---

## 验证规则

### 1. 始终使用 {{}}

表达式**必须**用双花括号括起来。

```javascript
❌ $json.field
✅ {{$json.field}}
```

### 2. 使用引号处理空格和特殊字符

带有空格、变音符号或特殊字符的字段或节点名称需要**方括号表示法**：

```javascript
❌ {{$json.field name}}
✅ {{$json['field name']}}

❌ {{$node.HTTP Request.json}}
✅ {{$node["HTTP Request"].json}}

// 方括号表示法对于带有特殊字符的键是强制性的
✅ {{$json['Gross Price w/o shipment']}}
✅ {{$json['Cena brutto zł']}}
```

### 3. 匹配确切的节点名称

节点引用是**区分大小写的**：

```javascript
❌ {{$node["http request"].json}}  // 小写
❌ {{$node["Http Request"].json}}  // 错误的大小写
✅ {{$node["HTTP Request"].json}}  // 精确匹配
```

### 4. 不嵌套 {{}}

不要双重包装表达式：

```javascript
❌ {{{$json.field}}}
✅ {{$json.field}}
```

---

## 常见错误

对于完整的错误目录和修复，请参阅 [COMMON_MISTAKES.md](COMMON_MISTAKES.md)

### 快速修复

| 错误 | 修复 |
|---------|-----|
| `$json.field` | `{{$json.field}}` |
| `{{$json.field name}}` | `{{$json['field name']}}` |
| `{{$node.HTTP Request}}` | `{{$node["HTTP Request"]}}` |
| `{{{$json.field}}}` | `{{$json.field}}` |
| `{{$json.name}}` (webhook) | `{{$json.body.name}}` |
| `'={{$json.email}}'` (Code node) | `$json.email` |

---

## 工作示例

有关真实工作流示例，请参阅 [EXAMPLES.md](EXAMPLES.md)

### 示例 1：Webhook 到 Slack

**Webhook 接收**：
```json
{
  "body": {
    "name": "John Doe",
    "email": "john@example.com",
    "message": "Hello!"
  }
}
```

**在 Slack 节点文本字段中**：
```
New form submission!

Name: {{$json.body.name}}
Email: {{$json.body.email}}
Message: {{$json.body.message}}
```

### 示例 2：HTTP 请求到 Email

**HTTP 请求返回**：
```json
{
  "data": {
    "items": [
      {"name": "Product 1", "price": 29.99}
    ]
  }
}
```

**在 Email 节点**（引用 HTTP 请求）：
```
Product: {{$node["HTTP Request"].json.data.items[0].name}}
Price: ${{$node["HTTP Request"].json.data.items[0].price}}
```

### 示例 3：格式化时间戳

```javascript
// 当前日期
{{$now.toFormat('yyyy-MM-dd')}}
// 结果：2025-10-20

// 时间
{{$now.toFormat('HH:mm:ss')}}
// 结果：14:30:45

// 完整日期时间
{{$now.toFormat('yyyy-MM-dd HH:mm')}}
// 结果：2025-10-20 14:30
```

---

## 数据类型处理

### 数组

```javascript
// 第一个项目
{{$json.users[0].email}}

// 数组长度
{{$json.users.length}}

// 最后一个项目
{{$json.users[$json.users.length - 1].name}}
```

### 对象

```javascript
// 点表示法（无空格）
{{$json.user.email}}

// 方括号表示法（带空格或动态）
{{$json['user data'].email}}
```

### 字符串

```javascript
// 连接（自动）
Hello {{$json.name}}!

// 字符串方法
{{$json.email.toLowerCase()}}
{{$json.name.toUpperCase()}}
```

### 数字

```javascript
// 直接使用
{{$json.price}}

// 数学运算
{{$json.price * 1.1}}  // 增加 10%
{{$json.quantity + 5}}
```

---

## 高级模式

### 条件内容

```javascript
// 三元运算符
{{$json.status === 'active' ? 'Active User' : 'Inactive User'}}

// 默认值
{{$json.email || 'no-email@example.com'}}
```

### 日期操作

```javascript
// 增加天数
{{$now.plus({days: 7}).toFormat('yyyy-MM-dd')}}

// 减去小时
{{$now.minus({hours: 24}).toISO()}}

// 设置特定日期
{{DateTime.fromISO('2025-12-25').toFormat('MMMM dd, yyyy')}}
```

### 字符串操作

```javascript
// 子字符串
{{$json.email.substring(0, 5)}}

// 替换
{{$json.message.replace('old', 'new')}}

// 分割和连接
{{$json.tags.split(',').join(', ')}}
```

---

## 性能：表达式复杂性几乎免费

一个常见的担忧是复杂的 `{{ }}` 慢。它不慢——成本在于 n8n 评估表达式*的次数*，而不是每个表达式的复杂性。

在 n8n 2.x 实例上测量，复杂的表达式（`sqrt`、`split`、`reduce`、算术）每个项目与简单的 `{{ $json.x > 50 }}` 成本相同——大约 **~0.2 ms/item** 无论是哪种方式，因为 ~90% 的成本是 n8n 构建每个项目的评估上下文，而不是运行您的表达式。

这意味着在实践中：

- **不要因为“速度”而将一个工作表达式拆分为一系列节点**。每个额外节点都会重新评估每个项目并重新复制所有项目；一个节点上的一个更丰富的表达式比三个节点上的简单表达式更好。
- **表达式 (~0.2 ms/item) 比代码节点在“为每个项目运行一次”模式下便宜 3 倍** (~0.6 ms/item) 用于相同的每个项目检查——但代码节点在“为所有项目运行一次”模式下仍然更便宜 (~0.02 ms/item)，因为它跨每个项目边界只跨越一次而不是 N 次。
- 这仅在 **数千个项目** 时才会影响；低于此它是亚 100 ms。**n8n 代码 JavaScript** 技能具有完整的每个项目边界模型。

---

## 调试表达式

### 运行时错误不会失败节点——它们会变成 `null`

在 n8n 2.38 上使用默认表达式运行时验证：在每个 `{{ }}` 周围的处理器中，在执行期间，它只重新抛出 n8n 自己的 `ExpressionError` 并吸收其他 JavaScript 错误，因此字段解析为空/`null`，节点仍然报告 **成功**。`$json.missing.field` (TypeError)、`JSON.parse('{bad')`、`throw new Error(...)` 和 JMESPath 语法错误都产生了 `null`。在 Filter 或 IF 条件中，每个项目都静默地失败了检查。在其他人版本或表达式引擎上，相同的错误可能会失败节点。无论如何，永远不要单独信任绿色的运行。

这不是避免表达式的原因（代码节点也有自己的静默陷阱）。这是**测试真实项目**的原因：

- 检查表达式编辑器预览与真实数据。预览*确实*显示错误。
- 在测试运行后，查看输出值。您期望数据的地方 `null` 是症状。`validate_workflow` 和绿色执行不会告诉您。
- 要暴露真实消息，暂时将表达式包装起来：
  `{{ (() => { try { return JSON.stringify(<expr>) } catch (e) { return 'ERROR: ' + e.message } })() }}`
- n8n 自己的错误仍然会失败节点（例如 `$jmespath` 给非对象参数）。

### 在表达式编辑器中测试

1. 点击带有表达式的字段
2. 打开表达式编辑器（点击“fx”图标）
3. 查看结果的实时预览
4. 检查红色突出显示的错误

### 常见错误消息

这些出现在编辑器预览中；在运行时，它们中的大多数都会解析为 `null`（见上文）。

**"Cannot read property 'X' of undefined"**
→ 父对象不存在
→ 检查您的数据路径

**"X is not a function"**
→ 尝试在非函数上调用方法
→ 检查变量类型

**表达式显示为字面文本**
→ 缺少 {{ }}
→ 添加花括号

---

## 表达式辅助工具

### 可用方法

**字符串**:
- `.toLowerCase()`, `.toUpperCase()`
- `.trim()`, `.replace()`, `.substring()`
- `.split()`, `.includes()`

**数组**:
- `.length`, `.map()`, `.filter()`
- `.find()`, `.join()`, `.slice()`

**DateTime** (Luxon):
- `.toFormat()`, `.toISO()`, `.toLocal()`
- `.plus()`, `.minus()`, `.set()`

**数字**:
- `.toFixed()`, `.toString()`
- 数学运算：`+`, `-`, `*`, `/`, `%`

**JSON 查询**:
- `$jmespath(object, "query")`: 过滤/选择/聚合嵌套 JSON（见 `$jmespath()` 部分关于引号规则）

---

## 最佳实践

### ✅ 做

- 始终使用 {{ }} 用于动态内容
- 使用方括号表示法处理带空格的字段名
- 从 `.body` 引用 webhook 数据
- 使用 $node 引用其他节点的数据
- 在表达式编辑器中测试表达式

### ❌ 不要

- 不要在代码节点中使用表达式
- 不要忘记用引号括起带空格的节点名
- 不要双重包装 `{{ }}`
- 不要假设 webhook 数据在根目录下（它在 `.body` 下！）
- 不要在 webhook 路径或凭证中使用表达式

---

## 相关技能

- **n8n MCP 工具专家**：学习如何使用 MCP 工具验证表达式
- **n8n 工作流模式**：查看表达式在真实工作流示例中的使用
- **n8n 节点配置**：了解何时需要表达式

---

## 总结

**基本规则**：
1. 用 {{ }} 括起表达式
2. Webhook 数据在 `.body` 下
3. 代码节点中不要用 {{ }}
4. 带空格的节点名用引号
5. 节点名区分大小写
6. `{{ }}` 中的运行时错误会静默地变为 `null`。在测试运行后检查输出值
7. `$jmespath(object, "query")`: `'string'`, `` `number` ``, `"field"`；`json.` 前缀优于 `.all()`

**最常见的错误**：
- 缺少 {{ }} → 添加花括号
- `{{$json.name}}` (webhooks) → 使用 `{{$json.body.name}}`
- `{{$json.email}}` (Code) → 使用 `$json.email`
- `{{$node.HTTP Request}}` → 使用 `{{$node["HTTP Request"]}}`

更多详情，请参阅：
- [COMMON_MISTAKES.md](COMMON_MISTAKES.md) - 完整错误目录
- [EXAMPLES.md](EXAMPLES.md) - 真实工作流示例

---

**需要帮助？** 参考 n8n 表达式文档或使用 n8n-mcp 验证工具检查您的表达式。
