# 财务洞察

使用此技能回答有关用户通过 Link 连接的财务数据的问题，包括：

- 近期交易记录
- 消费模式
- 账户余额
- 关联的钱包来源
- 基于用户财务数据的基本摘要

所有命令都是只读的。它们不会转移资金、发起支付、修改账户或暴露支付凭证。

## 安全与隐私

在用户使用所需来源操作进行身份验证之前，不要检索财务数据。

仅检索回答用户请求所需的数据。默认情况下，不要运行每个列表命令。

不要暴露敏感标识符、访问令牌、凭证或支付工具详细信息。在回答用户问题的程度上对财务信息进行摘要。

如果用户要求执行会转移资金的操作，请参考 `skills/create-payment-credential/SKILL.md`。

## 身份验证

在检索财务数据之前，检查用户是否已通过身份验证，以及当前会话是否具有所需的来源操作。

```bash
link-cli auth status --format json
```

当存在时，检查响应中的 `authorization_details` 字段，查找类型为 `"source"` 且包含所需操作的条目。当令牌端点未返回授权详细信息或身份验证来自 `LINK_ACCESS_TOKEN` 时，该字段可能不存在；在这种情况下，仅运行所需的最小数据命令，并按以下方式处理权限错误。

如果用户尚未通过身份验证，请启动一个仅请求获取请求数据所需来源操作的登录流程。如果用户已经通过身份验证，但缺少一个或多个所需来源操作，请使用 `auth upgrade` 而不是 `auth login`。`auth upgrade` 在用户批准额外访问权限时保留当前会话，并在批准成功后才替换它。

使用最小必需的来源操作：

- 通过 Link 处理的交易：`read_link_transactions`
- 从银行连接导入的交易：`read_external_transactions`
- 账户余额：`read_balances`
- 数据源详细信息和描述：`read_source_details`。此操作广泛有用，例如，如果您将来需要将交易或余额与特定账户名称关联。

如果用户提出需要多种数据类型的问题，请一次性请求所有相关操作。

需要所有财务数据类型的示例新登录：

```bash
link-cli auth login \
  --client-name "<your-agent-name>" \
  --source-actions read_link_transactions \
  --source-actions read_balances \
  --source-actions read_external_transactions \
  --source-actions read_source_details \
  --format json
```

向现有会话添加余额访问权限的示例：

```bash
link-cli auth upgrade \
  --client-name "<your-agent-name>" \
  --source-actions read_balances \
  --format json
```

将 `<your-agent-name>` 替换为代理或应用程序的清晰名称。向用户展示返回的 `verification_url`，然后按照响应中的 `_next` 指令操作或使用以下命令轮询：

```bash
link-cli auth status --interval 5 --max-attempts 60 --format json
```

在身份验证或访问升级成功之前，不要继续进行。如果批准过期、被拒绝或超时，请报告该结果，而不是重复启动新的授权流程。

## 选择正确的命令

使用能够回答用户问题的最小命令集。

| 用户询问关于 | 命令 |
|---|---|
| 近期购买、商家、消费、交易历史、收入、存款、订阅 | `link-cli transactions list` |
| 当前可用余额、账户余额、现金状况 | `link-cli balances list` |
| 已连接的账户、卡片、银行、钱包来源、来源元数据 | `link-cli sources list` |

示例：

- “我上个月在餐厅花了多少钱？” → 仅使用交易。
- “我的当前支票账户余额是多少？” → 仅使用余额。
- “哪些账户已连接？” → 仅使用来源。
- “总结我的现金状况和近期消费。” → 使用余额和交易。

## 输出格式

使用 JSON 进行代理可读的结构化输出。

```bash
link-cli transactions list --format json
link-cli balances list --format json
link-cli sources list --format json
```

默认的 `toon` 格式是供人类使用的。在解析、过滤、聚合或摘要结果时，请始终优先使用 `--format json`。

所有端点中的所有金额都是以货币最小单位表示的整数（例如，`152340` = $1,523.40 USD）。使用使用货币 ISO 4217 最小单位指数的货币感知格式化器格式化金额；不要假设每种货币都有两位小数或始终除以 100。

保持符号解释字段特定。只有 `transactions.amount` 使用负数表示资金离开账户（借记/购买），正数表示资金进入（贷记/存款）。不要将交易符号语义应用于余额字段；根据余额类型解释或过滤 `current`、`cash.available` 和 `credit.used`。

## 来源（概念）

**来源** 是连接到用户 Link 钱包的财务账户——银行账户、信用卡、储蓄账户等。每个来源都有一个唯一的 `id`（例如 `csmrpd_abc123`），其他端点可能将其作为 `source_id` 公开：

- 在 `transactions list` 中，`source_id` 指示交易所属的账户。
- 在 `balances list` 中，每个余额条目都包括一个 `source_id`，用于识别账户。
- 在 `sources list` 中，返回完整的来源元数据（名称、机构、类型、状态）。

使用 `source_id` 在不同命令之间关联数据——例如，查找特定账户的交易或匹配余额到其来源类型。不要通过猜测交易描述来将具有空 `source_id` 的交易分配给来源。

## 交易

使用交易来回答有关消费、收入、商家、类别、定期付款、存款或账户活动的问题。

```bash
link-cli transactions list --format json
```

常见选项：

```bash
link-cli transactions list --format json --start-date 2025-01-01 --end-date 2025-01-31
link-cli transactions list --format json --category groceries
link-cli transactions list --format json --origin external_connection
link-cli transactions list --format json --source <source_id> --source <source_id>
```

| 标志 | 描述 |
|---|---|
| `--start-date` | 仅检索此日期（YYYY-MM-DD）或之后的交易。 |
| `--end-date` | 仅检索此日期（YYYY-MM-DD）或之前的交易。 |
| `--category` | 按类别过滤。 |
| `--origin` | 按来源过滤：`link` 或 `external_connection`。 |
| `--source` | 按来源 ID 过滤（可重复）。 |

参见 [分页](#pagination) 以获取共享列表控制。

### 响应字段

| 字段 | 备注 |
|---|---|
| `amount` | 负数 = 资金离开账户（借记/购买），正数 = 资金进入（贷记/存款）。 |
| `origin` | `external_connection`（来自链接的银行/卡片）或 `link`（Link 本地交易）。 |
| `category` | 如果未分类，则可能为 `null`。 |
| `status` | API 提供的状态字符串。不要假设一组固定的值；观察到的值包括 `succeeded`。仅在其含义已知时解释或过滤状态。 |

对于交易摘要：

- 在计算总计之前，始终一致地规范化符号。
- 在可能的情况下，区分借记和贷记。
- 仅在相关时按商家、类别、账户、货币或时间段进行分组。
- 如果答案基于有限检索窗口，请说明。

## 余额

使用余额来回答有关当前账户余额或可用资金的问题。

```bash
link-cli balances list --format json
link-cli balances list --format json --source <source_id>
```

| 标志 | 描述 |
|---|---|
| `--source` | 按来源 ID 过滤（可重复）。 |

参见 [分页](#pagination) 以获取共享列表控制。

### 响应字段

| 字段 | 备注 |
|---|---|
| `type` | `cash`（银行/储蓄）或 `credit`（信用卡/信贷额度）。确定哪个子对象存在。 |
| `current` | 在待处理交易之前的余额。与可用资金不同。 |
| `cash.available` | 对象映射货币代码到可用资金（当前减去出站待处理加上入站待处理）。仅在 `type` 为 `cash` 时存在。 |
| `credit.used` | 对象映射货币代码到已使用的信贷。仅在 `type` 为 `credit` 时存在。 |
| `as_of` | 余额上次更新的时间——可能过时数小时或数天。 |

在摘要余额时：

- 保留货币。
- 除非用户明确要求且提供汇率数据，否则不要跨不同货币添加余额。
- 使用 `current` 字段作为余额的默认定义，除非用户的问题需要考虑待处理交易。
- 如果返回多个来源，按账户/来源进行汇总。

## 来源

使用来源来回答有关连接的钱包来源、链接账户或可用财务数据源的问题。参见 [分页](#pagination) 以获取共享列表控制。

```bash
link-cli sources list --format json
```

### 响应字段

| 字段 | 描述 |
|---|---|
| `id` | 唯一的来源标识符（与其他端点中的 `source_id` 相同）。 |
| `name` | 来源的显示名称。 |
| `type` | 来源类型（例如 `card`、`bank_account`）。 |
| `capabilities` | 对象指示可用数据。每个键（例如 `balances`、`transactions`）映射到一个包含 `status` 字段的对象（例如 `eligible`）。 |
| `external_connection.status` | 与外部机构的连接状态。 |
| `granted_actions` | 用户为此来源授予的操作列表。 |

在摘要来源时：

- 仅包含回答问题所需的非敏感元数据。
- 避免暴露完整的账户号码、凭证、令牌或支付工具详细信息。
- 优先使用机构、账户类型、来源状态和最后更新时间等标签（如果可用）。

## 分页

所有三个列表命令都支持相同的分页标志：

| 标志 | 描述 |
|---|---|
| `--limit` | 每页最大结果数（1-100）。如果可能需要多个页面，请优先使用 `100`。 |
| `--starting-after` | 在光标值之后获取下一页。 |
| `--ending-before` | 在光标值之前获取上一页。用于反向导航，而不是正常的前向收集。 |

JSON 响应包含 `data` 数组和可能包含 `has_more`。它们不提供单独的 next-cursor 字段。当 `has_more` 为 `true` 时，从 `data` 中的最后一个项目导出下一个光标：

| 命令 | 下一个光标 |
|---|---|
| `transactions list` | 最后一个交易的 `id`。 |
| `balances list` | 最后一个余额的 `source_id`。 |
| `sources list` | 最后一个来源的 `id`。 |

例如：

```bash
link-cli transactions list --format json --limit 100 --starting-after <last_transaction_id>
```

保持所有过滤器在跨页面时相同，仅更改 `--starting-after`。当 `has_more` 为 `false` 或不存在，或已检索到足够的数据以进行非穷尽查找时停止。如果 `has_more` 为 `true` 但 `data` 为空或所需的游标为空或缺失，请停止并报告分页无法继续。

除非用户的请求需要指定时间范围内的完整有界结果（例如总计），否则不要穷尽分页。

## 回答用户问题

在回答时：

- 首先陈述直接答案。
- 提及相关的时间范围和数据源。
- 注明任何限制，例如部分分页、缺失类别、待处理交易或不受支持的货币。
- 除非用户要求，否则避免转储原始记录和对象 ID。
- 优先使用简洁的摘要、总计和显著模式。

示例响应样式：

```text
您在 7 月份通过 12 笔交易在餐厅花费了 342.18 美元。最大的餐厅交易是在 7 月 18 日的 Example Bistro，金额为 86.40 美元。这是基于您连接的 Link 来源返回的交易。
```

## 错误处理

如果身份验证失败，请要求用户重新进行身份验证。

如果命令返回无数据，请说明在请求的范围内没有可用的匹配 Link 财务数据。

如果 CLI 返回表示缺少权限或来源操作的错误，请仅请求特定的缺失操作。当会话已通过身份验证时使用 `auth upgrade`，当会话未通过身份验证时使用 `auth login`，然后在获得批准后重试数据命令。

如果数据不完整或分页，请明确说明答案基于迄今为止检索到的数据。

## 安全限制

不要：

- 转移资金。
- 发起支付。
- 修改财务来源。
- 检索不相关的财务数据。
- 请求比所需更广泛的来源操作。
- 暴露凭证、令牌或完整的支付详细信息。
- 将不确定的派生洞察呈现为确定性。

要：

- 使用只读命令。
- 在检索前进行身份验证。
- 请求最小必需的来源操作。
- 使用 `--format json` 进行解析。
- 仅检索所需数据。
- 清晰地摘要并注明限制。
