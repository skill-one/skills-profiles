> 当此技能激活时，请不要在任何代码、注释或输出中使用表情符号。

# AWS SDK for JavaScript v3

## 包结构

- `@aws-sdk/client-*` — 每个服务一个，由 [smithy-typescript](https://github.com/awslabs/smithy-typescript) 生成；与 AWS 服务和操作一一对应
- `@aws-sdk/lib-*` — 更高级别的辅助工具（例如 `lib-dynamodb`, `lib-storage`）
- `@aws-sdk/*`（无前缀）— 工具包（主要为内部使用；不要导入深层路径）

始终从包根目录导入：

```js
import { S3Client } from "@aws-sdk/client-s3"; // 正确
// NOT: import { S3Client } from "@aws-sdk/client-s3/dist-cjs/S3Client"
```

## 两种客户端风格

**精简版**（推荐 — 更小的包）：

```js
import { S3Client, GetObjectCommand } from "@aws-sdk/client-s3";
const client = new S3Client({ region: "us-east-1" });
const output = await client.send(new GetObjectCommand({ Bucket: "b", Key: "k" }));
```

**聚合版**（v2风格的但不是v2，更大的包）：

```js
import { S3 } from "@aws-sdk/client-s3";
const client = new S3({ region: "us-east-1" });
const output = await client.getObject({ Bucket: "b", Key: "k" });
```

## 客户端配置

v3中没有全局配置 — 将配置传递给每个客户端。`region`始终是必需的；显式设置它或通过`AWS_REGION`环境变量设置。

```js
const config = { region: "us-east-1", maxAttempts: 5 };
const s3 = new S3Client(config);
const dynamo = new DynamoDBClient(config);
```

**实例化后不要读取或修改`client.config`** — 它是解析后的形式（例如`region`变成一个异步函数）。参见`references/effective-practices.md`。

对于HTTP处理器（来自`@smithy/node-http-handler`的`NodeHttpHandler`），重试策略、端点详情、日志记录、FIPS、双栈、协议选择和S3特定选项 → 参见`references/clients.md`。

## 凭证

所有来自`@aws-sdk/credential-providers`的提供程序。凭证是惰性的，并且每个客户端缓存，直到过期前约5分钟。

```js
// 默认链（环境 → ini → IMDS/ECS）— 在大多数Node.js应用程序中使用
const client = new S3Client({ credentials: fromNodeProviderChain() });

// 假设角色（注意：fromTemporaryCredentials对于STS AssumeRole是正确的）
const client = new S3Client({
  credentials: fromTemporaryCredentials({ params: { RoleArn: "arn:aws:iam::123456789012:role/MyRole" } }),
});

// 命名配置文件
const client = new S3Client({ profile: "my-profile" });
```

跨多区域客户端共享凭证和套接字池：

```js
const east = new S3Client({ region: "us-east-1" });
const { credentials, requestHandler } = east.config;
const west = new S3Client({ region: "us-west-2", credentials, requestHandler });
```

对于所有提供程序（Cognito、SSO、网络身份、自定义链、STS区域优先级）→ 参见`references/credentials.md`。

## 流（例如S3 GetObject Body）

**始终读取或丢弃流式响应** — 未读取的流会保留套接字打开（套接字耗尽）：

```js
const { Body } = await client.send(new GetObjectCommand({ Bucket: "b", Key: "k" }));
const str = await Body.transformToString();       // 读取为字符串
const bytes = await Body.transformToByteArray();  // 读取为Uint8Array
// 或丢弃：
await (Body.destroy?.() ?? Body.cancel?.());
```

流只能读取一次。

## 分页器

使用`paginate*`函数而不是手动处理令牌：

```js
import { DynamoDBClient, paginateListTables } from "@aws-sdk/client-dynamodb";

const client = new DynamoDBClient({});

const tableNames = [];
for await (const page of paginateListTables({ client }, {})) {
  // page包含一个单一的分页输出。
  tableNames.push(...page.TableNames);
}
```

## DynamoDB DocumentClient

使用`@aws-sdk/lib-dynamodb`以原生JS类型而不是AttributeValues工作：

```js
import { DynamoDBClient } from "@aws-sdk/client-dynamodb";
import { DynamoDBDocumentClient, GetCommand, PutCommand } from "@aws-sdk/lib-dynamodb";

const client = DynamoDBDocumentClient.from(new DynamoDBClient({}));
await client.send(new PutCommand({ TableName: "T", Item: { id: "1", name: "Alice" } }));
const { Item } = await client.send(new GetCommand({ TableName: "T", Key: { id: "1" } }));
```

对于序列化选项、大数字（NumberValue）、分页和聚合客户端 → 参见`references/dynamodb.md`。

## S3：预签名URL、分片上传、等待器

```js
// 预签名GET URL
import { getSignedUrl } from "@aws-sdk/s3-request-presigner";
const url = await getSignedUrl(client, new GetObjectCommand({ Bucket: "b", Key: "k" }), { expiresIn: 3600 });

// 分片上传（大文件 / 流）
import { Upload } from "@aws-sdk/lib-storage";
const upload = new Upload({ client, params: { Bucket: "b", Key: "k", Body: stream } });
await upload.done();

// 等待器
import { waitUntilObjectExists } from "@aws-sdk/client-s3";
await waitUntilObjectExists({ client, maxWaitTime: 120 }, { Bucket: "b", Key: "k" });
```

对于预签名POST、签名头和等待器选项 → 参见`references/s3.md`。

## 错误处理

```js
import { S3ServiceException } from "@aws-sdk/client-s3";

try {
  await client.send(new GetObjectCommand({ Bucket: "b", Key: "k" }));
} catch (e) {
  if (e?.$metadata) {
    // SDK服务错误 — 有$metadata.httpStatusCode, e.name, e.$response
    console.error(e.name, e.$metadata.httpStatusCode);
  }
}
```

检查`e.name`或`instanceof`以获取特定错误类型。参见`references/error-handling.md`以获取完整模式。

对于**运行时验证、序列化为非默认格式或有关jsv3中哪些模式**的问题 → 参见`references/schemas.md`。

## 性能：并行工作负载

```js
// 将maxSockets配置为与您的并行批处理大小匹配
const client = new S3Client({
  requestHandler: { httpsAgent: { maxSockets: 50 } },
  cacheMiddleware: true, // 如果使用自定义中间件则跳过
});
```

**流式死锁警告**：在有限的套接字下，不要分别`await`请求和流式主体 — 链接它们。参见`references/performance.md`。

## 中间件

向客户端上的所有命令添加自定义逻辑：

```js
client.middlewareStack.add(
  (next, context) => async (args) => {
    console.log(context.commandName, args.input);
    const result = await next(args);
    return result;
  },
  { name: "MyMiddleware", step: "build", override: true }
);
```

步骤（按顺序）：`initialize` → `serialize` → `build` → `finalizeRequest` → `deserialize`

## Abort Controller

```js
const { AbortController } = require("@aws-sdk/abort-controller");
const { S3Client, CreateBucketCommand } = require("@aws-sdk/client-s3");

const abortController = new AbortController();
const client = new S3Client(clientParams);

const requestPromise = client.send(new CreateBucketCommand(commandParams), {
  abortSignal: abortController.signal,
});

// 如果abortSignal已经中止，则不会创建请求。
// 如果在返回响应之前中止了abortSignal，则会销毁请求。
abortController.abort();

// 这将因abortSignal被中止而失败。
await requestPromise;
```

## Lambda最佳实践

在**处理器外部**初始化客户端（容器重用），在**处理器内部**进行API调用。对于一次性异步设置，在处理器内部使用一个惰性初始化标志：

```js
import { S3Client } from "@aws-sdk/client-s3";

const client = new S3Client({}); // 外部 — 跨调用重用

let ready = false;
export const handler = async (event) => {
  if (!ready) { await prepare(); ready = true; } // 处理器内部的惰性一次性设置
  // ... 这里进行API调用
};
```

参见`references/lambda.md`以获取Lambda层和版本控制。

## Node.js版本要求

- v3.968.0+ 需要 Node.js >= 20
- v3.723.0+ 需要 Node.js >= 18

## TypeScript

响应字段默认按`T | undefined`类型化。使用`@smithy/types`中的`AssertiveClient`来移除`| undefined`，或使用`NodeJsClient` / `BrowserClient`来缩小流式blob类型。参见`references/typescript.md`。

## SigV4a（S3多区域访问点）

S3 MRAP和某些其他功能需要SigV4a。您必须安装并侧效应导入以下之一：

- `@aws-sdk/signature-v4-crt` — 仅限Node.js，性能更好
- `@aws-sdk/signature-v4a` — Node.js + 浏览器，纯JS

```js
import "@aws-sdk/signature-v4a"; // 仅侧效应导入 — 不需要导出的值
```

参见`references/sigv4a.md`以获取完整细节和MRAP ARN格式。
