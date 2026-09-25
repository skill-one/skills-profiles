# Anime.js 适配 HyperFrames

HyperFrames 可以通过其 `animejs` 运行时适配器定位 Anime.js 实例。组合拥有动画对象；HyperFrames 拥有时钟。

## 契约

- 在组合初始化过程中同步创建动画或时间轴。
- 设置 `autoplay: false`，以便 Anime.js 不会根据自身时钟自行推进。
- 将每个返回的动画或时间轴注册到 `window.__hfAnime`。
- 使用有限时长和循环次数。
- 避免根据墙钟时间、网络状态或未播种的随机性修改 DOM 的回调。

适配器通过 `instance.seek(timeMs)` 定位每个已注册的实例，其中 `timeMs` 为 HyperFrames 的时间（毫秒）。

## 基础模式

```html
<script src="https://cdn.jsdelivr.net/npm/animejs@4.0.2/lib/anime.iife.min.js"></script>
<script>
  const anim = anime({
    targets: ".mark",
    translateX: 280,
    rotate: "1turn",
    opacity: [0, 1],
    duration: 1200,
    easing: "easeOutExpo",
    autoplay: false,
  });

  window.__hfAnime = window.__hfAnime || [];
  window.__hfAnime.push(anim);
</script>
```

## 时间轴模式

```html
<script>
  const tl = anime.timeline({
    autoplay: false,
    easing: "easeOutCubic",
  });

  tl.add({
    targets: ".title",
    translateY: [40, 0],
    opacity: [0, 1],
    duration: 650,
  }).add(
    {
      targets: ".accent",
      scaleX: [0, 1],
      duration: 450,
    },
    250,
  );

  window.__hfAnime = window.__hfAnime || [];
  window.__hfAnime.push(tl);
</script>
```

## 模块构建

如果你使用 ES 模块构建版本，适配器不关心实例是以何种方式创建的。它只需要返回的对象暴露 `seek()`、`pause()`，并最好暴露 `play()`：

```html
<script type="module">
  import { animate } from "https://cdn.jsdelivr.net/npm/animejs/+esm";

  const anim = animate(".chip", {
    x: "18rem",
    duration: 900,
    autoplay: false,
  });

  window.__hfAnime = window.__hfAnime || [];
  window.__hfAnime.push(anim);
</script>
```

## 适用场景

- 适用于 Anime.js 语法简洁的小型 SVG 与 DOM 装饰效果。
- 可转换为由 seek 驱动的已导入 Anime.js 示例。
- 将多个相互独立的微动画推入同一个注册表。

除非用户明确要求使用 Anime.js，否则复杂场景序列化请使用 GSAP。GSAP 仍然是 HyperFrames 的主要创作路径。

## 避免使用

- 不要将 `autoplay` 设置为 Anime.js 的默认值。
- 不要依赖 `anime.running` 的自动发现，而应显式调用 `window.__hfAnime.push(...)`。
- 不要使用无限循环。根据组合时长计算有限的重复次数。
- 不要在定时器、Promise、事件处理程序或异步资源加载完成后创建动画。

## 验证

在编辑使用 Anime.js 的组合后：

```bash
npx hyperframes lint
npx hyperframes validate
```

## 致谢与参考

- HyperFrames 适配器源码：`packages/core/src/runtime/adapters/animejs.ts`。
- Anime.js 关于 `autoplay`、`pause()` 和 `seek()` 的文档：https://animejs.com/documentation/
