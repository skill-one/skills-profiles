# Spring Boot 最佳实践

你的目标是遵循既定的最佳实践，帮助你编写高质量的 Spring Boot 应用程序。

## 项目设置与结构

- **构建工具：** 使用 Maven (`pom.xml`) 或 Gradle (`build.gradle`) 进行依赖管理。
- **启动器：** 使用 Spring Boot 启动器（例如 `spring-boot-starter-web`、`spring-boot-starter-data-jpa`）简化依赖管理。
- **包结构：** 按功能/领域组织代码（例如 `com.example.app.order`、`com.example.app.user`），而不是按层级（例如 `com.example.app.controller`、`com.example.app.service`）。

## 依赖注入与组件

- **构造器注入：** 始终使用构造器注入来注入必需的依赖项。这使得组件更易于测试，并且依赖项更加明确。
- **不可变性：** 将依赖字段声明为 `private final`。
- **组件注解：** 适当地使用 `@Component`、`@Service`、`@Repository` 和 `@Controller`/`@RestController` 注解来定义 Bean。

## 配置

- **外部化配置：** 使用 `application.yml`（或 `application.properties`）进行配置。通常推荐使用 YAML，因为它具有可读性和层次结构。
- **类型安全的属性：** 使用 `@ConfigurationProperties` 将配置绑定到强类型的 Java 对象。
- **配置文件：** 使用 Spring 配置文件 (`application-dev.yml`、`application-prod.yml`) 管理特定于环境的配置。
- **密钥管理：** 不要硬编码密钥。使用环境变量，或使用 HashiCorp Vault 或 AWS Secrets Manager 等专门的密钥管理工具。

## Web 层（控制器）

- **RESTful API：** 设计清晰且一致的 RESTful 端点。
- **DTO（数据传输对象）：** 使用 DTO 在 API 层暴露和消费数据。不要直接向客户端暴露 JPA 实体。
- **验证：** 使用 Java Bean 验证（JSR 380）并在 DTO 上使用注解（`@Valid`、`@NotNull`、`@Size`）来验证请求有效负载。
- **错误处理：** 使用 `@ControllerAdvice` 和 `@ExceptionHandler` 实现全局异常处理程序，以提供一致的错误响应。

## 服务层

- **业务逻辑：** 将所有业务逻辑封装在 `@Service` 类中。
- **无状态：** 服务应该是无状态的。
- **事务管理：** 在服务方法上使用 `@Transactional` 以声明式方式管理数据库事务。在必要时应用它。

## 数据层（仓库）

- **Spring Data JPA：** 使用 Spring Data JPA 仓库，通过扩展 `JpaRepository` 或 `CrudRepository` 进行标准数据库操作。
- **自定义查询：** 对于复杂查询，使用 `@Query` 或 JPA 标准 API。
- **投影：** 使用 DTO 投影从数据库中获取必要的数据。

## 日志记录

- **SLF4J：** 使用 SLF4J API 进行日志记录。
- **日志声明：** `private static final Logger logger = LoggerFactory.getLogger(MyClass.class);`
- **参数化日志：** 使用参数化消息（`logger.info("Processing user {}...", userId);`）而不是字符串连接来提高性能。

## 测试

- **单元测试：** 使用 JUnit 5 和 Mockito 等模拟框架为服务和组件编写单元测试。
- **集成测试：** 使用 `@SpringBootTest` 进行加载 Spring 应用程序上下文的集成测试。
- **测试切片：** 使用 `@WebMvcTest`（用于控制器）或 `@DataJpaTest`（用于仓库）等测试切片注解来隔离测试应用程序的特定部分。
- **Testcontainers：** 考虑使用 Testcontainers 进行可靠的集成测试，使用真实数据库、消息代理等。

## 安全

- **Spring Security：** 使用 Spring Security 进行身份验证和授权。
- **密码编码：** 始终使用 BCrypt 等强哈希算法对密码进行编码。
- **输入清理：** 通过使用 Spring Data JPA 或参数化查询防止 SQL 注入。通过正确编码输出防止跨站脚本 (XSS)。
