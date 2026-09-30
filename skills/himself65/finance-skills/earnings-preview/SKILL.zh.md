---
name: earnings-preview
description: 构建一份来自Yahoo Finance数据（yfinance）的股票盈利前简报：即将发布的报告日期和时间、市场一致预期的每股收益和收入预估及其范围、超越/未达预期的历史记录、分析师评级和目标价，以及印刷版中需要关注的要点。当用户准备即将到来的盈利报告或询问市场预期——市场一致预期或小道消息、每股收益预期、公司是否会超越预期、盈利格局或盈利季前瞻——时，以及每当在即将到来的盈利背景下出现股票代码，即使没有“前瞻”一词，也使用此技能。对于已经公布的结果，使用盈利回顾。
---

# 盈利预测技能

使用 Yahoo Finance 数据生成盈利预告简报，通过 [yfinance](https://github.com/ranaroussi/yfinance)。整合即将到来的盈利日期、市场预期估计、历史准确率、分析师情绪和关键财务背景——在盈利电话会议前所需的一切。

**重要提示**：数据仅供研究和教育目的使用。非投资建议。yfinance 与雅虎公司无关。

---

## 第 1 步：确保 yfinance 可用

**当前环境状态：**

```
!`python3 -c "exec('try:\n import yfinance\n print(\'yfinance \' + yfinance.__version__ + \' installed\')\nexcept Exception:\n print(\'YFINANCE_NOT_INSTALLED\')')"`
```

如果 `YFINANCE_NOT_INSTALLED`，请安装它：

```python
import subprocess, sys
subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "yfinance"])
```

如果已安装，请跳到下一步。

---

## 第 2 步：识别股票代码并收集所有数据

从用户请求中提取股票代码。如果他们提到公司名称但没有代码，请进行查询。然后在单个脚本中获取所有相关数据，以减少 API 调用。

```python
import yfinance as yf

ticker = yf.Ticker("AAPL")  # 替换为实际股票代码

# --- 核心数据 ---
info = ticker.info
calendar = ticker.calendar
earnings_dates = ticker.get_earnings_dates(limit=8)  # 报告时间戳；即将到来的一个还没有报告的 EPS
hist = ticker.history(period="1mo")                  # 近期价格表现

# --- 估计 ---
earnings_est = ticker.earnings_estimate
revenue_est = ticker.revenue_estimate

# --- 历史记录 ---
earnings_hist = ticker.earnings_history

# --- 分析师情绪 ---
price_targets = ticker.analyst_price_targets
recommendations = ticker.recommendations

# --- 近期财务数据作为背景 ---
quarterly_income = ticker.quarterly_income_stmt
quarterly_cashflow = ticker.quarterly_cashflow
```

### 从每个数据源提取的内容

| 数据源         | 关键字段         | 目的         |
|---------------|----------------|-------------|
| `calendar`    | 盈利日期、除息日期 | 盈利时间和关键日期 |
| `get_earnings_dates()` | 盈利日期（时区感知时间戳）、EPS 估计、报告的 EPS | 报告时间：即将到来的行没有报告的 EPS；在 16:00 ET 或之后的时间表示收盘后，更早的时间表示开盘前 |
| `earnings_estimate` | avg, low, high, numberOfAnalysts, yearAgoEps, growth (for 0q, +1q, 0y, +1y) | 市场对 EPS 的预期 |
| `revenue_estimate` | avg, low, high, numberOfAnalysts, yearAgoRevenue, growth | 收入预期 |
| `earnings_history` | epsEstimate, epsActual, epsDifference, surprisePercent | 赢/输记录（按财年结束索引，最旧的优先） |
| `analyst_price_targets` | current, low, high, mean, median | 街头价格目标 |
| `recommendations` | Buy/Hold/Sell 计数 | 情绪分布 |
| `quarterly_income_stmt` | TotalRevenue, NetIncome, BasicEPS | 近期趋势 |

---

## 第 3 步：构建盈利预告

简报应让用户能一目了然地了解情况。涵盖以下五个方面；如果某个方面的数据缺失，请用一行说明，而不是删除它。

1. **日期和背景** — 公司、股票代码、行业和行业；报告日期以及是否在开盘前或收盘后；当前价格以及 1 周和 1 个月的表现；市值。
2. **市场预期估计** — 表格展示本季度的 EPS 和收入预期，包括低、高、分析师数量、去年同期的值和预期增长。如果高/低差值超过预期值的约 20%，则表示不确定性异常；看到这种情况时请说明。
3. **赢/输记录** — 最近四个季度估计与实际 EPS 以及惊喜百分比，总结为赢/输次数和平均惊喜。
4. **分析师情绪** — 评级分布（从强力买入到强力卖出）和价格目标范围（低、均值、中位数、高），以及从均值目标隐含的上行或下行空间。
5. **需要关注的点** — 市场在这个简报中会关注的几个点，针对该公司和行业选择：收入增长加速或减速、利润率扩大或压缩、季度间大幅波动的项目，以及数据提供的细分趋势。这是简报中的判断部分。

---

## 第 4 步：回复用户

以标题开头——报告日期和简报的要点概述——然后是上述五个方面，使用表格有助于说明。最后以对整体情况的简短概述结束，基于估计、记录和情绪，以街头预期而不是建议的形式呈现。

包括适用的免责声明：估计在报告日期前可能变化，过去的赢/输不保证未来，Yahoo Finance 的市场预期可能比实时提供商晚几个小时，这不是投资建议。

---

## 参考文件

- `references/api_reference.md` — yfinance 盈利和估计方法的详细 API 参考

需要精确的方法签名或边缘情况处理时，请阅读参考文件。
