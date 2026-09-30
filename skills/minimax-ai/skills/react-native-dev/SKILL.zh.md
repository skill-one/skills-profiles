---
name: react-native-dev
description: 'React Native 和 Expo 开发指南，涵盖组件、样式、动画、导航、状态管理、表单、网络、性能优化、测试、原生功能以及工程（项目结构、部署、SDK 升级、CI/CD）。

  使用场景：构建 React Native 或 Expo 应用、实现动画或原生 UI、管理状态、获取数据、编写测试、优化性能、部署到 App Store/Play Store、设置 CI/CD、升级 Expo SDK 或配置 Tailwind/NativeWind。'
---

# React Native & Expo 开发指南

一份实用的指南，用于构建生产就绪的 React Native 和 Expo 应用。涵盖 UI、动画、状态管理、测试、性能和部署。

## 参考资料

根据需要查阅以下资源：

- [参考资料/导航.md](references/navigation.md) — Expo Router：栈、标签页、原生标签 (`headerLargeTitle`, `headerBackButtonDisplayMode`)、链接、模态框、抽屉、上下文菜单
- [参考资料/组件.md](references/components.md) — FlashList 模式、`expo-image`、安全区域 (`contentInsetAdjustmentBehavior`)、原生控件、模糊/玻璃效果、存储
- [参考资料/样式.md](references/styling.md) — StyleSheet、NativeWind/Tailwind、平台样式、主题、暗黑模式
- [参考资料/动画.md](references/animations.md) — Reanimated 3：进入/退出、共享值、手势、滚动驱动
- [参考资料/状态管理.md](references/state-management.md) — Zustand (选择器、持久化)、Jotai (原子、派生)、React Query、上下文
- [参考资料/表单.md](references/forms.md) — React Hook Form + Zod：验证、多步骤、动态数组
- [参考资料/网络.md](references/networking.md) — fetch 封装、React Query (乐观更新)、认证令牌、离线、API 路由、Webhooks
- [参考资料/性能.md](references/performance.md) — 性能分析工作流、FlashList + `memo`、包分析、TTI、内存泄漏、动画性能
- [参考资料/测试.md](references/testing.md) — Jest、React Native 测试库、Maestro 的端到端测试
- [参考资料/原生能力.md](references/native-capabilities.md) — 相机、位置、权限 (`use*Permissions` 钩子)、触觉反馈、通知、生物识别
- [参考资料/工程.md](references/engineering.md) — 项目布局 (`components/ui/`, `stores/`, `services/`)、路径别名、SDK 升级、EAS 构建/提交、CI/CD、DOM 组件

## 快速参考

### 组件偏好

| 目的 | 使用 | 替代 |
|------|------|------|
| 列表 | `FlashList` (`@shopify/flash-list`) + `memo` 项 | `FlatList` (无视图回收) |
| 图片 | `expo-image` | RN `<Image>` (无缓存、无 WebP) |
| 点击 | `Pressable` | `TouchableOpacity` (遗留) |
| 音频 | `expo-audio` | `expo-av` (已弃用) |
| 视频 | `expo-video` | `expo-av` (已弃用) |
| 动画 | Reanimated 3 | RN Animated API (功能有限) |
| 手势 | Gesture Handler | PanResponder (遗留) |
| 平台检查 | `process.env.EXPO_OS` | `Platform.OS` |
| 上下文 | `React.use()` | `React.useContext()` (React 18) |
| 安全区域滚动 | `contentInsetAdjustmentBehavior="automatic"` | `<SafeAreaView>` |
| SF Symbols | `expo-image` with `source="sf:name"` | `expo-symbols` |

### 扩展开发

| 情况 | 考虑 |
|------|------|
| 长列表滚动卡顿 | 虚拟化列表库 (例如 FlashList) |
| 需要 Tailwind 风格的类 | NativeWind v4 |
| 高频存储读取 | 基于同步的存储 (例如 MMKV) |
| 新项目使用 Expo | Expo Router 优于裸 React Navigation |

### 状态管理

| 状态类型 | 解决方案 |
|----------|----------|
| 本地 UI 状态 | `useState` / `useReducer` |
| 共享应用状态 | Zustand 或 Jotai |
| 服务器/异步数据 | React Query |
| 表单状态 | React Hook Form + Zod |

### 性能优先级

| 优先级 | 问题 | 解决方案 |
|--------|------|----------|
| 关键 | 长列表卡顿 | `FlashList` + memoized 项 |
| 关键 | 大包体积 | 避免 barrel imports, 启用 R8 |
| 高 | 过多重新渲染 | Zustand 选择器, React Compiler |
| 高 | 启动缓慢 | 禁用包压缩, 原生导航 |
| 中 | 动画丢失 | 仅动画 `transform`/`opacity` |

## 新项目初始化

```bash
# 1. 创建项目
npx create-expo-app@latest my-app --template blank-typescript
cd my-app

# 2. 安装 Expo Router + 核心依赖
npx expo install expo-router react-native-safe-area-context react-native-screens

# 3. (可选) 常用扩展
npx expo install expo-image react-native-reanimated react-native-gesture-handler
```

然后进行配置：

1. 在 `package.json` 中设置入口点：`"main": "expo-router/entry"`
2. 在 `app.json` 中添加 scheme：`"scheme": "my-app"`
3. 删除 `App.tsx` 和 `index.ts`
4. 创建 `app/_layout.tsx` 作为根栈布局
5. 创建 `app/(tabs)/_layout.tsx` 用于标签页导航
6. 在 `app/(tabs)/` 创建路由文件 (参见 [navigation.md](references/navigation.md))

要支持 Web，还需要安装：`npx expo install react-native-web react-dom @expo/metro-runtime`

## 核心原则

**在编写前查阅参考资料**：在实现导航、列表、网络或项目设置时，请查阅上述匹配的参考资料文件以获取模式和陷阱。

**首先尝试 Expo Go** (`npx expo start`)。自定义构建 (`eas build`) 仅在需要使用本地 Expo 模块、Apple 目标或 Expo Go 中不存在的第三方原生模块时才需要。

**条件渲染**：使用 `{count > 0 && <Text />}` 而不是 `{count && <Text />}` (渲染 "0")。

**动画规则**：仅动画 `transform` 和 `opacity` — GPU 合成，无布局重排。

**导入**：始终直接从源导入，而不是 barrel 文件 — 避免 包膨胀。

**列表和图片**：在使用 `FlatList` 或 RN `Image` 之前，请检查上述组件偏好表 — `FlashList` 和 `expo-image` 几乎总是正确的选择。

**路由文件**：始终使用连字符命名，`app/` 中不要共存组件/类型/工具。

## 检查清单

### 新项目设置
- [ ] `tsconfig.json` 路径别名配置
- [ ] 按环境设置 `EXPO_PUBLIC_API_URL` 环境变量
- [ ] 根布局包含 `GestureHandlerRootView` (如果使用手势)
- [ ] 所有滚动视图的 `contentInsetAdjustmentBehavior="automatic"`
- [ ] 列表 > 20 项使用 `FlashList` 而不是 `FlatList`

### 发布前
- [ ] 在 `--profile` 模式下分析，修复 > 16ms 的帧
- [ ] 包分析 (`source-map-explorer`)，无 barrel imports
- [ ] Android 启用 R8
- [ ] 关键路径的单元 + 组件测试
- [ ] 登录、核心功能、结账的端到端流程

---

Flutter 开发 → 参见 `flutter-dev` 技能。
iOS 原生 (UIKit/SwiftUI) → 参见 `ios-application-dev` 技能。
Android 原生 (Kotlin/Compose) → 参见 `android-native-dev` 技能。

*React Native 是 Meta Platforms, Inc. 的商标。Expo 是 650 Industries, Inc. 的商标。所有其他产品名称均为其各自所有者的商标。*
