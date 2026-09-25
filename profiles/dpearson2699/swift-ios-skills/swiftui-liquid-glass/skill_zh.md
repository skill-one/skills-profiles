# SwiftUI 液态玻璃

液态玻璃是苹果平台引入的动态半透明材质
26. 使用当前 SDK 构建的标凈 SwiftUI 条目和呈现效果会自动采用它。为功能性控件和导航表面保留自定义玻璃效果，而非通用的内容背景。

参见 [references/liquid-glass.md](references/liquid-glass.md) 获取完整的 API 参考，包含更多示例。

## 内容

- [工作流程](#workflow)
- [核心 API 概要](#core-api-summary)
- [代码示例](#code-examples)
- [常见错误](#common-mistakes)
- [审查清单](#review-checklist)
- [参考资料](#references)

## 工作流程

选择与需求匹配的路径：

### 1. 使用液态玻璃实现新功能

1. 确定目标表面（浮动控件、自定义条目、临时控件）。
2. 决定形状、突出程度，以及每个元素是真实控件还是静态状态。
3. 将分组玻璃元素包裹在 `GlassEffectContainer` 中。
4. 在布局和外观修饰符之后应用 `.glassEffect()`。
5. 仅对可点击/可聚焦元素添加 `.interactive()`。
6. 在视图层级随动画变化时添加变形过渡，使用 `glassEffectID(_:in:)`。将 `glassEffectTransition(_:)` 放在插入或移除的玻璃子元素上，而非始终存在的容器上，并使用 [变形与过渡](#morphing--transitions) 选择样式。
7. 使用 `if #available(iOS 26, *)` 进行版本控制，并为早期版本提供回退方案。

### 2. 使用液态玻璃改进现有功能

1. 找到可被 `.glassEffect()` 替换的自定义控件或导航背景。
2. 将兄弟玻璃元素包裹在 `GlassEffectContainer` 中以实现混合和性能优化。
3. 将自定义玻璃按钮替换为 `.buttonStyle(.glass)`、`.buttonStyle(.glassProminent)` 或可配置样式，如 `.buttonStyle(.glass(.clear))`。当按钮需要特定色调或变体时使用 `.glass(_:)`；保留 `.glassProminent` 用于高强调度的主要操作。
4. 在动画插入/移除处添加变形过渡。

### 3. 审查现有液态玻璃使用

通过内容/控件所有权、布局顺序、容器范围、交互性、过渡、可用性、无障碍设置和回退方案追踪每个效果。每次修正后恢复相同的 UI 固定件并重新运行清单。

## 核心API概要

### glassEffect(_:in:)

在视图后应用液态玻璃。默认：`Capsule` 形状的 `.regular` 变体。

```swift
nonisolated func glassEffect(
    _ glass: Glass = .regular,
    in shape: some Shape = DefaultGlassEffectShape()
) -> some View
```

### Glass 结构体

| 属性/方法 | 目的 |
|---|---|
| `.regular` | 标凘玻璃材质 |
| `.clear` | 透明变体；在需要可读性时添加暗化/对比处理 |
| `.identity` | 无视觉效果（透传） |
| `.tint(_:)` | 添加颜色色调以突出显示 |
| `.interactive(_:)` | 响应触摸和指针交互 |

链式调用：`.regular.tint(.blue).interactive()`

### GlassEffectContainer

包裹多个玻璃视图以实现共享渲染、混合和变形。

```swift
GlassEffectContainer(spacing: 24) {
    // 带有 .glassEffect() 的子视图
}
```

`spacing` 控制相邻玻璃形状开始混合的时间。匹配或超过内部布局间距，以便在动画过渡期间形状合并，但在静止时保持分离。

### 变形与过渡

| 修饰符 | 目的 |
|---|---|
| `glassEffectID(_:in:)` | 在视图层级变化时提供变形的稳定标识 |
| `glassEffectUnion(id:namespace:)` | 将多个视图合并为一个玻璃形状 |
| `glassEffectTransition(_:)` | 控制玻璃的显示/消失方式 |

过渡决策：使用 `.matchedGeometry` 处理容器间距内的邻近效果；使用 `.materialize` 处理远距离插入/移除或无需几何匹配的情况；仅在不需要过渡动画时使用 `.identity`。

### 按钮样式

```swift
Button("操作") { }
    .buttonStyle(.glass)           // 标凘玻璃按钮

Button("主要") { }
    .buttonStyle(.glassProminent)  // 突出玻璃按钮

Button("媒体") { }
    .buttonStyle(.glass(.clear))    // 可配置变体；验证对比度
```

### 相关 iOS 26 API

| API | 用途 |
|---|---|
| `scrollEdgeEffectStyle` | 配置滚动边界的外观处理。 |
| `backgroundExtensionEffect` | 在安全区域边缘扩展背景，并使用镜像模糊。 |
| `ToolbarSpacer` | 在工具栏项之间创建视觉分隔。 |

参见 [references/liquid-glass.md](references/liquid-glass.md) 中对应的章节获取签名和示例。

## 代码示例

### 带版本控制的玻璃按钮

```swift
if #available(iOS 26, *) {
    Button("显示状态") { showStatusDetails() }
        .buttonStyle(.glass)
} else {
    Button("显示状态") { showStatusDetails() }
        .buttonStyle(.bordered)
}
```

### 容器中的分组玻璃形状

```swift
let symbols = ["pencil", "eraser.fill", "lasso"]

GlassEffectContainer(spacing: 24) {
    HStack(spacing: 24) {
        ForEach(symbols, id: \.self) { symbol in
            Image(systemName: symbol)
                .frame(width: 56, height: 56)
                .glassEffect()
        }
    }
}
```

### 邻近的变形过渡

```swift
@State private var isExpanded = false
@Namespace private var ns

var body: some View {
    GlassEffectContainer(spacing: 40) {
        HStack(spacing: 40) {
            Image(systemName: "pencil")
                .frame(width: 80, height: 80)
                .glassEffect()
                .glassEffectID("pencil", in: ns)

            if isExpanded {
                Image(systemName: "eraser.fill")
                    .frame(width: 80, height: 80)
                    .glassEffect()
                    .glassEffectID("eraser", in: ns)
                    .glassEffectTransition(.matchedGeometry)
            }
        }
    }

    Button("切换") {
        withAnimation { isExpanded.toggle() }
    }
    .buttonStyle(.glass)
}
```

### 将视图合并为单个玻璃形状

```swift
@Namespace private var ns

GlassEffectContainer(spacing: 20) {
    HStack(spacing: 20) {
        ForEach(items.indices, id: \.self) { i in
            Image(systemName: items[i])
                .frame(width: 80, height: 80)
                .glassEffect()
                .glassEffectUnion(id: i < 2 ? "group1" : "group2", namespace: ns)
        }
    }
}
```

### 带色调的玻璃图标控件

```swift
struct GlassIconControl: View {
    let icon: String
    let tint: Color
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            Image(systemName: icon)
                .font(.title2)
                .padding()
        }
        .buttonStyle(.glass(.regular.tint(tint)))
    }
}
```

### 亮背景上的透明玻璃操作

```swift
if #available(iOS 26, *) {
    ZStack {
        Capsule()
            .fill(.black.opacity(0.28))

        Button {
            playRecap()
        } label: {
            Label("播放", systemImage: "play.fill")
                .font(.headline)
                .padding(.horizontal, 8)
        }
        .buttonStyle(.glass(.clear))
    }
    .fixedSize()
} else {
    Button("播放", systemImage: "play.fill") { playRecap() }
        .buttonStyle(.borderedProminent)
}
```

仅在背景仍能保持标签和符号可读时使用透明玻璃。在亮色或繁忙背景上，添加微暗层或选择更不透明的按钮样式。

### 静态状态计数，非工具栏控件

```swift
VStack(spacing: 8) {
    Text("24")
        .font(.headline.monospacedDigit())
        .accessibilityLabel("24 个选项即将过期")

    Text("选项即将过期")
        .font(.subheadline)
        .foregroundStyle(.secondary)
}
// 将只读状态保持在工具栏控件槽外，并不要添加 .interactive()。
```

## 常见错误

| 错误 | 修正 |
|---|---|
| 玻璃装饰静态内容 | 保持在控件/导航层。 |
| 只读状态使用 `.interactive()` 或操作槽 | 将状态作为内容呈现，或使整个徽章成为一个可访问的操作。 |
| 相关效果使用嵌套容器 | 每个相关混合/变形组使用一个 `GlassEffectContainer`。 |
| `.glassEffect()` 在布局/帧/样式之前 | 先应用布局和外观修饰符，再应用玻璃。 |
| 自定义效果假设默认无障碍设置 | 测试减少透明度、减少动画、对比度和可读性。 |
| 无 iOS 26 之前版本路径 | 使用 `if #available(iOS 26, *)` 控制效果，并保留功能回退。 |

## 审查清单

- [ ] **可用性**：`if #available(iOS 26, *)` 存在，并带有回退 UI。
- [ ] **容器**：多个玻璃视图被包裹在 `GlassEffectContainer` 中。
- [ ] **修饰符顺序**：`.glassEffect()` 在布局/外观修饰符之后应用。
- [ ] **交互性**：`.interactive()` 仅用于存在用户交互的元素。
- [ ] **状态 vs 操作**：静态计数/状态不是工具栏控件，且不暴露点击/悬停提示。
- [ ] **过渡**：使用 `glassEffectID` 与 `@Namespace` 实现变形动画。
- [ ] **过渡类型**：使用 `.matchedGeometry` 处理邻近效果；使用 `.materialize` 处理远距离插入/移除或无需几何匹配的情况；仅在不需要过渡动画时使用 `.identity`。
- [ ] **一致性**：相关元素中的形状、色调和间距保持统一。
- [ ] **性能**：玻璃效果数量有限；使用容器进行分组。
- [ ] **无障碍**：使用减少透明度和减少动画进行测试。
- [ ] **按钮样式**：标准 `.glass`、`.glassProminent` 或可配置 `.glass(_:)` 用于按钮；需要特定色调或透明变体时使用 `.glass(_:)`；保留 `.glassProminent` 用于高强调度的主要操作。
- [ ] **透明玻璃对比度**：亮背景上的透明玻璃具有暗化/对比处理或使用更易读的样式。
- [ ] **并发性**：传递给 `glassEffectID` / `glassEffectUnion` 的 ID 是 `Sendable`；带有 `MainActor` 注解的液态玻璃 API 保持在 SwiftUI UI 代码中。

## 参考资料

- 完整 API 指南：[references/liquid-glass.md](references/liquid-glass.md)
- Apple 文档：[将液态玻璃应用于自定义视图](https://sosumi.ai/documentation/swiftui/Applying-Liquid-Glass-to-custom-views)
- Apple 文档：[采用液态玻璃](https://sosumi.ai/documentation/technologyoverviews/adopting-liquid-glass)
