# AWS WAF

## 概述

AWS WAF（Web 应用防火墙）配置领域的专业知识，用于过滤发送到 CloudFront 分发、应用负载均衡器、API Gateway REST API 和 AppSync GraphQL API 的 HTTP 和 HTTPS 流量。涵盖 Web ACL 创建和关联、AWS 管理规则、基于速率的规则、匹配规则（IP 集和地理）、Bot Control 以及在其之上构建的信号转发工作流、登录和注册的欺诈控制、AI 和 LLM 爬虫管理，以及每个调优工作流都依赖的日志记录。

这项技能是一个路由器。每个客户任务都映射到 `references/` 下面的一个流程文件。在采取行动之前，请完整阅读匹配的参考文件，然后遵循其约束和步骤。参考文件是自包含的：每个文件都包含自己的决策表、约束、流程和故障排除说明。

连接时使用 AWS MCP 服务器执行命令（沙盒执行、审计日志记录、可观察性）。否则，回退到 AWS CLI。Web ACL 的范围在创建时固定：CloudFront Web ACL 必须在 `us-east-1` 中创建，范围为 `CLOUDFRONT`，而区域资源需要在资源的区域中创建 `REGIONAL` Web ACL。

## 您需要哪个 WAF 任务？

| 目标 | 参考 |
| --- | --- |
| 创建 Web ACL 并将其附加到资源 | [创建 Web ACL 并将其与资源关联](references/creating-a-web-acl-and-associating-it-with-a-resource.md) |
| 在进行任何调优之前设置日志记录和采样 | [设置日志记录和请求采样](references/setting-up-logging-and-request-sampling.md) |
| 添加 AWS 管理规则并调优误报 | [添加管理规则并使用计数模式调优](references/adding-managed-rules-and-tuning-with-count-mode.md) |
| 阻止 HTTP 洪水和暴力破解 | [添加基于速率的规则](references/adding-rate-based-rules.md) |
| 根据 IP 范围或国家允许或阻止 | [使用 IP 集和地理匹配规则](references/using-ip-sets-and-geographic-match-rules.md) |
| 检测和控制机器人（入口） | [使用 Bot Control 防护机器人](references/protecting-against-bots-with-bot-control.md) |
| 将机器人标签合并为一个置信信号 | [将 Bot Control 标签转换为置信信号](references/turning-bot-control-labels-into-a-confidence-signal.md) |
| 使用一条规则将所有信号转发到源站 | [使用动态标签插值转发信号](references/forwarding-signals-with-dynamic-label-interpolation.md) |
| 决定应用程序如何处理转发信号 | [转发信号的适应性缓解剧本](references/adaptive-mitigation-playbook-for-forwarded-signals.md) |
| 阻止攻击者伪造转发头 | [在信任它们之前移除传入 WAF 头](references/stripping-inbound-waf-headers-before-trusting-them.md) |
| 恢复 CDN 背后的真实客户端 IP | [恢复 CDN 背后的真实客户端 IP](references/recovering-the-real-client-ip-behind-a-cdn.md) |
| 保护登录和注册免受欺诈 | [使用欺诈控制保护登录和注册](references/protecting-logins-and-signups-with-fraud-control.md) |
| 查看和管理 AI 和 LLM 爬虫流量 | [查看和管理 AI 爬虫流量](references/seeing-and-managing-ai-crawler-traffic.md) |

## 路由说明

- **日志记录先于调优。** 每个计数模式调优工作流都假设日志记录和请求采样已开启。如果客户尚未设置日志记录，请先运行该参考文件；否则，计数模式调优将无内容可读取。
- **Web ACL 范围在创建时固定。** CloudFront Web ACL 在 `us-east-1` 中为 `CLOUDFRONT` 范围；区域资源需要在其自己的区域中创建 `REGIONAL` Web ACL。范围之后无法更改，因此创建参考文件会在构建任何内容之前确定它。
- **Bot Control 是一个链，而不是一个任务。** 防护机器人是入口（开启、选择通用与目标、观察）。将标签转换为置信信号、转发该信号、决定应用程序如何处理它，是三个按顺序构建的独立参考文件。当信号转发到源站时，移除头参考文件是强制性的安全伴侣。
- **通用与目标不是软选择。** 通用仅捕获自识别的机器人和已知恶意 IP。对于登录、结账或任何面临规避机器人的高价值端点，需要使用应用程序集成 SDK 的目标。机器人参考文件将目标用于真实的机器人威胁，而不是将其呈现为可选。
- **速率限制与欺诈控制。** 基于速率的规则会削弱流量型 HTTP 洪水。凭证填充和虚假账户创建是账户型滥用，速率限制会遗漏这些；这些属于欺诈控制参考文件（ATP 和 ACFP），而不是基于速率的参考文件。
- **转发头需要移除规则。** 任何将信号或客户端 IP 转发到源站的 `x-amzn-waf-*` 头，都需要添加传入头移除规则以防止伪造。置信信号、插值和客户端 IP 参考文件都指向它。
- **其他技能中的内容。** L3/L4 DDoS 防护和 Shield 成本保护信用是 shieldadvanced 技能。多账户 WAF 推广是 firewallmanager 技能。CloudFront 和应用负载均衡器配置是它们自己的技能。这项技能构建 WAF 规则；它不会配置它保护的资源。

## 安全注意事项

AWS WAF 本身是一个安全控制，因此配置错误会直接削弱应用程序的防御。在所有参考文件中应用这些内容：

- **最小权限 IAM。** 您必须只授予任务所需的特定 `wafv2:` 操作（例如 `wafv2:CreateWebACL`、`wafv2:GetWebACL`、`wafv2:UpdateWebACL`、`wafv2:AssociateWebACL`、`wafv2:PutLoggingConfiguration`），而不是 `wafv2:*` 或 `AWSWAFFullAccess` 管理策略。
- **临时凭证。** 您必须使用 IAM 角色和临时凭证（例如 EC2 实例配置文件、SSO 会话或 `aws sts assume-role`）来运行这些 WAF CLI 命令，而不是长期存在的 IAM 用户访问密钥。
- **监控配置更改。** 您应该启用 `wafv2` 管理事件的 AWS CloudTrail，并在关键 Web ACL 配置更改（例如 `DeleteWebACL` 和 `UpdateWebACL` 规则删除）以及 Web ACL 的 `BlockedRequests` 和 `CountedRequests` 指标上设置 CloudWatch 报警，以便检测规则更改和阻止或计数流量突然激增。
- **配置错误会导致访问。** 一个创建但从未关联的 Web ACL，或默认操作保留为 `Allow` 且没有强制规则，将过滤不到任何内容。您必须确认 Web ACL 已关联，并且其态势与预期的默认值（阻止与允许）匹配，然后才能报告设置完成。
- **保护日志目的地。** 日志可能捕获凭证和会话数据。您必须遮盖敏感字段（例如 `authorization` 头和 `cookie`），并且必须在日志目的地（CloudWatch Logs、Amazon S3 或 Amazon Data Firehose）上启用静态加密。
- **头伪造风险。** 任何转发到源站的 `x-amzn-waf-*` 信号都可以被传入伪造。当转发信号或客户端 IP 时，您必须添加传入头移除规则（参见移除传入 WAF 头之前信任它们）。

## 其他资源

- [AWS WAF 开发者指南](https://docs.aws.amazon.com/waf/latest/developerguide/waf-chapter.html)
- [AWS WAF 工作原理（AWS WAF 开发者指南）](https://docs.aws.amazon.com/waf/latest/developerguide/how-aws-waf-works.html)
- [AWS WAF 定价](https://aws.amazon.com/waf/pricing/)
