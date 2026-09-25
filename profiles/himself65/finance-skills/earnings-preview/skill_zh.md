# 收益预告技能

使用 Yahoo Finance 数据生成收益预告简报，通过 [yfinance](https://github.com/ranaroussi/yfinance)。整合即将到来的收益日期、共识预期、历史准确率、分析师情绪和关键财务背景——在收益电话会议之前，您所需的一切。

**重要提示**：数据仅供研究和教育目的使用。非财务建议。yfinance 与雅虎公司无关。

---

## 第 1 步：确保 yfinance 可用

**当前环境状态：**

```
!`python3 -c "exec('try:\n import yfinance\n print(\'yfinance \' + yfinance.__version__ + \' installed\')\nexcept Exception:\n print(\'YFINANCE_NOT_INSTALLED\')')"`
```

如果显示 `YFINANCE_NOT_INSTALLED`，请安装它：

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
import pandas as pd
from datetime import datetime

ticker = yf.Ticker("AAPL")  # 替换为实际代码

# --- 核心数据 ---
info = ticker.info
calendar = ticker.calendar

# --- 预期 ---
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

| 数据源 | 关键字段 | 目的 |
|---|---|---|
| `calendar` | 收益日期、除息日期 | 收益何时以及关键日期 |
| `earnings_estimate` | avg, low, high, numberOfAnalysts, yearAgoEps, growth (for 0q, +1q, 0y, +1y) | 共识 EPS 预期 |
| `revenue_estimate` | avg, low, high, numberOfAnalysts, yearAgoRevenue, growth | 收入预期 |
| `earnings_history` | epsEstimate, epsActual, epsDifference, surprisePercent | 超额/不及预期记录 |
| `analyst_price_targets` | current, low, high, mean, median | 街头价格目标 |
| `recommendations` | Buy/Hold/Sell 数量 | 情绪分布 |
| `quarterly_income_stmt` | TotalRevenue, NetIncome, BasicEPS | 近期趋势 |

---

## 第 3 步：构建收益预告

将数据组装成一个结构化的简报。目标是让用户一眼就能看到他们需要的一切。

### 第 1 部分：收益日期和关键信息

从 `calendar` 报告即将到来的收益日期。包括：
- 公司名称、代码、行业、行业
- 即将到来的收益日期（以及是否在市场之前/之后）
- 当前股价和近期表现（1 周、1 月）
- 市值

### 第 2 部分：共识预期

展示 `earnings_estimate` 和 `revenue_estimate` 中的当前季度预期：

| 指标 | 共识 | 低 | 高 | 分析师数量 | 去年 | 增长 |
|---|---|---|---|---|---|---|
| EPS | $1.42 | $1.35 | $1.50 | 28 | $1.26 | +12.7% |
| 收入 | $94.3B | $92.1B | $96.8B | 25 | $89.5B | +5.4% |

如果预期范围异常宽（高/低差距 > 共识的 20%），则注明这表明高度不确定性。

### 第 3 部分：历史超额/不及预期记录

从 `earnings_history` 显示过去 4 个季度：

| 季度 | EPS 预期 | EPS 实际 | 超额 | 超额/不及 |
|---|---|---|---|---|
| Q3 2024 | $1.35 | $1.40 | +3.7% | 超额 |
| Q2 2024 | $1.30 | $1.33 | +2.3% | 超额 |
| Q1 2024 | $1.52 | $1.53 | +0.7% | 超额 |
| Q4 2023 | $2.10 | $2.18 | +3.8% | 超额 |

总结："AAPL 在过去 4 个季度中有 4 个季度超额完成 EPS 预期，平均超额 2.6%."

### 第 4 部分：分析师情绪

从 `recommendations` 和 `analyst_price_targets`：

- 当前推荐分布（强力买入 / 买入 / 持有 / 卖出 / 强力卖出）
- 价格目标范围：低、均值、中位数、高 vs. 当前价格
- 从均值目标隐含的上行/下行空间

### 第 5 部分：关键指标

根据季度财务数据，突出市场将关注的 3-5 件事：
- 收入增长趋势（加速还是减速？）
- 利润率轨迹（扩大还是压缩？）
- 任何显著季度环比变化的科目
- 如果数据中提供，则按细分领域细分

这一部分需要判断——思考这对这家公司/行业来说什么才是重要的。

---

## 第 4 步：回复用户

以干净、结构化的简报形式呈现预告：

1. **以标题开头**："AAPL 将于 [日期] 发布收益。以下是预期内容。"
2. **显示所有 5 个部分**，带有清晰的标题和表格
3. **以简短总结结束**：2-3 句话概括整体情况（基于预期、记录和情绪的牛市/熊市倾向——以“市场预期”而非个人建议为框架）

### 需要包含的注意事项
- 预期可能直到报告日期才会变化
- 历史超额完成不保证未来超额完成
- 雅虎财经数据可能比实时共识滞后几个小时
- 这不是财务建议

---

## 参考文件

- `references/api_reference.md` — 详细的 yfinance API 参考，用于收益和预期方法

当您需要确切的函数签名或边缘情况处理时，请阅读参考文件。
