# Godot 2D 移动 (4.x)

使用 `CharacterBody2D` 和无参数的 `move_and_slide()` 构建 2D 角色控制器。目标 **Godot 4.7**。

## 何时使用

- 当编写移动和碰撞的 2D 玩家/敌人脚本时：平台游戏（重力 + 跳跃）或俯视视角（自由 8 向），斜坡行走或墙/地面检测。
- 当 `move_and_slide()` "无效果"，角色会穿过地面，或 `is_on_floor()` 始终为 `false` 时。

**不使用时：** 动态刚体、区域、射线检测、碰撞层 → `godot-physics`；基于瓦片的关卡 → `godot-tilemap`；完整平台游戏模板 → `platformer` 类型技能；引擎无关感调优 → `physics-tuning`。

## 核心工作流程

1. **使用 `CharacterBody2D`** 并添加 `CollisionShape2D` 子节点。它是脚本驱动的：它不会自行下落或对力做出反应。
2. **设置 `velocity` 属性，然后调用 `move_and_slide()`**（4.x 中无参数）。该方法读取 `velocity`，移动角色，沿表面滑动，并更新 `velocity` 以反映实际发生的情况。
3. **在 `_physics_process(delta)` 中执行** — `move_and_slide()` 内部使用物理步的 delta，因此不要自行将 `velocity` 乘以 `delta`。
4. **平台游戏：** 每次循环时向 `velocity.y` 添加重力，通过在 `is_on_floor()` 时将 `velocity.y` 设置为负值来跳跃。
5. **俯视视角：** 从输入构建方向并按速度缩放；设置 `motion_mode = MOTION_MODE_FLOATING` 以消除“地面/墙”的区分。
6. **读取结果** 使用 `is_on_floor()`、`is_on_wall()`、`get_wall_normal()` 和 `get_slide_collision(i)` 在调用后。

## 模式

### 1. 平台游戏控制器（重力、跳跃、斜坡）

```gdscript
extends CharacterBody2D

@export var speed := 200.0
@export var jump_velocity := -400.0
@export var gravity := 1200.0          # 像素/秒²（按需调整）

func _physics_process(delta: float) -> void:
    # 空中时应用重力。
    if not is_on_floor():
        velocity.y += gravity * delta

    # 仅在着地时跳跃（输入动作在项目设置 > 输入映射中设置）。
    if Input.is_action_just_pressed("jump") and is_on_floor():
        velocity.y = jump_velocity

    # 水平输入：-1、0 或 1。
    var dir := Input.get_axis("move_left", "move_right")
    if dir != 0.0:
        velocity.x = dir * speed
    else:
        velocity.x = move_toward(velocity.x, 0.0, speed)   # 减速至停止

    move_and_slide()   # 4.x：无参数；使用并更新 `velocity`
```

### 2. 俯视 8 向移动

```gdscript
extends CharacterBody2D

@export var speed := 220.0

func _ready() -> void:
    motion_mode = CharacterBody2D.MOTION_MODE_FLOATING  # 无地面/天花板概念

func _physics_process(_delta: float) -> void:
    # get_vector 返回从四个输入动作获得的规范化向量。
    var input := Input.get_vector("move_left", "move_right", "move_up", "move_down")
    velocity = input * speed
    move_and_slide()
```

### 3. 移动后读取滑动碰撞

```gdscript
func _physics_process(delta: float) -> void:
    # ... 设置 velocity ...
    move_and_slide()
    for i in get_slide_collision_count():
        var c := get_slide_collision(i)
        var other := c.get_collider()
        if other and other.is_in_group("enemies"):
            take_damage(1)        # 移动时触碰到敌人
```

### 4. Coyote 时间（离开平台后宽容的跳跃）

```gdscript
@export var coyote_time := 0.1
var _coyote := 0.0

func _physics_process(delta: float) -> void:
    if not is_on_floor():
        velocity.y += gravity * delta
        _coyote -= delta
    else:
        _coyote = coyote_time

    if Input.is_action_just_pressed("jump") and _coyote > 0.0:
        velocity.y = jump_velocity
        _coyote = 0.0
    # ... 水平输入 + move_and_slide() ...
```

## 陷阱

- **3.x 签名已消失。** `move_and_slide(velocity)`（返回新 velocity）已被移除。在 4.x 中设置 `velocity` 属性并调用无参数的 `move_and_slide()`。`move_and_slide(velocity, Vector2.UP)` 将无法解析。
- **将 velocity 乘以 delta。** `move_and_slide()` 已考虑物理 delta。设置 `velocity = dir * speed * delta` 会使角色爬行。
- **在 `_process` 中移动** 而不是 `_physics_process` 会导致帧率依赖的、抖动的运动。始终在 `_physics_process` 中移动。
- **`is_on_floor()` 始终为 `false`** 当 `up_direction` 错误（默认 `Vector2.UP`）、没有 `CollisionShape2D` 或本帧未调用 `move_and_slide()` 时。
- **穿过地面** 通常意味着碰撞形状缺失/尺寸为零、地面刚体在当前角色掩码不包含的层上，或通过 `position +=` 而不是 velocity + `move_and_slide()` 移动角色。
- **空闲时斜坡滑动：** 保持 `floor_stop_on_slope = true`（默认）并设置 `floor_snap_length` 以使角色吸附在向下斜坡上。

## 参考

- 对于单向平台、移动平台、跳跃缓冲、可变跳跃高度和 `move_and_collide()`（手动碰撞响应），请阅读 `references/controller-recipes.md`。

## 相关技能

- `godot-physics` — 碰撞层/掩码、区域、射线检测、刚体。
- `godot-tilemap` — 构建角色行走的关卡。
- `godot-animation` — 从移动状态驱动精灵/骨骼动画。
- `camera-systems` — 跟随相机、死区、和跟踪此角色的预读。
- `platformer` / `input-systems` — 完整类型模板和可重新绑定输入。
