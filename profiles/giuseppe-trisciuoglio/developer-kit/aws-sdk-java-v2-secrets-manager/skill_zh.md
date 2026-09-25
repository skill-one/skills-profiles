# AWS SDK for Java 2.x - AWS Secrets Manager

## 概述

使用此技能从 Java 服务中通过 AWS Secrets Manager 管理应用程序密钥。

它专注于生产中重要的操作流程：
- 如何安全地检索和反序列化密钥
- 何时添加本地缓存
- 如何将密钥访问集成到 Spring Boot 中，而不会将值泄漏到日志或配置文件中

将大型 API 注释和扩展的设置细节保留在捆绑的参考文档中。

## 何时使用

在以下情况下使用此技能：
- 用管理的密钥替换硬编码的密码、API 密钥或令牌
- 在运行时加载数据库凭证或第三方 API 凭证
- 添加缓存以减少 Secrets Manager 延迟和 API 成本
- 处理密钥版本阶段，如 `AWSCURRENT` 和 `AWSPENDING`
- 将密钥访问连接到 Spring Boot bean 或配置服务
- 准备支持轮换的应用程序或 Lambda 轮换工作流

典型的触发短语包括 `java secrets manager`、`spring boot secret`、`aws secret cache`、`load db credentials from secrets manager` 和 `rotate secret`。

## 说明

### 1. 在编写访问代码之前对密钥建模

决定：
- 密钥名称和路径约定
- 值是纯文本还是结构化 JSON
- 允许哪个应用程序边界读取它
- 调用者是否需要在每次请求中获取最新值，或者可以容忍缓存

对于包含数据库连接详情等多字段凭证，优先选择 JSON 密钥。

### 2. 为每个应用程序配置创建一个可重用的客户端

使用单个 `SecretsManagerClient`，除非环境需要更具体的配置，否则使用显式的区域和默认的凭证提供链。

将客户端创建保留在配置代码中，而不是业务服务中。

### 3. 在边界层检索和反序列化

在集成边界：
- 使用 `GetSecretValueRequest` 检索
- 将 JSON 反序列化为类型的对象或验证后的映射
- 将 AWS 异常转换为应用程序级别的错误
- 永远不要记录 `secretString()` 或将其包含在抛出的异常消息中

### 4. 仅在解决实际问题时添加缓存

在以下情况下使用缓存：
- 密钥被频繁读取
- 延迟对启动或请求处理很重要
- 重复查找的成本是实质性的

清楚地记录缓存 TTL 预期，特别是如果密钥会轮换。

### 5. 为轮换和分阶段版本设计

如果密钥会轮换：
- 通过一个薄的服务层读取，以便缓存失效和重试行为保持集中
- 了解哪些调用者必须容忍 `AWSPENDING` 在验证工作流期间
- 测试应用程序在陈旧缓存窗口或部分轮换失败期间的行为

### 6. 验证端到端行为

在发布前：
- 验证 IAM 权限和 KMS 访问
- 测试缺少密钥、错误区域和解密失败路径
- 确认密钥不会出现在日志、指标或调试端点中
- 证明数据库或 API 客户端在凭证轮换时正确刷新

## 示例

### 示例 1：可重用的客户端和类型化的密钥查找

```java
@Configuration
public class SecretsConfiguration {

    @Bean
    SecretsManagerClient secretsManagerClient() {
        return SecretsManagerClient.builder()
            .region(Region.of("eu-south-2"))
            .credentialsProvider(DefaultCredentialsProvider.create())
            .build();
    }
}

@Service
public class SecretsService {

    private final SecretsManagerClient client;
    private final ObjectMapper objectMapper;

    public SecretsService(SecretsManagerClient client, ObjectMapper objectMapper) {
        this.client = client;
        this.objectMapper = objectMapper;
    }

    public DatabaseSecret loadDatabaseSecret(String secretId) throws JsonProcessingException {
        GetSecretValueResponse response = client.getSecretValue(
            GetSecretValueRequest.builder().secretId(secretId).build()
        );
        return objectMapper.readValue(response.secretString(), DatabaseSecret.class);
    }
}
```

### 示例 2：缓存热路径密钥查找

```java
public class CachedSecretsService {

    private final SecretCache cache;

    public CachedSecretsService(SecretsManagerClient client) {
        this.cache = new SecretCache(client);
    }

    public String apiToken(String secretId) {
        return cache.getSecretString(secretId);
    }
}
```

仅在应用程序可以容忍所选缓存刷新行为时使用此模式。

## 最佳实践

- 使用与域和环境边界匹配的分层密钥名称。
- 优先选择类型化的 JSON 反序列化，而不是分散在代码库中的字符串解析。
- 将密钥检索保留在基础设施服务中，而不是控制器或实体中。
- 重用 SDK 客户端和缓存实例。
- 结合最小权限 IAM、KMS 权限和 CloudTrail 可见性。
- 在代码和操作文档中明确轮换行为。

## 限制和警告

- 不要记录密钥值、序列化的密钥对象或解密的有效载荷片段。
- 缓存值在轮换期间或之后可能仍然陈旧，具体取决于 TTL 和刷新行为。
- 密钥访问可能因 IAM 策略、KMS 策略、区域不匹配或已删除版本而失败；显式处理这些情况。
- 自动轮换不是每个密钥形状或集成的可用选项。
- 大型或频繁变化的密钥可能不适合激进的内存缓存。

## 参考

- `references/api-reference.md`
- `references/caching-guide.md`
- `references/spring-boot-integration.md`

## 相关技能

- `aws-sdk-java-v2-core`
- `aws-sdk-java-v2-kms`
- `spring-boot-dependency-injection`
