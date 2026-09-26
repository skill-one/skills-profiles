# 电影感滚动叙事

## 使用场景
- 当页面需要呈现为用户滚动时逐渐展开的精品编辑故事时。
- 用户提到滚动驱动叙事、滚动关联动画、粘性卡片堆叠、视差滚动、分栏文本、预加载器或电影感推进效果。
- 作品集、工作室、产品或落地页需要分区域逐步展示并具有分层深度。
- 实现可以使用GSAP、ScrollTrigger和Lenis。

## 效果词汇
- 滚动驱动叙事：区域按序列在滚动时逐步展现。
- 滚动关联动画：进度直接与滚动关联，使用`scrub`。
- 滚动触发运动：当区域进入视口时开始动画。
- 错落式展现：文字、行、卡片或元素以小延迟进入。
- 逐步展现：不透明度、缩放、模糊、裁剪或位置随滚动进度变化。
- 粘性卡片堆叠：粘性卡片在下一张卡片到达时分层、缩放和退后。
- 视差滚动：背景和前景层以不同速度移动。
- 滚动 scrubbing：动画跟随滚动条通过`scrub: true`或`scrub: 1`。
- 动态排版：遮罩分栏文本运动，通常逐字或逐行。
- 预加载器：开启加载屏幕、进度条和引入过渡。

## 目标感觉
- 豪华编辑网站。
- 高端创意工作室作品集。
- 苹果级运动打磨。
- 现代 Awwwards 交互语言。
- 沉浸式电影感落地页。

避免：
- 弹跳、弹性或弹簧式运动。
- 侵略性缩放跳跃。
- 闪亮的游戏风格效果。
- 同时使用过多滚动效果。
- 导致页面难以阅读的滚动劫持。

## 核心技术栈

```bash
npm i gsap lenis
```

```js
import Lenis from "lenis";
import "lenis/dist/lenis.css";
import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

gsap.registerPlugin(ScrollTrigger);

const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

if (!reduceMotion) {
  const lenis = new Lenis({
    lerp: 0.08,
    smoothWheel: true,
    wheelMultiplier: 0.9,
  });

  lenis.on("scroll", ScrollTrigger.update);

  gsap.ticker.add((time) => {
    lenis.raf(time * 1000);
  });

  gsap.ticker.lagSmoothing(0);
}

window.addEventListener("load", () => ScrollTrigger.refresh());
```

## 运动标记
- 进入缓动：`power3.out`或`power4.out`。
- Scrub场景：`ease: "none"`配合`scrub: 0.8`到`1.4`。
- 文本展现时长：`0.8s`到`1.1s`。
- 卡片展现时长：`0.9s`到`1.2s`。
- 字词错落：`0.035s`到`0.07s`。
- 行错落：`0.08s`到`0.14s`。
- 卡片错落：`0.06s`到`0.1s`。
- 展现偏移：`y: 24`到`48`。
- 模糊：`4px`到`10px`，然后`0px`。
- 粘性卡片缩放深度：`1`降至`0.92`。

## 页面结构
1. 预加载器：黑色屏幕、进度条、品牌/标题、引入淡出。
2. 英雄区：图像视差滚动、遮罩标题展现、微妙的滚动提示。
3. 介绍：逐字动态排版。
4. 故事区域：滚动触发淡上、模糊入和裁剪展现。
5. 近期项目：粘性卡片堆叠，配合缩放和分层深度。
6. 图库或证明：滚动 scrubbed 水平或逐步展现。
7. 页脚：视差展现或缓慢向上过渡。

## 标记模式

```html
<div class="preloader" data-preloader>
  <div class="preloader__bar" data-preloader-bar></div>
</div>

<main>
  <section class="hero" data-parallax-section>
    <img data-parallax-layer data-speed="-0.18" src="/hero.jpg" alt="">
    <h1 data-split-reveal>设计以电影感的克制展开。</h1>
  </section>

  <section data-story-section>
    <p data-split-reveal="words">每个区块都带着宁静的意图到来。</p>
  </section>

  <section class="project-stack" data-sticky-stack>
    <article data-stack-card>项目一</article>
    <article data-stack-card>项目二</article>
    <article data-stack-card>项目三</article>
  </section>

  <footer data-footer-parallax>...</footer>
</main>
```

## 预加载器序列

使用预加载器设定电影感基调，然后过渡到英雄区展现。

```js
function initPreloader() {
  const loader = document.querySelector("[data-preloader]");
  const bar = document.querySelector("[data-preloader-bar]");
  if (!loader) return Promise.resolve();

  if (reduceMotion) {
    loader.remove();
    return Promise.resolve();
  }

  return new Promise((resolve) => {
    const tl = gsap.timeline({
      defaults: { ease: "power3.out" },
      onComplete: () => {
        loader.remove();
        resolve();
      },
    });

    tl.fromTo(bar, { scaleX: 0, transformOrigin: "left" }, { scaleX: 1, duration: 1.1 })
      .to(loader, { yPercent: -100, duration: 0.9, ease: "power4.inOut" }, "+=0.15");
  });
}
```

## 分栏文本展现

使用遮罩溢出容器。避免分割包含链接或有意义内联标记的文本。

```js
function splitWords(element) {
  if (element.dataset.splitReady === "true") return;

  const text = element.textContent || "";
  const parts = text.split(/(\s+)/);
  element.textContent = "";
  element.setAttribute("aria-label", text.trim());

  parts.forEach((part) => {
    if (!part.trim()) {
      element.appendChild(document.createTextNode(part));
      return;
    }

    const mask = document.createElement("span");
    const word = document.createElement("span");
    mask.className = "split-word-mask";
    word.className = "split-word";
    word.textContent = part;
    mask.setAttribute("aria-hidden", "true");
    mask.appendChild(word);
    element.appendChild(mask);
  });

  element.dataset.splitReady = "true";
}

function initSplitReveals() {
  if (reduceMotion) {
    gsap.set("[data-split-reveal]", { autoAlpha: 1 });
    return;
  }

  gsap.utils.toArray("[data-split-reveal]").forEach((element) => {
    splitWords(element);
    const words = element.querySelectorAll(".split-word");

    gsap.fromTo(
      words,
      { yPercent: 110, autoAlpha: 0, filter: "blur(8px)" },
      {
        yPercent: 0,
        autoAlpha: 1,
        filter: "blur(0px)",
        duration: 0.95,
        ease: "power4.out",
        stagger: 0.05,
        scrollTrigger: {
          trigger: element,
          start: "top 82%",
          once: true,
        },
      }
    );
  });
}
```

```css
.split-word-mask {
  display: inline-block;
  overflow: hidden;
  vertical-align: top;
}

.split-word {
  display: inline-block;
  will-change: transform, opacity, filter;
}
```

## 滚动触发展现

用于普通区域。应只播放一次，感觉协调，而不是抽搐。

```js
function initSectionReveals() {
  if (reduceMotion) {
    gsap.set("[data-story-section], [data-reveal-item]", { autoAlpha: 1, clearProps: "all" });
    return;
  }

  gsap.utils.toArray("[data-story-section]").forEach((section) => {
    const items = section.querySelectorAll("[data-reveal-item]");
    const targets = items.length ? items : section.children;

    gsap.fromTo(
      targets,
      { y: 36, autoAlpha: 0, filter: "blur(8px)" },
      {
        y: 0,
        autoAlpha: 1,
        filter: "blur(0px)",
        duration: 1,
        ease: "power4.out",
        stagger: 0.08,
        scrollTrigger: {
          trigger: section,
          start: "top 82%",
          once: true,
        },
      }
    );
  });
}
```

## 滚动关联推进

使用 scrubbed timelines 进行电影感推进。保持 scrubbed 动画线性，让滚动位置决定时间。

```js
function initProgressionScenes() {
  if (reduceMotion) return;

  gsap.utils.toArray("[data-progress-scene]").forEach((scene) => {
    const media = scene.querySelector("[data-progress-media]");
    const copy = scene.querySelectorAll("[data-progress-copy]");

    gsap.timeline({
      scrollTrigger: {
        trigger: scene,
        start: "top top",
        end: "+=140%",
        scrub: 1.1,
        pin: true,
        anticipatePin: 1,
      },
    })
      .fromTo(media, { scale: 1.08 }, { scale: 1, ease: "none" })
      .fromTo(copy, { autoAlpha: 0, y: 40 }, { autoAlpha: 1, y: 0, stagger: 0.15, ease: "none" }, 0.15);
  });
}
```

## 粘性卡片堆叠

使用`position: sticky`进行布局，使用 ScrollTrigger 进行分层缩放/深度。早先的卡片应在后继卡片到达时退后。

```css
[data-sticky-stack] {
  position: relative;
}

[data-stack-card] {
  position: sticky;
  top: 12vh;
  transform-origin: center top;
  will-change: transform, opacity;
}
```

```js
function initStickyCardStack() {
  if (reduceMotion) return;

  gsap.utils.toArray("[data-sticky-stack]").forEach((stack) => {
    const cards = gsap.utils.toArray(stack.querySelectorAll("[data-stack-card]"));

    cards.forEach((card, index) => {
      const nextCard = cards[index + 1];
      if (!nextCard) return;

      gsap.to(card, {
        scale: 0.92 + index * 0.015,
        autoAlpha: 0.72,
        y: -24,
        ease: "none",
        scrollTrigger: {
          trigger: nextCard,
          start: "top 78%",
          end: "top 24%",
          scrub: true,
          invalidateOnRefresh: true,
        },
      });
    });
  });
}
```

## 视差滚动

用于英雄图像、背景层和页脚展现。保持距离小。

```js
function initParallax() {
  if (reduceMotion) return;

  gsap.utils.toArray("[data-parallax-layer]").forEach((layer) => {
    const speed = Number(layer.dataset.speed || -0.16);
    const section = layer.closest("[data-parallax-section]") || layer;

    gsap.to(layer, {
      y: () => window.innerHeight * speed,
      ease: "none",
      scrollTrigger: {
        trigger: section,
        start: "top bottom",
        end: "bottom top",
        scrub: 1,
        invalidateOnRefresh: true,
      },
    });
  });
}
```

页脚视差展现：

```js
function initFooterReveal() {
  if (reduceMotion) return;

  const footer = document.querySelector("[data-footer-parallax]");
  if (!footer) return;

  gsap.fromTo(
    footer,
    { yPercent: -12, autoAlpha: 0.85 },
    {
      yPercent: 0,
      autoAlpha: 1,
      ease: "none",
      scrollTrigger: {
        trigger: footer,
        start: "top bottom",
        end: "top 45%",
        scrub: 1,
      },
    }
  );
}
```

## 构建顺序
1. 首先构建静态页面。
2. 添加预加载器和英雄区入口。
3. 添加分栏文本展现。
4. 添加分区域展现。
5. 添加粘性卡片堆叠推进。
6. 添加视差层。
7. 仅在故事需要时添加 scrubbed 固定场景。
8. 添加减少运动和触摸回退。
9. 在桌面和移动端运行浏览器 QA。

## 提示模板

```txt
创建具有平滑 Lenis 滚动、GSAP ScrollTrigger 动画、错落式文本展现、粘性卡片堆叠推进、视差背景、滚动 scrubbed 过渡、分区域叙事和沉浸式预加载动画的电影感滚动驱动落地页。使用分层深度、缩放过渡、渐进式不透明度变化和流畅的视口触发运动，为用户提供精品编辑体验。
```

## QA 检查清单
- 内容在禁用 JavaScript 时可读。
- 减少运动用户看到静态内容和没有平滑滚动层。
- 滚动触发展现只播放一次。
- 滚动关联场景有意使用`scrub`。
- 粘性卡片不会重叠页脚或困住页面。
- 视差运动保持微妙，不损害可读性。
- 预加载器即使图像加载缓慢也能可靠退出。
- `ScrollTrigger.refresh()`在图像/字体/布局变化后运行。
- 移动端简化固定或性能下降时无固定。
