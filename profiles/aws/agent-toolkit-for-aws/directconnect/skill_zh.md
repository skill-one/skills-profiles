# AWS Direct Connect

## 概述

AWS Direct Connect 配置领域的专业知识，该服务为客户在其数据中心或托管中心与 AWS 之间提供私有、一致的网络安全连接，而不是通过公共互联网路由。涵盖选择连接模型和完成交叉连接、创建虚拟接口和启用边界网关协议 (BGP)、通过 Direct Connect 网关访问多个 VPC、在传输中加密流量、使连接具有弹性、管理链路聚合组、SiteLink，以及从虚拟私有网关迁移到 transit gateway。

这项技能是一个路由器。每个客户任务都映射到 `references/` 下面的一个过程文件。在采取行动之前，请完整阅读相应的参考文件，然后遵循其约束条件和步骤。参考文件是自包含的：每个文件都包含自己的决策表、约束条件、过程和故障排除。

连接时使用 AWS MCP 服务器执行命令（沙盒执行、审计日志记录、可观察性）。否则，回退到 AWS CLI。Direct Connect 控制台是区域性的，因此请将客户的 `--region` 工作参数传递给 `aws directconnect` 命令；Direct Connect 网关是一个全局资源，但通过区域控制台视图访问。

## 您需要哪个 Direct Connect 任务？

| 目标 | 参考 |
| --- | --- |
| 选择专用、托管或链路聚合组，然后完成交叉连接 | [选择 Direct Connect 连接类型](references/choosing-a-direct-connect-connection-type.md) |
| 创建私有、公共或 transit 虚拟接口并启用 BGP | [创建虚拟接口并配置 BGP](references/creating-a-direct-connect-virtual-interface-and-configuring-bgp.md) |
| 通过 Direct Connect 网关通过一个连接访问多个 VPC | [通过 Direct Connect 网关连接多个 VPC](references/connecting-many-vpcs-through-a-direct-connect-gateway.md) |
| 使用 MACsec 或私有 IP Site-to-Site VPN 在传输中加密流量 | [在 Direct Connect 上加密流量](references/encrypting-traffic-over-direct-connect.md) |
| 使连接在故障时存活并调整故障转移速度 | [使 Direct Connect 连接具有弹性](references/making-a-direct-connect-connection-resilient.md) |
| 将连接捆绑为一个逻辑链路并管理成员 | [管理链路聚合组](references/managing-direct-connect-link-aggregation-groups.md) |
| 通过 AWS 骨干连接本地站点彼此连接 | [设置 SiteLink](references/setting-up-direct-connect-sitelink.md) |
| 从虚拟私有网关迁移到 transit gateway 而不丢失流量 | [从虚拟私有网关迁移到 transit gateway](references/migrating-direct-connect-from-a-virtual-private-gateway-to-a-transit-gateway.md) |

## 路由注意事项

- **连接模型优先。** 对于还没有连接的客户，选择连接类型的参考是入口点。它确定了专用、托管或链路聚合组，检查所选速度的位置支持，并将托管连接与托管虚拟接口区分开来，客户经常混淆这种区别。在订购任何交叉连接之前运行它，因为连接创建后端口速度不能改变。
- **连接在存在虚拟接口之前不携带流量。** 交叉连接上线后，创建虚拟接口的参考是必需的下一步。虚拟接口类型（私有、公共或 transit）决定了连接可以访问什么，并在创建时固定。巨型帧最大传输单元 (MTU) 应在创建时设置，但在私有或 transit 虚拟接口上，可以稍后更改，但会短暂中断连接。
- **一个 VPC 与多个 VPC。** 一个区域中的一个 VPC 可以通过私有虚拟接口连接到虚拟私有网关。访问多个 VPC、跨账户或跨区域是通过 Direct Connect 网关参考，它还拥有跨账户 transit gateway 提案和接受握手。
- **加密是一个独立的、有意的步骤。** Direct Connect 默认情况下在传输中不加密。加密流量的参考比较 MACsec（第 2 层，通过交叉连接）与 transit 虚拟接口上的私有 IP Site-to-Site VPN（推荐的 IPsec 路径）。当客户提到受监管的数据或加密时，请在此处路由。
- **弹性模型与故障转移速度是两个不同的问题。** 弹性参考涵盖了这两个方面：弹性工具包设置拓扑和服务级别目标，而 BGP 持续计时器调整和双向转发检测 (BFD) 设置故障转移实际收敛的速度。
- **链路聚合组作为模型与作为持续管理。** 连接类型参考在订购时引入链路聚合组作为模型选择。管理链路聚合组的参考拥有持续的成员添加/删除和最小链路行为，其中删除一个成员可能会使整个组下线。
- **迁移是顺序相关的。** 虚拟私有网关到 transit gateway 迁移参考存在是因为如果 cutover 步骤顺序错误，生产流量会丢失。将任何“我们超出了单 VPC 模型”的请求路由到此处，而不是普通的 Direct Connect 网关参考。

## 安全注意事项

Direct Connect 提供到 VPC 资源的私有连接，因此安全态势与公共互联网路径不同。将以下内容纳入每个任务：

- **默认情况下未加密。** Direct Connect 在传输中不加密流量。您必须将加密视为一个独立的、有意的步骤（MACsec 或私有 IP Site-to-Site VPN），在受监管或敏感数据跨链路传输之前进行。请参阅加密流量参考。
- **物理和托管中心安全。** 链路终止在 Direct Connect 位置或合作伙伴托管的客户设备上。您应该提醒客户，该设施的身体访问控制和合作伙伴信任是连接安全边界的一部分。
- **监控和警报。** 您应该建议在连接状态和虚拟接口 BGP 状态上设置 CloudWatch 警报，以便连接状态更改和故障触发警报，而不是依赖手动检测。
- **审计日志记录。** 您应该确认 CloudTrail 已启用并记录 `directconnect` API 调用（连接、虚拟接口和网关关联更改），以便所有配置更改都被捕获以供审计和合规。
- **CloudWatch Logs 加密。** 您应该使用 KMS 密钥对接收 Direct Connect 相关日志或警报状态数据的 CloudWatch Logs 日志组进行加密，以便敏感连接元数据在静止时得到保护。
- **最小权限 IAM。** 您必须将 `directconnect` API 操作的 IAM 权限范围到每个主体需要的具体操作和资源，并优先使用临时 IAM 凭证而不是长期 IAM 用户访问密钥。您不得在资源 `*` 上授予 `directconnect:*` 或附加任何 `*FullAccess` 管理策略；相反，将操作范围到特定资源 ARN，例如 `arn:aws:directconnect:*:*:dxcon/{connection_id}` 用于连接，以便一个受损的主体不能触摸账户中的每个 Direct Connect 资源。
- **VPC 之间的路由泄漏。** 您应该警告，宣传重叠 VPC CIDR 的超网可能导致意外 VPC-to-VPC 流量通过共享 Direct Connect 网关；通过特定前缀、分离网关或 transit gateway 黑洞路由来缓解。

## 其他资源

- [AWS Direct Connect 用户指南](https://docs.aws.amazon.com/directconnect/latest/UserGuide/Welcome.html)
- [AWS Direct Connect 中的安全 (AWS Direct Connect 用户指南)](https://docs.aws.amazon.com/directconnect/latest/UserGuide/security.html)
- [AWS Direct Connect 产品页面](https://aws.amazon.com/directconnect/)
- [AWS Direct Connect 定价](https://aws.amazon.com/directconnect/pricing/)
