审查 Swift 和 SwiftUI 代码的正确性、现代 API 使用情况以及是否符合项目规范。仅报告真实问题——不要吹毛求疵或编造问题。

审查流程：

1. 使用 `references/api.md` 检查已弃用的 API。
1. 使用 `references/views.md` 检查视图、修饰符和动画是否已最佳编写。
1. 使用 `references/data.md` 验证数据流是否配置正确。
1. 使用 `references/navigation.md` 确保导航已更新且性能良好。
1. 使用 `references/design.md` 确保代码使用的设计符合可访问性要求并遵守 Apple 的人机界面指南。
1. 使用 `references/accessibility.md` 验证可访问性合规性，包括动态类型、VoiceOver 和减少运动。
1. 使用 `references/performance.md` 确保代码能够高效运行。
1. 使用 `references/swift.md` 快速验证 Swift 代码。
1. 使用 `references/hygiene.md` 进行最终的代码卫生检查。

如果进行部分审查，仅加载相关的参考文件。

## 核心指示

- iOS 26 存在，并且是新建应用默认的部署目标。
- 目标 Swift 6.2 或更高版本，使用现代的 Swift 并发。
- 作为 SwiftUI 开发者，用户应避免使用 UIKit，除非有要求。
- 未经询问，不要引入第三方框架。
- 将不同类型的代码分开到不同的 Swift 文件中，而不是将多个结构体、类或枚举放在一个文件中。
- 使用一致的项目结构，文件夹布局由应用功能决定。

## 输出格式

按文件组织发现。对于每个问题：

1. 说明文件和相关的行号。
2. 命名违反的规则（例如，“使用 `foregroundStyle()` 而不是 `foregroundColor()`”）。
3. 显示简短的原始/修复后的代码。

跳过没有问题的文件。最后以优先级总结需要首先进行的最有影响力的更改。

示例输出：

### ContentView.swift

**第 12 行：使用 `foregroundStyle()` 而不是 `foregroundColor()`。**

```swift
// 原始
Text("Hello").foregroundColor(.red)

// 修复后
Text("Hello").foregroundStyle(.red)
```

**第 24 行：仅图标按钮对 VoiceOver 不友好——添加文本标签。**

```swift
// 原始
Button(action: addUser) {
    Image(systemName: "plus")
}

// 修复后
Button("Add User", systemImage: "plus", action: addUser)
```

**第 31 行：避免在视图体中使用 `Binding(get:set:)`——使用 `@State` 与 `onChange()` 代替。**

```swift
// 原始
TextField("Username", text: Binding(
    get: { model.username },
    set: { model.username = $0; model.save() }
))

// 修复后
TextField("Username", text: $model.username)
    .onChange(of: model.username) {
        model.save()
    }
```

### 总结

1. **可访问性（高）：** 第 24 行的添加按钮对 VoiceOver 不可见。
2. **已弃用的 API（中）：** 第 12 行的 `foregroundColor()` 应该是 `foregroundStyle()`。
3. **数据流（中）：** 第 31 行的手动绑定脆弱且难以维护。

示例结束。

## 参考

- `references/accessibility.md` - 动态类型、VoiceOver、减少运动和其他可访问性要求。
- `references/api.md` - 更新代码以使用现代 API，以及它替换的已弃用代码。
- `references/design.md` - 构建符合 Apple 人机界面指南的可访问应用的指导。
- `references/hygiene.md` - 使代码能够干净编译并在长期内保持可维护性。
- `references/navigation.md` - 使用 `NavigationStack`/`NavigationSplitView` 的导航，以及警报、确认对话框和表单。
- `references/performance.md` - 优化 SwiftUI 代码以获得最佳性能。
- `references/data.md` - 数据流、共享状态和属性包装器。
- `references/swift.md` - 关于编写现代 Swift 代码的技巧，包括有效使用 Swift 并发。
- `references/views.md` - 视图结构、组合和动画。
