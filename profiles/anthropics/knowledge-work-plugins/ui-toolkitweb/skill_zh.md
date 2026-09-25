# Zoom 视频SDK UI工具包

Web上预构建的Zoom视频SDK UI工具包的背景参考。当用户可能仍然需要会议SDK时，请优先考虑`choose-zoom-approach`。

**官方文档**: https://developers.zoom.us/docs/video-sdk/web/ui-toolkit/
**API参考**: https://marketplacefront.zoom.us/sdk/uitoolkit/web/
**NPM包**: https://www.npmjs.com/package/@zoom/videosdk-zoom-ui-toolkit
**在线演示**: https://sdk.zoom.com/videosdk-uitoolkit

## 快速链接

**新手上UI工具包？请遵循此路径：**

1. **快速入门** - 5分钟内启动（见下文）
2. **JWT认证** - 服务器端令牌生成（必需）
3. **组合与组件** - 选择您的方案
4. **框架集成** - React、Vue、Angular、Next.js模式
5. **集成索引** - 查看本文件下方的此部分

**遇到问题？**
- 会话无法加入 → 检查JWT认证（最常见问题）
- React 18依赖项错误 → 查看安装部分
- CSS未加载 → 查看[Troubleshooting](troubleshooting/common-issues.md)
- 组件未显示 → 检查组件生命周期
- 先进行预检 → [5分钟Runbook](RUNBOOK.md)

## 概述

Zoom视频SDK UI工具包是一个**预构建的视频UI库**，使用最少的代码即可渲染完整的视频会议体验。与原始视频SDK不同，UI工具包提供：

- ✅ **即用型UI** - 开箱即用的专业视频界面
- ✅ **零UI代码** - 无需构建视频布局、控件或参与者管理
- ✅ **框架无关** - 兼容React、Vue、Angular、Next.js、纯JavaScript
- ✅ **高度可定制** - 选择要启用的功能，自定义主题
- ✅ **内置功能** - 聊天、屏幕共享、设置、虚拟背景等

**何时使用UI工具包：**
- 您想快速获得完整的视频解决方案
- 您需要Zoom风格的UI一致性
- 您不想构建自定义视频UI
- 您需要标准功能（聊天、共享、参与者）

**何时使用原始视频SDK：**
- 您需要完整的自定义UI控制
- 您正在构建非标准的视频体验
- 您需要访问原始视频/音频数据
- 您想构建自己的渲染管道

## 安装

```bash
npm install @zoom/videosdk-zoom-ui-toolkit jsrsasign
npm install -D @types/jsrsasign
```

**注意**：React支持取决于UI工具包版本。检查您安装版本的包依赖项（通常需要React 18）。

## 快速入门

### 基本用法（纯JavaScript）

```javascript
import uitoolkit from "@zoom/videosdk-zoom-ui-toolkit";
import "@zoom/videosdk-ui-toolkit/dist/videosdk-zoom-ui-toolkit.css";

const container = document.getElementById("sessionContainer");

const config = {
  videoSDKJWT: "your_jwt_token",
  sessionName: "my-session",
  userName: "John Doe",
  sessionPasscode: "",
  features: ["video", "audio", "share", "chat", "users", "settings"],
};

uitoolkit.joinSession(container, config);

uitoolkit.onSessionJoined(() => {
  console.log("会话已加入");
});

uitoolkit.onSessionClosed(() => {
  console.log("会话已关闭");
});
```

### Next.js / React集成

```typescript
'use client';

import { useEffect, useRef } from 'react';

export default function VideoSession({ jwt, sessionName, userName }) {
  const containerRef = useRef<HTMLDivElement>(null);
  const uitoolkitRef = useRef<any>(null);

  useEffect(() => {
    let isMounted = true;

    const init = async () => {
      const uitoolkitModule = await import('@zoom/videosdk-zoom-ui-toolkit');
      const uitoolkit = uitoolkitModule.default;
      uitoolkitRef.current = uitoolkit;
      
      // 如果TypeScript抱怨CSS导入，请配置您的应用程序以允许它们
      // （例如通过全局`declare module \"*.css\";`），或者从全局入口点（Next.js layout/_app）
      // 而不是在这里内联导入CSS。
      await import('@zoom/videosdk-ui-toolkit/dist/videosdk-zoom-ui-toolkit.css');

      if (!isMounted || !containerRef.current) return;

      const config: any = {
        videoSDKJWT: jwt,
        sessionName: sessionName,
        userName: userName,
        sessionPasscode: '',
        features: ['video', 'audio', 'share', 'chat', 'users', 'settings'],
      };

      uitoolkit.joinSession(containerRef.current, config);
      uitoolkit.onSessionJoined(() => console.log('Joined'));
      uitoolkit.onSessionClosed(() => console.log('Closed'));
    };

    init();

    return () => {
      isMounted = false;
      if (uitoolkitRef.current && containerRef.current) {
        try {
          uitoolkitRef.current.closeSession(containerRef.current);
        } catch (e) {}
      }
    };
  }, [jwt, sessionName, userName]);

  return <div ref={containerRef} style={{ width: '100%', height: '100vh' }} />;
}
```

## 可用功能

| 功能 | 描述 |
|---------|-------------|
| `video` | 启用视频布局和发送/接收视频 |
| `audio` | 显示音频按钮，发送/接收音频 |
| `share` | 屏幕共享 |
| `chat` | 会话内消息 |
| `users` | 参与者列表 |
| `settings` | 设备选择、虚拟背景 |
| `preview` | 加入前摄像头/麦克风预览 |
| `recording` | 云录制（付费计划） |
| `leave` | 离开/结束会话按钮 |

## 故障排除

- **[troubleshooting/common-issues.md](troubleshooting/common-issues.md)** - CSS、SSR、JWT/会话加入、定制限制

## JWT令牌生成（服务器端）

**必需**：在您的服务器上生成JWT令牌，切勿在客户端暴露SDK密钥。

### Node.js / Next.js API路由

```typescript
import { NextRequest, NextResponse } from 'next/server';
import { KJUR } from 'jsrsasign';

const ZOOM_VIDEO_SDK_KEY = process.env.ZOOM_VIDEO_SDK_KEY;
const ZOOM_VIDEO_SDK_SECRET = process.env.ZOOM_VIDEO_SDK_SECRET;

export async function POST(request: NextRequest) {
  const { sessionName, role, userName } = await request.json();

  if (!sessionName || role === undefined) {
    return NextResponse.json({ error: '缺少参数' }, { status: 400 });
  }

  const iat = Math.floor(Date.now() / 1000);
  const exp = iat + 60 * 60 * 2; // 2小时

  const oHeader = { alg: 'HS256', typ: 'JWT' };
  const oPayload = {
    app_key: ZOOM_VIDEO_SDK_KEY,
    role_type: role, // 0 = 参与者, 1 = 主持人
    tpc: sessionName,
    version: 1,
    iat,
    exp,
    user_identity: userName || 'User',
  };

  const signature = KJUR.jws.JWS.sign(
    'HS256',
    JSON.stringify(oHeader),
    JSON.stringify(oPayload),
    ZOOM_VIDEO_SDK_SECRET
  );

  return NextResponse.json({ signature });
}
```

### JWT负载字段

| 字段 | 是否必需 | 描述 |
|-------|----------|-------------|
| `app_key` | 是 | 您的视频SDK密钥 |
| `role_type` | 是 | 0 = 参与者, 1 = 主持人 |
| `tpc` | 是 | 会话/主题名称 |
| `version` | 是 | 始终为1 |
| `iat` | 是 | 发行人（Unix时间戳） |
| `exp` | 是 | 过期（Unix时间戳） |
| `user_identity` | 否 | 用户标识符 |

## API参考

### 核心方法

```javascript
uitoolkit.joinSession(container, config);
uitoolkit.closeSession(container);
```

### 事件监听器

```javascript
uitoolkit.onSessionJoined(callback);
uitoolkit.onSessionClosed(callback);
uitoolkit.offSessionJoined(callback);
uitoolkit.offSessionClosed(callback);
```

### 组件方法

```javascript
uitoolkit.showChatComponent(container);
uitoolkit.hideChatComponent(container);
uitoolkit.showUsersComponent(container);
uitoolkit.hideUsersComponent(container);
uitoolkit.showControlsComponent(container);
uitoolkit.hideControlsComponent(container);
uitoolkit.showSettingsComponent(container);
uitoolkit.hideSettingsComponent(container);
uitoolkit.hideAllComponents();
```

## CDN使用（无构建步骤）

```html
<link rel="stylesheet" href="https://source.zoom.us/uitoolkit/2.3.5-1/videosdk-zoom-ui-toolkit.css" />
<script src="https://source.zoom.us/uitoolkit/2.3.5-1/videosdk-zoom-ui-toolkit.min.umd.js"></script>

<div id="sessionContainer"></div>

<script>
  const uitoolkit = window.UIToolkit;
  
  uitoolkit.joinSession(document.getElementById('sessionContainer'), {
    videoSDKJWT: 'your_jwt',
    sessionName: 'my-session',
    userName: 'User',
    features: ['video', 'audio', 'chat']
  });
</script>
```

## Next.js with basePath

当在子路径下部署Next.js时：

```typescript
// next.config.ts
const nextConfig = {
  basePath: "/your-app-path",
  assetPrefix: "/your-app-path",
};
```

使用完整路径获取API路由：
```typescript
fetch('/your-app-path/api/token', { ... })
```

## 前置条件

1. **Zoom视频SDK凭证** 从 [Zoom Marketplace](https://marketplace.zoom.us/)
2. **兼容的React**版本（检查依赖项；常见的是React 18）
3. **服务器端JWT生成**（切勿在客户端暴露SDK密钥）
4. **现代浏览器** 带有WebRTC支持

## 浏览器支持

| 浏览器 | 版本 |
|---------|---------|
| Chrome | 78+ |
| Firefox | 76+ |
| Safari | 14.1+ |
| Edge | 79+ |

## 常见问题

| 问题 | 解决方案 |
|-------|----------|
| `peer react@"^18.0.0"`错误 | 使用安装的UI工具包包所需的React版本（检查依赖项；常见的是React 18） |
| CSS导入TypeScript错误 | 配置TS/CSS处理（优先使用全局`*.css`模块声明）；避免`@ts-ignore`，除非是在一次性演示中 |
| 配置类型错误 | 将配置作为`any`类型 |
| API返回HTML而不是JSON | 检查fetch URL中的basePath |

## 资源

- **GitHub**: https://github.com/zoom/videosdk-zoom-ui-toolkit-web
- **UI工具包文档**: https://developers.zoom.us/docs/video-sdk/web/ui-toolkit/
- **认证端点示例**: https://github.com/zoom/videosdk-auth-endpoint-sample
- **市场**: https://marketplace.zoom.us/

---

## 集成索引

_本节从`SKILL.md`迁移而来。_

所有UI工具包文档的完整导航。

## 📚 从这里开始

新手上UI工具包？请遵循此学习路径：

1. **[SKILL.md](SKILL.md)** - 主要概述和快速入门
2. **[5-Minute Runbook](RUNBOOK.md)** - 深入调试前的预检
3. **快速入门指南** - 5分钟内的工作代码（见skill.md）
4. **JWT认证** - 服务器端令牌生成（见skill.md）
5. **选择您的模式** - 组合与组件（见skill.md）

## 🎯 核心概念

了解UI工具包的工作原理：

- **组合与组件** - 使用UI工具包的两种方式（见skill.md）
- **UI工具包架构** - 它如何内部包装视频SDK
- **功能配置** - 理解featuresOptions结构
- **会话生命周期** - 加入→活动→离开/关闭→销毁流程

## 📖 完整指南

### 入门指南
- **安装** - NPM安装和React 18设置（见skill.md）
- **快速入门-组合** - 一个容器中的完整UI（见skill.md）
- **快速入门-组件** - 单个UI组件（见skill.md）
- **JWT认证** - 服务器端令牌生成（见skill.md）

### 框架集成
- **React集成** - Hooks、useEffect模式（见skill.md）
- **Vue.js集成** - Composition API和Options API（见skill.md）
- **Angular集成** - 组件生命周期（见skill.md）
- **Next.js集成** - App Router、服务器组件（见skill.md）
- **纯JavaScript** - 无框架使用（见skill.md）

### 高级主题
- **组件生命周期** - 挂载、卸载、清理模式
- **事件监听器** - 响应会话事件
- **会话管理** - 程序化控制
- **质量统计** - 监控连接质量
- **自定义主题** - 主题定制
- **虚拟背景** - 自定义背景图像

## 📚 API参考

完整API文档：

- **核心方法**（见skill.md）
  - `joinSession()` - 开始视频会话
  - `closeSession()` - 结束会话并移除UI
  - `destroy()` - 清理UI工具包实例
  - `leaveSession()` - 不销毁UI离开

- **组件方法**（见skill.md）
  - `showControlsComponent()` - 显示控制条
  - `showChatComponent()` - 显示聊天面板
  - `showUsersComponent()` - 显示参与者列表
  - `showSettingsComponent()` - 显示设置面板
  - `hideAllComponents()` - 隐藏所有组件

- **事件监听器**（见skill.md）
  - `onSessionJoined()` - 会话成功加入
  - `onSessionClosed()` - 会话结束
  - `onSessionDestroyed()` - UI工具包销毁
  - `onViewTypeChange()` - 视图模式更改
  - `on()` - 订阅视频SDK事件
  - `off()` - 取消订阅事件

- **信息方法**（见skill.md）
  - `getSessionInfo()` - 获取会话详细信息
  - `getCurrentUserInfo()` - 获取当前用户
  - `getAllUser()` - 获取所有参与者
  - `getClient()` - 获取底层视频SDK客户端
  - `version()` - 获取版本信息

- **控制方法**（见skill.md）
  - `changeViewType()` - 切换视图模式
  - `mirrorVideo()` - 镜像自己的视频
  - `isSupportCustomLayout()` - 检查设备支持

- **统计方法**（见skill.md）
  - `subscribeAudioStatisticData()` - 音频质量统计
  - `subscribeVideoStatisticData()` - 视频质量统计
  - `subscribeShareStatisticData()` - 共享质量统计

## 🔧 配置

- **功能配置**（见skill.md）
  - `featuresOptions`结构
  - 音频/视频选项
  - 聊天、用户、设置
  - 虚拟背景
  - 录制、字幕（付费功能）
  - 主题定制
  - 视图模式

- **会话配置**（见skill.md）
  - 必需的：`videoSDKJWT`, `sessionName`, `userName`
  - 可选的：`sessionPasscode`, `sessionIdleTimeoutMins`
  - 调试模式
  - Web端点
  - 语言设置

## ⚠️ 故障排除

### 常见问题
- React 18依赖项错误
- JWT令牌无效
- CSS未加载
- 组件未显示
- 会话加入失败

参见：**[troubleshooting/common-issues.md](troubleshooting/common-issues.md)**

### 框架特定问题
- React：SSR、hydration、清理
- Vue：响应性、生命周期
- Angular：模块导入、AOT
- Next.js：App Router、服务器组件

### 会话问题
- 认证失败
- 连接问题
- 视频音频不工作
- 屏幕共享问题

## 📦 示例应用程序

**官方仓库**：

| 框架 | 仓库 | 关键功能 |
|-----------|------------|--------------|
| React | [videosdk-zoom-ui-toolkit-react-sample](https://github.com/zoom/videosdk-zoom-ui-toolkit-react-sample) | Hooks, TypeScript |
| Vue.js | [videosdk-zoom-ui-toolkit-vuejs-sample](https://github.com/zoom/videosdk-zoom-ui-toolkit-vuejs-sample) | Composition API |
| Angular | [videosdk-zoom-ui-toolkit-angular-sample](https://github.com/zoom/videosdk-zoom-ui-toolkit-angular-sample) | Services, Guards |
| JavaScript | [videosdk-zoom-ui-toolkit-javascript-sample](https://github.com/zoom/videosdk-zoom-ui-toolkit-javascript-sample) | 纯JavaScript |
| 认证端点 | [videosdk-auth-endpoint-sample](https://github.com/zoom/videosdk-auth-endpoint-sample) | Node.js JWT |

## 🌐 外部资源

- **官方文档**: https://developers.zoom.us/docs/video-sdk/web/ui-toolkit/
- **API参考**: https://marketplacefront.zoom.us/sdk/uitoolkit/web/
- **NPM包**: https://www.npmjs.com/package/@zoom/videosdk-zoom-ui-toolkit
- **市场**: https://marketplace.zoom.us/
- **开发者论坛**: https://devforum.zoom.us/
- **在线演示**: https://sdk.zoom.com/videosdk-uitoolkit
- **版本日志**: https://developers.zoom.us/changelog/ui-toolkit/web/

## 🎓 学习路径

### 初学者
1. 阅读[SKILL.md](SKILL.md)概述
2. 跟随快速入门-组合
3. 在服务器上生成JWT
4. 加入您的第一个会话
5. 探索可用功能

### 中级
1. 尝试组件模式
2. 添加事件监听器
3. 自定义主题
4. 添加虚拟背景
5. 与您的框架集成

### 高级
1. 访问底层视频SDK
2. 订阅质量统计
3. 处理所有边缘情况
4. 实现自定义布局
5. 构建生产就绪的应用程序

## 📋 快速参考卡

### 最小工作示例

```javascript
import uitoolkit from "@zoom/videosdk-zoom-ui-toolkit";
import "@zoom/videosdk-ui-toolkit/dist/videosdk-zoom-ui-toolkit.css";

const config = {
  videoSDKJWT: "YOUR_JWT",
  sessionName: "test-session",
  userName: "User",
  featuresOptions: {
    video: { enable: true },
    audio: { enable: true }
  }
};

uitoolkit.joinSession(document.getElementById("container"), config);
uitoolkit.onSessionJoined(() => console.log("Joined"));
uitoolkit.onSessionClosed(() => uitoolkit.destroy());
```

### 必记规则

1. ✅ **始终**在服务器端生成JWT
2. ✅ **始终**在清理时调用`destroy()`
3. ✅ **始终**使用React 18（不是17/19）
4. ✅ **始终**导入CSS文件
5. ❌ **切勿**在客户端暴露SDK密钥
6. ❌ **切勿**跳过`onSessionClosed`清理
7. ❌ **切勿**在组件加入会话前调用

## 📞 支持

- **开发者论坛**: https://devforum.zoom.us/
- **开发者支持**: https://developers.zoom.us/support/
- **高级支持**: https://explore.zoom.us/en/support-plans/developer/

---

**导航**: [← 返回SKILL.md](SKILL.md)

## 环境变量

- 查看[references/environment-variables.md](references/environment-variables.md)以获取标准化的`.env`键以及每个值的来源。
