`DOMAdapter` 抽象了 PixiJS 所有的 DOM 访问操作（canvas 创建、Image 加载、fetch、XML 解析），以便库可以在非浏览器环境中运行。在 `app.init()` 之前调用 `DOMAdapter.set(...)` 以切换到不同的适配器。

## 快速入门

```ts
// worker.ts — 从主线程发送的 OffscreenCanvas
DOMAdapter.set(WebWorkerAdapter);

self.onmessage = async (event) => {
  const app = new Application();
  await app.init({
    canvas: event.data.canvas,
    width: 800,
    height: 600,
  });
};
```

对于阻止 `unsafe-eval` 的 CSP 环境，在任何渲染器初始化之前导入 polyfill：

```ts
import "pixi.js/unsafe-eval";
```

**相关技能：** `pixijs-application`（标准浏览器初始化）、`pixijs-migration-v8`（设置移除、适配器更改）。

## 核心模式

### 使用 Web Worker 和 OffscreenCanvas

将 OffscreenCanvas 从主线程转移，然后在 worker 中初始化 PixiJS：

```ts
// main.ts
const canvas = document.createElement("canvas");
canvas.width = 800;
canvas.height = 600;
document.body.appendChild(canvas);

const offscreen = canvas.transferControlToOffscreen();
const worker = new Worker("worker.ts", { type: "module" });
worker.postMessage({ canvas: offscreen }, [offscreen]);
```

```ts
// worker.ts
import { Application, DOMAdapter, WebWorkerAdapter } from "pixi.js";

DOMAdapter.set(WebWorkerAdapter);

self.onmessage = async (event) => {
  const app = new Application();
  await app.init({
    canvas: event.data.canvas,
    width: 800,
    height: 600,
  });
};
```

`DOMAdapter.set(WebWorkerAdapter)` 必须在 `new Application()` 之前发生。WebWorkerAdapter 使用 `OffscreenCanvas` 而不是 `document.createElement('canvas')`，并使用 `@xmldom/xmldom` 进行 XML 解析。

在 Web Worker 中无法工作的功能（没有 DOM 访问）：

- `DOMContainer` — 没有真实的 DOM 节点可以覆盖。
- `AccessibilitySystem` — 依赖于 DOM 聚焦和屏幕阅读器钩子。
- 通过字体加载 API 加载 `FontFace` — 使用预转换的位图字体（`BitmapFont.install` 或 `.fnt` 资源）代替。

### 环境特定的子路径导入

而不是导入 `pixi.js`，你可以为每个环境引入一个经过筛选的包：

```ts
import "pixi.js/browser"; // 可访问性、DOM、事件、精灵表、渲染、滤镜
import "pixi.js/webworker"; // 精灵表、渲染、滤镜（没有仅限 DOM 的模块）
```

`pixi.js/webworker` 故意省略了 `accessibility`、`dom` 和 `events`，因为它们需要 DOM。当你想要静态、同步的模块注册而不是依赖 `loadEnvironmentExtensions` 在渲染器初始化时动态导入正确的集合并使用这些子路径条目。

### loadEnvironmentExtensions

```ts
import { loadEnvironmentExtensions } from "pixi.js";

await loadEnvironmentExtensions(false); // false = 加载默认值；true = 跳过
```

`loadEnvironmentExtensions(skip)` 替换了已弃用的 `autoDetectEnvironment` 辅助程序（自 8.1.6 起）。传递 `true` 以避免在引导自定义环境时自动加载默认的浏览器扩展。`autoDetectEnvironment(add)` 仍然存在作为转发到 `loadEnvironmentExtensions(!add)` 的占位符。

### CSP 合规设置

PixiJS 内部使用 `new Function()` 进行着色器编译和统一同步。在阻止 `unsafe-eval` 的 CSP 环境中，导入 polyfill：

```ts
import "pixi.js/unsafe-eval";
import { Application } from "pixi.js";

const app = new Application();
await app.init({ width: 800, height: 600 });
```

`pixi.js/unsafe-eval` 导入用静态 polyfill 替换了基于 eval 的代码生成，用于着色器同步、UBO 同步、统一同步和粒子缓冲区更新。导入必须在任何 PixiJS 渲染器初始化之前进行。

**张力提示：** `pixi.js/unsafe-eval` 的名称具有误导性。它不会启用不安全的 eval；它消除了对它的需求。该名称指的是它绕过的 CSP 指令。

### 自定义适配器

对于非标准环境（Node.js、无头测试、SSR），实现完整的 Adapter 接口：

```ts
import { DOMAdapter } from "pixi.js";
import type { Adapter } from "pixi.js";
import { createCanvas, Image } from "canvas";
import { DOMParser } from "@xmldom/xmldom";

const HeadlessAdapter: Adapter = {
  createCanvas: (width, height) => createCanvas(width ?? 0, height ?? 0),
  createImage: () => new Image(),
  getCanvasRenderingContext2D: () => CanvasRenderingContext2D,
  getWebGLRenderingContext: () => WebGLRenderingContext,
  getNavigator: () => ({ userAgent: "HeadlessAdapter", gpu: null }),
  getBaseUrl: () => "file://",
  getFontFaceSet: () => null,
  fetch: (url, options) => fetch(url, options),
  parseXML: (xml) => new DOMParser().parseFromString(xml, "text/xml"),
};

DOMAdapter.set(HeadlessAdapter);
```

Adapter 接口需要这些方法：`createCanvas`、`createImage`、`getCanvasRenderingContext2D`、`getWebGLRenderingContext`、`getNavigator`、`getBaseUrl`、`getFontFaceSet`、`fetch`、`parseXML`。

### 检查当前适配器

```ts
import { DOMAdapter } from "pixi.js";

const adapter = DOMAdapter.get();
const canvas = adapter.createCanvas(256, 256);
const img = adapter.createImage();
```

`DOMAdapter.get()` 返回当前设置的适配器。在 PixiJS 相关代码中，使用此方法进行任何 DOM 访问，而不是直接调用 `document` 或 `Image`。

## 常见错误

### [CRITICAL] 在 app.init() 之前未设置适配器

错误：

```ts
const app = new Application();
await app.init({ width: 800, height: 600 });
DOMAdapter.set(WebWorkerAdapter); // 太晚了；在 init 期间已经读取了适配器
```

正确：

```ts
DOMAdapter.set(WebWorkerAdapter);
const app = new Application();
await app.init({ width: 800, height: 600 });
```

在非浏览器环境中，必须调用 `DOMAdapter.set()` 在 `app.init()` 之前。PixiJS 在创建渲染器时在 `app.init()` 期间读取适配器。`new Application()` 本身只创建舞台 Container，并不读取适配器。

### [HIGH] 直接使用 document 或 Image

错误：

```ts
const img = new Image();
img.src = "texture.png";
```

正确：

```ts
import { DOMAdapter } from "pixi.js";

const img = DOMAdapter.get().createImage();
img.src = "texture.png";
```

PixiJS 中的所有 DOM 访问都通过 DOMAdapter 进行。直接使用 `document`、`Image` 或其他浏览器全局变量会破坏 Web Worker 和 SSR 兼容性。

### [HIGH] CSP unsafe-eval 导入名称混淆

错误：

```ts
// CSP 环境，省略导入
import { Application } from "pixi.js";
// 抛出： "当前环境不允许 unsafe-eval，
// 请使用 pixi.js/unsafe-eval 模块以启用支持。"
```

正确：

```ts
import "pixi.js/unsafe-eval";
import { Application } from "pixi.js";
```

`pixi.js/unsafe-eval` 导入消除了着色器编译中对 `eval()` / `new Function()` 的需求。尽管名称暗示它启用了不安全的 eval，但它恰恰相反：它安装了静态 polyfill 以便 PixiJS 在严格的 CSP 下工作。

PixiJS 在渲染器初始化时检测到 CSP 阻挡并抛出上述错误。浏览器也可能在 PixiJS 报告之前记录自己的 CSP 违规；两者都指向相同的修复方法。

### [HIGH] 使用旧的 settings.ADAPTER 模式

错误：

```ts
import { settings, WebWorkerAdapter } from "pixi.js";
settings.ADAPTER = WebWorkerAdapter;
```

正确：

```ts
import { DOMAdapter, WebWorkerAdapter } from "pixi.js";
DOMAdapter.set(WebWorkerAdapter);
```

`settings` 对象在 v8 中已移除。所有适配器配置都使用 `DOMAdapter.set()`。

## API 参考

- [DOMAdapter](https://pixijs.download/release/docs/environment.DOMAdapter.html.md)
- [BrowserAdapter](https://pixijs.download/release/docs/environment.BrowserAdapter.html.md)
- [WebWorkerAdapter](https://pixijs.download/release/docs/environment.WebWorkerAdapter.html.md)
- [autoDetectEnvironment](https://pixijs.download/release/docs/environment.autoDetectEnvironment.html.md)
- [loadEnvironmentExtensions](https://pixijs.download/release/docs/environment.loadEnvironmentExtensions.html.md)
