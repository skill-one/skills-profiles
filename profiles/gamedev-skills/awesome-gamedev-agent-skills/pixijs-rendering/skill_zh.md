# PixiJS 8.19 渲染

设置和构建 PixiJS **8.19** 应用程序：异步 `Application`、通过 `Assets` 加载资源、`Container`/`Sprite` 场景图、ticker 循环、指针事件和渲染组。固定 8.19 API（异步 `init`、统一 `Assets`、`eventMode`）。

## 何时使用

- 启动 PixiJS v8 项目、修复空白画布、构建显示列表、加载纹理、通过 ticker 动画或处理指针输入时使用。
- 当 `package.json` 依赖 `pixi.js`（v8）且代码执行 `import { Application } from 'pixi.js'` 时使用。

**不使用的情况：** Phaser 的场景/加载器模型 → `phaser-core`。3D 场景 → `threejs-scene-setup`。PixiJS v7 及更早版本的代码（同步 `new Application({...})`、`Loader`、`interactive = true`）需要先进行 v8 迁移；此技能仅针对 v8。

## 核心工作流程

1. **创建并 `await` Application。** 在 v8 中，`new Application()` 是空的；配置发生在 `await app.init({...})` 中。将 `app.canvas`（不是 `app.view`）追加到 DOM 中。将顶级 `await` 包装在异步函数中以供打包器使用。
2. **使用 `Assets` 加载资源。** `await Assets.load(url)` 返回一个 `Texture`。对于许多资源，注册清单/包并通过名称加载。没有 v7 的 `Loader`。
3. **构建场景图。** 所有内容都继承自 `app.stage`（一个 `Container`）。将相关对象分组到 `Container` 中；子对象的变换相对于父对象。绘制顺序 = 插入顺序（后 = 在顶部）。
4. **使用 ticker 动画。** `app.ticker.add((ticker) => {...})`。通过 `ticker.deltaTime`（帧，60fps 时约 1）或 `ticker.deltaMS`（毫秒）缩放运动，使速度与帧率无关。
5. **通过设置 `eventMode = 'static'`（或 `'dynamic'`）为每个对象启用事件**，然后 `obj.on('pointerdown', ...)`。联邦指针事件覆盖鼠标/触摸/笔。
6. **将大的静态子树提升为渲染组** (`isRenderGroup: true`)，以便 GPU 缓存它们的变换。在之前和之后进行性能分析；确认屏幕上的像素。

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
    // preference: 'webgpu',  // 选择 WebGPU；默认 'webgl'
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

// 子对象相对于 `world` 定位；通过变换父对象来移动/缩放/旋转整个组。
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
  // deltaTime 在 60fps 时约等于 1；deltaMS 是自上一帧以来的毫秒数。
  elapsed += ticker.deltaMS;
  bunny.rotation += 0.05 * ticker.deltaTime;          // 任何帧率下都平滑
  bunny.y = app.screen.height / 2 + Math.sin(elapsed / 500) * 50;
});
```

### 4. 指针事件（联邦）

```js
bunny.eventMode = 'static';   // 'static' = 交互式，不会自行移动
bunny.cursor = 'pointer';
bunny.on('pointerdown', (event) => {
  bunny.tint = 0xff0000;
  // event.global 是指针在舞台空间中的位置。
});
bunny.on('pointerover', () => bunny.scale.set(1.1));
bunny.on('pointerout',  () => bunny.scale.set(1.0));
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

### 6. 用于大型静态层的渲染组

```js
// 一个大的、很少变化的背景子树：让 GPU 缓存其变换。
const background = new Container({ isRenderGroup: true });
app.stage.addChild(background);
// 向 `background` 添加数百个静态瓦片。移动 `background` 本身仍然很便宜；不断添加/移除子对象会抵消这种好处。
```

## 陷阱

- **空白画布 / "app.stage is undefined"** → 你没有 `await app.init()`，或者你配置了构造函数。在 v8 中，构造函数是空的；所有选项都去 `init()`。
- **`app.view` 是 undefined** → v8 将其重命名为 `app.canvas`。
- **v7 代码抛出异常** → `interactive = true` → `eventMode = 'static'`；`Loader`/`loader.add` → `Assets.load`；同步 `new Application({...})` → 异步 `init`。
- **顶级 await 打包错误（Vite ≤6.0.6）** → 将启动包装在 `(async () => { ... })()` 中。
- **速度随帧率变化** → 乘以 `ticker.deltaTime`（或使用 `deltaMS`）；永远不要假设 60fps。
- **点击无反应** → 对象的 `eventMode` 仍然是 `'none'`（默认值）；将其设置为 `'static'` 或 `'dynamic'`。
- **纹理在像素艺术上看起来模糊** → 设置 `texture.source.scaleMode = 'nearest'`（或在加载时传递它）。
- **内存增长** → `removeChild` 不会释放 GPU 内存；对于已完成的资源调用 `sprite.destroy()` 和 `Assets.unload(url)`。

## 参考

- 对于纹理/资源管道（精灵表/图集、`Assets.add`、背景加载、卸载）以及图形/文本/`TilingSprite`/`ParticleContainer` 和滤镜，请阅读 `references/assets-and-display.md`。

## 相关技能

- `phaser-core` — 一个包含所有功能的 2D 框架（场景、物理、输入）。
- `threejs-scene-setup` — 浏览器中的 3D（使用 three.js）。
- `prototype-fast` — 快速灰盒一个可玩的切片（通常引用 PixiJS）。
