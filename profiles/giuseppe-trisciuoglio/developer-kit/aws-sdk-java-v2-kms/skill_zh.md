# AWS SDK for Java 2.x - AWS KMS (密钥管理服务)

## 概述

使用 AWS SDK for Java 2.x 提供的 AWS KMS 模式。涵盖密钥管理、加密/解密、封装加密、数字签名和 Spring Boot 集成。

## 说明

1. **设置 IAM 权限** - 授予 kms:* 操作的最小权限
2. **创建 KMS 客户端** - 使用区域和凭证实例化 KmsClient
3. **创建密钥** - 使用 createKey() → **在继续之前验证密钥状态为 ENABLED**
4. **设置密钥策略** - 定义密钥使用权限 → **在生产前测试访问**
5. **加密数据** - 使用 encrypt() 对小于 4KB 的数据进行加密；**验证密文不为空**
6. **封装加密** - 对于较大数据，使用 generateDataKey() → **验证数据密钥生成成功**
7. **数字签名** - 创建签名密钥 → **在 sign/verify 后验证 signatureValid=true**
8. **密钥轮换** - 启用自动轮换 → **确认轮换计划已激活**

## 使用场景

- 创建/管理用于数据保护的对称加密密钥
- 实现用于大数据的封装加密
- 生成用于本地加密的 KMS 管理密钥的数据密钥
- 使用非对称密钥设置数字签名
- 将加密集成到 Spring Boot 应用程序中

## 依赖项

### Maven

```xml
<dependency>
    <groupId>software.amazon.awssdk</groupId>
    <artifactId>kms</artifactId>
</dependency>
```

### Gradle

```groovy
implementation 'software.amazon.awssdk:kms:2.x.x'
```

## 客户端设置

### 基础同步客户端

```java
import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.kms.KmsClient;

KmsClient kmsClient = KmsClient.builder()
    .region(Region.US_EAST_1)
    .build();
```

### 基础异步客户端

```java
import software.amazon.awssdk.services.kms.KmsAsyncClient;

KmsAsyncClient kmsAsyncClient = KmsAsyncClient.builder()
    .region(Region.US_EAST_1)
    .build();
```

### 高级客户端配置

```java
KmsClient kmsClient = KmsClient.builder()
    .region(Region.of(System.getenv("AWS_REGION")))
    .credentialsProvider(DefaultCredentialsProvider.create())
    .overrideConfiguration(c -> c.retryPolicy(RetryPolicy.builder()
        .numRetries(3)
        .build()))
    .build();
```

## 基础密钥管理

### 创建加密密钥

```java
public String createEncryptionKey(KmsClient kmsClient, String description) {
    CreateKeyRequest request = CreateKeyRequest.builder()
        .description(description)
        .keyUsage(KeyUsageType.ENCRYPT_DECRYPT)
        .build();

    CreateKeyResponse response = kmsClient.createKey(request);
    return response.keyMetadata().keyId();
}
```

### 描述密钥

```java
public KeyMetadata getKeyMetadata(KmsClient kmsClient, String keyId) {
    DescribeKeyRequest request = DescribeKeyRequest.builder()
        .keyId(keyId)
        .build();

    return kmsClient.describeKey(request).keyMetadata();
}
```

### 启用/禁用密钥

```java
public void toggleKeyState(KmsClient kmsClient, String keyId, boolean enable) {
    if (enable) {
        kmsClient.enableKey(EnableKeyRequest.builder().keyId(keyId).build());
    } else {
        kmsClient.disableKey(DisableKeyRequest.builder().keyId(keyId).build());
    }
}
```

## 基础加密和解密

### 加密数据

```java
public String encryptData(KmsClient kmsClient, String keyId, String plaintext) {
    SdkBytes plaintextBytes = SdkBytes.fromString(plaintext, StandardCharsets.UTF_8);

    EncryptRequest request = EncryptRequest.builder()
        .keyId(keyId)
        .plaintext(plaintextBytes)
        .build();

    EncryptResponse response = kmsClient.encrypt(request);
    return Base64.getEncoder().encodeToString(
        response.ciphertextBlob().asByteArray());
}
```

### 解密数据

```java
public String decryptData(KmsClient kmsClient, String ciphertextBase64) {
    byte[] ciphertext = Base64.getDecoder().decode(ciphertextBase64);
    SdkBytes ciphertextBytes = SdkBytes.fromByteArray(ciphertext);

    DecryptRequest request = DecryptRequest.builder()
        .ciphertextBlob(ciphertextBytes)
        .build();

    DecryptResponse response = kmsClient.decrypt(request);
    return response.plaintext().asString(StandardCharsets.UTF_8);
}
```

## 封装加密模式

### 生成和使用数据密钥

```java
public DataKeyResult encryptWithEnvelope(KmsClient kmsClient, String masterKeyId, byte[] data) {
    try {
        GenerateDataKeyRequest keyRequest = GenerateDataKeyRequest.builder()
            .keyId(masterKeyId)
            .keySpec(DataKeySpec.AES_256)
            .build();

        GenerateDataKeyResponse keyResponse = kmsClient.generateDataKey(keyRequest);

        // 验证响应
        if (keyResponse.plaintext() == null || keyResponse.ciphertextBlob() == null) {
            throw new IllegalStateException("数据密钥生成返回了 null");
        }

        byte[] encryptedData = encryptWithAES(data, keyResponse.plaintext().asByteArray());

        // 从内存中清除明文密钥
        Arrays.fill(keyResponse.plaintext().asByteArray(), (byte) 0);

        return new DataKeyResult(encryptedData, keyResponse.ciphertextBlob().asByteArray());

    } catch (KmsException e) {
        throw new RuntimeException("封装加密失败: " + e.awsErrorDetails().errorCode(), e);
    }
}

public byte[] decryptWithEnvelope(KmsClient kmsClient, DataKeyResult encryptedEnvelope) {
    try {
        DecryptRequest keyDecryptRequest = DecryptRequest.builder()
            .ciphertextBlob(SdkBytes.fromByteArray(encryptedEnvelope.encryptedKey()))
            .build();

        DecryptResponse keyDecryptResponse = kmsClient.decrypt(keyDecryptRequest);

        // 验证响应
        if (keyDecryptResponse.plaintext() == null) {
            throw new IllegalStateException("密钥解密返回了 null");
        }

        byte[] decryptedData = decryptWithAES(
            encryptedEnvelope.encryptedData(),
            keyDecryptResponse.plaintext().asByteArray());

        // 从内存中清除明文密钥
        Arrays.fill(keyDecryptResponse.plaintext().asByteArray(), (byte) 0);

        return decryptedData;

    } catch (KmsException e) {
        throw new RuntimeException("封装解密失败: " + e.awsErrorDetails().errorCode(), e);
    }
}
```

## 数字签名

### 创建签名密钥和签名数据

```java
public String createAndSignData(KmsClient kmsClient, String description, String message) {
    // 创建签名密钥
    CreateKeyRequest keyRequest = CreateKeyRequest.builder()
        .description(description)
        .keySpec(KeySpec.RSA_2048)
        .keyUsage(KeyUsageType.SIGN_VERIFY)
        .build();

    CreateKeyResponse keyResponse = kmsClient.createKey(keyRequest);
    String keyId = keyResponse.keyMetadata().keyId();

    // 签名数据
    SignRequest signRequest = SignRequest.builder()
        .keyId(keyId)
        .message(SdkBytes.fromString(message, StandardCharsets.UTF_8))
        .signingAlgorithm(SigningAlgorithmSpec.RSASSA_PSS_SHA_256)
        .build();

    SignResponse signResponse = kmsClient.sign(signRequest);
    return Base64.getEncoder().encodeToString(
        signResponse.signature().asByteArray());
}
```

### 验证签名

```java
public boolean verifySignature(KmsClient kmsClient,
                             String keyId,
                             String message,
                             String signatureBase64) {
    byte[] signature = Base64.getDecoder().decode(signatureBase64);

    VerifyRequest verifyRequest = VerifyRequest.builder()
        .keyId(keyId)
        .message(SdkBytes.fromString(message, StandardCharsets.UTF_8))
        .signature(SdkBytes.fromByteArray(signature))
        .signingAlgorithm(SigningAlgorithmSpec.RSASSA_PSS_SHA_256)
        .build();

    VerifyResponse verifyResponse = kmsClient.verify(verifyRequest);
    return verifyResponse.signatureValid();
}
```

## Spring Boot 集成

### 配置类

```java
@Configuration
public class KmsConfiguration {

    @Bean
    public KmsClient kmsClient() {
        return KmsClient.builder()
            .region(Region.US_EAST_1)
            .build();
    }

    @Bean
    public KmsAsyncClient kmsAsyncClient() {
        return KmsAsyncClient.builder()
            .region(Region.US_EAST_1)
            .build();
    }
}
```

### 加密服务

```java
@Service
@RequiredArgsConstructor
public class KmsEncryptionService {

    private final KmsClient kmsClient;

    @Value("${kms.encryption-key-id}")
    private String keyId;

    public String encrypt(String plaintext) {
        try {
            EncryptRequest request = EncryptRequest.builder()
                .keyId(keyId)
                .plaintext(SdkBytes.fromString(plaintext, StandardCharsets.UTF_8))
                .build();

            EncryptResponse response = kmsClient.encrypt(request);
            return Base64.getEncoder().encodeToString(
                response.ciphertextBlob().asByteArray());

        } catch (KmsException e) {
            throw new RuntimeException("加密失败", e);
        }
    }

    public String decrypt(String ciphertextBase64) {
        try {
            byte[] ciphertext = Base64.getDecoder().decode(ciphertextBase64);

            DecryptRequest request = DecryptRequest.builder()
                .ciphertextBlob(SdkBytes.fromByteArray(ciphertext))
                .build();

            DecryptResponse response = kmsClient.decrypt(request);
            return response.plaintext().asString(StandardCharsets.UTF_8);

        } catch (KmsException e) {
            throw new RuntimeException("解密失败", e);
        }
    }
}
```

## 示例

### 基础加密示例

```java
public class BasicEncryptionExample {
    public static void main(String[] args) {
        KmsClient kmsClient = KmsClient.builder()
            .region(Region.US_EAST_1)
            .build();

        // 创建密钥
        String keyId = createEncryptionKey(kmsClient, "示例加密密钥");
        System.out.println("创建的密钥: " + keyId);

        // 加密和解密
        String plaintext = "Hello, World!";
        String encrypted = encryptData(kmsClient, keyId, plaintext);
        String decrypted = decryptData(kmsClient, encrypted);

        System.out.println("原始: " + plaintext);
        System.out.println("解密: " + decrypted);
    }
}
```

### 封装加密示例

```java
public class EnvelopeEncryptionExample {
    public static void main(String[] args) {
        KmsClient kmsClient = KmsClient.builder()
            .region(Region.US_EAST_1)
            .build();

        String masterKeyId = "alias/your-master-key";
        String largeData = "这是一个需要加密的大量数据...";
        byte[] data = largeData.getBytes(StandardCharsets.UTF_8);

        // 使用封装模式加密
        DataKeyResult encryptedEnvelope = encryptWithEnvelope(
            kmsClient, masterKeyId, data);

        // 解密
        byte[] decryptedData = decryptWithEnvelope(
            kmsClient, encryptedEnvelope);

        String result = new String(decryptedData, StandardCharsets.UTF_8);
        System.out.println("解密: " + result);
    }
}
```

## 最佳实践

### 安全

- **始终使用封装加密处理大量数据** - 本地加密数据，仅用 KMS 加密数据密钥
- **使用加密上下文** - 添加上下文信息以跟踪和审计使用情况
- **永不记录敏感数据** - 避免记录明文或加密密钥
- **实施适当的密钥生命周期** - 启用自动轮换并设置删除策略
- **为不同用途使用不同的密钥** - 不要跨多个应用程序重用密钥

### 性能

- **缓存加密数据密钥** - 通过缓存数据密钥减少 KMS API 调用
- **使用异步操作** - 利用异步客户端进行非阻塞 I/O
- **重用客户端实例** - 不要为每个操作创建新客户端
- **实施连接池** - 配置适当的连接池设置

### 错误处理

- **实施重试逻辑** - 使用指数退避处理限流异常
- **检查密钥状态** - 在执行操作前验证密钥已启用
- **使用断路器** - 在 KMS 故障期间防止级联故障
- **全面记录错误** - 包括 KMS 错误代码和上下文

## 参考

有关详细的实现模式、高级技术和全面示例：

- @references/technical-guide.md - 完整的技术实现模式
- @references/spring-boot-integration.md - Spring Boot 集成模式
- @references/testing.md - 测试策略和示例
- @references/best-practices.md - 安全和操作最佳实践

## 相关技能

- `@`aws-sdk-java-v2-core - 核心AWS SDK模式和配置
- `@`aws-sdk-java-v2-dynamodb - DynamoDB 集成模式
- `@`aws-sdk-java-v2-secrets-manager - 密钥管理模式
- `@`spring-boot-dependency-injection - Spring 依赖注入模式

## 外部参考

- [AWS KMS 开发者指南](https://docs.aws.amazon.com/kms/latest/developerguide/)
- [AWS SDK for Java 2.x 文档](https://docs.aws.amazon.com/sdk-for-java/latest/developer-guide/home.html)
- [KMS 最佳实践](https://docs.aws.amazon.com/kms/latest/developerguide/best-practices.html)

## 限制和警告

- **数据大小限制**：直接加密限制为 4KB；使用封装加密处理较大数据
- **密钥使用限制**：KMS 对每秒 API 调用有配额
- **密钥材料**：导入的密钥材料不能由 AWS 管理轮换
- **密钥删除**：密钥删除需要 7-30 天的等待期
- **区域边界**：KMS 密钥不能跨区域使用
- **成本考虑**：KMS 按每秒 API 调用和密钥存储收费
- **非对称密钥**：并非所有区域都支持非对称密钥类型
- **密钥策略**：密钥策略的更改需要仔细的 IAM 审查
- **封装加密**：需要正确实现以保障数据密钥安全
- **日志记录**：启用 CloudTrail 以审计所有 KMS API 使用
