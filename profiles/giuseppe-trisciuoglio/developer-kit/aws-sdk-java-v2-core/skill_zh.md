# AWS SDK for Java 2.x 核心模式

## 概述

使用此技能来为 AWS SDK for Java 2.x 客户端设置生产安全的默认值。

它专注于最重要的决策：
- 身份凭证和区域的解析方式
- 同步和异步 HTTP 客户端的配置方式
- 如何应用超时、重试、生命周期管理和测试

保持 `SKILL.md` 聚焦于设置和交付流程。使用 `references/` 文件来获取更深入的 API 细节和扩展示例。

## 何时使用

- 创建或加固 AWS SDK for Java 2.x 服务客户端
- 为 AWS 集成配置 Spring Boot bean
- 调试身份验证、区域或身份凭证问题
- 在同步（`S3Client`、`DynamoDbClient`）和异步（`S3AsyncClient`、`SqsAsyncClient`）客户端之间进行选择

## 说明

### 1. 选择服务客户端类型

- 同步客户端（`S3Client`、`DynamoDbClient`）用于请求/响应流程
- 异步客户端（`S3AsyncClient`、`SqsAsyncClient`）用于并发、流式传输或背压
- 每个服务和配置文件重用一个客户端

### 2. 配置身份凭证和区域解析

使用具有环境感知默认值的 `DefaultCredentialsProvider`：
- 本地开发：共享 AWS 配置、SSO 或环境变量
- CI/CD：Web 身份或注入的环境变量
- AWS 运行时：ECS 任务角色、EKS IRSA 或 EC2 实例配置文件

仅当需要多账户访问、测试隔离或配置文件切换时才覆盖。

**验证**：在启动时调用 `StsClient.getCallerIdentity()` 以确认身份凭证解析。

### 3. 配置 HTTP 客户端、超时和重试

显式设置生产值：
- API 调用超时和尝试超时
- 连接超时和最大连接数或并发
- 与服务配额和幂等性一致的重试策略

使用 ApacheHttpClient 用于同步，NettyNioAsyncHttpClient 用于异步。

**验证**：在失败条件下确认超时和重试行为。

### 4. 将客户端作为应用程序级依赖项连接

在 Spring Boot 中：
- 将客户端作为 `@Bean` 单例公开
- 通过构造函数注入
- 将身份凭证和区域保留在配置文件中

**验证**：检查客户端没有被创建在热执行路径中。

如果生命周期未自动管理，则在关闭时关闭自定义 HTTP 客户端和 SDK 客户端。

### 5. 在集成边界处理失败

在边界层：
- 捕获 `SdkException` 或特定于服务的异常
- 区分可重试的失败与身份验证、配额和验证失败
- 记录请求上下文，永远不要记录密钥或原始身份凭证

### 6. 在发货前运行集成测试

- 在目标环境中验证区域和调用者身份
- 对 LocalStack、Testcontainers 或沙盒账户运行测试
- 在 Spring Boot 配置中使用 `@PostConstruct`，如果身份凭证缺失则快速失败

```java
StsClient stsClient = StsClient.builder().build();
GetCallerIdentityResponse identity = stsClient.getCallerIdentity();
// 记录：成功验证为：{identity.arn()}
```

## 示例

### 示例 1：具有显式 HTTP 和超时设置的 Spring Boot 同步客户端

```java
@Configuration
public class AwsClientConfiguration {

    @Bean
    S3Client s3Client() {
        return S3Client.builder()
            .region(Region.of("eu-south-2"))
            .credentialsProvider(DefaultCredentialsProvider.create())
            .httpClientBuilder(ApacheHttpClient.builder()
                .maxConnections(100)
                .connectionTimeout(Duration.ofSeconds(3)))
            .overrideConfiguration(ClientOverrideConfiguration.builder()
                .apiCallAttemptTimeout(Duration.ofSeconds(10))
                .apiCallTimeout(Duration.ofSeconds(30))
                .build())
            .build();
    }
}
```

### 示例 2：用于高并发工作负载的异步客户端

```java
SqsAsyncClient sqsAsyncClient = SqsAsyncClient.builder()
    .region(Region.US_EAST_1)
    .credentialsProvider(DefaultCredentialsProvider.create())
    .httpClientBuilder(NettyNioAsyncHttpClient.builder()
        .maxConcurrency(200)
        .connectionTimeout(Duration.ofSeconds(3))
        .readTimeout(Duration.ofSeconds(20)))
    .overrideConfiguration(ClientOverrideConfiguration.builder()
        .apiCallTimeout(Duration.ofSeconds(30))
        .build())
    .build();
```

## 最佳实践

- 除非项目要求另有说明，否则默认使用 `DefaultCredentialsProvider`。
- 对于服务器端服务，显式选择区域。
- 重用 SDK 客户端，而不是每次请求都构造它们。
- 考虑服务配额和幂等性来调整重试。
- 在 SDK 之上进行业务映射，而不是在控制器内部。
- 将集成测试保持在创建客户端的配置附近。
- 将深度特定于服务的示例移动到专门的技能，如 S3、DynamoDB、Bedrock 或 Secrets Manager。

## 限制和警告

- 不要在源代码、示例或配置文件中嵌入访问密钥或会话令牌。
- 只有在严格限定的本地测试中才接受静态身份凭证。
- 缺失区域或无效身份凭证解析通常仅在第一次调用时失败，因此请明确验证启动假设。
- 异步客户端需要生命周期管理底层 HTTP 资源。
- 过多的重试会放大限流并增加延迟。
- 代理、TLS 和指标发布器 API 可能因所选 HTTP 堆栈和 SDK 版本而异；根据项目已使用的版本调整示例。

## 参考

- `references/api-reference.md`
- `references/best-practices.md`
- `references/developer-guide.md`

## 相关技能

- `aws-sdk-java-v2-secrets-manager`
- `aws-sdk-java-v2-s3`
- `aws-sdk-java-v2-dynamodb`
- `aws-sdk-java-v2-bedrock`
