---
name: godot-physics
description: 使用 Godot 4.7 的 2D 和 3D 物理体及检测：RigidBody、StaticBody、Area 和 CharacterBody；碰撞层与掩码；接触/重叠信号；以及射线（RayCast 节点和直接空间状态查询）。在配置碰撞层/掩码、检测 Area2D/Area3D 的重叠、对 RigidBody 施加力或在 Godot 项目（包含物理体的 .tscn）中投射射线时使用，包括运行 Jolt Physics 的 3D 项目（4.6+ 创建项目的默认 3D 引擎）。
---

# Godot 物理引擎 (4.x, 2D + 3D)

选择合适的物理体，连接碰撞层/掩码，检测重叠，以及投射射线。这些概念适用于 2D 和 3D（只需切换 `2D`/`3D` 后缀）。目标版本为 **Godot 4.7**。在 3D 中，使用 Godot 4.6 或更高版本创建的项目默认运行 **Jolt Physics**；较旧的项目保持 **GodotPhysics3D**，除非有人将其切换。2D 始终使用 Godot 自身的 2D 引擎。

## 何时使用

- 在选择身体类型、设置碰撞层/掩码以使正确的事物发生碰撞、使用 `Area` 检测重叠（触发器、伤害框）、将力/冲量应用于 `RigidBody`，或投射射线进行视线/地面检查时使用。

**不使用时的场景**：运动学角色控制器（`move_and_slide`）→ `godot-2d-movement`；瓦片碰撞设置 → `godot-tilemap`；调整物理的触感（时间步长、质量、抖动）→ `physics-tuning`。

## 核心工作流程

1. **对于 3D，在调试行为之前检查运行哪个引擎**：项目设置 > 物理 > 3D > 物理引擎（在 `project.godot` 中的 `[physics]` `3d/physics_engine="Jolt Physics"`）。API 是相同的，但关节、射线投射面索引、运动学接触和碰撞边距的表现不同（参见常见问题）。
2. **选择身体类型**：
   - `StaticBody` — 永不移动（地板、墙壁）。发生碰撞，无模拟。
   - `RigidBody` — 完全模拟（重力、力、弹跳）。不要直接设置其 `position`；应用力/冲量或设置 `linear_velocity`。
   - `CharacterBody` — 脚本驱动的运动学（参见 `godot-2d-movement`）。
   - `Area` — 检测重叠并可以应用重力/阻尼；无实体碰撞。
   每个身体都需要一个 `CollisionShape`（或 `CollisionPolygon`）子节点。
3. **配置层和掩码**。一个身体位于其 **层** 上，并扫描其 **掩码**。只有当其中一个身体的层在另一个身体的掩码中时，两者才会交互。在项目设置 > 层名称中命名层，以便更清晰。
4. **使用 `Area` 信号（`body_entered`，`area_entered`）检测重叠**。
5. **使用力/冲量驱动 `RigidBodies`**，或重写 `_integrate_forces` 以实现完全控制。
6. **使用 `RayCast2D/3D` 节点（每帧轮询）或代码中的单次空间状态查询来投射射线**。

## 模式

### 1. 碰撞层与掩码（从代码设置）

```gdscript
# 玩家位于层 1，扫描层 2（墙壁）和层 3（敌人）。
func _ready() -> void:
    set_collision_layer_value(1, true)    # 我位于层 1
    set_collision_mask_value(2, true)     # 我与层 2 的事物发生碰撞
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

### 3. 向 `RigidBody3D` 应用力与冲量

```gdscript
extends RigidBody3D

func push(direction: Vector3) -> void:
    apply_central_impulse(direction * 8.0)     # 瞬时速度变化

func _physics_process(_delta: float) -> void:
    apply_central_force(Vector3.FORWARD * 4.0) # 持续力（每帧）
    # 不要直接设置 `position` 来移动 `RigidBody`；使用力/冲量或设置 linear_velocity。如果必须将其固定，请使用 freeze=true。
```

### 4. 两种投射射线的方法

```gdscript
# A) `RayCast2D` 节点：启用它，然后在物理更新后轮询。
@onready var ray: RayCast2D = $RayCast2D    # 在编辑器中设置目标位置

func _physics_process(_delta: float) -> void:
    if ray.is_colliding():
        var hit := ray.get_collider()
        var point := ray.get_collision_point()

# B) 代码中的单次查询（无需节点）。
func ground_under(global_from: Vector2) -> Dictionary:
    var space := get_world_2d().direct_space_state
    var query := PhysicsRayQueryParameters2D.create(global_from, global_from + Vector2(0, 64))
    query.collision_mask = 1                 # 仅层 1
    return space.intersect_ray(query)        # 如果没有命中，则为 {}，否则为 collider/position/normal
```

## 常见问题

- **层与掩码混淆** 是第一大 Bug。层 = "我是什么"；掩码 = "我在寻找什么"。要使 A 检测到 B，B 的层必须在 A 的掩码中。检测可以是单向的。
- **通过 `position` 移动 `RigidBody`** 会与求解器冲突并导致隧道/抖动。使用冲量/力、设置 `linear_velocity`，或 `freeze` 它。要传送，设置位置并在 `_integrate_forces` 中将速度置零。
- **`Area` 在以下情况下不会触发**：既未设置监控，也未设置可监控，或层/掩码不重叠。`monitoring` 必须开启才能让 Area 检测；`monitorable` 允许其他事物检测它。
- **`RayCast2D/3D` 读取陈旧或无数据** 如果 `enabled` 为 false，或在物理更新前读取 — 在 `_physics_process` 中读取，并在同一帧内移动它后调用 `force_raycast_update()`。
- **忘记添加 `CollisionShape`**（或将其留空）意味着身体永远不会发生碰撞。
- **快速物体穿过薄墙**；在 `RigidBody` 上启用 **连续碰撞检测**（`continuous_cd`）或使用基于射线的检查。
- **`intersect_ray` 排除了自己的身体？** 传递 `query.exclude = [self.get_rid()]`（一个 `Array[RID]`，而不是节点数组）以跳过自击。
- **Jolt Physics (3D) 的差异**

  - **在 Jolt 下，`face_index` 在 `intersect_ray()` / `RayCast3D` 结果中始终为 `-1`**。如果需要它，请打开项目设置 > 物理 > Jolt Physics 3D > 查询 > 启用射线投射面索引（它会使 `ConcavePolygonShape3D` 的内存使用量增加约 25%）。
  - **在切换引擎后，只有一个身体的关节会得到反转的限制**。Jolt 将单个身体视为 `node_b`，将 `node_a` 视为世界；GodotPhysics3D 始终将其视为 `node_a`。将身体分配给 Jolt 期望的插槽，或使用物理 > Jolt Physics 3D > 关节 > 世界节点以兼容旧项目。
  - **Jolt 下，关节软限制属性无效**（例如，Pin、Hinge 和 ConeTwist 关节的 `bias`/`softness`/`relaxation`；Slider 和 Generic6DOF 关节的限制软度/恢复/阻尼）。Godot 在设置非默认值时会发出警告。
  - **冻结的运动学 `RigidBody3D` 不会报告与静态或运动学身体的接触**，即使 `max_contacts_reported > 0`。如果游戏玩法依赖于这些接触，请启用物理 > Jolt Physics 3D > 模拟 > 生成所有运动学接触。
  - **Jolt 下，形状 `margin` 会缩小形状而不是填充它**，因此尺寸保持真实，但小形状的形状查询可能会返回奇怪的法线；有效边距来自物理 > Jolt Physics 3D > 碰撞 > 碰撞边距分数。
  - **Jolt 下，`Area3D` 现在会为 `SoftBody3D` 触发 `body_entered`**（GodotPhysics3D 从未这样做）。如果期望旧行为，请使用层/掩码过滤软体。

## 参考

- 对于 `_integrate_forces`、关节、单向碰撞、`PhysicsServer` 直接访问、形状查询（`intersect_shape`）和 3D `move_and_collide`，请阅读 `references/bodies-and-queries.md`。
- Jolt 的具体内容：Godot 文档 "使用 Jolt Physics"
  (`https://docs.godotengine.org/en/stable/tutorials/physics/using_jolt_physics.html`).

## 相关技能

- `godot-2d-movement` — 运动学 `CharacterBody2D` 控制器。
- `godot-tilemap` — 瓦片碰撞形状及其层。
- `physics-tuning` — 引擎无关的触感：时间步长、质量、阻力、CCD。
- `godot-3d-essentials` — 这些身体存在的 3D 场景设置。
