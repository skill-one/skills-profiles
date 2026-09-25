# 迁移到 React Native

仅在决定采用遗留迁移后使用此技能。当用户仍在选择遗留迁移、新建项目、基于检查点的路径、推迟或无迁移之间时，请先使用 `[assess-react-native-migration](../assess-react-native-migration/SKILL.md)`。

## 概述

使用 `@callstack/react-native-brownfield` 在现有原生应用中逐步采用 React Native 的指导性工作流程，从初始设置到分阶段的主机集成。

- Expo 路径
- 裸 React Native 路径

每个任务使用一个路径，除非用户明确要求迁移或比较。

## 迁移策略

用于遗留迁移规划和执行的策略：

1. 评估应用状态并选择 Expo 或裸路径。
2. 使用 `@callstack/react-native-brownfield` 执行初始设置。
3. 从 React Native 源应用打包 RN 产物（`XCFramework`/`AAR`）。
4. 将一个 RN 表面集成到主机应用并验证启动/运行时。
5. 通过功能/屏幕重复集成，进行渐进式发布。

## 代理约束（全局）

跨所有参考文件应用以下规则：

1. 首先选择一个路径（Expo 或裸），不要混合步骤。
2. 使用文档中的占位符（`<framework_target_name>`、`<android_module_name>`、`<registered_module_name>`），并从项目文件中解析。
3. 在进入主机集成之前验证每个打包命令。
4. 对于长平台片段和 CLI 选项详细信息，优先使用官方文档。
5. 尽可能使主机应用与直接 React Native API 隔离（外观方法）。
6. 对于启动/运行时验证，使用 `agent-device` 打开主机应用，导航到 RN 表面，捕获快照/屏幕截图，并收集设备证据。如果缺少且验证需要它，请通过环境的批准/信任路径安装，或要求用户安装或启用。

## 典型文档

- [快速入门](https://oss.callstack.com/react-native-brownfield/docs/getting-started/quick-start.md)
- [Expo 集成](https://oss.callstack.com/react-native-brownfield/docs/getting-started/expo.md)
- [iOS 集成](https://oss.callstack.com/react-native-brownfield/docs/getting-started/ios.md)
- [Android 集成](https://oss.callstack.com/react-native-brownfield/docs/getting-started/android.md)
- [Brownfield CLI](https://oss.callstack.com/react-native-brownfield/docs/cli/brownfield.md)
- [指南](https://oss.callstack.com/react-native-brownfield/docs/guides/guidelines.md)
- [故障排除](https://oss.callstack.com/react-native-brownfield/docs/guides/troubleshooting.md)

## 路径选择门（必须首先运行）

在选择任何参考文件之前，对项目进行分类：

1. 如果尚不存在 React Native 应用，请使用 Expo 创建路径：
   - [expo-create-app.md][expo-create-app] -> [expo-quick-start.md][expo-quick-start]
2. 如果存在 React Native 应用，请检查 `package.json` 和 `app.json`：
   - 如果存在 `expo` 或请求 Expo 插件工作流，则为 Expo。
   - 如果使用原生文件夹和直接 React Native CLI 工作流且没有 Expo 路径要求，则为裸 RN。
3. 如果仍不明确，请提出一个消除歧义的问题。
4. 继续使用确切的一个路径。

## 何时应用

参考此包的情况：

- 实施从纯原生应用到 React Native 或 Expo 的接受增量迁移
- 为 Expo 或裸 React Native 项目创建遗留集成流程
- 使用 `@callstack/react-native-brownfield` 执行初始设置
- 从 React Native 应用生成 iOS XCFramework 产物
- 从 React Native 应用生成和发布 Android AAR 产物
- 将生成的产物集成到主机 iOS/Android 应用

## 快速参考

| 文件 | 描述 |
|------|-------------|
| [quick-start.md][quick-start] | 共享的预检和强制路径选择门 |
| [expo-create-app.md][expo-create-app] | 在 Expo 遗留设置之前构建新的 Expo 应用 |
| [expo-quick-start.md][expo-quick-start] | Expo 插件设置和打包就绪 |
| [expo-ios-integration.md][expo-ios-integration] | Expo iOS 打包和主机启动集成 |
| [expo-android-integration.md][expo-android-integration] | Expo Android 打包、发布和主机集成 |
| [bare-quick-start.md][bare-quick-start] | 裸 React Native 基线设置 |
| [bare-ios-xcframework-generation.md][bare-ios-xcframework-generation] | 裸 iOS XCFramework 生成 |
| [bare-android-aar-generation.md][bare-android-aar-generation] | 裸 Android AAR 生成和发布 |
| [bare-ios-native-integration.md][bare-ios-native-integration] | 裸 iOS 主机集成 |
| [bare-android-native-integration.md][bare-android-native-integration] | 裸 Android 主机集成 |

## 问题 -> 技能映射

| 问题 | 从此开始 |
|---------|------------|
| 需要先决定迁移路径 | [assess-react-native-migration](../assess-react-native-migration/SKILL.md) |
| 需要决定 Expo 与裸路径 | [quick-start.md][quick-start] |
| 需要为遗留创建新的 Expo 应用 | [expo-create-app.md][expo-create-app] |
| 需要Expo遗留设置和插件连接 | [expo-quick-start.md][expo-quick-start] |
| 需要Expo iOS遗留集成 | [expo-ios-integration.md][expo-ios-integration] |
| 需要Expo Android遗留集成 | [expo-android-integration.md][expo-android-integration] |
| 需要裸 RN 基线设置 | [bare-quick-start.md][bare-quick-start] |
| 需要裸 RN iOS XCFramework 生成 | [bare-ios-xcframework-generation.md][bare-ios-xcframework-generation] |
| 需要裸 RN Android AAR 生成/发布 | [bare-android-aar-generation.md][bare-android-aar-generation] |
| 需要裸 RN iOS 主机集成 | [bare-ios-native-integration.md][bare-ios-native-integration] |
| 需要裸 RN Android 主机集成 | [bare-android-native-integration.md][bare-android-native-integration] |

## 相关技能

- 在选择迁移路径之前，先使用 [Assess React Native migration](../assess-react-native-migration/SKILL.md)。
