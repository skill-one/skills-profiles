# 输入系统

永远不要将游戏逻辑直接绑定到原始按键上。将物理输入（一个按键、一个按钮、一个触摸操作）映射到命名的**动作**（`跳跃`、`交互`、`移动`），然后让游戏逻辑读取这些动作。这个间接层几乎免费地为你提供了按键重映射、多设备支持和无障碍功能。这项技能是引擎无关的架构；将其绑定到 `unity-input-system`、`unreal-enhanced-input` 或 Godot 的 `InputMap`。

## 使用场景

- 用于设计输入层：动作、绑定、多设备支持，以及带有冲突检测和保存绑定的重映射 UI。
- 用于添加模拟处理（死区、灵敏度）和游戏体感功能（输入缓冲、科伊特时间）。
- 用于使控制更易于访问（完全重映射、按住与切换、灵敏度、无需同时按下的按键组合）。

**不使用场景**：对于引擎的具体输入包/API，使用 `unity-input-system`、`unreal-enhanced-input` 或 Godot 的 InputMap。对于缓冲器输入的移动/跳跃物理效果，请参考 `physics-tuning` 和引擎移动技能。持久化按键绑定到磁盘是 `save-systems` 的功能。

## 核心工作流程

1. **定义动作，而非按键。** 游戏逻辑询问“`跳跃`是否被按下？”，而不是“空格键是否被按下？”。动作是稳定的契约；绑定是数据。
2. **按设备绑定。** 每个动作都包含键盘、手柄和触摸的绑定。当前设备是最后一个发送输入的设备；切换 UI 提示以匹配。
3. **读取正确的边缘。** 使用 *本帧按下*（边缘）来处理离散动作（跳跃、交互），使用 *按住*（级别）来处理连续动作（移动、瞄准）。混淆两者会导致重复触发或遗漏按键。
4. **过滤模拟输入。** 对摇杆/扳机应用死区，使静止时的漂移读为零，并根据喜好调整灵敏度和曲线。
5. **缓冲以增强体感。** 在短时间内记住按下的动作，以便稍微提前的按键仍然能触发（输入缓冲）；允许在离开平台后不久跳跃（科伊特时间）。
6. **使重映射成为首要功能。** 一个捕获下一个输入、检测冲突并持久化绑定的 UI —— 以及恢复默认设置的选项。通过 `save-systems` 保存。
7. **在所有设备** 和重映射情况下验证：键盘、手柄、触摸；在游戏中重映射一个动作，并确认游戏逻辑和提示跟随。

## 模式

### 1. 动作而非原始按键；边缘与按住

```gdscript
# 游戏逻辑读取动作。按键/按钮到动作的映射存在于数据中。
# 离散（边缘）：在按下帧触发一次。
if Input.is_action_just_pressed("jump"):
    try_jump()
# 连续（按住）：每帧读取为轴。
var move := Input.get_axis("move_left", "move_right")   # -1..1
player.velocity.x = move * RUN_SPEED
# RIGHT: 命名动作（"跳跃"）；重映射/设备仅改变绑定数据。
# WRONG: `if Input.is_key_pressed(KEY_SPACE)` — 无法重映射、仅限键盘，
# 并且 `is_key_pressed` 是按住检查，会导致每帧重新触发跳跃。
```

引擎等效方案：Godot `InputMap` + `Input.is_action_just_pressed`；Unity Input System `InputAction` / 动作映射；Unreal Enhanced Input `Input Actions` + `Input Mapping Contexts`。

### 2. 模拟死区和灵敏度

```gdscript
# 原始摇杆永远不会精确地静止为零。应用径向死区（基于向量长度），而不是按轴，
# 这样对角线输入不会被裁剪到轴上。
func apply_deadzone(stick: Vector2, dead := 0.2, sens := 1.0) -> Vector2:
    var mag := stick.length()
    if mag < dead:
        return Vector2.ZERO                      # 在死区内 -> 无移动
    # 重缩放，使运动在死区边缘从 0 开始渐变，而不是从 `dead` 开始。
    var scaled := (mag - dead) / (1.0 - dead)
    return stick.normalized() * pow(scaled, sens)  # sens>1 = 中心附近更精细
# WRONG: 分别对每个轴进行限制 —— 它会切割一个方形孔，并直接映射到轴。
```

### 3. 输入缓冲 + 科伊特时间（宽容、响应体感）

```gdscript
# 缓冲：跳跃稍微提前按下，在着陆时仍然能触发。
# 科伊特：稍微在离开平台后按下跳跃，仍然有效。
const BUFFER := 0.12   # 提前按下的按键保持“记忆”的秒数
const COYOTE := 0.10   # 离开地面后仍可跳跃的秒数
var _buffer_timer := 0.0
var _coyote_timer := 0.0

func _physics_process(dt):
    _buffer_timer -= dt
    _coyote_timer = COYOTE if is_on_floor() else _coyote_timer - dt
    if Input.is_action_just_pressed("jump"):
        _buffer_timer = BUFFER                  # 记住按键
    if _buffer_timer > 0.0 and _coyote_timer > 0.0:
        velocity.y = JUMP_VELOCITY
        _buffer_timer = 0.0; _coyote_timer = 0.0  # 消耗两者，确保只触发一次
```

### 4. 带冲突检测的重映射

```gdscript
# 捕获下一个物理输入，拒绝重复，然后持久化。
func rebind(action: String, event: InputEvent) -> bool:
    for other in actions:                        # 跨动作的冲突检查
        if other != action and binding_of(other) == event:
            return false                         # 已使用 -> 让 UI 警告/切换
    set_binding(action, event)                   # 引擎：删除旧绑定 + 添加新事件
    save_bindings()                              # 持久化（见 save-systems）
    return true
# 始终提供“恢复默认设置”，并且永远不要让玩家解除绑定他们需要通过替代方案才能访问菜单的按键。
```

## 陷阱

- **在游戏逻辑中硬编码按键**：会禁用重映射、锁定手柄/触摸，并分散输入逻辑。仅读取命名动作。
- **边缘与按住混淆**：使用按住检查会导致跳跃每帧重新触发；使用边缘检查会导致移动丢失按住输入。将检查与动作匹配。
- **按轴死区**：会裁剪对角线摇杆输入，并将移动直接映射到轴。在向量长度上使用径向死区。
- **无缓冲/科伊特时间**：即使物理正确，也会使紧平台游戏感觉不公平 —— 玩家“显然按下了跳跃”。添加小窗口。
- **无冲突处理的重映射**：会导致两个动作共享一个按键，或因解除绑定菜单访问而困住玩家。检测冲突；保证有返回路径。
- **设备变更时不切换提示**：对手柄玩家显示“按空格键”。跟踪最后使用的设备并切换符号。
- **忽略无障碍性**：需要同时按下、无重映射、固定灵敏度、仅按住的动作。提供重映射、切换/按住选项和灵敏度调节。
- **在错误的循环中读取输入**：在物理步骤中轮询按住状态以实现一致移动；捕获离散按键以避免帧间遗漏。

## 参考

- `references/buffering-and-accessibility.md` — 缓冲/科伊特调优、跳跃体感（可变高度、顶点）、设备检测和提示切换、触摸控制，以及无障碍性检查清单（重映射、切换/按住、灵敏度、延迟）。

## 相关技能

- `unity-input-system`, `unreal-enhanced-input` — 具体的引擎输入 API（Godot 使用 `InputMap` + `Input` 单例）。
- `save-systems` — 持久化自定义按键绑定和输入设置。
- `physics-tuning` — 缓冲/科伊特窗口输入的移动。
- `platformer`, `fps-shooter` — 依赖输入处理的类型。
