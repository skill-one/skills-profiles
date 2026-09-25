# Expo Native UI 指南

对于路由、链接、堆栈、标签页、模态框、弹出层和页眉，请使用 `expo-router` 技能。对于任何动画效果——进入/退出、手势、弹簧、键盘驱动 UI——请使用 `expo-animation` 技能。

> **在选择任何 UI 组件之前，请先检查 `expo-ui`。** `@expo/ui` 提供原生等价物——BottomSheet、Button、Picker、Slider、Menu、Section、Switch、SegmentedControl 等——在 iOS 上渲染为真实的 SwiftUI，在 Android 上渲染为 Jetpack Compose，在 Expo Go 中（SDK 56+）无需自定义构建即可使用。在使用 **`expo-ui`** 技能加载正确的组件之前，请勿退回到 React Native 内建组件或社区库。本技能（`expo-native-ui`）涵盖周围结构：Expo Router 导航、布局、样式和视觉效果。

## 参考

根据需要查阅这些资源：

```
references/
  controls.md            原生 iOS：Switch、Slider、SegmentedControl、DateTimePicker、Picker
  gradients.md           通过 experimental_backgroundImage（仅限新架构）实现 CSS 渐变
  icons.md               SF Symbols 通过 expo-symbols SymbolView：名称、权重、动画；Android 上的 Material 图标
  media.md               相机、音频、视频和文件保存
  storage.md             SQLite、AsyncStorage、SecureStore
  visual-effects.md      模糊（expo-blur）和液态玻璃（expo-glass-effect）
  webgpu-three.md        使用 WebGPU 和 Three.js 进行 3D 图形、游戏、GPU 可视化
```

## 运行应用

**关键：** 在创建自定义构建之前，始终先尝试 Expo Go。

大多数 Expo 应用无需任何自定义原生代码即可在 Expo Go 中运行。在运行 `npx expo run:ios` 或 `npx expo run:android` 之前：

1. **从 Expo Go 开始**：运行 `npx expo start` 并使用 Expo Go 扫描二维码
2. **检查功能是否正常**：在 Expo Go 中彻底测试您的应用
3. **仅在需要时创建自定义构建**——见下文

### 当需要自定义构建时

您需要 `npx expo run:ios/android` 或 `eas build` 仅当使用：

- **本地 Expo 模块**（`modules/` 中的自定义原生代码）
- **Apple 目标**（通过 `@bacons/apple-targets` 的 Widget、App Clip、扩展）
- **未包含在 Expo Go 中的第三方原生模块**
- **无法在 `app.json` 中表达的自定义原生配置**

### 当 Expo Go 可以正常工作时

Expo Go 开箱即用地支持广泛的功能：

- 大多数 `expo-*` 包（相机、位置、传感器、sqlite 等）——但并非全部：自 SDK 53 起，Android 上的 Expo Go 不支持远程推送通知，并且某些包需要 Expo Go 未捆绑的原生功能（例如 WebGPU —— 见 `references/webgpu-three.md`）
- Expo Router 导航和深度链接
- 大多数 UI 库（reanimated、gesture handler 等）

**如果您不确定，请先尝试 Expo Go。** 创建自定义构建会增加复杂性、减慢迭代速度，并需要 Xcode/Android Studio 设置。

## 代码风格

- 注意未闭合的字符串。确保嵌套反引号被转义；始终正确转义引号。
- 始终在文件顶部使用导入语句。
- 始终使用 kebab-case 命名文件，例如 `comment-card.tsx`
- 文件名中切勿使用特殊字符
- 使用 `tsconfig.json` 配置路径别名，并优先使用别名而不是相对导入进行重构。

## 库偏好

- **对于任何弹出层、选择器、滑块、切换开关、菜单或分组表单部分：在使用 React Native 内建组件或社区库之前，请使用 `@expo/ui`（见 `expo-ui` 技能）**—— 它渲染原生 SwiftUI/Compose，并在 SDK 56+ 的 Expo Go 中工作。对于分组/设置风格的行（短、固定长度），使用 `@expo/ui` 的 `List` + `ListItem`。对于大型或未知长度的滚动列表（信息流、搜索结果、目录），使用 `FlatList` 或 `FlashList`——`@expo/ui` 的 `List` 未进行虚拟化。
- 切勿使用已从 React Native 中移除的模块，如 Picker、WebView、SafeAreaView 或 AsyncStorage
- 切勿使用 legacy expo-permissions
- `expo-audio` 而不是 `expo-av`
- `expo-video` 而不是 `expo-av`
- `expo-symbols`（`SymbolView`）用于 iOS 上的 SF Symbols，而不是 `@expo/vector-icons` —— 见 `references/icons.md`。SF Symbols 仅限 Apple：在 Android 上每个图标都需要 Material 来源（`md` 属性在 NativeTabs 触发；在 icons.md 中的屏幕选项下“Android: Material Icons”下），切勿仅使用 SF 图标
- `react-native-safe-area-context` 而不是 react-native SafeAreaView
- `process.env.EXPO_OS` 而不是 `Platform.OS`
- `React.use` 而不是 `React.useContext`
- `expo-image` Image 组件而不是内联元素 `img`
- `expo-glass-effect` 用于液态玻璃背景
- `Color` 来自 `expo-router` 用于原生语义颜色，而不是原始 `PlatformColor`（类型安全，自动适应亮/暗）
- 在 SDK 56+ 中，切勿直接从 `@react-navigation/*` 导入——改用 `expo-router/react-navigation`（涵盖 `@react-navigation/native`、`/core`、`/elements`、`/routers`）

## 响应式设计

- 将包含滚动内容的屏幕包裹在 `ScrollView` 中。根为 FlatList/FlashList 的屏幕不得添加外部 `ScrollView`（列表是滚动容器），全屏屏幕（相机、地图、画布）既不需要
- 使用 `<ScrollView contentInsetAdjustmentBehavior="automatic" />` 而不是 `<SafeAreaView>` 以获得更智能的安全区域偏移
- `contentInsetAdjustmentBehavior="automatic"` 应应用于 FlatList 和 SectionList
- 使用 flexbox 而不是 Dimensions API
- 始终优先使用 `useWindowDimensions` 而不是 `Dimensions.get()` 来测量屏幕尺寸

## 行为

- 在 iOS 上有条件地使用 expo-haptics 以创造更愉悦的体验
- 使用具有内置触觉的视图，如 React Native 的 `<Switch />` 和 `@react-native-community/datetimepicker`
- 当堆栈路由包含滚动内容时，使 `ScrollView`（或 FlatList）成为路由中的第一个组件，并设置 `contentInsetAdjustmentBehavior="automatic"`
- 在包含可复制数据的文本上使用 `<Text selectable />` 属性
- 考虑格式化大数字，如 1.4M 或 38k
- 除非在 webview 或 Expo DOM 组件中，否则切勿使用内联元素如 'img' 或 'div'
- 每个加载数据的屏幕都有四种状态（加载中、错误、空、内容）——在首次加载仍在解析时切勿显示空状态；规则位于 `expo-data-fetching` 技能中
- 在可滚动表单和搜索结果中，使用 `keyboardShouldPersistTaps="handled"`，以便控件接收第一个点击，未处理的点击可以关闭键盘。仅在未处理的点击也应保持打开时使用 `"always"`
- 表单的主要操作绝不能位于键盘下方。对于跟踪键盘实际帧的 UI，加载 `expo-animation` 技能的键盘配方（`react-native-keyboard-controller`）——切勿使用 `Keyboard.addListener` 加上定时动画
- 每个启用的控件必须执行其声明的操作：搜索过滤器结果、Save 提交编辑、设置影响行为。空的处理器和成功警报不是实现；当用户请求原型时，本地状态就足够了
- 对于异步保存，保留草稿并按 `expo-data-fetching` 处理挂起/失败状态；在保存成功之前切勿关闭表单

在调用屏幕完成之前，请走一遍其主要任务，包括一个失败和恢复的情况（在加载数据或保存数据时）。检查键盘访问和后退/关闭行为。尝试长标题、缺失的图像、无搜索结果和大型系统文本；必须保持所需操作可访问。报告您已执行的操作和无法运行的操作。

# 样式

遵循每个平台自己的设计语言：iOS 上的 Apple Human Interface Guidelines，Android 上的 Material Design 3。切勿让一个平台穿上另一个平台的制服——iOS 布局中不要 FAB 或涟漪；Android 上不要手绘的 iOS 界面（返回箭头、大标题文本、iOS 风格的 Switch）。

## 通用样式规则

- 优先使用 flex gap 而不是 margin 和 padding 样式
- 尽可能优先使用 padding 而不是 margin
- 始终考虑安全区域，可以使用堆栈标题、标签页或 `ScrollView/FlatList contentInsetAdjustmentBehavior="automatic"`
- 确保顶部和底部安全区域偏移都被考虑
- 除非重用样式更快，否则不要使用 `StyleSheet.create` 的内联样式
- 对于任何动画或动画工作，加载 `expo-animation` 技能——它拥有动画或非动画的决定、时间值和中断规则
- 使用 `{ borderCurve: 'continuous' }` 用于圆角，除非创建胶囊形状
- 始终使用导航堆栈标题，而不是页面上的自定义文本元素
- 当填充 `ScrollView` 时，使用 `contentContainerStyle` 的 padding 和 gap 而不是 `ScrollView` 本身的 padding（减少裁剪）
- CSS 和 Tailwind 不受支持——使用内联样式

## 颜色

使用 `expo-router` 的 `Color` API 用于原生语义颜色。它是一个类型安全的包装器，通过 `Color.ios.*` 暴露 iOS UIKit 颜色，通过 `Color.android.material.*`（静态）或 `Color.android.dynamic.*`（在 Android 12+ 上适应用户壁纸）暴露 Android Material 3 颜色。这些在设备上解析并自动适应亮/暗模式和可访问性设置，因此您不再需要维护单独的亮/暗十六进制表或 `colors.web.ts` 文件。

`Color` 是平台特定的，因此请将每个值包装在 `Platform.select` 中，并提供 Web 的 `default` 十六进制回退。在 `theme/colors.ts` 中集中调色板，并在所有地方导入 `colors`：

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
  secondarySystemBackground: Platform.select({
    ios: Color.ios.secondarySystemBackground,
    android: Color.android.dynamic.surfaceVariant,
    default: "#f2f2f7",
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
  <Text style={{ color: colors.label }}>Title</Text>
</View>;
```

- iOS 会自动重新解析这些颜色，当系统主题更改时。在 Android 上，在渲染它们的任何组件内部调用 `useColorScheme()`，以便在主题切换时重新渲染（当 React Compiler 内存化组件时需要）。
- 不要将 `Color` / `PlatformColor` 值传递到 Reanimated 样式中——它们是原生的颜色对象，不是字符串；在那里使用静态颜色。
- `Platform.select({...})!` 返回 `string | OpaqueColorValue`。大多数 React Native 样式属性接受 `ColorValue`（`string | OpaqueColorValue`），所以这很好用。但有些第三方属性只接受 `string`（例如 `expo-image` 上的 `tintColor`）。需要时进行转换：`colors.label as string`。

## 文本样式

- 将 `selectable` 属性添加到显示重要数据或错误消息的每个 `<Text/>` 元素
- 计数器应使用 `{ fontVariant: 'tabular-nums' }` 进行对齐

## 阴影

使用 CSS `boxShadow` 样式属性。切勿使用遗留的 React Native 阴影或 elevation 样式。

```tsx
<View style={{ boxShadow: "0 1px 2px rgba(0, 0, 0, 0.05)" }} />
```

'inset' 阴影受支持。

## 提交反馈

如果您在本技能中遇到错误、误导性或过时的信息，请报告以便 Expo 改进：
```bash
npx --yes submit-expo-feedback@latest --category skills --subject "expo-native-ui" "<actionable feedback>"
```
仅在您有具体且可操作的反馈时才提交。尽可能包含相关上下文。
如果 AI 代理反复失败或用户不得不接管 Expo 任务，加载 `expo-skill-feedback` 技能并遵循其 eval-candidate 流程，而不是重复使用上面的命令。
