# gog

使用 `gog` 来操作 Gmail/日历/云端硬盘/联系人/表格/文档。需要 OAuth 配置。

优先使用已授权的主机账户：先运行请求的 `gog` 命令。只有在出现认证错误后才能进行设置。聊天中切勿要求密码、客户端密钥或刷新令牌。

设置（只需一次）

- `gog auth credentials /path/to/client_secret.json`
- `gog auth add you@gmail.com --services gmail,calendar,drive,contacts,docs,sheets`
- `gog auth list`

远程/无头网关主机

当网关主机没有本地浏览器显示时：

1. 优先在网关主机上使用实时回调监听器。从有浏览器的机器上，将确切的回调端口 (`ssh -L <port>:127.0.0.1:<port> user@gateway-host`) 转发，打开 `gog` 打印的授权 URL，并在该转发端口上完成重定向。
2. 当实时监听器不可用时，操作员在网关主机上的可信 Shell 中选择一个粘贴模式路径。回调 URL 绝不能进入聊天或代理工具输入：
   - `--manual`：操作员将完整的重定向 URL 粘贴到 `gog` 的交互式提示符中。
   - `--remote --step 1`：打印 `auth_url`（和 `state_reused`）然后退出。浏览器同意后，操作员在可信 Shell 中运行 `--remote --step 2 --auth-url <callback-url>`。同意后预期会出现 `localhost` 页面加载失败。
3. 在远程步骤中保持相同的解析配置上下文：`GOG_CONFIG_DIR` 优先于 `--home`，`--home` 优先于 `GOG_HOME`。同时保留 `--client`、服务/范围、重定向 URI 和同意选项。可以重用未过期的手动状态 (`state_reused=true`)。
4. 如果桌面密钥库不可用，配置文件后端 (`gog auth keyring file`) 并在网关环境中设置 `GOG_KEYRING_PASSWORD`，以便非交互式代理/`--no-input` 运行可以读取令牌。`gog auth doctor` 在密码缺失时报告。
5. 收到的回调与存储的令牌不同。如果代理后令牌交换或身份查找失败，在操作员批准了所需 Google 端点的范围出站或代理例外后，从步骤 1 重新开始。不要绕过主机网络策略或重用失败或过期的状态。

用于诊断，检查 `gog auth list --check` 报告的每个条目；其退出状态并不能证明所有存储的令牌都有效。同样，检查 `gog auth doctor` 报告的状态，而不是仅依赖其退出代码。

常用命令

- Gmail 搜索：`gog gmail search 'newer_than:7d' --max 10`
- Gmail 消息搜索（每个邮件，忽略线程）：`gog gmail messages search "in:inbox from:ryanair.com" --max 20 --account you@example.com`
- Gmail 发送（纯文本）：`gog gmail send --to a@b.com --subject "Hi" --body "Hello"`
- Gmail 发送（多行）：`gog gmail send --to a@b.com --subject "Hi" --body-file ./message.txt`
- Gmail 发送（stdin）：`gog gmail send --to a@b.com --subject "Hi" --body-file -`
- Gmail 发送（HTML）：`gog gmail send --to a@b.com --subject "Hi" --body-html "<p>Hello</p>"`
- Gmail 草稿：`gog gmail drafts create --to a@b.com --subject "Hi" --body-file ./message.txt`
- 发送草稿：`gog gmail drafts send <draftId>`
- Gmail 回复：`gog gmail send --to a@b.com --subject "Re: Hi" --body "Reply" --reply-to-message-id <msgId>`
- 日历列出事件：`gog calendar events <calendarId> --from <iso> --to <iso>`
- 日历创建事件：`gog calendar create <calendarId> --summary "Title" --from <iso> --to <iso>`
- 带颜色的日历创建：`gog calendar create <calendarId> --summary "Title" --from <iso> --to <iso> --event-color 7`
- 日历更新事件：`gog calendar update <calendarId> <eventId> --summary "New Title" --event-color 4`
- 日历显示颜色：`gog calendar colors`
- 云端硬盘搜索：`gog drive search "query" --max 10`
- 联系人：`gog contacts list --max 20`
- 表格获取：`gog sheets get <sheetId> "Tab!A1:D10" --json`
- 表格更新：`gog sheets update <sheetId> "Tab!A1:B2" --values-json '[["A","B"],["1","2"]]' --input USER_ENTERED`
- 表格追加：`gog sheets append <sheetId> "Tab!A:C" --values-json '[["x","y","z"]]' --insert INSERT_ROWS`
- 表格清除：`gog sheets clear <sheetId> "Tab!A2:Z"`
- 表格元数据：`gog sheets metadata <sheetId> --json`
- 文档导出：`gog docs export <docId> --format txt --out /tmp/doc.txt`
- 文档显示：`gog docs cat <docId>`

日历颜色

- 使用 `gog calendar colors` 查看所有可用的事件颜色（ID 1-11）
- 使用 `--event-color <id>` 标志为事件添加颜色
- 事件颜色 ID（来自 `gog calendar colors` 输出）：
  - 1: #a4bdfc
  - 2: #7ae7bf
  - 3: #dbadff
  - 4: #ff887c
  - 5: #fbd75b
  - 6: #ffb878
  - 7: #46d6db
  - 8: #e1e1e1
  - 9: #5484ed
  - 10: #51b749
  - 11: #dc2127

邮件格式

- 优先使用纯文本。使用 `--body-file` 发送多段落消息（或 `--body-file -` 用于 stdin）。
- 同样的 `--body-file` 模式适用于草稿和回复。
- `--body` 不会转义 `\n`。如果需要内联换行，请使用 heredoc 或 `$'Line 1\n\nLine 2'`。
- 仅在需要富格式时使用 `--body-html`。
- HTML 标签：`<p>` 用于段落，`<br>` 用于换行，`<strong>` 用于加粗，`<em>` 用于斜体，`<a href="url">` 用于链接，`<ul>`/`<li>` 用于列表。
- 示例（通过 stdin 发送纯文本）：

  ```bash
  gog gmail send --to recipient@example.com \
    --subject "会议跟进" \
    --body-file - <<'EOF'
  您好 Name，

  感谢今天的会议。下一步：
  - 项目一
  - 项目二

  此致，
  您的姓名
  EOF
  ```

- 示例（HTML 列表）：
  ```bash
  gog gmail send --to recipient@example.com \
    --subject "会议跟进" \
    --body-html "<p>你好 Name,</p><p>感谢今天的会议。以下是下一步：</p><ul><li>项目一</li><li>项目二</li></ul><p>此致,<br>你的姓名</p>"
  ```

注意

- 设置 `GOG_ACCOUNT=you@gmail.com` 以避免重复 `--account`。
- 对于脚本，优先使用 `--json` 加上 `--no-input`。
- 表格值可以通过 `--values-json` 传递（推荐）或作为行内行传递。
- 文档支持导出/显示/复制。就地编辑需要 Docs API 客户端（不在 gog 中）。
- 发送邮件或创建事件前请确认。
- `gog gmail search` 每个线程返回一行；需要每个单独的邮件返回时使用 `gog gmail messages search`。
