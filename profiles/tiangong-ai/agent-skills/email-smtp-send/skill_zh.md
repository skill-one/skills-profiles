# 通过 SMTP 发送邮件

## 核心目标
- 使用环境配置的凭据通过 SMTP 发送外发邮件。
- 在需要时将本地文件附加到 MIME 邮件负载中。
- 可选地将发送的消息追加到 IMAP 已发送邮箱以实现跨客户端可见性。
- 在交付前验证 SMTP 和已发送同步配置。
- 返回机器可读的 JSON 状态/错误输出。

## 工作流程
1. 配置 SMTP 环境变量（参考 `references/env.md` 和 `assets/config.example.env`）。
2. 可选：配置 IMAP 已发送同步环境变量，并在启用同步时安装 `imapclient`。
3. 验证配置：

```bash
python3 scripts/smtp_send.py check-config
```

4. 发送一封邮件：

```bash
python3 scripts/smtp_send.py send \
  --to recipient@example.com \
  --subject "SMTP 测试" \
  --body "来自 email-smtp-send 的问候"
```

5. 发送带附件的邮件：

```bash
python3 scripts/smtp_send.py send \
  --to recipient@example.com \
  --subject "包裹交付" \
  --body "请查看附件。" \
  --attach ./report.pdf \
  --attach ./appendix.xlsx
```

6. 发送并同步到已发送邮箱：

```bash
python3 scripts/smtp_send.py send \
  --to recipient@example.com \
  --subject "同步发送" \
  --body "此消息将被追加到已发送项目。" \
  --sync-sent \
  --sent-mailbox "已发送项目"
```

## 输出契约
- `check-config` 打印经过清理的 SMTP 配置 + 默认值 + 已发送同步配置的 JSON。
- `send` 成功打印一个 `type=status` JSON 对象，包含：
  - `event=smtp_sent`
  - 发件人、收件人摘要、主题、SMTP 主机/端口
  - `message_id`
  - `attachment_count` 和 `attachments[]` 元数据
  - `sent_sync` 对象，包含 `enabled`、`required`、`appended` 和同步元数据/错误
- `send` 失败打印 `type=error` JSON 到 stderr，包含以下之一：
  - `event=smtp_send_invalid_args`
  - `event=smtp_send_failed`
  - `event=smtp_sent_sync_failed`（仅当同步为必需且同步失败时）

## 参数
- `send --to`：必需的收件人，可重复或逗号分隔。
- `send --cc`：可选的抄送收件人。
- `send --bcc`：可选的密送收件人。
- `send --subject`：可选的主题（默认从环境变量获取）。
- `send --body`：可选的正文（默认从环境变量获取）。
- `send --content-type`：`plain` 或 `html`。
- `send --from`：可选的发送者覆盖。
- `send --attach`：可选的本地附件路径，可重复或逗号分隔。
- `send --max-attachment-bytes`：每个附件允许的最大字节数。
- `send --message-id`：可选的 Message-ID 头。
- `send --in-reply-to`：可选的 In-Reply-To 头。
- `send --references`：可选的 References 头。
- `send --sync-sent|--no-sync-sent`：强制启用/禁用本次发送的 IMAP 已发送同步。
- `send --sent-mailbox`：覆盖已发送邮箱。
- `send --sent-flags`：IMAP APPEND 标志，逗号分隔（默认 `\Seen`）。
- `send --sent-sync-required`：如果 SMTP 成功但已发送同步失败，则返回非零值。

环境默认值：
- `SMTP_HOST`, `SMTP_PORT`, `SMTP_SSL`, `SMTP_STARTTLS`
- `SMTP_USERNAME`, `SMTP_PASSWORD`, `SMTP_FROM`, `SMTP_CONNECT_TIMEOUT`
- `SMTP_SUBJECT`, `SMTP_BODY`, `SMTP_CONTENT_TYPE`
- `SMTP_MAX_ATTACHMENT_BYTES`
- `SMTP_SYNC_SENT`, `SMTP_SYNC_SENT_REQUIRED`
- `SMTP_SENT_IMAP_HOST`, `SMTP_SENT_IMAP_PORT`, `SMTP_SENT_IMAP_SSL`
- `SMTP_SENT_IMAP_USERNAME`, `SMTP_SENT_IMAP_PASSWORD`
- `SMTP_SENT_IMAP_MAILBOX`, `SMTP_SENT_IMAP_FLAGS`, `SMTP_SENT_IMAP_CONNECT_TIMEOUT`
- 兼容性回退：`IMAP_HOST`, `IMAP_PORT`, `IMAP_SSL`, `IMAP_USERNAME`, `IMAP_PASSWORD`, `IMAP_CONNECT_TIMEOUT`

## 依赖
- 已发送同步模式需要 `imapclient`：

```bash
python3 -m pip install imapclient
```

## 错误处理
- 无效的环境配置退出码为 `2`。
- 发送失败退出码为 `1`。
- 如果同步为必需 (`--sent-sync-required` 或 `SMTP_SYNC_SENT_REQUIRED=true`)，同步失败退出码为 `1`。

## 参考
- `references/env.md`

## 资产
- `assets/config.example.env`

## 脚本
- `scripts/smtp_send.py`
