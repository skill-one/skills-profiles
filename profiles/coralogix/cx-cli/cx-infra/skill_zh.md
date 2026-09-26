# 基础设施资源技能

使用此技能来发现和检查**基础设施资源**——它们的存在情况、健康状况及其原始数据内容。

## CLI 命令

| 命令 | 目的 | 关键标志 |
|---|---|---|
| `cx infra resources types` | 列出可用的资源类型（类别/类型对） | - |
| `cx infra resources list` | 列出资源，可通过任何可过滤属性进行缩小 | 所有可选：`--match-all NAME=VALUE`, `--match-any NAME=VALUE`, `--category`, `--type`, `--start-row`, `--end-row` |
| `cx infra resources filters` | 列出资源可被过滤的属性及其接受的值 | `--category`, `--type` |
| `cx infra resources health-history <resource-id>` | 单个资源的每日健康样本，按时间顺序排列（最早优先） | - |
| `cx infra resources raw-data <resource-id>` | 资源的原始文档（JSON 格式） | - |

- 所有命令都是**只读**的，并支持 `-o json` / `-o toon` 用于结构化输出。
- **多配置文件分发给 `types`、`filters` 和 `list` 命令**。在这些命令上重复 `-p <profile>` 以跨账户比较舰队。`health-history` 和 `raw-data` 接收资源 ID，它仅限于一个团队，因此它们**拒绝**多个 `-p` 标志——为每个配置文件单独运行它们。
- **过滤需要两个标志**。每个 `--match-all` 必须匹配；至少一个 `--match-any` 必须匹配；这两个组使用**AND**运算符组合。因此 `--match-all OS=linux --match-any Health=Critical --match-any Region=eu-west-1` 表示 `OS=linux AND (Health=Critical OR Region=eu-west-1)`。
- **逗号列出单个属性的多值，而标志决定其含义**。在 `--match-any` 中，它们是备选项——任何一个匹配：`--match-any Region=eu-west-1,us-east-2`。在 `--match-all` 中，每个值都必须匹配，这是如何同时缩小到两个子字符串的方法：`--match-all 'Name=*alert*,*processing*'` 查找同时包含这两个名称的资源。单个值属性不能等于两个值，因此对于**任何值**，请使用 `--match-any`。
- **一个属性属于且仅属于一个标志**。在标志内重复它，或在两个标志中命名它都会被拒绝——在逗号后列出其值。
- **除了一个缩小输入外，没有什么是必需的**。`--category` 和 `--type` 是普通过滤器，不是先决条件，因此 `--match-all Health=Critical` 单独工作。命名 `--match-all`、`--match-any`、`--category` 或 `--type` 中任何一个的请求都会被拒绝。
- **`Category` 和 `Type` 不是可过滤属性**。它们选择请求涵盖的资源类型，有自己的标志，并且永远不会出现在 `filters` 输出中——因此没有 `--match-all Category=Hosts`，使用 `--category Hosts`。
- **确切值区分大小写；通配符值不区分**。`OS=linux` 匹配，而 `OS=Linux` 返回空结果，但 `Name=*checkout*` 和 `Name=*Checkout*` 是相同的查询。`filters` 仅列出固定集的值，因此对于自由文本，要么从行的 `columns` 中获取拼写，要么使用通配符。无论哪种方式，`status` 值都不区分大小写地匹配。
- **0 行是一个答案，而不是失败**。一个有效的属性如果简单地未填充则匹配不到任何内容；不要重试或重写查询。拼写错误的属性或超出集合的值会被直接拒绝，并命名接受的值。
- **`filters` 告诉你每个属性的三件事**。`kind` 是值的类型——`string` 表示自由文本，`status` 表示固定集，`number`、`bool` 和 `date` 表示它们自身。`values` 列出固定集的接受值——传递其中一个，拼写与 `filters` 报告的相同。`wildcard` 告知是否在值中接受 `*`——只有 `string` 属性接受一个，并且它匹配值中的任何位置：`--match-all 'Name=*checkout*'`——引号它，或者 shell 会展开 `*`。
- **`--name-filter` 和 `--scope` 是遗留标志，并独立于其他标志**。两者都需要 `--category` 和 `--type`，并且都不能与 `--match-all` 或 `--match-any` 组合。使用 `--scope` 通过 `service`、`environment` 或 `team` 缩小范围；使用过滤器标志进行其他所有操作——`--match-all 'Name=*web*'` 是相同的查询，与 `--name-filter web` 相同。
- 分页：`--start-row` / `--end-row` 定义一个行窗口（`--end-row` 是**排他性**的）；默认是前 100 行，省略 `--end-row` 仅提供从 `--start-row` 开始的 100 行。在窗口中（0-100，100-200，…）分页大型舰队。**`list` 命令不会为你分页**——舰队可以包含数十万资源，因此它返回一个窗口并报告总数。
- **窗口不能超过 10,000 行**。API 会拒绝任何 `start-row + rows` 超过 10,000 的请求，因此即使 `total_count` 报告其真实大小，分页也无法枚举大于该大小的舰队。在任何情况下，缩小结果以适应——添加 `--match-all` 属性，或一个 `--type`——并在每个子集中分页，而不是尝试遍历整个列表。
- `list` 将其行包装在信封中（`total_count`、`returned_count`、`resources`）——其他子命令返回裸数组。`total_count` 是跨舰队的匹配计数，独立于窗口。在推理行之前检查它：保持分页，直到 `start_row + returned_count < total_count`，如果它超过你可以分页到的范围，请缩小查询而不是信任部分答案。
- 传递资源 ID **必须与 `list` 返回的完全一致**（引号它们——它们包含 `:` 和 `=`）；CLI 会为您进行 URL 编码。

## 检查工作流

三个步骤，并且仅因为每个步骤都提供下一个步骤所需的输入：
`filters` 提供属性名称及其接受的值，`list` 提供 `resource_id`。回答“`web-server-1` 是否健康？”是这三个调用——不多不少。

1. **发现可以过滤的内容**——属性名称及其接受的值是按资源类型动态的，因此永远不要猜测。为所有类型组合省略两个标志：

   ```bash
   cx infra resources filters -o json
   ```

   `cx infra resources types -o json` 列出 `(category, type)` 对，当你需要它们而不是属性时。

2. **列出资源**，通过任何 `filters` 提供的属性缩小：

   ```bash
   cx infra resources list --category Hosts --type EC2_Instances \
     --match-all Health=Critical -o json
   ```

3. **使用步骤 2 中的 `resource_id` 检查单个资源**。状态是 `Healthy`、`Critical` 或 `Unmonitored`，每天一个样本，按时间顺序排列：

   ```bash
   cx infra resources health-history "1001234:host_id=i-abc123" -o json
   ```

   `raw-data` 是此步骤的**替代方案**，而不是后续步骤——当您需要特定于源的详细信息而不是健康信息时，请使用它。

## 示例

### 一个区域中的不健康主机

```bash
# 健康是一个固定集，因此首先使用 `filters` 获取接受的值
cx infra resources filters --category Hosts -o json | jq '.[] | select(.name == "Health")'

cx infra resources list --category Hosts \
  --match-all Health=Critical --match-all Region=eu-west-1 -o json \
  | jq '.resources[] | {name, type}'
```

### 每个名称包含子字符串的资源

```bash
# `filters` 报告 `Name` 的 `wildcard: true`，因此 `*` 是接受的
cx infra resources list --match-all 'Name=*checkout*' -o json \
  | jq '.resources[] | {name, category, type}'
```

### 两个属性中的任何一个，任何资源类型

```bash
# --match-any 跨属性 OR；不需要类别或类型
cx infra resources list \
  --match-any Name=coredns --match-any Namespace=kube-system -o json \
  | jq '.resources[] | {name, category, type}'

# 同一个属性的多个值使用逗号形式，而不是第二个标志
cx infra resources list --match-any Namespace=kube-system,observability -o json

# 在 `--match-all` 中相同的逗号需要所有值：同时包含这两个名称的资源
cx infra resources list --match-all 'Name=*alert*,*processing*' -o json
```

### 仅 id 和名称

```bash
# 行位于 `.resources` 下——`list` 返回一个信封
cx infra resources list --category Hosts --type EC2_Instances -o json \
  | jq '[.resources[] | {resource_id, name}]'
```

### 检查舰队大小，以及一个窗口是否覆盖了它

```bash
cx infra resources list --category Hosts --type EC2_Instances -o json \
  | jq '{total_count, returned_count}'

# 下一个窗口，如果存在
cx infra resources list --category Hosts --type EC2_Instances \
  --start-row 100 --end-row 200 -o json
```

### 查找资源何时变为临界

```bash
# health-history 返回裸数组，因此此处没有 `.resources`
cx infra resources health-history "1001234:host_id=i-abc123" -o json \
  | jq '[.[] | select(.status == "Critical")]'
```

### 读取原始资源文档

```bash
# 特定于源的详细信息：标签、实例元数据、配置
cx infra resources raw-data "1001234:host_id=i-abc123" -o json
```

## 关键原则

- **先发现后过滤**——永远不要猜测属性名称或状态值；从 `cx infra resources filters` 开始，它列出了两者。
- **引号资源 ID 并按原样传递**——它们包含 `:`, `|` 和 `=`；CLI 处理 URL 编码。
- **缺少原始文档不是错误**——`raw-data` 退出 0 并在 **stdout** 发出空结果：`[]` 在 `json` 中，`[0]:` 在 `agents` 中，以及文本中的 `No raw data found.`。只有 `no raw data for this resource` 被发送到 `stderr`。将空 stdout 结果解析为干净的缺失文档，而不是失败——并且不要期望 stdout 为空白。
- **使用 `-o json` 与 `jq` 进行过滤**；使用 `-o toon` 在代理上下文中进行标记高效的输出。
- **行窗口按配置文件应用**——多配置文件 `list` 添加 `counts_by_profile` 拆分，因此为每个配置文件针对其自己的 `total_count` 分页，而不是汇总。
- **资源 ID 永远不会跨越配置文件**——它嵌入团队 ID (`1001234:host_id=…`)，因此一个账户中的 ID 不能在另一个账户中解析。当多配置文件 `list` 出现值得检查的内容时，注意其 `profile` 字段，并为该单个配置文件查询其健康或原始数据。
- **基础设施健康是其自身的概念**——`Healthy`/`Critical`/`Unmonitored` 状态由基础设施域计算，与 Service Catalog 健康不同。将它们与遥测信号相关联；不要将它们视为可互换的。
- **`resource_id` 永远不会离开此技能**——仅将其传递给 `health-history` 和 `raw-data`。对于其他所有命令，围绕资源 `name` 或 `Service` 属性值进行转换。

## 相关技能

使用资源的**名称**或**Service**属性值桥接到这些技能——永远不要使用资源 ID，因为只有此技能理解它：

- **`cx-telemetry-querying`** — `cx search-fields "<name>" -s value` 发现哪些日志/跨度字段包含资源名称；`cx logs "filter $l.subsystemname == '<service>'"` 查询服务的遥测。将一个 `Critical` 健康日与错误日志或 CPU 指标相关联。
- **`cx-alerts`** — `cx alerts list --name "<name-or-service>"` 找到通过子字符串匹配资源或其服务的警报定义。
- **`cx-dashboards`** — `cx dashboards search "<name-or-service> ..."` 和 `cx dashboards query-search --description "..."` 按语义查找仪表板；与 `search-fields -s value` 配合使用，然后 `query-search --field` 包含资源名称的确切字段。
