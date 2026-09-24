# Prisma Postgres

在交互式和工作流程序中创建、管理并集成 Prisma Postgres 的指南。

## 何时应用

参考此技能，当：
- 从 Prisma Console 设置 Prisma Postgres
- 使用 `create-db` 配置即时临时数据库
- 使用 `prisma postgres link` 将现有本地项目关联
- 通过 Management API 管理 Prisma Postgres 资源
- 在 TypeScript/JavaScript 中使用 `@prisma/management-api-sdk`
- 处理认领 URL、连接字符串、区域及认证流程

## 按优先级划分的规则类别

| 优先级 | 类别 | 影响 | 前缀 |
|----------|----------|--------|--------|
| 1 | CLI 配置部署 | 关键 | `create-db-cli` |
| 2 | Management API | 关键 | `management-api` |
| 3 | Management API SDK | 高 | `management-api-sdk` |
| 4 | 控制台与连接 | 高 | `console-and-connections` |

## 快速参考

- `create-db-cli` - 即时数据库及当前 CLI 参数 (`--ttl`、`--copy`、`--quiet`、`--open`)
- `management-api` - 服务令牌及 OAuth API 工作流
- `management-api-sdk` - 带令牌存储的类型化 SDK 使用
- `console-and-connections` - 控制台操作、`prisma postgres link`、直接 TCP 连接及 serverless-driver 选择

## 核心工作流

### 1. 控制台优先的工作流

使用 Prisma Console 进行手动设置与操作：

- 打开 `https://console.prisma.io`
- 创建/选择工作区与项目
- 在项目侧边栏中使用 Studio 查看/编辑数据
- 从项目界面获取直接连接详情

### 2. 使用 create-db 快速配置

当需要立即获取数据库时使用 `create-db`：

```bash
npx create-db@latest
```

别名：

```bash
npx create-pg@latest
npx create-postgres@latest
```

对于应用集成，还可以使用 `create-db` npm 包中的编程 API（`create()` / `regions()`）。

除非被认领，否则临时数据库在约 24 小时后自动删除。

### 2b. 使用平台 CLI 创建持久数据库

对于属于 Project（而非一次性 `create-db` 数据库）的数据库，使用 `@prisma/cli`：

```bash
npx -y @prisma/cli@latest database create --help
npx -y @prisma/cli@latest database list --json
npx -y @prisma/cli@latest database connection create db_123
npx -y @prisma/cli@latest database usage db_123
npx -y @prisma/cli@latest database backup list db_123
```

`database create` 和 `database connection create` 会一次性打印连接 URL；请立即保存。
破坏性命令（`remove`、`restore`）要求使用精确的 `--confirm <id>`。

用于自动化时，建议使用 `--json --no-interactive`，在执行变更前解析 id，并验证已安装命令的 `--help`，因为该 CLI 处于测试（beta）阶段。

### 3. 关联现有本地项目

当数据库已存在且您希望将本地项目关联到该数据库时，使用 `prisma postgres link`：

```bash
prisma postgres link
```

对于 CI 或其他非交互式环境：

```bash
prisma postgres link --api-key "<your-api-key>" --database "db_..."
```

此流程会将 `DATABASE_URL` 更新到本地 `.env`，然后您可以运行 `prisma generate` 和 `prisma migrate dev`。

### 4. 通过 Management API 进行编程式配置

使用以下 API 端点：

```
https://api.prisma.io/v1
```

通过以下方式探索 schema 和端点：
- OpenAPI 文档：`https://api.prisma.io/v1/doc`
- Swagger 编辑器：`https://api.prisma.io/v1/swagger-editor`

认证选项：
- 服务令牌（工作区服务端到服务端）
- OAuth 2.0（代表用户执行操作）

### 5. 使用 Management API SDK 实现类型安全集成

安装并使用：

```bash
npm install @prisma/management-api-sdk
```

使用 `createManagementApiClient` 处理现有令牌，或使用 `createManagementApiSdk` 进行 OAuth + 令牌刷新。

该 SDK 提供了工作区服务令牌列表、创建和撤销的路由。新创建令牌的值仅返回一次。请让已安装的 SDK 类型或 OpenAPI 文档确定确切的 beta 端点形状。

## 规则文件

详细指引位于：

```
references/console-and-connections.md
references/create-db-cli.md
references/management-api.md
references/management-api-sdk.md
```

## 使用方法

快速设置从 `references/create-db-cli.md` 开始，当需要编程式配置时，再切换到 `references/management-api.md` 或 `references/management-api-sdk.md`。
