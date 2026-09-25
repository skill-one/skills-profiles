# GSAP & Framer Motion — 滚动动画技能

使用 GitHub Copilot 提示，提供即用代码配方和深度 API 参考，实现生产级滚动动画。

> **设计伴侣：** 此技能提供滚动驱动动画的*技术实现*。
> 对于*创意理念*、设计原则和高级美学，这些应指导**如何**和**何时**进行动画，始终参考**premium-frontend-ui**技能。
> 两者共同构成完整的方法：premium-frontend-ui 决定**什么**和**为什么**；此技能提供**如何**。

## 快速库选择器

| 需求 | 使用 |
|---|---|
| 纯 JavaScript、Webflow、Vue | **GSAP** |
| 固定位置、水平滚动、复杂时间线 | **GSAP** |
| React / Next.js、声明式风格 | **Framer Motion** |
| whileInView 进入动画 | **Framer Motion** |
| 在同一 Next.js 应用中使用两者 | 参考中的注释 |

阅读相关参考文件获取完整配方和 Copilot 提示：

- **GSAP** → `references/gsap.md` — ScrollTrigger API、所有配方、React 集成
- **Framer Motion** → `references/framer.md` — useScroll、useTransform、所有配方

## 设置（始终首先执行）

### GSAP
```bash
npm install gsap
```
```js
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
gsap.registerPlugin(ScrollTrigger); // 必须在使用 ScrollTrigger 之前调用
```

### Framer Motion (Motion v12, 2025)
```bash
npm install motion   # 自 2025 年中开始的新包名
# 或: npm install framer-motion  — 仍然可用，相同 API
```
```js
import { motion, useScroll, useTransform, useSpring } from 'motion/react';
// 旧版: import { motion } from 'framer-motion'  — 也有效
```

## 工作流程

1. 解读用户意图，确定 GSAP 或 Framer Motion 是否更适合。
2. 阅读 `references/` 中的相关参考文档，获取详细的 API 和模式。
3. 如果尚未存在，建议安装所需的包。
4. 实现动画结构的骨架，遵循请求的格式（React 组件、钩子要求或纯 JavaScript）。
5. 应用正确的工具（滚动 vs 在视图中元素），确保可访问性选项存在，钩子不会导致无限重新渲染。

## 最常见的 5 种滚动模式

快速参考 — 完整配方和 Copilot 提示在参考文件中。

### 1. 进入时淡入 (GSAP)
```js
gsap.from('.card', {
  opacity: 0, y: 50, stagger: 0.15, duration: 0.8,
  scrollTrigger: { trigger: '.card', start: 'top 85%' }
});
```

### 2. 进入时淡入 (Framer Motion)
```jsx
<motion.div
  initial={{ opacity: 0, y: 40 }}
  whileInView={{ opacity: 1, y: 0 }}
  viewport={{ once: true, margin: '-80px' }}
  transition={{ duration: 0.6 }}
/>
```

### 3. Scrub / 滚动关联 (GSAP)
```js
gsap.to('.hero-img', {
  scale: 1.3, opacity: 0, ease: 'none',
  scrollTrigger: { trigger: '.hero', start: 'top top', end: 'bottom top', scrub: true }
});
```

### 4. 滚动关联 (Framer Motion)
```jsx
const { scrollYProgress } = useScroll({ target: ref, offset: ['start end', 'end start'] });
const y = useTransform(scrollYProgress, [0, 1], [0, -100]);
return <motion.div style={{ y }} />;
```

### 5. 固定时间线 (GSAP)
```js
const tl = gsap.timeline({
  scrollTrigger: { trigger: '.section', pin: true, scrub: 1, start: 'top top', end: '+=200%' }
});
tl.from('.title', { opacity: 0, y: 60 }).from('.img', { scale: 0.85 });
```

## 关键规则（始终应用）

- **GSAP**：始终在使用前调用 `gsap.registerPlugin(ScrollTrigger)`
- **GSAP scrub**：始终使用 `ease: 'none'` — 当 scrub 激活时，缓动感会感觉不对
- **GSAP React**：使用 `@gsap/react` 的 `useGSAP`，绝不用纯 `useEffect` — 它会自动清理 ScrollTriggers
- **GSAP 调试**：开发期间添加 `markers: true`；生产前移除
- **Framer**：`useTransform` 输出必须放入 `motion.*` 元素的 `style` 属性中，而不是普通 div
- **Framer Next.js**：任何使用运动钩子的文件顶部始终添加 `'use client'`
- **两者**：仅动画化 `transform` 和 `opacity` — 避免 `width`、`height`、`box-shadow`
- **可访问性**：始终检查 `prefers-reduced-motion` — 参考每个文件中的模式
- **高级润色**：遵循 **premium-frontend-ui** 技能的原则，用于运动时间、缓动曲线和克制 — 动画应增强，而非压倒

## Copilot 提示技巧

- 一次性提供完整选择器、基础图像和滚动范围给 Copilot — 模糊提示会产生模糊代码
- 对于 GSAP，始终指定：选择器、开始/结束字符串、是否需要 scrub 或 toggleActions
- 对于 Framer，始终指定：哪个钩子（useScroll vs whileInView）、偏移值、要转换的内容
- 请求 `/fix` 时粘贴确切错误信息 — Copilot 的修复在真实错误下效果显著
- 在 Copilot Chat 中使用 `@workspace` 范围，使其读取您现有的组件结构

## 参考文件

| 文件 | 内容 |
|---|---|
| `references/gsap.md` | 完整 ScrollTrigger API 参考、10 个配方、React (useGSAP)、Lenis、matchMedia、可访问性 |
| `references/framer.md` | 完整 useScroll / useTransform API、8 个配方、variants、Motion v12 注意事项、Next.js 提示 |

## 相关技能

| 技能 | 关系 |
|---|---|
| **premium-frontend-ui** | 创意理念、设计原则和美学指南 — 定义*何时*和*为什么*进行动画 |
