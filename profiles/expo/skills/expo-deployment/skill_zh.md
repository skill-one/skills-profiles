# 部署

本技能涵盖使用 EAS（Expo 应用服务）在所有平台上部署 Expo 应用。

## 参考

按需查阅这些资源：

- ./references/workflows.md -- 自动化部署和 PR 预览的 CI/CD 工作流
- ./references/testflight.md -- 将 iOS 构建提交到 TestFlight 进行 Beta 测试
- ./references/app-store-metadata.md -- 管理 App Store 元数据和 ASO 优化
- ./references/play-store.md -- 将 Android 构建提交到 Google Play 商店
- ./references/ios-app-store.md -- iOS App Store 提交和审核流程

## 快速入门

### 安装 EAS CLI

```bash
npm install -g eas-cli
eas login
```

### 初始化 EAS

```bash
npx eas-cli@latest init
```

这会创建带有构建配置文件的 `eas.json`。

## 构建命令

### 生产构建

```bash
# iOS App Store 构建
npx eas-cli@latest build -p ios --profile production

# Android Play Store 构建
npx eas-cli@latest build -p android --profile production

# 两个平台
npx eas-cli@latest build --profile production
```

### 提交到商店

```bash
# iOS: 构建 并 提交到 App Store Connect
npx eas-cli@latest build -p ios --profile production --submit

# Android: 构建 并 提交到 Play Store
npx eas-cli@latest build -p android --profile production --submit

# iOS TestFlight 的快捷方式
npx testflight
```

## Web 部署

使用 EAS Hosting 部署 Web 应用：

```bash
# 部署到生产环境
npx expo export -p web
npx eas-cli@latest deploy --prod

# 部署 PR 预览
npx eas-cli@latest deploy
```

Expo Router API 路由会与 Web 包一起在 EAS Hosting 上部署 — `eas deploy` 会同时发送两者。要编写或配置 API 路由本身，请使用 `expo-api-routes` 技能。

## EAS 配置

生产部署的标准 `eas.json`：

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

- 使用 `npx testflight` 进行快速 TestFlight 提交
- 通过 `eas credentials` 配置 Apple 凭证
- 参考 ./references/testflight.md 了解凭证设置
- 参考 ./references/ios-app-store.md 了解 App Store 提交

### Android

- 设置 Google Play Console 服务账户
- 配置渠道：internal → closed → open → production
- 参考 ./references/play-store.md 了解详细设置

### Web

- EAS Hosting 为 PR 提供预览 URL
- 生产部署到您的自定义域名
- 参考 ./references/workflows.md 了解 CI/CD 自动化

## 自动化部署

EAS Workflows 自动化构建 → 提交 → 更新 → 部署的 CI/CD 管道。参考 ./references/workflows.md 了解面向部署的示例。要编写或验证工作流 YAML，请使用 `expo-cicd-workflows` 技能 — 它基于实时工作流模式。

## 版本管理

EAS 使用 `appVersionSource: "remote"` 自动管理版本号：

```bash
# 查看当前版本
eas build:version:get

# 手动设置版本
eas build:version:set -p ios --build-number 42
```

## 监控

```bash
# 列出最近构建
eas build:list

# 查看构建状态
eas build:view

# 查看提交状态
eas submit:list
```
