# Gmail 技能 - 邮件与联系人访问

读取、搜索和发送 Gmail 邮件。访问 Google 联系人。

## 关键：邮件发送确认要求

**在发送任何邮件之前，你必须获得用户的明确确认。**

当用户要求发送邮件时：
1. 首先，向他们展示完整的邮件详情：
   - 发件人（哪个账户）
   - 收件人
   - 抄送/密送（如有）
   - 主题
   - 完整正文内容
2. 询问："你想让我发送这封邮件吗？"
3. 仅在用户明确确认后（例如："是"、"发送它"、"继续"）才运行发送命令
4. 即使用户最初要求你发送邮件，也绝对不能在没有确认的情况下发送邮件

即使出现以下情况，也适用：
- 用户说"发送一封给 X 的邮件"
- 你处于"危险地跳过权限"模式
- 用户看起来很匆忙

始终先确认。没有例外。

## 首次设置（一次性，约 2 分钟）

首次运行时，脚本将引导你完成设置。你需要创建一个 Google Cloud OAuth 客户端一次：

1. 前往 [Google Cloud 控制台](https://console.cloud.google.com/apis/credentials)
2. 创建项目（或选择现有项目）
3. 启用 **Gmail API** 和 **People API**（APIs & Services → Library）
4. 配置 OAuth 同意屏幕：
   - 用户类型：外部
   - 应用名称：Gmail 技能
   - 添加自己为测试用户
   - 添加范围：`gmail.readonly`、`gmail.send`、`gmail.modify`、`contacts.readonly`
5. 创建 OAuth 客户端 ID：
   - 应用类型：**桌面应用**
   - 下载 JSON → 保存为 `~/.claude/skills/gmail-skill/credentials.json`

然后只需运行任何命令 - 浏览器打开，你批准，完成。适用于所有你的账户。

**注意：** 如果你之前使用过 gmail-reader，你需要重新认证以授予新的 `gmail.send` 范围。

## 命令

### 搜索邮件

```bash
python3 ~/.claude/skills/gmail-skill/gmail_skill.py search "查询" [--max-results N] [--account EMAIL]
```

**查询示例：**
- `from:john@example.com` - 来自特定发件人
- `subject:meeting after:2026/01/01` - 主题 + 日期
- `has:attachment filename:pdf` - 带有 PDF 附件
- `is:unread` - 未读邮件
- `"确切的短语"` - 精确匹配

### 读取邮件

```bash
python3 ~/.claude/skills/gmail-skill/gmail_skill.py read EMAIL_ID [--account EMAIL]
```

### 列出最近邮件

```bash
python3 ~/.claude/skills/gmail-skill/gmail_skill.py list [--max-results N] [--label LABEL] [--account EMAIL]
```

### 发送邮件（需要确认）

```bash
python3 ~/.claude/skills/gmail-skill/gmail_skill.py send --to EMAIL --subject "主题" --body "邮件正文" [--cc EMAIL] [--bcc EMAIL] [--account EMAIL]
```

**必需参数：**
- `--to` / `-t` - 收件人电子邮件地址
- `--subject` / `-s` - 邮件主题行
- `--body` / `-b` - 邮件正文

**可选参数：**
- `--cc` - 抄送收件人（逗号分隔）
- `--bcc` - 密送收件人（逗号分隔）
- `--account` / `-a` - 从特定账户发送

**示例：**
```bash
python3 ~/.claude/skills/gmail-skill/gmail_skill.py send \
  --to "recipient@example.com" \
  --subject "明天开会" \
  --body "嗨，确认一下我们明天 2 点的会议。" \
  --account work@company.com
```

### 标记为已读

```bash
python3 ~/.claude/skills/gmail-skill/gmail_skill.py mark-read EMAIL_ID [--account EMAIL]
```

### 标记为未读

```bash
python3 ~/.claude/skills/gmail-skill/gmail_skill.py mark-unread EMAIL_ID [--account EMAIL]
```

`mark-read` 和 `mark-unread` 都支持多个 ID（逗号分隔）：
```bash
python3 ~/.claude/skills/gmail-skill/gmail_skill.py mark-read "id1,id2,id3" --account user@gmail.com
```

### 标记完成（归档）

通过从收件箱中移除邮件来归档邮件。相当于 Gmail 的 'e' 键盘快捷键。

```bash
python3 ~/.claude/skills/gmail-skill/gmail_skill.py mark-done EMAIL_ID [--account EMAIL]
```

### 取消归档

将邮件移回收件箱（撤销归档）。

```bash
python3 ~/.claude/skills/gmail-skill/gmail_skill.py unarchive EMAIL_ID [--account EMAIL]
```

### 星标 / 取消星标

```bash
python3 ~/.claude/skills/gmail-skill/gmail_skill.py star EMAIL_ID [--account EMAIL]
python3 ~/.claude/skills/gmail-skill/gmail_skill.py unstar EMAIL_ID [--account EMAIL]
```

所有标签命令都支持多个 ID（逗号分隔）：
```bash
python3 ~/.claude/skills/gmail-skill/gmail_skill.py star "id1,id2,id3" --account user@gmail.com
```

### 创建草稿

创建草稿邮件。使用 `--reply-to-id` 回复现有邮件时，确保在 Superhuman 等邮件客户端中正确显示线程。

```bash
python3 ~/.claude/skills/gmail-skill/gmail_skill.py draft --to EMAIL --subject "主题" --body "邮件正文" [--reply-to-id EMAIL_ID] [--cc EMAIL] [--bcc EMAIL] [--account EMAIL]
```

**必需参数：**
- `--to` / `-t` - 收件人电子邮件地址
- `--subject` / `-s` - 邮件主题行
- `--body` / `-b` - 邮件正文

**可选参数：**
- `--reply-to-id` / `-r` - 回复的消息 ID（添加正确的 In-Reply-To 和 References 标头以显示线程）
- `--cc` - 抄送收件人（逗号分隔）
- `--bcc` - 密送收件人（逗号分隔）
- `--account` / `-a` - 在特定账户中创建草稿

**示例（新邮件）：**
```bash
python3 ~/.claude/skills/gmail-skill/gmail_skill.py draft \
  --to "recipient@example.com" \
  --subject "待审草稿" \
  --body "这是我的草稿消息。"
```

**示例（回复现有邮件）：**
```bash
python3 ~/.claude/skills/gmail-skill/gmail_skill.py draft \
  --to "sender@example.com" \
  --subject "Re: 原始主题" \
  --body "谢谢你的邮件..." \
  --reply-to-id 19b99b3127793843 \
  --account work@company.com
```

### 列出标签

```bash
python3 ~/.claude/skills/gmail-skill/gmail_skill.py labels [--account EMAIL]
```

### 列出联系人

```bash
python3 ~/.claude/skills/gmail-skill/gmail_skill.py contacts [--max-results N] [--account EMAIL]
```

### 搜索联系人

```bash
python3 ~/.claude/skills/gmail-skill/gmail_skill.py search-contacts "查询" [--account EMAIL]
```

### 管理账户

```bash
# 列出所有已认证的账户
python3 ~/.claude/skills/gmail-skill/gmail_skill.py accounts

# 移除账户
python3 ~/.claude/skills/gmail-skill/gmail_skill.py logout --account user@gmail.com
```

## 多账户支持

使用 `--account` 与新邮件添加账户 - 浏览器将打开该账户：

```bash
# 第一个账户（自动认证）
python3 ~/.claude/skills/gmail-skill/gmail_skill.py list

# 添加工作账户
python3 ~/.claude/skills/gmail-skill/gmail_skill.py list --account work@company.com

# 添加个人账户
python3 ~/.claude/skills/gmail-skill/gmail_skill.py list --account personal@gmail.com

# 使用特定账户
python3 ~/.claude/skills/gmail-skill/gmail_skill.py search "from:boss" --account work@company.com
```

令牌按账户存储在 `~/.claude/skills/gmail-skill/tokens/`

## 示例

### 查找本周未读邮件

```bash
python3 ~/.claude/skills/gmail-skill/gmail_skill.py search "is:unread after:2026/01/01"
```

### 读取特定邮件

```bash
python3 ~/.claude/skills/gmail-skill/gmail_skill.py read 18d5a3b2c1f4e5d6
```

### 快速发送邮件

```bash
python3 ~/.claude/skills/gmail-skill/gmail_skill.py send \
  --to "friend@example.com" \
  --subject "你好！" \
  --body "只是想打个招呼。"
```

### 查找某人的联系人信息

```bash
python3 ~/.claude/skills/gmail-skill/gmail_skill.py search-contacts "John Smith"
```

### 在个人设备上检查工作邮件

```bash
python3 ~/.claude/skills/gmail-skill/gmail_skill.py list --account work@company.com --max-results 5
```

## 输出

所有命令输出 JSON 以便于解析。

## 要求

- Python 3.9+
- `pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client requests`

## 安全提示

- **发送确认要求** - Claude 必须在发送邮件前始终与用户确认
- 令牌本地存储在 `~/.claude/skills/gmail-skill/tokens/`
- 随时撤销访问权限：https://myaccount.google.com/permissions
- 测试模式中的应用可能需要每 7 天重新认证（发布应用以避免）
