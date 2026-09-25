# Gemini Enterprise 注册

> **要求：** 需要部署代理。对于 Agent Runtime，`deployment_metadata.json`（由 `agents-cli deploy` 创建）启用自动检测。对于 Cloud Run 或 GKE，直接提供代理卡 URL 和标志。

## 前置条件

1. **代理必须已部署** — 代理必须正在运行且可访问
2. **Gemini Enterprise 应用必须存在** — 在 Google Cloud Console → Gemini Enterprise → 应用中创建一个，然后才能注册
3. **`deployment_metadata.json`**（仅限 Agent Runtime）— 由 `agents-cli deploy` 自动创建；包含代理运行时 ID、部署目标、A2A 标志和代理目录
4. **文本代理** — Live/语音（双向）代理不受 Gemini Enterprise 支持，因为 Gemini Enterprise 没有 `/run_live` 传输。注册一个文本代理。

## Cloud Run 上的 A2A 所需权限

- **`roles/run.servicesInvoker`** 授予 Discovery Engine 服务帐户（`service-<PROJECT_NUMBER>@gcp-sa-discoveryengine.iam.gserviceaccount.com`）在 Cloud Run 服务上。

---

## 注册模式

### A2A 注册

每个脚手架代理都提供 Agent-to-Agent 协议。A2A 是默认的 — 且仅有的 — 注册类型在 **Cloud Run** 和 **GKE** 上（没有本地调用推理引擎）。它也适用于 **Agent Runtime** 通过 `--registration-type a2a`。对于 ADK 代理，CLI 会警告它，因为 Gemini Enterprise 可以通过 `:streamQuery` 本地调用 Agent Runtime — 在这种情况下，请优先选择 ADK 注册。对于基于其他框架构建的代理，没有可本地调用的 ADK 应用，因此 A2A 是每个目标上的正确模式，警告是预期的。传递代理卡 URL，命令会获取卡并注册它；显示名称和描述默认为卡的 `name`/`description`。

```bash
# Cloud Run / GKE 上的 A2A。卡路径取决于项目的语言：
#   Python -> /a2a/{app_name}/.well-known/agent-card.json
#   Go     -> /.well-known/agent-card.json
agents-cli publish gemini-enterprise \
  --agent-card-url https://my-service-abc123.us-east1.run.app/a2a/app/.well-known/agent-card.json \
  --gemini-enterprise-app-id projects/123456/locations/global/collections/default_collection/engines/my-app
```

传递 `--display-name` / `--description` 以覆盖卡默认值。在 Agent Runtime 上，如果省略 `--agent-card-url`，卡 URL 会自动从 `deployment_metadata.json` 构建。

### ADK 注册（Agent Runtime 上的默认注册）

> **仅限 ADK 项目。** 代理必须作为 ADK 应用部署到 Agent Runtime，因为注册通过 `:streamQuery` 调用它。其他框架上的代理通过 A2A 注册，因此将其部署到 Cloud Run 或 GKE 并从那里发布。

这是 **Agent Runtime 上 ADK 代理的默认和推荐注册方式**：Gemini Enterprise 通过其推理引擎资源上的 `:streamQuery` 本地调用代理，进行端到端身份验证。在底层，`:streamQuery` 分发到 `AdkApp` 的 `streaming_agent_run_with_events` 方法 — 在调试 ADK 调用时，搜索运行时 `reasoning_engine_stderr` 日志中的该方法名称以跟踪失败。当代理需要 OAuth 身份验证 (`--authorization-id`) 时，也使用此路径。代理直接通过其推理引擎资源名称注册；不需要代理卡 URL。

```bash
agents-cli publish gemini-enterprise \
  --registration-type adk \
  --agent-runtime-id projects/123456/locations/us-east1/reasoningEngines/789 \
  --gemini-enterprise-app-id projects/123456/locations/global/collections/default_collection/engines/my-app \
  --display-name "My Agent" \
  --description "Handles customer queries" \
  --tool-description "Answers questions about products"
```

---

## 程序化模式（CI/CD）

命令默认非交互式 — 通过标志或环境变量传递所有必需值。这使得它适用于 CI/CD 管道。

### 通过标志

```bash
agents-cli publish gemini-enterprise \
  --agent-runtime-id "$AGENT_RUNTIME_ID" \
  --gemini-enterprise-app-id "$GEMINI_ENTERPRISE_APP_ID" \
  --display-name "Production Agent" \
  --registration-type adk
```

### 通过环境变量

大多数标志都有环境变量替代方案（`--metadata-file`、`--interactive` 和 `--list` 不适用）：

```bash
export AGENT_RUNTIME_ID="projects/123456/locations/us-east1/reasoningEngines/789"
export GEMINI_ENTERPRISE_APP_ID="projects/123456/locations/global/collections/default_collection/engines/my-app"
export GEMINI_DISPLAY_NAME="Production Agent"
export GEMINI_DESCRIPTION="Handles customer queries"

agents-cli publish gemini-enterprise
```

---

## 交互模式 (`--interactive`)

传递 `--interactive`（或 `-i`）以通过交互提示引导缺失值。命令将列出可用的 Gemini Enterprise 应用，提供从元数据自动检测代理运行时 ID，并提示输入显示名称和描述。

```bash
agents-cli publish gemini-enterprise --interactive
```

---

## 完整标志参考

| 标志 | 环境变量 | 描述 |
|------|---------|-------------|
| `--agent-runtime-id` | `AGENT_RUNTIME_ID` | Agent Runtime 资源名称（从 `deployment_metadata.json` 自动检测） |
| `--gemini-enterprise-app-id` | `ID` 或 `GEMINI_ENTERPRISE_APP_ID` | Gemini Enterprise 应用完整资源名称 |
| `--display-name` | `GEMINI_DISPLAY_NAME` | Gemini Enterprise 中的显示名称 |
| `--description` | `GEMINI_DESCRIPTION` | 代理描述 |
| `--tool-description` | `GEMINI_TOOL_DESCRIPTION` | 工具描述（仅限 ADK 模式，默认为描述） |
| `--registration-type` | `REGISTRATION_TYPE` | `adk` 或 `a2a`（ADK 代理在 Agent Runtime 上默认为 `adk`，其他地方包括任何非 ADK 框架默认为 `a2a`） |
| `--agent-card-url` | `AGENT_CARD_URL` | A2A 注册的代理卡 URL |
| `--deployment-target` | `DEPLOYMENT_TARGET` | `agent_runtime`、`cloud_run` 或 `gke`（设置默认注册类型 — Agent Runtime 上的 ADK，Cloud Run / GKE 上的 A2A — 以及 A2A 身份验证方法） |
| `--project-id` | `GOOGLE_CLOUD_PROJECT` | 用于计费的 GCP 项目 ID |
| `--project-number` | `PROJECT_NUMBER` | 用于 Gemini Enterprise 查找的 GCP 项目编号 |
| `--authorization-id` | `GEMINI_AUTHORIZATION_ID` | OAuth 身份验证资源名称 |
| `--metadata-file` | — | 部署元数据路径（默认：`deployment_metadata.json`） |
| `--interactive` / `-i` | — | 启用交互提示 |
| `--list` | — | 列出当前项目中的 Gemini Enterprise 应用并退出 |

---

## 从元数据自动检测

当存在 `deployment_metadata.json` 时，命令自动：

- 读取 **代理运行时 ID** (`remote_agent_runtime_id`)
- 确定 **注册类型**：默认为 **ADK**（本地 `:streamQuery`）在 **Agent Runtime** 上，以及在 **Cloud Run / GKE** 上为 **A2A**（它们没有推理引擎）。使用其他框架构建的项目没有 ADK 应用，因此它在每个目标上默认为 **A2A**。使用 `--registration-type` 覆盖。
- 确定 **部署目标** 用于身份验证

这意味着对于最简单的情况（Agent Runtime 上的 ADK 代理，以 ADK 注册），您只需要提供 Gemini Enterprise 应用 ID：

```bash
agents-cli publish gemini-enterprise \
  --gemini-enterprise-app-id projects/123456/locations/global/collections/default_collection/engines/my-app
```

---

## SDK 兼容性（仅限 Python）

Agent Runtime 部署可能会遇到 `google-cloud-aiplatform` 版本 <= 1.128.0 的 "Session not found" 错误。在交互模式 (`--interactive`) 中，命令会从 `uv.lock` 检查 SDK 版本并建议升级。在程序化模式中，确保在注册前更新 SDK。

---

## 代理注册（代理和 MCP 服务器）

代理注册（预览版）是 Google Cloud 全局的代理和 MCP 服务器目录，与 Gemini Enterprise 应用分离。
部署到托管运行时（Gemini Enterprise Agent Platform 上的 Agent Runtime）的代理会 **自动注册** — `agents-cli deploy` 后无需额外步骤。
使用 `gcloud` 管理（需要 `roles/agentregistry.editor`）：

```bash
# 列出/检查代理
gcloud agent-registry agents list --project PROJECT --location LOCATION
gcloud agent-registry agents describe AGENT_NAME

# 更新端点/元数据 — 编辑 Service 资源，而不是代理
gcloud agent-registry services update AGENT_NAME \
  --display-name "..." --description "..." \
  --interfaces "url=ENDPOINT_URL,protocolBinding=http-json"

# 注册外部 MCP 服务器：不会自动自省，因此上传一个
# toolspec.json（其 tools/list 响应，最大 10 KB）。没有 us/eu 多区域。
gcloud agent-registry services create SERVER_NAME --location=LOCATION \
  --mcp-server-spec-type=tool-spec --mcp-server-spec-content=toolspec.json \
  --interfaces="url=SERVER_URL,protocolBinding=jsonrpc"  # 或 http-json, grpc

# 删除：删除底层运行时代理（自动注册）OR，对于手动注册的代理/服务器，删除 Service 资源
gcloud agent-registry services delete NAME
```

Terraform: `google_agent_registry_service` 与 `mcp_server_spec` 块。

文档：https://docs.cloud.google.com/agent-registry/manage-agents · https://docs.cloud.google.com/agent-registry/register-mcp-servers

---

## 故障排除

| 问题 | 解决方案 |
|-------|----------|
| 注册后 "Session not found" | SDK 版本问题 — 升级 `google-cloud-aiplatform`（见上述 SDK 兼容性），重新部署，然后重新注册 |
| `--registration-type is required` | 非交互模式下需要 `--registration-type`，当不存在 `deployment_metadata.json` 时 |
| "Gemini Enterprise App ID is required" | 提供 `--gemini-enterprise-app-id` 或设置 `ID` / `GEMINI_ENTERPRISE_APP_ID` 环境变量 |
| 重新发布相同代理 | 注册是幂等的 — 重新运行会就地更新现有注册，而不是创建重复项 |
| 注册时 HTTP 403 | 确保您的帐户在 Gemini Enterprise 项目上具有 Discovery Engine 编辑权限 |
| Agent Runtime 上 ADK 调用失败的调试 | Gemini Enterprise 通过 `AdkApp` 的 `streaming_agent_run_with_events` 方法（本地的 `:streamQuery` 合同）调用代理。搜索运行时 `reasoning_engine_stderr` 日志中的 `streaming_agent_run_with_events` 以找到底层错误 |
| "Could not fetch agent card" | 验证代理正在运行且 URL 正确；对于 Cloud Run，确保 `gcloud auth login` 已执行。Live/语音代理会丢弃其 A2A 卡且无法发布 — Gemini Enterprise 不支持 Live 代理 |

---

## 相关技能

- `/google-agents-cli-deploy` — 部署目标、CI/CD 管道和生产工作流（也涵盖 Agent Gateway 管理的入站/出站和语义治理意识）
- `/google-agents-cli-workflow` — 开发工作流、编码规范和操作规则
- `/google-agents-cli-scaffold` — 使用 `agents-cli scaffold create` / `scaffold enhance` 创建和增强项目
