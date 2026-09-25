# Godot UI / 控制节点 (4.x)

使用 `Control` 锚点和 `Container` 节点布局响应式 UI，使用 `Theme` 进行样式设置，并通过键盘和游戏手柄进行导航。目标版本为 **Godot 4.7**。

## 使用场景

- 在构建 HUD、菜单、背包、对话框或设置界面时使用 `Control` 派生节点；
- 布局适应窗口大小的 UI；
- 主题化；
- 为控制器/键盘设置焦点导航。

**不建议使用场景：** 世界内的 2D 节点 (`Node2D`/精灵) → `godot-nodes-scenes`；
UI 过渡动画 → `godot-animation` (Tween)；
卡片游戏等特定类型 UI → `card-game`/`visual-novel`。完全重新绑定输入 → `input-systems`。

## 核心工作流程

1. **使用 `Control` 节点进行 UI**，而不是 `Node2D`。控制节点具有矩形（位置 + 大小）、锚点，并参与焦点/主题化。
2. **使用锚点实现响应式布局。** 锚点是父矩形（0-1）的分数，控制节点的边缘会吸附到这些位置。使用编辑器的 **布局** 预设（左上角、全矩形、居中等），而不是手动放置像素。
3. **让容器定位子节点。** 将子节点放入 `VBoxContainer`、`HBoxContainer`、`GridContainer`、`MarginContainer` 等。容器设置子节点的位置/大小；通过 `size_flags` 控制流。不要在容器内设置子节点锚点（会被覆盖）。
4. **使用 `Theme` 进行样式设置。** 在顶层 `Control` 上分配一个 `Theme` 资源；子节点会继承它。仅在必要时使用节点级别的主题覆盖。
5. **设置焦点**，以便游戏手柄/键盘可以在按钮间移动；设置默认焦点控制，并定义相邻节点或依赖自动相邻。
6. **连接信号** (`pressed`, `toggled`, `text_submitted`, `value_changed`)。

## 模式

### 1. 使用锚点实现响应式布局（代码形式）

```gdscript
extends Control

func _ready() -> void:
    # 将此面板拉伸以填充其父节点（相当于“全矩形”预设）。
    anchors_preset = Control.PRESET_FULL_RECT
    # 或者手动设置锚点：四个边缘位于父节点的最远角。
    # anchor_left = 0; anchor_top = 0; anchor_right = 1; anchor_bottom = 1
```

### 2. 使用容器和按钮信号构建菜单

```gdscript
extends VBoxContainer    # 子节点垂直堆叠，自动大小

func _ready() -> void:
    for child in get_children():
        if child is Button:
            child.pressed.connect(_on_button_pressed.bind(child.name))
    # 将第一个按钮设为焦点，以便游戏手柄可以立即导航。
    if get_child_count() > 0:
        (get_child(0) as Control).grab_focus()

func _on_button_pressed(which: StringName) -> void:
    match which:
        "PlayButton":  get_tree().change_scene_to_file("res://game.tscn")
        "QuitButton":  get_tree().quit()
```

### 3. 大小标志：使一个子节点扩展以填充剩余空间

```gdscript
# 在 HBoxContainer 中：左侧有一个标签，一个占位符占用剩余宽度。
func _ready() -> void:
    $Label.size_flags_horizontal = Control.SIZE_SHRINK_BEGIN
    $Spacer.size_flags_horizontal = Control.SIZE_EXPAND_FILL   # 扩展以填充
```

### 4. 单个节点的主题覆盖（无需完整的 `Theme` 资源）

```gdscript
func _ready() -> void:
    # 节点级别覆盖：使用 add_theme_*（类型特定设置器）。
    $Title.add_theme_font_size_override("font_size", 32)
    $Title.add_theme_color_override("font_color", Color.GOLD)
    $Panel.add_theme_stylebox_override("panel", preload("res://ui/panel.stylebox.tres"))
```

## 常见问题

- **混合手动位置与容器。** 容器子节点不能设置自己的位置/锚点——容器控制布局。要自由放置，请将节点从容器中移出或使用 `Control`/`PanelContainer` 包装器。
- **锚点与偏移量。** 锚点是父矩形的分数；偏移量是从锚点起的像素增量。通过预设设置锚点，然后用偏移量微调。仅设置位置而锚点为 0 时，UI 不会随窗口缩放。
- **使用 `Node2D` 进行 UI。** 在 `Node2D` 下父级的按钮/标签不会正确主题化或获取焦点。保持 UI 在 `CanvasLayer`/`Control` 子树下。
- **游戏手柄失去焦点。** 如果没有焦点，方向输入将无任何作用。在初始控制上调用 `grab_focus()` 并确保 `focus_mode` 不是 `FOCUS_NONE`。
- **主题与主题覆盖。** `Theme` 资源会样式化整个子树；`add_theme_*` 会覆盖单个节点。过度使用节点级别覆盖会破坏集中式主题化。
- **`rect_*` 属性被重命名。** Godot 3 的 `rect_size`/`rect_position`/`rect_min_size` 在 4.x 中现在是 `size`/`position`/`custom_minimum_size`。
- **全矩形 `Control` 的 `mouse_filter`** 可能会吞掉指向其下方节点的点击；在纯装饰性面板上设置 `MOUSE_FILTER_IGNORE`。

## 参考

- 关于锚点/偏移量数学、每种容器类型、构建/扩展 `Theme` 和 `StyleBox` 资源、焦点相邻节点连接以及 `CanvasLayer` 用于 HUD，请阅读 `references/layout-and-theming.md`。

## 相关技能

- `game-ui-ux` — 跨引擎 UI/UX：响应式缩放、安全区域、焦点导航、屏幕流。
- `godot-animation` — 基于 Tween 的 UI 过渡和动画效果。
- `godot-signals-groups` — 将 UI 事件连接到游戏逻辑。
- `input-systems` — 可重新绑定的输入和多设备焦点。
- `card-game` / `visual-novel` — UI 密集型特定类型模板。
