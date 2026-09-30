---
name: earnings-recap
description: 分析公司最新的（或指定的过去）盈利报告，使用Yahoo Finance数据（yfinance）：实际与预估的每股收益（EPS）对比、盈利惊喜幅度、营收和利润率趋势，以及股票价格反应。当用户询问盈利情况时——无论是超出预期还是未达预期、盈利惊喜、季度结果、盈利发布后的股价变动，还是盈利电话会议回顾——包括对过去报告的随意提及，如“AMZN昨晚发布了报告”或“他们表现如何”，都可以使用这项技能。对于即将发布的报告，使用盈利预览（earnings-preview）。
---

# 盈利回顾技能

使用 [yfinance](https://github.com/ranaroussi/yfinance) 通过雅虎财经数据生成盈利分析报告。涵盖实际值与预估值的对比、惊喜幅度、股价反应以及财务背景——提供全面的报告情况。

**重要提示**：数据仅用于研究和教育目的。非投资建议。yfinance 与雅虎公司无关。

---

## 第 1 步：确保 yfinance 可用

**当前环境状态：**

```
!`python3 -c "exec('try:\n import yfinance\n print(\'yfinance \' + yfinance.__version__ + \' 已安装\')\nexcept Exception:\n print(\'YFINANCE_NOT_INSTALLED\')')"`
```

如果显示 `YFINANCE_NOT_INSTALLED`，请安装它：

```python
import subprocess, sys
subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "yfinance"])
```

如果已安装，请跳至下一步。

---

## 第 2 步：识别股票代码并收集数据

从用户请求中提取股票代码。在一个脚本中获取所有相关的盈利后数据。

```python
import yfinance as yf
import pandas as pd

ticker = yf.Ticker("AAPL")  # 替换为实际股票代码

# --- 盈利结果 ---
盈利日期 = ticker.get_earnings_dates(limit=12)  # 报告时间戳，最新优先
盈利历史 = ticker.earnings_history               # 过去 4 个季度，按财年季度末索引，最旧优先

# --- 财务报表（约 5 个季度，最新优先） ---
季度收入 = ticker.quarterly_income_stmt
季度现金流 = ticker.quarterly_cashflow
季度资产负债表 = ticker.quarterly_balance_sheet

# --- 背景 ---
信息 = ticker.info
新闻 = ticker.news
建议 = ticker.recommendations
```

### 需要提取的内容

| 数据源 | 关键字段 | 目的 |
|---|---|---|
| `get_earnings_dates()` | 盈利日期、EPS 预估、报告 EPS、惊喜(%) | 哪个报告、何时发布以及是否超预期 |
| `earnings_history` | epsEstimate, epsActual, epsDifference, surprisePercent | 过去四个季度的结果按财年季度末索引 |
| `quarterly_income_stmt` | TotalRevenue, GrossProfit, OperatingIncome, NetIncome, BasicEPS | 实际财务数据 |
| `history()` | 每个报告周围的每日收盘价 | 股价反应 |
| `info` | currentPrice, marketCap, forwardPE | 当前背景 |
| `news` | 近期头条 | 与盈利相关的新闻 |

---

## 第 3 步：找到报告并衡量反应

`earnings_history` 按财年季度末索引，而非公告日期，因此从 `get_earnings_dates()` 获取报告时间：最新报告是具有 `Reported EPS` 的最新行。其时间戳（美国东部时间）设定反应窗口：16:00 或之后表示公司收盘后发布；更早表示开盘前或偶尔在交易期间。如果用户询问特定季度，则使用该行。

```python
def 盈利反应(ticker, report_ts):
    """报告前最后一个收盘价到报告后第一个收盘价的百分比变动。"""
    daily = ticker.history(start=(report_ts - pd.Timedelta(days=10)).date(),
                           end=(report_ts + pd.Timedelta(days=10)).date())
    收盘价 = daily["Close"]
    日期 = 收盘价.index.date
    报告日期 = report_ts.date()
    if report_ts.hour >= 16:  # 收盘后发布：报告日收盘价 -> 下一个收盘价
        pre, post = 收盘价[日期 <= 报告日期], 收盘价[日期 > 报告日期]
    else:                     # 开盘前或盘中：前一个收盘价 -> 报告日收盘价
        pre, post = 收盘价[日期 < 报告日期], 收盘价[日期 >= 报告日期]
    if pre.empty or post.empty:
        return None           # 反应时段尚未结束
    return (post.iloc[0] / pre.iloc[-1] - 1) * 100

报告 = 盈利日期[盈利日期["Reported EPS"].notna()]
最新时间戳 = 报告.index[0]
反应百分比 = 盈利反应(ticker, 最新时间戳)

# 过去四个报告的典型盈利日变动
先前变动 = [盈利反应(ticker, ts) for ts in 报告.index[1:5]]
平均绝对变动 = pd.Series([abs(m) for m in 先前变动 if m is not None]).mean()
```

如果 `反应百分比` 为 `None`，则报告在最新收盘价之后发布；可以说常规时段的反应仍在等待（使用 `history(..., prepost=True)` 调用可显示盘后变动，如果用户需要）。

---

## 第 4 步：构建盈利回顾

涵盖以下方面，以结果开头：

1. **标题结果** — EPS 实际值与预估值的对比、惊喜%、收入同比增长，以及股价反应。
2. **预估与实际** — 该季度的 EPS 预估、实际值和惊喜（金额和百分比）。
3. **季度趋势** — 收入、毛利率、营业利润率、EPS 最近几个季度的数据，利润率从报表计算（毛利润/收入，营业利润/收入）。yfinance 通常返回约 5 个季度，因此仅最新季度（第 0 列 vs 第 4 列）有同比增长；其他显示顺序变动而非虚构比较。
4. **价格反应** — 反应时段的变动、与过去四个报告的股票平均绝对盈利变动的比较，以及股票是否维持、回吐或延续该变动。
5. **变化内容** — 与上季度的利润率方向、收入增长轨迹的任何变化、此惊喜与公司通常模式的比较，以及如果可用，当前分析师情绪。

---

## 第 5 步：回复用户

以标题开头——哪个季度、何时发布、超预期或未达预期、收入增长、反应——然后是支持性表格。说明重点：这是否是显著的超预期或低标准达成，以及趋势是否改善或恶化。保持客观，不提供投资建议。

包括适用的免责声明：雅虎财经数据无法捕捉电话会议的所有内容（指引、部门细节）、收入比较基于报表的同比增长而非收入共识、价格反应可能反映当天的市场整体变动，以及这不是投资建议。

---

## 参考文件

- `references/api_reference.md` — 详细的 yfinance API 参考，用于盈利历史和财务报表方法

当需要精确的方法签名或处理财务数据的边缘情况时，请阅读参考文件。
