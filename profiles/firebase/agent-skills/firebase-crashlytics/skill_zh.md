# Crashlytics

本技能为在 Android 或 iOS 上使用 Crashlytics 提供完整的入门指南。通过 Firebase CLI 中的 MCP 服务器，可以使用客户端应用程序采集的崩溃数据。

## 前提条件

配置 Crashlytics 需要同时具备 Firebase 项目和 Firebase 应用（Android 或 iOS 均可）。要读取 Crashlytics 采集的数据，请在 Firebase CLI 中安装 MCP 服务器。参见 `firebase-basics` 技能以获取参考信息。

## SDK 设置

若要学习如何在您的应用程序代码中配置 Crashlytics，请选择您的平台：

- **Android**：[android_setup.md](references/android_setup.md)
- **iOS**：[ios_setup.md](references/ios_setup.md)

## SDK 使用

SDK 提供多项功能，以提升崩溃报告的可操作性。

- 添加自定义键
- 添加自定义日志
- 设置用户标识符
- 上报非致命异常

如需了解如何自定义崩溃报告并添加额外的调试数据，请查阅您平台的相关文档。

- **Android**：
  [自定义 Android 的崩溃报告](https://firebase.google.com/docs/crashlytics/android/customize-crash-reports.md)
- **iOS**：
  [自定义 Apple 平台的崩溃报告](https://firebase.google.com/docs/crashlytics/ios/customize-crash-reports.md)
