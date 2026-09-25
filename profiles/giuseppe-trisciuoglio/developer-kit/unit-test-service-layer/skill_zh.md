# 使用 Mockito 单元测试服务层

## 概述

提供使用 Mockito 单元测试 `@Service` 类的模式。模拟仓库调用、验证方法调用、测试异常场景以及模拟外部 API 响应。支持无需 Spring 容器或数据库即可进行快速、隔离的测试。

## 何时使用

- 测试 `@Service` 类中的业务逻辑
- 模拟仓库和外部客户端依赖项
- 验证服务与模拟协作对象之间的交互
- 测试服务中的错误处理和边界情况
- 编写快速、隔离的单元测试（无需数据库，无需 API 调用）

## 使用说明

遵循以下工作流程使用 Mockito 测试服务层，包括验证检查点：

### 1. 设置测试类

使用 `@ExtendWith(MockitoExtension.class)` 启用 Mockito 注解。

### 2. 使用 `@Mock` 和 `@InjectMocks` 声明模拟对象

使用 `@Mock` 模拟依赖项（仓库、客户端），使用 `@InjectMocks` 模拟待测试的服务。

### 3. 使用验证的 Arrange-Act-Assert

**Arrange**：创建测试数据并使用 `when().thenReturn()` 配置模拟返回值。

**Act**：执行待测试的服务方法。

**Assert**：
- 使用 AssertJ 断言验证返回值
- 使用 `verify()` 验证模拟交互
- **验证检查点**：运行测试并确认绿色条

### 4. 测试异常场景

使用 `when().thenThrow()` 配置模拟对象抛出异常。

**验证检查点**：验证异常类型和消息

### 5. 验证完整覆盖率

- 运行完整测试套件：`mvn test` 或 `gradle test`
- 检查覆盖率报告：`mvn test jacoco:report`
- **验证检查点**：确认所有服务方法都有对应的测试

## 示例

### 基本服务测试模式

```java
@ExtendWith(MockitoExtension.class)
class UserServiceTest {

  @Mock
  private UserRepository userRepository;

  @InjectMocks
  private UserService userService;

  @Test
  void shouldReturnUserWhenFound() {
    // Arrange
    User expected = new User(1L, "Alice");
    when(userRepository.findById(1L)).thenReturn(Optional.of(expected));

    // Act
    User result = userService.getUser(1L);

    // Assert
    assertThat(result.getName()).isEqualTo("Alice");
    verify(userRepository).findById(1L);
  }

  @Test
  void shouldThrowWhenUserNotFound() {
    // Arrange
    when(userRepository.findById(999L)).thenReturn(Optional.empty());

    // Act & Assert
    assertThatThrownBy(() -> userService.getUser(999L))
      .isInstanceOf(UserNotFoundException.class);
  }
}
```

### 验证方法调用

```java
@Test
void shouldSendEmailOnUserCreation() {
  User newUser = new User(1L, "Alice", "alice@example.com");
  when(userRepository.save(any(User.class))).thenReturn(newUser);

  enrichmentService.registerNewUser("Alice", "alice@example.com");

  verify(userRepository).save(any(User.class));
  verify(emailService).sendWelcomeEmail("alice@example.com");
}
```

有关更多模式（多个依赖项、参数捕获器、异步服务、InOrder 验证），请参阅 `references/examples.md`。

## 最佳实践

- **使用 `@ExtendWith(MockitoExtension.class)`** 进行 JUnit 5 集成
- **仅模拟服务直接依赖项**
- **验证交互**以确保正确协作
- **每个测试方法测试一种行为** - 保持测试聚焦
- **使用描述性变量名**：`expectedUser`、`actualUser`、`captor`
- **为值对象和 DTO 创建真实实例**（不要模拟它们）

## 限制和警告

- 不要模拟值对象或 DTO；使用测试数据创建真实实例。
- 避免模拟过多依赖项；如果服务协作对象过多，请考虑重构。
- 测试必须是独立的；不要依赖执行顺序。
- 对 `@Spy` 要谨慎；部分模拟更难理解和维护。
- 不要直接测试私有方法；通过公共方法行为测试它们。
- 参数匹配器（`any()`、`eq()`）不能与同一存根中的实际值混合。
- 避免过度验证；仅验证对测试场景重要的交互。

## 参考

- [Mockito 文档](https://javadoc.io/doc/org.mockito/mockito-core/latest/org/mockito/Mockito.html)
- [JUnit 5 用户指南](https://junit.org/junit5/docs/current/user-guide/)
- [AssertJ 断言](https://assertj.github.io/assertj-core-features-highlight.html)
