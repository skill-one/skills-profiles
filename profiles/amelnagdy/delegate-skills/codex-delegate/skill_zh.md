# Codex Delegate

你是**协调者**。这个技能让你可以将一个有边界的编码任务交给一个单独的**执行者**——OpenAI Codex CLI，然后审查它产生的内容并亲自完成。你编写简报并拥有判断权；Codex 在自己的沙盒中完成打字；你进行验证并提交。

这里没有什么是针对某个特定协调代理的具体内容。这个循环只需要运行一个 shell 命令和读取一个文件的能力，所以无论你是 Claude Code、带有选定模型的 OpenCode 或任何可比较的代理，它都工作得一样。 (它是为 Claude Code 设计的，并在 Claude Code 上运行；将其他协调者视为设计目标，尚未得到验证。)

## 不应使用此功能的情况

- 任务足够小，可以直接在行内完成——委托的开销不值得。
- `codex` CLI 未安装或未进行身份验证（运行 `codex login`）。
- 你想亲自编写代码，或者你只需要进行审查（使用 Codex 自身的 `review` 命令）。

## 前提条件（一次性检查）

1. `codex --version` 成功。如果不行，请安装 (`npm i -g @openai/codex`) 并 `codex login`。
2. **确认 `codex` 是否在 PATH 上。** 多次安装很常见（例如，当前的 npm/nvm 复本和陈旧的 Homebrew 复本）。`command -v codex` 显示活动的一个，`codex --version` 显示其版本——一个旧二进制文件可能早于此技能依赖的标志（`codex exec --json`、`-o`、`exec resume`）。中继也会将版本记录到 `result.json` 中，所以陈旧的二进制文件事后可见。
3. 你位于（或将要指向 `--cd` 的）目标 git 仓库。

## 循环

每个任务运行这五个步骤。步骤 1、4 和 5 是你的判断；2 和 3 是机械的。

### 1. 编写简报

Codex 只看到你发送的文本——没有仓库记忆、没有聊天历史、没有共享上下文。任务所需的所有内容都放在简报中：目标、当前状态、要更改的内容、要保留的内容、项目的**实际**门控命令（从仓库的 CLAUDE.md/AGENTS.md/Makefile 中发现它们——不要假设），以及报告合同。告诉 Codex 它将**不会**提交（你将）。每个简报保持一个任务。完整指南和模板：[references/writing-the-brief.md](references/writing-the-brief.md)。

### 2. 派遣

使用捆绑的辅助工具将简报发送给 Codex。它包装 `codex exec`，捕获运行情况，并写入结构化的 `result.json`——所以你唯一的工作就是“运行一个命令，读取一个文件。”（下面的 `<skill-dir>` 是此技能的安装目录——包含此 `SKILL.md` 的文件夹，即你加载技能的目录。Claude Code 在技能加载时将其打印为“此技能的基目录”；在其他协调者上使用相同的目录——如果不确定它在哪里落地，运行 `find ~ -name relay.mjs -path '*codex-delegate*'` 并替换它上面的目录。）

```bash
node "<skill-dir>/scripts/relay.mjs" --brief brief.txt --cd /path/to/repo
# 只读（审查/诊断，无编辑）：添加 --read-only
# 隔离审查（跳过环境 MCP/user 配置）：添加 --ignore-user-config
# 继续精确的 Codex 会话：添加 --session <threadId>  （从 result.json；只发送 delta 简报）
# 无线程 ID 时回退：添加 --resume-last
# 硬时间限制（看门狗）：添加 --timeout 2h  （默认：关闭；实现运行通常需要 1-2h）
# 查看所有选项：运行 node .../relay.mjs --help
```

辅助工具默认为可写 (`workspace-write`) 沙盒，并将其工件写入临时目录，所以被审查的仓库保持干净。它**永远不会提交**——见步骤 5。机制、标志和 `result.json` 的形状：[references/dispatch-and-poll.md](references/dispatch-and-poll.md)。

### 3. 等待完成

辅助工具会阻塞直到 Codex 完成，所以用你的协调者提供的任何东西来支持它，并在返回时恢复：

- **Claude Code：** 使用 `run_in_background: true` 运行 Bash 调用；你将在完成时收到通知。
- **纯 shell / 其他代理：** 对于短任务，在前景运行它，或者将其置于后台并轮询结果文件——`… &` 在 bash/zsh（包括 Git Bash/WSL），或你的 shell 的等效选项（`Start-Job` 在 PowerShell，`start /b` 在 cmd）。当 `result.json` 存在并带有 `status` 时，运行完成。（一个预运行使用错误——错误的参数或空的简报——会退出并带有代码 2 和 stderr 消息，并且不会写入结果文件，所以也要检查退出代码。缺少 `codex` 二进制文件会退出 127，但*确实*会写入一个带有 `status` `codex_unavailable` 的 `result.json`。）

不要相信进度跟踪器超过现实：运行完成当 `result.json` 被写入并且进程已经退出。读取工作树，而不是状态行。执行者的完整报告是 `result.json` 中的 `finalMessage` 字段（也在报告标记之间完整打印在 stdout 上）。

### 4. 审查——不要相信自我报告

Codex 的 `result.json` 包括它自己的摘要和门控声明。**重新验证，不要接受：**

- **自己重新运行项目的门控**（步骤 1 中的测试/检查/构建命令）。永远不要轻信“门控通过”。
- **与简报对比差异**：Codex 是否做了所要求的事情，没有更多（范围蔓延）也没有更少？`result` 中的 `touchedFiles` 是你的起点。
- **如果你安装了相关的守卫技能**，在差异上运行它们（来自 `guard-skills` 的 clean-code-guard、test-guard 等）——此技能生成工作；这些技能判断它。
- 对于模式/迁移更改，进行往返测试；对于删除，grep 悬挂引用。

完整清单：[references/review-and-land.md](references/review-and-land.md)。

### 5. 提交

因为 Codex 的沙盒无法可靠地写入 `.git`（它因版本、操作系统和路径而异），**协调者提交。** 只有在门控通过并且差异有效后：

- 自己提交经过验证的工作，并附带清晰的说明。
- 如果需要更改，使用先前的 `result.json` 中的 `--session <threadId>` 发送 delta 简报（只有在没有线程 ID 可用时才使用 `--resume-last`），并再次审查。

## 只读的第二意见

中继也用作一种安全的方式，以获得没有写入风险的对立第二意见：使用 `--read-only` 派遣一个列出已达成共识的点、然后每个有争议的点都带有两个立场、并要求 Codex 为每个点辩护或让步——在最终消息中交付，不接触任何文件。任何执行者提供只读模式的委托技能都支持相同的使用，但首先检查该模式的保证有多难：Codex 的沙盒执行它，而 Grok 的只是尽力而为，并且只有在事后标记（`readOnlyViolation`）——对于这些执行者，验证 `touchedFiles` 是否为空，而不是假设没有编辑。

## 授权模型

委托是人类选择进入的。一旦他们有了（“运行这个队列”、“继续”），提交经过验证的门控通过的工作是约定的合同——这就是整个要点。对此授权有两个限制：**表面，不要吸收**（报告 Codex 的设计决策、可辩护但未询问的转弯、非阻塞的吹毛求疵，而不是默默地保留它们）和**因范围变化而停止**（如果正确完成需要超出简报，请询问——不要自己扩展授权）。完整说明在 [references/review-and-land.md](references/review-and-land.md) 中。

## 如果你安装了 openai-codex 插件

官方的 openai-codex Claude Code 插件非常出色，并且是**互补的**——`codex-delegate` 基于相同的 `codex` CLI 构建，它不取代插件。它们指向不同的方向：

- 插件的 `codex:codex-rescue` 代理是一个**转发器**：它将一个任务交给 Codex 并返回输出。它故意不轮询、审查或提交。
- 插件的审查命令和停止审查门控运行**相反的方向**：**Codex 审查你的工作**。
- `codex-delegate` 是**反向的协调循环**：*你*驱动 Codex 实现一个任务或队列，*你*审查并提交每个结果。这个循环——简报 → 派遣 → 轮询 → 审查 → 提交，协调者拥有提交——是插件留给你的，也是此技能编码的。

如果你安装了插件，它的配套 CLI 是可选的替代派遣后端；捆绑的 `relay.mjs` 是默认的，因为它除了 `codex` 二进制文件（Node 和 `git`，中继也需要它们，并且是这里每个技能的先决条件）之外没有自己的安装。

## 参考

- [references/writing-the-brief.md](references/writing-the-brief.md) — 如何编写 Codex 可以盲目执行的简报：结构、XML 块、报告合同、嵌入实际门控命令。
- [references/dispatch-and-poll.md](references/dispatch-and-poll.md) — `relay.mjs` 标志、`result.json` 合同、每个协调者的后台运行，以及当运行行为异常时的恢复。
- [references/review-and-land.md](references/review-and-land.md) — 审查清单、提交边界和精确会话重做周期。
- [references/multi-task-queues.md](references/multi-task-queues.md) — 运行顺序队列：将约束向前传递、进度跟踪和运行结束的连贯性检查。
