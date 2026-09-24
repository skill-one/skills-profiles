# Prisma CLI 参考

Prisma ORM CLI 命令的参考文档。本技能提供当前 Prisma ORM 发布版本中命令使用、选项和最佳实践的指导。

## 边界：平台与计算

不要混淆稳定的 ORM 命令（`prisma`）与公开的 Beta 版 Platform 包（`@prisma/cli`，二进制文件 `prisma-cli`）。使用 `prisma-compute` 进行 Compute 应用和 workspace 身份验证，使用 `prisma-postgres` 进行 Platform 项目和数据库操作。

## 适用场景

在以下情况参考本技能：
- 设置新的 Prisma 项目（`prisma init`）
- 生成 Prisma Client（`prisma generate`）
- 执行数据库迁移（`prisma migrate`）
- 管理数据库状态（`prisma db push/pull`）
- 使用本地开发数据库（`prisma dev`）
- 调试 Prisma 问题（`prisma debug`）
- 生成 Shell 补全（`prisma complete`）

## 按优先级划分的规则类别

| 优先级 | 类别 | 影响 | 前缀 |
|----------|----------|--------|--------|
| 1 | 设置 | HIGH | `init` |
| 2 | 生成 | HIGH | `generate` |
| 3 | 开发 | HIGH | `dev` |
| 4 | 数据库 | HIGH | `db-` |
| 5 | 迁移 | CRITICAL | `migrate-` |
| 6 | 工具 | MEDIUM | `complete`、`studio`、`validate`、`format`、`debug`、`mcp` |

## 命令类别

| 类别 | 命令 | 用途 |
|----------|----------|---------|
| 设置 | `init` | 初始化 Prisma 项目 |
| 生成 | `generate` | 生成 Prisma Client |
| 验证 | `validate`、`format` | Schema 验证与格式化 |
| 开发 | `dev` | 本地 Prisma Postgres 开发 |
| 数据库 | `db pull`、`db push`、`db seed`、`db execute` | 直接数据库操作 |
| 迁移 | `migrate dev`、`migrate deploy`、`migrate reset`、`migrate status`、`migrate diff`、`migrate resolve` | Schema 迁移 |
| 工具 | `complete`、`studio`、`mcp`、`version`、`debug` | Shell、开发与 AI 工具 |

## 快速参考

### 项目设置

```bash
# 初始化新项目（创建 prisma/ 文件夹和 prisma.config.ts）
prisma init

# 使用特定数据库初始化
prisma init --datasource-provider postgresql
prisma init --datasource-provider mysql
prisma init --datasource-provider sqlite

# 使用 Prisma Postgres（云端）初始化
prisma init --db

# 使用示例模型初始化
prisma init --with-model

```

### Client 生成

```bash
# 生成 Prisma Client
prisma generate

# 开发中的监视模式
prisma generate --watch

# 仅生成特定生成器
prisma generate --generator client
```

### Bun 运行时

使用 Bun 时，始终添加 `--bun` 参数，以便 Prisma 以 Bun 运行时运行（否则因 CLI 的 shebang 会回退到 Node.js）：

```bash
bunx --bun prisma init
bunx --bun prisma generate
```

### 本地开发数据库

```bash
# 启动本地 Prisma Postgres
prisma dev

# 以特定名称启动
prisma dev --name myproject

# 后台（分离）启动
prisma dev --detach

# 列出所有本地实例
prisma dev ls

# 停止实例
prisma dev stop myproject

# 移除实例数据
prisma dev rm myproject
```

### 数据库操作

```bash
# 从现有数据库拉取 schema
prisma db pull

# 向数据库推送 schema（无迁移）
prisma db push

# 初始化数据库种子数据
prisma db seed

# 执行原始 SQL
prisma db execute --file ./script.sql
```

### 迁移（开发）

```bash
# 创建并应用迁移
prisma migrate dev

# 使用名称创建迁移
prisma migrate dev --name add_users_table

# 创建迁移但不应用
prisma migrate dev --create-only

# 重置数据库并应用所有迁移
prisma migrate reset
```

### 迁移（生产环境）

```bash
# 应用待执行的迁移（CI/CD）
prisma migrate deploy

# 检查迁移状态
prisma migrate status

# 对比 schema 并生成差异
prisma migrate diff --from-config-datasource --to-schema schema.prisma --script
```

### 工具命令

```bash
# 打开 Prisma Studio（数据库图形界面）
prisma studio

# 启动 Prisma 的 MCP 服务器供 AI 工具使用
prisma mcp

# 显示版本信息
prisma version
prisma -v

# 调试信息
prisma debug

# 验证 schema
prisma validate

# 格式化 schema
prisma format

# 生成 Shell 补全代码
prisma complete zsh
```

## AI 安全检查点

Prisma 在检测到 AI 代理执行破坏性命令时，会阻止该操作，直至代理获得用户的明确同意。这包括 `migrate reset`、`db push --force-reset` 和 `db push --accept-data-loss`。

- 在执行命令前，立即说明具体的数据丢失影响并获取同意。
- 不要从之前的或无关的信息中推断同意。
- 如果自动化需要同意变量，将 `PRISMA_USER_CONSENT_FOR_DANGEROUS_AI_ACTION` 设置为用户的确切同意信息。不要编造文本。
- Prisma MCP 服务器有意不包含 `migrate-reset` 工具。

在运行任何破坏性 Prisma 命令前，阅读 `references/agent-safety.md`。

## Prisma CLI 当前设置

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

- 需要获取最新的客户端输出时，在 `migrate dev`、`db push` 或其他 schema 同步之后明确运行 `prisma generate`
- 需要填充数据时，在 `migrate dev` 或 `migrate reset` 之后明确运行 `prisma db seed`
- 使用 `prisma db execute --file ...` 执行原始 SQL 脚本

### 环境变量

在 `prisma.config.ts` 中明确加载环境变量，通常使用 `dotenv`：

```typescript
// prisma.config.ts
import 'dotenv/config'
```

## 规则文件

请查看单个规则文件以获取详细的命令文档：

```
references/init.md           - 项目初始化
references/generate.md       - Client 生成
references/dev.md            - 本地开发数据库
references/db-pull.md        - 数据库内省
references/db-push.md        - Schema 推送
references/db-seed.md        - 数据库种子数据
references/db-execute.md     - 原始 SQL 执行
references/migrate-dev.md    - 开发迁移
references/migrate-deploy.md - 生产环境迁移
references/migrate-reset.md  - 数据库重置
references/migrate-status.md - 迁移状态
references/migrate-resolve.md - 迁移解决
references/migrate-diff.md   - Schema 差异对比
references/studio.md         - 数据库图形界面
references/mcp.md            - Prisma MCP 服务器
references/complete.md       - Shell 补全生成
references/agent-safety.md   - 破坏性命令的 AI 同意检查点
references/validate.md       - Schema 验证
references/format.md         - Schema 格式化
references/debug.md          - 调试信息
```

## 使用方法

使用上述命令类别进行导航，然后打开所需的特定命令参考文件。
