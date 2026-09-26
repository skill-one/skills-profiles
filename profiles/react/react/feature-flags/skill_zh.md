# React 功能标志

## 标志文件

| 文件 | 目的 |
|------|---------|
| `packages/shared/ReactFeatureFlags.js` | 默认标志 (canary)，`__EXPERIMENTAL__` 覆盖 |
| `packages/shared/forks/ReactFeatureFlags.www.js` | www 渠道，`__VARIANT__` 覆盖 |
| `packages/shared/forks/ReactFeatureFlags.native-fb.js` | React Native，`__VARIANT__` 覆盖 |
| `packages/shared/forks/ReactFeatureFlags.test-renderer.js` | 测试渲染器 |

## 控制测试

### `@gate` 指令 (测试级别)

当功能在没有标志的情况下完全不可用时使用：

```javascript
// @gate enableViewTransition
it('支持视图过渡', () => {
  // 只有当 enableViewTransition 为 true 时才运行此测试
  // 当为 false 时会被跳过 (不会失败)
});
```

### `gate()` 内联 (断言级别)

当功能存在但行为根据标志不同时使用：

```javascript
it('渲染组件', async () => {
  await act(() => root.render(<App />));

  if (gate(flags => flags.enableNewBehavior)) {
    expect(container.textContent).toBe('新输出');
  } else {
    expect(container.textContent).toBe('旧输出');
  }
});
```

## 添加新标志

1. 在 `ReactFeatureFlags.js` 中添加默认值
2. 在每个分支文件 (`*.www.js`，`*.native-fb.js` 等) 中添加
3. 如果在 www/React Native 中需要变化，在分支文件中设置为 `__VARIANT__`
4. 使用 `@gate flagName` 或内联 `gate()` 控制测试

## 检查标志状态

使用 `/flags` 查看各渠道的状态。有关完整命令选项，请参阅 `flags` 技能。

## `__VARIANT__` 标志 (GKs)

设置为 `__VARIANT__` 的标志模拟守门人 - 测试两次 (true 和 false)：

```bash
/test www <模式>              # __VARIANT__ = true
/test www variant false <模式> # __VARIANT__ = false
```

## 调试特定渠道的失败

1. 运行 `/flags --diff <渠道1> <渠道2>` 比较值
2. 检查 `@gate` 条件 - 测试可能仅针对特定渠道控制
3. 运行 `/test <渠道> <模式>` 隔离失败
4. 如果是新添加的，验证标志存在于所有分支文件中

## 常见错误

- **遗漏两种变体** - 对于 `__VARIANT__` 标志，始终测试 `www` 和 `www variant false`
- **使用 @gate 处理行为差异** - 如果两种路径都应该运行，使用内联 `gate()`
- **缺少分支文件** - 新标志必须添加到所有分支文件中，而不仅仅是主文件
- **错误的 gate 语法** - 使用 `gate(flags => flags.name)`，而不是 `gate('name')`
