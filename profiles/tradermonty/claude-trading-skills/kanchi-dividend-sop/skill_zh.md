# Kanchi 股息投资标准操作流程

## 概述

将 Kanchi 的五步法实现为用于美国股息投资的确定性工作流。
优先考虑安全性和可重复性，而非激进地追逐高收益。

## 使用场景

当用户需要以下功能时，使用此技能：
- 适用于美国股票的 Kanchi 风格股息股票筛选。
- 可重复的筛选和回调入场流程，而非临时性选择。
- 一页纸的承保备忘录，包含明确的无效条件。
- 用于监控和税务/账户位置工作流的交接包。

## 前置条件

### API 密钥设置

入口信号脚本需要 FMP API 访问权限：

```bash
export FMP_API_KEY=your_api_key_here
```

### 输入源

在运行工作流之前，准备以下输入之一：
1. `skills/value-dividend-screener/scripts/screen_dividend_stocks.py` 的输出。
2. `skills/dividend-growth-pullback-screener/scripts/screen_dividend_growth_rsi.py` 的输出。
3. 用户提供的股票代码列表（经纪商导出或手动列表）。

#### 预期 JSON 输入格式

使用 `--input` 时，提供以下格式的 JSON：

```json
{
  "profile": "balanced",
  "candidates": [
    {"ticker": "JNJ", "bucket": "core"},
    {"ticker": "O", "bucket": "satellite"}
  ]
}
```

或简化格式：

```json
{
  "tickers": ["JNJ", "PG", "KO"]
}
```

可选的 `value-dividend-screener` 和
`dividend-growth-pullback-screener` 交接使用 `stocks[].symbol`。
`build_sop_plan.py --input` 和 `build_entry_signals.py --input`
都直接接受上述 `candidates[].ticker` 和 `tickers[]` 格式。

为确定性工件生成提供股票代码：

```bash
python3 skills/kanchi-dividend-sop/scripts/build_sop_plan.py \
  --tickers "JNJ,PG,KO" \
  --output-dir reports/
```

为第 5 步入场时间工件。**`--yield-floor` 是必需的** — 它是第 1 步的收益门限；没有它，每一行都会安全地退回 `STEP1-RECHECK`（一行永远无法达到通过级别）。传递 `--profile` / `--safety-bias` 用于 run_context，和 `--events-json` 用于第 4b 步扫描（缺失 ⇒ 每一行都被视为 `SKIPPED`，且 TRIGGERED 名称被限制为 `HOLD-REVIEW` — 永不静默清理）：

```bash
python3 skills/kanchi-dividend-sop/scripts/build_entry_signals.py \
  --tickers "JNJ,PG,KO" \
  --alpha-pp 0.5 \
  --yield-floor 3.0 \
  --profile balanced --safety-bias medium \
  --events-json reports/kanchi_events_2026-05-17.json \
  --output-dir reports/
```

## 工作流

### 1) 筛选前定义投资指令

首先收集并锁定参数：
- 目标：当前现金收入与股息增长。
- 最大仓位和仓位大小上限。
- 允许的金融工具：仅股票，或包括 REIT/BDC/ETF。
- 优先的账户类型上下文：应税账户与类似 IRA 的账户。

加载 `references/default-thresholds.md` 并应用基准设置，除非用户覆盖。

### 2) 构建可投资组合

从质量导向的集合开始：
- 核心仓位：长期股息增长名称（例如，股息贵族风格的质量集合）。
- 卫星仓位：高收益板块（公用事业、电信、REIT）在单独的风险仓位中。

使用明确的股票代码收集源优先级：
1. `skills/value-dividend-screener/scripts/screen_dividend_stocks.py` 输出（FMP/FINVIZ）。
2. `skills/dividend-growth-pullback-screener/scripts/screen_dividend_growth_rsi.py` 输出。
3. 当 API 不可用时，用户提供的经纪商导出或手动股票代码列表。

在继续之前，返回按仓位分组的股票代码列表。

### 3) 应用 Kanchi 第 1 步（收益筛选与陷阱标志）

主要规则：
- 第 1 步收益 = **常规向前收益** = `latest_declared_regular
  dividend × cadence-implied frequency / price`（WS-1 `dividend_basis.py`）。
  永远不要使用 `profile.lastDividend` / TTM — 它滞后于最新宣布的增幅（缺陷 D5）并静默捆绑特殊股息（D4）。
- 将配置文件底线（收入现在 4.0% / 平衡 3.0% / 增长优先 1.5%）应用于**常规**收益。

陷阱与新鲜度控制（由 `dividend_basis.py` 机器生成）：
- `special_dividend_flag` → 排除特殊股息；报告常规与 TTM 收益。
- `variable_policy_flag` → `FAIL`（CALM 风格；不是收入基础）。
- `cut_flag` → `FAIL`；`suspension_flag` → `FAIL`。
- `freeze_flag` → `HOLD-REVIEW`（收入现金牛例外仅在步骤 8 综合中决定，如果安全干净且未阻塞）。
- **数据新鲜度门限**：如果常规收益在底线 ±0.20pp 内 (`floor_borderline`)，且最新宣布的股息未从权威来源确认，则发出 `STEP1-RECHECK` — **永远不是硬性失败**（这是 CFR D5 修复）。

### 4) 应用 Kanchi 第 2 步（增长与安全）— 板块分发

安全是**板块特定的** — 统一的 GAAP/FCF 三元组会误判银行（FCF 无意义）和受监管的公用事业（FCF 结构性为负）。
使用 `references/sector-step2-modules.md`；确定性分发是 `scripts/payout_safety.py`。

- 始终计算**支付三元组**：GAAP-EPS 支付、调整后 EPS 支付、FCF 支付。安全性判断使用 **调整后 EPS + FCF**（消费类），或板块模块（银行 / 公用事业 / 保险公司）。
- `adjusted_eps_source = UNAVAILABLE` ⇒ 限制为 `HOLD-REVIEW`（安全措施；
  永远不是静默通过）。
- GAAP↔调整后 EPS 差异 > 25% ⇒ 第 4 步一次性标志。
- 合并 **在 4 个季度内完成** 推测 GAAP EPS 被扭曲 ⇒ 强制调整路径或 `HOLD-REVIEW`（FITB/Comerica 金色案例）。
- 受监管的公用事业：**负 FCF 不是自动失败** — 基于 FFO/债务 + 允许的 ROE + 率案 + 股权发行风险进行判断。

当趋势混合但未破裂时，归类为 `HOLD-REVIEW` 而非硬性拒绝。

### 5) 应用 Kanchi 第 3 步（估值）与 US 板块映射

使用 `references/valuation-and-one-off-checks.md` 并应用板块特定估值逻辑：
- 金融业：`PER x PBR` 可保持为首要。
- REIT：使用 `P/FFO` 或 `P/AFFO` 而非纯 `P/E`。
- 轻资产板块：结合向前 `P/E`、`P/FCF` 和历史范围。

始终报告每个股票代码使用的估值方法。

### 6) 应用 Kanchi 第 4 步（一次性事件筛选）

拒绝或降级最近利润依赖一次性效应的名称：
- 资产出售收益、诉讼和解、税收效应激增。
- 利润率激增未得到销售趋势支持。
- 重复“一次性/非经常性”调整。

为每个 `FAIL` 记录一行证据以保持可审计性。

### 6b) 应用 Kanchi 第 4b 步（向前结构性事件扫描）

第 4 步是向后看的；第 4b 步捕捉 *待处理/最近的* 结构性事件（MKC-联合利华的失误，D3）。对每个幸存的候选股票，运行 WebSearch + 发行人 IR/SEC 检查，使用**源层次结构**：发行人 IR → SEC 文件（8-K/10-Q/10-K/代理/S-4）→ 交易所/公司演示文稿 → 可靠电传 → 财务门户（仅二级）。将结果记录到经过策展的事件 JSON 中，并通过 `build_entry_signals.py --events-json` 传递。

- 只有**重大结构性事件**会限制结论为 `HOLD-REVIEW`（交易 > 10% 市值、股权发行 > 10–20%、杠杆 +0.5x EBITDA、控制权/上市/HQ 变更、合并同类/剥离/分拆/大型资产出售、股息/评级/杠杆政策变更、板块特定实质性、或滚动 24m 累计 M&A > 15% 市值）。次要附加项仅为警告。
- **悲观限制**：在步骤 5 TRIGGERED 名称上 `FAILED-DEGRADED` / `SKIPPED` / `NO_EVENT_FOUND` ⇒ `HOLD-REVIEW` + **T1 阻塞**。WebSearch 不可用（Web 应用/离线）与相同处理 — 永不静默跳过。`CLEAN_CONFIRMED`（主要来源检查）强于 `NO_EVENT_FOUND`（仅搜索）。

### 7) 应用 Kanchi 第 5 步（弱势买入规则）

机械设置入场触发器：
- 收益触发器：当前收益高于 5 年平均收益 + alpha（默认 `+0.5pp`）。
- 估值触发器：目标倍数达到 (`P/E`、`P/FFO` 或 `P/FCF`)。

执行模式：
- 分批订单：`40% -> 30% -> 30%`。
- **预订单障碍**：如果候选股票有任何未解决的 `pre_order_blockers[]`（来自 WS-1/2/3 — 变量/削减/暂停、调整后 EPS 不可用、GAAP/Adj 差异、银行信用、公用事业 FFO/债务、事件扫描失败/跳过、陈旧股息、…）OR
  `t1_blocked` 为 true，第一批将**被阻塞或缩减为 ≤20% 的跟踪批次** — 不是 40%。
- **板块集群风险**：当 ≥ `SECTOR_CLUSTER_WARN_COUNT` 同一板块的名称通过（例如，许多小银行共享一个宏观 Beta）时，发出一个投资组合级别的 `CLUSTER-RISK` 警告。
- 在每个*未阻塞*添加前要求一句话合理性检查：“论点完整 vs 结构性破裂”。

### 8) 生成标准化输出

始终生成：
1. 筛选表格，包含**可操作的结论级别**：`CLEAN-PASS`、`PASS-CAUTION`、`CONDITIONAL-PASS`、`HOLD-REVIEW`、`STEP1-RECHECK`、`FAIL`（由 `verdict.py` 从步骤 1 + 步骤 2 + 步骤 4b + 障碍物综合）。每行包含证据。
2. 一页股票备忘录（使用 `references/stock-note-template.md`）与每个股票代码的**来源块**（价格/股息/支付/事件来源、`unresolved_blockers`、`evidence_refs[]`）。
3. 限价订单计划，包含分批尺寸、障碍物门限和无效条件。
4. 顶层**run_context**（配置文件、收益底线百分比、安全偏差、集合源、排除的资产类型），以便 3% 运行结果永远不会在 4% 运行中静默重复。

## 输出

返回和/或生成：
1. SOP 筛选摘要（Markdown 格式）。
2. 基于 `references/stock-note-template.md` 的承保备忘录集。
3. 可选的由 `skills/kanchi-dividend-sop/scripts/build_sop_plan.py` 生成的计划工件文件，位于 `reports/`。
4. 可选的步骤 5 入场信号工件，由 `skills/kanchi-dividend-sop/scripts/build_entry_signals.py` 生成，位于 `reports/`。

## 节奏

使用以下最小节奏：
- 每周（15 分钟）：仅检查股息和商业新闻变化。
- 每月（30 分钟）：重新运行筛选并刷新订单级别。
- 每季度（60 分钟）：使用最新文件/财报进行深度安全审查。

## 多技能交接

首先运行此技能，然后交接输出：
1. 交由 `kanchi-dividend-review-monitor` 进行每日/每周/季度异常检测。
2. 交由 `kanchi-dividend-us-tax-accounting` 进行账户位置和税务分类规划。

## 安全机制

- 在未经过步骤 4、步骤 4b 和安全检查的情况下，不要盲目发出买入指令。
- 在验证覆盖质量之前，不要将高收益视为价值。
- 使用**常规**向前收益进行步骤 1，永远不要使用特殊/TTM 包含的数字；接近底线 + 未确认 ⇒ `STEP1-RECHECK`，不是 FAIL。
- 在 TRIGGERED 名称上失败的/跳过的事件扫描 ⇒ `HOLD-REVIEW` + T1 阻塞。永不静默跳过步骤 4b。
- 保持假设明确；`adjusted_eps`/数据缺失 ⇒ 安全措施 `HOLD-REVIEW`，永不静默通过。

## 资源

- `scripts/thresholds.py`：**所有 SOP 阈值的单一真实来源** + `SCHEMA_VERSION`（下游模式演化守卫）。
- `scripts/dividend_basis.py`：WS-1 常规/特殊/变量/冻结/削减 + 数据新鲜度门限引擎（纯净、离线）。
- `scripts/payout_safety.py`：WS-2 板块感知 GAAP/调整后/FCF 支付三元组 + 完成合并链接。
- `scripts/event_scanner.py`：WS-3 孤立向前/最近公司行动扫描器 + 材质性门限 + 悲观限制。
- `scripts/verdict.py`：WS-5 可操作级别综合 + run_context + 证据_ref 辅助工具。
- `scripts/build_entry_signals.py`：协调器（步骤 5 目标 + WS-1/2/3/5 集成）。标志：`--yield-floor`、`--events-json`、`--profile`、`--safety-bias`、`--universe-source`。
- `scripts/build_sop_plan.py`：确定性 SOP 计划骨架生成器。
- `scripts/tests/test_golden_p0.py`：**P0 合并门限** — 端到端冻结的结论（通过 `scripts/run_all_tests.sh` 运行）。
- `references/default-thresholds.md`：人类可读的阈值镜像。
- `references/sector-step2-modules.md`：步骤 2 安全指标按板块。
- `references/valuation-and-one-off-checks.md`：步骤 3 估值 + 步骤 4 一次性事件。
- `references/stock-note-template.md`：一页备忘录 + 来源块。
