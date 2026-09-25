# Cookie 同步 — 本地 Chrome → Browserbase 上下文

将本地 Chrome 的 cookie 导出并保存到 Browserbase 的 **持久上下文** 中。同步后，使用 `browse` 命令行工具以该上下文打开经过身份验证的会话。

支持 **域名过滤**（仅同步您需要的 cookie）和 **上下文复用**（刷新 cookie 而无需创建新上下文）。

## 前置条件

- 带有远程调试功能的 Chrome（或 Chromium、Brave、Edge）
- 如果您的浏览器构建版本暴露了 `chrome://flags/#allow-remote-debugging`，请启用它并重启浏览器
- 否则，使用 `--remote-debugging-port=9222 --user-data-dir=/tmp/chrome-debug` 启动，并设置 `CDP_URL=ws://127.0.0.1:9222`
- Chrome 中至少打开一个标签页
- Node.js 22+
- 环境变量：`BROWSERBASE_API_KEY`

## 安装

首次使用前安装依赖项：

```bash
cd .claude/skills/cookie-sync && npm install
```

## 使用

### 基本用法 — 同步所有 cookie

```bash
node .claude/skills/cookie-sync/scripts/cookie-sync.mjs
```

创建包含所有 Chrome cookie 的持久上下文。输出上下文 ID。

### 按域名过滤 — 仅同步特定网站

```bash
node .claude/skills/cookie-sync/scripts/cookie-sync.mjs --domains google.com,github.com
```

匹配域名及其所有子域名（例如 `google.com` 匹配 `accounts.google.com`、`mail.google.com` 等）

### 在现有上下文中刷新 cookie

```bash
node .claude/skills/cookie-sync/scripts/cookie-sync.mjs --context ctx_abc123
```

将新鲜的 cookie 重新注入先前创建的上下文中。当 cookie 过期时使用此选项。

### 验证浏览器模式

```bash
node .claude/skills/cookie-sync/scripts/cookie-sync.mjs --verified
```

启用 Browserbase 身份验证的验证浏览器，以提高对受保护网站访问的权限。推荐用于像 Google 这样会指纹识别浏览器的网站。

### 居住地代理带地理位置

```bash
node .claude/skills/cookie-sync/scripts/cookie-sync.mjs --proxy "San Francisco,CA,US"
```

通过指定位置的居住地代理路由。格式：`"City,ST,Country"`（州为两位字母代码）。有助于匹配您本地 IP 的地理位置，以便身份验证 cookie 不会被拒绝。

### 组合标志

```bash
node .claude/skills/cookie-sync/scripts/cookie-sync.mjs --domains github.com,google.com --verified --proxy "San Francisco,CA,US"
```

## 浏览经过身份验证的网站

同步后，使用 `browse` 命令行工具和上下文 ID：

```bash
SESSION_JSON="$(browse cloud sessions create --context-id <ctx-id> --persist --keep-alive)"
SESSION_ID="$(echo "$SESSION_JSON" | jq -r .id)"
CONNECT_URL="$(echo "$SESSION_JSON" | jq -r .connectUrl)"

browse open https://mail.google.com --cdp "$CONNECT_URL"
```

在 `browse cloud sessions create` 上使用 `--persist` 标志将任何新的 cookie 或状态更改保存回上下文，当云会话释放时，保持会话新鲜以供下次使用。

**完整工作流示例：**

```bash
# 第 1 步：同步 Twitter 的 cookie
node .claude/skills/cookie-sync/scripts/cookie-sync.mjs --domains x.com,twitter.com
# 输出：上下文 ID: ctx_abc123

# 第 2 步：浏览经过身份验证的 Twitter
SESSION_JSON="$(browse cloud sessions create --context-id ctx_abc123 --persist --keep-alive)"
SESSION_ID="$(echo "$SESSION_JSON" | jq -r .id)"
CONNECT_URL="$(echo "$SESSION_JSON" | jq -r .connectUrl)"

browse open https://x.com/messages --cdp "$CONNECT_URL"
browse snapshot
browse screenshot
browse stop
browse cloud sessions update "$SESSION_ID" --status REQUEST_RELEASE
```

## 复用上下文进行计划任务

上下文跨会话持久化，非常适合计划/定期任务：

1. **一次性（笔记本电脑打开）：** 运行 cookie-sync → 获取上下文 ID
2. **计划任务：** 使用 `browse cloud sessions create --context-id <ctx-id> --persist --keep-alive` 创建 Browserbase 会话，然后使用 `browse open <url> --cdp <connectUrl>` 附着 — 无需本地 Chrome
3. **按需重新同步：** 当 cookie 过期时，再次运行 cookie-sync 使用 `--context <ctx-id>` 刷新

## 故障排除

- **"No DevToolsActivePort found"** → 如果您的浏览器构建版本暴露了 `chrome://flags/#allow-remote-debugging`，请启用它，或使用 `--remote-debugging-port=9222` 启动并设置 `CDP_URL=ws://127.0.0.1:9222`
- **"No open page targets found"** → 在 Chrome 中至少打开一个标签页
- **"WebSocket error"** → Chrome 可能卡死；强制退出并重新打开它
- **上下文中的 cookie 过期** → 使用 `--context <id>` 重新运行 cookie-sync 以刷新
- **网站拒绝身份验证** → 尝试添加 `--verified` 和/或 `--proxy` 使用您附近的地理位置
