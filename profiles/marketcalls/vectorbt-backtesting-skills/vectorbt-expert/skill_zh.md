# VectorBT 回测专家技能

## 环境

- Python 配备 vectorbt、pandas、numpy、plotly
- 数据源：OpenAlgo（印度市场）、DuckDB（直接数据库）、yfinance（美国/全球）、CCXT（加密货币）、自定义提供者
- DuckDB 支持：支持自定义 DuckDB 和 OpenAlgo Historify 格式
- API 密钥通过 `python-dotenv` + `find_dotenv()` 从单个根 `.env` 文件加载——绝不硬编码密钥
- 技术指标：**OpenAlgo ta**（默认 - `from openalgo import ta`，包含 100 多个指标，涵盖趋势/动量/波动率/成交量/震荡器/统计/混合）。仅在用户明确要求使用 TA-Lib/talib 时使用 **TA-Lib**。无论如何，都绝不使用 VectorBT 内置指标。
- 专业指标（无 TA-Lib 对应项，始终使用 `openalgo.ta`）：Supertrend、Donchian、Ichimoku、HMA、KAMA、ALMA、ZLEMA、VWMA
- 信号清理：`openalgo.ta` 用于极端、交叉、下穿、翻转（始终，无论指标库）
- 费用模式：印度市场标准（STT + 法定费用 + 每订单 20 卢比）
- 基准：默认通过 OpenAlgo (`NSE_INDEX`) 获取 NIFTY 50
- 图表：Plotly 配置 `template="plotly_dark"`
- 环境变量通过 `find_dotenv()` 从项目根目录下的单个 `.env` 文件加载（从脚本目录向上查找）
- 脚本存放在 `backtesting/{策略名称}/` 目录中（按需创建，非预创建）
- 代码或日志输出中绝不用图标/表情符号

## 关键规则

1. **所有技术指标默认使用 OpenAlgo ta** (`from openalgo import ta`)（EMA、SMA、RSI、MACD、BBANDS、ATR、ADX、STDDEV、MOM 及 90 多个更多指标）。**仅在用户在提示中明确要求 "talib"/"TA-Lib"** 时使用 TA-Lib。无论如何，都绝不使用 `vbt.MA.run()`、`vbt.RSI.run()` 或任何 VectorBT 内置指标。
2. **始终使用 OpenAlgo ta** 用于 TA-Lib 完全不存在的指标：Supertrend、Donchian、Ichimoku、HMA、KAMA、ALMA、ZLEMA、VWMA——这些没有 TA-Lib 对应项，因此即使在 TA-Lib 可选脚本中也使用 openalgo.ta。
3. **始终使用 OpenAlgo ta** 用于信号工具：`ta.exrem()`、`ta.crossover()`、`ta.crossunder()`、`ta.flip()`。如果 `openalgo.ta` 无法导入（独立的 DuckDB），则使用内联 `exrem()` 备用。参见 [duckdb-data](rules/duckdb-data.md)。
4. **生成原始买入/卖出信号后，始终使用 `ta.exrem()` 清理信号**。清理前始终 `.fillna(False)`。
5. **市场特定费用**：印度 ([indian-market-costs](rules/indian-market-costs.md))、美国 ([us-market-costs](rules/us-market-costs.md))、加密货币 ([crypto-market-costs](rules/crypto-market-costs.md))。根据用户市场自动选择。
6. **默认基准**：印度=NIFTY（通过 OpenAlgo）、美国=S&P 500 (`^GSPC`)、加密货币=比特币 (`BTC-USD`)。参见 [data-fetching](rules/data-fetching.md) 市场选择指南。
7. **每次回测后始终生成** 策略与基准对比表。
8. **始终用平实语言解释** 回测报告，以便普通交易者理解风险和优势。
9. **Plotly 蜡烛图必须使用 `xaxis type="category"`** 以避免周末缺口。
10. **整股交易**：始终设置 `min_size=1, size_granularity=1` 用于股票。
11. **DuckDB 数据加载**：当用户提供 DuckDB 路径时，使用 `duckdb.connect()` 并设置 `read_only=True` 直接加载数据。自动检测格式：OpenAlgo Historify（表 `market_data`，时间戳）或自定义（表 `ohlcv`，日期+时间列）。参见 [duckdb-data](rules/duckdb-data.md)。

## 模块化规则文件

每个主题的详细参考在 `rules/`：

| 规则文件 | 主题 |
|---------|------|
| [data-fetching](rules/data-fetching.md) | OpenAlgo（印度）、yfinance（美国）、CCXT（加密货币）、自定义提供者、.env 设置 |
| [simulation-modes](rules/simulation-modes.md) | from_signals、from_orders、from_holding、方向类型 |
| [position-sizing](rules/position-sizing.md) | 金额/价值/百分比/目标百分比规模 |
| [indicators-signals](rules/indicators-signals.md) | OpenAlgo ta 指标参考（默认）、TA-Lib 可选、信号生成 |
| [openalgo-ta-helpers](rules/openalgo-ta-helpers.md) | OpenAlgo ta 完整目录（100 多个指标）：exrem、crossover、Supertrend、Donchian、Ichimoku、MAs |
| [stop-loss-take-profit](rules/stop-loss-take-profit.md) | 固定止损、止盈、跟踪止损 |
| [parameter-optimization](rules/parameter-optimization.md) | 广播和基于循环的优化 |
| [performance-analysis](rules/performance-analysis.md) | 统计、指标、基准对比、CAGR |
| [plotting](rules/plotting.md) | 蜡烛图（分类 x 轴）、VectorBT 图表、自定义 Plotly |
| [indian-market-costs](rules/indian-market-costs.md) | 印度市场按板块划分的费用模式 |
| [us-market-costs](rules/us-market-costs.md) | 美国市场费用模式（股票、期权、期货） |
| [crypto-market-costs](rules/crypto-market-costs.md) | 加密货币费用模式（现货、USDT-M、COIN-M 期货） |
| [futures-backtesting](rules/futures-backtesting.md) | 合约大小（SEBI 2025 年 12 月修订）、价值规模 |
| [long-short-trading](rules/long-short-trading.md) | 同时多空、方向对比 |
| [duckdb-data](rules/duckdb-data.md) | DuckDB 直接加载、Historify 格式、自动检测、重采样、多符号 |
| [csv-data-resampling](rules/csv-data-resampling.md) | 加载 CSV、使用印度市场对齐重采样 |
| [walk-forward](rules/walk-forward.md) | 步进式分析、WFE 比率 |
| [robustness-testing](rules/robustness-testing.md) | 蒙特卡洛、噪声测试、参数敏感性、延迟测试 |
| [pitfalls](rules/pitfalls.md) | 常见错误和上线前检查清单 |
| [strategy-catalog](rules/strategy-catalog.md) | 带代码片段的策略参考 |
| [openstatz-tearsheet](rules/openstatz-tearsheet.md) | OpenStatz 离线交互式仪表板、指标、蒙特卡洛（替代 QuantStats） |

## 策略模板（位于 rules/assets/）

带真实费用、NIFTY 基准、对比表和平实语言报告的生产就绪脚本：

| 模板 | 路径 | 描述 |
|------|------|------|
| EMA 交叉 | `assets/ema_crossover/backtest.py` | EMA 10/20 交叉 |
| RSI | `assets/rsi/backtest.py` | RSI(14) 低位/高位 |
| Donchian | `assets/donchian/backtest.py` | Donchian 带状突破 |
| Supertrend | `assets/supertrend/backtest.py` | 带日内会话的 Supertrend |
| MACD | `assets/macd/backtest.py` | MACD 信号-蜡烛突破 |
| SDA2 | `assets/sda2/backtest.py` | SDA2 趋势跟踪 |
| 动量 | `assets/momentum/backtest.py` | 双重动量（MOM + MOM-of-MOM） |
| 双重动量 | `assets/dual_momentum/backtest.py` | 季度 ETF 轮换 |
| 买入持有 | `assets/buy_hold/backtest.py` | 静态多资产配置 |
| RSI 累积 | `assets/rsi_accumulation/backtest.py` | 每周 RSI 板块式累积 |
| 步进式 | `assets/walk_forward/template.py` | 步进式分析模板 |
| 真实费用 | `assets/realistic_costs/template.py` | 交易费用影响对比 |

## 快速模板：标准回测脚本

```python
import os
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import vectorbt as vbt
from dotenv import find_dotenv, load_dotenv
from openalgo import api, ta

# --- 配置 ---
script_dir = Path(__file__).resolve().parent
load_dotenv(find_dotenv(), override=False)

SYMBOL = "SBIN"
EXCHANGE = "NSE"
INTERVAL = "D"
INIT_CASH = 1_000_000
FEES = 0.00111              # 印度交割股票（STT + 法定费用）
FIXED_FEES = 20             # 每订单 20 卢比
ALLOCATION = 0.75
BENCHMARK_SYMBOL = "NIFTY"
BENCHMARK_EXCHANGE = "NSE_INDEX"

# --- 获取数据 ---
client = api(
    api_key=os.getenv("OPENALGO_API_KEY"),
    host=os.getenv("OPENALGO_HOST", "http://127.0.0.1:5000"),
)

end_date = datetime.now().date()
start_date = end_date - timedelta(days=365 * 3)

df = client.history(
    symbol=SYMBOL, exchange=EXCHANGE, interval=INTERVAL,
    start_date=start_date.strftime("%Y-%m-%d"),
    end_date=end_date.strftime("%Y-%m-%d"),
)
if "timestamp" in df.columns:
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.set_index("timestamp")
else:
    df.index = pd.to_datetime(df.index)
df = df.sort_index()
if df.index.tz is not None:
    df.index = df.index.tz_convert(None)

close = df["close"]

# --- 策略：EMA 交叉（OpenAlgo ta - 默认指标库） ---
ema_fast = ta.ema(close, 10)
ema_slow = ta.ema(close, 20)

buy_raw = (ema_fast > ema_slow) & (ema_fast.shift(1) <= ema_slow.shift(1))
sell_raw = (ema_fast < ema_slow) & (ema_fast.shift(1) >= ema_slow.shift(1))

entries = ta.exrem(buy_raw.fillna(False), sell_raw.fillna(False))
exits = ta.exrem(sell_raw.fillna(False), buy_raw.fillna(False))

# --- 回测 ---
pf = vbt.Portfolio.from_signals(
    close, entries, exits,
    init_cash=INIT_CASH, size=ALLOCATION, size_type="percent",
    fees=FEES, fixed_fees=FIXED_FEES, direction="longonly",
    min_size=1, size_granularity=1, freq="1D",
)

# --- 基准 ---
df_bench = client.history(
    symbol=BENCHMARK_SYMBOL, exchange=BENCHMARK_EXCHANGE, interval=INTERVAL,
    start_date=start_date.strftime("%Y-%m-%d"),
    end_date=end_date.strftime("%Y-%m-%d"),
)
if "timestamp" in df_bench.columns:
    df_bench["timestamp"] = pd.to_datetime(df_bench["timestamp"])
    df_bench = df_bench.set_index("timestamp")
else:
    df_bench.index = pd.to_datetime(df_bench.index)
df_bench = df_bench.sort_index()
if df_bench.index.tz is not None:
    df_bench.index = df_bench.index.tz_convert(None)
bench_close = df_bench["close"].reindex(close.index).ffill().bfill()
pf_bench = vbt.Portfolio.from_holding(bench_close, init_cash=INIT_CASH, fees=FEES, freq="1D")

# --- 结果 ---
print(pf.stats())

# --- 策略与基准对比 ---
comparison = pd.DataFrame({
    "策略": [
        f"{pf.total_return() * 100:.2f}%", f"{pf.sharpe_ratio():.2f}",
        f"{pf.sortino_ratio():.2f}", f"{pf.max_drawdown() * 100:.2f}%",
        f"{pf.trades.win_rate() * 100:.1f}%", f"{pf.trades.count()}",
        f"{pf.trades.profit_factor():.2f}",
    ],
    f"基准 ({BENCHMARK_SYMBOL})": [
        f"{pf_bench.total_return() * 100:.2f}%", f"{pf_bench.sharpe_ratio():.2f}",
        f"{pf_bench.sortino_ratio():.2f}", f"{pf_bench.max_drawdown() * 100:.2f}%",
        "-", "-", "-",
    ],
}, index=["总回报", "夏普比率", "索提诺比率", "最大回撤",
          "胜率", "总交易次数", "盈亏比"])
print(comparison.to_string())

# --- 解释 ---
print(f"* 总回报：{pf.total_return() * 100:.2f}% vs NIFTY {pf_bench.total_return() * 100:.2f}%")
print(f"* 最大回撤：{pf.max_drawdown() * 100:.2f}%")
print(f"  -> 在 Rs {INIT_CASH:,} 中，最差暂时亏损 = Rs {abs(pf.max_drawdown()) * INIT_CASH:,.0f}")

# --- 绘图 ---
fig = pf.plot(subplots=['value', 'underwater', 'cum_returns'], template="plotly_dark")
fig.show()

# --- 导出 ---
pf.positions.records_readable.to_csv(script_dir / f"{SYMBOL}_trades.csv", index=False)
```

## 快速模板：DuckDB 回测脚本

```python
import datetime as dt
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd
import vectorbt as vbt

try:
    # 默认：OpenAlgo ta 用于指标和信号清理
    from openalgo import ta
    exrem = ta.exrem
    ema = ta.ema
except ImportError:
    # 仅当 openalgo 包本身未安装时（独立的 DuckDB，无 OpenAlgo）使用 TA-Lib
    # 指标使用 TA-Lib，信号清理使用此内联 exrem() 替代。
    import talib as tl

    def ema(data, period):
        return pd.Series(tl.EMA(data.values, timeperiod=period), index=data.index)

    def exrem(signal1, signal2):
        result = signal1.copy()
        active = False
        for i in range(len(signal1)):
            if active:
                result.iloc[i] = False
            if signal1.iloc[i] and not active:
                active = True
            if signal2.iloc[i]:
                active = False
        return result

# --- 配置 ---
SYMBOL = "SBIN"
DB_PATH = r"path/to/market_data.duckdb"
INIT_CASH = 1_000_000
FEES = 0.000225              # 印度日内股票
FIXED_FEES = 20

# --- 从 DuckDB 加载数据 ---
con = duckdb.connect(DB_PATH, read_only=True)
df = con.execute("""
    SELECT date, time, open, high, low, close, volume
    FROM ohlcv WHERE symbol = ? ORDER BY date, time
""", [SYMBOL]).fetchdf()
con.close()

df["datetime"] = pd.to_datetime(df["date"].astype(str) + " " + df["time"].astype(str))
df = df.set_index("datetime").sort_index()
df = df.drop(columns=["date", "time"])

# --- 重采样到 5 分钟 ---
df_5m = df.resample("5min", origin="start_day", offset="9h15min",
                     label="right", closed="right").agg({
    "open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"
}).dropna()
close = df_5m["close"]

# --- 策略 + 回测（与 OpenAlgo 模板相同，但使用上面解析的 ema()/exrem()） ---
```

如果用户明确要求使用 TA-Lib，则跳过上面的 `try/except` 并直接 `import talib as tl`——仅当 `openalgo` 本身不可用时才使用 exrem 备用。
