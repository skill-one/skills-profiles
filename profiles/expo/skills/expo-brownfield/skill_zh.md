# Expo 老项目改造

一个**老项目**应用是指现有的原生 iOS 或 Android 应用，它逐步采用 React Native，而不是从一开始就是 React Native 的**新项目**。

## 首先检查宿主应用

识别现有应用的入口点、导航拥有者、原生构建系统、部署目标以及已链接的任何 React Native 运行时。从锁文件中记录 Expo、React Native 和老项目包的版本。将 EAS Build 或 Submit 添加到单独的 Swift 应用中不需要 React Native；将此任务路由到 `eas-app-stores`。

嵌入功能时，保留宿主的 SwiftUI `App` / UIKit 窗口和原生屏幕。**不要在手动维护的原生宿主中运行预构建**，包括在故障排除期间。一个隔离的 Expo 生产者可能使用 CNG；将其生成的 `ios/` 和 `android/` 与消费应用分开。

Expo 支持两种将 React Native 添加到老项目中的不同方式：

| 方法       | 发送到原生应用的组件                                  | 选择时机                                                                   |
| ---------- | -------------------------------------------------- | -------------------------------------------------------------------------- |
| **隔离**   | 预构建的 AAR / XCFramework                          | 原生团队不需要 Node 或 RN 工具链；RN 代码可以存放在单独的仓库中             |
| **集成**   | 将 React Native 源代码添加到现有的 Gradle / CocoaPods 构建 | 一个团队拥有所有内容；熟悉 RN 工具链；希望使用单一构建                      |

有关完整的决策矩阵，请参阅 [./references/comparison.md](./references/comparison.md)。

## 选择方法

使用这些快速规则——对于任何模糊的情况，请查阅 `comparison.md`。

- 如果 iOS/Android 团队必须将 RN 作为常规库依赖项（AAR 或 XCFramework）消费，而无需安装 Node、Yarn 或 React Native 构建工具链，则**选择隔离**。
- 如果 RN 代码和原生代码存放在不同的仓库中，或者以独立的节奏发布，则**选择隔离**。
- 如果一个团队同时拥有原生和 RN 代码，并且愿意将 React Native + Expo 添加到原生项目的 Gradle 和 CocoaPods 设置中，则**选择集成**。
- 两种方法都支持 Debug 中的 Metro 和 Fast Refresh。选择集成是为了共享构建所有权，而不是因为隔离缺乏实时 JS 迭代。

## 参考资料

- ./references/brownfield-isolated.md -- 将 RN 构建为 AAR/XCFramework 并从原生应用消费（BrownfieldActivity、ReactNativeViewController、ReactNativeView）
- ./references/brownfield-integrated.md -- 将 RN 和 Expo 直接添加到现有的 Gradle 和 CocoaPods 构建，保留原生应用外壳
- ./references/feature-integration.md -- 传递输入、返回结果、关闭、清理监听器、转发生命周期事件；包括 SwiftUI 宿主示例
- ./references/comparison.md -- 选择方法的决策标准、权衡和场景映射
- ./references/troubleshooting.md -- Metro 连接、构建、签名和模块解析问题，这两种方法都常见

更多信息请参阅 https://docs.expo.dev/brownfield/overview/

## 共享先决条件

两种方法都需要在构建 React Native 侧的环境中：

- **Node.js (LTS)** — 运行 Expo CLI 和 JavaScript 代码。
- 项目的包管理器和锁文件 — npm、Yarn、pnpm 或 Bun。不要仅仅为了遵循示例而切换包管理器。

iOS 构建环境需要 Xcode 和 CocoaPods（如果存在，则使用项目的 Gemfile/Bundler 设置）。隔离的消费者应用需要 Xcode，但不需要 CocoaPods 或 RN 工具链，只需消费工件即可。

## 选择兼容版本

对于现有的 Expo/RN 项目，保留其选择的 SDK 并使用 `npx expo install` 来对齐依赖项。不要仅仅为了遵循此技能而升级它。对于新的生产者，使用与宿主操作系统支持、依赖项和构建工具链兼容的**当前稳定 SDK**；在选择之前确认发布是稳定的。

在原生设置之前，请阅读 [./references/version-compatibility.md](./references/version-compatibility.md)，以匹配原生模板、工具链/操作系统要求以及不同 SDK 版本的构建默认值。一个纯粹的原生消费者没有 Expo SDK 版本可以固定，但必须满足工件的要求。

## 在宿主中验证功能

打开带有输入的 RN 屏幕，返回结果到原生，关闭，并使用新的输入重新打开。检查监听器清理和宿主的原始导航。然后使用 Release 工件停止 Metro 并以 Release 模式构建宿主。仅在 Expo Go 或生产者的示例应用中渲染不能验证集成。有关完整的验收场景，请参阅 [./references/feature-integration.md](./references/feature-integration.md)。

## 提交反馈
如果您在本技能中遇到错误、误导性或过时的信息，请报告它，以便 Expo 可以改进：
```bash
npx --yes submit-expo-feedback@latest --category skills --subject "expo-brownfield" "<可操作的反馈>"
```
只有当您有具体且可操作的反馈时才提交。尽可能包含所有相关的上下文。
如果 AI 代理反复失败或用户不得不接管 Expo 任务，请加载 `expo-skill-feedback` 技能并遵循其 eval-candidate 流程，而不是重复使用上面的命令。
