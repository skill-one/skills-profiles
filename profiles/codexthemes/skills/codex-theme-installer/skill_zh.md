# 从 CodexThemes 安装 Codex 主题

从 codexthemes.ai 下载已发布的主题的可移植包，并将其源文件解压到 `~/.codexthemes/themes/<theme-id>/`。这个技能是独立的：它的 TypeScript 脚本负责下载、验证和本地安装。它不会搜索画廊（codex-theme-finder）、创建主题（codex-theme-creator）或提交主题（codex-theme-submitter）。应用属于 codex-theme-switcher — 但成功的安装会直接链入它（步骤 4）；安装文件和停止并不是一个完成的任务。唯一需要的本地工具是 Node.js 20+ 和 `npx`。

在诊断意外的 API 响应或更改端点行为之前，请阅读 `references/download-api.md`。从已安装的技能目录中运行所有命令。

## 步骤 1：确定主题

将安装内容解析为主题 ID — 来自 codex-theme-finder 结果的 lowercase slug 或来自 `https://codexthemes.ai/themes/<theme-id>` URL 的主题 ID。脚本接受这两种形式。如果用户仅描述了风格而没有命名主题，应先使用 codex-theme-finder 找到候选主题，而不是猜测 ID。

## 步骤 2：安装

```bash
npx tsx scripts/install-theme.ts <theme-id | codexthemes.ai 主题 URL> [--force]
```

在没有 API 密钥的情况下，下载工作可以在免费匿名配额内完成，因此不要一开始就要求提供密钥。当密钥已配置（`CODEXTHEMES_API_KEY` 环境变量或 `~/.codexthemes/credentials.json`）时，脚本会自动发送它以获得更高的配额限制。

在写入任何内容之前，脚本会验证下载的包（格式、模式版本、匹配的主题 ID、安全的相对文件名、≤30 MB），然后将 `theme.json`、样式表、艺术作品和自述文件解压到 `~/.codexthemes/themes/<theme-id>/`。它拒绝覆盖现有的非空主题目录；只有在用户确认替换本地副本后，才传递 `--force` — 目录可能包含他们自己的修改。

**更新已安装的主题**：已发布的主题在 codexthemes.ai 上原地更新，因此当用户要求更新、升级或重新下载他们已安装的主题时，使用 `--force` 重新运行安装 — 更新请求本身就是确认，除非本地副本包含用户所做的修改（则先发出警告）。文件到达后，继续进入步骤 4，以便正在运行的应用程序实际切换到新版本；相同主题 ID 的热交换会重新注入更新的 CSS。

## 步骤 3：处理配额和速率限制

在 HTTP `429` 或 `402` 时，免费配额已用尽；脚本错误消息中包含任何 `Retry-After` 值。不要在循环中重试。告诉用户免费下载配额已用尽，并指导他们配置个人 API 密钥：

1. 在 `https://codexthemes.ai/settings/apikeys` 创建密钥。
2. 存储它：`printf '%s' "<api-key>" | npx tsx scripts/apikey.ts set`（stdin 将密钥保留在 shell 历史记录之外；`apikey.ts set <key>` 也适用）。
3. 重新运行安装。

使用 `npx tsx scripts/apikey.ts status` 检查当前密钥状态；使用 `npx tsx scripts/apikey.ts clear` 删除存储的密钥。永远不要打印完整的密钥（脚本仅显示掩码形式），永远不要将其写入项目文件，也永远不要提交它。

在 `401`/`403` 时，配置的密钥无效或被吊销 — 指导用户以相同方式创建新密钥。在 `404` 时，主题 ID 不存在；使用 codex-theme-finder 重新检查 ID。

## 步骤 4：激活，或直接给出用户确切的下一步回复

安装请求意味着用户希望在 Codex 中看到主题，而不仅仅是存储其文件。报告安装路径（`~/.codexthemes/themes/<theme-id>/`）、主题版本和写入的文件 — 然后直接进入 codex-theme-switcher 的激活。如果 codex-theme-switcher 未安装，则使用与启动此技能相同的方式启动它（`npx skills add codexthemes/skills --skill codex-theme-switcher -g -a codex`）。

- 如果 Codex 已公开其调试端点，现在使用 switcher 的 `switch-theme.ts apply <theme-id>` 进行热交换，并使用 `switch-theme.ts status` 进行验证 — 热交换是可逆的，除了安装请求本身，不需要其他确认。
- 如果激活需要重启 Codex，不要静默重启，也不要在“已安装”时停止。以告诉用户确切的回复来结束，例如：“回复 `apply`，我将重启 Codex 以激活 `<theme-id>`。” 当他们回复时，遵循 switcher 的 `--launch` 流程。

永远不要以“文件已安装，未应用”且没有可操作的下一步来结束对话，并且直到 switcher 的 `status` 报告 `active` 为止，永远不要声称主题已激活。
