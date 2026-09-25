# LangChain4j Spring Boot 集成

使用声明式 AI 服务、自动配置和 Spring Boot 启动器将 LangChain4j 与 Spring Boot 集成。配置 AI 模型 Bean，设置聊天内存，使用 Spring Data 实现 RAG 管道，并构建生产就绪的 AI 应用。

## 使用场景

在以下情况下使用此技能：
- 将 LangChain4j 集成到现有的 Spring Boot 应用中
- 使用 Spring Boot 构建 AI 驱动的微服务
- 使用 `@Bean` 注解配置 AI 模型 Bean
- 设置 AI 模型和服务的自动配置
- 使用 Spring 依赖注入创建声明式 AI 服务
- 使用 Spring Data 集成实现 RAG 系统
- 使用 Spring 上下文管理设置聊天内存
- 配置多个 AI 提供商（OpenAI、Azure、Ollama、Anthropic）
- 使用 Spring Boot 构建生产就绪的 AI 应用

## 概述

LangChain4j Spring Boot 集成通过 Spring Boot 启动器提供声明式 AI 服务，能够根据属性自动配置 AI 组件。结合 Spring 依赖注入和 LangChain4j 的 AI 功能，使用基于接口的定义和注解。

## 说明

### 1. 添加依赖项

```xml
<!-- 核心LangChain4j Spring Boot 启动器 -->
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-spring-boot-starter</artifactId>
    <version>1.8.0</version>
</dependency>

<!-- OpenAI Spring Boot 启动器 -->
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-open-ai-spring-boot-starter</artifactId>
    <version>1.8.0</version>
</dependency>
```

### 2. 配置应用属性

```properties
# application.properties
langchain4j.open-ai.chat-model.api-key=${OPENAI_API_KEY}
langchain4j.open-ai.chat-model.model-name=gpt-4o-mini
langchain4j.open-ai.chat-model.temperature=0.7
langchain4j.open-ai.chat-model.timeout=PT60S
langchain4j.open-ai.chat-model.max-tokens=1000
```

或使用 YAML：

```yaml
langchain4j:
  open-ai:
    chat-model:
      api-key: ${OPENAI_API_KEY}
      model-name: gpt-4o-mini
      temperature: 0.7
      timeout: 60s
      max-tokens: 1000
```

### 3. 创建声明式 AI 服务

```java
import dev.langchain4j.service.spring.AiService;

@AiService
public interface CustomerSupportAssistant {

    @SystemMessage("You are a helpful customer support agent for TechCorp.")
    String handleInquiry(String customerMessage);

    @UserMessage("Translate to {{language}}: {{text}}")
    String translate(String text, String language);
}
```

### 4. 启用组件扫描

```java
@SpringBootApplication
@ComponentScan(basePackages = {
    "com.yourcompany",
    "dev.langchain4j.service.spring"
})
public class Application {
    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }
}
```

### 5. 注入并使用 AI 服务

```java
@Service
public class CustomerService {

    private final CustomerSupportAssistant assistant;

    public CustomerService(CustomerSupportAssistant assistant) {
        this.assistant = assistant;
    }

    public String processCustomerQuery(String query) {
        return assistant.handleInquiry(query);
    }
}
```

### 6. 验证集成

设置后，验证配置：
1. 启动应用程序并检查日志以确认 `LangChain4jSpringBootAutoConfiguration` 激活
2. 确认 AI 服务 Bean 已注册：在 Spring 上下文中查找 `CustomerSupportAssistant`
3. 测试服务：调用 `assistant.handleInquiry("test")` 并验证是否返回响应

## 配置

**基于属性的配置：** 通过 `application.properties` 配置不同提供者的 AI 模型。

**手动 Bean 配置：** 对于高级配置，手动定义 Bean：

```java
@Configuration
public class AiConfig {

    @Bean
    public ChatModel chatModel(@Value("${OPENAI_API_KEY}") String apiKey) {
        return OpenAiChatModel.builder()
            .apiKey(apiKey)
            .modelName("gpt-4o-mini")
            .temperature(0.7)
            .build();
    }
}
```

**多个提供者：** 配置多个 AI 提供者时使用显式连接：

```java
@AiService(wiringMode = WiringMode.EXPLICIT)
interface MultiProviderAssistant {
    @AiServiceAnnotation
    ChatModel openAiModel;

    @AiServiceAnnotation
    ChatModel azureModel;
}
```

## 声明式 AI 服务

**基本 AI 服务：** 使用 `@AiService` 注解创建接口，并定义带有消息模板的方法。

**流式 AI 服务：** 使用 Project Reactor 实现流式响应：

```java
@AiService
public interface StreamingAssistant {
    @SystemMessage("You are a helpful assistant.")
    Flux<String> chatStream(String message);
}
```

**聊天内存：** 使用 Spring 上下文设置对话内存：

```java
@AiService
public interface ConversationalAssistant {
    @SystemMessage("You are a helpful assistant with memory.")
    String chat(@MemoryId String userId, String message);
}
```

## RAG 实现

**嵌入存储：** 使用 Spring Data 配置 RAG 管道的嵌入存储：

```java
@Configuration
public class RagConfig {

    @Bean
    public EmbeddingStore<TextSegment> embeddingStore() {
        return PgVectorEmbeddingStore.builder()
            .host("localhost")
            .port(5432)
            .database("vectordb")
            .table("embeddings")
            .dimension(1536)
            .build();
    }

    @Bean
    public EmbeddingModel embeddingModel() {
        return OpenAiEmbeddingModel.withApiKey(System.getenv("OPENAI_API_KEY"));
    }
}

@AiService
public interface RagAssistant {
    String answer(@UserMessage("Question: {{question}}") String question);
}
```

**文档摄取：** 使用 `ContentInjector` 和 `DocumentSplitter` 处理文档。
**内容检索：** 配置 `EmbeddingStoreContentRetriever` 以增强知识。

## 工具集成

**Spring 组件工具：** 将工具定义为 Spring 组件：

```java
@Component
public class Calculator {
    @Tool("Calculate the sum of two numbers")
    public double add(double a, double b) {
        return a + b;
    }
}

@AiService
public interface MathAssistant {
    String solve(String problem);
}
```

## 示例

### 基本AI服务

```java
@AiService
public interface ChatAssistant {
    @SystemMessage("You are a helpful assistant.")
    String chat(String message);
}
```

### 带内存的 AI 服务

```java
@AiService
public interface ConversationalAssistant {
    @SystemMessage("You are a helpful assistant with memory of conversations.")
    String chat(@MemoryId String userId, String message);
}
```

### 带工具的 AI 服务

```java
@Component
public class WeatherService {
    @Tool("Get weather for a city")
    public String getWeather(String city) {
        return "Sunny, 22°C in " + city;
    }
}

@AiService
public interface WeatherAssistant {
    String getWeatherForCity(String city);
}
```

更多示例（包括 RAG 配置、流式助手和多提供者设置），请参阅 [references/examples.md](references/examples.md)。

## 最佳实践

- **使用基于属性的配置：** 外部配置优于硬编码值
- **使用配置文件：** 开发、测试和生产的不同配置
- **添加适当的日志记录：** 调试 AI 服务调用并监控性能
- **实现重试机制：** 使用退避策略处理瞬态故障
- **监控令牌使用情况：** 跟踪令牌消耗并实施限制

## 参考

有关详细的 API 参考和高级配置：
- [API 参考](references/references.md) - 完整的 API 文档
- [示例](references/examples.md) - 综合实现示例
- [配置指南](references/configuration.md) - 深入配置选项

## 限制和警告

- 使用环境变量或密钥管理系统安全存储 API 密钥
- AI 模型响应是非确定性的；测试应考虑可变性
- AI 提供商可能适用速率限制；实施适当的重试和退避策略
- 内存提供者存储对话历史；实现清理以处理多用户场景
- 令牌成本会迅速累积；监控使用情况并实施令牌限制
- 流式响应需要适当的错误处理以处理部分失败
- 查看提供者特定文档以了解支持的特性
- 配置多个聊天模型时使用显式连接模式
- 在生产系统中使用前验证 AI 生成的输出
