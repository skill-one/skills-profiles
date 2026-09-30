---
name: grok-delegate
description: 将编码任务委托给 Grok Build CLI 作为后台实现者，然后自行审查其差异并合并。当用户希望将实现工作交给 Grok 时，无论使用“让 Grok 执行 X”、“将此委托给 Grok”、“通过 Grok 运行”、“使用 Grok Build 进行实现/修复/重构”或“让 grok CLI 执行此操作”等措辞，或者需要通过 Grok 运行编码任务队列时，都应优先使用此方法，同时保持审查者的角色。当用户将自行审查差异并提交时，更推荐使用此方法。对于足够小可以直接内联完成的任务，或用户希望直接编写代码而不进行委托的情况，请勿使用。
---

# Grok 委托

对于 Git 所拒绝的所有权检查的受信任存储库，中继支持 `--trust-git-root <精确工作树根>`。此选项仅影响中继 Git 检查，不会永久更改 Git 配置或 Grok 权限。请参阅 [调度和轮询](references/dispatch-and-poll.md#共享或重新挂载驱动器上的 Git 所有权错误)。

你是 **协调者**。这项技能让你可以将一个有界编码任务交给一个单独的 **实现者** — Grok 构建CLI (`grok`) — 然后审查它所生成的结果并自行提交。你编写简报并拥有判断权；Grok 在明确的自主性配置文件下进行打字；你进行验证并提交。

这里没有什么是针对某一个协调代理的具体内容。该循环只需要运行 shell 命令和读取文件的能力，因此无论你是 Claude Code、Cursor、带有选定模型的 OpenCode 或任何可比较的代理，它都工作相同。（它是为 Claude Code 和 Cursor 设计的；将其他协调者视为设计目标，尚未证明。）

## 不应使用此功能的情况

- 任务足够小，可以直接执行 — 委托的开销不值得。
- 未安装 `grok` CLI、未进行身份验证，或账户缺乏 Grok Build beta 访问权限。
- 你想自己编写代码，或者你只需要审查，而不需要实现者运行。

## 前置条件（一次性检查）

1. `grok version` 成功。如果未成功，请在任何平台上使用 `npm i -g @xai-official/grok`（或使用 xAI 官方 Grok CLI 文档中的安装程序）进行安装，并进行身份验证（`grok login`，或在无头主机上使用 `grok login --device-auth`，或设置 `XAI_API_KEY`）。
2. **确认 `grok` 是否在 PATH 中。** `command -v grok` 显示活动二进制文件，而 `grok version` 显示其版本 — 中继将运行到的版本记录在 `result.json` 中，因此过时的二进制文件事后可见。
3. 你位于（或将要指向 `--cd` 的）目标 git 存储库。

## 循环

每个任务运行这五个步骤。步骤 1、4 和 5 是你的判断；2 和 3 是机械的。

### 1. 编写简报

Grok 只看到你发送的文本 — 没有协调者的聊天历史记录，没有共享上下文。任务所需的所有内容都放在简报中：目标、当前状态、要更改的内容、要保留的内容、项目的 **实际** 门禁命令（从存储库的 CLAUDE.md/AGENTS.md/Makefile 中发现它们 — 不要假设），以及报告合同。告诉 Grok 它将 **不会** 提交（你将提交）。每个简报保持一个任务。完整指南和模板：[references/writing-the-brief.md](references/writing-the-brief.md)。

### 2. 调度

使用捆绑的辅助工具将简报发送给 Grok。它包装 `grok -p`，捕获运行情况，并写入结构化的 `result.json` — 因此你唯一的工作就是“运行一个命令，读取一个文件。”（下面的 `<skill-dir>` 是此技能的安装目录 — 包含此 `SKILL.md` 的文件夹，即你加载技能的目录。Claude Code 在技能加载时打印为“此技能的基目录”；在其他协调者上使用相同的目录 — 如果不确定它在哪里落地，请运行 `find ~ -name relay.mjs -path '*grok-delegate*'` 并替换它上面的目录。）

```bash
node "<skill-dir>/scripts/relay.mjs" --brief brief.txt --cd /path/to/repo
# 只读（审查/诊断；尽力而为 — 验证 touchedFiles）：添加 --read-only
# 继续之前的 Grok 会话：       添加 --resume-last  （仅发送 delta 简报）
# 硬时间限制（看门狗）：               添加 --timeout 2h  （默认：关闭；实现者运行通常需要 1-2h）
# 查看所有选项：                          node .../relay.mjs --help
```

辅助工具默认为可写 (`workspace-write`) 自主性配置文件 — `--always-approve` 加上 `--sandbox workspace` — 并将其工件写入临时目录，因此正在审查的存储库保持干净。它 **永远不会** 提交 — 请参阅步骤 5。机制、标志和 `result.json` 的形状：
[references/dispatch-and-poll.md](references/dispatch-and-poll.md)。

### 3. 等待完成

辅助工具会阻塞，直到 Grok 完成，因此用你的协调者提供的任何东西来支持它，并在它返回时恢复：

- **Claude Code：** 使用 `run_in_background: true` 运行 Bash 调用；你将在完成时收到通知。
- **纯 shell / 其他代理：** 对于短任务，在前景运行它，或者将其后台化并轮询结果文件 — `… &` 在 bash/zsh（包括 Git Bash/WSL），或你的 shell 的等效项（PowerShell 中的 `Start-Job`，cmd 中的 `start /b`）。运行完成时，当 `result.json` 存在并带有 `status` 时，运行就完成了。（预运行使用错误 — 坏参数或空简报 — 退出代码为 2 并带有 stderr 消息，并且不写入结果文件，因此也要检查退出代码。缺少 `grok` 二进制文件退出 127，但 *确实* 会写入带有状态 `grok_unavailable` 的 `result.json`。）

不要信任进度跟踪器超过现实：运行完成时，当 `result.json` 被写入并且进程已退出时，运行才算完成。读取工作树，而不是状态行。实现者的完整报告是 `result.json` 中的 `finalMessage` 字段（在报告标记之间完整打印在 stdout 上）。

### 4. 审查 — 不要信任自我报告

Grok 的 `result.json` 包括它自己的摘要和门禁声明。**重新验证，不要接受：**

- **自己重新运行项目的门禁**（步骤 1 中的测试/检查/构建命令）。永远不要相信“门禁通过”。
- **与简报读取差异**：Grok 是否做了所要求的事情，没有更多（范围蔓延）和没有更少？结果中的 `touchedFiles` 是你的起点。
- **如果你安装了相关的守卫技能**，在差异上运行它们（来自 `guard-skills` 的 clean-code-guard、test-guard 等）— 这项技能生成工作；这些技能判断它。
- 对于模式/迁移更改，进行往返操作；对于删除，grep 悬挂引用。

完整清单：[references/review-and-land.md](references/review-and-land.md)。

### 5. 提交

**协调者提交。** 只有在门禁通过并且差异有效时：

- 自己提交经过验证的工作，并附带清晰的说明。
- 如果需要更改，使用 `--resume-last` 发送 delta 简报（不要重新陈述整个任务）并再次审查。

## 自主性模型

Grok 的默认权限模式是 `ask`，这会 **在无头管道中的批准提示上阻塞**。因此，中继始终显式设置自主性：

| 中继标志 | Grok 获得的内容 | 使用情况 |
| --- | --- | --- |
| *(默认)* | `--always-approve --sandbox workspace` | 正常实现 — 写入范围限于工作树 |
| `--read-only` | `--sandbox read-only --always-approve` | 审查 / 诊断 — 内核强制沙盒，不是完全的（请参阅下一条说明） |
| `--full-access` | `--always-approve --sandbox off` | 明确选择，当任务需要不受限制的工具时 |

`--always-approve` 单独会批准所有工具（写入、shell、网络）— 更接近不受限制，而不是工作空间范围的写入。将它与 `--sandbox workspace` 配合使用是保持默认安全的原因。仅在人类要求时才使用 `--full-access`。

**`--read-only` 是内核强制，不是完全的。** 在 grok 1.0.25 上，只读沙盒（macOS 上的 Seatbelt，Linux 上的 Landlock）拒绝 grok 自己的写入/search_replace 工具和 shell 重定向，使用 EPERM，因此 `--always-approve` 仅自动批准沙盒内的工具。配置文件不是完全的：它仍然允许写入 `/tmp`、`/var/tmp` 和 `~/.grok/`，因此位于这些路径之一的存储库不受保护，并且在 macOS 上它不会限制子进程网络。始终确认 `touchedFiles`；将差异视为保证，而不是标志。中继自动化了一个报告触发器：它比较了解 git 陶器，并指纹识别 Git 可见路径中已经脏的工作树身份和索引条目。`readOnlyViolation` 为 `true` 当任一信号证明有更改，`false` 当覆盖完整且未检测到更改，以及 `null` 当覆盖不完整时。忽略路径、子模块内部、完美恢复和并发更改的归因仍然在其外，因此差异审查仍然是保证。

## 授权模型

委托是人类选择进入的。一旦他们有了（“运行这个队列”、“继续”），提交经过验证、门禁通过的工作是约定的合同 — 这就是整个要点。对此授权有两个限制：**表面，不要吸收**（报告 Grok 的设计决策、可辩护但未询问的转弯和非阻塞的吹毛求疵，而不是默默地保留它们）和 **停止范围变化**（如果正确完成需要超出简报，请询问 — 不要自己扩展授权）。完整说明在 [references/review-and-land.md](references/review-and-land.md) 中。

## 参考

- [references/writing-the-brief.md](references/writing-the-brief.md) — 如何编写 Grok 可以盲目执行的简报：结构、XML 块、报告合同、嵌入实际门禁命令。
- [references/dispatch-and-poll.md](references/dispatch-and-poll.md) — `relay.mjs` 标志、`result.json` 合同、每个协调者后台运行，以及运行行为异常时的恢复。
- [references/review-and-land.md](references/review-and-land.md) — 审查清单、提交边界，以及通过 `--resume-last` 的重做周期。
- [references/multi-task-queues.md](references/multi-task-queues.md) — 运行顺序队列：将约束向前传递、进度跟踪，以及运行结束时的连贯性检查。
