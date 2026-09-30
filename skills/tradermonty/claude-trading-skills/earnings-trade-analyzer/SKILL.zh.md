---
name: earnings-trade-analyzer
description: 使用5因素评分系统（缺口大小、盈利前趋势、成交量趋势、200日均线位置、50日均线位置）分析近期盈利后股票。每只股票评分0-100分，并评定A/B/C/D等级。当用户询问盈利交易分析、盈利后动量筛选、盈利缺口评分或寻找最佳近期盈利反应时使用。
---

# 收益交易分析器 - 盈后五因素评分

使用五因素加权评分系统分析近期盈后股票，以识别最强的收益反应，为潜在动量交易提供参考。

## 使用场景

- 用户需要盈后交易分析或收益缺口筛选
- 用户希望找到最佳的近期收益反应
- 用户请求收益动量评分或评级
- 用户询问盈后累积日（PEAD）候选股票

## 前置条件

- FMP API密钥（设置`FMP_API_KEY`环境变量或传递`--api-key`）
- 免费套餐（每天250次调用）足以进行默认筛选（回溯2天，前20名）
- 建议使用付费套餐进行更长的回溯窗口或完整筛选

## 工作流程

### 第1步：运行收益交易分析器

执行分析器脚本：

```bash
# 默认：最近2天的收益，前20名结果
python3 skills/earnings-trade-analyzer/scripts/analyze_earnings_trades.py --output-dir reports/

# 自定义回溯天数和市场价值过滤器
python3 skills/earnings-trade-analyzer/scripts/analyze_earnings_trades.py \
  --lookback-days 5 \
  --min-market-cap 1000000000 \
  --top 30 \
  --output-dir reports/

# 确定性锚定日期（America/New_York）；窗口基于ET日历日期，而非运行者的本地时钟。用于可重复运行/测试。
python3 skills/earnings-trade-analyzer/scripts/analyze_earnings_trades.py \
  --as-of 2026-09-15 \
  --output-dir reports/

# 带入场质量过滤器
python3 skills/earnings-trade-analyzer/scripts/analyze_earnings_trades.py \
  --apply-entry-filter \
  --output-dir reports/
```

#### 降级端点 / 预算回退方案用于计划性审查

如果分析器报告404错误、不合理的空收益日历，或在计划性收盘后/盘前运行期间耗尽API调用预算前未生成评分候选股票，请勿立即报告“无收益反应”。在包含至少一个XNYS交易日的日期窗口中返回干净的空响应，退出码为1，`ZERO_RESULT_REASON=earnings_calendar_empty_with_market_sessions`。如果共享的XNYS日历无法分类该窗口，退出码为1，`ZERO_RESULT_REASON=market_calendar_unavailable`。在获取个人资料期间预算或每日速率限制耗尽，退出码为1，`ZERO_RESULT_REASON=profiles_budget_exhausted`。将每个视为失败的运行以重试或回退，而非静默处理。仅在零交易窗口的干净空响应中退出0，`ZERO_RESULT_REASON=no_earnings_rows`。

1. 首先使用更窄的流动宇宙配置重试一次，以便完整的五因素评分器有机会完成，例如：

```bash
python3 skills/earnings-trade-analyzer/scripts/analyze_earnings_trades.py \
  --lookback-days 2 \
  --min-market-cap 5000000000 \
  --top 20 \
  --max-api-calls 600 \
  --output-dir reports/<routine-date>
```

2. 如果评分运行仍然无候选股票或无法完成，通过兼容性遮罩使用的稳定端点验证相同范围，并明确标记结果为未评分回退：

```bash
curl "https://financialmodelingprep.com/stable/earnings-calendar?from=YYYY-MM-DD&to=YYYY-MM-DD&apikey=$FMP_API_KEY"
```

然后可选地通过分析器的稳定优先FMP客户端或每个股票的`/stable/quote?symbol=<ticker>`调用丰富返回的US股票，按当日`changesPercentage`、市场价值和流动性排名。仅作为遗留密钥回退使用`/api/v3`报价调用，仅在稳定端点失败后使用。将这些呈现为**初步 / 未评分反应**，因为五因素评分器未运行；不要仅凭回退分配A/B/C/D等级。

**无候选股票输出陷阱：** 分析器可能打印`Candidates after filtering: 0` / `No candidates found matching criteria.`并成功退出，而未写入`earnings_trade_analyzer_*.json`文件。在这种情况下，不要尝试从不存在的候选文件中运行PEAD模式B。明确说明未生成评分分析器JSON，如果例行程序需要收益部分，则运行上述端点/报价丰富回退，并将任何名称标记为仅手动审核。此成功退出路径不包括获取个人资料期间预算耗尽：该情况退出1 (`ZERO_RESULT_REASON=profiles_budget_exhausted`)。

#### 空窗口和仅今日运行

收益日历窗口是包含性的，使用`--as-of`（或当前ET日期）的`America/New_York`日历日期。干净的提供者`[]`仅在共享的XNYS日历成功在该精确窗口中计数为零交易所会话时才是良性静默窗口结果，例如周末或节假日。如果窗口包含XNYS会话，相同的干净`[]`退出1，`ZERO_RESULT_REASON=earnings_calendar_empty_with_market_sessions`，因此不报告提供者降级为静默日。如果XNYS日历无法查询，运行也退出1，`ZERO_RESULT_REASON=market_calendar_unavailable`。

`--lookback-days 0`是有效的，并精确查询单个ET的`as-of`日期。在相关公告发布后（通常在会话收盘后）使用它；在XNYS会话上的空响应保持有意失败锁定。非空响应中不包含`symbol`的行保留单独的`ZERO_RESULT_REASON=no_earnings_rows`行为；该情况不是上述字面空列表会话检查。

### 第2步：审查结果

1. 阅读生成的JSON和Markdown报告
2. 加载`references/scoring_methodology.md`以获取评分解释背景
3. 重点关注A级和B级股票，寻找可操作的设置

### 第3步：展示分析

对每个顶级候选股票，展示：
- 综合评分和字母等级（A/B/C/D）
- 收益缺口大小和方向
- 盈前20天趋势
- 成交量比率（20天vs 60天平均）
- 相对于200天和50天移动平均线的位置
- 最弱和最强的评分组成部分

### 第4步：提供可操作指导

根据等级：
- **A级（85+）：** 强收益反应，有机构累积 - 考虑入场
- **B级（70-84）：** 良好收益反应值得监控 - 等待回调或确认
- **C级（55-69）：** 混合信号 - 谨慎使用，需要额外分析
- **D级（<55）：** 弱设置 - 避免或等待更好条件

## 输出

- `earnings_trade_analyzer_YYYY-MM-DD_HHMMSS.json` - 带有`schema_version "1.0"`的架构化结果
- `earnings_trade_analyzer_YYYY-MM-DD_HHMMSS.md` - 人类可读报告，包含表格

### 未知收益时间

FMP不会为每个收益行确认bmo/amc会话；未确认的行报告`earnings_timing: "unknown"`，缺口计算假设AMC窗口作为回退。两个报告都显示`timing_unknown_count` out of `timing_candidates_total`，因此这种假设保持可见，而不是未被注意地混合到评分中。

## 资源

- `references/scoring_methodology.md` - 五因素评分系统、等级阈值和入场质量过滤器规则
