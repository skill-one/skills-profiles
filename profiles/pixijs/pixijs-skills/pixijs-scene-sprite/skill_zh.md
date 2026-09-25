PixiJS 提供三种精灵类用于不同的绘制任务。`Sprite` 是默认的图像绘制节点；`NineSliceSprite` 是可调整大小的 UI 面板变体，可保留角落艺术；`TilingSprite` 在区域中重复纹理。`Sprite` 的子类 `AnimatedSprite` 通过纹理帧循环实现基于帧的动画。

假设熟悉 `pixijs-scene-core-concepts`。所有精灵类都是叶子节点；它们不能有子节点。将多个精灵包裹在 `Container` 中以将它们分组。

## 快速入门

```ts
const texture = await Assets.load("bunny.png");

const sprite = new Sprite({
  texture,
  anchor: 0.5,
  tint: 0xff8888,
});
sprite.x = app.screen.width / 2;
sprite.y = app.screen.height / 2;

app.stage.addChild(sprite);
```

构造后设置位置，因为 `app.screen.width / 2` 取决于实时渲染器的大小。字面位置可以通过 `x`/`y` 直接在选项对象中指定（继承自 `Container`）。

**相关技能：** `pixijs-scene-core-concepts`（叶子节点、变换）、`pixijs-assets`（纹理加载）、`pixijs-scene-particle-container`（成千上万的精灵）、`pixijs-performance`（精灵表、批处理）。

## 变体

| 变体           | 使用场景                                        | 优缺点                                      | 参考                                                        |
| -------------- | ---------------------------------------------- | ------------------------------------------- | ----------------------------------------------------------- |
| `Sprite`       | 在位置绘制单个纹理                              | 固定大小等于纹理大小                        | [references/sprite.md](references/sprite.md)                 |
| `AnimatedSprite` | 从纹理数组或精灵表进行基于帧的动画              | 仅限预渲染帧；无插值                      | [references/animated-sprite.md](references/animated-sprite.md) |
| `NineSliceSprite` | 可调整大小的 UI 面板、按钮、对话框框架          | 边框宽度固定；中心拉伸                      | [references/nineslice-sprite.md](references/nineslice-sprite.md) |
| `TilingSprite`  | 滚动背景、视差、重复图案                        | 单个纹理重复；`tilePosition` 滚动            | [references/tiling-sprite.md](references/tiling-sprite.md)       |

`AnimatedSprite` 是 `Sprite` 的子类；所有 `Sprite` 属性（anchor、tint、position）都适用。

每个变体的构造函数选项在其子参考文件（`references/{variant}.md`）中记录。所有变体也接受 `Container` 选项（`position`、`scale`、`tint`、`label`、`filters`、`zIndex` 等）——参见 `skills/pixijs-scene-core-concepts/references/constructor-options.md`。

## 何时使用什么

- **"我想在位置绘制单个图像"** → `Sprite`。90% 的 2D 游戏和应用程序内容的默认选择。
- **"我想通过一系列帧动画一个角色"** → `AnimatedSprite`。通过 Assets 加载精灵表并传递 `sheet.animations['walk']`。参见 `references/animated-sprite.md`。
- **"我想一个可调整大小的 UI 按钮/面板，不拉伸边框"** → `NineSliceSprite`。设置边框宽度，然后设置 `width`/`height`。参见 `references/nineslice-sprite.md`。
- **"我想一个滚动的重复背景"** → `TilingSprite`。动画 `tilePosition` 以滚动。参见 `references/tiling-sprite.md`。
- **"我想成千上万的相同精灵"** → 使用 `ParticleContainer` 与 `Particle` 实例（参见 `pixijs-scene-particle-container`），而不是普通精灵。
- **"我想绘制形状或路径"** → 使用 `Graphics`（参见 `pixijs-scene-graphics`），而不是精灵。

## 快速概念

### 锚点与枢轴

`Sprite.anchor` 是归一化 `[0, 1]`，仅移动纹理绘制原点；无位置偏移。`Container.pivot` 是像素空间，移动变换原点和视觉位置。为了居中精灵，始终使用 `anchor.set(0.5)`。

### 加载前创建

`Sprite.from(id)` 仅读取 Assets 缓存；它不会获取。始终先 `await Assets.load(...)`，或直接将返回的 `Texture` 传递给 `new Sprite(texture)`。

### 动态纹理

一旦纹理加载完成，修改其 `frame` 或交换其源不会自动通知精灵。设置 `texture.dynamic = true` 一次，或在更改后手动调用 `sprite['onViewUpdate']()`。

## 常见错误

### [高] 使用 `Texture.from(url)` 加载

错误：

```ts
const texture = Texture.from("https://example.com/image.png");
```

正确：

```ts
const texture = await Assets.load("https://example.com/image.png");
```

`Texture.from()` 仅在 v8 中读取缓存；先使用 `Assets.load()`；其返回值是纹理。

### [高] 混淆锚点与枢轴

错误：

```ts
sprite.pivot.set(sprite.width / 2, sprite.height / 2);
```

正确：

```ts
sprite.anchor.set(0.5);
```

`anchor` 仅移动绘制原点。`pivot` 移动变换原点 AND 视觉位置，导致精灵意外移动。

### [高] 旧的 `NineSlicePlane` 名称

`NineSlicePlane` 在 v8 中更名为 `NineSliceSprite`，并切换到选项对象构造函数：`new NineSliceSprite({ texture, leftWidth, topHeight, rightWidth, bottomHeight })`。

### [中] 向精灵添加子节点

`Sprite`、`NineSliceSprite` 和 `TilingSprite` 都设置 `allowChildren = false`。将它们包裹在 `Container` 中以将精灵与其他内容分组。

## API 参考

- [Sprite](https://pixijs.download/release/docs/scene.Sprite.html.md)
- [SpriteOptions](https://pixijs.download/release/docs/scene.SpriteOptions.html.md)
- [AnimatedSprite](https://pixijs.download/release/docs/scene.AnimatedSprite.html.md)
- [NineSliceSprite](https://pixijs.download/release/docs/scene.NineSliceSprite.html.md)
- [TilingSprite](https://pixijs.download/release/docs/scene.TilingSprite.html.md)
- [Texture](https://pixijs.download/release/docs/rendering.Texture.html.md)
