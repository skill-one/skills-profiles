# AWS SDK for Java 2.x - 消息 (SQS & SNS)

## 概述

提供 AWS SDK for Java 2.x 的 SQS 队列和 SNS 主题模式：客户端设置、队列管理、消息操作、订阅和 Spring Boot 集成。

## 何时使用

- 设置 SQS 队列（标准或 FIFO）用于消息缓冲
- 使用 SNS 主题和订阅实现发布/订阅
- 使用长轮询处理 SQS 队列中的消息
- 配置死信队列（DLQ）用于错误处理
- 将 AWS 消息与 Spring Boot 应用集成
- 使用 SQS/SNS 构建事件驱动架构

## 示例

### 快速设置

**依赖项：**
```xml
<dependency>
    <groupId>software.amazon.awssdk</groupId>
    <artifactId>sqs</artifactId>
</dependency>
<dependency>
    <groupId>software.amazon.awssdk</groupId>
    <artifactId>sns</artifactId>
</dependency>
```

**客户端配置：**
```java
SqsClient sqsClient = SqsClient.builder()
    .region(Region.US_EAST_1)
    .credentialsProvider(DefaultCredentialsProvider.create())
    .build();

SnsClient snsClient = SnsClient.builder()
    .region(Region.US_EAST_1)
    .build();
```

### SQS 操作

**创建并发送消息：**
```java
String queueUrl = sqsClient.createQueue(CreateQueueRequest.builder()
    .queueName("my-queue")
    .build()).queueUrl();

String messageId = sqsClient.sendMessage(SendMessageRequest.builder()
    .queueUrl(queueUrl)
    .messageBody("Hello, SQS!")
    .build()).messageId();
```

**接收并删除消息：**
```java
ReceiveMessageResponse response = sqsClient.receiveMessage(ReceiveMessageRequest.builder()
    .queueUrl(queueUrl)
    .maxNumberOfMessages(10)
    .waitTimeSeconds(20)
    .build());

response.messages().forEach(message -> {
    processMessage(message.body());
    sqsClient.deleteMessage(DeleteMessageRequest.builder()
        .queueUrl(queueUrl)
        .receiptHandle(message.receiptHandle())
        .build());
});
```

**FIFO 队列：**
```java
Map<QueueAttributeName, String> attributes = Map.of(
    QueueAttributeName.FIFO_QUEUE, "true",
    QueueAttributeName.CONTENT_BASED_DEDUPLICATION, "true"
);

String fifoQueueUrl = sqsClient.createQueue(CreateQueueRequest.builder()
    .queueName("my-queue.fifo")
    .attributes(attributes)
    .build()).queueUrl();

sqsClient.sendMessage(SendMessageRequest.builder()
    .queueUrl(fifoQueueUrl)
    .messageBody("Order #12345")
    .messageGroupId("orders")
    .messageDeduplicationId(UUID.randomUUID().toString())
    .build());
```

### SNS 操作

**创建主题并发布：**
```java
String topicArn = snsClient.createTopic(CreateTopicRequest.builder()
    .name("my-topic")
    .build()).topicArn();

snsClient.publish(PublishRequest.builder()
    .topicArn(topicArn)
    .subject("Test Notification")
    .message("Hello, SNS!")
    .build());
```

**SNS 到 SQS 订阅：**
```java
String queueArn = sqsClient.getQueueAttributes(GetQueueAttributesRequest.builder()
    .queueUrl(queueUrl)
    .attributeNames(QueueAttributeName.QUEUE_ARN)
    .build()).attributes().get(QueueAttributeName.QUEUE_ARN);

snsClient.subscribe(SubscribeRequest.builder()
    .protocol("sqs")
    .endpoint(queueArn)
    .topicArn(topicArn)
    .build());
```

### Spring Boot 集成
```java
@Service
@RequiredArgsConstructor
public class OrderNotificationService {
    private final SnsClient snsClient;
    private final ObjectMapper objectMapper;

    @Value("${aws.sns.order-topic-arn}")
    private String orderTopicArn;

    public void sendOrderNotification(Order order) throws JsonProcessingException {
        snsClient.publish(PublishRequest.builder()
            .topicArn(orderTopicArn)
            .subject("New Order Received")
            .message(objectMapper.writeValueAsString(order))
            .messageAttributes(Map.of(
                "orderType", MessageAttributeValue.builder()
                    .dataType("String")
                    .stringValue(order.getType())
                    .build()))
            .build());
    }
}
```

## 说明

### 实现消息处理（带验证）

1. **创建队列/主题** 使用适当的配置
2. **发送消息** 并验证返回 `messageId`
3. **接收消息** 使用长轮询 (`waitTimeSeconds: 20`)
4. **处理消息** - 在处理前验证负载
5. **删除消息** 仅在成功处理后删除 - 验证删除响应
6. **定期检查 DLQ** 使用 `redrivePolicy` 查找失败消息
7. **验证投递** - 监控 CloudWatch `NumberOfMessagesSent` 指标

**验证清单：**
```java
// 发送后
if (messageId == null || messageId.isEmpty()) {
    throw new MessagingException("消息发送失败 - 未返回 messageId");
}

// 接收后
if (response.messages().isEmpty()) {
    log.debug("无可用消息 - 长轮询正常");
}

// 删除后
if (!deleteResponse.sdkHttpResponse().isSuccessful()) {
    throw new MessagingException("消息删除失败");
}
```

### 设置凭证
```bash
export AWS_ACCESS_KEY_ID=your-access-key
export AWS_SECRET_ACCESS_KEY=your-secret-key
export AWS_REGION=us-east-1
```

### 监控和调试
- CloudWatch 指标：`ApproximateNumberOfMessages`, `NumberOfMessagesSent`, `NumberOfMessagesReceived`
- 启用 SDK 日志：`software.amazon.awssdk` 级别为 DEBUG
- 使用 X-Ray 进行分布式跟踪

## 最佳实践

**SQS:**
- 使用长轮询（20-40s）减少空响应和成本
- 成功处理后始终删除消息
- 实现幂等处理以处理重复消息
- 配置死信队列（DLQ）（`redrivePolicy`）用于失败消息
- 需要顺序时使用 FIFO 队列（300 msg/sec 限制）

**SNS:**
- 使用过滤策略减少不必要的投递
- 消息大小保持在 256KB 以下
- 实现指数退避重试
- 监控 `NumberOfNotificationFailed` 指标

**通用：**
- 使用 IAM 角色而非静态凭证
- 重用客户端（它们是线程安全的）
- 使用 LocalStack 或 Testcontainers 进行测试

## 详细参考

- [references/detailed-sqs-operations.md](references/detailed-sqs-operations.md)
- [references/detailed-sns-operations.md](references/detailed-sns-operations.md)
- [references/spring-boot-integration.md](references/spring-boot-integration.md)
- [references/aws-official-documentation.md](references/aws-official-documentation.md)

## 限制和警告

- **消息大小**：SQS 和 SNS 最大 256KB
- **可见性超时**：超时后未删除的消息会重新出现 - 处理后始终删除
- **输入验证**：处理前清理消息体 - 消息可能包含不可信的负载
- **FIFO 命名**：必须以 `.fifo` 后缀结尾
- **FIFO 吞吐量**：每个队列 300 msg/sec（使用分区提高吞吐量）
- **消息保留**：SQS 最多保留 14 天
- **DLQ 必须配置**：配置死信队列防止消息丢失
- **区域特定**：SQS 队列是区域特定的；跨区域需要 SNS
