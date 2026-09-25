# AWS Lambda TypeScript 集成

创建高性能 AWS Lambda 函数的 TypeScript 模式，具有优化的冷启动。

## 概述

TypeScript Lambda 的两种方法：

1. **NestJS 框架** - 依赖注入、模块化架构、较大的包（100KB+）
2. **原始 TypeScript** - 最小开销、较小的包（<50KB）、最大控制

两者都支持 API Gateway 和 ALB 集成。

## 何时使用

- 创建 TypeScript 中的新 Lambda 函数
- 优化冷启动性能
- 在 NestJS 和最小 TypeScript 之间进行选择
- 配置 API Gateway 或 ALB 集成
- 为 TypeScript Lambda 设置 CI/CD

## 说明

### 1. 选择您的方案

| 方案 | 冷启动 | 包大小 | 适合 | 复杂性 |
|------|--------|--------|------|--------|
| NestJS | < 500ms | 较大（100KB+） | 复杂 API、企业应用、需要 DI | 中等 |
| 原始 TypeScript | < 100ms | 较小（< 50KB） | 简单处理程序、微服务、最小依赖 | 低 |

### 2. 项目结构

#### NestJS 结构
```
my-nestjs-lambda/
├── src/
│   ├── app.module.ts
│   ├── main.ts
│   ├── lambda.ts           # Lambda 入口点
│   └── modules/
│       └── api/
├── package.json
├── tsconfig.json
└── serverless.yml
```

#### 原始 TypeScript 结构
```
my-ts-lambda/
├── src/
│   ├── handlers/
│   │   └── api.handler.ts
│   ├── services/
│   └── utils/
├── dist/                   # 编译输出
├── package.json
├── tsconfig.json
└── template.yaml
```

### 3. 实现示例

有关详细实现指南，请参阅[参考资料](#references)部分。快速示例：

**NestJS 处理程序:**
```typescript
// lambda.ts
import { NestFactory } from '@nestjs/core';
import { ExpressAdapter } from '@nestjs/platform-express';
import serverlessExpress from '@codegenie/serverless-express';
import { Context, Handler } from 'aws-lambda';
import express from 'express';
import { AppModule } from './src/app.module';

let cachedServer: Handler;

async function bootstrap(): Promise<Handler> {
  const expressApp = express();
  const adapter = new ExpressAdapter(expressApp);
  const nestApp = await NestFactory.create(AppModule, adapter);
  await nestApp.init();
  return serverlessExpress({ app: expressApp });
}

export const handler: Handler = async (event: any, context: Context) => {
  if (!cachedServer) {
    cachedServer = await bootstrap();
  }
  return cachedServer(event, context);
};
```

**原始 TypeScript 处理程序:**
```typescript
// src/handlers/api.handler.ts
import { APIGatewayProxyEvent, APIGatewayProxyResult, Context } from 'aws-lambda';

export const handler = async (
  event: APIGatewayProxyEvent,
  context: Context
): Promise<APIGatewayProxyResult> => {
  return {
    statusCode: 200,
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message: 'Hello from TypeScript Lambda!' })
  };
};
```

## 核心概念

### 冷启动优化

TypeScript 冷启动取决于包大小和初始化代码。关键策略：

1. **懒加载** - 延迟加载重型导入，直到需要时
2. **树摇动** - 从包中删除未使用的代码
3. **最小化** - 使用 esbuild 或 terser 创建较小的包
4. **实例缓存** - 在调用之间缓存初始化的服务

有关详细模式，请参阅[原始 TypeScript Lambda](references/raw-typescript-lambda.md#cold-start-optimization)。

### 连接管理

在模块级别创建客户端并重用：

```typescript
// GOOD: 一次初始化，跨调用重用
import { DynamoDBClient } from '@aws-sdk/client-dynamodb';

const dynamoClient = new DynamoDBClient({ region: process.env.AWS_REGION });

export const handler = async (event: APIGatewayProxyEvent) => {
  // 使用 dynamoClient - 已经初始化
};
```

### 环境配置

```typescript
// src/config/env.config.ts
export const env = {
  region: process.env.AWS_REGION || 'us-east-1',
  tableName: process.env.TABLE_NAME || '',
  debug: process.env.DEBUG === 'true',
};

// 验证必需的变量
if (!env.tableName) {
  throw new Error('TABLE_NAME 环境变量是必需的');
}
```

## 最佳实践

### 内存和超时配置

- **内存**：对于 NestJS 开始使用 512MB，对于原始 TypeScript 使用 256MB
- **超时**：根据冷启动 + 预期处理时间设置
  - NestJS：冷启动缓冲 10-30 秒
  - 原始 TypeScript：通常足够 3-10 秒

### 依赖项

保持 `package.json` 最小：

```json
{
  "dependencies": {
    "aws-lambda": "^3.1.0",
    "@aws-sdk/client-dynamodb": "^3.450.0"
  },
  "devDependencies": {
    "typescript": "^5.3.0",
    "esbuild": "^0.19.0"
  }
}
```

### 错误处理

返回正确的 HTTP 代码和结构化错误：

```typescript
export const handler = async (event: APIGatewayProxyEvent): Promise<APIGatewayProxyResult> => {
  try {
    const result = await processEvent(event);
    return {
      statusCode: 200,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(result)
    };
  } catch (error) {
    console.error('处理请求时出错:', error);
    return {
      statusCode: 500,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ error: '服务器内部错误' })
    };
  }
};
```

### 日志记录

使用结构化日志记录 CloudWatch Insights：

```typescript
const log = (level: string, message: string, meta?: object) => {
  console.log(JSON.stringify({
    level,
    message,
    timestamp: new Date().toISOString(),
    ...meta
  }));
};

log('info', '请求已处理', { requestId: context.awsRequestId });
```

## 部署选项

### 快速入门

**Serverless Framework:**
```yaml
service: my-typescript-api

provider:
  name: aws
  runtime: nodejs20.x

functions:
  api:
    handler: dist/handler.handler
    events:
      - http:
          path: /{proxy+}
          method: ANY
```

**AWS SAM:**
```yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31

Resources:
  ApiFunction:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: dist/
      Handler: handler.handler
      Runtime: nodejs20.x
      Events:
        ApiEvent:
          Type: Api
          Properties:
            Path: /{proxy+}
            Method: ANY
```

### 部署验证

**预部署检查:**
1. 运行 `npm test` - 验证所有测试通过
2. 运行 `npm run build` - 确认 TypeScript 无错误编译
3. 验证包大小 < 50MB（未压缩）
4. 运行 `serverless invoke local` 或 `sam local invoke` - 本地测试

**部署后验证:**
1. 运行 `serverless invoke` 或 `aws lambda invoke` - 验证处理程序执行
2. 通过 curl 或 Postman 测试 API 端点
3. 检查 CloudWatch 日志中的错误
4. 验证冷启动时间满足 SLA

有关完整的部署配置，包括 CI/CD，请参阅[Serverless 部署](references/serverless-deployment.md)。

## 限制和警告

### Lambda 限制

- **部署包**：最大 250MB 未压缩（50MB 压缩）
- **内存**：128MB 至 10GB
- **超时**：最大 15 分钟
- **并发执行**：默认 1000（可调整）
- **环境变量**：总大小 4KB

### TypeScript 特定注意事项

- **包大小**：TypeScript 编译为 JavaScript；使用打包器最小化大小
- **冷启动**：Node.js 20.x 提供最佳性能
- **依赖项**：使用 Lambda Layers 共享依赖项
- **原生模块**：必须为 Amazon Linux 2 编译

### 常见陷阱

1. **在模块级别导入重型库** - 如果不需要，延迟加载
2. **未打包依赖项** - 将所有生产依赖项包含在包中
3. **缺少类型定义** - 安装 `@types/aws-lambda` 以进行正确的事件类型
4. **没有超时处理** - 使用 `context.getRemainingTimeInMillis()` 进行长时间操作

### 安全注意事项

- 不要硬编码凭证；使用 IAM 角色和环境变量
- **事件数据输入验证**：所有传入的事件数据（API Gateway 请求正文、S3 事件对象、SQS 消息正文）都是不受信任的外部内容；始终在处理之前验证和清理以防止注入攻击
- **内容清理**：在处理 S3 对象或 SQS 消息有效负载时，将内容视为不受信任的第三方数据；应用适当的验证、模式检查和清理，然后再采取行动
- 验证所有输入数据
- 使用最小权限 IAM 策略
- 启用 CloudTrail 进行审计日志记录
- 清理日志以避免泄露敏感数据

## 参考资料

有关特定主题的详细指南：

- **[NestJS Lambda](references/nestjs-lambda.md)** - 完整的 NestJS 设置、依赖注入、Express/Fastify 适配器
- **[原始 TypeScript Lambda](references/raw-typescript-lambda.md)** - 最小处理程序模式、打包、树摇动
- **[Serverless 配置](references/serverless-config.md)** - Serverless Framework 和 SAM 配置
- **[Serverless 部署](references/serverless-deployment.md)** - CI/CD 管道、环境管理
- **[测试](references/testing.md)** - Jest、集成测试、SAM Local

## 示例

### 示例 1：创建 NestJS REST API

**输入：** `使用 NestJS 为待办事项应用程序创建 TypeScript Lambda REST API`

**处理：**
1. 使用 `nest new` 初始化 NestJS 项目
2. 安装 Lambda 依赖项：`@codegenie/serverless-express`、`aws-lambda`
3. 创建 `lambda.ts` 入口点，使用 Express 适配器
4. 使用 `serverless.yml` 配置 API Gateway 事件
5. 使用 Serverless Framework 部署

**验证：**
- 运行 `serverless invoke local -f api` - 验证处理程序工作
- 检查包大小 < 250MB
- 测试部署的端点返回 200 OK

**输出：** NestJS 项目，包含 REST API、DynamoDB 集成、部署配置

### 示例 2：创建原始 TypeScript Lambda

**输入：** `创建具有最佳冷启动的原始 TypeScript Lambda 函数`

**处理：**
1. 使用 esbuild 设置 TypeScript 项目
2. 创建具有正确 AWS 类型的处理程序
3. 配置最小的依赖项
4. 使用 SAM 或 Serverless 部署
5. 使用树摇动优化包大小

**验证：**
- 运行 `sam local invoke` - 在部署前本地测试
- 使用 `du -sh dist/` 验证包 < 50KB
- 通过 CloudWatch 确认冷启动 < 100ms

**输出：** 最小 TypeScript Lambda，包 < 50KB，冷启动 < 100ms

### 示例 3：使用 GitHub Actions 部署

**输入：** `使用 SAM 为 TypeScript Lambda 配置 CI/CD`

**处理：**
1. 创建 GitHub Actions 工作流程
2. 设置 Node.js 环境
3. 使用 Jest 运行测试
4. 使用 esbuild 打包
5. 使用 SAM 部署

**验证：**
- 验证 CI 管道成功运行 `npm test`
- 确认管道中 `sam validate` 通过
- 检查 CloudFormation 堆栈创建成功

**输出：** GitHub Actions 工作流程，多阶段管道，测试自动化

## 版本

版本：1.0.0
