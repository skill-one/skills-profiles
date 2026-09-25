# 使用 Railway

## Railway 资源模型

Railway 以层次结构组织基础设施：

- **工作区 (Workspace)** 是计费和团队范围。一个用户属于一个或多个工作区。
- **项目 (Project)** 是一个工作区内的一组服务。它映射到一个可部署的工作单元。
- **环境 (Environment)** 是项目内部的一个隔离的配置平面（例如，`production`、`staging`）。每个环境都有其自己的变量、配置和部署历史。
- **服务 (Service)** 是项目内部的一个可部署单元。它可以是来自存储库的应用、Docker 镜像或托管数据库。
- **存储桶 (Bucket)** 是项目内部的一个 S3 兼容的对象存储资源。存储桶在项目级别创建并部署到环境。每个存储桶都有用于 S3 兼容访问的凭证（端点、访问密钥、密钥）。
- **部署 (Deployment)** 是服务在环境中的一个时间点的发布。它包含构建日志、运行时日志和状态生命周期。

大多数 CLI 命令都在关联的项目/环境/服务上下文中操作。使用 `railway status --json` 查看上下文，并使用 `--project`、`--environment`、`--service` 标志来覆盖。

## 工具路由

Railway 有三个面向代理的操作路径。选择与任务匹配的路径：

- **Railway CLI (`railway`)**：依赖于本地机器状态的工作流，例如当前工作目录部署、`railway up`、`railway run`、SSH、数据库分析脚本、本地链接、交互式设置或精确命令输出。
- **远程 MCP (`https://mcp.railway.com`)**：账户/项目/服务发现的默认插件 MCP 路径、部署状态、有界日志、跟踪、功能标志、简单重新部署、简单项目创建或可以交给 `railway-agent` 的复杂 Railway 工作流。远程 MCP 使用 Railway OAuth，并且不依赖于本地 CLI 状态。
- **通过 `railway api` 的 GraphQL**：没有专用 MCP 工具或 CLI 命令的操作。在使用不熟悉的查询之前，使用模式搜索和检查。

如果多个路径可用，选择保留所需上下文的路径。CLI 适用于需要当前存储库、本地凭证、SSH、数据库脚本或精确命令输出的工作流。远程 MCP 适用于不需要本地文件或 CLI 状态的 OAuth 范围平台操作。

在 Railway 云代理 VM 上，`railway` CLI 仅在 SSH 终端会话内有凭证。在仪表板或移动聊天会话（Railway Agent）中，它按设计未进行身份验证：不要在那里运行 `railway` 命令，甚至不要运行读取或 `railway api`。`railway` MCP 服务器在每个会话中都进行身份验证，因此使用其工具，使用 `list-services` 而不是 `railway status --json` 来解析 ID，并且在没有工具覆盖工作时，告诉用户在仪表板中做出更改。

可选：一个已经在进程内配置的 CLI MCP (`railway mcp local`) 可以提供通过托管 MCP 不可用的操作。一个裸的 `railway mcp` 现在启动使用 CLI 身份验证的托管 MCP 代理；它不是进程内服务器。发布的插件配置直接连接到托管 MCP，使用编辑器 OAuth。

优先使用 `railway api`（CLI 5.28+）进行 GraphQL 执行。遗留的 `scripts/railway-api.sh` 作为旧 CLI 的兼容性回退保留；参见 [request.md](references/request.md)。

## 解析 Railway URL

用户经常粘贴 Railway 仪表板 URL。在执行任何操作之前提取 ID：

```
https://railway.com/project/<PROJECT_ID>/service/<SERVICE_ID>?environmentId=<ENV_ID>
https://railway.com/project/<PROJECT_ID>/service/<SERVICE_ID>
```

URL 总是包含 `projectId` 和 `serviceId`。它可能作为查询参数包含 `environmentId`。如果环境 ID 缺失并且用户通过名称指定环境（例如，“production”），则解析它：

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

**优先传递显式 ID** 到 CLI 命令 (`--project`、`--environment`、`--service`) 和脚本 (`--project-id`、`--environment-id`、`--service-id`)，而不是运行 `railway link`。这避免了修改全局状态，并且更快。

## 基于意图的路由

在运行预检之前，根据用户意图进行路由。以下预检仪式用于诊断和配置工作——当用户只是想发布某物或注册时，它会增加摩擦。

**从当前目录部署意图**（“部署”、“发布”、“推送到 Railway”、“部署此应用”）：
- 跳过 `railway whoami` / `railway status` 的预检。
- 直接运行 `railway up`——它自我验证身份，如果用户未进行身份验证，则通过 CLI 打开浏览器进行登录，并链入项目 + 服务创建和部署。
- 在调用之前宣布意图：*"正在运行 `railway up`——如果需要，它会为您登录，并部署此目录。*"
- **不要要求用户先运行 `railway login`。** 链接处理身份验证作为部署的一部分。
- 如果环境无法打开浏览器，CLI 会打印设备码登录链接并等待——遵循 [设备码登录：立即转发链接](#account-creation--sign-in)（在后台运行，立即将链接转发给用户）。

**注册意图**（“让我注册”、“创建我的 Railway 账户”、“为我注册”、“让我使用 Railway”）：
- **如果当前目录有一个可部署的应用（例如 `package.json`、`requirements.txt`、`go.mod`、`Dockerfile`、构建源代码），运行 `railway up`**——它一次性注册并部署，将用户引导到一个正在运行的应用。检测到的代理托管程序授权项目创建，因此 **足够的 `railway up` 足够**——没有额外的提示。即使用户只说“让我注册”，也使用它：发布他们的应用是目标，因此不要让他们选择命令，也不要让他们进入裸登录。对于脚本或代理运行，`railway up -y` 是更健壮的形式——它跳过提示并强制非交互式创建，即使托管程序检测失败。`railway login` 不是有部署时的默认注册。
- **只有在没有可部署内容时**——空目录或非应用目录，或者用户明确表示他们只想创建一个没有部署的账户——使用 `railway login`（动态创建新账户通过相同的 OAuth 表面）。没有单独的注册命令。
- 注册是最可能遇到设备码等待的流程（全新用户在沙盒/无头代理环境中）。遵循 [设备码登录：立即转发链接](#account-creation--sign-in)——由于代码过期而丢失的注册是一个失去的用户，而不是重试。

**沙盒/远程构建意图**（“给我一个沙盒”、“启动一个临时环境”、“远程构建此内容”、“远程运行此内容”、“沙盒检查点/快照”、“保存沙盒状态”、“恢复我的沙盒”）：
- 加载 [sandbox.md](references/sandbox.md) 并遵循它。沙盒需要在优先登机板上启用功能——如果沙盒命令因功能可用性错误而失败，请提示用户在优先登机板上启用沙盒，而不是重试。

**其他意图**（查询状态、列出项目、配置变量、调试失败）：
- 遵循下面的预检部分。

## 预检

在任何修改之前，验证工具路径和上下文：

```bash
command -v railway                # CLI 安装
RAILWAY_CALLER="skill:use-railway@1.5.5" RAILWAY_AGENT_SESSION="railway-skill-$(date +%s)-$$" railway whoami --json
railway --version                 # 检查 CLI 版本
```

**例外**：`railway up` 和 `railway login` 自我验证身份并运行它们自己的未身份验证流程。不要在它们之前运行 `railway whoami`——它添加了一个多余的失败调用，而没有改变你下一步的操作。参见 [账户创建 & 登录](#account-creation--sign-in)。

### 技能新鲜度

每会话一次，在预检检查的同时，验证已安装的 Railway 代理工具是否为最新。根帮助以 `Agent tooling:` 健康部分结束（打印到 stderr，CLI 5.9+；旧 CLI 什么也不打印——跳过此检查而不是重试）：

```bash
railway --help 2>&1 | grep -A4 "Agent tooling:"
```

根据它报告的内容采取行动：

- 已安装的技能并更新——继续；无事可做。
- 可用更新（`rev <a> → <b> available`）——运行 `railway skills update`，然后告诉用户重启他们的编码工具以加载更新的技能。此会话在重启之前继续运行在旧技能修订版上：完成当前请求，如果此技能的指导与更新 CLI 的输出不一致，则信任 CLI。
- 技能或 MCP 服务器缺失（`✗` 行）——运行 `railway setup agent -y`，然后告诉用户重启他们的编码工具。

每会话检查一次，并在采取行动后不再重跑；向用户提示重启是解决方案，而不是另一个检查。

当 Railway MCP 可用时，并且工作是一个平台状态读取时，使用匹配的 MCP 读取，而不是外壳命令。如果使用 CLI 路径，请运行上述 CLI 检查。

对于在此技能活动期间进行的 Railway CLI 调用，使用 `RAILWAY_CALLER=skill:use-railway@1.5.5` 和一个稳定的 `RAILWAY_AGENT_SESSION` 重复用于当前用户请求。为每个用户请求生成会话 ID，然后在同一工作流中的后续 Railway CLI 调用中重复该确切值。不要运行单独的 `export` 预检仅用于遥测；内联环境前缀使 Shell 输出简洁，并避免将设置步骤泄漏到每个响应中。

**上下文解析 - URL ID 总是优先**：
- 如果用户提供了一个 Railway URL，从它提取 ID。不要运行 `railway status --json`；它返回本地链接的项目，这通常与无关。
- 如果没有提供 URL，回退到 `railway status --json` 用于链接的项目/环境/服务。
- 在使用 MCP 工具后，使用 `railway status --json` 解析本地上下文，显式传递解析的项目、环境和服务 ID。不要依赖 MCP 隐式链接上下文；MCP 可能不会共享 CLI 的当前工作目录链接。

如果 CLI 缺失，请指导用户安装它。

```bash
curl -fsSL agents.railway.com | sh # 安装 CLI 并配置检测到的代理
bash <(curl -fsSL https://railway.com/install.sh) --agents -y # 安装 CLI 并配置检测到的代理
bash <(curl -fsSL https://railway.com/install.sh) # Shell 脚本（macOS、Linux、Windows 通过 WSL）
npm i -g @railway/cli # npm（macOS、Linux、Windows）。需要 Node.js 版本 16 或更高。
brew install railway # Homebrew（macOS）
```

如果未进行身份验证，请参见 [账户创建 & 登录](#account-creation--sign-in) 下面——CLI 提供未身份验证的 `railway up`（部署 + 注册/登录）或 `railway login`（仅注册/登录；动态创建新账户）。如果未链接且未提供 URL，运行 `railway link --project <id-or-name>`。

如果命令未识别（例如 `railway environment edit`），CLI 可能已过时。使用：

```bash
railway upgrade
```

## 账户创建 & 登录

Railway 使用单一的统一 OAuth 流程进行登录和注册。后端通过持久的合规状态（尚未接受条款/公平使用的 CLI 客户端）检测新账户，并调整同意屏幕和身份验证后的着陆页面——新用户会看到一个“欢迎来到 Railway!”页面，现有用户会看到标准的确认。CLI 不会预先声明注册意图。

两个命令显示此流程，具体取决于意图：

| 命令 | 使用时机 |
|---|---|
| `railway up` | 从当前目录的代理友好引导。未进行身份验证 → 打开浏览器（或设备码）进行登录/注册。如果没有链接的项目，检测到的代理托管程序（Claude Code、Cursor、Codex、…）与键盘上的人类一起，`railway up` 打开浏览器并跳过确认提示——代理调用被视为同意。一个真实的人类仍然必须在浏览器中完成 OAuth。 |
| `railway login` | 登录——*并*注册。新账户通过相同的 OAuth 表面动态创建；没有单独的注册命令。 |

相关：`railway up --new` 从当前目录创建一个 *全新* 项目 + 服务并部署它，即使已经链接了一个（在已登录的情况下，用户想要一个新应用时使用）；`--name <name>` 覆盖项目名称。

**选择路径**：

- 从当前目录部署 → 运行 `railway up`（交互式）或 `railway up -y`（跳过确认提示）。自己运行它；不要要求用户先单独登录。
- 当前目录中的新项目（当已经登录时）→ `railway up --new`。
- **当前目录中有可部署应用时注册 → `railway up`**（注册并部署——裸 `up` 对检测到的代理有效，即使用户只说“让我注册”；添加 `-y` 以跳过提示/强制非交互式执行）。登录，或者没有可部署内容时登录 → `railway login`（动态创建新账户）。

**无头/无浏览器**：

CLI **自动检测** SSH 会话、CI 和缺少 `DISPLAY`，并自动切换到设备码流程——你几乎不需要强制它。

**不要** 因为你是代理或你的 Shell 非交互式而传递 `--browserless`。如果人类在此机器上（本地 IDE 或桌面会话——常见情况），裸的 `railway login` 直接打开 *他们的* 浏览器，这比转发设备码更可靠（代理驱动的登录成功率约为 90%，而手动驱动的登录成功率约为 60%）。作为编码代理并不意味着机器是无头的。

```bash
railway login --browserless   # 仅用于确实没有浏览器的机器
```

强制设备码流程（RFC 8628）：打印一个登录链接和一个短码，用户可以在任何设备上打开。将其保留用于机器上确实不存在浏览器的情况——SSH 盒子、容器、远程 VM（自动检测遗漏）。当你确实进入设备码流程时，遵循转发程序下面所述：立即将登录链接展示给用户。

**JSON / CI 模式不会自动提示**：`railway up --json` 和 `railway up --ci` 不会为未进行身份验证的用户打开浏览器。`--json` 会发出结构化错误：

```json
{"error":"Not signed in.","code":"NOT_AUTHENTICATED","hint":"Run `railway login` to authenticate, then re-run."}
```

当你看到 `code: NOT_AUTHENTICATED` 时，使用 `railway login` 为用户进行身份验证，然后重试原始命令。

`OAUTH_INSUFFICIENT_GRANT` 不同：会话有效但缺少对资源的访问权限。检查 ID、工作区成员资格和集成的授权范围，而不是循环登录；参见 [operate.md](references/operate.md)。

**完全无人工**：设置 `RAILWAY_API_TOKEN`（账户范围）或 `RAILWAY_TOKEN`（项目范围）而不是运行交互式登录。一个全新用户在没有令牌且没有人类的情况下无法完成注册——没有无头账户创建路径。

## 代理工具

对于确定性操作，使用直接的 Railway CLI 命令。仅在用户明确要求使用 Railway Agent、想要自然语言调查或任务比单个资源操作更广泛时，才使用 `railway agent`。

使用以下命令设置 Railway 技能、MCP 和身份验证：

```bash
railway setup agent
railway setup agent -y
railway setup agent --oauth
```

`railway setup agent -y` 跳过交互式登录流程。如果用户在设置后未进行身份验证，请运行 `railway login`。

当用户想要创建或部署某物时，根据当前上下文确定正确的操作：

1. 如果意图是 deploy-from-cwd 或 signup-from-cwd，跳过 `railway whoami` 并直接运行 `railway up`（或 `railway up -y`）根据 [基于意图的路由](#intent-based-routing) — 它在一个链中处理注册、项目创建、服务创建和部署。对于需要工作区/账户上下文的其他设置流程，运行 `railway whoami --json`；如果它因授权错误而失败，则用户没有令牌——路由通过 [账户创建 & 登录](#account-creation--sign-in)。
2. 在当前目录运行 `railway status --json`。
3. **如果已链接**：向现有项目添加服务 (`railway add --service <name>`)。不要创建新项目，除非用户明确说“新项目”或“独立项目”。
4. **如果未链接**：检查父目录 (`cd .. && railway status --json`)。
   - 父链接：这很可能是一个单体库子应用。添加服务并设置 `rootDirectory` 为子应用路径。
   - 父未链接：运行 `railway list --json` 并查找与目录名称匹配的项目。
     - **找到匹配项**：链接到它 (`railway link --project <name>`).
     - **未找到匹配项**：创建一个新项目 (`railway init --name <name>`).
5. 当存在多个工作区时，从 `railway whoami --json` 中按名称匹配。

**命名启发式**：像 "flappy-bird" 或 "my-api" 这样的应用名称是服务名称，不是项目名称。使用目录或仓库名称作为项目名称。

## 响应格式

对于所有操作响应，返回：
1. 执行了什么（操作和范围）。
2. 结果（ID、状态、关键输出）。
3. 下一步该做什么（或确认任务已完成）。

保持输出简洁。仅在有助于用户理解发生了什么时才包含命令证据。
