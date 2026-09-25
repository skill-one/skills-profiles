# ADK 项目脚手架指南

使用 `agent-starter-pack` CLI（通过 `uvx`）创建新的 ADK 代理项目，或通过部署、CI/CD 和基础设施脚手架增强现有项目。

---

## 第 1 步：收集需求

从用例开始，根据回答进行后续提问。

**始终询问：**

1. **代理将解决什么问题？** — 核心目的和能力
2. **需要哪些外部 API 或数据源？** — 工具、集成、认证需求
3. **安全限制？** — 代理必须不做什么，安全护栏
4. **部署偏好？** — 先原型（推荐）还是完整部署？如果部署：Agent Engine、Cloud Run 或 GKE？

**根据上下文提问：**

- 如果提到**对数据进行检索或搜索**（RAG、语义搜索、向量搜索、嵌入、相似度搜索、数据摄取）→ **数据存储？** 使用 `--agent agentic_rag --datastore <选择>`：
  - `vertex_ai_vector_search` — 用于嵌入、相似度搜索、向量搜索
  - `vertex_ai_search` — 用于文档搜索、搜索引擎
- 如果代理需要**对其他代理可用** → **A2A 协议？** 使用 `--agent adk_a2a` 将代理作为兼容 A2A 的服务公开。
- 如果选择**完整部署** → **CI/CD 运行器？** GitHub Actions（默认）或 Google Cloud Build？
- 如果选择 **Cloud Run** 或 **GKE** → **会话存储？** 内存（默认）、Cloud SQL（持久化）或 Agent Engine（托管）。
- 如果选择**带 CI/CD 的部署** → **Git 仓库？** 是否已存在，或应创建一个？如果创建，公共还是私有？

---

## 第 2 步：编写 DESIGN_SPEC.md

编写**详细**的规范，包含以下部分。在脚手架之前向用户展示完整规范以供批准。

```markdown
# DESIGN_SPEC.md

## 概述
2-3 段话描述代理的目的及其工作原理。

## 示例用例
3-5 个具体示例，包括预期输入和输出。

## 所需工具
每个工具的用途、API 细节和认证需求。

## 限制与安全规则
具体规则 — 不仅仅是通用声明。

## 成功标准
可衡量的评估结果。

## 需处理的边缘情况
至少 3-5 个代理必须优雅处理的场景。
```

规范应足够详细，以便另一位开发者无需额外上下文即可实现代理。

---

## 第 3 步：创建或增强项目

### 创建新项目

```bash
uvx agent-starter-pack create <项目名> \
  --agent <模板> \
  --deployment-target <目标> \
  --region <区域> \
  --prototype \
  -y
```

**限制：**
- 项目名必须**26 个字符或更短**，仅包含小写字母、数字和连字符。
- 在运行 `create` 之前**不要 `mkdir` 项目目录** — CLI 会自动创建它。如果先 `mkdir`，`create` 会失败或表现异常。
- 根据 IDE 自动检测指导文件名，并相应地传递 `--agent-guidance-filename`。
- 增强现有项目时，检查代理代码的位置。如果不在 `app/` 中，请传递 `--agent-directory <目录>`（例如 `--agent-directory agent`）。如果设置错误，增强会遗漏或错误放置文件。

#### 创建标志

| 标志 | 简写 | 默认 | 描述 |
|------|-------|---------|-------------|
| `--agent` | `-a` | `adk` | 代理模板（见下表中的模板） |
| `--deployment-target` | `-d` | `agent_engine` | 部署目标 (`agent_engine`, `cloud_run`, `gke`, `none`) |
| `--region` | | `us-central1` | GCP 区域 |
| `--prototype` | `-p` | off | 跳过 CI/CD 和 Terraform（推荐用于初步尝试） |
| `--cicd-runner` | | `skip` | `github_actions` 或 `google_cloud_build` |
| `--datastore` | `-ds` | — | 数据摄取的数据存储 (`vertex_ai_search`, `vertex_ai_vector_search`) |
| `--session-type` | | `in_memory` | 会话存储 (`in_memory`, `cloud_sql`, `agent_engine`) |
| `--auto-approve` | `-y` | off | 跳过确认提示 |
| `--skip-checks` | `-s` | off | 跳过 GCP/Vertex AI 验证检查 |
| `--agent-directory` | `-dir` | `app` | 代理代码目录名 |
| `--agent-guidance-filename` | | `GEMINI.md` | 指导文件名 (`CLAUDE.md`, `AGENTS.md`) |
| `--debug` | | off | 启用调试日志以进行故障排除 |

默认情况下，脚手架的项目使用 Google Cloud 凭证（Vertex AI）。有关 API 密钥设置和模型配置，请参阅 [配置 Gemini 模型](https://adk.dev/agents/models/google-gemini/index.md) 和 [支持的模型](https://adk.dev/agents/models/index.md)。

### 增强现有项目

```bash
uvx agent-starter-pack enhance . \
  --deployment-target <目标> \
  -y
```

在项目目录内运行此命令（或传递路径代替 `.`）。记住，增强会创建新文件（`.github/`、`deployment/`、`tests/load_test/` 等），需要提交。

#### 增强标志

所有创建标志都受支持，此外还有：

| 标志 | 简写 | 默认 | 描述 |
|------|-------|---------|-------------|
| `--name` | `-n` | 目录名 | 用于模板的项目名 |
| `--base-template` | `-bt` | — | 覆盖基础模板（例如 `agentic_rag` 添加 RAG） |
| `--dry-run` | | off | 预览更改而不应用 |
| `--force` | | off | 强制覆盖所有文件（跳过智能合并） |

### 常见工作流

**在运行这些命令之前始终询问用户。** 展示选项（CI/CD 运行器、部署目标等），并在执行前确认。

```bash
# 为现有原型添加部署
uvx agent-starter-pack enhance . --deployment-target agent_engine -y

# 添加 CI/CD 管道（询问：GitHub Actions 或 Cloud Build？）
uvx agent-starter-pack enhance . --cicd-runner github_actions -y

# 添加 RAG 与数据摄取
uvx agent-starter-pack enhance . --base-template agentic_rag --datastore vertex_ai_search -y

# 预览将发生的变化（干运行）
uvx agent-starter-pack enhance . --deployment-target cloud_run --dry-run -y
```

---

## 模板选项

| 模板 | 部署 | 描述 |
|------|-------|-------------|
| `adk` | Agent Engine, Cloud Run, GKE | 标准 ADK 代理（默认） |
| `adk_a2a` | Agent Engine, Cloud Run, GKE | 代理间协调（A2A 协议） |
| `agentic_rag` | Agent Engine, Cloud Run, GKE | RAG 与数据摄取管道 |

---

## 部署选项

| 目标 | 描述 |
|------|-------------|
| `agent_engine` | 由 Google 管理（Vertex AI Agent Engine）。会话自动处理。 |
| `cloud_run` | 基于容器的部署。更多控制，需要 Dockerfile。 |
| `gke` | GKE Autopilot 上的基于容器的部署。完整的 Kubernetes 控制。 |
| `none` | 无部署脚手架。仅代码。 |

### "先原型"模式（推荐）

使用 `--prototype` 跳过 CI/CD 和 Terraform。首先专注于让代理工作，然后使用 `enhance` 添加部署：

```bash
# 第 1 步：创建原型
uvx agent-starter-pack create my-agent --agent adk --prototype -y

# 第 2 步：迭代代理代码...

# 第 3 步：准备好时添加部署
uvx agent-starter-pack enhance . --deployment-target agent_engine -y
```

### Agent Engine 和 session_type

使用 `agent_engine` 作为部署目标时，Agent Engine 内部管理会话。如果代码设置 `session_type`，请清除它 — Agent Engine 会覆盖它。

---

## 第 4 步：保存 DESIGN_SPEC.md 和加载开发工作流

脚手架后，将第 2 步中批准的规范保存到项目根目录作为 `DESIGN_SPEC.md`。

**然后立即加载 `/adk-dev-guide`** — 它包含开发工作流、编码指南和实施代理时必须遵循的操作规则。

---

## 作为参考脚手架

当你需要特定文件（Terraform、CI/CD 工作流、Dockerfile）但不想直接脚手架当前项目时，在 `/tmp/` 中创建临时参考项目：

```bash
uvx agent-starter-pack create /tmp/ref-project \
  --agent adk \
  --deployment-target cloud_run \
  --cicd-runner github_actions \
  -y
```

检查生成的文件，根据需要调整，并复制到实际项目中。完成后删除参考项目。

这适用于：
- 非标准项目结构，`enhance` 无法处理
- 挑选特定的基础设施文件
- 在提交 ASP 之前了解其生成内容

---

## 严格规则

- **除非明确要求，否则永远不要更改现有代码中的模型**
- **永远不要在 `create` 之前 `mkdir`** — CLI 会创建目录；预先创建会导致增强模式而不是创建模式
- **永远不要在未询问的情况下创建 Git 仓库或推送到远程** — 确认仓库名，公共还是私有，以及用户是否希望创建
- **选择 CI/CD 运行器前始终询问** — 展示 GitHub Actions 和 Cloud Build 作为选项，不要无声默认
- **Agent Engine 会清除 session_type** — 如果部署到 `agent_engine`，请从代码中删除任何 `session_type` 设置
- **使用 `--prototype` 开始** 进行快速迭代 — 后续使用 `enhance` 添加部署
- **项目名** 必须≤26 个字符，小写字母，仅包含字母/数字/连字符
- **永远不要从头编写 A2A 代码** — A2A Python API 表面（导入路径、`AgentCard` 模式、`to_a2a()` 签名）非常复杂且跨版本变化。始终使用 `--agent adk_a2a` 脚手架 A2A 项目。

---

# 示例

使用参考脚手架：
用户说："我需要一个 Dockerfile 用于我的非标准项目"
操作：
1. 创建临时项目：`uvx agent-starter-pack create /tmp/ref --agent adk --deployment-target cloud_run -y`
2. 从 /tmp/ref 复制相关文件（Dockerfile 等）
3. 删除临时项目
结果：基础设施文件适配到实际项目

---

A2A 项目：
用户说："为我构建一个 Python 代理，它公开 A2A 并部署到 Cloud Run"
操作：
1. 按标准流程（收集需求、DESIGN_SPEC、脚手架）
2. `uvx agent-starter-pack create my-a2a-agent --agent adk_a2a --deployment-target cloud_run --prototype -y`
结果：有效的 A2A 导入和 Dockerfile — 无需手动编写 A2A 代码。

---

## 故障排除

### `uvx` 命令未找到

按照 [官方安装指南](https://docs.astral.sh/uv/getting-started/installation/index.md) 安装 `uv`。

如果 `uv` 不可行，请使用 pip：

```bash
# macOS/Linux
python -m venv .venv && source .venv/bin/activate
# Windows
python -m venv .venv && .venv\Scripts\activate

pip install agent-starter-pack
agent-starter-pack create <项目名> ...
```

有关所有可用选项，运行 `uvx agent-starter-pack create --help`。
