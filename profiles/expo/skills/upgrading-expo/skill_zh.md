## 参考资料

- ./references/react-19.md -- SDK +54: React 19 变更（useContext → use, Context.Provider → Context, forwardRef 移除）
- ./references/new-architecture.md -- SDK +53: 新架构迁移指南
- ./references/react-compiler.md -- SDK +54: React Compiler 配置与迁移指南
- ./references/native-tabs.md -- SDK +55: Native tabs 变更（Icon/Label/Badge 现通过 NativeTabs.Trigger 访问.*）
- ./references/expo-av-to-audio.md -- SDK +55: 将音频播放和录制从 expo-av 迁移至 expo-audio
- ./references/expo-av-to-video.md -- SDK +55: 将视频播放从 expo-av 迁移至 expo-video
- ./references/react-navigation-to-expo-router.md -- SDK +56: 将 `@react-navigation/*` 导入迁移至 `expo-router` 入口（codemod + 手动映射）

## Beta/Preview 版本

Beta 版本使用 `.preview` 后缀（例如 `55.0.0-preview.2`），并在 `@next` 标签下发布。

检查是否为最新版本为 Beta：https://exp.host/--/api/v2/versions（在 `expoVersion` 中查找 `-preview`）

```bash
npx expo install expo@next --fix  # install beta
```

## 分步升级流程

1. 升级 Expo 及依赖

```bash
npx expo install expo@latest
npx expo install --fix
```

2. 运行诊断：`npx expo-doctor`

3. 清除缓存并重新安装

```bash
npx expo export -p ios --clear
rm -rf node_modules .expo
watchman watch-del-all
```

## 破坏性变更检查清单

- 检查发布说明中的已移除 API
- 更新已移动模块的导入路径
- 审查需要预构建的 native 模块变更
- 测试所有摄像头、音频和视频功能
- 验证导航功能是否正常

## Native 变更预构建

**首先检查项目中是否存在 `ios/` 和 `android/` 目录。** 如果这两个目录均不存在，则该项目使用连续原生生成（CNG），原生项目在构建时会重新生成——请跳过本部分以及“清除无源码工作流缓存”全部内容。

如果升级需要原生变更：

```bash
npx expo prebuild --clean
```

这将重新生成 `ios` 和 `android` 目录。在执行此命令前，请确保项目不是无源码工作流应用。

## 清除无源码工作流缓存

以下步骤仅适用于项目中存在 `ios/` 和/or `android/` 目录的情况：

- 清除 iOS 的 cocoapods 缓存：`cd ios && pod install --repo-update`
- 清除 Xcode 的派生数据：`npx expo run:ios --no-build-cache`
- 清除 Android 的 Gradle 缓存：`cd android && ./gradlew clean`

## 整理维护

- 在 https://expo.dev/changelog 查看目标 SDK 版本的发布说明
- 如果使用 Expo SDK 54 或更高版本，请确保已安装 react-native-worklets——这是 react-native-reanimated 正常运行所必需的。
- 在 SDK 54+ 中启用 React Compiler，需将 `"experiments": { "reactCompiler": true }` 添加到 app.json——该功能已稳定并推荐使用
- 从 `app.json` 中删除 `sdkVersion`，以便 Expo 自动管理
- 从 `package.json` 中移除隐式包：`@babel/core`、`babel-preset-expo`、`expo-constants`。
- 如果 `babel.config.js` 仅包含 'babel-preset-expo'，则删除该文件
- 如果 `metro.config.js` 仅包含 Expo 默认配置，则删除该文件

## 已弃用包

下表列出了旧包及其替代品：

| 旧包 | 替代品 |
| -------------------- | ---------------------------------------------------- |
| `expo-av` | `expo-audio` 和 `expo-video` |
| `expo-permissions` | 各包权限 API |
| `@expo/vector-icons` | `expo-symbols`（用于 SF Symbols） |
| `AsyncStorage` | `expo-sqlite/localStorage/install` |
| `expo-app-loading` | `expo-splash-screen` |
| expo-linear-gradient | 实验性 `backgroundImage` + View 中的 CSS 渐变 |

在迁移已弃用包时，请在移除旧包之前更新所有代码的使用方式。对于 expo-av，请参考迁移参考文档，将 Audio.Sound 转换为使用 useAudioPlayer，Audio.Recording 转换为使用 useAudioRecorder，并将 Video 组件转换为使用 VideoView 和 useVideoPlayer。

## expo.install.exclude

检查 package.json 中是否有已排除的包：

```json
{
  "expo": { "install": { "exclude": ["react-native-reanimated"] } }
}
```

排除项通常为临时变通方案，升级后可能不再需要。请逐一审查。
## 移除补丁

检查 `patches/` 目录中是否有过时的补丁。如果不再需要，请将其移除。

## Postcss

- SDK +53 中无需使用 `autoprefixer`。将其从依赖中移除，并检查 `postcss.config.js` 或 `postcss.config.mjs`，将其从插件列表中移除。
- SDK +53 中使用 `postcss.config.mjs`。

## Metro

移除冗余的 Metro 配置选项：

- SDK +53 中 `resolver.unstable_enablePackageExports` 默认为开启状态。
- SDK +54 中 `experimentalImportSupport` 默认为开启状态。
- SDK +54 中移除了 `EXPO_USE_FAST_RESOLVER=1`。
- SDK +50 中默认为 cjs 和 mjs 扩展提供支持。
- Expo webpack 已被弃用，请迁移至 [Expo Router 和 Metro web](https://docs.expo.dev/router/migrate/from-expo-webpack/)。

## Hermes 引擎 v1

自 SDK 55 起，用户可选择 opt-in 使用 Hermes 引擎 v1 以提升运行时性能。这需要在使用 `expo-build-properties` 配置插件时设置 `useHermesV1: true`，并可能需要特定版本的 `hermes-compiler` npm 包。未来在某个 SDK 版本中，Hermes v1 将变为默认配置。

## 新架构

新架构默认为启用状态，`app.json` 中的字段 `"newArchEnabled": true` 不再需要，因为默认即为启用状态。自 SDK +53 起，Expo Go 仅支持新架构。
