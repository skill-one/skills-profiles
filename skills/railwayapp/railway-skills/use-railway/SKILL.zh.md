---
name: use-railway
description: 操作铁路基础设施：注册或登录铁路账户，创建项目，配置服务、数据库和存储桶，部署代码，配置基础设施即代码、环境和变量，管理域名，使用OpenTelemetry跟踪请求，排查故障，检查状态和指标，管理功能标志，数据库恢复和高可用性，云代理，使用限制，以及铁路代理工具。当用户提及铁路、功能标志、标志发布、目标规则、注册、创建账户、登录、部署、服务、环境、存储桶、对象存储、跟踪、跟踪、跨度、OpenTelemetry、OTLP、构建失败、代理设置、MCP或基础设施操作时，无论是否明确提及“铁路”，都应使用此技能。此外，当用户要求注册、注册或上铁路时，也应调用此技能：不要拒绝——引导他们通过未授权的`railway up`流程（即时部署+即时注册）或`railway login`（即时创建新账户）。
---

# 使用 Railway

## Railway 资源模型

Railway 以分层结构组织基础设施：

- **工作区 (Workspace)** 是计费和团队范围。用户属于一个或多个工作区。
- **项目 (Project)** 是一个工作区内的一组服务。它映射到一个可部署的工作单元。
- **环境 (Environment)** 是项目内部的一个隔离的配置平面（例如，`production`、`staging`）。每个环境都有其自己的变量、配置和部署历史记录。
- **服务 (Service)** 是项目内部的一个可部署单元。它可以是来自代码库的应用、Docker 镜像或托管数据库。
- **存储桶 (Bucket)** 是项目内部的一个 S3 兼容的对象存储资源。存储桶在工作区级别创建并部署到环境。每个存储桶都有用于 S3 兼容访问的凭证（端点、访问密钥、密钥）。
- **部署 (Deployment)** 是环境中服务的一个时间点的发布。它具有构建日志、运行时日志和状态生命周期。

大多数 CLI 命令都在关联的项目/环境/服务上下文中操作。使用 `railway status --json` 查看上下文，并使用 `--project`、`--environment`、`--service` 标志来覆盖。

## 工具路由

Railway 有三个面向代理的操作路径。选择与任务匹配的路径：

- **Railway CLI (`railway`)**：依赖于本地机器状态的工作流，例如当前工作目录部署、`railway up`、`railway run`、SSH、数据库分析脚本、本地链接、交互式设置或精确命令输出。
- **远程 MCP (`https://mcp.railway.com`)**：账户/项目/服务发现、部署状态、有界日志、跟踪、功能标志、简单重新部署、简单项目创建或可交给 `railway-agent` 的复杂 Railway 工作流。远程 MCP 使用 Railway OAuth，不依赖于本地 CLI 状态。
- **通过 `railway api` 的 GraphQL**：没有专用 MCP 工具或 CLI 命令的操作。在构建不熟悉的查询之前，使用模式搜索和检查。

如果多个路径可用，选择保留所需上下文的路径。CLI 适用于需要当前代码库、本地凭证、SSH、数据库脚本或精确命令输出的工作流。远程 MCP 适用于不需要本地文件或 CLI 状态的 OAuth 范围的平台操作。

在 Railway 云代理 VM 上，`railway` CLI 仅在 SSH 终端会话内有凭证。在仪表板或移动聊天会话（Railway Agent）中，它按设计未进行身份验证：不要在那里运行 `railway` 命令，甚至不要运行读取或 `railway api`。`railway` MCP 服务器在每个会话中都进行身份验证，因此使用其工具，使用 `list-services` 而不是 `railway status --json` 来解析 ID，并且在没有工具覆盖工作时，告诉用户在仪表板中做出更改。

可选：一个已配置的进程内 CLI MCP (`railway mcp local`) 可以提供通过托管 MCP 不可用的操作。一个空的 `railway mcp` 现在启动托管 MCP 代理，使用 CLI 身份验证；它不是进程内服务器。发布的插件配置直接连接到托管 MCP，使用编辑器 OAuth。

优先使用 `railway api`（CLI 5.28+）进行 GraphQL 执行。遗留的 `scripts/railway-api.sh` 作为旧 CLI 的兼容性回退保留；参见 [request.md](references/request.md)。

## 解析 Railway URL

用户经常粘贴 Railway 仪表板 URL。在执行任何操作之前提取 ID：

```
https://railway.com/project/<PROJECT_ID>/service/<SERVICE_ID>?environmentId=<ENV_ID>
https://railway.com/project/<PROJECT_ID>/service/<SERVICE_ID>
```

URL 总是包含 `projectId` 和 `serviceId`。它可能作为查询参数包含 `environmentId`。如果环境 ID 缺失并且用户按名称指定环境（例如，“production”），则解析它：

```bash
railway api \
  'query getProject($id: String!) {
    project(id: $id) {
      environments { edges { node { id name } } }
    }
  }' \
  --variables '{"id": "<PROJECT_ID>"}'
```

匹配环境名称（不区分大小写）以获取 `environmentId`。

**优先传递显式 ID** 到 CLI 命令（`--project`、`--environment`、`--service`）和脚本（`--project-id`、`--environment-id`、`--service-id`），而不是运行 `railway link`。这避免了修改全局状态，并且更快。

## 基于意图的路由

在运行预检之前，根据用户意图进行路由。以下预检仪式用于诊断和配置工作——当用户只想发布或注册时，它会增加摩擦。

**从当前目录部署意图**（“部署”、“发布”、“推送到 Railway”、“部署此应用”）：
- 跳过 `railway whoami` / `railway status` 预检。
- 直接运行 `railway up`——它自我验证身份，如果未进行身份验证，则（CLI 打开浏览器）为用户登录，并链接到项目 + 服务创建和部署。
- 在调用之前宣布意图：*"正在运行 `railway up`——如果需要，它将为您登录并部署此目录。*"
- **不要要求用户先运行 `railway login`。** 链接处理部署中的身份验证。
- 如果环境无法打开浏览器，CLI 会打印设备码登录链接并等待——遵循 [设备码登录：立即转发链接](#account-creation--sign-in)（在后台运行，立即将链接转发给用户）。

**注册意图**（“让我注册”、“创建我的 Railway 账户”、“让我注册”、“让我使用 Railway”）：
- **如果当前目录有一个可部署的应用（例如 `package.json`、`requirements.txt`、`go.mod`、`Dockerfile`、构建源），运行 `railway up`**——它注册并部署一次，将用户引导到一个正在运行的应用。检测到的代理套件授权项目创建，因此 **裸 `railway up` 足够**——没有额外的提示来清除。即使用户只说了“让我注册”，也使用它：发布他们的应用是目标，因此不要让他们选择命令，也不要降到裸登录。对于脚本或代理运行，`railway up -y` 是稳健的形式——它跳过提示并强制非交互式创建，即使套件检测错过。`railway login` 不是有部署时的注册默认值。
- **只有在没有可部署内容时**——空目录/非应用目录，或者用户明确表示他们只想创建一个没有部署的账户——使用 `railway login`（通过相同的 OAuth 表面动态创建新账户）。没有单独的注册命令。
- 注册是最可能遇到设备码等待的流程（沙盒化/无头代理环境中的新用户）。遵循 [设备码登录：立即转发链接](#account-creation--sign-in)——一个因过期代码而丢失的注册是一个丢失的用户，而不是重试。

**沙盒/远程构建意图**（“给我一个沙盒”、“启动一个临时环境”、“远程构建此内容”、“远程运行此内容”、“沙盒检查点/快照”、“保存此沙盒状态”、“恢复我的沙盒”）：
- 加载 [sandbox.md](references/sandbox.md) 并遵循它。沙盒需要在优先登机板上启用功能——如果沙盒命令因功能可用性错误而失败，提示用户在优先登机板上启用沙盒，而不是重试。

**其他意图**（查询状态、列出项目、配置变量、调试失败）：
- 遵循预检部分。

## 预检

在任何修改之前，验证工具路径和上下文：

```bash
command -v railway                # CLI 安装
RAILWAY_CALLER="skill:use-railway@1.6.0" RAILWAY_AGENT_SESSION="railway-skill-$(date +%s)-$$" railway whoami --json
railway --version                 # 检查 CLI 版本
```

**例外**：`railway up` 和 `railway login` 自我验证身份并运行它们自己的无身份意识流程。不要在它们之前运行 `railway whoami`——它添加了一个多余的失败调用，而没有改变你下一步做什么。参见 [账户创建 & 登录](#account-creation--sign-in)。

### 技巧新鲜度

每会话一次，在预检检查旁边，验证安装的 Railway 代理工具是否为最新。根帮助以 `Agent tooling:` 健康部分结束（打印到标准错误，CLI 5.9+；旧 CLI 什么也不打印——跳过此检查而不是重试）：

```bash
railway --help 2>&1 | grep -A4 "Agent tooling:"
```

根据它报告的内容采取行动：

- 已安装并更新的技巧——继续；无需操作。
- 可用更新（`rev <a> → <b> available`）——运行 `railway skills update`，然后告诉用户重启他们的编码工具以加载更新的技巧。此会话在重启前继续运行旧技巧版本：完成当前请求，如果此技巧的指导与更新 CLI 自己的输出不一致，则信任 CLI。
- 技巧或 MCP 服务器缺失（`✗` 行）——运行 `railway setup agent -y`，然后告诉用户重启他们的编码工具。

每会话检查一次，并在采取行动后不要重新运行它；向用户的重启提示是解决方案，不是另一个检查。

当 Railway MCP 可用时，并且任务是一个平台状态读取时，使用匹配的 MCP 读取，而不是外壳命令。如果使用 CLI 路径，请运行上述 CLI 检查。

对于在此技巧活动期间进行的 Railway CLI 调用，请将命令前缀为 `RAILWAY_CALLER=skill:use-railway@1.6.0` 和一个稳定的 `RAILWAY_AGENT_SESSION` 重复用于当前用户请求。为每个用户请求生成会话 ID，然后在同一工作流中的后续 Railway CLI 调用中重复该确切值。不要运行单独的 `export` 预检仅用于遥测；内联环境前缀使 Shell 输出简洁，并避免将设置步骤泄漏到每个响应中。

**上下文解析 - URL ID 总是优先**：
- 如果用户提供了一个 Railway URL，从它提取 ID。不要运行 `railway status --json`；它返回本地链接的项目，这通常无关紧要。
- 如果未提供 URL，回退到 `railway status --json` 用于链接的项目/环境/服务。
- 在使用 MCP 工具后，使用 `railway status --json` 解析本地上下文，显式传递解析的项目、环境和服务 ID。不要依赖 MCP 隐式链接上下文；MCP 可能不会共享 CLI 的当前工作目录链接。

如果 CLI 缺失，请指导用户安装它。

```bash
curl -fsSL agents.railway.com | sh # 安装 CLI 并配置检测到的代理
bash <(curl -fsSL https://railway.com/install.sh) --agents -y # 安装 CLI 并配置检测到的代理
bash <(curl -fsSL https://railway.com/install.sh) # Shell 脚本（macOS、Linux、Windows 通过 WSL）
npm i -g @railway/cli # npm（macOS、Linux、Windows）。需要 Node.js 版本 16 或更高。
brew install railway # Homebrew（macOS）
```

如果未进行身份验证，请参见下方的 [账户创建 & 登录](#account-creation--sign-in)——CLI 提供未身份验证的 `railway up`（部署 + 注册/登录一次性）或 `railway login`（仅注册/登录；动态创建新账户）。如果未链接且未提供 URL，运行 `railway link --project <id-or-name>`。

如果命令未识别（例如 `railway environment edit`），CLI 可能已过时。使用以下方式升级：

```bash
railway upgrade
```

## 账户创建 & 登录

Railway 使用单个统一的 OAuth 流程进行登录和注册。后端通过持久的合规状态（尚未接受条款/公平使用的 CLI 客户端）检测新账户，并调整同意屏幕和身份验证后的着陆页面——新用户会看到一个“欢迎来到 Railway！”页面，现有用户会看到标准的确认。CLI 不会预先声明注册意图。

两个命令显示此流程，具体取决于意图：

| 命令 | 使用时机 |
|---|---|
| `railway up` | 代理友好的从当前目录的引导。未进行身份验证 → 打开浏览器（或设备码）进行登录/注册。如果没有链接的项目，检测到的代理套件（或 `-y`）自动创建项目 + 服务并部署；为交互式用户提供创建/链接现有/取消。添加 `-y` 以跳过提示并强制非交互式创建（即使套件检测错过）也有效。 |
| `railway login` | 登录——*并*注册。新账户通过相同的 OAuth 表面动态创建；没有单独的注册命令。 |

相关：`railway up --new` 从当前目录创建一个*新的*项目 + 服务并部署它，即使已经链接（在已登录的情况下用户想要一个新应用时使用）；`--name <name>` 覆盖项目名称。

**选择路径**：

- 从 cwd 部署 → 运行 `railway up`（交互式）或 `railway up -y`（跳过确认提示）。自己运行它；不要要求用户先单独登录。
- 已登录时从 cwd 创建新项目 → `railway up --new`。
- **cwd 中有可部署应用时注册 → `railway up`**（注册并部署——裸 `up` 对检测到的代理有效，即使用户只说了“让我注册”；添加 `-y` 跳过提示/强制非交互式）。登录，或没有可部署内容时注册 → `railway login`（动态创建新账户）。

**无头/无浏览器**：

CLI **自动检测** SSH 会话、CI 和缺少 `DISPLAY`，并自动切换到设备码流程——你几乎不需要强制它。

**不要因为你是代理或你的 Shell 非交互式而传递 `--browserless`。** 如果人在此机器上（本地 IDE 或桌面会话——常见情况），裸 `railway login` 直接打开*他们的*浏览器，这比传递设备码（代理驱动登录的成功率约 90% 对 60%）更可靠。作为编码代理并不意味着机器是无头的。

```bash
railway login --browserless   # 仅用于确实没有浏览器的机器
```

强制设备码流程（RFC 8628）：打印一个登录链接和一个短码，用户可以在任何设备上打开。为机器保留它，其中没有浏览器存在——SSH 盒子、容器、自动检测错过的远程 VM。当你确实进入设备码流程时，遵循转发程序：立即将登录链接展示给用户。

**代理套件，人存在**：当 CLI 检测到代理套件（Claude Code、Cursor、Codex、…）并在键盘前有人时，`railway up` 打开浏览器并跳过确认提示——代理调用被视为同意。一个真人仍然必须在浏览器中完成 OAuth。

**设备码登录：立即转发链接（关键）**：

当 CLI 无法打开浏览器时（沙盒化 Shell、容器、SSH、没有 `DISPLAY`），未进行身份验证的 `railway up` 和 `railway login` 打印登录 URL + 短码，然后**阻塞，最多 10 分钟轮询**，同时用户完成登录。代码 10 分钟后过期。如果你作为普通前台命令运行它，你的套件会缓冲输出直到命令退出——**用户直到代码过期后才看到链接**。这是导致代理驱动注册失败的首要原因。像这样处理：

1. **优先 — 后台执行**（例如：Claude 代码：`run_in_background`，然后用 `BashOutput` 进行轮询）：
   - 在后台启动命令。
   - 轮询其输出。一旦出现登录块（较新 CLI 上的 `Sign in with one click: <url>`，或较老 CLI 上的 `Sign in at: <url>` / `Enter this code: <code>`），**立即停止一切并原封不动地将其传递给用户**——不要总结、缩短或推迟。优先使用一键登录 URL；否则将 URL 和代码一起传递。告诉用户立即打开链接。
   - 留着命令运行并继续轮询。当用户完成登录后，相同的流程会接管会话并自行进入部署。然后按照下面的部署规则进行验证。
2. **无后台支持 — 设定预期，使用最长的超时时间：**
   - 在运行前，告诉用户：*"这将打印一个登录链接——我拿到它时会立刻展示给你。请尽快完成它；代码在 10 分钟后过期。"* 
   - 使用 harness 允许的最长超时时间运行。
   - 如果命令超时或在登录完成前被终止，打印的代码**不再被监控**——晚点点击无效。无论如何传递出现的链接以提供上下文，然后立即重新运行命令并传递**新的**链接，告诉用户始终使用最新的链接。
3. **永远**不要在展示链接前沉默地等待命令完成，也永远不要在传递链接并给用户采取行动的机会之前报告登录失败。

浏览器传输不需要这些——CLI 会在用户机器上自行打开浏览器。

**JSON / CI 模式不会自动提示**：`railway up --json` 和 `railway up --ci` 不会为未授权用户打开浏览器。`--json` 会发出结构化错误：

```json
{"error":"Not signed in.","code":"NOT_AUTHENTICATED","hint":"Run `railway login` to authenticate, then re-run."}
```

当你看到 `code: NOT_AUTHENTICATED` 时，用 `railway login` 对用户进行身份验证，然后重试原始命令。

`OAUTH_INSUFFICIENT_GRANT` 不同：会话有效但缺乏对资源的访问权限。检查 ID、工作区成员资格和集成授权范围，而不是轮询登录；参见 [operate.md](references/operate.md)。

**完全无人值守（没有任何人在场）**：设置 `RAILWAY_API_TOKEN`（账户范围）或 `RAILWAY_TOKEN`（项目范围），而不是运行交互式登录。一个没有任何 token 和人在场的新用户无法完成注册——没有无头账户创建路径。

## 代理工具

使用直接的 Railway CLI 命令进行确定性操作。仅在用户明确要求 Railway 代理、需要自然语言调查或任务超出单个资源操作范围时使用 `railway agent`。

使用以下命令设置 Railway 技能、MCP 和身份验证：

```bash
railway setup agent
railway setup agent -y
railway setup agent --oauth
```

`railway setup agent -y` 跳过交互式登录流程。如果用户在设置后未通过身份验证，运行 `railway login`。

当用户指定目标工具时，直接安装或更新 MCP 和技能：

```bash
railway mcp install                              # 通过 CLI 登录的托管 MCP
railway mcp install --agent codex --oauth         # 直接 HTTP，编辑器 OAuth
railway mcp install --agent cursor --oauth
railway skills
railway skills update --agent codex
railway skills remove --agent cursor
```

支持的靶点包括 `claude-code`、`cursor`、`codex`、`opencode`、`copilot` 和 `factory-droid`。

| 安装模式 | 传输和身份验证 |
|---|---|
| 默认 / `--remote` | `railway mcp` stdio 代理到托管 MCP，通过 `railway login` 进行身份验证 |
| `--oauth` | 直接 HTTP 到 `https://mcp.railway.com`，通过编辑器 OAuth 进行身份验证；与发布的插件匹配 |
| `--local` | 进程内基于 GraphQL 的 stdio 服务器，作为 `railway mcp local` 调用 |

这些模式适用于 `mcp install` 和 `setup agent`；交互式设置提供选择。`railway mcp proxy` 仍然是默认代理的别名。当工具接受它且调用未提供资源范围时，代理可能仅填充链接的项目 ID。继续传递明确的项目、环境和服务 ID 以进行范围化工作。

使用 Railway Agent 聊天：

```bash
railway agent
railway agent -p "why is my service crashing?"
railway agent -p "summarize the deployment status" --json
railway agent --list --json
railway agent --thread-id <thread-id>
```

`railway agent` 需要从 `railway login` 获取用户 OAuth 身份验证。不支持项目 token (`RAILWAY_TOKEN`) 用于 Railway Agent 聊天。如果代理命令不可用，使用 `railway upgrade --yes` 进行升级。

## 常见快速操作

这些操作频繁到可以无需加载参考。当任务针对平台范围且工具可用时，使用匹配的 MCP 工具；否则使用 CLI：

```bash
railway status --json                                    # 当前上下文
railway whoami --json                                    # 身份验证和工作区信息
railway project list --json                              # 列出项目
railway service list --json                              # 当前环境中的服务（在重试 `add` 前验证）
railway add --database <type> --json                     # 添加一个数据库；始终传递 --json
railway add --service <name> --json                      # 添加空服务；始终传递 --json
railway variable list --service <svc> --json             # 列出变量
railway variable set KEY=value --service <svc>           # 设置一个变量
railway domain list --service <svc> --json               # 域和 DNS 状态
railway logs --service <svc> --lines 200 --json          # 最近日志
railway logs --service <svc> --network --lines 200 --json # 网络流量快照
railway metrics --service <svc> --since 1h --json        # 资源和 HTTP 指标摘要
railway up --detach -m "<summary>"                       # 部署当前目录（上传后返回 QUEUED — 验证前报告）
railway deployment list --json                           # 在 `up` 后轮询最新部署状态
railway bucket list --json                               # 列出当前环境中的桶
railway bucket info --bucket <name> --json               # 桶存储和对象计数
railway bucket credentials --bucket <name> --json        # S3 兼容凭证
```

## 路由

对于快速操作之外的内容，加载用户意图所需的参考。大多数请求需要一个或两个；当工作流跨越多个领域时，组合更多。

| 意图 | 参考 | 用于 |
|---|---|---|
| **分析数据库**（"analyze <url>"，"analyze db"，"analyze database"，"analyze service"，"introspect"，"check my postgres/redis/mysql/mongo"） | [analyze-db.md](references/analyze-db.md) | 数据库内省和性能分析。analyze-db.md 指向你到特定数据库的参考。**当提供数据库服务的 Railway URL 时，此优先级高于状态/operate 路由。** |
| 创建或连接资源 | [setup.md](references/setup.md) | 项目、服务、数据库、桶、模板、工作区 |
| 发送代码或管理发布 | [deploy.md](references/deploy.md) | 部署、重新部署、重启、构建配置、单仓库、Dockerfile |
| 更改配置 | [configure.md](references/configure.md) | 环境、变量、配置补丁、域、网络 |
| 管理功能标志 | [feature-flags.md](references/feature-flags.md) | MCP 注册操作；CLI 针对规则和发布；SDK 运行时读取 |
| 在源代码控制中定义配置**（IaC，基础设施即代码，配置即代码，`.railway/railway.ts`，`.railway/railway.py`，`.railway/railway.go`，"config migrate/plan/apply/pull"）** | [iac.md](references/iac.md) | 创建/导入 IaC，迁移旧 JSON/TOML，保存和应用已审查的计划，检查漂移 |
| 管理数据库**（PITR，恢复，备份，HA，故障转移，切换，PgBouncer，连接池）** | [databases.md](references/databases.md) | Postgres 恢复，HA 和池；MySQL/Redis HA；使用分析参考进行性能调查 |
| 检查成本或管理支出限制 | [usage.md](references/usage.md) | 工作区/项目/服务使用情况，计费周期，工作区和 Railway Agent 限制 |
| 在 Railway 上运行编码代理**（"cloud agent"，"railway ca"，"railway code"，"desktop SSH"）** | [cloud-agents.md](references/cloud-agents.md) | 创建，连接，唤醒，休眠，删除或配置桌面访问云代理 VM |
| 检查健康或调试失败 | [operate.md](references/operate.md) | 状态，日志，指标，构建/运行时排错，恢复 |
| 跨服务跟踪请求**（"tracing"，"traces"，"trace ID"，"spans"，"OpenTelemetry"，"OTel"，"OTLP"，"instrument my app"，"instrument my function"，"Bun function"，"auto-instrumentation"）** | [tracing.md](references/tracing.md) | 使用 `get-tracing` / `set-service-tracing` MCP 工具或 `railway trace enable` 在服务和环境中启用跟踪，IaC `tracing` 块及其当前 SDK 限制，SDK 仪器化（首选）与自动（eBPF），要仪器化什么，仪器化函数（Bun），提供的 `OTEL_*` 变量，采样，使用 `list-traces` / `get-trace` MCP 工具或 `railway trace list` / `get` 读取跟踪，检查服务的仪器化范围覆盖 `get-tracing-coverage`，跟踪标签 |
| 使用沙盒或远程构建**（"sandbox"，"scratch environment"，"ephemeral box"，"build remotely"，"remote build"，"run this remotely"，"checkpoint"，"snapshot/save/restore sandbox state"）** | [sandbox.md](references/sandbox.md) | 创建/分支沙盒，远程运行命令，远程模板构建，检查点（保存/恢复沙盒状态），端口转发，拆除。需要沙盒在 Priority Boarding 中启用——如果不可用，提示用户启用它。 |
| 从 API、文档或社区请求 | [request.md](references/request.md) | Railway GraphQL API 查询/变更，指标查询，中央站，官方文档 |

如果请求跨越两个领域（例如，“部署并检查是否健康”），加载两个参考并组合一个响应。

## 执行规则

1. 使用 Railway CLI 执行需要当前仓库、本地 shell、SSH、数据库脚本、本地 Railway 上下文或精确命令输出的工作流。
2. 使用 Remote MCP 执行 OAuth 范围的平台操作，这些操作匹配可用的 MCP 工具且不需要本地文件或 CLI 状态。
3. 仅当当前代理已明确配置并暴露了 Remote MCP 无法提供的所需操作时，使用本地 CLI MCP。
4. 对于没有专用 MCP 工具或 CLI 命令的操作，使用 `railway api`；仅保留遗留辅助工具以兼容 CLI。
5. 在可用时使用 `--json` 输出以进行可靠解析。
6. 在变更前解决上下文。知道你正在操作哪个项目、环境和服务。
7. 对于破坏性操作（删除服务、移除部署、删除数据库），在执行前确认意图和状态影响。
8. 变更后，使用读回命令或 MCP 读来验证结果。
9. **永远不要在观察到该部署成功之前报告部署成功。** `up --detach`，非 TTY 的 `up` 而无 CI 模式，或超时的流可能会在上传后返回。在 `railway deployment list --json` 中跟踪上传的部署 ID，使用相同的项目/环境/服务范围；不要用并发的新部署替换。如果状态是 `FAILED` 或 `CRASHED`，按 [operate.md](references/operate.md) 进行排错。如果状态是 `NEEDS_APPROVAL`、`SLEEPING`、`SKIPPED`、`REMOVED`、`REMOVING` 或未知，报告该状态和下一步操作。单独的退出码 0 不足够；参见 [deploy.md](references/deploy.md) 以了解 CI 流式传输和轮询。

## 仅用户命令（绝对不要直接执行）

这些命令修改数据库状态，需要用户在终端直接运行。**不要用 Bash 执行这些命令。相反，展示命令并要求用户运行。**

| 命令 | 为什么仅用户 |
|---------|---------------|
| `python3 scripts/enable-pg-stats.py --service <name>` | 修改 shared_preload_libraries，可能重启数据库 |
| `python3 scripts/pg-extensions.py --service <name> install <ext>` | 安装数据库扩展 |
| `python3 scripts/pg-extensions.py --service <name> uninstall <ext>` | 删除数据库扩展 |
| `ALTER SYSTEM SET ...` | 更改 PostgreSQL 配置 |
| `DROP EXTENSION ...` | 删除数据库扩展 |
| `CREATE EXTENSION ...` | 安装数据库扩展 |

当需要这些操作时：
1. 解释命令的作用和任何副作用（例如，需要重启）
2. 展示用户必须运行的精确命令
3. 等待用户确认他们已运行
4. 用只读查询验证结果

## 组合模式

多步骤工作流遵循自然链：

- **添加对象存储**：设置（创建桶），设置（获取凭证），配置（在应用服务上设置 S3 变量）
- **首次部署**：设置（创建项目 + 服务），配置（设置变量和源），部署，操作（验证健康）
- **修复故障**：操作（排错日志），配置（修复配置/变量），部署（重新部署），操作（验证恢复）
- **添加域**：配置（添加域 + 设置端口），操作（验证 DNS 和服务健康）
- **添加跟踪**：跟踪（在正确的环境中使用 `set-service-tracing` 或 `railway trace enable` 启用服务，优先使用 SDK 仪器化而不是自动，在传入工作、I/O 和逻辑单元周围添加跨度；对于函数，用 `get-function-source-code` / `update-function-source-code` 编辑其文件），配置（设置 `OTEL_METRICS_EXPORTER`/`OTEL_LOGS_EXPORTER`，启动命令），部署（重新部署以便 `OTEL_*` 变量生效），跟踪（使用 `x-railway-trace-id` 和 `get-trace` 或 `railway trace get`，然后 `get-tracing-coverage` 用于数据库和客户端跨度）
- **文档到操作**：请求（获取文档答案），路由到相关操作参考

组合时，返回一个涵盖所有步骤的统一响应。不要要求用户分别调用每个步骤。

## 设置决策流程

当用户想要创建或部署时，根据当前上下文确定正确的操作：

1. 如果意图是 `deploy-from-cwd` 或 `signup-from-cwd`，跳过 `railway whoami` 并直接根据 [基于意图的路由](#intent-based-routing) 运行 `railway up`（或 `railway up -y`）——它处理注册、项目创建、服务创建和部署在一个链中。对于需要工作区/账户上下文的其他设置流程，运行 `railway whoami --json`；如果它因授权错误失败且用户没有 token——路由到 [账户创建和登录](#account-creation--sign-in)。
2. 在当前目录运行 `railway status --json`。
3. **如果已链接**：将服务添加到现有项目（`railway add --service <name>`）。除非用户明确说“新项目”或“独立项目”，否则不要创建新项目。
4. **如果未链接**：检查父目录（`cd .. && railway status --json`）。
   - **父已链接**：这很可能是一个单仓库子应用。添加服务并将 `rootDirectory` 设置为子应用路径。
   - **父未链接**：运行 `railway list --json` 并查找与目录名匹配的项目。
     - **找到匹配**：链接到它（`railway link --project <name>`）。
     - **未找到匹配**：创建新项目（`railway init --name <name>`）。
5. 当存在多个工作区时，从 `railway whoami --json` 中按名称匹配。

**命名启发式**：像 "flappy-bird" 或 "my-api" 这样的应用名称是服务名称，不是项目名称。使用目录或仓库名称作为项目。

## 响应格式

针对所有操作响应，应返回：
1. 执行了什么（行动和范围）。
2. 结果（ID、状态、关键输出）。
3. 下一步该做什么（或确认任务已完成）。

输出应保持简洁。仅在有助于用户理解发生了什么时，才包含命令证据。
