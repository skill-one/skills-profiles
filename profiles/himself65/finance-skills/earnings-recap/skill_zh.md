# 盈利回顾技能

使用 [yfinance](https://github.com/ranaroussi/yfinance) 通过雅虎财经数据生成盈利分析报告。涵盖实际值与预期值的对比、惊喜幅度、股价反应以及财务背景——全面了解发生了什么。

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

如果已安装，请跳到下一步。

---

## 第 2 步：确定股票代码并收集数据

从用户请求中提取股票代码。在一个脚本中获取所有相关的盈利后数据。

```python
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

ticker = yf.Ticker("AAPL")  # 替换为实际股票代码

# --- 盈利结果 ---
earnings_hist = ticker.earnings_history

# --- 财务报表 ---
季度利润表 = ticker.quarterly_income_stmt
季度现金流 = ticker.quarterly_cashflow
季度资产负债表 = ticker.quarterly_balance_sheet

# --- 股价反应 ---
# 获取约 30 天的历史数据以捕捉反应窗口
hist = ticker.history(period="1mo")

# --- 背景 ---
info = ticker.info
新闻 = ticker.news
建议 = ticker.recommendations
```

### 要提取的内容

| 数据源 | 关键字段 | 目的 |
|---|---|---|
| `earnings_history` | epsEstimate, epsActual, epsDifference, surprisePercent | 超额/不及预期结果 |
| `quarterly_income_stmt` | TotalRevenue, GrossProfit, OperatingIncome, NetIncome, BasicEPS | 实际财务数据 |
| `history()` | 盈利日期周围的收盘价 | 股价反应 |
| `info` | currentPrice, marketCap, forwardPE | 当前背景 |
| `news` | 最近新闻标题 | 与盈利相关的新闻 |

---

## 第 3 步：确定最新的盈利结果

最新的盈利结果是 `earnings_history` 中第一行（最新日期）。使用其日期：

1. **确定盈利日期** 以进行股价反应分析
2. **匹配到财务报表中的相应季度**
3. **计算股价反应** — 比较盈利前最后一个交易日的收盘价与下一个交易日的收盘价（或开盘价，取决于盈利是在市场开盘前还是收盘后发布）

### 股价反应计算

```python
import numpy as np

# 从 earnings_history 索引找到盈利日期
earnings_date = earnings_hist.index[0]  # 最新的

# 获取盈利日期周围的每日价格
hist_extended = ticker.history(start=earnings_date - timedelta(days=5),
                                end=earnings_date + timedelta(days=5))

# 反应通常按以下方式衡量：
# - 盈利前最后一个交易日的收盘价 -> 盈利后第一个交易日的收盘价
# 注意市场开盘前/收盘后发布的盈利
if len(hist_extended) >= 2:
    pre_price = hist_extended['Close'].iloc[0]
    post_price = hist_extended['Close'].iloc[-1]
    reaction_pct = ((post_price - pre_price) / pre_price) * 100
```

**注意**：确切的反应窗口取决于公司发布的时间（市场开盘前还是收盘后）。价格数据将反映这一点——在盈利日期附近寻找连续收盘价之间的最大差距。

---

## 第 4 步：构建盈利回顾

### 第 1 部分：标题结果

首先突出关键数字：
- **EPS**：实际值与预期值对比，超额/不及预期多少，惊喜百分比
- **收入**：实际值与去年同期对比（来自 `quarterly_income_stmt` 的 TotalRevenue）
- **股价反应**：盈利日的百分比变动

示例："AAPL 超额完成 Q3 EPS 预期 3.7% ($1.40 实际 vs $1.35 预期)。收入同比增长 5.4% 至 $94.3B。报告当日股价上涨 +2.1%。

### 第 2 部分：盈利与预期对比详情

| 指标 | 预期值 | 实际值 | 惊喜 |
|---|---|---|---|
| EPS | $1.35 | $1.40 | +$0.05 (+3.7%) |

如果用户询问特定季度（非最新季度），请在 `earnings_history` 中查找更早的数据。

### 第 3 部分：季度财务趋势

显示 `quarterly_income_stmt` 中最后 4 个季度的关键指标：

| 季度 | 收入 | 同比增长 | 毛利率 | 营业利润率 | EPS |
|---|---|---|---|---|---|
| Q3 2024 | $94.3B | +5.4% | 46.2% | 30.1% | $1.40 |
| Q2 2024 | $85.8B | +4.9% | 46.0% | 29.8% | $1.33 |
| Q1 2024 | $119.6B | +2.1% | 45.9% | 33.5% | $2.18 |
| Q4 2023 | $89.5B | -0.3% | 45.2% | 29.2% | $1.26 |

从原始财务数据计算利润率：
- 毛利率 = GrossProfit / TotalRevenue
- 营业利润率 = OperatingIncome / TotalRevenue

### 第 4 部分：股价反应

- 盈利日/下一个交易日的百分比变动
- 与该股票平均盈利日变动的比较（计算 `earnings_history` 中最后 4 个盈利日的平均绝对变动）
- 股票当前相对于盈利日变动的位置（是否持平、回吐收益、进一步上涨？）

### 第 5 部分：背景与变化

根据数据，注意：
- 与上一季度相比，利润率是扩张还是收缩
- 收入增长轨迹是否有任何显著变化
- 超额/不及预期与该股票历史模式的比较（来自完整的 `earnings_history`）
- 如果可用，从 `recommendations` 中提供当前分析师情绪

---

## 第 5 步：回复用户

以清晰、结构化的摘要形式呈现回顾：

1. **首先突出标题**："AAPL 在 [日期] 发布了 Q3 2024 盈利：EPS 超额 3.7%，收入同比增长 5.4%。"
2. **显示表格** 以提供细节
3. **突出重点**：这是否是一次有意义的超额完成，还是低标准的情况？趋势是改善还是恶化？
4. **保持客观** — 呈现数据，避免做出投资建议

### 需要包含的注意事项
- 雅虎财经数据可能不包含盈利电话会议的所有细节（指引、部门细分等）
- 收入预期难以精确比较——yfinance 提供财务报表中的同比增长比较
- 股价反应可能受同一天更广泛市场变动的影响
- 这不是投资建议

---

## 参考文件

- `references/api_reference.md` — 详细的 yfinance API 参考，用于盈利历史和财务报表方法

在需要精确方法签名或处理财务数据边缘情况时，请阅读参考文件。
