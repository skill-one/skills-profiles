# 使用 Kotlin 的 Spring Boot 最佳实践

你的目标是帮助我使用 Kotlin 编写高质量、符合规范的 Spring Boot 应用程序。

## 项目设置与结构

- **构建工具**：使用 Maven (`pom.xml`) 或 Gradle (`build.gradle`) 并配合 Kotlin 插件 (`kotlin-maven-plugin` 或 `org.jetbrains.kotlin.jvm`)。
- **Kotlin 插件**：对于 JPA，启用 `kotlin-jpa` 插件以自动将实体类声明为 `open` 而无需样板代码。
- **启动器**：像往常一样使用 Spring Boot 启动器（例如 `spring-boot-starter-web`、`spring-boot-starter-data-jpa`）。
- **包结构**：按功能/领域组织代码（例如 `com.example.app.order`、`com.example.app.user`），而不是按层级组织。

## 依赖注入与组件

- **主构造函数**：始终使用主构造函数进行必要的依赖注入。这是 Kotlin 中最符合规范且简洁的方法。
- **不可变性**：在主构造函数中将依赖项声明为 `private val`。在所有地方优先使用 `val` 而不是 `var` 以促进不可变性。
- **组件注解**：像在 Java 中一样使用 `@Service`、`@Repository` 和 `@RestController` 注解。

## 配置

- **外部化配置**：使用 `application.yml` 以其可读性和层次结构优势。
- **类型安全的属性**：使用 `@ConfigurationProperties` 与 `data class` 创建不可变、类型安全的配置对象。
- **配置文件**：使用 Spring 配置文件 (`application-dev.yml`、`application-prod.yml`) 管理特定于环境的配置。
- **密钥管理**：不要硬编码密钥。使用环境变量或专门的密钥管理工具（如 HashiCorp Vault 或 AWS Secrets Manager）。

## Web 层（控制器）

- **RESTful API**：设计清晰且一致的 RESTful 端点。
- **数据类用于 DTO**：使用 Kotlin `data class` 作为所有 DTO。这会免费提供 `equals()`、`hashCode()`、`toString()` 和 `copy()`，并促进不可变性。
- **验证**：使用 Java Bean 验证（JSR 380）并在 DTO 数据类上使用注解（`@Valid`、`@NotNull`、`@Size`）。
- **错误处理**：使用 `@ControllerAdvice` 和 `@ExceptionHandler` 实现全局异常处理程序，以获得一致的错误响应。

## 服务层

- **业务逻辑**：在 `@Service` 类中封装业务逻辑。
- **无状态**：服务应该是无状态的。
- **事务管理**：在服务方法上使用 `@Transactional`。在 Kotlin 中，这可以应用于类或函数级别。

## 数据层（仓库）

- **JPA 实体**：将实体定义为类。记住它们必须是 `open`。强烈建议使用 `kotlin-jpa` 编译器插件自动处理此问题。
- **空安全**：利用 Kotlin 的空安全（`?`）在类型级别清晰定义哪些实体字段是可选的或必需的。
- **Spring Data JPA**：通过扩展 `JpaRepository` 或 `CrudRepository` 使用 Spring Data JPA 仓库。
- **协程**：对于响应式应用程序，利用 Spring Boot 在数据层对 Kotlin 协程的支持。

## 日志记录

- **伴生对象日志记录器**：声明日志记录器的规范方式是在伴生对象中。
  ```kotlin
  companion object {
      private val logger = LoggerFactory.getLogger(MyClass::class.java)
  }
  ```
- **参数化日志记录**：使用参数化消息（`logger.info("处理用户 {}...", userId)`) 以提高性能和清晰度。

## 测试

- **JUnit 5**：JUnit 5 是默认选项，与 Kotlin 无缝协作。
- **符合规范的测试库**：为了更流畅和符合规范的测试，可以考虑使用 **Kotest** 进行断言和使用 **MockK** 进行模拟。它们是为 Kotlin 设计的，并提供了更表达式的语法。
- **测试切片**：使用测试切片注解（如 `@WebMvcTest` 或 `@DataJpaTest`）测试应用程序的特定部分。
- **Testcontainers**：使用 Testcontainers 进行可靠的集成测试，使用真实的数据库、消息代理等。

## 协程与异步编程

- **`suspend` 函数**：对于非阻塞的异步代码，在控制器和服务中使用 `suspend` 函数。Spring Boot 对协程有出色的支持。
- **结构化并发**：使用 `coroutineScope` 或 `supervisorScope` 管理协程的生命周期。
