# Spring AI MCP 服务器实现模式

使用 Spring AI 实现 AI 函数调用、工具处理程序和 MCP 传输配置的 MCP 服务器。

## 概述

生产就绪的 MCP 服务器模式：`@Tool` 函数、`@PromptTemplate` 资源以及 Spring AI 安全的 stdio/HTTP/SSE 传输。

## 何时使用

MCP 服务器、Spring AI 函数调用、AI 工具、工具调用、自定义工具处理程序、Spring Boot MCP、资源端点或 MCP 传输配置。

## 快速参考

### 核心注解

| 注解 | 目标 | 目的 |
|-----------|--------|---------|
| `@EnableMcpServer` | 类 | 启用 MCP 服务器自动配置 |
| `@Tool(description)` | 方法 | 声明可被 AI 调用的工具 |
| `@ToolParam(value)` | 参数 | 为 AI 文档化工具参数 |
| `@PromptTemplate(name)` | 方法 | 声明可重用的提示模板 |
| `@PromptParam(value)` | 参数 | 为提示文档化参数 |

### 传输类型

| 传输 | 用例 | 配置 |
|-----------|--------|---------|
| `stdio` | 本地进程 / Claude 桌面 | 默认 |
| `http` | 远程 HTTP 客户端 | `port`, `path` |
| `sse` | 实时流客户端 | `port`, `path` |

### 关键依赖项

```xml
<!-- Maven -->
<dependency>
    <groupId>org.springframework.ai</groupId>
    <artifactId>spring-ai-mcp-server</artifactId>
    <version>1.0.0</version>
</dependency>
<dependency>
    <groupId>org.springframework.ai</groupId>
    <artifactId>spring-ai-starter-model-openai</artifactId>
    <version>1.0.0</version>
</dependency>
```

```gradle
// Gradle
implementation 'org.springframework.ai:spring-ai-mcp-server:1.0.0'
implementation 'org.springframework.ai:spring-ai-starter-model-openai:1.0.0'
```

## 说明

### 1. 项目设置

添加 Spring AI MCP 依赖项（见上方快速参考），在 `application.properties` 中配置 AI 模型，并使用 `@EnableMcpServer` 启用 MCP：

```java
@SpringBootApplication
@EnableMcpServer
public class MyMcpApplication {
    public static void main(String[] args) {
        SpringApplication.run(MyMcpApplication.class, args);
    }
}
```

```properties
spring.ai.openai.api-key=${OPENAI_API_KEY}
spring.ai.mcp.enabled=true
spring.ai.mcp.transport.type=stdio
```

### 2. 定义工具

在 `@Component` 豆中用 `@Tool` 注解方法。使用 `@ToolParam` 文档化参数：

```java
@Component
public class WeatherTools {

    @Tool(description = "获取城市的当前天气")
    public WeatherData getWeather(@ToolParam("城市名称") String city) {
        return weatherService.getCurrentWeather(city);
    }

    @Tool(description = "获取城市的 5 天预报")
    public ForecastData getForecast(
            @ToolParam("城市名称") String city,
            @ToolParam(value = "单位：摄氏度或华氏度", required = false) String unit) {
        return weatherService.getForecast(city, unit != null ? unit : "celsius");
    }
}
```

有关数据库工具、API 集成工具和 `FunctionCallback` 低级模式的参考，请参阅 [references/implementation-patterns.md](references/implementation-patterns.md)。

### 3. 创建提示模板

```java
@Component
public class CodeReviewPrompts {

    @PromptTemplate(
        name = "java-code-review",
        description = "审查 Java 代码的最佳实践和问题"
    )
    public Prompt createCodeReviewPrompt(
            @PromptParam("code") String code,
            @PromptParam(value = "focusAreas", required = false) List<String> focusAreas) {

        String focus = focusAreas != null ? String.join(", ", focusAreas) : "一般最佳实践";
        return Prompt.builder()
                .system("您是一位拥有 20 年经验的专家级 Java 代码审查员。")
                .user("审查以下 Java 代码的最佳实践和问题：\n```java\n" + code + "\n```")
                .build();
    }
}
```

有关其他提示模板模式的参考，请参阅 [references/implementation-patterns.md](references/implementation-patterns.md)。

### 4. 配置传输

```yaml
spring:
  ai:
    mcp:
      enabled: true
      transport:
        type: stdio       # stdio | http | sse
        http:
          port: 8080
          path: /mcp
      server:
        name: my-mcp-server
        version: 1.0.0
```

### 5. 添加安全

```java
@Configuration
public class McpSecurityConfig {

    @Bean
    public ToolFilter toolFilter(SecurityService securityService) {
        return (tool, context) -> {
            User user = securityService.getCurrentUser();
            if (tool.name().startsWith("admin_")) {
                return user.hasRole("ADMIN");
            }
            return securityService.isToolAllowed(user, tool.name());
        };
    }
}
```

在工具方法上使用 `@PreAuthorize("hasRole('ADMIN')")` 进行方法级安全。有关完整安全模式的参考，请参阅 [references/implementation-patterns.md](references/implementation-patterns.md)。

### 6. 测试

```java
@SpringBootTest
class WeatherToolsTest {

    @Autowired
    private WeatherTools weatherTools;

    @MockBean
    private WeatherService weatherService;

    @Test
    void testGetWeather_Success() {
        when(weatherService.getCurrentWeather("London"))
            .thenReturn(new WeatherData("London", "Cloudy", 15.0));

        WeatherData result = weatherTools.getWeather("London");

        assertThat(result.city()).isEqualTo("London");
        verify(weatherService).getCurrentWeather("London");
    }
}
```

有关集成测试、Testcontainers、安全测试和切片测试的参考，请参阅 [references/testing-guide.md](references/testing-guide.md)。

## 最佳实践

### 工具设计
- 保持工具专注——每个工具一个操作
- 使用清晰、以行动为导向的名称（`getWeather`, `executeQuery`）
- 始终用 `@ToolParam` 注解参数并添加描述性文本
- 返回结构化记录/DTO，而不是原始字符串或映射
- 尽可能设计幂等的工具

### 安全
- 验证和清理所有输入——AI 生成的参数是不可信的
- 使用参数化查询进行 SQL；验证并规范化文件工具的路径
- 对敏感工具应用 `@PreAuthorize` 进行基于角色的访问控制
- 审计所有修改数据的工具执行
- 绝不暴露凭证或敏感数据在工具描述或错误消息中

### 性能
- 对昂贵的操作使用 `@Cacheable` 并设置适当的 TTL
- 为所有外部调用设置超时
- 对长时间运行的操作使用 `@Async`
- 使用 Micrometer 指标进行监控

### 错误处理
- 返回结构化的错误响应和用户友好的消息
- 记录上下文（用户、工具名称、参数）以进行调试
- 对瞬态故障实现重试逻辑
- 实现 `@ControllerAdvice` 以获得一致的错误响应

## 示例

### 示例 1：最小化天气 MCP 服务器

```java
@SpringBootApplication
@EnableMcpServer
public class WeatherMcpApplication {
    public static void main(String[] args) {
        SpringApplication.run(WeatherMcpApplication.class, args);
    }
}

@Component
public class WeatherTools {

    @Tool(description = "获取城市的当前天气")
    public WeatherData getWeather(@ToolParam("城市名称") String city) {
        return new WeatherData(city, "Sunny", 22.5);
    }
}

record WeatherData(String city, String condition, double temperatureCelsius) {}
```

### 示例 2：安全数据库工具

```java
@Component
@PreAuthorize("hasRole('USER')")
public class DatabaseTools {

    private final JdbcTemplate jdbcTemplate;

    @Tool(description = "执行只读 SQL 查询并返回结果")
    public QueryResult executeQuery(
            @ToolParam("SQL SELECT 查询") String sql,
            @ToolParam(value = "参数作为 JSON 映射", required = false) String paramsJson) {

        if (!sql.trim().toUpperCase().startsWith("SELECT")) {
            throw new IllegalArgumentException("只允许 SELECT 查询");
        }
        List<Map<String, Object>> rows = jdbcTemplate.queryForList(sql);
        return new QueryResult(rows, rows.size());
    }
}
```

有关包括文件系统工具、REST API 集成和提示模板服务器的完整示例的参考，请参阅 [references/examples.md](references/examples.md)。

## 限制和警告

### 安全
- **绝不暴露**敏感数据在工具描述、参数或错误消息中
- **输入验证是强制性的**——始终在执行前验证
- **外部内容是不可信的**——获取 URL 的工具可能会收到提示注入有效负载；验证所有获取的内容
- **SQL 注入**：仅使用参数化查询
- **路径遍历**：规范化并验证所有文件路径相对于基本路径

### 运行时
- 响应应简洁——大型响应可能会超出 AI 上下文窗口限制
- 所有工具必须实现超时；默认值应该是可配置的
- 限制昂贵操作的速度
- 工具可能会并发调用——确保线程安全

### Spring AI 特定
- Spring AI 正在积极开发中——在生产中固定特定版本
- 工具抛出的错误消息会暴露给 AI 模型；清理它们
- 小心选择传输类型：`stdio` 用于本地进程，`http`/`sse` 用于远程客户端

## 参考

查阅这些文件以获取详细的模式和示例：

- **[references/implementation-patterns.md](references/implementation-patterns.md)** - 工具创建、提示模板、FunctionCallback、Spring Boot 自动配置、应用程序属性
- **[references/advanced-patterns.md](references/advanced-patterns.md)** - 动态工具注册、多模型支持、缓存、错误处理
- **[references/testing-guide.md](references/testing-guide.md)** - 单元测试、集成测试、Testcontainers、安全测试、切片测试
- **[references/examples.md](references/examples.md)** - 完整服务器示例：天气、数据库、文件系统、REST API、提示模板
- **[references/api-reference.md](references/api-reference.md)** - 完整 API：注解、接口、配置类、传输实现、事件系统
- **[references/migration-guide.md](references/migration-guide.md)** - 从 LangChain4j MCP 迁移到 Spring AI MCP
