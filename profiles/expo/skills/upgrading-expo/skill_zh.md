## 参考文献

- ./references/react-19.md -- SDK +54: React 19 变更 (useContext → use, Context.Provider → Context, forwardRef 移除)
- ./references/new-architecture.md -- SDK +53: 新架构迁移指南
- ./references/react-compiler.md -- SDK +54: React 编译器设置和迁移指南
- ./references/native-tabs.md -- SDK +55: 本地标签页变更 (Icon/Label/Badge 现通过 NativeTabs.Trigger.* 访问)
- ./references/expo-av-to-audio.md -- SDK +55: 从 expo-av 迁移音频播放和录制到 expo-audio
- ./references/expo-av-to-video.md -- SDK +55: 从 expo-av 迁移视频播放到 expo-video
- ./references/react-navigation-to-expo-router.md -- SDK +56: 将 `@react-navigation/*` 导入迁移到 `expo-router` 入口 (codemod + 手动映射)

## Beta/预览版本

Beta 版本使用 `.preview` 后缀 (例如 `55.0.0-preview.2`), 发布在 `@next` 标签下。

检查最新版本是否为 Beta: https://exp.host/--/api/v2/versions (查找 `expoVersion` 中的 `-preview`)

```bash
npx expo install expo@next --fix  # 安装 Beta
```

## 分步升级流程

1. 升级 Expo 和依赖项

```bash
npx expo install expo@latest
npx expo install --fix
```

2. 运行诊断: `npx expo-doctor`

3. 清除缓存并重新安装

```bash
npx expo export -p ios --clear
rm -rf node_modules .expo
watchman watch-del-all
```

## 不兼容变更清单

- 检查发布说明中移除的 API
- 更新已移动模块的导入路径
- 审查需要预构建的本地模块变更
- 测试所有相机、音频和视频功能
- 验证导航是否仍正确工作

## 针对本地变更的预构建

**首先检查项目中是否存在 `ios/` 和 `android/` 目录。** 如果两个目录都不存在，项目使用持续本地生成 (CNG)，本地项目在构建时重新生成 — 跳过本节和“清除裸流程缓存”完全。

如果升级需要本地变更:

```bash
npx expo prebuild --clean
```

这将重新生成 `ios` 和 `android` 目录。在运行此命令前，确保项目不是裸流程应用。

## 清除裸流程缓存

这些步骤仅适用于项目中存在 `ios/` 和/或 `android/` 目录时:

- 清除 iOS 的 cocoapods 缓存: `cd ios && pod install --repo-update`
- 清除 Xcode 的派生数据: `npx expo run:ios --no-build-cache`
- 清除 Android 的 Gradle 缓存: `cd android && ./gradlew clean`

## 收尾工作

- 查看目标 SDK 版本的发布说明 https://expo.dev/changelog
- 如果使用 Expo SDK 54 或更高版本，确保已安装 react-native-worklets — 这是 react-native-reanimated 正常工作的必要条件。
- 在 SDK 54+ 中启用 React 编译器，通过在 `app.json` 中添加 `"experiments": { "reactCompiler": true }` — 它是稳定的且推荐的
- 删除 `app.json` 中的 `sdkVersion` 以让 Expo 自动管理
- 从 `package.json` 中移除隐式包: `@babel/core`, `babel-preset-expo`, `expo-constants`.
- 如果 `babel.config.js` 仅包含 'babel-preset-expo'，删除该文件
- 如果 `metro.config.js` 仅包含 expo 默认设置，删除该文件

## 已弃用包

| 旧包          | 替换方案                                          |
| ------------- | ------------------------------------------------- |
| `expo-av`     | `expo-audio` 和 `expo-video`                      |
| `expo-permissions` | 单独的权限 API                                  |
| `@expo/vector-icons` | `expo-symbols` (用于 SF Symbols)                  |
| `AsyncStorage` | `expo-sqlite/localStorage/install`                |
| `expo-app-loading` | `expo-splash-screen`                              |
| expo-linear-gradient | experimental_backgroundImage + View 中的 CSS 渐变 |

迁移已弃用包时，在移除旧包前更新所有代码使用。对于 expo-av，参考迁移指南将 Audio.Sound 转换为 useAudioPlayer，Audio.Recording 转换为 useAudioRecorder，以及 Video 组件转换为使用 useVideoPlayer 的 VideoView。

## expo.install.exclude

检查 `package.json` 是否有排除的包:

```json
{
  "expo": { "install": { "exclude": ["react-native-reanimated"] } }
}
```

排除通常是临时解决方案，升级后可能不再需要。审查每一个。

## 移除补丁

检查 `patches/` 目录中是否有过时的补丁。如果不再需要，删除它们。

## Postcss

- 在 SDK +53 中不再需要 `autoprefixer`。从依赖项中移除它，并检查 `postcss.config.js` 或 `postcss.config.mjs` 以从插件列表中移除它。
- 在 SDK +53 中使用 `postcss.config.mjs`。

## Metro

移除冗余 metro 配置选项:

- resolver.unstable_enablePackageExports 在 SDK +53 中默认启用。
- `experimentalImportSupport` 在 SDK +54 中默认启用。
- `EXPO_USE_FAST_RESOLVER=1` 在 SDK +54 中被移除。
- cjs 和 mjs 扩展在 SDK +50 中默认支持。
- Expo webpack 已弃用，迁移到 [Expo Router 和 Metro web](https://docs.expo.dev/router/migrate/from-expo-webpack/)。

## Hermes 引擎 v1

自 SDK 55 起，用户可以选择使用 Hermes 引擎 v1 以提升运行时性能。这需要设置 `expo-build-properties` 配置插件中的 `useHermesV1: true`，可能需要特定版本的 `hermes-compiler` npm 包。Hermes v1 在未来的某个 SDK 版本中将变为默认选项。

## 新架构

新架构默认启用，`app.json` 字段 `"newArchEnabled": true` 不再需要，因为它已经是默认值。自 SDK +53 起，Expo Go 仅支持新架构。
