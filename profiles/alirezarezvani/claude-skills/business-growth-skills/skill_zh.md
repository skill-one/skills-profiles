# 商业与成长技能 — 路由器

此插件捆绑了 **4 项技能**（该路由器是 `business-growth/skills/` 下第 5 个文件夹）。每项技能都是自包含的。

## 路由表

匹配请求，然后加载 `business-growth/skills/<技能>/SKILL.md`。如果有多行匹配，先问一个澄清问题。

| 请求信号 | 技能 | 路径 |
|---|---|---|
| 客户健康评分、流失风险、扩张策略 | 客户成功经理 | `skills/customer-success-manager/` |
| RFP/RFI 覆盖、竞争定位、PoC 计划 | 销售工程师 | `skills/sales-engineer/` |
| 管道覆盖、预测准确率（MAPE）、GTM 效率 | 收入运营 | `skills/revenue-operations/` |
| 报价书、合同、工作说明书、DPAs | 合同与报价书撰写者 | `skills/contract-and-proposal-writer/` |

## 快速入门

```bash
# 示例：路由一个账户健康请求
cat business-growth/skills/customer-success-manager/SKILL.md
python3 business-growth/skills/customer-success-manager/scripts/health_score_calculator.py --help
```

## 规则

- 路由到恰好一项技能，然后遵循该技能的工作流程。此路由器不自带任何工具。
- 使用技能的 Python 评分器进行指标评估，而不是手动估算；交易/合同输出为供人类法律/商业审核的草稿。
