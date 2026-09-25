# Amazon CloudFront

## 概述

配置 Amazon CloudFront 内容交付的领域专业知识：决定何时使用 CloudFront 以及它如何融入更广泛的整体架构、管理自定义域证书和多租户分发、保护源站、保障内容安全，以及监控流量。

这项技能是一个路由器。每个客户任务都映射到 `references/` 下面的一个流程文件。在采取行动之前，请完整阅读匹配的参考文件，然后遵循其约束条件和步骤。参考文件是自包含的：每个文件都包含自己的决策表、约束条件、流程和故障排除说明。

连接时（沙盒执行、审计日志、可观察性）使用 AWS MCP 服务器执行命令。否则，回退到 AWS CLI。CloudFront 是一个全球服务；无论客户的应用程序运行在哪里，其 API 调用和它使用的 AWS 证书管理器 (ACM) 证书都在 `us-east-1` 中进行。

## 您需要哪个 CloudFront 任务？

| 目标 | 参考 |
| --- | --- |
| 决定 CloudFront 是否是正确的层级、了解其集成方式、创建分发、调整缓存或选择定价 | [何时使用 CloudFront](references/when-to-use-cloudfront.md) |
| 通过 HTTPS 服务自定义域、管理 ACM 证书或为每个租户运行多个域并使用一个证书 | [使用 CloudFront 管理证书](references/managing-certificates-with-cloudfront.md) |
| 使 CloudFront 成为访问源站的唯一方式（S3 OAC、VPC 源站、源站相互 TLS、安全组） | [保护您的源站](references/protecting-your-origins.md) |
| 通过身份、位置、客户端证书或认证令牌限制谁可以查看内容 | [保护您的内容](references/securing-your-content.md) |
| 通过标准日志和实时日志获取流量可见性并进行分析 | [CloudFront 可观察性](references/cloudfront-observability.md) |
| 通过共享配置服务多个域，并进行每个租户的自定义（SaaS、平台） | [多租户分发](references/multi-tenant-distributions.md) |

## 路由说明

- **选择层级和创建分发与其它任务的区别。** CloudFront 是否是正确的入口层级、它如何集成、创建分发、缓存和定价都包含在何时使用参考中。其它参考假设分发已经存在，并配置其某个方面。
- **保护源站与保障内容安全的区别。** 将源站锁定为只能通过 CloudFront 访问（OAC、VPC 源站、源站 mTLS）是保护源站参考。限制哪些观众可以查看内容（签名 URL 和 Cookie、地理限制、观众 mTLS、边缘令牌验证）是保障内容安全参考。它们是成对的：只有当源站也被锁定时，内容控制才会生效。
- **观众 mTLS 与源站 mTLS 的区别。** 向 CloudFront 认证客户端（观众 mTLS）是内容安全。向源站认证 CloudFront（源站 mTLS）是源站保护。不同的控制，不同的参考。
- **自定义域证书与 Route 53 DNS 过渡。** 请求和验证 ACM 证书以及添加备用域名是管理证书参考。将域的 DNS 指向分发，包括区域 Apex 别名和任何故障转移，是 Route 53 工作，由单独的 `route53-cloudfront` 技能负责。

## 跨服务工作

将自定义域的 DNS 指向 CloudFront 分发，或使用 Route 53 记录在分发之间进行故障转移，是跨服务工作，由单独的 `route53-cloudfront` 技能负责。仅用于 CloudFront 端配置，请使用此技能。

## 额外资源

- [Amazon CloudFront 开发者指南](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/Introduction.html)
- [Amazon CloudFront 安全最佳实践（Amazon CloudFront 开发者指南）](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/security-best-practices.html)
- [Amazon CloudFront 产品页面](https://aws.amazon.com/cloudfront/)
- [Amazon CloudFront 定价](https://aws.amazon.com/cloudfront/pricing/)
