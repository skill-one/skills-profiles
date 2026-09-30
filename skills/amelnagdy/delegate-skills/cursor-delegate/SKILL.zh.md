---
name: cursor-delegate
description: 将编码任务委托给 Cursor Agent CLI (`cursor-agent`) 作为后台实现者，然后自行审查其差异并合并。当用户希望将实现工作交给 Cursor 时使用此方法——例如“让 Cursor 实现 X”、“将此委托给 Cursor”、“通过 Cursor Agent 运行”或“使用 Cursor 实现/修复/重构”——或者希望在保持审查者身份的情况下，通过 Cursor 运行编码任务队列。对于足够小可以直接内联完成的任务，或用户希望直接编写代码而不进行委托的情况，请勿使用。
---

# Cursor 委托代理

你是**指挥者**。将一个有边界的编码任务交给一个独立的**执行者**——Cursor Agent CLI，然后审阅它生成的内容，并亲自将其部署。你撰写简报并拥有最终判断权；Cursor 在其自己的会话中进行输入；你进行验证并提交。

这个循环只需要一个 shell 命令和文件访问权限，因此任何可比较的指挥者都可以驱动它。

## 不应使用此功能的情况

- 任务足够小，可以直接完成；委托的开销不值得。
- `cursor-agent` CLI 未安装或未进行身份验证（运行 `cursor-agent login`）。
- 你想亲自编写代码，或者你只需要对你自己编写的代码提出意见（一个 `--read-only` 分发可以涵盖这一点——见下文——但一个简单的审阅可能根本不需要委托）。

## 前置条件（检查一次）

1. `cursor-agent --version` 运行成功。如果没有，请按照你平台的安装程序在 [cursor.com/cli](https://cursor.com/cli) 上进行操作，检查它将运行的内容，并使用 `cursor-agent login` 进行身份验证。
2. `cursor-agent status` 显示你已登录。
3. 你位于（或将要指向 `--cd` 的）目标 git 仓库。中继会传递 `--trust`，因此仅将其指向你信任的仓库。

## 选择模型

省略 `--model` 将使用你的 Cursor 默认值（通常是 `auto`——Cursor 会选择）。要固定一个模型，请传递 `--model <name>`，其中 `<name>` 来自账户的实时 `cursor-agent models` 输出——从该列表中选择，而不是发明一个名称。参数化形式，如 `<name>[context=1m,effort=high]`，将按原样转发。实际服务该运行的模型被记录为 `resolvedModel` 在 `result.json` 中。

## 循环

每个任务运行以下五个步骤。步骤 1、4 和 5 需要判断；2 和 3 是机械的。

### 1. 撰写简报

Cursor 只能看到你发送的文本以及它可以在工作区中检查的内容——没有聊天历史记录或共享上下文。包括目标、当前状态、要更改的内容、要保留的内容、项目的**实际**门禁以及报告合同。告诉 Cursor 不要提交。每个简报保持一个任务。参见 [references/writing-the-brief.md](references/writing-the-brief.md)。

### 2. 分发

使用捆绑的辅助工具。它包装了 `cursor-agent -p`，将简报通过 stdin 输入，捕获结构化的事件流，并写入 `result.json`。（`<skill-dir>` 是包含此 `SKILL.md` 的安装文件夹。）

```bash
node "<skill-dir>/scripts/relay.mjs" --brief brief.txt --cd /path/to/repo
# 只读（计划模式——审查/诊断，无编辑）：添加 --read-only
# 具有写入能力但不自动批准命令：添加 --no-force
# 明确覆盖本次运行的 Cursor 沙盒：添加 --sandbox enabled|disabled
# 从 `cursor-agent models` 中固定一个模型：添加 --model <name>
# 恢复最新的会话：添加 --resume-last （仅限增量简报）
# 恢复特定会话：添加 --session <id> （仅限增量简报）
# 硬时间限制（看门狗）：添加 --timeout 2h （30m 的默认值适合短运行；实现简报通常需要 1-2h）
# 查看所有选项：node .../relay.mjs --help
```

子进程的当前工作目录固定了工作区。在 Cursor `2026.07.23` 或更新版本上，仅使用可重复的 `--add-dir` 标志来处理额外的工 作区目录。中继默认在系统临时目录下写入工件，并且永远不会提交。参见 [references/dispatch-and-poll.md](references/dispatch-and-poll.md)。

### 3. 等待完成

辅助工具会阻塞直到 Cursor 完成工作。使用指挥者的后台命令功能运行它，或者在 shell 中将其后台运行并轮询 `result.json`。运行前使用错误退出 2 并不写入结果；缺少 `cursor-agent` 退出 127 并写入 `status: "cursor_agent_unavailable"`。

信任进程状态和工作树而不是进度显示。完成意味着进程已退出并且 `result.json` 存在。Cursor 的完整报告是 `result.json` 中的 `finalMessage` 字段（在报告标记之间完整打印在 stdout 上）。

**Windows + 钩子注意事项**：如果用户已配置 Cursor 钩子（`~/.cursor/hooks.json`，或 Claude Code `PreToolUse` 钩子，cursor-agent 会导入），从 Git Bash (MSYS) 控制台分发会使 cursor-agent 将 PowerShell 语法钩子包装器传递给 bash，因此 Cursor 尝试运行的每个命令都会被阻止——编辑仍然会提交，门禁不会运行。改从 PowerShell 或 cmd 控制台分发。详情：[references/dispatch-and-poll.md](references/dispatch-and-poll.md)。

### 4. 审查——不要信任自我报告

将 Cursor 的最终消息和门禁声明视为声明：

- 自己重新运行项目的门禁。
- 与简报进行比较的 diff，从 `touchedFiles` 开始阅读。
- 如果安装了相关守卫技能，请运行它们。
- 进行往返迁移，并在删除或重命名后搜索悬而未决的引用。

参见 [references/review-and-land.md](references/review-and-land.md)。

### 5. 部署

执行者编辑工作树；**指挥者提交**。只有在门禁通过并且 diff 符合要求后才能提交。如果需要返工，请使用 `--resume-last` 或 `--session <id>` 发送增量简报，然后再次审查。

## 自主性和权限

全新运行默认为**具有 `--force` 的写入能力**：Cursor 在你的 Cursor 配置明确拒绝的情况下不会运行命令，因此普通门禁（测试、代码检查器、构建）会无头运行。`--no-force` 保持运行具有写入能力但会阻止自动命令批准；需要批准的命令会被拒绝，因为无头运行无法提示。`--read-only` 切换到 Cursor 的**计划模式**（只读分析，无编辑，无 `--force`）。中继始终传递 `--trust` 以防止无头运行因工作区信任提示而停滞，这就是为什么 `--cd` 必须始终指向你信任的仓库。仅在需要为该分发覆盖 Cursor 的沙盒时传递 `--sandbox enabled` 或 `--sandbox disabled`。请求的值被记录为 `sandbox` 在 `result.json` 中；它不声明 Cursor 实际应用了什么。Cursor 报告的权限模式被记录为 `permissionMode`；在每次运行后检查 `touchedFiles` 和 diff。

## 只读第二意见

`--read-only` 也可以作为一种干净的方式，以无写入风险的方式获得对抗性的第二意见：分发一个列出已同意点的简报，然后对每个有争议的点列出两个立场，并要求 Cursor 为每个点辩护或承认——在最终消息中交付，不接触任何文件。

## 授权模型

委托是用户选择进入的。一旦他们确认了（“运行这个队列”，“继续”），提交经过验证、门禁通过的工件就是约定的合同。仍然存在两个限制：**表面，不要吸收**（报告 Cursor 的设计决策、可辩护但未询问的转弯，以及非阻塞的吹毛求疵）和**因范围变化而停止**（如果正确完成需要超出简报，请询问而不是扩大授权）。参见 [references/review-and-land.md](references/review-and-land.md)。

## 参考

- [references/writing-the-brief.md](references/writing-the-brief.md) — 结构、报告合同、实际门禁和增量简报。
- [references/dispatch-and-poll.md](references/dispatch-and-poll.md) — 标志、工件、`result.json`、轮询和故障恢复。
- [references/review-and-land.md](references/review-and-land.md) — 审查清单、提交边界和通过 Cursor 会话进行返工。
- [references/multi-task-queues.md](references/multi-task-queues.md) — 顺序队列、约束传递、进度跟踪和最终一致性检查。
