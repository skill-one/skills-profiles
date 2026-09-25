# 查询 OQL — 快速参考

一个 OQL 容器暴露了两个只读方法：

| 方法 | 返回 | 目的 |
|---|---|---|
| `schema()` | 一个 JSON `Text` | 容器实体的目录：每个实体的主键、字段和边。 |
| `execute(qJson : text)` | 带有 Candid 类型的 `Result` | 运行 JSON 编码的查询并返回匹配的行。 |

## 调用容器

`icp` CLI 已经在沙盒中安装和配置；容器名称 `backend` 解析为项目的容器（无身份，无容器 ID）。这两种方法都是 `query` 调用，因此每次调用都使用 `--query`：

```bash
icp canister call backend schema '()' --query
icp canister call backend execute '("<json-query>")' --query
```

`execute` 接受一个 `text` 参数——嵌入为 Candid 文本字面量的 JSON 查询。将 JSON 包裹在 `("...")` 中，并将每个 `"` 转义为 `\"`。查询 `{"start":"customer","limit":3}` 变为：

```bash
icp canister call backend execute '("{\"start\":\"customer\",\"limit\":3}")' --query
```

`schema()` 以相同的方式返回其 JSON——一个 Candid `text` 字面量 `("...escaped json...")`；转义 `\"` → `"`（和 `\\` → `\`) 以读取它。添加 `--branch live` 以读取已部署的容器而不是草稿（live 仅用于查询）。如果一个字符串值包含单个引号，请使用 `'\''` 为 shell 转义它。

---

## 配方

1. **一次获取 schema。** `icp canister call backend schema '()' --query` — 缓存它以供会话使用；它仅在部署之间更改（§1）。
2. **将请求映射到实体。** 选择包含答案的实体。使用每个字段的 `typeName` 和 `values` 来选择字面量类型，并使用 `role: {"edge": ...}` 来查看实体如何连接。
3. **翻译成一个或多个查询。** 从您想要行的实体开始（§2）。添加 `where` (§2.1)、`orderBy` / `limit` / `offset`、`select` 和 `aggregate` / `groupBy` (§2.2)。在单个查询中跨一个前向边和一个点路径（§4.1）；一个反向一对多需要首先获取父键，然后 `in` (§4.2)。
4. **运行和读取。** `icp canister call backend execute '("<json>")' --query` — 通过单元 `name` 解析 Candid 行（§3）；如果 `hasMore`，则使用 `offset` 分页（§5）。
5. **在陷阱时重试。** 没有错误包——重新读取 schema，修复查询，重新运行（§6）。

---

## 1. 发现 — `schema`

一次获取并缓存以供会话使用——它仅在容器部署之间更改。

```bash
icp canister call backend schema '()' --query
```

像这样读取它：

- **`name`** → 实体名称；在查询中使用它作为 `start`。
- **`primaryKey`** → 确定行的字段值。边 `{"to": "<entity>"}` 值是目标实体的主键值。
- **`fields`** → 每个字段的 `name`、标量 `typeName` 和 `role`：
  `"payload"`（普通字段）或 `{"edge": {"to": "<entity>"}}`（外键——如何遍历图）。名称可能在两个列共享名称时会带有 `__1`、`__2`、… 后缀——使用 `schema()` 报告的确切名称。
- **`values`**（可选）→ 字段可以持有的确切字面量（通常是变体的臂）。使用这些字面量进行过滤，而不是猜测：
  `["free","pro","enterprise"]` 表示查询 `"enterprise"`，而不是 `"Enterprise"`。不存在 ⇒ 无限制——如果您需要候选者，请使用查询进行采样。
- **`typeName`** → `value` 的 JSON 字面量类型：
  - `"Nat"` → 无符号整数（`0`、`1`、…）
  - `"Int"` → 有符号整数（`-1`、`0`、`1`、…）
  - `"Float"` → 带有十进制点的 JSON 数字（`0.5`、`-3.14`、`1.0e2`）。裸整数（`10`）也接受——数字变体桥接，所以 `gt(price, 10)` 匹配 `price : Float = 12.5` 行。
  - 浮点数相等是按位 IEEE-754；使用范围（`ge` + `le`）来表示没有精确二进制形式的十进制数，例如 `0.42`。
  - `"Bool"` → `true` / `false`
  - `"Text"` → JSON 字符串。`Principal` 字段报告为 `"Text"`（规范文本形式）——使用字符串值进行过滤。

---

## 2. 形成查询 — `execute`

查询是一个 JSON 对象。只有 `start` 是必需的。

```json
{
  "start":     "<entityName>",
  "where":     <Predicate>,
  "groupBy":   ["<fieldName>", ...],
  "aggregate": [{ "fn": "count|sum|avg|min|max", "field": "<fieldName>", "as": "<outName>" }, ...],
  "orderBy":   [{ "field": "<fieldName>", "dir": "asc|desc" }, ...],
  "offset":    <Nat>,
  "limit":     <Nat>,
  "select":    ["<fieldName>", ...]
}
```

| 字段 | 默认 | 备注 |
|---|---|---|
| `start` | (必需) | 来自 `schema()` 的实体 `name`。 |
| `where` | 省略 ⇒ 无过滤 | 单个谓词（§2.1）——**不**包裹在 `{"filter": ...}` 中。 |
| `groupBy` | `[]` | 按这些字段对行进行分组；每个不同的组合一个输出行（§2.2）。 |
| `aggregate` | `[]` | 每个分组聚合，或当 `groupBy` 为空时对所有行聚合（§2.2）。 |
| `orderBy` | `[]`（容器定义的顺序，通常是插入顺序） | 多键排序，第一组为主要排序。`dir` 默认 `"asc"`。 |
| `offset` | `0` | 跳过前 N 个匹配项。 |
| `limit` | 每个匹配项 | 最多保留 N 个。结果中的 `hasMore` 告诉您是否存在更多。 |
| `select` | 每个非隐藏字段（或，当聚合时，分组键 + 聚合列） | 子集投影。 |

```bash
icp canister call backend execute '("{\"start\":\"customer\",\"limit\":3}")' --query
```

过滤 + 排序 + 投影——核心形状（`where` + `orderBy` + `limit` + `select`）：

```bash
icp canister call backend execute '("{\"start\":\"customer\",\"where\":{\"eq\":{\"field\":\"plan\",\"value\":\"enterprise\"}},\"orderBy\":[{\"field\":\"monthlyRevenueUsd\",\"dir\":\"desc\"}],\"limit\":5,\"select\":[\"companyName\",\"monthlyRevenueUsd\",\"accountManagerName\"]}")' --query
```

### 2.1 谓词运算符

谓词是一个具有**恰好一个键**的 JSON 对象，该键命名运算符。

| 运算符 | 形状 | 含义 |
|---|---|---|
| `eq` / `ne` / `lt` / `le` / `gt` / `ge` | `{"<op>": { "field": "<name>", "value": <scalar> } }` | 标量关系。 |
| `in` | `{"in": { "field": "<name>", "value": [<scalar>, ...] } }` | 成员资格；空数组匹配不到任何内容。 |
| `contains` / `startsWith` / `endsWith` | `{"<op>": { "field": "<name>", "value": "<text>" } }` | 对 `Text` 的区分大小写的子字符串 / 前缀 / 后缀——服务器端扫描，无需将行分页到上下文中。 |
| `icontains` | `{"icontains": { "field": "<name>", "value": "<text>" } }` | 区分大小写的 `contains`。对于用户输入的搜索词，请优先使用此选项。 |
| `and` / `or` / `not` | `{"and": [<P>, ...]}` / `{"or": [<P>, ...]}` / `{"not": <P>}` | 布尔组合。 |

文本搜索在服务器端运行——"提及 north 的客户"是一个查询，而不是对上下文中的行进行扫描：

```bash
icp canister call backend execute '("{\"start\":\"customer\",\"where\":{\"icontains\":{\"field\":\"companyName\",\"value\":\"north\"}},\"select\":[\"companyName\",\"accountManagerName\"]}")' --query
```

`<scalar>` 必须与字段的 `typeName` 匹配：

| JSON | 映射到 | 用于具有 typeName 的字段 |
|---|---|---|
| `null` | `null_` | 任何可空字段（在 `where` 中很少见） |
| `true` / `false` | `bool` | `"Bool"` |
| `0`、`1`、`42` | `nat` | `"Nat"`（也通过数字桥接匹配 `"Float"`） |
| `-1`、`-42` | `int` | `"Int"`（也通过数字桥接匹配 `"Float"`） |
| `0.5`、`-3.14`、`1.0e2` | `float` | `"Float"` |
| `"foo"` | `text` | `"Text"` |

一个字段为 `null_` 的行会失败除 `ne` 之外的所有关系。通过 `field` = `"<edge>"` 和 `value` = 目标实体的**主键值**进行过滤关系；或者通过边读取 `"<edge>.<targetField>"`（§4.1）。

### 2.2 聚合 — count、groupBy、sum/avg/min/max

在容器中而不是在客户端获取每一行并计算总计。`fn` 是 `count`/`sum`/`avg`/`min`/`max`；`field` 对于 `count` 之外的所有 `fn` 都是必需的；`min`/`max` 也适用于文本。`as` 重命名输出列（默认 `count`、`sum_<field>`、…），并且不能包含 `.`（点是用作边遍历分隔符——解析错误）。对于点 `field`，默认将段连接为 `_`（`sum` of `dept.budget` → `sum_dept_budget`）。没有 `groupBy` 的 `aggregate` → 对整个过滤集的一个行（`count` 的空匹配是 `0`）。没有 `aggregate` 的 `groupBy` → 服务器端的 DISTINCT。输出行只包含分组键 + 聚合列。

"有多少企业客户？"——对过滤集的 `count`，一个输出行：

```bash
icp canister call backend execute '("{\"start\":\"customer\",\"where\":{\"eq\":{\"field\":\"plan\",\"value\":\"enterprise\"}},\"aggregate\":[{\"fn\":\"count\"}]}")' --query
```

"哪个账户经理拥有最多的客户，以及总 MRR？"——`groupBy` + `count` + `sum`：

```bash
icp canister call backend execute '("{\"start\":\"customer\",\"groupBy\":[\"accountManager\"],\"aggregate\":[{\"fn\":\"count\"},{\"fn\":\"sum\",\"field\":\"monthlyRevenueUsd\",\"as\":\"mrr\"}],\"orderBy\":[{\"field\":\"count\",\"dir\":\"desc\"}],\"limit\":1}")' --query
```

---

## 3. 读取结果

```candid
type Value  = variant { null_; bool : bool; nat : nat; int : int; float : float; text : text };
type Cell   = record { name : text; value : Value };
type Result = record { rows : vec vec Cell; hasMore : bool };
```

外层 `rows = vec { ... }` 是行列表；每个内层 `vec { ... }` 是一行。每个 `record { value = variant { "<tag>" = <payload> }; name = "<field>" }` 是一个单元——`name` 告诉您哪个字段，`<tag>` 告诉您标量类型，有效负载是值。`35_000 : nat` 下划线是数字分隔符——如果解析，请删除它们。`hasMore = false` ⇒ 您获得了所有匹配项；`hasMore = true` ⇒ 截断，获取下一页。通过 `name` 而不是位置查找单元，因为如果 `select` 更改，顺序会改变。

---

## 4. 遍历边（连接）

**前向（单值）关系是一个查询**：一个点路径跨越一个声明的边，在任何字段位置。**反向（一对多）关系仍然是两个查询**，使用 `in` 模式（§4.2）。

### 4.1 前向（子→父）：点路径

`"<edgeField>.<targetField>"` 在服务器端通过边读取——在 `where`、`groupBy`、`orderBy`、`aggregate.field` 和 `select` 中。在一个查询中通过边投影：

```bash
icp canister call backend execute '("{\"start\":\"customer\",\"where\":{\"eq\":{\"field\":\"companyName\",\"value\":\"Northstar Public\"}},\"select\":[\"companyName\",\"accountManager.name\",\"accountManager.office\"]}")' --query
```

多跳链工作（`"manager.department.name"`，最多 4 跳），并且它可以与聚合组合——"按账户经理的办公室计算平均收入"是一个调用：

```bash
icp canister call backend execute '("{\"start\":\"customer\",\"groupBy\":[\"accountManager.office\"],\"aggregate\":[{\"fn\":\"avg\",\"field\":\"monthlyRevenueUsd\",\"as\":\"avg_mrr\"}],\"orderBy\":[{\"field\":\"avg_mrr\",\"dir\":\"desc\"}]}")' --query
```

规则：

- 头段必须在 `schema()` 中是 `{"edge": {"to": ... }}` 的字段——进入非边字段的点路径**会触发错误**，即使其值看起来像外键（遍历由 schema 驱动，而不是名称猜测）。如果作者没有声明边，请回退到下面的两个查询模式。
- 空或悬空 FK 将整个点路径解析为 `null`（左连接）：该行会失败除 `ne` 之外的所有关系，并且将单元投影为 `null`。
- **从多侧聚合。** 跨实体聚合运行在起始实体的行上：`avg` of `"department.budget"` from `employee` 是按员工加权的。对于每个部门的数字，从 `department` 开始——或者按点路径分组并聚合起始实体字段。
- 选择裸边字段（`"accountManager"`）仍然返回 FK 标量；没有 `.*`——命名您想要的每个目标字段。

### 4.2 反向（一父→多子）

`eq` 用于一个父主键，`in` 用于批量——在边字段上，使用目标实体的主键值。

```bash
icp canister call backend execute '("{\"start\":\"customer\",\"where\":{\"eq\":{\"field\":\"accountManager\",\"value\":\"daniel@helix.systems\"}},\"select\":[\"companyName\",\"monthlyRevenueUsd\"]}")' --query
```

当父条件是一个普通谓词时，您不需要批量——它是一个通过边的前向过滤（§4.1）。"所有由柏林办公室的任何人管理的客户"是一个查询：

```bash
icp canister call backend execute '("{\"start\":\"customer\",\"where\":{\"eq\":{\"field\":\"accountManager.office\",\"value\":\"Berlin\"}},\"select\":[\"companyName\",\"monthlyRevenueUsd\"]}")' --query
```

当父集需要自己的查询形状（top-N、排序、分页）时，需要使用 `in` 模式（§4.2）。"由三个最高级员工管理的客户"是两个查询：

```bash
icp canister call backend execute '("{\"start\":\"employee\",\"orderBy\":[{\"field\":\"level\",\"dir\":\"desc\"}],\"limit\":3,\"select\":[\"email\"]}")' --query
# 从行中收集三个电子邮件，然后：
icp canister call backend execute '("{\"start\":\"customer\",\"where\":{\"in\":{\"field\":\"accountManager\",\"value\":[\"alex@helix.systems\",\"james@helix.systems\",\"sarah@helix.systems\"]}},\"select\":[\"companyName\",\"monthlyRevenueUsd\"]}")' --query
```

始终使用 `in` 批量，而不是运行 N 个单独的 `eq` 查询。

### 4.3 复合条件

使用 `and` / `or` 堆叠：

```bash
icp canister call backend execute '("{\"start\":\"customer\",\"where\":{\"and\":[{\"eq\":{\"field\":\"plan\",\"value\":\"enterprise\"}},{\"in\":{\"field\":\"country\",\"value\":[\"US\",\"CA\",\"DE\"]}},{\"ge\":{\"field\":\"monthlyRevenueUsd\",\"value\":20000}}]},\"orderBy\":[{\"field\":\"monthlyRevenueUsd\",\"dir\":\"desc\"}]}")' --query
```

### 4.4 两跳 / 自边连接

当父键未给出但必须首先查找时——例如，"谁向 `forge20` 项目的负责人报告？"——运行两个查询。第二个查询根据第一个查询返回的键在自边（`employee.manager` → `employee`）上过滤：

```bash
icp canister call backend execute '("{\"start\":\"project\",\"where\":{\"eq\":{\"field\":\"codename\",\"value\":\"forge20\"}},\"select\":[\"lead\"]}")' --query
# 行的 `lead` 单元是负责人的电子邮件，例如 `priya@helix.systems`——将其用作父键：
icp canister call backend execute '("{\"start\":\"employee\",\"where\":{\"eq\":{\"field\":\"manager\",\"value\":\"priya@helix.systems\"}},\"select\":[\"name\",\"jobTitle\",\"level\"]}")' --query
```

---

## 5. 分页

`limit` 限制结果。`hasMore` 报告截断。使用 `offset` 遍历页面：

```text
offset = 0
limit  = 25
loop:
  result = icp canister call backend execute '("{\"start\":\"...\",\"limit\":25,\"offset\":<offset>,...}")' --query
  consume result.rows
  if not result.hasMore: break
  offset += limit
```

始终显式设置 `limit`。OQL 本身不设限制（省略 `limit` 返回所有匹配项），并且容器作者可能会添加一个限制——在这种情况下，过度请求会被静默截断。

---

## 6. 陷阱

| 症状 | 原因 / 修复 |
|---|---|
| `execute` 触发 `OQL: unknown entity '...'` | `start` 与 `schema()` 中的任何 `name` 都不匹配——实体名称区分大小写。重新读取 schema。 |
| `execute` 触发解析错误 | JSON 格式错误（尾随逗号、单引号），或者没有作为 Candid 文本字面量转义——包裹为 `("...")` 并将每个内部 `"` 转义为 `\"`。首先使用 `python3 -m json.tool` 验证 JSON。 |
| `execute` 触发 `OQL: unknown field '...' on '...' — fields: ...` | `field` 中的拼写错误——陷阱列出了实体的实际字段。选择其中一个。 |
| `execute` 触发 `OQL: invalid query — where: field "..." is Int but value is Text` | `value` 字面量的 JSON 类型永远不会匹配字段的 `typeName`（`"5"` 或 `"now-7d"` 对数字字段，数字对 `Text`/`Bool`；`in` 元素逐个检查）。发送字段类型的字面量——数字字段接受 `Nat`/`Int`/`Float`，`null` 始终是 is-null 测试。 |
| 您期望匹配的过滤器没有返回行 | 字段在存储中确实为 `null_`，或者字面量类型正确但值不正确（大小写、单位——时间戳是 epoch 纳秒）。 |
| `contains` 错过您可以看到的行 | `contains` / `startsWith` / `endsWith` 是区分大小写的。对于用户输入的搜索词，请使用 `icontains`。 |
| 点路径触发 `'x' is not an edge of 'y'` | 头段不是声明的边——遍历由 schema 驱动，即使值看起来像 FK。使用两个查询的 `in` 模式。 |
| 跨实体平均看起来不正确 | 聚合运行在**起始**实体的行上。从您想要平均的实体开始，或者按点路径分组并聚合起始实体字段。 |
| `execute` 返回行但缺少字段 | 您 `select`-ed 的字段不在实体中（拼写错误，或由作者隐藏）。从 `select` 中删除它，或者移除 `select` 以获取默认投影。 |

没有**结构化的错误包**。任何失败都是一个陷阱——修复查询并重试。
