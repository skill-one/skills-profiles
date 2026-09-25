# Spring Boot 测试模式

## 概述

使用 JUnit 5、Mockito、Testcontainers 和性能优化的切片测试模式编写 Spring Boot 应用程序健壮测试套件的全面指导。

## 何时使用

- 为具有模拟依赖项的服务或存储库编写单元测试
- 通过 Testcontainers 实现使用真实数据库的集成测试
- 使用 `@WebMvcTest` 或 MockMvc 测试 REST API
- 在 Spring Boot 3.5+ 中配置 `@ServiceConnection` 以进行容器管理

## 快速参考

| 测试类型 | 注解 | 目标时间 | 用例 |
|-----------|------------|-------------|----------|
| **单元测试** | `@ExtendWith(MockitoExtension.class)` | < 50ms | 无 Spring 上下文的业务逻辑 |
| **存储库测试** | `@DataJpaTest` | < 100ms | 具有最小上下文的数据库操作 |
| **控制器测试** | `@WebMvcTest` / `@WebFluxTest` | < 100ms | REST API 层测试 |
| **集成测试** | `@SpringBootTest` | < 500ms | 使用容器的完整应用程序上下文 |
| **Testcontainers** | `@ServiceConnection` / `@Testcontainers` | 变化 | 真实数据库/消息代理容器 |

## 核心概念

### 测试架构理念

1. **单元测试** — 快速、隔离的测试，无 Spring 上下文 (< 50ms)
2. **切片测试** — 最小化 Spring 上下文以针对特定层 (< 100ms)
3. **集成测试** — 使用真实依赖项的完整 Spring 上下文 (< 500ms)

### 关键注解

**Spring Boot 测试:**
- `@SpringBootTest` — 完整应用程序上下文（谨慎使用）
- `@DataJpaTest` — 仅 JPA 组件（存储库、实体）
- `@WebMvcTest` — 仅 MVC 层（控制器、`@ControllerAdvice`）
- `@WebFluxTest` — 仅 WebFlux 层（响应式控制器）
- `@JsonTest` — 仅 JSON 序列化组件

**Testcontainers:**
- `@ServiceConnection` — 将 Testcontainer 连接到 Spring Boot (3.5+)
- `@DynamicPropertySource` — 在运行时注册动态属性
- `@Testcontainers` — 启用 Testcontainers 生命周期管理

## 说明

### 1. 单元测试模式

使用模拟依赖项测试业务逻辑：

```java
@ExtendWith(MockitoExtension.class)
class UserServiceTest {
    @Mock
    private UserRepository userRepository;

    @InjectMocks
    private UserService userService;

    @Test
    void shouldFindUserByIdWhenExists() {
        when(userRepository.findById(1L)).thenReturn(Optional.of(user));
        Optional<User> result = userService.findById(1L);
        assertThat(result).isPresent();
        verify(userRepository).findById(1L);
    }
}
```

有关高级模式的更多信息，请参阅 [unit-testing.md](references/unit-testing.md)。

### 2. 切片测试模式

使用针对特定层的聚焦测试切片：

```java
@DataJpaTest
@AutoConfigureTestDatabase(replace = AutoConfigureTestDatabase.Replace.NONE)
@TestContainerConfig
class UserRepositoryIntegrationTest {
    @Autowired
    private UserRepository userRepository;

    @Test
    void shouldSaveAndRetrieveUser() {
        User saved = userRepository.save(user);
        assertThat(userRepository.findByEmail("test@example.com")).isPresent();
    }
}
```

有关所有切片模式的更多信息，请参阅 [slice-testing.md](references/slice-testing.md)。

### 3. REST API 测试模式

使用 MockMvc 测试控制器：

```java
@WebMvcTest(UserController.class)
class UserControllerTest {
    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private UserService userService;

    @Test
    void shouldGetUserById() throws Exception {
        mockMvc.perform(get("/api/users/1"))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.email").value("test@example.com"));
    }
}
```

### 4. 使用 `@ServiceConnection` 的 Testcontainers

在 Spring Boot 3.5+ 中配置容器：

```java
@TestConfiguration
public class TestContainerConfig {
    @Bean
    @ServiceConnection
    public PostgreSQLContainer<?> postgresContainer() {
        return new PostgreSQLContainer<>("postgres:16-alpine");
    }
}
```

在测试类上使用 `@Import(TestContainerConfig.class)` 应用。

有关详细配置的更多信息，请参阅 [testcontainers-setup.md](references/testcontainers-setup.md)。

### 5. 添加依赖项

包含所需的测试依赖项：

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-test</artifactId>
    <scope>test</scope>
</dependency>
<dependency>
    <groupId>org.testcontainers</groupId>
    <artifactId>junit-jupiter</artifactId>
    <version>1.19.0</version>
    <scope>test</scope>
</dependency>
```

有关完整依赖项列表的更多信息，请参阅 [test-dependencies.md](references/test-dependencies.md)。

### 6. 配置 CI/CD

设置 GitHub Actions 以进行自动化测试：

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    services:
      docker:
        image: docker:20-dind
    steps:
    - uses: actions/checkout@v4
    - name: Set up JDK 17
      uses: actions/setup-java@v4
      with:
        distribution: 'temurin'
    - name: Run tests
      run: ./mvnw test
```

有关完整 CI/CD 模式的更多信息，请参阅 [ci-cd-configuration.md](references/ci-cd-configuration.md)。

### 验证检查点

实施测试后，请验证：
- 容器正在运行：`docker ps`（查找 testcontainer 镜像）
- 上下文已加载：检查启动日志以查找“Started Application in X.XX seconds”
- 测试隔离：单独运行测试并确认没有交叉污染

## 示例

### 使用 `@ServiceConnection` 的完整集成测试

```java
@SpringBootTest
@Import(TestContainerConfig.class)
class OrderServiceIntegrationTest {

    @Autowired
    private OrderService orderService;

    @Autowired
    private UserRepository userRepository;

    @Test
    void shouldCreateOrderForExistingUser() {
        User user = userRepository.save(User.builder()
            .email("order-test@example.com")
            .build());

        Order order = orderService.createOrder(user.getId(), List.of(
            new OrderItem("SKU-001", 2)
        ));

        assertThat(order.getId()).isNotNull();
        assertThat(order.getStatus()).isEqualTo(OrderStatus.PENDING);
    }
}
```

### 使用 `@DataJpaTest` 和真实数据库

```java
@DataJpaTest
@AutoConfigureTestDatabase(replace = AutoConfigureTestDatabase.Replace.NONE)
@TestContainerConfig
class UserRepositoryTest {

    @Autowired
    private UserRepository userRepository;

    @Test
    void shouldFindByEmail() {
        userRepository.save(User.builder()
            .email("jpa-test@example.com")
            .build());
        assertThat(userRepository.findByEmail("jpa-test@example.com"))
            .isPresent();
    }
}
```

有关完整端到端示例的更多信息，请参阅 [workflow-patterns.md](references/workflow-patterns.md)。

## 最佳实践

- **使用正确的测试类型**：`@DataJpaTest` 用于存储库，`@WebMvcTest` 用于控制器，`@SpringBootTest` 仅用于完整集成
- **优先使用 `@ServiceConnection**` 在 Spring Boot 3.5+ 上进行更干净的容器管理，而不是 `@DynamicPropertySource`
- **保持测试确定性**：在 `@BeforeEach` 中显式初始化所有测试数据
- **按层组织**：按层分组测试以最大化上下文缓存
- **在 JVM 级别重用 Testcontainers** (`withReuse(true)` + `TESTCONTAINERS_REUSE_ENABLE=true`)
- **避免使用 `@DirtiesContext**`：强制上下文重建，显著影响性能
- **模拟外部服务**，仅在必要时使用真实数据库
- **性能目标**：单元 < 50ms，切片 < 100ms，集成 < 500ms

## 限制和警告

- 除非绝对必要，否则**不要使用 `@DirtiesContext**`（强制上下文重建）
- 避免混合 `@MockBean` 与不同配置（创建单独的上下文）
- Testcontainers 需要 Docker；确保 CI/CD 管道具有 Docker 支持
- 不要依赖测试执行顺序；每个测试必须独立
- 对 `@TestPropertySource` 要小心（创建单独的上下文）
- 不要使用 `@SpringBootTest` 进行单元测试；使用普通的 Mockito 代替
- 上下文缓存可能因不同的 `@MockBean` 配置而被使无效
- 避免在测试中使用静态可变状态（导致不可靠的测试）

## 参考

- **[test-dependencies.md](references/test-dependencies.md)** — Maven/Gradle 测试依赖项
- **[unit-testing.md](references/unit-testing.md)** — 使用 Mockito 模式的单元测试
- **[slice-testing.md](references/slice-testing.md)** — 存储库、控制器和 JSON 切片测试
- **[testcontainers-setup.md](references/testcontainers-setup.md)** — Testcontainers 配置模式
- **[ci-cd-configuration.md](references/ci-cd-configuration.md)** — GitHub Actions、GitLab CI、Docker Compose
- **[api-reference.md](references/api-reference.md)** — 完整的测试注解和实用工具
- **[best-practices.md](references/best-practices.md)** — 测试模式和优化
- **[workflow-patterns.md](references/workflow-patterns.md)** — 完整的集成测试示例
