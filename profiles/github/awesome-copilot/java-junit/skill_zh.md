# JUnit 5+ 最佳实践

你的目标是帮助我使用 JUnit 5 编写有效的单元测试，涵盖标准测试和数据驱动测试方法。

## 项目设置

- 使用标准的 Maven 或 Gradle 项目结构。
- 将测试源代码放置在 `src/test/java`。
- 添加 `junit-jupiter-api`、`junit-jupiter-engine` 和 `junit-jupiter-params` 的依赖项以进行参数化测试。
- 使用构建工具命令运行测试：`mvn test` 或 `gradle test`。

## 测试结构

- 测试类应具有 `Test` 后缀，例如 `CalculatorTest` 用于 `Calculator` 类。
- 使用 `@Test` 标注测试方法。
- 遵循 Arrange-Act-Assert (AAA) 模式。
- 使用描述性约定命名测试，例如 `methodName_should_expectedBehavior_when_scenario`。
- 使用 `@BeforeEach` 和 `@AfterEach` 进行每个测试的设置和清理。
- 使用 `@BeforeAll` 和 `@AfterAll` 进行类的设置和清理（必须是静态方法）。
- 使用 `@DisplayName` 为测试类和方法提供人类可读的名称。

## 标准测试

- 保持测试专注于单一行为。
- 避免在一个测试方法中测试多个条件。
- 使测试独立且幂等（可以按任何顺序运行）。
- 避免测试之间的相互依赖。

## 数据驱动（参数化）测试

- 使用 `@ParameterizedTest` 标注方法为参数化测试。
- 使用 `@ValueSource` 用于简单的字面量值（字符串、整数等）。
- 使用 `@MethodSource` 引用提供测试参数的工厂方法，如 `Stream`、`Collection` 等。
- 使用 `@CsvSource` 用于内联逗号分隔值。
- 使用 `@CsvFileSource` 使用类路径上的 CSV 文件。
- 使用 `@EnumSource` 使用枚举常量。

## 断言

- 使用 `org.junit.jupiter.api.Assertions` 的静态方法（例如 `assertEquals`、`assertTrue`、`assertNotNull`）。
- 考虑使用 AssertJ 库（`assertThat(...).is...`）以获得更流畅和可读的断言。
- 使用 `assertThrows` 或 `assertDoesNotThrow` 测试异常。
- 使用 `assertAll` 将相关的断言分组，以确保在测试失败前检查所有断言。
- 在断言中使用描述性消息以提供失败时的清晰度。

## 模拟和隔离

- 使用 Mockito 等模拟框架创建依赖项的模拟对象。
- 使用 Mockito 的 `@Mock` 和 `@InjectMocks` 注解简化模拟创建和注入。
- 使用接口来简化模拟。

## 测试组织

- 使用包按功能或组件分组测试。
- 使用 `@Tag` 对测试进行分类（例如，`@Tag("fast")`、`@Tag("integration")`）。
- 在必要时使用 `@TestMethodOrder(MethodOrderer.OrderAnnotation.class)` 和 `@Order` 控制测试执行顺序。
- 使用 `@Disabled` 暂时跳过测试方法或类，并提供原因。
- 使用 `@Nested` 将测试分组到嵌套内部类中，以更好地组织和结构化。
