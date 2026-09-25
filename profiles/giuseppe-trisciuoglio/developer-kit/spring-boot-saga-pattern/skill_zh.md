# Spring Boot Saga模式

## 概述

使用Saga模式在微服务之间实现分布式事务。用一系列本地事务和补偿操作替代两阶段提交。支持使用Kafka、RabbitMQ或Axon Framework实现协调（事件驱动）和编排（集中式协调器）方法。

## 何时使用

- 跨多个微服务构建分布式事务
- 用更可扩展的解决方案替代两阶段提交（2PC）
- 处理服务失败时的事务回滚
- 确保微服务架构中的最终一致性
- 实现失败操作的补偿事务
- 协调跨越多个服务复杂业务流程

**触发短语**：分布式事务、Saga模式、补偿事务、微服务事务、最终一致性、跨服务回滚、编排模式、协调模式

## 指南

### 1. 设计事务流程

映射操作序列及其补偿事务：

```
订单 → 支付 → 库存 → 发货
  ↓        ↓        ↓          ↓
取消  退款   释放    取消
```

**验证**：验证每个正向步骤都有对应的补偿。

### 2. 选择实现方法

| 方法 | 用例 | 技术栈 |
|------|------|-------|
| 协调 | 新建项目、少量参与者 | Spring Cloud Stream + Kafka/RabbitMQ |
| 编排 | 复杂工作流、现有系统 | Axon Framework, Eventuate Tram, Camunda |

**验证**：在做出选择前审查团队专业知识和系统复杂性。

### 3. 使用本地事务实现服务

每个服务原子地完成其本地ACID事务：

```java
@Service
@RequiredArgsConstructor
public class OrderService {
    private final OrderRepository orderRepository;
    private final KafkaTemplate<String, Object> kafka;

    @Transactional
    public Order createOrder(CreateOrderCommand cmd) {
        Order order = orderRepository.save(new Order(cmd.orderId(), cmd.items()));
        kafka.send("order.created", new OrderCreatedEvent(order.getId(), order.getItems()));
        return order;
    }
}
```

**验证**：测试本地事务提交前事件是否已发布。

### 4. 实现补偿事务

每个正向操作都需要幂等的补偿：

```java
@Service
@RequiredArgsConstructor
public class PaymentService {
    private final PaymentRepository paymentRepository;
    private final KafkaTemplate<String, Object> kafka;

    public void processPayment(PaymentRequest request) {
        Payment payment = paymentRepository.save(new Payment(request.orderId(), request.amount()));
        kafka.send("payment.processed", new PaymentProcessedEvent(payment.getId(), request.orderId()));
    }

    @Transactional
    public void refundPayment(String paymentId) {
        paymentRepository.findById(paymentId)
            .ifPresent(p -> {
                p.setStatus(REFUNDED);
                paymentRepository.save(p);
                kafka.send("payment.refunded", new PaymentRefundedEvent(paymentId));
            });
    }
}
```

**验证**：确认补偿可以安全地多次执行（幂等性）。

### 5. 配置消息代理

使用幂等消费者配置Kafka：

```java
@Configuration
@EnableKafka
public class KafkaConfig {
    @Bean
    public ConcurrentKafkaListenerContainerFactory<String, Object> kafkaListenerContainerFactory(
            ConsumerFactory<String, Object> consumerFactory) {
        ConcurrentKafkaListenerContainerFactory<String, Object> factory =
            new ConcurrentKafkaListenerContainerFactory<>();
        factory.setConsumerFactory(consumerFactory);
        factory.setCommonErrorHandler(new DefaultErrorHandler());
        return factory;
    }
}
```

**验证**：启用事务ID并验证精确一次语义。

### 6. 实现Saga编排器（仅限编排）

```java
@Service
@RequiredArgsConstructor
public class OrderSagaOrchestrator {
    private final KafkaTemplate<String, Object> kafka;
    private final SagaStateRepository sagaStateRepo;

    public void startSaga(OrderRequest request) {
        String sagaId = UUID.randomUUID().toString();
        sagaStateRepo.save(new SagaState(sagaId, STARTED, LocalDateTime.now()));
        kafka.send("saga.order.start", new StartOrderSagaCommand(sagaId, request));
    }

    @KafkaListener(topics = "payment.failed")
    public void handlePaymentFailed(PaymentFailedEvent event) {
        kafka.send("order.compensate", new CompensateOrderCommand(event.getSagaId()));
        kafka.send("inventory.compensate", new ReleaseInventoryCommand(event.getSagaId()));
        sagaStateRepo.updateStatus(event.getSagaId(), FAILED);
    }
}
```

**验证**：验证在发送命令前Saga状态是否持久化。检查每个失败路径上的补偿触发。

### 7. 实现事件处理器（仅限协调）

```java
@Service
public class OrderEventHandler {
    private final OrderService orderService;
    private final KafkaTemplate<String, Object> kafka;

    @KafkaListener(topics = "payment.processed", groupId = "order-service")
    public void onPaymentProcessed(PaymentProcessedEvent event) {
        try {
            InventoryReservedEvent result = orderService.reserveInventory(event.toInventoryRequest());
            kafka.send("inventory.reserved", result);
        } catch (InsufficientInventoryException e) {
            kafka.send("inventory.insufficient", new InsufficientInventoryEvent(event.getOrderId(), event.getPaymentId()));
        }
    }
}
```

**验证**：测试每个事件处理器是否正确触发下一步或补偿。

### 8. 添加监控和可观测性

```java
@Configuration
public class SagaMetricsConfig {
    @Bean
    public MeterRegistry meterRegistry() {
        return new PrometheusMeterRegistry(PrometheusConfig.DEFAULT);
    }
}
```

跟踪：Saga执行时长、补偿次数、失败率、卡顿Saga。

**验证**：为超出预期时长的Saga设置警报。

## 最佳实践

**设计**：
- 使用数据库约束或去重表使补偿事务**幂等**
- 使用**不可变事件**（Java记录）防止意外修改
- 将Saga状态存储在持久化存储中以便恢复

**错误处理**：
- 为服务间调用实现**断路器**
- 使用**死信队列**处理超出重试限制的消息
- 为每个Saga步骤设置适当的**超时**（默认30秒，可配置）

**监控**：
- 跟踪Saga状态：PENDING、COMPLETED、COMPENSATING、FAILED
- 监控补偿执行时间
- 当Saga超出SLA时长时发出警报

## 限制和警告

- 每个正向事务**必须**有对应的补偿事务
- 补偿事务**必须**幂等以处理重试场景
- Saga状态**必须**持久化以处理失败和恢复
- 永远不要在Saga参与者之间使用同步通信
- Saga提供最终一致性而非强一致性
- 测试所有失败场景包括部分失败
- 考虑使用Axon Framework或Eventuate处理复杂编排
- 确保消息代理高度可用

## 示例

### 基于协调的Saga

```java
// Application.java
@SpringBootApplication
@EnableKafka
@EnableKafkaListeners
public class OrderApplication {
    public static void main(String[] args) {
        SpringApplication.run(OrderApplication.class, args);
    }
}

// 事件类（不可变）
public record OrderCreatedEvent(String orderId, List<OrderItem> items) {}
public record PaymentProcessedEvent(String paymentId, String orderId) {}
public record InventoryReservedEvent(String reservationId, String orderId) {}
public record PaymentFailedEvent(String orderId, String reason) {}
public record InsufficientInventoryEvent(String orderId, String paymentId) {}

// OrderService带补偿
@Service
@RequiredArgsConstructor
public class OrderService {
    private final OrderRepository orderRepository;
    private final KafkaTemplate<String, Object> kafka;

    @KafkaListener(topics = "payment.failed", groupId = "order-service")
    public void handleCompensation(PaymentFailedEvent event) {
        orderRepository.findByOrderId(event.orderId())
            .ifPresent(order -> {
                order.setStatus(CANCELLED);
                orderRepository.save(order);
            });
    }
}
```

### 基于Axon Framework的编排Saga

```java
// 命令
@Aggregate
public class OrderAggregate {
    @AggregateIdentifier
    private String orderId;

    @CommandHandler
    public OrderAggregate(CreateOrderCommand cmd) {
        apply(new OrderCreatedEvent(cmd.orderId(), cmd.items()));
    }

    @EventSourcingHandler
    public void on(OrderCreatedEvent event) {
        this.orderId = event.orderId();
    }

    @CommandHandler
    public void handle(CancelOrderCommand cmd) {
        apply(new OrderCancelledEvent(cmd.orderId(), cmd.reason()));
    }
}
```

## 参考文献

- [Saga模式定义](references/saga-pattern-definition.md)
- [协调实现](references/choreography-implementation.md)
- [编排实现](references/orchestration-implementation.md)
- [补偿事务](references/compensating-transactions.md)
- [状态管理](references/state-management.md)
- [错误处理和重试](references/error-handling-retry.md)
- [测试策略](references/testing-strategies.md)
- [陷阱和解决方案](references/pitfalls-solutions.md)
- [示例](references/examples.md)
