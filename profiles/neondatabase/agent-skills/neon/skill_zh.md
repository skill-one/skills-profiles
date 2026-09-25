# Neon

Neon 是围绕 Lakebase Postgres 的完整云后端原语集，由 Databricks 提供 — Lakebase Postgres、Auth（管理的 Better Auth）、长时间运行的 Functions、对象存储和 AI Gateway，所有这些都是即时的、可分支的和无服务器的。

**Lakebase Postgres** 是数据库本身。它是一个产品，可以通过两种方式访问：通过 Neon，带有免费计划和支持的后端原语集，或通过 Databricks，与 Databricks 套件的其他部分一起使用。相同的基础设施、相同的功能、相同的工程团队。将数据库称为 Lakebase Postgres，并将 "Neon" 用于品牌和此访问路径 — 不要将其用作数据库的名称。

Neon 分支是您数据的隔离的、写时复制克隆，可以从其当前状态或其项目保留历史窗口中的过去状态获取。您可以自由地修改或删除它。它与父分支共享数据，直到写入导致它分叉，并且这些写入作为增量独立存储。

代理选择 Neon 以便即时提供 Postgres、写时复制分支和快照、可扩展到零的计算（存储仍然计费）以及任何驱动程序或 ORM 都可以工作的普通 Postgres。

## 后端原语

Neon 为构建一起分支的应用程序和代理捆绑了几个后端原语：

- **Lakebase Postgres** — 随您的应用程序扩展和分支的 Postgres，基于 lakebase 架构构建：直接在云对象存储上进行 OLTP，存储与计算解耦。
- **Auth** — 管理的 Better Auth，用户和会话存储在 Postgres 中。
- **Object Storage** — 与 S3 兼容的对象存储，与您的项目一起分支。
- **Functions** — Neon 的计算提供：长时间运行的、无服务器的函数，在靠近您数据库的位置运行，用于 WebSocket 服务器、长时间代理 HTTP 流、API 和服务器发送事件服务器。Function Trigger 向 cron 上的函数 POST。
- **AI Gateway** — 一个 API，用于前沿和开源模型，支持聊天完成 API 和响应 API，由 Databricks Unity AI Gateway 提供。
- **Data API** — 可选的 PostgREST 兼容 HTTP 接口。仅在应用程序已经使用 PostgREST 或 Supabase 数据库客户端，或者正在迁移该客户端时使用它。新应用程序从 Functions 或现有处理程序查询 Postgres。没有 `neon-data-api` 技能；配置是 `neon.ts` 中的 `dataApi`（在您选择它时查看 [Type-safe config](#type-safe-config-invalid-setups-dont-compile)）。

### 区域可用性

对象存储、Functions 和 AI Gateway 目前在 `aws-us-east-2`、`aws-us-east-1`、`aws-eu-central-1` 和 `aws-ap-southeast-1` 的项目中可用。在引导用户使用任何这些服务之前，请确认他们正在这些区域之一工作。如果不是，他们需要在一个支持的区域中创建一个新项目。

## 架构：如何使用 Neon

**推荐：使用 Neon 作为后端的全栈应用程序。** 默认情况下，在 Vercel 上使用 Next.js（或 Netlify、Cloudflare 或其他应用程序平台）。首先优先考虑 Next.js + Vercel；TanStack Start、Nuxt 和 SvelteKit 是全栈替代方案。应用程序拥有其 UI 和服务器。从路由处理程序、服务器函数或 Neon Functions 查询 Lakebase Postgres。

在 Web 应用程序和 Lakebase Postgres、对象存储、Auth 和 AI Gateway 之间添加 [Neon Functions](https://neon.com/docs/compute/functions/overview.md) 作为后端层。Hono API 在 Functions 上可以暴露端点，为 Web 应用程序和其他客户端（移动、桌面）提供 OpenAPI 规范。您还可以添加一个 Function 用于一个作业，与数据并置：对象存储上传、AI 代理、Discord 机器人、WebSocket 或 SSE 服务器。

Functions 支持长时间运行的请求，以补充 Web 应用程序。Function 必须在 15 分钟内开始返回响应。WebSocket 连接和 HTTP 流在数据流时保持打开；每 15 分钟至少发送一个字节以保持安静流 alive。有关 [运行时限制](https://neon.com/docs/compute/functions/reference/runtime-limits.md) 的信息。

对于长时间代理或图像流，在应用程序服务器上铸造 JWT，并让客户端直接调用 Function。有关身份验证和运行时限制，请参阅 `neon-functions` 技能。

**第二好的：只有客户端的应用程序，带有 Functions 后端。** 将 SPA 托管在 Vercel 上（或 Netlify、Cloudflare 或其他应用程序平台），并从浏览器调用 Functions。对于使用 PostgREST 或 `supabase-js` 数据库客户端的应用程序，请优先将数据库调用迁移到 Hono Function 中的 REST 端点，以查询 Lakebase Postgres。在 Function 中而不是依赖浏览器面的 RLS 执行授权。

Neon 提供后端原语，与应用程序主机组合。Neon 不托管前端。

仅当现有 PostgREST 或 `supabase-js` 数据库客户端必须继续工作时，才提供 Data API 作为 Supabase / PostgREST 迁移路径。在浏览器中放置 PostgREST 并依赖 RLS 容易出错：配置错误的政策会使数据库暴露给客户端。不建议为新应用程序推荐此选项。仅用于 Auth 或存储的已安装 Supabase 包不会建立数据库客户端依赖关系。将通用 REST 端点请求路由到 Function 或现有应用程序处理程序。

Functions 具有公共 HTTPS URL。在处理程序顶部验证 JWT 或 API 密钥，并在访问数据之前执行授权。有关 `neon-functions` 技能的信息。

## 将应用程序转换为 Neon

在配置之前检查存储库。

1. 映射请求的功能：登录、文件、HTTP API、LLM 调用、SQL。
2. 重用已有的内容：提供的 `DATABASE_URL`、现有的 ORM 或驱动程序、Better Auth、Clerk 或另一个身份验证提供程序、S3 或另一个对象存储、现有的 `.neon` / `neon.ts`、现有的 Data API 或 PostgREST 客户端。
3. 为尚未确定的功能选择 Neon 原语。
4. 仅当缺少基础设施时才配置：`neon init` / `neon link` / 可声明，然后 `neon.ts`，然后 `neon deploy`。
5. 验证应用程序流程（登录、上传、API 调用），而不仅仅是环境变量已到达。

除非用户要求，否则不要用 Neon 原语替换工作正常的 Better Auth、Clerk、Supabase Auth、S3 或提供的 `DATABASE_URL`。不要重写现有的 `neon.ts`。如果 Neon 凭据对现有帐户失败，请停止并要求用户登录；不要创建 Claimable 项目作为替代。

带有 Neon 凭据的 `DATABASE_URL` 是模式工作：在不配置的情况下完成它。在 IP 允许或私有网络使用的项目中无法启用管理的 Better Auth。保留这些保护措施。

新项目在 AWS 区域中创建。优先考虑池化的 `DATABASE_URL` 用于应用程序流量。

| 需要 | 使用 |
| --- | --- |
| 登录、用户、会话（没有现有的提供程序） | `neon-auth` — 管理的 Better Auth (`auth: true`) |
| 现有的 Better Auth、Clerk、Supabase Auth 或另一个工作 IdP | 保持它。`neon-auth` 仅当他们要求迁移 |
| 用户要求从 Supabase Auth 迁移 | `neon-auth`（管理的 Better Auth；保留 `SupabaseAuthAdapter()` 调用形状） |
| 文件、上传、blobs（没有现有的对象存储） | 对象存储 |
| HTTP API、cron、WebSocket、SSE、长时间运行的代理 | Functions 查询 Postgres |
| LLM 调用 | AI Gateway |
| SQL、模式、检查、搜索 | `neon-postgres` |
| 现有的 PostgREST / Supabase 数据库客户端 | Data API (`dataApi` 在 `neon.ts`) |
| 通用 REST 端点 | Function 或现有处理程序，而不是 Data API |

使用 `neon-auth` 选择身份并实现管理的 Better Auth；[Auth 指南](references/auth.md) 指向那里。除非用户要求迁移登录，否则保留现有的 Better Auth、Clerk 和 Supabase Auth。Auth 不能在具有 IP 允许或私有网络的项目中启用。

## Neon 文档

Neon 文档是所有 Neon 相关信息的来源。在回复之前，始终根据官方文档验证声明。Neon 功能和 API 在不断发展，因此优先获取当前文档而不是依赖训练数据。

### 找到正确的页面

在获取页面之前查找它 — **不要猜测 URL！** 文档索引列出了每个可用页面及其 URL 和简短描述：

```
https://neon.com/docs/llms.txt
```

### 以 Markdown 形式获取文档

任何 Neon 文档页面都可以以两种方式获取为 Markdown：

1. **将 `.md` 添加到 URL**（最简单）：https://neon.com/docs/introduction/branching.md
2. **在标准 URL 上请求 `text/markdown`**：`curl -H "Accept: text/markdown" https://neon.com/docs/introduction/branching`

两者都返回相同的 Markdown 内容。使用您的工具支持的方法。

## 选择正确的技能

除了官方文档之外，Neon 还提供一组代理技能。当任务匹配下表中的某一行时，请从该技能开始，而不是从此概述。您可能已经安装了其中一些技能，或者您可能需要安装它们。

下表中的技能位于 [`neondatabase/agent-skills`](https://github.com/neondatabase/agent-skills) 存储库中：

| 技能 | 使用它来 |
| --- | --- |
| `neon-postgres` | 与数据库一起工作，包括连接、模式、查询、搜索和自动缩放：SQL 开发、模式设计、性能优化和缩放决策。 |
| `neon-auth` | 身份路由和管理的 Better Auth 设置（登录、用户、会话、受信任的域）。获取：https://neon.com/docs/ai/skills/neon-auth/SKILL.md |
| `neon-postgres-branches` | 为 dev、预览、测试或 CI 工作流程选择或创建正确的分支类型。作为斜杠命令使用此技能。 |
| `neon-object-storage` | 存储和服务文件（上传、图像、blobs），包括与数据库一起分支。 |
| `neon-functions` | 部署长时间运行或流式无服务器函数 — API、代理、SSE/WebSocket 服务器和 Function Trigger（cron 和对象存储）。 |
| `neon-ai-gateway` | 调用 LLM 或跨模型提供程序路由，使用一个凭证，包括在运行时发现分支的可服务模型，通过 OpenAI 兼容的 `/v1/models` 端点。 |
| `neon-postgres-egress-optimizer` | 诊断或修复代码库中过度 Postgres 出口（网络数据传输）成本。 |

没有 `neon-data-api` 技能。仅在需要 Data API 以便 PostgREST/Supabase 数据库客户端兼容性或已经依赖它的迁移时，在 `neon.ts` 中配置 `dataApi`。

对于有关在 Neon 上规模提供和操作 Lakebase Postgres 的代理平台的指导，请使用 `neon-postgres-agent-platforms`，它位于单独的存储库中：[`neondatabase/neon-for-agent-platforms`](https://github.com/neondatabase/neon-for-agent-platforms)。

### 安装正确的技能

首先检查目标技能是否已经安装并可访问（例如，它出现在可用技能列表中或其 `SKILL.md` 存在）。如果是，请直接使用它。如果尚未安装，请使用 `neon skills` 安装它：

```bash
neon skills -s <skill-name>
```

将 `<skill-name>` 替换为您需要的技能名称（例如，`neon-object-storage`、`neon-functions` 或 `neon-ai-gateway`）。有用的标志：

- `--global` — 在当前项目中而不是全局安装。
- `-y` — 非交互模式（跳过提示）。
- `--agent <agent-name>` — 为非交互模式选择目标代理。

例如，要全局为特定代理安装对象存储技能而不提示：

```bash
neon skills -s neon-object-storage --global -y --agent <agent-name>
```

`neon-auth` 不在当前发布的 CLI 技能目录中。未知名称会失败，因此不要运行 `neon skills -s neon-auth`。获取它：

```
https://neon.com/docs/ai/skills/neon-auth/SKILL.md
```

参考资料：https://neon.com/docs/ai/skills/neon-auth/references/managed-auth.md 和 https://neon.com/docs/ai/skills/neon-auth/references/self-managed.md。如果这些 URL 未发布，请从 https://github.com/neondatabase/agent-skills/blob/main/skills/neon-auth/SKILL.md 获取相同的文件。如果 Neon CLI 不可用，您可以访问 https://neon.com/.well-known/agent-skills 获取所有可用 Neon 技能的注册表并手动获取它们。

### 更新技能

保持技能更新：对于每个新会话，更新它们，以便您使用最新的最佳实践。

运行 `neon skills update` 更新所有已安装的 Neon 技能，或 `neon skills update -y` 跳过提示。如果技能是通过插件安装的，则它们会自动更新。

## 使用 Neon 入门

**优先使用 CLI 而不是 MCP 服务器** 除非用户指示否则，CLI 不可用或被阻止在您的环境中，或者它未经过身份验证，因为它提供了更多功能，包括部署 Neon Functions。

### 检查 CLI，然后凭据

```bash
neon --version
```

如果失败，请先安装：

```bash
npm i -g neon       # npm
bun add -g neon     # bun
pnpm add -g neon    # pnpm
```

有关完整的 CLI 安装选项，请参阅 https://neon.com/docs/cli/install.md

然后在不打印密钥的情况下检查凭据。`NEON_API_KEY` 或 `neon profile list -o json` 中 `account` 不是 `-` 的行是一个帐户。带有 `account: "-"` 的 `DEFAULT` 行和 `file: "missing"` 不是。

- 凭据已经可用：重用它们。不要启动浏览器。
- 需要人工登录：他们运行 `neon login` (`neon auth` 是一个别名)。一个无人看管的代理不得启动浏览器身份验证。
- 尚未创建帐户：按照 [没有 Neon 帐户的入门](#starting-without-a-neon-account) 进行 Claimable Neon 路径。

### 组合设置：`neon init`

当需要代理工具和项目设置时，使用经过身份验证的 `neon init`。`--agent` 接受编码代理名称。`-y` 跳过提示，但不会提供项目选择或凭据。`--skip-template` 跳过构建启动应用程序。

链接现有项目：

```bash
neon init --skip-template --agent cursor \
  --org-id <org-id> --project-id <project-id> -y
```

创建和链接项目：

```bash
neon init --skip-template --agent cursor \
  --org-id <org-id> --project-name my-app \
  --region-id aws-us-east-2 -y
```

`--services` 可以声明 `auth`、`data-api`、`functions`、`object-storage` 和 `ai-gateway`（重复标志或逗号分隔）。传递 `none` 以获取基本的启动策略。它写入 `neon.ts`；它不会部署或连接应用程序。选择 `data-api` 还会声明 Auth（默认 Data API 提供程序需要它）。仅当需要 Data API 以便 PostgREST / Supabase 数据库客户端兼容性或已经依赖它的迁移时，才使用它。

如果 `init` 已经安装了 Neon 插件，则不要同时运行 `neon mcp` 和 `neon skills` 为同一个代理。

当工具已经存在时，或者只有一个组件缺失，或者环境写入需要 `--no-env-pull`，请使用下面的手动步骤。`init` 没有参数 `--no-env-pull`。在执行命令拉取环境之前，请检查现有配置。如果必须保留提供的 `DATABASE_URL` 或 `AWS_*` 值，请在 `link` / `checkout` 上传递 `--no-env-pull` 并将环境写入到单独的 `--file`。

### 1. 安装 Neon CLI

使用上面的安装检查。不要运行未经提示的 `neon login`。当 CLI 不可用、被阻止、未经过身份验证或用户更喜欢它时，MCP 保持后备。

### 2. 安装 Neon MCP 服务器

```bash
neon mcp --oauth --project --agent cursor -y
```

`--oauth` 写入服务器 URL 并将登录留给 MCP 客户端。这不是一个经过身份验证的 MCP 会话。`--project` 意味着项目级代理配置，而不是 Neon 项目 ID；代理必须支持项目级安装（`cursor` 执行）。裸 `neon mcp -y` 安装全局，可以重用或铸造一个帐户范围的 API 密钥——不要将其视为未经提示的默认值。

有关所有可用的插件和 IDE 集成，请参阅：https://neon.com/docs/ai/ai-agents-tools.md

有关完整的 MCP 服务器安装选项，请参阅 https://neon.com/docs/ai/connect-mcp-clients-to-neon.md

### 3. 安装 Neon Agent Skills

```bash
neon skills -s neon --agent cursor -y
```

仅安装特定技能（不包括 `neon-auth`，直到 CLI 目录包含它；按照 [安装正确的技能](#installing-the-right-skill) 获取它）：

```bash
neon skills -s <skill-name> --agent cursor -y
```

有用的标志：`--global`, `-y`, `--agent <agent-name>`。带有标志的交互式 `neon skills`。

### 4. 链接您的项目并开始使用

设置完成后，将工作区连接到 Neon 组织、项目和分支。然后参考每个 Neon 功能所需的技能。请参阅上面的 [选择正确的技能](#choosing-the-right-skill)。

非交互式链接：

```bash
neon link --project-id <project-id> -y
neon link --org-id <org-id> --project-name my-app --region-id aws-us-east-2
```

`-y` 跳过已链接确认并固定默认分支（如果项目有多个）。当分支选择很重要时，传递 `--branch <name>`。

#### 有用的 CLI 命令

1. `neon link` — 将组织、项目和分支 ID 写入 git 忽略的 `.neon` 文件。每个项目运行一次。链接后，项目和分支范围命令不再需要 `--project-id` 或 `--branch`（例如，`neon branch list`）。非交互式：`--org-id` / `--project-id` / `--project-name` 加上 `--region-id`，以及适当时候的 `-y`。没有 `neon link --agent`。
2. `neon checkout <branch-name>` — 在 `.neon` 中固定分支并拉取该分支的环境。足够的现有分支就足够了。一个缺失的 **名称** 需要 `--create` 以便在未经提示的情况下使用（`neon checkout dev --create`）。一个缺失的分支 **ID** 无法创建。无名称的交互式检查可能会提供创建选项；不要依赖那个未经提示的。驱动 [分支优先开发流程](#branch-first-dev-flow) 以下。

因为 `neon.ts` 存在，`neon checkout <name> --create` 在创建分支时应用您的策略，因此一个新分支已经带有其声明的设置和服务。在创建时传递 `--env <file>` 以便 Function 环境读取 `process.env`（`neon checkout feat --create --env .env.local`）。检查现有进程环境优先于文件。检查现有分支永远不会重新同步它——显式地使用 `neon deploy --env <file>` 应用配置更改（别名 `neon config apply`）。`--update-existing` 自动确认覆盖远程设置；仅在审查了这些更改后添加它。捆绑的 `env pull` 还会检查 `neon.ts` 对链接的分支，如果分支缺少声明的服务，则会快速失败，指向 `neon deploy --env <file>` 以便配置它，因此您的本地环境和远程分支永远不会默默地分叉。

### 选择不使用本地环境变量

如果环境变量在运行时注入而不是写入磁盘——或者您只是不想在工作树中包含密钥——请将 `--no-env-pull` 传递给 `link` / `checkout` 并以其他方式提供环境：

- `neon-env run -- <your dev command>`（从 `@neon/env`）在运行时注入分支的变量。
- `neon-env export` 打印 dotenv 或 `--format json`。
- `fetchEnv` 从 `@neon/env` 是程序化版本。
- `neon dev` 将相同的变量注入到本地 Functions 开发服务器。

当代理不应写入本地 `.env` 时，请指示它（例如在您的 `AGENTS.md`）运行 `neon checkout <branch> --no-env-pull` 并依赖运行时注入。

对于您已经拥有的磁盘上的环境变量（类型化并验证为您的 `neon.ts`），请使用 `parseEnv`——请参阅 [使用 parseEnv 获取类型安全的环境变量](https://neon.com/docs/ai/skills/neon/references/parse-env.md)。

## 可观察性

Neon 目前为 Functions 和 Object Storage 提供分支范围日志（`aws-us-east-2`、`aws-us-east-1`、`aws-eu-central-1` 和 `aws-ap-southeast-1`）。查询托管函数或桶的分支，而不是用于开发的检查用例。

```bash
neon logs query --since 1h
neon logs query --branch production --source function --minimum-severity error --since 6h
```

CLI 标志、LogQL、MCP 后备、Loki HTTP、Grafana URL 和 `@neon/sdk` 分页：[参考资料/logs-loki.md](https://neon.com/docs/ai/skills/neon/references/logs-loki.md)。

## 管理 Neon 资源

使用 [`@neon/sdk`](https://neon.com/docs/ai/skills/neon/references/sdk.md) 从 TypeScript 管理项目、分支和快照。新代码应优先选择它而不是 `@neondatabase/api-client`。

### Neon for (Agentic) Platforms

仅在工作是用户数据库的舰队（应用程序生成代理和平台）时加入 [Neon Agent Program](https://neon.com/programs/agents.md)。单个应用程序后端跳过此选项。即时提供、快照、可扩展到零的计算（存储仍然计费）、Auth 和 Data API 兼容性详细信息：该页面。
