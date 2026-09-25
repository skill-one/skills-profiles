# 金融技能 — 路由器

此插件捆绑了**2个金融技能**（该路由器是`finance/skills/`下的第3个文件夹）。每个技能都是自包含的。

## 路由表

| 请求信号 | 技能 | 路径 |
|---|---|---|
| 比率分析、DCF估值、预算差异、基于驱动力的预测 | financial-analyst | `skills/financial-analyst/` |
| ARR/MRR、流失率、CAC/LTV、NRR、速动比率、SaaS基准 | saas-metrics-coach | `skills/saas-metrics-coach/` |

如果两者都匹配（例如，“评估我的SaaS公司”），则询问用户是否需要财务报表级分析（financial-analyst）或SaaS运营指标（saas-metrics-coach）。

## 快速入门

```bash
# 示例：路由一个报表分析请求
cat finance/skills/financial-analyst/SKILL.md
python3 finance/skills/financial-analyst/scripts/ratio_calculator.py --help

# 或者一个SaaS指标请求
python3 finance/skills/saas-metrics-coach/scripts/metrics_calculator.py --help
```

## 相关（单独打包，不在此捆绑包中）

- `finance/business-investment-advisor/` — 投资逻辑评估、ROI建模（仅提示技能，独立的嵌套插件）
- 根命令`/financial-health`和`/saas-health`封装了这些技能的脚本。

## 规则

- 路由到恰好一个技能，然后遵循该技能的工作流程。此路由器不自带任何工具。
- 始终将财务输出与用户的源数据进行验证；输出是分析支持，不是投资建议。
