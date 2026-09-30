---
name: aws-storage
description: 选择、调查和比较 AWS 对象存储、文件存储和块存储服务，并回答有关存储服务的成本、性能、配置、安全和故障排除问题。适用于用户根据其使用模式询问数据存储或归档位置；选择哪个存储服务或如何比较两个服务；如何从本地环境或 AWS 服务之间迁移数据；如何保护、复制或恢复数据；如何优化存储成本；在哪里部署共享 NFS、SMB 或 POSIX 文件系统；在哪里存储向量嵌入或表格数据；哪个存储支持企业文件共享、EC2、VMware 或有状态容器上的自管理数据库；或询问 AWS 存储服务能做什么或如何工作。适用于 AI/ML、分析、EDA、HPC、媒体、基因组学或金融交易等工作负载的存储需求。不适用于 SQL 查询引擎（Athena、Spark、Redshift、EMR）、ETL（Glue）、流处理（Kafka、MSK、Kinesis）或托管数据库服务（RDS、Aurora、DynamoDB）。
---

## 概述

此技能提供选择 AWS 存储服务的领域专业知识，包括选择存储类别、优化成本以及路由到操作存储服务的资源。它涵盖了对象存储（S3 通用存储桶及其存储类别、S3 Express One Zone 目录存储桶、S3 表格、S3 向量）、文件存储（Amazon EFS、S3 文件、FSx for Lustre、FSx for NetApp ONTAP、FSx for OpenZFS 和 FSx for Windows File Server）、块存储（EBS 卷类型和 EC2 实例存储），以及连接它们的用于数据移动和保护的服务（DataSync、Storage Gateway、Transfer Family 和 AWS Backup）。它不提供数据库或分析查询引擎的建议。它可与 AWS MCP 服务器一起使用或单独使用；当可用时，建议使用 [AWS MCP 服务器](https://docs.aws.amazon.com/agent-toolkit/) 验证当前规范和定价，并且所有指导也适用于标准 AWS CLI。对于深度的单一服务任务，请路由到下方路由部分中列出的专业技能。

## 如何处理用户查询

当此技能被触发时，对用户请求进行分类并遵循相应的路径。

### 规则

这些规则适用于所有路径的响应，无论路径如何：

1. 您必须验证当前数字。当 AWS MCP 服务器可用时，使用 search_documentation 和 read_documentation 进行交叉检查，然后再引用具体信息。在引用成本时，您必须包含相关定价页面的链接。在引用性能指标时，您必须包含相关产品页面的链接。否则，请对照链接的 AWS 文档页面或使用 AWS CLI 确认当前值。如果参考文件指示您获取当前值，您必须在回答前从链接页面检索该值。不要用记住的数字代替，也不要用检索到的值代替近似值或范围。如果当前环境中无法检索，请命名您无法验证的值，而不是引用记忆中的值。
2. 您必须在回答有关该服务的问题之前，从下方路由部分中检索相关服务参考文件。AWS 存储规范、限制和服务功能经常变化。您不得仅凭记忆回答。您必须在响应中呈现来自参考文件的相关故障排除指南和“注意事项”。建议的理由是工作负载匹配，而不是提及参考文件“明确”为给定服务提及了工作负载。
3. 您必须在推荐服务或方法时包含成本影响。不要等待用户提问。不要仅根据存储费用比较服务；对象费用（如元数据费用）可能会实质性地改变 TCO。对于超出存储选择之外的深度成本分析、监控或优化，请路由到 [`billing-and-cost-management`](https://github.com/aws/agent-toolkit-for-aws/tree/e2588f4b494416e68c5a991e51b21c2d99038de3/skills/core-skills/aws-billing-and-cost-management) 技能。
4. 在提供建议时，您必须明确了解用户的需求。将您的响应的具体性匹配到请求的具体性。当查询确定存储类别和相关服务时，直接检索信息并提供建议。当查询未完全指定时，您必须提及建议的假设和限制，并包括确认或更改它的附加问题。仅在查询完全不允许您确定存储类别时，才用后续问题代替建议。即使它超出此技能的范围，也建议最适合工作负载的服务；将相关范围内的选项作为替代方案添加。

---

### 第 1 步：分类意图

确定用户需要什么：

| 意图 | 示例触发器 | 这意味着什么 |
| --- | --- | --- |
| SELECT | "我应该使用什么？", "哪个服务？", "比较服务 A 和服务 B", "帮助我选择", "我想将 X 迁移到 AWS"（没有指定服务的负载描述） | 用户需要帮助选择存储服务或方法 |
| INVESTIGATE | "我该如何配置服务 X？", "为什么服务 Y 失败？", "服务 Z 的限制是什么？", "我该如何开始使用服务 X？"（指定了特定服务并询问操作性问题） | 用户知道他们正在使用什么，并需要入门、故障排除或操作帮助 |

您必须遵循相应路径说明下的交互逻辑。

模糊情况：如果用户的主要请求是建议，则无论上下文如何，它都是 SELECT。如果他们需要帮助执行已知的计划，则它是 INVESTIGATE。

---

### 第 2a 步：SELECT 路径

用户需要帮助选择。您必须使用以下决策因素来为您提供建议，并询问问题以填补会改变选择的空白。

决策因素：

| # | 决策因素 | 需要理解什么 |
| --- | --- | --- |
| 1 | 负载上下文 | 这是一个新负载还是现有负载的迁移？如果迁移，源系统是什么（例如，NetApp、ZFS、Windows 文件服务器、Lustre、GPFS 等）？哪个应用程序或负载将访问此存储？它如何访问数据（API、文件协议、块设备）？客户端正在运行什么操作系统或平台？数据模型是什么（结构化/表格、向量嵌入、非结构化对象、文件系统）？ |
| 2 | 容量和访问模式 | 有多少数据，多少文件或对象，典型大小是多少？顺序访问还是随机访问模式？读重、写重还是混合？ |
| 3 | 性能要求 | 有特定的延迟、吞吐量或 IOPS 要求吗？预期的并发量是多少（同时访问的客户端或计算节点数量）？ |
| 4 | 可靠性和数据保护 | 恢复时间目标 (RTO) 是什么？恢复点目标 (RPO)？合规保留要求？跨区域弹性？不可变需求？ |
| 5 | 可用性 | 可以接受单 AZ 还是多 AZ？与特定计算共置？ |

使用存储选项表来识别候选服务，而不是裁剪服务；对常见工作负载列的关键字匹配不一定是唯一的答案。您必须使用下方路由部分检索每个候选服务的参考文件。

考虑这些因素，推荐特定的 AWS 存储服务，并：

1. 您必须包含与用户陈述要求紧密相关的明确理由。
2. 您必须在选择接近或依赖于未指定信息时提供替代方案，并解释权衡。

---

### 第 2b 步：INVESTIGATE 路径

用户知道他们的服务或方法，并需要操作帮助。

1. 根据下表对问题域进行分类，以确定哪个上下文很重要。

| 问题域 | 示例触发器 | 需要澄清什么 |
| --- | --- | --- |
| 迁移和数据传输 | "我该如何将我的数据迁移到 AWS？", "设置 DataSync", "从本地 NFS 同步到 EFS", 源到目标问题 | 源系统和协议、目标服务、数据量、到 AWS 的网络路径（Direct Connect、VPN、互联网） |
| 数据保护和弹性 | "设置备份", "跨区域复制", "我的灾难恢复策略是什么？", "RTO 小于 1 小时", 故障转移、不可变 | 故障场景（删除、损坏、AZ/区域丢失、合规保留）、RTO 和 RPO 目标、复制范围（同一区域、跨区域、跨账户） |
| 成本和生命周期 | "减少我的存储账单", "调整我的卷大小", "成本优化", 生命周期规则、分层决策、存储类别选择 | 当前服务和配置、访问频率（每天、每周、很少）、数据量和增长轨迹 |
| 性能 | "我的读取很慢", "吞吐量瓶颈", "我需要更多的 IOPS", 尺寸 | 观察到的与要求的对比（延迟、IOPS 或吞吐量）、访问模式（随机/顺序、读写混合）、是否怀疑存储、计算或网络是瓶颈 |
| 安全性和合规性 | "静态加密", "限制存储桶访问", "满足 HIPAA", 访问控制、合规框架 | 安全目标（限制访问、审计访问、加密、隔离网络、满足合规要求），如果有合规框架 |
| 配置和指导 | "在 EKS 上挂载 EFS", "设置复制", "服务 X 支持吗？", 部署步骤、最佳实践 | 客户端环境（操作系统、计算类型、VPC/本地）、目标操作或功能 |
| 故障排除 | "遇到 AccessDenied 错误", "挂载挂起", "意外的延迟激增", "为什么我的生命周期规则没有转换？" | 错误消息或症状、最近发生了什么变化、他们尝试了什么 |

<!-- markdownlint-disable MD029 -->
2. 根据列出的“需要澄清什么”询问范围问题，以获取查询中尚未包含的信息。如果缺少的详细信息不会改变指导，则假设声明而不是等待询问更多问题。
3. 您必须使用下方路由部分检索所有候选服务的参考文件。
4. 提供具体、可操作的指导、注意事项和文档链接的答案。
5. 在回答配置或安全问题时，您必须建议启用访问日志记录、CloudTrail 数据事件和 CloudWatch 指标，以实现可观察性。
<!-- markdownlint-enable MD029 -->

## 存储选项

此技能涵盖的 AWS 存储服务，按存储类别分组。有关存储类别的更多信息，请参阅 [块、文件和对象存储比较](https://aws.amazon.com/compare/the-difference-between-block-file-object-storage/)。

### 对象存储

| 服务 | 关键特性 | 常见工作负载 |
| --- | --- | --- |
| S3 通用 | 几乎无限扩展的对象存储，具有多个存储类别，涵盖频繁访问到低成本归档；生命周期规则将数据移动到针对较少频繁访问数据优化的低成本存储类别。区域可用性。通过 REST/HTTP API 从任何地方访问。 | 数据湖和分析、备份和归档目标、ML 训练数据、媒体存储和内容分发、日志和事件数据、静态网站和应用程序资源、监管和合规归档 |
| S3 Express One Zone | 单 AZ 目录存储桶，针对频繁访问的延迟敏感数据优化，延迟为个位数毫秒。 | 大规模 ML 训练和推理、Spark 和 EMR 洗牌、ML 检查点、草稿、模型加载、ETL 中间数据、交互式分析（热分区）、可观察性和日志分析（热层）、Kafka 分层存储、媒体和视频编辑、高频事务访问、机器学习推理的缓存 |
| S3 表格 | S3 上的托管 Apache Iceberg 表格，具有自动压缩和查询优化。区域可用性。专为使用 SQL 引擎查询的结构化、表格数据而设计。 | 数据湖表、结构化分析数据、ETL 管道输出、流式传输到表格以进行 SQL 分析、迁移到 S3 或自管理的 Iceberg 外部的开放表格式数据 |
| S3 向量 | 在 S3 上进行向量存储和相似性搜索，原生支持以经济高效的方式存储和查询向量嵌入。提供与 S3 通用存储桶相同的弹性、可靠性和可用性。区域可用性。 | RAG 管道、语义搜索、推荐系统、向量去重和匹配、异常和欺诈检测、AI 代理内存、经济高效的存储大型向量数据集 |
| S3 元数据 | 可查询的对象元数据，存储在完全托管的只读 Apache Iceberg 表格中，包括系统定义的详细信息、用户定义的元数据、对象标签和注释 | 业务分析、内容目录、数据治理和合规性、存储优化、实时推理应用程序、AI 代理 |

### 文件存储

在命名服务时，您必须始终指定完整名称（FSx for Lustre、FSx for Windows File Server、FSx for NetApp ONTAP 或 FSx for OpenZFS）。EFS 和 S3 文件可以由 Lambda 和 Fargate 挂载。使用最新 AWS 文档验证可以从无服务器计算挂载的附加服务。FSx for NetApp ONTAP 和 FSx for OpenZFS 数据可以通过 S3 Access Points for FSx 从无服务器计算和基于 S3 的管道访问（通过 S3 API 暴露文件数据，而无需复制；在用户需要从 S3 原生消费者或分析服务读取 FSx 居住数据时呈现此内容）。

| 服务 | 关键特性 | 常见工作负载 |
| --- | --- | --- |
| EFS | EFS 标准、EFS 不频繁访问 (EFS IA) 和 EFS 归档存储类别，由 EFS 生命周期管理管理，以实现自动成本优化。无服务器弹性 NFS，无需容量规划或配置，可由 Lambda、Fargate、EC2、ECS 和 EKS 挂载。默认多 AZ（区域）或单 AZ。跨多个并发客户端提供最高聚合吞吐量的最简单路径，用于共享 Linux 文件访问。 | 容器（ECS、EKS、Fargate）、云原生 Linux 应用程序、无服务器持久存储、分析和 ML 训练数据（包括 SageMaker）、大数据、媒体处理、内容管理、共享主目录、Web 服务、开发/测试、不经常访问的文件数据 |
| FSx for Lustre | SSD 和智能分层存储类别，其中智能分层是完全弹性的，SSD 是固定容量的。为跨许多计算节点提供非常高的聚合吞吐量的并行文件系统，用于大规模并行访问。 | 大规模的 ML 和 GPU 训练和推理、HPC、基因组学和地震处理、金融建模、媒体渲染、后端 EDA |
| FSx for OpenZFS | 智能分层和 SSD，具有 ZFS 数据管理（即时可写的克隆、快照、压缩、按需复制）。非常低延迟和高 IOPS，易于操作且对性能敏感的工作负载和快速开发/测试周期具有成本效益。单 AZ 和多 AZ 部署模型。通过 S3 Access Points for FSx 提供 S3-API 访问。 | 数据库（包括在 EC2 上）、快速克隆的开发/测试、ZFS 或 Linux-NFS 迁移、前端 EDA、金融建模、媒体处理、延迟敏感的业务应用程序 |
| FSx for NetApp ONTAP | 完全 ONTAP 数据管理（SnapMirror 复制、FlexClone、去重、压缩、SnapLock WORM、QoS、vscan 抗病毒、文件访问审计）。多协议：NFS、SMB、iSCSI、NVMe-over-TCP 和通过 S3 Access Points for FSx 的 S3-API 访问。可扩展到高聚合吞吐量和 IOPS。单 AZ 和多 AZ 部署模型。 | 企业网络附加存储 (NAS) 迁移、多协议环境、通用文件共享和主目录、业务关键数据库（包括在 EC2 上）（SAP HANA、Oracle、SQL Server）、VMware 数据存储、业务应用程序（医学影像、产品生命周期管理）、前端 EDA（芯片设计和验证）、混合和灾难恢复 |
| FSx for Windows File Server | 基于 Windows Server 的完全托管 SMB 文件存储，具有 Active Directory 身份（Kerberos、NTFS ACL）、DFS 命名空间、阴影副本和 FSRM 配额；共享也可以从 Linux 和 macOS 客户端访问。单 AZ 和多 AZ 部署模型。 | Windows 文件、主目录和部门共享、.NET 应用程序、Microsoft SQL Server、Windows Server 迁移 |

### 块存储

| 服务 | 主要特性 | 常见工作负载 |
| --- | --- | --- |
| EBS | 网络连接到 EC2 实例的高性能虚拟磁盘。耐用、可调整大小的 SSD 或 HDD，独立于实例持续存在，支持快照备份、基于时间的快照复制，并在 gp3 上独立于容量提供性能（请确认最新卷限制）。支持即时卷克隆。区域范围。 | 数据库、事务性应用程序和文件系统、启动卷、开发/测试环境、顺序批处理、日志和数据仓库扫描 |
| EC2 实例存储 | 物理上集成在主机服务器中的本地 SSD 存储，提供最低延迟和最高吞吐量。易失性：如果实例停止或硬件故障，数据将丢失。 | 可以承受丢失的临时临时数据、缓存和缓冲区 |

---

## 跨服务重叠

某些存储功能跨越类别边界，使得一个类别的服务具有通常与另一个类别关联的接口。当工作负载需要从多个协议或接口访问共享数据时，才显示这些功能。

| 功能 | 它所支持的功能 | 它是什么 | 其他来源 |
| --- | --- | --- | --- |
| S3 文件 | 使 S3 数据可访问文件应用程序 | 基于 EFS 基础设施的 S3 桶上的完全管理的 NFS 文件访问。数据作为系统记录保留在 S3 中。文件锁定、POSIX 权限和完全读写。当数据已存在于 S3 中，并且需要文件路径访问和对象访问时，选择 EFS。 | `references/s3-files-knowledge.md`，`references/efs-knowledge.md` |
| FSx 的 S3 访问点 | 使驻留在 FSx 中的数据可访问基于 S3 的应用程序和服务 | 通过 S3 API 暴露 FSx for NetApp ONTAP 或 FSx for OpenZFS 数据，而无需将其复制到存储桶。当文件数据必须到达 S3 原生消费者，或无服务器或基于 S3 的应用程序需要访问驻留在 FSx for NetApp ONTAP 或 FSx for OpenZFS 中的数据时，显示。 | `references/fsx-ontap-knowledge.md`，`references/fsx-openzfs-knowledge.md` |

---

## 安全

AWS 的云安全是最高优先级，这是 AWS 和客户之间的共同责任。您必须在使用或配置存储资源时包含安全指南。您必须始终建议启用静态加密和传输加密。当静态加密是可选的或不是默认值时，必须在创建时明确建议启用它，因为创建后通常不可变。您必须建议将 IAM 策略范围限制到授权主机的最小权限。您必须建议在资源策略中添加条件键（例如，aws:SourceArn、aws:SourceAccount、aws:SourceVpc），以防止跨服务混淆代理攻击。您必须建议加密日志目标：AWS KMS 用于 CloudTrail 跟踪和 CloudWatch 日志组、服务器端加密用于服务器访问日志存储桶，以及 AWS KMS 用于 SNS 主题。优先选择短期凭证或基于 IAM 的身份验证（例如，通过自定义 IdP 使用临时令牌）而不是长期 SSH 密钥。当需要 SSH 密钥时，执行轮换策略并将私钥存储在 AWS Secrets Manager 中以支持服务。您必须建议将安全组入站规则限制为最窄的适用源（特定的客户端安全组或最小的 CIDR）。特定服务的安全控制、加密模型和文档链接在每个参考的服务信息表的“安全”行中；您必须在就建议该服务之前阅读它。

## 路由

通过 AWS MCP 服务器的 retrieve_skill 工具加载时：技能未安装在本地文件系统中。您必须使用带有文件参数的 retrieve_skill 检索每个参考（例如，file="references/s3-general-purpose-knowledge.md"）。不要在本地文件读取这些路径。在 AWS MCP 服务器外部加载时（例如，从 Agent Toolkit 的本地文件系统），直接从技能目录中的相对路径读取参考文件。

### 参考文件

| 主题 | 参考 |
| --- | --- |
| S3（通用） | `references/s3-general-purpose-knowledge.md` |
| S3 元数据 | `references/s3-general-purpose-knowledge.md` |
| S3 表格 | `references/s3-tables-knowledge.md` |
| S3 向量 | `references/s3-vectors-knowledge.md` |
| S3 Express One Zone | `references/s3-express-knowledge.md` |
| S3 文件 | `references/s3-files-knowledge.md` |
| Amazon EFS | `references/efs-knowledge.md` |
| FSx for Lustre | `references/fsx-lustre-knowledge.md` |
| FSx for NetApp ONTAP | `references/fsx-ontap-knowledge.md` |
| FSx for OpenZFS | `references/fsx-openzfs-knowledge.md` |
| FSx for Windows File Server | `references/fsx-windows-knowledge.md` |
| Amazon EBS | `references/ebs-knowledge.md` |
| 数据移动和保护（DataSync、传输系列、存储网关、AWS Backup） | `references/data-movement-and-protection-knowledge.md` |

### 专用技能

| 主题 | 参考 |
| --- | --- |
| S3 上的安全 | [`securing-s3-buckets`](https://github.com/aws/agent-toolkit-for-aws/tree/main/skills/specialized-skills/storage-skills/securing-s3-buckets) |
| 使用 S3 表格 | [`creating-data-lake-table`](https://github.com/aws/agent-toolkit-for-aws/tree/main/skills/specialized-skills/storage-skills/creating-data-lake-table) |
| 使用 S3 向量 | [`storing-and-querying-vectors`](https://github.com/aws/agent-toolkit-for-aws/tree/main/skills/specialized-skills/storage-skills/storing-and-querying-vectors) |
| 故障排除 S3 文件 | [`troubleshooting-s3-files`](https://github.com/aws/agent-toolkit-for-aws/tree/main/skills/specialized-skills/storage-skills/troubleshooting-s3-files) |
| 故障排除 EFS | [`troubleshooting-efs`](https://github.com/aws/agent-toolkit-for-aws/tree/main/skills/specialized-skills/storage-skills/troubleshooting-efs) |
| 查询 S3 系统表格 | [`querying-aws-s3`](https://github.com/aws/agent-toolkit-for-aws/tree/main/skills/specialized-skills/system-table-skills/querying-aws-s3) |
| 将数据摄取到数据湖 | [`ingesting-into-data-lake`](https://github.com/aws/agent-toolkit-for-aws/tree/main/skills/specialized-skills/analytics-skills/ingesting-into-data-lake) |
| 查找数据湖资产 | [`finding-data-lake-assets`](https://github.com/aws/agent-toolkit-for-aws/tree/main/skills/specialized-skills/analytics-skills/finding-data-lake-assets) |
| 查询数据湖 | [`querying-data-lake`](https://github.com/aws/agent-toolkit-for-aws/tree/main/skills/specialized-skills/analytics-skills/querying-data-lake) |
