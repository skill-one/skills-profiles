# AWS Lambda 持久化函数

构建具有弹性的多步骤应用程序和 AI 工作流，这些函数可以执行长达 1 年，同时在遇到中断时仍能保持可靠的进度。

**最佳实践**是与 [AWS MCP 服务器](https://docs.aws.amazon.com/aws-mcp/) 配合使用，但不是必需的。此技能中的所有 AWS 交互都使用标准 AWS CLI 命令，这些命令在任何具有配置 AWS 凭据的环境中均可工作。

## 关键规则

在编写任何代码之前，请阅读这些内容。每一条都是一条约束，如果违反，函数将无声地失效。

1. **持久化执行必须在函数创建时启用——它不能进行后期改造。** 必须创建一个新的 Lambda 函数并将持久化执行打开。将逻辑迁移到新函数中；不要尝试在现有函数的处理器中安装 SDK 并将其包装起来，然后期望它能够工作。
2. **持久化函数必须使用限定 ARN 被调用**——一个特定的版本、一个别名或字面量 `$LATEST` 后缀。未限定的函数名称将失败。有关示例，请参阅下文中的 *调用要求* 部分。
3. **持久化操作不能嵌套。** 您不能在另一个步骤的回调中调用 `context.step()`、`context.wait()` 或 `context.invoke()`。相反，请使用 `context.runInChildContext()` 来分组操作。
4. **所有非确定性代码必须运行在步骤内。** `Date.now()`、`Math.random()`、UUID 生成、API 调用和步骤外的数据库查询将在重播时产生不同的值并损坏执行状态。
5. **闭包突变在重播时丢失** - 步骤返回值
6. **步骤外的副作用会重复** - 使用 `context.logger`（重播感知）

## 何时加载参考文件

根据用户正在处理的内容加载适当的参考文件：

- **入门指南**、**基本设置**、**示例**、**ESLint** 或 **Jest 设置** -> 查看 [getting-started.md](references/getting-started.md)
- **理解重播模型**、**确定性** 或 **非确定性错误** -> 查看 [replay-model-rules.md](references/replay-model-rules.md)
- **创建步骤**、**原子操作** 或 **重试逻辑** -> 查看 [step-operations.md](references/step-operations.md)
- **等待**、**延迟**、**回调**、**外部系统** 或 **轮询** -> 查看 [wait-operations.md](references/wait-operations.md)
- **并行执行**、**映射操作**、**批量处理** 或 **并发** -> 查看 [concurrent-operations.md](references/concurrent-operations.md)
- **错误处理**、**重试策略**、**Saga 模式** 或 **补偿事务** -> 查看 [error-handling.md](references/error-handling.md)
- **高级错误处理**、**超时处理**、**断路器** 或 **条件重试** -> 查看 [advanced-error-handling.md](references/advanced-error-handling.md)
- **测试**、**本地测试**、**云测试**、**测试运行器** 或 **不稳定测试** -> 查看 [testing-patterns.md](references/testing-patterns.md)
- **部署**、**CloudFormation**、**CDK**、**SAM**、**日志组**、**部署** 或 **基础设施** -> 查看 [deployment-iac.md](references/deployment-iac.md)
- **高级模式**、**GenAI 代理**、**完成策略**、**步骤语义** 或 **自定义序列化** -> 查看 [advanced-patterns.md](references/advanced-patterns.md)
- **故障排除**、**卡住执行**、**失败执行**、**调试执行 ID**、**执行历史记录**、**执行错误**、**我的执行为什么失败**、**执行超时**、**未收到回调**、**诊断执行** 或 **执行根本原因** -> 查看 [troubleshooting-executions.md](references/troubleshooting-executions.md)

## 快速参考

### 基本处理器模式

**TypeScript:**

```typescript
import { withDurableExecution, DurableContext } from '@aws/durable-execution-sdk-js';

export const handler = withDurableExecution(async (event, context: DurableContext) => {
  const result = await context.step('process', async () => processData(event));
  return result;
});
```

**Python:**

```python
from aws_durable_execution_sdk_python import durable_execution, DurableContext

@durable_execution
def handler(event: dict, context: DurableContext) -> dict:
    result = context.step(lambda _: process_data(event), name='process')
    return result
```

### Python API 差异

Python SDK 与 TypeScript 在以下几个方面有所不同：

- **步骤**：使用 `@durable_step` 装饰器 + `context.step(my_step(args))`，或内联 `context.step(lambda _: ..., name='...')`。建议使用装饰器以自动步骤命名。
- **等待**：`context.wait(duration=Duration.from_seconds(n), name='...')`
- **异常**：`ExecutionError`（永久）、`InvocationError`（临时）、`CallbackError`（回调失败）
- **测试**：直接使用 `DurableFunctionTestRunner` 类 - 使用处理器实例化，使用上下文管理器，调用 `run(input=...)`

### 调用要求

持久化函数 **必须使用限定 ARN**（版本、别名或 `$LATEST`）：

```bash
# 有效
aws lambda invoke --function-name my-function:1 output.json
aws lambda invoke --function-name my-function:live output.json

# 无效 - 将失败
aws lambda invoke --function-name my-function output.json
```

## IAM 权限

您的 Lambda 执行角色 **必须**附加 `AWSLambdaBasicDurableExecutionRolePolicy` 管理策略。这包括：

- `lambda:CheckpointDurableExecution` - 持久化执行状态
- `lambda:GetDurableExecutionState` - 检索执行状态
- CloudWatch 日志权限

**需要额外权限：**

- **持久化调用**：目标函数 ARN 上的 `lambda:InvokeFunction`
- **外部回调**：系统需要 `lambda:SendDurableExecutionCallbackSuccess` 和 `lambda:SendDurableExecutionCallbackFailure`

## 验证指南

在编写或审查持久化函数代码时，**始终**检查以下重播模型违规：

1. **步骤外的非确定性代码**：`Date.now()`、`Math.random()`、UUID 生成、API 调用、数据库查询必须都在步骤内
2. **步骤函数中的嵌套持久化操作**：不能在步骤函数内调用 `context.step()`、`context.wait()` 或 `context.invoke()` — 使用 `context.runInChildContext()` 代替
3. **不会持久化的闭包突变**：步骤内修改的变量不会在重播时保留 — 而是返回步骤的值
4. **步骤外重复的重播副作用**：使用 `context.logger` 进行日志记录（它是重播感知的，并会自动去重）

在实现或修改持久化函数的测试时，**始终**验证：

1. 所有操作都有描述性名称
2. 测试通过名称获取操作，而不是通过索引
3. 通过多次调用测试重播行为
4. 使用 `LocalDurableTestRunner` 进行本地测试

## 安全注意事项

- **检查点数据加密**：执行状态会自动持久化。在关联的 CloudWatch 日志组上启用 KMS 加密，以保护静态检查点数据。
- **步骤结果中的敏感数据**：步骤返回值会被检查点并持久化。不要从步骤中返回密钥、原始凭证或个人身份信息 (PII) — 将敏感数据存储在 Secrets Manager 或 SSM 参数存储中，并返回引用。
- **输入验证**：在将数据传递给步骤之前，在处理器入口点验证和清理事件有效负载。
- **凭证管理**：在步骤内从 AWS Secrets Manager 或 SSM 参数存储中检索密钥。
- **回调有效负载验证**：通过 `waitForCallback` 接收的数据来自外部系统 — 在处理之前验证和清理。
- **日志记录**：避免在非开发环境中使用 `DEBUG` 日志级别，因为它可能会暴露步骤结果和执行状态。使用 KMS 启用 CloudWatch 日志加密。

## 资源

- [AWS Lambda 持久化函数文档](https://docs.aws.amazon.com/lambda/latest/dg/durable-functions.html)
- [JavaScript SDK 仓库](https://github.com/aws/aws-durable-execution-sdk-js)
- [Python SDK 仓库](https://github.com/aws/aws-durable-execution-sdk-python)
- [IAM 策略参考](https://docs.aws.amazon.com/aws-managed-policy/latest/reference/AWSLambdaBasicDurableExecutionRolePolicy.html)
