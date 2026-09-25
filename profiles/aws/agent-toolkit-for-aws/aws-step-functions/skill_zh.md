# AWS Step Functions

## 概述

AWS Step Functions 使用 Amazon States Language (ASL) 以 JSON 格式定义状态机。通过 AWS Step Functions，您可以创建工作流（也称为状态机），用于构建分布式应用程序、自动化流程、编排微服务以及创建数据和机器学习管道。

本技能为编写 ASL 状态机提供了全面的指导，涵盖以下内容：

- ASL 结构和 JSONata 表达式语法
- 八种可用工作流状态的详细信息
- `$states` 保留变量
- 使用 `Assign` 的工作流变量
- 错误处理
- AWS 服务集成模式
- 数据转换和架构的示例代码
- 状态机的验证和测试
- 如何从 JSONPath 迁移到 JSONata

建议使用 AWS MCP 服务器进行沙盒执行和审计日志记录，但所有步骤都使用 AWS CLI 语法，并且无需使用它即可工作。

## 何时加载参考文件

根据用户正在处理的内容加载相应的参考文件：

- **ASL 结构**、**状态类型**、**Task**、**Pass**、**Choice**、**Wait**、**Succeed**、**Fail**、**Parallel**、**Map** → 查看 `references/asl-state-types.md`
- **错误处理**、**故障排除**、**Retry**、**Catch**、**fallback**、**error codes**、**States.Timeout**、**States.ALL** → 查看 `references/error-handling.md`
- **服务集成**、**Lambda invoke**、**DynamoDB**、**SNS**、**SQS**、**SDK 集成**、**Resource ARN**、**sync**、**async** → 查看 `references/service-integrations.md`
- **从 JSONPath 迁移到 JSONata**、**迁移**、**JSONPath to JSONata**、**InputPath**、**Parameters**、**ResultSelector**、**ResultPath**、**OutputPath**、**intrinsic functions**、**Iterator**、**payload template** → 查看 `references/migrating-from-jsonpath-to-jsonata.md`
- **验证**、**linting**、**测试**、**TestState**、**test state**、**mock**、**mocking**、**unit test**、**inspection level**、**DEBUG**、**TRACE**、**validate state**、**test in isolation** → 查看 `references/validation-and-testing.md`
- **架构模式**、**示例**、**polling**、**saga**、**compensation**、**scatter-gather**、**semaphore**、**lock**、**human-in-the-loop**、**escalation**、**Express to Standard** → 查看 `references/architecture-patterns.md`
- **数据转换**、**JSONata expressions**、**filtering**、**aggregation**、**string operations**、**$reduce**、**$lookup**、**$toMillis**、**$partition**、**$parse**、**$hash**、**$uuid** → 查看 `references/transforming-data.md`
- **状态输入/输出**、**$states**、**Assign**、**Output**、**Arguments**、**variable scope**、**variable limits**、**evaluation order**、**passing data between states** → 查看 `references/processing-state-inputs-and-outputs.md`

## 快速参考

### 标准与 Express 工作流

|                                   | 标准                             | Express                                     |
| --------------------------------- | ------------------------------------ | ------------------------------------------- |
| **最大持续时间**                  | 1 年                               | 5 分钟                                   |
| **执行语义**                     | Exactly-once                         | At-least-once (async) / At-most-once (sync) |
| **执行历史**                     | 保留 90 天，可通过 API 查询        | 仅 CloudWatch Logs                        |
| **最大吞吐量**                | 2,000 exec/sec                       | 100,000 exec/sec                            |
| **定价模型**                 | 每次状态转换                     | 每次执行计数 + 持续时间                  |
| **`.sync` / `.waitForTaskToken`** | 支持                              | 不支持                               |
| **最适合**                      | 可审计、非幂等的操作              | 高吞吐量、幂等的事件处理                |

**选择标准** 用于：支付处理、订单履行、合规工作流、任何必须永不执行两次的操作。

**选择 Express** 用于：IoT 数据摄取、流式转换、移动后端、高吞吐量短生命周期处理。

> **推荐 Express 时，必须始终说明一个限制——即使对于一次性/高吞吐量管道——Express 不支持 `.sync` 或 `.waitForTaskToken`**（没有回调，没有嵌套的 `.sync` 等待，没有人工批准或作业完成等待）。还请注意：最大持续时间 5 分钟，没有可查询的执行历史（仅 CloudWatch Logs），至少一次（async）/最多一次（sync）执行——因此非幂等工作可能会运行两次。如果任何这些因素都重要，请选择标准（精确一次，最长 1 年，完整历史）。

### 设置状态机查询语言

JSONata 是在 ASL 中引用和转换数据的首选方式。它用两个字段（`Arguments`（输入）和 `Output`）替换了五个 JSONPath I/O 字段（`InputPath`、`Parameters`、`ResultSelector`、`ResultPath`、`OutputPath`）。

**在顶层启用** 以应用于所有状态：

```json
{ "QueryLanguage": "JSONata", "StartAt": "...", "States": {...} }
```

**或每个状态** 以逐步从 JSONPath 迁移：

```json
{ "Type": "Task", "QueryLanguage": "JSONata", ... }
```

**JSONPath 受支持**，如果省略 `QueryLanguage`，则默认为 JSONPath——现有的状态机无需迁移。

**字段映射（JSONPath → JSONata）：**

| JSONPath 字段 | JSONata 等价物 |
| --- | --- |
| `Parameters` (键使用 `key.$`) | `Arguments` — 删除 `.$` 后缀并将每个值包装在 `{% %}` 中 |
| `ResultSelector` 和 `OutputPath` | `Output`（通过 `$states.result` 引用原始结果） |
| `ResultPath` | `Assign`（首选）或 `Output` |
| `InputPath` | 不需要 — 直接引用 `$states.input` |

> **一个状态使用一种查询语言，而不是两种。** 不要在同一状态中混合 JSONPath 字段（`InputPath`/`Parameters`/`ResultSelector`/`ResultPath`/`OutputPath`）和 JSONata 字段（`Arguments`/`Output`）——这是最常见的迁移错误。有关详细信息，请参阅 `references/migrating-from-jsonpath-to-jsonata.md`。

### 如何评估 Assign 和 Output（并行，非顺序）

在同一状态内，`Assign` 和 `Output` 是**同时评估的——并行地——两者都读取相同的数据（状态输入加上任务结果）**。它们**不是**按顺序评估的。由于它们一起运行，因此在 `Assign` 中设置的变量**不会**在当前状态的 `Output` 中可见：`Output` 无法观察到刚刚分配的值。分配的值仅在**后续**状态中可用。

因此，如果您在 `Assign` 中设置一个变量，并在同一状态的 `Output` 中引用它，您将获得旧/未定义的值——不是因为 `Output` 在 `Assign` 之前运行，而是因为两者同时从相同的快照评估。要立即使用该值，请在**下一个**状态中引用它（变量跨状态持久）；要从任务结果塑造当前状态的输出，请在 `Output` 中直接使用 `$states.result`。

### 使用 TestState 测试状态

使用 TestState API (`aws stepfunctions test-state`) 并使用 `--mock` **在不部署状态机或调用真实服务的情况下测试单个状态**。完整的答案涵盖所有四个点：

- **精确模拟服务响应** — `--mock` `result` 必须**完全匹配**目标 AWS 服务的 API 响应模式（字段名区分大小写）。对于 Lambda `invoke` Task，其 `StatusCode` 和 `Payload`：`--mock '{"result":"{\"StatusCode\":200,\"Payload\":{...}}"}'`。
- **所有三个检查级别** (`--inspection-level`)：`INFO`（默认——`output`、`status`、`nextState`）、`DEBUG`（添加数据流：`afterArguments`、`result`、`variables`——用于调试 JSONata/数据流）、`TRACE`（添加原始 HTTP `request`/`response`，用于 HTTP Task）。
- **`.sync` 和 `.waitForTaskToken` 集成仍然需要模拟** — 对于 `.sync`，模拟轮询 API（例如 `DescribeExecution`，而不是初始调用）；对于 `.waitForTaskToken`，还传递 `--context '{"Task":{"Token":"..."}}'`。
- **无需部署**或真实调用——状态在隔离环境中测试。

查看 `references/validation-and-testing.md` 获取每个服务的模拟结构和错误/重试/Map/Parallel 测试。

## 最佳实践

- 对于新状态机，在顶层设置 `"QueryLanguage": "JSONata"`，除非用户想使用 JSONPath
- 保持 `Output` 最小——仅包括当前状态之后的状态需要的内容
- 使用 `Assign` 存储在后续状态中需要的变量，而不是通过 Output 传递
- 使用 `$states.input` 引用原始状态输入
- `Assign` 和 `Output` 是从状态入口数据**并行评估的，而不是顺序评估**——因此，在 `Assign` 中设置的变量**不会**在当前状态的 `Output` 中可见（`Output` 仍然看到 `Assign` 之前的值）；新值仅在下一个状态生效。
- 所有 JSONata 表达式都必须产生定义的值——`$data.nonExistentField` 抛出 `States.QueryEvaluationError`
- 使用 `$states.context.Execution.Input` 从任何状态访问原始工作流输入
- 在控制台外工作时，将状态机定义保存为 `.asl.json` 扩展名
- 优先使用优化的 Lambda 集成（`arn:aws:states:::lambda:invoke`）而不是 SDK 集成

## 故障排除

### 常见错误

- `States.QueryEvaluationError` — JSONata 表达式失败。检查类型错误、未定义的字段或超出范围的值。
- 在同一状态中混合 JSONPath 字段和 JSONata 字段。
- 在 JSONata 表达式的顶层使用 `$` 或 `$$` — 使用 `$states.input` 代替。
- 遗忘 JSONata 表达式周围的 `{% %}` 定界符——该字符串将被视为字面量。
- 在同一状态的 `Assign` 中分配变量并期望在 `Output` 中引用它——新值仅在下一个状态生效。
- 参考 `references/validation-and-testing.md` 和 `references/error-handling.md` 获取详细的故障排除信息。

## 安全注意事项

- **最小权限执行角色。** 将状态机的 IAM 角色的范围限制为它调用的特定资源和操作（特定的 Lambda/DynamoDB/SQS/SNS ARNs）。避免 `*FullAccess` 策略和服务 `*` 通配符。
- **加密。** 建议对工作流接触的每个数据存储进行加密：KMS 加密的 DynamoDB 表、SQS 队列和 SNS 主题的服务端加密（`KmsMasterKeyId`），以及 HTTP Task 的 TLS。
- **任务令牌和消息正文是敏感的。** `.waitForTaskToken` 令牌是凭证——将其视为秘密。不要将 PII、财务数据或秘密放在 SQS/SNS 消息正文或通知中；传递一个参考 ID，并让接收者通过授权渠道查找详细信息。
- **验证输入并快速失败。** 在工作流的开始处使用 Choice（或 Pass）状态使用 `$exists()` 和 `$type()` 验证必需字段，并将无效输入路由到 Fail 状态，以便损坏的数据永远不会到达下游状态。通过在 Map 状态上设置 `MaxConcurrency` 并限制上游（StartExecution 速率限制或 EventBridge）来保护下游服务免受突发影响。
- **跨账户访问。** 当使用 `Credentials` 字段在其他账户中假设角色时，在目标角色的信任策略中包括条件键，例如 `aws:SourceArn` 或 `aws:SourceAccount`，以防止意外假设。
- **外部秘密。** 对于调用第三方 API 的 HTTP Task，将 API 密钥和令牌存储在 AWS Secrets Manager（通过 EventBridge 连接引用），永远不要将其嵌入状态机定义中。
- **可观察性。** 为执行启用 CloudWatch Logs（日志级别 `ALL` 或 `ERROR`；Express 工作流需要，因为它们没有可查询的执行历史），启用 CloudTrail 以审计 Step Functions API 调用，并为执行失败设置 CloudWatch Alarms。始终使用客户管理的 KMS 密钥加密执行日志组，因为状态输入/输出通常流经执行日志。

## 资源

- [ASL 规范](https://states-language.net/spec.html)
- [JSONata 文档](https://docs.jsonata.org/overview.html)
- [Step Functions 开发者指南](https://docs.aws.amazon.com/step-functions/latest/dg/welcome.html)
- [Step Functions 安全最佳实践](https://docs.aws.amazon.com/step-functions/latest/dg/security-best-practices.html)
