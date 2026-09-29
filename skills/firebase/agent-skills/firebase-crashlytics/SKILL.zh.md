---
name: firebase-crashlytics
description: Firebase Crashlytics 的全面指南，包括配置和 SDK 使用。当用户需要帮助设置 Crashlytics、添加崩溃报告或在其应用程序中使用 Crashlytics SDK 时，请使用此技能。
---

# Crashlytics

本技能为如何在 Android 或 iOS 上开始使用 Crashlytics 提供了完整指南。您可以使用 Firebase CLI 中的 MCP 服务器读取从客户端应用程序收集的崩溃数据。

## 前置条件

配置 Crashlytics 需要一个 Firebase 项目和一个 Firebase 应用（Android 或 iOS）。要读取 Crashlytics 收集的数据，请在 Firebase CLI 中安装 MCP 服务器。请参考 `firebase-basics` 技能。

## SDK 配置

要学习如何在您的应用程序代码中配置 Crashlytics，请选择您的平台：

- **Android**：[android_setup.md](references/android_setup.md)
- **iOS**：[ios_setup.md](references/ios_setup.md)

## SDK 使用

SDK 提供了多种功能，使崩溃报告更具可操作性。

- 添加自定义键
- 添加自定义日志
- 设置用户标识符
- 报告非致命异常

要学习如何自定义崩溃报告并添加额外的调试数据，请参考您的平台的文档。

- **Android**：
  [Customize Crash Reports for Android](https://firebase.google.com/docs/crashlytics/android/customize-crash-reports.md)
- **iOS**：
  [Customize Crash Reports for Apple Platforms](https://firebase.google.com/docs/crashlytics/ios/customize-crash-reports.md)
