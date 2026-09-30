---
name: himalaya
description: Himalaya CLI用于IMAP/SMTP邮件：列出、阅读、搜索、撰写、回复、转发、复制、移动、删除。
---

# 喜马拉雅

从 shell 使用 `himalaya` 进行 IMAP/SMTP 邮件。

## 参考

- `references/configuration.md`: 账户配置、认证、后端设置。
- `references/message-composition.md`: MML 组成语法。

## 设置

```bash
himalaya --version
himalaya account configure
```

配置路径: `~/.config/himalaya/config.toml`。

优先使用密码管理器/密钥环存储凭证；不要将密钥粘贴到聊天/日志中。

## 读取/搜索

```bash
himalaya folder list
himalaya envelope list
himalaya message read <id>
himalaya envelope list from alice@example.com subject invoice
```

## 写入

```bash
himalaya message write
himalaya template write
himalaya template send < /tmp/message.txt
himalaya message reply <id>
himalaya message forward <id>
```

使用 MML 处理附件和富文本消息；先阅读 `references/message-composition.md`。

## 组织

```bash
himalaya message copy <id> <folder>
himalaya message move <id> <folder>
himalaya message delete <id>
himalaya flag add <id> --flag seen
himalaya flag remove <id> --flag seen
```

## 注意事项

- 当存在多个账户时，使用 `--account`。
- 在摘要中精确引用消息 ID。
