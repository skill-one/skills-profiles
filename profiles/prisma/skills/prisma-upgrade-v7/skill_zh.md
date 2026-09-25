# 升级到 Prisma ORM 7

从 Prisma ORM v6 迁移到 v7 的完整指南。此次升级在新的 `prisma-client` 生成器、驱动程序适配器、`prisma.config.ts`、显式环境加载和生成客户端入口点等方面引入了重大破坏性变更。

## 何时应用

在以下情况下参考此指南：
- 从 Prisma v6 升级到 v7
- 更新到 `prisma-client` 生成器
- 设置驱动程序适配器
- 配置 `prisma.config.ts`
- 升级后修复导入错误

## 按优先级分类的规则类别

| 优先级 | 类别 | 影响 | 前缀 |
|--------|------|------|------|
| 1 | 模式迁移 | 关键 | `schema-changes` |
| 2 | 数据库连接 | 关键 | `driver-adapters` |
| 3 | 模块系统 | 关键 | `esm-support` |
| 4 | 配置和环境 | 高 | `prisma-config`, `env-variables` |
| 5 | 已移除的功能 | 高 | `removed-features` |
| 6 | 加速 | 高 | `accelerate-users` |

## 快速参考

- `schema-changes` - 生成器迁移、必需的输出路径、生成入口点以及 `Prisma.validator` 替换
- `driver-adapters` - SQL 提供商所需的适配器安装、连接池差异以及 Prisma Postgres 适配器选择
- `esm-support` - ESM 优先设置以及 `moduleFormat = "cjs"` 的 CommonJS 降级
- `prisma-config` - 创建和使用 `prisma.config.ts`
- `env-variables` - 显式环境加载
- `removed-features` - 已移除的中间件、指标和遗留 CLI 行为
- `accelerate-users` - Accelerate 用户迁移说明

## 使用 MongoDB？此指南不适用

Prisma 7 没有 MongoDB 连接器。不要将此指南中的任何步骤应用于 `provider = "mongodb"` 的项目——请参考 `prisma-mongodb-upgrade` 技能以获取实际决策（故意停留在 v6 而不是迁移到 Prisma Next）。

## 重要说明

- **MongoDB 项目应停留在 Prisma 6.x 或迁移到 Prisma Next** - 不要将 MongoDB 应用迁移到 Prisma 7 的 SQL 客户端路径（见 `prisma-mongodb-upgrade`）
- **需要 Node.js 20.19.0+**
- **需要 TypeScript 5.4.0+**
- **最新稳定 Prisma ORM 版本**：`7.6.0`

## 升级步骤概述

1. 更新包到 v7
2. 选择模块格式（默认为 `esm`，如果需要则为 `cjs`）
3. 更新 TypeScript 配置
4. 更新模式生成器块
5. 创建 `prisma.config.ts`
6. 安装和配置 SQL 提供商的驱动程序适配器
7. 更新 Prisma Client 导入
8. 更新客户端实例化
9. 替换已弃用的辅助模式，如 `Prisma.validator`
10. 运行 `prisma generate` 并测试

## 快速升级命令

```bash
# 更新包
npm install @prisma/client@7
npm install -D prisma@7

# 安装驱动程序适配器（PostgreSQL 或通过直接 TCP 的 Prisma Postgres）
npm install @prisma/adapter-pg pg

# 安装 dotenv 以进行环境加载
npm install dotenv

# 重新生成客户端
npx prisma generate
```

## 破坏性变更摘要

| 变更 | v6 | v7 |
|------|----|----|
| 模块格式 | 隐式/混合 | ESM 优先，`moduleFormat = "cjs"` 受支持 |
| 生成器提供者 | `prisma-client-js` | `prisma-client` 是默认值，而 `prisma-client-js` 仍存在以供遗留设置使用 |
| 输出路径 | 自动（node_modules） | 需要显式指定 |
| 驱动程序适配器 | 可选 | SQL 提供商必需 |
| 配置文件 | `.env` + 模式 | `prisma.config.ts` |
| 环境加载 | 自动 | 手动（dotenv） |
| 生成的入口点 | 单个包导出 | `client`, `browser`, `models`, `enums` 入口点 |
| 类型安全的查询片段 | `Prisma.validator()` | TypeScript `satisfies` |
| 中间件 | `$use()` | 客户端扩展 |
| 指标 | 预览功能 | 已移除 |

## 规则文件

每个破坏性变更的详细迁移指南：

```
references/esm-support.md        - ESM 和 CommonJS 配置
references/schema-changes.md     - 生成器、输出、导入和生成入口点
references/driver-adapters.md    - 必需的驱动程序适配器设置
references/prisma-config.md      - 新配置文件
references/env-variables.md      - 环境变量加载
references/removed-features.md   - 中间件、指标和 CLI 标志
references/accelerate-users.md   - Accelerate 的特殊处理
```

## 分步迁移

### 1. 为 ESM 优先项目更新 package.json

```json
{
  "type": "module"
}
```

如果您需要停留在 CommonJS，请保持您的应用为 CJS，并在生成器块中而不是强制 ESM 设置 `moduleFormat = "cjs"`。

### 2. 更新 tsconfig.json

```json
{
  "compilerOptions": {
    "module": "ESNext",
    "moduleResolution": "bundler",
    "target": "ES2023",
    "strict": true,
    "esModuleInterop": true
  }
}
```

### 3. 更新 schema.prisma

```prisma
// 之前（v6）
generator client {
  provider = "prisma-client-js"
}

// 之后（v7）
generator client {
  provider = "prisma-client"
  output   = "../generated/prisma"
  // 如果您需要 CommonJS，则可选：
  // moduleFormat = "cjs"
}
```

### 4. 创建 prisma.config.ts

```typescript
import 'dotenv/config'
import { defineConfig, env } from 'prisma/config'

export default defineConfig({
  schema: 'prisma/schema.prisma',
  migrations: {
    path: 'prisma/migrations',
  },
  datasource: {
    url: env('DATABASE_URL'),
  },
})
```

### 5. 安装驱动程序适配器（仅限 SQL 提供商）

```bash
# PostgreSQL
npm install @prisma/adapter-pg pg

# MySQL
npm install @prisma/adapter-mariadb mariadb

# SQLite
npm install @prisma/adapter-better-sqlite3 better-sqlite3

# Prisma Postgres 在标准 Node.js 应用中（推荐）
npm install @prisma/adapter-pg pg

# Prisma Postgres 服务器端驱动（edge/serverless）
npm install @prisma/adapter-ppg @prisma/ppg

# Neon
npm install @prisma/adapter-neon
```

MongoDB 在已发布的 Prisma 7.6.0 包中没有 SQL `@prisma/adapter-*` 包。如果您正在升级 MongoDB 项目，请停止并让该项目停留在最新的 Prisma 6.x 版本，而不是遵循标准的 Prisma 7 迁移路径。

### 6. 更新客户端实例化

```typescript
// 之前（v6）
import { PrismaClient } from '@prisma/client'
const prisma = new PrismaClient()

// 之后（v7）
import { PrismaClient } from '../generated/prisma/client'
import { PrismaPg } from '@prisma/adapter-pg'

const adapter = new PrismaPg({
  connectionString: process.env.DATABASE_URL
})

const prisma = new PrismaClient({ adapter })
```

### 7. 替换 Prisma.validator 为 satisfies

```typescript
import { Prisma } from '../generated/prisma/client'

const userSelect = {
  id: true,
  email: true,
  name: true,
} satisfies Prisma.UserSelect
```

### 8. 运行迁移并生成

```bash
npx prisma generate
npx prisma migrate dev  # 如果需要
```

## 故障排除

### "Cannot find module" 错误
- 确保生成器 `output` 路径与您的导入路径匹配
- 确保 `prisma generate` 成功运行

### SSL 证书错误
- 如果您需要保留旧行为，请向适配器配置添加 `ssl: { rejectUnauthorized: false }`
- 或者正确配置您的证书，使用 `NODE_EXTRA_CA_CERTS` / OpenSSL CA 设置

### 连接超时问题
- 驱动程序适配器使用底层驱动程序的默认值，这与 v6 不同
- 如果需要，请在适配器上显式配置池设置

## 资源

- [官方 v7 升级指南](https://www.prisma.io/docs/orm/more/upgrades/to-v7)
- [驱动程序适配器文档](https://www.prisma.io/docs/orm/core-concepts/supported-databases/database-drivers)
- [Prisma Config 参考](https://www.prisma.io/docs/orm/reference/prisma-config-reference)

## 如何使用

首先遵循 `references/schema-changes.md` 和 `references/driver-adapters.md`，然后根据您的项目设置应用其余的参考文件。
