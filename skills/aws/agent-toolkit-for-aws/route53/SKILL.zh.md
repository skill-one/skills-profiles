---
name: route53
description: 配置 Amazon Route 53 DNS：公共和私有记录、流量转向路由策略、健康检查、DNS 防火墙、Route 53 配置文件、VPC 解析器（也称为 Route 53 解析器）用于混合网络和 Outposts 网络，以及全球解析器。适用于客户希望将主机名指向目标、跨端点拆分或切换流量、监控端点、阻止恶意域名、跨账户集中管理 DNS 或在混合网络中解析私有 DNS 的情况。根据任务需求，引导至正确的操作步骤。不涵盖 CloudFront 特定设置（请参阅 route53-cloudfront 技能）或非 DNS 网络配置。
---

# 亚马逊Route 53

## 概述

在公共和私有解析路径上配置亚马逊Route 53 DNS的专业知识：托管区域记录、流量转向路由策略、健康检查、DNS防火墙、Route 53配置文件、VPC解析器（也称为Route 53解析器）用于混合和Outposts网络，以及全局解析器。

这项技能是一个路由器。每个客户任务都映射到`references/`下的一个流程文件。在采取行动之前，请完整阅读匹配的参考文档，然后遵循其约束条件和步骤。参考文件是自包含的：每个文件都包含自己的决策表、约束条件、流程和故障排除。

连接时使用AWS MCP服务器执行命令（沙盒执行、审计日志记录、可观察性）。否则，回退到AWS CLI。所有Route 53域名API调用均在`us-east-1`区域进行，无论客户在哪里工作。

## 您需要哪个Route 53任务？

| 目标 | 参考 |
| --- | --- |
| 将主机名或区域 Apex 指向 IP、AWS 资源或主机名 | [创建公共DNS记录](references/creating-a-public-dns-record.md) |
| 按比例（蓝/绿、金丝雀、A/B）将流量分配到端点 | [使用加权路由拆分流量](references/splitting-traffic-with-weighted-routing.md) |
| 在两个区域之间进行故障转移以实现灾难恢复 | [配置故障转移路由](references/configuring-failover-routing.md) |
| 监控端点是否正常并接收警报 | [设置Route 53健康检查](references/setting-up-a-route53-health-check.md) |
| 在解析器上阻止恶意域名 | [阻止恶意域名](references/blocking-malicious-domains.md) |
| 确定多个规则组中哪个DNS防火墙规则对某个域名生效 | [识别有效的DNS防火墙规则](references/identifying-the-effective-dns-firewall-rule.md) |
| 在许多VPC和账户中应用一个DNS配置 | [配置Route 53配置文件](references/configuring-route53-profiles.md) |
| 在整个组织中通过配置文件扩展DNS防火墙 | [使用配置文件集中DNS防火墙](references/centralizing-dns-firewall.md) |
| 在混合网络中双向解析私有DNS | [为混合网络解析私有DNS](references/resolving-private-dns-for-hybrid-networks.md) |
| 在AWS Outposts机架上本地运行VPC解析器 | [在Outposts上运行VPC解析器](references/running-route53-resolver-on-outposts.md) |
| 为本地和远程客户端提供单个任何播DNS端点 | [设置全局解析器](references/setting-up-route53-global-resolver.md) |

## 路由注意事项

- **记录与路由策略。** 纯粹的主机名到目标映射是公共DNS记录任务。拆分或转向流量（加权、故障转移）是具有其自身参考的单独路由策略任务。从客户意图开始，而不是记录类型。
- **健康检查与故障转移。** 健康检查监控端点并触发警报。故障转移路由策略在检查失败时决定流量去向。它们是两个参考，并且通常一起使用：设置健康检查，然后将其连接到故障转移。
- **单个VPC的DNS防火墙与多个账户。** 为VPC编写规则是阻止参考。使用配置文件和防火墙管理器在整个账户中扩展相同保护是集中参考。
- **DNS防火墙编写与诊断。** 创建或更改规则是阻止参考。在关联多个规则组时确定哪个规则对某个域名已经生效（读取和诊断任务）是识别有效规则的参考。
- **配置文件，两个入口点。** 一般配置文件设置（附加资源、通过RAM共享、成本和可见性权衡）是配置配置文件的参考。专门使用配置文件在整个组织中扩展DNS防火墙是集中参考。
- **VPC解析器，三个上下文。** 区域内混合解析、Outposts本地解析器和全局解析器任何播端点是三个独立的参考。将参考与解析器运行位置匹配。

## 跨服务协作

将自定义域名指向CloudFront分发，或在CloudFront分发之间进行故障转移，是`route53-cloudfront`技能拥有的跨服务工作。仅用于纯Route 53任务的Route 53方面，请使用此技能。

## 安全注意事项

以下适用于以下Route 53任务；每个参考都重复其工作流中承重的部分。

- 您应该使用通过IAM角色（实例配置文件、SSO/IAM身份中心会话凭证或`aws sts assume-role`）配置的最低权限IAM凭证，而不是长生命周期的IAM用户访问密钥，并且对于检查步骤，更喜欢只读凭证。
- 您应该建议使用加密DNS传输（DoT或DoH）而不是明文的Do53，因为Do53将查询的域名暴露给路径观察者。
- 您必须将解析器端点安全组规则的范围限制在本地CIDR范围或已知的DNS服务器IP上，绝不能是`0.0.0.0/0`。
- 您必须加密查询日志和通知目的地：CloudWatch Logs日志组的KMS、S3桶的SSE-S3/SSE-KMS、数据火管流的服务器端加密（SSE）以及SNS主题的SSE，因为DNS查询日志和健康检查通知可能会泄露基础设施拓扑。
- 对于全局解析器，您必须将创建时返回的访问令牌`value`视为机密；将其存储在AWS Secrets Manager中，而不是明文，并验证每个DNS视图授权哪些客户端群体。

## 其他资源

- [亚马逊Route 53开发者指南](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/Welcome.html)
- [亚马逊Route 53产品页面](https://aws.amazon.com/route53/)
- [Route 53定价](https://aws.amazon.com/route53/pricing/)
