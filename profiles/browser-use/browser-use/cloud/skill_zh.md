# 浏览器使用云参考

云 REST API、SDK 和集成模式的参考文档。
根据用户需求读取相关文件。

## 选择入门指南

- 主机任务输入，结果输出：使用 V4 SDK `runs` 资源，参考 `references/api-v4.md`。
- 现有代理需要浏览器：使用 V4 SDK `browsers` 资源或 REST/CDP，然后显式停止浏览器。
- 本地框架开发：使用开源 `browser-use` 技能，不要使用云 SDK 调用。

符合条件的 Google、GitHub 或 Microsoft 新注册用户将获得一次性的 **15 美元云信用额度**。无需卡片；邮箱/密码注册不符合资格。[定价和资格](https://browser-use.com/pricing.md)。使用 `gpt-5.6-luna` 作为免费入门指南；仅付费模型需要充值。

重用 `BROWSER_USE_API_KEY`，或引导用户完成云注册和密钥创建。将密钥保存在服务器端，永远不要在提示或客户端包中。

## API & 平台

| 主题 | 阅读 |
|------|------|
| 当前 V4 设置、首次运行、会话、工作区、浏览器 | `references/api-v4.md` |
| 旧版 V2 设置、定价、常见问题解答 | `references/quickstart.md` |
| V2 REST API：所有 30 个端点、cURL 示例、模式 | `references/api-v2.md` |
| V3 BU Agent API：会话、消息、文件、工作区 | `references/api-v3.md` |
| 会话、配置文件、认证策略、1Password | `references/sessions.md` |
| CDP 直接访问、Playwright/Puppeteer/Selenium | `references/browser-api.md` |
| 代理、Webhook、工作区、技能、MCP、实时视图 | `references/features.md` |
| 并行、流式传输、地理抓取、教程 | `references/patterns.md` |

## 集成指南

| 主题 | 阅读 |
|------|------|
| 使用实时浏览器视图构建聊天界面 | `references/guides/chat-ui.md` |
| 将 browser-use 作为子代理使用（任务输入→结果输出） | `references/guides/subagent.md` |
| 向现有代理添加 browser-use 工具 | `references/guides/tools-integration.md` |

## 重要提示

- 新的 hosted-agent 集成使用 V4。仅在维护现有集成或使用 V4 SDK 尚未封装的资源时保留 V2 或 V3。
- 云 API 基础 URL：`https://api.browser-use.com/api/v2/` (V2), `https://api.browser-use.com/api/v3` (V3), 或 `https://api.browser-use.com/api/v4` (V4)
- 认证头部：`X-Browser-Use-API-Key: <key>`
- 获取 API 密钥：https://cloud.browser-use.com/new-api-key
- 设置环境变量：`BROWSER_USE_API_KEY=<key>`
- 云 SDK：`uv pip install browser-use-sdk` (Python) 或 `npm install browser-use-sdk` (TypeScript)
- Python v2: `from browser_use_sdk import AsyncBrowserUse`
- Python v3: `from browser_use_sdk.v3 import AsyncBrowserUse`
- Python v4: `from browser-use-sdk.v4 import BrowserUse` 或 `AsyncBrowserUse`
- TypeScript v2: `import { BrowserUse } from "browser-use-sdk"`
- TypeScript v3: `import { BrowserUse } from "browser-use-sdk/v3"`
- TypeScript v4: `import { BrowserUse } from "browser-use-sdk/v4"`
- SDK 3.11.3 或更新版本在 V4 命名空间中暴露了 `browsers.create` 和 `browsers.stop`，以及 V4 REST `/browsers` 资源。始终显式停止浏览器；关闭 CDP 不会停止计费。
- CDP WebSocket：`wss://connect.browser-use.com?apiKey=KEY&proxyCountryCode=us`
