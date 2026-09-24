# React View Transitions

使用浏览器的原生 `document.startViewTransition` 在不同 UI 状态之间进行动画。使用 `<ViewTransition>` 声明 *什么*，在 *何时* 触发使用 `startTransition` / `useDeferredValue` / `Suspense`，通过 CSS 类控制 *如何*。不支持的浏览器会优雅地跳过动画。

## 何时进行动画

每个 `<ViewTransition>` 都应该传达一种空间关系或连续性。如果你无法说明它传达了什么，就不要添加它。

按照以下顺序实现 **所有** 适用的模式：

| 优先级 | 模式 | 传达的内容 |
|--------|------|------------|
| 1 | **共享元素**（`name`） | "相同内容——深入其中" |
| 2 | **Suspense 展现** | "数据已加载" |
| 3 | **列表身份**（单条目 `key`） | "相同条目，新排列" |
| 4 | **状态变化**（`enter`/`exit`） | "出现了/消失的内容" |
| 5 | **路由变化**（页面级） | "前往新地方" |

这是实现顺序，不是"选择一个"的列表。实现所有适用于该应用的模式。只有在应用没有相关使用场景时，才可以跳过某个模式。

### 选择动画样式

| 场景 | 动画 | 原因 |
|------|------|------|
| 层级导航（列表 → 详情） | 类型键控的 `nav-forward` / `nav-back` | 传达空间深度 |
| 横向导航（标签页间） | 无包裹的 `<ViewTransition>`（淡入淡出）或 `default="none"` | 无空间深度可传达 |
| Suspense 展现 | `enter`/`exit` 字符串属性 | 内容到达 |
| 重新验证 / 后台刷新 | `default="none"` | 静默——无需动画 |

将方向性滑动仅保留用于层级导航（列表 → 详情）和有序序列（上一张/下一张照片、轮播图、分页结果）。对于有序序列，方向传达位置："下一张"从右侧滑动，"上一张"从左侧滑动。横向/无序导航（标签页间）不应使用方向性滑动——这会错误地暗示空间深度。

---

## 可用性

- **Next.js：** **不要**安装 `react@canary` —— App Router 已在内部捆绑 React canary。`ViewTransition` 开箱即用。`npm ls react` 可能会显示一个看似稳定的版本；这是预期的。
- **不使用 Next.js：** 安装 `react@canary react-dom@canary`（`ViewTransition` 不在稳定的 React 中）。
- 浏览器支持：Chromium 125+（React 需要 `startViewTransition` 的 v2 对象形式），Firefox 144+，Safari 18.2+。不支持浏览器的降级处理为优雅降级。

---

## 实现工作流程

在现有应用中添加视图过渡时，**按照 [references/implementation.md](references/implementation.md) 的步骤逐步执行。** 从审计开始——不要跳过它。使用 [references/css-recipes.md](references/css-recipes.md) 获取适用的 CSS，并适配到应用中。

---

## 核心概念

### `<ViewTransition>` 组件

```jsx
import { ViewTransition } from 'react';

<ViewTransition>
  <Component />
</ViewTransition>
```

React 会自动分配唯一的 `view-transition-name` 并在后台调用 `document.startViewTransition`。永远不要自行调用 `startViewTransition`。

### 动画触发器

| 触发器 | 触发时机 |
|--------|----------|
| **enter** | 在 Transition 期间首次插入的 `<ViewTransition>` |
| **exit** | 在 Transition 期间首次移除的 `<ViewTransition>` |
| **update** | 在 `<ViewTransition>` 内部发生的 DOM 变更，或边界本身因立即的兄弟节点而变化尺寸/位置。对于嵌套 VT，变更作用于最内层的那个 |
| **share** | 命名 VT 卸载，而同 Transition 中相同 `name` 的另一个 VT 挂载 |

只有 `startTransition`、`useDeferredValue` 或 `Suspense` 会激活 VT。普通的 `setState` 不会进行动画。

### 关键放置规则

`<ViewTransition>` 只有在 **在任意 DOM 节点之前** 出现时，才会激活 enter/exit：

```jsx
// 有效
<ViewTransition enter="auto" exit="auto">
  <div>内容</div>
</ViewTransition>

// 无效——div 包裹了 VT，抑制了 enter/exit
<div>
  <ViewTransition enter="auto" exit="auto">
    <div>内容</div>
  </ViewTransition>
</div>
```

---

## 使用 View Transition 类进行样式设置

### 属性

取值：`"auto"`（浏览器跨淡）、`"none"`（禁用）、`"class-name"`（自定义 CSS），或 `{ [type]: value }` 用于类型特定动画。

```jsx
<ViewTransition default="none" enter="slide-in" exit="slide-out" share="morph" />
```

如果 `default` 为 `"none"`，则除非显式列出，所有触发器都会关闭。

### CSS 伪元素

- `::view-transition-old(.class)` —  outgoing snapshot（出发快照）
- `::view-transition-new(.class)` — incoming snapshot（到来快照）
- `::view-transition-group(.class)` — 容器
- `::view-transition-image-pair(.class)` — old + new 配对

参见 [references/css-recipes.md](references/css-recipes.md) 获取即用型动画配方。

---

## 过渡类型

通过 `addTransitionType` 为过渡打上 `addTransitionType` 标签，以便 VT 可以根据上下文选择不同动画：

```jsx
startTransition(() => {
  addTransitionType('nav-forward');
  addTransitionType('select-item');
  router.push('/detail/1');
});
```

传入对象可将类型映射到 CSS 类。适用于 `enter`、`exit` 以及 **`share`**：

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

`enter` 和 `exit` 不必对称。例如，淡入但方向性滑动退出：

```jsx
<ViewTransition
  enter={{ 'nav-forward': 'fade-in', 'nav-back': 'fade-in', default: 'none' }}
  exit={{ 'nav-forward': 'nav-forward', 'nav-back': 'nav-back', default: 'none' }}
  default="none"
>
```

**TypeScript：** `ViewTransitionClassPerType` 要求对象中包含 `default` 键。

对于多页面应用，将类型键控的 VT 提取为可复用的包装器：

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

`router.back()` 和浏览器的后退/前进按钮不携带 **过渡类型**，因此类型键控动画（方向性滑动）解析为其 `default` 且不播放——未类型化的共享元素变形仍会应用。对于类型化动画，使用带显式 URL 的 `router.push()`。

### 类型与 Suspense

类型在导航期间可用，但 **不** 在随后的 Suspense 展现期间可用（独立的过渡，无类型）。使用类型映射进行页面级 enter/exit；使用简单字符串属性进行 Suspense 展现。

### 共享元素就绪状态

共享元素过渡只能在旧视图和新视图均在同一个 Transition 中渲染时，才能将元素配对。如果 incoming 内容发生挂起，只有其兜底版本存在于该更新中；解析后的内容出现在稍后的 Suspense 过渡中，并可单独进行动画。

---

## 共享元素过渡

相同 `name` 出现在两个 VT 上——一个卸载，一个挂载——会创建共享元素变形：

```jsx
<ViewTransition name="hero-image">
  <img src="/thumb.jpg" onClick={() => startTransition(() => onSelect())} />
</ViewTransition>

// 另一视图——相同 name
<ViewTransition name="hero-image">
  <img src="/full.jpg" />
</ViewTransition>
```

- 同一个 `name` 下只能同时挂载一个 VT —— 使用唯一名称（`photo-${id}`）。注意可复用组件：如果带有命名 VT 的组件同时在模态框/弹出层页面和页面中渲染，两者会同时挂载并破坏变形。要么使名称根据属性条件化，要么将命名 VT 从共享组件中移出，放入具体使用者中。
- `share` 优先于 `enter`/`exit`。逐一思考每条导航路径：当不形成匹配对时（例如，目标页面没有相同 name），`enter`/`exit` 会触发。考虑该元素在这些路径是否需要兜底动画。
- 两个方式使得配置好的变形始终静默不触发：(1) `default="none"` 且无显式 `share` 属性——share 解析为 none；(2) 类型键控的 `share`，而导航从未添加类型——普通链接点击解析映射的 `default`。每个应变形的链接都必须添加类型（`next/link` 上的 `transitionTypes`，或 `addTransitionType`）。
- 切勿在带有共享变形的页面上使用淡出退出——改用方向性滑动。

---

## 常见模式

### Enter/Exit

```jsx
{show && (
  <ViewTransition enter="fade-in" exit="fade-out"><Panel /></ViewTransition>
)}
```

### 列表重排

```jsx
{items.map(item => (
  <ViewTransition key={item.id}><ItemCard item={item} /></ViewTransition>
))}
```

在 `startTransition` 内部触发。避免列表与 VT 之间的包裹 `<div>`。

### 布局位移变形

只有已激活边界内的内容会动画位置——其他内容会被瞬间移至新的布局位置。将位于增长/缩小列表下方的内容用无包裹的 `<ViewTransition>` 包裹，使其滑动而非跳转。参见 [Layout Displacement Morph](references/patterns.md#layout-displacement-morph)。

### 共享元素与列表身份的组合

共享元素和列表身份是独立的问题——不要混淆二者。当列表条目包含共享元素（例如，会变形到详情视图的图片）时，使用两个嵌套的 `<ViewTransition>` 边界：

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

外层 VT 处理列表重排/进入动画。内层 VT 处理跨路由的共享元素变形。缺少任一层级意味着该动画不会发生。

### 使用 `key` 强制重新进入

```jsx
<ViewTransition key={searchParams.toString()} enter="slide-up" default="none">
  <ResultsGrid />
</ViewTransition>
```

**注意：** 如果包裹了 `<Suspense>`，更改 `key` 会重新挂载边界并重新获取。

### Suspense 兜底到内容

简单跨淡：
```jsx
<ViewTransition>
  <Suspense fallback={<Skeleton />}><Content /></Suspense>
</ViewTransition>
```

方向性展现：
```jsx
<Suspense fallback={<ViewTransition exit="slide-down"><Skeleton /></ViewTransition>}>
  <ViewTransition enter="slide-up" default="none"><Content /></ViewTransition>
</Suspense>
```

更多信息，参见 [references/patterns.md](references/patterns.md)。

---

## 多个 VT 如何交互

每个匹配触发器的 VT 在单个 `document.startViewTransition` 中同时触发。**不同** 过渡中的 VT（导航与稍后 Suspense 解析之间的过渡）不相互竞争。

### 有意使用 `default="none"`

如果不使用，每个 VT 会在 **每次** 过渡中对浏览器执行跨淡——Suspense 解析、`useDeferredValue` 更新、后台重新验证。在命名/共享元素和类型键控页面 VT 上使用 `default="none"`。

但它也关闭了 `update`（布局/重排变形）和 `share`（无显式 `share` 属性的命名配对永远不会变形）。带 `key` 的列表项和位移的兄弟节点 **需要** `update`——保留为裸属性或设置 `update="auto"`。

### 两种模式共存

**模式 A —— 方向性滑动：** 每个页面上的类型键控 VT，在导航期间触发。
**模式 B —— Suspense 展现：** 简单字符串属性，在数据加载时触发（无类型）。

它们共存，因为它们在不同时刻触发。两者都使用 `default="none"` 可防止交叉干扰。始终将 `enter` 与 `exit` 配对。将方向性 VT 放在页面组件中，而非布局中。

### 嵌套 VT 限制

当父 VT 与内部的嵌套 VT **作为整体** 挂载/卸载时，嵌套 VT 不会触发它们自己的 enter/exit——只有最外层的 VT 进行动画。（在 *持久* 父 VT 内部挂载的子 VT 正常触发 enter/exit。）页面导航期间的单条目交错动画在 Next.js 中目前不可用；参见 [troubleshooting](references/troubleshooting.md) 了解上游实验状态。

---

## Next.js 集成

对于 Next.js 集成（`next/link` 和 `useRouter` 上的 `transitionTypes`、App Router 模式、Server Components），参见 [references/nextjs.md](references/nextjs.md)。

---

## 可访问性

始终在全局样式中添加 [references/css-recipes.md](references/css-recipes.md#reduced-motion) 中的减少动态 CSS。

---

## 参考文件

- **[references/implementation.md](references/implementation.md)** — 分步实现工作流程。
- **[references/patterns.md](references/patterns.md)** — 模式、动画时序和事件 API。
- **[references/troubleshooting.md](references/troubleshooting.md)** — 基于症状的调试和运行时限制。
- **[references/css-recipes.md](references/css-recipes.md)** — 即用型 CSS 动画配方。
- **[references/nextjs.md](references/nextjs.md)** — Next.js App Router 模式和 Server Component 详情。

## 完整编译文档

包含所有参考文件展开的完整指南：`AGENTS.md`
