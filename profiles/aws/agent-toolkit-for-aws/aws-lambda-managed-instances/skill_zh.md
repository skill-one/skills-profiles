# AWS Lambda 管理实例 (LMI)

在用户账户中的 EC2 实例上运行 Lambda 函数，同时 AWS 负责资源供应、补丁更新、扩展、路由和负载均衡。结合了 Lambda 的开发者体验和 EC2 的定价和硬件选项。

**最佳搭配**：[AWS MCP 服务器](https://docs.aws.amazon.com/aws-mcp/)，用于沙盒化 CLI 执行和审计日志记录。所有指导也适用于标准 AWS CLI 或 SAM CLI。

**注意**：在生产部署前，请根据当前 AWS 文档确认区域可用性、配额和实例类型提供情况。

## 快速决策：LMI 是否适合此工作负载？

| 信号 | LMI 是最佳选择 | 标准Lambda更合适 |
|------|---------------------|---------------------------|
| 流量 | 稳定、可预测、每月 50M+ 请求 | 峰值流量、不可预测、长时间无流量 |
| 持续时间 | 超过 15 分钟的长时间运行异步/ESM 任务（LMI 上可达 90 分钟）：ETL/数据处理、媒体转码、ML 推理、金融计算、网络爬虫 | 短暂调用；需要超过 15 分钟的同步工作（Lambda 不支持任何超过 15 分钟的同步工作） |
| 成本 | 规模化时持续时间成本较高 | 低频或零星调用 |
| 冷启动 | 无法接受（LMI 通过资源供应消除了冷启动） | 可接受 |
| 计算 | 最新 CPU、特定系列、高网络带宽、GPU 要求 | 标准 Lambda 内存/CPU 足够 |
| 隔离 | 您账户中的专用 EC2 实例，完全 VPC 控制 | 可接受的 Firecracker 微型虚拟机共享 |
| 零扩展 | 无法零扩展，但可以使用 AWS 提供的解决方案创建自定义计划 | 需要（空闲时不付费） |
| 代码准备情况 | 线程安全（Node.js/Java/.NET）或任何 Python 代码 | 非线程安全代码，更改成本高 |

## 路由

仅读取与用户任务匹配的单个参考文件。不要预加载多个参考文件。

| 用户需求 | 操作 |
|-----------|--------|
| 成本比较、定价分析、Savings Plans、保留实例 | 读取 [cost-comparison.md](references/cost-comparison.md) |
| 实例类型、内存大小、vCPU 比率、扩展调优、容量提供者配置 | 读取 [configuration-guide.md](references/configuration-guide.md) |
| 线程安全、并发模型、代码审查清单、多并发准备 | 读取 [thread-safety.md](references/thread-safety.md) |
| 代码示例（前后）、运行时特定迁移、连接池 | 读取 [migration-patterns.md](references/migration-patterns.md) |
| IAM 角色、VPC 配置、CLI 命令、SAM 模板、CDK 示例 | 读取 [infrastructure-setup.md](references/infrastructure-setup.md) |
| 错误、限流、调试、卡住部署 | 读取 [troubleshooting.md](references/troubleshooting.md) |

**故障排除快速要点**（诊断问题时始终提及）：

- 容量提供者卡在 CREATING 状态 → 最常见的原因是**私有子网缺少 NAT 网关路由**（实例需要外网访问镜像拉取和 Lambda 服务通信）
- 函数无法扩展 → 确认已发布**版本**（PublishToLatestPublished: true）
- 内存错误 → LMI 最小内存为 **2048 MB**

## 工作流程

### 第 1 步：评估工作负载

在推荐前收集以下信号：

1. **流量模式**：稳定还是峰值？每秒请求数？
2. **当前成本**：每月 Lambda 花费？现有 Savings Plans？
3. **运行时**：Node.js、Java、.NET 或 Python？
4. **内存/CPU**：多少内存？CPU 密集型还是 I/O 密集型？
5. **执行持续时间**：平均值和 P99？
6. **并发准备情况**：线程安全？共享 `/tmp` 路径？每次调用的数据库连接？
7. **VPC**：已在 VPC 中？需要私有资源访问？

**超过 15 分钟的长时间运行异步/ESM 任务是积极匹配** — LMI 支持异步和事件源映射调用（ETL/数据处理、媒体转码、ML 推理、金融计算、网络爬虫）的功能，最长可达 90 分钟（5400 秒）。持续时间是关键区别，而不仅仅是成本。

推荐 LMI 时，**始终提及**：至少需要 3 个执行环境以实现 AZ 弹性（生产中不能低于 3 个）。

### 第 2 步：构建成本比较

**必须**：在推荐 LMI 前提供成本比较。

经验法则：LMI 在每月 50-100M+ 请求且流量稳定时具有成本竞争力。使用 [LMI 定价计算器](https://aws-samples.github.io/sample-aws-lambda-managed-instances/) 进行准确比较。

### 第 3 步：配置部署

- **实例系列**（400+ 类型，.large 及以上）：C 系列（计算）、M 系列（通用）、R 系列（内存）。ARM（Graviton）以获得最佳性价比。
- **使用 Graviton 实例时，必须在函数配置中设置 `Architectures: [arm64]`** 以匹配。
- **内存到 vCPU 比率**：2:1（计算）、4:1（通用，默认）、8:1（内存）。最小 2 GB，最大 32 GB。
- **每个 vCPU 的最大并发数**：Node.js 64、Java 32、.NET 32、Python 16。这些是系统限制 — 实际设置为 PerExecutionEnvironmentMaxConcurrency（每个执行环境，而不是每个 vCPU）。
- **对于 I/O 密集型工作负载**：使用运行时默认值或更高的 PerExecutionEnvironmentMaxConcurrency（例如 Node.js 的 10），因为每个请求在等待网络时使用极少 CPU。
- **对于 CPU 密集型工作负载**：将 PerExecutionEnvironmentMaxConcurrency 设置为每个 vCPU 1-2，因为每个请求会饱和 CPU。
- **扩展**：MinExecutionEnvironments（默认 3）、MaxVCpuCount（可选，默认 400 — 作为最佳实践显式设置）、TargetResourceUtilization。
- **函数超时长达 5400 秒（90 分钟）** — 通过现有 `Timeout` 字段设置（CLI `update-function-configuration --timeout 5400`，SAM/CFN `Timeout: 5400`，或控制台）。使用现有 `Timeout` 字段 — 无需单独 API、属性、标签或代码更改。仅适用于**异步和 ESM 调用**；同步和 On-Demand 调用仍受 15 分钟限制（即使 `Timeout` 更高；`GetFunctionConfiguration` 仍报告配置值）。初始化阶段仍受 15 分钟限制。持久函数：每个步骤可运行长达 90 分钟；多步骤工作流长达 1 年。

### 第 4 步：迁移代码

检查代码的并发安全性。LMI 会为每个执行环境并发运行多个调用：

- **Python**：进程隔离 — 全局变量**不共享**。无需线程安全更改。重点检查 `/tmp` 冲突和内存大小。
- **Node.js**：工作线程 — 全局变量在同一个工作线程内共享。需要异步安全性。
- **Java/.NET**：操作系统线程/任务 — 处理程序跨线程共享。需要完全线程安全。

### 第 5 步：设置基础设施

1. 创建两个 IAM 角色：执行角色（用于函数）和操作角色（用于容量提供者 EC2 管理）
2. 配置 VPC，包含跨 3 个以上 AZ 的子网
3. 创建容量提供者，配置 VPC 和扩展限制
4. 创建或更新函数，附加容量提供者
5. 发布一个版本（触发实例供应）

### 第 6 步：验证并切换

1. 首先在非生产环境中部署
2. 监控 CloudWatch：CPU 利用率、内存、并发、限流率
3. 逐步流量切换，使用加权别名（10% → 50% → 100%）
4. 1-2 周生产数据后比较成本
5. 稳定后退役标准 Lambda

## 最佳实践

### 定价（讨论成本时始终提及）

- **三个组成部分**：EC2 实例小时 + 15% 管理费 + $0.20/100 万请求
- **Savings Plans**：计算部分适用 Savings Plans（最高 60-72% 折扣）
- **15% 费用**：在 EC2 成本之上额外收取，用于 AWS 管理资源供应、补丁、扩展和生命周期

### 扩展（讨论扩展或流量时始终提及）

- LMI 可立即吸收 50% 的流量激增，并在 5 分钟内**翻倍容量** — 如果流量增长更快，请求会被限流
- 标准Lambda立即峰值到 3000 — LMI 无法匹配
- **预热**：在已知峰值前使用 MinExecutionEnvironments
- **MaxVCpuCount**（默认 400）— 作为成本上限显式设置
- **形状**：在非高峰时段降低 MinExecutionEnvironments 以降低容量（最低 3 个以实现 AZ 弹性）

### 实例大小

- **每个实例 1 vCPU + 1 GB 保留**用于操作系统开销（不用于函数）
- 可用容量 = 总容量 - 开销

### 配置

- 从 4:1 比率和运行时默认并发开始
- 使用 ARM（Graviton），除非存在 x86 依赖
- 让 Lambda 选择实例类型，除非需要特定硬件
- 设置 MaxVCpuCount 以控制成本上限
- **永不**将 MinExecutionEnvironments 设置低于 3（破坏 AZ 弹性）

### 迁移

- 从 I/O 密集型函数开始（从多并发中受益最多）
- 在附加到容量提供者前检查代码的并发安全性
- 使用加权别名进行逐步流量切换
- 在所有日志语句中包含请求 ID
- 在处理程序外初始化数据库池和 SDK 客户端

### 运维

- 设置 CloudWatch 限流率 > 1% 和 CPU > 80% 的警报
- 计划 14 天实例轮换（自动）
- **永不**手动终止 LMI EC2 实例（删除容量提供者）
- **始终**发布版本 — 未发布的函数无法在 LMI 上运行

### 长时间运行调用（异步/ESM 最高 90 分钟）

- **SQS**：队列可见性超时必须 ≥ 函数超时（≥ 5400 秒对于 90 分钟的函数）。ESM 在创建和更新时验证此条件 — 但一旦 ESM 存在，SQS 可见性超时和函数超时可以独立更改（ESM API 外），这会绕过检查并可能重新引入不匹配，导致消息重新出现和重复调用。
- **Kinesis / DynamoDB Streams**：启用**部分批次失败报告**（`ReportBatchItemFailures`）并调整最大批处理窗口和并行化因子 — 否则一个失败记录会重试整个批次，重新运行高达 ~80 分钟的已完成工作。
- **异步调用**：失败或超时的调用遵循重试策略（默认最多 2 次重试），然后路由到 DLQ / 失败目的地。
- **并非所有 ESM 源都适用**：Amazon MQ 和 Amazon DocumentDB ESM 仍限制为 15 分钟；仅 SQS、Kinesis 和 DynamoDB Streams ESM（以及异步调用）可长达 90 分钟。
- **可观察性不变**：CloudWatch、CloudTrail（完成/超时时的单个调用事件）和 X-Ray（单个跟踪）行为相同。使用 X-Ray 子段查找接近 90 分钟限制的慢速阶段。

### 长时间网络（函数现在可运行数分钟）

- **NAT 网关空闲超时** — 通过 NAT 网关发送定期保活数据包，用于长时间运行的 TCP 连接。
- **空闲连接超时**（RDS、ElastiCache、外部 API） — 为可能在中途空闲的计算连接添加连接健康检查/重连逻辑。
- **DNS TTL** — 定期重新解析外部主机名；AWS SDK 会这样做，但自定义 HTTP 客户端可能缓存超过 TTL。
- **凭证** — 依赖执行角色的临时凭证（由运行时自动刷新）。对于非 IAM 密码（数据库密码、API 密钥），使用 SDK 缓存和定期刷新从 AWS Secrets Manager 或 SSM Parameter Store 获取；**切勿**将长期凭证嵌入代码或环境变量。

## 限制快速参考

| 资源 | 限制 |
|----------|-------|
| 内存 | 最小 2 GB，最大 32 GB |
| 异步/ESM 调用超时 | 90 分钟（5400 秒），通过现有 Timeout 字段 |
| 同步 + On-Demand 调用超时 | 15 分钟 |
| 初始化阶段 | 15 分钟 |
| 限制为 15 分钟的 ESM 源 | Amazon MQ、Amazon DocumentDB（SQS/Kinesis/DynamoDB Streams 可达 90 分钟） |
| 执行环境 | 最小 3 个（MinExecutionEnvironments，AZ 弹性） |
| 实例寿命 | 14 天（自动替换） |
| 并发/vCPU | 64（Node.js）、32（Java/.NET）、16（Python） |
| 运行时 | Node.js 22+、Java 21+、.NET 8+、Python 3.13+、Rust（provided.al2023） |
| 实例系列 | C、M、R（.large 及以上） |
| 扩展 | 峰值空间等于 TargetResourceUtilization 中未使用的容量；新实例在几分钟内启动 |

## 安全注意事项

- **操作角色范围**：在信任策略中添加 `aws:SourceAccount` 和 `aws:SourceArn` 条件，以防止混淆代理攻击。
- **VPC 出站**：将安全组出站范围限制为 VPC 端点安全组或 AWS 前缀列表，而不是 0.0.0.0/0。
- **凭证**：使用 AWS Secrets Manager 或 Parameter Store 存储数据库凭证 — **切勿**使用环境变量存储密码。
- **加密**：启用 SQS SSE、CloudWatch 日志加密（KMS）和 S3 默认加密，以保护所有静态数据。
- **日志记录**：设置 CloudWatch 日志组保留策略。避免记录 PII 或凭证。启用 Lambda 的 CloudTrail 数据事件。
- **实例轮换**：14 天自动轮换确保安全补丁应用，无需人工干预。
- **参考**：[Lambda 安全最佳实践](https://docs.aws.amazon.com/lambda/latest/dg/lambda-security.html)、[IAM 最佳实践](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html)

## 文件

| 文件 | 内容 |
|------|---------|
| [cost-comparison.md](references/cost-comparison.md) | 定价分析、盈亏平衡计算、Savings Plans/保留实例影响 |
| [configuration-guide.md](references/configuration-guide.md) | 实例选择、内存比率、扩展调优、容量提供者配置 |
| [thread-safety.md](references/thread-safety.md) | 每个运行时的并发模型、代码审查清单、Powertools 兼容性 |
| [migration-patterns.md](references/migration-patterns.md) | 每个运行时的前后代码、连接池、逐步切换 |
| [infrastructure-setup.md](references/infrastructure-setup.md) | IAM 角色、VPC 配置、SAM 模板、CLI 命令 |
| [troubleshooting.md](references/troubleshooting.md) | 常见错误、限流、调试、卡住部署 |
