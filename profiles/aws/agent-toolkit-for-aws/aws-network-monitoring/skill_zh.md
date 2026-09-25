# AWS 网络监控

## 概述

安装和配置 Amazon CloudWatch Network Flow Monitor 在 EC2 实例上的代理的领域专业知识。涵盖 IAM 权限设置、通过 SSM 分发器或命令行安装代理、代理激活、验证和故障排除。

Network Flow Monitor 代理是轻量级软件，它将性能指标（延迟、丢包率）发布到 Network Flow Monitor 后端，从而能够监控工作负载之间的网络路径健康状况。

**最佳搭配** [AWS MCP 服务器](https://docs.aws.amazon.com/aws-mcp/) — 能够直接运行 SSM 命令、附加 IAM 策略和验证代理状态。所有指南也适用于标准 AWS CLI 访问。

## 路由

| 用户需求 | 操作 |
|-----------|--------|
| 在 EC2 上安装 Network Flow Monitor 代理 | 阅读 [agent-install-ec2.md](references/agent-install-ec2.md) |
| 配置 Network Flow Monitor 代理的 IAM | 阅读 [agent-permissions.md](references/agent-permissions.md) |
| 故障排除 Network Flow Monitor 代理（403、无指标、连接性） | 阅读 [troubleshooting.md](references/troubleshooting.md) |
| 跨多个领域 | 首先阅读最具体的参考，然后根据需要咨询其他内容 |

## 文件

| 文件 | 内容 |
|------|---------|
| [agent-install-ec2.md](references/agent-install-ec2.md) | 通过 SSM 分发器进行端到端 Network Flow Monitor 代理安装、激活、验证 |
| [agent-permissions.md](references/agent-permissions.md) | Network Flow Monitor 代理指标发布的 IAM 策略设置 |
| [troubleshooting.md](references/troubleshooting.md) | Network Flow Monitor 代理问题的错误 → 原因 → 修复（HTTP 403、缺失指标、连接性） |

## 支持的版本

有关支持的 Linux 发行版、内核版本和架构，请参阅 [AWS 文档](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/CloudWatch-NetworkFlowMonitor-agents-versions.html)。Windows 不受支持。

## 安全注意事项

- **最小权限 IAM**：仅附加 `CloudWatchNetworkFlowMonitorAgentPublishPolicy` 用于发布指标和 `AmazonSSMManagedInstanceCore` 用于 SSM 管理。不要使用 `*FullAccess` 策略。
- **私有子网**：当实例位于私有子网时，优先使用 SSM 的 VPC 端点（`com.amazonaws.<region>.ssm`, `.ssmmessages`, `.ec2messages`）而不是 NAT 网关，以保持流量在 AWS 网络上。
- **凭证存储**：切勿在实例中嵌入 AWS 凭证；发布策略必须附加到实例角色，而不是配置为静态密钥。
- **审计跟踪**：确保在账户中启用 CloudTrail，以便在代理设置过程中记录 SSM `SendCommand` 调用和 IAM `AttachRolePolicy` 操作，以便进行安全调查。
- **参考资料**：[CloudWatch Network Flow Monitor 安全](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/CloudWatch-NetworkFlowMonitor-security.html)，[IAM 最佳实践](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html)
