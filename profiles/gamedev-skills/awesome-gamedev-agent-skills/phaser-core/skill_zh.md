# Phaser 4 核心

设置 Phaser 游戏的基础：`Game` 配置、`Scene` 生命周期、资源加载、摄像机以及场景间数据传递。新项目请针对 **Phaser 4.2**；保留现有的 Phaser 3.90 项目在已固定的主版本上，除非用户明确要求迁移。

## 使用场景

- 在开始 Phaser 游戏时使用，配置 `Phaser.Game`、结构化 `Scene`、在 `preload` 中加载资源，或修复场景过渡和共享状态。
- 当项目在 `package.json` 中包含 `phaser` 或 `import Phaser from 'phaser'`，且代码使用 `preload()`/`create()`/`update()` 时使用。

**不使用场景：** 移动、速度、碰撞器、重力或重叠 → 使用 `phaser-arcade-physics`。复杂的刚体模拟使用 Matter physics（这是另一个独立问题）。跨引擎保存/加载模式使用 `save-systems`。

## 核心工作流程

1. **首先检测已安装的主版本。** 读取 `package.json` 和锁文件。为新工作使用 Phaser 4.2；不要无声地重写 Phaser 3 项目为 Phaser 4。
2. **从配置创建游戏。** 使用 `new Phaser.Game(config)`，其中 `type: Phaser.AUTO`（WebGL 带 Canvas 降级）、`width`/`height`，以及 `scene` 数组。第一个场景（以及任何 `active: true` 的场景）会自动启动。
3. **将每个屏幕建模为 `Scene`。** 继承 `Phaser.Scene`，向 `super` 传递唯一的 `key`，并实现生命周期：`init(data)` → `preload()` → `create(data)` → `update(time, delta)`。
4. **在 `preload` 中加载资源，在 `create` 中使用。** 队列中的资源在 `create` 之前不可用。加载器是按场景的；它填充的缓存是全局的。
5. **在 `init()` 中重置每次运行的状态，而不是构造函数。** 场景实例在重启间被重用，所以构造函数设置的字段会保留过时的值。
6. **使用 `this.scene.start/launch/switch/sleep/wake` 在屏幕间切换。** 通过 `this.registry`（全局）或兄弟场景的事件发射器共享数据。
7. **运行并观察。** 上传页面，打开它，确认资源加载（查看网络标签和控制台）和场景切换符合预期，再假设成功。

## 模式

### 1. 游戏配置 + 启动（ES 模块）

```js
// main.js — 一个 Game 拥有渲染器、循环、缓存和场景管理器。
import Phaser from 'phaser';
import BootScene from './scenes/BootScene.js';
import PlayScene from './scenes/PlayScene.js';

const config = {
  type: Phaser.AUTO,            // 如果可用则为 WebGL，否则为 Canvas
  width: 800,
  height: 600,
  backgroundColor: '#1d1d28',
  scale: { mode: Phaser.Scale.FIT, autoCenter: Phaser.Scale.CENTER_BOTH },
  scene: [BootScene, PlayScene] // BootScene 首先启动
};

new Phaser.Game(config);
```

### 2. 具有完整生命周期的场景

```js
// scenes/PlayScene.js
import Phaser from 'phaser';

export default class PlayScene extends Phaser.Scene {
  constructor() {
    super('play');                  // 唯一的场景 key
  }

  init(data) {
    // 在此处重置运行特定状态，以便重启时干净启动。
    this.score = 0;
    this.level = data.level ?? 1;
  }

  preload() {
    // 队列下载。在 create 之前不可用。
    this.load.image('player', 'assets/player.png');
    this.load.spritesheet('coin', 'assets/coin.png', { frameWidth: 16, frameHeight: 16 });
  }

  create() {
    this.player = this.add.sprite(400, 300, 'player');
    this.scoreText = this.add.text(10, 10, 'Score: 0', { fontSize: '20px', color: '#fff' });
    this.cursors = this.input.keyboard.createCursorKeys();
  }

  update(time, delta) {
    // delta 是自上一帧以来的毫秒数；除以 1000 转换为秒。
    const speed = 200 * (delta / 1000);
    if (this.cursors.left.isDown)  this.player.x -= speed;
    if (this.cursors.right.isDown) this.player.x += speed;
  }
}
```

### 3. 跨场景数据 + 事件

```js
// 注册表是每个场景共享的全局 DataManager。
this.registry.set('coins', 0);                 // 在任何场景中
const coins = this.registry.get('coins');      // 任何地方都可以读取

// 响应注册表变化（例如，HUD 场景监听游戏玩法）：
this.registry.events.on('changedata-coins', (parent, value) => {
  this.coinText.setText(`Coins: ${value}`);
});

// 直接通过另一个正在运行场景的事件发射器与其通信：
const ui = this.scene.get('hud');
ui.events.emit('show-message', 'Level cleared!');
```

### 4. 场景过渡（选择正确的动词）

```js
this.scene.start('gameover', { score: this.score }); // 停止当前场景，启动目标
this.scene.launch('hud');        // 并行运行第二个场景（叠加 HUD）
this.scene.switch('menu');       // 暂停当前场景，启动/唤醒目标
this.scene.pause();              // 暂停更新但保留渲染（模态）
this.scene.sleep();              // 停止更新和渲染，保留状态以唤醒
```

### 5. 跟随玩家的摄像机

```js
this.cameras.main.setBounds(0, 0, 1600, 1200);  // 世界大小
this.cameras.main.startFollow(this.player, true, 0.1, 0.1); // 平滑插值跟随
this.cameras.main.setZoom(1.5);
```

## 陷阱

- **在 `create`/`update` 中资源是 `undefined`** → 你忘记在 `preload` 中队列它们，或使用了错误的 key。加载器在 `preload` 和 `create` 之间运行。
- **状态在重启间泄漏** → 你在构造函数中设置了字段。场景实例被重用；在 `init()` 中重置运行状态，并在 `shutdown` 中清空数组。
- **`this.scene.start` vs `this.scene.launch`** → `start` 停止调用场景；`launch` 与目标场景并行运行。使用 `start` 启动 HUD 会隐藏游戏。
- **回调中的 `this` 不正确** → 箭头函数保留场景的 `this`；普通 `function` 回调需要上下文参数或 `.bind(this)`。
- **Phaser 2 教程不适用** → "状态" 在 Phaser 3 中被重命名为 "场景"，每个场景拥有自己的系统（输入、摄像机、缓动），而不是全局的 Game World。
- **Phaser 3 自定义管线在 Phaser 4 中失败** → Phaser 4 重建了渲染器，并替换了旧的 FX/管线扩展点。根据 Phaser 4 指南迁移自定义着色器和渲染器插件；不要机械地复制内部渲染器代码。
- **无渲染 / 黑屏** → 确认已挂载 canvas，`width`/`height` 已设置，且场景确实启动（检查 `game.scene.dump()` 输出）。

## 参考

- 对于完整场景状态机（暂停/恢复 vs 睡眠/唤醒 vs 停止/启动、重启状态问题、移除/替换场景），请阅读 `references/scene-flow.md`。

## 相关技能

- `phaser-arcade-physics` — 速度、重力、碰撞器、重叠和分组。
- `input-systems` — 可重新绑定、多设备输入架构（引擎无关）。
- `pixijs-rendering` / `threejs-scene-setup` — 其他浏览器渲染堆栈。
- `platformer` / `puzzle` — 组合 Phaser 技能的流派模板。
