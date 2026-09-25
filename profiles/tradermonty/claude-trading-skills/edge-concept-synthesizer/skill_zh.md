# 边缘概念合成器

## 概述

在检测与策略实现之间创建一个抽象层。
这项技能聚合工单证据，总结重复条件，并输出带有明确论点和无效化逻辑的 `edge_concepts.yaml` 文件。

## 使用场景

- 您有许多原始工单，需要机制层面的结构。
- 您希望避免工单到策略的直接过拟合。
- 您需要在策略制定前进行概念层面的评审。

## 前置条件

- Python 3.9+
- `PyYAML`
- 检测器输出的工单 YAML 目录 (`tickets/exportable`, `tickets/research_only`)
- 可选的 `hints.yaml`

## 输出

- `edge_concepts.yaml` 文件，包含：
  - 概念簇
  - 支持统计
  - 抽象论点
  - 无效化信号
  - 导出准备标志

## 工作流程

1. 从自动检测输出中收集工单 YAML 文件。
2. 可选地提供 `hints.yaml` 以进行上下文匹配。
3. 运行 `scripts/synthesize_edge_concepts.py`。
4. 去重概念：合并具有相同假设且条件重叠的概念（包含度 > 阈值）。
5. 评审概念，仅将高支持度的概念推进策略制定。

## 快速命令

```bash
python3 skills/edge-concept-synthesizer/scripts/synthesize_edge_concepts.py \
  --tickets-dir /tmp/edge-auto/tickets \
  --hints /tmp/edge-hints/hints.yaml \
  --output /tmp/edge-concepts/edge_concepts.yaml \
  --min-ticket-support 2

# 带提示提升和合成上限
python3 skills/edge-concept-synthesizer/scripts/synthesize_edge_concepts.py \
  --tickets-dir /tmp/edge-auto/tickets \
  --hints /tmp/edge-hints/hints.yaml \
  --output /tmp/edge-concepts/edge_concepts.yaml \
  --promote-hints \
  --max-synthetic-ratio 1.5

# 带自定义去重阈值（或禁用去重）
python3 skills/edge-concept-synthesizer/scripts/synthesize_edge_concepts.py \
  --tickets-dir /tmp/edge-auto/tickets \
  --output /tmp/edge-concepts/edge_concepts.yaml \
  --overlap-threshold 0.6

python3 skills/edge-concept-synthesizer/scripts/synthesize_edge_concepts.py \
  --tickets-dir /tmp/edge-auto/tickets \
  --output /tmp/edge-concepts/edge_concepts.yaml \
  --no-dedup
```

## 资源

- `skills/edge-concept-synthesizer/scripts/synthesize_edge_concepts.py`
- `references/concept_schema.md`
