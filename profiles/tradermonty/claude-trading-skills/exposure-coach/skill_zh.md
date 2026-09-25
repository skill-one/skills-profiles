# 暴露指导教练

## 概述

暴露指导教练整合市场广度分析器、上升趋势分析器、宏观环境检测器、市场顶部检测器、期货交易检测器、主题检测器、行业分析师和机构资金流向追踪器的输出，形成统一的控制平面决策。该技能在开始任何个股分析之前，回答独立交易者的核心问题："我现在应该投入多少资金到股票市场？"

## 使用场景

- 在建立任何新股票头寸前确定适当的资金投入
- 每个交易周开始时校准投资组合暴露度
- 当多个市场信号冲突需要统一立场时
- 在重大宏观或市场事件后重新评估暴露上限
- 在市场环境转换期间（扩散、集中、收缩）

## 前置条件

- Python 3.9+
- FMP API密钥（设置`FMP_API_KEY`环境变量）用于机构资金流向追踪数据
- 来自上游技能的输入JSON文件（见工作流步骤1）
- 标准库 + `argparse`, `json`, `datetime`

## 工作流

### 步骤1：收集上游技能输出

收集集成技能的最新JSON输出。每个文件提供特定的信号维度：

| 技能 | 输出文件模式 | 提供的信号 |
|------|--------------|-----------|
| market-breadth-analyzer | `breadth_*.json` | 涨跌比率、新高/新低 |
| uptrend-analyzer | `uptrend_*.json` | 上升趋势参与百分比 |
| macro-regime-detector | `regime_*.json` | 当前环境（集中、扩散等） |
| market-top-detector | `top_risk_*.json` | 分配天数、最高概率分数 |
| ftd-detector | `ftd_*.json` | 跟进日质量（市场底部确认） |
| theme-detector | `theme_detector_*.json` 或 `theme_*.json` | 活跃投资主题和轮动 |
| sector-analyst | `sector_*.json` | 行业表现排名 |
| institutional-flow-tracker | `institutional_*.json` | 净机构买入/卖出 |

### 步骤2：运行暴露评分引擎

执行暴露评分脚本，指定上游输出路径：

```bash
python3 skills/exposure-coach/scripts/calculate_exposure.py \
  --breadth reports/breadth_latest.json \
  --uptrend reports/uptrend_latest.json \
  --regime reports/regime_latest.json \
  --top-risk reports/top_risk_latest.json \
  --ftd reports/ftd_latest.json \
  --theme reports/theme_latest.json \
  --sector reports/sector_latest.json \
  --institutional reports/institutional_latest.json \
  --output-dir reports/
```

脚本接受部分输入；缺失文件会降低置信度但不会阻止执行。

规范化的宏观环境报告必须包含嵌套的`regime.confidence`和`composite.data_quality`，其中包含有效的整数组件计数。缺失或格式错误的可用性元数据、`very_low`置信度和零可用组件被视为缺失关键输入。它们不会贡献环境评分或偏差，并且正常缺失输入的扣减和置信度上限适用。永远不要通过手动将报告的环境标签复制到暴露决策中而覆盖这种退化。

**验证陷阱：** 每次运行后，检查生成的JSON字段`inputs_provided`和`inputs_missing`。如果你在CLI中传递的文件仍然出现在`inputs_missing`中（例如一个主题检测器JSON，暴露引擎未识别），将受影响的维度标记为退化，并保持置信度上限；不要假设提供的输入被纳入，仅仅因为CLI参数存在。

**主题检测器摄入注意事项：** 主题检测器通常发出`theme_detector_YYYY-MM-DD_HHMMSS.json`，其中包含`themes`对象。如果该文件未被`calculate_exposure.py`识别，并且`theme`仍然在`inputs_missing`中，不要手动将主题强度纳入暴露上限。相反，保持暴露指导教练的置信度上限，声明主题维度未被纳入，并在更广泛的交易简报中分别总结主题/行业发现。

### 步骤3：解读市场立场摘要

审查生成的立场报告，其中包含：

1. **暴露上限** -- 推荐的最大股票配置比例（0-100%）
2. **偏差方向** -- 基于环境和资金流向的增长/价值倾斜
3. **参与评估** -- 广泛（健康）与狭窄（脆弱）市场
4. **行动建议** -- NEW_ENTRY_ALLOWED, REDUCE_ONLY 或 CASH_PRIORITY
5. **置信度水平** -- 基于输入完整性的HIGH, MEDIUM 或 LOW

### 步骤4：应用暴露指导

将立场建议映射到投资组合操作：

| 建议 | 操作 |
|------|------|
| NEW_ENTRY_ALLOWED | 继续进行股票级分析和新头寸 |
| REDUCE_ONLY | 无新入场；根据强势削减现有头寸 |
| CASH_PRIORITY | 积极筹集现金；避免所有新承诺 |

## 输出格式

### JSON报告

```json
{
  "schema_version": "1.0",
  "generated_at": "2026-03-16T07:00:00Z",
  "exposure_ceiling_pct": 70,
  "bias": "GROWTH",
  "participation": "BROAD",
  "recommendation": "NEW_ENTRY_ALLOWED",
  "confidence": "HIGH",
  "component_scores": {
    "breadth_score": 65,
    "uptrend_score": 72,
    "regime_score": 80,
    "top_risk_score": 25,
    "ftd_score": 10,
    "theme_score": 68,
    "sector_score": 70,
    "institutional_score": 75
  },
  "inputs_provided": ["breadth", "uptrend", "regime", "top_risk"],
  "inputs_missing": ["ftd", "theme", "sector", "institutional"],
  "rationale": "广泛参与与低顶部风险支持提高暴露水平。"
}
```

### Markdown报告

Markdown报告提供一页摘要，适合快速审查：

```markdown
# 市场立场摘要
**日期：** 2026-03-16 | **置信度：** HIGH

## 暴露上限：70%

| 维度 | 分数 | 状态 |
|------|------|------|
| 广度 | 65 | 健康 |
| 上升趋势参与 | 72% | 广泛 |
| 环境 | 扩散 | 有利 |
| 顶部风险 | 25 | 低 |

## 建议：NEW_ENTRY_ALLOWED

**偏差：** 增长 > 价值
**参与：** 广泛（健康内部）

### 理由
广泛参与与低分配天数支持提高股票暴露。
允许在70%上限内建立新头寸。

报告保存在`reports/`目录下，文件名`exposure_posture_YYYY-MM-DD_HHMMSS.{json,md}`。

## 资源

- `scripts/calculate_exposure.py` -- 主要协调器，用于评分和整合输入
- `references/exposure_framework.md` -- 评分规则和阈值定义
- `references/regime_exposure_map.md` -- 环境到暴露上限映射

## 关键原则

1. **安全优先** -- 输入不完整或冲突时默认较低暴露
2. **环境对齐** -- 让宏观环境设定基准；广度在范围内调整
3. **可操作输出** -- 始终提供明确建议，而不仅仅是数据聚合
