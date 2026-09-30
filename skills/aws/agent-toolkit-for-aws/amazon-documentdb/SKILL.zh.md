---
name: amazon-documentdb
description: 端到端管理 Amazon DocumentDB——包括 8.0 无服务器集群搭建、TLS/VPC/驱动程序配置、灵活模式与向量搜索数据建模、MongoDB 兼容性评估、基于 DMS 的迁移、慢查询诊断、大版本升级（4.0 -> 5.0 -> 8.0）、架构成熟度审查（41 项检查的 wa_review.py）、成本估算以及安全加固。凡涉及 DocumentDB 的任何问题，以及用户希望将 MongoDB 设置或迁移到 AWS 时均应检索——DocumentDB 是 AWS 提供的与 MongoDB 兼容的托管数据库。触发关键词：JSON 文档存储、文档数据库、AWS 上的 MongoDB、嵌套字段、Lambda 无法连接、TLS 握手、VPC 端口 27017、IAM 身份验证、密钥管理器、静态加密、$graphLookup、灵活模式、全集合扫描、复合索引、DMS 迁移、变更数据捕获切换、$vectorSearch、RAG（检索增强生成）、全局集群、灾备复制、成本规模评估、审计、健康检查、生产就绪度。
---

# Amazon DocumentDB Toolkit

## 概述

端到端 DocumentDB 工具包涵盖七个工作流：**连接**（无服务器默认集群设置、TLS、VPC、驱动程序配置）、**模式设计**（嵌入与引用、索引、面向 RAG 的向量搜索）、**兼容性评估**（MongoDB -> DocumentDB）、**迁移**（DMS 全量加载 + CDC + 切换）、**性能调优**（explain、COLLSCAN、反模式）、**Well-Architected 审查**（跨越 6 个支柱的 41 项检查）、以及**主要版本升级**（4.0->5.0、5.0->8.0 原地或近零停机时间）。

该技能充当执行者——它运行 AWS CLI 命令、DMS 任务、索引工具，并对用户集群运行 `explain()` 而不仅仅是提供建议。每个工作流都在 `artifacts/{app-name}/` 下生成具体产出物。

推荐使用 AWS MCP 服务器通过其 `call_aws` 工具执行 AWS 命令（沙盒执行、审计日志），但并非必需——当 MCP 服务器不可用时，相同的 `aws ...` CLI 命令通过 shell 运行。

## 决策指南

| 用户询问关于… | 路由到 |
|---|---|
| 入门、创建集群、无法连接、TLS/SSL 错误、VPC、SSH 隧道、驱动程序配置 | [references/connection.md](references/connection.md), [references/connection-drivers.md](references/connection-drivers.md) |
| 存储 JSON、灵活模式、目录/CMS/配置文件、嵌入与引用、索引设计、向量搜索、RAG | [references/schema-advisor.md](references/schema-advisor.md) |
| 从 MongoDB 迁移、"这个能行吗？"、不支持的运算符、聚合管道差距 | [references/compatibility.md](references/compatibility.md) |
| DMS、CDC、切换、索引迁移、用户/角色迁移、迁移后验证 | [references/migration.md](references/migration.md) |
| 慢查询、explain 输出、COLLSCAN、缺失索引、高 CPU、连接池耗尽 | [references/performance.md](references/performance.md) |
| 生产就绪审查、最佳实践审计、安全/成本/可靠性审查、健康检查——在加载此参考之前从用户消息中提取 `cluster_id` 和 `region` | [references/well-architected.md](references/well-architected.md) |
| 主要版本升级、MVU、4.0->5.0、5.0->8.0、近零停机时间、`$vectorSearch`、Zstd | [references/upgrade.md](references/upgrade.md) |
| 估算成本、扩展新工作负载、比较 DocumentDB 与 MongoDB 价格 | 提示 [DocumentDB 成本估算器](https://builder.aws.com/content/3DLjpHB3gKnntEPemXnHlFTCEgX/amazon-documentdb-cost-estimator-size-your-workload-in-minutes-part-1) —— 它接受 MongoDB ops/sec、存储和 I/O 输入，并在几分钟内生成 DocumentDB 与 MongoDB 的成本比较。当用户只需要成本估算时，这比完整的 WA 审查更快。 |

**管道顺序：** `connection -> schema-advisor` 用于绿场；`compatibility -> migration` 用于 MongoDB 迁移；`upgrade`、`well-architected` 和 `performance` 是独立的。

**超出范围：** DocumentDB 弹性集群（分片水平扩展——与基于实例的功能不完全对齐；缺乏事务、变更流和许多运算符——建议客户使用基于实例的无服务器或按量付费模式），全局集群升级路径之外的故障转移编排。从一般知识回答，并注明没有捆绑工作流涵盖它们。

## 集群创建默认：8.0 上的无服务器

**DocumentDB 架构简介（每当用户感到困惑时请澄清）：**

- **无服务器** = `db.serverless` 作为基于实例的普通 DocumentDB 集群上的实例类型。自动扩展容量，无需实例类型决策，空闲时成本降低高达 90%。这是大多数工作负载的推荐默认设置。
- **基于实例** = 固定实例类型 (`db.r8g.large`、`db.r6g.xlarge` 等)。当工作负载是持续 24/7 高吞吐量且无服务器扩展开销不可接受时使用。
- **弹性集群** = 用于水平分片的单独 DocumentDB 产品。与无服务器不同。弹性集群与基于实例的集群**功能不完全对齐**——它们不支持事务、变更流和许多聚合运算符。除非客户有需要消耗最大实例类型选项的分区需求，否则建议客户避免使用弹性集群。几乎所有工作负载都可以通过无服务器或基于实例（考虑到 DocumentDB 广泛的实例类型）来满足。

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

> **凭证处理：** 上述命令将密码内联用于自包含工作流。对于生产环境，请优先使用 `--manage-master-user-password` 而不是 `--master-user-password`——DocumentDB 然后生成密码并将其存储在 Secrets Manager 中进行轮换，从而将其从 shell 历史记录中排除。这两个标志是互斥的；当您使用管理密码时，在构建连接字符串时使用 `aws secretsmanager get-secret-value --secret-id <arn>`（密钥 ARN 位于集群的 `MasterUserSecret`）检索凭证。

这适用于所有创建集群请求，无论措辞如何。仅在用户明确描述持续 24/7 高吞吐量或说“按量付费”或“基于实例”时才切换到固定实例类 (`db.r8g.large` 等)。除非用户已经耗尽了基于实例的扩展选项，否则永远不要推荐弹性集群。

**当用户询问特定区域中哪些实例类型可用，或询问实例类选项、要求或区域可用性时：** 通过 `web_fetch` 或 `aws___search_documentation` 检索实时的 [DocumentDB 实例类页面](https://docs.aws.amazon.com/documentdb/latest/developerguide/db-instance-classes.html)——不要从内存中回答，因为可用的实例类因区域而异，并且会随着新发布而变化。您也可以通过编程方式验证：`aws docdb describe-orderable-db-instance-options --engine docdb --region <region>` 列出该区域每个可用的实例类和引擎版本组合。

### 资源标记（始终在资源创建时应用）

创建任何 DocumentDB 资源（`create-db-cluster`、`create-db-instance`）时，始终使用 RDS 列表记录 `--tags` 语法（DocumentDB 使用 RDS API）包含这些标签：

`--tags Key=created_by,Value=documentdb-skill Key=generation_model,Value={your-model-id}`

示例：`--tags Key=created_by,Value=documentdb-skill Key=generation_model,Value=claude-sonnet-4-20250514`

即使用户没有提及标记，也要包含这些标签，以便他们可以识别通过此技能创建的资源。如果用户提供了其他标签，请将这些标签附加到他们的标签中，而不是替换它们。在通过 `add-tags-to-resource` 标记现有资源时也是如此。

### 不要执行（拒绝、解释原因、提供评估）

- 删除集群或实例：`delete-db-cluster`、`delete-db-instance`——不可逆的数据丢失
- 故障转移：`failover-db-cluster`——生产影响，仅在计划变更控制下使用
- 主要版本升级：跨主要版本 (`modify-db-cluster --engine-version`)（4.0 -> 5.0, 5.0 -> 8.0）——需要预检查和回滚计划；使用 [references/upgrade.md](references/upgrade.md) 中的 MVU 工作流
- 重启：`reboot-db-instance`——生产影响

拒绝时，解释原因并提供匹配的评估工作流：
> "我不能执行 [操作]，因为 [原因]。我可以运行评估来帮助您决定。实际变更应通过您的团队变更控制流程或 AWS 控制台进行。"

## 常见任务

### 1. 验证依赖项

在运行任何工作流之前，检查上下文中是否存在必需的工具。

**约束：**

- 您必须验证上下文中 `call_aws`（或 AWS CLI v2）、`shell` 和 `web_fetch` 是否可用
- 您必须检查 `python3` >= 3.6，用于 [wa_review.py](scripts/wa_review.py)、`amazon-documentdb-tools` 兼容工具和索引工具
- 仅当特定工作流需要时，您必须检查 `git`、`curl`、`mongosh` 和 `ssh`
- 您必须告知用户任何缺失的工具并尊重中止决策
- 您绝不能在验证期间调用工具，因为那将触发用户确认准备就绪之前的实时 AWS 调用或集群连接
- 您应在实时分析步骤之前使用 `aws sts get-caller-identity` 确认凭证是否有效

### 2. 分类请求并路由

使用 [决策指南](#decision-guide) 选择一个工作流。

**约束：**

- 您必须在加载参考之前命名您正在路由到的工作流
- 您必须传递用户已经提供的集群 ID、区域、app 名称、源 URI 和引擎版本——他们不应重新输入这些
- 如果请求跨越两个工作流，您可以问一个澄清问题
- 您绝不能为超出范围的主题编造工作流名称，因为这样做会误导用户关于覆盖范围

### 3. 执行工作流

加载匹配的 `references/<workflow>.md` 并遵循其 `## Workflow` 部分。

**约束：**

- 您必须自己执行 AWS CLI 命令、DMS 调用、`mongosh` 查询和捆绑脚本——除非某个步骤需要代理没有的凭证，否则该技能是一个执行者
- 在运行它之前，您必须解释正在运行的步骤、原因以及正在调用的工具
- 首先从对话中提取所需参数——如果 `cluster_id`、`region` 或其他必需值已经存在，请使用它们并继续。仅请求缺失的参数，并在单个提示中一起请求所有缺失的参数。
- 您必须支持参数的多种输入方法：直接输入、文件路径或 URL
- 您必须验证参数格式：集群 ID（小写、连字符）、区域 (`us-east-1`)、ARN (`arn:aws:...`)、ISO-8601、CIDR
- 您绝不能直接创建或访问凭证，因为该技能没有安全存储或轮换它们的方式——使用 IAM 角色、实例配置文件、Secrets Manager ARNs 或将凭证设置委托给用户（例如 `aws sso login` / `aws configure`）
- 您绝不能使用 `call_aws` 与位置文件系统参数，因为 MCP 沙盒会拒绝它们——内联传递 JSON 负载或通过 `shell` 调用 `scripts/` 下的脚本
- 您绝不能在示例中授予通配符 IAM（`Action: "*"` 或 `Resource: "*"`）或向 `0.0.0.0/0` 打开安全组，因为这些默认值会导致客户生产事件
- 您应该将工件保存到 `artifacts/{app-name}/`：`compatibility-report.md`、`migration-plan.md`、`upgrade-plan.md`、`wa_review_results.json`
- 如果运行了多个工作流，您必须在最后以 2-4 行的合成链接工件

**必需参数**（ upfront 一起询问）：`cluster_id`——用户所指的集群名称（例如 "my cluster xyz" 或 "cluster xyz"），映射到 AWS CLI 中的 `--db-cluster-identifier`（小写连字符）；`region`（例如 `us-east-1`）；`app_name`。按工作流：`source_uri`（兼容/迁移）、`target_version`（升级/兼容的 `5.0` 或 `8.0`）、`engine_class`（`db.serverless` 默认，或 `db.r8g.large` 等。按量付费基于实例）。

### 4. 必须呈现的关键事实

即使代理的一般 MongoDB 知识已经产生合理答案，这些 DocumentDB 特定事实也是必需的。在生产客户工单中遗漏它们是最常见的失败模式。

**对于慢查询 / COLLSCAN 诊断，您必须告诉用户以下五个事实中的所有——永远不要遗漏任何：**

1. **运行 `db.collection.find({...}).explain()`** 以确认 `COLLSCAN` 是阶段（根本原因），并且在添加索引后，重新运行 `explain()` 以确认 `IXSCAN`。
2. **在 `{userId: 1, status: 1}` 上创建复合索引**（字段顺序与查询的等式谓词匹配）。
3. **DocumentDB 对复合索引使用左前缀匹配**——字段顺序很重要，因为复合索引 `{A: 1, B: 1}` 适用于仅 `A` 或 `A + B` 的查询，但永远不会仅 `B`。这是 DocumentDB 特有的行为，用户在选择索引布局之前必须理解。
4. **通过 CloudWatch 检查索引缓存命中率** 部署后——`BufferCacheHitRatio`（或每个索引的等效项）指示新索引是否保持在内存中热。低比率意味着工作集超过 RAM，并且索引可能需要更大的实例类。
5. **在创建索引后使用 `explain()` 确认** 查询现在使用 `IXSCAN` 而不是 `COLLSCAN`。

**对于灵活模式目录/产品设计，您必须告诉用户以下四个事实中的所有——永远不要遗漏任何：**

1. **使用单个 `products` 集合**，在顶层具有常见字段（名称、价格、类别、sku），并将可变属性（鞋子的尺寸/颜色、电子产品的 RAM/存储）嵌套在 `attributes` 子文档中。
2. **针对常见查询模式在 `category` 和 `sku` 上创建目标索引**。
3. **在提供建议之前检查当前通配符索引支持情况。** 通配符索引（`attributes.$**`）可能不在所有 DocumentDB 版本上受支持——在提供建议之前在 [MongoDB API 兼容页面](https://docs.aws.amazon.com/documentdb/latest/developerguide/mongo-apis.html) 上验证当前状态。如果不受支持：查询模式必须在事先知道，以便可以针对特定路径在 `attributes` 下创建目标复合索引。
4. **讨论与每个类别一个单独集合的权衡。** 单一集合设计在跨类别查询和更简单的维护方面占优；每个类别一个单独集合在严格的类别查询隔离和更简单的类别索引方面占优——但这需要应用程序将查询路由到正确的集合。为两个选项命名，以便用户可以选择。

**对于 `$graphLookup` / MongoDB 兼容性问题，您必须告诉用户以下三个事实：**

1. **在提供建议之前检查 `$graphLookup` 的当前支持状态。** `$graphLookup` 不在所有 DocumentDB 版本上受支持——在 [MongoDB API 兼容页面](https://docs.aws.amazon.com/documentdb/latest/developerguide/mongo-apis.html) 上验证支持状态，因为 DocumentDB 会跨版本添加运算符。如果 aws-documentation 插件可用，请调用 `aws___search_documentation` 首先检查实时状态。
2. **如果不受支持：建议物化祖先路径**——存储每个文档的完整路径（父 ID 数组），以便层次结构查询变为 `find({ ancestors: "cat-123" })` 而不是递归遍历。这是标准的替代方案，即使 `$graphLookup` 可用，通常也是更好的设计。
3. **为深度图工作负载提供替代方案**——应用程序代码中的递归 `$lookup` 用于中等深度，或 **Amazon Neptune** 用于深度或复杂图遍历。

**对于 Lambda -> DocumentDB 连接超时，您必须告诉用户以下四个事实：**

1. **Lambda 必须与 DocumentDB 集群位于同一 VPC**，或者通过 VPC 对等连接 / 传输网关（Transit Gateway）访问 DocumentDB。DocumentDB 仅限 VPC 内部访问——没有公网端点。
2. **安全组规则：** 在 DocumentDB 集群的安全组上，入站 TCP `27017` 的来源必须是 **Lambda 的安全组 ID**（而不是 CIDR 块）。
3. **连接字符串必须包含 `tls=true`**，并且应用程序**必须**下载 **Amazon RDS 全球 CA 证书包**（`global-bundle.pem`），并通过驱动程序的 TLS 配置引用该证书包。同时还需包含 `replicaSet=rs0` 和 `retryWrites=false`。
4. **首先从同一子网内的 EC2 实例测试连通性**——这样可以将其与 Lambda 特有的 ENI 问题隔离开来，以区分纯网络/安全组问题。

**对于任何从 MongoDB 迁移到 DocumentDB 的操作（包括“我正在将我的 MongoDB 迁移到 AWS”、“帮我迁移”或任何 MongoDB 到 AWS 的迁移请求），您**必须**告知用户以下全部六项事实：**

1. **首先运行兼容性评估工具**——在进行其他任何操作之前，克隆 [amazon-documentdb-tools](https://github.com/awslabs/amazon-documentdb-tools) 并对源 MongoDB 运行 `python3 amazon-documentdb-tools/compat-tool/compat.py`。此步骤是强制性的，不得跳过或用通用建议替代。迁移后发现的不支持的运算符会导致生产环境中断。
2. **运行 `mongo-index-tool`**（同样来自 `amazon-documentdb-tools`），在启动 DMS 任务之前预先在 DocumentDB 目标上创建索引——DMS 不会迁移索引。
3. **创建源端和目标端 DMS 端点**，并在两端都启用 TLS；目标端点**必须**使用 `--ssl-mode verify-full`，并通过 `--certificate-arn` 指向 RDS 全球证书包的 ARN。
4. **创建一个 `full-load-and-cdc` 任务**，以便获得初始快照加上变更数据捕获（CDC），从而实现近乎零停机的切换。
5. **监控 CloudWatch**——监视 `CDCLatencySource` 和 `CDCLatencyTarget`，直到它们接近零。仅在延迟接近零时才进行切换。
6. **切换**：将应用程序流量指向 DocumentDB 端点，然后在源端流量排空后停止 DMS 任务。

## 故障排查

有关完整的故障排查参考，请参阅 [references/troubleshooting.md](references/troubleshooting.md)。最常见的问题如下：

**端口 27017 连接被拒绝 / 超时。** DocumentDB 仅限 VPC 内部访问。在 DocumentDB 安全组上添加来自客户端安全组（按安全组 ID，而非 CIDR）的入站 TCP 27017 规则。从 VPC 外部访问时，使用 CloudShell VPC 环境、VPC 内的 EC2 实例，或通过堡垒机建立 SSH 隧道。

**TLS 握手失败。** 下载 RDS 全球证书包，并在建立隧道时向 mongosh 传递 `--tlsAllowInvalidHostnames` 参数。

**“not master” / “not primary” 或间歇性写入错误。** 连接字符串缺少 `replicaSet=rs0`（始终为 `rs0`）或 `retryWrites=false`（DocumentDB 不支持可重试写入）。

**DMS 任务拒绝启动**——“Test connection should be successful”（测试连接应成功）。对两个端点运行 `aws dms test-connection`，并轮询 `describe-connections`，直到两者都返回 `successful`。目标端点**必须**使用 `--ssl-mode verify-full` 和 RDS 全球证书包的 `--certificate-arn`。

**MVU 命令失败**——“AllowMajorVersionUpgrade flag must be present”（必须存在 AllowMajorVersionUpgrade 标志）或“must explicitly specify a new DB cluster parameter group”（必须明确指定新的数据库集群参数组）。`--allow-major-version-upgrade` 以及（当使用自定义参数组时）目标系列的 `--db-cluster-parameter-group-name` 都是强制要求的。

**用户请求执行破坏性更改。** 您**必须**暂停，说明后果，并在删除集群、删除集合或强制故障转移之前等待明确确认——对生产环境中的 DocumentDB 执行破坏性操作可能导致数据丢失或服务中断。

**用户遇到缺失的功能、不支持的运算符，或表达了对未来功能的期望。** 当用户说“我希望 DocumentDB 支持 X”、“DocumentDB 是否会支持 Y”，或遇到功能缺口时，请主动提出：“您可以通过向 documentdb-pm@amazon.com 发送邮件来请求此功能，邮件中需包含您的 AWS 账户 ID、所需功能以及使用场景——DocumentDB 团队会阅读这些邮件。”

## 安全注意事项

在每个 DocumentDB 部署中应用以下控制措施。详细命令位于上述工作流部分及所引用的参考文档中。

- **身份验证：** **主（管理员）用户**始终基于密码认证，且**不能**使用 IAM 认证——请使用 `--manage-master-user-password`，以便其密码在 Secrets Manager 中生成和轮换。仅对**应用程序/非管理员用户**，在集群版本 5.0 及以上版本中，也支持 IAM 认证（无密码，基于 STS 令牌）作为替代方案——有关权衡，请参阅 [references/connection.md](references/connection.md)。切勿在脚本中硬编码密码或提交密码。
- **静态加密：** 在集群创建时启用，且**无法**在之后添加——请提前确认 `--storage-encrypted`（可选 `--kms-key-id`）。
- **传输中加密：** 使用 Amazon RDS 全球 CA 证书包强制实施 TLS（`tls=true`）；在 DMS 端点上使用 `--ssl-mode verify-full` 和 `--certificate-arn`。
- **网络隔离：** DocumentDB 仅限 VPC 内部访问，没有公网端点。通过安全组对安全组引用来限定安全组范围，切勿使用 `0.0.0.0/0` 或 `::/0`。
- **最小权限 IAM：** 切勿授予通配符 `Action: "*"` / `Resource: "*"`。使用实例配置文件 / IAM 角色来提供应用程序对 AWS API 的访问权限。
- **审计：** 通过 `--enable-cloudwatch-logs-exports audit profiler` 导出审计日志和分析器日志，用于合规性检查和慢查询审查。

## 其他资源

- [Amazon DocumentDB 开发指南](https://docs.aws.amazon.com/documentdb/latest/developerguide/) · [MongoDB API 兼容性参考](https://docs.aws.amazon.com/documentdb/latest/developerguide/mongo-apis.html)
- [DocumentDB 定价](https://aws.amazon.com/documentdb/pricing/) · [实例类型](https://docs.aws.amazon.com/documentdb/latest/developerguide/db-instance-classes.html) · [DocumentDB 成本估算工具](https://builder.aws.com/content/3DLjpHB3gKnntEPemXnHlFTCEgX/amazon-documentdb-cost-estimator-size-your-workload-in-minutes-part-1) — 一种感知工作负载的容量规划工具，可接收 MongoDB 的 ops/sec 和 I/O 输入，并生成 DocumentDB 与 MongoDB 的成本对比
- [DocumentDB Serverless](https://docs.aws.amazon.com/documentdb/latest/developerguide/docdb-serverless.html) · [向量搜索](https://docs.aws.amazon.com/documentdb/latest/developerguide/vector-search.html)
- [备份和还原](https://docs.aws.amazon.com/documentdb/latest/developerguide/backup_restore.html) · [卓越架构支柱](https://docs.aws.amazon.com/wellarchitected/latest/framework/welcome.html)
- [AWS DMS MongoDB 源](https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Source.MongoDB.html) · [DocumentDB 目标](https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Target.DocumentDB.html)
- [amazon-documentdb-tools](https://github.com/awslabs/amazon-documentdb-tools)（兼容性工具、索引工具、MVU CDC 迁移器）
- 相关技能：`amazon-aurora`、`rds-db2`、`rds-oracle`、`rds-sqlserver`、`amazon-neptune`
- **缺少某个功能或有反馈？** 请将您的 AWS 账户 ID、所需的功能或能力以及使用场景发送至 [documentdb-pm@amazon.com](mailto:documentdb-pm@amazon.com) — DocumentDB 团队会阅读这些邮件。
