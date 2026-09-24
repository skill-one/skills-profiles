# Remote Config

This skill provides a complete guide for getting started with Remote Config on
Android or iOS. Remote Config allows you to change the behavior and appearance

## 前提条件

配置 Remote Config 需要同时拥有 Firebase 项目和 Firebase 应用（Android 或 iOS 均可）。如需通过命令行管理 Remote Config 模板和条件，请使用 Firebase CLI。参见 `firebase-basics` 技能以获取项目初始化的相关参考。

## 故障排除与执行

### 处理 npx 403 禁止访问错误

如果 `npx -y firebase-tools@latest` 因注册表权限问题（403 错误）而失败：

1. **告知用户**："由于注册表错误，我无法通过 npx 获取最新的 Firebase 工具。"
1. **备选方案**：若用户确认已全局安装（使用 `npm install -g firebase-tools`），尝试直接使用本地的 `firebase` 命令。

### 处理项目上下文问题

如果命令因“未选择活跃项目”而失败：

1. **检查登录状态**：运行 `npx -y firebase-tools@latest login:list`。
1. **询问项目 ID**：如果已登录但未选择活跃项目，请向用户询问：“请提供您的 Firebase 项目 ID 以继续。”
1. **使用参数标志**：在后续所有命令后追加 `--project <PROJECT_ID>`。

## SDK 配置

如需学习如何在应用程序代码中配置 Remote Config，请选择您的平台：

- **Android**：[android_setup.md](references/android_setup.md)
- **iOS**：[ios_setup.md](references/ios_setup.md)

## 最佳实践与模板管理

请遵循以下指南，并使用相关的 CLI 工具，以确保高效、安全地使用 Remote Config。

### 获取策略

为优化应用性能与用户体验，请遵循以下推荐模式（参见
[Loading Strategies](https://firebase.google.com/docs/remote-config/loading)）：

- **为下次启动加载新值**：最有效的模式是在启动时立即激活之前获取的值，并在后台获取新值，供下次使用。这最大程度减少了用户的等待时间。
- **实时更新**：使用 SDK 的实时监听器，当服务端配置发生变化时，立即更新应用，无需刷新。

### 通过 CLI 管理模板

为通过终端管理 Remote Config 模板和版本历史，请使用以下命令：

### 通过 CLI 管理模板

为通过终端管理 Remote Config 模板和版本历史，请使用以下命令：

- **获取当前模板**：将远程模板保存为本地 JSON 文件，以便进行审计或修改。

  ```bash
  npx -y firebase-tools@latest remoteconfig:get -o remote_config.json
  ```

- **自主编辑与发现**：直接修改本地的 `remote_config.json`。确定正确的信号（例如 `device.country` 或 `percent`），并相应更新 "conditions" 数组和 "parameters" 映射表。

- **强制：用户审查与验证**：在执行部署前，请立即停止并询问用户确认您的修改。

  - 操作：告知用户：“我已准备好 `remote_config.json` 中的修改。请核对该文件的准确性。确认无误后，请告知我执行 `deploy` 以使修改生效。”

- **部署编排**：要推送更改，必须确保环境已配置为支持部署。

  - 配置映射：如果缺少 `firebase.json` 文件，请创建该文件，将本地 JSON 映射到 Remote Config 服务：

  ```json
    { "remoteconfig": { "template": "remote_config.json" } }
  ```

  - 部署：执行部分部署命令
    
    ```bash
    npx -y firebase-tools@latest deploy --only remoteconfig
    ```

- **验证**：部署后，通过列出版本历史来验证更新。

  ```bash
  npx -y firebase-tools@latest remoteconfig:versions:list
  ```

SDK 提供多项功能，使您的应用程序能够更加动态，并响应用户群体。

- **设置应用内默认值**：定义基准值，以确保应用在离线状态或首次获取数据之前能够正常运行。
- **获取并激活**：从 Firebase 后端获取值，并将其应用到本地 UI/逻辑中。
- **模板管理**：使用 Firebase CLI 对配置 JSON 文件进行版本控制、获取和部署。
