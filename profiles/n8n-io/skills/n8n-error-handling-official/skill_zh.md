# n8n 错误处理

默认的 n8n 节点行为：错误 → 工作流中断 → 调用者什么都没得到。对于无人值守的工作流（webhook API、定时任务、队列工作器），这个默认行为是错误的。症状是“集成突然停止工作”，没有日志、没有消息、没有线索。

这项技能是关于处理错误，以便失败是响亮的、结构化的、可恢复的。或者最好的情况是，以自我修复的方式进行处理。

## 必须遵守的规则

对于任何**API 形式的流程**（webhook 触发器与 `响应 Webhook` 配合使用）：

1. **每个可能出错的节点的错误输出都被连接，并且两条路径都终止于 `响应 Webhook`。** 没有悬空的错误分支，否则调用者会看到超时。**可能出错** = HTTP、数据库、第三方 API、文件操作、任何会抛出异常的操作。
2. **状态码映射到原因。** 调用者的问题 → 4xx，你的问题 → 5xx。错误路径上的默认 200 会导致静默失败：调用者认为成功，处理空数据。

对于任何**无人值守的工作流**（定时、cron、队列驱动、代理工具）：

3. **设置工作流级别的错误工作流。** 捕获每个节点处理中遗漏的内容：超时、节点之间的崩溃、未连接节点的错误。通过 `update_workflow` `setWorkflowSettings.errorWorkflow`（n8n 2.29.0+）进行设置；目标必须是一个包含活动错误触发器已发布的流程，否则更新将被拒绝。参见 `references/ERROR_WORKFLOWS.md`。

## 强制性默认值

- **错误响应体是结构化的。** 不仅仅是“内部服务器错误”。使用 `{ "error": "<简短标识符>", "message": "<人类可读的>" }`。参见 `references/RESPONSE_SHAPES.md`。
- **进行网络调用的节点配置了 `retryOnFail`。** 瞬时 429 和上游波动会被吸收，在到达错误路径之前被处理。参见下文“瞬态失败的自我修复”。

## 错误处理可以宽松的情况

内部一次性工作流，只有你使用，你监控每个运行，失败的成本是“我注意到并重新运行”。默认 `onError: 'stopWorkflow'` 是可以的。如果除了你之外还有其他人看到输出（下游系统、最终用户、值班人员），则必须遵守强制性规则。

## API 工作流形状

标准的 webhook-API 工作流：

```
Webhook 触发器
  ├── (成功路径)  → 处理 → 响应 Webhook (200, 正文)
  └── (任何节点的错误输出)
                       → 响应 Webhook (5xx, 结构化错误正文)
                       → 可选：记录到错误追踪器 / 日志记录器 / 通知频道
```

有关如何将多个可能出错的节点连接到单个错误响应器的完整演练，请参见 `references/API_WORKFLOWS.md`。

## 模式验证器（设置 IIFE）

对于任何进行输入验证的 webhook API，将基于集合的模式验证器模式提升到端点中，而不是为每个字段编写 IF/Switch 链。两个示例文件是权威来源：

- `references/examples/validation-subworkflow.ts`：基本模式（Webhook → 设置包含验证 IIFE → 响应，表达式驱动的状态码）。可用作最小演示。
- `references/examples/validation-subworkflow-usage.ts`：端点模式（Webhook → 设置 → 如果有效 → 你的业务逻辑 → 200 成功 / 400 带有标准的 `{error: "validation_error", message, details, request_schema}` 正文）。将此模式提升到你的端点，并将 NoOp 占位符替换为实际逻辑。

**使用代理的步骤：**

1. **将使用示例结构提升到新端点。** Webhook → 设置（验证模式）→ 如果参数有效 → 你的逻辑 → 成功/400 响应。不要重新发明。
2. **编辑你的模式的 IIFE。** 更新 `REQUIRED_SCHEMA` 和 Set 节点表达式中的每个字段检查（对于你的端点输入形状）。模式常数下方的模式是机械的：存在性检查、类型检查、约束检查、推送到 `errors[]`。
3. **保持输出形状不变。** `valid`, `validationError`, `details`, `requiredSchema` 是响应节点消费的合同。重命名它们会破坏响应正文。

完整步骤、支持的限制模式、模式设计规则以及 `={{ ... }}` 包装陷阱都在 `references/API_WORKFLOWS.md` “模式验证器（设置 IIFE）”中。

## 每个节点的错误设置（回顾）

每个可能出错的节点需要两个更改（参见 `references/NODE_ERROR_OUTPUTS.md`）：

1. **在节点配置中设置 `onError: 'continueErrorOutput'`。**
2. **将 `output(1)` 连接到你的错误处理程序。**

两者都是必需的。缺少任何一个都会导致静默失败。

## 瞬态失败的自我修复

在连接错误路径之前，配置任何进行网络调用的节点（HTTP 请求、Gmail/Slack/Discord 等通信、数据库、AI、第三方 API 节点）的节点级重试。瞬态 429 和短暂的上游波动会被吸收，因此错误输出仅在真实失败时触发，并且警报和 5xx 响应反映实际问题而不是噪音。

```ts
{
    retryOnFail: true,
    maxTries: 3,
    waitBetweenTries: 5000,    // ms; 5000 是最大值，应作为默认值
}
```

适用于任何调用网络服务的节点，而不仅仅是 HTTP 请求。引擎在 *任何* 错误时重试，没有按状态码过滤，并且引擎将 `maxTries` 限制为 5，将 `waitBetweenTries` 限制为 5000ms（`packages/core/src/execution-engine/workflow-execute.ts`）。参见 `n8n-node-configuration-official` `HTTP_NODES.md` 和 `AI_NODES.md` 的节点特定说明。

## 响应形状：将原因映射到状态码

带有 `text/plain "Internal Server Error"` 的 5xx 响应在技术上可能是 5xx 但无用处。并且并非每个错误都是 5xx。将状态码与请求失败的原因匹配。

**常见错误：** 将每个错误路径连接到返回 500 "internal_error" 的单个 `响应 Webhook`。每个失败对调用者来说看起来都一样，即使他们发送了错误输入。破坏监控：你无法区分真实故障与调用者输入错误。

**按原因的默认映射：**

| 原因 | 状态 | 错误代码 | 路径 |
|---|---|---|---|
| 必须字段缺失或类型错误 | 400 | `validation_error` | 在前面使用基于集合的模式验证器进行验证（参见 `references/examples/validation-subworkflow.ts` 的基本模式和 `validation-subworkflow-usage.ts` 的端点模板），或者对于简单情况，使用内联 IF/Switch + 专门的 400 响应。不要通过错误输出。理想情况下，在响应中回显模式，以便调用者可以自我纠正。 |
| 认证缺失或无效 | 401 | `unauthorized` | 同上。提前检查，直接返回 401。 |
| 认证通过但无权限 | 403 | `forbidden` | 同上。 |
| 请求中的资源 ID 存在，但在你的数据中不存在 | 404 | `not_found` | 从查找结果分支，而不是查找错误。 |
| 操作与当前状态冲突（重复、竞争） | 409 | `conflict` | 通过逻辑检测，而不是错误输出。 |
| 调用者超出速率限制 | 429 | `rate_limit_exceeded` | 设置 `Retry-After` 标头。 |
| 节点抛出且你不知道原因 | 500 | `internal_error` | 错误输出路径。 |
| 第三方 API 出错 | 502 | `upstream_error` | HTTP 请求节点的错误输出。 |
| 工作流当前无法处理（下游系统故障、速率限制的上游） | 503 | `service_unavailable` | 通过特定错误检测，并带有提示返回。 |
| 第三方 API 超时 | 504 | `upstream_timeout` | 错误输出按错误消息过滤。 |

**两个不同的流程：**

- **验证失败（4xx）** 是在流程上游通过 IF/Switch 分支检查的，而不是错误输出。使用每个形状的专用响应（400 缺失字段、401 无认证等）。
- **执行失败（5xx）** 来自错误输出（“我们尝试了，某处出了问题”）。一个用于所有 5xx 的错误响应器是足够的。通过检查有用的失败节点来区分正文中的 `error` 代码。

**一个响应，表达式驱动的状态码。** 当错误路径仅通过状态码和消息文本不同（相同的正文形状，没有标头/内容类型更改）时，不要通过 Switch 分支到 N 个响应节点。`响应 Webhook` 节点接受其 `Response Code` 和正文字段中的表达式。内联计算代码，因此一个响应节点承载整个错误路径。

```ts
// 单个响应 Webhook 节点的响应代码：
{{ (() => {
    const msg = $json.error?.message || $json.message || ''
    if (msg.includes('INVALID_ID')) return 400
    if (/429|too many/i.test(msg)) return 429
    if (/openrouter|anthropic|llm/i.test(msg)) return 502
    return 500
})() }}
```

Switch + N 个响应节点只有在响应结构不同时（不同的标头、不同的正文形状、重定向、不同的内容类型）才值得存在。相同的形状但数量不同是一个表达式驱动的响应。

有关完整约定，包括关联 ID、可重试与致命标志、验证详细信息以及速率限制形状，请参见 `references/RESPONSE_SHAPES.md`。

## 工作流级别的错误工作流

对于无人值守的工作流，配置实例的错误工作流（或每个工作流的覆盖）以指向一个工作流，该工作流：

1. 捕获失败（工作流名称、执行 ID、错误、堆栈）。
2. 通知某人（Slack、电子邮件、值班人员）。
3. 可选：使用退避排队重试。

捕获每个节点处理遗漏的内容：超时、节点之间的崩溃、未连接节点的错误。

参见 `references/ERROR_WORKFLOWS.md`。

## 参考文件

| 文件 | 何时阅读 |
|---|---|
| `references/API_WORKFLOWS.md` | 构建或审查 webhook 触发器 / 响应 Webhook 工作流 |
| `references/ERROR_WORKFLOWS.md` | 为生产工作流设置工作流级错误捕获 |
| `references/RESPONSE_SHAPES.md` | 定义你的 API 的响应正文约定 |
| `references/NODE_ERROR_OUTPUTS.md` | 在单个可能出错的节点上连接每个节点的错误输出 |

## 反模式

| 反模式 | 出现的问题 | 修复 |
|---|---|---|
| Webhook → 处理 → 响应，没有错误分支 | 调用者遇到超时或空 500 | 将每个可能出错的节点的 `output(1)` 连接到 `响应 Webhook` |
| 单个 `响应 Webhook` 用于两条路径 | 正文形状无法告诉调用者发生了什么 | 两个响应节点，每个路径一个，带有明确的代码和正文 |
| 错误路径返回 200 带有 `{ "error": ... }` 正文 | 调用者的 HTTP 客户端将其视为成功，因此错误处理永远不会触发 | 错误路径始终为 4xx/5xx |
| 在 Code 节点中捕获错误并以数据形式返回 | 下游看到错误形状的数据，工作流继续 | 让它抛出，配置 `onError: 'continueErrorOutput'` 并连接错误路径 |
| 生产工作流没有工作流级错误工作流 | 真正的失败无处可去 | 设置错误工作流。参见 `ERROR_WORKFLOWS.md` |
| 每个失败都带有通用“内部服务器错误” | 无法区分调用者错误与上游错误与速率限制 | 结构化错误代码。参见 `RESPONSE_SHAPES.md` |
| 生产节点调用易出错的或速率限制的 API 而没有 `retryOnFail` | 每个瞬态 429 或上游波动都会显示为 5xx，并且警报会在噪音上触发 | 设置 `retryOnFail: true, maxTries: 3, waitBetweenTries: 5000` 在节点上。参见“瞬态失败的自我修复” |
| 500 对于所有非 200 | 调用者无法将他们的错误输入与你的故障区分开来，因此他们的监控会在你的噪音上触发 | 映射原因 → 状态码。调用者的问题是 4xx。 |
| Switch 基于 错误消息 → N 个仅通过状态码不同的响应节点 | 5 个节点用于一个带有表达式驱动的 `Response Code` 的响应 | 在单个响应中内联计算代码。参见上文“一个响应，表达式驱动的状态码”。 |
