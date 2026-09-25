# Amazon DocumentDB Toolkit

## 概述

端到端 DocumentDB 工具包涵盖七个工作流：**连接**（无服务器默认集群设置、TLS、VPC、驱动程序配置）、**模式设计**（嵌入与引用、索引、用于 RAG 的向量搜索）、**兼容性评估**（MongoDB -> DocumentDB）、**迁移**（DMS 全量加载 + CDC + 切换）、**性能调优**（explain、COLLSCAN、反模式）、**Well-Architected 审查**（跨越 6 个支柱的 41 项检查）以及**主要版本升级**（4.0->5.0、5.0->8.0 原地或近零停机时间）。

该技能充当执行者——它运行 AWS CLI 命令、DMS 任务、索引工具，并对用户集群运行 `explain()` 而不仅仅是提供建议。每个工作流都在 `artifacts/{app-name}/` 下生成具体工件。

推荐使用 AWS MCP 服务器通过其 `call_aws` 工具执行 AWS 命令（沙盒执行、审计日志），但它不是必需的——当 MCP 服务器不可用时，相同的 `aws ...` CLI 命令通过 shell 运行。

## 决策指南

| 用户询问关于… | 路由到 |
|---|---|
| 开始使用、创建集群、无法连接、TLS/SSL 错误、VPC、SSH 隧道、驱动程序配置 | [references/connection.md](references/connection.md), [references/connection-drivers.md](references/connection-drivers.md) |
| 存储 JSON、灵活模式、目录/CMS/配置文件、嵌入与引用、索引设计、向量搜索、RAG | [references/schema-advisor.md](references/schema-advisor.md) |
| 从 MongoDB 迁移、"这个会工作吗？"、不支持的运算符、聚合管道差距 | [references/compatibility.md](references/compatibility.md) |
| DMS、CDC、切换、索引迁移、用户/角色迁移、迁移后验证 | [references/migration.md](references/migration.md) |
| 慢查询、explain 输出、COLLSCAN、缺失索引、高 CPU、连接池耗尽 | [references/performance.md](references/performance.md) |
| 生产就绪审查、最佳实践审计、安全/成本/可靠性审查、健康检查——加载此参考前从用户消息中提取 `cluster_id` 和 `region` | [references/well-architected.md](references/well-architected.md) |
| 主要版本升级、MVU、4.0->5.0、5.0->8.0、近零停机时间、`$vectorSearch`、Zstd | [references/upgrade.md](references/upgrade.md) |
| 估算成本、扩展新工作负载、比较 DocumentDB 与 MongoDB 定价 | 提示 [DocumentDB Cost Estimator](https://builder.aws.com/content/3DLjpHB3gKnntEPemXnHlFTCEgX/amazon-documentdb-cost-estimator-size-your-workload-in-minutes-part-1) —— 它接受 MongoDB ops/sec、存储和 I/O 输入，并在几分钟内生成 DocumentDB 与 MongoDB 的成本比较。当用户只需要成本估算时，比完整的 WA 审查更快。 |

**管道顺序：** `connection -> schema-advisor` 用于绿字段；`compatibility -> migration` 用于 MongoDB 迁移；`upgrade`、`well-architected` 和 `performance` 是独立的。

**超出范围：** DocumentDB 弹性集群（分片水平扩展——与基于实例的功能不完全对等；缺乏事务、更改流和许多运算符——建议客户使用基于实例的无服务器或按量付费模式）。升级路径之外的全球集群 DR 或策动。从一般知识中回答，并注明没有捆绑工作流涵盖它们。

## 集群创建默认：8.0 上的无服务器

**DocumentDB 架构简介（每当用户困惑时请澄清）：**

- **无服务器** = `db.serverless` 作为基于实例的普通 DocumentDB 集群上的实例类。自动扩展容量，无需实例类决策，空闲时成本降低高达 90%。这是大多数工作负载的推荐默认设置。
- **基于实例** = 固定实例类 (`db.r8g.large`、`db.r6g.xlarge` 等)。当工作负载持续 24/7 高吞吐量且无服务器扩展开销不可接受时使用。
- **弹性集群** = 用于水平分片的单独 DocumentDB 产品。与无服务器不同。弹性集群与基于实例的集群**功能不完全对等**——它们不支持事务、更改流和许多聚合运算符。建议客户除非有需要最大实例类选项也无法满足的分片需求，否则避免使用弹性集群。几乎所有工作负载都可以由无服务器或基于实例提供，因为 DocumentDB 提供了广泛的实例类。

**创建任何新的 DocumentDB 集群时，您必须使用以下确切命令——默认为 8.0 上的无服务器：**

```bash
aws docdb create-db-cluster \
  --db-cluster-identifier <cluster_id> \
  --engine docdb \
  --engine-version 8.0.0 \
  --serverless-v2-scaling-configuration MinCapacity=1,MaxCapacity=16 \
  --master-username adminuser \
  --master-user-password '<password>' \
  --tags Key=created_by,Value=documentdb-skill Key=generation_model,Value=<your-model-id> \
  --region <region>

aws docdb create-db-instance \
  --db-instance-identifier <cluster_id>-instance \
  --db-instance-class db.serverless \
  --engine docdb \
  --db-cluster-identifier <cluster_id> \
  --tags Key=created_by,Value=documentdb-skill Key=generation_model,Value=<your-model-id> \
  --region <region>
```

> **凭证处理：** 上述命令将密码内联用于自包含工作流。对于生产环境，请优先使用 `--manage-master-user-password` 而不是 `--master-user-password`——DocumentDB 然后生成密码并将其存储在 Secrets Manager 中进行轮换，从而将其从 shell 历史记录中排除。这两个标志是互斥的；当您使用管理密码时，使用 `aws secretsmanager get-secret-value --secret-id <arn>` 获取凭证（密码 ARN 位于集群的 `MasterUserSecret` 上），在构建连接字符串时使用（当用户明确描述持续 24/7 高吞吐量或说“按量付费”或“基于实例”时）。仅当用户明确描述持续 24/7 高吞吐量或说“按量付费”或“基于实例”时，才切换到固定实例类 (`db.r8g.large` 等)。除非用户已使用 Elastic Clusters 并耗尽了实例类扩展选项，否则永远不要推荐 Elastic Clusters。

**当用户询问特定区域中哪些实例类型可用，或询问实例类选项、要求或区域可用性时：** 通过 `web_fetch` 或 `aws___search_documentation` 检索实时的 [DocumentDB 实例类页面](https://docs.aws.amazon.com/documentdb/latest/developerguide/db-instance-classes.html)——不要从内存中回答，因为可用实例类因区域而异，并随新发布而变化。您还可以通过编程方式验证：`aws docdb describe-orderable-db-instance-options --engine docdb --region <region>` 列出该区域每个可用实例类和引擎版本组合。

### 资源标记（资源创建时始终应用）

创建任何 DocumentDB 资源（`create-db-cluster`、`create-db-instance`），始终使用 RDS 记录列表 `--tags` 语法（DocumentDB 使用 RDS API）包含这些标签：

`--tags Key=created_by,Value=documentdb-skill Key=generation_model,Value={your-model-id}`

示例：`--tags Key=created_by,Value=documentdb-skill Key=generation_model,Value=claude-sonnet-4-20250514`

即使用户没有提到标记，也包含这些标签，以便他们可以识别通过此技能创建的资源。如果用户提供其他标签，请将这些标签附加到他们的标签中，而不是替换它们。在通过 `add-tags-to-resource` 标记现有资源时也适用相同的规则。

### 不要执行（拒绝、解释原因、提供评估）

- 删除集群或实例：`delete-db-cluster`、`delete-db-instance`——不可逆的数据丢失
- 故障转移：`failover-db-cluster`——生产影响，仅在计划变更控制下使用
- 主要版本升级：跨主要版本 `modify-db-cluster --engine-version`（4.0 -> 5.0，5.0 -> 8.0）——需要预检查和回滚计划；使用 [references/upgrade.md](references/upgrade.md) 中的 MVU 工作流
- 重启：`reboot-db-instance`——生产影响

拒绝时，解释原因并提供匹配的评估工作流：
> "我不能执行 [action]，因为 [reason]。我可以运行一个评估来帮助您决定。实际变更应通过您的团队变更控制流程或 AWS 控制台进行。"

## 常见任务

### 1. 验证依赖项

在运行任何工作流之前，检查上下文中是否存在所需工具。

**约束：**

- 您必须验证上下文中存在 `call_aws`（或 AWS CLI v2）、`shell` 和 `web_fetch`
- 您必须检查 `python3` >= 3.6，用于 [wa_review.py](scripts/wa_review.py)、`amazon-documentdb-tools` 兼容工具和索引工具
- 仅当特定工作流需要时，您必须检查 `git`、`curl`、`mongosh` 和 `ssh`
- 您必须告知用户任何缺失的工具并尊重中止决策
- 您绝不能在验证期间调用工具，因为那将触发用户确认准备就绪之前的实时 AWS 调用或集群连接
- 在执行实时分析步骤之前，您应该使用 `aws sts get-caller-identity` 确认凭证有效

### 2. 分类请求并路由

使用 [决策指南](#decision-guide) 选择一个工作流。

**约束：**

- 您必须在加载参考之前命名要路由到的工作流
- 您必须传递用户已经提供的集群 ID、区域、应用名称、源 URI 和引擎版本——他们不应重新输入这些
- 如果请求跨越两个工作流，您可以问一个澄清问题
- 您绝不能为超出范围的主题编造工作流名称，因为这样做会误导用户关于覆盖范围

### 3. 执行工作流

加载匹配的 `references/<workflow>.md` 并遵循其 `## Workflow` 部分。

**约束：**

- 您必须自己执行 AWS CLI 命令、DMS 调用、`mongosh` 查询和捆绑脚本——除非步骤需要代理没有的凭证，否则该技能充当执行者
- 在运行它之前，您必须解释正在运行的步骤、原因以及正在调用的工具
- 首先从对话中提取所需参数——如果 `cluster_id`、`region` 或其他所需值已经存在，请使用它们并继续。仅要求缺失的参数，并在单个提示中一次性要求所有缺失的参数。
- 您必须支持参数的多种输入方法：直接输入、文件路径或 URL
- 您必须验证参数格式：集群 ID（小写、连字符）、区域（`us-east-1`）、ARN（`arn:aws:...`）、ISO-8601、CIDR
- 您绝不能直接创建或访问凭证，因为技能没有安全的方法来存储或轮换它们——使用 IAM 角色、实例配置文件、Secrets Manager ARN 或将凭证设置委托给用户（例如 `aws sso login` / `aws configure`）
- 您绝不能使用 `call_aws` 与位置文件系统参数，因为 MCP 沙盒会拒绝它们——将 JSON 负载内联或通过 `shell` 调用 `scripts/` 下的脚本
- 您绝不能在示例中使用通配符 IAM（`Action: "*"` 或 `Resource: "*"`）或向 `0.0.0.0/0` 打开安全组，因为这些默认值会导致客户生产事件
- 您应该将工件保存到 `artifacts/{app-name}/`：`compatibility-report.md`、`migration-plan.md`、`upgrade-plan.md`、`wa_review_results.json`
- 如果运行了多个工作流，您必须以 2-4 行的总结结束，将工件联系起来

**所需参数**（ upfront 一次性要求）：`cluster_id`——用户提到的集群名称（例如“my cluster xyz”或“cluster xyz”），映射到 AWS CLI 中的 `--db-cluster-identifier`（小写连字符）；`region`（例如 `us-east-1`）；`app_name`。按工作流：`source_uri`（兼容/迁移）、`target_version`（`5.0` 或 `8.0` 用于升级/兼容）、`engine_class`（`db.serverless` 默认，或 `db.r8g.large` 等 用于按量付费的基于实例）。

### 4. 必须呈现的关键事实

即使代理的一般 MongoDB 知识已经产生合理答案，这些 DocumentDB 特定的事实也是必需的。遗漏它们是生产客户工单中最常见的失败模式。

**对于慢查询 / COLLSCAN 诊断，您必须告诉用户以下五个事实中的所有——永远不要遗漏任何：**

1. **运行 `db.collection.find({...}).explain()`** 以确认 `COLLSCAN` 是阶段（根本原因），并在添加索引后重新运行 `explain()` 以确认 `IXSCAN`。
2. **在 `{userId: 1, status: 1}` 上创建复合索引**（字段顺序与查询的等式谓词匹配）。
3. **DocumentDB 对复合索引使用左前缀匹配**——字段顺序很重要，因为复合索引 `{A: 1, B: 1}` 适用于仅 `A` 或 `A + B` 的查询，但永远不会仅适用于 `B`。这是 DocumentDB 特有的行为，用户在选择索引布局之前必须理解这一点。
4. **通过 CloudWatch 检查索引缓存命中率** 部署后——`BufferCacheHitRatio`（或每个索引的等效指标）指示新索引是否保持在内存中热。低比率意味着工作集超过 RAM，索引可能需要更大的实例类。
5. **在创建索引后通过 `explain()` 确认** 查询现在使用 `IXSCAN` 而不是 `COLLSCAN`。

**对于灵活模式目录/产品设计，您必须告诉用户以下四个事实中的所有——永远不要遗漏任何：**

1. **使用单个 `products` 集合**，在顶层具有常见字段（名称、价格、类别、sku），并将可变属性（鞋子的尺寸/颜色、电子产品的 RAM/存储）嵌套在 `attributes` 子文档中。
2. **针对常见查询模式在 `category` 和 `sku` 上创建目标索引**。
3. **在提供建议之前检查当前通配符索引支持情况。** 通配符索引（`attributes.$**`）可能不在所有 DocumentDB 版本上受支持——在提供建议之前，在 [MongoDB API 兼容性页面](https://docs.aws.amazon.com/documentdb/latest/developerguide/mongo-apis.html) 上验证当前状态。如果不受支持：必须预先知道查询模式，以便可以针对 `attributes` 下特定路径创建目标复合索引。
4. **讨论与每个类别一个单独集合的权衡。** 单集合设计在跨类别查询和更简单的维护方面占优；每个类别一个单独集合的占优在于严格的每个类别查询隔离和更简单的每个类别索引——但这需要应用程序将查询路由到正确的集合。为两个选项命名，以便用户可以选择。

**对于 `$graphLookup` / MongoDB 兼容性问题，您必须告诉用户以下三个事实：**

1. **在提供建议之前检查 `$graphLookup` 的当前支持状态。** `$graphLookup` 不在所有 DocumentDB 版本上受支持——在 [MongoDB API 兼容性页面](https://docs.aws.amazon.com/documentdb/latest/developerguide/mongo-apis.html) 上验证支持状态，因为 DocumentDB 会跨版本添加运算符。如果 aws-documentation 插件可用，首先调用 `aws___search_documentation` 检查实时状态。
2. **如果不受支持：建议使用物化祖先路径**——存储每个文档的完整路径（父 ID 数组），以便层次结构查询变为 `find({ ancestors: "cat-123" })` 而不是递归遍历。这是标准的替代方案，即使 `$graphLookup` 可用，通常也是更好的设计。
3. **为深度图工作负载提供替代方案**——应用程序代码中的递归 `$lookup` 用于中等深度，或使用 **Amazon Neptune** 进行深度或复杂图遍历。

**对于 Lambda -> DocumentDB 连接超时，您必须告诉用户以下四个事实：**

1. **Lambda 必须与 DocumentDB 集群位于同一 VPC**，或通过 VPC 对等/传输网关到达它。DocumentDB 仅限于 VPC——没有公共端点。
2. **安全组规则：** DocumentDB 集群 SG 上的入站 TCP `27017`，源自 **Lambda 的安全组 ID**（不是 CIDR）。
3. **连接字符串必须包括 `tls=true`**，应用程序必须下载 **Amazon RDS 全局 CA 套件**（`global-bundle.pem`）并通过驱动程序的 TLS 配置引用它。还包括 `replicaSet=rs0` 和 `retryWrites=false`。
4. **首先从与 Lambda 相同子网中的 EC2 实例测试连接**——这将隔离 Lambda 特定的 ENI 问题与纯网络/SG 问题。
