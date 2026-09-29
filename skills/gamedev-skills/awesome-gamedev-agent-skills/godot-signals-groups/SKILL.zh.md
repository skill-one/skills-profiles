---
name: godot-signals-groups
description: 构建基于信号和节点组的 Godot 4.7 解耦事件驱动游戏玩法：声明和发射自定义信号，通过可调用对象（包括绑定/一次性）进行连接，并通过节点组及 call_group 函数向多个节点广播。适用于 Godot 项目中节点通信的线路连接，可替代紧密引用信号、发射/连接事件，或迁移 3.x 版本的 connect("sig", self, "method") 代码。
---

# Godot 信号与组 (4.x)

使用观察者模式（信号）解耦节点，并通过组一次性对多个节点进行操作，而不是在场景之间硬编码引用。目标 **Godot 4.7**。

## 使用场景

- 当一个节点需要告诉其他节点“某事发生了”（玩家死亡、物品拾取、波次清除）而不直接引用它们时使用。
- 当你需要一次性处理整个节点类别时使用（“暂停所有敌人”、“保存所有检查点”）。

**不使用时的场景**：原始信号语法基础 → `godot-gdscript`；场景结构和实例化 → `godot-nodes-scenes`。对于跨场景的全局事件，从自动加载模块发出（参见 `godot-nodes-scenes`）。

## 核心工作流程

1. **确定方向**。子节点/子场景应向上*发出*信号；父节点*连接*到它。这使子节点可重用且对监听者一无所知。
2. 在发射器上声明*类型化的信号*；当事件发生时*发出*它们。
3. 使用*可调用对象*（`sig.connect(_on_sig)`）连接，可选地在编辑器的节点泊坞窗中操作。使用 `CONNECT_ONE_SHOT` 进行一次性触发，`bind()` 传递额外上下文。
4. 使用组进行广播：将节点添加到命名组中，然后迭代 `get_tree().get_nodes_in_group(...)` 或 `call_group(...)`。
5. 在需要时*断开连接*（例如，在释放长生命周期监听器之前），并检查 `is_connected()` 以避免重复连接。

## 模式

### 1. 向上发出信号，从父节点连接

```gdscript
# coin.gd (可重用的拾取物 — 什么都不知道关于玩家或HUD)
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
    # 一次性触发，然后自动断开连接。
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

从代码或通过编辑器的节点 > 组选项卡将节点添加到组：

```gdscript
func _ready() -> void:
    add_to_group("enemies")        # remove_from_group("enemies") 以退出
```

### 4. 内联等待信号

```gdscript
func open_chest() -> void:
    $AnimationPlayer.play("open")
    await $AnimationPlayer.animation_finished   # 直到它发出信号后暂停
    spawn_loot()
```

## 陷阱

- **3.x 的连接签名已消失**。`connect("died", self, "_on_died")` → `died.connect(_on_died)`。目标由可调用对象隐含。传统的 `Object.connect("died", Callable(self, "_on_died"))` 可以工作，但方法名字符串形式不行。
- **重复连接会多次触发处理器**。在 `_ready()` 中重新添加节点后再次连接会堆叠回调。使用 `if not sig.is_connected(cb): sig.connect(cb)` 进行保护。
- **连接到已释放的节点会报错**。断开长生命周期监听器，或依赖 Godot 在连接对象被释放时自动断开连接（它对节点是这么做的）。
- **组对整个 SceneTree 是全局的，不是按场景**。两个级别使用相同组名的成员会共享。如果需要命名空间，请命名组。
- **`call_group` 会静默忽略没有该方法的节点**。方法名拼写错误会安静失败 — 当合同重要时，优先使用类型化信号。
- **信号参数必须匹配**。使用错误数量或类型的参数发出会引发错误；声明类型化参数并精确发出。

## 参考

- 关于连接标志、延迟连接、自定义信号参数、带超时的等待以及信号与直接调用权衡，请阅读 `references/signal-patterns.md`。

## 相关技能

- `godot-gdscript` — 信号/`await` 语法基础。
- `godot-nodes-scenes` — 用于全局事件总线的自动加载模块。
- `game-ai` — 常常驱动和消费这些事件的有限状态机。
