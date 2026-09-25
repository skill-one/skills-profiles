# n8n 表达式

n8n 的表达式语言是嵌入在 `{{...}}` 块中的 JavaScript。它们同步运行，每次处理一个项目 (`$json`)，可以访问上游节点 (`$('Name')`)、使用 Luxon 处理日期，以及使用大部分原生 JS 功能。

## 必须遵守的规则

**通过节点名称引用数据，而不是 `$json`。** 使用 `$('Node Name').item.json.field`（或 `.first().json.field`）。`$json` 可以工作，但在任何节点清除项目上下文（聚合、用于所有代码的代码节点、分支合并）或重构添加中间节点时都会失效。失败时没有错误提示，下游会接收到错误的数据。通过节点名称的引用是稳定的。

## 强制默认值

- **不要创建仅用于向单个下游字段提供数据的 Set 节点。** 在消费者处内联表达式。当 2 个或更多消费者读取相同的派生值、派生过程不简单，或者 Set 是子工作流的最终返回形状时，Set 才有其存在的意义。见下文的 "Set 节点反模式"。
- **使用 Luxon 处理日期，而不是 DateTime 节点。** 日期计算、格式化和解析都在表达式中工作：`{{ DateTime.now().minus({ days: 7 }).toISO() }}`。DateTime 节点在画布上对初学者用户更明显，但除非用户明确要求，否则避免使用它。
- **通常在额外节点上进行表达式处理。** 在邮件节点的 body 字段中构建邮件正文，并在 HTTP 请求的 URL 字段中计算 URL。当转换被重用或一个部分的*主要目的*是转换时，再考虑使用额外节点。
- **多行表达式需要缩进和注释。** 当表达式跨越多行时，像真实代码一样格式化它。大多数 n8n 用户不是程序员，因此用简洁的内联注释解释代码。

## 为什么通过节点名称 (`$('Name').item.json.x`) 引用比 `$json.x` 更好

`$json` 意味着“当前流入此节点的项目。” 当节点直接位于一个源下游，并且没有清除项目上下文时（某些节点会清除：聚合、用于所有代码的代码节点、分支合并），这是可以的。

它会在以下情况下失效：

- 你在源和消费者之间插入了一个节点（消费者原本从 3 步前的节点读取 `$json.x`，现在新的中间节点变成了 `$json` 指向的对象）。
- 节点清除了上下文（聚合、某些合并、不保留形状的代码节点）。
- 分支通过合并汇聚。`$json` 是最后触发的分支，而不是确定性的。

`$('Get User').item.json.id` 是明确的。始终是命名节点的第一个项目 JSON，无论中间有什么。

**例外情况使规则成立：**

当分支汇聚并且你需要一个稳定的参考点时，**在汇聚处插入一个 NoOp 节点**。描述性地命名它（例如，`Combine Inputs`）。下游节点通过名称引用它。

```
分支 A ──┐
        ├─→ [NoOp: Combine Inputs] ──→ 下游节点使用 $('Combine Inputs').item.json.x
分支 B ──┘
```

NoOp 在重构中生存：在 Combine Inputs 和消费者之间插入转换不会破坏 `$('Combine Inputs')` 引用。

当下游节点需要来自其上下文被中间操作清除的节点的数据时，此模式是**必需的**。

**如果分支产生不同的形状，则使用 Set 节点而不是 NoOp。** NoOp 传递任何到达的形状，因此下游仍然必须知道哪个分支被触发。Set 节点将两个分支归一化为一个形状，下游读取一组字段：

```ts
// Set 节点："Normalize Inputs"
name: `={{ $('Lookup by Email').item.json.name || $('Lookup by ID').item.json.full_name }}`
email: `={{ $('Lookup by Email').item.json.email || $('Lookup by ID').item.json.contact_email }}`
```

下游节点引用 `$('Normalize Inputs').item.json.name`，无论哪个分支生成它。

## Set 节点反模式

AI 代理经常产生的模式：

```
Webhook → Set: { customer_id: $json.body.customer_id, amount: $json.body.amount }
       → Postgres: WHERE id = {{ $json.customer_id }}
       → Email: Total is {{ $json.amount }}
```

Set 节点没有做任何有用的事情。每个下游节点都可以直接从 webhook 读取：

```
Webhook → Postgres: WHERE id = {{ $('Webhook').item.json.body.customer_id }}
       → Email: Total is {{ $('Webhook').item.json.body.amount }}
```

只有以下情况 Set 节点才值得存在：

- 相同的派生值被**多个下游消费者**使用（派生过程不简单）。
- 派生过程逻辑复杂，名称有助于可读性。
- 多个分支需要相同的形状，共享上游引用更干净。
- **它是子工作流的最后一个节点，塑造返回契约。** 明确例外：当“单个消费者”是每个调用者时，Set 是 API 边界。可选但鼓励用于子工作流，有时在先前的节点携带噪声字段时是必需的。见 `n8n-subworkflows-official`。
- **你需要通过设置 `Include Other Fields: false` 来删除项目中的字段。** Set 是以白名单输出形状的最干净方式。这是上述子工作流返回形状机制背后的底层机制（防止内部临时字段泄漏给调用者），但它适用于任何需要下游干净形状的地方。
- **你需要重命名字段。** Set 将重命名显式地保留在一个地方，而不是分散在所有消费者表达式中。

对于“从请求正文中提取一个字段并使用一次”，**不需要** Set 节点。表达式放在消费字段中。

对于“一次提取多次用于下游使用”，Set 节点是合法的。如果只有一个消费者使用它，Set 就是债务（上述返回形状情况除外）。

### 判断是否需要 Set 节点的快速测试

下游节点引用每个字段的数量是多少？

- **0 或 1** → 删除，内联表达式。
- **2+** → 可能值得存在，尤其是当派生过程不简单时。

连续多个 Set 节点几乎肯定是过度提取。合并。

## 表达式能做什么

### 单字段转换

```ts
{{ $json.name.toUpperCase() }}
{{ $json.email.toLowerCase().trim() }}
{{ $json.items.length }}
{{ $json.user.first_name + ' ' + $json.user.last_name }}
{{ `(${$json.user.phone.slice(0, 3)}) ${$json.user.phone.slice(3, 6)}-${$json.user.phone.slice(6, 10)}` }}
```

### 方法链：`.map()`、`.filter()`、`.find()`、`.reduce()`

数组方法是表达式中最有用的工具之一。它们可以替代几十个节点。

```ts
{{ $json.tags.filter(tag => tag.active).map(tag => tag.name).join(', ') }}
{{ Object.values($json.scores).reduce((sum, score) => sum + score, 0) }}

// 从另一个节点的输出中查找一个匹配项
{{ $('Get Models').all().find(model => model.json.id === $json.modelId).json.modelName }}

// 过滤数组，然后检查形状
{{
  $('Get User\'s Entries').all()
    .map(item => item.json)
    .filter(entry => entry.prize_eligible === 'eligible')
    .length > 0
}}
```

#### 始终缩进多步链并添加注释

当链有 2 个或更多方法调用或过滤逻辑不明显时，跨行格式化并添加注释。读者可能不是作者，因此注释使非技术人员也能理解意图。

```ts
{{
  // 查找所有 1 小时后仍在处理的条目
  // （用于允许重新提交，因为可能出了问题）
  $('Get User\'s Entries').all()
    .map(item => item.json)
    .filter(entry =>
      entry.prize_eligible === 'processing' &&
      $now.diffTo(entry.created_at, 'minutes') > 60
    )
    .length > 0
}}
```

这种逻辑在路由节点（Switch、IF）中很常见。未注释的，对大多数用户来说难以阅读。

#### `.all().map()` 触发“执行一次”问题

当你使用 `$('Source Node').all().map(...)`（或 `.filter()`、`.reduce()`）来处理整个数据集时，**表达式本身会迭代**。如果节点具有默认的每个项目执行模式，它会对每个输入项目运行一次，但每次运行都会执行完整的 `.all()` 聚合：浪费工作，并且可能错误。

**当表达式使用 `.all().map()` / `.all().filter()` / `.all().reduce()` 时，设置节点为执行一次：**

- 输出应该是单个聚合结果，而不是每个项目的。

这是 `executeOnce: true` 在节点上。大多数节点都有它。

```ts
const aggregateNode = node({
    type: 'n8n-nodes-base.set',
    config: {
        executeOnce: true,            // 使用 .all() 在表达式中的时候很重要
        parameters: {
            assignments: {
                assignments: [
                    {
                        name: 'totalEligible',
                        value: `={{
                            $('Get Entries').all()
                                .map(item => item.json)
                                .filter(entry => entry.eligible)
                                .length
                        }}`,
                        type: 'number',
                    },
                ],
            },
        },
    },
})
```

忘记 `executeOnce` 通常仍然可以工作，但会为每个项目执行 N 次工作。更糟的是，如果下游期望一个项目，你会得到 N 个。

**反例：`.all()` 作为每个项目的查找，而不是聚合。** 当 `.all()` 读取一个*不同*的节点，并由当前项目的身份过滤时，你想要每个项目执行。每次迭代产生不同的结果，所以这是真实的工作，而不是浪费。

```ts
// 工作流：Get Tags (200 个项目) → 搜索帖子 (10 个项目) → 这个 Set Fields 节点。
// 每个帖子都携带一个 `tag_ids` 数组。Set Fields 按项目执行（10 次）
// 并将每个帖子的 tag_ids 解析为完整的 tag 对象。
tags: ={{
  $('Get Tags').all()
    .filter(tag => $('Search Posts').item.json.tag_ids.includes(tag.json.id))
}}
```

设置 `executeOnce: true` 会将 10 个输出合并为 1。

区分两者的形状：

- `$source.all()` *单独*（跨数据集聚合）→ `executeOnce: true`。
- `$source.all().filter(... matches $other.item.json.x)`（通过当前项目查找）→ 不需要 `executeOnce`。

**快速测试：** 表达式是否使用 `.all()` *而没有*与另一个节点的 `.item` 结合？如果是，节点可能应该是 `executeOnce: true`。

对于迭代和显式循环的更广泛概述，见 `n8n-loops-official` 技能。

### 条件语句

```ts
{{ $json.status === 'active' ? 'Active' : 'Inactive' }}
{{ $json.amount >= 100 ? 'Large' : ($json.amount >= 10 ? 'Medium' : 'Small') }}
```

### 日期计算（Luxon）

```ts
{{ DateTime.now().toISO() }}
{{ DateTime.fromISO($json.created_at).toFormat('yyyy-MM-dd') }}
{{ DateTime.now().minus({ days: 7 }).startOf('day').toISO() }}
{{ DateTime.fromISO($json.due).diffNow('days').days }}    // 现在的日期差（如果是负数，则表示已过期）
```

### 跨节点引用（优先于 `$json`）

```ts
{{ $('Webhook Trigger').item.json.body.customer_id }}
{{ $('Lookup customer').item.json.email }}
{{ $('Combine Inputs').item.json.coupon_code }}    // NoOp 汇聚点
```

`.item` 和 `.first()` 对于单项目节点几乎等效，所以选择一个。`.first()` 更明确，`.item` 更简短。

### 带有 IIFE 箭函数的多行逻辑

当逻辑太复杂无法在一行中写完，但操作在单个项目上时，将其包装在立即调用的箭函数中：

```ts
{{ (() => {
    // 计算包括税的总价
    const items = $json.line_items
    const subtotal = items.reduce((sum, item) => sum + item.price * item.qty, 0)
    const tax = subtotal * 0.08
    return (subtotal + tax).toFixed(2)
})() }}
```

在内部，你得到完整的表达式范围（`$json`、`$('Node Name')`、`$now`、Luxon）以及你在任何函数中写的 JS：`const`/`let`、`if`/`switch`、`try`/`catch`、正则表达式。

**参数不起作用。** 表达式没有调用者来传递它们，所以 `(text) => text.replace(...)` 没有东西来调用它。直接引用外部的值。函数仍然需要 IIFE 包装（`(...)()`) 来实际执行。

```ts
{{ (() => $json.text.replace(/\b(?:foo|bar)\b/gi, 'baz'))() }}
```

外部的 `(` 和尾随的 `)()` 是必需的：第一对括号括住函数表达式，尾随的 `()` 调用它。丢掉任何一个，n8n 都会出错并拒绝运行工作流。

**为什么选择这个而不是代码节点？** 代码节点在一个沙盒化的虚拟机中运行：最坏情况下大约 500-1000ms。表达式 IIFE 在周围表达式的相同上下文中运行：一致地 1-10ms。对于纯单项目形状，这是一个 100 倍的差距，没有功能差异。这是常见的高级用户方法。

代码节点仍然值得存在用于多项目聚合（`$input.all()`）、外部库或异步工作。见 `n8n-code-nodes-official` 的决策树，以及 `n8n-code-nodes-official` `ARROW_FUNCTIONS_IN_EDIT_FIELDS.md` 的更长时间示例和格式规则。

### 可用的原生 JS

`String`、`Array`、`Number`、`Object`、`Map`、`Set`、`JSON.parse`、`JSON.stringify`、`Math`、正则表达式、`Date`（但只使用 Luxon）。

## 有用的模式

### 当字段可能缺失时的默认值

```ts
{{ $json.id || "fallback-id-here" }}
```

或者使用可选链：

```ts
{{ $json.user?.profile?.id ?? "anonymous" }}
```

特别适用于为查询提供过滤值的场景：传递一个匹配不到任何行的默认值，而不是让查询因 `undefined` 而失败。

### 在文本字段中嵌入 JSON：哪个序列化器

两个序列化器，两个上下文：

- **`.toJsonString()`** 用于紧凑的 JSON，格式不重要。典型情况：**AI 提示**。更小，对 token 更友好，在提示模板中更容易扫描。
  ```ts
  {{ $('Get Data').item.json.toJsonString() }}
  ```
- **`JSON.stringify(value, null, 2)`** 用于格式化的 JSON，格式很重要。典型情况：**邮件正文、Slack 消息、调试输出**，任何人类会阅读结果的地方。
  ```ts
  {{ JSON.stringify($('Source Node').item.json, null, 2) }}
  ```

故意选择。在 LLM 提示中格式化会浪费 token 并使模型上下文混乱。在邮件中传递紧凑的 JSON 是难以阅读的。

### `JSON.stringify` 和 `JSON.parse`：它们属于哪里

`JSON.stringify` 和 `JSON.parse` 在表达式中很常见。两者都可以。关键纪律：**序列化和解析是存储层操作，不是接口层操作。**

- **序列化时写入不原生支持类型的存储列。** 典型情况：一个 Data Tables `_object` 后缀的字符串列，实际上是一个数组或对象。见 `n8n-data-tables-official`。
- **从存储列中读取时解析。** 在拥有存储的工作流内部。
- **不要在边界之间传播序列化的形状。** 子工作流返回、webhook 响应、代理工具结果、下游消费者：所有这些都应该接收自然形状（数组作为数组，对象作为对象），而不是调用者必须记住要 `JSON.parse` 的字符串化外壳。
- 经典错误：子工作流有一个“新鲜”路径（由 LLM 产生的数据，已经是数组）和一个“缓存”路径（从 `_object` 列刚读取的数据，仍然是字符串）。错误的直觉是序列化新鲜路径“以匹配”缓存的一个。正确的直觉是解析缓存路径，以便两个分支在出去时都产生相同的自然形状。见 `n8n-subworkflows-official` SKILL.md “返回自然形状，而不是存储形状” 从子工作流的角度，以及 `n8n-data-tables-official` 从存储的角度覆盖这一点。

存储表示属于拥有存储的工作流内部。在这个边界之外，用自然形状交谈。`n8n-subworkflows-official` 技能的 "Return natural shapes, not storage shapes" 从子工作流的角度覆盖了这一点，`n8n-data-tables-official` 从存储的角度覆盖了这一点。

### 返回正确的类型：何时用 `={{ ... }}` 包裹

某些节点字段会将其值视为字符串字面量，除非你告诉 n8n 将其作为表达式评估。用 `={{ ... }}`（`=` 前缀将字段转换为表达式模式）返回内部代码产生的实际类型：

```ts
// 字符串字面量（默认行为）
foo: 'plain string'

// 数字
foo: '={{ 100 }}'

// 布尔值
foo: '={{ true }}'

// 对象（`={{ ... }}` 是使接收者看到对象而不是字符串的关键）
foo: '={{ { "valid": true, "items": [] } }}'

// 数组
foo: '={{ ["a", "b", "c"] }}'

// 引用另一个节点的值（保留该值已经的类型）
foo: '={{ $("Source Node").item.json.payload }}'
```

当类型很重要时：Set / Edit Fields 上的对象/数组字段（将列的 `Type` 设置为 Object 或 Array）、HTTP 请求的 JSON 正文参数、子工作流的类型化 `workflowInputs.values[type]` 输入、代理工具参数、任何接收者验证类型的字段。没有 `={{ ... }}` 包装，你会传递一个字符串，接收者要么强制转换，要么出错。

**通过节点名称引用，而不是 `$json`**，根据非谈判 #1：

```ts
// 错误
foo: '={{ $json.payload }}'

// 正确
foo: '={{ $("Source Node").item.json.payload }}'
```

例外：如果 `$json` 真的是正确的（没有中间转换，没有汇聚），并且字段是直接位于一个源下游的每个项目槽位。即使如此，命名引用也更安全于重构。

### 带有解释性注释的多行表达式

```ts
{{
  // 当用户_id 缺失时避免查询错误。
  // 落幅 UUID 是一个已知的空行。
  $json.id || "305f7106-6988-4651-b26a-18979641b7b5"
}}
```

**鼓励** 当逻辑不明显时。注释将在那里为下一个读者提供。

## 表达式不能做什么

- 使用外部库（没有 `require`）。
- Async / await。

`$json` 本身只是当前项目，但表达式*可以通过* `$input.all()`、`$input.all()[3]`、`$('Source Node').all()` 等跨项目查找。见上文的“方法链”。

对于这些，见 `n8n-code-nodes-official`。

## 决策：表达式、Edit Fields 或 Code 节点？

根据 `n8n-code-nodes-official` 的决策树：

```
1. 单字段转换 → 字段中的表达式
2. 单个项目上的多步纯逻辑 → Edit Fields 中的箭函数
3. 多源聚合、库或状态 → Code 节点
```

表达式是默认值。只有在输入或范围要求时才超出它。

## “额外节点”的气味

应该保留在表达式中的常见额外节点：

| 添加这个节点 | 更好的方式 |
|---|---|
| DateTime 节点来格式化日期 | `DateTime.fromISO(...).toFormat(...)` 在消费者的表达式中 |
| Set 节点来构建邮件正文 | 在邮件节点的 body 字段中内联表达式 |
| Set 节点来计算仅用于一次的派生字段 | 在消费者处内联 |
| 两个节点（Set + IF）来计算然后测试 | 一个 IF，计算在其条件表达式 |
| Code 节点来调用 `.toUpperCase()` | 仅表达式 |

为转换添加节点意味着更多的视觉杂乱，工作流更慢，阅读更困难。

当额外节点是正确的时候：

- 转换被*多个下游消费者*重用。
- 转换很重（Code 节点领域）。
- 转换是一个部分的*主要目的*（一个清晰的“计算 X”步骤）。

## 反模式

| 反模式 | 出现什么问题 | 修复 |
|---|---|---|
| 存在仅用于从 webhook 正文提取一个字段以供单个下游消费者使用的 Set 节点 | 额外节点用于本应内联的内容，重构时易碎 | 删除 Set 节点，在消费者处直接引用 `$('Webhook').item.json.body.x` |
| 多个连续的 Set 节点，每个节点定义一个字段 | 工作流填充 | 合并。大多数都不需要，对于需要它们的部分，合并成一个 Set 节点 |
| 在具有多个分支和中间转换的工作流深处使用 `$json.x` | 当中间节点被添加或上下文被清除时引用会中断 | 使用 `$('Source Node').item.json.x`。如果分支汇聚，添加一个 NoOp 汇聚点。 |
| 添加 DateTime 节点来格式化时间戳 | 额外节点用于 1 行 Luxon 表达式可以完成的事情 | `{{ DateTime.fromISO($('Source').item.json.x).toFormat('yyyy-MM-dd') }}` |
| Set 节点来构建邮件 HTML，然后在邮件节点中读取它 | 两个节点用于一个表达式可以完成的事情 | 直接在邮件节点的 body 字段中构建 HTML |
| `new Date($json.created_at)` 而不是 Luxon | 失去格式化/操作功能 | `DateTime.fromISO($('Source').item.json.created_at)` |
| 一行表达式实际上是 200 个字符 | 难以阅读 | 多行带箭函数、缩进、注释 |
| `$json.foo.bar.baz` 而不检查 `$json.foo` 存在 | 缺失中间项时崩溃 | 使用 `?.` 链：`$('Source').item.json.foo?.bar?.baz` |
| 在表达式硬编码应该配置的值 | 魔术字符串 | 使用 `$vars.X`（n8n 变量，付费计划）或 Data Table |
| 分支汇聚时下游使用 `$json` 引用 | 最后触发的分支获胜，非确定性 | 在合并处插入一个 NoOp（“Combine Inputs”），通过名称引用 |
| 在任何表达式中使用 `$env.X` | 不起作用；在运行时抛出错误 | 配置使用 `$vars.X`（付费计划）或 Data Table。密钥使用凭证系统 |
