# 组合：动画

## 核心原则

选择能够表达运动及其生命周期的最小 API。

## 步骤

1. 识别任务：显示或隐藏子树、动画化一个值、从一个状态协调多个值、调整内容大小、交换内容或处理用户驱动的运动。
2. 从表格中选择匹配的 API。优先选择目标状态 API；仅在手势、中断或命令式控制需要时使用 `Animatable`。
3. 检查生命周期：alpha 动画保持内容组合；`AnimatedVisibility` 在退出后移除它。在需要卸载时不要使用淡出效果。
4. 对于 `AnimatedContent`，从内容 lambda 目标渲染，并且仅在视觉身份与有效载荷相等性不同时选择 `contentKey`。阅读 [AnimatedContent 身份](references/animated-content.md) 了解状态持有者详情。
5. 当动画 `State` 在帧率变化时，将其保持在布局或绘制块修饰符中；将更深层次的诊断路由到 [Compose 性能](../compose-performance/SKILL.md)。
6. 使用 Navigation Compose 过渡效果处理目标交换，并使用专用库处理基于艺术的运动。
7. 当 API、生命周期和内容身份与 UI 匹配，没有更简单的 API 适用，且相关行为已验证时，完成。

## API 选择

| 需求 | 优先选择 |
|---|---|
| 带有进入/退出语义地显示/隐藏子树 | [`AnimatedVisibility`](https://developer.android.com/develop/ui/compose/animation/composables-modifiers#animatedvisibility) |
| 一个值跟随状态 | `animate*AsState` |
| 多个值跟随一个布尔值、枚举或密封状态 | `rememberTransition` 加上子动画 |
| 子项大小变化 | `Modifier.animateContentSize()` |
| 不同的组合项树填充一个区域 | `AnimatedContent`，或对于简单情况使用 `Crossfade` |
| 拖动、快速滑动、中断或命令式控制 | [`Animatable`](https://developer.android.com/reference/kotlin/androidx/compose/animation/core/Animatable) |

当默认运动不正确时使用 `AnimationSpec`，当多个动画需要工具可见性时使用一个独特的 `label`。

```kotlin
val width by animateDpAsState(
    targetValue = if (expanded) 200.dp else 56.dp,
    animationSpec = spring(dampingRatio = 0.7f),
    label = "fabWidth",
)
```

对于必须保持同步的值，在单个过渡上定义它们，而不是多个独立的 `animate*AsState` 调用：

```kotlin
val transition = rememberTransition(targetState = phase, label = "phase")
val alpha by transition.animateFloat(label = "alpha") { target ->
    if (target == Phase.Visible) 1f else 0f
}
val offset by transition.animateDp(label = "offset") { target ->
    if (target == Phase.Visible) 0.dp else 24.dp
}
```

对于动画填充，当颜色每帧更新时，优先选择 `drawBehind { drawRect(color.value) }` 覆盖值形式背景。对于 API 模棱两可的情况，从官方 [选择动画 API](https://developer.android.com/develop/ui/compose/animation/choose-api) 指南开始；使用 [`rememberInfiniteTransition`](https://developer.android.com/reference/kotlin/androidx/compose/animation/core/rememberInfiniteTransition) 处理重复循环，使用 [`SeekableTransitionState`](https://developer.android.com/reference/kotlin/androidx/compose/animation/core/SeekableTransitionState) 处理可搜索或测试控制的进度。

## 不应使用此技巧的情况

- 对于副作用定时或点击启动的工作，使用 [Compose 状态和效果](../compose-state-and-effects/SKILL.md)。
- 对于深层状态读取或重组诊断，使用 [Compose 性能](../compose-performance/SKILL.md)。
