# 边缘候选代理

## 概述

将日常市场观察转化为可复现的研究工单和与第一阶段兼容的候选规格。
优先考虑信号质量和接口兼容性，而非激进策略的扩散。
此技能可以独立运行端到端，但在拆分工作流中主要服务于最终的导出/验证阶段。

## 使用场景

- 将市场观察、异常或假设转化为结构化的研究工单。
- 运行每日自动检测，从每日收盘价OHLCV和可选提示中发现新的边缘候选。
- 将验证后的工单导出为`strategy.yaml` + `metadata.json`，用于`trade-strategy-pipeline`的第一阶段。
- 在管道执行前运行`edge-finder-candidate/v1`的预检兼容性检查。

## 前置条件

- Python 3.9+，并安装了`PyYAML`。
- 可以访问目标`trade-strategy-pipeline`仓库以进行模式/阶段验证。
- 在通过`--pipeline-root`运行管道管理的验证时，`uv`可用。

## 输出

- `strategies/<candidate_id>/strategy.yaml`：与第一阶段兼容的策略规格。
- `strategies/<candidate_id>/metadata.json`：包含接口版本和工单上下文的可追溯性元数据。
- 来自`scripts/validate_candidate.py`的验证状态（通过/失败+原因）。
- 每日检测工件：
  - `daily_report.md`
  - `market_summary.json`
  - `anomalies.json`
  - `watchlist.csv`
  - `tickets/exportable/*.yaml`
  - `tickets/research_only/*.yaml`

## 拆分工作流中的位置

推荐的拆分工作流：

1. `skills/edge-hint-extractor`：观察/新闻 -> `hints.yaml`
2. `skills/edge-concept-synthesizer`：工单/提示 -> `edge_concepts.yaml`
3. `skills/edge-strategy-designer`：概念 -> `strategy_drafts` + 可导出工单YAML
4. `skills/edge-candidate-agent`（此技能）：导出+验证，用于管道交接

## 工作流

1. 从每日收盘价运行自动检测：
   - `skills/edge-candidate-agent/scripts/auto_detect_candidates.py`
   - 可选：`--hints`用于人类构思输入
   - 可选：`--llm-ideas-cmd`用于外部LLM构思循环
2. 加载合约和映射引用：
   - `references/pipeline_if_v1.md`
   - `references/signal_mapping.md`
   - `references/research_ticket_schema.md`
   - `references/ideation_loop.md`
3. 使用`references/research_ticket_schema.md`构建或更新研究工单。
4. 使用`skills/edge-candidate-agent/scripts/export_candidate.py`导出候选工件。
5. 使用`skills/edge-candidate-agent/scripts/validate_candidate.py`验证接口和第一阶段约束。
6. 将候选目录交接给`trade-strategy-pipeline`，并首先运行干跑。

## 快速命令

每日自动检测（带可选导出/验证）：

```bash
python3 skills/edge-candidate-agent/scripts/auto_detect_candidates.py \
  --ohlcv /path/to/ohlcv.parquet \
  --output-dir reports/edge_candidate_auto \
  --top-n 10 \
  --hints path/to/hints.yaml \
  --export-strategies-dir /path/to/trade-strategy-pipeline/strategies \
  --pipeline-root /path/to/trade-strategy-pipeline
```

从工单创建候选目录：

```bash
python3 skills/edge-candidate-agent/scripts/export_candidate.py \
  --ticket path/to/ticket.yaml \
  --strategies-dir /path/to/trade-strategy-pipeline/strategies
```

仅验证接口合约：

```bash
python3 skills/edge-candidate-agent/scripts/validate_candidate.py \
  --strategy /path/to/trade-strategy-pipeline/strategies/my_candidate_v1/strategy.yaml
```

验证接口合约和管道模式/阶段规则：

```bash
python3 skills/edge-candidate-agent/scripts/validate_candidate.py \
  --strategy /path/to/trade-strategy-pipeline/strategies/my_candidate_v1/strategy.yaml \
  --pipeline-root /path/to/trade-strategy-pipeline \
  --stage phase1
```

## 导出规则

- 保持`validation.method: full_sample`。
- 保持`validation.oos_ratio`省略或`null`。
- 仅导出v1支持的入场家族：
  - `pivot_breakout` with `vcp_detection`
  - `gap_up_continuation` with `gap_up_detection`
- 在工单备注中将不支持的假设家族标记为仅研究，而非导出候选。

## 安全限制

- 拒绝违反模式边界（风险、退出、空条件）的候选。
- 当文件夹名和`id`不匹配时拒绝候选。
- 要求确定性元数据，`interface_version: edge-finder-candidate/v1`。
- 在管道全执行前使用`--dry-run`。

## 资源

### `skills/edge-candidate-agent/scripts/export_candidate.py`
从研究工单YAML生成`strategies/<candidate_id>/strategy.yaml`和`metadata.json`。

### `skills/edge-candidate-agent/scripts/validate_candidate.py`
运行接口检查，并可选地针对`trade-strategy-pipeline`运行`StrategySpec`/`validate_spec`检查。

### `skills/edge-candidate-agent/scripts/auto_detect_candidates.py`
从每日收盘价自动检测边缘想法，生成可导出/研究工单，并可选自动导出/验证。

### `references/pipeline_if_v1.md`
`edge-finder-candidate/v1`的集成合约摘要。

### `references/signal_mapping.md`
将假设家族映射到当前可导出的信号家族。

### `references/research_ticket_schema.md`
`export_candidate.py`使用的工单模式。

### `references/ideation_loop.md`
提示模式和外部LLM构思命令合约。
