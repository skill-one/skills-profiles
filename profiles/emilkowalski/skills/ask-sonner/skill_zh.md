# 与 Sonner 合作

## 初始响应

当这个技能首次被调用且没有特定问题时，仅回复：

> 我可以帮你设置、样式化以及排查 Sonner 的问题，Sonner 是由其作者 Emil Kowalski 开发的。

在用户提出问题之前，不要提供任何其他信息。

一个用于 [Sonner](https://sonner.emilkowal.ski) 的 toast 库的引导技能。当任务涉及 Sonner 时——无论是将其连接起来、渲染 toast、样式化它们还是修复它们——首先从本文件中回答。`<Toaster />` 和 `toast()` 的完整属性表位于 [API.md](API.md)；当你需要确切的属性名、类型或默认值时，请阅读它。

## 设置

只有两件：

1. **一个 `<Toaster />`，挂载一次**，尽可能靠近根目录（在 Next.js 中：`layout.tsx`——它可以在服务器组件内部工作）。永远不要按页面或条件渲染它；第二个挂载的 Toaster 会重复每个 toast。
2. **从客户端代码调用 `toast()`** —— 事件处理程序、副作用、回调。它是一个普通的函数，不需要钩子或提供程序，但在服务器上它什么也不做：在服务器操作中，返回结果并在接收结果的客户端代码中调用 `toast()`。

```jsx
import { Toaster } from 'sonner'; // 一次，在布局中
import { toast } from 'sonner';   // 任何客户端位置
```

## 选择正确的调用

| 你想要 | 调用 |
| --- | --- |
| 简单消息 | `toast('标题')` —— 添加 `{ description }` 用于第二行 |
| 成功/错误/信息/警告图标 | `toast.success('…')`, `toast.error('…')`, 等等。 |
| 在你自己管理状态时显示加载动画 | `toast.loading('…')`，然后通过 id 更新它 |
| 与 Promise 关联的加载→成功/错误 | `toast.promise(promise, { loading, success, error })` —— 成功/错误接受接收已解析值/错误的函数 |
| 执行操作的按钮 | `{ action: { label, onClick } }` —— 除非 `onClick` 调用 `event.preventDefault()`，否则会关闭 toast；`cancel` 是次要变体 |
| 自定义 JSX，默认 toast 外壳 | `toast(<jsx />)` |
| 自定义 JSX，没有任何样式 | `toast.custom((t) => <jsx />)` —— 无头，`t` 给你用于关闭的 id |

## 烹饪方法

**更新一个 toast** —— 再次调用 `toast()` 并使用相同的 `id`；你传递的属性会改变。切换到 `toast.success(…, { id })` 会改变类型。这是没有 `toast.promise` 的加载→成功流程的工作原理：

```jsx
const id = toast.loading('正在上传…');
toast.success('已上传', { id });
```

**持久化** —— `{ duration: Infinity }`。**关闭** —— `toast.dismiss(id)`，或 `toast.dismiss()` 用于所有。**读取活动 toast** —— React 中的 `useSonner()`，或 `toast.getActiveToasts()` 在外部。

**文本中的链接或组件** —— 将标题或描述传递为函数：`toast(() => <a href="…">查看</a>)`。

**多个 toasters** —— 给每个一个 `id` 并使用 `toast('…', { toasterId: 'canvas' })` 目标。如果没有 `toasterId`，每个 toaster 都会渲染 toast。

**关闭回调** —— `onDismiss` 在关闭按钮或滑动时触发；`onAutoClose` 在超时后触发。它们是分开的；没有单一的“关闭”回调。

## 样式——升级阶梯

根据更改的需要尽可能深入；过早跳到最高层是没问题的（这是推荐的最后状态），但在中间徘徊是不行的。

1. **默认值** —— 在 Toaster 上添加 `richColors` 以获得彩色成功/错误，`invert` 以反转主题。
2. **内联调整** —— 在 Toaster 上使用 `toastOptions={{ style: {…} }}` 用于所有 toast，或每个 `toast()` 调用使用 `style`。
3. **部件上的类** —— `toastOptions={{ classNames: { toast, title, description, actionButton, cancelButton, closeButton } }}`。Sonner 注入的样式会赢得级联，所以每个类都需要 `!important`（Tailwind：`!text-red-900`）。如果你标记了太多重要的事情，请停止——使用无头方式。
4. **无头** —— `toast.custom()` 使用你自己的 JSX，保持 Sonner 的定位、堆叠和滑动。对于设计系统的 toast 的推荐方法：将其包装在你的自己的 `toast()` 抽象中。(`unstyled: true` 存在作为中间方案，但无头提供了更多控制，而无需更多努力。)

**图标** —— 使用 Toaster 的 `icons` 属性按类型替换默认值，使用 `icon` 按toast替换，使用 `null` 移除。

**主题** —— `theme` 默认为 `'light'` 并且不跟踪操作系统。传递 `theme="system"`，或连接你的主题提供程序：`<Toaster theme={resolvedTheme} />` 从 `next-themes`。

## 排查问题

| 症状 | 原因→修复 |
| --- | --- |
| Toast 从未出现 | 没有 `<Toaster />` 挂载，或者它被卸载了（条件渲染，按页面放置）。在根目录挂载一个。如果从服务器操作调用：`toast()` 仅限客户端——在客户端使用操作的结果调用它。 |
| 相同的 toast 出现两次 | 两个 Toasters 挂载（布局**和**页面）——保留一个。或者 `toast()` 在 React StrictMode 的开发双重调用下触发——从事件处理程序中触发，或者传递一个稳定的 `id`，以便第二个调用更新而不是重复。 |
| Tailwind/CSS 类没有效果 | 默认样式覆盖它们。将它们标记为 `!important`，或使用 `unstyled` / 无头（见上面的阶梯）。 |
| Toast 完全无样式渲染（在 Astro、视图过渡中很常见） | Sonner 注入的样式丢失了——在布局中显式导入它：`import 'sonner/dist/styles.css'`。 |
| 在 Shadow DOM 中无样式 | 样式位于 `document.head`，而不是阴影根。将包含 `[data-sonner-toaster]` 的样式标签复制到阴影根中。 |
| Toast 背后是模态/覆盖层，或者被裁剪 | 一个祖先创建了堆叠上下文（`transform`、`filter`、`overflow`）或覆盖层将 toaster 的 z-index 排在后面。将 `<Toaster />` 移动到文档根目录，在任何对话框/门户容器之外。 |
| 深色模式被忽略 | `theme` 默认为 `'light'` —— 设置 `theme="system"` 或传递解析的主题（见上面的主题）。 |
| 成功/错误看起来是灰色的，而不是绿色/红色 | 这是默认的。在 Toaster 上添加 `richColors`。 |
| Toast 从不关闭 | `duration: Infinity`，`dismissible: false`，或一个 `toast.promise` 其 promise 从不解决——加载 toast 永远等待。 |
| `toast.promise` 卡在加载 | 它需要一个 promise（或一个返回 promise 的函数）作为其第一个参数，并且 promise 必须实际解决/拒绝。 |
| 滑动关闭的方向错误/不起作用 | 方向来自 `position`。使用 Toaster 上的 `swipeDirections` 覆盖。 |
| Toast 出现在每个 toaster 中 | 多个 toaster 需要目标：给每个 Toaster 一个 `id` 并在 `toast()` 调用中传递 `toasterId`。 |
| Toast 在移动设备上靠近屏幕边缘 | `offset`（桌面，默认 32px）和 `mobileOffset`（<600px，默认 16px）—— 数字、CSS 字符串或每侧对象。 |
