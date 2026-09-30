---
name: ra-qm-skills
description: 本插件内嵌的 15 项监管与质量管理技能的 Router/index（涵盖 ISO 13485 质量管理体系、欧盟《医疗器械法规》MDR 2017/745、依据 FDA《质量管理体系法规》（QMSR）进行的提交、ISO 14971 风险管理、纠正与预防措施（CAPA）、文档管理、ISO 27001/信息安全管理体系（ISMS）、ISO 42001 人工智能管理体系（AIMS）、欧盟《人工智能法案》、GDPR/DSGVO、SOC 2 以及审计）。当合规请求未明显对应某一项具体技能、而需要选定最匹配的技能时，请使用此 Router/index（例如：“准备 ISO 13485 审核”、“我的 AI 系统是否属于《人工智能法案》下的高风险系统”）。
---

# 监管事务与质量管理技能 — 路由器

此插件捆绑了面向医疗科技/健康科技组织的**15项合规技能**（此路由器是`ra-qm-team/skills/`下的第16个文件夹）。每项技能都是自包含的。

## 路由表

匹配请求，然后加载`ra-qm-team/skills/<技能>/SKILL.md`。如果有多行匹配，先问一个澄清问题。

| 请求信号 | 技能 | 路径 |
|---|---|---|
| 监管策略、途径选择、提交计划 | regulatory-affairs-head | `skills/regulatory-affairs-head/` |
| 管理评审、质量KPI、QMR治理 | quality-manager-qmr | `skills/quality-manager-qmr/` |
| ISO 13485 QMS实施、过程控制 | quality-manager-qms-iso13485 | `skills/quality-manager-qms-iso13485/` |
| ISO 14971风险分析、FMEA、风险文件 | risk-management-specialist | `skills/risk-management-specialist/` |
| 根本原因分析、纠正/预防措施 | capa-officer | `skills/capa-officer/` |
| 文件控制、21 CFR 第11部分、DHF/DMR/DHR | quality-documentation-manager | `skills/quality-documentation-manager/` |
| ISO 13485内部审计、NC分类 | qms-audit-expert | `skills/qms-audit-expert/` |
| ISO 27001审计计划与执行 | isms-audit-expert | `skills/isms-audit-expert/` |
| ISMS设计、安全风险评估 | information-security-manager-iso27001 | `skills/information-security-manager-iso27001/` |
| EU MDR分类、技术文件、PSUR | mdr-745-specialist | `skills/mdr-745-specialist/` |
| FDA 510(k)/PMA/De Novo、QMSR | fda-consultant-specialist | `skills/fda-consultant-specialist/` |
| GDPR/DSGVO、DPIA、数据主体权利 | gdpr-dsgvo-expert | `skills/gdpr-dsgvo-expert/` |
| EU AI法案风险分类、义务 | eu-ai-act-specialist | `skills/eu-ai-act-specialist/` |
| ISO/IEC 42001 AI管理系统 | iso42001-specialist | `skills/iso42001-specialist/` |
| SOC 2 Type I/II准备、信任标准 | soc2-compliance | `skills/soc2-compliance/` |

## 快速入门

```bash
# 示例：路由一个风险分析请求
cat ra-qm-team/skills/risk-management-specialist/SKILL.md
python3 ra-qm-team/skills/risk-management-specialist/scripts/risk_matrix_calculator.py --help
```

## 规则

- 路由到恰好一项技能，然后遵循该技能的工作流程。此路由器不自带任何工具。
- 所有输出都是决策支持：最终合规判定路由到指定的人类负责人（QMR、DPO、监管顾问）——绝不自动判定。
- 核实监管引用与当前文本是否一致（例如，2026-02-02生效的FDA QMSR取代了遗留的QSR子章节）。
