`app.ticker` 每帧运行注册的回调函数，并在 `UPDATE_PRIORITY.LOW` 优先级下驱动 `app.render()`。每个回调函数都会接收到 Ticker 实例；将 `deltaTime` 作为与帧率无关的乘数（在 60fps 时约等于 1.0）或使用 `deltaMS` 进行实时计算。

## 快速入门

```ts
app.ticker.add((ticker) => {
  sprite.rotation += 0.01 * ticker.deltaTime;
  sprite.x += (200 / 1000) * ticker.deltaMS;
});

app.ticker.add(
  (ticker) => {
    updatePhysics(ticker.deltaMS);
  },
  undefined,
  UPDATE_PRIORITY.HIGH,
);

app.ticker.maxFPS = 30;
app.ticker.speed = 0.5;

sprite.onRender = () => {
  sprite.scale.x = Math.sin(performance.now() / 500);
};
```

**相关技能：** `pixijs-application`（应用程序设置和 sharedTicker 选项）、`pixijs-performance`（帧率优化）、`pixijs-migration-v8`（v7 Ticker 签名变更）。

## 核心模式

### 时间单位

Ticker 提供了三种计时值，每种值适用于不同的场景：

| 属性    | 类型                          | 是否按速度缩放 | 是否按 minFPS 限制 | 使用场景                                     |
| ------- | ----------------------------- | -------------- | ----------------- | -------------------------------------------- |
| `deltaTime` | 无量纲 (~1.0 在 60fps 时) | 是              | 是               | 与帧率无关的动画乘数                         |
| `deltaMS`   | 毫秒                          | 是              | 是               | 基于时间的计算（像素/秒）                   |
| `elapsedMS` | 毫秒                          | 否               | 否                | 原始测量值，用于分析性能                   |

```ts
import { Application } from "pixi.js";

const app = new Application();
await app.init({ width: 800, height: 600 });

app.ticker.add((ticker) => {
  // deltaTime：无量纲标量，在 60fps 时约等于 1.0
  sprite.rotation += 0.1 * ticker.deltaTime;

  // deltaMS：实际毫秒（按速度缩放，按限制）
  sprite.x += (200 / 1000) * ticker.deltaMS; // 每秒移动 200 像素

  // elapsedMS：原始毫秒（不缩放，无限制）
  console.log(`原始帧时间：${ticker.elapsedMS}ms`);
});
```

**注意：** `deltaTime` 不是毫秒。它是 `deltaMS * Ticker.targetFPMS`，其中 targetFPMS 是 0.06（即 1/16.67）。在 60fps 时，deltaTime 等于 1.0。在 30fps 时，deltaTime 等于 2.0。这会捕获那些将其视为时间值的人。

### 优先级排序和上下文绑定

```ts
import { Application, UPDATE_PRIORITY } from "pixi.js";

const app = new Application();
await app.init({ width: 800, height: 600 });

// 交互（50）> 高（25）> 正常（0）> 低（-25）> 实用（-50）
// app.render() 由 TickerPlugin 在低优先级下注册

app.ticker.add(
  (ticker) => {
    // 物理计算在正常优先级回调之前运行
    updatePhysics(ticker.deltaMS);
  },
  undefined,
  UPDATE_PRIORITY.HIGH,
);

app.ticker.add((ticker) => {
  // 默认优先级（正常 = 0），在 HIGH 之后但渲染之前运行
  updateAnimations(ticker.deltaTime);
});

// 将 `this` 作为第二个参数传递以保留类方法的上下文
class GameSystem {
  public speed = 5;
  public position = 0;

  public update(ticker: Ticker): void {
    this.position += this.speed * ticker.deltaTime;
  }
}

const system = new GameSystem();
app.ticker.add(system.update, system);
app.ticker.remove(system.update, system); // 必须与函数和上下文匹配
```

### 帧率限制

```ts
import { Ticker } from "pixi.js";

const ticker = new Ticker();

ticker.maxFPS = 30; // 限制在 30fps（跳过帧以保持间隔）
ticker.minFPS = 10; // 限制 deltaTime 以确保它不会超过 10fps 的值

// 如果 maxFPS < minFPS，minFPS 会降低以匹配
// 如果 minFPS > maxFPS，maxFPS 会提高以匹配
```

`maxFPS` 跳过更新调用以强制执行上限。`minFPS` 限制 deltaTime/deltaMS 以防止因帧丢失而产生巨大的增量（默认 minFPS 为 10）。

### 对象的 onRender 钩子

```ts
import { Sprite, Assets, Application } from "pixi.js";

const app = new Application();
await app.init({ width: 800, height: 600 });

const texture = await Assets.load("bunny.png");
const sprite = new Sprite(texture);
app.stage.addChild(sprite);

sprite.onRender = (renderer) => {
  sprite.rotation += 0.01;
};
```

`onRender` 在场景图遍历期间调用，在 GPU 渲染之前。当逻辑与特定显示对象相关联时，它是全局 ticker 回调的替代方案。

### Ticker.shared、Ticker.system 和新的 Ticker

```ts
import { Ticker, UPDATE_PRIORITY } from "pixi.js";

// Ticker.shared：单例，autoStart=true，受保护，不会因销毁而消失
const shared = Ticker.shared;

// Ticker.system：由引擎后台任务使用的独立实例，与主场景 ticker 无关。它是一个普通的 Ticker 实例
// （autoStart=true, _protected=true），没有内在优先级；通常按实用优先级添加监听器。
const system = Ticker.system;

// new Ticker()：自定义实例，autoStart=false，你需要管理生命周期
const custom = new Ticker();
custom.autoStart = true; // 当第一个监听器添加时启动
custom.add((ticker) => {
  console.log(ticker.deltaMS);
});

// 一次性回调，触发后自动移除
custom.addOnce(() => console.log("只触发一次"), null, UPDATE_PRIORITY.NORMAL);

// 完成时：
custom.stop();
custom.destroy();
```

`Application` 默认创建自己的 Ticker。在 `app.init()` 中设置 `sharedTicker: true` 以使用 `Ticker.shared`。`Ticker.shared` 和 `Ticker.system` 都是 `_protected` 的，即使你调用 `destroy()` 也不会实际销毁它们。读取 `ticker.FPS` 获取测量的帧率，读取 `ticker.count` 获取当前监听器数量。

### 应用程序生命周期和手动渲染

```ts
import { Application } from "pixi.js";

const app = new Application();
await app.init({ autoStart: false });

// 随时暂停和恢复内置渲染循环。
app.start();
app.stop();

// 或者自己驱动循环（无头模式、按可见性切换、固定时间步长等）
function animate() {
  app.ticker.update(); // 触发注册的回调
  app.render(); // 渲染舞台
  requestAnimationFrame(animate);
}
animate();
```

`app.start()` 和 `app.stop()` 由 `TickerPlugin` 添加，分别映射到 `ticker.start()` / `ticker.stop()`。当你需要在标签页模糊时暂停、运行固定时间步长循环或离屏渲染时，使用 `autoStart: false` 加上你自己的帧驱动器。

### 速度缩放

```ts
import { Application } from "pixi.js";

const app = new Application();
await app.init({ width: 800, height: 600 });

app.ticker.speed = 0.5; // 半速（慢动作）
app.ticker.speed = 2.0; // 双倍速度

// speed 影响 deltaTime 和 deltaMS，但不影响 elapsedMS
```

## 常见错误

### [关键] Ticker 回调期望 delta 作为第一个参数

错误：

```ts
app.ticker.add((dt) => {
  bunny.rotation += dt;
});
```

正确：

```ts
app.ticker.add((ticker) => {
  bunny.rotation += ticker.deltaTime;
});
```

v8 将 Ticker 实例作为回调参数传递，而不是 delta 数字。v7 模式 `(dt) => ...` 编译但 `dt` 是整个 Ticker 对象，因此对其进行算术运算会产生 `NaN`。


### [高] 使用 updateTransform 进行每帧逻辑

错误：

```ts
class MySprite extends Sprite {
  updateTransform() {
    super.updateTransform();
    this.rotation += 0.01;
  }
}
```

正确：

```ts
class MySprite extends Sprite {
  constructor() {
    super();
    this.onRender = this._onRender.bind(this);
  }
  private _onRender() {
    this.rotation += 0.01;
  }
}
```

`updateTransform` 在 v8 中已移除。使用 `onRender` 回调进行每帧对象逻辑。


### [中] 将 deltaTime 视为毫秒

错误：

```ts
app.ticker.add((ticker) => {
  // 尝试每秒移动 100 像素，但 deltaTime 约等于 1.0，不是约等于 16.67
  sprite.x += (100 * ticker.deltaTime) / 1000;
});
```

正确：

```ts
app.ticker.add((ticker) => {
  // 使用 deltaMS 进行基于时间的移动
  sprite.x += (100 / 1000) * ticker.deltaMS;
  // 或者使用 deltaTime 作为帧率乘数
  sprite.x += 1.5 * ticker.deltaTime;
});
```

`deltaTime` 是无量纲标量（在 60fps 时约等于 1.0），不是毫秒。使用 `deltaMS` 进行实时计算。使用 `deltaTime` 作为简单乘数，当你想要“每帧在 60fps”行为时。
