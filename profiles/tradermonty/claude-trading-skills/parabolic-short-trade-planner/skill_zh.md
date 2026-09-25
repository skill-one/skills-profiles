## 概述

生成 Qullamaggie 风格的抛物线短仓观察清单和条件盘前计划，用于美国股票。该技能不会发送订单。它会发出 JSON + Markdown，供人类在进入前与他们的经纪商进行核对。

三个阶段：

- **阶段 1 (`screen_parabolic.py`)**：从 FMP 拉取日线 K 线图 + 公司概况，应用硬性无效规则（模式感知），对幸存者在 5 个因素（权重 30/25/20/15/10）上打分，并分配 A/B/C/D 等级。
- **阶段 2 (`generate_pre_market_plan.py`)**：获取阶段 1 的 JSON，按 `--tradable-min-grade`（默认 `B`）进行过滤，检查 Alpaca 短仓库存（或 `ManualBrokerAdapter`），评估继承的前一交易日收盘的 SEC 规则 201 SSR 状态，并为每个候选对象渲染三个触发计划。
- **阶段 3 (`monitor_intraday_trigger.py`)**：读取阶段 2 的计划，获取 5 分钟 K 线图（Alpaca 实时或固定），按每个计划的状态机（FSM）向前推进一步，持久化每个计划的状态，并写入 `intraday_monitor` JSON，包含 `state`、`entry_actual`、`stop_actual` 和 `shares_actual`（触发时）。一次性操作——交易员通过 `watch` 或 cron 每隔 1-5 分钟运行一次；重放确定性，因此重新运行时字节相同。

## 何时使用

当用户需要时调用此技能：

- 从标普 500（或自定义 CSV）构建每日抛物线短仓观察清单。
- 将观察清单转换为具有明确借入 / SSR / 状态上限门控的盘前交易计划。
- 在 Alpaca 下单前审计候选对象的阻塞原因与建议手动确认原因。

不用于：

- 多头侧动量筛选——使用 vcp-screener 或 canslim-screener。
- 1 分钟 / 亚分钟日内信号——阶段 3 仅评估 5 分钟 K 线图。
- 实时订单路由——此技能按设计仅进行检测；阶段 3 发出 `triggered` 状态，包含具体的进入/止损/股份数量，但交易员手动触发订单。

## 工作流程

### 阶段 1 — 每日筛选器

1. 确认 `FMP_API_KEY` 已设置（环境变量或 `--api-key`）。
2. 以更安全为默认模式运行：
   ```bash
   python3 skills/parabolic-short-trade-planner/scripts/screen_parabolic.py \
     --mode safe_largecap --as-of 2026-04-30 --output-dir reports/
   ```
3. 检查 `reports/parabolic_short_<date>.md`——观察清单按等级（A→D）分组。
4. 将有趣的名称提升到阶段 2。

对于小盘股爆发行情，切换到 `--mode classic_qm`（市场市值和 ADV 下限更宽松，5 天 ROC 阈值更高）。

在没有 API 的情况下进行测试，运行 `--dry-run --fixture <path>` 对 JSON 固定数据进行操作（一个固定数据已随 `scripts/tests/fixtures/dry_run_minimal.json` 发送）。

### 阶段 2 — 盘前计划生成器

1. 可选：设置 `ALPACA_API_KEY` / `ALPACA_SECRET_KEY` 以进行实时借入检查。如果没有它们，计划器会回退到 `ManualBrokerAdapter`，将每个候选对象标记为 `borrow_inventory_unavailable` / `plan_status: watch_only`。
2. 运行：
   ```bash
   python3 skills/parabolic-short-trade-planner/scripts/generate_pre_market_plan.py \
     --candidates-json reports/parabolic_short_2026-04-30.json \
     --account-size 100000 --risk-bps 50 --output-dir reports/
   ```
3. 输出：`reports/parabolic_short_plan_<date>.json`。每个计划包含三个进入计划（5min ORL 突破、首个红色 5 分钟、VWAP 失败）与 `entry_hint` / `stop_hint` 公式字符串（没有内置股份数量——交易员在触发时根据 `shares_formula` 计算股份数）。

### 阶段 3 — 日内触发监控器

1. 确认 `ALPACA_API_KEY` / `ALPACA_SECRET_KEY` 已设置（阶段 3 使用 Alpaca 市场数据；`data.alpaca.markets` 适用于纸面和实盘账户）。
2. 在美国常规交易时段内，按节奏运行一次性操作——典型的是在第一个 30 分钟内每 60 秒运行一次，然后每 5 分钟运行一次：
   ```bash
   python3 skills/parabolic-short-trade-planner/scripts/monitor_intraday_trigger.py \
     --plans-json reports/parabolic_short_plan_2026-05-05.json \
     --bars-source alpaca \
     --state-dir state/parabolic_short/ \
     --output-dir reports/
   ```
   或将其包装在 `watch -n 60 'python3 ...'` / cron 中。
3. 输出：`reports/parabolic_short_intraday_<date>.json` 列出每个监控计划，包含 `state`（`armed` / `triggered` / `invalidated` / FSM 特定）、源自 K 线图的转换时间戳，以及 `size_recipe_resolved`（具体的 `shares_actual`）在触发时。
4. 在没有 API 的情况下进行测试，使用 `--bars-source fixture --bars-fixture <path>` 对 JSON 固定数据进行操作（`scripts/tests/fixtures/intraday_bars/`）。

阶段 3 触发检测不是订单指令。在手动短仓进入前，确认借入/定位可用性、SEC 规则 201 SSR 状态、经纪商卖空控制以及经纪商当前的日内保证金或日内交易控制。FINRA 以 2026-06-04 生效的日内保证金标准取代了旧的 P模式交易者日计数和 25,000 美元最低净资产要求，允许经纪商分阶段实施，直至 2027-10-20。

阶段 3 是 **幂等的**：每次运行都会从开盘到 `now_et`（或 `--now-et` 覆盖）重放完整会话 K 线图，因此在同一分钟内重新运行会产生相同的状态。`prior_state` 仅用于差异/通知显示；它永远不会推进 FSM。

### 进入前审查计划

每个股票读取三个顶层字段：

- `plan_status`：`actionable`（手动门控可清除）或 `watch_only`（硬性阻塞——借入不可用或 SSR 活跃）。
- `blocking_manual_reasons`：必须全部解决才能触发。
- `advisory_manual_reasons`：仅提示，例如 `manual_locate_required`（始终设置）、`warning:too_early_to_short`、`warning:recent_earnings_catalyst`（最近财报在 `--earnings-catalyst-window-days` 内，默认 10 个交易日——将动量视为事件驱动而非纯粹技术性爆发行情）。

### 财报感知筛选

阶段 1 每次运行（单个调用，非每个股票）获取一次 FMP 财报日历，并发出两个财报感知检查：

- `--exclude-earnings-within-days`（默认 2 个日历日，向前）——当下一个财报在窗口内时硬性无效。匹配遗留 `earnings_blackout_days` 语义。
- `--earnings-catalyst-window-days`（默认 10 个交易日，向后）——当最后一个财报在窗口内时发出软性警告 `recent_earnings_catalyst`。作为建议手动原因路由到阶段 2，而不会强制 `trade_allowed_without_manual: false`。

每个候选对象的输出暴露 `last_earnings_date`、`next_earnings_date`、`trading_days_since_earnings`（交易日）、`earnings_within_days`（日历日，向前）、`earnings_blackout_days`（配置阈值）和 `earnings_in_blackout_window`。遗留 `earnings_within_2d` 保留以向后兼容。

顶层日期：`as_of` 是计划日期（阶段 2 合同——永不修改）；`run_date` 与其镜像；`market_data_as_of` 是用于技术指标的最新 K 线图日期（周末运行时与 `as_of` 不同）。

## 交易所日历和重放

运行计划器前安装 `requirements.txt`。阶段 1 `--as-of` 使用严格的 `YYYY-MM-DD`，过滤该上限之外的 K 线图，并使用 XNYS 会话计算财报年龄。阶段 3 使用实际假日和提前收盘；收盘边界是排他的。仅接受历史日期与阶段 1 `--dry-run` 固定数据；实盘宇宙和概况端点不是 PIT，因此对于非当前的 `--as-of` 会失败关闭。

## 输出格式

阶段 1 JSON：`parabolic_short_<as_of>.json`（schema_version 1.0）。
阶段 2 JSON：`parabolic_short_plan_<as_of>.json`（schema_version 1.0）。
阶段 3 JSON：`parabolic_short_intraday_<as_of>.json`（schema_version 1.0，phase = `intraday_monitor`）。
合同由 `tests/test_schema_contract.py` 加上 `tests/test_monitor_intraday_smoke.py`（阶段 3）固定。

## 资源

- `references/parabolic_short_methodology.md` — Qullamaggie 的 3 触发框架和耗尽信号。
- `references/short_invalidation_rules.md` — 模式感知排除规则。
- `references/short_risk_management.md` — 规则 201、ETB vs HTB、定位。
- `references/intraday_trigger_playbook.md` — 每个触发类型的详细信息、阶段 3 实现的 FSM 转换以及相同 K 线图平分语义。
- `references/broker_capability_matrix.md` — 每个经纪商通过其 API 暴露的短仓库存。
