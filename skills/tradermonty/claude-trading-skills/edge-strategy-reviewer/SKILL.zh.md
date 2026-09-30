---
name: edge-strategy-reviewer
description: 对边缘策略设计者（edge-strategy-designer）提交的策略草稿进行严格审查，重点评估边缘可信度、过拟合风险、样本量充分性以及执行可行性。当存在 strategy_drafts/*.yaml 且需在流水线导出前通过质量门禁时，应使用本功能。输出包含 PASS/REVISE/REJECT 判定及置信度评分。
---

# 边缘策略审查器

`edge-strategy-designer` 生成的策略草图的确定性质量门禁。

## 使用场景

- `edge-strategy-designer` 生成 `strategy_drafts/*.yaml` 后
- 在通过管道导出草稿到 `edge-candidate-agent` 之前
- 在手动验证边缘可行性策略草稿时

## 前置条件

- 策略草稿 YAML 文件（`edge-strategy-designer` 的输出）
- Python 3.10+ 及 PyYAML

## 工作流程

1. 从 `--drafts-dir` 或单个 `--draft` 文件加载草稿 YAML 文件
2. 使用加权评分对每个草稿针对 8 项标准（C1-C8）进行评估
3. 计算置信度分数（所有标准的加权平均值）
4. 确定判定结果：PASS / REVISE / REJECT
5. 评估导出资格（PASS + export_ready_v1 + 可导出系列）
6. 编写审查输出（YAML 或 JSON）和可选的 markdown 摘要

## 审查标准

| # | 标准 | 权重 | 关键检查 |
|---|-----------|--------|------------|
| C1 | 边缘可行性 | 20 | 论文质量、领域术语、机制关键词（连续 50-95） |
| C2 | 过拟合风险 | 20 | 5 级过滤器计数评分（90/80/60/40/10）、精确阈值惩罚 |
| C3 | 样本充分性 | 15 | 从估计的年机会数量连续评分（10-95） |
| C4 | 体制依赖性 | 10 | 跨体制验证 |
| C5 | 出场校准 | 10 | 止损、风险回报比 |
| C6 | 风险集中度 | 10 | 仓位规模限制 |
| C7 | 执行现实性 | 10 | 成交量过滤器、导出一致性 |
| C8 | 无效质量 | 5 | 信号数量和特异性 |

## 判定逻辑

- C1 或 C2 严重性=fail → 立即 REJECT
- 置信度 >= 70，无 fail 检查结果 → PASS
- 置信度 < 35 → REJECT
- 其他情况 → REVISE（附带修订说明）

## 运行脚本

```bash
# 审查目录中的所有草稿
python3 skills/edge-strategy-reviewer/scripts/review_strategy_drafts.py \
  --drafts-dir reports/edge_strategy_drafts/ \
  --output-dir reports/

# 单个草稿审查
python3 skills/edge-strategy-reviewer/scripts/review_strategy_drafts.py \
  --draft reports/edge_strategy_drafts/draft_xxx.yaml \
  --output-dir reports/

# JSON 输出带 markdown 摘要
python3 skills/edge-strategy-reviewer/scripts/review_strategy_drafts.py \
  --drafts-dir reports/edge_strategy_drafts/ \
  --output-dir reports/ \
  --format json \
  --markdown-summary

# 严格导出模式：任何 warn 的导出资格草稿 → REVISE
python3 skills/edge-strategy-reviewer/scripts/review_strategy_drafts.py \
  --drafts-dir reports/edge_strategy_drafts/ \
  --output-dir reports/ \
  --strict-export

# 偏好清单（问题 #297）：强制策略研究偏好门禁。
# 使用捆绑清单，除非提供了自定义 YAML 路径。
# 任何必需项目未处理的草稿会降级 PASS → REVISE
# 并失去导出资格。
python3 skills/edge-strategy-reviewer/scripts/review_strategy_drafts.py \
  --drafts-dir reports/edge_strategy_drafts/ \
  --output-dir reports/ \
  --bias-checklist
```

## 输出格式

主要输出：`review.yaml`（或 `review.json`）

```yaml
generated_at_utc: "2026-02-28T12:00:00+00:00"
source:
  drafts_dir: "/path/to/strategy_drafts"
  draft_count: 4
summary:
  total: 4
  PASS: 1
  REVISE: 2
  REJECT: 1
  export_eligible: 1
reviews:
  - draft_id: "draft_xxx_core"
    verdict: "PASS"
    confidence_score: 80
    export_eligible: true
    findings: [...]
    revision_instructions: []
```

## 资源

- `references/review_criteria.md` — C1-C8 的详细评分标准
- `references/overfitting_checklist.md` — 过拟合检测启发式方法
