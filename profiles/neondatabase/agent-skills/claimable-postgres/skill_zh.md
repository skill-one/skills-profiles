**首先**：使用父级 `neon` 技能获取 Neon 概览、开始使用 Neon、Neon 开发最佳实践等内容。

如果未安装 `neon` 技能，请从 https://neon.com/docs/ai/skills/neon/SKILL.md 获取或使用以下命令安装：

```bash
npx skills add neondatabase/agent-skills --skill neon
```

# 可认领的 Postgres

用于本地开发、演示、原型设计和测试环境的即时 Postgres 数据库。无需账户。数据库在 72 小时后过期，除非被认领到 Neon 账户。

## 快速入门

```bash
curl -s -X POST "https://neon.new/api/v1/database" \
  -H "Content-Type: application/json" \
  -d '{"ref": "agent-skills"}'
```

从 JSON 响应中解析 `connection_string` 和 `claim_url`。将 `connection_string` 写入项目的 `.env` 文件作为 `DATABASE_URL`。

对于其他方法（CLI、SDK、Vite 插件），请参阅下方的 [哪种方法？](#which-method)。

## 哪种方法？

- **REST API**：返回结构化 JSON。除了 `curl` 之外无需其他运行时依赖。当代理需要可预测的输出和错误处理时首选。
- **CLI** (`npx neon-new@latest --yes`)：一键配置并写入 `.env`。当 Node.js 可用且用户希望简单设置时方便。
- **SDK** (`neon-new/sdk`)：在 Node.js 中进行脚本或程序化配置。
- **Vite 插件** (`vite-plugin-neon-new`)：如果 `DATABASE_URL` 缺失，在 `vite dev` 时自动配置。适用于具有 Vite 项目的用户。
- **浏览器**：用户无法运行 CLI 或 API。直接访问 https://neon.new。

## 自动配置

如果代理需要数据库来完成任务（例如“为我构建一个带有真实数据库的待办事项应用”），并且用户未提供连接字符串，请通过 API 配置一个并通知用户。包含认领 URL，以便他们保留。

## 代理工作流程

### API 路径

1. **确认意图**：如果请求不明确，请确认用户希望获得临时、无需注册的数据库。如果他们明确要求快速或临时数据库，则跳过此步骤。
2. **配置**：POST 到 `https://neon.new/api/v1/database` 并使用 `{"ref": "agent-skills"}`。
3. **解析响应**：从 JSON 响应中提取 `connection_string`、`claim_url` 和 `expires_at`。
4. **写入 .env**：将 `DATABASE_URL=<connection_string>` 写入项目的 `.env`（或用户的首选文件和键）。未经确认，不要覆盖现有键。
5. **种子（如果需要）**：如果用户有种子 SQL 文件，请在新数据库上运行它：
   ```bash
   psql "$DATABASE_URL" -f seed.sql
   ```
6. **报告**：涵盖 [输出清单](#output-checklist) 中的所有项目。
7. **可选**：提供快速连接测试（例如 `SELECT 1`）。

### CLI 路径

1. **检查 .env**：检查目标 `.env` 中是否存在 `DATABASE_URL`（或选择的键）。如果存在，则不运行。提供移除、`--env` 或 `--key` 并获取确认（请参阅 [预运行检查](#pre-run-check)）。
2. **确认意图**：如果请求不明确，请确认用户希望获得临时、无需注册的数据库。如果他们明确要求快速或临时数据库，则跳过此步骤。
3. **收集选项**：除非上下文暗示其他情况（例如，用户提到自定义环境文件、种子 SQL 或逻辑复制），否则使用默认值。
4. **运行**：使用 `@latest --yes` 加上确认的选项执行。始终使用 `@latest` 以避免过时的缓存版本。`--yes` 跳过会阻止代理的交互式提示。
   ```bash
   npx neon-new@latest --yes --ref agent-skills --env .env.local --seed ./schema.sql
   ```
5. **验证**：确认连接字符串已写入预期文件。
6. **报告**：涵盖 [输出清单](#output-checklist) 中的所有项目。
7. **可选**：提供快速连接测试（例如 `SELECT 1`）。

### 输出清单

始终报告：

- 连接字符串的写入位置（例如 `.env`）
- 使用的变量键（`DATABASE_URL` 或自定义键）
- 认领 URL（来自 `.env` 或 API 响应）
- 未认领的数据库是临时的（72 小时）：数据库现在可用，并在 72 小时内认领可永久保留

## 安全和 UX 注意事项

- 不要覆盖现有的环境变量。首先检查，然后使用 `--env` 或 `--key`（CLI）或跳过写入（API）以避免冲突。
- 在运行破坏性种子 SQL（`DROP`、`TRUNCATE`、大量 `DELETE`）之前，请先询问用户。
- 对于生产工作负载，建议使用标准 Neon 配置而不是临时可认领数据库。
- 如果用户需要长期持久化，请指示他们立即打开认领 URL。
- 将凭证写入 .env 文件后，检查它是否包含在 .gitignore 中。如果没有，请警告用户。未经确认，不要修改 `.gitignore`。

## REST API

**基本 URL**：`https://neon.new/api/v1`

### 创建数据库

```bash
curl -s -X POST "https://neon.new/api/v1/database" \
  -H "Content-Type: application/json" \
  -d '{"ref": "agent-skills"}'
```

| 参数                    | 是否必需 | 描述                                                                                                           |
| ----------------------- | -------- | --------------------------------------------------------------------------------------------------------------------- |
| `ref`                    | 是      | 用于标识谁配置了数据库的跟踪标签。通过此技能配置数据库时，请使用 `"agent-skills"`。                               |
| `enable_logical_replication` | 否       | 启用逻辑复制（默认：false，启用后无法禁用）                                                                  |

API 返回的 `connection_string` 是一个池化连接 URL。对于直接（非池化）连接（例如 Prisma 迁移），请从主机名中删除 `-pooler`。CLI 会自动写入池化和直接 URL。

**响应**：

```json
{
  "id": "019beb39-37fb-709d-87ac-7ad6198b89f7",
  "status": "UNCLAIMED",
  "neon_project_id": "gentle-scene-06438508",
  "connection_string": "postgresql://...",
  "claim_url": "https://neon.new/claim/019beb39-...",
  "expires_at": "2026-01-26T14:19:14.580Z",
  "created_at": "2026-01-23T14:19:14.580Z",
  "updated_at": "2026-01-23T14:19:14.580Z"
}
```

### 检查状态

```bash
curl -s "https://neon.new/api/v1/database/{id}"
```

返回相同的响应形状。状态转换：`UNCLAIMED` -> `CLAIMING` -> `CLAIMED`。数据库被认领后，`connection_string` 返回 `null`。

### 错误响应

| 条件              | HTTP | 消息                          |
| ---------------------- | ---- | -------------------------------- |
| 缺失或空的 `ref` | 400  | `Missing referrer`               |
| 无效的数据库 ID    | 400  | `Database not found`             |
| 无效的 JSON 正文      | 500  | `Failed to create the database.` |

## CLI

```bash
npx neon-new@latest --yes
```

一键配置数据库并将连接字符串写入 `.env`。始终使用 `@latest` 和 `--yes`（跳过会阻止代理的交互式提示）。

### 预运行检查

检查目标 `.env` 中是否存在 `DATABASE_URL`（或选择的键）。如果找到该键，CLI 将不会配置并退出。

如果键存在，请向用户提供三个选项：

1. 移除或注释掉现有行，然后重新运行。
2. 使用 `--env` 写入到不同的文件（例如 `--env .env.local`）。
3. 使用 `--key` 写入到不同的变量名。

在继续之前获取确认。

### 选项

| 选项                  | 别名 | 描述                                                           | 默认值        |
| ----------------------- | ----- | --------------------------------------------------------------------- | -------------- |
| `--yes`                 | `-y`  | 跳过提示，使用默认值                                            | `false`        |
| `--env`                 | `-e`  | .env 文件路径                                                        | `./.env`       |
| `--key`                 | `-k`  | 连接字符串环境变量键                                         | `DATABASE_URL` |
| `--prefix`              | `-p`  | 生成的公共环境变量的前缀                                      | `PUBLIC_`      |
| `--seed`                | `-s`  | 种子 SQL 文件路径                                                 | 无           |
| `--logical-replication` | `-L`  | 启用逻辑复制                                                    | `false`        |
| `--ref`                 | `-r`  | 引用 ID（通过此技能配置数据库时使用 `agent-skills`） | 无           |

替代包管理器：`yarn dlx neon-new@latest`、`pnpm dlx neon-new@latest`、`bunx neon-new@latest`、`deno run -A neon-new@latest`。

### 输出

CLI 写入目标 `.env`：

```
DATABASE_URL=postgresql://...              # 池化（用于应用查询）
DATABASE_URL_DIRECT=postgresql://...       # 直接（用于迁移，例如 Prisma）
PUBLIC_POSTGRES_CLAIM_URL=https://neon.new/claim/...
```

## SDK

用于脚本和程序化配置流程。

```typescript
import { instantPostgres } from "neon-new";

const { databaseUrl, databaseUrlDirect, claimUrl, claimExpiresAt } =
  await instantPostgres({
    referrer: "agent-skills",
    seed: { type: "sql-script", path: "./init.sql" },
  });
```

返回 `databaseUrl`（池化）、`databaseUrlDirect`（直接，用于迁移）、`claimUrl` 和 `claimExpiresAt`（Date 对象）。`referrer` 参数是必需的。

## Vite 插件

对于 Vite 项目，`vite-plugin-neon-new` 在 `vite dev` 时如果 `DATABASE_URL` 缺失，会自动配置数据库。使用 `npm install -D vite-plugin-neon-new` 安装。有关配置，请参阅 [可认领的 Postgres 文档](https://neon.com/docs/reference/claimable-postgres#vite-plugin)。

## 认领

认领是可选的。数据库在未认领的情况下立即可用。要可选认领，用户在浏览器中打开认领 URL，在那里他们登录或创建 Neon 账户以认领数据库。

- **API/SDK**：向用户提供创建响应中的 `claim_url`。
- **CLI**：`npx neon-new@latest claim` 会从 `.env` 中读取认领 URL 并自动打开浏览器。

用户无法将 Vercel 链接的组织认领到 Neon；他们必须选择另一个 Neon 组织。

## Neon 基础设施即代码 (`neon.ts`)

可认领的数据库是故意设计为一次性使用的，并通过上述 `neon.new` 配置，因此它们不由 `neon.ts` 管理。一旦用户将数据库认领到 Neon 账户，它就成为了一个正常的 Neon 项目——此时，`neon.ts`（Neon 的基础设施即代码文件）将用于管理它（请参阅 `neon` 技能的完整参考）：声明其分支应具有的服务、按分支程序化计算，并获取类型安全的环境变量。

```bash
npm i @neon/config
```

```typescript
// neon.ts
import { defineConfig } from "@neon/config/v1";

export default defineConfig({
  auth: true, // Neon Auth，一旦超出纯连接字符串的范围
  dataApi: true, // Data API
  branch: (branch) => (branch.exists ? {} : { ttl: "7d" }), // 临时非默认分支
});
```

```bash
neon config apply   # 配置声明的服务（neon deploy 是别名）
```

如果项目需要分支、多个服务或版本控制中的持久化基础设施，建议先认领，然后采用 `neon.ts`——而不是重新配置一次性可认领数据库。

## 默认值和限制

| 参数 | 值     |
| --------- | --------- |
| 提供商  | AWS       |
| 区域    | us-east-2 |
| Postgres  | 17        |

对于可认领数据库，区域无法更改。未认领的数据库有更严格的配额。认领后，限制将重置为免费计划的默认值。

|            | 未认领 | 认领（免费计划） |
| ---------- | --------- | ------------------- |
| 存储空间    | 100 MB    | 512 MB              |
| 传输   | 1 GB      | ~5 GB               |
| 分支   | 无        | 是                 |
| 过期时间 | 72 小时  | 无                |
