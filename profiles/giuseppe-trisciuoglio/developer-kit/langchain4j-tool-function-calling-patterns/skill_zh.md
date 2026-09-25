# LangChain4j 工具与函数调用模式

提供标注方法为工具、配置工具执行器、向 AI 服务注册工具、验证参数以及处理工具执行错误在 LangChain4j 应用中的模式。

## 概述

LangChain4j 使用 `@Tool` 注解将 Java 方法暴露为 AI 代理可调用的函数。`AiServices` 构建器将工具注册到聊天模型，使 LLM 能够执行文本生成之外的操作：数据库查询、API 调用、计算和业务系统集成。参数使用 `@P` 进行描述，以指导 LLM。

## 使用场景

- 构建 AI 代理调用外部工具（天气、股票、数据库查询）
- 定义 LLM 工具使用的函数规范（`@Tool`、`@P` 注解）
- 使用 `AiServices.builder().tools()` 注册和管理工具集
- 处理工具执行错误、超时和幻觉工具名称
- 实现上下文感知工具，通过 `@ToolMemoryId` 注入用户状态
- 配置动态工具提供程序用于大型或条件性工具集

## 指南

### 1. 使用 `@Tool` 标注方法

定义一个工具类，其中方法使用 `@Tool` 标注。将描述作为第一个参数提供。使用 `@P` 对每个参数进行描述。

```java
public class WeatherTools {
    private final WeatherService weatherService;

    public WeatherTools(WeatherService weatherService) {
        this.weatherService = weatherService;
    }

    @Tool("获取城市的当前天气")
    public String getWeather(
            @P("城市名称") String city,
            @P("温度单位：摄氏度或华氏度") String unit) {
        return weatherService.getWeather(city, unit);
    }
}
```

**验证**：创建一个实例并确认类加载没有错误。

### 2. 使用 AiServices 注册工具

使用 `AiServices.builder()` 将工具实例注册到聊天模型。

```java
MathAssistant assistant = AiServices.builder(MathAssistant.class)
    .chatModel(chatModel)
    .tools(new Calculator(), new WeatherTools(weatherService))
    .build();
```

**验证**：调用 `assistant.chat("2 + 2 是什么？")` 并确认 LLM 没有抛出异常地响应。

### 3. 端到端测试工具调用

发送一个触发工具使用的提示，并验证工具执行及其结果被整合。

```java
String response = assistant.chat("罗马的天气如何？");
System.out.println(response);
```

**验证**：检查日志以确认工具调用，并确认响应使用了工具的输出。

### 4. 处理工具执行错误

添加错误处理程序以优雅地管理失败，而不会暴露堆栈跟踪。

```java
AiServices.builder(Assistant.class)
    .chatModel(chatModel)
    .tools(new ExternalServiceTools())
    .toolExecutionErrorHandler((request, exception) -> {
        logger.error("工具 '{}' 失败：{}", request.name(), exception.getMessage());
        return "处理您的请求时发生错误";
    })
    .hallucinatedToolNameStrategy(request ->
        ToolExecutionResultMessage.from(request,
            "错误：工具 '" + request.name() + "' 不存在"))
    .toolArgumentsErrorHandler((error, context) ->
        ToolErrorHandlerResult.text("无效的参数： " + error.getMessage()))
    .build();
```

**验证**：触发一个错误条件，并确认 LLM 接收到一个安全的错误消息。

### 5. 优化性能和扩展性

启用并发工具执行，并为长时间运行的工具设置超时。

```java
AiServices.builder(Assistant.class)
    .chatModel(chatModel)
    .tools(new DbTools(), new HttpTools())
    .executeToolsConcurrently(Executors.newFixedThreadPool(5))
    .toolExecutionTimeout(Duration.ofSeconds(30))
    .build();
```

**验证**：运行并发请求，并确认没有线程争用或死锁。

## 示例

### 带完整类的计算器工具

```java
public class Calculator {
    @Tool("执行基本算术")
    public double calculate(
            @P("表达式如 2+2 或 10*5") String expression) {
        // 解析并计算表达式
        return eval(expression);
    }
}

Assistant assistant = AiServices.builder(Assistant.class)
    .chatModel(ChatModel.builder()
        .apiKey(System.getenv("API_KEY"))
        .model("gpt-4o")
        .build())
    .tools(new Calculator())
    .build();
```

### 立即返回工具（无需 LLM 响应）

```java
@Tool(value = "发送电子邮件通知", returnBehavior = ReturnBehavior.IMMEDIATELY)
public void sendEmail(@P("收件人电子邮件地址") String to,
                     @P("电子邮件主题") String subject,
                     @P("电子邮件正文") String body) {
    emailService.send(to, subject, body);
}
```

### 动态工具提供程序

```java
ToolProvider provider = request -> {
    if (request.userContext().contains("admin")) {
        return List.of(new AdminTools());
    }
    return List.of(new UserTools());
};

AiServices.builder(Assistant.class)
    .chatModel(chatModel)
    .toolProvider(provider)
    .build();
```

## 最佳实践

- **描述性的 `@Tool` 名称**：使用祈使动词（"获取"、"发送"、"计算"）并具有清晰的范围
- **精确的 `@P` 描述**：包括格式、约束和有效值——模糊的描述会导致 LLM 调用错误
- **安全的错误处理**：不要暴露堆栈跟踪；返回用户友好的错误字符串
- **超时配置**：始终设置 `.toolExecutionTimeout()` 用于外部服务调用
- **并发执行**：当工具独立时启用 `.executeToolsConcurrently()` 
- **输入验证**：在工具方法内部验证参数；返回描述性错误
- **权限检查**：在工具内部执行授权，而不是在 AI 服务级别
- **审计日志**：记录工具名称、参数和执行结果以用于调试和合规

## 常见问题和解决方案

| 问题 | 解决方案 |
|-------|----------|
| LLM 调用不存在的工具 | 添加 `.hallucinatedToolNameStrategy()` 返回一个安全的错误消息 |
| 工具接收错误的参数 | 完善 `@P` 描述；添加 `.toolArgumentsErrorHandler()` |
| 工具执行挂起 | 设置 `.toolExecutionTimeout(Duration.ofSeconds(N))` |
| 外部 API 的速率限制错误 | 在工具方法内部添加重试逻辑或速率限制器 |
| LLM 忽略工具输出 | 确保工具返回 LLM 可以解释的字符串 |

有关弹性模式的更多信息，请参阅 [references/error-handling.md](references/error-handling.md)，有关参数和返回类型详情，请参阅 [references/core-patterns.md](references/core-patterns.md)。

## 快速参考

| 注解 / API | 目的 |
|-----------------|---------|
| `@Tool` | 将方法标记为可调用的工具 |
| `@P` | 描述工具参数以供 LLM 使用 |
| `@ToolMemoryId` | 将对话/用户 ID 注入工具 |
| `AiServices.builder()` | 创建带有注册工具的 AI 服务 |
| `ReturnBehavior.IMMEDIATELY` | 执行工具而无需等待 LLM 响应 |
| `ToolProvider` | 基于上下文动态提供工具 |
| `executeToolsConcurrently()` | 并行运行独立的工具调用 |
| `toolExecutionTimeout()` | 单个工具调用的超时 |

## 限制和警告

- **敏感数据**：不要在 `@Tool` 或 `@P` 描述中传递 API 密钥、密码或凭证
- **副作用**：修改数据的工具应在描述中警告；AI 模型可能会多次调用它们
- **大型工具集**：过多的工具会使 LLM 模型感到困惑——使用 `ToolProvider` 进行条件性注册
- **阻塞操作**：工具不应执行长时间同步 I/O 而不进行超时配置
- **堆栈跟踪暴露**：始终通过返回安全字符串的错误处理程序路由异常
- **参数精确性**：模糊的 `@P` 描述直接导致错误的工具调用——具体说明格式和约束
- **并发安全性**：在使用 `executeToolsConcurrently()` 时，确保工具类是无状态的或线程安全的

## 相关技能

- `langchain4j-ai-services-patterns` — 高级 AI 服务配置
- `langchain4j-rag-implementation-patterns` — 带工具集成的 RAG 检索
- `langchain4j-spring-boot-integration` — 在 Spring Boot 应用中注册工具

## 参考文献

- **[references/setup-configuration.md](references/setup-configuration.md)** — Maven 设置、聊天模型配置、第一个工具注册
- **[references/core-patterns.md](references/core-patterns.md)** — 基本工具定义、复杂参数、返回类型
- **[references/advanced-features.md](references/advanced-features.md)** — 内存上下文、动态工具提供程序、流式传输、立即返回
- **[references/error-handling.md](references/error-handling.md)** — 错误处理程序、重试逻辑、监控
- **[references/integration-examples.md](references/integration-examples.md)** — 数据库、REST API 和上下文感知工具示例
