# 物理调优

大多数"糟糕的物理效果"并非引擎本身的错误——而是**固定步长模拟**与**可变速率渲染循环**之间的不匹配，或者是未调优的质量/阻力/CCD/层设置。本技巧涵盖了让物理效果稳定且响应迅速的中立性调节参数；配合`godot-physics`或`unity-physics`使用具体API。

## 使用场景

- 当出现运动抖动、物体穿墙（隧道效应）、堆叠爆炸，或移动感觉漂浮/粘滞/卡顿时使用。
- 用于决定哪些内容放在固定（物理）步长中，哪些放在渲染帧中，以及如何在这两者之间插值。
- 用于调优重力、质量、阻力、恢复力、求解器迭代次数、休眠状态和碰撞层/掩码。

**不使用场景：** 对于引擎的精确物理节点/组件和碰撞回调，使用`godot-physics`或`unity-physics`。对于*移动决策*（何时跳跃、AI转向）使用`input-systems`和`game-ai`。对于平台跳跃感具体细节（如科伊特时间/跳跃缓冲），那是输入/控制器领域——参考`input-systems`和`platformer`类型。

## 核心工作流程

1. **在固定步长上运行物理模拟。** 以恒定速率（例如50-60 Hz）进行模拟。固定的`dt`使模拟近乎确定性和稳定性；可变的`dt`导致积分和碰撞不一致。
2. **将物理工作放在物理回调中，而不是渲染帧中。** 在固定步长（`FixedUpdate` / `_physics_process`）中应用力/速度并读取碰撞，使用该步长的`dt`。
3. **在物理步长之间插值渲染。** 渲染帧速率≠物理速率，因此需要平滑地将变换插值到最新的物理状态，或启用引擎的Rigidbody插值，以消除可见的卡顿。
4. **调整物体，而非场景。** 设置质量以调整相对重量，设置阻力以调整阻尼，设置每个物体的重力缩放，并通过材质设置恢复力/摩擦力。
5. **对小型/快速物体使用CCD**以停止隧道效应；限制最大速度。
6. **使用更多求解器迭代次数、合理的质量比和休眠状态**来稳定堆叠/关节。
7. **通过感觉和压力测试进行验证。** 在低和高帧率下运行；将快速物体扔向薄墙；堆叠和推挤物体。报告你的观察结果。

## 模式

### 1. 固定步长模拟，渲染插值实现平滑

```gdscript
# 物理回调：以固定速率运行。使用其dt进行所有积分。
func _physics_process(dt):                  # Unity: void FixedUpdate()
    velocity += gravity * dt                # 使用固定dt进行积分
    move_and_slide()                        # 引擎在此步长中解决碰撞
    _prev_pos = _curr_pos; _curr_pos = global_position   # 记录用于插值的位置

# 渲染帧：尽可能快地运行。在物理状态之间插值。
func _process(_frame_dt):                   # Unity: void Update()
    var alpha = Engine.get_physics_interpolation_fraction()  # 在步长内为0..1
    visual.global_position = _prev_pos.lerp(_curr_pos, alpha)
# 正确：在固定步长中积分，通过插值渲染。
# 错误：在_frame_dt/Update中应用力——速度和碰撞将依赖于帧率和负载下的抖动。
```

大多数引擎都为你提供此功能（Godot `physics_interpolation`/Rigidbody interpolate；Unity `Rigidbody.interpolation = Interpolate`）。优先使用内置功能，而不是手动编写。

### 2. 停止隧道效应：CCD + 速度限制

```gdscript
# 快速、小型物体在步长之间跳过薄碰撞器。两种修复方法：
body.continuous_cd = true            # RigidBody3D布尔值（RigidBody2D：CCD_MODE_*枚举）。Unity：rb.collisionDetectionMode = Continuous
# 限制速度，以便单个步长不能移动超过~一个碰撞器厚度。
const MAX_SPEED := 40.0
if velocity.length() > MAX_SPEED:
    velocity = velocity.normalized() * MAX_SPEED
# 经验法则：max_distance_per_step (= speed / physics_hz) 应该小于最薄的墙。当失败时提高physics_hz或启用CCD。
```

### 3. 物体调优：质量、阻力、重力缩放、材质

```gdscript
# 质量是相对重量，在碰撞中；它不会改变下落速度（所有质量都同等受到重力加速）。使用阻力和gravity_scale来塑造感觉。
body.mass = 2.0                      # 更重的物体在碰撞中会推轻物体
body.linear_damp = 0.5               # 空气阻力：更高=停止更快（Unity：drag）
body.gravity_scale = 1.5             # 每个物体的重力乘数（更快的下落）
# 弹跳/滑动来自物理材质，而非代码：
material.bounce = 0.2                # 恢复力0..1（Unity：bounciness）
material.friction = 0.8              # 表面抓地力
```

### 4. 碰撞层和掩码（谁与谁碰撞）

```gdscript
# 物体位于其层上，并扫描其掩码中的层。两者必须配置双向才能交互。
player.collision_layer = LAYER_PLAYER
player.collision_mask  = LAYER_WORLD | LAYER_ENEMY     # 玩家检测世界+敌人
pickup.collision_layer = LAYER_PICKUP
pickup.collision_mask  = LAYER_PLAYER                  # 拾取物只对玩家反应
# Unity等效：分配GameObject层并编辑物理碰撞矩阵（或Physics.IgnoreLayerCollision）。保留命名层常量表，而非魔法数字。
```

## 陷阱

- **在渲染帧中应用力/移动**（`Update`/`_process`）使行为依赖于帧率——更快的PC运行更快，碰撞变得不稳定。在固定步长中执行模拟。
- **即使有固定步长，仍有可见抖动**通常意味着没有渲染插值：物理速率和显示速率相互冲突。启用插值。
- **穿过薄墙的隧道效应**：离散碰撞会错过快速移动的物体。启用CCD，限制速度，加厚墙，或提高物理速率。
- **期望较重的物体下落更快。** 重力是加速度；质量影响碰撞响应，不影响下落速度。使用`gravity_scale`/阻力来调整感觉。
- **爆炸的堆叠/抖动的关节**：质量比极端，或求解器迭代次数太少。保持合理的质量比并提高迭代次数。
- **永远不休息的物体**会消耗CPU并抖动。为静止物体启用休眠和合理的休眠阈值。
- **单向层设置**：A的掩码包含B，但B的掩码排除A。检测/碰撞可能需要双向；验证完整矩阵。
- **巨大的`dt`峰值**（加载延迟、断点）会破坏积分。限制最大物理步长/子步数，以防止停滞导致所有东西启动。

## 参考

- `references/timestep-and-ccd.md` — 固定步长累加器循环、插值数学、子步、CCD模式、求解器/迭代调优、休眠和稳定性检查清单。

## 相关技能

- `godot-physics`, `unity-physics` — 具体的物体、碰撞器和回调。
- `input-systems` — 响应式控制、跳跃缓冲、科伊特时间。
- `game-ai` — 必须与物理步长一致的智能体移动。
- `platformer`, `fps-shooter` — 感觉依赖于此调优的类型。
