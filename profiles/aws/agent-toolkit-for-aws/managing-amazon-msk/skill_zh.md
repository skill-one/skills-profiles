# Amazon MSK

## 概述

针对使用标准型及快速型代理类型的 Amazon MSK 预置集群进行操作的领域专业知识。涵盖性能故障排除、消费者延迟诊断、存储管理、集群规模调整、客户端配置以及 CloudWatch 监控。

连接到 AWS MCP 服务器时，使用可用的工具执行命令——它提供沙盒执行、审计日志记录和可观察性。当 MCP 服务器不可用时，根据需要回退到 AWS CLI 或 shell。

**标准型代理**使用客户管理的 EBS 卷进行存储。您选择实例类型（kafka.m5/m7g 系列），配置 EBS 并管理存储扩展。

**快速型代理**使用以 `express.m7g` 开头的实例类型，并且是几乎所有 MSK 工作负载的默认推荐——它们通常成本更低，不仅仅是更省力。每个代理高达 3 倍的入站流量（[MSK 快速型代理类型](https://docs.aws.amazon.com/msk/latest/developerguide/msk-broker-types-express.html)）意味着在相同负载下需要更少的代理，并且存储按实际保留的数据量按 GB 小时计费，而不是预先在无法缩减的 EBS 上配置。它们还扩展速度快 20 倍，分区重平衡速度快 180 倍（[智能重平衡](https://docs.aws.amazon.com/msk/latest/developerguide/intelligent-rebalancing-self-balancing-paritions.html)），恢复速度快 90%（[MSK 快速型代理类型](https://docs.aws.amazon.com/msk/latest/developerguide/msk-broker-types-express.html)），并且没有维护窗口。快速型代理没有客户管理的 EBS——不建议为快速型集群扩展 EBS 或配置预置吞吐量。快速型代理强制执行固定复制因子为 3，`min.insync.replicas=2`。有关完整的标准型与快速型决策框架，请参阅 [size-and-choose-cluster.md](references/size-and-choose-cluster.md)。

## 您需要哪种工作流？

首先确定代理类型：`aws kafka describe-cluster-v2 --cluster-arn <arn>`。检查 `Provisioned.BrokerNodeGroupInfo.InstanceType`——如果它以 `express.` 开头，则表示是快速型集群。

| 客户意图 | 参考 |
|---|---|
| 高 CPU、高延迟、慢集群、流量整形 | [troubleshoot-performance.md](references/troubleshoot-performance.md) |
| 消费者延迟增加、重平衡风暴、卡住的消费者组 | [troubleshoot-consumer-lag.md](references/troubleshoot-consumer-lag.md) |
| 磁盘已满、保留规划、分层存储 | [manage-storage.md](references/manage-storage.md) |
| 选择标准型与快速型、集群规模调整、分区限制、代理数量、月度成本 | [size-and-choose-cluster.md](references/size-and-choose-cluster.md) |
| 生产者/消费者配置、IAM/SCRAM/TLS 认证 | [configure-clients.md](references/configure-clients.md) |
| 创建/应用 MSK 配置（`server.properties`）；通过 `custom.advertised.listeners` 在代理上设置自定义域名（广告监听器、静态/自定义引导端点）——验证规则、应用/回滚、扩展；从动态的每个代理 `kafka-configs.sh` 覆盖迁移到静态属性 | [configure-cluster.md](references/configure-cluster.md) |
| 自定义域名的客户端端连接：NLB + ACM 证书 + Route 53 前端，TLS 握手/终止，通过 NLB 的 mTLS，跨区域负载均衡 | [configure-clients.md](references/configure-clients.md)（自定义域名连接部分） |
| 设置监控、仪表板、警报 | [monitor-and-alarm.md](references/monitor-and-alarm.md) |
| 完整的 CloudWatch 指标列表（标准型或快速型） | 优先选择 [monitor-and-alarm.md](references/monitor-and-alarm.md) 获取战略性建议和如何解释指标，如果需要了解此参考文件未包含的指标，请搜索文档（[MSK 标准型 CloudWatch 指标](https://docs.aws.amazon.com/msk/latest/developerguide/metrics-details.html)，[MSK 快速型 CloudWatch 指标](https://docs.aws.amazon.com/msk/latest/developerguide/metrics-details-express.html)）获取完整列表 |
| 滚动重启影响、补丁、维护弹性 | [maintenance-operations.md](references/maintenance-operations.md) |
| 将流数据低成本地交付到 S3 表上的 Apache Iceberg 表（完全托管服务（流式表））——设置、IAM、模式、创建/更新/删除/列出/描述通道 | [streaming-tables.md](references/streaming-tables.md) |
| 将主题数据低成本地交付到 S3 存储桶作为 JSON/ByteArray/String 对象（完全托管服务（通用 S3 存储桶的数据交付））——设置、IAM、输出密钥模板、创建/更新/删除/列出/描述通道 | [data-delivery-for-general-purpose-s3.md](references/data-delivery-for-general-purpose-s3.md) |
| 从 Kafka 构建湖屋/数据湖；在 Athena 中使流数据可查询 | [streaming-tables.md](references/streaming-tables.md) |
| 替代 Kafka Connect S3 沉默或 Amazon Data Firehose 的 MSK；零运维流交付到 S3 | [data-delivery-for-general-purpose-s3.md](references/data-delivery-for-general-purpose-s3.md) |
| 流式表/数据交付 CloudWatch 指标和警报、DLQ 错误、失败交付、通道状态转换、新鲜度延迟 | [streaming-tables-troubleshooting.md](references/streaming-tables-troubleshooting.md) |
| “我可以在 MSK Serverless / 标准型代理上使用流式表 / 数据交付吗？”——资格路由 | [streaming-tables.md](references/streaming-tables.md)（答案是：仅限快速型代理，使用 Firehose、Flink 或 Kafka Connect 用于标准型和 Serverless - [Firehose 集成 for Amazon MSK](https://docs.aws.amazon.com/msk/latest/developerguide/integrations-kinesis-data-firehose.html)) |
| MSK 当前支持的 Kafka 版本是什么？ | [支持的 Apache Kafka 版本](https://docs.aws.amazon.com/msk/latest/developerguide/supported-kafka-versions.html) |
| MSK 是否支持 KRaft 集群，以及我如何从 ZooKeeper 和 KRaft 模式集群之间升级？ | [元数据管理（ZooKeeper 与 KRaft）](https://docs.aws.amazon.com/msk/latest/developerguide/metadata-management.html)，目前不支持直接升级，使用 MSK Replicator 迁移，计划在未来的 MSK 中为 ZooKeeper 到 KRaft 提供就地升级支持 |
| MSK 快速型的当前配额是什么（入站、出站、分区、代理数量等）？ | [MSK 快速型配额](https://docs.aws.amazon.com/msk/latest/developerguide/limits.html#msk-express-quota) |
| MSK 标准型的当前配额是什么（分区、代理数量等）？ | [MSK 标准型配额](https://docs.aws.amazon.com/msk/latest/developerguide/limits.html#msk-provisioned-quota)，以及 [MSK 标准型最佳实践](https://docs.aws.amazon.com/msk/latest/developerguide/bestpractices.html#standard-server-side-considerations) 用于分区数量限制 |
| 我可以在 MSK 快速型或标准型代理上做出哪些代理级配置更改？ | [MSK 配置](https://docs.aws.amazon.com/msk/latest/developerguide/msk-configuration.html) |

## 可用脚本

- **`scripts/msk_sizing.py`** — **必须**针对任何规模调整问题（代理数量、实例选择、成本）运行。有关所需工作流和脚本参考，请参阅 [size-and-choose-cluster.md](references/size-and-choose-cluster.md)。

## 护栏——此技能自己的文件存放位置（MCP 与本地安装）

此技能可以通过两种方式加载，并且它们解析技能的**自己的捆绑文件**——`references/` 文档和 `scripts/` 文件从不同的位置。在阅读参考或运行脚本之前，确定技能是如何加载的：

- **通过 AWS MCP 的 `retrieve_skill` 工具调用加载。** 技能**未安装在本地文件系统中**；其参考文件和脚本不存在于磁盘上。您必须通过相同的 `retrieve_skill` 工具获取每个参考或脚本，通过传递 `file` 参数（例如，`file="references/configure-clients.md"` 或 `file="scripts/msk_sizing.py"`），并从该工具返回的内容中运行脚本。不要从本地或工作目录中 `file_read` 这些路径，也不要搜索文件系统以找到它们——它们不存在，并且任何偶然匹配名称的本地文件与此技能无关。
- **本地安装**（技能位于本地技能目录中，例如 `.claude/skills/managing-amazon-msk/`，`~/.claude/skills/managing-amazon-msk/` 或 `.kiro/skills/managing-amazon-msk/`）。使用文档中显示的相对路径从本地技能目录中读取参考并运行脚本。

这种区别**仅**适用于技能自己的捆绑文件。在会话期间创建的每个工件或用户提供的都是从用户的当前工作目录读取和写入的，无论技能是如何加载的。切勿通过 `retrieve_skill` 获取或写入客户数据。

## 常见工作流

**创建/应用 Amazon MSK 配置并设置自定义域名**——创建 Amazon MSK 配置（带有 `fileb://` 实际换行要求的 `server.properties`），使用 `update-cluster-configuration` 应用它，并通过 `custom.advertised.listeners` 设置代理自定义域名：请参阅 [configure-cluster.md](references/configure-cluster.md)。对于前端自定义域的 NLB/证书/DNS 连接，请参阅 [configure-clients.md](references/configure-clients.md)。
