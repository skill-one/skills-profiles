# SwiftUI 动画 (iOS 26+)

复习、编写和修复 SwiftUI 动画。使用 Swift 6.3 模式，应用具有正确时间、过渡和可访问性处理的现代动画 API。

## 目录

- [分类处理流程](#triage-workflow)
- [withAnimation（显式动画）](#withanimation-explicit-animation)
- [隐式动画](#implicit-animation)
- [弹簧类型 (iOS 17+)](#spring-type-ios-17)
- [PhaseAnimator (iOS 17+)](#phaseanimator-ios-17)
- [KeyframeAnimator (iOS 17+)](#keyframeanimator-ios-17)
- [`@Animatable 宏`](#animatable-macro)
- [matchedGeometryEffect (iOS 14+)](#matchedgeometryeffect-ios-14)
- [导航缩放过渡 (iOS 18+)](#navigation-zoom-transition-ios-18)
- [过渡 (iOS 17+)](#transitions-ios-17)
- [ContentTransition (iOS 16+)](#contenttransition-ios-16)
- [Symbol Effects (iOS 17+)](#symbol-effects-ios-17)
- [Symbol 渲染模式](#symbol-rendering-modes)
- [常见错误](#common-mistakes)
- [审查清单](#review-checklist)
- [参考资料](#references)

## 分类处理流程

### 第 1 步：识别动画类别

| 类别 | API | 使用场景 |
|---|---|---|
| 状态驱动 | `withAnimation`, `.animation(_:body:)`, `.animation(_:value:)` | 显式状态变化、选择性修饰符动画或简单的值绑定变化 |
| 多阶段 | `PhaseAnimator` | 序列多步动画 |
| 关键帧 | `KeyframeAnimator` | 复杂的多属性编排 |
| 共享元素 | `matchedGeometryEffect` | 布局驱动的英雄过渡 |
| 导航 | `matchedTransitionSource` + `.navigationTransition(.zoom)` | 导航栈的推/弹缩放 |
| 视图生命周期 | `.transition()` | 插入和移除 |
| 文本内容 | `.contentTransition()` | 原地文本/数字变化 |
| Symbol | `.symbolEffect()` | SF Symbol 动画 |
| 自定义 | `CustomAnimation` 协议 | 新奇的时序曲线 |
| Core Animation 桥接 | `CALayer`, `CAAnimation`, `CADisplayLink` | 在建议 `references/core-animation-bridge.md` 之前阅读 |

### 第 2 步：选择动画曲线

```swift
.easeInOut(duration: 0.3)       // 机械时序
.smooth                         // 流畅，无弹跳
.snappy                         // 响应式，小弹跳
.bouncy                         // 活泼，可见弹跳
.spring(duration: 0.5, bounce: 0.3)
```

当预设无法表达预期运动时，使用 [高级目录](references/animation-advanced.md#spring-type-all-initializer-variants)。

### 第 3 步：应用和验证

- 确认动画在正确的状态变化时触发。
- 使用可访问性 > 减少运动进行测试。
- 验证动画内容闭包内没有运行昂贵的操作。
- 对于 CA 桥接，使用协调器作为代理，使无效显示链接，将帧率范围视为提示，并使工作适应实际刷新率。

## withAnimation（显式动画）

```swift
withAnimation(.spring) { isExpanded.toggle() }

// 带完成条件 (iOS 17+)
withAnimation(.smooth(duration: 0.35), completionCriteria: .logicallyComplete) {
    isExpanded = true
} completion: { loadContent() }
```

## 隐式动画

使用 `withAnimation` 处理状态变化所有权，`.animation(_:body:)` 用于选择性修饰符，`.animation(_:value:)` 用于简单的值绑定变化。

```swift
Badge()
    .foregroundStyle(isActive ? .green : .secondary)
    .animation(.snappy) { content in
        content
            .scaleEffect(isActive ? 1.15 : 1.0)
            .opacity(isActive ? 1.0 : 0.7)
    }
```

```swift
Circle()
    .scaleEffect(isActive ? 1.2 : 1.0)
    .opacity(isActive ? 1.0 : 0.6)
    .animation(.bouncy, value: isActive)
```

## 弹簧类型 (iOS 17+)

优先选择感知形式或预设。仅在需要物理、响应式或沉降参数时才加载高级参考。

```swift
Spring(duration: 0.5, bounce: 0.3)
Spring.smooth
Spring.snappy
Spring.bouncy
```

## PhaseAnimator (iOS 17+)

使用每个阶段的动画曲线循环遍历离散阶段。

```swift
enum PulsePhase: CaseIterable {
    case idle, grow, shrink
}

struct PulsingDot: View {
    var body: some View {
        PhaseAnimator(PulsePhase.allCases) { phase in
            Circle()
                .frame(width: 40, height: 40)
                .scaleEffect(phase == .grow ? 1.4 : 1.0)
                .opacity(phase == .shrink ? 0.5 : 1.0)
        } animation: { phase in
            switch phase {
            case .idle: .easeIn(duration: 0.2)
            case .grow: .spring(duration: 0.4, bounce: 0.3)
            case .shrink: .easeOut(duration: 0.3)
            }
        }
    }
}
```

基于触发的变体在每次触发变化时进入下一阶段：

```swift
PhaseAnimator(PulsePhase.allCases, trigger: tapCount) { phase in
    // ...
} animation: { _ in .spring(duration: 0.4) }
```

## KeyframeAnimator (iOS 17+)

沿独立时间线动画多个属性。

```swift
struct AnimValues {
    var scale: Double = 1.0
    var yOffset: Double = 0.0
    var opacity: Double = 1.0
}

struct BounceView: View {
    @State private var trigger = false

    var body: some View {
        Button { trigger.toggle() } label: {
            Image(systemName: "star.fill")
                .font(.largeTitle)
                .keyframeAnimator(
                    initialValue: AnimValues(),
                    trigger: trigger
                ) { content, value in
                    content
                        .scaleEffect(value.scale)
                        .offset(y: value.yOffset)
                        .opacity(value.opacity)
                } keyframes: { _ in
                    KeyframeTrack(\.scale) {
                        SpringKeyframe(1.5, duration: 0.3)
                        CubicKeyframe(1.0, duration: 0.4)
                    }
                    KeyframeTrack(\.yOffset) {
                        CubicKeyframe(-30, duration: 0.2)
                        CubicKeyframe(0, duration: 0.4)
                    }
                    KeyframeTrack(\.opacity) {
                        LinearKeyframe(0.6, duration: 0.15)
                        LinearKeyframe(1.0, duration: 0.25)
                    }
                }
        }
        .buttonStyle(.plain)
    }
}
```

关键帧类型：`LinearKeyframe`（线性）、`CubicKeyframe`（平滑曲线）、`SpringKeyframe`（弹簧物理）、`MoveKeyframe`（瞬间跳跃）。

使用 `repeating: true` 进行循环关键帧动画。
Swift 6：关键帧闭包是 `@Sendable`；在修饰符之前捕获状态/环境值。

## `@Animatable` 宏

替换手动 `AnimatableData` 模板代码。附加到任何具有可动画存储属性的类型。

```swift
@Animatable
struct WaveShape: Shape {
    var frequency: Double
    var amplitude: Double
    var phase: Double
    @AnimatableIgnored var lineWidth: CGFloat

    func path(in rect: CGRect) -> Path {
        // 使用 frequency、amplitude、phase 绘制波浪
    }
}
```

规则：
- 存储属性必须遵循 `VectorArithmetic`。
- 使用 `@AnimatableIgnored` 排除不可动画属性。
- 计算属性永远不会包含。

## matchedGeometryEffect (iOS 14+)

同步视图之间的几何形状以用于共享元素动画。

```swift
struct HeroView: View {
    @Namespace private var heroSpace
    @State private var isExpanded = false

    var body: some View {
        Group {
            if isExpanded {
                Button {
                    withAnimation(.spring(duration: 0.4, bounce: 0.2)) {
                        isExpanded = false
                    }
                } label: {
                    DetailCard()
                        .matchedGeometryEffect(id: "card", in: heroSpace)
                }
            } else {
                Button {
                    withAnimation(.spring(duration: 0.4, bounce: 0.2)) {
                        isExpanded = true
                    }
                } label: {
                    ThumbnailCard()
                        .matchedGeometryEffect(id: "card", in: heroSpace)
                }
            }
        }
        .buttonStyle(.plain)
    }
}
```

每个 ID 刚好一个源视图应可见；否则结果未定义。

## 导航缩放过渡 (iOS 18+)

在源视图上配对 `matchedTransitionSource`，在目标视图上使用 `.navigationTransition(.zoom(...))`。

```swift
struct GalleryView: View {
    @Namespace private var zoomSpace
    let items: [GalleryItem]

    var body: some View {
        NavigationStack {
            ScrollView {
                LazyVGrid(columns: [GridItem(.adaptive(minimum: 100))]) {
                    ForEach(items) { item in
                        NavigationLink {
                            GalleryDetail(item: item)
                                .navigationTransition(
                                    .zoom(sourceID: item.id, in: zoomSpace)
                                )
                        } label: {
                            ItemThumbnail(item: item)
                                .matchedTransitionSource(
                                    id: item.id, in: zoomSpace
                                )
                        }
                    }
                }
            }
        }
    }
}
```

在目标视图上应用 `.navigationTransition`，而不是在内部容器中。

## 过渡 (iOS 17+)

控制视图在插入和移除时的动画方式。

```swift
if showBanner {
    BannerView()
        .transition(.move(edge: .top).combined(with: .opacity))
}
```

查看 [所有过渡类型](references/animation-advanced.md#all-transition-types-ios-17) 以获取内置目录和自定义 `Transition` 示例。

非对称过渡：

```swift
.transition(.asymmetric(
    insertion: .push(from: .bottom),
    removal: .opacity
))
```

## ContentTransition (iOS 16+)

原地内容变化动画，无需插入/移除。

```swift
Text("\(score)")
    .contentTransition(.numericText(countsDown: false))
    .animation(.snappy, value: score)

// 对于 SF Symbols
Image(systemName: isMuted ? "speaker.slash" : "speaker.wave.3")
    .contentTransition(.symbolEffect(.replace.downUp))
```

类型：`.identity`, `.interpolate`, `.opacity`,
`.numericText(countsDown:)`, `.numericText(value:)`, `.symbolEffect`。

## Symbol Effects (iOS 17+)

使用语义效果动画 SF Symbols。`.bounce`, `.pulse`, `.variableColor`,
`.scale`, `.appear`, `.disappear`, 和 `.replace` 是 iOS 17+；`.breathe`,
`.rotate`, 和 `.wiggle` 需要 iOS 18+。

```swift
// 离散（在值变化时触发）
Image(systemName: "bell.fill").symbolEffect(.bounce, value: notificationCount)

// iOS 18+
Image(systemName: "arrow.clockwise")
    .symbolEffect(.wiggle.clockwise, value: refreshCount)

// 无限（条件保持时活动）
Image(systemName: "wifi").symbolEffect(.pulse, isActive: isSearching)

// iOS 18+
Image(systemName: "mic.fill")
    .symbolEffect(.breathe, isActive: isRecording)

// 变量颜色带链式
Image(systemName: "speaker.wave.3.fill")
    .symbolEffect(
        .variableColor.iterative.reversing.dimInactiveLayers,
        options: .repeating,
        isActive: isPlaying
    )
```

范围：`.byLayer`, `.wholeSymbol`。方向因效果而异。

## Symbol 渲染模式

使用 `.symbolRenderingMode(_:)` 选择 `.monochrome`, `.hierarchical`, `.multicolor`, 或 `.palette`；使用 `.foregroundStyle` 供应调色板颜色。

**变量符号：** 使用 `Image(systemName:variableValue:)` (iOS 16+) 进行百分比填充。使用 `.symbolVariableValueMode(_:)` (iOS 26+) 选择 `.draw` 或 `.color`。

```swift
Image(systemName: "wifi", variableValue: signalStrength) // 0.0...1.0
    .symbolVariableValueMode(.draw) // iOS 26+
```

> **文档：** [SymbolRenderingMode](https://sosumi.ai/documentation/swiftui/symbolrenderingmode) · [symbolRenderingMode(_:)](https://sosumi.ai/documentation/swiftui/view/symbolrenderingmode(_:)) · [Image(systemName:variableValue:)](https://sosumi.ai/documentation/swiftui/image/init(systemname:variablevalue:)) · [symbolVariableValueMode(_:)](https://sosumi.ai/documentation/swiftui/view/symbolvariablevaluemode(_:))

## 常见错误

### 1. 当需要精确范围时使用裸 `.animation(_:)`

```swift
// 太宽泛——当视图变化时应用
.animation(.easeIn)

.animation(.easeIn, value: isVisible) // 正确：值绑定

// 正确——将动画范围限定到选定的修饰符
.animation(.easeIn) { content in
    content.opacity(isVisible ? 1.0 : 0.0)
}

withAnimation(.easeIn) { isVisible.toggle() } // 正确：拥有变化
```

### 2. 动画闭包内运行昂贵的操作或 actor-isolated 读取

`keyframeAnimator` / `PhaseAnimator` 内容闭包每帧运行。预计算昂贵的值，仅动画视觉属性，并在 `@Sendable` 关键帧闭包之前捕获状态/环境值。

### 3. 缺少减少运动支持

对于符号，移除继承的效应；使用 `reduceMotion ? .none : animation` 限制较大运动。
```swift
@Environment(\.accessibilityReduceMotion) private var reduceMotion
Image(systemName: "wifi").symbolEffect(.pulse, isActive: isSearching).symbolEffectsRemoved(reduceMotion)
```

### 4. 多个 matchedGeometryEffect 源

每个 ID 刚好一个源视图应可见。具有相同 ID 的多个可见源导致未定义的布局。

### 5. 使用 DispatchQueue 或 UIView.animate

```swift
// 错误
DispatchQueue.main.asyncAfter(deadline: .now() + 0.5) { withAnimation { isVisible = true } }
// 正确
withAnimation(.spring.delay(0.5)) { isVisible = true }
```

### 6. 忘记 ContentTransition 上的动画

```swift
// 错误——没有动画，内容过渡没有效果
Text("\(count)").contentTransition(.numericText(countsDown: true))
// 正确——与动画配对
Text("\(count)")
    .contentTransition(.numericText(countsDown: true))
    .animation(.snappy, value: count)
```

### 7. navigationTransition 在错误的视图上

在最外层的目标视图上应用 `.navigationTransition(.zoom(sourceID:in:))`，而不是在容器内。

## 审查清单

- [ ] 动画曲线与意图匹配（弹簧用于自然，缓动用于机械）
- [ ] `withAnimation` 包裹状态变化；隐式动画使用 `.animation(_:body:)` 用于选择性修饰符范围或 `.animation(_:value:)` 带显式值
- [ ] `matchedGeometryEffect` 每个ID恰好一个源；缩放使用匹配的 `id`/`namespace`
- [ ] `@Animatable` 宏在适合合成时使用；仅当自定义打包更清晰时保留手动 `animatableData`
- [ ] 检查 `accessibilityReduceMotion`；没有 `DispatchQueue`/`UIView.animate`
- [ ] 过渡使用 `.transition()`；`contentTransition` 与动画配对，并使用最窄的隐式动画范围
- [ ] 动画状态变化在 @MainActor 上；动画驱动类型是 Sendable

## 参考资料

- 查看 [references/animation-advanced.md](references/animation-advanced.md) 以获取 CustomAnimation 协议、Spring 变体、过渡类型、符号效果、Transaction 系统、UnitCurve 和性能指南；Core Animation 桥接模式：[references/core-animation-bridge.md](references/core-animation-bridge.md)。
