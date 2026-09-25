# imsg

首先使用通用的 `message` 工具处理其当前 iMessage 模式所暴露的操作。当任务需要本地 Messages.app 历史记录、目标发现、监视或 `message` 未暴露的管理员/私有-API 功能时，使用 `imsg`。

不要使用此技能处理 Telegram、Signal、WhatsApp、Discord、Slack，或在配置的频道已路由回复时，在当前 OpenClaw 对话内回复。

## 代理流程

1. 首先解析对话。
2. 选择 DM、现有群组或新建群组。
3. 优先选择可用的 `message` 操作；否则选择保留请求语义的最低能力 `imsg` 命令。
4. 除非用户已给出确切接收者、内容和操作，否则确认发送或可见状态变化。
5. 使用稳定标识符执行：正常发送/监视/历史记录优先使用 `--chat-id`，桥接操作使用 `--chat` chat GUID。

当多个聊天或用户名可能匹配时，切勿仅凭随意名称推断接收者。在发送前，显示匹配的显示名称、用户名、群组成员和消息文本/操作。

## 主机要求

- macOS 14+ 且 Messages.app 已登录，用于发送/反应/桥接操作。
- 强烈建议 OpenClaw iMessage 使用私有 API 模式。它解锁回复、精确的轻点回复、效果、投票、附件回复、已读/输入操作和群组管理。基本模式是读取和纯文本/文件发送的回退。
- `imsg` 或 OpenClaw 运行进程需要完整磁盘访问权限；没有 Messages DB 访问，读取会失败。
- 使用公共 `send` 时，Messages.app 需要自动化权限。
- 运行公共 `imsg react` 的进程上下文需要辅助功能权限；它使用 System Events UI 自动化。桥接 `tapback` 使用私有 API。
- 可选的联系人权限用于联系人名称解析。
- 发送 SMS 需要用户 iPhone 到此 Mac 的短信转发。
- Linux 仅读取复制的 `chat.db`；它不能发送、反应、启动 Messages.app、标记已读或输入。

## 解析目标

使用 `--json` 读取。输出为行分隔的 JSON；当 `jq` 可用时，使用 `jq -s`，或直接逐行消费对象。

```bash
imsg chats --limit 25 --json | jq -s
imsg search --query "dinner" --match contains --json | jq -s
imsg history --chat-id 42 --limit 20 --attachments --json | jq -s
imsg group --chat-id 42 --json
```

目标规则：

- DM 至手机/邮箱：用户给出确切用户名后，或单次明确聊天匹配后，使用 `imsg send --to`。
- 现有 DM 线程：`imsg send --chat-id <id>` 比重新解析名称更安全。
- 现有群组：使用 `imsg group --chat-id <id> --json` 检查；使用 `--chat-id` 发送，桥接使用 `group` 中的群组 GUID。
- 新建群组：仅在用户明确要求创建群组或没有现有群组匹配时使用 `chat-create`。
- 模糊群组名称：确认参与者，而不仅仅是显示名称。
- SMS：仅在请求或不想使用 iMessage 回退时使用 `--service sms`。SMS 中继需要短信转发。

不要将 `jq` 设为技能的硬性前提；它仅是示例的便捷格式化工具。

## 能力选择

当当前 `message` 模式不覆盖操作或需要本地历史记录时，使用 `imsg` 标准命令：

- 读取/列表/搜索/监视：`chats`、`group`、`history`、`search`、`watch`
- 基本文本/文件发送：`send`
- 向聊天中最新的消息发送标准轻点回复：`react`

使用私有 API 桥接执行 OpenClaw 用户通常期望的原生 iMessage 操作：

- 富回复、文本格式化、效果、主题、多部分发送
- 原生 Apple Messages 投票和投票
- 通过消息 GUID 或移除轻点回复
- 编辑、撤回、删除、无论如何通知
- 已读回执、输入指示器、桥接事件监视
- 群组创建/命名/照片/成员/离开/删除/标记操作
- 账户、whois、昵称检查

对于 OpenClaw 频道设置，尽早检查桥接可用性：

```bash
imsg status --json
```

如果主机支持桥接操作但 Messages 尚未注入，运行 `imsg launch` 前询问。它会杀死并重新启动 Messages.app 以注入桥接，因此将其视为可见状态变化：

```bash
imsg launch
imsg status --json
```

如果系统完整性保护、库验证、私有权限检查或缺失选择器仍阻止功能，解释该主机无法提供请求的私有-API 操作，并尽可能提供最接近的非桥接操作。不要将线程回复、效果、主题、投票或 GUID 目标的轻点回复降级为普通发送/反应。

## DM 场景

确切用户名，基本发送：

```bash
imsg send --to "+14155551212" --text "On my way" --service auto
```

已知 DM 线程：

```bash
imsg send --chat-id 42 --text "On my way"
imsg send --chat-id 42 --file /path/to/photo.jpg
```

仅在用户要求时强制频道：

```bash
imsg send --to "+14155551212" --text "green bubble" --service sms
imsg send --to "+14155551212" --text "iMessage only" --service imessage --no-sms-fallback
```

线程回复、格式化、效果或附件回复：

```bash
imsg send-rich --chat 'iMessage;-;+15551234567' \
  --reply-to <message-guid> --text "reply text"
imsg send-rich --chat 'iMessage;-;+15551234567' --text 'hello world' \
  --format '[{"start":0,"length":5,"styles":["bold"]}]'
imsg send-rich --chat 'iMessage;-;+15551234567' --text "boom" --effect impact
imsg send-attachment --chat 'iMessage;-;+15551234567' \
  --reply-to <message-guid> --file /path/to/file.jpg
```

格式化范围是 UTF-16 位置。支持的风格包括 `bold`、`italic`、`underline` 和 `strikethrough`；使用 `--format-file` 生成 JSON。

## 群组场景

行动前检查：

```bash
imsg group --chat-id 42 --json
imsg history --chat-id 42 --limit 20 --json | jq -s
```

向现有群组发送：

```bash
imsg send --chat-id 42 --text "Works for me"
```

在现有群组中桥接回复或投票：

```bash
imsg send-rich --chat 'iMessage;+;chat0000' \
  --reply-to <message-guid> --text "replying in thread"
imsg poll send --chat 'iMessage;+;chat0000' \
  --question "Dinner?" --option "Pizza" --option "Sushi"
```

仅在明确请求时创建或修改群组：

```bash
imsg chat-create --addresses '+15551111111,+15552222222' --name 'Crew' --text 'gm'
imsg chat-name --chat 'iMessage;+;chat0000' --name 'Renamed'
imsg chat-photo --chat 'iMessage;+;chat0000' --file /path/to/group.jpg
imsg chat-add-member --chat 'iMessage;+;chat0000' --address +15553333333
imsg chat-remove-member --chat 'iMessage;+;chat0000' --address +15553333333
imsg chat-leave --chat 'iMessage;+;chat0000'
imsg chat-delete --chat 'iMessage;+;chat0000'
imsg chat-mark --chat 'iMessage;+;chat0000' --read
```

群组修改高度可见。更改成员资格、名称、照片、已读状态、离开或删除前，确认确切群组和参与者列表。

## 反应和回复

公共 `react` 受限：它仅对聊天中最新的接收消息进行反应。

```bash
imsg react --chat-id 42 --reaction like
imsg react --chat-id 42 --reaction love
imsg react --chat-id 42 --reaction dislike
imsg react --chat-id 42 --reaction laugh
imsg react --chat-id 42 --reaction emphasis
imsg react --chat-id 42 --reaction question
```

对于特定消息 GUID 或移除，使用桥接 `tapback`：

```bash
imsg tapback --chat 'iMessage;-;+15551234567' --message <message-guid> --kind love
imsg tapback --chat 'iMessage;-;+15551234567' --message <message-guid> --kind love --remove
```

使用 `send-rich --reply-to <message-guid>` 进行线程回复。如果用户说“那个”或“上一个”，请确认引用的消息。

## 投票

原生 Apple Messages 投票需要桥接。创建至少需要两个 `--option` 值。投票需要 `--option-id`、`--option-index` 或 `--option` 之一。

Messages 仅在投票气泡中渲染选项，因此当前 `imsg poll send` 会回显 `--question` 作为最佳尝试的纯文本标题。使用 `--comment` 覆盖该标题。当仅标题失败时，不要自动重试：投票可能已发送。

```bash
imsg poll send --chat 'iMessage;-;+15551234567' \
  --question "Dinner?" --option "Pizza" --option "Sushi" --comment "Vote by 5pm"
imsg poll send --chat 'iMessage;+;chat0000' --reply-to <message-guid> \
  --question "Approve?" --option "Yes" --option "No"
imsg poll vote --chat 'iMessage;+;chat0000' \
  --poll <poll-message-guid> --option-id <option-id>
```

使用以下命令查找投票 ID 和选项：

```bash
imsg history --chat-id 42 --limit 20 --json | jq -s '.[] | select(.poll != null) | {guid, poll}'
```

`history` 和 `watch` 会从干净标题行回填无标题原生投票的 `poll.question`。投票行是 `poll` 事件，不是轻点回复；`watch --reactions` 不需要即可看到它们。

## 监视和长时运行代理

对于短时一次性等待，使用 `watch`：

```bash
imsg watch --chat-id 42 --since-rowid 9000 --json
imsg watch --chat-id 42 --attachments --convert-attachments --json
imsg watch --chat-id 42 --reactions --json
imsg watch --chat-id 42 --bb-events --json
```

`--since-rowid` 是排他的。没有它，`watch` 从最新行开始。`watch` 使用文件系统事件加上低频轮询回退，因此可以在错过 SQLite 侧车事件后追上。没有 `--reactions`，轮询对象也会出现。

对于守护进程或多聊天集成，使用 `imsg rpc`。它通过 stdin/stdout 传输 JSON-RPC 2.0。使用 `imsg status --json` 检查 `rpc_methods`，再使用新的桥接或投票方法。

## 安全规则

- 除非用户请求已包含确切值，否则每次发送前确认接收者、聊天和内容。
- 确认可见状态变化：已读回执、输入指示器、编辑、撤回、删除、投票、轻点回复、群组成员、群组名称/照片、离开/删除群组。
- 不要向未知号码或模糊的联系人名称匹配发送，除非获得批准。
- 确认附件存在且为预期文件。
- 优先使用 E.164 电话号码；仅在需要本地格式时使用 `--region US` 或其他区域。
- 使用桥接操作处理桥接专有语义，但首先确认可见状态变化和破坏性操作。
