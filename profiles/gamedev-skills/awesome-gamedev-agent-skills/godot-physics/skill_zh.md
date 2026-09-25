# Godot 物理引擎 (4.x, 2D + 3D)

选择合适的物理体，连接碰撞层/掩码，检测重叠，以及投射射线。这些概念适用于 2D 和 3D（只需切换 `2D`/`3D` 后缀）。目标版本为 **Godot 4.7**。

## 何时使用

- 在选择物体类型、设置碰撞层/掩码以使正确物体发生碰撞、使用 `Area` 检测重叠（触发器、伤害框）、向 `RigidBody` 施加力/冲量，或进行用于视线/地面检测的射线投射时使用。
- **不适用场景**：运动学角色控制器（`move_and_slide`）→ `godot-2d-movement`；瓦片碰撞设置 → `godot-tilemap`；调整物理效果（时间步长、质量、抖动）→ `physics-tuning`。

## 核心工作流程

1. **选择物体类型：**
   - `StaticBody` — 永不移动（地板、墙壁）。可发生碰撞，无模拟。
   - `RigidBody` — 完全模拟（重力、力、弹跳）。不要直接设置其 `position`；应用力/冲量或设置 `linear_velocity`。
   - `CharacterBody` — 脚本驱动的运动学（参见 `godot-2d-movement`）。
   - `Area` — 检测重叠并可以施加重力/阻尼；无实体碰撞。
   每个物体都需要一个 `CollisionShape`（或 `CollisionPolygon`）子节点。
2. **配置层和掩码。** 物体位于其 **层** 上，并扫描其 **掩码**。只有当其中一个物体的层在另一个物体的掩码中时，两个物体才会交互。在项目设置 > 层名称中命名层以保持清晰。
3. **使用 `Area` 信号（`body_entered`、`area_entered`）检测重叠。**
4. **使用力/冲量驱动 `RigidBodies`**，或重写 `_integrate_forces` 以实现完全控制。
5. **使用 `RayCast2D/3D` 节点（每帧轮询）或从代码中发起一次性空间状态查询进行射线投射。**

## 模式

### 1. 碰撞层与掩码（从代码设置）

```gdscript
# 玩家位于层 1，扫描层 2（墙壁）和层 3（敌人）。
func _ready() -> void:
    set_collision_layer_value(1, true)    # 我位于层 1
    set_collision_mask_value(2, true)     # 我与层 2 的物体发生碰撞
    set_collision_mask_value(3, true)     # ...以及层 3
    # 也可以使用位字段形式：collision_layer = 1; collision_mask = 0b110
```

### 2. `Area2D` 作为触发器 / 伤害框

```gdscript
extends Area2D                            # 例如，一个伤害区域

func _ready() -> void:
    body_entered.connect(_on_body_entered)
    area_entered.connect(_on_area_entered)

func _on_body_entered(body: Node2D) -> void:
    if body.has_method("take_damage"):
        body.take_damage(10)

func _on_area_entered(area: Area2D) -> void:
    print("重叠区域: ", area.name)
```

### 3. 向 `RigidBody3D` 施加力与冲量

```gdscript
extends RigidBody3D

func push(direction: Vector3) -> void:
    apply_central_impulse(direction * 8.0)     # 瞬时速度变化

func _physics_process(_delta: float) -> void:
    apply_central_force(Vector3.FORWARD * 4.0) # 持续力（每帧）
    # 不要直接设置 `position` 来移动 `RigidBody`；使用力/冲量或设置 linear_velocity。如需固定位置，使用 freeze=true。
```

### 4. 两种射线投射方式

```gdscript
# A) `RayCast2D` 节点：启用它，然后在物理更新后轮询。
@onready var ray: RayCast2D = $RayCast2D    # 在编辑器中设置 target_position

func _physics_process(_delta: float) -> void:
    if ray.is_colliding():
        var hit := ray.get_collider()
        var point := ray.get_collision_point()

# B) 代码中的单次查询（无需节点）。
func ground_under(global_from: Vector2) -> Dictionary:
    var space := get_world_2d().direct_space_state
    var query := PhysicsRayQueryParameters2D.create(global_from, global_from + Vector2(0, 64))
    query.collision_mask = 1                 # 仅层 1
    return space.intersect_ray(query)        # 如果未命中，则为 {}，否则为 collider/position/normal
```

## 陷阱

- **层与掩码混淆** 是最常见的错误。层 = "我是谁"；掩码 = "我在寻找谁"。要使 A 检测到 B，B 的层必须在 A 的掩码中。检测可以是单向的。
- **通过 `position` 移动 `RigidBody`** 会与求解器冲突并导致隧道/抖动。使用冲量/力、设置 `linear_velocity` 或 `freeze` 它。要传送，设置位置并在 `_integrate_forces` 中将速度置零。
- **`Area` 在未设置监控或可监控，或层/掩码不重叠时不会触发**。`monitoring` 必须开启才能检测；`monitorable` 允许其他物体检测它。
- **`RayCast2D/3D` 读取陈旧或无数据** 如果 `enabled` 为 false，或在物理更新前读取 — 在 `_physics_process` 中读取，并在同一帧移动后调用 `force_raycast_update()`。
- **忘记 `CollisionShape`**（或将其留空）意味着物体永远不会发生碰撞。
- **快速物体穿过薄墙**；在 `RigidBody` 上启用 **连续碰撞检测**（`continuous_cd`）或使用基于射线的检查。
- **`intersect_ray` 排除了自身物体？** 传递 `query.exclude = [self.get_rid()]`（一个 `Array[RID]`，不是节点数组）以跳过自碰撞。

## 参考

- 关于 `_integrate_forces`、关节、单向碰撞、`PhysicsServer` 直接访问、形状查询（`intersect_shape`）和 3D `move_and_collide`，请阅读 `references/bodies-and-queries.md`。

## 相关技能

- `godot-2d-movement` — 运动学 `CharacterBody2D` 控制器。
- `godot-tilemap` — 瓦片碰撞形状及其层。
- `physics-tuning` — 引擎无关的物理效果：时间步长、质量、阻力、CCD。
- `godot-3d-essentials` — 这些物体存在的 3D 场景设置。
