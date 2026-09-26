# harden

为您的 AgentCore 代理准备生产环境 — 安全性、可靠性和性能。

## 使用场景

- 您即将将代理部署到生产环境
- 您需要一个在发布前要检查的清单
- 您希望限制谁可以调用您的代理
- 您希望从默认值缩小 IAM 权限
- 您遇到了速率限制或配额错误（参考 [`references/limits.md`](references/limits.md)）
- 您需要调整会话生命周期以适应您的工作负载
- 您在代理中运行长时间运行的背景工作

## 输入

不需要任何参数。该技能读取您的项目配置并为您生成一个包含特定发现的清单。

## 流程

### 第 0 步：验证 CLI 版本

运行 `agentcore --version`。此技能需要 v0.9.0 或更高版本。如果版本较旧，请告诉开发人员在继续之前运行 `agentcore update`。

### 第 1 步：读取项目

读取 `agentcore/agentcore.json` 以了解：

- 配置了哪些资源（内存、网关、凭证、评估器）
- 正在使用哪个框架
- 配置的网络模式（PUBLIC 或 VPC）

### 第 2 步：运行清单

逐个检查每个类别并报告特定于项目的发现。

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

**运行时资源基于策略**（仅 API）：为了对可以调用您的运行时的主体进行更细粒度的控制（超出 IAM 角色和 JWT 认证提供的控制），请使用 `PutAgentRuntimeResourcePolicy` 通过 boto3。这不在 CLI 或 `agentcore.json` 中公开。如果可用，请使用 `awsknowledge` MCP 服务器查找当前的 API 形状。

---

## Shell 访问：单独缩小 `InvokeAgentRuntimeCommand` 权限

如果您的项目使用 `InvokeAgentRuntimeCommand`（参考 [`agents-build/references/integrate.md`](../agents-build/references/integrate.md)），请单独审计其 IAM 权限，而不是 `InvokeAgentRuntime`。这两个操作具有不同的影响范围：`InvokeAgentRuntimeCommand` 是在活动的微 VM 内执行的任意 shell 执行，具有运行时的完整执行角色 — 调用者可以读取/写入文件系统、访问代理可以访问的任何网络资源，并访问执行角色的凭证。

**检查哪些主体具有权限：**

```bash
# 列出您账户中的客户管理策略，然后检查每个策略以查看 InvokeAgentRuntimeCommand
aws iam list-policies --scope Local \
  --query 'Policies[*].[PolicyName, Arn, DefaultVersionId]' \
  --output table
# 然后，对于每个感兴趣的策略：
aws iam get-policy-version \
  --policy-arn <POLICY_ARN> \
  --version-id <VERSION_ID> \
  --query 'PolicyVersion.Document'
```

或者，使用 IAM 控制台：**IAM → 策略 → 按类型筛选：客户管理** → 在策略 JSON 编辑器中搜索 `InvokeAgentRuntimeCommand`。

**为命令调用者单独的 IAM 策略** — 与授予 `InvokeAgentRuntime` 的策略保持区分：

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

**如果命令是从调用代码中的任何地方构造的：** 在传递之前进行验证 — 拒绝包含 `&&`、`;`、`$(...)`、反引号、`|` 或其他 shell 保留字符的字符串。

---

## 入站认证：控制谁可以调用您的代理

默认情况下，代理使用 AWS IAM（SigV4）进行入站认证。对于生产环境，请验证此配置是否正确。

**检查当前的认证配置：**

```bash
agentcore status --runtime <AgentName> --json | jq '.runtimes[0].authorizerConfig'
```

**选项：**

`AWS_IAM`（默认） — 调用者必须使用 SigV4 签名请求。适用于内部服务和 AWS 原生客户端。

`CUSTOM_JWT` — 调用者提供来自您的身份提供者的 JWT。适用于 Web/移动应用和外部客户端。

```bash
agentcore add agent \
  --name MyAgent \
  --authorizer-type CUSTOM_JWT \
  --discovery-url https://your-idp.example.com/.well-known/openid-configuration \
  --allowed-audience my-api \
  --allowed-clients my-client-id
```

> [!WARNING]
> 生产环境中绝对不要使用 `--authorizer-type NONE`。它允许未经身份验证访问您的代理 — 任何拥有端点 URL 的人都可以调用它。始终使用 AWS_IAM 或 CUSTOM_JWT。如果您在生产环境中看到 NONE，请立即更改它。

### 选择 `allowedClients` 还是 `allowedAudience`

这是最常见的 JWT 配置错误。正确的选择取决于您的身份提供者签发的令牌中包含的内容。

**解码一个样本令牌**（在您的身份提供者处或使用 `jwt.io`）并查看负载：

- 令牌具有 `client_id` 声明，没有 `aud` 声明 → 在运行时配置 **`allowedClients`**
- 令牌具有 `aud` 声明 → 在运行时配置 **`allowedAudience`**
- 令牌两者都有 → 使用 `allowedAudience`。`aud` 声明是标准的 OIDC 受众字段；将其作为主要检查。

如果您选择了错误的一个，即使令牌有效，调用也会返回 403 — 运行时正在验证令牌没有的声明。

### 发行人 ↔ 发现 URL 前缀要求

AgentCore 强制执行 OIDC 发现规范（RFC 8414 §3）：发现文档中的 `issuer` 值必须是发现端点的 URL 前缀。

这意味着如果您的发现 URL 是 `https://qa.example.com/.well-known/openid-configuration`，该文档中的 `issuer` 字段必须以 `https://qa.example.com` 开头。如果文档宣传的发布者像 `https://example.com`（没有子域），则验证失败。

一些企业身份提供者（PingFederate、Paylocity、某些 Keycloak 设置）在特定于环境的子域上托管发现端点，同时宣传生产级别的发布者。这种模式与 RFC 8414 前缀规则不兼容。

修复选项：

1. **使 IdP 的发现端点与其发布者保持一致** — 从同一来源提供发现。
2. **将运行时指向实际的发现 URL 域** — 使用与令牌发布者匹配的子域配置运行时的发现 URL。

### 调试 JWT 认证失败

当调用失败并返回 403 时，缩小失败的检查。

**`Authorization method mismatch`** — 运行时的认证类型和请求的认证类型不匹配。两种情况：

- 运行时配置为 `AWS_IAM`（或无授权器），但调用者正在发送 Bearer 令牌 → 重新配置运行时为 `CUSTOM_JWT`，或者让调用者使用 SigV4。
- 运行时配置为 `CUSTOM_JWT`，但调用者的请求正在使用 SigV4 签名 → 可能是 SDK 或环境在出站请求中注入了 SigV4 标头与 Bearer 令牌一起。在出站请求中查找 `X-Amz-Date`、`X-Amz-Security-Token` 或 `Authorization: AWS4-HMAC-SHA256`。移除 SigV4 路径并仅发送 Bearer 令牌。

**`Invalid inbound token`**（或类似） — JWT 验证器拒绝了令牌。按顺序执行以下操作：

1. **发行人 ↔ 发现 URL 前缀**（如上所述） — 验证令牌的 `iss` 声明是否与发现 URL 的原点匹配
2. **`allowedClients` vs `allowedAudience`** — 运行时是否配置了适合您的令牌格式的正确声明？
3. **JWKS 可达性** — AgentCore 能否到达发现文档中列出的 `jwks_uri`？它必须公开可达。
4. **令牌过期** — 解码令牌，检查 `exp` 与当前时间
5. **签名算法支持** — 一些 IdP 使用算法（PS256、ES384 等）这些算法不是普遍支持的。检查您的 IdP 支持的算法，并在兼容性是问题的情况下切换到 RS256。

只有在排除了所有这些之后，您才应将其视为服务端问题。

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
        # 在内部记录完整的错误
        app.logger.error(f"Agent error: {e}", exc_info=True)
        # 向调用者返回一个安全消息
        return {"error": "An error occurred. Please try again."}

if __name__ == "__main__":
    app.run()
```

**检查：** 埋单的 `except` 块无声地吞没错误、错误消息向调用者暴露堆栈跟踪或内部详细信息、工具调用代码中缺少错误处理。

---

## 输入验证和速率限制

代理入口点接收来自调用者的任意有效负载。在处理之前进行验证：

```python
@app.entrypoint
def invoke(payload, context):
    prompt = payload.get("prompt", "")

    # 验证输入
    if not prompt or not isinstance(prompt, str):
        return {"error": "Missing or invalid 'prompt' field"}
    if len(prompt) > 10000:
        return {"error": "Prompt exceeds maximum length (10,000 characters)"}

    # 清理 — 删除控制字符、过多的空格
    prompt = " ".join(prompt.split())

    # 使用验证的输入继续
    result = agent(prompt)
    return {"response": str(result)}
```

**要验证的内容：**

- 必要字段是否存在且具有预期的类型
- 字符串输入不超过合理的长度限制（防止模型被 token-bombing）
- 数字输入在预期范围内
- 用户提供的 ID（actor_id、session_id）符合预期格式

**速率限制：** AgentCore 运行时具有内置的调用速率限制（默认每代理 25 TPS — 参考 [`references/limits.md`](references/limits.md)）。对于应用程序级别的速率限制（按用户、按租户），请在调用应用程序或 API Gateway 层中实现，而不是在代理代码本身中实现。代理应假定在请求到达它时已经被速率限制。

---

## 密钥：代码中无凭证，运行时环境变量中无密钥

要检查的两个故障模式：

### 1. 代理代码中硬编码的密钥

```bash
# 在代理代码中搜索常见的密钥模式
grep -r "sk-\|api_key\s*=\s*['\"]" app/ --include="*.py"
grep -r "password\s*=\s*['\"]" app/ --include="*.py"
```

### 2. 从运行时环境变量中拉取密钥

AgentCore 运行时环境变量是**不**受密钥保护的。任何开发人员通过 CDK、boto3 `UpdateAgentRuntime` 或类似方式放入运行时环境的任何内容都是明文配置值，不是密钥。审核以下模式：

```bash
# 标记任何 os.getenv / os.environ 调用，其名称暗示是密钥
grep -rE "os\.(getenv|environ).*(TOKEN|SECRET|KEY|PASSWORD|CREDENTIAL)" app/ --include="*.py"
```

平台注入的非密钥标识符是允许的，不应匹配允许列表（例如，`MEMORY_*_ID`、`AGENTCORE_GATEWAY_*_URL`、`AWS_REGION`、下游代理 ARN）。审核匹配项并确认它们不是密钥。

**正确模式：** 使用 `agentcore add credential` 注册每个出站凭证，然后在代码中通过集成的凭证提供程序获取它：

```python
from bedrock_agentcore.identity.auth import requires_api_key, requires_access_token

@requires_api_key(provider_name="MyAPI")
def call_api(payload: dict, *, api_key: str) -> dict:
    ...

@requires_access_token(provider_name="MyOAuthProvider", scopes=["read"], auth_flow="M2M")
async def call_downstream(data: dict, *, access_token: str) -> dict:
    ...
```

装饰器在调用时从 Secrets Manager 获取凭证并处理缓存/刷新。以这种方式注册的凭证在存储时是加密的，并且可以在不重新部署的情况下进行轮换。

**本地开发：** `agentcore/.env.local`（gitignored）被 `agentcore dev` 读取，以便装饰器本地解析。此文件**不会**在部署时上传到运行时 — 生产凭证存储在凭证提供程序中。

---

## 工具表面：优先使用网关目标而不是代理代码中的直接 HTTP 调用

相关的审核 — 对于代理调用的每个外部服务，询问它是否应该是网关目标而不是代理代码中隐藏的直接 HTTP 调用。网关的凭证提供程序在边缘注入认证（因此代理进程永远不会看到密钥），工具目录是可策略执行的，并且来自代理代码的泄露跟踪/日志行无法泄露代理代码从未到达的凭证。

```bash
# 在代理代码中查找直接出站 HTTP 调用
grep -rEn 'httpx\.|requests\.|aiohttp\.' app/ --include="*.py"
```

对于每个匹配项，决定：

| 匹配项看起来像 | 操作 |
|---|---|
| 调用一个外部 REST API，代理将其视为工具 | 作为网关目标前端（`agentcore add gateway-target --type open-api-schema` 或 `api-gateway`）。加载 [`agents-connect/SKILL.md`](../agents-connect/SKILL.md) 路径 C。 |
| 直接调用 MCP 服务器 | 作为网关目标前端（`--type mcp-server`）。加载 [`agents-connect/SKILL.md`](../agents-connect/SKILL.md) 路径 A。 |
| 调用 AWS 服务（S3、DynamoDB 等） — 不适合匹配此行，应使用 `boto3` | 从 `requests`/`httpx` 迁移到 `boto3` 客户端，使用运行时的执行角色进行 IAM。不需要凭证。 |
| 调用流式服务（SSE-with-live-output、WebSocket、WebRTC） | 可以保留直接调用 — 网关目前不前端这些。确认任何认证都使用 `@requires_*`，而不是 `os.getenv`。 |
| 通过 A2A 调用另一个代理 | 可以保留直接调用 — A2A 是设计为 HTTP。确认它使用 `@requires_access_token` 提供的 Bearer 令牌。 |
| 调用测量延迟的热路径，团队选择了它 | 可以保留，但确认测量存在，认证使用 `@requires_*`。 |

如果匹配项不属于“可以保留直接调用”的任何行，请打开工单将其转换为网关目标。对于大多数框架集成，网关目标可以在不更改代理代码的情况下添加。

---

## 可观察性：验证跟踪是否启用

AgentCore 自动启用 X-Ray 跟踪和 CloudWatch 日志。验证：

```bash
agentcore status --runtime <AgentName> --json | jq '.runtimes[0].observabilityConfig'
```

**CloudWatch 仪表板：** AWS 控制台 → CloudWatch → GenAI 可观察性 → Bedrock AgentCore

**日志保留：** 默认情况下，日志保留无限期。为成本控制设置保留策略：

```bash
aws logs put-retention-policy \
  --log-group-name /aws/bedrock-agentcore/runtimes/<AGENT_ID>-DEFAULT \
  --retention-in-days 30
```

---

## 评估基线：在发布前了解您的质量

在发布到生产环境之前，建立质量基线，以便您可以检测回归：

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

记录基线分数。如果分数在更改后显著下降，请在继续之前进行调查。

---

## 网络：VPC 用于私有资源

如果您的代理访问私有 AWS 资源（RDS、内部 API），请配置 VPC：

```bash
agentcore add agent \
  --name MyAgent \
  --network-mode VPC \
  --subnets subnet-abc,subnet-def \
  --security-groups sg-123
```

有关完整 VPC 配置指南，请参考 `agents-build`（加载 [`references/vpc.md`](../agents-build/references/vpc.md)）。

---

## 初始化时间：优化冷启动性能

代理初始化缓慢会导致超时、424 错误和糟糕的用户体验 — 特别是活动不活跃一段时间后第一次调用时。代理在准备好处理请求之前所做的每件事都会增加用户等待的时间。

### 冷启动时间实际花费

新环境的典型冷启动大约需要 20–30 秒。分解大致如下：

- **容器镜像拉取** — 对于容器构建占主导地位。一个 100 MB 的镜像需要几秒钟；一个 500 MB 的镜像可能需要 15+ 秒。
- **应用程序启动** — 您的代码的导入时间、框架初始化、模块级设置。通常 5–10 秒，如果导入时加载模型或打开连接，可能会更长。
- **平台开销**（微 VM 启动、网络附加、容器启动） — 亚秒到几秒钟。

您控制的两个是镜像大小和应用程序启动。优化这两者可以直接减少首次响应时间。

### 会话重用是最高的优化杠杆

同一会话的请求路由到已初始化的环境 — 没有冷启动。每个会话的第一个请求支付冷启动成本；该会话中的后续请求都很快。

具体模式：

- **多轮对话：** 在多轮之间重用相同的 `session_id`。不要为每轮生成一个新的 UUID。
- **批量处理：** 在批处理项之间重用相同的 `session_id`。
- **面向用户的界面：** 将会话范围限定于用户交互（例如，每个聊天对话一个会话），而不是每个消息一个会话。

跨 SDK 注意：如果您正在使用 MCP，请传递**一个**会话标识符，而不是同时传递 `runtimeSessionId` 和 `mcpSessionId`。发送两者可能导致平台将两个独立的环境绑定到同一个逻辑会话，使冷启动成本翻倍。

### 包大小预算

部署包的每 MB 都会增加冷启动时间。

- **目标：** 小于 200 MB。如果可能，目标小于 100 MB。
- **对于容器构建：** 多阶段 Dockerfile、精简或 distroless 基础镜像、删除构建工具和测试文件、添加 `.dockerignore`。
- **对于 CodeZip 构建：** 从 `pyproject.toml` / `requirements.txt` 中删除开发依赖项。不要发送 `tests/`、`docs/`、`.git/`、本地缓存。
- **定期审核：** `pip list`（Python）或 `npm ls`（Node）将显示实际安装的内容。删除您未使用的任何内容。

### 延迟初始化

不要在模块导入时加载大型模型、连接到数据库或初始化 MCP 客户端。每在模块导入中花费的一秒钟，代理都不能响应请求。

```python
# ❌ 慢 — 在代理可以处理请求之前运行
import heavy_library
client = heavy_library.Client(config)

# ✅ 快 — 延迟直到第一个请求
_client = None
def get_client():
    global _client
    if _client is None:
        import heavy_library
        _client = heavy_library.Client(config)
    return _client
```

### 根据流量模式选择部署类型，而不是默认值

之前建议在可能的情况下使用 CodeZip 考虑到容器。这是一个过度简化。以下是真正的权衡：

- **CodeZip：** 更容易迭代，更小的表面区域。冷启动包括代码下载 + 提取 — 一个 ~95 MB 的包在应用程序启动开始之前增加了大约 1.3 秒的平台下载时间。
- **容器：** 您控制完整的镜像，需要自定义系统依赖项。较大的镜像每次冷启动成本更高，但您可以通过多阶段构建进行激进优化。

两者都以会话重用和保持包小的相同方式受益。如果您的流量模式有大量突发冷会话，请投资于缩小您正在使用的部署工件。如果您的流量模式重用会话，部署类型的重要性要小得多。

### 对于 Gateway 背后的 Lambda 目标

在 Lambda 函数上使用配置并发性以消除 Lambda 冷启动。这是与运行时初始化分离的 — 它是 Lambda 本身，在冷 Lambda 的首次调用中添加延迟。

---

## 会话生命周期管理

会话管理与成本、性能和 `maxVms` 配额紧密相关。正确地执行它通常是成功生产发布与配额阻止之间的区别。

### 默认生命周期

当收到带有新会话 ID 的请求时，运行时为它初始化一个新的环境。该环境保持活动状态，直到以下任一情况发生：

1. **显式停止会话** — 通过 `StopRuntimeSession`。
2. **空闲超时过期。** 运行时回收未收到请求的环境，`idleRuntimeSessionTimeout`（默认 900 秒）。
3. **达到最大生命周期。** (`maxLifetime`, 默认 8 小时).

空闲环境计 against 您的 `maxVms` 配额，即使它们不提供服务流量。这是导致意外 `maxVms` 错误的首要原因。

### 根据工作负载形状选择超时

不要为生产环境保留默认值。选择与您实际使用会话匹配的值：

| 工作负载 | `idleRuntimeSessionTimeout` | `maxLifetime` | 理由 |
|---|---|---|---|
| 交互式聊天 / 支持代理 | 600–900s (默认) | 3600–7200s | 用户暂停阅读/思考。在他们离开后快速回收。 |
| 请求/回复 API，没有后续 | 60–120s | 1800s | 每个调用都是自包含的 — 快速释放 VM。 |
| 批量处理，每个作业一个会话 | 120s | 匹配作业长度 + 缓冲区 | 批处理项之间的空闲间隔很小；在作业之间激进地回收。 |
| 背景任务 / 长时间运行的任务（使用 `add_async_task`） | 120–300s | up to 28800s (8h) | 异步任务 API 在跟踪工作运行期间保持环境活跃；空闲超时适用于任务之间。 |

**一目了然的权衡：**

- **低空闲超时** = `maxVms` 在配额下有更多空间，成本较低。**风险：** 在对话中回收导致下一个回合冷启动。
- **高空闲超时** = 热回合，低延迟。**风险：** 空闲 VM 消耗配额；`maxVms` 错误在突发中。
- **低最大生命周期** = 可预测的回收，限制内存泄漏/陈旧状态。**风险：** 活跃长时间会话可能在流程中被打断。
- **高最大生命周期** = 粘性会话，大的热状态节省。**风险：** 漂移，陈旧内存状态，更难的发布。

### 最佳实践

**当工作完成时调用 `StopRuntimeSession`。** 如果您的代理完成一项任务并且不期望在该会话中接收更多请求，请显式停止它。这会立即释放环境，而不是等待空闲超时。

```python
# 在您的调用逻辑完成后，并且您知道会话已完成：
client.stop_runtime_session(
    agentRuntimeArn=runtime_arn,
    runtimeSessionId=session_id,
)
```

**重用会话 ID 以进行相关工作。** 每个HTTP请求使用新的会话 ID 意味着每个HTTP请求都有一个新初始化的环境。对于多轮对话、批量作业或面向用户的界面，每个对话/批量/用户交互使用一个会话 ID，并将所有相关请求路由到它。

**调整 `idleRuntimeSessionTimeout` 以适应您的工作负载。** 默认 900 秒适用于交互式工作负载，您期望快速后续请求。对于请求回复工作负载，会话很短，请降低它。

编辑 `agentcore/agentcore.json` 中运行时的条目：

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

然后 `agentcore deploy` 应用。CLI 和 CDK 处理底层的 `UpdateAgentRuntime` 调用。

如果您更喜欢 CLI，`agentcore add agent ... --idle-timeout 120 --max-lifetime 3600` 将相同的字段写入 `agentcore.json`。该文件是事实依据 — 文件中的每个字段都可以通过文件顶部的 `$schema` URL（`https://schema.agentcore.aws.dev/v1/agentcore.json`）获得 IDE 自动完成。

降低超时 = 更快的 VM 回收 = 在 `maxVms` 下有更多空间。太低 = 环境在对话中回收，导致下一个回合冷启动。

**不要传递 `runtimeSessionId` 和 `mcpSessionId` 一起。** 对于 MCP 代理，使用一个。传递两者可能导致两个独立的 VM 绑定到同一个逻辑会话。

### 诊断 `maxVms` 问题

如果您遇到 `ServiceQuotaExceededException: maxVms limit exceeded`，不要首先请求配额增加。CloudWatch 的并发会话指标与实际 VM 数量不同 — 空闲环境直到回收才计配额。

按以下顺序处理：

1. 在完成每个逻辑请求后调用 `StopRuntimeSession`
2. 审核会话 ID 生成 — 您是否为应该重用 ID 的请求创建了一个新的 ID？
3. 降低 `idleRuntimeSessionTimeout` 如果您的会话很短
4. 只有在完成以上所有操作后仍然遇到限制时，才应请求增加

参考 [`references/limits.md`](references/limits.md) 以获取增加请求的工作流程（通过服务配额控制台）和理由模板。

---

## 生产清单摘要

生成特定于项目的清单：

```
生产就绪清单 <AgentName>

IAM
[ ] 执行角色 Bedrock 访问缩小到特定模型 ARN
[ ] ECR 访问缩小到特定存储库
[ ] 信任策略缩小到您的账户 ID

认证
[ ] 入站认证是 AWS_IAM 或 CUSTOM_JWT（不是 NONE）
[ ] 如果 CUSTOM_JWT: 发现 URL、受众和客户端 ID 配置

Shell 访问（如果使用 InvokeAgentRuntimeCommand）
[ ] InvokeAgentRuntimeCommand 权限仅授予需要身份的主体
[ ] 独立的 IAM 策略与 InvokeAgentRuntime 策略区分
[ ] 启用 CloudTrail 报警。创建 EventBridge 规则，在调用 InvokeAgentRuntimeCommand 时通知您的安全团队

**如果命令是从调用代码中的任何地方构造的：** 在传递之前进行验证 — 拒绝包含 `&&`、`;`、`$(...)`、反引号、`|` 或其他 shell 保留字符的字符串。

代码质量
[ ] 错误处理包装所有代理逻辑
[ ] 输入验证在有效负载字段（类型、长度、格式）
[ ] 代码中无硬编码的密钥
[ ] 凭证通过 agentcore add credential 注册

可观察性
[ ] X-Ray 跟踪启用（自动配置）
[ ] CloudWatch 日志保留策略设置
[ ] 评估基线已建立

性能
[ ] 代理初始化时间测量和优化
[ ] 部署包大小小于 200 MB（目标小于 100 MB）
[ ] 依赖项审核 — 没有未使用的包
[ ] 依赖项清理 — 删除控制字符、过多的空格
[ ] 延迟初始化延迟到请求时间
[ ] 会话重用策略已为多轮/批量工作负载选择
[ ] `StopRuntimeSession` 在适用情况下调用
[ ] `idleRuntimeSessionTimeout` 调整为工作负载（默认 900s）
[ ] 对于长时间运行的背景任务：`add_async_task` / `complete_async_task` 使用

资源
[ ] 适当的内存策略（如果使用内存）
[ ] 网关认证配置（如果使用网关）
[ ] 策略引擎附加（如果限制工具访问）

测试
[ ] 使用生产代表性输入测试代理
[ ] 错误情况测试（工具失败、模型错误）
[ ] 内存跨会话测试（如果使用 LTM）
```

## 输出

- 包含项目特定发现的清单
- 修复任何发现问题的特定命令
- 推荐的 IAM 策略，检测到的模型和资源
