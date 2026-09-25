# PEAD Screener - 盈后公告漂移效应

使用周K线分析筛选盈后公告漂移效应（PEAD）的股票，检测红色K线回调和突破信号。

## 使用场景

- 用户请求PEAD筛选或盈后漂移效应分析
- 用户希望找到具有持续上涨潜力的盈后跳空上涨股票
- 用户请求盈后红色K线突破模式
- 用户询问周度盈后动量布局
- 用户提供盈后交易分析器JSON输出以进行进一步筛选

## 前置条件

- FMP API密钥（设置`FMP_API_KEY`环境变量或传递`--api-key`）
  ```bash
  export FMP_API_KEY=your_api_key_here
  ```
- 免费套餐（每天250次调用）足以满足默认筛选需求
- 对于模式B：具有`schema_version "1.0"`的盈后交易分析器JSON输出文件

## 工作流程

### 第1步：准备和执行筛选

以两种模式之一运行PEAD筛选器脚本：

**模式A（FMP盈后日历）：**
```bash
# 默认：最近14天的盈后数据，5周监控窗口
python3 skills/pead-screener/scripts/screen_pead.py --output-dir reports/

# 自定义参数
python3 skills/pead-screener/scripts/screen_pead.py \
  --lookback-days 21 \
  --watch-weeks 6 \
  --min-gap 5.0 \
  --min-market-cap 1000000000 \
  --output-dir reports/
```

**模式B（盈后交易分析器JSON输入）：**
```bash
# 从盈后交易分析器输出
python3 skills/pead-screener/scripts/screen_pead.py \
  --candidates-json reports/earnings_trade_analyzer_YYYY-MM-DD_HHMMSS.json \
  --min-grade B \
  --output-dir reports/
```

**美国股票定时任务陷阱：** 优先选择模式B进行盈后/美国股票定时简报，前提是已运行`earnings-trade-analyzer`。模式A会拉取全球FMP盈后日历，将API预算消耗在非美国股票上，并在到达目标美国观察列表之前返回较弱的/非可操作的国外上市股票。如果无论如何使用模式A，且脚本报告预算削减或非美国股票，请将PEAD输出标记为降级，并将其视为仅手动审核，而不是干净的候选源。

### 第2步：审核结果

1. 阅读生成的JSON和Markdown报告
2. 加载`references/pead_strategy.md`以了解PEAD理论和模式背景
3. 加载`references/entry_exit_rules.md`以了解交易管理规则

### 第3步：呈现分析

针对每个候选股票，呈现：
- 阶段分类（MONITORING、SIGNAL_READY、BREAKOUT、EXPIRED）
- 周K线模式详情（红色K线位置、突破状态）
- 综合评分和评级
- 交易布局：入场点、止损点、目标价、风险/收益比
- 流动性指标（ADV20、平均成交量）

### 第4步：提供可操作的指导

根据阶段和评级：
- **BREAKOUT + 强势布局（85+）：** 高置信度PEAD交易，满仓位
- **BREAKOUT + 良好布局（70-84）：** 稳健的PEAD布局，标准仓位
- **SIGNAL_READY：** 形成红色K线，设置突破红色K线高位的警报
- **MONITORING：** 盈后阶段，尚未形成红色K线，加入观察列表
- **EXPIRED：** 超出监控窗口，从观察列表移除

## 输出

- `pead_screener_YYYY-MM-DD_HHMMSS.json` - 带阶段分类的结构化结果
- `pead_screener_YYYY-MM-DD_HHMMSS.md` - 分阶段组织的可读报告

### 盈后时间未知

FMP不会为每条盈后记录确认bmo/amc会议；未确认的记录在模式A中带有`earnings_timing: "unknown"`，价格跳空计算假设AMC窗口作为后备。模式A报告显示`timing_unknown_count`（`timing_candidates_total`），因此这种假设保持可见（模式B报告`n/a`，因为时间继承自输入JSON）。`timing_candidates_total`是预算削减后实际分析的盈后日历行数，而不是原始盈后日历行数。

## 资源

- `references/pead_strategy.md` - PEAD理论和周K线方法
- `references/entry_exit_rules.md` - 入场、离场和仓位调整规则
