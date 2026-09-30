---
name: launching-ec2-instance-with-best-practices
description: 启动一个具有安全、经济高效的默认设置的 EC2 实例，包括 AMI 选择、可突发实例尺寸、最小权限 IAM 角色、加固安全组、加密 EBS 卷和全面标记。在遵循 AWS 安全和成本优化最佳实践的情况下部署新 EC2 实例时使用。
---

# 使用最佳实践启动 EC2 实例

## 概述

针对安全、成本效益和运维最佳实践进行优化的合理默认值领域专业知识，用于启动 EC2 实例。涵盖 AMI 选择、实例类型推荐、网络配置、IAM 角色创建、安全组加固、存储配置、标签策略和启动后验证。

## 启动 EC2 实例

要启动具有最佳实践默认值的完全配置 EC2 实例，请严格按照流程操作。
参见 [EC2 实例启动流程](references/launch-ec2-instance-with-best-practices.md)。

该流程处理：

- 基于工作负载类型和环境设置智能默认值
- 网络验证（VPC、子网、公网/私网部署）
- 兼容架构的 AMI 选择
- 为所需 AWS 服务访问设置最小权限 IAM 角色
- 具有最小端口暴露的加固安全组
- 环境适用加密 gp3 存储
- 用于成本跟踪和组织的全面标签
- 启动后验证和连接说明

## 故障排除

### 实例容量不足

尝试不同的可用区或实例类型（例如，使用 t3a 而不是 t3）。参见 [启动流程](references/launch-ec2-instance-with-best-practices.md) 中的完整故障排除指南。

### 实例立即终止

使用 `aws ec2 get-console-output` 检查控制台输出。验证 EBS 卷大小是否足够，并且 AMI 与实例类型兼容。

### 无法通过 SSH 连接

验证安全组允许从您的 IP 进行 SSH，密钥文件权限为 `400`，并且实例正在运行。考虑使用 AWS Systems Manager Session Manager 作为替代方案。
