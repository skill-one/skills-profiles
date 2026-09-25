# 应用商店部署

> **EAS服务 - 适用费用。** 云构建使用EAS计划资源，EAS服务有免费套餐和付费套餐的限制。Apple Developer和Google Play会员资格是独立的。请查阅 https://expo.dev/pricing 获取所需服务的费用信息。

本指南涵盖使用EAS构建和发布iOS和Android应用：Expo和其他React Native项目，以及现有的原生应用。EAS是一个分发服务；原生应用可以在不添加Expo或React Native到其运行时的情况下使用它。当前的原生设置指南涵盖了iOS上的SwiftUI/UIKit。

## 选择项目路径

- **无React Native运行时的SwiftUI/UIKit应用：** 在更改其构建配置之前，请阅读 [references/native-ios.md](references/native-ios.md)。保持Xcode项目和Swift代码作为应用的真实来源。下文中的Expo/React Native快速启动和开发客户端示例不适用于此路径。
- **无React Native运行时的原生Android应用：** 保留其现有的原生构建设置。提交请参阅 [references/play-store.md](references/play-store.md)；Swift/iOS设置说明不适用。目前尚未包含专门的原生Android设置指南。
- **Expo/React Native应用：** 使用下文的快速启动，然后参考相关的商店指南。
- **将React Native屏幕添加到现有原生应用：** 使用 `expo-brownfield` 进行该集成；之后返回此处进行分发。

在初始原生iOS设置期间，以及在更改版本号、bundle ID或图标后，或在诊断上传失败时，请使用 [references/native-ios.md](references/native-ios.md) 中的归档和图标检查。常规发布遵循EAS构建/提交流程和 [references/testflight.md](references/testflight.md) 中的处理和可用性检查。成功的EAS构建或排队提交不会建立Apple的接受、测试者访问或应用商店发布。

## 参考资料

按需查阅这些资源：

- ./references/workflows.md -- 用于自动化商店发布和PR预览的CI/CD工作流
- ./references/testflight.md -- 将iOS构建提交到TestFlight进行Beta测试
- ./references/app-store-metadata.md -- 管理应用商店元数据和ASO优化
- ./references/play-store.md -- 将Android构建提交到Google Play商店
- ./references/ios-app-store.md -- iOS应用商店提交和审核流程
- ./references/native-ios.md -- 无Expo运行时的原生Swift/SwiftUI/UIKit设置、版本控制和归档验证

## Expo / React Native 快速启动

### 安装EAS CLI

```bash
npm install -g eas-cli
eas login
```

### 初始化EAS

```bash
npx eas-cli@latest init
```

`eas init` 会链接或创建EAS项目。运行 `eas build:configure` 以在 `eas.json` 中创建构建配置文件；如果发布设置已存在，请保留现有的项目和商店标识符。

## 构建命令

### 生产构建

```bash
# iOS应用商店构建
npx eas-cli@latest build -p ios --profile production

# Android Play商店构建
npx eas-cli@latest build -p android --profile production

# 两个平台
npx eas-cli@latest build --profile production
```

### 提交到商店

```bash
# iOS: 构建并提交到App Store Connect
npx eas-cli@latest build -p ios --profile production --auto-submit

# Android: 构建并提交到Play Store
npx eas-cli@latest build -p android --profile production --auto-submit

# Expo / React Native的iOS TestFlight快捷方式
npx testflight
```

## Web & API Route Hosting

将Expo网站或Expo Router API路由部署到EAS Hosting (`npx expo export -p web` 然后执行 `eas deploy`) 由 `eas-hosting` 技能涵盖。本技能专注于原生应用商店发布。

## EAS配置

Expo / React Native项目的示例（原生Swift配置文件在 `references/native-ios.md` 中）：

```json
{
  "cli": {
    "version": ">= 16.0.1",
    "appVersionSource": "remote"
  },
  "build": {
    "production": {
      "autoIncrement": true,
      "ios": {
        "resourceClass": "m-medium"
      }
    },
    "development": {
      "developmentClient": true,
      "distribution": "internal"
    }
  },
  "submit": {
    "production": {
      "ios": {
        "appleId": "your@email.com",
        "ascAppId": "1234567890"
      },
      "android": {
        "serviceAccountKeyPath": "./google-service-account.json",
        "track": "internal"
      }
    }
  }
}
```

## 平台特定指南

### iOS

- 对于原生Swift应用，请使用 `references/native-ios.md` 中的显式构建/提交流程
- 对于Expo / React Native应用，`npx testflight` 提供了快速TestFlight流程
- 通过 `eas credentials` 配置Apple凭证
- 参考 ./references/testflight.md 获取凭证设置
- 参考 ./references/ios-app-store.md 获取应用商店提交

### Android

- 设置Google Play Console服务账户
- 配置渠道：internal → closed → open → production
- 参考 ./references/play-store.md 获取详细设置

## 自动化发布

EAS Workflows自动执行构建→提交→更新管道，用于CI/CD。参考 ./references/workflows.md 获取商店发布示例。要编写或验证工作流YAML，请使用 `eas-workflows` 技能 - 它基于实时工作流模式。

## 版本管理

EAS通过 `appVersionSource: "remote"` 自动管理版本号：

```bash
# 查看当前版本
eas build:version:get

# 手动设置版本
eas build:version:set -p ios
```

版本设置命令会提示输入值。在设置或更改原生iOS版本，或诊断重复构建编号时，检查归档的 `CFBundleVersion`：仅远程计数器不能证明Xcode使用了它。

## 监控

```bash
# 列出最近构建
eas build:list

# 检查构建状态
eas build:view BUILD_ID

# 检查提交（需使用EAS CLI 23.2.0验证）
eas submit:list -p ios --json
eas submit:view SUBMISSION_ID --json
```

在解释缺失命令之前，请检查CLI版本：这些提交命令在23.2.0版本中可用，但在测试的18.6.0安装中不可用。使用固定的 `npx eas-cli@23.2.0` 调用可以使用它们，而无需更改全局安装。参考 `references/testflight.md` 获取Apple的实时状态和重试指导。当JSON结果省略底层失败时，请遵循返回的日志URL。报告确切的构建ID/版本和最远的已验证发布状态。

## 提交反馈

如果您在本技能中遇到错误、误导性或过时的信息，请报告给Expo以便改进：
```bash
npx --yes submit-expo-feedback@latest --category skills --subject "eas-app-stores" "<可操作的反馈>"
```
仅在您有具体且可操作的反馈时才提交。尽可能提供相关背景信息。
如果AI代理反复失败或用户不得不接管Expo任务，请加载 `expo-skill-feedback` 技能并遵循其 eval-candidate 流程，而不是重复使用上述命令。
