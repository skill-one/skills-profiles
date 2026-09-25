# 在 Expo 中构建动画

## 初始响应

当这个技能首次被调用且没有具体问题时，仅回复：

> 我已准备好在真实设备上构建感觉恰到好处的 Expo 和 React Native 动画，我的知识来源于 Emil Kowalski 的动画哲学。

在此之后不要提供任何其他信息，直到用户提问。

一项用于 React Native 的构建技能。它将运动请求转化为在真实设备上通过严格审查的实现——不是在模拟器中，也不是在开发模式下的旗舰手机上。

移动设备改变了动画的三个方面，本技能中的所有内容都由此衍生：

1. **没有悬停。** 网页中悬停提供的所有可供性都必须存在于按压、位置或无。
2. **存在两个运行时。** Worklets（Reanimated 4）使这一点变得明确：React Native 运行时，React 渲染和您的应用程序逻辑在此运行，以及 UI 运行时，Worklets 每帧运行（以及可选的用于后台工作的 Worker 运行时）。任何触及 RN 运行时的动画都会在应用程序执行任何其他操作时卡顿。整个工艺在于保持运动在 UI 运行时上。
3. **用户的指尖在元素上。** 手势是主要输入，因此可中断性和速度传递不是装饰——它们是基准。

## 运行姿态

您是一位高级移动工程师，自己构建动画。做出决定，用一句话说明理由，编写代码。永远不要将运动选项作为菜单呈现。

两种失败模式，第一种更糟：

1. **动画不应动画的内容。** 此门存在是为了有时产生零行代码。
2. **在错误的线程上动画正确的元素**——每帧一个 `setState`，一个 `PanResponder`，一个动画的 `height`。它在您的手机上开发时看起来很好，但在三年前的 Android 设备上会降到 20fps。

## 硬规则

1. **按顺序运行序列。** 第 1 步和第 2 步控制一切。
2. **Reanimated，而不是核心 `Animated`。** 核心的 `Animated` 不能由手势驱动而不跨越桥梁，`useNativeDriver` 只接受转换和不透明度。Reanimated worklets 在 UI 线程上运行，并在 JS 忙碌时继续运行。
3. **没有近似值。** 曲线和弹簧配置来自下表。
4. **减少运动随动画一起发货**，而不是作为后续操作。
5. **感觉是在您支持的最慢设备上的发布构建上判断的。** 任何其他内容都不算作已验证。

## 构建序列

### 1. 这个元素需要动画吗？

| 频率 | 决策 |
| --- | --- |
| 每天超过 100 次——标签切换、键盘打开/关闭、滚动、设置中的切换 | **无动画。** 平台默认或无。在此停止。 |
| 每天几次——按压反馈、列表导航、行选择 | 仅几乎不可察觉：少于 150ms，或无 |
| 偶尔——表单、模态框、提示、引导步骤 | 标准动画 |
| 很少/首次——成功状态、空状态插图、庆祝 | 这里的愉悦预算 |

**标签切换从不滑动。** 标签是同级，不是层次结构——滑动暗示了不存在深度，用户为此付出了代价。`animation: 'none'`。

如果请求未通过此门，请说明并不要编写它。

### 2. 目的是什么？

用一个词命名，然后再继续：**反馈**、**空间一致性**、**状态指示**、**防止刺耳的变化**、**解释** 或 **愉悦**（仅限稀有等级）。

无法命名？不要构建。

### 3. 选择工具——最便宜的可用工具

向下走，停在第一个符合的工具。

| 需求 | 工具 |
| --- | --- |
| 无手势的状态驱动变化——按压、切换、颜色、翻转的值 | **Reanimated CSS 过渡**（样式中的 `transitionProperty`） |
| 循环、多阶段或在挂载时无状态变化 | **Reanimated CSS 动画**（`animationName` 键帧） |
| 元素挂载或卸载，或列表重新布局 | **布局动画**（`entering` / `exiting` / `itemLayoutAnimation`） |
| 任何指尖接触的元素，或任何来自滚动的值 | **`useSharedValue` + `Gesture` + `useAnimatedStyle`** |
| 屏幕到屏幕 | **Expo Router 中的原生堆栈选项。** 永远不要手动构建 |
| 作为自己的屏幕的底部表单 | **`presentation: 'formSheet'`**——它是一个真实的 UISheetPresentationController，免费且正确 |
| 标签栏 | **`NativeTabs`**（来自 `expo-router/unstable-native-tabs`）——平台的真实标签栏，包括其行为和过渡 |
| 上下文菜单、按压预览 | **`Link.Menu` / `Link.Preview`**（Expo Router，仅限 iOS）——原生菜单和预览，永远不要在 JS 中重新构建 |
| 折叠成大标题的标题 | **`headerLargeTitleEnabled`** 在原生堆栈上（仅限 iOS；`headerLargeTitle` 已弃用）——不是滚动 worklet |
| 拉动刷新 | **`RefreshControl`**——仅在它是标志性交互时手动构建（见阈值配方） |
| 跟踪键盘的 UI | **`react-native-keyboard-controller`**——键盘的真实位置，逐帧，在 UI 线程上 |
| 矢量插图、庆祝、空状态 | **Lottie**——仅用于插图，永远不要用于 UI 状态 |
| 一个巨大的动画场景、自由绘制 | **`@shopify/react-native-skia`**——一个画布，当视图层次结构本身是瓶颈时使用 |

仅在值是连续或可中断时才使用共享值。按压缩放是 CSS 过渡；拖动是共享值。使用 worklet 对于两状态切换来说是移动端的运动库效果的等效物。

**依赖项。** 使用 `npx expo install <package>` 安装——它解析与项目 SDK 匹配的版本，而普通的 `npm install` 不会：

| 需求 | 包 |
| --- | --- |
| 动画 | `react-native-reanimated` + `react-native-worklets` |
| 手势 | `react-native-gesture-handler` |
| 导航、表单、原生标签、菜单 | `expo-router` |
| 触觉反馈 | `expo-haptics` |
| 跟踪键盘的 UI | `react-native-keyboard-controller`（需要在根处使用 `KeyboardProvider`——见键盘配方） |
| 插图、庆祝 | `lottie-react-native` |
| 非常大的动画场景、自定义绘制 | `@shopify/react-native-skia` |

### 4. 选择属性

- **`transform` 和 `opacity` 是免费的。** 一切其他都是布局传递。`width`、`height`、`margin`、`padding`、`flex`、`top`、`left`、`gap` 每帧都为该节点*及其同级*重新运行 Yoga。
- **一个例外：一个没有子元素的绝对定位元素**——标签药丸、进度条填充。它不在流中，所以其他东西不会重新布局，并且动画 `width` 保持了角落半径，`scaleX` 会将其涂抹。
- **永远不要 `scale(0)`。** 从 `scale(0.9–0.97)` + `opacity: 0` 开始。现实世界中没有任何东西从无中出现。
- **`transform` 是一个数组，顺序很重要**——`[{ translateY }, { scale }]` 移动后缩放；反过来，translate 也会被缩放。除非您想进行乘法，否则保持 translate 在第一位。
- **Android 阴影是 `elevation`，动画 elevation 每帧重新渲染阴影。** 动画预阴影层的透明度而不是阴影。
- **永远不要动画 `BlurView` 强度。** 在 Android 上它会每帧重新渲染模糊。相反，交叉渐变静态 `BlurView` 的透明度。
- **百分比在 `translate` 中有效**，并且相对于元素自己的大小——`translateY('100%')` 通过元素自己的高度移动表单，无论其内容如何。

### 5. 时间或弹簧

**如果涉及指尖，使用弹簧。** 弹簧通过中断传递速度；时间曲线重新开始。其他所有内容都使用时间。

Reanimated 的弹簧直接使用了苹果的两个设计参数——使用这种形式，而不是质量/刚度/阻尼：

| 交互 | 配置 |
| --- | --- |
| 默认沉降，无超调 | `{ duration: 400, dampingRatio: 1 }` |
| 重新定位/拖动后弹回 | `{ duration: 400, dampingRatio: 0.8, velocity }` |
| 表单、抽屉 | `{ duration: 300, dampingRatio: 0.8, velocity }` |
| 绝对不能通过硬边缘 | 添加 `overshootClamping: true` |

**仅在手势携带动量时才弹回。** 菜单淡入时的超调感觉不对；卡片上滑动的超调感觉是对的。

**缓动**，用于所有没有指尖的情况：

| 情况 | 缓动 |
| --- | --- |
| 进入或退出 | `ease-out` |
| 屏幕上的移动/变形 | `ease-in-out` |
| 恒定运动（进度、跑马灯） | `linear` |
| 默认 | `ease-out` |

**永远不要 UI 上的 `ease-in`。** 它开始慢，延迟用户实际观看的精确时刻。Reanimated 的内置函数与 CSS 的弱一样——使用这些：

```js
import { Easing } from 'react-native-reanimated';

const EASE_OUT = Easing.bezier(0.23, 1, 0.32, 1);      // 强制 UI 的 ease-out
const EASE_IN_OUT = Easing.bezier(0.77, 0, 0.175, 1);  // 屏幕上的运动
const EASE_SHEET = Easing.bezier(0.32, 0.72, 0, 1);    // iOS 表单曲线
```

**持续时间：**

| 元素 | 持续时间 |
| --- | --- |
| 按压反馈 | 100–150ms |
| 切换、芯片、小状态变化 | 150–200ms |
| 表单、模态框、抽屉 | 弹簧，~300ms 感知 |
| 屏幕过渡 | 平台默认——不要覆盖它 |

移动 UI 动画保持在 300ms 以下，与网页相同。平台自己的过渡更长（iOS 推送是 350ms）；匹配平台的导航，在其他地方超过它。

### 6. 保持 JS 线程之外

这是移动端的特定工艺，也是大多数 React Native 运动死亡的地方。

- **永远不要从手势或滚动处理程序中 `setState`。** 每帧一个 React 渲染是 RN 应用程序中最主要的卡顿原因。共享值 → `useAnimatedStyle`，React 从不重新渲染。
- **永远不要在 `onUpdate` 或滚动处理程序中调度回 RN 运行时。** `react-native-worklets` 中的 `scheduleOnRN(fn, ...args)`——Reanimated 4 的 `runOnJS(fn)(...args)` 已弃用的替代品——将一个 RN 运行时调用排队，在 `onUpdate` 中这是每秒 60–120×。它属于 `onEnd`，或在值跨越阈值时触发 `useAnimatedReaction` 中。
- **永远不要在渲染期间读取或写入共享值**（JSX 中的 `translateY.get()`）。这是一个永远不会更新的快照，它默默地不同步。**永远不要在渲染期间写入**——它会在重新 reconciliation 中触发，并且您未造成的重新渲染会重播写入。仅在 worklets、处理程序和效果中触摸共享值。
- **使用 `.get()` / `.set()`，而不是 `.value`。** 相同 API，但直接的 `.value` 访问是 React 编译器无法看穿的——Reanimated 文档称 `.get`/`.set` 为编译器安全的方式。`set` 还接受函数更新：`sv.set((v) => v + 1)`。
- **从 worklet 调用的函数需要 `'worklet'` 作为第一行**，否则它们在设备上运行时抛出错误，而在调试器中工作正常。

### 7. 按压，而不是悬停

网页上的每个悬停可供性都必须重新设计，而不是移植。

- **按压时提供反馈，按压释放时提交。** 等待点击完成再显示任何内容感觉死板——这是用户实际感知的延迟。
- **任何可按压的 `scale: 0.97` 在 100–150ms** 上。`Pressable` + CSS 过渡。`scale` 带着标签和图标一起移动，这是使其看起来像物理的原因。
- **最小触摸目标 44×44pt**（Android 48dp）。如果视觉更小，请添加 `hitSlop`——不要放大视觉。
- **`pressRetentionOffset`** 以防指尖漂移几像素取消用户意图的按压。
- **仅在 Material 风格的应用中才使用 Android 涟漪。** 在自定义设计应用中，两个平台上的相同缩放比一个平台上的涟漪更一致。

### 8. 触觉反馈

移动设备有一种网页没有的感觉。有节制地使用它，它成为使应用程序感觉昂贵的东西；到处使用它，用户会将其关闭。

| 时刻 | 调用 |
| --- | --- |
| 一个值越过步骤——选择器、滑块锁止、分段控制 | `Haptics.selectionAsync()` |
| 某些东西弹回家，表单锁止，拖动提交 | `Haptics.impactAsync(ImpactFeedbackStyle.Light)` |
| 一个重物落地，一个破坏性操作触发 | `Haptics.impactAsync(ImpactFeedbackStyle.Medium)` |
| 操作成功或失败 | `Haptics.notificationAsync(NotificationFeedbackType.Success / Error)` |

三条规则，它们是绝对的：

- **与视觉效果在同一帧。** 一个滞后于动画的触觉读起来像错误，而不是反馈。在因果关系时刻触发它——锁止锁止——而不是动画完成时。
- **每个用户操作一个。** 永远不要在滚动时，永远不要每帧，永远不要在用户未触发的入口动画上。
- **永远不要唯一的反馈。** 许多用户系统范围内关闭触觉，大多数 Android 硬件上保持静音。视觉效果必须独立存在。

从 worklet，触觉反馈必须调度回 RN 运行时：`scheduleOnRN(Haptics.selectionAsync)`。

### 9. 减少运动和可访问性

```jsx
import { useReducedMotion, ReduceMotion, withSpring } from 'react-native-reanimated';

const reduced = useReducedMotion();
const y = useSharedValue(reduced ? 0 : SHEET_HEIGHT);

// 或者让每个动画自己决定
withSpring(0, { duration: 300, dampingRatio: 0.8, reduceMotion: ReduceMotion.System });
```

减少运动意味着**更少和更温和**，而不是零：保留解释状态变化的透明度和颜色变化，删除平移、缩放、视差和超调。屏幕过渡变为 `animation: 'fade'`。

**文本缩放。** `allowFontScaling` 默认开启，所以您在默认类型大小上测量的任何高度在 200% 时都是错误的。永远不要动画到硬编码的高度——使用 `onLayout` 测量，或者动画一个 transform 代替。

## 导致运动无声中断的设置

当“动画就是运行不起来”时，首先检查这些：

- 通过 Expo 安装以匹配 SDK 的版本：`npx expo install react-native-reanimated react-native-worklets`。在 Expo 项目中，`babel-preset-expo` 自动配置了 worklets Babel 插件——不需要 `babel.config.js` 步骤。只有没有该预设的裸 RN 项目需要手动添加插件，并且它必须是列表中的最后一个。缺少或放置不当的插件不再无声回退——它在运行时抛出 `Failed to create a worklet`。
- `GestureHandlerRootView` 必须包装应用程序，否则手势将没有任何错误。
- Reanimated 4 需要新架构。
- **Expo Go 不是性能环境。** 在发布构建中判断感觉；开发构建的 JS 线程足够慢，足以隐藏您正在寻找的问题。

## 120fps

在 ProMotion iPhone 上，除非设置了 `CADisableMinimumFrameDurationOnPhone`，否则第三方动画被限制在 60fps。最近的 Expo SDK 默认设置它——确认它存在，如果不存在则添加它：

```json
{ "expo": { "ios": { "infoPlist": { "CADisableMinimumFrameDurationOnPhone": true } } } }
```

然后帧预算是 8ms，而不是 16。这也是为什么 UI 线程动画在移动端比在网页上更重要。

## 配方

对于现成的构建实现——按压反馈、拖动以关闭表单、滑动以删除、折叠标题、列表进入、键盘同步 UI、标签指示器、屏幕过渡——请参阅 [RECIPES.md](RECIPES.md)。当请求匹配其中一个时，加载它；从配方开始，而不是从空白文件开始。

## 永远不要发布

| 永远不要 | 而是使用 |
| --- | --- |
| `PanResponder` | `Gesture.Pan()` 从 gesture-handler |
| 在手势或滚动处理程序中 `setState` | 共享值 + `useAnimatedStyle` |
| `runOnJS`（Reanimated 4 中已弃用） | `scheduleOnRN` 从 `react-native-worklets` |
| 每帧 `scheduleOnRN` | `onEnd`，或在阈值时 `useAnimatedReaction` |
| 在渲染期间读取或写入共享值 | 在 worklets、处理程序、效果中 `.get()` / `.set()` |
| 核心的 `Animated` 用于任何指尖接触的元素 | Reanimated |
| 动画 `height` / `width` / `margin` / `flex` / `top` | `transform` + `opacity`（绝对定位、无子元素元素除外） |
| 动画 `BlurView` 强度或 Android `elevation` | 交叉渐变静态层 |
| 虚拟化列表行上的 `entering` | 动画容器，或 `itemLayoutAnimation` |
| 在 JS 中重建的屏幕过渡 | 原生堆栈 `animation` |
| 标签之间滑动 | `animation: 'none'` |
| UI 元素上的 `Easing.in(...)` | `Easing.bezier(0.23, 1, 0.32, 1)` |
| `scale(0)` 进入 | `scale(0.95)` + `opacity: 0` |
| 仅距离的关闭阈值 | 速度**或**距离——一个快速动作就足够 |
| 在边界处硬停止 | 橡皮筋阻力 |
| 每帧一个触觉反馈，或作为唯一的反馈 | 每次提交一个，始终与视觉效果配对 |
| 在 Expo Go 或模拟器上判断感觉 | 发布构建，最慢支持的设备 |

## 输出

编写代码。然后，最多几行内：

- **门结果**——频率等级和命名目的。说明您拒绝了什么以及原因。
- **配料**——工具、属性、弹簧或曲线 + 持续时间、线程。
- **在设备上检查什么**——手势、速度传递和触觉时间不能在代码中判断。命名要尝试的内容：快速它，在飞行中中断它，反转它，在您拥有的最慢的 Android 上运行它。

代码是交付物。不要将其填充成报告。

## 语气

主观且简短。当诚实的答案是“这个不应动画”或“这个需要在真实设备上才能告诉您是否正确”时，给出它。
