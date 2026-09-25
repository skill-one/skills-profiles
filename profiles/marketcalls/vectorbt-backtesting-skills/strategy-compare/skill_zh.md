创建策略比较脚本。

## 参数

将 `$ARGUMENTS` 解析为：符号后跟策略名称

- `$0` = 符号（例如，SBIN、RELIANCE、NIFTY）
- 剩余参数 = 要比较的策略（例如，ema-crossover rsi donchian）

如果只给定符号而没有策略，则比较：ema-crossover、rsi、donchian、supertrend。

如果 "long-vs-short" 是策略之一，则比较第一个真实策略的 longonly 与 shortonly 与 both。

## 说明

1. 参考 vectorbt-expert 技能规则中的模式读取
2. 如果不存在，则创建 `backtesting/strategy_comparison/` 目录（按需）
3. 在 `backtesting/strategy_comparison/` 中创建一个名为 `{symbol}_strategy_comparison.py` 的 `.py` 文件
3. 脚本必须：
   - 通过 OpenAlgo 一次性获取数据
   - 如果用户提供了一个 DuckDB 路径，则通过 `duckdb.connect(path, read_only=True)` 直接加载数据。参见 vectorbt-expert `rules/duckdb-data.md`。
   - 如果 `openalgo.ta` 无法导入（独立的 DuckDB），则使用内联 `exrem()` 备用
   - **默认情况下对所有指标使用 OpenAlgo ta**（从不使用 VectorBT 内置）。只有当用户明确说 "talib"/"TA-Lib" 时才切换到 TA-Lib
   - **始终使用 OpenAlgo ta** 用于特殊指标（Supertrend、Donchian 等）- 没有TA-Lib的对应项
   - 使用 `ta.exrem()` 清理信号（始终在 `exrem` 之前 `.fillna(False)`）
   - 在相同数据上运行每个策略
   - **印度交割费**：`fees=0.00111, fixed_fees=20` 用于交割股票
   - 将每个策略的关键指标收集到一个并排的 DataFrame 中
   - **在比较表中包含 NIFTY 基准**（通过 OpenAlgo `NSE_INDEX`）
   - **打印策略与基准比较表**：总回报、夏普比率、索提诺比率、最大回撤、胜率、交易次数、盈亏比率
   - **用 plain language 解释结果** - 哪个策略表现最好以及为什么
   - 使用 Plotly 绘制所有策略的叠加权益曲线（`template="plotly_dark"`）
   - 将比较结果保存为 CSV
4. 不要在代码或日志输出中使用图标/表情符号

## 示例用法

`/strategy-compare RELIANCE ema-crossover rsi donchian`
`/strategy-compare SBIN long-vs-short ema-crossover`
