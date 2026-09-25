# OKX 任务监控

用户会话任务收件箱的实时监控。负责：触发器、监控命令、反 Cron 规则、项目分发（`notification` / `decision_request`）、认领语义、`llmContent` 执行、停止条件。

业务操作（申请 / 交付 / 争议 / 报价 / 接受）属于 `okx-agent-task`。此技能仅处理监控循环。

## 触发器 — 强制路由（非 cron / 定时 / 轮询）

当以下任何触发短语匹配时，执行 §Action。监控命令是一个单一的 long-poll 调用（调用本身等待事件）；**不要**将其包装在 `/loop`、`Cron`、`$CODEX_HOME/automations`、`watch -n`、`sleep` 循环、调度框架或“设置周期性任务”中。**不要**询问“我应该多久检查一次？”—— long-poll 就是等待。**不要**用另一个命令替代轮询。

**触发短语**：
- 中文（实时监控）：`监听任务进展` / `开始监听任务` / `关注任务进展` / `使用监听 skill 监听任务进展` / `帮我盯着任务` / `任务有进度就告诉我` / `任务有动静告诉我` / `开监听` / `watch 任务`
- 中文（历史 / 回收站清空）：`历史消息` / `历史记录` / `过去消息` / `之前的消息` / `帮我看看之前的历史消息` / `看下之前的消息` / `未读消息`
- 中文（延续——先澄清，见 §延续触发器）：`继续监听` / `继续盯着` / `继续 watch` / `接着监听` / `再监听一下` / `继续监听任务`
- 英文（实时监控）：`task watch` / `user watch` / `monitor task progress` / `keep me posted on tasks` / `watch tasks` / `start watching`
- 英文（历史 / 回收站清空）：`show past messages` / `show message history` / `catch me up on tasks` / `unread task messages`
- 英文（延续——先澄清，见 §延续触发器）：`keep watching` / `continue watching` / `resume monitoring`

> ⚠️ **延续触发器是一个特殊情况**——它们不会立即调用 watch。它们意味着用户想要继续监控某个特定的任务，但意图是模糊的（哪个任务？还是所有任务？）。见下文 §延续触发器 的澄清流程。

> 📥 **为什么“查看历史”路由到这里**：watch 是事件流的**破坏性读取**——每次调用返回自上次调用以来累积的未读事件完整回执（例如，在无人监控时），然后 long-poll 新事件。用户要求过去 / 错过 / 未读消息是要求清空该回执——相同的命令，相同的 Dispatch 流。**不要**路由到 `agent active-tasks` / `agent status`（那些是摘要，不是实际通知正文）。对于未回复的 `decision_request` 项目（`watch` 已经消费，但用户还没有 `check`），见 §“拉取未处理的 `decision_request` 项目”。

## 平台兼容性 — 仅限 Claude Code / Codex

🛑 `okx-a2a` CLI 仅在 **Claude Code** 和 **Codex** 扣具上连接。在 **Hermes** 和 **OpenClaw** 上，客户端本身原生推送任务通知——无需手动监控。

在 §Action 之前，检查环境变量：

```bash
detect_watch_support() {
  if [ "${CLAUDECODE:-}" = "1" ]; then
    echo "Claude"
  elif [ -n "${CODEX_THREAD_ID:-}" ]; then
    echo "Codex"
  else
    echo "unsupported"
  fi
}
detect_watch_support
```

- 输出 ∈ {`Claude`, `Codex`} → 继续执行 §Action。
- 输出 = `unsupported` → **停止**。告诉用户（本地化到他们的语言）："当前平台不支持 `okx-a2a` 监听——任务通知会由客户端直接推送，无需手动开监听。" / "This platform doesn't support `okx-a2a`; task notifications are delivered natively by the client — no manual watch needed." **不要**运行任何 `okx-a2a` 命令。

## Action

### 延续触发器 — 回忆上次 jobId，然后重新启动

如果用户的消息匹配了**延续式**短语（`继续监听` / `继续盯着` / `继续 watch` / `接着监听` / `再监听一下` / `继续监听任务` / `keep watching` / `continue watching` / `resume monitoring`），用户的意思是“继续监控我们之前正在跟踪的任务”——他们期望在相同的 jobId 上进行范围监控，而不是一个全新的全局监控。

**步骤 1 — 从当前对话的文本中回忆 jobId。** 按以下顺序搜索，取第一个匹配项：

1. 在当前对话中较早发出的 CLI `[Watch]` 块（jobId 是其 `okx-a2a user watch ...` 命令中的 `--job-id <X>` 值）。
2. 最新的成功 `agent create-task` / `agent publish-draft` stdout（jobId 以 `jobId: 0x...` 打印）。
3. 在当前对话中渲染的任何 `notification` / `decision_request` 中引用的最新 jobId。

**步骤 2 — 根据回忆结果路由**：

- **找到 jobId** → 进入范围会话。**不要**发出 §Banner（用户已经知道他们在跟踪什么——在这里显示横幅是多余的仪式）。只需运行 `okx-a2a user watch --json --job-id <X>`。粘性 `--job-id <X>` 应用于本会话的其余部分，根据 §Session-scoped sticky。

- **没有找到 jobId** → 回退到全局会话。用户“继续监控”的意图与此行为不同，所以 **必须** 发出 §Banner（这是用户唯一的信号，表明监控已重新启动为全局而不是范围）。然后运行 `okx-a2a user watch --json`（没有 `--job-id`）。**不要**询问用户——延续短语加上无法恢复的 jobId 与一个全新的 `task watch` 条目相同。

### 🛑 进入监控前的横幅

**根据入口决定，而不是“这是这个回合中的第一个监控吗”。** 查看**触发** `okx-a2a user watch` 调用的内容——而不是当前回合中是否是第一个监控调用。

**需要横幅的条目（仅这两个）**：

1. **触发短语入口**——当前回合的用户消息匹配了 §Triggers 短语（例如 `监听任务进展` / `历史消息` / `task watch`）。**例外**：延续式短语（`继续监听` / `keep watching` / ...）仅在回忆失败并且监控回退到全局时才触发横幅——见 §延续触发器 的完整规则。
2. **CLI `[Watch]` 块入口**——当前回合中较早发出的命令在 stdout 中输出了 `[Watch]` 块：一个提示块，以 `[Watch]` 开头，并指示当前调用运行 `okx-a2a user watch ...`（典型示例：`` [Watch] Per `okx-task-watch` SKILL.md, start the monitor now: ``, output by `agent create-task` / `agent publish-draft`）。

任何不匹配这两个条目之一的监控调用**必须**不发出横幅——所有会话延续路径（dispatch resume、wake fire 等）都排除在外。

**如何发送**：将确切的规范横幅作为独立的**用户可见助手消息**发出（在聊天中作为 AI 对用户的回复出现——不是工具 stdout、思考块或用户无法看到的内部注释）。

| 聊天语言 | 精确字符串（逐字） |
|---|---|
| 中文 | `🔔 监听已启动，如果有历史消息，我们将先逐个处理，新任务进展会及时通知。` |
| 英文 | `🔔 Watch started — any backlog will be processed first, then you'll be notified of new task events as they arrive.` |
| 其他 | 翻译英文行；保持 🔔 开头和两句话结构（启动 + 先处理回执 + 然后新事件）。 |

❌ 违规示例：

- 没有在同一个助手消息中包含确切的规范字符串就说 `我现在开始监听` / `I'll start watching now`（或任何释义）。
- 在横幅出现之前调用监控工具。
- 将横幅嵌入 Bash 工具 stdout / 思考块 / 工具调用参数——这些位置对用户不可见，所以横幅实际上没有被传递。
- 在重新进入路径（通知/decision_request 处理后的恢复、wake fire）上发出横幅——这些不是新入口。

### 运行监控

```bash
okx-a2a user watch --json
```

当调用返回项目时，根据 §Dispatch 逐个处理。处理所有项目后，重新进入相同的命令（没有横幅）——唯一的例外是 §停止条件触发器。

### Session-scoped `--job-id`（粘性）

如果此监控会话是从 CLI `[Watch]` 块启动的（唯一将 `--job-id <X>` 放在第一个调用的路径），**`--job-id <X>` 在整个会话中是粘性的**。无论此技能显示裸命令 `okx-a2a user watch --json`，都直接附加 `--job-id <X>`——包括：

- §Dispatch notification resume
- §Dispatch decision_request resume（结果 3 / 4 / 5）
- §处理后的重新进入

会话在 §停止条件触发时结束，或者当用户通过 §Triggers 短语启动**新的**监控时——那个新会话是全局的，没有 `--job-id`。

## 反模式

- **不要**使用 `/loop`、Cron、`$CODEX_HOME/automations`、`watch -n`、`sleep` 循环或任何围绕 `onchainos agent status` / `agent active-tasks` 的轮询。
- 🛑 一旦启动，监控循环**只有在** §停止条件触发时才会停止。在此之前你没有权力结束它——不是通过 Ctrl-C'ing 在飞的调用，不是通过跳过下一个重新进入，不是因为输出“看起来很薄”、“感觉很慢”或你想“干净地重启”。沉默是一个长轮询的健康状态。
- **不要**传递 `--from-now`。默认情况下 watch 首先返回未读事件的完整回执，然后 long-poll 新事件；`--from-now` 跳过回执并静默丢弃用户尚未看到的事件（watch 是破坏性读取——那些事件将永久消失）。
- **不要**传递 `--job-id` **除了在发布后的 `[Watch]` 块中**。`user watch` 默认是用户会话范围的监控；缩小到单个任务会使其目的失效并错过跨任务事件。唯一的例外是 `agent create-task` / `agent publish-draft` 发出的 CLI `[Watch]` 块，它故意将第一个 watch 调用缩小到新发布的 `jobId`，以便用户在发布后立即看到该任务的通知。触发短语入口（例如 `监听任务进展` / `task watch`）和任何 §Dispatch 重新进入必须仍然运行 watch **没有** `--job-id`。
- 🛑 **必须**按原文运行 `okx-a2a user watch` / `okx-a2a user outdated-list。不要**附加 `| grep` / `| tail` / `| head` / `| awk` / `| sed` / `| jq` / shell 重定向。**两个命令都发出一个结构化的 JSON 文档——任何管道/截断都会破坏 JSON 并静默丢弃项目。如果输出看起来很嘈杂，带有 `[DEBUG]` 行，这些属于 stderr，永远不会影响 stdout 上的 JSON；不要“清理”stdout。管道=数据丢失。
- 🛑 **始终以前台方式运行 `okx-a2a user watch`。** 在 Claude Code 上，Bash 工具暴露了 `run_in_background` 参数——你**必须**用 `run_in_background: false`（默认值）调用 watch。将监控置于后台会破坏整个 dispatch 循环：stdout（带有项目的 JSON）不再同步返回到相同的工具调用，所以你无法通过 `kind` 分发、无法渲染 `userContent`、无法认领 `decision_request` 项目，甚至无法知道 watch 是否返回了任何内容。监控是一个单一的长轮询，必须阻塞本回合直到它返回；长轮询就是等待。如果你发现自己因为“watch 太慢”而使用 `run_in_background: true`，你正在误用该工具——这种等待是设计的。

  **如果监控已经意外进入后台**（意外的 `run_in_background: true`，或前台超时重新路由）：输出作为后台任务通知交付给你，你必须仍然将其传递给用户。完整恢复流程（定位输出文件 → 分发项目 → `TaskStop` → 前台重新启动）：见 [`references/background-recovery.md`](./references/background-recovery.md)。

## 根据 `kind` 分发

返回的项目始终是两种 `kind` 之一，完全不同地处理。

### `kind == notification` — 逐字粘贴，然后重新开始

**在通知项目上，你唯一的工作是粘贴其 `userContent` 并重新开始监控。别做别的。** 没有解释，没有摘要（包括“N 项，全部处理”之类的计数摘要），没有评论，没有问候语，没有标题，没有页脚，没有翻译正文内容。无论 `status` / `seen` / `handled` / `type` / 年龄如何，都渲染每个返回的项目——如果 watch 返回了它，就粘贴它。

**步骤 1 — 输出这个助手消息**（逐字符；将 `<userContent>` 替换为实际字段值，每行前缀 `> `）：

```
> <userContent>
```

这就是**整个**助手消息——不是一部分，全部。如果你发现自己准备写任何其他文本（前缀、后缀、标题、摘要、“这是最新的更新”），**停止，擦除，只输出引用块**。

**不要思考这个项目。** 没有 `<thinking>` 块，没有分析，没有推理，没有“这对用户意味着什么”。通知处理是**纯粹的机械**：从 JSON 中读取 `userContent` → 将每行前缀为 `> ` → 发出。然后调用 watch。这里没有什么需要解释的。

**步骤 2 — 重新开始监控。** 再次调用 `okx-a2a user watch --json`（如果适用，根据 §Session-scoped sticky 附加粘性 `--job-id <X>`）。

**多项目排序**——当 watch 返回 N 个通知时，按顺序逐个粘贴每个 `userContent` 作为自己的引用块（每个引用块占一行），然后运行一个重新开始调用。

> 💡 `notification` 项目由 `watch` 自动消费（破坏性读取——它们将不会出现在任何后续的 `watch` 调用中）。**不要**为通知调用 `okx-a2a user check --todo-ids …`；该命令仅用于 `decision_request` 项目。

### `kind == decision_request`

**在 `decision_request` 项目上，你的可见助手消息只有一个元素**：`userContent` 正文，逐字粘贴为 markdown 引用块。**别做别的**——没有前缀，没有后缀，没有自动生成的编号选项列表，没有对决策含义的评论，没有摘要，没有“请选择：”标题。`userContent` 已经自我文档化了用户应该如何回复（例如 `请回复：A / B / C`）；将其作为 `1. A / 2. B / 3. C / 4. 自定义回复` 反复输出是重复的，并引入 1 对 A 的歧义。

```
> <item.userContent>
```

如果你发现自己准备在引用块外写任何其他文本，**停止，擦除，只输出引用块**。

**不要在本回合中计划回复处理。** 没有 `<thinking>` 关于 `llmContent`，没有排练下一回合的步骤。这一回合纯粹是机械的：粘贴 `userContent` 作为引用块 → 安排 wake（如果适用，根据 §Schedule wake）→ 结束回合。`llmContent` 是用于**下一回合**的（在用户实际回复后——见 §处理用户回复）；在那时再重新阅读它，现在不是。
