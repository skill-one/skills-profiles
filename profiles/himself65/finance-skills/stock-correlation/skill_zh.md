# 股票相关性分析技能

使用来自Yahoo Finance的历史价格数据[通过yfinance](https://github.com/ranaroussi/yfinance)查找和分析相关股票。根据用户意图路由到专门的子技能。

**重要提示**：这仅用于研究和教育目的。不是财务建议。yfinance与Yahoo公司无关。

---

## 第1步：确保依赖项可用

**当前环境状态**：

```
!`python3 -c "exec('try:\n import yfinance, pandas, numpy\n print(f\'yfinance={yfinance.__version__} pandas={pandas.__version__} numpy={numpy.__version__}\')\nexcept Exception:\n print(\'DEPS_MISSING\')')"`
```

如果`DEPS_MISSING`，在运行任何代码之前安装所需的软件包：

```python
import subprocess, sys
subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "yfinance", "pandas", "numpy"])
```

如果所有依赖项都已安装，则跳过安装步骤并直接进行。

---

## 第2步：路由到正确的子技能

对用户的请求进行分类，并跳转到下方的匹配子技能部分。

| 用户请求 | 路由到 | 示例 |
|---|---|---|
| 单个股票代码，希望找到相关股票 | **子技能A：共同运动发现** | "与NVDA相关什么"，"查找与AMD相关的股票"，"TSLA的同情交易" |
| 两个或多个特定股票代码，希望了解关系细节 | **子技能B：回报相关性** | "AMD和NVDA之间的相关性"，"LITE和COHR如何一起运动"，"比较AAPL与MSFT" |
| 一组股票代码，希望结构/分组 | **子技能C：行业聚类** | "FAANG的相关性矩阵"，"聚类这些半导体股票"，"AMD的行业同行" |
| 希望了解随时间变化或条件相关的相关性 | **子技能D：已实现相关性** | "AMD NVDA的滚动相关性"，"当NVDA下跌时还有什么是下跌的"，"相关性如何变化" |

如果模糊不清，默认为**子技能A**（共同运动发现）用于单个股票代码，或**子技能B**（回报相关性）用于两个股票代码。

### 所有子技能的默认值

| 参数 | 默认值 |
|---|---|
| 回顾期 | `1y`（1年） |
| 数据间隔 | `1d`（每日） |
| 相关性方法 | Pearson |
| 最小相关性阈值 | 0.60 |
| 结果数量 | 前10个 |
| 返回类型 | 每日对数回报 |
| 滚动窗口 | 60个交易日 |

---

## 子技能A：共同运动发现

**目标**：给定单个股票代码，找到与其一起运动的股票。

### A1：构建同行宇宙

您需要15-30个候选者。**不要使用硬编码的股票代码列表**——在运行时动态构建宇宙。参见`references/sector_universes.md`以获取完整实现。方法如下：

1. **筛选同一行业的股票**，使用`yf.screen()` + `yf.EquityQuery`查找与目标在同一行业的股票
2. **扩展到行业**，如果行业筛选返回的同行少于10个
3. **添加主题/相邻行业**——读取目标的`longBusinessSummary`并筛选1-2个相关行业（例如，半导体公司→同时筛选半导体设备）
4. **合并、去重、移除目标股票代码**

### A2：计算相关性

```python
import yfinance as yf
import pandas as pd
import numpy as np

def discover_comovement(target_ticker, peer_tickers, period="1y"):
    all_tickers = [target_ticker] + [t for t in peer_tickers if t != target_ticker]
    data = yf.download(all_tickers, period=period, auto_adjust=True, progress=False)

    # 提取收盘价——yf.download返回MultiIndex（价格，股票代码）列
    closes = data["Close"].dropna(axis=1, thresh=max(60, len(data) // 2))

    # 对数回报
    returns = np.log(closes / closes.shift(1)).dropna()
    corr_series = returns.corr()[target_ticker].drop(target_ticker, errors="ignore")

    # 按绝对相关性排序
    ranked = corr_series.abs().sort_values(ascending=False)

    result = pd.DataFrame({
        "股票代码": ranked.index,
        "相关性": [round(corr_series[t], 4) for t in ranked.index],
    })
    return result, returns
```

### A3：展示结果

显示一个排名表格，包含公司名称和行业（通过`yf.Ticker(t).info.get("shortName")`获取）：

| 排名 | 股票代码 | 公司 | 相关性 | 为什么相关 |
|---|---|---|---|---|
| 1 | AMD | Advanced Micro Devices | 0.82 | 同一行业—GPU/CPU |
| 2 | AVGO | Broadcom | 0.78 | AI基础设施同行 |

包括：
- 前10个正相关性股票
- 任何值得注意的负相关性股票（潜在的套期保值）
- 简要解释**为什么**每个可能相关（行业、供应链、客户重叠）

---

## 子技能B：回报相关性

**目标**：深入分析两个（或几个）特定股票代码之间的关系。

### B1：下载和计算

```python
import yfinance as yf
import pandas as pd
import numpy as np

def return_correlation(ticker_a, ticker_b, period="1y"):
    data = yf.download([ticker_a, ticker_b], period=period, auto_adjust=True, progress=False)
    closes = data["Close"][[ticker_a, ticker_b]].dropna()

    returns = np.log(closes / closes.shift(1)).dropna()
    corr = returns[ticker_a].corr(returns[ticker_b])

    # Beta：B每单位A的变动量
    cov_matrix = returns.cov()
    beta = cov_matrix.loc[ticker_b, ticker_a] / cov_matrix.loc[ticker_a, ticker_a]

    # R-squared
    r_squared = corr ** 2

    # 60天滚动相关性以保持稳定性
    rolling_corr = returns[ticker_a].rolling(60).corr(returns[ticker_b])

    # Spread（对数价格比率）用于均值回归
    spread = np.log(closes[ticker_a] / closes[ticker_b])
    spread_z = (spread - spread.mean()) / spread.std()

    return {
        "correlation": round(corr, 4),
        "beta": round(beta, 4),
        "r_squared": round(r_squared, 4),
        "rolling_corr_mean": round(rolling_corr.mean(), 4),
        "rolling_corr_std": round(rolling_corr.std(), 4),
        "rolling_corr_min": round(rolling_corr.min(), 4),
        "rolling_corr_max": round(rolling_corr.max(), 4),
        "spread_z_current": round(spread_z.iloc[-1], 4),
        "observations": len(returns),
    }
```

### B2：展示结果

显示一个摘要卡片：

| 指标 | 值 |
|---|---|
| Pearson相关性 | 0.82 |
| Beta（B vs A） | 1.15 |
| R-squared | 0.67 |
| 滚动相关性（60d平均） | 0.80 |
| 滚动相关性范围 | [0.55, 0.94] |
| 滚动相关性标准差 | 0.08 |
| Spread Z分数（当前） | +1.2 |
| 观察值 | 250 |

解释指南：
- **相关性 > 0.80**：强共同运动—这些股票紧密相关
- **相关性 0.50–0.80**：中等—共享行业驱动因素但独立因素太多
- **相关性 < 0.50**：弱—尽管可能存在行业重叠，但共同运动有限
- **高滚动标准差**：关系不稳定—相关性随时间变化显著
- **Spread Z > |2|**：与历史关系异常背离

---

## 子技能C：行业聚类

**目标**：给定一组股票代码，显示完整的相关性结构和识别聚类。

### C1：构建相关性矩阵

```python
import yfinance as yf
import pandas as pd
import numpy as np

def sector_clustering(tickers, period="1y"):
    data = yf.download(tickers, period=period, auto_adjust=True, progress=False)

    # yf.download返回MultiIndex（价格，股票代码）列
    closes = data["Close"].dropna(axis=1, thresh=max(60, len(data) // 2))
    returns = np.log(closes / closes.shift(1)).dropna()
    corr_matrix = returns.corr()

    # 谱系聚类顺序
    from scipy.cluster.hierarchy import linkage, leaves_list
    from scipy.spatial.distance import squareform

    dist_matrix = 1 - corr_matrix.abs()
    np.fill_diagonal(dist_matrix.values, 0)
    condensed = squareform(dist_matrix)
    linkage_matrix = linkage(condensed, method="ward")
    order = leaves_list(linkage_matrix)
    ordered_tickers = [corr_matrix.columns[i] for i in order]

    # 重新排序矩阵
    clustered = corr_matrix.loc[ordered_tickers, ordered_tickers]

    return clustered, returns
```

注意：如果`scipy`不可用，则回退到按平均相关性排序而不是层次聚类。

### C2：展示结果

1. **完整相关性矩阵**—格式化为表格。如果超过8个股票代码，显示为热图描述或仅突出显示最强/最弱的对。
2. **识别的聚类**—将具有高组内相关性的股票分组：
   - 聚类1：[NVDA, AMD, AVGO]—平均组内相关性0.82
   - 聚类2：[AAPL, MSFT]—平均组内相关性0.75
3. **异常值**—与组平均相关性低的股票（潜在的分散化因素）。
4. **最强对**—矩阵中前5个最高相关性对。
5. **最弱对**—矩阵中前5个最低/负相关性对（套期保值候选者）。

---

## 子技能D：已实现相关性

**目标**：显示相关性如何随时间变化以及在不同市场条件下如何变化。

### D1：滚动相关性

```python
import yfinance as yf
import pandas as pd
import numpy as np

def realized_correlation(ticker_a, ticker_b, period="2y", windows=[20, 60, 120]):
    data = yf.download([ticker_a, ticker_b], period=period, auto_adjust=True, progress=False)
    closes = data["Close"][[ticker_a, ticker_b]].dropna()

    returns = np.log(closes / closes.shift(1)).dropna()

    rolling = {}
    for w in windows:
        rolling[f"{w}d"] = returns[ticker_a].rolling(w).corr(returns[ticker_b])

    return rolling, returns
```

### D2：条件相关性

```python
def regime_correlation(returns, ticker_a, ticker_b, condition_ticker=None):
    """比较不同市场环境下的相关性。"""
    if condition_ticker is None:
        condition_ticker = ticker_a

    ret = returns[condition_ticker]

    regimes = {
        "所有交易日": pd.Series(True, index=returns.index),
        "上涨日（目标 > 0）": ret > 0,
        "下跌日（目标 < 0）": ret < 0,
        "高波动（前25%）": ret.abs() > ret.abs().quantile(0.75),
        "低波动（后25%）": ret.abs() < ret.abs().quantile(0.25),
        "大幅回撤（< -2%）": ret < -0.02,
    }

    results = {}
    for name, mask in regimes.items():
        subset = returns[mask]
        if len(subset) >= 20:
            results[name] = {
                "correlation": round(subset[ticker_a].corr(subset[ticker_b]), 4),
                "天数": int(mask.sum()),
            }

    return results
```

### D3：展示结果

1. **滚动相关性摘要表格**：

| 窗口 | 当前 | 平均 | 最小 | 最大 | 标准差 |
|---|---|---|---|---|---|
| 20天 | 0.88 | 0.76 | 0.32 | 0.95 | 0.12 |
| 60天 | 0.82 | 0.78 | 0.55 | 0.92 | 0.08 |
| 120天 | 0.80 | 0.79 | 0.68 | 0.88 | 0.05 |

2. **条件相关性表格**：

| 环境 | 相关性 | 天数 |
|---|---|---|
| 所有交易日 | 0.82 | 250 |
| 上涨日 | 0.75 | 132 |
| 下跌日 | 0.87 | 118 |
| 高波动（前25%） | 0.90 | 63 |
| 大幅回撤（< -2%） | 0.93 | 28 |

3. **关键洞察**：突出显示相关性是否在抛售期间**增加**（非常常见——"危机中相关性会达到1"）。这对风险管理至关重要。

4. **趋势**：相关性最近是**高于还是低于**历史平均水平？

---

## 第3步：响应用户

在运行适当的子技能后，清晰地呈现结果：

### 总是包括

- 使用的**回顾期**和**数据间隔**
- **观察值数量**（交易日）
- 任何因数据不足而**被排除的股票代码**

### 总是附注

- **相关性不是因果关系**—共同运动不意味着因果联系
- **过去的相关性不保证未来的相关性**—环境会变化
- **短期回顾窗口**产生噪声估计；较长的窗口平滑但可能错过环境变化

### 实际应用（在相关时提及）

- **同情交易**：可能跟随同行业绩的股票
- **配对交易**：高相关性对，其中价差已偏离均值
- **投资组合分散化**：寻找低相关性资产以降低风险
- **套期保值**：识别负相关性工具
- **行业轮动**：了解哪些行业一起运动
- **风险管理**：压力期间相关性激增—当最需要时分散化可能失效

**重要提示**：切勿建议具体交易。呈现数据并让用户得出结论。

---

## 参考文件

- `references/sector_universes.md` — 使用yfinance Screener API动态构建同行宇宙

在需要为给定股票代码构建同行宇宙时，请阅读参考文件。
