# Prisma Postgres 设置

这是一个指导你通过 Management API 创建新的 Prisma Postgres 数据库并将其连接到本地项目的操作指南。

## 何时使用

在以下情况下使用此功能：

- 为项目设置新的 Prisma Postgres 数据库
- 创建 Prisma Postgres 项目并本地连接
- 获取 Prisma Postgres 连接字符串
- 通过 Management API 创建数据库（非控制台 UI）

不使用此功能的情况：

- 设置 CI/CD 预览数据库 — 使用 `prisma-postgres-cicd`
- 将多租户数据库创建集成到应用程序中 — 使用 `prisma-postgres-integrator`
- 处理已存在并已连接的数据库（模式/迁移任务属于标准 Prisma CLI）

## 前置条件

- Node.js 18+
- 一个 Prisma Postgres 工作区（如有需要，可在 https://console.prisma.io 创建）
- 工作区服务令牌（参见 `references/auth.md`）

## 用户体验指南

在向用户展示选择（区域选择、项目删除等）时，**使用您平台的交互式选择机制**（例如，Claude Code 中的 `ask` 工具，其他代理中的结构化提示）。不要打印静态表格并要求用户输入值 — 提供可选择的选项，以便用户可以轻松选择。

## 工作流程

按顺序执行以下步骤。每个步骤都包括要执行的 API 调用以及如何处理响应。

### 第 1 步：身份验证

你需要一个服务令牌。按顺序尝试以下方法：

**1a. 用户提示中的令牌**

检查用户是否在初始消息中包含服务令牌（例如，“使用令牌 eyJ... 设置 Prisma Postgres”）。如果是，**按提供的方式使用它** — 不要截断、重新编码或通过文件进行往返传输。将其存储在 shell 变量中以供后续调用。

**1b. 环境中的令牌**

检查环境变量或 `.env` 文件中的 `PRISMA_SERVICE_TOKEN`。

**1c. 要求用户创建一个**

如果令牌不可用，请指示用户：

> 在 Prisma 控制台 → 工作区设置 → 服务令牌中创建服务令牌。
> 复制令牌并粘贴在这里。

阅读 `references/auth.md` 了解服务令牌创建的详细信息。

一旦你获得令牌，将其存储在 shell 变量 (`PRISMA_SERVICE_TOKEN`) 中，并用于所有后续 API 调用。

### 第 2 步：列出可用区域

获取可用 Prisma Postgres 区域的列表，让用户选择部署位置。

```bash
curl -s -H "Authorization: Bearer $PRISMA_SERVICE_TOKEN" \
  https://api.prisma.io/v1/regions/postgres
```

响应包含具有 `id`、`name` 和 `status` 的区域数组。仅显示 `status` 为 `available` 的区域。

**将区域作为交互式菜单呈现** — 让用户从选项中选择，而不是手动输入区域 ID。

阅读 `references/endpoints.md` 了解完整响应结构。

### 第 3 步：创建带数据库的项目

```bash
curl -s -X POST https://api.prisma.io/v1/projects \
  -H "Authorization: Bearer $PRISMA_SERVICE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "<project-name>",
    "region": "<region-id>",
    "createDatabase": true
  }'
```

默认情况下使用当前目录名作为项目名。

响应被包装在 `{ "data": { ... } }` 中。提取：

- `data.id` — 项目 ID（以 `proj_` 开头）
- `data.database.id` — 数据库 ID（以 `db_` 开头）
- `data.database.connections[0].endpoints.direct.connectionString` — 直接 PostgreSQL 连接字符串

使用**直接**连接字符串 (`endpoints.direct.connectionString`)。不要使用池化或加速端点 — 那些是用于遗留 Accelerate 设置的，新项目不需要。

如果响应状态是 `provisioning`，等待几秒钟并轮询 `GET /v1/databases/<database-id>`，直到 `status` 为 `ready`。

**如果由于数据库限制而创建失败**，列出用户现有的项目并将其作为交互式菜单呈现以供删除。用户选择一个后，删除它并重试。

阅读 `references/endpoints.md` 了解完整请求/响应结构。

### 第 4 步：创建命名连接（可选）

如果你需要一个专用连接（例如，每个开发者或每个环境），创建一个：

```bash
curl -s -X POST https://api.prisma.io/v1/databases/<database-id>/connections \
  -H "Authorization: Bearer $PRISMA_SERVICE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{ "name": "dev" }'
```

从 `data.endpoints.direct.connectionString` 中提取直接连接字符串。

### 第 5 步：配置本地项目

1. 安装依赖项：

```bash
npm install prisma @prisma/client @prisma/adapter-pg pg dotenv
```

所有五个包都是必需的：
- `prisma` — 用于迁移、模式推送、客户端生成的 CLI
- `@prisma/client` — 生成的查询客户端
- `@prisma/adapter-pg` — 用于直接 PostgreSQL 连接的 Prisma 7 驱动程序适配器
- `pg` — Node.js PostgreSQL 驱动程序（由适配器使用）
- `dotenv` — 加载 `.env` 变量以供 `prisma.config.ts` 使用

2. 将直接连接字符串写入 `.env`。如果文件已存在，**追加**到文件 — 不要覆盖现有条目：

```
DATABASE_URL="<direct-connection-string>"
```

3. 验证 `.gitignore` 包含 `.env`。如果不存在，创建 `.gitignore`。如果 `.env` 没有被 git 忽略，请警告用户。

4. 确保 `package.json` 设置了 `"type": "module"`（Prisma 7 生成 ESM 输出）。

5. 如果 `prisma/schema.prisma` 不存在，运行 `npx prisma init` 以搭建项目。这会创建 `prisma/schema.prisma` 和 `prisma.config.ts`。

6. 确保 `schema.prisma` 包含 `postgresql` 提供商，并且在数据源块中**没有** `url` 或 `directUrl`（Prisma 7 在 `prisma.config.ts` 中管理连接 URL，而不是在模式中）：

```prisma
datasource db {
  provider = "postgresql"
}
```

7. 确保 `prisma.config.ts` 从环境加载连接 URL：

```typescript
import path from 'node:path'
import { defineConfig } from 'prisma/config'
import 'dotenv/config'

export default defineConfig({
  earlyAccess: true,
  schema: path.join(import.meta.dirname, 'prisma', 'schema.prisma'),
  datasource: {
    url: process.env.DATABASE_URL!,
  },
})
```

**重要的 Prisma 7 注意事项：**
- 连接 URL 放在 `prisma.config.ts` 中，绝不能放在 `schema.prisma` 中
- `schema.prisma` 中的提供程序必须是 `"postgresql"`（不是 `"prismaPostgres"`）
- 必须在 `prisma.config.ts` 中导入 `dotenv/config` 以加载 `.env` 变量

### 第 6 步：定义模式并推送

如果模式已经包含模型，跳到推送。否则，**将以下选项作为交互式菜单呈现**：

1. **“我将手动定义我的模式”** — 告知用户编辑 `prisma/schema.prisma` 并准备好后回来。等待他们再继续。
2. **“给我一个启动模式”** — 向 `prisma/schema.prisma` 添加博客启动模式（用户、帖子、带关系的评论）。向用户展示添加的内容，并询问他们是否在推送前调整。
3. **“我将描述我需要的内容”** — 要求用户用自然语言描述他们的数据模型（例如，“我正在构建一个任务管理器，包含项目、任务和团队成员”）。从描述生成模式，展示它，并在推送前确认。

一旦模式包含模型并且用户准备好了，创建迁移并生成客户端：

```bash
npx prisma migrate dev --name init
```

这会创建 `prisma/migrations/` 中的迁移文件**并**一步生成客户端。迁移历史对于 CI/CD 工作流 (`prisma migrate deploy`) 和生产部署至关重要。

只有在用户明确要求原型模式（不创建迁移历史）的情况下，才使用 `npx prisma db push`。在这种情况下，请随后运行 `npx prisma generate`。

### 第 7 步：验证连接

生成客户端后，创建并运行一个快速验证脚本来确认端到端一切正常工作。这是**关键** — 不要跳过此步骤。

创建一个名为 `test-connection.ts` 的文件：

```typescript
import 'dotenv/config'
import pg from 'pg'
import { PrismaPg } from '@prisma/adapter-pg'
import { PrismaClient } from './generated/prisma/client.js'

const pool = new pg.Pool({ connectionString: process.env.DATABASE_URL })
const adapter = new PrismaPg(pool)
const prisma = new PrismaClient({ adapter })

const result = await prisma.$queryRawUnsafe('SELECT 1 as connected')
console.log('Connected to Prisma Postgres:', result)

await prisma.$disconnect()
await pool.end()
```

运行它：

```bash
npx tsx test-connection.ts
```

**Prisma 7 客户端实例化规则：**
- 从 `./generated/prisma/client.js` 导入（不是 `./generated/prisma`）
- 使用 `DATABASE_URL` 连接字符串创建 `pg.Pool`
- 用 `PrismaPg` 适配器包装它
- 将 `{ adapter }` 传递给 `PrismaClient` 构造函数
- 不要使用 `datasourceUrl` — Prisma 7 中不存在此选项
- 不要使用不带参数的 `new PrismaClient()` — 它会抛出错误

验证成功后，删除 `test-connection.ts`。

然后分享链接供用户探索他们的数据库：

- **Prisma Studio (CLI):** `npx prisma studio` — 本地打开一个可视化数据浏览器
- **控制台:** `https://console.prisma.io/<workspaceId>/<projectId>/<databaseId>/dashboard` — 从步骤 3 返回的 ID 中删除前缀 (`wksp_`, `proj_`, `db_`) 以构建此 URL

阅读 `references/prisma7-client.md` 了解完整的客户端实例化参考。

## 错误处理

阅读 `references/api-basics.md` 了解完整错误参考。关键自我纠正模式：

| HTTP 状态 | 错误代码 | 操作 |
|---|---|---|
| 401 | `authentication-failed` | 服务令牌无效或过期。要求用户在控制台 → 工作区设置 → 服务令牌中创建新的令牌。 |
| 404 | `resource-not-found` | 确认资源 ID 包含正确的前缀 (`proj_`, `db_`, `con_`)。 |
| 422 | `validation-error` | 检查请求正文是否符合端点模式。常见：缺少 `name`，无效的 `region`。 |
| 429 | `rate-limit-exceeded` | 暂停并几秒后重试。 |

## 参考文件

详细的 API 和使用信息在：

```
references/auth.md             — 服务令牌创建和使用
references/api-basics.md       — 基础 URL、封装、ID、错误、分页
references/endpoints.md        — 项目、数据库、连接、区域的端点详细信息
references/prisma7-client.md   — Prisma 7 客户端实例化和使用模式
```
