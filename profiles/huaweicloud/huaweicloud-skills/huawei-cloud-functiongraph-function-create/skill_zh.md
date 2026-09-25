# 函数工作流函数创建技能

## 概述

该技能基于用户提供的参数（包括函数名称、运行时环境和代码内容）在华为云上创建函数工作流函数。

**架构**：使用华为云函数工作流 Python SDK 与函数工作流服务交互。

**适用场景**：

- 无需手动登录控制台快速创建云函数
- 批量创建多个函数
- 工作流部署的基础组件
- 函数部署的 CI/CD 集成

**典型用例**：

1. "创建名为 my_handler 的 Python 函数"
2. "将此代码部署到函数工作流"
3. "从模板批量创建 10 个函数"

## 前置条件

### 1. Python 环境

- Python 3.9+
- 验证：`python --version`

### 2. SDK 安装

```bash
pip install huaweicloudsdkfunctiongraph
```

### 3. 身份认证配置

- 有效的华为云凭证（AK/SK 模式）
- 通过环境变量配置：

```bash
export HUAWEI_AK="your-access-key"
export HUAWEI_SK="your-secret-key"
export HUAWEI_REGION="cn-north-4"
export HUAWEI_PROJECT_ID="your-project-id"
```

**安全规则**：

- **绝对不要**在代码或日志中暴露 AK/SK 值
- **绝对不要**让用户直接在对话中输入 AK/SK
- **始终**使用环境变量存储凭证
- **推荐**使用 IAM 用户而不是主账户

### 4. IAM 权限要求

- `functiongraph:function:create` - 创建函数
- `functiongraph:function:get` - 查询函数详情
- `functiongraph:function:list` - 列出函数

有关详细权限配置，请参阅 [IAM 策略](references/iam-policies.md)。

## 使用方法

### 命令

```bash
cd scripts
python create_function.py   --name <function_name>   --runtime <runtime>   --handler <handler>   --code <code_content>   --memory <memory_size>   --timeout <timeout>
```

## 参数确认

|| 参数 | 必填/可选 | 描述 | 默认值 ||
|| ----------- | ------------------ | ------------- | --------- ||
|| `function_name` | 必填 | 函数名称，必须符合命名规则 | - ||
|| `runtime` | 必填 | 运行时环境（Python3.9 等） | - ||
|| `code_content` | 必填 | 函数代码内容 | - ||
|| `handler` | 必填 | 函数入口点（例如，index.handler） | - ||
|| `memory_size` | 可选 | 内存大小（MB） | 128 ||
|| `timeout` | 可选 | 超时时间（秒） | 3 ||
|| `description` | 可选 | 函数描述 | - ||

### 运行时选项

|| 运行时 | 处理器格式 | 示例 ||
|| --------- | ---------------- | --------- ||
|| Python3.9 | index.handler | `def handler(event, context):` ||
|| Node.js14.18 | index.handler | `exports.handler = (event, context) => {}` ||
|| Java8 | com.example.Handler::handleRequest | Java 类方法 ||
|| Go1.x | handler | Go 函数名称 ||

## 验证方法

有关详细步骤，请参阅 [验证方法](references/verification-method.md)。

### 快速验证

```python
## 使用 SDK 验证函数是否存在

from huaweicloudsdkfunctiongraph.v2.functiongraph_client import FunctionGraphClient
from huaweicloudsdkfunctiongraph.v2.model import ListFunctionsRequest

# 列出函数以验证创建
client = FunctionGraphClient.new_builder().build()
request = ListFunctionsRequest()
response = client.list_functions(request)
print(f"总函数数量：{len(response.functions)}")
```

## 输出格式

该技能返回一个包含以下字段的 JSON 结构化对象：

- `function_urn`：创建的函数的唯一资源标识符
- `function_name`：创建的函数名称
- `runtime`：运行时环境
- `memory_size`：分配的内存（MB）
- `timeout`：函数超时时间（秒）
- `handler`：函数入口点
- `description`：函数描述（如果提供）

示例输出：

```json
{
  "function_urn": "urn:fss:cn-north-4:project_id:function:default:my_function",
  "function_name": "my_function",
  "runtime": "Python3.9",
  "memory_size": 128,
  "timeout": 3,
  "handler": "index.handler",
  "description": "由技能创建的测试函数"
}
```

## 最佳实践

1. **生产前测试**：始终先在开发环境中测试
2. **监控资源**：为函数调用和错误设置监控
3. **使用环境变量**：将敏感数据存储在环境变量中
4. **实现错误处理**：在函数代码中添加适当的错误处理
5. **设置合适的超时**：根据函数逻辑配置超时

## 错误处理

|| 错误代码 | 描述 | 解决方案 ||
|| ------------ | ------------- | ------------ ||
|| InvalidParameter | 无效的输入参数 | 检查参数格式和值 ||
|| InsufficientPermission | 权限不足 | 检查 IAM 权限 ||
|| QuotaExceeded | 资源配额超出 | 申请配额增加或删除未使用的函数 ||
|| FunctionAlreadyExists | 已存在同名函数 | 使用不同的函数名称或删除现有函数 ||

## 参考资料

- [函数工作流文档](https://support.huaweicloud.com/functiongraph/)
- [Python SDK 文档](https://github.com/huaweicloud/huaweicloud-sdk-python-v3)
- [IAM 策略指南](references/iam-policies.md)
- [验证方法](references/verification-method.md)
