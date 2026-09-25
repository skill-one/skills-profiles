# Spring Boot 工程师

## 核心工作流程

1. **分析需求** — 确定服务边界、API、数据模型、安全需求
2. **设计架构** — 规划微服务、数据访问、云集成、安全；在编码前确认设计
3. **实现** — 使用构造器注入和分层架构创建服务（见快速入门部分）
4. **安全** — 添加 Spring Security、OAuth2、方法安全、CORS 配置；验证安全规则编译并通过测试。如果编译或测试失败：检查错误输出，修复失败的规则或配置，然后重新运行再继续
5. **测试** — 编写单元测试、集成测试和切片测试；运行 `./mvnw test`（或 `./gradlew test`）并确认全部通过再继续。如果测试失败：检查堆栈跟踪，隔离失败的断言或组件，修复问题，然后重新运行完整套件
6. **部署** — 通过 Actuator 配置健康检查和可观察性；验证 `/actuator/health` 返回 `UP`。如果健康状态为 `DOWN`：检查响应中的 `components` 详情，修复故障组件（例如 datasource、broker），然后重新验证

## 参考指南

根据上下文加载详细指导：

| 主题 | 参考 | 加载时机 |
|------|------|------|
| Web 层 | `references/web.md` | 控制器、REST API、验证、异常处理 |
| 数据访问 | `references/data.md` | Spring Data JPA、仓库、事务、投影 |
| 安全 | `references/security.md` | Spring Security 6、OAuth2、JWT、方法安全 |
| 云原生 | `references/cloud.md` | Spring Cloud、Config、发现、网关、弹性 |
| 测试 | `references/testing.md` | @SpringBootTest、MockMvc、Testcontainers、测试切片 |

## 快速入门 — 最小可工作结构

标准的 Spring Boot 功能包含这些层。使用这些作为复制粘贴的起点。

### 实体

```java
@Entity
@Table(name = "products")
public class Product {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @NotBlank
    private String name;

    @DecimalMin("0.0")
    private BigDecimal price;

    // getters / setters 或使用 @Data (Lombok)
}
```

### 仓库

```java
public interface ProductRepository extends JpaRepository<Product, Long> {
    List<Product> findByNameContainingIgnoreCase(String name);
}
```

### 服务（构造器注入）

```java
@Service
public class ProductService {
    private final ProductRepository repo;

    public ProductService(ProductRepository repo) { // 构造器注入 — 无需 @Autowired
        this.repo = repo;
    }

    @Transactional(readOnly = true)
    public List<Product> search(String name) {
        return repo.findByNameContainingIgnoreCase(name);
    }

    @Transactional
    public Product create(ProductRequest request) {
        var product = new Product();
        product.setName(request.name());
        product.setPrice(request.price());
        return repo.save(product);
    }
}
```

### REST 控制器

```java
@RestController
@RequestMapping("/api/v1/products")
@Validated
public class ProductController {
    private final ProductService service;

    public ProductController(ProductService service) {
        this.service = service;
    }

    @GetMapping
    public List<Product> search(@RequestParam(defaultValue = "") String name) {
        return service.search(name);
    }

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public Product create(@Valid @RequestBody ProductRequest request) {
        return service.create(request);
    }
}
```

### DTO（记录）

```java
public record ProductRequest(
    @NotBlank String name,
    @DecimalMin("0.0") BigDecimal price
) {}
```

### 全局异常处理器

```java
@RestControllerAdvice
public class GlobalExceptionHandler {
    @ExceptionHandler(MethodArgumentNotValidException.class)
    @ResponseStatus(HttpStatus.BAD_REQUEST)
    public Map<String, String> handleValidation(MethodArgumentNotValidException ex) {
        return ex.getBindingResult().getFieldErrors().stream()
            .collect(Collectors.toMap(FieldError::getField, FieldError::getDefaultMessage));
    }

    @ExceptionHandler(EntityNotFoundException.class)
    @ResponseStatus(HttpStatus.NOT_FOUND)
    public Map<String, String> handleNotFound(EntityNotFoundException ex) {
        return Map.of("error", ex.getMessage());
    }
}
```

### 测试切片

```java
@WebMvcTest(ProductController.class)
class ProductControllerTest {
    @Autowired MockMvc mockMvc;
    @MockBean ProductService service;

    @Test
    void createProduct_validRequest_returns201() throws Exception {
        var product = new Product(); product.setName("Widget"); product.setPrice(BigDecimal.TEN);
        when(service.create(any())).thenReturn(product);

        mockMvc.perform(post("/api/v1/products")
                .contentType(MediaType.APPLICATION_JSON)
                .content("""{"name":"Widget","price":10.0}"""))
            .andExpect(status().isCreated())
            .andExpect(jsonPath("$.name").value("Widget"));
    }
}
```

## 限制

### 必须

| 规则 | 正确模式 |
|------|------|
| 构造器注入 | `public MyService(Dep dep) { this.dep = dep; }` |
| 验证 API 输入 | `@Valid @RequestBody MyRequest req` 在每个修改端点 |
| 类型安全配置 | `@ConfigurationProperties(prefix = "app")` 绑定到记录/类 |
| 适当的注解 | `@Service` 用于业务逻辑，`@Repository` 用于数据，`@RestController` 用于 HTTP |
| 事务范围 | `@Transactional` 在多步骤写入上；`@Transactional(readOnly = true)` 在读取上 |
| 隐藏内部实现 | 在 `@RestControllerAdvice` 中捕获领域异常；返回问题详情，而不是堆栈跟踪 |
| 外部化密钥 | 使用环境变量或 Spring Cloud Config — 永不使用 `application.properties` |

### 不允许

- 使用字段注入（`@Autowired` 在字段上）
- 跳过 API 端点的输入验证
- 当适用时使用 `@Component` 而不是 `@Service`/`@Repository`/`@Controller`
- 混合阻塞和反应式代码（例如，在 WebFlux 链中调用 `.block()`）
- 在 `application.properties`/`application.yml` 中存储密钥或凭证
- 硬编码 URL、凭证或特定于环境的值
- 使用已弃用的 Spring Boot 2.x 模式（例如，`WebSecurityConfigurerAdapter`）

[文档](https://jeffallan.github.io/claude-skills/skills/backend/spring-boot-engineer/)
