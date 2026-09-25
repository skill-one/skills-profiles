# Prisma CLI 参考

Prisma ORM CLI 命令的参考文档。本指南提供了当前 Prisma ORM 版本中命令用法、选项和最佳实践的指导。

## 边界：平台与计算

不要将稳定的 ORM 命令 (`prisma`) 与公开测试版的平台包 (`@prisma/cli`, 二进制文件 `prisma-cli`) 混淆。使用 `prisma-compute` 进行计算应用和工作区认证，使用 `prisma-postgres` 进行平台项目和数据库。

## 适用场景

在以下情况下参考本指南：
- 设置新的 Prisma 项目 (`prisma init`)
- 生成 Prisma Client (`prisma generate`)
- 运行数据库迁移 (`prisma migrate`)
- 管理数据库状态 (`prisma db push/pull`)
- 使用本地开发数据库 (`prisma dev`)
- 调试 Prisma 问题 (`prisma debug`)
- 生成 Shell 补全 (`prisma complete`)

## 按优先级分类的规则类别

| 优先级 | 类别 | 影响 | 前缀 |
|--------|------|------|------|
| 1 | 设置 | 高 | `init` |
| 2 | 生成 | 高 | `generate` |
| 3 | 开发 | 高 | `dev` |
| 4 | 数据库 | 高 | `db-` |
| 5 | 迁移 | 关键 | `migrate-` |
| 6 | 实用工具 | 中 | `complete`, `studio`, `validate`, `format`, `debug`, `mcp` |

## 命令类别

| 类别 | 命令 | 目的 |
|------|------|------|
| 设置 | `init` | 初始化 Prisma 项目 |
| 生成 | `generate` | 生成 Prisma Client |
| 验证 | `validate`, `format` | 模式验证和格式化 |
| 开发 | `dev` | 本地 Prisma Postgres 用于开发 |
| 数据库 | `db pull`, `db push`, `db seed`, `db execute` | 直接数据库操作 |
| 迁移 | `migrate dev`, `migrate deploy`, `migrate reset`, `migrate status`, `migrate diff`, `migrate resolve` | 模式迁移 |
| 实用工具 | `complete`, `studio`, `mcp`, `version`, `debug` | Shell、开发和 AI 工具 |

## 快速参考

### 项目设置

```bash
# 初始化新项目（创建 prisma/ 文件夹和 prisma.config.ts）
prisma init

# 指定数据库初始化
prisma init --datasource-provider postgresql
prisma init --datasource-provider mysql
prisma init --datasource-provider sqlite

# 使用 Prisma Postgres（云）初始化
prisma init --db

# 带示例模型的初始化
prisma init --with-model
```

### Client 生成

```bash
# 生成 Prisma Client
prisma generate

# 开发模式监听
prisma generate --watch

# 仅生成特定生成器
prisma generate --generator client
```

### Bun 运行时

使用 Bun 时，始终添加 `--bun` 标志，以便 Prisma 使用 Bun 运行时（否则会回退到 Node.js，因为 CLI shebang 的影响）：

```bash
bunx --bun prisma init
bunx --bun prisma generate
```

### 本地开发数据库

```bash
# 启动本地 Prisma Postgres
prisma dev

# 指定名称启动
prisma dev --name myproject

# 后台运行（分离模式）
prisma dev --detach

# 列出所有本地实例
prisma dev ls

# 停止实例
prisma dev stop myproject

# 删除实例数据
prisma dev rm myproject
```

### 数据库操作

```bash
# 从现有数据库拉取模式
prisma db pull

# 推送模式到数据库（无迁移）
prisma db push

# 种子数据库
prisma db seed

# 执行原始 SQL
prisma db execute --file ./script.sql
```

### 迁移（开发）

```bash
# 创建并应用迁移
prisma migrate dev

# 带名称创建迁移
prisma migrate dev --name add_users_table

# 创建迁移但不应用
prisma migrate dev --create-only

# 重置数据库并应用所有迁移
prisma migrate reset
```

### 迁移（生产）

```bash
# 应用待处理的迁移（CI/CD）
prisma migrate deploy

# 检查迁移状态
prisma migrate status

# 比较模式并生成差异
prisma migrate diff --from-config-datasource --to-schema schema.prisma --script
```

### 实用工具命令

```bash
# 打开 Prisma Studio（数据库 GUI）
prisma studio

# 启动 Prisma 的 MCP 服务器用于 AI 工具
prisma mcp

# 显示版本信息
prisma version
prisma -v

# 调试信息
prisma debug

# 验证模式
prisma validate

# 格式化模式
prisma format

# 生成 Shell 补全代码
prisma complete zsh
```

## AI 安全检查点

当 Prisma 检测到 AI 代理时，会阻止破坏性命令，直到代理获得明确的用户同意。这包括 `migrate reset`, `db push --force-reset` 和 `db push --accept-data-loss`。

- 在运行命令前立即解释确切的数据丢失影响并请求同意。
- 不要从早期或不相关的消息中推断同意。
- 如果自动化需要同意变量，请将 `PRISMA_USER_CONSENT_FOR_DANGEROUS_AI_ACTION` 设置为用户的确切同意消息。不要编造文本。
- Prisma MCP 服务器故意没有 `migrate-reset` 工具。

在执行任何破坏性 Prisma 命令前阅读 `references/agent-safety.md`。

## 当前 Prisma CLI 设置

### 新配置文件

使用 `prisma.config.ts` 进行 CLI 配置：

```typescript
import 'dotenv/config'
import { defineConfig, env } from 'prisma/config'

export default defineConfig({
  schema: 'prisma/schema.prisma',
  migrations: {
    path: 'prisma/migrations',
    seed: 'tsx prisma/seed.ts',
  },
  datasource: {
    url: env('DATABASE_URL'),
  },
})
```

### 当前命令行为

- 在需要新鲜 Client 输出时，在 `migrate dev`, `db push` 或其他模式同步后显式运行 `prisma generate`
- 在需要种子数据时，在 `migrate dev` 或 `migrate reset` 后显式运行 `prisma db seed`
- 使用 `prisma db execute --file ...` 运行原始 SQL 脚本

### 环境变量

在 `prisma.config.ts` 中显式加载环境变量，通常使用 `dotenv`：

```typescript
// prisma.config.ts
import 'dotenv/config'
```

## 规则文件

查看各个命令的详细文档：

```
references/init.md           - 项目初始化
references/generate.md       - Client 生成
references/dev.md            - 本地开发数据库
references/db-pull.md        - 数据库内省
references/db-push.md        - 模式推送
references/db-seed.md        - 数据库种子
references/db-execute.md     - 原始 SQL 执行
references/migrate-dev.md    - 开发迁移
references/migrate-deploy.md - 生产迁移
references/migrate-reset.md  - 数据库重置
references/migrate-status.md - 迁移状态
references/migrate-resolve.md - 迁移解析
references/migrate-diff.md   - 模式差异
references/studio.md         - 数据库 GUI
references/mcp.md            - Prisma MCP 服务器
references/complete.md       - Shell 补全生成
references/agent-safety.md   - 破坏性命令的 AI 同意检查点
references/validate.md       - 模式验证
references/format.md         - 模式格式化
references/debug.md          - 调试信息
```

## 如何使用

使用上方的命令类别进行导航，然后打开您需要的特定命令参考文件。
