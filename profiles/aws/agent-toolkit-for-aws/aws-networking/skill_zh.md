# AWS 网络服务

## 概述

将网络请求路由到正确的服务特定技能。涵盖 DNS 和内容交付、混合连接以及网络安全（Web 应用防火墙和 DDoS 保护）等 7 个服务。其他 AWS 网络服务（VPC 基础、负载均衡、端点、PrivateLink、API Gateway 等）不在此路由器范围内（见步骤 6）。

**最佳搭配** [AWS MCP 服务器](https://docs.aws.amazon.com/aws-mcp/) — 支持沙盒执行、审计日志和企业控制。所有指南也适用于标准 AWS CLI 访问。

## 如何使用此技能

1. 将用户的请求与下方的 **技能路由表** 进行匹配。基于含义而非精确措辞进行匹配。
2. **如果请求匹配多个技能**，使用跨服务概念表确定请求目标层级，然后路由到拥有该层级的技能。
3. **如果仍然模糊**，提出一个澄清问题："您是要设置连接，还是控制/过滤现有流量？"
4. 加载目标技能：如果 AWS MCP 服务器可用，使用 `aws___retrieve_skill(skill_name="<skill>")`；否则从此仓库的 `skills/<skill>/SKILL.md` 获取技能文档。
5. **如果请求涉及多个这些技能**，按依赖顺序路由到每个技能。当路由到面向互联网的服务（`cloudfront`）时，也路由到 `shieldadvanced` 进行 DDoS 保护，并路由到 `waf` 进行 L7 过滤（AWS WAF 附着于 CloudFront、应用负载均衡器、API Gateway 和 AppSync），如果用户尚未解决 L7 过滤和 DDoS 保护。当路由到连接技能（`directconnect`、`sitetositevpn`、`transitgateway`）时，确认传输加密是否已解决（Direct Connect 的 MACsec、VPN 的 IPsec、Transit Gateway 的跨区域对等加密）。当请求涉及自定义域名或 `cloudfront` 上的 TLS 时，请注意 ACM 证书配置是实施的一部分。当路由到 `cloudfront` 用于面向 Web 的分发时，请注意目标技能应通过 CloudFront 响应头策略处理安全响应头（CSP、HSTS、X-Frame-Options、X-Content-Type-Options），包括管理的 `SecurityHeadersPolicy`。目标技能处理配置。
6. **如果请求是技能路由表中未包含的 AWS 网络任务**（例如 VPC 子网或路由表、安全组、负载均衡器、VPC 端点、PrivateLink 或 API Gateway），告知用户该服务在此技能集中不可用，而不是路由到最接近列出的技能。此技能集不涵盖所有 AWS 网络服务。
7. 此技能进行分诊——不进行实施。不要仅凭此技能回答特定服务的配置问题。

## 连接与安全

| 维度 | 连接 | 安全 |
| --- | --- | --- |
| **回答** | 流量能否到达目的地？ | 流量是否应被允许？ |
| **失败症状** | 超时、无法到达、黑洞 | 拒绝、否认、丢弃 |
| **依赖性** | 独立于策略——路径存在或不存在 | 假设连接存在——只能过滤可达流量 |
| **粒度** | 影响路径上的所有流 | 通过匹配条件针对特定流进行目标 |

## 技能路由表

| 技能 | 选择时机... |
| --- | --- |
| `transitgateway` | 连接超过两个 VPC 或本地网络（在中心）、路由分割、跨账户/跨区域大规模连接、集中出站/检查、组播 |
| `directconnect` | 专用私有连接到本地——一致延迟、高吞吐量、MACsec 加密、LAGs、Direct Connect Gateway 用于多 VPC、SiteLink 用于站点到站点绕过、生产混合工作负载 |
| `sitetositevpn` | 通过互联网的加密 IPsec 隧道——快速设置、DX 备份、静态或 BGP 路由、通过 Global Accelerator 主干加速选项、标准或大型隧道带宽 |
| `route53` | DNS 管理（公共/私有区域、记录）、健康检查、路由策略（加权、故障转移、地理、延迟）、域名注册、Resolver（混合 DNS 转发）、DNS 防火墙、Route 53 配置文件、全局 Resolver |
| `cloudfront` | 缓存、边缘 TLS 终止、源保护（OAC）、自定义域名、缓存策略/行为、签名 URL、CloudFront 函数、观众 mTLS、VPC 源、多租户分发 |
| `waf` | Web 应用防火墙（L7）——CloudFront/ALB/API Gateway/AppSync 上的 Web ACL、AWS 管理规则、基于速率的规则用于 HTTP 洪水、IP/地理匹配、Bot 控制、欺诈控制（账户接管/创建），用于保护 Web 应用和 API 免受利用、机器人攻击和凭证注入 |
| `shieldadvanced` | 面向互联网资源的 L3/L4 DDoS 保护、通过 WAF 自动应用层（L7）缓解、基于健康的检测、Shield 响应团队访问和 DDoS 成本保护信用 |

## 跨服务概念

相同概念，不同层级对应不同服务。使用这些概念来消除歧义，当技能路由表匹配多个技能时。

### 过滤/阻止

当用户说 "阻止"、"拒绝"、"过滤" 或 "限制流量" 时使用——确定过滤操作发生的层级。

| 层级 | 服务 | 过滤条件 | 技能 |
| --- | --- | --- | --- |
| L7 (HTTP/HTTPS, Web 应用和 API) | AWS WAF | HTTP 请求属性、AWS 管理规则、基于速率和机器人规则、IP/地理匹配 | `waf` |
| L3/L4 (DDoS 容量/状态耗尽) | Shield Advanced | 面向互联网资源的网络/传输层 DDoS 洪水 | `shieldadvanced` |
| DNS (解析) | Route 53 DNS 防火墙 | 域名模式——阻止解析，而非流量 | `route53` |

当路由到 `waf` 或 `cloudfront` 用于面向互联网的 API 或网站时，将 WAF 基于速率的规则视为默认保护措施，而不仅限于用户询问时：请注意目标技能应添加 WAF 基于速率的规则以限制每个客户端的请求量——目标技能实现它。

### 日志/可见性

当用户说 "日志"、"可见性"、"什么被阻止了" 或 "我能看到流量吗" 时使用——确定要检查的日志源。

| 需要查看的内容 | 服务 | 日志类型 | 技能 |
| --- | --- | --- | --- |
| VPC 的 DNS 查询 | Route 53 Resolver | 查询日志 | `route53` |
| 被阻止/允许的 HTTP 请求 | AWS WAF | Web ACL 日志（S3、CloudWatch Logs 或 Kinesis Data Firehose） | `waf` |
| DDoS 事件和攻击详情 | Shield Advanced | CloudWatch 指标、DDoS 事件检测 | `shieldadvanced` |
| 边缘/CDN 请求访问 | CloudFront | 标准日志（S3）、实时日志（Kinesis Data Streams） | `cloudfront` |
| 隧道状态和流量 | 站点到站点 VPN | 隧道遥测、CloudWatch 指标 | `sitetositevpn` |

当路由到这些服务中的任何一个时，提醒用户启用相应的日志（上表）以实现安全可见性和事件响应——目标技能实现它。这些日志可能包含敏感数据（请求查询字符串、DNS 查询中的内部主机名），因此还提醒用户日志目标（S3、CloudWatch Logs、Kinesis Data Firehose 或 Kinesis Data Streams）必须启用静态加密并限制授权人员访问——目标技能实现它。

### 流量转移

当用户说 "转移流量"、"蓝绿"、"故障转移"、"金丝雀" 或 "加权路由" 时使用——确定粒度和哪个服务控制它。

| 粒度 | 服务 | 机制 | 技能 |
| --- | --- | --- | --- |
| DNS 层级（全局） | Route 53 | 加权、故障转移、地理位置、延迟路由 | `route53` |
| 边缘 (HTTP) | CloudFront | 源故障转移、源组 | `cloudfront` |

## 安全注意事项

这些服务涉及安全，因此在路由时无论将哪个技能交给用户，都要提出相关风险和控制——目标技能实现控制：

| 风险 | 目标技能应解决的控制 | 技能 |
| --- | --- | --- |
| 传输中未加密流量 | MACsec (`directconnect`)、IPsec 隧道 (`sitetositevpn`)、跨区域对等加密 (`transitgateway`)、TLS 终止和观众 mTLS (`cloudfront`) | `directconnect`, `sitetositevpn`, `transitgateway`, `cloudfront` |
| 面向互联网资源缺少 DDoS 保护 | Shield Advanced L3/L4 保护加上 WAF L7 缓解 | `shieldadvanced`, `waf` |
| Web/API 利用、机器人、请求洪水 | WAF Web ACL、AWS 管理规则和基于速率的规则；应用层输入验证（请求体大小限制、模式验证）；安全响应头 | `waf`, `cloudfront` |
| 过度宽松的过滤规则 | 最小权限 DNS 防火墙域名阻止 | `route53` |
| 服务资源权限过高的 IAM 策略 | 最小权限 IAM 角色限制到特定资源和操作；避免 `FullAccess` 管理策略和 `Action: *`；优先使用 IAM 角色具有临时凭证（实例配置文件、IRSA、任务角色、`sts assume-role`）而非具有长期访问密钥的 IAM 用户 | 所有 |
| 硬编码凭证和共享密钥 | 在支持的情况下让 AWS 自动生成密钥（例如 Site-to-Site VPN 预共享密钥），或将客户管理的密钥存储在 AWS Secrets Manager 而非硬编码 | `sitetositevpn`, `directconnect` |
| 跨服务资源策略中的混淆代理 | 在 S3 存储桶策略、KMS 密钥策略和日志目标资源策略（CloudFront OAC、日志发送到 S3/CloudWatch Logs/Kinesis）中包含 `aws:SourceArn` 和/或 `aws:SourceAccount` 条件键，以便只有预期资源和账户可以调用它们 | `cloudfront`, `waf`, 所有 |
| 事件响应可见性不足 | 启用日志表中的服务日志，并在日志目标上启用静态加密和限制访问 | 所有 |
| 控制平面变更没有审计记录或警报 | 启用 AWS CloudTrail 审计控制平面 API 调用（记录、规则、策略和防火墙变更），并在安全相关事件（Shield Advanced DDoS 检测、WAF 阻止/计数峰值、意外的规则或记录修改）上设置 CloudWatch 闹钟；将接收警报通知的 SNS 主题限制为授权人员，并在这些主题上启用静态加密（SSE-KMS），因为通知可能包含敏感事件详情 | 所有 |

对于权威指南，请将用户指向 [AWS Well-Architected Framework Security Pillar](https://docs.aws.amazon.com/wellarchitected/latest/security-pillar/) 和目标技能的特定服务安全文档。
