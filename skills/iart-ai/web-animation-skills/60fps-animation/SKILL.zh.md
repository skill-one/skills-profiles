---
name: 60fps-animation
description: 当用户要求“修复卡顿的 CSS 动画”、“使动画达到 60fps”、“停止布局抖动”、“平滑地动画化宽度/高度/顶部/左侧”、“将动画转换为 transform”、“高效地动画化 box-shadow”、“动画化高度为自动”、“FLIP 动画”或“我的滚动/悬停动画为什么卡顿”时，应使用此技能。
---

# 高性能 Web 动画

消除 janky web 动画的头号原因：动画那些迫使浏览器每帧重新计算布局（reflow）或重绘的属性。浏览器分阶段渲染——**布局 → 绘制 → 合成**。动画 `width`、`height`、`top`、`left`、`margin`、`padding`、`box-shadow` 或 `filter` 每帧都会重新运行布局和/或绘制，阻塞主线程。动画 **`transform`** 和 **`opacity`** 完全在合成器（通常是 GPU）上运行，跳过布局和绘制，这就是动画能在 60/120fps 下流畅的原因。

## 何时使用

当动画出现卡顿或掉帧时使用，当悬停/滚动效果感觉沉重时使用，当动画大小/位置/阴影时使用，当布局变化需要平滑动画（卡片重新排序，元素在容器间移动时），当动画 `height: auto` 时，或当检查动画代码性能时使用。

## 核心规则：仅动画 transform 和 opacity

将每个“昂贵”的动画映射到一个廉价等效方案。

| 动画属性（昂贵） | 触发 | 替换为（廉价） |
|---|---|---|
| `width` / `height` | 布局 + 绘制 | `transform: scaleX()/scaleY()` (+ FLIP 用于真实大小) |
| `top` / `left` / `margin` | 布局 + 绘制 | `transform: translate()` |
| `box-shadow` | 绘制 | 动画伪元素的 `opacity`（承载阴影） |
| `filter: blur()` | 绘制（昂贵） | 通过 `opacity` 交叉渐变两层，或谨慎使用 |
| `background-position` | 绘制 | 对子层使用 `transform: translate()` |
| `color` / `background` | 绘制 | 通常可以接受；或交叉渐变层 |

### 通过 transform 实现位置和大小

```css
/* BAD: 每帧动画布局 */
.box { transition: left 300ms, width 300ms; left: 0; width: 100px; }
.box:hover { left: 200px; width: 200px; }

/* GOOD: 仅合成器动画 */
.box {
  transition: transform 300ms ease;
  transform: translateX(0) scaleX(1);
  transform-origin: left center;
}
.box:hover { transform: translateX(200px) scaleX(2); }
```

`scaleX` 会扭曲内部内容（文本拉伸）。对于无扭曲的真实缩放，使用 **FLIP**。

## 廉价的 box-shadow 通过伪元素 opacity

动画 `box-shadow` 每帧都会重绘一个大的模糊区域。相反，在 `::after` 上绘制一次阴影，然后仅动画其 `opacity`。

```css
.card { position: relative; }
.card::after {
  content: "";
  position: absolute;
  inset: 0;
  border-radius: inherit;
  box-shadow: 0 12px 28px rgba(0,0,0,0.35);
  opacity: 0;
  transition: opacity 300ms ease;
  pointer-events: none;
}
.card:hover::after { opacity: 1; }
```

模糊阴影只被光栅化一次；悬停时仅改变合成器 opacity —— 任何帧率下都流畅。

## FLIP：廉价动画布局变化

FLIP（First, Last, Invert, Play）使用 `transform` 动画布局变化（重新排序、调整大小、在容器间移动）。测量元素原始位置（First）和最终位置（Last），应用一个反转 transform 使其视觉上看起来未移动，然后动画 transform 回到 identity（Play）。DOM 最终处于其真实最终布局；运动完全是合成器工作。

```js
function flip(el, mutate) {
  const first = el.getBoundingClientRect();   // First
  mutate();                                    // 改变 DOM 布局
  const last = el.getBoundingClientRect();     // Last

  const dx = first.left - last.left;
  const dy = first.top - last.top;
  const sx = first.width  / last.width;
  const sy = first.height / last.height;

  el.animate(
    [
      { transformOrigin: 'top left',
        transform: `translate(${dx}px, ${dy}px) scale(${sx}, ${sy})` }, // Invert
      { transformOrigin: 'top left', transform: 'none' },               // Play
    ],
    { duration: 300, easing: 'cubic-bezier(0.2, 0, 0, 1)' }
  );
}

// 使用示例：动画元素移动到新的网格位置
flip(card, () => targetContainer.appendChild(card));
```

Web 动画 API `animate()` 在合成器上运行 transform。对于许多元素，在所有变更前批量读取所有 `getBoundingClientRect()`（见下文布局 thrashing）。

## 动画 height: auto

`height: auto` 历史上不可插值。现代和后备方案：

```css
/* 现代（Chrome 129+ 支持浏览器）：将尺寸关键字纳入动画 */
.panel {
  interpolate-size: allow-keywords;   /* 允许动画到/from auto */
  height: 0;
  overflow: clip;
  transition: height 300ms ease;
}
.panel.open { height: auto; }
/* calc-size() 也有效：height: calc-size(auto, size); */
```

```css
/* 今日稳健后备：CSS grid 1fr -> 0fr */
.wrapper {
  display: grid;
  grid-template-rows: 0fr;            /* 收缩 */
  transition: grid-template-rows 300ms ease;
}
.wrapper.open { grid-template-rows: 1fr; }
.wrapper > .content { overflow: hidden; min-height: 0; }
```

网格技巧动画轨道大小（对合成器足够友好且广泛支持），无需 JS 高度测量。在目标浏览器支持的情况下使用 `interpolate-size: allow-keywords` / `calc-size(auto, size)`；将网格技术作为跨浏览器默认方案。

## 避免布局 thrashing（批量读取，然后写入）

在写入后读取布局属性（`offsetWidth`、`getBoundingClientRect`、`scrollTop`、`getComputedStyle`）会强制同步 reflow。在循环中交错读取和写入（“布局 thrashing”）可能导致每帧运行数十次强制 reflow。

```js
// BAD: 读取，写入，读取，写入... 每次迭代强制 reflow
items.forEach((el) => {
  const w = el.offsetWidth;          // 读取（强制布局）
  el.style.width = w * 1.5 + 'px';   // 写入（使布局失效）
});

// GOOD: 批量所有读取，然后所有写入
const widths = items.map((el) => el.offsetWidth);  // 所有读取
items.forEach((el, i) => {                          // 所有写入
  el.style.width = widths[i] * 1.5 + 'px';
});
```

对于帧同步工作，在 `requestAnimationFrame` 回调中读取，然后应用写入；像 fastdom 这样的库形式化这种读写调度。

## will-change：谨慎使用

`will-change: transform` 提前将元素提升到自己的合成器层，避免动画开始时的卡顿。但每个提升的层都会消耗 GPU 内存，过度使用会降低性能。

```css
.menu { will-change: transform; }   /* 仅在即将动画的元素上使用 */
```

规则：在动画前立即应用（例如悬停/父状态），空闲时移除它（`will-change: auto`），不要对许多元素进行全盘应用，也不要永久保留在大型/多个节点上。一个 `transform: translateZ(0)` 小技巧也能实现相同的提升，但更难撤销——优先使用 `will-change`。

## 交付与验证（独立 HTML）

> **打包辅助工具** (`scripts/`)：`scripts/seek-shot.sh anim.html 0 1.5 3` 冻结 `?t=N` 捆绑并截图每个时刻；`scripts/contact-sheet.sh sheet.png frame-*.png` 将它们平铺以快速审查。见 `scripts/README.md`。

交付物是**一个自包含的 `.html`**，直接在浏览器中打开——包含标记、CSS/JS 动画和冻结捆绑器在一个文件中。对于这项技能，验证是双重的：帧必须看起来正确，并且生成成本要低（仅合成器）。

**输出合同：**
- 一个 `.html`，依赖项通过 CDN（如有），动画由 CSS transitions/`@keyframes` 或 Web 动画 API 驱动。
- 一个冻结机制，使截图落在确定性帧：
  - CSS `@keyframes` → `?t=N` 设置 `el.style.animationDelay = (-N)+'s'; el.style.animationPlayState = 'paused'`。
  - WAAPI / JS → 保留动画对象并 `anim.pause(); anim.currentTime = N*1000`。

**验证循环——冻结 → 截图，然后性能分析 jank：**
1. 在开始/中间/结束时无头打开 (`?t=0`，中间，结束)，截图每个；确认运动在视觉上正确（没有 `scaleX` 剪辑/拉伸文本，FLIP 落在真实布局上，阴影/高度过渡看起来正确）。
2. **确认它是合成器仅用**——这是这项技能的要点。要么：
   - DevTools → Performance：记录动画，检查每帧**没有紫色“布局”或绿色“绘制”**条带（只有“合成层”）。
   - 或无头跟踪：`npx playwright screenshot` 用于视觉，加上 CDP/`tracing` 捕获，并断言在动画窗口期间没有 `布局`/`绘制` 事件触发。
3. 观察FPS/“帧渲染统计”覆盖层保持在 60——掉帧意味着昂贵的属性又回来了。

```bash
npx playwright screenshot --wait-for-timeout=500 "file://$PWD/anim.html?t=0.3" frame.png
```

**在完成前：**
1. 独立打开——无控制台错误。
2. 仅 `transform` / `opacity` 每帧动画；DevTools 显示无每帧布局/绘制。
3. 在开始/中间/结束时截图——正确，没有 `scaleX` 文本扭曲，FLIP 落在真实位置。
4. 保持 60fps；`will-change` 及时应用并在空闲时移除（无剩余层）。
5. 尊重 `prefers-reduced-motion`。

## 快速参考

| 目标 | 做这个 |
|---|---|
| 移动元素 | `transform: translate()` |
| 无扭曲调整大小 | FLIP with `transform` |
| 悬停阴影 | 动画阴影伪元素的 `opacity` |
| 扩展到内容高度 | grid `0fr→1fr`，或 `interpolate-size: allow-keywords` |
| 多个元素移动 | 批量 `getBoundingClientRect` 读取，然后写入 |
| 平滑动画开始 | 及时 `will-change`，空闲时移除 |
| 验证仅合成器 | DevTools Performance：每帧无紫色“布局”/绿色“绘制” |

## 注意事项

- `scaleX/scaleY` 拉伸文本和子元素；内容必须保持清晰时使用 FLIP。
- `transform` 百分比相对于元素自己的框，而不是父级——与 `left: %` 不同。
- 过度使用 `will-change` 或 `translateZ(0)` 创建太多层并*损害*性能；仅提升实际动画的元素。
- `filter` 和 `backdrop-filter` 与合成器相关但仍然昂贵；通过 `opacity` 交叉渐变其存在，而不是动画模糊半径。
- 网格 `1fr→0fr` 内容必须有 `overflow: hidden` 和 `min-height: 0` 或它不会收缩。
- 始终在 `@media (prefers-reduced-motion: reduce)` 后门非必要运动。

## 参考文件

- `references/patterns-and-profiling.md` — 完整可运行示例（手风琴，重新排序列表，视差），DevTools 性能分析演练以确认合成器仅用帧，减少运动模式，以及属性成本速查表。
