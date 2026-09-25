# AWS CDK TypeScript

## 概述

使用此技能通过可重用的构建块、安全的默认值和以验证为先的交付循环，在 TypeScript 中构建 AWS 基础设施。

## 何时使用

在以下情况下使用此技能：

- 创建或重构 TypeScript 中的 CDK 应用程序、堆栈或可重用构建块
- 在 L1、L2 和 L3 构建块之间进行选择
- 构建无服务器、网络或安全为中心的 AWS 基础设施
- 连接多堆栈应用程序和环境感知部署
- 使用 `cdk synth`、测试、`cdk diff` 和 `cdk deploy` 验证基础设施更改

## 说明

### 1. 项目初始化

```bash
# 创建新的 CDK 应用程序
npx cdk init app --language typescript

# 项目结构
my-cdk-app/
├── bin/
│   └── my-cdk-app.ts          # 应用程序入口点（实例化堆栈）
├── lib/
│   └── my-cdk-app-stack.ts    # 堆栈定义
├── test/
│   └── my-cdk-app.test.ts     # 测试
├── cdk.json                    # CDK 配置
├── tsconfig.json
└── package.json
```

### 2. 核心架构

```typescript
import { App, Stack, StackProps, CfnOutput, RemovalPolicy } from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as s3 from 'aws-cdk-lib/aws-s3';

// 定义可重用的堆栈
class StorageStack extends Stack {
  public readonly bucketArn: string;

  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    const bucket = new s3.Bucket(this, 'DataBucket', {
      versioned: true,
      encryption: s3.BucketEncryption.S3_MANAGED,
      removalPolicy: RemovalPolicy.RETAIN,
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
    });

    this.bucketArn = bucket.bucketArn;
    new CfnOutput(this, 'BucketName', { value: bucket.bucketName });
  }
}

// 应用程序入口点
const app = new App();

new StorageStack(app, 'DevStorage', {
  env: { account: process.env.CDK_DEFAULT_ACCOUNT, region: 'us-east-1' },
  tags: { Environment: 'dev' },
});

new StorageStack(app, 'ProdStorage', {
  env: { account: '123456789012', region: 'eu-west-1' },
  tags: { Environment: 'prod' },
  terminationProtection: true,
});

app.synth();
```

### 3. 构建块级别

| 级别 | 描述 | 何时使用 |
|-------|-------------|----------|
| **L1** (`Cfn*`) | 直接 CloudFormation 映射，完全控制 | 需要未暴露的属性 |
| **L2** | 使用合理的默认值和辅助方法进行整理 | 标准资源配置（推荐） |
| **L3** (模式) | 多资源架构 | 常见模式，如 `LambdaRestApi` |

```typescript
// L1 — 原始 CloudFormation
new s3.CfnBucket(this, 'L1Bucket', { bucketName: 'my-l1-bucket' });

// L2 — 合理的默认值 + 授权辅助方法
const bucket = new s3.Bucket(this, 'L2Bucket', { versioned: true });
bucket.grantRead(myLambda);

// L3 — 多资源模式
new apigateway.LambdaRestApi(this, 'Api', { handler: myLambda });
```

### 4. CDK 生命周期命令

```bash
cdk synth          # 合成 CloudFormation 模板
cdk diff           # 比较已部署与本地更改
cdk deploy         # 将堆栈部署到 AWS
cdk deploy --all   # 部署所有堆栈
cdk destroy        # 删除堆栈
cdk ls             # 列出应用程序中的所有堆栈
cdk doctor         # 检查环境设置
```

### 5. 推荐的交付循环

1. **建模堆栈**
   - 从 L2 构建块开始，并将重复的逻辑提取到自定义构建块中。

2. **运行 `cdk synth`**
   - 检查点：合成成功，没有缺失的导入、无效的属性、缺失的上下文或未解决的引用。
   - 如果失败：修复构建块配置或上下文值，然后重新运行 `cdk synth`。

3. **运行基础设施测试**
   - 检查点：断言涵盖 IAM 范围、有状态资源和关键输出。
   - 如果测试失败：更新堆栈或测试预期，然后重新运行测试套件。

4. **运行 `cdk diff`**
   - 检查点：审查 IAM 扩展、资源替换、导出更改和有状态资源的删除。
   - 如果差异有风险：调整名称、依赖项或 `RemovalPolicy`，然后重新运行 `cdk diff`。

5. **运行 `cdk deploy`**
   - 检查点：堆栈达到 `CREATE_COMPLETE` 或 `UPDATE_COMPLETE`。
   - 如果部署失败：检查 CloudFormation 事件、修复配额、权限、导出冲突或引导问题，然后重试 `cdk deploy`。

6. **验证运行时结果**
   - 在继续之前确认堆栈输出、端点、警报和集成按预期工作。

### 6. 跨堆栈引用

```typescript
// 堆栈 A 导出一个值
class NetworkStack extends Stack {
  public readonly vpc: ec2.Vpc;
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);
    this.vpc = new ec2.Vpc(this, 'Vpc', { maxAzs: 2 });
  }
}

// 堆栈 B 通过属性导入它
interface AppStackProps extends StackProps {
  vpc: ec2.Vpc;
}
class AppStack extends Stack {
  constructor(scope: Construct, id: string, props: AppStackProps) {
    super(scope, id, props);
    new lambda.Function(this, 'Fn', {
      runtime: lambda.Runtime.NODEJS_20_X,
      handler: 'index.handler',
      code: lambda.Code.fromAsset('lambda'),
      vpc: props.vpc,
    });
  }
}

// 将它们连接起来
const network = new NetworkStack(app, 'Network');
new AppStack(app, 'App', { vpc: network.vpc });
```

## 示例

### 示例 1：无服务器 API

```typescript
import * as cdk from 'aws-cdk-lib';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as apigateway from 'aws-cdk-lib/aws-apigateway';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';

class ServerlessApiStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const table = new dynamodb.Table(this, 'Items', {
      partitionKey: { name: 'id', type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
    });

    const fn = new lambda.Function(this, 'Handler', {
      runtime: lambda.Runtime.NODEJS_20_X,
      handler: 'index.handler',
      code: lambda.Code.fromAsset('lambda'),
      environment: { TABLE_NAME: table.tableName },
    });

    table.grantReadWriteData(fn);

    new apigateway.LambdaRestApi(this, 'Api', { handler: fn });
  }
}
```

### 示例 2：CDK 断言测试

```typescript
import { Template } from 'aws-cdk-lib/assertions';
import { App } from 'aws-cdk-lib';
import { ServerlessApiStack } from '../lib/serverless-api-stack';

test('creates DynamoDB table with PAY_PER_REQUEST', () => {
  const app = new App();
  const stack = new ServerlessApiStack(app, 'TestStack');
  const template = Template.fromStack(stack);

  template.hasResourceProperties('AWS::DynamoDB::Table', {
    BillingMode: 'PAY_PER_REQUEST',
  });

  template.resourceCountIs('AWS::Lambda::Function', 1);
});
```

## 最佳实践

1. **每个堆栈一个关注点** — 分离网络、计算、存储和监控。
2. **优先使用 L2 构建块** — 只有在需要不受支持的属性时才降级到 `Cfn*`。
3. **设置明确的 环境** — 传递 `env` 包含账户和区域；避免隐式的生产目标。
4. **使用授权辅助方法** — 优先使用 `.grant*()` 而不是手写的 IAM。
5. **部署前审查差异** — 将 IAM 扩展、替换和删除视为强制性的检查点。
6. **测试基础设施** — 使用细粒度断言覆盖关键资源。
7. **避免硬编码值** — 使用上下文、参数或环境变量。
8. **使用正确的 `RemovalPolicy`** — `RETAIN` 用于生产数据，`DESTROY` 仅用于可丢弃的环境。

## 限制和警告

- **CloudFormation 限制** — 每个堆栈最多 500 个资源；将大型应用程序拆分为多个堆栈
- **合成不是部署** — `cdk synth` 仅生成模板；`cdk deploy` 应用更改
- **跨堆栈引用** 创建 CloudFormation 导出；移除它们需要仔细的顺序
- **有状态资源** (RDS、DynamoDB、带有数据的 S3) — 在生产中始终设置 `removalPolicy: RETAIN`
- **需要引导** — 在每个账户/区域运行一次 `cdk bootstrap`，在首次部署之前
- **资源捆绑** — Lambda 代码和 Docker 镜像上传到 CDK 引导堆栈

## 参考

在 `references/` 目录中提供详细的实现指南：

- [核心概念](references/core-concepts.md) — 应用程序生命周期、堆栈、构建块、环境、资源
- [无服务器模式](references/serverless-patterns.md) — Lambda、API Gateway、DynamoDB、S3 事件、Step Functions
- [网络 & VPC](references/networking-vpc.md) — VPC 设计、子网、NAT、安全组、VPC 端点
- [安全加固](references/security-hardening.md) — IAM、KMS、Secrets Manager、WAF、合规性
- [测试策略](references/testing-strategies.md) — 断言、快照、集成测试、CDK Nag
