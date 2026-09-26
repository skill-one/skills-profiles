# QianWenAI 使用说明

QianWenAI 账户、使用情况、计费和订阅的统一入口：认证状态、使用摘要、免费套餐配额、Token 计划、按量付费、计费摘要、模型成本明细、订阅状态、订单历史、团队席位和按量付费消费限额。

## 前置条件

- **QianWen CLI** 必须已安装。通过以下命令验证：

```bash
qianwen version
```

如果未安装，请运行：

```bash
npm install -g @qianwenai/qianwen-cli
```

需要 Node.js >= 18。

- **认证**：首次使用无需配置。CLI 会自动处理非 TTY 检测和安全登录（请参阅下方的认证流程）。

## 执行基准

本技能中的每个命令都适用以下规则：

- **CLI 版本基准：1.3.0。** 执行前，请检查 `qianwen version`。如果安装的版本低于 1.3.0，请勿调用可能缺失的命令（特别是 `billing` 和 `subscription` 组）；解释已安装的 CLI 早于基准，并等待用户确认升级后再继续。（这是每次运行的预执行检查——与下文“CLI 更新检查”部分不同，后者仅在用户明确询问 CLI 更新时适用。）
- **仅白名单。** 仅运行本文件中记录的命令和参数。切勿连接任意的 shell 字符串或将未检查的用户输入传递到命令行。
- **统一结果状态。** 将每个命令结果映射到五种状态之一：`success` / `partial` / `empty` / `confirmation_required` / `error`。切勿用模拟数据填充缺失或失败的结果——报告实际发生的情况。
- **仅来自 CLI 输出的 URL。** 仅呈现 CLI 返回的 URL（例如 `verification_url`）。切勿从名称或猜测中编造 URL。

## 认证流程（针对代理）

CLI 会自动检测非 TTY 环境，并安全降级——无需包装脚本。

### TL;DR — 3 步认证路径

1. `qianwen auth status --format json` → `authenticated: true` → 跳转到命令
2. `qianwen auth login --init-only --format json` → 提取 `verification_url` → 在浏览器中打开
3. `qianwen auth login --complete --format json` → 循环直到 `success` 事件

### 快速检查：是否已登录？

```bash
qianwen auth status --format json
```

如果 `authenticated: true` 且 token 未过期，则完全跳过登录。

### 推荐：两阶段登录

适用于所有环境（桌面、无头、远程容器）。

**步骤 1 — 初始化登录（非阻塞）：**

```bash
qianwen auth login --init-only --format json
```

立即退出。解析 stdout JSON `events` 数组：
- `already_authenticated` → 用户已登录，跳转到命令
- `device_code` → 提取 `verification_url` 并呈现给用户

在具有浏览器的桌面环境中，为用户打开 URL：

```bash
open "$VERIFICATION_URL"          # macOS
xdg-open "$VERIFICATION_URL"      # Linux
start "" "$VERIFICATION_URL"      # Windows
```

**步骤 2 — 立即开始循环（不要等待用户确认）：**

```bash
qianwen auth login --complete --format json
```

解析 stdout JSON `events` 数组：
- `success` → 登录完成，继续到命令
- `expired` → 设备代码过期，返回步骤 1
- `error` → 报告失败

### TTY 环境（交互式终端）

如果代理在 TTY（例如用户的终端）中运行，只需运行：

```bash
qianwen auth login
```

CLI 将自动打开浏览器并循环，直到授权完成。

### JSON 事件结构

`--init-only` 和 `--complete` 都输出单个 JSON 文档：

```json
{
  "events": [
    {"event": "device_code", "verification_url": "...", "expires_in": 300},
    {"event": "success", "authenticated": true, "user": {"aliyunId": "..."}}
  ]
}
```

事件类型：`already_authenticated`、`device_code`、`success`、`expired`、`error`、`pending`。

### 永远不要：

- ❌ 在运行 `--complete` 之前询问用户“您已完成授权？”
- ❌ 在循环之前等待用户确认——立即运行 `--complete` 后呈现 URL
- ❌ 在未完成的情况下重新运行 `--init-only`（这会创建一个新的设备代码并使之前的代码失效）

## 使用情况

所有命令都支持 `--format json` 以结构化、机器可解析的输出（**推荐默认**），以及 `--format text` 以干净的纯文本输出。

对于代理使用，**始终优先选择 `--format json`** 并解析 JSON 响应。仅在用户明确要求人类可读的纯文本时，才回退到 `--format text`。

切勿以编程方式解析 `table` 格式——它包含 ANSI 代码和 Unicode 边框。

### 认证命令

**`qianwen auth status`** — 检查当前认证状态

```bash
qianwen auth status --format json
```

**`qianwen auth logout`** — 在服务器端撤销会话并清除本地凭证

⚠️ **需要确认**：注销会破坏当前会话。始终先询问用户确认（`confirmation_required` 状态）；只有在明确确认后才能运行命令。

```bash
qianwen auth logout
```

### 使用情况命令

**`qianwen usage summary`** — 查看使用摘要（免费套餐、Token 计划、按量付费）

```bash
qianwen usage summary                      # 当前月份
qianwen usage summary --period last-month  # 上个月
qianwen usage summary --from 2026-03-01 --to 2026-03-31
qianwen usage summary --format json        # JSON 输出
```

**周期预设**：`today`、`yesterday`、`week`、`month`（默认）、`last-month`、`quarter`、`year`、`YYYY-MM`

**`qianwen usage breakdown`** — 查看模型使用明细

```bash
qianwen usage breakdown --model qwen3.6-plus --days 7
qianwen usage breakdown --model qwen3.5-plus --period 2026-03
qianwen usage breakdown --model qwen-plus --period 2026-03 --granularity month
qianwen usage breakdown --model qwen3.6-plus --format json
```

注意：明细仅显示按量付费消耗。免费套餐使用不包括在内——使用 `usage free-tier` 查看当前配额状态。

**`qianwen usage free-tier`** — 查看免费套餐配额详情

```bash
qianwen usage free-tier
qianwen usage free-tier --format json
```

**`qianwen usage payg`** — 查看按量付费使用情况和模型成本

显示当前周期按量付费消耗。对于历史计费周期，使用 `qianwen billing summary`（见下方的计费命令）。

```bash
qianwen usage payg
qianwen usage payg --format json
qianwen usage payg --period month --format json   # 推荐：当前月份按量付费
```

**`qianwen usage logs`** — 浏览分页调用日志（每请求历史），可按时间、模型和状态过滤

用于**请求级**问题——"哪些调用失败？"、"显示 4xx/5xx 错误"、"请求耗时多长？"、"最近调用了哪些模型？"、"查找此请求 ID"。这与 `usage summary`/`breakdown`（聚合 token/成本）不同——将故障诊断、延迟和调用历史问题路由到此处，而不是到摘要/明细。

```bash
qianwen usage logs --period 7d --format json
qianwen usage logs --period 24h --status 4xx --status 5xx --format json   # 最近客户端/服务器错误
qianwen usage logs --model qwen-plus --page 2 --page-size 50 --format json
qianwen usage logs --from 2026-07-25 --to 2026-08-07 --format json         # 明确范围（必须 ≤ 14 天）
qianwen usage logs --request-id 8c81644f-... --format json                # 精确查找
```

选项：
- `--from` / `--to` — 日期范围 (`YYYY-MM-DD` 或 RFC3339)
- `--period <preset>` — `1h`、`24h`、`7d`、`today`、`yesterday`、`week`、`month`、…（与 `usage summary` 相同的预设系列）。**⚠️ 解析的范围必须 ≤ 14 天。** `month`（月中之后）、`last-month`、`quarter` 和 `year` 等预设将超出限制并返回 `INVALID_ARGUMENT`。优先选择短预设：`1h`、`24h`、`7d`、`today`、`yesterday`、`week`。
- `--model <id>` — 按模型过滤；**可重复**（传递多个 `--model` 标志以包含多个模型）
- `--status <type>` — 状态过滤：`0`（已取消）、`2xx`（成功）、`4xx`（客户端错误）、`5xx`（服务器错误）；**可重复**
- `--request-id <id>` — 精确请求 ID；**设置时，所有其他过滤器将被忽略**
- `--page <n>`（默认 1）/ `--page-size <n>`（1..100）

**⚠️ 14 天范围限制**：解析的时间范围必须 **≤ 14 天**。任何超过 14 天的范围（无论通过 `--from`/`--to` 或长 `--period`）都会返回 `INVALID_ARGUMENT`（退出码 4，`"Time range cannot be longer than 14 days."`）。要扫描更长的历史，使用 ≤14 天的窗口，并连续使用 `--from`/`--to` 调用。这与 `usage summary`/`breakdown` 不同，后者接受多个月份范围。

**分页**：结果分页。要遍历窗口内的完整历史，从 `--page 1 --page-size 100` 开始，然后保持递增 `--page`，直到 `page × pageSize < totalCount`，直到检索到所有 `totalCount` 条目。

JSON 结构（每个 CLI 源——顶级 `totalCount` / `page` / `pageSize` / `period` / `items`；在 `items[]` 中，`errorCode` 仅在失败的调用中存在，`usages` 携带每请求的 token/字符消耗，对于失败/已取消的调用为空）：

```json
{
  "totalCount": 4,
  "page": 1,
  "pageSize": 20,
  "period": { "from": "2026-07-25", "to": "2026-08-07" },
  "items": [
    { "requestId": "8c81644f-...", "model": "wan3.0-video", "statusCode": 403, "durationMs": 548, "errorCode": "Forbidden.NoPermission", "usages": [] },
    { "requestId": "8e3a2c02-...", "model": "qwen3.8-max", "statusCode": 200, "durationMs": 956, "usages": [ { "type": "tokens", "total": 1820 } ] }
  ]
}
```

`period.from` / `period.to` 回显解析的窗口：日历预设和显式 `--from`/`--to` 日期渲染为 `YYYY-MM-DD`，而滚动预设（`1h`、`24h`、`7d`）渲染为 RFC3339 时间戳。当没有匹配的调用时，CLI 返回 `totalCount: 0` 和空的 `items: []`——将其映射到 `empty` 状态（不是错误）。

字段：`requestId`（与服务器端跟踪相关联）、`model`、`statusCode`（HTTP 风格代码——`2xx` 成功，`4xx` 客户端错误，`5xx` 服务器错误，`0` 已取消）、`durationMs`（调用延迟）、`errorCode`（失败原因，仅在非 2xx 时存在）、`usages`（每请求消耗；对于失败/已取消的调用为空）。使用 `statusCode` + `errorCode` 进行故障排除，使用 `durationMs` 进行延迟分析。

### 明细参数：如何思考它们

**三个独立维度——自由组合：**

`--model`（必需）+ **日期范围** + **粒度**

**模型范围：**
- `--model <id>` — 单个模型（例如 `qwen3.5-plus`）；**必需**

**日期范围** — 三种模式，根据用户如何描述周期选择：

| 模式 | 使用场景 | 如何工作 |
|---|---|---|
| `--period YYYY-MM` | 用户指定特定月份（“三月”、“上四月”） | 精确日历月份，从头到尾 |
| `--period <preset>` | 用户描述相对周期 | `last-month` = 上一个完整月份；`month` = 本月至今；`quarter` = 本季度至今 |
| `--days N` | 用户说“过去 N 天” | 从今天开始向后滚动窗口，自然跨越月份边界 |
| `--from YYYY-MM-DD --to YYYY-MM-DD` | 用户给出明确日期或命名季度/范围 | 完全控制，当其他模式不适用时使用 |

**粒度** — 确定结果的分组，不是范围：

- `day`（默认）— 每天一行；适用于发现使用峰值
- `month` — 每个月一行；适用于多个月份趋势
- `quarter` — 每个季度一行；适用于季度间比较

**经典示例：**

```bash
# 单个模型，单个月份，每日明细
qianwen usage breakdown --model qwen3.5-plus --period 2026-03

# 单个模型，过去 3 个月，每月摘要
qianwen usage breakdown --model qwen3.5-plus --days 90 --granularity month

# 单个模型，特定季度，季度汇总
qianwen usage breakdown --model qwen3.5-plus --from 2026-01-01 --to 2026-03-31 --granularity quarter

# 单个模型，本月，每日明细
qianwen usage breakdown --model qwen3.6-plus --period month
```

### 计费命令

**`qianwen billing summary`** — 包含 `YYYY-MM` 周期的计费总额

```bash
qianwen billing summary --from 2026-05 --to 2026-07 --format json
qianwen billing summary --charge-type payg --format json   # payg | subscription | all (默认)
```

`cycles` 涵盖 `--from`..`--to` 窗口中的**每个月份**，按顺序，没有间隙。每个周期都包含 `billingCycle`、`aftertaxAmount` 和 `settled` 标志。`chargeType` 是内部值——`all`、`prepaid` 为订阅，`postpaid` 为按量付费；金额为十进制字符串。

如果 `settled` 出现在 JSON 输出中，则表示该周期是否存在计费数据（`true` = 存在，`false` = 不存在）。当 `true` 时，报告 `aftertaxAmount` 为实际金额（包括 ¥0）。

```json
{
  "period": { "from": "2026-05", "to": "2026-08" },
  "chargeType": "all",
  "currency": "CNY",
  "cycles": [
    { "billingCycle": "202605", "aftertaxAmount": null, "settled": false },
    { "billingCycle": "202606", "aftertaxAmount": "3.710000", "settled": true },
    { "billingCycle": "202607", "aftertaxAmount": null, "settled": false },
    { "billingCycle": "202608", "aftertaxAmount": "0.000000", "settled": true }
  ],
  "totals": { "aftertaxAmount": "3.71" }
}
```

**`qianwen billing breakdown`** — 按模型（或 API 密钥）的 Top-N 消耗

```bash
qianwen billing breakdown --period month --group-by model --top 10 --format json
qianwen billing breakdown --group-by api-key --top 10 --format json
```

选项：`--group-by model|api-key`（默认 `model`），`--top <n>`（默认 10，最大 100），`--granularity day|month`（默认 `month`），`--charge-type all|subscription|payg`，以及 `--period` / `--from` / `--to` 日期范围。日粒度需要范围 ≤ 31 天；月粒度 ≤ 12 个月。

JSON 结构（每个 CLI 源，原始 `ConsumeBreakdown` 对象）：

```json
{
  "groupBy": "model",
  "period": { "from": "2026-07-01", "to": "2026-07-29" },
  "chargeType": "all",
  "rows": [
    { "groupKey": "qwen3.6-plus", "groupLabel": "qwen3.6-plus", "amount": "5.20" },
    { "groupKey": "qwen-plus", "groupLabel": "qwen-plus", "amount": "1.80" }
  ],
  "totalRows": 12,
  "totalAmount": "9.80",
  "currency": "CNY"
}
```

当范围跨越多个周期（例如几个月）时，JSON 将被切片为每个周期：`{ "groupBy", "dateRange": { "from", "to" }, "granularity", "chargeType", "slices": [ { "period", "rows", "totalAmount" } ], "currency" }`.

**`qianwen billing limit`** — 按量付费消费限额和警报配置

```bash
qianwen billing limit --format json
```

**只读**——此命令仅显示按量付费消费限额；CLI 不支持修改它。直接引导用户在控制台进行更改。

JSON 结构（每个 CLI 源，原始 `UsageLimit` 对象；`limitAmount` 可能当未设置时为 `null`）：

```json
{
  "status": "normal",
  "limitAmount": "500.00",
  "currency": "CNY",
  "alertThreshold": "80"
}
```

`status` 值：`normal` / `active` / `exceeded` / `warning` / `unknown`.

### 订阅命令

**`qianwen subscription status`** — 跨计划聚合订阅状态

```bash
qianwen subscription status --format json
qianwen subscription status --plan token --format json
```

JSON 结构（每个 CLI 源：`SubscriptionStatus` 字段加上 `diagnostics`; `recentOrders[].orderType` 和 `.status` 已映射为显示标签，如 `Purchase` / `Paid`; 可空字段可能为 `null`，数组可能为空）：

```json
{
  "isGray": false,
  "plan": "Token Plan Team Edition",
  "period": { "start": "2026-07-01", "end": "2026-08-01" },
  "quota": { "remaining": 21000, "total": 25000, "usedPct": 16 },
  "autoRenew": true,
  "renewable": true,
  "remainingDays": 3,
  "seatTiers": [
    { "specType": "standard", "seats": 2, "totalCredits": 50000, "remainingCredits": 42000, "usedPct": 16, "nextCycleFlushTime": "2026-08-01" }
  ],
  "creditPacks": [
    { "instanceId": "cp-xxxxxxxx", "totalCredits": 10000, "remainingCredits": 8000, "expiresAt": "2026-12-31" }
  ],
  "recentOrders": [
    { "orderId": "20260701xxxx", "orderType": "Purchase", "orderTime": "2026-07-01 10:00:00", "amount": "199.00", "currency": "CNY", "status": "Paid" }
  ],
  "diagnostics": []
}
```

状态由多个子调用组合而成；部分失败会出现在 `diagnostics` 中（每个条目：`api`, `errorCode`, `errorMessage”）——将此类结果映射到 `partial` 状态。如果 `data` 完全为 `null`，则命令退出码为 1 (`error` 状态)。

**⚠️ `nextCycleFlushTime` 仅在 `autoRenew` 为 true 时才表示配额重置。** 当 `autoRenew` 为 `false` 时，CLI 为每个席位 tier 返回 `nextCycleFlushTime: null`，因此非空值可以理解为“此日期重置到满额”。如果 `autoRenew` 为 `null`（未知续订状态），则该字段可能仍然包含日期——切勿将其视为保证重置。当 `autoRenew` 为 `false` 时，将 `period.end` 日期视为**到期**，例如“您的订阅将于 <日期> 到期；自动续订已关闭，因此除非您续订，否则计划将失效”而不是重置。

**`qianwen subscription orders`** — 订单历史（购买 / 续订 / 升级）

```bash
qianwen subscription orders --page 1 --page-size 100 --format json
qianwen subscription orders --from 2026-01-01 --to 2026-06-30 --type purchase --format json
```

选项：`--page <n>`（默认 1），`--page-size <n>`（默认 20，最大 100），`--type purchase|renew|upgrade`, `--from` / `--to` (`YYYY-MM-DD`)。

**分页**：结果分页。要获取完整历史记录，从 `--page 1 --page-size 100` 开始，然后保持递增 `--page`，直到 `pagination.page × pagination.pageSize < pagination.total`，直到检索到所有 `pagination.total` 订单。

JSON 结构（每个 CLI 源：`orderType` / `status` 已映射为显示标签；`amount` 是带货币符号的显示字符串）：

```json
{
  "orders": [
    { "orderId": "20260701xxxx", "orderType": "Purchase", "orderTime": "2026-07-01 10:00:00", "amount": "¥199.00", "currency": "CNY", "status": "Paid" }
  ],
  "pagination": { "page": 1, "pageSize": 100, "total": 231 },
  "diagnostics": []
}
```

**`qianwen subscription tokenplan status`** — Token 计划实例详情（周期、自动续订、席位摘要）

```bash
qianwen subscription tokenplan status --format json
```

JSON 结构（每个 CLI 源；`period` / `config` 可能是 `null`；`cycle.surplusValue` 是当前周期中席位的剩余配额）：

```json
{
  "product": "Token Plan Team Edition",
  "period": { "start": "2026-07-01", "end": "2026-08-01", "remainingDays": 3 },
  "autoRenew": { "enabled": true, "period": 1, "periodUnit": "M" },
  "renewable": { "canRenew": true, "interceptCode": null },
  "seatSummary": {
    "groups": [
      { "specType": "standard", "seats": 2, "assigned": 1, "totalValue": "50000", "surplusValue": "42000", "unit": "Credits", "nextCycleFlushTime": "2026-08-01" }
    ],
    "total": { "seats": 2, "totalValue": "50000", "surplusValue": "42000", "unit": "Credits" }
  },
  "diagnostics": []
}
```

如果所有四个数据字段都是 `null`，则命令退出码为 1 (`error` 状态)。

**⚠️ `seatSummary.groups[].nextCycleFlushTime` 仅在 `autoRenew.enabled` 为 true 时才表示配额重置。** 当 `autoRenew.enabled` 为 `false` 时，CLI 为每个组返回 `nextCycleFlushTime: null`。如果 `autoRenew` 本身是 `null`（状态未知），则可能仍然包含日期——切勿将其视为保证重置。当 `autoRenew.enabled` 为 `true` 时，才可以说“您的配额将在 <日期> 重置”。当 `autoRenew` 为 `false` 时，将 `period.end` 日期视为**到期**，例如“您的订阅将于 <日期> 到期；自动续订已关闭，因此除非您续订，否则计划将失效”而不是重置。

## 输出和代理显示规则

CLI 命令在代理/管道环境中默认返回 JSON（自动格式：TTY → table, pipe → json）。
**JSON 是代理的主要输出模式**——始终显式传递 `--format json`，解析结构化响应，然后向用户呈现人类可读的摘要。

### JSON 输出示例 (`--format json`)

```bash
qianwen usage summary --period month --format json
```

返回结构化 JSON，包含三个部分：

```json
{
  "period": { "from": "2026-04-01", "to": "2026-04-24 },
  "free_tier": [
    { "model_id": "qwen3.6-plus", "quota": { "remaining": 850000, "total": 1000000, "unit": "tokens", "used_pct": 15 }
  ],
  "token_plan": {
    "subscribed": true,
    "planName": "Token Plan Team Edition",
    "status": "valid",
    "totalCredits": 25000,
    "remainingCredits": 21000,
    "usedPct": 16,
    "resetDate": "2026-05-01",
    "addonRemaining": 8000
  },
  "pay_as_you_go": {
    "models": [
      { "model_id": "qwen3.6-plus", "usage": { "tokens_total": 480000 }, "cost": 0.38, "currency": "CNY" },
      { "model_id": "qwen-plus", "usage": { "tokens_total": 460000 }, "cost": 0.13, "currency": "CNY" }
    ],
    "total": { "cost": 0.51, "currency": "CNY" }
  }
}
```

### 文本输出示例 (`--format text`)

```plaintext
使用摘要  ·  2026-04-10

-- 免费套餐配额 -------------------------------------------------------
模型                剩余          总计          进度
qwen3.6-plus         850K tokens    1M tokens      85% 剩余
wan2.6-t2i           38 images      50 images      76% 剩余
--------------------------------------------------------------------------

-- Token Plan  ·  Token Plan Team Edition - Standard Seat  ·  valid-------
使用:      25K / 25K Credits
配额剩余: 100%
状态:     valid
重置:     2026-06-01
--------------------------------------------------------------------------

-- 按量付费 · 2026-04-01 → 2026-04-10 -------------------------------
模型                使用              成本
qwen3.6-plus         480K tok           ¥0.38
qwen-plus            460K tok           ¥0.13
--------------------------------------------------------------------------
总计                —                  ¥0.51
```

### ⚠️ 关键：如何向用户呈现输出

**使用 `--format json`（推荐代理）:**

1. **解析 JSON** 并提取用户问题的相关数据
2. **呈现人类可读的摘要**——不要向用户显示原始 JSON
3. **在摘要之后添加分析**——清晰分隔，用 `---`

**使用 `--format text`:**

1. **完全按 CLI 输出显示**——不要修改，不要重新格式化
2. **保留所有格式**——对齐、空格、进度条、分隔符
3. **仅在输出之后添加分析**——清晰分隔，用 `---`

**永远不要：**
- ❌ 在运行 `--complete` 之前向用户询问“您已完成授权？”
- ❌ 在循环之前等待用户确认——立即运行 `--complete` 后呈现 URL
- ❌ 在未完成的情况下重新运行 `--init-only`（这会创建一个新的设备代码并使之前的代码失效）

**✅ 正确 (JSON 模式):**
```
您的 QianWen 使用情况为 2026 年 4 月：

**免费套餐**: qwen3.6-plus 剩余 85% (850K / 1M tokens), wan2.6-t2i 剩余 76% (38 / 50 images).
**Token 计划**: 16% 使用 (21K / 25K Credits 剩余).
**按量付费**: ¥0.51 总计 — qwen3.6-plus ¥0.38, qwen-plus ¥0.13.

---

**💡 分析**: 您的 qwen3.6-plus 免费套餐剩余 85%...
```

**✅ 正确 (文本模式):**
```
[CLI 文本输出 - 完全按原样]

---

**💡 分析**: 您的 qwen3.6-plus 免费套餐剩余 85%...
```

**❌ 错误:**
```
这里显示您的使用情况:
- qwen3.6-plus: 850K tokens 剩余 (85% left)
```

## 退出代码

| 代码 | 含义              |
|------|----------------------|
| 0    | 成功              |
| 1    | 一般/使用错误  |
| 2    | 认证错误        |
| 3    | 网络错误        |
| 4    | 配置错误        |
| 130  | 中断              |

- 在非零退出代码的情况下，首先尝试解析 stdout 中的任何结构化 JSON——它可能包含可用的错误负载或部分结果。
- 在退出码 2（认证错误）: 引导用户完成认证流程，然后最多重试一次原始任务。**切勿循环登录尝试**。

## CLI 更新检查

当用户明确要求检查 CLI 更新（例如“检查 CLI 更新”, “检查 cli 版本”, “cli 有新版本吗”）:

1. 运行: `qianwen version --check`
2. 报告结果。

QianWen CLI 原生处理更新通知；在此技能中不需要额外的 stderr 信号处理。

## 实现说明

- **按量付费**: API 返回总使用情况（没有输入/输出分割）
- **Token 计划**: 在计划级别聚合信用消耗（没有按模型明细）
- **logout**: 在服务器端撤销会话并清除本地凭证（密钥库 + 文件）。服务器端调用是尽力而为的——本地注销总是成功的。
- **认证**: 使用 OAuth 2.0 设备授权授予与 PKCE。凭证在 OS 密钥库中存储（如果可用），否则使用加密文件回退。
- **breakdown --model 是必需的**: 与之前的 Python 实现不同，CLI 需要 `--model` 才能进行明细。要查询所有模型的使用情况，请使用 `qianwen usage summary`。
