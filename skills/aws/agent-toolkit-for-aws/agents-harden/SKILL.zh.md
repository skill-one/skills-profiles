---
name: agents-harden
description: 在准备将您的代理部署到生产环境时使用——包括 IAM 权限范围、入站认证（JWT、SigV4）、密钥管理、冷启动优化、会话生命周期、速率限制、输入验证和配额指导。触发条件包括："生产清单"、"加固代理"、"生产就绪"、"安全代理"、"入站认证"、"正式上线"、"冷启动优化"、"会话生命周期"、"StopRuntimeSession"、"配额"、"速率限制"、"安全审计出站 API 调用"、"生产网关目标审计"、"限制谁可以调用"、"锁定端点"、"仅允许我们的应用调用"。不适用于 Cedar 工具限制策略——请使用 agents-connect。不适用于质量测量——请使用 agents-optimize。不适用于出站凭证存储或 API 密钥配置——请使用 agents-connect。不适用于 A2A 代理间认证——请使用 agents-build。冷启动观察和诊断（非优化）路由至 agents-debug。
---

# harden

为您的 AgentCore 代理准备生产环境 — 安全性、可靠性和性能。

## 何时使用

- 您即将将代理投入生产
- 您需要一个在发布前要检查的清单
- 您希望限制谁可以调用您的代理
- 您希望从默认值缩小 IAM 权限范围
- 您遇到了速率限制或配额错误（参考 [`references/limits.md`](references/limits.md)）
- 您需要根据您的工作负载调整会话生命周期
- 您在代理中运行长时间运行的背景工作

## 输入

不需要任何参数。该技能读取您的项目配置，并为您生成一个包含针对您项目的具体发现的清单。

## 流程

### 第 0 步：验证 CLI 版本

运行 `agentcore --version`。此技能需要 v0.9.0 或更高版本。如果版本较旧，请告诉开发人员在继续之前运行 `agentcore update`。

### 第 1 步：读取项目

读取 `agentcore/agentcore.json` 以了解：

- 配置了哪些资源（内存、网关、凭证、评估器）
- 正在使用哪个框架
- 配置的网络模式（PUBLIC 或 VPC）

### 第 2 步：运行清单

逐个检查每个类别并报告针对您项目的具体发现。

---

## IAM：缩小权限范围

自动创建的执行角色具有广泛的 Bedrock 访问权限（`arn:aws:bedrock:*::foundation-model/*`）。对于生产环境，将其缩小到您的代理使用的特定模型。

**检查当前的执行角色：**

```bash
agentcore status --json | jq -r '.runtimes[0].executionRoleArn'
```

**推荐的 production Bedrock 策略：**

```json
{
  "Effect": "Allow",
  "Action": [
    "bedrock:InvokeModel",
    "bedrock:InvokeModelWithResponseStream"
  ],
  "Resource": [
    "arn:aws:bedrock:<REGION>::foundation-model/anthropic.claude-sonnet-4-5-20250929-v1:0"
  ]
}
```

将资源 ARN 替换为您代理使用的特定模型。

**ECR 访问：** 缩小到您的特定存储库：

```json
{
  "Effect": "Allow",
  "Action": ["ecr:BatchGetImage", "ecr:GetDownloadUrlForLayer"],
  "Resource": "arn:aws:ecr:<REGION>:<YOUR_ACCOUNT_ID>:repository/bedrock-agentcore-<AGENT_NAME>-*"
}
```

**信任策略：** 验证执行角色的信任策略是否缩小到您的账户：

```json
{
  "Principal": {"Service": "bedrock-agentcore.amazonaws.com"},
  "Action": "sts:AssumeRole",
  "Condition": {
    "StringEquals": {"aws:SourceAccount": "<YOUR_ACCOUNT_ID>"},
    "ArnLike": {"aws:SourceArn": "arn:aws:bedrock-agentcore:<REGION>:<YOUR_ACCOUNT_ID>:*"}
  }
}
```

**基于资源的运行时策略**（仅 API）：为了更精细地控制哪些主体可以调用您的运行时（超出 IAM 角色和 JWT 认证提供的范围），请使用 `PutAgentRuntimeResourcePolicy` 通过 boto3。这不在 CLI 或 `agentcore.json` 中公开。如果可用，请使用 `awsknowledge` MCP 服务器查找当前的 API 形状。

---

## Shell 访问：单独缩小 `InvokeAgentRuntimeCommand` 权限

如果您的项目使用 `InvokeAgentRuntimeCommand`（参考 [`agents-build/references/integrate.md`](../agents-build/references/integrate.md)），请将其 IAM 权限与 `InvokeAgentRuntime` 分开审计。这两个操作具有不同的影响范围：`InvokeAgentRuntimeCommand` 是在运行时的完整执行角色中执行的任意 shell 命令——调用者可以读取/写入文件系统、访问代理可以访问的任何网络资源，并访问执行角色的凭证。

**检查哪些主体具有权限：**

```bash
# 列出您账户中的客户管理策略，然后检查每个策略中的 InvokeAgentRuntimeCommand
aws iam list-policies --scope Local \
  --query 'Policies[*].[PolicyName, Arn, DefaultVersionId]' \
  --output table
# 然后针对每个感兴趣的策略：
aws iam get-policy-version \
  --policy-arn <POLICY_ARN> \
  --version-id <VERSION_ID> \
  --query 'PolicyVersion.Document'
```

或者，使用 IAM 控制台：**IAM → 策略 → 按类型筛选：客户管理** → 在策略 JSON 编辑器中搜索 `InvokeAgentRuntimeCommand`。

**为命令调用者设置单独的 IAM 策略**——与授予 `InvokeAgentRuntime` 的策略保持区分：

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": "bedrock-agentcore:InvokeAgentRuntimeCommand",
    "Resource": "arn:aws:bedrock-agentcore:<REGION>:<YOUR_ACCOUNT_ID>:runtime/<RUNTIME_NAME>-*"
  }]
}
```

**启用 CloudTrail 报警。** 创建一个 EventBridge 规则，在调用 `InvokeAgentRuntimeCommand` 时通知您的安全团队：

```bash
aws events put-rule \
  --name AgentCoreCommandExecution \
  --event-pattern '{"source":["aws.bedrock-agentcore"],"detail-type":["AWS API Call via CloudTrail"],"detail":{"eventName":["InvokeAgentRuntimeCommand"]}}' \
  --state ENABLED
```

**如果命令是从调用代码中的任何地方构造的：** 在传递之前进行验证——拒绝包含 `&&`、`;`、`$(...)`、反引号、`|` 或其他 shell 保留字符的字符串。

---

## 入站认证：控制谁可以调用您的代理

默认情况下，代理使用 AWS IAM（SigV4）进行入站认证。对于生产环境，请验证此配置是否正确。

**检查当前的认证配置：**

```bash
agentcore status --runtime <AgentName> --json | jq '.runtimes[0].authorizerConfig'
```

**选项：**

`AWS_IAM`（默认）——调用者必须使用 SigV4 签名请求。适用于内部服务和 AWS 原生客户端。

`CUSTOM_JWT`——调用者提供来自您的身份提供程序的 JWT。适用于 Web/移动应用和外部客户端。

```bash
agentcore add agent \
  --name MyAgent \
  --authorizer-type CUSTOM_JWT \
  --discovery-url https://your-idp.example.com/.well-known/openid-configuration \
  --allowed-audience my-api \
  --allowed-clients my-client-id
```

> [!WARNING]
> 生产环境中永远不要使用 `--authorizer-type NONE`。它允许未经身份验证访问您的代理——任何拥有端点 URL 的人都可以调用它。始终使用 AWS_IAM 或 CUSTOM_JWT。如果您在生产环境中看到 NONE，请立即更改它。

### 选择 `allowedClients` 还是 `allowedAudience`

这是最常见的 JWT 配置错误。正确的选择取决于您的身份提供程序发出的令牌中包含的内容。

**解码一个样本令牌**（在您的身份提供程序处或使用 `jwt.io`）并查看负载：

- 令牌具有 `client_id` 声明，没有 `aud` 声明 → 在运行时配置 **`allowedClients`**
- 令牌具有 `aud` 声明 → 在运行时配置 **`allowedAudience`**
- 令牌两者都有 → 使用 `allowedAudience`。`aud` 声明是标准的 OIDC 受众字段；使用该字段作为主要检查。

如果您选择了错误的一个，即使令牌有效，调用也会返回 403——运行时正在验证令牌没有的声明。

### Issuer 与发现 URL 前缀要求

AgentCore 强制 OIDC 发现规范（RFC 8414 §3）：发现文档中的 `issuer` 值必须是发现端点的 URL 前缀。

这意味着如果您的发现 URL 是 `https://qa.example.com/.well-known/openid-configuration`，该文档中的 `issuer` 字段必须以 `https://qa.example.com` 开头。如果文档宣传的发布者像 `https://example.com`（没有子域），则验证失败。

一些企业身份提供程序（PingFederate、Paylocity、某些 Keycloak 设置）在环境特定的子域上托管发现端点，同时宣传生产级别的发布者。这种模式与 RFC 8414 前缀规则不兼容。

修复选项：

1. **使 IdP 的发现端点与其发布者对齐**——从相同的来源提供发现。
2. **将运行时指向实际的发现 URL 域**——使用与令牌发布者匹配的子域配置运行时的发现 URL。

### 调试 JWT 认证失败

当调用失败并返回 403 时，缩小失败的检查。

**`Authorization method mismatch`**——运行时的认证类型和请求的认证类型不匹配。两种情况：

- 运行时配置为 `AWS_IAM`（或无认证器），但调用者正在发送 Bearer 令牌 → 重新配置运行时为 `CUSTOM_JWT`，或让调用者使用 SigV4。
- 运行时配置为 `CUSTOM_JWT`，但调用者的请求正在使用 SigV4 签名→ 可能是 SDK 或环境在出站请求中注入了 SigV4 标头和 Bearer 令牌。检查出站请求中是否有 `X-Amz-Date`、`X-Amz-Security-Token` 或 `Authorization: AWS4-HMAC-SHA256`。移除 SigV4 路径，仅发送 Bearer 令牌。

**`Invalid inbound token`**（或类似）——令牌被 JWT 验证器拒绝。按顺序检查这些：

1. **Issuer 与发现 URL 前缀**（如上所述）——验证令牌的 `iss` 声明是否与发现 URL 的原点匹配
2. **`allowedClients` vs `allowedAudience`**——运行时是否配置了与您的令牌格式匹配的正确声明？
3. **JWKS 可达性**——AgentCore 是否可以到达发现文档中列出的 `jwks_uri`？它必须公开可达。
4. **令牌过期**——解码令牌，检查 `exp` 与当前时间比较
5. **签名算法支持**——某些身份提供程序使用算法（PS256、ES384 等）这些算法并非普遍支持。检查您的身份提供程序支持的算法，并在兼容性是问题时切换到 RS256。

只有在排除了所有这些之后，才应将其视为服务端问题。

---

## 错误处理：优雅地失败

检查您的代理代码是否在不暴露内部详细信息的情况下处理错误：

```python
from bedrock_agentcore.runtime import BedrockAgentCoreApp

app = BedrockAgentCoreApp()

@app.entrypoint
def invoke(payload, context):
    try:
        # 您的代理逻辑
        return {"response": result}
    except Exception as e:
        # 在内部记录完整错误
        app.logger.error(f"Agent error: {e}", exc_info=True)
        # 向调用者返回安全消息
        return {"error": "An error occurred. Please try again."}

if __name__ == "__main__":
    app.run()
```

**检查：** 空的 `except` 块无声地吞下错误、向调用者暴露堆栈跟踪或内部详细信息的错误消息、工具调用代码中缺少错误处理。

---

## 输入验证和速率限制

代理入口点接收来自调用者的任意负载。在处理之前验证输入：

```python
@app.entrypoint
def invoke(payload, context):
    prompt = payload.get("prompt", "")

    # 验证输入
    if not prompt or not isinstance(prompt, str):
        return {"error": "Missing or invalid 'prompt' field"}
    if len(prompt) > 10000:
        return {"error": "Prompt exceeds maximum length (10,000 characters)"}

    # 清理——删除控制字符、过多的空白
    prompt = " ".join(prompt.split())

    # 使用验证的输入继续
    result = agent(prompt)
    return {"response": str(result)}
```

**要验证的内容：**

- 必填字段是否存在并具有预期的类型
- 字符串输入不超过合理的长度限制（防止向模型发送 token-bomb）
- 数字输入在预期范围内
- 用户提供的 ID（actor_id、session_id）符合预期格式

**速率限制：** AgentCore 运行时有内置的调用速率限制（默认每个代理 25 TPS——参考 [`references/limits.md`](references/limits.md)）。对于应用程序级别的速率限制（按用户、按租户），请在调用应用程序或 API Gateway 层中实现，而不是在代理代码本身中实现。代理应假定在请求到达它时，速率限制已经由调用方处理。

---

## 密钥：代码中无凭证，运行时环境变量中无密钥

两个需要检查的故障模式：

### 1. 代理代码中硬编码的密钥

```bash
# 在代理代码中搜索常见的密钥模式
grep -r "sk-\|api_key\s*=\s*['\"]" app/ --include="*.py"
grep -r "password\s*=\s*['\"]" app/ --include="*.py"
```

### 2. 从运行时环境变量中拉取的密钥

AgentCore 运行时环境变量是**不是**受密钥保护的。任何开发人员通过 CDK、boto3 `UpdateAgentRuntime` 或类似方式放入运行时环境中的任何内容都是明文配置值，而不是密钥。审计查找以下模式：

```bash
# 标记任何 os.getenv / os.environ 调用，其名称暗示是密钥
grep -rE "os\.(getenv|environ).*(TOKEN|SECRET|KEY|PASSWORD|CREDENTIAL)" app/ --include="*.py"
```

平台注入的非密钥标识符是允许的，不应与允许列表匹配（例如，`MEMORY_*_ID`、`AGENTCORE_GATEWAY_*_URL`、`AWS_REGION`、下游代理 ARNs）。检查匹配项并确认没有密钥。

**正确模式：** 使用 `agentcore add credential` 注册每个出站凭证，然后在代码中通过集成的凭证提供程序获取：

```python
from bedrock_agentcore.identity.auth import requires_api_key, requires_access_token

@requires_api_key(provider_name="MyAPI")
def call_api(payload: dict, *, api_key: str) -> dict:
    ...

@requires_access_token(provider_name="MyOAuthProvider", scopes=["read"], auth_flow="M2M")
async def call_downstream(data: dict, *, access_token: str) -> dict:
    ...
```

装饰器在调用时从 Secrets Manager 获取并处理缓存/刷新。以这种方式注册的凭证在存储时加密，无需重新部署即可旋转。

**本地开发：** `agentcore/.env.local`（git 忽略）由 `agentcore dev` 读取，以便装饰器本地解析。此文件**不会**在部署时上传到运行时——生产凭证存储在凭证提供程序中。

---

## 工具界面：优先使用网关目标而不是代理代码中的直接 HTTP 调用

相关审计——对于代理调用的每个外部服务，询问是否应将其作为网关目标而不是埋藏在代理代码中的直接 HTTP 调用。网关的凭证提供程序在边缘注入认证（因此代理进程永远不会看到密钥），工具目录是可策略执行的，并且从代理代码中泄露的堆栈跟踪/日志行无法泄露代理代码从未接触过的凭证。

```bash
# 在代理代码中查找直接出站 HTTP 调用
grep -rEn 'httpx\.|requests\.|aiohttp\.' app/ --include="*.py"
```

对于每个匹配项，决定：

| 匹配项看起来像 | 操作 |
|---|---|
| 调用代理视为工具的外部 REST API | 作为网关目标前端（`agentcore add gateway-target --type open-api-schema` 或 `api-gateway`）。加载 [`agents-connect/SKILL.md`](../agents-connect/SKILL.md) 路径 C。 |
| 直接调用 MCP 服务器 | 作为网关目标前端（`--type mcp-server`）。加载 [`agents-connect/SKILL.md`](../agents-connect/SKILL.md) 路径 A。 |
| 调用 AWS 服务（S3、DynamoDB 等）——不适用于此行，应使用 `boto3` | 从 `requests`/`httpx` 迁移到 `boto3` 客户端，使用运行时的执行角色进行 IAM。不需要凭证。 |
| 调用流式服务（SSE-with-live-output、WebSocket、WebRTC） | 可以保持直接——网关目前不转发这些。确认任何认证都使用 `@requires_*`，而不是 `os.getenv`。 |
| 通过 A2A 调用另一个代理 | 可以保持直接——A2A 设计为 HTTP。确认它使用 `@requires_access_token` 获取 Bearer 令牌。 |
| 调用经过测量的延迟热点路径，团队选择了它 | 可以，但确认测量存在并且认证使用 `@requires_*`。 |

如果匹配项不属于“可以保持直接”的任何行，请开一个工单将其转换为网关目标。对于大多数框架集成，添加网关目标不需要在代理中进行代码更改（MCP 工具发现处理绑定）。

---

## 可观察性：验证跟踪是否启用

AgentCore 自动启用 X-Ray 跟踪和 CloudWatch 日志。验证：

```bash
agentcore status --runtime <AgentName> --json | jq '.runtimes[0].observabilityConfig'
```

**CloudWatch 仪表板：** AWS 控制台 → CloudWatch → GenAI 可观察性 → Bedrock AgentCore

**日志保留：** 默认情况下，日志无限期保留。为成本控制设置保留策略：

```bash
aws logs put-retention-policy \
  --log-group-name /aws/bedrock-agentcore/runtimes/<AGENT_ID>-DEFAULT \
  --retention-in-days 30
```

---

## 评估基线：发布前了解您的质量

在投入生产之前，建立质量基线，以便您可以检测回归：

```bash
# 运行基线评估
agentcore run eval \
  --evaluator "Builtin.Helpfulness" \
  --evaluator "Builtin.GoalSuccessRate"

# 设置持续监控
agentcore add online-eval \
  --name production_monitor \
  --runtime <AgentName> \
  --evaluator "Builtin.Helpfulness" \
  --sampling-rate 5
agentcore deploy -y
```

记录基线分数。如果更改后分数显著下降，请在继续之前进行调查。

---

## 网络：VPC 用于私有资源

如果您的代理访问 AWS 私有资源（RDS、内部 API），请配置 VPC：

```bash
agentcore add agent \
  --name MyAgent \
  --network-mode VPC \
  --subnets subnet-abc,subnet-def \
  --security-groups sg-123
```

有关完整的 VPC 配置指南，请参阅 `agents-build`（加载 [`references/vpc.md`](../agents-build/references/vpc.md)）。

---

## 初始化时间：优化冷启动性能

代理初始化缓慢会导致超时、424 错误和糟糕的用户体验——尤其是在一段时间不活动后首次调用时。代理在准备好处理请求之前所做的任何操作都会增加用户等待的时间。

### 冷启动时间实际花费在哪里

新环境的典型冷启动大约需要 20–30 秒。分解大致如下：

- **容器镜像拉取** — 对于容器构建占主导地位。一个 100 MB 的镜像需要几秒钟；一个 500 MB 的镜像可能需要 15+ 秒。
- **应用程序启动** — 您代码的导入时间、框架初始化、模块级设置。通常为 5–10 秒，如果导入时加载模型或打开连接，则可能更长。
- **平台开销**（微 VM 启动、网络连接、容器启动）— 毫秒级到几秒钟。

您可以控制的是镜像大小和应用程序启动。优化其中任何一个都可以直接减少首次响应时间。

### 会话重用是最具杠杆的优化

相同会话的请求路由到已初始化的环境——无需冷启动。每个会话的第一个请求支付冷启动成本；该会话的后续请求都很快。

具体模式：

- **多轮对话**：跨回合重用相同的 `session_id`。不要每个回合生成一个新的 UUID。
- **批量处理**：跨批量项重用相同的 `session_id`。
- **面向用户的应用程序**：将会话范围限定于用户交互（例如，每个聊天对话一个会话），而不是每个消息一个会话。

跨 SDK 注意：如果您使用 MCP，请传递**一个**会话标识符，而不是同时传递 `runtimeSessionId` 和 `mcpSessionId`。发送两者可能会导致平台将两个独立的环境绑定到同一个逻辑会话，从而将冷启动成本加倍。

### 包大小预算

部署包的每 MB 都会增加冷启动时间。

- **目标**：小于 200 MB。如果可以，目标小于 100 MB。
- **对于容器构建**：多阶段 Dockerfile、精简或 distroless 基础镜像、移除构建工具和测试文件、添加 `.dockerignore`。
- **对于 CodeZip 构建**：从 `pyproject.toml` / `requirements.txt` 中删除开发依赖项。不要发送 `tests/`、`docs/`、`.git/`、本地缓存。
- **定期审计**：`pip list`（Python）或 `npm ls`（Node）将显示实际安装的内容。移除您未使用的任何内容。

### 推迟重初始化

不要在模块导入时加载大型模型、连接到数据库或初始化 MCP 客户端。模块导入中花费的每一秒都是代理无法响应请求的每一秒。

```python
# ❌ 慢——在代理可以处理请求之前在导入时运行
import heavy_library
client = heavy_library.Client(config)

# ✅ 快——推迟到第一个请求时
_client = None
def get_client():
    global _client
    if _client is None:
        import heavy_library
        _client = heavy_library.Client(config)
    return _client
```

### 根据流量模式选择部署类型，而不是默认值

之前建议在可能的情况下将 CodeZip 优于容器。这是一种过度简化。以下是真正的权衡：

- **CodeZip**：更易于迭代，表面更小。冷启动包括代码下载 + 解压——一个 ~95 MB 的包在应用程序启动开始之前会增加大约 1.3 秒的平台下载时间。
- **容器**：您可以控制完整的镜像，需要自定义系统依赖项。较大的镜像每次冷启动成本更高，但您可以通过多阶段构建进行激进优化。

两者都不是普遍适用。两者都以会话重用和保持包小的相同方式受益。如果您的流量模式有大量突发冷会话，请投资于缩小您正在使用的部署工件。如果您的流量模式重用会话，部署类型就不那么重要了。

### 对于 Gateway 背后的 Lambda 目标

在 Lambda 函数上使用预留并发以消除 Lambda 冷启动。这与运行时初始化是分开的——它是在冷 Lambda 的首次调用时添加延迟的 Lambda 本身。

---

## 会话生命周期管理

会话管理与成本、性能和 `maxVms` 配额紧密相关。正确处理这一点通常是平滑生产发布与配额阻塞之间的区别。

### 默认生命周期

当带有新的会话 ID 的请求到达时，运行时会为它初始化一个新鲜的环境。该环境保持活动状态，直到以下之一发生：

1. **显式停止会话**，通过 `StopRuntimeSession`。
2. **空闲超时到期**。运行时会回收未在 `idleRuntimeSessionTimeout`（默认 900 秒）期间收到请求的环境。
3. **达到最大生命周期**（`maxLifetime`，默认 8 小时）。

空闲环境会占用您的 `maxVms` 配额，直到被回收，即使它们没有提供服务流量。这是导致意外 `maxVms` 错误的首要原因。

### 根据工作负载形状选择超时

不要为生产保留默认值。选择与您的实际会话使用方式匹配的值：

| 工作负载 | `idleRuntimeSessionTimeout` | `maxLifetime` | 理由 |
|---|---|---|---|
| 交互式聊天 / 支持代理 | 600–900s（默认） | 3600–7200s | 用户暂停阅读/思考。在他们离开后快速回收。 |
| 请求/回复 API 没有后续操作 | 60–120s | 1800s | 每个调用都是自包含的——快速释放 VM。 |
| 批量处理，每个作业一个会话 | 120s | 匹配作业长度 + 缓冲区 | 批量项之间的空闲间隔很小；作业之间激进回收。 |
| 背景 / 长任务（使用 `add_async_task`） | 120–300s | 最高 28800s（8h） | 异步任务 API 在跟踪工作期间保持 VM 活跃；空闲超时适用于任务之间。 |

**一览权衡：**

- **低空闲超时** = `maxVms` 下更多空间，成本较低。**风险**：在对话中回收导致下一回合冷启动。
- **高空闲超时** = 热回合，低延迟。**风险**：空闲 VM 消耗配额；在突发中 `maxVms` 错误。
- **低最大生命周期** = 可预测的回收，限制内存泄漏 / 过期状态。**风险**：活动长会话在中间被杀死。
- **高最大生命周期** = 粘性会话，大的热状态节省。**风险**：漂移，内存中的过期状态，发布更难。

### 最佳实践

**当工作完成时调用 `StopRuntimeSession`。** 如果您的代理完成一项任务并且不期望在该会话上进行更多请求，请显式停止它。这会立即释放环境，而不是等待空闲超时。

```python
# 在您的调用逻辑完成后并且您知道会话已完成：
client.stop_runtime_session(
    agentRuntimeArn=runtime_arn,
    runtimeSessionId=session_id,
)
```

**重用会话 ID 用于相关工作。** 每个 HTTP 请求都有一个新会话 ID 意味着每个 HTTP 请求都有一个新环境。对于多轮对话、批量作业或面向用户的交互，为每个对话/批量/用户交互使用一个会话 ID，并将所有相关请求路由到它。

**根据工作负载调整 `idleRuntimeSessionTimeout`。** 默认的 900 秒适用于交互式工作负载，您期望快速后续请求。对于请求/回复工作负载，其中会话很短暂，请降低它。

编辑运行时的 `agentcore/agentcore.json` 中的条目：

```json
{
  "runtimes": [
    {
      "name": "MyAgent",
      "lifecycleConfiguration": {
        "idleRuntimeSessionTimeout": 120,
        "maxLifetime": 3600
      }
    }
  ]
}
```

然后 `agentcore deploy` 以应用。CLI 和 CDK 处理底层的 `UpdateAgentRuntime` 调用。

如果您更喜欢 CLI，`agentcore add agent ... --idle-timeout 120 --max-lifetime 3600` 将相同的字段写入 `agentcore.json`。该文件是真实来源——文件中的每个字段都可以通过文件顶部的 `$schema` URL（`https://schema.agentcore.aws.dev/v1/agentcore.json`）获得 IDE 自动完成。

降低超时 = 更快的 VM 回收 = `maxVms` 下更多空间。太低 = 环境在对话中回收，导致下一回合冷启动。

**不要同时传递 `runtimeSessionId` 和 `mcpSessionId`。** 对于 MCP 代理，使用一个。传递两者可能会导致两个独立 VM 绑定到同一个逻辑会话。

### 诊断 `maxVms` 问题

如果您遇到 `ServiceQuotaExceededException: maxVms limit exceeded`，请不要首先请求配额增加。CloudWatch 的并发会话指标与活动 VM 数不同——空闲环境会占用配额，直到被回收。

按顺序处理：

1. 在每个逻辑请求完成后调用 `StopRuntimeSession`
2. 审核会话 ID 生成——您是否为应该重用 ID 的请求创建了新 ID？
3. 如果您的会话很短暂，请降低 `idleRuntimeSessionTimeout`
4. 只有在完成以上所有内容并且仍然达到限制时，才请求增加

有关增加请求工作流程（通过服务配额控制台）和理由模板的副本粘贴，请参阅 [`references/limits.md`](references/limits.md)。

---

## 长时间运行的背景任务

如果您的代理触发的工作超出了 `/invocations` 响应的生存期——背景处理、异步作业、长工具链——一个“发射并忘记”的模式是不够的。环境可以在 `idleRuntimeSessionTimeout` 时被回收，即使您的背景任务仍在运行，因为运行时认为一旦发送调用响应，会话就空闲了。

### 使用 SDK 的异步任务 API 来指示“仍在忙”

bedrock-agentcore SDK 提供任务注册，它可以在跟踪工作运行时保持环境活跃。在 Python 中：

```python
from bedrock_agentcore.runtime import BedrockAgentCoreApp

app = BedrockAgentCoreApp()

@app.entrypoint
def invoke(payload, context):
    # 在启动它之前注册任务
    task_id = app.add_async_task("background_work")

    # 启动工作（在线程、asyncio 等）
    start_background_work(task_id, payload)

    # 返回调用响应——任务仍在跟踪
    return {"status": "processing", "taskId": task_id}


def start_background_work(task_id, payload):
    try:
        # 这里是长时间运行的工作
        do_the_work(payload)
    finally:
        # 完成时标记任务完成——这将释放“忙”信号
        app.complete_async_task(task_id)

if __name__ == "__main__":
    app.run()
```

在至少有一个注册的任务处于活动状态时，运行时将环境视为忙，并且不会在 `idleRuntimeSessionTimeout` 时回收它。`maxLifetime`（默认 8 小时）仍然适用作为硬上限。

检查您的语言 bedrock-agentcore SDK 文档以获取等效 API——TypeScript SDK 有一个类似的模式。

### 当异步任务 API 不可用时替代方案

- **将 `idleRuntimeSessionTimeout` 增加到与您的预期任务持续时间匹配。** 如果您知道任务运行长达 10 分钟，请将超时设置为 12 分钟。保持它远低于 `maxLifetime`。
- **保持 HTTP 连接打开** 使用流式响应并定期发出心跳事件。当您希望调用者等待结果而不是轮询时很有用。有关 SSE keepalive 模式，请参阅 [`agents-debug/SKILL.md`](../agents-debug/SKILL.md)（“流在中间断开”部分）。
- **将长工作跨多个调用分成多个** 在同一个会话上。每个调用都会重置空闲时钟。

---

## 配额和限制

如果您遇到限流、`ServiceQuotaExceededException` 或任何其他与配额相关的错误——或者您即将发布并希望确保配额不会阻止您——加载 [`references/limits.md`](references/limits.md)。

该参考涵盖：

- 每个错误映射到哪个配额
- 在请求增加之前尝试的缓解措施（关键——大多数“配额”错误实际上是会话生命周期问题）
- 如何通过服务配额控制台请求增加（边缘情况，其中直接支持案例是罕见的）
- 一个可复制粘贴的理由模板，包含审阅者需要批准的所有内容

---

## 生产清单摘要

生成特定于项目的清单：

```
<AgentName> 的生产就绪清单

IAM
[ ] 执行角色 Bedrock 访问范围限定为特定的模型 ARN
[ ] ECR 访问范围限定为特定的存储库
[ ] 信任策略范围限定为您的账户 ID

身份验证
[ ] 入站身份验证是 AWS_IAM 或 CUSTOM_JWT（不是 NONE）
[ ] 如果 CUSTOM_JWT：发现 URL、受众和客户端 ID 已配置

Shell 访问（如果使用 InvokeAgentRuntimeCommand）
[ ] 仅授予需要它的身份 `InvokeAgentRuntimeCommand` 权限
[ ] 将 `InvokeAgentRuntime` 策略与单独的 IAM 策略分开
[ ] 配置 CloudTrail / EventBridge 指令以记录 `InvokeAgentRuntimeCommand` 调用
[ ] 如果命令从用户输入构建：实现 shell 注入验证

代码质量
[ ] 所有代理逻辑都包装了错误处理
[ ] 对有效负载字段进行输入验证（类型、长度、格式）
[ ] 代理代码中没有硬编码的密钥
[ ] 通过 agentcore add credential 注册凭证

可观察性
[ ] 启用 X-Ray 跟踪（自动配置）
[ ] 设置 CloudWatch 日志保留策略
[ ] 建立评估基线

性能
[ ] 测量并优化代理初始化时间
[ ] 部署包大小小于 200 MB（目标小于 100 MB）
[ ] 审计依赖项——没有未使用的包
[ ] 将重初始化推迟到请求时间
[ ] 为多轮 / 批量工作负载选择会话重用策略
[ ] 在适用的情况下调用 `StopRuntimeSession` 完成工作
[ ] 调整 `idleRuntimeSessionTimeout` 以匹配工作负载（默认 900s）
[ ] 对于长时间运行的背景任务：使用 `add_async_task` / `complete_async_task`

资源
[ ] 适用于用例的内存策略（如果使用内存）
[ ] Gateway 身份验证配置（如果使用 gateway）
[ ] 连接策略引擎（如果限制工具访问）

测试
[ ] 使用生产代表性输入测试代理
[ ] 测试错误情况（工具故障、模型错误）
[ ] 测试跨会话内存（如果使用 LTM）
```

## 输出

- 具有项目特定发现的清单
- 修复发现的任何问题的特定命令
- 检测到的模型和资源的推荐 IAM 策略
