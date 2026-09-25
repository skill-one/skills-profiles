# AWS Transit Gateway

## 概述

AWS Transit Gateway 配置领域的专业知识，它是区域网络中心，通过单个路由器连接多个 VPC 和本地网络，而不是通过点对点连接的网状结构。涵盖构建中心、连接 VPC、使用路由表分割流量、集中出站和检查、使用 AWS Network Firewall 进行东西向检查、通过 Site-to-Site VPN 和 Direct Connect 实现混合连接、跨区域对等连接、从 VPC 对等连接网迁移以及 IP 组播。

这项技能是一个路由器。每个客户任务都映射到 `references/` 下面的一个流程文件。在采取行动之前，请完整阅读匹配的参考文档，然后遵循其约束条件和步骤。参考文件是自包含的：每个文件都包含自己的决策表、约束条件、流程和故障排除说明。

连接时（沙盒执行、审计日志、可观察性）使用 AWS MCP 服务器执行命令。否则，回退到 AWS CLI。所有 CLI 操作都需要最小权限、临时凭证（通过 AWS STS 或 AWS IAM Identity Center / SSO 假设的 IAM 角色），永远不会使用长期有效的 IAM 用户访问密钥。传输网关是区域资源：在每个包含中心的区域中运行每个 `aws ec2` 传输网关命令。

## 您需要哪个 Transit Gateway 任务？

| 目标 | 参考 |
| --- | --- |
| 创建区域中心并将 VPC 连接到它 | [创建 Transit Gateway 并连接 VPC](references/creating-a-transit-gateway-and-attaching-vpcs.md) |
| 隔离一些 VPC，同时允许其他 VPC 共享服务 | [使用路由表分割流量](references/segmenting-traffic-with-route-tables.md) |
| 通过一个经过检查的出站 VPC 发送所有分支流量 | [集中出站和检查](references/centralizing-egress-and-inspection.md) |
| 使用 AWS Network Firewall 检查 VPC 之间的流量 | [使用 Network Firewall 检查东西向流量](references/inspecting-east-west-traffic-with-network-firewall.md) |
| 通过 Site-to-Site VPN 或 Direct Connect 连接到本地网络 | [连接本地网络](references/connecting-on-premises-networks.md) |
| 通过 AWS 网络在两个区域的传输网关之间建立连接 | [跨区域对等连接传输网关](references/peering-transit-gateways-across-regions.md) |
| 在不丢失流量的情况下从 VPC 对等连接迁移 | [从 VPC 对等连接迁移](references/migrating-from-vpc-peering.md) |
| 在连接的 VPC 之间分发 IP 组播 | [路由组播流量](references/routing-multicast-traffic.md) |

## 路由注意事项

- **在构建之前决定分割。** “默认路由表关联”和“默认路由表传播”默认情况下是开启的，这会将每个连接都连接到一个开放的网状结构中。如果客户计划隔离环境，创建参考会提前禁用默认设置，并转交给分割参考。在开放的中心上重新构建隔离是一个重新架构的过程。
- **南北出站与东西向检查。** 集中出站通过中央 VPC 将分支流量发送到互联网。东西向检查保持分支之间的流量内部，并强制其通过防火墙。它们看起来相似，但使用不同的路由表配方。根据客户实际流量方向匹配参考。
- **检查的设备与网关负载均衡器。** 原始第三方设备和网关负载均衡器（GWLB）端点是达到相同目标的两种路径。对于新设计，推荐使用 GWLB。两者都位于集中出站参考中；设备模式和 GWLB 端点路由表条目不同，参考涵盖了每个。
- **设备模式需要状态跨可用区检查，但有权衡。** 设备模式将每个流保持在单个可用区的设备上，以便请求和响应不会拆分。它还禁用了该连接的跨可用区故障转移，因此检查设计必须与基于健康检查的故障转移配对。出站和东西向参考都包含这一点。
- **传输网关侧与 Direct Connect 侧。** 连接本地网络的参考涵盖了传输网关侧：Site-to-Site VPN 连接选项、路由传播和等价多路径（ECMP）。Direct Connect 网关和虚拟接口设置属于单独的 `directconnect` 技能。不要在这里重述 Direct Connect 侧。

## 安全注意事项

传输网关是许多 VPC 和本地网络的中枢路由点，因此这里的配置错误会影响每个连接的网络。无论具体任务如何，都必须应用这些控制措施；每个按任务划分的参考都包含详细信息。

- 您必须启用 Transit Gateway 流量日志，以便在整个中心进行流量可见性、审计和事件响应，并且必须启用目标（CloudWatch 日志组的 KMS 密钥或 S3 存储桶的 SSE-KMS）的静态加密。
- 当 KMS 密钥加密流量日志目标（CloudWatch 日志组或 S3 存储桶）或 CloudTrail 目标时，您必须使用条件密钥（`aws:SourceArn`、`aws:SourceAccount` 和 `kms:ViaService`）限制 KMS 密钥策略的范围，以便只有预期账户和服务中的特定日志组、存储桶或跟踪才能使用该密钥，防止跨账户或跨服务滥用。
- 您应该为传输网关管理应用最小权限 IAM，避免服务通配符和 FullAccess 策略，限制谁可以创建连接、修改路由表以及更改关联或传播。
- 您应该确保 Site-to-Site VPN 隧道使用强加密（例如 AES-256-GCM 与 IKEv2），并启用隧道日志记录到 CloudWatch Logs（使用加密的 KMS 密钥），以保护敏感连接状态和 IKE 协商细节免受未经授权的访问（请参阅连接本地网络参考）。
- 您必须将配置错误的传输网关路由表视为安全风险，因为错误的关联或传播可能会暴露跨环境的工作负载（请参阅分割流量参考）。
- 您必须启用 AWS CloudTrail 以检测对传输网关路由表、关联和传播的未经授权的更改，必须启用 CloudTrail 目标的静态加密（KMS 密钥），并使用 AWS Config 规则检测与预期设计的偏差。

## 其他资源

- [AWS Transit Gateway 指南](https://docs.aws.amazon.com/vpc/latest/tgw/what-is-transit-gateway.html)
- [AWS Transit Gateway 产品页面](https://aws.amazon.com/transit-gateway/)
- [AWS Transit Gateway 定价](https://aws.amazon.com/transit-gateway/pricing/)
