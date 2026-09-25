# Apache Flink 管理服务

## 概述

针对 Amazon 管理服务 for Apache Flink (MSF) 上 Apache Flink 应用的领域专业知识。涵盖开发、KPU 资源管理、连接器、状态管理、监控、IaC 部署和版本迁移。

连接时，使用 AWS MCP 服务器提供的可用工具执行命令——它提供沙盒执行、审计日志记录和可观察性。当 MCP 服务器不可用时，根据需要回退到 AWS CLI 或 shell。

## 一般指导

开始之前，确保您对用户角色、用例和需求有清晰的理解：

STOP：在继续之前，确定用户的背景和用例：

- 他们是 Flink 的新手吗？是 Apache Flink 管理服务的新手吗？
- 他们熟悉 Java 开发吗？
- 用例是否复杂包含大量业务逻辑？还是简单且声明式的？

这将决定如何组织项目，以及是否使用 Flink Table API 或 DataStream API。通常，假设使用 DataStream API。

### 新应用的示例工作流

```
1. 用户请求构建一个 Flink 应用
2. 确认用户的目标和用例
3. READ [best-practices.md](references/best-practices.md)
4. READ [dependency-management.md](references/dependency-management.md)
5. READ 相关的连接器指南（例如 [kinesis-connector-guide.md](references/kinesis-connector-guide.md)）
6. 根据加载的指导生成代码
7. 与最佳实践进行验证
8. READ [environment-setup.md](references/environment-setup.md) 通过 [environment-setup.md](references/environment-setup.md)
9. 本地编译和测试
```

### 一般问题的示例工作流

```
1. 用户询问将数据实时传递到 Iceberg 的问题
2. 确认用户的目标和用例
3. READ [best-practices.md](references/best-practices.md)
4. READ [iceberg-connector-guide.md](references/iceberg-connector-guide.md)
5. 根据需要读取其他参考文件
6. 使用加载的指导回答问题
```

## 参考文件

- 您必须使用此技能及其参考文件来回答这些主题的任何问题。
- 当问题涉及 Apache Flink、Apache Flink 管理服务、KPU 尺寸、Flink 监控、部署、迁移、实时分析或使用 Flink 的 Iceberg/LakeHouse 流时，**绝对不要**从训练知识或通过搜索通用 AWS 文档来回答
  - 您必须在采取其他步骤之前加载以下相关的参考文件。
  - 参考文件包含 MSF 特定的细节（阈值、统计数据、命名空间、约束），这些细节与通用 Flink 指导不同，并且对于正确回答是必需的。

| 目标 | 参考 | 加载时间 |
|------|-----------|-------------|
| 最佳实践 | [best-practices.md](references/best-practices.md) | **始终** 在编写代码之前 |
| Maven 依赖项 | [dependency-management.md](references/dependency-management.md) | 新项目或添加连接器 |
| 本地开发环境 | [environment-setup.md](references/environment-setup.md) | 基于 Docker 的本地开发 |
| MSF 架构 | [msf-overview.md](references/msf-overview.md) | KPU 模型和服务约束 |
| MSF 约束和模式 | [msf-constraints-and-patterns.md](references/msf-constraints-and-patterns.md) | MSF 与自管理的 Flink、服务级与应用级配置分离、MSF 特定的资源/网络/存储限制、常见的 MSF 模式 |
| 配额、ENI 规划、MSF 与 EMR、源/接收器选择 | [foundation-operations.md](references/foundation-operations.md) | 容量规划、服务选择、架构设计、CLI/IAM/CloudWatch 标识符消除 |
| IAM 执行角色、信任策略、操作前缀、服务主体 | [foundation-operations.md](references/foundation-operations.md) | 为 MSF 编写 IAM 策略——涵盖 `kinesisanalytics:`（无 v2）操作前缀、`kinesisanalytics.amazonaws.com`（无 v2）信任主体，以及 v2/非 v2 断开连接，这是最常见导致权限和 AssumeRole 失败的原因 |
| Flink 2.x 迁移 | [flink-2x-migration.md](references/flink-2x-migration.md) | 版本升级、状态兼容性 |
| KPU 尺寸 | [resource-optimization.md](references/resource-optimization.md) | 正确的尺寸、性能诊断、扩展 |
| 运行应用上的扩展决策 | [scaling-decisions.md](references/scaling-decisions.md) | 在飞行中扩展矩阵、扩展变化对成本/内存的影响、自动扩展行为、反模式 |
| 成本估算 | [pricing-calculator.md](references/pricing-calculator.md) | 预算规划、尺寸到成本映射、优化杠杆 |
| 应用生命周期操作 | [application-lifecycle.md](references/application-lifecycle.md) | 启动/停止、部署代码、回滚、快照生命周期、运行时属性、删除 |
| 重启循环诊断 | [first-fault-isolation.md](references/first-fault-isolation.md) | 失败的应用/重启、找到原始故障与循环维持者、Flink 仪表板实时诊断 |
| Checkpoint 调整 | [checkpoint-tuning.md](references/checkpoint-tuning.md) | Checkpoint 对 KPU 内存和 CPU 的影响、频率与网络带宽的权衡、Checkpoint 持续时间超过间隔、在 Checkpoint 期间 OOM/GC |
| 作业图设计 | [job-graph-architecture.md](references/job-graph-architecture.md) | 性能问题、拆分作业 |
| 作业图反模式 | [job-graph-anti-patterns.md](references/job-graph-anti-patterns.md) | 数据倾斜检测和缓解、单体作业反模式、高扇出反模式、移除多个混洗、何时拆分大型应用 |
| 监控和警报 | [monitoring-and-metrics.md](references/monitoring-and-metrics.md) | CloudWatch 仪表板、警报、指标 |
| 日志记录 | [logging-configuration.md](references/logging-configuration.md) | Log4j2、CloudWatch Logs 设置 |
| Kinesis 连接器 | [kinesis-connector-guide.md](references/kinesis-connector-guide.md) | Kinesis 源和接收器构建器、轮询配置和限制 (`READER_EMPTY_RECORDS_FETCH_INTERVAL`, `SHARD_GET_RECORDS_MAX`, `ReadProvisionedThroughputExceeded`, `LimitExceededException`), 旧连接器迁移 |
| Kinesis 增强型扇出 (EFO) | [kinesis-efo-guide.md](references/kinesis-efo-guide.md) | 何时使用 EFO 而不是轮询、EFO 源配置、消费者生命周期 (`JOB_MANAGED` vs `SELF_MANAGED`), 并行度与分片数量、IAM 权限、故障排除 |
| Iceberg 集成（写入 API、分布模式、分区） | [iceberg-connector-guide.md](references/iceberg-connector-guide.md) | Iceberg 写入 API（追加、更新、动态）、分布模式（NONE/HASH/RANGE）、CoW vs MoR、读取模式、分区、DDL。**不包含目录选择或维护方法**——对于这些，加载 `iceberg-tuning-and-operations.md`。 |
| Iceberg 调整、操作、目录选择、维护 | [iceberg-tuning-and-operations.md](references/iceberg-tuning-and-operations.md) | 提供 S3 表的维护方法、Glue + Glue 自动压缩，以及 Glue + Flink 嵌入式维护（使用 JDBC 锁）用于目录选择问题；小文件问题和缓解措施；Flink TableMaintenance API、提交后维护、锁工厂；IcebergSink 监控、反模式。 |
| CDC 连接器 | [cdc-connector-guide.md](references/cdc-connector-guide.md) | MySQL、PostgreSQL、Oracle、SQL Server、MongoDB CDC |
| IaC 和部署 | [iac-and-deployment.md](references/iac-and-deployment.md) | CloudFormation、CDK、Terraform、两阶段部署 |
| 序列化 | [serialization-guide.md](references/serialization-guide.md) | POJO、Avro、Kryo 指导 |
| 状态管理 | [state-management.md](references/state-management.md) | TTL、状态类型、迁移安全性 |

## 其他资源

- [GitHub Issues](https://github.com/awslabs/managed-service-for-apache-flink-agent-steering-files/issues)
