# React 视图过渡

使用浏览器的原生 `document.startViewTransition` 在 UI 状态之间进行动画。通过 `<ViewTransition>` 声明 *什么*，使用 `startTransition` / `useDeferredValue` / `Suspense` 触发 *何时*，通过 CSS 类控制 *如何*。不支持的浏览器会优雅地跳过动画。

## 何时进行动画

每个 `<ViewTransition>` 都应该传达空间关系或连续性。如果你无法说明它传达了什么，就不要添加它。

按此顺序实现此列表中 **所有** 适用的模式：

| 优先级 | 模式 | 它传达了什么 |
|--------|------|-------------|
| 1 | **共享元素** (`name`) | "相同事物——深入查看" |
| 2 | **Suspense 揭示** | "数据已加载" |
| 3 | **列表身份** (per-item `key`) | "相同项目，新排列" |
| 4 | **状态变化** (`enter`/`exit`) | "某物出现/消失" |
| 5 | **路由变化** (页面级) | "前往新地方" |

这是一个实现顺序，而不是 "选择一个" 的列表。实现适合应用的每个模式。只有当应用没有该模式用例时才跳过。

### 选择动画样式

| 上下文 | 动画 | 原因 |
|--------|------|------|
| 分层导航 (列表→详情) | 类型键 `nav-forward` / `nav-back` | 传达空间深度 |
| 横向导航 (标签→标签) | 纯 `<ViewTransition>` (淡入淡出) 或 `default="none"` | 没有深度需要传达 |
| Suspense 揭示 | `enter`/`exit` 字符串属性 | 内容到达 |
| 重新验证 / 背景刷新 | `default="none"` | 安静的——不需要动画 |

保留方向性滑动用于分层导航 (列表→详情) 和有序序列 (前/后照片、轮播、分页结果)。对于有序序列，方向传达位置："下一个" 从右侧滑动，"上一个" 从左侧滑动。横向/无序导航 (标签→标签) 不应使用方向性滑动——它会错误地暗示空间深度。

---

## 可用性

- **Next.js:** 不要安装 `react@canary` —— App Router 已经内部捆绑了 React canary。`ViewTransition` 开箱即用。`npm ls react` 可能会显示一个看起来很稳定的版本；这是预期的。
- **没有 Next.js:** 安装 `react@canary react-dom@canary` (`ViewTransition` 不在稳定版 React 中)。
- 浏览器支持：Chromium 125+ (React 需要的是 `startViewTransition` 的 v2 对象形式)，Firefox 144+，Safari 18.2+。在不支持的浏览器上优雅降级。

---

## 实现工作流程

在现有应用中添加视图过渡时，**按步骤遵循 [references/implementation.md](references/implementation.md)**。从审计开始——不要跳过它。使用 [references/css-recipes.md](references/css-recipes.md) 获取适用的 CSS 并将其应用于应用。

---

## 核心概念

### `<ViewTransition>` 组件

```jsx
import { ViewTransition } from 'react';

<ViewTransition>
  <Component />
</ViewTransition>
```

React 自动分配一个唯一的 `view-transition-name` 并在后台调用 `document.startViewTransition`。自己永远不要调用 `startViewTransition`。

### 动画触发器

| 触发器 | 触发时机 |
|--------|----------|
| **enter** | 在过渡期间首次插入 `<ViewTransition>` 时 |
| **exit** | 在过渡期间首次移除 `<ViewTransition>` 时 |
| **update** | `<ViewTransition>` 内部的 DOM 变化，或边界本身因立即同级元素而改变大小/位置。对于嵌套 VT，变化适用于最内层的一个 |
| **share** | 命名的 VT 卸载，在同一个过渡中挂载具有相同 `name` 的另一个 VT |

只有 `startTransition`、`useDeferredValue` 或 `Suspense` 激活 VT。常规的 `setState` 不会动画。

### 关键位置规则

`<ViewTransition>` 仅在它出现在 **任何 DOM 节点之前** 时才会激活 enter/exit：

```jsx
// 工作
<ViewTransition enter="auto" exit="auto">
  <div>内容</div>
</ViewTransition>

// 错误——div 包裹了 VT，抑制了 enter/exit
<div>
  <ViewTransition enter="auto" exit="auto">
    <div>内容</div>
  </ViewTransition>
</div>
```

---

## 使用视图过渡类进行样式设置

### 属性

值：`"auto"` (浏览器跨淡入淡出)、`"none"` (禁用)、`"class-name"` (自定义 CSS)，或 `{ [type]: value }` 用于类型特定动画。

```jsx
<ViewTransition default="none" enter="slide-in" exit="slide-out" share="morph" />
```

如果 `default` 是 `"none"`，除非明确列出，否则所有触发器都是关闭的。

### CSS 伪元素

- `::view-transition-old(.class)` — 出站快照
- `::view-transition-new(.class)` — 入站快照
- `::view-transition-group(.class)` — 容器
- `::view-transition-image-pair(.class)` — 旧 + 新对

有关现成的动画配方，请参阅 [references/css-recipes.md](references/css-recipes.md)。

---

## 过渡类型

使用 `addTransitionType` 标记过渡，以便 VT 可以根据上下文选择不同的动画。多次调用它以堆叠类型——树中的不同 VT 对不同的类型做出反应：

```jsx
startTransition(() => {
  addTransitionType('nav-forward');
  addTransitionType('select-item');
  router.push('/detail/1');
});
```

将类型映射到 CSS 类的对象传递。适用于 `enter`、`exit` **和** `share`：

```jsx
<ViewTransition
  enter={{ 'nav-forward': 'slide-from-right', 'nav-back': 'slide-from-left', default: 'none' }}
  exit={{ 'nav-forward': 'slide-to-left', 'nav-back': 'slide-to-right', default: 'none' }}
  share={{ 'nav-forward': 'morph-forward', 'nav-back': 'morph-back', default: 'morph' }}
  default="none"
>
  <Page />
</ViewTransition>
```

`enter` 和 `exit` 不必对称。例如，淡入但方向性滑动淡出：

```jsx
<ViewTransition
  enter={{ 'nav-forward': 'fade-in', 'nav-back': 'fade-in', default: 'none' }}
  exit={{ 'nav-forward': 'nav-forward', 'nav-back': 'nav-back', default: 'none' }}
  default="none"
>
```

**TypeScript:** `ViewTransitionClassPerType` 要求对象中有一个 `default` 键。

对于具有多个页面的应用，将类型键 VT 提取为可重用的包装器：

```jsx
export function DirectionalTransition({ children }: { children: React.ReactNode }) {
  return (
    <ViewTransition
      enter={{ 'nav-forward': 'nav-forward', 'nav-back': 'nav-back', default: 'none' }}
      exit={{ 'nav-forward': 'nav-forward', 'nav-back': 'nav-back', default: 'none' }}
      default="none"
    >
      {children}
    </ViewTransition>
  );
}
```

### `router.back()` 和浏览器后退按钮

`router.back()` 和浏览器后退/前进按钮不携带 **任何过渡类型**，因此类型键动画（方向性滑动）会解析为其 `default` 并不会播放——未标记的共享元素变形仍然适用。对于类型动画，请使用 `router.push()` 并带有明确的 URL。

### 类型与 Suspense

在导航期间类型可用，但在后续的 Suspense 揭示期间 **不可用**（分离的过渡，没有类型）。使用类型映射进行页面级 enter/exit；使用简单字符串属性进行 Suspense 揭示。

### 共享元素就绪

共享元素过渡只能在旧视图和新视图在同一个过渡中渲染时才配对元素。如果传入的内容挂起，则只有其回退存在于此更新中；解析的内容会在后续的 Suspense 过渡中出现，并可以单独动画。

---

## 共享元素过渡

两个 VT 上具有相同的 `name`——一个卸载，一个挂载——会创建一个共享元素变形：

```jsx
<ViewTransition name="hero-image">
  <img src="/thumb.jpg" onClick={() => startTransition(() => onSelect())} />
</ViewTransition>

// 在另一个视图上——相同的名称
<ViewTransition name="hero-image">
  <img src="/full.jpg" />
</ViewTransition>
```

- 每个给定 `name` 的 VT 只能挂载一次——使用唯一名称 (`photo-${id}`)。注意可重用组件：如果具有命名 VT 的组件在模态/弹出框 *和* 页面上都渲染，则两者会同时挂载并破坏变形。要么使名称有条件（通过属性），要么将命名的 VT 从共享组件中移出并放入特定消费者中。
- `share` 优先于 `enter`/`exit`。考虑每个导航路径：当没有匹配的对形成时（例如，目标页面没有相同的名称），`enter`/`exit` 会触发。考虑元素是否需要为这些路径提供回退动画。
- 有两种方式使配对的变形无声地不触发：(1) `default="none"` 且没有显式的 `share` 属性——共享解析为无；(2) 类型键 `share`，其中导航从未添加类型——普通链接点击解析了映射的 `default`。每个应该变形的链接都必须添加类型 (`transitionTypes` 在 `next/link` 上，或 `addTransitionType`)。
- 永远不要在具有共享变形的页面上使用淡出退出——使用方向性滑动。

---

## 常见模式

### Enter/Exit

```jsx
{show && (
  <ViewTransition enter="fade-in" exit="fade-out"><Panel /></ViewTransition>
)}
```

### 列表重新排序

```jsx
{items.map(item => (
  <ViewTransition key={item.id}><ItemCard item={item} /></ViewTransition>
))}
```

在 `startTransition` 内部触发。避免在列表和 VT 之间使用包装 `<div>`。

### 布局位移变形

只有激活边界内的内容会动画位置——其他所有内容会传送至其新布局位置。将同级内容包裹在正在增长/缩小的列表下方的一个裸 `<ViewTransition>` 中，使其滑动而不是跳跃。参见 [Layout Displacement Morph](references/patterns.md#layout-displacement-morph)。

### 组合共享元素与列表身份

共享元素和列表身份是独立的问题——不要混淆它们。当列表项包含共享元素（例如，一个变形为详情视图的图像）时，使用两个嵌套的 `<ViewTransition>` 边界：

```jsx
{items.map(item => (
  <ViewTransition key={item.id}>                                      {/* 列表身份 */}
    <Link href={`/items/${item.id}`}>
      <ViewTransition name={`item-image-${item.id}`} share="morph">   {/* 共享元素 */}
        <Image src={item.image} />
      </ViewTransition>
      <p>{item.name}</p>
    </Link>
  </ViewTransition>
))}
```

外部 VT 处理列表重新排序/进入动画。内部 VT 处理跨路由的共享元素变形。缺少任何一层都意味着动画无声地不会发生。

### 使用 `key` 强制重新进入

```jsx
<ViewTransition key={searchParams.toString()} enter="slide-up" default="none">
  <ResultsGrid />
</ViewTransition>
```

**注意：** 如果包装 `<Suspense>`，更改 `key` 会重新挂载边界并重新获取。

### Suspense 回退到内容

简单的跨淡入淡出：
```jsx
<ViewTransition>
  <Suspense fallback={<Skeleton />}><Content /></Suspense>
</ViewTransition>
```

方向性揭示：
```jsx
<Suspense fallback={<ViewTransition exit="slide-down"><Skeleton /></ViewTransition>}>
  <ViewTransition enter="slide-up" default="none"><Content /></ViewTransition>
</Suspense>
```

更多模式，请参阅 [references/patterns.md](references/patterns.md)。

---

## 多个 VT 如何交互

每个匹配触发器的 VT 在单个 `document.startViewTransition` 中同时触发。不同过渡中的 VT（导航与后续 Suspense 解析）不会竞争。

### 故意使用 `default="none"`

如果没有它，每个 VT 都会在 **每个** 过渡中触发浏览器的跨淡入淡出——Suspense 解析，`useDeferredValue` 更新，背景重新验证。对命名的共享元素和类型键页面 VT 使用 `default="none"`。

但它也关闭了 `update`（布局/回流变形）和 `share`（没有显式 `share` 属性的命名对永远不会变形）。键列表项和位移同级元素 *希望* `update`——将它们保持裸露或设置 `update="auto"`。

### 两种模式共存

**模式 A — 方向性滑动：** 每个页面上的类型键 VT，在导航期间触发。
**模式 B — Suspense 揭示：** 简单字符串属性，在数据加载时触发（无类型）。

它们共存是因为它们在不同的时刻触发。`default="none"` 对两者都使用，以防止相互干扰。始终将 `enter` 与 `exit` 配对。将方向性 VT 放在页面组件中，而不是布局中。

### 嵌套 VT 限制

当父 VT 作为整体挂载/卸载，嵌套 VT 在其中时，嵌套的 VT 不会触发自己的 enter/exit——只有最外层的 VT 会动画。（在持久父 VT 内挂载的子 VT 正常触发 enter/exit。）在 Next.js 中，页面导航期间的逐项交错动画目前不可用；参见 [troubleshooting](references/troubleshooting.md) 了解上游实验状态。

---

## Next.js 集成

有关 Next.js 集成（`transitionTypes` 在 `next/link` 和 `useRouter` 上，App Router 模式，服务器组件），请参阅 [references/nextjs.md](references/nextjs.md)。

---

## 可访问性

始终将来自 [references/css-recipes.md](references/css-recipes.md#reduced-motion) 的减少运动 CSS 添加到您的全局样式表中。

---

## 参考文件

- **[references/implementation.md](references/implementation.md)** — 步骤实现工作流程。
- **[references/patterns.md](references/patterns.md)** — 模式、动画时间以及事件 API。
- **[references/troubleshooting.md](references/troubleshooting.md)** — 基于症状的调试和运行时限制。
- **[references/css-recipes.md](references/css-recipes.md)** — 现成的 CSS 动画配方。
- **[references/nextjs.md](references/nextjs.md)** — Next.js App Router 模式和服务器组件详细信息。

## 完整编译文档

有关包含所有参考文件的完整指南：`AGENTS.md`
