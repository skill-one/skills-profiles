# Crashlytics

本技能提供了一份完整的指南，帮助您在 Android 或 iOS 上开始使用 Crashlytics。您可以使用 Firebase CLI 中的 MCP 服务器读取来自客户端应用程序的崩溃数据。

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
