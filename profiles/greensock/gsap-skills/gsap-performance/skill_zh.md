# GSAP 性能

## 何时使用此技能

当需要对 GSAP 动画进行优化，以实现流畅的 60fps、降低布局/绘制成本，或用户询问有关性能、卡顿或快速动画最佳实践时，使用此技能。

**相关技能：** 使用 **gsap-core**（变换、autoAlpha）和 **gsap-timeline** 构建动画；关于 ScrollTrigger 性能，请参阅 **gsap-scrolltrigger**。

## 优先使用 Transform 和 Opacity

对 **transform**（`x`、`y`、`scaleX`、`scaleY`、`rotation`、`rotationX`、`rotationY`、`skewX`、`skewY`）和 **opacity** 进行动画，可以将工作保持在合成器上，并避免布局和大部分绘制操作。当 transform 可以实现相同效果时，应避免动画化布局密集型属性。

- ✅ 优先使用：**x**、**y**、**scale**、**rotation**、**opacity**。
- ❌ 如有可能，应避免：**width**、**height**、**top**、**left**、**margin**、**padding**（它们会触发布局，并可能导致卡顿）。

GSAP 的 **x** 和 **y** 默认使用 transform（平移）；用于移动时应使用它们，而不是 **left**/**top**。

## will-change

在将动画化的元素上使用 CSS 中的 **will-change**。它提示浏览器将图层提升。

```css
will-change: transform;
```

## 批量读取和写入

GSAP 内部会批量更新。当将 GSAP 与直接对 DOM 进行读取/写入或布局相关代码混合使用时，应避免以可能导致重复布局抖动的方式进行读取和写入的交替。优先先完成所有读取，再进行所有写入（或让 GSAP 一次性处理写入）。

## 多个元素（Stagger、列表）

- 当动画相同时，使用 **stagger** 而非多个带有手动延迟的独立补间动画，效率更高。
- 对于长列表，考虑使用**虚拟化**或仅动画化可见项；如果会导致卡顿，应避免创建数百个同时进行的补间动画。
- 尽可能复用时间轴；避免每帧都创建新的时间轴。

## 频繁更新的属性（例如鼠标跟随器）

对于频繁更新的属性（例如鼠标跟随器的 x/y），优先使用 **gsap.quickTo()**。它在每次更新时复用单个补间，而不是为每次更新创建新的补间。

```javascript
let xTo = gsap.quickTo("#id", "x", { duration: 0.4, ease: "power3" }),
    yTo = gsap.quickTo("#id", "y", { duration: 0.4, ease: "power3" });

document.querySelector("#container").addEventListener("mousemove", (e) => {
  xTo(e.pageX);
  yTo(e.pageY);
});
```

## ScrollTrigger 与性能

- **pin: true** 会提升被固定的元素；仅固定所需内容。
- 使用较小值（如 `scrub: 1`）进行 **scrub** 可以减少滚动时的计算量；在低端设备上测试。
- 仅在布局实际发生变化时（例如内容加载后）调用 **ScrollTrigger.refresh()**，不要在每个缩放（resize）事件中都调用；尽量进行防抖处理。

## 减少同时工作

- 当动画不可见时，暂停或停止屏幕外或未活跃的动画（例如当用户离开页面时）。
- 避免同时为许多元素动画化大量属性；如有需要，应进行简化或排序。

## 最佳实践

- ✅ 动画化 **transform** 和 **opacity**；仅在正在动画化的元素上使用 CSS 中的 **will-change**。
- ✅ 当动画相同时，使用 **stagger** 而非多个带有手动延迟的独立补间动画。
- ✅ 对于频繁更新的属性（例如鼠标跟随器），使用 **gsap.quickTo()**。
- ✅ 清理或停止屏幕外动画；当布局发生变化时调用 **ScrollTrigger.refresh()**，尽量进行防抖处理。

## 切勿

- ❌ 当 **x**/**y**/**scale** 可以实现相同效果时，切勿为了移动动画而使用 **width**/**height**/**top**/**left**。
- ❌ 不要对每个元素都设置 **will-change** 或 **force3D**“以防万一”；请为确实在动画化的元素使用。
- ❌ 在没有在低端设备测试的情况下，创建数百个重叠的补间动画或 ScrollTrigger。
- ❌ 忽视清理；游离的补间动画和 ScrollTrigger 会持续运行，并可能影响性能和正确性。
