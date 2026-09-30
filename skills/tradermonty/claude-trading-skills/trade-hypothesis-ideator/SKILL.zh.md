---
name: trade-hypothesis-ideator
description: 从市场数据、交易日志和日记片段中生成可证伪的交易策略假设。当您拥有结构化的输入数据包，并希望获得带有实验设计、终止标准和可选的与 edge-finder-candidate/v1 兼容的 strategy.yaml 导出的排名假设卡片时使用。
---

# 交易假设构思器

根据归一化的输入数据包生成1-5张结构化假设卡片，进行评论和排序，然后可选地将 `pursue` 卡片导出到 `strategy.yaml` + `metadata.json` 产物中。

## 使用场景

- 在收集到交易日志、日记条目或市场观察结果，这些暗示可能存在优势时
- 当你有一个结构化的输入数据包（JSON）包含证据片段，并希望得到可证伪的假设时
- 将定性观察结果转化为定量实验设计
- 在将资本投入以用淘汰标准验证新策略想法之前

## 前置条件

- 输入JSON数据包，包含一个或多个：`trade_log`、`journal_snippets`、`market_data`、`observations`
- Python 3.9+ 并安装了 `pyyaml`
- 无需外部API密钥（纯计算技能）

## 工作流程

1. 接收输入JSON数据包。
2. 运行第一轮归一化+证据提取。
3. 使用提示生成假设：
   - `prompts/system_prompt.md`
   - `prompts/developer_prompt_template.md`（注入 `{{evidence_summary}}`）
4. 使用 `prompts/critique_prompt_template.md` 评论假设。
5. 运行第二轮排序+输出格式化+安全防护。
6. 可选地通过步骤H策略导出器导出 `pursue` 假设。

## 脚本

- 第一轮（证据摘要）：

```bash
python3 skills/trade-hypothesis-ideator/scripts/run_hypothesis_ideator.py \
  --input skills/trade-hypothesis-ideator/examples/example_input.json \
  --output-dir reports/
```

- 第二轮（排序+输出+可选导出）：

```bash
python3 skills/trade-hypothesis-ideator/scripts/run_hypothesis_ideator.py \
  --input skills/trade-hypothesis-ideator/examples/example_input.json \
  --hypotheses reports/raw_hypotheses.json \
  --output-dir reports/ \
  --export-strategies
```

## 输出

- `hypothesis_cards_<date>.json` — 排序的假设卡片，包含结论（`pursue`、`revise`、`discard`）
- `hypothesis_cards_<date>.md` — 人类可读的摘要，包含实验设计和淘汰标准
- `strategy_<hypothesis_id>.yaml` — （可选）用于 `pursue` 卡片的边缘发现器兼容策略导出
- `metadata_<hypothesis_id>.json` — （可选）导出策略的溯源元数据

## 资源

- `references/hypothesis_types.md` — 假设模式的分类法（均值回归、动量、事件驱动等）
- `references/evidence_quality_guide.md` — 评估证据强度和样本量要求的标准
