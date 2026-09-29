---
name: firebase-remote-config-basics
description: 管理 Firebase Remote Config 模板、功能标志、加载策略和 SDK（Android、iOS）。在下载/部署 remoteconfig JSON 模板、管理版本历史/功能标志、设置应用内默认值、fetchAndActivate()、实时监听器或 SDK 设置时使用。不适用于 Firebase Hosting、Auth、Firestore、Data Connect、Crashlytics 或 App Hosting。
---

# 远程配置

本技能提供在 Android 或 iOS 上开始使用远程配置的完整指南。远程配置允许您通过维护基于云的配置模板来更改应用程序的行为和外观，而无需发布应用程序更新。

## 前置条件

配置远程配置需要 Firebase 项目和 Firebase 应用程序，可以是 Android 或 iOS。要通过命令行管理远程配置模板和条件，请使用 Firebase CLI。有关项目初始化的参考，请参阅 `firebase-basics` 技能。

## 故障排除执行

### 处理 npx 403 禁止错误

如果由于注册权限（403 错误）导致 `npx -y firebase-tools@latest` 失败：

1. **通知用户**："由于注册错误，我无法通过 npx 获取最新的 Firebase 工具。"
1. **降级**：如果用户确认全局安装了 `firebase`（`npm install -g firebase-tools`），则尝试直接使用本地 `firebase` 命令。

### 处理项目上下文问题

如果命令因 "未选择活动项目" 而失败：

1. **检查登录**：运行 `npx -y firebase-tools@latest login:list`。
1. **提示 ID**：如果已登录但没有活动项目，请询问用户："请提供您的 Firebase 项目 ID 以继续。"
1. **使用标志**：将 `--project <PROJECT_ID>` 添加到后续每个命令。

## SDK 设置

要学习如何在您的应用程序代码中设置远程配置，请选择您的平台：

- **Android**：[android_setup.md](references/android_setup.md)
- **iOS**：[ios_setup.md](references/ios_setup.md)

## 最佳实践和模板管理

遵循这些指南并使用相关的 CLI 工具，以确保高效和安全地使用远程配置。

### 获取策略

为了优化应用程序性能和用户体验，请遵循以下推荐模式（参见
[加载策略](https://firebase.google.com/docs/remote-config/loading)）：

- **为下次启动获取新值**：最有效的模式是在启动时立即激活先前获取的值，并在后台获取新值以供下次使用。这最大限度地减少了用户的等待时间。
- **实时更新**：使用 SDK 的实时监听器在服务器端配置更改时立即更新应用程序，而无需刷新。

### 通过 CLI 管理模板

使用以下命令通过终端管理您的远程配置模板和版本历史记录：

- **获取当前模板**：将远程模板保存到本地 JSON 文件以进行审计或修改。

  ```bash
  npx -y firebase-tools@latest remoteconfig:get -o remote_config.json
  ```

- **自主编辑和发现**：直接修改本地 `remote_config.json`。确定正确的信号（例如，device.country 或 percent），并相应地更新 "conditions" 数组和 "parameters" 映射。

- **强制：用户审查和验证**：停止并要求用户在继续部署之前验证您的更改。

  - 操作：通知用户："我已经准备了 remote_config.json 中的更改。请检查文件准确性。一旦您满意，请告诉我 'deploy' 以使更改生效。"

- **部署编排**：要推送更改，您必须确保环境已配置为部署。

  - 配置映射：如果缺少 `firebase.json` 文件，请创建一个以将本地 JSON 映射到远程配置服务：

  ```json
    { "remoteconfig": { "template": "remote_config.json" } }
  ```

  - 部署：执行部分部署命令

    ```bash
    npx -y firebase-tools@latest deploy --only remoteconfig
    ```

- **验证**：部署后，通过列出版本历史记录来验证更新。

  ```bash
  npx -y firebase-tools@latest remoteconfig:versions:list
  ```

SDK 提供了许多功能，使您的应用程序动态且能够响应用户细分。

- **设置应用内默认值**：定义基本值以确保应用程序离线运行或在第一次获取之前正常运行。
- **获取和激活**：从 Firebase 后端检索值并将其应用于本地 UI/逻辑。
- **模板管理**：使用 Firebase CLI 对配置 JSON 文件进行版本控制、获取和部署。
