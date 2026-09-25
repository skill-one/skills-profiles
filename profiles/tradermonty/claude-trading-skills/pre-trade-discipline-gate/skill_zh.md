# 交易前纪律门

## 概述

在将计划的手动订单提交给经纪商之前，评估该订单是否应该进行。此技能读取本地清单，以及可选的市场状态、熔断机制和交易者记忆核心组件。它生成一个 `pre_trade_discipline_decision` 组件，并且可以将该组件链接回相关的论点，而不会更改论点审查计划。

该门被有意设置为离线状态。它不会提交订单、取消订单、调用经纪商 API 或获取市场数据。

## 使用场景

- 提交任何手动入场订单之前立即
- 当候选者已通过图表验证和头寸规模验证时
- 在最近的亏损后，以避免在冷却期内进行报复性交易
- 当工作流具有上游的 `exposure_decision` 和 `circuit_breaker_decision` 时
- 当您希望在后续的交易者记忆核心审查中看到清单遵守情况时

## 前置条件

- Python 3.9+
- 一个包含候选者级别清单答案的本地 JSON 或 YAML 答案文件
- 可选的 `trader-memory-core` 论点状态，位于 `state/theses/` 下
- 可选的 `exposure_decision` JSON，来自 `market-regime-daily` / `exposure-coach`
- 可选的 `circuit_breaker_decision` JSON，来自 `drawdown-circuit-breaker`

## 工作流

### 第一步：准备清单

创建一个包含候选者答案的 JSON 或 YAML 文件。只有可执行的手动订单意图会被门控制。观察列表和忽略意图会被记录为 `NO_ACTIONABLE_ORDERS`。

```json
{
  "candidates": [
    {
      "symbol": "AAPL",
      "thesis_id": "th_aapl_gm_20260703_0001",
      "order_intent": "ENTRY_READY",
      "entry_in_written_plan": true,
      "stop_predefined": true,
      "size_within_plan": true,
      "planned_risk_dollars": 500,
      "actual_risk_dollars": 500,
      "notes": "入场与记录的突破计划匹配。"
    }
  ]
}
```

可执行意图是 `ENTRY_READY`、`ACTIONABLE`、`ACTIONABLE_DAY1` 和 `MANUAL_ORDER`。非可执行意图，如 `WATCHLIST`、`DELAYED_EP_WATCH`、`PEAD_HANDOFF`、`IGNORE` 和 `REJECTED`，会被记录但不会创建订单权限。

为每个可执行的候选者提供 `planned_risk_dollars` 和 `actual_risk_dollars`。使用有限、非负的数字或数字字符串；零是有效的。将缺失值、布尔值、非数字字符串、`NaN`、无穷大和负值视为 `REVIEW_REQUIRED` 输入，并在提交订单前进行审查。

### 第二步：运行门

```bash
python3 skills/pre-trade-discipline-gate/scripts/check_pre_trade_discipline.py \
  --answers-file state/manual-entry-checklist.json \
  --state-dir state/theses \
  --market-regime-decision reports/exposure_decision_latest.json \
  --circuit-breaker-decision reports/circuit_breaker_decision_latest.json \
  --output-dir reports/pre-trade-discipline \
  --journal-dir state/journal/pre-trade-discipline
```

设置 `--as-of` 进行确定性测试或回填：

```bash
python3 skills/pre-trade-discipline-gate/scripts/check_pre_trade_discipline.py \
  --answers-file state/manual-entry-checklist.json \
  --as-of 2026-07-03T12:00:00-04:00
```

### 第三步：解释决策

| 决策 | 含义 |
|---|---|
| `GO` | 所有可执行的手动订单候选者都通过了清单和上游门 |
| `REVIEW_REQUIRED` | 输入缺失、未知或记录失败；在审查前不要提交订单 |
| `NO_GO` | 至少有一个可执行的候选者违反了纪律规则 |
| `NO_ACTIONABLE_ORDERS` | 文件不包含可执行的手动订单；什么都不要提交 |

默认情况下，CLI 对每个有效决策退出 `0`，并且仅在输入或运行时错误时退出 `1`。使用 `--fail-on-non-go` 当 shell 管道应该对任何非 `GO` 决策返回 `2` 时。

## 规则

当门阻止可执行的候选者时：

- 入场未在书面计划中确认
- 止损未预定义
- 规模未在计划内确认
- 任何风险美元字段缺失或不是有限、非负数字 (`REVIEW_REQUIRED`)
- `actual_risk_dollars` 超过 `planned_risk_dollars`
- 交易者记忆核心在报复窗口内有亏损退出或部分亏损
- exposure-coach 建议为 `REDUCE_ONLY` 或 `CASH_PRIORITY`
- drawdown-circuit-breaker 建议为 `COOLDOWN`、`HALTED` 或 `TRADING_HALTED`

缺失或无法读取的市场状态或熔断机制组件会为可执行订单产生 `REVIEW_REQUIRED`。如果没有可执行的订单，结果仍然是 `NO_ACTIONABLE_ORDERS`。

## 输出

脚本会写入：

- `pre_trade_discipline_decision_YYYY-MM-DD_HHMMSS.json`
- 匹配的 markdown 报告（除非设置了 `--json-only`）
- 在 `--journal-dir` 提供时，在 `state/journal/pre-trade-discipline/` 下写入 JSONL 记录行

每个候选者结果都包括一个 `checklist_answers` 对象，其中包含用于决策的书面计划、止损、规模、风险美元和备注答案，以便后续审查可以审计订单时的答案。无效的风险美元值被存储为 JSON `null`。有效的 JSON 小数如果无法通过二进制浮点数来回转换，则保留为数字字符串，以防止下溢或精度损失改变门决策。

如果候选者包含 `thesis_id` 且 `--state-dir` 提供，JSON 报告会使用交易者记忆核心的 `link_report` 链接到论点 `linked_reports` 列表中。该技能不会调用 `mark_reviewed`，也不会更改监控审查日期。

## 资源

- `scripts/check_pre_trade_discipline.py` - 主 CLI 和规则引擎
- `references/discipline_gate_framework.md` - 规则定义和集成说明
- `skills/trader-memory-core/schemas/thesis.schema.json` - 论点状态模式

## 关键原则

1. **仅手动执行** - 输出是一个预经纪商清单门，不是订单路由器。
2. **优先书面计划** - 没有书面入场计划、止损或规模确认意味着不进行手动入场。
3. **与生产者兼容的状态读取** - 报复性风险检测遵循交易者记忆核心的时间戳和结果行为。
4. **无审查副作用的记录** - 门将报告链接到论点，而不会推进审查计划。
