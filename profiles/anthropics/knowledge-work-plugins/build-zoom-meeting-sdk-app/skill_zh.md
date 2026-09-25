# /build-zoom-meeting-sdk-app

跨平台嵌入 Zoom 会议的背景参考，包括网页、移动端、桌面端和 Linux 机器人环境。建议优先使用 `build-zoom-meeting-app` 或 `build-zoom-bot`，然后根据平台细节路由至此。

# Zoom 会议 SDK

将完整的 Zoom 会议体验嵌入到网页、移动端、桌面端和无头集成中。

## 硬件路由防护措施（首次阅读）

- 如果用户需要在他们的应用 UI 中嵌入/加入会议，请路由到会议 SDK 实现。
- 除非用户明确要求会议资源管理或浏览器 `join_url` 链接，否则不要切换到纯 REST 会议链接流程。
- 会议 SDK 加入路径需要 SDK 签名 + SDK 加入调用；REST `join_url` 不是会议 SDK 加入负载。

## 前置条件

- 具备会议 SDK 凭据的 Zoom 应用
- 来自市场版的 SDK Key 和 Secret
- 平台特定的开发环境（网页、Android、iOS、macOS、虚幻引擎、Electron、Linux 或 Windows）

> **需要 OAuth 或签名帮助？** 查看 **[zoom-oauth](../oauth/SKILL.md)** 技能以获取认证流程。
>
> **需要在网页上进行加入前诊断？** 在 Meeting SDK 初始化/加入之前使用 **[probe-sdk](../probe-sdk/SKILL.md)** 以筛选低就绪设备/网络。
>
> **快速开始故障排除：** 在深入调试之前使用 **[5-Minute Runbook](RUNBOOK.md)**。

## 快速入门（网页 - 通过 CDN 的客户端视图）

```html
<script src="https://source.zoom.us/3.1.6/lib/vendor/react.min.js"></script>
<script src="https://source.zoom.us/3.1.6/lib/vendor/react-dom.min.js"></script>
<script src="https://source.zoom.us/3.1.6/lib/vendor/redux.min.js"></script>
<script src="https://source.zoom.us/3.1.6/lib/vendor/redux-thunk.min.js"></script>
<script src="https://source.zoom.us/3.1.6/lib/vendor/lodash.min.js"></script>
<script src="https://source.zoom.us/3.1.6/zoom-meeting-3.1.6.min.js"></script>

<script>
// CDN 提供 ZoomMtg（客户端视图 - 全页）
// 对于 ZoomMtgEmbedded（组件视图），请使用 npm

ZoomMtg.preLoadWasm();
ZoomMtg.prepareWebSDK();

ZoomMtg.init({
  leaveUrl: window.location.href,
  patchJsMedia: true,
  disableCORP: !window.crossOriginIsolated,
  success: function() {
    ZoomMtg.join({
      sdkKey: 'YOUR_SDK_KEY',
      signature: 'YOUR_SIGNATURE',  // 服务器端生成！
      meetingNumber: 'MEETING_NUMBER',
      userName: 'User Name',
      passWord: '',  // 注意：大写 W 的驼峰命名
      success: function(res) { console.log('Joined'); },
      error: function(err) { console.error(err); }
    });
  },
  error: function(err) { console.error(err); }
});
</script>
```

## 网页关键注意事项

### 1. CDN 与 npm - 不同的 API！

| 分发方式 | 全局对象 | 视图类型 | API 风格 |
|--------------|---------------|-----------|-----------|
| CDN (`zoom-meeting-{ver}.min.js`) | `ZoomMtg` | 客户端视图（全页） | 回调 |
| npm (`@zoom/meetingsdk`) | `ZoomMtgEmbedded` | 组件视图（可嵌入） | Promise |

### 2. 生产环境需要后端

**绝不要在客户端代码中暴露 SDK Secret。** 在服务器端生成签名：

```javascript
// server.js (Node.js 示例)
const KJUR = require('jsrsasign');

app.post('/api/signature', (req, res) => {
  const { meetingNumber, role } = req.body;
  const iat = Math.floor(Date.now() / 1000) - 30;
  const exp = iat + 60 * 60 * 2;
  
  const header = { alg: 'HS256', typ: 'JWT' };
  const payload = {
    sdkKey: process.env.ZOOM_SDK_KEY,
    mn: String(meetingNumber).replace(/\D/g, ''),
    role: parseInt(role, 10),
    iat, exp, tokenExp: exp
  };
  
  const signature = KJUR.jws.JWS.sign('HS256',
    JSON.stringify(header),
    JSON.stringify(payload),
    process.env.ZOOM_SDK_SECRET
  );
  
  res.json({ signature, sdkKey: process.env.ZOOM_SDK_KEY });
});
```

### 3. CSS 冲突 - 避免全局重置

全局 `* { margin: 0; }` 会破坏 Zoom 的 UI。限定你的样式：

```css
/* BAD */
* { margin: 0; padding: 0; }

/* GOOD */
.your-app, .your-app * { box-sizing: border-box; }
```

### 4. 客户端视图工具栏裁剪修复

如果工具栏超出屏幕，缩小 Zoom UI：

```css
#zmmtg-root {
  position: fixed !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  width: 100vw !important;
  height: 100vh !important;
  /* 对 SPA（React/Next 等）至关重要：确保 Zoom UI 不在应用外壳/覆盖层后面。 */
  z-index: 9999 !important;
  transform: scale(0.95) !important;
  transform-origin: top center !important;
}
```

### 5. 会议开始时隐藏你的应用

客户端视图会接管整个页面。隐藏你的 UI：

```javascript
// 在 ZoomMtg.init 成功回调中：
document.documentElement.classList.add('meeting-active');
document.body.classList.add('meeting-active');
```

```css
body.meeting-active .your-app { display: none !important; }
body.meeting-active { background: #000 !important; }
```

## UI 选项（网页）

会议 SDK 提供 **带定制选项的 Zoom UI**：

| 视图 | 描述 |
|------|-------------|
| **组件视图** | 可提取、可定制的 UI - 将会议嵌入 div 中 |
| **客户端视图** | 全页 Zoom UI 体验 |

**注意**：与视频 SDK 不同（需要从零构建 UI），会议 SDK 以 Zoom UI 为基础，并在其上添加定制功能。

## 关键概念

| 概念 | 描述 |
|---------|-------------|
| SDK Key/Secret | 来自市场版的凭证 |
| 签名 | 使用 SDK Secret 签名的 JWT |
| 组件视图 | 可提取、可定制的 UI（网页） |
| 客户端视图 | 网页全页 Zoom UI |

## 详细参考

### 平台指南
- **[android/SKILL.md](android/SKILL.md)** - Android SDK（默认/自定义 UI、加入/启动/认证生命周期、移动端集成）
- **[android/references/android-reference-map.md](android/references/android-reference-map.md)** - Android API 表面映射和漂移监控点
- **[ios/SKILL.md](ios/SKILL.md)** - iOS SDK（默认/自定义 UI、加入/启动/认证生命周期、移动端集成）
- **[ios/references/ios-reference-map.md](ios/references/ios-reference-map.md)** - iOS API 表面映射和漂移监控点
- **[macos/SKILL.md](macos/SKILL.md)** - macOS SDK（桌面默认/自定义 UI、服务控制器、主持人流程）
- **[macos/references/macos-reference-map.md](macos/references/macos-reference-map.md)** - macOS API 表面映射和漂移监控点
- **[unreal/SKILL.md](unreal/SKILL.md)** - 虚幻引擎包装器（C++/蓝图包装器行为和 SDK 映射）
- **[unreal/references/unreal-reference-map.md](unreal/references/unreal-reference-map.md)** - 虚幻包装器参考映射和版本滞后说明
- **[references/android.md](references/android.md)** - Android 指针文档，用于从宽泛的 Meeting SDK 查询快速路由
- **[references/ios.md](references/ios.md)** - iOS 指针文档，用于从宽泛的 Meeting SDK 查询快速路由
- **[references/macos.md](references/macos.md)** - macOS 指针文档，用于从宽泛的 Meeting SDK 查询快速路由
- **[references/unreal.md](references/unreal.md)** - 虚幻指针文档，用于从宽泛的 Meeting SDK 查询快速路由
- **[linux/SKILL.md](linux/SKILL.md)** - Linux SDK 无头机器人技能入口点
- **[linux/linux.md](linux/linux.md)** - Linux SDK（C++ 无头机器人、原始媒体访问）
- **[linux/references/linux-reference.md](linux/references/linux-reference.md)** - Linux 依赖项、Docker、故障排除
- **[react-native/SKILL.md](react-native/SKILL.md)** - React Native SDK（iOS/Android 包装器、加入/启动流程、桥接设置）
- **[react-native/SKILL.md](react-native/SKILL.md)** - React Native 完整导航
- **[electron/SKILL.md](electron/SKILL.md)** - Electron SDK（桌面包装器、认证/加入流程、模块控制器、原始数据）
- **[electron/SKILL.md](electron/SKILL.md)** - Electron 完整导航
- **[windows/SKILL.md](windows/SKILL.md)** - Windows SDK（C++ 桌面应用程序、原始媒体访问）
- **[windows/references/windows-reference.md](windows/references/windows-reference.md)** - Windows 依赖项、Visual Studio 设置、故障排除
- **[web/references/web.md](web/references/web.md)** - Web SDK（组件 + 客户端视图）
- **[web/references/web-tracking-id.md](web/references/web-tracking-id.md)** - 跟踪 ID 配置

### 功能
- **[references/authorization.md](references/authorization.md)** - SDK JWT 生成
- **[references/bot-authentication.md](references/bot-authentication.md)** - 机器人认证的 ZAK、OBF、JWT 令牌
- **[references/breakout-rooms.md](references/breakout-rooms.md)** - 程序化分组会议室管理
- **[references/ai-companion.md](references/ai-companion.md)** - 会议中的 AI 伴侣控制
- **[references/webinars.md](references/webinars.md)** - 网络研讨会 SDK 功能
- **[references/forum-top-questions.md](references/forum-top-questions.md)** - 常见论坛问题模式（需要涵盖的内容）
- **[references/triage-intake.md](references/triage-intake.md)** - 首先需要询问什么（将模糊报告转化为答案）
- **[references/signature-playbook.md](references/signature-playbook.md)** - 签名/根本原因剧本
- **[references/multiple-meetings.md](references/multiple-meetings.md)** - 加入多个会议/多个实例
- **[references/troubleshooting.md](references/troubleshooting.md)** - 常见问题和解决方案

## 示例仓库

### 官方（由 Zoom 提供）

| 类型 | 仓库 | Stars |
|------|------------|-------|
| Linux 无头 | [meetingsdk-headless-linux-sample](https://github.com/zoom/meetingsdk-headless-linux-sample) | 4 |
| Linux 原始数据 | [meetingsdk-linux-raw-recording-sample](https://github.com/zoom/meetingsdk-linux-raw-recording-sample) | 0 |
| 网页 | [meetingsdk-web-sample](https://github.com/zoom/meetingsdk-web-sample) | 643 |
| 网页 NPM | [meetingsdk-web](https://github.com/zoom/meetingsdk-web) | 324 |
| React | [meetingsdk-react-sample](https://github.com/zoom/meetingsdk-react-sample) | 177 |
| 认证 | [meetingsdk-auth-endpoint-sample](https://github.com/zoom/meetingsdk-auth-endpoint-sample) | 124 |
| Angular | [meetingsdk-angular-sample](https://github.com/zoom/meetingsdk-angular-sample) | 60 |
| Vue.js | [meetingsdk-vuejs-sample](https://github.com/zoom/meetingsdk-vuejs-sample) | 42 |

**完整列表**：参见 [general/references/community-repos.md](../general/references/community-repos.md)

## 资源

- **官方文档**：https://developers.zoom.us/docs/meeting-sdk/
- **开发者论坛**：https://devforum.zoom.us/

## 环境变量

- 参考 [references/environment-variables.md](references/environment-variables.md) 了解标准化的 `.env` 键和每个值的来源。
