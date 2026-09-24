# 升级到 Prisma ORM 7

从 Prisma ORM v6 迁移到 v7 的完整指南。此次升级在全新的 `prisma-client` 生成器、驱动程序适配器、`prisma.config.ts`、显式环境加载以及生成的客户端入口点方面引入了一些重大变更。

## 适用场景

当以下情况时需要参考本技能：
- 从 Prisma v6 升级到 v7
- 更新至 `prisma-client` 生成器
- 设置驱动程序适配器
- 配置 `prisma.config.ts`
- 升级后修复导入错误

## 按优先级划分的规则类别

| 优先级 | 类别 | 影响 | 前缀 |
|----------|----------|--------|--------|
| 1 | Schema 迁移 | CRITICAL | `schema-changes` |
| 2 | 数据库连接 | CRITICAL | `driver-adapters` |
| 3 | 模块系统 | CRITICAL | `esm-support` |
| 4 | 配置与环境变量 | HIGH | `prisma-config`, `env-variables` |
| 5 | 已移除功能 | HIGH | `removed-features` |
| 6 | 加速（Accelerate） | HIGH | `accelerate-users` |

## 快速参考

- `schema-changes` - 生成器迁移、必需的输出路径、生成的入口点，以及 `Prisma.validator` 的替换
- `driver-adapters` - 为 SQL 提供商安装的必需适配器、连接池差异，以及 Prisma Postgres 适配器选择
- `esm-support` - 以 ESM 优先的部署方案，以及使用 `moduleFormat = "cjs"` 的 CommonJS 备选方案
- `prisma-config` - 创建和使用 `prisma.config.ts`
- `env-variables` - 显式加载环境变量
- `removed-features` - 已移除的中间件、指标以及旧版 CLI 行为
- `accelerate-users` - 针对 Accelerate 用户的迁移说明

## 使用 MongoDB？本指南不适用

Prisma 7 没有 MongoDB 连接器。请勿将本指南中的任何步骤应用于 `provider = "mongodb"` 的项目——请参考 `prisma-mongodb-upgrade` 技能以了解实际决策（有意停留在 v6 还是迁移到 Prisma Next）。

## 重要说明

- **MongoDB 项目应停留在 Prisma 6.x 或迁移至 Prisma Next** - 请勿将 MongoDB 应用迁移至 Prisma 7 的 SQL 客户端路径（参见 `prisma-mongodb-upgrade`）
- **要求 Node.js 20.19.0 及以上版本**
- **要求 TypeScript 5.4.0 及以上版本**
- **最新稳定版 Prisma ORM 版本**：`7.6.0`

## 升级步骤概览

1. 更新软件包至 v7
2. 选择模块格式（默认为 `esm`，如需则使用 `cjs`）
3. 更新 TypeScript 配置
4. 更新 schema 生成器代码块
5. 创建 `prisma.config.ts`
6. 为 SQL 提供商安装并配置驱动程序适配器
7. 更新 Prisma Client 导入
8. 更新客户端实例化
9. 替换 `Prisma.validator` 等已弃用的辅助模式
10. 运行 `prisma generate` 并进行测试

## 快速升级命令

```bash
# 更新软件包
npm install @prisma/client@7
npm install -D prisma@7

# 安装驱动程序适配器（PostgreSQL 或通过直接 TCP 连接使用 Prisma Postgres）
npm install @prisma/adapter-pg pg

# 安装 dotenv 用于环境变量加载
npm install dotenv

# 重新生成客户端
npx prisma generate
```

## 变更摘要

| 变更 | v6 | v7 |
|--------|----|----|
| 模块格式 | 隐式/混合 | 以 ESM 优先，支持 `moduleFormat = "cjs"` |
| 生成器提供商 | `prisma-client-js` | `prisma-client` 为默认值，而 `prisma-client-js` 仍可用于旧版部署 |
| 输出路径 | 自动（node_modules） | 必须显式指定 |
| 驱动程序适配器 | 可选 | SQL 提供商必需 |
| 配置文件 | `.env` + schema | `prisma.config.ts` |
| 环境变量加载 | 自动 | 手动（使用 dotenv） |
| 生成的入口点 | 单一包导出 | `client`、`browser`、`models`、`enums` 入口点 |
| 类型安全查询片段 | `Prisma.validator()` | TypeScript `satisfies` |
| 中间件 | `$use()` | Client 扩展 |
| 指标 | 预览功能 | 已移除 |

## 规则文件

各破坏性变更的详细迁移指南：

```
references/esm-support.md        - ESM 与 CommonJS 配置
references/schema-changes.md     - 生成器、输出、导入及生成的入口点
references/driver-adapters.md    - 必需的驱动程序适配器配置
references/prisma-config.md      - 新的配置文件
references/env-variables.md      - 环境变量加载
references/removed-features.md   - 中间件、指标及 CLI 参数
references/accelerate-users.md   - 针对 Accelerate 的特殊处理
```

## 分步迁移

### 1. 为 ESM 优先项目更新 package.json

```json
{
  "type": "module"
}
```

若需继续使用 CommonJS，请保持应用程序为 CommonJS，并在生成器代码块中设置 `moduleFormat = "cjs"`，而非强制使用 ESM。

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
  // 如需 CommonJS，可选：
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

### 5. 为 SQL 提供商安装驱动程序适配器

```bash
# PostgreSQL
npm install @prisma/adapter-pg pg

# MySQL
npm install @prisma/adapter-mariadb mariadb

# SQLite
npm install @prisma/adapter-better-sqlite3 better-sqlite3

# Prisma Postgres（适用于标准 Node.js 应用，推荐）
npm install @prisma/adapter-pg pg

# Prisma Postgres 服务端无服务器驱动（edge/serverless）
npm install @prisma/adapter-ppg @prisma/ppg

# Neon
npm install @prisma/adapter-neon
```

MongoDB 在 Prisma 7.6.0 发布的包中没有对应的 SQL `@prisma/adapter-*` 包。如果您正在升级 MongoDB 项目，请停止并按照最新的 Prisma 6.x 版本继续使用，而不是按照标准的 Prisma 7 迁移路径操作。

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

### 7. 将 `Prisma.validator` 替换为 `satisfies`

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
npx prisma migrate dev  # 如需
```

## 故障排查

### "找不到模块" 错误
- 检查生成器的 `output` 路径是否与你的导入路径匹配
- 确保 `prisma generate` 已成功运行

### SSL 证书错误
- 如果需要保持旧版行为，请将 `ssl: { rejectUnauthorized: false }` 添加到适配器配置中
- 或通过 `NODE_EXTRA_CA_CERTS` / OpenSSL CA 设置正确配置您的证书

### 连接超时问题
- 驱动程序适配器使用底层驱动程序的默认设置，与 v6 存在差异
- 如有需要，请在适配器上显式配置连接池设置

## 资源

- [Prisma 7 官方升级指南](https://www.prisma.io/docs/orm/more/upgrades/to-v7)
- [驱动程序适配器文档](https://www.prisma.io/docs/orm/core-concepts/supported-databases/database-drivers)
- [Prisma 配置参考](https://www.prisma.io/docs/orm/reference/prisma-config-reference)

## 使用方法

首先参考 `references/schema-changes.md` 和 `references/driver-adapters.md`，然后根据您的项目配置应用其余的参考文件。
