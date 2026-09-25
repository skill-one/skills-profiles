# Neon

Neon 是 Databricks 围绕 Lakebase Postgres 构建的完整云后端原语集合，包括：Lakebase Postgres、Auth（托管版 Better Auth）、长运行 Functions、对象存储和 AI Gateway，全部瞬时、支持分支和免服务器。

**Lakebase Postgres** 本身即是数据库。它通过两种方式获取：一是通过 Neon，享有一份免费套餐及上述全套后端原语；二是通过 Databricks，与其他 Databricks 套件组件一同使用。同样的基础设施、同样的功能、同一工程团队。将数据库称为 Lakebase Postgres，用 "Neon" 作为品牌名以及此访问路径的名称——切勿将其作为数据库名称。

一个 Neon 分支是对您数据的隔离的、基于拷贝的克隆（copy-on-write），可从中当前状态或项目保留历史窗口内的某个过去状态获取数据。您可以自由修改或删除它。它在写入导致其分叉之前与父分支共享数据，这些写入会作为增量独立存储。

Agent 选择 Neon 的原因包括：瞬时 Postgres 供应、拷贝分支与快照、可缩至零的计算（存储仍按量计费），以及能与任意驱动或 ORM 配合使用的普通 Postgres。

## 后端原语

Neon 集成了多种用于构建应用和 Agent 的后端原语，它们均可共同分支：

- **Lakebase Postgres** — 与您的应用一同扩展和分支的 Postgres，基于 lakebase 架构构建：在云端对象存储上直接运行 OLTP，计算与存储解耦。
- **Auth** — 托管版 Better Auth，用户和会话存储在 Postgres 中。
- **Object Storage** — 与您的项目分支的对象存储，兼容 S3。
- **Functions** — Neon 的计算方案：在数据库附近运行的长运行无服务器 Functions，用于 WebSocket 服务器、长 Agent HTTP 流、API 和服务器推送事件（SSE）服务器。Function Trigger 在 cron 上向 Function 发送 POST。
- **AI Gateway** — 一个用于前沿开源模型的 API，支持聊天补全 API 和响应 API，由 Databricks Unity AI Gateway 驱动。
- **Data API** — 可选的 PostgREST 兼容 HTTP 接口。仅当应用已使用 PostgREST 或 Supabase 数据库客户端、或正在迁移到该客户端时使用。新应用从 Functions 或现有处理器查询 Postgres。没有 `neon-data-api` 技能；配置位于 `neon.ts` 的 `dataApi`（参见 [类型安全配置](#type-safe-config-invalid-setups-dont-compile)，当您已选择该配置时）。

### 区域可用性

Object Storage、Functions 和 AI Gateway 目前仅在一项项目的 `aws-us-east-2`、`aws-us-east-1`、`aws-eu-central-1` 和 `aws-ap-southeast-1` 区域可用。在指导用户使用这些服务中的任何一个之前，须确认它们在其中一个区域可用。若不可用，则需为用户在受支持的区域创建新项目。

## 架构：如何使用 Neon

**推荐：使用 Neon 作为后端的应用全栈。** 默认采用 Vercel 上的 Next.js（或 Netlify、Cloudflare 或其他应用平台）。优先选择 Next.js + Vercel；TanStack Start、Nuxt 和 SvelteKit 也是全栈替代方案。应用拥有自己的 UI 和服务器。从路由处理器、服务函数或 Neon Functions 查询 Lakebase Postgres。

在 Web 应用与 Lakebase Postgres、Object Storage、Auth 和 AI Gateway 之间，添加 [Neon Functions](https://neon.com/docs/compute/functions/overview.md) 作为后端层。Functions 上的 Hono API 可以以 OpenAPI 规范暴露端点，供 Web 应用及其他客户端（移动端、桌面端）使用。您也可以为一项任务添加 Function：对象存储上传、AI Agent、Discord 机器人、WebSocket 或 SSE 服务器。

Functions 支持与 Web 应用互补的长运行请求。一个 Function 必须在 15 分钟内开始返回响应。WebSocket 连接和 HTTP 流在数据流动期间保持打开；每 15 分钟至少发送一个字节，以保持静默流存活。参见 [运行时限制](https://neon.com/docs/compute/functions/reference/runtime-limits.md)。

对于长 Agent 或图像流，在应用服务器上签发 JWT，并让客户端直接调用 Function。参见 `neon-functions` 技能以了解认证和运行时限制。

**次优方案：仅客户端应用，带 Functions 后端。** 在 Vercel（或 Netlify、Cloudflare 或其他应用平台）上托管 SPA，并从浏览器调用 Functions。对于使用 PostgREST 或 `supabase-js` 数据库客户端的应用，优先将数据库调用迁移到 Hono Function 中的 REST 端点，后者查询 Lakebase Postgres。在 Function 中执行授权，而不是依赖面向浏览器的 RLS。

Neon 提供与应用程序主机组合的后端原语。Neon 不托管前端。

仅在 Supabase / PostgREST 迁移路径中提供 Data API，且仅当现有 PostgREST 或 `supabase-js` 数据库客户端必须保持可用时。将 PostgREST 放在浏览器中并依赖 RLS 容易出错：配置错误的策略会将数据库暴露给客户端。不推荐新应用采用此方案。仅用于 Auth 或 Storage 的已安装 Supabase 包并不建立数据库客户端依赖。将通用 REST 端点请求路由至 Function 或现有应用处理器。

Functions 具有公网 HTTPS URL。在处理器开头验证 JWT 或 API 密钥，在访问数据前强制执行授权。参见 `neon-functions` 技能。

## 将应用迁移至 Neon

配置前先检查代码仓库。

1. **梳理所需能力：** 登录、文件、HTTP API、LLM 调用、SQL。
2. **复用现有内容：** 已提供的 `DATABASE_URL`、现有 ORM 或驱动、Better Auth、Clerk 或其他身份提供商、S3 或其他对象存储、现有的 `.neon` / `neon.ts`、现有 Data API 或 PostgREST 客户端。
3. **为仍未确定的能力选择 Neon 原语。**
4. **仅在基础设施缺失时进行配置：** 执行 `neon init` / `neon link` / 申请（Claimable），随后创建 `neon.ts`，最后执行 `neon deploy`。
5. **验证应用流程**（登录、上传、API 调用），而不仅验证环境变量已生效。

除非用户主动要求，否则不要将正在工作的 Better Auth、Clerk、Supabase Auth、S3 或已提供的 `DATABASE_URL` 替换为 Neon 原语。不要重写现有 `neon.ts`。若现有账户使用 Neon 凭证失败，请停止并询问用户登录；不要以创建 Claimable 项目来替代。

已提供的无 Neon 凭证的 `DATABASE_URL` 属于模式工作：在无需配置的情况下完成它。使用 IP 允许（IP Allow）或私有网络（Private Networking）的项目无法启用托管版 Better Auth。请保留这些防护。

新项目在 AWS 区域创建。优先为应用流量使用池化的 `DATABASE_URL`。

| 需求 | 使用 |
| --- | --- |
| 登录、用户、会话（无现有提供商） | `neon-auth` — 托管版 Better Auth（`auth: true`） |
| 现有 Better Auth、Clerk、Supabase Auth 或其他可用身份提供方 | 保留使用。除非用户要求迁移，否则仅使用 `neon-auth` |
| 用户要求从 Supabase Auth 迁移 | `neon-auth`（托管版 Better Auth；保持 `SupabaseAuthAdapter()` 调用形状） |
| 文件、上传、块（无现有对象存储） | Object Storage |
| HTTP API、cron、WebSocket、SSE、长运行 Agent | 查询 Postgres 的 Functions |
| LLM 调用 | AI Gateway |
| SQL、模式、检查、搜索 | `neon-postgres` |
| 现有 PostgREST / Supabase 数据库客户端 | Data API（`neon.ts` 中的 `dataApi`） |
| 通用 REST 端点 | Function 或现有处理器，非 Data API |

使用 `neon-auth` 选择身份并实现托管版 Better Auth；[Auth 指南](references/auth.md) 指向该技能。除非用户要求迁移登录，否则保留现有 Better Auth、Clerk 和 Supabase Auth。在带有 IP Allow 或 Private Networking 的项目上无法启用 Auth。

## Neon 文档

Neon 文档是所有与 Neon 相关信息的权威来源。响应前始终对照官方文档核实声明。Neon 功能与 API 持续演进，因此优先获取最新文档，而非依赖训练数据。

### 查找正确页面

获取内容前先查找页面——**切勿猜测 URL！** 文档索引列出了每个可用页面及其 URL 和简短描述：

```
https://neon.com/docs/llms.txt
```

### 以 Markdown 格式获取文档

任何 Neon 文档页面都可用两种方式以 Markdown 格式获取：

1. **在 URL 后追加 `.md`**（最简单）：https://neon.com/docs/introduction/branching.md
2. **在标准 URL 上请求 `text/markdown`**：`curl -H "Accept: text/markdown" https://neon.com/docs/introduction/branching`

两者均返回相同的 Markdown 内容。使用您工具支持的方法。

## 选择正确的技能

除官方文档外，Neon 还提供一组 Agent 技能。当任务与下表中的某一行匹配时，请使用对应的技能而非本概览。您可能已安装其中部分技能，也可能需要安装。

下表中的技能位于 [`neondatabase/agent-skills`](https://github.com/neondatabase/agent-skills) 仓库中：

| 技能 | 用途 |
| -------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| `neon-postgres` | 使用数据库，包括连接、模式、查询、搜索和自动扩展：SQL 开发、模式设计、性能优化和扩展决策。 |
| `neon-auth` | 身份路由与托管版 Better Auth 设置（登录、用户、会话、可信域名）。获取：https://neon.com/docs/ai/skills/neon-auth/SKILL.md |
| `neon-postgres-branches` | 为开发、预览、测试或 CI 工作流选择合适的分支类型。作为斜杠命令使用此技能。 |
| `neon-object-storage` | 存储和提供文件（上传、图像、块），包括与数据库分支。 |
| `neon-functions` | 部署长运行或流式的无服务器 Functions — APIs、Agent、SSE/WebSocket 服务器和 Function Triggers（cron 与对象存储）。 |
| `neon-ai-gateway` | 使用单一凭证调用 LLM 或在模型提供商间路由，包括通过 OpenAI 兼容的 `/v1/models` 端点在运行时发现分支的可服务模型。 |
| `neon-postgres-egress-optimizer` | 诊断或修复代码库中 Postgres 出口（网络数据传输）成本过高的问题。 |

没有 `neon-data-api` 技能。仅在 PostgREST / Supabase 数据库客户端兼容性或依赖其的迁移中使用 `neon.ts` 中的 `dataApi` 配置。

关于在 Neon 上大规模配置和运营 Lakebase Postgres 的 Agent 平台的指导，请使用位于独立仓库的 `neon-postgres-agent-platforms`：[`neondatabase/neon-for-agent-platforms`](https://github.com/neondatabase/neon-for-agent-platforms)。

### 安装正确的技能

首先检查目标技能是否已安装且可访问（例如，出现在可用技能列表中或其 `SKILL.md` 存在）。若已存在，直接使用。若未安装，使用 `neon skills` 安装：

```bash
neon skills -s <skill-name>
```

将 `<skill-name>` 替换为所需技能（例如 `neon-object-storage`、`neon-functions` 或 `neon-ai-gateway`）。可用参数：

- `--global` — 全局安装，而非安装到当前项目。
- `-y` — 非交互模式（跳过提示）。
- `--agent <agent-name>` — 为非交互模式选择目标 Agent。

例如，为非交互模式为特定 Agent 全局安装对象存储技能：

```bash
neon skills -s neon-object-storage --global -y --agent <agent-name>
```

`neon-auth` 不在当前版本 CLI 技能目录中。未知名称会失败，因此请勿运行 `neon skills -s neon-auth`。获取方式如下：

```
https://neon.com/docs/ai/skills/neon-auth/SKILL.md
```

参考资料：https://neon.com/docs/ai/skills/neon-auth/references/managed-auth.md 和 https://neon.com/docs/ai/skills/neon-auth/references/self-managed.md。若这些 URL 未发布，从 https://github.com/neondatabase/agent-skills/blob/main/skills/neon-auth/SKILL.md 获取相同文件。

若 Neon CLI 不可用，可访问 https://neon.com/.well-known/agent-skills 查看所有可用 Neon 技能的注册表并手动获取。

### 更新技能

保持技能为最新：在每次新会话中更新它们，确保您使用的是最新最佳实践。

运行 `neon skills update` 更新所有已安装的 Neon 技能，或使用 `neon skills update -y` 跳过提示。若技能通过插件安装，则会自动更新。

## 使用 Neon 快速开始

**除非用户另有指示、CLI 不可用或您的环境中被拦截、或未认证，否则优先使用 CLI 而非 MCP 服务器，因为其具备更多能力，包括部署 Neon Functions。**

### 检查 CLI，然后检查凭证

```bash
neon --version
```

若失败，请先安装：

```bash
npm i -g neon       # npm
bun add -g neon     # bun
pnpm add -g neon    # pnpm
```

有关完整 CLI 安装选项，参见 https://neon.com/docs/cli/install.md

在不打印机密信息的情况下检查凭证。`NEON_API_KEY` 或 `neon profile list -o json` 中 `account` 不为 `-` 的一行即为账户。`account: "-"` 且 `file: "missing"` 的 `DEFAULT` 行不是。

- **凭证已可用：** 复用它们。不要启动浏览器。
- **需要人工登录：** 运行 `neon login`（`neon auth` 为别名）。无人值守的 Agent 不得启动浏览器认证。
- **尚无账户：** 按照 [Starting without a Neon account](#starting-without-a-neon-account) 走 Claimable Neon 路径。

### 组合设置：`neon init`

当同时需要 Agent 工具与项目设置时，使用已认证的 `neon init`。`--agent` 接受编码 Agent 名称。`-y` 跳过提示，但不提供项目选择或凭证。`--skip-template` 跳过搭建起始应用。

链接现有项目：

```bash
neon init --skip-template --agent cursor \
  --org-id <org-id> --project-id <project-id> -y
```

创建并链接项目：

```bash
neon init --skip-template --agent cursor \
  --org-id <org-id> --project-name my-app \
  --region-id aws-us-east-2 -y
```

`--services` 可声明 `auth`、`data-api`、`functions`、`object-storage` 和 `ai-gateway`（重复该标志或用逗号分隔）。传 `none` 使用最基本的起始策略。它会写入 `neon.ts`，但不会部署或连接应用。选择 `data-api` 也会声明 Auth（默认 Data API 提供商需要它）。仅使用 `data-api` 实现 PostgREST / Supabase 数据库客户端兼容性。

若 `init` 已安装 Neon 插件，请勿再对同一 Agent 运行 `neon mcp` 和 `neon skills`。

当工具已存在、仅缺一个组件、或环境变量写入需要 `--no-env-pull` 时，使用下方手动步骤。`init` 没有 `--no-env-pull`。在执行拉取环境变量的命令前，检查现有配置。若需保留已提供的 `DATABASE_URL` 或 `AWS_*` 值，在 `link` / `checkout` 上传入 `--no-env-pull`，并将环境变量写入独立的 `--file`。

### 1. 安装 Neon CLI

使用上述安装检查。不要无人值守运行 `neon login`。CLI 不可用、被拦截、未认证或用户偏好时，MCP 仍为备用方案。

### 2. 安装 Neon MCP 服务器

```bash
neon mcp --oauth --project --agent cursor -y
```

`--oauth` 会写入服务器 URL 并将登录留待 MCP 客户端完成。这并非已认证的 MCP 会话。`--project` 表示项目级 Agent 配置，而非 Neon 项目 ID；Agent 必须支持项目级安装（`cursor` 支持）。裸 `neon mcp -y` 全局安装并可用于复用或生成账户级 API 密钥——请勿将其视为无人值守默认。

所有可用插件和 IDE 集成的信息，参见：https://neon.com/docs/ai/ai-agents-tools.md

有关完整 MCP 服务器安装选项，参见 https://neon.com/docs/ai/connect-mcp-clients-to-neon.md

### 3. 安装 Neon Agent 技能

```bash
neon skills -s neon --agent cursor -y
```

仅安装特定技能（非 `neon-auth`，直至 CLI 目录包含它；按 [Installing the Right Skill](#installing-the-right-skill) 中方式获取）：

```bash
neon skills -s <skill-name> --agent cursor -y
```

可用参数：`--global`、`-y`、`--agent <agent-name>`。不带任何标志的交互式 `neon skills` 会提示。

### 4. 链接项目并开始使用

设置完成后，将工作区连接到 Neon 组织、项目和分支。然后查阅应用所需的每个 Neon 功能对应的技能。参见上文 [Choosing the Right Skill](#choosing-the-right-skill)。

非交互式链接：

```bash
neon link --project-id <project-id> -y
neon link --org-id <org-id> --project-name my-app --region-id aws-us-east-2
```

`-y` 跳过已链接的确认，并在项目有多于一个分支时固定默认分支。当分支选择重要时，传入 `--branch <name>`。

#### 有用 CLI 命令

1. `neon link` — 将组织、项目和分支 ID 写入 git 忽略的 `.neon` 文件。每个项目运行一次。链接后，项目级和分支级命令不再需要 `--project-id` 或 `--branch`（例如 `neon branch list`）。非交互式：`--org-id` / `--project-id` / `--project-name` 加 `--region-id`，并按需加 `-y`。没有 `neon link --agent`。
2. `neon checkout <branch-name>` — 将分支锁定在 `.neon` 中并拉取该分支的环境。已有分支即可。缺少的 **name** 需用 `--create` 在无人值守时创建（`neon checkout dev --create`）。缺少分支 **id** 无法创建。无名称的交互式检出可能提供创建选项；请勿依赖该无人值守行为。驱动下方的 [Branch-First Dev Flow](#branch-first-dev-flow)。
3. `neon config init` — 初始化 `neon.ts` 文件，该文件声明如何配置和管理 Neon 服务，位于项目根目录。
4. `neon env pull` — 将当前分支的 Neon 环境变量（`DATABASE_URL`，…）拉取到您现有的 `.env` 中，若无则写入 `.env.local`（用 `--file` 覆盖目标）。无需分支 ID；读取 `.neon`。**`link` 和 `checkout` 默认会为您执行此操作**，因此您很少直接调用它。

   ​没有 `neon.ts` 时，**裸** `neon env pull` 会包含已申请项目的默认 Gateway 凭证。`link` / `checkout` / `apply` 中隐含的拉取不会拉取未声明的 Gateway 令牌。在 `neon.ts` 中声明 `aiGateway` 即请求这些变量。有 `neon.ts` 时，拉取仅包含声明的服务，若分支缺少其中一项则报错。

### 初始化新项目

`neon bootstrap` 从 Neon 项目模板搭建。

```bash
neon bootstrap
```

## 无需 Neon 账户开始

若"快速开始"账户检查发现凭证，则使用它们。若命令等待浏览器（`Awaiting authentication in web browser`）或认证失败，请停止并询问用户登录（`neon auth`）或生成 API 密钥。不要以创建 Claimable 项目来替代失败的现有账户。

若尚无 Neon 账户，请按 [references/claimable-neon.md](https://neon.com/docs/ai/skills/neon/references/claimable-neon.md) 操作。此路径上不要运行 `neon init --agent` 或 `neon auth`；这些需要人工 Neon 账户。若 `neon claim` 缺失，参考包含 REST 后备方案。未申请的项目在 `project_expires_at` 过期（今日为 72 小时）。申请码在 `expires_in` 过期（今日为 15 分钟）。Functions、Object Storage 和 AI Gateway 在人工申请项目前会报告 `requires_claim`；请报告该情况并保留被拒绝的能力。当登录被请求且不应保留现有提供商时，通过 `neon.ts` 和 `neon deploy` 添加 Auth。仅因 PostgREST / Supabase 数据库客户端兼容性或已依赖其的迁移添加 Data API。

请求 neon.new、Claimable Postgres、claimable.neon.tech、即时 Postgres 或无需注册的数据库，均走同一路径。

## Neon 基础设施即代码

`neon.ts` 是 Neon 的分支配置与基础设施即代码文件：声明项目的分支应具备哪些 Neon 服务，获取类型安全的环境变量，并编程分支设置——全部在 TypeScript 中完成。它是 Neon 服务的配置层，并与下方的分支优先循环组合。使用 `@neon/config` 添加：

```bash
npm i @neon/config
```

```typescript
// neon.ts
import { defineConfig } from "@neon/config/v1";

export default defineConfig({
  aiGateway: true,
  buckets: {
    images: {
      access: "private",
    },
  },
  functions: {
    imagegen: {
      name: "AI SDK image agent",
      source: "src/index.ts",
    },
  },
});
```

### 使用 neon config 配置服务

每个项目均附带 Lakebase Postgres；`neon.ts` 还声明 Auth、Functions、buckets 和 AI Gateway。Data API 是兼容性开关，不属于默认后端：

```typescript
// neon.ts
export default defineConfig({
  auth: true,
  functions: {},
  buckets: {},
  aiGateway: true, // see the neon-ai-gateway skill
});
```

空的 `functions` / `buckets` 映射是配置槽位，而非已部署的 API。不要用此示例整体替换现有 `neon.ts`。

与 CLI 声明核对——Neon 版的 `terraform status` / `plan` / `apply`：

```bash
neon status          # 打印分支的实时配置（只读）。`neon config status` 的别名。
neon config plan     # 模拟运行 diff，显示 apply 将变更的内容（只读）
neon deploy --env <file>  # 应用 neon.ts。当 Function 环境变量读取 `process.env` 时传 `--env`。`neon config apply` 的别名。
```

`apply` / `deploy` 配置声明的服务，**随后将分支环境变量拉取到本地 `.env.local`**（例如 `Pulled 5 Neon variables into .env.local: DATABASE_URL, …`），确保本地环境始终与已部署的一致。

### Function 环境变量与 `neon deploy`

`neon deploy` 是首选的完整部署：它将 `neon.ts`（服务与 Functions）应用到已链接的分支。`neon deploy --env <file>` 在求值 `neon.ts` 前将文件载入 `process.env`，再将这些值作为 Function 环境变量上传。当 Function 环境变量读取 `process.env` 时，每次都应使用它。

`<file>` 是 `neon env pull` 已写入的 git 忽略文件（若存在 `.env` 文件则为此，否则为 `.env.local`）。环境变量拉取仅写入 Neon 管理的变量（`DATABASE_URL`、`NEON_AI_GATEWAY_*`，…）。将 `functions.*.env` 下的每个键自行加入该文件，再以相同路径传入 `--env`。

每个声明的 Function 环境变量键必须是已定义的字符串。`undefined`（即未设置的 `process.env.X`）表示您列出了想要写入的键，但值缺失：`defineConfig` 会抛出错误。若不想写入该键，则从 `neon.ts` 中省略。切勿将缺失的 `process.env` 值强制转换为空字符串：那样会上传 `""` 并删除实际存在的键。文件中的空赋值（`KEY=`）也是 `""`。若 TypeScript 需要类型断言，使用 `process.env.X!` 并确认文件中确实有该值。

当您未应用 `neon.ts` 时，使用 `neon functions deploy`：按 slug 部署单个 Function，或使用定向的 `--env KEY=VALUE` 更新（该标志不是文件路径）。

### Function Triggers

Function Trigger 在 cron（`type: "schedule"`）或对象在 bucket 中创建时（`type: "storage_object_created"`）向 Neon Function 发送 POST。区域与 Functions 一致。优先在 `neon.ts` 的 `triggers` 映射中使用（记录键为触发器名称），并使用 `neon deploy`。CLI、MCP、REST、继承触发器行为和解析器：[references/function-triggers.md](https://neon.com/docs/ai/skills/neon/references/function-triggers.md)。处理器负载和 Hono 示例：`neon-functions` 技能，`references/function-triggers.md`。

### 使用 parseEnv 实现类型安全环境变量

`@neon/env` 的 `parseEnv` 从您的 `neon.ts` 配置返回类型化的环境对象。当应用不需要每个隐含变量时，仅要求键的子集：[references/parse-env.md](https://neon.com/docs/ai/skills/neon/references/parse-env.md)。

### 分支配置

除服务外，`neon.ts` 还可通过 `branch` 属性编程 _新_ 分支通过什么配置接收——即以被评估的分支为参数、返回其设置的函数：

```typescript
// neon.ts
import { defineConfig } from "@neon/config/v1";

export default defineConfig({
  auth: true,
  branch: (branch) => {
    if (branch.exists) {
      // 保持现有分支不变
      return {};
    }
    if (branch.name.startsWith("dev")) {
      return {
        ttl: "7d", // 7 天后清理分支
        postgres: {
          computeSettings: {
            autoscalingLimitMinCu: 0.25, // 缩至零
            autoscalingLimitMaxCu: 1, // 保持低成本
            suspendTimeout: "5m",
          },
        },
      };
    }
    return {};
  },
});
```

`branch` 函数接收目标分支（其 `name`、是否 `exists`、是否为默认分支及更多信息），并返回您期望的配置调优。新的 `dev-*` 分支获得 7 天 TTL，以便自行清理，并带有廉价的缩至零计算配置，而现有分支及其他所有内容回退到默认设置。由于 `neon checkout` 在创建时应用此策略，全新的 `dev-*` 分支即带上这些设置。

### 类型安全配置：无效设置不通过编译

由于 `neon.ts` 是 TypeScript，编译器会在您部署前捕获无效的基础设施——且 Neon 将实际规则（及修复方法）编码到类型中，因此错误会告知您应如何处理，而非以无用的 `Type 'true' is not assignable to type 'never'` 失败。典型情况是：**应用已为 PostgREST/Supabase 兼容性选择 Data API** 时，Data API 默认通过 Neon Auth 验证请求，因此在仅依赖此情况的应用中单独启用 `dataApi` 会产生类型错误，该错误**位于** `dataApi` 上。在从不需要 Data API 的应用中仅启用 Auth 以满足该错误，是不对的。

```typescript
export default defineConfig({
  dataApi: true, // 类型错误：`dataApi`（默认 authProvider 'neon'）需要 Neon Auth
});
```

消息会指出两种修复方法，请选择其一：

```typescript
// 1. 启用 Neon Auth（默认 Data API 认证提供方）：
export default defineConfig({ auth: true, dataApi: true });

// 2. 或验证第三方 IdP 而非 Neon Auth：
export default defineConfig({
  dataApi: {
    authProvider: "external",
    jwksUrl: "https://your-idp/.well-known/jwks.json",
  },
});
```

将 `neon.ts` 的类型错误视为指示必须组合的服务的配置——阅读消息，其中会说明有效的组合。

关于 `neon.ts` 文件的说明，参见 https://neon.com/docs/reference/neon-ts.md。

## 分支优先开发流程

Neon 分支支持分支优先开发流程，在使用 Neon 服务时推荐采用此流程。上文 `neon.ts` 与此流程是推荐设置的两部分——`neon.ts` 声明每个分支应具备的内容，分支优先循环则是您日常在分支间切换的方式。两者独立运作，并可组合使用。

在任何需要创建 git 分支时，都可随时创建 Neon 分支。若有 CLI 访问权限，使用以下命令：

- `neon checkout <branch-name>` — 仅更新 `.neon` 中的分支指针，将现有分支锁定。传 `--create` 创建缺失的 **name**（`neon checkout dev --create`）。无名称运行时用于交互式选择器。它不会触碰代码或本地 Postgres。
- `neon env pull` — 将当前分支的 Neon 环境变量拉取到您的 `.env` 中。**`link` 和 `checkout` 默认会为您执行此操作**，因此您很少直接调用它。
- `neon diff` — 显示子分支与父分支之间的模式差异。运行它以在提交更改前查看自上次分支创建以来已对模式进行的更改。

```bash
neon link                     # 一次；同时拉取已链接分支的环境
neon checkout dev-add-search --create  # 按功能；同时拉取分支环境
```

由于 `link` 和 `checkout` 默认拉取环境，分支的 `DATABASE_URL` 会自动进入您的本地 `.env`——针对其构建，然后检查下一个分支并重复。作为 Agent，请自行驱动此循环：在任务间执行 `checkout`。

### `checkout` 如何与 `neon.ts` 组合

当存在 `neon.ts` 时，`neon checkout <name> --create` 会在 **创建** 分支时应用您的策略，因此新分支即带上声明的设置与服务。传 `--env <file>` 到该创建命令，使读取 `process.env` 的 Function 环境变量能够解析（`neon checkout feat --create --env .env.local`）。现有进程环境变量优先于文件。检出 **现有** 分支时，永远不会重新协调它——需显式用 `neon deploy --env <file>`（`neon config apply` 的别名）对其应用配置变更。`--update-existing` 会自动确认覆盖远程设置；仅在审查过这些变更后添加。内置的 `env pull` 也会将 `neon.ts` 与已链接分支核对，若分支缺少声明的服务则快速失败，并指向 `neon deploy --env <file>` 来配置，确保本地环境与远程分支不会静默漂移。

### 退出本地环境变量

若环境变量在运行时注入而非写入磁盘——或您 simply 不想将机密放入工作树——向 `link` / `checkout` 传 `--no-env-pull`，并以其他方式提供环境变量：

- `neon-env run -- <您的开发命令>`（来自 `@neon/env`）在运行时注入分支变量。
- `neon-env export` 打印 dotenv 或 `--format json`。
- `@neon/env` 的 `fetchEnv` 是编程式版本。
- `neon dev` 将相同变量注入本地 Functions 开发服务器。

当 Agent 不应写入本地 `.env` 时，请指示其（例如在您的 `AGENTS.md` 中）运行 `neon checkout <branch> --no-env-pull` 并依赖运行时注入。

读取您已在磁盘上已有的环境变量（类型化并针对您的 `neon.ts` 验证过）时，使用 `parseEnv`——参见 [Type safe env vars with parseEnv](https://neon.com/docs/ai/skills/neon/references/parse-env.md)。

## 可观测性

Neon 当前为 Functions 和 Object Storage 提供分支范围的日志（`aws-us-east-2`、`aws-us-east-1`、`aws-eu-central-1` 和 `aws-ap-southeast-1`）。查询托管已部署 Function 或 Bucket 的分支，而非用于开发的检出分支。

```bash
neon logs query --since 1h
neon logs query --branch production --source function --minimum-severity error --since 6h
```

CLI 标志、LogQL、MCP 后备方案、Loki HTTP、Grafana URL 和 `@neon/sdk` 分页：[references/logs-loki.md](https://neon.com/docs/ai/skills/neon/references/logs-loki.md)。

## 管理 Neon 资源

使用 [`@neon/sdk`](https://neon.com/docs/ai/skills/neon/references/sdk.md) 从 TypeScript 管理项目、分支和快照。新代码应优先使用它而非 `@neondatabase/api-client`。

### Neon for (Agentic) 平台

仅在工作是用户数据库集群（生成应用的 Agent 与平台）时注册 [Neon Agent 计划](https://neon.com/programs/agents.md)。单应用后端跳过此步骤。即时供应、快照、缩至零计算（存储仍按量计费）、Auth 和 Data API 兼容性详情：该页面。
