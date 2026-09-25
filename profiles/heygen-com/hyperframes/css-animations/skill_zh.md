# HyperFrames 的 CSS 动画

HyperFrames 可以通过其 `css` 运行时适配器来定位并播放 CSS 关键帧动画。请将其用于简单的重复图案、背景运动、闪烁、发光、遮罩以及非顺序装饰。

对于场景编排，GSAP 通常更清晰。CSS 动画在运动归属于单个元素且持续时间固定时表现最佳。

## 契约

- 在运行时初始化完成前，将需要动画的元素放入 DOM。
- 为带有时序的元素设置 `data-start` 值，使本地动画时间与片段（clip）匹配。
- 使用有限的 `animation-duration` 和 `animation-iteration-count`，因为在没有基于 WAAPI 的 CSS 动画支持的环境中，负延迟回退方案无法表示无界时长。
- 优先使用 `animation-fill-mode: both`，以便在活动运动之前和之后保持已寻址的状态。
- 避免使用基于挂钟时间的 JavaScript、由悬停触发的状态，以及依赖用户事件触发类切换的方案。

该适配器通过计算出的 `animation-name` 发现元素，在可用时定位其浏览器的 `Animation` 句柄，并回退至通过负 `animation-delay` 进行暂停。

## 基础模式

```html
<div
  id="pulse-ring"
  class="clip pulse-ring"
  data-start="0"
  data-duration="4"
  data-track-index="2"
></div>

<style>
  .pulse-ring {
    width: 280px;
    height: 280px;
    border: 4px solid rgba(255, 255, 255, 0.7);
    border-radius: 50%;
    animation-name: pulse-ring;
    animation-duration: 1200ms;
    animation-timing-function: cubic-bezier(0.2, 0, 0, 1);
    animation-iteration-count: 3;
    animation-fill-mode: both;
  }

  @keyframes pulse-ring {
    from {
      opacity: 0;
      transform: scale(0.82);
    }
    35% {
      opacity: 1;
    }
    to {
      opacity: 0;
      transform: scale(1.18);
    }
  }
</style>
```

## 交错模式

使用 CSS 自定义属性，以避免重复定义关键帧：

```html
<div class="clip dots" data-start="1" data-duration="3" data-track-index="3">
  <span style="--i: 0"></span>
  <span style="--i: 1"></span>
  <span style="--i: 2"></span>
</div>

<style>
  .dots span {
    display: inline-block;
    width: 18px;
    height: 18px;
    margin-right: 10px;
    border-radius: 50%;
    background: currentColor;
    animation: dot-pop 900ms ease-out both;
    animation-delay: calc(var(--i) * 120ms);
  }

  @keyframes dot-pop {
    from {
      opacity: 0;
      transform: translateY(18px) scale(0.75);
    }
    to {
      opacity: 1;
      transform: translateY(0) scale(1);
    }
  }
</style>
```

## 良好用途

- 具有已知重复次数的装饰性循环。
- 遮罩、发光、闪烁、颗粒以及微妙的视差层。
- 对于全量 JS 时间线来说过于繁冗的简单单元素入场效果。

## 应避免

- 除非已验证浏览器支持可寻址的基于 WAAPI 的 CSS 动画句柄，否则避免使用无限 CSS 动画。优先使用能够覆盖可见时长的有限迭代次数。
- 当 transform 可用时，避免动画化 `top`、`left`、`width` 或 `height` 等布局属性。
- 不要依赖悬停、聚焦、滚动或媒体查询来触发对渲染至关重要的运动。
- 启动后更改动画类，除非有其他确定性时间线控制这些更改。

## 验证

编辑 CSS 动画组合后：

```bash
npx hyperframes lint
npx hyperframes validate
```

## 致谢与参考

- HyperFrames 适配器源码：`packages/core/src/runtime/adapters/css.ts`。
- MDN CSS 动画文档：https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/animation
- MDN `animation-fill-mode` 文档：https://developer.mozilla.org/en-US/docs/Web/CSS/animation-fill-mode
