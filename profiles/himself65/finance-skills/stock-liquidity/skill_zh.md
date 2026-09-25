# 股票流动性分析技能

分析多个维度的股票流动性——买卖价差、成交量模式、订单簿深度、估计的市场冲击和换手率——使用来自 Yahoo Finance 的数据，通过 [yfinance](https://github.com/ranaroussi/yfinance)。

流动性很重要，因为它决定了实际交易成本。报价价格不是你实际支付的——价差、滑点和市场冲击都会侵蚀回报，特别是对于较大的头寸或流动性较差的股票。

**重要提示**：这仅用于研究和教育目的。不是财务建议。yfinance 与 Yahoo, Inc. 没有关联。

---

## 第 1 步：确保依赖项可用

**当前环境状态**：

```
!`python3 -c "exec('try:\n import yfinance, pandas, numpy\n print(f\'yfinance={yfinance.__version__} pandas={pandas.__version__} numpy={numpy.__version__}\')\nexcept Exception:\n print(\'DEPS_MISSING\')')"`
```

如果 `DEPS_MISSING`，安装所需的包：

```python
import subprocess, sys
subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "yfinance", "pandas", "numpy"])
```

如果已安装，则跳过并继续。

---

## 第 2 步：路由到正确的子技能

对用户的请求进行分类并跳转到匹配的部分。如果用户询问一般流动性评估而没有指定特定指标，则运行 **子技能 A（流动性仪表板）**，该仪表板会一起计算所有关键指标。

| 用户请求 | 路由到 | 示例 |
|---|---|---|
| 一般流动性检查，“X 的流动性如何” | **子技能 A：流动性仪表板** | "AAPL 的流动性如何"，"TSLA 的流动性分析"，"这只股票的流动性是否足够" |
| 买卖价差、交易成本、有效价差 | **子技能 B：价差分析** | "AMD 的买卖价差"，"NVDA 期权上的价差是多少"，"交易成本估计" |
| 成交量、ADTV、美元成交量、成交量分布 | **子技能 C：成交量分析** | "MSFT 的成交量分析"，"平均每日成交量"，"SPY 的成交量分布" |
| 订单簿深度、市场深度、二级市场 | **子技能 D：订单簿深度** | "AAPL 的订单簿深度"，"市场深度"，"显示给我订单簿" |
| 市场冲击、滑点、大额订单的执行成本 | **子技能 E：市场冲击** | "5 万股将如何移动价格"，"滑点估计"，"100 万美元订单的市场冲击" |
| 换手率、相对于流通股的交易活动 | **子技能 F：换手率** | "GME 的换手率"，"流通股换手率"，"这只股票的交易活跃度如何" |
| 比较多只股票的流动性 | **子技能 A**（多股票模式） | "AAPL 与 TSLA 的流动性比较"，"AMD 或 INTC 哪个流动性更高" |

### 默认值

| 参数 | 默认值 |
|---|---|
| 回溯期 | `3mo`（3 个月） |
| 数据间隔 | `1d`（每日） |
| 市场冲击模型 | 平方根模型 |
| 当日间隔（当需要时） | `5m` |

---

## 子技能 A：流动性仪表板

**目标**：为一只或多只股票生成综合流动性快照，结合所有关键指标。

### A1：获取数据并计算所有指标

```python
import yfinance as yf
import pandas as pd
import numpy as np

def liquidity_dashboard(ticker_symbol, period="3mo"):
    ticker = yf.Ticker(ticker_symbol)
    info = ticker.info
    hist = ticker.history(period=period)

    if hist.empty:
        return None

    # --- 价差指标（从当前报价） ---
    bid = info.get("bid", None)
    ask = info.get("ask", None)
    current_price = info.get("currentPrice") or info.get("regularMarketPrice") or hist["Close"].iloc[-1]

    spread = None
    spread_pct = None
    if bid and ask and bid > 0 and ask > 0:
        spread = round(ask - bid, 4)
        midpoint = (ask + bid) / 2
        spread_pct = round((spread / midpoint) * 100, 4)

    # --- 成交量指标 ---
    avg_volume = hist["Volume"].mean()
    median_volume = hist["Volume"].median()
    avg_dollar_volume = (hist["Close"] * hist["Volume"]).mean()
    volume_std = hist["Volume"].std()
    volume_cv = volume_std / avg_volume if avg_volume > 0 else None  # 变异系数

    # --- 换手率 ---
    shares_outstanding = info.get("sharesOutstanding", None)
    float_shares = info.get("floatShares", None)
    base_shares = float_shares or shares_outstanding
    turnover_ratio = round(avg_volume / base_shares, 6) if base_shares else None

    # --- Amihud 不流动性比率 ---
    # 每日回报绝对值 / 每日美元成交量的平均值
    returns = hist["Close"].pct_change().dropna()
    dollar_volume = (hist["Close"] * hist["Volume"]).iloc[1:]  # 与回报对齐
    amihud_values = returns.abs() / dollar_volume
    amihud = amihud_values[amihud_values.replace([np.inf, -np.inf], np.nan).notna()].mean()

    # --- 市场冲击估计（平方根模型） ---
    # 假设订单为 1% 的 ADV
    adv = avg_volume
    order_size = adv * 0.01
    daily_volatility = returns.std()
    sigma = daily_volatility
    participation_rate = order_size / adv if adv > 0 else 0
    impact_bps = sigma * np.sqrt(participation_rate) * 10000  # 以基点表示

    return {
        "ticker": ticker_symbol,
        "current_price": round(current_price, 2),
        "bid": bid,
        "ask": ask,
        "spread": spread,
        "spread_pct": spread_pct,
        "avg_daily_volume": int(avg_volume),
        "median_daily_volume": int(median_volume),
        "avg_dollar_volume": round(avg_dollar_volume, 0),
        "volume_cv": round(volume_cv, 3) if volume_cv else None,
        "shares_outstanding": shares_outstanding,
        "float_shares": float_shares,
        "turnover_ratio": turnover_ratio,
        "amihud_illiquidity": round(amihud * 1e9, 4) if not np.isnan(amihud) else None,
        "daily_volatility": round(daily_volatility * 100, 2),
        "impact_1pct_adv_bps": round(impact_bps, 2),
        "observations": len(hist),
    }
```

### A2：解释和展示

以摘要卡的形式展示。对于 Amihud 不流动性比率，乘以 1e9 以提高可读性（标准惯例）。

**流动性等级**（使用以下大致阈值来评估美国股票）：

| 等级 | 平均美元成交量 | 价差（%） | Amihud（×10⁹） |
|---|---|---|---|
| 非常高 | > $500M/天 | < 0.03% | < 0.01 |
| 高 | $50M–$500M/天 | 0.03–0.10% | 0.01–0.1 |
| 中等 | $5M–$50M/天 | 0.10–0.50% | 0.1–1.0 |
| 低 | $500K–$5M/天 | 0.50–2.00% | 1.0–10 |
| 非常低 | < $500K/天 | > 2.00% | > 10 |

当比较多只股票时，显示并排表格，并突出显示哪只股票流动性更高以及原因。

---

## 子技能 B：价差分析

**目标**：详细分析买卖价差，包括当前价差、期权数据的歷史背景和有效价差估计。

### B1：从报价获取当前价差

```python
import yfinance as yf

def spread_analysis(ticker_symbol):
    ticker = yf.Ticker(ticker_symbol)
    info = ticker.info

    bid = info.get("bid", 0)
    ask = info.get("ask", 0)
    bid_size = info.get("bidSize", None)
    ask_size = info.get("askSize", None)
    current_price = info.get("currentPrice") or info.get("regularMarketPrice", 0)

    result = {"bid": bid, "ask": ask, "bid_size": bid_size, "ask_size": ask_size}

    if bid > 0 and ask > 0:
        midpoint = (bid + ask) / 2
        result["absolute_spread"] = round(ask - bid, 4)
        result["relative_spread_pct"] = round((ask - bid) / midpoint * 100, 4)
        result["relative_spread_bps"] = round((ask - bid) / midpoint * 10000, 2)
    return result
```

### B2：期权价差背景

yfinance 中的期权数据包括每个行权价的买卖价差，这为衍生品流动性提供了参考。使用最近到期的期权，提取价内看涨和看跌期权，并计算每个价差的价差和价差百分比。

有关完整代码模板，请参阅 `references/liquidity_reference.md` § "Options Spread Analysis"。

### B3：展示结果

显示：
- 当前报价价差（绝对值、相对百分比、基点）
- 如果可用，则显示买卖报价量
- 价内期权价差，以供参考
- 该价差与该市值层级的典型范围相比如何

---

## 子技能 C：成交量分析

**目标**：分析交易量模式——平均值、趋势、相对成交量和美元成交量。

### C1：计算成交量指标

```python
import yfinance as yf
import pandas as pd
import numpy as np

def volume_analysis(ticker_symbol, period="3mo"):
    ticker = yf.Ticker(ticker_symbol)
    hist = ticker.history(period=period)

    if hist.empty:
        return None

    vol = hist["Volume"]
    close = hist["Close"]
    dollar_vol = vol * close

    # 相对成交量（今天与平均相比）
    rvol = vol.iloc[-1] / vol.mean() if vol.mean() > 0 else None

    # 成交量趋势（线性回归斜率在期间内）
    x = np.arange(len(vol))
    slope, _ = np.polyfit(x, vol.values, 1) if len(vol) > 1 else (0, 0)
    trend_pct = (slope * len(vol)) / vol.mean() * 100  # 期间内的百分比变化

    # 按星期几划分的成交量分布
    hist_copy = hist.copy()
    hist_copy["DayOfWeek"] = hist_copy.index.dayofweek
    day_names = {0: "Mon", 1: "Tue", 2: "Wed", 3: "Thu", 4: "Fri"}
    vol_by_day = hist_copy.groupby("DayOfWeek")["Volume"].mean()
    vol_by_day.index = vol_by_day.index.map(day_names)

    # 高/低成交量日
    high_vol_days = hist.nlargest(5, "Volume")[["Close", "Volume"]]
    low_vol_days = hist.nsmallest(5, "Volume")[["Close", "Volume"]]

    return {
        "avg_volume": int(vol.mean()),
        "median_volume": int(vol.median()),
        "avg_dollar_volume": round(dollar_vol.mean(), 0),
        "current_volume": int(vol.iloc[-1]),
        "relative_volume": round(rvol, 2) if rvol else None,
        "volume_trend_pct": round(trend_pct, 1),
        "volume_by_day": vol_by_day.to_dict(),
        "high_vol_days": high_vol_days,
        "low_vol_days": low_vol_days,
        "max_volume": int(vol.max()),
        "min_volume": int(vol.min()),
    }
```

### C2：展示结果

显示：
- 平均每日成交量（股数和美元），与中位数进行比较
- 相对成交量（RVOL）——今天的成交量与平均值相比。RVOL > 1.5 表示成交量较高；RVOL < 0.5 表示异常清淡
- 成交量趋势——交易活动是在增加还是减少？
- 星期几模式（如果存在有意义的变化）
- 5 个最高成交量日，提供背景信息（例如，盈利？新闻？）

---

## 子技能 D：订单簿深度

**目标**：使用可用的买卖报价数据估计订单簿深度。

Yahoo Finance 不提供完整的二级市场/订单簿数据。应明确说明这一限制。我们可以做的是：

1. **股票报价**：买入价、卖出价、买入报价量、卖出报价量（仅限订单簿顶部）
2. **期权链**：行权价的买卖价差和未平仓合约，提供衍生品深度的参考
3. **日内成交量分布**：日内成交量如何分布，表明连续市场的深度

### D1：收集可用的深度数据

收集三个数据点：

1. **订单簿顶部** — 从 `ticker.info` 获取买入价、卖出价、买入报价量、卖出报价量
2. **日内成交量分布** — 最后 5 天的 5 分钟 K 线图，按时间划分并归一化为每日成交量的百分比
3. **期权未平仓合约** — 最近到期期权总看涨/看跌未平仓合约和成交量，作为衍生品深度参考

有关完整代码模板，请参阅 `references/liquidity_reference.md` § "Order Book Depth Proxy"。

### D2：展示结果

显示：
- **订单簿顶部**：当前买入价/卖出价及大小
- **日内成交量形状**：成交量集中在何处（开盘/收盘与盘中）
- **期权深度**：总未平仓合约和成交量作为衍生品流动性的参考
- **诚实限制**： "Yahoo Finance 仅提供订单簿顶部数据。对于完整的二级市场深度，需要直接的市场数据源（例如，NYSE OpenBook、NASDAQ TotalView）。

---

## 子技能 E：市场冲击

**目标**：使用平方根市场冲击模型估计特定订单大小将如何移动价格。

实践中标准的模型是：**冲击（%）= σ × √(Q / V)**，其中 σ 是每日波动率，Q 是股份数量，V 是平均每日成交量。这是机构交易者使用的 Almgren-Chriss 框架的简化版本。

### E1：计算市场冲击估计

```python
import yfinance as yf
import numpy as np

def market_impact(ticker_symbol, order_shares=None, order_dollars=None, period="3mo"):
    ticker = yf.Ticker(ticker_symbol)
    hist = ticker.history(period=period)
    info = ticker.info

    if hist.empty:
        return None

    current_price = info.get("currentPrice") or hist["Close"].iloc[-1]
    avg_volume = hist["Volume"].mean()
    daily_volatility = hist["Close"].pct_change().dropna().std()

    # 确定订单大小（股数）
    if order_dollars and not order_shares:
        order_shares = order_dollars / current_price
    elif not order_shares:
        # 默认：估计各种大小
        order_shares = avg_volume * 0.01  # 1% 的 ADV

    participation_rate = order_shares / avg_volume if avg_volume > 0 else 0
    pct_adv = (order_shares / avg_volume * 100) if avg_volume > 0 else 0

    # 平方根冲击模型
    impact_pct = daily_volatility * np.sqrt(participation_rate) * 100
    impact_bps = impact_pct * 100
    impact_dollars = impact_pct / 100 * current_price * order_shares

    # 生成多个订单大小的冲击曲线
    sizes = [0.001, 0.005, 0.01, 0.02, 0.05, 0.10, 0.20, 0.50]  # 以 ADV 的百分比表示
    curve = []
    for s in sizes:
        q = avg_volume * s
        imp = daily_volatility * np.sqrt(s) * 100
        curve.append({
            "pct_adv": round(s * 100, 1),
            "shares": int(q),
            "dollars": round(q * current_price, 0),
            "impact_bps": round(imp * 100, 1),
            "impact_dollars_per_share": round(imp / 100 * current_price, 4),
        })

    return {
        "ticker": ticker_symbol,
        "current_price": round(current_price, 2),
        "avg_daily_volume": int(avg_volume),
        "daily_volatility_pct": round(daily_volatility * 100, 2),
        "order_shares": int(order_shares),
        "order_dollars": round(order_shares * current_price, 0),
        "pct_of_adv": round(pct_adv, 2),
        "estimated_impact_bps": round(impact_bps, 1),
        "estimated_impact_pct": round(impact_pct, 4),
        "estimated_impact_total_dollars": round(impact_dollars, 2),
        "impact_curve": curve,
    }
```

### E2：展示结果

显示：
- 估计的特定订单大小的冲击
- 冲击曲线表格，显示成本如何随订单大小变化
- 背景： "这使用平方根市场冲击模型，这是机构交易者使用的标准估计。实际冲击取决于执行策略（VWAP、TWAP 等）、交易时间和当前市场状况。"
- 如果冲击 > 50 bps，则标记该订单相对于流动性较大，建议用户考虑算法执行或将订单分摊到多日

---

## 子技能 F：换手率

**目标**：衡量股票交易活动相对于其流通股和自由流通股的活跃程度。

### F1：计算换手率指标

```python
import yfinance as yf
import pandas as pd
import numpy as np

def turnover_analysis(ticker_symbol, period="3mo"):
    ticker = yf.Ticker(ticker_symbol)
    hist = ticker.history(period=period)
    info = ticker.info

    if hist.empty:
        return None

    avg_volume = hist["Volume"].mean()
    shares_outstanding = info.get("sharesOutstanding")
    float_shares = info.get("floatShares")

    result = {
        "avg_daily_volume": int(avg_volume),
        "shares_outstanding": shares_outstanding,
        "float_shares": float_shares,
    }

    if shares_outstanding:
        daily_turnover = avg_volume / shares_outstanding
        result["daily_turnover_ratio"] = round(daily_turnover, 6)
        result["annualized_turnover"] = round(daily_turnover * 252, 2)
        result["days_to_trade_float"] = round(
            (float_shares or shares_outstanding) / avg_volume, 1
        ) if avg_volume > 0 else None

    if float_shares:
        float_turnover = avg_volume / float_shares
        result["float_turnover_daily"] = round(float_turnover, 6)
        result["float_turnover_annualized"] = round(float_turnover * 252, 2)

    # 换手率趋势
    vol = hist["Volume"]
    base = float_shares or shares_outstanding
    if base:
        hist_copy = hist.copy()
        hist_copy["turnover"] = hist_copy["Volume"] / base
        recent_turnover = hist_copy["turnover"].tail(20).mean()
        older_turnover = hist_copy["turnover"].head(20).mean()
        if older_turnover > 0:
            result["turnover_trend_pct"] = round(
                (recent_turnover - older_turnover) / older_turnover * 100, 1
            )

    return result
```

### F2：展示结果

显示：
- 每日和年度换手率（相对于流通股和自由流通股）
- "自由流通股交易天数"——平均成交量下需要多少天才能周转整个自由流通股
- 换手率趋势——这只股票的交易活跃度是在增加还是减少？
- 背景：

| 换手率（年度化） | 解释 |
|---|---|
| > 500% | 极度活跃——可能是投机或动量驱动 |
| 100–500% | 积极交易 |
| 30–100% | 中等活动 |
| < 30% | 流动性差——可能是机构持有或被忽视 |

---

## 第 3 步：响应用户

运行适当的子技能后：

### 总是包括

- 用于歷史指标**的回溯期**
- **数据时间戳**——价差和报价是快照，不是实时数据
- 任何返回**空数据**的股票（无效代码、退市等）

### 总是附注

- Yahoo Finance 报价数据有**15 分钟延迟**，适用于大多数交易所——显示的价差可能无法反映当前实时市场
- 完整的订单簿（二级市场）数据**无法**通过 Yahoo Finance 获取
- 市场冲击估计是**模型，不是保证**——实际执行成本取决于策略、时间和市场状况
- 流动性可以**迅速变化**——今天流动性的股票明天可能不再流动（尤其是在事件、停牌或盘后交易期间）

### 实用建议（在相关时提及）

- **头寸规模**：如果估计冲击超过 25 bps，该头寸对于这只股票的流动性可能太大
- **小型/微型股警告**：每日美元成交量小于 $1M 的股票需要小心执行
- **价差成本复合**：双向交易（买入 + 卖出）的 0.10% 价差成本为 0.20% ——这对于活跃策略来说会累积
- **流动性溢价**：流动性差的股票历史上会获得更高的回报作为补偿——但交易成本可能会侵蚀这部分溢价

**重要提示**：永远不要建议具体的交易。展示流动性数据，让用户自行做出决定。
