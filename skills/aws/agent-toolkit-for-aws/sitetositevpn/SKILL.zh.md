---
name: sitetositevpn
description: 配置 AWS 站点到站点 VPN：在本地网络和 VPC 之间创建 IPsec VPN 连接，选择目标网关（虚拟私有网关、传输网关或 AWS 云 WAN），选择静态或动态（BGP）路由，调整隧道带宽（标准 1.25 Gbps 或大型 5 Gbps），通过 VPN 集中器连接多个站点，应用客户网关设备配置，使连接高度可用，并使用 CloudWatch 监控隧道。适用于用户希望通过加密隧道连接数据中心或分支机构到 AWS、选择路由交换方式、扩展吞吐量、整合站点或诊断故障隧道的情况。根据任务需求，参考正确的每项操作步骤。不适用于 AWS Direct Connect（其独立服务）、为单个远程用户提供的客户端 VPN、VPN 附加的传输网关端（传输网关技能）或 Route 53 DNS 工作场景。
---

# AWS 站点到站点 VPN

## 概述

AWS 站点到站点 VPN 的配置领域知识，这是一个托管服务，用于在本地网络和 AWS 之间建立加密的 IP 安全 (IPsec) 连接。涵盖路由决策（静态与动态（BGP）路由）、按正确顺序创建连接及其依赖资源、调整隧道带宽、通过 VPN 集中器整合多个站点、应用客户网关设备配置、构建高可用性方案以及监控和排错隧道。

这项技能是一个路由器。每个客户任务都映射到 `references/` 下面的一个流程文件。在采取行动之前，请完整阅读匹配的参考文件，然后遵循其约束条件和步骤。参考文件是自包含的：每个文件都包含自己的决策表、约束条件、流程和排错说明。

连接时使用 AWS MCP 服务器执行命令（沙盒执行、审计日志记录、可观察性）。否则，回退到 AWS CLI。站点到站点 VPN 是一个区域服务：传递与 VPC 或传输网关连接终止区域匹配的 `--region {region}`。

## 您需要哪个站点到站点 VPN 任务？

| 目标 | 参考 |
| --- | --- |
| 在创建连接之前，在静态和动态（BGP）路由之间进行选择 | [选择静态或动态路由](references/choosing-static-or-dynamic-routing.md) |
| 从本地网络创建到 VPC 的加密 VPN 连接 | [创建站点到站点 VPN 连接](references/creating-a-site-to-site-vpn-connection.md) |
| 选择标准（1.25 Gbps）或大（5 Gbps）的隧道带宽 | [选择隧道带宽](references/choosing-tunnel-bandwidth-standard-or-large.md) |
| 通过一个共享连接连接 25 个或更多低带宽站点 | [使用 VPN 集中器连接多个站点](references/connecting-many-sites-with-a-vpn-concentrator.md) |
| 配置本地客户网关设备 | [应用客户网关设备配置](references/applying-the-customer-gateway-device-configuration.md) |
| 使连接在隧道维护和设备故障时保持可用 | [使连接具有高可用性](references/making-a-connection-highly-available.md) |
| 检测到下线隧道并找出原因 | [监控和排错隧道](references/monitoring-and-troubleshooting-tunnels.md) |

## 路由注意事项

- **在构建之前决定路由。** 静态与动态的决策会影响客户网关、故障转移行为以及客户是否可以控制哪些路由进入其网络。在创建连接之前运行选择静态或动态路由参考，这样客户就不必重新创建连接来更改路由类型。
- **目标网关几乎控制所有内容。** 虚拟私有网关在一个 VPC 中终止 VPN。传输网关面向多个 VPC，并且是唯一支持大（5 Gbps）隧道、等价多路径（ECMP）带宽聚合、IPv6 客户网关和 VPN 集中器的目标。网关选择在创建参考中，并由带宽和集中器参考再次引用，因为选择虚拟私有网关会关闭这些选项。
- **带宽调整与集中器。** 两者都按相反方向扩展容量。大隧道为单个连接提供更高的吞吐量（每个隧道高达 5 Gbps）；集中器为许多低带宽站点提供共享的 5 Gbps 连接，这样每个站点都不需要自己的全带宽连接。根据客户是有一个高吞吐量站点还是多个小站点来匹配参考。
- **AWS 端与设备端。** 创建连接和下载配置在 AWS 端进行；应用该配置在客户的本地设备上进行，AWS 从不接触该设备。应用客户网关设备配置参考是设备端指导，而不是 AWS 端步骤。
- **监控是一项独立的任务。** 检测和诊断下线隧道（CloudWatch 指标、警报和 VPN 日志）是监控参考，与构建连接是分开的。

## 其他资源

- [AWS 站点到站点 VPN 用户指南](https://docs.aws.amazon.com/vpn/latest/s2svpn/VPC_VPN.html)
- [AWS 站点到站点 VPN 产品页面](https://aws.amazon.com/vpn/site-to-site-vpn/)
- [AWS VPN 定价](https://aws.amazon.com/vpn/pricing/)
