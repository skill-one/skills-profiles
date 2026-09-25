> 当此技能启用时，不要在任何代码、注释或输出中使用表情符号。

# AWS SDK for Python (boto3)

boto3 是 AWS 的高级 Python SDK。它封装了 botocore（低级 SDK），并提供了两个不同的接口：**客户端**（低级，1:1 API 映射）和 **资源**（高级，面向对象）。了解何时以及如何使用它们至关重要。

## 客户端与资源

**客户端**直接映射到 AWS 服务 API。每个服务都有一个客户端。响应是普通的字典。

**资源**提供面向对象的接口，具有属性和操作。只有某些服务有资源（S3、DynamoDB、EC2、IAM、SQS、SNS、CloudFormation、CloudWatch、Glacier）。资源自动封装类型（特别是对 DynamoDB 很有用）。

```python
import boto3

# 客户端 - 低级，所有服务
s3_client = boto3.client("s3")
response = s3_client.list_buckets()
buckets = response["Buckets"]  # 普通字典

# 资源 - 高级，选择服务
s3_resource = boto3.resource("s3")
for bucket in s3_resource.buckets.all():
    print(bucket.name)  # 属性访问，不是字典键
```

当您需要完整的 API 覆盖或服务没有资源接口时，使用客户端。当它们存在并且可以简化您的代码时使用资源（尤其是 DynamoDB 和 S3）。

## 会话和客户端创建

```python
import boto3

# 默认会话隐式创建
client = boto3.client("s3")
resource = boto3.resource("dynamodb")

# 当您需要自定义客户端创建方式、使用显式配置文件等时，显式使用会话
session = boto3.Session(
    profile_name="my-profile",
    region_name="us-west-2",
)
client = session.client("s3")
```

不要在循环中创建客户端 - 重用单个客户端实例。客户端是线程安全的，一旦实例化，就可以跨线程共享。

## 调用 API

```python
# 客户端 - 将参数作为关键字参数传递，返回字典
response = client.get_object(Bucket="my-bucket", Key="my-key")
data = response["Body"].read()

# 资源 - 使用对象方法和属性
obj = s3_resource.Object("my-bucket", "my-key")
response = obj.get()
data = response["Body"].read()
```

参数名称与 AWS API 的确切大小写匹配，通常是帕斯卡大小写，而不是蛇形大小写。

## 错误处理

只有在您有可执行的操作时才捕获异常 - 返回备用值、重试、采取不同的代码路径。只是为了打印并吞掉异常是错误的：它隐藏了真实错误，并阻止调用者做出反应。默认情况下让异常传播。

当您确实捕获时，请优先在客户端上使用类型化的异常，而不是通用的 `ClientError`，通过 `client.exceptions` 属性匹配字符串代码：

```python
lambda_client = boto3.client("lambda")

def get_function_config(name: str) -> dict | None:
    """返回函数配置，如果不存在则返回 None。"""
    try:
        return lambda_client.get_function_configuration(FunctionName=name)
    except lambda_client.exceptions.ResourceNotFoundException:
        return None  # 可执行操作：将缺失的函数转换为 None
    # 其他所有内容传播 - 调用者或 main() 处理
```

仅在顶层错误处理程序中作为捕获所有内容的通用 `ClientError`，而不是在业务逻辑函数中使用。它位于 botocore 中，而不是 boto3：

```python
from botocore.exceptions import ClientError

def main() -> int:
    try:
        result = do_the_work()
        print(result)
        return 0
    except ClientError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
```

有关完整的错误层次结构和 botocore 异常，请参阅 `references/error-handling.md`。

## 脚本结构

当被要求编写使用 `boto3` 或 `botocore` 的脚本时，将 `if __name__ == "__main__"` 保留为单个函数调用。参数解析、错误呈现和退出代码应属于 `main()`，而不是分散在业务逻辑函数中：

```python
def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("bucket")
    args = parser.parse_args()

    try:
        do_the_work(args.bucket)
        return 0
    except ClientError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
```

永远不要从业务逻辑函数中调用 `sys.exit()`——它使函数无法测试且无法作为库使用。相反，请引发异常或返回错误值，让 `main()` 决定如何呈现。

## 分页

永远不要手动使用 `NextToken` 循环——使用分页器。当您只需要特定字段时，使用 `.search()` 并使用 JMESPath 表达式提取并展平跨页面：

```python
paginator = iam.get_paginator("list_users")
for name in paginator.paginate().search("Users[].UserName"):
    print(name)

# 过滤和投影
for arn in paginator.paginate().search("Users[?Path == '/admin/'][].Arn"):
    print(arn)
```

当您需要每个项目的完整响应对象，或者需要每页控制（例如，计数页数、按页分批）时，直接迭代页面：

```python
for page in paginator.paginate():
    for user in page.get("Users", []):
        process(user)
```

有关分页的更多详细信息，请参阅：`references/pagination.md`。

## 等待器

等待资源达到期望状态：

```python
waiter = client.get_waiter("bucket_exists")
waiter.wait(
    Bucket="my-bucket",
    WaiterConfig={"Delay": 5, "MaxAttempts": 20},
)
```

有关等待器的更多详细信息，请参阅 `references/waiters.md`。

## 客户端配置

使用 `botocore.config.Config` 进行重试、超时和连接池设置等：

```python
from botocore.config import Config

config = Config(
    retries={"total_max_attempts": 2, "mode": "adaptive"},
    connect_timeout=5,
    read_timeout=10,
    max_pool_connections=50,
)
client = boto3.client("s3", config=config)
```

当为客户端创建自定义配置时，请参阅 `references/configuration.md`。

## 日志记录

boto3 和 botocore 都使用标准库 `logging` 模块。您可以通过标准的 `logging` API 配置日志记录，或者您可以使用 boto3 和 botocore 提供的辅助程序以方便的方式使用：

```python
# 快速：将所有 botocore 线路级详细信息记录到 stderr
boto3.set_stream_logger("")  # 根日志——所有内容
boto3.set_stream_logger("botocore")  # 仅 botocore

# Botocore，记录所有 botocore 详细信息
import logging

from botocore.session import Session

session = Session()

session.set_stream_logger('botocore', logging.DEBUG)
# 或者：将日志配置到文件。
session.set_file_logger(logging.DEBUG, '/tmp/botocore.log')
```

`set_stream_logger(name, level=logging.DEBUG)` 为命名日志器添加一个 `StreamHandler`。这是从 SDK 获取请求/响应调试输出的惯用方式。

## 常见问题

### 问题：ClientError 导入位置

**错误：** `from boto3.exceptions import ClientError`
**正确：** `from botocore.exceptions import ClientError`

## 服务特定自定义

当编写使用以下服务的任何 Python 代码时，您必须加载这些附加参考文件以遵循最佳实践和自定义高级 API：

* S3 - 您必须加载 `references/s3.md`。
* Dynamoodb - 您必须加载 `references/dynamodb.md`。

## 参考

* 客户端配置（重试、超时、端点）：`references/configuration.md`
* 凭据和会话：`references/credentials.md`
* 错误处理模式：`references/error-handling.md`
* 分页：`references/pagination.md`
* 等待器：`references/waiters.md`
* S3 转移和预签名 URL：`references/s3.md`
* DynamoDB 操作：`references/dynamodb.md`
