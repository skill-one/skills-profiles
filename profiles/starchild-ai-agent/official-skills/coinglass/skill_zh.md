## 权限分级（平台 key = Startup 级，2026-09 实测）

平台注入的 `COINGLASS_API_KEY` 已降级为 **Startup** 计划。工具层对端点的实际权限：

**✅ Startup 可用**（全部正常数据）：
- Funding rates（v2/v4）、Supported coins/exchanges/pairs、Pairs markets
- Open interest（当前值 / OHLC history / aggregated history）
- Long/Short ratios（global / top-account / top-position）
- Taker buy/sell volume（单所 + aggregated，需 `exchange_list`）
- CVD、Net position（v1/v2）、Coin netflow
- Liquidations：coin-list、coin/pair history（pair 需 BTCUSDT 格式）、aggregated history（需 `exchange_list`）
- ETF flows / lists / premium（BTC、ETH、SOL、XRP、HK）
- Whale transfers、Hyperliquid whale alerts（仅 alert 流）
- Price history（symbol 需 pair 格式 BTCUSDT）

**❌ Startup 不可用**（401 "Upgrade plan"，调用前直接跳过）：
- `api/futures/coins-markets`（币种市场汇总）
- `api/futures/liquidation/order`（逐笔清算单）
- `api/futures/liquidation/heatmap/model1` + `aggregated-heatmap/model1`（**清算热力图整个不可用**）
- `api/hyperliquid/position`、`api/hyperliquid/wallet/position-distribution`（Hyperliquid 持仓分布；仅 whale-alert 可用）

**替代方案（按优先级）**：
1. **用户提供自己的 key**（Basic+ 计划）：设 `COINGLASS_API_KEY` 并绕过 sc-proxy 直连
   `https://open-api-v4.coinglass.com`（sc-proxy 会强制覆盖该 header，代理路径下自带 key 无效）。
2. **Apify 爬虫**：用 `apify` skill 抓 coinglass.com 页面上的清算热力图 / Hyperliquid 持仓数据。

对 401 "Upgrade plan" 错误，`cg_request` 会抛 `CoinglassPlanError`，错误信息已含上述引导。

## Liquidation Heatmap（❌ Startup 不可用 — 历史用法存档）

`cg_liquidation_analysis` 返回全0，不可用。热力图两个端点（`heatmap/model1` 与
`aggregated-heatmap/model1`）在 Startup 计划下均返回 401 Upgrade plan。

如需热力图数据：让用户自带 Basic+ key 直连（见上文替代方案），或用 Apify 爬取页面。

```python
# 以下仅在用户自有高级 key 下可用（直连，不走 sc-proxy）
from tools._api import cg_request

# 全市场聚合热力图（推荐，无需指定交易所）
# range 支持: 12h, 24h, 3d, 7d, 30d, 90d, 180d, 1y
data = cg_request("api/futures/liquidation/aggregated-heatmap/model1",
                  params={"symbol": "BTC", "range": "24h"})

# 返回结构：
# data["y_axis"]                   → 价格档位列表（从低到高）
# data["liquidation_leverage_data"] → [[y_idx, leverage, usd_value], ...]
# data["price_candlesticks"]        → OHLCV K线，最后一根收盘价 = 当前价
# data["update_time"]               → 更新时间戳

# 解析方法：
from collections import defaultdict
y_axis = data["y_axis"]
current_price = float(data["price_candlesticks"][-1][4])
price_liq = defaultdict(float)
for y_idx, leverage, usd_val in data["liquidation_leverage_data"]:
    if 0 <= y_idx < len(y_axis):
        price_liq[y_axis[y_idx]] += usd_val

longs  = {p: v for p, v in price_liq.items() if p < current_price}  # 多头清算（↓触发）
shorts = {p: v for p, v in price_liq.items() if p > current_price}  # 空头清算（↑触发）
```

## Script Usage

Script-mode skill — read this file, then invoke from a `bash` block:

```bash
python3 - <<'EOF'
import sys, json
sys.path.insert(0, "/data/workspace/skills/coinglass")
from exports import funding_rate, cg_open_interest, cg_liquidations

print(funding_rate(symbol="BTC"))
print(cg_open_interest(symbol="BTC"))
EOF
```

Read `exports.py` for the full list of available functions and exact
signatures. Common ones: `funding_rate`, `long_short_ratio`,
`cg_open_interest`, `cg_liquidations`, `cg_liquidation_analysis`,
`cg_global_account_ratio`, `cg_top_account_ratio`, `cg_top_position_ratio`,
`cg_taker_exchanges`, `cg_net_position`, `cg_supported_coins`,
`cg_supported_exchanges`, `cg_coins_market_data`, `cg_pair_market_data`,
`cg_ohlc_history`, `cg_hyperliquid_whale_alerts`,
`cg_hyperliquid_whale_positions`, `cg_taker_volume_history`,
`cg_aggregated_taker_volume`, `cg_cumulative_volume_delta`,
`cg_coin_netflow`, `cg_whale_transfers`, `cg_btc_etf_flows`,
`cg_eth_etf_flows`, `cg_sol_etf_flows`.


# Coinglass

Coinglass 提供了最全面的加密衍生品和机构数据。37 种工具涵盖期货头寸、鲸鱼追踪、成交量分析、清算和 ETF 流动。

**API 计划**: Startup (平台 key 已降级，见顶部「Plan 权限分级」)
**速率限制**: 请求级限制随计划降低，控制批量调用频率
**API 版本**: V4 (与 V2 向后兼容)
**总工具数**: 37 个跨 8 个类别


## Function Reference (full signatures + return shapes)

All functions live in `exports.py`. Most return `Optional[List[Dict]]` or
`Optional[Dict]`. None means the upstream call failed or returned empty —
always check before indexing.

### ⚠️ Field naming convention (READ THIS FIRST)

CoinGlass v4 API 使用 **camelCase** 为几乎所有数据字段命名，清算端点中有一些遗留的 snake_case 例外。不要假设 snake_case — 在脚本之前 `inspect` 字典。

- camelCase: `openInterest`, `volUsd`, `longRate`, `shortVolUsd`,
  `exchangeName`, `nextFundingTime`, `fundingIntervalHours`,
  `oichangePercent`, `h4OIChangePercent`, `avgFundingRateBySymbol`,
  `tokenAmount`, `liquidationUsd` (in some endpoints)
- snake_case (遗留，仅在 `cg_liquidations` 中): `liquidation_usd`,
  `longLiquidation_usd`, `shortLiquidation_usd`
- `rate` 字段（资金费率）是 STRINGS，带有 "+" / "-" / "%" — 用
  `float(r.rstrip('%').lstrip('+'))` 数值比较
- 时间戳是毫秒级 Unix epoch (例如 `1777881600000`)

### Funding & Open Interest

| Function | Signature |
|---|---|
| `funding_rate(symbol, exchange=None)` | dict — keys: `symbol`, `exchange`, `rate` (str), `num_exchanges`, `exchanges_data` (list of {`exchangeName`, `rate`, `nextFundingTime`, `fundingIntervalHours`, `status`}) |
| `cg_open_interest(symbol='BTC', interval='0')` | LIST of dicts (one per exchange) — keys: `symbol`, `openInterest`, `volUsd`, `oichangePercent`, `h4OIChangePercent`, `h24VolChangePercent`, `volChangePercent7d`, `avgFundingRateBySymbol`, `exchangeName`, `exchangeLogo` |

### Long/Short Ratios

| Function | Signature |
|---|---|
| `long_short_ratio(symbol='BTC', interval='h4')` | LIST — top item is aggregated; `list` field inside has per-exchange breakdown. Keys: `longRate`, `shortRate`, `longVolUsd`, `shortVolUsd`, `totalVolUsd`, `list` |
| `cg_global_account_ratio(symbol='BTC', exchange='Binance', interval='1h')` | list of historical bars |
| `cg_top_account_ratio(symbol='BTC', exchange='Binance', interval='1h')` | list — top trader account-count ratio |
| `cg_top_position_ratio(symbol='BTC', exchange='Binance', interval='1h')` | list — top trader position-size ratio |
| `cg_taker_exchanges(symbol='BTC', range_type='4h')` | list — taker buy/sell across exchanges |
| `cg_net_position(symbol='BTC', exchange='Binance', interval='1h')` | list — net long-short USD over time |

### Liquidations

| Function | Signature |
|---|---|
| `cg_liquidations(symbol='BTC', time_type='h24')` | LIST of dicts (one per exchange + an `'All'` row first). Keys: `exchange`, `liquidation_usd`, `longLiquidation_usd`, `shortLiquidation_usd` (NOTE: snake_case legacy fields) |
| `cg_liquidation_analysis(symbol='BTC', time_type='h24')` | dict — aggregated network-wide stats |
| `cg_coin_liquidation_history(symbol='BTC', interval='h4')` | list — historical liq bars |
| `cg_pair_liquidation_history(symbol='BTC', exchange='Binance', interval='h4')` | list — historical liq for one pair on one exchange |
| `cg_liquidation_coin_list(symbol=None)` | list of all coins with liq summary |
| `cg_liquidation_orders(symbol='BTC', exchange=None)` | list — recent individual liq orders |

### Futures Market Data

| Function | Signature |
|---|---|
| `cg_supported_coins()` | List[str] — symbols supported by CoinGlass |
| `cg_supported_exchanges()` | list of exchange info dicts |
| `cg_coins_market_data(symbol=None)` | list — current snapshot for all coins (or one if symbol given) |
| `cg_pair_market_data(symbol='BTC', exchange=None)` | list — pair-level snapshot |
| `cg_ohlc_history(symbol='BTC', interval='h4', exchange=None)` | list of OHLCV bars |

### Hyperliquid Whale Tracking

| Function | Signature |
|---|---|
| `cg_hyperliquid_whale_alerts()` | list — recent large-position alerts |
| `cg_hyperliquid_whale_positions()` | list — current open whale positions |
| `cg_hyperliquid_positions_by_coin(symbol='BTC')` | list — whales holding a specific coin |
| `cg_hyperliquid_position_distribution(symbol='BTC')` | dict — long/short position-size distribution |

### Volume / Flow

| Function | Signature |
|---|---|
| `cg_taker_volume_history(symbol='BTC', exchange='Binance', interval='1h', limit=1000, start_time=None, end_time=None)` | list — taker buy/sell volume bars |
| `cg_aggregated_taker_volume(symbol='BTC', interval='h4')` | list — aggregated across all exchanges |
| `cg_cumulative_volume_delta(symbol='BTC', exchange='Binance', interval='1h', limit=1000, start_time=None, end_time=None)` | list — CVD bars |
| `cg_coin_netflow(symbol=None)` | list — net inflow/outflow per coin |
| `cg_whale_transfers()` | dict — recent on-chain large transfers |

### ETF Flows

| Function | Signature |
|---|---|
| `cg_btc_etf_flows()` | list — daily flows per US BTC ETF |
| `cg_btc_etf_history(etf_ticker=None)` | list — historical AUM/flows |
| `cg_btc_etf_list()` | list of BTC ETF tickers + AUM |
| `cg_btc_etf_premium_discount()` | list — premium/discount % vs NAV |
| `cg_hk_btc_etf_flows()` | list — Hong Kong BTC ETF flows |
| `cg_eth_etf_flows()` / `cg_eth_etf_list()` / `cg_eth_etf_premium_discount()` / `cg_hk_eth_etf_flows()` | ETH ETF equivalents |
| `cg_sol_etf_flows()` / `cg_sol_etf_list()` | SOL ETF data |
| `cg_xrp_etf_flows()` / `cg_xrp_etf_list()` | XRP ETF data |

### Sample responses (most-used functions)

`funding_rate(symbol="BTC")`:
```json
{
  "symbol": "BTC",
  "exchange": "average",
  "rate": "-0.0016%",
  "num_exchanges": 21,
  "exchanges_data": [
    {"exchangeName": "Binance", "rate": "+0.0050%",
     "nextFundingTime": 1777881600000, "fundingIntervalHours": 8, "status": 1}
  ]
}
```

`cg_liquidations(symbol="BTC", time_type="h24")`:
```json
[
  {"exchange": "All", "liquidation_usd": 170497688.16,
   "longLiquidation_usd": 8179073.80, "shortLiquidation_usd": 162318614.36},
  {"exchange": "Bybit", "liquidation_usd": 40454694.98, ...}
]
```

`cg_open_interest(symbol="BTC")`:
```json
[
  {"symbol": "BTC", "openInterest": 61395303653.62, "volUsd": 56349328748.42,
   "oichangePercent": 7.17, "h4OIChangePercent": 5.33,
   "avgFundingRateBySymbol": -0.001874, "exchangeName": "Binance"}
]
```

`long_short_ratio(symbol="BTC", interval="h4")`:
```json
[{
  "symbol": "BTC", "longRate": 53.65, "shortRate": 46.35,
  "longVolUsd": 12558668895.91, "shortVolUsd": 10848776476.99,
  "totalVolUsd": 23407445372.91,
  "list": [
    {"exchangeName": "Binance", "longRate": 55.75, "shortRate": 44.25, ...}
  ]
}]
```

## Tool Selection Guide

### Decision Tree

**Step 1: Is this about LIQUIDATIONS?**

```
Liquidation query?
├─ YES → How many coins?
│   ├─ ALL coins / ranking / 排行 / 汇总
│   │   └─ → cg_liquidation_coin_list  ✅ (most liquidation queries land here)
│   ├─ ONE coin, need history over time
│   │   └─ → cg_coin_liquidation_history
│   ├─ ONE coin, specific orders (price/side/USD)
│   │   └─ → cg_liquidation_orders
│   └─ ONE coin, just a quick total + sentiment label
│       └─ → cg_liquidation_analysis  (rarely needed; only if explicitly "simple summary")
```

**Step 1: Is this about LONG/SHORT RATIO?**

```
Long/short query?
├─ Historical time-series, trend over time, 多空比变化
│   └─ → cg_global_account_ratio  (ALL accounts)
│      or cg_top_account_ratio    (top traders only)
│      or cg_top_position_ratio   (by position size)
└─ Current snapshot only (no history needed)
    └─ → long_short_ratio
```

**Step 1: Is this about OPEN INTEREST?**

```
OI query?
└─ → cg_open_interest  (always — do NOT use cg_coins_market_data for OI)
```

**Step 1: Is this a MARKET OVERVIEW / SENTIMENT query?**

```
Sentiment / 市场情绪 / pre-trade check?
└─ Use: funding_rate + long_short_ratio + cg_open_interest
   DO NOT use cg_coins_market_data as a substitute for any of the above
```

---

### Keyword → Tool Lookup

| Keyword / Pattern | Correct Tool | ❌ Do NOT use |
|---|---|---|
| 爆仓排行 / 今日爆仓 / all coins liquidation | `cg_liquidation_coin_list` | `cg_liquidations` |
| 24h爆仓汇总 / liquidation summary | `cg_liquidation_coin_list` | `cg_liquidation_analysis` |
| 全网账户多空比 / account L/S ratio | `cg_global_account_ratio` | `long_short_ratio` |
| 头部交易者多空 / top trader ratio | `cg_top_account_ratio` | `long_short_ratio` |
| 未平仓合约 / open interest | `cg_open_interest` | `cg_coins_market_data` |
| 市场情绪多空分析 | `funding_rate` + `long_short_ratio` + `cg_open_interest` | `cg_coins_market_data` |
| BTC 做多检查 / pre-trade checklist | `funding_rate` + `cg_global_account_ratio` + `cg_liquidation_coin_list` | — |

---

### Common Mistakes

**Mistake 1 (most common — 8x failure): Using `cg_liquidations` when you need `cg_liquidation_coin_list`**
- `cg_liquidations` → one coin, one timeframe, basic total only
- `cg_liquidation_coin_list(exchange)` → ALL coins, multi-timeframe (1h/4h/12h/24h), per-exchange breakdown
- **Rule:** If the question asks for a ranking, overview, or doesn't specify a single coin → use `cg_liquidation_coin_list`

**Mistake 2 (5x failure): Using `cg_liquidation_analysis` for liquidation rankings**
- `cg_liquidation_analysis` adds a sentiment label to a single-coin total — it is NOT a ranking tool
- **Rule:** "今日爆仓排行" / "各币种爆仓" → always `cg_liquidation_coin_list`

**Mistake 3 (3x failure): Using `long_short_ratio` for historical L/S analysis**
- `long_short_ratio` is a current snapshot (no time-series)
- `cg_global_account_ratio` returns history — use it when the user wants trends or comparison over time
- **Rule:** If the question compares 全网 (global) vs 头部 (top traders) → call BOTH `cg_global_account_ratio` AND `cg_top_account_ratio`

**Mistake 4 (2x failure): Using `cg_coins_market_data` for open interest**
- `cg_coins_market_data` is a bulk snapshot of many coins — not a replacement for dedicated OI or L/S tools
- **Rule:** OI question → `cg_open_interest`. L/S question → `long_short_ratio` or `cg_global_account_ratio`. Never route either to `cg_coins_market_data`.

## Rules

### Tool Call Guidance

**❌ FORBIDDEN TOOLS — NEVER USE:**
- `bash` — Do NOT write scripts to process/format data. Use natural language.
- `write_file` / `read_file` / `edit_file` — Do NOT save intermediate data. Answer directly.
- `learning_log` — ONLY for genuine skill bugs or persistent API errors. NOT for empty responses.
- `echo` — Do NOT use for debugging or output.

**✅ CORRECT PATTERN:**
- Tool returns data → Summarize in natural language → Done
- Tool returns empty/null → Report "no data available" → Done
- Need calculation (%, change, ratio) → Do mental math in reply

**Match tool count to question scope:**
  - 单一指标问题（"BTC 资金费率"、"ETH 多空比"）→ 1 个工具，直接返回
  - 多维度分析（"做多是否合适"、"衍生品体检"）→ 3-5 个工具，综合分析
  - 对比问题（"ETH vs SOL"）→ 每个币种调相同工具，并列对比
- **避免重复调用同一工具。** 除非用户明确要求不同币种/交易所的对比。

**替代方案（按优先级）**：
1. **用户提供自己的 key**（Basic+ 计划）：设 `COINGLASS_API_KEY` 并绕过 sc-proxy 直连
   `https://open-api-v4.coinglass.com`（sc-proxy 会强制覆盖该 header，代理路径下自带 key 无效）。
2. **Apify 爬虫**：用 `apify` skill 抓 coinglass.com 页面上的清算热力图 / Hyperliquid 持仓数据。

对 401 "Upgrade plan" 错误，`cg_request` 会抛 `CoinglassPlanError`，错误信息已含上述引导。

### Learning Log Usage (CRITICAL)

**`learning_log` is FORBIDDEN for:**
- ❌ Empty API responses — just report "no data available"
- ❌ Tool returning None/null — handle gracefully
- ❌ Uncertainty about tool selection — check decision tree first
- ❌ Normal tool errors — retry once, then report failure

**`learning_log` is ONLY for:**
- ✅ Genuine bugs in skill code (wrong data format returned)
- ✅ Persistent API rate limit errors after 2+ retries
- ✅ Missing tools that should exist per skill definition

### ETF Tool Selection
| Query | Primary Tool | Secondary Tool |
|-------|--------------|----------------|
| BTC ETF 资金流入/流出 | `cg_btc_etf_flows()` | `cg_btc_etf_history()` for detailed history |
| ETH ETF 资金流入/流出 | `cg_eth_etf_flows()` / `cg_eth_etf_list()` | — |
| SOL/XRP ETF flows | `cg_sol_etf_flows()` / `cg_xrp_etf_flows()` | — |
| HK ETF flows | `cg_hk_btc_etf_flows()` / `cg_hk_eth_etf_flows()` | — |
| ETF 列表/代码 | `cg_btc_etf_list()` / `cg_eth_etf_list()` | — |
| ETF 溢价/折价 | `cg_btc_etf_premium_discount()` | — |

**ETF 对比问题 workflow:**
```
# BTC vs ETH ETF 对比
btc = cg_btc_etf_flows()
eth = cg_eth_etf_flows()
# Compare the latest day's net flows, summarize in 2-3 sentences
```

## Quick Routing (use this first)

| Query type | Tool |
|---|---|
| 爆仓/liquidation summary (24h, by coin) | `cg_liquidation_coin_list` |
| Individual liquidation orders | `cg_liquidation_orders` |
| Liquidation history for a coin | `cg_coin_liquidation_history` |
| Funding rate | `funding_rate` |
| Long/short ratio (global) | `cg_global_account_ratio` |
| Open interest | `cg_open_interest` |
| Whale activity on Hyperliquid | `cg_hyperliquid_whale_alerts` |
| ETF flows (BTC) | `cg_btc_etf_flows` |

## When to Use Coinglass

Use Coinglass for:
- **衍生品头寸** - 杠杆交易者正在做什么？
- **鲸鱼追踪** - 追踪 Hyperliquid DEX 上的大额头寸
- **资金费率** - 持有永续期货的成本
- **未平仓合约** - 开放头寸的总名义价值
- **多空比** - 杠杆交易者的情绪（全局，头部账户，头部头寸）
- **清算** - 强制平仓，包括热力图和单个订单
- **成交量分析** - 买卖量，CVD，净流模式
- **ETF 流动** - 机构采用（比特币、以太坊、索拉纳、瑞波币、香港）
- **鲸鱼转账** - 链上大额转移（> $10M）
- **期货市场数据** - 支持的币种、交易所、对，和 OHLC 价格历史

## Tool Categories

### 1. Basic Derivatives Analytics (7 tools)

核心衍生品数据用于市场分析：

- `funding_rate(symbol, exchange=None)` - 当前资金费率
- `long_short_ratio(symbol, exchange?, interval?)` - 基础 L/S 比率
- `cg_open_interest(symbol)` - 跨交易所的当前 OI
- `cg_liquidations(symbol, time?)` - 最近清算
- `cg_liquidation_analysis(symbol)` - ❌ Startup 下不可用（依赖 heatmap 端点）
- `cg_supported_coins()` - CoinGlass 支持的所有币种
- `cg_supported_exchanges()` - 所有包含对子的交易所信息

### 2. Advanced Long/Short Ratios (6 tools)

具有多种指标的深度头寸分析：

- `cg_global_account_ratio(symbol, interval?)` - 全局账户 L/S 比率
- `cg_top_account_ratio(symbol, exchange, interval?)` - 头部账户比率
- `cg_top_position_ratio(symbol, exchange, interval?)` - 持仓大小比率
- `cg_taker_exchanges(symbol)` - 跨交易所的买卖量
- `cg_net_position(symbol, exchange)` - 净多头/空头头寸
- `cg_net_position_v2(symbol)` - 增强型净头寸数据

**用例**:
- 智能资金追踪（头部账户 vs 零售）
- 交易所特定情绪
- 头寸大小分布分析

### 3. Advanced Liquidations (4 tools)

用于级联预测的粒度清算追踪：

- `cg_coin_liquidation_history(symbol, interval?, limit?, start_time?, end_time?)` - 跨所有交易所的聚合清算历史
- `cg_pair_liquidation_history(symbol, exchange, interval?, limit?, start_time?, end_time?)` - 单个交易所上的单个对子历史清算
- `cg_liquidation_coin_list(exchange)` - 单个交易所的所有币种
- `cg_liquidation_orders(symbol, exchange, min_liquidation_amount, start_time?, end_time?)` - 最近强制平仓订单

**用例**:
- 识别清算集群
- 跟踪清算模式随时间变化
- 查找大额清算事件 = 级联风险区域

### 4. Hyperliquid Whale Tracking (4 tools)

追踪 Hyperliquid DEX 上的大额交易者（~200 个最近的警报）：

- `cg_hyperliquid_whale_alerts()` - 最近大额头寸开仓/平仓警报
- `cg_hyperliquid_whale_positions()` - 当前鲸鱼头寸，包括 PnL
- `cg_hyperliquid_positions_by_coin(symbol='BTC')` - 持有特定币种的鲸鱼头寸
- `cg_hyperliquid_position_distribution(symbol='BTC')` - 持仓大小分布，包括情绪

**用例**:
- 在 Hyperliquid 上追踪智能资金
- 检测大额头寸变化
- 追踪鲸鱼 PnL 和情绪

### 5. Futures Market Data (5 tools)

市场概览和价格数据：

- `cg_coins_market_data()` - 一个调用即可获取 100 多个币种的全部指标（100+ 币种）
- `cg_pair_market_data(symbol='BTC', exchange=None)` - 对子级指标
- `cg_ohlc_history(symbol, exchange, interval='h4', exchange=None)` - OHLC K线

**用例**:
- 市场筛选（一次调用即可获取所有币种）
- 价格动作分析
- 成交量模式识别

### 6. Volume & Flow Analysis (4 tools)

订单流和资本流动追踪：

- `cg_cumulative_volume_delta(symbol, exchange, interval, limit?, start_time?, end_time?)` - CVD = 买卖差额的累积指标
- `cg_coin_netflow()` - 每个币种的净流入/流出
- `cg_whale_transfers()` - 链上大额转账（> $10M，过去 6 个月）

**用例**:
- 订单流背离检测
- 智能资金追踪
- 机构流动监控

### 7. Bitcoin ETF Data (5 tools)

追踪比特币机构采用情况：

- `cg_btc_etf_flows()` - 每日净流入/流出
- `cg_btc_etf_history()` - 详细历史（价格、NAV、溢价%、份额、资产）
- `cg_btc_etf_list()` - 比特币 ETF 列表
- `cg_hk_btc_etf_flows()` - 香港比特币 ETF 流动

**用例**:
- 机构需求追踪
- 溢价/折价套利
- 区域流动比较（美国 vs 香港地区）

### 8. Other ETF Data (8 tools)

以太坊、索拉纳、瑞波币和香港 ETF：

- `cg_eth_etf_flows()` - 以太坊 ETF 流动
- `cg_eth_etf_list()` - 以太坊 ETF 列表
- `cg_eth_etf_premium_discount()` - 以太坊 ETF 溢价/折价
- `cg_sol_etf_flows()` - 索拉纳 ETF 数据
- `cg_sol_etf_list()` - 索拉纳 ETF 列表
- `cg_xrp_etf_flows()` - 瑞波币 ETF 数据
- `cg_xrp_etf_list()` - 瑞波币 ETF 列表
- `cg_hk_eth_etf_flows()` - 香港以太坊 ETF 流动

**用例**:
- 多资产机构追踪
- 对比流动分析
- 区域偏好分析

## Common Workflows

### Quick Market Scan
```
# Get everything in 3 calls
all_coins = cg_coins_market_data()  # 100+ coins with full metrics
btc_liquidations = cg_liquidations("BTC")
whale_alerts = cg_hyperliquid_whale_alerts()
```

### Deep Position Analysis
```
# BTC positioning across metrics
cg_global_account_ratio("BTC")  # Retail sentiment
cg_top_account_ratio("BTC", "Binance")  # Smart money
cg_net_position_v2("BTC")  # Net positioning
# 注：清算热力图在 Startup 下不可用，见顶部「Plan 权限分级」
```

### ETF Flow Monitoring
```
# Institutional demand
btc_flows = cg_btc_etf_flows()
eth_flows = cg_eth_etf_flows()
sol_flows = cg_sol_etf_flows()
```

### Whale Tracking
```
# Follow the whales
hyperliquid_whales = cg_hyperliquid_whale_alerts()
whale_positions = cg_hyperliquid_whale_positions()
onchain_whales = cg_whale_transfers()  # >$10M on-chain
```

### Volume Analysis
```
# Order flow
cvd = cg_cumulative_volume_delta("BTC", "Binance", "1h", 100)
netflow = cg_coin_netflow()  # All coins
taker_vol = cg_aggregated_taker_volume("BTC", "1h", 100)
```

## Interpretation Guides

### Funding Rates

| Rate (8h) | Read |
|------------|------|
| > +0.05% | Extreme greed — crowded long, squeeze risk |
| +0.01% to +0.05% | Bullish bias, normal |
| -0.005% to +0.01% | Neutral |
| -0.05% to -0.005% | Bearish bias, normal |
| < -0.05% | Extreme fear — crowded short, bounce risk |

Extreme funding often precedes reversals. The crowd is usually wrong at extremes.

### Open Interest + Price Matrix

| OI | Price | Read |
|----|-------|------|
| Up | Up | New longs entering — bullish conviction |
| Up | Down | New shorts entering — bearish conviction |
| Down | Up | Short covering — weaker rally, less conviction |
| Down | Down | Long liquidation — weaker selloff, capitulation |

### Long/Short Ratio

| Ratio | Read |
|-------|------|
| > 1.5 | Crowded long — contrarian bearish |
| 1.1–1.5 | Moderately bullish |
| 0.9–1.1 | Balanced |
| 0.7–0.9 | Moderately bearish |
| < 0.7 | Crowded short — contrarian bullish |

### CVD (Cumulative Volume Delta)

| Pattern | Read |
|---------|------|
| CVD rising, price rising | Strong buy pressure, healthy uptrend |
| CVD falling, price rising | Weak rally, distribution |
| CVD rising, price falling | Accumulation, potential bottom |
| CVD falling, price falling | Strong sell pressure, healthy downtrend |

### ETF Flows

| Flow | Read |
|------|------|
| Large inflows | Institutional buying, bullish |
| Consistent inflows | Sustained demand |
| Large outflows | Institutional selling, bearish |
| Premium to NAV | High demand, bullish sentiment |
| Discount to NAV | Weak demand, bearish sentiment |

## Analysis Patterns

**Multi-metric confirmation**: 结合跨类别的工具进行高置信度信号：
- 资金费率 + L/S 比率 + 清算 = 头寸极端
- CVD + 买卖量 + 鲸鱼警报 = 智能资金方向
- ETF 流动 + 鲸鱼转账 + 未平仓合约 = 机构信心

**Smart money vs retail**: 比较指标以识别背离：
- `cg_top_account_ratio` (智能资金) vs `cg_global_account_ratio` (零售)
- Hyperliquid 鲸鱼头寸 vs 整体多空比

**Cascade prediction**: 使用清算工具进行级联预测：
- `cg_coin_liquidation_history` 显示清算模式随时间变化
- `cg_liquidation_orders` 揭示最近的强制平仓
- 大额清算事件 = 级联风险区域

**Flow divergence**: 追踪资本流动：
- `cg_coin_netflow` 显示资金流向
- `cg_whale_transfers` 揭示大额移动
- ETF 流动显示机构需求

## Performance Optimization

### Batch vs Individual Calls

**✅ OPTIMAL**: 使用批量端点
```
# One call gets 100+ coins
all_coins = cg_coins_market_data()

# One call gets all whale alerts
whales = cg_hyperliquid_whale_alerts()

# One call gets all ETF flows
btc_etf = cg_btc_etf_flows()
```

**❌ INEFFICIENT**: 多个单独调用
```
# Don't do this - wastes API quota
btc = cg_pair_market_data("BTC", "Binance")
eth = cg_pair_market_data("ETH", "Binance")
sol = cg_pair_market_data("SOL", "Binance")
```

### Query Parameters

大多数历史端点支持：
- `interval`: 时间粒度 (1h, 4h, 12h, 24h, 等)
- `limit`: 记录数（默认值不同，最大 1000）
- `start_time`: Unix 时间戳（毫秒）
- `end_time`: Unix 时间戳（毫秒）

示例：
```
cg_coin_liquidation_history(
    symbol="BTC",
    interval="1h",
    limit=100,
    start_time=1704067200000,  # 2024-01-01
    end_time=1704153600000     # 2024-01-02
)
```

## Supported Exchanges

具有期货数据的交易所：
- **一级**: Binance, OKX, Bybit, Gate, KuCoin, MEXC
- **传统**: CME (比特币和以太坊期货), Coinbase
- **去中心化交易所**: Hyperliquid, dYdX, ApeX
- **其他**: Bitfinex, Kraken, HTX, BingX, Crypto.com, CoinEx, Bitget

使用 `cg_supported_exchanges()` 获取完整列表，包含对子详情。

## Important Notes

- **API Key**: 需要 COINGLASS_API_KEY 环境变量
- **币种符号**: 使用标准符号（BTC, ETH, SOL, 等） - 使用 `cg_supported_coins()` 检查
- **交易所**: 使用 `cg_supported_exchanges()` 检查完整列表，包含对子
- **更新频率**:
  - 市场数据: ≤ 1 分钟
  - 资金费率: 每 8 小时（或某些交易所为 1 小时）
  - OHLC: 实时到 1 分钟，取决于间隔
  - ETF 数据: 市场收盘后每日更新
  - 鲸鱼转账: 实时（几分钟内）
- **API 版本**:
  - V4 端点使用 `CG-API-KEY` header（大多数工具）
  - V2 端点使用 `coinglassSecret` header（一些遗留工具）
  - 两者都使用相同的 COINGLASS_API_KEY 环境变量
- **速率限制**: Startup 计划 — 保持批量轮询适度；避免紧密循环
- **历史数据限制**:
  - 清算订单: 过去 7 天，最多 200 条记录
  - 鲸鱼转账: 过去 6 个月，最低 $10M
  - Hyperliquid 警报: ~200 个最近的 大额头寸
  - 其他端点: 通常有几个月到几年的历史
- **计划限制（Startup）**: heatmap、liquidation/order、coins-markets、
  Hyperliquid position 返回 401 Upgrade plan（会抛 `CoinglassPlanError`）。
  用户需要这些数据 → 让用户提供自己的 key（`COINGLASS_DIRECT=1` + 自有
  `COINGLASS_API_KEY` 直连），或用 Apify skill 爬 coinglass.com 页面。

## Data Quality Notes

- **Hyperliquid**: 数据是交易所特定的，不包括其他 DEX
- **鲸鱼转账**: 涵盖比特币、以太坊、波场币、瑞波币、狗狗币、莱特币、Polygon、阿尔戈兰德、比特币现金、索拉纳
- **ETF 数据**: 美国ETFs 在市场收盘后更新（美国东部时间下午 4 点），香港ETFs 在香港市场收盘后更新
- **清算订单**: 限制为 200 条最近的，使用heatmap获取更广泛的视图
- **CVD**: 累积指标 - 重置不是自动的，跟踪变化而不是绝对值

## Version History

- **v3.1.0** (2026-09): Startup plan adaptation
  - Platform key downgraded to Startup; documented full endpoint permission map
  - Added `CoinglassPlanError` with BYOK / Apify guidance on 401 "Upgrade plan"
  - Added `COINGLASS_DIRECT=1` direct mode for user-supplied keys (sc-proxy overwrites user keys)
  - Fixed 4 parameter bugs: coin/pair liquidation history (`exchange_list` / pair symbol),
    aggregated taker volume (`exchange_list`), price history (pair symbol)
- **v3.0.0** (2025-03): Added 36 new tools
  - Advanced liquidations (5 tools)
  - Hyperliquid whale tracking (5 tools)
  - Volume & flow analysis (5 tools)
  - Whale transfers (1 tool)
  - Bitcoin ETF (6 tools)
  - Other ETFs (8 tools)
  - Advanced L/S ratios (6 tools)
- **v2.2.0** (2024): V4 API migration with futures market data
- **v1.0.0** (2024): Initial release with basic derivatives data
