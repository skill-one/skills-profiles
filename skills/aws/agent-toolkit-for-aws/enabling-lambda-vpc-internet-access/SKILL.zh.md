---
name: enabling-lambda-vpc-internet-access
description: 通过创建NAT网关基础设施、配置公共/私有子网路由以及更新安全组，为部署在VPC子网中的AWS Lambda函数启用互联网访问。当VPC连接的Lambda函数无法访问互联网时使用。
---

# 启用 Lambda VPC 互联网访问

## 概述

关于在 VPC 私有子网中运行的 AWS Lambda 函数启用互联网访问的专业知识。VPC 中的 Lambda 函数不能接收公网 IP 地址，因此出站互联网访问需要 NAT 网关基础设施，该基础设施将私有子网的流量路由通过公共子网到互联网网关。

## 为 VPC Lambda 函数启用互联网访问

要为需要互联网访问的 Lambda 函数设置 NAT 网关基础设施并配置路由，请严格按照以下步骤操作。
请参阅 [Lambda VPC 互联网访问设置步骤](references/lambda-vpc-internet-access.md)。

## 故障排除

### NAT 网关无法工作

验证与 Lambda 子网关联的路由表是否具有指向 NAT 网关的 `0.0.0.0/0` 路由。有关详细信息，请参阅完整步骤。

### Lambda 函数超时

检查安全组出站规则是否允许必要的端口，并确保 NAT 网关和互联网网关已正确配置。

### 网络更改未生效

VPC 网络更改可能需要 1-2 分钟才能传播。在创建 NAT 网关或更新路由表后，请稍等再进行测试。

### 路由表关联问题

确认 Lambda 函数的子网已与具有指向 NAT 网关的 `0.0.0.0/0` 路由的路由表关联。
