# 滚动动画技能

## 工作流程
1. 确认动画样式、时间以及动画是否应一次性运行或重复运行。
2. 提供关键帧 + JS 观察器代码片段以及确切的 Tailwind 类名以应用。
3. 仅提供专注的微调（阈值、根边距、持续时间、延迟、变换/模糊值）。

## 使用清单
- 在 `<head>` 中插入 JS 代码片段，并在关键帧之后。
- 为元素添加动画类和 `animate-on-scroll`。
- 确保您的关键帧名称与 Tailwind 动画参考匹配。

## IntersectionObserver 触发
```html
<script>
  /*
    滚动时按顺序触发动画。需要动画关键帧。使用方法：

    1) 将此代码与动画关键帧代码一起插入 <head> 中。

    2) 添加到 Tailwind 类名：[animation:animationIn_0.8s_ease-out_0.1s_both] animate-on-scroll
  */
  (function () {
    // 注入用于暂停/运行状态的 CSS
    const style = document.createElement("style");
    style.textContent = `
      /* 默认：暂停 */
      .animate-on-scroll { animation-play-state: paused !important; }
      /* 由 JS 激活 */
      .animate-on-scroll.animate { animation-play-state: running !important; }
    `;
    document.head.appendChild(style);

    const once = true;

    if (!window.__inViewIO) {
      window.__inViewIO = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("animate");
            if (once) window.__inViewIO.unobserve(entry.target);
          }
        });
      }, { threshold: 0.2, rootMargin: "0px 0px -10% 0px" });
    }

    window.initInViewAnimations = function (selector = ".animate-on-scroll") {
      document.querySelectorAll(selector).forEach((el) => {
        window.__inViewIO.observe(el); // 重复观察是无操作的
      });
    };

    document.addEventListener("DOMContentLoaded", () => initInViewAnimations());
  })();
</script>
```

## 关键帧
```html
<style>
  /*
    按顺序引入动画。使用方法：

    1) 将此代码插入 <head>

    2) 添加到 Tailwind 类名：[animation:animationIn_0.8s_ease-out_0.1s_both]
  */
  @keyframes animationIn {
    0% {
      opacity: 0;
      transform: translateY(30px);
      filter: blur(8px);
    }

    100% {
      opacity: 1;
      transform: translateY(0);
      filter: blur(0px);
    }
  }
</style>
```

## Tailwind 示例
```html
<div class="animate-on-scroll [animation:animationIn_0.8s_ease-out_0.1s_both]">
  ...
</div>
```

## 自定义选项
- 触发：调整 `threshold` 和 `rootMargin` 以实现更早或更晚的显示。
- 重复：将 `once = false` 设置为允许重新进入时的重播。
- 运动效果：在关键帧中调整 `translateY` 和 `blur`。
- 时间：更改 Tailwind 动画值中的持续时间和延迟。

## 常见陷阱
- 忘记在 JS 代码片段之前包含关键帧。
- 使用与 Tailwind 动画不同的关键帧名称。
- 动画未运行，因为元素在观察器初始化之前已经处于视图中。

## 缺少规格时应询问的问题
- 动画应一次性运行还是每次元素重新进入时运行？
- 它们应在进入视口之前多久开始？
- 您想要什么运动样式（淡入、滑动、模糊、缩放）？
