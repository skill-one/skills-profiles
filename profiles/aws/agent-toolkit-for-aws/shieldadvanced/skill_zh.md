# AWS Shield Advanced

## 概述

AWS Shield Advanced 提供专业领域的配置指导，这是付费层级，在始终开启的 AWS Shield Standard 基础上增加了增强型分布式拒绝服务 (DDoS) 保护、自动应用层缓解、攻击可见性、专家支持以及成本保护。涵盖订阅和资源保护、自动应用层缓解、基于健康的检测、Shield 响应小组 (SRT) 访问和主动参与、事件审查和成本保护信用额度，以及保护组。

此技能是一个路由器。每个客户任务都映射到 `references/` 下面的一个流程文件。在采取行动之前，请完整阅读匹配的参考文件，然后遵循其约束条件和步骤。参考文件是自包含的：每个文件都包含自己的决策表、约束条件、流程和故障排除。

连接时使用 AWS MCP 服务器执行命令（沙盒执行、审计日志记录、可观察性）。否则，回退到 AWS CLI。Shield Advanced 是一项全球服务：其控制平面 API 调用在 `us-east-1` 中运行，因此在对每个 `aws shield` 命令传递 `--region us-east-1`。

## 您需要哪个 Shield Advanced 任务？

| 目标 | 参考 |
| --- | --- |
| 判断是否需要 Shield Advanced（与 Shield Standard + AWS WAF 相比） | [deciding between Shield Standard and Advanced](references/deciding-between-shield-standard-and-advanced.md) |
| 订阅账户并将资源添加到保护中 | [subscribing to Shield Advanced and protecting resources](references/subscribing-to-shield-advanced-and-protecting-resources.md) |
| 通过 AWS WAF 自动响应第 7 层洪水 | [enabling automatic application layer mitigation](references/enabling-automatic-application-layer-mitigation.md) |
| 使用 Route 53 健康检查将资源健康状态输入检测 | [configuring health-based detection](references/configuring-health-based-detection.md) |
| 在攻击期间让 Shield 响应小组采取行动或联系 | [setting up SRT support and proactive engagement](references/setting-up-srt-support-and-proactive-engagement.md) |
| 审查 DDoS 事件并恢复攻击驱动的扩展费用 | [reviewing DDoS events and requesting cost protection](references/reviewing-ddos-events-and-requesting-cost-protection.md) |
| 将相关资源视为一个单元进行检测 | [aggregating resources into protection groups](references/aggregating-resources-into-protection-groups.md) |

## 路由说明

- **在订阅前做出决定。** Shield Advanced 是一项付费订阅，按一年期自动续订。在订阅之前，请确认客户确实需要它：Shield Standard（免费、始终开启）加上 AWS WAF 的速率规则和 AWS WAF Anti-DDoS 管理规则组 (`AWSManagedRulesAntiDDoSRuleSet`) 可以以较低成本覆盖许多第 7 层情况。当客户尚未做出决定时，请首先路由到决策参考文件；路由到 WAF 技能以获取 WAF 规则本身。
- **订阅和保护是首要任务。** 订阅本身不会保护任何内容；资源必须明确添加。这里的其他所有任务都假设资源已经订阅并受到保护。如果客户从零开始，请先运行订阅参考文件。
- **自动缓解与基于健康的检测。** 这些是不同的控制，客户会混淆它们。自动应用层缓解在发生第 7 层攻击时部署 AWS WAF 规则。基于健康的检测将 Route 53 健康检查输入 Shield Advanced 的检测，使其能够更快地做出反应。客户可以运行其中任何一个，或者都不运行。选择与客户实际需求匹配的参考文件。
- **健康检查也是 SRT 的先决条件。** 主动参与（SRT 联系）需要在受保护资源上配置 Route 53 健康检查。如果客户希望主动参与，配置基于健康的检测是基础工作。SRT 参考文件会指向基于健康的检测参考文件以完成该步骤。
- **保护组仅用于检测。** 保护组会改变 Shield Advanced 在一组资源上的检测方式。它不会应用共享缓解；自动缓解仍然按资源工作。使用保护组参考文件进行检测调整，而不是作为缓解控制。
- **WAF 规则、健康检查和组织推广在其他地方。** 编写 AWS WAF 规则、速率规则或 Web ACL 是 WAF 技能的工作。创建 Route 53 健康检查是 route53 技能的工作。使用 Firewall Manager 在组织内推广 Shield Advanced 是 firewallmanager 技能的工作。此技能将 Shield Advanced 连接到这些部分；它不会构建它们。AWS WAF 与 Shield Advanced 一起不是可选的：您应该建议在每個面向互联网的受保护资源（CloudFront 分发和 Application Load Balancers）上部署 AWS WAF Web ACL，作为纵深防御——Shield Advanced 和 AWS WAF 是互补的第 3/4 层和第 7 层控制，AWS WAF 提供的速率规则也是成本保护所要求的。

## 日志和监控

对配置更改和攻击活动的可见性对这里的每个任务都很重要。

- 您应该建议启用 AWS CloudTrail，以便所有 Shield Advanced API 调用（订阅、保护、SRT 和保护组更改）都为审计目的进行日志记录。
- 您应该建议在 CloudTrail 日志存储桶和 CloudWatch Logs 日志组上启用 SSE-KMS 加密，因为 CloudTrail 记录敏感的 API 元数据（调用者身份、资源 ARN、参数），这些元数据必须在静态时加密。
- 您应该建议在 Shield Advanced 指标（例如 `DDoSDetected` 和 `DDoSAttackBitsPerSecond`）上设置 CloudWatch 报警，以便当检测到事件时，运维人员会收到警报。
- 您应该建议使用 SSE-KMS 加密用于这些报警的任何 SNS 主题，因为通知包含敏感的事件数据。
- 您应该建议确认所有 Shield Advanced 报警的 SNS 主题订阅者都是经过授权的人员，他们被批准接收敏感的 DDoS 事件通知。

## 安全注意事项

Shield Advanced 设置会创建 IAM 信任关系并暴露日志数据，因此请指出风险和包含这些风险的控制措施。

- **SRT 角色是第三方主体。** 授予 SRT 访问权限会创建一个 IAM 角色，`drt.shield.amazonaws.com` 会假设该角色在账户中执行操作。使用 `aws:SourceAccount` 条件将其信任策略的范围设置为与账户 ID 相等的值，以防止混淆代理假设，仅授予其所需的操作，并在不再需要时使用 `disassociate-drt-role` 撤销它。
- **与 SRT 共享的日志存储桶可能会泄露数据。** AWS WAF 和访问日志会捕获请求 URI、标头和客户端 IP。在将它们与 SRT 共享之前，请确认这些存储桶具有服务器端加密，并且不包含明文 PII 或密钥。
- **操作员的最低权限。** 将调用者的 IAM 权限范围限制为每个流程所需的最低权限，而不是广泛的 Shield 或管理员访问权限。
- **审计跟踪。** 保持 AWS CloudTrail 启用并记录 `shield:*` 调用，以便每次配置更改都留有记录。

## 其他资源

- [AWS Shield Advanced 概述 (AWS WAF、AWS Firewall Manager 和 AWS Shield Advanced 开发者指南)](https://docs.aws.amazon.com/waf/latest/developerguide/ddos-overview.html)
- [AWS Shield 工作原理 (AWS WAF、AWS Firewall Manager 和 AWS Shield Advanced 开发者指南)](https://docs.aws.amazon.com/waf/latest/developerguide/ddos-how-shield-works.html)
- [AWS Shield Advanced 定价](https://aws.amazon.com/shield/pricing/)
