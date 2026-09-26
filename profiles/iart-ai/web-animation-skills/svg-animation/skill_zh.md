# SVG 动画

清晰、轻量、无限可缩放的矢量运动——非常适合图标、插图、标志和数据标记。SVG 可以通过三种方式实现动画：CSS（声明式、简单）、SMIL（在 SVG 内部的 `<animate>`）和 JS（GSAP/Web Animations，用于控制和变形）。根据任务选择；下面的技术会说明哪种适合。

## 使用场景

- 图标、插图、签名、地图的“描边绘制”效果
- 形状/路径变形和动画图标状态变化（菜单 ↔ 关闭，播放 ↔ 暂停）
- 沿路径移动元素（运动路径）
- 动画渐变、滤镜（发光、置换）和动画标志

## 核心技术

### 描边绘制（基础）

将虚线数组绘制得与路径一样长，完全偏移（不可见），然后动画偏移量为 0。

```css
.path {
  stroke-dasharray: var(--len);
  stroke-dashoffset: var(--len);
  animation: draw 1.4s ease forwards;
}
@keyframes draw { to { stroke-dashoffset: 0; } }
```

获取长度：
- JS（最可靠）：`const len = path.getTotalLength(); path.style.setProperty("--len", len);`
- 无 JS 技巧：在 `<path>` 上设置 `pathLength="1"`，然后 `stroke-dasharray: 1; stroke-dashoffset: 1;` 并动画到 `0`。这会将任何路径标准化为 0–1 长度，无需测量。

反向（擦除）通过将偏移量从 0 动画回 `len` 实现。使用 `animation-delay` 错开多个路径。绘制方向遵循路径的点的顺序；在编辑器中反转它或在偏移量符号上取反如果它“反向”绘制。

### 一个路径变形为另一个路径

路径逐点插值，因此一个简单的变形需要两个 `d` 属性具有**相同数量和类型的命令**。有两种稳健的方法：

- **GSAP MorphSVG**（自 GSAP 3.12 起免费）——自动处理不匹配的点数并找到良好的映射：

```js
gsap.registerPlugin(MorphSVGPlugin);
gsap.to("#start", { morphSVG: "#end", duration: 0.8, ease: "power2.inOut" });
// 将任何形状转换为可变形路径：
MorphSVGPlugin.convertToPath("circle, rect, ellipse, line, polygon");
```

- **Flubber**（小型独立库）——无需 GSAP 生成插值器，与 React/Framer Motion 配合良好：

```js
import { interpolate } from "flubber";
const interpolator = interpolate(pathA, pathB, { maxSegmentLength: 2 });
// interpolator(0) === pathA, interpolator(1) === pathB；将 t 喂入补间动画。
```

对于手写的变形（图标切换），保持两个路径具有相同的命令结构，并通过 Web Animations 或 CSS 直接动画 `d`（在现代浏览器中，`d` 可通过 `path("...")` 动画）。

### 沿路径运动

- **GSAP MotionPath**（首选——控制、对齐、可滚动）：

```js
gsap.registerPlugin(MotionPathPlugin);
gsap.to("#rocket", {
  duration: 4, repeat: -1, ease: "none",
  motionPath: { path: "#track", align: "#track", autoRotate: true, alignOrigin: [0.5, 0.5] },
});
```

`autoRotate: true` 使对象朝向路径切线；`align` 使坐标相对于路径元素。

- **SMIL**（无需 JS）：

```svg
<path id="track" d="M10,80 C40,10 120,10 150,80" fill="none"/>
<circle r="6" fill="#3b82f6">
  <animateMotion dur="3s" repeatCount="indefinite" rotate="auto">
    <mpath href="#track"/>
  </animateMotion>
</circle>
```

- **CSS** offset-path（现代、声明式）：`offset-path: path("M10,80 C..."); animation: move 3s linear infinite;` 配合 `@keyframes move { to { offset-distance: 100%; } }` 和 `offset-rotate: auto`。

### 动画渐变和滤镜

渐变：动画 `gradientTransform` 或停止偏移。一个光泽扫过：

```svg
<linearGradient id="sheen">
  <stop offset="0%"  stop-color="#fff" stop-opacity="0"/>
  <stop offset="50%" stop-color="#fff" stop-opacity=".8"/>
  <stop offset="100%" stop-color="#fff" stop-opacity="0"/>
  <animateTransform attributeName="gradientTransform" type="translate"
    from="-1 0" to="1 0" dur="2s" repeatCount="indefinite"/>
</linearGradient>
```

滤镜：动画 `feDisplacementMap` `scale` 以实现粘稠/波动效果，`feGaussianBlur` `stdDeviation` 以实现焦点拉取，或 `feColorMatrix`/`feFlood` 以实现发光。滤镜是绘制密集的——尽量少动画，并在可能的情况下优先使用 `transform`/`opacity`。

## 实现选择（快速选择）

| 需求 | 使用 |
|------|-----|
| 单个声明式绘制/淡出 | CSS |
| 独立、无需 JS 打包 | SMIL (`<animate*>` 在 SVG 中) |
| 协调、可滚动、滚动绑定 | GSAP |
| 不匹配点数的变形 | GSAP MorphSVG 或 Flubber |
| 沿路径运动并旋转 | GSAP MotionPath / CSS offset-path |

SMIL 注意事项：不支持 IE/旧 Edge，历史上标记为弃用；对于最大覆盖范围或滚动同步，优先选择 CSS 或 JS。SMIL 对于在常青浏览器中的独立图标资源仍然很好。

## 创建和优化

- 使用 **SVGO** 构建和清理：保留 `viewBox`，删除编辑器元数据，但禁用 `cleanupIds`/`removeViewBox` 和任何重命名您从 CSS/JS/SMIL 引用的 ID 的插件。如果您动画单个子路径或形状，请禁用 `mergePaths` 和 `convertShapeToPath`。
- 在 DOM 中内联 SVG（不是 `<img src>`），以便 CSS/JS 可以访问其内部；嵌入的 SVG 只能通过内部 SMIL/CSS 自动画。
- 设置显式的 `viewBox` 并避免固定的 `width`/`height`，以便资产流畅缩放。
- 对于描边绘制，确保路径是实际的描边（`fill:none; stroke:...`），而不是填充轮廓——`dashoffset` 仅影响描边。
- 尊重 `prefers-reduced-motion`：限制循环/大运动；保持静态最终状态。

## 交付和验证（独立 HTML）

> **打包辅助工具**（`scripts/`）：`scripts/seek-shot.sh anim.html 0 1.5 3` 冻结 `?t=N` 捆绑并捕获每个时刻；`scripts/contact-sheet.sh sheet.png frame-*.png` 将它们平铺以供一目了然地审查。参见 `scripts/README.md`。

对于自包含的图标/标志/描边，交付物是**一个直接在浏览器中打开的 HTML 文件**——在标记中内联 SVG，使用一个机制驱动动画，无需构建步骤。一个文件是矢量资产的正确层级；不要使用打包器。

**输出合同：**
- 一个 `.html` 文件：内联 `<svg>`，加上 CSS `@keyframes` / 一个 `<script>` 带来自 CDN 的 GSAP / SMIL `<animate*>`——选择一个驱动器。
- 包含与该驱动器匹配的查找手柄，以便任何时刻都可以冻结以供截图。

**查找手柄——冻结精确时刻。** `?t=N` 查找并暂停，以便截图落在静止帧上。使用与 SVG 动画方式匹配的机制：

```html
<script>
  const t = new URLSearchParams(location.search).get("t");
  if (t !== null) {
    const N = parseFloat(t);
    // SMIL: 暂停 SVG 的时钟并滚动它
    const svg = document.querySelector("svg");
    svg.pauseAnimations(); svg.setCurrentTime(N);
    // CSS @keyframes 描边绘制：el.style.animationDelay=(-N)+"s"; el.style.animationPlayState="paused";
    // GSAP 时间线：tl.pause(); tl.seek(N);
  }
  window.__ready = true;
</script>
```

**验证循环——渲染 → 冻结 → 截图 → 检查：** 在开始/中间/结束（`?t=0`，`?t=<dur/2>`，`?t=<dur>`）打开文件，截图每个，并检查**保真度**（描边绘制方向正确，变形端点干净）加上**伪影**（路径被 `viewBox` 裁剪，描边从陈旧的 dashoffset 消失，FOUC，变形接缝处的卡顿）。任何无头工具都可以：

```bash
npx playwright screenshot --wait-for-timeout=500 "file://$PWD/icon.html?t=0.7" frame-mid.png
```

**在您完成之前：**
1. 独立打开——无控制台错误，内联 SVG 可达，CDN（如果有）加载。
2. 您的驱动器的查找机制可以冻结确定性帧。
3. 在开始/中间/结束截图——与简报匹配，无裁剪或 `viewBox` 描边偏移。
4. 尊重 `prefers-reduced-motion`——限制循环/大运动，保持静态最终状态。
5. 缓动是故意的——`ease`/GSAP 缓动是故意选择的，没有意外的 `linear` 描边。

## 参考文件

- `references/svg-techniques.md` — 完整的 dashoffset 数学和 `getTotalLength` 陷阱，`pathLength="1"` 标准化，GSAP MorphSVG 与 Flubber 决策指南和代码，一个图标切换变形（汉堡包↔关闭），MotionPath/offset-path 详细信息，SMIL 对比 CSS 对比 JS 的权衡，以及针对动画调整的 SVGO 配置。
