# GSAP与Vue、Svelte和其他框架

> 内容源自GreenSock官方GSAP技能：https://github.com/greensock/gsap-skills

## 何时使用此技能

在Vue（或Nuxt）、Svelte（或SvelteKit）或其他使用生命周期（挂载/卸载）的组件框架中编写或审查GSAP代码时使用。对于**React**，请使用**gsap-react**（useGSAP钩子、gsap.context()）。

**相关技能**：对于补间和 timelines 使用 **gsap-core** 和 **gsap-timeline**；对于基于滚动的动画使用 **gsap-scrolltrigger**；对于 React 使用 **gsap-react**。

## 原则（所有框架）

- **在组件的DOM可用后**创建补间和 ScrollTriggers（例如 onMounted、onMount）。
- 在**卸载**（或等效）清理中**销毁或还原**它们，以便在分离的节点上不运行任何内容，并且没有泄漏。
- **将选择器作用域限制**到组件根，以便 `.box` 和类似的选择器仅匹配该组件内的元素，而不是页面的其他部分。

## Vue 3（组合式API）

要查看一个可运行的Vite + Vue 3项目，其中展示了这些模式，请参阅上游示例：https://github.com/greensock/gsap-skills/tree/main/examples/vue。

使用 **onMounted** 在组件进入DOM后运行GSAP。使用 **onUnmounted** 进行清理。

```javascript
import { onMounted, onUnmounted, ref } from "vue";
import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
gsap.registerPlugin(ScrollTrigger); // 每个应用只注册一次，例如在 main.js 中

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

- ✅ **gsap.context(scope)** — 将容器引用（例如 `container.value`）作为第二个参数传递，以便像 `.item` 这样的选择器仅作用域于该根。在回调中创建的所有动画和 ScrollTriggers 都会被跟踪，并在 **ctx.revert()** 被调用时还原。
- ✅ **onUnmounted** — 始终调用 **ctx.revert()**，以便补间和 ScrollTriggers 被销毁，并且内联样式被还原。

## Vue 3（script setup）

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

> 要查看一个具有插件注册、懒加载和SSR安全模式的可运行Nuxt 4项目，请参阅：https://github.com/greensock/gsap-skills/tree/main/examples/nuxt。

使用一个**可重用的组合式函数**来注册GSAP插件，并且也可以用来懒加载应用程序中不经常使用的插件：

```typescript
// composables/useGSAP.ts
import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

// 为了动态加载所有GSAP插件
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
type LoadablePlugin = keyof PluginMap;

// 解析给定键的模块类型，然后选择匹配该键的命名导出
// 这允许在代码编辑器中获得自动补全的类型定义
type PluginModule<K extends LoadablePlugin> = Awaited<ReturnType<PluginMap[K]>>;
type PluginExport<K extends LoadablePlugin> = PluginModule<K>[K & keyof PluginModule<K>];

export default function () {
  // 在这一点上注册您想要的所有GSAP插件
  gsap.registerPlugin(ScrollTrigger);

  /*
    如果您想懒加载应用程序中不经常使用的某些插件（例如仅在几个组件或单个路由中使用），您可以使用此方法
  */
  async function lazyLoadPlugin<K extends LoadablePlugin>(plugin: K): Promise<PluginExport<K>> {
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
- ✅ **懒加载任何插件**（SplitText、MorphSVG等），这些插件在应用程序中不常用，以减少初始包大小。
- ✅ 在组件中使用 **gsap.context(scope)** 和 **onUnmounted → ctx.revert()**，与 Vue 3 相同。

## Svelte

使用 **onMount** 在DOM准备好后运行GSAP。使用 **onMount 返回的清理函数**（或跟踪上下文并在响应式块/组件销毁时清理）来还原。Svelte 5使用不同的生命周期；相同的原理适用：在“mounted”中创建，在“destroyed”中还原。

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

- ✅ **bind:this={container}** — 获取对根元素的引用，以便您可以将其传递给 **gsap.context(scope)**。
- ✅ **return () => ctx.revert()** — Svelte的 onMount 可以返回一个清理函数；在那里调用 **ctx.revert()**，以便在组件销毁时运行清理。

## 选择器作用域

不要使用可能匹配当前组件外元素的的全局选择器。始终将**作用域**（容器元素或引用）作为 **gsap.context(callback, scope)** 的第二个参数传递，以便在回调中运行的任何选择器都仅限于该子树。

- ✅ **gsap.context(() => { gsap.to(".box", ...) }, containerRef)** — `.box` 仅在 `containerRef` 内搜索。
- ❌ 在组件中运行 **gsap.to(".box", ...)** 而没有上下文作用域，可能会影响其他实例或页面的其余部分。

## ScrollTrigger 清理

当您在补间/timeline上使用 `scrollTrigger` 配置或 **ScrollTrigger.create()** 时，会创建 ScrollTrigger 实例。它们**包含**在 **gsap.context()** 中，并在您调用 **ctx.revert()** 时还原。因此：

- 在您用于补间的相同 **gsap.context()** 回调中创建 ScrollTriggers。
- 在影响触发位置的布局更改后调用 **ScrollTrigger.refresh()**；在 Vue/Svelte 中，这通常意味着在DOM更新后（例如 Vue 中的 nextTick、Svelte 中的 tick 或异步内容加载后）。

## 何时创建与何时销毁

| 生命周期     | 操作                                                                                                        |
| ------------ | ----------------------------------------------------------------------------------------------------------- |
| **挂载**     | 在 **gsap.context(scope)** 内创建补间和 ScrollTriggers。                                                    |
| **卸载 / 销毁** | 调用 **ctx.revert()**，以便在该上下文中所有动画和 ScrollTriggers 被销毁，并且内联样式被还原。                 |

不要在组件的 setup 或在根元素存在之前运行的同步顶层脚本中创建 GSAP 动画。等待 **onMounted** / **onMount**（或等效）以便容器引用在DOM中。

## 不要

- ❌ 在组件挂载之前创建补间或 ScrollTriggers（例如在 setup 中没有 onMounted）；DOM 节点可能还不存在。
- ❌ 使用没有 **作用域** 的选择器字符串（将容器传递给 gsap.context() 作为第二个参数），以便选择器不会匹配组件外的元素。
- ❌ 跳过清理；始终在 onUnmounted / onMount 的返回值中调用 **ctx.revert()**，以便在组件销毁时销毁动画和 ScrollTriggers。
- ❌ 在每次渲染时运行（它不会造成任何伤害，只是浪费）；在应用级别注册一次。

### 了解更多

- **gsap-react** 技能，针对 React 特定模式（useGSAP、contextSafe）。
