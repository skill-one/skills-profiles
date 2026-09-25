PixiJS v8 获取屏幕像素的基础模型：渲染器决定使用哪个 GPU 后端，渲染循环驱动每帧工作，环境层将库适配到浏览器、Web Worker 或 SSR 环境。有关场景图本身（容器、变换、销毁），请参阅 `pixijs-scene-core-concepts`。

## 快速入门

```ts
console.log(app.renderer.name); // 'webgl' | 'webgpu' | 'canvas'

app.ticker.add((ticker) => {
  sprite.rotation += 0.01 * ticker.deltaTime;
});

const tex = app.renderer.extract.texture({ target: app.stage });

app.renderer.render({ container: app.stage });
```

`app.renderer` 是由 `autoDetectRenderer` 选择 的 `WebGLRenderer`、`WebGPURenderer` 或 `CanvasRenderer`。TickerPlugin 会自动驱动 `renderer.render()`；只有当 `autoStart: false` 时才需要手动调用。后端选择在 `Application.init({ preference })` 中发生；请参阅 `pixijs-application` 了解设置。

**相关技能：** `pixijs-application`（应用构建和生命周期）、`pixijs-ticker`（每帧逻辑、优先级、FPS 限制）、`pixijs-environments`（Web Worker、SSR、严格 CSP）、`pixijs-custom-rendering`（编写 RenderPipe）、`pixijs-scene-core-concepts`（场景图基础）。

## 主题

| 主题               | 参考                                              | 时间                                                      |
| ------------------- | ------------------------------------------------------ | --------------------------------------------------------- |
| 选择后端          | [references/renderers.md](references/renderers.md)     | 偏好表单、每渲染器选项、系统和管道                        |
| 每帧执行          | [references/render-loop.md](references/render-loop.md) | 优先级顺序、时间单位、手动渲染                          |

要深入了解任何单个主题，请打开相应的参考文件。非浏览器目标（`DOMAdapter`、`WebWorkerAdapter`、自定义适配器、严格 CSP）在 `pixijs-environments` 技能中涵盖。

## 决策指南

- **设置应用？** 从 `pixijs-application` 开始。此技能解释了渲染器在底层的工作原理。
- **在 WebGL 和 WebGPU 之间选择？** 将 `['webgpu', 'webgl']` 作为您的偏好数组。WebGPU 在可用时最快；WebGL 是可靠的回退。请参阅 `references/renderers.md`。
- **在 Web Worker 中运行？** 在 `app.init` 之前设置 `DOMAdapter.set(WebWorkerAdapter)`。请参阅 `pixijs-environments` 技能了解完整设置。
- **需要手动控制渲染何时发生？** 设置 `autoStart: false` 并从您自己的循环中调用 `app.renderer.render(app.stage)`。请参阅 `references/render-loop.md`。
- **与物理库集成？** 在 `UPDATE_PRIORITY.HIGH` 添加您的更新，以便物理效果在 `LOW` 优先级的渲染之前运行。请参阅 `references/render-loop.md`。
- **编写自定义可渲染对象？** 实现 `RenderPipe`。请参阅 `pixijs-custom-rendering` 技能。
- **渲染到纹理或自定义渲染目标？** 将 `target` 传递给 `renderer.render()`，或使用显式的颜色和深度附件构建 `RenderTarget`。请参阅 `references/renderers.md`。
- **在严格 CSP 下运行？** 导入 `'pixi.js/unsafe-eval'`。请参阅 `pixijs-environments` 技能。

## 快速概念

### 渲染器 = 系统 + 管道

每个渲染器由 `Systems`（生命周期服务：纹理、缓冲区、状态、滤镜、遮罩）和 `RenderPipes`（每可渲染对象指令构建器：精灵、图形、网格、粒子、文本、瓦片）组成。编写自定义可渲染对象意味着实现一个 `RenderPipe` 并通过扩展注册它。特定于后端的系统和管道可以通过渲染器加载器扩展（`WebGLLoader`、`WebGPULoader`、`CanvasLoader`）动态导入；请参阅 `references/renderers.md`。

### 渲染循环

`app.ticker.add(fn)` 注册一个每帧运行的回调。`TickerPlugin` 在 `UPDATE_PRIORITY.LOW` 注册 `app.render()`，因此 `NORMAL` 或 `HIGH` 优先级的 ticker 回调会在绘制之前运行。使用 `autoStart: false` 禁用插件以进行手动控制。

### 环境

`DOMAdapter` 抽象了 PixiJS 执行的每个 DOM 调用（画布创建、图像加载、fetch、XML 解析）。通过 `DOMAdapter.set(WebWorkerAdapter)` 交换以用于 Worker，或在 Node/SSR 中实现自定义 `Adapter`。必须在 `Application.init` 之前完成。

## 常见错误

### [HIGH] 在 `init()` 解决之前访问 `app.renderer`

错误：

```ts
const app = new Application();
app.init({ width: 800, height: 600 });
console.log(app.renderer.name); // undefined — init() 是异步的
```

正确：

```ts
const app = new Application();
await app.init({ width: 800, height: 600 });
console.log(app.renderer.name); // 'webgl' | 'webgpu' | 'canvas'
```

`Application.init()` 是异步的。`app.renderer`、`app.canvas` 和 `app.screen` 在 Promise 解决后才存在。

### [HIGH] 在 `Application.init` 之后设置 `DOMAdapter`

错误：

```ts
const app = new Application();
await app.init({ width: 800, height: 600 });
DOMAdapter.set(WebWorkerAdapter); // 太晚了 — init 已经分配了资源
```

正确：

```ts
DOMAdapter.set(WebWorkerAdapter);
const app = new Application();
await app.init({ width: 800, height: 600 });
```

适配器抽象了渲染器在构建过程中执行的 DOM 调用（画布创建、图像加载、fetch）。在 `init()` 之前交换它，否则错误的适配器将被烘焙到渲染器中。

### [MEDIUM] 将 `preference` 视为一种保证

错误：

```ts
await app.init({ preference: "webgpu" });
// 假设 WebGPU 是活动的
useWebGPUOnlyFeature(app.renderer);
```

正确：

```ts
await app.init({ preference: "webgpu" });
if (app.renderer.name === "webgpu") {
  useWebGPUOnlyFeature(app.renderer);
}
```

`preference` 是一个提示，不是要求。如果浏览器缺乏 WebGPU 支持，PixiJS 会回退到 WebGL（或 Canvas）。始终根据 `renderer.name` 分支以进行后端特定代码。

## API 参考

- [autoDetectRenderer](https://pixijs.download/release/docs/rendering.autoDetectRenderer.html.md)
- [AbstractRenderer](https://pixijs.download/release/docs/rendering.AbstractRenderer.html.md)
- [WebGLRenderer](https://pixijs.download/release/docs/rendering.WebGLRenderer.html.md)
- [WebGPURenderer](https://pixijs.download/release/docs/rendering.WebGPURenderer.html.md)
- [CanvasRenderer](https://pixijs.download/release/docs/rendering.CanvasRenderer.html.md)
- [Application](https://pixijs.download/release/docs/app.Application.html.md)
- [DOMAdapter](https://pixijs.download/release/docs/environment.DOMAdapter.html.md)
