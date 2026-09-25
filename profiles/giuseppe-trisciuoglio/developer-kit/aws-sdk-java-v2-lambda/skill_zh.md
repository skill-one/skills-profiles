# AWS SDK for Java 2.x - AWS Lambda

## 概述

AWS Lambda 是一种计算服务，无需管理服务器即可运行代码。使用此技能在应用程序和服务中实现 AWS Lambda 操作。

## 何时使用

- 从 Java 应用程序中调用 Lambda 函数
- 通过 SDK 部署和更新 Lambda 函数
- 管理函数配置和层
- 将 Lambda 与 Spring Boot 应用程序集成

## 快速参考

| 操作 | SDK 方法 | 用例 |
|-------|------------|----------|
| **调用** | `invoke()` | 同步/异步函数调用 |
| **列出函数** | `listFunctions()` | 获取所有 Lambda 函数 |
| **获取配置** | `getFunction()` | 检索函数配置 |
| **创建函数** | `createFunction()` | 创建新的 Lambda 函数 |
| **更新代码** | `updateFunctionCode()` | 部署新函数代码 |
| **更新配置** | `updateFunctionConfiguration()` | 修改设置（超时、内存、环境变量） |
| **删除函数** | `deleteFunction()` | 删除 Lambda 函数 |

## 说明

### 1. 添加依赖项

在 `pom.xml` 中包含 Lambda SDK 依赖项：

```xml
<dependency>
    <groupId>software.amazon.awssdk</groupId>
    <artifactId>lambda</artifactId>
</dependency>
```

有关完整设置的详细信息，请参阅 [client-setup.md](references/client-setup.md)。

### 2. 创建客户端

使用适当的配置实例化 `LambdaClient`：

```java
LambdaClient lambdaClient = LambdaClient.builder()
    .region(Region.US_EAST_1)
    .build();
```

对于异步操作，请使用 `LambdaAsyncClient`。

### 3. 调用 Lambda 函数

同步调用：

```java
InvokeRequest request = InvokeRequest.builder()
    .functionName("my-function")
    .payload(SdkBytes.fromUtf8String(payload))
    .build();

InvokeResponse response = lambdaClient.invoke(request);

return response.payload().asUtf8String();
```

有关模式的详细信息，请参阅 [invocation-patterns.md](references/invocation-patterns.md)。

### 4. 处理响应

解析响应有效负载并检查错误：

```java
if (response.functionError() != null) {
    throw new LambdaInvocationException("Lambda 错误: " + response.functionError());
}

String result = response.payload().asUtf8String();
```

### 5. 管理函数

创建、更新或删除 Lambda 函数：

```java
// 创建
CreateFunctionRequest createRequest = CreateFunctionRequest.builder()
    .functionName("my-function")
    .runtime(Runtime.JAVA17)
    .role(roleArn)
    .code(code)
    .build();

lambdaClient.createFunction(createRequest);

// 在继续之前验证函数是否处于活动状态
GetFunctionRequest getRequest = GetFunctionRequest.builder()
    .functionName("my-function")
    .build();
GetFunctionResponse getResponse = lambdaClient.getFunction(getRequest);
if (!"Active".equals(getResponse.configuration().state())) {
    throw new IllegalStateException("函数未处于活动状态: " + getResponse.configuration().stateReason());
}

// 更新代码
UpdateFunctionCodeRequest updateCodeRequest = UpdateFunctionCodeRequest.builder()
    .functionName("my-function")
    .zipFile(SdkBytes.fromByteArray(zipBytes))
    .build();

lambdaClient.updateFunctionCode(updateCodeRequest);

// 等待部署完成
Waiter<GetFunctionConfigurationRequest> waiter = lambdaClient.waiter();
waiter.waitUntilFunctionUpdatedActive(GetFunctionConfigurationRequest.builder()
    .functionName("my-function")
    .build());
```

有关完整模式的详细信息，请参阅 [function-management.md](references/function-management.md)。

### 6. 配置环境

设置环境变量和并发限制：

```java
Environment env = Environment.builder()
    .variables(Map.of(
        "DB_URL", "jdbc:postgresql://db",
        "LOG_LEVEL", "INFO"
    ))
    .build();

UpdateFunctionConfigurationRequest configRequest = UpdateFunctionConfigurationRequest.builder()
    .functionName("my-function")
    .environment(env)
    .timeout(60)
    .memorySize(512)
    .build();

lambdaClient.updateFunctionConfiguration(configRequest);
```

### 7. 与 Spring Boot 集成

配置 Lambda bean 和服务：

```java
@Configuration
public class LambdaConfiguration {
    @Bean
    public LambdaClient lambdaClient() {
        return LambdaClient.builder()
            .region(Region.US_EAST_1)
            .build();
    }
}

@Service
public class LambdaInvokerService {
    public <T, R> R invoke(String functionName, T request, Class<R> responseType) {
        // 实现
    }
}
```

有关完整集成的详细信息，请参阅 [spring-boot-integration.md](references/spring-boot-integration.md)。

### 8. 本地测试

使用模拟或 LocalStack 进行开发测试。

有关测试模式的详细信息，请参阅 [testing.md](references/testing.md)。

## 示例

### 基本调用

```java
public String invokeFunction(LambdaClient client, String functionName, String payload) {
    InvokeRequest request = InvokeRequest.builder()
        .functionName(functionName)
        .payload(SdkBytes.fromUtf8String(payload))
        .build();

    InvokeResponse response = client.invoke(request);

    if (response.functionError() != null) {
        throw new RuntimeException("Lambda 错误: " + response.functionError());
    }

    return response.payload().asUtf8String();
}
```

### 异步调用

```java
public void invokeAsync(LambdaClient client, String functionName, Map<String, Object> event) {
    String jsonPayload = new ObjectMapper().writeValueAsString(event);

    InvokeRequest request = InvokeRequest.builder()
        .functionName(functionName)
        .invocationType(InvocationType.EVENT)
        .payload(SdkBytes.fromUtf8String(jsonPayload))
        .build();

    client.invoke(request);
}
```

### Spring Boot 服务

```java
@Service
public class LambdaService {
    private final LambdaClient lambdaClient;

    public UserResponse processUser(UserRequest request) {
        String payload = objectMapper.writeValueAsString(request);

        InvokeResponse response = lambdaClient.invoke(
            InvokeRequest.builder()
                .functionName("user-processor")
                .payload(SdkBytes.fromUtf8String(payload))
                .build()
        );

        return objectMapper.readValue(
            response.payload().asUtf8String(),
            UserResponse.class
        );
    }
}
```

有关更多示例的详细信息，请参阅 [examples.md](references/examples.md)。

## 最佳实践

- **重用客户端**：创建一次 `LambdaClient`/`LambdaAsyncClient`；它们是线程安全的
- **使用异步客户端**：对于“发后即忘”调用，使用 `LambdaAsyncClient` 并配合 `CompletableFuture`
- **验证部署**：创建/更新操作后，始终等待函数状态变为 `Active`
- **限制有效负载大小**：将请求/响应有效负载保持在异步 256KB、同步 6MB 以下
- **配置超时**：将客户端读取超时设置略高于 Lambda 函数超时
- **使用最新运行时**：指定 `Runtime.JAVA17` 或更高版本以改善冷启动性能

## 限制和警告

- **有效负载限制**：6MB（同步）、256KB（异步调用）
- **超时**：每次调用最大 900 秒（15 分钟）
- **冷启动**：基于 JVM 的函数冷启动时间较长；使用 GraalVM Native Image 改善
- **部署大小**：函数代码+层不能超过 50MB（压缩）或 250MB（未压缩）
- **并发**：每个区域默认 1000 个；使用保留并发保证容量
- **成本**：使用 CloudWatch 指标监控；设置计费警报以防止成本失控

## 参考

- **[client-setup.md](references/client-setup.md)** — 客户端配置和设置
- **[invocation-patterns.md](references/invocation-patterns.md)** — 同步和异步调用模式
- **[function-management.md](references/function-management.md)** — 创建、更新、删除函数
- **[spring-boot-integration.md](references/spring-boot-integration.md)** — Spring Boot 配置和服务
- **[testing.md](references/testing.md)** — 单元和集成测试模式
- **[examples.md](references/examples.md)** — 完整代码示例和集成模式
- **[official-documentation.md](references/official-documentation.md)** — AWS Lambda 概念和 API 参考

## 相关技能

- `aws-sdk-java-v2-core` — 核心AWS SDK模式和客户端配置
- `spring-boot-dependency-injection` — Spring 依赖注入最佳实践
- `unit-test-service-layer` — 使用 Mockito 的服务测试模式
- `spring-boot-actuator` — 生产监控和健康检查

## 外部资源

- [GitHub 上的 Lambda 示例](https://github.com/awsdocs/aws-doc-sdk-examples/tree/main/javav2/example_code/lambda)
- [Lambda API 参考](https://sdk.amazonaws.com/java/api/latest/software/amazon/awssdk/services/lambda/package-summary.html)
- [AWS Lambda 开发者指南](https://docs.aws.amazon.com/lambda/latest/dg/welcome.html)
