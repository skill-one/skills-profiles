# 入门指南

引导开发者从零开始在 AWS 上部署运行代理。

## 使用场景

- 开发者希望在 AWS 上构建代理但不知道从何开始
- 开发者希望创建一个新的 AgentCore 项目
- 开发者在框架之间进行选择（Strands、LangGraph、GoogleADK、OpenAI Agents）
- 开发者刚刚运行了 `agentcore create` 并想知道下一步该做什么

**不适用场景**：

- 环境/前提条件问题（CLI 未找到、凭证损坏）→ 使用 `agents-debug`
- 向现有项目添加功能（内存、工具、策略）→ 使用 `agents-build` 或 `agents-connect`
- 迁移现有的 Bedrock 代理 → 使用 `agents-build`（加载 [`references/migrate.md`](../agents-build/references/migrate.md)）

## 输入

`$ARGUMENTS` 可以是：

- 框架偏好："使用 LangGraph"、"使用 Strands"
- 协议："MCP 服务器"、"A2A"
- 代理应执行的操作描述："一个客户支持代理"
- 空的 — 技能将引导框架选择

## 流程

### 第 0 步：验证 CLI 版本

```bash
agentcore --version
```

此技能需要 v0.9.0 或更高版本。

如果版本较旧：
> 您的 AgentCore CLI 已过时（找到 vX.Y.Z，需要 v0.9.0+）。

建议运行更新：`agentcore update`。更新完成后，重新检查版本以确认 ≥0.9.0 才继续。保留开发者已提供的任何上下文（框架偏好、项目名称、他们想构建的内容），以免他们重复输入。

如果找不到 `agentcore`：
> AgentCore CLI 未安装。运行 `npm install -g @aws/agentcore`（需要 Node.js 20+）。
> 如果您在安装过程中遇到问题，我可以运行 `agents-debug` 技能（加载 [`references/doctor.md`](../agents-debug/references/doctor.md)）来诊断您的环境。

### 第 1 步：确定意图 — 探索中还是准备创建？

在进入框架选择之前，先确定开发者的状态：

**询问开发者**："您是在探索选项（比较框架、了解 AgentCore 的功能）还是准备创建项目？"

- **探索** → 跳转到第 2 步（框架比较）。展示选项、回答问题并等待。在开发者表示准备好之前，不要构建 `create` 命令。
- **准备创建** → 跳转到第 3 步（创建项目）。如果他们已经指定了框架，则完全跳过第 2 步。
- **已有项目** → 在当前目录中查找 `agentcore/agentcore.json`。如果找到，读取它并跳转到第 5 步（下一步该做什么）。不要重新构建基础结构。

如果开发者的意图从 `$ARGUMENTS` 中明确（例如，"创建一个名为 MyBot 的 Strands 代理"），则直接跳转到第 3 步。

### 第 2 步：框架选择

**首先检查对话上下文**。如果开发者在本次对话的早期已经讨论过框架（例如，从之前的技能调用中），则不要重新展示完整表格。总结已讨论的内容，询问他们是否已决定，或者是否有变化。

如果这是第一次讨论框架，则展示选项：

**支持的框架（CLI 构建、Python）**：

| 框架 | CLI 值 | 适用于 |
|---|---|---|
| Strands | `Strands` | AWS 本地、最简单路径、最佳 AgentCore 集成 |
| LangGraph | `LangChain_LangGraph` | 复杂的基于图的流程、现有的 LangChain 投资 |
| Google ADK | `GoogleADK` | 已经使用 Google 代理工具包的团队 |
| OpenAI Agents | `OpenAIAgents` | 已经使用 OpenAI 代理 SDK 的团队 |

**询问开发者选择**。展示选项并等待他们的选择。除非他们明确表示没有偏好，否则不要假设默认值。

> **命名说明**：CLI 标志值是传递给 `--framework` 的确切字符串。在文本中使用较短的名称。

**默认推荐**（只有在开发者说 "没有偏好" 或 "你选" 的情况下）：Strands — AWS 本地框架，与 AgentCore 集成最紧密，并具有最多的示例/文档。

**关键决策点**：

- "您有现有的 LangGraph 或 OpenAI Agents 代理代码吗？" → 使用该框架
- "您需要复杂的基于图的流程和条件分支吗？" → LangGraph
- "从零开始，没有偏好？" → Strands

#### 未列出的框架？

如果开发者询问上表中未列出的框架，请按以下方式处理：

| 他们询问 | 该说什么 |
|---|---|
| **CrewAI、AutoGen、Semantic Kernel** | 未由 CLI 构建，但您可以通过 BYO Container 路径（下方）使用它们。AgentCore 运行时不依赖框架 — 任何实现 HTTP 合同的代码都可以工作。 |
| **Anthropic SDK / Claude Agent SDK** | 这是一个模型 SDK，不是代理框架。您可以在任何框架（Strands、LangGraph 等）或独立使用它。对于独立使用，用运行时合同将其封装在容器中。 |
| **Claude Code / Cursor / Copilot** | 这些是 IDE 工具，不是代理框架。它们是您 *编写* 代理代码的地方，而不是部署的地方。为代理本身选择上表中的框架。 |
| **LangChain（不使用 LangGraph）** | LangChain 是一个库，LangGraph 是基于它的代理框架。CLI 构建 LangGraph。如果您正在使用纯 LangChain 链，则 BYO Container 路径适用。 |
| **自定义/自研框架** | BYO Container 路径 — 下方查看。 |

**BYO Container 路径（任何框架、任何语言）**：

对于 CLI 未构建的框架或语言，AgentCore 运行时接受任何实现 HTTP 合同（`POST /invocations`，`GET /ping`）的容器。工作流程：

1. `agentcore create --name <ProjectName> --defaults` 构建项目结构
2. `agentcore add agent --type byo --build Container --language <Language> --code-location <path>` 注册您的代码
3. 编写 `Dockerfile` 以构建和运行您的代理
4. `agentcore deploy` 处理 ECR 推送、CDK 基础设施和运行时创建

**语言特定说明**：

| 语言 | 推荐路径 |
|---|---|
| Java (Spring Boot) | [Spring AI SDK for AgentCore](https://aws.amazon.com/blogs/machine-learning/spring-ai-sdk-for-amazon-bedrock-agentcore-is-now-generally-available) — 处理运行时合同、SSE 流式传输和健康检查。使用 `--language Other --build Container`。 |
| JavaScript / TypeScript | 在 Express/Fastify 等 中实现运行时合同。使用 `--language TypeScript --build Container`。 |
| Go、Rust、.NET、其他 | 实现 HTTP 合同。使用 `--language Other --build Container`。 |

一旦容器正确构建，本技能的其余部分（部署、状态、日志、调用）都适用。

#### 框架与模型提供者 — 常见的混淆

框架是代理如何协调（Strands、LangGraph 等）。模型提供者是它调用的 LLM（Bedrock、Anthropic、OpenAI、Gemini）。这些是独立的选择：

- Strands + Bedrock（默认）— AWS 本地一切
- Strands + Anthropic — Strands 协调，直接 Anthropic API 用于模型
- LangGraph + Bedrock — LangGraph 协调，Bedrock 用于模型
- OpenAI Agents + OpenAI — OpenAI 一切

如果开发者说 "我想使用 Claude"，他们指的是模型提供者（Bedrock 或 Anthropic），而不是框架。如果他们说是 "我想使用 LangGraph"，他们指的是框架。

### 第 3 步：创建项目

根据开发者的选择构建 `agentcore create` 命令。

**构建命令前 — 验证项目名称**。CLI 晚期失败：如果名称无效，您会在完成提示或构建完整命令后看到错误。提前检查这些规则，如果任何规则失败则拒绝名称并请求新名称：

- **长度 ≤ 23 个字符**（这比大多数开发者假设的短 — `MyCustomerSupportAgent` 是 22 个字符并适用；`CustomerSupportChatbot` 是 22 个字符并适用；`MyCustomerSupportBotApp` 是 23 个字符并刚刚适用；`MyCustomerSupportChatBot` 是 24 个字符并**失败**）
- **仅限字母数字** — 不能有连字符、下划线、点或空格
- **必须以字母开头**

接近限制时大声说出计数："该名称是 24 个字符 — CLI 将项目名称限制为 23。要将其缩短为 `<suggestion>` 吗？" 不要在名称无效的情况下运行命令，假设 CLI 错误消息会很清楚 — 它不总是这样，开发者的心智模型会因此出错。

**构建命令后，在开发者运行之前展示它以供确认**。显示带有所有标志的完整命令并解释每个选择的含义。等待开发者确认或调整后再继续。

示例展示：

> 根据您告诉我的内容，我建议的命令如下：
>
> ```bash
> agentcore create --name MyAgent --framework Strands --model-provider Bedrock --build CodeZip --memory none
> ```
>
> 这会创建一个使用 Bedrock 模型的 Strands 代理，以代码压缩包方式部署（无需 Docker）。内存可以稍后添加。
>
> 要运行此命令，还是更改任何内容？

不要自动执行命令 — 展示并等待。

**最小（默认 — Strands、Bedrock、CodeZip、无内存）**：

```bash
agentcore create --name <ProjectName> --defaults
```

**带特定选项**：

```bash
agentcore create \
  --name <ProjectName> \
  --framework <Framework> \
  --model-provider Bedrock \
  --build CodeZip \
  --memory none
```

**标志参考**：

| 标志 | 值 | 默认 |
|---|---|---|
| `--name` | 字母数字，最大 23 个字符 | 提示 |
| `--framework` | `Strands`、`LangChain_LangGraph`、`GoogleADK`、`OpenAIAgents` | 提示 |
| `--protocol` | `HTTP`、`MCP`、`A2A` | `HTTP` |
| `--build` | `CodeZip`、`Container` | `CodeZip` |
| `--model-provider` | `Bedrock`、`Anthropic`、`OpenAI`、`Gemini` | 提示 |
| `--memory` | `none`、`shortTerm`、`longAndShortTerm` | 提示 |
| `--network-mode` | `PUBLIC`、`VPC` | `PUBLIC` |
| `--dry-run` | — | 预览而不创建 |

**选择指导**：

- **协议**：除非开发者需要 MCP 工具服务或 A2A 代理间通信，否则使用 `HTTP`
- **构建**：除非开发者需要自定义系统依赖项（CodeZip 部署更快，无需本地 Docker），否则使用 `CodeZip`
- **模型提供者**：除非开发者有使用其他提供者的特定原因（Bedrock 不需要管理 API 密钥），否则使用 `Bedrock`
- **内存**：从 `none` 开始 — 内存可以通过 `agents-build`（加载 [`references/memory.md`](../agents-build/references/memory.md)）在开发者需要时添加

### 第 4 步：解释已创建的内容

项目存在后，读取 `agentcore/agentcore.json` 和生成的代码来解释项目结构。

以下布局反映 CLI v0.9.x。如果 CLI 版本不同，运行 `tree <ProjectName>/ -L 3` 查看实际生成的结构并从此解释。

```
<ProjectName>/
├── agentcore/
│   ├── agentcore.json      ← 项目配置（代理、资源）
│   ├── aws-targets.json    ← AWS 账户 + 区域
│   ├── .env.local          ← 本地环境变量（git 忽略）
│   └── cdk/                ← CDK 基础设施（自动管理，不要编辑）
└── app/
    └── <AgentName>/
        ├── main.py          ← 您的代理代码 — 这是您构建的地方
        ├── mcp_client/      ← 预先连接的 MCP 客户端示例（见下注）
        └── pyproject.toml   ← Python 依赖项
```

**突出显示的关键文件**：

- `app/<AgentName>/main.py` — 代理的入口点。这是开发者添加工具、系统提示和逻辑的地方。
- `agentcore/agentcore.json` — 项目配置。资源通过 `agentcore add` 命令添加到这里。
- `agentcore/.env.local` — 本地环境变量。部署后，资源 ID 会写入此处以供本地开发。

**关于预先构建的 MCP 客户端的提示**。`main.py` 从 `mcp_client/client.py` 导入 `get_streamable_http_mcp_client()` 并将其添加到 `tools`。在全新项目中，此客户端指向公共示例 MCP 端点 — 因此 `agentcore dev` 立即工作。需要关注的两点：

1. **如果您将其指向尚未部署的网关，它将变成一个无声的无操作。** 常见路径是将示例端点替换为 `os.getenv("AGENTCORE_GATEWAY_<NAME>_URL")`。该环境变量仅在 `agentcore deploy` 后填充。如果开发者重新指向并运行 `agentcore dev` 之前部署，`get_streamable_http_mcp_client()` 返回一个 `None` URL 的客户端，代理开始时没有 MCP 工具 — 没有错误，也没有警告。参见 `agents-connect` 中 "Local dev gap" 部分的守卫模式：`if not GATEWAY_URL: tools = []`。
2. **如果开发者根本不需要 MCP 工具**，请删除 `mcp_clients` 列和将它们添加到 `tools` 的循环。模板包含它作为便利，而不是要求。

`agents-connect` 中 `Path A` 的参考客户端代码显示了部署运行后网关后 MCP 客户端的正确模式。

### 第 5 步：本地开发

```bash
agentcore dev
```

这会启动本地开发服务器。开发者可以立即与他们的代理交互。

**开发服务器绑定到的端口**（如果您正在脚本化 `curl` 调用或从另一个进程进行测试，则很重要）：

| 协议 | 默认端口 |
|---|---|
| HTTP | `8080` |
| MCP | `8000` |
| A2A | `9000` |

CLI 在启动时打印绑定的端口和 URL — 始终从 CLI 输出中读取实际值，而不是硬编码。**如果默认端口已被占用**，CLI 会自动递增（例如，8080 → 8081 → 8082），因此第二个开发会话或先前运行中遗留的进程可能会在不警告的情况下更改您的端口。使用 `agentcore dev --port <N>` 固定它，或者如果调用失败显示连接拒绝或退出代码 7 错误，则使用 `ps` 搜索/检查 CLI 旗帜。

**需要提及的重要限制**：

- 内存在 `agentcore dev` 中不可用 — 它需要部署
- 网关 URL 在本地不可用 — 它需要部署
- 本地服务器使用项目中配置的模型提供者

### 第 6 步：首次部署

当开发者准备好部署时：

```bash
agentcore deploy
```

这将：

1. 展示将要创建的 AWS 资源预览
2. 请求确认
3. 通过 CDK 构建和部署

**首次部署需要 3-5 分钟。** 后续部署更快。

部署后，展示他们如何调用：

```bash
agentcore invoke "你好，你能做什么？"
```

以及如何检查状态：

```bash
agentcore status
```

### 第 7 步：下一步做什么

根据开发者表示他们想构建的内容，建议逻辑上的下一步技能：

| 开发者意图 | 下一步技能 | 命令提示 |
|---|---|---|
| "我如何从我的应用中调用它？" | `agents-build` | `agentcore fetch access` |
| "我想让它记住事情" | `agents-build` | `agentcore add memory` |
| "我想让它调用外部 API" | `agents-connect` | `agentcore add gateway` |
| "我想限制它能做什么" | `agents-connect` | `agentcore add policy-engine` |
| "我想衡量质量" | `agents-optimize` | `agentcore add evaluator` |
| "我想进入生产环境" | `agents-harden` | 生产就绪清单 |
| "我想让多个代理协同工作" | `agents-build` | `agentcore create --protocol A2A` |
| "我需要它在一个 VPC 中" | `agents-build` | `agentcore create --network-mode VPC` |

不要压倒 — 根据开发者实际询问的内容建议一个或两个下一步。

### 示例演练

对于任务导向的提示（例如，"构建一个客户支持代理"），加载匹配的示例参考：

| 开发者任务 | 参考 |
|---|---|
| 客户支持、聊天机器人、回答策略问题 | [`references/example-support-agent.md`](references/example-support-agent.md) |

随着常见模式的涌现，可以将更多示例添加到此技能的参考目录中。
