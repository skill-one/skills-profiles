# 游戏界面/用户体验

构建适用于手机、超宽显示器和电视的HUD（平视显示器）和菜单，确保在游戏手柄和鼠标输入下都能正确显示。这项技能拥有引擎无关的UI架构——响应式布局、缩放、焦点导航、屏幕流程以及UI与游戏状态的交互方式——并将具体的组件API委托给引擎的UI技能。

## 使用场景

- 在构建HUD（生命值/弹药/得分）、菜单（主菜单/暂停/设置）、库存或商店界面，或任何需要正确缩放和导航的覆盖层时使用。
- 用于修复在其他分辨率/宽高比下失效的UI、忽略凹口/安全区域、无法使用控制器，或通过每帧轮询与游戏状态绑定的UI。
- 用于将屏幕流程（标题→游戏→暂停→设置）作为栈结构组织，而不是简单的标志集合。

**不适用场景：** 对于引擎的具体UI节点/组件和样式，请使用`godot-ui-control`或Unity UI（UGUI/UI Toolkit）。对于视觉效果（按钮弹出、伤害数字、震动）使用`game-feel`。对于分支对话UI使用`dialogue-systems`。对于UI字符串翻译，那是本地化（参见`references/`和`input-systems`以重新绑定屏幕）。对于卡片/棋盘布局的具体需求，`card-game`类型会组合这项技能。

## 核心工作流程

1. **选择布局模型：锚点+容器，绝不使用绝对像素。** 将元素锚定到边缘/角落/中心，让容器（行、列、网格）流式布局子元素。绝对`(x, y)`位置会在第一个新分辨率下失效。
2. **为整个UI选择缩放策略：** 一个参考分辨率用于缩放以适应（大多数游戏），以及在其他宽高比下的额外宽度/高度策略（遮幅、扩展或锚定HUD角落向外）。
3. **尊重安全区域。** 将关键UI从屏幕边缘内嵌，以避免凹口、圆角和电视 overscan 导致的裁剪。
4. **使每个屏幕都可通过键盘/游戏手柄导航。** 为每个屏幕设置一个初始焦点，定义焦点顺序/相邻关系，并显示清晰的焦点高亮。鼠标和焦点必须共存。
5. **将屏幕建模为栈。** 推（暂停游戏）、弹（恢复），输入和可见性交给顶层屏幕。这使得覆盖层和“返回”变得简单。
6. **通过事件而非轮询驱动HUD。** HUD订阅`health_changed`、`score_changed`等事件，仅在它们触发时更新——它不会每帧读取游戏状态。
7. **跨屏幕和设备验证。** 调整窗口大小，切换宽高比，拔掉鼠标仅通过游戏手柄导航，并确认焦点、缩放和安全区域内嵌。报告你在哪些分辨率下实际观察到的现象。

## 模式

### 1. 锚点+容器，而非绝对坐标

```gdscript
# Godot 4.7 锚定HUD标签到TOP-LEFT；让容器流式布局一行心形图标。
func _ready() -> void:
    $Score.set_anchors_preset(Control.PRESET_TOP_LEFT)   # 任何尺寸下都粘在角落
    # HBoxContainer自动从左到右流式布局子元素；绝不要手动定位心形图标。
    for i in lives:
        $Hearts.add_child(make_heart())                   # HBoxContainer为你间隔它们
# Unity 6.3 LTS uGUI：设置RectTransform锚点到角落；使用HorizontalLayoutGroup。
# RIGHT：锚点+布局组。WRONG：rect.anchoredPosition = new Vector2(640, 360) (仅1080p适用)。
```

### 2. 缩放到参考分辨率（一个UI，多个屏幕）

```text
# Godot 4.7 — 项目设置 > 显示 > 窗口 > 拉伸：
#   模式 = "canvas_items"，宽高比 = "expand"，参考尺寸例如1920x1080。
#   UI缩放到窗口；"expand"显示额外空间，你锚定HUD角落到其中。
# Unity 6.3 LTS — 画布 > CanvasScaler：
#   UI缩放模式 = "Scale With Screen Size"，参考分辨率 = 1920x1080，
#   匹配 = 0.5 (宽度/高度混合) — 如果你的HUD高度关键，选择1.0。
```

### 3. 凹口/overscan的安全区域内嵌

```gdscript
# Godot 4.7. 内嵌边距容器到操作系统报告的安全矩形（手机、电视）。
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

### 4. 游戏手柄/键盘焦点（没有焦点，控制器上的UI无法使用）

```gdscript
# Godot 4.7. 为每个屏幕设置默认焦点，并连接相邻关系，以便摇杆/方向键导航。
func _on_screen_shown() -> void:
    $PlayButton.grab_focus()                               # 打开时始终聚焦某物
$PlayButton.focus_neighbor_bottom = $SettingsButton.get_path()
$SettingsButton.focus_neighbor_top = $PlayButton.get_path()
# Unity 6.3 LTS: 在启用时调用EventSystem.SetSelectedGameObject(playButton)；设置每个Selectable的
# 导航（显式或自动）。RIGHT：打开时焦点在某个控件上。WRONG：未选择→游戏手柄无响应，玩家卡住。
```

### 5. 事件驱动HUD（将UI与游戏逻辑解耦）

```gdscript
# RIGHT：HUD对信号做出反应；仅在生命值实际变化时更新。
func _ready() -> void:
    player.health_changed.connect(_on_health_changed)     # 由游戏逻辑发出
func _on_health_changed(current: int, max: int) -> void:
    $HealthBar.value = float(current) / max
# WRONG: func _process(dt): $HealthBar.value = player.hp / player.max_hp  # 每帧轮询，
# 将UI与玩家的内部结构绑定，并在未变化时仍执行工作。
```

## 陷阱

- **绝对像素位置/单一设计分辨率。** 在你的显示器上看起来正常，在其他地方都失效。锚定到边缘/中心，并随容器流式布局。
- **没有宽高比策略。** 仅16:9的布局在超宽显示器和手机上严重遮幅或遮幅。决定扩展或遮幅，并锚定HUD到向外移动的角落。
- **忽略安全区域。** 凹口下的HUD或被电视overscan丢失的HUD。内嵌关键元素。
- **没有初始焦点/没有焦点相邻关系。** 游戏在游戏手柄上无法玩；玩家落在未选择任何控件的菜单上。始终聚焦一个控件并定义导航。
- **在`_process`/`Update`中轮询游戏状态。** 将UI与内部结构绑定并浪费工作。通过信号/事件推送更新。
- **极小的固定字体大小。** 在远距离电视或小手机上难以阅读。随UI缩放文本，并提供文本大小选项。
- **菜单流程作为布尔标志** (`isPaused`, `inSettings`, …)变得难以管理。使用屏幕栈与推/弹。
- **硬编码的英文字符串嵌入布局。** 翻译溢出按钮。外部化字符串，并让容器根据内容调整大小（参见`references/`）。
- **仅鼠标或仅焦点。** 支持两者；切换输入设备不应困住用户。

## 参考文献

- 关于每个引擎的拉伸/缩放模式、安全区域数学、完整的焦点导航和屏幕栈模式、拟真与非拟真UI、无障碍性（文本大小、对比度、无障碍状态），以及本地化准备好的布局，请阅读`references/layout-and-flow.md`。

## 相关技能

- `godot-ui-control`, Unity UI (UGUI/UI Toolkit) — 具体的组件、主题和样式。
- `game-feel` — 按钮弹出、过渡和HUD的视觉效果，构建在这布局之上。
- `dialogue-systems` — 在此UI外壳内的对话/选择UI。
- `input-systems` — 设备切换、重新绑定屏幕和可访问控件。
- `rpg`, `card-game`, `tower-defense`, `visual-novel` — 重度依赖UI的类型，会组合这项技能。
