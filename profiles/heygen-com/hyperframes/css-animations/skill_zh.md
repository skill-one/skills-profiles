# HyperFrames 的 CSS 动画

HyperFrames 可以通过其 `css` 运行时适配器来寻址 CSS 关键帧动画。使用此功能来处理简单的重复图案、背景运动、闪烁、发光、遮罩以及非顺序装饰。

对于场景编排，通常使用 GSAP 更清晰。当运动属于单个元素且具有固定持续时间时，CSS 动画效果最佳。

## 合约

- 在运行时初始化完成前，将动画元素放置在 DOM 中。
- 为定时元素设置 `data-start` 值，以便本地动画时间与片段匹配。
- 使用有限的 `animation-duration` 和 `animation-iteration-count`，因为负延迟回退无法在没有 WAAPI 支持的 CSS 动画环境中表示无限持续时间。
- 优先使用 `animation-fill-mode: both`，以便寻址状态在活动运动前后保持。
- 避免依赖用户事件的墙钟 JavaScript、悬停触发的状态以及类切换。

适配器发现具有计算 `animation-name` 的元素，在可用时寻址其浏览器 `Animation` 对象，并在回退时使用负 `animation-delay` 暂停。

## 基本模式

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

## 错落模式

使用 CSS 自定义属性来避免重复关键帧：

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

## 适用场景

- 具有已知重复次数的装饰性循环。
- 遮罩、发光、闪烁、颗粒和微妙的视差层。
- 简单的单元素入场动画，使用完整的 JS 时间轴会过于复杂。

## 避免

- 无限 CSS 动画，除非你已验证浏览器暴露了可寻址的 WAAPI 支持的 CSS 动画对象。优先使用覆盖可见持续时间的有限迭代次数。
- 当使用变换效果时，避免动画布局属性如 `top`、`left`、`width` 或 `height`。
- 依赖悬停、焦点、滚动或媒体查询来触发关键渲染运动。
- 在启动后更改动画类，除非有另一个确定性时间轴控制该变化。

## 验证

编辑 CSS 动画组合后：

```bash
npx hyperframes lint
npx hyperframes validate
```

## 致谢与参考

- HyperFrames 适配器源代码：`packages/core/src/runtime/adapters/css.ts`。
- MDN CSS 动画文档：https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/animation
- MDN `animation-fill-mode`：https://developer.mozilla.org/en-US/docs/Web/CSS/animation-fill-mode
