# React 测试库技能

## 快速导航

| 主题       | 链接                                                   |
| ---------- | ------------------------------------------------------ |
| 查询       | [references/queries.md](references/queries.md)         |
| 用户事件   | [references/user-events.md](references/user-events.md) |
| API        | [references/api.md](references/api.md)                 |
| 异步       | [references/async.md](references/async.md)             |
| 调试       | [references/debugging.md](references/debugging.md)     |
| 配置       | [references/config.md](references/config.md)           |

---

## 安装

安装：`npm install --save-dev @testing-library/react @testing-library/dom`。推荐额外安装：`@testing-library/user-event` 和 `@testing-library/jest-dom`。React 19 需要 v16.1.0+。

## 核心理念

> "你的测试越像软件的实际使用方式，它们能给你带来的信心就越多。"

**避免测试**：

- 组件的内部状态
- 内部方法
- 生命周期方法
- 子组件的实现细节

**应该测试**：

- 用户看到和交互的内容
- 从用户的角度出发的行为
- 可访问性（通过角色、标签进行查询）

---

## 查询优先级

按以下优先级顺序使用查询：

### 1. 对所有人可见（首选）

```ts
// 最佳 — 通过 ARIA 角色
getByRole("button", { name: /submit/i });
getByRole("textbox", { name: /email/i });

// 表单字段 — 通过标签
getByLabelText("Email");

// 非交互式内容 — 通过文本
getByText("欢迎回来！");
```

### 2. 语义查询

```ts
// 图片
getByAltText("公司标志");

// 标题属性（可靠性较低）
getByTitle("关闭");
```

### 3. 测试 ID（紧急出口）

```ts
// 仅当其他查询无效时使用
getByTestId("自定义元素");
```

---

## 查询类型

| 类型            | 无匹配 | 1 个匹配 | 多个匹配 | 异步 |
| --------------- | ------ | ------- | ------ | ----- |
| `getBy...`      | 抛出异常 | 返回    | 抛出异常 | 否   |
| `queryBy...`    | null   | 返回    | 抛出异常 | 否   |
| `findBy...`     | 抛出异常 | 返回    | 抛出异常 | 是   |
| `getAllBy...`   | 抛出异常 | 数组    | 数组    | 否   |
| `queryAllBy...` | []     | 数组    | 数组    | 否   |
| `findAllBy...`  | 抛出异常 | 数组    | 数组    | 是   |

**使用场景**：

- `getBy*` — 元素存在
- `queryBy*` — 元素可能不存在（如 `expect(...).not.toBeInTheDocument()`）
- `findBy*` — 元素异步出现

---

## 基本测试模式

```tsx
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

test("登录后显示问候语", async () => {
  const user = userEvent.setup();
  render(<App />);

  // 行动 — 模拟用户交互
  await user.type(screen.getByLabelText(/用户名/i), "john");
  await user.click(screen.getByRole("button", { name: /登录/i }));

  // 断言 — 验证结果
  expect(await screen.findByText(/欢迎，john/i)).toBeInTheDocument();
});
```

---

## 用户事件

始终使用 `@testing-library/user-event` 而不是 `fireEvent`：

```ts
import userEvent from "@testing-library/user-event";

test("用户交互", async () => {
  const user = userEvent.setup();

  // 点击
  await user.click(element);
  await user.dblClick(element);
  await user.tripleClick(element);

  // 输入
  await user.type(input, "Hello");
  await user.clear(input);

  // 选择
  await user.selectOptions(select, ["option1", "option2"]);

  // 键盘
  await user.keyboard("{Enter}");
  await user.keyboard("[ShiftLeft>]a[/ShiftLeft]"); // Shift+A

  // 复制板
  await user.copy();
  await user.paste();

  // 指针
  await user.hover(element);
  await user.unhover(element);
});
```

---

## 异步模式

### waitFor — 重试直到成功

```ts
await waitFor(() => {
  expect(screen.getByText("已加载")).toBeInTheDocument();
});

// 带选项
await waitFor(() => expect(callback).toHaveBeenCalled(), {
  timeout: 5000,
  interval: 100,
});
```

### findBy — 内置的 waitFor

```ts
// 等价于：await waitFor(() => getByText('已加载'))
const element = await screen.findByText("已加载");
```

### waitForElementToBeRemoved

```ts
await waitForElementToBeRemoved(() => screen.queryByText("加载中..."));
```

---

## 常见模式

### 带提供者的自定义渲染

```tsx
// test-utils.tsx
import { render } from "@testing-library/react";
import { ThemeProvider } from "./ThemeProvider";
import { AuthProvider } from "./AuthProvider";

function AllProviders({ children }) {
  return (
    <ThemeProvider>
      <AuthProvider>{children}</AuthProvider>
    </ThemeProvider>
  );
}

const customRender = (ui, options) => render(ui, { wrapper: AllProviders, ...options });

export * from "@testing-library/react";
export { customRender as render };
```

### 测试钩子

```ts
import { renderHook, act } from "@testing-library/react";

test("useCounter 增量", () => {
  const { result } = renderHook(() => useCounter());

  expect(result.current.count).toBe(0);

  act(() => {
    result.current.increment();
  });

  expect(result.current.count).toBe(1);
});
```

### 带新属性的重新渲染

```ts
const { rerender } = render(<Counter count={1} />);
expect(screen.getByText("Count: 1")).toBeInTheDocument();

rerender(<Counter count={2} />);
expect(screen.getByText("Count: 2")).toBeInTheDocument();
```

### 容器内的查询

```ts
import { within } from "@testing-library/react";

const modal = screen.getByRole("dialog");
const submitBtn = within(modal).getByRole("button", { name: /提交/i });
```

---

## 调试

```ts
// 打印整个 DOM
screen.debug();

// 打印特定元素
screen.debug(screen.getByRole("button"));

// 记录可用角色
import { logRoles } from "@testing-library/react";
logRoles(container);

// 带 prettyDOM 选项
screen.debug(undefined, 10000); // 最大长度
```

---

## jest-dom 匹配器

```ts
import "@testing-library/jest-dom";

expect(element).toBeInTheDocument();
expect(element).toBeVisible();
expect(element).toBeEnabled();
expect(element).toBeDisabled();
expect(element).toHaveTextContent("Hello");
expect(element).toHaveValue("input value");
expect(element).toHaveAttribute("href", "/home");
expect(element).toHaveClass("active");
expect(element).toHaveFocus();
expect(element).toBeChecked();
```

---

## 配置

```ts
import { configure } from "@testing-library/react";

configure({
  // 自定义测试 ID 属性
  testIdAttribute: "data-my-test-id",

  // 异步超时
  asyncUtilTimeout: 5000,

  // 默认隐藏
  defaultHidden: true,

  // 抛出建议（调试）
  throwSuggestions: true,
});
```

---

## ❌ 禁止（反模式）

```ts
// ❌ 不要通过类/ID 查询
container.querySelector(".my-class");

// ❌ 不要使用 container.firstChild
const { container } = render(<Component />);
expect(container.firstChild).toHaveClass("active");

// ❌ 当 userEvent 可用时不要使用 fireEvent
fireEvent.click(button); // 使用 userEvent.click 代替

// ❌ 不要测试实现细节
expect(component.state.loading).toBe(false);

// ❌ 不要在 waitFor 回调中使用 waitFor 与 findBy
await waitFor(() => screen.findByText("x")); // findBy 已经等待

// ❌ 不要在 waitFor 回调中断言（除非必要）
await waitFor(() => {
  expect(mockFn).toHaveBeenCalled(); // OK — 需要等待调用
});
```

---

## ✅ 最佳实践

```ts
// ✅ 使用 screen 进行所有查询
import { render, screen } from "@testing-library/react";
render(<Component />);
screen.getByRole("button"); // 良好

// ✅ 优先使用 userEvent 而不是 fireEvent
const user = userEvent.setup();
await user.click(button);

// ✅ 使用 findBy 测试异步元素
const element = await screen.findByText("已加载");

// ✅ 使用 queryBy 测试不存在的情况
expect(screen.queryByText("错误")).not.toBeInTheDocument();

// ✅ 使用 within 进行作用域查询
const form = screen.getByRole("form");
within(form).getByLabelText("Email");

// ✅ 使用可访问性查询（角色、标签、文本）
getByRole("button", { name: /提交/i });
```

---

## 文本匹配选项

```ts
// 精确匹配（默认）
getByText("Hello World");

// 子字符串匹配
getByText("llo Worl", { exact: false });

// 正则表达式
getByText(/hello world/i);

// 自定义函数
getByText((content, element) => {
  return element.tagName === "SPAN" && content.startsWith("Hello");
});
```

---

## 快速参考

| 导入              | 使用                             |
| ----------------- | --------------------------------- |
| `render`          | 将组件渲染到 DOM                 |
| `screen`          | 查询渲染的 DOM                   |
| `cleanup`         | 卸载组件（Jest 自动执行）        |
| `act`             | 包装状态更新                     |
| `renderHook`      | 测试自定义钩子                   |
| `within`          | 将查询作用域限制到元素            |
| `waitFor`         | 重试直到断言通过                 |
| `configure`       | 设置全局选项                     |
| `userEvent.setup()` | 创建用户事件实例                 |

## 链接

- [文档](https://testing-library.com/docs/react-testing-library/intro/)
- [发布](https://github.com/testing-library/react-testing-library/releases)
- [GitHub](https://github.com/testing-library/react-testing-library)
- [npm](https://www.npmjs.com/package/@testing-library/react)
