这项技能是一个用于将 v7 代码库升级到 v8 的破坏性变更清单。按类别自上而下进行工作；清单将每个 v7 模式映射到其 v8 替代方案。

## 快速入门

安装单个包，然后按此顺序移植：导入 → 应用程序初始化 → 图形 → 文本 → 事件 → 着色器/滤镜 → 清理。

```ts
const app = new Application();
await app.init({ width: 800, height: 600 });
document.body.appendChild(app.canvas);

const g = new Graphics()
  .rect(0, 0, 100, 100)
  .fill({ color: 0xff0000 })
  .stroke({ width: 2, color: 0x000000 });
app.stage.addChild(g);
```

**相关技能：** `pixijs-application`（异步初始化）、`pixijs-scene-graphics`（新的填充/描边 API）、`pixijs-custom-rendering`（着色器重写）、`pixijs-scene-text`（文本构造函数变更）、`pixijs-performance`（销毁模式）。

## 迁移清单：v7 到 v8

逐个类别进行工作。每个项目都显示了预期的 v8 模式和必须替换的 v7 模式。

### 初始化

**Async app.init()** -- 预期：

```ts
const app = new Application();
await app.init({ width: 800, height: 600 });
document.body.appendChild(app.canvas);
```

失败：向 `new Application({...})` 传递选项并同步使用。

**app.canvas 替换 app.view** -- `app.view` 会发出弃用警告。

**Application 类型参数** -- 预期：`new Application<Renderer<HTMLCanvasElement>>()`。失败：`new Application<HTMLCanvasElement>()`。

### 导入

**单个包** -- 预期：

```ts
import { Sprite, Application, Assets, Graphics } from "pixi.js";
```

失败：从任何弃用的 v7 核心 `@pixi/*` 子包中导入（见下列表）。补充包如 `@pixi/sound` 仍然有效，应继续使用。

弃用的 `@pixi/*` 包（任何版本都不要使用）：
`@pixi/accessibility`, `@pixi/app`, `@pixi/assets`, `@pixi/compressed-textures`, `@pixi/core`, `@pixi/display`, `@pixi/events`, `@pixi/extensions`, `@pixi/extract`, `@pixi/filter-alpha`, `@pixi/filter-blur`, `@pixi/filter-color-matrix`, `@pixi/filter-displacement`, `@pixi/filter-fxaa`, `@pixi/filter-noise`, `@pixi/graphics`, `@pixi/mesh`, `@pixi/mesh-extras`, `@pixi/mixin-cache-as-bitmap`, `@pixi/mixin-get-child-by-name`, `@pixi/mixin-get-global-position`, `@pixi/particle-container`, `@pixi/prepare`, `@pixi/sprite`, `@pixi/sprite-animated`, `@pixi/sprite-tiling`, `@pixi/spritesheet`, `@pixi/text`, `@pixi/text-bitmap`, `@pixi/text-html`。

**自定义构建** -- 设置 `skipExtensionImports: true` 并仅导入需要的扩展：

```ts
import "pixi.js/graphics";
import "pixi.js/text";
import "pixi.js/events";
import { Application } from "pixi.js";
await app.init({ skipExtensionImports: true });
```

注意：`manageImports: false` 仍然接受，但自 8.1.6 起已弃用；优先使用 `skipExtensionImports: true`。

**未自动导入的扩展**（即使默认自动导入启用也需要显式导入）：
`pixi.js/advanced-blend-modes`, `pixi.js/unsafe-eval`, `pixi.js/prepare`, `pixi.js/math-extras`, `pixi.js/dds`, `pixi.js/ktx`, `pixi.js/ktx2`, `pixi.js/basis`。

**社区滤镜** -- 预期：`import { AdjustmentFilter } from 'pixi-filters/adjustment'`。失败：`@pixi/filter-adjustment`。

### 图形 API

**先绘制形状后填充** -- 预期：

```ts
const g = new Graphics().rect(50, 50, 100, 100).fill(0xff0000);
```

失败：`beginFill(0xff0000).drawRect(50, 50, 100, 100).endFill()`。

**重命名的形状方法：**

| v7                   | v8            |
| -------------------- | ------------- |
| `drawRect`           | `rect`        |
| `drawCircle`         | `circle`      |
| `drawEllipse`        | `ellipse`     |
| `drawPolygon`        | `poly`        |
| `drawRoundedRect`    | `roundRect`   |
| `drawStar`           | `star`        |
| `drawRegularPolygon` | `regularPoly` |
| `drawRoundedPolygon` | `roundPoly`   |
| `drawRoundedShape`   | `roundShape`  |
| `drawChamferRect`    | `chamferRect` |
| `drawFilletRect`     | `filletRect`  |

**填充替换 beginFill/beginTextureFill** -- 预期：

```ts
graphics
  .rect(0, 0, 100, 100)
  .fill({ texture: Texture.WHITE, alpha: 0.5, color: 0xff0000 });
```

失败：`beginFill(color, alpha)` 或 `beginTextureFill({ texture, alpha, color })`。

**描边替换 lineStyle** -- 预期：

```ts
graphics.rect(0, 0, 100, 100).fill("blue").stroke({ width: 2, color: "white" });
```

失败：`lineStyle(2, 'white')` 或 `lineTextureStyle({ texture, width, color })`。

**孔洞使用 cut()** -- 预期：

```ts
graphics.rect(0, 0, 100, 100).fill(0x00ff00).circle(50, 50, 20).cut();
```

失败：`beginHole()` / `endHole()`。

**GraphicsContext 替换 GraphicsGeometry** -- 预期：

```ts
const context = new GraphicsContext().rect(0, 0, 100, 100).fill(0xff0000);
const g1 = new Graphics(context);
const g2 = new Graphics(context);
```

失败：`new Graphics(graphics.geometry)`。

### 文本

**选项对象构造函数** -- 预期：

```ts
const text = new Text({ text: "Hello", style: { fontSize: 24 } });
const bmp = new BitmapText({ text: "Hello", style: { fontFamily: "MyFont" } });
const html = new HTMLText({ text: "<b>Hello</b>", style: { fontSize: 24 } });
```

失败：`new Text('Hello', { fontSize: 24 })`（位置参数）。

**位图字体加载** -- 必须在 `Assets.load('font.fnt')` 之前 `import 'pixi.js/text-bitmap'`。

### 图标 / 网格

**Texture.from 不再加载 URL** -- 必须先调用 `await Assets.load('image.png')`，然后 `Texture.from('image.png')`。

**NineSliceSprite 替换 NineSlicePlane** -- 预期：

```ts
const ns = new NineSliceSprite({
  texture,
  leftWidth: 10,
  topHeight: 10,
  rightWidth: 10,
  bottomHeight: 10,
});
```

**网格重命名：** `SimpleMesh` -> `MeshSimple`，`SimplePlane` -> `MeshPlane`，`SimpleRope` -> `MeshRope`。所有都使用选项对象。

**网格几何体选项** -- 预期：

```ts
const geom = new MeshGeometry({
  positions: vertices,
  uvs,
  indices,
  topology: "triangle-list",
});
```

失败：`new MeshGeometry(vertices, uvs, indices)`。

**ParticleContainer 使用 Particle** -- 预期：

```ts
const container = new ParticleContainer({
  boundsArea: new Rectangle(0, 0, 800, 600),
});
const particle = new Particle(texture);
container.addParticle(particle);
```

失败：`container.addChild(new Sprite(texture))`。

### 事件

**eventMode 替换 interactive** -- 预期：

```ts
sprite.eventMode = "static";
sprite.cursor = "pointer";
sprite.on("pointertap", () => {
  /* handle */
});
```

遗留：`sprite.interactive = true;`（仍然作为 `eventMode = 'static'` 的别名工作），但优先使用显式形式。

默认 `eventMode` 是 `'passive'`（无事件）。必须显式设置为 `'static'` 或 `'dynamic'`。

**Ticker 回调** -- 预期：

```ts
app.ticker.add((ticker) => {
  bunny.rotation += ticker.deltaTime;
});
```

损坏：`app.ticker.add((dt) => { bunny.rotation += dt; })` -- 编译但 `dt` 是 `Ticker` 对象，不是数字。强制转换为 `NaN`，静默损坏旋转。

**updateTransform 已移除** -- 在构造函数中使用 `this.onRender = this._onRender.bind(this)` 代替。

### 着色器

**Shader.from 使用选项** -- 预期：

```ts
const shader = Shader.from({
  gl: { vertex: vertexSrc, fragment: fragmentSrc },
  resources: {
    myUniforms: new UniformGroup({ uTime: { value: 0, type: "f32" } }),
  },
});
```

失败：`Shader.from(vertex, fragment, uniforms)`。

**Filter 构造函数** -- 预期：

```ts
const filter = new Filter({
  glProgram: GlProgram.from({ fragment, vertex }),
  resources: { filterUniforms: { uTime: { value: 0, type: "f32" } } },
});
```

失败：`new Filter(vertex, fragment, { uTime: 0 })`。

**Uniforms 需要类型** -- `new UniformGroup({ uTime: { value: 1, type: 'f32' } })`。失败：`new UniformGroup({ uTime: 1 })`。

**纹理是资源，不是 uniform** -- 作为顶级资源条目传递（`texture.source`，`texture.style`），而不是在 UniformGroup 内部。

### 纹理

**Sprite 不再自动检测纹理 UV 变化** -- 如果在创建后修改了纹理的帧，请调用 `texture.update()` 以重新计算 UV，然后调用 `sprite.onViewUpdate()` 以刷新 sprite。这两个调用按此顺序都需要。更新源数据（例如视频纹理）仍然是自动的。

```ts
texture.frame.width = texture.frame.width / 2;
texture.update(); // 首先重新计算纹理 UV
sprite.onViewUpdate(); // 然后刷新 sprite 的显示
```

**Mipmaps** -- `BaseTexture.mipmap` 重命名为 `autoGenerateMipmaps`。对于 RenderTextures，您必须手动更新 mipmap：

```ts
const rt = RenderTexture.create({
  width: 100,
  height: 100,
  autoGenerateMipmaps: true,
});
renderer.render({ target: rt, container: scene });
rt.source.updateMipmaps();
```

### 适配器

**DOMAdapter 替换 settings.ADAPTER** -- 预期：

```ts
import { DOMAdapter, WebWorkerAdapter } from "pixi.js";
DOMAdapter.set(WebWorkerAdapter);
DOMAdapter.get().createCanvas();
```

失败：`settings.ADAPTER = WebWorkerAdapter; settings.ADAPTER.createCanvas();`。

内置适配器：`BrowserAdapter`（默认），`WebWorkerAdapter`（用于 Web Workers）。

### 其他

**DisplayObject 已移除** -- `Container` 是基类。`class MyObj extends DisplayObject` 失败。

**叶节点不能有子节点** -- `Sprite`，`Graphics`，`Mesh`，`Text` 是叶节点。用 `Container` 包裹。

**重命名的属性**（旧名称仍然作为弃用别名存在并带警告）：

- `container.name` -> `container.label`
- `container.cacheAsBitmap = true` -> `container.cacheAsTexture(true)`

**getBounds() 返回类型已更改：** `getBounds()` 现在返回一个 `Bounds` 对象，而不是 `Rectangle`。`Bounds` 有 `.x`，`.y`，`.width`，`.height` 获取器，因此基本用法正常。当您需要 `Rectangle` 实例时（例如，用于 `.contains()`），使用 `.rectangle`。

**settings 对象已移除** -- 使用 `AbstractRenderer.defaultOptions.resolution = 1` 和 `DOMAdapter.set(BrowserAdapter)`。

**utils 命名空间已移除** -- 使用 `import { isMobile } from 'pixi.js'` 而不是 `utils.isMobile`。

**文本解析器重命名：**

- `TextFormat` -> `bitmapFontTextParser`
- `XMLStringFormat` -> `bitmapFontXMLStringParser`
- `XMLFormat` -> `bitmapFontXMLParser`

**Assets.add** -- `Assets.add({ alias: 'bunny', src: 'bunny.png' })`。失败：`Assets.add('bunny', 'bunny.png')`。

**枚举常量被字符串替换：**

| v7                           | v8                 |
| ---------------------------- | ------------------ |
| `SCALE_MODES.NEAREST`        | `'nearest'`        |
| `SCALE_MODES.LINEAR`         | `'linear'`         |
| `WRAP_MODES.CLAMP`           | `'clamp-to-edge'`  |
| `WRAP_MODES.REPEAT`          | `'repeat'`         |
| `WRAP_MODES.MIRRORED_REPEAT` | `'mirror-repeat'`  |
| `DRAW_MODES.TRIANGLES`       | `'triangle-list'`  |
| `DRAW_MODES.TRIANGLE_STRIP`  | `'triangle-strip'` |
| `DRAW_MODES.LINES`           | `'line-list'`      |
| `DRAW_MODES.LINE_STRIP`      | `'line-strip'`     |
| `DRAW_MODES.POINTS`          | `'point-list'`     |

**剔除是手动操作** -- 设置 `cullable = true`，然后在渲染前调用 `Culler.shared.cull(container, viewRect)`。或者通过 `extensions.add(CullerPlugin)` 添加 `CullerPlugin`。

## 迁移前总结

- [ ] 依赖中没有弃用的 v7 核心 `@pixi/*` 包（补充包如 `@pixi/sound` 可以）
- [ ] 所有核心 `@pixi/*` 导入转换为 `pixi.js`
- [ ] 所有 `new Application({...})` 转换为 `await app.init({...})`
- [ ] 所有图形代码使用先绘制形状后填充模式
- [ ] 所有构造函数使用选项对象（文本、网格、NineSliceSprite 等）
- [ ] Shader/Filter 代码使用 `{gl, resources}` 模式并带有类型化的 uniform
- [ ] ParticleContainer 代码使用 `Particle`，而不是 `Sprite`
- [ ] Ticker 回调访问 `ticker.deltaTime`，而不是将第一个参数作为 delta
- [ ] 事件处理使用 `eventMode` 而不是 `interactive`
- [ ] `settings` 和 `utils` 引用已移除
- [ ] `DisplayObject` 引用替换为 `Container`
- [ ] 纹理 UV 修改调用 `sprite.onViewUpdate()` 以确保需要
- [ ] RenderTexture mipmap 代码手动调用 `source.updateMipmaps()` 
- [ ] `settings.ADAPTER` 替换为 `DOMAdapter.set()`

## 常见错误

### [CRITICAL] 从弃用的 v7 核心 @pixi/\* 子包中导入

错误：

```ts
import { Sprite } from "@pixi/sprite";
import { Application } from "@pixi/app";
```

正确：

```ts
import { Sprite, Application } from "pixi.js";
```

v8 使用单个 `pixi.js` 包。v7 核心 `@pixi/*` 子包已弃用，不得使用（见导入部分中的完整列表）。补充包如 `@pixi/sound` 仍然有效。

### [CRITICAL] 使用 DisplayObject 作为基类

错误：`class MyObject extends DisplayObject { ... }`
正确：`class MyObject extends Container { ... }`

`DisplayObject` 在 v8 中已移除。`Container` 是所有显示对象的基类。

### [HIGH] 使用旧的 SCALE_MODES/WRAP_MODES/DRAW_MODES 枚举

错误：`texture.source.scaleMode = SCALE_MODES.NEAREST;`
正确：`texture.source.scaleMode = 'nearest';`

v8 使用字符串值。旧枚举可能作为弃用别名工作，但应替换。

### [HIGH] 使用 `interactive = true` 而不是 `eventMode`

遗留：`sprite.interactive = true;`（仍然作为 `eventMode = 'static'` 的别名工作）
推荐：`sprite.eventMode = 'static';`

默认 `eventMode` 是 `'passive'`（无事件）。必须显式设置为 `'static'`（可点击，无 tick 检查）或 `'dynamic'`（可点击并带有 tick 检查）。`interactive = true` 仍然工作而无需弃用警告，但 `eventMode` 是 v8 的规范 API。

### [HIGH] 使用 utils 命名空间

错误：`import { utils } from 'pixi.js'; utils.isMobile.any();`
正确：`import { isMobile } from 'pixi.js'; isMobile.any();`

`utils` 命名空间已移除。所有工具函数都是直接导入。

### [HIGH] 期望纹理 UV 变化自动更新 sprite

错误：修改 `texture.frame` 并假设 sprite 自动更新。
正确：在修改纹理 UV 后调用 `sprite.onViewUpdate()`。

Sprites 不再订阅纹理 UV 变更事件以优化性能。源数据更新（例如视频）仍然自动反映。
