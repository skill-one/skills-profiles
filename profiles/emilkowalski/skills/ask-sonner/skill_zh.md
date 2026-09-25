# 与 Sonner 一起工作

## 初始响应

当此技能首次在没有具体问题的情况下被调用时，仅以以下内容回应：

> 我已准备好帮助您配置、样式化并排查 Sonner，我的知识来源于其作者 Emil Kowalski。

在用户提问之前，不要提供任何其他信息。

这是用于 [Sonner](https://sonner.emilkowal.ski)（一个吐司通知库）的指南技能。当任务涉及 Sonner——包括集成配置、渲染吐司通知、样式化或修复相关问题时，请首先依据本文件进行解答。`Toaster` 组件和 `toast()` 函数的完整属性表位于 [API.md](API.md)，当您需要确切的属性名称、类型或默认值时，请阅读该文件。

## 设置

两部分，仅两部分：

1. **一个 `<Toaster />`，仅挂载一次**，尽可能靠近根节点（在 Next.js 中：`layout.tsx`——它可以在服务端组件内部运行）。切勿按页面条件或条件地渲染它；多余的已挂载 Toaster 会重复渲染每一个吐司通知。

2. **从客户端代码中调用 `toast()`**——事件处理器、效果、回调函数。它是一个普通函数，无需使用 hook 或 provider，但在服务器端不执行任何操作：在服务端 action 中，返回结果并在接收该结果的客户端代码中调用 `toast()`。

```jsx
import { Toaster } from 'sonner'; // once, in layout
import { toast } from 'sonner';   // anywhere client-side
```

## 选择合适的调用方式

| 你要什么 | 调用 |
| --- | --- |
| 普通消息 | `toast('Title')` — 添加 `{ description }` 作为第二行内容 |
| 成功 / 错误 / 信息 / 警告图标 | `toast.success('…')`、`toast.error('…')` 等 |
| 自行管理状态时的加载中 | `toast.loading('…')`，然后按 id 更新 |
| 关联到 Promise 的加载中 → 成功/错误 | `toast.promise(promise, { loading, success, error })` — success/error 接收接收已解析值/错误值的函数 |
| 能执行操作的按钮 | `{ action: { label, onClick } }` — 除非 `onClick` 调用 `event.preventDefault()`，否则不会关闭吐司；`cancel` 是备选变体 |
| 自定义 JSX，使用默认吐司外壳 | `toast(<jsx />)` |
| 自定义 JSX，完全不添加样式 | `toast.custom((t) => <jsx />)` — headless（无样式），`t` 会提供用于关闭的 id |

## 配方

**更新吐司通知**——以相同的 `id` 再次调用 `toast()`；只有你传入的属性会发生变化。切换为 `toast.success(…, { id })` 会改变类型。这是不使用 `toast.promise` 实现加载中 → 成功流程的方式：

```jsx
const id = toast.loading('Uploading…');
toast.success('Uploaded', { id });
```

**持久化**——`{ duration: Infinity }`。**关闭**——`toast.dismiss(id)`，或对所有使用 `toast.dismiss()`。**读取活跃的吐司**——在 React 中使用 `useSonner()`，在其他地方使用 `toast.getActiveToasts()`。

**文本中的链接或组件**——在标题或描述中传入一个函数：`toast(() => <a href="…">View</a>)`。

**多个吐司**——给每个一个 `id`，并使用 `toast('…', { toasterId: 'canvas' })` 进行定位。如果不使用 `toasterId`，每个吐司都会渲染该通知。

**关闭回调**——`onDismiss` 在点击关闭按钮或滑动时触发；`onAutoClose` 在超时后触发。它们是分开的；没有单一的"已关闭"回调。

## 样式设置——升级阶梯

仅根据需求上升到所需的层级；过早跳到最高层（这是推荐的最终状态）没有问题，但若停留在中间层级则不行。

1. **默认值**——为 Toaster 添加 `richColors`，用于丰富色彩的成功/错误样式，使用 `invert` 以与主题反转显示。
2. **内联调整**——在 Toaster 上为所有吐司添加 `toastOptions={{ style: {…} }}`，或在每个 `toast()` 调用中添加 `style`。
3. **部分上的类**——`toastOptions={{ classNames: { toast, title, description, actionButton, cancelButton, closeButton } }}`。Sonner 注入的样式会胜出级联，因此每个类都需要 `!important`（Tailwind：`! text-red-900`）。如果你需要标记不止少量内容为重要，请停止——转向 headless 模式。
4. **Headless 模式**——使用自定义 JSX 调用 `toast.custom()`，保留 Sonner 的定位、堆叠和滑动功能。对于设计系统吐司通知，推荐的方案是：用你自己的 `toast()` 抽象包装它。（`unstyled: true` 是一种折中方案，但 headless 模式以同样的努力提供更多控制。）

**图标**——使用 Toaster 的 `icons` 属性按类型替换默认值，使用 `icon` 按吐司替换，使用 `null` 移除。

**主题**——`theme` 默认为 `'light'`，且不跟随操作系统。传入 `theme="system"`，或连接你的主题 provider：从 `next-themes` 中获取 `<Toaster theme={resolvedTheme} />`。

## 故障排除

| 症状 | 原因 → 解决方法 |
| --- | --- |
| 吐司从未出现 | 未挂载 `<Toaster />`，或它已卸载（条件渲染、按页面放置）。在根节点挂载一个。如果从服务端 action 中调用：`toast()` 仅限客户端使用——在客户端中使用 action 的结果来调用它。 |
| 同一个吐司出现两次 | 挂载了两个 Toaster（布局 **和** 页面）——只保留一个。或者 `toast()` 在 React StrictMode 开发环境的双调用效果中触发——改为从事件处理器中触发，或传入稳定的 `id`，使第二次调用进行更新而非重复。 |
| Tailwind/CSS 类无效果 | 默认样式覆盖它们。将它们标记为 `!important`，或使用 `unstyled` / headless（见上述阶梯）。 |
| 吐司渲染完全无样式（Astro、视图过渡中常见） | Sonner 注入的样式表丢失——在布局中显式导入它：`import 'sonner/dist/styles.css'`。 |
| Shadow DOM 内无样式 | 样式位于 `document.head`，而非阴影根节点。将包含 `[data-sonner-toaster]` 文本的样式标签复制到阴影根节点中。 |
| 前驱元素创建了堆叠上下文（`transform`、`filter`、`overflow`），或遮罩层将吐司置于其后（z-index 更高） | 将 `<Toaster />` 移动到文档根节点，移出任何对话框/门户容器之外。 |
| 深色模式被忽略 | `theme` 默认为 `'light'`——设置为 `theme="system"` 或传入解析后的主题（见上文"主题"部分）。 |
| 成功/错误显示为灰色而非绿色/红色 | 这是默认样式。为 Toaster 添加 `richColors`。 |
| 吐司从不关闭 | `duration: Infinity`、`dismissible: false`，或一个无法解决的 `toast.promise`——加载中的吐司会无限等待。 |
| `toast.promise` 卡在加载状态 | 它需要一个 Promise（或返回 Promise 的函数）作为第一个参数，且该 Promise 必须确实解析或拒绝。 |
| 滑动关闭方向错误/无法使用 | 方向从 `position` 派生。使用 Toaster 上的 `swipeDirections` 进行覆盖。 |
| 吐司出现在每个吐司中 | 多个吐司需要定位：给每个 Toaster 一个 `id`，并在 `toast()` 调用中传入 `toasterId`。 |
| 移动端吐司离屏幕边缘太近 | `offset`（桌面端，默认 32px）和 `mobileOffset`（小于 600px，默认 16px）——数字、CSS 字符串或按侧的对象。 |
