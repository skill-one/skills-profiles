# Android移动端设计

掌握Material Design 3（Material You）和Jetpack Compose，构建与现代Android生态系统无缝集成的现代、自适应Android应用程序。

## 使用此技能的场景

- 按照Material Design 3设计Android应用界面
- 构建Jetpack Compose UI和布局
- 实现Android导航模式（Navigation Compose）
- 为手机、平板和折叠屏创建自适应布局
- 使用Material 3主题和动态颜色
- 构建可访问的Android界面
- 实现Android特有的手势和交互
- 针对不同屏幕配置进行设计

## 详细部分：核心概念

最初是此SKILL.md中一个9201字节的段落。已移至`references/details.md`以适应Codex的8 KB技能主体限制。

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

1. **使用Material主题**：通过`MaterialTheme.colorScheme`访问颜色，以支持自动暗黑模式
2. **支持动态颜色**：在Android 12+上启用动态颜色以实现个性化
3. **自适应布局**：使用`WindowSizeClass`进行响应式设计
4. **内容描述**：为所有交互元素添加`contentDescription`
5. **触摸目标**：最小48dp触摸目标以实现可访问性
6. **状态提升**：提升状态以使组件可重用和可测试
7. **正确记忆**：适当使用`remember`和`rememberSaveable`
8. **预览注解**：使用`@Preview`添加不同配置

## 常见问题

- **重组问题**：避免传递不稳定的lambda；使用`remember`
- **状态丢失**：使用`rememberSaveable`处理配置更改
- **性能问题**：对于长列表使用`LazyColumn`而不是`Column`
- **主题泄漏**：确保所有可组合项都被`MaterialTheme`包裹
- **导航崩溃**：正确处理返回键和深层链接
- **内存泄漏**：在`DisposableEffect`中取消协程
