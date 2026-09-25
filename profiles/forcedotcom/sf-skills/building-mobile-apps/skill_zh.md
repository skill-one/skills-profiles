# Salesforce 移动端

将用户引导至正确的 SDK 系列（Mobile SDK 或 Agentforce SDK）技能，用于构建与 Salesforce 集成的移动应用。在此处不实现功能；子技能负责场景检测和分步指导。

## 路由前

在两个维度上进行区分：**SDK 系列**（Mobile SDK 对比 Agentforce SDK）和**平台**（iOS 对比 Android）。它们不是互斥的——应用可以使用这两个 SDK。

如果用户的意图可能适用于任一 SDK，则在路由前询问。猜测错误会浪费用户的时间，因为子技能是平台和 SDK 特定的。

## 路由 — 哪个 SDK 系列？

| 用户情况 | SDK |
|---|---|
| 将最终用户认证至 Salesforce、同步记录 (MobileSync)、离线存储数据 (SmartStore)、生物识别登录、推送通知、REST 集成 | **Mobile SDK** |
| 嵌入 Agentforce 代理——聊天 UI、代理对话、作为主要界面的对话功能 | **Agentforce SDK** |
| 两者都适用（数据驱动应用并嵌入代理） | **Mobile SDK 优先**，然后在上面叠加 **Agentforce SDK** |

### 当两者都适用时的裁决规则

- 代理是 *主要界面*（聊天优先应用），还是 *数据驱动应用中的功能*？
  - 主要 → Agentforce SDK
  - 功能 → Mobile SDK；通过 Agentforce SDK 嵌入代理
- 最终用户是否认证至 Salesforce 数据？
  - 是 → 需要 Mobile SDK（可以在上面添加 Agentforce SDK）。
  - 否 → 单独使用 Agentforce SDK 可能就足够了（它使用访客认证）。
- 询问离线存储、同步、REST、推送或生物识别？→ Mobile SDK。
- 询问代理对话、聊天 UI 或流式响应？→ Agentforce SDK。

如果仍然不明确，直接询问用户。

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

这种顺序是这个技能拥有的唯一多技能逻辑。其他所有内容都存在于子技能中。

## 加载子技能

通过 harness 按名称调用子技能。如果本地不可用，提示用户使用 `npx skills add <repo>` 安装。如果用户确认（或已预授权安装），运行命令并加载子技能——不要让用户去弄清楚如何继续工作流。如果用户拒绝，停止并解释子技能拥有 SDK 的设置步骤，没有它工作流无法继续。每个子技能都从公共仓库发布：

| 技能 | 仓库 | 安装命令 |
|---|---|---|
| `ios-mobile-sdk` | [`forcedotcom/SalesforceMobileSDK-Templates`](https://github.com/forcedotcom/SalesforceMobileSDK-Templates) → `skills/ios-mobile-sdk/` | `npx --yes skills add forcedotcom/SalesforceMobileSDK-Templates --skill ios-mobile-sdk --yes` |
| `android-mobile-sdk` | [`forcedotcom/SalesforceMobileSDK-Templates`](https://github.com/forcedotcom/SalesforceMobileSDK-Templates) → `skills/android-mobile-sdk/` | `npx --yes skills add forcedotcom/SalesforceMobileSDK-Templates --skill android-mobile-sdk --yes` |
| `integrate-agentforce-ios` | [`salesforce/AgentforceMobileSDK-iOS`](https://github.com/salesforce/AgentforceMobileSDK-iOS) → `skills/integrate-agentforce-ios/` | `npx --yes skills add salesforce/AgentforceMobileSDK-iOS --skill integrate-agentforce-ios --yes` |
| `integrate-agentforce-android` | [`salesforce/AgentforceMobileSDK-Android`](https://github.com/salesforce/AgentforceMobileSDK-Android) → `skills/integrate-agentforce-android/` | `npx --yes skills add salesforce/AgentforceMobileSDK-Android --skill integrate-agentforce-android --yes` |

安装后，加载子技能并交由其接管。不要内联子技能的内容——子技能拥有场景检测、先决条件和分步指导。
