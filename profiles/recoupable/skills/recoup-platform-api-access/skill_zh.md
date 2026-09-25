# Recoup — API 访问

平台访问层：验证身份、与 Recoup REST API 通信，并调用外部连接器。基础 `https://api.recoupable.dev/api`；文档 `https://docs.recoupable.dev` (`/llms.txt`, `/llms-full.txt`, OpenAPI JSON 文件)。

## 认证 — 一个 Bearer 头部，内联

每个调用都使用相同的头部，直接放入 `curl`（无需设置步骤）：沙盒设置其中一个变量，API 接受 `recoup_sk_` 键或通过 `Bearer` 传递的 Privy JWT。

```bash
curl -sS -H "Authorization: Bearer ${RECOUP_API_KEY:-$RECOUP_ACCESS_TOKEN}" \
  "https://api.recoupable.dev/api/artists/{id}/socials"
```

如果这两个变量都没有设置，请要求用户进行身份验证——不要盲目重试。

## 首先选择艺术家模式（此处猜测会生成艺术家）

- **A — 任何艺术家研究**（一个名称；不查找阵容）→ 研究端点。
- **B — 浏览我的阵容** → 阵容发现（下方）。
- **C — 一个特定的阵容艺术家** → 阵容发现，匹配名称，捕获 `account_id` + 行 `id`。
- **D — 添加艺术家** → 使用 recoup-roster-add-artist。

**阵容发现：** `GET /accounts/id` → `GET /artists`（您的阵容；`org_id` 可选——组织通常是空的，所以当 `organizations` 为 `[]` 时不要停止）。

> **对于每个 `/artists/{id}/*` 子资源，使用 `account_id` 而不是列表 `id**`
>（`socials/posts/fans` 键位于 `account_id`；列表的顶层 `id` 会返回 404）。并且
> **社交信息嵌入在 `/artists` 响应中作为 `account_socials**`
> (`username`, `followerCount`, `profile_url`)——在调用 `/artists/{account_id}/socials` 之前先读取它们。

**停止规则——永远不要凭空创建阵容：** 如果 `GET /accounts/id` 解析为 `agent+…@recoupable.com` 邮箱，或者 `organizations` 和 `artists` 都返回 `[]`，这是一个一次性密钥——说明这一点并要求一个真实账户密钥（或 recoup-platform-connect-account）。不要凭空创建艺术家/阵容以继续进行。

**停止规则——永远不要凭空创建指标/数据：** 仅报告本次运行中从成功调用中检索到的数据。如果调用出错或返回空，或者没有指标连接器（`GET /connectors/actions` → 检查 `isConnected`），**说明这一点并省略它**——永远不要估计、使用“行业平均水平”，或用样本/占位符数字填充空白。简短准确的报告胜过填充的、凭空编造的报告。

**在您放弃缺失数据之前——获取它，或返回连接链接。** 当指标的源未连接时，在省略之前按以下列表操作：
1. **抓取您可以获取的公开数据** — `POST /api/socials/{social_id}/scrape`
   （一个个人资料）或 `POST /api/artist/socials/scrape`（一位艺术家的所有）。适用于 TikTok / Instagram / X / YouTube / Threads / Facebook。报告这些真实的公开数字。
2. **检查连接状态** — `GET /api/connectors` → 每个连接器的 `isConnected`。
3. **生成连接链接** — `POST /api/connectors {"connector":"youtube"}` 返回
   `{ redirectUrl }`（一个 Composio OAuth URL）。向调用者展示它，以便用户可以自行连接：*"CPM/收入需要 YouTube Analytics — 在这里连接：{redirectUrl}"*。

返回真实公开数据 **加上** 连接链接——这比凭空编造的报告和空/省略的报告都更好。

## 文档映射（拉取您需要的部分；不要猜测路径）

账户与身份 · 艺术家与内容 · 研究（Songstats + Web）· 社交集成 · 聊天与代理 · 开发者/基础设施。通过 `llms-full.txt` 的 `grep` 或拉取该区域的 OpenAPI JSON 来找到确切的路径/参数，例如：

```bash
curl -s https://docs.recoupable.dev/llms-full.txt | grep -A 30 -i "similar artists"
curl -s https://docs.recoupable.dev/api-reference/openapi/research.json | jq '.paths | keys'
```

地理位置来自 `audience`；发现来自 `similar` + `web`。

## 连接器操作（Google Docs/Sheets/Drive, Gmail, TikTok, Instagram）

对于 Recoup **外部** 的读取/写入：
- `GET /connectors/actions` — 目录（每个操作的 `slug`, `parameters`
  模式, `connectorSlug`, `isConnected`）。
- `POST /connectors/actions` `{actionSlug, parameters}` — 执行一个。

Slugs 是 `UPPERCASE_SNAKE_CASE`（例如 `GOOGLEDOCS_UPDATE_DOCUMENT_MARKDOWN`,
`GMAIL_FETCH_EMAILS`）。**在执行之前始终从目录中拉取参数模式**——每个操作的形状不同。触发启发式：粘贴的 `docs.google.com`/`drive.google.com`/`sheets.google.com` URL，或“编辑此文档”、“发送电子邮件”、“在 TikTok 上发布”。

## 从 Recoup 发送电子邮件

`POST /api/emails` 通过 Recoup 从 `Agent by Recoup <agent@recoupable.com>` 发送电子邮件——无需 Gmail 连接器即可在无头模式下工作。用于报告、警报和计划任务输出。

使用 `bash` 运行它（不要 `web_fetch`——那会隐藏响应，并且您无法确认收件人）：

```bash
curl -sS -X POST -H "Authorization: Bearer ${RECOUP_API_KEY:-$RECOUP_ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"to":["someone@example.com"],"subject":"Weekly report","text":"# Summary\n…"}' \
  "https://api.recoupable.dev/api/emails"
# → {"success":true,"message":"Email sent successfully … to someone@example.com.","id":"<resend-id>"}
```

`to` 是一个 JSON 数组，包含电子邮件字符串（`["a@b.com"]`——不是裸字符串，也不是 `[{"email":…}]`）。唯一的键是 `to`, `cc`, `subject`, `text`, `html`, `chat_id`, `account_id`；未知键（例如 `recipients`）会被丢弃，并且 `to` 会默认为您自己的账户电子邮件——静默地错误路由消息。`subject` 是可选的。读取响应并检查 `message` 是否命名了您打算的收件人。没有支付方式记录 → `to`/`cc` 限制为账户自己的电子邮件（403）。要作为用户从他们自己的 Gmail 发送，请使用 `GMAIL_SEND_EMAIL`。

## 故障排除

401 = 缺少/过期令牌（检查凭证）。403 = 没有对组织/艺术家的访问权限。404 = 重新检查文档映射（端点已移动/重命名）。5xx = 重试一次，然后显示状态。

## 不应使用的情况

- 沙盒中的文件 → 文件系统工具。
- 在线/操作艺术家的工位 → recoup-roster-* 技能。
- 一个域任务（研究/内容/发布/交易/歌曲）→ 该域技能，它会自行调用。
