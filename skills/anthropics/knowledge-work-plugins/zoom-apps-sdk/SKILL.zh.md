---
name: zoom-apps-sdk
description: Zoom 应用来宾 SDK 的参考技能。在构建可在 Zoom 会议、网络研讨会、主客户端或 Zoom Phone 中运行的 Web 应用时，在路由到客户端应用工作流后使用。
---

# Zoom 应用程序 SDK

运行在 Zoom 客户端内部的 Web 应用的背景参考。优先选择 `choose-zoom-approach`，然后从这里路由到 Layers API、Collaborate Mode、客户端 OAuth 和运行时约束。

# Zoom 应用程序 SDK

构建运行在 Zoom 客户端内的 Web 应用 - 会议、网络研讨会、主客户端和 Zoom Phone。

**官方文档**: https://developers.zoom.us/docs/zoom-apps/
**SDK 参考**: https://appssdk.zoom.us/
**NPM 包**: https://www.npmjs.com/package/@zoom/appssdk

## 快速链接

**新接触 Zoom 应用程序？请遵循此路径：**

1. **[架构](concepts/architecture.md)** - 前端/后端模式、嵌入式浏览器、深度链接
2. **[快速入门](examples/quick-start.md)** - 完整的 Express + SDK 应用程序
3. **[运行上下文](concepts/running-contexts.md)** - 应用程序运行的位置（inMeeting、inMainClient 等）
4. **[Zoom 应用程序与会议 SDK](concepts/meeting-sdk-vs-zoom-apps.md)** - 停止混合应用程序类型
5. **[客户端 OAuth](examples/in-client-oauth.md)** - 使用 PKCE 的无缝授权
6. **[API 参考](references/apis.md)** - 100 多个 SDK 方法
7. **集成索引** - 查看此文件下方的部分
8. **[5 分钟运行手册](RUNBOOK.md)** - 深度调试前的预检

**参考：**
- **[API 参考](references/apis.md)** - 按类别列出所有 SDK 方法
- **[事件参考](references/events.md)** - 所有 SDK 事件监听器
- **[Layers API](references/layers-api.md)** - 沉浸式和相机模式渲染
- **[OAuth 参考](references/oauth.md)** - Zoom 应用的 OAuth 流
- **[Zoom Mail](references/zmail-sdk.md)** - 邮件插件集成

**遇到问题？**
- 应用程序无法在 Zoom 中加载 → 检查下方的 [域名白名单](#url-whitelisting-required)
- SDK 错误 → [常见问题](troubleshooting/common-issues.md)
- 本地开发设置 → [调试指南](troubleshooting/debugging.md)
- 版本升级 → [迁移指南](troubleshooting/migration.md)
- 论坛派生的常见问题 → [论坛常见问题](troubleshooting/forum-top-questions.md)

**正在构建沉浸式体验？**
- [Layers 沉浸模式](examples/layers-immersive.md) - 自定义视频布局
- [相机模式](examples/layers-camera.md) - 虚拟相机叠加

> **需要 OAuth 帮助？** 查看 **[zoom-oauth](../oauth/SKILL.md)** 技能以获取身份验证流。

## SDK 概述

Zoom 应用程序 SDK (`@zoom/appssdk`) 为运行在 Zoom 嵌入式浏览器中的 Web 应用程序提供 JavaScript API：

- **上下文 API** - 获取会议、用户和参与者信息
- **会议操作** - 分享应用程序、邀请参与者、打开 URL
- **授权** - 使用 PKCE 的客户端 OAuth（无浏览器重定向）
- **Layers API** - 沉浸式视频布局和相机模式叠加
- **Collaborate 模式** - 跨参与者共享应用程序状态
- **应用程序通信** - 在应用程序实例之间传递消息（主客户端 <-> 会议）
- **媒体控制** - 虚拟背景、相机列表、录制控制
- **UI 控制** - 扩展应用程序、通知、弹出
- **事件** - 响应会议状态、参与者、共享等

## 前提条件

- 在 [Marketplace](https://marketplace.zoom.us/) 中将 Zoom 应用程序配置为 **"Zoom 应用程序"** 类型
- 具有与 Zoom 应用程序范围的 Zoom 应用程序 OAuth 凭据（客户端 ID + 密钥）
- Web 应用程序（推荐使用 Node.js + Express）
- **您的域名已列入 Marketplace 域名白名单**
- ngrok 或 HTTPS 隧道用于本地开发
- Node.js 18+（用于后端服务器）

## 快速入门

### 选项 A：NPM（推荐用于框架）

```bash
npm install @zoom/appssdk
```

```javascript
import zoomSdk from '@zoom/appssdk';

async function init() {
  try {
    const configResponse = await zoomSdk.config({
      capabilities: [
        'shareApp',
        'getMeetingContext',
        'getUserContext',
        'openUrl'
      ],
      version: '0.16'
    });

    console.log('运行上下文:', configResponse.runningContext);
    // 'inMeeting' | 'inMainClient' | 'inWebinar' | 'inImmersive' | ...

    const context = await zoomSdk.getMeetingContext();
    console.log('会议 ID:', context.meetingID);
  } catch (error) {
    console.error('未在 Zoom 内运行:', error.message);
    showDemoMode();
  }
}
```

### 选项 B：CDN（纯 JavaScript）

```html
<script src="https://appssdk.zoom.us/sdk.js"></script>

<script>
// 关键：不要声明 "let zoomSdk" - SDK 将 window.zoomSdk 定义为全局变量
// 使用 "let zoomSdk = ..." 会导致：SyntaxError: redeclaration of non-configurable global property
let sdk = window.zoomSdk;  // 使用不同的变量名

async function init() {
  try {
    const configResponse = await sdk.config({
      capabilities: ['shareApp', 'getMeetingContext', 'getUserContext'],
      version: '0.16'
    });

    console.log('运行上下文:', configResponse.runningContext);
  } catch (error) {
    console.error('未在 Zoom 内运行:', error.message);
    showDemoMode();
  }
}

function showDemoMode() {
  document.body.innerHTML = '<h1>预览模式</h1><p>在 Zoom 中打开此应用程序以使用。</p>';
}

document.addEventListener('DOMContentLoaded', () => {
  init();
  setTimeout(() => { if (!sdk) showDemoMode(); }, 3000);
});
</script>
```

## 关键：全局变量冲突

CDN 脚本定义了 `window.zoomSdk` 全局变量。**不要重新声明它：**

```javascript
// 错误 - 在 Zoom 的嵌入式浏览器中会导致 SyntaxError
let zoomSdk = null;
zoomSdk = window.zoomSdk;

// 正确 - 使用不同的变量名
let sdk = window.zoomSdk;

// 也正确 - NPM 导入（无冲突）
import zoomSdk from '@zoom/appssdk';
```

这仅适用于 CDN 方法。NPM 导入创建了一个模块作用域变量，没有冲突。

## 浏览器预览 / 示例模式

SDK 仅在 Zoom 客户端中运行。在普通浏览器中访问时：
- `window.zoomSdk` 存在，但 `sdk.config()` 抛出错误
- 始终实现 try/catch 并带有回退 UI
- 添加超时（3 秒）以防 SDK 挂起

## URL 白名单（必需）

**除非域名已白名单，否则应用程序将无法在 Zoom 中加载。**

1. 前往 [Zoom Marketplace](https://marketplace.zoom.us/)
2. 打开您的应用程序 -> **功能** 选项卡
3. 在 **Zoom 应用程序** 下找到 **添加允许列表**
4. 添加您的域名（例如，`yourdomain.com` 用于生产，`xxxxx.ngrok.io` 用于开发）

没有这个，Zoom 客户端会显示一个空白面板，没有任何错误消息。

## OAuth 范围（必需）

功能需要在 Marketplace 中启用匹配的 OAuth 范围：

| 功能 | 必需范围 |
|------|----------|
| `getMeetingContext` | `zoomapp:inmeeting` |
| `getUserContext` | `zoomapp:inmeeting` |
| `shareApp` | `zoomapp:inmeeting` |
| `openUrl` | `zoomapp:inmeeting` |
| `sendAppInvitation` | `zoomapp:inmeeting` |
| `runRenderingContext` | `zoomapp:inmeeting` |
| `authorize` | `zoomapp:inmeeting` |
| `getMeetingParticipants` | `zoomapp:inmeeting` |

**要添加范围：** Marketplace -> 您的应用程序 -> **范围** 选项卡 -> 添加必需的范围。

缺少范围 = 功能静默失败或抛出错误。如果添加新范围，用户必须重新授权。

## 运行上下文

您的应用程序在不同的 Zoom 表面中运行。`configResponse.runningContext` 告诉您在哪里：

| 上下文 | 表面 | 描述 |
|--------|------|------|
| `inMeeting` | 会议侧边栏 | 最常见。可用的完整会议 API |
| `inMainClient` | 主客户端面板 | 主选项卡。没有会议上下文 API |
| `inWebinar` | 网络研讨会侧边栏 | 主持人/参与者。会议 + 网络研讨会 API |
| `inImmersive` | Layers API | 全屏自定义渲染 |
| `inCamera` | 相机模式 | 虚拟相机叠加 |
| `inCollaborate` | Collaborate 模式 | 共享状态上下文 |
| `inPhone` | Zoom Phone | 电话呼叫应用程序 |
| `inChat` | 团队聊天 | 聊天侧边栏 |

有关特定上下文行为和 API，请参阅 **[运行上下文](concepts/running-contexts.md)**。

## SDK 初始化模式

每个 Zoom 应用程序都以 `config()` 开头：

```javascript
import zoomSdk from '@zoom/appssdk';

const configResponse = await zoomSdk.config({
  capabilities: [
    // 列出您将使用的所有 API
    'getMeetingContext',
    'getUserContext',
    'shareApp',
    'openUrl',
    'authorize',
    'onAuthorized'
  ],
  version: '0.16'
});

// configResponse 包含：
// {
//   runningContext: 'inMeeting',
//   clientVersion: '5.x.x',
//   unsupportedApis: []  // 在此客户端版本中不受支持的 API
// }
```

**规则：**
1. `config()` 必须在其他任何 SDK 方法之前调用
2. 仅在 `config()` 中列出的功能可用
3. 功能必须与 Marketplace 中的 OAuth 范围匹配
4. 检查 `unsupportedApis` 以实现优雅降级

## 客户端 OAuth（摘要）

最佳授权体验 - 无浏览器重定向：

```javascript
// 1. 从您的后端获取 code challenge
const { codeChallenge, state } = await fetch('/api/auth/challenge').then(r => r.json());

// 2. 触发客户端授权
await zoomSdk.authorize({ codeChallenge, state });

// 3. 监听授权结果
zoomSdk.addEventListener('onAuthorized', async (event) => {
  const { code, state } = event;
  // 4. 将 code 发送到后端以交换令牌
  await fetch('/api/auth/token', {
    method: 'POST',
    body: JSON.stringify({ code, state })
  });
});
```

有关完整实现，请参阅 **[客户端 OAuth 指南](examples/in-client-oauth.md)**。

## Layers API（摘要）

构建沉浸式视频布局和相机叠加：

```javascript
// 启动沉浸模式 - 替换画廊视图
await zoomSdk.runRenderingContext({ view: 'immersive' });

// 定位参与者视频源
await zoomSdk.drawParticipant({
  participantUUID: 'user-uuid',
  x: 0, y: 0, width: 640, height: 480, zIndex: 1
});

// 添加叠加图像
await zoomSdk.drawImage({
  imageData: canvas.toDataURL(),
  x: 0, y: 0, width: 1280, height: 720, zIndex: 0
});

// 退出沉浸模式
await zoomSdk.closeRenderingContext();
```

有关详细信息，请参阅 **[Layers 沉浸](examples/layers-immersive.md)** 和 **[相机模式](examples/layers-camera.md)**。

## 环境变量

| 变量 | 描述 | 位置 |
|------|------|------|
| `ZOOM_APP_CLIENT_ID` | 应用程序客户端 ID | Marketplace -> 应用程序 -> 应用程序凭据 |
| `ZOOM_APP_CLIENT_SECRET` | 应用程序客户端密钥 | Marketplace -> 应用程序 -> 应用程序凭据 |
| `ZOOM_APP_REDIRECT_URI` | OAuth 重定向 URL | 您的服务器 URL + `/auth` |
| `SESSION_SECRET` | Cookie 签名密钥 | 生成随机字符串 |
| `ZOOM_HOST` | Zoom 主机 URL | `https://zoom.us`（或 `https://zoomgov.com`） |

## 常见 API

| API | 描述 |
|------|------|
| `config()` | 初始化 SDK，请求功能 |
| `getMeetingContext()` | 获取会议 ID、主题、状态 |
| `getUserContext()` | 获取用户名、角色、参与者 ID |
| `getRunningContext()` | 获取当前运行上下文 |
| `getMeetingParticipants()` | 列出参与者 |
| `shareApp()` | 与参与者共享应用程序屏幕 |
| `openUrl({ url })` | 在外部浏览器中打开 URL |
| `sendAppInvitation()` | 邀请用户打开您的应用程序 |
| `authorize()` | 触发客户端 OAuth |
| `connect()` | 连接到其他应用程序实例 |
| `postMessage()` | 向连接的实例发送消息 |
| `runRenderingContext()` | 启动 Layers API（沉浸式/相机） |
| `expandApp({ action })` | 扩展/折叠应用程序面板 |
| `showNotification()` | 在 Zoom 中显示通知 |

## 完整文档库

### 核心概念
- **[架构](concepts/architecture.md)** - 前端/后端模式、嵌入式浏览器、深度链接、X-Zoom-App-Context
- **[运行上下文](concepts/running-contexts.md)** - 所有上下文、特定上下文 API、多实例通信
- **[安全](concepts/security.md)** - OWASP 标头、CSP、Cookie 安全、PKCE、令牌存储

### 完整示例
- **[快速入门](examples/quick-start.md)** - Hello World Express + SDK 应用程序
- **[客户端 OAuth](examples/in-client-oauth.md)** - PKCE 授权流
- **[Layers 沉浸](examples/layers-immersive.md)** - 自定义视频布局
- **[相机模式](examples/layers-camera.md)** - 虚拟相机叠加
- **[Collaborate 模式](examples/collaborate-mode.md)** - 跨参与者共享状态
- **[访客模式](examples/guest-mode.md)** - 未验证/验证/授权状态
- **[ breakout 会议室](examples/breakout-rooms.md)** - 房间检测和跨房间状态
- **[应用程序通信](examples/app-communication.md)** - connect + postMessage 在实例之间

### 故障排除
- **[常见问题](troubleshooting/common-issues.md)** - 快速诊断和错误代码
- **[调试](troubleshooting/debugging.md)** - 本地开发、ngrok、浏览器预览
- **[迁移](troubleshooting/migration.md)** - SDK 版本升级说明

### 参考
- **[API 参考](references/apis.md)** - 所有 100 多个 SDK 方法
- **[事件参考](references/events.md)** - 所有 SDK 事件监听器
- **[Layers API 参考](references/layers-api.md)** - 绘制和渲染方法
- **[OAuth 参考](references/oauth.md)** - Zoom 应用的 OAuth 流
- **[Zoom Mail](references/zmail-sdk.md)** - 邮件插件集成

## 示例存储库

### 官方（由 Zoom）

| 存储库 | 类型 | 最后更新 | 状态 | SDK 版本 |
|--------|------|----------|------|----------|
| [zoomapps-sample-js](https://github.com/zoom/zoomapps-sample-js) | Hello World (纯 JavaScript) | 2025 年 12 月 | 活跃 | ^0.16.26 |
| [zoomapps-advancedsample-react](https://github.com/zoom/zoomapps-advancedsample-react) | 高级 (React + Redis) | 2025 年 10 月 | 活跃 | 0.16.0 |
| [zoomapps-customlayout-js](https://github.com/zoom/zoomapps-customlayout-js) | Layers API | 2023 年 11 月 | 不活跃 | ^0.16.8 |
| [zoomapps-texteditor-vuejs](https://github.com/zoom/zoomapps-texteditor-vuejs) | Collaborate (Vue + Y.js) | 2023 年 10 月 | 不活跃 | ^0.16.7 |
| [zoomapps-serverless-vuejs](https://github.com/zoom/zoomapps-serverless-vuejs) | 无服务器 (Firebase) | 2024 年 8 月 | 不活跃 | ^0.16.21 |
| [zoomapps-cameramode-vuejs](https://github.com/zoom/zoomapps-cameramode-vuejs) | 相机模式 | - | - | - |
| [zoomapps-workshop-sample](https://github.com/zoom/zoomapps-workshop-sample) | 工作坊 | - | - | - |

**新项目推荐：** 使用 `@zoom/appssdk` 版本 `^0.16.26`。

### 社区

| 类型 | 存储库 | 描述 |
|------|--------|------|
| 库 | [harvard-edtech/zaccl](https://github.com/harvard-edtech/zaccl) | Zoom 应用程序完整连接库 |

**完整列表**：查看 [general/references/community-repos.md](../general/references/community-repos.md)

### 学习路径

1. **开始**：`zoomapps-sample-js` - 最简单、最新
2. **高级**：`zoomapps-advancedsample-react` - 全面（客户端 OAuth、访客模式、Collaborate）
3. **专业**：根据功能选择（Layers、无服务器、相机模式）

## 关键陷阱（来自实际开发）

### 1. 全局变量冲突
CDN 脚本定义了 `window.zoomSdk`。在您的代码中声明 `let zoomSdk` 会导致 `SyntaxError: redeclaration of non-configurable global property`。使用 `let sdk = window.zoomSdk` 或 NPM 导入。

### 2. 域名白名单
您的应用程序 URL **必须** 在 Marketplace 域名白名单中。没有它，Zoom 会显示一个空白面板，没有任何错误。还要添加 `appssdk.zoom.us` 和您使用的任何 CDN 域名。

### 3. 必须列出功能
仅当在 `config({ capabilities: [...] })` 中列出时，功能才可用。调用未列出的 API 会抛出错误。为事件监听器也是如此。

### 4. SDK 仅在 Zoom 内工作
`zoomSdk.config()` 在 Zoom 客户端外会抛出错误。始终用 try/catch 包裹并带有浏览器回退：
```javascript
try { await zoomSdk.config({...}); } catch { showBrowserPreview(); }
```

### 5. ngrok URL 更改
免费 ngrok URL 在重启时更改。您必须在 Marketplace 中更新 4 个位置：主页 URL、重定向 URL、OAuth 允许列表、域名允许列表。考虑 ngrok 付费计划以获得稳定的子域名。

### 6. 客户端 OAuth 与 Web OAuth
使用 `zoomSdk.authorize()`（客户端）以获得最佳用户体验 - 无需浏览器重定向。仅在从 Marketplace 进行初始安装时回退到 Web 重定向。

### 7. 摄像头模式 CEF 竞态条件
摄像头模式使用 CEF，初始化需要时间。如果过早调用 `drawImage`/`drawWebView`，可能会失败。实现带指数退避的重试。

### 8. Cookie 配置
Zoom 的嵌入式浏览器需要带有 `SameSite=None` 和 `Secure=true` 的 Cookie。没有这些，会话将静默中断。

### 9. 状态验证
始终验证 OAuth `state` 参数以防止 CSRF 攻击。生成加密随机状态，存储它并在回调时验证。

## 资源

- **官方文档**：https://developers.zoom.us/docs/zoom-apps/
- **SDK 参考**：https://appssdk.zoom.us/
- **NPM 包**：https://www.npmjs.com/package/@zoom/appssdk
- **开发者论坛**：https://devforum.zoom.us/
- **GitHub SDK 源代码**：https://github.com/zoom/appssdk

---

**需要帮助？** 从下方的集成索引部分开始，以获得完整导航。

---

## 集成索引

_本节是从 `SKILL.md` 迁移过来的。_

## 快速入门路径

**如果您是 Zoom 应用的新手，请按以下顺序操作：**

1. **首先运行预检** -> [RUNBOOK.md](RUNBOOK.md)

2. **阅读架构** -> [concepts/architecture.md](concepts/architecture.md)
   - 前端/后端模式、嵌入式浏览器、深度链接
   - 了解 Zoom 如何加载并与您的应用通信

3. **构建您的第一个应用** -> [examples/quick-start.md](examples/quick-start.md)
   - 完整的 Express + SDK Hello World
   - 本地开发的 ngrok 设置

4. **理解运行上下文** -> [concepts/running-contexts.md](concepts/running-contexts.md)
   - 您的应用运行的位置（inMeeting、inMainClient、inWebinar 等）
   - 上下文特定的 API 和限制

5. **实现 OAuth** -> [examples/in-client-oauth.md](examples/in-client-oauth.md)
   - 带有 PKCE 的客户端 OAuth（最佳用户体验）
   - 令牌交换和存储

6. **添加功能** -> [references/apis.md](references/apis.md)
   - 按类别组织的 100 多个 SDK 方法
   - 每个方法的代码示例

7. **故障排除** -> [troubleshooting/common-issues.md](troubleshooting/common-issues.md)
   - 常见问题的快速诊断

---

## 文档结构

```
zoom-apps-sdk/
├── SKILL.md                           # 主要技能概述
├── SKILL.md                           # 此文件 - 导航指南
│
├── concepts/                          # 核心架构模式
│   ├── architecture.md               # 前端/后端、嵌入式浏览器、OAuth 流
│   ├── running-contexts.md           # 应用运行位置 + 上下文特定 API
│   └── security.md                   # OWASP 标头、CSP、数据访问层
│
├── examples/                          # 完整的可用代码
│   ├── quick-start.md                # Hello World - 最小 Express + SDK 应用
│   ├── in-client-oauth.md            # 带有 PKCE 的客户端 OAuth
│   ├── layers-immersive.md           # Layers API - 浸入式模式（自定义布局）
│   ├── layers-camera.md              # Layers API - 摄像头模式（虚拟摄像头）
│   ├── collaborate-mode.md           # 协作模式（共享状态）
│   ├── guest-mode.md                 # 访客模式（未认证 -> 授权）
│   ├── breakout-rooms.md             # 小组讨论室集成
│   └── app-communication.md          # connect + postMessage 在实例之间
│
├── troubleshooting/                   # 问题解决指南
│   ├── common-issues.md              # 快速诊断、错误代码
│   ├── debugging.md                  # 本地开发设置、ngrok、浏览器预览
│   └── migration.md                  # SDK 版本迁移说明
│
└── references/                        # 参考文档
    ├── apis.md                        # 完整 API 参考（100 多个方法）
    ├── events.md                      # 所有 SDK 事件
    ├── layers-api.md                  # Layers API 详细参考
    ├── oauth.md                       # Zoom 应用的 OAuth 流
    └── zmail-sdk.md                   # Zoom 邮件集成
```

---

## 按用例划分

### 我想构建一个基本的 Zoom 应用
1. [架构](concepts/architecture.md) - 了解模式
2. [快速入门](examples/quick-start.md) - 构建 Hello World
3. [客户端 OAuth](examples/in-client-oauth.md) - 添加授权
4. [安全](concepts/security.md) - 必要的标头

### 我想沉浸式视频布局（Layers API）
1. [沉浸式 Layers](examples/layers-immersive.md) - 自定义视频位置
2. [Layers API 参考](references/layers-api.md) - 所有绘图方法
3. [应用通信](examples/app-communication.md) - 跨参与者同步布局

### 我想添加虚拟摄像头覆盖
1. [摄像头模式](examples/layers-camera.md) - 摄像头模式渲染
2. [Layers API 参考](references/layers-api.md) - 绘图方法

### 我想实时协作
1. [协作模式](examples/collaborate-mode.md) - 共享状态 API
2. [应用通信](examples/app-communication.md) - 实例消息传递

### 我想访客/匿名访问
1. [访客模式](examples/guest-mode.md) - 三个授权状态
2. [客户端 OAuth](examples/in-client-oauth.md) - promptAuthorize 流

### 我想支持小组讨论室
1. [小组讨论室](examples/breakout-rooms.md) - 房间检测和状态同步

### 我想在主客户端和会议之间同步
1. [应用通信](examples/app-communication.md) - connect + postMessage
2. [运行上下文](concepts/running-contexts.md) - 多实例行为

### 我想无服务器部署
1. [快速入门](examples/quick-start.md) - 首先了解基本模式
2. 示例：[zoomapps-serverless-vuejs](https://github.com/zoom/zoomapps-serverless-vuejs) - Firebase 模式

### 我想添加 Zoom 邮件集成
1. [Zoom 邮件参考](references/zmail-sdk.md) - REST API + 邮件插件

### 我遇到错误
1. [常见问题](troubleshooting/common-issues.md) - 快速诊断表
2. [调试](troubleshooting/debugging.md) - 本地开发设置、DevTools
3. [迁移](troubleshooting/migration.md) - 版本兼容性

---

## 最关键的文档

### 1. 架构（基础）
**[concepts/architecture.md](concepts/architecture.md)**

了解 Zoom 应用的工作原理：嵌入式浏览器中的前端，OAuth/API 的后端，SDK 作为桥梁。没有这个，其他任何东西都不起作用。

### 2. 快速入门（第一个应用）
**[examples/quick-start.md](examples/quick-start.md)**

完整的可用代码。在深入高级功能之前，先让一些东西运行起来。

### 3. 常见问题（最常见的问题）
**[troubleshooting/common-issues.md](troubleshooting/common-issues.md)**

90% 的 Zoom 应用问题都是：域名白名单、全局变量冲突或缺少功能。

---

## 关键学习

### 关键发现：

1. **全局变量冲突是 #1 潜在问题**
   - CDN 脚本定义 `window.zoomSdk` 为全局变量
   - `let zoomSdk = ...` 在 Zoom 的浏览器中导致 SyntaxError
   - 使用 `let sdk = window.zoomSdk` 或 NPM 导入

2. **域名白名单是不可协商的**
   - 如果域名未白名单，应用将显示空白面板，没有任何错误
   - 必须包含您的域名、`appssdk.zoom.us` 和任何 CDN 域名
   - ngrok URL 在重启时更改 - 必须每次更新 Marketplace

3. **config() 控制一切**
   - 必须首先调用，必须列出所有功能
   - 未列出的功能会抛出错误
   - 检查 `unsupportedApis` 以检查客户端版本兼容性

4. **客户端 OAuth > Web OAuth 以获得最佳用户体验**
   - `authorize()` 将用户保持在 Zoom 中（无需浏览器重定向）
   - Web 重定向仅在初始 Marketplace 安装时需要
   - 始终实现 PKCE（code_verifier + code_challenge）

5. **两个应用实例可以同时运行**
   - 主客户端实例 + 会议实例
   - 使用 `connect()` + `postMessage()` 在它们之间同步
   - 在主客户端中预会议设置，在会议中使用

6. **摄像头模式有 CEF 特性**
   - CEF 初始化需要时间
   - 如果过早调用绘图调用可能会失败
   - 使用带指数退避的重试

7. **Cookie 设置很重要**
   - 需要 `SameSite=None` + `Secure=true`
   - 没有这些，会话在嵌入式浏览器中会静默失败

---

## 快速参考

### "应用显示空白面板"
-> [域名白名单](troubleshooting/common-issues.md) - 将域名添加到 Marketplace

### "SyntaxError: redeclaration"
-> [全局变量](troubleshooting/common-issues.md) - 使用 `let sdk = window.zoomSdk`

### "config() 抛出错误"
-> [浏览器预览](troubleshooting/debugging.md) - SDK 仅在 Zoom 内部工作

### "API 调用静默失败"
-> [OAuth 范围](troubleshooting/common-issues.md) - 在 Marketplace 中添加所需的范围

### "如何实现 [功能]？"
-> [API 参考](references/apis.md) - 找到方法，检查所需的功能

### "如何本地测试？"
-> [调试指南](troubleshooting/debugging.md) - ngrok + Marketplace 配置

---

## 文档版本

基于 **@zoom/appssdk v0.16.x**（最新：0.16.26+）

---

**祝您编码愉快！**

从 [架构](concepts/architecture.md) 开始了解模式，然后从 [快速入门](examples/quick-start.md) 开始构建您的第一个应用。
