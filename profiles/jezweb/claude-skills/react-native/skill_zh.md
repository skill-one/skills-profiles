# React Native 模式

React Native + Expo 应用的性能和架构模式。按影响程度排序的规则——先修复 CRITICAL 级别的问题，再处理 MEDIUM 级别的问题。

这是一个起点。随着你构建更多移动应用，这项技能会不断增长。

## 何时应用

- 构建 React Native 或 Expo 新应用
- 优化列表和滚动性能
- 实现动画
- 审查移动代码中的性能问题
- 设置新的 Expo 项目

## 1. 列表性能 (CRITICAL)

列表是 React Native 中首要的性能问题。卡顿的滚动会毁掉整个应用体验。

| 模式 | 问题 | 解决方案 |
|------|------|---------|
| **使用 ScrollView 处理数据** | `<ScrollView>` 一次性渲染所有项目 | 使用 `<FlatList>` 或 `<FlashList>` — 虚拟化，仅渲染可见项目 |
| **缺少 keyExtractor** | 没有 `keyExtractor` 的 FlatList → 不必要的重新渲染 | `keyExtractor={(item) => item.id}` — 每个项目一个稳定的唯一键 |
| **复杂的 renderItem** | 在 renderItem 中的昂贵组件在每次滚动时都会重新渲染 | 用 `React.memo` 包裹，提取到单独的组件中 |
| **renderItem 中的内联函数** | `renderItem={({ item }) => <Row onPress={() => nav(item.id)} />}` | 提取处理函数：`const handlePress = useCallback(...)` |
| **没有 getItemLayout** | FlatList 在滚动时测量每个项目（成本高） | 为固定高度的项目提供 `getItemLayout`：`(data, index) => ({ length: 80, offset: 80 * index, index })` |
| **FlashList** | FlatList 很好，FlashList 对大型列表更好 | `@shopify/flash-list` — 即插即用替代方案，回收架构 |
| **列表中的大图像** | 主线程解码全分辨率图像 | 使用 `expo-image` 配合占位符 + 过渡效果，指定尺寸 |

### FlatList 检查清单

每个 FlatList 都应该包含：
```tsx
<FlatList
  data={items}
  keyExtractor={(item) => item.id}
  renderItem={renderItem}           // 备忘录化组件
  getItemLayout={getItemLayout}     // 如果项目高度固定
  initialNumToRender={10}           // 挂载时不渲染 100 个项目
  maxToRenderPerBatch={10}          // 离屏渲染的批处理大小
  windowSize={5}                    // 内存中保留多少屏幕
  removeClippedSubviews={true}      // 卸载离屏项目（Android）
/>
```

## 2. 动画 (HIGH)

原生动画在 UI 线程上运行。JS 动画会阻塞 JS 线程并导致卡顿。

| 模式 | 问题 | 解决方案 |
|------|------|---------|
| **用于复杂动画的 Animated API** | `Animated` 在 JS 线程上运行，会阻塞交互 | 使用 `react-native-reanimated` — 在 UI 线程上运行 |
| **布局动画** | 项目出现/消失时没有过渡效果 | `LayoutAnimation.configureNext(LayoutAnimation.Presets.easeInEaseOut)` |
| **共享元素过渡** | 在屏幕间导航时元素瞬间移动 | `react-native-reanimated` 共享过渡或 `expo-router` 共享元素 |
| **手势 + 动画** | 拖动/滑动感觉卡顿 | `react-native-gesture-handler` + `reanimated` worklets — 所有操作都在 UI 线程上 |
| **测量布局** | `onLayout` 触发过晚，导致闪烁 | 使用 `useAnimatedStyle` 与共享值实现即时响应 |

### Reanimated 基础

```tsx
import Animated, { useSharedValue, useAnimatedStyle, withSpring } from 'react-native-reanimated';

function AnimatedBox() {
  const offset = useSharedValue(0);
  const style = useAnimatedStyle(() => ({
    transform: [{ translateX: withSpring(offset.value) }],
  }));

  return (
    <GestureDetector gesture={panGesture}>
      <Animated.View style={[styles.box, style]} />
    </GestureDetector>
  );
}
```

## 3. 导航 (HIGH)

| 模式 | 问题 | 解决方案 |
|------|------|---------|
| **Expo Router** | 文件路由（类似 Next.js）的 React Native 实现 | `app/` 目录下的 `_layout.tsx` 文件。新 Expo 项目首选。 |
| **栈上的重屏** | 每个屏幕都保留在栈中 | 对不需要持久化的屏幕使用 `unmountOnBlur: true` |
| **深度链接** | 应用对 URL 无响应 | Expo Router 自动处理。对于原生 RN：`Linking` API 配置 |
| **标签徽章更新** | 标签聚焦时徽章数量不更新 | 使用 `useIsFocused()` 或聚焦时重新获取：`useFocusEffect(useCallback(...))` |
| **导航状态持久化** | 应用在后台/杀死时丢失位置 | `onStateChange` + `initialState` 与 AsyncStorage |

### Expo Router 结构

```
app/
├── _layout.tsx          # 根布局（标签导航器）
├── index.tsx            # 首页标签
├── (tabs)/
│   ├── _layout.tsx      # 标签栏配置
│   ├── home.tsx
│   ├── search.tsx
│   └── profile.tsx
├── [id].tsx             # 动态路由
└── modal.tsx            # 模态路由
```

## 4. UI 模式 (HIGH)

| 模式 | 问题 | 解决方案 |
|------|------|---------|
| **安全区域** | 内容在凹口或主指示器下方 | `<SafeAreaView>` 或 `useSafeAreaInsets()` 来自 `react-native-safe-area-context` |
| **键盘避免** | 表单字段被键盘遮挡 | `<KeyboardAvoidingView behavior={Platform.OS === 'ios' ? 'padding' : 'height'}>` |
| **平台特定代码** | iOS 和 Android 需要不同的行为 | `Platform.select({ ios: ..., android: ... })` 或 `.ios.tsx` / `.android.tsx` 文件 |
| **状态栏** | 状态栏与内容重叠或颜色不正确 | `<StatusBar style="auto" />` 来自 `expo-status-bar` 在根布局中 |
| **触摸目标** | 按钮太小无法点击 | 最小 44x44pt。使用 `hitSlop={{ top: 10, bottom: 10, left: 10, right: 10 }}` |
| **触觉反馈** | 点击感觉死板 | `expo-haptics` — `Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light)` 在重要操作上 |

## 5. 图像和媒体 (MEDIUM)

| 模式 | 问题 | 解决方案 |
|------|------|---------|
| **图像组件** | `react-native` 的 `<Image>` 功能基础 | 使用 `expo-image` — 缓存、占位符、过渡、模糊哈希 |
| **没有尺寸的远程图像** | 图像加载时布局偏移 | 始终指定 `width` 和 `height`，或使用 `aspectRatio` |
| **大图像** | Android 内存溢出崩溃 | 服务器端调整大小或使用 `expo-image`（它处理内存） |
| **SVG** | SVG 支持不是原生的 | `react-native-svg` + `react-native-svg-transformer` 用于 SVG 导入 |
| **视频** | 视频播放 | `expo-av` 或 `expo-video`（新 API） |

## 6. 状态和数据 (MEDIUM)

| 模式 | 问题 | 解决方案 |
|------|------|---------|
| **用于复杂数据的 AsyncStorage** | 每次读取都进行 JSON 解析/序列化 | 使用 MMKV (`react-native-mmkv`) — 比 AsyncStorage 快 30 倍 |
| **全局状态** | Redux/MobX 的简单状态样板 | Zustand — 最小化，在 React Native 中表现良好 |
| **服务器状态** | 手动获取 + 加载 + 错误 + 缓存 | TanStack Query — 与 Web 相同，适用于 React Native |
| **优先离线** | 没有网络应用无法使用 | TanStack Query `persistQueryClient` + MMKV，或 WatermelonDB 用于复杂离线 |
| **深度状态更新** | 嵌套对象使用展开运算符痛苦 | Immer 通过 Zustand：`set(produce(state => { state.user.name = 'new' }))` |

## 7. Expo 工作流 (MEDIUM)

| 模式 | 何时 | 如何 |
|------|------|------|
| **开发构建** | 需要原生模块 | `npx expo run:ios` 或 `eas build --profile development` |
| **Expo Go** | 快速原型，不需要原生模块 | `npx expo start` — 扫描二维码 |
| **EAS Build** | CI/CD，应用商店构建 | `eas build --platform ios --profile production` |
| **EAS Update** | 无需应用商店审核的热修复 | `eas update --branch production --message "Fix bug"` |
| **配置插件** | 不需要 ejection 修改原生配置 | `app.config.ts` 与 `expo-build-properties` 或自定义配置插件 |
| **环境变量** | 每次构建不同配置 | `eas.json` 构建配置文件 + `expo-constants` |

### 新项目设置

```bash
npx create-expo-app my-app --template tabs
cd my-app
npx expo install expo-image react-native-reanimated react-native-gesture-handler react-native-safe-area-context
```

## 8. 测试 (LOW-MEDIUM)

| 工具 | 用于 | 设置 |
|------|------|------|
| **Jest** | 单元测试，钩子测试 | Expo 默认包含 |
| **React Native Testing Library** | 组件测试 | `@testing-library/react-native` |
| **Detox** | 在真实设备/模拟器上的 E2E 测试 | `detox` — Wix 的测试框架 |
| **Maestro** | 使用 YAML 流的 E2E 测试 | `maestro test flow.yaml` — 比 Detox 简单 |

## 常见陷阱

| 陷阱 | 解决方案 |
|------|---------|
| Metro bundler 缓存 | `npx expo start --clear` |
| Pod 安装问题（iOS） | `cd ios && pod install --repo-update` |
| Reanimated 不工作 | 必须是第一个导入：`import 'react-native-reanimated'` 在根文件中 |
| Expo SDK 升级 | 更新 SDK 版本后 `npx expo install --fix` |
| Android 构建失败 | 检查 `gradle.properties` 中的内存：`org.gradle.jvmargs=-Xmx4g` |
| iOS 模拟器缓慢 | 使用物理设备进行性能测试——模拟器不能反映真实性能 |
