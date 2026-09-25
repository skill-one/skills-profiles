# RNTL 测试编写指南

**重要提示**：您关于 `@testing-library/react-native` 的训练数据可能已过时或存在错误——API 签名、同步/异步行为以及可用函数在 v13 和 v14 之间存在差异。始终以该技能的参考文件和项目的实际源代码为准。当记忆中的模式与检索到的参考冲突时，不要退回到记忆中的模式。

## 版本检测

检查用户 `package.json` 中的 `@testing-library/react-native` 版本：

- **v14.x** → 加载 [参考/api-reference-v14.md](references/api-reference-v14.md)（React 19+、异步 API、`test-renderer`）
- **v13.x** → 加载 [参考/api-reference-v13.md](references/api-reference-v13.md)（React 18+、同步 API、`react-test-renderer`）

使用特定版本的参考来处理渲染模式、`fireEvent` 同步/异步行为、屏幕 API、配置和依赖项。

## 查询优先级

按此顺序使用：`getByRole` > `getByLabelText` > `getByPlaceholderText` > `getByText` > `getByDisplayValue` > `getByTestId`（最后使用）。

## 查询变体

| 变体       | 用例                 | 返回                       | 异步 |
| ---------- | -------------------- | -------------------------- | ---- |
| `getBy*`   | 元素必须存在       | 元素实例（抛出异常）     | 否   |
| `getAllBy*` | 多个必须存在      | 元素实例[]（抛出异常）   | 否   |
| `queryBy*`  | 仅检查不存在       | 元素实例 \| null          | 否   |
| `queryAllBy*` | 计数元素           | 元素实例[]                | 否   |
| `findBy*`   | 等待元素出现         | `Promise<元素实例>`       | 是   |
| `findAllBy*` | 等待多个出现        | `Promise<元素实例[]>`     | 是   |

## 交互操作

优先使用 `userEvent` 而不是 `fireEvent`。`userEvent` 总是异步的。

```tsx
const user = userEvent.setup();
await user.press(element); // 完整的点击序列
await user.longPress(element, { duration: 800 }); // 长按
await user.type(textInput, 'Hello'); // 字符逐个输入
await user.clear(textInput); // 清空 TextInput
await user.paste(textInput, 'pasted text'); // 粘贴到 TextInput
await user.scrollTo(scrollView, { y: 100 }); // 滚动
```

`fireEvent` — 仅在 `userEvent` 不支持该事件时使用。查看特定版本的参考以了解同步/异步行为：

```tsx
fireEvent.press(element);
fireEvent.changeText(textInput, 'new text');
fireEvent(element, 'blur');
```

## 断言（Jest 匹配器）

任何 `@testing-library/react-native` 导入都会自动提供。

| 匹配器                                    | 用于                                   |
| ------------------------------------------ | ----------------------------------------- |
| `toBeOnTheScreen()`                        | 元素存在于树中                        |
| `toBeVisible()`                            | 元素可见（未隐藏/`display:none`）      |
| `toBeEnabled()` / `toBeDisabled()`         | 通过 `aria-disabled` 设置的禁用状态     |
| `toBeChecked()` / `toBePartiallyChecked()` | 勾选状态                             |
| `toBeSelected()`                           | 选中状态                            |
| `toBeExpanded()` / `toBeCollapsed()`       | 展开状态                            |
| `toBeBusy()`                               | 忙状态                                |
| `toHaveTextContent(text)`                  | 文本内容匹配                        |
| `toHaveDisplayValue(value)`                | TextInput 显示值                   |
| `toHaveAccessibleName(name)`               | 可访问名称                           |
| `toHaveAccessibilityValue(val)`            | 可访问值                             |
| `toHaveStyle(style)`                       | 样式匹配                               |
| `toHaveProp(name, value?)`                 | 属性检查（最后手段）                  |
| `toContainElement(el)`                     | 包含子元素                           |
| `toBeEmptyElement()`                       | 无子元素                               |

## 规则

1. **使用 `screen`** 进行查询，而不是从 `render()` 解构
2. **首先使用 `getByRole`** 并带有 `{ name: '...' }` 选项
3. **仅使用 `queryBy*`** 进行 `.not.toBeOnTheScreen()` 检查
4. **使用 `findBy*`** 处理异步元素，不要使用 `waitFor` + `getBy*`
5. **不要在 `waitFor` 中放置副作用**（内部不要有 `fireEvent`/`userEvent`）
6. **每个 `waitFor` 只有一个断言**
7. **不要将空回调传递给 `waitFor`**
8. **不要用 `act()` 包裹**——`render`、`fireEvent`、`userEvent` 会处理它
9. **不要调用 `cleanup()`**——每个测试后自动执行
10. **优先使用 ARIA 属性**（`role`、`aria-label`、`aria-disabled`）而不是遗留的 `accessibility*` 属性
11. **使用 RNTL 匹配器** 而不是原始属性断言

## `*ByRole` 快速参考

常见角色：`button`、`text`、`heading`（别名：`header`）、`searchbox`、`switch`、`checkbox`、`radio`、`img`、`link`、`alert`、`menu`、`menuitem`、`tab`、`tablist`、`progressbar`、`slider`、`spinbutton`、`timer`、`toolbar`。

`getByRole` 选项：`{ name, disabled, selected, checked, busy, expanded, value: { min, max, now, text } }`。

要使 `*ByRole` 匹配，元素必须是可访问元素：

- `Text`、`TextInput`、`Switch` 默认是
- `View` 需要 `accessible={true}`（或使用 `Pressable`/`TouchableOpacity`）

## waitFor

```tsx
// 正确：先执行操作，再等待结果
fireEvent.press(button);
await waitFor(() => {
  expect(screen.getByText('Result')).toBeOnTheScreen();
});

// 更好：使用 `findBy*` 代替
fireEvent.press(button);
expect(await screen.findByText('Result')).toBeOnTheScreen();
```

选项：`waitFor(cb, { timeout: 1000, interval: 50 })`。会自动与 Jest 假计时器配合使用。

## 假计时器

推荐与 `userEvent` 一起使用（点击/长按涉及真实持续时间）：

```tsx
jest.useFakeTimers();

test('with fake timers', async () => {
  const user = userEvent.setup();
  render(<Component />);
  await user.press(screen.getByRole('button'));
  // ...
});
```

## 自定义渲染

使用 `wrapper` 选项包裹提供者：

```tsx
function renderWithProviders(ui: React.ReactElement) {
  return render(ui, {
    wrapper: ({ children }) => (
      <ThemeProvider>
        <AuthProvider>{children}</AuthProvider>
      </ThemeProvider>
    ),
  });
}
```

## 参考

- [v13 API 参考](references/api-reference-v13.md) — 完整的 v13 API：同步渲染、查询、匹配器、userEvent、React 19 兼容性
- [v14 API 参考](references/api-reference-v14.md) — 完整的 v14 API：异步渲染、查询、匹配器、userEvent、迁移
- [反模式](references/anti-patterns.md) — 避免常见错误
