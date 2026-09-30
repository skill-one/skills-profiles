---
name: recoup-platform-email-helper
description: 通过 Recoup API 以可靠的方式发送电子邮件——这是一个 Node.js 辅助工具，它可以正确序列化邮件正文，并在发送空邮件时发出明显的错误提示。每当需要向账户所有者或收件人发送报告/摘要/通知邮件时，请使用此脚本。始终使用此脚本发送邮件；切勿手动构建 `curl … -d "{…}"` 并使用内联 `jq`/shell 插值（这种方式会静默生成只有空“来自 Recoup 的消息”页脚的邮件）。它与 recoup-platform-api-access 配合使用（它会通过该接口发送）。
---

# 从任务中发送电子邮件

通过运行捆绑的 Node 脚本发送电子邮件 — **请勿**在 shell 中组装 JSON。

## 存在的原因

手动发送 (`curl -sS … -d "{… \"html\": $(echo "$HTML" | jq -R -s '.') …}"`) 是脆弱的：依赖于引号/转义，它会产生一个**格式不正确的正文**，并且使用的 API 会静默地发送一个标题为**"来自 Recoup 的消息"**且 `success:true` 的空页脚电子邮件。模型随机地对此出错。此脚本完全消除了 shell 序列化。

## 如何发送

1. 将电子邮件正文写入文件（推荐用于 HTML — 可避免所有转义问题）：

   ```bash
   cat > /tmp/report.html <<'HTML'
   <h1>每日报告</h1>
   <p>…你的实际内容…</p>
   HTML
   ```

2. 发送它：

   ```bash
   node "$SKILL_DIR/scripts/send-email.mjs" \
     --subject "每日报告 — $(date '+%B %d, %Y')" \
     --html-file /tmp/report.html \
     --to owner@example.com
   ```

`$SKILL_DIR` 是此技能的安装目录 (`~/.agents/skills/recoup-platform-email-helper`)；使用 `scripts/send-email.mjs` 的绝对路径。

## 标志

| 标志 | 含义 |
|------|---------|
| `--subject <s>` | 主题行（可选 — 如果省略，API 将从正文中派生一个）。 |
| `--html-file <path>` / `--html <s>` | HTML 正文。优先使用 `--html-file`。 |
| `--text-file <path>` / `--text <s>` | 纯文本正文。 |
| `--to <email>` | 收件人（可重复）。**省略以默认为账户自己的电子邮件**（"发邮件给我这个"）。 |
| `--cc <email>` | 抄送（可重复）。 |
| `--chat-id <id>` | 页脚 "继续对话" 链接的房间 ID。 |
| `--dry-run` | 序列化 + 验证并打印负载；**不发送**。用于预览。 |

## 规则

- **必须且仅有一个正文。** 如果没有非空的 `--html`/`--text`，脚本**拒绝发送**（退出码 2）。切勿尝试发送空电子邮件。
- **检查退出码。** 非零表示它**未发送** — 读取 stderr 并修复它；不要报告成功。脚本在实际发送时打印 Resend 消息 ID。
- 脚本从环境读取 `RECOUP_API_KEY` / `RECOUP_ACCESS_TOKEN` 和 `RECOUP_API_BASE` — 这些已在沙盒中设置。切勿打印或硬编码它们。
- 仅 Node（沙盒运行时为 `node22`；`python3` 不保证）。零依赖。
