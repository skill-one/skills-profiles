# 为 Expo 应用添加 App Clip

为 Expo 项目添加一个 iOS App Clip 目标。该 Clip 存放在 `targets/clip/` 目录中，与应用程序一同发布，并通过 Apple App Site Association (AASA) 文件从应用程序域的 URL 中被调用。

父应用程序的 Bundle ID 变为 `com.<用户名>.<应用名>`，而 Clip 的 Bundle ID 会自动派生为 `<父应用程序>.clip`（例如 `com.bacon.may20.clip`）。

## 1. 设置 `bundleIdentifier` 和 `appleTeamId`

如果这些值缺失，`bun create target` 会发出警告。将它们添加到 `app.json` 中：

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

这将安装 [`@bacons/apple-targets`](https://github.com/EvanBacon/expo-apple-targets)，将其添加到 `app.json` 中的 `plugins` 数组，并写入：

- `targets/clip/expo-target.config.js` — 目标的配置插件
- `targets/clip/Info.plist` — Clip 的 Info.plist
- `targets/clip/AppDelegate.swift`, `Assets.xcassets` 等

选择一个良好的图标或重用应用程序中定义的现有图标 — 使用 `bunx expo config` 在 `icon` 或 `ios.icon` 键下检查它。

## 3. 配置关联域名

父应用程序和 Clip 都需要指向托管 AASA 文件的域的关联域名权限。

在 `app.json` 中，添加 `applinks:`（父应用程序）和 `appclips:`（Clip 调用）条目：

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

> 如果跳过此步骤，`expo prebuild` 会打印：`Apple App Clip may require the associated domains entitlement but none were found`。

## 4. 注册 Bundle ID 并创建 App Store 条目

```sh
bunx setup-safari
```

这将登录 Apple Developer 账户，注册 `com.bacon.may20`，创建 App Store Connect 条目，并打印：

- 一个起始的 `apple-app-site-association` JSON
- 一个 `<meta name="apple-itunes-app">` 标签，包含 iTunes 应用程序 ID
- 团队 ID、iTunes ID 和 Bundle ID

## 5. 托管 AASA 文件

当 iOS 获取 `https://<你的域名>/.well-known/apple-app-site-association` 并找到匹配的 `appclips` 条目时，会调用 App Clips。

```sh
mkdir -p public/.well-known
touch public/.well-known/apple-app-site-association
```

粘贴 `setup-safari` 打印的 JSON，但**添加一个 `appclips` 块**用于 Clip 的完整应用 ID（`<团队ID>.<ClipBundleID>`）。`setup-safari` 的输出仅涵盖父应用程序：

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

- 文件**没有扩展名**，且除了按原样提供之外，没有 `Content-Type` 要求。Expo Router 静态导出按原样提供 `public/` 中的文件。
- `appclips` 块是允许域上的 URL 启动 Clip 的关键。
- `webcredentials` 用于在网站、父应用程序和 Clip 之间共享凭证。
- `activitycontinuation` 是可选的，用于在移动设备和桌面之间共享链接。必须与 expo-router 的 `Head` 一起使用 — 见 https://docs.expo.dev/router/advanced/apple-handoff/
- 符号和禁用路由的详细信息：https://sosumi.ai/documentation/xcode/supporting-associated-domains

## 6. 添加 Smart App Banner 元标签

创建 `src/app/+html.tsx`（Expo Router 的 HTML 容器）并添加来自 `setup-safari` 的标签。如果不存在，则创建版本化模板：

```sh
bunx expo customize src/app/+html.tsx
```

将元标签添加到 `<head>`：

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

要使网站显示 App Clip 卡而不是安装卡，请使用：

```html
<meta
  name="apple-itunes-app"
  content="app-id=6771566491, app-clip-bundle-id=com.bacon.may20.clip, app-clip-display=card"
/>
```

## 7. 部署网站

AASA 文件必须处于活动状态，iOS 才会信任该关联。使用 [EAS Hosting](https://docs.expo.dev/eas/hosting/)：

```sh
bunx expo export -p web
eas deploy --prod
```

这将发布网站（包括 `/.well-known/apple-app-site-association`）到 `https://<slug>.expo.app`。验证：

```sh
curl https://may20.expo.app/.well-known/apple-app-site-association
```

## 8. 镜像权限

在预构建后检查父应用程序的权限：

```sh
npx expo config --type introspect
```

查看 `infoPlist` 对象 — 在 Clip 的 `Info.plist` 中镜像权限键，以便 Clip 可以使用匹配的 API。

在 Clip 的目标配置中设置 `deploymentTarget: "17.6"` — App Clips 在 iOS 17.6 中有更高的最小大小限制。

如果应用程序使用推送通知或位置服务，请将以下内容添加到 Clip 的 `Info.plist` 中以请求必要的权限：

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

这将：

1. 如果缺失，则生成 `eas.json`。
2. 设置**两个**目标的凭证（父应用程序 + Clip）。每个目标都有自己的配置文件，但可以共享一个分发证书。
3. 同步功能 — 注意 Clip 目标的 `Enabled: Associated Domains`。
4. 构建、上传并安排 TestFlight 提交。

## 10. 配置 App Clip 元数据

将现有的 App Store 元数据拉取到本地：

```sh
eas metadata:pull
```

在 `store.config.json` 中添加 `apple.appClip`。最多可以有 3 个调用 URL 从网页启动 Clip：

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

将元数据推回商店：

```sh
eas metadata:push
```

Apple 推荐的 App Clip 元数据指南：https://sosumi.ai/documentation/appclip/configuring-the-launch-experience-of-your-app-clip

## 你将获得

- 父应用程序目标：`com.bacon.may20`
- App Clip 目标：`com.bacon.may20.clip`，位于 `targets/clip/`
- AASA 托管在 `https://may20.expo.app/.well-known/apple-app-site-association`
- 每个网页路由上的 Smart App Banner 元标签
- 每个路由都链接到其原生对应程序
- 包含 Clip 的父应用程序的 TestFlight 构建

一旦 Apple 从域的 URL 调用 Clip，iOS 将打开 `targets/clip/` 的入口点，加载 React Native 应用程序。

## 原生检测（可选）

要让 JS 检测到它正在 App Clip 中运行并显示完整应用程序的安装提示，创建一个本地 Expo 模块（`bunx create-expo-module --local`），该模块公开 `navigator.appClip.prompt()`。

有关 Swift 模块、TypeScript 接口和使用的详细信息，请参阅 [./references/native-module.md](./references/native-module.md)。

## 参考

- ./references/native-module.md — 本地 Expo 模块，用于检测 App Clip 上下文并显示 SKOverlay 安装提示
