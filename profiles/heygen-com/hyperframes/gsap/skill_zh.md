# GSAP

## HyperFrames 合同

HyperFrames 通过其 `gsap` 运行时适配器控制 GSAP。同步创建一个暂停的时间轴，在 `window.__timelines` 上注册它，并使用确切的 `data-composition-id`，然后让 HyperFrames 搜索它。

```html
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<script>
  window.__timelines = window.__timelines || {};
  const tl = gsap.timeline({ paused: true });

  tl.from(".title", { y: 48, opacity: 0, duration: 0.6, ease: "power3.out" }, 0);
  tl.to(".accent", { scaleX: 1, duration: 0.5, ease: "power2.out" }, 0.25);

  window.__timelines["main"] = tl; // key 必须与组合根上的 data-composition-id 匹配
</script>
```

- 注册键必须与组合根的 `data-composition-id` 匹配。
- 不要调用 `tl.play()` 进行渲染关键动画。
- 不要在异步代码、计时器或事件处理程序中构建时间轴。
- 保持循环有限。HyperFrames 渲染有限的视频持续时间。

## 核心补间方法

- **gsap.to(targets, vars)** — 从当前状态动画到 `vars`。最常用。
- **gsap.from(targets, vars)** — 从 `vars` 动画到当前状态（入场）。
- **gsap.fromTo(targets, fromVars, toVars)** — 明确的起始和结束。
- **gsap.set(targets, vars)** — 立即应用（持续时间 0）。

始终使用 **camelCase** 属性名称（例如 `backgroundColor`、`rotationX`）。

## 常用 vars

- **duration** — 秒（默认 0.5）。
- **delay** — 开始前的秒数。
- **ease** — `"power1.out"`（默认）、`"power3.inOut"`、`"back.out(1.7)"`、`"elastic.out(1, 0.3)"`、`"none"`。
- **stagger** — 数字 `0.1` 或对象：`{ amount: 0.3, from: "center" }`、`{ each: 0.1, from: "random" }`。
- **overwrite** — `false`（默认）、`true` 或 `"auto"`。
- **repeat** — 有限数字；HyperFrames 中永不使用 `-1`。根据可见持续时间计算重复次数。**yoyo** — 重复时交替方向。
- **onComplete**、**onStart**、**onUpdate** — 回调函数。
- **immediateRender** — 默认 `true` 对于 from()/fromTo()。在针对相同属性+元素的后续补间中设置为 `false` 以避免覆盖。

## 变换和 CSS

优先使用 GSAP 的 **变换别名** 而不是原始 `transform` 字符串：

| GSAP 属性               | 等效项          |
| ----------------------- | ------------------- |
| `x`、`y`、`z`               | translateX/Y/Z (px) |
| `xPercent`、`yPercent`      | translateX/Y in %   |
| `scale`、`scaleX`、`scaleY` | scale               |
| `rotation`                  | rotate (deg)        |
| `rotationX`、`rotationY`    | 3D 旋转           |
| `skewX`、`skewY`            | skew                |
| `transformOrigin`           | transform-origin    |

- **autoAlpha** — 优先于 `opacity`。在 0 时：也会设置 `visibility: hidden`。
- **CSS 变量** — `"--hue": 180`。
- **svgOrigin** _(仅限 SVG)_ — 全局 SVG 坐标空间原点。不要与 `transformOrigin` 结合使用。
- **方向旋转** — `"360_cw"`、`"-170_short"`、`"90_ccw"`。
- **clearProps** — `"all"` 或逗号分隔；在完成时移除内联样式。
- **相对值** — `"+=20"`、`"-=10"`、`"*=2"`。

## 基于函数的值

```javascript
gsap.to(".item", {
  x: (i, target, targets) => i * 50,
  stagger: 0.1,
});
```

## 缓动函数

内置缓动函数：`power1`–`power4`、`back`、`bounce`、`circ`、`elastic`、`expo`、`sine`。每个都有 `.in`、`.out`、`.inOut`。

## 默认值

```javascript
gsap.defaults({ duration: 0.6, ease: "power2.out" });
```

## 控制补间

```javascript
const tween = gsap.to(".box", { x: 100 });
tween.pause();
tween.play();
tween.reverse();
tween.kill();
tween.progress(0.5);
tween.time(0.2);
```

## gsap.matchMedia() (响应式 + 可访问性)

仅在媒体查询匹配时运行设置；停止匹配时自动还原。

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

## 时间轴

### 创建时间轴

```javascript
const tl = gsap.timeline({ defaults: { duration: 0.5, ease: "power2.out" } });
tl.to(".a", { x: 100 }).to(".b", { y: 50 }).to(".c", { opacity: 0 });
```

### 位置参数

第三个参数控制位置：

- **绝对**：`1` — 在 1 秒
- **相对**：`"+=0.5"` — 在结束之后；`"-=0.2"` — 在结束之前
- **标签**：`"intro"`、`"intro+=0.3"`
- **对齐**：`"<"` — 与前一个相同的开始；`">"` — 在前一个结束后；`"<0.2"` — 在前一个开始 0.2 秒后

```javascript
tl.to(".a", { x: 100 }, 0);
tl.to(".b", { y: 50 }, "<"); // 与 .a 相同的开始
tl.to(".c", { opacity: 0 }, "<0.2"); // 在 .b 开始 0.2 秒后
```

### 标签

```javascript
tl.addLabel("intro", 0);
tl.to(".a", { x: 100 }, "intro");
tl.addLabel("outro", "+=0.5");
tl.play("outro");
tl.tweenFromTo("intro", "outro");
```

### 时间轴选项

- **paused: true** — 创建暂停的；调用 `.play()` 开始。
- **repeat**、**yoyo** — 应用于整个时间轴。
- **defaults** — vars 合并到每个子补间中。

### 嵌套时间轴

```javascript
const master = gsap.timeline();
const child = gsap.timeline();
child.to(".a", { x: 100 }).to(".b", { y: 50 });
master.add(child, 0);
```

### 播放控制

`tl.play()`、`tl.pause()`、`tl.reverse()`、`tl.restart()`、`tl.time(2)`、`tl.progress(0.5)`、`tl.kill()`。

---

## 性能

### 优先使用变换和透明度

动画 `x`、`y`、`scale`、`rotation`、`opacity` 保持在合成器上。当变换可以实现相同效果时，避免使用 `width`、`height`、`top`、`left`。

### will-change

```css
will-change: transform;
```

仅对实际进行动画的元素使用。

### gsap.quickTo() 用于频繁更新

```javascript
let xTo = gsap.quickTo("#id", "x", { duration: 0.4, ease: "power3" }),
  yTo = gsap.quickTo("#id", "y", { duration: 0.4, ease: "power3" });
container.addEventListener("mousemove", (e) => {
  xTo(e.pageX);
  yTo(e.pageY);
});
```

### Stagger > 许多补间

使用 `stagger` 而不是具有手动延迟的单独补间。

### 清理

暂停或杀死屏幕外的动画。

---

## 参考（按需加载）

- **[references/effects.md](references/effects.md)** — 即用型效果：打字机文本、音频可视化器。在需要 HyperFrames 的现成效果模式时阅读。

## 最佳实践

- 使用 camelCase 属性名称；优先使用变换别名和 autoAlpha。
- 优先使用时间轴而不是使用延迟链；使用位置参数。
- 使用 `addLabel()` 添加标签以进行可读的顺序。
- 将默认值传递到时间轴构造函数。
- 存储补间/时间轴返回值以控制播放。

## 不要

- 当变换足够时，不要动画布局属性（width/height/top/left）。
- 在同一个 SVG 元素上同时使用 svgOrigin 和 transformOrigin。
- 当时间轴可以按顺序排列它们时，不要使用带有延迟的链式动画。
- 在 DOM 存在之前创建补间。
- 跳过清理——当不再需要时，始终杀死补间。
- 在 HyperFrames 组合中使用无限重复值。使用根据可见持续时间计算的有限重复次数。

## 致谢和参考

- HyperFrames 适配器源代码：`packages/core/src/runtime/adapters/gsap.ts`。
- GSAP 文档：https://gsap.com/docs/v3/
- GSAP 时间轴暂停和搜索行为：https://gsap.com/docs/v3/GSAP/Timeline/pause%28%29/
