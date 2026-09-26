# GSAP for the Web

GSAP (GreenSock Animation Platform) 是代码驱动型网页动画的工作核心：序列化时间轴、滚动驱动的叙事、文本揭示和布局过渡。自 GSAP 3.12 版本起，所有插件（ScrollTrigger、SplitText、Flip、MotionPath、MorphSVG、Draggable、Observer）均完全免费，包括商业用途。

## 使用场景

- 滚动驱动的叙事：固定区域、视差效果、进度滚动、水平滚动
- 序列化英雄动画和具有精确重叠控制的复杂多元素时间轴
- 文本揭示（SplitText）分为字符/单词/行
- 布局过渡（Flip）中元素改变位置/大小/父级
- 任何需要精细时间控制、缓动精度或命令式编排的运动

## 安装和注册

```js
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { SplitText } from "gsap/SplitText";
import { Flip } from "gsap/Flip";

gsap.registerPlugin(ScrollTrigger, SplitText, Flip);
```

插件必须在使用前注册，否则将静默无操作。使用打包工具时，在应用入口处注册一次即可。

## 核心技巧

### 优先使用时间轴

优先使用一个时间轴而不是多个独立的补间动画——这提供了一个单一的播放头、相对定位和易于反向操作。

```js
const tl = gsap.timeline({ defaults: { ease: "power3.out", duration: 0.6 } });
tl.from(".title", { yPercent: 100, opacity: 0 })
  .from(".sub",   { y: 20, opacity: 0 }, "-=0.3")  // 开始比前一个动画提前 0.3 秒
  .from(".cta",   { scale: 0.9, opacity: 0 }, "<"); // 与前一个动画的起始对齐
```

定位参数速查表：
- `"+=0.5"` / `"-=0.3"` — 相对于时间轴的结束（间隙/重叠）
- `"<"` — 前一个补间的起始；`">"` — 前一个补间的结束
- `"<0.2"` — 前一个补间开始后的 0.2 秒
- `"myLabel"` — 通过 `tl.addLabel("myLabel")` 添加的命名标签

使用 `.from()` 进行入场动画（从给定值动画到当前 CSS 状态），`.to()` 进行出场动画，`.fromTo()` 当两端都需要明确指定时（最稳健地防止重新运行）。

### gsap.to vs set vs quickTo

```js
gsap.set(el, { autoAlpha: 0 });           // 瞬时，无补间（autoAlpha = 透明度 + 可见性）
const xTo = gsap.quickTo(el, "x", { duration: 0.4, ease: "power3" });
window.addEventListener("pointermove", (e) => xTo(e.clientX)); // 快速重复更新
```

`autoAlpha` 优于原始 `opacity`，因为它在 0 时也会切换 `visibility:hidden`，从而从命中测试中移除元素。

### ScrollTrigger 基础

```js
gsap.to(".panel", {
  xPercent: -100,
  ease: "none",
  scrollTrigger: {
    trigger: ".wrap",
    start: "top top",      // 当触发器顶部到达视口顶部时
    end: "+=2000",         // 2000 像素的滚动距离
    pin: true,             // 在动画播放时冻结 .wrap
    scrub: 1,              // 将进度与滚动条绑定（1 = 1 秒的追赶平滑）
    markers: true,         // 开发者专用的视觉标记——生产环境中移除
  },
});
```

关键语义：
- `start`/`end` 接受 `"triggerPos viewportPos"`（例如 `"top center"`) 或 `"+=px"`。
- `scrub: true` 锁定动画进度与滚动完全对应；`scrub: <number>` 添加平滑延迟。
- `toggleActions: "play pause resume reverse"` 控制非滚动触发器的 onEnter/onLeave/onEnterBack/onLeaveBack。
- 使用 `ease: "none"` 为滚动补间设置，使运动与滚动线性跟踪。

### 平滑滚动（Lenis）+ ScrollTrigger

Lenis（或 Locomotive）平滑滚动与 ScrollTrigger 除非它们在同一循环中运行，否则会不同步。Lenis 自己在 rAF 上平滑滚动，而 ScrollTrigger 在 GSAP 的 ticker 上读取滚动；当它们独立运行时，ScrollTrigger 会采样一个过时的位置。修复方法：使用 GSAP 的 ticker 驱动 Lenis，并在每个 Lenis 滚动时更新 ScrollTrigger。

```js
import Lenis from "lenis";

const lenis = new Lenis({ duration: 1.2, smoothWheel: true });

lenis.on("scroll", ScrollTrigger.update);          // 1. 每个Lenis滚动时更新 ScrollTrigger
gsap.ticker.add((t) => lenis.raf(t * 1000));       // 2. 单一循环：ticker 驱动 Lenis（秒 → 毫秒）
gsap.ticker.lagSmoothing(0);                        // 3. 停止 GSAP 在重负载帧上的追赶抖动
```

关键点：`gsap.ticker` 传递时间以**秒**为单位，`lenis.raf()` 需要**毫秒**——乘以 1000。不要同时运行一个独立的 `requestAnimationFrame(raf)` 循环用于 Lenis；那会导致双重驱动。

常见错误：
- **抖动/卡顿** — 一个遗留的 `requestAnimationFrame(raf)` 循环与 ticker 竞争，或缺少 `lagSmoothing(0)`。移除非法循环；将滞后平滑设置为 0。
- **标记漂移** — 标记从其触发器漂移——`ScrollTrigger.update` 未订阅 `lenis.on("scroll", …)`。
- **固定失效** — 在 Lenis 下不要设置 `scrollerProxy`（它滚动文档）。在 Locomotive 下你必须连接 `scrollerProxy` + `pinType`，并在每个触发器上设置 `scroller:`。
- **滚动卡住/方向翻转** — 缺少 `* 1000` 单位转换，或两个循环顺序错误。

在 SPA 卸载时进行清理：`gsap.ticker.remove(update)` + `lenis.destroy()`，否则每个导航都会堆叠循环。在 `prefers-reduced-motion` 后面（跳过 Lenis，运行原生滚动）。完整的 Lenis + Locomotive 连接、锚链接路由、`data-lenis-prevent`、React（`useGSAP`/`useEffect`）以及症状→原因表在 `references/scrolltrigger-lenis.md` 中。

### SplitText（文本揭示）

```js
const split = SplitText.create(".headline", { type: "lines, words", linesClass: "line" });
gsap.from(split.lines, { yPercent: 100, opacity: 0, stagger: 0.08, duration: 0.7, ease: "power4.out" });
```

注意事项：
- 包裹线遮罩揭示：在行包装器上设置 `overflow: hidden` 以便 `yPercent: 100` 清晰隐藏。添加 `autoSplit: true`（GSAP 3.13+）以在字体加载/调整大小时重新分割。
- 在重新分割或卸载前调用 `split.revert()` 以恢复原始 DOM 并避免重复节点。
- 始终在 Web 字体加载后（`document.fonts.ready.then(...)`）分割，以防止错误的行断。

### Flip（布局过渡）

Flip 记录状态，允许 DOM 瞬间改变，然后动画化视觉差异（FLIP 技术）。适用于网格<->列表、扩展卡片和重新父级。

```js
const state = Flip.getState(".item");   // 1. 捕获前
container.classList.toggle("grid");      // 2. 改变 DOM/CSS（瞬时）
Flip.from(state, {                        // 3. 动画差异
  duration: 0.6, ease: "power2.inOut", stagger: 0.05,
  absolute: true,                         // 在移动期间将元素移出流（防止重排抖动）
});
```

### 缓动快速指南

- `power2/3.out` — 入场动画（快速然后稳定）
- `power2.inOut` — 在两个屏幕状态之间移动
- `back.out(1.7)` — 超出/弹出（数字 = 超出量）
- `elastic.out(1, 0.3)` — 弹性，谨慎使用
- `none` — 滚动补间
- `steps(n)` — 精灵/阶梯运动
- 自定义 cubic-bezier 等价物：`CustomEase.create("x", "M0,0 C0.2,0 0,1 1,1")`（CustomEase 是免费的）

## 性能和清理

- 仅动画化 `transform`（`x/y/xPercent/scale/rotation`）和 `opacity`——它们是 GPU 组合的，跳过布局/绘制。避免动画化 `top/left/width/height`。
- 在重型/固定元素上设置 `will-change: transform`；之后移除。
- 使用 `ScrollTrigger.batch()` 批量处理许多相似的滚动揭示，而不是每个元素一个触发器。
- 在视口/内容更改后，调用 `ScrollTrigger.refresh()`。

SPA/框架清理是必须的——孤立的触发器会导致内存泄漏和幽灵固定。使用 `gsap.context()`（或 `@gsap/react` 的 `useGSAP`）：

```js
useEffect(() => {
  const ctx = gsap.context(() => {
    // 所有 GSAP + ScrollTrigger 代码在这里
  }, rootRef);
  return () => ctx.revert(); // 终止补间、触发器并恢复内联样式
}, []);
```

## 交付和验证（独立 HTML）

> **打包辅助工具**（`scripts/`）：`scripts/seek-shot.sh anim.html 0 1.5 3` 冻结 `?t=N` 捕获器并截图每个时刻；`scripts/contact-sheet.sh sheet.png frame-*.png` 将它们平铺以一目了然地审查。参见 `scripts/README.md`。

对于自包含动画（英雄、揭示、循环、微场景），交付物是**一个可以直接在浏览器中打开的 HTML 文件**——无需构建步骤、无需框架、无需渲染管道。根据工作的重量匹配交付物：单个文件是网页动画的正确级别；当单个文件可以完成工作时，不要寻求打包器。

**输出合同：**
- 一个 `.html` 文件：CDN 上的 GSAP + 插件、你的标记和动画在一个内联 `<script>` 中。
- 所有动画在**一个主时间轴**上（`const tl = gsap.timeline()`）——你可以搜索的单个播放头。
- 包含下面的搜索捕获器，以便任何时刻都可以冻结以供检查。

**搜索捕获器——冻结精确时刻以供截图。** 网页上的视频播放器帧固定：`?t=N` 将主时间轴搜索到 `N` 秒并暂停，因此截图会落在静止的、确定性的帧上。

```html
<script>
  // ... 构建你的主时间轴作为 `tl` ...
  const t = new URLSearchParams(location.search).get("t");
  if (t !== null) { tl.pause(); tl.seek(parseFloat(t)); }  // 冻结在 t 秒
  // 无 ?t → 正常播放
  window.__ready = true;            // 准备信号，用于无头等待
  console.log("duration", tl.duration());
</script>
```

**验证循环——渲染 → 冻结 → 截图 → 检查：**
1. 在时间轴上的三个时刻打开文件——开始、中间、结束：
   `…/anim.html?t=0`，`?t=<dur/2>`，`?t=<dur>`。从控制台读取 `tl.duration()` 获取结束时间。
2. 截图每个冻结的帧。
3. 检查**保真度**（是否匹配简报？）和**伪影**（文本剪切、元素离屏、字体加载前的 FOUC、接缝处的卡顿）。输出应看起来有意且完成。

任何无头截图工具都适用——你的代理浏览器工具或 Playwright：

```bash
npx playwright screenshot --wait-for-timeout=500 "file://$PWD/anim.html?t=1.2" frame-mid.png
```

**在完成前：**
1. 独立在浏览器中打开——无控制台错误，无缺失的 CDN。
2. 所有动画在一个主时间轴上；`?t=N` 冻结正确。
3. 在开始/中间/结束处截图——匹配简报，无伪影。
4. 尊重 `prefers-reduced-motion`（简化时间轴或跳过）。
5. 缓动是故意的——空间运动上没有意外的 `linear`。

一个完整的可运行模板，其中捕获器已连接，在 `examples/standalone-template.html` 中。

## 快速参考

| 目标 | API |
|------|-----|
| 序列化重叠 | `tl.from(...).from(..., "-=0.3")` |
| 滚动时固定 | `scrollTrigger:{ pin:true, end:"+=N" }` |
| 滚动到滚动 | `scrollTrigger:{ scrub:1, ease:"none" }` |
| 揭示文本行 | `SplitText.create(el,{type:"lines"})` |
| 动画布局变化 | `Flip.getState` → 变化 → `Flip.from` |
| 快速指针跟随 | `gsap.quickTo(el,"x",{...})` |
| 终止所有 | `ScrollTrigger.getAll().forEach(t=>t.kill())` |

## 参考文件

- `references/scrolltrigger-cookbook.md` — 固定、滚动、水平滚动、快进、`ScrollTrigger.batch()` 揭示、视差、嵌套触发器和 SPA 清理模式，带完整代码。
- `references/scrolltrigger-lenis.md` — 完整的 ScrollTrigger + Lenis/Locomotive 平滑滚动同步：规范连接、`scrollerProxy`、锚链接、减少运动、React（`useGSAP`/`useEffect`）、调试清单和症状→原因表。
- `examples/hero-timeline.js` — 完整、可运行的英雄入场时间轴，带 SplitText、交错揭示和减少运动处理。
- `examples/standalone-template.html` — 交付模板：自包含（CDN GSAP）、一个主时间轴、用于截图验证的 `?t=N` 搜索捕获器，以及减少运动处理。
