---
name: aws-database
description: 将涉及 AWS 数据库的任何任务——选择、比较、推荐、入门或操作数据库——路由到正确的服务特定技能。使用后培训服务更新、修正限制以及关系型（Aurora、DSQL、RDS）、键值（DynamoDB）、宽列（Keyspaces）、文档（DocumentDB）、图（Neptune）、时序（Timestream）和内存/缓存（ElastiCache、MemoryDB）工作负载的决策程序，取代通用的培训数据知识。当用户描述在 AWS 上构建将存储、检索或管理数据的应用程序时，即使他们没有明确提及“数据库”，该功能也会被激活。
---

# AWS 数据库

**停止 — 请勿凭一般知识回答。** 在回答任何数据库问题时，请先根据下方的子技能注册表匹配用户请求，并遵循其流程。如果流程指示将问题转交给特定服务技能，则你必须先加载该技能，然后再提供操作指导。切勿跳过路由步骤。

AWS 数据库包含 15 种以上的全托管数据库引擎，为智能代理式 AI 和数据驱动型应用提供高性能、安全可靠的坚实基础。每个 AWS 数据库都针对特定的负载形状或数据模型进行了优化——关系型（Aurora、DSQL、RDS）、键值型（DynamoDB）、宽列型（Keyspaces）、文档型（DocumentDB）、图型（Neptune）、时序型（Timestream for InfluxDB）和内存型（ElastiCache、MemoryDB）。对于关系型工作负载，AWS 支持以下数据库：PostgreSQL（Aurora、DSQL、RDS）、MySQL（Aurora、RDS）、MariaDB（RDS）、Oracle（RDS、ODB@AWS）、SQL Server（RDS）和 Db2（RDS）。

将此技能作为与 AWS 数据库相关的任何操作或问题的入口点。它有助于将工作负载匹配到合适的 AWS 数据库服务，或将问题转交给特定服务技能以进行操作性问题或操作。

此技能在使用或不使用 AWS MCP 服务器的情况下均可工作。当可用时，推荐使用 AWS MCP 服务器进行沙盒执行和审计日志记录。

## 全局规则

1. **匹配用户语言。** 使用与用户相同的语言进行回复。默认使用非技术性解释。仅在用户展示出熟练度时（通过使用术语、说明技术角色或用技术性回答普通问题）才升级技术深度。

2. **新信息到达时修订。** 如果用户提出异议或添加新细节，请在回复前重新检查子技能注册表触发器。与 `report-issue` 触发器匹配的异议（例如，“那不对”、“是错的”、“你选错了服务”）必须路由到 `report-issue`——不要为自己之前的建议辩护或要求用户为其异议进行辩护。目标是正确答案，而不是与第一次回复的一致性。

3. **不要依赖训练数据获取事实。** AWS 数据库经常变化。在陈述定价、配额或 GA 状态之前，请先通过此技能加载的知识卡片进行验证。如果事实不在知识卡片中，请查找——优先顺序为：(a) 如果可用，使用 AWS MCP 服务器（`aws___read_documentation`、`aws___search_documentation`）；(b) 从其知识卡片中获取服务的 `llms.txt` URL 以获取结构化文档索引；(c) 指导用户访问 AWS 文档。如果用户提到知识卡片未涵盖的功能，请查找而不是猜测。

4. **核实，不要猜测。** 如果你无法从知识卡片或文档中确认事实，请说明。 “我不确定——请查看文档”比自信地给出错误答案更好。

## 此技能的工作原理

1. **找到子技能** — 将用户请求与下方的子技能注册表进行匹配。按意义匹配，而不是精确措辞。如果存在歧义，请询问：“你是要选择数据库，还是需要帮助使用已有的数据库？”**此匹配适用于每个用户消息，而不仅仅是第一条消息。** 如果后续消息匹配不同子技能的触发器（例如，用户对建议提出异议，其措辞匹配 `report-issue`），请立即重新路由——不要继续之前子技能的流程。

2. **如果子技能匹配** — 阅读 `references/{sub-skill-id}.md` 并遵循其流程。

3. **如果没有子技能匹配** — 从 `assets/` 中的知识卡片回答。如果卡片未涵盖，如果可用，则使用文档工具（`aws___search_documentation`、`aws___read_documentation`），或从其知识卡片中获取服务的 `llms.txt` URL，或指导用户访问卡片中列出的 AWS 文档 URL。这是快速获取事实的路径：已发布的单位价格、限制、GA 状态、功能确认或任何仅从卡片中即可回答的问题。不要加载服务技能来回答卡片已涵盖的快速事实。特定工作负载的成本估算不是快速事实：当用户指定服务并基于吞吐量、存储、拓扑或其他工作负载输入请求估算时，路由到 `handoff` 并加载可用服务技能。仅在提供有用信息或用户请求操作帮助时，才提供更深层次的服务技能指导。

## 子技能注册表

| ID | 名称 | 触发短语 | 路由时机 | 下一步骤 |
|----|------|-----------------|-------------------|------------|
| `select` | 数据库选择 | "哪个数据库"、"帮我选择"、"推荐"、"我应该使用什么"、"开始新项目"、"选择数据库"、"我需要数据库"、"我在构建"、"构建一个"、"如何存储"、"处理的最佳方式"、"需要支持"、"为...设计" | 用户尚未选择服务，正在比较选项，或描述工作负载/数据问题但未指定特定服务 | `handoff` |
| `handoff` | 服务转接 | "如何操作"、"配置"、"优化"、"故障排除"、"设置"、"迁移到"、"连接到"、"扩展"、"升级"、"监控"、"备份"、"恢复"、"估算成本"、"定价估算"、"我的工作负载成本"、"构建"、"创建"、"部署"、"提供"，+ 指定服务 | 用户指定了特定的 AWS 数据库服务，并有一个操作性问题、建议性问题或行动性问题，包括特定工作负载的成本估算 | — |
| `report-issue` | 报告问题 | "那不对"、"不正确"、"错误的推荐"、"你应该说过"、"缺失"、"技能是错的"、"报告这个"、"提交错误"、"报告问题" | 用户报告技能提供了不正确或不完整的指导 | — |

## 服务参考

按需加载知识卡片——仅在当前回合需要验证或陈述关于服务的 fact 时才加载。阅读 `assets/{filename}` 获取相关服务。仅加载正在积极考虑的服务卡片（通常每个请求 2-3 个）。

| 服务 | 知识文件 | 服务技能转接 |
|---------|---------------|---------------|
| Aurora DSQL | `assets/aurora-dsql.md` | `aurora-dsql` |
| Aurora MySQL | `assets/aurora-mysql.md` | `amazon-aurora-mysql` |
| Aurora PostgreSQL | `assets/aurora-postgresql.md` | `amazon-aurora-postgresql` |
| DocumentDB | `assets/documentdb.md` | `amazon-documentdb` |
| DynamoDB | `assets/dynamodb.md` | `amazon-dynamodb` |
| ElastiCache | `assets/elasticache.md` | `amazon-elasticache` |
| Keyspaces | `assets/keyspaces.md` | `amazon-keyspaces` |
| MemoryDB | `assets/memorydb.md` | — |
| Neptune | `assets/neptune.md` | — |
| ODB @ AWS | `assets/odb-aws.md` | — |
| RDS for Db2 | `assets/rds-db2.md` | `rds-db2` |
| RDS for MariaDB | `assets/rds-mariadb.md` | `rds-oss` |
| RDS for MySQL | `assets/rds-mysql.md` | `rds-oss` |
| RDS for Oracle | `assets/rds-oracle.md` | `rds-oracle` |
| RDS for PostgreSQL | `assets/rds-postgresql.md` | `rds-oss` |
| RDS for SQL Server | `assets/rds-sqlserver.md` | `rds-sqlserver` |
| Timestream for InfluxDB | `assets/timestream.md` | `timestream-influxdb` |
