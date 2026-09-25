# 期货仓位计算器

## 概述

Shapiro 管道步骤 4：根据账户风险预算和经过验证的合约规格（乘数、最小变动价位、最小变动价值），将方向、入场价和止损价转换为合约数量。这是一个全新的、独立的技能，与 `position-sizer` 不同——期货合约是杠杆化的、基于乘数的工具，其每点价值差异巨大（0.25 美元的变动在 ES 上是 12.50 美元，在 NQ 上是 5.00 美元，在 ZB 上是 31.25 美元）；重用股票份额计算器来计算期货仓位会导致无声的错误仓位。

调整交易规模的两种方法：

- **模式 A（显式）**：直接提供 `--symbol --direction --entry --stop`。
- **模式 B（网关交接）**：提供 `--gate-json <contrarian-setup-gate 报告> --entry`。方向和止损（网关的 `invalidation_level`）来自网关的 `READY_FOR_PLAN` 报告——计算器永远不会计算网关未确认为 READY 的设置，并且永远不会在提供 `--gate-json` 时接受显式的 `--direction`/`--stop`（网关在提供时具有权威性）。

`--entry` 在两种模式下都是必需的——这个技能和网关都不会推导入场价；操作员提供它。

## 使用场景

- 在 `contrarian-setup-gate` 达到 `READY_FOR_PLAN` 状态后，需要为确认的方向和止损计算合约数量
- 用户询问“我应该交易多少 ES/NQ/GC/CL/... 合约？”
- 用户有一个期货交易想法，具有已知的入场价和止损价，并希望进行基于风险的调整
- 用户希望在调整前检查符号的已验证合约规格（乘数/最小变动价位/最小变动价值）（`--list-specs`）

## 前置条件

- Python 3.9+，仅使用标准库——没有 API 密钥，完全离线
- 一个方向、入场价和止损（模式 A），或一个具有 `setup_status: READY_FOR_PLAN` 的 `contrarian-setup-gate` JSON 报告（模式 B）
- 对于核心表格外（已验证的 23 个市场）的符号：其乘数、最小变动价位和报价货币（三者必须一起提供）

## 工作流程

### 第 1 步：计算仓位

**模式 A -- 显式：**

```bash
python3 skills/futures-position-sizer/scripts/futures_position_sizer.py \
  --symbol ES --direction LONG --entry 5000.25 --stop 4980.00 \
  --account-size 100000 --risk-pct 1.0 \
  --output-dir reports/ --format both
```

**模式 B -- 网关交接：**

```bash
python3 skills/futures-position-sizer/scripts/futures_position_sizer.py \
  --gate-json reports/contrarian_setup_gate_B6_2026-07-15.json \
  --entry 1.3400 \
  --account-size 100000 --risk-pct 1.0 \
  --output-dir reports/ --format both
```

在模式 B 中可以省略 `--symbol`——它从网关报告中获取。如果两者都提供，它们必须匹配（否则 `gate_symbol_mismatch`）。`--direction`/`--stop` 与 `--gate-json` 一起被拒绝（使用错误，退出 2）——只传递一种模式，不要同时传递。

### 第 2 步：读取结果

| `sizing_status` | 含义 |
|---|---|
| `SIZED` | `contracts` >= 1；`total_risk_usd`/`risk_pct_of_account` 是实际承担的风险 |
| `NO_TRADE` | 永远不会崩溃——始终携带 `no_trade_reason`。见下方的原因词汇表 |

来自 `risk_below_one_contract` 的 `NO_TRADE` 结果仍然报告完整的风险计算（每合约风险、风险预算、止损距离）——账户在这个风险百分比和止损距离下无法负担一个合约；扩大止损、增加风险 % 或跳过交易。

### 第 3 步：检查警告

`warnings`（顶层列表）永远不会阻止计算——它标记值得审计的条件：`risk_pct_above_2`（风险高于 2% 指导方针）、`off_tick_grid_entry`/`off_tick_grid_stop`（非债券符号的价格不在最小变动价位上——合法的中间报价，但值得再看一眼）。

### 第 4 步：检查已验证合约规格表

```bash
python3 skills/futures-position-sizer/scripts/futures_position_sizer.py --list-specs
```

打印完整的 23 市场核心表（乘数、最小变动价位、最小变动价值、货币、交易所）——来自官方交易所合约规格页面——见 `references/futures-contract-specs.md` 获取每行来源 URL 和验证日期。

## 示例：债券离格保护（32 分位 -> 小数）

债券/票据期货（ZT、ZF、ZN、ZB）以点的分数报价（32 分位，或 32 分位的 32 分位），通常用撇号表示：`110'16` 表示 `110 + 16/32 = 110.50`。输入 `110.16` 而不是——将撇号后的数字读作小数分——是一个经典、无声、错误的金钱计算错误：`110.16` 根本不在 ZB 的最小变动价位上（`0.03125` = 1/32）。

```bash
# 错误——110.16 不在 1/32 网格上；这几乎肯定是
# 错误输入的 "110'16"（意思是 110.50）。退出 2，不写入报告：
python3 skills/futures-position-sizer/scripts/futures_position_sizer.py \
  --symbol ZB --direction LONG --entry 110.16 --stop 108.00 \
  --account-size 100000 --risk-pct 1.0

# 正确——小数点，不是原始 32 分位数字：
python3 skills/futures-position-sizer/scripts/futures_position_sizer.py \
  --symbol ZB --direction LONG --entry 110.50 --stop 108.00 \
  --account-size 100000 --risk-pct 1.0
```

表中的其他符号以纯小数点报价——那里的离格价格（例如中间报价）只是一个软 `off_tick_grid_*` 警告，永远不会被拒绝。

## 输出合约

当 `--format json|both` 时，将 `futures_position_size_<SYMBOL>_<as-of>.json` 写入 `--output-dir`；`--format text|both` 将格式化摘要打印到 stdout。`--as-of` 默认为今天（这是一个操作员时间的计算工具，不是回测工具）。

```yaml
schema_version: "1.0"
symbol: ES
direction: LONG
sizing_status: SIZED | NO_TRADE
no_trade_reason: null | risk_below_one_contract | gate_not_ready | gate_symbol_mismatch | ...
entry: 5000.25
stop: 4980.00
stop_distance_points: 20.25
stop_distance_ticks: 81
contract_spec: {multiplier: 50, tick_size: 0.25, tick_value: 12.5, currency: USD, source: cme, verified: "2026-07-17"}
risk_per_contract_usd: 1012.50
risk_budget_usd: 2000.00
contracts: 1
total_risk_usd: 1012.50
risk_pct_of_account: 1.01
max_contracts_cap_applied: false
fx_rate_used: 1.0
margin_note: "交易所保证金要求是经纪商/时间相关的，这里不计算；与您的经纪商核实初始/维持保证金。"
gate: {report_path, setup_status, gate_confidence, warnings}   # 模式 B 仅限
warnings: []
run_context: {symbol, as_of, schema_version, skill}
```

## 安全机制

1. **从不计算没有显式止损的仓位。** 模式 A 中需要 `--stop`；模式 B 拒绝计算（`gate_not_ready`），直到网关本身报告 `READY_FOR_PLAN` 并带有有效的 `invalidation_level`。
2. **向下取整，永不向上舍入——按设计精确，无 epsilon。** `contracts = floor(risk_budget / risk_per_contract)` 使用精确的有理数算术（Python 的 `Fraction`，不是浮点除法）计算，因此 `contracts * risk_per_contract <= risk_budget` 由设计保证——没有 epsilon 推动，没有浮点表示的边缘情况，并且永远不会超过预算。如果结果计数在经济上不合理（例如，不正常的输入，如异常的乘数覆盖），则会被直接拒绝。零合约是一个合法的、失败关闭的 `NO_TRADE` 结果，不是错误。
3. **两种失败关闭的类别，与谁提供了错误值相匹配。** 由操作员引起的问题（在 `--entry` 错误一侧的显式 `--stop`、比一个最小变动价位更近的止损、键入的债券价格离格）是使用错误：退出 2，不写入报告。来自不可信的网关报告文件（模式 B 的止损）的相同类别的错误则是一个失败关闭的 `NO_TRADE` 结果：退出 0，写入报告并命名原因——这永远不会在坏的或尚未准备好的网关文件上崩溃，与管道中的其他技能完全匹配。
4. **债券系列的离格价格是硬拒绝，不是警告。** ZT/ZF/ZN/ZB 以 32 分位/64 分位符号报价；不在最小变动价位上的价格几乎肯定是符号输入错误，如果计算会无声地产生错误的金钱计算。其他符号只警告。
5. **从不计算保证金。** `margin_note` 是一个静态的、永远不会过时的提醒——保证金要求是经纪商和时间相关的；这个技能不估计它们。
6. **货币感知。** 每个核心表符号都是以美元报价的（通过表级单元测试确认），包括 CME 外汇期货（例如 B6 的 GBP 62,500）的合约 SIZE 以外币计价，但交易和结算在美元。以非美元货币（通过 `--contract-currency` 覆盖）报价的符号需要显式的 `--fx-rate`——没有无声的默认值。
7. **不是投资建议。** 这个技能对操作员提供的或网关确认的输入执行基于风险的算术；它不推荐交易、方向或入场价。

## 资源

- `scripts/futures_position_sizer.py` -- CLI：参数解析、加固的网关-json 加载（不可读 / parse_error 包括 RecursionError / 非有限值通过迭代全文扫描）、报告生成
- `scripts/futures_sizing.py` -- 纯计算核心：数字验证器、已验证的 23 市场合约规格表、风险计算、向下取整算法、最小变动价位保护、网关报告形状规范化
- `references/futures-contract-specs.md` -- 已验证的合约规格表，包含每行的官方来源 URL 和验证日期
- `references/sizing-methodology.md` -- 公式、精确有理数向下取整算法的合理性、失败关闭退出码约定和示例（ES 多头、B6 空头通过网关交接）
