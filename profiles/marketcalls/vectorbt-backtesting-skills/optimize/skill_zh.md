为 VectorBT 策略创建参数优化脚本。

## 参数

将 `$ARGUMENTS` 解析为：策略符号 交易所 间隔

- `$0` = 策略名称（例如，ema-crossover, rsi, donchian）。默认：ema-crossover
- `$1` = 符号（例如，SBIN, RELIANCE, NIFTY）。默认：SBIN
- `$2` = 交易所（例如，NSE, NFO）。默认：NSE
- `$3` = 间隔（例如，D, 1h, 5m）。默认：D

如果没有参数，则询问用户要优化哪个策略。

## 指令

1.  参考 vectorbt-expert 技能规则中的模式
2.  如果 `backtesting/{strategy_name}/` 目录不存在，则创建该目录（按需）
3.  在 `backtesting/{strategy_name}/` 中创建一个名为 `{symbol}_{strategy}_optimize.py` 的 `.py` 文件
4.  脚本必须：
   - 使用 `find_dotenv()` 从项目根目录加载 `.env`，并通过 OpenAlgo `client.history()` 获取数据
   - 如果用户提供了一个 DuckDB 路径，则通过 `duckdb.connect(path, read_only=True)` 直接加载数据。参见 vectorbt-expert `rules/duckdb-data.md`。
   - 如果 `openalgo.ta` 无法导入（独立 DuckDB），则使用内联 `exrem()` 备用方案
   - **默认情况下对所有指标使用 OpenAlgo ta**（永不使用 VectorBT 内置）。只有当用户明确说明 "talib"/"TA-Lib" 时才切换到 TA-Lib
   - **始终使用 OpenAlgo ta** 用于特殊指标（Supertrend, Donchian 等）——没有 TA-Lib 对应项
   - 使用 `ta.exrem()` 清理信号（在 `exrem` 之前始终 `.fillna(False)`）
   - 为所选策略定义合理的参数范围
   - 使用基于循环的优化来收集每个组合的多个指标
   - 跟踪：总回报率、夏普比率、最大回撤、交易次数，每个组合
   - 使用 `tqdm` 进度条
   - **印度交割费**：`fees=0.00111, fixed_fees=20` 用于交割股票
   - 通过总回报率和夏普比率找到最佳参数
   - 为两个标准打印前 10 名结果
   - 生成总回报率在参数网格上的 Plotly 热图（`template="plotly_dark"`）
   - 生成夏普比率在参数网格上的 Plotly 热图
   - **获取 NIFTY 基准**，并将最佳参数与基准进行比较
   - **打印策略与基准比较表**
   - **用普通语言解释结果**，供普通交易者理解
   - 将结果保存到 CSV
4. 代码或日志输出中永不使用图标/表情符号
5. 对于期货符号，使用考虑合约手数的尺寸：
   - NIFTY: `min_size=65, size_granularity=65`
   - BANKNIFTY: `min_size=30, size_granularity=30`

## 默认参数范围

| 策略       | 参数 1        | 参数 2        |
|------------|---------------|---------------|
| ema-crossover | 快速 EMA: 5-50 | 慢速 EMA: 10-60 |
| rsi         | 窗口: 5-30    | 超卖: 20-40   |
| donchian    | 期间: 5-50    | -             |
| supertrend  | 期间: 5-30    | 乘数: 1.0-5.0  |

## 示例用法

`/optimize ema-crossover RELIANCE NSE D`
`/optimize rsi SBIN`
