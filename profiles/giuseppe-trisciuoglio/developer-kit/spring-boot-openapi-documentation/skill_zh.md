# 使用 SpringDoc 构建 Spring Boot OpenAPI 文档

## 概述

SpringDoc OpenAPI 可自动为 Spring Boot 项目生成 OpenAPI 3.0 文档，并提供 Swagger UI 网页界面用于 API 探索和测试。

## 使用场景

- 在 Spring Boot 3.x 项目中设置 SpringDoc OpenAPI
- 为 REST API 生成 OpenAPI 3.0 规范
- 配置和自定义 Swagger UI
- 使用注解添加详细的 API 文档
- 使用注解记录请求/响应模型并实现验证
- 实现 API 安全性文档（JWT、OAuth2、基本认证）
- 记录可分页和可排序的端点
- 为 API 端点添加示例和模式
- 通过代码自定义 OpenAPI 定义
- 支持多个 API 组和版本
- 记录错误响应和异常处理器
- 为 API 文档添加 JSR-303 Bean 验证
- 支持基于 Kotlin 的 Spring Boot API

## 快速参考

| 概念 | 描述 |
|------|------|
| **依赖项** | `springdoc-openapi-starter-webmvc-ui` 用于 WebMvc，`springdoc-openapi-starter-webflux-ui` 用于 WebFlux |
| **配置** | `application.yml` 中使用 `springdoc.api-docs.*` 和 `springdoc.swagger-ui.*` 属性 |
| **访问点** | OpenAPI JSON: `/v3/api-docs`，Swagger UI: `/swagger-ui/index.html` |
| **核心注解** | `@Tag`、`@Operation`、`@ApiResponse`、`@Parameter`、`@Schema`、`@SecurityRequirement` |
| **安全性** | 在 OpenAPI bean 中配置安全方案，使用 `@SecurityRequirement` 应用 |
| **分页** | 使用 `@ParameterObject` 与 Spring Data `Pageable` 结合 |

## 使用说明

### 1. 添加依赖项

为您的应用程序类型（WebMvc 或 WebFlux）添加 SpringDoc 启动器。有关 Maven/Gradle 配置，请参阅 [dependency-setup.md](references/dependency-setup.md)。

### 2. 配置 SpringDoc

在 `application.yml` 中设置基本配置：

```yaml
springdoc:
  api-docs:
    path: /api-docs
  swagger-ui:
    path: /swagger-ui.html
    operationsSorter: method
```

有关高级选项，请参阅 [configuration.md](references/configuration.md)。

### 3. 文档化控制器

使用 OpenAPI 注解添加描述性信息：

```java
@RestController
@Tag(name = "Book", description = "图书管理 API")
public class BookController {

    @Operation(summary = "根据 ID 获取图书")
    @ApiResponse(responseCode = "200", description = "找到图书")
    @GetMapping("/{id}")
    public Book findById(@PathVariable Long id) { }
}
```

有关模式，请参阅 [controller-documentation.md](references/controller-documentation.md)。

### 4. 文档化模型

将 `@Schema` 注解应用于 DTO：

```java
@Schema(description = "图书实体")
public class Book {
    @Schema(example = "1", accessMode = Schema.AccessMode.READ_ONLY)
    private Long id;

    @Schema(example = "Clean Code", required = true)
    private String title;
}
```

有关验证模式，请参阅 [model-documentation.md](references/model-documentation.md)。

### 5. 配置安全性

在 OpenAPI bean 中设置安全方案：

```java
@Bean
public OpenAPI customOpenAPI() {
    return new OpenAPI()
        .components(new Components()
            .addSecuritySchemes("bearer-jwt", new SecurityScheme()
                .type(SecurityScheme.Type.HTTP)
                .scheme("bearer")
                .bearerFormat("JWT")
            )
        );
}
```

在控制器上使用 `@SecurityRequirement(name = "bearer-jwt")` 应用。有关详细信息，请参阅 [security-configuration.md](references/security-configuration.md)。

### 6. 文档化分页

使用 `@ParameterObject` 与 Spring Data `Pageable` 结合：

```java
@GetMapping("/paginated")
public Page<Book> findAll(@ParameterObject Pageable pageable) {
    return repository.findAll(pageable);
}
```

有关详细信息，请参阅 [pagination-support.md](references/pagination-support.md)。

### 7. 测试文档

访问 Swagger UI 在 `/swagger-ui/index.html` 以验证文档完整性。

### 8. 生产环境定制

配置 API 分组、版本和构建插件。有关详细信息，请参阅 [advanced-configuration.md](references/advanced-configuration.md) 和 [build-integration.md](references/build-integration.md)。

## 最佳实践

- **使用描述性操作摘要**：简短（< 120 字符），清晰的陈述
- **记录所有响应代码**：包括成功（2xx）、客户端错误（4xx）、服务器错误（5xx）
- **为请求/响应正文添加示例**：使用 `@ExampleObject` 添加真实示例
- **利用 JSR-303 验证注解**：SpringDoc 自动从验证注解生成约束
- **使用 `@ParameterObject` 处理复杂参数**：特别是用于 Pageable、自定义过滤器对象
- **使用 `@Tag` 分组相关端点**：按领域实体或功能组织 API
- **记录安全性要求**：在需要认证的地方应用 `@SecurityRequirement`
- **适当隐藏内部端点**：使用 `@Hidden` 或创建单独的 API 组
- **自定义 Swagger UI 以提升用户体验**：启用过滤、排序、尝试功能
- **版本化 API 文档**：在 OpenAPI Info 中包含版本信息

## 参考

- **[dependency-setup.md](references/dependency-setup.md)** — Maven/Gradle 依赖项和版本选择
- **[configuration.md](references/configuration.md)** — 基本和高级配置选项
- **[controller-documentation.md](references/controller-documentation.md)** — 控制器和端点文档模式
- **[model-documentation.md](references/model-documentation.md)** — 实体、DTO 和验证文档
- **[security-configuration.md](references/security-configuration.md)** — JWT、OAuth2、基本认证、API 密钥配置
- **[pagination-support.md](references/pagination-support.md)** — Pageable、Slice 和自定义分页模式
- **[advanced-configuration.md](references/advanced-configuration.md)** — API 分组、自定义器、OpenAPI bean 配置
- **[exception-handling.md](references/exception-handling.md)** — 异常文档和错误响应模式
- **[build-integration.md](references/build-integration.md)** — Maven/Gradle 插件和 CI/CD 集成
- **[complete-examples.md](references/complete-examples.md)** — 完整的控制器、实体和配置示例
- **[annotations-reference.md](references/annotations-reference.md)** — 完整注解参考，包含属性
- **[springdoc-official.md](references/springdoc-official.md)** — SpringDoc 官方文档
- **[troubleshooting.md](references/troubleshooting.md)** — 常见问题和解决方案

## 限制和警告

- 不要在 API 示例或模式描述中暴露敏感数据
- 尽量使用全局配置，避免在控制器代码中堆砌 OpenAPI 注解
- 大型 API 定义可能会影响 Swagger UI 性能；考虑按领域分组 API
- 模式生成可能无法正确处理复杂的泛型类型；使用显式的 `@Schema` 注解
- 避免在 DTO 中创建循环引用，这会导致模式生成无限递归
- 在使用 `@SecurityRequirement` 注解之前，必须正确配置安全方案
- 被隐藏的端点（`@Operation(hidden = true)`）仍然在代码中可见，可能会通过其他文档工具泄露

## 示例

### 基本控制器文档

```java
@RestController
@Tag(name = "Books", description = "图书管理 API")
@RequestMapping("/api/books")
public class BookController {

    @Operation(
        summary = "根据 ID 获取图书",
        description = "检索特定图书的详细信息"
    )
    @ApiResponse(responseCode = "200", description = "找到图书")
    @ApiResponse(responseCode = "404", description = "图书未找到")
    @GetMapping("/{id}")
    public Book getBook(@PathVariable Long id) {
        return bookService.findById(id);
    }

    @Operation(summary = "创建新图书")
    @SecurityRequirement(name = "bearer-jwt")
    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public Book createBook(@Valid @RequestBody CreateBookRequest request) {
        return bookService.create(request);
    }
}
```

### 带验证的文档化模型

```java
@Schema(description = "图书实体")
public class Book {
    @Schema(description = "唯一标识符", example = "1", accessMode = Schema.AccessMode.READ_ONLY)
    private Long id;

    @Schema(description = "图书标题", example = "Clean Code", required = true)
    @NotBlank
    @Size(min = 1, max = 200)
    private String title;

    @Schema(description = "作者姓名", example = "Robert C. Martin")
    @NotBlank
    private String author;

    @Schema(description = "美元价格", example = "29.99", minimum = "0")
    @NotNull
    @DecimalMin("0.0")
    private BigDecimal price;
}
```

### 安全性配置

```java
@Bean
public OpenAPI customOpenAPI() {
    return new OpenAPI()
        .info(new Info()
            .title("图书 API")
            .version("1.0.0")
            .description("图书管理 REST API"))
        .components(new Components()
            .addSecuritySchemes("bearer-jwt", new SecurityScheme()
                .type(SecurityScheme.Type.HTTP)
                .scheme("bearer")
                .bearerFormat("JWT"))
            .addSecuritySchemes("api-key", new SecurityScheme()
                .type(SecurityScheme.Type.APIKEY)
                .in(SecurityScheme.In.HEADER)
                .name("X-API-Key")));
}
```

## 相关技能

- `spring-boot-rest-api-standards` — REST API 设计标准
- `spring-boot-dependency-injection` — 依赖注入模式
- `unit-test-controller-layer` — 测试 REST 控制器
- `spring-boot-actuator` — 生产监控和管理

## 外部资源

- [SpringDoc 官方文档](https://springdoc.org/)
- [OpenAPI 3.0 规范](https://swagger.io/specification/)
- [Swagger UI 配置](https://swagger.io/docs/open-source-tools/swagger-ui/usage/configuration/)
