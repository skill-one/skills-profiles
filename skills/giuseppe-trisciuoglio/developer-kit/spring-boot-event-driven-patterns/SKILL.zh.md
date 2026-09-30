---
name: spring-boot-event-driven-patterns
description: 为 Spring Boot 提供事件驱动架构（EDA）模式——创建领域事件、配置 ApplicationEvent 和 @TransactionalEventListener、设置 Kafka 生产者和消费者，并实现事务性输出箱模式以进行可靠的分布式消息传递。适用于在 Spring Boot 中实现事件驱动系统、使用 Kafka 设置异步消息、从 DDD 聚合发布领域事件，或需要使用输出箱模式进行可靠事件发布的情况。
---

# Spring Boot 事件驱动模式

## 概述

使用领域事件、`ApplicationEventPublisher`、`@TransactionalEventListener` 以及 Kafka 和 Spring Cloud Stream 的分布式消息，在 Spring Boot 3.x 中实现事件驱动架构（EDA）模式。

## 何时使用

- 使用 Kafka 消息实现事件驱动的微服务
- 在 DDD 架构中从聚合根发布领域事件
- 设置在数据库提交后触发的交易性事件监听器
- 通过 Spring Kafka 添加生产者和消费者的异步消息
- 使用交易性输出模式确保可靠的事件传递
- 使用事件驱动的服务间通信替换同步调用

## 快速参考

| 概念 | 描述 |
|------|------|
| **领域事件** | 扩展 `DomainEvent` 基类的不变事件，包含 eventId、occurredAt、correlationId |
| **事件发布** | `ApplicationEventPublisher.publishEvent()` 用于本地，`KafkaTemplate` 用于分布式 |
| **事件监听** | `@TransactionalEventListener(phase = AFTER_COMMIT)` 用于可靠处理 |
| **Kafka** | `@KafkaListener(topics = "...")` 用于分布式事件消费 |
| **Spring Cloud Stream** | 使用 `Consumer` bean 的函数式编程模型 |
| **输出模式** | 带有业务数据的原子事件存储和计划发布者 |

## 示例

### 单体到事件驱动的重构

**之前（反模式）：**
```java
@Transactional
public Order processOrder(OrderRequest request) {
    Order order = orderRepository.save(request);
    inventoryService.reserve(order.getItems()); // 阻塞
    paymentService.charge(order.getPayment()); // 阻塞
    emailService.sendConfirmation(order); // 阻塞
    return order;
}
```

**之后（事件驱动）：**
```java
@Transactional
public Order processOrder(OrderRequest request) {
    Order order = Order.create(request);
    orderRepository.save(order);

    // 事务提交后发布事件
    eventPublisher.publishEvent(new OrderCreatedEvent(order.getId(), order.getItems()));

    return order;
}

@Component
public class OrderEventHandler {
    @TransactionalEventListener(phase = TransactionPhase.AFTER_COMMIT)
    public void handleOrderCreated(OrderCreatedEvent event) {
        // 在订单保存后异步执行
        inventoryService.reserve(event.getItems());
        paymentService.charge(event.getPayment());
    }
}
```

有关完整工作示例，请参阅 [examples.md](references/examples.md)。

## 指令

### 1. 设计领域事件

创建扩展基本 `DomainEvent` 类的不变事件类：

```java
public abstract class DomainEvent {
    private final UUID eventId;
    private final LocalDateTime occurredAt;
    private final UUID correlationId;
}

public class ProductCreatedEvent extends DomainEvent {
    private final ProductId productId;
    private final String name;
    private final BigDecimal price;
}
```

有关模式，请参阅 [domain-events-design.md](references/domain-events-design.md)。

### 2. 从聚合发布事件

将领域事件添加到聚合根，通过 `ApplicationEventPublisher` 发布：

```java
@Service
@Transactional
public class ProductService {
    public Product createProduct(CreateProductRequest request) {
        Product product = Product.create(request.getName(), request.getPrice(), request.getStock());
        repository.save(product);

        product.getDomainEvents().forEach(eventPublisher::publishEvent);
        product.clearDomainEvents();

        return product;
    }
}
```

有关 DDD 模式，请参阅 [aggregate-root-patterns.md](references/aggregate-root-patterns.md)。

### 3. 事务性处理事件

使用 `@TransactionalEventListener` 进行可靠的事件处理：

```java
@Component
public class ProductEventHandler {
    @TransactionalEventListener(phase = TransactionPhase.AFTER_COMMIT)
    public void onProductCreated(ProductCreatedEvent event) {
        notificationService.sendProductCreatedNotification(event.getName());
    }
}
```

**验证：** 通过检查数据库状态在处理程序执行之前已提交，确认事件处理程序仅在事务提交后触发。

有关处理模式，请参阅 [event-handling.md](references/event-handling.md)。

### 4. 配置 Kafka 基础设施

配置用于发布的 KafkaTemplate，用于消费的 `@KafkaListener`：

```yaml
spring:
  kafka:
    bootstrap-servers: localhost:9092
    producer:
      value-serializer: org.springframework.kafka.support.serializer.JsonSerializer
```

**验证：** 通过 `KafkaTemplate` 发送测试事件，并在继续到生产模式之前确认它出现在消费者日志中。

有关依赖项设置，请参阅 [dependency-setup.md](references/dependency-setup.md) 和 [configuration.md](references/configuration.md)。

### 5. 实现 Outbox 模式

创建用于原子事件存储的 `OutboxEvent` 实体：

```java
@Entity
public class OutboxEvent {
    private UUID id;
    private String aggregateId;
    private String eventType;
    private String payload;
    private LocalDateTime publishedAt;
}
```

**验证：** 通过检查 `publishedAt` 时间戳在计划运行后是否设置，确认计划处理器拾取挂起事件。

计划处理器发布挂起事件。有关 Outbox 模式，请参阅 [outbox-pattern.md](references/outbox-pattern.md)。

### 6. 处理失败场景

实现重试逻辑、死信队列、幂等处理程序：

```java
@RetryableTopic(attempts = "3")
@KafkaListener(topics = "product-events")
public void handleProductEvent(ProductCreatedEventDto event) {
    orderService.onProductCreated(event);
}
```

**验证：** 确认消息在用尽重试后到达死信主题之前进行可观察性。

### 7. 添加可观察性

启用 Spring Cloud Sleuth 进行分布式跟踪，监控指标。

## 最佳实践

- **使用过去时命名**：`ProductCreated`（而不是 `CreateProduct`）
- **保持事件不变**：所有字段应为 final
- **包含关联 ID**：用于跨服务跟踪事件
- **使用 AFTER_COMMIT 阶段**：确保事件在成功的数据库事务后发布
- **实现幂等处理程序**：优雅处理重复事件
- **添加重试机制**：对于失败的事件处理，使用指数退避
- **实现死信队列**：对于重试后仍无法处理的事件
- **记录所有失败**：包含足够的上下文以进行调试
- **使处理程序无序**：事件顺序在分布式系统中无法保证
- **批量处理事件**：在处理高容量时
- **监控事件延迟**：为慢速处理设置警报

## 参考

- **[dependency-setup.md](references/dependency-setup.md)** — Maven/Gradle 依赖项
- **[configuration.md](references/configuration.md)** — Kafka 和 Spring Cloud Stream 配置
- **[domain-events-design.md](references/domain-events-design.md)** — 领域事件设计模式
- **[aggregate-root-patterns.md](references/aggregate-root-patterns.md)** — 带有事件发布的聚合根
- **[event-publishing.md](references/event-publishing.md)** — 本地和分布式事件发布
- **[event-handling.md](references/event-handling.md)** — 事件处理和消费模式
- **[outbox-pattern.md](references/outbox-pattern.md)** — 用于可靠性的交易性输出模式
- **[testing-strategies.md](references/testing-strategies.md)** — 单元和集成测试方法
- **[examples.md](references/examples.md)** — 完整工作示例
- **[event-driven-patterns-reference.md](references/event-driven-patterns-reference.md)** — 详细参考文档

## 限制和警告

- 使用 `@TransactionalEventListener` 发布的事件仅在事务提交后触发
- 避免在事件中发布大型对象（内存压力、序列化问题）
- 对异步事件处理程序要小心（单独线程、并发问题）
- Kafka 消费者必须处理重复消息（实现幂等处理）
- 分布式系统中事件顺序无法保证（设计无序处理程序）
- 在主事务线程上的事件监听器中永远不要执行阻塞操作
- 监控事件处理积压（指示系统容量问题）

## 相关技能

- `spring-boot-security-jwt` — 用于安全事件发布的 JWT 认证
- `spring-boot-test-patterns` — 测试事件驱动应用程序
- `aws-sdk-java-v2-lambda` — 使用 AWS Lambda 的事件驱动处理
- `langchain4j-tool-function-calling-patterns` — AI 驱动的事件处理
