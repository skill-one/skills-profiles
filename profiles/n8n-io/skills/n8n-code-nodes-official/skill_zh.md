# n8n 代码节点

代码节点功能强大，但往往不是正确的工具。n8n 中相当于在 ORM 可以完成时直接使用原始 SQL 的情况：确实存在实际案例，但一旦代码节点处理逻辑而表达式可以完成，工作流就变得更难阅读、调试和维护。还有一个真实的性能差距：代码在沙盒化的 JS 运行时中运行，表达式和编辑字段在进程内运行，每次调用的开销可能高数百倍（据传闻约 2ms 对比 ~600ms 用于等效逻辑）。对于热路径和大量项目，这会累积。

## 强制默认值

1. **代码节点是最后的手段。** 决策顺序：表达式（`{{...}}`）→ 编辑字段内的箭头函数 → 代码节点。前两种路径涵盖了大多数“转换这些数据”的任务。代码为其在多源聚合、外部库和一些特定模式（如下文所述）中赢得了一席之地。

2. **默认使用 JavaScript。** 除非用户明确要求使用 Python（“在这里使用 Python”、“我们是 Python 团队”、“粘贴了 Python 代码”），否则编写 JS。n8n 的其他地方（表达式、编辑字段）都是 JS，JS 有一个经过筛选的库白名单（`lodash`、`crypto`、`luxon`）。

## 决策树

```
需要自定义逻辑吗？
├── 它是对一个或两个字段的转换吗？
│   └── 表达式：`{{ $json.foo.toUpperCase() }}` 或 `{{ $json.items.map(item => item.name).join(', ') }}`
│       大多数“只是转换这些”的情况都落在这里。
│
├── 它是多行的，但纯粹是数据塑形（map、filter、reduce、条件）吗？
│   └── 带箭头函数表达式的编辑字段。参见参考资料/ARROW_FUNCTIONS_IN_EDIT_FIELDS.md
│
├── 它需要完整语句、多个数据源或外部库吗？
│   ├── 你确定前两种方法行不通吗？
│   │   └── 重新阅读父节点。标准很高。
│   └── 是的，确实需要它
│       └── 代码节点。参见参考资料/JAVASCRIPT_PATTERNS.md
│
└── 它实际上是两个分开的转换连接在一起吗？
    └── 使用两个节点（编辑字段 → 编辑字段，或编辑字段 → IF）。组合性优于一个大的代码块。
```

有关每个分支的完整决策逻辑和示例，请参阅 `references/DECISION_TREE.md`。

## 表达式可以做到而人们忘记的事情

应该使用表达式而不是代码节点的常见情况：

```ts
// ❌ 代码节点
return { name: $input.first().json.name.toUpperCase() }

// ✅ 编辑字段中的表达式，“name”字段
{{ $json.name.toUpperCase() }}
```

```ts
// ❌ 代码节点
const items = $input.first().json.items
return { tags: items.map(item => item.tag).filter(tag => tag).join(', ') }

// ✅ 表达式
{{ $json.items.map(item => item.tag).filter(tag => tag).join(', ') }}
```

```ts
// ❌ 代码节点
const date = new Date($input.first().json.created_at)
return { formatted: date.toISOString().slice(0, 10) }

// ✅ 使用 n8n 的日期扩展的表达式
{{ $json.created_at.toDateTime().format('yyyy-MM-dd') }}
```

有关表达式可以表达的内容的更多信息，请参阅 `n8n-expressions-official` 技能。

## 编辑字段中的箭头函数可以做到

编辑字段通过表达式分配字段值。内联箭头函数可以在不使用代码节点的情况下获得大多数多行逻辑：

```ts
// 在编辑字段中，“summary”字段：
{{ (() => {
    const items = $json.items
    const total = items.reduce((sum, item) => sum + item.price, 0)
    const tax = total * 0.08
    return `Total: $${(total + tax).toFixed(2)}`
})() }}
```

适用于“逻辑稍微复杂，不适合单行”的情况。有关模式和格式的详细信息，请参阅 `references/ARROW_FUNCTIONS_IN_EDIT_FIELDS.md`。

## 代码节点是正确答案的情况

确实存在实际用途。标准很高，不是“从不”。以下情况是**合法的**。使用代码构建，无需道歉。

### 跨整个数据集的多源聚合

当节点需要：

- 同时从**多个上游节点读取**（例如，`$('Source A').all()`、`$('Source B').all()`、`$('Source C').first().json`）。
- 计算或转换**一次跨所有项目**（不是按项目）。
- 应用多步逻辑和中间数据结构（查找映射、累加器、比率）。

最常见的有效情况。示例：

- 分析汇总：按组的平均值、百分位数评分、跨类别的标准化。
- 从一个源构建查找表，并与来自另一个源的数据行进行连接。
- 计算两个参考数据集的偏移/比率，然后应用于第三个数据集。

```ts
// 真实形状：从一个源聚合测试结果，
// 从另一个源建模元数据，
// 从第三个源获取类别映射，
// 并生成按模型按类别的平均值。

const testResults = $('Get Test Results').all().map(item => item.json)
const models = $('Get Models').all().map(item => item.json)
const categoryMap = $('Get Category Map').first().json.testCategoryMap

const categoryByTestId = Object.fromEntries(
    categoryMap.map(mapping => [mapping.testId, mapping.category])
)

const result = models.map(model => {
    const modelTests = testResults.filter(test => test.modelId === model.id)
    const stats = modelTests.reduce((acc, test) => {
        const cat = categoryByTestId[test.testId]
        if (!cat) return acc
        acc[cat] ??= { scored: 0, available: 0, count: 0 }
        acc[cat].scored += test.pointsScored ?? 0
        acc[cat].available += test.pointsAvailable ?? 0
        acc[cat].count += 1
        return acc
    }, {})

    const averages = Object.fromEntries(
        Object.entries(stats).map(([category, stat]) => [
            category,
            { avg: stat.available > 0 ? stat.scored / stat.available : 0, n: stat.count }
        ])
    )

    return { modelId: model.id, modelName: model.modelName, ...averages }
})

return result.map(json => ({ json }))
```

技术上，表达式可以通过 `$('Node Name').all()` 跨项目，并内联减少，但对于具有这种程度形状（连接、分组、嵌套聚合）的情况，结果是一个单行超级表达式，难以阅读且无法调试。使用代码。

### 外部库

JS 代码可以从经过筛选的白名单（lodash 等）中 `require`，但表达式不能。 

**始终先检查是否有原生节点。** n8n 比人们意识到的原生节点更多。为具有原生节点的东西使用代码是一个反复出现的错误。下一节的两个子部分涵盖了特定的陷阱。

### 密码学操作：使用密码学节点，而不是代码

HMAC、签名、哈希、加密：**n8n 有一个原生密码学节点（`n8n-nodes-base.crypto`）。** 使用它。它处理 SHA256、MD5、HMAC、加密/解密和随机生成，所有这些都不需要编写 JavaScript。

```ts
// 错误（反复出现的 AI 错误）：
const crypto = require('crypto')
const hash = crypto.createHash('sha256').update(buf).digest('hex').slice(0, 12)

// 正确：配置密码学节点，操作：'hash'，类型：'SHA256'
//   然后在下游读取 `$('Hash').item.json.<output>`。
```

带 `require('crypto')` 的代码模式是“这需要代码节点”最常见的假阳性之一。它不需要。密码学节点涵盖了它。

#### 哈希二进制，而不是字符串

不要因为需要哈希*二进制*（一个 PDF、一个图像、一个文件缓冲区）就使用代码。密码学节点有一个 `binaryPropertyName` 参数。将它指向二进制槽键，它将直接哈希缓冲区。你不需要用户代码中的 `this.helpers.getBinaryDataBuffer(...)`。

```ts
// 错误（带有二进制的反复出现的 AI 错误）：
const crypto = require('crypto')
const buf = await this.helpers.getBinaryDataBuffer($itemIndex, 'data')
const hash = crypto.createHash('sha256').update(buf).digest('hex')

// 正确：配置密码学节点，binaryPropertyName='data'，SHA256。
//   然后 `$('Crypto').item.json.<output>` 有哈希；链接一个设置节点进行任何字段塑形。
```

剩余的有效代码-加密情况：一种密码学节点未公开的非标准签名方案（例如，自定义 AWS 风格的签名），并且 `httpCustomAuth` 凭据也不适用。罕见。明确说明理由。

### XML / SOAP / RSS 解析：使用 XML 节点，而不是代码

**n8n 有一个原生 XML 节点（`n8n-nodes-base.xml`）** 具有解析和字符串化操作。它已经将 XML 转换为 JSON。一旦它有了，结果就是普通的 JSON，编辑字段中的箭头函数表达式处理所有字段提取、数组规范化（`Array.isArray(...) ? ... : ...`）和链接查找（`.find()`），这些是你会使用代码来完成的事情。

```ts
// 错误（反复出现的 AI 错误）：
// XML 节点已解析 → 另一个代码节点来提取几个字段：
const entry = $('Parse XML').item.json.feed.entry
const firstEntry = Array.isArray(entry) ? entry[0] : entry
return { json: { title: firstEntry.title, url: firstEntry.link.find(link => link.type === 'pdf').href } }

// 正确：编辑字段中的箭头函数表达式：
//   title:  ={{ (() => { const entry = $('Parse XML').item.json.feed.entry; return Array.isArray(entry) ? entry[0].title : entry.title; })() }}
//   pdfUrl: ={{ $('Parse XML').item.json.feed.entry.link.find(link => link.type === 'pdf')?.href }}
```

如果字段提取逻辑对于内联表达式即使使用多行箭头函数也过于复杂，下一步是使用单个多行箭头函数的编辑字段，而不是代码节点。参见 `references/ARROW_FUNCTIONS_IN_EDIT_FIELDS.md`。

### 这些共同点是什么

有效情况是关于**范围**：整个数据集、多个源或单项目工具无法触及的状态性结构。无效情况：代码节点做表达式可以完成的事情，或者原生节点已经做的事情。

快速测试：

- **“我可以将代码节点的任务描述为‘取这个单个项目并...'吗？”** 如果是，错误工具。
- **“有这个原生节点吗？”** 通过 `search_nodes` 首先搜索。密码学、XML、JSON 解析、日期数学（Luxon）、HTTP 调用、文件 I/O、正则表达式匹配：所有这些都有原生节点或表达式级支持。

## JavaScript 代码节点具体细节

两种模式：

- **为所有项目运行一次（默认，使用此模式）：** 使用 `$input.all()` 运行一次。如果你需要按项目逻辑，只需在内部 `for (const item of $input.all())`。这是标准形状，几乎总是你想要的。
- **为每个项目运行一次：** 使用 `$input.first()`（或 `$input.item`）为每个项目运行一次。

常见形状：

```ts
// 为所有项目运行一次
const items = $input.all()
const totals = items.map(item => ({
  ...item.json,
  total: item.json.qty * item.json.price,
}))
return totals.map(json => ({ json }))
```

返回值必须是 `{ json: ... }` 对象的数组（或 `{ json: ..., binary: ... }`），而不是原始 JSON。

对于二进制处理、错误模式以及代码节点特有的错误，请参阅 `references/JAVASCRIPT_PATTERNS.md`。

## 参考资料

| 文件 | 何时阅读 |
|---|---|
| `references/DECISION_TREE.md` | 你想使用代码节点，并想验证简单的路径真的行不通 |
| `references/ARROW_FUNCTIONS_IN_EDIT_FIELDS.md` | 转换是多行的，但纯粹是数据塑形 |
| `references/JAVASCRIPT_PATTERNS.md` | 真的需要代码节点，并且使用的是 JavaScript |

## 反模式

| 反模式 | 出现什么问题 | 修复 |
|---|---|---|
| 代码节点执行 `return { x: $input.first().json.x.toUpperCase() }` | 整个节点用于一个表达式 | 用编辑字段表达式替换 |
| 代码节点构建用于电子邮件正文的 HTML 字符串 | 电子邮件节点的正文字段接受表达式 | 将表达式内联到电子邮件节点 |
| 代码节点使用 `new Date()` 进行日期格式化 | 损失了 Luxon 的清晰度 | 在表达式中使用 Luxon。参见 `n8n-expressions-official` |
| 设置节点 + 代码节点组合（设置节点构建输入，代码节点转换） | 两个节点用于应该是一个编辑字段的事情 | 合并成一个带箭头函数的编辑字段 |
| 将凭证/令牌粘贴到代码节点文本中 | 与文本字段相同的泄漏 | 使用凭证，而不是代码节点 |
