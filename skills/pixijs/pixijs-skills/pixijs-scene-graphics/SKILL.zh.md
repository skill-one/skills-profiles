---
name: pixijs-scene-graphics
description: 在 PixiJS v8 中绘制矢量形状和路径时使用此技能。涵盖 Graphics API：形状-填充方法（rect/circle/ellipse/poly/roundRect/star/regularPoly/roundPoly/roundShape/filletRect/chamferRect）、路径方法（moveTo/lineTo/bezierCurveTo/quadraticCurveTo/arc/arcTo/arcToSvg/closePath）、填充/描边/切割、孔洞、FillGradient（线性/径向）、FillPattern、GraphicsContext 共享、svg 导入/导出、containsPoint 碰撞检测、克隆、清除、边界、fillStyle/strokeStyle、绘制时变换（rotateTransform/scaleTransform/translateTransform/setTransform/save/restore）、默认样式、GraphicsPath 重用。触发条件：Graphics、GraphicsContext、rect、circle、poly、roundRect、fill、stroke、cut、hole、beginHole、FillGradient、FillPattern、moveTo、bezierCurveTo、svg、graphicsContextToSvg、svg 导出、GraphicsOptions、containsPoint、clone、clear、bounds、rotateTransform、translateTransform、setFillStyle、setStrokeStyle、GraphicsPath。
---

`Graphics` 是 PixiJS v8 场景图的矢量绘图分支。v8 API 遵循形状优先于样式的模式：使用 `rect`、`circle`、`moveTo` 等绘制形状或路径，然后应用 `fill` 和/或 `stroke`。每个方法都返回 `this` 以支持链式调用，绘图指令存储在 `GraphicsContext` 中，该上下文可以在实例之间共享。

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

**相关技能：** `pixijs-scene-core-concepts`（场景图基础）、`pixijs-scene-container`（与其他对象组合图形）、`pixijs-scene-core-concepts/references/masking.md`（Graphics 作为遮罩）、`pixijs-filters`（效果）、`pixijs-performance`（批处理、`cacheAsTexture`）。

## 构造函数选项

所有 `Container` 选项（`position`、`scale`、`tint`、`label`、`filters`、`zIndex` 等）在此处也有效——请参阅 `skills/pixijs-scene-core-concepts/references/constructor-options.md`。

由 `GraphicsOptions` 添加的特定于叶节点的选项：

| 选项        | 类型              | 默认                 | 描述                                                                                                                                                                                          |
| ------------- | ----------------- | ----------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `context`     | `GraphicsContext` | new `GraphicsContext()` | 共享绘图上下文。传递上下文可在多个 `Graphics` 节点之间重用其 tessellated 几何形状，避免重复 GPU 工作。如果省略，每个 `Graphics` 都会创建并拥有一个新的上下文。 |
| `roundPixels` | `boolean`         | `false`                 | 将屏幕上的最终 `x`/`y` 四舍五入到最近的像素。为像素艺术风格生成更清晰的线条，但会牺牲亚像素移动的平滑度。                                                       |

构造函数也接受 `GraphicsContext` 实例作为其唯一参数（`new Graphics(ctx)`），这是 `new Graphics({ context: ctx })` 的简写。

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

- `'local'`（默认）：纹理按每个形状的边界框缩放（归一化 0-1 坐标）。
- `'global'`：纹理位置/缩放相对于 Graphics 对象的坐标系，在所有形状之间共享。
- 图集子纹理：`'global'` 尊重帧原点和旋转，因此绘制在帧大小处的形状与该帧的 `Sprite` 匹配。`'local'` 映射整个源图像；传递一个 `matrix` 以针对源图像的帧区域，或先使用 `renderer.generateTexture()` 处理帧。

`FillInput` 还支持嵌套的 `fill` 子字段：一个 `FillStyle` 选项对象可以在其 `fill` 键下嵌入 `FillGradient` 或 `FillPattern`，该渐变或图案将与外对象上的 `color`、`alpha`、`texture` 和 `matrix` 修饰符一起应用。

`stroke()` 接受颜色、`FillGradient`、`FillPattern` 或一个 `StrokeStyle` 对象，该对象组合了所有 `FillStyle` 键（`color`、`alpha`、`texture`、`matrix`、`fill`、`textureSpace`）与描边属性：

| 属性    | 默认   | 备注                                                                   |
| ------------ | --------- | ----------------------------------------------------------------------- |
| `width`      | `1`       | 描边的像素宽度。                                              |
| `cap`        | `'butt'`  | `'butt'`、`'round'`、`'square'` 之一。开放路径的端点样式。       |
| `join`       | `'miter'` | `'miter'`、`'round'`、`'bevel'` 之一。角落样式。                   |
| `miterLimit` | `10`      | 限制 miter 连接延伸的距离，超出后回退到 bevel。           |
| `alignment`  | `0.5`     | `1` = 形状内部，`0.5` = 居中，`0` = 外部。                |
| `pixelLine`  | `false`   | 将 1 像素线条对齐到像素网格以获得清晰的输出。Graphics-only。 |

描边可以使用与填充相同的渐变和图案，通过 `fill: gradient` 或 `texture: tex`：

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

`fill()` 和 `stroke()` 都可以在同一个形状之后被调用；在 `fill()` 之后立即调用 `stroke()` 会重用相同的路径。

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

### 使用 cut() 创建孔洞

```ts
g.rect(0, 0, 200, 200).fill(0x00ff00).circle(100, 100, 50).cut();
```

`cut()` 从先前绘制的填充或描边中减去当前活动路径。规则：

- 孔洞必须完全**位于**目标形状内部。重叠边缘或位于形状外部的孔洞将无法正确渲染，因为渲染器将孔洞作为内部边界进行三角剖分。
- `cut()` 会回溯**最多两个**指令。当你对相同路径进行 `fill()` 和 `stroke()` 时，单个 `cut()` 首先在描边中添加孔洞；第二个 `cut()` 在下方的填充中添加。
- `cut()` 后，活动路径会重置，因此你可以使用 `moveTo`、`rect` 等开始下一个形状。
- `cut()` 也适用于描边——`g.rect(...).stroke(...).circle(...).cut()` 在描边轮廓中切割孔洞。

通过在调用 `cut()` 之前绘制多个形状到活动路径中，使用单个 `cut()` 切割多个孔洞。每个形状都会累积到相同的孔洞路径中：

```ts
const g = new Graphics();

g.rect(350, 350, 150, 150).fill(0x00ff00);

// 绘制三个圆到活动路径中，然后一次调用 cut() 切割它们
g.circle(375, 375, 25);
g.circle(425, 425, 25);
g.circle(475, 475, 25);
g.cut();
```

如果您需要在**不同**的填充形状上创建孔洞，请为每个形状提供自己的 `fill()` 和匹配的 `cut()`：

```ts
g.rect(0, 0, 100, 100).fill(0x3498db);
g.circle(50, 50, 20).cut(); // 矩形中的孔洞

g.rect(120, 0, 100, 100).fill(0xe74c3c);
g.circle(170, 50, 20).cut(); // 第二个矩形中的孔洞
```

在已具有孔洞的形状上调用 `cut()` **会添加**到现有的孔洞路径，而不是替换它。使用此方法将孔洞加法叠加。

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

路径方法：`moveTo`、`lineTo`、`bezierCurveTo`、`quadraticCurveTo`、`arc`、`arcTo`、`arcToSvg`、`closePath`。调用 `beginPath()` 以丢弃当前路径并开始一个新路径。

```ts
// arc(cx, cy, radius, startAngle, endAngle, counterclockwise?)
g.moveTo(80, 50)
  .arc(50, 50, 30, 0, Math.PI)
  .stroke({ width: 4, color: 0x2c3e50 });

// arcTo(x1, y1, x2, y2, radius) — 在两段线段之间绘制圆角
g.moveTo(150, 20)
  .arcTo(200, 20, 200, 80, 20)
  .lineTo(200, 80)
  .stroke({ width: 2 });

// arcToSvg(rx, ry, xAxisRotation, largeArcFlag, sweepFlag, x, y) — 匹配 SVG 的 `A` 命令
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

// 像素坐标需要 textureSpace: "global"；渐变然后跨形状扩展。
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

`FillGradient` 的默认 `type` 是 `'linear'`，从 `start {0,0}` 到 `end {0,1}`（垂直）。设置 `type: 'radial'` 并使用 `center`/`innerRadius` 和 `outerCenter`/`outerRadius` 创建径向渐变；`rotation`（弧度，默认 `0`）和 `scale`（默认 `1`）使其呈椭圆形，并仅适用于 Graphics。`textureSpace` 默认为 `'local'`（归一化 0-1 形状坐标）；使用 `'global'` 以像素坐标跨形状共享。

`FillPattern` 接受一个选项对象（`{ texture, repetition?, textureSpace? }`）或遗留的位置形式（`new FillPattern(texture, repetition?)`）。`repetition` 选择平铺模式。`textureSpace` 控制瓷砖如何映射到形状：

- `'global'`（默认）：瓷砖在 `Graphics` 坐标系中连续平铺，因此相邻形状共享一个平铺网格。最适合背景和无缝纹理。
- `'local'`：单个瓷砖适合每个形状的边界。结合 `setTransform` 将形状细分为瓷砖网格。

注意 `FillPattern` 默认 `textureSpace` 为 `'global'`，而纹理填充的默认值为 `'local'`，如上所示。

`setTransform(matrix)` 将给定的矩阵直接复制到图案变换上，以缩放、旋转或偏移平铺；不带参数调用 `setTransform()` 以重置为单位矩阵。

在 `FillPattern` 上设置 `textureSpace` 和变换。当图案作为样式对象传递（`fill({ fill: pattern, textureSpace: "local" })`）时，图案自己的值将替换样式的 `textureSpace` 和 `matrix`。

### 直接绘制纹理

```ts
const tex = await Assets.load("icon.png");

// 在 (x, y) 处绘制整个纹理，可选着色
g.texture(tex, 0xffffff, 20, 20);

// 绘制子区域 (dx, dy, dw, dh)
g.texture(tex, 0xff0000, 100, 20, 64, 64);
```

`Graphics.texture(texture, tint?, dx?, dy?, dw?, dh?)` 是绘制单个带纹理矩形而不通过 `fill()` 的快捷方式。适用于不需要完整精灵生命周期的图标。

### GraphicsContext 共享

```ts
const ctx = new GraphicsContext().rect(0, 0, 50, 50).fill(0xff0000);

const g1 = new Graphics(ctx);
const g2 = new Graphics(ctx);
g2.x = 100;
```

上下文共享避免了重复 GPU 几何形状；昂贵的 tessellation 只运行一次。您也可以在构建后分配上下文：`g.context = existingContext`。

### SVG 导入和导出

使用 `svg()` 将 SVG 标记解析到活动上下文中：

```ts
g.svg(`<svg viewBox="0 0 100 100">
    <circle cx="50" cy="50" r="40" fill="red"/>
</svg>`);
```

`svg()` 解析 `<path>`（`fill-rule="evenodd"` 孔洞）、`<rect>`、`<circle>`、`<ellipse>`、`<line>`、`<polygon>`、`<polyline>` 和 `<g>` 分组。样式来自 `fill`、`stroke`、`stroke-width`、`fill-opacity`、`stroke-opacity` 和 `opacity`，作为属性或内联 `style`。`<linearGradient>` 和 `<radialGradient>` 定义在 `<defs>` 中成为通过 `url(#id)` 应用的 `FillGradient`；`gradientUnits` 映射到 `textureSpace` 和百分比坐标被接受。不支持：`transform` 属性、`<style>` 块、`stroke-linecap`/`stroke-linejoin`/`stroke-dasharray`、`gradientTransform`、`spreadMethod`、`stop-opacity`、`<text>`、`<image>`、`<use>`、`<clipPath>`、`<mask>`、`<pattern>`。不支持的元素记录警告并跳过。复杂的孔洞几何形状可能渲染不准确，因为 Pixi 的三角剖分是针对性能优化的。

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

`graphicsContextToSvg(source, precision = 2)` 是一个纯函数，它读取上下文的指令并返回一个完整的 `<svg>` 字符串，带有自动计算的 `viewBox`。传递一个 `Graphics` 或一个 `GraphicsContext`；`precision` 控制输出的坐标小数位数。导出每个形状-然后-填充原语（高级原语如 `regularPoly`/`filletRect` 回退到形状路径）、所有路径方法、描边属性（`width`、`cap`、`join`、`miterLimit`）、`fill-opacity`/`stroke-opacity` 和 `FillGradient`（线性和径向）通过 `<defs>` 块。孔洞合并为一个 `<path>`，`fill-rule="evenodd"`。`FillPattern` 和纹理填充没有 SVG 等价物：图案透过后填充的实心 `color`，而 `texture()` 指令被完全跳过。导出的标记通过 `g.svg(...)` 无清理地返回，因此您可以导出、存储，稍后重新导入形状到另一个 `Graphics`。

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

`Graphics.path(graphicsPath)`（和 `GraphicsContext.path()`）将预构建的 `GraphicsPath` 追加到活动路径上。一次构建，多次绘制。

### 绘图时变换

`Graphics` 有自己的变换栈，在**绘图时**使用，与应用于渲染输出的 `Container` 变换分开。绘图方法是重命名的，以避免与 `Container.rotation`、`Container.scale`、`Container.position` 冲突：

| 绘图变换                                         | 容器变换       |
| --------------------------------------------------------- | ------------------------- |
| `g.rotateTransform(angle)`                                | `g.rotation`              |
| `g.scaleTransform(x, y?)`                                 | `g.scale.set(x, y)`       |
| `g.translateTransform(x, y?)`                             | `g.position.set(x, y)`    |
| `g.setTransform(matrix)` 或 `setTransform(a,b,c,d,tx,ty)` | `g.setFromMatrix(matrix)` |
| `g.transform(matrix)` 或 `transform(a,b,c,d,tx,ty)`       | n/a                       |
| `g.getTransform()` / `g.resetTransform()`                 | n/a                       |

```ts
const g = new Graphics();

g.translateTransform(100, 100)
  .rotateTransform(Math.PI / 4)
  .rect(-25, -25, 50, 50)
  .fill(0x3498db);

// 正方形在添加到几何图形时旋转了45度。
// 设置 g.rotation 后会在屏幕上旋转整个 Graphics。
```

绘图变换会影响添加到上下文中的每个后续形状和路径命令。使用 `save()`/`restore()` 来限定范围。

### 状态保存/恢复

```ts
g.save();
g.translateTransform(100, 100);
g.rotateTransform(Math.PI / 4);
g.rect(0, 0, 50, 50).fill(0xff0000);
g.restore();
```

`save()` 将绘图变换、填充样式和描边样式推到栈上；`restore()` 将它们弹出。`Graphics` 直接暴露 `save`/`restore`，镜像底层的 `GraphicsContext` 调用。

### 默认样式通过 setFillStyle / setStrokeStyle

```ts
g.setFillStyle({ color: 0x3498db, alpha: 0.8 }).setStrokeStyle({
  width: 2,
  color: 0x2c3e50,
});

g.rect(0, 0, 100, 100).fill().stroke();
g.circle(150, 50, 40).fill().stroke();
```

`setFillStyle()` 和 `setStrokeStyle()` 配置后续 `fill()` / `stroke()` 调用在没有参数时使用的默认样式。随时通过 `fillStyle` 和 `strokeStyle` 的 getter/setter 读取或替换当前样式。通过在启动时修改 `GraphicsContext.defaultFillStyle` 和 `GraphicsContext.defaultStrokeStyle` 来覆盖库范围的默认值。

### 碰撞检测

```ts
const g = new Graphics().star(100, 100, 5, 60, 30).fill(0xf39c12);
g.eventMode = "static";
g.on("pointermove", (e) => {
  if (g.containsPoint(g.toLocal(e.global))) {
    /* 在星星上，不仅仅是它的 bbox */
  }
});
```

`Graphics.containsPoint(pointInLocalSpace)` 对上下文中的每个填充和描边的形状（包括孔洞）运行拓扑感知测试。首先使用 `toLocal()` 转换全局指针坐标。描边的形状会检测到绘制的描边：碰撞带跟随描边的 `width` 和 `alignment` (`1` 内部，`0.5` 居中，`0` 外部)，与多边形的环绕顺序无关。

### 克隆、清除和边界

```ts
const g = new Graphics().rect(0, 0, 100, 100).fill(0xff0000);

const shallow = g.clone(); // 共享相同的 GraphicsContext
const deep = g.clone(true); // 创建独立的上下文

console.log(g.bounds.width); // 100 - 变换前的几何边界

g.clear(); // 清除活动路径、指令和变换；填充/描边样式保持不变
```

- `clone()` 返回一个新的 `Graphics`，它共享源上下文（廉价，几何图形被重用）。如果上下文更改，两个对象会一起更新。
- `clone(true)` 克隆上下文，以便新的 `Graphics` 可以独立编辑。
- `bounds` 返回变换前的几何边界。适用于布局决策。
- `clear()` 重置上下文，以便相同的 `Graphics` 可以重复使用。见 **常见错误** 部分关于何时清除以及何时保持稳定几何图形的指导。

### GraphicsContext 工具

| 成员                                          | 行为                                                                                             |
| ----------------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| `ctx.path(graphicsPath)`                        | 将预构建的 `GraphicsPath` 应用到活动路径。跨多个上下文或帧重用一条路径。                         |
| `ctx.beginPath()`                               | 抛弃当前活动路径并开始新路径，不影响已提交的指令。                                                |
| `ctx.setFillStyle(style)` / `ctx.fillStyle`     | 设置或读取后续形状使用的默认填充样式，而无需调用 `fill()`。                                        |
| `ctx.setStrokeStyle(style)` / `ctx.strokeStyle` | 设置或读取后续形状使用的默认描边样式，而无需调用 `stroke()`。                                    |
| `ctx.bounds`                                    | 跨所有填充/描边/纹理指令的缓存几何边界。                                                        |
| `ctx.clear()`                                   | 清除指令、活动路径和绘图变换。                                                                    |
| `ctx.clone()`                                   | 深拷贝，包括指令、活动路径、变换、样式和栈。                                                      |
| `ctx.containsPoint(point)`                      | 对所有填充和描边的形状（包括孔洞）进行拓扑感知的碰撞检测。                                        |
| `ctx.batchMode`                                 | `'auto'`、`'batch'`、`'no-batch'` — 强制或禁用此上下文中的形状的批处理。                          |
| `ctx.customShader`                              | 为覆盖默认图形着色器分配一个 `Shader`。                                                          |
| `GraphicsContext.defaultFillStyle`              | 当 `fill()` 被调用而没有参数且未设置填充样式时使用的静态回退。                                    |
| `GraphicsContext.defaultStrokeStyle`            | 当 `stroke()` 被调用而没有参数且未设置描边样式时使用的静态回退。                                    |

`GraphicsContext` 是一个 `EventEmitter`，它发出 `update`、`destroy` 和 `unload` 事件。当工具或池需要响应上下文生命周期变化时，通过 `ctx.on('update' | 'destroy' | 'unload', cb)` 订阅。

## 常见错误

### [严重] 使用 v7 beginFill/drawRect/endFill

错误：

```ts
const g = new Graphics().beginFill(0xff0000).drawRect(0, 0, 100, 100).endFill();
```

正确：

```ts
const g = new Graphics().rect(0, 0, 100, 100).fill(0xff0000);
```

v8 用“设置样式、绘制、结束”替换为“绘制形状，然后应用样式”。`beginFill`/`endFill` 不存在。

### [严重] 使用旧的形状方法名称

错误：

```ts
g.drawCircle(50, 50, 25);
```

正确：

```ts
g.circle(50, 50, 25);
```

v8 中所有 `draw*` 方法都被重命名：`drawRect` → `rect`，`drawCircle` → `circle`，`drawEllipse` → `ellipse`，`drawPolygon` → `poly`，`drawRoundedRect` → `roundRect`，`drawStar` → `star`。

### [严重] 使用 lineStyle 而不是 stroke

错误：

```ts
g.lineStyle(2, 0xffffff);
g.drawRect(0, 0, 100, 100);
```

正确：

```ts
g.rect(0, 0, 100, 100).stroke({ width: 2, color: 0xffffff });
```

`lineStyle` 已被移除。在绘制形状后使用 `stroke()`。描边选项对象接受 `width`、`color`、`alpha`、`cap`、`join`、`alignment`、`miterLimit` 和 `pixelLine`。

### [高] 使用 beginHole/endHole 来创建孔洞

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

`beginHole`/`endHole` 被 `cut()` 替换。绘制外形状，填充它，然后绘制孔洞形状并调用 `cut()`。

### [高] 使用 GraphicsGeometry 而不是 GraphicsContext

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

`GraphicsGeometry` 在 v8 中被 `GraphicsContext` 替换。没有 `.geometry` 属性。

### [高] 意外销毁共享的 GraphicsContext

```ts
const ctx = new GraphicsContext().rect(0, 0, 50, 50).fill(0xff0000);
const g1 = new Graphics(ctx);
const g2 = new Graphics(ctx);

g1.destroy({ context: true }); // g2 仍然持有已销毁的上下文
```

销毁共享的 `GraphicsContext` 不会销毁使用它的其他 `Graphics`，但它们会保留对已销毁上下文的引用，并且停止正确更新或渲染。当通过构造函数传递上下文时，`destroy()` 不带参数会保留上下文并使实例与其分离；使用 `destroy({ context: false })` 以明确。仅在所有共享实例都使用完上下文时才销毁上下文。自有的上下文（未通过构造函数传递）仍然可以通过不带参数的 `destroy()` 销毁。

### [高] 每帧清除并重绘 Graphics

Graphics 设计为稳定，而不是动态。每次调用 `clear()` 并重绘每帧都会每次重建 GPU 几何图形。对于动态视觉效果：

- 使用 `Sprite` 和预渲染纹理以及变换更改。
- 使用 `cacheAsTexture(true)` 对于复杂的静态图形。
- 对于实时形状更改，考虑使用 `Mesh` 和自定义几何图形更新。

这与 HTML Canvas 2D 相反，其中每帧重绘是正常的。PixiJS 将形状 tessellate 成 GPU 三角形，因此初始绘制成本很高，但后续渲染速度快。将 `Graphics` 视为 SVG 元素，而不是 canvas 绘制调用。

### [中] 不要在 Graphics 中嵌套子元素

`Graphics` 设置 `allowChildren = false`。添加子元素会记录弃用警告，并在未来版本中成为硬错误。将多个 Graphics 与其他叶子一起包裹在普通的 `Container` 中：

```ts
const group = new Container();
group.addChild(graphics, sprite);
```

## API 参考

- [Graphics](https://pixijs.download/release/docs/scene.Graphics.html.md)
- [GraphicsOptions](https://pixijs.download/release/docs/scene.GraphicsOptions.html.md)
- [GraphicsContext](https://pixijs.download/release/docs/scene.GraphicsContext.html.md)
- [GraphicsPath](https://pixijs.download/release/docs/scene.GraphicsPath.html.md)
- [graphicsContextToSvg](https://pixijs.download/release/docs/scene.graphicsContextToSvg.html.md)
- [FillGradient](https://pixijs.download/release/docs/scene.FillGradient.html.md)
- [FillPattern](https://pixijs.download/release/docs/scene.FillPattern.html.md)
- [FillStyle](https://pixijs.download/release/docs/scene.FillStyle.html.md)
- [FillInput](https://pixijs.download/release/docs/scene.FillInput.html.md)
