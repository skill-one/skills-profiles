`Graphics` 是 PixiJS v8 场景图的矢量绘图分支。v8 API 遵循形状优先于样式的模式：使用 `rect`、`circle`、`moveTo` 等绘制形状或路径，然后应用 `fill` 和/或 `stroke`。每个方法都返回 `this` 以便链式调用，绘图指令存储在 `GraphicsContext` 上，该指令可以在实例之间共享。

假设熟悉 `pixijs-scene-core-concepts`。`Graphics` 是一个叶节点：不要在其内部嵌套子节点。将多个 `Graphics` 对象包装在 `Container` 中以将它们分组。

## 快速入门

```ts
const g = new Graphics();

g.rect(10, 10, 200, 100)
  .fill({ color: 0x3498db, alpha: 0.8 })
  .stroke({ width: 3, color: 0x2c3e50 });

g.circle(300, 60, 40).fill(0xe74c3c);

g.moveTo(50, 200)
  .lineTo(200, 200)
  .bezierCurveTo(250, 250, 100, 300, 50, 250)
  .closePath()
  .fill(0x6c5ce7);

app.stage.addChild(g);
```

**相关技能：** `pixijs-scene-core-concepts`（场景图基础）、`pixijs-scene-container`（与其他对象组合图形）、`pixijs-scene-core-concepts/references/masking.md`（图形作为遮罩）、`pixijs-filters`（效果）、`pixijs-performance`（批处理、`cacheAsTexture`）。

## 构造选项

所有 `Container` 选项（`position`、`scale`、`tint`、`label`、`filters`、`zIndex` 等）在此处也有效——请参阅 `skills/pixijs-scene-core-concepts/references/constructor-options.md`。

由 `GraphicsOptions` 添加的特定于叶节点的选项：

| 选项        | 类型              | 默认                 | 描述                                                                                                                                                                                          |
| ------------- | ----------------- | ----------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `context`     | `GraphicsContext` | new `GraphicsContext()` | 共享绘图上下文。传递上下文可跨多个 `Graphics` 节点重用其 tessellated 几何形状，避免重复 GPU 工作。如果省略，每个 `Graphics` 都会创建并拥有一个新的上下文。 |
| `roundPixels` | `boolean`         | `false`                 | 将屏幕上的 `x`/`y` 四舍五入到最近的像素。为像素艺术风格生成更清晰的线条，但代价是平滑的亚像素移动。                                                       |

构造函数也接受一个 `GraphicsContext` 实例作为其唯一参数（`new Graphics(ctx)`），这相当于 `new Graphics({ context: ctx })`。

## 核心模式

### 形状优先于填充的工作流程

```ts
const g = new Graphics();

g.rect(10, 10, 200, 100)
  .fill({ color: 0x3498db, alpha: 0.8 })
  .stroke({ width: 3, color: 0x2c3e50 });

g.circle(150, 200, 40).fill(0xe74c3c);
g.roundRect(300, 10, 150, 80, 12).fill(0x2ecc71);
g.poly([0, 0, 60, 0, 30, 50], true).fill(0x9b59b6);
g.star(400, 200, 5, 40, 20, 0).fill(0xf39c12);
g.ellipse(100, 350, 60, 30).fill(0x1abc9c);
```

`fill()` 接受一个 `FillInput`：颜色数字/字符串、`{ color, alpha, texture, matrix, textureSpace }`、`FillGradient`、`FillPattern` 或 `Texture`。当使用纹理填充时，`textureSpace` 控制坐标映射：

- `'local'`（默认）：纹理缩放以适应每个形状的边界框（归一化 0-1 坐标）。
- `'global'`：纹理位置/缩放相对于 Graphics 对象的坐标系，所有形状共享。
- 图集子纹理：`'global'` 尊重帧原点和旋转，因此绘制的形状与该帧的 `Sprite` 匹配。`'local'` 映射整个源图像；传递一个 `matrix` 针对源图像的帧区域，或先使用 `renderer.generateTexture()` 处理帧。

`FillInput` 还支持嵌套的 `fill` 子字段：`FillStyle` 选项对象可以在其 `fill` 键下嵌入 `FillGradient` 或 `FillPattern`，该渐变或图案与外对象的 `color`、`alpha`、`texture` 和 `matrix` 修饰符一起应用。

`stroke()` 接受颜色、`FillGradient`、`FillPattern` 或一个组合所有 `FillStyle` 键（`color`、`alpha`、`texture`、`matrix`、`fill`、`textureSpace`）的 `StrokeStyle` 对象：

| 属性    | 默认   | 备注                                                                   |
| ------------ | --------- | ----------------------------------------------------------------------- |
| `width`      | `1`       | 线条的像素宽度。                                              |
| `cap`        | `'butt'`  | `'butt'`、`'round'`、`'square'` 之一。开放路径的端点样式。       |
| `join`       | `'miter'` | `'miter'`、`'round'`、`'bevel'` 之一。拐角样式。                   |
| `miterLimit` | `10`      | 限制 miter 拐角延伸的距离，超出部分将回退到 bevel。           |
| `alignment`  | `0.5`     | `1` = 形状内部，`0.5` = 居中，`0` = 外部。                |
| `pixelLine`  | `false`   | 将 1 像素线条对齐到像素网格，以获得清晰的输出。仅限 Graphics。 |

线条可以使用与填充相同的渐变和图案，通过 `fill: gradient` 或 `texture: tex`：

```ts
const grad = new FillGradient({
  end: { x: 1, y: 0 },
  colorStops: [
    { offset: 0, color: 0xff0000 },
    { offset: 1, color: 0x0000ff },
  ],
});
g.rect(0, 0, 200, 100).stroke({
  width: 8,
  fill: grad,
  join: "round",
  cap: "round",
});
```

`fill()` 和 `stroke()` 都可以在同一个形状之后调用；立即在 `fill()` 之后调用 `stroke()` 将重用相同的路径。

### 高级形状原语

```ts
g.regularPoly(100, 100, 50, 6, 0).fill(0x3498db);
g.roundPoly(250, 100, 50, 5, 10).fill(0xe74c3c);
g.chamferRect(350, 50, 100, 80, 15).fill(0x2ecc71);
g.filletRect(500, 50, 100, 80, 15).fill(0x9b59b6);
g.roundShape(
  [
    { x: 50, y: 250, radius: 20 },
    { x: 150, y: 250, radius: 5 },
    { x: 150, y: 350, radius: 10 },
    { x: 50, y: 350, radius: 15 },
  ],
  10,
).fill(0xf39c12);
```

### 使用 `cut()` 创建孔洞

```ts
g.rect(0, 0, 200, 200).fill(0x00ff00).circle(100, 100, 50).cut();
```

`cut()` 从先前绘制的填充或线条中减去当前活动路径。规则：

- 孔洞必须完全位于目标形状内部。重叠边缘或位于形状外部的孔洞将无法正确渲染，因为渲染器将孔洞作为内部边界进行三角剖分。
- `cut()` 查看最多到最后两个指令。当你对相同的路径进行 `fill()` 和 `stroke()` 时，单个 `cut()` 首先将孔洞添加到线条；第二个 `cut()` 将其添加到下方的填充。
- 调用 `cut()` 后，活动路径会重置，因此你可以使用 `moveTo`、`rect` 等开始下一个形状。
- `cut()` 也适用于线条——`g.rect(...).stroke(...).circle(...).cut()` 在线条轮廓中切割孔洞。

通过在调用 `cut()` 之前在活动路径中绘制多个形状来使用单个 `cut()` 绘制多个孔洞。每个形状都累积到相同的孔洞路径中：

```ts
const g = new Graphics();

g.rect(350, 350, 150, 150).fill(0x00ff00);

// 将三个圆绘制到活动路径中，然后一次性调用 cut() 切割它们
g.circle(375, 375, 25);
g.circle(425, 425, 25);
g.circle(475, 475, 25);
g.cut();
```

如果你需要在**不同**的填充形状上创建孔洞，请为每个形状提供自己的 `fill()` 和匹配的 `cut()`：

```ts
g.rect(0, 0, 100, 100).fill(0x3498db);
g.circle(50, 50, 20).cut(); // 矩形的孔洞

g.rect(120, 0, 100, 100).fill(0xe74c3c);
g.circle(170, 50, 20).cut(); // 第二个矩形的孔洞
```

在已存在孔洞的形状上调用 `cut()` **会添加**到现有的孔洞路径，而不是替换它。使用此方法将孔洞叠加。

### 路径和复杂形状

```ts
g.moveTo(50, 50)
  .lineTo(200, 50)
  .bezierCurveTo(250, 100, 250, 150, 200, 200)
  .quadraticCurveTo(100, 250, 50, 200)
  .closePath()
  .fill({ color: 0x6c5ce7, alpha: 0.7 })
  .stroke({ width: 2, color: 0xdfe6e9 });
```

路径方法：`moveTo`、`lineTo`、`bezierCurveTo`、`quadraticCurveTo`、`arc`、`arcTo`、`arcToSvg`、`closePath`。调用 `beginPath()` 以丢弃当前活动路径并开始新路径。

```ts
// arc(cx, cy, radius, startAngle, endAngle, counterclockwise?)
g.moveTo(80, 50)
  .arc(50, 50, 30, 0, Math.PI)
  .stroke({ width: 4, color: 0x2c3e50 });

// arcTo(x1, y1, x2, y2, radius) — 在两个线段之间绘制圆角
g.moveTo(150, 20)
  .arcTo(200, 20, 200, 80, 20)
  .lineTo(200, 80)
  .stroke({ width: 2 });

// arcToSvg(rx, ry, xAxisRotation, largeArcFlag, sweepFlag, x, y) — 与 SVG 的 `A` 命令匹配
g.moveTo(250, 50).arcToSvg(40, 20, 0, 1, 0, 330, 50).stroke({ width: 2 });
```

### 渐变和图案

```ts
// 线性渐变
const linear = new FillGradient({
  end: { x: 1, y: 0 },
  colorStops: [
    { offset: 0, color: 0xff0000 },
    { offset: 1, color: 0x0000ff },
  ],
});
g.rect(0, 0, 200, 100).fill(linear);

// 径向渐变。坐标在默认的 "local" 空间中归一化 0-1：
// 内圆位于中心，外圆延伸到边缘。
const radial = new FillGradient({
  type: "radial",
  center: { x: 0.5, y: 0.5 },
  innerRadius: 0,
  outerCenter: { x: 0.5, y: 0.5 },
  outerRadius: 0.5,
  colorStops: [
    { offset: 0, color: 0xffffff },
    { offset: 1, color: 0x000000 },
  ],
});
g.circle(100, 100, 100).fill(radial);

// 像素坐标需要 textureSpace: "global"; 渐变然后跨形状扩展。
const shared = new FillGradient({
  type: "radial",
  center: { x: 100, y: 100 },
  outerRadius: 100,
  textureSpace: "global",
  colorStops: [
    { offset: 0, color: 0xffffff },
    { offset: 1, color: 0x000000 },
  ],
});
g.rect(0, 0, 200, 200).fill(shared);

const brick = await Assets.load("brick.png");

// 选项对象形式（首选）
const pattern = new FillPattern({
  texture: brick,
  repetition: "repeat", // 'repeat' | 'repeat-x' | 'repeat-y' | 'no-repeat'
  textureSpace: "global", // 'global' (默认) | 'local'
});

// 遗留的位置形式仍然受支持
const pattern2 = new FillPattern(brick, "repeat");

g.rect(0, 120, 200, 100).fill(pattern);
```

`FillGradient` 的默认 `type` 是 `'linear'`，从 `start {0,0}` 到 `end {0,1}`（垂直）。设置 `type: 'radial'` 并使用 `center`/`innerRadius` 和 `outerCenter`/`outerRadius` 创建径向渐变；`rotation`（弧度，默认 `0`）和 `scale`（默认 `1`）使其呈椭圆形，仅适用于 Graphics。`textureSpace` 默认为 `'local'`（归一化 0-1 形状坐标）；使用 `'global'` 以像素坐标跨形状共享。

`FillPattern` 接受一个选项对象（`{ texture, repetition?, textureSpace? }`）或遗留的位置形式（`new FillPattern(texture, repetition?)`）。`repetition` 选择平铺模式。`textureSpace` 控制瓷砖如何映射到形状：

- `'global'`（默认）：瓷砖在 `Graphics` 坐标系中连续平铺，因此相邻形状共享一个平铺网格。适用于背景和无缝纹理。
- `'local'`：单个瓷砖适合每个形状的边界。结合 `setTransform` 将形状细分为瓷砖网格。

注意 `FillPattern` 默认 `textureSpace` 为 `'global'`，而纹理填充的 `'local'` 默认如上所示。

直接在 `FillPattern` 上设置 `textureSpace` 和变换；当模式作为样式对象传递（`fill({ fill: pattern, textureSpace: "local" })`）时，模式自己的值将替换样式的 `textureSpace` 和 `matrix`。

### 直接绘制纹理

```ts
const tex = await Assets.load("icon.png");

// 在 (x, y) 处绘制整个纹理，并可选地应用色调
g.texture(tex, 0xffffff, 20, 20);

// 绘制子区域 (dx, dy, dw, dh)
g.texture(tex, 0xff0000, 100, 20, 64, 64);
```

`Graphics.texture(texture, tint?, dx?, dy?, dw?, dh?)` 是绘制单个带纹理矩形（无需通过 `fill()`）的快捷方式。适用于不需要完整精灵生命周期中的图标。

### GraphicsContext 共享

```ts
const ctx = new GraphicsContext().rect(0, 0, 50, 50).fill(0xff0000);

const g1 = new Graphics(ctx);
const g2 = new Graphics(ctx);
g2.x = 100;
```

上下文共享避免了重复 GPU 几何形状；昂贵的 tessellation 只运行一次。你也可以在构造后分配上下文：`g.context = existingContext`。

### SVG 导入和导出

使用 `svg()` 将 SVG 标记解析到活动上下文中：

```ts
g.svg(`<svg viewBox="0 0 100 100">
    <circle cx="50" cy="50" r="40" fill="red"/>
</svg>`);
```

`svg()` 解析 `<path>`（`fill-rule="evenodd"` 孔洞）、`<rect>`、`<circle>`、`<ellipse>`、`<line>`、`<polygon>`、`<polyline>` 和 `<g>` 分组。样式来自 `fill`、`stroke`、`stroke-width`、`fill-opacity`、`stroke-opacity` 和 `opacity`，作为属性或内联 `style`。`<linearGradient>` 和 `<radialGradient>` 定义在 `<defs>` 中的渐变成为通过 `url(#id)` 应用的 `FillGradient`；`gradientUnits` 映射到 `textureSpace`，百分比坐标被接受。不支持：`transform` 属性、`<style>` 块、`stroke-linecap`/`stroke-linejoin`/`stroke-dasharray`、`gradientTransform`、`spreadMethod`、`stop-opacity`、`<text>`、`<image>`、`<use>`、`<clipPath>`、`<mask>`、`<pattern>`。不支持的元素记录警告并跳过。复杂的孔洞几何形状可能因 Pixi 的三角剖分针对性能优化而渲染不准确。

使用 `graphicsContextToSvg` 将 `Graphics` 或 `GraphicsContext` 序列化为自包含的 SVG 文档字符串：

```ts
import { Graphics, graphicsContextToSvg } from "pixi.js";

const g = new Graphics()
  .rect(0, 0, 100, 50)
  .fill({ color: 0xff0000 })
  .circle(150, 25, 25)
  .stroke({ color: 0x0000ff, width: 4 });

const svgString = graphicsContextToSvg(g, 2);
```

`graphicsContextToSvg(source, precision = 2)` 是一个纯函数，它读取上下文的指令并返回一个完整的 `<svg>` 字符串，带有自动计算的 `viewBox`。传递 `Graphics` 或 `GraphicsContext`；`precision` 控制输出的坐标小数位数。导出所有形状-然后-填充原语（如 `regularPoly`/`filletRect` 回退到形状路径），所有路径方法，线条属性（`width`、`cap`、`join`、`miterLimit`）、`fill-opacity`/`stroke-opacity` 和通过 `<defs>` 块导出的 `FillGradient`（线性 和 径向）。孔洞合并为一个 `<path>`，`fill-rule="evenodd"`。`FillPattern` 和纹理填充没有 SVG 等效物：图案通过填充的固有色 `color` 传递，而 `texture()` 指令被完全忽略。导出的标记可以无损地通过 `g.svg(...)` 返回，因此你可以导出、存储并在稍后重新导入形状到另一个 `Graphics`。

### 重用 GraphicsPath

```ts
const arrow = new GraphicsPath()
  .moveTo(0, 0)
  .lineTo(40, 0)
  .lineTo(40, -10)
  .lineTo(60, 10)
  .lineTo(40, 30)
  .lineTo(40, 20)
  .lineTo(0, 20)
  .closePath();

g.path(arrow).fill(0x3498db);
g.translateTransform(80, 0).path(arrow).fill(0xe74c3c);
```

`Graphics.path(graphicsPath)`（和 `GraphicsContext.path()`）将预构建的 `GraphicsPath` 添加到活动路径上。一次构建，多次绘制。

### 绘图时变换

`Graphics` 有自己的变换栈，用于**绘图时**，与应用于渲染输出的 `Container` 变换是分开的。绘图方法重命名以避免与 `Container.rotation`、`Container.scale`、`Container.position` 冲突：

| 绘图变换                                         | 容器变换       |
| --------------------------------------------------------- | ------------------------- |
| `g.rotateTransform(angle)`                                | `g.rotation`              |
| `g.scaleTransform(x, y?)`                                 | `g.scale.set(x, y)`       |
| `g.translateTransform(x, y?)`                             | `g.position.set(x, y)`    |
| `g.setTransform(matrix)` or `setTransform(a,b,c,d,tx,ty)` | `g.setFromMatrix(matrix)` |
| `g.transform(matrix)` or `transform(a,b,c,d,tx,ty)`       | n/a                       |
| `g.getTransform()` / `g.resetTransform()`                 | n/a                       |

```ts
const g = new Graphics();

g.translateTransform(100, 100)
  .rotateTransform(Math.PI / 4)
  .rect(-25, -25, 50, 50)
  .fill(0x3498db);

// 正方形在添加到几何形状时旋转 45 度。
// 设置 g.rotation 后，整个 Graphics 在屏幕上旋转。
```

绘图变换影响添加到上下文中的每个后续形状和路径命令。使用 `save()`/`restore()` 来限定范围。

### 状态保存/恢复

```ts
g.save();
g.translateTransform(100, 100);
g.rotateTransform(Math.PI / 4);
g.rect(0, 0, 50, 50).fill(0xff0000);
g.restore();
```

`save()` 将绘图变换、填充样式和线条样式推入栈中；`restore()` 将它们弹出。`Graphics` 直接暴露 `save`/`restore`，镜像底层的 `GraphicsContext` 调用。

### 默认样式通过 `setFillStyle` / `setStrokeStyle`

```ts
g.setFillStyle({ color: 0x3498db, alpha: 0.8 }).setStrokeStyle({
  width: 2,
  color: 0x2c3e50,
});

g.rect(0, 0, 100, 100).fill().stroke();
g.circle(150, 50, 40).fill().stroke();
```

`setFillStyle()` 和 `setStrokeStyle()` 配置后续 `fill()` / `stroke()` 调用使用的默认样式（当未传递参数时）。随时通过 `fillStyle` 和 `strokeStyle` 获取或替换当前样式。通过修改 `GraphicsContext.defaultFillStyle` 和 `GraphicsContext.defaultStrokeStyle` 在启动时覆盖库的默认值。

### 碰撞检测

```ts
const g = new Graphics().star(100, 100, 5, 60, 30).fill(0xf39c12);
g.eventMode = "static";
g.on("pointermove", (e) => {
  if (g.containsPoint(g.toLocal(e.global))) {
    /* 指向星星，而不仅仅是其 bbox */
  }
});
```

`Graphics.containsPoint(pointInLocalSpace)` 运行拓扑感知测试，针对上下文中的每个填充和线条形状（包括孔洞）。首先将全局指针坐标转换为本地坐标，使用 `toLocal()`。线条使用与填充相同的渐变和图案，通过 `fill: gradient` 或 `texture: tex`：

```ts
const grad = new FillGradient({
  end: { x: 1, y: 0 },
  colorStops: [
    { offset: 0, color: 0xff0000 },
    { offset: 1, color: 0x0000ff },
  ],
});
g.rect(0, 0, 200, 100).stroke({
  width: 8,
  fill: grad,
  join: "round",
  cap: "round",
});
```

`fill()` 和 `stroke()` 都可以在同一个形状之后调用；立即在 `fill()` 之后调用 `stroke()` 将重用相同的路径。

### 克隆、清除和边界

```ts
const g = new Graphics().rect(0, 0, 100, 100).fill(0xff0000);

const shallow = g.clone(); // 共享相同的 GraphicsContext
const deep = g.clone(true); // 创建一个独立的上下文

console.log(g.bounds.width); // 100 - 变换前的几何边界

g.clear(); // 清除活动路径、指令和变换；填充/线条样式保持不变
```

- `clone()` 返回一个新的 `Graphics`，共享源上下文（便宜，几何形状被重用）。如果上下文更改，两个对象会一起更新。
- `clone(true)` 克隆上下文，因此新的 `Graphics` 可以独立编辑。
- `bounds` 返回变换前的几何边界。用于布局决策。
- `clear()` 重置上下文，以便相同的 `Graphics` 可以重复使用。有关何时清除而不是保留稳定几何形状的指导，请参阅 **常见错误** 下面的内容。

### GraphicsContext 实用工具

| 成员                                          | 行为                                                                                             |
| ----------------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| `ctx.path(graphicsPath)`                        | 将预构建的 `GraphicsPath` 应用于活动路径。跨多个上下文或帧重用单个路径。                   |
| `ctx.beginPath()`                               | 丢弃当前活动路径并开始新路径，而不会影响已提交的指令。                                      |
| `ctx.setFillStyle(style)` / `ctx.fillStyle`     | 设置或读取后续形状使用的默认填充样式，而无需调用 `fill()`。                                     |
| `ctx.setStrokeStyle(style)` / `ctx.strokeStyle` | 设置或读取后续形状使用的默认线条样式，而无需调用 `stroke()`。                                     |
| `ctx.bounds`                                    | 跨所有填充/线条/纹理指令的缓存的几何边界。                                              |
| `ctx.clear()`                                   | 清除指令、活动路径和绘图变换。                                                               |
| `ctx.clone()`                                   | 包括指令、活动路径、变换、样式和堆栈的深度副本。                                              |
| `ctx.containsPoint(point)`                      | 对所有填充和线条形状（包括孔洞）进行拓扑感知的碰撞测试。                                        |
| `ctx.batchMode`                                 | `'auto'`、`'batch'`、`'no-batch'` 之一——强制或禁用此上下文中的形状的批处理。                 |
| `ctx.customShader`                              | 分配一个 `Shader` 以覆盖默认图形着色器。                                                    |
| `GraphicsContext.defaultFillStyle`              | 当 `fill()` 调用没有参数且没有设置填充样式时使用的静态后备。                                     |
| `GraphicsContext.defaultStrokeStyle`            | 当 `stroke()` 调用没有参数且没有设置线条样式时使用的静态后备。                                     |

`GraphicsContext` 是一个 `EventEmitter`，在上下文生命周期变化时发出 `update`、`destroy` 和 `unload` 事件。当工具或池需要对此做出反应时，通过 `ctx.on('update' | 'destroy' | 'unload', cb)` 订阅。

## 常见错误

### [CRITICAL] 使用 v7 beginFill/drawRect/endFill

错误：

```ts
const g = new Graphics().beginFill(0xff0000).drawRect(0, 0, 100, 100).endFill();
```

正确：

```ts
const g = new Graphics().rect(0, 0, 100, 100).fill(0xff0000);
```

v8 替换了 "设置样式、绘制、结束" 模式为 "绘制形状，然后应用样式"。`beginFill`/`endFill` 不存在。

### [CRITICAL] 使用旧的形状方法名称

错误：

```ts
g.drawCircle(50, 50, 25);
```

正确：

```ts
g.circle(50, 50, 25);
```

所有 `draw*` 方法在 v8 中重命名：`drawRect` → `rect`, `drawCircle` → `circle`, `drawEllipse` → `ellipse`, `drawPolygon` → `poly`, `drawRoundedRect` → `roundRect`, `drawStar` → `star`.

### [CRITICAL] 使用 lineStyle 而不是 stroke

错误：

```ts
g.lineStyle(2, 0xffffff);
g.drawRect(0, 0, 100, 100);
```

正确：

```ts
g.rect(0, 0, 100, 100).stroke({ width: 2, color: 0xffffff });
```

`lineStyle` 已移除。在绘制形状后使用 `stroke()`。线条样式对象接受 `width`, `color`, `alpha`, `cap`, `join`, `alignment`, `miterLimit` 和 `pixelLine`。

### [HIGH] 使用 beginHole/endHole 创建孔洞

错误：

```ts
g.beginFill(0x00ff00)
  .drawRect(0, 0, 100, 100)
  .beginHole()
  .drawCircle(50, 50, 20)
  .endHole()
  .endFill();
```

正确：

```ts
g.rect(0, 0, 100, 100).fill(0x00ff00).circle(50, 50, 20).cut();
```

`beginHole`/`endHole` 被 `cut()` 替代。绘制外部形状，填充它，然后绘制孔洞形状并调用 `cut()`。

### [HIGH] 使用 GraphicsGeometry 而不是 GraphicsContext

错误：

```ts
const geom = g.geometry;
const clone = new Graphics(geom);
```

正确：

```ts
const ctx = new GraphicsContext().rect(0, 0, 100, 100).fill(0xff0000);
const g1 = new Graphics(ctx);
const g2 = new Graphics(ctx);
```

`GraphicsGeometry` 在 v8 中被 `GraphicsContext` 替代。没有 `.geometry` 属性。

### [HIGH] 意外销毁共享的 GraphicsContext

```ts
const ctx = new GraphicsContext().rect(0, 0, 50, 50).fill(0xff0000);
const g1 = new Graphics(ctx);
const g2 = new Graphics(ctx);

g1.destroy({ context: true }); // g2 仍然持有已销毁的上下文
```

销毁共享的 `GraphicsContext` 不会销毁使用它的其他 `Graphics`，但它们保留对已销毁的上下文的引用，并且停止更新或渲染。当通过构造函数传递上下文时，`destroy()` 没有参数会保留上下文并使实例与其分离；使用 `destroy({ context: false })` 以明确。仅在所有共享实例都使用它时才销毁上下文。自拥有的上下文（未通过构造函数传递）仍然可以通过 `destroy()` 没有参数销毁。

### [HIGH] 每帧清除并重绘 Graphics

Graphics 设计为稳定，而不是动态的。每帧调用 `clear()` 并重绘会每次重建 GPU 几何形状。对于动态视觉效果：

- 使用 `Sprite` 和预渲染纹理以及变换更改。
- 使用 `cacheAsTexture(true)` 对于复杂的静态图形。
- 对于实时形状更改，请考虑 `Mesh` 和自定义几何形状更新。

这是 HTML Canvas 2D 的反面，其中每帧重绘是正常的。PixiJS 将形状 tessellated 为 GPU 三角形，因此初始绘制昂贵，但后续渲染速度快。将 `Graphics` 更像 SVG 元素而不是 canvas 绘制调用。

### [MEDIUM] 不要在 Graphics 内嵌子节点

`Graphics` 设置 `allowChildren = false`。添加子节点会记录弃用警告，在未来的版本中将是硬错误。将多个图形与其他叶节点一起包装在普通的 `Container` 中：

```ts
const group = new Container();
group.addChild(graphics, sprite);
```
