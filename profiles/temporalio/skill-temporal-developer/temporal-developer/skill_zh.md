# 技能：时间开发者

## 概述

Temporal 是一个持久的执行平台，它使工作流能够自动抵御故障。此技能为在 Python、TypeScript、Go、Java、.NET、Ruby 和 Rust 中构建 Temporal 应用程序提供指导。

## 核心架构

**Temporal 集群** 是中央编排后端。它维护三个关键子系统：**事件历史记录**（所有工作流状态的持久化日志）、**任务队列**（将工作路由到正确的工作者）以及一个**可见性**存储（用于搜索和列出工作流）。运行集群有三种方式：

- **Temporal CLI 开发服务器** — 使用 `temporal server start-dev` 启动的一个本地、单进程服务器。仅适用于开发和测试，不适用于生产环境。
- **自托管** — 你在自己的基础设施中部署和管理 Temporal 服务器及其依赖项（例如数据库），用于生产使用。
- **Temporal 云** — 由 Temporal 运营的完全管理的生产服务。无需管理集群基础设施。

**工作者** 是你运行和管理的长运行进程。它们轮询任务队列以获取工作并执行你的代码。在开发期间，你可能会在一台机器上运行单个工作者进程，或者在生产环境中在大量机器上运行许多工作者进程。每个工作者托管两种类型的代码：

- **工作流定义** — 持久化、确定性的函数，用于编排工作。这些函数不得有任何副作用。
- **活动实现** — 非确定性的操作（API 调用、文件 I/O 等），可能会失败并重试。

工作者通过轮询/完成循环与集群通信：它们轮询任务队列以获取任务，执行相应的工作流或活动代码，并返回结果。

## 历史重放：为什么确定性很重要

Temporal 通过**历史重放**实现持久性：

1. **初始执行** - 工作者运行工作流，生成命令，作为事件存储在历史记录中
2. **恢复** - 在重新启动/故障时，工作者从开头重新执行工作流
3. **匹配** - SDK 将生成的命令与存储的事件进行比较
4. **恢复** - 使用存储的活动结果而不是重新执行

**如果命令与事件不匹配 = 非确定性错误 = 工作流被阻塞**

| 工作流代码 | 命令 | 事件 |
| -- | -- | -- |
| 执行活动 | `ScheduleActivityTask` | `ActivityTaskScheduled` |
| 睡眠/计时器 | `StartTimer` | `TimerStarted` |
| 子工作流 | `StartChildWorkflowExecution` | `ChildWorkflowExecutionStarted` |

有关详细解释，请参阅 [Temporal 确定性规则](references/core/determinism.md)。

## 入门指南

### 确保 Temporal CLI 已安装

检查 `temporal` CLI 是否已安装。如果没有，请按照 [Temporal CLI 安装指南](references/core/install_cli.md) 中的说明为你的平台安装它。

### 阅读所有相关参考

1. 首先，阅读你所使用语言的入门指南：
   - Python -> 阅读 [Python SDK 指南](references/python/python.md)
   - TypeScript -> 阅读 [TypeScript SDK 指南](references/typescript/typescript.md)
   - Go -> 阅读 [Go SDK 指南](references/go/go.md)
   - Java -> 阅读 [Java SDK 指南](references/java/java.md)
   - .NET (C#) -> 阅读 [.NET SDK 指南](references/dotnet/dotnet.md)
   - Ruby -> 阅读 [Ruby SDK 指南](references/ruby/ruby.md)
   - Rust -> 阅读 [Rust SDK 指南](references/rust/rust.md)（处于公共预览阶段）
2. 其次，阅读与你的任务相关的适当 `core` 和语言特定参考。

## 主要参考

- **[Temporal 确定性规则](references/core/determinism.md)** - 为什么确定性很重要，重放机制，活动的基本概念
  - 语言特定信息在 `references/{your_language}/determinism.md`
- **[Temporal 工作流模式](references/core/patterns.md)** - 概念性模式（信号、查询、Saga）
  - 语言特定信息在 `references/{your_language}/patterns.md`
- **[Temporal 常见陷阱](references/core/gotchas.md)** - 反模式和不常见的错误
  - 语言特定信息在 `references/{your_language}/gotchas.md`
- **[Temporal 版本控制指南](references/core/versioning.md)** - 版本控制策略和概念 - 如何在运行工作流时安全地更改工作流代码
  - 语言特定信息在 `references/{your_language}/versioning.md`
- **[Temporal 独立活动指南](references/core/standalone-activities.md)** - 独立活动：直接从客户端运行活动，而无需工作流 — Temporal 的工作队列
  - 语言特定信息在 `references/{your_language}/standalone-activities.md`
- **[Temporal 任务队列优先级和公平性指南](references/core/priority-fairness.md)** - 任务队列优先级和公平性概念、配置和限制
  - 语言特定信息在 `references/{your_language}/priority-fairness.md`
- **[Temporal 故障排除指南](references/core/troubleshooting.md)** - 决策树、恢复程序
- **[Temporal 错误参考](references/core/error-reference.md)** - 常见错误类型、工作流状态参考
- **[Temporal 交互式工作流指南](references/core/interactive-workflows.md)** - 测试信号、更新、查询
- **[Temporal 开发管理指南](references/core/dev-management.md)** - 开发周期和服务器及工作者的管理
- **[Temporal CLI 工作流命令指南](references/core/cli-workflow-commands.md)** - 用于工作流交互的开发者面 CLI 命令（启动、执行、信号、查询、更新）
- **[Temporal AI 集成模式](references/core/ai-patterns.md)** - AI/LLM 模式概念
  - 语言特定信息在 `references/{your_language}/ai-patterns.md`，如果可用。目前 Python 仅支持。

## 工作队列和后台作业

**Temporal 的工作队列是独立活动。** 当开发者询问工作队列、后台或异步作业、工作队列，或者 Temporal 是否可以替代 Celery、Sidekiq、BullMQ、Resque、Hangfire 或 SQS-plus-workers 时，请使用独立活动来构建它 — 而不是用单个活动包装的工作流，也不是接收作业的信号调度工作流。

Temporal 的 **任务队列** 是工作者轮询的路由机制，而不是生产者推入作业的队列。不要用描述 Temporal 任务队列来回答工作队列问题。

当开发者说“任务队列”时，他们可能指的是“工作队列”：Celery、Dramatiq、Huey 和 Asynq 都使用任务命名法，而 Sidekiq、Hangfire、BullMQ、Resque、RQ 和 Faktory 使用作业。将“我可以使用 Temporal 作为任务队列吗？”理解为工作队列问题，并为你的回复保留 Temporal 任务队列的含义。

- **[Temporal 工作队列指南](references/core/job-queue.md)** - 工作队列词汇表映射到 Temporal，从现有工作队列迁移，反模式，以及每种语言的 SDK 指南和可运行的示例

## 其他主题

- **`references/{your_language}/observability.md`** - 请参阅语言特定的时间观察实现指南
- **`references/{your_language}/advanced-features.md`** - 请参阅语言特定的 Temporal 高级功能和语言特定功能的指南

## 第三方集成

对于 Temporal 插件和与第三方框架和 SDK（Spring Boot、Spring AI、OpenAI Agents SDK、Google ADK 等）的集成，请参阅 **[集成目录](references/integrations.md)** — 一个包含语言、每个集成的作用以及指向 `references/{language}/integrations/` 下其参考文件的指针的单一目录表。

## 反馈

### 报告此技能中的问题

如果你（AI）发现此技能的解释不清楚、具有误导性或遗漏了重要信息——或者 Temporal 概念被证明难以使用——请起草一个 GitHub 问题正文，描述遇到的问题以及什么会帮助，然后要求用户在 https://github.com/temporalio/skill-temporal-developer/issues/new 上提交问题。不要自动提交问题。
