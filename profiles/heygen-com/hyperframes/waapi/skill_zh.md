# HyperFrames 的 Web Animations API

HyperFrames 可以通过其 `waapi` 运行时适配器对 Web Animations API 动画进行寻址。WAAPI 非常适用于当你需要原生浏览器关键帧、由 JavaScript 创建的计时，且无需使用 GSAP 的场景。

## 契约

- 在组合初始化期间同步创建动画。
- 使用 `element.animate(...)`，并指定有限的 `duration` 和 `iterations`。
- 使用 `fill: "both"`，以便寻址状态得以保留。
- 创建动画后暂停，或在首次寻址时由适配器暂停动画。
- 避免在影响渲染状态的关键部分使用回调和 Promise。

该适配器调用 `document.getAnimations()`，将每个动画的 `currentTime` 设置为 HyperFrames 的时间（以毫秒为单位），然后暂停该动画。

## 基础模式

```html
<div id="orb" class="clip orb" data-start="2" data-duration="3" data-track-index="2"></div>

<script>
  const orb = document.getElementById("orb");
  const animation = orb.animate(
    [
      { transform: "translate3d(-160px, 0, 0) scale(0.8)", opacity: 0 },
      { transform: "translate3d(0, 0, 0) scale(1)", opacity: 1, offset: 0.35 },
      { transform: "translate3d(120px, 0, 0) scale(1.08)", opacity: 1 },
    ],
    {
      duration: 3000,
      delay: 2000,
      easing: "cubic-bezier(0.2, 0, 0, 1)",
      fill: "both",
      iterations: 1,
    },
  );

  animation.pause();
</script>
```

## 交错模式

```js
document.querySelectorAll(".token").forEach((token, index) => {
  const animation = token.animate(
    [
      { transform: "translateY(24px)", opacity: 0 },
      { transform: "translateY(0)", opacity: 1 },
    ],
    {
      duration: 620,
      delay: index * 80,
      easing: "cubic-bezier(0.2, 0, 0, 1)",
      fill: "both",
      iterations: 1,
    },
  );
  animation.pause();
});
```

## 适用场景

- 当 CSS 关键帧过于僵化且无需使用 GSAP 时的轻量级 DOM 运动。
- 基于结构化数据生成的动画。
- 可表示为关键帧、延迟和偏移的简单时间线。

## 避免使用

- 无限 `iterations`。
- 依赖 `animation.finished` 来修改影响渲染状态的关键 DOM。
- 使用 `requestAnimationFrame`、定时器或 `performance.now()` 运行独立的时钟。
- 在变换（transforms）和透明度（opacity）足以表达运动时，动画布局属性。
- 默认认为剪辑本地起始时间自动生效。WAAPI 适配器寻址的是文档级别的动画时间；请使用 `delay` 来模拟剪辑偏移，或在 HyperFrames 时间控制可见性的元素上创建动画。

## 校验

编辑 WAAPI 组合后：

```bash
npx hyperframes lint
npx hyperframes validate
```

## 致谢与参考资料

- HyperFrames 适配器源码：`packages/core/src/runtime/adapters/waapi.ts`。
- MDN Web Animations API 指南：https://developer.mozilla.org/docs/Web/API/Web_Animations_API/Using_the_Web_Animations_API
- MDN `Animation.currentTime`：https://developer.mozilla.org/en-US/docs/Web/API/Animation/currentTime
