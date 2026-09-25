# 部署到 Render

Render 支持 **Git 驱动的** 服务和 **预构建的 Docker 镜像** 服务。

本技能涵盖 **Git 驱动的** 流程：
1. **蓝图方法** - 为基础设施即代码部署生成 render.yaml
2. **直接创建** - 通过 MCP 工具即时创建服务

蓝图也可以通过使用 `runtime: image` 来运行 **预构建的 Docker 镜像**，但 `render.yaml` 仍然必须存在于 Git 仓库中。

如果没有 Git 远程，请停止并要求用户执行以下操作：
- 创建/推送 Git 远程（如果只需要蓝图，可以最小化操作），或
- 使用 Render 控制台/API 部署预构建的 Docker 镜像（MCP 无法创建镜像驱动的服务）。

## 前置条件

- 当沙盒阻止部署网络调用时，使用 `sandbox_permissions=require_escalated` 重新运行。
- 部署可能需要几分钟时间。使用适当的超时值。

## 何时使用此技能

当用户希望执行以下操作时，激活此技能：
- 将应用程序部署到 Render
- 创建 render.yaml 蓝图文件
- 为他们的项目设置 Render 部署
- 在 Render 的云平台上托管或发布他们的应用程序
- 创建数据库、计划任务或其他 Render 资源

## 快速路径（新用户）

在使用深度分析之前，使用此简短的提示序列以减少摩擦：
1. 询问他们是否想从 Git 仓库或预构建的 Docker 镜像部署。
2. 询问 Render 是否应为其应用程序提供所有所需资源（根据用户描述的似乎可能的情况）或仅提供应用程序而他们自己提供基础设施。如果依赖关系不明确，请询问简短的后续问题以确认他们是否需要数据库、工作器、计划任务或其他服务。

然后继续执行下面的适当方法。

## 选择您的源路径

**Git 仓库路径**： 对蓝图和直接创建都必需。仓库必须推送到 GitHub、GitLab 或 Bitbucket。

**预构建的 Docker 镜像路径**： 通过镜像驱动的服务由 Render 支持。这 **不** 由 MCP 支持；使用控制台/API。请求：
- 镜像 URL（注册表 + 标签）
- 注册表认证（如果私有）
- 服务类型（web/worker）和端口

如果用户选择 Docker 镜像，请指导他们使用 Render 控制台镜像部署流程，或要求他们添加 Git 远程（以便您可以使用 `runtime: image` 的蓝图）。

## 选择您的部署方法（Git 仓库）

两种方法都需要将 Git 仓库推送到 GitHub、GitLab 或 Bitbucket。（如果使用 `runtime: image`，仓库可以最小化，仅包含 `render.yaml`。）

| 方法 | 最佳用途 | 优点 |
|------|----------|------|
| **蓝图** | 多服务应用程序、基础设施即代码工作流 | 版本控制、可重复、支持复杂设置 |
| **直接创建** | 单一服务、快速部署 | 即时创建、不需要 render.yaml 文件 |

### 方法选择启发式算法

默认情况下使用此决策规则，除非用户请求特定方法。首先分析代码库；如果部署意图不明确（例如，DB、工作器、计划任务），则询问。

**当所有以下条件都为真时，使用直接创建（MCP）**：
- 单一服务（一个 Web 应用程序或一个静态网站）
- 没有单独的工作器/计划任务服务
- 没有附加的数据库或 Key Value
- 仅简单的环境变量（没有共享环境组）

如果此路径适用且 MCP 尚未配置，请停止并指导 MCP 设置，然后再继续。

**当任何以下条件为真时，使用蓝图**：
- 多个服务（Web + 工作器、API + 前端等）
- 需要数据库、Redis/Key Value 或其他数据存储
- 计划任务、后台工作器或私有服务
- 您希望可重复的 IaC 或将 render.yaml 提交到仓库
- 单一仓库或多环境设置需要一致配置

如果不确定，请问一个快速澄清问题，但默认情况下使用蓝图以确保安全。对于单一服务，强烈建议通过 MCP 使用直接创建，并在需要时指导 MCP 设置。

## 前置条件检查

开始部署时，按顺序验证这些要求：

**1. 确认源路径（Git 与 Docker）**

如果使用基于 Git 的方法（蓝图或直接创建），仓库必须推送到 GitHub/GitLab/Bitbucket。引用预构建镜像的蓝图仍然需要一个包含 `render.yaml` 的 Git 仓库。

```bash
git remote -v
```

- 如果没有远程存在，请停止并要求用户创建/推送远程**或**切换到 Docker 镜像部署。

**2. 检查 MCP 工具可用性（对于单一服务首选）**

MCP 工具提供最佳体验。通过尝试以下操作来检查是否可用：
```
list_services()
```

如果 MCP 工具可用，您可以为大多数操作跳过 CLI 安装。

**3. 检查 Render CLI 安装（用于蓝图验证）**
```bash
render --version
```
如果未安装，请提供安装选项：
- macOS: `brew install render`
- Linux/macOS: `curl -fsSL https://raw.githubusercontent.com/render-oss/cli/main/bin/install.sh | sh`

**4. MCP 设置（如果 MCP 未配置）**

如果 `list_services()` 因 MCP 未配置而失败，请询问他们是否想设置 MCP（首选）或继续使用 CLI 回退。如果他们选择 MCP，请询问他们正在使用哪个 AI 工具，然后提供以下匹配的说明。始终使用他们的 API 密钥。

### Cursor

引导用户完成以下步骤：

1) 获取 Render API 密钥：
```
https://dashboard.render.com/u/*/settings#api-keys
```

2) 将此添加到 `~/.cursor/mcp.json`（替换 `<YOUR_API_KEY>`）：
```json
{
  "mcpServers": {
    "render": {
      "url": "https://mcp.render.com/mcp",
      "headers": {
        "Authorization": "Bearer <YOUR_API_KEY>"
      }
    }
  }
}
```

3) 重新启动 Cursor，然后重试 `list_services()`。

### Claude Code

引导用户完成以下步骤：

1) 获取 Render API 密钥：
```
https://dashboard.render.com/u/*/settings#api-keys
```

2) 使用 Claude Code 添加 MCP 服务器（替换 `<YOUR_API_KEY>`）：
```bash
claude mcp add --transport http render https://mcp.render.com/mcp --header "Authorization: Bearer <YOUR_API_KEY>"
```

3) 重新启动 Claude Code，然后重试 `list_services()`。

### Codex

引导用户完成以下步骤：

1) 获取 Render API 密钥：
```
https://dashboard.render.com/u/*/settings#api-keys
```

2) 在他们的 shell 中设置它：
```bash
export RENDER_API_KEY="<YOUR_API_KEY>"
```

3) 使用 Codex CLI 添加 MCP 服务器：
```bash
codex mcp add render --url https://mcp.render.com/mcp --bearer-token-env-var RENDER_API_KEY
```

4) 重新启动 Codex，然后重试 `list_services()`。

### 其他工具

如果用户使用其他 AI 应用，请指导他们查看该工具的 Render MCP 文档以获取设置步骤和安装方法。

### 工作区选择

配置 MCP 后，使用类似以下提示让用户设置活动的 Render 工作区：

```
将我的 Render 工作区设置为 [WORKSPACE_NAME]
```

**5. 检查认证（仅 CLI 回退）**

如果 MCP 不可用，请使用 CLI 并验证您是否可以访问您的帐户：
```bash
# 检查用户是否已登录（使用 -o json 以非交互模式）
render whoami -o json
```

如果 `render whoami` 失败或返回空数据，则 CLI 未经过认证。CLI 不一定会自动提示，因此明确提示用户进行认证：

如果两者都未配置，请询问用户他们更喜欢哪种方法：
- **API 密钥（CLI）**： `export RENDER_API_KEY="rnd_xxxxx"`（从 https://dashboard.render.com/u/*/settings#api-keys 获取）
- **登录**： `render login`（将打开浏览器进行 OAuth）

**6. 检查工作区上下文**

验证活动工作区：
```
get_selected_workspace()
```

或通过 CLI：
```bash
render workspace current -o json
```

要列出可用工作区：
```
list_workspaces()
```

如果用户需要切换工作区，他们必须通过控制台或 CLI (`render workspace set`) 完成。

一旦满足前置条件，即可继续部署工作流。

---

# 方法 1：蓝图部署（适用于复杂应用程序推荐）

## 蓝图工作流

### 第 1 步：分析代码库

分析代码库以确定框架/运行时、构建和启动命令、所需环境变量、数据存储和端口绑定。使用 [references/codebase-analysis.md](references/codebase-analysis.md) 中的详细检查清单。

### 第 2 步：生成 render.yaml

创建一个遵循蓝图规范的 `render.yaml` 蓝图文件。

完整规范：[references/blueprint-spec.md](references/blueprint-spec.md)

**要点：**
- 除非用户指定否则始终使用 `plan: free`
- 包含应用程序所需的所有环境变量
- 使用 `sync: false` 标记秘密（用户在控制台中填写这些内容）
- 使用适当的服务类型：`web`、`worker`、`cron`、`static` 或 `pserv`
- 使用适当的运行时：[references/runtimes.md](references/runtimes.md)

**基本结构：**
```yaml
services:
  - type: web
    name: my-app
    runtime: node
    plan: free
    buildCommand: npm ci
    startCommand: npm start
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: postgres
          property: connectionString
      - key: JWT_SECRET
        sync: false  # 用户在控制台中填写

databases:
  - name: postgres
    databaseName: myapp_db
    plan: free
```

**服务类型：**
- `web`：HTTP 服务、API、Web 应用程序（公开访问）
- `worker`：后台作业处理器（不公开访问）
- `cron`：按 cron 时间表运行的计划任务
- `static`：静态网站（通过 CDN 提供的 HTML/CSS/JS）
- `pserv`：私有服务（仅同一帐户内部可见）

服务类型详细信息：[references/service-types.md](references/service-types.md)
运行时选项：[references/runtimes.md](references/runtimes.md)
模板示例：[assets/](assets/)

### 第 2.5 步：立即下一步（始终提供）

创建 `render.yaml` 后，始终给用户一个简短的明确清单，并在 CLI 可用时立即运行验证：
1. **认证（CLI）**：运行 `render whoami -o json`（如果未登录，运行 `render login` 或设置 `RENDER_API_KEY`)
2. **验证（推荐）**：运行 `render blueprints validate`
   - 如果 CLI 未安装，请提供安装选项并提供命令。
3. **提交 + 推送**：`git add render.yaml && git commit -m "添加 Render 部署配置" && git push origin main`
4. **打开控制台**：使用蓝图深度链接，如果提示，则完成 Git OAuth
5. **填写秘密**：设置标记为 `sync: false` 的环境变量
6. **部署**：点击“应用”并监控部署

### 第 3 步：验证配置

在部署之前验证 `render.yaml` 文件以捕获错误。如果 CLI 已安装，请直接运行命令；如果 CLI 缺失，请提示用户：

```bash
render whoami -o json  # 确保 CLI 已认证（不会总是提示）
render blueprints validate
```

在继续之前修复任何验证错误。常见问题：
- 缺少必需字段（`name`、`type`、`runtime`）
- 无效的运行时值
- YAML 语法错误
- 无效的环境变量引用

配置指南：[references/configuration-guide.md](references/configuration-guide.md)

### 第 4 步：提交和推送

**重要提示**：在部署之前，您必须将 `render.yaml` 文件合并到您的仓库中。

确保 `render.yaml` 文件已提交并推送到您的 Git 远程：

```bash
git add render.yaml
git commit -m "添加 Render 部署配置"
git push origin main
```

如果还没有 Git 远程，请在此停止并指导用户创建 GitHub/GitLab/Bitbucket 仓库，将其作为 `origin` 添加，并推送后再继续。

**为什么这很重要**：控制台深度链接将从此仓库读取 `render.yaml`。如果文件未合并和推送，Render 将找不到配置，部署将失败。

在继续到下一步之前，请验证文件是否在您的远程仓库中。

### 第 5 步：生成深度链接

获取 Git 仓库 URL：

```bash
git remote get-url origin
```

这将返回来自您的 Git 提供商的 URL。**如果 URL 是 SSH 格式，请将其转换为 HTTPS**：

| SSH 格式 | HTTPS 格式 |
|----------|------------|
| `git@github.com:user/repo.git` | `https://github.com/user/repo` |
| `git@gitlab.com:user/repo.git` | `https://gitlab.com/user/repo` |
| `git@bitbucket.org:user/repo.git` | `https://bitbucket.org/user/repo` |

**转换模式**：将 `git@<host>:` 替换为 `https://<host>/` 并删除 `.git` 后缀。

使用 HTTPS 仓库 URL 格式化控制台深度链接：
```
https://dashboard.render.com/blueprint/new?repo=<REPOSITORY_URL>
```

示例：
```
https://dashboard.render.com/blueprint/new?repo=https://github.com/username/repo-name
```

### 第 6 步：指导用户

**关键**：确保用户在点击深度链接之前已将 `render.yaml` 文件合并并推送到他们的仓库中。如果文件不在仓库中，Render 无法读取蓝图配置，部署将失败。

向用户提供深度链接和以下说明：

1. **验证 render.yaml 已合并** - 确认文件存在于 GitHub/GitLab/Bitbucket 上的您的仓库中
2. 点击深度链接以打开 Render 控制台
3. 如果提示，完成 Git 提供商 OAuth
4. 为蓝图命名（或使用 render.yaml 中的默认值）
5. 填写标记为 `sync: false` 的秘密环境变量
6. 审查服务和数据库配置
7. 点击“应用”以部署

部署将自动开始。用户可以在 Render 控制台中监控进度。

### 第 7 步：验证部署

用户通过控制台部署后，验证一切是否正常工作。

**通过 MCP 检查部署状态**：
```
list_deploys(serviceId: "<service-id>", limit: 1)
```
查找 `status: "live"` 以确认成功部署。

**检查运行时错误（部署后 2-3 分钟）**：
```
list_logs(resource: ["<service-id>"], level: ["error"], limit: 20)
```

**检查服务健康指标**：
```
get_metrics(
  resourceId: "<service-id>",
  metricTypes: ["http_request_count", "cpu_usage", "memory_usage"]
)
```

如果发现错误，请继续到下面的 **部署后验证和基本故障排除** 部分。

---

# 方法 2：直接服务创建（快速单服务部署）

对于没有基础设施即代码的简单部署，通过 MCP 工具直接创建服务。

## 何时使用直接创建

- 单个 Web 服务或静态网站
- 快速原型或演示
- 当您不需要在仓库中包含 render.yaml 文件时
- 向现有项目添加数据库或计划任务

## 直接创建的前置条件

**仓库必须推送到 Git 提供商。** Render 克隆您的仓库以构建和部署服务。

```bash
git remote -v  # 验证远程是否存在
git push origin main  # 确保代码已推送
```

支持的提供者：GitHub、GitLab、Bitbucket

如果没有远程存在，请停止并要求用户创建/推送远程或切换到 Docker 镜像部署。

**注意**：MCP 不支持创建镜像驱动的服务。使用控制台/API 进行预构建 Docker 镜像部署。

## 直接创建工作流

使用以下简洁步骤，并参考 [references/direct-creation.md](references/direct-creation.md) 获取完整的 MCP 命令示例和后续配置。

### 第 1 步：分析代码库
使用 [references/codebase-analysis.md](references/codebase-analysis.md) 确定运行时、构建/启动命令、环境变量和数据存储。

### 第 2 步：通过 MCP 创建资源
创建服务（Web 或静态）以及任何所需的数据库或 Key Value 存储库。参见 [references/direct-creation.md](references/direct-creation.md)。

如果 MCP 返回关于缺少 Git 凭据或仓库访问的错误，请停止并指导用户在 Render 控制台中连接他们的 Git 提供商，然后重试。

### 第 3 步：配置环境变量
创建后通过 MCP 添加所需环境变量。参见 [references/direct-creation.md](references/direct-creation.md)。

提醒用户如果他们不想通过 MCP 传递秘密，可以在控制台中设置它们。

### 第 4 步：验证部署
检查部署状态、日志和指标。参见 [references/direct-creation.md](references/direct-creation.md)。

---

对于服务发现、配置详细信息、快速命令和常见问题，请参阅 [references/deployment-details.md](references/deployment-details.md)。

---

# 部署后验证和基本故障排除（所有方法）

保持简短和可重复。如果任何检查失败，请在重新部署之前修复它。

1. 确认最新的部署是 `live` 并正在服务流量
2. 访问健康端点（或根）并验证 200 响应
3. 扫描最近的错误日志以查找明显的失败特征
4. 验证所需环境变量和端口绑定（`0.0.0.0:$PORT`）

详细清单和命令：[references/post-deploy-checks.md](references/post-deploy-checks.md)

如果服务无法启动或健康检查超时，请使用基本故障排除指南：
[references/troubleshooting-basics.md](references/troubleshooting-basics.md)

## 故障排除

### 升级网络访问

如果由于网络问题（超时、DNS 错误、连接重置）部署失败，请使用 `sandbox_permissions=require_escalated` 重新运行部署以获得升级权限。当沙盒网络阻止出站请求时，部署需要升级网络访问。

向用户提供的示例指导：

```
部署需要升级网络访问才能部署到 Render。我可以使用升级权限重新运行命令——您要我继续吗？
```

可选：如果您需要更深入的诊断（指标/DB 检查/错误目录），建议安装 `render-debug` 技能。它不是核心部署流程所必需的。
