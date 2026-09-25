`Application` 是一个便捷的封装器，它拥有一个渲染器、一个根 `stage` 容器、一个画布以及 Ticker/Resize 插件。在 v8 版本中，构造函数不接受任何参数；所有配置都通过异步 `app.init()` 调用传递，该调用通过 `autoDetectRenderer` 实例化渲染器。

## 快速入门

```ts
import { Application } from "pixi.js";

const app = new Application();

await app.init({
  resizeTo: window,
  background: "#1099bb",
  antialias: true,
  preference: "webgl",
  autoDensity: true,
  resolution: window.devicePixelRatio,
});

document.body.appendChild(app.canvas);
```

**相关技能：** `pixijs-core-concepts`（渲染器、渲染管线）、`pixijs-ticker`（渲染循环细节）、`pixijs-scene-container`（使用 `app.stage`）、`pixijs-environments`（非浏览器环境设置）。

## 核心模式

### 生命周期：构造、初始化、渲染、销毁

```ts
import { Application } from "pixi.js";

const app = new Application();

await app.init({ width: 800, height: 600 });
document.body.appendChild(app.canvas);

// ... 运行场景，Ticker 自动驱动 app.render() ...

app.destroy(
  { removeView: true, releaseGlobalResources: true },
  { children: true, texture: true, textureSource: true },
);
```

- `new Application()` 分配实例但不创建任何内容。传递这里的选项会被忽略并记录一个弃用警告。
- `app.init(options)` 是异步的。它构建渲染器、连接插件，并且必须在您可以使用 `app.canvas`、`app.renderer` 或 `app.screen` 之前完成。
- TickerPlugin 在初始化解决后每帧调用 `app.render()`（除非 `autoStart: false`）。
- `app.destroy(rendererDestroyOptions, stageDestroyOptions)` — 第一个参数转发到 `renderer.destroy()`。传递 `true` 或 `{ removeView: true }` 以从 DOM 中移除画布。添加 `releaseGlobalResources: true` 以在销毁和在同一选项卡中重新创建应用时排空全局池（批处理、纹理缓存）；省略它是重新初始化后出现闪烁和陈旧纹理的常见原因（见 `pixijs-performance`）。

### 关键初始化选项

```ts
await app.init({
  width: 800,
  height: 600,
  background: 0x1099bb,
  backgroundAlpha: 1,

  antialias: true,
  resolution: window.devicePixelRatio,
  autoDensity: true,

  preference: "webgpu",

  autoStart: true,
  sharedTicker: false,

  resizeTo: window,

  canvas: document.querySelector("#game-canvas") as HTMLCanvasElement,
});
```

对于每个选项——视图/画布、背景、渲染器偏好（包括数组形式）、Ticker、调整大小、剔除器、事件、无障碍访问、WebGL/WebGPU 上下文标志、图形贝塞尔平滑度、GC 以及每渲染器覆盖（`webgl` / `webgpu` / `canvasOptions`）——请参阅 [references/application-options.md](references/application-options.md)。

### Application 属性

```ts
app.stage; // 根容器；将所有显示对象添加到这里
app.renderer; // WebGL/WebGPU/Canvas 渲染器实例
app.canvas; // HTMLCanvasElement（您自己将其插入 DOM）
app.screen; // 描述可见区域的矩形（以 CSS 像素为单位）
app.domContainerRoot; // 包含 DOMContainer 叠层的 HTMLDivElement
```

`app.stage` 是一个普通的 `Container`。有关场景图细节（变换、addChild、destroy）请参阅 `pixijs-scene-container`。有关渲染器级别的操作（提取、生成纹理、自定义系统）请参阅 `pixijs-core-concepts` 和 `pixijs-custom-rendering`。`app.domContainerRoot` 是渲染器用于托管 `DOMContainer` 叠层的 `<div>`；当您需要将 DOM 元素固定到场景节点时，将其添加到 `app.canvas` 旁边（见 `pixijs-scene-dom-container`）。

### ResizePlugin

在初始化时设置 `resizeTo`（或在之后重新分配 `app.resizeTo`）以使插件监听 `resize` 事件并调用 `renderer.resize()` 使用目标元素的客户端大小。结合 `autoDensity: true` 和 `resolution: window.devicePixelRatio` 以获得高 DPI 输出。

```ts
await app.init({ resizeTo: window });

app.resizeTo = document.querySelector("#game-container") as HTMLElement;

app.resize(); // 立即调整为目标当前大小
app.queueResize(); // 将调整推迟到下一帧动画帧；内部用于 `window.resize` 监听器以避免重复工作
app.cancelResize(); // 取消挂起的 queueResize
```

插件使画布与目标匹配。`app.screen` 和 `app.canvas.width/height` 会相应更新；在调整大小后读取它们以放置 UI。

- `app.resize()` — 立即同步调整大小。
- `app.queueResize()` — 合并快速调用，通过推迟到下一帧；内部用于 `window.resize` 监听器以避免重复工作。
- `app.cancelResize()` — 取消挂起的调整大小。在您触发 `queueResize` 的自己的布局代码销毁之前调用此方法。

### Ticker 基础

TickerPlugin 创建 `app.ticker` 并在 `UPDATE_PRIORITY.LOW` 将 `app.render()` 注册到它。使用 `app.start()`/`app.stop()` 控制循环，并使用 `app.ticker.add` / `app.ticker.addOnce` 添加回调：

```ts
app.ticker.add((ticker) => {
  sprite.rotation += 0.01 * ticker.deltaTime;
});

app.ticker.addOnce(() => {
  console.log("在下一帧运行一次，然后移除自己");
});

app.stop(); // 暂停渲染循环（例如选项卡隐藏）
app.start(); // 恢复
```

回调接收 `Ticker` 实例；读取 `ticker.deltaTime` 获取帧率无关的乘数（60fps 时约等于 1.0）、`ticker.deltaMS` 获取实际毫秒数，或 `ticker.FPS` 获取当前帧率。有关优先级、帧率限制、`onRender`、共享与私有 Ticker 以及 v8 回调签名更改，请参阅 `pixijs-ticker`。

### 手动渲染循环

```ts
await app.init({ autoStart: false, width: 800, height: 600 });
document.body.appendChild(app.canvas);

function frame() {
  updateScene();
  app.render();
  requestAnimationFrame(frame);
}
frame();
```

`autoStart: false` 防止 TickerPlugin 自动启动 Ticker。您自己调用 `app.render()`（或 `app.renderer.render({ container: app.stage })` 以达到相同效果）。如果您仍然希望注册的 Ticker 回调被触发，请在循环中 `app.ticker.update()` 在 `app.render()` 之前调用。

### CullerPlugin（可选）

CullerPlugin 跳过渲染位于 `app.renderer.screen` 外部的容器。它默认未注册；在创建应用之前添加它：

```ts
import {
  Application,
  Container,
  Sprite,
  extensions,
  CullerPlugin,
  Rectangle,
} from "pixi.js";

extensions.add(CullerPlugin);

const app = new Application();
await app.init({ width: 800, height: 600 });

const world = new Container();
world.cullable = true; // 当其边界离开屏幕时，此容器会被剔除
world.cullableChildren = true; // 默认；设置为 `false` 以跳过递归到子元素

const tile = Sprite.from("tile.png");
tile.cullable = true;
world.addChild(tile);
app.stage.addChild(world);
```

除非设置 `cullable`，否则容器不会被剔除。使用 `container.cullArea = new Rectangle(x, y, w, h)` 覆盖默认边界检查，当子边界计算成本高昂时。插件包装 `app.render()`，因此 `Culler.shared.cull(app.stage, app.renderer.screen)` 在每帧之前运行。有关剔除何时有效，请参阅 `pixijs-performance`。

### 自定义 Application 插件

通过注册一个具有 `static init`、`static destroy` 和 `static extension = ExtensionType.Application` 的类来扩展 `Application`。这两种方法都使用 `this` 绑定到 Application 实例，因此 `this.renderer` 和 `this.stage` 是可用的。

```ts
import {
  Application,
  ExtensionType,
  extensions,
  type ApplicationOptions,
} from "pixi.js";

class FpsOverlay {
  public static extension = ExtensionType.Application;

  public static init(this: Application, options: Partial<ApplicationOptions>) {
    // 在 app.init() 内部运行，渲染器创建后
    // 将属性/方法附加到 `this` 以在应用上公开它们
  }

  public static destroy(this: Application) {
    // 在 app.destroy() 内部运行——销毁您附加的任何内容
  }
}

extensions.add(FpsOverlay);
```

插件按注册顺序初始化，按相反顺序销毁。要为您的插件添加带类型的选项，请扩展 `PixiMixins.ApplicationOptions`：

```ts
declare global {
  namespace PixiMixins {
    interface ApplicationOptions {
      fpsOverlay?: { visible?: boolean };
    }
  }
}

await app.init({ fpsOverlay: { visible: true } });
```

内置的 `ResizePlugin`、`TickerPlugin` 和可选的 `CullerPlugin` 都使用相同的契约。如果您设置 `skipExtensionImports: true`，请自己注册所需的内置插件（`extensions.add(ResizePlugin, TickerPlugin)`）。

## 常见错误

### [CRITICAL] 向构造函数传递选项

错误：

```ts
const app = new Application({ width: 800, height: 600 });
document.body.appendChild(app.canvas);
```

正确：

```ts
const app = new Application();
await app.init({ width: 800, height: 600 });
document.body.appendChild(app.canvas);
```

在 v8 中，`Application` 构造函数不接受任何参数。传递这里的选项会被忽略并记录一个弃用警告；渲染器仅在异步 `init()` 调用内部创建。

### [HIGH] 使用 app.view 而不是 app.canvas

错误：

```ts
document.body.appendChild(app.view);
```

正确：

```ts
document.body.appendChild(app.canvas);
```

`app.view` 在 v8 中被重命名为 `app.canvas`。旧获取器仍然有效，但会发出弃用警告。

### [MEDIUM] 在 init 解决之前触摸 app.canvas 或 app.renderer

错误：

```ts
const app = new Application();
document.body.appendChild(app.canvas);
app.init({ width: 800, height: 600 });
```

正确：

```ts
const app = new Application();
await app.init({ width: 800, height: 600 });
document.body.appendChild(app.canvas);
```

`app.renderer`、`app.canvas` 和 `app.screen` 只有在 `init()` 的 Promise 解决后才会填充。在更早的时间访问它们会返回 `undefined`。

## API 参考

- [Application](https://pixijs.download/release/docs/app.Application.html.md)
- [ApplicationOptions](https://pixijs.download/release/docs/app.ApplicationOptions.html.md)
- [ApplicationPlugin](https://pixijs.download/release/docs/app.ApplicationPlugin.html.md)
- [ResizePlugin](https://pixijs.download/release/docs/app.ResizePlugin.html.md)
- [ResizePluginOptions](https://pixijs.download/release/docs/app.ResizePluginOptions.html.md)
- [TickerPlugin](https://pixijs.download/release/docs/app.TickerPlugin.html.md)
- [TickerPluginOptions](https://pixijs.download/release/docs/app.TickerPluginOptions.html.md)
- [CullerPlugin](https://pixijs.download/release/docs/app.CullerPlugin.html.md)
- [autoDetectRenderer](https://pixijs.download/release/docs/rendering.autoDetectRenderer.html.md)
