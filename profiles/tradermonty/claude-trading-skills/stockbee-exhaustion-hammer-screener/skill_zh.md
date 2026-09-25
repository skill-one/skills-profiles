# Stockbee 极度疲软锤形筛子

筛选美股，寻找符合Stockbee风格的极度疲软锤形候选股。该技能是一个候选股生成和设置质量的工作流，而非信号服务或自动执行系统。

## 使用场景

- 用户需要筛选Stockbee / Pradeep Bonde风格的极度疲软设置
- 用户想要寻找接近收盘的锤形/长下影线反转候选股
- 用户想要扫描强流动性股票，这些股票回调后可能正在经历卖方极度疲软
- 用户想要在收盘前或收盘后寻找下穿/收复候选股
- 用户提供股票代码列表、宇宙文件或历史/临时OHLCV JSON文件用于筛选
- 用户希望候选股输出能用于`technical-analyst`、`position-sizer`、`trader-memory-core`或`stockbee-setup-fluency-trainer`

## 前置条件

- FMP API密钥用于实时宇宙和历史OHLCV筛选：
  ```bash
  export FMP_API_KEY=your_api_key_here
  ```
- 可选无API路径：提供`--prices-json`包含按股票代码的每日OHLCV柱状图。对于近收盘使用场景，最新柱状图应为在收盘附近捕获的临时当前日柱状图。
- 可选`--profiles-json`可添加质量元数据，如`marketCap`、`mutualFundHolders`、`institutionalHolders`或`institutionalOwnershipPct`。
- 仅在市场状态工作流允许新的摆动风险后运行，或标记输出为仅人工审核。

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

**模式C：离线/近收盘OHLCV JSON**
```bash
python3 skills/stockbee-exhaustion-hammer-screener/scripts/screen_exhaustion_hammer.py \
  --prices-json data/near_close_daily_ohlcv.json \
  --profiles-json data/quality_profiles.json \
  --market-gate allowed \
  --output-dir reports/
```

对于最佳努力FMP近收盘运行，使用报价覆盖。这会为每个股票增加一个额外的报价调用，取决于提供者的新鲜度：

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

- **卖方极度疲软锤形**：长下影线、小实体、强收盘位置，并从日内低点反弹
- **下穿/收复锤形**：当前低点低于短期低点，且近收盘价格收复该水平
- **前期动能回调**：近期高点在配置的回溯期内形成，随后是可控回调而非长期下跌趋势
- **高质量/流动性背景**：价格、成交量、20日均美元成交量、市值元数据和可选的持有人元数据

然后使用以下指标评分设置质量：

- 质量流动性
- 前期动能
- 回调和卖方极度疲软背景
- 锤形蜡烛形态
- 日内低点风险距离加缓冲
- 市场门状态对齐

### 第3步：审核输出

阅读生成的JSON和Markdown报告。对于每个候选股，呈现：

- 触发类型和所有匹配标签
- 从近期高点回撤深度和自高点以来的天数
- 下穿/收复状态和短期前期低点
- 锤形形态：下影线、实体、上影线、收盘位置、从低点反弹
- 成交量比率、平均美元成交量和质量元数据
- 入场参考、止损参考和止损风险百分比
- 设置评分、评级、状态和拒绝原因
- 建议的后续操作

### 第4步：将幸存者发送至交易规划

谨慎使用输出：

- **A/A-候选股**：手动验证图表，检查盈利/新闻风险，然后发送至`position-sizer`
- **B候选股**：人工审核或次日锤形高点确认
- **观察候选股**：加入观察列表/模型簿；等待跟进行动或更紧风险
- **拒绝候选股**：用于事后分析，不用于执行

## 输出

- `stockbee_exhaustion_hammer_YYYY-MM-DD_HHMMSS.json` - 结构化候选股列表、元数据、阈值、评分组件和拒绝项
- `stockbee_exhaustion_hammer_YYYY-MM-DD_HHMMSS.md` - 按评级/状态分组的可读报告

## 资源

- `references/exhaustion_hammer_methodology.md` - Stockbee风格方法摘要和实现边界
- `references/scoring_system.md` - 组件权重、状态阈值和失败过滤器
- `references/near_close_operations.md` - 近收盘操作清单和调度笔记
