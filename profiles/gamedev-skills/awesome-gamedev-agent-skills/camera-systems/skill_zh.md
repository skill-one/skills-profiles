# 摄像系统

摄像机是玩家的窗口；糟糕的摄像机操作会让好游戏感觉糟糕。这项技能涵盖了与引擎无关的摄像机技术——平滑跟随、死区、预判、边界限制、带碰撞的第三人称环绕、第一人称视角和多目标构图——并将它们映射到每个引擎的摄像机节点或 rig 上。

## 使用场景

- 当 2D 摄像机需要平滑跟随玩家、保持在关卡内、引导玩家动作或忽略微小移动（死区）时使用。
- 当构建 3D 第三人称环绕摄像机（鼠标/摇杆视角、碰撞推入）或第一人称视角控制器，或同时构图多个目标时使用。
- 用于修复摄像机抖动、瞬移、运动病或显示关卡边缘之外的摄像机。

**不使用场景：** 对于屏幕抖动的 *幅度和触发*，使用 `game-feel`（这项技能暴露了它驱动的抖动偏移钩子）。对于引擎的具体摄像机节点/组件设置，使用 `godot-3d-essentials`（Camera3D、环境）或引擎技能。对于玩家移动本身，使用引擎移动技能（`godot-2d-movement`）。对于多个摄像机/渲染目标的性能，请参考 `performance-optimization`。

## 核心工作流程

1. **确定摄像机的作用。** 平台游戏（引导跳跃、识别障碍）、俯视游戏（带死区居中）、第三人称（环绕+碰撞）、第一人称（仅视角）。类型决定了规则。
2. **平滑跟随且与帧率无关。** 用指数平滑或弹簧（`SmoothDamp`）将摄像机移向目标，而不是固定的 `lerp(a, b, 0.1)`——那 0.1 是每帧的，会随帧率变化。
3. **添加死区** 以防止微小目标移动时推动摄像机；只有当目标离开一个框/区域时才跟随。防止快节奏游戏中的恶心。
4. **用预判引导动作** 通过在运动或朝向方向上偏移摄像机目标，缓入缓出以防止猛地甩动。
5. **限制在关卡边界内** 以确保摄像机不会显示在可玩区域之外；结合平滑效果，使其在边缘处平滑停止。
6. **对于 3D，将视角与碰撞分离。** 通过 rig 上的偏航/俯仰进行环绕；当几何体阻挡时，用弹簧臂/射线将摄像机拉入；限制俯仰。
7. **在目标移动后更新摄像机。** 在晚步/后步（移动和物理解决后）跟随，以避免一帧的滞后抖动。
8. **通过在低帧率和高帧率下移动目标**，进入角落和墙壁，并在关卡边缘进行验证；确认没有抖动、没有越过边界、平滑停止。报告你看到的情况。

## 模式

### 1. Godot 2D 内置跟随：平滑+边界（不要手动编写第一人称）

```gdscript
# Godot 4.7 Camera2D。引擎提供的平滑+硬限制+拖动边距。
@onready var cam := $Camera2D
func _ready() -> void:
    cam.make_current()
    cam.position_smoothing_enabled = true
    cam.position_smoothing_speed = 6.0           # 更高 = 更突然；更低 = 更漂浮
    cam.limit_left = 0; cam.limit_top = 0        # 限制在关卡矩形（像素）内
    cam.limit_right = level_width; cam.limit_bottom = level_height
    cam.drag_horizontal_enabled = true           # 通过拖动边距实现内置死区
```

### 2. 帧率无关的平滑跟随（当你手动编写时）

```gdscript
# 正确：指数平滑——在任何 FPS 下都有相同的感觉。`rate` ~ 5..12。
func _follow(dt: float) -> void:
    var t := 1.0 - exp(-rate * dt)               # 无论 dt 如何都正确收敛
    global_position = global_position.lerp(target.global_position, t)
# 错误：global_position = global_position.lerp(target.global_position, 0.1)
#        → 在高 FPS 下平滑更快；在不同机器上有不同的感觉。
# Unity 6.3 LTS：在 LateUpdate 中使用 Vector3.SmoothDamp(transform.position, target.position, ref vel, smoothTime) 给出与内置帧率校正相同的弹簧行为。
```

### 3. 死区+预判（引导玩家，忽略抖动）

```gdscript
# 摄像机只在目标离开死区框后才追逐，然后朝向运动前方。
func _camera_target(dt: float) -> Vector2:
    var to := target.global_position - _focus
    var dz := deadzone_half_extents                  # 例如 Vector2(48, 32)
    # 仅通过超出死区的溢出（每个轴）移动焦点。
    _focus.x += clampf(absf(to.x) - dz.x, 0, INF) * signf(to.x)
    _focus.y += clampf(absf(to.y) - dz.y, 0, INF) * signf(to.y)
    var lead := target.velocity.normalized() * look_ahead_dist    # 朝向运动前方
    return _focus + lead
```

### 4. 3D 第三人称环绕带碰撞推入

```gdscript
# Godot 4.7。偏航/俯仰一个枢轴；当被阻挡时 SpringArm3D 自动将摄像机拉入。
func _unhandled_input(e):
    if e is InputEventMouseMotion:
        _yaw -= e.relative.x * sensitivity
        _pitch = clampf(_pitch - e.relative.y * sensitivity, -1.2, 0.4)   # 限制俯仰！
func _process(_dt):
    pivot.rotation = Vector3(_pitch, _yaw, 0)
    # $SpringArm3D 处理墙壁碰撞：设置 spring_length + collision_mask；子级 Camera3D 自动滑入。
    # 正确：弹簧臂。错误：摄像机穿过墙壁。
# Unity 6.3 LTS：一个 Cinemachine 3 CinemachineCamera（命名空间 Unity.Cinemachine）带有 Orbital Follow + Cinemachine Deoccluder；Camera 上的 CinemachineBrain 自动混合。
```

### 5. 屏幕抖动钩子（触发存在于 `game-feel` 中）

```gdscript
# 暴露一个游戏感觉创伤模型写入的加性偏移；跟随+抖动组合。
var shake_offset := Vector2.ZERO                 # 每帧由游戏感觉（创伤^2 * 噪声）设置
func _apply(final_focus: Vector2) -> void:
    global_position = final_focus + shake_offset  # 抖动叠加在平滑跟随之上
# Unity Cinemachine：添加一个 CinemachineBasicMultiChannelPerlin 并从创伤设置振幅。
```

## 陷阱

- **每帧 `lerp(pos, target, const)`** 与帧率相关——30 FPS 时更漂浮，144 FPS 时更突然。使用 `1 - exp(-rate*dt)` 或 `SmoothDamp`。
- **在目标移动前正常更新时跟随** 会导致一帧的滞后抖动。在 `LateUpdate` / 移动/物理解决后跟随。
- **没有边界限制** 让摄像机显示在关卡边缘之外的黑屏。将焦点限制在关卡矩形内（考虑视口半尺寸，使 *视图* 而不是中心停留在内部）。
- **在快节奏游戏中没有死区** 让摄像机随着每个微小移动抖动 → 恶心。
- **未限制的俯仰** 在第三/第一人称中翻转摄像机。限制俯仰至约 ±80°。
- **3D 摄像机穿过墙壁** — 使用弹簧臂/遮挡射线拉入。
- **传送/重生时的瞬移** 令人不快；要么有意硬切（并重置平滑），要么快速缓动。不要让巨大的 `SmoothDamp` 距离横扫关卡。
- **抖动驱动跟随目标** 而不是加性偏移会使跟随与抖动冲突。组合：先平滑跟随，最后加抖动偏移。
- **轴向与径向死区混淆** — 矩形死区与圆形死感不同；故意选择。

## 参考

- 对于指数平滑/弹簧推导、完整的死区+预判+边界 2D rig、3D 弹簧臂/环绕细节、第一人称视角、多目标/分组构图和分屏、电影摄像机混合以及 Cinemachine 3 / Godot Camera2D / PhantomCamera 映射，请阅读 `references/follow-and-framing.md`。

## 相关技能

- `game-feel` — 拥有屏幕抖动创伤/触发；这项技能暴露了它写入的偏移。
- `godot-2d-movement`, `godot-3d-essentials` — 摄像机构图的玩家/世界；Camera3D 设置。
- `physics-tuning` — 将摄像机跟随与物理步长插值以消除抖动。
- `platformer`, `fps-shooter` — 这项技能实现其摄像机规则的类型。
- `performance-optimization` — 额外摄像机、渲染目标和分屏的成本。
