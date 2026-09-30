---
name: basecamp
description: '通过 Basecamp CLI 与 Basecamp 进行交互。全面 API 支持：项目、待办事项、卡片、消息、文件、日程、签到、时间线、录音、模板、Webhook、订阅、阵容、聊天、提醒、仪表盘、分配、通知、书签、上浮、草稿、笔记、日历和账户。

  适用于任何 Basecamp 问题或操作。'
---

# /basecamp - Basecamp 工作流命令

完整的 CLI 覆盖：涵盖 todos、卡片、消息、文件、日程、签到、时间线、录音、模板、Webhooks、订阅、阵容、聊天、提醒、仪表、任务分配、通知和账户等 189 个跟踪的范围内端点。

## 代理不变量

**必须遵循以下规则：**

1. **选择正确的输出模式** — 需要过滤/提取数据时使用 `--jq`；需要完整 JSON 时使用 `--json`；向人类展示结果时使用 `--md`（见输出模式部分）。**绝对不要将输出管道到外部 `jq` — 使用 `--jq` 代替。**
2. **首先解析 URL** 使用 `basecamp url parse "<url>"` 提取 ID
3. **评论是扁平的** — 回复到父级录音，而不是评论
4. **通过 `.basecamp/config.json` 检查上下文** 在假设项目之前
5. **内容字段接受 Markdown 和 @提及** — 消息正文和评论内容接受 Markdown 语法；CLI 会自动将其转换为 HTML。使用 Markdown 格式（列表、粗体、链接、代码块、表格）进行丰富内容。有四种提及语法可用（为代理推荐确定性语法）：
   - **`[@Name](mention:SGID)`** — 零 API 调用，直接嵌入 SGID（代理首选）
   - **`[@Name](person:ID)`** — 一个 API 调用，通过可提醒集将人员 ID 解析为 SGID
   - **`@sgid:VALUE`** — 内联 SGID 嵌入，用于管道组合性
   - **`@Name` / `@First.Last`** — 模糊名称解析（可能存在歧义）
   对于 todos、文档和卡片，内容按原样发送 — 直接使用纯文本或 HTML。

   **表格边界：** GFM 表格往返：它们在消息/评论正文中渲染，显示时将它们转换回管道表格，TUI 嵌入式编辑器打开简单的网格进行编辑。只有 **复杂** 表格 — 合并单元格（colspan/rowspan）、标题、额外的标题行、嵌套表格、单元格内的附件/图像或块内容、多段落或多行单元格，或块引号内/列表内的表格 — 拒绝打开，因为 GFM 管道表格无法表示这些形状（在 Basecamp 网站上编辑它们，或通过 `messages update` / `comments update` / `todos update --description` 替换整个字段，这些命令接收新内容且不受影响）。复杂表格仍然 **尝试显示**，展开为纯网格。

   **多行 / 非 ASCII 内容：** 不要依赖 bash ANSI-C 引用（`$'...\n...'`）— 它是 bash/zsh 的扩展。在 POSIX `/bin/sh`（dash、busybox-ash、常见于沙盒）下，`$` 会按字面意义传递并导致前置 `$`，`\n` 保持为字面意义的反斜杠-n。通过 stdin 传输内容，使用 `-` 作为内容参数：
   ```bash
   printf '%s\n' '海报 mockup 方向稿：' '' '<bc-attachment ...>' | basecamp comments create <recording_id> - --in <project> --json
   ```
   `-` 表示“从 stdin 读取”在每次内容输入时：内容类型位置参数（`comments create/update`、`messages create [body]`、`cards create [body]`、`todos create`、`docs documents create [content]`、`chat post/update`、`boost create`、`checkins answer create/update`、`notes set`）和内容标志（`api post/put` 上的 `--data`、`todos sweep` 上的 `--body`、`--content`、`--description`、`--comment`、`notes set` 上的 `--file`）。每个命令的 `--agent` 帮助列出了其 stdin 输入。规则：
   - 管道 **永远不会被隐式消耗** — 没有 `-` 它会被忽略（或，在内容需要但缺失的情况下，错误会教 `-`）。
   - 每个调用只能读取一次 stdin。
   - 在其他任何地方（标题、名称、路径）使用字面 `-` 当 stdin 被管道时 **会报错**。在 `--` 分隔符后转义位置参数（`basecamp projects create -- -`）；标志值没有行内转义 — 不带管道 stdin 运行命令。`basecamp help` 和 shell 完成是例外：它们不会写入 Basecamp，并且完成时确实接收 `-` 作为正在完成的单词。
   - `-` 与没有管道（交互式 TTY）立即报错而不是挂起；使用管道、heredoc（`basecamp comments create <id> - <<'EOF'`）或提供 `--edit` 时使用。
   - stdin 内容的尾随换行符会被修剪，所以 `printf 'x\n' | ... -` 会发布 `x`（这使 `boost create -` 在其 16 字符限制内）。
  - 通用 `-` 支持和 `stray-` `-` 守护程序随 **v0.10.0** 发布。旧版 CLI 不一致支持它：`comments create/update` 读取 stdin，而未支持的输入可能将 `-` 视为字面内容或失败。例如，`messages create "Title" -` 会发布 `-`，Markdown 渲染为空的项目符号列表。当 CLI 版本未知时，先检查 `basecamp --version`，或将内容可移植地作为 `"$(cat file.md)"` 传递并验证发布时的 `content`。
6. **大多数命令需要项目范围** — 通过 `--in <project>` 或 `.basecamp/config.json`。跨项目例外：`basecamp reports assigned` 用于分配的工作，`basecamp assignments` 用于结构化任务分配视图，`basecamp reports overdue` 用于过期的 todos，`basecamp reports schedule` 用于所有项目的即将到来的日程，`basecamp recordings <type>` 用于按类型浏览，`basecamp notifications` 用于通知，`basecamp gauges list` 用于账户范围的仪表，以及第 7 点中涵盖的七个列表命令。
7. **账户范围列表。** `basecamp todos list --all-projects --json` 列出所有项目；相同的标志在 `cards list`、`messages list`、`comments list`、`files list`、`forwards list` 和 `checkins answers` 上也起相同作用。它会覆盖配置的项目，并且在没有项目范围内时这些命令已经列出账户范围而不是提示。命名单个项目内某物的标志会拒绝而不是静默忽略。
   账户范围列表默认返回 **前 100 个项目** — 账户范围的“全部”是整个账户，而不是一个项目的量。使用 `--limit N` 提高上限（它将逐页收集 N 个），或使用 `--all` 获取所有内容。`--page N` 获取确切的一页，但仅在分页列表上。
   两个过期变体 — `basecamp todos list --all-projects --overdue` 和 `basecamp cards list --all-projects --overdue` — 来自不分页端点。它们接受 `--limit` 和 `--all` 但 **拒绝 `--page`**，因此不要对它们使用 `--page`。

### 输出模式

**选择模式：**

| 目标 | 标志 | 格式 |
|------|------|--------|
| 过滤/提取 JSON 数据 | `--jq '<expr>'` | 内置 jq 过滤器（无需外部 jq）。隐含 `--json`；过滤器在信封上运行。 |
| 代理模式下的过滤 | `--agent --jq '<expr>'` | 过滤器在仅数据有效负载上运行（无信封），匹配 `--agent` 合约。 |
| 完整 JSON 输出 | `--json` | JSON 信封：`{ok, data, summary, breadcrumbs, meta}`；错误：`{ok:false, error, code, retryable, hint, meta}` |
| 向用户展示结果 | `--md` / `-m` | GFM 表格、任务列表、结构化 Markdown |
| 自动化/脚本 | `--agent` | 成功：原始 JSON 数据（无信封）；错误：`{ok:false,...}` 对象；无交互式提示 |

始终显式传递 `--json` 或 `--md` — 自动检测依赖于配置，可能不会产生您期望的格式。使用 `--md` 在组合报告、汇总数据或内联显示结果时。`--agent` 用于无头集成脚本。

**避免交互式提示。** 标志 `--agent`/`--json`/`--quiet`/`--ids-only`/`--count` 和环境变量 `BASECAMP_NONINTERACTIVE=1` 会抑制交互式选择提示。`--md` 不 — 如果一个必需的目标是模糊的（例如，具有多个 todosets 且没有 `--todoset` 的项目），并且 CLI 连接到终端，它将显示一个阻塞选择器。当您需要 Markdown 输出 *且* 无提示时，要么传递命名模糊内容的标志（例如，上述 todosets 案例中的 `--todoset <id>`，或 `--in <project>` / `--list <id>` 当项目或列表模糊时），要么在环境中设置 `BASECAMP_NONINTERACTIVE=1`。`BASECAMP_NONINTERACTIVE` 会禁用所有提示（它们变为可操作的错误），而不会改变输出格式 — 为在 PTY 下运行的代理提供的逃生通道。

**其他模式：** `--quiet`（成功：原始 JSON，无信封；错误：`{ok:false,...}`）、`--ids-only`、`--count`、`--stats`（会话统计）、`--styled`（强制 ANSI）、`-v` / `-vv`（详细/跟踪）、`--jq '<expr>'`（内置 jq 过滤器 — 见下文）。

### CLI 自省

使用 `--agent --help` 导航不熟悉的命令 — 返回描述任何命令的结构化 JSON：

```bash
basecamp todos --agent --help
```

```json
{"command":"todos","path":"basecamp todos","short":"...","long":"...","usage":"...","notes":["..."],
 "subcommands":[{"name":"sweep","short":"...","path":"basecamp todos sweep"}],
 "flags":[{"name":"assignee","type":"string","default":"","usage":"..."}],
 "inherited_flags":[{"name":"json","shorthand":"j","type":"bool","default":"false","usage":"..."}]}
```

遍历树：从 `basecamp --agent --help` 开始顶级命令，然后深入任何子命令。命令携带特定领域的代理提示（例如，"`--assignee` 仅过滤账户范围列表；在项目中，获取所有内容并在客户端过滤”）。

### 分页

```bash
basecamp <cmd> --limit 50   # 限制结果（默认因资源而异）
basecamp <cmd> --all        # 获取所有（对于大型数据集可能较慢）
basecamp <cmd> --page 1     # 仅第一页，无自动分页
```

`--all` 和 `--limit` 互斥。`--page` 不能与任何一方组合。

### 智能默认值

- `--assignee me` 解析为当前用户
- `--due tomorrow` / `--due +3` / `--due "next week"` — 自然日期解析，**在设置截止日期时**（`todos create`、`todos update`、`cards create` 等等）
- **列表上的 `--due`** 是不同的标志，不接受日期：它只接受 `with`、`without` 或 `overdue`，并且仅限账户范围。`basecamp todos list --due tomorrow` 被拒绝。对于基于日期的列表，使用 `--overdue`、`--no-due-date` 或 `basecamp assignments due <scope>`
- 如果未指定 `--in`，则从 `.basecamp/config.json` 获取项目
- 多个身份使用命名配置文件：`basecamp profile create <name>`，然后使用全局 `--profile <name>` 或 `BASECAMP_PROFILE=<name>` 选择一个。

## 快速参考

> **注意：** 大多数查询需要项目范围（通过 `--in <project>` 或 `.basecamp/config.json`）。跨项目例外：`basecamp reports assigned`、`basecamp assignments`、`basecamp reports overdue`、`basecamp reports schedule`、`basecamp recordings <type>`、`basecamp notifications`、`basecamp gauges list`。

| 任务 | 命令 |
|------|------|
| 列出项目 | `basecamp projects list --json` |
| 我的项目中的待办事项 | `basecamp todos list --assignee me --in <项目> --json` |
| 跨项目的我的待办事项 | `basecamp reports assigned --json` (默认为 "me") |
| 跨项目的我的日程安排 | `basecamp reports schedule --json` (所有项目中的即将发生的事件) |
| 跨项目的所有待办事项 | `basecamp todos list --all-projects --json` (按项目分组) |
| 项目中的过期待办事项 | `basecamp todos list --overdue --in <项目> --json` |
| 跨项目的过期待办事项 | `basecamp todos list --all-projects --overdue --json` (扁平化，按时间顺序) 或 `basecamp reports overdue --json` (按逾期程度分组) |
| 跨项目的所有卡片 | `basecamp cards list --all-projects --json` (按项目分组) |
| 某人的待办事项 (跨项目) | `basecamp todos list --all-projects --assignee "Ann" --json` (服务器端过滤) |
| 两个人的待办事项 (跨项目) | `basecamp todos list --all-projects --assignee ann --assignee bob --json` (匹配任意一个) |
| 某人的卡片 (跨项目) | `basecamp cards list --all-projects --assignee "Ann" --json` |
| 没有设置截止日期的待办事项 (跨项目) | `basecamp todos list --all-projects --due without --json` |
| 我的书签 | `basecamp bookmarks list --json` |
| 添加书签 | `basecamp bookmarks add <id-or-url> --json` |
| 是否已书签？ | `basecamp bookmarks check <id-or-url> --json` (始终退出状态为 0) |
| 将录音提升 | `basecamp bubble-up add <id-or-url> --json` |
| 安排提升 | `basecamp bubble-up add <id-or-url> --at tomorrow --json` |
| 弹出提升 | `basecamp bubble-up remove <id-or-url> --json` |
| 我的未发布的草稿 | `basecamp drafts list --json` |
| 阅读我的个人笔记 | `basecamp notes show --json` |
| 替换我的个人笔记 | `basecamp notes set "<content>" --json` |
| 我需要回答的签到 | `basecamp checkins reminders --json` |
| 添加到下一步 | `basecamp assignments prioritize <id> --json` |
| 更改日历颜色 | `basecamp calendars update <id-or-url> --color blue --json` |
| 项目外的待办事项 | `basecamp todos create "<content>" --loose --in <项目> --json` |
| 分配待办事项 | `basecamp assign <id> [id...] --to <person> --in <项目> --json` |
| 分配卡片 | `basecamp assign <id> [id...] --card --to <person> --in <项目> --json` |
| 分配卡片步骤 | `basecamp assign <id> [id...] --step --to <person> --in <项目> --json` |
| 创建待办事项 | `basecamp todos create "Task" --in <项目> --list <列表> --json` |
| 创建待办事项列表 | `basecamp todolists create "Name" --in <项目> --json` |
| 完成待办事项 | `basecamp todos complete <id> --json` |
| 列出卡片 | `basecamp cards list --in <项目> --json` |
| 创建卡片 | `basecamp cards create "Title" --in <项目> --json` |
| 完成卡片 | `basecamp cards done <id|url> --in <项目> --json` |
| 移动卡片 | `basecamp cards move <id> --to <列> [--position N] --in <项目> --json` |
| 将卡片移至挂起状态 | `basecamp cards move <id> --on-hold --in <项目> --json` |
| 将卡片移至另一个项目 | `basecamp cards move <id> --to-wormhole <wormhole_id> --in <项目> --json` (异步传送) |
| 发布消息 | `basecamp messages create "Title" "Body" --in <项目> --json` |
| 带有 @提及发布消息 | `basecamp messages create "Title" "Hey @First.Last, ..." --in <项目> --json` |
| 沉默发布消息 | `basecamp messages create "Title" "Body" --no-subscribe --in <项目> --json` |
| 发布到聊天 | `basecamp chat post "Message" --in <项目> --json` |
| 列出提醒 | `basecamp notifications --json --jq '.data.reads[]? | select(.section == "pings")'` |
| 阅读提醒线程 | `basecamp api get "/buckets/<circle_id>/chats/<chat_id>/lines.json" --agent` |
| 发布到提醒线程 | `basecamp api post "/buckets/<circle_id>/chats/<chat_id>/lines.json" --data '{"content":"<p>message</p>"}' --json` |
| 添加评论 | `basecamp comments create <recording_id> "Text" --in <项目> --json` |
| 检查评论/回复原子 | `basecamp comments show <url> --json` → `.data` 中的 `reply_target` + `mention` |
| 列出附件 | `basecamp attachments list <id\|url> --json` |
| 下载附件 | `basecamp attachments download <id> --out /tmp/` |
| 显示并下载 | `basecamp todos show <id> --download-attachments --json` |
| 将附件流到标准输出 | `basecamp attachments download <id> --file <name> --out -` |
| 更改项目历史记录 | `basecamp events <id\|url> --json` (当卡片移动列时，当待办事项被完成时) |
| 搜索 | `basecamp search "query" --json` |
| 解析 URL | `basecamp url parse "<url>" --json` |
| 上传文件 | `basecamp files uploads create <file> [--vault <folder_id>] --in <项目> --json` |
| 下载文件 | `basecamp files download <id> --in <项目>` |
| 将文件流到标准输出 | `basecamp files download <id> --out - --in <项目>` |
| 下载存储 URL | `basecamp files download "https://storage.3.basecamp.com/.../download/report.pdf"` |
| 我的分配 | `basecamp assignments --json` (优先级 + 非优先级) |
| 过期分配 | `basecamp assignments due overdue --json` |
| 已完成分配 | `basecamp assignments completed --json` |
| 提醒 | `basecamp notifications --json` |
| 标记提醒为已读 | `basecamp notifications read <id> --json` |
| 所有提升 (BC5) | `basecamp notifications bubbleups --json` |
| 计量表 (全局) | `basecamp gauges list --json` |
| 计量表指针 | `basecamp gauges needles --in <项目> --json` |
| 创建指针 | `basecamp gauges create --position 75 --color green --in <项目> --json` |
| 账户详情 | `basecamp accounts show --json` |

## URL 解析

**在执行操作前解析 URL —— 除非你将 URL 直接传递给接受 URL 的命令** (`show`, `comments show`, `comments thread`, `attachments list`/`attachments download`), 这些命令会为你提取 ID。只有 `comments show` 和 `comments thread` 在获取前会验证 URL 的主机和账户。对于其他接受 URL 的命令，仅传递来自可信 Basecamp 主机的 URL：`basecamp url parse` 提取 ID 但**不会**验证 URL 的来源，因此解析攻击者控制的路径会产生看起来可信的 ID。

```bash
basecamp url parse "https://3.basecamp.com/2914079/buckets/41746046/messages/9478142982#__recording_9488783598" --json
```

返回：`account_id`, `project_id`, `type`, `recording_id`, `comment_id` (来自片段)。

**URL 模式：**
- `/buckets/27/messages/123` - 项目 27 中的消息 123
- `/buckets/27/messages/123#__recording_456` - 消息 123 上的评论 456
- `/buckets/27/card_tables/cards/789` - 卡片 789
- `/buckets/27/card_tables/columns/456` - 列 456 (用于创建卡片)
- `/buckets/27/todos/101` - 待办事项 101
- `/buckets/27/uploads/202` - 上传/文件 202
- `/buckets/27/documents/303` - 文件 303
- `/buckets/27/schedule_entries/404` - 日程条目 404

**回复评论：**
```bash
# 评论是扁平的 - 回复父级 recording_id，而不是 comment_id
basecamp url parse "https://...messages/123#__recording_456" --json
# 返回 recording_id: 123 (父级), comment_id: 456 (片段) - 评论在 123 上，而不是 456
basecamp comments create 123 "Reply" --in <项目>

# 或者在一个调用中确定性地获取整个回复准备好的上下文：
basecamp comments thread "https://...messages/123#__recording_456" --json
# .data.reply_target.recording_id  → 回复位置
# .data.reply_target.account_id    → 回复所属的账户 (构建完全限定命令)
# .data.focus.author.mention.syntax → 可粘贴的 [@Name](mention:SGID)
# .data.comments                   → 周围的讨论 (默认窗口为 41)
# --all 返回所有获取的评论；--window N 设置窗口大小
# 当账户来自 URL (未配置) 时，回复面包屑携带 --account
```

## 决策树

### 查找内容

```
需要查找某物？
├── 知道类型 + 项目？ → basecamp <类型> list --in <项目> --json
│   (某些组有默认列表行为；不确定时使用 --agent --help)
├── 我的分配工作？ → basecamp assignments --json (优先级 + 非优先级)
│   或：basecamp reports assigned --json (传统视图，默认为 "me")
├── 我的过期分配？ → basecamp assignments due overdue --json
├── 我的提醒？ → basecamp notifications --json
├── 即将到来的日程？ → basecamp reports schedule --json (跨项目)
├── 跨项目的过期？ → basecamp reports overdue --json
├── 跨项目按类型浏览？ → basecamp recordings <类型> --json
│   (类型：待办事项、消息、文档、评论、卡片、上传)
│   注意：默认为活动状态；使用 --status archived 查找已归档项
│   ⚠ 没有分配数据 — 无法按人员过滤；使用 reports assigned 代替
├── 全文搜索？ → basecamp search "query" --json
├── 有评论 URL 或针对评论的提醒链接？ → basecamp comments thread <url> --json
└── 有 URL？ → basecamp url parse "<url>" --json
```

### 修改内容

```
想更改某物？
├── 有 URL？ → basecamp url parse "<url>" → 使用提取的 ID
├── 有 ID？ → basecamp <资源> update <id> --field value
├── 更改状态？ → basecamp recordings trash|archive|restore <id>
├── 完成待办事项？ → basecamp todos complete <id>
├── 完成卡片？ → basecamp cards done <id|url> --in <项目>
└── 回复评论？ → basecamp comments show <url> --jq '.data | {reply_target, mention}'
    (一个调用，廉价的原子 — 提及是机器专用的，因此使用 --jq/--json，而不是纯 show)
    或 basecamp comments thread <url> 当你需要周围的讨论时；
    然后 basecamp comments create <reply_target.recording_id> <文本>
```

## 常见工作流

### 将代码链接到 Basecamp 待办事项

```bash
# 获取提交信息并在待办事项上评论 (使用 printf %q 进行安全引用)
COMMIT=$(git rev-parse --short HEAD)
MSG=$(git log -1 --format=%s)
basecamp comments create <todo_id> "提交 $COMMIT: $(printf '%s' "$MSG")" --in <项目>

# 完成时
basecamp todos complete <todo_id>
```

### 在 Basecamp 中跟踪 PR

```bash
# 创建 PR 工作的待办事项
basecamp todos create "Review PR #42" --in <项目> --assignee me --due tomorrow

# 合并时
basecamp todos complete <todo_id>
basecamp chat post "Merged PR #42" --in <项目>
```

### 批量处理过期待办事项

```bash
# 预览过期待办事项
basecamp todos sweep --overdue --dry-run --in <项目>

# 带评论完成所有
basecamp todos sweep --overdue --complete --comment "清理" --in <项目>
```

### 提及人员 (首选 — 确定性)

```bash
# 1. 查找人员
basecamp people pingable --jq '.data[] | select(.name == "Jane Smith")'
# => {"id": 42000, "attachable_sgid": "BAh7CEkiCG...", "name": "Jane Smith"}

# 2. 使用 SGID 在 Markdown 提及语法中 (发布期间零 API 调用)
basecamp comments create 123 "Hey [@Jane Smith](mention:BAh7CEkiCG...), check this" --in <项目>

# 或使用人员 ID (发布期间一个查找)
basecamp comments create 123 "Hey [@Jane Smith](person:42000), check this" --in <项目>
```

### 提及人员 (交互式 — 可能存在歧义)

```bash
# 模糊匹配：使用 @First.Last 减少歧义
basecamp comments create <id> "@Jane.Smith, please review this" --in <项目>
basecamp messages create "Update" "cc @Jane, @Alex" --in <项目>
basecamp chat post "@Jane, done!" --in <项目>

# 模糊名称返回错误并提供建议
# 使用 @First.Last 进行消除歧义
```

### 将卡片通过工作流移动

```bash
# 列出列以获取 ID
basecamp cards columns --in <项目> --json

# 完成卡片 (自动将其移至完成列)
basecamp cards done <card_id> --in <项目>

# 将卡片移至列
basecamp cards move <card_id> --to <column_id> --in <项目>

# 将卡片移至列中的特定位置 (1 索引)
basecamp cards move <card_id> --to <column_id> --position 1 --in <项目>

# 将卡片移至当前列的挂起部分
basecamp cards move <card_id> --on-hold --in <项目>

# 将卡片移至特定列的挂起部分 (数字 ID)
basecamp cards move <card_id> --to <column_id> --on-hold --in <项目>

# 将卡片移至命名列的挂起部分 (需要 --card-table)
basecamp cards move <card_id> --to "Column Name" --on-hold --card-table <table_id> --in <项目>
```

### 从 Basecamp 下载文件

```bash
basecamp files download <upload_id> --in <项目> --out ./downloads

# 下载存储 URL 的附件 (不需要 --in)
basecamp files download "https://storage.3.basecamp.com/123/blobs/abc/download/report.pdf"

# 流到标准输出 (用于管道)
basecamp files download <upload_id> --out - --in <项目>
```

### 使用附件 (多模态代理工作流)

消息、待办事项、卡片和文档可能包含图像和文件附件 (原型图、截图、注释设计)。显示命令将这些作为字段范围的集合显示出来 — `content_attachments` 和/或 `description_attachments` — 由包含它们的富文本属性键入。注意字段提示下载命令。

**步骤 1：获取录音并检查附件**
```bash
basecamp todos show <id> --json
# 响应包括 description_attachments 当存在附件时
# 消息/文档使用 content_attachments；卡片可能两者都有
# 注意字段提示："3 个附件 — 下载: basecamp attachments download <id>"
```

**步骤 2 (一次性)：使用显示命令下载附件**
```bash
# --download-attachments 一次性获取并下载
basecamp todos show <id> --download-attachments --json
# content_attachments/description_attachments 条目现在包括指向本地文件的 "path"
# 默认下载到操作系统临时目录，或指定：--download-attachments /tmp/att
```

**步骤 2 (替代方案)：单独下载**
```bash
# 一次性下载所有 (在 stderr 上显示进度)
basecamp attachments download <id> --out /tmp/attachments
```

**步骤 3：使用本地文件阅读工具查看图像**
对于多模态 LLM (Claude, Gemini)，使用文件阅读工具在响应的 "path" 上查看下载的图像，直接无需浏览器。这会显示视觉上下文 (原型图、截图、注释设计)，这些通常是 Basecamp 待办事项或消息中最重要的部分。

```bash
# 将单个图像流到标准输出以进行管道
basecamp attachments download <id> --file mockup.png --out -

# 当名称冲突时选择索引
basecamp attachments download <id> --index 2 --out -
```

**关键模式：** 当显示命令响应包含 `content_attachments` 或 `description_attachments` 时，始终下载并查看它们 — 视觉上下文通常比文本内容更重要。使用 `--download-attachments` 进行一次性获取+下载，或遵循面包屑提示进行两步控制。

## 资源参考

### 项目

```bash
basecamp projects list --json               # 列出所有
basecamp projects show <id> --json          # 显示详情
basecamp projects create "Name" --json      # 创建
basecamp projects update <id> --name "New"  # 更新
basecamp projects trash <id>                # 移至回收站 (可恢复)
```

**归档项目：** CLI 没有专门的归档命令，但底层状态端点可以通过原始 API 访问。相同的路径适用于恢复到活动状态或移至回收站。

```bash
basecamp api put "projects/<id>/status/archived" -d '{}' --json   # 归档
basecamp api put "projects/<id>/status/active" -d '{}' --json     # 恢复
basecamp api put "projects/<id>/status/trashed" -d '{}' --json    # 回收站 (与 `projects trash` 相同)
```

验证：`basecamp projects show <id> --jq '.data.status'`.

### 待办事项

```bash
basecamp todos list --in <项目> --json               # 在项目中列出
basecamp todos list --assignee 我 --in <项目>        # 我的待办事项
basecamp todos list --overdue --in <项目>            # 仅逾期
basecamp todos list --status 已完成 --in <项目>     # 已完成
basecamp todos list --list <待办事项列表ID> --in <项目> # 在特定列表中
basecamp todos create "任务" --in <项目> --list <列表> --assignee 我 --due 明天
basecamp todos complete <id> [id...]                # 完成（多个可以）
basecamp todos uncomplete <id>                      # 重新打开
basecamp assign <id> [id...] --to <人员> --in <项目>       # 指派待办事项（多个可以）
basecamp unassign <id> [id...] --from <人员> --in <项目>   # 移除待办事项指派者（多个可以）
basecamp assign <id> [id...] --card --to <人员> --in <项目>   # 指派卡片
basecamp unassign <id> [id...] --card --from <人员> --in <项目> # 移除卡片指派者
basecamp assign <id> [id...] --step --to <人员> --in <项目>   # 指派卡片步骤
basecamp unassign <id> [id...] --step --from <人员> --in <项目> # 移除步骤指派者
basecamp todos position <id> --to 1                     # 移动到顶部
basecamp todos position <id> --to 1 --list <id|name|url> # 移动到不同列表
basecamp todos sweep --overdue --complete --comment "完成" --in <项目>
basecamp todos create "任务" --in <项目> --list <列表> --notify-on-completion "Jane,Bob"  # 完成时通知
basecamp todos update <id> --notify-on-completion "Jane"  # 设置完成时通知的对象
basecamp todos update <id> --no-notify-on-completion      # 清除完成时通知
```

**标志：** `--assignee`（可重复；服务器端全局账户范围，客户端项目范围内；也适用于`cards list`的全局账户范围，但不适用于消息），`--status`（已完成/未完成/已归档/已删除），`--overdue`，`--list`，`--due`（**列表筛选：`with`/`without`/`overdue`仅，全局仅** — 不是日期；参见智能默认值），`--limit`，`--all`

**完成订阅者**（"完成时通知…"）：在`todos create`和`todos update`上使用`--notify-on-completion <名称或ID，逗号分隔>`设置；使用`todos update`上的`--no-notify-on-completion`清除。
普通更新（标题、截止日期等）会保留现有的完成订阅者。

**待办事项子任务（检查表步骤）：** Basecamp 待办事项子任务存储为`Kanban::Step`记录，即使其父项是普通`Todo`。常规`basecamp todos show`响应可能不包含它们；使用`basecamp recordings list --in <项目> --type Kanban::Step`并按`parent.id`筛选，以列出/检查待办事项的子任务。

```bash
# 在待办事项下创建子任务。
# 在此卡片式路径中使用数字项目ID和待办事项ID。
basecamp api post /buckets/<project_id>/card_tables/cards/<parent_todo_id>/steps.json \
  --data '{"title":"子任务标题"}' \
  --json

# 读取或编辑子任务
basecamp api get /buckets/<project_id>/card_tables/steps/<step_id>.json --json
basecamp api put /buckets/<project_id>/card_tables/steps/<step_id>.json \
  --data '{"title":"更新的子任务标题"}' \
  --json

# 列出待办事项的子任务
PARENT_TODO_ID=<parent_todo_id> \
basecamp recordings list --in <项目> --type Kanban::Step --all \
  --jq '.data[] | select(.parent.id==(env.PARENT_TODO_ID | tonumber)) | {id,title,status,parent:.parent.id,url}'

# 指派或设置截止日期。只发送你正在更改的字段——省略的字段保持不变。`assignee_ids`替换整个列表，因此请命名所有保持分配的人员。
basecamp api put /buckets/<project_id>/card_tables/steps/<step_id>.json \
  --data '{"assignee_ids":[<人员ID>,<现有人员ID>],"due_on":"<YYYY-MM-DD>"}' \
  --json

# 完成或重新打开子任务
basecamp api put /buckets/<project_id>/card_tables/steps/<step_id>/completions.json \
  --data '{"completion":"on"}' \
  --json
basecamp api put /buckets/<project_id>/card_tables/steps/<step_id>/completions.json \
  --data '{"completion":"off"}' \
  --json

# 从待办事项 UI 中通过删除步骤记录（Kanban::Step）来删除子任务
basecamp recordings trash <step_id> --in <项目> --json
```

要点：在运行示例之前，替换数字占位符，如`<project_id>`、`<parent_todo_id>`和`<person_id>`。桶范围 API 路径需要数字项目/桶 ID；`--in <项目>`仍然可以接受 CLI 命令支持名称解析的项目名称。对于创建待办事项子任务，Basecamp 接受父待办事项 ID 在`/buckets/<project_id>/card_tables/cards/<parent_todo_id>/steps.json`路径中。要列出待办事项下的子任务，使用`basecamp recordings list --in <项目> --type Kanban::Step`并使用上述`parent.id`筛选。

已完成的子任务有`completed: true`和一个带有`created_at`和`creator`的`completion`对象。未完成的子任务有`completed: false`且没有`completion`对象。已删除的子任务可能仍然可以直接读取，状态为`"trashed"`且`inherits_status: false`，但它们不再出现在待办事项 UI 中。

在测试带待办事项的步骤时，这些桶范围的直接`GET`请求返回了`not_found`：
`/buckets/<project_id>/card_tables/cards/<parent_todo_id>/steps.json`、
`/buckets/<project_id>/card_tables/cards/<parent_todo_id>.json`和
`/buckets/<project_id>/todos/<parent_todo_id>/steps.json`。要检查已删除的子任务，请添加`--status trashed`；归档的父项可能需要`--status archived`。

**原始步骤更新是部分更新。** `PUT .../card_tables/steps/<id>.json`会保留你省略的每个参数，因此只发送你正在更改的字段。回显你没有打算更改的`title`不仅是多余的——它会撤销在你读取和写入之间编辑标题的任何人。要清除值，请明确说明：`"due_on": null`清除截止日期，`"assignee_ids": []`移除所有人。`assignee_ids`始终替换整个列表而不是添加到其中，因此请命名所有应保持分配的人员。

(This is bc3#12521。在此之前，省略的字段会被清除，并且没有标题的更新会被拒绝，这就是为什么旧的指南说要重新发送标题。待办事项子任务和卡片步骤共享一个端点和合同——`PUT card_tables/steps/:id`路由到同一个控制器，用于两者。)

通用的`basecamp assign <step_id> --step ...`命令用于卡片步骤，并且对于待办事项支持的步骤可能会失败并显示`Bad Request`，因此对于待办事项子任务，请优先使用原始步骤更新端点上的`assignee_ids`。

### 待办事项列表

待办事项列表是待办事项的容器。在添加待办事项之前创建待办事项列表。

```bash
basecamp todolists list --in <项目> --json              # 列出待办事项列表
basecamp todolists show <id> --in <项目>                # 显示详细信息
basecamp todolists create "名称" --in <项目> --json     # 创建
basecamp todolists create "名称" --description "描述" --in <项目>
basecamp todolists create "名称" --visible-to-clients --in <项目>  # 对客户可见
basecamp todolists update <id> --name "新名称" --in <项目> # 更新
basecamp todolists position <id> --to 1                     # 重新排序一个列表（1 = 顶部）
basecamp todolists position <id> <id> <id>                  # 按顺序排列未完成的列表，从上到下
```

批量`position`在一个命令中设置可见顺序：传递来自同一待办事项集的不完整列表，从上到下。它始终将它们置于顶部。

### 卡片（Kanban）

**注意：** `cards list`上的`--assignee`是**仅全局账户范围**——传递`--all-projects`（或没有项目在范围内），它将成为一个真正的服务器端过滤器。在单个项目中，卡片没有指派过滤器：获取所有卡片并在客户端筛选。`--due with|without|overdue`在卡片上也是仅全局范围。如果一个项目有多个卡片表，你必须指定`--card-table <id>`。当你收到"不明确的卡片表"错误时，提示会显示可用的表 ID 和名称。

```bash
basecamp cards list --in <项目> --json             # 所有卡片
basecamp cards list --card-table <id> --in <项目>  # 特定表（如果多个则必需）
basecamp cards list --column <id> --in <项目>      # 列中的卡片
basecamp cards columns --in <项目> --json          # 列出列（如果多个则需要`--card-table`）
basecamp cards show <id> --in <项目>               # 卡片详细信息
basecamp cards create "标题" "<p>正文</p>" --in <项目> --column <id>
basecamp cards update <id> --title "新标题" --due 明天 --assignee 我
basecamp cards done <id|url> --in <项目>           # 自动移动到完成列
basecamp cards move <id> --to <column_id>             # 移动到列（数字ID）
basecamp cards move <id> --to "完成" --card-table <table_id>  # 通过名称移动（需要表）
basecamp cards move <id> --to "完成" --position 1 --card-table <table_id>  # 移动到位置
basecamp cards move <id> --on-hold                    # 移动到当前列的暂停状态
basecamp cards move <id> --to <column_id> --on-hold   # 移动到目标列的暂停状态
```

**跨项目卡片移动（虫洞）：** 移动卡片到另一个项目的唯一方法是通过一个*虫洞*——卡片表上的一个门户，将卡片发送到另一个项目卡片表上的预配置列（每个表最多4个）。传送是**异步的并生成一个新的卡片ID**：移动被接受后，服务器将卡片复制到目的地并删除原始卡片，因此**原始ID 404**——不要重用它。

```bash
basecamp cards wormholes list --in <项目>          # 发现虫洞（ID、目的地、链接）
basecamp cards wormholes create --to-column <id|url> --in <项目>   # 链接到另一个表上的列（≤4）
basecamp cards wormholes update <id> --to-column <id|url> --in <项目>
basecamp cards wormholes delete <id> --in <项目>
basecamp cards move <card_id> --to-wormhole <wormhole_id> --in <项目>          # 传送（异步）
basecamp cards move <card_id> --to-wormhole <destination_column_url> --in <项目>  # 通过目的地列匹配
```

`--to-wormhole`与`--to`/`--on-hold`/`--position`互斥。传递一个数字虫洞 ID 以直接路由，或传递一个目的地列 URL 以与源表的虫洞匹配。

**已归档/已删除的卡片：** `cards list`仅返回活动卡片。对于已归档或已删除的卡片，使用`basecamp recordings cards --status archived --in <项目>`或`--status trashed`。

**识别已完成的卡片：** 位于完成列中的卡片有`parent.type: "Kanban::DoneColumn"`和`completed: true`。使用此方法来识别未归档的已完成卡片。

**当卡片移动列时：** 不要读取`updated_at`——它在任何修改时都会改变。使用事件历史记录：`basecamp events <card_id> --json`为每个列移动记录一个`adopted`事件，并且卡片进入或离开完成列会与`completed`/`uncompleted`配对。参见[事件](#events-change-history)。

**卡片步骤（检查表）：**
```bash
basecamp cards steps <card_id> --in <项目>     # 列出步骤
basecamp cards step create "步骤" --card <id> --in <项目>
basecamp cards step complete <step_id> --in <项目>
basecamp cards step uncomplete <step_id>
```

**列管理：**
```bash
basecamp cards column show <id> --in <项目>
basecamp cards column create "名称" --in <项目>
basecamp cards column update <id> --title "新名称"
basecamp cards column move <id> --position 2
basecamp cards column color <id> --color blue
basecamp cards column on-hold <id>                # 启用暂停部分
basecamp cards column watch <id>                  # 订阅列
```

### 消息

```bash
basecamp messages list --in <项目> --json  # 列出消息
basecamp messages show <id> --in <项目>    # 显示消息
basecamp messages create "标题" "正文" --in <项目>
basecamp messages create "草稿" "WIP" --draft --in <项目>  # 创建草稿
basecamp messages publish <id>               # 发布草稿
basecamp messages update <id> --title "新标题" --body "更新"
basecamp messages pin <id> --in <项目>     # 固定到顶部
basecamp messages unpin <id>                  # 取消固定
```

**已归档/已删除的消息：** `messages list`仅返回活动消息。对于已归档或已删除的消息，使用`basecamp recordings messages --status archived --in <项目>`或`--status trashed`。

**标志：** `--draft`（创建为草稿），`--no-subscribe`（静默，无通知），`--subscribe "人员"`（逗号分隔的名称、电子邮件、ID或"我"；与`--no-subscribe`互斥），`--message-board <id>`（如果有多个板），`--visible-to-clients`（使项目中的客户可见；省略为服务器默认）

```bash
basecamp messages create "机器人更新" "完成" --no-subscribe --in <项目>
basecamp messages create "仅供参考" "笔记" --subscribe "Alice,bob@x.com" --in <项目>
basecamp messages create "对客户" "..." --visible-to-clients --in <项目>
```

**创建时的客户端可见性：** `messages create`、`todolists create`、`schedule create`、`checkins question create`和`tools create`接受`--visible-to-clients`以在一个调用中发布客户可见的记录（对于`tools create`，只有聊天和kanban_board工具类型会尊重它——其他类型继承项目默认值）。省略标志使用服务器默认值，这取决于上下文：**作为团队成员发布时为团队仅**，但**客户认证调用者始终创建客户可见的记录**（显式的`--visible-to-clients=false`在服务器端会被客户调用者覆盖）。传递`--visible-to-clients`在任何情况下都会发布客户可见的记录。要更改已创建记录的可见性，请使用`recordings visibility <id> --visible`。

### 评论

```bash
basecamp comments list <recording_id> --in <项目> --json
basecamp comments show <comment-id|comment-url> --json            # 现在返回回复目标 + 粘贴就绪的提及（JSON）
basecamp comments thread <comment-id|comment-url> --json          # 回复就绪：父项 + 聚焦 + 讨论 + @提及
basecamp comments thread <comment-id> --all --json                # 每个获取的评论而不是一个窗口
basecamp comments thread <comment-id> --window 11 --json          # 聚焦为中心的11个窗口
basecamp comments create <recording_id> "文本" --in <项目>
basecamp comments create <recording_id> "@Jane.Smith, 看起来不错!" --in <项目>  # 带有@提及
basecamp comments update <id> "更新" --in <项目>
```

**廉价原子与深度上下文（根据需要选择）：**
- `comments show <url> --jq '.data | {reply_target, mention}'` — 一个 API 调用。返回`reply_target`（`recording_id` — 回复发布的位置，评论是扁平的——加上`account_id`）和一个粘贴就绪的作者`mention`（仅 JSON；人类输出显示回复面包屑）。用于精确评论回复原子。
- `comments thread <url>` — 两个额外的调用。添加完整的父项记录、周围的讨论（窗口化、诚实截断）、和聚焦附件。当周围的讨论很重要时使用。

### 文件与文档

```bash
basecamp files list --in <项目> --json               # 列出所有（文件夹、文件、文档）
basecamp files list --vault <文件夹ID> --in <项目>  # 列出文件夹内容
basecamp files list --all-projects --json            # 跨所有项目（前100个）
basecamp files list --all-projects --limit 500       # 直至收集到500个
basecamp files list --all-projects --page 2          # 精确到第2页
basecamp files list --all-projects --all             # 每一页（在大型账户中较慢）
basecamp files show <ID> --in <项目>                 # 显示项目（自动检测类型）
basecamp files versions <上传ID> --json              # 上传文件的所有版本
basecamp files versions <上传ID> --limit 5 --json    # 限制结果（默认：全部）
basecamp files replace <上传ID> <文件>               # 替换文件，保留ID/URL/评论
basecamp files replace <上传ID> <文件> --description "v2 notes"  # 同时设置新描述
basecamp files download <ID> --in <项目>             # 下载文件
basecamp files download <ID> --out ./dir             # 下载到特定目录
basecamp files download "https://storage.../download/f" # 从存储URL下载
basecamp files uploads create <文件> --in <项目>      # 上传文件到根目录
basecamp files uploads create <文件> --vault <文件夹ID> --in <项目>  # 上传到文件夹
basecamp files uploads create <文件> --visible-to-clients --in <项目>  # 对客户可见（仅根文件夹）
basecamp files folder create "文件夹" --in <项目>
basecamp files doc create "文档" "正文" --in <项目>
basecamp files doc create "草稿" --draft --in <项目>
basecamp files doc create "笔记" "..." --no-subscribe --in <项目>
basecamp files doc create "对客户" "..." --visible-to-clients --in <项目>  # 对客户可见（仅根文件夹）
basecamp files update <文档ID> --title "新标题" --content "更新"
basecamp files update <文档ID> --title "新标题" --in <项目>      # 保留现有文档内容
basecamp files update <文档ID> --content "更新" --in <项目> # 保留现有文档标题
```

**文档更新语义：** `basecamp files update <文档ID>` 在CLI中安全用于部分更新：当你只传递 `--title` 或只传递 `--content` 时，CLI会先获取当前文档并保留未修改的字段。

**创建时客户可见性：** `doc create` 和 `uploads create` 接受 `--visible-to-clients`，但服务器仅在项目的**根 Docs & Files 文件夹**中认可它。使用标志定位嵌套文件夹（`--vault`/`--folder`）会引发硬错误，在上传任何内容之前——嵌套项继承其文件夹的可见性，之后无法针对单个项目更改（可见性端点会拒绝嵌套文档/上传）。要使嵌套项对客户可见，请在根文件夹中创建它，或首先更改控制文件夹可见性的符合条件的顶层祖先。省略标志使用服务器默认值；与消息一样，**客户认证调用者始终创建客户可见的记录**，无论如何。`recordings visibility` 是**不**针对嵌套文档/上传的补救措施。

**上传版本：** 替换文件会保留同一上传ID下的早期副本，因此 `basecamp files versions <上传ID>` 是查看一个文件历史的方式。从未被替换的文件会返回其当前版本，而不是错误。仅接受 `--page 1`；使用 `--all` 遍历每一页。
`basecamp files replace <上传ID> <文件>` 会替换位置上的新版本——上传保留其ID、URL和评论，无人通知，描述会继续传递，除非给出 `--description`。在发送同一文件的相同版本时，使用它而不是 `uploads create`。

**子命令：** `folders`、`uploads`、`documents`（每个都有分页标志）

### 时间表

对于所有项目的即将到来的事件，使用 `basecamp reports schedule --json`。

```bash
basecamp schedule info --in <项目> --json       # 时间表信息
basecamp schedule entries --in <项目> --json   # 列出条目
basecamp schedule show <ID> --in <项目>        # 条目详情
basecamp schedule show <ID> --date 20240315       # 特定发生（重复）
basecamp schedule create "事件" --starts-at "2024-03-15T09:00:00Z" --ends-at "2024-03-15T10:00:00Z" --in <项目>
basecamp schedule create "会议" --all-day --notify --participants 1,2,3 --in <项目>
basecamp schedule create "同步" --starts-at "..." --ends-at "..." --no-subscribe --in <项目>
basecamp schedule update <ID> --summary "新标题" --starts-at "..."
basecamp schedule settings --include-due --in <项目>  # 包含待办事项/卡片截止日期
```

**标志：** `--all-day`、`--notify`、`--participants <IDs>`、`--no-subscribe`、`--subscribe "people"`（互斥）、`--status`（活动/已归档/已删除）、`--visible-to-clients`（对客户可见；省略为服务器默认）

### 检查

```bash
basecamp checkins --in <项目> --json           # 问卷信息
basecamp checkins questions --in <项目>        # 列出问题
basecamp checkins question <ID> --in <项目>    # 问题详情
basecamp checkins answers <问题ID> --in <项目>  # 列出答案
basecamp checkins answers <问题ID> --by me --in <项目>  # 我的答案
basecamp checkins answers <问题ID> --by "Alice Smith" --in <项目>  # 按人员筛选（姓名、电子邮件或ID）
basecamp checkins answer <ID> --in <项目>      # 答案详情
basecamp checkins question create "你今天做了什么？" --in <项目>
basecamp checkins question update <ID> "新问题" --frequency 每周
basecamp checkins answer create <问题ID> "我的答案" --in <项目>  # 默认为今天
basecamp checkins answer update <ID> "更新" --in <项目>
```

**时间表选项：** `--frequency`（每天、每周、每两周、每月、特定日期）、`--days 1,2,3,4,5`（0=周日）、`--time "5:00pm"`

**客户可见性：** `checkins question create` 接受 `--visible-to-clients` 使问题对客户可见（省略为服务器默认；参见消息下的上下文相关规则）。

**管理问题：**

```bash
basecamp checkins question pause <ID> --json      # 停止询问
basecamp checkins question resume <ID> --json     # 再次询问
basecamp checkins question answerers <ID> --json  # 谁回答
basecamp checkins question notify <ID> --on-answer --json
basecamp checkins question notify <ID> --no-on-answer --json
basecamp checkins question notify <ID> --digest-include-unanswered --json
```

`notify` 更改**你自己的**设置，并且除非你命名它，否则每个设置都保持不变——所以 `--on-answer` 不会默默重置摘要设置。`--no-...` 变体发送明确的假值；不传递任何设置会被拒绝，而不是作为空更新发送。

**你的待办提醒**（账户范围，无 `--in`）：

```bash
basecamp checkins reminders --json
basecamp checkins reminders --limit 10 --json
```

`reminders` 和 `answerers` 接受 `--limit`，但故意**无 `--page`**：API不会在这些问题上认可页码，因此标志会接受它无法处理的值。

### 时间线

```bash
basecamp timeline --json                          # 账户范围活动
basecamp timeline --in <项目> --json           # 项目活动
basecamp timeline me --json                       # 你的活动
basecamp timeline --person <ID> --json            # 人员的活动
```

使用 `--limit N` 限制结果或 `--all` 获取所有内容（默认：100个事件）。

### 事件（变更历史）

`basecamp timeline` 报告项目或账户中的活动。对于特定项（待办事项、卡片、消息、文档）的审计跟踪，使用 `basecamp events`：

```bash
basecamp events <ID|url> --json                   # 变更历史
basecamp events <ID> --limit 25 --json            # 限制结果（默认100）
basecamp events <ID> --all --json                 # 获取所有
```

常见的 `action` 值：`created`、`completed`/`uncompleted`、`assignment_changed`、`content_changed`、`archived`/`unarchived`、`commented_on`，以及对于卡片——`adopted`，记录卡片每次移动到另一列时。这使得 `events` 成为回答“这张卡片何时移动？”或“这个何时真正完成？”的方式，而 `updated_at` 无法告诉你。

`--page` 仅接受 `1`；使用 `--all` 遍历每一页。

### 录音（跨项目）

使用 `basecamp recordings <类型>` 进行跨项目类型浏览。**对于分配的待办事项，请优先使用 `basecamp reports assigned`**——录音不包括指派者数据，并且无法按人员筛选。

```bash
basecamp recordings todos --json                  # 所有待办事项
basecamp recordings todos --all --json            # 所有待办事项（分页）
basecamp recordings messages --in <项目>       # 项目中的消息
basecamp recordings documents --status archived   # 归档文档
basecamp recordings cards --sort created_at --direction asc
basecamp recordings cards --status archived --all --json  # 包括归档卡片
```

**类型：** `todos`、`messages`、`documents`、`comments`、`cards`、`uploads`

**状态筛选：** 默认仅返回 `active` 录音。使用 `--status archived` 或 `--status trashed` 查询其他状态。您可能需要单独查询以获取完整数据（例如，活动+归档）。

**状态管理：**
```bash
basecamp recordings trash <ID> --in <项目>     # 移至回收站
basecamp recordings archive <ID> --in <项目>   # 归档
basecamp recordings restore <ID> --in <项目>   # 恢复到活动状态
basecamp recordings visibility <ID> --visible --in <项目>  # 对客户显示
basecamp recordings visibility <ID> --hidden      # 对客户隐藏
```

### 模板

```bash
basecamp templates list --json                    # 列出项目模板
basecamp templates show <ID> --json               # 项目模板详情
basecamp templates create "模板名称"             # 创建空项目模板
basecamp templates update <ID> --name "新名称"
basecamp templates delete <ID>                    # 回收项目模板
basecamp templates construct <ID> --name "新项目"  # 创建项目（异步）
basecamp templates construction <模板ID> <构造ID>  # 检查项目状态

basecamp templates library --json                 # 列出活动待办事项列表模板
basecamp templates copy <模板ID> --in <项目>  # 开始复制到待办事项
basecamp templates copy-status <复制ID>          # 检查复制状态
```

**异步结果：** `construct` 返回构造ID；轮询 `construction` 直至 `status="completed"` 获取项目。`copy` 返回复制ID；轮询 `copy-status` 通过 `pending` 和 `processing` 直至完成或失败。

复制可以报告需要访问目标项目的人员。向用户显示这些人并重新运行，使用 `--confirm-adding-people` 仅在用户明确批准授予权限后。永远不要自动添加此标志。

### Webhooks

```bash
basecamp webhooks list --in <项目> --json  # 列出webhooks
basecamp webhooks show <ID> --in <项目>    # webhook详情
basecamp webhooks create "https://..." --in <项目>
basecamp webhooks create "https://..." --types "Todo,Comment" --in <项目>
basecamp webhooks update <ID> --active --in <项目>
basecamp webhooks update <ID> --inactive      # 禁用
basecamp webhooks delete <ID> --in <项目>
```

**事件类型：** Todo、Todolist、Message、Comment、Document、Upload、Vault、Schedule::Entry、Kanban::Card、Question、Question::Answer

### 订阅

```bash
basecamp subscriptions <录音ID>              # 谁订阅
basecamp subscriptions subscribe <ID>              # 订阅自己
basecamp subscriptions unsubscribe <ID>            # 取消订阅
basecamp subscriptions add <ID> --people 1,2,3     # 添加人员
basecamp subscriptions remove <ID> --people 1,2,3  # 移除人员
```

### Lineup（账户范围标记）

```bash
basecamp lineup list                              # 列出所有标记
basecamp lineup create "里程碑" "2024-03-15"   # 创建标记
basecamp lineup create "发布" 明天          # 自然日期解析
basecamp lineup update <ID> "新名称" "+7"
basecamp lineup delete <ID>
```

**注意：** Lineup标记是账户范围的，不是项目范围的。

### Gauges

Gauges 使用0-100刻度上的彩色指针跟踪项目进度。

```bash
basecamp gauges list --json                           # 所有gauge（账户范围）
basecamp gauges needles --in <项目> --json         # 项目的指针
basecamp gauges needle <ID> --json                    # 指针详情
basecamp gauges create --position 75 --color green --in <项目>
basecamp gauges create --position 50 --color yellow --description "中途" --in <项目>
basecamp gauges create --position 25 --notify custom --subscriptions 1,2 --in <项目>
basecamp gauges update <ID> --description "更新"
basecamp gauges delete <ID>
basecamp gauges enable --in <项目>                 # 在项目上启用gauge
basecamp gauges disable --in <项目>                # 禁用gauge
```

**颜色：** green、yellow、red。**Notify：** everyone、working_on、custom（与 `--subscriptions` 一起使用）。

### 分配

查看所有项目中的你的分配。与 `reports assigned` 分开——提供结构化的优先级分组和截止日期范围。

```bash
basecamp assignments --json                           # 所有（优先级+非优先级）
basecamp assignments list --json                      # 相同
basecamp assignments completed --json                 # 已完成的分配
basecamp assignments due overdue --json               # 过期
basecamp assignments due due_today --json             # 今天到期
basecamp assignments due due_tomorrow --json          # 明天到期
basecamp assignments due due_later_this_week --json   # 本周稍后到期
```

**范围：** overdue、due_today、due_tomorrow、due_later_this_week、due_next_week、due_later。

**跨项目指派者筛选：** `basecamp todos list --all-projects
--assignee <人员>` 和 `basecamp cards list --all-projects --assignee <人员>`
在所有项目中服务器端筛选。两者都是可重复的，并匹配分配给任何命名人员的任务。
嵌套步骤上的指派者不被考虑，因此分配给某人的卡片的步骤不会基于此匹配。

**始终传递 `--all-projects` 当你指代所有项目时。** 没有它，这些列表在没有任何项目在范围内时仅账户范围——并且配置的默认项目计为在范围内。有一个配置时，`--assignee` 会默默降级为对单个项目的客户端筛选，并且 `--due` 会直接拒绝作为仅账户范围的。`--all-projects` 是覆盖配置默认值的方式，因此省略它的配方根据读者的配置返回不同的结果。

在项目内 `--assignee` 仍然适用于待办事项，但没有服务器端筛选，因此它会获取所有内容并客户端缩小。卡片完全没有项目范围的 `--assignee`。`--due with|without|overdue` 仅在两者上都是账户范围的，并且与 `--overdue` 和 `--no-due-date` 冲突，它们在同一轴上选择自己的列表。`--assignee` 与 `--unassigned` 一起被拒绝——服务器使这种组合必然为空。

**接下来**——重新排序优先级列表：

```bash
basecamp assignments prioritize <ID> --json      # 添加到 Next
basecamp assignments deprioritize <ID> --json    # 从 Next 移除
basecamp assignments reorder <ID> --position 1 --json
```

**应该传递哪个 ID —— 三种情况，不是两种。** 待办事项或卡片通过其自身的 `id` 进行引用。尚未优先处理的步骤通过其自身的 `id` 进行引用，该 `id` 位于父卡片的 `children` 中。但一旦步骤被优先处理，列表会将其显示在其父卡片下，因此条目的顶级 `id` 属于**卡片**，只有 `priority_recording_id` 才能引用步骤。

`basecamp assignments list` 是 `priority_recording_id` 出现的唯一位置 —— 它不出现在任何 URL 中。从那里读取它，而不是猜测：`deprioritize` 针对一个确切的记录，服务器无论如何都回答 204，所以一个错误的 ID 会报告成功而不会改变任何内容。如果一张卡片上的两个步骤都被优先处理，列表会显示一次卡片，并使用一个 `priority_recording_id`，而兄弟姐妹则无法单独引用。

### 个人（书签、上浮、草稿、笔记）

仅属于您自己，跨越所有项目 —— 无需 `--in <project>`。

```bash
basecamp bookmarks list --json
basecamp bookmarks add <id-or-url> --json
basecamp bookmarks remove <id-or-url> --json
basecamp bookmarks check <id-or-url> --json
basecamp bubble-up add <id-or-url> --json
basecamp bubble-up add <id-or-url> --at tomorrow --json
basecamp bubble-up remove <id-or-url> --json
basecamp drafts list --json
basecamp notes show --json
basecamp notes set "<content>" --json
```

`bubble-up add`/`remove` 会将记录重新出现在您的阅读中（BC5 的“保存”继任者），通过 ID 或粘贴的 URL 进行引用。`add` 默认现在会上浮；`--at` 会安排它 —— 关键字（`today`、`tomorrow`、`weekend`、`next_week`）或日历日期（`YYYY-MM-DD`）。这两个动词都是幂等的。没有每个记录的状态读取（GET 是一个不可渲染的 API 间隙）；完整列表是 `basecamp notifications bubbleups`。

`bookmarks add` 和 `remove` 是幂等的 —— 重新添加会返回现有的书签，删除不存在的书签仍然会成功。`check` 报告 `{"bookmarked": true|false}` 并**始终退出 0**：两个答案都是成功，所以这里非零退出意味着请求失败，而不是答案为假。

`bookmarks list` 和 `drafts list` 的边界与全局列表类似：默认 100，`--limit N`，`--page N`，`--all` 用于每一页。草稿在服务器端最多 250 条。

`notes` 是一个私有的临时笔记板 —— 每个人一个，没有 ID，没有可列出的内容。在您第一次写入之前，它会显示为空而不是返回 404。`set` **替换**整个笔记（它不会追加）并从参数或 `--file` 获取内容 —— 两者都接受 `-` 来读取标准输入（`cat notes.md | basecamp notes set -`）；没有 `-` 的管道不会被消耗。Markdown 被转换为 HTML。

### 日历

```bash
basecamp calendars show <id-or-url> --json
basecamp calendars update <id-or-url> --color blue --json
```

**没有 `calendars list`** —— API 没有索引端点，因此通过 ID 或粘贴其 URL 来引用日历。颜色：白色、红色、橙色、黄色、绿色、蓝色、青色、紫色、灰色、粉色、棕色。

### 通知

```bash
basecamp notifications --json                         # 列表（第 1 页）
basecamp notifications list --page 2 --json           # 第 2 页
basecamp notifications read <id> --json               # 标记为已读
basecamp notifications read <id> <id> --page 2 --json # 从第 2 页标记
basecamp notifications bubbleups --json               # 所有上浮（BC5）
basecamp notifications list --limit-bubble-ups --json # 将内联上浮限制为 2 条
```

**注意：** `read` 会从指定的页面上解析通知 ID。使用 `--page` 来匹配您列出的页面。

**上浮（BC5）：** `bubbleups` 列出所有当前和计划的上浮（分页；`--page` 获取单页）。`list --limit-bubble-ups` 使通知源保持紧凑：最多 2 条内联上浮，计划的上浮被省略，但未限制的计数仍然报告。

### 账户

```bash
basecamp accounts list --json                         # 列出已授权的账户
basecamp accounts use <id>                            # 设置默认账户
basecamp accounts show --json                         # 账户详情、限制、订阅
basecamp accounts update --name "New Name" --json     # 重命名账户
basecamp accounts logo upload <file> --json           # 上传标志（PNG/JPEG/GIF/WebP/AVIF/HEIC，最大 5MB）
basecamp accounts logo remove --json                  # 移除标志
```

### 聊天

```bash
basecamp chat --in <project> --json           # 列出聊天
basecamp chat messages --in <project> --json  # 列出消息
basecamp chat post "Hello!" --in <project>
basecamp chat post "@Jane.Smith, check this" --in <project>  # 带有 @提及（自动文本/HTML）
basecamp chat line <line_id> --in <project>   # 显示行
basecamp chat update <line_id> "edited content" --in <project>  # 在原地编辑现有消息
basecamp chat delete <line_id> --in <project> --force # 删除行（永久，不可恢复；需要 --force）
```

### Pings（直接消息）

Pings 是 Basecamp 的 1 对 1 和小群组直接消息。它们存储为 `Circle` 桶中的聊天记录，并使用与 Campfires 相同的行 API 形状。

使用 `notifications` 来发现活动的 Ping 线程，然后使用通用的 `api` 命令来读取或发布行。

```bash
# 查找在通知中可见的 Ping 线程。
# circle_id 是 UI URL 中的 Circle 桶 ID；chat_id 识别 Chat::Transcript。
basecamp notifications --json \
  --jq '.data.reads[]? | select(.section == "pings") | {bucket_name, app_url, circle_id: (.subscription_url | capture("/buckets/(?<id>[0-9]+)/").id), chat_id: (.subscription_url | capture("/recordings/(?<id>[0-9]+)/").id)}'

# 读取一个 Ping 线程。行按最新顺序返回。
basecamp api get "/buckets/<circle_id>/chats/<chat_id>/lines.json" --agent

# 发布一个 Ping 行。
basecamp api post "/buckets/<circle_id>/chats/<chat_id>/lines.json" \
  --data '{"content":"<p>Hey, quick question.</p>"}' --json
```

Ping 行记录包括 `creator.name`、`created_at`、HTML 内容、`type`、`bucket.type: "Circle"`，以及当存在文件或语音笔记时，附件字段。

Ping URL 使用 `/circles/<circle_id>`，并且可能在 `@` 后面包含行锚点：

```bash
echo "https://app.basecamp.com/<account_id>/circles/44024535@9927050443" \
  | sed -E 's|.*/circles/([0-9]+)(@([0-9]+))?.*|circle:\1 line:\3|'
# circle:44024535 line:9927050443
```

Pings 不会被 `basecamp recordings <type>` 返回。使用 `notifications` 进行发现，并使用聊天行 API 进行对话。

### 人员

```bash
basecamp people list --json                          # 账户中所有人员
basecamp people list --project <project> --json    # 项目上的人员
basecamp me --json                                 # 当前用户
basecamp people show <id> --json                   # 人员详情
basecamp people show me --json                     # 您自己的个人资料
basecamp people update me --bio "..." --title "..." --json   # 编辑您自己的个人资料
basecamp people out-of-office me --json            # 您的离岗状态
basecamp people out-of-office me --start 2026-09-14 --end 2026-09-18 --json  # 设置离岗
basecamp people out-of-office me --clear --json    # 清除离岗
basecamp people add <id> --project <project>       # 将团队成员添加到项目
basecamp people remove <id> --project <project>    # 从项目中移除团队成员
```

`people update me` 编辑您自己的个人资料（简介、标题、姓名、电子邮件、位置、时区）；传递一个带有空值的标志来清除该字段。`people
out-of-office me` 显示您的离岗状态，使用 `--start`/`--end`（自然语言或 YYYY-MM-DD，结束时间不在开始时间之前）来设置它，或使用 `--clear` 来清除它。

`people list` 报告每个人的 `client` 标志。`people add`/`remove` 仅管理团队成员 —— 传递给它们的客户端 ID 在服务器端被丢弃，永远不会跨等级 —— 因此客户端有自己的动词：

```bash
basecamp people clients enable --in <project>                 # 打开客户端访问（首先执行此操作）
basecamp people clients list --in <project>                   # 项目上的客户端
basecamp people clients add <id|email|name> --in <project>    # 授予现有客户端用户
basecamp people clients invite annie@example.com --in <project>                 # 通过电子邮件邀请新客户端
basecamp people clients invite "Annie Bryan <annie@example.com>" --in <project> # ... 带有姓名
basecamp people clients invite - --in <project>               # 标准输入上每行一个邀请人
basecamp people clients remove <id|email|name> --in <project> # 撤销客户端的访问权限
basecamp people clients disable --in <project>                # 关闭客户端访问（在移除每个客户端后）
```

启用客户端是一个故意的单独步骤：它应用项目的默认客户端可见性（时间线和大多数工具共享；卡片表格、Campfire 和 Doors 私有），因此 `add`/`invite` 从不隐式启用，并在客户端关闭时回答 `forbidden` 并带有 `enable` 提示。`invite` 接受 `--company`（适用于每个邀请人）和 `--title`（仅适用于一个邀请人），并且是全有或全无：一个不是地址的令牌在本地被拒绝作为 `usage`（2）命名每个，服务器拒绝命名每个被拒绝的行，座位不足退出 `limit_exceeded`（10）—— 在所有情况下都没有人被邀请。`add`/`remove` 在通知中报告服务器未授予或撤销的 ID（已经在项目上，或不是客户端用户）。

### 搜索

```bash
basecamp search "query" --json                    # 全文搜索（限制为 20；--all 用于每个匹配项）
basecamp search "query" --sort recency --limit 20
basecamp search "query" --project Marketing       # 限制到一个项目（--in 也适用）
basecamp search "query" --type todo               # 按类型过滤：todo、message、document、comment，
                                                  #   card、file、ping、chat、check-in、event、folder，
                                                  #   forward、client
basecamp search "query" --creator me              # 按创建者过滤（姓名、电子邮件、ID 或 'me')
basecamp search "query" --since last_30_days      # last_7_days|last_30_days|last_90_days|last_12_months|forever
basecamp search "query" --file-type pdf           # 过滤附件：image、audio、video、pdf
basecamp search "query" --exclude-chat            # 掉落聊天/营火结果
basecamp search metadata --json                   # API 接受的记录和文件类型作为过滤器
```

### 通用显示

```bash
basecamp show <type> <id> --in <project> --json                   # 显示任何记录类型（默认包含最多 100 条评论）
basecamp show <type> <id> --all-comments --in <project> --json   # 需要每条评论时获取完整讨论
basecamp show <type> <id> --no-comments --in <project> --json    # 跳过额外的评论获取
# 类型：todo、todolist、message、comment、card、card-table、document（或省略 <type> 进行通用查找）

# 带有类型显示命令也支持 --comments / --all-comments / --no-comments：
basecamp todos show <id> --comments --json                        # 选择在类型显示上显示评论
basecamp cards show <id> --all-comments --json                    # 获取卡片上的所有评论
basecamp messages show <id> --no-comments --json                  # 抑制评论
# 所有可评论显示命令：todos、messages、cards、files、todolists、schedule、checkins、forwards、chat
```

## 配置

CLI 使用两个目录命名空间：`basecamp` 用于您的 Basecamp 身份和项目关系，`basecamp` 用于特定于工具的操作数据。

```
~/.config/basecamp/           # Basecamp 身份（不要读取凭证）
├── credentials.json          #   OAuth 令牌 — 永远不要读取或记录
├── client.json               #   已过时（以前是仅开发人员客户端注册；可以安全删除）
└── config.json               #   全局首选项（account_id、base_url、format）

~/.cache/basecamp/            # 工具缓存（易失性，自动管理）
├── completion.json           #   Tab 补全缓存
└── resilience/               #   Circuit breaker 状态

.basecamp/                    # 每个存储库配置（提交到 git）
└── config.json               #   项目默认值（project_id、account_id、todolist_id）
```

**每个存储库配置：** `.basecamp/config.json`
```json
{
  "project_id": "12345",
  "todolist_id": "67890"
}
```

**初始化：**
```bash
basecamp config init
basecamp config set project_id <id>
basecamp config set todolist_id <id>
```

**配置信任：**

本地/存储库配置中的权限密钥（`base_url`、`default_profile`、`profiles`）在明确信任之前被阻止。这防止了克隆存储库的配置重定向 OAuth 令牌。

```bash
basecamp config trust                    # 信任最近的 .basecamp/config.json
basecamp config trust /path/to/.basecamp/config.json  # 信任特定的配置文件
basecamp config trust --list             # 显示所有信任的配置
basecamp config untrust                  # 为最近的配置撤销信任
basecamp config untrust /path/to/.basecamp/config.json  # 为特定路径撤销信任
```

**检查上下文：**
```bash
cat .basecamp/config.json 2>/dev/null || echo "未配置项目"
```

**全局配置：** `~/.config/basecamp/config.json`（account_id、base_url、格式首选项）

## 错误处理

**一般诊断：**
```bash
basecamp doctor --json                            # 检查 CLI 健康、认证、连接性
```

**编码代理设置（非交互式）：**
```bash
basecamp setup agents                             # 安装技能 + 连接检测到的代理
basecamp setup agents --json                      # 结构化结果包
```
`setup agents` 安装基本技能并连接编码代理而不提示。选择由 `BASECAMP_SETUP_AGENT` (`claude`、`codex`、`all` 或 `none`）；未设置时自动检测 —— 检测到一个代理被连接，多个则只保留技能并显示每个代理的 `basecamp setup <id>` 命令。

**速率限制（429）：** CLI 自动处理回退。如果您看到 429 错误，请减少请求频率。

**认证错误：**
```bash
basecamp auth status                              # 检查认证
basecamp auth login                               # 重新认证
basecamp auth login --scope full                  # 全访问权限（默认；Launchpad 忽略）
basecamp auth login --scope read                  # 只读访问权限（Launchpad 忽略）
basecamp auth login --device-code                 # 带有手动浏览器说明的无头认证
basecamp auth login --with-token -P bot --account <id>  # 从标准输入导入个人访问令牌（管道输入）
basecamp auth login --expect-identity <id>        # 除非它认证为此身份，否则丢弃登录
basecamp profile create <name> --account <id> --expect-identity <id>  # 新个人资料也使用相同的断言
```

**网络错误 / 本地主机 URL：**
```bash
# 检查开发配置
cat ~/.config/basecamp/config.json
# 应该只包含：{"account_id": "<id>"}
# 如果指向本地主机，请移除 base_url/api_url
```

**未找到错误：**
```bash
basecamp auth status                              # 验证认证是否正常工作
cat ~/.config/basecamp/accounts.json              # 检查可用账户
```

**必需的参数是位置性的（不是标志）：**
- `basecamp todos create "Buy milk"`（不是 `--content`）
- `basecamp cards create "New feature"`（不是 `--title`）
- `basecamp messages create "Subject" "Body"`（不是 `--subject`）
- `basecamp chat post "Hello"`（不是 `--content`）
- `basecamp comments create <id> "Text"`（不是标志）
- `basecamp webhooks create "https://..." --in <project>`（不是 `--url`）
- `basecamp checkins answer create <question-id> "content"`（不是 `--question`）
- `--date YYYY-MM-DD` 对于 `checkins answer create` 是可选的；如果省略，它将默认为今天

**缺少参数错误（代码："usage"）：**
当缺少必要的位置参数时，CLI 会返回一个结构化的错误，指明具体的参数。使用以下方式获取信息：

```bash
$ basecamp todos create --json
{"ok": false, "error": "<content> required", "code": "usage", "retryable": false,
 "hint": "Usage: basecamp todos create <content>"}

$ basecamp comments create 123 --json
{"ok": false, "error": "<content> required", "code": "usage", "retryable": false, ...}
```

`error` 字段指明了缺失的 `<arg>` — 使用它来提示用户输入具体的值。

**可重试错误（`retryable`）：** 每个错误封装都包含一个布尔值 `retryable` — 当 CLI 将失败分类为暂时性错误（网络、超时、速率限制、电路开启、大多数 5xx/gateway 响应 — 但并非所有：507 和一些 500s 是最终判定）且重试可能改变结果时为 `true`，对于最终判定（用法、未找到、认证、禁止、验证、账户限制）和任何未分类的错误为 `false`。在决定是否重试时，应依据 `retryable` 而非 `code` 或 `error` — `false` 表示没有已知原因重试会有帮助，并非永久性的保证；它永远不会出现在成功封装中。

**URL 格式错误（curl 退出码 3）：** 内容中包含特殊字符。使用纯文本或正确转义的 HTML。

## 内置 jq 过滤功能

CLI 具有由 gojq 驱动的内置 `--jq` 标志 — 无需外部 `jq` 二进制文件。**始终优先使用 `--jq` 而非将输出重定向到外部 `jq`。**

```bash
# 从数据数组中提取字段
basecamp todos list --in <project> --jq '.data[] | select(.completed == false) | .title'
basecamp todos list --in <project> --jq '.data | length'
basecamp todos list --in <project> --jq '[.data[] | {id, title, status}]'

# 访问封装元数据
basecamp todos list --in <project> --jq '.breadcrumbs[0].cmd'
basecamp todos list --in <project> --jq '.meta.stats.requests'

# 过滤和转换
basecamp cards list --in <project> --jq '[.data[] | select(.completed == true) | .title]'
basecamp people list --jq '[.data[] | {name: .name, email: .email_address}]'
```

`--jq` 意味着 `--json` — 无需同时传递两者。字符串结果以纯文本形式打印；对象和数组以格式化的 JSON 打印。

## 退出码

| 退出码 | 含义 | 解决方法 |
|------|---------|-----|
| 0 | 成功 | — |
| 1 | 用法错误 | 查看 `basecamp <cmd> --help` |
| 2 | 未找到 | 验证 ID/URL 是否存在 |
| 3 | 认证错误 | `basecamp auth login` |
| 4 | 禁止 | 检查账户/项目权限 |
| 5 | 速率限制 | 等待并重试（弹性层会自动处理 Retry-After） |
| 6 | 网络错误 | 检查连接性，`basecamp doctor` |
| 7 | API 错误 | 重试；如果持续存在，请查看 `basecamp doctor` |
| 8 | 模糊 | 更加具体（使用 ID 而非名称） |

## 了解更多

- API 概念：https://github.com/basecamp/bc3-api#key-concepts
- CLI 仓库：https://github.com/basecamp/basecamp-cli
- API 覆盖范围：查看 CLI 仓库中的 API-COVERAGE.md 文件
