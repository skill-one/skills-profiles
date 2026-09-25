# 项目脚手架指南

> **要求：** `agents-cli` (`uv tool install google-agents-cli`) — 如果需要，请先安装 uv ([安装 uv](https://docs.astral.sh/uv/getting-started/installation/index.md))。

使用 `agents-cli` 命令行界面创建新的代理项目，或通过部署、CI/CD 和基础设施脚手架增强现有项目。

---

## 前置条件：明确需求（新项目必填）

在脚手架新项目之前，加载 `/google-agents-cli-workflow` 并完成阶段 0** — 在运行任何 `scaffold create` 命令之前，先明确用户的需求。询问代理应该做什么，它需要哪些工具/API，以及他们是否想要原型或完整部署。

---

## 第 1 步：选择架构

**将用户选择映射到 CLI 标志：**

| 选择 | CLI 标志 |
|------|----------|
| 检索/RAG、沙盒执行、跨会话内存、OAuth 同意、护栏、计划运行 | **无标志** — 这些来自克隆并学习配方。**ADK Python：** 查看位于 `/google-agents-cli-adk-code` 中的主题索引 → `references/samples.md`；在其他框架上，查看框架模板提供的示例索引 |
| A2A 协议 | 内置于脚手架的应用程序中 — 正常脚手架（**ADK Python：** `--agent adk`，默认值；**ADK Go：** `--agent adk_go`） |
| 原型（无部署） | `--prototype` |
| 部署目标 | `--deployment-target <agent_runtime\|cloud_run\|gke>` |
| CI/CD 运行器 | `--cicd-runner <github_actions\|google_cloud_build>` |
| 会话存储 | `--session-type <in_memory\|cloud_sql\|agent_platform_sessions>` |

### 产品名称映射

旧名称 → CLI 值（`vertexai` SDK 包名称保持不变）：

- Agent Engine / Vertex AI Agent Engine → `--deployment-target agent_runtime`
- Agent Engine 会话 / Agent Platform Sessions → `--session-type agent_platform_sessions`
- Vertex AI 搜索 / Vertex AI 向量搜索 / RAG → 克隆并学习配方，不是标志

> **已移除的标志。** `--datastore`、`agentic_rag` 模板以及 `agents-cli infra datastore` /
> `agents-cli data-ingestion` 已不再存在。如果你尝试使用其中一个，你需要一个配方。

---

## 第 2 步：创建或增强项目

### 创建新项目

```bash
agents-cli scaffold create <project-name> \
  --agent <template> \
  --deployment-target <target> \
  --region <region> \
  --prototype
```

**约束：**
- 项目名称必须为 **26 个字符或更少**，仅包含小写字母、数字和连字符。
- 在运行 `create` 之前**不要** `mkdir` 项目目录 — CLI 会自动创建它。如果你先创建目录，`create` 将失败或表现异常。
- 根据你正在运行的 IDE 自动检测指导文件名，并相应地传递 `--agent-guidance-filename`（Antigravity CLI 为 `GEMINI.md`，Claude Code 为 `CLAUDE.md`，OpenAI Codex/其他为 `AGENTS.md`）。
- 增强现有项目时，检查代理代码的位置。如果它不在 `app/` 中，请传递 `--agent-directory <dir>`（例如 `--agent-directory agent`）。如果设置错误，增强将遗漏或错误放置文件。

### 参考文件

| 文件 | 内容 |
|------|----------|
| `references/flags.md` | `create` 和 `enhance` 命令的完整标志参考 |

### 增强现有项目

```bash
agents-cli scaffold enhance . --deployment-target <target>
agents-cli scaffold enhance . --cicd-runner <runner>
```

从项目目录内部运行此命令（或传递路径而不是 `.`）。

### 升级项目

将现有项目升级到更新的 agents-cli 版本，智能地应用更新同时保留你的自定义设置：

```bash
agents-cli scaffold upgrade                # 升级当前目录
agents-cli scaffold upgrade <project-path> # 升级特定项目
agents-cli scaffold upgrade --dry-run      # 预览更改而不应用
agents-cli scaffold upgrade --auto-approve  # 自动应用非冲突更改
```

### 执行模式

CLI 默认为 **严格程序化模式** — 所有必需的参数必须作为 CLI 标志提供，否则将引发 `UsageError`。不需要批准标志。显式传递所有必需参数。

### 常见工作流

**在运行这些命令之前，始终询问用户。** 展示选项（CI/CD 运行器、部署目标等），并在执行前确认。

```bash
# 向现有原型添加部署（严格程序化）
agents-cli scaffold enhance . --deployment-target agent_runtime

# 添加 CI/CD 管道（询问：GitHub Actions 或 Cloud Build？）
agents-cli scaffold enhance . --cicd-runner github_actions
```

---

## 模板选项

| 模板 | 语言 | 部署 | 描述 |
|------|------|------|------|
| `adk` | Python | Agent Runtime, Cloud Run, GKE | 标准 ADK 代理（默认值）；内置 A2A 协议 |
| `adk_go` | Go | Agent Runtime, Cloud Run, GKE | 标准 ADK Go 代理；内置 A2A 协议 |

> **`adk` 和 `adk_go` 是唯一的内置模板。** `adk` 是默认值，因此 Go 项目需要显式指定 `--agent adk_go`。
> 其他框架作为模板存储库直接提供，你可以从它们脚手架：`--agent google/agents-cli/extensions/langchain/template@v1.7.0`，无需安装任何内容。第一方 LangChain 模板是 agents-cli 存储库中的 `extensions/langchain/template/`；查看
> `/google-agents-cli-workflow` → `references/extension.md` 以发布你自己的。模板之外的特性（检索、沙盒执行、内存、OAuth、护栏）是克隆并学习配方，不是模板。**ADK Python：** 查看位于
> `/google-agents-cli-adk-code` → `references/samples.md` 中的主题索引。**

> **实时和语音代理：** 无模板。脚手架 `adk`，然后按照 `/google-agents-cli-adk-code` 中的转换清单
> (`references/adk-python-live.md`，"将脚手架项目转换为实时") 进行操作。模型交换是五个编辑之一。**

---

## 部署选项

| 目标 | 描述 |
|------|------|
| `agent_runtime` | 由 Google 管理（Vertex AI Agent Runtime）。基于容器 — Agent Engine 构建项目 Dockerfile。会话自动处理。 |
| `cloud_run` | 基于容器的部署。更多控制；你构建和部署 Dockerfile。 |
| `gke` | 基于 GKE Autopilot 的容器。完整的 Kubernetes 控制。 |
| `none` | 无部署脚手架。仅代码（仍然包含 Dockerfile）。 |

### "先原型"模式（推荐）

使用 `--prototype` 跳过 CI/CD 和 Terraform，首先专注于让代理工作，然后使用 `scaffold enhance` 添加部署：

```bash
# 第 1 步：创建原型
agents-cli scaffold create my-agent --agent adk --prototype

# 第 2 步：迭代代理代码...

# 第 3 步：准备好时添加部署
agents-cli scaffold enhance . --deployment-target agent_runtime
```

### Agent Runtime 和 session_type

使用 `agent_runtime` 作为部署目标时，Agent Runtime 内部管理会话。如果你的代码设置了 `session_type`，请清除它 — Agent Runtime 会覆盖它。

---

## 第 3 步：加载开发工作流

脚手架后立即加载 `/google-agents-cli-workflow` — 它包含实现代理时必须遵循的开发工作流、编码指南和操作规则。

你编辑的内容因语言而异；`/google-agents-cli-adk-code` 包含每个语言的注释树，
在 `references/adk-python.md` 和 `references/adk-go.md` 中。

- **ADK Python (`--agent adk`)** — 自定义 `app/agent.py` 和 `app/tools.py`。
- **ADK Go (`--agent adk_go`)** — 自定义 `app/agent.go`。

`.env` 是你的。保留模板生成的所有其他内容 — 它们用于设置服务、会话和内置 A2A 表面。

**适应配方：** 复制其 `app/`、`infra/terraform/` 以及任何摄取或配置到你的脚手架项目中，然后从配方自己的 `Makefile` 运行配置（例如 `make setup-infra`）。从其 `AGENTS.md` 开始。

**验证你的代理是否正常工作：** 使用 `agents-cli run "test prompt"` 进行快速冒烟测试，然后使用 `agents-cli eval run` 进行系统验证。**不要** 编写断言 LLM 响应内容的 pytest 测试，这属于 eval。

---

## 作为参考脚手架

当你需要特定文件（Terraform、CI/CD 工作流、Dockerfile）但不想直接脚手架当前项目时，在 `/tmp/` 中创建临时参考项目：

```bash
agents-cli scaffold create ref-project --output-dir /tmp \
  --agent adk \
  --deployment-target cloud_run
```

检查生成的文件，修改你需要的内容，并复制到实际项目中。完成后删除参考项目。

这适用于：
- 非标准项目结构，`enhance` 无法处理
- 挑选特定的基础设施文件
- 在提交之前理解 CLI 生成的内容

---

## 关键规则

- **永远不要跳过需求澄清** — 加载 `/google-agents-cli-workflow` 阶段 0 并在运行 `scaffold create` 之前明确用户的意图
- **永远不要在现有代码中更改模型**，除非明确要求
- **永远不要在 `create` 之前 `mkdir`** — CLI 创建目录；预先创建它会导致增强模式而不是创建模式
- **永远不要在未询问的情况下创建 Git 仓库或推送到远程** — 确认仓库名称、公开与私有，以及用户是否希望创建它
- **在选择 CI/CD 运行器之前始终询问** — 展示 GitHub Actions 和 Cloud Build 作为选项，不要无声默认
- **Agent Runtime 清除 session_type** — 如果部署到 `agent_runtime`，请从你的代码中删除任何 `session_type` 设置
- **始终使用 `--prototype` 开始** 进行快速迭代 — 使用 `enhance` 添加部署
- **项目名称** 必须为 ≤26 个字符，小写字母，仅包含字母、数字和连字符
- **永远不要从头开始编写 A2A 代码** — A2A 内置于脚手架的应用程序中（`adk` 和 `adk_go` 模板以及框架模板一样）；每种语言的 A2A 表面（导入路径、`AgentCard` 模式等）都很复杂，并且随版本变化。正常脚手架；永远不要手动编写 A2A 表面。（唯一认可的 A2A 手动编辑是*移除*为**实时**代理生成的连接，它不能通过 A2A 提供 — 查看 `/google-agents-cli-adk-code`，`references/adk-python-live.md`。）

---

# 示例

使用作为参考的脚手架：
用户说："我需要一个非标准项目的 Dockerfile"
操作：
1. 创建临时项目：`agents-cli scaffold create ref --output-dir /tmp --agent adk --deployment-target cloud_run`
2. 从 /tmp/ref 复制相关文件（Dockerfile 等）
3. 删除临时项目
结果：基础设施文件适应实际项目

---

A2A 项目：
用户说："为我构建一个 Python 代理，它暴露 A2A 并部署到 Cloud Run"
操作：
1. 遵循标准流程（理解需求、选择架构、脚手架）
2. `agents-cli scaffold create my-a2a-agent --agent adk --deployment-target cloud_run --prototype`
结果：有效的 A2A 导入和 Dockerfile — 没有手动编写 A2A 代码。

---

Go 项目：
用户说："为我构建一个部署到 Cloud Run 的 Go 代理"
操作：
1. 遵循标准流程（理解需求、选择架构、脚手架）
2. `agents-cli scaffold create my-go-agent --agent adk_go --deployment-target cloud_run --prototype`
结果：Go 项目包含 `app/agent.go`、`main.go` 中的启动器，以及根目录的 A2A 卡。

---

## 故障排除

### `agents-cli` 命令未找到

查看 `/google-agents-cli-workflow` → **设置** 部分。

---

## 相关技能

- `/google-agents-cli-workflow` — 开发工作流、编码指南和构建-评估-部署生命周期
- `/google-agents-cli-adk-code` — 编写代理代码的 ADK API 快速参考，包括图工作流 API
- `/google-agents-cli-deploy` — 部署目标、CI/CD 管道和生产工作流
- `/google-agents-cli-eval` — 评估方法、数据集模式以及 eval-修复循环
