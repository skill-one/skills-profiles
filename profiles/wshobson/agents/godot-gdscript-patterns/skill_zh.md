# Godot GDScript 模式

Godot 4.x 游戏开发中使用的 GDScript 生产模式，涵盖架构、信号、场景和优化。

## 何时使用此技能

- 使用 Godot 4 开发游戏
- 在 GDScript 中实现游戏系统
- 设计场景架构
- 管理游戏状态
- 优化 GDScript 性能
- 学习 Godot 最佳实践

## 核心概念

### 1. Godot 架构

```
Node：基础构建块
├── Scene：可复用的节点树（保存为 .tscn）
├── Resource：数据容器（保存为 .tres）
├── Signal：事件通信
└── Group：节点分类
```

### 2. GDScript 基础

```gdscript
class_name Player
extends CharacterBody2D

# 信号
signal health_changed(new_health: int)
signal died

# 导出（可在检查器中编辑）
@export var speed: float = 200.0
@export var max_health: int = 100
@export_range(0, 1) var damage_reduction: float = 0.0
@export_group("战斗")
@export var attack_damage: int = 10
@export var attack_cooldown: float = 0.5

# Onready（准备好时初始化）
@onready var sprite: Sprite2D = $Sprite2D
@onready var animation: AnimationPlayer = $AnimationPlayer
@onready var hitbox: Area2D = $Hitbox

# 私有变量（约定：下划线前缀）
var _health: int
var _can_attack: bool = true

func _ready() -> void:
    _health = max_health

func _physics_process(delta: float) -> void:
    var direction := Input.get_vector("left", "right", "up", "down")
    velocity = direction * speed
    move_and_slide()

func take_damage(amount: int) -> void:
    var actual_damage := int(amount * (1.0 - damage_reduction))
    _health = max(_health - actual_damage, 0)
    health_changed.emit(_health)

    if _health <= 0:
        died.emit()
```

## 详细模式和工作示例

详细模式文档位于 `references/details.md`。当上述导航层级不足时，请阅读该文件。
