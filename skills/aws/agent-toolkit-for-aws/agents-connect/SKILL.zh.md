---
name: agents-connect
description: 在通过网关连接您的代理到外部API、工具或服务，或使用Cedar策略限制工具访问时使用。处理网关设置、目标类型、出站认证（OAuth、API密钥、IAM）、凭证以及Cedar策略编写。触发条件包括："连接到API"、"添加网关"、"连接到MCP服务器"、"Lambda工具"、"OpenAPI"、"网关目标"、"Cedar策略"、"限制工具"、"策略引擎"、"网关认证错误"、"存储API密钥"、"出站凭证"、"环境变量API密钥"、"部署后API密钥为空"、"部署后凭证不可用"、"是否应为网关目标"、"给我的代理工具"、"向代理添加工具"。不适用于入站认证（谁可以调用您的代理）——请使用agents-harden。不适用于调试代理行为——请使用agents-debug。不适用于VPC网络错误（代理因VPC无法访问API）——请使用agents-build。不适用于创建或托管新的MCP服务器项目——请使用agents-get-started。
---

# 连接

通过 AgentCore 网关为您的 AgentCore 代理访问外部 API、工具和服务提供接口 — 并使用 Cedar 策略控制其访问权限。

## 使用场景

- 您希望代理调用外部 API 或 MCP 服务器
- 您希望将 Lambda 函数作为代理工具公开
- 您有一个 OpenAPI 规范，希望将其转换为代理工具
- 您的代理需要凭证来调用外部服务
- 您希望限制代理可以调用的工具（Cedar 策略）
- 您希望对工具调用进行基于角色或基于金额的访问控制
- 网关连接、工具调用或策略授权失败

要添加 Cedar 策略以控制工具访问，请加载 [`references/policy.md`](references/policy.md)。

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

运行 `agentcore --version`。此技能需要 v0.9.0 或更高版本。如果版本较旧，请告知开发者在继续之前运行 `agentcore update`。

### 第 1 步：读取项目

读取 `agentcore/agentcore.json` 以了解：

- 项目使用的框架
- 已配置的网关和目标（在 `agentCoreGateways` 数组中）

**如果没有项目上下文：** 询问他们正在尝试连接什么，并使用相应的模式继续进行。

### 第 2 步：确定他们正在连接什么

询问（或从 `$ARGUMENTS` 推断）：

> "您正在将代理连接到什么？
>
> 1. 外部 MCP 服务器（例如，第三方工具提供者）
> 2. 您编写的 Lambda 函数
> 3. 具有 OpenAPI 规范的 API
> 4. AWS API Gateway REST API
> 5. 没有 OpenAPI 规范、MCP 服务器或 Lambda 作为前置的外部服务 — 并且您无法添加一个"

**选项 1–4 将服务作为网关目标前置。** 这是默认路径：网关通过其凭证提供者处理出站认证（因此代理代码永远不会看到密钥），工具通过 MCP 可发现，策略引擎可以在边缘授权或拒绝调用。选择与服务匹配的目标类型。

**选项 5 是路径 D** — 注册凭证并从代理代码直接调用 API。这是当前置不实用时的回退方案；当合适时，技能会引导您完成操作。

---

## 默认：优先选择网关目标而不是代码中的直接 API 调用

在深入路径之前，设定预期。大多数“我的代理需要调用 X”的请求都会落在网关目标上 — 而不是入口点中的 `httpx`。

**为什么网关是默认选择：**

- **边缘处的凭证注入。** 网关的凭证提供者（OAuth、API 密钥、IAM）将认证附加到出站请求。代理代码调用 `session.call_tool(...)` — 它永远不会接触密钥。执行 `client = openai.OpenAI(api_key=...)` 的代理代码距离泄露密钥只有一个提示/日志行/回溯。

- **可发现的工具目录。** 工具由 MCP 服务器列出；框架（Strands、LangGraph 等）自动绑定它们。添加工具是 `agentcore add gateway-target` + 重新部署，而不是代码更改。

- **策略执行。** Cedar 策略可以按主体、按工具、按参数值授权或拒绝工具调用。当工具调用隐藏在代理代码中的 `httpx.post(...)` 中时，这是不可能的。

- **语义搜索。** 一旦目录中有 20 多个工具，`x_amz_bedrock_agentcore_search` 会根据每次交互选择相关的工具。

**当代理代码中的直接 API 调用是正确答案时：**

| 情况 | 为什么网关不合适 | 应该做什么 |
|---|---|---|
| 流式传输/双向协议（SSE 带实时输出、WebSockets、WebRTC、长轮询） | 网关的 MCP 传输尚未支持这些 | 直接调用，路径 D |
| 延迟热点路径，其中 MCP 跳转是可测量的，并且权衡是可以接受的 | 额外的网络跳转 | 直接调用，路径 D，并附带决策依据的测量 |
| 商家专有协议/二进制 SDK | 网关没有 HTTP 表面来前置 | 直接使用商家 SDK，路径 D 用于任何密钥 |
| 通过 A2A 调用另一个代理 | A2A 是设计为 HTTP 并有其自身的认证模型 | [`agents-build/references/multi-agent.md`](../agents-build/references/multi-agent.md)，而不是网关目标 |
| 运行时已经具有 IAM 的 AWS 服务 SDK（S3、DynamoDB、SQS 等） | 没有前置认证 — 增加跳转 | 使用运行时的执行角色直接调用 boto3 |

对于**其他所有情况**，建议使用网关目标。如果开发人员坚持直接调用，请询问上述五个情况中哪个适用。如果没有，请将他们引导回网关目标。

**分类启发式：**

- 服务有 MCP 服务器 → 路径 A
- 服务是您控制的 Lambda 函数 → 路径 B
- 服务有 OpenAPI 规范（或者您可以生成一个 — FastAPI、ASP.NET、Spring 等 自动生成 OpenAPI）→ 路径 C
- 服务已经由 API Gateway 前置 → 路径 C (`--type api-gateway`)
- 以上都不符合，并且您无法添加一个 → 路径 D

---

## 网关是什么 — 以及它不是什么

在选择目标类型之前，确保正确的思维模型。大多数网关混淆来自于将其弄反。

**网关为您的代理托管工具以供调用。** 方向是：

```
您的代理  ───→  网关  ───→  Lambda 函数 / OpenAPI API / MCP 服务器 / Smithy 模型
             (代理调用工具)
```

代理是客户端。网关前置一个工具目录。每个工具是一个网关目标（Lambda、OpenAPI、MCP 服务器、API Gateway、Smithy）。

**网关不是一个用于代理的入站反向代理。** 如果您正在构建一个需要调用您的代理的应用，应用不会通过网关。方向是：

```
您的应用  ───→  AgentCore 运行时  (直接 invoke_agent_runtime 调用)
```

应用使用 IAM SigV4 签署调用或提供 JWT。有关应用端模式的更多信息，请参阅 [`agents-build/references/integrate.md`](../agents-build/references/integrate.md)。

### 当您不确定需要哪个方向时

问：**谁在调用谁？**

- "我的代理需要查找天气数据" → 代理在调用工具 → **网关目标**（此技能，路径 A/B/C）
- "我的 FastAPI 应用需要调用我的代理" → 应用在调用代理 → **直接调用**（不是网关；使用 [`agents-build/references/integrate.md`](../agents-build/references/integrate.md)）
- "我的代理需要从我的 FastAPI 应用获取数据" → 代理将应用作为工具调用 → **网关目标**，并将应用公开为 OpenAPI 或 REST 目标（使用您的 FastAPI 的 `/openapi.json` 的路径 C）

如果您发现自己配置了一个网关目标，其端点是 `bedrock-agentcore.<region>.amazonaws.com` 或指向您自己的运行时 URL，请停止 — 您已经弄反了流程。

### 适合您工具的目标类型

| 工具是什么 | 目标类型 | 备注 |
|---|---|---|
| MCP 服务器（第三方或您自己的） | `mcp-server` | 最常见的 MCP 工具目录 |
| 您编写的 AWS Lambda 函数 | `lambda-function-arn` | 自动使用 IAM 认证 |
| 具有 OpenAPI 规范的 HTTP API | `open-api-schema` | FastAPI 的内置 `/openapi.json` 可以工作 |
| AWS API Gateway REST API | `api-gateway` | 用于已经由 API Gateway 前置的 API |
| 具有 Smithy 模型的 AWS 服务 | `smithy-model` | 直接 AWS 服务集成 |

您的工具没有自然的 OpenAPI 规范，也不是 MCP 服务器或 Lambda？要么将其包装在 Lambda 中（最简单），为其生成 OpenAPI 规范（FastAPI 会自动生成），或者使用 API Gateway 前置它。

---

### 第 3 步：导航认证矩阵

**这是最常见的错误来源。** 认证选项取决于目标类型，而 CLI 仅暴露 API/SDK 支持的一小部分。

| 您正在连接什么 | CLI `--type` | 通过 CLI 的出站认证 | 通过 API/SDK 的其他选项 |
|---|---|---|---|
| 外部 MCP 服务器 | `mcp-server` | `none`、`oauth`（仅 2LO） | OAuth 3LO (`AUTHORIZATION_CODE`）；IAM（SigV4） |
| Lambda 函数 | `lambda-function-arn` | `none`（默认 — 通过网关角色直接调用），`oauth`（2LO）用于受 OAuth 保护的下级服务 | OAuth 3LO |
| OpenAPI 规范 | `open-api-schema` | `oauth`（2LO）、`api-key`（必需 — 没有 `none`） | OAuth 3LO |
| AWS API Gateway | `api-gateway` | `none`、`api-key` | IAM (`GATEWAY_IAM_ROLE`) |
| Smithy 模型 | `smithy-model` | `oauth`（2LO） | IAM；OAuth 3LO |

**两种 OAuth 授权类型，而不是一种。** CLI 的 `--outbound-auth oauth` 仅配置**两脚 OAuth**（客户端凭证 / M2M）。如果服务需要**三脚 OAuth**（`AUTHORIZATION_CODE` 授权类型，用户委托访问），则没有 CLI 标志 — 您必须通过 boto3 / AWS SDK 配置目标。有关 `OAuthCredentialProvider` 的文档，请参阅 [CreateGatewayTarget](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway-building-adding-targets-authorization.html) 的 `grantType: AUTHORIZATION_CODE` 和 `defaultReturnUrl`。3LO 适用于 MCP、Lambda、OpenAPI 和 Smithy 目标。从一开始就指出这一点 — 需要 3LO 的开发人员否则会浪费一个来回尝试不存在的 CLI 标志。

**MCP 服务器的 IAM（SigV4）** 通过 AWS SDK/API 配置（`CreateGatewayTarget` 使用 `GATEWAY_IAM_ROLE` 凭证提供者 + `iamCredentialProvider.service`），而不是 CLI。它需要 MCP 服务器托管在原生验证 SigV4 的 AWS 服务后面：AgentCore 运行时、AgentCore 网关、Amazon API Gateway 或 Lambda Function URLs。ALB 或直接 EC2 端点不会验证 SigV4 — 在那里使用 OAuth。([MCP 服务器目标认证策略](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway-target-MCPservers.html#gateway-target-MCPservers-considerations))

**MCP 服务器目标的 API 密钥认证在 API 级别不受支持** — 不仅仅是 CLI 上的差距。[MCP 服务器目标文档](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway-target-MCPservers.html#gateway-target-MCPservers-considerations) 列出了 MCP 目标仅支持“无授权”、“OAuth”和“IAM”作为支持的认证策略。如果 MCP 服务器使用 API 密钥（第三方 MCP 提供者的一个常见模式），请在代理代码中通过 Path D 处理。

**认证选项会变化。** 如果上面的矩阵与 CLI 接受的内容不匹配，请检查当前的 CLI 帮助 (`agentcore add gateway-target --help`) 和 AWS 文档 — 每个目标类型的认证支持随版本发布而演变。如果 `awsknowledge` MCP 服务器可用，请搜索“AgentCore CreateGatewayTarget”以获取当前的 API 参数。

**CLI 与 API 用于网关认证：** CLI 覆盖 `none`、`oauth`（2LO）和 `api-key`。对于 IAM（SigV4）和三脚 OAuth，请直接使用 boto3 — 示例在 Path A 部分中。一般模式：通过 CLI 创建网关和目标，部署，然后如果 CLI 不支持，通过 boto3 应用高级认证配置。

在生成任何命令之前，告知开发人员其目标类型的适用认证选项。

### 当您的网关有许多工具时，让模型搜索它们

一旦网关有超过一两个工具 — 大约 20 多个 — 在每次交互时传递每个工具定义到模型会浪费代币并降低准确性。当模型只看到与当前请求相关的工具时，它会表现更好。

AgentCore 网关有一个内置的语义搜索工具，正好用于此目的。您的代理调用名为 `x_amz_bedrock_agentcore_search` 的单个 MCP 工具，并附带自然语言查询，网关会从其目录中返回最相关的工具。然后代理正常调用返回的工具。

如果开发人员正在考虑使用 Bedrock Knowledge Bases、向量存储或自定义嵌入构建自己的工具选择层 — 请阻止他们。网关已经做了这件事，根据经过策展的相关性标准评估，无需管理任何基础设施。

使用模式（代理像调用任何其他网关工具一样调用它）：

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

- **三脚OAuth (`AUTHORIZATION_CODE`授权)** — 用户授权访问 — 由API支持，但没有CLI路径。通过boto3 `create_gateway_target`配置，设置`OAuthCredentialProvider.grantType = "AUTHORIZATION_CODE"`和`defaultReturnUrl`。参见[使用授权码流程连接到受OAuth保护的MCP服务器](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway-target-MCPservers.html#gateway-target-MCPservers-auth-code-grant-flow)。
- **IAM（SigV4）** 用于在AgentCore Runtime、另一个AgentCore网关、API Gateway或Lambda Function URLs上托管的MCP服务器，通过AWS SDK/API（非CLI）配置 — 使用`CreateGatewayTarget`与`GATEWAY_IAM_ROLE`凭证提供者和`iamCredentialProvider.service`值。
- **API密钥认证** 在API级别不支持MCP服务器目标（MCP目标文档仅列出无认证、OAuth和IAM作为策略）— 如果MCP服务器使用API密钥，直接在代理代码中处理（参见路径D）。

### 部署并获取网关URL

```bash
agentcore deploy -y
agentcore fetch access --name MyGateway
```

部署后，网关URL作为`AGENTCORE_GATEWAY_<NAME>_URL`注入。

### 生成网关客户端代码

**与框架无关的MCP客户端：**

```python
import os
import asyncio
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

# AgentCore部署后注入。格式：AGENTCORE_GATEWAY_<UPPERCASENAME>_URL
GATEWAY_URL = os.getenv("AGENTCORE_GATEWAY_MYGATEWAY_URL")

async def get_gateway_tools():
    """从网关发现工具。未部署时返回空列表。"""
    if not GATEWAY_URL:
        return []
    async with streamablehttp_client(GATEWAY_URL) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.list_tools()
            return result.tools

async def call_gateway_tool(tool_name: str, arguments: dict):
    """通过网关调用特定工具。"""
    if not GATEWAY_URL:
        raise RuntimeError("本地开发环境中网关不可用 — 请先部署")
    async with streamablehttp_client(GATEWAY_URL) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            return await session.call_tool(tool_name, arguments)
```

**对于Strands**，直接将网关工具传递给代理：

```python
from mcp.client.streamable_http import streamablehttp_client
from mcp import ClientSession
from strands import Agent
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from model.load import load_model  # scaffolded by `agentcore create`

app = BedrockAgentCoreApp()
GATEWAY_URL = os.getenv("AGENTCORE_GATEWAY_MYGATEWAY_URL")

@app.entrypoint
def invoke(payload, context):
    if not GATEWAY_URL:
        # 本地开发 — 无网关工具运行
        agent = Agent(model=load_model())
        return {"response": str(agent(payload.get("prompt", "")))}

    # 已部署 — 发现并使用网关工具
    tools = asyncio.run(get_gateway_tools())
    agent = Agent(
        model=load_model(),
        tools=tools,
    )
    return {"response": str(agent(payload.get("prompt", "")))}

if __name__ == "__main__":
    app.run()
```

**对于LangGraph**，将网关工具添加到工具节点：

```python
from langchain_mcp_adapters.client import MultiServerMCPClient

@app.entrypoint
def agent_invocation(payload, context):
    if not GATEWAY_URL:
        tools = []
    else:
        # 使用LangChain MCP适配器获取与LangChain兼容的工具
        client = MultiServerMCPClient({"gateway": {"url": GATEWAY_URL, "transport": "streamable_http"}})
        tools = asyncio.run(client.get_tools())

    llm_with_tools = llm.bind_tools(tools)
    # ... 剩余的LangGraph图 ...
```

---

## 路径B：Lambda函数作为工具

```bash
agentcore add gateway-target \
  --type lambda-function-arn \
  --name MyTools \
  --lambda-arn arn:aws:lambda:us-east-1:123456789012:function:my-tools \
  --tool-schema-file tools.json \
  --gateway MyGateway
```

`tools.json`定义工具模式：

```json
{
  "inlinePayload": [
    {
      "name": "get_weather",
      "description": "获取城市的当前天气",
      "inputSchema": {
        "type": "object",
        "properties": {
          "city": {"type": "string", "description": "城市名称"}
        },
        "required": ["city"]
      }
    }
  ]
}
```

**认证：** Lambda目标自动使用IAM角色认证 — 无需`--outbound-auth`标志。网关的执行角色需要在Lambda ARN上具有`lambda:InvokeFunction`权限。

使用与路径A相同的MCP客户端代码调用工具。

---

## 路径C：OpenAPI规范作为工具

```bash
# 从本地文件（API密钥认证）
agentcore add credential --name MyAPIKey --api-key sk-...

agentcore add gateway-target \
  --type open-api-schema \
  --name MyAPI \
  --schema specs/api.json \
  --gateway MyGateway \
  --outbound-auth api-key \
  --credential-name MyAPIKey
```

**OpenAPI目标需要认证** — 无论是`oauth`（客户端凭证或授权码）还是`api-key`。

⚠️ **安全提示：** `--api-key`会出现在shell历史记录中。更安全的选项：

1. **交互式提示（推荐）：** 运行`agentcore add credential --name MyAPIKey --type api-key`而不带`--api-key` — CLI会提示输入，值会直接进入凭证提供者（Secrets Manager后端）而不会触及你的shell历史记录。
2. **仅本地开发使用`agentcore.json` + `.env.local`：** 如果你需要在`agentcore dev`下工作，将值放入`agentcore/.env.local`（git忽略）。该文件仅被本地开发服务器读取 — 它**不会**部署到运行时。部署的运行时从凭证提供者在调用时获取值 — **永远不要**通过环境变量将凭证发送到部署的运行时。

**不要**尝试通过环境变量将凭证发送到部署的运行时 — AgentCore运行时环境变量不是密钥库后端。使用`agentcore add credential`注册一次凭证，并在网关目标或代码（路径D）中引用其名称。

---

## 路径D：代理代码中使用的凭证

直接在代理代码中调用API（非通过网关目标）。

### 在你选择路径D之前，检查是否确实需要路径D

路径D是**备选方案**，不是起点。对于大多数外部服务，网关目标（路径A–C）更安全且代码更少。在生成路径D代码之前，确认以下情况之一适用：

- 服务使用网关不支持的流式/双向协议（SSE带实时输出、WebSockets、WebRTC）
- 这是一个可测量的延迟关键热路径，团队已接受权衡
- 客户端是带有无HTTP表面的供应商二进制SDK
- 这是一个AWS服务SDK，运行时的执行角色已具有IAM权限（在这种情况下：直接使用SDK — 无需注册凭证）
- 开发者有特定障碍（例如，服务提供类似OpenAI的API，供应商SDK封装，重建SDK调用作为网关目标将是回归）

如果都不适用，返回路径A/B/C：

> "在我们为代理代码直接连接凭证之前，能否将其作为网关目标进行前端？网关在边缘注入凭证 — 你的代理代码永远不会接触密钥 — 并且工具成为策略可执行。如果SERVICE前面有OpenAPI规范、MCP服务器或Lambda函数，路径C / A / B是更好的选择。哪种适用？"

只有当开发者确认网关无效的合法理由时，才继续路径D。

### 注册凭证

```bash
# API密钥
agentcore add credential --name OpenAI --api-key sk-...

# OAuth（机器到机器）
agentcore add credential \
  --name MyOAuthProvider \
  --type oauth \
  --discovery-url https://idp.example.com/.well-known/openid-configuration \
  --client-id my-client-id \
  --client-secret my-client-secret \
  --scopes read,write
```

⚠️ **安全提示：** `--api-key`和`--client-secret`会出现在shell历史记录中。不带这些标志运行命令以获取交互式提示 — 值会直接进入凭证提供者而不会触及你的shell历史记录。

**仅本地开发**，将相同的值放入`agentcore/.env.local`（git忽略），以便`agentcore dev`可以本地解析装饰器。部署的运行时忽略`.env.local`，在调用时从凭证提供者获取密钥 — **永远不要**将密钥作为运行时环境变量发送。

### 在代理代码中使用凭证

使用`@requires_api_key`或`@requires_access_token`装饰器 — 它们自动处理令牌缓存和刷新。装饰器适用于同步和异步函数：

```python
from bedrock_agentcore.identity.auth import requires_api_key, requires_access_token

# 同步函数 — 装饰器通过关键字参数注入获取的密钥
@requires_api_key(provider_name="OpenAI")
def call_openai(prompt: str, *, api_key: str) -> str:
    import openai
    client = openai.OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

# 异步函数 — 相同装饰器，异步def
@requires_access_token(
    provider_name="MyOAuthProvider",
    scopes=["read", "write"],
    auth_flow="M2M",
)
async def call_my_api(data: dict, *, access_token: str) -> dict:
    import httpx
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.example.com/endpoint",
            headers={"Authorization": f"Bearer {access_token}"},
            json=data,
        )
        return response.json()
```

装饰器本身处理令牌生命周期 — 你不需要将函数变为异步仅为了使用它。参数是关键字仅（`*, api_key: str`或`*, access_token: str`）— 装饰器注入它们。

**本地开发：** 在`agentcore dev`中，凭证从`agentcore/.env.local`读取。装饰器模式在本地和部署时工作方式相同。

---

## 本地开发差距

> [!WARNING]
> 网关URL（AGENTCORE_GATEWAY_*_URL）仅在部署后可用。
> 在`agentcore dev`中，这些环境变量未设置。使用前始终检查：
>
> ```python
> GATEWAY_URL = os.getenv("AGENTCORE_GATEWAY_MYGATEWAY_URL")
> if not GATEWAY_URL:
>     # 本地开发中不使用网关工具
> ```
>
> 始终检查网关是否在本地可用。

---

## 故障排除

**"mcp-server目标不支持api-key认证"**
正确 — API密钥认证在API级别不支持MCP服务器目标（[MCP目标认证策略](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway-target-MCPservers.html#gateway-target-MCPservers-considerations)）。选项：OAuth（2LO或3LO）、IAM（对于在AgentCore Runtime、API Gateway或Lambda Function URLs上托管的MCP服务器）、或路径D — 在代理代码中管理凭证并直接调用MCP服务器。

**"我需要3LO / 授权码OAuth，但`--outbound-auth oauth`没有要求返回URL"**
CLI仅配置2LO（客户端凭证）。3脚OAuth需要boto3 — 调用`create_gateway_target`设置`credentialProviderType: OAUTH`、`grantType: AUTHORIZATION_CODE`和`defaultReturnUrl`。参见[使用授权码流程连接到受OAuth保护的MCP服务器](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway-target-MCPservers.html#gateway-target-MCPservers-auth-code-grant-flow)。

**"api-gateway目标不支持oauth"**
使用`api-key`或`none`配置API Gateway目标。

**部署后未设置网关URL**
运行`agentcore fetch access --name MyGateway`获取URL。检查`agentcore status --type gateway`验证网关是否部署。

**工具调用因认证错误失败**
检查`agentcore logs --runtime MyAgent --since 1h --level error`获取具体错误。常见原因：OAuth令牌过期、凭证名称错误、IAM权限缺失。

**"向现有代理添加网关"的解决方案**
CLI建议创建一个一次性代理来复制网关客户端代码。此技能直接生成代码 — 无需解决方案。

**MCP客户端（Claude Desktop、claude.ai）无法自动连接到网关**
AgentCore网关当前未实现MCP OAuth规范端点（RFC 8414 OAuth授权服务器元数据、RFC 7591动态客户端注册）。期望自动发现OAuth配置并自行注册的MCP客户端（如Claude Desktop和claude.ai）无法连接，除非手动配置凭证。解决方案是手动获取Cognito`client_id`和`client_secret`并在MCP客户端的高级设置中输入。这是一个平台限制，不是配置错误。
