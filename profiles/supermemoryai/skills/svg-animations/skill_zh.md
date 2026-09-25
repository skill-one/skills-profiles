这项技能指导创建手工制作的 SVG 动画——从简单的动画图标到复杂的多阶段路径动画。SVG 是一种用于图像的标记语言；每个元素都是一个可以样式化、动画化和脚本的 DOM 节点。

## SVG 基础知识

### 坐标系
SVG 使用由 `viewBox="minX minY width height"` 定义的坐标系。viewBox 是你的画布——所有坐标都相对于它，这使得 SVG 具有分辨率独立性。

```svg
<svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
  <!-- 200x200 单位画布，可缩放到任何大小 -->
</svg>
```

### 形状原语

```svg
<rect x="10" y="10" width="80" height="40" rx="4" fill="#1a1a1a" />
<circle cx="50" cy="50" r="30" fill="#e63946" />
<ellipse cx="50" cy="50" rx="40" ry="20" fill="#457b9d" />
<line x1="10" y1="10" x2="90" y2="90" stroke="#2a9d8f" stroke-width="2" />
<polygon points="50,5 95,90 5,90" fill="#e9c46a" />
<polyline points="10,80 40,20 70,60 100,10" fill="none" stroke="#264653" stroke-width="2" />
```

### `<path>` 元素——强大的工具

`d` 属性使用命令定义路径。大写 = 绝对，小写 = 相对。

| 命令 | 目的 | 语法 |
|-------|-------|-------|
| M/m | 移动到 | `M x y` |
| L/l | 直线到 | `L x y` |
| H/h | 水平线 | `H x` |
| V/v | 垂直线 | `V y` |
| C/c | 三次贝塞尔曲线 | `C x1 y1, x2 y2, x y` |
| S/s | 平滑三次贝塞尔曲线 | `S x2 y2, x y` |
| Q/q | 二次贝塞尔曲线 | `Q x1 y1, x y` |
| T/t | 平滑二次 | `T x y` |
| A/a | 椭圆弧 | `A rx ry rotation large-arc sweep x y` |
| Z/z | 关闭路径 | `Z` |

**三次贝塞尔曲线** (`C`): 两个控制点定义曲线。第一个控制点设置离开角度，第二个设置到达角度。

```svg
<path d="M 10 80 C 40 10, 65 10, 95 80" stroke="#000" fill="none" stroke-width="2" />
```

**平滑三次** (`S`): 自动反射前一个控制点——非常适合串联流畅的 S 曲线。

```svg
<path d="M 10 80 C 40 10, 65 10, 95 80 S 150 150, 180 80" stroke="#000" fill="none" />
```

**弧** (`A`): `rx ry x-rotation large-arc-flag sweep-flag x y`
- `large-arc-flag`: 0 = 小弧，1 = 大弧 (>180°)
- `sweep-flag`: 0 = 逆时针，1 = 顺时针

```svg
<!-- 使用弧和二次曲线绘制的爱心形状 -->
<path d="M 10,30 A 20,20 0,0,1 50,30 A 20,20 0,0,1 90,30 Q 90,60 50,90 Q 10,60 10,30 Z"
      fill="#e63946" />
```

### 分组和变换

```svg
<g transform="translate(50, 50) rotate(45)" opacity="0.8">
  <rect x="-20" y="-20" width="40" height="40" fill="#264653" />
</g>
```

使用 `<g>` 将元素分组以进行集体变换、样式化和动画目标。

### 渐变、遮罩和滤镜

```svg
<defs>
  <!-- 线性渐变 -->
  <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
    <stop offset="0%" stop-color="#e63946" />
    <stop offset="100%" stop-color="#457b9d" />
  </linearGradient>

  <!-- 径向渐变 -->
  <radialGradient id="glow" cx="50%" cy="50%" r="50%">
    <stop offset="0%" stop-color="#fff" stop-opacity="0.8" />
    <stop offset="100%" stop-color="#fff" stop-opacity="0" />
  </radialGradient>

  <!-- 遮罩 -->
  <mask id="reveal">
    <rect width="100%" height="100%" fill="black" />
    <circle cx="100" cy="100" r="50" fill="white" />
  </mask>

  <!-- 模糊滤镜 -->
  <filter id="blur">
    <feGaussianBlur in="SourceGraphic" stdDeviation="3" />
  </filter>
</defs>

<rect width="200" height="200" fill="url(#grad)" />
<rect width="200" height="200" fill="url(#grad)" mask="url(#reveal)" />
<circle cx="50" cy="50" r="20" filter="url(#blur)" fill="#e63946" />
```

---

## CSS 动画在 SVG 上

许多 SVG 属性是有效的 CSS 属性：`fill`，`stroke`，`opacity`，`transform`，`stroke-dasharray`，`stroke-dashoffset` 等。

### 基本 CSS 动画

```css
.pulse {
  animation: pulse 2s ease-in-out infinite;
  transform-origin: center;
}
@keyframes pulse {
  0%, 100% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.15); opacity: 0.7; }
}
```

### 线条绘制动画（经典）

最经典的 SVG 动画。使用 `stroke-dasharray` 和 `stroke-dashoffset` 使路径看起来像是在自己绘制。

**工作原理：**
1. 设置 `stroke-dasharray` 为路径的总长度（一个巨大的短划线 + 一个巨大的间隙）
2. 设置 `stroke-dashoffset` 为相同的长度（将短划线移出屏幕）
3. 动画 `stroke-dashoffset` 到 0（将短划线滑入视图）

```svg
<svg viewBox="0 0 200 200">
  <path class="draw" d="M 20 100 C 20 50, 80 50, 80 100 S 140 150, 140 100"
        fill="none" stroke="#1a1a1a" stroke-width="3" />
</svg>

<style>
  .draw {
    stroke-dasharray: 300;
    stroke-dashoffset: 300;
    animation: draw 2s ease forwards;
  }
  @keyframes draw {
    to { stroke-dashoffset: 0; }
  }
</style>
```

**在 JS 中获取精确路径长度：**
```js
const path = document.querySelector('.draw');
const length = path.getTotalLength();
path.style.strokeDasharray = length;
path.style.strokeDashoffset = length;
```

### 交错多路径绘制

```css
.line-1 { animation-delay: 0s; }
.line-2 { animation-delay: 0.3s; }
.line-3 { animation-delay: 0.6s; }
```

### CSS `d` 属性动画

现代浏览器支持直接在 CSS 中动画 `d` 属性：

```css
path {
  d: path("M 10,30 A 20,20 0,0,1 50,30 A 20,20 0,0,1 90,30 Q 90,60 50,90 Q 10,60 10,30 z");
  transition: d 0.5s ease;
}
path:hover {
  d: path("M 10,50 A 20,20 0,0,1 50,10 A 20,20 0,0,1 90,50 Q 90,80 50,100 Q 10,80 10,50 z");
}
```

**要求：** 两个路径必须具有相同数量和类型的命令才能进行插值。

---

## SMIL 动画（原生 SVG）

SMIL 动画直接在 SVG 标记中声明。即使 SVG 作为 `<img>` 或 CSS `background-image` 加载时也能工作——在这种情况下，CSS 和 JS 无法访问。

### `<animate>` — 动画任何属性

```svg
<circle cx="50" cy="50" r="20" fill="#e63946">
  <animate attributeName="r" from="20" to="40" dur="1s"
           repeatCount="indefinite" />
</circle>
```

带关键帧：
```svg
<animate attributeName="cx"
         values="50; 150; 100; 50"
         keyTimes="0; 0.33; 0.66; 1"
         dur="3s" repeatCount="indefinite" />
```

### `<animateTransform>` — 变换动画

```svg
<rect x="-20" y="-20" width="40" height="40" fill="#264653">
  <animateTransform attributeName="transform" type="rotate"
                    from="0" to="360" dur="4s" repeatCount="indefinite" />
</rect>
```

类型：`translate`，`scale`，`rotate`，`skewX`，`skewY`

### `<animateMotion>` —沿路径移动

```svg
<circle r="5" fill="#e63946">
  <animateMotion dur="3s" repeatCount="indefinite" rotate="auto">
    <mpath href="#motionPath" />
  </animateMotion>
</circle>
<path id="motionPath" d="M 20,50 C 20,0 80,0 80,50 S 140,100 140,50"
      fill="none" stroke="#ccc" />
```

`rotate="auto"` 使元素沿着路径切线方向旋转。`rotate="auto-reverse"` 将其翻转 180°。

### `<set>` — 离散值变化

```svg
<rect width="40" height="40" fill="#264653">
  <set attributeName="fill" to="#e63946" begin="1s" />
</rect>
```

### 时间和同步

```svg
<!-- 通过引用 ID 链接动画 -->
<animate id="first" attributeName="cx" to="150" dur="1s" fill="freeze" />
<animate attributeName="cy" to="150" dur="1s" begin="first.end" fill="freeze" />
<animate attributeName="r" to="30" dur="0.5s" begin="first.end + 0.5s" fill="freeze" />
```

触发值：
- `begin="click"` — 点击时
- `begin="2s"` — 2 秒后
- `begin="other.end"` — 当另一个动画结束时
- `begin="other.end + 1s"` — 另一个结束 1 秒后
- `begin="other.repeat(2)"` — 另一个的第 2 次重复时

### 使用 `calcMode` 和 `keySplines` 进行缓动

```svg
<animate attributeName="cx" values="50;150" dur="1s"
         calcMode="spline" keySplines="0.42 0 0.58 1" />
```

`calcMode` 选项：`linear`（默认），`discrete`，`paced`，`spline`

`keySplines` 接受三次贝塞尔控制点（x1 y1 x2 y2）每个间隔。常见的缓动：
- Ease-in-out: `0.42 0 0.58 1`
- Ease-out: `0 0 0.58 1`
- Bounce-ish: `0.34 1.56 0.64 1`

### 形状变形的 SMIL

两个形状必须具有相同的命令结构（相同数量的点，相同的命令类型）：

```svg
<path fill="#e63946">
  <animate attributeName="d" dur="2s" repeatCount="indefinite"
    values="M 50,10 L 90,90 L 10,90 Z;
            M 50,90 L 90,10 L 10,10 Z;
            M 50,10 L 90,90 L 10,90 Z" />
</path>
```

---

## 动画模式和配方

### 加载旋转器

```svg
<svg viewBox="0 0 50 50">
  <circle cx="25" cy="25" r="20" fill="none" stroke="#1a1a1a"
          stroke-width="3" stroke-linecap="round"
          stroke-dasharray="90 150" stroke-dashoffset="0">
    <animateTransform attributeName="transform" type="rotate"
                      from="0 25 25" to="360 25 25" dur="1s"
                      repeatCount="indefinite" />
    <animate attributeName="stroke-dashoffset" values="0;-280"
             dur="1.5s" repeatCount="indefinite" />
  </circle>
</svg>
```

### 动画勾选标记

```svg
<svg viewBox="0 0 52 52">
  <circle cx="26" cy="26" r="24" fill="none" stroke="#4caf50"
          stroke-width="2" class="draw"
          style="stroke-dasharray:150;stroke-dashoffset:150;
                 animation:draw .6s ease forwards" />
  <path fill="none" stroke="#4caf50" stroke-width="3"
        stroke-linecap="round" stroke-linejoin="round"
        d="M14 27l7 7 16-16" class="draw"
        style="stroke-dasharray:50;stroke-dashoffset:50;
               animation:draw .4s ease .5s forwards" />
</svg>
```

### 变形汉堡到 X

```svg
<svg viewBox="0 0 24 24" id="menu">
  <path id="top" d="M 3,6 L 21,6" stroke="#1a1a1a" stroke-width="2" stroke-linecap="round">
    <animate attributeName="d" to="M 5,5 L 19,19" dur="0.3s" begin="menu.click" fill="freeze" />
  </path>
  <path id="mid" d="M 3,12 L 21,12" stroke="#1a1a1a" stroke-width="2" stroke-linecap="round">
    <animate attributeName="opacity" to="0" dur="0.1s" begin="menu.click" fill="freeze" />
  </path>
  <path id="bot" d="M 3,18 L 21,18" stroke="#1a1a1a" stroke-width="2" stroke-linecap="round">
    <animate attributeName="d" to="M 5,19 L 19,5" dur="0.3s" begin="menu.click" fill="freeze" />
  </path>
</svg>
```

### 渐变动画（颜色转换）

```svg
<defs>
  <linearGradient id="shift" x1="0%" y1="0%" x2="100%" y2="0%">
    <stop offset="0%">
      <animate attributeName="stop-color"
               values="#e63946;#457b9d;#2a9d8f;#e63946"
               dur="4s" repeatCount="indefinite" />
    </stop>
    <stop offset="100%">
      <animate attributeName="stop-color"
               values="#457b9d;#2a9d8f;#e63946;#457b9d"
               dur="4s" repeatCount="indefinite" />
    </stop>
  </linearGradient>
</defs>
<rect width="200" height="100" fill="url(#shift)" rx="8" />
```

### 呼吸/脉冲发光

```svg
<circle cx="100" cy="100" r="30" fill="#e63946">
  <animate attributeName="r" values="30;35;30" dur="2s"
           calcMode="spline" keySplines="0.4 0 0.6 1;0.4 0 0.6 1"
           repeatCount="indefinite" />
  <animate attributeName="opacity" values="1;0.6;1" dur="2s"
           calcMode="spline" keySplines="0.4 0 0.6 1;0.4 0 0.6 1"
           repeatCount="indefinite" />
</circle>
```

### 波浪/液体效果

```svg
<path fill="#457b9d" opacity="0.7">
  <animate attributeName="d" dur="5s" repeatCount="indefinite"
    values="M 0,40 C 30,35 70,45 100,40 L 100,100 L 0,100 Z;
            M 0,40 C 30,50 70,30 100,40 L 100,100 L 0,100 Z;
            M 0,40 C 30,35 70,45 100,40 L 100,100 L 0,100 Z"
    calcMode="spline" keySplines="0.4 0 0.6 1;0.4 0 0.6 1" />
</path>
```

---

## 最佳实践

1. **使用 `viewBox`，不要在 SVG 中硬编码 `width`/`height`** — 让容器来调整大小。这保持了它的分辨率独立性。

2. **`<defs>` 用于可重用定义** — 渐变、滤镜、遮罩、clipPaths 和可重用形状应放在 `<defs>` 中。

3. **对于自包含的 SVG**（图标、标志通过 `<img>` 加载）优先使用 SMIL——CSS/JS 无法访问那里。当 SVG 被内联且您希望与页面其余部分协调时，使用 CSS 动画。

4. **形状变形需要匹配命令** — 相同数量的路径命令，相同的类型，相同的顺序。如果形状不同，则添加不可见的中间点来均衡。

5. **`stroke-linecap="round"`** 使线条动画看起来更精致。

6. **`fill="freeze"`** 在 SMIL 中保持最终动画状态。如果没有它，元素会弹回。

7. **CSS 中的 `transform-origin: center`** — SVG 变换默认为原点（0,0），而不是元素中心。始终明确设置此值。

8. **在 JS 中使用 `getTotalLength()`** 获取精确路径长度，用于线条动画，而不是猜测。

9. **使用 `<g>` 组分层动画** — 将组变换单独于元素属性动画，以进行复杂的编排。

10. **性能：** 当动画 `transform` 和 `opacity` 时，SVG 动画会 GPU 组合。动画 `d`、`points` 或布局属性会在复杂 SVG 上触发重绘——谨慎使用。

11. **`will-change: transform`** 在动画 SVG 元素上帮助浏览器优化组合。

12. **可访问性：** 添加 `role="img"` 和 `<title>` / `<desc>` 元素。使用 `prefers-reduced-motion` 媒体查询来禁用用户请求的动画：

```css
@media (prefers-reduced-motion: reduce) {
  svg * {
    animation: none !important;
    transition: none !important;
  }
}
```
