# 图表绘制

## ⚠️ 重要提示：不要调用数据工具

**绝对不要**在创建图表时调用`price_chart`、`get_coin_ohlc_range_by_id`、`twelvedata_time_series`或任何市场数据工具。图表脚本会内部获取数据。调用这些工具会向你的上下文中注入78KB+的不必要数据。

**工作流程（4个步骤）：**
1. 从`skills/charting/scripts/`读取模板
2. 将脚本写入`scripts/`
3. 使用`bash`运行脚本
4. 对输出PNG文件调用`read_file`，然后使用Markdown图片语法显示：`![图表描述](output/filename.png)`

---

你可以生成TradingView质量的K线图。暗色主题，简洁布局，专业配色。每个图表都是一个独立的Python脚本——没有内部导入。

**附加规则：**
- 图表脚本在工作区中运行，不能从`core`导入。直接使用`requests`库，**不要**使用`proxied_get()`。
- 模板包含代理自动配置。如果存在`PROXY_HOST`环境变量，脚本会自动配置`HTTP_PROXY`/`HTTPS_PROXY`。

工具：`write_file`、`bash`、`read_file`

## 何时使用何种图表

**简单价格行为** → 无指标的K线图。适用于"给我看这个月BTC的情况"。
**趋势分析** → 添加EMA/SMA叠加层。适用于"ETH是否处于上升趋势？"。
**动量检查** → 添加RSI或MACD作为子图。适用于"SOL是否超买？"。
**完整技术视图** → K线图+布林带+RSI+MACD。适用于"给我看BTC的完整情况"。
**成交量分析** → 需要从市场图表端点单独获取（OHLC端点没有成交量）。
**资产比较** → 比较两个资产的折线图（BTC vs 黄金，ETH vs 标普500等）。使用比较模板进行归一化或百分比比较。

## 如何构建图表

阅读并自定义`skills/charting/scripts/`中的模板脚本：
- `chart_template.py` — 基准K线图，TradingView样式（加密货币通过CoinGecko）
- `chart_with_indicators.py` — RSI、MACD、布林带、EMA/SMA示例（加密货币通过CoinGecko）
- `chart_stock_template.py` — 使用Twelve Data API的股票/外汇图表
- `chart_comparison_template.py` — 比较两个资产（加密货币vs大宗商品，股票vs加密货币等）

将相关模板复制到`scripts/`，自定义配置部分（币种、天数、指标），然后运行它。

模板会内部处理所有数据获取，并具有重试逻辑和错误处理。

**注意：** 这些模板用于市场数据可视化（价格图表、指标）。对于回测结果图表（权益曲线、回撤、性能仪表板），直接在回测脚本中添加matplotlib图表——数据已经存在，无需重新获取或创建单独的文件。

## TradingView配色方案

| 元素 | 颜色 | 十六进制 |
|------|------|----------|
| 上涨蜡烛 | 青色 | `#26a69a` |
| 下跌蜡烛 | 红色 | `#ef5350` |
| 背景 | 暗色 | `#131722` |
| 网格 | 微妙的点状 | `#1e222d` |
| 文本/坐标轴 | 浅灰色 | `#d1d4dc` |
| MA线 | 蓝色/橙色 | `#2196f3` / `#ff9800` |
| RSI线 | 紫色 | `#b39ddb` |
| MACD线 | 蓝色 | `#2196f3` |
| 信号线 | 橙色 | `#ff9800` |

除非用户要求，否则不要偏离此配色方案。

## 数据源API

### CoinGecko（仅限加密货币）

**端点：** `https://pro-api.coingecko.com/api/v3/coins/{coin_id}/ohlc/range`
**认证：** 头部 `x-cg-pro-api-key: {COINGECKO_API_KEY}`
**用途：** BTC、ETH、SOL，以及所有加密货币

示例：
```python
url = f"https://pro-api.coingecko.com/api/v3/coins/{COIN_ID}/ohlc/range"
params = {"vs_currency": "usd", "from": from_ts, "to": now, "interval": "daily"}
headers = {"x-cg-pro-api-key": os.getenv("COINGECKO_API_KEY")}
resp = requests.get(url, params=params, headers=headers)
raw = resp.json()  # [[timestamp_ms, open, high, low, close], ...]
```

### Twelve Data（股票、外汇、大宗商品）

**端点：** `https://api.twelvedata.com/time_series`
**认证：** 查询参数 `apikey={TWELVEDATA_API_KEY}`
**用途：** 股票（AAPL、MSFT）、外汇（EUR/USD）、大宗商品（XAU/USD用于黄金）

**常用符号：**
- 股票：`AAPL`、`MSFT`、`GOOGL`、`TSLA`、`SPY`
- 外汇：`EUR/USD`、`GBP/JPY`、`USD/CHF`
- 大宗商品：`XAU/USD`（黄金）、`XAG/USD`（白银）、`CL/USD`（原油）

**间隔：** `1min`、`5min`、`15min`、`30min`、`1h`、`4h`、`1day`、`1week`、`1month`

示例：
```python
url = "https://api.twelvedata.com/time_series"
params = {
    "symbol": "XAU/USD",  # 黄金现货价格
    "interval": "1day",
    "outputsize": 90,  # 蜡烛数量
    "apikey": os.getenv("TWELVEDATA_API_KEY")
}
resp = requests.get(url, params=params)
data = resp.json()
# data["values"] = [{"datetime": "2024-01-01", "open": "2050.00", "high": "2060.00", ...}, ...]
```

**重要提示：** Twelve Data返回的数据是**逆时间顺序**（最新优先）。在创建DataFrame之前，始终反转列表：
```python
values = data["values"][::-1]  # 反转为最早优先
```

## 间隔选择策略

模板现在会自动选择最优间隔，以最小化数据量同时保持视觉质量：

| 时间范围 | 自动选择的间隔 | 理由 |
|---------|---------------|------|
| ≤31天 | 每小时 | 短期分析的高粒度 |
| 32-365天 | 每日 | 足够的细节，较低的数据量 |
| >365天 | 每日 | 每日是长期趋势的最佳选择 |

**覆盖：** 在配置中设置`INTERVAL = "daily"`或`INTERVAL = "hourly"`以覆盖自动选择。

## 关键注意事项

- **`savefig`背景色**：你必须设置`facecolor='#131722'`和`edgecolor='#131722'`在`savefig`中，否则保存的PNG会恢复为白色背景。
- **标题间距**：在标题前缀`\n`以添加与顶部边缘的间距。
- **`returnfig=True`**：当你需要后绘图自定义（价格格式化、注释）时使用。使用它时，手动调用`fig.savefig()`——不要将`savefig`传递给`mpf.plot()`。
- **OHLC中没有成交量**：CoinGecko OHLC端点返回`[timestamp_ms, open, high, low, close]`。使用`volume=False`或从`coin_chart`端点单独获取成交量。
- **面板比例**：添加指标子图时设置`panel_ratios`。例如，`(4, 1, 2)`用于蜡烛+成交量+一个指标，`(5, 1, 2, 2)`用于两个指标。
- **图形大小**：默认`(14, 8)`。添加子图时增加到`(14, 10)`或`(14, 12)`。

## 规则

- **路径相对于工作区**。写入`scripts/foo.py`，而不是`workspace/scripts/foo.py`。bash的当前工作目录已经是工作区。
- **始终保存到`output/`目录**。使用`os.makedirs("output", exist_ok=True)`。
- **始终使用`bash("python3 scripts/<name>.py")`运行脚本**以验证它是否正常工作。
- **始终对生成的PNG调用`read_file`，然后使用Markdown图片语法显示：** `![图表](output/filename.png)`
- **脚本必须是独立的**。使用`requests` + `os.getenv()`。没有内部导入，没有dotenv。
- **重要提示：图表脚本中不要使用`proxied_get()`**。图表脚本是独立的，在工作区中运行——它们不能从`core.http_client`导入。始终直接使用`requests.get()`和`requests.post()`。这是PLATFORM.md代理规则的一个例外，因为这些脚本在主Star Child进程之外执行。模板展示了正确的模式。
- **环境变量会被继承**。`os.getenv("COINGECKO_API_KEY")`可以直接使用。
- **默认为暗色主题**，除非用户要求亮色。
- **文件名应描述图表**。例如`btc_30d_candles.png`，`eth_7d_rsi_macd.png`。
- **数据源**：使用CoinGecko API进行加密货币（BTC、ETH等）。使用Twelve Data API进行股票、外汇和大宗商品（AAPL、EUR/USD、XAU/USD用于黄金）。永远不要混合API——保持脚本专注于一个数据源。
- **考虑你在测量什么**：在创建图表之前，问问自己："用户试图回答什么问题？" 归一化图表（所有值从100开始）显示相对趋势，但隐藏实际收益幅度。如果用户想知道"哪个收益更多"或比较投资表现，他们需要实际乘数（例如，50x vs 10x），而不仅仅是看起来相似的线。

## 故障排除

### 401未授权错误

模板自动从`PROXY_HOST`/`PROXY_PORT`环境变量配置代理。如果出现401错误：

**检查环境：**
```bash
bash("env | grep -E 'PROXY|REQUESTS_CA'")
```

**预期变量：**
- `PROXY_HOST` / `PROXY_PORT` - 代理地址（模板使用这些设置HTTP_PROXY/HTTPS_PROXY）
- `REQUESTS_CA_BUNDLE` - 代理CA证书用于SSL
- `COINGECKO_API_KEY` / `TWELVEDATA_API_KEY` - 在代理环境中可以是假的

如果变量缺失，这是环境配置问题，不是脚本问题。
