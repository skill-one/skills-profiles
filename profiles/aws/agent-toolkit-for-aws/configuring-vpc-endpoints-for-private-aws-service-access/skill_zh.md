# 配置 VPC 端点以实现私有 AWS 服务访问

## 概述

配置 VPC 端点的领域专业知识，以实现不通过互联网路由流量即可访问 AWS 服务的私有访问。涵盖由 AWS PrivateLink 驱动的网关端点（S3、DynamoDB）和接口端点（EC2、SSM、Secrets Manager 等）。

## 配置 VPC 端点

要创建和配置用于私有 AWS 服务访问的 VPC 端点，请严格按照程序操作。请参阅 [VPC 端点配置程序](references/configure-vpc-endpoints-for-private-aws-service-access.md)。

## 故障排除

### 端点不可用

检查安全组规则、子网配置以及区域中的服务可用性。

### DNS 解析问题

验证 VPC 上是否启用了 DNS 主机名和 DNS 解析，并且 DHCP 选项集具有正确的域名服务器。

### 连接超时

验证安全组规则允许 HTTPS 流量（端口 443），并且网关端点的路由表已正确配置。

### 策略限制

检查端点策略——默认策略允许所有访问，但自定义策略可能具有限制性。
