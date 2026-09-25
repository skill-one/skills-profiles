`Assets` API 是 PixiJS 的单一实例资源加载器、解析器和缓存。使用它来加载纹理、视频、精灵表、字体、JSON 以及其他资源，支持格式检测、分辨率切换、资源捆绑、进度跟踪和 GPU 清理。

## 快速入门

```ts
await Assets.init({ basePath: "/static/" });

const texture = await Assets.load("bunny.png");
const sprite = new Sprite(texture);
app.stage.addChild(sprite);

const [hero, enemy] = await Assets.load(["hero.png", "enemy.png"]);

await Assets.load({
  alias: "logo",
  src: "logo.webp",
});

const logo = new Sprite(Assets.get("logo"));
```

`Assets.init()` 是可选的，但推荐用于设置 `basePath`、`texturePreference` 或清单。初始化后，使用 URL、别名、数组或 `UnresolvedAsset` 调用 `Assets.load()`；解析的资源将被缓存，并由 `Assets.get()` 重新解析。

## 支持的文件类型

| 类型                | 扩展名                                                       | 解析器 ID                     | 加载器                                                                                                                          |
| ------------------- | ---------------------------------------------------------------- | ----------------------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| 纹理                | `.png`, `.jpg`, `.jpeg`, `.webp`, `.avif`                        | `texture`                     | `loadTextures`                                                                                                                  |
| SVG                 | `.svg`                                                           | `svg`                         | `loadSvg` (参见 `references/svg.md`)                                                                                             |
| 视频纹理            | `.mp4`, `.m4v`, `.webm`, `.ogg`, `.ogv`, `.h264`, `.avi`, `.mov` | `video`                       | `loadVideoTextures` (参见 `references/video.md`)                                                                                 |
| 精灵表              | `.json` (精灵表格式)                                         | `spritesheet`                 | `spritesheetAsset` (参见 `references/spritesheet.md`)                                                                            |
| 位图字体            | `.fnt`, `.xml`                                                   | `bitmap-font`                 | `loadBitmapFont` (默认情况下加载工作正常；渲染 `BitmapText` 需要 `'pixi.js/text-bitmap'`；参见 `references/fonts.md`) |
| Web 字体            | `.ttf`, `.otf`, `.woff`, `.woff2`                                | `web-font`                    | `loadWebFont` (参见 `references/fonts.md`)                                                                                       |
| JSON                | `.json`                                                          | `json`                        | `loadJson`                                                                                                                      |
| 文本                | `.txt`                                                           | `text`                        | `loadTxt`                                                                                                                       |
| 压缩纹理            | `.basis`, `.dds`, `.ktx`, `.ktx2`                                | `basis`, `dds`, `ktx`, `ktx2` | 参见 `references/compressed-textures.md`                                                                                         |
| 动画 GIFs           | `.gif`                                                           | `gif`                         | 需要 `'pixi.js/gif'`；返回 `GifSource` (参见 `references/gif.md`)                                                         |

**解析器 ID** 列是您传递给资源描述符顶层 `parser` 字段以强制指定加载器的值。参见下文“强制解析器”。

## 使用 `parser` 强制解析器

默认情况下，PixiJS 通过匹配文件扩展名或 MIME 类型来选择加载器。当您的 URL 没有扩展名（CDN 签名 URL、blob URL、API 端点、内容哈希路径）时，解析器无法告诉加载器该做什么。在资源描述符的顶层 `parser` 字段中设置，以强制指定加载器：

```ts
// 签名 CDN URL 且没有扩展名
const texture = await Assets.load({
  src: "https://cdn.example.com/signed/abc123?token=xyz",
  parser: "texture",
});

// 返回 JSON 的 API 端点
const data = await Assets.load({
  alias: "config",
  src: "https://api.example.com/v1/config",
  parser: "json",
});

// 没有扩展名的字体 URL 且指定了字体族
await Assets.load({
  src: "https://cdn.example.com/fonts/hero-v2",
  parser: "web-font",
  data: { family: "Hero", weights: ["400", "700"] },
});

// 没有文件扩展名的视频流
const clipTexture = await Assets.load({
  src: "https://cdn.example.com/stream/xyz",
  parser: "video",
  data: { mime: "video/mp4", muted: true, playsinline: true },
});
```

`parser` 字段位于资源描述符的顶层（与 `src` 和 `data` 一起），而不是 `data` 内部。它接受上表中“支持的文件类型”的任何解析器 ID：

- `'texture'`, `'svg'`, `'video'`: 图像、SVG 和视频纹理
- `'json'`, `'text'`: JSON 和纯文本
- `'web-font'`, `'bitmap-font'`: Web 和位图字体
- `'spritesheet'`: 纹理图集 JSON
- `'gif'`: 动画 GIFs (需要 `'pixi.js/gif'`)
- `'basis'`, `'dds'`, `'ktx'`, `'ktx2'`: 压缩纹理 (每个都需要其副作用导入)

### 当您需要它

- **签名 CDN URL**: `https://cdn.example.com/get?id=abc123` 没有加载器可以测试的扩展名。
- **Blob 或 ObjectURL**: `URL.createObjectURL(blob)` 产生 `blob:...` URL 且没有扩展名。
- **自定义路由**: `/api/assets/hero-v2` 其中服务器决定内容类型。
- **没有后缀的内容哈希路径**: 一些构建管道产生像 `/static/abc123def` 这样的名称，而不是 `/static/abc123def.png`。

如果 URL 确实有扩展名，则不需要 `parser`；让自动检测完成其工作。只有在检测无法工作时才设置 `parser`。

### `loadParser` 已弃用

v7 的 `loadParser` 字段仍然有效，但会发出弃用警告。对于新代码，请使用 `parser`。

```ts
// 旧版 (已弃用)
await Assets.load({ src: "...", loadParser: "loadTextures" });

// 新版
await Assets.load({ src: "...", parser: "texture" });
```

## 主题

每个资源工作流都在一个参考文件中涵盖。选择与问题匹配的文件：

| 主题                          | 参考                                                              | 何时                                        |
| ------------------------------ | ---------------------------------------------------------------------- | ------------------------------------------- |
| 纹理图集和动画               | [references/spritesheet.md](references/spritesheet.md)                 | 使用 `AnimatedSprite` 加载精灵表时         |
| 视频纹理                     | [references/video.md](references/video.md)                             | `.mp4`, `.webm`, 自动播放, 循环, 移动设备  |
| Web 和位图字体               | [references/fonts.md](references/fonts.md)                             | `.woff2`, `.fnt`, 字体族, SDF 字体        |
| 动画 GIFs                    | [references/gif.md](references/gif.md)                                 | `.gif`, `GifSprite`, 播放控制             |
| 按功能分组资源               | [references/bundles.md](references/bundles.md)                         | `addBundle`, `loadBundle`, `unloadBundle`   |
| 预先声明所有内容               | [references/manifests.md](references/manifests.md)                     | `Assets.init({ manifest })` 工作流       |
| 缓存查找和清理               | [references/caching.md](references/caching.md)                         | `Assets.get`, `Assets.unload`, `Cache`      |
| 预热未来资源                 | [references/background.md](references/background.md)                   | `backgroundLoad`, `backgroundLoadBundle`    |
| 加载屏幕                    | [references/progress.md](references/progress.md)                       | `onProgress`, LoadOptions 进度          |
| GPU 压缩格式                 | [references/compressed-textures.md](references/compressed-textures.md) | `.ktx2`, `.basis`, `.dds`, `.ktx`           |
| 向量与光栅 SVG               | [references/svg.md](references/svg.md)                                 | `parseAsGraphicsContext`, 纹理模式      |
| Retina + 格式检测            | [references/resolution.md](references/resolution.md)                   | `@{1,2}x`, `format` 偏好设置             |

## 决策指南

- **需要加载单个图像？** 使用 `Assets.load(url)`。无需设置。
- **按层级/场景分组加载许多资源？** 使用捆绑包。参见 `references/bundles.md`。
- **在构建时知道所有资源？** 在 `Assets.init` 中使用清单。参见 `references/manifests.md`。
- **需要加载进度条？** 将进度回调传递给 `Assets.load`。参见 `references/progress.md`。
- **平滑切换层级？** 背景加载下一个层级。参见 `references/background.md`。
- **内存预算很重要？** 使用压缩纹理并在屏幕之间使用 `Assets.unload`。参见 `references/compressed-textures.md` 和 `references/caching.md`。
- **需要任何尺寸的清晰 SVG 图标？** 作为图形加载，而不是纹理。参见 `references/svg.md`。
- **Retina + WebP/AVIF？** 配置 `texturePreference` 并使用格式模式。参见 `references/resolution.md`。

## 加载选项和错误处理

加载资源时有两种独立的“选项”概念：

1. **`LoadOptions`**: `Assets.load`/`loadBundle` 的第二个参数。控制跨整个加载的错误恢复、重试、进度和完成回调。
2. **`data`**: 每个资源描述符上的字段。将解析器特定选项（缩放模式、分辨率、字体族、自动播放标志等）转发给特定资源的加载器。

### LoadOptions (每个调用)

```ts
await Assets.load(["hero.png", "enemy.png"], {
  onProgress: (p) => updateBar(p),
  onError: (err, url) => {
    const src = typeof url === "string" ? url : url.src;
    console.warn("failed:", src, err);
  },
  strategy: "retry",
  retryCount: 3,
  retryDelay: 250,
});
```

- `onProgress(progress)`: `[0, 1]` 作为调用中的资源完成。
- `onError(error, url)`: `url` 是 `string | ResolvedAsset`。在读取 `.src` 之前进行保护；当 `url` 是字符串时，`.src` 未定义。
- `strategy: 'throw' | 'skip' | 'retry'` — 默认 `'throw'`。`'skip'` 使用任何成功的资源；`'retry'` 重试失败的资源。
- `retryCount` — 默认 `3`，当 `strategy` 为 `'retry'` 时，每个资源重试次数。
- `retryDelay` — 默认 `250` 毫秒之间的重试间隔。

全局默认值位于 `Loader.defaultOptions`，或传递 `loadOptions` 给 `Assets.init()`。

### `data` 选项 (每个资源)

每个加载器解析器从资源描述符的 `data` 字段读取其自己的选项。使用下表为每种资源类型选择正确的选项：

| 资源类型         | `data` 形状                                                                    | 关键选项                                                                                                                                                                                                                                                | 参考                           |
| ------------------ | ------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------- |
| 纹理 (图像)    | `TextureSourceOptions`                                                          | `resolution`, `scaleMode`, `alphaMode`, `autoGenerateMipmaps`, `antialias`, `addressMode`                                                                                                                                                                  | `references/resolution.md`          |
| SVG                | `{ parseAsGraphicsContext?, resolution? }`                                      | `parseAsGraphicsContext` 用于图形模式；`resolution` 用于更清晰的栅格                                                                                                                                                                                | `references/svg.md`                 |
| 视频              | `VideoSourceOptions`                                                            | `autoPlay`, `loop`, `muted`, `playsinline`, `preload`, `updateFPS`, `crossorigin`, `mime`                                                                                                                                                                  | `references/video.md`               |
| Web 字体           | `LoadFontData`                                                                  | `family`, `weights`, `style`, `display`, `unicodeRange`, `featureSettings`                                                                                                                                                                                 | `references/fonts.md`               |
| 位图字体        | (无；自动配置)                                                         | 距离场检测设置缩放模式和 Mipmaps                                                                                                                                                                                                                       | `references/fonts.md`               |
| 精灵表        | `{ texture?, imageFilename?, ignoreMultiPack?, textureOptions?, cachePrefix? }` | `textureOptions` 将 `TextureSourceOptions` (例如 `scaleMode`) 转发到图集图像；`texture` 跳过图像加载；`imageFilename` 覆盖引用的图像；`ignoreMultiPack` 跳过多包后续；`cachePrefix` 命名空间帧 | `references/spritesheet.md`         |
| GIF                | `GifBufferOptions`                                                              | `fps`, `scaleMode`, `resolution`, `autoGenerateMipmaps`                                                                                                                                                                                                    | `references/gif.md`                 |
| 压缩纹理            | `TextureSourceOptions`                                                          | `scaleMode`, `addressMode`, `autoGenerateMipmaps`                                                                                                                                                                                                          | `references/compressed-textures.md` |
| JSON / 文本        | (无)                                                                          | 原样返回                                                                                                                                                                                                                                                 | —                                   |

结合 `LoadOptions` 和 `data` 的示例：

```ts
await Assets.load(
  {
    alias: "hero",
    src: "hero.png",
    data: { scaleMode: "nearest", resolution: 2 },
  },
  { strategy: "retry", retryCount: 3 },
);
```

在清单或捆绑包中，每个条目都可以携带自己的 `data`：

```ts
await Assets.init({
  manifest: {
    bundles: [
      {
        name: "level1",
        assets: [
          { alias: "tiles", src: "tiles.png", data: { scaleMode: "nearest" } },
          { alias: "font", src: "hero.woff2", data: { family: "Hero" } },
          {
            alias: "clip",
            src: "intro.mp4",
            data: { autoPlay: false, muted: true },
          },
        ],
      },
    ],
  },
});
```

## 运行时配置

`Assets.init(options)` 接受 `basePath` 和 `manifest` 以及：

- `defaultSearchParams` — 字符串或 `Record<string, any>` 追加到每个解析的 URL。用于缓存破坏。
- `skipDetections: boolean` — 跳过浏览器格式检测以加快初始化。需要显式 `texturePreference.format`。
- `bundleIdentifier: BundleIdentifierOptions` — 自定义捆绑包键解析方式，以便相同的别名可以存在于多个捆绑包中。
- `loadOptions: Partial<LoadOptions>` — 设置每个后续 `Assets.load` 调用的默认 `strategy`、`retryCount`、`retryDelay` 和回调。
- `preferences: Partial<AssetsPreferences>` — `crossOrigin`、`preferWorkers`、`preferCreateImageBitmap`、`parseAsGraphicsContext`。

初始化后，偏好设置仍然可以调整：

```ts
Assets.setPreferences({
  crossOrigin: "anonymous",
  preferCreateImageBitmap: false,
});

for (const detection of Assets.detections) {
  console.log(detection.extension);
}

Assets.reset();
```

- `Assets.setPreferences(preferences)` — 将新的偏好设置推送到支持它们的每个解析器。
- `Assets.detections` — 获取注册的 `FormatDetectionParser` 列表；在检查当前环境宣传的格式时使用。
- `Assets.reset()` — 内部完整重置（解析器 + 加载器 + 缓存）。专为测试设计，以便可以运行新的 `Assets.init`。

## 常见错误

### [CRITICAL] 使用 `Texture.from(url)` 加载

错误：

```ts
const texture = Texture.from("https://example.com/image.png");
```

正确：

```ts
const texture = await Assets.load("https://example.com/image.png");
```

在 v8 中，`Texture.from()` 仅读取缓存。它不会从 URL 获取。首先使用 `Assets.load()`；返回值是纹理本身。


### [HIGH] 使用位置 `Assets.add` 签名

错误：

```ts
Assets.add("bunny", "bunny.png");
```

正确：

```ts
Assets.add({ alias: "bunny", src: "bunny.png" });
```

位置 `Assets.add(key, url)` 形式在 v8 中已移除。使用具有 `alias` 和 `src` 属性的选项对象。


### [HIGH] 在层级之间未卸载纹理

`Assets.load()` 无限期缓存纹理。对于基于层级的游戏或具有不同资源集的屏幕，在过渡到释放 GPU 内存时调用 `Assets.unloadBundle()`。


## API 参考

- [Assets](https://pixijs.download/release/docs/assets.Assets.html.md)
- [Loader](https://pixijs.download/release/docs/assets.Loader.html.md)
- [Resolver](https://pixijs.download/release/docs/assets.Resolver.html.md)
- [Cache](https://pixijs.download/release/docs/assets.Cache.html.md)
- [LoadOptions](https://pixijs.download/release/docs/assets.LoadOptions.html.md)
- [AssetInitOptions](https://pixijs.download/release/docs/assets.AssetInitOptions.html.md)
- [AssetsManifest](https://pixijs.download/release/docs/assets.AssetsManifest.html.md)
- [AssetsBundle](https://pixijs.download/release/docs/assets.AssetsBundle.html.md)
- [BackgroundLoader](https://pixijs.download/release/docs/assets.BackgroundLoader.html.md)
- [Spritesheet](https://pixijs.download/release/docs/assets.Spritesheet.html.md)
