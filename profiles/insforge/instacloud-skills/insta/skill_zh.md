# InstaCloud

## 代理执行模式（托管平台）

`agent policy` 是唯一的策略系统。人类使用标准的 RBAC；只有代理请求会进入策略评估器。之前的 `policy` 命令和 `--always` 标志已被移除。

作为代理调用 CLI 时，始终使用 `insta --agent <command> …`，包括设置和只读命令。示例包括显式地包含全局标志；使用 npx 时，使用 `npx -y insta@latest --agent <command> …`。不要仅依赖环境检测。
明确为人类管理员标记的命令是转发指令，而不是代理工具调用：不要自己执行它们或移除 `--agent` 来绕过限制。
首先在链接的项目中运行 `insta --agent agent setup`（或 `--project <id>` / `--create <name>`）。
这会存储一个项目绑定、24 小时会话在 `.insta/agent-session.json` 中，自动被 Git 忽略。它补充了现有的用户登录。缺失、过期、撤销或错误项目的会话会以设置指导失败；不要在没有 `--agent` 的情况下重试被拒绝的代理请求。
已知的 Codex/Claude 代码/Cursor 环境也会激活代理模式；通用的 CI 或缺乏 TTY 不会。MCP 工具调用会自动成为代理请求。检查 `insta --agent agent policy get --json` 获取当前模式和受保护分支。所有项目最初使用 `full_access`。
在 `branch_specific`（以及 `customize`，它是相同的模式但带有显式规则）中，受保护的写入被拒绝；有风险的无保护操作需要人类批准。将批准命令转发给人类管理员，并在批准后重试不变的原始请求；代理不能批准自己的请求。详细信息和 SQL 限制：[governance.md](references/governance.md)。此协议需要支持代理会话的托管平台版本；旧版/OSS 端点不实现它，会话错误不是无声切换执行身份的理由。

InstaCloud 在一个 CLI 和一个凭证边界后面提供和管理项目的云服务。`insta` CLI 仅与 InstaCloud 控制平面通信——你永远不会直接配置云后端。一个项目可以有任意数量的 **服务**，按需添加。你直接构建的常见服务类型包括：

- **postgres** — 关系型数据库在其计划的资源上限时出生（使用 `insta --agent postgres limits` 在任何计划的免费上限内移动它；超过免费上限需要付费计划）。纯 Postgres：直接使用绑定到计算环境（下方）的 `DATABASE_URL` 连接任何驱动程序/ORM——不需要供应商 SDK 或供应商技能。数据库也可以从计算外部公开拨号：`insta --agent postgres url` 打印连接字符串，`insta --agent postgres connect` 打开 psql 会话——这就是你（或人类）从笔记本电脑、迁移脚本或任何外部工具中访问它的方式。它在空闲时扩展到零，所以保持你的池的 `idleTimeoutMillis` 在挂起窗口（见 [frameworks.md](references/frameworks.md)）之下。
- **storage** — S3 兼容的对象/存储桶存储。将任何 S3 库指向绑定的 `AWS_*` / `BUCKET_NAME` 环境——不需要供应商 SDK。显式设置端点或客户端与真实 AWS 通信；每个分支通常得到一个分叉的存储桶（遗留的预快照项目共享一个——见下文）。见 [storage.md](references/storage.md)。
- **compute** — 你的容器（们）在公共 URL 下。一个项目可以有多个计算服务（例如 `api`，`worker`）。
- **redis/mysql/mongodb** — 托管的 Fly 背层数据服务。它们暴露连接环境名称，例如 `REDIS_URL`，`MYSQL_URL` 和 `MONGODB_URL`。

**新项目开始为空**——不会自动创建任何服务。添加你需要的服务：`insta --agent service add postgres <name>`，`insta --agent service add compute <name>`，`insta --agent service add storage <name>`，`insta --agent service add redis <name>`，等等。一个项目可以有 **每种类型的多个服务**（每种类型最多 5 个）。提供者凭证的范围是创建它们的服务的服务，并在该范围内使用规范名称（`DATABASE_URL`，`REDIS_URL`，`MYSQL_URL`，`MONGODB_URL`，`AWS_ACCESS_KEY_ID`，`BUCKET_NAME`，…）。**本地开发边界**（`insta --agent secrets` → `.env`，`insta --agent run`）为每种类型携带一个，来自该类型在分支上的 **主要** 服务——但它们不会自动出现在 **计算环境** 中：容器只能通过显式绑定获得提供者凭证，非主要相同类型的服务不在组合中：对于 **postgres** 使用 `insta --agent postgres url <name>` 读取；对于其他类型，没有任何直接读取——绑定它，或读取绑定到它的计算服务的环境 `insta --agent secrets --service compute/<name>`。绑定计算服务需要的凭证，然后部署——或者，如果服务已经在运行，`insta --agent compute restart`（CLI ≥ 0.0.51）来获取绑定，而无需部署新的一个。它重新运行已记录的镜像引用，所以一个在移动标签（`app:latest`）上的服务仍然得到该标签现在解析到的任何内容——在使用它之前，请参阅 [operate.md](references/operate.md)：

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

如果 `command -v insta` 找不到，就安装它（永远不要假设它存在）：

```bash
curl -fsSL https://raw.githubusercontent.com/InsForge/insta-cli/main/install.sh | sh  # 原生二进制，无需 Node
npm install -g insta                                    # npm 替代方案
npx insta@latest --agent <cmd>                                  # 一次性，始终最新（每次调用较慢）
```

CLI 预装 1.0 并经常发布。如果命令行为异常或不被识别，**首先升级**：`insta --agent upgrade`（有此功能的 CLI；预 1.0 默认开启自动更新——`insta --agent config autoupdate off` 来禁用），否则重新运行安装程序（幂等）或 `npm update -g insta`。

## 两个目标，一个 CLI

相同的命令驱动两个。从 `insta --agent status`（`api:` 行）解析你所在的哪个：

- **InstaCloud（托管云）** — 需要 `insta --agent login`（代理：`--email/--password` 或 API 令牌；人类：裸 `insta --agent login` 在浏览器中打开控制台登录/批准页面——任何账户类型；无头机器在别处可联系人类：`--device` 打印一个链接 + 代码，他们可以从任何其他浏览器批准）。
- **insta-oss（本地托管守护进程）** — `INSTA_API_URL=http://127.0.0.1:8080`（其默认值）。
  **不存在登录或不需要登录**（本地信任，内置 `local` 用户）；计费/使用量/指标返回清晰的“云独有”错误——不要重试它们。

## 工具路由：CLI 与 MCP

InstaCloud 有两个面向代理的操作路径。**此技能 + CLI 是默认的**——CLI 覆盖完整的命令表面（少数仅 MCP 的只读诊断除外，列在 mcp.md 中），携带链接存储库上下文（`.insta/project.json`），并且是本地机器状态的唯一路径：认证 (`insta --agent login`)，拉取密钥值 (`insta --agent secrets` / `insta --agent run`，以及通过 `insta --agent postgres url` / `insta --agent postgres connect` 的 postgres DSN)，源目录部署 (`insta --agent deploy <dir>`)，以及观察挂钩。

仅在 CLI 无法调用时才回退到 **远程 MCP 工具** (`insta_*`)：没有 shell（如 Claude.ai / ChatGPT 连接器等托管代理），或者 CLI 未安装且无法安装（常见情况可通过 PATH 上没有 CLI 解决：`npx -y insta@latest --agent agent setup -y` 自行安装——见下文自我修复）。相同的平台 API，相同的治理门禁，相同的审计跟踪——但 MCP 工具需要 **显式的 `projectId`/`branch` 参数**：永远不要假设 CLI 的链接上下文会传递；首先解析 ID (`insta_project_list`) 并显式传递。完整映射 + 连接指南：**[mcp.md](references/mcp.md)**。

**自我修复**：如果预期 Insta 技能或 `insta_*` MCP 工具缺失，运行 `insta --agent agent setup -y`（安装技能 + 注册 MCP 用于 Claude Code 和每个检测到的代理），然后告诉用户**重启他们的编码工具**——运行中的会话永远不会拾取新注册的 MCP 服务器或工具。特定代理：`insta --agent config install-mcp --agent <slug>`。注册本身不会验证客户端；实际工具使用需要完成的 OAuth 流程或授权凭证。`--mcp-token` 选项需要令牌创建权限；被 `403 unclassified_agent_action` 拒绝的代理必须停止该尝试，而不是重试作为人类。对于无人值守认证，请参阅 [mcp.md](references/mcp.md#connecting)。

## 基于意图的路由

在运行预检仪式之前，根据意图路由：

**“部署这个应用”（从零开始）：** 不要先检查状态——运行链并宣布它：`insta --agent status`（已登录？已链接？）→ 如果在云上未认证，`insta --agent login` → 如果未链接，`insta --agent project create <dir-name>` → `insta --agent service add postgres db`（如果应用需要数据库）+ `insta --agent service add compute app` → 将所需服务凭证绑定到计算 (`insta --agent secrets sources`，然后 `insta --agent secrets bind DATABASE_URL postgres/db --to compute/app`) → `insta --agent deploy . --port <应用监听的端口>` → **验证打印的 URL 可用**（下方）。
应用读取 `process.env` 凭证。

**“设置/上线/注册”：** 云 → `insta --agent login`（浏览器登录；如果浏览器未打开，则转发打印的链接）；然后 `insta --agent project create`。本地/oss → 超出守护进程之外无需设置。

**一个现有项目上的工作单元（功能、修复、实验、代理任务）：** 每个工作单元一个分支——见核心原则下方和 **[branching.md](references/branching.md)**。永远不要在 `main` 上开发。

**其他任何内容（配置、调试、检查）：** 轻量级预检，然后匹配下方的参考。

## 预检和上下文（在变异之前）

```bash
command -v insta                 # 安装？(否则：安装部分)
insta --agent status --json              # 目标 api, login, 链接项目, 当前分支
```

跳过上述链的此仪式——`status` 已经是其第一步。

**上下文规则（多代理安全）：**

- 链接（`./.insta/project.json`）是 **每个目录** 的，包括当前分支。
- **优先使用显式的 `--branch <name>`** 在接受它的命令上（`secrets`，`deploy`，`<type> metrics`，`<type> logs`，`agent events`，`postgres url` / `postgres connect`——错误的分支 DSN 意味着查询错误的数据库）而不是 `insta --agent branch switch`，当你对不拥有的分支采取行动时——`switch` 修改共享的每个目录链接，并并行代理在相同的检出中竞争。
- 对于并行代理，规则是 **1:1:1 — 任务 ↔ git 工作树 ↔ insta 分支**（每个工作树都有自己的链接，所以 `switch` 在那里是安全的）。见 [branching.md](references/branching.md)。

## 核心原则

**一个工作单元 = 一个分支 = 一个隔离的环境。** `insta --agent branch create <name>` 会将 **父分支** 的当前服务在新的分支上具体化——一个 CoW 数据库分支（父数据的副本），一个 CoW 分叉的存储桶，以及每个计算服务的克隆（每个都有自己的 URL），在分支创建时创建，所以分支从一开始就是一个可运行的完整环境。
分支完全并行运行；你做的任何事都不会影响另一个。**≤10 个分支每个项目（硬限制）。** 不要在 `main` 上开发；不要在一个分支上堆叠多个功能。

**一次有多个独立功能（或代理任务）？** 给每个分配自己的分支 **和自己的子代理**——隔离的数据库 + 存储桶 + 计算器 + URL 意味着零冲突。见 **[branching.md](references/branching.md) → 并行代理**。

## 部署前验证（部署）

**仅凭命令退出就报告部署成功是不对的。** `insta --agent deploy` 成功时打印分支 URL——这意味着平台接受并部署了机器，而不是应用正在提供服务：

1. 每 ~3 秒轮询打印的 URL (`curl -s -o /dev/null -w '%{http_code}'`)，最多 ~60 秒。
   冷启动的扩展到零的服务（使用 `--no-always-on` 创建，或使用 `insta --agent compute always-on off` 关闭）在第一个请求时启动——允许慢速第一个命中。自 2026-09-07 以来，新的计算服务始终为始终开启，跳过此步骤；见 references/operate.md。
2. `200`（或应用预期的状态）→ 部署；报告 URL。
3. 仍然失败 → [operate.md](references/operate.md) 中的有序故障排除列表（端口不匹配和迁移启动的启动条件解释了大多数失败）。
4. 报告确切的失败状态——永远不要声称你没有观察到的成功。

## 批准转发（关键——受保护操作）

敏感操作在凭证边界（`secrets.read`，`secrets.write`，`deploy`，`project.delete`，`branch.delete`，`service.add/remove/scale/upgrade`，`domain.purchase`，`domain.delegate`，`zone.delegate`；每个操作的策略：允许/拒绝/批准，使用项目的代理策略）。当命令返回 **“需要批准”并带有批准 ID**：

- **立即和逐字地转发给人类**——要在人类终端中运行的精确行：
  `insta agent approvals approve <id>`。批准仅授权一个确切请求。
  不要总结它，不要重试命令，并且在没有表面批准的情况下不要报告任务失败。只有 **管理员** 可以批准。
- 授予是 **一次性使用**：批准后，**重新运行原始命令**；下一次发生除非人类明确更改适用的 `agent policy` 规则才会再次提示。
- **永远不要绕过门禁**（例如通过手动编辑状态或绕过 CLI）——门禁是产品的安全模型。拒绝策略是一个硬性禁止：报告它，不要规避它。

## 常见快速操作

```bash
insta --agent status --json                          # 目标, login, link, 当前分支
insta --agent agent manifest --json                        # 代理可读环境视图：每个分支的服务 + URL
insta --agent service list --json                   # 此项目上存在什么
insta --agent run -- <cmd>                           # 使用分支捆绑注入运行（磁盘上无任何内容; --branch <b>)
insta --agent run --service compute/app -- <cmd>     # 一个服务的自己的环境 — 当多个定义相同名称时需要
insta --agent run --ignore-collisions -- <cmd>       # 无论如何运行; 每个冲突的名称都会从子环境删除
insta --agent secrets --print                        # 分支的密钥（--branch <b>, --service <compute/name>)
insta --agent secrets sources --json                 # 可用于绑定的提供者凭证来源
insta --agent secrets bind DATABASE_URL postgres/db --to compute/app
insta --agent secrets bindings --target compute/app --json
insta --agent secrets set NAME value                 # 用户配置（项目范围; --branch 用于覆盖）
insta --agent build . --port 8080                    # 本地预部署构建/就绪检查
insta --agent deploy . --port 8080                   # 远程构建（Dockerfile，或 nixpacks on insta-compute）+ 部署到当前分支
insta --agent deploy --image <ref> --port 8080       # 预构建镜像
insta --agent compute connect-repo owner/repo app    # 云独有; 指导 GitHub 授权和 App 访问，然后连接; 或 --public
insta --agent compute exec app -- printenv PORT      # 在运行计算上的一次性命令（无 shell/stdin）
insta compute ssh app --setup                        # 仅人类：通过 `ssh app.insta` 的交互式 shell（API 密钥被拒绝; 代理使用 `compute exec`)
insta --agent compute volume app --size 1Gi          # 挂载/增长持久 /data; 在下一次部署或 `compute restart` 时挂载
insta --agent branch create feat && insta --agent branch list --json
insta --agent compute logs --limit 100 --json        # 运行时日志 (--branch <b>; 也 <postgres|redis|mysql|mongodb>; postgres 受提供者限制)
insta --agent compute logs --since 2h --json         # 时间窗口 (--from/--to too) — 无时间窗口的读取是单页 (~100 行)
insta --agent compute metrics --json                 # 服务指标 (也 <postgres|redis|mysql|mongodb>)
insta --agent agent events --limit 50 --json               # 审计 + 代理事件时间线
insta --agent billing usage --json                           # 云独有 (insta --agent billing --json 同样)
insta --agent agent approvals list --status pending        # 未处理的门禁
```

在需要解析输出的地方使用 `--json`。

## 路由

对于超出快速操作的任何内容，加载匹配意图的参考——通常足够，最多两个：

| 意图 | 参考 | 覆盖 |
| --- | --- | --- |
| 创建或连接事物（“设置”、“新项目”、“添加数据库/计算”） | [setup.md](references/setup.md) | CLI 安装/升级, 云 vs oss 目标, 认证, 项目, 服务, 从零部署 |
| 在计划上运行某事（“每天”、“cron 作业”、“定期任务”、“每小时运行这个”） | [cli-reference.md](cli-reference.md#cron) | `insta --agent cron` 命令, 仅 UTC 表达式, 服务 vs 外部目标（平台允许组织中的任何服务; CLI 针对当前分支的），运行 ID 幂等性合同，编辑会替换请求而不是合并它，以及每个运行状态的含义 |
| 部署代码或管理发布 | [deploy.md](references/deploy.md) · 框架配方: [frameworks.md](references/frameworks.md) | 镜像 vs 源 (远程构建), `--port` 语义, 显式服务凭证绑定, 运行时密钥, 验证程序, Dockerfile 模板, 自定义域名 (购买的域名的主机名通过 `insta --agent domain delegate` 服务) |
| 将现有应用迁移到 InstaCloud 中（“将我的 Render/Railway 服务迁移到 InstaCloud”，“从 Heroku/Railway/Fly/Render 移动”，“导入我的应用”，“将我的应用迁移过来”） | [migrate.md](references/migrate.md) **加上** `references/migrate/` 中的源文件（`render.md`，`railway.md`，`fly.md`，`insforge.md`） | 有序切换 + 传递条件及其回滚边界, InstaCloud 端的语义（绑定需要部署，没有批量环境导入，cron 是 HTTP 而不是命令，工作者），命令 + 添加项映射, 每个源（每个源现在有它自己的文件，与 migrate.md 一起阅读，而不是替代它）差异 |
| 分支环境、并行代理、提升（“预览环境”，“每个任务沙盒”，“合并到 main”） | [branching.md](references/branching.md) | **数据分叉环境模型**（实际克隆的内容），分支循环, 1:1:1 工作树模式 + 派遣简报, 提升, 迁移纪律 |
| 批准、策略、审计、凭证扫描 | [governance.md](references/governance.md) | 门禁目录, 批准转发, 事件时间线, 观察挂钩, 代理审计模式 |
| 检查健康或调试失败 | [operate.md](references/operate.md) | 状态/manifest 故障排除, 有序部署失败列表, 指标/日志, 云 vs oss 差异 |
| 命令查找 | [cli-reference.md](cli-reference.md) | 完整 CLI 目录，包括标志和门禁 |
| 远程 MCP 工具（“连接一个连接器”, `insta_*` 工具可用） | [mcp.md](references/mcp.md) | 连接客户端, 工具 ↔ CLI 映射, 保留 CLI 独占的内容 |
| InstaCloud 自己挡了你的路（问题） | [cli-reference.md → Feedback](cli-reference.md#feedback) | `insta --agent feedback` / `insta_feedback`: 何时提交, 情况 → 类型映射 |

如果一个请求跨越两个区域（“部署并检查它是否健康”），加载两个并一次性回答。

## 两个不可协商的事项（无论你在哪里）

- **优先使用 `insta --agent run -- <cmd>`** 对于需要分支密钥的任何内容——捆绑每个调用时获取并仅注入到子环境；没有任何内容写入磁盘，所以不会泄露或提交。捆绑还携带分支的 **规范** 提供者凭证——每种类型一个，来自该类型的 **主要** 服务——所以本地运行可以直接连接数据库，无需绑定任何内容。计算服务接收的是分开的：使用 `insta --agent secrets bind` 绑定，然后部署（或 `insta --agent compute restart` 已运行的服务，CLI ≥ 0.0.51——绑定更改不会自行到达正在运行的机器上）。
  **`run` 在定义相同名称的服务冲突时拒绝并退出 2**：不会启动任何内容，并且名称加上两种方式转发打印到 stderr。不要将其作为临时失败重试——使用 `--service <type>/<name>` 为该服务获取环境，或 `--ignore-collisions` 以从子环境中删除那些名称继续进行。退出 2 也是批准代码，所以请阅读 stderr 消息以区分它们。
- 当确实需要文件时，将 `./.env`（来自 `insta --agent secrets`；在 git 仓库中自动忽略）视为 **唯一的基于文件的密钥来源**——它包含你的用户密钥和分支的 **主要** 提供者凭证——永远不要硬编码或打印密钥值。`DATABASE_URL`，`AWS_*` / `BUCKET_NAME`，`REDIS_*`，`MYSQL_*` 和 `MONGODB_*` 是服务凭证，它们仅通过显式 `insta --agent secrets bind` 规则才能到达生产计算。对于直接使用 **外部** 计算，受认可的读取是 `insta --agent postgres url` / `insta --agent postgres connect`（postgres；受保护的 `secrets.read`）——管道 (`psql "$(insta --agent postgres url)"`), 从不把 DSN 粘贴到文件或代码中。对于每种类型，分支的 **主要** 服务的凭证已经在 `insta --agent secrets` / `insta --agent run` 中。非主要服务不在捆绑中：postgres 使用 `[service]` 位置读取（`insta --agent postgres url <name>`），其他类型没有任何直接读取——绑定它，或读取绑定到它的计算服务的环境 `insta --agent secrets --service compute/<name>`。
  用户设置属于 `insta --agent secrets set <NAME>`（项目范围）/ `--branch` 用于分支覆盖——永远不要手动编辑 `.env` 值，你想持久保存。
- 将 **每个** 模式更改作为文件存储在 `migrations/` 下，以便它在分支数据库上重放，并且在合并后 `main` 上再次重放。**InstaCloud 从不合并数据库——只有迁移文件携带模式向前传递。** 迁移在绑定数据库凭证的地方运行：在计算服务上，通过 `insta --agent compute exec app -- <migrate-cmd>`（永远不会作为启动门禁——见 [deploy.md](references/deploy.md)); 或者直接，没有任何计算参与：
  `psql "$(insta --agent postgres url --branch <b>)" -f migrations/<file>.sql`（显式 `--branch`——裸形式读取链接分支的数据库）。匹配 `psql` / `pg_dump` / `pg_restore` 与服务器的 Postgres 主要版本匹配——在 `insta --agent service list --json --branch <b>`（与 DSN 相同的分支）；如果该行没有，请读取确切版本（见 [operate.md](references/operate.md))。

## 治理与审计（这是平台的核心理念）

门禁机制和转发程序已在上方；观察凭证审计挂钩、事件时间线和代理审计模式在 [governance.md](references/governance.md) 中。

**计费基于实际应用使用情况**（vCPU·min / RAM GB·min 实际消耗 + 存储空间 + 出站——不是机器大小 × 小时）。自 2026-09-07 以来，新的计算服务始终为始终开启：没有冷启动，并且空闲应用的驻留 RAM 按实际使用情况计费。扩展到零（在创建时使用 `--no-always-on` 或 `insta --agent compute always-on off`）使空闲服务成本几乎为零，代价是冷启动；postgres 不变（`insta --agent postgres always-on`，默认关闭）——见 [operate.md](references/operate.md)。**付费杠杆是资源上限**（`insta --agent compute limits`，`insta --agent postgres limits`——每台机器的大小，见 [operate.md](references/operate.md)）**和机器数量**（`insta --agent compute scale`——水平）：新服务在其计划的上限时出生，免费计划可以在免费上限内移动，但不能超过它，并且保持在一台机器上——超出任何一个是 403——`insta --agent billing subscribe` 首先使用；`insta --agent billing usage` / `insta --agent billing` 显示周期使用量和成本。每个用户一个免费组织。完整标志在 [cli-reference.md](cli-reference.md) 中。

## 当 InstaCloud 自己挡了你的路（反馈）

如果你遇到 InstaCloud 的障碍——违反了其文档合同的命令，技能/文档文本与现实不符，缺少功能，令人困惑的 UX——使用 `insta --agent feedback`（或 `insta_feedback` MCP 工具）报告它，**然后继续用户的任务**。永远不要因为报告而阻塞，并且**永远不要为用户正在构建的应用中的问题提交反馈**——这个渠道仅用于 InstaCloud 工具包 (`--component cli|mcp|platform|skills|docs`)。完整标志和情况 → 类型映射：[cli-reference.md → Feedback](cli-reference.md#feedback).

## 响应格式

对于操作工作，报告：**做了什么**（操作 + 范围：项目/分支/服务），**结果**（URL，ID，观察到的状态——不是假设的），**下一步**（或已完成）。仅在有助于输出的情况下包含命令输出。
