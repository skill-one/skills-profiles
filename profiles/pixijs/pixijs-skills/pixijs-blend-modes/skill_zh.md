将 `container.blendMode` 设置为使用 GPU 混合方程（标准模式）或基于滤镜的高级模式来组合显示对象。混合模式转换会破坏渲染批次，因此请将具有相同模式的同级对象组合在一起。

## 快速入门

```ts
const light = new Sprite(await Assets.load("light.png"));
light.blendMode = "add";
app.stage.addChild(light);

const shadow = new Sprite(await Assets.load("shadow.png"));
shadow.blendMode = "multiply";
app.stage.addChild(shadow);

import "pixi.js/advanced-blend-modes";
const overlay = new Sprite(await Assets.load("overlay.png"));
overlay.blendMode = "color-burn";
app.stage.addChild(overlay);
```

**相关技能：** `pixijs-filters`（高级模式使用滤镜管线）、`pixijs-performance`（使用混合模式的批次处理）、`pixijs-color`（颜色操作）。

## 核心模式

### 标准混合模式

标准模式是内置的，并直接使用 GPU 混合方程：

```ts
import { Sprite } from "pixi.js";

sprite.blendMode = "normal"; // 标准alpha混合（根节点处的有效默认值）
sprite.blendMode = "add"; // 加法（变亮、辉光效果）
sprite.blendMode = "multiply"; // 乘法（变暗、阴影效果）
sprite.blendMode = "screen"; // 滤镜（变亮、减淡效果）
sprite.blendMode = "erase"; // 从渲染目标擦除像素
sprite.blendMode = "none"; // 无混合，覆盖目标
sprite.blendMode = "inherit"; // 从父级继承（这是实际默认值）
sprite.blendMode = "min"; // 保持源和目标的最小值（仅WebGL2+）
sprite.blendMode = "max"; // 保持源和目标的最大值（仅WebGL2+）
```

这些是硬件加速的，成本较低。它们不需要滤镜。

### 高级混合模式

高级模式需要显式导入以注册扩展。在 WebGL 渲染器上，它们在初始化时也需要 `useBackBuffer: true`，否则 PixiJS 会记录警告，混合模式会静默回退：

```ts
import "pixi.js/advanced-blend-modes";
import { Application, Sprite, Assets } from "pixi.js";

const app = new Application();
await app.init({ useBackBuffer: true }); // WebGL上使用高级模式所需的

const texture = await Assets.load("overlay.png");
const overlay = new Sprite(texture);
overlay.blendMode = "color-burn";
```

可用的高级模式：

| 模式           | 效果                                          |
| -------------- | ----------------------------------------------- |
| `color-burn`   | 通过增加对比度变暗                            |
| `color-dodge`  | 通过减少对比度变亮                            |
| `darken`       | 保持两层中较暗的                              |
| `difference`   | 绝对差值                                      |
| `divide`       | 用底部除以顶部                                |
| `exclusion`    | 类似于差值，对比度较低                        |
| `hard-light`   | 根据顶部层进行乘法或滤镜                     |
| `hard-mix`     | 高对比度阈值混合                              |
| `lighten`      | 保持两层中较亮的                              |
| `linear-burn`  | 通过加法和减法变暗                            |
| `linear-dodge` | 将层组合在一起                                |
| `linear-light` | 基于顶部层的线性烧灼或减淡                   |
| `luminosity`   | 顶部层的亮度，底层的色相/饱和度               |
| `negation`     | 反转差值                                      |
| `overlay`      | 基于底部层的乘法或滤镜                       |
| `pin-light`    | 基于亮度比较替换                              |
| `saturation`   | 顶部层的饱和度，底层的色相/亮度               |
| `soft-light`   | 轻柔的叠加效果                                |
| `subtract`     | 用顶部减去底部                                |
| `vivid-light`  | 基于顶部层的颜色烧灼或减淡                   |
| `color`        | 顶部层的色相和饱和度，底层的亮度               |

您设置高级混合模式的方式与标准模式相同，通过 `blendMode` 属性。它们内部使用滤镜，因此成本高于标准模式。

### 批次友好的排序

不同的混合模式会破坏渲染批次。排序对象以最小化转换：

```ts
import { Container, Sprite } from "pixi.js";

const scene = new Container();
scene.addChild(screenSprite1); // 'screen'
scene.addChild(screenSprite2); // 'screen'
scene.addChild(normalSprite1); // 'normal'
scene.addChild(normalSprite2); // 'normal'
```

2 个绘制调用。交替顺序（`screen, normal, screen, normal`）会产生 4 个。

## 常见错误

### [高] 未导入 advanced-blend-modes 扩展

错误：

```ts
import { Sprite } from "pixi.js";

sprite.blendMode = "color-burn"; // 静默回退到 normal
```

正确：

```ts
import "pixi.js/advanced-blend-modes";
import { Sprite } from "pixi.js";

sprite.blendMode = "color-burn";
```

高级混合模式（color-burn、overlay 等）需要扩展导入。没有它，只有标准模式（normal、add、multiply、screen）可用。无效模式静默回退。

### [中] 在相邻对象之间混合混合模式

不同的混合模式会破坏渲染批次。`screen / normal / screen / normal` 产生 4 个绘制调用，而 `screen / screen / normal / normal` 产生 2 个。排序子对象，使具有相同混合模式的对象相邻。

### [高] 使用 v7 BLEND_MODES 枚举

错误：

```ts
import { BLEND_MODES } from "pixi.js";

sprite.blendMode = BLEND_MODES.ADD; // 运行时错误：BLEND_MODES 未定义
```

正确：

```ts
sprite.blendMode = "add";
```

在 v8 中，`BLEND_MODES` 只是一个 TypeScript 类型（字符串字面量联合）。没有运行时枚举导出，因此 `BLEND_MODES.ADD` 评估为访问 `undefined` 的属性。使用字符串形式。

### [高] 没有使用 useBackBuffer 的高级混合模式

错误：

```ts
import "pixi.js/advanced-blend-modes";
await app.init({
  /* no useBackBuffer */
});
sprite.blendMode = "color-burn"; // 记录警告，回退
```

正确：

```ts
import "pixi.js/advanced-blend-modes";
await app.init({ useBackBuffer: true });
sprite.blendMode = "color-burn";
```

高级模式从后缓冲区读取。在 WebGL 上，如果后缓冲区未启用，混合模式会静默回退。WebGPU 无条件启用后缓冲区。

### [中] 高DPI渲染器上高级混合模式被裁剪或缩放

高级混合模式基于滤镜，并使用 `Filter.defaultOptions`，其分辨率默认为 `1`。在高DPI渲染目标上，混合对象可能看起来被裁剪、缩放或只部分应用。

错误：

```ts
import "pixi.js/advanced-blend-modes";

sprite.blendMode = "overlay"; // 在视网膜上以分辨率 1 渲染，可能裁剪
```

正确：

```ts
import { Filter } from "pixi.js";
import "pixi.js/advanced-blend-modes";

Filter.defaultOptions.resolution = "inherit"; // 在创建受影响对象之前设置

sprite.blendMode = "overlay";
```

设置 `Filter.defaultOptions.resolution = "inherit"` 使高级混合模式在渲染目标的分辨率上渲染。这会消耗更多内存和运行时，因此仅在保真度重要时应用。

## API 参考

- [Container.blendMode](https://pixijs.download/release/docs/scene.Container.html.md)
- [OverlayBlend](https://pixijs.download/release/docs/filters.OverlayBlend.html.md)
- [ColorBurnBlend](https://pixijs.download/release/docs/filters.ColorBurnBlend.html.md)
- [ColorDodgeBlend](https://pixijs.download/release/docs/filters.ColorDodgeBlend.html.md)
- [HardLightBlend](https://pixijs.download/release/docs/filters.HardLightBlend.html.md)
- [SoftLightBlend](https://pixijs.download/release/docs/filters.SoftLightBlend.html.md)
- [DifferenceBlend](https://pixijs.download/release/docs/filters.DifferenceBlend.html.md)
