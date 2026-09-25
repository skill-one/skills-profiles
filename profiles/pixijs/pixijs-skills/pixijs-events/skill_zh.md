PixiJS 的联邦事件系统在场景图中模拟 DOM 事件。将 `container.eventMode = 'static'` 设置为对象以启用，然后使用 `.on()`、`addEventListener()` 或 `onEventName` 属性处理器进行监听。移动事件仅在监听对象上触发；使用 `globalpointermove` 进行拖拽。

## 快速入门

```ts
const button = new Sprite(await Assets.load("button.png"));
button.eventMode = "static";
button.cursor = "pointer";
app.stage.addChild(button);

button.on("pointertap", (event) => {
  console.log("clicked at", event.global.x, event.global.y);
});

let dragging = false;
button.on("pointerdown", () => {
  dragging = true;
});
button.on("pointerup", () => {
  dragging = false;
});
button.on("pointerupoutside", () => {
  dragging = false;
});
button.on("globalpointermove", (event) => {
  if (dragging) button.parent.toLocal(event.global, undefined, button.position);
});
```

**相关技能：** `pixijs-accessibility`（屏幕阅读器 + 键盘）、`pixijs-scene-dom-container`（HTML 叠加层）、`pixijs-performance`（事件密集场景）。

## 核心模式

### eventMode 值

```ts
import { Sprite } from "pixi.js";

const sprite = new Sprite();

// 完全无交互；子元素也忽略
sprite.eventMode = "none";

// 默认。自身不交互；交互子元素仍然有效
sprite.eventMode = "passive";

// 仅在父元素交互时进行命中测试
sprite.eventMode = "auto";

// 标准交互：接收指针/鼠标/触摸事件
sprite.eventMode = "static";

// 类似静态，但在指针静止时从计时器触发合成事件
// （用于光标下方的动画对象）
sprite.eventMode = "dynamic";
```

为按钮、UI 元素和拖拽目标使用 `'static'`。仅对光标下移动且需要持续悬停更新的对象使用 `'dynamic'`。

使用 `isInteractive()` 检查对象是否可以接收事件：

```ts
sprite.eventMode = "static";
sprite.isInteractive(); // true

sprite.eventMode = "passive";
sprite.isInteractive(); // false
```

### 事件类型

指针事件（推荐用于跨设备兼容性）：`pointerdown`、`pointerup`、`pointerupoutside`、`pointermove`、`pointerover`、`pointerout`、`pointerenter`、`pointerleave`、`pointertap`、`pointercancel`。

鼠标事件：`mousedown`、`mouseup`、`mouseupoutside`、`mousemove`、`mouseover`、`mouseout`、`mouseenter`、`mouseleave`、`click`、`rightdown`、`rightup`、`rightupoutside`、`rightclick`、`wheel`。

触摸事件：`touchstart`、`touchend`、`touchendoutside`、`touchmove`、`touchcancel`、`tap`。每个触摸事件都携带从原生 `TouchEvent` 复制的 `altKey`、`ctrlKey`、`metaKey` 和 `shiftKey`，因此修饰键与鼠标或指针事件相同。

全局移动事件：`globalpointermove`、`globalmousemove`、`globaltouchmove`。这些事件在指针移动时始终触发，无论指针是否在监听对象上。

容器生命周期事件（无需 `eventMode`）：`added`、`removed`、`destroyed`、`childAdded`、`childRemoved`、`visibleChanged`。

### 监听风格

```ts
import { Sprite } from "pixi.js";

const sprite = new Sprite();
sprite.eventMode = "static";

// EventEmitter 风格（推荐）
const handler = (e) => console.log("clicked");
sprite.on("pointerdown", handler);
sprite.once("pointerdown", handler); // 一次性
sprite.off("pointerdown", handler);

// DOM 风格
sprite.addEventListener(
  "click",
  (event) => {
    console.log("Clicked!", event.detail);
  },
  { once: true },
);

// 属性处理器
sprite.onclick = (event) => {
  console.log("Clicked!", event.detail);
};
```

### 指针事件和事件冒泡

```ts
import { Sprite, Container } from "pixi.js";

const parent = new Container();
parent.eventMode = "static";

const child = new Sprite();
child.eventMode = "static";
parent.addChild(child);

child.on("pointerdown", (event) => {
  console.log("child pressed");
  event.stopPropagation(); // 防止父元素接收此事件
});

parent.on("pointerdown", () => {
  console.log("parent pressed (only if child did not stop propagation)");
});
```

### 捕获阶段事件

所有事件都支持通过在事件名后添加 `capture` 来支持捕获阶段（例如，`pointerdowncapture`、`clickcapture`）。捕获监听器在事件到达目标之前，在捕获阶段触发。

```ts
container.addEventListener(
  "pointerdown",
  (event) => {
    event.stopImmediatePropagation(); // 阻止事件到达子元素
  },
  { capture: true },
);
```

### 命中测试

当指针事件触发时，PixiJS 遍历显示树以找到指针下方的最高交互元素。遍历遵循以下规则：

- 容器上的 `eventMode = 'none'` 跳过该元素及其整个子树。
- 容器上的 `interactiveChildren = false` 跳过其子元素（容器本身仍可测试）。
- `hitArea` 覆盖基于边界的测试；仅检查形状。
- 不可见、不可渲染或不可测量的对象被跳过。

设置自定义 `hitArea` 以覆盖基于边界的测试。这还可以通过减少检查的几何形状来加快大型或复杂对象的命中测试：

```ts
import { Sprite, Rectangle, Circle, Polygon } from "pixi.js";

const sprite = new Sprite();
sprite.eventMode = "static";

// 矩形命中区域
sprite.hitArea = new Rectangle(0, 0, 100, 50);

// 圆形命中区域
sprite.hitArea = new Circle(50, 50, 40);

// 多边形命中区域
sprite.hitArea = new Polygon([0, 0, 100, 0, 50, 100]);

// 通过 contains() 进行自定义命中测试
sprite.hitArea = {
  contains(x: number, y: number): boolean {
    return x >= 0 && x <= 100 && y >= 0 && y <= 100;
  },
};
```

### 全局移动事件和拖拽

```ts
import { Sprite, FederatedPointerEvent } from "pixi.js";

const sprite = new Sprite();
sprite.eventMode = "static";
sprite.cursor = "grab";

let dragging = false;

sprite.on("pointerdown", (event: FederatedPointerEvent) => {
  dragging = true;
  sprite.cursor = "grabbing";
});

// globalpointermove 即使指针离开对象也会触发
sprite.on("globalpointermove", (event: FederatedPointerEvent) => {
  if (dragging) {
    sprite.position.set(event.global.x, event.global.y);
  }
});

sprite.on("pointerup", () => {
  dragging = false;
  sprite.cursor = "grab";
});

sprite.on("pointerupoutside", () => {
  dragging = false;
  sprite.cursor = "grab";
});
```

### 光标样式

基本用法为每个对象设置 `cursor` 属性。对于可重用光标，在事件系统中注册命名样式：

```ts
app.renderer.events.cursorStyles.default = "url('bunny.png'), auto";
app.renderer.events.cursorStyles.hover = "url('bunny_saturated.png'), auto";

sprite.eventMode = "static";
sprite.cursor = "hover"; // 使用注册的 'hover' 样式
```

光标样式可以是字符串（CSS 光标值）、对象（作为 CSS 样式应用）或函数（使用模式字符串调用）。

### 事件属性

`FederatedPointerEvent` 携带丰富的输入数据；更常用的字段是：

```ts
sprite.on("pointerdown", (event: FederatedPointerEvent) => {
  event.global; // 事件发生的场景空间点
  event.client; // 视口相对的 CSS 像素点
  event.offset; // 相对于目标容器在世界空间中的点（目前不支持）
  event.target; // 接收事件的容器
  event.currentTarget; // 正在运行监听器的容器

  event.pointerType; // 'mouse' | 'pen' | 'touch'
  event.pointerId; // 多点触控跟踪的唯一 ID
  event.isPrimary; // 多点触控手势中的第一个指针
  event.persistentDeviceId; // 始终为 0；用于 DOM PointerEvent 类型的兼容性
  event.pressure; // 0-1 的笔/触摸压力
  event.button; // 0 左键，1 中键，2 右键
  event.buttons; // 按住按钮的位掩码
  event.altKey; // 修饰键状态
  event.ctrlKey;
  event.shiftKey;
  event.metaKey;

  event.nativeEvent; // 底层的 DOM PointerEvent / MouseEvent / Touch
  event.preventDefault();
  event.stopPropagation();
  event.stopImmediatePropagation();
});
```

`FederatedWheelEvent` 添加 `deltaX`、`deltaY`、`deltaZ` 和 `deltaMode`。滚轮事件在指针命中测试的对象上触发。

### 事件特性

全局切换事件类别以优化性能：

```ts
await app.init({
  eventFeatures: {
    move: true, // 指针/鼠标/触摸移动事件
    globalMove: true, // 全局移动事件（globalpointermove 等）
    click: true, // 点击/轻点/按压事件
    wheel: true, // 鼠标滚轮事件
  },
});

// 或初始化后配置
app.renderer.events.features.globalMove = false;
```

### 性能技巧

- 在非交互子树上将 `eventMode = 'none'` 设置为完全跳过命中测试。
- 在仅容器本身需要交互的容器上将 `interactiveChildren = false` 设置为 `false`。
- 在大型或复杂对象上使用 `hitArea` 以将基于边界的命中测试替换为廉价的形状检查。
- 对静止元素使用 `'static'`；保留 `'dynamic'` 用于光标下移动或动画的对象。
- 通过 `eventFeatures`（例如，`globalMove: false`）禁用未使用的事件特性以减少每帧工作。

## 常见错误

### [高] 默认 eventMode 是 passive

错误：

```ts
const sprite = new Sprite(texture);
sprite.on("pointerdown", () => {
  console.log("clicked");
});
```

正确：

```ts
const sprite = new Sprite(texture);
sprite.eventMode = "static";
sprite.on("pointerdown", () => {
  console.log("clicked");
});
```

默认 `eventMode` 是 `'passive'`，这意味着对象本身不会接收事件。您必须显式设置 `eventMode` 为 `'static'` 或 `'dynamic'`，然后监听器才会触发。

### [高] buttonMode 已移除；使用 cursor

错误：

```ts
sprite.interactive = true;
sprite.buttonMode = true;
```

正确：

```ts
sprite.eventMode = "static";
sprite.cursor = "pointer";
```

`buttonMode` 在 v8 中已移除。使用 `cursor = 'pointer'` 在悬停时显示手形光标。`interactive = true` 仍然作为 `eventMode = 'static'` 的别名工作，但 `eventMode` 更受推荐。

### [高] 移动事件仅在 v8 中在对象上触发

错误：

```ts
sprite.eventMode = "static";
sprite.on("pointermove", (event) => {
  // 期望在所有地方触发；仅在 sprite 边界内触发
  updateDrag(event.global.x, event.global.y);
});
```

正确：

```ts
sprite.eventMode = "static";
sprite.on("globalpointermove", (event) => {
  // 在所有地方触发，即使在 sprite 边界外
  updateDrag(event.global.x, event.global.y);
});
```

在 v8 中，`pointermove`、`mousemove` 和 `touchmove` 仅在指针在显示对象上时触发。在 v7 中，它们在任何画布移动时都会触发。对于拖拽操作或全局跟踪，使用 `globalpointermove`、`globalmousemove` 或 `globaltouchmove`。

### [中] 光标不继承自父元素

在父容器上设置 `cursor` 对其子元素没有影响。只有直接命中目标的 `cursor` 值会被应用。

```ts
// 这不会使子元素显示指针光标
parent.cursor = "pointer";

// 每个交互子元素需要自己的光标
child.eventMode = "static";
child.cursor = "pointer";
```

如果您希望所有子元素具有统一的光标，请单独为每个交互子元素设置 `cursor`，或在父元素上设置 `hitArea` 并使子元素非交互。
