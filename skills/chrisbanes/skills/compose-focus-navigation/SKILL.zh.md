---
name: compose-focus-navigation
description: 在编写或审查适用于电视、键盘、桌面、可访问性焦点、方向键导航、FocusRequester、focusProperties、按键事件或初始焦点行为时的Jetpack Compose UI时使用。
---

# 组成：焦点导航

## 核心原则

焦点是具有状态的用户界面行为：明确目标与异常边缘，然后通过用户的键盘、方向键或遥控器输入来驱动和验证它。

## 步骤

1. 从已参与焦点的组件开始。仅针对请求的行为添加钩子：

| 需求 | 添加 |
|---|---|
| 普通按钮/文本字段/可点击焦点 | 无需额外操作；使用可聚焦组件 |
| 程序化初始/恢复焦点 | `FocusRequester` + `Modifier.focusRequester(...)` |
| 对焦点变化的视觉或状态反应 | `Modifier.onFocusChanged { ... }` |
| 自定义交互表面且尚未可聚焦 | `Modifier.focusable()` 加上适当的角色/语义 |

2. 从 `LaunchedEffect` 中请求初始或恢复焦点，以目标出现条件为键。对于惰性内容，通过稳定的项目 ID 保留请求者，并在项目组合后仅请求。在 `AnimatedContent` 中，始终使用内容 lambda 的目标来保持渲染身份、标签、请求者所有权和效果键；捕获的外部状态使进出内容具有相同的身份。
   在评审中，关于 `requestFocus()` 在可组合体中运行的发现，在命名在目标可用后应发出请求的事件或键化效果之前是不完整的。
3. 除非具体边缘、跳跃或陷阱错误，否则保留默认空间搜索。仅用 `focusProperties` 编码这些异常。
4. 仅处理非正常点击或遍历的行为的按键。精确消费处理的事件；在昂贵所有者处而不是跨屏幕限制快速方向键工作。
5. 刷新后通过语义身份恢复：当存在时保留聚焦 ID，否则选择确定性的后备方案。
6. 使用一个具体的键/方向键交互和聚焦语义进行测试。当正在评审的行为由用户触发时，不要用直接状态变异或使输入条件化。仅使用截图来测试焦点外观。
7. 当所有有意目标与异常边缘都被编码，加载/刷新行为具有稳定的焦点策略，并且测试使用与用户相同的输入模型时，即可完成。

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

从效果中调用焦点请求，而不是可组合体体：

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

过多的硬编码链接会创建陈旧的焦点图。对于特殊键行为，仅消费处理的事件：

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

更广泛的测试形状选择在 [Compose UI 测试模式](../compose-ui-testing-patterns/SKILL.md) 中。
