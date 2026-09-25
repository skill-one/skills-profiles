# 信号事后分析

## 概述

信号事后分析记录和分析由边缘管道、筛选器和其它技能生成的交易信号结果。它将预测的边缘方向与5天和20天的实际回报进行比较，对结果进行分类（真阳性、假阳性、错失机会、状态不匹配），并为边缘信号聚合器权重调整和技能改进待办事项生成反馈。

## 使用场景

- 交易关闭后，需要记录结果
- 审查已达到持有期（5天或20天）的一批信号
- 识别特定技能的系统性假阳性模式
- 为边缘信号聚合器权重校准生成反馈
- 根据决策质量指标构建技能改进待办事项
- 定期（每周/每月）进行信号质量审计

## 前置条件

- Python 3.9+
- FMP API密钥（可选，用于获取实际回报，如未手动提供）
- 标准库 + `requests`用于API调用
- 输入：JSON格式的信号记录（来自边缘信号聚合器或筛选器输出）

### API密钥设置（可选）

如果您想自动获取用于回报计算的价格数据，请设置FMP API密钥：

```bash
export FMP_API_KEY=your_api_key_here
```

或者，通过命令行传递密钥，使用`--api-key YOUR_KEY`。没有API密钥时，您仍然可以通过提供`--exit-price`和`--exit-date`手动记录结果。

## 工作流程

### 第1步：准备信号记录

收集已关闭或成熟的信号记录。每条记录应包括：
- `signal_id`：唯一标识符
- `ticker`：股票代码
- `signal_date`：信号生成日期
- `predicted_direction`：LONG或SHORT
- `source_skill`：生成信号的技能
- `entry_price`：信号生成时的价格（可选，用于手动覆盖）

```bash
# 示例：列出准备进行事后分析的信号（5天以上）
python3 skills/signal-postmortem/scripts/postmortem_recorder.py \
  --list-ready \
  --signals-dir state/signals/ \
  --min-days 5
```

### 第2步：记录结果

运行事后分析记录器以获取实际回报并分类结果。

```bash
python3 skills/signal-postmortem/scripts/postmortem_recorder.py \
  --signals-file state/signals/aggregated_signals_2026-03-10.json \
  --holding-periods 5,20 \
  --output-dir reports/
```

对于手动结果记录（当价格数据已可用时）：

```bash
python3 skills/signal-postmortem/scripts/postmortem_recorder.py \
  --signal-id sig_aapl_20260310_abc \
  --exit-price 178.50 \
  --exit-date 2026-03-15 \
  --outcome-notes "在目标价位关闭，5天内上涨3.2%" \
  --output-dir reports/
```

### 第3步：分类结果

记录器自动将每条信号分类为以下四类之一：

| 分类 | 定义 |
|------|------|
| 真阳性 | 预测方向与实际回报符号一致 |
| 假阳性 | 预测方向与实际回报相反 |
| 错失机会 | 信号未被执行但本应是盈利的 |
| 状态不匹配 | 信号因市场状态变化而失败 |

分类规则在`references/outcome-classification.md`中记录。

### 第4步：生成反馈文件

为下游消费者生成反馈：

```bash
# 生成边缘信号聚合器权重调整建议
python3 skills/signal-postmortem/scripts/postmortem_analyzer.py \
  --postmortems-dir reports/postmortems/ \
  --generate-weight-feedback \
  --output-dir reports/

# 生成技能改进待办事项
python3 skills/signal-postmortem/scripts/postmortem_analyzer.py \
  --postmortems-dir reports/postmortems/ \
  --generate-improvement-backlog \
  --output-dir reports/
```

### 第5步：审查汇总统计

按技能、股票代码和时间周期生成汇总统计：

```bash
python3 skills/signal-postmortem/scripts/postmortem_analyzer.py \
  --postmortems-dir reports/postmortems/ \
  --summary \
  --group-by skill,month \
  --output-dir reports/
```

## 输出格式

### 事后分析记录（JSON）

```json
{
  "schema_version": "1.0",
  "postmortem_id": "pm_sig_aapl_20260310_abc",
  "signal_id": "sig_aapl_20260310_abc",
  "ticker": "AAPL",
  "signal_date": "2026-03-10",
  "source_skill": "edge-signal-aggregator",
  "predicted_direction": "LONG",
  "entry_price": 172.50,
  "realized_returns": {
    "5d": 0.032,
    "20d": 0.058
  },
  "exit_price": 178.50,
  "exit_date": "2026-03-15",
  "holding_days": 5,
  "outcome_category": "TRUE_POSITIVE",
  "regime_at_signal": "RISK_ON",
  "regime_at_exit": "RISK_ON",
  "outcome_notes": "干净突破，持有一路小回调",
  "recorded_at": "2026-03-17T10:30:00Z"
}
```

### 权重反馈（JSON）

```json
{
  "schema_version": "1.0",
  "generated_at": "2026-03-17T10:35:00Z",
  "analysis_period": {
    "from": "2026-02-01",
    "to": "2026-03-15"
  },
  "skill_adjustments": [
    {
      "skill": "vcp-screener",
      "current_weight": 1.0,
      "suggested_weight": 0.85,
      "reason": "RISK_OFF状态下15%的假阳性率",
      "sample_size": 42
    }
  ],
  "confidence": "MEDIUM",
  "min_sample_threshold": 20
}
```

### 技能改进待办事项（YAML）

```yaml
- skill: vcp-screener
  issue_type: false_positive_cluster
  severity: medium
  evidence:
    false_positive_rate: 0.15
    sample_size: 42
    regime_correlation: RISK_OFF
  suggested_action: "添加状态过滤器或减少RISK_OFF状态下的信号置信度"
  generated_by: signal-postmortem
  generated_at: "2026-03-17T10:35:00Z"
```

### 汇总报告（Markdown）

报告保存在`reports/`目录下，文件名格式为`postmortem_summary_YYYY-MM-DD.md`。

## 资源

- `scripts/postmortem_recorder.py` -- 记录单个信号结果
- `scripts/postmortem_analyzer.py` -- 生成反馈和汇总统计
- `references/outcome-classification.md` -- 分类规则和边缘情况
- `references/feedback-integration.md` -- 如何将反馈与下游技能整合

## 关键原则

1. **诚实归因** -- 每个结果都归因于其源技能以实现问责
2. **状态意识** -- 记录状态上下文以区分技能失败与市场状态变化
3. **最小样本量** -- 权重调整需要20+信号以验证统计有效性
4. **反馈闭环** -- 结果回流以改进信号聚合和技能质量
