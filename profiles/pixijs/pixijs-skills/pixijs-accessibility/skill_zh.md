通过 PixiJS 的 AccessibilitySystem 启用屏幕阅读器和键盘导航。该系统创建一个覆盖在可访问容器上的不可见阴影 DOM 覆盖层，以便辅助技术可以发现并激活它们。

## 快速入门

```ts
const button = new Sprite(await Assets.load("button.png"));
button.accessible = true;
button.accessibleTitle = "Play game";
button.accessibleHint = "Starts a new game session";
button.eventMode = "static";
button.tabIndex = 0;
app.stage.addChild(button);

app.renderer.accessibility.setAccessibilityEnabled(true);

button.on("pointertap", () => startGame());
```

**相关技能：** `pixijs-events` (指针/点击处理器), `pixijs-scene-dom-container` (画布上的 HTML 元素), `pixijs-application` (初始化选项)。

**要点：**

- 默认情况下，系统只有在用户按下 Tab 键后才会激活。在应用程序初始化中设置 `enabledByDefault: true` 以立即激活。
- 在移动设备上，系统创建一个隐藏的触摸钩；屏幕阅读器焦点会激活整个会话的可访问性。
- AccessibilitySystem 需要主线程；它在 Web Worker 中不可用。

## 核心模式

### 容器可访问属性

```ts
import { Container, Sprite } from "pixi.js";

const container = new Container();
container.accessible = true;
container.accessibleTitle = "Navigation menu";
container.accessibleHint = "Contains links to other pages";
container.eventMode = "static"; // required for custom tabIndex to apply
container.tabIndex = 0;
container.accessibleType = "div"; // defaults to 'button'

const sprite = new Sprite();
sprite.accessible = true;
sprite.accessibleTitle = "Close dialog";
sprite.accessibleText = "X"; // text content of the shadow div
sprite.eventMode = "static";
sprite.tabIndex = 1;
```

任何容器上可用的属性：

- `accessible` (布尔值) - 启用可访问覆盖的 div
- `accessibleTitle` (字符串) - 在阴影 div 上设置 `title` 属性
- `accessibleHint` (字符串) - 设置 `aria-label` 属性
- `accessibleText` (字符串) - 设置阴影 div 的内部文本内容
- `accessibleType` (字符串) - 阴影元素的 HTML 标签，默认为 `'button'`
- `tabIndex` (数字) - 键盘导航的 Tab 顺序（仅当 `interactive` 为 true / `eventMode` 为 `'static'` 或 `'dynamic'` 时应用）
- `accessibleChildren` (布尔值，默认 `true`) - 当为 `false` 时，阻止子容器可访问
- `accessiblePointerEvents` (字符串) - 阴影 div 的 CSS `pointer-events` 值

### 自定义 Tab 顺序

给每个可访问容器分配一个 `tabIndex` 以控制辅助技术遍历它们的顺序。较高的数字会出现在后面；相等的数字会回退到场景图顺序。

```ts
menuButton.accessible = true;
menuButton.eventMode = "static";
menuButton.tabIndex = 1;

playButton.accessible = true;
playButton.eventMode = "static";
playButton.tabIndex = 2;

settingsButton.accessible = true;
settingsButton.eventMode = "static";
settingsButton.tabIndex = 3;
```

`tabIndex` 仅在容器为 `interactive` (`eventMode` 为 `'static'` 或 `'dynamic'`) 时才会转发到阴影 div。如果没有，系统会将 div 的 tabIndex 限制回 `0`，并且您设置的顺序将被忽略。

### 程序化控制

```ts
import { Application } from "pixi.js";

const app = new Application();
await app.init({ width: 800, height: 600 });

// 在运行时启用可访问性
app.renderer.accessibility.setAccessibilityEnabled(true);

// 检查当前状态
console.log(app.renderer.accessibility.isActive);
console.log(app.renderer.accessibility.isMobileAccessibility);

// 完整的初始化选项：
await app.init({
  accessibilityOptions: {
    enabledByDefault: true, // 立即激活（默认：false）
    debug: true, // 使覆盖的 div 可见（默认：false）
    activateOnTab: true, // Tab 键激活系统（默认：true）
    deactivateOnMouseMove: false, // 鼠标移动时保持激活（默认：true）
  },
});
```

该系统也可以在创建应用程序之前通过静态默认值进行配置：

```ts
import { AccessibilitySystem, Application } from "pixi.js";

AccessibilitySystem.defaultOptions.enabledByDefault = true;
AccessibilitySystem.defaultOptions.deactivateOnMouseMove = false;

const app = new Application();
await app.init();
```

### 处理可访问交互

```ts
import { Sprite } from "pixi.js";

const button = new Sprite();
button.eventMode = "static";
button.accessible = true;
button.accessibleTitle = "Submit form";
button.tabIndex = 0;

// 屏幕阅读器通过阴影 DOM 元素触发点击/点击事件
button.on("pointertap", () => {
  submitForm();
});
```

当可访问性激活时，并且用户通过 Enter/Space 键或屏幕阅读器操作激活阴影 div，系统会向相应的容器派发 `click`、`pointertap` 和 `tap` 联邦事件。阴影 div 的焦点会派发 `mouseover`，焦点移出会派发 `mouseout`。`eventMode` 和 `accessible` 都应设置以获得完整的键盘和指针支持。

## 常见错误

### [中等] 期望在未按下 Tab 键的情况下激活可访问性

AccessibilitySystem 直到用户按下 Tab 键（或在移动设备上聚焦触摸钩）才会创建其 DOM 覆盖层。如果您的应用程序需要立即启用可访问性：

```ts
const app = new Application();
await app.init({
  accessibilityOptions: {
    enabledByDefault: true,
  },
});
```

或在运行时：

```ts
app.renderer.accessibility.setAccessibilityEnabled(true);
```

如果没有这些之一，自动可访问性测试工具将找不到覆盖元素。

### [中等] 未设置 accessibleTitle 而设置 accessible

错误：

```ts
const sprite = new Sprite();
sprite.accessible = true;
// 未设置标题或提示
```

正确：

```ts
const sprite = new Sprite();
sprite.accessible = true;
sprite.accessibleTitle = "Play button";
sprite.accessibleHint = "Click to start the game";
```

具有 `accessible = true` 但没有 `accessibleTitle` 或 `accessibleHint` 的容器会获得 `"container {tabIndex}"` 的回退标题。屏幕阅读器将宣布这个通用标签，没有任何有用的上下文。始终至少提供 `accessibleTitle`。

### [中等] 移动鼠标时可访问性会失效

默认情况下，`deactivateOnMouseMove` 为 `true`。Tab 激活后的任何鼠标移动都会使覆盖层失效。这是设计上的（假设仅使用键盘的用户不使用鼠标），但它使使用鼠标进行测试变得令人沮丧。

```ts
await app.init({
  accessibilityOptions: {
    deactivateOnMouseMove: false,
  },
});
```

### [中等] 在自定义构建中未导入可访问性扩展

在使用 `skipExtensionImports: true` 进行自定义构建时，可访问性扩展不会自动注册。您必须显式导入它：

```ts
import "pixi.js/accessibility";
import { Application } from "pixi.js";

const app = new Application();
await app.init({ skipExtensionImports: true });
```

如果没有这个导入，`app.renderer.accessibility` 将为 undefined，并且不会创建阴影 DOM 层。

## API 参考

- [AccessibilitySystem](https://pixijs.download/release/docs/accessibility.AccessibilitySystem.html.md)
- [AccessibilitySystemOptions](https://pixijs.download/release/docs/accessibility.AccessibilitySystemOptions.html.md)
- [AccessibilityOptions](https://pixijs.download/release/docs/accessibility.AccessibilityOptions.html.md)
- [AccessibleOptions](https://pixijs.download/release/docs/accessibility.AccessibleOptions.html.md)
- [PointerEvents](https://pixijs.download/release/docs/accessibility.PointerEvents.html.md)
