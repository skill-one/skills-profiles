# Spring Boot中的清洁架构、六边形架构与领域驱动设计

## 概述

本技能为Java 21+ Spring Boot 3.5+应用程序中实现清洁架构、六边形架构（端口与适配器）和领域驱动设计战术模式提供全面指导。它通过正确的分层和依赖管理，确保关注点清晰分离、框架无关的领域逻辑和高度可测试的代码库。

## 使用场景

- 架构新的Spring Boot应用程序，实现关注点清晰分离
- 重构紧密耦合的代码为可测试的分层架构
- 实现独立于框架和基础设施的领域逻辑
- 设计可替换实现的端口和适配器
- 应用领域驱动设计的战术模式（实体、值对象、聚合）
- 创建无Spring上下文依赖的可测试业务逻辑

## 指导

### 1. 理解核心概念

#### 清洁架构分层（依赖规则）

依赖项流向内部。内部层不知道外部层。

| 层级 | 责任 | Spring Boot等效 |
|------|------|----------------|
| **领域** | 实体、值对象、领域事件、仓库接口 | `domain/` - 无Spring注解 |
| **应用** | 用例、应用服务、DTO、端口 | `application/` - `@`Service, `@`Transactional |
| **基础设施** | 框架、数据库、外部API | `infrastructure/` - `@`Repository, `@`Entity |
| **适配器** | 控制器、呈现器、外部网关 | `adapter/` - `@`RestController |

#### 六边形架构（端口与适配器）

- **领域核心**：纯Java业务逻辑，无框架依赖
- **端口**：定义契约的接口（驱动和被驱动）
- **适配器**：具体实现（JPA、REST、消息传递）

#### 领域驱动设计战术模式

- **实体**：具有身份和生命周期的对象（例如，`Order`, `Customer`）
- **值对象**：不可变，由属性定义（例如，`Money`, `Email`）
- **聚合**：具有根实体的一致性边界
- **领域事件**：捕获重要的业务事件
- **仓库**：持久化抽象，在基础设施中实现

### 2. 组织包结构

遵循基于功能的包组织结构：

```
com.example.order/
├── domain/
│   ├── model/              # 实体、值对象
│   ├── event/              # 领域事件
│   ├── repository/         # 仓库接口（端口）
│   └── exception/          # 领域异常
├── application/
│   ├── port/in/            # 驱动端口（用例接口）
│   ├── port/out/           # 被驱动端口（外部服务接口）
│   ├── service/            # 应用服务
│   └── dto/                # 请求/响应DTO
├── infrastructure/
│   ├── persistence/        # JPA实体、仓库适配器
│   └── external/           # 外部服务适配器
└── adapter/
    └── rest/               # REST控制器
```

### 3. 实现领域层（无框架依赖）

领域层必须对Spring或任何框架无依赖。

- 使用Java记录实现不可变的值对象，内置验证
- 将业务逻辑放在实体中，而不是服务中（富领域模型）
- 在领域层定义仓库接口（端口）
- 使用强类型ID防止ID混淆
- 实现领域事件以解耦副作用
- 使用工厂方法创建实体以强制不变性

### 4. 实现应用层

- 在`application/port/in/`创建用例接口（驱动端口）
- 在`application/port/out/`创建外部服务接口（被驱动端口）
- 使用`@Service`和`@Transactional`实现应用服务
- 使用DTO处理请求/响应，与领域模型分离
- 成功操作后发布领域事件

### 5. 实现基础设施层（适配器）

- 在`infrastructure/persistence/`创建JPA实体
- 实现映射领域和JPA实体的仓库适配器
- 使用MapStruct或手动映射器进行领域-JPA转换
- 配置条件Bean以实现可替换的实现
- 将基础设施关注点与领域逻辑隔离

### 6. 实现适配器层（REST）

- 在`adapter/rest/`创建REST控制器
- 注入用例接口，而不是实现
- 在DTO上使用Bean Validation
- 返回适当的HTTP状态码和响应
- 使用全局异常处理器处理异常

### 7. 应用最佳实践

1. **依赖规则**：领域对Spring或其他框架无依赖
2. **不可变值对象**：使用Java记录实现具有内置验证的值对象
3. **富领域模型**：将业务逻辑放在实体中，而不是服务中
4. **仓库模式**：领域定义接口，基础设施实现
5. **领域事件**：解耦副作用与主要操作
6. **构造器注入**：通过final字段强制依赖
7. **DTO映射**：分离领域模型与API契约
8. **事务边界**：在应用服务中放置`@`Transactional
9. **工厂方法**：使用`Entity.create()`在构造时强制不变性
10. **分离JPA实体**：使用映射器将领域实体与JPA实体分离

### 8. 验证架构合规性

实现每层后，验证依赖规则是否得到遵守：

- **领域层检查**：运行`grep -r "@Service\|@Component\|@Autowired" domain/`确保无Spring导入
- **ArchUnit测试**：添加依赖测试以验证领域层无基础设施导入：
  ```java
  noClasses().that().resideInPackage("..domain..")
      .should().accessClassesThat().resideInAnyPackage("..spring..", "..infrastructure..");
  ```
- **实体暴露检查**：验证JPA实体从未从领域服务返回
- **事务检查**：确认`@`Transactional仅应用于应用层服务，从未应用于领域

### 9. 编写测试

- **领域测试**：无Spring上下文的纯单元测试，执行快速
- **应用测试**：使用Mockito模拟端口的单元测试
- **基础设施测试**：使用`@DataJpaTest`和Testcontainers的集成测试
- **适配器测试**：使用`@WebMvcTest`的控制器测试

## 示例

### 示例1：领域层 - 带领域事件的实体

```java
// domain/model/Order.java
public class Order {
    private final OrderId id;
    private final List<OrderItem> items;
    private Money total;
    private OrderStatus status;
    private final List<DomainEvent> domainEvents = new ArrayList<>();

    private Order(OrderId id, List<OrderItem> items) {
        this.id = id;
        this.items = new ArrayList<>(items);
        this.status = OrderStatus.PENDING;
        calculateTotal();
    }

    public static Order create(List<OrderItem> items) {
        validateItems(items);
        Order order = new Order(OrderId.generate(), items);
        order.domainEvents.add(new OrderCreatedEvent(order.id, order.total));
        return order;
    }

    public void confirm() {
        if (status != OrderStatus.PENDING) {
            throw new DomainException("Only pending orders can be confirmed");
        }
        this.status = OrderStatus.CONFIRMED;
    }

    public List<DomainEvent> getDomainEvents() {
        return List.copyOf(domainEvents);
    }

    public void clearDomainEvents() {
        domainEvents.clear();
    }
}
```

### 示例2：领域层 - 带验证的值对象

```java
// domain/model/Money.java (值对象)
public record Money(BigDecimal amount, Currency currency) {
    public Money {
        if (amount.compareTo(BigDecimal.ZERO) < 0) {
            throw new DomainException("Amount cannot be negative");
        }
    }

    public static Money zero() {
        return new Money(BigDecimal.ZERO, Currency.getInstance("EUR"));
    }

    public Money add(Money other) {
        if (!this.currency.equals(other.currency)) {
            throw new DomainException("Currency mismatch");
        }
        return new Money(this.amount.add(other.amount), this.currency);
    }
}
```

### 示例3：领域层 - 仓库端口

```java
// domain/repository/OrderRepository.java (端口)
public interface OrderRepository {
    Order save(Order order);
    Optional<Order> findById(OrderId id);
}
```

### 示例4：应用层 - 用例和服务

```java
// application/port/in/CreateOrderUseCase.java
public interface CreateOrderUseCase {
    OrderResponse createOrder(CreateOrderRequest request);
}

// application/dto/CreateOrderRequest.java
public record CreateOrderRequest(
    @NotNull UUID customerId,
    @NotEmpty List<OrderItemRequest> items
) {}

// application/service/OrderService.java
@Service
@RequiredArgsConstructor
@Transactional
public class OrderService implements CreateOrderUseCase {
    private final OrderRepository orderRepository;
    private final PaymentGateway paymentGateway;
    private final DomainEventPublisher eventPublisher;

    @Override
    public OrderResponse createOrder(CreateOrderRequest request) {
        List<OrderItem> items = mapItems(request.items());
        Order order = Order.create(items);

        PaymentResult payment = paymentGateway.charge(order.getTotal());
        if (!payment.successful()) {
            throw new PaymentFailedException("Payment failed");
        }

        order.confirm();
        Order saved = orderRepository.save(order);
        publishEvents(order);

        return OrderMapper.toResponse(saved);
    }

    private void publishEvents(Order order) {
        order.getDomainEvents().forEach(eventPublisher::publish);
        order.clearDomainEvents();
    }
}
```

### 示例5：基础设施层 - JPA实体和适配器

```java
// infrastructure/persistence/OrderJpaEntity.java
@Entity
@Table(name = "orders")
public class OrderJpaEntity {
    @Id
    private UUID id;
    @Enumerated(EnumType.STRING)
    private OrderStatus status;
    private BigDecimal totalAmount;
    @OneToMany(cascade = CascadeType.ALL, orphanRemoval = true)
    private List<OrderItemJpaEntity> items;
}

// infrastructure/persistence/OrderRepositoryAdapter.java
@Component
@RequiredArgsConstructor
public class OrderRepositoryAdapter implements OrderRepository {
    private final OrderJpaRepository jpaRepository;
    private final OrderJpaMapper mapper;

    @Override
    public Order save(Order order) {
        OrderJpaEntity entity = mapper.toEntity(order);
        return mapper.toDomain(jpaRepository.save(entity));
    }

    @Override
    public Optional<Order> findById(OrderId id) {
        return jpaRepository.findById(id.value()).map(mapper::toDomain);
    }
}
```

### 示例6：适配器层 - REST控制器

```java
// adapter/rest/OrderController.java
@RestController
@RequestMapping("/api/orders")
@RequiredArgsConstructor
public class OrderController {
    private final CreateOrderUseCase createOrderUseCase;

    @PostMapping
    public ResponseEntity<OrderResponse> createOrder(
            @Valid @RequestBody CreateOrderRequest request) {
        OrderResponse response = createOrderUseCase.createOrder(request);
        URI location = ServletUriComponentsBuilder
            .fromCurrentRequest()
            .path("/{id}")
            .buildAndExpand(response.id())
            .toUri();
        return ResponseEntity.created(location).body(response);
    }
}
```

### 示例7：领域测试（无Spring上下文）

```java
class OrderTest {
    @Test
    void shouldCreateOrderWithValidItems() {
        List<OrderItem> items = List.of(
            new OrderItem(new ProductId(UUID.randomUUID()), 2, new Money("10.00", EUR))
        );

        Order order = Order.create(items);

        assertThat(order.getStatus()).isEqualTo(OrderStatus.PENDING);
        assertThat(order.getDomainEvents()).hasSize(1);
    }
}
```

### 示例8：应用测试（带Mock的单元测试）

```java
@ExtendWith(MockitoExtension.class)
class OrderServiceTest {
    @Mock OrderRepository orderRepository;
    @Mock PaymentGateway paymentGateway;
    @Mock DomainEventPublisher eventPublisher;

    @InjectMocks OrderService orderService;

    @Test
    void shouldCreateAndConfirmOrder() {
        when(paymentGateway.charge(any())).thenReturn(new PaymentResult(true, "tx-123"));
        when(orderRepository.save(any())).thenAnswer(i -> i.getArgument(0));

        OrderResponse response = orderService.createOrder(createRequest());

        assertThat(response.status()).isEqualTo(OrderStatus.CONFIRMED);
        verify(eventPublisher).publish(any(OrderCreatedEvent.class));
    }
}
```

## 最佳实践

- **领域纯净性**：保持领域层无Spring注解和框架导入 — 对外部层无依赖
- **基于功能的包**：按业务能力（`order/`, `customer/`）而非技术角色组织，每个功能包含所有四层
- **不可变值对象**：使用Java记录实现具有内置验证的值对象 — 设计上不可变
- **富领域模型**：将业务逻辑放在实体和聚合中，而不是应用服务中 — 服务编排，实体封装
- **始终映射**：使用MapStruct或手动映射器分离JPA实体与领域模型；永不暴露JPA实体到基础设施外
- **领域事件用于解耦**：使用`DomainEventPublisher`解耦跨聚合副作用，而非直接服务调用
- **应用层事务边界**：仅在应用服务中放置`@Transactional`，永不应用于领域类
- **构造器方法用于不变性**：使用`Entity.create(...)`静态方法在构造时强制不变性
- **使用ArchUnit强制执行**：在测试套件中添加ArchUnit测试以验证无Spring或基础设施导入到达领域层
- **强类型ID**：使用`record OrderId(UUID value)`而非原始`UUID`以防止聚合间ID混淆

## 限制和警告

### 关键限制

- **领域层纯净性**：永不向领域类添加Spring注解（`@Entity`, `@Autowired`, `@Component`）
- **依赖方向**：依赖项必须仅指向内部（领域 <- 应用 <- 基础设施/适配器）
- **框架隔离**：所有特定于框架的代码必须保留在基础设施和适配器层

### 避免常见陷阱

- **贫血领域模型**：仅含getter/setter的实体，逻辑在服务中 — 将业务逻辑放在实体中
- **框架泄漏**：领域层中的`@Entity`, `@Autowired` — 保持领域无框架
- **懒加载问题**：通过领域模型暴露JPA实体 — 使用映射器转换
- **循环依赖**：聚合间直接引用 — 使用ID而非直接引用
- **缺少领域事件**：直接服务调用而非事件用于跨聚合通信
- **仓库误置**：在基础设施中定义仓库接口 — 它们属于领域
- **DTO绕过**：直接在API中暴露领域实体 — 始终使用DTO作为外部契约

### 性能考虑

- 分离JPA实体与领域模型以避免懒加载问题
- 使用只读事务进行查询操作
- 考虑CQRS用于复杂读写场景

## 参考文献

- `references/java-clean-architecture.md` - Java特定模式（记录、密封类、强类型ID）
- `references/spring-boot-implementation.md` - Spring Boot集成（DI模式、JPA映射、事务管理）
