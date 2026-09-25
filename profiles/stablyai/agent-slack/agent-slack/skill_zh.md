# agent-slack

使用 `$PATH` 中的 `agent-slack`。如果缺失，请使用以下命令安装：

```bash
curl -fsSL https://raw.githubusercontent.com/stablyai/agent-slack/main/install.sh | sh
```

备用方案：`npm i -g agent-slack` (Node >= 22.5)。

在猜测命令或标志之前，请运行 `agent-slack --help` 或相关子命令的帮助。

如果此处列出的某个功能在已安装的帮助中不存在，请报告版本差异，而不是猜测。未经明确授权，不要自行更新 CLI。

## 安全性

- 自由阅读和搜索。
- 仅在明确请求时执行写操作：发送、编辑、删除、反应、邀请、频道或画布的创建/编辑、标记已读操作、安排或取消发送、上传、Later 状态/提醒更改、创建/编辑 DM 或群组 DM，以及 `workflow run`。工作流运行可以执行下游操作。
- 对于仅用于编写或审阅的请求，无需调用 Slack 即返回建议文本，或使用 `message draft create` 向用户添加 Slack 原生草稿以供审阅和发送（不会发布）。`message compose` 具有发送功能；仅在用户明确要求打开交互式编辑器时使用它。在 CI 或其他非交互式环境中，未经单独授权发送立即调用它：CI 跳过编辑器并发送提供的文本。
- 设置 `AGENT_SLACK_SAFE_MODE=1`（或全局 `--safe-mode` 标志）时，在工具级别强制执行安全模式：`message send` 被重定向到草稿编辑器，`message edit`/`message delete` 被阻止。在无需人工审核即可发布任何内容时使用它。

## 工作流

1. 运行 `agent-slack auth whoami`。如有需要，使用 `auth import-desktop`、`auth import-brave`、`auth import-chrome` 或 `auth import-firefox` 导入凭据，然后运行 `auth test`。
2. 当可用时，优先使用 Slack 消息 URL。它包含大多数消息操作所需的工作区、频道和时间戳。
3. 选择最窄的读取操作：`message get` 用于一条消息，`message list` 用于完整线程或频道历史记录，以及 `search messages` 或 `search files` 用于发现。
4. 使用输出限制，如 `--limit`、`--max-body-chars` 和 `--max-content-chars`，以避免不必要的上下文。
5. 对于请求的写操作，仅执行请求的变更并验证结果的 JSON 元数据。

对于计划写操作，优先使用带 ISO 8601 时间戳和明确偏移量的 `--schedule`（当时区重要时）。命名 `--schedule-in` 短语使用执行环境的本地时区；确认它是否与用户的意图匹配。

命名 `later remind --in` 值，如 `tomorrow` 或 `monday`，也使用执行环境的本地时区在 9:00。确认时区或传递明确的 Unix 时间戳。

在 `message send` 或 `message compose` 中使用 `--no-unfurl` 时，如果用户希望抑制 Slack 链接和媒体预览。它不能与 `message send --attach` 结合使用。

普通的 `message send` 和 `message edit` 调用自动转换列表。`message send --blocks` 和 `message edit --blocks` 使用提供的 Block Kit 块，而 `message send --attach` 发送其初始评论而不自动转换列表。在自动转换的列表内，使用 Slack 的 `<URL|label>` 语法，因为 CommonMark `[label](URL)` 链接不会被转换为带标签的链接元素。

Slack 原生草稿 (`message draft list|create|update|delete`) 管理出现在用户 Slack 客户端的草稿；`create` 不会发布任何内容。`create` 和 `update` 接受可重复的 `--attach <path>`；在 `update` 中，文件被添加到草稿的现有附件中，而不是替换它们。它们使用未公开的会话端点，并需要浏览器风格的认证 (xoxc/xoxd)。

`canvas edit` 使用 Slack 的公共 `canvases.edit` API，并且每次调用仅应用一个操作。默认的 `replace` 操作替换整个画布；针对部分目标的插入/替换和删除需要 Slack 画布工具返回的部分 ID，而 `rename` 需要 `--title`。内容操作需要恰好一个 `--file` 或 `--markdown` 源。它需要一个标准 `canvases:write` 令牌；导入的浏览器凭据可以创建独立的画布，但不能编辑。

## 条件引用

- 仅在以下情况下阅读 [references/targets.md](references/targets.md)：在消息 URL、频道或用户目标之间选择，或解析多个工作区时。
- 仅在处理返回的消息或画布元数据、解析用户或下载并失败的附件时阅读 [references/output.md](references/output.md)。
