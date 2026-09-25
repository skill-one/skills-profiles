# AWS Lambda Python 集成

创建高性能 AWS Lambda 函数的 Python 模式，具有优化的冷启动和干净的架构。

## 概述

AWS Lambda Python 集成采用两种方法：**AWS Chalice**（全功能框架）和**原始 Python**（最小开销）。两者都支持 API Gateway/ALB 集成，并提供生产就绪的配置。

## 何时使用

在以下情况下使用此技能：
- 创建新的 Python Lambda 函数
- 将现有的 Python 应用程序迁移到 Lambda
- 优化 Python Lambda 的冷启动性能
- 在基于框架和最小 Python 方法之间进行选择
- 配置 API Gateway 或 ALB 集成
- 设置 Python Lambda 的部署管道

## 说明

### 1. 选择您的方案

| 方案 | 冷启动 | 适用于 | 复杂性 |
|------|--------|--------|--------|
| AWS Chalice | < 200ms | REST API、快速开发、内置路由 | 低 |
| 原始 Python | < 100ms | 简单处理程序、最大控制、最小依赖项 | 低 |

### 2. 项目结构

#### AWS Chalice 结构
```
my-chalice-app/
├── app.py                    # 主应用程序与路由
├── requirements.txt          # 依赖项
├── .chalice/
│   ├── config.json          # Chalice 配置
│   └── deploy/              # 部署工件
├── chalicelib/              # 额外模块
│   ├── __init__.py
│   └── services.py
└── tests/
    └── test_app.py
```

#### 原始 Python 结构
```
my-lambda-function/
├── lambda_function.py       # 处理程序入口点
├── requirements.txt         # 依赖项
├── template.yaml            # SAM/CloudFormation 模板
└── src/                     # 额外模块
    ├── __init__.py
    ├── handlers.py
    └── utils.py
```

### 3. 实现示例

有关详细实现指南，请参阅[参考资料](#references)部分。快速示例：

**AWS Chalice:**
```python
from chalice import Chalice
app = Chalice(app_name='my-api')

@app.route('/')
def index():
    return {'message': 'Hello from Chalice!'}
```

**原始 Python:**
```python
def lambda_handler(event, context):
    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'Hello from Lambda!'})
    }
```

## 核心概念

### 冷启动优化

关键策略：

1. **模块级初始化** - 在热调用之间持久化
2. **使用懒加载** - 延迟重导入，直到需要时
3. **缓存 boto3 客户端** - 在调用之间重用连接

有关详细模式，请参阅[原始 Python Lambda](references/raw-python-lambda.md#cold-start-optimization)。

### 连接管理

在模块级别创建客户端并重用：

```python
_dynamodb = None

def get_table():
    global _dynamodb
    if _dynamodb is None:
        _dynamodb = boto3.resource('dynamodb').Table('my-table')
    return _dynamodb
```

### 环境配置

```python
class Config:
    TABLE_NAME = os.environ.get('TABLE_NAME')
    DEBUG = os.environ.get('DEBUG', 'false').lower() == 'true'

    @classmethod
    def validate(cls):
        if not cls.TABLE_NAME:
            raise ValueError("TABLE_NAME required")
```

## 最佳实践

### 内存和超时配置

- **内存**：对于简单处理程序，从 256MB 开始；对于复杂操作，从 512MB 开始
- **超时**：根据预期处理时间设置
  - 简单处理程序：3-5 秒
  - 具有数据库调用的 API：10-15 秒
  - 数据处理：30-60 秒

### 依赖项

保持 `requirements.txt` 最小：

```txt
# 核心AWS SDK - 总是需要的
boto3>=1.35.0

# 只添加您需要的
requests>=2.32.0  # 如果调用外部API
pydantic>=2.5.0   # 如果使用数据验证
```

### 错误处理

返回正确的 HTTP 代码和请求 ID：

```python
def lambda_handler(event, context):
    try:
        result = process_event(event)
        return {'statusCode': 200, 'body': json.dumps(result)}
    except ValueError as e:
        return {'statusCode': 400, 'body': json.dumps({'error': str(e)})}
    except Exception as e:
        print(f"Error: {str(e)}")  # 记录到 CloudWatch
        return {'statusCode': 500, 'body': json.dumps({'error': 'Internal error'})}
```

有关结构化错误模式，请参阅[原始 Python Lambda](references/raw-python-lambda.md#error-handling)。

### 日志记录

使用结构化日志记录以供 CloudWatch Insights：

```python
import logging, json
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# 结构化日志
logger.info(json.dumps({
    'eventType': 'REQUEST',
    'requestId': context.aws_request_id,
    'path': event.get('path')
}))
```

有关高级模式，请参阅[原始 Python Lambda](references/raw-python-lambda.md#logging)。

## 部署选项

### 快速入门

> **验证检查点**：在部署之前始终运行 `serverless print` 或 `sam validate` 以尽早捕获配置错误。

**Serverless Framework:**
```yaml
# serverless.yml
service: my-python-api
provider:
  name: aws
  runtime: python3.12  # 或 python3.11
functions:
  api:
    handler: lambda_function.lambda_handler
    events:
      - http:
          path: /{proxy+}
          method: ANY
```

**AWS SAM:**
```yaml
# template.yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31

Resources:
  ApiFunction:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: ./
      Handler: lambda_function.lambda_handler
      Runtime: python3.12  # 或 python3.11
      Events:
        ApiEvent:
          Type: Api
          Properties:
            Path: /{proxy+}
            Method: ANY
```

**AWS Chalice:**
```bash
chalice new-project my-api
cd my-api
chalice local 8080  # 在部署之前本地测试
chalice deploy --stage dev
```

> **验证检查点**：在部署到生产之前，使用 `chalice local` 或 `sam local invoke` 进行本地测试。

有关完整的部署配置，包括 CI/CD、特定环境的设置和高级 SAM/Serverless 模式，请参阅[Serverless 部署](references/serverless-deployment.md)。

## 限制和警告

### Lambda 限制

- **部署包**：解压缩后最大 250MB（压缩后 50MB）
- **内存**：128MB 到 10GB
- **超时**：最大 15 分钟
- **并发执行**：默认 1000（可调整）
- **环境变量**：总大小 4KB

### Python 特定注意事项

- **冷启动**：Python 具有出色的冷启动性能；避免在模块级别进行重导入
- **依赖项**：保持 `requirements.txt` 最小；使用 Lambda Layers 共享依赖项
- **本地依赖项**：必须在 Amazon Linux 2 上编译（x86_64 或 arm64）

### 常见陷阱

1. **在模块级别导入重库** - 如果不需要，延迟到函数级别
2. **不处理 Lambda 上下文** - 使用 `context.get_remaining_time_in_millis()` 意识到超时
3. **不验证输入** - 始终验证和清理事件数据
4. **打印敏感数据** - 小心日志和 CloudWatch

**错误恢复**：如果部署失败，请检查 CloudWatch 日志以查找初始化错误，并运行 `sam logs` 以诊断问题。

### 安全注意事项

- 不要硬编码凭证；使用 IAM 角色和环境变量
- 验证所有输入数据
- 使用最小权限 IAM 策略
- 启用 CloudTrail 进行审计日志记录

## 参考资料

有关特定主题的详细指南：

- **[AWS Chalice](references/chalice-lambda.md)** - 完整 Chalice 设置、路由、中间件、部署
- **[原始 Python Lambda](references/raw-python-lambda.md)** - 最小处理程序模式、模块缓存、打包
- **[Serverless 部署](references/serverless-deployment.md)** - Serverless Framework、SAM、CI/CD 管道
- **[测试 Lambda](references/testing-lambda.md)** - pytest、moto、SAM Local、localstack

## 示例

### 示例 1：创建 AWS Chalice REST API

**输入:**
```
使用 AWS Chalice 创建 Python Lambda REST API 用于待办事项应用程序
```

**处理:**
1. 使用 `chalice new-project` 初始化 Chalice 项目
2. 配置 CRUD 操作的路由
3. 设置 DynamoDB 集成
4. 配置部署阶段
5. 使用 `chalice deploy` 部署

**输出:**
- 完整的 Chalice 项目结构
- 具有 CRUD 端点的 REST API
- DynamoDB 表配置
- 部署配置

### 示例 2：优化原始 Python 的冷启动

**输入:**
```
我的 Python Lambda 冷启动缓慢，如何优化它？
```

**处理:**
1. 分析导入和初始化代码
2. 将重导入移到函数内部（懒加载）
3. 在模块级别缓存 boto3 客户端
4. 移除不必要的依赖项
5. 如有必要，使用预配置并发

**输出:**
- 使用懒加载的重构代码
- 优化冷启动 < 100ms
- 依赖项分析

### 示例 3：使用 GitHub Actions 部署

**输入:**
```
使用 SAM 配置 Python Lambda 的 CI/CD
```

**处理:**
1. 创建 GitHub Actions 工作流程
2. 设置 Python 环境和依赖项
3. 运行带有覆盖的 pytest
4. 使用 SAM 打包
5. 部署到 dev/prod 阶段

**输出:**
- 完整的 `.github/workflows/deploy.yml`
- 多阶段管道
- 集成测试自动化

## 版本

版本：1.0.0
