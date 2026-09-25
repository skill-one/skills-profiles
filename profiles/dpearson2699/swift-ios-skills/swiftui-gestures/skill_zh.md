# SwiftUI 手势 (iOS 26+)

复习、编写和修复 SwiftUI 手势交互。使用 Swift 6.3 模式，以正确的组合、状态管理和冲突解决方式应用现代手势 API。

**范围边界**：此技能拥有 SwiftUI 手势识别、组合、手势状态和特定于手势的可访问性替代方案。更广泛的 SwiftUI 架构/状态所有权属于 `swiftui-patterns`；列表、滚动、表单和控制布局属于 `swiftui-layout-components`；广泛的 UIKit 桥接属于 `swiftui-uikit-interop`。

在更正 Apple API 的可用性、弃用或行为声明时，请在回复中引用相关的 Sosumi 或官方 Apple 文档 URL。

## 内容

- [手势概述](#手势概述)
- [TapGesture](#tapgesture)
- [LongPressGesture](#longpressgesture)
- [DragGesture](#draggesture)
- [MagnifyGesture (iOS 17+)](#magnifygesture-ios-17)
- [RotateGesture (iOS 17+)](#rotategesture-ios-17)
- [手势组合](#gesture-composition)
- [`@GestureState`](#gesturestate)
- [将手势添加到视图](#adding-gestures-to-views)
- [自定义手势协议](#custom-gesture-protocol)
- [常见错误](#common-mistakes)
- [审查清单](#review-checklist)
- [参考资料](#references)

## 手势概述

| 手势 | 类型 | 值 | 自 iOS 版本 |
|---|---|---|---|
| `TapGesture` | 离散 | `Void` | iOS 13 |
| `LongPressGesture` | 离散 | `Bool` | iOS 13 |
| `DragGesture` | 连续 | `DragGesture.Value` | iOS 13 |
| `MagnifyGesture` | 连续 | `MagnifyGesture.Value` | iOS 17 |
| `RotateGesture` | 连续 | `RotateGesture.Value` | iOS 17 |
| `SpatialTapGesture` | 离散 | `SpatialTapGesture.Value` | iOS 16 |

**离散**手势在一次（`.onEnded`）触发。**连续**手势流式传输更新（`.onChanged`、`.onEnded`、`.updating`）。

## TapGesture

识别一个或多个点击。使用 `count` 参数进行多指点击。

```swift
// 单击、双击和三击
TapGesture()            .onEnded { tapped.toggle() }
TapGesture(count: 2)    .onEnded { handleDoubleTap() }
TapGesture(count: 3)    .onEnded { handleTripleTap() }

// 简便修饰符
Text("点击我").onTapGesture(count: 2) { handleDoubleTap() }
```

## LongPressGesture

在用户保持 `minimumDuration` 后成功。如果手指移动超过 `maximumDistance` 则失败。

```swift
// 基本长按（默认 0.5 秒）
LongPressGesture()
    .onEnded { _ in showMenu = true }

// 自定义持续时间和距离容差
LongPressGesture(minimumDuration: 1.0, maximumDistance: 10)
    .onEnded { _ in triggerHaptic() }
```

通过 `@GestureState` + `.updating()` 提供视觉反馈：

```swift
@GestureState private var isPressing = false

Circle()
    .fill(isPressing ? .red : .blue)
    .scaleEffect(isPressing ? 1.2 : 1.0)
    .gesture(
        LongPressGesture(minimumDuration: 0.8)
            .updating($isPressing) { current, state, _ in state = current }
            .onEnded { _ in completedLongPress = true }
    )
```

简便：`.onLongPressGesture(minimumDuration:perform:onPressingChanged:)`。

## DragGesture

跟踪手指移动。`Value` 提供 `startLocation`、`location`、`translation`、`velocity` 和 `predictedEndTranslation`。
`DragGesture.Value.velocity` 从 iOS 13+ 的 `DragGesture` 中可用；不要将其与 iOS 17+ 的手势类型（如 `MagnifyGesture` 和 `RotateGesture`）混淆。

```swift
@State private var offset = CGSize.zero

RoundedRectangle(cornerRadius: 16)
    .fill(.blue)
    .frame(width: 100, height: 100)
    .offset(offset)
    .gesture(
        DragGesture()
            .onChanged { value in offset = value.translation }
            .onEnded { _ in withAnimation(.spring) { offset = .zero } }
    )
```

配置最小距离和坐标空间：

```swift
DragGesture(minimumDistance: 20, coordinateSpace: .global)
```

## MagnifyGesture (iOS 17+)

替换已弃用的 `MagnificationGesture`。跟踪捏合缩放比例。

```swift
@GestureState private var magnifyBy = 1.0

Image("photo")
    .resizable().scaledToFit()
    .scaleEffect(magnifyBy)
    .gesture(
        MagnifyGesture()
            .updating($magnifyBy) { value, state, _ in
                state = value.magnification
            }
    )
```

## RotateGesture (iOS 17+)

`RotateGesture` 是 `RotationGesture` 的新替代方案。跟踪双指旋转角度。

```swift
@State private var angle = Angle.zero

Rectangle()
    .fill(.blue).frame(width: 200, height: 200)
    .rotationEffect(angle)
    .gesture(
        RotateGesture(minimumAngleDelta: .degrees(1))
            .onChanged { value in angle = value.rotation }
    )
```

对于持久化、限制放大和组合旋转示例，请加载 [references/gesture-patterns.md](references/gesture-patterns.md)。

## 手势组合

### `.simultaneously(with:)` — 同时识别两个手势

```swift
let magnify = MagnifyGesture()
    .onChanged { value in scale = value.magnification }

let rotate = RotateGesture()
    .onChanged { value in angle = value.rotation }

Image("photo")
    .scaleEffect(scale)
    .rotationEffect(angle)
    .gesture(magnify.simultaneously(with: rotate))
```

值是 `SimultaneousGesture.Value`，具有 `.first` 和 `.second` 可选参数。

### `.sequenced(before:)` — 第一个必须成功后第二个才能开始

```swift
let longPressBeforeDrag = LongPressGesture(minimumDuration: 0.5)
    .sequenced(before: DragGesture())
    .onEnded { value in
        guard case .second(true, let drag?) = value else { return }
        finalOffset.width += drag.translation.width
        finalOffset.height += drag.translation.height
    }
```

### `.exclusively(before:)` — 只有一个成功（第一个优先）

```swift
let doubleTapOrLongPress = TapGesture(count: 2)
    .exclusively(before:
        LongPressGesture()
    )
    .onEnded { result in
        switch result {
        case .first(_): handleDoubleTap()
        case .second(_): handleLongPress()
        }
    }
```

## `@GestureState`

`@GestureState` 是一个属性包装器，当手势结束时**自动重置**为其初始值。用于临时反馈；使用 `@State` 用于持久值。

```swift
@GestureState private var dragOffset = CGSize.zero  // 重置为 .zero
@State private var position = CGSize.zero            // 持久化

Circle()
    .offset(
        x: position.width + dragOffset.width,
        y: position.height + dragOffset.height
    )
    .gesture(
        DragGesture()
            .updating($dragOffset) { value, state, _ in
                state = value.translation
            }
            .onEnded { value in
                position.width += value.translation.width
                position.height += value.translation.height
            }
    )
```

自定义动画重置：`@GestureState(resetTransaction: Transaction(animation: .spring))`

## 将手势添加到视图

三个修饰符控制视图层次结构中手势的优先级：

| 修饰符 | 行为 |
|---|---|
| `.gesture()` | 低于视图或其子视图已定义的手势的优先级。 |
| `.highPriorityGesture()` | 添加的手势优先级高于现有手势。 |
| `.simultaneousGesture()` | 添加的手势与现有手势相同优先级处理。 |

```swift
let parentTap = TapGesture().onEnded { handleParent() }

VStack {
    Image(systemName: "star.fill")
        .onTapGesture { handleChild() }
}
.simultaneousGesture(parentTap) // 两个处理程序都在子内容上运行。
```

使用 `.gesture(parentTap)` 为默认低优先级父手势，或使用 `.highPriorityGesture(parentTap)` 当添加的父手势应获胜时。

### GestureMask

使用 `.gesture(_:including:)` 控制哪些手势参与：

```swift
.gesture(drag, including: .gesture)   // 添加的手势；禁用子视图手势
.gesture(drag, including: .subviews)  // 子视图手势；禁用添加的手势
.gesture(drag, including: .all)       // 默认：添加 + 子视图手势
.gesture(drag, including: .none)      // 禁用添加 + 子视图手势
```

## 自定义手势协议

通过遵循 `Gesture` 创建可重用的手势：

```swift
struct SwipeGesture: Gesture {
    enum Direction { case left, right, up, down }
    typealias Value = Direction

    let minimumDistance: CGFloat

    init(minimumDistance: CGFloat = 50) {
        self.minimumDistance = minimumDistance
    }

    var body: AnyGesture<Direction> {
        AnyGesture(
            DragGesture(minimumDistance: minimumDistance)
                .map { value in
                    let h = value.translation.width, v = value.translation.height
                    if abs(h) > abs(v) {
                        return h > 0 ? .right : .left
                    } else {
                        return v > 0 ? .down : .up
                    }
                }
        )
    }
}

// 使用
Rectangle().gesture(SwipeGesture().onEnded { print("Swiped \($0)") })
```

将其包装在 `View` 扩展中以获得更符合人体工程学的 API：

```swift
extension View {
    func onSwipe(perform action: @escaping (SwipeGesture.Direction) -> Void) -> some View {
        gesture(SwipeGesture().onEnded(action))
    }
}
```

## 常见错误

### 1. 错误理解父/子手势优先级

不要假设父 `.gesture()` 覆盖子视图手势。明确选择关系，如 [将手势添加到视图](#adding-gestures-to-views) 中所示。

### 2. 使用 `@State` 而不是 `@GestureState` 用于临时状态

使用 `@GestureState` 用于应在识别结束时重置的值；将持久结果保留在 `@State` 中。参见 [`@GestureState`](#gesturestate)。

### 3. 未使用 `.updating()` 提供中间反馈

```swift
// 不要：长按期间无视觉反馈
LongPressGesture(minimumDuration: 2.0)
    .onEnded { _ in showResult = true }

// 要：按住时提供反馈
@GestureState private var isPressing = false

LongPressGesture(minimumDuration: 2.0)
    .updating($isPressing) { current, state, _ in
        state = current
    }
    .onEnded { _ in showResult = true }
```

### 4. 在 iOS 17+ 上使用已弃用的手势类型

```swift
// 不要：自 iOS 17 已弃用
MagnificationGesture()   // 已弃用 — 使用 MagnifyGesture()

// 要：使用新的手势类型
MagnifyGesture()         // iOS 17+
RotateGesture()          // iOS 17+ (较新替代方案)
```

### 5. `onChanged` 中的重计算

```swift
// 不要：每帧调用昂贵工作 (~60-120 Hz)
DragGesture()
    .onChanged { value in
        let result = performExpensiveHitTest(at: value.location)
        let filtered = applyComplexFilter(result)
        updateModel(filtered)
    }

// 要：节流或延迟昂贵工作
DragGesture()
    .onChanged { value in
        dragPosition = value.location  // 仅轻量级状态更新
    }
    .onEnded { value in
        performExpensiveHitTest(at: value.location)  // 结束时一次
    }
```

### 6. 使用 `onTapGesture` 用于应作为 Button 的操作

```swift
// 不要：onTapGesture 没有可访问性特征、VoiceOver 角色、Voice Control 定位、Switch Control 扫描或键盘激活
Text("删除")
    .onTapGesture { deleteItem() }

// 要：Button 自动提供所有这些功能
Button("删除", role: .destructive) { deleteItem() }

// 要：对于自定义视觉效果，使用 ButtonStyle 而不是 onTapGesture
Button { toggleExpanded() } label: {
    CardView()
}
.buttonStyle(.plain)
```

将 `onTapGesture` 保留用于多指点击 (`count: 2+`)、点击位置相关行为或向已有适当可访问性特征的交互内容添加点击识别。

## 审查清单

- [ ] 正确的手势类型：`MagnifyGesture`/`RotateGesture`（不是已弃用的 `Magnification`/`Rotation` 变体）
- [ ] `@GestureState` 用于应重置的临时值；`@State` 用于持久值
- [ ] `.updating()` 在连续手势期间提供中间视觉反馈
- [ ] 使用 `.highPriorityGesture()` 或 `.simultaneousGesture()` 解决父/子冲突
- [ ] `onChanged` 闭包轻量级 — 每帧不进行重计算
- [ ] 组合手势使用正确的组合器：`simultaneously`、`sequenced` 或 `exclusively`
- [ ] 持久化缩放/旋转在 `onEnded` 中限制在合理范围内
- [ ] 自定义 `Gesture` 遵循返回手势体；映射到自定义 `Value` 时使用 `AnyGesture<Value>`
- [ ] 手势驱动动画使用 `.spring` 或类似功能实现自然减速
- [ ] `GestureMask` 考虑在视图层次结构级别混合手势时
- [ ] `onTapGesture` 仅用于 `count > 1`、点击位置或坐标空间有意义的情况 — 简单单击操作使用 `Button` 而不是

## 参考资料

- 当任务需要完整的拖动排序、捏合缩放、组合旋转+缩放、速度/投影、序列化手势状态机或特定于手势的 UIKit 互操作示例时，请阅读 [references/gesture-patterns.md](references/gesture-patterns.md)。
- [Gesture 协议](https://sosumi.ai/documentation/swiftui/gesture)
- [TapGesture](https://sosumi.ai/documentation/swiftui/tapgesture)
- [LongPressGesture](https://sosumi.ai/documentation/swiftui/longpressgesture)
- [DragGesture](https://sosumi.ai/documentation/swiftui/draggesture)
- [DragGesture.Value.velocity](https://sosumi.ai/documentation/swiftui/draggesture/value/velocity)
- [MagnifyGesture](https://sosumi.ai/documentation/swiftui/magnifygesture)
- [RotateGesture](https://sosumi.ai/documentation/swiftui/rotategesture)
- [GestureState](https://sosumi.ai/documentation/swiftui/gesturestate)
- [组合 SwiftUI 手势](https://sosumi.ai/documentation/swiftui/composing-swiftui-gestures)
- [使用手势添加交互](https://sosumi.ai/documentation/swiftui/adding-interactivity-with-gestures)
