# Composio — 通过网关进行外部应用集成

Composio 允许用户将 1000 多个外部应用（Gmail、Slack、GitHub、Google Calendar、Notion 等）连接到他们的 Starchild 代理。所有操作都通过 **Composio 网关** (`composio-gateway.fly.dev`) 进行，该网关负责身份验证和 API 密钥管理。

## 架构

```
Agent (Fly 6PN 网络)
    ↓  HTTP (通过 IPv6 自动身份验证)
Composio 网关 (composio-gateway.fly.dev)
    ↓  Composio SDK
Composio 云 → 目标 API (Gmail、Slack、等)
```

- **您永远不会接触到 COMPOSIO_API_KEY** — 网关持有它
- **您永远不会直接调用 Composio SDK** — 使用网关 HTTP API
- **身份验证是自动的** — 您的 Fly 6PN IPv6 通过计费数据库解析为 user_id
- **不需要环境变量** — 网关可以从任何代理容器中访问

## 网关基本 URL

```
GATEWAY = "http://composio-gateway.flycast"
```

所有请求都使用 **通过 Fly 内部网络传输的普通 HTTP** (flycast)。不需要 JWT。

**关键 — 永远不要将网关通过 sc-proxy 路由：**
- 使用 **curl**（如以下示例所示）或普通的 `requests` / `http.client` 并**不使用代理**。
- **不要**使用 `proxied_get` / `proxied_post` 用于此主机（即使 PROTOCOL 说“始终通过代理”用于外部 API — flycast 是文档中的例外；`core.http_client` 也自动绕过 `*.flycast`）。
- **不要**设置 `HTTP_PROXY` / `HTTPS_PROXY` 或 `curl -x` 指向网关。
- 代理会重写调用者身份，因此网关会看到错误的用户，连接/执行失败或命中另一个锁定器。

## API 参考

### 1. 搜索工具（紧凑）

为任务找到正确的工具 slug。返回 **紧凑** 的工具信息 — 仅 slug、描述和参数名称。足以选择正确的工具。

```bash
curl -s -X POST $GATEWAY/internal/search \
  -H "Content-Type: application/json" \
  -d '{"query": "通过 gmail 发送邮件"}'
```

**响应（紧凑）：**
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

### 2. 获取工具模式（完整）

获取特定工具的 **完整** 参数定义 — 类型、描述、枚举、默认值。在搜索后**需要**精确参数格式时使用此功能。

```bash
curl -s -X POST $GATEWAY/internal/tool_schema \
  -H "Content-Type: application/json" \
  -d '{"tool": "GOOGLECALENDAR_EVENTS_LIST"}'
```

**响应:**
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

执行 Composio 工具。**关键字是 `arguments`，而不是 `params`。**

```bash
curl -s -X POST $GATEWAY/internal/execute \
  -H "Content-Type: application/json" \
  -d '{"tool": "GMAIL_SEND_EMAIL", "arguments": {"to": "x@example.com", "subject": "Hi", "body": "Hello!"}}'
```

**成功时：**
```json
{"data": {"messages": [...]}, "error": null}
```

**失败时** — 包括工具模式，以便您可以自我纠正：
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
- `oauth_completed_active`：布尔值，仅在 OAuth 完成为 `ACTIVE` 时为 true

缓存失效仅在观察到 `ACTIVE` 后触发，并且针对用户的实例（`fly-force-instance-id=<用户容器_id 从 user_mapping>`），而不是 composio-gateway 自己的实例。

### 5. 启动新连接

```bash
curl -s -X POST $GATEWAY/api/connect \
  -H "Content-Type: application/json" \
  -d '{"toolkit": "gmail"}'
```

返回 `connect_url`，用户需要完成 OAuth。

### 无摩擦连接（执行操作时必须）

仅在用户想要在**外部应用**中执行操作（发送/读取邮件、创建日历事件、打开 GitHub 问题、发布等）并且该应用**尚未连接**时触发。

**不要**用于纯问答/解释（“什么是 Gmail？”、“日历如何工作？”）。

1. **不要**描述连接检查、空列表、OAuth 机制，或询问“想要我连接吗？”。
2. 在**Web**上（活动 SSE 会话）：调用针对**一个主要**工具包的内置工具：
   ```
   frontend_action(action_type="composio_connect", toolkit="gmail")
   ```
   可选：`display_name="Gmail"`, `title=...`, `description=...`。
   使用正确的**小写**工具包 slug。**不要**粘贴 `connect_url` Markdown 链接 — 前端会从 action_request 渲染一个连接卡片。

3. 可见回复：**一句话**说明您在用户连接后将执行什么（不要表情符号边框，不要授权 URL）。

4. **停止并等待**用户完成 OAuth / 完成，然后继续原始任务。

5. **永远不要**将用户引导到连接页面首先。

6. **后备**（没有 SSE / 非网页频道，或 `frontend_action` 失败）：
   ```bash
   curl -s -X POST $GATEWAY/api/connect \
     -H "Content-Type: application/json" \
     -d '{"toolkit": "gmail"}'
   ```
   然后以纯文本形式提供 `connect_url`（仍然不需要 Markdown 卡片软匹配）。
   如果这也失败了，请用一句话说明并停止 — 不要编造替代设置流程。

### 6. 断开连接

```bash
curl -s -X DELETE $GATEWAY/api/connections/{connection_id}
```

### Instagram 发布（重要的 slug 映射）

Composio 搜索可能会返回此环境中不可执行的旧版 Instagram slugs。发布到 Instagram 时，请使用这些**工作 slug**：

1) 创建草稿容器：
- `INSTAGRAM_CREATE_MEDIA_CONTAINER`
- 必需：`ig_user_id`
- 典型照片参数：`{"ig_user_id":"...","image_url":"https://...","content_type":"photo","caption":"..."}`

2) 发布草稿：
- `INSTAGRAM_CREATE_POST`
- 必需：`ig_user_id`, `creation_id`

两步流程：
- 执行 `INSTAGRAM_CREATE_MEDIA_CONTAINER` → 读取 `data.data.id` 作为 `creation_id`
- 使用该 `creation_id` 执行 `INSTAGRAM_CREATE_POST`

提示：如果 `/internal/search` 建议使用 `INSTAGRAM_POST_IG_USER_MEDIA` 或 `INSTAGRAM_POST_IG_USER_MEDIA_PUBLISH`，但执行返回“找不到工具 ...”，请切换到上述两个 slug。

### Browserbase — 混合工作流（会话管理 + Playwright CDP）

**Composio 的 Browserbase 工具仅管理会话生命周期（打开/关闭/列出）。它们**不**控制网页。**

要实际操作浏览器（导航、点击、填写表单、抓取数据），请使用 **Playwright `connect_over_cdp`** 连接到会话的 WebSocket URL。

#### 第 1 步：通过 Composio 创建 Browserbase 会话

```bash
curl -s -X POST $GATEWAY/internal/execute \
  -H "Content-Type: application/json" \
  -d '{"tool": "BROWSERBASE_TOOL_SESSIONS_CREATE", "arguments": {"projectId": "YOUR_PROJECT_ID"}}'
```

响应包括 `id`（session_id）、`status` 和时间戳。

#### 第 2 步：构建 CDP WebSocket URL

```python
import os
session_id = "<session_id from step 1>"
api_key = os.environ.get("BROWSERBASE_API_KEY")  # 存储在 workspace/.env 中
cdp_url = f"wss://connect.browserbase.com?apiKey={api_key}&sessionId={session_id}"
```

#### 第 3 步：使用 Playwright 控制浏览器

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

#### 第 4 步：删除会话（重要 — 停止计费）

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
| **内存成本** | ~30-50MB 本地（Playwright 客户端仅限）；Chromium 在 Browserbase 服务器上运行 |
| **反检测** | Browserbase 在服务器端处理 — 指纹掩码、验证码解决、Cloudflare 绕过。Playwright 客户端不做特殊处理。 |
| **计费** | 按分钟计费（四舍五入）。完成时始终删除会话。 |

#### 完整示例脚本（创建 → 控制 → 清理）

```python
#!/usr/bin/env python3
"""Browserbase: 创建会话 → 使用 Playwright 控制 → 清理。"""
import asyncio, os, json, requests
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

#### 可用的 Browserbase 工具通过 Composio

| 工具 slug | 目的 | 关键参数 |
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
| `BROWSERBASE_TOOL_CONTEXTS_UPDATE` | 更新上下文标签 | `id`, `labels` |
| `BROWSERBASE_TOOL_UPLOADS_CREATE` | 将文件上传到会话 | `projectId`, 文件数据 |
| `BROWSERBASE_TOOL_UPLOADS_GET` | 获取上传信息 | `id` |
| `BROWSERBASE_TOOL_UPLOADS_LIST` | 列出上传 | (无) |
| `BROWSERBASE_TOOL_UPLOADS_DELETE` | 删除上传 | `id` |
| `BROWSERBASE_TOOL_DOWNLOADS_LIST` | 列出下载 | `sessionId` |
| `BROWSERBASE_TOOL_DOWNLOADS_GET` | 获取下载 | `downloadId` |
| `BROWSERBASE_TOOL_DOWNLOADS_GET_STREAM` | 流式传输下载 | `downloadId` |
| `BROWSERBASE_TOOL_KB_GET_KNOWLEDGE` | 获取 KB 文章 | `id` |

### Browserbase / 浏览器工具故障排除

如果 Browserbase 已连接但执行失败，请检查连接工具包与工具 slug 之间的命名不匹配：

- 连接可能显示为 toolkit `browserbase_tool` 为 ACTIVE，但执行 `BROWSER_TOOL_*` 返回“找不到活动连接 toolkit 'browser'”。

**要做什么:**
1. 对于会话管理工具 (`SESSIONS_*`, `CONTEXTS_*`, `UPLOADS_*`, 等)，网关应在服务器端规范化 Browserbase 别名。如果它不这样做，请尝试 `BROWSER_TOOL_*` 和 `BROWSERBASE_TOOL_*` slugs。
2. 对于**实际浏览器控制**（导航、点击、填写、抓取），**不要**使用 Composio 执行 — 使用 Playwright `connect_over_cdp`，如 Browserbase 部分上述所述。Composio 工具仅管理会话，不控制页面交互。

### Gmail 嵌套 JSON 解析

Gmail 返回复杂的 JSON 结构，包含多个级别的 HTML 内容。**不要**尝试解析嵌套字符串使用 `json.loads`。直接作为 Python 中的字典访问 — 网关已经返回了解析的 JSON。

---
