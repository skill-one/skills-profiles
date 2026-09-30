---
name: stockbee-momentum-burst-screener
description: 为Stockbee风格的短期动量爆发形态筛选美国股市，使用4%突破、美元突破、区间扩展、成交量扩展、前期区间收缩、收盘位置、失败过滤和风险距离评分。当用户要求Stockbee、Pradeep Bonde、动量爆发、4%突破、区间扩展、美元突破、短期摆动动量候选或3-5天爆发形态回顾时使用。
---

# Stockbee 动量爆发筛选器

用于筛选美国股票市场中符合Stockbee风格的短期动量爆发候选股。该技能是一个候选股生成和设置质量的工作流，而非信号服务或自动执行系统。

## 使用场景

- 用户需要Stockbee / Pradeep Bonde风格的动量爆发筛选
- 用户需要4%突破、美元突破或区间扩展候选股
- 用户需要短期3-5天摆动动量设置
- 用户需要评估每日突破是否具有A/B/C设置质量
- 用户提供股票代码列表、宇宙文件或历史OHLCV JSON用于筛选
- 用户需要候选输出用于输入`technical-analyst`、`position-sizer`或`trader-memory-core`

## 前置条件

- FMP API密钥用于实时宇宙和历史OHLCV筛选：
  ```bash
  export FMP_API_KEY=your_api_key_here
  ```
- 可选无API路径：提供包含每日OHLCV柱状图的`--prices-json`
- 仅在市场状态工作流允许新的摆动风险后运行，或标记输出为仅人工审核

## 工作流

### 第1步：选择输入模式

使用以下三种模式之一：

**模式A：FMP宇宙扫描**
```bash
python3 skills/stockbee-momentum-burst-screener/scripts/screen_momentum_burst.py \
  --fmp-universe \
  --max-symbols 300 \
  --output-dir reports/
```

**模式B：显式股票代码**
```bash
python3 skills/stockbee-momentum-burst-screener/scripts/screen_momentum_burst.py \
  --symbols NVDA SMCI PLTR TSLA \
  --output-dir reports/
```

**模式C：离线OHLCV JSON**
```bash
python3 skills/stockbee-momentum-burst-screener/scripts/screen_momentum_burst.py \
  --prices-json data/daily_ohlcv.json \
  --output-dir reports/
```

### 第2步：运行筛选流程

脚本检测以下触发条件：

- **4%突破**：`close / previous_close >= 1.04`，成交量高于前一日，且成交量高于流动性门槛
- **美元突破**：`close - open >= 0.90`，成交量高于流动性门槛
- **区间扩展**：当日区间超过前三个日区间，且前一日未已扩展

然后使用以下指标评分设置质量：

- 触发强度
- 成交量扩展
- 前期基础/区间收缩质量
- 收盘价接近当日最高价
- 风险距离触发日低点
- 失败过滤条件，如前期3日上涨或近期4%下跌
- 市场状态匹配

### 第3步：审核输出

阅读生成的JSON和Markdown报告。对每个候选股，呈现：

- 触发类型和所有匹配的触发标签
- 当日涨幅、美元涨幅、成交量比和收盘位置百分比
- 前期基础长度和基础宽度
- 入场参考、止损参考和止损风险百分比
- 设置评分、评级、状态和拒绝原因
- 建议的下游操作

### 第4步：将幸存者发送至交易规划

谨慎使用输出：

- **A / A-候选股**：发送至`technical-analyst`进行人工图表验证，然后`position-sizer`
- **B候选股**：仅监控或小风险审核
- **仅监控候选股**：保留在模型簿中；除非图表审核升级设置，否则不规划交易
- **拒绝候选股**：用于事后分析，不用于执行

## 输出

- `stockbee_momentum_burst_YYYY-MM-DD_HHMMSS.json` - 结构化候选列表、元数据、阈值、评分组件和拒绝项
- `stockbee_momentum_burst_YYYY-MM-DD_HHMMSS.md` - 分组按评级/状态的易读报告

## 资源

- `references/momentum_burst_methodology.md` - Stockbee风格方法总结和实现边界
- `references/scoring_system.md` - 组件权重、状态阈值和失败过滤条件
- `references/entry_exit_rules.md` - 入场参考、止损、规模交接和退出模板
