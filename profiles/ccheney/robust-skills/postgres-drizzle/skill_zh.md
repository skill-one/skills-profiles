# PostgreSQL 和 Drizzle ORM

将数据库工作与项目的已安装 API 和部署上下文相匹配。用户的明确指令优先于此技能的指南。

## 建立数据库契约

使用相关的模式/查询、迁移历史和请求的行为作为输入。对于 Drizzle 代码，检查已安装的 `drizzle-orm`/`drizzle-kit` 版本和驱动程序；对于 SQL，当特定版本的特性很重要时，确定 PostgreSQL 版本。

参考资料涵盖 PostgreSQL 17/18，并区分 Drizzle 的 0.x `relations()` API 和 v1 `defineRelations()` API。不要混用它们或从 npm dist-tag 推断已安装的 API。当版本未知时，使用导入/锁文件或在提供版本相关代码之前请求缺失的版本。

## 保持变更一致

- 将数据库外键与 ORM 关系元数据分开声明。将空值性、唯一性和删除行为与实际关系相匹配。
- 在该事务中的每个语句都使用事务处理程序；通过外部连接的查询可以脱离它。
- 从计划和负载证据中诊断慢查询。评估引用列上的索引；PostgreSQL 不会自动创建它们。
- 生成并检查用于模式更改的迁移 SQL。保留已应用的迁移历史；使用新的迁移文件进行后续更改。
- 在应用迁移或 `push` 之前确定目标。编写或审查 SQL 本身并不需要将其执行到数据库上。当用户已经授权该目标和操作时，继续执行。
- 将 `EXPLAIN ANALYZE` 视为查询执行，包括写入。当执行不在任务范围内时，使用合适的测试目标或非执行计划。

提供请求的 SQL/代码、迁移或诊断，包括兼容性假设和相关验证。如果请求执行但目标缺失，准备变更并仅请求缺失的目标。

## 参考资料

阅读当前操作所需的主题。

| 任务 | 参考资料 |
|---|---|
| 表、类型、约束、索引、生成列 | [SCHEMA.md](references/SCHEMA.md) |
| 读取、写入、连接、事务、预准备查询 | [QUERIES.md](references/QUERIES.md) |
| 关系和特定于版本的关联查询 API | [RELATIONS.md](references/RELATIONS.md) |
| drizzle-kit 配置、迁移生成和部署 | [MIGRATIONS.md](references/MIGRATIONS.md) |
| PostgreSQL 特性、RLS、分区、JSONB、全文搜索 | [POSTGRES.md](references/POSTGRES.md) |
| 查询计划、索引、连接池、分页、批量工作 | [PERFORMANCE.md](references/PERFORMANCE.md) |
| 紧凑语法或连接设置查找 | [CHEATSHEET.md](references/CHEATSHEET.md) |

对于已安装项目和参考资料未建立的 API 或支持，请参考与版本匹配的 [Drizzle](https://orm.drizzle.team) 和 [PostgreSQL](https://www.postgresql.org/docs/) 文档。
