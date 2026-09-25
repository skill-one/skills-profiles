`HTMLSource` 和 `ElementImageSource` 将一个 DOM 元素转换为可在任何普通纹理可用的地方使用的 `TextureSource`：在 `Sprite` 上、作为 `Texture` 帧或映射到 `Mesh` 上。`HTMLSource` 将实时元素的像素镜像到 GPU（元素在浏览器中保持可编辑和可点击）；`ElementImageSource` 封装一个不可变的快照，该快照永远不会重绘。两者都位于 `pixi.js/html-source` 中；从该路径导入会注册它们的扩展。

> 这些来源依赖于实验性的“Canvas 中的 HTML”浏览器提案，并在 PixiJS v8 中标记为 EXPERIMENTAL。必须启用浏览器 API，或者在第一次渲染时纹理上传器会抛出错误；在使用它之前，请使用 `canvas.requestPaint` 进行特性检测。该 API 可能在次要版本之间发生变化。

假设熟悉 `pixijs-scene-sprite` 和纹理。这些是纹理 *来源*，不是显示对象：将它们包装在 `Sprite`（或 `Texture`/`Mesh`）中，才能将它们显示在屏幕上。不可在 Web Workers 中使用；worker 没有可以捕获的 DOM。

## 快速入门

```ts
import { Application, Sprite } from "pixi.js";
import { HTMLSource } from "pixi.js/html-source";

const app = new Application();
await app.init({ resizeTo: window });
document.body.appendChild(app.canvas);

// 元素必须是 Pixi canvas 的直接子元素。
const form = document.createElement("form");
form.innerHTML = '<input value="still editable" />';
app.canvas.appendChild(form);

// 将实时表单作为精灵渲染。它在浏览器中保持交互性。
const source = new HTMLSource({ resource: form });
const sprite = Sprite.from(source);

sprite.anchor.set(0.5);
sprite.position.set(app.screen.width / 2, app.screen.height / 2);
app.stage.addChild(sprite);
```

**相关技能：** `pixijs-scene-sprite`（显示纹理）、`pixijs-scene-mesh`（映射到几何图形，`PerspectiveMesh`）、`pixijs-scene-dom-container`（相反：在 canvas 之上叠加 HTML，在 GPU 管道之外）、`pixijs-assets`（纹理来源与加载器/缓存）、`pixijs-environments`（Web Workers 中没有 DOM）。

## 构造函数选项

两者都扩展了 `TextureSource`，因此所有 `TextureSourceOptions`（`resolution`、`scaleMode`、`addressMode`、`label` 等）都是有效的。每个 `resource` 都是必需的。

`HTMLSourceOptions`（实时元素）：

| 选项             | 类型               | 默认 | 描述                                                                                                                                              |
| ------------------ | ------------------ | ------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `resource`         | `Element`          | —       | 必需。要渲染的实时 DOM 元素。必须是所属 canvas 的直接子元素，否则构造函数会抛出错误。                                         |
| `canvas`           | `HTMLSourceCanvas` | —       | 拥有元素布局子树的 canvas。当元素是直接 canvas 子元素时，从 `resource.parentElement` 推断；当推断不可用时，传递它。 |
| `autoLayout`       | `boolean`          | `true`  | 在所属 canvas 上设置 `layoutsubtree` 属性。浏览器仅在存在该属性时才会布局和绘制 canvas 子元素。如果自己编写 `<canvas layoutsubtree>`，请设置为 `false`。 |
| `autoUpdate`       | `boolean`          | `true`  | 监听 canvas `paint` 事件，并在元素重绘时重新上传。设置为 `false` 以获取静态、一次性捕获的纹理。                             |
| `autoRequestPaint` | `boolean`          | `true`  | 构造后请求一次初始绘制。设置为 `false` 并在每一帧调用 `source.requestPaint()` 以实现连续动画。                  |

`ElementImageSourceOptions`（不可变快照）：

| 选项       | 类型           | 默认 | 描述                                                                                                                            |
| ------------ | -------------- | ------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| `resource`   | `ElementImage` | —       | 必需。来自 `canvas.captureElementImage(element)` 的快照。                                                                        |
| `autoClose`  | `boolean`      | `false` | 源被销毁时调用 `snapshot.close()`。当快照与其他来源共享时，保留 `false`，否则您可能会遇到 use-after-free。 |

通过静态 `HTMLSource.defaultOptions` 对象更改每个 `HTMLSource` 的默认值，例如 `HTMLSource.defaultOptions.autoUpdate = false`。

## 核心模式

### 设置和副作用导入

```ts
import "pixi.js/html-source";
import { HTMLSource, ElementImageSource } from "pixi.js/html-source";
```

`pixi.js/html-source` 调用 `extensions.add(...)` 来注册 `HTMLSource`、`ElementImageSource` 及其 WebGL/WebGPU 上传器。如果没有它，渲染器没有 `'html'` 上传器，这些来源永远不会渲染。这些类是从 `pixi.js/html-source` 导出的，而不是从 `pixi.js`。

从 `pixi.js/html-source` 导入命名导出也会触发副作用，因此只有当您不从这个路径导入任何其他内容时，才需要 `import 'pixi.js/html-source'`。

### 特性检测和浏览器支持

HTML-in-Canvas API 背后有一个浏览器标志。在使用它之前进行特性检测：

```ts
import type { HTMLSourceCanvas } from "pixi.js/html-source";

const canvas = app.canvas as HTMLSourceCanvas;

if (canvas.requestPaint) {
  // HTML-in-Canvas 可用。
}
```

将 `app.canvas` 强制转换为 `HTMLSourceCanvas` 以获取带 `requestPaint` 和 `captureElementImage` 成员的类型化属性。当浏览器缺少 API 时，`source.requestPaint()` 返回 `false`；当 API 被禁用时，纹理上传器在第一次渲染时抛出错误。

当 API 缺失时，第一次上传会抛出 WebGL 或 WebGPU 上的错误：`[HTMLSource] WebGLRenderingContext.texElementImage2D is not available...` 或 `[HTMLSource] GPUQueue.copyElementImageToTexture is not available...`。

### 使用 HTMLSource 的实时元素

```ts
const form = document.createElement("form");
app.canvas.appendChild(form); // canvas 的直接子元素

const source = new HTMLSource({ resource: form });
const sprite = Sprite.from(source);
```

元素必须是渲染器的 `<canvas>` 的直接子元素；源从 `resource.parentElement`（或传递 `canvas`）推断所属的 canvas。使用默认值时，它在 canvas 上设置 `layoutsubtree`，监听 canvas `paint` 事件，并请求一次初始绘制。`source.isReady` 在第一次绘制到达之前为 `false`，然后为 `true`。当 `autoUpdate` 为 `false` 时，它立即为 `true`。`resourceWidth`/`resourceHeight` 报告元素的实际像素大小（`offsetWidth`/`offsetHeight`）。

### 使用 requestPaint 进行连续动画

```ts
const source = new HTMLSource({ resource: clock, autoRequestPaint: false });
const sprite = Sprite.from(source);

app.ticker.add(() => {
  clock.textContent = new Date().toLocaleTimeString();
  source.requestPaint(); // 本帧重新捕获 DOM
});
```

浏览器仅在按需时才重绘 canvas 子元素。对于内容每帧变化的元素，设置 `autoRequestPaint: false` 并在您的 ticker 中调用 `source.requestPaint()` 以按您的计划驱动重绘。

### 使用 ElementImageSource 的不可变快照

```ts
import { ElementImageSource } from "pixi.js/html-source";
import type { HTMLSourceCanvas } from "pixi.js/html-source";

const canvas = app.canvas as HTMLSourceCanvas;
const snapshot = canvas.captureElementImage!(element);

const source = new ElementImageSource({ resource: snapshot, autoClose: true });
const sprite = Sprite.from(source);
```

`captureElementImage()` 将元素的当前像素冻结为不可变的 `ElementImage`。没有所属的 canvas，没有 `paint` 监听器，也没有重绘生命周期，因此源在构造时即可准备就绪。当您需要一个在其元素之外生存的冻结副本或需要传递时（过渡、“碎裂”或轨迹效果），请使用它。完成时调用 `snapshot.close()` 释放快照，或传递 `autoClose: true` 以让源在 `destroy()` 时关闭它。

### 在精灵、纹理或网格上使用来源

两者都是普通的 `TextureSource`。使用 `Sprite.from(source)` / `Texture.from(source)` 将其包装，将其帧或切片为子纹理，或将其映射到网格：

```ts
import { Rectangle, Texture } from "pixi.js";

// 渲染元素的 64x64 切片。
const chunk = new Texture({
  source,
  frame: new Rectangle(0, 0, 64, 64),
});

// 映射到几何图形（例如透视扭曲）。
const mesh = new PerspectiveMesh({ texture: Texture.from(source) /* ... */ });
```

### 自动检测和优先级

```ts
// 仅在最后手段时解析为 HTMLSource（元素）或 ElementImageSource（快照）。
const sprite = Sprite.from(elementAlreadyInTheCanvas);
```

传递给 `Texture.from`/`Sprite.from` 的通用 HTML 元素或 `ElementImage` 在纹理来源优先级最低（`-10`）时解析为这些来源，因此它们仅在没有任何内置来源处理的资源时才会声明。图像、视频和 canvas 元素被故意拒绝；它们有专门的、更快的来源。当您需要选项（`autoUpdate`、`autoClose`）或非 HTML 元素（如 SVG）时，请显式构造来源。

## 常见错误

### [高] 从 pixi.js 而不是 pixi.js/html-source 导入

错误：

```ts
import { HTMLSource } from "pixi.js"; // 未从核心入口导出
```

正确：

```ts
import { HTMLSource } from "pixi.js/html-source";
```

`HTMLSource`、`ElementImageSource` 和 `'html'` 上传器仅存在于 `pixi.js/html-source` 中。从该路径导入会注册扩展；该模块被标记为副作用，因此即使您只导入一个类，打包器也会保留注册。

### [高] 假设浏览器 API 已启用

HTML-in-Canvas 提案默认未发布。如果 API 被禁用，上传器在第一次渲染时会抛出错误。先进行特性检测：

```ts
const canvas = app.canvas as HTMLSourceCanvas;
if (!canvas.requestPaint) {
  // 回退到静态图像、DOMContainer 叠加或消息。
}
```

### [中] 元素不是 canvas 的直接子元素

```ts
document.body.appendChild(form); // 错误的父元素
const source = new HTMLSource({ resource: form }); // 抛出
```

`HTMLSource` 要求元素是所属 canvas 的直接子元素（`app.canvas.appendChild(form)`），否则会抛出错误。在构造源之前将元素附加到 canvas，或传递 `canvas` 选项。

### [中] 期望实时元素在不需要 requestPaint 的情况下更新

非动画元素在浏览器 `paint` 事件上自动更新（`autoUpdate: true`）。每帧变化的內容不会重新上传，除非有东西触发绘制；使用 `source.requestPaint()` 每帧驱动（设置 `autoRequestPaint: false`）。

### [中] 关闭仍在使用的 ElementImage

```ts
const source = new ElementImageSource({ resource: snapshot, autoClose: true });
const other = new ElementImageSource({ resource: snapshot }); // 共享快照

source.destroy(); // 关闭快照 — `other` 现在是 use-after-free
```

仅在源独占拥有快照时设置 `autoClose: true`。对于共享快照，保留 `autoClose` 不用，并在最后一个源销毁后调用 `snapshot.close()` 以释放内存。

## 清理

```ts
source.destroy();
```

`HTMLSource.destroy()` 断开 canvas `paint` 监听器并使其 canvas 引用为 `null`。`ElementImageSource.destroy()` 在设置 `autoClose` 时关闭快照；否则，您需要自己调用 `snapshot.close()` 以释放内存。

## API 参考

- [HTMLSource](https://pixijs.download/release/docs/rendering.HTMLSource.html.md)
- [HTMLSourceOptions](https://pixijs.download/release/docs/rendering.HTMLSourceOptions.html.md)
- [ElementImageSource](https://pixijs.download/release/docs/rendering.ElementImageSource.html.md)
- [ElementImageSourceOptions](https://pixijs.download/release/docs/rendering.ElementImageSourceOptions.html.md)
- [HTMLSourceCanvas](https://pixijs.download/release/docs/rendering.HTMLSourceCanvas.html.md)
- [ElementImage](https://pixijs.download/release/docs/rendering.ElementImage.html.md)
