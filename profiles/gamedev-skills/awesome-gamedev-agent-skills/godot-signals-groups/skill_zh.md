# Godot 信号与组 (4.x)

使用观察者模式（信号）解耦节点，并通过组同时作用于多个节点，而不是在场景之间硬编码引用。目标 **Godot 4.7**。

## 使用场景

- 当一个节点需要通知其他节点“某事发生了”（玩家死亡、物品拾取、波次清除），而不直接持有它们的引用时使用。
- 当你需要一次性处理整个节点类别时使用（例如，“暂停所有敌人”、“保存所有检查点”）。

**不使用场景：** 原始信号语法基础 → `godot-gdscript`；场景结构和实例化 → `godot-nodes-scenes`。对于跨场景的全局事件，从自动加载模块发出（参见 `godot-nodes-scenes`）。

## 核心工作流程

1. **确定方向。** 子节点/子场景应向上发出信号；父节点连接到它。这使子节点保持可重用且对监听者不知情。
2. 在发射器上声明类型化的信号；当事件发生时 `emit()` 它。
3. 使用可调用对象连接（`sig.connect(_on_sig)`），可选地在编辑器的节点泊坞窗中连接。使用 `CONNECT_ONE_SHOT` 进行一次性触发，使用 `bind()` 传递额外上下文。
4. 使用组进行广播：将节点添加到命名组，然后迭代 `get_tree().get_nodes_in_group(...)` 或 `call_group(...)`。
5. 在需要时断开连接（例如，在释放长生命周期的监听器之前），并检查 `is_connected()` 以避免重复连接。

## 模式

### 1. 向上发出信号，从父节点连接

```gdscript
# coin.gd (可重用的拾取物 — 什么也不知道关于玩家或HUD)
extends Area2D
signal collected(value: int)

func _on_body_entered(body: Node) -> void:
    if body.is_in_group("player"):
        collected.emit(10)
        queue_free()
```

```gdscript
# level.gd (父节点将金币连接到游戏状态)
func _ready() -> void:
    for coin in get_tree().get_nodes_in_group("coins"):
        coin.collected.connect(_on_coin_collected)

func _on_coin_collected(value: int) -> void:
    GameState.add_score(value)
```

### 2. 连接标志：一次性和绑定额外参数

```gdscript
func _ready() -> void:
    # 精确触发一次，然后自动断开连接。
    $Door.opened.connect(_on_door_opened, CONNECT_ONE_SHOT)
    # bind() 在连接时追加参数（在信号自己的参数之后）。
    $RedButton.pressed.connect(_on_button.bind("red"))

func _on_button(color: String) -> void:
    print("按下了 %s 按钮" % color)
```

### 3. 组：向多个节点广播

```gdscript
func pause_all_enemies() -> void:
    # 对“enemies”组中的每个节点调用方法（如果缺失则无操作）。
    get_tree().call_group("enemies", "set_paused", true)

func count_enemies() -> int:
    return get_tree().get_nodes_in_group("enemies").size()
```

从代码或通过编辑器的节点 > 组选项卡添加节点到组：

```gdscript
func _ready() -> void:
    add_to_group("enemies")        # remove_from_group("enemies") 以退出
```

### 4. 内联等待信号

```gdscript
func open_chest() -> void:
    $AnimationPlayer.play("open")
    await $AnimationPlayer.animation_finished   # 等待它发出信号后暂停
    spawn_loot()
```

## 陷阱

- **3.x 的连接签名已消失。** `connect("died", self, "_on_died")` → `died.connect(_on_died)`。目标由可调用对象隐含。传统的 `Object.connect("died", Callable(self, "_on_died"))` 可以工作，但方法名字符串形式不行。
- **重复连接会多次触发处理器。** 在 `_ready()` 中重新添加节点后再次连接会堆叠回调。使用 `if not sig.is_connected(cb): sig.connect(cb)` 进行保护。
- **连接到已释放的节点会报错。** 断开长生命周期的监听器，或依赖 Godot 在连接对象被释放时自动断开连接（它对节点是这么做的）。
- **组对整个 SceneTree 是全局的，不是按场景。** 两个级别使用相同组名的成员会共享。如果需要命名空间，请命名组。
- **`call_group` 会静默忽略没有该方法的节点。** 方法名中的拼写错误会安静地失败 — 当合同重要时，优先使用类型化信号。
- **信号参数必须匹配。** 使用错误的参数数量/类型会引发错误；声明类型化参数并精确发出这些参数。

## 参考

- 关于连接标志、延迟连接、自定义信号参数、带超时的等待以及信号与直接调用权衡，请阅读 `references/signal-patterns.md`。

## 相关技能

- `godot-gdscript` — 信号/`await` 语法基础。
- `godot-nodes-scenes` — 用于全局事件总线的自动加载模块。
- `game-ai` — 常常驱动和消费这些事件的有限状态机。
