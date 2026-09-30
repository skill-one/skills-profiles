---
name: swiftui-liquid-glass
description: 实现、审查或改进适用于iOS 26及更高版本的SwiftUI Liquid Glass效果。涵盖glassEffect修饰符、GlassEffectContainer、玻璃按钮样式、玻璃工具栏/标签栏、静态状态徽章与交互式控件、变形过渡、染色、交互式玻璃、ToolbarSpacer、scrollEdgeEffectStyle、背景扩展效果以及可用性门控。在询问Liquid Glass、玻璃按钮、glassEffect、GlassEffectTransition、glassEffectID、glassEffectUnion、滚动边缘效果或采用iOS 26设计时使用。
---

# SwiftUI 液态玻璃

液态玻璃是苹果平台引入的动态半透明材料
26. 使用当前 SDK 构建的标凈 SwiftUI 条和呈现会自动采用它。为功能控件和导航表面保留自定义玻璃，不要用于一般内容背景。

参见 [references/liquid-glass.md](references/liquid-glass.md) 获取完整的 API 参考，其中包含更多示例。

## 内容

- [工作流](#workflow)
- [核心 API 摘要](#core-api-summary)
- [代码示例](#code-examples)
- [常见错误](#common-mistakes)
- [审查清单](#review-checklist)
- [参考资料](#references)

## 工作流

选择与需求匹配的路径：

### 1. 使用液态玻璃实现新功能

1. 确定目标表面（浮动控件、自定义条、临时控件）。
2. 确定形状、突出显示程度，以及每个元素是真实控件还是静态状态。
3. 将分组玻璃元素包裹在 `GlassEffectContainer` 中。
4. 在布局和外观修饰符之后应用 `.glassEffect()`。
5. 仅对可点击/可聚焦元素添加 `.interactive()`。
6. 在视图层次结构随动画变化的地方添加变形过渡，使用 `glassEffectID(_:in:)`。将 `glassEffectTransition(_:)` 放在插入或移除的玻璃子元素上，而不是始终存在的容器上，并使用 [变形与过渡](#morphing--transitions) 选择样式。
7. 使用 `if #available(iOS 26, *)` 进行门控，并为早期版本提供回退方案。

### 2. 使用液态玻璃改进现有功能

1. 找到可以用 `.glassEffect()` 替换的自定义控件或导航背景。
2. 将兄弟玻璃元素包裹在 `GlassEffectContainer` 中以实现混合和性能优化。
3. 将自定义玻璃状按钮替换为 `.buttonStyle(.glass)`、`.buttonStyle(.glassProminent)` 或可配置样式，如 `.buttonStyle(.glass(.clear))`。当按钮需要特定色调或变体时使用 `.glass(_:)`；保留 `.glassProminent` 用于高强调度的主要操作。
4. 在动画插入/移除处添加变形过渡。

### 3. 审查现有液态玻璃使用

通过内容/控件所有权、布局顺序、容器范围、交互性、过渡、可用性、无障碍设置和回退来追踪每个效果。每次修正后，恢复相同的 UI 固定件并重新运行清单。

## 核心API摘要

### glassEffect(_:in:)

在视图后面应用液态玻璃。默认：`Capsule` 形状的 `.regular` 变体。

```swift
nonisolated func glassEffect(
    _ glass: Glass = .regular,
    in shape: some Shape = DefaultGlassEffectShape()
) -> some View
```

### Glass 结构体

| 属性 / 方法 | 目的 |
|---|---|
| `.regular` | 标凘玻璃材料 |
| `.clear` | 透明变体；在需要可读性时添加变暗/对比度处理 |
| `.identity` | 无视觉效果（传递） |
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

`spacing` 控制附近玻璃形状何时开始混合。匹配或超过内部布局间距，以便在动画过渡期间形状合并，但在静止时保持分离。

### 变形与过渡

| 修饰符 | 目的 |
|---|---|
| `glassEffectID(_:in:)` | 在视图层次结构变化期间变形时的稳定身份 |
| `glassEffectUnion(id:namespace:)` | 将多个视图合并为一个玻璃形状 |
| `glassEffectTransition(_:)` | 控制玻璃出现/消失的方式 |

过渡决策：使用 `.matchedGeometry` 用于容器间距内的附近效果；使用 `.materialize` 用于远距离插入/移除或不应发生几何匹配时；仅在不需要过渡动画时使用 `.identity`。

### 按钮样式

```swift
Button("操作") { }
    .buttonStyle(.glass)           // 标凘玻璃按钮

Button("主要") { }
    .buttonStyle(.glassProminent)  // 突出显示玻璃按钮

Button("媒体") { }
    .buttonStyle(.glass(.clear))    // 可配置变体；验证对比度
```

### 相关 iOS 26 API

| API | 用途 |
|---|---|
| `scrollEdgeEffectStyle` | 配置滚动边界的外观处理。 |
| `backgroundExtensionEffect` | 使用镜像模糊扩展安全区域边缘下的一个背景。 |
| `ToolbarSpacer` | 在工具栏项之间创建视觉分隔。 |

参见 [references/liquid-glass.md](references/liquid-glass.md) 中相应的部分以获取签名和示例。

## 代码示例

### 带可用性门控的玻璃按钮

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

### 附近变形过渡

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

### 亮内容上的透明玻璃操作

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

仅在背景仍然使标签和符号可读时使用透明玻璃。在明亮或繁忙的背景上，添加微妙的变暗层或选择更不透明的按钮样式。

### 静态状态计数，而不是工具栏控件

```swift
VStack(spacing: 8) {
    Text("24")
        .font(.headline.monospacedDigit())
        .accessibilityLabel("24 个选项即将过期")

    Text("选项即将过期")
        .font(.subheadline)
        .foregroundStyle(.secondary)
}
// 将只读状态保持在工具栏控件槽外，不要添加 .interactive()。
```

## 常见错误

| 错误 | 修复 |
|---|---|
| 玻璃装饰静态内容 | 将其保持在控件/导航层。 |
| 只读状态使用 `.interactive()` 或动作槽 | 将状态作为内容呈现，或将整个徽章设为一个真实可访问的操作。 |
| 相关效果使用嵌套容器 | 每个相关混合/变形组使用一个 `GlassEffectContainer`。 |
| `.glassEffect()` 预先于填充/框架/样式 | 首先应用布局和外观，然后应用玻璃。 |
| 自定义效果假设默认无障碍设置 | 测试减少透明度、减少运动、对比度和可读性。 |
| 没有 pre-iOS 26 路径 | 门控效果并保留功能回退。 |

## 审查清单

- [ ] **可用性**：`if #available(iOS 26, *)` 存在，带回退 UI。
- [ ] **容器**：多个玻璃视图包裹在 `GlassEffectContainer` 中。
- [ ] **修饰符顺序**：`.glassEffect()` 应用于布局/外观修饰符之后。
- [ ] **交互性**：`.interactive()` 仅用于存在用户交互的地方。
- [ ] **状态 vs 操作**：静态计数/状态不是工具栏控件，也不暴露点击/悬停提示。
- [ ] **过渡**：使用 `glassEffectID` 与 `@Namespace` 进行变形动画。
- [ ] **过渡类型**：`.matchedGeometry` 用于附近效果；`.materialize` 用于远距离插入/移除，或不应发生几何匹配时；仅在不需要过渡动画时使用 `.identity`。
- [ ] **一致性**：形状、色调和间距在相关元素中保持一致。
- [ ] **性能**：玻璃效果数量有限；使用容器进行分组。
- [ ] **无障碍**：使用 Reduce Transparency 和 Reduce Motion 进行测试。
- [ ] **按钮样式**：使用标准 `.glass`、`.glassProminent` 或可配置 `.glass(_:)`；当需要特定色调或透明变体时使用 `.glass(_:)`；保留 `.glassProminent` 用于高强调度的主要操作。
- [ ] **透明玻璃对比度**：亮内容上的透明玻璃具有变暗/对比度处理或使用更可读的样式。
- [ ] **并发性**：传递给 `glassEffectID` / `glassEffectUnion` 的 ID 是 `Sendable`；MainActor 注释的液态玻璃 API 保持 SwiftUI UI 代码中。

## 参考资料

- 完整 API 指南：[references/liquid-glass.md](references/liquid-glass.md)
- Apple 文档：[将液态玻璃应用于自定义视图](https://sosumi.ai/documentation/swiftui/Applying-Liquid-Glass-to-custom-views)
- Apple 文档：[采用液态玻璃](https://sosumi.ai/documentation/technologyoverviews/adopting-liquid-glass)
