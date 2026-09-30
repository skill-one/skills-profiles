---
name: mobile-apps-create
description: 构建任何 Salesforce 原生移动应用（iOS 或 Android）的入口点。当用户说以下内容时触发： "构建一个 Salesforce iOS 应用"、"为我的 Android 应用添加 Salesforce 登录"、"设置 Mobile SDK"、"添加 MobileSync / SmartStore 离线存储"、"在我的移动应用中嵌入 Agentforce 代理"、"为 iOS/Android 添加 Agentforce 聊天"，或以其他方式要求创建、扩展或集成 Swift 或 Kotlin 中的 Salesforce 移动体验（MSDK、Agentforce SDK 或两者）。当用户正在构建非 Salesforce 移动应用、使用 React Native / Flutter / Ionic 而没有 Salesforce 集成、询问通用移动 UI 设计，或正在处理 Salesforce 相关的 Web/桌面界面（LWC、Experience Cloud、仅限 Mobile Publisher 品牌标识）时跳过。
---

# Salesforce 移动端

将用户引导至正确的 SDK 系列（Mobile SDK 或 Agentforce SDK）技能，用于构建与 Salesforce 集成的移动应用。在此处不应实现功能；子技能负责场景检测和分步指导。

## 路由前

在两个维度上进行歧义消除：**SDK 系列**（Mobile SDK 对比 Agentforce SDK）和**平台**（iOS 对比 Android）。它们并非互斥——一个应用可以使用这两个 SDK。

如果用户的意图可能适用于任一 SDK，应在路由前询问。猜测错误会浪费用户的时间，因为子技能是平台和 SDK 特定的。

## 路由 — 哪个 SDK 系列？

| 用户情况 | SDK |
|---|---|
| 将最终用户认证至 Salesforce、同步记录 (MobileSync)、离线存储数据 (SmartStore)、生物识别登录、推送通知、REST 集成 | **Mobile SDK** |
| 嵌入 Agentforce 代理——聊天界面、代理对话、作为主要界面的对话功能 | **Agentforce SDK** |
| 两者兼具（数据驱动应用并嵌入代理） | **Mobile SDK 优先**，然后在顶层叠加 **Agentforce SDK** |

### 当两者都适用时的裁决规则

- 代理是*主要界面*（聊天优先应用），还是*数据驱动应用中的功能*？
  - 主要 → Agentforce SDK
  - 功能 → Mobile SDK；通过 Agentforce SDK 嵌入代理
- 最终用户是否认证至 Salesforce 数据？
  - 是 → 需要 Mobile SDK（Agentforce SDK 可在顶层添加）。
  - 否 → 单独使用 Agentforce SDK 可能足够（它使用访客认证）。
- 询问离线存储、同步、REST、推送或生物识别？→ Mobile SDK。
- 询问代理对话、聊天界面或流式响应？→ Agentforce SDK。

如果仍不明确，直接询问用户。

## 路由 — 哪个平台？

| 平台 | Mobile SDK 技能 | Agentforce SDK 技能 |
|---|---|---|
| iOS (Swift) | `ios-mobile-sdk` | `integrate-agentforce-ios` |
| Android (Kotlin) | `android-mobile-sdk` | `integrate-agentforce-android` |

如果用户需要两个平台，分别路由至每个子技能——它们是独立的。

## 组合工作流（Mobile SDK + Agentforce SDK）

当应用需要两者时：

1. 首先路由至 Mobile SDK 平台技能以搭建和认证。
2. 路由至 Agentforce SDK 平台技能以叠加代理界面。
3. 将每个子技能的指导视为其 SDK 的权威；不要合并它们的步骤。每个 SDK 拥有自身的认证设置、依赖安装顺序和初始化序列——交错它们会导致配置冲突和初始化顺序错误。

这种顺序是这个技能拥有的唯一多技能逻辑。其他内容都包含在子技能中。

## 加载子技能

通过 harness 通过名称调用子技能。如果本地不可用，提示用户使用 `npx skills add <repo>` 安装。如果用户确认（或已预授权安装），运行命令并加载子技能——不要让用户去弄清楚如何继续工作流。如果用户拒绝，停止并解释子技能拥有 SDK 的设置步骤，没有它工作流无法继续。每个子技能都从公共仓库发布：

| 技能 | 仓库 | 安装命令 |
|---|---|---|
| `ios-mobile-sdk` | [`forcedotcom/SalesforceMobileSDK-Templates`](https://github.com/forcedotcom/SalesforceMobileSDK-Templates) → `skills/ios-mobile-sdk/` | `npx --yes skills add forcedotcom/SalesforceMobileSDK-Templates --skill ios-mobile-sdk --yes` |
| `android-mobile-sdk` | [`forcedotcom/SalesforceMobileSDK-Templates`](https://github.com/forcedotcom/SalesforceMobileSDK-Templates) → `skills/android-mobile-sdk/` | `npx --yes skills add forcedotcom/SalesforceMobileSDK-Templates --skill android-mobile-sdk --yes` |
| `integrate-agentforce-ios` | [`salesforce/AgentforceMobileSDK-iOS`](https://github.com/salesforce/AgentforceMobileSDK-iOS) → `skills/integrate-agentforce-ios/` | `npx --yes skills add salesforce/AgentforceMobileSDK-iOS --skill integrate-agentforce-ios --yes` |
| `integrate-agentforce-android` | [`salesforce/AgentforceMobileSDK-Android`](https://github.com/salesforce/AgentforceMobileSDK-Android) → `skills/integrate-agentforce-android/` | `npx --yes skills add salesforce/AgentforceMobileSDK-Android --skill integrate-agentforce-android --yes` |

安装后，加载子技能并交由其接管。不要内联子技能的内容——子技能拥有场景检测、先决条件和分步指导。
