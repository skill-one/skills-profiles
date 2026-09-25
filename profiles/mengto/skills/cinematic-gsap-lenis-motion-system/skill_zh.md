# 电影级 GSAP Lenis 动画系统

## 使用场景
- 当网站需要完整的顶级动画语言，而非孤立的单个动画时。
- 平滑滚动、滚动揭示、固定场景、视差效果、悬停动画和光标行为应感觉连贯。
- 目标风格是奢侈的编辑风格、苹果级别的精致感、创意工作室作品集或沉浸式电影叙事。
- 技术栈可以使用 GSAP、ScrollTrigger 和 Lenis。

## 动画风格
- 平滑、优雅、略微延迟且有意为之。
- 错开动画应引导阅读顺序。
- 分层运动应在不使界面感觉繁忙的情况下创造深度。
- ScrollTrigger 应在场景进入视口时开始，而不是对每个微小的滚动做出反应。
- 偏好微妙而非强烈。

避免：
- 弹跳、弹性、弹簧或俏皮的动画。
- 快速突兀的过渡。
- 大规模的跳跃。
- 过度动画化的 UI。
- 闪亮的游戏风格效果。

## 基础参数
- 缓动函数：`power3.out`、`power4.out`、`expo.out`。
- 滚动循环：`scrub: 0.8` 到 `1.4` 用于电影级延迟。
- 揭示：`0.75s` 到 `1.1s`。
- 悬停：`0.35s` 到 `0.6s`。
- 光标延迟：`0.25s` 到 `0.45s`。
- 文本错开：单词 `0.035s` 到 `0.07s`，行 `0.08s` 到 `0.14s`。
- 卡片错开：`0.06s` 到 `0.1s`。
- 揭示触发：`start: "top 82%"`。
- 固定过渡：`anticipatePin: 1`。

## 初始化

安装：

```bash
npm i gsap lenis
```

在 DOM 存在后只初始化一次。Lenis 通过 GSAP ticker 驱动其 RAF，因此 ScrollTrigger 和平滑滚动保持同步。

```js
import Lenis from "lenis";
import "lenis/dist/lenis.css";
import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

gsap.registerPlugin(ScrollTrigger);
gsap.defaults({ ease: "power3.out", duration: 0.85 });

const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

let lenis;

if (!reduceMotion) {
  lenis = new Lenis({
    lerp: 0.08,
    smoothWheel: true,
    wheelMultiplier: 0.9,
    anchors: true,
  });

  lenis.on("scroll", ScrollTrigger.update);

  gsap.ticker.add((time) => {
    lenis.raf(time * 1000);
  });

  gsap.ticker.lagSmoothing(0);
}

window.addEventListener("load", () => {
  ScrollTrigger.refresh();
});
```

## 标记 API

使用小的数据属性，以便动画系统可以在页面之间重复使用。

```html
<h1 data-motion-text="lines">具有电影级克制的数字产品。</h1>
<p data-motion-text="words">每次交互都应感觉刻意。</p>

<section data-reveal-group>
  <article data-reveal="fade-up" data-reveal-item>...</article>
  <article data-reveal="fade-up" data-reveal-item>...</article>
</section>

<figure data-image-reveal data-parallax-section>
  <img data-parallax-image src="/studio.jpg" alt="">
</figure>

<a data-magnetic data-cursor-label="探索" href="/work">探索</a>
<div data-cursor><span data-cursor-label></span></div>
```

## CSS 基础

```css
html.has-motion [data-motion-text],
html.has-motion [data-reveal],
html.has-motion [data-reveal-item],
html.has-motion [data-image-reveal] {
  visibility: hidden;
}

.motion-line-mask,
.motion-word-mask {
  display: inline-block;
  overflow: hidden;
  vertical-align: top;
}

.motion-line,
.motion-word {
  display: inline-block;
  will-change: transform, opacity, filter;
}

[data-image-reveal] {
  overflow: hidden;
}

[data-parallax-image] {
  display: block;
  width: 100%;
  height: 115%;
  object-fit: cover;
  will-change: transform;
}

[data-cursor] {
  position: fixed;
  left: 0;
  top: 0;
  z-index: 9999;
  pointer-events: none;
  mix-blend-mode: difference;
  transform: translate3d(-50%, -50%, 0);
  will-change: transform;
}

@media (prefers-reduced-motion: reduce), (pointer: coarse) {
  [data-cursor] {
    display: none;
  }
}
```

## 错开文本揭示

使用遮罩容器创建高级文本效果。当精确换行很重要时，优先使用手动行包装器。使用单词分割来创建灵活的响应式文本。

```js
document.documentElement.classList.add("has-motion");

function splitWords(element) {
  if (element.dataset.motionSplit === "true") return;

  const text = element.textContent || "";
  const parts = text.split(/(\s+)/);

  element.textContent = "";
  element.setAttribute("aria-label", text.trim());

  let index = 0;
  parts.forEach((part) => {
    if (!part.trim()) {
      element.appendChild(document.createTextNode(part));
      return;
    }

    const mask = document.createElement("span");
    const word = document.createElement("span");

    mask.className = "motion-word-mask";
    mask.setAttribute("aria-hidden", "true");
    word.className = "motion-word";
    word.textContent = part;
    word.style.setProperty("--word-index", index);

    mask.appendChild(word);
    element.appendChild(mask);
    index += 1;
  });

  element.dataset.motionSplit = "true";
}

function splitLines(element) {
  if (element.dataset.motionLineSplit === "true") return;
  if (element.querySelector(".motion-line")) return;

  const text = (element.textContent || "").trim();
  const lines = text.split(/\n+/).map((line) => line.trim()).filter(Boolean);
  if (lines.length < 2) return;

  element.textContent = "";
  element.setAttribute("aria-label", text);

  lines.forEach((line) => {
    const mask = document.createElement("span");
    const inner = document.createElement("span");

    mask.className = "motion-line-mask";
    mask.setAttribute("aria-hidden", "true");
    inner.className = "motion-line";
    inner.textContent = line;

    mask.appendChild(inner);
    element.appendChild(mask);
    element.appendChild(document.createTextNode(" "));
  });

  element.dataset.motionLineSplit = "true";
}

function initTextReveals() {
  if (reduceMotion) {
    gsap.set("[data-motion-text]", { autoAlpha: 1, clearProps: "all" });
    return;
  }

  gsap.utils.toArray("[data-motion-text='words']").forEach((element) => {
    splitWords(element);
    const words = element.querySelectorAll(".motion-word");

    gsap.set(element, { autoAlpha: 1 });
    gsap.fromTo(
      words,
      { yPercent: 110, autoAlpha: 0, filter: "blur(8px)" },
      {
        yPercent: 0,
        autoAlpha: 1,
        filter: "blur(0px)",
        duration: 0.9,
        ease: "power4.out",
        stagger: 0.055,
        scrollTrigger: {
          trigger: element,
          start: "top 82%",
          once: true,
        },
      }
    );
  });

  gsap.utils.toArray("[data-motion-text='lines']").forEach((element) => {
    splitLines(element);
    const lines = element.querySelectorAll(".motion-line");
    const targets = lines.length ? lines : element.children;

    gsap.set(element, { autoAlpha: 1 });
    gsap.fromTo(
      targets,
      { yPercent: 100, autoAlpha: 0, filter: "blur(8px)" },
      {
        yPercent: 0,
        autoAlpha: 1,
        filter: "blur(0px)",
        duration: 1,
        ease: "power4.out",
        stagger: 0.11,
        scrollTrigger: {
          trigger: element,
          start: "top 84%",
          once: true,
        },
      }
    );
  });
}
```

精确换行时的行标记：

```html
<h2 data-motion-text="lines">
  <span class="motion-line-mask"><span class="motion-line">电影级动画</span></span>
  <span class="motion-line-mask"><span class="motion-line">具有编辑风格克制。</span></span>
</h2>
```

## 滚动揭示

创建一个小型揭示预设映射。使用 `autoAlpha`、变换和轻微的模糊。仅在大型元素上谨慎使用模糊。

```js
const revealPresets = {
  "fade-up": { from: { y: 32, autoAlpha: 0 }, to: { y: 0, autoAlpha: 1 } },
  "blur-in": { from: { y: 18, autoAlpha: 0, filter: "blur(10px)" }, to: { y: 0, autoAlpha: 1, filter: "blur(0px)" } },
  "scale": { from: { scale: 0.96, autoAlpha: 0 }, to: { scale: 1, autoAlpha: 1 } },
  "slide-left": { from: { x: 48, autoAlpha: 0 }, to: { x: 0, autoAlpha: 1 } },
  "slide-right": { from: { x: -48, autoAlpha: 0 }, to: { x: 0, autoAlpha: 1 } },
};

function initScrollReveals() {
  if (reduceMotion) {
    gsap.set("[data-reveal], [data-reveal-item]", { autoAlpha: 1, clearProps: "all" });
    return;
  }

  gsap.utils.toArray("[data-reveal-group]").forEach((group) => {
    const items = group.querySelectorAll("[data-reveal-item]");
    gsap.set(group, { autoAlpha: 1 });
    gsap.fromTo(
      items,
      { y: 36, autoAlpha: 0, filter: "blur(8px)" },
      {
        y: 0,
        autoAlpha: 1,
        filter: "blur(0px)",
        duration: 0.95,
        ease: "power4.out",
        stagger: 0.075,
        scrollTrigger: {
          trigger: group,
          start: "top 82%",
          once: true,
        },
      }
    );
  });

  gsap.utils.toArray("[data-reveal]:not([data-reveal-item])").forEach((element) => {
    const preset = revealPresets[element.dataset.reveal] || revealPresets["fade-up"];
    gsap.set(element, { autoAlpha: 1 });
    gsap.fromTo(element, preset.from, {
      ...preset.to,
      duration: 0.9,
      ease: "power4.out",
      delay: Number(element.dataset.revealDelay || 0),
      scrollTrigger: {
        trigger: element,
        start: "top 84%",
        once: true,
      },
    });
  });
}
```

## 剪影图像揭示

```js
function initImageReveals() {
  if (reduceMotion) {
    gsap.set("[data-image-reveal]", { autoAlpha: 1, clipPath: "none" });
    return;
  }

  gsap.utils.toArray("[data-image-reveal]").forEach((figure) => {
    const image = figure.querySelector("img");
    gsap.set(figure, { autoAlpha: 1 });

    const tl = gsap.timeline({
      scrollTrigger: {
        trigger: figure,
        start: "top 82%",
        once: true,
      },
    });

    tl.fromTo(
      figure,
      { clipPath: "inset(0 0 100% 0)" },
      { clipPath: "inset(0 0 0% 0)", duration: 1.1, ease: "power4.out" }
    ).fromTo(
      image,
      { scale: 1.08, autoAlpha: 0.75 },
      { scale: 1, autoAlpha: 1, duration: 1.2, ease: "power4.out" },
      0
    );
  });
}
```

## 视差动画

使用速度差异而非戏剧性运动。背景比内容移动得更慢。前景装饰元素移动得略快。

```js
function initParallax() {
  if (reduceMotion) return;

  gsap.utils.toArray("[data-parallax-image], [data-parallax-layer]").forEach((layer) => {
    const speed = Number(layer.dataset.parallaxSpeed || 0.18);
    const section = layer.closest("[data-parallax-section]") || layer;

    gsap.to(layer, {
      y: () => window.innerHeight * speed * -1,
      ease: "none",
      scrollTrigger: {
        trigger: section,
        start: "top bottom",
        end: "bottom top",
        scrub: 1.2,
        invalidateOnRefresh: true,
      },
    });
  });
}
```

## 固定滚动区域

使用固定区域仅用于故事时刻。保持滚动同步运动线性，然后在场景内部层叠缓动的揭示补间。

```js
function initHorizontalGalleries() {
  if (reduceMotion) return;

  gsap.utils.toArray("[data-horizontal-gallery]").forEach((section) => {
    const track = section.querySelector("[data-horizontal-track]");
    if (!track) return;

    gsap.to(track, {
      x: () => -(track.scrollWidth - window.innerWidth),
      ease: "none",
      scrollTrigger: {
        trigger: section,
        start: "top top",
        end: () => `+=${track.scrollWidth}`,
        scrub: 1,
        pin: true,
        anticipatePin: 1,
        invalidateOnRefresh: true,
      },
    });
  });
}
```

粘性故事讲述模式：

```js
function initStoryScenes() {
  if (reduceMotion) return;

  gsap.utils.toArray("[data-story-scene]").forEach((scene) => {
    const panels = scene.querySelectorAll("[data-story-panel]");

    gsap.timeline({
      scrollTrigger: {
        trigger: scene,
        start: "top top",
        end: () => `+=${panels.length * window.innerHeight}`,
        scrub: 1.1,
        pin: true,
        anticipatePin: 1,
      },
    })
      .to(panels, { yPercent: -100 * (panels.length - 1), ease: "none" })
      .to(scene.querySelectorAll("[data-story-depth]"), { yPercent: -16, ease: "none" }, 0);
  });
}
```

## 高级悬停交互

使用 GSAP `quickTo` 实现磁性运动，以便悬停跟随指针，而无需在每次事件上重新创建补间。

```js
function initMagnetic() {
  if (reduceMotion || window.matchMedia("(pointer: coarse)").matches) return;

  gsap.utils.toArray("[data-magnetic]").forEach((element) => {
    const strength = Number(element.dataset.magnetic || 0.18);
    const xTo = gsap.quickTo(element, "x", { duration: 0.45, ease: "power3.out" });
    const yTo = gsap.quickTo(element, "y", { duration: 0.45, ease: "power3.out" });

    element.addEventListener("pointermove", (event) => {
      const rect = element.getBoundingClientRect();
      const x = (event.clientX - rect.left - rect.width / 2) * strength;
      const y = (event.clientY - rect.top - rect.height / 2) * strength;

      xTo(x);
      yTo(y);
    });

    element.addEventListener("pointerleave", () => {
      xTo(0);
      yTo(0);
    });
  });
}
```

悬停配方：
- 磁性按钮：仅转换 `x/y`，保持缩放低于 `1.03`。
- 磁性卡片：添加 `rotateX/rotateY` 低于 `4deg`。
- 图像缩放：`scale: 1` 到 `1.06`，持续时间 `0.7s`，缓动 `power3.out`。
- 灰度到彩色：仅在小型/中型媒体上过渡滤镜。
- 动画箭头：移动图标 `x: 0` 到 `x: 6`，淡入重复箭头。
- 方向性悬停：计算指针进入侧，但保持运动低于 `16px`。

## 自定义光标

使用光标跟随作为氛围，而非装饰。在触摸设备上隐藏它。

```js
function initCursor() {
  if (reduceMotion || window.matchMedia("(pointer: coarse)").matches) return;

  const cursor = document.querySelector("[data-cursor]");
  if (!cursor) return;

  const label = cursor.querySelector("[data-cursor-label]");
  const xTo = gsap.quickTo(cursor, "x", { duration: 0.35, ease: "power3.out" });
  const yTo = gsap.quickTo(cursor, "y", { duration: 0.35, ease: "power3.out" });

  document.addEventListener("pointermove", (event) => {
    xTo(event.clientX);
    yTo(event.clientY);
  });

  gsap.utils.toArray("[data-cursor-label]")
    .filter((target) => !cursor.contains(target))
    .forEach((target) => {
      target.addEventListener("pointerenter", () => {
        if (label) label.textContent = target.dataset.cursorLabel || "";
        gsap.to(cursor, { scale: 1.75, duration: 0.35, ease: "power3.out" });
      });

      target.addEventListener("pointerleave", () => {
        if (label) label.textContent = "";
        gsap.to(cursor, { scale: 1, duration: 0.35, ease: "power3.out" });
      });
    });
}
```

## 鼠标响应层

为每个区域使用一个指针监听器。深度应几乎看不见。

```js
function initMouseParallax() {
  if (reduceMotion || window.matchMedia("(pointer: coarse)").matches) return;

  gsap.utils.toArray("[data-mouse-parallax]").forEach((section) => {
    const layers = section.querySelectorAll("[data-mouse-depth]");
    const setters = Array.from(layers).map((layer) => ({
      layer,
      depth: Number(layer.dataset.mouseDepth || 0.04),
      xTo: gsap.quickTo(layer, "x", { duration: 0.8, ease: "power3.out" }),
      yTo: gsap.quickTo(layer, "y", { duration: 0.8, ease: "power3.out" }),
    }));

    section.addEventListener("pointermove", (event) => {
      const rect = section.getBoundingClientRect();
      const x = event.clientX - rect.left - rect.width / 2;
      const y = event.clientY - rect.top - rect.height / 2;

      setters.forEach(({ depth, xTo, yTo }) => {
        xTo(x * depth);
        yTo(y * depth);
      });
    });

    section.addEventListener("pointerleave", () => {
      setters.forEach(({ xTo, yTo }) => {
        xTo(0);
        yTo(0);
      });
    });
  });
}
```

## 舞台规则
- 主角：背景或媒体首先开始，标题行其次，辅助文本第三，CTA 最后。
- 区域：标签首先，标题其次，媒体第三，卡片/详情最后。
- 固定场景：每个视口一个想法。避免堆叠太多同时的转换。
- 视差：背景移动较慢，前景略快，文本基本稳定。
- 光标和悬停效果应支持导航意图，而非与之冲突。

## 性能规则
- 动画 `transform`、`opacity` 和短命的 `clip-path`。
- 仅在文本或小型元素上使用 `filter: blur()`。
- 保持固定区域有限，并在移动设备上测试它们。
- 仅对实际动画的元素添加 `will-change`。
- 在图像、字体或布局更改后使用 `ScrollTrigger.refresh()`。
- 在 React 或 SPA 路由中，将设置包装在 `gsap.context()` 中，并在清理时调用 `ctx.revert()`。
- 在页面过渡期间杀死或还原 ScrollTriggers，然后再初始化下一个路由。

## 初始化顺序

```js
initTextReveals();
initScrollReveals();
initImageReveals();
initParallax();
initHorizontalGalleries();
initStoryScenes();
initMagnetic();
initCursor();
initMouseParallax();
ScrollTrigger.refresh();
```

## QA 检查清单
- 文本和内容在禁用 JavaScript 时保持可见。
- 减少运动用户获得静态内容和没有平滑滚动劫持。
- 滚动揭示应只动画一次，除非设计明确要求重播。
- 固定区域不应与下一个区域重叠。
- 悬停和光标交互在触摸设备上被禁用。
- 在滚动期间没有动画化布局属性。
- 如果移除所有装饰性运动，页面仍然感觉可读。
