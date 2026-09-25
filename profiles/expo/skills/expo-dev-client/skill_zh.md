使用 EAS Build 创建开发客户端，用于在物理设备上测试原生代码更改。使用此方法创建自定义 Expo Go 客户端，用于测试您的应用程序的分支。

> **本地免费；云构建需要付费。** `expo-dev-client` 本身是开源的，本地构建是免费的。通过 EAS Build/TestFlight 构建或分发需要使用您的 EAS 计划的构建分钟数，并且设备/TestFlight 分发需要一个付费的 Apple Developer 账户。请参阅 https://expo.dev/pricing。

## 重要提示：何时需要开发客户端

**开发客户端是任何真实或生产应用程序的推荐设置。** Expo Go 是一个用于学习和快速实验其捆绑的原生库的游乐场；大多数应用程序都会超出其范围，并迁移到开发客户端。有关完整原因，请参阅 [Expo Go 与开发构建](https://docs.expo.dev/develop/development-builds/introduction/)。

您只有在使用以下功能时才需要开发客户端：

- 本地 Expo 模块（自定义原生代码）
- Apple 目标（小部件、应用快照、扩展）
- Expo Go 中不包含的第三方原生模块
- 配置插件，或测试远程推送通知和 App/通用链接

## EAS 配置

确保 `eas.json` 具有开发配置文件：

```json
{
  "cli": {
    "version": ">= 16.0.1",
    "appVersionSource": "remote"
  },
  "build": {
    "production": {
      "autoIncrement": true
    },
    "development": {
      "autoIncrement": true,
      "developmentClient": true
    }
  },
  "submit": {
    "production": {},
    "development": {}
  }
}
```

关键设置：

- `developmentClient: true` - 为开发构建捆绑 expo-dev-client
- `autoIncrement: true` - 自动递增构建编号
- `appVersionSource: "remote"` - 使用 EAS 作为版本编号的权威来源

## 构建 TestFlight

使用一个命令构建 iOS 开发客户端并提交到 TestFlight：

```bash
eas build -p ios --profile development --submit
```

这将：

1. 在云端构建开发客户端
2. 自动提交到 App Store Connect
3. 当构建在 TestFlight 中准备好时，向您发送电子邮件

收到 TestFlight 电子邮件后：

1. 在您的设备上从 TestFlight 下载构建
2. 启动应用程序以查看 expo-dev-client UI
3. 连接到您的本地 Metro 打包器或扫描 QR 码

## 本地构建

在您的机器上构建开发客户端：

```bash
# iOS（需要 Xcode）
eas build -p ios --profile development --local

# Android
eas build -p android --profile development --local
```

本地构建输出：

- iOS: `.ipa` 文件
- Android: `.apk` 或 `.aab` 文件

## 安装本地构建

在模拟器上安装 iOS 构建：

```bash
# 在 .tar.gz 输出中找到 .app
tar -xzf build-*.tar.gz
xcrun simctl install booted ./path/to/App.app
```

在设备上安装 iOS 构建（需要签名）：

```bash
# 使用 Xcode 设备窗口或 ideviceinstaller
ideviceinstaller -i build.ipa
```

安装 Android 构建：

```bash
adb install build.apk
```

## 为特定平台构建

```bash
# 仅 iOS
eas build -p ios --profile development

# 仅 Android
eas build -p android --profile development

# 两个平台
eas build --profile development
```

## 检查构建状态

```bash
# 列出最近的构建
eas build:list

# 查看构建详细信息
eas build:view
```

## 使用开发客户端

安装后，开发客户端提供：

- **开发服务器连接** - 输入您的 Metro 打包器 URL 或扫描 QR 码
- **构建信息** - 查看原生构建详细信息
- **启动器 UI** - 在开发服务器之间切换

连接到本地开发：

```bash
# 启动 Metro 打包器
npx expo start --dev-client

# 使用开发客户端扫描 QR 码或手动输入 URL
```

## 故障排除

**构建因签名错误失败：**

```bash
eas credentials
```

**清除构建缓存：**

```bash
eas build -p ios --profile development --clear-cache
```

**检查 EAS CLI 版本：**

```bash
eas --version
eas update
```

## 提交反馈
如果您在技能中遇到错误、误导性或过时的信息，请报告它，以便 Expo 可以改进：
```bash
npx --yes submit-expo-feedback@latest --category skills --subject "expo-dev-client" "<actionable feedback>"
```
仅在您有具体且可操作的反馈时才提交。尽可能提供相关上下文。
如果 AI 代理反复失败或用户不得不接管 Expo 任务，请加载 `expo-skill-feedback` 技能并遵循其 eval-candidate 流程，而不是重复使用上面的命令。
