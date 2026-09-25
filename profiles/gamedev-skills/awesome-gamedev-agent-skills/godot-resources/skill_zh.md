# Godot 资源 (4.x)

将游戏数据建模为可重用、可在 Inspector 中编辑的 `Resource` 对象，而不是硬编码的值，并以 `.tres`/`.res` 格式加载/保存它们。目标 **Godot 4.7**。

## 何时使用

- 当表示物品、属性、敌人配置、对话行或关卡元数据为数据时；在 Inspector 中创建 `.tres` 文件；或加载/保存自定义资源时使用。

**不应使用的情况：** 节点/场景结构 → `godot-nodes-scenes`；保存玩家的 *运行时进度*（引擎无关的保存格式/槽位）→ `save-systems`；此模式的 C# 变体 → `godot-csharp`。

## 核心工作流程

1. **从 `Resource` 继承**，并包含 `class_name` 和 `@export` 字段。它现在出现在 "新建资源" 对话框中，并作为 `@export` 类型，可在 Inspector 中编辑。
2. **在 FileSystem 面板中创建 `.tres` 文件**（文本，支持差异）或 `.res`（二进制，更小/更快）。在 Inspector 中编辑其字段——无需代码。
3. **通过 `@export var data: ItemResource` 或数组 `@export var loot: Array[ItemResource]` 从节点中引用资源**。
4. **在运行时加载**，使用 `preload`（常量路径）或 `load`/`ResourceLoader.load`（变量路径）。对大型资源使用线程加载。
5. **在运行时修改共享资源之前进行复制**，否则使用它的每个节点都会改变（资源是共享引用）。
6. **使用 `ResourceSaver.save` 保存生成的/编辑的资源**。

## 模式

### 1. 自定义数据资源

```gdscript
# item.gd
extends Resource
class_name ItemResource

@export var id: StringName = &""
@export var display_name: String = "Item"
@export_multiline var description: String = ""
@export var icon: Texture2D
@export var max_stack: int = 99
@export var value: int = 0
```

在 FileSystem 面板中从该类创建 `sword.tres` 并在 Inspector 中填写。

### 2. 从节点中消费资源

```gdscript
extends Node
@export var starting_items: Array[ItemResource] = []   # 在 Inspector 中拖入 .tres 文件

func _ready() -> void:
    for item in starting_items:
        print("拥有: %s (最大 x%d)" % [item.display_name, item.max_stack])
```

### 3. 修改共享数据前进行复制

```gdscript
func give_unique_copy(template: ItemResource) -> ItemResource:
    # true = 深拷贝子资源；false = 浅拷贝（共享子资源）。
    var copy: ItemResource = template.duplicate(true)
    copy.value += 5                # 修改副本不会影响模板 .tres
    return copy
```

### 4. 运行时保存和加载资源

```gdscript
func save_config(cfg: Resource) -> void:
    ResourceSaver.save(cfg, "user://config.tres")   # user:// = 可写应用数据目录

func load_config() -> Resource:
    if ResourceLoader.exists("user://config.tres"):
        return ResourceLoader.load("user://config.tres")
    return null
```

## 陷阱

- **资源是按引用共享的。** 一个分配给多个节点的 `.tres` 是同一个对象——修改它会改变所有使用它的节点（并重新保存文件）。调用 `duplicate(true)` 以实现每个实例的状态。
- **需要 `class_name` 才能从编辑器中实例化。** 没有 `class_name`，该类不会出现在 "新建资源" 对话框中或作为 `@export` 类型。
- **`res://` 在导出游戏中是只读的。** 将运行时数据写入 `user://`，切勿写入 `res://`。`ResourceSaver.save` 到 `res://` 仅在编辑器中有效。
- **将节点存储在资源中不会序列化它们。** 资源存储数据，而不是活动的场景节点。通过 `PackedScene` 而不是节点实例引用场景。
- **循环资源引用**（A 持有 B 持有 A）可能无法干净地保存/加载——保持数据图无环或使用 ID/查找。
- **`preload` vs `load`。** `preload` 需要常量路径并在脚本中加载；`load` 接受运行时的变量路径。在 `load` 之前使用 `ResourceLoader.exists()` 以避免因文件缺失而出错。
- **不要将秘密信息存储在 `.tres` 中**——它们以明文形式包含在导出文件中。

## 参考

- 对于线程/后台加载 (`load_threaded_request`)、带自定义设置的 `@tool` 资源、自定义 `ResourceFormatLoader`/`Saver`、资源本地到场景、资源 UIDs，请阅读 `references/resource-patterns.md`。

## 相关技能

- `godot-gdscript` — 使用 `@export` 注释定义资源字段。
- `godot-nodes-scenes` — 实例化场景与共享资源数据。
- `save-systems` — 持久化运行时进度（与静态数据无关）。
- `unity-scriptableobjects` — Unity 中等效的数据资产模式。
