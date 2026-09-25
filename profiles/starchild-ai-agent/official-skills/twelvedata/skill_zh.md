# Twelve Data

股票、外汇和商品价格数据。**仅限传统市场——不适用于加密货币。**

## 脚本使用

此技能包含一个 `exports.py` 文件，其中包含所有函数。从 `bash` 块中调用它：

```bash
python3 - <<'EOF'
import sys, json
sys.path.insert(0, "/data/workspace/skills/twelvedata")
from exports import twelvedata_price, twelvedata_quote, twelvedata_time_series

# 单个报价
print(twelvedata_quote(symbol="AAPL"))

# 时间序列（最近30个每日蜡烛图）
series = twelvedata_time_series(symbol="AAPL", interval="1day", outputsize=30)
print(json.dumps(series.get("values", [])[:3], indent=2))
EOF
```

`exports.py` 中可用的函数：`twelvedata_price`、`twelvedata_quote`、`twelvedata_time_series`、`twelvedata_eod`、`twelvedata_quote_batch`、`twelvedata_price_batch`、`twelvedata_search`、`twelvedata_stocks`、`twelvedata_forex_pairs`、`twelvedata_exchanges`。当你需要确切的签名时，直接阅读 `exports.py`。

## 函数参考（签名）

所有函数都在 `exports.py` 中。符号使用 TwelveData 格式（例如 `AAPL`、`EUR/USD`、`XAU/USD`）。对于美国股票，使用 `prepost=True` 获取盘前/盘后数据。

| 函数 | 描述 |
|---|---|
| `twelvedata_price(symbol, prepost=False)` | 单个符号的当前价格。 |
| `twelvedata_price_batch(symbols, prepost=False)` | 多个符号的价格（`symbols` = 以逗号分隔的字符串）。 |
| `twelvedata_quote(symbol, prepost=False)` | 详细报价：价格、成交量、52周最高/最低价、变化百分比。 |
| `twelvedata_quote_batch(symbols, prepost=False)` | 多个符号的详细报价。 |
| `twelvedata_time_series(symbol, interval='1day', outputsize=30, start_date=None, end_date=None, prepost=False)` | OHLCV 蜡烛图。`interval` = `1min`/`5min`/`15min`/`30min`/`1h`/`2h`/`4h`/`1day`/`1week`/`1month`。 |
| `twelvedata_eod(symbol, date=None, prepost=False)` | 某一天（默认为最新）的收盘价。 |
| `twelvedata_search(query)` | 按名称或代码搜索符号。 |
| `twelvedata_stocks(exchange=None, country=None)` | 列出支持的股票（可过滤）。 |
| `twelvedata_forex_pairs()` | 列出所有支持的外汇对。 |
| `twelvedata_exchanges()` | 列出支持的交易所。 |

## 关键词 → 工具查询

| 用户询问 | 工具 | 不要这个 |
|----------------|------|----------|
| "AAPL 股价", "当前价格"（单个） | `twelvedata_quote` | 不是 `twelvedata_price`（细节较少） |
| "仅价格数字" | `twelvedata_price` | — |
| "多只股票对比"（2+ 符号） | `twelvedata_quote_batch` | 不是多个 `twelvedata_quote` 调用 |
| "K线", "历史数据", "时间序列" | `twelvedata_time_series` | — |
| "收盘价" | `twelvedata_eod` | — |
| "找股票代码" | `twelvedata_search` | — |
| "NASDAQ 有哪些股票" | `twelvedata_stocks` | — |
| "汇率", "EUR/USD" | `twelvedata_quote(symbol="EUR/USD")` | — |
| "外汇对列表" | `twelvedata_forex_pairs` | — |
| "金价", "油价" | `twelvedata_quote(symbol="XAU/USD")` | 不是 CoinGecko |
| "BTC 价格", 任何加密货币 | **CoinGecko** `coin_price` | ❌ 从不使用 TwelveData 处理加密货币 |

## TwelveData 与 CoinGecko — 边界

| 资产类别 | 使用 | 原因 |
|-------------|-----|-----|
| 股票 (AAPL, TSLA) | **TwelveData** | CoinGecko 没有股票 |
| 外汇 (EUR/USD) | **TwelveData** | CoinGecko 没有外汇 |
| 商品 (黄金、石油) | **TwelveData** | CoinGecko 没有商品 |
| 加密货币 (BTC, ETH, SOL) | **CoinGecko** | TwelveData 加密货币数据有限/不可靠 |

## 错误操作 — 调用前阅读

### ❌ 错误 1：使用 TwelveData 处理加密货币
```
用户: "BTC 价格"
❌ 错误: twelvedata_quote(symbol="BTC/USD")
✅ 正确: coin_price(ids="bitcoin")  ← CoinGecko
```

### ❌ 错误 2：为多只股票单独调用报价
```
用户: "AAPL MSFT GOOGL 现在什么价"
❌ 错误: twelvedata_quote("AAPL"), twelvedata_quote("MSFT"), twelvedata_quote("GOOGL")  ← 3 调用
✅ 正确: twelvedata_quote_batch(symbols=["AAPL", "MSFT", "GOOGL"])  ← 1 调用，最多 120 个符号
```

### ❌ 错误 3：外汇没有斜杠
```
❌ 错误: twelvedata_quote(symbol="EURUSD")
✅ 正确: twelvedata_quote(symbol="EUR/USD")  ← 始终使用斜杠格式
```
另外：`USD/CNH` 不是 `USDCNH`，`GBP/JPY` 不是 `GBPJPY`。

### ❌ 错误 4：期望从报价中获取买价/卖价
```
❌ 错误: "EUR/USD 买价: 1.0850, 卖价: 1.0852"  ← 报价仅返回收盘价
✅ 正确: "EUR/USD 当前价格: 1.0851 (收盘价/最后价格 — 买价/卖价差价不可用)"
```

### ❌ 错误 5：时间间隔格式错误
```
❌ 错误: twelvedata_time_series(interval="1D")  ← 大写
✅ 正确: twelvedata_time_series(interval="1day")
```
有效：`1min`、`5min`、`15min`、`30min`、`1h`、`2h`、`4h`、`8h`、`1day`、`1week`、`1month`

### ❌ 错误 6：使用完整输出时，紧凑输出已足够
```
用户: "AAPL 最近走势"
❌ 错误: twelvedata_time_series(symbol="AAPL", interval="1day", outputsize="full")  ← 5000 蜡烛图
✅ 正确: twelvedata_time_series(symbol="AAPL", interval="1day", outputsize="compact")  ← 30 蜡烛图
```
仅在用户明确需要深度历史记录时使用 `full`。

## 符号参考

### 商品（已验证）

| 资产 | 符号 |
|-------|--------|
| 黄金 | `XAU/USD` |
| 白银 | `XAG/USD` |
| 铂金 | `XPT/USD` |
| 钯金 | `XPD/USD` |
| 原油（WTI） | `WTI/USD` |
| 天然气 | `NG/USD` |

### 热门外汇对

| 对 | 符号 |
|------|--------|
| 欧元 / 美元 | `EUR/USD` |
| 英镑 / 美元 | `GBP/USD` |
| 美元 / 日元 | `USD/JPY` |
| 美元 / 人民币 | `USD/CNH` |

使用 `twelvedata_search` 发现其他对。

## 盘前/盘后数据

```
twelvedata_quote(symbol="AAPL", prepost=true)
twelvedata_time_series(symbol="AAPL", interval="1min", prepost=true)
```
当可用时，返回 `premarket_change`、`premarket_change_percent`、`postmarket_change`、`postmarket_change_percent`。

## 输出大小

- `compact` — 最后 30 个数据点（默认，更快）。用于 "最近走势"。
- `full` — 最多 5000 个数据点。用于深度分析/制图。

## 代理安全使用

1. **代理工具调用**：始终优先使用 `twelvedata_*` 工具（此技能）。
2. **平台代码**（`skills/`、`tools/`）：使用 `core.http_client`。
3. **工作区脚本**（`bash`）：不要直接调用 TwelveData。使用技能工具。

## 复合查询

### 股票对比
```
1. twelvedata_quote_batch(symbols=["AAPL", "MSFT", "GOOGL", "TSLA"])
2. twelvedata_time_series(symbol="AAPL", interval="1day", outputsize="compact")  ← 仅针对用户最关心的那一个
```

### 宏仪表盘（股票 + 外汇 + 商品）
```
1. twelvedata_quote_batch(symbols=["SPY", "QQQ"])          → 美国指数
2. twelvedata_quote_batch(symbols=["EUR/USD", "USD/JPY"])   → 外汇
3. twelvedata_quote(symbol="XAU/USD")                       → 黄金
```
