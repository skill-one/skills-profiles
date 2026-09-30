---
name: agents-debug
description: 当您的代理或环境出现问题时使用——包括错误答案、错误、超时、工具失败或CLI问题。读取跟踪记录和日志以诊断根本原因。当CLI本身无法工作时，还会检查先决条件。触发条件包括："代理无法工作"、"错误答案"、"代理错误"、"工具调用失败"、"调试代理"、"检查日志"、"读取跟踪记录"、"损坏"、"500错误"、"424错误"、"模型访问被拒绝"、"命令未找到"、"卡在DELETING状态"、"maxVms超出限制"、"冷启动诊断"、"冷启动缓慢"、"agentcore创建错误"、"创建失败"、"退出码7"、"本地开发连接被拒绝"。不适用于部署失败——请使用agents-deploy。不适用于无错误时的性能调优——请使用agents-optimize。不适用于VPC配置——请使用agents-build。不适用于可观测性设置或缺失日志——请使用agents-optimize。
---

# 调试

诊断您的 AgentCore 代理或环境为何无法正常工作。

## 何时使用

- 代理返回错误答案或错误
- 工具调用失败或超时
- 代理本地运行正常，但部署后失败
- 日志未在 CloudWatch 中显示
- AgentCore CLI 无法工作或环境似乎损坏
- 未找到 `agentcore` 命令或缺少先决条件

**不要**用于以下情况：

- 部署失败（CDK 错误，部署期间 IAM 问题）→ 使用 `agents-deploy`
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

## 流程

### 第 0 步：确定问题类型

如果开发人员的问题是关于 CLI 本身（命令未找到，先决条件，环境设置），请加载 [`references/doctor.md`](references/doctor.md) 并遵循其诊断清单。

如果问题是关于代理行为（错误答案，错误，超时，工具失败），请继续执行下文中的第 1 步。

### 第 1 步：验证 CLI 版本

运行 `agentcore --version`。此技能需要 v0.9.0 或更高版本。如果版本较旧，请告知开发人员在继续之前运行 `agentcore update`。

### 第 2 步：了解症状

询问（或从上下文中推断）：

> "发生了什么？
>
> 1. 代理返回错误消息
> 2. 代理返回错误或不相关的答案
> 3. 特定工具调用失败
> 4. 内存无法工作（代理不记得事情）
> 5. 代理运行缓慢或超时
> 6. 我想了解代理在特定会话中的操作"

### 第 3 步：自动读取跟踪记录和日志

不要要求开发人员粘贴日志 — 直接读取它们。

```bash
# 列出最近的跟踪记录
agentcore traces list --runtime <AgentName> --since 1h

# 获取最新的跟踪记录 ID
agentcore traces list --runtime <AgentName> --since 1h --limit 1

# 下载并读取跟踪记录
agentcore traces get <traceId> --runtime <AgentName>

# 搜索日志中的错误
agentcore logs --runtime <AgentName> --since 1h --level error

# 搜索特定模式的日志
agentcore logs --runtime <AgentName> --since 2h --query "timeout"
agentcore logs --runtime <AgentName> --since 2h --query "model access"
```

**重要提示：** CloudWatch 的 put-to-get 延迟为 **~10 秒端到端** — 这是从跟踪记录发出到 `agentcore traces get` 或 `agentcore run eval` 可读之间的延迟。没有单独的 "跟踪记录已接收但 eval 尚未准备就绪" 窗口；相同的接收步骤解锁了这两条路径。旧技能和文档称跟踪记录为 30–60 秒，评估为 2–5 分钟 — 这两者都已过时。如果您刚刚调用了代理，请等待 ~15 秒，跟踪记录读取和评估都将正常工作。

如果未提供代理名称，请读取 `agentcore/agentcore.json` 获取代理名称。

### 第 4 步：根据症状诊断

---

## 症状："model access denied" 或模型错误

**最常见的原因：** 模型在您的区域 Bedrock 控制台中未启用。

修复：

1. 前往 AWS 控制台 → Amazon Bedrock → 模型访问
2. 启用您的代理使用的模型
3. 等待 1–2 分钟以使访问生效

**第二原因：** 执行角色缺少 `bedrock:InvokeModel` 权限。

检查：

```bash
aws iam simulate-principal-policy \
  --policy-source-arn $(agentcore status --json | jq -r '.runtimes[0].executionRoleArn') \
  --action-names bedrock:InvokeModel \
  --resource-arns "arn:aws:bedrock:*::foundation-model/*"
```

**第三原因：** 跨区域推理配置文件需要在所有区域中启用模型访问。

以地理前缀开头的模型 ID 是跨区域推理配置文件，它们在该地理区域内路由请求：

| 前缀 | 地理区域 | 示例目标区域 |
|---|---|---|
| `us.` | 美国 | us-east-1, us-east-2, us-west-2 |
| `eu.` | 欧洲 | eu-central-1, eu-west-1, eu-west-2, eu-west-3 |
| `apac.` | 亚洲太平洋 | ap-northeast-1, ap-southeast-1, ap-southeast-2, ap-south-1 |
| `global.` | 全球所有商业区域 | 所有支持的区域 |

AgentCore CLI 默认创建 `global.`（例如，`global.anthropic.claude-sonnet-4-5-20250929-v1:0`）。所有前缀都需要在配置文件覆盖的所有目标区域中启用模型访问。对于 `us.` 配置文件，请在所有美国区域中启用；对于 `eu.`，所有欧盟区域；对于 `global.`，所有支持的区域。并非所有模型都支持所有前缀 — 目前 `global.` 仅适用于部分模型。当可用时，使用 `global.` 可获得最大吞吐量，或在数据驻留要求限制推理运行位置时使用地理前缀。检查 Bedrock 推理配置文件文档以获取当前模型 × 前缀的可用性。

---

## 症状：工具调用失败

**第 1 步：** 在跟踪记录中找到失败的工具调用：

```bash
agentcore traces get <traceId> --runtime <AgentName>
```

查找错误状态的工具调用条目。

**第 2 步：** 检查网关状态：

```bash
agentcore status --type gateway
agentcore fetch access --name <AgentName> --type agent
```

**第 3 步：** 常见的工具调用失败原因：

**网关 URL 未设置（本地开发）：**
`AGENTCORE_GATEWAY_*_URL` 环境变量仅在部署后设置。在 `agentcore dev` 中，网关工具不可用。这是预期的 — 代理应优雅地处理此问题。

**工具调用身份验证失败：**

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

跟踪记录显示了模型的推理步骤、调用的工具以及最终响应。查找：

- 代理是否使用了正确的工具？
- 工具调用是否返回了预期数据？
- 系统提示是否提供了正确的上下文？

**第 2 步：** 检查是否涉及内存：
如果代理应使用内存上下文但未使用，请查看本技能中稍后的“症状：内存无法持久化”部分，或如果这是环境问题，请加载 [`references/doctor.md`](references/doctor.md)。

**第 3 步：** 常见原因：

- 系统提示过于模糊或缺少关键上下文
- 代理未调用正确的工具（工具描述需要改进）
- 工具返回了意外的数据格式
- 模型 ID 不适用于任务（例如，使用较小的模型进行复杂推理）

---

## 症状：内存无法工作

**跨会话持久化内存（LTM）：**

1. 验证 LTM 策略是否配置（SEMANTIC 或 USER_PREFERENCE）：

```bash
agentcore status --type memory --json | jq '.memories[].strategies'
```

1. 会话结束后等待 5–30 秒 — LTM 提取是异步的。代理必须完成其会话才能提取事实。

2. 使用 UUID（v4）作为会话 ID — 平台要求至少 33 个字符。像 "session-1" 这样的短 ID 会导致 LTM 沉默失败。`agentcore invoke` 默认生成合规 ID。

3. 验证内存资源处于 ACTIVE 状态：

```bash
agentcore status --type memory
```

**会话开始时内存未加载：**

1. 检查 `MEMORY_*_ID` 环境变量是否设置：

```bash
agentcore status --type memory --json | jq '.memories[].id'
```

1. 验证 `actor_id` 在会话之间是否一致 — 内存按角色作用域划分。

2. 检查检索配置中的命名空间路径是否与写入时使用的命名空间匹配。

---

## 症状：代理超时

**第 1 步：** 检查跟踪记录以查看时间消耗在哪里：

```bash
agentcore traces get <traceId> --runtime <AgentName>
```

查找长时间运行的步骤 — 模型调用、工具调用、内存操作。

**第 2 步：** 常见超时原因：

**代理初始化缓慢：** 如果在空闲期间后的第一次调用缓慢但后续请求快速，代理在初始化上花费了太多时间。检查模块级别是否有重型导入、全局范围内的数据库连接或启动期间的 MCP 客户端初始化。将昂贵的设置移入请求处理程序或使用延迟初始化。有关优化指导，请参阅 `agents-harden` 技能。

**模型调用超时：** 模型运行时间过长。对于时间敏感操作，考虑使用更快的模型（例如，Haiku 代替 Sonnet 用于简单任务）。

**工具调用超时：** Lambda 或外部 API 运行缓慢。检查工具自身的日志。

**内存检索超时：** 对于大型内存存储，语义搜索可能很慢。考虑在检索配置中减少 `top_k`。

**VPC 连接问题：** 如果代理位于 VPC 中，请检查安全组规则和路由表。有关 VPC 特定调试信息，请参阅 `agents-build`（加载 [`references/vpc.md`](../agents-build/references/vpc.md)）。

---

## 症状：`ServiceQuotaExceededException: maxVms limit exceeded`（尽管观察到的并发量较低）

您的 CloudWatch "concurrent sessions" 指标显示适度数字（可能为 30–50），但 `InvokeAgentRuntime` 调用返回 `ServiceQuotaExceededException: maxVms limit exceeded`。

**实际情况：** CloudWatch 的并发会话指标与实时微 VM 数量不同。`maxVms` 配额计算您的账户中所有活动的环境 — 包括那些已完成调用但尚未被回收的环境。空闲但尚未被回收的环境会占用配额，直到 `idleRuntimeSessionTimeout` 过期（默认 900 秒 / 15 分钟）或您显式停止它们。

如果您的代码为每个请求使用新的会话 ID 且不调用 `StopRuntimeSession`，则每个请求都会在 15 分钟内留下一个空闲的环境，占用配额。

**修复顺序（按此顺序尝试，在请求配额增加之前）：**

1. **每次逻辑请求完成后调用 `StopRuntimeSession`。** 如果您不会在此会话上发送更多请求，请显式停止它。

   ```python
   client.stop_runtime_session(
       agentRuntimeArn=runtime_arn,
       runtimeSessionId=session_id,
   )
   ```

2. **跨相关请求重用会话 ID。** 如果用户交互产生多个后端调用，请将它们路由到同一会话，而不是为每个调用生成新的会话 ID。

3. **降低 `idleRuntimeSessionTimeout`。** 如果您的会话生命周期短，且无法在所有地方添加 `StopRuntimeSession`，请通过编辑 `agentcore/agentcore.json` 中的运行时 `lifecycleConfiguration` 并运行 `agentcore deploy` 来降低超时时间。

4. **以上操作后，再请求配额增加。** 请参阅 `agents-harden`（加载 [`references/limits.md`](../agents-harden/references/limits.md)） — 通过服务配额控制台（Amazon Bedrock AgentCore）请求，而不是直接提交支持工单。

请参阅 `agents-harden` 会话生命周期管理部分以获取完整模式。

---

## 症状：424 Failed Dependency on invoke

这通常意味着代理容器启动失败或在初始化期间崩溃。

**第 1 步：** 检查代理日志以查找启动错误：

```bash
agentcore logs --runtime <AgentName> --since 30m --level error
```

**第 2 步：** 常见原因：

**缺少 Python 依赖项：** 代理代码导入的包不在 `pyproject.toml` 中。容器启动正常，但在第一次请求时崩溃。修复：添加依赖项并重新部署。

**入口点崩溃：** `main.py` 在导入或 `app.run()` 时抛出异常。检查日志以获取堆栈跟踪。

**容器镜像拉取失败：** 如果使用容器构建，ECR 镜像可能不存在或执行角色缺少 `ecr:BatchGetImage`。检查：

```bash
agentcore status --runtime <AgentName> --json
```

**内存资源未处于 ACTIVE 状态：** 如果代理代码假设内存可用，但内存资源仍处于 CREATING 状态，入口点可能会失败。检查：

```bash
agentcore status --type memory
```

**初始化超时：** 代理准备就绪以接收第一个请求的时间过长 — 模块级别的重型导入、同步数据库连接或启动期间的 MCP 客户端初始化可能超出了服务的健康检查窗口。症状看起来像是在第一次调用时为 424，但在后续调用时正常。修复：将昂贵的设置移出模块级别，使用延迟初始化，或在生产流量之前预热代理。请参阅 `agents-harden` 初始化时间部分以获取模式。

---

## 症状：本地调用失败，显示 connection-refused / 退出代码 7

通常不是代理错误 — 开发人员服务器端口与您的预期不同。

**`agentcore dev` 绑定的默认端口：**

| 协议 | 默认 |
|---|---|
| HTTP | 8080 |
| MCP | 8000 |
| A2A | 9000 |

**当默认端口被占用时**（第二个开发会话，先前运行留下的悬空进程，8080 上有其他服务），CLI 会**自动递增**：8080 → 8081 → 8082。测试工具或 `curl` 脚本硬编码为 8080 将收到 `Connection refused`（curl 退出代码 7），而代理在 8082 上运行正常。

按以下顺序诊断：

1. 读取 `agentcore dev` 打印的 CLI 标记 — 它显示了实际绑定的端口和 URL。这是始终的真相来源。
2. 如果标记消失（终端清除，后台运行），请检查日志文件：

   ```bash
   tail -20 agentcore/.cli/logs/dev/*.log
   ```

3. 或直接找到进程：

   ```bash
   # macOS / Linux
   ps aux | grep -E 'agentcore dev|uvicorn' | grep -v grep
   lsof -iTCP -sTCP:LISTEN -n -P | grep -E '8080|8081|8082|8000|9000'
   ```

**修复选项：**

- 显式绑定端口：`agentcore dev --port 8080`
- 杀死占用默认端口的进程：`lsof -tiTCP:8080 -sTCP:LISTEN | xargs kill`
- 更新测试工具中硬编码的端口，以从 CLI 输出或环境变量读取

这也是“本地运行正常，但部署后失败”报告的常见来源 — 端口在运行之间发生变化。

---

## 症状：网关工具调用失败，显示身份验证错误

**第 1 步：** 验证身份验证类型是否与目标类型匹配。这是最常见的网关错误 — 使用了目标不正确的出站身份验证：

| 目标类型 | 有效的出站身份验证 |
|---|---|
| `mcp-server` | `none`, `oauth`, 或 IAM（通过 API 的 SigV4） |
| `lambda-function-arn` | 仅 IAM（自动） |
| `open-api-schema` | `oauth` 或 `api-key`（必需） |
| `api-gateway` | `none`, `api-key`, 或 IAM |
| `smithy-model` | IAM 或 `oauth` |

**第 2 步：** 检查 OAuth 令牌是否过期。如果网关目标使用 OAuth，访问令牌可能已过期。查找与身份验证相关的错误：

```bash
agentcore logs --runtime <AgentName> --since 1h --query "auth"
agentcore logs --runtime <AgentName> --since 1h --query "401"
agentcore logs --runtime <AgentName> --since 1h --query "403"
```

如果令牌正在过期，请验证 OAuth 凭证提供者的令牌端点是否可达，客户端凭证是否仍然有效。对于使用 OAuth 的 MCP 服务器目标，网关会自动处理令牌刷新 — 如果失败，凭证提供者配置可能不正确。

**第 3 步：** 检查凭证是否配置：

```bash
agentcore status --type credential
agentcore status --type gateway --json
```

---

## 症状：未出现跟踪记录

**等待 ~15 秒** — 调用和跟踪记录可用之间存在短延迟（通常为 ~10 秒）。

如果 ~30 秒后仍无跟踪记录：

1. 验证代理部署时启用了可观测性
2. 检查代理是否实际被调用：`agentcore logs --runtime <AgentName> --since 1h`
3. 检查执行角色的 CloudWatch 权限

---

## 症状：CloudWatch 日志未出现

这是最常见的可观测性问题，特别是对于容器/Docker 构建的。

AgentCore 不会捕获原始的 stdout。它使用 OpenTelemetry 将日志发送到 CloudWatch。必须满足以下三个条件：

**1. 你的入口点必须用 `opentelemetry-instrument` 包裹。**

CodeZip 构建会自动执行此操作。Docker/容器构建需要手动添加 — 这是人们最容易遗漏的第1件事。

在你的 Dockerfile CMD 中：

```dockerfile
# ✅ 正确 — 用 opentelemetry-instrument 包裹
CMD ["opentelemetry-instrument", "python", "main.py"]

# ❌ 错误 — 没有 OTEL 包裹，日志不会出现
CMD ["python", "main.py"]
```

**2. 你的运行时 IAM 角色需要 CloudWatch 和 X-Ray 权限：**

```
logs:CreateLogGroup
logs:CreateLogStream
logs:PutLogEvents    → 作用域限制为 /aws/bedrock-agentcore/runtimes/*
xray:PutTelemetryRecords
xray:PutTraceSegments → 作用域限制为 *
```

如果使用 AgentCore CLI 和 CodeZip，CDK 框架会自动添加这些权限。如果使用自定义角色或容器构建，请验证它们是否存在。

**3. 使用 Python 的 `logging` 模块，而不是 `print()`。**

OTEL 自动挂钩到 `logging` — 不需要自定义处理器。`print()` 语句不会出现在 CloudWatch 中。

```python
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# ✅ 这会出现在 CloudWatch 中
logger.info("处理请求")

# ❌ 这不会出现在 CloudWatch 中
print("处理请求")
```

**另外验证：** 确保你的账户中启用了 CloudWatch 事务搜索。如果没有，跟踪和跨度将不会出现在 GenAI 可观测性仪表板中。

### Terraform/CDK/IaC 部署的运行时日志缺失

常见模式：通过 Terraform、CDK 或自定义 IAM 角色部署的运行时工作正常（返回响应），但没有出现 CloudWatch 日志流 — 而相同代理代码通过 AgentCore 控制台部署的日志正常。

这几乎总是 IAM 作用域问题。通过控制台部署的运行时的执行角色默认具有广泛的 CloudWatch 权限。IaC 模板通常将权限狭义地限制为 `/aws/bedrock-agentcore/runtimes/*`，这会破坏日志流创建。

**修复方法：** `logs:DescribeLogGroups` 必须具有 `Resource: "*"`, 而不是作用域资源。其他日志操作可以作用域到运行时的日志组。

```json
{
  "Effect": "Allow",
  "Action": [
    "logs:DescribeLogGroups"
  ],
  "Resource": "*"
},
{
  "Effect": "Allow",
  "Action": [
    "logs:CreateLogGroup",
    "logs:CreateLogStream",
    "logs:PutLogEvents"
  ],
  "Resource": "arn:aws:logs:<REGION>:<ACCOUNT_ID>:log-group:/aws/bedrock-agentcore/runtimes/*:*"
}
```

更新执行角色的 IAM 策略后，使用 `agentcore deploy` 重新部署运行时以获取新权限。

---

## 症状：响应中途流连接断开

你的代理使用 SSE 或长轮询响应，连接在流中途断开。客户端代码中的症状：

- `RemoteProtocolError: peer closed connection without sending complete message body`
- 迭代流时出现 `IncompleteRead` 异常
- 沉默断开连接 — 无错误，无 `[DONE]` 事件，响应直接停止
- 发生在多工具使用对话中（5 次或更多顺序工具调用）
- 在客户端超时之前很久就失败

**根本原因：** 基础设施层的流连接空闲超时。如果响应流在几分钟内没有数据流（例如，工具执行时的沉默期），运行时前面的负载均衡器会终止 TCP 连接。

超时是针对**流中流动的数据**，而不是请求总持续时间。只要你定期发出字节，连接就会保持打开状态。

**修复方法：** 在长时间运行的工具执行期间发出保持活动状态事件。

Python 流式入口点模式：

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

        # 工具运行时发出心跳
        async for event in emit_keepalive(tool_task):
            yield event

        # 工具完成 — 发出实际结果
        result = await tool_task
        yield f"data: {json.dumps({'type': 'result', 'content': result})}\n\n"
        yield "data: [DONE]\n\n"

    return stream()
```

选择约 30 秒的心跳间隔。太长有风险触发空闲超时；太短会浪费带宽。

**在客户端端，在将字节展示给用户前过滤心跳事件：**

```python
for chunk in response.iter_lines():
    if not chunk:
        continue
    data = json.loads(chunk.removeprefix(b"data: "))
    if data.get("type") == "heartbeat":
        continue  # 忽略保持活动状态事件
    # 处理实际事件
```

**替代方案：** 使用 SDK 的异步任务 API 处理“发后即忘”模式。如果客户端不需要等待结果，通过 `add_async_task` / `complete_async_task` 注册工作并立即返回调用。见 `agents-harden` 长时间运行的后台任务部分。

---

## 症状：并发代理调用中的跟踪合并

你并行运行多个具有唯一 `runtimeSessionId` 值的代理调用，但 AI 可观测性仪表板将它们分组为单个会话 — 使其无法隔离单个运行。数据平面日志显示会话 ID 正确地 1:1 对应请求 ID，但跟踪视图仍然合并它们。

**最常见原因：** 调用者没有启用**主动跟踪**，因此上游跨度带有 `Sampled=0`。AgentCore 默认尊重上游跟踪采样决策。如果父上下文指示“不采样”，跨度会被丢弃，并发调用在仪表板中可能合并。

**按调用者类型修复：**

**Lambda 调用者：** 在 Lambda 函数上启用主动跟踪。

```bash
aws lambda update-function-configuration \
  --function-name my-caller-function \
  --tracing-config Mode=Active
```

或在 Lambda 控制台：配置 → 监控和操作工具 → AWS X-Ray → 主动跟踪。

**ECS / EC2 / 容器调用者：** 初始化 AWS X-Ray SDK 并确保对 AgentCore 的出站调用被instrument。对于 Python，使用 `aws-xray-sdk` 并修补 SDK：

```python
from aws_xray_sdk.core import xray_recorder, patch_all
patch_all()  # 补丁 boto3, requests 等
```

**没有 X-Ray 的直接 SDK 调用者：** 如果无法启用上游跟踪，通过在代理上设置环境变量强制运行时采样：

```
OTEL_TRACES_SAMPLER=always_on
```

这会使运行时无论父上下文的采样决策如何都采样每个跟踪。权衡：跟踪成本更高，但跟踪是正确的。

### 也检查：使用端点 ARN 而不是代理 ARN 调用

如果跟踪只显示单个顶层 `AgentCore.Runtime.Invoke` 跨度且没有子跨度，检查调用者使用的 ARN。调用目标应该是代理运行时 ARN：

```
arn:aws:bedrock-agentcore:<region>:<account>:runtime/<runtime-name>
```

而不是端点 ARN：

```
arn:aws:bedrock-agentcore:<region>:<account>:runtime/<runtime-name>/runtime-endpoint/DEFAULT
```

使用端点 ARN 可能会绕过完整的跟踪instrument路径。这是一个微妙的陷阱 — 两个 ARN 都会产生成功响应，但只有代理 ARN 产生完整跟踪。

---

## 症状：运行时卡在 DELETING 状态数小时

你调用了 `DeleteAgentRuntime`，收到成功响应 `status: DELETING`，但运行时已卡在这个状态超过 30 分钟。尝试单独删除默认端点会返回 `ConflictException: 当你删除代理时，默认端点会被移除。`

**发生的情况：** 删除工作流在服务端卡住。重试 `DeleteAgentRuntime` 无济于事 — 调用立即成功（返回 DELETING），但后端工作流卡住了。客户端工具无法强制完成它。

**该怎么做：**

1. **不要不断重试。** 它不会解除卡住的工作流。
2. **在 https://console.aws.amazon.com/support 打开一个 AWS 支持案例。** 包括：
   - AWS 账户 ID
   - 区域
   - 运行时 ARN（或 `agentRuntimeId`）
   - 原始 `DeleteAgentRuntime` 调用的 `requestId` 和时间戳（来自 CloudTrail）
   - 运行时卡在 DELETING 状态多长时间
3. **在同时期间绕过它。** 如果你需要继续发送，部署一个具有不同名称的新运行时。不要让卡住的资源阻塞你的工作。

来自卡住删除的遗弃资源（ENIs、工作负载身份）可能需要服务团队作为同一案例的一部分进行手动清理。

---

## 框架特定问题

**LangGraph — 模型格式：**
`langchain-aws` 的旧版本需要不带跨区域前缀的模型 ID。最新版本可能支持跨区域推理配置文件 — 检查你的安装版本：

```bash
pip show langchain-aws | grep Version
```

如果你在 LangGraph 中遇到模型错误，尝试非前缀 ID：

```python
# 如果你的 langchain-aws 版本存在跨区域前缀错误：
llm = init_chat_model("anthropic.claude-sonnet-4-5-20250929-v1:0", model_provider="bedrock_converse")

# 如果你的版本支持跨区域配置文件（us. = 美国, eu. = 欧洲, apac. = 亚洲太平洋, global. = 全球）：
llm = init_chat_model("global.anthropic.claude-sonnet-4-5-20250929-v1:0", ...)
```

参考当前 `langchain-aws` 发布说明：https://github.com/langchain-ai/langchain-aws/releases — 跨区域推理配置文件支持正在不断发展。

**Google ADK — 仅限 Gemini：**
ADK 仅适用于 Gemini 模型。如果你在 ADK 中遇到模型错误，请检查 `GEMINI_API_KEY` 是否设置且你正在使用 `gemini-*` 模型 ID。

**A2A 代理 — 端口错误：**
A2A 服务器必须运行在端口 9000 上。如果你的 A2A 代理没有响应，请检查它是否意外运行在 8080 上。

---

## 读取跟踪

跟踪显示一个代理调用的完整执行路径。关键部分：

- **模型调用** — 模型被要求做什么以及它如何响应
- **工具调用** — 调用了哪些工具，输入了什么，返回了什么
- **内存操作** — 从内存中读取和写入的内容
- **策略决策** — 允许或拒绝的内容（如果附加了策略引擎）
- **延迟分解** — 每个组件花费的时间

```bash
# 下载跟踪到文件以进行详细检查
agentcore traces get <traceId> --runtime <AgentName> --output trace.json
cat trace.json | jq '.trace.orchestrationTrace.modelInvocationOutput'
```

## 输出

- 具体故障诊断和根本原因
- 具体修复命令或代码更改
- 解释跟踪显示的内容（如果读取跟踪）
- 当修复超出调试范围时，转交给适当的技能

## 诊断后 — 转交

一旦你确定了根本原因，转交给拥有修复的技能：

| 根本原因 | 转交给 | 详情 |
|---|---|---|
| 内存配置错误（策略、命名空间、连接） | `agents-build` | 加载 [`references/memory.md`](../agents-build/references/memory.md) |
| 从应用调用代理不工作（认证、URL、流） | `agents-build` | 加载 [`references/integrate.md`](../agents-build/references/integrate.md) |
| VPC 连接（无法到达 RDS、无互联网、AZ 错误） | `agents-build` | 加载 [`references/vpc.md`](../agents-build/references/vpc.md) |
| 多代理委派不工作 | `agents-build` | 加载 [`references/multi-agent.md`](../agents-build/references/multi-agent.md) |
| 自定义请求头未到达代理代码 | `agents-build` | 加载 [`references/request-headers.md`](../agents-build/references/request-headers.md) |
| 跨账户从另一个账户中的应用调用 | `agents-build` | 加载 [`references/integrate.md`](../agents-build/references/integrate.md)（跨账户部分） |
| 网关认证配置错误（401、错误认证类型） | `agents-connect` | 网关认证矩阵 |
| 网关目标类型问题（Lambda vs OpenAPI vs MCP vs API Gateway） | `agents-connect` | “网关是什么和不是什么”部分 |
| 策略意外拒绝（Cedar、工具访问被拒绝） | `agents-connect` | 加载 [`references/policy.md`](../agents-connect/references/policy.md) |
| 可观测性未设置（无日志、无跟踪出现） | `agents-optimize` | 加载 [`references/observability.md`](../agents-optimize/references/observability.md) |
| 冷启动/初始化太慢 | `agents-harden` | 初始化时间部分 |
| 会话生命周期 / `maxVms` / `StopRuntimeSession` | `agents-harden` | 会话生命周期管理部分 |
| 长时间运行的后台任务被回收 | `agents-harden` | 长时间运行的后台任务部分 |
| JWT 入站认证失败（403、`allowedClients`/`allowedAudience`、发行者不匹配） | `agents-harden` | 入站认证部分 |
| 流量限制 / 配额错误 / 限制增加请求 | `agents-harden` | 加载 [`references/limits.md`](../agents-harden/references/limits.md) |
| 部署工件过时或版本错误 | `agents-deploy` | 重新部署工作流 |
| 环境损坏（CLI、凭证、Node、uv） | 加载 [`references/doctor.md`](references/doctor.md) | 本身包含在此技能中 |

清晰地说明诊断结果，然后告诉开发者下一步使用哪个技能。如果代理可以在同一会话中加载参考技能，请这样做。
