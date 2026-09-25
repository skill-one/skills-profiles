# 边缘策略设计器

## 概述

将概念层面的假设转化为具体的策略草稿规格。
该技能位于概念合成之后，管道导出验证之前。

## 使用场景

- 您拥有 `edge_concepts.yaml` 并需要策略候选方案。
- 您希望每个概念生成多个变体（核心/保守/研究探测）。
- 您希望为接口 v1 家族生成可选的导出文件。

## 前置条件

- Python 3.9+
- `PyYAML`
- 由概念合成生成的 `edge_concepts.yaml`

## 输出

- `strategy_drafts/*.yaml`
- `strategy_drafts/run_manifest.json`
- 可选的 `exportable_tickets/*.yaml`，用于下游 `export_candidate.py`

## 工作流程

1. 加载 `edge_concepts.yaml`。
2. 选择风险配置（`conservative`、`balanced`、`aggressive`）。
3. 生成每个概念的变体，并进行假设类型退出校准。
4. 应用 `HYPOTHESIS_EXIT_OVERRIDES` 调整每个假设类型的止损、风险回报率、时间止损和跟踪止损（如突破、收益漂移、恐慌反转等）。
5. 将风险回报率钳制在 `RR_FLOOR=1.5` 以防止 C5 审核失败。
6. 在适用情况下导出 v1 准备好的票证 YAML。
7. 将可导出的票证交接给 `skills/edge-candidate-agent/scripts/export_candidate.py`。

## 快速命令

仅生成草稿：

```bash
python3 skills/edge-strategy-designer/scripts/design_strategy_drafts.py \
  --concepts /tmp/edge-concepts/edge_concepts.yaml \
  --output-dir /tmp/strategy-drafts \
  --risk-profile balanced
```

生成草稿 + 可导出票证：

```bash
python3 skills/edge-strategy-designer/scripts/design_strategy_drafts.py \
  --concepts /tmp/edge-concepts/edge_concepts.yaml \
  --output-dir /tmp/strategy-drafts \
  --exportable-tickets-dir /tmp/exportable-tickets \
  --risk-profile conservative
```

## 资源

- `skills/edge-strategy-designer/scripts/design_strategy_drafts.py`
- `references/strategy_draft_schema.md`
- `skills/edge-candidate-agent/scripts/export_candidate.py`
