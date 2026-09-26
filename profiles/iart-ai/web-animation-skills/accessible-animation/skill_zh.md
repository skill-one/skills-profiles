# 可访问性动画（减少运动，分级）

将 `prefers-reduced-motion: reduce` 尊为*优雅降级*，而非关闭开关。系统级设置（macOS：设置 > 可访问性 > 显示 > 减少运动；Windows：设置 > 可访问性 > 视觉效果 > 动画效果；iOS/Android 对应设置）表示*前庭触发*的运动会导致恶心、头晕或偏头痛。正确的做法是移除危险运动，同时保留方向提示。

## 使用场景

在添加或审核 Web UI 中的动画、用户报告运动病或 WCAG 测评结果、或将动画库（GSAP、Framer Motion、Lenis smooth scroll、Anime.js、CSS keyframes）集成到可访问产品中时使用。

## 核心原则：分级运动，勿全删

移除所有动画是常见的过度纠正。无过渡的即时状态变化可能更令人迷失方向（元素瞬移），并移除有用的可供性（焦点环、加载旋转器等进度指示）。将每个动画分为三级：

- **第一级 — 完全移除（前庭触发）。** 视差；大范围视口滑动/平移；大元素缩放/缩放；3D 旋转和旋转；连续自动播放的轮播和跑马灯；平滑滚动劫持（Lenis/Locomotive）；被劫持的固定场景；运动路径动画；任何移动大屏幕部分或暗示深度/自运动的动画。
- **第二级 — 软化/缩短。** 用短淡入淡出（≤200ms）替换运动。减少距离和持续时间。保留过渡的*事实*（以便元素不瞬移），但移除位移。将 600ms 从左侧滑入替换为 150ms 横向淡入。
- **第三级 — 始终保留。** 淡入淡出、颜色/背景过渡、焦点环过渡、加载指示器，以及*对意义至关重要*的运动（WCAG 允许必要动画）。这些很少触发前庭反应，因为它们暗示无自运动。

## CSS 层：媒体查询控制

默认情况下编写运动，然后在减少查询下覆盖。优先使用全局安全网加针对性覆盖。

```css
/* 全局安全网：消除失控运动，但不要盲目设置 0s，这会破坏等待 transitionend/animationend 的 JS。使用 0.01ms。 */
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;   /* 停止无限旋转/跑马灯 */
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;          /* 关闭平滑滚动 */
  }
}
```

全局网是后备措施。在顶层叠加*有意、分级的*覆盖，以便第三级运动得以保留：

```css
.card {
  transition: transform 400ms ease, opacity 400ms ease, background-color 200ms ease;
}

@media (prefers-reduced-motion: reduce) {
  .card {
    /* 第二级：移除 transform（运动），保留 opacity + color（第三级） */
    transition: opacity 150ms ease, background-color 150ms ease;
  }
  .parallax-layer { transform: none !important; }        /* 第一级：移除 */
  .hero-zoom      { animation: none !important; }        /* 第一级：移除 */
}
```

使用*正向*查询 `(prefers-reduced-motion: no-preference)` 启用运动，这是最安全的模式，适用于复杂效果：

```css
.hero { opacity: 1; } /* 默认可见、静态 */
@media (prefers-reduced-motion: no-preference) {
  .hero { animation: zoom-in 1.2s ease both; } /* 仅在允许时动画 */
}
```

## JS 层：matchMedia 控制

CSS 无法控制 JS 驱动的动画（GSAP 时间线、Framer 的 `animate`、canvas/WebGL、Lenis）。通过 `matchMedia` 读取相同信号，并实时响应变化（用户在不刷新页面的情况下切换系统设置）。

```js
const REDUCE_QUERY = '(prefers-reduced-motion: reduce)';

export function prefersReducedMotion() {
  return typeof window !== 'undefined'
    && window.matchMedia
    && window.matchMedia(REDUCE_QUERY).matches;
}

// 实时更新：监听切换系统设置立即生效。
export function onReducedMotionChange(cb) {
  const mq = window.matchMedia(REDUCE_QUERY);
  const handler = (e) => cb(e.matches);
  mq.addEventListener('change', handler);          // 现代 API
  return () => mq.removeEventListener('change', handler);
}
```

### 库控制，作为可重用层应用

```js
// GSAP — 使用 matchMedia：GSAP 在变化时撤销条件设置。
import gsap from 'gsap';
const mm = gsap.matchMedia();
mm.add({
  motionOK: '(prefers-reduced-motion: no-preference)',
  motionReduce: '(prefers-reduced-motion: reduce)',
}, (ctx) => {
  const { motionOK } = ctx.conditions;
  if (motionOK) {
    gsap.from('.hero', { y: 80, opacity: 0, duration: 1 });   // 第一级移动
  } else {
    gsap.from('.hero', { opacity: 0, duration: 0.15 });        // 第二级淡入
  }
});

// Lenis smooth scroll — 减少时完全不实例化。
import Lenis from 'lenis';
let lenis = null;
if (!prefersReducedMotion()) {
  lenis = new Lenis();
  const raf = (t) => { lenis.raf(t); requestAnimationFrame(raf); };
  requestAnimationFrame(raf);
}
```

## React：`useReducedMotion` 钩子

```jsx
import { useState, useEffect } from 'react';

export function useReducedMotion() {
  const query = '(prefers-reduced-motion: reduce)';
  const get = () =>
    typeof window !== 'undefined' && window.matchMedia
      ? window.matchMedia(query).matches
      : false;
  const [reduced, setReduced] = useState(get);

  useEffect(() => {
    const mq = window.matchMedia(query);
    const onChange = () => setReduced(mq.matches);
    onChange();                                   // 水合后同步
    mq.addEventListener('change', onChange);
    return () => mq.removeEventListener('change', onChange);
  }, []);

  return reduced;
}
```

```jsx
// Framer Motion 有自己的 useReducedMotion()；上述钩子同样适用。
import { motion } from 'framer-motion';
function Card() {
  const reduced = useReducedMotion();
  return (
    <motion.div
      initial={reduced ? { opacity: 0 } : { opacity: 0, y: 40 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: reduced ? 0.15 : 0.5 }}
    />
  );
}
```

服务器端渲染状态初始化为 `false`（运动），并在 `useEffect` 中同步，以避免水合不匹配；系统值仅在客户端已知。

## WCAG 映射

- **2.3.3 交互触发的动画（AAA）。** 由交互（滚动、悬停）触发的运动必须可禁用，除非必要。尊重 `prefers-reduced-motion` 是标准技术。
- **C39（CSS 技术）。** 使用 `prefers-reduced-motion` 查询防止运动。这是命名充分技术。
- **2.2.2 暂停、停止、隐藏（A）。** 任何持续超过 5 秒的自动播放运动必须提供暂停/停止。无论媒体查询如何，自动轮播和跑马灯都未通过此要求——提供控制。

## 交付与验证（独立 HTML）

> **打包辅助工具**（`scripts/`）：`scripts/seek-shot.sh anim.html 0 1.5 3` 冻结 `?t=N` 捕获器并截图每个时刻；`scripts/contact-sheet.sh sheet.png frame-*.png` 将它们平铺以便快速审查。参见 `scripts/README.md`。

对于自包含演示，交付物是**一个可直接在浏览器中打开的 HTML 文件**——标记、CSS 和任何 JS（来自 CDN 的 GSAP/`matchMedia`）内联，无需构建步骤。对于此技能，验证是重点：你必须截图**正常和减少运动路径的两者**，并确认分级正确。

**输出合同：**
- 一个 `.html` 文件，包含完整的运动及其分级减少运动覆盖（CSS 查询 + `matchMedia`/`gsap.matchMedia()` 用于 JS 驱动的运动）。
- 一个捕获帧的寻求捕手，以及强制减少运动代码路径的截图方法。

**寻求捕手 — 冻结帧，强制偏好。** `?t=N` 冻结时间线；`?reduce=1` 即使系统设置关闭也强制减少路径（CSS 无法从 JS 切换，因此查询与 JS 控制的相同标志，并模拟 CSS 层的偏好进行截图）：

```html
<script>
  const q = new URLSearchParams(location.search);
  const reduce = q.get("reduce") === "1"
    || window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  // 根据 `reduce` 条件性构建运动（移除第一级，软化第二级，保留第三级）
  const t = q.get("t");
  if (t !== null) { tl.pause(); tl.seek(parseFloat(t)); }      // GSAP；CSS: el.style.animationDelay=(-t)+"s"; playState="paused"
  window.__ready = true;
</script>
```

**验证循环 — 截图两者状态：** 捕获正常路径和减少路径的动画中间状态，并确认第一级运动消失，第二级是短淡入，第三级保留。模拟偏好以控制 CSS 层（Playwright `--reduced-motion=reduce`；代理的浏览器工具也可以模拟）：

```bash
npx playwright screenshot --wait-for-timeout=500 "file://$PWD/demo.html?t=0.6" normal.png
npx playwright screenshot --reduced-motion=reduce --wait-for-timeout=500 "file://$PWD/demo.html?t=0.6&reduce=1" reduced.png
```

**完成前：**
1. 独立打开 — 无控制台错误，CDN（如有）加载。
2. 冻结 + `?reduce=1`（和 `--reduced-motion=reduce`）可靠地执行两个代码路径。
3. 在两种状态下截图动画中间状态 — 正常看起来有意，减少移除第一级/软化第二级。
4. `prefers-reduced-motion` 尊为*分级*，而非关闭开关 — 无瞬移，第三级淡入/焦点环/旋转器保留；任何 >5s 自动运动仍有暂停控制（2.2.2）。
5. 缓动有意设计在两个路径中 — 无意外 `linear`，持续时间合理（减少淡入 ≤200ms，`0.01ms` 而非 `0s`）。

## 快速参考

| 运动类型 | 级别 | 减少行为 |
|---|---|---|
| 视差/深度 | 1 | 移除 (`transform: none`) |
| 大滑动/平移 | 1 | 移除或用淡入替换 |
| 缩放/缩放（大） | 1 | 移除 |
| 旋转/3D 旋转 | 1 | 移除 (`animation: none`) |
| 自动轮播/跑马灯 | 1 | 停止 + 提供暂停控制（2.2.2） |
| 平滑滚动（Lenis） | 1 | 不实例化 |
| 小滑动/弹出 | 2 | 横向淡入 ≤200ms |
| 淡入淡出 | 3 | 保留（过长则缩短） |
| 颜色/焦点环过渡 | 3 | 保留 |
| 加载旋转器 | 3 | 保留（必要反馈） |

## 注意事项

- `animation-duration: 0s` 可能破坏等待 `animationend`/`transitionend` 的代码；使用 `0.01ms` 以确保事件仍触发。
- 全局 `*` 重置单独移除过多第三级运动；始终叠加有意覆盖。
- 忘记 `animation-iteration-count: 1` 会留下无限旋转（近零持续时间运行，CPU 消耗，仍在动画）。
- 无媒体查询覆盖 JS/canvas/WebGL — 用 `matchMedia` 或循环永远不会停止。
- 切换系统设置不触发页面刷新；无 `change` 监听器页面保持陈旧状态。
- 服务器端渲染：渲染期间读取 `matchMedia` 抛出或不匹配；默认运动并在效果中同步。
- 自动播放运动即使在减少运动关闭时也需要可见暂停控制（2.2.2 是 A 级）。

## 参考文件

- `references/patterns.md` — 完整 GSAP `matchMedia` 拆解、Framer Motion `MotionConfig`、Lenis 在实时切换时启动/停止、可重用的 `animateWithMotionPreference` 包装器、带暂停控制的跑马灯，以及分级分类审计清单。
