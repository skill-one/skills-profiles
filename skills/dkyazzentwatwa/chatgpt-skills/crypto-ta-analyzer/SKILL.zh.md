---
name: crypto-ta-analyzer
description: 对加密货币或市场 OHLCV 数据进行多指标技术分析。用于确定性趋势、动量、成交量和背离分析。
---

# 加密货币技术分析工具

当用户需要明确的技术分析而非叙述性市场观点时，使用捆绑的指标。

## 工作流程

1. 首先获取标准化OHLCV数据。
2. 当源格式需要重塑时，使用`scripts/data_converter.py`或`scripts/coingecko_converter.py`。
3. 运行`scripts/ta_analyzer.py`进行实际指标堆栈和信号评分。
4. 解释指标一致性、冲突和状态敏感性，而不是在没有上下文的情况下呈现一个数字。

## 安全约束

- 不要将信号呈现为必然结果。
- 明确区分确定性指标输出和自由裁量解释。
