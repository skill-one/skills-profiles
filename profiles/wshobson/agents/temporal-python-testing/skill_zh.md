# 临时Python测试策略

使用pytest对Temporal工作流进行综合测试方法，以及针对特定测试场景的资源逐步披露。

## 使用此技能的场景

- **工作流单元测试** - 具有时间跳过的快速测试
- **集成测试** - 具有模拟活动的工作流
- **重放测试** - 验证与生产历史的确定性
- **本地开发** - 设置Temporal服务器和pytest
- **CI/CD集成** - 自动化测试流程
- **覆盖率策略** - 实现≥80%的测试覆盖率

## 测试理念

**推荐方法**（来源：docs.temporal.io/develop/python/testing-suite）：

- 大部分编写为集成测试
- 使用带有异步 fixtures 的 pytest
- 时间跳过可快速反馈（月长工作流→秒）
- 模拟活动以隔离工作流逻辑
- 使用重放测试验证确定性

**三种测试类型**：

1. **单元**：具有时间跳过的工作流，使用 ActivityEnvironment 的活动
2. **集成**：具有模拟活动的 Worker
3. **端到端**：具有真实活动的完整 Temporal服务器（谨慎使用）

## 可用资源

此技能通过逐步披露提供详细指导。根据您的测试需求加载特定资源：

### 单元测试资源

**文件**：`resources/unit-testing.md`
**加载时机**：独立测试单个工作流或活动
**包含内容**：

- 具有时间跳过的 WorkflowEnvironment
- 用于活动测试的 ActivityEnvironment
- 长工作流的快速执行
- 手动时间推进模式
- pytest fixtures 和模式

### 集成测试资源

**文件**：`resources/integration-testing.md`
**加载时机**：测试具有模拟外部依赖的工作流
**包含内容**：

- 活动模拟策略
- 错误注入模式
- 多活动工作流测试
- 信号和查询测试
- 覆盖率策略

### 重放测试资源

**文件**：`resources/replay-testing.md`
**加载时机**：验证确定性或部署工作流更改
**包含内容**：

- 确定性验证
- 生产历史重放
- CI/CD集成模式
- 版本兼容性测试

### 本地开发资源

**文件**：`resources/local-setup.md`
**加载时机**：设置开发环境
**包含内容**：

- Docker Compose配置
- pytest设置和配置
- 覆盖工具集成
- 开发工作流

## 快速入门指南

### 基本工作流测试

```python
import pytest
from temporalio.testing import WorkflowEnvironment
from temporalio.worker import Worker

@pytest.fixture
async def workflow_env():
    env = await WorkflowEnvironment.start_time_skipping()
    yield env
    await env.shutdown()

@pytest.mark.asyncio
async def test_workflow(workflow_env):
    async with Worker(
        workflow_env.client,
        task_queue="test-queue",
        workflows=[YourWorkflow],
        activities=[your_activity],
    ):
        result = await workflow_env.client.execute_workflow(
            YourWorkflow.run,
            args,
            id="test-wf-id",
            task_queue="test-queue",
        )
        assert result == expected
```

### 基本活动测试

```python
from temporalio.testing import ActivityEnvironment

async def test_activity():
    env = ActivityEnvironment()
    result = await env.run(your_activity, "test-input")
    assert result == expected_output
```

## 覆盖目标

**推荐覆盖率**（来源：docs.temporal.io最佳实践）：

- **工作流**：≥80%逻辑覆盖率
- **活动**：≥80%逻辑覆盖率
- **集成**：具有模拟活动的关键路径
- **重放**：部署前所有工作流版本

## 关键测试原则

1. **时间跳过** - 月长工作流秒级测试
2. **模拟活动** - 将工作流逻辑与外部依赖隔离
3. **重放测试** - 部署前验证确定性
4. **高覆盖率** - 生产工作流≥80%目标
5. **快速反馈** - 单元测试运行在毫秒级

## 如何使用资源

**按需加载特定资源**：

- "显示单元测试模式" → 加载`resources/unit-testing.md`
- "如何模拟活动?" → 加载`resources/integration-testing.md`
- "设置本地Temporal服务器" → 加载`resources/local-setup.md`
- "验证确定性" → 加载`resources/replay-testing.md`

## 其他参考

- Python SDK测试：docs.temporal.io/develop/python/testing-suite
- 测试模式：github.com/temporalio/temporal/blob/main/docs/development/testing.md
- Python示例：github.com/temporalio/samples-python
