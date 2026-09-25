网格渲染带纹理或自定义着色的任意 2D（或透视投影）几何图形。PixiJS 提供了基础的 `Mesh` 类以及四个用于常见形状的专门子类：`MeshSimple`、`MeshPlane`、`MeshRope` 和 `PerspectiveMesh`。根据你的形状选择合适的子类；当你需要顶点级别的完全控制或自定义着色时，使用基础的 `Mesh` 类。

假设你熟悉 `pixijs-scene-core-concepts`。网格是叶节点；它们不能有子节点。将多个网格包裹在 `Container` 中以将它们分组。

## 快速入门

```ts
const texture = await Assets.load("pattern.png");

const geometry = new MeshGeometry({
  positions: new Float32Array([0, 0, 100, 0, 100, 100, 0, 100]),
  uvs: new Float32Array([0, 0, 1, 0, 1, 1, 0, 1]),
  indices: new Uint32Array([0, 1, 2, 0, 2, 3]),
  topology: "triangle-list",
});

const mesh = new Mesh({
  geometry,
  texture,
  roundPixels: false,
});
app.stage.addChild(mesh);
```

每个 `Mesh` 子类都接受一个选项对象。基础的 `Mesh` 需要 `geometry`；子类（`MeshSimple`、`MeshPlane`、`MeshRope`、`PerspectiveMesh`）内部构建几何图形，并需要 `texture`。请参考每个变体的文档以获取完整的字段列表。

## 变体

| 变体           | 使用场景                                              | 权衡                                              | 参考                                                        |
| -------------- | ----------------------------------------------------- | ------------------------------------------------ | ---------------------------------------------------------------- |
| `Mesh`            | 完全控制、自定义几何图形、自定义着色                 | 你需要自己构建 `MeshGeometry`                   | [references/mesh.md](references/mesh.md)                         |
| `MeshSimple`      | 快速带每帧顶点动画的纹理形状                        | 薄包装；自动更新顶点缓冲区            | [references/mesh-simple.md](references/mesh-simple.md)           |
| `MeshPlane`       | 用于扭曲效果的细分纹理矩形                          | 固定拓扑；`verticesX`/`verticesY` 控制密度 | [references/mesh-plane.md](references/mesh-plane.md)             |
| `MeshRope`        | 沿着折线路径的纹理跟随                              | 在每个点弯曲；需要许多点以实现平滑曲线 | [references/mesh-rope.md](references/mesh-rope.md)               |
| `PerspectiveMesh` | 带透视角落的 2D 平面                                | 不是真正的 3D；仅 UV 级别的透视校正       | [references/mesh-perspective.md](references/mesh-perspective.md) |

## 何时使用什么

- **"我需要一个带纹理的四边形"** → `Sprite`（见 `pixijs-scene-sprite`），而不是网格。网格用于 Sprite 无法表达的场景。
- **"我需要变形一个带纹理的矩形"** → `MeshPlane`。设置 `verticesX`/`verticesY` 以获得所需的平滑度。
- **"我需要一个沿着点移动的绳索或轨迹"** → `MeshRope`。使用 `width` 控制粗细；使用 `textureScale: 0` 拉伸或 `> 0` 重复纹理。
- **"我需要一个倾斜的 2D 卡片或地板"** → `PerspectiveMesh`。传递四个角位置；不是真正的 3D，但对于 2.5D 效果足够好。
- **"我需要一个带简单形状的每帧顶点动画"** → `MeshSimple`。它为你处理缓冲区更新。
- **"我需要一个自定义着色或非标准几何图形"** → 带手建 `MeshGeometry` 的基础 `Mesh`。参考 `pixijs-custom-rendering` 以进行着色器编写。
- **"我需要一个真正的 3D 渲染"** → 使用专门的 3D 库。`PerspectiveMesh` 在 UV 级别模拟透视，但没有深度缓冲区。

## 快速概念

### `MeshGeometry` 拥有顶点数据

`MeshGeometry` 持有 `positions`、`uvs`、`indices` 和 `topology`。你可以将一个几何图形跨多个 `Mesh` 实例共享；位置是引用计数的。

### 批处理

只有当网格使用 `MeshGeometry`、没有自定义着色器、没有深度或剔除状态，并且使用 `'auto'` 规则（`batchMode = 'auto'` 且 ≤100 个顶点）时，才会批处理（与其他绘制调用组合）。自定义着色器总是独立渲染。

### 拓扑在几何图形上，而不是在网格上

`new MeshGeometry({ topology: 'triangle-strip' })`；拓扑是几何图形属性。默认值是 `'triangle-list'`；如果你的数据组织方式不同，请显式设置它。

### 额外的控制选项

- `new MeshGeometry({ shrinkBuffersToFit: true })` — 创建时修剪 GPU 缓冲区存储以匹配实际顶点数。当你提供大型、一次性几何图形时使用它。
- `Mesh.containsPoint(point)` — 拓扑感知的碰撞检测，遍历三角形。适用于任何 `MeshGeometry`，包括自定义布局。
- `new Mesh({ geometry, state })` — 传递一个 `State` 对象以控制混合、深度和剔除。如果设置了深度或剔除标志，批处理将自动禁用。省略时默认为 `State.for2d()`。

## 常见错误

### [高] 使用旧的 `SimpleMesh` / `SimplePlane` / `SimpleRope` 名称

错误：

```ts
import { SimpleRope } from "pixi.js";
const rope = new SimpleRope(texture, points);
```

正确：

```ts
import { MeshRope } from "pixi.js";
const rope = new MeshRope({ texture, points });
```

在 v8 中重命名：`SimpleMesh` → `MeshSimple`，`SimplePlane` → `MeshPlane`，`SimpleRope` → `MeshRope`。所有都切换到选项对象构造器。

### [高] `MeshGeometry` 的位置构造函数参数

错误：

```ts
const geom = new MeshGeometry(vertices, uvs, indices);
```

正确：

```ts
const geom = new MeshGeometry({
  positions: vertices,
  uvs,
  indices,
  topology: "triangle-list",
});
```

v8 使用选项对象。注意属性是 `positions`，而不是 `vertices`；`vertices` 名称仅由 `MeshSimple` 使用。

### [中] 向网格添加子节点

错误：

```ts
mesh.addChild(otherMesh);
```

正确：

```ts
const group = new Container();
group.addChild(mesh, otherMesh);
```

`Mesh` 设置 `allowChildren = false`。添加子节点会记录弃用警告。将网格分组在普通的 `Container` 中。

## API 参考

- [Mesh](https://pixijs.download/release/docs/scene.Mesh.html.md)
- [MeshGeometry](https://pixijs.download/release/docs/scene.MeshGeometry.html.md)
- [MeshSimple](https://pixijs.download/release/docs/scene.MeshSimple.html.md)
- [MeshPlane](https://pixijs.download/release/docs/scene.MeshPlane.html.md)
- [MeshRope](https://pixijs.download/release/docs/scene.MeshRope.html.md)
- [PerspectiveMesh](https://pixijs.download/release/docs/scene.PerspectiveMesh.html.md)
