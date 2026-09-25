# AWS SDK for Java 2.x - Amazon Bedrock

## 概述

通过 AWS SDK for Java 2.x 调用基础模型。配置客户端、构建特定模型的 JSON 负载、处理带错误恢复的流式响应、为 RAG 创建嵌入、将生成式 AI 集成到 Spring Boot 应用程序中，并实现指数退避以提高弹性。

## 何时使用

- 调用 Claude、Llama、Titan 或 Stable Diffusion 进行文本/图像生成
- 配置 BedrockClient 和 BedrockRuntimeClient 实例
- 构建和解析特定模型的负载（Claude、Titan、Llama 格式）
- 使用异步处理程序和错误恢复流式传输实时 AI 响应
- 为检索增强生成创建嵌入
- 将生成式 AI 集成到 Spring Boot 微服务中
- 使用指数退避重试逻辑处理限流

## 快速入门

### 依赖项

```xml
<!-- Bedrock (模型管理) -->
<dependency>
    <groupId>software.amazon.awssdk</groupId>
    <artifactId>bedrock</artifactId>
</dependency>

<!-- Bedrock Runtime (模型调用) -->
<dependency>
    <groupId>software.amazon.awssdk</groupId>
    <artifactId>bedrockruntime</artifactId>
</dependency>

<!-- 用于 JSON 处理 -->
<dependency>
    <groupId>org.json</groupId>
    <artifactId>json</artifactId>
    <version>20231013</version>
</dependency>
```

### 客户端设置

```java
import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.bedrock.BedrockClient;
import software.amazon.awssdk.services.bedrockruntime.BedrockRuntimeClient;

// 模型管理客户端
BedrockClient bedrockClient = BedrockClient.builder()
    .region(Region.US_EAST_1)
    .build();

// 模型调用客户端
BedrockRuntimeClient bedrockRuntimeClient = BedrockRuntimeClient.builder()
    .region(Region.US_EAST_1)
    .build();
```

## 说明

按照以下步骤进行生产就绪的 Bedrock 集成：

1. **配置 AWS 凭证** - 设置具有 Bedrock 权限的 IAM 角色（避免使用访问密钥）
2. **启用模型访问** - 在 AWS 控制台请求访问特定的基础模型
3. **初始化客户端** - 创建可重用的 `BedrockClient` 和 `BedrockRuntimeClient` 实例
4. **验证模型可用性** - 在生产使用前进行简单调用测试
5. **构建负载** - 创建具有正确格式的特定模型 JSON 负载
6. **处理响应** - 解析响应结构并提取内容
7. **实现流式传输** - 使用响应流处理程序进行实时生成
8. **添加错误处理** - 实现带指数退避的重试逻辑

**验证检查点**：在生产使用前始终使用简单提示（例如，“Hello”）进行测试，以验证模型访问和响应解析。

## 示例

### 使用 Claude 进行文本生成

```java
public String generateWithClaude(BedrockRuntimeClient client, String prompt) {
    JSONObject payload = new JSONObject()
        .put("anthropic_version", "bedrock-2023-05-31")
        .put("max_tokens", 1000)
        .put("messages", new JSONObject[]{
            new JSONObject().put("role", "user").put("content", prompt)
        });

    InvokeModelResponse response = client.invokeModel(InvokeModelRequest.builder()
        .modelId("anthropic.claude-sonnet-4-5-20250929-v1:0")
        .body(SdkBytes.fromUtf8String(payload.toString()))
        .build());

    JSONObject responseBody = new JSONObject(response.body().asUtf8String());
    return responseBody.getJSONArray("content")
        .getJSONObject(0)
        .getString("text");
}
```

### 模型发现

```java
import software.amazon.awssdk.services.bedrock.model.*;

public List<FoundationModelSummary> listFoundationModels(BedrockClient bedrockClient) {
    return bedrockClient.listFoundationModels().modelSummaries();
}
```

### 多模型调用

```java
public String invokeModel(BedrockRuntimeClient client, String modelId, String prompt) {
    JSONObject payload = createPayload(modelId, prompt);

    InvokeModelResponse response = client.invokeModel(request -> request
        .modelId(modelId)
        .body(SdkBytes.fromUtf8String(payload.toString())));

    return extractTextFromResponse(modelId, response.body().asUtf8String());
}

private JSONObject createPayload(String modelId, String prompt) {
    if (modelId.startsWith("anthropic.claude")) {
        return new JSONObject()
            .put("anthropic_version", "bedrock-2023-05-31")
            .put("max_tokens", 1000)
            .put("messages", new JSONObject[]{
                new JSONObject().put("role", "user").put("content", prompt)
            });
    } else if (modelId.startsWith("amazon.titan")) {
        return new JSONObject()
            .put("inputText", prompt)
            .put("textGenerationConfig", new JSONObject()
                .put("maxTokenCount", 512)
                .put("temperature", 0.7));
    } else if (modelId.startsWith("meta.llama")) {
        return new JSONObject()
            .put("prompt", "[INST] " + prompt + " [/INST]")
            .put("max_gen_len", 512)
            .put("temperature", 0.7);
    }
    throw new IllegalArgumentException("不支持的模型: " + modelId);
}
```

### 带错误处理的流式响应

```java
public String streamResponseWithRetry(BedrockRuntimeClient client, String modelId, String prompt, int maxRetries) {
    int attempt = 0;
    while (attempt < maxRetries) {
        try {
            JSONObject payload = createPayload(modelId, prompt);
            StringBuilder fullResponse = new StringBuilder();

            InvokeModelWithResponseStreamRequest request = InvokeModelWithResponseStreamRequest.builder()
                .modelId(modelId)
                .body(SdkBytes.fromUtf8String(payload.toString()))
                .build();

            client.invokeModelWithResponseStream(request,
                InvokeModelWithResponseStreamResponseHandler.builder()
                    .onEventStream(stream -> stream.forEach(event -> {
                        if (event instanceof PayloadPart) {
                            String chunk = ((PayloadPart) event).bytes().asUtf8String();
                            fullResponse.append(chunk);
                        }
                    }))
                    .onError(e -> System.err.println("流错误: " + e.getMessage()))
                    .build());

            return fullResponse.toString();
        } catch (Exception e) {
            attempt++;
            if (attempt >= maxRetries) {
                throw new RuntimeException("流式传输失败，尝试次数达到 " + maxRetries, e);
            }
            try {
                Thread.sleep((long) Math.pow(2, attempt) * 1000); // 指数退避
            } catch (InterruptedException ie) {
                Thread.currentThread().interrupt();
                throw new RuntimeException("重试期间被中断", ie);
            }
        }
    }
    throw new RuntimeException("流式传输中意外错误");
}
```

### 限流的指数退避

```java
import software.amazon.awssdk.awscore.exception.AwsServiceException;

public <T> T invokeWithRetry(Supplier<T> invocation, int maxRetries) {
    int attempt = 0;
    while (attempt < maxRetries) {
        try {
            return invocation.get();
        } catch (AwsServiceException e) {
            if (e.statusCode() == 429 || e.statusCode() >= 500) {
                attempt++;
                if (attempt >= maxRetries) throw e;
                long delayMs = Math.min(1000 * (1L << attempt) + (long) (Math.random() * 1000), 30000);
                Thread.sleep(delayMs);
            } else {
                throw e;
            }
        }
    }
    throw new IllegalStateException("不应达到此处");
}
```

### 文本嵌入

```java
public double[] createEmbeddings(BedrockRuntimeClient client, String text) {
    String modelId = "amazon.titan-embed-text-v1";

    JSONObject payload = new JSONObject().put("inputText", text);

    InvokeModelResponse response = client.invokeModel(request -> request
        .modelId(modelId)
        .body(SdkBytes.fromUtf8String(payload.toString())));

    JSONObject responseBody = new JSONObject(response.body().asUtf8String());
    JSONArray embeddingArray = responseBody.getJSONArray("embedding");

    double[] embeddings = new double[embeddingArray.length()];
    for (int i = 0; i < embeddingArray.length(); i++) {
        embeddings[i] = embeddingArray.getDouble(i);
    }
    return embeddings;
}
```

### Spring Boot 集成

```java
@Configuration
public class BedrockConfiguration {

    @Bean
    public BedrockClient bedrockClient() {
        return BedrockClient.builder()
            .region(Region.US_EAST_1)
            .build();
    }

    @Bean
    public BedrockRuntimeClient bedrockRuntimeClient() {
        return BedrockRuntimeClient.builder()
            .region(Region.US_EAST_1)
            .build();
    }
}

@Service
public class BedrockAIService {

    private final BedrockRuntimeClient bedrockRuntimeClient;
    private final ObjectMapper mapper;

    @Value("${bedrock.default-model-id:anthropic.claude-sonnet-4-5-20250929-v1:0}")
    private String defaultModelId;

    public BedrockAIService(BedrockRuntimeClient bedrockRuntimeClient, ObjectMapper mapper) {
        this.bedrockRuntimeClient = bedrockRuntimeClient;
        this.mapper = mapper;
    }

    public String generateText(String prompt) {
        Map<String, Object> payload = Map.of(
            "anthropic_version", "bedrock-2023-05-31",
            "max_tokens", 1000,
            "messages", List.of(Map.of("role", "user", "content", prompt))
        );

        InvokeModelResponse response = bedrockRuntimeClient.invokeModel(
            InvokeModelRequest.builder()
                .modelId(defaultModelId)
                .body(SdkBytes.fromUtf8String(mapper.writeValueAsString(payload)))
                .build());

        return extractText(response.body().asUtf8String());
    }
}
```

有关全面的用法模式，请参阅 [示例目录](references/aws-sdk-examples.md)。

## 最佳实践

### 模型选择
- **Claude 4.5 Sonnet**：复杂的推理、分析和创意任务
- **Claude 4.5 Haiku**：快速且经济实惠，适用于实时应用程序
- **Llama 3.1**：开源替代方案，适用于一般任务
- **Titan**：AWS 原生，适用于简单文本生成的成本效益方案

### 性能
- 重用客户端实例（避免每次请求创建新客户端）
- 使用异步客户端进行 I/O 操作
- 实现流式传输以处理长响应
- 缓存基础模型列表

### 安全
- 永远不要记录敏感的提示数据
- 使用 IAM 角色进行身份验证
- 对用户输入进行清理以防止提示注入
- 为公共应用程序实现速率限制

## 限制和警告

- **成本管理**：Bedrock API 调用按 token 收费；实施使用监控和预算警报。
- **模型访问**：基础模型必须在 AWS 控制台启用；验证区域可用性。
- **速率限制**：实施指数退避以处理限流；检查每个模型的限制。
- **负载大小**：每个模型的最大负载大小不同；对大文档进行分块。
- **流式传输复杂性**：仔细处理部分内容和错误恢复。
- **数据隐私**：AWS 可能记录提示和响应；审查数据策略。
- **凭证**：永远不要在代码中嵌入凭证；为 EC2/Lambda 使用 IAM 角色。

## 常用模型 ID

- Claude Sonnet 4.5: `anthropic.claude-sonnet-4-5-20250929-v1:0`
- Claude Haiku 4.5: `anthropic.claude-haiku-4-5-20251001-v1:0`
- Llama 3.1 70B: `meta.llama3-1-70b-instruct-v1:0`
- Titan 嵌入: `amazon.titan-embed-text-v1`

有关完整列表，请参阅 [模型参考](references/model-reference.md)。

## 参考

- [高级主题](references/advanced-topics.md) - 多模型模式、高级错误处理
- [模型参考](references/model-reference.md) - 详细规范、负载格式
- [测试策略](references/testing-strategies.md) - 单元测试、LocalStack 集成
- [AWS Bedrock 用户指南](references/aws-bedrock-user-guide.md)
- [AWS SDK 示例](references/aws-sdk-examples.md)
- [支持的模型](references/bedrock-models-supported.md)

## 相关技能

- `aws-sdk-java-v2-core` - 核心 AWS SDK 模式
- `langchain4j-ai-services-patterns` - LangChain4j 集成
- `spring-boot-dependency-injection` - Spring DI 模式
