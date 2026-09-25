# 游戏体感（juice）

一个运作良好的机制与一个感觉良好的机制之间的区别在于反馈：一个动作所引发的多层、略微夸张的响应。这项技能涵盖了与引擎无关的技术——屏幕震动、击打停止、缓动、挤压与拉伸、击退和堆叠反馈——并告诉你如何在不埋没底层模拟的情况下应用它们。它**在现有机制之上添加光泽**；它不会实现该机制。

## 使用时机

- 当一个动作（击打、跳跃、冲刺、拾取、死亡、按键）在机制上正确但感觉薄弱、轻飘飘或不令人满意，并且你想让它感觉有响应力和冲击力时使用。
- 用于添加屏幕震动、击打停止/冻结帧、缓动运动、挤压与拉伸、击退、闪烁，或将多个反馈通道叠加到一个事件上。
- 用于决定*多少* juice 足够以及它何时会变成噪音。

**不使用时机：** 对于原始控制器数学（跳跃高度、猫头鹰时间）使用 `platformer` 类型以及引擎移动技能。对于相机 *跟随/死区/轨道* 帧面使用 `camera-systems`（这项技能仅触发震动）。对于混合、潜行和自适应音乐使用 `audio-design`。对于基于着色的溶解/闪烁使用 `shader-programming` 和引擎着色技能。对于具体的补间/粒子节点 API，使用引擎动画技能（`godot-animation`，`unity-animation`）。

## 核心原则：反馈是分层和夸张的

一次令人满意的击打通常在 ~100 毫秒内**同时触发 5–8 个微小响应**：一个声音、一个粒子爆发、一个短暂的击打停止、一个闪烁、一个击退、一个小屏幕震动，以及一个数字弹出。每个都是廉价的；堆叠起来，它们看起来像“冲击”。两条规则防止它变得混乱：**(1)** 短暂夸张并恢复平静（juice 是暂时的，不是新的静止状态）；**(2)** 根据事件重要性调整 juice——脚步声不是Boss死亡。

## 核心工作流程

1. **确认事件钩子是否存在。** Juice 附加到离散事件：`on_hit`，`on_land`，`on_pickup`，`on_death`，`on_fire`。如果机制不发出这些，请先添加它们。
2. **从菜单中为每个事件选择反馈通道**（声音、粒子、震动、击打停止、闪烁、击退、补间、数字弹出）。从 2–3 个开始；添加直到它看起来合适，然后停止。
3. **使运动缓动而不是线性。** 将缩放/位置/UI 变化通过一个带有缓动的补间路由（“pop”使用过冲，“settle”使用缓出）。线性运动感觉像机器人。
4. **将击打停止和震动保留用于冲击。** 它们是最强、最容易被滥用的工具——短持续时间、按重要性缩放，并且永远不会在常规动作上使用。
5. **保持反馈与关键模拟分离。** 震动移动 *相机/视觉*，而不是身体；击打停止使用时间缩放或实时暂停，而不是游戏逻辑停滞。
6. **按重要性等级进行微调。** 定义小/中/大反馈预设，并将事件分配给一个等级，以便整个游戏 juice 保持一致和成比例。
7. **通过播放和观察进行验证。** 重复触发事件；确认反馈被触发、恢复平静，并且不会引起恶心或阻塞输入。报告你的观察结果（震动是否衰减？击打停止期间输入是否仍然注册？）。

## 模式

### 1. 通过衰减“创伤”进行屏幕震动（平滑，而不是随机抖动）

```gdscript
# Godot 4.7. 存储创伤 0..1；震动 = 创伤^2，所以小击打几乎不动，大击打有冲击力。
# 驱动 Camera2D OFFSET（视觉），而不是玩家身体。每帧衰减。
@export var decay := 1.2          # 每秒丢失的创伤
@export var max_offset := Vector2(12, 8)
@export var max_roll := 0.1       # 弧度
var trauma := 0.0
var _t := 0.0

func add_trauma(amount: float) -> void:
    trauma = clampf(trauma + amount, 0.0, 1.0)   # 击打添加；它们不会重置

func _process(dt: float) -> void:
    if trauma <= 0.0: return
    trauma = maxf(trauma - decay * dt, 0.0)
    var shake := trauma * trauma                  # 二次方：低处轻柔，高处尖锐
    _t += dt * 30.0
    # 通过采样噪声/正弦进行平滑伪随机，而不是每帧随机（那会嗡嗡作响）。
    offset = Vector2(max_offset.x * shake * sin(_t * 1.7),
                     max_offset.y * shake * sin(_t * 2.3))
    rotation = max_roll * shake * sin(_t * 1.1)
# Unity 6.3 LTS：在 CinemachineCamera 上使用 CinemachineBasicMultiChannelPerlin 进行相同的模型
# （从创伤^2设置 AmplitudeGain/FrequencyGain）——参见 camera-systems。
```

### 2. 击打停止 / 冻结帧（通过短暂停止时间来提升冲击力）

```gdscript
# Godot 4.7. 降低时间缩放，然后在实时延迟后恢复（不受时间缩放影响）。
func hit_stop(duration := 0.08, scale := 0.05) -> void:
    Engine.time_scale = scale
    # 第4个参数 ignore_time_scale=true → 游戏冻结时计时器仍然触发。
    await get_tree().create_timer(duration, true, false, true).timeout
    Engine.time_scale = 1.0
```

```csharp
// Unity 6.3 LTS (C#)。 WaitForSecondsRealtime 忽略 Time.timeScale，所以计时器仍然流逝。
IEnumerator HitStop(float duration = 0.08f, float scale = 0.05f) {
    Time.timeScale = scale;
    yield return new WaitForSecondsRealtime(duration);
    Time.timeScale = 1f;            // 正确：实时等待。错误：WaitForSeconds（永远不会在缩放 0 时恢复）
}
```

### 3. 挤压与拉伸 + 通过缓动补间进行过冲（“pop”）

```gdscript
# Godot 4.7. 保持体积：拉伸一个轴，挤压另一个轴，然后带有过冲弹回。
func pop(node: Node2D) -> void:
    node.scale = Vector2(1.3, 0.7)                       # 事件上立即挤压
    var tw := create_tween()
    tw.tween_property(node, "scale", Vector2.ONE, 0.18) \
      .set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)   # BACK = 过冲超过 1，然后稳定
# 正确：缓动回退（TRANS_BACK/ELASTIC）用于生命周期。错误：线性补间 → 机械的，死板的。
```

### 4. 按重要性缩放的反馈包（保持 juice 成比例）

```gdscript
# 每个事件一个调用；等级决定强度，以便整个游戏保持一致。
func feedback(event_pos: Vector2, tier: String) -> void:
    match tier:
        "small":  AudioBus.play("tick");  Camera.add_trauma(0.15)
        "medium": AudioBus.play("hit");   Camera.add_trauma(0.4);  hit_stop(0.05); spawn_particles(event_pos, 6)
        "large":  AudioBus.play("boom");  Camera.add_trauma(0.8);  hit_stop(0.12); spawn_particles(event_pos, 30); flash_white(0.06)
```

## 陷阱

- **震动玩家/身体而不是相机偏移**会导致碰撞和瞄准不同步。震动相机（或一个视觉枢轴），永远不要震动模拟的变换。
- **每帧随机偏移**会像静电一样嗡嗡作响。通过采样噪声/正弦和衰减的创伤值驱动震动，使其平滑且自结束。
- **使用 `WaitForSeconds` / 缩放计时器进行击打停止**永远不会恢复（时间缩放为 0 时计时器不会前进）。使用实时等待（`WaitForSecondsRealtime`，或 Godot 的 `ignore_time_scale` 计时器）。
- **在持续攻击的每一帧上使用击打停止**会锁定游戏。每次冲击只触发一次。
- **到处使用线性补间**感觉像机器人。几乎一切都使用缓动；保留过冲（BACK/ELASTIC）用于“pop”，使用缓出用于“settle”。
- **永久夸张**（缩放永远不会恢复，震动永远不会衰减）成为新的正常状态，并停止被视为反馈。Juice 必须恢复平静。
- **过度 juice 常规动作**（每一步都有完整的震动 + 击打停止）会导致恶心并掩盖真正的冲击。按重要性缩放；添加“减少屏幕震动”/“减少闪烁”的无障碍选项。
- **阻塞输入的反馈**（长时间冻结、不可取消的动画）会损害响应性。保持 juice 短暂，并让输入在其通过。

## 参考

- 对于创伤震动数学、缓动曲线速查表（哪种缓动用于 pop 对比 settle）、击退 + 闪烁 + 数字弹出配方、重要性等级预设，以及每个引擎的补间/粒子绑定，请阅读 `references/feedback-recipes.md`。

## 相关技能

- `camera-systems` — 拥有相机跟随/死区/轨道；这项技能仅向其提供震动创伤。
- `godot-animation`, `unity-animation` — 具体的补间/AnimationPlayer/粒子 API juice 靠其运行。
- `audio-design` — 每个反馈包的声音层；潜行和 SFX 变化。
- `physics-tuning` — 击退力和 juice 必须不会使其不稳定的时间步长。
- `platformer`, `fps-shooter`, `roguelike` — 这类游戏的即时体感会因此提升。
