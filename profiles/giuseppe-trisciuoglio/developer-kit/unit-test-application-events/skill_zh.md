# 单元测试应用事件

## 概述

提供可操作的测试模式，用于使用JUnit 5和Mockito测试Spring `ApplicationEvent`发布者和`@EventListener`消费者——而无需启动完整的Spring上下文。

## 何时使用

- 为事件发布者或监听器编写单元测试
- 验证是否已使用正确的有效负载发布事件
- 测试`@EventListener`方法的调用和副作用
- 测试通过多个监听器的事件传播
- 验证异步事件处理（`@Async` + `@EventListener`）
- 在服务测试中模拟`ApplicationEventPublisher`

## 说明

1. **添加测试依赖项**：`spring-boot-starter`、JUnit 5、Mockito、AssertJ
2. **模拟ApplicationEventPublisher**：在测试的服务中的发布者字段上使用`@Mock`
3. **使用ArgumentCaptor捕获事件**：`ArgumentCaptor.forClass(EventType.class)`以检查发布的有效负载
4. **验证监听器副作用**：直接对模拟的依赖项调用监听器
5. **测试异步处理程序**：使用`Thread.sleep()`或Awaitility——然后断言异步操作被调用
6. **添加验证检查点**：
   - 捕获事件后，在断言字段之前确认`eventCaptor.getValue()`不为null
   - 如果监听器未被调用，请验证`publishEvent()`是否使用正确的事件类型被调用
   - 如果异步断言失败，请增加等待时间并检查执行器池是否饱和
7. **覆盖错误场景**：断言监听器优雅地处理异常

## 示例

### Maven

```xml
<dependency>
  <groupId>org.springframework.boot</groupId>
  <artifactId>spring-boot-starter</artifactId>
</dependency>
<dependency>
  <groupId>org.junit.jupiter</groupId>
  <artifactId>junit-jupiter</artifactId>
  <scope>test</scope>
</dependency>
<dependency>
  <groupId>org.mockito</groupId>
  <artifactId>mockito-core</artifactId>
  <scope>test</scope>
</dependency>
<dependency>
  <groupId>org.assertj</groupId>
  <artifactId>assertj-core</artifactId>
  <scope>test</scope>
</dependency>
```

### Gradle

```kotlin
dependencies {
  implementation("org.springframework.boot:spring-boot-starter")
  testImplementation("org.junit.jupiter:junit-jupiter")
  testImplementation("org.mockito:mockito-core")
  testImplementation("org.assertj:assertj-core")
}
```

### 自定义事件和发布者测试

```java
public class UserCreatedEvent extends ApplicationEvent {
  private final User user;

  public UserCreatedEvent(Object source, User user) {
    super(source);
    this.user = user;
  }

  public User getUser() { return user; }
}

@Service
public class UserService {
  private final ApplicationEventPublisher eventPublisher;
  private final UserRepository userRepository;

  public UserService(ApplicationEventPublisher eventPublisher, UserRepository userRepository) {
    this.eventPublisher = eventPublisher;
    this.userRepository = userRepository;
  }

  public User createUser(String name, String email) {
    User savedUser = userRepository.save(new User(name, email));
    eventPublisher.publishEvent(new UserCreatedEvent(this, savedUser));
    return savedUser;
  }
}
```

### 事件发布单元测试

```java
@ExtendWith(MockitoExtension.class)
class UserServiceEventTest {

  @Mock
  private ApplicationEventPublisher eventPublisher;

  @Mock
  private UserRepository userRepository;

  @InjectMocks
  private UserService userService;

  @Test
  void shouldPublishUserCreatedEvent() {
    User newUser = new User(1L, "Alice", "alice@example.com");
    when(userRepository.save(any(User.class))).thenReturn(newUser);

    ArgumentCaptor<UserCreatedEvent> eventCaptor = ArgumentCaptor.forClass(UserCreatedEvent.class);

    userService.createUser("Alice", "alice@example.com");

    verify(eventPublisher).publishEvent(eventCaptor.capture());
    assertThat(eventCaptor.getValue().getUser()).isEqualTo(newUser);
  }
}
```

### 直接测试监听器

```java
@Component
public class UserEventListener {
  private final EmailService emailService;

  public UserEventListener(EmailService emailService) { this.emailService = emailService; }

  @EventListener
  public void onUserCreated(UserCreatedEvent event) {
    emailService.sendWelcomeEmail(event.getUser().getEmail());
  }
}

class UserEventListenerTest {

  @Test
  void shouldSendWelcomeEmailOnUserCreated() {
    EmailService emailService = mock(EmailService.class);
    UserEventListener listener = new UserEventListener(emailService);

    User user = new User(1L, "Alice", "alice@example.com");
    listener.onUserCreated(new UserCreatedEvent(this, user));

    verify(emailService).sendWelcomeEmail("alice@example.com");
  }

  @Test
  void shouldNotThrowWhenEmailServiceFails() {
    EmailService emailService = mock(EmailService.class);
    doThrow(new RuntimeException("down")).when(emailService).sendWelcomeEmail(any());

    UserEventListener listener = new UserEventListener(emailService);
    User user = new User(1L, "Alice", "alice@example.com");

    assertThatCode(() -> listener.onUserCreated(new UserCreatedEvent(this, user)))
      .doesNotThrowAnyException();
  }
}
```

### 异步监听器测试

```java
@Component
public class AsyncEventListener {
  private final SlowService slowService;

  @EventListener
  @Async
  public void onUserCreatedAsync(UserCreatedEvent event) {
    slowService.processUser(event.getUser());
  }
}

class AsyncEventListenerTest {

  @Test
  void shouldProcessEventAsynchronously() throws Exception {
    SlowService slowService = mock(SlowService.class);
    AsyncEventListener listener = new AsyncEventListener(slowService);

    User user = new User(1L, "Alice", "alice@example.com");
    listener.onUserCreatedAsync(new UserCreatedEvent(this, user));

    Thread.sleep(200); // 检查点：允许异步执行器运行
    verify(slowService).processUser(user);
  }
}
```

## 最佳实践

- 模拟`ApplicationEventPublisher`——在单元测试中永不让它发布到真实上下文
- 使用`ArgumentCaptor`捕获事件，并断言字段级相等性，而不仅仅是类型
- 独立测试监听器：使用模拟的依赖项构建它们，并直接调用处理程序方法
- 覆盖错误路径：监听器必须不会将异常传播到发布者
- 异步监听器：优先使用Awaitility而不是`Thread.sleep()`进行确定性等待
- 保持事件不可变和可序列化——如果事件跨JVM边界，请测试两者

## 限制和警告

- **不要测试Spring自己的事件基础设施**——专注于您的业务逻辑和事件有效负载
- **`@Async`需要`@EnableAsync`**——使用`Thread.sleep()`的测试可能仍然通过，即使异步代理未在测试中连接；使用模拟验证代替
- **Spring不保证监听器顺序**——除非您添加`@Order`，否则不要编写依赖于执行顺序的测试
- **在CI环境中避免使用`Thread.sleep()`**——在负载下它会使测试不稳定；使用Awaitility `.atMost()`块替换
- **跨JVM边界的事件需要序列化测试**——远程监听器中的空字段通常意味着缺少`Serializable`

## 参考

- [Spring ApplicationEvent Javadoc](https://docs.spring.io/spring-framework/docs/current/javadoc-api/org/springframework/context/ApplicationEvent.html)
- [ApplicationEventPublisher Javadoc](https://docs.spring.io/spring-framework/docs/current/javadoc-api/org/springframework/context/ApplicationEventPublisher.html)
- [`@EventListener` Javadoc](https://docs.spring.io/spring-framework/docs/current/javadoc-api/org/springframework/context/event/EventListener.html)
