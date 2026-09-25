# Apple Reminders 命令行工具 (remindctl)

使用 `remindctl` 直接从终端管理 Apple Reminders。

## 何时使用

在以下情况使用：

- 用户明确提到 "提醒" 或 "Reminders 应用"
- 创建带有截止日期的个人待办事项，并同步到 iOS
- 管理Apple Reminders 列表
- 用户希望任务出现在他们的 iPhone/iPad Reminders 应用中

## 何时不用

在以下情况不要使用：

- 安排 OpenClaw 任务或提醒 -> 使用 `cron` 工具配合 systemEvent
- 日历事件或预约 -> 使用 Apple 日历
- 项目/工作任务管理 -> 使用 Notion、GitHub Issues 或任务队列
- 一次性通知 -> 使用 `cron` 工具进行定时提醒
- 用户说 "提醒我" 但实际是指 OpenClaw 提醒 -> 先进行澄清

## 安装

- 安装：`brew install steipete/tap/remindctl`
- 仅限 macOS；在提示时授予 Reminders 权限
- 检查状态：`remindctl status`
- 请求访问：`remindctl authorize`

## 常用命令

### 查看提醒事项

```bash
remindctl                    # 今日提醒事项
remindctl today              # 今日
remindctl tomorrow           # 明日
remindctl week               # 本周
remindctl overdue            # 过期
remindctl all                # 所有事项
remindctl 2026-01-04         # 指定日期
```

### 管理列表

```bash
remindctl list               # 列出所有列表
remindctl list Work          # 显示特定列表
remindctl list Projects --create    # 创建列表
remindctl list Work --delete        # 删除列表
```

### 创建提醒事项

```bash
remindctl add "买牛奶"
remindctl add --title "给妈妈打电话" --list 个人 --due 明日
remindctl add --title "会议准备" --due "2026-02-15 09:00"
```

### 完成/删除

```bash
remindctl complete 1 2 3     # 通过 ID 完成
remindctl delete 4A83 --force  # 通过 ID 删除
```

### 输出格式

```bash
remindctl today --json       # 脚本用的 JSON 格式
remindctl today --plain      # TSV 格式
remindctl today --quiet      # 仅统计数量
```

## 日期格式

`--due` 和日期筛选器接受的格式：

- `today`, `tomorrow`, `yesterday`
- `YYYY-MM-DD`
- `YYYY-MM-DD HH:mm`
- ISO 8601 (`2026-01-04T12:34:56Z`)

## 示例：澄清用户意图

用户："两小时后提醒我检查部署情况"

**询问：** "您希望这是在 Apple Reminders（同步到您的手机）中，还是作为 OpenClaw 提醒（我会在这里消息您）？"

- Apple Reminders -> 使用此技能
- OpenClaw 提醒 -> 使用 `cron` 工具配合 systemEvent
