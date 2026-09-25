# Cursor 委托代理

你是**指挥者**。将一个有边界的编码任务交给一个独立的**执行者**——Cursor Agent CLI，然后审阅它生成的内容并亲自将其部署。你撰写简报并拥有最终判断权；Cursor 在其自己的会话中进行输入；你进行验证并提交。

这个循环只需要一个 shell 命令和文件访问权限，因此任何可比较的指挥者都可以驱动它。

## 不应使用此方法的情况

- 任务足够小，可以直接在行内完成；委托的开销不值得。
- `cursor-agent` CLI 未安装或未进行身份验证（运行 `cursor-agent login`）。
- 你想亲自编写代码，或者你只需要对你自己编写的代码提供 Cursor 的意见（一个 `--read-only` 分发可以涵盖这一点——见下文——但一个普通的审阅可能根本不需要委托）。

## 前置条件（检查一次）

1. `cursor-agent --version` 命令成功执行。如果没有，请按照你所在平台的安装程序说明，在 [cursor.com/cli](https://cursor.com/cli) 上查看它将运行的内容，并使用 `cursor-agent login` 进行身份验证。
2. `cursor-agent status` 命令显示你已登录。
3. 你位于目标 git 仓库中（或者将 `--cd` 参数指向该仓库）。中继会传递 `--trust` 参数，因此请仅将其指向你信任的仓库。

## 选择模型

省略 `--model` 参数将使用你的 Cursor 默认设置（通常是 `auto`——Cursor 会自动选择）。要锁定某个模型，请使用 `--model <name>` 参数，其中 `<name>` 来自账户的实时 `cursor-agent models` 输出——从该列表中选择名称，而不是自行发明名称。参数化形式，如 `<name>[context=1m,effort=high]`，将按原样转发。实际服务该运行的模型将记录为 `resolvedModel`，位于 `result.json` 文件中。

## 循环流程

每个任务运行以下五个步骤。步骤 1、4 和 5 需要判断；2 和 3 是机械操作。

### 1. 撰写简报

Cursor 只能看到你发送的文本以及它可以在工作区中检查的内容——没有聊天历史记录或共享上下文。包括目标、当前状态、要更改的内容、要保留的内容、项目的**实际**门禁，以及报告合同。告诉 Cursor 不要提交。每个简报只包含一个任务。请参阅 [references/writing-the-brief.md](references/writing-the-brief.md)。

### 2. 分发

使用捆绑的辅助工具。它包装了 `cursor-agent -p`，将简报作为标准输入传递，捕获结构化的事件流，并写入 `result.json`。 (`<skill-dir>` 是包含此 `SKILL.md` 文件的安装文件夹。)

```bash
node "<skill-dir>/scripts/relay.mjs" --brief brief.txt --cd /path/to/repo
# 仅读模式（计划模式——审阅/诊断，无修改）：添加 --read-only
# 无需自动命令批准即可进行写操作：添加 --no-force
# 显式覆盖本次运行的 Cursor 沙盒：添加 --sandbox enabled|disabled
# 从 `cursor-agent models` 中锁定模型：添加 --model <name>
# 恢复最近会话：添加 --resume-last  (仅限增量简报)
# 恢复特定会话：添加 --session <id> (仅限增量简报)
# 硬性时间限制（看门狗）：添加 --timeout 2h  (30 分钟的默认设置适合短运行；实现简报通常需要 1-2 小时)
# 查看所有选项：node .../relay.mjs --help
```

子进程的当前工作目录（cwd）固定了工作区。在 Cursor `2026.07.23` 或更新版本中，仅使用可重复的 `--add-dir` 参数来指定额外的工作区目录。中继默认在系统临时目录下写入工件，并且永远不会提交。请参阅 [references/dispatch-and-poll.md](references/dispatch-and-poll.md)。

### 3. 等待完成

辅助工具会阻塞直到 Cursor 完成任务。使用指挥者的后台命令功能运行它，或者在 shell 中将其置于后台，并轮询 `result.json`。如果运行前出现使用错误，则退出码为 2 且不写入结果；如果缺少 `cursor-agent`，则退出码为 127 并写入 `status: "cursor_agent_unavailable"`。

信任进程状态和工作树，而不是进度显示。完成意味着进程已退出并且 `result.json` 文件存在。Cursor 的完整报告是 `result.json` 中的 `finalMessage` 字段（在报告标记之间完整打印在标准输出上）。

**Windows + 钩子注意事项**：如果用户已配置 Cursor 钩子（`~/.cursor/hooks.json`，或 Claude Code 的 `PreToolUse` 钩子，cursor-agent 会导入这些钩子），从 Git Bash (MSYS) 控制台分发会导致 cursor-agent 将 PowerShell 语法钩子包装器传递给 bash，因此 Cursor 尝试运行的每个命令都会被阻止——修改仍然会提交，门禁不会运行。改从 PowerShell 或 cmd 控制台分发。详情：[references/dispatch-and-poll.md](references/dispatch-and-poll.md)。

### 4. 审阅——不要信任自报

将 Cursor 的最终消息和门禁声明视为声明：

- 亲自运行项目的门禁。
- 对简报进行差异比较，从 `touchedFiles` 开始。
- 如果安装了相关守卫技能，请运行它们。
- 运行往返迁移，并在删除或重命名后查找悬空引用。

请参阅 [references/review-and-land.md](references/review-and-land.md)。

### 5. 提交

执行者编辑工作树；**指挥者提交**。只有在门禁通过并且差异有效后才能提交。如果需要返工，请使用 `--resume-last` 或 `--session <id>` 发送增量简报，然后再次审阅。

## 自主性和权限

新运行默认为**带 `--force` 的写操作能力**：Cursor 在未获得你的 Cursor 配置明确拒绝的情况下会运行命令，因此普通门禁（测试、代码检查、构建）会无头运行。`--no-force` 保持运行为写操作能力，但会阻止自动命令批准；需要批准的命令会被拒绝，因为无头运行无法提示。`--read-only` 切换到 Cursor 的**计划模式**（只读分析，无修改，无 `--force`）。中继始终传递 `--trust` 参数，以防止无头运行因工作区信任提示而停滞，这就是为什么 `--cd` 必须始终指向你信任的仓库。仅在需要覆盖本次分发的 Cursor 沙盒时，才传递 `--sandbox enabled` 或 `--sandbox disabled`。请求的值记录为 `result.json` 中的 `sandbox`；它不声明 Cursor 实际应用了什么。Cursor 报告的权限模式记录为 `permissionMode`；每次运行后检查 `touchedFiles` 和差异。

## 仅读的第二意见

`--read-only` 也可以作为一种干净的方式，以无写入风险的方式获得对抗性的第二意见：分发一个列出已同意点的简报，然后对每个有争议的点列出两种立场，并要求 Cursor 为每种立场辩护或承认——在最终消息中交付，不触碰任何文件。

## 授权模型

委托是用户选择参与的。一旦他们确认了（“运行这个队列”，“继续”），提交经过验证且门禁通过的工件就是双方同意的合同。仍然存在两个限制：**表面，不要吸收**（报告 Cursor 的设计决策、可辩护但未询问的转折，以及非阻塞的吹毛求疵）和**因范围变化而停止**（如果正确完成需要超出简报范围，请询问而不是扩大授权）。请参阅 [references/review-and-land.md](references/review-and-land.md)。

## 参考资料

- [references/writing-the-brief.md](references/writing-the-brief.md) — 结构、报告合同、实际门禁和增量简报。
- [references/dispatch-and-poll.md](references/dispatch-and-poll.md) — 标志、工件、`result.json`、轮询和故障恢复。
- [references/review-and-land.md](references/review-and-land.md) — 审阅清单、提交边界和通过 Cursor 会话进行返工。
- [references/multi-task-queues.md](references/multi-task-queues.md) — 顺序队列、约束传递、进度跟踪和最终一致性检查。
