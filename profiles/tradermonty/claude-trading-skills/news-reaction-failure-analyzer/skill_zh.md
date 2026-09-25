# 新闻反应失败分析器

## 概述

实现 Jason Shapiro 的 COT 逆势过程的第 2 步：一旦市场被标记为拥挤（`cot-contrarian-detector`，第 1 步），检查它是否未能对应该奖励群体的新闻做出反应。不因真正看涨的新闻而上涨的拥挤多头市场，或不因真正看跌的新闻而下跌的拥挤空头市场，是群体买入/卖出动力耗尽的典型行为特征——这是将“拥挤”转化为逆势设置候选者的确认步骤（第 3-5 步，仍需手动：价格行为确认、入场、出场）。

**为何这不是一个简单的失败率检查：** 早期设计在相关事件少于一半“响应”时标记“新闻失败”——但在纯噪声下，约 69% 的单个事件会因偶然性而未能响应，因此该规则会在不同样本量下 48-83% 的时间内确认随机噪声。此技能要求市场已显著向群体有利新闻的反方向移动（一个具有蒙特卡洛验证的零假设假阳性界限的漂移显著性检验），而不仅仅是“响应不足”。有关完整统计依据，请参阅 `references/news-failure-patterns.md`。

## 何时使用此技能

**英文：**
- “尽管 [资产] 拥挤多头/空头，市场是否无视了 [事件]？”
- “对 [符号] 运行新闻失败检查”
- “[符号] 是否确认了 Shapiro 风格的逆势设置？”
- 在 `cot-contrarian-detector` 标记市场为 CROWDED_LONG / CROWDED_SHORT 后，且用户希望进入第 2 步时

**日文：**
- 「この市場は好材料に反応しなかった？」
- 「COTで偏っているこの銘柄のニュース失敗を確認して」

**不要使用时：**
- 市场未拥挤（NEUTRAL 分类）——此技能拒绝闭锁失败，除非显式使用 `--direction` 覆盖
- 尚未存在编辑后的事件 JSON——必须先运行 WebSearch（下文第 2 步）；切勿编造事件或 URL 以获取结论

## 前置条件

- **FMP API Key：** 必须设置。设置 `FMP_API_KEY` 或传递 `--api-key`。仅用于价格数据（`stable/historical-price-eod/light`）——覆盖范围因符号而异；请参阅 `references/price-source-map.md`。
- **Python 3.9+** 并安装 `requests`。
- **WebSearch 访问权限** 以编辑事件 JSON（第 2 步）。无此权限时，技能会优雅降级（声明限制；不会编造事件）。
- **可选：** 一个 `cot-contrarian-detector` JSON 报告（`--detector-json`）以自动解析符号 + 方向，或显式提供 `--direction`。

## 工作流程

### 第 1 步：获取符号 + 方向

从 `cot-contrarian-detector` 报告（`--detector-json`，在 `markets[]` 中查找符号）或直接由用户（`--symbol` + `--direction`）提供。NEUTRAL 分类、报告中缺少符号或报告年龄超过 `--max-detector-age-days`（默认 10 天）都将拒绝闭锁失败，并给出具体原因——只有显式 `--direction` 可覆盖。

### 第 2 步：通过 WebSearch 编辑事件 JSON

使用 4 层级来源层次结构（发行人/主要 → SEC/官方统计 → 电线 → 门户——请参阅 `references/news-failure-patterns.md`）在评估窗口（`--window-days`，默认 10 天）内搜索新闻。将结果写入 `references/news-failure-patterns.md` 模板的编辑后事件 JSON——每个事件包含 `event`、`event_time`（ISO8601 带显式 UTC 偏移）、`source_url`、`source_tier`、`expected_impact`（BULLISH/BEARISH）。

**切勿编造事件或 URL。** WebSearch 不可用 → 明确声明；仅当用户接受 `INSUFFICIENT_EVIDENCE` 结果（原因 `no_events_provided`）时才可无事件 JSON 继续——CLI 不会因缺少事件文件而抛出异常，始终以 0 退出并记录原因。

### 第 3 步：运行 CLI

```bash
python3 skills/news-reaction-failure-analyzer/scripts/analyze_news_reaction.py \
  --symbol B6 --detector-json reports/cot_crowding_2026-07-12.json \
  --events-json reports/nrf_events_B6_2026-07-12.json \
  --output-dir reports/
```

脚本获取价格序列（文档中记录的降级链——期货符号优先，ETF 代理若 402/受限或 `rows == 0`；请参阅 `references/price-source-map.md`），计算每个事件的有效日期/回报/标准分，将 3 个交易日窗口重叠的事件聚类（独立性检验），并综合结论。

### 第 4 步：展示结论 + 交接

展示结论、汇总统计（`drift_stat`、`responded_ratio`）和证据表（每个事件的回报/标准分/反应标签，显示任何 `dropped_events` 原因——永不隐匿）。若使用代理（`run_context.proxy_used`），需注明跟踪误差限制。

输出 `contrarian-setup-gate` (#241，尚未构建) 的交接块：

```json
{"news_failure": {"verdict": "CONFIRMED", "confidence": "HIGH", "report_path": "reports/nrf_B6_2026-07-12.json"}}
```

## 输出

- **JSON：** `reports/nrf_<symbol>_<as-of-date>.json`——`schema_version`、`symbol`、`direction`、`expected_direction`、`actual_reaction`（`FAILED_TO_RALLY`/`FAILED_TO_SELL_OFF`/`RALLIED`/`SOLD_OFF`/`MIXED_REACTION`/`NO_DATA`）、`verdict`、`confidence`、`relevant_events_used`、`aggregate`（mean_z3/drift_stat/responded_ratio）、`evidence[]`、`dropped_events[]`、`run_context`。
- **Markdown：** `reports/nrf_<symbol>_<as-of-date>.md`——人类可读的结论、汇总统计、证据表、被丢弃事件表、代理限制（若使用）、以及方法论脚注。

## 安全机制

- **确认不是交易信号。** 它确认第 5 步中的第 2 步——价格行为确认（第 3 步）、入场（第 4 步）、出场（第 5 步）仍需手动，且在建立任何头寸前仍需完成。
- **不足证据永不推进流程。** 可用相关事件聚类少于 `--min-events`（默认 3 个）、缺少检测报告、检测报告的 `data_date` 缺失、无法解析、日期晚于 `--as-of` 或早于 `--max-detector-age-days`（陈旧）、无显式覆盖的 NEUTRAL 分类、或无可用价格来源时均会给出此结论——永不崩溃，永不因数据不足而强制调用。
- **COT 发布滞后。** COT 数据在读取时已 3-9 天滞后（请参阅 `cot-contrarian-detector`）；新闻失败证据应在此背景下读取，而非作为当日确认。
- **反方向事件仅作背景参考**——显示在证据表中但不会影响结论（仅计算 `expected_impact` 与群体 `expected_direction` 匹配的事件）。
- **基于代理的价格会注明，不会隐藏。** 当使用 ETF 代理时（`run_context.proxy_used`），报告会注明——跟踪误差、费用拖累、滚动时间差异使反应方向读数近似而非精确。
- **极端相关性下的残余统计风险。** 结论的零假设假阳性率在 i.i.d. 噪声（<8%）和现实残余相关性压力（AR(1) ρ=0.1，<10%）下已严格验证。在故意极端相关性压力下（非聚类事件窗口的滞后 1 ρ=0.3——约 10 倍于流动性期货的经验自相关），测量的零率上升至 ~11-13%。这是一个记录在案的 v1 限制，而非沉默的缺口——请参阅 `references/news-failure-patterns.md` 获取完整数据。希望即使在压力下也保持 <10% 边际的用户可传递 `--drift-z 1.75`（代价是可能遗漏部分真实的新闻失败信号，而不仅是噪声）。
- **非投资建议。** 仅限研究/教育目的。

## 资源

### `references/news-failure-patterns.md`
完整方法论：什么可被视为相关事件、4 层级来源层次结构、实例、事件 JSON 编辑指南+模板、以及结论阈值依据（为何是漂移显著性而非简单比率；蒙特卡洛验证的零假设界限）。

### `references/price-source-map.md`
每个市场的价格来源降级链、验证/402/0 行状态（实施时实时探测）、ETF 代理限制，以及无可用来源的市场（记录的 `no_price_source` 案例：VX、ZQ、HO、所有农业相关）。

### 何时加载资源
- **首次使用/解释方法论：** 加载 `references/news-failure-patterns.md`
- **解释市场为何无结论（无价格来源）：** 加载 `references/price-source-map.md`
- **常规执行：** CLI 本身无需资源——仅第 2 步（事件编辑）和向用户解释结果时需要。
