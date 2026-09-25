# /build-zoom-contact-center-app

Zoom Contact Center 集成跨应用、网页和原生移动端界面的背景参考。

Zoom Contact Center 实现指南：
- Zoom 客户端中的 Contact Center 应用（Zoom Apps SDK 路径）
- 网页渠道嵌入（聊天/视频/活动）
- 原生移动 SDK（Android/iOS）

官方文档：
- https://developers.zoom.us/docs/contact-center/
- https://developers.zoom.us/docs/contact-center/web/sdk-reference/
- https://marketplacefront.zoom.us/sdk/contact/android/index.html
- https://marketplacefront.zoom.us/sdk/contact/ios/index.html

## 路径引导

- 如果用户在 Zoom Contact Center 桌面客户端内构建应用，请遵循 Zoom Apps SDK 路径并使用此技能加上 `zoom-apps-sdk`。
- 如果用户在网站上嵌入聊天/视频组件，请跳转到 [web/SKILL.md](web/SKILL.md)。
- 如果用户正在集成原生 Android 或 iOS SDK 二进制文件，请跳转到 [android/SKILL.md](android/SKILL.md) 或 [ios/SKILL.md](ios/SKILL.md)。
- 如果用户需要 Contact Center 通话控制或队列 API，请与 [../rest-api/SKILL.md](../rest-api/SKILL.md) 链接。

## 快速链接

从这里开始：
1. [concepts/architecture-and-lifecycle.md](concepts/architecture-and-lifecycle.md)
2. [scenarios/high-level-scenarios.md](scenarios/high-level-scenarios.md)
3. [references/forum-top-questions.md](references/forum-top-questions.md)
4. [references/versioning-and-compatibility.md](references/versioning-and-compatibility.md)
5. [references/samples-validation.md](references/samples-validation.md)
6. [references/environment-variables.md](references/environment-variables.md)
7. [troubleshooting/common-drift-and-breaks.md](troubleshooting/common-drift-and-breaks.md)
8. [RUNBOOK.md](RUNBOOK.md)

平台技能：
- [android/SKILL.md](android/SKILL.md)
- [ios/SKILL.md](ios/SKILL.md)
- [web/SKILL.md](web/SKILL.md)

## 文档结构

```
contact-center/
├── SKILL.md
├── RUNBOOK.md
├── concepts/
│   └── architecture-and-lifecycle.md
├── scenarios/
│   └── high-level-scenarios.md
├── references/
│   ├── versioning-and-compatibility.md
│   ├── samples-validation.md
│   └── environment-variables.md
├── troubleshooting/
│   └── common-drift-and-breaks.md
├── android/
│   ├── SKILL.md
│   ├── concepts/sdk-lifecycle.md
│   ├── examples/service-patterns.md
│   ├── references/android-reference-map.md
│   └── troubleshooting/common-issues.md
├── ios/
│   ├── SKILL.md
│   ├── concepts/sdk-lifecycle.md
│   ├── examples/service-patterns.md
│   ├── references/ios-reference-map.md
│   └── troubleshooting/common-issues.md
└── web/
    ├── SKILL.md
    ├── concepts/lifecycle-and-events.md
    ├── examples/app-context-and-state.md
    ├── references/web-reference-map.md
    └── troubleshooting/common-issues.md
```

## 常见生命周期模式

1. 尽早初始化平台上下文。
2. 构建通道项（聊天/视频/ZVA 的 `entryId`，计划回调和活动流程的 `apiKey`）。
3. 获取服务/客户端实例。
4. 在用户交互前注册监听器/代理。
5. 启动流程（`fetchUI`，`startVideo` 或网页 SDK 打开/显示路径）。
6. 处理参与状态变化（`start`，`hold`，`resume`，`end`）和上下文切换。
7. 结束流程并释放资源（`endChat`/`endVideo`，`logout/logoff`，反初始化/释放）。

## 高级场景

- 存储每个 `engagementId` 笔记的代理侧边栏应用，并能跨上下文切换。
- 从网页标签启动的浏览器聊天/视频活动。
- 用于聊天/视频/计划回调的原生移动客户应用。
- 活动驱动的通道选择（聊天，ZVA，视频，计划回调）。
- 移动端掉线视频参与的重新加入流程。
- 具备 postMessage 事件契约的智能嵌入 CRM 软电话。

详情请见 [scenarios/high-level-scenarios.md](scenarios/high-level-scenarios.md)。

## 链接

- 认证和客户端内应用身份：[../zoom-apps-sdk/SKILL.md](../zoom-apps-sdk/SKILL.md) 和 [../oauth/SKILL.md](../oauth/SKILL.md)
- Contact Center REST 工作流：[../rest-api/SKILL.md](../rest-api/SKILL.md)
- 网页语音/聊天通道的 Cobrowse：[../cobrowse-sdk/SKILL.md](../cobrowse-sdk/SKILL.md)

## 环境变量

- 请见 [references/environment-variables.md](references/environment-variables.md) 了解标准化的 `.env` 键及其值来源。
