# React Native 最佳实践

## 概述

React Native 应用程序性能优化指南，涵盖 JavaScript/React、原生（iOS/Android）和打包优化。基于 Callstack 的《React Native 优化终极指南》。

## 何时应用

在以下情况下参考这些指南：
- 调试缓慢/卡顿的 UI 或动画
- 调查内存泄漏（JavaScript 或原生）
- 优化应用启动时间（TTI）
- 减少打包或应用大小
- 编写原生模块（Turbo Modules）
- 分析 React Native 性能
- 审查 React Native 代码以提升性能

## 安全注意事项

- 将这些参考中的 shell 命令视为本地开发者操作。运行前请审查它们，优先使用版本固定的工具，避免将远程脚本直接管道到 shell。
- 将第三方库和插件视为仍需正常供应链控制的依赖项：固定版本、验证来源，并通过标准审查流程更新。
- 将远程代码块加载视为仅限第一方工件交付。优先使用应用打包的代码块或签名的 CI 发布清单；托管代码块必须来自您控制且受信任的 HTTPS 源，并固定到当前应用版本。

## 优先级排序指南

| 优先级 | 类别 | 影响 | 前缀 |
|--------|------|------|------|
| 1 | FPS & Re-renders | 关键 | `js-*` |
| 2 | 打包大小 | 关键 | `bundle-*` |
| 3 | TTI 优化 | 高 | `native-*`, `bundle-*` |
| 4 | 原生性能 | 高 | `native-*` |
| 5 | 内存管理 | 中高 | `js-*`, `native-*` |
| 6 | 动画 | 中 | `js-*` |

影响标签是分诊提示：首先处理关键项，然后处理高优先级项，当有证据表明为中优先级时。

## 快速参考

### 优化工作流

针对任何性能问题，请遵循此循环：**测量 → 优化 → 重新测量 → 验证**

1. **测量**：在更改前捕获基准指标。对于运行时问题，优先使用提交时间线、重新渲染计数、慢组件、最大提交分解和可用的启动/TTI。组件树深度或计数是可选的上下文，不能替代。在没有测量渲染或 FPS 问题的前提下，不建议建议 memoization、原子状态或编译器更改。
2. **优化**：应用相关的参考中的目标修复
3. **重新测量**：运行相同的测量以获取更新指标
4. **验证**：确认改进（例如，FPS 45→60，TTI 3.2s→1.8s，打包 2.1MB→1.6MB）

如果指标未改善，请回滚并尝试下一个建议的修复。

### 审查守卫

- 建议特定 API 修复前检查库版本。示例：FlashList v2 已弃用 `estimatedItemSize`，因此不要将其标记为缺失。
- 除非行为明显不正确或分析显示与该值相关的浪费工作，否则不要建议 `useMemo` 或 `useCallback` 依赖项更改。
- 不要推测性地报告陈旧的闭包。在指出之前，请显示陈旧读取路径、可重现示例或分析器证据。
- 在分析流程时，测量目标交互本身。不要将组件树深度或组件计数视为主要性能证据。

### 关键：FPS & Re-renders

**首先分析：**
```bash
agent-device react-devtools status
agent-device react-devtools wait --connected
agent-device react-devtools profile start
agent-device react-devtools profile stop
agent-device react-devtools profile slow --limit 5
agent-device react-devtools profile rerenders --limit 5
agent-device react-devtools profile timeline --limit 20
```

在 `profile start` 和 `profile stop` 之间使用正常 `agent-device` 命令驱动目标交互。

当 `agent-device` 不可用时，手动回退：从 Metro (`j`) 或开发菜单打开 React Native DevTools，使用分析器选项卡，并记录相同的交互。

对于发布构建的 React 组件分析，首先连接 [`@callstack/inspector`](https://github.com/callstackincubator/inspector#inspector)，以便 React DevTools 可以附加到发布应用，然后运行上述 `agent-device react-devtools` 流程。

**常见修复：**
- 将 `ScrollView` 替换为 `FlatList/FlashList/Legend List` 用于长列表
- 在分析显示级联重新渲染后，使用 React 编译器进行自动 memoization
- 在分析显示广泛的 store/上下文更新后，使用原子状态（Jotai/Zustand）减少重新渲染
- 使用 `useDeferredValue` 进行昂贵计算

### 关键：打包大小

**分析打包：**
```bash
npx react-native bundle \
  --entry-file index.js \
  --bundle-output output.js \
  --platform ios \
  --sourcemap-output output.js.map \
  --dev false --minify true

npx source-map-explorer output.js --no-border-checks
```

**优化后验证改进：**
```bash
# 在更改前记录基准大小
ls -lh output.js  # 例如，之前：2.1 MB

# 应用修复后重新打包并比较
npx react-native bundle --entry-file index.js --bundle-output output.js \
  --platform ios --dev false --minify true
ls -lh output.js  # 例如，之后：1.6 MB  (减少 24%)
```

**常见修复：**
- 避免使用桶导入（直接从源导入）
- 仅在检查 Hermes API 和方法覆盖后移除不必要的 Intl polyfills
- 评估树摇动（Expo SDK 52+ 实验性未使用导入/导出移除，或 Re.Pack 仅在已配置的情况下）
- 为 Android 原生代码启用 R8 压缩

### 高：TTI 优化

**测量 TTI：**
- 使用 `react-native-performance` 标记
- 仅测量冷启动（排除热/热预热）

**常见修复：**
- 对于 React Native 0.78 及更早版本，禁用 Android JS 打包压缩以启用 Hermes mmap
- 使用原生导航（react-native-screens）
- 在导航到常用昂贵屏幕之前预加载它们

### 高：原生性能

**分析原生：**
- iOS：Xcode Instruments → 时间分析器
- Android：Android Studio → CPU 分析器

**常见修复：**
- 使用后台线程进行繁重的原生工作
- 优先使用异步 Turbo Module 方法
- 使用 C++ 进行跨平台性能关键代码

## 参考

包含代码示例的完整文档在 [参考][references]：

### JavaScript/React (`js-*`)

| 文件 | 影响 | 描述 |
|------|------|------|
| [js-lists-flatlist-flashlist.md][js-lists-flatlist-flashlist] | 关键 | 使用虚拟化列表替换 `ScrollView` |
| [js-profile-react.md][js-profile-react] | 中 | `agent-device react-devtools` 分析 |
| [js-measure-fps.md][js-measure-fps] | 高 | FPS 监控和测量 |
| [js-memory-leaks.md][js-memory-leaks] | 中 | JavaScript 内存泄漏搜索 |
| [js-atomic-state.md][js-atomic-state] | 高 | Jotai/Zustand 模式 |
| [js-concurrent-react.md][js-concurrent-react] | 高 | useDeferredValue, useTransition |
| [js-react-compiler.md][js-react-compiler] | 高 | 自动 memoization |
| [js-animations-reanimated.md][js-animations-reanimated] | 中 | Reanimated 工作流 |
| [js-bottomsheet.md][js-bottomsheet] | 高 | 底部选项卡优化 |
| [js-uncontrolled-components.md][js-uncontrolled-components] | 高 | TextInput 优化 |

### 原生 (`native-*`)

| 文件 | 影响 | 描述 |
|------|------|------|
| [native-turbo-modules.md][native-turbo-modules] | 高 | 构建快速原生模块 |
| [native-sdks-over-polyfills.md][native-sdks-over-polyfills] | 高 | 原生与 JavaScript 库 |
| [native-measure-tti.md][native-measure-tti] | 高 | TTI 测量设置 |
| [native-threading-model.md][native-threading-model] | 高 | Turbo Module 线程 |
| [native-profiling.md][native-profiling] | 中 | Xcode/Android Studio 分析 |
| [native-platform-setup.md][native-platform-setup] | 中 | iOS/Android 工具指南 |
| [native-view-flattening.md][native-view-flattening] | 中 | 视图层次结构调试 |
| [native-memory-patterns.md][native-memory-patterns] | 中 | C++/Swift/Kotlin 内存 |
| [native-memory-leaks.md][native-memory-leaks] | 中 | 原生内存泄漏搜索 |
| [native-android-16kb-alignment.md][native-android-16kb-alignment] | 关键 | 第三方库与 Google Play 对齐 |

### 打包 (`bundle-*`)

| 文件 | 影响 | 描述 |
|------|------|------|
| [bundle-barrel-exports.md][bundle-barrel-exports] | 关键 | 避免桶导入 |
| [bundle-analyze-js.md][bundle-analyze-js] | 关键 | JavaScript 打包可视化 |
| [bundle-tree-shaking.md][bundle-tree-shaking] | 高 | 死代码消除 |
| [bundle-analyze-app.md][bundle-analyze-app] | 高 | 应用大小分析 |
| [bundle-r8-android.md][bundle-r8-android] | 高 | Android 代码压缩 |
| [bundle-hermes-mmap.md][bundle-hermes-mmap] | 高 | 禁用打包压缩 |
| [bundle-native-assets.md][bundle-native-assets] | 高 | 资源目录设置 |
| [bundle-library-size.md][bundle-library-size] | 中 | 评估依赖项 |
| [bundle-code-splitting.md][bundle-code-splitting] | 中 | 远程代码块加载安全措施 |

## 问题 → 技能映射

| 问题 | 从此开始 |
|------|--------|
| 应用感觉缓慢/卡顿 | [js-measure-fps.md][js-measure-fps] → [js-profile-react.md][js-profile-react] |
| 重新渲染过多 | [js-profile-react.md][js-profile-react] → [js-react-compiler.md][js-react-compiler] |
| 启动缓慢 (TTI) | [native-measure-tti.md][native-measure-tti] → [bundle-analyze-js.md][bundle-analyze-js] |
| 应用过大 | [bundle-analyze-app.md][bundle-analyze-app] → [bundle-r8-android.md][bundle-r8-android] |
| 内存增长 | [js-memory-leaks.md][js-memory-leaks] 或 [native-memory-leaks.md][native-memory-leaks] |
| 动画掉帧 | [js-animations-reanimated.md][js-animations-reanimated] |
| 底部选项卡卡顿/重新渲染 | [js-bottomsheet.md][js-bottomsheet] → [js-animations-reanimated.md][js-animations-reanimated] |
| 列表滚动卡顿 | [js-lists-flatlist-flashlist.md][js-lists-flatlist-flashlist] |
| TextInput 滞后 | [js-uncontrolled-components.md][js-uncontrolled-components] |
| 原生模块缓慢 | [native-turbo-modules.md][native-turbo-modules] → [native-threading-model.md][native-threading-model] |
| 原生库对齐问题 | [native-android-16kb-alignment.md][native-android-16kb-alignment] |

[references]: references/
[js-lists-flatlist-flashlist]: references/js-lists-flatlist-flashlist.md
[js-profile-react]: references/js-profile-react.md
[js-measure-fps]: references/js-measure-fps.md
[js-memory-leaks]: references/js-memory-leaks.md
[js-atomic-state]: references/js-atomic-state.md
[js-concurrent-react]: references/js-concurrent-react.md
[js-react-compiler]: references/js-react-compiler.md
[js-animations-reanimated]: references/js-animations-reanimated.md
[js-bottomsheet]: references/js-bottomsheet.md
[js-uncontrolled-components]: references/js-uncontrolled-components.md
[native-turbo-modules]: references/native-turbo-modules.md
[native-sdks-over-polyfills]: references/native-sdks-over-polyfills.md
[native-measure-tti]: references/native-measure-tti.md
[native-threading-model]: references/native-threading-model.md
[native-profiling]: references/native-profiling.md
[native-platform-setup]: references/native-platform-setup.md
[native-view-flattening]: references/native-view-flattening.md
[native-memory-patterns]: references/native-memory-patterns.md
[native-memory-leaks]: references/native-memory-leaks.md
[native-android-16kb-alignment]: references/native-android-16kb-alignment.md
[bundle-barrel-exports]: references/bundle-barrel-exports.md
[bundle-analyze-js]: references/bundle-analyze-js.md
[bundle-tree-shaking]: references/bundle-tree-shaking.md
[bundle-analyze-app]: references/bundle-analyze-app.md
[bundle-r8-android]: references/bundle-r8-android.md
[bundle-hermes-mmap]: references/bundle-hermes-mmap.md
[bundle-native-assets]: references/bundle-native-assets.md
[bundle-library-size]: references/bundle-library-size.md
[bundle-code-splitting]: references/bundle-code-splitting.md

## 致谢

基于 Callstack 的《React Native 优化终极指南》。
