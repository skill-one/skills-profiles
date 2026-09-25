# GSAP 性能

> 内容选自 GreenSock 官方 GSAP 技巧：https://github.com/greensock/gsap-skills

## 何时使用此技巧

在优化 GSAP 动画以实现流畅的 60fps、减少布局/绘制成本，或当用户询问性能、卡顿或快速动画的最佳实践时使用。

**相关技巧：** 使用 **gsap-core**（变换、autoAlpha）和 **gsap-timeline** 创建动画；关于 ScrollTrigger 性能请参考 **gsap-scrolltrigger**。

## 优先使用变换和透明度

对 **变换**（`x`、`y`、`scaleX`、`scaleY`、`rotation`、`rotationX`、`rotationY`、`skewX`、`skewY`）和 **透明度** 进行动画处理，可以将工作交给合成器，避免布局和大多数绘制。当变换可以实现相同效果时，避免对布局密集型属性进行动画处理。

- ✅ 优先：**x**、**y**、**scale**、**rotation**、**opacity**。
- ❌ 尽量避免：**width**、**height**、**top**、**left**、**margin**、**padding**（它们会触发布局并可能导致卡顿）。

GSAP 的 **x** 和 **y** 默认使用变换（translate）；使用它们代替 **left**/**top** 进行移动。

## will-change

在将要进行动画的元素上使用 CSS 的 **will-change**，它提示浏览器提升该层。

```css
will-change: transform;
```

## 批量读写

GSAP 内部会批量处理更新。当将 GSAP 与直接的 DOM 读写或依赖布局的代码混合使用时，避免以导致重复布局抖动的方式交错读写。优先先完成所有读取，再完成所有写入（或让 GSAP 一次性处理写入）。

## 多个元素（错开、列表）

- 当动画相同时，使用 **stagger** 而不是多个带有手动延迟的单独缓动，它更高效。
- 对于长列表，考虑使用 **虚拟化** 或仅对可见项进行动画；避免创建数百个同时进行的缓动，如果这会导致卡顿。
- 尽可能重用时间轴；避免每帧创建新的时间轴。

## 经常更新的属性（例如鼠标跟随器）

对于经常更新的属性（例如鼠标跟随器的 x/y），优先使用 **gsap.quickTo()**。它重用单个缓动，而不是每次更新时创建新的缓动。

```javascript
let xTo = gsap.quickTo("#id", "x", { duration: 0.4, ease: "power3" }),
    yTo = gsap.quickTo("#id", "y", { duration: 0.4, ease: "power3" });

document.querySelector("#container").addEventListener("mousemove", (e) => {
  xTo(e.pageX);
  yTo(e.pageY);
});
```

## ScrollTrigger 和性能

- **pin: true** 会提升固定元素；仅固定所需的元素。
- 使用较小的值（例如 `scrub: 1`）进行 **scrub** 可以在滚动时减少工作量；在低端设备上测试。
- 仅在布局实际发生变化时（例如内容加载后）调用 **ScrollTrigger.refresh()**，而不是每次调整大小；可能时使用防抖。

## 减少同时工作

- 当元素不可见时（例如用户导航离开），暂停或销毁屏幕外或非活动的动画。
- 避免对许多元素同时动画化大量属性；如有必要，简化或分步处理。

## 最佳实践

- ✅ 动画化 **transform** 和 **opacity**；仅在将要动画化的元素上使用 CSS 的 **will-change**。
- ✅ 当动画相同时，使用 **stagger** 而不是多个带有手动延迟的单独缓动。
- ✅ 使用 **gsap.quickTo()** 对于经常更新的属性（例如鼠标跟随器）。
- ✅ 清理或销毁屏幕外动画；布局变化时调用 **ScrollTrigger.refresh()**，可能时使用防抖。

## 不要

- ❌ 当 **x**/**y**/**scale** 可以实现相同效果时，不要对 **width**/ **height**/ **top**/ **left** 进行移动动画。
- ❌ 每个元素都设置 **will-change** 或 **force3D** “以防万一”；仅用于实际进行动画的元素。
- ❌ 在未在低端设备上测试的情况下创建数百个重叠的缓动或 ScrollTriggers。
- ❌ 忽略清理；未清理的缓动和 ScrollTriggers 会继续运行，并可能影响性能和正确性。
