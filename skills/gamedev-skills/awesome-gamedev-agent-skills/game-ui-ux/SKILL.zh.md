---
name: game-ui-ux
description: 设计并构建能够在所有屏幕上正常运行的游戏UI/UX——包括HUD、菜单和覆盖层——采用基于锚点的响应式布局、分辨率/宽高比例缩放和安全区域、键盘/手柄焦点导航、屏幕/菜单状态栈，以及事件驱动（非轮询）的HUD更新。使用与检测到的引擎UI技能相匹配的引擎无关模式。当用户提及HUD、生命值条、主菜单、暂停菜单、设置界面、UI布局、锚点、UI缩放、宽高比、安全区域、控制器/键盘菜单导航，或UI与游戏状态连接时使用。
---

# 游戏界面/用户体验

构建适用于手机、超宽显示器和电视的HUD（平视显示器）和菜单，跨游戏手柄和鼠标保持正确显示。这项技能拥有引擎无关的界面架构——响应式布局、缩放、焦点导航、屏幕流程以及界面如何与游戏状态交互——并将具体的组件API委托给引擎界面技能。

## 使用场景

- 在构建HUD（生命/弹药/得分）、菜单（主菜单/暂停/设置）、库存或商店屏幕，或任何叠加层时使用，并希望它能正确缩放和导航。
- 用于修复在其他分辨率/宽高比下崩溃的UI、忽略凹口/安全区域、无法与控制器一起使用，或通过每帧轮询与游戏状态连接的UI。
- 用于将屏幕流程（标题→游戏→暂停→设置）作为堆栈结构，而不是标志汤。

**不使用场景：** 对于引擎的具体界面节点/组件和样式，使用`godot-ui-control`或Unity UI（UGUI/UI Toolkit）。对于*视觉*冲击（按钮弹出、伤害数字、震动）使用`game-feel`。对于分支对话UI使用`dialogue-systems`。对于翻译UI字符串，那是本地化（参见`references/`和`input-systems`以重新绑定屏幕）。对于卡片/棋盘布局的具体情况，`card-game`类型组合这项技能。

## 核心工作流程

1. **选择布局模型：锚点+容器，绝不使用绝对像素。** 将元素锚定到边缘/角落/中心，并让容器（行、列、网格）流动子元素。绝对`(x, y)`位置会在第一个新分辨率时失效。
2. **为整个UI选择缩放策略：** 一个参考分辨率，使其缩放以适应（大多数游戏），以及在其他宽高比上额外宽度/高度的策略（画幅、扩展或锚定HUD角落向外）。
3. **尊重安全区域。** 从屏幕边缘嵌入关键UI，以防止凹口、圆角和电视 overscan 切割它。
4. **使每个屏幕都可通过键盘/游戏手柄导航。** 为每个屏幕设置一个初始焦点，定义焦点顺序/相邻元素，并显示清晰的焦点高亮。鼠标和焦点必须共存。
5. **将屏幕建模为堆栈。** 推（暂停游戏），弹（恢复），输入+可见性交给顶部屏幕。这使得叠加层和“返回”变得简单。
6. **通过事件而非轮询驱动HUD。** HUD订阅`health_changed`、`score_changed`等事件，仅在它们触发时更新——它不会每帧读取游戏状态。
7. **跨屏幕和设备进行验证。** 调整窗口大小，切换宽高比，拔掉鼠标仅通过游戏手柄导航，并确认焦点、缩放和安全区域嵌入。报告你在哪些分辨率下实际观察到的情况。

## 模式

### 1. 锚点+容器，而非绝对坐标

```gdscript
# Godot 4.7 锚定HUD标签到TOP-LEFT；让容器流动一行心形。
func _ready() -> void:
    $Score.set_anchors_preset(Control.PRESET_TOP_LEFT)   # 任何大小都粘在角落
    # HBoxContainer自动从左到右布局子元素；绝不要手动定位心形。
    for i in lives:
        $Hearts.add_child(make_heart())                   # HBoxContainer为你间隔它们
# Unity 6.3 LTS uGUI：设置RectTransform锚点到角落；使用HorizontalLayoutGroup。
# RIGHT: 锚点+布局组。WRONG: rect.anchoredPosition = new Vector2(640, 360) (仅1080p)。
```

### 2. 缩放到参考分辨率（一个UI，多个屏幕）

```text
# Godot 4.7 — 项目设置>显示>窗口>拉伸：
#   模式 = "canvas_items"，宽高比 = "expand"，参考大小例如1920x1080。
#   UI缩放到窗口；“expand”显示你锚定HUD角落的额外空间。
# Unity 6.3 LTS — 画布>CanvasScaler：
#   UI缩放模式 = "Scale With Screen Size"，参考分辨率 = 1920x1080，
#   匹配 = 0.5（混合宽高）—— 如果你的HUD高度关键，则选择1.0。
```

### 3. 凹口/overscan的安全区域嵌入

```gdscript
# Godot 4.7. 嵌入到操作系统报告的安全矩形（手机、电视）的边距容器。
func _apply_safe_area() -> void:
    var safe: Rect2i = DisplayServer.get_display_safe_area()
    var win := DisplayServer.window_get_size()
    $Margin.add_theme_constant_override("margin_left", safe.position.x)
    $Margin.add_theme_constant_override("margin_top",  safe.position.y)
    $Margin.add_theme_constant_override("margin_right", win.x - safe.end.x)
    $Margin.add_theme_constant_override("margin_bottom", win.y - safe.end.y)
# Unity 6.3 LTS: 读取Screen.safeArea（像素中的矩形）并设置面板的anchorMin/anchorMax为
# safeArea.position / (position+size)通过Screen.width/height归一化。
```

### 4. 游戏手柄/键盘焦点（没有它控制器上的UI无法使用）

```gdscript
# Godot 4.7. 给每个屏幕一个默认焦点，并连接相邻元素，以便摇杆/方向键可以导航。
func _on_screen_shown() -> void:
    $PlayButton.grab_focus()                               # 打开时始终聚焦某物
$PlayButton.focus_neighbor_bottom = $SettingsButton.get_path()
$SettingsButton.focus_neighbor_top = $PlayButton.get_path()
# Unity 6.3 LTS: EventSystem.SetSelectedGameObject(playButton) 在启用时；设置每个Selectable的
# 导航（显式或自动）。RIGHT: 打开时焦点在一个控制上。WRONG: 未选择→游戏手柄无反应，玩家卡住。
```

### 5. 事件驱动HUD（将UI与游戏逻辑解耦）

```gdscript
# RIGHT: HUD对信号做出反应；仅在生命值实际变化时更新。
func _ready() -> void:
    player.health_changed.connect(_on_health_changed)     # 由游戏逻辑发出
func _on_health_changed(current: int, max: int) -> void:
    $HealthBar.value = float(current) / max
# WRONG: func _process(dt): $HealthBar.value = player.hp / player.max_hp  # 每帧轮询，
# 将UI与玩家的内部结构耦合，并且在未变化时也会运行工作。
```

## 陷阱

- **绝对像素位置/单个设计分辨率。** 在你的显示器上看起来正确，在其他地方都损坏。锚定到边缘/中心，并随容器流动。
- **没有宽高比策略。** 仅16:9的布局在超宽显示器和手机上严重裁剪或画幅。决定扩展与画幅，并将HUD锚定向外移动的角落。
- **忽略安全区域。** 凹口下的HUD或被电视overscan丢失。嵌入关键元素。
- **没有初始焦点/没有焦点相邻元素。** 游戏在游戏手柄上无法玩；玩家落在未选择任何元素的菜单上。始终聚焦一个控制并定义导航。
- **在`_process`/`Update`中轮询游戏状态。** 将UI与内部结构耦合并浪费工作。通过信号/事件推送更新。
- **极小的固定字体大小。** 在远距离电视或小手机上难以阅读。随UI缩放文本，并提供文本大小选项。
- **菜单流程作为布尔标志** (`isPaused`, `inSettings`, …)变得无法管理。使用屏幕堆栈与push/pop。
- **硬编码的英文字符串嵌入布局。** 翻译溢出按钮。外部化字符串并让容器根据内容调整大小（参见`references/`）。
- **仅鼠标或仅焦点。** 支持两者；切换输入设备不应让用户困住。

## 参考

- 对于每个引擎的拉伸/缩放模式、安全区域数学、完整的焦点导航和屏幕堆栈模式、非拟人化UI与拟人化UI、无障碍性（文本大小、对比度、无障碍状态），以及本地化准备好的布局，请阅读`references/layout-and-flow.md`。

## 相关技能

- `godot-ui-control`, Unity UI (UGUI/UI Toolkit) — 具体的组件、主题和样式。
- `game-feel` — 按钮弹出、过渡和HUD精华，这些是在此布局之上运行的。
- `dialogue-systems` — 在此UI外壳内运行的对话/选择UI。
- `input-systems` — 设备切换、重新绑定屏幕和可访问控制。
- `rpg`, `card-game`, `tower-defense`, `visual-novel` — 组合此技能的UI密集型类型。
