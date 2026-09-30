---
name: page-transition-animation
description: 当用户要求“动画化页面或路由过渡”、“在视图之间添加页面过渡或交叉淡入淡出”、“动画化 Next.js 应用路由中的路由更改”、“使用视图过渡 API”、“AnimatePresence 在导航时未触发退出动画”或“Framer Motion 退出动画不工作 / 在 Next.js 中卸载前的退出动画”时，应使用此技能。它涵盖了使用视图过渡 API 和 Framer Motion 进行的页面进入/退出过渡动画，适用于 Next.js 应用路由和通用 SPA 路由。
---

# 页面过渡动画 (Next.js 应用路由器)

在 Next.js **应用路由器**中实现页面进入/退出过渡，并修复最常见的一个问题：**Framer Motion 的 `AnimatePresence` 退出动画在导航时从未触发**。原因是结构性的——在应用路由器中，当导航时，Next.js 会卸载旧路由的内容并几乎立即挂载新内容。`AnimatePresence` 只能在退出元素在持久化的 `AnimatePresence` 包装器下保持挂载足够长的时间来运行动画时才能进行动画。因为路由器会从其下方交换子元素，所以会跳过退出。有两种方法可以解决这个问题：路径名键控的 `AnimatePresence` 与 **FrozenRouter** 模式，或 **视图过渡 API** (原生 / `next-view-transitions`)。

## 使用场景

在 Next.js 应用路由器应用中添加动画页面过渡时使用，当 Framer Motion 的 `exit` 属性在路由更改时无任何作用时使用，当旧页面立即消失而不是动画退出时使用，当在 Framer Motion 和视图过渡 API 之间为 Next.js 进行选择时使用，或当调试 `AnimatePresence` 为什么不会在路由之间进行动画时使用。

## 退出不触发的原因（核心问题）

`AnimatePresence` 检测到直接键控子元素的移除。在应用路由器导航时：

1. 包装器必须在导航过程中保持持久。如果 `AnimatePresence` 生活在自身会卸载的组件中，则没有东西来运行退出动画。
2. 子元素的 `key` 必须按路由更改，以便 AnimatePresence 看到“旧移除，新添加”。
3. 在短暂的重叠期间，*正在退出的*子树必须仍然渲染其旧内容——但应用路由器已经交换了路由上下文，所以正在退出的树原本会渲染*新*页面的数据。这就是 **FrozenRouter** 修复的问题。

## 解决方案 A：template.tsx + 键控 AnimatePresence + FrozenRouter

`template.tsx` 是应用路由器为此专门构建的钩子：与 `layout.tsx`（它保持持久）不同，**template** 在每次导航时都会重新挂载，为每个路由提供一个新鲜实例——非常适合按路由的进入动画。将其与路径名键控的 `AnimatePresence` 和 FrozenRouter 结合使用，以实现干净的退出和进入。

```tsx
// app/template.tsx
'use client';
import { AnimatePresence } from 'framer-motion';
import { usePathname } from 'next/navigation';
import { FrozenRouter } from './frozen-router';
import { PageTransition } from './page-transition';

export default function Template({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  return (
    <AnimatePresence mode="wait" initial={false}>
      {/* 以路径名为 key，以便 AnimatePresence 检测到旧内容移除 / 新内容添加 */}
      <PageTransition key={pathname}>
        {/* FrozenRouter 保持正在退出的树在动画期间渲染其旧内容 */}
        <FrozenRouter>{children}</FrozenRouter>
      </PageTransition>
    </AnimatePresence>
  );
}
```

```tsx
// app/page-transition.tsx
'use client';
import { motion } from 'framer-motion';

export function PageTransition({ children }: { children: React.ReactNode }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -12 }}
      transition={{ duration: 0.3, ease: [0.22, 1, 0.36, 1] }}
    >
      {children}
    </motion.div>
  );
}
```

```tsx
// app/frozen-router.tsx
'use client';
import { useContext, useRef } from 'react';
import {
  LayoutRouterContext,
} from 'next/dist/shared/lib/app-router-context.shared-runtime';

// 冻结路由上下文，以便退出页面在退出动画期间渲染其自己的内容，而不是下一个路由的内容。
export function FrozenRouter({ children }: { children: React.ReactNode }) {
  const context = useContext(LayoutRouterContext ?? {}).current;
  const frozen = useRef(context).current;

  return (
    <LayoutRouterContext.Provider value={frozen}>
      {children}
    </LayoutRouterContext.Provider>
  );
}
```

它们如何协同工作：

- `mode="wait"` 使 AnimatePresence 在挂载新页面之前完全完成退出动画。（如果进入/退出应该重叠/交叉渐变，请使用默认模式。）
- `initial={false}` 在首次加载时跳过进入动画（可选）。
- `key={pathname}` 是使 AnimatePresence 将每个路由视为独特存在的原因。
- `FrozenRouter` 快照 `LayoutRouterContext`，以便正在退出的子树在整个退出期间渲染*上一个*路由的内容，而不是闪现新路由的内容。没有它，退出要么被跳过，要么显示错误的内容。

注意：`LayoutRouterContext` 是 Next.js 的内部；其导入路径可能在 Next 版本之间发生变化。如果升级后导入中断，则需要更新该路径。

## 解决方案 B：原生视图过渡 API

视图过渡 API 通过浏览器捕获前后快照来在两个 DOM 状态之间进行动画，无需每个元素的退出组件。

```css
/* globals.css */
@view-transition { navigation: auto; } /* 在支持的情况下选择 MPA 风格 */

::view-transition-old(root) { animation: fade 0.25s both reverse; }
::view-transition-new(root) { animation: fade 0.25s both; }
@keyframes fade { from { opacity: 0; } to { opacity: 1; } }
```

对于 SPA 风格的应用路由器导航，请包装路由更新：

```ts
if (document.startViewTransition) {
  document.startViewTransition(() => router.push(href));
} else {
  router.push(href);
}
```

### next-view-transitions 库

`next-view-transitions` 将视图过渡 API 与应用路由器的客户端导航集成，因此可以开箱即用：

```tsx
// app/layout.tsx
import { ViewTransitions } from 'next-view-transitions';
export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <ViewTransitions>
      <html lang="en"><body>{children}</body></html>
    </ViewTransitions>
  );
}
```

```tsx
// 使用库的 Link 而不是 next/link
import { Link } from 'next-view-transitions';
<Link href="/about">About</Link>;
```

选择视图过渡进行简单的跨页面淡入/淡出/变形和共享元素过渡，并使用最少的 JS；选择 Framer Motion 当需要细粒度、编排、可中断或交错退出动画时。视图过渡 API 的浏览器支持仍然不均衡，因此始终提供优雅的回退（`if (document.startViewTransition)` 防护）。

## AnimatePresence 调试清单

当退出仍然不会触发时，按顺序验证：

1. **包装器保持挂载**。`AnimatePresence` 必须存在于持久化的东西中——最好是 `template.tsx`，或一个布局级别的客户端组件——而不是正在卸载的页面内部。
2. **稳定的、变化的 key**。动画子元素需要 `key={pathname}`（或类似）以便检测到移除。没有 key，或 key 不变化→没有退出。
3. **直接 motion 子元素**。具有 `exit` 属性的元素必须是 `motion.*` 组件，并且是 `AnimatePresence` 的子元素（中间的非 motion 包装器可能会阻止检测）。
4. **`mode="wait"`** 如果旧页面和新页面不应重叠；没有它，两者会同时渲染，可能会跳转。
5. **FrozenRouter 存在** 如果正在退出的页面在退出期间闪现新路由的内容。
6. **`'use client'`** 在每个使用 AnimatePresence/usePathname/motion 的文件上。
7. **一次只有一个子元素** 在 `mode="wait"` 下——AnimatePresence 期望一个键控存在来交换。

## 交付和验证（独立的 HTML）

> **打包辅助工具** (`scripts/`)：`scripts/seek-shot.sh anim.html 0 1.5 3` 冻结 `?t=N` 扼杀器并捕获每个时刻的屏幕截图；`scripts/contact-sheet.sh sheet.png frame-*.png` 将它们平铺以供一目了然地查看。参见 `scripts/README.md`。

真实的目标是一个 Next.js 应用，但为了*证明过渡形状*（进入/退出的曲线、方向、交叉渐变），您可以发送**一个可以直接在浏览器中打开的 HTML 文件**——两个 stub "页面"您可以切换，使用 `motion` 从 CDN 或原生视图过渡 API 进行动画。一个文件是验证动画的正确级别，在连接路由之前不要启动 Next.js，只是观察淡入淡出。

**输出合同：**
- 一个 `.html` 文件：两个视图 stub 和一个切换器，使用 CDN 的 `motion`/React 的内联 `<script type="module">` 或 `document.startViewTransition` + `::view-transition-*` CSS 进行动画。
- 一种冻结**解析的最终状态**的方法——路由过渡是状态驱动的（哪个视图，在交换期间），所以捕获状态，而不是时钟。

**Seek harness — 固定一个过渡阶段。** `?view=b` 挂载目标视图（或 `?phase=exit` 以在动画期间挂载正在退出的树）以便屏幕截图落在已解决的阶段：

```html
<script>
  const p = new URLSearchParams(location.search);
  document.documentElement.dataset.view = p.get("view") || "a";   // CSS/React 基于 this
  // Framer Motion：从 ?view 设置受控的 key/route；对于 mode="wait"，解析的最终状态是新页面
  // 视图过渡：捕获最终状态（快照是瞬时的）；或通过模拟慢速动画来暂停
  window.__ready = true;
</script>
```

**验证循环——渲染 → 设置阶段 → 屏幕截图 → 检查：** 打开源、中、目标 (`?view=a`, `?phase=exit`, `?view=b`)，屏幕截图每个，并检查**保真度**（退出确实运行，方向/交叉渐变与简报匹配，没有 `mode="wait"` 滞后）加上**伪影**（正在退出的页面闪现新页面的内容，双挂载，FOUC，卡顿）。任何无头工具都可以工作：

```bash
npx playwright screenshot --wait-for-timeout=500 "file://$PWD/transition.html?view=b" dest.png
```

**在您完成之前：**
1. 独立打开——没有控制台错误，CDN `motion`/React（如果使用）解析，`startViewTransition` 受保护。
2. `?view=`/`?phase=` 冻结落在确定性过渡阶段。
3. 屏幕截图在源 / 中 / 目标——与简报匹配，没有内容闪现或跳过的退出。
4. 尊重 `prefers-reduced-motion`——滑块/平移降级为短交叉渐变。
5. 缓动是故意的——进入缓出，退出缓入，持续时间 ~0.2–0.4s（在 `mode="wait"` 下不会滞后）。

## 快速参考

| 需要 | 方法 |
|---|---|
| 按路由进入动画 | `app/template.tsx`（每次导航重新挂载） |
| 导航时的退出动画 | 键控 `AnimatePresence mode="wait"` + FrozenRouter |
| 正在退出的页面显示旧内容 | FrozenRouter（快照 `LayoutRouterContext`） |
| 检测路由更改 | `usePathname()` 作为 `key` |
| 简单的跨页面淡入/淡出 | 视图过渡 API / next-view-transitions |
| 共享元素过渡 | `view-transition-name` CSS |
| 跳过首次加载动画 | `initial={false}` |

## 注意事项

- `layout.tsx` 保持持久，并且**不会**按路由重新挂载——用于按路由的进入动画，请使用 `template.tsx`。
- 省略 FrozenRouter 会使正在退出的页面在动画期间渲染*新*路由的内容（可见闪现）或完全跳过退出。
- `LayoutRouterContext` 导入路径是 Next 的内部；它可能在版本之间发生变化——升级后首先要修复的是该路径。
- 没有 `key={pathname}`，AnimatePresence 看到相同的子元素，并且永远不会触发退出。
- `mode="wait"` 等待退出后再进入；在慢速退出上过度使用它会使导航感觉滞后——调整持续时间 (~0.2-0.4s)。
- 视图过渡 API 缺乏完整的浏览器支持；始终使用 `document.startViewTransition` 进行防护。
- 每个过渡文件都需要 `'use client'`；服务器组件不能使用 AnimatePresence/usePathname。

## 参考文件

- `references/full-examples.md` — 方向性/滑动过渡，具有 `view-transition-name` 的共享元素视图过渡，非 `mode="wait"` 的交叉渐变变体，使用 `loading.tsx` 的加载状态过渡，以及一个完整的、可工作的应用路由器文件夹布局。
