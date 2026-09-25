# ADK 代码参考

首先激活 `/google-agents-cli-workflow` 以进行所需的开发阶段和脚手架步骤。

## 1. 学习配方（无需项目）

**Python — 在回答“如何构建 X”之前，先阅读 `references/samples.md` 中的主题索引。**
现有的工作实现包括：沙盒化/按用户代码执行、可由代理加载的 `SKILL.md` 技能、跨会话内存、风险操作前的审批门禁、工具护栏、按用户凭证以及计划/事件驱动运行。

**Go — 阅读上游的 [`examples/`](https://github.com/google/adk-go/tree/main/examples)。**
克隆仓库并在实现它之前阅读与您需要的功能匹配的示例。

## 2. 编写代码的先决条件

在项目脚手架完成之前，请勿编写代理代码。

1. 验证项目：运行 `agents-cli info`（如果配置存在则继续）。
2. 新项目：运行 `agents-cli scaffold create <name>` — 为 Go 添加 `--agent adk_go`。
3. 现有代码：运行 `agents-cli scaffold enhance .`。

## 快速参考 — 最常见模式

有关 Python 和 Go 代码示例，请分别参阅 `references/adk-python.md` 和 `references/adk-go.md`。

---

## 参考

使用速查表进行常见模式。对于深入知识，请获取文档索引或检查已安装的包。

| 参考 | 语言 | 阅读时间 |
|------|------|-------------|
| `references/samples.md` | Python | **ADK 参考配方主题索引目录。** 在工作流第一阶段（在脚手架之前和编写代码之前）阅读 — 将功能映射到实现它的配方。 |
| `references/adk-python.md` | Python | 核心 ADK API：`Agent`、工具、回调、插件、状态、工件、多代理系统、`SequentialAgent` / `ParallelAgent` / `LoopAgent`、自定义 `BaseAgent`、`ManagedAgent`（服务器托管的本地代理）、A2A 协议、A2UI。大多数代理的默认设置。 |
| `references/adk-python-workflows.md` | Python | 基于图的 Workflow API（ADK Python 2.0）：节点、边、分支/汇合、HITL、并行处理。当您需要显式图拓扑时使用。 |
| `references/adk-go.md` | Go | 核心 ADK Go API：`llmagent`、工具、回调、插件、状态、工件、多代理系统、顺序/并行/循环代理、自定义代理、运行器、通过 HTTP 提供、A2A 协议和环境触发器。大多数代理的默认设置。 |
| `references/adk-go-workflows.md` | Go | 基于图的 Workflow API：节点、边、分支/汇合、HITL、并行处理。当您需要显式图拓扑时使用。 |
| [`examples/`](https://github.com/google/adk-go/tree/main/examples) | Go | 可运行的上游程序 — Go 的配方目录最接近的东西。 |
| `curl https://adk.dev/llms.txt` | Python | 文档索引（每页标题 + URL）。获取它，然后使用 `WebFetch` 获取特定页面，以获取速查表之外的内容。 |
| 已安装的 ADK 包 | Python | 精确的签名和符号 — 检查源代码（参见 `references/adk-python.md` 中的“检查 ADK 源代码”）。 |

## 相关技能

- `/google-agents-cli-workflow` — 开发工作流、编码规范和操作规则
- `/google-agents-cli-scaffold` — 使用 `agents-cli scaffold create` / `scaffold enhance` 创建和增强项目
- `/google-agents-cli-eval` — 评估方法、数据集模式以及 eval-fix 循环
- `/google-agents-cli-deploy` — 部署目标、CI/CD 管道和生产工作流
