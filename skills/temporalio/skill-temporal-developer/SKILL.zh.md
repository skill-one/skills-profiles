---
name: temporal-developer
description: 在 Python、TypeScript、Go、Java、.NET、Ruby 和 Rust 等语言中开发、调试和管理 Temporal 应用。当用户使用 Temporal SDK 构建 workflows、activities、workers 或后台任务队列，使用 Temporal CLI、Temporal Server 或 Temporal Cloud 调试非确定性错误、卡住的工作流或活动重试等问题，或处理信号、查询、心跳、版本控制、继续为新的、子工作流或 saga 模式等持久执行概念时，请使用。此外，当用户提到“从 CLI 运行 Temporal 工作流”、“启动开发服务器”、“运行 temporal server start-dev”、“temporal workflow start”、“temporal workflow execute”、“temporal workflow signal”、“temporal workflow query”、“temporal workflow update”时，也请使用。
---

# 技能：temporal-developer

## 概述

Temporal 是一个持久的执行平台，能够自动让工作流在发生故障时继续运行。此技能为在 Python、TypeScript、Go、Java、.NET、Ruby 和 Rust 中构建 Temporal 应用程序提供指导。

## 不在范围内

- **操作 CLI 命令**，例如批量操作、健康查询、云管理、`tcld` 和脚本 → 使用 [temporal-ops 技能](https://github.com/temporalio/skill-temporal-ops)。
- **无服务器工作者的部署和故障排除** → 使用 [temporal-serverless 技能](https://github.com/temporalio/skill-temporal-serverless)。
- **首次 Temporal Cloud 设置**，包括命名空间、API 密钥、示例应用程序和第一个工作流 → 使用 [temporal-cloud-setup 技能](https://github.com/temporalio/skill-temporal-cloud-setup)。

如果一个任务转移到这些领域之一，请遵循相关技能。本地开发和面向开发者的工作流 CLI 命令仍然在此处涵盖。

## 核心架构

**Temporal 集群** 是中央编排后端。它维护三个关键子系统：**事件历史记录**（所有工作流状态的持久化日志）、**任务队列**（将工作路由到正确的工作者）以及一个 **可见性** 存储库（用于搜索和列出工作流）。运行集群有三种方式：

- **Temporal CLI 开发服务器** — 一个本地、单进程服务器，通过 `temporal server start-dev` 启动。仅适用于开发和测试，不适用于生产。
- **自托管** — 你在自己的基础设施中部署和管理 Temporal 服务器及其依赖项（例如数据库），用于生产使用。
- **Temporal Cloud** — 由 Temporal 运营的完全管理的生产服务。无需管理集群基础设施。

**工作者** 是长时间运行的过程，你可以运行和管理它们。它们轮询任务队列以获取工作并执行你的代码。在开发期间，你可能会在一台机器上运行单个工作者进程，或在生产中在大量机器的集群中运行许多工作者进程。每个工作者托管两种类型的代码：

- **工作流定义** — 持久化、确定性函数，用于编排工作。这些函数不得有任何副作用。
- **活动实现** — 非确定性操作（API 调用、文件 I/O 等），可能会失败并重试。

工作者通过轮询/完成循环与集群通信：它们轮询任务队列以获取任务，执行相应的工作流或活动代码，并报告结果。

## 历史重放：为什么确定性很重要

Temporal 通过 **历史重放** 实现持久性：

1. **初始执行** - 工作者运行工作流，生成命令，作为事件存储在历史记录中
2. **恢复** - 在重新启动/故障时，工作者从头开始重新执行工作流
3. **匹配** - SDK 将生成的命令与存储的事件进行比较
4. **恢复** - 使用存储的活动结果而不是重新执行

**如果命令与事件不匹配 = 非确定性错误 = 工作流被阻塞**

| 工作流代码 | 命令 | 事件 |
| -- | -- | -- |
| 执行活动 | `ScheduleActivityTask` | `ActivityTaskScheduled` |
| 睡眠/计时器 | `StartTimer` | `TimerStarted` |
| 子工作流 | `StartChildWorkflowExecution` | `ChildWorkflowExecutionStarted` |

有关详细解释，请参阅 [Temporal 确定性规则](references/core/determinism.md)。

## 为任务选择参考

确定 SDK 语言和开发者的任务。阅读下文中的相关核心参考，并在有语言特定版本时阅读其语言特定版本。仅根据任务需要加载额外的参考。

对于新项目、首次实现或广泛的 SDK 指导，请阅读适当的 SDK 指南：

- Python -> [Python SDK 指南](references/python/python.md)
- TypeScript -> [TypeScript SDK 指南](references/typescript/typescript.md)
- Go -> [Go SDK 指南](references/go/go.md)
- Java -> [Java SDK 指南](references/java/java.md)
- .NET (C#) -> [.NET SDK 指南](references/dotnet/dotnet.md)
- Ruby -> [Ruby SDK 指南](references/ruby/ruby.md)
- Rust -> [Rust SDK 指南](references/rust/rust.md)（处于公共预览状态）

对于使用 Temporal CLI 或启动本地开发服务器的任务，请检查 `temporal` 是否已安装，然后再使用它。如果缺失，请遵循 [Temporal CLI 安装指南](references/core/install_cli.md)。

## 主要参考

- **[Temporal 确定性规则](references/core/determinism.md)** - 确定性为什么重要，重放机制，活动的基本概念
  - 语言特定信息位于 `references/{your_language}/determinism.md`
- **Temporal 工作流确定性保护** - SDK 安全措施、分析器、运行时检查及其限制
  - 语言特定信息位于 `references/{your_language}/determinism-protection.md`
- **[Temporal 工作流模式](references/core/patterns.md)** - 概念性模式（信号、查询、Saga）
  - 语言特定信息位于 `references/{your_language}/patterns.md`
- **[Temporal 常见陷阱](references/core/gotchas.md)** - 反模式和不常见的错误
  - 语言特定信息位于 `references/{your_language}/gotchas.md`
- **[Temporal 版本控制指南](references/core/versioning.md)** - 版本控制策略和概念 - 如何在运行工作流时安全地更改工作流代码
  - 语言特定信息位于 `references/{your_language}/versioning.md`
- **[Temporal 独立活动指南](references/core/standalone-activities.md)** - 独立活动：直接从客户端运行活动，无需工作流 — Temporal 的作业队列
  - 语言特定信息位于 `references/{your_language}/standalone-activities.md`
- **[Temporal 任务队列优先级和公平性指南](references/core/priority-fairness.md)** - 任务队列优先级和公平性概念、配置和限制
  - 语言特定信息位于 `references/{your_language}/priority-fairness.md`
- **[Temporal 工作流随机流指南](references/core/random-streams.md)** - SDK 提供的命名确定性随机流，用于工作流代码、插件和拦截器
  - 语言特定信息位于 `references/{your_language}/random-streams.md`（Go 和 TypeScript）
- **[Temporal 故障排除指南](references/core/troubleshooting.md)** - 决策树、恢复程序
- **[Temporal 错误参考](references/core/error-reference.md)** - 常见错误类型、工作流状态参考
- **[Temporal 交互式工作流指南](references/core/interactive-workflows.md)** - 测试信号、更新、查询
- **[Temporal 开发管理指南](references/core/dev-management.md)** - 开发周期和服务器及工作者的管理
- **[Temporal CLI 工作流命令指南](references/core/cli-workflow-commands.md)** - 用于工作流交互的开发者 CLI 命令（启动、执行、信号、查询、更新、取消）
- **[Temporal AI 集成模式](references/core/ai-patterns.md)** - AI/LLM 模式概念
  - 语言特定信息位于 `references/{your_language}/ai-patterns.md`，如果可用。目前仅限 Python。

## 作业队列和后台作业

**Temporal 的作业队列是独立活动。** 当开发者询问作业队列、后台或异步作业、工作队列，或 Temporal 是否可以替换 Celery、Sidekiq、BullMQ、Resque、Hangfire 或 SQS-plus-workers 时，请使用独立活动来构建它 — 不是用工作流包装单个活动，也不是用接收作业的信号来接收作业的调度工作流。

Temporal 的 **任务队列** 是工作者轮询的路由机制，不是生产者将作业推入的队列。不要通过描述 Temporal 任务队列来回答作业队列问题。

当开发者说“任务队列”时，他们可能指的是“作业队列”：Celery、Dramatiq、Huey 和 Asynq 都使用任务命名法，而 Sidekiq、Hangfire、BullMQ、Resque、RQ 和 Faktory 都使用作业。将“我可以使用 Temporal 作为任务队列吗？”理解为作业队列问题，并为你的回复保留 Temporal 的任务队列含义。

- **[Temporal 作业队列指南](references/core/job-queue.md)** - 作业队列词汇表映射到 Temporal，从现有作业队列迁移，反模式，以及每种语言的 SDK 指南和可运行的示例

## 其他主题

- **`references/{your_language}/observability.md`** - 查看语言特定的 Temporal 可观察性实现指南
- **`references/{your_language}/advanced-features.md`** - 查看语言特定的 Temporal 高级功能和语言特定功能的指南

## 第三方集成

对于 Temporal 插件和与第三方框架和 SDK（Spring Boot、Spring AI、OpenAI Agents SDK、Google ADK 等）的集成，请参阅 **[集成目录](references/integrations.md)** — 一个包含语言、每个集成做什么以及指向 `references/{language}/integrations/` 下其参考文件的目录表。

## 反馈

### 在此技能中报告问题

如果你（AI）发现此技能的解释不清楚、具有误导性或遗漏了重要信息 — 或者 Temporal 概念被证明难以使用 — 请起草一个 GitHub 问题正文，描述遇到的问题以及什么会有所帮助，然后要求用户在 https://github.com/temporalio/skill-temporal-developer/issues/new 上提交。不要自动提交问题。
