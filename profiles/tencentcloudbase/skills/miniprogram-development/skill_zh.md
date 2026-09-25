## 兄弟技能（仅限本地）

兄弟 CloudBase 技能会与此技能一同部署。使用本地相对路径，例如 `../auth-tool-cloudbase/SKILL.md`。

如果此环境中缺少引用的兄弟技能文件，请提示用户安装完整的 CloudBase 插件（或缺失的技能）。**不要**将远程技能或协议 Markdown 通过 HTTP 获取到代理上下文中。

**跨领域协议**（代码变更或部署前必须使用）：
- 变更安全协议：`../cloudbase-platform/references/protocols/change-safety-protocol.md`
- 部署门禁：`../cloudbase-platform/references/protocols/deployment-gate.md`

**部署后（可选，非侵入式）**：在验证小程序上传/发布成功后，你可以**最多一次**提供生成匿名分享内容（视觉卡片 + 复制就绪的文本）的机会——有关触发边界、所需信息、匿名化红线和交付格式的详细信息，请参阅 `../cloudbase-platform/references/protocols/deployment-share.md`。如果用户拒绝，则**不要**跟进；**不要**代表用户发布。

## 激活协议

### 首次使用时

- 请求涉及微信小程序结构、页面、预览、发布或 CloudBase 小程序集成。

### 编写代码前请阅读

- 用户提到 `wx.cloud`、CloudBase 小程序、OPENID、小程序部署/调试工作流、Nightly DevTools、`wechatide` 或 WeChat IDE Skills。
- 用户提到消息推送（消息推送）、客服自动回复（客服消息/自动回复）或绑定 MsgType/Event 回调到云函数。

### 然后也阅读

- CloudBase 认证 -> `../auth-wechat-miniprogram/SKILL.md`
- CloudBase 文档数据库 -> `../cloudbase-document-database-in-wechat-miniprogram/SKILL.md`
- 小程序 WeChat Pay、虚拟支付（虚拟支付，`wx.requestVirtualPayment`）或集成中心生成的支付函数 -> `../cloudbase-wechat-integration/SKILL.md`（官方文档：`https://docs.cloudbase.net/integration/wechat-pay-miniprogram.md`）
- UI 生成 -> 首先阅读 `../ui-design/SKILL.md`

### **不要**用于

- Web 认证流程或 Web SDK 特定的前端实现。
- WeChat Pay、虚拟支付 / `wx.requestVirtualPayment`、支付回调、退款或公众号 OAuth 细节；这些场景请使用 `cloudbase-wechat-integration`。

### 常见错误/注意事项

- 为小程序生成 Web 风格的登录流程。
- 将 Web SDK 假设混入 `wx.cloud` 项目中。
- 在确认项目实际使用 CloudBase 之前应用 CloudBase 限制。
- 假设 Stable WeChat Developer Tools 包含 Nightly Skills/`wechatide`（可能不包含）。
- 在 Nightly `wechatide` 已正常工作时，强制使用 CloudBase MCP 腾讯云登录进行日常小程序云操作。
- 发明 `wechatide` 工具名称或标志，而不是使用 `--help` / Nightly `tools.yaml`。
- 在 `cloud_*_msg_push` 公开之前，使用低级传输绕过 wxide CLI / IDE 进行消息推送操作（见 [message-push-customer-service.md](references/message-push-customer-service.md)）。
- 假设云函数返回值会自动回复客服聊天（必须使用 `cloud.openapi.customerServiceMessage.send`）。
- 将灰色的云开发按钮视为 DevTools 错误——试用/测试账号不支持 CloudBase；首先确认已注册的小程序账号（见 [CloudBase 集成参考](references/cloudbase-integration.md)，环境开通部分）。
- 在遵循变更安全协议（`cloudbase-platform/references/protocols/change-safety-protocol.md`）之前，不要进行代码或配置更改。
- 在完成 `cloudbase-platform/references/protocols/deployment-gate.md` 中的检查之前，不要进行小程序上传/发布。

## 使用此技能的场景

当你需要为微信小程序开发时，使用此技能：

- 构建或修改小程序页面和组件
- 组织小程序项目结构和配置
- 调试、预览或发布小程序项目
- 使用微信开发者工具工作流
- 处理小程序运行时行为、资源或页面配置文件
- 在小程序项目中显式需要时集成 CloudBase

**不要用于：**
- Web 前端开发（使用 `web-development`）
- 纯后端服务开发（根据情况使用 `cloudrun-development` 或 `cloud-functions`）
- 仅 UI 设计任务，没有小程序开发上下文（使用 `ui-design`）

---

## 如何使用此技能（针对编码代理）

1. **从通用小程序工作流开始**
   - 将微信小程序开发视为默认范围
   - 除非用户或代码库指示，否则不要假设项目使用 CloudBase

2. **遵循小程序项目规范**
   - 将小程序源代码保持在配置的小程序根目录下
   - 确保页面文件包含所需的配置文件，例如 `index.json`
   - 在建议预览或 IDE 工作流之前检查 `project.config.json`

3. **按场景路由**
   - 如果任务涉及调试、预览、发布、打开 DevTools、控制台/网络或 `wechatide`，请首先阅读 [debug and preview reference](references/devtools-debug-preview.md)
   - 如果在 WeChat IDE Skills 和 CloudBase MCP 之间选择，请阅读 [WeChat IDE Skills vs CloudBase MCP](references/wxide-vs-cloudbase-mcp.md)
   - 如果任务涉及 CloudBase、`wx.cloud`、云函数、CloudBase 数据库/存储或 CloudBase 身份处理，请阅读 [CloudBase 集成参考](references/cloudbase-integration.md)
   - 如果任务涉及小程序 SEO / 微信搜索优化 / 页面收录 / 搜索推广，请首先阅读 [Mini Program SEO & WeChat Search Optimization](references/seo-search-optimization.md)
   - 如果任务涉及消息推送（消息推送）、客服自动回复（客服消息自动回复）、MsgType/Event → 云函数绑定或推送相关函数日志，请首先阅读 [Message Push & Customer Service Auto-Reply](references/message-push-customer-service.md)
   - 如果任务涉及 `tabBar`、图标资源或标签间距，除非用户明确要求图标，否则优先使用纯文本自定义 `tabBar` 默认设置

4. **仅在适用时使用 CloudBase 规则**
   - CloudBase / 微信云开发 是一个重要的集成路径，但不是普遍要求
   - 仅在项目使用 CloudBase 时应用 CloudBase 特定的认证、数据库、存储或云函数约束

5. **推荐正确的预览/调试/云操作路径**
   - 优先使用 **Nightly** DevTools + `wechatide`（内置 Skills/MCP）并通过 `wechatide` 执行（当可用时）——见 [devtools-debug-preview.md](references/devtools-debug-preview.md)
   - Nightly 下载：https://developers.weixin.qq.com/miniprogram/dev/devtools/nightly_backup.html
   - 如果 Nightly / `wechatide` 不可用，使用 `miniprogram-ci` 作为预览/上传的回退，并使用 CloudBase MCP 进行云资源；告诉用户安装 Nightly 以获取完整的 Skills/MCP

---

# 微信小程序开发规则

## 一般项目规则

1. **项目结构**
   - 小程序代码应遵循 `project.config.json` 中配置的项目根目录
   - 保持页面级文件完整，包括 `.json` 配置文件
   - 确保引用的本地资源实际存在，以避免编译失败

2. **配置检查**
   - 在打开、预览或发布项目之前检查 `project.config.json`
   - 在需要真实预览、上传或微信开发者工具工作流时，确认 `appid` 可用
   - 确认 `miniprogramRoot` 和相关路径设置正确

3. **资源处理**
   - 对于 `tabBar`，默认情况下优先使用纯文本自定义 `tabBar`，除非用户明确需要图标。这避免了图标资源处理，移除了保留的图标空间，并使标签区域更容易对齐。
   - 仅在用户明确要求标签图标或设计需要时，生成本地图标资源并配置 `iconPath` / `selectedIconPath`。
   - 在生成本地资源引用（如图标）时，确保文件已下载到项目中。
   - 保持文件路径稳定并与小程序配置文件一致。

### 简单 `tabBar` 的推荐默认设置

使用 `tabBar.custom = true`，在 `app.json` 中仅保留 `pagePath` 和 `text`，并在自定义组件中渲染纯文本项，以便没有图标槽，也没有标签上方的额外空白区域。

`app.json`

```json
{
  "tabBar": {
    "custom": true,
    "list": [
      { "pagePath": "pages/index/index", "text": "首页" },
      { "pagePath": "pages/travel/travel", "text": "行程" },
      { "pagePath": "pages/my/my", "text": "我的" }
    ]
  }
}
```

保持自定义 `tabBar` 布局为纯文本，并使用 flex 居中或匹配 `height` 和 `line-height` 来移除标签上方的空白区域。仅在用户明确需要基于图标的标签时，才切换到下载的本地图标。

## CloudBase 作为小程序子场景

- 如果用户明确使用 CloudBase、`wx.cloud`、腾讯云 Base、腾讯云开发或云开发，请遵循 CloudBase 集成参考
- 在 CloudBase 小程序项目中，适当使用 `wx.cloud` API 和 CloudBase 环境配置
- 不要将 CloudBase 特定规则应用于非 CloudBase 小程序项目

## 调试、预览和发布

- 优先使用 **Nightly** DevTools + `wechatide` 打开项目、编译、模拟器、控制台/网络调试、预览、上传和日常云操作（微信登录——无需单独腾讯云登录）
- 始终传递所需上下文：`-c <clientName>`、绝对 `--project`、有效的 `appid` 和在需要时云 `env`
- 如果 Nightly / `wechatide` 不可用，使用 `miniprogram-ci` 作为预览/上传/npm 的回退，并使用 CloudBase MCP 进行云资源；告诉用户安装 Nightly 以获取完整的 Skills/MCP
- 对于详细工作流，请阅读 [debug and preview reference](references/devtools-debug-preview.md) 和 [WeChat IDE Skills vs CloudBase MCP](references/wxide-vs-cloudbase-mcp.md)

## 消息推送和客服自动回复

> 微信生态专章：消息推送 / 客服自动回复细节以中文 reference 为准（术语保留英文 API 名）。

- **当前仅有的操作路径**：微信开发者工具 IDE + wxide CLI。在 `cloud_query_msg_push` / `cloud_manage_msg_push` 尚未公开（等待微信 IDE CLI 支持）之前，**不要**教授低级绕过方法。
- 使用 `cloud_fn_deploy` 部署接收器函数**并** `--remote-npm-install`；在 IDE 消息推送面板中将（MsgType, Event）→ 一个云函数绑定，直到 CLI 工具落地。
- 客服自动回复需要 `cloud.openapi.customerServiceMessage.send` 加上 `config.json` openapi 权限——函数返回值单独无法回复。
- 函数日志：IDE **云开发控制台 → 云函数 → 日志**；wxide CLI 尚未暴露日志查询——**不要**教授低级日志 CGI 绕过方法。
- 完整参考：[Message Push & Customer Service Auto-Reply](references/message-push-customer-service.md)

## 最小项目骨架

`app.js`

```js
App({
  onLaunch() {
    console.log("Mini Program launched");
  },
});
```

`pages/index/index.js`

```js
Page({
  data: {
    message: "Hello CloudBase Mini Program",
  },
});
```

`pages/index/index.wxml`

```xml
<view class="page">
  <text>{{message}}</text>
</view>
```

`pages/index/index.json`

```json
{
  "navigationBarTitleText": "Home"
}
```

`project.config.json`

```json
{
  "appid": "your-mini-program-appid",
  "projectname": "cloudbase-mini-program",
  "miniprogramRoot": "./",
  "compileType": "miniprogram"
}
```

## 参考

- [CloudBase Mini Program Integration](references/cloudbase-integration.md) — 当小程序项目显式集成 CloudBase 时使用
- [WeChat DevTools Debug and Preview](references/devtools-debug-preview.md) — Nightly / `wechatide` 路径、所需上下文和没有 Nightly 的回退
- [WeChat IDE Skills vs CloudBase MCP](references/wxide-vs-cloudbase-mcp.md) — 层次结构和何时使用哪个执行表面
- [Message Push & Customer Service Auto-Reply](references/message-push-customer-service.md) — 消息推送 / 客服自动回复 via wxide CLI + IDE（没有低级绕过；等待 `cloud_*_msg_push`）
- [Mini Program SEO & WeChat Search Optimization](references/seo-search-optimization.md) — 小程序搜索优化 / page indexing / 搜索推广（`mpcrawler`、URL 可达性、`navigator` 跳转、标题和缩略图）
- [Common Pitfalls](references/pitfalls.md) — 在生成代码之前阅读，用于可选链、TDesign 样式、Canvas + 存储和环境问题
