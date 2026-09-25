# 连接

通过 AgentCore 网关为您的 AgentCore 代理访问外部 API、工具和服务 — 并使用 Cedar 策略控制其访问权限。

## 使用场景

- 您希望代理调用外部 API 或 MCP 服务器
- 您希望将 Lambda 函数作为代理工具公开
- 您有一个 OpenAPI 规范，希望将其转换为代理工具
- 您的代理需要凭证来调用外部服务
- 您希望限制代理可以调用的工具（Cedar 策略）
- 您希望对工具调用进行基于角色或基于金额的访问控制
- 网关连接、工具调用或策略授权失败

为添加 Cedar 策略以控制工具访问，加载 [`references/policy.md`](references/policy.md)。

## 输入

`$ARGUMENTS` 是可选的：

```
/connect                    # 交互式 — 询问您正在连接什么
/connect mcp                # MCP 服务器设置
/connect lambda             # Lambda 函数作为工具
/connect openapi            # OpenAPI 规范作为工具
/connect credential         # 添加用于出站认证的凭证
```

## 处理

### 第 0 步：验证 CLI 版本

运行 `agentcore --version`。此技能需要 v0.9.0 或更高版本。如果版本较旧，请告诉开发者在继续之前运行 `agentcore update`。

### 第 1 步：读取项目

读取 `agentcore/agentcore.json` 以了解：

- 项目使用的框架
- 已配置的网关和目标（在 `agentCoreGateways` 数组中）

**如果没有项目上下文：** 询问他们试图连接什么，并使用相应的模式继续进行。

### 第 2 步：确定他们正在连接什么

询问（或从 `$ARGUMENTS` 推断）：

> "您正在连接您的代理到什么？
>
> 1. 外部 MCP 服务器（例如，第三方工具提供者）
> 2. 您编写的 Lambda 函数
> 3. 具有 OpenAPI 规范的 API
> 4. AWS API Gateway REST API
> 5. 没有 OpenAPI 规范、MCP 服务器或 Lambda 的外部服务 — 并且您无法添加一个"

**选项 1–4 将服务作为网关目标。** 这是默认路径：网关通过其凭证提供程序处理出站认证（因此代理代码永远不会看到密钥），工具通过 MCP 可发现，策略引擎可以在边缘授权或拒绝调用。选择与服务匹配的目标类型。

**选项 5 是路径 D** — 注册凭证并从代理代码直接调用 API。这是当前端不实用时的回退；该技能将引导您了解何时适用以及何时不适用。

---

## 默认：优先选择网关目标而不是代码中的直接 API 调用

在深入路径之前，设定预期。大多数“我的代理需要调用 X”的请求都落在网关目标上 — 而不是 `httpx` 在入口点内。

**为什么网关是默认选项：**

- **边缘处的凭证注入。** 网关的凭证提供程序（OAuth、API 密钥、IAM）将认证附加到出站请求。代理代码调用 `session.call_tool(...)` — 它永远不会接触密钥。执行 `client = openai.OpenAI(api_key=...)` 的代理代码可能在泄露提示/日志行/回溯的一线之外泄露密钥。
- **可发现的工具目录。** 工具由 MCP 服务器列出；框架（Strands、LangGraph 等）自动绑定它们。添加工具是 `agentcore add gateway-target` + 重新部署，而不是代码更改。
- **策略执行。** Cedar 策略可以按主体、按工具、按参数值授权或拒绝工具调用。当工具调用埋藏在 `httpx.post(...)` 内的代理代码中时，这是不可能的。
- **语义搜索。** 一旦目录中有 20 多个工具，`x_amz_bedrock_agentcore_search` 根据每次回合选择相关的工具。

**当代理代码中的直接 API 调用是正确答案时：**

| 情况 | 为什么网关不合适 | 该怎么做 |
|---|---|---|
| 流式/双向协议（带有实时输出的 SSE、WebSockets、WebRTC、长轮询） | 网关的 MCP 传输不支持这些 | 直接调用，路径 D |
| 可测量的延迟热点，MCP 跳转的权衡可接受 | 额外的网络跳转 | 直接调用，路径 D，并附带测量以支持决策 |
| 商家专有协议 / 二进制 SDK | 网关没有 HTTP 表面来前端 | 直接使用商家 SDK，路径 D 用于任何密钥 |
| 通过 A2A 调用另一个代理 | A2A 按设计是 HTTP，并有自己的认证模型 | [`agents-build/references/multi-agent.md`](../agents-build/references/multi-agent.md)，而不是网关目标 |
| 运行时已经具有 IAM 的 AWS 服务 SDK（S3、DynamoDB、SQS 等） | 前端没有认证值 — 增加跳转 | 直接使用 boto3 调用运行时的执行角色 |

对于**所有其他情况**，建议使用网关目标。如果开发人员坚持直接调用，请询问上述五个情况中哪个适用。如果没有，请将他们引导回网关目标。

**分类启发式：**

- 服务具有 MCP 服务器 → 路径 A
- 服务是您控制的 Lambda 函数 → 路径 B
- 服务具有 OpenAPI 规范（或者您可以生成一个 — FastAPI、ASP.NET、Spring 等自动生成 OpenAPI）→ 路径 C
- 服务已经由 API Gateway 前端 → 路径 C (`--type api-gateway`)
- 以上都不适用，并且您无法添加一个 → 路径 D

---

## 网关是什么 — 以及它不是什么

在选择目标类型之前，确保正确的思维模型。大多数网关混淆来自将其翻转。

**网关为您的代理提供要调用的工具。** 方向是：

```
您的代理  ───→  网关  ───→  Lambda 函数 / OpenAPI API / MCP 服务器 / Smithy 模型
             (代理调用工具)
```

代理是客户端。网关提供工具目录。每个工具是网关目标（Lambda、OpenAPI、MCP 服务器、API Gateway、Smithy）。

**网关不是一个用于代理的入站反向代理。** 如果您正在构建一个需要调用您的代理的应用，应用不会通过网关。方向是：

```
您的应用  ───→  AgentCore 运行时  (直接 invoke_agent_runtime 调用)
```

应用使用 IAM SigV4 签署调用或显示 JWT。有关应用端模式的更多信息，请参阅 [`agents-build/references/integrate.md`](../agents-build/references/integrate.md)。

### 当您不确定需要哪个方向时

问：**谁在调用谁？**

- "我的代理需要查找天气数据" → 代理正在调用一个工具 → **网关目标**（此技能，路径 A/B/C）
- "我的 FastAPI 应用需要调用我的代理" → 应用正在调用代理 → **直接调用**（不是网关；使用 [`agents-build/references/integrate.md`](../agents-build/references/integrate.md)）
- "我的代理需要从我的 FastAPI 应用获取数据" → 代理正在将应用作为工具调用 → **网关目标**，将应用公开为 OpenAPI 或 REST 目标（路径 C，带有您的 FastAPI 的 `/openapi.json`）

如果您发现自己配置了一个网关目标，其端点是 `bedrock-agentcore.<region>.amazonaws.com` 或指向您自己的运行时 URL，请停止 — 您已经翻转了流程。

### 适合您工具的目标类型

| 工具是什么 | 目标类型 | 备注 |
|---|---|---|
| MCP 服务器（第三方或您自己的） | `mcp-server` | 最常见的 MCP 工具目录 |
| 您编写的 AWS Lambda 函数 | `lambda-function-arn` | 自动使用 IAM 认证 |
| 具有 OpenAPI 规范的 HTTP API | `open-api-schema` | FastAPI 的内置 `/openapi.json` 适用 |
| AWS API Gateway REST API | `api-gateway` | 用于已经由 API Gateway 前端的 API |
| 具有 Smithy 模型的 AWS 服务 | `smithy-model` | 直接 AWS 服务集成 |

您的工具没有自然的 OpenAPI 规范，也不是 MCP 服务器或 Lambda？要么将其包装在 Lambda 中（最简单），为其生成 OpenAPI 规范（FastAPI 自动生成），要么使用 API Gateway 前端。

---

### 第 3 步：导航认证矩阵

**这是最常见的错误来源。** 认证选项取决于目标类型，CLI 仅暴露 API/SDK 支持的子集。

| 您正在连接什么 | CLI `--type` | 通过 CLI 的出站认证 | 通过 API/SDK 的其他选项 |
|---|---|---|---|
| 外部 MCP 服务器 | `mcp-server` | `none`，`oauth`（仅 2LO） | OAuth 3LO (`AUTHORIZATION_CODE`)；IAM（SigV4） |
| Lambda 函数 | `lambda-function-arn` | `none`（默认 — 通过网关角色直接调用），`oauth`（2LO）用于受保护的下游 | OAuth 3LO |
| OpenAPI 规范 | `open-api-schema` | `oauth`（2LO），`api-key`（必需 — 没有 `none`） | OAuth 3LO |
| AWS API Gateway | `api-gateway` | `none`，`api-key` | IAM (`GATEWAY_IAM_ROLE`) |
| Smithy 模型 | `smithy-model` | `oauth`（2LO） | IAM；OAuth 3LO |

**两种 OAuth 授权类型，而不是一种。** CLI 的 `--outbound-auth oauth` 仅配置**2 脚 OAuth**（客户端凭证 / M2M）。如果服务需要**3 脚 OAuth**（`AUTHORIZATION_CODE` 授权类型，用户委托访问），则没有 CLI 标志 — 您必须通过 boto3 / AWS SDK 配置目标。有关 [CreateGatewayTarget 文档](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway-building-adding-targets-authorization.html) 中的 `OAuthCredentialProvider`，`grantType: AUTHORIZATION_CODE` 和 `defaultReturnUrl`。3LO 适用于 MCP、Lambda、OpenAPI 和 Smithy 目标。在开始之前就指出这一点 — 需要使用 3LO 的开发人员否则会浪费一个回合尝试不存在的 CLI 标志。

**MCP 服务器（SigV4）** 配置通过 AWS SDK/API (`CreateGatewayTarget` 使用 `GATEWAY_IAM_ROLE` 凭证提供程序 + `iamCredentialProvider.service`)，而不是 CLI。它要求 MCP 服务器托管在原生验证 SigV4 的 AWS 服务后面：AgentCore 运行时、另一个 AgentCore 网关、Amazon API Gateway 或 Lambda Function URLs。ALB 或直接 EC2 端点不验证 SigV4 — 使用 OAuth 代替。([MCP 服务器目标认证策略](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway-target-MCPservers.html#gateway-target-MCPservers-considerations))

**MCP 服务器目标的 API 密钥认证** 在 API 层不适用 — 不仅仅是 CLI 上的差距。[MCP 服务器目标文档](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway-target-MCPservers.html#gateway-target-MCPservers-considerations) 列出了 MCP 目标支持的认证策略为“无认证”、“OAuth”和 IAM。如果 MCP 服务器使用 API 密钥（第三方 MCP 提供者的一个常见模式），请在代理代码中处理它（见路径 D）。

**认证选项会变化。** 如果上面的矩阵与 CLI 接受的内容不匹配，请检查当前的 CLI 帮助 (`agentcore add gateway-target --help`) 和 AWS 文档 — 每个目标类型的认证支持随版本发布而演变。如果 `awsknowledge` MCP 服务器可用，请搜索“AgentCore CreateGatewayTarget”以获取当前的 API 参数。

**CLI 与 API 的网关认证：** CLI 覆盖 `none`、`oauth`（2LO）和 `api-key`。对于 IAM（SigV4）和 3 脚 OAuth，请直接使用 boto3 — 示例在路径 A 部分中。一般模式：通过 CLI 创建网关和目标，部署，然后通过 boto3 应用高级认证，如果 CLI 不支持它。

在生成任何命令之前，告诉开发人员适用于其目标类型的认证选项。

### 当您的网关有许多工具时，让模型搜索它们

一旦网关中有超过一小堆工具——大约 20 多个——在每次回合都将每个工具定义传递给模型会浪费代币并降低准确性。当它只看到与当前请求相关的工具时，模型表现更好。

AgentCore 网关具有内置的语义搜索工具，正好用于此目的。您的代理调用名为 `x_amz_bedrock_agentcore_search` 的单个 MCP 工具，并带有自然语言查询，网关从其目录中返回最相关的工具。然后代理正常调用返回的工具。

如果开发人员正在考虑使用 Bedrock Knowledge Bases、向量存储或自定义嵌入构建自己的工具选择层 — 停止他们。网关已经执行了此操作，针对经过策划的相关性标准，无需管理基础设施。

使用模式（代理调用任何其他网关工具的方式相同）：

```python
# 通过 MCP 客户端，作为工具调用
result = await session.call_tool(
    "x_amz_bedrock_agentcore_search",
    arguments={"query": "查找与处理退款相关的工具"}
)
# result.content 列出了最相关的工具 — 代理然后调用它们
```

该功能适用于任何目标类型（Lambda、OpenAPI、MCP、API Gateway、Smithy）。按网关启用它 — 请参阅 [在您的 AgentCore 网关中搜索工具](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway-using-mcp-semantic-search.html) 文档以获取确切的 API 表面和特定于框架的客户端代码。

经验法则：如果网关有 20 多个工具，建议启用语义搜索。对于较小的目录，直接传递所有工具仍然可以。
