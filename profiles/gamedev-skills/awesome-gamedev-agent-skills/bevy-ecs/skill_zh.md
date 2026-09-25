# Bevy ECS

围绕实体组件系统（Entity Component System）在 Rust 中构建 Bevy 游戏：`App` 和插件、组件和资源、带查询的系统、调度以及帧率无关的更新。新示例针对 **Bevy 0.19** 版本。如果项目已经固定了另一个版本，请保留该版本并使用其匹配的迁移指南。

## 使用场景

- 当连接 Bevy `App`、定义 `Component`/`Resource` 类型、编写查询实体的系统、排序/过滤系统或修复借用冲突恐慌和帧依赖移动时使用。
- 当 `Cargo.toml` 依赖 `bevy` 且代码调用 `App::new()`、`add_systems`、`Query` 或 `Commands` 时使用。

**不建议使用的情况**：这是 ECS 核心。深度渲染、自定义着色器/管线、UI 布局和音频是独立的问题。对于引擎无关的 AI 或程序化算法，与 `game-ai` / `procedural-gen` 配合使用。

## 核心工作流程

1. **检测并固定版本**。首先读取 `Cargo.toml` 和 `Cargo.lock`。对于新项目使用 `bevy = "0.19"`；切勿在 Bevy 小版本之间无声地迁移现有项目。将匹配的文档和迁移指南视为真理。
2. **构建 `App`**。`App::new().add_plugins(DefaultPlugins)` 提供窗口、输入、渲染、时间等。将系统注册到调度中：`Startup`（一次性）和 `Update`（每帧）。
3. **将数据建模为组件，全局建模为资源**。`#[derive(Component)]` 用于每个实体的数据；`#[derive(Resource)]` 用于唯一数据（分数、设置、`Time` 时钟）。在 0.19 中 `Resource` 扩展了 `Component`，因此不要派生两者。
4. **将系统编写为普通函数**。参数声明数据访问：`Query<...>` 用于实体，`Res<T>`/`ResMut<T>` 用于资源，`Commands` 用于延迟生成/销毁。当它们的访问不冲突时，系统并行运行。
5. **通过 `time.delta_secs()` 驱动移动**，这样速度与帧率无关。
6. **仅对必须排序的内容进行排序**，使用 `.chain()` 或显式约束；使用 `run_if` 门控系统。将相关设置分组到 `Plugin` 中。使用 `cargo run` 构建，并读取恐慌——Bevy 在启动时报告冲突的查询。

## 模式

### 1. Cargo.toml + 最小化 App

```toml
# Cargo.toml — 固定版本；API 在小版本之间有所不同。
[dependencies]
bevy = "0.19"
```

```rust
// main.rs
use bevy::prelude::*;

fn main() {
    App::new()
        .add_plugins(DefaultPlugins)            // 窗口、输入、渲染、时间等
        .add_systems(Startup, setup)            // 在启动时运行一次
        .add_systems(Update, move_players)      // 每帧运行
        .run();
}
```

### 2. 组件、资源和生成

```rust
#[derive(Component)]
struct Player;

#[derive(Component)]
struct Velocity(Vec2);

#[derive(Resource)]
struct Score(u32);

fn setup(mut commands: Commands) {
    commands.insert_resource(Score(0));

    // Camera2d 是一个组件，带有必需的组件（在 0.16 中移除了包）；生成它将自动引入 Transform、Camera 等。
    commands.spawn(Camera2d);

    // 作为组件的元组生成实体。
    commands.spawn((
        Player,
        Velocity(Vec2::new(150.0, 0.0)),
        Transform::from_xyz(0.0, 0.0, 0.0),
    ));
}
```

### 3. 带查询和 Time 资源的系统

```rust
// 遍历同时具有 Velocity 和 Transform 的每个实体；修改 Transform。
fn move_players(time: Res<Time>, mut query: Query<(&Velocity, &mut Transform)>) {
    for (velocity, mut transform) in &mut query {
        // delta_secs() 是 f32 秒（在 0.16 中从 delta_seconds() 更名）。
        transform.translation += velocity.0.extend(0.0) * time.delta_secs();
    }
}
```

### 4. 查询过滤器（With / Without / Changed）

```rust
// 仅查询标记为 Player 的实体（Player 组件本身不被读取）。
fn aim_player(mut q: Query<&mut Transform, With<Player>>) { /* ... */ }

// 将两个可变的 Transform 查询分离，以避免在运行时冲突。
fn separate(
    mut players: Query<&mut Transform, With<Player>>,
    mut enemies: Query<&mut Transform, Without<Player>>,
) { /* ... */ }

// 仅在 Health 自上次运行以来发生变化时反应（变化检测）。
fn on_health_change(q: Query<&Health, Changed<Health>>) {
    for health in &q { /* 更新 HUD 等 */ }
}
```

### 5. 资源：读取和写入

```rust
fn add_points(mut score: ResMut<Score>) {
    score.0 += 10;                 // ResMut = 写入访问
}

fn show_score(score: Res<Score>) {
    info!("score: {}", score.0);   // Res = 读取访问
}
```

### 6. 排序、运行条件和插件

```rust
fn main() {
    App::new()
        .add_plugins((DefaultPlugins, GameplayPlugin))
        // .chain() 强制顺序：伤害在死亡检查之前解决。
        .add_systems(Update, (apply_damage, check_deaths).chain())
        // run_if 在每帧上基于条件门控系统。
        .add_systems(Update, spawn_wave.run_if(wave_timer_finished))
        .run();
}

struct GameplayPlugin;
impl Plugin for GameplayPlugin {
    fn build(&self, app: &mut App) {
        app.insert_resource(Score(0))
           .add_systems(Startup, setup)
           .add_systems(Update, (move_players, add_points));
    }
}
```

## 陷阱

- **找不到 `delta_seconds()`** → 它在 0.16 中被重命名为 `time.delta_secs()`（和 `elapsed_secs()`）。使用旧名称会导致编译失败。
- **移动速度随帧率缩放** → 将每帧变化乘以 `time.delta_secs()`。切勿假设固定的帧时间。
- **恐慌："冲突访问" / "&mut T 和 &mut T"** → 一个系统中的两个 `Query` 同时写入相同的组件，或者一个读取时另一个写入重叠的实体。使用 `With`/`Without` 使它们分离，或使用 `ParamSet`。
- **找不到 `Camera2dBundle`/`SpriteBundle`** → 包在 0.15 中被弃用，在 0.16 中被移除。
  直接生成组件（`Camera2d`、`Sprite`、`Transform`）；必需的组件将自动填充其余部分。
- **"trait `Component` 没有实现"** → 你忘了 `#[derive(Component)]`（或 `#[derive(Resource)]` 用于资源）。
- **生成的实体在同一帧中不被后续查询看到** → `Commands` 是延迟的，在下一个同步点应用。在后续系统中读取实体，而不是生成它的那个系统。
- **系统顺序假设但未强制** → 系统默认并行运行。如果 `B` 必须跟随 `A`，添加 `(A, B).chain()` 或显式排序约束。
- **在 0.19 中派生 `Resource` 和 `Component`** → `Resource` 现在扩展了 `Component`；仅派生 `Resource` 以避免冲突实现。
- **复制粘贴旧 Bevy 代码片段** → API 在小版本之间会变化。缓冲事件系统在最近版本中变成了消息系统。针对你固定的版本，对照文档和迁移指南进行验证；不要混用版本。

## 参考

- 对于调度和 `SystemSet` 排序、`States`/`OnEnter`/`OnExit`、变化检测、`Commands` 生命周期和同步点、`ParamSet` 用于冲突查询，以及事件/观察者 API 的版本说明，请阅读 `references/queries-and-scheduling.md`。

## 相关技能

- `game-ai` — FSMs/行为树/转向作为可在 ECS 中实现的便携概念。
- `procedural-gen` — 噪声/RNG/生成算法从系统驱动。
- `pygame-core` / `love2d-core` — 较轻量级的引擎，适用于较小的项目。
