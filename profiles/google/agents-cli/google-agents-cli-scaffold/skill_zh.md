# 项目脚手架指南

> **要求：** `agents-cli`（`uv tool install google-agents-cli`）—— 如需要，请先安装 uv：[安装 uv](https://docs.astral.sh/uv/getting-started/installation/index.md)

使用 `agents-cli` CLI 创建新的 agent 项目，或通过部署、CI/CD 和基础设施脚手架来完善现有项目。

---

## 前提条件：明确需求（新项目强制）

在搭建新项目之前，请加载 `/google-agents-cli-workflow` 并完成 **阶段 0**——在运行任何 `scaffold create` 命令之前，先明确用户的需求。询问 agent 应该执行什么操作、需要哪些工具和 API，以及是希望制作原型还是进行完整部署。

---

## 步骤 1：选择架构

**将用户选择映射到 CLI 参数：**

| 选择 | CLI 参数 |
|--------|----------|
| 检索/RAG、沙盒执行、跨会话记忆、OAuth 同意、护栏、定时运行 | **无参数**——这些来自克隆并学习配方。**ADK Python：** 参见 `/google-agents-cli-adk-code` 中的主题索引 → `references/samples.md`；在其他框架上，参见框架模板自带的示例索引 |
| A2A 协议 | 内置在脚手架应用中——正常脚手架（**ADK Python：** `--agent adk`，默认值；**ADK Go：** `--agent adk_go`） |
| 原型（无部署） | `--prototype` |
| 部署目标 | `--deployment-target <agent_runtime\|cloud_run\|gke>` |
| CI/CD 运行器 | `--cicd-runner <github_actions\|google_cloud_build>` |
| 会话存储 | `--session-type <in_memory\|cloud_sql\|agent_platform_sessions>` |

### 产品名称映射

旧版名称 → CLI 值（`vertexai` SDK 包名称不变）：

- Agent Engine / Vertex AI Agent Engine → `--deployment-target agent_runtime`
- Agent Engine sessions / Agent Platform Sessions → `--session-type agent_platform_sessions`
- Vertex AI Search / Vertex AI Vector Search / RAG → 克隆并学习配方，而非标志

> **已移除的标志。** `--datastore`、`agentic_rag` 模板，以及 `agents-cli infra datastore` / `agents-cli data-ingestion` 不再存在。如果你使用其中之一，请转而使用配方。

---

## 步骤 2：创建或完善项目

### 创建新项目

```bash
agents-cli scaffold create <project-name> \
  --agent <template> \
  --deployment-target <target> \
  --region <region> \
  --prototype
```

**约束条件：**
- 项目名称必须**不超过 26 个字符**，仅可使用小写字母、数字和连字符。
- 在运行 `create` 之前，不要对项目目录执行 `mkdir`——CLI 会自动创建该目录。如果先执行 mkdir，`create` 将失败或行为异常。
- 根据你正在使用的 IDE 自动检测指导文件名，并相应传递 `--agent-guidance-filename`（Antigravity CLI 对应 `GEMINI.md`，Claude Code 对应 `CLAUDE.md`，OpenAI Codex/其他对应 `AGENTS.md`）。
- 在完善现有项目时，检查 agent 代码所在位置。如果不在 `app/` 目录中，请传递 `--agent-directory <dir>`（例如 `--agent-directory agent`）。设置错误会导致 enhance 遗漏或误置文件。

### 参考文件

| 文件 | 内容 |
|------|----------|
| `references/flags.md` | `create` 和 `enhance` 命令的完整标志参考 |

### 完善现有项目

```bash
agents-cli scaffold enhance . --deployment-target <target>
agents-cli scaffold enhance . --cicd-runner <runner>
```

运行此命令时，需在当前项目目录内（或直接传入路径代替 `.`）。

### 升级项目

将现有项目升级到更新的 agents-cli 版本，智能应用更新，同时保留你的自定义设置：

```bash
agents-cli scaffold upgrade                # 升级当前目录
agents-cli scaffold upgrade <project-path> # 升级特定项目
agents-cli scaffold upgrade --dry-run      # 预览变更，不实际应用
agents-cli scaffold upgrade --auto-approve # 自动应用不冲突的变更
```

### 执行模式

CLI 默认采用 **严格的编程模式**——所有必填参数必须通过 CLI 标志或参数提供，否则将抛出 `UsageError`。无需审批标志。请明确传递所有必填参数。

### 常见工作流

**在执行以下命令之前，始终先询问用户。** 呈现选项（CI/CD 运行器、部署目标等），并在执行前确认。

```bash
# 为现有原型添加部署（严格的编程模式）
agents-cli scaffold enhance . --deployment-target agent_runtime

# 添加 CI/CD 流水线（询问：GitHub Actions 还是 Cloud Build？）
agents-cli scaffold enhance . --cicd-runner github_actions
```

---

## 模板选项

| 模板 | 语言 | 部署 | 说明 |
|----------|----------|------------|-------------|
| `adk` | Python | Agent Runtime、Cloud Run、GKE | 标准 ADK agent（默认值）；A2A 协议内置 |
| `adk_go` | Go | Agent Runtime、Cloud Run、GKE | 标准 ADK Go agent；A2A 协议内置 |

> **`adk` 和 `adk_go` 是仅有的内置模板。** `adk` 是默认值，因此 Go 项目需要显式使用 `--agent adk_go`。
> 其他框架作为模板仓库，你可以直接脚手架（scaffold）它们：`--agent google/agents-cli/extensions/langchain/template@v1.6.1`，无需安装任何东西。第一方的 LangChain 模板位于 agents-cli 仓库的 `extensions/langchain/template/` 目录中；请参考
> `/google-agents-cli-workflow` → `references/extension.md` 以发布你自己的版本。超出模板的能力——检索、沙盒执行、记忆、OAuth、护栏——是配方，而非模板。**ADK Python：** 参见
> `/google-agents-cli-adk-code` → `references/samples.md`。

---

## 部署选项

| 目标 | 说明 |
|--------|-------------|
| `agent_runtime` | 由 Google（Vertex AI Agent Runtime）管理。基于容器的——Agent Engine 构建项目 Dockerfile。会话自动处理。 |
| `cloud_run` | 基于容器的部署。控制更灵活；你需要构建并部署 Dockerfile。 |
| `gke` | 基于 GKE Autopilot 的容器化部署。完整的 Kubernetes 控制。 |
| `none` | 无部署脚手架。仅代码（仍包含 Dockerfile）。 |

### "先原型后部署"模式（推荐）

以 `--prototype` 开始，跳过 CI/CD 和 Terraform。首先专注于让 agent 正常工作，之后再使用 `scaffold enhance` 添加部署：

```bash
# 步骤 1：创建原型
agents-cli scaffold create my-agent --agent adk --prototype

# 步骤 2：迭代 agent 代码...

# 步骤 3：就绪后添加部署
agents-cli scaffold enhance . --deployment-target agent_runtime
```

### Agent Runtime 与 session_type

当使用 `agent_runtime` 作为部署目标时，Agent Runtime 会在内部管理会话。如果代码中设置了 `session_type`，请将其清除——Agent Runtime 会覆盖它。

---

## 步骤 3：加载开发工作流

脚手架完成后，请立即加载 `/google-agents-cli-workflow`——其中包含开发工作流、编码指南和必须遵循的运维规则。

你编辑的内容因语言而异；`/google-agents-cli-adk-code` 包含每种语言的标注树，位于 `references/adk-python.md` 和 `references/adk-go.md` 中。

- **ADK Python（`--agent adk`）** —— 修改 `app/agent.py` 和 `app/tools.py`。
- **ADK Go（`--agent adk_go`）** —— 修改 `app/agent.go`。

`.env` 由你自行管理。保留模板生成的其他所有内容——它负责连接服务、会话和内置的 A2A 界面。

**适配配方：** 将配方的 `app/`、`infra/terraform/` 以及任何摄取或配置内容复制到脚手架的项目中，然后从配方的 `Makefile` 运行配置（例如 `make setup-infra`）。从其 `AGENTS.md` 开始。

**验证 agent 是否正常工作：** 使用 `agents-cli run "test prompt"` 进行快速冒烟测试，然后使用 `agents-cli eval run` 进行系统化验证。**不要**编写针对 LLM 响应内容断言的 pytest 测试，此类测试应放在 eval 中。

---

## 作为参考脚手架

当你需要特定的文件（Terraform、CI/CD 工作流、Dockerfile），但不打算直接为当前项目进行脚手架时，请在 `/tmp/` 中创建一个临时参考项目：

```bash
agents-cli scaffold create ref-project --output-dir /tmp \
  --agent adk \
  --deployment-target cloud_run
```

检查生成的文件，适配所需部分，然后复制到实际项目中。完成后删除参考项目。

这适用于以下场景：
- 无法通过 `enhance` 处理的非标准项目结构
- 挑选特定的基础设施文件
- 在决定采用 CLI 生成的内容之前，理解 CLI 生成的内容

---

## 关键规则

- **切勿跳过需求澄清** —— 加载 `/google-agents-cli-workflow` 的阶段 0，并在运行 `scaffold create` 之前明确用户意图
- **切勿在未明确要求的情况下修改现有代码中的模型**
- **切勿在 `create` 之前执行 `mkdir`** —— CLI 会创建该目录；提前创建会导致以 enhance 模式而非 create 模式运行
- **切勿未经询问就创建 Git 仓库或推送到远程** —— 确认仓库名称、公/私、以及用户是否希望创建它
- **选择 CI/CD 运行器前始终询问** —— 呈现 GitHub Actions 和 Cloud Build 作为选项，不要静默默认为某个默认值
- **Agent Runtime 会清除 session_type** —— 如果部署到 `agent_runtime`，从代码中移除任何 `session_type` 设置
- **以 `--prototype` 开始** 进行快速迭代——后续使用 enhance 添加部署
- **项目名称** 必须 ≤26 个字符，仅限小写字母，字母/数字/连字符
- **切勿从零开始编写 A2A 代码** —— A2A 已内置在脚手架应用中（`adk` 和 `adk_go` 模板及框架模板均如此）；每种语言的 A2A 界面（导入路径、`AgentCard` schema 等）非同寻常，且随版本变化。正常脚手架，切勿手动编写 A2A 界面。

---

# 示例

使用脚手架作为参考：
用户说："我需要为我的非标准项目生成 Dockerfile"
操作：
1. 创建临时项目：`agents-cli scaffold create ref --output-dir /tmp --agent adk --deployment-target cloud_run`
2. 从 /tmp/ref 复制相关文件（Dockerfile 等）
3. 删除临时项目
结果：适配实际项目的基建文件

---

A2A 项目：
用户说："请为我构建一个暴露 A2A 并部署到 Cloud Run 的 Python agent"
操作：
1. 遵循标准流程（理解需求、选择架构、脚手架）
2. `agents-cli scaffold create my-a2a-agent --agent adk --deployment-target cloud_run --prototype`
结果：有效的 A2A 导入和 Dockerfile——未手动编写 A2A 代码。

---

Go 项目：
用户说："请为我构建一个部署到 Cloud Run 的 Go agent"
操作：
1. 遵循标准流程（理解需求、选择架构、脚手架）
2. `agents-cli scaffold create my-go-agent --agent adk_go --deployment-target cloud_run --prototype`
结果：包含 `app/agent.go`、`main.go` 启动器和根目录下 A2A 卡片的 Go 项目。

---

## 故障排除

### `agents-cli` 命令未找到

参见 `/google-agents-cli-workflow` → **设置** 部分。

---

## 相关技能

- `/google-agents-cli-workflow` — 开发工作流、编码指南，以及构建-评估-部署生命周期
- `/google-agents-cli-adk-code` — ADK API 快速参考，包括图 Workflow API
- `/google-agents-cli-deploy` — 部署目标、CI/CD 流水线和生产工作流
- `/google-agents-cli-eval` — 评估方法、数据集 schema 和评估修复循环
