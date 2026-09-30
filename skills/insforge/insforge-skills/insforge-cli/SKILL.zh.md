---
name: insforge-cli
description: 每次需要后端服务，或者任务通过 InsForge CLI 涉及 InsForge 后端或云基础设施时，请使用此技能：项目、SQL、迁移、RLS 策略、函数、存储、备份、部署、计算、密钥、配置、计划、日志、诊断、顾问扫描和抑制、导入/导出、AI/OpenRouter 设置和使用概述、Stripe/Razorpay 支付、Apify 网络爬虫/数据源、PostHog 产品分析、后端分支、组织成员资格（邀请、退出、删除）、代理内存（记忆/回忆项目事实和决策）、报告 InsForge 端的 Bug 或文档差异（反馈），或 CLI 文档。对于使用 InsForge 或 @insforge/sdk 的应用代码，请改用 insforge app-integration 技能。
---

# InsForge CLI

当需要后端时，或者使用 InsForge CLI 管理InsForge后端和云基础设施时，请使用此技能。对于从前端、后端或边缘函数调用InsForge的应用代码，请使用 `insforge` 应用集成技能。

## 核心规则

- 始终通过 `npx -y @insforge/cli <command>` 运行CLI。保留 npx 的 `-y`：没有它，npx 在安装包之前会询问“是否继续？”并在附加到TTY的代理 shell 中永久阻塞。不要安装或调用全局 `insforge` 二进制文件。
- 如果项目已经链接，请使用当前链接的项目。仅在连接设置实际需要时运行登录、项目创建、链接、项目发现、组织列表或云项目命令。
- 当任务需要后端且尚未链接任何项目时，请首先进行连接设置——在编写任何应用代码之前：(1) 登录（使用 `whoami` 检查；在沙盒中使用以下两步设备登录），(2) `create` 一个新项目或 `link` 一个现有项目，(3) 然后从CLI使用来自真实项目 URL 和密钥进行构建。永远不要使用占位符凭证（如 `your-project.region.insforge.app`）进行脚手架——首先获取真实值。
- 将 InsForge API 密钥视为完全访问权限的管理员密钥。将它们保留在服务器上，不要在前端/公共环境变量中。
- 优先使用 CLI 命令和文档化的项目配置，而不是原始后端 HTTP 调用。如果 `config apply` 报告不支持的/跳过的字段，请显示该结果，而不是使用直接 API 调用绕过 CLI。
- 当需要结构化输出或非交互式值收集时，使用 `--json`。当用户已批准操作时，使用 `--yes` 进行确认提示。
- 在链接项目的非平凡任务开始时，运行 `npx -y @insforge/cli memory list`（廉价，无 AI 调用）并回忆与任务相关的任何标题，然后再进行设计或调试。在发生时使用 `memory remember` 记录决策和遇到的陷阱。参见 `references/memory.md`。
- 当遇到 InsForge 的故障——应该工作但无法工作的情况、需要但不受支持的功能、与现实相矛盾说明（文档/技能）或无谓的摩擦时——使用 `npx -y @insforge/cli feedback`（参见反馈），然后继续用户的任务并使用替代方案。永远不要为用户自己的应用代码中的问题提交反馈。

## 全局选项

| 标志          | 使用                                                                                                                                                                                                           |
| ------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `--json`      | 结构化 JSON 输出并跳过值收集提示，如文本/选择提示。如果任何必需值缺失，则报错。与 `-y` 结合用于破坏性命令，这些命令也会要求 Y/N 确认。                                                                         |
| `-y`, `--yes` | 自动接受 Y/N 确认提示，如删除或覆盖提示。不会跳过值收集提示；使用 `--json` 即可。与 npx 的 `-y` 分开，因此两者一起出现：`npx -y @insforge/cli link --project-id <id> -y`。 |

## 退出代码

| 代码 | 含义                                                 |
| ---- | ------------------------------------------------------- |
| 0    | 成功                                                 |
| 1    | 一般错误，包括来自函数调用的 HTTP 400+                 |
| 2    | 未认证                                               |
| 3    | 项目未链接                                          |
| 4    | 资源未找到                                          |
| 5    | 权限被拒绝                                          |

## 环境变量

| 变量                | 使用                                |
| ----------------------- | ---------------------------------- |
| `INSFORGE_ACCESS_TOKEN` | 覆盖存储的访问令牌       |
| `INSFORGE_PROJECT_ID`   | 覆盖链接的项目 ID         |
| `INSFORGE_EMAIL`        | 非交互式登录的邮箱    |
| `INSFORGE_PASSWORD`     | 非交互式登录的密码     |

## 连接设置

如果任务需要项目访问权限且连接状态未知，从 `npx -y @insforge/cli current` 开始。当认证身份很重要或 `current` 报告 CLI 未认证时，使用 `npx -y @insforge/cli whoami`。

如果未认证，运行 `npx -y @insforge/cli login`（打开浏览器）。对于无头/代理/CI 环境且没有浏览器的情况，使用用户 API 密钥进行非交互式认证：`npx -y @insforge/cli login --user-api-key "$INSFORGE_USER_API_KEY"`（用户在控制台下的 Profile → API Keys 中创建该密钥）。在沙盒中，用户有浏览器但无法到达 CLI 的本地回调（例如 ChatGPT 应用），使用设备登录作为两步：`timeout 15 npx -y @insforge/cli login --device --json 2>&1 || true` 来捕获验证链接 + 代码，将它们传递给用户，然后重新运行 `npx -y @insforge/cli login --device --json` 以继续相同的代码并在他们点击授权后完成——参见 `references/login.md`。如果沙盒报告 `api.insforge.dev` 不是允许的网络域，请要求用户将其添加到工作区的允许网络域中，然后重试。如果未链接项目，使用 `npx -y @insforge/cli link` 用于现有项目或 `npx -y @insforge/cli create` 当用户要求新的后端时。在已经预链接或预配置的工作流中，如 CI、本地测试项目、自动化或明确提供的用户项目上下文，直接使用该项目上下文。云项目是默认的；只有在用户明确要求在他们的机器上以 Docker 运行的后端时，参见 `references/local.md`——永远不要作为登录或 `create` 不方便时的备用方案。

## 命令路由

| 需要                                                                                               | CLI 区域                                        | 参考                                                                                   |
| -------------------------------------------------------------------------------------------------- | ----------------------------------------------- | ------------------------------------------------------------------------------------------- |
| 登录、登出、当前用户                                                                        | `login`, `logout`, `whoami`                     | `references/login.md`                                                                       |
| 创建/链接/列表/当前项目                                                                   | `create`, `link`, `list`, `current`, `metadata` | `references/create.md`                                                                      |
| 用户自己的机器上的 Docker 后端——仅在它们明确要求时     | `local`                                         | `references/local.md`                                                                       |
| 项目生命周期：状态、重命名、删除、恢复、版本更新、实例调整大小、转移       | `projects`                                      | 此文件                                                                                   |
| 订阅/计划、信用额度、使用情况、支付历史、计费周期、计划升级、计费门户    | `billing`, `usage`                              | 此文件                                                                                   |
| 组织和成员（创建、更新、邀请、角色、离开、删除）                           | `orgs`                                          | 此文件                                                                                   |
| 项目备份（列表、最新、创建、重命名、删除、恢复 — 云和自托管）            | `backups`                                       | 此文件                                                                                   |
| Advisor 扫描和抑制发现（误报、接受的风险）                           | `advisor`, `diagnose advisor`                   | 此文件                                                                                   |
| 模式、SQL、RLS、触发器、索引、导入、导出                                              | `db`                                            | `references/database/*`                                                                     |
| 认证重定向、密码策略、SMTP、存储大小、实时/计划保留、子域配置 | `config`                                        | `references/config.md`                                                                      |
| 存储桶和对象                                                                        | `storage`                                       | 此文件                                                                                   |
| 实时后端设置                                                                             | `db` 迁移                                 | `references/realtime.md`                                                                    |
| 边缘函数                                                                                     | `functions`                                     | `references/functions-deploy.md`                                                            |
| AI/OpenRouter 密钥设置和模型网关使用概述                                           | `ai setup`, `ai overview`                       | 此文件                                                                                   |
| Agent 内存：项目事实、决策、偏好、跨会话的引用                    | `memory`                                        | `references/memory.md`                                                                      |
| Stripe/Razorpay 密钥、目录同步、Webhooks                                                       | `payments`                                      | `references/payments/overview.md`                                                           |
| 前端部署                                                                               | `deployments`                                   | `references/deployments/deploy.md`                                                          |
| 自定义域名、Cloudflare 注册商、DNS 同步、SSL 验证                                    | `domains`                                       | `references/deployments/domains.md`                                                         |
| 后端容器/服务                                                                        | `compute`                                       | `references/compute-deploy.md`                                                              |
| 密码/环境变量                                                                                   | `secrets`, 部署/计算环境命令      | 此文件                                                                                   |
| 定时任务                                                                                     | `schedules`                                     | `references/schedules.md`                                                                   |
| 后端分支                                                                                   | `branch`                                        | `references/branch/overview.md`, `references/branch/merge.md`, `references/branch/reset.md` |
| 日志和健康检查                                                                             | `logs`, `diagnose`                              | `references/diagnostics.md`                                                                 |
| 内置文档查找                                                                      | `docs`                                          | 此文件                                                                                   |
| PostHog 设置                                                                                      | `posthog setup`                                 | `references/posthog.md`                                                                     |
| Apify 网页抓取器（连接、认证桥接、抓取、着陆、计划）                                   | `webscraper apify`                              | `references/webscraper/apify.md`                                                            |
| 报告 InsForge 端的 Bug、文档差异或设计问题                                    | `feedback`                                      | 此文件                                                                                   |

## 数据库工作流

在编写迁移之前使用数据库参考，当任务涉及非平凡数据库工作时：

- `references/database/migrations.md` - 迁移文件创建和 apply 工作流。
- `references/database/query.md` - 原始 SQL 执行和目标检查。
- `references/database/access-control.md` - RLS、授权、递归安全辅助函数、ACL、受保护字段和公共投影。
- `references/database/integrity.md` - 约束、触发器、派生状态、生命周期保护、仅追加历史记录和服务器维护字段。
- `references/database/vector.md` - pgvector 扩展、向量模式、距离运算符、索引和向量搜索 SQL/RPC 模式。
- `references/database/export.md` / `references/database/import.md` - 模式或数据导入/导出任务。

默认模式：

- 优先使用 `npx -y @insforge/cli db migrations new <name>` 加上一个迁移 SQL 文件，用于模式、授权、索引、触发器、函数和 RLS 策略更改。
- 使用 `npx -y @insforge/cli db migrations up --all` 应用迁移。
- 对于新模式工作，在实用时将相关的 DDL 组合到一个迁移中。
- 当现有状态未知或命令失败时，使用目标检查。
- 仅当迁移不适用时，使用 `npx -y @insforge/cli db query <sql>` 进行目标检查和小的纠正行/数据 SQL。
- 使用 `npx -y @insforge/cli db rpc <fn> [--data <json>]` 通过后端调用数据库函数。

公共模式范围：

- 对于通用应用数据库工作，在 `public` 模式中创建和修改应用拥有的对象。
- 对 `public` 应用对象进行创建、修改、删除、授权、撤销、索引、触发器、函数、视图和策略更改。
- 不要创建自定义模式或写入 InsForge 管理的系统模式，如 `auth`、`storage`、`realtime`、`payments`、`graphql`、`extensions`、`pg_catalog`、`information_schema` 或 `system`，除非您正在处理该特定功能模块并且其文档明确允许该操作。
- 允许从公共表或公共 RLS 策略中引用内置对象，如 `auth.users(id)` 和 `auth.uid()`；不要修改这些内置对象。
- 不要创建用户、播种业务行或运行应用 CRUD 工作流，除非用户请求明确要求数据迁移、修复或测试设置。

RLS 和访问控制：

- 使用 `auth.uid()` 或等效的经过身份验证的身份表达式进行用户所有权检查。
- 添加 SQL 权限和 RLS 策略。策略不会取代 `GRANT`。
- 运行时角色对 `public` 表具有广泛的默认 DML 权限，以便 RLS 可以决定行访问。如果一个表需要更窄的操作或列访问，请在授予权确切的允许的操作或列之前明确 `REVOKE` 广泛的权限。
- 在 INSERT 和 UPDATE 策略中包含 `WITH CHECK`，以便写入不会创建用户不应拥有的行。
- 当直接策略连接可能递归通过其他 RLS 策略时，优先使用辅助函数进行跨表 RLS 检查。
- 从 RLS 策略中调用的辅助函数，如果查询 RLS 启用的表，则应该是 `SECURITY DEFINER`。
- 将 RLS 辅助函数放在 `public` 中，并对引用进行模式限定，例如 `public.team_members` 和 `auth.uid()`。
- 对于 ACL、受保护的拥有者/租户/角色字段、字段级更新掩码、清理后的公共视图或递归敏感策略，在编写迁移之前，请阅读 `references/database/access-control.md`。

完整性：

- 对于计数器、余额、最新指针、仅追加的历史记录、状态转换、生命周期保护、受保护的删除、配额保护、租赁或触发维护的列，在编写迁移之前，请阅读 `references/database/integrity.md`。

向量：

- 对于 pgvector、向量搜索函数、分数语义、ANN 索引、混合排名、RAG 片段检索、多向量搜索或嵌入版本选择，在编写迁移之前，请阅读 `references/database/vector.md`。

## 项目和配置

项目命令：

- `npx -y @insforge/cli create` - 创建一个新项目。在非交互式代理运行时使用必需标志与 `--json` 一起使用。参见 `references/create.md`。
- `npx -y @insforge/cli link` - 将当前目录链接到现有项目。
- `npx -y @insforge/cli link --api-base-url <url> --api-key <admin key>` - 通过其 URL 和管理员 API 密钥直接链接到自托管（OSS）后端；无需平台登录。
- `npx -y @insforge/cli current` - 显示当前链接的项目。
- `npx -y @insforge/cli metadata --json` - 在需要发现时检查后端元数据。

项目生命周期（除非给出 `--project <id>`，否则在链接的项目上操作）：

- `npx -y @insforge/cli projects get [--project <id>]` - 显示项目的当前状态、进行中的 `operation_status`、区域、实例类型和版本。使用此方法在异步操作（恢复、版本更新、实例调整大小）后轮询，直到 `operation_status` 清除。
- `npx -y @insforge/cli projects update [--name <name>] [--domain <domain>] [--storage-size <gib>] [--project <id>]` - 重命名或更改项目设置。
- `npx -y @insforge/cli projects restore [--project <id>]` - 将暂停的项目恢复在线。只有暂停的项目才能被恢复。
- `npx -y @insforge/cli projects update-version [--wait] [--project <id>]` - 将后端更新到最新的 InsForge 版本（自动解析；如果已经是当前版本则为无操作）。会导致短暂重启。添加 `--wait` 以阻塞，直到完成，而不是在排队时返回。
- `npx -y @insforge/cli projects upgrade-instance <type> [--project <id>]` - 更改实例类。有效：`nano`、`micro`、`small`、`medium`、`large`、`xl`（`xl` 是上限）。重启项目并更改账单。
- `npx -y @insforge/cli projects delete --project <id>` - 永久删除项目及其所有资源。`--project` 是必需的（它不会默认为链接的项目）。不可逆——首先与用户确认确切的项目 ID；这是一个受保护的、人工参与的操作，因此不要自动绕过确认。
- `npx -y @insforge/cli projects transfer <targetOrgId> --project <id>` - 将项目移动到另一个组织（账单和访问权限随其一起移动）。`--project` 是必需的（它不会默认为链接的项目）。受保护、人工参与——首先确认源项目和目标组织。

配置：

- 使用 `npx -y @insforge/cli config export`、`config plan` 和 `config apply` 来配置支持的 `insforge.toml` 杠杆。
- TOML 仅用于配置值。SQL 属于 `db migrations`；函数代码属于 `functions deploy`；前端代码属于 `deployments deploy`；计算代码/图像属于 `compute deploy`。
- 如果 `config apply` 返回 `skipped[]`，请报告跳过项和必需的后端升级。不要用原始 HTTP 重试。

## 组织和成员

组织范围的命令按以下顺序解析组织：`--org-id` 标志、`INSFORGE_ORG_ID`、链接项目的组织、配置的默认组织，然后是提示（或单组织自动选择）。传递 `--org-id <id>` 以对特定组织执行操作。

- `npx -y @insforge/cli orgs list` - 列出您所属的组织。
- `npx -y @insforge/cli orgs create <name> [--type personal|team|company]` - 创建一个组织（默认类型 `team`）。
- `npx -y @insforge/cli orgs update [--name <name>] [--type <type>] [--org-id <id>]` - 重命名或更改组织的类型。
- `npx -y @insforge/cli orgs members list [--org-id <id>]` - 列出成员和待处理的邀请。
- `npx -y @insforge/cli orgs members invite <email> [--role administrator|developer] [--org-id <id>]` - 邀请新成员（默认角色 `developer`）。
- `npx -y @insforge/cli orgs members role <memberId> <role> [--org-id <id>]` - 更改成员的角色 (`administrator` 或 `developer`)。
- `npx -y @insforge/cli orgs members remove <memberId> [--org-id <id>]` - 移除成员。首先确认意图。
- `npx -y @insforge/cli orgs leave --org-id <id>` - 离开组织。`--org-id` 是必需的（它不会默认为链接的组织）。您将失去对所有项目的访问权限，必须重新邀请才能返回。如果您是最后一个管理员，后端将拒绝——首先转移管理员角色。受保护、人工参与——首先确认意图。
- `npx -y @insforge/cli orgs delete --org-id <id>` - 永久删除组织。`--org-id` 是必需的（它不会默认为链接的组织）。仅限所有者。这将级联：组织中的每个项目（数据库、存储、所有资源）都将被永久删除，订阅也将被取消——CLI 会列出受影响的项目并在当前链接的项目是其中之一时发出警告。不可逆；首先与用户确认确切的 org ID，然后不要自动绕过确认。

## 账单和使用情况

检查组织的计划/消耗并管理其订阅。组织解析与组织部分匹配。

- `npx -y @insforge/cli billing status [--org-id <id>]` - 显示当前的订阅/计划和周期。
- `npx -y @insforge/cli billing credits [--org-id <id>]` - 显示信用余额和最近的信用交易。
- `npx -y @insforge/cli billing history [--org-id <id>]` - 列出过去的付款/发票。
- `npx -y @insforge/cli billing cycles [--org-id <id>]` - 显示当前和以前的账单周期窗口。
- `npx -y @insforge/cli usage [--org-id <id>]` - 显示当前账单周期的消耗（摘要加上每个项目的细分：数据库、存储、出口等）。
- `npx -y @insforge/cli billing upgrade <plan> [--org-id <id>]` - 开始 Stripe 结账以更改计划（`free | starter | pro | team | enterprise`）。在浏览器中打开托管结账 URL，并将其打印出来。使用 `--json` 它将打印一个 JSON 对象（`{ checkoutUrl, sessionId }`）并且不会打开浏览器——用于无头/CI。直到用户完成结账才会发生收费；后端将验证计划和管理员权限。
- `npx -y @insforge/cli billing manage [--org-id <id>]` - 打开 Stripe 客户门户以管理订阅、付款方式或取消。在浏览器中打开门户 URL 并将其打印出来。使用 `--json` 它将打印一个 JSON 对象（`{ portalUrl }`）并且不会打开浏览器——用于无头/CI。

## 备份

除非给出 `--project <id>`，否则在链接的项目上操作。适用于云项目和自托管项目（使用 `link --api-base-url <url> --api-key <key>` 链接）——CLI 会自动路由到正确的后端；显式的 `--project <id>` 始终针对云项目。

- `npx -y @insforge/cli backups list [--project <id>]` - 列出备份。
- `npx -y @insforge/cli backups latest [--project <id>]` - 显示最新的备份。云打印最新的转储文件，并提供预签名下载 URL；自托管打印最新的备份记录（无下载 URL）。
- `npx -y @insforge/cli backups create [--name <name>] [--wait] [--project <id>]` - 创建备份。`--name` 是可选的；提供时它必须是 1–64 个字符。`--wait` 会阻塞，直到完成，而不是在排队时返回。
- `npx -y @insforge/cli backups rename <backupId> <name> [--project <id>]` - 重命名备份（传递 `""` 以清除名称）。
- `npx -y @insforge/cli backups delete <backupId> [--project <id>]` - 删除备份。首先确认意图。
- `npx -y @insforge/cli backups restore <backupId> [--project <id>]` - 从备份恢复项目。首先确认意图。云：覆盖项目的当前数据库和存储——自备份以来写入的所有数据都将丢失。自托管：数据库仅 `pg_restore --clean`——备份表中数据将被回滚，但备份后创建的表不会被删除，存储不受影响。

## 存储

- `npx -y @insforge/cli storage buckets` - 列出存储桶。
- `npx -y @insforge/cli storage create-bucket <name> [--private]` - 创建存储桶。
- `npx -y @insforge/cli storage delete-bucket <name>` - 删除存储桶和所有对象。首先确认破坏性意图。
- `npx -y @insforge/cli storage list-objects <bucket> [--prefix] [--search] [--limit] [--sort]` - 检查对象。
- `npx -y @insforge/cli storage upload <file> --bucket <name> [--key <objectKey>]` - 上传对象。
- `npx -y @insforge/cli storage download <objectKey> --bucket <name> [--output <path>]` - 下载对象。
- `npx -y @insforge/cli storage s3-keys list` - 列出 S3 兼容的访问密钥（密钥值永远不会显示）。
- `npx -y @insforge/cli storage s3-keys create [--description <text>]` - 创建 S3 访问密钥。密钥访问密钥在创建时仅显示一次——立即捕获它。
- `npx -y @insforge/cli storage s3-keys delete <id>` - 删除 S3 访问密钥。使用它的工具将停止工作。首先确认意图。

对于通过 Postgres 策略实现的存储访问控制行为，请使用存储特定产品文档或功能指南。除非引用的存储文档明确说明，否则不要将存储内部视为通用公共模式数据库表。

## 实时

通过迁移创建通道模式、应用表发布触发器和通道/消息 RLS。参见 `references/realtime.md`。

## 边缘函数

- `npx -y @insforge/cli functions list` - 列出部署的函数。
- `npx -y @insforge/cli functions code <slug>` - 查看函数源代码。
- `npx -y @insforge/cli functions deploy <slug> --file <path>` - 部署或更新。参见 `references/functions-deploy.md`。
- `npx -y @insforge/cli functions invoke <slug> [--data <json>] [--method GET|POST]` - 调用函数。
- `npx -y @insforge/cli functions delete <slug>` - 删除函数。首先确认破坏性意图。

## AI 网关

- `npx -y @insforge/cli ai setup` 获取链接项目的活动 OpenRouter 密钥并将 `OPENROUTER_API_KEY` 写入本地服务器端环境文件。
- `npx -y @insforge/cli ai overview` 显示模型网关密钥使用情况：总支出、限制、剩余信用、每日/每周/每月支出以及按模型的活动（当可观察性可用时）。金额以美元信用为单位。使用它来回答“还剩多少 AI 信用/正在使用多少”。
- 保持 `OPENROUTER_API_KEY` 仅服务器使用。永远不要将其作为 `NEXT_PUBLIC_*`、`VITE_*`、`PUBLIC_*` 或 `REACT_APP_*` 公开。

## 内存

每个项目都有内置的代理内存：持久的事实、决策、偏好和引用，它们在会话之间存活。将其视为本能，而不是事后思考。

- `npx -y @insforge/cli memory list` - 便宜的标题索引（不调用 AI）。在非平凡任务的开始时运行；回忆与任务相关的任何标题。
- `npx -y @insforge/cli memory recall "<query>" [--scope] [--limit] [--threshold]` - 语义+关键词召回。
- `npx -y @insforge/cli memory remember "<content>" [--kind] [--title] [--scope] [--source]` - 存储一个原子内存。在发生决策和注意事项时记录，而不是在会话结束时记录。`--kind` 仅接受 `fact`、`decision`、`preference` 或 `reference` - 将注意事项存储为 `fact`（或存储选择时为 `decision`）。
- `npx -y @insforge/cli memory remember --file <path>` - 从摘要或笔记文件中提取持久的记忆。

存储是幂等的：重新记住已知事实是无操作的，而矛盾的事实会更新现有内存而不是重复它——当真相改变时，只需 `remember` 新真相。有关要存储的内容、类型和示例，请参阅 `references/memory.md`。

## 付款

使用 `payments` 进行 Stripe/Razorpay 后端设置和目录同步。参见 `references/payments/overview.md`。

- 付款是提供程序特定的：明确使用 `payments stripe ...` 或 `payments razorpay ...`。
- 使用 `payments <provider> config set` 配置提供程序密钥；设置密钥会自动同步提供程序状态，当密钥或账户更改时。
- 使用 `payments <provider> status` 检查密钥/账户/同步/webhook 健康状况。
- 运行 `payments <provider> sync` 以手动刷新或重试镜像提供程序数据。
- Stripe 使用产品/价格并支持托管 webhook 注册；Razorpay 使用项目/计划/订单并需要在 Razorpay 仪表板中手动设置 webhook。
- 构建时优先使用测试模式。用户明确批准后仅使用实时模式。
- 如果后端报告付款不可用，请要求用户/管理员启用或升级付款。不要通过将提供程序密钥作为通用密钥或将付款密钥密钥嵌入应用代码来绕过它。
- 在提供程序特定设置之前加载 `references/payments/stripe.md` 或 `references/payments/razorpay.md`。

运行时结账、订阅、客户门户流程和应用代码属于 `insforge` 应用集成技能。

## 部署

前端部署：

- 当应用有构建步骤时，先在本地构建。
- 在部署之前确保前端运行时环境变量配置了正确的框架前缀。
- 使用 `npx -y @insforge/cli deployments deploy <dir>` 前端源目录。除非部署引用明确要求，否则不要部署生成的输出目录。
- 参见 `references/deployments/deploy.md`。

自定义域名：

- 使用 `npx -y @insforge/cli domains ...` 进行自定义域名、Cloudflare 注册商、DNS 同步和 SSL 验证。
- 参见 `references/deployments/domains.md`。

后端计算服务：

- 使用 `npx -y @insforge/cli compute ...`；不要使用用户的 `flyctl` 账户直接管理 InsForge 计算服务。
- 使用带有 Dockerfile 的目录的源模式，或使用 `--image <url>` 的图像模式进行预构建图像。
- 使用 `--env-file` 或重复的环境设置/更新命令来代替大型内联 JSON 存储密钥。
- 参见 `references/compute-deploy.md`。

## 密钥

- `npx -y @insforge/cli secrets list [--all]` - 列出密钥而不显示值。
- `npx -y @insforge/cli secrets get <key>` - 仅在必要时检索密钥值。
- `npx -y @insforge/cli secrets add <key> <value> [--reserved] [--expires <ISO date>]` - 创建密钥。
- `npx -y @insforge/cli secrets update <key> [--value] [--active] [--reserved] [--expires]` - 更新密钥。
- `npx -y @insforge/cli secrets delete <key>` - 软删除密钥。首先确认意图。
- `npx -y @insforge/cli secrets rotate <api-key|anon-key> [--grace-hours <n>]` - 旋转项目 API 密钥或匿名密钥。新密钥仅显示一次——捕获它。旧密钥在宽限期期间仍然有效（如果省略 `--grace-hours` 则为服务器默认值）；在它过期之前更新所有消费者。

## 计划

- `npx -y @insforge/cli schedules list/get/create/update/delete/logs`.
- 使用标准的5字段cron表达式用于墙时钟计划。
- 使用pg_cron间隔语法，例如`30秒`用于亚分钟频率。不支持带秒的六字段cron。
- 标头可以引用InsForge密钥，使用`${{secrets.KEY_NAME}}`。
- 参考`references/schedules.md`了解cron格式、密钥标头引用、示例、常见错误和推荐设置工作流。

## 分支

使用后端分支在将风险模式、RLS、认证或函数更改应用到生产环境之前进行测试。参见`references/branch/overview.md`。

常用命令：

- `npx -y @insforge/cli branch create <name> [--mode full|schema-only] [--no-switch]`
- `npx -y @insforge/cli branch list`
- `npx -y @insforge/cli branch switch <name>` 或 `--parent`
- `npx -y @insforge/cli branch merge <name> [--dry-run] [--save-sql <path>]`
- `npx -y @insforge/cli branch reset <name>`
- `npx -y @insforge/cli branch delete <name>`

分支需要支持它的后端版本。如果不可用，请报告后端版本限制，而不是编造解决方案。

## 诊断和日志

- `npx -y @insforge/cli diagnose` - 完整的健康报告。
- `npx -y @insforge/cli diagnose --ai "<问题描述>"` - 请求InsForge调试代理诊断具体的后端问题。
- `npx -y @insforge/cli diagnose metrics [--range 1h|6h|24h|7d]` - EC2指标。
- `npx -y @insforge/cli diagnose advisor [--severity critical|warning|info] [--category security|performance|health]` - 顾问问题。规则列是`advisor suppress`使用的id。
- `npx -y @insforge/cli diagnose db [--check <checks>]` - 数据库健康检查。
- `npx -y @insforge/cli diagnose logs [--source <name>] [--limit <n>]` - 汇总错误日志。
- `npx -y @insforge/cli logs <source> [--limit <n>]` - 特定源的后端日志。

典型日志源包括`function.logs`、`function-deploy.logs`、`postgres.logs`、`postgrest.logs`和`insforge.logs`。参考`references/diagnostics.md`了解常见的调试场景和源选择。

## 顾问

后端顾问扫描项目以查找安全、性能和健康问题。使用`diagnose advisor`读取结果；使用`advisor`管理扫描和误报：

- `npx -y @insforge/cli advisor scan` - 立即触发扫描，而不是等待计划。用于在修复问题后立即重新检查。扫描异步运行（通常在1分钟内完成）— 循环`diagnose advisor --json`，直到`scan.status`为`completed`且`scan.scanId`等于`advisor scan`返回的id，然后读取结果。
- `npx -y @insforge/cli advisor suppressions` - 列出被抑制的发现。
- `npx -y @insforge/cli advisor suppress <ruleId> [--object <affectedObject>] --reason <reason> [--note <note>]` - 以记录的原因放弃一个发现。使用`--object`（发现的受影响对象，原文）仅抑制该实例；不使用它则抑制整个规则。`--reason`是`false_positive | accepted_risk | wont_fix | other`之一；`--note`对于`other`是必需的。抑制从下一个扫描生效（运行`advisor scan`以查看其应用）。仅抑制用户判断的问题 — 不要抑制以使报告看起来干净。
- `npx -y @insforge/cli advisor unsuppress <suppressionId>` - 移除抑制，以便发现在下一次扫描时重新出现。

## 反馈

当InsForge工具包的任何部分行为异常 — 后端平台、SDK、CLI、代理技能或文档 — 请向InsForge团队报告，然后继续使用解决方案继续任务。仅报告InsForge侧问题，绝不要报告用户自己的应用代码中的问题。

```bash
npx -y @insforge/cli feedback --json \
  --type bug \
  --component backend \
  --title "db policies create returns 500 on uppercase table names" \
  --detail "在表\"Users\"上创建RLS策略返回500；小写名称可以工作。重现：创建带引号的 uppercase 名称的表，然后运行policies create。" \
  --area db \
  --command "insforge db policies create --table Users ..." \
  --error "<verbatim error output>" \
  --severity major
```

必需标志：

- `--type`：你遇到的障碍类型。根据你的情况映射：
  - "这不是工作的"（根据文档/合同应该工作）→ `bug`
  - "我被指示做X，但现实需要替代方案" → 也是`bug`，带有`--doc`（指示在哪里）、`--expected`（它声称的）和`--workaround`（实际工作替代方案） — 你无法知道指示是否过时或产品是否回退，而这三个字段让团队可以区分
  - "我想做的事情不受支持" → `feature-request`
  - "它工作，但它令人困惑或不方便"（无用的错误，被迫绕道）→ `friction`
  - 任何其他情况 → `other`
- `--component`：工具包中的位置 — `backend`（平台/托管服务）| `sdk` | `cli` | `skills`（代理技能内容）| `docs` | `other`。
- `--title` 和 `--detail`（或 `--file <path>`）。

可选标志：

- `--language`：**当`--component sdk`时必需** — 哪个SDK，例如`js`、`python`、`flutter`、`swift`、`kotlin`、`rest-api`或`multiple`如果跨越SDK。在与`--component docs`一起使用时也很有用，用于语言特定的文档页面。对于其他组件省略。
- `--area`：产品区域 — `db` | `auth` | `storage` | `functions` | `deployments` | `billing` | `ai` | `realtime` | `payments`。与`--component`正交：Python SDK中的存储上传故障是`--component sdk --language python --area storage`。
- `--workaround`：你用来绕过障碍的替代方案 — 如果你找到了一个，请始终包含它；它告诉团队问题阻塞的程度，并且通常成为文档修复。
- `--command`（导致问题的CLI/SDK调用）、`--error`（原文输出；自动截断和截断）、`--expected`（文档/技能指示或你期望的）和`--doc "<页面或技能部分>"`用于差异，`--severity blocker|major|minor`（默认`minor`）。

保持`--detail`简洁且InsForge相关：发生了什么，你期望什么，最小的重现。不要粘贴用户应用数据 — CLI本地截断常见模式（电子邮件、已知凭证/密钥格式、密钥分配、公共IPv4地址、主目录用户名）并截断长字段，但截断是基于模式的：一个安全网，不是许可证。无需登录 — 未登录和OSS设置中均可工作；当云项目链接时，项目/组织上下文会自动附加。成功时返回反馈id（重复报告会合并到现有报告中并返回其id）。

## 文档

- `npx -y @insforge/cli docs` - 列出文档主题。
- `npx -y @insforge/cli docs instructions` - 设置指南。
- `npx -y @insforge/cli docs <feature> <language>` - `db`、`storage`、`functions`、`auth`、`ai`或`realtime`在`typescript`、`swift`、`kotlin`或`rest-api`中的功能文档。

对于使用InsForge或`@insforge/sdk`的应用代码，使用`insforge`应用集成技能，并仅将`docs`用作官方功能参考。

## PostHog

- `npx -y @insforge/cli posthog setup` 确保仪表板有PostHog连接，然后打印官方PostHog向导命令以及连接的项目公共`phc_` API密钥和主机。
- ⚠️ 单独的`posthog setup`**不会**instrument应用：没有环境变量，没有SDK，没有事件，直到向导步骤发生。向导是交互式的，可能会打开浏览器；要求用户在他们的真实终端中运行它，或使用打印的`phc_`密钥/主机（PostHog的公共客户端密钥，安全地存储在前端环境变量中）手动instrument。
- 云独有：自托管后端不暴露集成。不要将来自单独PostHog帐户的`phc_`密钥替换到应用环境变量中 — 分析页面从仅`posthog setup`填充的服务端连接读取；使用它打印的密钥。

## Apify网络爬虫

- `npx -y @insforge/cli webscraper apify connect` — 一次性OAuth连接；在InsForge中存储可刷新的令牌。
- `npx -y @insforge/cli webscraper apify login` — 认证桥接：获取InsForge管理的令牌，运行`apify login --token`，并安装Apify的官方代理技能。**永远不要**运行纯`apify login`（浏览器OAuth）。对任何Apify `401` / "未登录"，重新运行`login`。
- 参考`references/webscraper/apify.md`了解完整的抓取→着陆→计划工作流和基于大小的着陆策略。

## 非交互式CI/CD

使用环境变量和JSON模式用于自动化环境：

```bash
INSFORGE_EMAIL=$EMAIL INSFORGE_PASSWORD=$PASSWORD npx -y @insforge/cli login --email -y
npx -y @insforge/cli link --project-id $PROJECT_ID --org-id $ORG_ID -y
npx -y @insforge/cli db query "SELECT 1 AS ok" --json
```

## 项目配置文件

在`create`或`link`之后，`.insforge/project.json`包含链接的项目ID、应用密钥、区域、API密钥和后端URL。

- 永远不要提交`.insforge/project.json`或公开分享。
- 不要手动编辑它。使用`npx -y @insforge/cli link`或分支命令切换项目。
