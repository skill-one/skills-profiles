# AWS Lambda PHP 集成

使用 Bref 框架在 AWS Lambda 上部署 PHP 和 Symfony 应用的模式。

## 概述

有两种方法可用：
- **Bref 框架** - 标准 PHP 在 Lambda 上运行，支持 Symfony，内置路由，冷启动 < 2 秒
- **原始 PHP** - 最小开销，最大控制，冷启动 < 500 毫秒

两者都支持 API Gateway 集成，具有生产就绪的配置。

## 何时使用

- 创建新的 PHP Lambda 函数
- 将现有的 Symfony 应用迁移到 Lambda
- 优化冷启动性能
- 配置 API Gateway 或 SQS/SNS 事件触发器
- 设置 PHP Lambda 的部署管道

## 说明

### 1. 选择你的方法

| 方法 | 冷启动 | 适合 | 复杂度 |
|------|--------|------|--------|
| Bref | < 2 秒 | Symfony 应用，全功能 API | 中等 |
| 原始 PHP | < 500 毫秒 | 简单处理器，最大控制 | 低 |

### 2. 项目结构

#### 使用 Bref 的 Symfony 结构
```
my-symfony-lambda/
├── composer.json
├── serverless.yml
├── public/
│   └── index.php         # Lambda 入口点
├── src/
│   └── Kernel.php        # Symfony Kernel
├── config/
│   ├── bundles.php
│   ├── routes.yaml
│   └── services.yaml
└── templates/
```

#### 原始 PHP 结构
```
my-lambda-function/
├── public/
│   └── index.php         # 处理器入口点
├── composer.json
├── serverless.yml
└── src/
    └── Services/
```

### 3. 实现

**使用 Bref 的 Symfony:**
```php
// public/index.php
use Bref\Symfony\Bref;
use App\Kernel;
use Symfony\Component\HttpFoundation\Request;

require __DIR__.'/../vendor/autoload.php';

$kernel = new Kernel($_SERVER['APP_ENV'] ?? 'dev', $_SERVER['APP_DEBUG'] ?? true);
$kernel->boot();

$bref = new Bref($kernel);
return $bref->run($event, $context);
```

**原始 PHP 处理器:**
```php
// public/index.php
use function Bref\Lambda\main;

main(function ($event) {
    $path = $event['path'] ?? '/';
    $method = $event['httpMethod'] ?? 'GET';

    return [
        'statusCode' => 200,
        'body' => json_encode(['message' => 'Hello from PHP Lambda!'])
    ];
});
```

### 4. 冷启动优化

1. **延迟加载** - 直到需要时才加载重型服务
2. **禁用未使用的 Symfony 功能** - 关闭验证、注解
3. **优化 composer 自动加载** - 生产环境使用 classmap
4. **使用 Bref 优化运行时** - 利用 PHP 8.x 优化

### 5. 连接管理

```php
// 在函数级别缓存 AWS 客户端
use Aws\DynamoDb\DynamoDbClient;

class DatabaseService
{
    private static ?DynamoDbClient $client = null;

    public static function getClient(): DynamoDbClient
    {
        if (self::$client === null) {
            self::$client = new DynamoDbClient([
                'region' => getenv('AWS_REGION'),
                'version' => 'latest'
            ]);
        }
        return self::$client;
    }
}
```

## 最佳实践

### 内存和超时

- **内存**: Symfony 从 512MB 开始，原始 PHP 从 256MB 开始
- **超时**: Symfony 10-30 秒用于冷启动缓冲，原始 PHP 通常 3-10 秒足够

### 依赖项

```json
{
    "require": {
        "php": "^8.2",
        "bref/bref": "^2.0",
        "symfony/framework-bundle": "^6.0"
    },
    "config": {
        "optimize-autoloader": true,
        "preferred-install": "dist"
    }
}
```

### 错误处理

```php
try {
    $result = processRequest($event);
    return [
        'statusCode' => 200,
        'body' => json_encode($result)
    ];
} catch (ValidationException $e) {
    return [
        'statusCode' => 400,
        'body' => json_encode(['error' => $e->getMessage()])
    ];
} catch (Exception $e) {
    error_log($e->getMessage());
    return [
        'statusCode' => 500,
        'body' => json_encode(['error' => '内部错误'])
    ];
}
```

### 日志记录

```php
error_log(json_encode([
    'level' => 'info',
    'message' => 'Request processed',
    'request_id' => $context->getAwsRequestId(),
    'path' => $event['path'] ?? '/'
]));
```

## 部署

### Serverless 配置

```yaml
# serverless.yml
service: symfony-lambda-api

provider:
  name: aws
  runtime: php-82
  memorySize: 512
  timeout: 20

package:
  individually: true
  exclude:
    - '**/node_modules/**'
    - '**/.git/**'

functions:
  api:
    handler: public/index.php
    events:
      - http:
          path: /{proxy+}
          method: ANY
```

### 部署并验证

```bash
# 1. 安装 Bref
composer require bref/bref --dev

# 2. 本地测试（部署前验证）
sam local invoke -e event.json

# 3. 部署
vendor/bin/bref deploy

# 4. 验证部署
aws lambda invoke --function-name symfony-lambda-api-api \
  --payload '{"path": "/", "httpMethod": "GET"}' /dev/stdout
```

### Symfony 完整配置

```yaml
# serverless.yml for Symfony
service: symfony-lambda-api

provider:
  name: aws
  runtime: php-82
  stage: ${self:custom.stage}
  region: ${self:custom.region}
  environment:
    APP_ENV: ${self:custom.stage}
    APP_DEBUG: ${self:custom.isLocal}
  iam:
    role:
      statements:
        - Effect: Allow
          Action:
            - dynamodb:GetItem
            - dynamodb:PutItem
          Resource: '*'

functions:
  web:
    handler: public/index.php
    timeout: 30
    memorySize: 1024
    events:
      - http:
          path: /{proxy+}
          method: ANY

  console:
    handler: bin/console
    timeout: 300
    events:
      - schedule: rate(1 day)

plugins:
  - ./vendor/bref/bref

custom:
  stage: dev
  region: us-east-1
  isLocal: false
```

## 限制和警告

### Lambda 限制

- **部署包**: 解压后最大 250MB（压缩后 50MB）
- **内存**: 128MB 至 10GB
- **超时**: API Gateway 29 秒，异步 15 分钟
- **并发执行**: 默认 1000 个

### PHP 特定注意事项

- **冷启动**: PHP 冷启动适中；使用 Bref 优化运行时
- **依赖项**: 保持 composer.json 最小化；使用 Lambda Layers 共享依赖项
- **PHP 版本**: 使用 PHP 8.2+ 获取最佳 Lambda 性能
- **无本地存储**: Lambda 容器是短暂的；使用 S3/DynamoDB 进行持久化

### 常见陷阱

1. **大型 vendor 文件夹** - 排除开发依赖项；使用 --no-dev
2. **会话存储** - 不要使用本地文件存储；使用 DynamoDB
3. **长时间运行进程** - 不适合 Lambda；使用 ECS 代替
4. **Websockets** - 使用 API Gateway WebSockets 或 AppSync 代替

### 安全注意事项

- 不要硬编码凭证；使用 IAM 角色和 SSM 参数存储
- 验证所有输入数据
- 使用最小权限 IAM 策略
- 启用 CloudTrail 进行审计日志记录
- 设置适当的 CORS 标头

## 示例

### 示例 1：创建 Symfony Lambda API

**输入:** "使用 Bref 为待办事项应用程序创建 Symfony Lambda REST API"

**处理:**
1. 使用 `composer create-project` 初始化 Symfony 项目
2. 安装 Bref: `composer require bref/bref`
3. 配置 serverless.yml
4. 在 config/routes.yaml 中设置路由
5. **本地测试**: `sam local invoke`
6. **部署**: `vendor/bin/bref deploy`
7. **验证**: `aws lambda invoke --function-name <name> --payload '{}'`

**输出:** 完整的 Symfony 项目结构，包含 REST API、DynamoDB 集成、部署配置

### 示例 2：优化 Symfony 冷启动

**输入:** "我的 Symfony Lambda 冷启动时间为 5 秒，如何优化它？"

**处理:**
1. 分析启动时加载的服务
2. 禁用未使用的 Symfony 功能（验证、注解）
3. 使用延迟加载重型服务
4. 优化 composer 自动加载
5. **测量**: 部署并调用以验证冷启动 < 2 秒

**输出:** 优化的 Symfony 配置，冷启动 < 2 秒

### 示例 3：使用 GitHub Actions 部署

**输入:** "使用 Serverless Framework 配置 Symfony Lambda 的 CI/CD"

**处理:**
1. 创建 GitHub Actions 工作流程
2. 设置 PHP 环境和 composer
3. 运行 PHPUnit 测试
4. **部署** 使用 Serverless Framework
5. **验证**: 检查 Lambda 函数是否存在并响应

**输出:** 完整的 .github/workflows/deploy.yml，包含多阶段管道和测试自动化

## 参考

- **[Bref Lambda](references/bref-lambda.md)** - 完整 Bref 设置，Symfony 集成，路由
- **[原始 PHP Lambda](references/raw-php-lambda.md)** - 最小处理器模式，缓存，打包
- **[Serverless 部署](references/serverless-deployment.md)** - Serverless Framework，SAM，CI/CD 管道
- **[Lambda 测试](references/testing-lambda.md)** - PHPUnit，SAM Local，集成测试
