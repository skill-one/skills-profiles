# Anime.js 用于 HyperFrames

HyperFrames 可以通过其 `animejs` 运行时适配器来寻址 Anime.js 实例。组合体拥有动画对象；HyperFrames 拥有时钟。

## 协议

- 在组合体初始化期间同步创建动画或时间轴。
- 设置 `autoplay: false` 以防止 Anime.js 在其自身时钟上自动推进。
- 将每个返回的动画或时间轴注册到 `window.__hfAnime` 上。
- 使用有限时长和循环次数。
- 避免基于墙上时钟时间、网络状态或未播种随机性的回调，这些回调会修改 DOM。

适配器使用 `instance.seek(timeMs)` 寻址每个注册的实例，其中 `timeMs` 是 HyperFrames 时间（以毫秒为单位）。

## 基本模式

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

如果你使用 ES 模块构建，适配器不关心实例是如何创建的。它只需要返回的对象能够暴露 `seek()`、`pause()`，并且最好还能暴露 `play()`：

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

## 合理使用场景

- 小型 SVG 和 DOM 装饰，其中 Anime.js 语法紧凑。
- 可转换为寻址驱动的导入 Anime.js 示例。
- 多个独立的微动画被推入同一注册表中。

除非用户明确要求使用 Anime.js，否则应使用 GSAP 进行复杂场景序列化。GSAP 仍然是 HyperFrames 主要的创作路径。

## 避免

- 将 `autoplay` 保持为 Anime.js 的默认值。
- 依赖 `anime.running` 自动发现，而不是显式的 `window.__hfAnime.push(...)`。
- 无限循环。根据组合体时长计算有限的重复次数。
- 在计时器、Promise、事件处理程序或异步资源加载后构建动画。

## 验证

编辑使用 Anime.js 的组合体后：

```bash
npx hyperframes lint
npx hyperframes validate
```

## 致谢与参考

- HyperFrames 适配器源代码：`packages/core/src/runtime/adapters/animejs.ts`。
- Anime.js 文档关于 `autoplay`、`pause()` 和 `seek()`：https://animejs.com/documentation/
