# Slack CLI

调用 `slack-cli` 二进制文件（通过 `brew install paymog/tap/slack-cli` 安装）。
真实来源是 [`paymog/slack-cli`](https://github.com/paymog/slack-cli)。它封装了 `korotovsky/slack-mcp-server` 引擎的行为，但默认情况下**打印 JSON**（底层的 MCP 服务器发出 CSV），因此输出可以干净地输入 `jq`。

## 输出

每个成功的命令默认打印**有效的 JSON**。列表/表格命令（频道、消息、用户、保存的项目、用户组）发出对象数组。
结构化变更直接暴露其结果字段；`conversations add` 返回 `channel`、可选的 `thread_ts` 和 `ts`。遗留的纯文本状态被包装为 `{"message":"…"}`。直接输入 `jq`：

```sh
slack-cli channels list | jq -r '.[].Name'
slack-cli conversations history '#general' --limit 1d | jq -r '.[].Text'
slack-cli users search alice | jq -r '.[].DMChannelID'
slack-cli conversations add C123 --thread-ts 123.456 -t "hello" | jq -r .ts
```

来自 CSV 支持的表格的字段值是字符串；使用 jq 的 `tonumber` 进行数值比较。`--raw` 打印底层的 CSV/文本或遗留的人类可读命令输出。

## 认证（任何命令之前都需要）

通过环境变量提供恰好一个凭证集（CLI 还读取存储的配置文件）：

```sh
export SLACK_MCP_XOXP_TOKEN=xoxp-...        # 用户 OAuth — 完整功能（推荐）
# 或
export SLACK_MCP_XOXB_TOKEN=xoxb-...        # 机器人令牌 — 仅限邀请的频道，无搜索
# 或
export SLACK_MCP_XOXC_TOKEN=xoxc-...        # 浏览器会话令牌  + 以下 cookie
export SLACK_MCP_XOXD_TOKEN=xoxd-...        # 浏览器 cookie d (隐身模式)
```

功能说明：
- **搜索** (`conversations search`，`users_search` 实时) 和 **未读消息** 最佳使用 `xoxp` 或浏览器 (`xoxc`/`xoxd`)。**机器人令牌无法搜索。**
- **保存的项目** (`saved …`) 仅需要浏览器令牌 (`xoxc`/`xoxd`)。
- `--govslack` / `SLACK_MCP_GOVSLACK=true` 路由到 slack-gov.com。

### 存储的配置文件（环境变量的替代方案）

```sh
slack-cli auth login [name]        # 提示输入模式 + 令牌；验证后再保存
slack-cli auth list                # * 标记默认
slack-cli auth default <name>
slack-cli --profile <name> <cmd>   # 对一个命令使用配置文件
slack-cli auth status              # 显示解析的来源 + 模式
slack-cli auth logout <name> [-f]
```

优先级：显式 `--xoxp/--xoxc/...` 标志或 `SLACK_MCP_*` 环境变量 → `--profile <name>` → 默认配置文件。显式令牌 + `--profile` 被拒绝为歧义。
`SLACK_CLI_PROFILE` 通过环境变量设置配置文件。

## 缓存（名称查找前先执行）

`#channel-name` / `@username` 查找和 `channels list` 需要热缓存。
缓存位于磁盘上，跨所有调用共享，因此刷新一次：

```sh
slack-cli cache refresh            # 获取用户 + 频道，将缓存写入磁盘
```

读取命令自动加载磁盘缓存（并在第一次运行时获取）。使用 `--no-cache` 跳过它 — 然后仅解析原始 ID (`C…`，`U…`，`D…`)，名称无法解析。

## 频道 / ID

`<channel>` 接受 ID (`C123…`)、名称 (`#general`) 或 DM (`@username`)。

## 读取命令

```sh
# 频道 (JSON 数组；字段：ID,Name,Topic,Purpose,MemberCount,Cursor)
slack-cli channels list [--types public_channel,private_channel,im,mpim] [--query foo] [--query-targets name,topic,purpose] [--sort popularity] [--limit 100] [--cursor C]
slack-cli channels me                      # 你所属的频道

# 对话历史和线程
slack-cli conversations history <channel> [--limit 1d|1w|30d|<count>] [--cursor C] [--activity]
slack-cli conversations replies <channel> <thread_ts>
# 分页：读取最后一个元素的 Cursor 字段，然后传递 `--limit='' --cursor <value>`。
# 未列出的 Slack 应用：1 分钟/请求和 15 条消息/页面的历史记录/回复。CLI 等待
# Retry-After 并跨进程共享槽位。设置 SLACK_MCP_UNLISTED_HISTORY=1
# 强制该限制。默认 --timeout 是 2m。不要在循环中猛击这些。

# 搜索（需要 xoxp 或浏览器令牌；机器人无法搜索）
slack-cli conversations search [query] \
  [--in-channel #general] [--in-dm @user] [--with @user] [--from @user] \
  [--before YYYY-MM-DD] [--after YYYY-MM-DD] [--on YYYY-MM-DD] [--during July] \
  [--threads-only] [--limit 20] [--cursor C]
# 作为查询的完整 Slack 消息 URL 仅返回该消息。

# 未读消息，优先级 DM > 合作伙伴 > 内部（最佳使用 xoxp 浏览器）
slack-cli conversations unreads [--types all|dm|group_dm|partner|internal] [--mentions-only] [--max-channels 50] [--max-messages-per-channel 10] [--include-muted]

# 用户 (JSON 数组包括 DMChannelID 以快速发送消息)
slack-cli users search <query> [--limit 10]

# 用户组
slack-cli usergroups list [--include-users] [--include-disabled]
slack-cli usergroups me <list|join|leave> [--usergroup-id S123]

# 保存的项目（仅浏览器令牌）
slack-cli saved list [--filter saved|completed|archived] [--limit 50]

# 附件（通过 ID 下载文件；始终可用，无需环境变量）。
slack-cli attachments get <file_id> [-o path]   # Fxxxxxxxxxx, 最大 5MB
```

## 写入 / 敏感命令（可选加入）

默认禁用 — 每个命令都需要在同一调用中设置相应的环境变量，因此代理不会意外发布或变更。允许列表形式 (`C123,D456`，或 `!C123` 表示除外的所有）限制可写入的频道。

```sh
SLACK_MCP_ADD_MESSAGE_TOOL=true  slack-cli conversations add <channel> -t "hello" [--thread-ts 123.456] [--content-type text/markdown|text/plain]
SLACK_MCP_ADD_MESSAGE_TOOL=true  slack-cli conversations add <channel> --blocks '<Block Kit JSON 数组>'
SLACK_MCP_MARK_TOOL=true         slack-cli conversations mark <channel> [--ts 123.456]
SLACK_MCP_REACTION_TOOL=true     slack-cli reactions add <channel> <timestamp> --emoji rocket
SLACK_MCP_REACTION_TOOL=true     slack-cli reactions remove <channel> <timestamp> --emoji rocket
slack-cli usergroups create --name "Eng" [--handle eng] [--description ...] [--channels C1,C2]
slack-cli usergroups update <usergroup_id> [--name ...] [--handle ...] [--channels ...]
slack-cli usergroups users-update <usergroup_id> --users U1,U2,U3
slack-cli saved update <item_id> <ts> [--mark completed] [--date-due <unix>]
slack-cli saved clear-completed
```

## 关键：多行 / 格式化发布

**任何多行、项目符号或代码密集型发布的默认值：使用 `--blocks`（Block Kit），而不是 `-t`。**

单行 `-t` 是可以的。对于任何包含换行符、项目符号、代码分隔符或反引号的内容：

1. 优先使用 `--blocks '<Block Kit JSON 数组>'`，以便 Slack 将标题/部分/分隔符渲染为单独的块。
2. 通过环境变量（或读取到环境变量的文件）传递负载 — 永远不要使用 shell 命令替换，也不要使用带反引号的内联文本。
3. 在每个块的 `mrkdwn` 文本中放入真实的 `\n`。不要依赖 markdown `-t` 通过代理 shell 保留换行符。

```sh
# 良好 — 通过环境变量使用 Block Kit（换行符 + 反引号幸存）
BLOCKS='[{"type":"section","text":{"type":"mrkdwn","text":"line1\n• 项目符号\n• 项目符号2"}}]'
SLACK_MCP_ADD_MESSAGE_TOOL=true slack-cli conversations add C123 --thread-ts 123.456 --blocks "$BLOCKS"

# 差 — heredoc / 带反引号的内联 markdown
# Shell 将 `...` 视为命令替换；项目符号会折叠；部分垃圾发布。
SLACK_MCP_ADD_MESSAGE_TOOL=true slack-cli conversations add C123 -t "$(cat <<'EOF'
# 标题带 `code`
• 项目符号
EOF
)"
```

### 删除错误的发布

`slack-cli` 没有**删除命令**。使用 Slack 的 Web API 和解析的 xoxp 令牌：

```sh
TOKEN=$(slack-cli auth token | jq -r .SLACK_MCP_XOXP_TOKEN)
# chat.delete 需要频道 + 消息 ts（例如 1783603079.714919 从回复）
curl -s -X POST https://slack.com/api/chat.delete \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json; charset=utf-8" \
  -d '{"channel":"C061WRT6XM5","ts":"1783603079.714919"}'
```

仅适用于您的令牌允许删除的消息（您自己的用户消息使用 `xoxp`，或机器人消息使用机器人令牌）。

### 发布前验证

发布多行内容后，重新阅读线程并检查：
- 项目符号粘在单行上
- 标题/代码分隔符后缺少换行符
- 截断或 shell 错误片段（`command not found`，半吃掉的反引号）

如果出现任何这些情况，使用 `chat.delete` 删除，然后使用 `--blocks` 重新发布。

## 配方

```sh
# 筛选未读 DM 和提及
slack-cli cache refresh
slack-cli conversations unreads --types dm
slack-cli conversations unreads --mentions-only

# 查找线程，然后读取其回复
slack-cli conversations search "deploy rollback" --in-channel #incidents --after 2024-06-01
slack-cli conversations replies C0123456789 1718000000.123456

# 某人的身份，然后 DM 他们（需要 SLACK_MCP_ADD_MESSAGE_TOOL）
slack-cli users search alice            # 注意 DMChannelID，例如 D0123
SLACK_MCP_ADD_MESSAGE_TOOL=D0123 slack-cli conversations add D0123 -t "ping"

# 频道的最后一天作为 JSON，使用 jq 提取消息文本
slack-cli conversations history #general --limit 1d | jq -r '.[].Text'

# 下载图像（或任何二进制）附件到文件。 -o 写入解码后的字节并保留 stdout 到小的元数据 JSON — 用于图像/二进制，以免 MB 级别的 base64 片段淹没终端。
slack-cli attachments get F0123ABCD -o avatar.png
# 没有 -o 字节会内联返回，base64 编码在 .content 下 — 解码：
slack-cli attachments get F0123ABCD | jq -r .content | base64 --decode > avatar.png
```

## 常见问题

- **`no Slack credentials`** — 设置 `SLACK_MCP_XOXP_TOKEN`（或 xoxb，或 xoxc+xoxd）
  或运行 `slack-cli auth login`。
- **`users cache is not ready` / 空的 `channels list` / `#name not found`** —
  运行 `slack-cli cache refresh` 优先，或使用 `--no-cache` 传递 ID。
- **`conversations_add_message tool is disabled` / reactions / mark disabled** —
  在同一命令中设置匹配的环境变量（`SLACK_MCP_ADD_MESSAGE_TOOL`，`SLACK_MCP_REACTION_TOOL`,
  `SLACK_MCP_MARK_TOOL`）。(`attachments get` 无需环境变量。)
- **搜索 / 保存 / 未读消息返回空或错误** — 机器人令牌 (`xoxb`)
  无法搜索且缺乏边缘 API；使用 `xoxp` 或浏览器令牌。`saved` 需要
  浏览器令牌。
- **首次运行缓慢** — 初始 `cache refresh`（或无缓存的第一次读取）
  搜索整个工作区；后续调用读取缓存的文件。
- **多行发布看起来损坏（项目符号在单行上 / 反引号执行）** —
  shell 吃掉了正文。**不要**使用 heredoc 或带反引号的内联 `-t`
  进行多行发布。使用 `--blocks` + 环境变量 JSON（见 **关键：多行 /
  格式化发布**）。使用 `chat.delete` 删除错误消息，然后重新发布。
- **需要删除消息** — 没有 CLI 子命令；调用 `https://slack.com/api/chat.delete`
  使用 `slack-cli auth token` 中的 xoxp 令牌（见配方）。
