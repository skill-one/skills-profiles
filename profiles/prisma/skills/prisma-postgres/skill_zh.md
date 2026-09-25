# Prisma Postgres

创建、管理和集成 Prisma Postgres 的指南，适用于交互式和程序化工作流。

## 何时应用

在以下情况下参考此技能：
- 从 Prisma Console 设置 Prisma Postgres
- 使用 `create-db` 创建即时临时数据库
- 使用 `prisma postgres link` 链接现有本地项目
- 通过管理 API 管理Prisma Postgres 资源
- 在 TypeScript/JavaScript 中使用 `@prisma/management-api-sdk`
- 处理声明 URL、连接字符串、区域和认证流程

## 按优先级分类的规则类别

| 优先级 | 类别 | 影响 | 前缀 |
|--------|------|------|------|
| 1 | CLI 创建 | 关键 | `create-db-cli` |
| 2 | 管理 API | 关键 | `management-api` |
| 3 | 管理 API SDK | 高 | `management-api-sdk` |
| 4 | 控制台和连接 | 高 | `console-and-connections` |

## 快速参考

- `create-db-cli` - 即时数据库和当前 CLI 标志 (`--ttl`, `--copy`, `--quiet`, `--open`)
- `management-api` - 服务令牌和 OAuth API 工作流
- `management-api-sdk` - 带令牌存储的 TypeScript/JavaScript 类型化 SDK 使用
- `console-and-connections` - 控制台操作、`prisma postgres link`、直接 TCP 连接和 serverless-driver 选择

## 核心工作流

### 1. 控制台优先工作流

使用 Prisma 控制台进行手动设置和操作：

- 打开 `https://console.prisma.io`
- 创建/选择工作区和项目
- 在项目侧边栏中使用 Studio 查看/编辑数据
- 从项目 UI 中获取直接连接详情

### 2. 使用 create-db 快速创建

当您需要立即使用数据库时，使用 `create-db`：

```bash
npx create-db@latest
```

别名：

```bash
npx create-pg@latest
npx create-postgres@latest
```

对于应用集成，您还可以使用 `create-db` npm 包中的程序化 API (`create()` / `regions()`).

临时数据库在 ~24 小时后自动删除，除非被声明。

### 2b. 使用 Platform CLI 创建持久数据库

对于属于项目（非 `create-db` 临时数据库）的数据库，使用 `@prisma/cli`：

```bash
npx -y @prisma/cli@latest database create --help
npx -y @prisma/cli@latest database list --json
npx -y @prisma/cli@latest database connection create db_123
npx -y @prisma/cli@latest database usage db_123
npx -y @prisma/cli@latest database backup list db_123
```

`database create` 和 `database connection create` 打印一次性连接 URL；立即存储它。破坏性命令 (`remove`, `restore`) 需要 `--confirm <id>` 的精确确认。

对于自动化，优先使用 `--json --no-interactive`，在变异前解析 ID，并验证已安装命令的帮助信息，因为此 CLI 是 Beta 版。

### 3. 链接现有本地项目

当数据库已存在且您想将其与本地项目连接时，使用 `prisma postgres link`：

```bash
prisma postgres link
```

对于 CI 或其他非交互式环境：

```bash
prisma postgres link --api-key "<your-api-key>" --database "db_..."
```

此流程将 `DATABASE_URL` 更新到本地 `.env`，然后您可以运行 `prisma generate` 和 `prisma migrate dev`。

### 4. 使用管理 API 进行程序化创建

使用以下地址上的 API 端点：

```text
https://api.prisma.io/v1
```

使用以下方式探索模式和端点：

- OpenAPI 文档：`https://api.prisma.io/v1/doc`
- Swagger 编辑器：`https://api.prisma.io/v1/swagger-editor`

认证选项：

- 服务令牌（工作区服务器到服务器）
- OAuth 2.0（代表用户操作）

### 5. 使用管理 API SDK 进行类型安全的集成

安装和使用：

```bash
npm install @prisma/management-api-sdk
```

使用 `createManagementApiClient` 用于现有令牌，或使用 `createManagementApiSdk` 用于 OAuth + 令牌刷新。

SDK 暴露了类型化的工作区服务令牌列表、创建和撤销路由。新创建的令牌值只返回一次。让已安装的 SDK 类型或 OpenAPI 文档稳定 Beta 端点形状。

## 规则文件

详细指南位于：

```
references/console-and-connections.md
references/create-db-cli.md
references/management-api.md
references/management-api-sdk.md
```

## 如何使用

从 `references/create-db-cli.md` 开始快速设置，当您需要程序化创建时，切换到 `references/management-api.md` 或 `references/management-api-sdk.md`。
