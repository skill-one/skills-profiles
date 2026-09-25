为用户创建一个完整的 VectorBT 回测脚本。

## 参数

解析 `$ARGUMENTS` 为：策略名称 交易对 交易所 间隔

- `$0` = 策略名称（例如，ema-crossover, rsi, donchian, supertrend, macd, sda2, momentum）
- `$1` = 交易对（例如，SBIN, RELIANCE, NIFTY）。默认：SBIN
- `$2` = 交易所（例如，NSE, NFO）。默认：NSE
- `$3` = 间隔（例如，D, 1h, 5m）。默认：D

如果没有参数，则询问用户他们想要哪种策略。

## 说明

1. 读取 vectorbt-expert 技能规则作为参考模式
2. 如果 `backtesting/{strategy_name}/` 目录不存在，则创建该目录（按需）
3. 在 `backtesting/{strategy_name}/` 中创建一个名为 `{symbol}_{strategy}_backtest.py` 的 `.py` 文件
4. 使用 `rules/assets/{strategy}/backtest.py` 中的匹配模板作为起点
5. 脚本必须：
   - 使用 `find_dotenv()` 从项目根目录加载 `.env`（脚本目录自动向上查找）
   - 通过 OpenAlgo 的 `client.history()` 获取数据
   - 如果用户提供了一个 DuckDB 路径，则通过 `duckdb.connect(path, read_only=True)` 直接加载数据，而不是 OpenAlgo API。自动检测格式：Historify（`market_data` 表，时间戳）vs 自定义（`ohlcv` 表，日期+时间）。参见 vectorbt-expert 的 `rules/duckdb-data.md`。
   - 如果 `openalgo.ta` 无法导入（独立 DuckDB），则使用内联 `exrem()` 备用
   - **默认情况下，使用 OpenAlgo ta 为所有指标**（EMA, SMA, RSI, MACD, BBands, ATR, ADX, STDDEV, MOM，以及 90 多种更多指标）- `from openalgo import ta`
   - **只有当用户在请求中明确说明 "talib"/"TA-Lib" 时才使用 TA-Lib**；专业指标（Supertrend, Donchian, Ichimoku, HMA, KAMA, ALMA, ZLEMA, VWMA）始终来自 OpenAlgo ta，因为 TA-Lib 没有等价物
   - 使用 `ta.exrem()` 清理重复信号（在 `exrem` 之前始终 `.fillna(False)`）
   - 使用 `vbt.Portfolio.from_signals()` 并设置 `min_size=1, size_granularity=1`
   - **印度交割费用**：`fees=0.00111, fixed_fees=20` 用于交割股票
   - 通过 OpenAlgo 获取 NIFTY 基准（`symbol="NIFTY", exchange="NSE_INDEX"`）
   - 打印完整的 `pf.stats()`
   - **打印策略与基准对比表**（总回报率，夏普比率，索提诺比率，最大回撤，胜率，交易次数，利润因子）
   - **用普通语言为普通交易者解释回测报告**
   - 如果 `openstatz` 可用，则通过 `ostz.dashboard(...)` 生成 OpenStatz 交互式仪表板摘要表 - 一个自包含的离线 HTML 文件，无需服务器（始终使用 OpenStatz，永远不要 QuantStats；永远不要遗留的 `ostz.reports.html` 静态报告）。**在调用 `dashboard()` 之前设置 `strategy_returns.name`（例如 `""EMA 20/50 Crossover - SBIN"``）和 `benchmark.name`** - 这个名称，而不是 `title=` 参数，是摘要表显示的策略标题/列/图例（参见 openstatz-tearsheet 规则）
   - 使用 Plotly 绘制权益曲线和回撤（`template="plotly_dark"`）
   - 将交易导出为 CSV
6. 代码或日志输出中不要使用图标/表情符号

## 可用策略

| 策略         | 关键词         | 模板                      |
|------------|--------------|-------------------------|
| EMA 交叉     | `ema-crossover` | `assets/ema_crossover/backtest.py` |
| RSI         | `rsi`         | `assets/rsi/backtest.py` |
| Donchian 通道 | `donchian`    | `assets/donchian/backtest.py` |
| Supertrend  | `supertrend`  | `assets/supertrend/backtest.py` |
| MACD 突破   | `macd`        | `assets/macd/backtest.py` |
| SDA2        | `sda2`        | `assets/sda2/backtest.py` |
| 动量         | `momentum`    | `assets/momentum/backtest.py` |
| 双动量       | `dual-momentum` | `assets/dual_momentum/backtest.py` |
| 买入持有     | `buy-hold`    | `assets/buy_hold/backtest.py` |
| RSI 累积     | `rsi-accumulation` | `assets/rsi_accumulation/backtest.py` |

## 基准规则

- 默认：通过 OpenAlgo 的 NIFTY 50（`symbol="NIFTY", exchange="NSE_INDEX"`）
- 如果用户指定了不同的基准，则使用该基准
- 对于 yfinance：印度使用 `^NSEI`，美国市场使用 `^GSPC`（标普 500）
- 始终比较：总回报率，夏普比率，索提诺比率，最大回撤

## 示例用法

`/backtest ema-crossover RELIANCE NSE D`
`/backtest rsi SBIN`
`/backtest supertrend NIFTY NFO 5m`
