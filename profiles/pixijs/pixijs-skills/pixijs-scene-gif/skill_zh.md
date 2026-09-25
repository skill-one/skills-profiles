`GifSprite` 将动画 GIF 作为显示对象播放。`Assets.load('animation.gif')` 返回的是 `GifSource`（而不是 `Texture`），你需要将这个对象包装在 `GifSprite` 中。这需要执行一个副作用 `import 'pixi.js/gif'` 来注册加载器扩展。

假定你已经熟悉了 `pixijs-scene-core-concepts`。`GifSprite` 继承自 `Sprite`，因此它是一个叶子节点：不要在其内部嵌套子对象。将多个 `GifSprite` 实例包装在 `Container` 中以将它们分组。

## 快速入门

```ts
import "pixi.js/gif";
import { GifSprite } from "pixi.js/gif";

const source = await Assets.load("animation.gif");

const gif = new GifSprite({
  source,
  autoPlay: true,
  loop: true,
  animationSpeed: 1,
});

gif.anchor.set(0.5);
gif.x = app.screen.width / 2;
gif.y = app.screen.height / 2;

app.stage.addChild(gif);
```

> [!NOTE]
> GIF 会将每一帧解码为单独的画布纹理。对于包含许多帧的性能关键型动画，建议使用 `AnimatedSprite` 和精灵表——它使用单个图集纹理，并且在 GPU 上批处理效果更好。

**相关技能：** `pixijs-scene-core-concepts`（场景图基础）、`pixijs-scene-sprite`（基于精灵表的动画 `AnimatedSprite`）、`pixijs-assets`（`Assets.load`、缓存、卸载）、`pixijs-ticker`（帧计时）、`pixijs-performance`（纹理内存）。

## 构造函数选项

`GifSpriteOptions` 扩展自 `Omit<SpriteOptions, 'texture'>`；`texture` 由内部管理（从 `source.textures[0]` 获取，并在每帧之间切换）。所有其他 `Sprite` 选项（`anchor`、`scale`、`tint`、`roundPixels` 等）都是有效的，所有 `Container` 选项（`position`、`scale`、`tint`、`label`、`filters`、`zIndex` 等）也在此处有效——参见 `skills/pixijs-scene-core-concepts/references/constructor-options.md`。

`GifSpriteOptions` 添加的叶子特定选项：

| 选项           | 类型                              | 默认    | 描述                                                                                                                |
| -------------- | --------------------------------- | ------- | ------------------------------------------------------------------------------------------------------------------ |
| `source`       | `GifSource`                       | —       | 必须提供。由 `Assets.load('file.gif')` 返回的解析 GIF 数据。可以在多个 `GifSprite` 实例之间共享。                  |
| `autoPlay`     | `boolean`                         | `true`  | 构造时立即开始播放。如果为 `false`，你必须调用 `gif.play()` 来开始。                                               |
| `loop`         | `boolean`                         | `true`  | 到达最后一帧时重复动画。当 `false` 时，精灵停在最后一帧并触发 `onComplete`。                                     |
| `animationSpeed` | `number`                          | `1`     | GIF 原始帧计时的乘数。`2` 运行为双倍速度；`0.5` 运行为半速。                                                         |
| `autoUpdate`   | `boolean`                         | `true`  | 连接到 `Ticker.shared`。设置为 `false` 以通过 `gif.update(ticker)` 自行驱动更新。                                   |
| `fps`          | `number`                          | `30`    | GIF 未指定每帧延迟时的备用帧率。                                                                                     |
| `onComplete`   | `() => void \| null`              | `null`  | 当非循环动画到达最后一帧时被调用。                                                                                   |
| `onLoop`       | `() => void \| null`              | `null`  | 每次循环动画绕回时被调用。                                                                                           |
| `onFrameChange`| `(frame: number) => void \| null` | `null`  | 每次显示的帧索引变化时被调用。                                                                                       |
| `scaleMode`     | `SCALE_MODE`                      | `'linear'` | 自 8.13.0 起已弃用——通过 `Assets.load(..., { data: { scaleMode } })` 传递 `scaleMode`。                                |

构造函数也接受一个纯 `GifSource` 作为其唯一参数（`new GifSprite(source)`），这相当于使用上述默认值 `new GifSprite({ source })`。

## 核心模式

### 设置和副作用导入

```ts
import "pixi.js/gif";
import { Assets } from "pixi.js";
import { GifSprite } from "pixi.js/gif";

const source = await Assets.load("animation.gif");
const gif = new GifSprite({ source });
```

`pixi.js/gif` 调用 `extensions.add(GifAsset)`，将 `.gif` 注册到资源加载器中。没有它，`Assets.load` 不会识别 GIF 文件。`GifSprite` 和 `GifSource` 是从 `pixi.js/gif` 而不是 `pixi.js` 导出的。

从 `pixi.js/gif` 导出命名导也会触发副作用，因此当你不从这个路径导入任何内容时，只需要一个裸的 `import 'pixi.js/gif'`。

### 播放控制

```ts
const gif = new GifSprite({ source });

gif.play();
gif.stop();

gif.currentFrame = 5;
gif.animationSpeed = 2;
gif.animationSpeed = 0.5;

gif.playing; // 只读
gif.progress; // 0-1 播放位置
gif.totalFrames; // 帧数
gif.duration; // 总持续时间（毫秒）
```

`autoPlay: true`（默认）立即开始播放；`loop: true`（默认）重复。`animationSpeed` 是 GIF 原始帧计时的乘数。`currentFrame` 是从 0 开始的。

### 加载选项

```ts
const source = await Assets.load({
  src: "animation.gif",
  data: {
    fps: 12,
    scaleMode: "nearest",
    resolution: 2,
  },
});

const fromDataUri = await Assets.load("data:image/gif;base64,R0lGODlh...");
```

`data` 中的选项传递给 `GifSource.from`。`fps` 设置未指定计时的 GIF 的备用帧延迟。`scaleMode` 和 `resolution` 控制为每一帧创建的画布纹理。加载器匹配 `.gif` 文件扩展名和 `data:image/gif` URI。

### 回调

```ts
const gif = new GifSprite({
  source,
  loop: false,
  onComplete: () => console.log("animation finished"),
  onLoop: () => console.log("loop completed"),
  onFrameChange: (frame) => console.log("now on frame", frame),
});
```

- `onComplete` 在非循环动画到达最后一帧时触发。
- `onLoop` 每次循环动画绕回时触发。
- `onFrameChange` 每次显示的帧变化时触发。

### 手动更新模式

```ts
const gif = new GifSprite({ source, autoUpdate: false });

app.ticker.add((ticker) => {
  gif.update(ticker);
});
```

`autoUpdate: false` 与 `Ticker.shared` 断开连接。你通过传递任何 `Ticker` 实例调用 `gif.update(ticker)`。当动画应由私有计时器驱动时（例如，一个感知暂停的游戏计时器）时，这很有用。

### 共享源数据和克隆

```ts
const source = await Assets.load("animation.gif");

const gif1 = new GifSprite({ source, autoPlay: true });
const gif2 = new GifSprite({ source, autoPlay: false });

const gif3 = gif1.clone();
gif3.animationSpeed = 0.5;
```

`GifSource` 可以在多个 `GifSprite` 实例之间共享；每个精灵都有独立的播放状态。`clone()` 复制所有播放设置，但创建一个独立的实例。

## 常见错误

### [高] 未导入 pixi.js/gif

错误：

```ts
import { Assets } from "pixi.js";
const gif = await Assets.load("animation.gif");
```

正确：

```ts
import "pixi.js/gif";
import { Assets } from "pixi.js";
const source = await Assets.load("animation.gif");
```

GIF 加载器扩展必须在加载之前注册。如果没有副作用导入，加载器不会识别 `.gif` 文件，加载要么失败，要么返回原始数据。

### [中] 期望 Assets.load 返回 Texture

错误：

```ts
const texture = await Assets.load("animation.gif");
const sprite = new Sprite(texture);
```

正确：

```ts
const source = await Assets.load("animation.gif");
const gif = new GifSprite({ source });
```

对 GIF 的 `Assets.load` 返回一个包含帧纹理和计时数据的 `GifSource`。将源传递给 `GifSprite`；对于单个静止帧，读取 `source.textures[0]`。

### [中] GIF 内存在销毁时未释放

错误：

```ts
gif.destroy();
// GifSource 和帧纹理仍然在内存中
```

正确：

```ts
gif.destroy(true);
// 或
await Assets.unload("animation.gif");
```

GIF 帧作为单独的画布纹理持有解码的像素数据。`gif.destroy()`（或 `destroy(false)`) 销毁精灵但保留 `GifSource` 完好无损。传递 `true` 以销毁源。对于共享源，在最后一个消费者完成时才销毁，或调用 `Assets.unload` 让资源缓存处理。

### [低] 不要在 GifSprite 内部嵌套子对象

`GifSprite` 继承自 `Sprite`，这设置了 `allowChildren = false`。它是一个叶子节点。要将 GIF 与其他显示对象分组，将它们全部包装在普通的 `Container` 中：

```ts
const group = new Container();
group.addChild(gif, label);
```

## API 参考

- [GifSprite](https://pixijs.download/release/docs/gif.GifSprite.html.md)
- [GifSpriteOptions](https://pixijs.download/release/docs/gif.GifSpriteOptions.html.md)
- [GifSource](https://pixijs.download/release/docs/gif.GifSource.html.md)
- [GifAsset](https://pixijs.download/release/docs/gif.GifAsset.html.md)
- [GifBufferOptions](https://pixijs.download/release/docs/gif.GifBufferOptions.html.md)
- [GifFrame](https://pixijs.download/release/docs/gif.GifFrame.html.md)
