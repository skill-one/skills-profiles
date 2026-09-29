---
name: business-growth-skills
description: 此插件中捆绑的4项业务与成长技能的Router/index：客户成功经理（健康评分、流失风险、拓展）、销售工程师（RFP分析、竞争矩阵、PoC规划）、收入运营（管道、预测准确率、GTM效率）以及合同与提案撰写者。当成长/收入请求不明显匹配某项技能，且需要选择正确技能时使用（例如，“哪些账户存在风险”、“是否应该竞标此RFP”）。
---

# 商业与成长技能 — 路由器

此插件捆绑了**4项技能**（该路由器是`business-growth/skills/`下的第5个文件夹）。每项技能都是自包含的。

## 路由表

匹配请求，然后加载`business-growth/skills/<技能>/SKILL.md`。如果有多行匹配，先问一个澄清问题。

| 请求信号 | 技能 | 路径 |
|---|---|---|
| 客户健康评分、流失风险、扩张策略 | 客户成功经理 | `skills/customer-success-manager/` |
| RFP/RFI覆盖、竞争定位、PoC计划 | 销售工程师 | `skills/sales-engineer/` |
| 管道覆盖、预测准确度（MAPE）、GTM效率 | 收入运营 | `skills/revenue-operations/` |
| 投标书、合同、工作说明书、DPAs | 合同与投标书撰写人 | `skills/contract-and-proposal-writer/` |

## 快速入门

```bash
# 示例：路由一个账户健康请求
cat business-growth/skills/customer-success-manager/SKILL.md
python3 business-growth/skills/customer-success-manager/scripts/health_score_calculator.py --help
```

## 规则

- 路由到恰好一项技能，然后遵循该技能的工作流程。此路由器不自带任何工具。
- 使用技能的Python评分器进行指标评估，而不是手动估算；交易/合同输出为供人工法律/商业审核的草稿。
