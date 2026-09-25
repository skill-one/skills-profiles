`DOMContainer` 将 HTML 元素定位在 PixiJS 画布之上，并从场景图中驱动其 CSS 变换。用于原生输入、iframe、视频或需要跟随显示对象位置的丰富 HTML。默认的 `pixi.js` 浏览器捆绑包会自动注册 `DOMPipe`；自定义构建需要添加一个副作用 `import 'pixi.js/dom'`。

> 在 PixiJS v8 中，`DOMContainer` 被标记为 EXPERIMENTAL。API 可能在次要版本之间发生变化。

假设熟悉 `pixijs-scene-core-concepts`。`DOMContainer` 继承自 `ViewContainer`，因此它是一个叶节点：不要在它里面嵌套 PixiJS 子元素。将 DOM 内容嵌套在 HTML 元素本身内部，或者将多个 `DOMContainer` 实例包裹在一个 `Container` 中。在 Web Workers 中不可用；工作线程没有 DOM 可以叠加。

## 快速入门

```ts
import "pixi.js/dom";

const input = document.createElement("input");
input.type = "text";
input.placeholder = "Enter name...";

const dom = new DOMContainer({
  element: input,
  anchor: 0.5,
});
dom.position.set(app.screen.width / 2, app.screen.height / 2);

app.stage.addChild(dom);
```

**相关技能：** `pixijs-scene-core-concepts`（场景图基础）、`pixijs-scene-container`（包裹多个 DOM 叠加层）、`pixijs-events`（画布与 DOM 上的指针处理）、`pixijs-accessibility`（屏幕阅读器叠加层）。

## 构造函数选项

所有 `Container` 选项（`position`、`scale`、`tint`、`label`、`filters`、`zIndex` 等）在此处也有效——参见 `skills/pixijs-scene-core-concepts/references/constructor-options.md`。

`DOMContainerOptions` 添加的叶节点特定选项：

| 选项    | 类型                  | 默认                         | 描述                                                                                                                                                                    |
|---------|---------------------|-----------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `element` | `HTMLElement`         | `document.createElement('div')` | 容器驱动的 HTML 元素。任何元素都有效：`input`、`textarea`、`iframe`、`video`、`div` 等。如果省略，将创建一个裸的 `<div>`。                        |
| `anchor`  | `PointData \| number` | `0`                         | 元素相对于其自身尺寸的起源。`0` 是左上角，`0.5` 是居中，`1` 是右下角。单个数字设置两个轴；`{ x, y }` 独立设置每个轴。 |

`tint`、`filters`、`mask` 和 `blendMode` 被接受（继承自 `Container`），但没有视觉效果——DOM 元素位于 WebGL/WebGPU 管道之外。通过 CSS 样式这些效果。

## 核心模式

### 设置和副作用导入

```ts
import "pixi.js/dom";
import { DOMContainer } from "pixi.js";
```

或者使用注册管道并重新导出类的组合导入：

```ts
import { DOMContainer } from "pixi.js/dom";
```

默认的 `pixi.js` 浏览器捆绑包通过 `browserAll.ts` 已经导入 `pixi.js/dom`，因此 `DOMContainer` 在典型的浏览器应用中开箱即用。只有在设置 `skipExtensionImports: true`（自定义构建）或运行在非浏览器捆绑包下时，才需要显式的 `import 'pixi.js/dom'` 行。

### 变换、锚点和 alpha

```ts
const dom = new DOMContainer({
  element: document.createElement("div"),
  anchor: 0.5,
});
dom.position.set(400, 300);
dom.scale.set(1.5);
dom.rotation = Math.PI / 8;
dom.alpha = 0.5;
```

`DOMContainer` 的变换会传播到元素作为 CSS `transform`。`anchor` 会将元素的起源相对于其自身尺寸移动：`0` 是左上角，`0.5` 是居中，`1` 是右下角。单个数字设置两个轴；对象 `{ x, y }` 独立设置每个轴。`alpha`（包括继承的父 alpha）每帧都会写入到元素的 `style.opacity`。

如果没有提供 `element`，默认会创建一个 `<div>`。

### 直接样式化元素

```ts
const panel = document.createElement("div");
panel.innerHTML = "<h2>Score</h2><p>1500</p>";
panel.style.color = "white";
panel.style.fontFamily = "Arial";
panel.style.pointerEvents = "none";

const dom = new DOMContainer({ element: panel });
dom.position.set(50, 50);
app.stage.addChild(dom);
```

PixiJS 不会干扰元素的 CSS 样式。共享的根 `<div>` 设置为 `pointer-events: none`，每个附加元素默认为 `pointer-events: auto`。对于纯装饰性叠加层，将 `pointer-events` 覆盖为 `none`，以便画布在它们下方仍然可以接收点击。

### 可见性和清理

```ts
dom.visible = false;
dom.visible = true;

dom.destroy();
```

设置 `visible = false` 或从场景图中移除 `DOMContainer` 会将元素从 DOM 中分离。恢复可见性会重新附加它。`destroy()` 会从其父节点中移除元素并清空内部引用；HTML 元素本身被保留，因此你可以将其重新附加到其他位置：

```ts
const element = dom.element;
dom.destroy();
document.body.appendChild(element);
```

### DOM 容器根

`DOMPipe` 使用一个具有 `z-index: 1000` 的共享根 `<div>` 来托管每个附加的元素。它作为 `app.domContainerRoot`（一个 `HTMLDivElement`）暴露。所有 `DOMContainer` 元素都渲染在画布内容之上；你不能在 PixiJS 绘制调用之间交错 DOM 元素。

在首次渲染且附加了 `DOMContainer` 时，管道会自动将根附加到画布的父节点。如果你需要显式、稳定的 DOM 树中的位置（例如，当画布与其他分层内容共享包装器时），可以自己将根附加到 `app.canvas` 旁边：

```ts
document.body.appendChild(app.canvas);
document.body.appendChild(app.domContainerRoot);
```

根使用绝对定位，其变换通过 `ResizeObserver` 从画布的 `getBoundingClientRect()` 重新计算，因此 CSS 缩放的画布无需额外工作即可保持对齐。

## 常见错误

### [MEDIUM] 自定义构建中缺少 `pixi.js/dom` 导入

默认浏览器捆绑包自动注册 `DOMPipe`，因此大多数应用不需要显式导入。只有在选择退出自动导入时才需要它：

```ts
await app.init({ skipExtensionImports: true });
// 现在必须自己添加：
import "pixi.js/dom";
```

在自定义构建下未注册时，`DOMContainer` 仍然可以导入，但渲染器没有管道来处理它；元素永远不会与场景图同步，也永远不会出现。

### [MEDIUM] 期望滤镜、遮罩或混合模式会影响 DOM 元素

错误：

```ts
const dom = new DOMContainer();
dom.filters = [new BlurFilter()];
```

正确：

```ts
dom.element.style.filter = "blur(4px)";
```

DOM 元素是 HTML 叠加层，通过 CSS 变换定位；它们存在于 WebGL/WebGPU 管道之外。PixiJS 滤镜、遮罩和混合模式对它们没有效果。直接在元素上使用 CSS 滤镜和 CSS `mix-blend-mode`。

### [MEDIUM] 不要在 DOMContainer 中嵌套子元素

错误：

```ts
const dom = new DOMContainer();
dom.addChild(new Sprite(texture));
```

正确：

```ts
const group = new Container();
group.addChild(dom, new Sprite(texture));
```

`DOMContainer` 继承自 `ViewContainer`，它设置 `allowChildren = false`。它是 PixiJS 场景图中的一个叶节点。对于 PixiJS 子元素，将 `DOMContainer` 与它们一起包裹在一个普通的 `Container` 中。对于嵌套的 HTML，嵌套在元素本身内部（`element.appendChild(...)`）。

### [LOW] 忘记设置锚点进行居中定位

默认锚点是 `(0, 0)`，将元素的左上角定位在容器的位置。对于在其场景图位置上居中一个 UI 元素，设置 `anchor: 0.5`：

```ts
const dom = new DOMContainer({ element: myElement, anchor: 0.5 });
dom.position.set(400, 300);
```

## API 参考

- [DOMContainer](https://pixijs.download/release/docs/scene.DOMContainer.html.md)
- [DOMContainerOptions](https://pixijs.download/release/docs/scene.DOMContainerOptions.html.md)
- [ViewContainer](https://pixijs.download/release/docs/scene.ViewContainer.html.md)
- [Container](https://pixijs.download/release/docs/scene.Container.html.md)
