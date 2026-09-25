# Spring Boot 依赖注入

## 概述

为 Spring Boot 提供构造器优先的依赖注入模式：
- 通过构造器注入必需的协作对象
- 通过 `ObjectProvider` 或无操作回退注入可选的协作对象
- 通过 `@Primary` 和 `@Qualifier` 选择 Bean
- 在完整集成前通过最小化上下文测试进行验证

## 何时使用

在以下情况下使用此技巧：
- 创建新的 `@Service`、`@Component`、`@Repository` 或 `@Configuration` 类
- 替换传统 Spring 代码中的字段注入
- 使用限定符或主 Bean 解析相同类型的多个 Bean
- 处理可选功能、适配器或集成，无需空值驱动连接
- 审查循环依赖或脆弱的上下文启动失败
- 准备代码以进行直接基于构造器的单元测试

## 指令

### 1. 分离必需和可选的协作对象

对于每个类，识别：
- 正确行为所需的必需协作对象
- 启用集成、缓存、通知或特性标记行为的可选协作对象

必需的协作对象应放在构造器中。可选的协作对象需要显式策略，如 `ObjectProvider`、条件 Bean 或无操作实现。

### 2. 默认使用构造器注入

对于应用服务和适配器：
- 通过构造器注入必需的依赖
- 将注入的字段保持为 `final`
- 在单元测试中直接实例化类，无需启动 Spring

通常一个构造器就足够了；在这种情况下，`@Autowired` 是不必要的。

### 3. 有意地解析可选行为

好的选项包括：
- 使用 `ObjectProvider<T>` 当懒加载有用时
- 使用 `@ConditionalOnProperty` 或 `@ConditionalOnMissingBean` 当连接应根据配置变化时
- 使用无操作实现当调用者不应关心功能是否启用时

避免使用可空的协作对象，这会使运行时行为模糊不清。

### 4. 仅在需要时使用 Bean 选择注解

当多个 Bean 共享相同类型时：
- 使用 `@Primary` 为默认实现
- 使用 `@Qualifier` 为命名变体
- 保持限定符名称稳定且易于通过 grep 查找

如果选择规则变得复杂，应将它们移到专门的配置类中，而不是分散在服务中。

### 5. 将连接逻辑放在配置中，而不是业务代码中

在以下情况下使用 `@Configuration` 和 `@Bean` 方法：
- 对象来自第三方库
- 需要条件创建逻辑
- 需要环境特定的连接或显式组合

业务服务不应知道基础设施协作对象是如何实例化的。

### 6. 显式验证连接

编写新服务或配置后：

1. **使用最小化上下文测试验证 Bean 加载**：
   ```java
   @SpringBootTest
   @ContextConfiguration(classes = UserService.class)
   class UserServiceWiringTest {
       @Autowired UserService userService;
       @Test void serviceIsInstantiated() { assertNotNull(userService); }
   }
   ```
2. **运行基于构造器的单元测试以验证服务行为（无需 Spring）**。
3. **仅在必须验证 MVC、JPA 或消息集成时才添加切片测试**。
4. **保留 `@SpringBootTest` 用于容器级连接验证**。

步骤 1 失败表示在添加业务逻辑之前存在连接问题。

## 示例

### 示例 1：构造器优先的应用服务

```java
@Service
public class UserService {

    private final UserRepository userRepository;
    private final EmailSender emailSender;

    public UserService(UserRepository userRepository, EmailSender emailSender) {
        this.userRepository = userRepository;
        this.emailSender = emailSender;
    }

    public User register(UserRegistrationRequest request) {
        User user = userRepository.save(User.from(request));
        emailSender.sendWelcome(user);
        return user;
    }
}
```

此类易于在单元测试中直接使用 Mock 实例化。

### 示例 2：带有无操作回退的可选依赖

```java
@Service
public class ReportService {

    private final ReportRepository reportRepository;
    private final NotificationGateway notificationGateway;

    public ReportService(
        ReportRepository reportRepository,
        ObjectProvider<NotificationGateway> notificationGatewayProvider
    ) {
        this.reportRepository = reportRepository;
        this.notificationGateway = notificationGatewayProvider.getIfAvailable(NotificationGateway::noOp);
    }
}
```

这使可选行为保持显式，而不会将 `null` 处理泄漏到类的其他部分。

### 示例 3：具有清晰选择的多个 Bean

```java
@Configuration
public class PaymentConfiguration {

    @Bean
    @Primary
    PaymentGateway stripeGateway() {
        return new StripePaymentGateway();
    }

    @Bean
    @Qualifier("fallbackGateway")
    PaymentGateway mockGateway() {
        return new MockPaymentGateway();
    }
}
```

使用 `@Primary` 为默认路径，仅在需要特定变体时使用 `@Qualifier`。

## 最佳实践

- 优先为必需依赖使用构造器注入。
- 保持服务构造器简短；如果类需要太多协作对象，设计可能需要另一种抽象。
- 使用无操作或条件 Bean 而不是可空的可选依赖。
- 将框架特定的创建逻辑放在配置类中。
- 首先不使用 Spring 测试服务，仅在容器测试能增加价值时添加。
- 在重构期间移除字段注入，而不是扩展它。

## 限制和警告

- 字段注入隐藏依赖关系，使测试更难编写。
- 循环依赖通常是设计问题，而不是使用 `@Lazy` 解决的连接技巧。
- 过度使用限定符会使代码库难以理解；优先使用更好的抽象或更清晰的配置。
- 可选协作对象在缺失时仍需要确定性行为。
- 如果使用过早，完整上下文测试可能会隐藏连接失败的真正原因。

## 参考

- `references/reference.md`
- `references/examples.md`
- `references/spring-official-dependency-injection.md`

## 相关技巧

- `spring-boot-crud-patterns`
- `spring-boot-rest-api-standards`
- `unit-test-service-layer`
