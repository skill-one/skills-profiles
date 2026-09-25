# 在 Expo 中构建动画

这项技能由 [Emil Kowalski](https://github.com/emilkowalski) 协作创建，也可以在 [emilkowalski/skills](https://github.com/emilkowalski/skills) 存储库中找到，其中还包含其他有用的动画技能。

一个用于 React Native 的构建技能。它将一个运动请求转化为在真实设备上通过严格审查的实现——不是在模拟器上，也不是在开发模式下的旗舰手机上。

移动设备改变了动画的三个方面，而这项技能中的所有内容都由此衍生：

1. **没有悬停。** 网页中悬停提供的所有可供性都必须存在于按下、位置或无。
2. **有两个运行时。** Worklets（Reanimated 4）使这一点变得明确：React Native 运行时，React 渲染并您的应用程序逻辑在此运行，以及 UI 运行时，Worklets 每帧运行（加上可选的用于后台工作的 worker 运行时）。一个触及 RN 运行时的动画会在应用程序执行任何其他操作时卡顿。整个工艺在于保持运动在 UI 运行时上。
3. **用户的指尖在元素上。** 手势是主要输入，因此可中断性和速度传递不是装饰——它们是基本要求。

## 运作姿态

您是一位高级移动工程师，自己构建动画。做出决定，用一句话说明理由，编写代码。永远不要将运动选项呈现为菜单。

两种失败模式，第一种更糟：

1. **对不应该动画化的东西进行动画。** 以下门存在是为了有时生成零行代码。
2. **在错误的线程上对正确的东西进行动画**—— 每帧一个 `setState`，一个 `PanResponder`，一个动画化的 `height`。它在您的手机上开发时看起来很好，但在三年前的 Android 设备上会降到 20fps。

## 硬性规则

1. **按顺序运行序列。** 第 1 步和第 2 步控制一切。
2. **Reanimated，而不是核心 `Animated`。** 核心的 `Animated` 不能在没有跨越桥梁的情况下由手势驱动，而 `useNativeDriver` 拒绝任何但变换和不透明度。Reanimated worklets 在 UI 线程上运行，并在 JS 忙碌时继续运行。
3. **没有近似值。** 曲线和弹簧配置来自下表。
4. **减少运动随动画一起发货**，而不是作为后续操作。
5. **在您支持的最慢的设备上的发布构建上判断感觉。** 除此之外，没有任何东西被视为经过验证。

## 构建序列

### 1. 这个需要动画吗？

| 频率 | 决策 |
| --- | --- |
| 每天超过 100 次——标签切换、键盘打开/关闭、滚动、设置中的切换 | **不动画。** 平台默认或无。到这里停止。 |
| 每天几十次——按下反馈、列表导航、行选择 | 只有几乎察觉不到的：少于 150ms，或无 |
| 偶尔——表单、模态框、提示、引导步骤 | 标准动画 |
| 很少/第一次——成功状态、空状态插图、庆祝 | 欣喜预算就在这里 |

**标签切换从不滑动。** 标签是同级，不是层次结构——滑动暗示了不存在深度，而用户为此付出了代价。`animation: 'none'`。

如果请求未通过此门，请说明并不要编写它。

### 2. 目的是什么？

在继续之前，用一句话命名：**反馈**、**空间一致性**、**状态指示**、**防止刺耳的变化**、**解释** 或 **欣喜**（仅限稀有级别）。

无法命名？不要构建。

### 3. 选择工具——最便宜的可用工具

向下走；停在第一个符合的工具处。

| 需求 | 工具 |
| --- | --- |
| 一个无手势的状态驱动变化——按下、切换、颜色、值翻转 | **Reanimated CSS 过渡** (`transitionProperty` 在样式中) |
| 循环、多阶段或在没有状态变化的情况下挂载时播放 | **Reanimated CSS 动画** (`animationName` 关键帧) |
| 元素挂载或卸载，或列表重新布局 | **布局动画** (`entering` / `exiting` / `itemLayoutAnimation`) |
| 任何指尖接触的元素，或任何来自滚动的衍生 | **`useSharedValue` + `Gesture` + `useAnimatedStyle`** |
| 屏幕到屏幕 | **Expo Router 中的原生堆栈选项。** 永远不要手动构建 |
| 一个作为自己的屏幕的底部表单 | **`presentation: 'formSheet'`** — 它是一个真实的 UISheetPresentationController，免费且正确 |
| 标签栏 | **`NativeTabs`**（来自 `expo-router/unstable-native-tabs`）— 平台的真正标签栏，包括其行为和过渡 |
| 上下文菜单、按下预览 | **`Link.Menu` / `Link.Preview`**（Expo Router，仅限 iOS）— 原生菜单和预览，永远不会在 JS 中重新构建 |
| 折叠成大标题的标题 | **`headerLargeTitleEnabled`** 在原生堆栈上（仅限 iOS；`headerLargeTitle` 已弃用）— 不是滚动 worklet |
| 拉动刷新 | **`RefreshControl`** — 只有当它是标志性的交互时才手动构建（见阈值配方） |
| 跟踪键盘的 UI | **`react-native-keyboard-controller`** — 键盘的真实位置，逐帧，在 UI 线程上 |
| 矢量插图、庆祝、空状态 | **Lottie** — 仅用于插图， never for UI state |
| 一个巨大的动画场景、自由绘制 | **`@shopify/react-native-skia`** — 一个画布，当视图层次结构本身是瓶颈时使用 |

只有在值是连续的或可中断的情况下才使用共享值。按下缩放是一个 CSS 过渡；拖动是一个共享值。使用 worklet 对于一个两状态切换来说，相当于为淡出安装一个运动库。

**依赖项。** 使用 `npx expo install <package>` 安装——它解析与项目 SDK 匹配的版本，而普通的 `npm install` 不会：

| 需求 | 包 |
| --- | --- |
| 动画 | `react-native-reanimated` + `react-native-worklets` |
| 手势 | `react-native-gesture-handler` |
| 导航、表单、原生标签、菜单 | `expo-router` |
| 触觉反馈 | `expo-haptics` |
| 跟踪键盘的 UI | `react-native-keyboard-controller`（需要在根目录处提供 `KeyboardProvider` — 见键盘配方） |
| 插图、庆祝 | `lottie-react-native` |
| 非常大的动画场景、自定义绘制 | `@shopify/react-native-skia` |

### 4. 选择属性

- **`transform` 和 `opacity` 是免费的。** 一切其他都是布局传递。`width`、`height`、`margin`、`padding`、`flex`、`top`、`left`、`gap` 每帧都为该节点 *及其兄弟节点* 重新运行 Yoga。
- **一个例外：一个没有子元素的绝对定位元素**—— 标签药丸、进度条填充。它脱离了流，因此没有其他东西重新布局，并且动画化 `width` 保持角落半径，`scaleX` 会将其涂抹。
- **永远不要 `scale(0)`。** 从 `scale(0.9–0.97)` + `opacity: 0` 开始。现实世界中没有任何东西从无中出现。
- **`transform` 是一个数组，顺序很重要** — `[{ translateY }, { scale }]` 移动后缩放；反过来，translate 也会被缩放。除非您想进行乘法，否则请保持 translate 在第一位。
- **Android 阴影是 `elevation`，并且动画化 elevation 每帧都会重新渲染阴影。** 代替的是，动画化预阴影层的透明度。
- **永远不要动画化 `BlurView` 强度。** 在 Android 上它会每帧重新渲染模糊。相反，交叉渐变静态 `BlurView` 的透明度。
- **百分比在 `translate` 中有效**，并且相对于元素自己的大小——`translateY('100%')` 通过元素自己的高度移动一个表单，无论其内容如何。

### 5. 时间或弹簧

**如果涉及指尖，使用弹簧。** 弹簧在中断中传递速度；时间曲线重新开始。其他所有内容都使用时间。

Reanimated 的弹簧直接使用了苹果的两个设计参数——使用这种形式，而不是质量/刚度/阻尼：

| 交互 | 配置 |
| --- | --- |
| 默认沉降，无超调 | `{ duration: 400, dampingRatio: 1 }` |
| 重新定位/拖动后弹回 | `{ duration: 400, dampingRatio: 0.8, velocity }` |
| 表单、抽屉 | `{ duration: 300, dampingRatio: 0.8, velocity }` |
| 绝对不能通过硬边缘 | 添加 `overshootClamping: true` |

**只有在手势携带动量时才弹回。** 菜单淡入时的超调感觉不对；卡片上滑动的超调感觉是对的。

**对于没有指尖在其上的所有内容，使用缓动**：

| 情况 | 缓动 |
| --- | --- |
| 进入或退出 | `ease-out` |
| 屏幕上的移动/变形 | `ease-in-out` |
| 恒定运动（进度、marquee） | `linear` |
| 默认 | `ease-out` |

**永远不要在 UI 上使用 `ease-in`。** 它开始慢，延迟了用户正在观看的确切时刻。Reanimated 的内置内容与 CSS 的弱一样——使用这些：

```js
import { cubicBezier, Easing } from 'react-native-reanimated';

// transitionTimingFunction / animationTimingFunction
const CSS_EASE_OUT = cubicBezier(0.23, 1, 0.32, 1);

// withTiming / .easing(...)
const EASE_OUT = Easing.bezier(0.23, 1, 0.32, 1);      // 强 UI ease-out
const EASE_IN_OUT = Easing.bezier(0.77, 0, 0.175, 1);  // 屏幕上的移动
const EASE_SHEET = Easing.bezier(0.32, 0.72, 0, 1);    // iOS 表单曲线
```

Reanimated 4.1.1 和 4.5.1 拒绝原始的 `'cubic-bezier(...)'` 字符串。CSS 过渡和动画使用 `cubicBezier(...)`；`withTiming` 和 `.easing(...)` 使用 `Easing.bezier(...)`。

**持续时间：**

| 元素 | 持续时间 |
| --- | --- |
| 按下反馈 | 100–150ms |
| 切换、芯片、小状态变化 | 150–200ms |
| 表单、模态框、抽屉 | 弹簧，~300ms 感知 |
| 屏幕过渡 | 平台默认——不要覆盖它 |

移动 UI 动画保持在 300ms 以下，与网页相同。平台自己的过渡更长（iOS 推送是 350ms）；为导航匹配平台，在其他地方超过它。

### 6. 避免在 JS 线程上运行

这是移动特有的工艺，也是大多数 React Native 运动失败的地方。

- **永远不要从手势或滚动处理程序中 `setState`。** 每帧一个 React 渲染是 RN 应用程序中最主要的卡顿原因。共享值 → `useAnimatedStyle`，React 永远不会重新渲染。
- **永远不要在 `onUpdate` 或滚动处理程序中调度回 RN 运行时。** 从 `react-native-worklets` 中的 `scheduleOnRN(fn, ...args)` — Reanimated 4 的 `runOnJS(fn)(...args)` 已弃用的替代方案——将一个 RN 运行时调用排队，在 `onUpdate` 中这是每秒 60–120×。它属于在 `onEnd` 中，或在跨阈值时触发 `useAnimatedReaction` 中。
- **在渲染期间永远不要读取共享值** (`translateY.get()` 在 JSX 中)。它是一个永远不会更新的快照，并且会无声地不同步。**在渲染期间也永远不要写入**——它会在重新组合过程中触发，并且您未造成的重新渲染会重播写入。仅在 worklets、处理程序和效果中触摸共享值。
- **使用 `.get()` / `.set()`，而不是 `.value`。** 相同 API，但直接的 `.value` 访问是 React 编译器无法看穿的——Reanimated 文档称 `get`/`set` 是编译器安全的方式。`set` 还接受一个函数更新：`sv.set((v) => v + 1)`。
- **从 worklet 调用的函数需要 `'worklet'`** 作为其第一行，否则它们在设备上运行时抛出错误，而在调试器中运行良好。

### 7. 按下，而不是悬停

网页上的每个悬停可供性都必须重新设计，而不是移植。

- **按下时提供反馈，按下释放时提交。** 等待点击完成再显示任何内容感觉死板——这是用户实际感知的延迟。
- **任何按钮样式的可点击项上 `scale: 0.97`，在 100–150ms 内**，`Pressable` + CSS 过渡。`scale` 会带着标签和图标一起移动，这是使其看起来像物理的原因。全宽列表行是例外：它们突出显示其背景——缩放行看起来像整个屏幕被挤压。
- **44×44pt 最小触摸目标**（Android 48dp）。如果视觉更小，请添加 `hitSlop`——不要放大视觉。
- **`pressRetentionOffset`** 以防指尖漂移几像素取消用户意图的按下。
- **仅在 Material 风格的应用中才使用 Android 水波纹。** 在自定义设计应用中，两个平台上的相同缩放比在一个平台上出现水波纹更一致。

### 8. 触觉反馈

移动设备有一种网页没有的感觉。有节制地使用它，它会使应用程序感觉昂贵；到处使用它，用户会将其关闭。

| 时刻 | 调用 |
| --- | --- |
| 一个值越过步骤——选择器、滑块锁定、分段控制 | `Haptics.selectionAsync()` |
| 某物弹回，表单锁定，拖动提交 | `Haptics.impactAsync(ImpactFeedbackStyle.Light)` |
| 一个重物落地，一个破坏性操作触发 | `Haptics.impactAsync(ImpactFeedbackStyle.Medium)` |
| 操作成功或失败 | `Haptics.notificationAsync(NotificationFeedbackType.Success / Error)` |

三条规则，它们是绝对的：

- **与视觉效果在同一帧。** 一个滞后于其动画的触觉读起来像错误，而不是反馈。在因果关系时刻触发它——锁定锁定——而不是在动画完成时。
- **每个用户操作一次。** 永远不要在滚动上，永远不要每帧一次，永远不要在用户未触发的进入动画上。
- **永远不要它是唯一的反馈。** 许多用户系统范围内关闭触觉，并且在大多数 Android 硬件上保持静音。视觉效果必须独立存在。

从 worklet，触觉必须调度回 RN 运行时：`scheduleOnRN(Haptics.selectionAsync)`。

### 9. 减少运动和可访问性

```jsx
import { useReducedMotion, ReduceMotion, withSpring } from 'react-native-reanimated';

const reduced = useReducedMotion();
const y = useSharedValue(reduced ? 0 : SHEET_HEIGHT);

// 或让每个动画自己决定
withSpring(0, { duration: 300, dampingRatio: 0.8, reduceMotion: ReduceMotion.System });
```

减少运动意味着**更少和更温和**，而不是零：保留解释状态变化的透明度和颜色变化，删除平移、缩放、视差和超调。屏幕过渡变为 `animation: 'fade'`。

**文本缩放。** `allowFontScaling` 默认开启，因此您在默认类型大小上测量的任何高度在 200% 时都是错误的。永远不要动画化到硬编码的高度——使用 `onLayout` 测量，或者动画化变换而不是。
