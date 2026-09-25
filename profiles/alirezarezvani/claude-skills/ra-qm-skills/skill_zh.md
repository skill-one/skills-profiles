# 监管事务与质量管理技能 — 路由器

此插件捆绑了 **15 项合规技能**，适用于医疗科技/健康科技组织（此路由器是 `ra-qm-team/skills/` 下第 16 个文件夹）。每项技能都是自包含的。

## 路由表

匹配请求，然后加载 `ra-qm-team/skills/<技能>/SKILL.md`。如果有多行匹配，先问一个澄清问题。

| 请求信号 | 技能 | 路径 |
|---|---|---|
| 监管策略、途径选择、提交计划 | regulatory-affairs-head | `skills/regulatory-affairs-head/` |
| 管理评审、质量 KPI、QMR 治理 | quality-manager-qmr | `skills/quality-manager-qmr/` |
| ISO 13485 QMS 实施、过程控制 | quality-manager-qms-iso13485 | `skills/quality-manager-qms-iso13485/` |
| ISO 14971 风险分析、FMEA、风险文件 | risk-management-specialist | `skills/risk-management-specialist/` |
| 根本原因分析、纠正/预防措施 | capa-officer | `skills/capa-officer/` |
| 文件控制、21 CFR 第 11 部分、DHF/DMR/DHR | quality-documentation-manager | `skills/quality-documentation-manager/` |
| ISO 13485 内部审计、NC 分类 | qms-audit-expert | `skills/qms-audit-expert/` |
| ISO 27001 审计计划与执行 | isms-audit-expert | `skills/isms-audit-expert/` |
| ISMS 设计、安全风险评估 | information-security-manager-iso27001 | `skills/information-security-manager-iso27001/` |
| EU MDR 分类、技术文件、PSUR | mdr-745-specialist | `skills/mdr-745-specialist/` |
| FDA 510(k)/PMA/De Novo、QMSR | fda-consultant-specialist | `skills/fda-consultant-specialist/` |
| GDPR/DSGVO、DPIA、数据主体权利 | gdpr-dsgvo-expert | `skills/gdpr-dsgvo-expert/` |
| EU AI 法风险分类、义务 | eu-ai-act-specialist | `skills/eu-ai-act-specialist/` |
| ISO/IEC 42001 AI 管理系统 | iso42001-specialist | `skills/iso42001-specialist/` |
| SOC 2 类型 I/II 准备、信任标准 | soc2-compliance | `skills/soc2-compliance/` |

## 快速入门

```bash
# 示例：路由一个风险分析请求
cat ra-qm-team/skills/risk-management-specialist/SKILL.md
python3 ra-qm-team/skills/risk-management-specialist/scripts/risk_matrix_calculator.py --help
```

## 规则

- 路由到恰好一项技能，然后遵循该技能的工作流程。此路由器不自带任何工具。
- 所有输出都是决策支持：最终合规判定路由到指定的负责人（QMR、DPO、监管顾问）——从不自动判定。
- 核对监管引用与当前文本（例如，FDA QMSR 生效于 2026-02-02 替换了遗留的 QSR 子部分）。
