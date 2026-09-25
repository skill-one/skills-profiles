# Prisma 数据库设置

配置 Prisma ORM 与各种数据库提供者的全面指南。

## 何时应用

在以下情况下参考此技能：
- 初始化新的 Prisma 项目
- 切换数据库提供者
- 配置连接字符串和环境变量
- 排查数据库连接问题
- 设置数据库特定功能
- 生成和实例化 Prisma Client

## 按优先级分类的规则类别

| 优先级 | 类别 | 影响 | 前缀 |
|--------|------|------|------|
| 1 | 提供者指南 | CRITICAL | 提供者名称 |
| 2 | Prisma Postgres | HIGH | `prisma-postgres` |
| 3 | Client Setup | CRITICAL | `prisma-client-setup` |

## 系统先决条件

- **Node.js 20.19.0+**
- **TypeScript 5.4.0+**

## Bun 运行时

如果你使用 Bun，请使用 `bunx --bun prisma ...` 运行 Prisma CLI 命令，以便 Prisma 使用 Bun 运行时而不是回退到 Node.js。

## 支持的数据库

| 数据库 | 提供者字符串 | 备注 |
|--------|--------------|------|
| PostgreSQL | `postgresql` | 默认，支持全部功能 |
| MySQL | `mysql` | 广泛支持，部分 JSON 差异 |
| SQLite | `sqlite` | 基于本地文件，不支持枚举/标量列表 |
| MongoDB | `mongodb` | Mongo 特定工作流；不要应用 SQL 驱动器适配器指南 |
| SQL Server | `sqlserver` | 微软生态系统 |
| CockroachDB | `cockroachdb` | 分布式 SQL，兼容 Postgres |
| Prisma Postgres | `postgresql` | 管理式无服务器数据库 |

## 配置文件

你的配置结构取决于提供者和 Prisma 主版本：

1. **所有提供者**都使用**`prisma/schema.prisma`**。
2. **Prisma 7 SQL 设置**通常使用**`prisma.config.ts`**配置数据源 URL。
3. **MongoDB 项目应保持在 Prisma 6.x**，在模式中保留`url = env("DATABASE_URL")`，并继续使用经典 MongoDB 设置。

## 驱动器适配器

标准 SQL 工作流使用驱动器适配器。为你的数据库选择适配器和驱动器，并将其传递给 `PrismaClient`。

| 数据库 | 适配器 | JS 驱动器 |
|--------|--------|-----------|
| PostgreSQL | `@prisma/adapter-pg` | `pg` |
| CockroachDB | `@prisma/adapter-pg` | `pg` |
| Prisma Postgres (Node.js) | `@prisma/adapter-pg` | `pg` |
| Prisma Postgres (edge/serverless) | `@prisma/adapter-ppg` | `@prisma/ppg` |
| MySQL / MariaDB | `@prisma/adapter-mariadb` | `mariadb` |
| SQLite | `@prisma/adapter-better-sqlite3` | `better-sqlite3` |
| SQLite (Turso/LibSQL) | `@prisma/adapter-libsql` | `@libsql/client` |
| SQL Server | `@prisma/adapter-mssql` | `node-mssql` |

MongoDB 不应遵循 Prisma 7 SQL 适配器工作流。使用最新 Prisma 6.x 版本为 MongoDB 项目，并且不要为它安装 SQL `@prisma/adapter-*` 包。

示例（PostgreSQL）：

```ts
import 'dotenv/config'
import { PrismaClient } from '../generated/client'
import { PrismaPg } from '@prisma/adapter-pg'

const adapter = new PrismaPg({ connectionString: process.env.DATABASE_URL })
const prisma = new PrismaClient({ adapter })
```

## Prisma Client Setup（必需）

Prisma Client 必须为任何数据库进行安装和生成。

1. 安装 Prisma CLI 和 Prisma Client：
   ```bash
   npm install prisma --save-dev
   npm install @prisma/client
   ```

1. 添加生成器块（`prisma-client`需要显式输出路径）：
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

1. 对于 SQL 提供者，使用数据库特定驱动器适配器实例化 Prisma Client：
   ```typescript
   import { PrismaClient } from '../generated/client'
   import { PrismaPg } from '@prisma/adapter-pg'

   const adapter = new PrismaPg({ connectionString: process.env.DATABASE_URL })
   const prisma = new PrismaClient({ adapter })
   ```

1. 每次模式更改后重新运行 `prisma generate`。

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

对于 MongoDB，保持在最新 Prisma 6.x 线上，并在 `schema.prisma` 中保留连接 URL。不要将 MongoDB 项目迁移到 Prisma 7 SQL 适配器设置。如果 MongoDB 项目询问升级 Prisma 版本，请路由到 `prisma-mongodb-upgrade` 技能（保持 Prisma 6 vs Prisma Next 是真正决策；Prisma 7 不是选项）。

## 规则文件

查看各个规则文件以获取详细设置说明：

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

## 如何使用

选择你的数据库的提供者参考文件，然后应用 `references/prisma-client-setup.md` 完成客户端生成和适配器设置。对于 MongoDB，使用 `references/mongodb.md` 而不是复制 SQL 适配器示例或 Prisma 7 配置模式。
