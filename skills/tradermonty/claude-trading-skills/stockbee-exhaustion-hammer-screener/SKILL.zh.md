---
name: stockbee-exhaustion-hammer-screener
description: 为Stockbee风格的卖出竭尽锤形形态筛选美国股市，需结合前期动能、回调深度、下探/回补、长下影线几何形态、收盘位置、成交量确认、质/流动性门槛以及风险距离评分。当用户要求Stockbee、Pradeep Bonde、竭尽形态、卖出竭尽、锤形反转、下探回补、近收盘反转候选或高质量基金控股股票的回调入场时使用。
---

# Stockbee 极度疲软锤形筛子

筛选美股，寻找符合Stockbee风格的极度疲软锤形候选股。这项技能是一个候选股生成和设置质量的工作流，而不是一个信号服务或自动执行系统。

## 使用场景

- 用户请求筛选Stockbee / Pradeep Bonde风格的极度疲软设置
- 用户想要寻找接近收盘的锤形/长下影线反转候选股
- 用户想要扫描强劲、流动的股票，这些股票回调后可能正在经历极度疲软
- 用户想要在收盘前或收盘后寻找下穿/收复候选股
- 用户提供股票代码列表、宇宙文件或历史/临时OHLCV JSON用于筛选
- 用户想要将候选股输出结果输入到`technical-analyst`、`position-sizer`、`trader-memory-core`或`stockbee-setup-fluency-trainer`

## 前置条件

- FMP API密钥用于实时宇宙和历史OHLCV筛选：
  ```bash
  export FMP_API_KEY=your_api_key_here
  ```
- 可选的无API路径：提供`--prices-json`，其中包含按股票代码的每日OHLCV柱状图。对于预期的接近收盘的使用场景，最新柱状图应该是接近收盘时捕获的临时当前日柱状图。
- 可选的`--profiles-json`可以添加质量元数据，例如`marketCap`、`mutualFundHolders`、`institutionalHolders`或`institutionalOwnershipPct`。
- 仅在市场状态工作流允许新的摆动风险后运行，或将输出标记为仅手动审核。

## 工作流

### 第1步：选择输入模式

使用以下三种模式之一：

**模式A：FMP宇宙扫描**
```bash
python3 skills/stockbee-exhaustion-hammer-screener/scripts/screen_exhaustion_hammer.py \
  --fmp-universe \
  --max-symbols 300 \
  --market-gate allowed \
  --output-dir reports/
```

**模式B：显式股票代码**
```bash
python3 skills/stockbee-exhaustion-hammer-screener/scripts/screen_exhaustion_hammer.py \
  --symbols APP ENPH NVDA TSLA \
  --market-gate allowed \
  --output-dir reports/
```

**模式C：离线/接近收盘的OHLCV JSON**
```bash
python3 skills/stockbee-exhaustion-hammer-screener/scripts/screen_exhaustion_hammer.py \
  --prices-json data/near_close_daily_ohlcv.json \
  --profiles-json data/quality_profiles.json \
  --market-gate allowed \
  --output-dir reports/
```

对于最佳努力FMP接近收盘运行，使用报价覆盖。这会为每个股票增加一个额外的报价调用，并且取决于提供者的新鲜度：

```bash
python3 skills/stockbee-exhaustion-hammer-screener/scripts/screen_exhaustion_hammer.py \
  --fmp-universe \
  --use-quote-latest \
  --max-api-calls 700 \
  --market-gate allowed \
  --output-dir reports/
```

### 第2步：运行筛选过程

脚本检测以下设置类型：

- **极度疲软锤形**：长下影线、小实体、强劲收盘位置，并从日内低点反弹
- **下穿/收复锤形**：当前低点低于短期低点，且接近收盘价收复该水平
- **前期动能回调**：近期高点在配置的回溯期内形成，随后是受控回调而不是长期下跌趋势
- **高质量/流动性背景**：价格、成交量、20日均美元成交量、市值元数据和可选的持有人元数据

然后使用以下指标评分设置质量：

- 质量流动性
- 前期动能
- 回调和极度疲软背景
- 锤形蜡烛几何形状
- 到日内低点的风险距离加缓冲
- 市场门状态对齐

### 第3步：审核输出

阅读生成的JSON和Markdown报告。对于每个候选股，呈现：

- 触发类型和所有匹配的标签
- 从近期高点回撤的深度和自高点以来的天数
- 下穿/收复状态和短期前期低点
- 锤形几何形状：下影线、实体、上影线、收盘位置、从低点反弹
- 成交量比率、平均美元成交量和质量元数据
- 入场参考、止损参考和到止损的风险百分比
- 设置分数、评级、状态和拒绝原因
- 建议的下游操作

### 第4步：将幸存者发送到交易规划

谨慎使用输出：

- **A / A- 候选股**：手动验证图表，检查盈利/新闻风险，然后发送到`position-sizer`
- **B 候选股**：手动审核或次日锤形高点确认
- **观察候选股**：加入观察列表/模型簿；等待后续确认或更严格的风险
- **拒绝的候选股**：保留用于事后分析，不用于执行

## 输出

- `stockbee_exhaustion_hammer_YYYY-MM-DD_HHMMSS.json` - 结构化候选股列表、元数据、阈值、分数组件和拒绝项
- `stockbee_exhaustion_hammer_YYYY-MM-DD_HHMMSS.md` - 按评级/状态分组的可读报告

## 资源

- `references/exhaustion_hammer_methodology.md` - Stockbee风格方法摘要和实现边界
- `references/scoring_system.md` - 组件权重、状态阈值和失败过滤器
- `references/near_close_operations.md` - 接近收盘操作清单和调度笔记
