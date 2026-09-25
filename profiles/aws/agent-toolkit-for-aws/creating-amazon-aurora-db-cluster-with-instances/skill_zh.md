# 创建 Amazon Aurora DB 集群及实例

## 概述

创建完整的 Amazon Aurora 数据库设置的专业知识，包括集群创建、实例配置和通过 AWS Secrets Manager 进行管理密码配置。支持 Aurora MySQL 和 Aurora PostgreSQL 引擎。

## 创建带有实例的 Aurora 集群

要创建一个完全配置的 Aurora 数据库集群并附加实例，请严格按照以下步骤操作。
参见 [Aurora 集群创建步骤](references/create-amazon-aurora-db-cluster-with-instances.md)。

该步骤首先创建一个空的 Aurora 集群，然后添加一个数据库实例使其可查询。它使用 AWS Secrets Manager 进行密码管理，并包含适当的状态监控和重试逻辑。

## 故障排除

### 集群创建失败

验证引擎版本是否在您的区域受支持，并且您是否有足够的权限进行 RDS 和 Secrets Manager 操作。

### 实例创建失败

检查实例类别是否与 Aurora 引擎兼容，并且在您的区域可用性区域中可用。

### 创建时间长

Aurora 集群和实例的创建可能需要 10-20 分钟。对于 Aurora 资源，延长等待时间是正常的。
