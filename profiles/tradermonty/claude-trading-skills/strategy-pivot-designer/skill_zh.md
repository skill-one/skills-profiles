# 策略转向设计师

## 概述

检测策略回测迭代循环何时停滞，并提出结构上不同的策略架构。这项技能作为 Edge 管道的反馈循环（提示提取器 -> 概念综合器 -> 策略设计师 -> 候选代理），通过重新设计策略的骨架而非调整参数来跳出局部最优。

## 使用场景

- 尽管经过多次优化迭代，回测分数仍停滞不前。
- 策略显示出过拟合迹象（样本内表现高，鲁棒性低）。
- 交易成本抵消了策略的微弱优势。
- 尾部风险或回撤超过可接受阈值。
- 你希望为同一市场假设探索根本不同的策略架构。

## 前置条件

- Python 3.9+
- `PyYAML`
- 迭代历史 JSON（累积的回测专家评估）
- 源策略草稿 YAML（来自 edge-strategy-designer）

## 输出

- `pivot_drafts/research_only/*.yaml` — 兼容策略草稿的 YAML 提案
- `pivot_drafts/exportable/*.yaml` — 可导出的草稿 + 候选代理的票证 YAML
- `pivot_report_*.md` — 人类可读的转向分析
- `pivot_manifest_*.json` — 所有生成文件元数据
- `pivot_diagnosis_*.json` — 停滞检测结果

## 工作流程

1. 使用 `--append-eval` 将回测评估结果累积到迭代历史文件中。
2. 对历史运行停滞检测以识别触发器（平台期、过拟合、成本抵消、尾部风险）。
3. 如果检测到停滞，使用三种技术生成转向提案：假设反转、原型切换、目标重构。
4. 审阅按质量潜力+新颖性评分的提案排名。
5. 对于可导出提案，票证 YAML 已准备好供 edge-candidate-agent 管道使用。
6. 对于 research_only 提案，在管道集成前需要手动策略设计。
7. 将选定的转向草稿反馈回回测专家进行下一迭代循环。

## 快速命令

向历史中追加回测评估（新创建历史）：

```bash
python3 skills/strategy-pivot-designer/scripts/detect_stagnation.py \
  --append-eval reports/backtest_eval_2026-02-10_120000.json \
  --history reports/iteration_history.json \
  --strategy-id draft_edge_concept_breakout_behavior_riskon_core \
  --changes "将止损从 5% 扩展到 7%"
```

检测停滞：

```bash
python3 skills/strategy-pivot-designer/scripts/detect_stagnation.py \
  --history reports/iteration_history.json \
  --output-dir reports/
```

生成转向提案：

```bash
python3 skills/strategy-pivot-designer/scripts/generate_pivots.py \
  --diagnosis reports/pivot_diagnosis_*.json \
  --strategy reports/edge_strategy_drafts/draft_*.yaml \
  --max-pivots 3 \
  --output-dir reports/
```

## 资源

- `skills/strategy-pivot-designer/scripts/detect_stagnation.py`
- `skills/strategy-pivot-designer/scripts/generate_pivots.py`
- `references/stagnation_triggers.md`
- `references/strategy_archetypes.md`
- `references/pivot_techniques.md`
- `references/pivot_proposal_schema.md`
- `skills/backtest-expert/scripts/evaluate_backtest.py`
- `skills/edge-strategy-designer/scripts/design_strategy_drafts.py`
