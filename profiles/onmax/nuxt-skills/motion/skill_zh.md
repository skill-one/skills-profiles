# Motion Vue (motion-v)

适用于 Vue 3 和 Nuxt 的动画库。生产就绪，硬件加速的动画，且打包体积极小。

**当前稳定版本：** motion-v 1.x - Motion 的 Vue 版本（前身为 Framer Motion）

## 概述

Motion Vue 动画的渐进式参考。仅加载与当前任务相关的文件（基础包约 200 个 token，每个子文件 500-1500 个）。

## 使用场景

**使用 Motion Vue 的场景：**

- 简单的声明式动画（淡入、滑动、缩放）
- 基于手势的交互（悬停、点击、拖拽）
- 滚动关联动画
- 布局动画和共享元素过渡
- 弹簧物理动画

**考虑替代方案：**

- **GSAP** - 复杂的时间轴、SVG 变形、滚动触发序列
- **@vueuse/motion** - 更简单的 API、更少的功能、更小的打包体积
- **CSS 动画** - 简单的过渡效果，无需 JS

## 安装

```bash
# Vue 3
pnpm add motion-v

# Nuxt 3
pnpm add motion-v @vueuse/nuxt
```

```ts
// nuxt.config.ts - Nuxt 3 配置
export default defineNuxtConfig({
  modules: ['motion-v/nuxt'],
})
```

## 快速参考

| 正在处理...                | 加载文件                 |
| ---------------------------- | ------------------------- |
| Motion 组件、手势           | references/components.md  |
| useMotionValue, useScroll    | references/composables.md |
| 动画示例、模式             | references/examples.md    |

## 文件加载

**根据您的任务考虑加载以下参考文件：**

- [ ] [references/components.md](references/components.md) - 如果使用 Motion 组件、手势或布局动画
- [ ] [references/composables.md](references/composables.md) - 如果使用 useMotionValue、useScroll、useSpring 或 animate()
- [ ] [references/examples.md](references/examples.md) - 如果寻找动画模式或灵感

**不要一次性加载所有文件。** 仅加载与当前任务相关的文件。

## 核心概念

### Motion 组件

渲染任何具有动画能力的 HTML/SVG 元素：

```vue
<script setup lang="ts">
import { motion } from 'motion-v'
</script>

<template>
  <motion.div
    :initial="{ opacity: 0, y: 20 }"
    :animate="{ opacity: 1, y: 0 }"
    :exit="{ opacity: 0, y: -20 }"
    :transition="{ duration: 0.3 }"
  >
    动画内容
  </motion.div>
</template>
```

### 手势动画

```vue
<motion.button
  :whileHover="{ scale: 1.05 }"
  :whilePress="{ scale: 0.95 }"
  :transition="{ type: 'spring', stiffness: 400 }"
>
  点击我
</motion.button>
```

### 滚动动画

```vue
<motion.div
  :initial="{ opacity: 0 }"
  :whileInView="{ opacity: 1 }"
  :viewport="{ once: true, margin: '-100px' }"
>
  滚动时出现
</motion.div>
```

## 可用指南

**[references/components.md](references/components.md)** - Motion 组件变体、动画属性、手势属性、布局动画、过渡配置

**[references/composables.md](references/composables.md)** - useMotionValue、useSpring、useTransform、useScroll、useInView、animate()

**[references/examples.md](references/examples.md)** - 外部资源、组件库、动画模式和灵感
