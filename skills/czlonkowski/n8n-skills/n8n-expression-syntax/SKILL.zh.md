---
name: n8n-expression-syntax
description: 验证n8n表达式语法并修复常见错误。在编写n8n表达式、使用{{}}语法、访问$json/$node变量、排查表达式错误、在节点间映射数据或在工作流中引用webhook数据时使用。每当配置引用前序节点数据的节点字段时，都要使用此技能——表达式是n8n在节点间传递数据的方式，语法错误是工作流中最常见的错误来源。此外，在询问复杂表达式是否影响性能时也使用。
---

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
❌ $json.email  （没有花括号 - 被视为普通文本）
❌ {$json.email}  （单花括号 - 无效）
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
- 必须与工作流中的节点名称完全匹配

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

**最常见的错误**：Webhook 数据**不在**根目录！

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

// 方括号表示法（用于空格）
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
path: "user-webhook"  // 仅支持静态路径
```

### ❌ 凭证字段

```javascript
// ❌ 错误
apiKey: "={{$env.API_KEY}}"

// ✅ 正确
使用 n8n 凭证系统，而不是表达式
```

---

## 转换守门人

在添加任何节点或编写任何代码以转换数据之前，请按以下顺序操作，并在第一个符合的节点停止：

1. **表达式** (`{{ ... }}`) 在消费字段中。属性访问、方法链（`.map().filter().join()`）、三元运算符、字符串构建、Luxon 日期数学——如果它是“取 A，生成 B”而不需要中间变量，则它是表达式。这涵盖了大多数“只需转换此内容”的情况。
   - **查询嵌套 JSON**（过滤数组、选择字段、求和、排序、展平）→ 在同一表达式中 `$jmespath()`，在拆分项目或链式 `.map().filter()` 之前。一个查询可以替代 Split Out → Filter → Aggregate 链。下文规则。
2. **Edit Fields 字段的箭头函数 IIFE**。当逻辑需要中间变量、分支或注释，但仍然作用于单个项目时，在字段值中将其包装在立即调用的箭头函数中：

   ```
   ={{ (() => {
       const items = $json.line_items;
       const subtotal = items.reduce((sum, it) => sum + it.price * it.qty, 0);
       const tax = subtotal * 0.08;
       return (subtotal + tax).toFixed(2);
   })() }}
   ```

   外部的 `(...)` 括号括住函数，尾随的 `()` 调用它。删除任何一个，n8n 都会拒绝执行。在内部，你获得完整的表达式作用域（`$json`、`$('Node')`、`$now`、Luxon）以及 `const`/`let`、`if`/`switch`、`try`/`catch` 和正则表达式。没有 `require`，没有 `await`。
3. **代码节点——最后手段**。仅在需要跨整个数据集进行多项目聚合（`$input.all()`）、允许的库或异步工作时使用。

**为什么顺序很重要**。这不是风格——这是可读性和性能。代码节点在沙盒化的 VM 中运行，具有每次调用的设置和值序列化——冷启动成本可能达到 500–1000ms 才能运行你的逻辑。（它在热启动、高项目数运行中摊销，所以将其视为常见情况成本，而不是通用常数。）相同的逻辑在表达式或 Edit Fields IIFE 中运行在进程中，以个位数毫秒运行，并且完全跳过沙盒。对于纯单项目塑形来说，这是一个巨大的差距，没有功能差异，并且在高路径（如每个请求的 webhook）上会成倍增加。表达式也保留在它使用的字段中，而不是隐藏在需要打开上游节点才能理解的节点中。仅在输入或范围真正需要时才进入下一阶段。

## `$jmespath()` —— 在一个表达式中查询嵌套 JSON

```
{{ $jmespath($json, "customers[?country=='PL' && revenue > `100000`].name") }}    →  ["Acme"]
```

在 n8n 2.38 上验证：这个表达式返回与 Split Out → Filter → Aggregate 相同的结果，无需额外节点。语法不容忍错误，并且**大多数错误会静默失败**：

| 写法 | 不 | 错误形式的作用 |
|---|---|---|
| `$jmespath(object, "query")`, object first | `$jmespath("query", object)` | 抛出 `expected two arguments (Object, string) for this function`（JMESPath 自己的文档显示 `search(query, data)`) |
| 字符串单引号：`country=='PL'` | `country=="PL"` | 解析错误 → 整个表达式变为 `null`（见调试） |
| 数字/布尔值反引号：`` revenue > `100000` `` | `revenue > 100000` | 解析错误 → 整个表达式变为 `null`（见调试） |
| `&&` `\|\|` `!` `==` | `and` `or` `=` | 解析错误 → `null` |
| 带特殊字符的键引号：`'customers[*].contact."first-name"'`（单引号 JS 字符串） | `contact.first-name` | 解析错误 → `null` |
| 对项目进行操作，保留包装：`$jmespath($('Node').all(), "[?json.country=='PL'].json.name")` 或 `$jmespath($input.all().map(i => i.json), "[?country=='PL'].name")` | `"[?country=='PL'].name"` on `.all()` | 项目是 `{json: …}` 包装 → `[]` |

- **结果**：缺失路径或索引 → `null`；过滤无匹配 → `[]`；`sum()` 对空投影 → `0`。
- **第一个参数必须是对象或数组**。字符串（例如带有文本响应的 HTTP Request）或 `undefined`（`$json.missingField`）会抛出相同的 `expected two arguments` 错误。那个会失败节点。
- **方便的部分**：`length()`、`sum()`、`max_by(arr, &field)`、`sort_by(arr, &field)`、`reverse()`、`contains()`、`starts_with()`、`keys()`、`to_number()`；投影 `[*]`、展平 `[]`、管道 `| [0]`、重塑 `{name: name, email: contact.email}`。
- **它返回值，而不是项目**。用于结果作为单个字段（消息文本、HTTP body、IF/Filter 条件）。当下游需要每个匹配一个项目时，使用 Edit Fields 中的 `$jmespath` 窄化，然后对那个字段进行单个 Split Out。
- **存在位置**：表达式和 JavaScript 代码节点（相同的参数顺序）。不在原生 Python 代码节点中。

## Set 节点的反模式与分支汇聚

### 删除只向一个消费者提供值的 Set 节点

只负责提取值并将其传递给**一个**下游节点的 Set / Edit Fields 节点是冗余的。在消费者处内联其表达式。

```
❌  Webhook → Set { customer_id: {{ $json.body.customer_id }} } → Postgres: WHERE id = {{ $json.customer_id }}

✅  Webhook → Postgres: WHERE id = {{ $('Webhook').item.json.body.customer_id }}
```

Set 节点增加了跳转、画布杂乱和重构风险，而消费者本身可以完成它所做的任何事情。使用 `n8n_update_partial_workflow` 干净地删除它：重新连接连接（从 Set 的源和目标删除 `removeConnection`，从源直接到消费者添加 `addConnection`），`patchNodeField` 消费者的表达式以通过节点名称引用原始源，然后 `removeNode` Set。

**快速测试**：计算每个 Set 产生的字段有多少个下游节点引用。
- **0 或 1** → 删除，在消费者处内联。
- **2+** → 它可能值得保留。

**合法例外**——当您保留 Set 时：
- **2+ 消费者**读取相同的派生值，并且派生是非平凡的（名称有助于可读性，并且您一次计算它）。
- **它是子工作流的最终 Return 节点**，塑造输出契约。在这里，“单个消费者”是每个调用者，所以 Set *是* API 边界——并且带有 `Include Other Fields: false` 它白名单了输出形状，所以内部临时字段不会泄漏。
- **您正在重命名或白名单字段**，并且希望在某个地方而不是跨消费者表达式显示它。

### 分支汇聚：使用 NoOp 锚定

当分支汇聚（IF/Switch/Merge 之后）时，`$json` 变为“最后一个触发的分支”——非确定性，并且是错误的数据的无声来源。在汇聚处插入一个**NoOp** 节点，并具有描述性名称（`Combine Inputs`），下游节点通过名称引用它：

```
分支 A ──┐
           ├─→ [NoOp: Combine Inputs] ──→ 下游使用 $('Combine Inputs').item.json.x
分支 B ──┘
```

NoOp 在重构中幸存：在它和消费者之间插入转换不会破坏 `$('Combine Inputs')` 引用。（如果分支产生*不同*的形状，使用 Set 节点而不是 NoOp 来将两者归一化为一个形状——见上面的例外。）

更广泛地说，在分支式流程中，**优先使用 `$('Node').item.json.x` 而不是深度 `$json.x`**。`$json` 在插入中间节点或节点清除项目上下文（Aggregate、带有 Run for All 的 Code、分支合并）时就会中断；失败是静默的，下游会得到错误的数据而没有错误。节点名称引用无论源和消费者之间有什么，都是明确的。

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

有关完整错误目录和修复，请参阅 [COMMON_MISTAKES.md](COMMON_MISTAKES.md)

### 快速修复

| 错误 | 修复 |
|---------|-----|
| `$json.field` | `{{$json.field}}` |
| `{{$json.field name}}` | `{{$json['field name']}}` |
| `{{$node.HTTP Request}}` | `{{$node["HTTP Request"]}}` |
| `{{{$json.field}}}` | `{{$json.field}}` |
| `{{$json.name}}`（webhook） | `{{$json.body.name}}` |
| `'={{$json.email}}'`（代码节点） | `$json.email` |

---

## 实际示例

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

### 示例 2：HTTP Request 到 Email

**HTTP Request 返回**：
```json
{
  "data": {
    "items": [
      {"name": "Product 1", "price": 29.99}
    ]
  }
}
```

**在 Email 节点**（引用 HTTP Request）：
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

一个常见的担忧是复杂的 `{{ }}` 慢。它不慢——成本是 n8n 评估表达式*次数*，而不是每个表达式的复杂性。

在 n8n 2.x 实例上测量，复杂的表达式（`sqrt`、`split`、`reduce`、算术）与简单的 `{{ $json.x > 50 }}` 每项目成本相同——大约 **~0.2 ms/item**，因为 ~90% 是 n8n 构建每个项目的评估上下文，而不是运行你的表达式。

这意味着在实践中：

- **不要为了“速度”将工作表达式拆分为节点链**。每个额外的节点都会对每个项目重新评估并重新复制所有项目；一个节点包含一个更丰富的表达式胜过三个简单的节点。
- **在“为每个项目运行一次”模式下，表达式（约0.2毫秒/项目）比“运行一次代码节点”（约0.6毫秒/项目）便宜约3倍**，用于相同的每项检查——但“为所有项目运行一次”模式下的代码节点仍然更便宜（约0.02毫秒/项目），因为它只跨越一次每项边界，而不是N次。
- 这只在**数千个项目**时才会出现问题；低于这个数量级它就是低于100毫秒。**n8n Code JavaScript**技能具有完整的每项边界模型。

---

## 表达式调试

### 运行时错误不会导致节点失败——它们会变成`null`

在n8n 2.38的默认表达式运行时上已验证：在执行期间，围绕每个`{{ }}`的处理程序只重新抛出n8n自己的`ExpressionError`并吞噬其他JavaScript错误，因此字段解析为空/`null`，节点仍然报告**成功**。`$json.missing.field`（TypeError）、`JSON.parse('{bad')`、`throw new Error(...)`和JMESPath语法错误都产生了`null`。在Filter或IF条件中，每个项目都会无声地失败检查。在其他版本或表达式引擎上，同样的错误可能会导致节点失败。无论如何，永远不要单独相信绿色的运行。

这不是避免表达式的理由（代码节点也有它自己的无声陷阱）。这是一个**使用真实项目进行测试**的理由：

- 将表达式编辑器预览与真实数据进行比较。预览*确实*显示了错误。
- 测试运行后，查看输出值。你期望数据的地方出现`null`是症状。`validate_workflow`和绿色的执行不会告诉你。
- 要显示真实消息，暂时包装表达式：
  `{{ (() => { try { return JSON.stringify(<expr>) } catch (e) { return 'ERROR: ' + e.message } })() }}`
- n8n自己的错误仍然会导致节点失败（例如，给`$jmespath`传递非对象参数）。

### 在表达式编辑器中测试

1. 点击带有表达式的字段
2. 打开表达式编辑器（点击“fx”图标）
3. 查看结果的实时预览
4. 检查红色突出显示的错误

### 常见错误消息

这些出现在编辑器预览中；在运行时，其中大多数会解析为`null`（见上文）。

**“Cannot read property 'X' of undefined”**
→ 父对象不存在
→ 检查你的数据路径

**“X is not a function”**
→ 尝试在非函数上调用方法
→ 检查变量类型

**表达式显示为纯文本**
→ 缺少{{ }}
→ 添加花括号

---

## 表达式辅助工具

### 可用方法

**String**:
- `.toLowerCase()`, `.toUpperCase()`
- `.trim()`, `.replace()`, `.substring()`
- `.split()`, `.includes()`

**Array**:
- `.length`, `.map()`, `.filter()`
- `.find()`, `.join()`, `.slice()`

**DateTime**（Luxon）:
- `.toFormat()`, `.toISO()`, `.toLocal()`
- `.plus()`, `.minus()`, `.set()`

**Number**:
- `.toFixed()`, `.toString()`
- 数学运算：`+`, `-`, `*`, `/`, `%`

**JSON查询**:
- `$jmespath(object, "query")`: 过滤/选择/聚合嵌套JSON（请参阅`$jmespath()`部分以了解引号规则）

---

## 最佳实践

### ✅ 做

- 总是使用{{ }}用于动态内容
- 使用方括号表示名称带空格的字段
- 从`.body`引用webhook数据
- 使用$node引用其他节点的数据
- 在表达式编辑器中测试表达式

### ❌ 不要

- 不要在代码节点中使用表达式
- 不要忘记带空格的节点名称周围的引号
- 不要用额外的{{ }}双层包装
- 不要假设webhook数据在根目录下（它在`.body`下！）
- 不要在webhook路径或凭证中使用表达式

---

## 相关技能

- **n8n MCP Tools Expert**：学习如何使用MCP工具验证表达式
- **n8n Workflow Patterns**：查看真实工作流示例中的表达式
- **n8n Node Configuration**：了解何时需要表达式

---

## 总结

**基本规则**：
1. 用{{ }}包装表达式
2. Webhook数据在`.body`下
3. 代码节点中不要有{{ }}
4. 带空格的节点名称要加引号
5. 节点名称区分大小写
6. `{{ }}`内的运行时错误会无声地变成`null`。测试运行后检查输出值
7. `$jmespath(object, "query")`: `'string'`, `` `number` ``, `"field"`；`json.`前缀优于`.all()`

**最常见错误**：
- 缺少{{ }} → 添加花括号
- `{{$json.name}}`在webhooks中 → 使用`{{$json.body.name}}`
- `{{$json.email}}`在代码中 → 使用`$json.email`
- `{{$node.HTTP Request}}` → 使用`{{$node["HTTP Request"]}}`

更多详情，请参阅：
- [COMMON_MISTAKES.md](COMMON_MISTAKES.md) - 完整错误目录
- [EXAMPLES.md](EXAMPLES.md) - 真实工作流示例

---

**需要帮助？** 参考 n8n 表达式文档或使用 n8n-mcp 验证工具检查你的表达式。
