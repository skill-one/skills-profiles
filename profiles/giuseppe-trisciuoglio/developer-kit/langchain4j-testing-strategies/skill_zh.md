# LangChain4J 测试策略

## 概述

使用 mock 进行单元测试、使用 Testcontainers 进行集成测试以及验证 RAG 系统、AI 服务和工具执行端到端的有效性。

## 使用场景

- **单元测试 AI 服务**：当你需要使用 LangChain4j AiServices 进行快速、隔离的测试时
- **集成测试 LangChain4j 组件**：当你使用 Testcontainers 测试真实的 ChatModel、EmbeddingModel 或 RAG 管道时
- **模拟 AI 模型**：当你需要确定性响应而不调用外部 API 时
- **测试基于 LLM 的 Java 应用**：当你验证 RAG 工作流、工具执行或检索链时

## 使用说明

### 1. 使用 Mock 进行单元测试

使用 mock 模型进行快速、隔离的测试。参考 `references/unit-testing.md`。

```java
ChatModel mockModel = mock(ChatModel.class);
when(mockModel.generate(any(String.class)))
    .thenReturn(Response.from(AiMessage.from("Mocked response")));

var service = AiServices.builder(AiService.class)
        .chatModel(mockModel)
        .build();
```

### 2. 配置测试依赖项

设置 Maven/Gradle 依赖项。参考 `references/testing-dependencies.md`。

- `langchain4j-test` - Guardrail 断言
- `testcontainers` - 容器化测试
- `mockito` - 模拟外部依赖
- `assertj` - 流畅断言

### 3. 使用 Testcontainers 进行集成测试

使用真实服务进行测试。参考 `references/integration-testing.md`。

```java
@Testcontainers
class OllamaIntegrationTest {
    @Container
    static GenericContainer<?> ollama = new GenericContainer<>(
        DockerImageName.parse("ollama/ollama:0.5.4")
    ).withExposedPorts(11434);

    @Test
    void shouldGenerateResponse() {
        // 验证容器健康状态
        assertTrue(ollama.isRunning());
        await().atMost(30, TimeUnit.SECONDS)
            .until(() -> ollama.getLogs().contains("API server listening"));

        ChatModel model = OllamaChatModel.builder()
                .baseUrl(ollama.getEndpoint())
                .build();

        // 在运行测试前验证模型响应
        assertDoesNotThrow(() -> model.generate("ping"));

        String response = model.generate("Test query");
        assertNotNull(response);
    }
}
```

### 4. 高级功能

`references/advanced-testing.md` 中的流式传输、内存、错误处理模式。

### 5. 测试工作流

遵循 `references/workflow-patterns.md` 中的测试金字塔：

- **70% 单元测试**：快速、使用 mock 进行隔离
- **20% 集成测试**：使用健康检查的真实服务
- **10% 端到端测试**：完整的工作流

```
70% 单元测试 ─ Mock ChatModel、guardrails、边界情况
20% 集成测试 ─ Testcontainers、向量存储、RAG
10% 端到端测试 ─ 完整的用户旅程
```

### 故障排除

- **容器启动失败**：检查 Docker 守护进程是否运行，验证镜像是否存在，增加超时时间
- **模型无响应**：验证 baseUrl 是否正确，检查容器日志，确保模型已加载
- **测试超时**：增加 `@Timeout` 持续时间以适应慢速模型，检查容器资源限制
- **不稳定测试**：在断言前添加重试逻辑或健康检查

## 示例

### 单元测试

```java
@Test
void shouldProcessQueryWithMock() {
    ChatModel mockModel = mock(ChatModel.class);
    when(mockModel.generate(any(String.class)))
        .thenReturn(Response.from(AiMessage.from("Test response")));

    var service = AiServices.builder(AiService.class)
            .chatModel(mockModel)
            .build();

    String result = service.chat("What is Java?");
    assertEquals("Test response", result);
}
```

### 使用 Testcontainers 的集成测试

```java
@Testcontainers
class RAGIntegrationTest {
    @Container
    static GenericContainer<?> ollama = new GenericContainer<>(
        DockerImageName.parse("ollama/ollama:0.5.4")
    );

    @BeforeAll
    static void waitForContainerReady() {
        await().atMost(60, TimeUnit.SECONDS)
            .until(() -> ollama.getLogs().contains("API server listening"));
    }

    @Test
    void shouldCompleteRAGWorkflow() {
        assertTrue(ollama.isRunning());

        var chatModel = OllamaChatModel.builder()
                .baseUrl(ollama.getEndpoint())
                .build();

        var embeddingModel = OllamaEmbeddingModel.builder()
                .baseUrl(ollama.getEndpoint())
                .build();

        var store = new InMemoryEmbeddingStore<>();
        var retriever = EmbeddingStoreContentRetriever.builder()
                .chatModel(chatModel)
                .embeddingStore(store)
                .embeddingModel(embeddingModel)
                .build();

        var assistant = AiServices.builder(RagAssistant.class)
                .chatLanguageModel(chatModel)
                .contentRetriever(retriever)
                .build();

        String response = assistant.chat("What is Spring Boot?");
        assertNotNull(response);
        assertTrue(response.contains("Spring"));
    }
}
```

## 最佳实践

- 使用 `@BeforeEach`/`@AfterEach` 进行测试隔离
- 单元测试中不要调用真实 API；使用 mock
- 对外部服务调用添加 `@Timeout`
- 测试成功和错误处理场景
- 验证响应一致性和边界情况

## 常见模式

### Mock 策略
```java
ChatModel mockModel = mock(ChatModel.class);
when(mockModel.generate(anyString())).thenReturn(Response.from(AiMessage.from("Mocked")));
when(mockModel.generate(eq("Hello"))).thenReturn(Response.from(AiMessage.from("Hi")));
when(mockModel.generate(contains("Java"))).thenReturn(Response.from(AiMessage.from("Java")));
```

### 断言辅助工具
```java
assertThat(response).isNotNull().isNotEmpty();
assertThat(response).containsAll(expectedKeywords);
assertThat(response).doesNotContain("error");
```

## 参考文档

- **[测试依赖项](references/testing-dependencies.md)** - Maven/Gradle 配置
- **[单元测试](references/unit-testing.md)** - Mock 模型、guardrails
- **[集成测试](references/integration-testing.md)** - Testcontainers、真实服务
- **[高级测试](references/advanced-testing.md)** - 流式传输、内存、错误处理
- **[工作流模式](references/workflow-patterns.md)** - 测试金字塔、最佳实践

## 限制和警告

- AI 响应是不可确定的；使用 mock 进行可靠的单元测试
- 测试中避免调用真实 API，以防止成本和速率限制
- 集成测试需要 Docker；使用容器健康检查
- RAG 测试需要正确初始化的向量存储
- 基于 mock 的测试无法保证实际 LLM 行为；补充集成测试
- 使用特定于测试的配置文件；不要影响生产数据
