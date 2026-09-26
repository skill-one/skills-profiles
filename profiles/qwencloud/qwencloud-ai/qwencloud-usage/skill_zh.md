# QwenCloud 使用说明

使用此技能进行账户认证、使用情况、计费、调用日志、配额、订阅、订单、席位以及PAYG支出限额管理。切勿伪造或模拟账户数据。

## 工作流程

1. 在执行任何操作之前，请阅读 [参考资料/cli.md](references/cli.md)。它是安装、认证流程、命令、参数、分页、输出模式和退出处理的唯一来源。
2. 仅阅读与请求相关的结果语义参考资料：
   - 使用摘要、免费套餐、PAYG、模型分解或请求日志：[参考资料/usage.md](references/usage.md)
   - 计费周期、成本分解或支出限额：[参考资料/billing.md](references/billing.md)
   - 订阅状态、订单或席位：[参考资料/subscriptions.md](references/subscriptions.md)
   - 登录、登出、过期凭证或认证事件：[参考资料/authentication.md](references/authentication.md)
3. 对于精确的 requestId 查询，直接查询，无需添加 `--from`、`--to` 或 `--period`，或询问用户日期。仅在用户明确要求时添加时间过滤器；参见 [参考资料/cli.md](references/cli.md)。
4. 根据下方的输出合同解释并显示结果。

## 输出合同

### 格式和展示

遵循 CLI 参考资料中的输出模式规则。仅展示与用户问题相关的可读信息，并在结果后放置可选分析。

不要在面向用户的输出中显示 Coding Plan。忽略 `coding_plan`、`codingPlanStatus` 及其子字段，包括“未订阅”占位符，即使由 CLI 返回。

### 结果规则

- 将结果分类为 `success`、`partial`、`empty`、`confirmation_required` 或 `error`。
- 如果 Top-N 限制省略了行、分页未完成或 CLI 参考资料的完整性检查失败，请使用 `partial`；切勿暗示数据完整。
- 对于免费套餐，当用户询问所有配额时，显示所有返回的模型。如果答案只显示部分，请说明显示/总数模型数量，标记为 `partial`，并包含来自 [参考资料/cli.md](references/cli.md) 的完整命令以查看所有免费套餐配额。提供更多显示的提议不能替代该命令。
- 当两个支持命令对看似相同记录返回冲突值时，显示每个值的来源和范围，并将结果标记为 `partial`。切勿无声地选择一个、合并它们或编造协调结果。

### 计费和订阅数据

- 使用操作返回的货币，切勿转换。仅对于计费周期摘要，显示其 `pretaxAmount`、`tax` 和 `aftertaxAmount` 值。
- 对于成本分解，仅显示返回的 `rows[].amount`、适用的扁平响应或切片级 `totalAmount` 和 `currency`。对于订阅状态或订单，仅显示实际存在的金额和货币字段。切勿合成缺失的 pretax、tax、after-tax 或货币字段。
- 在成本分解中，从模型排名中忽略 `groupKey=__tax__`，并将该行的返回金额单独显示为税。
- 仅从 `seatSummary.groups[]` 计算 Team 席位：对每个组使用 `max(seats - assigned, 0)`，然后求和。不要从历史席位实例列表推导当前容量。
- 不要重新计算返回的日期或货币金额。验证响应并应用上述展示规则。
- 在展示计费或订阅数据时，始终附加：“最终金额以控制台计费声明为准。”

### 产品语义

- Token 套餐配额和余额使用十进制积分。保留 JSON 返回的剩余和总积分的完整精度，无论编码为数字还是数字字符串；切勿四舍五入、截断或缩写。例如，显示 `63028.84805624` 而不是 `63,029`。这适用于使用摘要、订阅配额、套餐、席位和积分包；没有按模型分解的积分。
- 使用来自相同配额范围的精确值进行消耗比较。零的舍入使用百分比不能证明未消耗积分；不要从舍入显示中推断未使用状态或退款资格。
- Coding Plan 在 `per_5h`、`weekly` 和 `monthly` 窗口中使用聚合请求计数；它没有按模型分解。如果未订阅，其分支为 `{ "subscribed": false }`。
- PAYG 仅暴露总使用量，没有输入/输出拆分。
- 按模型分解仅适用于 PAYG。零或空的分解对免费套餐、Token 套餐或 Coding Plan 消耗无意义。
- 使用摘要具有 `period: { from, to }` 和以下产品分支：
  - `free_tier[]`：`model_id` 加上 `quota: null` 或 `quota: { remaining, total, unit, used_pct, status, resetDate }`。只有 `status=valid` 可用，并可能计入可用配额总数。将 `expire` 视为过期，将 `exhaust` 视为耗尽，即使 `remaining` 为正；未知状态或 `quota: null` 具有未知可用性。
  - `token_plan`：订阅时，`subscribed`、`planName`、`status`、`totalCredits`、`remainingCredits`、`usedPct` 和 `resetDate`；否则至少为 `{ "subscribed": false }`。`resetDate` 是下一个积分刷新日期（如果存在）；如果不存在，则报告刷新日期为未知。当订阅自动续订关闭时，请注意该计划在此日期后到期。
  - `coding_plan`：订阅时，`subscribed`、`plan` 和 `windows` 包含 `per_5h`、`weekly` 和 `monthly`，每个都有 `remaining`、`total` 和 `used_pct`；否则为 `{ "subscribed": false }`。
  - `pay_as_you_go`：`models[]` 条目具有 `model_id`、`usage`、`cost` 和 `currency`，以及 `total: { cost, currency }`。
