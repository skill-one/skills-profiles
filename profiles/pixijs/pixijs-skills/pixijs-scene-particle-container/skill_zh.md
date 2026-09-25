`ParticleContainer` 是一个专门用于在单个绘制调用中渲染数百到数万个轻量级精灵的容器。用于粒子效果、弹道模式或任何需要大量外观相似的物体且每个物体开销最小的场景。粒子共享单个基础纹理，并具有受限的变换集；它们不是完整的 `Container` 子元素。

假设熟悉 `pixijs-scene-core-concepts`。`ParticleContainer` 在另一个意义上是一个特殊的叶子节点：它在自己的 `particleChildren` 数组中包含 `Particle` 实例，并拒绝普通 PixiJS 子元素。使用 `addParticle` 而不是 `addChild`，如果需要将 `ParticleContainer` 与其他场景对象分组，请将其包裹在 `Container` 中。

粒子 API 在 v8 中是新的，但已稳定可用于生产。

## 快速入门

```ts
const texture = await Assets.load("particle.png");

const container = new ParticleContainer({
  texture,
  boundsArea: new Rectangle(0, 0, app.screen.width, app.screen.height),
  dynamicProperties: {
    position: true,
    rotation: false,
    color: false,
  },
});

for (let i = 0; i < 10000; i++) {
  container.addParticle(
    new Particle({
      texture,
      x: Math.random() * app.screen.width,
      y: Math.random() * app.screen.height,
    }),
  );
}

app.stage.addChild(container);
```

**相关技能：** `pixijs-scene-core-concepts`（场景图基础）、`pixijs-scene-sprite`（当你需要每个物体具有完整功能时）、`pixijs-assets`（共享纹理、图集）、`pixijs-performance`（批处理、纹理优化）、`pixijs-scene-container`（与其他显示对象包裹）。

## 构造函数选项

### ParticleContainerOptions

所有 `Container` 选项（`position`、`scale`、`tint`、`label`、`filters`、`zIndex` 等）在此处也有效——参见 `skills/pixijs-scene-core-concepts/references/constructor-options.md`。注意 `children` 被省略了：使用 `particles` 代替。

| 选项              | 类型                 | 默认值                                                                        | 描述                                                                                                                                                                     |
| ------------------- | -------------------- | ------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `texture`           | `Texture`            | `null`                                                                         | 所有粒子的共享基础纹理。如果省略，容器会回退到第一个添加的粒子的纹理；每个粒子必须共享相同的基础纹理源。                                                                 |
| `particles`         | `T[]`                | `[]`                                                                           | 初始 `Particle`（或 `IParticle`）实例数组。相当于调用 `addParticle` 对每个实例，但跳过每次调用的视图更新。                                                                 |
| `dynamicProperties` | `ParticleProperties` | `{ vertex: false, position: true, rotation: false, uvs: false, color: false }` | 标记哪些粒子属性每帧重新上传到 GPU。默认情况下只有 `position` 是动态的；标记你动画的属性，其余的保持静态以提高速度。                                                                        |
| `roundPixels`       | `boolean`            | `false`                                                                        | 将粒子位置四舍五入到最近的像素。为像素艺术风格产生更清晰的渲染效果，但代价是平滑的亚像素运动。                                                                                     |
| `shader`            | `Shader`             | 默认粒子着色器                                                                | 替换默认粒子着色器。自定义着色器必须声明 `aPosition`、`aUV`、`aColor`，以及通过 `dynamicProperties` 启用的任何动态属性。                                                              |

`boundsArea` 继承自 `Container`，但在 `ParticleContainer` 中实际上是必需的：容器默认返回空边界 `(0, 0, 0, 0)` 以提高性能，因此如果没有 `boundsArea`，在裁剪激活时它会被裁剪为不可见，且 `containsPoint` 总是找不到。

### ParticleOptions

`Particle` 是一个轻量级结构，不是 `Container` 的子类——`ContainerOptions` 的字段都不适用。完整选项列表：

| 选项     | 类型          | 默认值    | 描述                                                                                                                            |
| ---------- | ------------- | ---------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| `texture`  | `Texture`     | —          | 必须的。用于渲染此粒子的纹理。同一 `ParticleContainer` 中的所有粒子必须共享相同的基础纹理源。                                       |
| `x`        | `number`      | `0`        | 容器本地空间中的 X 位置。                                                                                                     |
| `y`        | `number`      | `0`        | 容器本地空间中的 Y 位置。                                                                                                     |
| `scaleX`   | `number`      | `1`        | 水平缩放因子。                                                                                                                   |
| `scaleY`   | `number`      | `1`        | 垂直缩放因子。                                                                                                                 |
| `anchorX`  | `number`      | `0`        | 0–1 范围内的水平锚点；`0` 是左，`0.5` 是中，`1` 是右。                                                                    |
| `anchorY`  | `number`      | `0`        | 0–1 范围内的垂直锚点；`0` 是上，`0.5` 是中，`1` 是下。                                                                    |
| `rotation` | `number`      | `0`        | 以弧度表示的旋转。                                                                                                               |
| `tint`     | `ColorSource` | `0xffffff` | 作为十六进制数字或 CSS 颜色字符串的染色颜色。与 `alpha` 结合到内部 `color` 字段中。                                               |
| `alpha`    | `number`      | `1`        | 透明度（0–1）。值超出范围会被裁剪。与 `tint` 结合到内部 `color` 字段中。                                                         |

构造函数也接受一个单独的 `Texture` 作为其唯一参数（`new Particle(texture)`），这是 `new Particle({ texture })` 使用上述默认值的简写。

`Particle.defaultOptions` 是一个静态对象，你可以重新分配它来全局更改默认值；参见下文“粒子创建”部分。

## 核心模式

### 粒子创建

```ts
const particle = new Particle({
  texture,
  x: 100,
  y: 200,
  scaleX: 0.5,
  scaleY: 0.5,
  anchorX: 0.5,
  anchorY: 0.5,
  rotation: Math.PI / 4,
  tint: 0xff0000,
  alpha: 0.8,
});

container.addParticle(particle);
```

`Particle` 是一个轻量级结构，具有扁平的数字字段：`x`、`y`、`scaleX`、`scaleY`、`anchorX`、`anchorY`、`rotation`、`color`、`texture`。它还暴露 `tint`（十六进制/CSS 颜色）和 `alpha`（0-1）作为设置器，它们组合成内部 `color` 字段。没有变换层次结构，没有事件，没有滤镜。

可以直接传递 `Texture` 作为唯一参数：`new Particle(texture)`。

覆盖 `Particle.defaultOptions` 以全局更改默认值：

```ts
Particle.defaultOptions = {
  ...Particle.defaultOptions,
  anchorX: 0.5,
  anchorY: 0.5,
};
```

### 使用 particles 选项预填充

```ts
const particles = Array.from(
  { length: 10000 },
  () =>
    new Particle({
      texture,
      x: Math.random() * 800,
      y: Math.random() * 600,
    }),
);

const container = new ParticleContainer({
  texture,
  boundsArea: new Rectangle(0, 0, 800, 600),
  particles,
});
```

在构造函数中传递 `particles` 等同于创建空容器并调用 `addParticle` 对每个实例，但避免了每次调用的视图更新。

### 动态与静态属性以及 update()

```ts
const container = new ParticleContainer({
  dynamicProperties: {
    rotation: true,
  },
});
```

`dynamicProperties` 控制哪些粒子属性每帧重新上传到 GPU。`ParticleContainer.defaultOptions.dynamicProperties` 的默认值是：

```ts
{ vertex: false, position: true, rotation: false, uvs: false, color: false }
```

你只需要覆盖你正在动画的属性；其余的继承默认值（位置动态，其他静态）。总共五个属性：

- `vertex`：缩放/锚点顶点
- `position`
- `rotation`
- `uvs`：纹理坐标（用于帧交换的粒子）
- `color`：染色和透明度

只标记你动画的属性；静态属性更便宜。如果在运行时更改静态属性，请调用 `container.update()` 以重新上传：

```ts
container.particleChildren.forEach((p) => {
  p.tint = 0x00ff00;
});
container.update();
```

### 对 particleChildren 执行批处理操作

```ts
// 批量添加
const batch = [];
for (let i = 0; i < 5000; i++) {
  batch.push(
    new Particle({ texture, x: Math.random() * 800, y: Math.random() * 600 }),
  );
}
container.particleChildren.push(...batch);
container.update();

// 批量删除
container.particleChildren.length = 0;
container.update();
```

`addParticle`、`addParticleAt`、`removeParticle`、`removeParticleAt` 和 `removeParticles` 都会触发每次调用的视图更新。对于大批量操作，直接数组操作加上一个 `update()` 更快。

### 纹理和着色器选项

`ParticleContainerOptions` 中的 `texture` 是可选的。如果省略，容器会回退到第一个添加的粒子的纹理；每个后续粒子必须共享相同的基础纹理源。当你需要提前声明图集或第一个粒子可能在运行中途更改时，请显式设置它：

```ts
const container = new ParticleContainer({ texture });
```

`shader` 允许你用任何 `Shader` 实例替换默认粒子着色器。自定义着色器必须声明粒子管道上传的属性（`aPosition`、`aUV`、`aColor`，以及通过 `dynamicProperties` 启用的任何动态属性）。用于自定义混合数学、距离场精灵或非标准效果：

```ts
const container = new ParticleContainer({ texture, shader: myCustomShader });
```

### 对整个粒子系统进行淡出或染色

```ts
const burst = new ParticleContainer({ texture, particles });
const layer = new Container();
layer.addChild(burst);

app.ticker.add(() => {
  layer.alpha -= 0.01; // 每个粒子都会淡出
});
burst.tint = 0x66ccff; // 每个粒子都会染色
```

容器的 `alpha`、`tint` 和 `blendMode` 与精灵相同的方式级联到粒子中，因此你可以不接触 `particleChildren` 就对整个系统进行淡出或重新着色。

### 限制

`ParticleContainer` 故意牺牲功能以换取速度：

- 没有滤镜、掩码或每个粒子的混合模式。混合模式应用于容器级别：在 `ParticleContainer` 上设置 `blendMode` 或让它从父 `Container` 继承（默认 `"inherit"` 会解析为祖先的混合模式，如 `Sprite` 和 `Mesh`）。整个粒子批处理共享一个混合模式。容器的 `alpha` 和 `tint` 或任何祖先的值会乘以每个粒子，在每个粒子自己的 `alpha`/`tint` 之上。
- 粒子没有嵌套子元素。
- 没有自动边界计算。
- 所有粒子必须共享相同的基础纹理源（图集有效；多个不相关的纹理无效）。
- 通过 `shader` 选项支持自定义着色器。

### 容器方法迁移

`ParticleContainer` 使用一个单独的子元素管理 API，针对 GPU 缓冲区更新进行了优化。标准的 `Container` 子元素方法在 `ParticleContainer` 上调用时会抛出异常。

| 标准容器方法    | ParticleContainer 等效方法                        |
| ---------------------------- | --------------------------------------------------- |
| `addChild(child)`            | `addParticle(particle)`                             |
| `removeChild(child)`         | `removeParticle(particle)`                          |
| `addChildAt(child, index)`   | `addParticleAt(particle, index)`                    |
| `removeChildAt(index)`       | `removeParticleAt(index)`                           |
| `removeChildren(begin, end)` | `removeParticles(begin, end)`                       |
| `getChildAt(index)`          | 直接访问 `container.particleChildren[index]`        |
| `swapChildren()`             | 不可用                                           |
| `reparentChild()`            | 不可用                                           |

## 常见错误

### [CRITICAL] 向 ParticleContainer 添加精灵

错误：

```ts
const container = new ParticleContainer();
const sprite = new Sprite(texture);
container.addChild(sprite);
```

正确：

```ts
const container = new ParticleContainer();
const particle = new Particle(texture);
container.addParticle(particle);
```

`ParticleContainer` 不接受 `Sprite` 子元素。`addChild` 会抛出错误。粒子必须是 `Particle` 实例（或任何实现 `IParticle` 的对象），通过 `addParticle` 添加。这是一个从 v7 完全重写的版本，当时 `ParticleContainer` 接受 `Sprite` 子元素。


### [HIGH] 未在 ParticleContainer 上设置 boundsArea

错误：

```ts
const container = new ParticleContainer();
// bounds 始终是 (0, 0, 0, 0) — 裁剪和命中测试失败
```

正确：

```ts
const container = new ParticleContainer({
  boundsArea: new Rectangle(0, 0, 800, 600),
});
```

`ParticleContainer` 默认返回空边界 `(0, 0, 0, 0)` 以提高性能。如果没有 `boundsArea`，在裁剪激活时容器会被裁剪为不可见，且 `containsPoint` 总是找不到。设置 `boundsArea` 为你的粒子占据的区域。


### [HIGH] 使用 children 而不是 particleChildren

错误：

```ts
container.addParticle(new Particle(texture));
console.log(container.children.length); // 0
```

正确：

```ts
container.addParticle(new Particle(texture));
console.log(container.particleChildren.length); // 1
```

粒子存储在 `particleChildren` 数组中，而不是 `children`。标准的 `Container.children` 数组在 `ParticleContainer` 上为空。所有粒子枚举、计数和操作都必须使用 `particleChildren` 加上 `*Particle` 方法。


### [MEDIUM] 不要将 ParticleContainer 作为普通容器使用

`ParticleContainer` 包含粒子，而不是显示对象。如果你需要将粒子系统与背景精灵或 UI 叠加层分组，请将 `ParticleContainer` 本身包裹在普通的 `Container` 中：

```ts
const world = new Container();
world.addChild(backgroundSprite, particleContainer, uiLayer);
```


## API 参考

- [ParticleContainer](https://pixijs.download/release/docs/scene.ParticleContainer.html.md)
- [ParticleContainerOptions](https://pixijs.download/release/docs/scene.ParticleContainerOptions.html.md)
- [Particle](https://pixijs.download/release/docs/scene.Particle.html.md)
- [ParticleOptions](https://pixijs.download/release/docs/scene.ParticleOptions.html.md)
- [IParticle](https://pixijs.download/release/docs/scene.IParticle.html.md)
- [ParticleProperties](https://pixijs.download/release/docs/scene.ParticleProperties.html.md)
