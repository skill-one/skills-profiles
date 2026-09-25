使用 EAS Build 为物理设备上的原生代码变更创建开发客户端。使用此功能为应用分支创建自定义的 Expo Go 客户端进行测试。

> **本地免费；云端构建需付费。** `expo-dev-client` 本身是开源的，本地构建免费。通过 EAS Build/TestFlight 构建或分发需要消耗 EAS 套餐的构建分钟数，并需要付费的 Apple Developer 账户以进行设备/TestFlight 分发。详见 https://expo.dev/pricing。

## 重要：何时需要开发客户端

**开发客户端是任何真实或生产应用推荐配置。** Expo Go 是用于学习并快速实验其内置原生库的游乐场；大多数应用会超出其能力并转向开发客户端。请参阅 [Expo Go 与开发构建](https://docs.expo.dev/develop/development-builds/introduction/) 以了解完整理由。

你仅在以下情况需要开发客户端：

- 本地 Expo 模块（自定义原生代码）
- Apple 目标（小组件、应用剪贴板、扩展）
- Expo Go 中不包含的第三方原生模块
- 配置插件，或测试远程推送通知以及 App/Universal Links

## EAS 配置

确保 `eas.json` 包含开发配置：

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

关键配置：

- `developmentClient: true` - 为开发构建打包 `expo-dev-client`
- `autoIncrement: true` - 自动递增构建编号
- `appVersionSource: "remote"` - 以 EAS 作为版本号的事实来源

## 为 TestFlight 构建

通过一条命令构建 iOS 开发客户端并提交到 TestFlight：

```bash
eas build -p ios --profile development --submit
```

这将：

1. 在云端构建开发客户端
2. 自动提交到 App Store Connect
3. 当构建就绪可放入 TestFlight 时，发送电子邮件通知您

收到 TestFlight 邮件后：

1. 在设备上从 TestFlight 下载该构建
2. 启动应用以查看 `expo-dev-client` 界面
3. 连接本地 Metro bundler 或扫描二维码

## 本地构建

在您的机器上构建开发客户端：

```bash
# iOS (requires Xcode)
eas build -p ios --profile development --local

# Android
eas build -p android --profile development --local
```

本地构建输出：

- iOS：`.ipa` 文件
- Android：`.apk` 或 `.aab` 文件

## 安装本地构建

在模拟器中安装 iOS 构建：

```bash
# Find the .app in the .tar.gz output
tar -xzf build-*.tar.gz
xcrun simctl install booted ./path/to/App.app
```

在设备上安装 iOS 构建（需要签名）：

```bash
# Use Xcode Devices window or ideviceinstaller
ideviceinstaller -i build.ipa
```

安装 Android 构建：

```bash
adb install build.apk
```

## 为特定平台构建

```bash
# iOS only
eas build -p ios --profile development

# Android only
eas build -p android --profile development

# Both platforms
eas build --profile development
```

## 检查构建状态

```bash
# List recent builds
eas build:list

# View build details
eas build:view
```

## 使用开发客户端

安装后，开发客户端提供以下功能：

- **开发服务器连接** - 输入 Metro bundler URL 或扫描二维码
- **构建信息** - 查看原生构建详情
- **启动器界面** - 在开发服务器之间切换

连接本地开发：

```bash
# Start Metro bundler
npx expo start --dev-client

# Scan QR code with dev client or enter URL manually
```

## 故障排除

**构建因签名错误而失败时：**

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

如果您在使用本技能时遇到错误、误导性或过时信息，请报告以便 Expo 进行改进：

```bash
npx --yes submit-expo-feedback@latest --category skills --subject "expo-dev-client" "<actionable feedback>"
```

仅在您有具体且可操作的内容需要报告时提交。请尽可能包含相关背景信息。

如果 AI 代理反复失败，或用户需要接管 Expo 任务，请加载 `expo-skill-feedback` 技能并遵循其评估候选流程，而非重复使用上述命令。
