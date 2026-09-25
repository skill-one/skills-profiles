# AWS 安全

**停止 — 请勿凭一般知识回答。** 在回答任何安全服务问题时，请先根据下方的子技能注册表匹配用户请求，并遵循其流程。如果流程指示加载参考文件，您必须在提供操作指导之前阅读该文件。切勿跳过路由步骤。

AWS 安全服务提供威胁检测（GuardDuty）、漏洞管理（Inspector）、统一安全仪表板和暴露分析（Security Hub）、合规态势管理（Security Hub CSPM）、敏感数据发现（Macie）、调查（Detective）以及集中式日志存储（Security Lake）。每个服务都有专门的参考流程，用于配置审查和发现/调查总结。

此技能可与或无需 AWS MCP 服务器配合使用。当可用时，建议使用 AWS MCP 服务器进行沙盒执行和审计日志记录。流程使用标准 AWS CLI 语法（`aws <服务> <命令>`）。

请参阅 `references/services-overview.md` 了解服务关系、数据格式和跨服务集成模式。

## 全局规则

1. **仅使用只读 API。** 此技能及其所有参考都仅使用非修改型 API。切勿参考、推荐或调用任何创建、修改、删除、启用、禁用或以其他方式修改资源状态或配置的 API — 即使是在文字推荐中也一样。请参阅服务参考文件以获取完整的允许 API 列表。

2. **不要对配置状态进行严重性判断。** 事实性地陈述已配置和未配置的内容。不要为配置状态分配严重性标签、差距评估或编辑性框架（例如，“关键差距”、“安全问题”）。

3. **不要推荐误报抑制建议。** 专注于帮助客户理解发现。不要推荐抑制过滤器、归档规则或发现驳回。

4. **在 GuardDuty 中优先处理攻击序列。** 类型前缀为 `AttackSequence:` 的发现代表关联的多步骤攻击。始终优先展示这些内容，然后再进行严重性分解。

5. **在 Security Hub 中优先处理暴露发现。** 暴露发现（攻击路径、资源暴露）代表 Security Hub 独特的跨服务关联。在任何发现总结中，始终优先展示这些内容。

6. **昂贵操作需要明确请求。** 默认情况下切勿按成员账户进行分页。仅当用户明确请求详细的账户级信息时，才执行按账户枚举。在可用的情况下使用统计/计数 API（例如，`get-coverage-statistics`）。

7. **匹配用户的语言。** 使用与用户相同的语言进行回复。

8. **核实，不要猜测。** 如果您无法从参考文件或 API 输出中确认事实，请说明。

9. **敏感数据披露。** 当流程生成的输出可能包含敏感信息（完整发现正文、IP 地址、资源标识符、网络配置、威胁情报详情）时，请先展示摘要。注明完整输出中包含的敏感数据。仅在调用方明确请求时才显示完整的原始响应。

## 此技能的工作原理

1. **找到子技能** — 将用户的请求与下方的子技能注册表进行匹配。按意义匹配，而不是按确切措辞匹配。如果存在歧义，请询问：“您是在检查配置，还是需要发现总结？”

2. **如果匹配子技能** — 阅读 `references/{sub-skill-id}.md` 并遵循其流程。

3. **如果没有匹配子技能** — 从下列服务参考文件中获取答案。加载 `references/services-overview.md` 获取跨服务上下文，或加载相关服务参考文件（例如，`references/guardduty.md`）以获取 API 范围和严重性评分问题。

4. **跨服务概述** — 当用户询问多个服务整体安全态势时，从 `references/services-overview.md` 开始，然后路由到相关子技能。

## 子技能注册表

| ID | 名称 | 触发短语 | 路由时机 | 参考 |
|----|------|-----------------|-------------------|-----------|
| `guardduty-configuration` | GuardDuty 配置审查 | "GuardDuty 是否配置", "检查探测器", "GuardDuty 功能启用", "运行时监控设置" | 用户想验证 GuardDuty 部署完整性 | `references/guardduty-configuration.md` |
| `guardduty-findings` | GuardDuty 发现总结 | "总结 GuardDuty 发现", "有哪些威胁", "GuardDuty 严重性分解", "攻击序列" | 用户想获取发现态势快照 | `references/guardduty-findings.md` |
| `inspector-configuration` | Inspector 配置审查 | "Inspector 是否扫描", "Inspector 启用", "扫描类型", "覆盖差距" | 用户想验证 Inspector 部署 | `references/inspector-configuration.md` |
| `inspector-findings` | Inspector 发现总结 | "发现的漏洞", "Inspector 发现", "CVE 总结", "漏洞态势" | 用户想获取漏洞概述 | `references/inspector-findings.md` |
| `security-hub-configuration` | Security Hub 配置审查 | "Security Hub 集成", "聚合配置", "连接器", "自动化规则", "V2 自动化规则", "OCSF 自动化规则" | 用户想验证 Security Hub V2 (OCSF) 设置 | `references/security-hub-configuration.md` |
| `security-hub-findings` | Security Hub 发现总结 | "风险概述", "暴露发现", "攻击路径", "OCSF 发现", "安全态势趋势" | 用户想获取 Security Hub V2 (OCSF) 发现概述 | `references/security-hub-findings.md` |
| `security-hub-cspm-configuration` | CSPM 配置审查 | "标准启用", "控制项", "FSBP", "CIS", "PCI-DSS", "NIST", "合规设置", "AI 安全", "AI 最佳实践", "CSPM 自动化规则", "ASFF 自动化规则" | 用户想验证合规标准设置 | `references/security-hub-cspm-configuration.md` |
| `security-hub-cspm-findings` | CSPM 合规总结 | "合规态势", "失败控制项", "通过率", "ASFF 发现", "第三方发现" | 用户想获取合规发现概述 | `references/security-hub-cspm-findings.md` |
| `macie-configuration` | Macie 配置审查 | "Macie 配置", "数据发现设置", "分类作业", "Macie 启用" | 用户想验证 Macie 部署 | `references/macie-configuration.md` |
| `macie-findings` | Macie 发现总结 | "发现的敏感数据", "Macie 发现", "数据分类结果", "PII 检测" | 用户想获取敏感数据概述 | `references/macie-findings.md` |
| `detective-configuration` | Detective 配置审查 | "Detective 配置", "行为图", "Detective 成员", "数据源" | 用户想验证 Detective 部署 | `references/detective-configuration.md` |
| `detective-investigations` | Detective 调查总结 | "Detective 调查", "调查状态", "指标", "发现组" | 用户想获取调查态势概述 | `references/detective-investigations.md` |
| `security-lake-configuration` | Security Lake 配置审查 | "Security Lake 配置", "启用的日志源", "订阅者", "数据湖设置" | 用户想验证 Security Lake 部署 | `references/security-lake-configuration.md` |
| `security-lake-sources` | Security Lake 源总结 | "什么正在流入 Security Lake", "摄取状态", "源健康", "数据湖异常" | 用户想获取数据湖健康概述 | `references/security-lake-sources.md` |
| `organization-policies` | 组织策略审查 | "组织策略", "org 策略", "SECURITYHUB_POLICY", "INSPECTOR_POLICY", "列出策略", "策略目标", "策略强制执行" | 用户想审查或发现 AWS Organizations 服务策略 | `references/organization-policies.md` |

## 模糊处理

| 关键词 | 路由至 |
|----------|----------|
| "自动化规则"（模糊） | Security Hub 和 Security Hub CSPM 都有自动化规则。如果客户使用 Security Hub V2 (OCSF)，路由至 Security Hub 配置。如果客户使用 Security Hub CSPM (ASFF)，路由至 CSPM 配置。不明确时请询问。 |
| "标准", "控制项", "合规", "FSBP", "CIS", "PCI", "NIST", "ASFF" | Security Hub CSPM 技能 |
| "集成", "风险评分", "攻击路径", "OCSF", "暴露", "连接器" | Security Hub 技能 |
| "威胁检测", "GuardDuty", "探测器", "运行时监控", "攻击序列" | GuardDuty 技能 |
| "漏洞", "CVE", "Inspector", "扫描", "代码漏洞" | Inspector 技能 |
| "敏感数据", "分类", "Macie", "PII", "数据发现" | Macie 技能 |
| "调查", "行为图", "Detective", "指标" | Detective 技能 |
| "数据湖", "日志源", "Security Lake", "订阅者", "摄取" | Security Lake 技能 |
| "组织策略", "org 策略", "策略类型", "列出策略 --filter" | 组织策略（跨服务） |

**注意：** 如果客户正在使用 Security Hub V2 (OCSF)，他们应使用 Security Hub 自动化规则（`list-automation-rules-v2`），并且不应使用 Security Hub CSPM 功能创建新规则，即使 CSPM 技术上仍然可用。

## 服务参考

按需加载服务参考文件 — 仅在当前回合需要服务功能、API 范围或严重性评分的上下文时。

| 参考 | 内容 | 加载时机 |
|-------|---------|-------------|
| `references/services-overview.md` | 跨服务关系、数据格式、成员模型、管理员发现、API 约定 | 跨服务问题、一般安全态势、"我应该启用哪些服务" |
| `references/guardduty.md` | GuardDuty API、严重性评分、服务说明 | GuardDuty 特定关于 API 或严重性的问题 |
| `references/inspector.md` | Inspector API、严重性评分、服务说明 | Inspector 特定关于 API 或严重性的问题 |
| `references/security-hub.md` | Security Hub V2 (OCSF) API、严重性评分、服务说明 | Security Hub V2 特定关于 API 或严重性的问题 |
| `references/security-hub-cspm.md` | Security Hub CSPM (V1/ASFF) API、严重性评分、服务说明 | CSPM 特定关于 API 或严重性的问题 |
| `references/macie.md` | Macie API、严重性评分、服务说明 | Macie 特定关于 API 或严重性的问题 |
| `references/detective.md` | Detective API、严重性评分、服务说明 | Detective 特定关于 API 或严重性的问题 |
| `references/security-lake.md` | Security Lake API、服务说明 | Security Lake 特定关于 API 的问题 |
| `references/organization-policies.md` | 组织级策略发现模式、策略类型、Organizations API | 关于跨安全服务组织级策略强制执行的问题 |

## 安全注意事项

- **日志记录和监控**：验证 CloudTrail 是否为安全服务和 Organizations API 调用启用了，CloudTrail 日志文件验证是否激活，以及 CloudWatch 是否存在用于异常特权读取模式的指标过滤器或警报，例如意外量、不寻常的主体或意外区域。
- **加密和目的地**：验证发布或导出目的地（如 S3 桶、SNS 主题和 CloudWatch 日志）在静态时使用 KMS 加密，在传输时使用 TLS。对于下游 S3 或 SNS 目的地，验证资源策略是否使用 `aws:SourceArn` 和 `aws:SourceAccount` 条件键。
- **通知接收者**：验证 SNS 主题订阅和其他安全警报接收者是否仅限于授权的安全人员，并定期审计订阅端点。
- **凭证管理**：确认 CLI 执行是否使用临时凭证（如 IAM 角色或 AWS SSO）。验证第三方集成凭证、API 令牌或连接器密钥是否存储在 AWS Secrets Manager 或 AWS Systems Manager Parameter Store 中，而不是明文配置文件或环境变量。
- **安全参考**：参考 [AWS Security Hub 最佳实践](https://docs.aws.amazon.com/securityhub/latest/userguide/securityhub-v2-recommendations.html)、[AWS CloudTrail 安全最佳实践](https://docs.aws.amazon.com/awscloudtrail/latest/userguide/best-practices-security.html)、[IAM 安全最佳实践](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html) 以及 [AWS Well-Architected 安全支柱](https://docs.aws.amazon.com/wellarchitected/latest/security-pillar/) 获取当前服务指导。
- **敏感数据**：安全服务输出可能包含敏感信息，如 IP 地址、资源标识符、账户 ID、漏洞详情、暴露路径和威胁情报。分类和处理要求因客户而异；在验证组织数据处理策略之前，切勿在不受保护的环境中存储或共享输出。
