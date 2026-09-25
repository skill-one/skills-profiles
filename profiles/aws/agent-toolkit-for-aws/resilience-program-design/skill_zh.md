# 弹性计划设计

## 概述

组织弹性计划的规划级指导：如何按层级结构化策略，以及如何定期运行弹性活动。

## 在整个组织中结构化弹性策略

建议采用**分层策略模型**（而不是每个服务一个策略）：按业务关键性对服务进行分类，并相应地设置策略目标。

- **可用性SLO** — 随着关键性提高而提高。API仅接受一组固定的SLO值，并拒绝超出范围的值，因此**从API/文档中确认有效值**（例如 `aws resiliencehubv2 create-policy help` 或弹性中心文档），而不是依赖硬编码列表——例如值如 `99.9`/`99.95`/`99.99`。
- **RTO/RPO** — 随着关键性提高而收紧（关键性为单位数分钟，低级别为小时）。
- **灾难恢复方法** — 与关键性匹配（关键性越高越激进），使用API的灾难恢复方法枚举值——**通过API/文档验证有效集**（例如 `aws resiliencehubv2 create-policy help`）；例如 `ACTIVE_ACTIVE` … `BACKUP_AND_RESTORE`。

示例（说明性——在推荐前需与API确认实际枚举值）：payments/auth → `99.99` + 单位数分钟RTO + `ACTIVE_ACTIVE`；内部工具 → `99.9` + 十位数分钟RTO + `WARM_STANDBY`；开发/测试 → `99.9` + 多小时RTO + `BACKUP_AND_RESTORE`。

警告不要设置矛盾策略（例如最大SLO `99.99` 与 `BACKUP_AND_RESTORE`，或跨区域RTO短于跨可用区RTO）。

## 运行弹性活动的频率（节奏）

当被问及运行弹性活动的频率时，建议此最低频率：

- **持续**：ARC区域自动迁移练习（自动化）
- **每周**：查看弹性中心发现仪表板
- **每月**：运行FIS实验（单服务故障注入测试）
- **每季度**：跨服务GameDay
- **事件驱动**：每次生产事件后以及主要部署前后

## 安全注意事项

计划级指导——将安全纳入你设定的标准：

- **标准化最小权限**：要求你的模板和策略中的每个弹性角色（弹性中心调用者、FIS执行者、ARC操作员）均为最小权限和资源范围，并在其信任策略中使用 `aws:SourceArn` / `aws:SourceAccount` 条件键，以防止混淆代理访问。
- **强制使用短期凭证**：要求所有弹性自动化以IAM **角色**进行身份验证，使用短期凭证（角色假定、AWS SSO、实例配置文件）——永远不要使用具有长期访问密钥的IAM用户——作为计划标准，因为这些角色执行特权和可能具有破坏性的操作。
- **强制使用加密**：将报告/状态桶的SSE-KMS纳入你的层级基线，并强制执行传输中加密（TLS）——例如在这些桶策略中添加 `aws:SecureTransport` 拒绝为false的条件，并仅允许HTTPS API访问。
- **在生产中管理FIS**：将生产故障注入的授权/变更管理网关作为计划节奏的一部分进行定义。
- **限制弹性输出的暴露**：评估结果、FIS日志和GameDay报告可能包含敏感的架构细节（资源ARN、IP、故障模式）——将限制其对授权人员的访问作为你的计划标准的一部分。
- **进一步阅读**：将团队指向 [AWS Well-Architected Security Pillar](https://docs.aws.amazon.com/wellarchitected/latest/security-pillar/welcome.html)、[FIS Security Best Practices](https://docs.aws.amazon.com/fis/latest/userguide/security.html) 和 [IAM Best Practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html) 以实施这些标准。
