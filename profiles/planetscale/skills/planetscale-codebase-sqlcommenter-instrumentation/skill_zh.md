# 代码库 SQLCommenter 仪器化

## 目的

检查与 PlanetScale 连接的应用程序代码库，并推荐正确的 SQLCommenter 风格仪器化，以便 PlanetScale Insights 和 Postgres Traffic Control 可以将查询归属到应用程序代码路径。未经批准，不得编辑文件或安装依赖项。

## 代码库检查

识别：

- 语言和框架。
- ORM 或查询构建器。
- 数据库适配器。
- 迁移工具。
- 后台作业系统。
- 路由框架。
- 部署元数据源，例如 git SHA 或发布 ID。
- 现有的 SQL 注释、查询标签、跟踪、OpenTelemetry 或数据库中间件。
- PlanetScale 连接配置。
- 代码库是否连接到 Vitess、Postgres 或两者。

## 推荐的包映射

为检测到的堆栈使用最原生的维护选项。

### Ruby on Rails / ActiveRecord

首选与 PlanetScale 标签兼容的：

- 当 Rails 查询注释需要 SQLCommenter 格式以用于 PlanetScale Query Insights 时，使用 PlanetScale 的 `activerecord-sql_commenter`。

其他选项：

- 当足够且与目标数据库/Insights 行为兼容时，使用 Rails 内置查询日志。
- 对于较旧的 Rails 或当已使用 Basecamp 风格的 ActiveRecord 查询归属时，使用 `marginalia`。
- 当项目已使用 OpenTelemetry SQLCommenter 生态系统时，使用 `sqlcommenter_rails`。

推荐标签：

- `application`
- `controller`
- `action`
- `job`
- `route`
- `release_sha`

### Laravel / PHP

首选：

- `spatie/laravel-sql-commenter` 用于与 PlanetScale Query Insights 兼容的 SQLCommenter 格式注释。

推荐标签：

- `application`
- `route`
- `controller`
- `action`
- `job`
- `queue`
- `release_sha`

### Prisma / TypeScript / JavaScript

首选：

- 当检测到 Prisma 时，使用 Prisma 的原生 SQL 注释包：
  - `@prisma/sqlcommenter`
  - `@prisma/sqlcommenter-query-tags`
  - `@prisma/sqlcommenter-trace-context`

注意：PlanetScale 的 Postgres 查询标签文档可能列出不提供官方 SQLCommenter 支持的 Prisma，但 Prisma 自己的当前文档提供了原生 SQLCommenter 包。当检测到 Prisma 时，优先参考当前 Prisma 文档。

推荐标签：

- `application`
- `service`
- `route`
- `operation`
- `feature`
- `release_sha`

### Knex / Sequelize / Express / Node

使用 OpenTelemetry SQLCommenter 生态系统中的兼容 SQLCommenter 中间件或仪器化，前提是它们被维护且兼容。

推荐标签：

- `application`
- `service`
- `route`
- `controller`
- `action`
- `feature`
- `release_sha`

### Kysely / Drizzle / Bun / 自定义查询构建器

如果没有维护的 SQLCommenter 包，建议在数据库客户端边界或查询构建器扩展层进行手动标签。

要求：

- 标签必须是结构化的 SQL 注释。
- 标签必须在语句终止符之前插入。
- 标签必须能够经受 ORM、代理和池器行为。
- 值必须进行 URL 编码，并适合 SQL 注释。
- 标签必须是低基数。

### Django / SQLAlchemy / psycopg2 / Flask / Python

在兼容的情况下，使用 OpenTelemetry SQLCommenter 生态系统中的 SQLCommenter 仪器化。

推荐标签：

- `application`
- `framework`
- `route`
- `view`
- `job`
- `release_sha`

### Java / Hibernate / Spring

在兼容的情况下，使用 Hibernate/Spring 兼容的 SQLCommenter 仪器化。

推荐标签：

- `application`
- `service`
- `controller`
- `action`
- `route`
- `release_sha`

### Go / database/sql / net/http / gorilla/mux

使用兼容的 SQLCommenter 仪器化或在查询边界使用数据库包装器。

推荐标签：

- `application`
- `service`
- `handler`
- `route`
- `job`
- `release_sha`

## 标准标签策略

在所有框架中推荐此基线：

- 仅使用稳定、有界的值。
- 在标签之前规范化路由。
- 包括应用程序/服务/作业归属。
- 包括部署 SHA。
- 包括代理、脚本、BI、工作器和集成的源类型。
- 不包括密钥、PII、用户 ID、请求 ID、原始租户 ID 或原始 URL。

## 验证计划

在推荐合并之前：

- 确认生成的 SQL 注释出现在本地/预发布查询日志中。
- 确认注释能够经受 ORM、驱动器、池器和 PlanetScale 连接路径。
- 确认 Insights 显示标签。
- 确认标签基数是有界的。
- 确认 Traffic Control 可以匹配预期的 Postgres 标签。
- 确认没有敏感数据存在。

## 输出

返回：

- 检测到的堆栈。
- 当前查询标签状态。
- 推荐的包或手动仪器化路径。
- 提议的标签架构。
- 可能会更改的文件。
- 验证步骤。
- 风险。
- 需要批准的提议更改。

以：

“没有更改任何代码库文件或依赖项。” 结尾。
