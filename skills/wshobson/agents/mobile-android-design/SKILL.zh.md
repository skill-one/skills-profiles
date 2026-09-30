---
name: mobile-android-design
description: 掌握 Material Design 3 和 Jetpack Compose 模式，用于构建原生 Android 应用。在设计 Android 界面、实现 Compose UI 或遵循 Google 的 Material Design 指南时使用。
---

# 安卓移动设计

掌握 Material Design 3 (Material You) 和 Jetpack Compose，以构建现代、自适应的安卓应用程序，使其能够与安卓生态系统无缝集成。

## 何时使用这项技能

- 按照 Material Design 3 设计安卓应用界面
- 构建 Jetpack Compose UI 和布局
- 实现 Android 导航模式（Navigation Compose）
- 为手机、平板和折叠屏创建自适应布局
- 使用 Material 3 主题和动态颜色
- 构建可访问的安卓界面
- 实现安卓特有的手势和交互
- 针对不同屏幕配置进行设计

## 详细部分：核心概念

最初是本 SKILL.md 中一个 9201 字节的部分。已移至 `references/details.md` 以适应 Codex 的 8 KB 技能主体限制。

## 快速入门组件

```kotlin
@Composable
fun ItemListCard(
    item: Item,
    onItemClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    Card(
        onClick = onItemClick,
        modifier = modifier.fillMaxWidth(),
        shape = RoundedCornerShape(12.dp)
    ) {
        Row(
            modifier = Modifier
                .padding(16.dp)
                .fillMaxWidth(),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Box(
                modifier = Modifier
                    .size(48.dp)
                    .clip(CircleShape)
                    .background(MaterialTheme.colorScheme.primaryContainer),
                contentAlignment = Alignment.Center
            ) {
                Icon(
                    imageVector = Icons.Default.Star,
                    contentDescription = null,
                    tint = MaterialTheme.colorScheme.onPrimaryContainer
                )
            }

            Spacer(modifier = Modifier.width(16.dp))

            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = item.title,
                    style = MaterialTheme.typography.titleMedium
                )
                Text(
                    text = item.subtitle,
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }

            Icon(
                imageVector = Icons.Default.ChevronRight,
                contentDescription = null,
                tint = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }
    }
}
```

## 最佳实践

1. **使用 Material 主题**：通过 `MaterialTheme.colorScheme` 访问颜色，以支持自动暗黑模式
2. **支持动态颜色**：在安卓 12 及更高版本上启用动态颜色以实现个性化
3. **自适应布局**：使用 `WindowSizeClass` 进行响应式设计
4. **内容描述**：为所有交互元素添加 `contentDescription`
5. **触摸目标**：最小 48dp 触摸目标以实现可访问性
6. **状态提升**：提升状态以使组件可重用和可测试
7. **正确记忆**：适当使用 `remember` 和 `rememberSaveable`
8. **预览注解**：使用 `@Preview` 并配置不同的参数

## 常见问题

- **重组问题**：避免传递不稳定的 lambda；使用 `remember`
- **状态丢失**：使用 `rememberSaveable` 处理配置更改
- **性能问题**：对于长列表使用 `LazyColumn` 而不是 `Column`
- **主题泄漏**：确保 `MaterialTheme` 包裹所有可组合项
- **导航崩溃**：正确处理返回键和深度链接
- **内存泄漏**：在 `DisposableEffect` 中取消协程
