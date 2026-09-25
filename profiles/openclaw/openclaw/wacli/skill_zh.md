# wacli

仅当用户明确要求您在 WhatsApp 上向他人发送消息或要求同步/搜索 WhatsApp 历史记录时，才使用 `wacli`。
不要使用 `wacli` 进行普通用户聊天；OpenClaw 会自动路由 WhatsApp 对话。
如果用户正在 WhatsApp 上与您聊天，除非他们要求您联系第三方，否则不应使用此工具。

安全

- 需要明确的收件人 + 消息文本。
- 发送前确认收件人 + 消息。
- 如果有任何模糊之处，请提出澄清问题。

认证 + 同步

- `wacli auth` (QR 登录 + 初始同步)
- `wacli sync --follow` (持续同步)
- `wacli doctor`

查找聊天 + 消息

- `wacli chats list --limit 20 --query "姓名或号码"`
- `wacli messages search "查询内容" --limit 20 --chat <jid>`
- `wacli messages search "发票" --after 2025-01-01 --before 2025-12-31`

检查 / 验证消息

- `wacli messages show --chat <jid> --id <消息ID> --json --full`
- `messages show` 需要 `--chat` 和 `--id`；不要将消息 ID 作为位置参数传递。
- 发送后，在精确格式很重要时（尤其是多行文本）验证存储的消息。

历史记录补录

- `wacli history backfill --chat <jid> --requests 2 --count 50`

发送

- 文本：`wacli send text --to "+14155551212" --message "你好！你下午三点有空吗？"`
- 群组：`wacli send text --to "1234567890-123456789@g.us" --message "晚五分钟。"`
- 文件：`wacli send file --to "+14155551212" --file /path/日程.pdf --caption "日程"`
- 多行：`--message` 默认为字面值；传递 `--message-escapes` 以解释 `\n`、`\r`、`\t`。

备注

- 存储目录：`~/.wacli`（使用 `--store` 覆盖）。
- 解析时使用 `--json` 获取机器可读输出。
- 补录需要您的手机在线；结果尽力而为。
- 常规用户聊天不需要 WhatsApp CLI；它是用于联系其他人的。
- JIDs：直接聊天看起来像 `<号码>@s.whatsapp.net`；群组看起来像 `<ID>@g.us`（使用 `wacli chats list` 查找）。
