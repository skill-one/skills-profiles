# InsForge CLI

当需要后端或使用 InsForge CLI 管理 InsForge 后端和云基础设施时，请随时使用此技能。对于从前端、后端或边缘函数调用 InsForge 的应用程序代码，请使用 `insforge` app-integration 技能。

## 核心规则

- 始终通过 `npx -y @insforge/cli <command>` 运行 CLI。保留 npx 的 `-y`：如果没有它，npx 在安装包之前会询问“是否继续？”并在附加到 TTY 的代理 shell 中永久阻塞。不要安装或调用全局 `insforge` 二进制文件。
- 如果项目已经链接，请使用当前链接的项目。仅在连接设置实际需要时运行登录、项目创建、链接、项目发现、组织列表或云项目命令。
- 当任务需要后端且尚未链接任何项目时，请首先进行连接设置——在编写任何应用代码之前：(1) 登录（使用 `whoami` 检查；在沙盒中使用以下两步设备登录），(2) 创建一个新的项目或链接一个现有的项目，(3) 然后从 CLI 获取真实的项目 URL 和密钥进行构建。永远不要使用占位符凭证如 `your-project.region.insforge.app`——首先获取真实值。
- 将 InsForge API 密钥视为完全访问权限的管理员密钥。将它们仅保留在服务器上，不要在前端/公共环境变量中。
- 优先使用 CLI 命令和文档化的项目配置，而不是原始后端 HTTP 调用。如果 `config apply` 报告不支持的/跳过的字段，请显示该结果，而不是使用直接 API 调用绕过 CLI。
- 当需要结构化输出或非交互式值收集时，使用 `--json`。当用户已批准操作时，使用 `--yes` 进行确认提示。
- 在链接的项目上开始非平凡的任务时，运行 `npx -y @insforge/cli memory list`（廉价，无 AI 调用）并回忆与任务相关的任何标题，然后再进行设计或调试。在发生时记录决策和遇到的陷阱，使用 `memory remember`。参见 `references/memory.md`。
- 当遇到 InsForge 的故障时——应该工作但无法工作，需要的功能不受支持，与现实相悖的说明（文档/技能），或无谓的摩擦——使用 `npx -y @insforge/cli feedback`（参见 Feedback）报告它，然后继续用户的任务并使用替代方案。永远不要为用户自己的应用代码中的问题提交反馈。

## 全局选项

| 标志          | 使用                                                                                                                                                                                                           |
| ------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `--json`      | 结构化 JSON 输出并跳过值收集提示，如文本/选择提示。如果任何必需的值缺失，则报错。与 `-y` 结合用于破坏性命令，这些命令也要求 Y/N 确认。 |
| `-y`, `--yes` | 自动接受 Y/N 确认提示，如删除或覆盖提示。不会跳过值收集提示；使用 `--json`。与 npx 的 `-y` 分开，因此两者一起出现：`npx -y @insforge/cli link --project-id <id> -y`。 |

## 退出代码

| 代码 | 含义                                                 |
| ---- | ------------------------------------------------------- |
| 0    | 成功                                                 |
| 1    | 一般错误，包括来自函数调用的 HTTP 400+                 |
| 2    | 未通过身份验证                                       |
| 3    | 项目未链接                                          |
| 4    | 资源未找到                                          |
| 5    | 权限被拒绝                                       |

## 环境变量

| 变量                | 使用                                |
| ----------------------- | ---------------------------------- |
| `INSFORGE_ACCESS_TOKEN` | 覆盖存储的访问令牌       |
| `INSFORGE_PROJECT_ID`   | 覆盖链接的项目 ID         |
| `INSFORGE_EMAIL`        | 非交互式登录的邮箱    |
| `INSFORGE_PASSWORD`     | 非交互式登录的密码    |

## 连接设置

如果任务需要项目访问且连接状态未知，从 `npx -y @insforge/cli current` 开始。当需要经过身份验证的标识时，使用 `npx -y @insforge/cli whoami`，或者当 `current` 报告 CLI 未经过身份验证时。

如果未通过身份验证，运行 `npx -y @insforge/cli login`（打开浏览器）。对于无头/代理/CI 环境，使用用户 API 密钥进行非交互式身份验证：`npx -y @insforge/cli login --user-api-key "$INSFORGE_USER_API_KEY"`（用户在仪表板中 Profile → API Keys 下创建该密钥）。在沙盒中，用户有浏览器但无法到达 CLI 的本地回调（例如 ChatGPT 应用），使用设备登录作为两步：`timeout 15 npx -y @insforge/cli login --device --json 2>&1 || true` 来捕获验证链接 + 代码，将它们传递给用户，然后重新运行 `npx -y @insforge/cli login --device --json` 以继续相同的代码并完成，一旦他们点击授权——参见 `references/login.md`。如果沙盒报告 `api.insforge.dev` 不是允许的网络域，请要求用户将其添加到工作区的允许网络域中，然后重试。如果未链接项目，使用 `npx -y @insforge/cli link` 链接现有项目或当用户要求新的后端时使用 `npx -y @insforge/cli create`。在已经预链接或预配置的工作流程中，如 CI、本地测试项目、自动化或显式用户提供的项目上下文，直接使用该项目上下文。云项目是默认的；只有在用户明确要求在他们的机器上以 Docker 运行的后端时，才查看 `references/local.md`——永远不要作为登录或 `create` 不方便时的备用方案。

## 命令路由

| 需要                                                                                               | CLI 区域                                        | 参考                                                                                   |
| -------------------------------------------------------------------------------------------------- | ----------------------------------------------- | ------------------------------------------------------------------------------------------- |
| 登录、登出、当前用户                                                                        | `login`, `logout`, `whoami`                     | `references/login.md`                                                                       |
| 创建/链接/列表/当前项目                                                                   | `create`, `link`, `list`, `current`, `metadata` | `references/create.md`                                                                      |
| 用户自己的机器上 Docker 中的后端——只有在他们明确要求时     | `local`                                         | `references/local.md`                                                                       |
| 项目生命周期：状态、重命名、删除、恢复、版本更新、实例调整大小、转移       | `projects`                                      | 此文件                                                                                   |
| 订阅/计划、信用、使用情况、支付历史、计费周期、计划升级、计费门户    | `billing`, `usage`                              | 此文件                                                                                   |
| 组织和成员（创建、更新、邀请、角色、离开、删除）                           | `orgs`                                          | 此文件                                                                                   |
| 项目备份（列表、最新、创建、重命名、删除、恢复——云和自托管）            | `backups`                                       | 此文件                                                                                   |
| Advisor 扫描和抑制发现（误报、接受的风险）                           | `advisor`, `diagnose advisor`                   | 此文件                                                                                   |
| 模式、SQL、RLS、触发器、索引、导入、导出                                              | `db`                                            | `references/database/*`                                                                     |
| 认证重定向、密码策略、SMTP、存储大小、实时/计划保留、子域配置 | `config`                                        | `references/config.md`                                                                      |
| 存储桶和对象                                                                        | `storage`                                       | 此文件                                                                                   |
| 实时后端设置                                                                             | `db` 迁移                                 | `references/realtime.md`                                                                    |
| 边缘函数                                                                                     | `functions`                                     | `references/functions-deploy.md`                                                            |
| AI/OpenRouter 密钥设置和模型网关使用概述                                           | `ai setup`, `ai overview`                       | 此文件                                                                                   |
| 代理内存：项目事实、决策、偏好、跨会话的引用                                             | `memory`                                        | `references/memory.md`                                                                      |
| Stripe/Razorpay 密钥、目录同步、webhooks                                                       | `payments`                                      | `references/payments/overview.md`                                                           |
| 前端部署                                                                               | `deployments`                                   | `references/deployments/deploy.md`                                                          |
| 自定义域名、Cloudflare 注册商、DNS 同步、SSL 验证                                    | `domains`                                       | `references/deployments/domains.md`                                                         |
| 后端容器/服务                                                                        | `compute`                                       | `references/compute-deploy.md`                                                              |
| 密钥/环境变量                                                                                   | `secrets`, 部署/计算环境命令      | 此文件                                                                                   |
| 计划工作                                                                                     | `schedules`                                     | `references/schedules.md`                                                                   |
| 后端分支                                                                                   | `branch`                                        | `references/branch/overview.md`, `references/branch/merge.md`, `references/branch/reset.md` |
| 日志和健康检查                                                                             | `logs`, `diagnose`                              | `references/diagnostics.md`                                                                 |
| 内置文档查找                                                                            | `docs`                                          | 此文件                                                                                   |
| PostHog 设置                                                                                      | `posthog setup`                                 | `references/posthog.md`                                                                     |
| Apify 网页抓取器 (连接、认证桥接、抓取、着陆、计划)                                   | `webscraper apify`                              | `references/webscraper/apify.md`                                                            |
| 报告 InsForge 端的 Bug、文档差异或设计问题                                    | `feedback`                                      | 此文件                                                                                   |

## 数据库工作流

在涉及非平凡数据库工作的任务中，在编写迁移之前使用数据库参考：

- `references/database/migrations.md` - 迁移文件创建和 apply 工作流。
- `references/database/query.md` - 原始 SQL 执行和目标检查。
- `references/database/access-control.md` - RLS、授权、递归安全的辅助函数、ACL、受保护的字段和公共投影。
- `references/database/integrity.md` - 约束、触发器、派生状态、生命周期保护、仅追加历史记录和服务器维护字段。
- `references/database/vector.md` - pgvector 扩展、向量模式、距离运算符、索引和向量搜索 SQL/RPC 模式。
- `references/database/export.md` / `references/database/import.md` - 模式或数据导入/导出任务。

默认模式：

- 优先使用 `npx -y @insforge/cli db migrations new <name>` 加上迁移 SQL 文件，用于模式、授权、索引、触发器、函数和 RLS 策略更改。
- 使用 `npx -y @insforge/cli db migrations up --all` 应用迁移。
- 对于新的模式工作，当实际时，将相关的 DDL 组合到一个迁移中。
- 当现有状态未知或命令失败时，使用目标检查。
- 当迁移不适用时，使用 `npx -y @insforge/cli db query <sql>` 进行目标检查和小的纠正行/数据 SQL。
- 使用 `npx -y @insforge/cli db rpc <fn> [--data <json>]` 通过后端调用数据库函数。

公共模式范围：

- 对于通用应用程序数据库工作，在 `public` 模式下创建和修改应用拥有的对象。
- 创建、修改、删除、授权、撤销、索引、触发器、函数、视图和策略更改，适用于 `public` 应用对象。
- 不要创建自定义模式或写入 InsForge 管理的/系统模式，如 `auth`, `storage`, `realtime`, `payments`, `graphql`, `extensions`, `pg_catalog`, `information_schema`, 或 `system`，除非您正在处理该特定功能模块且其文档明确允许该操作。
- 允许从公共表或公共 RLS 策略中引用内置对象，如 `auth.users(id)` 和 `auth.uid()`；不要修改这些内置对象。
- 不要创建用户、播种业务行或运行应用程序 CRUD 工作流，除非用户请求明确要求数据迁移、修复或测试设置。

RLS 和访问控制：

- 使用 `auth.uid()` 或等效经过身份验证的标识表达式进行用户所有检查。
- 添加 SQL 权限和 RLS 策略。策略不会取代 `GRANT`。
- 运行时角色对 `public` 表具有广泛的默认 DML 权限，以便 RLS 可以决定行访问。如果一个表需要更窄的操作或列访问，请明确 `REVOKE` 广泛权限，然后再授予精确允许的操作或列。
- 在 INSERT 和 UPDATE 策略中包含 `WITH CHECK`，以便写入不会创建用户不应拥有的行。
- 当跨表 RLS 检查时，优先使用辅助函数，因为直接策略连接可能递归通过其他 RLS 策略。
- 从 RLS 策略中调用的辅助函数，这些函数查询 RLS 启用的表应该是 `SECURITY DEFINER`。
- 将 RLS 辅助函数放在 `public` 中，并使用模式限定引用，例如 `public.team_members` 和 `auth.uid()`。
- 对于 ACL、受保护的所有者/租户/角色字段、字段级更新掩码、清理的公共视图或递归敏感策略，请先阅读 `references/database/access-control.md` 再编写迁移。

完整性：

- 对于计数器、余额、最新指针、仅追加历史记录、状态转换、生命周期保护、受保护的删除、配额保护、租用或触发器维护列，请先阅读 `references/database/integrity.md` 再编写迁移。

向量：

- 对于 pgvector、向量搜索函数、分数语义、ANN 索引、混合排名、RAG 块检索、多向量搜索或嵌入版本选择，请先阅读 `references/database/vector.md` 再编写迁移。

## 项目和配置

项目命令：

- `npx -y @insforge/cli create` - 创建新项目。使用 `--json` 与必需标志一起用于非交互式代理运行。参见 `references/create.md`。
- `npx -y @insforge/cli link` - 将当前目录链接到现有项目。
- `npx -y @insforge/cli link --api-base-url <url> --api-key <admin key>` - 直接通过其 URL 和管理员 API 密钥链接自托管（OSS）后端；无需平台登录。
- `npx -y @insforge/cli current` - 显示当前链接的项目。
- `npx -y @insforge/cli metadata --json` - 当需要发现时检查后端元数据。

项目生命周期（除非 `--project <id>` 给出，否则操作针对链接的项目）：

- `npx -y @insforge/cli projects get [--project <id>]` - 显示项目的当前状态、in-flight `operation_status`、区域、实例类型和版本。使用此方法在异步操作（恢复、版本更新、实例调整大小）后轮询，直到 `operation_status` 清除。
- `npx -y @insforge/cli projects update [--name <name>] [--domain <domain>] [--storage-size <gib>] [--project <id>]` - 重命名或更改项目设置。
- `npx -y @insforge/cli projects restore [--project <id>]` - 将暂停的项目恢复在线。只有暂停的项目才能恢复。
- `npx -y @insforge/cli projects update-version [--wait] [--project <id>]` - 将后端更新到最新的 InsForge 版本（自动解析；如果已经当前则为无操作）。会导致短暂重启。添加 `--wait` 以阻塞直到完成而不是在排队时返回。
- `npx -y @insforge/cli projects upgrade-instance <type> [--project <id>]` - 更改实例类。有效：`nano`, `micro`, `small`, `medium`, `large`, `xl` (`xl` 是上限)。重启项目并更改账单。
- `npx -y @insforge/cli projects delete --project <id>` - 永久删除项目和所有资源。`--project` 是必需的（它不会默认为链接的项目）。不可逆——在确认确切的项目 ID 之前不要自动绕过确认。
- `npx -y @insforge/cli projects transfer <targetOrgId> --project <id>` - 将项目转移到另一个组织（账单和访问权限随之前移）。`--project` 是必需的（它不会默认为链接的项目）。受保护，人工参与——在确认源项目和目标组织之前。

配置：

- 使用 `npx -y @insforge/cli config export`, `config plan`, 和 `config apply` 用于支持的 `insforge.toml` 钩子。
- TOML 仅用于配置值。SQL 属于 `db migrations`；函数代码属于 `functions deploy`；前端代码属于 `deployments deploy`；计算代码/镜像属于 `compute deploy`。
- 如果 `config apply` 返回 `skipped[]`，报告跳过的项目并需要后端升级。不要重试原始 HTTP。

## 组织和成员

Org 范围命令按以下顺序解析组织：`--org-id` 标志，`INSFORGE_ORG_ID`，链接项目的组织，配置的默认组织，然后是提示（或单组织自动选择）。传递 `--org-id <id>` 以针对特定组织执行。

- `npx -y @insforge/cli orgs list` - 列出您所属的组织。
- `npx -y @insforge/cli orgs create <name> [--type personal|team|company]` - 创建组织（默认类型 `team`）。
- `npx -y @insforge/cli orgs update [--name <name>] [--type <type>] [--org-id <id>]` - 重命名或更改组织的类型。
- `npx -y @insforge/cli orgs members list [--org-id <id>]` - 列出成员和待处理的邀请。
- `npx -y @insforge/cli orgs members invite <email> [--role administrator|developer] [--org-id <id>]` - 邀请新成员（默认角色 `developer`）。
- `npx -y @insforge/cli orgs members role <memberId> <role> [--org-id <id>]` - 更改成员的角色 (`administrator` 或 `developer`)。
- `npx -y @insforge/cli orgs members remove <memberId> [--org-id <id>]` - 移除成员。首先确认意图。
- `npx -y @insforge/cli orgs leave --org-id <id>` - 离开组织。`--org-id` 是必需的（它不会默认为链接的组织）。您将失去对所有项目的访问权限，必须重新邀请才能返回。如果您是最后一个管理员，后端会拒绝——请首先转移管理员角色。受保护，人工参与——首先确认意图。
- `npx -y @insforge/cli orgs delete --org-id <id>` - 永久删除组织。`--org-id` 是必需的（它不会默认为链接的组织）。只有所有者才能执行。这将级联：组织中的每个项目（数据库、存储、所有资源）都将被永久删除，订阅也将被取消——CLI 会列出受影响的项目并在当前链接的项目是其中之一时发出警告。不可逆；在确认确切的组织 ID 之前与用户确认，不要自动绕过确认。

## 账单和使用情况

检查组织的计划/消耗并管理其订阅。Org 解析与组织部分匹配。

- `npx -y @insforge/cli billing status [--org-id <id>]` - 显示当前的订阅/计划和周期。
- `npx -y @insforge/cli billing credits [--org-id <id>]` - 显示信用余额和最近的信用交易。
- `npx -y @insforge/cli billing history [--org-id <id>]` - 列出过去的支付/发票。
- `npx -y @insforge/cli billing cycles [--org-id <id>]` - 显示当前和以前的计费周期窗口。
- `npx -y @insforge/cli usage [--org-id <id>]` - 显示当前计费周期（摘要加上每个项目的细分：数据库、存储、出口等）。
- `npx -y @insforge/cli billing upgrade <plan> [--org-id <id>]` - 启动 Stripe 结账以更改计划 (`free | starter | pro | team | enterprise`)。在浏览器中打开托管结账 URL，并在命令行中打印它。使用 `--json`，它会打印一个 JSON 对象 (`{ checkoutUrl, sessionId }`) 并不打开浏览器——用于无头/CI。直到用户完成结账才会收费；后端验证计划和管理员权限。
- `npx -y @insforge/cli billing manage [--org-id <id>]` - 打开 Stripe 客户门户以管理订阅、支付方式或取消。在浏览器中打开门户 URL 并打印它。使用 `--json`，它会打印一个 JSON 对象 (`{ portalUrl }`) 并不打开浏览器——用于无头/CI。

## 备份

除非 `--project <id>` 给出，否则操作针对链接的项目。适用于云项目和自托管项目（使用 `link --api-base-url <url> --api-key <key> 链接）——CLI 会自动路由到正确的后端；显式的 `--project <id>` 始终针对云项目。

- `npx -y @insforge/cli backups list [--project <id>]` - 列出备份。
- `npx -y @insforge/cli backups latest [--project <id>]` - 显示最新的备份。云打印最新的转储文件，带有预签名的下载 URL；自托管打印最新的备份记录（没有下载 URL）。
- `npx -y @insforge/cli backups create [--name <name>] [--wait] [--project <id>]` - 创建备份。`--name` 是可选的；如果提供，它必须是 1-64 个字符。`--wait` 阻塞直到完成而不是在排队时返回。
- `npx -y @insforge/cli backups rename <backupId> <name> [--project <id>]` - 重命名备份（传递 `""` 以清除名称）。
- `npx -y @insforge/cli backups delete <backupId> [--project <id>]` - 删除备份。首先确认意图。
- `npx -y @insforge/cli backups restore <backupId> [--project <id>]` - 从备份恢复项目。首先确认意图。云：覆盖项目的当前数据库和存储——所有自备份以来的数据都将丢失。自托管：仅数据库 `pg_restore --clean`——备份表中数据将被回滚，但备份后创建的表不会被删除，存储不受影响。

## 存储

- `npx -y @insforge/cli storage buckets` - 列出存储桶。
- `npx -y @insforge/cli storage create-bucket <name> [--private]` - 创建存储桶。
- `npx -y @insforge/cli storage delete-bucket <name>` - 删除存储桶和所有对象。首先确认破坏性意图。
- `npx -y @insforge/cli storage list-objects <bucket> [--prefix] [--search] [--limit] [--sort]` - 检查对象。
- `npx -y @insforge/cli storage upload <file> --bucket <name> [--key <objectKey>]` - 上传对象。
- `npx -y @insforge/cli storage download <objectKey> --bucket <name> [--output <path>]` - 下载对象。
- `npx -y @insforge/cli storage s3-keys list` - 列出 S3 兼容的访问密钥（密钥值永远不会显示）。
- `npx -y @insforge/cli storage s3-keys create [--description <text>]` - 创建 S3 访问密钥。密钥的密钥值在创建时显示一次——立即捕获它。
- `npx -y @insforge/cli storage s3-keys delete <id>` - 删除 S3 访问密钥。使用它的工具将停止工作。首先确认意图。

对于通过 Postgres 策略实现的存储访问控制行为，请使用特定的产品文档或功能指南。不要将存储内部视为通用公共模式数据库表，除非参考的存储文档明确说明要这样做。

## 实时

通过迁移创建通道模式、应用表发布触发器，以及通道/消息 RLS。参见 `references/realtime.md`。

## 边缘函数

- `npx -y @insforge/cli functions list` - 列出已部署的函数。
- `npx -y @insforge/cli functions code <slug>` - 查看函数源代码。
- `npx -y @insforge/cli functions deploy <slug> --file <path>` - 部署或更新。参见 `references/functions-deploy.md`。
- `npx -y @insforge/cli functions invoke <slug> [--data <json>] [--method GET|POST]` - 调用函数。
- `npx -y @insforge/cli functions delete <slug>` - 删除函数。首先确认破坏性意图。

## AI 网关

- `npx -y @insforge/cli ai setup` 检索链接项目的活动 OpenRouter 密钥，并将 `OPENROUTER_API_KEY` 写入本地服务器端环境文件。
- `npx -y @insforge/cli ai overview` 显示模型网关密钥使用情况：总支出、限制、剩余信用、每日/每周/每月支出，以及当可观察性可用时每个模型的活动。数字以美元信用为单位。使用它来回答“还有多少 AI 信用可用/正在使用”。
- 将 `OPENROUTER_API_KEY` 仅保留在服务器上。永远不要将其作为 `NEXT_PUBLIC_*`, `VITE_*`, `PUBLIC_*` 或 `REACT_APP_*` 公开。
- `npx -y @insforge/cli posthog setup` 确保仪表板有一个 PostHog 连接，然后打印官方 PostHog 工具命令，以及连接的项目的公共 `phc_` API 密钥和主机。
- ⚠️ `posthog setup` 单独不会自动为应用程序进行仪器：没有环境变量，没有 SDK，没有事件，直到工具步骤发生。工具是交互式的，可能会打开浏览器；要求用户在他们的真实终端上运行它，或者使用打印的 `phc_` 密钥/主机手动进行仪器（PostHog 的公共客户端密钥，可以安全地放在前端环境变量中）。
- 云独有：自托管后端不暴露此集成。不要将来自单独 PostHog 账户的 `phc_` 密钥放入应用环境变量——分析页面从仅填充的服务器端连接中读取；使用它打印的密钥/主机；使用 `phc_` 密钥/主机（PostHog 的公共客户端密钥）。

## Apify 网页抓取器

- `npx -y @insforge/cli webscraper apify connect` — 一次性 OAuth 连接；将可刷新的令牌存储在 InsForge 中。
- `npx -y @insforge/cli webscraper apify login` — 认证桥接：获取 InsForge 管理的令牌，运行 `apify login --token`，并安装 Apify 的官方代理技能。永远不要运行纯 `apify login`（浏览器 OAuth）。对于任何 Apify `401` / “未登录”，重新运行 `login`。
- 参见 `references/webscraper/apify.md` 以获取完整的抓取→着陆→计划工作流程和基于大小的着陆策略。

## 非交互式 CI/CD

对于自动化环境，使用环境变量和 JSON 模式：

```bash
INSFORGE_EMAIL=$EMAIL INSFORGE_PASSWORD=$PASSWORD npx -y @insforge/cli login --email -y
npx -y @insforge/cli link --project-id $PROJECT_ID --org-id $ORG_ID -y
npx -y @insforge/cli db query "SELECT 1 AS ok" --json
```

## 项目配置文件

在 `create` 或 `link` 之后，`.insforge/project.json` 包含链接的项目 ID、应用密钥、区域、API 密钥和后端 URL。

- 永远不要提交 `.insforge/project.json` 或公开分享它。
- 不要手动编辑它。使用 `npx -y @insforge/cli link` 或分支命令切换项目。
