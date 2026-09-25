# Godot 节点与场景 (4.x)

使用节点和场景构建游戏，在运行时可实例化它们，并安全地访问树结构而不会因节点被释放或缺失而崩溃。目标版本 **Godot 4.7**。

## 使用场景

- 在构建 `.tscn` 场景结构时使用，选择如何将功能拆分为节点、实例化 `PackedScene`（子弹、敌人、UI），或设置自动加载的单例。
- 在调试 `get_node()` / `$Path` 返回 `null`，或出现 "Attempt to call on a previously freed instance" 错误时使用。

**不建议使用的情况：** GDScript 语言/语法 → `godot-gdscript`；基于信号的解耦 → `godot-signals-groups`；物理体/碰撞 → `godot-physics`。

## 核心工作流程

1. **使用组合进行建模。** 场景是作为 `.tscn` 保存的节点树。构建小型、单一用途的场景（玩家、子弹、敌人），并从它们组合成更复杂的场景。优先添加子节点，而不是深度继承。
2. **通过为根节点添加脚本并暴露 `@export` 配置来使场景可重用。** 保存它；它将成为一个可以多次实例化的 `PackedScene`。
3. **在运行时实例化** 使用 `preload`/`load` → `scene.instantiate()` → `add_child(instance)`。在添加后（或添加前）设置位置/状态（两者都有效）。
4. **安全地访问节点。** 使用 `@onready var x = $Path` 来访问固定子节点；使用唯一名称（`%Name`）来访问树中深层的节点；永远不要假设节点仍然存在。
5. **使用自动加载来管理全局状态/服务**（游戏状态、音频、场景切换）—— 在项目设置 > 全局（自动加载）中注册，可以在任何地方通过名称访问。
6. **使用 `queue_free()` 释放节点**，并使用 `is_instance_valid()` 来保护后续访问。

## 模式

### 1. 在运行时实例化场景

```gdscript
extends Node2D

const BULLET := preload("res://bullet.tscn")   # preload: 在编译时加载

func shoot(at: Vector2, dir: Vector2) -> void:
    var bullet := BULLET.instantiate()         # 创建场景的实例
    bullet.global_position = at
    bullet.direction = dir                      # 设置导出/公开状态
    add_child(bullet)                           # 现在它在树中并运行
```

### 2. 安全的节点访问：$、get_node_or_null 和唯一名称

```gdscript
@onready var label: Label = $UI/Label            # $ 是 get_node("UI/Label") 的简写
@onready var health_bar: ProgressBar = %HealthBar # % = 场景唯一名称（重命名安全）

func update() -> void:
    var optional := get_node_or_null("Maybe/Missing")  # 返回 null 而不是报错
    if optional:
        optional.queue_free()
```

### 3. 一个自动加载的单例（全局游戏状态）

```gdscript
# game_state.gd — 在项目设置 > 全局 > 自动加载中添加为 "GameState"。
extends Node

var score := 0
signal score_changed(value: int)

func add_score(points: int) -> void:
    score += points
    score_changed.emit(score)         # 任何场景都可以：GameState.score_changed.connect(...)
```

### 4. 切换正在运行的场景

```gdscript
func go_to_level_2() -> void:
    # 用另一个场景替换当前场景。释放旧场景树。
    get_tree().change_scene_to_file("res://levels/level_2.tscn")
    # 或者，使用预加载的 PackedScene：
    # get_tree().change_scene_to_packed(LEVEL_2)
```

## 陷阱

- **`$Path` / `get_node()` 返回 `null` 或报错** 当路径错误或节点尚未在树中时。使用 `@onready`，验证路径与场景匹配，或对可选节点使用 `get_node_or_null()`。
- **重命名节点会破坏 `$Path`。** 使用 **唯一名称**（`%Name`，通过右键点击 > 访问为唯一名称设置）以便深层引用在重命名和重新父化后仍然有效。
- **在帧中途中使用 `free()` 可能导致** 其他仍在使用该节点的代码崩溃。优先使用 `queue_free()`（在帧末尾删除）并检查 `is_instance_valid(node)`。
- **在 `add_child()` 之前设置子状态是安全的**，但子节点的 `_ready()` 只在它进入树后才运行——不要期望在那时之前它的 `@onready` 变量。
- **自动加载的顺序很重要**：自动加载在主场景之前按列表顺序添加。自动加载不能依赖主场景在此时已存在。
- **Godot 4 中 `instance()` 已重命名为 `instantiate()`。** `preload` 在解析时运行（路径必须为常量）；`load` 在运行时运行（路径可以是变量）。
- **`change_scene_to_file()` 是延迟执行的**，不是立即执行的——Godot 在当前帧末尾交换并释放旧场景。调用后的任何代码仍然针对 _旧_ 树，`get_tree().current_scene` 直到下一帧才变为新场景。不要在同一行读取新场景的节点；从新场景的 `_ready()` 中读取。

## 参考

- 关于场景继承、保存场景代码时的 `owner`/所有权、组与唯一名称，以及节点路径的边缘情况，请阅读 `references/tree-and-instancing.md`。

## 相关技能

- `godot-gdscript` — 语言、生命周期和 `@onready`。
- `godot-signals-groups` — 将实例化的场景与其生成者解耦。
- `godot-resources` — 在实例之间共享数据而不重复数据。
- `save-systems` — 在运行之间持久化场景/游戏状态。
