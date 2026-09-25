## 脚本使用说明

脚本模式技能 — 请先阅读此文件，然后从 `bash` 块中调用：

```bash
python3 - <<'EOF'
import sys, json
sys.path.insert(0, "/data/workspace/skills/coingecko")
from exports import coin_price, cg_trending, cg_global

print(coin_price(coin_ids="bitcoin,ethereum"))
print(cg_trending())
EOF
```

请阅读 `exports.py` 获取所有可用函数的完整列表。常用函数：
`coin_price`, `coin_ohlc`, `coin_chart`, `cg_trending`,
`cg_top_gainers_losers`, `cg_new_coins`, `cg_global`, `cg_global_defi`,
`cg_categories`, `cg_derivatives`, `cg_coins_markets`, `cg_coin_data`,
`cg_coin_tickers`, `cg_search`, `cg_token_price`, `cg_coin_by_contract`.


# CoinGecko 技能


## 函数参考（签名）

所有公共函数都在 `exports.py` 中。`coin_id` 是 CoinGecko ID
（例如 `bitcoin`, `ethereum`） — 如果不确定，请先使用 `cg_search(query)`。
`vs_currency` 默认为 `usd`。

### 价格与图表
| 函数 | 描述 |
|---|---|
| `coin_price(coin_ids, timestamps=None, vs_currency='usd')` | 当前或历史价格。`coin_ids` = 类似 `"bitcoin,ethereum"` 的逗号字符串。`timestamps` = 历史使用的 Unix 时间戳列表（默认：现在）。 |
| `coin_ohlc(coin_id, days=30, vs_currency='usd')` | 最近 N 天的 OHLC 柱状图。返回 `[ts, o, h, l, c]` 列表。粒度自动选择：1d=30分钟，7-30d=4小时，30d+=4小时。 |
| `coin_chart(coin_id, days=30, vs_currency='usd')` | 价格 + 市值 + 总成交量时间序列。返回 `{prices, market_caps, total_volumes}`（每个列表为 `[ts, val]`）。 |

### 发现
| 函数 | 描述 |
|---|---|
| `cg_trending()` | 过去 24 小时内趋势中的币种、NFT、板块。 |
| `cg_top_gainers_losers(vs_currency='usd', duration='24h')` | 顶部涨跌。`duration` = `1h`/`24h`/`7d`/`14d`/`30d`/`60d`/`1y`。 |
| `cg_new_coins()` | 最近上线的币种。 |
| `cg_search(query)` | 按名称搜索币种/交易所/板块。 |

### 市场数据
| 函数 | 描述 |
|---|---|
| `cg_global()` | 全球加密市场：总市值、成交量、占比。 |
| `cg_global_defi()` | 全球 DeFi：TVL、占比、顶级协议。 |
| `cg_coins_markets(vs_currency='usd', order='market_cap_desc', per_page=100, page=1, sparkline=False, price_change_percentage='24h', category=None, ids=None)` | 带有完整市场数据的顶级币种。 |
| `cg_coin_data(coin_id, localization=False, tickers=False, market_data=True, community_data=False, developer_data=False, sparkline=False)` | 单个币种的详细数据。 |
| `cg_coin_tickers(coin_id, exchange_ids=None, include_exchange_logo=False, page=1, order='volume_desc', depth=False)` | 币种的交易地点及成交量。 |
| `cg_coins_list(include_platform=False)` | 所有币种 ID/符号（用于解析）。 |

### 板块 / 衍生品 / NFT
| 函数 | 描述 |
|---|---|
| `cg_categories(order='market_cap_desc')` | 市值和成交量排名靠前的板块。 |
| `cg_categories_list()` | 仅板块 ID/名称。 |
| `cg_derivatives(include_tickers='unexpired')` | 交易所的衍生品 ticker。 |
| `cg_derivatives_exchanges(order='open_interest_btc_desc', per_page=50)` | 衍生品交易所排名。 |
| `cg_nfts_list(order='market_cap_usd_desc', per_page=100, page=1)` | 顶级 NFT 集合。 |
| `cg_nft(nft_id)` | NFT 集合详情。 |
| `cg_nft_by_contract(asset_platform, contract_address)` | 通过合约地址的 NFT。 |

### 交易所
| 函数 | 描述 |
|---|---|
| `cg_exchanges(per_page=100, page=1)` | 交易所排名。 |
| `cg_exchange(exchange_id)` | 单个交易所的详情。 |
| `cg_exchange_tickers(exchange_id, ...)` | 交易所上的 ticker。 |
| `cg_exchange_volume_chart(exchange_id, days=30)` | 交易所成交量历史。 |

### 合约 / 代币（按平台）
| 函数 | 描述 |
|---|---|
| `cg_token_price(platform, contract_addresses, vs_currencies='usd', include_market_cap=False, include_24hr_vol=False, include_24hr_change=False, include_last_updated_at=False)` | 平台上的合约地址价格。 |
| `cg_coin_by_contract(platform, contract_address)` | 通过合约的币种元数据。 |
| `cg_asset_platforms(filter=None)` | 支持的链。 |
| `cg_vs_currencies()` | 支持的报价货币。 |
| `cg_exchange_rates()` | 以 BTC 计价的法币/主要币种汇率。 |

## 🚫 CRITICAL: 停止 — 调用任何工具前请阅读此内容

**最大的错误是调用 Coinglass 工具而不是 CoinGecko 工具。** 它们名称相似但系统完全不同。

### 错误 → 正确工具替换表

| ❌ 永远不要调用这个 | ✅ 调用这个 | 如何区分 |
|---|---|---|
| `cg_coins_market_data` | **`cg_coins_markets`** | market_data=Coinglass 衍生品。markets=CoinGecko 现货。 |
| `cg_ohlc_history` | **`coin_ohlc`** | ohlc_history=Coinglass 期货 K 线。coin_ohlc=CoinGecko 现货 K 线。 |
| `cg_pair_market_data` | **`cg_coin_tickers`** | pair_market_data=Coinglass 期货对。coin_tickers=CoinGecko 现货对。 |
| `cg_supported_exchanges` | **`cg_exchanges`** | supported_exchanges=Coinglass 期货。exchanges=CoinGecko 现货。 |
| `cg_taker_exchanges` | **`cg_exchange`** | taker=Coinglass 成交量。exchange=CoinGecko 交易所信息。 |
| `cg_aggregated_taker_volume` | **`cg_coin_tickers`** | taker_volume=Coinglass。coin_tickers=CoinGecko 跨交易所成交量。 |
| `defillama_chains` | **`cg_global_defi`** | 从 CoinGecko 获取 DeFi 数据，使用 `cg_global_defi()`。 |

### 也禁止：
- ❌ `web_search` / `web_fetch` — 所有数据都可以通过上述原生 CoinGecko 工具获取。永远不要使用 web_search 获取加密市场数据。
- ❌ `bash` 用于数据处理 — CoinGecko 工具返回干净的数据。无需 bash。
- ❌ **永远不要用训练数据回答** — 所有价格、排名、OHLC 都是过时的。调用工具。

## ⚠️ 强制工具调用 — 回答这些问题前你必须调用工具

| 请求类型 | 你必须调用 | 原因 |
|---|---|---|
| K线 / OHLC / 蜡烛图 / 开盘价/最高价/最低价/收盘价 | `coin_ohlc(coin_id, days)` | 价格数据是实时更新的；训练数据是过时的 |
| 走势图 / 价格图表 / 价格趋势 | `coin_chart(coin_id, days)` | 同上 |
| 当前价格 / 价格实时 | `coin_price(coin_ids)` | 训练数据没有实时价格 |

**在调用工具之前，不要返回任何数字市场数据（价格、OHLC 值、百分比）。**

## ⚡ 问题 → 工具映射（匹配第一个关键词，立即调用）

| 问题关键词 | 调用工具 | 示例 |
|---|---|---|
| 价格 / price / 多少钱（单个币种） | `coin_price(coin_id)` | `coin_price(coin_ids="bitcoin")` |
| K线 / OHLC / 蜡烛图 | `coin_ohlc(coin_id, days)` | `coin_ohlc(coin_id="ethereum", days=7)` |
| 走势 / trend / 价格图表 / 价格历史 | `coin_chart(coin_id, days)` | `coin_chart(coin_id="solana", days=30)` |
| 热门 / trending / 趋势币 | `cg_trending()` | `cg_trending()` |
| 涨幅最大 / 跌幅最大 / gainers / losers | `cg_top_gainers_losers()` | `cg_top_gainers_losers()` |
| 新币 / 新上线 / new coins / recently added | `cg_new_coins()` | `cg_new_coins()` |
| 总市值 / BTC市占率 / global / 晨报 / 市场概况 | `cg_global()` | `cg_global()` |
| DeFi总市值 / DeFi TVL / DeFi 占比 | `cg_global_defi()` | `cg_global_defi()` |
| 板块 / sector / category / L1 / L2 / Meme / AI 币 | `cg_categories()` | `cg_categories()` |
| 板块内个币 / Meme前10 / AI币排名 / DeFi币排名 | `cg_coins_markets(category=X)` | `cg_coins_markets(category="meme-token", per_page=10)` |
| 市值排名 / top 10 / ranking / 前10币 | `cg_coins_markets(per_page=N)` | `cg_coins_markets(per_page=10)` |
| ATH / 历史最高 / 社区 / dev / 研究 / 基本面 | `cg_coin_data(coin_id)` | `cg_coin_data(coin_id="solana", community_data=True)` |
| 对比两个币 / compare / XX vs YY | `cg_coin_data()` × 2 | 每个币种调用一次 |
| NFT排名 / NFT市场 / floor price / 顶级 NFTs | `cg_nfts_list()` | `cg_nfts_list()` |
| 某个 NFT (BAYC/Punks/Azuki) | `cg_nft(nft_id)` | `cg_nft(nft_id="bored-ape-yacht-club")` |
| 交易所详情 / Binance详情 / 交易所数据 | `cg_exchange(exchange_id)` | `cg_exchange(exchange_id="binance")` |
| 交易所列表 / 交易所排名 | `cg_exchanges()` | `cg_exchanges()` |
| 交易对 / trading pairs / 流动性分布 | `cg_coin_tickers(coin_id)` | `cg_coin_tickers(coin_id="bitcoin")` |
| 交易所成交量趋势 / volume chart | `cg_exchange_volume_chart(exchange_id)` | `cg_exchange_volume_chart(exchange_id="binance", days=30)` |
| 合约地址价格 / token price on-chain | `cg_token_price(platform, contract)` | `cg_token_price(platform="ethereum", contract_addresses="0xa0b...")` |
| 搜索币 / 找币 / coin lookup / search | `cg_search(query)` | `cg_search(query="pepe")` |
| 永续合约交易所 / derivatives exchange / OI排名 | `cg_derivatives_exchanges()` | `cg_derivatives_exchanges()` |
| 合约 ticker / perpetual / funding / basis | `cg_derivatives()` | `cg_derivatives()` |
| 交易所对比 + 永续交易所 | `cg_exchanges()` + `cg_derivatives_exchanges()` | 两个调用 |

## 🌳 决策树

```
有多少币种？
├─ 一个币种
│   ├─ 只需要价格？→ coin_price()
│   ├─ ATH/社区/dev/深度？→ cg_coin_data()
│   ├─ OHLC 蜡烛图？→ coin_ohlc()
│   ├─ 价格趋势？→ coin_chart()
│   └─ 不确定 ID？→ 先用 cg_search()
├─ 多个币种 / 排名
│   ├─ 板块汇总（板块总市值）？→ cg_categories()
│   ├─ 板块内个币（Meme前10）？→ cg_coins_markets(category=X)
│   └─ 一般排名？→ cg_coins_markets(per_page=N)
├─ NFTs → cg_nfts_list() 或 cg_nft(nft_id)
├─ 交易所 → cg_exchange(id) 或 cg_exchanges()
├─ 全球 → cg_global() 或 cg_global_defi()
└─ 代币按合约 → cg_token_price()
```

## 常见板块 ID

`meme-token`, `artificial-intelligence`, `layer-1`, `layer-2`, `decentralized-finance-defi`, `gaming`, `real-world-assets-rwa`

## 输出格式

- 价格：始终使用 `$` 符号 → `$66,697`
- 百分比：始终使用 `%` → `+4.2%`
- NFT 挂牌价（以 ETH 为单位）：同时显示 USD → `5.17 ETH ($10,534)`

## 重要提示

- CoinGecko 使用 slug ID："bitcoin", "ethereum", "solana"。符号（BTC, ETH, SOL）自动解析。
- 如果不确定币种 ID → `cg_search(query="coin name")` 先搜索。
- 大多数问题只需要 1-2 次工具调用。不要链式调用 3 次以上。

## 常见问题

### coin_price 因无效 ID 失败
**解决方案：** 先用 `cg_search(query="coin name")` 找到正确的 CoinGecko ID，或者直接使用符号（例如 'COMP'）。
