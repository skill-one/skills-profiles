# Stockbee 分段枢轴分析器

使用 **催化剂质量** 和 **价格/成交量确认** 对第一天分段枢轴 (EP) 候选进行分类。该技能是一个候选质量分析器，而不是执行引擎。

## 使用场景

- 用户需要 Pradeep Bonde / Stockbee 风格的 EP 候选
- 用户提供了盈利、指引、并购、FDA、分析师、合同、产品、空头挤压或主题/新闻事件
- 用户需要将 `ACTIONABLE_DAY1` 候选与 `DELAYED_EP_WATCH` 名称区分开
- 用户需要将强劲的盈利/指引 EP 交给 `pead-screener`
- 用户需要将催化剂分析与 `stockbee-momentum-burst-screener` 的价格/成交量输出相结合

## 前置条件

- Python 3.10+
- 可选：FMP API 密钥用于 OHLCV/概况增强
- 以下之一：
  - 催化剂/事件 JSON
  - `earnings-trade-analyzer` JSON 输出
  - 催化剂 JSON 加上 `stockbee-momentum-burst-screener` JSON 增强输出
- 此技能本身不获取或发现新闻。如果未提供催化剂，请使用用户偏好的新闻或研究流程首先收集事件/新闻背景。

## 工作流程

### 第 1 步：准备候选输入

使用以下一种或多种输入模式。

**模式 A — 催化剂/事件 JSON：**

```json
{
  "events": [
    {
      "symbol": "ABC",
      "event_date": "2026-04-25",
      "catalyst_type": "guidance_raise",
      "headline": "ABC 在创纪录的需求后提高年度指引",
      "summary": "管理层提高了收入和 EPS 指引。"
    }
  ]
}
```

**模式 B — 盈利管道：**

使用 `earnings-trade-analyzer` 生成的 JSON。

**模式 C — 价格/成交量增强：**

传递一个 `stockbee-momentum-burst-screener` JSON 报告以重用日涨幅、成交量、收盘位置和风险距离字段。

### 第 2 步：运行分析器

```bash
# 催化剂 JSON + 离线 OHLCV
python3 skills/stockbee-episodic-pivot-analyzer/scripts/analyze_ep.py \
  --events-json data/catalysts.json \
  --prices-json data/daily_ohlcv.json \
  --output-dir reports/

# 盈利管道输入
python3 skills/stockbee-episodic-pivot-analyzer/scripts/analyze_ep.py \
  --earnings-json reports/earnings_trade_analyzer_YYYY-MM-DD_HHMMSS.json \
  --output-dir reports/

# 催化剂 JSON + Stockbee 动量增强
python3 skills/stockbee-episodic-pivot-analyzer/scripts/analyze_ep.py \
  --events-json data/catalysts.json \
  --momentum-json reports/stockbee_momentum_burst_YYYY-MM-DD_HHMMSS.json \
  --output-dir reports/
```

可选 FMP 增强输出：

```bash
export FMP_API_KEY=your_key
python3 skills/stockbee-episodic-pivot-analyzer/scripts/analyze_ep.py \
  --events-json data/catalysts.json \
  --max-api-calls 200 \
  --output-dir reports/
```

### 第 3 步：查看输出

针对每个候选，呈现：

- `state`：`ACTIONABLE_DAY1`、`DAY1_WATCH`、`DELAYED_EP_WATCH`、`CATALYST_WATCH` 或 `REJECT`
- `ep_type`：`EARNINGS_EP`、`GUIDANCE_EP`、`FDA_EP`、`M_AND_A_EP`、`STORY_EP` 等
- 催化剂质量评分和原因
- 价格/范围扩展、成交量冲击和收盘位置质量
- EP 日低点的风险
- `pead_handoff` 和 `delayed_ep_watch` 标志

### 第 4 步：交接规则

- `ACTIONABLE_DAY1`：在做出任何交易决策前发送给 `technical-analyst` 和 `position-sizer`
- `DAY1_WATCH`：保留在日内/次日观察列表中；需要图表确认
- `DELAYED_EP_WATCH`：不要追逐第一天；监控可控回调或新区间
- `CATALYST_WATCH`：催化剂可能很重要，但价格/成交量确认尚不充分
- `REJECT`：不要从该候选源进行交易
- 具有默认为 `pead_handoff=true` 的盈利/指引 EP 可以发送给 `pead-screener` 进行每周红烛/延迟反应监控

## 输出

- `stockbee_episodic_pivot_YYYY-MM-DD_HHMMSS.json` — 结构化 EP 评分报告
- `stockbee_episodic_pivot_YYYY-MM-DD_HHMMSS.md` — 人类可读的候选报告

## 资源

- `references/ep_methodology.md` — Stockbee EP 解释和设置分类法
- `references/catalyst_quality.md` — 催化剂分类和质量评分
- `references/handoff_rules.md` — 下游工作流交接和审查规则
