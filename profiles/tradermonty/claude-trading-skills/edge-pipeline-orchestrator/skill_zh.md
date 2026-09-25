# 边缘流程编排器

将所有边缘研究阶段协调为一个自动化的单一流程运行。

## 使用场景

- 从工单（或 OHLCV）运行完整的边缘流程到导出的策略
- 从草稿阶段恢复部分完成的流程
- 使用反馈循环审查和修订现有策略草稿
- 运行流程进行预览而不导出结果

## 工作流程

1. 从 CLI 参数加载流程配置
2. 如果提供 `--from-ohlcv`，则运行 `auto_detect` 阶段（从原始 OHLCV 数据生成工单）
3. 运行 `hints` 阶段从市场摘要和异常中提取边缘提示
4. 运行 `concepts` 阶段从工单和提示中合成抽象的边缘概念
5. 运行 `drafts` 阶段从概念中设计策略草稿
6. 运行审查-修订反馈循环：
   - 审查所有草稿（最多 2 次迭代）
   - `PASS` 判决累积；`REJECT` 判决累积
   - `REVISE` 判决触发 `apply_revisions` 并重新审查
   - 最大迭代次数后的剩余 `REVISE` 降级为 `research_probe`
7. 导出符合条件的草稿（`PASS` + `export_ready_v1` + 可导出 `entry_family`）
8. 写入 `pipeline_run_manifest.json` 包含完整的执行跟踪

## CLI 使用

```bash
# 从工单运行完整流程
python3 scripts/orchestrate_edge_pipeline.py \
  --tickets-dir path/to/tickets/ \
  --output-dir reports/edge_pipeline/

# 从 OHLCV 运行完整流程
python3 scripts/orchestrate_edge_pipeline.py \
  --from-ohlcv path/to/ohlcv.csv \
  --output-dir reports/edge_pipeline/

# 从草稿阶段恢复
python3 scripts/orchestrate_edge_pipeline.py \
  --resume-from drafts \
  --drafts-dir path/to/drafts/ \
  --output-dir reports/edge_pipeline/

# 仅审查模式
python3 scripts/orchestrate_edge_pipeline.py \
  --review-only \
  --drafts-dir path/to/drafts/ \
  --output-dir reports/edge_pipeline/

# 干运行（不导出）
python3 scripts/orchestrate_edge_pipeline.py \
  --tickets-dir path/to/tickets/ \
  --output-dir reports/edge_pipeline/ \
  --dry-run
```

## 输出

所有工件写入 `--output-dir`：

```
output-dir/
├── pipeline_run_manifest.json
├── tickets/          (来自 auto_detect)
├── hints/hints.yaml  (来自 hints)
├── concepts/edge_concepts.yaml
├── drafts/*.yaml
├── exportable_tickets/*.yaml
├── reviews_iter_0/*.yaml
├── reviews_iter_1/*.yaml  (如果需要)
└── strategies/<candidate_id>/
    ├── strategy.yaml
    └── metadata.json
```

## Claude 代码 LLM 增强工作流程

在 Claude 代码中完全运行 LLM 增强流程：

1. 运行 `auto_detect` 生成 `market_summary.json` + `anomalies.json`
2. Claude 代码分析数据并生成边缘提示
3. 将提示保存到 YAML 文件：

```yaml
- title: 工业品行业轮动
  observation: 科技表现不佳而工业品显示相对强势
  symbols: [CAT, DE, GE]
  regime_bias: 中性
  mechanism_tag: 流动
  preferred_entry_family: pivot_breakout
  hypothesis_type: 行业_股票
```

4. 使用 `--llm-ideas-file` 和 `--promote-hints` 运行编排器：

```bash
python3 scripts/orchestrate_edge_pipeline.py \
  --tickets-dir path/to/tickets/ \
  --llm-ideas-file llm_hints.yaml \
  --promote-hints \
  --as-of 2026-02-28 \
  --max-synthetic-ratio 1.5 \
  --strict-export \
  --output-dir reports/edge_pipeline/
```

### 可选标志

- `--as-of YYYY-MM-DD` — 传递给 `hints` 阶段进行日期过滤
- `--strict-export` — 导出符合条件的草稿，任何 `warn` 发现都会触发 `REVISE` 而不是 `PASS`
- `--max-synthetic-ratio N` — 将合成工单限制为真实工单数量的 N 倍（下限：3）
- `--overlap-threshold F` — 概念去重时的条件重叠阈值（默认：0.75）
- `--no-dedup` — 禁用概念去重

注意：`--llm-ideas-file` 和 `--promote-hints` 仅在完整流程运行时有效。
`--resume-from drafts` 和 `--review-only` 跳过 `hints`/`concepts` 阶段，因此这些标志会被忽略。

## 资源

- `references/pipeline_flow.md` — 流程阶段、数据契约和架构
- `references/revision_loop_rules.md` — 审查-修订反馈循环规则和启发式方法
