# 回测交易策略

## 概述

在投入真实资本之前，使用历史数据验证交易策略。这项技能提供了一个完整的回测框架，包含8种内置策略、全面的性能指标和参数优化功能。

**主要功能：**
- 8种预置交易策略（简单移动平均线、指数移动平均线、相对强弱指数、MACD、布林带、突破、均值回归、动量）
- 完整的性能指标（夏普比率、索提诺比率、卡玛比率、在险价值、最大回撤）
- 参数网格搜索优化
- 资产曲线可视化
- 逐笔交易分析

## 前置条件

安装必要的依赖项：

```bash
pip install pandas numpy yfinance matplotlib
```

高级功能的可选安装：

```bash
pip install ta-lib scipy scikit-learn
```

## 使用说明

### 第1步：获取历史数据

```bash
python {baseDir}/scripts/fetch_data.py --symbol BTC-USD --period 2y --interval 1d
```

数据会缓存到 `{baseDir}/data/{symbol}_{interval}.csv` 以供重复使用。

### 第2步：运行回测

使用默认参数的基本回测：

```bash
python {baseDir}/scripts/backtest.py --strategy sma_crossover --symbol BTC-USD --period 1y
```

使用自定义参数的高级回测：

```bash
# 示例：使用特定日期范围回测
python {baseDir}/scripts/backtest.py \
  --strategy rsi_reversal \
  --symbol ETH-USD \
  --period 1y \
  --capital 10000 \
  --params '{"period": 14, "overbought": 70, "oversold": 30}'
```

### 第3步：分析结果

结果会保存到 `{baseDir}/reports/`，包括：
- `*_summary.txt` - 性能指标
- `*_trades.csv` - 交易日志
- `*_equity.csv` - 资产曲线数据
- `*_chart.png` - 资产曲线可视化

### 第4步：优化参数

通过网格搜索找到最佳参数：

```bash
python {baseDir}/scripts/optimize.py \
  --strategy sma_crossover \
  --symbol BTC-USD \
  --period 1y \
  --param-grid '{"fast_period": [10, 20, 30], "slow_period": [50, 100, 200]}'
```

## 输出

### 性能指标

| 指标 | 描述 |
|------|------|
| 总收益率 | 总体盈亏百分比 |
| CAGR | 复合年增长率 |
| 夏普比率 | 风险调整回报率（目标：>1.5） |
| 索提诺比率 | 下行风险调整回报率 |
| 卡玛比率 | 收益率与最大回撤的比值 |

### 风险指标

| 指标 | 描述 |
|------|------|
| 最大回撤 | 最大峰谷跌幅 |
| VaR (95%) | 95%置信度下的在险价值 |
| CVaR (95%) | VaR之外的预期损失 |
| 波动率 | 年化标准差 |

### 交易统计

| 指标 | 描述 |
|------|------|
| 总交易次数 | 往返交易数量 |
| 胜率 | 盈利交易的百分比 |
| 盈亏比 | 毛利润与毛亏损的比值 |
| 期望值 | 每笔交易的预期收益 |

### 示例输出

```
================================================================================
                    回测结果：简单移动平均线交叉
                    BTC-USD | [开始日期] 至 [结束日期]
================================================================================
 性能                          | 风险
 总收益率：        +47.32%         | 最大回撤：      -18.45%
 CAGR：                +47.32%         | VaR (95%):         -2.34%
 夏普比率：        1.87            | 波动率：        42.1%
 索提诺比率：       2.41            | 资金曲线指标：   8.2
--------------------------------------------------------------------------------
 交易统计
 总交易次数：        24              | 盈亏比：     2.34
 胜率：            58.3%           | 期望值：        $197.17
 平均盈利：         $892.45         | 最大连续亏损次数： 3
================================================================================
```

## 支持的策略

| 策略 | 描述 | 关键参数 |
|------|------|----------|
| `sma_crossover` | 简单移动平均线交叉 | `fast_period`, `slow_period` |
| `ema_crossover` | 指数移动平均线交叉 | `fast_period`, `slow_period` |
| `rsi_reversal` | 相对强弱指数超买/超卖 | `period`, `overbought`, `oversold` |
| `macd` | MACD信号线交叉 | `fast`, `slow`, `signal` |
| `bollinger_bands` | 布林带均值回归 | `period`, `std_dev` |
| `breakout` | 价格突破区间 | `lookback`, `threshold` |
| `mean_reversion` | 回归移动平均线 | `period`, `z_threshold` |
| `momentum` | 变化率动量 | `period`, `threshold` |

## 配置

创建 `{baseDir}/config/settings.yaml`：

```yaml
data:
  provider: yfinance
  cache_dir: ./data

backtest:
  default_capital: 10000
  commission: 0.001     # 每笔交易0.1%
  slippage: 0.0005      # 0.05%滑点

risk:
  max_position_size: 0.95
  stop_loss: null       # 可选固定止损
  take_profit: null     # 可选固定止盈
```

## 错误处理

参考 `{baseDir}/references/errors.md` 了解常见问题和解决方案。

## 示例

参考 `{baseDir}/references/examples.md` 了解详细使用示例，包括：
- 多资产比较
- 前瞻式分析
- 参数优化工作流

## 文件

| 文件 | 目的 |
|------|------|
| `scripts/backtest.py` | 主回测引擎 |
| `scripts/fetch_data.py` | 历史数据获取器 |
| `scripts/strategies.py` | 策略定义 |
| `scripts/metrics.py` | 性能计算 |
| `scripts/optimize.py` | 参数优化 |

## 资源

- [yfinance](https://github.com/ranaroussi/yfinance) - 洛基财经数据
- [TA-Lib](https://ta-lib.org/) - 技术分析库
- [QuantStats](https://github.com/ranaroussi/quantstats) - 投资组合分析
