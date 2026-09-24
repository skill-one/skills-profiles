# GSAP

## HyperFrames Contract

HyperFrames 通过其 `gsap` 运行时适配器控制 GSAP。请同步创建暂停的 timeline，将其以精确的 `data-composition-id` 注册到 `window.__timelines` 上，然后让 HyperFrames 定位到该 timeline。

```html
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<script>
  window.__timelines = window.__timelines || {};
  const tl = gsap.timeline({ paused: true });

  tl.from(".title", { y: 48, opacity: 0, duration: 0.6, ease: "power3.out" }, 0);
  tl.to(".accent", { scaleX: 1, duration: 0.5, ease: "power2.out" }, 0.25);

  window.__timelines["main"] = tl; // key 必须与 composition root 上的 data-composition-id 一致
</script>
```

- 注册键必须与 composition root 的 `data-composition-id` 匹配。
- 不要在需要渲染的关键动效上调用 `tl.play()`。
- 不要在异步代码、定时器或事件处理器中创建 timeline。
- 保持循环有限。HyperFrames 渲染的是有限时长的视频。

## Core Tween Methods

- **gsap.to(targets, vars)** — 从当前状态动画到 `vars`。最常用。
- **gsap.from(targets, vars)** — 从 `vars` 动画到当前状态（入场动效）。
- **gsap.fromTo(targets, fromVars, toVars)** — 明确起始和结束状态。
- **gsap.set(targets, vars)** — 立即应用（持续时间为 0）。

始终使用 **camelCase** 属性名（例如 `backgroundColor`、`rotationX`）。

## Common vars

- **duration** — 秒数（默认 0.5）。
- **delay** — 开始前的秒数。
- **ease** — `"power1.out"`（默认）、`"power3.inOut"`、`"back.out(1.7)"`、`"elastic.out(1, 0.3)"`、`"none"`。
- **stagger** — 数字 `0.1` 或对象：`{ amount: 0.3, from: "center" }`、`{ each: 0.1, from: "random" }`。
- **overwrite** — `false`（默认）、`true` 或 `"auto"`。
- **repeat** — 有限数字；HyperFrames 中绝不可为 `-1`。从可见时长计算重复次数。**yoyo** — 配合 repeat 交替方向。
- **onComplete**、**onStart**、**onUpdate** — 回调函数。
- **immediateRender** — 默认在 `from()` / `fromTo()` 中为 `true`。在后续针对同一属性+元素的补间中设为 `false`，以避免被覆盖。

## Transforms and CSS

优先使用 GSAP 的 **transform 别名**，而非原始 `transform` 字符串：

| GSAP property               | 等价写法          |
| --------------------------- | ------------------- |
| `x`, `y`, `z`               | translateX/Y/Z（px） |
| `xPercent`, `yPercent`      | translateX/Y（%）   |
| `scale`, `scaleX`, `scaleY` | scale               |
| `rotation`                  | rotate（度）        |
| `rotationX`, `rotationY`    | 3D 旋转             |
| `skewX`, `skewY`            | skew                |
| `transformOrigin`           | transform-origin    |

- **autoAlpha** — 优先使用，而非 `opacity`。为 0 时同时设置 `visibility: hidden`。
- **CSS 变量** — `"--hue": 180`。
- **svgOrigin** _(仅 SVG)_ — 全局 SVG 坐标空间原点。不可与 `transformOrigin` 同时使用。
- **方向性旋转** — `"360_cw"`、`"-170_short"`、`"90_ccw"`。
- **clearProps** — `"all"` 或逗号分隔；完成后移除内联样式。
- **相对值** — `"+=20"`、`"-=10"`、`"*=2"`。

## Function-Based Values

```javascript
gsap.to(".item", {
  x: (i, target, targets) => i * 50,
  stagger: 0.1,
});
```

## Easing

内置缓动：`power1`–`power4`、`back`、`bounce`、`circ`、`elastic`、`expo`、`sine`。每个都有 `.in`、`.out`、`.inOut`。

## Defaults

```javascript
gsap.defaults({ duration: 0.6, ease: "power2.out" });
```

## Controlling Tweens

```javascript
const tween = gsap.to(".box", { x: 100 });
tween.pause();
tween.play();
tween.reverse();
tween.kill();
tween.progress(0.5);
tween.time(0.2);
```

## gsap.matchMedia()（响应式 + 无障碍）

仅在匹配媒体查询时运行设置；停止匹配时自动 revert。

```javascript
let mm = gsap.matchMedia();
mm.add(
  {
    isDesktop: "(min-width: 800px)",
    reduceMotion: "(prefers-reduced-motion: reduce)",
  },
  (context) => {
    const { isDesktop, reduceMotion } = context.conditions;
    gsap.to(".box", {
      rotation: isDesktop ? 360 : 180,
      duration: reduceMotion ? 0 : 2,
    });
  },
);
```

---

## Timelines

### Creating a Timeline

```javascript
const tl = gsap.timeline({ defaults: { duration: 0.5, ease: "power2.out" } });
tl.to(".a", { x: 100 }).to(".b", { y: 50 }).to(".c", { opacity: 0 });
```

### Position Parameter

第三个参数控制放置方式：

- **绝对**：`1` — 在 1 秒处
- **相对**：`"+=0.5"` — 结束后；`"-=0.2"` — 结束前
- **标签**：`"intro"`、`"intro+=0.3"`
- **对齐**：`"<"` — 与上一个同时开始；`">"` — 上一个结束后；`"<0.2"` — 上一个开始后 0.2 秒

```javascript
tl.to(".a", { x: 100 }, 0);
tl.to(".b", { y: 50 }, "<"); // 与 .a 同时开始
tl.to(".c", { opacity: 0 }, "<0.2"); // 在 .b 开始后 0.2 秒
```

### Labels

```javascript
tl.addLabel("intro", 0);
tl.to(".a", { x: 100 }, "intro");
tl.addLabel("outro", "+=0.5");
tl.play("outro");
tl.tweenFromTo("intro", "outro");
```

### Timeline Options

- **paused: true** — 创建时暂停；调用 `.play()` 启动。
- **repeat**、**yoyo** — 作用于整个 timeline。
- **defaults** — 变量合并到每个子补间中。

### Nesting Timelines

```javascript
const master = gsap.timeline();
const child = gsap.timeline();
child.to(".a", { x: 100 }).to(".b", { y: 50 });
master.add(child, 0);
```

### Playback Control

`tl.play()`、`tl.pause()`、`tl.reverse()`、`tl.restart()`、`tl.time(2)`、`tl.progress(0.5)`、`tl.kill()`。

---

## Performance

### Prefer Transform and Opacity

动画 `x`、`y`、`scale`、`rotation`、`opacity` 保持在合成器上。避免使用 `width`、`height`、`top`、`left`，当 transform 能实现相同效果时。

### will-change

```css
will-change: transform;
```

仅应用于确实会动画的元素。

### gsap.quickTo() for Frequent Updates

```javascript
let xTo = gsap.quickTo("#id", "x", { duration: 0.4, ease: "power3" }),
  yTo = gsap.quickTo("#id", "y", { duration: 0.4, ease: "power3" });
container.addEventListener("mousemove", (e) => {
  xTo(e.pageX);
  yTo(e.pageY);
});
```

### Stagger > Many Tweens

使用 `stagger` 替代带有手动延迟的多个补间。

### Cleanup

暂停或终止离屏动画。

---

## References (loaded on demand)

- **[references/effects.md](references/effects.md)** — 即用效果：打字机文字、音频可视化器。需要 HyperFrames 现成的效果模式时阅读。

## Best Practices

- 使用 camelCase 属性名；优先使用 transform 别名和 autoAlpha。
- 优先使用 timeline 替代带延迟的链式调用，使用位置参数。
- 使用 `addLabel()` 添加标签，便于阅读顺序。
- 将默认值传入 timeline 构造函数。
- 控制播放时存储补间/timeline 的返回值。

## Do Not

- 当 transform 足够时，动画布局属性（width/height/top/left）。
- 在同一个 SVG 元素上同时使用 svgOrigin 和 transformOrigin。
- 能用 timeline 顺序化时，使用带延迟的动画链式调用。
- 在 DOM 不存在之前创建补间。
- 跳过清理——始终在不再需要时终止补间。
- 在 HyperFrames 的组合中使用无限 repeat 值。使用从可见时长计算出的有限重复次数。

## Credits And References

- HyperFrames 适配器源码：`packages/core/src/runtime/adapters/gsap.ts`。
- GSAP 文档：https://gsap.com/docs/v3/
- GSAP timeline 暂停与 seek 行为：https://gsap.com/docs/v3/GSAP/Timeline/pause%28%29/
