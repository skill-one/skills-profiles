这项技能是所有 `pixijs-scene-*` 组件共同参考的共享心智模型。它解释了 PixiJS v8 中的场景图是什么，`Container` 与组件的区别，以及每个概念所处的位置。它不会深入探讨任何单个 API；它只是将各个部分组织起来，并指向执行该功能的技能或参考文件。

## 快速入门

```ts
const world = new Container({ isRenderGroup: true });
app.stage.addChild(world);

const hero = new Container({ label: "hero" });
hero.addChild(new Sprite(bodyTexture));
hero.addChild(new Sprite(faceTexture));
world.addChild(hero);

const mask = new Graphics().rect(0, 0, 800, 600).fill(0xffffff);
world.mask = mask;
world.addChild(mask);

hero.position.set(world.width / 2, world.height / 2);
```

**相关技能：** `pixijs-scene-container`（Container API 详细说明）、组件技能（`pixijs-scene-sprite`、`pixijs-scene-graphics`、`pixijs-scene-text`、`pixijs-scene-mesh`、`pixijs-scene-particle-container`、`pixijs-scene-dom-container`、`pixijs-scene-gif`）、`pixijs-events`（命中测试遍历场景图）、`pixijs-performance`（缓存、剔除、渲染组）、`pixijs-math`（矩阵、toGlobal/toLocal 详细说明）。

## 核心概念

### 场景图是什么

PixiJS 的场景图是以 `app.stage` 为根节点的显示对象树。每个节点都有一个父节点，相对于父节点的变换（位置、缩放、旋转、锚点、倾斜），以及可选的视觉状态（透明度、色调、混合模式、可见性）。每一帧渲染器都会遍历这棵树，合成变换和视觉状态到世界空间，剔除屏幕外的对象，并发出绘制调用。场景图既是布局模型也是渲染顺序：较早的兄弟节点会在较晚的兄弟节点之后绘制。

v8 中的每个显示对象都是 `Container` 的子类。早期版本中的 `DisplayObject` 已被移除。

### 容器与组件（关键）

树中有两种角色：

- **容器**：包含子节点的节点。对于需要分组、定位或变换其他节点的节点，使用 `Container`（或 `RenderLayer`）。
- **组件**：绘制内容且没有子节点的节点。使用 `Sprite`、`Graphics`、`Text`、`Mesh`、`ParticleContainer` 的 `Particle`、`DOMContainer` 或 `GifSprite` 作为组件。

在 PixiJS v8 中，组件不能有子节点。向 `Sprite` / `Graphics` / `Text` / `Mesh` 添加子节点会记录弃用警告，并计划变为硬错误。规则是：**需要子节点的节点使用 `Container`；不要在组件场景对象内嵌套子节点。** 如果需要将组件与其他组件组合，请将它们包裹在 `Container` 中。

这种区别是为什么 `pixijs-scene-*` 技能按这种方式划分：`pixijs-scene-container` 覆盖分组节点，每个组件都有自己的技能专注于其绘制行为。

### 变换与坐标空间

每个容器都从其 `position`、`scale`、`rotation`、`pivot` 和 `skew` 组合出一个 `localTransform`（一个 `Matrix`）。渲染器将父节点的局部变换相乘，生成 `worldTransform`（如果链中有渲染组，还会生成 `groupTransform`），将局部点映射到场景根空间。使用 `toGlobal(point)` 和 `toLocal(point, from?)` 在不同空间之间转换，使用 `getGlobalPosition()` 获取此对象的世界位置。完整的矩阵详细信息在 `pixijs-math` 中；变换设置器和 `toLocal`/`toGlobal` 在 `pixijs-scene-container` 中。

### 渲染顺序与显式 z 排序

子节点按数组顺序渲染：索引 0 首先渲染，最后一个索引最后渲染。对于单个容器上的显式 z 排序，设置 `sortableChildren = true` 并为子节点分配 `zIndex` 值。对于与逻辑层次解耦的渲染顺序（例如，角色的父节点是游戏世界但其绘制发生在 UI 层），使用 `RenderLayer`。详细说明，包括何时选择 sortable children 而不是 RenderLayer，在 `references/scene-management.md` 中。

### 渲染组

将容器标记为 `isRenderGroup: true`（或调用 `container.enableRenderGroup()`）告诉 PixiJS 在 GPU 上将变换应用为单个矩阵，而不是每帧在 CPU 上重新计算每个子节点的世界变换。在大型、稳定的子树（如世界、UI 层或视差条）上使用渲染组。详细说明在 `references/scene-management.md` 中。

### 剔除

`cullable = true` + 一个 `cullArea: Rectangle` 告诉 `CullerPlugin`（或任何剔除传递）跳过渲染屏幕外的对象。`cullableChildren = false` 会短路递归剔除，因为子节点始终在屏幕上。剔除是一个性能话题；`pixijs-performance` 和 `references/scene-management.md` 涵盖了权衡。

### 掩模

将 `container.mask` 设置为另一个显示对象以剪辑其渲染。PixiJS 会自动选择掩模类型：`Graphics` 或 `Container` 掩模使用模板缓冲区，`Sprite` 掩模使用 alpha 滤镜，数字选择 `ColorMask`。所有四种掩模类型（AlphaMask、StencilMask、ScissorMask、ColorMask）在 `references/masking.md` 中都有涵盖。

### 可见性、透明度、色调和混合模式

`visible = false` 跳过渲染和变换更新；`renderable = false` 跳过渲染但仍更新变换（在命中测试或边界查询需要保持活跃时使用）。`alpha` 和 `tint` 会通过子树传递；`blendMode` 控制此容器的绘制指令如何与目标上已有的内容合成。查看 `pixijs-blend-modes` 获取完整的混合模式列表，查看 `pixijs-scene-container` 获取每个节点的状态。

### 销毁语义

`container.destroy()` 断开一个节点。`container.destroy({ children: true })` 递归销毁整个子树；销毁分支时始终使用此方法。`texture: true` 和 `textureSource: true` 会额外销毁组件拥有的 GPU 资源。如果 `cacheAsTexture` 开启，则在销毁前禁用它。`pixijs-scene-container` 记录了完整的签名。

### 生命周期事件

容器在层次结构和可见性变化时发出事件：父节点上的 `childAdded` / `childRemoved`，子节点上的 `added` / `removed`，以及容器本身的 `visibleChanged` 和 `destroyed`。这对于连接响应式 UI 更新或资源管理很有用。完整细节在 `references/container-hierarchy.md` 中。

## 组件比较：哪个技能涵盖哪个对象

| 组件                                                         | 主要用途                                                                                                                                                                 | 技能                             |
| -------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------- |
| `Sprite`                                                             | 在位置绘制单个纹理（`NineSliceSprite` 用于可调整大小的 UI 面板，`TilingSprite` 用于重复背景）。                                 | `pixijs-scene-sprite`             |
| `Text` / `BitmapText` / `HTMLText` / `SplitText` / `SplitBitmapText` | 渲染文本。基于 Canvas 的 `Text` 用于一般用途，`BitmapText` 用于高容量廉价文本，`HTMLText` 用于丰富的 HTML/CSS 布局，分割变体用于逐字符动画。 | `pixijs-scene-text`               |
| `Graphics`                                                           | 矢量绘制：形状、线条、路径、填充、描边。由 `GraphicsContext` 支持。                                                                                        | `pixijs-scene-graphics`           |
| `Mesh` / `MeshSimple` / `MeshPlane` / `MeshRope` / `PerspectiveMesh` | 带有着色器或纹理的自定义几何图形。使用 `MeshRope` 绘制带纹理的路径跟随带状，使用 `PerspectiveMesh` 绘制 2D 透视。                                      | `pixijs-scene-mesh`               |
| `ParticleContainer` + `Particle`                                     | 数千个具有受限变换集的轻量级精灵，用于高吞吐量粒子效果。                                                                                                                                     | `pixijs-scene-particle-container` |
| `DOMContainer`                                                       | 在场景图中定位 HTML 元素（适用于输入、iframe、可访问性覆盖层）。                                                                                                                              | `pixijs-scene-dom-container`      |
| `GifSprite`                                                          | 作为显示对象的动画 GIF 播放。需要 `pixi.js/gif`。                                                                                                          | `pixijs-scene-gif`                |

`Container` 本身在 `pixijs-scene-container` 中有涵盖，并且是每个组件所在的节点。

## 何时使用什么（快速决策）

- "我想分组和变换一些显示对象" → `Container`，见 `pixijs-scene-container`。
- "我想绘制纹理" → `Sprite`，见 `pixijs-scene-sprite`。
- "我想绘制矢量形状或路径" → `Graphics`，见 `pixijs-scene-graphics`。
- "我想绘制文本" → `Text` / `BitmapText` / `HTMLText`，见 `pixijs-scene-text`。
- "我想绘制数千个廉价精灵" → `ParticleContainer`，见 `pixijs-scene-particle-container`。
- "我想绘制自定义几何图形或变形精灵" → `Mesh` 或其变体之一，见 `pixijs-scene-mesh`。
- "我想剪辑子树" → 设置 `.mask`，见 `references/masking.md`。
- "我想解耦渲染顺序" → `RenderLayer`，见 `references/scene-management.md`。
- "我想大型稳定子树的 GPU 级别变换" → `isRenderGroup: true`，见 `references/scene-management.md`。
- "我想跳过屏幕外渲染" → `cullable = true` + `CullerPlugin`，见 `pixijs-performance`。

## 参考

- [references/constructor-options.md](references/constructor-options.md)：每个 `Container` 派生节点继承的 ~30 个字段（变换、显示、层次结构、排序、布局、效果、回调），包括默认值、类型和何时逐行赋值。所有组件技能的共享参考。
- [references/container-hierarchy.md](references/container-hierarchy.md)：添加/删除/交换子节点，保持变换的重新父级，标签导航，销毁子树。
- [references/transforms.md](references/transforms.md)：位置、缩放、旋转、锚点、原点、倾斜、toGlobal/toLocal、三个矩阵（局部/组/世界）、边界。
- [references/masking.md](references/masking.md)：AlphaMask、StencilMask、ScissorMask、ColorMask、反向掩模、成本比较。
- [references/layers.md](references/layers.md)：`RenderLayer`，附加/分离，排序层，层 + 逻辑父级分离。
- [references/render-groups.md](references/render-groups.md)：`isRenderGroup`，GPU 级别变换，何时使用，渲染组 vs `cacheAsTexture`。
- [references/scene-management.md](references/scene-management.md)：综合视图；渲染组、`RenderLayer`、剔除、zIndex 排序、`boundsArea`。

## 常见错误

### [关键] 向组件显示对象添加子节点

错误：

```ts
const sprite = new Sprite(texture);
sprite.addChild(new Graphics().rect(0, 0, 10, 10).fill(0xff0000));
```

正确：

```ts
const group = new Container();
group.addChild(new Sprite(texture));
group.addChild(new Graphics().rect(0, 0, 10, 10).fill(0xff0000));
```

在 v8 中组件（`Sprite`、`Graphics`、`Text`、`Mesh`、`ParticleContainer`、`DOMContainer`、`GifSprite`）技术上扩展了 `Container`，但不应包含子节点。向组件添加子节点会导致未定义的渲染行为。当需要分组时，请将组件包裹在 `Container` 中。

### [关键] 引用 DisplayObject

错误：

```ts
import { DisplayObject } from "pixi.js"; // v8 中没有此导出
function moveNode(node: DisplayObject) {
  node.x += 1;
}
```

正确：

```ts
import { Container } from "pixi.js";
function moveNode(node: Container) {
  node.x += 1;
}
```

`DisplayObject` 在 v8 中已被移除。现在每个显示对象——包括 `Sprite`、`Graphics`、`Text`、`Mesh`——都是 `Container` 的子类。使用 `Container` 作为基本类型。

### [高] 忘记大型静态子树上的 isRenderGroup

错误：

```ts
const world = new Container();
for (let i = 0; i < 5000; i++) {
  world.addChild(new Sprite(texture));
}
app.stage.addChild(world);
```

正确：

```ts
const world = new Container({ isRenderGroup: true });
for (let i = 0; i < 5000; i++) {
  world.addChild(new Sprite(texture));
}
app.stage.addChild(world);
```

没有 `isRenderGroup: true`，渲染器每帧都会重新计算每个子节点相对于其父节点的变换。将子树标记为渲染组会缓存变换和绘制状态，直到子节点发生变化，这对于大型或基本静态的树至关重要。

### [高] 将 child.x 视为世界空间

错误：

```ts
const enemy = new Container();
enemy.x = 500;
world.addChild(enemy);
world.x = 200;
console.log(enemy.x); // 500（局部），不是 700（世界）
```

正确：

```ts
const worldPos = enemy.toGlobal({ x: 0, y: 0 });
console.log(worldPos.x); // 700
```

`Container.x/y/scale/rotation` 是相对于父节点的。使用 `toGlobal(point)` 计算世界空间坐标，或使用 `getGlobalPosition()` 获取容器在世界空间中的原点。世界变换不会作为简单的 `x/y` 对暴露。

### [中] sortableChildren 而没有 zIndex

错误：

```ts
const layer = new Container();
layer.sortableChildren = true;
layer.addChild(bg); // 没有 zIndex
layer.addChild(mid); // 没有 zIndex
layer.addChild(fg); // 没有 zIndex
// 顺序不变——所有 zIndex 默认为 0
```

正确：

```ts
const layer = new Container();
layer.sortableChildren = true;
bg.zIndex = 0;
mid.zIndex = 10;
fg.zIndex = 20;
layer.addChild(bg, mid, fg);
```

`sortableChildren` 会根据 `zIndex` 重新排序子节点，但只有当子节点实际具有不同的 `zIndex` 值时才会生效。仅设置父节点标志没有可见效果。

## 工具

[PixiJS Devtools Chrome 扩展](https://chromewebstore.google.com/detail/pixijs-devtools/aamddddknhcagpehecnhphigffljadon) 允许您实时检查和操作正在运行的场景图。对于任何非平凡的布局或渲染顺序调试，安装它。
