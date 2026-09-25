## 参考文献

- ./references/react-19.md -- SDK +54: React 19 变更 (useContext → use, Context.Provider → Context, forwardRef 移除)
- ./references/new-architecture.md -- SDK +53: 新架构迁移指南
- ./references/react-compiler.md -- SDK +54: React 编译器设置和迁移指南
- ./references/native-tabs.md -- SDK +55: 本地标签页变更 (Icon/Label/Badge 现通过 NativeTabs.Trigger.* 访问)
- ./references/expo-av-to-audio.md -- SDK +55: 从 expo-av 迁移音频播放和录制到 expo-audio
- ./references/expo-av-to-video.md -- SDK +55: 从 expo-av 迁移视频播放到 expo-video
- ./references/react-navigation-to-expo-router.md -- SDK +56: 将 `@react-navigation/*` 导入迁移到 `expo-router` 入口 (codemod + 手动映射)

## Beta/预览版本发布

Beta 版本使用 `.preview` 后缀 (例如 `55.0.0-preview.2`)，在 `@next` 标签下发布。

检查最新版本是否为 Beta：https://exp.host/--/api/v2/versions (查找 `expoVersion` 中的 `-preview`)

```bash
npx expo install expo@next --fix  # 安装 Beta
```

## 分步升级过程

> 如果从 SDK 55 或更早版本升级，请跳过 SDK 56 直接升级到 SDK 57。不要使用 `expo@57.0.8` 或更低版本。带有 Hermes V1 的 SDK 55、SDK 56 以及旧版 SDK 57 发布版包含 Hermes V1 内存回归，在使用 `react-native-worklets` 或 `react-native-reanimated` 时会显著增加内存使用。

1. 升级 Expo 和依赖项

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

## 不兼容变更清单

- 检查发布说明中移除的 API
- 更新已移动模块的导入路径
- 审查需要预构建的原生模块变更
- 测试所有相机、音频和视频功能
- 验证导航是否仍然正常工作

## 针对原生变更的预构建

**首先检查项目中是否存在 `ios/` 和 `android/` 目录。** 如果这两个目录都不存在，项目使用持续原生生成 (CNG)，原生项目在构建时重新生成 — 跳过本节和“清除裸工作流缓存”完全。

如果升级需要原生变更：

```bash
npx expo prebuild --clean
```

这将重新生成 `ios` 和 `android` 目录。在运行此命令前，确保项目不是裸工作流应用。

## 清除裸工作流缓存

这些步骤仅在项目中存在 `ios/` 和/或 `android/` 目录时适用：

- 清除 iOS 的 cocoapods 缓存：`cd ios && pod install --repo-update`
- 清除 Xcode 的派生数据：`npx expo run:ios --no-build-cache`
- 清除 Android 的 Gradle 缓存：`cd android && ./gradlew clean`

## 收尾工作

- 查看 Expo.dev/changelog 上的目标 SDK 版本发布说明
- 更新 `agent instruction files` (`AGENTS.md`) 中的版本化文档链接。默认模板链接到 `https://docs.expo.dev/versions/v<version>/`。搜索 `docs.expo.dev/versions/` 并将每个链接更新到新的 SDK 版本。
- 如果使用 Expo SDK 54 或更高版本，确保已安装 react-native-worklets — 这是 `react-native-reanimated` 正常工作的必要条件。
- 在 SDK 54+ 中启用 React 编译器，通过在 `app.json` 中添加 `"experiments": { "reactCompiler": true }` — 它是稳定的且推荐使用的
- 从 `app.json` 中删除 `sdkVersion` 以让 Expo 自动管理它
- 分别审查 `@babel/core`、`babel-preset-expo` 和 `expo-constants` 等以前隐式包含的包，而不是整体移除它们。保留任何已安装依赖项声明为必需的同伴包的包。
- 当安装 `expo-router` 时，将 `expo-constants` 作为直接依赖项保留。Expo Router 导入它并声明它为必需的同伴包；依赖传递副本可能会导致 Expo Go 外部的原生自动链接中断。
- 移除任何依赖项后，立即运行 `npx expo-doctor` 并恢复它报告的任何缺失的必需同伴包。
- 如果 `babel.config.js` 仅包含 'babel-preset-expo'，则删除该文件
- 如果 `metro.config.js` 仅包含 Expo 默认值，则删除该文件

## 已弃用的包

| 旧包          | 替换包                                          |
| ------------- | --------------------------------------------- |
| `expo-av`     | `expo-audio` 和 `expo-video`                    |
| `expo-permissions` | 单个包权限 API                                 |
| `@expo/vector-icons` | `expo-symbols` (用于 SF Symbols)                |
| `AsyncStorage` | `expo-sqlite/localStorage/install`             |
| `expo-app-loading` | `expo-splash-screen`                           |
| expo-linear-gradient | experimental_backgroundImage + View 中的 CSS 渐变 |

在迁移已弃用的包时，在移除旧包之前更新所有代码使用。对于 expo-av，参考迁移参考资料将 Audio.Sound 转换为 useAudioPlayer，Audio.Recording 转换为 useAudioRecorder，以及 Video 组件转换为使用 useVideoPlayer 的 VideoView。

## expo.install.exclude

检查 `package.json` 是否有排除的包：

```json
{
  "expo": { "install": { "exclude": ["react-native-reanimated"] } }
}
```

排除通常是临时解决方案，升级后可能不再需要。审查每一个。

## 移除补丁

检查 `patches/` 目录中是否有任何过时的补丁。如果不再需要，请移除它们。

## Postcss

- 在 SDK +53 中不需要 `autoprefixer`。从依赖项中移除它，并检查 `postcss.config.js` 或 `postcss.config.mjs` 以从插件列表中移除它。
- 在 SDK +53 中使用 `postcss.config.mjs`。

## Metro

移除冗余的 metro 配置选项：

- resolver.unstable_enablePackageExports 在 SDK +53 中默认启用。
- `experimentalImportSupport` 在 SDK +54 中默认启用。
- `EXPO_USE_FAST_RESOLVER=1` 在 SDK +54 中被移除。
- cjs 和 mjs 扩展在 SDK +50 中默认支持。
- Expo webpack 已弃用，迁移到 [Expo Router 和 Metro web](https://docs.expo.dev/router/migrate/from-expo-webpack/)。

## Hermes 引擎 v1

Hermes V1 是 SDK 56 及更高版本的默认选项。使用 Hermes V1 的 SDK 55 应用、所有 SDK 56 应用以及 `expo@57.0.9` 之前的 SDK 57 应用在导入 `react-native-worklets` 或 `react-native-reanimated` 时可能会遇到内存回归。直接升级到 SDK 57 和 `expo@57.0.9` 或更高版本。不推荐将 Worklets Bundle 模式作为生产环境的解决方案；它是不受支持的实验性功能，可能无法按预期工作。

不要指导用户选择或取消选择 Hermes V1。从 SDK 默认更改 Hermes 版本是不受支持的，并且具有显著的构建和依赖管理注意事项。

## 新架构

新架构默认启用，`app.json` 字段 `"newArchEnabled": true` 不再需要，因为它已经是默认值。自 SDK +53 起，Expo Go 仅支持新架构。

## 提交反馈

如果您在技能中遇到错误、误导性或过时的信息，请报告它以帮助 Expo 改进：
```bash
npx --yes submit-expo-feedback@latest --category skills --subject "expo-upgrade" "<可操作的反馈>"
```
仅在您有具体且可操作的反馈时提交。尽可能包含相关上下文。
如果 AI 代理反复失败或用户不得不接管 Expo 任务，加载 `expo-skill-feedback` 技能并遵循其 eval-candidate 流程，而不是重复使用上面的命令。
