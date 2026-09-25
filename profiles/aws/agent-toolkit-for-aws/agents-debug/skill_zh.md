# 调试

诊断您的 AgentCore 代理或环境为何无法正常工作。

## 使用场景

- 代理返回错误答案或错误
- 工具调用失败或超时
- 代理本地运行正常，但在部署后失败
- 日志未在 CloudWatch 中显示
- AgentCore CLI 无法工作或环境似乎损坏
- 未找到 `agentcore` 命令或缺少先决条件

**不要**用于以下情况：

- 部署失败（CDK 错误，部署期间 IAM）→ 使用 `agents-deploy`
- 搭建新项目 → 使用 `agents-get-started`
- 衡量质量或设置监控 → 使用 `agents-optimize`

## 输入

`$ARGUMENTS` 是可选的：

```
/agents-debug                      # 交互式 — 描述问题所在
/agents-debug traces               # 读取并解释最近的跟踪记录
/agents-debug logs                 # 搜索最近的日志以查找错误
/agents-debug memory               # 专门诊断内存召回问题
/agents-debug doctor               # 检查环境先决条件
```

## 处理

### 第 0 步：确定问题类型

如果开发人员的问题是关于 CLI 本身（命令未找到，先决条件，环境设置），请加载 [`references/doctor.md`](references/doctor.md) 并遵循其诊断清单。

如果问题是关于代理行为（错误答案，错误，超时，工具失败），请继续执行第 1 步。

### 第 1 步：验证 CLI 版本

运行 `agentcore --version`。此技能需要 v0.9.0 或更高版本。如果版本较旧，请告诉开发人员在继续之前运行 `agentcore update`。

### 第 2 步：了解症状

询问（或从上下文中推断）：

> "发生了什么？
>
> 1. 代理返回错误消息
> 2. 代理返回错误或不相关的答案
> 3. 特定工具调用失败
> 4. 内存无法工作（代理不记得事情）
> 5. 代理运行缓慢或超时
> 6. 我想了解代理在特定会话中的行为"

### 第 3 步：自动读取跟踪记录和日志

不要要求开发人员粘贴日志 — 直接读取它们。

```bash
# 列出最近的跟踪记录
agentcore traces list --runtime <AgentName> --since 1h

# 获取最新的跟踪记录 ID
agentcore traces list --runtime <AgentName> --since 1h --limit 1

# 下载并读取跟踪记录
agentcore traces get <traceId> --runtime <AgentName>

# 搜索日志以查找错误
agentcore logs --runtime <AgentName> --since 1h --level error

# 搜索日志以查找特定模式
agentcore logs --runtime <AgentName> --since 2h --query "timeout"
agentcore logs --runtime <AgentName> --since 2h --query "model access"
```

**重要提示：** CloudWatch 的 put-to-get 延迟为 **~10 秒端到端** — 这是从跟踪记录发出到 `agentcore traces get` 或 `agentcore run eval` 可读之间的延迟。没有单独的“跟踪记录已摄入但 eval 未准备好”窗口；相同的摄入步骤解锁了这两条路径。旧技能和文档称跟踪记录为 30–60 秒，评估为 2–5 分钟 — 这都是过时的。如果您刚刚调用了代理，请等待 ~15 秒，跟踪记录读取和评估都将正常工作。

如果未提供代理名称，请读取 `agentcore/agentcore.json` 获取代理名称。

### 第 4 步：根据症状进行诊断

---

## 症状："model access denied" 或模型错误

**最常见的原因：** 模型在您的区域 Bedrock 控制台中未启用。

解决方法：

1. 前往 AWS 控制台 → Amazon Bedrock → 模型访问
2. 启用您的代理使用的模型
3. 等待 1–2 分钟以使访问生效

**第二个原因：** 执行角色缺少 `bedrock:InvokeModel`。

检查：

```bash
aws iam simulate-principal-policy \
  --policy-source-arn $(agentcore status --json | jq -r '.runtimes[0].executionRoleArn') \
  --action-names bedrock:InvokeModel \
  --resource-arns "arn:aws:bedrock:*::foundation-model/*"
```

**第三个原因：** 跨区域推理配置文件需要在所有区域中启用模型访问。

以地理前缀开头的模型 ID 是跨区域推理配置文件，它们在该地理区域内路由请求：

| 前缀 | 地理区域 | 示例目标区域 |
|---|---|---|
| `us.` | 美国 | us-east-1, us-east-2, us-west-2 |
| `eu.` | 欧洲 | eu-central-1, eu-west-1, eu-west-2, eu-west-3 |
| `apac.` | 亚洲太平洋 | ap-northeast-1, ap-southeast-1, ap-southeast-2, ap-south-1 |
| `global.` | 全球所有商业区域 | 所有支持区域 |

AgentCore CLI 默认使用 `global.` 搭建（例如，`global.anthropic.claude-sonnet-4-5-20250929-v1:0`）。所有前缀都需要在配置文件覆盖的所有目标区域中启用模型访问。对于 `us.` 配置文件，请在所有美国区域中启用；对于 `eu.`，所有欧盟区域；对于 `global.`，所有支持区域。并非所有模型都支持所有前缀 — `global.` 目前仅对某些模型可用。当可用时，使用 `global.` 可获得最大吞吐量，或者当数据驻留要求限制推理运行位置时，使用地理前缀。检查 Bedrock 推理配置文件文档以获取当前模型 × 前缀的可用性。

---

## 症状：工具调用失败

**第 1 步：** 在跟踪记录中找到失败的工具调用：

```bash
agentcore traces get <traceId> --runtime <AgentName>
```

查找具有错误状态的工具调用条目。

**第 2 步：** 检查网关状态：

```bash
agentcore status --type gateway
agentcore fetch access --name <AgentName> --type agent
```

**第 3 步：** 常见的工具调用失败：

**网关 URL 未设置（本地开发）：**
`AGENTCORE_GATEWAY_*_URL` 环境变量仅在部署后设置。在 `agentcore dev` 中，网关工具不可用。这是预期的 — 代理应优雅地处理此问题。

**工具调用上的身份验证失败：**

```bash
agentcore logs --runtime <AgentName> --since 1h --query "auth"
```

检查凭证是否配置正确：`agentcore status --type credential`

**Lambda 函数错误：**
Lambda 本身正在失败。直接检查 Lambda 日志：

```bash
aws logs tail /aws/lambda/<function-name> --since 1h
```

**策略拒绝：**
如果附加了策略引擎，请检查策略决策日志：

```bash
agentcore logs --runtime <AgentName> --since 1h --query "policy"
agentcore status --type policy-engine
```

---

## 症状：错误或不相关的答案

**第 1 步：** 读取跟踪记录以查看代理的推理过程：

```bash
agentcore traces get <traceId> --runtime <AgentName>
```

跟踪记录显示了模型的推理步骤、调用的工具和最终响应。查找：

- 代理是否使用了正确的工具？
- 工具调用是否返回了预期的数据？
- 系统提示是否提供了正确的上下文？

**第 2 步：** 检查是否涉及内存：
如果代理应使用内存上下文但未使用，请查看本技能中的“症状：内存无法持久化”部分，或者如果这是环境问题，请加载 [`references/doctor.md`](references/doctor.md)。

**第 3 步：** 常见原因：

- 系统提示过于模糊或缺少关键上下文
- 代理未调用正确的工具（工具描述需要改进）
- 工具返回意外的数据格式
- 模型 ID 不适合任务（例如，使用较小的模型进行复杂推理）

---

## 症状：内存无法工作

**跨会话内存不持久化（LTM）：**

1. 验证 LTM 策略是否配置（SEMANTIC 或 USER_PREFERENCE）：

```bash
agentcore status --type memory --json | jq '.memories[].strategies'
```

1. 会话结束后等待 5–30 秒 — LTM 提取是异步的。代理必须完成其会话才能提取事实。

2. 使用 UUID（v4）作为会话 ID — 平台要求会话 ID 最少为 33 个字符。像 "session-1" 这样的短 ID 会导致 LTM 沉默地失败。`agentcore invoke` 默认生成合规的 ID。

3. 验证内存资源处于活动状态：

```bash
agentcore status --type memory
```

**会话开始时内存未加载：**

1. 检查 `MEMORY_*_ID` 环境变量是否设置：

```bash
agentcore status --type memory --json | jq '.memories[].id'
```

1. 验证 `actor_id` 在会话之间是否一致 — 内存按角色作用域。

2. 检查检索配置中的命名空间路径是否与写入时使用的命名空间匹配。

---

## 症状：代理超时

**第 1 步：** 检查跟踪记录以查看时间消耗在哪里：

```bash
agentcore traces get <traceId> --runtime <AgentName>
```

查找长时间运行的步骤 — 模型调用、工具调用、内存操作。

**第 2 步：** 常见超时原因：

**代理初始化缓慢：** 如果在空闲期间后的第一次调用缓慢但后续请求快速，代理在初始化上花费了太多时间。检查模块级别是否有大量导入、全局作用域中的数据库连接或启动期间的 MCP 客户端初始化。将昂贵的设置移入请求处理程序或使用延迟初始化。有关优化指导，请参阅 `agents-harden` 技能。

**模型调用超时：** 模型花费时间过长。考虑使用更快的模型进行时间敏感操作（例如，使用 Haiku 而不是 Sonnet 进行简单任务）。

**工具调用超时：** Lambda 或外部 API 缓慢。检查工具自身的日志。

**内存检索超时：** 对于大型内存存储，语义搜索可能很慢。考虑在检索配置中减少 `top_k`。

**VPC 连接问题：** 如果代理位于 VPC 中，请检查安全组规则和路由表。有关特定于 VPC 的调试，请参阅 `agents-build`（加载 [`references/vpc.md`](../agents-build/references/vpc.md)）。

---

## 症状：`ServiceQuotaExceededException: maxVms limit exceeded`（尽管观察到并发性较低）

您的 CloudWatch "concurrent sessions" 指标显示适度数字（可能为 30–50），但 `InvokeAgentRuntime` 调用返回 `ServiceQuotaExceededException: maxVms limit exceeded`。

**实际发生的情况：** CloudWatch 的并发会话指标与实时微 VM 数量不同。`maxVms` 配额计算您的帐户中所有活动的环境 — 包括那些已完成调用但尚未回收的环境。空闲但尚未回收的环境直到 `idleRuntimeSessionTimeout` 过期（默认 900 秒 / 15 分钟）或您显式停止它们之前，都会计入配额。

如果您的代码为每个请求使用新的会话 ID 并且不调用 `StopRuntimeSession`，则每个请求都会留下一个空闲的环境，在 15 分钟内计入配额。

**解决顺序（按此顺序尝试，在请求配额增加之前）：**

1. **在每个逻辑请求完成后调用 `StopRuntimeSession`。** 如果您不会在此会话中发送更多请求，请显式停止它。

   ```python
   client.stop_runtime_session(
       agentRuntimeArn=runtime_arn,
       runtimeSessionId=session_id,
   )
   ```

2. **跨相关请求重用会话 ID。** 如果用户交互产生多个后端调用，请将它们路由到同一会话，而不是为每个调用生成新的会话 ID。

3. **降低 `idleRuntimeSessionTimeout`。** 如果您的会话很短，并且您无法在到处添加 `StopRuntimeSession`，请通过编辑 `agentcore/agentcore.json` 中的运行时 `lifecycleConfiguration` 并运行 `agentcore deploy` 来降低超时时间。

4. **在上述操作之后，才请求配额增加。** 请参阅 `agents-harden`（加载 [`references/limits.md`](../agents-harden/references/limits.md)）— 通过服务配额控制台（Amazon Bedrock AgentCore）请求，而不是直接通过支持票证提交。

有关会话生命周期管理的完整模式，请参阅 `agents-harden` 会话生命周期管理部分。

---

## 症状：在调用期间中间流式连接断开

您的代理使用 SSE 或长轮询响应，并且在响应流中间断开连接。客户端代码中的症状：

- `RemoteProtocolError: peer closed connection without sending complete message body`
- 在迭代流时出现 `IncompleteRead` 异常
- 沉默断开连接 — 没有错误，没有 `[DONE]` 事件，响应只是停止
- 发生在多工具使用对话中（5+ 顺序工具调用）
- 在客户端端超时之前很久就失败

**根本原因：** 基础设施层流式连接的空闲超时。如果响应流在几分钟内没有数据流（例如，在工具执行期间的沉默期），位于运行时前面的负载均衡器会终止 TCP 连接。

超时是 **流中数据流**，而不是请求总持续时间。只要您定期发出字节，连接就会保持打开状态。

**解决方法：** 在长时间运行的工具执行期间发出保持活动状态事件。**

Python 模式用于流式入口点：

```python
import asyncio
import json
from bedrock_agentcore.runtime import BedrockAgentCoreApp

app = BedrockAgentCoreApp()

async def emit_keepalive(tool_task):
    """在 tool_task 运行时每 30 秒生成心跳事件。"""
    while not tool_task.done():
        yield f"data: {json.dumps({'type': 'heartbeat'})}\n\n"
        try:
            await asyncio.wait_for(asyncio.shield(tool_task), timeout=30)
        except asyncio.TimeoutError:
            continue  # 工具仍在运行，发出另一个心跳

@app.entrypoint
async def invoke(payload, context):
    async def stream():
        tool_task = asyncio.create_task(run_long_tool(payload))

        # 在工具运行时发出心跳
        async for event in emit_keepalive(tool_task):
            yield event

        # 工具完成 — 发出实际结果
        result = await tool_task
        yield f"data: {json.dumps({'type': 'result', 'content': result})}\n\n"
        yield "data: [DONE]\n\n"

    return stream()
```

选择大约 30 秒的心跳间隔。太长有风险触发空闲超时；太短会浪费带宽。

**在客户端端，过滤心跳事件** 在将字节显示给用户之前：

```python
for chunk in response.iter_lines():
    if not chunk:
        continue
    data = json.loads(chunk.removeprefix(b"data: "))
    if data.get("type") == "heartbeat":
        continue  # 忽略保持活动状态
    # 处理实际事件
```

**替代方案：** 使用 SDK 的异步任务 API 进行火并忘模式。如果客户端不需要等待结果，请通过 `add_async_task` / `complete_async_task` 注册工作，并立即返回调用。有关详细信息，请参阅 `agents-harden` 长时间运行的背景任务部分。

---

## 症状：跟踪记录显示并发代理调用合并

您并行运行多个代理调用，并具有唯一的 `runtimeSessionId` 值，但 AI 可观察性仪表板将它们分组为单个会话，这使得无法隔离单个运行。数据平面日志显示会话 ID 与请求 ID 正确地 1:1 匹配，但跟踪记录视图仍然合并它们。

**最常见的原因：** 调用者未启用 **Active Tracing**，因此上游跟踪记录带有 `Sampled=0`。AgentCore 默认尊重上游跟踪记录采样决策。如果父上下文表示“不要采样”，则跟踪记录会被丢弃，并发起的代理可能看起来在仪表板中合并。

**根据调用者类型的解决方法：**

**Lambda 调用者：** 在 Lambda 函数上启用 Active Tracing。

```bash
aws lambda update-function-configuration \
  --function-name my-caller-function \
  --tracing-config Mode=Active
```

或者，在 Lambda 控制台中：配置 → 监控和操作工具 → AWS X-Ray → Active tracing。

**ECS / EC2 / 容器调用者：** 初始化 AWS X-Ray SDK 并确保对 AgentCore 的出站调用进行了仪器化。对于 Python，使用 `aws-xray-sdk` 并修补 SDK：

```python
from aws_xray_sdk.core import xray_recorder, patch_all
patch_all()  # 补丁 boto3, requests 等
```

**没有 X-Ray 的直接 SDK 调用者：** 如果您无法启用上游跟踪，请通过在代理上设置环境变量强制运行时采样：

```
OTEL_TRACES_SAMPLER=always_on
```

这会使运行时采样每个跟踪记录，而不管父上下文的采样决策如何。权衡：更高的跟踪成本，但跟踪记录是正确的。

### 还要检查：使用端点 ARN 而不是代理 ARN 调用

如果跟踪记录只显示单个顶层 `AgentCore.Runtime.Invoke` 跟踪记录，没有任何子跟踪记录，请检查调用者使用的 ARN。调用目标应该是代理运行时 ARN：

```
arn:aws:bedrock-agentcore:<region>:<account>:runtime/<runtime-name>
```

而不是端点 ARN：

```
arn:aws:bedrock-agentcore:<region>:<account>:runtime/<runtime-name>/runtime-endpoint/DEFAULT
```

使用端点 ARN 调用可能会绕过完整的跟踪记录仪器化路径。这是一个微妙的陷阱 — 两个 ARN 都会产生成功的响应，但只有代理 ARN 产生完整的跟踪记录。

---

## 读取跟踪记录

跟踪记录显示了单个代理调用的完整执行路径。关键部分：

- **模型调用** — 模型被要求做什么以及它如何响应
- **工具调用** — 调用了哪些工具，输入是什么，以及它们返回了什么
- **内存操作** — 从内存中读取和写入的内容
- **策略决策** — 允许或拒绝的内容（如果附加了策略引擎）
- **延迟分解** — 在每个组件中花费的时间

```bash
# 下载跟踪记录到文件以进行详细检查
agentcore traces get <traceId> --runtime <AgentName> --output trace.json
cat trace.json | jq '.trace.orchestrationTrace.modelInvocationOutput'
```

## 输出

- 特定失败的诊断和根本原因
- 具体的修复命令或代码更改
- 解释跟踪记录显示的内容（如果读取跟踪记录）
- 当修复超出调试范围时，转交给相应的技能

## 诊断后 — 转交

一旦您确定了根本原因，请转交给拥有修复的技能：

| 根本原因 | 转交给 | 详细信息 |
|---|---|---|
| 内存配置错误（错误的策略、命名空间、连接） | `agents-build` | 加载 [`references/memory.md`](../agents-build/references/memory.md) |
| 从应用调用代理不工作（身份验证、URL、流式传输） | `agents-build` | 加载 [`references/integrate.md`](../agents-build/references/integrate.md) |
| VPC 连接（无法到达 RDS、没有互联网、AZ 错误） | `agents-build` | 加载 [`references/vpc.md`](../agents-build/references/vpc.md) |
| 多代理委派不工作 | `agents-build` | 加载 [`references/multi-agent.md`](../agents-build/references/multi-agent.md) |
| 自定义请求头未到达代理代码 | `agents-build` | 加载 [`references/request-headers.md`](../agents-build/references/request-headers.md) |
| 跨帐户调用来自另一个帐户的应用 | `agents-build` | 加载 [`references/integrate.md`](../agents-build/references/integrate.md)（跨帐户部分） |
| 网关身份验证配置错误（401、错误的身份验证类型） | `agents-connect` | 网关身份验证矩阵 |
| 网关目标类型问题（Lambda 与 OpenAPI 与 MCP 与 API Gateway） | `agents-connect` | “网关是什么和不是”部分 |
| 策略意外拒绝（Cedar、工具访问被拒绝） | `agents-connect` | 加载 [`references/policy.md`](../agents-connect/references/policy.md) |
| 可观察性未设置（没有日志，没有跟踪记录出现） | `agents-optimize` | 加载 [`references/observability.md`](../agents-optimize/references/observability.md) |
| 冷启动 / 初始化太慢 | `agents-harden` | 初始化时间部分 |
| 会话生命周期 / `maxVms` / `StopRuntimeSession` | `agents-harden` | 会话生命周期管理部分 |
| 长时间运行的背景任务被回收 | `agents-harden` | 长时间运行的背景任务部分 |
| JWT 入站身份验证失败（403、`allowedClients`/`allowedAudience`、发行者不匹配） | `agents-harden` | 入站身份验证部分 |
| 限制 / 配额错误 / 限制增加请求 | `agents-harden` | 加载 [`references/limits.md`](../agents-harden/references/limits.md) |
| 部署 artifact 过期或版本错误 | `agents-deploy` | 重部署工作流 |
| 环境损坏（CLI、凭证、Node、uv） | 加载 [`references/doctor.md`](references/doctor.md) | 本技能自包含 |

清楚地说明诊断结果，然后告诉开发人员下一步要使用哪个技能。如果代理可以在同一会话中加载引用的技能，请这样做。
