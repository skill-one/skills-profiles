# Kimi 委托代理

你是**协调者**。将一个有边界的编码任务交给一个单独的**执行者**——Kimi Code CLI，然后查看它生成的内容并亲自完成。你编写简报并拥有最终判断权；Kimi 在其自己的会话中进行输入；你进行验证并提交。

这个循环只需要一个 shell 命令和文件访问权限，因此任何可比较的协调者都可以驱动它。

## 不应使用此方法的情况

- 任务足够小，可以直接完成；委托的开销不值得。
- `kimi` CLI 未安装或未进行身份验证。
- 你需要一个 CLI 强制的只读执行者。无头 Kimi 没有只读模式。

## 前置条件（一次性检查）

1. 在 macOS/Linux 上使用 `brew install kimi-code` 安装 Kimi Code，或从 [官方 Kimi Code 文档](https://moonshotai.github.io/kimi-code/en/) 使用原生安装程序。
2. 使用 `kimi login` 进行身份验证（设备码流程，无 TUI），或在 TUI 中使用 `/login`。
3. 确认 `kimi --version` 成功。
4. 在目标 git 仓库中工作，或将 `--cd` 指向该仓库。

## 选择模型别名

当省略 `--model` 时，Kimi 使用其 `config.toml` 中的 `default_model`。要选择另一个模型别名，请传递 `--model <从你的 kimi 配置中获取的别名>`。模型别名是用户定义的配置键；使用人类已配置的别名，而不是自行发明。

## 循环

每个任务运行以下五个步骤。步骤 1、4 和 5 需要判断；2 和 3 是机械的。

### 1. 编写简报

Kimi 只能看到你发送的文本以及它可以在工作区中检查的内容——没有聊天历史记录或共享上下文。包括目标、当前状态、要更改的内容、要保留的内容、项目的**实际**门禁以及报告合同。告诉 Kimi 不要提交。每个简报只包含一个任务。参见 [references/writing-the-brief.md](references/writing-the-brief.md)。

### 2. 派发

使用捆绑的辅助工具。它封装了 Kimi 的无头提示模式，捕获结构化的事件流，并写入 `result.json`。（`<skill-dir>` 是包含此 `SKILL.md` 的安装文件夹。）

```bash
node "<skill-dir>/scripts/relay.mjs" --brief brief.txt --cd /path/to/repo
# 选择一个配置的模型别名：       添加 --model <从你的 kimi 配置中获取的别名>
# 恢复最新的会话：              添加 --resume-last  (仅限 delta 简报)
# 恢复特定会话：                添加 --session <id> (仅限 delta 简报)
# 硬时间限制（看门狗）：          添加 --timeout 2h  (30m 默认适合短运行；实现简报通常需要 1-2h)
# 查看所有选项：                 node .../relay.mjs --help
```

子进程的当前工作目录固定了工作区。仅使用重复的 `--add-dir` 标志添加额外的工 作区目录。中继默认在系统临时目录下写入工件，并且永远不会提交。参见 [references/dispatch-and-poll.md](references/dispatch-and-poll.md)。

### 3. 等待完成

辅助工具会阻塞直到 Kimi 完成。使用协调者的后台命令功能运行它，或在 shell 中将其后台运行并轮询 `result.json`。运行前如果使用错误会退出 2 并不写入结果；如果 `kimi` 未找到会退出 127 并写入 `status: "kimi_unavailable"`。

相信进程状态和工作树而不是进度显示。完成意味着进程已退出并且 `result.json` 存在。Kimi 的完整报告是 `result.json` 中的 `finalMessage` 字段（也完整打印在报告标记之间的 stdout 上）。

### 4. 审查——不要相信自我报告

将 Kimi 的最终消息和门禁声明视为声明：

- 自己重新运行项目的门禁。
- 与简报进行 diff，从 `touchedFiles` 开始阅读。
- 如果安装了相关守卫技能，请运行它们。
- 在删除或重命名后进行往返迁移，并查找悬而未决的引用。

参见 [references/review-and-land.md](references/review-and-land.md)。

### 5. 提交

执行者编辑工作树；**协调者提交**。只有在门禁通过并且 diff 符合要求后才能提交。如果需要返工，请使用 `--resume-last` 或 `--session <id>` 发送 delta 简报，然后再次审查。

## 自主性和权限

在无头 `-p` 模式下，Kimi 始终以**自动权限模式**运行，并且永远不会请求批准。Kimi 拒绝 `--prompt` 与 `--yolo`、`--auto` 或 `--plan` 结合使用，因此中继不会传递任何它们，并且不提供 `--read-only` 或 `--full-access` 选项。没有 CLI 强制的只读模式：每次运行后检查 `touchedFiles` 和 diff。这个 diff，而不是一个标志，是变更的保证。

## 授权模型

委托是人类选择进入的。一旦他们确认了（“运行这个队列”、“继续”），提交经过验证且通过门禁的工作就是约定的合同。仍然有两个限制：**表面，不要吸收**（报告 Kimi 的设计决策、可辩护但未询问的转弯，以及非阻塞的吹毛求疵）和**停止以应对范围变更**（如果正确完成需要超出简报，请询问而不是扩展授权）。参见 [references/review-and-land.md](references/review-and-land.md)。

## 参考资料

- [references/writing-the-brief.md](references/writing-the-brief.md) - 结构、报告合同、实际门禁、argv 传递和 delta 简报。
- [references/dispatch-and-poll.md](references/dispatch-and-poll.md) - 标志、工件、`result.json`、轮询和故障恢复。
- [references/review-and-land.md](references/review-and-land.md) - 审查清单、提交边界和通过 Kimi 会话进行返工。
- [references/multi-task-queues.md](references/multi-task-queues.md) - 顺序队列、约束传递、进度跟踪和最终一致性检查。
