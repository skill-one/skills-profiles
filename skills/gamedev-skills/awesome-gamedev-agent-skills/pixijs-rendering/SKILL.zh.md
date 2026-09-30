---
name: pixijs-rendering
description: 构建 PixiJS v8 渲染层：创建异步 Application，使用 Assets 加载纹理，通过 Container 和 Sprite 组合场景图，驱动 ticker 循环，连接指针事件，并使用渲染组分组绘制。在构建或调试 PixiJS v8 时使用——当用户提及 PixiJS、Pixi、Application、app.stage、Container、Sprite、Assets.load、app.ticker 或 eventMode 时。固定 v8 异步 init() API。
---

# PixiJS 8.21 渲染

设置和构建 PixiJS **8.21** 应用程序：异步 `Application`、通过 `Assets` 加载资源、`Container`/`Sprite` 场景图、ticker 循环、指针事件和渲染组。固定 8.21 API（异步 `init`、统一 `Assets`、`eventMode`）。

## 何时使用

- 启动 PixiJS v8 项目、修复空白画布、构建显示列表、加载纹理、通过 ticker 动画或处理指针输入时使用。
- 当 `package.json` 依赖 `pixi.js`（v8）且代码执行 `import { Application } from 'pixi.js'` 时使用。

**不使用的情况：** Phaser 的场景/加载器模型 → `phaser-core`。3D 场景 → `threejs-scene-setup`。PixiJS v7 及更早版本的代码（同步 `new Application({...})`、`Loader`、`beginFill`/`endFill`）需要先进行 v8 迁移；此技能仅针对 v8。(`interactive = true` 在 v8 中仍然作为 `eventMode = 'static'` 的别名工作，但优先使用显式的 `eventMode`。)

## 核心工作流程

1. **创建并 `await` Application。** 在 v8 中，`new Application()` 是空的；配置发生在 `await app.init({...})` 中。将 `app.canvas`（不是 `app.view`）附加到 DOM。将顶级 `await` 包装在异步函数中以供打包器使用。
2. **使用 `Assets` 加载资源。** `await Assets.load(url)` 返回一个 `Texture`。对于许多资源，注册清单/包并通过名称加载。v7 没有 `Loader`。
3. **构建场景图。** 一切都继承自 `app.stage`（一个 `Container`）。将相关对象分组到 `Container` 中；子对象的变换相对于父对象。绘制顺序 = 插入顺序（后 = 在顶部）。
4. **使用 ticker 动画。** `app.ticker.add((ticker) => {...})`。通过 `ticker.deltaTime`（帧，~1 在 60fps）或 `ticker.deltaMS`（毫秒）缩放运动，使速度与帧率无关。
5. **通过设置 `eventMode = 'static'`（或 `'dynamic'`）为每个对象启用事件，然后 `obj.on('pointerdown', ...)`。联邦指针事件涵盖鼠标/触摸/笔。
6. **将大的静态子树提升为渲染组** (`isRenderGroup: true`)，以便 GPU 缓存其变换。在之前和之后进行性能分析；确认屏幕上的像素。

## 模式

### 1. 异步 Application 启动（v8 入口点）

```js
import { Application, Assets, Sprite } from 'pixi.js';

(async () => {
  // v8：构造空对象，然后 await init()。配置不在构造函数中。
  const app = new Application();
  await app.init({
    background: '#1099bb',
    resizeTo: window,        // 跟踪窗口大小
    antialias: true,
    // preference: 'webgpu',  // 仅提示；默认顺序首先尝试 'webgl'。
    //                        // Pixi 如果后端不可用会回退——
    //                        // 根据 app.renderer.name 分支，不要假设它被接受。
  });

  document.body.appendChild(app.canvas); // v8 使用 app.canvas，不是 app.view

  const texture = await Assets.load('https://pixijs.com/assets/bunny.png');
  const bunny = new Sprite(texture);
  bunny.anchor.set(0.5);
  bunny.position.set(app.screen.width / 2, app.screen.height / 2);
  app.stage.addChild(bunny);
})();
```

### 2. 用于相对变换场景图的 Containers

```js
import { Container, Sprite } from 'pixi.js';

const world = new Container();
app.stage.addChild(world);

// 子对象相对于 `world` 定位；通过变换父对象来移动/缩放/旋转整个组
for (let i = 0; i < 10; i++) {
  const coin = new Sprite(coinTexture);
  coin.x = i * 40;
  world.addChild(coin);
}
world.position.set(100, 100);
world.scale.set(2);            // 每个硬币随容器缩放
```

### 3. ticker 循环（与帧率无关）

```js
let elapsed = 0;
app.ticker.add((ticker) => {
  // deltaTime ≈ 1 在 60fps；deltaMS 是自上一帧以来的毫秒数。
  elapsed += ticker.deltaMS;
  bunny.rotation += 0.05 * ticker.deltaTime;          // 任何帧率下都平滑
  bunny.y = app.screen.height / 2 + Math.sin(elapsed / 500) * 50;
});
```

### 4. 指针事件（联邦）

```js
bunny.eventMode = 'static';   // 'static' = 交互式，不会自行移动
bunny.cursor = 'pointer';     // 悬停光标；`buttonMode` 在 v8 中已移除
bunny.on('pointerdown', (event) => {
  bunny.tint = 0xff0000;
  // event.global 是指针在舞台空间中的位置。
});
bunny.on('pointerover', () => bunny.scale.set(1.1));
bunny.on('pointerout',  () => bunny.scale.set(1.0));
```

拖动需要 `globalpointermove`，而不是 `pointermove`。在 v8 中 `pointermove` 仅在指针在对象上方时触发，所以跟随光标经过对象边缘的拖动会停止更新。`globalpointermove` 在每次移动时触发：

```js
let dragging = false;
bunny.on('pointerdown', () => { dragging = true; });
bunny.on('pointerup', () => { dragging = false; });
bunny.on('pointerupoutside', () => { dragging = false; }); // 在对象外释放
bunny.on('globalpointermove', (event) => {
  if (dragging) bunny.position.copyFrom(event.global);
});
```

### 5. 通过名称加载许多资源（包）

```js
import { Assets } from 'pixi.js';

await Assets.init({
  manifest: {
    bundles: [{
      name: 'level-1',
      assets: [
        { alias: 'hero',  src: 'assets/hero.png' },
        { alias: 'tiles', src: 'assets/tiles.png' },
      ],
    }],
  },
});

const bundle = await Assets.loadBundle('level-1'); // { hero: Texture, tiles: Texture }
const hero = new Sprite(bundle.hero);
```

### 6. 渲染组用于大型静态层

```js
// 一个大的、很少变化的背景子树：让 GPU 缓存其变换。
const background = new Container({ isRenderGroup: true });
app.stage.addChild(background);
// 向 `background` 添加数百个静态瓦片。移动 `background` 本身仍然很便宜；不断添加/移除子对象会抵消收益。
```

## 陷阱

- **空白画布 / "app.stage is undefined"** → 你没有 `await app.init()`，或者你配置了构造函数。在 v8 中构造函数是空的；所有选项都去 `init()`。`app.renderer`/`app.canvas`/`app.screen` 在 `init()` 的 Promise 解决之前是 `undefined`。
- **`app.view` 是 undefined** → v8 将其重命名为 `app.canvas`。
- **迁移 v7 代码** → `Loader`/`loader.add` → `Assets.load`（`Loader` 类已移除）；同步 `new Application({...})` → 空构造函数 + 异步 `init()`（构造函数中的选项被弃用警告，不是错误）；`beginFill()`/`endFill()` → 先形状 `.rect(...).fill(...)`。`interactive = true` 和 `app.view` 仍然作为弃用别名工作。
- **ticker 回调参数是 Ticker，而不是 delta 数** → `app.ticker.add((dt) => { obj.rotation += dt; })` 编译通过，但 `dt` 是整个 `Ticker` 对象，所以数学运算结果为 `NaN` 且没有动画。从参数中读取 `ticker.deltaTime`。
- **顶级 await 打包错误（Vite ≤6.0.6）** → 将启动包装在 `(async () => { ... })()` 中。
- **速度随帧率变化** → 乘以 `ticker.deltaTime`（~1 在 60fps）或按 `ticker.deltaMS` 缩放；永远不要假设 60fps。`deltaTime` 是一个无单位的乘数，不是毫秒。
- **点击无反应** → 对象的 `eventMode` 仍然是 `'passive'`（v8 默认：自身不交互，子对象仍然交互）；将其设置为 `'static'`（或 `'dynamic'` 用于在静止光标下移动的对象）。
- **拖动在对象边缘停止** → v8 中 `pointermove` 仅在指针在对象上方时触发；使用 `globalpointermove` 进行拖动/全局跟踪。
- **`Texture.from(url)` 返回空白/未定义的纹理** → 在 v8 中它仅读取资源缓存；先 `await Assets.load(url)`，然后使用返回的 `Texture`。
- **WebGPU 功能出错** → `preference` 是提示。如果后端不可用，Pixi 会回退（WebGL，然后 Canvas）；在使用后端特定代码之前根据 `app.renderer.name` 分支。
- **像素艺术看起来模糊** → 设置 `texture.source.scaleMode = 'nearest'`（或在加载时传递它）。
- **内存增长** → `removeChild` 不会释放 GPU 内存；调用 `sprite.destroy()` 和 `Assets.unload(url)` 以释放你不再使用的资源。
- **在同一选项卡中销毁并重新创建应用程序后出现闪烁/损坏** → 使用 `app.destroy({ releaseGlobalResources: true })` 销毁；否则旧应用程序的池化批次/纹理会泄漏到新应用程序中。

## 参考

- 对于纹理/资源管道（精灵表/图集、`Assets.add`、背景加载、卸载）和图形/文本/`TilingSprite`/`ParticleContainer` 以及滤镜，请阅读 `references/assets-and-display.md`。

## 相关技能

- `phaser-core` — 一个包含所有功能的 2D 框架（场景、物理、输入）。
- `threejs-scene-setup` — 浏览器中的 3D，使用 three.js。
- `prototype-fast` — 快速灰盒一个可玩的切片（通常引用 PixiJS）。
