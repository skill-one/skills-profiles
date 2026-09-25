# 组成：焦点导航

## 核心原则

焦点是具有状态的用户界面行为：明确目标与异常边缘，然后通过用户的键盘、方向键或遥控器输入来驱动和验证它。

## 程序

1. 从已参与焦点的组件开始。仅针对请求的行为添加钩子：

| 需求 | 添加 |
|---|---|
| 普通按钮/文本字段/可点击焦点 | 无需额外操作；使用可聚焦组件 |
| 程序初始化/恢复焦点 | `FocusRequester` + `Modifier.focusRequester(...)` |
| 对焦点变化的视觉或状态反应 | `Modifier.onFocusChanged { ... }` |
| 自定义交互表面且尚未可聚焦 | `Modifier.focusable()` 加上适当的角色/语义 |

2. 从 `LaunchedEffect` 中请求初始或恢复焦点，以目标呈现的条件为键。对于惰性内容，通过稳定的项目 ID 保留请求者，并在项目组合后仅请求。在 `AnimatedContent` 中，使用内容 lambda 的目标一致地用于渲染身份、标签、请求者所有权和效果键；捕获的外部状态使进出内容具有相同的身份。

3. 除非具体边缘、跳跃或陷阱错误，否则保留默认空间搜索。使用 `focusProperties` 仅编码这些异常。

4. 仅处理非正常点击或遍历的行为的按键。精确消费处理的事件；在昂贵所有者处而不是跨屏幕对方向键工作进行节流。

5. 刷新后通过语义身份恢复：当存在时保留聚焦 ID，否则选择确定性的后备方案。

6. 使用具体按键/方向键交互和聚焦语义进行测试。当正在审查的行为是用户触发的，不要用直接状态变异或使输入条件化。仅使用截图来测试焦点外观。

7. 当所有有意目标与异常边缘都已编码，加载/刷新行为具有稳定的焦点策略，且测试使用与用户相同的输入模型时，即可完成。

例如，仅在两种行为都必需时请求和观察焦点：

```kotlin
val requester = remember { FocusRequester() }

Button(
    onClick = onClick,
    modifier = Modifier
        .focusRequester(requester)
        .onFocusChanged { state -> isFocused = state.isFocused },
) {
    Text("Play")
}
```

从效果中调用焦点请求，而不是组合体：

```kotlin
val initialFocus = remember { FocusRequester() }

LaunchedEffect(initialFocus) {
    initialFocus.requestFocus()
}
```

如果目标在加载后出现，以条件为键请求：

```kotlin
LaunchedEffect(items.isNotEmpty()) {
    if (items.isNotEmpty()) {
        firstItemRequester.requestFocus()
    }
}
```

仅当默认空间搜索错误时使用 `focusProperties`：

```kotlin
Modifier.focusProperties {
    up = headerRequester
    down = firstRowRequester
    left = FocusRequester.Cancel
}
```

过多的硬编码链接会创建陈旧的焦点图。对于特殊按键行为，仅消费处理的事件：

```kotlin
Modifier.onPreviewKeyEvent { event ->
    if (event.type == KeyEventType.KeyUp && event.key == Key.Back) {
        onBack()
        true
    } else {
        false
    }
}
```

通过用户输入测试焦点：

```kotlin
composeTestRule.onNodeWithTag("screen").performKeyInput {
    pressKey(Key.DirectionDown)
}

composeTestRule.onNodeWithTag("play-button").assertIsFocused()
```

更广泛的测试形状选择在 [Compose UI 测试模式](../compose-ui-testing-patterns/SKILL.md)。
