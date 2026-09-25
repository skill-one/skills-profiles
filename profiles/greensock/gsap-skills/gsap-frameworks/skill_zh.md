# 使用 GSAP 与 Vue、Svelte 及其他框架

## 何时使用此技能

在 Vue（或 Nuxt）、Svelte（或 SvelteKit）或其他使用生命周期（挂载/卸载）的组件框架中编写或审查 GSAP 代码时使用。对于 **React** 特定情况，请使用 **gsap-react**（useGSAP 钩子、gsap.context()）。

**相关技能**：对于缓动和时间轴使用 **gsap-core** 和 **gsap-timeline**；对于基于滚动的动画使用 **gsap-scrolltrigger**；对于 React 使用 **gsap-react**。

## 原则（所有框架）

- **在**组件的 DOM 可用时创建缓动和 ScrollTriggers（例如 onMounted、onMount）。
- 在 **卸载**（或等效）清理中**销毁或还原**它们，以便在分离的节点上不运行任何内容，并且没有泄漏。
- **将选择器作用域**限制在组件根，以便 `.box` 和类似选择器仅匹配该组件内的元素，而不是页面的其他部分。

## Vue 3 (Composition API)

查看 `examples/vue/` 目录，其中包含一个可运行的 Vite + Vue 3 项目，展示了这些模式。

使用 **onMounted** 在组件进入 DOM 后运行 GSAP，使用 **onUnmounted** 进行清理。

```javascript
import { onMounted, onUnmounted, ref } from "vue";
import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
gsap.registerPlugin(ScrollTrigger); // 每个应用中只需注册一次，例如在 main.js 中

export default {
  setup() {
    const container = ref(null);
    let ctx;

    onMounted(() => {
      if (!container.value) return;
      ctx = gsap.context(() => {
        gsap.to(".box", { x: 100, duration: 0.6 });
        gsap.from(".item", { autoAlpha: 0, y: 20, stagger: 0.1 });
      }, container.value);
    });

    onUnmounted(() => {
      ctx?.revert();
    });

    return { container };
  },
};
```

- ✅ **gsap.context(scope)** — 将容器引用（例如 `container.value`）作为第二个参数传递，以便像 `.item` 这样的选择器作用域限制在该根。在回调中创建的所有动画和 ScrollTriggers 都会被跟踪，并在调用 **ctx.revert()** 时被还原。
- ✅ **onUnmounted** — 始终调用 **ctx.revert()**，以便销毁缓动和 ScrollTriggers 并还原内联样式。

## Vue 3 (script setup)

使用 `<script setup>` 和引用，具有相同的概念：

```javascript
<script setup>
import { onMounted, onUnmounted, ref } from "vue";
import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

const container = ref(null);
let ctx;

onMounted(() => {
  if (!container.value) return;
  ctx = gsap.context(() => {
    gsap.to(".box", { x: 100 });
    gsap.from(".item", { autoAlpha: 0, stagger: 0.1 });
  }, container.value);
});

onUnmounted(() => {
  ctx?.revert();
});
</script>

<template>
  <div ref="container">
    <div class="box">Box</div>
    <div class="item">Item</div>
  </div>
</template>
```

## Nuxt 4

> 查看 `examples/nuxt/` 目录，其中包含一个可运行的 Nuxt 4 项目，展示了插件注册、懒加载和 SSR 安全模式。

使用一个**可重用的组合式 API**来注册 GSAP 插件，并用于懒加载应用程序中不常用的一些插件：

```typescript
// composables/useGSAP.ts
import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

const PLUGINS = [
  "CSSRulePlugin",
  "CustomBounce",
  "CustomEase",
  "CustomWiggle",
  "Draggable",
  "DrawSVGPlugin",
  "EaselPlugin",
  "EasePack",
  "Flip",
  "GSDevTools",
  "InertiaPlugin",
  "MorphSVGPlugin",
  "MotionPathHelper",
  "MotionPathPlugin",
  "Observer",
  "Physics2DPlugin",
  "PhysicsPropsPlugin",
  "PixiPlugin",
  "ScrambleTextPlugin",
  "ScrollSmoother",
  "ScrollToPlugin",
  "ScrollTrigger",
  "SplitText",
  "TextPlugin",
] as const;

type Plugins = (typeof PLUGINS)[number];

// 为了动态加载所有 GSAP 插件
const pluginMap = {
  CustomEase: () => import("gsap/CustomEase"),
  Draggable: () => import("gsap/Draggable"),
  CSSRulePlugin: () => import("gsap/CSSRulePlugin"),
  EaselPlugin: () => import("gsap/EaselPlugin"),
  EasePack: () => import("gsap/EasePack"),
  Flip: () => import("gsap/Flip"),
  MotionPathPlugin: () => import("gsap/MotionPathPlugin"),
  Observer: () => import("gsap/Observer"),
  PixiPlugin: () => import("gsap/PixiPlugin"),
  ScrollToPlugin: () => import("gsap/ScrollToPlugin"),
  ScrollTrigger: () => import("gsap/ScrollTrigger"),
  TextPlugin: () => import("gsap/TextPlugin"),
  DrawSVGPlugin: () => import("gsap/DrawSVGPlugin"),
  Physics2DPlugin: () => import("gsap/Physics2DPlugin"),
  PhysicsPropsPlugin: () => import("gsap/PhysicsPropsPlugin"),
  ScrambleTextPlugin: () => import("gsap/ScrambleTextPlugin"),
  CustomBounce: () => import("gsap/CustomBounce"),
  CustomWiggle: () => import("gsap/CustomWiggle"),
  GSDevTools: () => import("gsap/GSDevTools"),
  InertiaPlugin: () => import("gsap/InertiaPlugin"),
  MorphSVGPlugin: () => import("gsap/MorphSVGPlugin"),
  MotionPathHelper: () => import("gsap/MotionPathHelper"),
  ScrollSmoother: () => import("gsap/ScrollSmoother"),
  SplitText: () => import("gsap/SplitText"),
} as const;

type PluginMap = typeof pluginMap;
type Plugins = keyof PluginMap;

// 解析给定键的模块类型，然后选择匹配该键的命名导出
// 这允许在代码编辑器中获得自动补全的类型定义
type PluginModule<K extends Plugins> = Awaited<ReturnType<PluginMap[K]>>;
type PluginExport<K extends Plugins> = PluginModule<K>[K & keyof PluginModule<K>];

export default function () {
  // 在此位置注册您想要的所有 GSAP 插件
  gsap.registerPlugin(ScrollTrigger);

  /*
    如果您想懒加载应用程序中不常用的一些插件（例如仅在几个组件或单个路由中使用），您可以使用此方法
  */
  async function lazyLoadPlugin<K extends Plugins>(plugin: K): Promise<PluginExport<K>> {
    const loader = pluginMap[plugin];
    const m = await loader();
    const p = (m as any)[plugin];
    gsap.registerPlugin(p);
    return p;
  }

  return {
    gsap,
    ScrollTrigger,
    lazyLoadPlugin,
  };
}
```

在组件中通过 `useGSAP()` 访问：

```javascript
const { gsap, ScrollTrigger, lazyLoadPlugin } = useGSAP();
```

- ✅ **`useGSAP()`** 提供对 gsap 实例和懒加载方法的类型化访问。
- ✅ **懒加载任何插件**（SplitText、MorphSVG 等）以减少初始包大小，这些插件在应用程序中不常用。
- ✅ 在组件中使用 **gsap.context(scope)** 和 **onUnmounted → ctx.revert()**，与 Vue 3 相同。

## Svelte

使用 **onMount** 在 DOM 准备就绪后运行 GSAP。使用 onMount 返回的**清理函数**（或在响应式块/组件销毁中跟踪上下文并清理）来还原。Svelte 5 使用不同的生命周期；相同的原理适用：在“挂载”时创建，在“销毁”时还原。

```javascript
<script>
  import { onMount } from "svelte";
  import { gsap } from "gsap";
  import { ScrollTrigger } from "gsap/ScrollTrigger";

  let container;

  onMount(() => {
    if (!container) return;
    const ctx = gsap.context(() => {
      gsap.to(".box", { x: 100 });
      gsap.from(".item", { autoAlpha: 0, stagger: 0.1 });
    }, container);
    return () => ctx.revert();
  });
</script>

<div bind:this={container}>
  <div class="box">Box</div>
  <div class="item">Item</div>
</div>
```

- ✅ **bind:this={container}** — 获取对根元素的引用，以便将其传递给 **gsap.context(scope)**。
- ✅ **return () => ctx.revert()** — Svelte 的 onMount 可以返回一个清理函数；在 **ctx.revert()** 中调用它，以便在组件销毁时运行清理。

## 选择器作用域

不要使用全局选择器，这些选择器可能会匹配当前组件外的元素。始终将 **作用域**（容器元素或引用）作为 **gsap.context(callback, scope)** 的第二个参数传递，以便在回调中运行的任何选择器都限制在该子树内。

- ✅ **gsap.context(() => { gsap.to(".box", ...) }, containerRef)** — `.box` 仅在 `containerRef` 内搜索。
- ❌ 在组件中运行 **gsap.to(".box", ...)** 而没有上下文作用域可能会影响其他实例或页面的其余部分。

## ScrollTrigger 清理

当您在缓动/时间轴上使用 `scrollTrigger` 配置或 **ScrollTrigger.create()** 时，会创建 ScrollTrigger 实例。它们**包含**在 **gsap.context()** 中，并在调用 **ctx.revert()** 时被还原。因此：

- 在您用于缓动的相同 **gsap.context()** 回调中创建 ScrollTriggers。
- 在影响触发位置的布局更改后调用 **ScrollTrigger.refresh()**；在 Vue/Svelte 中，这通常意味着在 DOM 更新后（例如 Vue 中的 nextTick、Svelte 中的 tick 或异步内容加载后）。

## 创建与销毁的时机

| 生命周期     | 操作                                                                                                        |
| ------------ | ---------------------------------------------------------------------------------------------------------- |
| **挂载**     | 在 **gsap.context(scope)** 内创建缓动和 ScrollTriggers。                                                    |
| **卸载/销毁** | 调用 **ctx.revert()**，以便在该上下文中所有动画和 ScrollTriggers 都被销毁并还原内联样式。                     |

不要在组件的 setup 中或在根元素存在之前运行的同步顶层脚本中创建 GSAP 动画。等待 **onMounted** / **onMount**（或等效）以便容器引用在 DOM 中。

## 不要

- ❌ 在组件挂载之前创建缓动或 ScrollTriggers（例如在 setup 中没有 onMounted）；DOM 节点可能还不存在。
- ❌ 使用没有 **作用域** 的选择器字符串（将容器传递给 gsap.context() 作为第二个参数），以便选择器不会匹配组件外的元素。
- ❌ 跳过清理；始终在 onUnmounted / onMount 的返回值中调用 **ctx.revert()**，以便在组件销毁时销毁动画和 ScrollTriggers。
- ❌ 在每次渲染时运行（组件体）中注册插件（它不会造成任何伤害，只是浪费）；在应用级别注册一次。

### 了解更多

- **gsap-react** 技能，用于 React 特定模式（useGSAP、contextSafe）。
