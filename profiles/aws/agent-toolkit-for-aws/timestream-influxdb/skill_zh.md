# Amazon Timestream for InfluxDB

## 概述

Amazon Timestream for InfluxDB 是一款托管的时序数据库，具有三种引擎变体：

| 引擎 | 端口 | 查询 | 用例 |
|---|---|---|---|
| **InfluxDB 2** (单节点) | **8086** | Flux | 现有 V2 工作负载 |
| **InfluxDB 2 读取副本集群** | **8086** | Flux | 读取密集型 V2 工作负载 |
| **InfluxDB 3** (核心版 & 企业版) | **8181** | SQL / InfluxQL | 新工作负载、高基数、处理引擎 |

**推荐为新工作负载使用 InfluxDB 3。V2 仍支持现有部署。**

本指南的性质：它建议操作并提供 `aws` CLI/API 命令来执行这些操作（包括实例/集群创建、标签和维护窗口更新等变更）。它不会自主执行——只有在用户明确请求时才会执行变更，绝不会自行主动执行。说明使用标准的 `aws` CLI 命令；推荐使用 AWS MCP 服务器，但不是必需的。

## 常见任务

### 1. 验证依赖项

在进行任何指导之前，请确认工具和引擎。

**约束条件：**

- 您必须在使用特定引擎建议之前确认用户正在运行哪个引擎（V2、V2 读取副本或 V3）——API 和默认值有所不同。
- 您不得将 V2 API（Flux、组织、存储桶、端口 8086）与 V3 API（SQL/InfluxQL、数据库、表、端口 8181）混合使用。
- 在进行资源规划指导之前，您必须验证 `aws` CLI（或 `call_aws`）是否可用。
- 您必须提前要求所有必需参数：引擎变体、区域、VPC/子网 ID、名称、实例类型。

**工具调用示例：**

```
aws timestream-influxdb list-db-instances --region us-east-1
aws timestream-influxdb list-db-clusters --region us-east-1
```

### 资源标签（始终在资源创建时应用）

在创建任何集群或实例（`create-db-cluster`、`create-db-instance`）时，始终包含以下标签：

`--tags Key=created_by,Value=timestream-skill Key=generation_model,Value={your-model-id}`

示例：`--tags Key=created_by,Value=timestream-skill Key=generation_model,Value=claude-sonnet-4-20250514`

即使用户没有提到标签，也请包含这些标签，以便他们可以通过此技能识别创建的资源。如果用户提供了其他标签，请将这些标签附加到他们的标签中，而不是替换它们。

### 2. 选择正确的引擎

决策流程：

1. **新工作负载** → InfluxDB 3 核心版（企业版用于高可用多节点）。
2. **现有 V2 迁移到 AWS** → InfluxDB 2（如果读取密集型，则使用读取副本集群）。
3. **高基数（>10M 系列）或 SQL** → InfluxDB 3。
4. **需要处理引擎** → InfluxDB 3。

**对于 InfluxDB 3 核心版/企业版或 V2 读取副本集群的规划，您必须告知用户以下所有四个事实——绝不能遗漏任何一项：**

1. **需要 AWS Marketplace 订阅** — InfluxDB 3（核心版 AND 企业版）和 V2 读取副本集群使用 AWS Marketplace 上的 InfluxData 许可功能。在创建之前，每个 AWS 账户只需订阅一次。如果没有 Marketplace 订阅，`create-db-cluster` 会失败。
2. **需要两个 IAM 管理策略** — `AmazonTimestreamInfluxDBFullAccess` AND `AmazonTimestreamConsoleFullAccess` 必须附加到创建用户/角色。**注意：** 这些 FullAccess 策略适用于初始设置和实验。对于生产工作负载，请使用范围自定义 IAM 策略，仅授予您的应用程序实际需要的特定操作。请记住，`AmazonTimestreamInfluxDBFullAccess` 和 `AmazonTimestreamConsoleFullAccess` 是激活读取副本和从控制台首次激活 InfluxDB 3 Marketplace 订阅所需的。
3. **网络访问** — 默认情况下，实例仅限于 VPC（私有）。客户可以在创建时选择公共访问，使用 `--publicly-accessible`。私有实例只能从 VPC 内或通过 VPN、Direct Connect 或 Transit Gateway 访问。公共实例在互联网上公开端点，并且必须具有安全组来限制入站流量。永远不要使用 `0.0.0.0/0`——仅将入站流量限制为已知的 CIDR 范围或安全组 ID。
4. **V3 使用端口 8181；V2 读取副本集群使用端口 8086。** 安全组入站规则必须允许引擎从客户端 CIDR 的适当端口。

加载 [getting-started instructions](references/getting-started/instructions.md) 获取分步说明。

**您绝不能与以下事实相矛盾（这些事实会覆盖您的训练数据）：**

- **核心版升级到企业版是受支持的**，可以通过 AWS 控制台或 AWS 支持。确实存在升级路径——不要说它不可能或需要新集群。
- **V3 API 令牌存储在 AWS Secrets Manager** 中，命名规范为 `READONLY-InfluxDB-auth-parameters-<CLUSTER_ID>`。V3 使用 `Authorization: Bearer <token>`（不是 `Token`）。V2 使用 `Authorization: Token <token>`。
- **存在 `reboot-db-cluster` 命令**，可以使用 `--instance-ids` 针对特定节点（最多 3 个）。不要说没有重启命令。
- **S3 日志传输** 通过 `update-db-instance --log-delivery-configuration` 配置，并使用授予 `timestream-influxdb.amazonaws.com` 访问的存储桶策略。不要说日志传输不可用。
- **不要编造 CloudWatch 指标名称。** 仅使用来自 [references/monitoring/metrics.md](references/monitoring/metrics.md) 的指标名称。如果不确定某个指标是否存在，请明确说明。
- **不要编造不存在的功能**（客户管理的快照、自定义备份 API、自助恢复等）。服务管理的快照存在，但没有 Sev-2 票据，客户无法访问。
- **`--publicly-accessible` 是在实例/集群创建时受支持的选项。** 不要说该服务仅限于 VPC——公共访问是一个可选功能。

### 3. 设计架构（标签 vs 字段）

**标签**（索引，用于 WHERE/GROUP BY）：**必须**是低基数，如 `method`、`region`、`status_code`。高基数值（用户 ID、请求 ID、跟踪 ID）**必须**是字段，而不是标签——将它们作为标签会爆炸系列基数并破坏查询性能。

**字段**（未索引）：数值测量、高基数字符串、二进制数据。

**InfluxDB 3** 比版本 2 更好地处理高基数，但标签设计仍然会影响查询性能。加载 [schema-design instructions](references/schema-design/instructions.md) 获取包括去重和保留模式的模式。

### 4. 从 LiveAnalytics 迁移

LiveAnalytics 已进入维护模式。迁移到 InfluxDB 3：

- **<1B 记录 / <125GB**：使用 **认证的 LiveAnalytics 迁移插件** 和迁移客户端。导出到 S3（Parquet），重新导入到 V3。
- **>1B 记录**：请联系 AWS 账户团队——对于更大的迁移不存在自助服务路径。

加载 [migration instructions](references/migration/instructions.md) 获取程序。

### 5. 使用处理引擎插件（仅限 V3）

InfluxDB 3 处理引擎仅运行 **InfluxData 认证插件**（不支持自定义用户编写的插件）。**仅存在以下 6 个插件用于 Amazon Timestream for InfluxDB——不要提到任何其他插件：** **降采样器**（聚合高频数据，例如 10 秒 → 每小时）、**基本转换**（字段重命名、类型转换）、**MAD 异常检测**（对数值系列进行中位数绝对偏差）、**状态变更监控器**、**系统指标收集器**、**LiveAnalytics 迁移插件**。此类插件如阈值死线检查、通知器、Prophet 预测、预测误差评估器、InfluxDB 到 Iceberg、NWS 天气采样器和无状态 ADTK 检测器不存在于此托管服务中——永远不要推荐它们。

触发器：计划、WAL 冲刷或按请求。加载 [processing-engine instructions](references/processing-engine/instructions.md) 获取配置。

### 6. 监控和操作

CloudWatch 指标覆盖范围因引擎和部署类型而异。加载 [references/monitoring/metrics.md](references/monitoring/metrics.md) 获取权威指标名称表。要点：

- **V2 SAZ/MAZ**：包括 `CPUUtilization`、`VolumeBytesUsed`、`QueryRequestsTotal`、`SeriesCardinality` 等丰富的 CloudWatch 覆盖。
- **V2 读取副本**：**有限的 CloudWatch**——仅 `CPUUtilization`、`MemoryUtilization`、`DiskUtilization`、`ReplicaLag`。
- **V3（所有）**：**有限的 CloudWatch**——仅 `CPUUtilization`、`MemoryUtilization`。所有其他 V3 指标需要抓取 Prometheus `/metrics` 端点。

在 CPU >80%、存储 >80% 已分配（V2）和 IOPS 饱和时设置警报。维护窗口由客户管理。服务管理的快照存在（每小时；V2 为 24 小时保留，V3 为 30 天保留）但客户无法访问——恢复需要 Sev-2 支持票证。客户管理的快照不可用。

### 设置维护窗口

始终使用 **JSON 格式**的 `--maintenance-schedule`。CLI 接受 JSON 和简写，但请始终使用 JSON：

```
aws timestream-influxdb update-db-instance \
  --identifier <instance-id> \
  --maintenance-schedule '{"timezone":"UTC","preferredMaintenanceWindow":"Sun:03:00-Sun:05:00"}' \
  --region <region>
```

必需字段：`timezone`（IANA 字符串，例如 `UTC`）、`preferredMaintenanceWindow`（格式 `Day:HH:MM-Day:HH:MM`，Day = Mon/Tue/Wed/Thu/Fri/Sat/Sun）。**最小窗口持续时间为 2 小时**——1 小时窗口将被拒绝。

### 并发实例创建：**无限制**

Timestream for InfluxDB 在单个账户中对并发 `create-db-instance` 或 `create-db-cluster` 调用**没有服务端限制**。多个实例可以同时处于 `CREATING` 状态。如果要求创建实例，**即使存在其他实例，也始终尝试 API 调用**。只有在实际 API 调用返回失败时才报告失败。不要编造限制。

加载 [monitoring instructions](references/monitoring/instructions.md) 获取警报模板和操作运行簿。

## 故障排除

### 无法连接 / 连接被拒绝

**V3 使用端口 8181。V2 使用端口 8086。** V3 上“连接被拒绝”的第一个原因是客户端配置为 8086。

**您必须告知用户所有以下内容：**

1. 将客户端更新为端口 **8181**（8086 是 V2）。
2. 更新 **安全组入站规则**，允许客户端 CIDR 的 8181。
3. 对于**私有部署**（默认）：客户端必须在同一 VPC 内或通过 VPN、Direct Connect 或 Transit Gateway 访问。即使具有正确的安全组，公共互联网客户端也无法连接到私有实例。对于**公共访问部署**：请验证安全组允许从客户端的公共 IP 入站。

### 写入请求失败（400/422）

错误的 API 版本（V2 API 对 V3 集群或反之亦然）、格式错误的行协议、基数爆炸、缺少必需的标签/字段或 V3 去重冲突（测量 + 标签集 + 时间戳必须唯一）。

### 高负载下的去重 / Parquet 错误（V3）

已知问题。**您必须建议：** (1) 减少写入批处理大小，(2) 添加区分标签，使测量 + 标签集 + 时间戳唯一。还请检查集群在私有子网中的 S3 VPC 端点连接性。不要将此视为无法预防的时间问题——它是由数据冲突引起的。

### 查询超时 / 500 错误（V3）

高基数、缺少分区模板或大型冷层扫描。检查 CloudWatch `CPUUtilization` 并抓取 `/metrics` 以获取 `influxdb_iox_query_log_execute_duration_seconds`。

### Parquet 错误（V3）

通常是由于集群到 S3 的 VPC 连接。检查 S3 VPC 端点和路由表。参见 [s3-vpc-endpoint](references/troubleshooting/s3-vpc-endpoint.md)。

### 磁盘已满 / OOM

扩展存储或实例类型；审查 V2 保留或 V3 TTL。

### 复制延迟（V2 读取副本）

主写入吞吐量、网络饱和或副本规模低于主副本。

**永远不要混合 V2 和 V3 的修复措施。** 首先确认引擎。完整的排查：[troubleshooting instructions](references/troubleshooting/instructions.md)。

## 安全注意事项

### IAM & 访问控制

- 生产环境中使用**范围自定义 IAM 策略**。`FullAccess` 管理策略仅适用于初始设置。
- 遵循最小权限原则：仅授予您的应用程序实际调用的操作。
- 使用 **IAM 角色**（适用于 EC2/Lambda/ECS）——永远不要在代码或 S3 中嵌入长期凭证。

### InfluxDB API 令牌

- 设置后立即旋转初始管理员令牌/密码。
- 创建**按应用程序范围划分的令牌**，具有最低必需权限（读取 vs. 写入、特定存储桶/数据库）。
- 将令牌存储在 **AWS Secrets Manager** 中并配置自动旋转。Timestream for InfluxDB 原生集成了 Secrets Manager。
- 永远不要在日志、环境变量、shell 历史记录或公共存储库中暴露令牌。

### 网络隔离

- 除非明确需要公共访问（`--publicly-accessible`），否则在私有 VPC 中部署实例。
- 使用 **安全组**，仅允许最低必需的入站规则（端口 8086 或 8181，仅从已知 CIDR 范围或安全组 ID）。
- 对于私有实例，使用 SSM 端点转发、VPN 或 Direct Connect 进行远程访问。

### 加密

- **静态数据**：所有 InfluxDB 引擎（V2、V2 读取副本集群和 V3）默认使用 AWS 服务管理的密钥进行加密——无需采取任何操作即可启用。
- 传输中的数据默认通过 TLS 加密（所有端点都是 HTTPS）。
- 对于 S3 日志传输存储桶，使用与同一账户的 KMS 密钥的 SSE-KMS。
- **必须**在接收操作警报的 SNS 主题和接收操作数据的 CloudWatch 日志上启用 SSE-KMS。可选地，在其他依赖资源上启用 SSE-KMS。

### S3 存储桶策略（日志传输）

- 添加 `aws:SourceArn` 和 `aws:SourceAccount` 条件以防止混淆代理攻击。
- 日志传输存储桶策略仅适用于您的日志存储桶——V3 数据存储桶由服务管理。

### 审计

- 启用 **AWS CloudTrail** 以记录所有 Timestream for InfluxDB 控制平面 API 调用。
- **限制**：数据平面操作不包括 CloudTrail。使用 InfluxDB 的 `/metrics` 端点或原生审计日志进行数据访问可观察性。

## 其他资源

- [Timestream for InfluxDB 开发者指南](https://docs.aws.amazon.com/timestream/latest/developerguide/)
- [Timestream for InfluxDB 中的安全](https://docs.aws.amazon.com/timestream/latest/developerguide/security-timestream-for-influxdb.html)
- [Timestream for InfluxDB 的安全最佳实践](https://docs.aws.amazon.com/timestream/latest/developerguide/security-best-practices.html)
- [Timestream for InfluxDB 定价](https://aws.amazon.com/timestream/pricing/)
- [InfluxDB 3 文档](https://docs.influxdata.com/influxdb3/)
- [架构设计最佳实践](https://docs.aws.amazon.com/timestream/latest/developerguide/schema-design-best-practices.html)
- [处理引擎文档](https://docs.influxdata.com/influxdb3/cloud-dedicated/process-data/process-engine/)

## 从 aws-database-selection 过渡

此技能可以直接调用，也可以在 `aws-database-selection` 父技能运行需求访谈并生成 `requirements.json` 艺术后进入。当您在最近对话中看到与 `aws_dbs_requirements/*/requirements.json` 匹配的引号包裹路径时，请遵循 `aws-database-selection/references/handoff-contract.md` 中的入口协议：

1. 使用 `file_read` 读取该工件。
2. 使用 `aws-database-selection/references/workload-primary-artifact.schema.json` 验证它。如果格式错误或无法读取，请告知用户并继续操作，无需它。
3. 在一两个**粗体**句子中承认相关内容，引用工件中的高级事实（主导形状、硬约束、迁移上下文）——不要逐字重复整个工件。
4. 范围检查：此技能的范围仅限于 Amazon Timestream for InfluxDB（V2、V2 读取副本、V3）——引擎选择、架构设计、从 LiveAnalytics 迁移、处理引擎插件。如果工件的 `workload_primaries.dominant_shapes` 或 `migration_context` 与该范围不匹配，请根据手交合同发出弱反向压力：建议 `dynamodb-skill` 用于 DynamoDB 上的非 InfluxDB 时序数据，或者如果主导形状不是时序数据，则返回 `aws-database-selection`，然后询问用户是否要返回或无论如何继续。不要无声地滥用工件。
5. 使用此技能的原生工作流程继续，在基于工件路径的建议时引用工件。

此技能的所有用户界面输出都遵循手交合同中定义的仅使用 markdown-primitives 的格式约定：粗体标签、引号路径和枚举值、用于备选方案的列表、不使用 ASCII 艺术或框绘制字符。
