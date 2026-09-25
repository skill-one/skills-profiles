# 将 RDS/Aurora 导出至 S3

## 概述

在 Apache Parquet 格式下，将 Amazon RDS 和 Aurora 数据库快照导出到 Amazon S3 的领域专业知识。涵盖完整的工作流程：快照识别或创建、IAM 角色和 KMS 加密设置、S3 存储桶准备、导出任务启动、进度监控、数据验证，以及为 Athena、Glue 和 Redshift Spectrum 等分析服务提供的导出后访问指南。

## 将 RDS 或 Aurora 快照导出至 S3

要使用适当的 IAM 角色和加密进行监控，将数据库快照导出到 S3，请严格按照程序操作。
参见 [RDS 至 S3 导出程序](references/export-rds-to-s3.md)。

## 故障排除

### 找不到数据库
验证数据库标识符的拼写、大小写和区域。对于 Aurora，请使用 `describe-db-clusters` 而不是 `describe-db-instances`。

### 不支持导出
快照导出仅支持 MySQL、PostgreSQL、MariaDB、Aurora MySQL 和 Aurora PostgreSQL。Oracle 和 SQL Server 不受支持。

### IAM 角色权限错误
确保角色信任策略允许 `export.rds.amazonaws.com` 并具有 `aws:SourceAccount` 和 `aws:SourceArn` 条件以防止混淆代理攻击，并具有 S3 PutObject 和 KMS 权限。角色创建后等待 10–15 秒以进行传播。

### 导出卡住或失败
检查导出任务状态以获取失败原因。常见原因：导出期间 S3 存储桶被删除、IAM 角色被修改或 KMS 密钥被禁用。参见 [完整程序](references/export-rds-to-s3.md) 以获取详细的故障排除信息。
