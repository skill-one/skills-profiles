# /build-zoom-video-sdk-app

为完全定制视频会话产品提供背景参考。当会议SDK和视频SDK之间的边界尚不明确时，优先考虑 `plan-zoom-product`。

使用Zoom的基础设施构建定制的视频体验。

## 硬件路由防护措施（首先阅读）

- 如果用户要求定制的实时视频应用程序行为（主题/会话加入、自定义渲染、附加/分离），请路由到视频SDK。
- 不要为视频SDK加入流程切换到REST会议端点。
- 视频SDK不使用会议ID、`join_url` 或会议SDK加入有效载荷字段（`meetingNumber`、`passWord`）。

## 会议SDK与视频SDK

| 功能 | 会议SDK | 视频SDK |
|------|--------|--------|
| UI | 默认Zoom UI或自定义UI | **完全自定义UI**（您自己构建） |
| 体验 | Zoom会议 | 视频会话 |
| 品牌定制 | 有限的定制 | **完全品牌控制** |
| 功能 | Zoom完整功能 | 核心视频功能 |

## UI选项（Web）

视频SDK为您提供 **完全控制UI** 的能力：

| 选项 | 描述 |
|------|------|
| **UI工具包** | 预构建的React组件（低代码） |
| **自定义UI** | 使用SDK API构建自己的UI |

## 前置条件

- 市场中的Zoom视频SDK凭证
- SDK密钥和密钥
- Web开发环境

> **需要OAuth或签名帮助吗？** 查看认证流程的 **[zoom-oauth](../oauth/SKILL.md)** 技能。

> **需要在Web上进行加入前诊断吗？** 在视频SDK `join()` 之前使用 **[probe-sdk](../probe-sdk/SKILL.md)** 来减少第一分钟的失败。

> **快速开始故障排除：** 在深入调试之前使用 **[5分钟运行手册](RUNBOOK.md)**。

## 快速入门（Web）

### NPM使用（像Vite/Webpack这样的打包器）

```javascript
import ZoomVideo from '@zoom/videosdk';

const client = ZoomVideo.createClient();
await client.init('en-US', 'Global', { patchJsMedia: true });
await client.join(topic, signature, userName, password);

// 重要提示：只有在加入后才能使用getMediaStream()
const stream = client.getMediaStream();
await stream.startVideo();
await stream.startAudio();
```

### CDN使用（无打包器）

> **警告：** 广告拦截器会拦截 `source.zoom.us`。为了防止问题，请自行托管SDK。

```bash
# 本地下载SDK
curl "https://source.zoom.us/videosdk/zoom-video-1.12.0.min.js" -o js/zoom-video-sdk.min.js
```

```html
<script src="js/zoom-video-sdk.min.js"></script>
```

```javascript
// CDN导出为WebVideoSDK，而不是ZoomVideo
// 必须使用 .default 属性
const ZoomVideo = WebVideoSDK.default;
const client = ZoomVideo.createClient();

await client.init('en-US', 'Global', { patchJsMedia: true });
await client.join(topic, signature, userName, password);

// 重要提示：只有在加入后才能使用getMediaStream()
const stream = client.getMediaStream();
await stream.startVideo();
await stream.startAudio();
```

### 使用CDN的ES模块（解决竞态条件）

当使用 `<script type="module">` 与CDN一起使用时，SDK可能尚未加载：

```javascript
// 在SDK加载后再使用
function waitForSDK(timeout = 10000) {
  return new Promise((resolve, reject) => {
    if (typeof WebVideoSDK !== 'undefined') {
      resolve();
      return;
    }
    const start = Date.now();
    const check = setInterval(() => {
      if (typeof WebVideoSDK !== 'undefined') {
        clearInterval(check);
        resolve();
      } else if (Date.now() - start > timeout) {
        clearInterval(check);
        reject(new Error('SDK加载失败'));
      }
    }, 100);
  });
}

// 使用方法
await waitForSDK();
const ZoomVideo = WebVideoSDK.default;
const client = ZoomVideo.createClient();
```

## SDK生命周期（关键顺序）

SDK具有严格的生命周期。违反它会导致静默失败。

```
1. 创建客户端：     client = ZoomVideo.createClient()
2. 初始化：        await client.init('en-US', 'Global', options)
3. 加入会话：      await client.join(topic, signature, userName, password)
4. 获取流：        stream = client.getMediaStream()  ← 只有在加入后
5. 开始媒体：       await stream.startVideo() / await stream.startAudio()
```

**常见错误（静默失败）：**

```javascript
// ❌ 错误：在加入前获取流
const client = ZoomVideo.createClient();
await client.init('en-US', 'Global');
const stream = client.getMediaStream();  // 返回undefined！
await client.join(...);

// ✅ 正确：在加入后获取流
const client = ZoomVideo.createClient();
await client.init('en-US', 'Global');
await client.join(...);
const stream = client.getMediaStream();  // 可以工作！
```

## 视频渲染（事件驱动）

**SDK是事件驱动的。** 您必须监听事件并相应地渲染视频。

### 使用 `attachVideo()` 而不是 `renderVideo()`

```javascript
import { VideoQuality } from '@zoom/videosdk';

// 启动您的摄像头
await stream.startVideo();

// 附加视频 - 返回要追加到DOM的元素
const element = await stream.attachVideo(userId, VideoQuality.Video_360P);
container.appendChild(element);

// 完成时分离
await stream.detachVideo(userId);
```

### 必须的事件

```javascript
// 当其他参与者的视频打开/关闭时
client.on('peer-video-state-change', async (payload) => {
  const { action, userId } = payload;
  if (action === 'Start') {
    const el = await stream.attachVideo(userId, VideoQuality.Video_360P);
    container.appendChild(el);
  } else {
    await stream.detachVideo(userId);
  }
});

// 当参与者加入/离开时
client.on('user-added', (payload) => { /* 检查bVideoOn */ });
client.on('user-removed', (payload) => { stream.detachVideo(payload.userId); });
```

有关完整事件处理模式的更多信息，请参阅 [web/references/web.md](web/references/web.md)。

## 关键概念

| 概念 | 描述 |
|------|------|
| 会话 | 视频会话（不是会议） |
| 主题 | 会话标识符（您选择的任何字符串） |
| 签名 | 授权的JWT |
| MediaStream | 音频/视频流控制 |

## 会话创建模型

**重要提示**：视频SDK会话是 **即时创建** 的，而不是预先创建的。

| 方面 | 视频SDK | 会议SDK |
|------|--------|--------|
| 预创建 | 不需要 | 首先通过API创建会议 |
| 会话开始 | 第一个参与者使用主题加入 | 加入现有的会议ID |
| 主题 | 任何字符串（您定义的） | API的会议ID |
| 安排 | 无 - 会话是临时的 | 会议可以安排 |

### 会话如何工作

1. **不需要预创建**：会话在有人加入之前不存在
2. **主题 = 会话ID**：任何使用相同 `topic` 字符串加入的参与者都会加入同一个会话
3. **第一个加入创建它**：会话在第一个参与者加入时创建
4. **没有会议ID**：没有像Zoom会议那样的数字会议ID

```javascript
// 会话在第一个用户加入时即时创建
// 任何字符串都可以作为主题 - 它成为会话标识符
await client.join('my-custom-session-123', signature, '用户名');

// 其他参与者使用相同的主题加入相同的会话
await client.join('my-custom-session-123', signature, '另一个用户');
```

### 签名端点设置

签名端点必须可以从前端无CORS问题地访问。

**选项1：同源代理（推荐）**

```nginx
# Nginx配置
location /api/ {
    proxy_pass http://YOUR_BACKEND_HOST:3005/api/;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
}
```

```javascript
// 前端使用相对URL（同源）
const response = await fetch('/api/signature', { ... });
```

**选项2：CORS配置**

```javascript
// Express.js后端
const cors = require('cors');
app.use(cors({
  origin: ['https://your-domain.com'],
  credentials: true
}));
```

**警告：** 混合内容（HTTPS页面 → HTTP API）将被浏览器阻止。

## 用例

| 用例 | 描述 |
|------|------|
| [视频SDK BYOS（自带存储）](../general/use-cases/video-sdk-bring-your-own-storage.md) | 将录制直接保存到您的S3存储桶 |

## BYOS（自带存储）

视频SDK功能 - Zoom将云录制 **直接** 保存到您的Amazon S3存储桶。无需下载。

> **官方文档**：https://developers.zoom.us/docs/build/storage/

**前提条件：**
- 具有云录制附加组件的视频SDK帐户（通用积分包含此功能）
- AWS S3存储桶

**认证选项：**
1. **AWS访问密钥** - 简单设置
2. **跨帐户访问** - 更安全（IAM角色假定）

**S3路径结构：**
```
Buckets/{bucketName}/cmr/byos/{YYYY}/{MM}/{DD}/{GUID}/cmr_byos/
```

**主要优势：**
- 零下载带宽成本
- 录制期间直接存储
- 仅需配置（无需webhook/下载代码）

**设置位置**：开发者门户 → 帐户设置 → 常规 → 沟通内容存储位置

有关完整设置指南，请参阅 **[../general/use-cases/video-sdk-bring-your-own-storage.md](../general/use-cases/video-sdk-bring-your-own-storage.md)**。

## 详细参考

### UI和组件
- **[references/ui-toolkit.md](references/ui-toolkit.md)** - Web预构建UI组件
- **[references/triage-intake.md](references/triage-intake.md)** - 首先要问什么（将模糊报告转化为答案）
- **[references/session-lifecycle.md](references/session-lifecycle.md)** - 正确的API顺序 + 事件驱动渲染
- **[references/licensing-and-entitlements.md](references/licensing-and-entitlements.md)** - 许可证/管理前提条件
- **[references/token-contract-test-spec.md](references/token-contract-test-spec.md)** - 共享后端令牌合同和跨平台冒烟测试

### 平台指南
- **[references/authorization.md](references/authorization.md)** - 视频SDK JWT生成
- **[web/SKILL.md](web/SKILL.md)** - Web视频SDK（JavaScript/TypeScript）
  - **[web/SKILL.md](web/SKILL.md)** - 完整文档导航
  - **[web/examples/react-hooks.md](web/examples/react-hooks.md)** - 官方React钩子库
  - **[web/examples/framework-integrations.md](web/examples/framework-integrations.md)** - Next.js, Vue/Nuxt模式
- **[react-native/SKILL.md](react-native/SKILL.md)** - React Native视频SDK（移动包装器，事件/辅助架构）
  - **[react-native/SKILL.md](react-native/SKILL.md)** - React Native文档导航
  - **[react-native/examples/session-join-pattern.md](react-native/examples/session-join-pattern.md)** - 令牌化会话加入流程
- **[flutter/SKILL.md](flutter/SKILL.md)** - Flutter视频SDK（移动包装器，事件驱动架构）
  - **[flutter/SKILL.md](flutter/SKILL.md)** - Flutter文档导航
  - **[flutter/examples/session-join-pattern.md](flutter/examples/session-join-pattern.md)** - 令牌化会话加入流程
- **[android/SKILL.md](android/SKILL.md)** - Android视频SDK（原生移动自定义UI，令牌化会话）
- **[ios/SKILL.md](ios/SKILL.md)** - iOS视频SDK（原生移动自定义UI，委托驱动生命周期）
- **[macos/SKILL.md](macos/SKILL.md)** - macOS视频SDK（桌面原生应用程序，自定义会话窗口）
- **[unity/SKILL.md](unity/SKILL.md)** - Unity视频SDK包装器（游戏引擎集成，场景驱动UX）
- **[linux/SKILL.md](linux/SKILL.md)** - Linux视频SDK概述（C++无头机器人）
- **[linux/linux.md](linux/linux.md)** - Linux C++ SDK（无头机器人，原始媒体捕获/注入）
- **[linux/references/linux-reference.md](linux/references/linux-reference.md)** - Linux API参考
- **[windows/SKILL.md](windows/SKILL.md)** - Windows C++ SDK（桌面应用程序，原始媒体捕获/注入）
- **[windows/references/windows-reference.md](windows/references/windows-reference.md)** - Windows API参考
- **[references/troubleshooting.md](references/troubleshooting.md)** - 常见问题和解决方案
- **[references/forum-top-questions.md](references/forum-top-questions.md)** - 常见论坛问题模式（要涵盖的内容）

## 示例存储库

### 官方（由Zoom）

| 类型 | 存储库 | 星标 |
|------|--------|------|
| Web | [videosdk-web-sample](https://github.com/zoom/videosdk-web-sample) | 137 |
| Web NPM | [videosdk-web](https://github.com/zoom/videosdk-web) | 56 |
| 认证 | [videosdk-auth-endpoint-sample](https://github.com/zoom/videosdk-auth-endpoint-sample) | 23 |
| UI工具包Web | [videosdk-zoom-ui-toolkit-web](https://github.com/zoom/videosdk-zoom-ui-toolkit-web) | 17 |
| UI工具包React | [videosdk-zoom-ui-toolkit-react-sample](https://github.com/zoom/videosdk-zoom-ui-toolkit-react-sample) | 17 |
| Next.js | [videosdk-nextjs-quickstart](https://github.com/zoom/videosdk-nextjs-quickstart) | 16 |
| 远程医疗 | [VideoSDK-Web-Telehealth](https://github.com/zoom/VideoSDK-Web-Telehealth) | 11 |
| Linux | [videosdk-linux-raw-recording-sample](https://github.com/zoom/videosdk-linux-raw-recording-sample) | - |

**完整列表**：参见 [general/references/community-repos.md](../general/references/community-repos.md)

## 资源

- **官方文档**：https://developers.zoom.us/docs/video-sdk/
- **开发者论坛**：https://devforum.zoom.us/

## 环境变量

- 参见 [references/environment-variables.md](references/environment-variables.md) 了解标准化的 `.env` 键和每个值的位置。

## Linux操作

- [linux/RUNBOOK.md](linux/RUNBOOK.md) - Linux平台预检和调试清单。
