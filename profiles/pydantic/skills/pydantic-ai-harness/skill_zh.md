# 使用 Pydantic AI 托管构建

Pydantic AI 托管是 Pydantic AI 的官方能力库。需要模型或框架支持的能力——以及每个代理都必不可少的基础能力——都存在于核心 `pydantic-ai` 中；而可选的、包含所有功能的特性则生活在这里。两者都通过相同的 `capabilities=[...]` API 组合到代理上。

本技能涵盖了 `pydantic-ai-harness` 发行的能力。对于核心框架——代理、工具、结构化输出、钩子和测试——请使用 `building-pydantic-ai-agents` 技能。

## 何时使用此技能

在以下情况下调用此技能：
- 用户提到 `pydantic-ai-harness`、`CodeMode`、代码模式或 Monty 沙盒
- 代理执行许多顺序工具调用，这些调用可以合并为一个沙盒化的 Python 执行
- 用户希望模型编写 Python 代码来循环、分支、聚合或使用 `asyncio.gather` 并行化工具调用
- 用户要求沙盒化或限制代理运行的代码

**不要**使用此技能用于：
- 核心Pydantic AI使用——构建代理、添加工具、结构化输出、流式传输或测试（使用 `building-pydantic-ai-agents`）
- 核心在 `pydantic-ai` 中发布的能力，如网络搜索、工具搜索和思考
- 仅 Pydantic 验证库（`pydantic`/`BaseModel` 而没有代理）

## 支持的能力

`CodeMode` 下方有完整的参考；它是旗舰能力，也是本技能深入探讨的对象。其余能力今天就会发布，每个能力都有自己的 README，包含 API 和示例。

每个能力都位于自己的子模块中，并从那里导入（`from pydantic_ai_harness.<module> import ...`）。按设计，能力不能从顶层 `pydantic_ai_harness` 包中导入，因此每个能力都保持其可选依赖项的隔离。`CodeMode`、`FileSystem`、`Shell` 和 `ManagedPrompt` 也有顶层的重新导出（可以直接从 `pydantic_ai_harness` 导入）。

API 在版本之间可能会发生变化；在实用的情况下，破坏性变更会发布弃用警告。

| 能力 | 模块 | 描述 |
|---|---|---|
| `CodeMode` | `pydantic_ai_harness.code_mode`（也位于顶层） | 将符合条件的工具包装为单个沙盒化的 `run_code` 工具，以便模型用 Python 协调它们——参见 [代码模式](./references/CODE-MODE.md) |
| `FileSystem` | `pydantic_ai_harness.filesystem`（也位于顶层） | 在根目录下读取、写入、编辑和搜索文件，并防止遍历 |
| `Shell` | `pydantic_ai_harness.shell`（也位于顶层） | 在子进程中运行命令，具有允许列表、默认拒绝列表、超时和环境掩码 |
| `ManagedPrompt` | `pydantic_ai_harness.logfire`（也位于顶层） | 使用 Logfire 管理的提示支持代理的指令 |
| `SubAgents` | `pydantic_ai_harness.subagents` | 将子任务委托给专门的子代理 |
| `DynamicWorkflow` | `pydantic_ai_harness.dynamic_workflow` | 从模型编写的 Python 脚本中编排子代理 |
| `Planning` | `pydantic_ai_harness.planning` | 在执行前将复杂任务分解为结构化计划 |
| 压缩系列（`SlidingWindowCompaction`、`SummarizingCompaction`、...） | `pydantic_ai_harness.compaction` | 剪辑或总结对话历史以保持在令牌限制内 |
| `ToolOutputLimits` | `pydantic_ai_harness.tool_output_limits` | 截断、总结或溢出大型工具输出 |
| `RepoContext` | `pydantic_ai_harness.repo_context` | 自动加载 CLAUDE.md/AGENTS.md 和仓库结构 |
| `StepPersistence` | `pydantic_ai_harness.step_persistence` | 保存、恢复、继续和分支运行状态 |
| `PydanticAIDocs` | `pydantic_ai_harness.pydantic_ai_docs` | 用于 Pydantic AI 文档的按需 `read_pyai_docs` 工具 |
| `CapabilityCreation` | `pydantic_ai_harness.capability_creation` | 允许代理在运行时编写、验证和加载真实能力 |
| 媒体外部化 | `pydantic_ai_harness.media` | 将大型 `BinaryContent` 外部化到内容寻址存储 |

仍在实验中：ACP 服务器适配器，从 `pydantic_ai_harness.experimental.acp` 导入。导入它会发出 `HarnessExperimentalWarning`。

完整的当前列表，包含链接和状态，在
[能力矩阵](https://github.com/pydantic/pydantic-ai-harness#capability-matrix) 中。

## 安装

```bash
uv add pydantic-ai-harness
```

每个能力声明自己的额外。代码模式需要 Monty 沙盒：

```bash
uv add "pydantic-ai-harness[codemode]"   # `code-mode` 也作为别名接受
```

需要 Python 3.10+ 和 `pydantic-ai-slim>=2.18.0`。

## 快速入门

像任何其他能力一样，将托管能力添加到代理。这里 `CodeMode` 将本地注册的工具包装为单个 `run_code` 工具，模型用 Python 驱动它。

```python {test="skip"}
from pydantic_ai import Agent

from pydantic_ai_harness import CodeMode

agent = Agent('anthropic:claude-sonnet-4-6', capabilities=[CodeMode()])


@agent.tool_plain
def get_temperature_f(city: str) -> float:
    return {'Paris': 68.0, 'Tokyo': 77.0}[city]


@agent.tool_plain
def convert_temp(fahrenheit: float) -> float:
    return round((fahrenheit - 32) * 5 / 9, 1)

result = agent.run_sync(
    '比较巴黎和东京的天气，并报告两种温度的摄氏度。'
)
print(result.output)
#> 巴黎是 20.0 C，东京是 25.0 C。
```

模型编写单个 Python 脚本，使用 `asyncio.gather` 获取两个温度，然后进行转换——在一个 `run_code` 调用中执行四个工具调用，跨越两个依赖阶段。

## 关键实践

- **确认实际需要托管能力。** 如果核心 Pydantic AI 工具和能力就足够，请使用 `building-pydantic-ai-agents` 技能——不要默认使用托管。
- **在编写代码前阅读参考。** 每个能力都有自己的配置、限制和注意事项——首先加载链接的参考（例如 [代码模式](./references/CODE-MODE.md)）。
- **安装能力的额外部分。** 没有 `pydantic-ai-harness[codemode]` 导入 `CodeMode` 会引发 `ImportError`；Monty 沙盒是一个可选依赖项。

## 常见陷阱

- **`native=True` 工具绕过 `CodeMode`。** 提供商原生 MCP 服务器和网络搜索在服务器端执行，因此 `run_code` 从不看到它们。使用 `native=False` 进行客户端调度，`CodeMode` 可以包装，但不要将远程服务器视为可信或沙盒化；参见 [代码模式的信任边界](./references/CODE-MODE.md#sandbox-restrictions)。
- **Monty 沙盒是 Python 的子集。** 它没有第三方导入，并且只有一个小型 stdlib 允许列表——在调试生成的失败代码之前，请阅读 [代码模式](./references/CODE-MODE.md#sandbox-restrictions)。
- **`CodeMode` 需要它的额外部分。** 安装 `pydantic-ai-harness[codemode]`，而不是裸包。
