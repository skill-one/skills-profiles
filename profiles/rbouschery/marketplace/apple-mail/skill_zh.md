# Apple Mail 技能

该技能提供通过 AppleScript 在 macOS 上与 Apple Mail 交互的命令。

## 可用脚本

所有脚本位于 `../../scripts/` 目录（相对于此文件）。从插件根目录通过 bash 执行它们。

### 账户与邮箱管理

| 脚本 | 目的 | 参数 |
|------|------|------|
| `list-accounts.sh` | 列出所有邮箱账户 | 无 |
| `list-mailboxes.sh` | 列出邮箱/文件夹 | `[account]`（可选） |
| `get-unread-count.sh` | 获取未读邮件数量 | `[account] [mailbox]`（可选） |

### 阅读邮件

| 脚本 | 目的 | 参数 |
|------|------|------|
| `get-emails.sh` | 获取最新邮件 | `[account] [mailbox] [limit] [include_content] [unread_only]` |
| `get-email-by-id.sh` | 通过 ID 获取特定邮件 | `<id> [account] [mailbox] [include_content]` |
| `search-emails.sh` | 搜索邮件 | `<query> [account] [mailbox] [limit]` |

### 发送与撰写

| 脚本 | 目的 | 参数 |
|------|------|------|
| `send-email.sh` | 发送邮件 | `<to> <subject> <body> [cc] [bcc] [from]` |
| `create-draft.sh` | 创建草稿邮件 | `<subject> <body> [to] [cc] [bcc] [from]` |
| `create-reply-draft.sh` | 创建回复邮件 | `<message_id> <body> [reply_all] [account] [mailbox]` |
| `send-draft.sh` | 发送最前方的草稿 | 无 |

### 邮件管理

| 脚本 | 目的 | 参数 |
|------|------|------|
| `archive-email.sh` | 归档邮件 | `<message_id> [account] [mailbox] [archive_mailbox]` |
| `delete-email.sh` | 删除邮件 | `<message_id> [account] [mailbox]` |
| `mark-read.sh` | 标记邮件为已读 | `<message_id> [account] [mailbox]` |
| `mark-unread.sh` | 标记邮件为未读 | `<message_id> [account] [mailbox]` |

## 输出格式

脚本使用分隔符进行结构化输出：
- `<<>>` 分隔记录内的字段
- `|||` 分隔多个记录
- `ERROR:` 前缀表示错误消息

### 邮件记录格式

```
id<<>>subject<<>>sender<<>>to<<>>cc<<>>bcc<<>>dateSent<<>>isRead<<>>content|||
```

## 使用示例

### 列出账户
```bash
./scripts/list-accounts.sh
```

### 从 INBOX 获取最新邮件
```bash
./scripts/get-emails.sh "" "INBOX" 10 false false
```

### 获取最新未读邮件并包含内容
```bash
./scripts/get-emails.sh "" "INBOX" 10 true true
```

### 通过 ID 获取特定邮件
```bash
./scripts/get-email-by-id.sh 12345 "iCloud" "INBOX" true
```

### 搜索邮件
```bash
./scripts/search-emails.sh "meeting notes" "" "" 20
```

### 发送邮件
```bash
./scripts/send-email.sh "recipient@example.com" "Subject" "Body text"
```

### 发送带 CC 和 BCC
```bash
./scripts/send-email.sh "to@example.com" "Subject" "Body" "cc@example.com" "bcc@example.com"
```

### 创建草稿
```bash
./scripts/create-draft.sh "Draft Subject" "Draft body" "recipient@example.com"
```

### 回复邮件
```bash
./scripts/create-reply-draft.sh 12345 "Thanks for your message!" false "iCloud" "INBOX"
```

### 发送最前方的草稿
```bash
./scripts/send-draft.sh
```

### 归档邮件
```bash
./scripts/archive-email.sh 12345 "iCloud" "INBOX"
```

### 标记为已读/未读
```bash
./scripts/mark-read.sh 12345 "iCloud" "INBOX"
./scripts/mark-unread.sh 12345 "iCloud" "INBOX"
```

## 解析输出

接收邮件记录时，按以下方式解析：

1. 按 `|||` 分割以获取单个记录
2. 按 `<<>>` 分割每个记录以获取字段
3. 字段为：id, subject, sender, to, cc, bcc, dateSent, isRead, content

bash 中解析示例：
```bash
IFS='|||' read -ra emails <<< "$output"
for email in "${emails[@]}"; do
    IFS='<<>>' read -ra fields <<< "$email"
    id="${fields[0]}"
    subject="${fields[1]}"
    sender="${fields[2]}"
    # ... 等
done
```

## 注意事项

- 脚本需要 macOS 且已配置 Apple Mail
- Apple Mail 必须至少设置一个账户
- 首次运行可能触发 macOS 自动化权限提示
- 空的可选参数应传递为空字符串 ""
- 对于需要数组的脚本（多个收件人），传递逗号分隔值

## 参考

有关高级 AppleScript 模式和自定义，请参阅 `./reference/applescript-patterns.md`。
