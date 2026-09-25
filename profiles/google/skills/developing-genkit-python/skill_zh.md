# Genkit Python

使用 Python 构建 AI 功能——生成、流式传输、工具、工作流和多轮代理——只需一个 SDK。

## 前置条件

- Python **3.10+** 和 **`uv`** ([安装](https://docs.astral.sh/uv/getting-started/installation/))
- Genkit CLI：如果缺少 `genkit --version`，请运行 `npm install -g genkit-cli`

新应用？[设置](references/setup.md)。模式？[示例](references/examples.md)。

## 欢迎世界

```python
from genkit import Genkit
from genkit_google_genai import GoogleAI

ai = Genkit(
    plugins=[GoogleAI()],
    model='googleai/gemini-flash-latest',
)

async def main():
    response = await ai.generate(prompt='给我讲一个关于 Python 的笑话。')
    print(response.text)

if __name__ == '__main__':
    ai.run_main(main())
```

## 代理（Beta）

具有历史记录、类型化状态、人工批准、分支和后台工作的多轮聊天。从这里开始：[代理](references/agents.md)。

```python
chat = agent.chat()
res = await chat.send('你好')           # AgentResponse
turn = chat.send_stream('你好')         # AgentTurn — .stream / .response
```

更多：[会话](references/agents-sessions.md) ·
[HITL](references/agents-human-in-the-loop.md) ·
[分支](references/agents-branching.md) ·
[后台](references/agents-background.md) ·
[状态](references/agents-state.md) ·
[工件](references/agents-artifacts.md) ·
[自定义](references/agents-custom.md) ·
[HTTP](references/agents-http.md)

## 导入

- Google AI：`from genkit_google_genai import GoogleAI`
- 代理：`from genkit.agent import InMemorySessionStore, ...`
- 中间件：`from genkit_middleware import Middleware, ToolApproval, ...`
- FastAPI：`from genkit_fastapi import serve_agent, serve_flow`
- 评估：`from genkit_evaluators import register_genkit_evaluators`

## 工作流

1. **代理还是工作流？** 如果任务是会话式的、多轮的，或者描述为“代理”、“助手”或“聊天机器人”，请使用 `ai.define_agent`（参见 [代理](references/agents.md)）来构建，而不是在流程中手动编写 `generate` + 工具循环。仅对于单次、无状态的生成，才使用纯流程。
2. 设置 **`GEMINI_API_KEY`**。使用前缀模型 ID（`googleai/gemini-flash-latest`）。
3. 通过 **`ai.run_main(main())`** 进入 Genkit 应用（尤其是在 `genkit start` 下）。参见 [常见错误](references/common-errors.md)。
4. 使用 [开发工作流](references/dev-workflow.md) (`genkit start` + 开发 UI) 运行。
5. 通过跟踪而不是盲目运行进行验证。直接运行应用 (`uv run`) **不会**捕获开发跟踪。参见 [Genkit CLI](#genkit-cli-recommended) 了解如何运行您的应用并捕获跟踪。
6. 卡住？首先查看 [常见错误](references/common-errors.md)。

## Genkit CLI（推荐）

`genkit start` 无干扰地包装任何使用 Genkit 库的 Python 程序，在运行它不变的同时捕获每个 Genkit 操作的跟踪，以便您可以在终端中证明工具实际上被调用并检查模型 I/O，即使对于无头检查也是如此。它转发 stdio，因此依赖 stdin/stdout 的交互式 CLI 工具可以正常工作而不会出现问题。直接运行应用 (`uv run`) 会跳过跟踪捕获，因此您是在盲目地调试。

**主要模式（默认）：** 在您的正常运行命令前缀 `genkit start --`。这将收集您的程序运行任何 Genkit 代码的遥测数据，无论是由开发 UI、您自己的 Web 服务器/Web UI 还是普通脚本触发：
```bash
genkit start -- uv run src/main.py
genkit start --noui -- uv run src/main.py   # 相同，但不显示开发 UI（仍然是一个持久服务器）
```
`genkit start` 运行，直到您使用 Ctrl+C 停止。这对于常见情况是预期和正确的：您的 Web/移动应用调用的服务器，或您自己退出的交互式 CLI。`--noui` 仅丢弃开发 UI；它**不是**一个一次性命令，并且不会自行退出。**不要**在自动化/非交互式环境中使用 `genkit start` 作为阻塞步骤；使用 `flow:run`（下方）来执行该操作。

**非交互式使用（代理/CI）：** 在 `--` 之前添加全局 `--non-interactive` 标志，以便 CLI 使用默认值并且永远不会在提示上阻塞（例如首次运行的分析通知）：`genkit start --non-interactive -- uv run src/main.py`（与 `flow:run` 也适用）。

**运行工作流 (`flow:run`)：** 从 CLI 中按名称调用特定工作流。在 `--` 后附加您的运行命令以仅为此运行启动运行时（命令按原样运行以注册您的工作流）：
```bash
genkit flow:run myFlow '{"data": "input"}' -- uv run src/main.py
```
这是**自终止的**：它运行一次工作流，打印一个 `Trace ID`，然后退出，因此它是快速、非交互式检查的正确选择（与 `genkit start` 不同）。注意：`flow:run` 运行**工作流**（`@ai.flow()`），而不是代理；您不能直接 `flow:run` 代理 (`ai.define_agent`)。要从 CLI 练习代理，请将一个回合包装在一个一次性工作流中并运行该工作流（参见 [代理](references/agents.md)）。

**使用跟踪进行调试：** 查看提示、模型输入/输出、工具调用、延迟和错误的最快方法。在 `genkit start` 下运行后从终端中检查：
```bash
genkit trace:list                        # 查找最近的跟踪 ID
genkit trace:get <traceId>               # 完整跟踪详细信息（输入、输出、工具调用、错误）
genkit trace:get <traceId> --format json # 机器可读的 JSON，可以安全地管道输入 `jq` 或其他解析器
```

对于机器可读的输出，传递 `--format json` 以获取干净的 JSON，您可以将其管道输入 `jq` 或其他解析器。**默认**输出是面向人类的（横幅/日志行，可能在大跟踪上截断），因此不要直接管道该形式；使用 `--format json`、grep 或开发 UI 跟踪查看器。

参见 [开发工作流](references/dev-workflow.md) 获取完整清单和开发 UI 漫游指南。

## 参考

- [示例](references/examples.md)：结构化输出、流式传输、工作流、工具、嵌入。
- [设置](references/setup.md)：新项目引导和插件。
- [常见错误](references/common-errors.md)：当出现问题时首先阅读。
- [FastAPI](references/fastapi.md)：HTTP、`genkit_fastapi_handler`、并行工作流。
- [Dotprompt](references/dotprompt.md)：`.prompt` 文件和辅助程序。
- [评估](references/evals.md)：评估器和数据集。
- [开发工作流](references/dev-workflow.md)：`genkit start`、开发 UI、清单。
- [代理（Beta）](references/agents.md)：多轮 API。
