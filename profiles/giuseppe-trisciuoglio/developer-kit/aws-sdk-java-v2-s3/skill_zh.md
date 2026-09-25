# AWS SDK for Java 2.x - Amazon S3

## 概述

提供 S3 操作的模式：存储桶管理、支持分片的对象上传/下载、预签名 URL、S3 传输管理器以及使用 AWS SDK for Java 2.x 的特定于 S3 的配置。

## 何时使用

- 使用正确配置创建、列出或删除 S3 存储桶
- 从 S3 上传或下载带有元数据和加密的对象
- 使用分片上传处理大于 100MB 的大文件
- 生成预签名 URL 以临时访问 S3 对象
- 在 S3 存储桶之间复制或移动对象并保留元数据
- 设置对象元数据、存储类别和访问控制
- 实现优化的文件传输的 S3 传输管理器
- 将 S3 集成到 Spring Boot 应用程序中用于云存储

## 快速参考

| 操作 | 方法 | 备注 |
|-------|--------|-------|
| 创建存储桶 | `createBucket()` | 使用 `waiter().waitUntilBucketExists()` 等待 |
| 上传对象 | `putObject()` | 使用 `RequestBody.fromFile()` |
| 下载对象 | `getObject()` | 流到文件或内存 |
| 删除对象 | `deleteObjects()` | 批量最多 1000 个键 |
| 预签名 URL | `presigner.presignGetObject()` | 最大 7 天过期 |

### 存储类别

| 类别 | 用例 |
|-------|----------|
| `STANDARD` | 经常访问的数据 |
| `STANDARD_IA` | 不经常访问的数据 |
| `GLACIER` | 长期归档 |
| `INTELLIGENT_TIERING` | 自动成本优化 |

## 说明

### 1. 添加依赖项

```xml
<dependency>
    <groupId>software.amazon.awssdk</groupId>
    <artifactId>s3</artifactId>
    <version>2.20.0</version>
</dependency>

<dependency>
    <groupId>software.amazon.awssdk</groupId>
    <artifactId>s3-transfer-manager</artifactId>
    <version>2.20.0</version>
</dependency>
```

### 2. 创建 S3 客户端

```java
S3Client s3Client = S3Client.builder()
    .region(Region.US_EAST_1)
    .build();

// 带重试逻辑
S3Client s3Client = S3Client.builder()
    .region(Region.US_EAST_1)
    .overrideConfiguration(b -> b
        .retryPolicy(RetryPolicy.builder()
            .numRetries(3)
            .build()))
    .build();
```

### 3. 创建存储桶

```java
CreateBucketRequest request = CreateBucketRequest.builder()
    .bucket(bucketName)
    .build();

s3Client.createBucket(request);

// 等待就绪
s3Client.waiter().waitUntilBucketExists(
    HeadBucketRequest.builder().bucket(bucketName).build()
);
```

### 4. 上传对象

```java
PutObjectRequest request = PutObjectRequest.builder()
    .bucket(bucketName)
    .key(key)
    .contentType("application/pdf")
    .serverSideEncryption(ServerSideEncryption.AES256)
    .storageClass(StorageClass.STANDARD_IA)
    .build();

s3Client.putObject(request, RequestBody.fromFile(Paths.get(filePath)));

// 验证上传完成
HeadObjectResponse headResp = s3Client.headObject(HeadObjectRequest.builder()
    .bucket(bucketName)
    .key(key)
    .build());
```

### 5. 下载对象

```java
GetObjectRequest request = GetObjectRequest.builder()
    .bucket(bucketName)
    .key(key)
    .build();

s3Client.getObject(request, Paths.get(destPath));
```

### 6. 生成预签名 URL

```java
try (S3Presigner presigner = S3Presigner.create()) {
    GetObjectRequest getRequest = GetObjectRequest.builder()
        .bucket(bucketName)
        .key(key)
        .build();

    GetObjectPresignRequest presignRequest = GetObjectPresignRequest.builder()
        .signatureDuration(Duration.ofMinutes(10))
        .getObjectRequest(getRequest)
        .build();

    String url = presigner.presignGetObject(presignRequest).url().toString();
}
```

### 7. 使用传输管理器（大文件）

```java
try (S3TransferManager tm = S3TransferManager.create()) {
    UploadFileRequest request = UploadFileRequest.builder()
        .putObjectRequest(req -> req.bucket(bucketName).key(key))
        .source(Paths.get(filePath))
        .build();

    FileUpload upload = tm.uploadFile(request);
    CompletedFileUpload result = upload.completionFuture().join();
}
```

## 最佳实践

### 性能
- **使用 S3 传输管理器**：自动分片上传文件 >100MB
- **重用 S3 客户端**：客户端是线程安全的；在整个应用程序中重用
- **启用异步操作**：使用 `S3AsyncClient` 处理 I/O 密集型操作
- **配置超时**：为大型文件操作设置适当的超时

### 安全
- **使用临时凭证**：IAM 角色或 AWS STS 用于短期令牌
- **启用加密**：使用 AES-256 或 AWS KMS 处理敏感数据
- **使用预签名 URL**：避免通过临时访问暴露凭证
- **验证元数据**：清理用户提供的元数据

### 错误处理
- **实现重试逻辑**：指数退避网络操作
- **处理限制**：正确处理 429 响应
- **清理失败**：中止失败的分片上传

### 成本优化
- **使用适当的存储类别**：STANDARD、STANDARD_IA、INTELLIGENT_TIERING
- **实现生命周期策略**：自动转换/过期
- **最小化 API 调用**：尽可能使用批量操作

## 限制和警告

- **对象大小**：单个 PUT 限制为 5GB；使用分片上传大文件
- **存储桶名称**：必须跨所有 AWS 账户全局唯一
- **对象不可变性**：对象不能修改；必须完全替换
- **最终一致性**：列表操作在上传后可能有轻微延迟
- **预签名 URL**：最大过期时间为 7 天
- **分片上传**：部分至少为 5MB，最后一部分除外

## 示例

### 带验证的完整上传工作流

```java
// 1. 带验证上传
PutObjectRequest putRequest = PutObjectRequest.builder()
    .bucket(bucketName)
    .key(key)
    .contentType(contentType)
    .build();

s3Client.putObject(putRequest, RequestBody.fromFile(Paths.get(filePath)));

// 2. 使用 headObject 验证
HeadObjectResponse headResp = s3Client.headObject(HeadObjectRequest.builder()
    .bucket(bucketName)
    .key(key)
    .build());

// 3. 验证元数据
long fileSize = Files.size(Paths.get(filePath));
if (headResp.contentLength() != fileSize) {
    throw new IllegalStateException("上传大小不匹配");
}
```

### 带失败中止的分片上传

```java
// 1. 初始化分片上传
CreateMultipartUploadRequest createRequest = CreateMultipartUploadRequest.builder()
    .bucket(bucketName)
    .key(key)
    .build();

CreateMultipartUploadResponse multipartUpload = s3Client.createMultipartUpload(createRequest);
String uploadId = multipartUpload.uploadId();

try {
    // 2. 上传部分
    List<CompletedPart> parts = new ArrayList<>();
    int partNumber = 1;
    byte[] fileBytes = Files.readAllBytes(Paths.get(filePath));
    int chunkSize = 5 * 1024 * 1024; // 5MB 最小

    for (int offset = 0; offset < fileBytes.length; offset += chunkSize) {
        int length = Math.min(chunkSize, fileBytes.length - offset);
        UploadPartRequest uploadPartRequest = UploadPartRequest.builder()
            .bucket(bucketName)
            .key(key)
            .uploadId(uploadId)
            .partNumber(partNumber)
            .build();

        UploadPartResponse partResponse = s3Client.uploadPart(uploadPartRequest,
            RequestBody.fromBytes(Arrays.copyOfRange(fileBytes, offset, offset + length)));

        parts.add(CompletedPart.builder()
            .partNumber(partNumber)
            .eTag(partResponse.eTag())
            .build());
        partNumber++;
    }

    // 3. 完成分片上传
    CompleteMultipartUploadRequest completeRequest = CompleteMultipartUploadRequest.builder()
        .bucket(bucketName)
        .key(key)
        .uploadId(uploadId)
        .multipartUpload(CompletedMultipartUpload.builder().parts(parts).build())
        .build();
    s3Client.completeMultipartUpload(completeRequest);

} catch (Exception e) {
    // 4. 失败时中止
    AbortMultipartUploadRequest abortRequest = AbortMultipartUploadRequest.builder()
        .bucket(bucketName)
        .key(key)
        .uploadId(uploadId)
        .build();
    s3Client.abortMultipartUpload(abortRequest);
    throw new RuntimeException("上传失败，已执行清理", e);
}
```

## 参考

- **[references/s3-client-setup.md](references/s3-client-setup.md)** — 客户端配置和基本操作
- **[references/s3-object-operations.md](references/s3-object-operations.md)** — 高级对象操作
- **[references/s3-transfer-patterns.md](references/s3-transfer-patterns.md)** — 传输管理器和分片上传
- **[references/s3-spring-boot-integration.md](references/s3-spring-boot-integration.md)** — Spring Boot 集成模式
- [AWS S3 开发者指南](https://docs.aws.amazon.com/AmazonS3/latest/userguide/)
- [AWS SDK for Java 2.x S3 API](https://sdk.amazonaws.com/java/api/latest/software/amazon/awssdk/services/s3/package-summary.html)

## 相关技能

- `aws-sdk-java-v2-core` - 核心AWS SDK模式和配置
- `spring-boot-dependency-injection` - Spring 依赖注入模式
