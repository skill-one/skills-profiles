# 为 Expo 应用添加 App Clip

> **要求。** 添加 App Clip 目标是开源的。发布一个需要 Apple 开发者计划会员资格和 App Store 审核，并且 AASA 文件必须在您的域名上通过 HTTPS 提供（任何 HTTPS 主机都可以；EAS Hosting 是一个选项）。通过 EAS Build 或 `bunx testflight` 构建会使用您的 EAS 计划的构建分钟数。请参阅 https://expo.dev/pricing 和 https://developer.apple.com/app-clips/。

为 Expo 项目添加一个 iOS App Clip 目标。Clip 存放在 `targets/clip/` 中，与父应用一起发布，并通过 Apple App Site Association (AASA) 文件从应用域上的 URL 调用。

父应用的 Bundle ID 变为 `com.<用户名>.<应用名>`，Clip 的 Bundle ID 会自动派生为 `<父应用>.clip`（例如 `com.bacon.may20.clip`）。

## 1. 设置 `bundleIdentifier` 和 `appleTeamId`

`bun create target` 如果这些值缺失会发出警告。添加到 `app.json`：

```json
{
  "expo": {
    "ios": {
      "bundleIdentifier": "com.<用户名>.<应用名>",
      "appleTeamId": "XX57RJ5UTD"
    }
  }
}
```

## 2. 添加 App Clip 目标

```sh
bun create target clip
```

这会安装 [`@bacons/apple-targets`](https://github.com/EvanBacon/expo-apple-targets)，将其添加到 `app.json` 中的 `plugins` 数组，并写入：

- `targets/clip/expo-target.config.js` — 目标的配置插件
- `targets/clip/Info.plist` — Clip 的 Info.plist
- `targets/clip/AppDelegate.swift`, `Assets.xcassets` 等。

选择一个良好的图标或重用应用中定义的现有图标 — 使用 `bunx expo config` 在 `icon` 或 `ios.icon` 键下检查它。

## 3. 配置关联域名

父应用和 Clip 都需要指向托管 AASA 文件的域的关联域名权限。

在 `app.json` 中，添加 `applinks:`（父应用）和 `appclips:`（Clip 调用）条目：

```json
{
  "expo": {
    "ios": {
      "associatedDomains": [
        "applinks:may20.expo.app",
        "appclips:may20.expo.app"
      ]
    }
  }
}
```

在 `targets/clip/expo-target.config.js` 中，声明 Clip 的权限：

```js
/** @type {import('@bacons/apple-targets/app.plugin').ConfigFunction} */
module.exports = (config) => ({
  type: "clip",
  icon: "https://github.com/expo.png",
  entitlements: {
    "com.apple.developer.associated-domains": ["appclips:may20.expo.app"],
  },
});
```

> 如果您跳过这一步，`expo prebuild` 会打印：`Apple App Clip may require the associated domains entitlement but none were found`。

## 4. 注册 Bundle ID 并创建 App Store 条目

```sh
bunx setup-safari
```

这会登录 Apple 开发者账户，注册 `com.bacon.may20`，创建 App Store Connect 条目，并打印：

- 一个起始的 `apple-app-site-association` JSON
- 一个 `<meta name="apple-itunes-app">` 标签，包含 iTunes 应用 ID
- 团队 ID、iTunes ID 和 Bundle ID

## 5. 托管 AASA 文件

当 iOS 获取 `https://<your-domain>/.well-known/apple-app-site-association` 并找到匹配的 `appclips` 条目时，会调用 App Clips。

```sh
mkdir -p public/.well-known
touch public/.well-known/apple-app-site-association
```

粘贴 `setup-safari` 打印的 JSON，但**添加一个 `appclips` 块**用于 Clip 的完整应用 ID（`<TeamID>.<ClipBundleID>`）。`setup-safari` 的输出仅涵盖父应用：

```json
{
  "applinks": {
    "details": [
      {
        "appIDs": ["XX57RJ5UTD.com.bacon.may20"],
        "components": [{ "/": "*", "comment": "Matches all routes" }]
      }
    ]
  },
  "appclips": {
    "apps": ["XX57RJ5UTD.com.bacon.may20.clip"]
  },
  "activitycontinuation": {
    "apps": ["XX57RJ5UTD.com.bacon.may20"]
  },
  "webcredentials": {
    "apps": ["XX57RJ5UTD.com.bacon.may20"]
  }
}
```

注意：

- 文件**没有扩展名**，且**没有 `Content-Type` 要求**，除了直接按原样提供。Expo Router 静态导出会按原样提供 `public/` 中的文件。
- `appclips` 块是允许域名上的 URL 启动 Clip 的关键。
- `webcredentials` 用于在网站、父应用和 Clip 之间共享凭证。
- `activitycontinuation` 是可选的，用于在移动设备和桌面之间共享链接。必须与 expo-router 的 `Head` 一起使用 — 见 https://docs.expo.dev/router/advanced/apple-handoff/
- 符号和禁用路由的详细信息：https://sosumi.ai/documentation/xcode/supporting-associated-domains

## 6. 添加 Smart App Banner meta 标签

创建 `src/app/+html.tsx`（Expo Router 的 HTML 容器）并添加来自 `setup-safari` 的标签。如果不存在，则创建版本化模板：

```sh
bunx expo customize src/app/+html.tsx
```

将 meta 标签添加到 `<head>`：

```tsx
import { ScrollViewStyleReset } from "expo-router/html";

export default function Root({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <head>
        <meta charSet="utf-8" />
        <meta httpEquiv="X-UA-Compatible" content="IE=edge" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <meta name="apple-itunes-app" content="app-id=6771566491" />
        <ScrollViewStyleReset />
      </head>
      <body>{children}</body>
    </html>
  );
}
```

要使网站显示 App Clip 卡而不是安装卡，使用：

```html
<meta
  name="apple-itunes-app"
  content="app-id=6771566491, app-clip-bundle-id=com.bacon.may20.clip, app-clip-display=card"
/>
```

## 7. 部署网站

AASA 文件必须在线，iOS 才会信任该关联。使用 [EAS Hosting](https://docs.expo.dev/eas/hosting/)：

```sh
bunx expo export -p web
eas deploy --prod
```

这会发布网站（包括 `/.well-known/apple-app-site-association`）在 `https://<slug>.expo.app`。验证：

```sh
curl https://may20.expo.app/.well-known/apple-app-site-association
```

## 8. 反射权限

在预构建后检查父应用的权限：

```sh
npx expo config --type introspect
```

查看 `infoPlist` 对象 — 在 Clip 的 `Info.plist` 中镜像权限键，以便 Clip 可以使用匹配的 API。

在 Clip 的目标配置中设置 `deploymentTarget: "17.6"` — App Clips 在 iOS 17.6 中有更高的最小大小限制。

如果应用使用推送通知或位置服务，添加到 Clip 的 `Info.plist` 以请求必要的权限：

```xml
<key>NSAppClip</key>
<dict>
  <key>NSAppClipRequestEphemeralUserNotification</key>
  <false/>
  <key>NSAppClipRequestLocationConfirmation</key>
  <true/>
</dict>
```

## 9. 构建并提交到 TestFlight

```sh
bunx testflight
```

这会：

1. 如果缺失，生成 `eas.json`。
2. 设置**两个**目标的凭证（父应用 + Clip）。每个目标都有自己的配置文件，但可以共享一个分发证书。
3. 同步功能 — 注意 Clip 目标的 `Enabled: Associated Domains`。
4. 构建、上传并安排 TestFlight 提交。

## 10. 配置 App Clip 元数据

将现有的 App Store 元数据拉取到本地：

```sh
eas metadata:pull
```

在 `store.config.json` 中添加 `apple.appClip`。最多 3 个调用 URL 可以从网页启动 Clip：

```json
{
  "configVersion": 0,
  "apple": {
    "appClip": {
      "defaultExperience": {
        "action": "PLAY",
        "releaseWithAppStoreVersion": true,
        "reviewDetail": {
          "invocationUrls": ["https://may20.expo.app/", null, null]
        },
        "info": {
          "en-US": {
            "subtitle": "Instantly native with Expo",
            "headerImage": "store/apple/app-clip/en-US/asc-app-clip.png"
          }
        }
      }
    }
  }
}
```

`headerImage` 必须是 1800x1200 的 PNG，且**没有透明度**。

推回商店：

```sh
eas metadata:push
```

Apple 推荐的 App Clip 元数据指南：https://sosumi.ai/documentation/appclip/configuring-the-launch-experience-of-your-app-clip

## 您将获得

- 父应用目标：`com.bacon.may20`
- App Clip 目标：`com.bacon.may20.clip`，位于 `targets/clip/`
- AASA 托管在 `https://may20.expo.app/.well-known/apple-app-site-association`
- 每个网页路由上的 Smart App Banner meta 标签
- 每个路由链接到其原生对应应用
- 包含 Clip 的父应用的 TestFlight 构建

一旦 Apple 从域名上的 URL 调用 Clip，iOS 会打开 `targets/clip/` 的入口点，加载 React Native 应用。

## 原生检测（可选）

要让 JS 检测到它正在 App Clip 中运行并显示完整应用的安装提示，创建一个本地 Expo 模块（`bunx create-expo-module --local`），该模块公开 `navigator.appClip.prompt()`。

见 [./references/native-module.md](./references/native-module.md) 获取 Swift 模块、TypeScript 接口和用法。

## 参考

- ./references/native-module.md — 本地 Expo 模块，用于检测 App Clip 上下文并显示 SKOverlay 安装提示

## 提交反馈
如果您遇到错误、误导性或过时的信息，请报告给 Expo 以改进：
```bash
npx --yes submit-expo-feedback@latest --category skills --subject "expo-app-clip" "<可操作的反馈>"
```
仅在您有具体且可操作的反馈时提交。尽可能提供相关上下文。
如果 AI 代理反复失败或用户不得不接管 Expo 任务，加载 `expo-skill-feedback` 技能并遵循其 eval-candidate 流程，而不是重复使用上述命令。
