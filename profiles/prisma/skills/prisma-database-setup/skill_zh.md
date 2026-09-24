# Prisma 数据库设置

用于配置 Prisma ORM 与多种数据库提供商的全面指南。

## 适用场景

在以下情况下参考此技能：
- 初始化新的 Prisma 项目
- 切换数据库提供商
- 配置连接字符串和环境变量
- 排查数据库连接问题
- 配置数据库特定功能
- 生成并实例化 Prisma Client

## 按优先级划分的规则分类

| 优先级 | 分类 | 影响 | 前缀 |
|----------|----------|--------|--------|
| 1 | 提供商指南 | 关键 | 提供商名称 |
| 2 | Prisma Postgres | 高 | `prisma-postgres` |
| 3 | 客户端设置 | 关键 | `prisma-client-setup` |

## 系统先决条件

- **Node.js 20.19.0+**
- **TypeScript 5.4.0+**

## Bun 运行时

如果您正在使用 Bun，请使用 `bunx --bun prisma ...` 运行 Prisma CLI 命令，以便 Prisma 使用 Bun 运行时，而非回退到 Node.js。

## 支持数据库

| 数据库 | 提供商标签 | 备注 |
|----------|-----------------|-------|
| PostgreSQL | `postgresql` | 默认，功能支持完整 |
| MySQL | `mysql` | 支持广泛，部分 JSON 差异 |
| SQLite | `sqlite` | 本地文件存储，无枚举/标量列表 |
| MongoDB | `mongodb` | Mongo 专属工作流；不应用 SQL 驱动适配器指南 |
| SQL Server | `sqlserver` | 微软生态 |
| CockroachDB | `cockroachdb` | 分布式 SQL，兼容 Postgres |
| Prisma Postgres | `postgresql` | 托管无服务器数据库 |

## 配置文件

您的配置结构取决于提供商和 Prisma 主版本：

1. **所有提供商**均使用 **`prisma/schema.prisma`**。
2. **Prisma 7 SQL 配置**通常使用 **`prisma.config.ts`** 配置数据源 URL。
3. **MongoDB 项目**应保持使用 Prisma 6.x，在 schema 中保留 `url = env("DATABASE_URL")`，并继续使用传统的 MongoDB 配置。

## 驱动适配器

标准的 SQL 工作流程使用驱动适配器。根据您的数据库选择适配器和驱动，并将适配器传入 `PrismaClient`。

| 数据库 | 适配器 | JS 驱动 |
|----------|---------|-----------|
| PostgreSQL | `@prisma/adapter-pg` | `pg` |
| CockroachDB | `@prisma/adapter-pg` | `pg` |
| Prisma Postgres (Node.js) | `@prisma/adapter-pg` | `pg` |
| Prisma Postgres (edge/serverless) | `@prisma/adapter-ppg` | `@prisma/ppg` |
| MySQL / MariaDB | `@prisma/adapter-mariadb` | `mariadb` |
| SQLite | `@prisma/adapter-better-sqlite3` | `better-sqlite3` |
| SQLite (Turso/LibSQL) | `@prisma/adapter-libsql` | `@libsql/client` |
| SQL Server | `@prisma/adapter-mssql` | `node-mssql` |

MongoDB 不应遵循 Prisma 7 的 SQL 适配器工作流。MongoDB 项目应使用最新的 Prisma 6.x 版本，且不得为其安装 SQL 的 `@prisma/adapter-*` 包。

示例（PostgreSQL）：

```ts
import 'dotenv/config'
import { PrismaClient } from '../generated/client'
import { PrismaPg } from '@prisma/adapter-pg'

const adapter = new PrismaPg({ connectionString: process.env.DATABASE_URL })
const prisma = new PrismaClient({ adapter })
```

## Prisma Client 设置（必需）

任何数据库都必须安装并生成 Prisma Client。

1. 安装 Prisma CLI 和 Prisma Client：
   ```bash
   npm install prisma --save-dev
   npm install @prisma/client
   ```

1. 添加生成器代码块（`prisma-client` 需要显式的输出路径）：
   ```prisma
   generator client {
     provider = "prisma-client"
     output   = "../generated"
   }
   ```

1. 生成 Prisma Client：
   ```bash
   npx prisma generate
   ```

1. 对于 SQL 提供商，使用数据库特定的驱动适配器实例化 Prisma Client：
   ```typescript
   import { PrismaClient } from '../generated/client'
   import { PrismaPg } from '@prisma/adapter-pg'

   const adapter = new PrismaPg({ connectionString: process.env.DATABASE_URL })
   const prisma = new PrismaClient({ adapter })
   ```

1. 每次修改 schema 后，重新运行 `prisma generate`。

## 快速参考

### PostgreSQL
```prisma
datasource db {
  provider = "postgresql"
}

generator client {
  provider = "prisma-client"
  output   = "../generated"
}
```

### MySQL
```prisma
datasource db {
  provider = "mysql"
}

generator client {
  provider = "prisma-client"
  output   = "../generated"
}
```

### SQLite
```prisma
datasource db {
  provider = "sqlite"
}

generator client {
  provider = "prisma-client"
  output   = "../generated"
}
```

### MongoDB
```prisma
datasource db {
  provider = "mongodb"
  url      = env("DATABASE_URL")
}

generator client {
  provider = "prisma-client-js"
}
```

对于 MongoDB，请保持在最新的 Prisma 6.x 版本线路上，并将连接 URL 保留在 `schema.prisma` 中。不要将 MongoDB 项目迁移至 Prisma 7 的 SQL 适配器设置。如果 MongoDB 项目询问关于升级 Prisma 版本的问题，请将其路由至 `prisma-mongodb-upgrade` 技能（选择“维持 6.x”与 Prisma Next 是真正的决策；Prisma 7 不可选）。

## 规则文件

请查看单独的规则文件以获取详细的设置说明：

```
references/postgresql.md
references/mysql.md
references/sqlite.md
references/mongodb.md
references/sqlserver.md
references/cockroachdb.md
references/prisma-postgres.md
references/prisma-client-setup.md
```

## 使用方法

请根据您的数据库选择提供商参考文件，然后应用 `references/prisma-client-setup.md` 以完成客户端生成和适配器设置。对于 MongoDB，请使用 `references/mongodb.md`，而不是照搬 SQL 适配器示例或 Prisma 7 配置模式。
