# MongoDB Atlas Streams

使用 MongoDB MCP 服务器中的四个 MCP 工具构建、操作和调试 Atlas Stream Processing (ASP) 管道。

## 前置条件

此技能需要连接到 **MongoDB MCP 服务器**，并具有：
- Atlas API 凭证（`apiClientId` 和 `apiClientSecret`）

四个工具：`atlas-streams-discover`、`atlas-streams-build`、`atlas-streams-manage`、`atlas-streams-teardown`。

**所有操作都需要一个 Atlas 项目 ID。** 如果未知，请先调用 `atlas-list-projects` 找到您的项目 ID。

## 如果 MCP 工具不可用

如果 MongoDB MCP 服务器未连接或流工具缺失，请参阅 [references/mcp-troubleshooting.md](references/mcp-troubleshooting.md) 以获取诊断步骤和备用方案。

## 工具选择矩阵

### atlas-streams-discover — 所有读取操作
| 操作 | 使用场景 |
|--------|----------|
| `list-workspaces` | 查看项目中的所有工作空间 |
| `inspect-workspace` | 查看工作空间配置、状态、区域 |
| `list-connections` | 查看工作空间中的所有连接 |
| `inspect-connection` | 检查连接状态、配置、健康状态 |
| `list-processors` | 查看工作空间中的所有处理器 |
| `inspect-processor` | 检查处理器状态、管道、配置 |
| `diagnose-processor` | 完整健康报告：状态、统计信息、错误 |
| `get-networking` | PrivateLink 和 VPC 对等连接的详细信息。可选：`cloudProvider` + `region` 以获取 Atlas 账户详细信息用于 PrivateLink 设置 |

**分页**（所有列表操作）：`limit`（1-100，默认 20）、`pageNum`（默认 1）。
**响应格式**：`responseFormat` — `"concise"`（列表操作的默认值）或 `"detailed"`（检查/诊断的默认值）。

### atlas-streams-build — 所有创建操作
| 资源 | 关键参数 |
|----------|---------------|
| `workspace` | `cloudProvider`、`region`、`tier`（默认 SP10）、`includeSampleData` |
| `connection` | `connectionName`、`connectionType`（Kafka/Cluster/S3/Https/Kinesis/Lambda/SchemaRegistry/Sample）、`connectionConfig` |
| `processor` | `processorName`、`pipeline`（必须以 `$source` 开头，以 `$merge`/`$emit` 结尾）、`dlq`、`autoStart` |
| `privatelink` | `privateLinkConfig`（项目级，与特定工作空间无关） |

**字段映射 — 仅填写所选资源类型的字段：**

- **resource = "workspace":** 填写：`projectId`、`workspaceName`、`cloudProvider`、`region`、`tier`、`includeSampleData`。留空：所有连接和处理器字段。
- **resource = "connection":** 填写：`projectId`、`workspaceName`、`connectionName`、`connectionType`、`connectionConfig`。留空：所有工作空间和处理器字段。（参见 [references/connection-configs.md](references/connection-configs.md) 获取类型特定的模式。）
- **resource = "processor":** 填写：`projectId`、`workspaceName`、`processorName`、`pipeline`、`dlq`（推荐）、`autoStart`（可选）。留空：所有工作空间和连接字段。（参见 [references/pipeline-patterns.md](references/pipeline-patterns.md) 获取管道示例。）
- **resource = "privatelink":** 填写：`projectId`、`privateLinkConfig`。注意：PrivateLink 是 **项目级**，不是工作空间级。`workspaceName` 不是必需的 — 跳过它。留空：所有连接和处理器字段。

### atlas-streams-manage — 所有更新/状态操作
| 操作 | 备注 |
|--------|-------|
| `start-processor` | 开始计费。可选 `tier` 覆盖，`resumeFromCheckpoint` |
| `stop-processor` | 停止计费。保留状态 45 天 |
| `modify-processor` | 处理器必须先停止。更改管道、DLQ 或名称 |
| `update-workspace` | 更改 tier 或 region |
| `update-connection` | 更新配置（网络是不可变的 — 必须删除并重新创建） |
| `accept-peering` / `reject-peering` | VPC 对等管理 |

**字段映射** — 始终填写 `projectId`、`workspaceName`，然后根据操作：

- `"start-processor"` → `resourceName`。可选：`tier`、`resumeFromCheckpoint`、`startAtOperationTime`（ISO 8601 时间戳，以从特定点恢复）
- `"stop-processor"` → `resourceName`
- `"modify-processor"` → `resourceName`。至少提供一个：`pipeline`、`dlq`、`newName`
- `"update-workspace"` → `newRegion` 或 `newTier`
- `"update-connection"` → `resourceName`、`connectionConfig`。**例外：** 网络配置（例如 PrivateLink）创建后无法修改 — 删除并重新创建。
- `"accept-peering"` → `peeringId`、`requesterAccountId`、`requesterVpcId`
- `"reject-peering"` → `peeringId`

**状态预检查：**
- `start-processor` → 如果处理器已经 `STARTED` 则报错
- `stop-processor` → 如果已经 `STOPPED` 或 `CREATED` 则无操作（不是错误）
- `modify-processor` → 如果处理器是 `STARTED` 则报错（必须先停止）

**处理器状态：** `CREATED` → `STARTED`（通过 start）→ `STOPPED`（通过 stop）。也可能因运行时错误进入 `FAILED` 状态。修改需要 `STOPPED` 或 `CREATED` 状态。

**拆除安全检查：**
- **处理器删除** → 删除前自动停止（无需手动停止）
- **连接删除** → 如果有正在运行的处理器引用它，则会阻止。先停止/删除引用的处理器。
- **工作空间删除** → 见下方详细工作流程（第 108-111 行）。

### atlas-streams-teardown — 所有删除操作
| 资源 | 安全行为 |
|----------|----------------|
| `processor` | 删除前自动停止 |
| `connection` | 如果被正在运行的处理器引用，则会阻止 |
| `workspace` | 级联删除所有连接和处理器 |
| `privatelink` / `peering` | 删除网络资源 |

**字段映射** — 始终填写 `projectId`、`resource`，然后：

- `resource: "workspace"` → `workspaceName`
- `resource: "connection"` 或 `"processor"` → `workspaceName`、`resourceName`
- `resource: "privatelink"` 或 `"peering"` → `resourceName`（ID）。这些是项目级资源，不是特定工作空间的。

**删除工作空间之前**，请先检查它：
1. `atlas-streams-discover` → `inspect-workspace` — 获取连接/处理器数量
2. 向用户展示： "工作空间 X 包含 N 个连接和 M 个处理器。删除将永久移除所有。继续？"
3. 等待确认后再调用 `atlas-streams-teardown`

## 关键：创建处理器前验证

**您必须在组合任何处理器管道之前调用 `search-knowledge`。** 这不是可选的。
- **字段验证**：使用 sink/source 类型进行查询，例如 "Atlas Stream Processing $emit S3 字段" 或 "Atlas Stream Processing Kafka $source 配置"。这可以捕获错误，例如 S3 `$emit` 的 `prefix` 与 `path`。
- **模式示例**：使用 `dataSources: [{"name": "devcenter"}]` 查询以获取工作管道示例，例如 "Atlas Stream Processing 滚动窗口示例"。

构建非简单处理器时，也从官方 ASP 示例存储库中获取示例：**https://github.com/mongodb/ASP_example**（快速入门、示例处理器、Terraform 示例）。从 `example_processors/README.md` 开始获取完整模式目录。

关键快速入门：
| 快速入门 | 模式 |
|-----------|---------|
| `00_hello_world.json` | 内联 `$source.documents` 与 `$match`（零基础设施，临时） |
| `01_changestream_basic.json` | 变更流 → 滚动窗口 → `$merge` 到 Atlas |
| `03_kafka_to_mongo.json` | Kafka 源 → 滚动窗口汇总 → `$merge` 到 Atlas |
| `04_mongo_to_mongo.json` | 链式处理器：汇总 → 存档到单独集合 |
| `05_kafka_tail.json` | 实时 Kafka 主题监控（无 sink，类似 `tail -f`） |

## 管道规则和警告

**无效结构** — 这些在流管道中无效：
- **`$$NOW`**、**`$$ROOT`**、**`$$CURRENT`** — 流处理中不可用。**绝对不要使用**。使用文档自己的时间戳字段或 `_stream_meta` 元数据代替 `$$NOW`。
- **HTTPS 连接作为 `$source`** — HTTPS 仅用于 `$https` 富集或 sink，**不能**作为数据源
- **没有 `topic` 的 Kafka `$source`** — 需要 topic 字段
- **没有 sink 的管道** — 需要终端阶段（`$merge`、`$emit`、`$https` 或 `$externalFunction` 异步）才能部署处理器（sinkless 仅通过 `sp.process()` 工作）
- **作为 `$emit` 目标的 Lambda** — Lambda 使用 `$externalFunction`（管道中间的富集），而不是 `$emit`
- **`$validate` 与 `validationAction: "error"`** — 导致处理器崩溃；使用 `"dlq"` 代替

**每个阶段的必需字段：**
- **`$source`（变更流）**：包含 `fullDocument: "updateLookup"` 以获取完整文档内容
- **`$source`（Kinesis）**：使用 `stream`（**不是** `streamName` 或 `topic`）
- **`$emit`（Kinesis）**：必须包含 `partitionKey`
- **`$emit`（S3）**：使用 `path`（**不是** `prefix`）
- **`$https`**：必须包含 `connectionName`、`path`、`method`、`as`、`onError: "dlq"`
- **`$externalFunction`**：必须包含 `connectionName`、`functionName`、`execution`、`as`、`onError: "dlq"`
- **`$validate`**：必须包含 `validator` 与 `$jsonSchema` 和 `validationAction: "dlq"`
- **`$lookup`**：包含 `parallelism` 设置（例如，`parallelism: 2`）以进行并发 I/O
- **AWS 连接**（S3、Kinesis、Lambda）：IAM 角色ARN必须通过 Atlas Cloud Provider Access 首先注册。始终与用户确认。参见 [references/connection-configs.md](references/connection-configs.md) 获取详细信息。

参见 [references/pipeline-patterns.md](references/pipeline-patterns.md) 获取带有 JSON 语法每个阶段的字段示例。

**SchemaRegistry 连接**：`connectionType` 必须是 `"SchemaRegistry"`（**不是** `"Kafka"`）。模式类型值区分大小写（使用小写 `avro`，而不是 `AVRO`）。参见 [references/connection-configs.md](references/connection-configs.md#schemaregistry) 获取必需字段和认证类型。

## MCP 工具行为

**引出**：创建连接时，构建工具自动通过 MCP 引出收集缺失的敏感字段（密码、bootstrap servers）。**不要**向用户索要这些 — 让工具收集它们。

**自动规范化：**
- `bootstrapServers` 数组 → 自动转换为逗号分隔的字符串
- `schemaRegistryUrls` 字符串 → 自动包装为数组
- `dbRoleToExecute` → 默认为 `{role: "readWriteAnyDatabase", type: "BUILT_IN"}`，用于 Cluster 连接

**工作空间创建**：`includeSampleData` 默认为 `true`，将自动创建 `sample_stream_solar` 连接。

**区域命名**：`region` 字段使用 Atlas 特定名称，因云提供商而异。使用错误格式将返回一个神秘的 `dataProcessRegion` 错误。

| 提供商 | 云区域 | Streams `region` 值 |
|----------|-------------|----------------------|
| **AWS** | us-east-1 | `VIRGINIA_USA` |
| **AWS** | us-east-2 | `OHIO_USA` |
| **AWS** | eu-west-1 | `DUBLIN_IRL` |
| **GCP** | us-central1 | `US_CENTRAL1` |
| **GCP** | europe-west1 | `EUROPE_WEST1` |
| **Azure** | eastus | `eastus` |
| **Azure** | westeurope | `westeurope` |

参见 [references/connection-configs.md](references/connection-configs.md) 获取完整的区域映射表。如有疑问，使用 `atlas-streams-discover` → `inspect-workspace` 检查现有工作空间并检查 `dataProcessRegion.region`。

## 连接功能 — 源/接收器参考

在创建管道之前，了解每种连接类型的功能：

| 连接类型 | 作为源 ($source) | 作为接收器 ($merge / $emit) | 管道中间 | 备注 |
|-----------------|---------------------|--------------------------|--------------|-------|
| **Cluster** | ✅ 变更流 | ✅ $merge 到集合 | ✅ $lookup | 变更流监控插入/更新/删除/替换操作 |
| **Kafka** | ✅ 主题消费者 | ✅ $emit 到主题 | ❌ | 源必须包含 `topic` 字段 |
| **Sample Stream** | ✅ 示例数据 | ❌ 无效 | ❌ | 仅用于测试/演示 |
| **S3** | ❌ 无效 | ✅ $emit 到存储桶 | ❌ | 仅 sink — 使用 `path`、`format`、`compression`。支持 AWS PrivateLink。 |
| **Https** | ❌ 无效 | ✅ $https 作为 sink | ✅ $https 富集 | 可用于管道中间的富集或作为最终 sink 阶段 |
| **AWSLambda** | ❌ 无效 | ✅ $externalFunction（仅异步） | ✅ $externalFunction（同步或异步） | **Sink：** `execution: "async"` 必须使用。**管道中间：** `execution: "sync"` 或 `"async"` |
| **AWS Kinesis** | ✅ 流消费者 | ✅ $emit 到流 | ❌ | 类似 Kafka 模式 |
| **SchemaRegistry** | ❌ 无效 | ❌ 无效 | ✅ 模式解析 | **仅元数据** - 由 Kafka 连接用于 Avro 模式 |

**常见的连接使用错误要避免：**
- ❌ 使用 `$externalFunction` 作为 sink 且 `execution: "sync"` → sink 阶段必须使用 `execution: "async"`
- ❌ 忘记变更流存在 → Atlas Cluster 不仅是 sink，也是强大的源
- ❌ 使用 `$merge` 与 Kafka → Kafka 源使用 `$emit`

参见 [references/connection-configs.md](references/connection-configs.md) 获取按类型详细连接配置模式。

## 核心工作流程

### 从零开始设置
1. `atlas-streams-discover` → `list-workspaces`（检查现有）
2. `atlas-streams-build` → `resource: "workspace"`（靠近数据，开发使用 SP10）
3. `atlas-streams-build` → `resource: "connection"`（为每个源/接收器/富集）
4. **验证连接**：`atlas-streams-discover` → `list-connections` + `inspect-connection` 对每个 — 验证名称与目标匹配，向用户展示摘要
5. 调用 `search-knowledge` 验证字段名称。从 https://github.com/mongodb/ASP_example 获取相关示例
6. `atlas-streams-build` → `resource: "processor"`（配置 DLQ）
7. `atlas-streams-manage` → `start-processor`（警告计费）

### 工作流程模式

**增量管道开发（推荐）：**
参见 [references/development-workflow.md](references/development-workflow.md) 获取完整的 5 阶段生命周期。
1. 从基本的 `$source` → `$merge` 管道开始（验证连接性）
2. 添加 `$match` 阶段（验证过滤）
3. 添加 `$addFields` / `$project` 转换（验证重塑）
4. 添加窗口或富集（验证聚合逻辑）
5. 添加错误处理 / DLQ 配置

**修改处理器管道：**
1. `atlas-streams-manage` → `action: "stop-processor"` — **处理器必须先停止**
2. `atlas-streams-manage` → `action: "modify-processor"` — 提供新管道
3. `atlas-streams-manage` → `action: "start-processor"` — 重新启动

**调试失败的处理器：**
1. `atlas-streams-discover` → `diagnose-processor` — 单次健康报告。始终先调用此命令。
2. **确定具体根本原因。** 将症状与诊断模式匹配：
   - **错误 419 + "no partitions found"** → Kafka 主题不存在或拼写错误
   - **状态：FAILED + 多次重启** → 连接级错误（绕过 DLQ），检查连接配置
   - **状态：STARTED + 零输出 + 窗口管道** → 可能是空闲 Kafka 分区阻止窗口关闭；为 Kafka `$source` 添加 `partitionIdleTimeout`（例如，`{"size": 30, "unit": "second"}`）
   - **状态：STARTED + 零输出 + 非窗口** → 检查源是否有数据；检查 Kafka 偏移量滞后
   - **high memoryUsageBytes 接近 tier 限制** → OOM 风险；建议更高 tier
   - **DLQ 计数增加** → 每个文档错误；使用 MongoDB `find` 在 DLQ 集合上
   参见 [references/output-diagnostics.md](references/output-diagnostics.md) 获取完整模式表。
3. 在解释输出量之前，先分类处理器类型（警报 vs 转换 vs 过滤）
4. 提供针对诊断根本原因的具体、有序的修复步骤。**不要**展示假设性场景列表。
5. 如果需要详细日志，请指导用户到 Atlas UI：**Atlas → Stream Processing → Workspace → Processor → Logs tab**。

### 链式处理器（多接收器模式）
**关键：单个管道只能有一个终端 sink**（`$merge` 或 `$emit`）。当用户请求多个输出目的地（例如，"写入 Atlas AND 发送到 Kafka"）时，您必须承认单 sink 限制，并提出使用中间目的地链式处理器。参见 [references/pipeline-patterns.md](references/pipeline-patterns.md) 获取完整模式及示例。

## 部署前和部署后检查清单

参见 [references/development-workflow.md](references/development-workflow.md) 获取完整的部署前质量检查清单（连接验证、管道验证）和部署后验证工作流程。

## Tier 尺寸和性能

参见 [references/sizing-and-parallelism.md](references/sizing-and-parallelism.md) 获取 tier 规格、并行公式、复杂度评分和性能优化策略。

## 故障排除

参见 [references/development-workflow.md](references/development-workflow.md) 获取完整的故障排除表，涵盖处理器故障、API 错误、配置问题和性能问题。

## 计费和成本

**Atlas Stream Processing 没有免费 tier。** 所有部署的处理器在运行时都会产生持续费用。

- 费用按小时计算，按秒计费，仅在处理器运行时产生
- `stop-processor` 停止计费；停止的处理器保留状态 45 天免费
- **为原型设计而无需计费：** 在 mongosh 中使用 `sp.process()` — 运行管道临时，无需部署处理器
- 参见 `references/sizing-and-parallelism.md` 获取 tier 定价和成本优化策略

## 安全规则

- `atlas-streams-teardown` 和 `atlas-streams-manage` 需要用户确认 — 不要绕过
- **在调用 `atlas-streams-teardown` 删除工作空间之前**，您必须先使用 `atlas-streams-discover` 检查工作空间以计算连接和处理器数量，然后向用户展示此信息，然后再请求确认
- **在创建任何处理器之前**，您必须根据 [references/development-workflow.md](references/development-workflow.md) 中的 "Pre-Deployment Validation" 部分验证所有连接
- 删除工作空间会永久删除所有连接和处理器
- 停止处理器后，状态保留 45 天 — 然后丢弃检查点
- `resumeFromCheckpoint: false` 会丢弃所有窗口状态 — 首先警告用户
- 在工作空间之间移动处理器不受支持（必须重新创建）
- 不支持干跑/模拟 — 解释您将做什么并请求确认
- 在启动处理器之前始终警告用户关于计费
- 将 API 认证凭据存储在连接设置中，**不要**在处理器管道中硬编码
