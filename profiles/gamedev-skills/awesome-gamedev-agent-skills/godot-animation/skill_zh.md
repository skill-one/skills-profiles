# Godot 动画 (4.x)

选择并驱动合适的动画工具：`AnimationPlayer`（片段）、`AnimationTree`（混合/状态机）或 `Tween`（简短的程序性移动）。目标 **Godot 4.7**。

## 何时使用

- 在播放关键帧动画、混合行走/奔跑/待机状态、动画精灵表或通过代码缓动 UI/对象时使用。

**不使用时**：决定播放哪个状态的移动逻辑 → `godot-2d-movement`；UI 布局（相对于 UI 缓动）→ `godot-ui-control`；着色器驱动效果 → `godot-shaders`。

## 核心工作流程

1. **选择工具：**
   - `AnimationPlayer` — 创建关键帧片段（变换、属性、方法调用、音频，甚至其他动画）。片段数据的权威来源。
   - `AnimationTree` — 在运行时通过状态机和/或混合空间混合和过渡这些片段。需要 `AnimationPlayer` 来提取片段。
   - `Tween` — 代码中的程序性插值（`create_tween()`）；理想用于 UI 弹出、淡入淡出和一次性移动。
2. **对于 2D 精灵表：** 使用 `AnimatedSprite2D` + `SpriteFrames`，或在 `AnimationPlayer` 中关键帧 `frame` 属性。
3. **对于角色：** 在 `AnimationPlayer` 中构建片段，然后添加一个 `AnimationTree`（`active = true`），设置其 `anim_player`，并设计 `AnimationNodeStateMachine` 或 `AnimationNodeBlendSpace2D` 作为树根。
4. **通过代码驱动过渡** 通过播放对象 (`travel`) 或通过设置混合参数。
5. **通过 `animation_finished` 信号响应片段事件** 并调用/方法轨道。

## 模式

### 1. AnimationPlayer：播放片段并等待

```gdscript
@onready var anim: AnimationPlayer = $AnimationPlayer

func attack() -> void:
    anim.play("attack")
    await anim.animation_finished     # 在片段结束后继续
    anim.play("idle")
```

### 2. AnimationTree 状态机：在状态之间切换

```gdscript
@onready var tree: AnimationTree = $AnimationTree

func _ready() -> void:
    tree.active = true                # 树驱动动画；AnimationPlayer 是来源

func set_state(state: StringName) -> void:
    # 播放对象控制 AnimationNodeStateMachine 根。
    var sm: AnimationNodeStateMachinePlayback = tree.get("parameters/playback")
    sm.travel(state)                  # 使用图的连接进行过渡

func _physics_process(_d: float) -> void:
    set_state(&"run" if velocity.length() > 5.0 else &"idle")
```

### 3. 混合空间：通过 2D 参数混合运行方向

```gdscript
# 根是一个名为 "Move" 的 AnimationNodeBlendSpace2D，其中放置了待机和运行点。
func update_locomotion(input_dir: Vector2) -> void:
    # 参数路径 = "parameters/<节点名称>/blend_position"。
    tree.set("parameters/Move/blend_position", input_dir)
```

### 4. Tween：淡入淡出并缩放 UI 元素（代码驱动）

```gdscript
func pop_in(node: Control) -> void:
    node.scale = Vector2.ZERO
    node.modulate.a = 0.0
    var tw := create_tween()                          # 绑定到此节点的树
    tw.set_parallel(true)                             # 一起运行两个缓动
    tw.tween_property(node, "scale", Vector2.ONE, 0.2) \
      .set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
    tw.tween_property(node, "modulate:a", 1.0, 0.2)   # 通过 ":" 缓动子属性
```

## 陷阱

- **`AnimationTree.active` 设置为 false** → 什么都不会动画，`travel()` 看起来什么都没做。设置 `active = true` 并分配 `anim_player` 路径。
- **错误的参数路径。** 混合/条件路径是 `"parameters/<节点名称>/..."`，必须与树中的节点名称完全匹配（例如 `"parameters/playback"`、`"parameters/Move/blend_position"`）。一个拼写错误会静默无操作。
- **AnimationPlayer 和 AnimationTree 冲突。** 当 `AnimationTree` 处于活动状态时，不要也为相同轨道调用 `AnimationPlayer.play()` — 让树拥有播放权。
- **3.x Tween 节点已消失。** 4.x 中没有 `Tween` 节点可以添加；使用 `create_tween()` 在代码中创建缓动（返回 `Tween`）。它们自动启动并释放自己。
- **重用已完成的 tween。** Tween 是一次性；再次调用 `create_tween()` 以进行新的动画。使用 `set_loops()` 进行重复。
- **`yield`/`yield(anim, "...")` 已消失。** 使用 `await anim.animation_finished`。
- **子属性 tween** 使用冒号：`"modulate:a"`、`"position:x"`。缓动整个属性会覆盖兄弟。

## 参考

- 对于状态机过渡/条件、根运动、一次性/混合节点、方法 & 调用轨道、`SpriteFrames`/`AnimatedSprite2D` 和 Tween 缓动/链式/回调，请阅读 `references/animation-tree-and-tween.md`。

## 相关技能

- `godot-2d-movement` — 提供选择动画的速度/状态。
- `godot-ui-control` — Tweens 动画的 UI。
- `godot-3d-essentials` — 由 AnimationTree 驱动的 3D 角色场景。
- `game-ai` — 与动画状态镜像的状态机。
