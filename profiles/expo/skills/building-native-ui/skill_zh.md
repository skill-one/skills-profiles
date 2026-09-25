# Expo UI 指南

对于路由、链接、堆栈、标签页、模态框、折叠面板和页眉，请使用 `expo-router` 技术。

## 参考

根据需要查阅以下资源：

```
references/
  animations.md          Reanimated：进入、退出、布局、滚动驱动、手势
  controls.md            原生 iOS：开关、滑块、分段控制器、日期时间选择器、选择器
  gradients.md           通过 experimental_backgroundImage 实现的 CSS 渐变（仅限新架构）
  icons.md               通过 expo-image 的 SF Symbols（sf: source）、名称、动画、权重
  media.md               相机、音频、视频和文件保存
  storage.md             SQLite、AsyncStorage、SecureStore
  visual-effects.md      模糊（expo-blur）和液态玻璃（expo-glass-effect）
  webgpu-three.md        使用 WebGPU 和 Three.js 的 3D 图形、游戏、GPU 可视化
```

## 运行应用

**关键：** 在创建自定义构建之前，始终先尝试 Expo Go。

大多数 Expo 应用无需任何自定义原生代码即可在 Expo Go 中运行。在运行 `npx expo run:ios` 或 `npx expo run:android` 之前：

1. **从 Expo Go 开始**：运行 `npx expo start` 并使用 Expo Go 扫描二维码
2. **检查功能是否正常**：在 Expo Go 中彻底测试您的应用
3. **仅在需要时创建自定义构建** - 详见下文

### 当需要自定义构建时

您需要 `npx expo run:ios/android` 或 `eas build` 仅当使用：

- **本地 Expo 模块**（`modules/` 中的自定义原生代码）
- **Apple 目标**（通过 `@bacons/apple-targets` 的 Widget、App Clip、扩展）
- **未包含在 Expo Go 中的第三方原生模块**
- **无法在 `app.json` 中表达的自定义原生配置**

### 当 Expo Go 适用时

Expo Go 开箱即用地支持大量功能：

- 所有 `expo-*` 包（相机、位置、通知等）
- Expo Router 导航
- 大多数 UI 库（reanimated、手势处理等）
- 推送通知、深度链接等

**如果您不确定，请先尝试 Expo Go。** 创建自定义构建会增加复杂性、减慢迭代速度，并需要设置 Xcode/Android Studio。

## 代码风格

- 注意未闭合的字符串。确保嵌套的反引号被转义；始终正确转义引号。
- 始终在文件顶部使用导入语句。
- 始终使用连字符命名法（kebab-case）命名文件，例如 `comment-card.tsx`
- 文件名中切勿使用特殊字符
- 使用 tsconfig.json 配置路径别名，并优先使用别名而不是相对导入进行重构。

## 库偏好

- 切勿使用 React Native 中已移除的模块，如 Picker、WebView、SafeAreaView 或 AsyncStorage
- 切勿使用过时的 expo-permissions
- `expo-audio` 而不是 `expo-av`
- `expo-video` 而不是 `expo-av`
- `expo-image` 使用 `source="sf:name"` 用于 SF Symbols，而不是 `expo-symbols` 或 `@expo/vector-icons`
- `react-native-safe-area-context` 而不是 react-native SafeAreaView
- `process.env.EXPO_OS` 而不是 `Platform.OS`
- `React.use` 而不是 `React.useContext`
- `expo-image` Image 组件而不是内联元素 `img`
- `expo-glass-effect` 用于液态玻璃背景
- `Color` 来自 `expo-router` 用于原生语义颜色，而不是原始 `PlatformColor`（类型安全，自动适应亮/暗模式）
- 在 SDK 56+ 中，切勿直接从 `@react-navigation/*` 导入 — 而是使用 `expo-router/react-navigation`（涵盖 `@react-navigation/native`、`/core`、`/elements`、`/routers`）

## 响应式设计

- 始终将根组件包裹在滚动视图中以实现响应式设计
- 使用 `<ScrollView contentInsetAdjustmentBehavior="automatic" />` 而不是 `<SafeAreaView>` 以获得更智能的安全区域偏移
- `contentInsetAdjustmentBehavior="automatic"` 应应用于 FlatList 和 SectionList
- 使用 flexbox 而不是 Dimensions API
- 始终优先使用 `useWindowDimensions` 而不是 `Dimensions.get()` 来测量屏幕尺寸

## 行为

- 在 iOS 上有条件地使用 expo-haptics 以创造更愉悦的体验
- 使用具有内置触觉的视图，如 React Native 的 `<Switch />` 和 `@react-native-community/datetimepicker`
- 当路由属于堆栈时，其第一个子组件几乎总是应该是带有 `contentInsetAdjustmentBehavior="automatic"` 设置的 `ScrollView`
- 向页面添加 `ScrollView` 时，它几乎总是应该是路由组件内的第一个组件
- 在包含可复制数据的文本上使用 `<Text selectable />` 属性
- 考虑格式化大数字，如 1.4M 或 38k
- 除非在 WebView 或 Expo DOM 组件中，否则切勿使用内联元素如 'img' 或 'div'

# 样式

遵循 Apple 人类界面指南。

## 通用样式规则

- 优先使用 flex gap 而不是 margin 和 padding 样式
- 在可能的情况下优先使用 padding 而不是 margin
- 始终考虑安全区域，无论是使用堆栈页眉、标签页还是 `ScrollView/FlatList contentInsetAdjustmentBehavior="automatic"`
- 确保顶部和底部安全区域偏移都被考虑
- 除非重用样式更快，否则不要使用 StyleSheet.create 进行内联样式
- 为状态变化添加进入和退出动画
- 使用 `{ borderCurve: 'continuous' }` 用于圆角，除非创建胶囊形状
- 始终使用导航堆栈标题而不是页面上的自定义文本元素
- 当为 `ScrollView` 添加内边距时，使用 `contentContainerStyle` 的内边距和 gap 而不是 `ScrollView` 本身的内边距（减少裁剪）
- 不支持 CSS 和 Tailwind - 使用内联样式

## 颜色

使用 `expo-router` 的 `Color` API 用于原生语义颜色。它是 `PlatformColor` 的类型安全包装器，通过 `Color.ios.*` 暴露 iOS UIKit 颜色，通过 `Color.android.material.*`（静态）或 `Color.android.dynamic.*`（在 Android 12+ 上适应用户壁纸）暴露 Android Material 3 颜色。这些在设备上解析并自动适应亮/暗模式和辅助功能设置，因此您不再需要维护单独的亮/暗十六进制表或 `colors.web.ts` 文件。

`Color` 是平台特定的，因此请将每个值用 `Platform.select` 包裹，并提供 Web 的默认十六进制回退。将调色板集中到 `theme/colors.ts` 中，并在所有地方导入 `colors`：

```tsx
// theme/colors.ts
import { Platform } from "react-native";
import { Color } from "expo-router";

export const colors = {
  label: Platform.select({
    ios: Color.ios.label,
    android: Color.android.dynamic.onSurface,
    default: "#000000",
  })!,
  secondaryLabel: Platform.select({
    ios: Color.ios.secondaryLabel,
    android: Color.android.dynamic.onSurfaceVariant,
    default: "#3c3c43",
  })!,
  separator: Platform.select({
    ios: Color.ios.separator,
    android: Color.android.dynamic.outlineVariant,
    default: "#c6c6c8",
  })!,
  systemBackground: Platform.select({
    ios: Color.ios.systemBackground,
    android: Color.android.dynamic.surface,
    default: "#ffffff",
  })!,
  systemBlue: Platform.select({
    ios: Color.ios.systemBlue,
    android: Color.android.dynamic.primary,
    default: "#007aff",
  })!,
};
```

```tsx
import { colors } from "@/theme/colors";

<View style={{ backgroundColor: colors.systemBackground }}>
  <Text style={{ color: colors.label }}>标题</Text>
</View>;
```

- iOS 会自动重新解析这些颜色，当系统主题更改时。在 Android 上，在渲染它们的任何组件内部调用 `useColorScheme()`，以便在主题切换时重新渲染（当 React 编译器记忆组件时需要）。
- 不要将 `Color` / `PlatformColor` 值传递到 Reanimated 样式中 — 在那里使用静态颜色（见 `references/animations.md`）。
- `Platform.select({...})!` 返回 `string | OpaqueColorValue`。大多数 React Native 样式属性接受 `ColorValue`（`string | OpaqueColorValue`），所以这很好用。但有些第三方属性只接受 `string`（例如 `expo-image` 上的 `tintColor`）。需要时进行类型转换：`colors.label as string`。

## 文本样式

- 为显示重要数据或错误消息的每个 `<Text/>` 元素添加 `selectable` 属性
- 计数器应使用 `{ fontVariant: 'tabular-nums' }` 进行对齐

## 阴影

使用 CSS `boxShadow` 样式属性。切勿使用过时的 React Native 阴影或 elevation 样式。

```tsx
<View style={{ boxShadow: "0 1px 2px rgba(0, 0, 0, 0.05)" }} />
```

'inset' 阴影受支持。
