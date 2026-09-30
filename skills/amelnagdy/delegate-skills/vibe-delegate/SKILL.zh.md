---
name: vibe-delegate
description: 将编码任务委托给 Mistral Vibe CLI (`vibe`) 作为后台实现者，然后自行审查其差异并合并。当用户希望将实现工作交给 Vibe 时（例如“让 Vibe 实现 X”、“将此委托给 Vibe”、“通过 Mistral Vibe 运行”、“使用 vibe 实现/修复/重构”）——或者希望在保持审查者身份的情况下，通过 Vibe 运行编码任务队列——请使用此方法。对于足够小可以直接内联完成的任务，或用户希望直接编写代码而不进行委托的情况，请勿使用。
---

# Vibe 委托代理

你是**协调者**。将一个有边界的编码任务交给一个单独的**执行者**——Mistral Vibe CLI (`vibe`)，然后审查它生成的内容并亲自将其部署。你编写简报并拥有最终判断权；Vibe 在其自己的会话中进行打字；你进行验证并提交。

这个循环只需要一个 shell 命令和文件访问权限，因此任何可比较的协调者都可以驱动它。

## 不应使用此方法的情况

- 任务足够小，可以直接在行内完成；委托的额外开销不值得。
- `vibe` CLI 未安装或未进行身份验证。

## 前置条件（一次性检查）

1. 安装 [`uv`](https://docs.astral.sh/uv/getting-started/installation/)，然后安装 Mistral Vibe：
   - `uv tool install mistral-vibe`
2. 使用 `vibe --setup` 配置你的 API 密钥，或在环境中设置 `MISTRAL_API_KEY`。
3. 确认 `vibe --version` 命令成功执行。
4. 在目标 git 仓库中工作，或使用 `--cd` 指向该仓库。

## 循环流程

每个任务运行以下五个步骤。步骤 1、4 和 5 需要判断；2 和 3 是机械性的。

### 1. 编写简报

Vibe 只能看到你发送的文本以及它可以在工作区中检查的内容——没有聊天历史记录或共享上下文。包括目标、当前状态、需要更改的内容、需要保留的内容、项目的**实际**门禁以及报告合同。告诉 Vibe 不要提交。每个简报只包含一个任务。参见 [references/writing-the-brief.md](references/writing-the-brief.md)。

默认模式无法无头地批准大多数 shell 命令，因此协调者运行门禁。当人类明确授权 `--full-access` 时，才要求 Vibe 运行门禁。

### 2. 派发

使用捆绑的辅助工具。它封装了 Vibe 的无头 `--prompt` 模式，捕获结构化的事件流，并写入 `result.json`。（`<skill-dir>` 是包含此 `SKILL.md` 的安装文件夹。）

```bash
node "<skill-dir>/scripts/relay.mjs" --brief brief.txt --cd /path/to/repo
# 限制轮次以控制成本：           添加 --max-turns <n>
# 指示性价格阈值/令牌上限：  添加 --max-price <usd> --max-tokens <n>
# 仅规划/只读：                     添加 --plan-only
# 无限制的 shell 和工具：           添加 --full-access (需要明确授权)
# 恢复最新会话：         添加 --resume-last  (仅限增量简报)
# 恢复特定会话：              添加 --session <id> (仅限增量简报)
# 查看所有选项：                        node .../relay.mjs --help
```

子进程的当前工作目录（cwd）固定了工作区。Relay 默认在系统临时目录下写入工件，并且永远不会提交。参见 [references/dispatch-and-poll.md](references/dispatch-and-poll.md)。

### 3. 等待完成

辅助工具会阻塞直到 Vibe 完成任务。使用协调者的后台命令功能运行它，或在 shell 中将其后台运行并轮询 `result.json`。运行前如果出现使用错误，会退出状态码 2 且不写入结果；如果 `vibe` 未可用，会退出状态码 127 并写入 `status: "vibe_unavailable"`。
Watchdog 会写入 `status: "timeout"`；在 POSIX 上终止 Relay 会停止 Vibe 的进程树后写入 `status: "aborted"`。

信任进程状态和工作树，而不是进度显示。完成意味着进程已退出且 `result.json` 存在。

### 4. 审查——不要信任自我报告

将 Vibe 的最终消息和门禁声明视为声明：

- 自己重新运行项目的门禁。
- 与简报进行 diff 对比，从 `touchedFiles` 开始阅读。
- 如果安装了相关守卫技能，请运行它们。
- 在删除或重命名后，进行往返迁移并查找悬空引用。

参见 [references/review-and-land.md](references/review-and-land.md)。

### 5. 部署

执行者编辑工作树；**协调者提交**。只有在门禁通过且 diff 合格后才能提交。如果需要返工，请使用 `--resume-last` 或 `--session <id>` 发送增量简报，然后再次审查。

## 自主性和权限

在 `--prompt` 模式下，Relay 始终显式设置代理配置文件：

| Relay 标志 | Vibe 获取的内容 | 使用场景 |
| --- | --- | --- |
| *(默认)* | `--agent accept-edits` | 正常实现——内置文件编辑被批准 |
| `--plan-only` | `--agent plan` | 只读审查、探索或规划 |
| `--full-access` | `--agent auto-approve` | 需要任意 shell/工具的明确授权运行 |

默认模式允许 Vibe 编辑目标工作树中的文件。无头地拒绝大多数需要门禁的 shell 命令，包括大多数项目门禁；协调者运行门禁。
`--full-access` 禁用 Vibe 的工具批准并允许在用户账户下执行任意 shell/工具；仅在使用明确的人类授权时使用它。每次运行后始终检查 `touchedFiles` 和 diff。

`--trust` 始终传递以防止无头运行中的交互式目录信任提示。它不是一个沙盒，也不会授予权限。

## 授权模型

委托是人类选择进入的事情。一旦他们确认了（“运行这个队列”、“继续”），提交经过验证且通过门禁的工作就是约定的合同。仍然存在两个限制：**表面，不要吸收**（报告 Vibe 的设计决策、可辩护但未询问的轮次、非阻塞的挑剔意见）和**因范围变更而停止**（如果正确完成需要超出简报范围，请询问而不是扩展授权）。参见 [references/review-and-land.md](references/review-and-land.md)。

## 参考资料

- [references/writing-the-brief.md](references/writing-the-brief.md) — 结构、报告合同、实际门禁、argv 传递和增量简报。
- [references/dispatch-and-poll.md](references/dispatch-and-poll.md) — 标志、工件、`result.json`、轮询和故障恢复。
- [references/review-and-land.md](references/review-and-land.md) — 审查清单、提交边界和通过 Vibe 会话进行返工。
- [references/multi-task-queues.md](references/multi-task-queues.md) — 顺序队列、约束传递、进度跟踪和最终一致性检查。
