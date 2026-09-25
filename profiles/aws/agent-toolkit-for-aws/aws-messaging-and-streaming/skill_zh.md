# AWS 消息与流服务

在回答 AWS 消息和流相关问题时，应从服务特定技能或官方 AWS 文档中核实具体数字、版本、限制和行为细节。不确定时，应搜索技能或文档而不是猜测。虚构的配置选项或错误的版本号比承认不确定性更糟糕。

当问题询问推荐配置（CloudWatch 报警设置、阈值、缺失数据处理）时，应搜索服务特定技能或文档而不是依赖通用最佳实践。

## 概述

选择和使用 AWS 服务在生产者和消费者之间移动数据的领域专业知识。
此技能涵盖两个基本模式——**消息**和**流**——以及实现每个模式的 AWS 服务。
它还标志着与**客户通信**的边界——消息传递给人类而不是应用程序组件——并将这些问题路由到拥有每个渠道的技能或 AWS 文档（参见客户通信（应用程序到人））。
使用此技能来决定哪个模式适用于工作负载、选择正确的服务，并了解服务如何相互集成。

有关特定 AWS 服务的具体指导，请参阅参考文件或服务特定技能。

## 流与消息

### 什么是消息？

消息使组件之间能够进行**解耦、异步通信**。生产者发送消息；一个或多个消费者接收并处理它。处理完成后，消息通常会被删除。消息服务处理交付保证、重试和死信路由。

**主要特征：**

- 消息被一次性消费（点对点）或扩散（发布/订阅），然后被移除
- 无重放——一旦确认，消息就消失了
- 设计用于命令/请求工作负载、任务分配和事件通知

### 什么是流？

流使能够**有序、持久、高吞吐量的连续数据流**。生产者将记录追加到日志中；消费者从该日志中的位置读取。记录在可配置的保留期内持续存在，无论是否被消费。

**主要特征：**

- 记录在保留窗口内保持持久并可以重放
- 在分区/分片中严格有序
- 多个独立消费者可以在不同位置读取相同的数据
- 设计用于事件溯源、实时分析、变更数据捕获和持续处理

### 主要区别

| 维度 | 消息 | 流 |
|---|---|---|
| **数据生命周期** | 消费后删除 | 保留用于重放（几小时到无限期） |
| **排序** | 尽力而为（标准）或按组（FIFO） | 严格按分区/分片 |
| **消费者模型** | 竞争消费者（工作分配） | 独立读取者（按位置扩散） |
| **吞吐量模式** | 爆发式、可变 | 持续、高容量 |
| **重放** | 不支持（除死信队列重放外） | 本地支持——可在保留期内任何位置查找 |
| **典型延迟** | 毫秒（推送或短轮询） | 毫秒到低秒 |
| **扩展单元** | 并发（消费者/轮询器） | 分区或分片 |

### 消息用例

- 使用请求/响应或命令模式解耦微服务
- 在竞争消费者池中分配工作（任务队列）
- 扩散通知，其中每个订阅者独立操作
- 峰值工作负载，从队列缓冲中受益
- 迁移现有的 JMS/AMQP 应用程序（Amazon MQ）

### 流用例

- 连续、高吞吐量的数据摄取（日志、指标、点击流、IoT遥测）
- 事件溯源，其中消费者需要从任何时间点重放
- 多个独立消费者以不同方式处理相同的数据
- 实时分析、窗口聚合或复杂事件处理
- 变更数据捕获（CDC）管道

### 消息服务

这些服务通常用于消息工作负载。
有时流服务（Kinesis Data Streams、Managed Streaming for Apache Kafka）也用于消息工作负载，具体取决于用例和需求。

| 服务 | 适用于 | 主要区别 |
|---|---|---|
| **Amazon SQS** | 任务队列、解耦、缓冲 | 完全管理、无限吞吐量（标准）、精确一次（FIFO）、公平队列用于多租户工作负载 |
| **Amazon SNS** | 扩散、发布/订阅通知 | 推送给多个订阅者（SQS、Lambda、HTTP；电子邮件/SMS 端点适用于操作警报——对于客户电子邮件或 SMS 请参见客户通信（应用程序到人）） |
| **Amazon EventBridge** | 事件路由、跨账户/SAAS 集成 | 基于内容过滤、模式注册、200+ AWS 源集成 |
| **Amazon MQ** | 现有 JMS/AMQP/MQTT 应用的迁移 | 协议兼容性（ActiveMQ、RabbitMQ）用于遗留迁移 |

### 流服务

这些服务通常用于流工作负载。

| 服务 | 适用于 | 主要区别 |
|---|---|---|
| **Amazon Kinesis Data Streams** | 使用 AWS 原生消费者进行实时摄取 | 按需优势模式（即时扩展、无分片管理）、1-365 天保留 |
| **Amazon Data Firehose** | 零管理交付到存储/分析 | 自动扩展、缓冲、批处理并交付到目的地 |
| **Amazon Managed Service for Apache Flink** | 复杂流处理（连接、窗口、状态） | 完整的 Apache Flink 运行时——SQL、Java、Python API 用于有状态计算 |
| **Amazon MSK** | Kafka 原生工作负载、生态系统兼容性 | Apache Kafka API、Express 代理（3 倍吞吐量、20 倍更快扩展与标准代理相比）、广泛的连接器生态系统 |

## 客户通信（应用程序到人）

上述服务在应用程序之间移动数据，即同一应用程序的组件之间。
一组单独的 AWS 服务是应用程序到人（A2P）：它将消息传递给或从应用程序外部的接收者，例如客户和订阅者。
这两个组不能互换。

| 渠道 | 服务 | 技能 |
|---|---|---|
| 电子邮件 | **Amazon SES** | `amazon-ses` |
| WhatsApp | **AWS End User Messaging Social** | `aws-social-messaging` |
| SMS、MMS、RCS、语音 | **AWS End User Messaging SMS** | `aws-sms-voice` |
| 移动推送 | **AWS End User Messaging Push** | 无 |

直接从此部分回答两种类型的问题：工作负载属于哪个组，以及哪个服务拥有一个渠道。
对于其他所有客户通信问题——设置渠道、通过它发送或解决交付问题——不要从此技能回答：加载表格中命名的技能并从该技能回答。
加载时，使用 `aws___retrieve_skill(skill_name="<skill>")` 并使用表格中的确切名称，当 AWS MCP 服务器可用时；或从 Agent Toolkit 在 `skills/<skill>/SKILL.md` 读取技能文档。
如果表格显示无，或者无法加载命名的技能，请说明，然后使用文档工具（`aws___search_documentation`、`aws___read_documentation`）如果可用，或使用命名的服务的 AWS 文档否则。

## 常见集成陷阱

- **SQS 系统属性与用户消息属性：** 像`AWSTraceHeader`（由 X-Ray / EventBridge / Pipes 发送到 SQS DLQ 时设置）和 `SenderId`、`SentTimestamp` 这样的属性是 SQS *系统*属性，不是用户消息属性。它们默认情况下不会从 `ReceiveMessage` 返回——通过 `AttributeNames=[...]`（或 `MessageSystemAttributeNames`）明确请求它们，与 `MessageAttributeNames` 分开，后者获取用户属性。这对于 DLQ 很重要，其中跟踪头在系统属性上，而用户属性槽携带服务的失败元数据（例如 EventBridge 的 `RULE_ARN`、`ERROR_CODE`）。

- **SNS → Firehose → S3 记录分隔符：** 对于使用 `firehose` 协议并将数据发送到 S3 的 SNS 订阅，记录默认情况下已经是按行分隔的（NDJSON）。不要打开 Firehose 的 `AppendDelimiterToRecord`——SNS 本身发出换行符，启用处理器会产生双换行符。

- **EventBridge 规则目标 DLQ + SNS 订阅 DLQ 都需要一个 DLQ 队列策略。** 仅附加 DLQ 不够——DLQ 在其队列策略允许服务主体之前会静默丢弃消息。EventBridge：`PutTargets` 使用 `DeadLetterConfig.Arn=<DLQ>`，加上 SQS 策略 `Allow sqs:SendMessage` 为 `Service: events.amazonaws.com` 并使用 `aws:SourceArn` = 规则 ARN。SNS：`SetSubscriptionAttributes` `RedrivePolicy={"deadLetterTargetArn":"<DLQ>"}`，加上允许 `Service: sns.amazonaws.com` 由主题 ARN 范围限制的 SQS 策略。

- **SQS 生产默认值：长轮询 + 客户端管理加密。** 新队列默认为短轮询（`ReceiveMessageWaitTimeSeconds=0`）和 SSE-SQS（AWS 拥有的密钥）。对于生产环境，使用 `SetQueueAttributes` 并设置 `ReceiveMessageWaitTimeSeconds=20`（长轮询）和 `KmsMasterKeyId=<customer-managed key id/ARN>` 而不是 `alias/aws/sqs`。

- **代理和 Kafka 凭据属于 Secrets Manager，而不是连接字符串。** 不要在应用程序配置、环境变量、JAAS 文件或 IaC 中硬编码用户名、密码或 SASL/SCRAM 凭据。对于 Amazon MQ（ActiveMQ/RabbitMQ）存储代理用户为密钥，并在启动时获取；Lambda 事件源映射对于 Amazon MQ 需要代理凭据作为 Secrets Manager 密钥 ARN（`BASIC_AUTH`），而不是内联。对于 MSK SASL/SCRAM 密钥不是可选的：它必须以 `AmazonMSK_` 前缀命名，并使用**客户管理的** KMS 密钥加密（使用默认 `aws/secretsmanager` 密钥创建的密钥不能与集群关联），然后通过 `BatchAssociateScramSecret` 附加。Lambda 事件源映射对于 MSK（SASL/SCRAM 或 mTLS）和自管理的 Kafka 也引用 Secrets Manager 密钥 ARN 而不是内联凭据。启用旋转并仅将 IAM 读取访问权限（`secretsmanager:GetSecretValue`）限制在消费角色上。参见 AWS Well-Architected [SEC02-BP03 安全地存储和使用密钥](https://docs.aws.amazon.com/wellarchitected/latest/security-pillar/sec_identities_secrets.html)。

- **服务主体资源策略需要 `aws:SourceArn` / `aws:SourceAccount` 条件。** 当队列或主题策略授予服务主体（如 `events.amazonaws.com`、`sns.amazonaws.com` 或 `s3.amazonaws.com`）权限以 `sqs:SendMessage` 或 `sns:Publish` 时，省略源条件会打开混淆代理漏洞——任何 AWS 账户中的任何规则、主题或存储桶都可以驱动写入。使用 `aws:SourceArn`（特定规则/主题/存储桶/管道 ARN；使用 `ArnLike` 与 `*` 当 ARN 尚未完全已知时）和 `aws:SourceAccount`（您的账户 ID）对每个此类语句进行范围限制。对于 S3 事件通知，两个键都需要，因为 S3 存储桶 ARN 不携带账户 ID，所以仅 `aws:SourceArn` 不能限制账户。对于由 EventBridge 规则和 EventBridge Pipes（主体 `events.amazonaws.com` / `pipes.amazonaws.com`，`aws:SourceArn` = 规则或管道 ARN）使用的 IAM 角色的信任策略也是如此——不仅上述 DLQ 情况。参见 IAM 用户指南中关于 [混淆代理问题](https://docs.aws.amazon.com/IAM/latest/UserGuide/confused-deputy.html)。
