# SwiftUI 液态玻璃

## 概述
使用此技能构建或审查与 iOS 26+ 液态玻璃 API 完全一致的 SwiftUI 功能。优先考虑原生 API（`glassEffect`、`GlassEffectContainer`、玻璃按钮样式）和苹果设计指南。保持使用一致性，在需要时提供交互性，并注意性能。

## 工作流决策树
选择与请求匹配的路径：

### 1) 审查现有功能
- 检查液态玻璃应使用和不应使用的位置。
- 验证修饰符顺序、形状使用和容器放置是否正确。
- 检查 iOS 26+ 可用性处理和合理的回退方案。

### 2) 使用液态玻璃改进功能
- 确定需要玻璃处理的组件（表面、芯片、按钮、卡片）。
- 在出现多个玻璃元素时，重构为使用 `GlassEffectContainer`。
- 仅对可点击或可聚焦的元素引入交互式玻璃。

### 3) 使用液态玻璃实现新功能
- 首先设计玻璃表面和交互（形状、突出度、分组）。
- 在布局/外观修饰符之后添加玻璃修饰符。
- 仅在视图层次结构随动画变化时添加变形过渡。

## 核心指南
- 优先使用原生液态玻璃 API 而非自定义模糊效果。
- 当多个玻璃元素共存时使用 `GlassEffectContainer`。
- 在布局和视觉修饰符之后应用 `.glassEffect(...)`。
- 对响应触摸/指针的元素使用 `.interactive()`。
- 在相关元素中保持形状一致以实现协调的外观。
- 使用 `#available(iOS 26, *)` 进行门控并提供非玻璃回退方案。

## 审查清单
- **可用性**：存在 `#available(iOS 26, *)` 并提供回退 UI。
- **组合**：多个玻璃视图包裹在 `GlassEffectContainer` 中。
- **修饰符顺序**：`glassEffect` 应在布局/外观修饰符之后应用。
- **交互性**：仅在存在用户交互时使用 `interactive()`。
- **过渡**：使用 `@Namespace` 与 `glassEffectID` 进行变形。
- **一致性**：功能中形状、染色和间距需保持一致。

## 实现清单
- 定义目标元素和期望的玻璃突出度。
- 将分组玻璃元素包裹在 `GlassEffectContainer` 中并调整间距。
- 根据需要使用 `.glassEffect(.regular.tint(...).interactive(), in: .rect(cornerRadius: ...))`。
- 对操作使用 `.buttonStyle(.glass)` / `.buttonStyle(.glassProminent)`。
- 在层次结构变化时使用 `glassEffectID` 添加变形过渡。
- 为较早版本的 iOS 提供回退材质和视觉效果。

## 快速片段
直接使用这些模式，并根据需要调整形状/染色/间距。

```swift
if #available(iOS 26, *) {
    Text("Hello")
        .padding()
        .glassEffect(.regular.interactive(), in: .rect(cornerRadius: 16))
} else {
    Text("Hello")
        .padding()
        .background(.ultraThinMaterial, in: RoundedRectangle(cornerRadius: 16))
}
```

```swift
GlassEffectContainer(spacing: 24) {
    HStack(spacing: 24) {
        Image(systemName: "scribble.variable")
            .frame(width: 72, height: 72)
            .font(.system(size: 32))
            .glassEffect()
        Image(systemName: "eraser.fill")
            .frame(width: 72, height: 72)
            .font(.system(size: 32))
            .glassEffect()
    }
}
```

```swift
Button("Confirm") { }
    .buttonStyle(.glassProminent)
```

## 资源
- 参考指南：`references/liquid-glass.md`
- 优先参考苹果文档以获取最新的 API 细节。
