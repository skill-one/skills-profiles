---
name: aws-serverless
description: 使用 Lambda、API Gateway、Step Functions、EventBridge 和 SAM/CDK 在 AWS 上构建、部署、管理、调试、配置和优化无服务器应用程序。涵盖冷启动、CORS 调试、事件源映射、故障排除、并发、SnapStart、Powertools、函数 URL、EventBridge Scheduler、Lambda 层以及生产就绪。在提及 Lambda、API Gateway、Step Functions、SAM 模板、CDK 无服务器堆栈、DynamoDB 流触发器、SQS 事件源、冷启动、超时、502/504 错误、限流、并发、CORS、Powertools 或 AWS 上的任何事件驱动架构（即使不使用“无服务器”一词）时触发。不适用于 EC2、ECS/Fargate 容器或 Amplify 托管。
---

# AWS 无服务器

在 AWS 上构建无服务器应用程序的领域专业知识：Lambda、API 网关、步骤函数、事件桥接器、事件源映射、并发性、冷启动、部署和故障排除。

**最佳搭配** [AWS MCP 服务器](https://docs.aws.amazon.com/aws-mcp/) — 运行 CLI 命令、查询 CloudWatch、直接验证配置。所有指导也适用于标准 AWS CLI 访问。

## 专门技能 — 首先检查这些

这些涵盖通用参考下**未**涵盖的功能和流程。其中一些是专门功能或逐步测试的流程，否则您可能会错过。在退回到参考之前，请路由到匹配的技能。

### 高级 Lambda 计算（容易忽略）

| 使用此技能 | 当工作负载涉及 |
|---|---|
| **aws-lambda-microvms** | 强租户隔离、沙盒/不受信任代码执行（AI 代理代码沙盒、REPL、笔记本、CI 运行器）、长时间运行的会话、挂起/恢复保留状态、端口监听服务器（gRPC、WebSocket、自定义 TCP）、Firecracker 微虚拟机、快照可恢复计算、长达 8 小时的生命周期 |
| **aws-lambda-durable-functions** | 持久执行、检查点重放、长时间运行的多步骤工作流（以普通代码形式编写，TS/Python/Java）、自动状态持久化、代码中的 saga 模式、人工参与回调、长达 1 年的执行、`context.step`/`context.wait`/`context.invoke`、`withDurableExecution`、`durable-execution-sdk` |
| **aws-lambda-managed-instances** | Lambda 管理实例（LMI）、容量提供者、EC2 背后的 Lambda、稳定的高流量（每月 5000 万+ 请求）希望使用 Savings Plans / Reserved Instance 定价、`PerExecutionEnvironmentMaxConcurrency`、`CapacityProviderConfig`、多并发执行环境 |

### 工作流编排

当用户希望协调多个步骤、服务或函数时，请路由到此。触发条件包括“编排”、“工作流”、“状态机”、“多步骤协调”、“协调 Lambda 函数”、“持久执行”、“具有重试的管道”、“意图构建 saga/补偿”、“人工参与批准”、“发散”或长时间运行的异步协调。

开始新的编排或多步骤工作流时，您**必须**在实施之前显示 AWS Step Functions 和 AWS Lambda Durable Functions 之间的选择——不要无声地选择一个。根据以下信号进行路由。当请求仅命名通用模式（saga/补偿、人工参与、发散或“工作流编排”）而没有技术时，请提供两个选项和一句话的权衡，然后让用户决定。在信号已经指向一个服务时，不要首先提出权衡的注意事项。

| 使用此技能 | 当工作负载涉及 |
|---|---|
| **aws-step-functions** | 主要工作是直接调用 AWS 服务的工作流；通过原生管理的集成协调非 Lambda 计算（ECS/Fargate、Glue、SageMaker、Batch）；需要可视化、可审计的工作流定义以符合合规性、跨团队运营可观察性或作为不共享代码库的团队之间的共享合同（ASL 是规范，不是应用程序代码）；编写或编辑状态机和 Amazon States Language (ASL) — 状态类型、JSONata 数据转换、Retry/Catch 错误处理、`.sync`/`waitForTaskToken` 服务集成、分布式映射、TestState 单元测试、JSONPath-to-JSONata 迁移 |
| **aws-lambda-durable-functions** | 在已经基于 Lambda 构建时进行代码优先编排（`context.step`/`context.wait`/`context.invoke`、`withDurableExecution`）；每个执行中许多细粒度步骤，累积 Step Functions Standard 状态转换成本可能很高 — 在选择之前，比较 Step Functions 定价（Standard vs Express）与预期量下的 Lambda 调用成本；在同一应用程序代码库中编写的一般用途语言编写的编排步骤（与应用程序代码共享模块、数据类型和测试套件）；应用标准软件工程实践（单元测试、代码审查、类型检查）到编排逻辑，而无需学习声明式工作流语言 |

**权衡（使用任一选项时）：** Durable Functions 将编排保留在您的 Lambda 代码库中；Step Functions 将其外部化为一个管理的可视化状态机，具有内置的服务集成。

**安全：** 两个服务都持久化工作流状态和有效负载 — Step Functions 在执行历史记录中记录完整的输入/输出（可在控制台查看，如果启用了日志记录，则可在 CloudWatch 日志中查看）。作为基本操作，启用执行日志记录（CloudTrail）并在执行失败时使用执行警报和 CloudWatch，并使用每个工作流的最低权限执行角色。不要通过工作流状态传递密钥、令牌或 PII；通过 Secrets Manager/ARN 指针引用它们，并在数据敏感时使用客户管理的 KMS 密钥加密状态。

### 事件驱动架构

当用户正在设计或操作事件驱动系统，而不是编排已知步骤序列时，请路由到此。触发条件包括“事件总线”、“事件驱动架构”、“发布/订阅”、“发布/订阅”、“发散”、“事件排序”、“有序交付”、“FIFO 事件”、“事件重放”、“重放事件”、“事件保留”、“事件存储”、“CloudEvents”、“Avro”、“Protobuf”、“模式注册中心”、“去重”、“编排”、“解耦”、“异步集成”、“事件代理”或跨团队和帐户共享的中心总线。

| 使用此技能 | 当工作负载涉及 |
|---|---|
| **amazon-eventbridge-event-bus** | 新的事件驱动工作负载；平台团队拥有许多团队和帐户发布和订阅的中心总线；对该总线的治理（订阅者控制、撤销、按帐户限流、成本分配、端到端可观察性）；通过模式注册中心解码开放事件格式（Avro、Protobuf、CloudEvents）；每个事件组按有序或 FIFO 交付；高发散，其中按帐户转发成本很重要；持久保留和重放过去的事件到新创建的订阅者；按订阅者 JSONata 转换；去重；跨服务编排和解耦；跨越多个帐户的事件驱动架构。**此技能绝对不能用于有关 EventBridge 经典自定义事件总线、EventBridge Scheduler、EventBridge Pipes、EventBridge 全球端点、EventBridge 模式注册中心、EventBridge API 目标或 EventBridge 连接的问题。** |

### 逐步任务流程（测试的 CLI SOP）

| 使用此技能 | 用于任务 |
|---|---|
| **connecting-lambda-to-api-gateway** | 将现有 Lambda 连接到新的 REST/HTTP API：代理集成、权限、CORS、限流、访问日志记录、部署 |
| **connecting-lambda-to-dynamodb** | 将 Lambda 连接到 DynamoDB：IAM 执行角色、读写权限、流事件源映射 |
| **creating-api-gateway-stage** | 创建具有 CloudWatch 日志记录、X-Ray 跟踪、限流、WAF 关联和授权的 API 网关阶段 |
| **deploying-custom-domain-rest-api** | 部署具有自定义域的区域 REST API：ACM 证书、Lambda 后端、请求授权器、基本路径映射、Route 53 DNS |
| **debugging-lambda-timeouts** | 系统地诊断超时的 Lambda：配置、CloudWatch 日志/指标、VPC、冷启动、内存、下游调用 |
| **processing-s3-uploads-with-step-functions** | 部署事件驱动工作流：S3 上传 → EventBridge → Step Functions → Lambda（小文件）或 Fargate（大文件），具有 VPC/ECR/ECS/IAM |

## 路由（此技能中的通用参考）

| 用户需求 | 阅读 |
|-----------|------|
| 构建新的无服务器应用程序 — 模式选择 | [architecture.md](references/architecture.md) |
| Lambda 配置、冷启动、SnapStart、内存、VPC、层、Function URLs | [lambda.md](references/lambda.md) |
| 并发性（保留、配置、ESM 控制） | [concurrency.md](references/concurrency.md) |
| 事件源（SQS、DynamoDB Streams、SNS、Kinesis）、过滤、批量失败 | [event-sources.md](references/event-sources.md) |
| Step Functions、EventBridge 规则/管道/调度器 | [orchestration.md](references/orchestration.md) |
| API 网关配额、授权器、WebSocket | [api-gateway.md](references/api-gateway.md) |
| SAM/CDK 资源类型和快速迭代 | [deployment.md](references/deployment.md) |
| 生产就绪、可观察性、反模式 | [production.md](references/production.md) |
| 调试错误（确切字符串 → 原因 → 修复） | [troubleshooting.md](references/troubleshooting.md) |
| Powertools 处理器模板 | [powertools-handler.py](assets/powertools-handler.py) |

**注意：** 参考文件包含特定于运行时的版本、配额和功能矩阵，这些会发生变化。当精确度很重要（生产、运行时选择、配额）时，请对照当前 AWS 文档进行确认。参考重点在于容易出错的价值和陷阱，而不是基础知识。
