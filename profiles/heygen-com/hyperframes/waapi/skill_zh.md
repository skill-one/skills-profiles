# HyperFrames 的 Web 动画 API

HyperFrames 可以通过其 `waapi` 运行时适配器寻址 Web 动画 API 动画。WAAPI 在您需要原生浏览器关键帧、JavaScript 创建的时序且无需 GSAP 依赖时非常有用。

## 协议

- 在组合初始化期间同步创建动画。
- 使用 `element.animate(...)` 并设置有限的 `duration` 和 `iterations`。
- 使用 `fill: "both"` 以使寻址状态持久化。
- 创建动画后暂停动画，或让适配器在首次寻址时暂停它们。
- 避免使用回调和 Promise 处理渲染关键状态。

适配器调用 `document.getAnimations()`，将每个动画的 `currentTime` 设置为 HyperFrames 时间（以毫秒为单位），然后暂停它。

## 基本模式

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

## 错落模式

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

- 轻量级 DOM 动画，其中 CSS 关键帧过于僵化且无需 GSAP。
- 从结构化数据生成的动画。
- 可以用关键帧、延迟和偏移表示的简单时间轴。

## 避免

- 无限的 `iterations`。
- 依赖 `animation.finished` 来修改渲染关键的 DOM。
- 使用 `requestAnimationFrame`、计时器或 `performance.now()` 运行独立的时钟。
- 当变换和透明度可以表达运动时，避免动画布局属性。
- 假设剪辑本地起始时间是自动的。WAAPI 适配器寻址文档级动画时间；使用 `delay` 模型剪辑偏移量，或创建动画在由 HyperFrames 时序控制的可见性元素上。

## 验证

编辑 WAAPI 组合后：

```bash
npx hyperframes lint
npx hyperframes validate
```

## 致谢与参考

- HyperFrames 适配器源代码：`packages/core/src/runtime/adapters/waapi.ts`。
- MDN Web 动画 API 指南：https://developer.mozilla.org/docs/Web/API/Web_Animations_API/Using_the_Web_Animations_API
- MDN `Animation.currentTime`：https://developer.mozilla.org/en-US/docs/Web/API/Animation/currentTime
