# Stockbee 动量爆发筛选器

用于筛选美国股票的 Stockbee 风格短期动量爆发候选股。该技能是一个候选股生成和设置质量的工作流，而非信号服务或自动执行系统。

## 使用场景

- 用户请求 Stockbee / Pradeep Bonde 风格的动量爆发筛选
- 用户需要 4% 突破、美元突破或区间扩展候选股
- 用户请求短期 3-5 天的摆动动量设置
- 用户希望审查每日突破是否具有 A/B/C 设置质量
- 用户提供符号列表、宇宙文件或历史 OHLCV JSON 以供筛选
- 用户希望候选输出用于 `technical-analyst`、`position-sizer` 或 `trader-memory-core`

## 前置条件

- FMP API 密钥用于实时宇宙和历史 OHLCV 筛选：
  ```bash
  export FMP_API_KEY=your_api_key_here
  ```
- 可选无 API 路径：提供 `--prices-json` 包含按符号的每日 OHLCV 棒。
- 仅在市场状态工作流允许新的摆动风险后运行，或标记输出为仅手动审核。

## 工作流

### 第 1 步：选择输入模式

使用以下三种模式之一：

**模式 A：FMP 宇宙扫描**
```bash
python3 skills/stockbee-momentum-burst-screener/scripts/screen_momentum_burst.py \
  --fmp-universe \
  --max-symbols 300 \
  --output-dir reports/
```

**模式 B：显式符号**
```bash
python3 skills/stockbee-momentum-burst-screener/scripts/screen_momentum_burst.py \
  --symbols NVDA SMCI PLTR TSLA \
  --output-dir reports/
```

**模式 C：离线 OHLCV JSON**
```bash
python3 skills/stockbee-momentum-burst-screener/scripts/screen_momentum_burst.py \
  --prices-json data/daily_ohlcv.json \
  --output-dir reports/
```

### 第 2 步：运行筛选流程

脚本检测以下触发条件：

- **4% 突破**：`close / previous_close >= 1.04`，成交量高于前一日，且成交量高于流动性门槛
- **美元突破**：`close - open >= 0.90`，成交量高于流动性门槛
- **区间扩展**：当日区间超过前三个日区间，且前一日未已扩展

然后使用以下指标评分设置质量：

- 触发强度
- 成交量扩展
- 前期基础/区间收缩质量
- 收盘价接近当日最高价
- 风险距离触发日低点
- 失败过滤条件，如前期 3 天上涨或近期 4% 下跌
- 市场门限对齐

### 第 3 步：审核输出

阅读生成的 JSON 和 Markdown 报告。对于每个候选股，呈现：

- 触发类型和所有匹配的触发标签
- 当日涨幅、美元涨幅、成交量比和收盘价位置百分比
- 前期基础长度和基础宽度
- 入场参考、止损参考和止损风险百分比
- 设置分数、评级、状态和拒绝原因
- 建议的下游操作

### 第 4 步：将幸存者发送至交易规划

谨慎使用输出：

- **A / A- 候选股**：发送至 `technical-analyst` 进行手动图表验证，然后 `position-sizer`
- **B 候选股**：仅监控或小风险审核
- **仅监控候选股**：保留在模型簿中；除非图表审核升级设置，否则不规划交易
- **拒绝候选股**：保留用于事后分析，不用于执行

## 输出

- `stockbee_momentum_burst_YYYY-MM-DD_HHMMSS.json` - 结构化候选列表、元数据、阈值、分数组件和拒绝项
- `stockbee_momentum_burst_YYYY-MM-DD_HHMMSS.md` - 分组按评级/状态的易读报告

## 资源

- `references/momentum_burst_methodology.md` - Stockbee 风格方法摘要和实现边界
- `references/scoring_system.md` - 组件权重、状态阈值和失败过滤条件
- `references/entry_exit_rules.md` - 入场参考、止损、规模交接和退出模板
