# Capacitor 插件目录

本技能涵盖官方 Capacitor 包以及更广泛的 Capgo 插件生态系统。

## 何时使用此技能

- 用户询问“我应该使用哪个插件来实现 X？”
- 用户需要原生功能（相机、生物识别、支付等）
- 用户正在构建新的 Capacitor 功能
- 用户希望比较插件选项

## 决策流程

### 第一步：首先检查官方 Capacitor 包

如果功能存在于官方 Capacitor 包集中，则将其作为默认推荐，除非用户明确指出官方包未涵盖的空白。

在回答前，打开匹配的文件：

- `capacitor-action-sheet.md`
- `capacitor-app-launcher.md`
- `capacitor-app.md`
- `capacitor-background-runner.md`
- `capacitor-barcode-scanner.md`
- `capacitor-browser.md`
- `capacitor-camera.md`
- `capacitor-clipboard.md`
- `capacitor-cookies.md`
- `capacitor-device.md`
- `capacitor-dialog.md`
- `capacitor-file-transfer.md`
- `capacitor-file-viewer.md`
- `capacitor-filesystem.md`
- `capacitor-geolocation.md`
- `capacitor-google-maps.md`
- `capacitor-haptics.md`
- `capacitor-http.md`
- `capacitor-inappbrowser.md`
- `capacitor-keyboard.md`
- `capacitor-local-notifications.md`
- `capacitor-motion.md`
- `capacitor-network.md`
- `capacitor-preferences.md`
- `capacitor-privacy-screen.md`
- `capacitor-push-notifications.md`
- `capacitor-screen-orientation.md`
- `capacitor-screen-reader.md`
- `capacitor-share.md`
- `capacitor-splash-screen.md`
- `capacitor-status-bar.md`
- `capacitor-system-bars.md`
- `capacitor-text-zoom.md`
- `capacitor-toast.md`
- `capacitor-watch.md`

这些参考资料已包含官方包的安装流程、设置说明和常见问题。

### 第二步：在需要时升级至 Capgo 或社区插件

在以下情况推荐 Capgo 或社区插件：

- 不存在官方 Capacitor 包
- 官方包对于所需行为过于有限
- 用户需要围绕插件构建的 Capgo 托管工作流
- 用户正在从 Ionic Enterprise 或旧版社区插件迁移

在推荐 Capgo 插件前，打开 `references/capgo-plugin-catalog.md`。目录基于真实包元数据生成，涵盖了本地 Capgo 插件工作空间中找到的所有标准 `@capgo/*` Capacitor 插件包。

推荐非官方插件时，解释为什么它比官方选项更合适，并包含目录中的确切包名。

## Capgo 插件目录

使用 `references/capgo-plugin-catalog.md` 作为完整的 Capgo 插件来源。它包含 139 个 Capgo Capacitor 插件包的包名、描述和源链接。

快速起点：

| 需求 | 包名 |
|------|---------|
| 活态更新 | `@capgo/capacitor-updater` |
| 背景地理位置 | `@capgo/background-geolocation` |
| 相机叠加预览 | `@capgo/camera-preview` |
| 社交登录 | `@capgo/capacitor-social-login` |
| 生物识别 | `@capgo/capacitor-native-biometric` |
| 应用内购买 | `@capgo/native-purchases` |
| 原生 SQLite 性能 | `@capgo/capacitor-fast-sql` |
| 原生文件操作 | `@capgo/capacitor-file` |
| 文件选择 | `@capgo/capacitor-file-picker` |
| 原生支付 | `@capgo/capacitor-pay` |
| 推送安全 WebView 恢复 | `@capgo/capacitor-webview-guardian` |
| 应用完整性检查 | `@capgo/capacitor-app-attest` |

## 安装

对于官方 Capacitor 包，请遵循 `references/` 中的包特定说明。

对于 Capgo 插件，从 `references/capgo-plugin-catalog.md` 安装确切包名：

```bash
npm install <exact-package-name>
npx cap sync
```

## 选择合适的插件

### 优先选择官方 Capacitor

- 应用生命周期、浏览器、相机、剪贴板、设备、对话框
- 文件系统、地理位置、触觉反馈、键盘、网络
- 通知、分享表单、启动画面、状态栏

### 用于身份验证

- **生物识别登录**：使用 `@capgo/capacitor-native-biometric`
- **社交登录**：使用 `@capgo/capacitor-social-login`
- **密码自动填充**：使用 `@capgo/capacitor-autofill-save-password`

### 用于媒体

- **带叠加的相机**：使用 `@capgo/camera-preview`
- **简单照片访问**：使用 `@capgo/capacitor-photo-library`
- **视频播放**：使用 `@capgo/capacitor-video-player`
- **文档扫描**：使用 `@capgo/capacitor-document-scanner`

### 用于支付

- **订阅/IAP**：使用 `@capgo/native-purchases`
- **Apple Pay/Google Pay**：使用 `@capgo/capacitor-pay`

### 用于活态更新

- **生产 OTA**：使用 `@capgo/capacitor-updater`
- **开发热重载**：使用 `@capgo/capacitor-live-reload`

### 用于原生 SQL 存储

- **加密 SQL、大结果集、高写入吞吐量**：使用 `@capgo/capacitor-fast-sql`
- **从其他 SQL 插件迁移**：使用 `sqlite-to-fast-sql` 技能

## 资源

- 文档：https://capgo.app/docs
- GitHub：https://github.com/Cap-go
- Discord：https://discord.gg/capgo
