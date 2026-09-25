`Container` 是 PixiJS v8 场景图中的通用节点。它包含子节点，并对其整个子树应用变换、透明度、色调和混合模式。你创建的每个显示对象要么是你要构建分支的 `Container`，要么是你要嵌套在其中的叶子节点（`Sprite`、`Graphics`、`Text`、`Mesh`）。

假设你熟悉 `pixijs-scene-core-concepts`。

## 快速入门

```ts
const group = new Container({
  label: "hero-group",
  x: 200,
  y: 150,
  sortableChildren: true,
});

const body = new Sprite(await Assets.load("body.png"));
const head = new Sprite(await Assets.load("head.png"));
head.position.set(0, -40);
head.zIndex = 1;

group.addChild(body, head);
group.pivot.set(group.width / 2, group.height / 2);
group.scale.set(1.5);

app.stage.addChild(group);
```

**相关技能：** `pixijs-scene-core-concepts`（场景图心智模型、遮罩、图层、渲染组）、`pixijs-scene-sprite` / `pixijs-scene-graphics` / `pixijs-scene-text` / `pixijs-scene-mesh`（可以嵌套在容器中的叶子对象）、`pixijs-events`（`eventMode`、命中测试）、`pixijs-math`（矩阵、toGlobal/toLocal 详情）、`pixijs-performance`（`cacheAsTexture`、剔除、渲染组）。

## 核心模式

### 构造函数选项

```ts
const container = new Container({
  label: "world",
  x: 100,
  y: 50,
  scale: 2,
  rotation: Math.PI / 4,
  alpha: 0.8,
  visible: true,
  tint: 0xffaa00,
  blendMode: "add",
  sortableChildren: true,
  isRenderGroup: true,
  origin: { x: 0, y: 0 },
  boundsArea: new Rectangle(0, 0, 1920, 1080),
});
```

所有 `Container` 选项（`position`、`scale`、`tint`、`label`、`filters`、`zIndex` 等）在这里也是有效的——参见 `skills/pixijs-scene-core-concepts/references/constructor-options.md`。

`Container` 构造函数使用 `assignWithIgnore` 将选项对象中的每个字段批量复制到实例上，除了 `children`、`parent` 和 `effects`。`Container` 的任何公共属性都是有效的构造函数选项：`cullable`、`cullArea`、`mask`、`filterArea`、`eventMode`、`hitArea` 等。上面的选项块分组了最常见的选项；参见上面的共享参考以获取完整列表。

`isRenderGroup: true` 将容器提升为其自己的渲染组，以便其变换在 GPU 上应用，而不是在 CPU 上为每个子节点重新计算。用于稳定的子树（大型静态世界、UI 图层）。不要过度使用；大多数场景不需要显式的渲染组，太多会损害性能。在提升之前进行性能分析。参见 `pixijs-scene-core-concepts/references/scene-management.md`。

`sortableChildren: true` 会导致子节点在下次渲染时按 `zIndex` 重新排序。参见下面的 `zIndex`。

`origin` 是一个 v8 变换辅助工具：一个 `ObservablePoint`，它充当旋转/缩放中心，**而不移动容器**。`pivot` 会移动父空间中本地原点的投影（因此改变它会移动对象），而 `origin` 保持位置不变，只是在指定的本地点周围旋转/缩放。接受 `PointData`、单个数字（应用于两个轴）或可以通过 `container.origin.set(x, y)` 实时设置。在同一容器上同时设置 `pivot` 和 `origin` 会导致复合行为，不建议这样做；选择其中一个。

`boundsArea` 强制 `getBounds()` 返回一个固定的矩形，而不是递归测量子节点；对于具有数百个廉价、可预测子节点的容器来说，这是一个性能提升。

`cullable` 和 `cullArea` 是有效的构造函数选项（`assignWithIgnore` 遍历将它们像任何其他字段一样复制），但由于剔除设置是性能问题而不是场景图问题，因此它们在 `pixijs-performance` 中有文档记录。

### 叶子节点与容器

```ts
const parent = new Container();
const sprite = new Sprite(texture);

parent.addChild(sprite);
```

只有 `Container`（以及像 `RenderLayer` 这样的旨在包含子节点的子类）应该有子节点。`Sprite`、`Graphics`、`Text`、`Mesh`、`ParticleContainer` 粒子和 `DOMContainer` 内容在 PixiJS v8 中按约定是叶子节点。当你需要分组时，请将它们包装在 `Container` 中：给容器分配布局逻辑，并保持叶子节点为纯视觉数据。向叶子节点添加子节点会记录弃用警告，并且计划在未来版本中变为硬错误。

### 添加和移除子节点

```ts
const parent = new Container();

parent.addChild(a, b, c);
parent.addChildAt(d, 0);
parent.swapChildren(a, b);
parent.setChildIndex(c, 0);

parent.removeChild(b);
parent.removeChildAt(0);
parent.removeChildren();

parent.removeChildren(0, 2);
```

`addChild` 接受任意数量的子节点，并返回第一个。子节点按数组顺序渲染：索引 0 是最先绘制的（在后面），最后一个索引是最后绘制的（在前面）。`addChildAt` 在特定索引处插入；`setChildIndex` 移动现有子节点；`swapChildren` 交换两个子节点的位置。

`removeChildren(beginIndex?, endIndex?)` 移除一个切片并返回移除的数组。

使用 `addChildAt` 将已属于同一容器的子节点静默移动到新索引。不会触发 `added` / `childAdded` / `removed` / `childRemoved` 事件，因为父子关系没有改变。事件仅在子节点来自不同的父节点（或没有父节点）时触发。

要保留世界变换的重新父化（因此子节点不会在视觉上跳跃），请使用 `reparentChild` / `reparentChildAt`。要在原地交换子节点并复制旧子节点的本地变换，请使用 `replaceChild`。

### 变换属性

```ts
const obj = new Container();

obj.x = 100;
obj.y = 200;
obj.position.set(100, 200);

obj.scale.set(2);
obj.scale = 2;

obj.rotation = Math.PI / 4;
obj.angle = 45;

obj.pivot.set(50, 50);
obj.skew.set(0.1, 0.2);

obj.alpha = 0.5;
obj.tint = 0xff0000;
obj.visible = false;
obj.renderable = false;
```

- `position`、`scale`、`pivot`、`skew` 是 `ObservablePoint`。分配 `scale = 2` 是有效的，并设置两个轴。
- `rotation` 是弧度；`angle` 是度数；它们是别名，保持同步。
- `pivot` 设置本地空间中的点，该点映射到父空间中的 `position`；改变它会同时移动和旋转容器。
- `alpha` 和 `tint` 沿着子节点向下乘。`blendMode` 应用于此容器的绘制指令。
- `visible = false` 跳过渲染和变换更新。`renderable = false` 跳过渲染，但仍然更新变换（当你需要 `getBounds()` 或命中测试而不绘制时使用）。

### zIndex 和 sortableChildren

```ts
const world = new Container({ sortableChildren: true });

const ground = new Sprite(groundTexture);
ground.zIndex = 0;

const player = new Sprite(playerTexture);
player.zIndex = 10;

const ui = new Sprite(uiTexture);
ui.zIndex = 100;

world.addChild(ground, player, ui);
```

当 `sortableChildren` 为 `true` 时，容器在下次渲染之前会按 `zIndex` 重新排序其子节点。更改任何子节点的 `zIndex` 会自动将父节点标记为需要排序。只排序你需要排序的内容；关闭 `sortableChildren` 更便宜。如果你想要完全手动控制，在更改 `zIndex` 值后自己调用 `container.sortChildren()`。

对于与层次结构解耦的渲染顺序控制（子节点保持其逻辑父节点用于变换，但在不同的 z 值渲染），请使用 `RenderLayer`。参见 `pixijs-scene-core-concepts/references/scene-management.md`。

### 边界和坐标转换

```ts
const bounds = container.getBounds();
console.log(bounds.x, bounds.y, bounds.width, bounds.height);

const rect = container.getBounds().rectangle;

const local = new Point(10, 20);
const world = container.toGlobal(local);
const backToLocal = container.toLocal(world);

const selfPos = container.getGlobalPosition();
```

`getBounds()` 返回一个 `Bounds` 对象（不是 `Rectangle`）；它公开 `x`、`y`、`width`、`height` 和 `.rectangle` 获取器，用于需要实际 `Rectangle` 的 API。签名是 `getBounds(skipUpdate?: boolean, bounds?: Bounds)`——将第一个参数作为 `true` 以跳过强制变换更新，并将第二个参数作为可选的 `Bounds` 实例以避免分配新的实例。

`toGlobal(point)` 将此容器本地空间中的点转换为场景根空间。`toLocal(point, from?)` 从另一个容器的本地空间（如果 `from` 被省略，则从全局空间）转换。`getGlobalPosition()` 是 `parent.toGlobal(this._position)` 的简写。

### 尺寸

```ts
const sprite = new Sprite(texture);

sprite.setSize(200, 100);
const { width, height } = sprite.getSize();
```

`setSize` 调整 `scale`，使容器的边界适合请求的像素尺寸，一次操作完成。单独设置 `.width` 和 `.height` 也是有效的，但每个分配都会触发单独的边界重新计算；当更改两个轴时，请优先使用 `setSize`。

### 容器事件

```ts
const parent = new Container();

parent.on("childAdded", (child, container, index) => {
  console.log("added at", index, child.label);
});

parent.on("childRemoved", (child, container, index) => {
  console.log("removed from", index);
});

const child = new Container();
child.on("added", (newParent) => console.log("entered", newParent.label));
child.on("removed", (oldParent) => console.log("left", oldParent.label));
child.on("visibleChanged", (visible) => console.log("visible:", visible));
child.on("destroyed", (destroyed) => console.log("gone", destroyed.label));

parent.addChild(child);
```

| 事件            | 触发于                              | 参数                   |
| ---------------- | ------------------------------------- | --------------------------- |
| `childAdded`     | 接收子节点的父节点                  | `(child, container, index)` |
| `childRemoved`   | 失去子节点的父节点                   | `(child, container, index)` |
| `added`          | 被附加的子节点                      | `(parent)`                  |
| `removed`        | 被分离的子节点                      | `(parent)`                  |
| `destroyed`      | 被销毁的容器                       | `(container)`               |
| `visibleChanged` | `visible` 翻转的容器                 | `(visible)`                 |

这些是在 `Container` 的 `EventEmitter` 端发出的；不要将它们与 `pixijs-events` 的指针事件混淆。

`destroyed` 在内部清理后但在监听器移除之前触发，因此当你的处理程序运行时 `position`、`scale`、`pivot`、`origin`、`skew` 和 `parent` 已经被置空，`children` 已经被清空（长度为 0，但数组引用本身没有被置空）。在调用 `destroy()` 之前捕获你需要的容器数据，而不是在处理程序内部。

### 每帧更新 with onRender

```ts
const container = new Container();

container.onRender = (renderer) => {
  container.rotation += 0.01;
};

container.onRender = null;
```

`onRender` 在容器被渲染时每帧运行，并接收活动的 `Renderer`。用于轻量级动画或与特定容器绑定的每帧更新。在 v7 中，这种模式是通过重写 `updateTransform` 完成的，而 v8 中不再每帧运行。将 `onRender = null` 以分离回调。

### 查找和从父节点移除

```ts
const player = world.getChildByLabel("player");
const enemies = world.getChildrenByLabel(/enemy-\d+/, true);

const bounds = hud.getLocalBounds();

oldSprite.removeFromParent();
```

- `getChildByLabel(label, deep?)` — 按字符串或 `RegExp` 首次匹配。传递 `true` 以进行递归搜索。
- `getChildrenByLabel(label, deep?, out?)` — 所有匹配项。接受一个可选的可重用输出数组。
- `getLocalBounds()` — 此容器自己的坐标空间中的边界，忽略父节点变换。对于自包含布局数学，比 `getBounds()` 更便宜。
- `removeFromParent()` — 从当前父节点分离 `this`（如果已经无父节点则为空操作）。

### 销毁

```ts
container.destroy();

container.destroy({
  children: true,
  texture: true,
  textureSource: true,
});

console.log(container.destroyed);
```

默认情况下 `destroy()` 将此容器与其父节点断开连接并销毁其自身状态。传递 `{ children: true }` 以递归销毁每个后代；这是销毁整个子树的常用调用。`texture: true` 和 `textureSource: true` 还会销毁叶子子节点引用的 GPU 资源（对于你为它们加载纹理的精灵很有用）。如果 `cacheAsTexture` 是开启的，则在销毁之前使用 `container.cacheAsTexture(false)` 禁用它。

## 常见错误

### [CRITICAL] 向叶子场景对象添加子节点

错误：

```ts
const sprite = new Sprite(texture);
const overlay = new Sprite(overlayTexture);
sprite.addChild(overlay);
```

正确：

```ts
const group = new Container();
const sprite = new Sprite(texture);
const overlay = new Sprite(overlayTexture);
group.addChild(sprite, overlay);
```

精灵、图形、文本和网格是叶子节点。现在向它们添加子节点会记录弃用警告，并在未来版本中变为错误。当你需要分组时，请始终将它们包装在 `Container` 中。

### [HIGH] 期望 getBounds() 返回 Rectangle

错误：

```ts
const rect = container.getBounds();
rect.contains(x, y); // TypeError: contains is not a function
```

正确：

```ts
const rect = container.getBounds().rectangle;
rect.contains(x, y);

const bounds = container.getBounds();
console.log(bounds.width, bounds.height);
```

`getBounds()` 在 v8 中返回一个 `Bounds` 实例。其基本获取器（`x`、`y`、`width`、`height`）有效，但对于 `.contains()` 或需要 `Rectangle` 的 API，请读取 `.rectangle` 属性。

### [HIGH] 使用 cacheAsBitmap 而不是 cacheAsTexture

错误：

```ts
container.cacheAsBitmap = true;
```

正确：

```ts
container.cacheAsTexture(true);
```

`cacheAsBitmap`（v7 属性）在 v8 中重命名为 `cacheAsTexture()`（一个方法）。在调用 `destroy()` 之前始终禁用它。

### [MEDIUM] 使用 container.name 而不是 container.label

`name` 在 v8 中重命名为 `label`。旧属性仍然作为弃用别名工作；`getChildByLabel` 是 v8 中按名称查找子节点的方法。

### [MEDIUM] 在同一容器上设置 pivot 和 origin

Pivot 会移动父空间中本地原点的投影（作为改变旋转中心的副作用移动对象）。Origin 改变旋转/缩放中心而不移动。在同一容器上同时设置两者会产生意外的复合行为；选择其中一个。

## API 参考

- [Container](https://pixijs.download/release/docs/scene.Container.html.md)
- [ContainerOptions](https://pixijs.download/release/docs/scene.ContainerOptions.html.md)
- [ViewContainer](https://pixijs.download/release/docs/scene.ViewContainer.html.md)
- [Bounds](https://pixijs.download/release/docs/rendering.Bounds.html.md)
- [Point](https://pixijs.download/release/docs/maths.Point.html.md)
- [ObservablePoint](https://pixijs.download/release/docs/maths.ObservablePoint.html.md)
- [RenderGroup](https://pixijs.download/release/docs/rendering.RenderGroup.html.md)
