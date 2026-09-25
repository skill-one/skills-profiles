# Godot 4.x GDScript 最佳实践

指导 AI 代理为 Godot 4.x 编写高质量的 GDScript 代码。这项技能提供编码标准、架构模式和游戏开发模板。

## 使用此技能的场景

在以下情况下使用此技能：
- 生成新的 GDScript 代码
- 创建或组织 Godot 场景
- 设计游戏架构和节点层级
- 实现状态机、对象池或存档系统
- 回答有关 GDScript 模式或 Godot 习惯用法的问题
- 审查存在质量问题的 GDScript 代码

**不**使用此技能的场景：
- 在 Godot 中使用 C#（使用 C# 模式）
- 使用 Godot 3.x（语法差异显著）
- 使用 GDExtension/C++（不同的范式）
- 使用 Godot 的可视化脚本

## 核心原则

### 1. 命名规范

始终一致地遵循 GDScript 命名标准：

```gdscript
# 类：PascalCase
class_name PlayerController
extends CharacterBody2D

# 信号：过去式蛇形命名（描述发生了什么）
signal health_changed(new_health: int)
signal player_died
signal item_collected(item: Item)

# 常量：SCREAMING_SNAKE_CASE
const MAX_SPEED: float = 200.0
const JUMP_FORCE: int = -400

# 变量和函数：蛇形命名
var current_health: int = 100
var _private_variable: float = 0.0  # 以下划线开头表示私有
func calculate_damage(base: int, multiplier: float) -> int:
    return int(base * multiplier)
func _private_helper() -> void:  # 以下划线开头表示私有
    pass
```

### 2. 类型提示（静态类型）

在所有地方使用显式类型提示以实现自动补全和错误检测：

```gdscript
# 变量声明
var speed: float = 100.0
var player: CharacterBody2D
var items: Array[Item] = []
var stats: Dictionary = {}

# 带返回类型的函数签名
func get_damage() -> int:
    return _base_damage * _multiplier

func find_nearest_enemy(position: Vector2) -> Enemy:
    # 实现
    return null

# 带类型提示的信号（Godot 4.x）
signal score_updated(new_score: int, old_score: int)
signal target_acquired(target: Node2D, distance: float)

# 带类型的节点引用
@onready var sprite: Sprite2D = $Sprite2D
@onready var collision: CollisionShape2D = $CollisionShape2D
@onready var animation_player: AnimationPlayer = %AnimationPlayer
```

### 3. 节点引用

使用现代模式以实现稳定、易于重构的引用：

```gdscript
# 优先：带类型提示的 @onready
@onready var health_bar: ProgressBar = $UI/HealthBar
@onready var weapon: Weapon = $WeaponMount/Weapon

# 优先：带唯一名称的 %（用于关键节点）
@onready var player: Player = %Player
@onready var game_manager: GameManager = %GameManager

# 避免：_ready() 中的 get_node()
func _ready() -> void:
    # 不要这样做
    var sprite = get_node("Sprite2D")

# 避免：深层脆弱路径
@onready var thing = $Parent/Child/GrandChild/GreatGrandChild  # 脆弱
```

### 4. 信号驱动架构

使用信号进行解耦通信。遵循“信号向上，调用向下”原则：

```gdscript
# 子节点发出信号（不知道父节点）
class_name HealthComponent
extends Node

signal health_changed(current: int, maximum: int)
signal died

var _health: int = 100
var _max_health: int = 100

func take_damage(amount: int) -> void:
    _health = max(0, _health - amount)
    health_changed.emit(_health, _max_health)
    if _health <= 0:
        died.emit()
```

```gdscript
# 父节点连接到子节点信号（知道子节点）
class_name Player
extends CharacterBody2D

@onready var health: HealthComponent = $HealthComponent
@onready var sprite: Sprite2D = $Sprite2D

func _ready() -> void:
    health.health_changed.connect(_on_health_changed)
    health.died.connect(_on_died)

func _on_health_changed(current: int, maximum: int) -> void:
    # 更新 UI、播放效果等
    pass

func _on_died() -> void:
    sprite.modulate = Color.RED
    queue_free()
```

### 5. 资源加载

选择正确的加载策略：

```gdscript
# preload()：编译时加载关键/小资源
const BULLET_SCENE: PackedScene = preload("res://scenes/bullet.tscn")
const PLAYER_SPRITE: Texture2D = preload("res://sprites/player.png")
const DAMAGE_SOUND: AudioStream = preload("res://audio/damage.wav")

# load()：运行时加载可选/大资源
func load_level(level_name: String) -> void:
    var path := "res://levels/%s.tscn" % level_name
    var level_scene: PackedScene = load(path)
    var level := level_scene.instantiate()
    add_child(level)

# ResourceLoader 用于异步加载（防止卡顿）
func _load_level_async(path: String) -> void:
    ResourceLoader.load_threaded_request(path)
    # 检查：ResourceLoader.load_threaded_get_status(path)
    # 获取：ResourceLoader.load_threaded_get(path)
```

## 快速参考

| 类别 | 优先 | 避免 |
|------|------|------|
| 节点引用 | `@onready var x: Type = $Path` | `_ready()` 中的 `get_node()` |
| 唯一节点 | `%UniqueName` | 深层路径 `$A/B/C/D` |
| 资源加载 | `preload()` 用于小/关键资源 | `load()` 处处使用 |
| 信号 | 带类型提示：`signal x(val: int)` | 字符串：`emit_signal("x")` |
| 类型安全 | 显式类型提示 | 未类型化的变量 |
| 常量 | `const` 或 `@export` | 魔术数字/字符串 |
| 空值检查 | `is_instance_valid(node)` | `node != null` 用于已释放节点 |
| 协程 | `await` | `yield`（已弃用） |
| 组 | 场景特定组 | 全局组用于所有内容 |
| Autoloads | 仅限服务和管理器 | 游戏逻辑在 autoloads 中 |
| 属性 | Setters/getters | 直接修改 |
| 通信 | 信号向上，调用向下 | 子节点调用父节点方法 |

## 代码生成指南

### 脚本结构

一致地排序部分：

```gdscript
class_name MyClass
extends Node2D
## 对此类的简要描述。
##
## 如有需要，提供更长的描述，解释目的和用法。

# === 信号 ===
signal state_changed(new_state: State)

# === 枚举 ===
enum State { IDLE, RUNNING, JUMPING }

# === 导出 ===
@export var speed: float = 100.0
@export_group("Combat")
@export var damage: int = 10
@export var attack_range: float = 50.0

# === 常量 ===
const MAX_HEALTH: int = 100

# === 公共变量 ===
var current_state: State = State.IDLE

# === 私有变量 ===
var _internal_counter: int = 0

# === Onready ===
@onready var sprite: Sprite2D = $Sprite2D
@onready var collision: CollisionShape2D = $CollisionShape2D

# === 生命周期方法 ===
func _ready() -> void:
    pass

func _process(delta: float) -> void:
    pass

func _physics_process(delta: float) -> void:
    pass

# === 公共方法 ===
func take_damage(amount: int) -> void:
    pass

# === 私有方法 ===
func _calculate_knockback() -> Vector2:
    return Vector2.ZERO
```

### 导出注释

使用导出为编辑器可配置值：

```gdscript
# 基本导出
@export var health: int = 100
@export var speed: float = 200.0
@export var player_name: String = "Player"

# 范围约束
@export_range(0, 100) var percentage: int = 50
@export_range(0.0, 1.0, 0.1) var volume: float = 0.8

# 资源导出
@export var texture: Texture2D
@export var scene: PackedScene
@export var audio: AudioStream

# 分组导出
@export_group("Movement")
@export var walk_speed: float = 100.0
@export var run_speed: float = 200.0

@export_group("Combat")
@export var attack_damage: int = 10

# 枚举导出
@export var difficulty: Difficulty = Difficulty.NORMAL
enum Difficulty { EASY, NORMAL, HARD }

# 标志（多选）
@export_flags("Fire", "Water", "Earth", "Air") var elements: int = 0
```

## 常见游戏模式

### 状态机（概述）

使用基于枚举的状态机处理简单情况：

```gdscript
enum State { IDLE, WALK, JUMP, ATTACK }

var current_state: State = State.IDLE

func _physics_process(delta: float) -> void:
    match current_state:
        State.IDLE:
            _process_idle(delta)
        State.WALK:
            _process_walk(delta)
        State.JUMP:
            _process_jump(delta)
        State.ATTACK:
            _process_attack(delta)

func change_state(new_state: State) -> void:
    if current_state == new_state:
        return
    _exit_state(current_state)
    current_state = new_state
    _enter_state(new_state)
```

有关高级实现的详细信息，请参阅 `references/patterns/state-machine.md`。

### 对象池（概述）

重用对象以避免实例化成本：

```gdscript
class_name ObjectPool
extends Node

var _pool: Array[Node] = []
var _scene: PackedScene

func _init(scene: PackedScene, initial_size: int = 10) -> void:
    _scene = scene
    for i in initial_size:
        var obj := _scene.instantiate()
        obj.set_process(false)
        _pool.append(obj)

func acquire() -> Node:
    if _pool.is_empty():
        return _scene.instantiate()
    var obj := _pool.pop_back()
    obj.set_process(true)
    return obj

func release(obj: Node) -> void:
    obj.set_process(false)
    _pool.append(obj)
```

有关完整实现的详细信息，请参阅 `references/patterns/object-pooling.md`。

### 存档/加载（概述）

使用资源或 JSON 存档数据：

```gdscript
# 自定义资源用于存档数据
class_name SaveData
extends Resource

@export var player_position: Vector2
@export var player_health: int
@export var inventory: Array[String]
@export var level_name: String

# 存档
func save_game(data: SaveData) -> void:
    ResourceSaver.save(data, "user://save.tres")

# 加载
func load_game() -> SaveData:
    if ResourceLoader.exists("user://save.tres"):
        return load("user://save.tres") as SaveData
    return SaveData.new()
```

有关全面指南的详细信息，请参阅 `references/patterns/save-load-system.md`。

## 常见反模式

| 反模式 | 问题 | 解决方案 |
|--------|------|----------|
| `_process` 中的轮询 | 在状态未改变时浪费 CPU | 使用信号进行状态变化 |
| `get_parent().get_parent()` | 紧密耦合、脆弱 | 信号向上，或使用组 |
| 深层节点路径 `$A/B/C/D` | 重构时易中断 | 使用 `%UniqueName` |
| `_process` 中的 `load()` | 卡顿、内存消耗 | `preload()` 或缓存引用 |
| 字符串信号 `emit_signal("x")` | 拼写错误、无自动补全 | 带类型提示：`signal_name.emit()` |
| 未类型化的 `@onready var x = $Node` | 失去自动补全 | 始终添加类型提示 |
| Autoloads 中的逻辑 | 测试难度、耦合 | 保持 Autoloads 轻量 |
| 魔术数字 | 含义不明确 | 使用 `const` 或 `@export` |
| `node != null` 用于已释放节点 | 返回已释放节点的 true | 使用 `is_instance_valid()` |
| 循环依赖 | 加载错误、流程不清晰 | 依赖注入或信号 |

## 额外资源

### 模式指南
- `references/patterns/state-machine.md` - 完整状态机实现
- `references/patterns/object-pooling.md` - 完整对象池系统
- `references/patterns/save-load-system.md` - 全面存档/加载指南
- `references/patterns/input-handling.md` - 输入缓冲和重新绑定

### 架构
- `references/architecture/project-structure.md` - 目录组织
- `references/architecture/scene-composition.md` - 场景设计模式
- `references/architecture/node-communication.md` - 信号与直接调用

### GDScript 深入
- `references/gdscript/type-system.md` - 静态类型深入
- `references/gdscript/coroutines-await.md` - 使用 await 的异步模式

### 模板
- `assets/templates/base-script.gd.md` - 标准脚本模板
- `assets/templates/state-machine.gd.md` - 状态机模板
- `assets/templates/autoload-manager.gd.md` - Autoload 单例模板

## 限制

- 仅限 GDScript（不包括 C#、GDExtension 或可视化脚本）
- 仅限 Godot 4.x 语法（某些模式与 3.x 不同）
- 仅限游戏相关模式（不包括编辑器插件开发）
- 无运行时验证脚本（GDScript 需要Godot 运行时）
