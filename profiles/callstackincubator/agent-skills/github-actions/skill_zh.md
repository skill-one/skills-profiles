# GitHub Actions 构建工件

## 概述

可重用的 GitHub Actions 模式，用于在云端构建 React Native 应用程序，并在 iOS 模拟器和 Android 模拟器上发布可通过 `gh` CLI 或 GitHub API 获取的工件。

## 何时使用

在以下情况下使用此技能：
- 创建构建 React Native 模拟器/模拟器工件的 CI 工作流。
- 从 PR 或手动触发运行中上传 iOS 模拟器和 Android 模拟器安装程序。
- 用可下载的 CI 工件替换本地仅限移动构建。
- 需要 `gh` 或 REST API 脚本检索的稳定工件 ID/名称。

## 快速参考

1. 从 [gha-ios-composite-action.md][gha-ios-composite-action] 和 [gha-android-composite-action.md][gha-android-composite-action] 添加复合动作。
2. 从 [gha-workflow-and-downloads.md][gha-workflow-and-downloads] 将其连接到 `.github/workflows/mobile-build.yml`。
3. 使用 `actions/upload-artifact@v4` 上传，并捕获 `artifact-id` 输出。
4. 使用 `gh run download` 或 `GET /repos/{owner}/{repo}/actions/artifacts/{artifact_id}/{archive_format}` 下载。

## 参考

| 文件 | 描述 |
|------|-------------|
| [gha-ios-composite-action.md][gha-ios-composite-action] | 用于 iOS 模拟器 `.app.tar.gz` 构建和工件上传的复合 `action.yml` |
| [gha-android-composite-action.md][gha-android-composite-action] | 用于 Android 模拟器 `.apk` 构建和工件上传的复合 `action.yml` |
| [gha-workflow-and-downloads.md][gha-workflow-and-downloads] | 端到端工作流连接以及 `gh` 和 REST 下载命令 |

## 问题 -> 技能映射

| 问题 | 从...开始 |
|---------|------------|
| 需要 CI iOS 模拟器 `.app.tar.gz` 工件 | [gha-ios-composite-action.md][gha-ios-composite-action] |
| 需要 CI Android 模拟器 `.apk` 工件 | [gha-android-composite-action.md][gha-android-composite-action] |
| 需要一个工作流触发两个平台任务 | [gha-workflow-and-downloads.md][gha-workflow-and-downloads] |
| 需要 `gh` 脚本下载工件 | [gha-workflow-and-downloads.md][gha-workflow-and-downloads] |

## 源灵感

- [callstackincubator/ios/action.yml](https://github.com/callstackincubator/ios/blob/main/action.yml)
- [callstackincubator/android/action.yml](https://github.com/callstackincubator/android/blob/main/action.yml)

[gha-ios-composite-action]: references/gha-ios-composite-action.md
[gha-android-composite-action]: references/gha-android-composite-action.md
[gha-workflow-and-downloads]: references/gha-workflow-and-downloads.md
