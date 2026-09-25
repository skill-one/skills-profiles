# Postgres 最佳实践

Postgres 使用指南和最佳实践，涵盖模式设计、索引、查询优化和常见陷阱。

## 支持的版本

本指南涵盖 PostgreSQL 14 至 18 版。版本特定功能会标记（例如 `[PG15+]`、`[PG18+]`）；环境依赖的示例会指明所需的权限、扩展或多节点配置。

PostgreSQL 每个大版本提供 5 年支持。始终运行最新的小版本。

| 版本 | 初始发布日期    | 结束支持日期    |
| ---- | -------------- | -------------- |
| 18   | 2025年9月      | 2030年11月      |
| 17   | 2024年9月      | 2029年11月      |
| 16   | 2023年9月      | 2028年11月      |
| 15   | 2022年10月     | 2027年11月      |
| 14   | 2021年9月      | 2026年11月      |

来源：[postgresql.org/support/versioning](https://www.postgresql.org/support/versioning/)

## 参考资料

| 领域                    | 资源                                | 使用场景                                                        |
| ----------------------- | --------------------------------------- | ------------------------------------------------------------------ |
| 模式设计               | `references/schema-design.md`           | 设计表、选择数据类型、规范化、分区                               |
| 索引                   | `references/indexing.md`                | 选择索引类型、复合索引、部分/覆盖索引                            |
| 查询优化               | `references/query-optimization.md`      | 阅读 EXPLAIN ANALYZE、修复瓶颈、查询规划器调优                    |
| 查询模式               | `references/query-patterns.md`          | CTE、窗口函数、侧连接、UPSERT、JSONB、反模式                      |
| 性能诊断               | `references/performance-diagnostics.md` | pg_stat 视图、锁分析、VACUUM、连接管理                          |
| 逻辑复制               | `references/logical-replication.md`     | 发布/订阅复制、在线迁移、CDC                                    |
| 热备站                 | `references/hot-standby.md`             | 流式复制、读副本、故障转移                                      |
| 事务隔离               | `references/transaction-isolation.md`   | 隔离级别、丢失更新、序列化失败、重试逻辑                        |
| 备份与恢复             | `references/backup-restore.md`          | pg_dump/pg_restore、pg_basebackup、PITR、恢复                    |
| 安全与角色             | `references/security-roles.md`          | 权限、RLS、pg_hba.conf、认证、SSL                              |
| 批量数据加载           | `references/bulk-loading.md`            | COPY 模式、ETL 阶段、优化大数据加载、批处理操作                  |
| 连接池                 | `references/connection-pooling.md`      | PgBouncer 配置、池模式、预编译语句、尺寸配置                      |
| 大版本升级             | `references/major-version-upgrades.md`  | pg_upgrade、逻辑复制迁移、预/后检查清单                          |
