---
name: recoup-platform-api-access
description: 直接调用 Recoup API 和外部连接器——获取任何平台资源（艺术家、社交平台、组织机构、研究资料、文档），并执行连接器操作（如 Google Docs/Sheets/Drive 编辑、Gmail、TikTok、Instagram）。在需要原始 Recoup 数据、平台资源，用于对 api.recoupable.dev 编写 curl 命令，或读取/写入 Recoup 外部的 Google 文档链接或电子表格时使用。这是其他所有技能所依赖的基础设施。要为艺术家进行上线或操作，请使用 recoup-roster-* 技能；首次连接时使用 recoup-platform-connect-account。
---

# Recoup — API 访问

平台访问层：验证身份、与 Recoup REST API 通信，并调用外部连接器。基础 `https://api.recoupable.dev/api`；文档 `https://docs.recoupable.dev` (`/llms.txt`, `/llms-full.txt`, OpenAPI JSON 文件)。

## 认证 — 一个 Bearer 头部，内联

每个调用都使用相同的头部，直接放入 `curl`（无需设置步骤）：沙盒设置其中一个变量，API 接受 `recoup_sk_` 键或通过 `Bearer` 传递的 Privy JWT。

```bash
curl -sS -H "Authorization: Bearer ${RECOUP_API_KEY:-$RECOUP_ACCESS_TOKEN}" \
  "https://api.recoupable.dev/api/artists/{id}/socials"
```

如果这两个变量都没有设置，请要求用户进行身份验证——不要盲目重试。

## 首先选择艺术家模式（这里猜测会创建艺术家）

- **A — 任何艺术家研究**（一个名称；不查找阵容）→ 研究端点。
- **B — 浏览我的阵容** → 阵容发现（下文）。
- **C — 一个特定的阵容艺术家** → 阵容发现，匹配名称，捕获 `account_id` + 行 `id`。
- **D — 添加一个艺术家** → 使用 recoup-roster-add-artist。

**阵容发现：** `GET /accounts/id` → `GET /artists`（您的阵容；`org_id` 可选 — 组织通常是空的，所以当 `organizations` 为 `[]` 时不要停止）。

> **对于每个 `/artists/{id}/*` 子资源，使用 `account_id` 而不是列表 `id**`
>（`socials/posts/fans` 键在 `account_id` 上；列表的顶层 `id` 会返回 404）。并且
> **社交信息嵌入在 `/artists` 响应中作为 `account_socials**`
> (`username`, `followerCount`, `profile_url`) — 在调用 `/artists/{account_id}/socials` 之前先读取它们。

**停止规则 — 不要编造阵容：** 如果 `GET /accounts/id` 解析为 `agent+…@recoupable.com` 邮箱，或者 `organizations` 和 `artists` 都返回 `[]`，这是一个一次性密钥——说明这一点并要求一个真实账户密钥（或 recoup-platform-connect-account）。不要编造艺术家/阵容以继续进行。

**停止规则 — 不要编造指标/数据：** 只报告您在本轮调用中检索到的数字。如果调用出错或返回空，或者没有指标连接器（`GET /connectors/actions` → 检查 `isConnected`），**说明这一点并省略它** — 不要估计、使用“行业平均水平”，或用样本/占位符数字填充空白。简短准确的报告胜过填充的、编造的报告。

**在您放弃缺失数据之前 — 获取它，或返回连接链接。** 当指标的源未连接时，在省略之前按以下列表操作：
1. **抓取您可以获取的公共数据** — `POST /api/socials/{social_id}/scrape`
   （一个个人资料）或 `POST /api/artist/socials/scrape`（一位艺术家的所有）。适用于 TikTok / Instagram / X / YouTube / Threads / Facebook。报告这些真实的公共数字。
2. **检查连接状态** — `GET /api/connectors` → 每个连接器的 `isConnected`。
3. **生成连接链接** — `POST /api/connectors {"connector":"youtube"}` 返回
   `{ redirectUrl }`（一个 Composio OAuth URL）。向调用者展示它，以便用户可以自行连接：*"CPM/收入需要 YouTube Analytics — 在这里连接：{redirectUrl}"*。

返回真实公共数据 **加上** 连接链接——这比编造的报告和空/省略的报告都好。

## 文档映射（拉取您需要的部分；不要猜测路径）

账户与身份 · 艺术家与内容 · 研究（Songstats + Web） · 社交集成 · 聊天与代理 · 开发者/基础设施。通过 `llms-full.txt` 搜索或拉取相应区域的 OpenAPI JSON 来找到确切的路径/参数，例如：

```bash
curl -s https://docs.recoupable.dev/llms-full.txt | grep -A 30 -i "similar artists"
curl -s https://docs.recoupable.dev/api-reference/openapi/research.json | jq '.paths | keys'
```

地理位置来自 `audience`；发现来自 `similar` + `web`。

## 连接器操作（Google Docs/Sheets/Drive, Gmail, TikTok, Instagram）

用于 Recoup **外部** 的读取/写入：
- `GET /connectors/actions` — 目录（每个操作的 `slug`, `parameters`
  模式, `connectorSlug`, `isConnected`）。
- `POST /connectors/actions` `{actionSlug, parameters}` — 执行一个。

Slugs 是 `UPPERCASE_SNAKE_CASE`（例如 `GOOGLEDOCS_UPDATE_DOCUMENT_MARKDOWN`,
`GMAIL_FETCH_EMAILS`）。**在执行之前始终从目录中拉取参数模式** — 每个操作的形状不同。触发启发式：粘贴的
`docs.google.com`/`drive.google.com`/`sheets.google.com` URL，或“编辑此文档”、“发送电子邮件”、“在 TikTok 上发布”。

## 从 Recoup 发送电子邮件

`POST /api/emails` 通过 Recoup 从 `Agent by Recoup <agent@recoupable.com>` 发送电子邮件——使用 API 密钥可无头运行，无需 Gmail 连接器。用于报告、警报和计划任务输出。

使用 `bash` 运行它（不是 `web_fetch` — 那会隐藏响应，并且您无法确认收件人）：

```bash
curl -sS -X POST -H "Authorization: Bearer ${RECOUP_API_KEY:-$RECOUP_ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"to":["someone@example.com"],"subject":"Weekly report","text":"# Summary\n…"}' \
  "https://api.recoupable.dev/api/emails"
# → {"success":true,"message":"Email sent successfully … to someone@example.com.","id":"<resend-id>"}
```

`to` 是一个 JSON 数组，包含电子邮件字符串（`["a@b.com"]` — 不是裸字符串，也不是 `[{"email":…}]`）。唯一的键是 `to`, `cc`, `subject`, `text`, `html`,
`chat_id`, `account_id`；未知键（例如 `recipients`）会被丢弃，并且 `to`
然后默认为您自己的账户电子邮件——静默地重定向消息。`subject` 是可选的。读取响应并检查 `message` 指出了您打算的收件人。没有支付方式记录 → `to`/`cc` 限制为账户自己的电子邮件（403）。要作为用户从他们自己的 Gmail 发送，请使用 `GMAIL_SEND_EMAIL`。

## 故障排除

401 = 缺少/过期令牌（检查凭证）。403 = 没有对组织/艺术家的访问权限。404 = 重新检查文档映射（端点已移动/重命名）。5xx = 重试一次，然后显示状态。

## 不应使用的情况

- 沙盒中的文件 → 文件系统工具。
- 在线/操作艺术家的工位 → recoup-roster-* 技能。
- 一个域任务（研究/内容/发布/交易/歌曲）→ 该域技能，它会自行调用。
