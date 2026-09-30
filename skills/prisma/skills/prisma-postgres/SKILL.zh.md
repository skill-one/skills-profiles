---
name: prisma-postgres
description: Prisma Postgres 的设置和操作指南，涵盖控制台、create-db 命令行工具、管理 API 和管理 API SDK。在创建 Prisma Postgres 数据库、使用 Prisma 控制台、通过 create-db/create-pg/create-postgres 进行配置，或使用服务令牌或 OAuth 进行程序化配置时使用。
---

# Prisma Postgres

创建、管理和集成 Prisma Postgres 的指南，适用于交互式和程序化工作流。

## 适用场景

在以下情况下参考此技能：
- 从 Prisma Console 设置 Prisma Postgres
- 使用 `create-db` 快速创建临时数据库
- 使用 `prisma postgres link` 将现有本地项目与数据库关联
- 通过 Management API 管理Prisma Postgres资源
- 在TypeScript/JavaScript中使用 `@prisma/management-api-sdk`
- 处理声明URL、连接字符串、区域和认证流程

## 按优先级分类的规则类别

| 优先级 | 类别 | 影响 | 前缀 |
|----------|----------|--------|--------|
| 1 | CLI创建 | CRITICAL | `create-db-cli` |
| 2 | Management API | CRITICAL | `management-api` |
| 3 | Management API SDK | HIGH | `management-api-sdk` |
| 4 | 控制台和连接 | HIGH | `console-and-connections` |

## 快速参考

- `create-db-cli` - 快速数据库和当前CLI标志 (`--ttl`, `--copy`, `--quiet`, `--open`)
- `management-api` - 服务令牌和OAuth API工作流
- `management-api-sdk` - 带令牌存储的类型安全SDK使用
- `console-and-connections` - 控制台操作、`prisma postgres link`、直接TCP连接和serverless驱动选择

## 核心工作流

### 1. 控制台优先工作流

使用 Prisma 控制台进行手动设置和操作：

- 打开 `https://console.prisma.io`
- 创建/选择工作区和项目
- 在项目侧边栏中使用 Studio 查看或编辑数据
- 从项目界面获取直接连接详情

### 2. 使用 create-db 快速创建

当你需要立即获取数据库时，使用 `create-db`：

```bash
npx create-db@latest
```

别名：

```bash
npx create-pg@latest
npx create-postgres@latest
```

对于应用集成，你也可以使用 `create-db` npm包中的程序化API (`create()` / `regions()`).

临时数据库在约24小时后自动删除，除非被声明。

### 2b. 使用 Platform CLI 创建持久数据库

对于属于项目（非一次性 `create-db` 数据库）的数据库，使用 `@prisma/cli`：

```bash
npx -y @prisma/cli@latest database create --help
npx -y @prisma/cli@latest database list --json
npx -y @prisma/cli@latest database connection create db_123
npx -y @prisma/cli@latest database usage db_123
npx -y @prisma/cli@latest database backup list db_123
```

`database create` 和 `database connection create` 会打印一次性连接URL；立即保存它。破坏性命令 (`remove`, `restore`) 需要精确的 `--confirm <id>`。

对于自动化，优先使用 `--json --no-interactive`，在变异前解析ID，并验证已安装命令的帮助信息，因为此CLI处于Beta阶段。

### 3. 关联现有本地项目

当数据库已存在且你想将本地项目连接到它时，使用 `prisma postgres link`：

```bash
prisma postgres link
```

对于CI或其他非交互式环境：

```bash
prisma postgres link --api-key "<your-api-key>" --database "db_..."
```

此流程会更新你的本地 `.env` 文件中的 `DATABASE_URL`，然后你可以运行 `prisma generate` 和 `prisma migrate dev`。

### 4. 使用 Management API 程序化创建

使用以下地址的API端点：

```text
https://api.prisma.io/v1
```

使用以下方式探索模式和端点：

- OpenAPI文档：`https://api.prisma.io/v1/doc`
- Swagger Editor：`https://api.prisma.io/v1/swagger-editor`

认证选项：

- 服务令牌（工作区服务器到服务器）
- OAuth 2.0（代表用户操作）

### 5. 使用 Management API SDK 进行类型安全集成

安装和使用：

```bash
npm install @prisma/management-api-sdk
```

使用 `createManagementApiClient` 用于现有令牌，或使用 `createManagementApiSdk` 用于OAuth + 令牌刷新。

SDK暴露了类型化的工作区服务令牌列表、创建和撤销路由。新创建的令牌值只会返回一次。让已安装的SDK类型或OpenAPI文档稳定精确的Beta端点形状。

## 规则文件

详细指南位于：

```
references/console-and-connections.md
references/create-db-cli.md
references/management-api.md
references/management-api-sdk.md
```

## 如何使用

从 `references/create-db-cli.md` 开始快速设置，当你需要程序化创建时，切换到 `references/management-api.md` 或 `references/management-api-sdk.md`。
