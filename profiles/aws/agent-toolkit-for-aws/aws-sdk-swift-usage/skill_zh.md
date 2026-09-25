# Swift AWS SDK

## 异步代码结构

所有 SDK 操作都是异步的。使用 `@main` 入口点：

```swift
@main
struct Main {
    static func main() async throws {
        let client = try await S3Client()
        // ... 异步操作
    }
}
```

## 重要提示：使用结构体配置类型

绝对不要使用 `S3ClientConfiguration` 或 `DynamoDBClientConfiguration` - 这些是已弃用的类。

始终使用基于结构体的配置类型：

- `S3Client.S3ClientConfig`（不是 S3ClientConfiguration）
- `DynamoDBClient.DynamoDBClientConfig`（不是 DynamoDBClientConfiguration）
- `STSClient.STSClientConfig`（不是 STSClientConfiguration）

配置参数必须按声明顺序排列。创建配置时，区域是始终必需的。检查服务客户端源代码以获取确切的顺序。

```swift
// 正确 - 结构体配置
let config = try await S3Client.S3ClientConfig(region: "us-west-2")
let client = S3Client(config: config)

// 错误 - 已弃用的类
// let config = try await S3Client.S3ClientConfiguration(region: "us-west-2")
```

## 客户端创建

所有服务客户端遵循相同的模式：`<服务>Client`，其中 `<服务>Client.<服务>ClientConfig`。

模型类型（用于请求/响应的结构体/枚举）位于 `<服务>ClientTypes` 命名空间下：

- `S3ClientTypes.Bucket`，`S3ClientTypes.Object`
- `DynamoDBClientTypes.AttributeValue`
- `CloudWatchClientTypes.MetricDatum`，`CloudWatchClientTypes.Dimension`

```swift
import AWSS3
import AWSDynamoDB

// 简单 - 自动检测区域
let s3 = try await S3Client()
let dynamo = try await DynamoDBClient()

// 指定区域
let s3 = try S3Client(region: "us-west-2")

// 使用配置 - 参数必须按声明顺序
let config = try await S3Client.S3ClientConfig(
    useFIPS: true,
    awsRetryMode: .adaptive,
    maxAttempts: 5,
    region: "us-west-2"
)
let client = S3Client(config: config)

// 使用自定义端点和凭证
let config = try await S3Client.S3ClientConfig(
    awsCredentialIdentityResolver: resolver,
    region: "us-west-2",
    endpoint: "https://s3.custom-endpoint.com"
)
```

常见配置参数（必须按声明顺序）：

- `awsCredentialIdentityResolver` - 自定义凭证
- `useFIPS` - 启用 FIPS 端点
- `useDualStack` - 启用双栈端点
- `awsRetryMode` - 重试策略（.adaptive，.standard，.legacy）
- `maxAttempts` - 最大重试次数
- `region` - AWS 区域
- `httpClientEngine` - 自定义 HTTP 客户端（需要 HttpClientConfiguration 参数）：

  ```swift
  import ClientRuntime
  let httpConfig = HttpClientConfiguration()
  let httpClient = URLSessionHTTPClient(httpClientConfiguration: httpConfig)
  let config = try await S3Client.S3ClientConfig(
      region: "us-east-1",
      httpClientEngine: httpClient
  )
  ```

- `endpoint` - 自定义端点 URL

对于特定服务的配置选项或确切的参数顺序，请检查 SDK 中的 `Sources/Services/AWS@Service/Sources/AWS@Service/\Service\Client.swift`。

## 凭证解析器

```swift
import AWSSDKIdentity
import SmithyIdentity

// 静态凭证 - 直接传递凭证对象
let creds = AWSCredentialIdentity(accessKey: "AKIA...", secret: "...")
let resolver = StaticAWSCredentialIdentityResolver(creds)

// 假设角色 - 需要底层解析器
let underlying = try DefaultAWSCredentialIdentityResolverChain()
let resolver = try STSAssumeRoleAWSCredentialIdentityResolver(
    awsCredentialIdentityResolver: underlying,
    roleArn: "arn:aws:iam::123456789012:role/MyRole",
    sessionName: "session-name"
)

// 在配置中使用
let config = try await S3Client.S3ClientConfig(
    awsCredentialIdentityResolver: resolver,
    region: "us-west-2"
)
```

## 等待器

导入 `SmithyWaitersAPI`。`WaiterOptions` 需要 `maxWaitTime` 参数：

```swift
import AWSS3
import SmithyWaitersAPI

let client = try await S3Client()
_ = try await client.waitUntilBucketExists(
    options: WaiterOptions(maxWaitTime: 120.0),
    input: HeadBucketInput(bucket: "my-bucket")
)
```

## 分页

```swift
let input = ListObjectsV2Input(bucket: "my-bucket")
for try await page in client.listObjectsV2Paginated(input: input) {
    for object in page.contents ?? [] {
        print(object.key ?? "")
    }
}
```

## 预签名 URL

```swift
let url = try await client.presignedURLForGetObject(
    input: GetObjectInput(bucket: "my-bucket", key: "file.pdf"),
    expiration: 3600
)
```

## 常见操作

```swift
// 上传对象
_ = try await client.putObject(input: PutObjectInput(
    body: .data(data),
    bucket: "bucket",
    key: "key"
))

// 获取对象
let output = try await client.getObject(input: GetObjectInput(bucket: "bucket", key: "key"))
let data = try await output.body?.readData()

// 列出存储桶
let response = try await client.listBuckets(input: ListBucketsInput())
for bucket in response.buckets ?? [] {
    print(bucket.name ?? "")
}
```
