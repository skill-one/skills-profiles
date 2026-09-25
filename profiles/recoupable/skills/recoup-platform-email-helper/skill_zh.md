# 从任务中发送邮件

通过运行捆绑的 Node 脚本发送邮件 — **请勿**在 shell 中组装 JSON。

## 存在的原因

手动发送 (`curl -sS … -d "{… \"html\": $(echo "$HTML" | jq -R -s '.') …}"`) 是脆弱的：依赖于引号/转义，它会产生一个**格式不正确的正文**，并且使用的 API 会静默地发送一个只有页脚的空邮件，标题为**"来自 Recoup 的消息"**，并带有 `success:true`。模型随机地对此出错。此脚本完全消除了 shell 序列化。

## 如何发送

1. 将邮件正文写入文件（推荐用于 HTML — 可避免所有转义问题）：

   ```bash
   cat > /tmp/report.html <<'HTML'
   <h1>每日报告</h1>
   <p>…你的实际内容…</p>
   HTML
   ```

2. 发送：

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
| `--subject <s>` | 主题行（可选 — 如果省略，API 会从正文中派生一个）。 |
| `--html-file <path>` / `--html <s>` | HTML 正文。优先使用 `--html-file`。 |
| `--text-file <path>` / `--text <s>` | 纯文本正文。 |
| `--to <email>` | 收件人（可重复）。**省略将默认为账户自己的邮箱**（"邮件通知我"）。 |
| `--cc <email>` | 抄送（可重复）。 |
| `--chat-id <id>` | 页脚 "继续对话" 链接的房间 ID。 |
| `--dry-run` | 序列化 + 验证并打印负载；**不发送**。用于预览。 |

## 规则

- **必须且仅有一个正文**。如果没有任何非空的 `--html`/`--text`，脚本**拒绝发送**（退出码 2）。切勿尝试发送空邮件。
- **检查退出码**。非零表示**未发送** — 读取 stderr 并修复；不要报告成功。脚本在实际发送时打印 Resend 消息 ID。
- 脚本从环境变量中读取 `RECOUP_API_KEY` / `RECOUP_ACCESS_TOKEN` 和 `RECOUP_API_BASE` — 这些已在沙盒中设置。切勿打印或硬编码它们。
- 仅 Node 环境（沙盒运行时为 `node22`；`python3` 不保证）。零依赖。
