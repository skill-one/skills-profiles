# Godot GDScript (4.x)

编写正确的、静态类型的 GDScript，并按照引擎的意图使用节点生命周期和信号系统。目标为 **Godot 4.7** (GDScript 2.0)。

## 何时使用

- 在编写或修复 `.gd` 文件时使用：声明变量、函数、类，使用 `@export`/`@onready`，连接信号，或等待协程/信号。
- 在将 Godot 3.x 脚本移植到 4.x 且脚本不再被解析时使用。

**不使用的情况：** 场景/节点结构及实例化问题 → `godot-nodes-scenes`；信号 *架构* / 解耦模式 → `godot-signals-groups`；使用 C# 而不是 GDScript → `godot-csharp`。

## 核心工作流程

1. **尽可能使用类型。** GDScript 2.0 支持静态类型 (`var hp: int = 10`，`func add(a: int, b: int) -> int:`)。类型在解析时捕获错误并加速虚拟机。使用 `:=` 进行类型推断。
2. **按其用途使用生命周期回调：** `_ready()` 在节点及其子节点进入树时执行一次；`_process(delta)` 每个渲染帧执行一次；`_physics_process(delta)` 在固定物理帧上执行（用于移动/物理）。
3. **使用 `@onready` 获取节点引用**，而不是在 `_init()` 中获取——子节点在节点进入树之前不存在。
4. **使用 `@export` 暴露可调参数**，以便设计师在 Inspector 中编辑它们。
5. **使用信号 + `await` 响应事件**，而不是轮询，这样代码更清晰。
6. **运行并读取错误。** Debugger 面板打印带行号的类型错误；首先修复第一个错误（后面的错误通常是级联错误）。

## 模式

### 1. 带生命周期、@export 和 @onready 的类型化脚本

```gdscript
extends Node2D
class_name Spinner            # 注册一个全局类型，可在其他脚本中使用

@export var speed: float = 90.0          # 可在 Inspector 中编辑（度/秒）
@export_range(0, 10, 0.5) var wobble := 2.0
@onready var sprite: Sprite2D = $Sprite2D # 在节点进入树时解析

func _ready() -> void:
    # 运行一次，在子节点准备好之后。此时可以安全地操作 $Sprite2D。
    sprite.modulate = Color.AQUA

func _process(delta: float) -> void:
    # delta 是上一帧以来的秒数；将速率乘以它以实现帧率独立性。
    rotation_degrees += speed * delta
```

### 2. 信号：声明、发射、连接 (4.x Callable 语法)

```gdscript
extends Node

signal health_changed(current: int, maximum: int)   # 带有类型化信号参数

var health := 100

func take_damage(amount: int) -> void:
    health = max(health - amount, 0)
    health_changed.emit(health, 100)     # 4.x：作为信号上的方法发射

func _ready() -> void:
    # 4.x：使用 Callable 连接，而不是字符串方法名。
    health_changed.connect(_on_health_changed)

func _on_health_changed(current: int, maximum: int) -> void:
    print("HP: %d/%d" % [current, maximum])
```

### 3. await — 暂停直到计时器或信号触发（替换 3.x yield）

```gdscript
func flash_then_continue() -> void:
    modulate = Color.RED
    await get_tree().create_timer(0.2).timeout   # 0.2s 后继续
    modulate = Color.WHITE
    # await 任何信号：var result = await some_node.some_signal
```

### 4. Lambdas、类型化数组和安全访问

```gdscript
var enemies: Array[Node] = []                    # 类型化数组

func cull_dead() -> void:
    enemies = enemies.filter(func(e): return e.is_inside_tree())

func get_first_name(d: Dictionary) -> String:
    return d.get("name", "unknown")              # 默认值避免了缺少键的错误
```

## 陷阱

- **3.x → 4.x 信号 API 已更改。** `emit_signal("x")` 仍然有效，但优先使用 `x.emit(...)`；`connect("x", self, "_on_x")` 已消失——使用 `x.connect(_on_x)` 并配合 Callable。`yield(obj, "sig")` 现在是 `await obj.sig`。
- **`export var` 现在是 `@export var`**（注解）。同样 `onready`→`@onready`，`tool`→`@tool`，`remote`/`master` RPC 关键字→`@rpc(...)` 注解。
- **`@onready` 和 `$NodePath` 在 `_init()` 中失败**——节点尚未进入树。在 `_ready()` 或使用 `@onready` 中初始化节点引用。
- **整数除法会截断。** `5 / 2 == 2`。使用 `5.0 / 2` 或强制转换为 `float`。
- **`_process` vs `_physics_process`。** 将 `move_and_slide()` 和物理放在 `_physics_process(delta)` 中；使用 `_process` 会使运动依赖于帧率。
- **`class_name` 必须在项目中唯一**，并且在使用其他脚本中的类型名或作为 Inspector 类型时是必需的。

## 参考

- 要了解完整的注解列表、高级类型化和样式规范，请阅读 `references/annotations-and-typing.md`。

## 相关技能

- `godot-nodes-scenes` — 场景树、实例化和自动加载。
- `godot-signals-groups` — 使用信号和组的事件驱动架构。
- `godot-resources` — 使用自定义 `Resource` 类型的数据驱动设计。
- `godot-csharp` — 使用 C#/.NET 的相同引擎概念。
