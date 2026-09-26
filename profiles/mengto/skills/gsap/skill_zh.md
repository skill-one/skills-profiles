# GSAP (GreenSock) — Web 动画技能

## 何时使用
- 高质量 UI/动效设计：入场动画、微交互、页面过渡
- 基于时间轴的序列（而非零散的 CSS 过渡）
- 基于滚动的叙事（配合 ScrollTrigger）
- 复杂的缓动曲线、错开、跨多个元素的编排

## 核心概念与 API
- 缓动动画：
  - `gsap.to(targets, vars)`
  - `gsap.from(targets, vars)`
  - `gsap.fromTo(targets, fromVars, toVars)`
- 时间轴：
  - `const tl = gsap.timeline({ defaults, repeat, yoyo, paused })`
  - 链式调用：`tl.to(...).from(...).addLabel('x').add(() => ...)`
  - 位置参数：绝对值 `1.2`、相对值 `"+=0.5"`、重叠 `"-=0.3"`、标签 `"intro"`
- 缓动曲线：`ease: "power2.out"`、`"expo.inOut"`、`"elastic.out(1, 0.3)"`
- 错开动画：`stagger: 0.05` 或 `{ each, from: "start|center|end|random", grid }`
- 性能友好的属性：
  - 优先使用变换属性（`x`、`y`、`scale`、`rotation`）和透明度（`autoAlpha`）
- ScrollTrigger 插件：
  - `gsap.registerPlugin(ScrollTrigger)`
  - 内联用法：`gsap.to(".box", { scrollTrigger: ".box", x: 500 })`
  - 高级用法：`scrollTrigger: { trigger, start, end, scrub, pin, snap, markers }`
  - 独立用法：`ScrollTrigger.create({ trigger, start, end, onUpdate, onToggle })`

## 常见问题（及解决方案）
- 动画布局属性（`top`/`left`/`width`/`height`）→ 卡顿
  - 使用变换属性，添加 `will-change: transform`，避免强制重排
- ScrollTrigger “未触发”因触发器尺寸/滚动容器问题
  - 确保触发器存在、有高度，并检查滚动容器（嵌套滚动需要配置）
- SPA/React 中未清理资源
  - 使用 `gsap.context()` 并在卸载时回滚；如有需要可销毁触发器（`ScrollTrigger.getAll().forEach(t => t.kill())`）
- FOUC / 字体/图片加载前测量
  - 在布局稳定后初始化；图片加载后运行 `ScrollTrigger.refresh()`

## 快速示例

### 1) 英雄版入场动画（错开）
```js
gsap.from(".hero [data-anim]", {
  y: 24,
  autoAlpha: 0,
  duration: 0.8,
  ease: "power2.out",
  stagger: 0.06,
});
```

### 2) 序列化时间轴
```js
const tl = gsap.timeline({ defaults: { ease: "power2.out", duration: 0.6 } });
tl.from(".nav", { y: -20, autoAlpha: 0 })
  .from(".hero-title", { y: 30, autoAlpha: 0 }, "-=0.2")
  .from(".hero-cta", { scale: 0.95, autoAlpha: 0 }, "-=0.2");
```

### 3) 滚动缓动固定区域
```js
gsap.registerPlugin(ScrollTrigger);

gsap.timeline({
  scrollTrigger: {
    trigger: ".story",
    start: "top top",
    end: "+=800",
    scrub: 1,
    pin: true,
  },
}).to(".story .panel", { xPercent: -200 });
```

## 需要用户确认的需求（若不明确）
- 是静态网站还是 SPA（React/Next/Vue）？是否需要页面过渡？
- 是否需要基于滚动的区域（固定/缓动/快进）？
- 性能约束（移动端支持、减少动画）？
