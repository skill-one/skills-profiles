---
name: coinglass
description: '加密衍生品数据：资金费率、持仓量、平仓量、多空比率。


  用于研究永续合约市场或比较ETF资金流（例如BTC资金费率、ETH持仓量）。

  注意：平台API密钥为初创级——平仓热力图、币市场详情、平仓订单簿和Hyperliquid持仓需要更高套餐（参见套餐等级）。'
---

## 计划层级（平台密钥 = 初创，验证 2026-09）

平台注入的 `COINGLASS_API_KEY` 位于 **初创** 计划。工具层级的实际端点访问：

**✅ 初创计划可用**（正常数据）：
- 资金利率（v2/v4）、支持的币种/交易所/交易对、交易对市场
- 未平仓合约（当前 / OHLC 历史记录 / 汇总历史记录）
- 多头/空头比率（全球 / 顶级账户 / 顶级头寸）
- 主动买入/卖出量（单个交易所 + 汇总；汇总需要 `exchange_list`）
- CVD、净头寸（v1/v2）、币种净流量
- 平仓：币种列表、币种/交易对历史（交易对需要 BTCUSDT 格式）、汇总历史记录（需要 `exchange_list`）
- ETF 流动量 / 列表 / 溢价（BTC、ETH、SOL、XRP、HK）
- 大户转账，Hyperliquid 大户警报（仅警报源）
- 价格历史（符号必须是交易对格式，例如 BTCUSDT）

**❌ 初创计划不可用**（401 "升级计划" — 跳过这些，不要调用）：
- `api/futures/coins-markets`（所有币种市场摘要，即 `cg_coins_market_data`） — **不要调用**；使用下面的“全市场/多币种 OHLC 路由”
- `api/futures/liquidation/order`（单个平仓订单）
- `api/futures/liquidation/heatmap/model1` + `aggregated-heatmap/model1` (**平仓热力图完全不可用**)
- `api/hyperliquid/position`, `api/hyperliquid/wallet/position-distribution`（Hyperliquid 位置分布；仅大户警报有效）

**替代方案（优先级顺序）**：
1. **用户自行提供密钥**（基础+计划）：设置 `COINGLASS_API_KEY` 并直接调用
   `https://open-api-v4.coinglass.com`，绕过 sc-proxy（sc-proxy 会覆盖该头部，因此用户密钥对代理路径无效）。
2. **Apify 抓取器**：使用 `apify` 技能抓取 coinglass.com 上的平仓热力图 / Hyperliquid 位置页面。

在收到 401 "升级计划" 响应时，`cg_request` 会引发 `CoinglassPlanError`，并且错误消息已包含此指导。

### 全市场/多币种 OHLC 路由（币种市场不可用）

| 需求 | 使用 | 备注 |
|---|---|---|
| 单个币种的当前 OHLC 和 4h/24h 变化 | `cg_open_interest(symbol)`（取 `exchangeName=="All"` 行） | 在初创计划上可用 |
| 单个币种的资金利率 | `funding_rate(symbol)` | 返回一个带有 `%` 的字符串 |
| 跨币种的 OHLC 历史 | 按时间戳汇总的每个币种的 OHLC 历史 | 将其标记为 "Top-N 汇总" 并使用条形间隔；永远不要将其呈现为全市场 |
| 全市场当前 OHLC 总计 / 每个币种的当前 OHLC | **coingecko 技能** `cg_derivatives(include_tickers='unexpired')`：保持 `contract_type=="perpetual"`，按 `index_id` 汇总 `open_interest`（USD） | 交易所报告的，包括小型交易所，运行值高于 CoinGlass；仅当前值，无历史记录；始终在图表和文本中注明来源 |

**不要** 将来自不同来源（CoinGlass Top-N、CoinGecko 全市场、彭博或其他第三方）的数字绘制在同一个图表上作为比较或参考线。

## 平仓热力图（❌ 初创计划不可用 — 归档使用）

`cg_liquidation_analysis` 返回所有零且无法使用。两个热力图端点（`heatmap/model1` 和
`aggregated-heatmap/model1`）在初创计划上都返回 401 升级计划。

如果需要热力图数据：让用户使用基础+密钥并直接调用（见上述替代方案），或使用 Apify 抓取页面。

```python
# 仅在使用用户拥有的更高层级密钥时才工作（直接，不是通过 sc-proxy）
from tools._api import cg_request

# 全市场汇总热力图（推荐，无需交易所）
# range 支持：12h、24h、3d、7d、30d、90d、180d、1y
data = cg_request("api/futures/liquidation/aggregated-heatmap/model1",
                  params={"symbol": "BTC", "range": "24h"})

# 响应结构：
# data["y_axis"]                   → 价格水平（低到高）
# data["liquidation_leverage_data"] → [[y_idx, leverage, usd_value], ...]
# data["price_candlesticks"]        → OHLCV 蜡烛图；最后一个收盘价 = 当前价格
# data["update_time"]               → 更新时间戳

# 如何解析：
from collections import defaultdict
y_axis = data["y_axis"]
current_price = float(data["price_candlesticks"][-1][4])
price_liq = defaultdict(float)
for y_idx, leverage, usd_val in data["liquidation_leverage_data"]:
    if 0 <= y_idx < len(y_axis):
        price_liq[y_axis[y_idx]] += usd_val

longs  = {p: v for p, v in price_liq.items() if p < current_price}  # 多头平仓（在下跌过程中触发）
shorts = {p: v for p, v in price_liq.items() if p > current_price}  # 空头平仓（在上涨过程中触发）
```

## 脚本使用

脚本模式技能 — 读取此文件，然后从 `bash` 块中调用：

```bash
python3 - <<'EOF'
import sys, json
sys.path.insert(0, "/data/workspace/skills/coinglass")
from exports import funding_rate, cg_open_interest, cg_liquidations

print(funding_rate(symbol="BTC"))
print(cg_open_interest(symbol="BTC"))
EOF
```

阅读 `exports.py` 获取可用函数的完整列表和确切的签名。常用函数：`funding_rate`，`long_short_ratio`，
`cg_open_interest`，`cg_liquidations`，`cg_liquidation_analysis`，
`cg_global_account_ratio`，`cg_top_account_ratio`，`cg_top_position_ratio`，
`cg_taker_exchanges`，`cg_net_position`，`cg_supported_coins`，
`cg_supported_exchanges`，`cg_coins_market_data`，`cg_pair_market_data`，
`cg_ohlc_history`，`cg_hyperliquid_whale_alerts`,
`cg_hyperliquid_whale_positions`，`cg_taker_volume_history`,
`cg_aggregated_taker_volume`，`cg_cumulative_volume_delta`，
`cg_coin_netflow`，`cg_whale_transfers`，`cg_btc_etf_flows`，
`cg_eth_etf_flows`，`cg_sol_etf_flows`。

# Coinglass

Coinglass 提供了最全面的加密衍生品和机构数据。37 个工具涵盖期货头寸、大户追踪、成交量分析、平仓和 ETF 流动。

**API 计划**：初创（平台密钥降级；见顶部的“计划层级”）
**速率限制**：此计划上的请求限制较低；保持批量调用适度
**API 版本**：V4（与 V2 向后兼容）
**总工具数**：8 类中的 37 个

## 函数参考（完整签名 + 返回形状）

所有函数都位于 `exports.py` 中。大多数返回 `Optional[List[Dict]]` 或
`Optional[Dict]`。None 表示上游调用失败或返回空 — 始终在索引之前进行检查。

### ⚠️ 字段命名约定（首先阅读此内容）

CoinGlass v4 API 对几乎所有数据字段使用 **camelCase**，平仓端点中有一些遗留的 snake_case 异常。在脚本之前不要假设 snake_case — `inspect` 字典。

- camelCase: `openInterest`, `volUsd`, `longRate`, `shortVolUsd`,
  `exchangeName`, `nextFundingTime`, `fundingIntervalHours`,
  `oichangePercent`, `h4OIChangePercent`, `avgFundingRateBySymbol`,
  `tokenAmount`, `liquidationUsd`（在某些端点中）
- snake_case（遗留，仅在 `cg_liquidations` 中）：`liquidation_usd`,
  `longLiquidation_usd`, `shortLiquidation_usd`
- `rate` 字段（资金）是字符串，带有 "+" / "-" / "%" — 使用 `float(r.rstrip('%').lstrip('+'))` 以数值方式比较
- `avgFundingRateBySymbol`（在 `cg_open_interest` 行中）是一个数字，已经以百分比表示 — `0.005313` 表示 0.0053%/8h。**不要乘以 100**。合理范围：BTC 资金通常在 ±0.01%/8h；任何高于 ~0.1%/8h 的几乎肯定是单位错误。
- 时间戳是毫秒 Unix 纪元（例如 `1777881600000`）

### 资金 & 未平仓合约

| 函数 | 签名 |
|---|---|
| `funding_rate(symbol, exchange=None)` | dict — 键：`symbol`, `exchange`, `rate`（str）, `num_exchanges`, `exchanges_data`（交易所信息列表） |
| `cg_open_interest(symbol='BTC', interval='0')` | 列表，每个交易所一个字典 — 键：`symbol`, `openInterest`, `volUsd`, `oichangePercent`, `h4OIChangePercent`, `h24VolChangePercent`, `volChangePercent7d`, `avgFundingRateBySymbol`, `exchangeName`, `exchangeLogo` |

### 多头/空头比率

| 函数 | 签名 |
|---|---|
| `long_short_ratio(symbol='BTC', interval='h4')` | 列表 — 顶级项目是汇总；`list` 字段内有按交易所的细分。键：`longRate`, `shortRate`, `longVolUsd`, `shortVolUsd`, `totalVolUsd`, `list` |
| `cg_global_account_ratio(symbol='BTC', exchange='Binance', interval='1h')` | 历史条形图列表 |
| `cg_top_account_ratio(symbol='BTC', exchange='Binance', interval='1h')` | 列表 — 顶级交易员账户比率 |
| `cg_top_position_ratio(symbol='BTC', exchange='Binance', interval='1h')` | 列表 — 顶级交易员头寸大小比率 |
| `cg_taker_exchanges(symbol='BTC', range_type='4h')` | 列表 — 跨交易所的主动买入/卖出 |
| `cg_net_position(symbol='BTC', exchange='Binance', interval='1h')` | 列表 — 随时间推移的净多头/空头 USD |

### 平仓

| 函数 | 签名 |
|---|---|
| `cg_liquidations(symbol='BTC', time_type='h24')` | 列表，每个交易所一个字典，第一个是 `'All'` 行。键：`exchange`, `liquidation_usd`, `longLiquidation_usd`, `shortLiquidation_usd`（注意：遗留的 snake_case 字段） |
| `cg_liquidation_analysis(symbol='BTC', time_type='h24')` | 字典 — 汇总网络范围内的统计数据 |
| `cg_coin_liquidation_history(symbol='BTC', interval='h4')` | 历史平仓条形图列表 |
| `cg_pair_liquidation_history(symbol='BTC', exchange='Binance', interval='h4')` | 列表 — 在一个交易所上对单个交易对的历史平仓 |
| `cg_liquidation_coin_list(symbol=None)` | 所有币种的平仓摘要列表 |
| `cg_liquidation_orders(symbol='BTC', exchange=None)` | 列表 — 近期的单个平仓订单 |

### 期货市场数据

| 函数 | 签名 |
|---|---|
| `cg_supported_coins()` | List[str] — CoinGlass 支持的符号列表 |
| `cg_supported_exchanges()` | 交易所信息字典列表 |
| `cg_coins_market_data(symbol=None)` | ❌ 初创计划不可用（401） — 见“全市场/多币种 OHLC 路由” |
| `cg_pair_market_data(symbol='BTC', exchange=None)` | 列表 — 交易对级别的快照 |
| `cg_ohlc_history(symbol='BTC', interval='h4', exchange=None)` | OHLCV 条形图列表 |

### Hyperliquid 大户追踪

| 函数 | 签名 |
|---|---|
| `cg_hyperliquid_whale_alerts()` | 列表 — 近期的大头寸警报 |
| `cg_hyperliquid_whale_positions()` | 列表 — 当前开放的鲸户头寸 |
| `cg_hyperliquid_positions_by_coin(symbol='BTC')` | 列表 — 持有特定币种的鲸户 |
| `cg_hyperliquid_position_distribution(symbol='BTC')` | 字典 — 多头/空头头寸大小分布 |

### 成交量 / 流动

| 函数 | 签名 |
|---|---|
| `cg_taker_volume_history(symbol='BTC', exchange='Binance', interval='1h', limit=1000, start_time=None, end_time=None)` | 列表 — 主动买入/卖出成交量条形图 |
| `cg_aggregated_taker_volume(symbol='BTC', interval='h4')` | 列表 — 跨所有交易所的汇总 |
| `cg_cumulative_volume_delta(symbol='BTC', exchange='Binance', interval='1h', limit=1000, start_time=None, end_time=None)` | 列表 — CVD 条形图 |
| `cg_coin_netflow(symbol=None)` | 列表 — 每个币种的净流入/流出 |
| `cg_whale_transfers()` | 字典 — 近期的链上大额转账 |

### ETF 流动

| 函数 | 签名 |
|---|---|
| `cg_btc_etf_flows()` | 列表 — 每日 US BTC ETF 流动 |
| `cg_btc_etf_history(etf_ticker=None)` | 列表 — 历史 AUM/流动 |
| `cg_btc_etf_list()` | BTC ETF 符号列表 + AUM |
| `cg_btc_etf_premium_discount()` | 列表 — 相对于 NAV 的溢价/折价 % |
| `cg_hk_btc_etf_flows()` | 列表 — 香港 BTC ETF 流动 |
| `cg_eth_etf_flows()` / `cg_eth_etf_list()` / `cg_eth_etf_premium_discount()` / `cg_hk_eth_etf_flows()` | ETH ETF 对等物 |
| `cg_sol_etf_flows()` / `cg_sol_etf_list()` | SOL ETF 数据 |
| `cg_xrp_etf_flows()` / `cg_xrp_etf_list()` | XRP ETF 数据 |

### 示例响应（最常用的函数）

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

## 工具选择指南

### 决策树

**步骤 1：这是关于平仓吗？**

```
平仓查询?
├─ 是 → 有多少币种？
│   ├─ 所有币种 / 排名 / 摘要
│   │   └─ → cg_liquidation_coin_list  ✅（大多数平仓查询都落在这里）
│   ├─ 一个币种，需要随时间推移的历史
│   │   └─ → cg_coin_liquidation_history
│   ├─ 一个币种，需要特定订单（价格/方向/USD）
│   │   └─ → cg_liquidation_orders
│   └─ 一个币种，只需要快速总计 + 情感标签
│       └─ → cg_liquidation_analysis  (很少需要；仅当明确为“简单摘要”时)
```

**步骤 2：这是关于多头/空头比率吗？**

```
多头/空头查询?
├─ 历史时间序列，随时间推移的趋势，L/S 比率变化
│   └─ → cg_global_account_ratio  (所有账户)
│      or cg_top_account_ratio    (仅顶级交易员)
│      or cg_top_position_ratio   (按头寸大小)
└─ 仅当前快照（不需要历史）
    └─ → long_short_ratio
```

**步骤 3：这是关于未平仓合约吗？**

```
OHLC 查询?
└─ → cg_open_interest  (始终 — 不要使用 cg_coins_market_data 作为上述任何内容的替代)
```

**步骤 4：这是一个市场概览 / 情感查询吗？**

```
情感 / 预交易检查?
└─ 使用：funding_rate + long_short_ratio + cg_open_interest
   不要使用 cg_coins_market_data 作为上述任何内容的替代
```

---

### 关键词 → 工具查找

| 关键词 / 模式 | 正确工具 | ❌ 不要使用 |
|---|---|---|
| 平仓排名 / 今天平仓 / 所有币种平仓 | `cg_liquidation_coin_list` | `cg_liquidations` |
| 24h 平仓摘要 | `cg_liquidation_coin_list` | `cg_liquidation_analysis` |
| 全球账户 L/S 比率 | `cg_global_account_ratio` | `long_short_ratio` |
| 顶级交易员 L/S 比率 | `cg_top_account_ratio` | `long_short_ratio` |
| 未平仓合约 | `cg_open_interest` | `cg_coins_market_data` |
| 市场情感 / 位置分析 | `funding_rate` + `long_short_ratio` + `cg_open_interest` | `cg_coins_market_data` |
| BTC 多头预交易检查 | `funding_rate` + `cg_global_account_ratio` + `cg_liquidation_coin_list` | — |

---

### 常见错误

**错误 1（最常见 — 8x 失败）：使用 `cg_liquidations` 而不是 `cg_liquidation_coin_list`**
- `cg_liquidations` → 一个币种，一个时间段，仅基本总计
- `cg_liquidation_coin_list(exchange)` → 所有币种，多时间段（1h/4h/12h/24h），按交易所细分
- **规则**：如果问题要求排名、概览或不指定单个币种 → 使用 `cg_liquidation_coin_list`

**错误 2（5x 失败）：使用 `cg_liquidation_analysis` 进行平仓排名**
- `cg_liquidation_analysis` 为单个币种总计添加情感标签 — 它不是排名工具
- **规则**：“今天平仓排名” / “按币种平仓” → 始终 `cg_liquidation_coin_list`

**错误 3（3x 失败）：使用 `long_short_ratio` 进行历史 L/S 分析**
- `long_short_ratio` 是当前快照（没有时间序列）
- `cg_global_account_ratio` 返回历史 — 使用它当用户想要趋势或随时间推移的比较
- **规则**：如果问题比较全球账户与顶级交易员 → 调用 `cg_global_account_ratio` AND `cg_top_account_ratio`

**错误 4（2 次失败）：使用 `cg_coins_market_data` 查询未平仓合约**
- `cg_coins_market_data` 是多个币种的快照集合——它不能替代专门的未平仓合约（OI）或多空工具
- **规则：** OI 问题 → `cg_open_interest`。多空问题 → `long_short_ratio` 或 `cg_global_account_ratio`。绝对不要将任何问题路由到 `cg_coins_market_data`。

## 规则

### 工具调用指南

**❌ 禁止使用的工具——绝对禁止使用：**
- `bash` — 不要编写脚本来处理/格式化数据。使用自然语言。
- `write_file` / `read_file` / `edit_file` — 不要保存中间数据。直接回答。
- `learning_log` — 仅用于真实的技能错误或持续的 API 错误。不用于空响应。
- `echo` — 不要用于调试或输出。

**✅ 正确的模式：**
- 工具返回数据 → 用自然语言总结 → 完成
- 工具返回空/空值 → 报告“无可用数据” → 完成
- 需要计算（百分比、变化、比率）→ 在回复中进行心算

**使工具数量与问题范围匹配：**
  - 单指标问题（“BTC 资金费率”、“ETH 多空比率”）→ 1 个工具，直接回答
  - 多维度分析（“现在是长仓的好时机吗”、“衍生品健康状况”）→ 3-5 个工具，综合分析
  - 比较（“ETH vs SOL”）→ 每个币种使用相同工具，并排显示
- **避免重复调用同一个工具**，除非用户明确要求跨币种/跨交易所比较。

### 学习日志使用（关键）

**`learning_log` 禁止用于：**
- ❌ 空的 API 响应 — 直接报告“无可用数据”
- ❌ 工具返回 None/空值 — 优雅处理
- ❌ 对工具选择不确定 — 首先检查决策树
- ❌ 正常工具错误 — 重试一次，然后报告失败

**`learning_log` 仅用于：**
- ✅ 技能代码中的真实错误（返回错误的数据格式）
- ✅ 持续的 API 速率限制错误（重试 2 次后）
- ✅ 根据技能定义缺失的工具

### ETF 工具选择
| 查询 | 主要工具 | 次要工具 |
|-------|--------------|----------------|
| BTC ETF 流入/流出 | `cg_btc_etf_flows()` | `cg_btc_etf_history()` 用于详细历史 |
| ETH ETF 流入/流出 | `cg_eth_etf_flows()` | — |
| SOL/XRP ETF 流动 | `cg_sol_etf_flows()` / `cg_xrp_etf_flows()` | — |
| HK ETF 流动 | `cg_hk_btc_etf_flows()` / `cg_hk_eth_etf_flows()` | — |
| ETF 列表 / 指令牌 | `cg_btc_etf_list()` / `cg_eth_etf_list()` | — |
| ETF 溢价 / 折扣 | `cg_btc_etf_premium_discount()` | — |

**ETF 对比工作流：**
```
# BTC vs ETH ETF 对比
btc = cg_btc_etf_flows()
eth = cg_eth_etf_flows()
# 对比最新一天的净流入，用 2-3 句话总结
```

## 快速路由（首先使用）

| 查询类型 | 工具 |
|---|---|
| 流动性清算摘要（24 小时，按币种） | `cg_liquidation_coin_list` |
| 单个流动性清算订单 | `cg_liquidation_orders` |
| 某个币种的流动性清算历史 | `cg_coin_liquidation_history` |
| 资金费率 | `funding_rate` |
| 多空比率（全局） | `cg_global_account_ratio` |
| 未平仓合约 | `cg_open_interest` |
| Hyperliquid 上的鲸鱼活动 | `cg_hyperliquid_whale_alerts` |
| ETF 流动（BTC） | `cg_btc_etf_flows` |

## 何时使用 Coinglass

使用 Coinglass 进行：
- **衍生品头寸** - 杠杆交易者在做什么？
- **鲸鱼追踪** - 追踪 Hyperliquid DEX 上的大仓位
- **资金费率** - 持有永续期货的成本
- **未平仓合约** - 开放仓位的名义总价值
- **多空比率** - 杠杆交易者的情绪（全局、顶级账户、顶级仓位）
- **清算** - 强制仓位关闭，带有热力图和单个订单
- **成交量分析** - 主动成交量、CVD、净流模式
- **ETF 流动** - 机构采用（比特币、以太坊、索拉纳、XRP、香港）
- **鲸鱼转账** - 大的链上移动（> $10M）
- **期货市场数据** - 支持的币种、交易所、对、OHLC 价格历史

## 工具类别

### 1. 基础衍生品分析（7 个工具）

市场分析的核心衍生品数据：

- `funding_rate(symbol, exchange?)` - 当前资金费率
- `long_short_ratio(symbol, exchange?, interval?)` - 基础多空比率
- `cg_open_interest(symbol)` - 跨交易所的当前 OI
- `cg_liquidations(symbol, time?)` - 最近清算
- `cg_liquidation_analysis(symbol)` - ❌ 在 Startup 上不可用（取决于热力图端点）
- `cg_supported_coins()` - 所有支持的币种
- `cg_supported_exchanges()` - 所有有对子的交易所

### 2. 高级多空比率（6 个工具）

使用多个指标进行深度头寸分析：

- `cg_global_account_ratio(symbol, interval?)` - 基于账户的多空比率
- `cg_top_account_ratio(symbol, exchange, interval?)` - 顶级交易账户比率
- `cg_top_position_ratio(symbol, exchange, interval?)` - 按规模最大的顶级仓位
- `cg_taker_exchanges(symbol)` - 按交易所的主动买入/卖出
- `cg_net_position(symbol, exchange)` - 净多/空仓位
- `cg_net_position_v2(symbol)` - 增强型净仓位数据

**用例**：
- 智能资金追踪（顶级账户 vs 零售）
- 交易所特定情绪
- 仓位规模分布分析

### 3. 高级清算（4 个工具）

用于级联预测的粒度清算追踪：

- `cg_coin_liquidation_history(symbol, interval?, limit?, start_time?, end_time?)` - 跨所有交易所聚合
- `cg_pair_liquidation_history(symbol, exchange, interval?, limit?, start_time?, end_time?)` - 交易所特定对
- `cg_liquidation_coin_list(exchange)` - 交易所上的所有币种
- `cg_liquidation_orders(symbol, exchange, min_liquidation_amount, start_time?, end_time?)` - 单个订单（过去 7 天，最多 200）

**用例**：
- 识别清算集群
- 跟踪清算模式随时间变化
- 查找大型清算事件

### 4. Hyperliquid 鲸鱼追踪（4 个工具）

追踪 Hyperliquid DEX 上的大交易者（约 200 个最近警报）：

- `cg_hyperliquid_whale_alerts()` - 最近的大仓位开/平仓（> $1M）
- `cg_hyperliquid_whale_positions()` - 当前鲸鱼仓位，带 PnL
- `cg_hyperliquid_positions_by_coin()` - 按币种分组的所有仓位
- `cg_hyperliquid_position_distribution()` - 按规模分布，带情绪

**用例**：
- 追踪 Hyperliquid 上的智能资金
- 检测大型仓位变化
- 追踪鲸鱼 PnL 和情绪

### 5. 期货市场数据（5 个工具）

市场概览和价格数据：

- `cg_coins_market_data()` - ❌ 在 Startup 上不可用；多币种数据请参阅“全市场 / 多币种 OI 路由”
- `cg_pair_market_data(symbol, exchange)` - 特定对指标
- `cg_ohlc_history(symbol, exchange, interval, limit?)` - OHLC 蜡烛图
- `cg_taker_volume_history(symbol, exchange, interval, limit?, start_time?, end_time?)` - 对特定主动成交量
- `cg_aggregated_taker_volume(symbol, interval, limit?, start_time?, end_time?)` - 跨交易所聚合

**用例**：
- 市场筛选（一次扫描所有币种）
- 价格行动分析
- 成交量模式识别

### 6. 成交量 & 流动分析（4 个工具）

订单流和资本流动追踪：

- `cg_cumulative_volume_delta(symbol, exchange, interval, limit?, start_time?, end_time?)` - CVD = 买入 - 卖出的运行总和
- `cg_coin_netflow()` - 流入/流出币种的资本
- `cg_whale_transfers()` - 大的链上转账（> $10M，过去 6 个月）

**用例**：
- 订单流背离检测
- 智能资金追踪
- 机构运动监控

### 7. 比特币 ETF 数据（5 个工具）

追踪机构比特币采用情况：

- `cg_btc_etf_flows()` - 每日净流入/流出
- `cg_btc_etf_premium_discount()` - ETF 价格 vs NAV
- `cg_btc_etf_history()` - 全面历史（价格、NAV、溢价%、份额、资产）
- `cg_btc_etf_list()` - 比特币 ETF 列表
- `cg_hk_btc_etf_flows()` - 香港比特币 ETF 流动

**用例**：
- 机构需求追踪
- 溢价/折扣套利
- 区域流动比较（美国 vs 香港）

### 8. 其他 ETF 数据（8 个工具）

以太坊、索拉纳、XRP 和香港 ETF：

- `cg_eth_etf_flows()` - 以太坊 ETF 流动
- `cg_eth_etf_list()` - 以太坊 ETF 列表
- `cg_eth_etf_premium_discount()` - ETH ETF 溢价/折扣
- `cg_sol_etf_flows()` - 索拉纳 ETF 流动
- `cg_sol_etf_list()` - 索拉纳 ETF 列表
- `cg_xrp_etf_flows()` - XRP ETF 流动
- `cg_xrp_etf_list()` - XRP ETF 列表
- `cg_hk_eth_etf_flows()` - 香港以太坊 ETF 流动

**用例**：
- 多资产机构追踪
- 比较流动分析
- 区域偏好分析

## 常见工作流

### 快速市场扫描
```
# 3 次调用获取所有信息
btc_oi = cg_open_interest("BTC")  # coins-markets 在 Startup 上受计划限制
btc_liquidations = cg_liquidations("BTC")
whale_alerts = cg_hyperliquid_whale_alerts()
```

### 深度头寸分析
```
# BTC 跨指标定位
cg_global_account_ratio("BTC")  # 零售情绪
cg_top_account_ratio("BTC", "Binance")  # 智能资金
cg_net_position_v2("BTC")  # 净定位
# 注意：热力图在 Startup 上不可用；请参阅顶部的“计划层级”
```

### ETF 流动监控
```
# 机构需求
btc_flows = cg_btc_etf_flows()
eth_flows = cg_eth_etf_flows()
sol_flows = cg_sol_etf_flows()
```

### 鲸鱼追踪
```
# 追踪鲸鱼
hyperliquid_whales = cg_hyperliquid_whale_alerts()
whale_positions = cg_hyperliquid_whale_positions()
onchain_whales = cg_whale_transfers()  # >$10M 链上
```

### 成交量分析
```
# 订单流
cvd = cg_cumulative_volume_delta("BTC", "Binance", "1h", 100)
netflow = cg_coin_netflow()  # 所有币种
taker_vol = cg_aggregated_taker_volume("BTC", "1h", 100)
```

## 解释指南

### 资金费率

| 率（8 小时） | 读取 |
|------------|------|
| > +0.05% | 极端贪婪——拥挤多头，挤压风险 |
| +0.01% 到 +0.05% | 看涨倾向，正常 |
| -0.005% 到 +0.01% | 中性 |
| -0.05% 到 -0.005% | 看跌倾向，正常 |
| < -0.05% | 极端恐惧——拥挤空头，反弹风险 |

极端资金费率通常预示着反转。群众在极端情况下通常是错的。

### 未平仓合约 + 价格矩阵

| OI | 价格 | 读取 |
|----|-------|------|
| 上升 | 上升 | 新多头进入——看涨信念 |
| 上升 | 下降 | 新空头进入——看跌信念 |
| 下降 | 上升 | 空头平仓——较弱反弹，信念较弱 |
| 下降 | 下降 | 多头清算——较弱抛售，恐慌 |

### 多空比率

| 比率 | 读取 |
|-------|------|
| > 1.5 | 拥挤多头——逆向看跌 |
| 1.1–1.5 | 适度看涨 |
| 0.9–1.1 | 平衡 |
| 0.7–0.9 | 适度看跌 |
| < 0.7 | 拥挤空头——逆向看涨 |

### CVD（累积成交量差）

| 模式 | 读取 |
|---------|------|
| CVD 上升，价格上升 | 强劲买入压力，健康上涨趋势 |
| CVD 下降，价格上升 | 弱势反弹，派发 |
| CVD 上升，价格下降 | 累积，潜在底部 |
| CVD 下降，价格下降 | 强势卖出压力，健康下跌趋势 |

### ETF 流动

| 流动 | 读取 |
|------|------|
| 大额流入 | 机构买入，看涨 |
| 持续流入 | 持续需求 |
| 大额流出 | 机构卖出，看跌 |
| 溢价于 NAV | 高需求，看涨情绪 |
| 折扣于 NAV | 需求疲软，看跌情绪 |

## 分析模式

**多指标确认**：跨类别组合工具以获得高置信度信号：
- 资金费率 + 多空比率 + 清算 = 定位极端
- CVD + 主动成交量 + 鲸鱼警报 = 智能资金方向
- ETF 流动 + 鲸鱼转账 + 未平仓合约 = 机构信念

**智能资金 vs 零售**：比较指标以识别背离：
- `cg_top_account_ratio`（智能资金）vs `cg_global_account_ratio`（零售）
- Hyperliquid 鲸鱼仓位 vs 整体多空比率

**级联预测**：使用清算工具预测波动性：
- `cg_coin_liquidation_history` 显示清算模式随时间变化
- `cg_liquidation_orders` 揭示最近的强制关闭
- 大型清算事件 = 级联风险区域

**流动背离**：追踪资本流动：
- `cg_coin_netflow` 显示资金流向
- `cg_whale_transfers` 揭示大额移动
- ETF 流动显示机构需求

## 性能优化

### 批量 vs 单个调用

**✅ 最佳**：使用批量端点
```
# 全市场当前 OI: coingecko cg_derivatives (coins-markets 在 Startup 上受计划限制)

# 一次调用获取所有鲸鱼警报
whales = cg_hyperliquid_whale_alerts()

# 一次调用获取所有 ETF 流动
btc_etf = cg_btc_etf_flows()
```

**❌ 低效**：多个单个调用
```
# 不要这样做 - 浪费 API 配额
btc = cg_pair_market_data("BTC", "Binance")
eth = cg_pair_market_data("ETH", "Binance")
sol = cg_pair_market_data("SOL", "Binance")
```

### 查询参数

大多数历史端点支持：
- `interval`：时间粒度（1h, 4h, 12h, 24h 等）
- `limit`：记录数量（默认值不同，最大 1000）
- `start_time`：Unix 时间戳（毫秒）
- `end_time`：Unix 时间戳（毫秒）

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

## 支持的交易所

具有期货数据的交易所：
- **一级**：Binance、OKX、Bybit、Gate、KuCoin、MEXC
- **传统**：CME（比特币和以太坊期货）、Coinbase
- **去中心化交易所**：Hyperliquid、dYdX、ApeX
- **其他**：Bitfinex、Kraken、HTX、BingX、Crypto.com、CoinEx、Bitget

使用 `cg_supported_exchanges()` 获取完整列表及对子详情。

## 重要说明

- **API Key**：需要 COINGLASS_API_KEY 环境变量
- **符号**：使用标准符号（BTC、ETH、SOL 等）- 使用 `cg_supported_coins()` 查询
- **交易所**：使用 `cg_supported_exchanges()` 查询完整列表及对子
- **更新频率**：
  - 市场数据：≤ 1 分钟
  - 资金费率：每 8 小时（某些交易所为 1 小时）
  - OHLC：实时到 1 分钟，取决于间隔
  - ETF 数据：每日（收盘后）
  - 鲸鱼转账：实时（几分钟内）
- **API 版本**：
  - V4 端点使用 `CG-API-KEY` 头（大多数工具）
  - V2 端点使用 `coinglassSecret` 头（一些遗留工具）
  - 两者都使用相同的 COINGLASS_API_KEY 环境变量
- **速率限制**：Startup 计划 — 保持批量轮询适度；避免紧密循环
- **历史数据限制**：
  - 清算订单：过去 7 天，最多 200 条记录
  - 鲸鱼转账：过去 6 个月，最低 $10M
  - Hyperliquid 警报：约 200 个最近大仓位
  - 其他端点：通常有几个月到几年的历史
- **计划限制（Startup）**：heatmap、liquidation/order、coins-markets、
  Hyperliquid 位置返回 401 升级计划（引发 `CoinglassPlanError`）。
  如果用户需要这些数据 → 让他们提供自己的密钥（`COINGLASS_DIRECT=1` + 自己的
  `COINGLASS_API_KEY`，直接调用），或使用 Apify 技能抓取 coinglass.com 页面。

## 数据质量说明

- **Hyperliquid**：数据是交易所特定的，不包括其他 DEX
- **鲸鱼转账**：涵盖比特币、以太坊、波场、瑞波、狗币、莱特币、Polygon、Algorand、比特币现金、索拉纳
- **ETF 数据**：美国 ETF 在收盘后（美国东部时间下午 4 点）更新，香港 ETF 在香港市场收盘后更新
- **清算订单**：限制为 200 个最近记录，使用热力图获取更广泛的视图
- **CVD**：累积指标 - 重置不是自动的，跟踪变化而不是绝对值

## 版本历史

- **v3.1.0** (2026-09): 启动计划适配
  - 平台密钥降级为启动计划；记录了完整的端点权限映射
  - 添加了 `CoinglassPlanError`，并在 401 "升级计划" 错误中提供 BYOK / Apify 指导
  - 添加了 `COINGLASS_DIRECT=1` 直接模式，用于用户提供的密钥（sc-proxy 会覆盖用户密钥）
  - 修复了 4 个参数错误：币/对清算历史（`exchange_list` / 对象符号）、聚合做市商量（`exchange_list`）、价格历史（对象符号）
- **v3.0.0** (2025-03)：新增 36 个工具
  - 高级清算（5 个工具）
  - Hyperliquid 庞物追踪（5 个工具）
  - 量价流分析（5 个工具）
  - 庞物转账（1 个工具）
  - 比特币 ETF（6 个工具）
  - 其他 ETF（8 个工具）
  - 高级 L/S 比率（6 个工具）
- **v2.2.0** (2024)：迁移至 V4 API，包含期货市场数据
- **v1.0.0** (2024)：初始发布，包含基础衍生品数据
