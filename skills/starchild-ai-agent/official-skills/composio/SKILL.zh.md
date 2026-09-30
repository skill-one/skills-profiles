---
name: composio
description: 'Composio网关：可操作1000多个已连接的应用，如Gmail、Slack、GitHub、日历。


  当用户希望在一个已连接的SaaS应用中执行操作时使用（例如：发送Gmail、创建Notion页面、添加日历事件、打开GitHub问题）。'
---

# Composio — 通过网关进行外部应用集成

Composio 允许用户将 1000 多个外部应用（如 Gmail、Slack、GitHub、Google 日历、Notion 等）连接到他们的 Starchild 代理。所有操作都通过 **Composio 网关** (`composio-gateway.fly.dev`) 进行，该网关负责处理身份验证和 API 密钥管理。

## 架构

```
Agent (Fly 6PN 网络)
    ↓  HTTP (通过 IPv6 自动进行身份验证)
Composio Gateway (composio-gateway.fly.dev)
    ↓  Composio SDK
Composio Cloud → 目标 API (Gmail、Slack、等)
```

- **你永远不会直接接触 COMPOSIO_API_KEY** — 网关会持有它
- **你永远不会直接调用 Composio SDK** — 使用网关的 HTTP API
- **身份验证是自动的** — 你的 Fly 6PN IPv6 通过计费数据库解析为 user_id
- **不需要环境变量** — 网关可以从任何代理容器中始终访问

## 网关基本 URL

```
GATEWAY = "http://composio-gateway.flycast"
```

所有请求都使用 **通过 Fly 内部网络传输的纯 HTTP** (flycast)。不需要 JWT。

**关键提示 — 永远不要将网关通过 sc-proxy 路由：**
- 使用 **curl**（如下面的示例所示）或纯 `requests` / `http.client` 并**不使用代理**。
- **不要**对主机使用 `proxied_get` / `proxied_post`（即使 PROTOCOL 说“外部 API 始终需要代理” — flycast 是文档中的例外；`core.http_client` 也会自动绕过 `*.flycast`）。
- **不要**设置 `HTTP_PROXY` / `HTTPS_PROXY` 或 `curl -x` 指向网关。
- 代理会重写调用者的身份，导致网关看到错误的用户，连接/执行失败或触发另一个锁。

## API 参考

### 1. 搜索工具（简洁版）

为任务找到正确的工具 slug。返回 **简洁** 的工具信息 — 仅包括 slug、描述和参数名称。足够用来选择正确的工具。

```bash
curl -s -X POST $GATEWAY/internal/search \
  -H "Content-Type: application/json" \
  -d '{"query": "通过 gmail 发送邮件"}'
```

**响应（简洁版）：**
```json
{
  "results": [{"primary_tool_slugs": ["GMAIL_SEND_EMAIL"], "use_case": "发送邮件", ...}],
  "tool_schemas": {
    "GMAIL_SEND_EMAIL": {
      "tool_slug": "GMAIL_SEND_EMAIL",
      "toolkit": "gmail",
      "description": "发送邮件...",
      "parameters": ["to", "subject", "body", "cc", "bcc"],
      "required": ["to", "subject", "body"]
    }
  },
  "toolkit_connection_statuses": [...]
}
```

### 2. 获取工具模式（完整版）

获取特定工具的**完整**参数定义 — 类型、描述、枚举、默认值。在搜索后需要确切的参数格式时使用。

```bash
curl -s -X POST $GATEWAY/internal/tool_schema \
  -H "Content-Type: application/json" \
  -d '{"tool": "GOOGLECALENDAR_EVENTS_LIST"}'
```

**响应：**
```json
{
  "data": {
    "tool_slug": "GOOGLECALENDAR_EVENTS_LIST",
    "description": "返回指定日历上的事件。",
    "input_parameters": {
      "properties": {
        "timeMin": {"type": "string", "description": "RFC3339 时间戳..."},
        "timeMax": {"type": "string", "description": "RFC3339 时间戳..."},
        "calendarId": {"type": "string", "default": "primary"}
      },
      "required": ["calendarId"]
    }
  },
  "error": null
}
```

### 3. 执行工具

执行 Composio 工具。**关键名称是 `arguments`，而不是 `params`。**

```bash
curl -s -X POST $GATEWAY/internal/execute \
  -H "Content-Type: application/json" \
  -d '{"tool": "GMAIL_SEND_EMAIL", "arguments": {"to": "x@example.com", "subject": "Hi", "body": "Hello!"}}'
```

**成功时：**
```json
{"data": {"messages": [...]}, "error": null}
```

**失败时** — 包括工具模式，以便你可以自行纠正：
```json
{
  "data": null,
  "error": "缺少必需参数：calendarId",
  "tool_schema": {
    "tool_slug": "GOOGLECALENDAR_EVENTS_LIST",
    "description": "...",
    "input_parameters": {"properties": {...}, "required": [...]}
  }
}
```

### 4. 列出用户的连接（并确认 OAuth 完成）

```bash
# 可选工具包过滤器：oauth_completed_active 仅在工具包状态为 ACTIVE 时才为 true。
curl -s "$GATEWAY/internal/connections?toolkit=gmail"
```

响应包括：
- `connections`：当前的连接列表
- `oauth_completed_active`：布尔值，仅在观察到 OAuth 完成为 `ACTIVE` 时为 true

缓存失效仅在观察到 `ACTIVE` 后才会触发，并且它针对的是用户的实例（`fly-force-instance-id=<用户容器 ID 从 user_mapping>`），而不是 composio-gateway 自己的实例。

### 5. 启动新连接

```bash
curl -s -X POST $GATEWAY/api/connect \
  -H "Content-Type: application/json" \
  -d '{"toolkit": "gmail"}'
```

返回 `connect_url`，用户需要完成 OAuth。

### 无摩擦连接（执行操作时必须）

仅在用户想要在**外部应用**（发送/读取邮件、创建日历事件、打开 GitHub 问题、发布等）中**执行操作**且该应用**尚未连接**时触发

**不要**对纯问答/解释（“Gmail 是什么？”“日历如何工作？”）触发。

1. **不要**描述连接检查、空列表、OAuth 机制或询问“要我连接吗？”。
2. 在**Web**（活动 SSE 会话）上：调用**一个主要**工具包的内置工具：
   ```
   frontend_action(action_type="composio_connect", toolkit="gmail")
   ```
   可选：`display_name="Gmail"`，`title=...`，`description=...`。
   使用正确的**小写**工具包 slug。**不要**粘贴 `connect_url` 的 Markdown 链接 — 前端会从 action_request 渲染一个连接卡片。
3. 可见回复：**一句话**说明你将在他们连接后做什么（不要使用 Emoji 界面，不要使用授权 URL）。
4. **停止并等待**用户完成 OAuth / 完成，然后继续原始任务。
5. **不要**先让用户去浏览连接页面。
6. **备用方案**（没有 SSE / 非网页通道，或 `frontend_action` 失败）：
   ```bash
   curl -s -X POST $GATEWAY/api/connect \
     -H "Content-Type: application/json" \
     -d '{"toolkit": "gmail"}'
   ```
   然后以纯文本形式提供 `connect_url`（仍然不需要 Markdown 卡片软匹配）。
   如果这也失败了，用一句话说明并停止 — 不要编造替代设置流程。

### 6. 断开连接

```bash
curl -s -X DELETE $GATEWAY/api/connections/{connection_id}
```

### Instagram 发布（重要的 slug 映射）

Composio 搜索可能会返回在此环境中不可执行的传统 Instagram slugs。发布到 Instagram 时，使用这些**可用的 slugs**：

1) 创建草稿容器：
- `INSTAGRAM_CREATE_MEDIA_CONTAINER`
- 必需：`ig_user_id`
- 典型照片参数：`{"ig_user_id":"...","image_url":"https://...","content_type":"photo","caption":"..."}`

2) 发布草稿：
- `INSTAGRAM_CREATE_POST`
- 必需：`ig_user_id`，`creation_id`

两步流程：
- 执行 `INSTAGRAM_CREATE_MEDIA_CONTAINER` → 读取 `data.data.id` 作为 `creation_id`
- 使用该 `creation_id` 执行 `INSTAGRAM_CREATE_POST`

提示：如果 `/internal/search` 建议使用 `INSTAGRAM_POST_IG_USER_MEDIA` 或 `INSTAGRAM_POST_IG_USER_MEDIA_PUBLISH` 但执行返回“工具 ... 未找到”，切换到上面的两个 slugs。

### Browserbase — 混合工作流（会话管理 + Playwright CDP）

**Composio 的 Browserbase 工具仅管理会话生命周期（打开/关闭/列出）。它们不控制网页。**

要实际操作浏览器（导航、点击、填写表单、抓取数据），使用 **Playwright `connect_over_cdp`** 连接到会话的 WebSocket URL。

#### 第一步：通过 Composio 创建 Browserbase 会话

```bash
curl -s -X POST $GATEWAY/internal/execute \
  -H "Content-Type: application/json" \
  -d '{"tool": "BROWSERBASE_TOOL_SESSIONS_CREATE", "arguments": {"projectId": "YOUR_PROJECT_ID"}}'
```

响应包括 `id`（session_id），`status` 和时间戳。

#### 第二步：构建 CDP WebSocket URL

```python
import os
session_id = "<从第一步获取的 session_id>"
api_key = os.environ.get("BROWSERBASE_API_KEY")  # 存储在 workspace/.env 中
cdp_url = f"wss://connect.browserbase.com?apiKey={api_key}&sessionId={session_id}"
```

#### 第三步：使用 Playwright 控制浏览器

```python
from playwright.async_api import async_playwright

async with async_playwright() as p:
    browser = await p.chromium.connect_over_cdp(cdp_url)
    page = await browser.new_page()
    await page.goto("https://example.com")

    # 点击、填写、截图 — 完整 Playwright API
    await page.click("button.submit")
    await page.fill("input[name='email']", "user@test.com")
    await page.screenshot(path="result.png")

    content = await page.content()
```

#### 第四步：删除会话（重要 — 停止计费）

```bash
curl -s -X POST $GATEWAY/internal/execute \
  -H "Content-Type: application/json" \
  -d '{"tool": "BROWSERBASE_TOOL_SESSIONS_DELETE", "arguments": {"id": "YOUR_SESSION_ID"}}'
```

#### 关键概念

| 方面 | 详情 |
|------|------|
| **Composio 角色** | 会话生命周期管理 — 创建、列出、删除会话 |
| **Playwright 角色** | 页面控制 — 导航、点击、填写、抓取、截图 |
| **内存成本** | ~30-50MB 本地（仅 Playwright 客户端）；Chromium 在 Browserbase 服务器上运行 |
| **反检测** | Browserbase 在服务器端处理 — 指纹掩码、验证码解决、Cloudflare 绕过。Playwright 客户端不做特殊处理。 |
| **计费** | 按分钟计费（四舍五入）。完成时始终删除会话。 |

#### 完整示例脚本（创建 → 控制 → 清理）

```python
#!/usr/bin/env python3
"""Browserbase: 创建会话 → 使用 Playwright 控制 → 清理。"""
import asyncio, os, requests
from playwright.async_api import async_playwright

GATEWAY = "http://composio-gateway.flycast"
PROJECT_ID = os.environ.get("BROWSERBASE_PROJECT_ID")

async def main():
    # 1. 通过 Composio 创建会话
    resp = requests.post(f"{GATEWAY}/internal/execute", json={
        "tool": "BROWSERBASE_TOOL_SESSIONS_CREATE",
        "arguments": {"projectId": PROJECT_ID}
    }).json()
    session_id = resp["data"]["id"]
    print(f"会话创建：{session_id}")

    try:
        # 2. 通过 CDP 连接
        api_key = os.environ["BROWSERBASE_API_KEY"]
        cdp_url = f"wss://connect.browserbase.com?apiKey={api_key}&sessionId={session_id}"

        async with async_playwright() as p:
            browser = await p.chromium.connect_over_cdp(cdp_url)
            page = await browser.new_page()
            await page.goto("https://example.com")
            title = await page.title()
            print(f"页面标题：{title}")
            await browser.close()

    finally:
        # 3. 始终删除会话以停止计费
        requests.post(f"{GATEWAY}/internal/execute", json={
            "tool": "BROWSERBASE_TOOL_SESSIONS_DELETE",
            "arguments": {"id": session_id}
        })
        print("会话删除")

asyncio.run(main())
```

#### 可用的 Browserbase 工具（通过 Composio）

| 工具 Slug | 目的 | 关键参数 |
|-----------|------|----------|
| `BROWSERBASE_TOOL_SESSIONS_CREATE` | 创建浏览器会话 | `projectId` |
| `BROWSERBASE_TOOL_SESSIONS_DELETE` | 删除会话 | `id` |
| `BROWSERBASE_TOOL_SESSIONS_GET` | 获取会话信息 | `id` |
| `BROWSERBASE_TOOL_SESSIONS_LIST` | 列出所有会话 | (无) |
| `BROWSERBASE_TOOL_SESSIONS_GET_DEBUG_INFO` | 获取调试信息 | `id` |
| `BROWSERBASE_TOOL_SESSIONS_STOP` | 停止会话 | `id` |
| `BROWSERBASE_TOOL_CONTEXTS_CREATE` | 创建持久上下文 | `projectId` |
| `BROWSERBASE_TOOL_CONTEXTS_DELETE` | 删除上下文 | `id` |
| `BROWSERBASE_TOOL_CONTEXTS_GET` | 获取上下文信息 | `id` |
| `BROWSERBASE_TOOL_CONTEXTS_LIST` | 列出上下文 | (无) |
| `BROWSERBASE_TOOL_CONTEXTS_UPDATE` | 更新上下文标签 | `id`，`labels` |
| `BROWSERBASE_TOOL_UPLOADS_CREATE` | 将文件上传到会话 | `projectId`，文件数据 |
| `BROWSERBASE_TOOL_UPLOADS_GET` | 获取上传信息 | `id` |
| `BROWSERBASE_TOOL_UPLOADS_LIST` | 列出上传 | (无) |
| `BROWSERBASE_TOOL_UPLOADS_DELETE` | 删除上传 | `id` |
| `BROWSERBASE_TOOL_DOWNLOADS_LIST` | 列出下载 | `sessionId` |
| `BROWSERBASE_TOOL_DOWNLOADS_GET` | 获取下载 | `downloadId` |
| `BROWSERBASE_TOOL_DOWNLOADS_GET_STREAM` | 流式传输下载 | `downloadId` |
| `BROWSERBASE_TOOL_KB_GET_KNOWLEDGE` | 获取 KB 文章 | `id` |

### Browserbase / 浏览器工具故障排除

如果 Browserbase 已连接但执行失败，请检查**连接工具包**与**工具 slug** 之间的命名不匹配：

- 连接可能显示为工具包 `browserbase_tool`
- 搜索可能返回工具 slug 如 `BROWSER_TOOL_CREATE_TASK`
- 执行可能仍然拒绝该 slug (`Tool ... not found`)，而仅解析传统 slug 在工具包 `browserbase` 下

快速诊断：

```bash
# 1) 健康 + 活动连接
curl -s $GATEWAY/health
curl -s $GATEWAY/internal/connections

# 2) 搜索浏览器工具 slugs
curl -s -X POST $GATEWAY/internal/search \
  -H "Content-Type: application/json" \
  -d '{"query":"browserbase create task"}'

# 3) 尝试执行并检查确切错误
curl -s -X POST $GATEWAY/internal/execute \
  -H "Content-Type: application/json" \
  -d '{"tool":"BROWSER_TOOL_CREATE_TASK","arguments":{"task":"打开 https://example.com"}}'
```

如果错误说**未找到 toolkit 'browserbase' 的活动连接**，网关应在服务器端规范化 Browserbase 别名（`browser`/`browserbase`/`browserbase_tool`）并规范化执行 slug 变体（`BROWSERBASE_TOOL_*` ↔ `BROWSER_TOOL_*`），以便旧/新客户端在活动连接 `browserbase_tool` 下都能工作。

## 最佳工作流（最小化工具调用）

### 已知工具 → 直接执行（1 次调用）

如果你已经知道工具 slug 和参数（从之前的用法或下方的 Common Tools 表格），**完全跳过搜索**：

```bash
curl -s -X POST $GATEWAY/internal/execute \
  -H "Content-Type: application/json" \
  -d '{"tool": "GOOGLECALENDAR_EVENTS_LIST", "arguments": {"calendarId": "primary", "timeMin": "2026-04-02T00:00:00+08:00", "timeMax": "2026-04-09T00:00:00+08:00", "singleEvents": true, "timeZone": "Asia/Hong_Kong"}}'
```

### 未知工具 → 搜索 + 模式 + 执行（2-3 次调用）

1. **搜索**（简洁版）→ 选择正确的工具 slug
2. **获取模式**（如果参数细节不明确）→ 知道确切的参数格式
3. **执行** → 带正确参数

如果执行失败，错误响应**包括完整模式** — 因此你可以立即重试，而无需额外的模式调用。

### 封装在脚本中以供重复使用

对于定期查询，编写一个一次性 Python 脚本：

```python
#!/usr/bin/env python3
import sys, json, requests
from datetime import datetime, timedelta, timezone

GATEWAY = "http://composio-gateway.flycast"
days = int(sys.argv[1]) if len(sys.argv) > 1 else 7
tz_name = sys.argv[2] if len(sys.argv) > 2 else "UTC"

# ... 构建时间戳 ...
resp = requests.post(f"{GATEWAY}/internal/execute", json={
    "tool": "GOOGLECALENDAR_EVENTS_LIST",
    "arguments": {"calendarId": "primary", "timeMin": t_min, "timeMax": t_max,
                   "singleEvents": True, "timeZone": tz_name}
}).json()

# ... 格式化并打印 ...
```

然后未来的调用只是：`bash("python3 scripts/calendar_events.py 7 Asia/Hong_Kong")` — **1 次工具调用**。

## 常用工具快速参考（跳过搜索）

### 📧 Gmail

| 工具 Slug | 目的 | 关键参数 |
|-----------|------|----------|
| `GMAIL_SEND_EMAIL` | 发送邮件 | `to`，`subject`，`body`，`cc`，`bcc` |
| `GMAIL_FETCH_EMAILS` | 获取邮件 | `max_results` (int)，`label_ids` (list)，`q` (Gmail 搜索语法) |
| `GMAIL_CREATE_EMAIL_DRAFT` | 创建草稿 | `to`，`subject`，`body` |

**Gmail 使用示例：**

```bash
# 发送邮件
curl -s -X POST $GATEWAY/internal/execute \
  -H "Content-Type: application/json" \
  -d '{"tool": "GMAIL_SEND_EMAIL", "arguments": {"to": "user@example.com", "subject": "Hello", "body": "Hi there!"}}'

# 获取最后5封邮件
curl -s -X POST $GATEWAY/internal/execute \
  -H "Content-Type: application/json" \
  -d '{"tool": "GMAIL_FETCH_EMAILS", "arguments": {"max_results": 5}}'

# 搜索特定邮件（使用Gmail搜索语法）
curl -s -X POST $GATEWAY/internal/execute \
  -H "Content-Type: application/json" \
  -d '{"tool": "GMAIL_FETCH_EMAILS", "arguments": {"max_results": 10, "q": "from:github.com after:2026/03/01"}}'
```

**Gmail响应解析：** 邮件数据位于`data.data.messages[]`，每封邮件包含`id`、`snippet`、`payload.headers[]`（发件人/主题/日期位于headers中，通过名称查找）。

### 🐦 Twitter

| 工具缩写 | 用途 | 关键参数 |
|-----------|---------|---------------|
| `TWITTER_CREATION_OF_A_POST` | 创建推文 | `text`（必填）、`media_media_ids`、`reply_in_reply_to_tweet_id` |
| `TWITTER_POST_DELETE_BY_POST_ID` | 删除推文 | `id` |
| `TWITTER_POST_LOOKUP_BY_POST_ID` | 获取单条推文 | `id`、`tweet_fields` |
| `TWITTER_RECENT_SEARCH` | 搜索最近7天 | `query`、`max_results`（最小10） |
| `TWITTER_USER_LOOKUP_ME` | 获取自己的资料 | （无参数） |
| `TWITTER_USER_LOOKUP_BY_USERNAME` | 获取用户资料 | `username` |

**Twitter使用示例：**

```bash
# 发布推文
curl -s -X POST $GATEWAY/internal/execute \
  -H "Content-Type: application/json" \
  -d '{"tool": "TWITTER_CREATION_OF_A_POST", "arguments": {"text": "Hello from Composio!"}}'

# 删除推文
curl -s -X POST $GATEWAY/internal/execute \
  -H "Content-Type: application/json" \
  -d '{"tool": "TWITTER_POST_DELETE_BY_POST_ID", "arguments": {"id": "2039756730192601584"}}'
```

**Twitter响应结构：** 发布/创建返回`data.data.data`（3级嵌套），包含`id`、`text`、`edit_history_tweet_ids`。

#### Twitter — 带图片发布（FileUploadable流程）

**关键限制：** 网关的`/internal/execute`是Composio v2 `actions/{slug}/execute`的薄封装——它**不支持版本固定或FileUploadable合成**。Twitter媒体上传工具（`TWITTER_UPLOAD_MEDIA`、`TWITTER_UPLOAD_LARGE_MEDIA`）需要**两者都支持**，因此**必须**通过`composio_client` Python SDK直接调用，不能通过网关调用。

网关有意设计为通用——将所有工具流程（如本例）保留在此技能中。

**3步流程（已验证可行）：**

```python
import hashlib, httpx, json
from pathlib import Path
from composio_client import Composio

# COMPOSIO_API_KEY: 从 /data/workspace/composio-gateway/.env读取
# （网关拥有该密钥；技能脚本按相同方式读取）
client = Composio(api_key=COMPOSIO_API_KEY)

USER_ID = f"starchild-{user_id}"   # 注意：使用连字符，不是下划线
img = Path("output/images/foo.jpg")

# 1. 获取预签名S3上传URL
md5 = hashlib.md5(img.read_bytes()).hexdigest()
presigned = client.files.create_presigned_url(
    filename=img.name, md5=md5, mimetype="image/jpeg",
    tool_slug="TWITTER_UPLOAD_MEDIA", toolkit_slug="twitter",
)
# presigned.type == "new" → 文件是新的，必须PUT
# presigned.type == "existing" → 已缓存，跳过PUT
if presigned.type == "new":
    httpx.put(presigned.new_presigned_url, content=img.read_bytes(),
              headers={"Content-Type": "image/jpeg"}, timeout=60).raise_for_status()

# 2. 执行上传工具——必须传递版本="20260501_00"（或当前最新）
#    media是FileUploadable字典，不是base64
upload_resp = client.tools.execute(
    tool_slug="TWITTER_UPLOAD_MEDIA",
    user_id=USER_ID,
    version="20260501_00",
    arguments={
        "media": {"name": img.name, "mimetype": "image/jpeg", "s3key": presigned.key},
        "media_type": "image/jpeg",
        "media_category": "tweet_image",   # 或 "dm_image", "subtitles"
    },
)
result = upload_resp.model_dump()
assert result["successful"], result["error"]
# 响应嵌套：data.data.id（不是data.id，不是data.media_id_string）
media_id = result["data"]["data"]["id"]

# 3. 带media_media_ids创建推文——这个也可以通过网关调用
tweet_resp = client.tools.execute(
    tool_slug="TWITTER_CREATION_OF_A_POST",
    user_id=USER_ID,
    arguments={"text": "your tweet text", "media_media_ids": [str(media_id)]},
)
tweet_id = tweet_resp.model_dump()["data"]["data"]["id"]
url = f"https://x.com/i/web/status/{tweet_id}"
```

**为什么可行（调试笔记——不要丢失这些知识）：**
- `GET /api/v3/tools/TWITTER_UPLOAD_MEDIA`在没有版本的情况下返回404，因为它位于工具包版本`20260501_00+`，而不是默认的`00000000_00`。
- `client.tools.execute(version=...)`通过`/api/v3/tools/execute/{slug}`路由，它是版本感知的。
- 网关使用v2 `/api/v2/actions/{slug}/execute`进行execute——v2没有版本路由，所以它永远无法到达版本化工具。不要尝试“修复”网关以支持此功能——添加版本+FileUploadable会使它臃肿。保持它精简。
- `media`参数期望`{name, mimetype, s3key}`（FileUploadable模式），不是base64。传递base64会返回："Input should be a valid dictionary or instance of FileUploadable on parameter `media`"。
- `TWITTER_UPLOAD_MEDIA`的文件大小限制约为5 MB。对于较大的文件/视频/GIF，使用`TWITTER_UPLOAD_LARGE_MEDIA`（分块，流程相同，但额外的segment参数）。

**⚠️ Twitter限制与回退：**
- `TWITTER_RECENT_SEARCH`仅覆盖**最近7天**，旧的推文不会出现
- `TWITTER_FULL_ARCHIVE_SEARCH`需要Twitter API **专业版访问**，常规OAuth应用无法使用
- **获取用户推文历史时，优先使用平台原生工具`twitter_user_tweets`**，不限于7天

### 📅 Google Calendar

| 工具缩写 | 用途 | 关键参数 |
|-----------|---------|---------------|
| `GOOGLECALENDAR_EVENTS_LIST` | 列出事件 | `calendarId`（默认："primary"）、`timeMin`、`timeMax`（RFC3339+tz）、`singleEvents`（true）、`timeZone` |
| `GOOGLECALENDAR_CREATE_EVENT` | 创建事件 | `calendarId`、`summary`、`start`、`end`、`description`、`attendees` |
| `GOOGLECALENDAR_DELETE_EVENT` | 删除事件 | `calendarId`、`eventId` |

### 🐙 GitHub

| 工具缩写 | 用途 | 关键参数 |
|-----------|---------|---------------|
| `GITHUB_CREATE_AN_ISSUE` | 创建问题 | `owner`、`repo`、`title`、`body`、`labels`、`assignees` |
| `GITHUB_LIST_REPOSITORY_ISSUES` | 列出问题 | `owner`、`repo`、`sort`、`state`（open/closed/all）、`page`、`per_page` |
| `GITHUB_GET_AN_ISSUE` | 获取问题详情 | `owner`、`repo`、`issue_number` |
| `GITHUB_CREATE_A_PULL_REQUEST` | 创建PR | `owner`、`repo`、`title`、`head`、`base`、`body`、`draft` |
| `GITHUB_LIST_PULL_REQUESTS` | 列出PRs | `owner`、`repo`、`state`、`sort`、`head`、`base` |
| `GITHUB_MERGE_A_PULL_REQUEST` | 合并PR | `owner`、`repo`、`pull_number`、`commit_title`、`sha` |
| `GITHUB_GET_A_REPOSITORY` | 获取仓库信息 | `owner`、`repo` |
| `GITHUB_SEARCH_CODE` | 搜索代码 | `q`（GitHub搜索语法）、`sort`、`order`、`per_page` |
| `GITHUB_GET_REPOSITORY_CONTENT` | 获取文件内容 | `owner`、`repo`、`path`、`ref` |

```bash
# 创建问题
curl -s -X POST $GATEWAY/internal/execute \
  -H "Content-Type: application/json" \
  -d '{"tool": "GITHUB_CREATE_AN_ISSUE", "arguments": {"owner": "myorg", "repo": "myrepo", "title": "Bug: login fails", "body": "Steps to reproduce..."}}'

# 列出开放问题
curl -s -X POST $GATEWAY/internal/execute \
  -H "Content-Type: application/json" \
  -d '{"tool": "GITHUB_LIST_REPOSITORY_ISSUES", "arguments": {"owner": "myorg", "repo": "myrepo", "state": "open", "per_page": 10}}'
```

### 📝 Notion

| 工具缩写 | 用途 | 关键参数 |
|-----------|---------|---------------|
| `NOTION_CREATE_NOTION_PAGE` | 创建页面 | `parent_id`、`title`、`markdown`、`icon`、`cover` |
| `NOTION_SEARCH_NOTION_PAGE` | 搜索页面/数据库 | `query`、`filter_value`（页面/数据库）、`page_size` |
| `NOTION_QUERY_DATABASE_WITH_FILTER` | 带筛选查询数据库 | `database_id`、`filter`、`sorts`、`page_size` |
| `NOTION_INSERT_ROW_DATABASE` | 添加数据库行 | `database_id`、`properties` |
| `NOTION_UPDATE_ROW_DATABASE` | 更新数据库行 | `row_id`、`properties`、`icon`、`cover` |
| `NOTION_FETCH_DATABASE` | 获取数据库模式 | `database_id` |
| `NOTION_FETCH_BLOCK_CONTENTS` | 获取页面内容 | `block_id`（=页面id） |
| `NOTION_ADD_MULTIPLE_PAGE_CONTENT` | 添加块 | `parent_block_id`、`content_blocks`、`after` |
| `NOTION_UPDATE_PAGE` | 更新页面属性 | `page_id`、`properties`、`icon`、`cover`、`archived` |
| `NOTION_DELETE_BLOCK` | 删除/归档块 | `block_id` |

```bash
# 搜索页面
curl -s -X POST $GATEWAY/internal/execute \
  -H "Content-Type: application/json" \
  -d '{"tool": "NOTION_SEARCH_NOTION_PAGE", "arguments": {"query": "Meeting Notes", "page_size": 5}}'

# 带筛选查询数据库
curl -s -X POST $GATEWAY/internal/execute \
  -H "Content-Type: application/json" \
  -d '{"tool": "NOTION_QUERY_DATABASE_WITH_FILTER", "arguments": {"database_id": "abc123", "filter": {"property": "Status", "select": {"equals": "In Progress"}}, "page_size": 10}}'
```

### 📁 Google Drive

| 工具缩写 | 用途 | 关键参数 |
|-----------|---------|---------------|
| `GOOGLEDRIVE_CREATE_FILE_FROM_TEXT` | 创建文件 | `file_name`、`text_content`、`mime_type`、`parent_id` |
| `GOOGLEDRIVE_FIND_FILE` | 搜索文件 | `q`（Drive搜索语法）、`fields`、`spaces` |
| `GOOGLEDRIVE_DOWNLOAD_FILE` | 下载文件 | `fileId`、`mime_type` |
| `GOOGLEDRIVE_COPY_FILE` | 复制文件 | `fileId` |
| `GOOGLEDRIVE_ADD_FILE_SHARING_PREFERENCE` | 共享文件 | `fileId`、`role`、`type`、`emailAddress` |

```bash
# 按名称搜索文件
curl -s -X POST $GATEWAY/internal/execute \
  -H "Content-Type: application/json" \
  -d '{"tool": "GOOGLEDRIVE_FIND_FILE", "arguments": {"q": "name contains '\''report'\'' and mimeType != '\''application/vnd.google-apps.folder'\''"}}'

# 创建文本文件
curl -s -X POST $GATEWAY/internal/execute \
  -H "Content-Type: application/json" \
  -d '{"tool": "GOOGLEDRIVE_CREATE_FILE_FROM_TEXT", "arguments": {"file_name": "notes.txt", "text_content": "Hello World"}}'
```

**Google Drive搜索语法（`q`参数）：** `name contains 'keyword'`，`mimeType = 'application/vnd.google-apps.folder'`（文件夹），`'<folderId>' in parents`（文件夹中的文件），`modifiedTime > '2026-01-01'`。

### 📄 Google Docs

| 工具缩写 | 用途 | 关键参数 |
|-----------|---------|---------------|
| `GOOGLEDOCS_CREATE_DOCUMENT_MARKDOWN` | 从markdown创建文档 | `title`、`markdown_text` |
| `GOOGLEDOCS_GET_DOCUMENT_PLAINTEXT` | 获取文档为文本 | `document_id`、`include_tables`、`include_headers` |
| `GOOGLEDOCS_GET_DOCUMENT_BY_ID` | 获取原始文档对象 | `id` |

```bash
# 创建带markdown内容的文档
curl -s -X POST $GATEWAY/internal/execute \
  -H "Content-Type: application/json" \
  -d '{"tool": "GOOGLEDOCS_CREATE_DOCUMENT_MARKDOWN", "arguments": {"title": "Meeting Notes", "markdown_text": "# Q2 Planning\n\n- Item 1\n- Item 2"}}'

# 读取文档为纯文本
curl -s -X POST $GATEWAY/internal/execute \
  -H "Content-Type: application/json" \
  -d '{"tool": "GOOGLEDOCS_GET_DOCUMENT_PLAINTEXT", "arguments": {"document_id": "1abc...xyz"}}'
```

### 📊 Google Sheets

| 工具缩写 | 用途 | 关键参数 |
|-----------|---------|---------------|
| `GOOGLESHEETS_CREATE_GOOGLE_SHEET1` | 创建电子表格 | `title` |
| `GOOGLESHEETS_GET_SHEET_NAMES` | 列出电子表格中的工作表 | `spreadsheet_id`、`exclude_hidden` |
| `GOOGLESHEETS_BATCH_GET` | 读取单元格值 | `spreadsheet_id`、`ranges`（列表，A1表示法）、`majorDimension`、`valueRenderOption` |
| `GOOGLESHEETS_UPDATE_VALUES_BATCH` | 写入单元格值 | `spreadsheet_id`、`data`（{range, values}列表）、`valueInputOption` |
| `GOOGLESHEETS_SPREADSHEETS_VALUES_APPEND` | 追加行 | `spreadsheetId`、`range`、`values`、`valueInputOption`、`insertDataOption` |
| `GOOGLESHEETS_SPREADSHEETS_VALUES_BATCH_CLEAR` | 清除范围 | `spreadsheet_id`、`ranges` |
| `GOOGLESHEETS_GET_SPREADSHEET_INFO` | 获取完整电子表格元数据 | `spreadsheet_id` |
| `GOOGLESHEETS_UPDATE_SHEET_PROPERTIES` | 更新工作表属性 | `spreadsheet_id`、`sheet_id`、`title`、`index` |

```bash
# 读取单元格
curl -s -X POST $GATEWAY/internal/execute \
  -H "Content-Type: application/json" \
  -d '{"tool": "GOOGLESHEETS_BATCH_GET", "arguments": {"spreadsheet_id": "1abc...xyz", "ranges": ["Sheet1!A1:D10"]}}'

# 写入单元格
curl -s -X POST $GATEWAY/internal/execute \
  -H "Content-Type: application/json" \
  -d '{"tool": "GOOGLESHEETS_UPDATE_VALUES_BATCH", "arguments": {"spreadsheet_id": "1abc...xyz", "valueInputOption": "USER_ENTERED", "data": [{"range": "Sheet1!A1:B2", "values": [["Name", "Score"], ["Alice", 95]]}]}}'

# 追加行
curl -s -X POST $GATEWAY/internal/execute \
  -H "Content-Type: application/json" \
  -d '{"tool": "GOOGLESHEETS_SPREADSHEETS_VALUES_APPEND", "arguments": {"spreadsheetId": "1abc...xyz", "range": "Sheet1!A:B", "valueInputOption": "USER_ENTERED", "values": [["Bob", 88], ["Charlie", 92]]}}'
```

**⚠️ Google Sheets笔记：**
- `valueInputOption`：`"USER_ENTERED"`（解析公式/数字）或`"RAW"`（文本）
- `ranges`使用**A1表示法**：`"Sheet1!A1:D10"`，`"Sheet1!A:A"`（整列）
- `BATCH_GET`返回`data.data.valueRanges[].values`（2D数组）
- `spreadsheetId` vs `spreadsheet_id`：某些工具使用camelCase，某些使用snake_case——不确定时检查模式

## 重要笔记

- **工具缩写**：全大写：`GMAIL_SEND_EMAIL`
- **工具包缩写**：全小写：`gmail`、`github`
- **参数键**：始终使用`"arguments"`，不要`"params"`——`params`会被静默忽略
- **时间参数**：使用带时区偏移的RFC3339（`2026-04-08T00:00:00+08:00`），不是UTC（除非有意）
- **OAuth令牌由Composio管理**——到期时自动刷新
- **响应嵌套**：Composio execute响应通常是`data.data`，但Twitter是`data.data.data`（3级）。通过递归访问数据来解析。
- **原生工具回退**：当Composio工具有限制（例如Twitter搜索仅7天）时，优先使用平台内置原生工具（例如`twitter_user_tweets`）

## 常见问题

### Browserbase连接名称不匹配

如果`/internal/connections`显示工具包`browserbase_tool`为ACTIVE，但执行`BROWSER_TOOL_*`返回"没有为工具包 'browser' 找到活动的连接"，这是网关侧工具包别名不匹配（`browserbase_tool` vs `browser`）。

**怎么办：**
1. 对于会话管理工具（`SESSIONS_*`、`CONTEXTS_*`、`UPLOADS_*`等），网关应在服务器端规范化Browserbase别名。如果它不这样做，尝试`BROWSER_TOOL_*`和`BROWSERBASE_TOOL_*`缩写。
2. 对于**实际浏览器控制**（导航、点击、填充、抓取），**不要使用Composio execute**——使用Playwright `connect_over_cdp`，如上Browserbase部分所述。Composio工具仅管理会话，不管理页面交互。

### Gmail嵌套JSON解析

Gmail返回复杂的JSON结构，包含多层HTML内容。**不要**尝试用`json.loads`解析嵌套字符串。直接以Python字典形式访问——网关已返回解析后的JSON。

---
