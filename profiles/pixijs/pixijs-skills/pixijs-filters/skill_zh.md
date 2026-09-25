通过将一个滤镜（或用于链式操作的数组）分配给 `container.filters` 来附加视觉效果。内置滤镜涵盖模糊、颜色矩阵、置换、透明度和噪声；自定义滤镜通过 `Filter.from(...)` 封装 GLSL/WGSL 片段着色器。

## 快速入门

```ts
const sprite = new Sprite(await Assets.load("hero.png"));
app.stage.addChild(sprite);

const blur = new BlurFilter({ strength: 4, quality: 4 });
const colorMatrix = new ColorMatrixFilter();
colorMatrix.brightness(1.2, false);

sprite.filters = [blur, colorMatrix];

const container = new Container();
container.filters = [new BlurFilter({ strength: 2 })];
container.filterArea = new Rectangle(0, 0, 800, 600);
app.stage.addChild(container);
```

**相关技能：** `pixijs-custom-rendering`（着色器内部、统一变量类型）、`pixijs-blend-modes`（与滤镜合成）、`pixijs-performance`（滤镜调优、filterArea）。

## 核心模式

### 内置滤镜

```ts
import {
  AlphaFilter,
  BlurFilter,
  ColorMatrixFilter,
  DisplacementFilter,
  NoiseFilter,
  Assets,
  Sprite,
} from "pixi.js";

// Alpha（无子层分层的一律透明度）
const alpha = new AlphaFilter({ alpha: 0.5 });

// 模糊 — strength/quality 是一元的；strengthX/strengthY 分割轴；
// kernelSize 必须是奇数（5, 7, 9, ... 15）；repeatEdgePixels 避免透明边缘
const blur = new BlurFilter({
  strength: 4,
  quality: 4,
  kernelSize: 5,
  repeatEdgePixels: false,
});

// 颜色矩阵 — 亮度是许多预设之一。其他：色调，
// 对比度、饱和度、去饱和度、灰度/灰度、黑白、负片、棕褐色、复古、
// 颜色色调、夜晚、捕食者、迷幻、重置。直接通过 `colorMatrix.matrix`（20元素数组）和 `colorMatrix.alpha`（在原始和转换之间混合）访问。
const colorMatrix = new ColorMatrixFilter();
colorMatrix.brightness(1.5, false);
colorMatrix.contrast(0.5, true); // 乘法堆叠在现有矩阵之上
colorMatrix.alpha = 0.7; // 70% 强度混合

// 置换 — scale 是一个数字或 PointData
const displacementTexture = await Assets.load("displacement_map.png");
const displacementSprite = new Sprite(displacementTexture);
const displacement = new DisplacementFilter({
  sprite: displacementSprite,
  scale: { x: 20, y: 10 },
});

// 噪声 — seed 是一个任意数字，它决定了噪声模式；相同的 seed 重复产生相同的模式
const noise = new NoiseFilter({ noise: 0.5, seed: Math.random() });

sprite.filters = [blur, colorMatrix];
```

### 使用 Filter.from() 创建自定义滤镜

创建自定义滤镜的最简单方法。只需要片段着色器；PixiJS 提供默认的顶点着色器。

```ts
import { Filter } from "pixi.js";

const filter = Filter.from({
  gl: {
    fragment: `
            in vec2 vTextureCoord;
            out vec4 finalColor;
            uniform sampler2D uTexture;
            uniform float uTime;

            void main() {
                vec2 uv = vTextureCoord;
                uv.x += sin(uv.y * 10.0 + uTime) * 0.02;
                finalColor = texture(uTexture, uv);
            }
        `,
  },
  resources: {
    timeUniforms: {
      uTime: { value: 0, type: "f32" },
    },
  },
});

sprite.filters = filter;

app.ticker.add((ticker) => {
  filter.resources.timeUniforms.uniforms.uTime += 0.04 * ticker.deltaTime;
});
```

要获得更多控制，直接构建 `GlProgram`/`GpuProgram` 对象：

```ts
import { Filter, GlProgram } from "pixi.js";

const glProgram = GlProgram.from({ fragment: fragmentSrc, vertex: vertexSrc });

const filter = new Filter({
  glProgram,
  resources: {
    timeUniforms: {
      uTime: { value: 0, type: "f32" },
    },
  },
});
```

要点：

- 片段着色器中使用 `out vec4 finalColor`，而不是 `gl_FragColor`（GLSL ES 3.0）。
- 使用 `texture()` 采样，而不是 `texture2D`。
- `glProgram` 用于 WebGL，`gpuProgram` 用于 WebGPU。省略其中一个将跳过该渲染器。
- 纹理放在 `resources` 中，而不是统一变量。滤镜系统自动提供 `uTexture`（输入）。
- 通过 `filter.resources.{groupName}.uniforms.{name}` 访问统一变量值。

### 滤镜选项

```ts
import { Filter, GlProgram, Rectangle } from "pixi.js";

const filter = new Filter({
  glProgram: GlProgram.from({ fragment }),
  resources: {},
  resolution: 0.5, // 默认 1. 较低 = 更快，更模糊。'inherit' 匹配渲染目标的分辨率
  padding: 10, // 默认 0. 额外像素用于扩展边界的特效
  antialias: "off", // 默认 'off'。'on' | 'off' | 'inherit'
  blendMode: "normal", // 默认 'normal'
  blendRequired: false, // 默认 false。如果着色器采样 uBackTexture，则为 true
  clipToViewport: true, // 默认 true
});

// 优化：设置已知边界以避免每帧测量
container.filterArea = new Rectangle(0, 0, 800, 600);

// 无需重建滤镜数组即可切换
filter.enabled = false;

// 在许多显示对象之间共享一个滤镜实例
sprite1.filters = [filter];
sprite2.filters = [filter];
```

### 社区滤镜（pixi-filters）

```ts
import { AdjustmentFilter } from "pixi-filters/adjustment";
import { GlowFilter } from "pixi-filters/glow";

sprite.filters = [
  new AdjustmentFilter({ brightness: 1.2, contrast: 1.1 }),
  new GlowFilter({ distance: 15, outerStrength: 2 }),
];
```

对于 v8，社区滤镜使用 `pixi-filters/{name}` 导入，而不是旧的 `@pixi/filter-*` 包。

### 高级混合模式

高级混合模式（`color-burn`、`overlay`、`hard-light` 等）由滤镜系统提供支持，必须在使用前导入。它们还需要 WebGL 上的 `useBackBuffer: true`；请参阅 `pixijs-blend-modes` 技能以获取完整列表。

```ts
import "pixi.js/advanced-blend-modes";

await app.init({ useBackBuffer: true });
sprite.blendMode = "color-burn";
```

高级混合模式基于滤镜，因此它们继承 `Filter.defaultOptions`，其 `resolution` 默认为 `1`。在高 DPI 渲染目标上，这可能导致混合模式看起来被裁剪、缩放或只部分应用。在创建受影响的对象之前设置 `Filter.defaultOptions.resolution = 'inherit'` 以在渲染目标分辨率下渲染，但这会以更高的内存和运行时成本为代价：

```ts
import { Filter } from "pixi.js";
import "pixi.js/advanced-blend-modes";

Filter.defaultOptions.resolution = "inherit";
sprite.blendMode = "overlay";
```

## 常见错误

### [关键] 使用旧的 Filter 构造函数（顶点、片段、统一变量）

错误：

```ts
import { Filter } from "pixi.js";

const filter = new Filter(vertex, fragment, { uTime: 0 });
```

正确：

```ts
import { Filter, GlProgram } from "pixi.js";

const filter = new Filter({
  glProgram: GlProgram.from({ fragment, vertex }),
  resources: {
    timeUniforms: { uTime: { value: 0, type: "f32" } },
  },
});
```

v8 使用选项对象。着色器必须用 `GlProgram.from()` 或 `GpuProgram.from()` 包装。统一变量分组在 `resources` 中，并具有显式类型。纹理是资源，不是统一变量。

### [高] 使用 v8 的 @pixi/filter-\* 包

错误：

```ts
import { AdjustmentFilter } from "@pixi/filter-adjustment";
```

正确：

```ts
import { AdjustmentFilter } from "pixi-filters/adjustment";
```

`@pixi/filter-*` 包仅适用于 v7。对于 v8，社区滤镜包重构为 `pixi-filters/{name}`。

### [高] 未将滤镜容器化而使用过多滤镜

每个滤镜应用都需要帧缓冲区切换、边界测量和渲染到纹理传递。父容器上的一个滤镜比每个子对象上的相同滤镜便宜得多。

错误：

```ts
for (const child of container.children) {
  child.filters = [new BlurFilter({ strength: 4 })];
}
```

正确：

```ts
container.filters = [new BlurFilter({ strength: 4 })];
```

### [高] 在 WebGL 上使用 blendRequired 滤镜而未设置 useBackBuffer

自定义滤镜和大多数高级社区滤镜设置 `blendRequired: true` 会采样后缓冲区。在 WebGL 上，这只有在渲染器使用 `useBackBuffer: true` 初始化时才有效；否则 PixiJS 会记录警告，滤镜会静默回退：

```ts
await app.init({ useBackBuffer: true });
```

WebGPU 无条件启用后缓冲区，因此这仅影响 WebGL。

### [中] 未为已知尺寸的容器设置 filterArea

没有 `filterArea`，PixiJS 每帧通过 `getGlobalBounds()` 测量容器边界，这会递归遍历所有子对象。对于具有已知尺寸的容器，设置 `filterArea` 以避免此成本：

```ts
import { Rectangle } from "pixi.js";

container.filterArea = new Rectangle(0, 0, 800, 600);
container.filters = [someFilter];
```

## API 参考

- [Filter](https://pixijs.download/release/docs/filters.Filter.html.md)
- [AlphaFilter](https://pixijs.download/release/docs/filters.AlphaFilter.html.md)
- [BlurFilter](https://pixijs.download/release/docs/filters.BlurFilter.html.md)
- [BlurFilterPass](https://pixijs.download/release/docs/filters.BlurFilterPass.html.md)
- [ColorMatrixFilter](https://pixijs.download/release/docs/filters.ColorMatrixFilter.html.md)
- [DisplacementFilter](https://pixijs.download/release/docs/filters.DisplacementFilter.html.md)
- [NoiseFilter](https://pixijs.download/release/docs/filters.NoiseFilter.html.md)
- [FilterSystem](https://pixijs.download/release/docs/rendering.FilterSystem.html.md)
