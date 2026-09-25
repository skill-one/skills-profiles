# Phaser 4 弹射物理

为 Phaser 游戏（使用轻量级**弹射物理**引擎，仅支持 AABB 矩形和圆形）添加移动和碰撞。新项目请使用 **Phaser 4.2**；编辑现有项目前请检查已安装的版本。

## 使用场景

- 用于俯视或平台游戏移动、速度/加速度/重力、弹跳、世界边界以及精灵、组、瓦片之间的碰撞/重叠解决。
- 当场景启用 `physics: { default: 'arcade' }` 且代码调用 `this.physics.add.*`、`body.setVelocity` 或 `this.physics.add.collider` 时使用。

**不适用场景：**游戏配置、场景结构、资源加载或摄像机 → 使用 `phaser-core`。铰链、弹簧、复杂多边形或堆叠刚体 → 使用 Matter 物理引擎（不同引擎；弹射和 Matter 刚体不交互）。关于引擎无关的触感调整，请参考 `physics-tuning`。

## 核心工作流程

1. **启用世界。** 在游戏或场景配置中设置 `physics: { default: 'arcade', arcade: { gravity: {...}, debug: true } }`。构建时开启 `debug` 以查看刚体轮廓和速度向量。
2. **为精灵添加刚体。** 使用 `this.physics.add.sprite(...)`（动态）或 `this.physics.add.staticImage(...)`（静态）创建，或使用 `this.physics.add.existing(obj)` 附加到现有对象。
3. **通过刚体驱动，而非直接设置 `x`/`y`。** 使用 `setVelocity`、`setAcceleration`、重力、`setBounce` 和 `setCollideWorldBounds`。引擎每步从速度积分位置（已帧率无关）。
4. **解决交互。** `this.physics.add.collider(a, b)` 分离刚体；`this.physics.add.overlap(a, b, cb)` 检测但不分离（拾取物、触发器）。传递回调函数以响应。
5. **分组多个对象。** 使用 `this.physics.add.group()`（动态）或 `staticGroup()`（平台）使一个碰撞器调用处理所有成员。
6. **检查地面接触** 在跳跃前使用 `body.onFloor()` / `body.blocked.down`。使用 `debug: true` 运行并确认刚体、接触点和边界。

## 模式

### 1. 启用弹射物理（游戏配置）

```js
const config = {
  type: Phaser.AUTO,
  width: 800, height: 600,
  physics: {
    default: 'arcade',
    arcade: {
      gravity: { x: 0, y: 600 },  // 俯视？使用 { x: 0, y: 0 }
      debug: false                // true 在构建时绘制刚体+速度
    }
  },
  scene: [PlayScene]
};
new Phaser.Game(config);
```

### 2. 俯视移动（输入速度）

```js
create() {
  this.player = this.physics.add.sprite(400, 300, 'player');
  this.player.setCollideWorldBounds(true);
  this.cursors = this.input.keyboard.createCursorKeys();
}

update() {
  const speed = 220;
  const body = this.player.body;
  body.setVelocity(0);                              // 每帧重置
  if (this.cursors.left.isDown)  body.setVelocityX(-speed);
  if (this.cursors.right.isDown) body.setVelocityX(speed);
  if (this.cursors.up.isDown)    body.setVelocityY(-speed);
  if (this.cursors.down.isDown)  body.setVelocityY(speed);
  body.velocity.normalize().scale(speed);           // 保持对角线速度一致
}
```

### 3. 平台跳跃（重力+地面检测）

```js
create() {
  this.player = this.physics.add.sprite(100, 450, 'player');
  this.player.setCollideWorldBounds(true);

  // 静态平台：每个一个刚体，碰撞不会移动。
  this.platforms = this.physics.add.staticGroup();
  this.platforms.create(400, 568, 'ground');
  this.physics.add.collider(this.player, this.platforms);

  this.cursors = this.input.keyboard.createCursorKeys();
}

update() {
  const onGround = this.player.body.blocked.down; // 或 this.player.body.onFloor()
  if (this.cursors.left.isDown)  this.player.setVelocityX(-160);
  else if (this.cursors.right.isDown) this.player.setVelocityX(160);
  else this.player.setVelocityX(0);

  if (this.cursors.up.isDown && onGround) this.player.setVelocityY(-450);
}
```

### 4. 碰撞器 vs 重叠（分离 vs 检测）

```js
// 推开并响应：玩家 vs 敌人。
this.physics.add.collider(this.player, this.enemies, (player, enemy) => {
  this.handleHit(player, enemy);
});

// 检测不推开：收集金币。第 4 个参数是可选的
// 过程回调，返回布尔值以在主回调前过滤配对。
this.physics.add.overlap(this.player, this.coins, (player, coin) => {
  coin.disableBody(true, true);              // 禁用+隐藏
  this.registry.inc('score', 10);
});
```

### 5. 一组移动对象

```js
this.bullets = this.physics.add.group({
  defaultKey: 'bullet',
  maxSize: 30                  // 池大小；重用而非分配
});

fire(x, y) {
  const bullet = this.bullets.get(x, y);     // 如果可用，重用已死亡的子弹
  if (!bullet) return;
  bullet.enableBody(true, x, y, true, true);
  bullet.setVelocityY(-500);
}
```

## 陷阱

- **精灵忽略物理** → 它使用 `this.add.sprite` 而非 `this.physics.add.sprite`（或 `this.physics.add.existing(obj)`）添加，因此没有刚体。
- **直接设置 `sprite.x` 与引擎冲突** → 使用 `setVelocity`/`setAcceleration` 移动动态刚体。直接位置写入可能穿透碰撞器。
- **对角线移动更快** → 独立的 X 和 Y 速度相加；归一化速度向量并缩放到目标速度。
- **平台被玩家推动** → 使用 `staticGroup`，或对动态平台设置 `body.setImmovable(true)`。
- **`onFloor()` 始终为 false** → 刚体需要与某物碰撞；在检查前添加对地面/平台的碰撞器，并确保重力开启。
- **移动了静态刚体但碰撞陈旧** → 静态刚体不自动同步；调用 `body.updateFromGameObject()`（或游戏对象上的 `refreshBody()`）。
- **每帧添加碰撞器** → 在 `create` 中注册 `collider`/`overlap`，而非 `update`。

## 参考

- 关于刚体解剖和调优（摩擦力、弹跳、最大速度、自定义 `setSize`/`setCircle`/`setOffset` 碰撞框、碰撞分类/掩码，以及 `worldbounds` 事件），请阅读 `references/bodies-and-collision.md`。

## 相关技能

- `phaser-core` — 游戏配置、场景、加载器、摄像机（必备设置）。
- `physics-tuning` — 引擎无关的触感（固定步长、隧道、抖动）。
- `platformer` / `tower-defense` — 使用此技能的游戏类型。
- `level-design` — 布置这些刚体碰撞的瓦片/平台几何形状。
