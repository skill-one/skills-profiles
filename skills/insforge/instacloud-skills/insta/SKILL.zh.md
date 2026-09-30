---
name: insta
description: 使用 `insta` 命令行界面 (CLI) 操作 InstaCloud 基础设施：创建项目、添加 PostgreSQL/存储/计算服务、部署应用程序、创建可一次性使用的分支环境（每个分支拥有独立的数据库+存储+计算环境）、对服务或外部 URL 调度定期 HTTP 调用（cron 任务）、将服务凭证绑定到计算环境、将用户密钥连接到 `.env` 文件、在每个分支中运行多个代理、处理治理审批、检查指标/日志/使用情况，并将分支提升至主分支。在以下情况下使用此技能：在 InstaCloud 管理的项目中工作（`.insta/` 目录或 `insta` CLI）、用户提及 InstaCloud 或 insta，以及当用户请求部署应用程序、需要数据库/后端/对象存储、需要计划或定期任务、需要预览或每个代理的沙盒环境、需要可分支的基础设施、需要从 Heroku / Railway / Fly / Render 迁移现有应用程序，或提及代理设置或 MCP（即使他们没有明确提及 "InstaCloud"）。此外，还涵盖 insta-cloud 远程 MCP 服务器（insta_* 工具）和自托管的 insta-oss 运行时（相同 CLI，本地守护进程）。
---

# InstaCloud

## 代理执行模式（托管平台）

`agent policy` 是唯一的策略系统。人类使用标准的 RBAC；只有代理请求会进入策略评估器。之前的 `policy` 命令和 `--always` 接受标志已被移除。

作为代理调用 CLI 时，始终使用 `insta --agent <command> …`，包括设置和只读命令。示例包括显式地包含全局标志；使用 npx 时，使用 `npx -y insta@latest --agent <command> …`。不要仅依赖环境检测。

明确为人类管理员标记的命令是转发指令，而不是代理工具调用：切勿自行执行它们或移除 `--agent` 来绕过限制。

首先在关联项目中运行 `insta --agent agent setup`（或 `--project <id>` / `--create <name>`）。这会存储一个项目绑定的、24 小时有效的会话在 `.insta/agent-session.json` 中，Git 会自动忽略它。它补充了现有的用户登录。缺失、过期、吊销或错误项目的会话会因设置指导而失败；切勿在未使用 `--agent` 的情况下重试被拒绝的代理请求。

已知的 Codex/Claude 代码/Cursor 环境也会激活代理模式；通用的 CI 或缺乏 TTY 不会。MCP 工具调用会自动成为代理请求。检查 `insta --agent agent policy get --json` 获取当前模式和受保护分支。所有项目最初使用 `full_access`。

在 `branch_specific`（以及 `customize`，它使用相同的模式并带有显式规则）中，受保护的写入会被拒绝；有风险的无保护操作需要人类批准。将批准命令转发给人类管理员，并在批准后重试未更改的原始请求；代理不能批准自己的请求。详细信息和 SQL 限制：[governance.md](references/governance.md)。此协议需要支持代理会话的托管平台版本；旧版本/OSS 端点不实现它，会话错误不是在无声切换执行身份的理由。

InstaCloud 在一个 CLI 和一个凭证边界后面提供和管理项目的云服务。`insta` CLI 仅与 InstaCloud 控制平面通信——你永远不会直接配置云后端。一个项目可以有任意数量的 **服务**，按需添加。你直接构建的常见服务类型包括：

- **postgres** — 关系型数据库，在其计划的资源上限时出生（使用 `insta --agent postgres limits` 在任何计划的免费上限内移动它；超出免费上限需要付费计划）。纯 Postgres：直接使用绑定到计算环境（见下文）的 `DATABASE_URL` 连接任何驱动程序/ORM——不需要供应商 SDK 或供应商技能。数据库也可以从计算外部公开拨号：`insta --agent postgres url` 打印连接字符串，`insta --agent postgres connect` 打开一个 psql 会话——这就是你（或人类）从笔记本电脑、迁移脚本或任何外部工具访问它的方式。它在空闲时扩展到零，因此请保持你的池的 `idleTimeoutMillis` 在暂停窗口（见 [frameworks.md](references/frameworks.md)）之下。
- **storage** — S3 兼容的对象/存储桶存储。将任何 S3 库指向绑定的 `AWS_*` / `BUCKET_NAME` 环境——不需要供应商 SDK。显式设置端点，或者客户端会与真实的 AWS 通信；通常每个分支都会得到一个分叉的存储桶（旧版快照项目共享一个——见下文）。见 [storage.md](references/storage.md)。
- **compute** — 你在公共 URL 上的容器（们）。一个项目可以有多个计算服务（例如 `api`、`worker`）。
- **redis/mysql/mongodb** — 托管的 Fly 背层数据服务。它们暴露连接环境名称，例如 `REDIS_URL`、`MYSQL_URL` 和 `MONGODB_URL`。

**新项目为空**——不会自动创建任何服务。添加你需要的服务：`insta --agent service add postgres <name>`、`insta --agent service add compute <name>`、`insta --agent service add storage <name>`、`insta --agent service add redis <name>` 等。一个项目可以有每种类型的 **多个服务**，每个分支的上限由计划设置（见 [cli-reference.md](cli-reference.md)）。提供者凭证的范围是创建它们的服务的凭证，并在该范围内使用规范名称（`DATABASE_URL`、`REDIS_URL`、`MYSQL_URL`、`MONGODB_URL`、`AWS_ACCESS_KEY_ID`、`BUCKET_NAME`、…）。**本地开发边界**（`insta --agent secrets` → `.env`、`insta --agent run`）包含每种类型的每个设置，来自该分支上该类型的主服务——但它们 **不会** 自动出现在 **计算环境** 中：容器只能通过显式绑定获得提供者凭证，非主同类型服务不在包中：对于 **postgres**，使用 `insta --agent postgres url <name>` 读取；对于其他类型，没有任何直接读取——绑定它，或者读取它绑定到的计算服务的环境 `insta --agent secrets --service compute/<name>`。绑定计算服务需要的凭证，然后部署——或者，如果服务已经在运行，`insta --agent compute restart`（CLI ≥ 0.0.51）来获取绑定，而无需部署新服务。它重新运行已记录的镜像引用，因此移动标签（`app:latest`）上的服务仍然会得到该标签现在解析到的任何内容——在使用它之前，请参阅 [operate.md](references/operate.md)：

```bash
insta --agent secrets sources                    # 可用于绑定（--branch <b> 目标另一个分支）
insta --agent secrets bind DATABASE_URL postgres/db --to compute/app
insta --agent secrets bind REDIS_URL redis/cache --source-name REDIS_URL --to compute/app
insta --agent secrets bind MYSQL_URL mysql/orders --source-name MYSQL_URL --to compute/app
insta --agent secrets bind MONGODB_URL mongodb/catalog --source-name MONGODB_URL --to compute/app
insta --agent deploy . --group app --port 8080
```

绑定仅用于 **计算环境**。要你自己使用凭证——运行迁移、检查数据、将本地工具指向数据库——直接读取值：`insta --agent postgres url`（postgres 连接字符串；`insta --agent postgres connect` 用于 psql shell）。

使用 `insta --agent service rename <type> <name> <new-name>` 重命名服务；现有的绑定仍然指向该服务。

## 安装和升级 CLI

如果 `command -v insta` 找不到任何内容，请安装它（永远不要假设它存在）：

```bash
curl -fsSL https://raw.githubusercontent.com/InsForge/insta-cli/main/install.sh | sh  # 原生二进制文件，无需 Node
npm install -g insta                                    # npm 替代方案
npx insta@latest --agent <cmd>                                  # 一次性，始终最新（每次调用较慢）
```

CLI 预 1.0 版本，经常发布。如果命令行为不正常或无法识别，**首先升级**：`insta --agent upgrade`（有此功能的 CLI；预 1.0 版本默认开启自动更新——`insta --agent config autoupdate off` 来禁用），否则重新运行安装程序（幂等）或 `npm update -g insta`。

## 两个目标，一个 CLI

相同的命令驱动两个目标。从 `insta --agent status`（`api:` 行）解析你所在的哪个：

- **InstaCloud（托管云）** — 需要 `insta --agent login`（代理：`--email/--password` 或 API 令牌；人类：裸 `insta --agent login` 在浏览器中打开控制台登录/批准页面——任何账户类型；无头机器，其他地方可以联系到人类：`--device` 打印链接 + 代码，他们可以从任何其他浏览器批准）。**CI 和长时间运行的自动化使用范围 API 令牌**：`insta --agent tokens create <name> --org <id>`（或 `--project <id>`），然后 `insta --agent login --api-key <insta_…>`——永远不会使用全局账户令牌。来自任何命令的 `403 token_scope` 意味着凭证比调用更窄，而不是缺少角色；从账户登录中铸造更宽的令牌，而不是触摸成员资格（见 [cli-reference.md](cli-reference.md#commands)）。
- **insta-oss（本地托管守护进程）** — `INSTA_API_URL=http://127.0.0.1:8080`（它的默认值）。
  **不存在登录或不需要登录**（本地信任，内置 `local` 用户）；计费/使用量/指标返回清晰的“云仅限”错误——不要重试它们。

## 工具路由：CLI 与 MCP

InstaCloud 有两个面向代理的操作路径。**此技能 + CLI 是默认的**——CLI 覆盖完整的命令表面（除了几个仅限 MCP 的只读诊断，列在 mcp.md 中），携带关联存储库上下文（`.insta/project.json`），并且是本地机器状态唯一的路径：认证（`insta --agent login`）、获取秘密 **值**（`insta --agent secrets` / `insta --agent run`，以及通过 `insta --agent postgres url` / `insta --agent postgres connect` 的 postgres DSN），源目录部署（`insta --agent deploy <dir>`），以及观察挂钩。

仅在 CLI 无法调用时才回退到 **远程 MCP 工具**（`insta_*`）：没有 shell（如 Claude.ai / ChatGPT 连接器）或 CLI 未安装且无法安装（常见情况是 PATH 上没有 CLI：`npx -y insta@latest --agent agent setup -y` 会自行安装它——见自我修复 below）。相同的平台 API、相同的治理门禁、相同的审计跟踪——但 MCP 工具需要 **显式的 `projectId`/`branch` 参数**：永远不要假设 CLI 的关联上下文会传递过来；首先解析 ID（`insta_list_projects`）并显式传递它们。完整映射 + 连接指南：**[mcp.md](references/mcp.md)**。

**自我修复**：如果预期 InstaCloud 技能或 `insta_*` MCP 工具缺失，运行 `insta --agent agent setup -y`（安装技能 + 注册 MCP 用于 Claude Code 和每个检测到的代理），然后告诉用户**重启他们的编码工具**——运行中的会话永远不会获取新注册的 MCP 服务器或工具。特定代理：`insta --agent config install-mcp --agent <slug>`。注册本身不会验证客户端；实际工具使用需要完成的 OAuth 流程或授权凭证。`--mcp-token` 选项需要令牌创建权限；被 `403 unclassified_agent_action` 拒绝的代理必须停止该尝试，而不是重试作为人类。对于无人值守认证，请阅读 [mcp.md](references/mcp.md#connecting)。

## 当 InstaCloud 不是答案时

直接说，停止，而不是强迫适合。下面的每一行都是可检查的，因此命名一个是给用户的真实答案，而不是拒绝参与：

| 不适合 | 原因 |
| --- | --- |
| GPU 训练或大型模型推理 | 没有提供 GPU |
| 多容器 docker compose 应用 | 托管计算没有 Docker-in-Docker 和嵌套虚拟化 |
| 有人不断在里面切换的交互式 shell | 该 shell 是 `insta compute ssh`，需要批准，并且它会落在访客根目录而不是容器内。这一行不是关于 `compute exec`，也不是关于分支环境：每个代理一个分支是隔离工作的支持方式，也是上述方向之一 |
| 作为服务部署的一次运行后退出脚本 | 健康门期待持续运行并回答的东西。当服务已存在时，在它内部运行脚本使用 `insta compute exec`，这是为一次性命令设计的，并限制在 180 秒内 |
| 只有后端存在于其他地方的静态前端 | 仓库中没有运行服务器，因此没有环境可以分叉，也没有状态可以保留，静态主机做得更好。如果后端也是用户的，请判断其仓库 |

前四个是平台无法做的事情。第五个它可以做，但不应选择，因此指向工作所属的地方。同一列表也发布在 <https://instacloud.com/prompt.md>，以及仓库被判断的方向。保持两者同步。

## 基于意图的路由

在运行预检仪式之前，根据意图路由：

**“发布/部署此应用”（从零开始）：** 不要先查询状态——运行链并宣布它：`insta --agent status`（已登录？已关联？）→ 如果云上未认证，`insta --agent login` → 如果未关联，`insta --agent project create <dir-name>` → `insta --agent service add postgres db`（如果应用需要数据库）+ `insta --agent service add compute app` → 将所需服务凭证绑定到计算（`insta --agent secrets sources`，然后 `insta --agent secrets bind DATABASE_URL postgres/db --to compute/app`）→ `insta --agent deploy . --port <应用监听的端口>` → **验证打印的 URL 是否提供服务**（见下文）。应用读取 `process.env` 凭证。

**“设置/入职/注册”：** 云 → `insta --agent login`（浏览器登录；如果未打开浏览器，则转发打印的链接）或 `--email/--password`；然后 `insta --agent project create`。本地/oss → 超过守护进程之外无需设置。

**一个现有项目上的工作单元（功能、修复、实验、代理任务）：** 每个工作单元一个分支——见核心原则 below 和 **[branching.md](references/branching.md)**。永远不会在 `main` 上开发。

**其他任何东西（配置、调试、检查）：** 轻量级预检，然后匹配下文参考。

## 预检和上下文（在变更之前）

```bash
command -v insta                 # 安装？(否则：安装部分)
insta --agent status --json              # 目标 api，登录，关联项目，当前分支
```

跳过上述从零发布的链的此仪式——`status` 已经是其第一步。

**上下文规则（多代理安全）：**

- 链接（`./.insta/project.json`）是 **按目录** 的，并包括当前分支。
- **优先使用显式的 `--branch <name>`** 在接受它的命令上（`secrets`、`deploy`、`<type> metrics`、`<type> logs`、`agent events`、`postgres url` / `postgres connect`——错误的分支 DSN 意味着查询错误数据库）而不是 `insta --agent branch switch`，当你对不拥有的分支采取行动时——`switch` 修改共享的按目录链接，并在同一检出中的并行代理中竞争。
- 对于并行代理，规则是 **1:1:1 — 任务 ↔ git 工作树 ↔ insta 分支**（每个工作树都有自己的链接，所以 `switch` 在那里是安全的）。见 [branching.md](references/branching.md)。

## 核心原则

**一个工作单元 = 一个分支 = 一个隔离的环境。** `insta --agent branch create <name>` 会将 **父分支的** 当前服务材料化到新分支上——一个 CoW 数据库分支（父数据的副本）、一个 CoW 分叉的存储桶，以及每个计算服务的克隆（每个都有自己的 URL），在分支创建时创建，因此分支从一开始就是一个可运行的完整环境。
分支完全并行运行；你做的任何事都不会影响另一个。**≤10 个分支每个项目（硬限制）。** 不要在 `main` 上开发；不要在一个分支上堆叠多个功能。

**一次有多个独立功能（或代理任务）？** 给每个分配自己的分支 **和自己的子代理**——隔离的 DB + 存储桶 + 计算器 + URL 意味着零冲突。见 **[branching.md](references/branching.md) → 并行代理**。

## 部署前验证（部署）

**仅凭命令退出就报告部署成功是不对的。** `insta --agent deploy` 成功时打印分支 URL——这意味着平台接受并滚动了机器，而不是应用正在服务：

1. 每 ~3 秒轮询打印的 URL (`curl -s -o /dev/null -w '%{http_code}'`)，最多 ~60 秒。
   创建的扩展到零的服务（使用 `--no-always-on` 创建，或使用 `insta --agent compute always-on off` 关闭）在第一个请求时冷启动——允许慢速第一个命中。自 2026-09-07 以来，计算服务始终是始终开启的，并跳过此步骤；见 references/operate.md。
2. `200`（或应用预期的状态）→ 部署；报告 URL。
3. 仍然失败 → [operate.md](references/operate.md) 中的有序故障排除列表（端口不匹配和迁移门控启动解释了大多数失败）。
4. 报告确切的失败状态——永远不会声称你没有观察到的成功。

## 批准转发（关键——受门禁操作）

敏感操作在凭据边界处受到限制（`secrets.read`、`secrets.write`、`deploy`、`project.delete`、`branch.delete`、`service.add/remove/scale/upgrade`、`domain.purchase`、`domain.delegate`、`zone.delegate`；每个操作对应一项策略：允许/拒绝/需审批，使用项目的代理策略）。当命令返回 **“需要审批”以及一个审批 ID** 时：

- **立即且原样地将其转达给人类** —— 在人类终端中运行的准确命令为：`insta agent approvals approve <id>`。审批仅针对某一条确切请求生效。不要将其概括省略，不要重试该命令，且不要在未先呈现审批的情况下就将任务报告为失败。仅 **管理员** 可以审批。
- 授权是 **一次性** 的：审批通过后，**重新运行原始命令**；下次出现时仍会再次提示，除非人类明确更改适用的 `agent policy` 规则。
- **绝不绕过门禁**（例如通过手动编辑状态或绕过 CLI）—— 门禁是产品的安全模型。`deny` 策略是硬性否定：上报即可，不得规避。

## 常用快速操作

```bash
insta --agent status --json                          # 目标、登录、链接、当前分支
insta --agent agent manifest --json                        # 代理可读的环境视图：每个分支的服务 + URL
insta --agent service list --json                   # 该项目中存在哪些资源
insta --agent run -- <cmd>                           # 在注入分支集束（完全不在磁盘上；--branch <b>）后运行
insta --agent run --service compute/app -- <cmd>     # 单个服务自身的环境变量——当多个服务定义同名项时需要
insta --agent run --ignore-collisions -- <cmd>       # 仍要运行；每个冲突的名称都从子进程中移除
insta --agent secrets --print                        # 分支的密钥（--branch <b>，--service <compute/name>）
insta --agent secrets sources --json                 # 可供绑定的供应商凭据源
insta --agent secrets bind DATABASE_URL postgres/db --to compute/app
insta --agent secrets bindings --target compute/app --json
insta --agent secrets set NAME value                 # 用户配置（项目级；--branch 用于分支覆盖）
insta --agent build . --port 8080                    # 本地部署前构建/就绪检查
insta --agent deploy . --port 8080                   # 远程构建（Dockerfile，或在 insta-compute 上使用 nixpacks）+ 部署到当前分支
insta --agent deploy --image <ref> --port 8080       # 使用预构建镜像
insta --agent compute connect-repo owner/repo app    # 仅云侧；引导 GitHub 授权和 App 访问，然后连接；或使用 --public
insta --agent compute exec app -- printenv PORT      # 在实时计算上执行一次性命令（无 shell/stdin）
insta compute ssh app --setup                        # 仅人类可用：通过 `ssh app.insta` 进入交互式 shell（拒绝 API 密钥；代理请使用 `compute exec`）
insta --agent compute volume app --size 1Gi          # 附加/扩展持久化 /data；下次部署或 `compute restart` 时挂载
insta --agent branch create feat && insta --agent branch list --json
insta --agent compute logs --limit 100 --json        # 运行时日志（--branch <b>；亦支持 <postgres|redis|mysql|mongodb>；postgres 受供应商限制）
insta --agent compute logs --since 2h --json         # 时间窗口（也可用 --from/--to）—— 无窗口读取仅为单页（约 100 行）
insta --agent compute metrics --json                 # 服务指标（亦支持 <postgres|redis|mysql|mongodb>）
insta --agent agent events --limit 50 --json               # 审计 + 代理事件时间线
insta --agent billing usage --json                           # 仅云侧（insta --agent billing --json 同理）
insta --agent agent approvals list --status pending        # 待处理门禁
```

凡是要解析输出，一律使用 `--json`。

## 路由

对于超出上述快速操作范围的一切内容，加载与意图匹配的参考文档——通常一份就够，最多两份：

| 意图 | 参考文档 | 涵盖内容 |
| --- | --- | --- |
| 创建或连接资源（“搭建”、“新建项目”、“添加数据库/计算资源”） | [setup.md](references/setup.md) | CLI 安装/升级，云 vs oss 目标，认证，项目，服务，从零起步 |
| 按计划运行（“每晚”、“cron 任务”、“周期性任务”、“每小时运行此命令”） | [cli-reference.md](cli-reference.md#cron) | `insta --agent cron` 命令，仅限 UTC 的表达式，服务 vs 外部目标（平台允许组织内任意服务；CLI 触达当前分支的），运行 ID 幂等契约，用于凭据的 `--secret-ref`（发送时解析，因此轮换无需编辑），编辑是替换而非合并请求，以及每个运行状态的含义 |
| 发布代码或管理版本 | [deploy.md](references/deploy.md) · 框架配方：[frameworks.md](references/frameworks.md) | 镜像 vs 源码（远程构建），`--port` 语义，显式服务凭据绑定，运行时密钥，验证流程，Dockerfile 模板，自定义域名（已购域名的顶点域通过 `insta --agent domain delegate` 提供服务） |
| 将现有应用迁移进来（“将我的 Render/Railway 服务迁移到 InstaCloud”、“从 Heroku/Railway/Fly/Render 移走”、“导入我的应用”、“把我的应用带过来”） | [migrate.md](references/migrate.md) **外加** 你所需的来自 `references/migrate/` 的源文件（`render.md`、`railway.md`、`fly.md`、`insforge.md`） | 带通过条件和回滚边界的有序切换，InstaCloud 侧的语义要点（绑定需要一次部署，无批量环境变量导入，cron 是 HTTP 而非命令，workers），命令 + 附加功能映射，按源区分（每个源现在都有独立文件，应与 migrate.md 并读而非替代）的增量内容 |
| 分支环境，并行代理，晋级（“预览环境”、“每个任务一个沙箱”、“合并到 main”） | [branching.md](references/branching.md) | **数据分叉环境模型**（实际克隆的是什么），分支循环，1:1:1 worktree 模式 + 分发简报，晋级，迁移纪律 |
| 审批、策略、审计、凭据扫描 | [governance.md](references/governance.md) | 门禁目录，审批转达，事件时间线，observe hook，代理审计模式 |
| 检查健康状态或排查失败 | [operate.md](references/operate.md) | 状态/manifest 分诊，有序的部署失败清单，指标/日志，云 vs oss 差异 |
| 命令查找 | [cli-reference.md](cli-reference.md) | 带标志和门禁的完整 CLI 目录 |
| 远程 MCP 工具（“连接一个连接器”，可用 `insta_*` 工具） | [mcp.md](references/mcp.md) | 连接客户端，工具 ↔ CLI 映射，哪些功能仅限 CLI |
| InstaCloud 本身成了阻碍（bug、文档过期、功能缺失、摩擦） | [cli-reference.md → Feedback](cli-reference.md#feedback) | `insta --agent feedback` / `insta_send_feedback`：何时提交，情形 → 类型映射 |

如果请求涉及两个领域（“部署并检查其健康状态”），两份都加载，然后一次性作答。

## 两条不可妥协的原则（无论你在何处）

- 对于任何需要分支密钥的内容，**优先使用 `insta --agent run -- <cmd>`** —— 集束在每次调用时获取，仅注入到子进程环境；不会写入磁盘，因此不会泄露或被提交。集束还携带该分支 **规范** 的供应商凭据 —— 每种类型一组，来自该类型的主服务 —— 因此本地运行即可访问数据库，无需绑定任何内容。 **计算服务** 接收的内容是分开的：使用 `insta --agent secrets bind` 绑定，然后部署（或对已在运行的服务执行 `insta --agent compute restart`，CLI ≥ 0.0.51 —— 绑定变更本身不会到达运行中的机器）。 **当多个服务定义同名项时，`run` 会拒绝并退出 2**（CLI ≥ 0.0.65）：不会生成任何进程，冲突的名称及两条解决路径会打印到 stderr。不要将其视为瞬时故障而重试 —— 使用 `--service <type>/<name>` 运行以获取该服务的环境，或使用 `--ignore-collisions` 使那些名称从子进程环境中移除后继续。退出 2 也是审批代码，因此请阅读 stderr 消息以区分二者。
- 当确实需要文件时，将 `./.env`（来自 `insta --agent secrets`；在 git 仓库中自动 gitignore）视为 密钥的 **唯一** 基于文件的来源 —— 其中包含你的用户密钥以及分支的主供应商凭据 —— 永远不要硬编码或打印密钥值。 `DATABASE_URL`、`AWS_*` / `BUCKET_NAME`、`REDIS_*`、`MYSQL_*` 和 `MONGODB_*` 是服务凭据，仅通过显式的 `insta --agent secrets bind` 规则到达生产计算。在计算 **外部** 直接使用时，授权的读取方式是 `insta --agent postgres url` / `insta --agent postgres connect`（postgres；受 `secrets.read` 门禁保护）—— 通过管道传递（`psql "$(insta --agent postgres url)"`），永远不要将 DSN 粘贴到文件或代码中。对于所有类型，分支的 **主** 服务的凭据已包含在 `insta --agent secrets` / `insta --agent run` 中。 **非主** 服务不在集束中：postgres 有上述的 `[service]` 位置参数读取方式（`insta --agent postgres url <name>`），而 **没有其他类型有直接读取方式** —— 请绑定它，或使用 `insta --agent secrets --service compute/<name>` 读取该服务自身的环境。用户设置的配置应放入 `insta --agent secrets set <NAME>`（项目级）/ `--branch` 用于分支覆盖 —— 永远不要手动编辑你希望持久化的 `.env` 值。
- 将 **每个** schema 变更都跟踪为 `migrations/` 下的文件，以便在分支数据库上重放，并在合并后在 `main` 上再次重放。 **InstaCloud 从不合并数据库 —— 只有迁移文件将 schema 向前推进。** 迁移在数据库凭据绑定的地方运行：在计算服务上，通过 `insta --agent compute exec app -- <migrate-cmd>`（绝不作为启动门禁 —— 参见 [deploy.md](references/deploy.md)）；或直接运行，不涉及计算：`psql "$(insta --agent postgres url --branch <b>)" -f migrations/<file>.sql`（显式 `--branch` —— 无参数形式读取已链接分支的 DB）。先让 `psql` / `pg_dump` / `pg_restore` 匹配服务器的 Postgres 主版本 —— 在 `insta --agent service list --json --branch <b>` 上查看 `pg_version`（与 DSN 相同的分支）；如果该行没有，则读取确切版本（参见 [operate.md](references/operate.md)）。

## 治理与审计（这是平台的核心差异化优势）

门禁机制和转达流程如上所述；observe 凭据审计 hook、事件时间线和代理审计模式见 [governance.md](references/governance.md)。

**计费基于实际应用用量**（实际消耗的 vCPU·min / RAM GB·min + 存储 + 出口流量 —— 而非机器大小 × 小时数）。新的计算服务天生始终开启（自 2026-09-07 起）：无冷启动，空闲应用的驻留 RAM 按实际用量计费。缩放至零（创建时使用 `--no-always-on`，或 `insta --agent compute always-on off`）使空闲服务几乎零成本，代价是冷启动；postgres 不受影响（`insta --agent postgres always-on`，默认关闭）—— 参见 [operate.md](references/operate.md)。 **付费杠杆是资源上限**（`insta --agent compute limits`、`insta --agent postgres limits` —— 单台机器大小，参见 [operate.md](references/operate.md)） **以及机器数量**（`insta --agent compute scale` —— 水平方向）：新服务在其计划上限处生成，免费计划可以在免费上限内移动但不能超出，且保持一台机器 —— 超出即返回 403 —— 先执行 `insta --agent billing subscribe`；`insta --agent billing usage` / `insta --agent billing` 显示周期用量和成本。每个用户只有一个免费组织。完整标志见 [cli-reference.md](cli-reference.md)。

## 当 InstaCloud 本身成为阻碍时（反馈）

如果你遇到 **InstaCloud 的过错** 造成的障碍 —— 违反其文档契约的命令、与事实不符的技能/文档文本、缺失的能力、令人困惑的 UX —— 使用 `insta --agent feedback`（或 `insta_send_feedback` MCP 工具）上报， **然后通过变通方案继续用户的任务**。绝不要因上报而阻塞，并且 **绝不要为用户正在构建的应用中的问题提交反馈** —— 此通道仅用于 InstaCloud 工具包（`--component cli|mcp|platform|skills|docs`）。团队将在控制台中回复，用户在控制台阅读并作答； **（CLI ≥ 0.1.7）** 你只会收到工单链接，并在请求时获得其状态。完整标志及情形 → 类型映射：[cli-reference.md → Feedback](cli-reference.md#feedback)。

## 响应格式

对于操作性工作，报告： **做了什么**（操作 + 范围：项目/分支/服务）、 **结果**（URLs、ID、观察到的状态 —— 而非假设的）以及 **下一步**（或任务已完成）。仅在有帮助时包含命令输出。
