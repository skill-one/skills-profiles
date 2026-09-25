# 跨多个可用区创建可生产环境的 VPC

## 概述

创建跨多个可用区分布的可生产环境 VPC 基础设施的领域专业知识。涵盖支持 DNS 的 VPC 创建、公共和私有子网布局（自动 CIDR 计算）、互联网网关、用于高可用性出站访问的 NAT 网关、路由表配置以及遵循 AWS Well-Architected 原则的分层安全组。

## 创建可生产环境的 VPC

要创建具有公共/私有子网、NAT 网关、路由表和安全组的完全配置的多 AZ VPC，请严格按照程序进行操作。
参见 [可生产环境 VPC 创建程序](references/create-production-vpc-multi-az.md)。

关键参数：

- `vpc_name`（必需）：所有资源的名称前缀
- `region`（必需）：目标 AWS 区域
- `allowed_web_cidrs`（必需）：允许用于 Web 访问的 CIDR 块——仅当明确请求时才允许 0.0.0.0/0
- `vpc_cidr`（可选，默认 `10.0.0.0/16`）：VPC CIDR 块
- `availability_zones`（可选，默认 3）：可用区数量（2-6）
- `environment`（必需）：环境标签
- `enable_ssh_access`（可选，默认 false）：是否创建 SSH 安全组

## 故障排除

### 可用区不足

目标区域必须至少有 2 个可用的可用区。使用 `aws ec2 describe-availability-zones` 进行验证。

### NAT 网关创建延迟

NAT 网关可能需要几分钟才能变为可用状态。程序会在配置路由表之前等待其可用。

### 安全组 CIDR 警告

程序会针对 Web 访问 CIDR 的 `0.0.0.0/0` 发出警告，并建议为生产工作负载指定特定的 IP 范围，但如果明确请求，则允许使用。
