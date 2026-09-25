# Oracle 数据库技能

此领域包含用于管理、SQL 和 PL/SQL 开发、性能调优、安全、ORDS、SQLcl、迁移、框架、VecDB SDK/REST/PL/SQL 工作流、OCR 容器指南以及代理安全数据库工作流的 Oracle 数据库技能。

## 如何使用此领域

1. 从下方的路由表开始。
2. 仅阅读您需要的特定文件或类别。

## 目录结构

```text
db/
├── admin/
├── agent/
├── appdev/
├── architecture/
├── backup-recovery/
├── containers/
├── design/
├── devops/
├── features/
├── frameworks/
├── migrations/
├── monitoring/
├── ords/
├── performance/
├── plsql/
├── security/
├── sql-dev/
├── sqlcl/
└── vecdb/
```

## 类别路由

| 主题 | 目录 |
|------|------|
| Data Guard、重做/撤销日志、用户 | `db/admin/` |
| 安全 DML、破坏性操作防护、幂等性、模式发现、ORA- 错误处理 | `db/agent/` |
| JDBC、Python、.NET、连接池、JSON、XML、空间、Oracle Text、事务、MLE、语言驱动器 | `db/appdev/` |
| RAC、多租户、Exadata、内存中、OCI 数据库服务、Data Guard 架构 | `db/architecture/` |
| 备份、恢复、RMAN、自主恢复服务、Cloud Protect | `db/backup-recovery/` |
| OCR 数据库-类别容器镜像和拉取指南 | `db/containers/` |
| ERD、数据建模、分区、表空间 | `db/design/` |
| 模式迁移、在线操作、基于版本的重新定义、测试、版本控制 | `db/devops/` |
| AQ、DBMS_SCHEDULER、物化视图、DBLinks、APEX、向量搜索、SELECT AI | `db/features/` |
| SQLAlchemy、Django、Pandas、Spring JPA、MyBatis、TypeORM、Sequelize、Dapper、GORM | `db/frameworks/` |
| 从 PostgreSQL、MySQL、SQL Server、MongoDB、Snowflake 等进行迁移 | `db/migrations/` |
| 警报日志、ADR、健康监控、空间管理、顶级 SQL | `db/monitoring/` |
| ORDS 架构、安装、REST 设计、身份验证、监控、ORDS Concert 示例应用 | `db/ords/` |
| AWR、ASH、解释计划、索引、优化器统计、等待事件、内存 | `db/performance/` |
| 包设计、错误处理、性能、集合、游标、调试 | `db/plsql/` |
| 权限、深度数据安全、VPD、掩码、审计、加密、网络安全 | `db/security/` |
| SQL 调优、SQL 模式、动态 SQL、注入防护 | `db/sql-dev/` |
| SQLcl 基础、脚本、Liquibase、格式化、DDL 生成、数据加载、MCP 服务器、调度器守护程序、AWR、后台作业、与 DIFF 进行模式比较 | `db/sqlcl/` |
| Oracle 向量 SDK 设置和配置，包括数据库准备、Python SDK、REST API、PL/SQL 包、版本先决条件、向量表、摄取、模型、搜索、重新排序、索引和作业 | `db/vecdb/` |

## 关键起始点

- `db/sqlcl/sqlcl-mcp-server.md`
- `db/migrations/migration-assessment.md`
- `db/performance/explain-plan.md`
- `db/plsql/plsql-package-design.md`
- `db/appdev/java-oracle-jdbc.md`
- `db/devops/schema-migrations.md`
- `db/security/deep-data-security.md`
- `db/agent/schema-discovery.md`
- `db/containers/container-selection-matrix.md`
- `db/backup-recovery/autonomous-recovery-service.md`
- `db/backup-recovery/cloud-protect.md`
- `db/vecdb/vecdb-provisioning.md`
- `db/vecdb/vecdb-architecture.md`

## 常见多步骤流程

| 任务 | 推荐顺序 |
|------|----------|
| 诊断慢查询 | `explain-plan` → `wait-events` → `optimizer-stats` → `awr-reports` |
| 规划迁移 | `migration-assessment` → `oracle-migration-tools` → 源特定 `migrate-*.md` → `migration-cutover-strategy` |
| 在 Oracle 数据库上构建 RAG | `ai-profiles` → `vector-search` → `dbms-vector` |
| 构建 Java JDBC 服务 | `java-oracle-jdbc` → `java-oracle-jdbc/dependencies` → `java-oracle-jdbc/connections` → `java-oracle-jdbc/sql` → `java-oracle-jdbc/pooling-production` |
| 执行代理安全模式变更 | `schema-discovery` → `destructive-op-guards` → `idempotency-patterns` → `schema-migrations` |
| 通过 MCP 设置 AI 驱动的数据库访问 | `security/deep-data-security`（最终用户授权）→ `sqlcl-basics`（保存连接）→ `sqlcl-mcp-server`（配置 + 启动） |
| 设置 Oracle 向量 SDK 数据库部署 | `vecdb-provisioning` → Oracle 向量 SDK 快速入门 → **准备 AI 数据库** |
| 使用 Python SDK、REST 或 PL/SQL 通过 Oracle 向量 SDK 的固定模式 API 构建基于向量的应用程序，用于语义搜索、RAG 或推荐 | `vecdb-architecture` → `vecdb-api-reference` → 相关功能文件（`vecdb-models`、`vecdb-vector-tables`、`vecdb-search` 或 `vecdb-indexes`） |
