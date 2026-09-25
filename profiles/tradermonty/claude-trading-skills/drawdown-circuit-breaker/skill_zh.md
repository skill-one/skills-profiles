# 收盘断路器

## 概述

根据账户级别的已实现盈亏和最近的终端交易结果，评估交易者今天是否应承担新的交易风险。此技能仅读取交易者记忆核心的论点 YAML 文件。它生成一个 `circuit_breaker_decision` 产物，与市场端的 `exposure_decision` 从 exposure-coach 补充。

断路器是一个建议和记录工具。它不能替代人类判断，并且它不会执行经纪商端的阻止或自动订单拒绝。

## 使用时机

- 在筛选或调整任何新的波段交易候选之前
- 在亏损交易或部分削减之后，检查是否处于冷却状态
- 在每日计划期间，当交易者记忆核心包含最近的已关闭或部分关闭头寸时
- 作为工作流网关，在波段机会每日进入候选生成之前
- 在审查是否已突破每日、每周或每月的亏损限额时

## 前置条件

- Python 3.9+
- 本地的交易者记忆核心论点 YAML 文件，通常在 `state/theses/`
- 美元计价的账户规模
- 无需 API 密钥或网络访问

## 工作流

### 第 1 步：读取交易者记忆状态

将脚本指向论点状态目录：

```bash
python3 skills/drawdown-circuit-breaker/scripts/check_circuit_breaker.py \
  --state-dir state/theses \
  --account-size 100000 \
  --output-dir reports/
```

脚本扫描每个 `th_*.yaml` 文件，并从每个论点的 `status_history[]` 分类账条目中读取已实现盈亏。它不使用 `_index.json` 来读取盈亏，因为索引是一个轻量级的查找文件，并且不包含所需的已实现盈亏分类账。

验证每个文件后，脚本按大小写敏感的、去除空白的 `thesis_id` 对有效论点进行分组。如果两个或多个有效文件共享一个 ID，它将排除整个重复组，从盈亏和亏损连续计算中排除，报告每个实际源路径，并返回 `PARTIAL` + `HALTED`，直到重复状态被修复并且决策重新运行。`metrics.theses_scanned` 仅计算具有唯一 ID 的接受的论点。

如果状态目录缺失或为空目录，该技能返回 `TRADING_ALLOWED` 并带有 `data_quality: EMPTY_STATE`，以便新用户不会被缺乏历史记录而阻止。如果配置的状态路径存在但不是目录，该技能将因不完整的状态数据而关闭失败。

如果状态存在，但必须跳过某个论点、分类账事件或终端结果，或与另一个记录值冲突，该技能将因 `data_quality: PARTIAL`、`recommendation: HALTED` 和 `incomplete_state_data` 规则而关闭失败。在修复警告并重新运行之前，不要承担新的风险。唯一的可恢复例外是针对没有已实现盈亏分类账条目的遗留论点的有限终端 `outcome.pnl_dollars` 回退；它仍然可见为 `PARTIAL`，但本身不会覆盖计算出的建议。对于 `ACTIVE`、`PARTIALLY_CLOSED`、`CLOSED` 和 `INVALIDATED` 论点，每个历史事件必须是一个具有识别 `status` 和可解析 `at` 的对象，并且最后的历史状态必须与论点状态匹配。`ACTIVE` 和 `PARTIALLY_CLOSED` 论点还必须携带条目实际值；`PARTIALLY_CLOSED` 必须携带一个头寸。格式错误、过时或骨骼化的生命周期历史将取消终端回退并停止。形状如分类账的事件，如果 `realized_pnl` 缺失、未分类或非有限，则停止而不是被强制转换。

### 第 2 步：评估断路器规则

默认规则如下：

| 规则 | 默认值 | 触发状态 | 释放 |
|------|---------|-----------------|---------|
| 每日最大亏损 | 账户的 2.0% | HALTED | 下一个 ET 工作日 |
| 亏损连续冷却 | 2 个终端亏损论点 | COOLDOWN | 最新亏损退出后的 24 小时 |
| 每周回撤停止 | 账户的 5.0% | HALTED | 下一个星期一 ET |
| 每月回撤停止 | 账户的 8.0% | HALTED | 下个月的第一天 ET |

日、周和月边界使用 `America/New_York`。来自 `trader-memory-core` 的仅日期生产者时间戳在命名的 ET 日期上计算。设置 `--as-of` 以进行确定性评估；仅日期的 `--as-of` 值覆盖整个 ET 日，而时间戳值在该时间后排除未来事件：

```bash
python3 skills/drawdown-circuit-breaker/scripts/check_circuit_breaker.py \
  --state-dir state/theses \
  --account-size 100000 \
  --as-of 2026-07-02T12:00:00-04:00 \
  --output-dir reports/
```

### 第 3 步：在需要时覆盖阈值

在 CLI 上覆盖单个阈值：

```bash
python3 skills/drawdown-circuit-breaker/scripts/check_circuit_breaker.py \
  --account-size 100000 \
  --max-daily-loss-pct 1.5 \
  --losing-streak-n 3 \
  --cooldown-hours 48 \
  --weekly-drawdown-pct 4 \
  --monthly-drawdown-pct 6
```

或提供一个 JSON 配置文件：

```json
{
  "max_daily_loss_pct": 1.5,
  "losing_streak_n": 3,
  "cooldown_hours": 48,
  "weekly_drawdown_pct": 4.0,
  "monthly_drawdown_pct": 6.0
}
```

CLI 参数覆盖配置文件值。

### 第 4 步：解释决策

将生成的决策用作新交易风险的工作流网关：

| 建议 | 含义 |
|----------------|---------|
| TRADING_ALLOWED | 没有激活的断路器规则；新的交易风险可以继续通过其余工作流 |
| COOLDOWN | 不要开新头寸；继续管理现有头寸并审查最近的亏损 |
| HALTED | 因回撤限额激活或账户状态数据不完整而停止新条目；在继续之前修复/重新运行任何数据警告 |

现有头寸管理仍然是人类决策。断路器旨在防止在已实现损失后风险升级，而不是强制清算。

基于时间的规则带有 ISO 8601 `active_until`。非基于时间的 `incomplete_state_data` 规则使用 `active_until: null`；其 Markdown 报告说停止持续到状态被修复并且决策重新运行。

## 输出格式

脚本写入 `circuit_breaker_decision_YYYY-MM-DD_HHMMSS.json` 以及（除非设置了 `--json-only`），一个匹配的 markdown 报告。

```json
{
  "schema_version": "1.0",
  "generated_at": "2026-07-02T16:00:00+00:00",
  "as_of_date": "2026-07-02",
  "recommendation": "COOLDOWN",
  "triggered_rules": [
    {
      "rule": "losing_streak_cooldown",
      "threshold": 2,
      "observed": 2,
      "active_until": "2026-07-02T15:30:00-04:00",
      "detail": "2 个连续亏损关闭；最后一次亏损退出 2026-07-01T15:30:00-04:00."
    }
  ],
  "metrics": {
    "realized_pnl_today": 0.0,
    "realized_pnl_wtd": -250.0,
    "realized_pnl_mtd": -250.0,
    "consecutive_losses": 2,
    "last_loss_exit_at": "2026-07-01T15:30:00-04:00",
    "theses_scanned": 12
  },
  "account_size": 100000.0,
  "config": {
    "max_daily_loss_pct": 2.0,
    "losing_streak_n": 2,
    "cooldown_hours": 24.0,
    "weekly_drawdown_pct": 5.0,
    "monthly_drawdown_pct": 8.0
  },
  "data_quality": "OK",
  "warnings": [],
  "rationale": "最近的亏损关闭触发了冷却。避免新条目，直到冷却到期。"
}
```

## 交易所日历契约

在运行检查器之前安装 `requirements.txt`。每日、每周和每月停止日期使用实际的 XNYS 会话。`active_until` 保持兼容性：停止在下一个符合条件的会话日期的 00:00 America/New_York 结束，而不是在该会话的开盘钟。使用 `--as-of` 进行确定性评估。

## 资源

- `scripts/check_circuit_breaker.py` - 主 CLI 和规则引擎
- `references/circuit_breaker_framework.md` - 规则定义、默认值和数据源说明
- `skills/trader-memory-core/schemas/thesis.schema.json` - 论点状态的源模式

## 关键原则

1. **仅已实现损失** - 使用记录的已实现盈亏，而不是未实现盈亏或论点级别的累积字段进行每日计算。
2. **生存优先** - 断路器存在是为了防止在亏损后风险升级。
3. **建议而非自动执行** - 输出通知工作流网关；它不会下单、取消或阻止经纪商订单。
4. **不完整状态时关闭失败** - 空状态允许新用户开始，但格式错误、丢弃、冲突或非有限的风险数据返回 `PARTIAL` + `HALTED` 而不崩溃。有限的遗留结果回退报告为可恢复的 `PARTIAL` 并保持非阻止。
