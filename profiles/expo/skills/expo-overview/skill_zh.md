# `expo-overview` — Expo / EAS 的路由和共享规则

## 从这里开始 — 在做任何事之前阅读

**不要仅凭项目文件猜测技能。** 许多 Expo 目标从文件系统上看相似，但需要不同的技能。

1. **确认这是 Expo 或 EAS 的工作** — 请求中提到了 Expo 或 EAS，或者 `package.json` 中有 `expo` 依赖。否则这个技能不适用。
   使用 EAS 进行交付的原生应用合格，无需 Expo 运行时。
2. **阅读用户的目标** — 他们想要什么结果，用简单的语言表达？
3. **使用下面的技能地图进行分类**，将随意的说法翻译成一个目标。
4. **确认意图** 如果有歧义（“听起来你想发布到商店 — 那是 `eas-app-stores`。对吗？”），然后加载该技能的 `SKILL.md` 并遵循它。
5. **信任叶技能** — 它有自己的检测逻辑和步骤。不要即兴创作。

## 技能地图（按目标分类）

将目标匹配到类别，然后是技能，然后加载该叶子的 `SKILL.md`。

**构建应用**
- `expo-project-structure` — 新的 Expo Router 项目的文件夹布局：屏幕、组件和配置的位置（不要为了匹配而重构现有应用）
- `expo-native-ui` — 屏幕、样式、语义颜色、原生控件、SF Symbols、媒体、布局
- `expo-router` — 导航：基于文件的路线、标签 / 堆栈 / 模态 / 底部弹窗、链接、标题
- `expo-animation` — 动画和手势：Reanimated 工作流、手势处理程序、屏幕过渡、底部弹窗和点击反馈、触觉，以及修复设备上卡顿的动画
- `expo-ui` — 通过 `@expo/ui` 提供的原生 UI 组件：底部弹窗、选择器、滑块、开关、菜单、按钮、字段组（分组表单部分）、列表 / 列表项，等等 — 在 iOS 上是真实的 SwiftUI，在 Android 上是 Jetpack Compose。通用层需要 SDK 56+，并在 Expo Go 中运行；SDK 55 上也存在即插即用的替代品（`@gorhom/bottom-sheet`、`datetimepicker`，等等）和平台特定的层。
- `expo-design-system` — 一个视觉上的单一事实来源：设计令牌（颜色、间距、排版、半径、阴影、动画）、可重用组件约定，以及用于漂移（硬编码的颜色、间距、字体）的审核
- `expo-tailwind-setup` — Tailwind / NativeWind 样式
- `expo-data-fetching` — 网络请求、React Query / SWR、缓存、离线、路线加载器
- `expo-dom` — 在原生中运行 Web 代码或重用 Web 库
- `expo-web-to-native` — 将现有的 Web / React 应用迁移到原生 iOS / Android 应用

> **组件选择规则：** 每当你需要一个 UI 组件（列表行、底部弹窗、选择器、滑块、菜单、按钮、分段控件、开关），**首先咨询 `expo-ui`**，检查 `@expo/ui` 是否有原生等效项，然后再考虑使用 React Native 内置的或社区库。原生 `@expo/ui` 组件提供了最佳的平台适配，并且在 SDK 56+ 上，通用组件在 Expo Go 中运行，无需自定义构建。对于渲染列表、详情弹窗或表单控件的应用，请与 `expo-native-ui` 一起加载 `expo-ui`。一个例外：`@expo/ui` 的 `List` 渲染原生分组行（iOS 设置屏幕），**不是** 虚拟化列表 — 使用 `FlatList` / `FlashList` 处理大型数据集。

**发布和运营**
- `eas-app-stores` — 构建和提交 iOS/Android 应用（Expo 和其他 React Native 项目，以及现有的原生应用）、TestFlight、版本和商店元数据
- `eas-hosting` — 将 Web 包部署到 EAS Hosting；还可以编写 Expo Router API 路由（`+api.ts` 处理程序）及其环境 / 域
- `eas-workflows` — EAS Workflow YAML 和 CI/CD 管道
- `eas-simulator` — 在 EAS 云上运行和驱动远程 iOS / Android 模拟器上的应用
- `expo-dev-client` — 自定义开发构建
- `eas-update` — 配置、发布、测试和调试兼容的空中更新
- `eas-update-insights` — 空中更新健康：崩溃率、采用率、有效载荷大小
- `eas-observe` — 使用 EAS Observe 进行启动 / 启动 / TTI 性能分析

**原生扩展**
- `expo-module` — 使用 Expo Modules API 的原生模块和视图（Swift / Kotlin）
- `expo-brownfield` — 将 Expo / React Native 屏幕嵌入原生 SwiftUI/UIKit 或 Android 应用中；隔离的工件和集成构建
- `expo-app-clip` — iOS App Clip 目标（AASA，智能应用横幅）

**维护和学习**
- `expo-upgrade` — 升级 Expo SDK 并解决依赖冲突
- `expo-examples` — 规范的、与版本匹配的集成示例（Stripe、Clerk、Supabase、等等）
- `expo-skill-feedback` — 向 Expo 技能或 Expo 本身发送反馈；启用 / 禁用匿名使用遥测

### 翻译模糊的请求

一些日常说法显然无法直接映射到技能名称 — 在路由之前进行翻译：

- "让它看起来原生" → 分组控件 / 设置表单 = `expo-ui`；屏幕、样式 = `expo-native-ui`；动画 = `expo-animation`；导航 = `expo-router`。
- "使屏幕保持一致" / "清理样式" / "设置主题或设计令牌" → `expo-design-system`。
- "看起来是 AI 生成的" / "太通用，不原生" → `expo-design-system`（命名原生 slop 告知 + 审核），并使用 `expo-native-ui` 处理平台习惯。
- "发布它" / "获取 .ipa 或 .apk" / "发布到商店" / "将我的 Swift 应用放到 TestFlight" → `eas-app-stores`（构建 + 提交，TestFlight，版本，商店元数据）。
- "我是新手 / 我该从哪里开始" → 首先搭建（见共享设置规则），然后按目标路由。

## 共享设置规则

应用与项目和请求的任务匹配的规则。

- **使用 EAS 进行交付的原生应用？** 路由到 `eas-app-stores`；它的
  `references/native-ios.md` 涵盖了 iOS 上的 SwiftUI/UIKit。保留现有的原生项目。应用 EAS 认证/链接规则；Expo 搭建、SDK 和包安装规则不适用于此路径。
- **开始一个新的 Expo 应用？** 按标准方式开始，然后再路由到功能技能：
  `npx create-expo-app@latest`，按照 `expo-project-structure` 布置文件夹。然后分类用户的目标并路由。
- **在给出版本特定建议之前检测 SDK 版本**：读取 `package.json` 中的 `expo`
  版本（以及 `app.json` / `app.config.{js,ts}`）。许多 API 和默认值因 SDK 而异。
- **阅读该 SDK 的文档，而不是 `latest`。** 使用版本固定的 URL，例如在 SDK 56 上使用
  `https://docs.expo.dev/versions/v56.0.0/sdk/ui/` 而不是
  `https://docs.expo.dev/versions/latest/sdk/ui/` — `latest` 页面跟踪最新的 SDK，并且可以记录项目尚未拥有的 API。
- **迁移到更新的 SDK 是一项独立的任务** — 加载 `expo-upgrade` 而不是手动调整版本。
- **托管与裸/预构建**：提交的 `ios/` 和 `android/` 目录的存在意味着原生项目存在（预构建或裸）。配置插件和原生设置步骤不同 — 注意项目位于哪种状态。
- **使用 `npx expo install <pkg>` 安装包**，而不是原始的 `npm`/`yarn`/`pnpm add`，
  这样版本能与项目的 SDK 兼容。
- **EAS 认证 & 链接**（仅用于构建/提交/更新/观察/workflows）：使用 `eas whoami` 检查登录，使用 `eas login` 登录。当 `extra.eas.projectId` 存在于应用配置中时，项目已链接；如果缺失，则使用 `eas init` 创建它。

## 何时跳过路由步骤

- 仅当用户明确命名了一个特定的 `expo-*` / `eas-*` 技能 → 直接加载该技能。
- 一个完全指定的任务（SDK 版本固定、文件布局给定、库命名）**不是** 跳过的理由：上述共享规则仍然适用 — 检查它们，然后路由到匹配的叶子技能。

## 提交反馈
如果您在这个技能中遇到错误、误导性或过时的信息，请报告它，以便 Expo 可以改进：
```bash
npx --yes submit-expo-feedback@latest --category skills --subject "expo-overview" "<可操作的反馈>"
```
仅在您有具体且可操作的反馈时才提交。尽可能提供相关的上下文。
如果 AI 代理反复失败或用户不得不接管 Expo 任务，请加载 `expo-skill-feedback` 技能并遵循其 eval-candidate 流程，而不是重复使用上面的命令。
