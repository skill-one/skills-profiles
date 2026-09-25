优化前的配置文件。PixiJS 可以很好地处理许多内容，开箱即用；浏览器开发者工具中的性能分析 + GPU 分析应作为首选。找到瓶颈后，应用以下目标模式（销毁、池化、批处理、缓存或剔除）。

## 快速入门

```ts
container.cacheAsTexture(true);
container.updateCacheTexture();
container.cacheAsTexture(false);
container.destroy({ children: true });

import { CullerPlugin, extensions } from "pixi.js";
extensions.add(CullerPlugin);

offscreenContainer.cullable = true;
offscreenContainer.cullArea = new Rectangle(0, 0, 256, 256);

// 通过初始化选项调整 GC（毫秒）。自 8.15.0 起，`textureGC.*` 属性已弃用 — 应在应用程序初始化时使用这些选项。
await app.init({ gcMaxUnusedTime: 60_000, gcFrequency: 30_000 });
```

**相关技能：** `pixijs-scene-container`（销毁选项）、`pixijs-scene-core-concepts`（渲染组、图层、剔除）、`pixijs-scene-text`（动态内容 BitmapText）、`pixijs-assets`（纹理图集）、`pixijs-custom-rendering`（自定义批处理器）。

## 核心模式

### 正确的销毁与清理

```ts
import { Sprite, Assets } from "pixi.js";

const texture = await Assets.load("character.png");
const sprite = new Sprite(texture);

// 仅销毁 sprite（保留纹理以供重用）
sprite.destroy();

// 销毁 sprite 及其纹理
sprite.destroy({ children: true, texture: true, textureSource: true });
```

完成加载的资产后：

```ts
Assets.unload("character.png");
```

这将将其从缓存中移除并卸载 GPU 资源。

为自定义渲染构建的对象以相同的方式清理：调用您创建的 `geometry.destroy()` 和 `renderTarget.destroy()`。销毁容器也会销毁其渲染组的缓存批处理器。

### 应用程序销毁/重建周期

```ts
import { Application } from "pixi.js";

// 正确的销毁方式，清理全局池
app.destroy({ releaseGlobalResources: true });

const newApp = new Application();
await newApp.init({ width: 800, height: 600 });
```

没有 `releaseGlobalResources: true`，旧应用程序的池化对象（批处理器、纹理）会泄漏到新应用程序中，导致闪烁和损坏。

### 纹理垃圾回收

PixiJS 通过 `GCSystem` 自动收集未使用的纹理和 GPU 资源（包括 WebGPU 绑定组）。默认设置：每 30 秒检查一次，移除闲置 60 秒的资源。这些基于时间（毫秒）。

```ts
import { Application } from "pixi.js";

const app = new Application();

await app.init({
  gcActive: true,
  gcMaxUnusedTime: 120000, // 清理前的闲置时间（毫秒）（默认：60000）
  gcFrequency: 60000, // 检查间隔（毫秒）（默认：30000）
});
```

手动控制：

```ts
texture.source.unload(); // 立即释放 GPU 内存
```

### PrepareSystem 用于 GPU 上传

在渲染之前上传纹理和图形到 GPU，以避免第一帧卡顿：

```ts
import "pixi.js/prepare";
import { Application, Assets } from "pixi.js";

const app = new Application();
await app.init();

// 资产上传前不渲染
app.stop();

const texture = await Assets.load("large-scene.png");

// 提前上传到 GPU
await app.renderer.prepare.upload(app.stage);

// 现在渲染不会在第一帧卡顿
app.start();
```

`prepare.upload()` 接受一个容器（上传子树中的所有纹理、文本和图形）或单个资源。

### cacheAsTexture 以提升性能

`cacheAsTexture()` 将容器的子树渲染到单个纹理中，减少复杂静态内容的绘制调用。它内部创建一个渲染组并缓存结果。

**使用场景：**

- 许多静态子项（UI 面板、装饰性背景、复杂 Graphics）
- 具有昂贵滤镜的容器（缓存滤镜结果）
- 大型子树且很少变化

**权衡：**

- 使用 GPU 内存缓存纹理（容器越大，内存消耗越多）
- 最大纹理大小取决于 GPU（通常为 4096x4096 或更大）。没有 PixiJS 属性可以暴露它，因此直接查询后端：
- 修改子项后必须调用 `updateCacheTexture()`
- 与遮罩结合使用时可能不稳定（请参阅遮罩技能）

```ts
import type { WebGLRenderer, WebGPURenderer } from "pixi.js";

// 在两个后端初始化 renderer/app 后可用
const maxTextureSize = renderer.name === "webgpu"
  ? (renderer as WebGPURenderer).gpu.device.limits.maxTextureDimension2D
  : (renderer as WebGLRenderer).gl.getParameter(WebGL2RenderingContext.MAX_TEXTURE_SIZE);
```

```ts
import { Container, Sprite } from "pixi.js";

const panel = new Container();
// ... 添加许多静态子项 ...

panel.cacheAsTexture(true);

// 带选项
panel.cacheAsTexture({ resolution: 2, antialias: true });

// 修改后刷新
panel.updateCacheTexture();

// 销毁前必须禁用（见常见错误）
panel.cacheAsTexture(false);
panel.destroy();
```

**避免：** 反复切换开/关（持续缓存抵消了优势）、缓存稀疏容器（收益微乎其微）、缓存超过 4096x4096 的容器。

### 对象回收

通过更改属性而不是销毁/重建来重用对象：

```ts
import { Sprite, Container, Texture } from "pixi.js";

class BulletPool {
  private _pool: Sprite[] = [];
  private _container: Container;

  constructor(container: Container) {
    this._container = container;
  }

  public get(texture: Texture): Sprite {
    let bullet = this._pool.pop();

    if (!bullet) {
      bullet = new Sprite(texture);
      this._container.addChild(bullet);
    }

    bullet.texture = texture;
    bullet.position.set(0, 0);
    bullet.rotation = 0;
    bullet.scale.set(1);
    bullet.alpha = 1;
    bullet.tint = 0xffffff;
    bullet.blendMode = "normal";
    bullet.visible = true;
    return bullet;
  }

  public release(bullet: Sprite): void {
    bullet.visible = false;
    this._pool.push(bullet);
  }
}
```

销毁和重建的成本远高于切换 `visible` 和更新属性。GPU 资源保持分配；仅更改场景图可见性。

### 批处理优化

PixiJS 将连续的相似对象批处理到单个绘制调用中。批处理断点发生在：

- 对象类型更改（Sprite 与 Graphics）
- 纹理源更改（超出每批纹理限制，通常为 16）
- 混合模式更改
- 拓扑更改

优化绘制顺序：

```ts
import { Sprite, Graphics, Container } from "pixi.js";

// 4 个绘制调用：类型交替
const bad = new Container();
bad.addChild(new Sprite(t1));
bad.addChild(new Graphics().rect(0, 0, 10, 10).fill(0xff0000));
bad.addChild(new Sprite(t2));
bad.addChild(new Graphics().rect(0, 0, 10, 10).fill(0x00ff00));

// 2 个绘制调用：类型分组
const good = new Container();
good.addChild(new Sprite(t1));
good.addChild(new Sprite(t2));
good.addChild(new Graphics().rect(0, 0, 10, 10).fill(0xff0000));
good.addChild(new Graphics().rect(0, 0, 10, 10).fill(0x00ff00));
```

混合模式也适用：`screen/normal/screen/normal` = 4 绘制；`screen/screen/normal/normal` = 2 绘制。

### 使用 Spritesheet 而不是单个纹理

```ts
import { Assets, Sprite } from "pixi.js";

// 加载一个 Spritesheet（单个纹理图集）
const sheet = await Assets.load("game-atlas.json");

// 所有帧共享一个 GPU 纹理；启用批处理
const hero = new Sprite(sheet.textures["hero.png"]);
const enemy = new Sprite(sheet.textures["enemy.png"]);
const coin = new Sprite(sheet.textures["coin.png"]);
```

单个纹理每个都需要其自己的 GPU 上传，当纹理限制超出时会破坏批处理。Spritesheet 将多个帧合并到一个图集纹理中。

在半分辨率图集的文件名后使用 `@0.5x` 后缀，以便 PixiJS 自动缩放它们。

### 文本性能

文本和 HTMLText 在每次更改时都会重新渲染到画布并上传到 GPU。切勿无条件地每帧更新它们：

```ts
import { BitmapText, Text } from "pixi.js";

// 错误：每帧重新渲染画布 + GPU 上传
app.ticker.add(() => {
  scoreText.text = `Score: ${score}`;
});

// 正确：使用 BitmapText 处理频繁变化的文本
const scoreText = new BitmapText({
  text: "Score: 0",
  style: { fontFamily: "Arial", fontSize: 24, fill: 0xffffff },
});

app.ticker.add(() => {
  scoreText.text = `Score: ${score}`;
});
```

BitmapText 从预生成的字形图集中渲染。更新仅重新定位四边形；无需重新渲染画布或上传到 GPU。适用于分数、计时器、计数器等频繁变化的文本。

如果必须使用画布 Text，请保护更新，以便仅在值变化时发生：

```ts
app.ticker.add(() => {
  const next = `Score: ${score}`;
  if (scoreText.text !== next) {
    scoreText.text = next;
  }
});
```

文本分辨率默认与渲染器分辨率匹配。在具有高 DPI 显示器的情况下，可以通过 `text.resolution = 1` 独立降低分辨率以减少 GPU 内存使用。

### Graphics 性能

当 Graphics 对象的形状不变化时（变换、alpha 和 tint 可以正常使用）速度最快。小 Graphics（少于 ~100 个点）像 Sprite 一样进行批处理。具有数百个形状的复杂 Graphics 慢；将它们转换为纹理：

```ts
import { Graphics, Sprite } from "pixi.js";

const complex = new Graphics();
// ... 绘制复杂形状 ...

// 一次渲染到纹理，用作 Sprite
const texture = app.renderer.generateTexture(complex);
const sprite = new Sprite(texture);
```

### 剔除

当 `cullable` 设置为 true 时，PixiJS 会跳过渲染不可见区域的对象。默认情况下禁用，因为它用 CPU 成本（边界检查）换取 GPU 节省。剔除仅在注册 `CullerPlugin` 时运行：

```ts
import { extensions, CullerPlugin, Culler, Rectangle } from "pixi.js";

extensions.add(CullerPlugin); // 在 Application.init 之前

// 启用可能离屏的对象
sprite.cullable = true;

// 可选：预计算的剔除矩形可避免每帧边界计算。
// 没有 cullArea 时，Culler 使用对象的全球边界。
sprite.cullArea = new Rectangle(0, 0, 800, 600);

// 跳过整个子树的剔除（静态 UI，始终可见）
uiRoot.cullableChildren = false;

// 或者不使用插件手动剔除：
Culler.shared.cull(app.stage, app.renderer.screen);
```

容器的 `cullableChildren` 停止剔除器递归到其子项；对具有许多子项的静态 UI 面板来说这是一个巨大的优势。`Culler.shared.cull(container, rect)` 对自定义渲染管线运行相同的逻辑。在 GPU 受限时使用剔除；在 CPU 受限时避免使用，因为每对象的边界检查会增加开销。

### 分辨率和抗锯齿权衡

```ts
import { Application } from "pixi.js";

const app = new Application();

// 适合移动设备：降低分辨率，无抗锯齿
await app.init({
  resolution: 1,
  antialias: false,
  backgroundAlpha: 1, // 不透明背景更快
});
```

`resolution: 2` 四倍像素数量。在移动设备上，这可能导致帧率减半。通过分析找到合适的平衡。

### 低级渲染优化

```ts
import { RenderTexture } from "pixi.js";

// 单次通过抗锯齿渲染纹理：在通过结束时丢弃 MSAA 缓冲区
const rt = RenderTexture.create({ width: 1024, height: 1024, antialias: true, transient: true });

// 上传大型缓冲区更改的字节范围（WebGL 也适用）
buffer.update(changedBytes, offsetBytes);
```

`transient: true`（仅 WebGPU）告诉 GPU 多样本缓冲区是临时内存：它被丢弃而不是写回，并且当 `renderer.device.extensions.transientAttachment` 为 true 时，基于瓦片的 GPU 会跳过分配。仅在单次通过渲染的纹理上使用，且永远不会以 `clear: false` 或作为滤镜包装使用。对于 WebGPU 上的静态自定义绘制序列，记录一次渲染包并在每帧重播；请参阅 `pixijs-custom-rendering` 技能。

### 分批销毁纹理

```ts
function staggerDestroy(textures: Texture[], perFrame: number = 5): void {
  let index = 0;
  const ticker = app.ticker;

  const destroy = () => {
    const end = Math.min(index + perFrame, textures.length);

    for (let i = index; i < end; i++) {
      textures[i].destroy(true);
    }
    index = end;

    if (index >= textures.length) {
      ticker.remove(destroy);
    }
  };

  ticker.add(destroy);
}
```

在单帧销毁许多纹理会导致冻结。将成本分摊到多帧。

### 滤镜和遮罩成本

- 当您知道边界时，设置 `container.filterArea = new Rectangle(x, y, w, h)`。没有它，PixiJS 每帧测量边界。
- 释放滤镜内存：`container.filters = null`。
- 全屏滤镜纹理在屏幕尺寸下池化，但填充（`BlurFilter` 默认）将请求推过屏幕并提升到下一个 2 的幂。在全屏模糊上设置 `repeatEdgePixels: true` 以保持它们为屏幕尺寸。
- 遮罩成本（从最便宜到最贵）：轴对齐矩形遮罩（剪切矩形） < Graphics 遮罩（模板缓冲区） < Sprite/alpha 遮罩（滤镜管道）。无论类型如何，数百个遮罩都会减慢速度；当边界轴对齐时，请优先使用矩形遮罩。
- 在没有交互子项的容器上设置 `interactiveChildren = false`。
- 在大型容器上设置 `hitArea` 以跳过递归子项命中测试。

### 安全的销毁顺序

在销毁前从场景中移除：

```ts
parent.removeChild(sprite);
sprite.destroy();
```

在渲染管线仍然持有引用时销毁会导致空指针崩溃。如果销毁必须在帧中发生，请延迟它：

```ts
app.ticker.addOnce(() => {
  parent.removeChild(sprite);
  sprite.destroy();
});
```

## 常见错误

### [关键] 应用程序销毁而不释放全局资源

错误：

```ts
app.destroy();
const newApp = new Application();
```

正确：

```ts
app.destroy({ releaseGlobalResources: true });
const newApp = new Application();
```

没有这个标志，旧应用程序的池化批处理器和纹理会持续存在于全局池中，并由新应用程序重用，导致闪烁和视觉损坏。

### [高] 场景图中交错对象类型

`sprite / graphic / sprite / graphic` = 4 绘制调用。
`sprite / sprite / graphic / graphic` = 2 绘制调用。

在子项顺序中将相同类型的对象组合在一起，以最小化批处理断点。这同样适用于混合模式排序。

### [高] 销毁和重建对象而不是回收

销毁/重建很昂贵：它释放 GPU 资源，触发垃圾回收，并需要新的 GPU 上传。通过更新 `texture`、`position`、`visible` 和其他属性来重用对象。对于频繁生成/销毁的实体，使用对象池模式。

### [高] 加载许多单个纹理而不是 Spritesheet

每个单独的纹理占用自己的 GPU 内存槽，当每批纹理限制超出时会破坏批处理。Spritesheet 将纹理合并到图集中。还避免超过 4096px 的纹理（在任一轴上），因为它们在某些移动 GPU 上会失败。

### [高] 每帧更新 Text 或 HTMLText

每次更新都会将整个字符串重新渲染到画布并上传到 GPU。在 60fps 下，这会产生巨大的开销。使用 BitmapText 处理动态内容（分数、计时器、计数器）。如果需要画布 Text，则仅在值实际变化时更新。来源：src/**docs**/concepts/performance-tips.md

### [高] 使用复杂 Graphics 而不是纹理

具有数百个复杂 Graphics 对象的渲染速度很慢。小 Graphics（少于 ~100 个点）像 Sprite 一样高效地批处理，但复杂的 Graphics 不行。使用 `renderer.generateTexture()` 将复杂静态形状渲染为纹理，然后作为 Sprite 显示。来源：src/**docs**/concepts/performance-tips.md

### [中] 不分批销毁大量纹理

在单帧销毁几十个纹理会导致可见冻结。将销毁分摊到多帧（例如，每帧 5 个通过 ticker 回调）。来源：src/**docs**/concepts/garbage-collection.md

### [中] 不使用 PrepareSystem 处理大型场景

没有 `renderer.prepare.upload()`，纹理在第一次渲染时上传到 GPU，导致帧卡顿。对于加载屏幕或场景过渡，在显示前上传。需要 `import 'pixi.js/prepare'`（即使默认包中也不包含；始终显式导入）。来源：src/prepare/PrepareSystem.ts

### [中] 未分析就使用高分辨率或抗锯齿

`resolution: 2` 四倍像素数量。`antialias: true` 增加 GPU 成本。两者都会降低移动设备的性能。在目标硬件上启用前始终进行性能分析。来源：performance-tips.md

## API 参考

- [GCSystem](https://pixijs.download/release/docs/rendering.GCSystem.html.md)
- [TextureGCSystem](https://pixijs.download/release/docs/rendering.TextureGCSystem.html.md)
- [RenderableGCSystem](https://pixijs.download/release/docs/rendering.RenderableGCSystem.html.md)
- [PrepareSystem](https://pixijs.download/release/docs/rendering.PrepareSystem.html.md)
- [Culler](https://pixijs.download/release/docs/scene.Culler.html.md)
- [CullerPlugin](https://pixijs.download/release/docs/app.CullerPlugin.html.md)
- [Pool](https://pixijs.download/release/docs/utils.Pool.html.md)
