# 桌面控制技能

该技能通过 PyAutoGUI 提供全面的桌面自动化功能，使 AI 代理能够控制鼠标、键盘、进行屏幕截图以及与桌面环境交互。

## 如何使用此技能

作为 AI 代理，您可以使用 `uvx desktop-agent` 命令行界面 (CLI) 调用桌面自动化命令。

### 命令结构

所有命令都遵循以下模式：

```bash
uvx desktop-agent <类别> <命令> [参数] [选项]
```

**类别：**
- `mouse` - 鼠标控制
- `keyboard` - 键盘输入
- `screen` - 屏幕截图和屏幕分析
- `message` - 用户对话框
- `app` - 应用程序控制（打开、聚焦、列出窗口）

## 可用命令

### 🖱️ 鼠标控制 (`mouse`)

控制光标移动和点击。

```bash
# 移动光标到坐标
uvx desktop-agent mouse move <x> <y> [--duration SECONDS]

# 在当前位置或特定坐标点击
uvx desktop-agent mouse click [x] [y] [--button left|right|middle] [--clicks N]

# 特殊点击
uvx desktop-agent mouse double-click [x] [y]
uvx desktop-agent mouse right-click [x] [y]
uvx desktop-agent mouse middle-click [x] [y]

# 拖动到坐标
uvx desktop-agent mouse drag <x> <y> [--duration SECONDS] [--button BUTTON]

# 滚动（正数=向上，负数=向下）
uvx desktop-agent mouse scroll <点击次数> [x] [y]

# 获取当前鼠标位置
uvx desktop-agent mouse position
```

**示例：**
```bash
# 移动到 1920x1080 屏幕的中心
uvx desktop-agent mouse move 960 540 --duration 0.5

# 在特定位置右键点击
uvx desktop-agent mouse right-click 500 300

# 向下滚动 5 次点击
uvx desktop-agent mouse scroll -5
```

### ⌨️ 键盘控制 (`keyboard`)

输入文本并执行键盘快捷键。

```bash
# 输入文本
uvx desktop-agent keyboard write "<text>" [--interval SECONDS]

# 按键
uvx desktop-agent keyboard press <key> [--presses N] [--interval SECONDS]

# 执行热键组合（逗号分隔）
uvx desktop-agent keyboard hotkey "<key1>,<key2>,..."

# 按住/释放键
uvx desktop-agent keyboard keydown <key>
uvx desktop-agent keyboard keyup <key>
```

**示例：**
```bash
# 带自然延迟输入文本
uvx desktop-agent keyboard write "Hello World" --interval 0.05

# 复制选定文本
uvx desktop-agent keyboard hotkey "ctrl,c"

# 打开任务管理器
uvx desktop-agent keyboard hotkey "ctrl,shift,esc"

# 按 Enter 3 次
uvx desktop-agent keyboard press enter --presses 3
```

**常见键名：**
- 修饰键：`ctrl`、`shift`、`alt`、`win`
- 特殊键：`enter`、`tab`、`esc`、`space`、`backspace`、`delete`
- 功能键：`f1` 到 `f12`
- 方向键：`up`、`down`、`left`、`right`

### 🖼️ 屏幕 & 屏幕截图 (`screen`)

捕获屏幕截图并分析屏幕内容。支持针对特定窗口。

```bash
# 拍摄屏幕截图
uvx desktop-agent screen screenshot <filename> [--region "x,y,width,height"] [--window <title>] [--active]

# 在屏幕或窗口中定位图像
uvx desktop-agent screen locate <image_path> [--confidence 0.0-1.0] [--window <title>] [--active]
uvx desktop-agent screen locate-center <image_path> [--confidence 0.0-1.0] [--window <title>] [--active]

# 使用 OCR 在窗口中定位文本
uvx desktop-agent screen locate-text-coordinates <text> [--window <title>] [--active]
uvx desktop-agent screen read-all-text [--window <title>] [--active]

# 实用命令
uvx desktop-agent screen pixel <x> <y>
uvx desktop-agent screen size
uvx desktop-agent screen on-screen <x> <y>
```

**示例：**
```bash
# 活动窗口的屏幕截图
uvx desktop-agent screen screenshot active.png --active

# 特定应用程序的屏幕截图
uvx desktop-agent screen screenshot chrome.png --window "Google Chrome"

# 在记事本中定位图像
uvx desktop-agent screen locate-center button.png --window "Notepad"
```

### 💬 消息对话框 (`message`)

显示用户交互对话框。

```bash
# 显示警告
uvx desktop-agent message alert "<text>" [--title TITLE] [--button BUTTON]

# 显示确认对话框
uvx desktop-agent message confirm "<text>" [--title TITLE] [--buttons "OK,Cancel"]

# 提示输入
uvx desktop-agent message prompt "<text>" [--title TITLE] [--default TEXT]

# 密码输入
uvx desktop-agent message password "<text>" [--title TITLE] [--mask CHAR]
```

**示例：**
```bash
# 简单警告
uvx desktop-agent message alert "任务完成！"

# 获取用户确认
uvx desktop-agent message confirm "继续操作？"

# 询问用户输入
uvx desktop-agent message prompt "请输入您的姓名："
```

### 📱 应用程序控制 (`app`)

跨 Windows、macOS 和 Linux 控制应用程序。

```bash
# 通过名称打开应用程序
uvx desktop-agent app open <name> [--arg ARGS...]

# 聚焦于标题/名称的窗口
uvx desktop-agent app focus <name>

# 列出所有可见窗口
uvx desktop-agent app list
```

**示例：**
```bash
# Windows：打开记事本
uvx desktop-agent app open notepad

# Windows：打开 Chrome 并带 URL
uvx desktop-agent app open "chrome" --arg "https://google.com"

# macOS：打开 Safari
uvx desktop-agent app open "Safari"

# 聚焦于特定窗口
uvx desktop-agent app focus "Untitled - Notepad"

# 列出所有打开的窗口
uvx desktop-agent app list
```

## 常见自动化工作流

### 工作流 1：打开应用程序并输入

```bash
# 直接打开记事本（跨平台）
uvx desktop-agent app open notepad

# 等待应用程序打开，然后聚焦它
uvx desktop-agent app focus notepad

# 输入一些文本
uvx desktop-agent keyboard write "来自桌面技能的问候！"
```

### 工作流 2：截图 + 分析

```bash
# 获取屏幕尺寸
uvx desktop-agent screen size

# 拍摄完整截图
uvx desktop-agent screen screenshot current_screen.png

# 检查特定 UI 元素是否可见
uvx desktop-agent screen locate save_button.png
```

### 工作流 3：表单填写

```bash
# 点击第一个字段
uvx desktop-agent mouse click 300 200

# 填写字段
uvx desktop-agent keyboard write "John Doe"

# Tab 到下一个字段
uvx desktop-agent keyboard press tab

# 填写第二个字段
uvx desktop-agent keyboard write "john@example.com"

# 提交表单（Enter）
uvx desktop-agent keyboard press enter
```

### 工作流 4：复制/粘贴操作

```bash
# 全选文本
uvx desktop-agent keyboard hotkey "ctrl,a"

# 复制
uvx desktop-agent keyboard hotkey "ctrl,c"

# 点击目标位置
uvx desktop-agent mouse click 500 600

# 粘贴
uvx desktop-agent keyboard hotkey "ctrl,v"
```

## 安全注意事项

在使用此技能时，AI 代理应：

1. **验证坐标**：在使用 `click` 命令前使用 `screen size` 和 `on-screen`
2. **添加延迟**：在命令之间插入适当的延迟以适应 UI 响应
3. **验证图像**：在使用 `locate` 命令前确保图像文件存在
4. **处理失败**：如果窗口更改或元素移动，命令可能会失败
5. **用户安全**：始终通过 `message confirm` 与用户确认破坏性操作

## 故障排除

### PyAutoGUI 安全机制
PyAutoGUI 具有安全机制：将鼠标移动到屏幕角落会中止操作。这是一个安全特性。

### 图像未找到
在使用 `screen locate` 时，请确保：
- 图像文件存在且路径正确
- 调整 `--confidence`（尝试 0.7-0.9）
- 图像与屏幕外观完全匹配（分辨率、颜色）

## 获取帮助

```bash
# 显示所有可用命令
uvx desktop-agent --help

# 显示特定类别的命令
uvx desktop-agent mouse --help
uvx desktop-agent keyboard --help
uvx desktop-agent screen --help
uvx desktop-agent message --help

# 显示特定命令的帮助
uvx desktop-agent mouse move --help
```

## AI 代理集成技巧

1. **在处理绝对坐标时始终检查屏幕尺寸**
2. **尽可能使用相对定位**（例如，获取当前位置，计算偏移量）
3. **组合命令以用于复杂的工作流**
4. **执行前验证**（例如，检查屏幕上是否存在图像）
5. **使用消息对话框为重要操作提供用户反馈**
6. **优雅地处理错误** - 如果 UI 状态更改，命令可能会失败

## 性能注意事项

- 使用 `--duration` 的鼠标移动是动画的，需要时间
- 图像定位 (`locate`) 在大屏幕上可能较慢 - 尽可能使用区域
- 键盘命令通常很快（< 100ms）
- 屏幕截图取决于屏幕分辨率和区域大小

## 输出格式

所有命令默认输出结构化 JSON，非常适合 AI 代理程序化使用：

```bash
uvx desktop-agent mouse position
# 输出: {"success": true, "command": "mouse.position", "timestamp": "2026-01-31T10:00:00Z", "duration_ms": 5, "data": {"position": {"x": 960, "y": 540}}}
```

### 响应模式

所有 JSON 响应都遵循此模式：

```json
{
  "success": true,
  "command": "category.command",
  "timestamp": "2026-01-31T10:00:00Z",
  "duration_ms": 150,
  "data": { ... },
  "error": null
}
```

### 错误响应模式

```json
{
  "success": false,
  "command": "category.command",
  "timestamp": "2026-01-31T10:00:00Z",
  "duration_ms": 50,
  "data": null,
  "error": {
    "code": "image_not_found",
    "message": "图像文件 'button.png' 未找到",
    "details": {},
    "recoverable": true
  }
}
```

### 错误代码

| 代码 | 描述 |
|------|------|
| `success` | 命令成功 |
| `invalid_argument` | 无效的命令参数 |
| `coordinates_out_of_bounds` | 坐标超出屏幕范围 |
| `image_not_found` | 图像文件未找到或不在屏幕上 |
| `window_not_found` | 未找到目标窗口 |
| `ocr_failed` | OCR 操作失败 |
| `application_not_found` | 未找到应用程序 |
| `permission_denied` | 权限被拒绝 |
| `platform_not_supported` | 平台不受支持 |
| `timeout` | 操作超时 |
| `unknown_error` | 未知错误 |

**鼠标移动:**
```bash
uvx desktop-agent mouse move 960 540
```
```json
{"success": true, "command": "mouse.move", "timestamp": "...", "duration_ms": 150, "data": {"x": 960, "y": 540, "duration": 0}, "error": null}
```

**屏幕尺寸:**
```bash
uvx desktop-agent screen size
```
```json
{"success": true, "command": "screen.size", "timestamp": "...", "duration_ms": 5, "data": {"size": {"width": 1920, "height": 1080}}, "error": null}
```

**定位图像:**
```bash
uvx desktop-agent screen locate button.png
```
```json
{"success": true, "command": "screen.locate", "timestamp": "...", "duration_ms": 250, "data": {"image_found": true, "bounding_box": {"left": 100, "top": 200, "width": 50, "height": 30, "center_x": 125, "center_y": 215}}, "error": null}
```

**列出窗口:**
```bash
uvx desktop-agent app list
```
```json
{"success": true, "command": "app.list", "timestamp": "...", "duration_ms": 100, "data": {"windows": ["Untitled - Notepad", "Google Chrome", "Visual Studio Code"]}, "error": null}
```

**错误示例:**
```bash
uvx desktop-agent screen locate missing.png
```
```json
{"success": false, "command": "screen.locate", "timestamp": "...", "duration_ms": 50, "data": null, "error": {"code": "image_not_found", "message": "图像文件 'missing.png' 未找到", "details": {}, "recoverable": true}}
```

## AI 代理有效使用指南

本节教 AI 代理如何使用此技能，包括最佳命令序列和最佳实践。

### 🎯 核心策略：先观察，再行动

**始终** 了解当前状态后再执行操作。这可以避免点击错误的坐标或在错误的窗口中输入。

**推荐初始序列：**
```bash
# 1. 获取屏幕尺寸以了解您的工作空间
uvx desktop-agent screen size
uvx desktop-agent app list
uvx desktop-agent mouse position
```

### 📋 按任务推荐的命令序列

#### 打开并交互应用程序

```bash
# ✅ 正确：打开、等待、验证，然后交互
uvx desktop-agent app open notepad              # 第 1 步：打开应用程序
uvx desktop-agent app list
uvx desktop-agent app focus "Notepad"
uvx desktop-agent keyboard write "Hello World"  # 第 4 步：现在可以安全地输入

# ❌ 错误：立即输入而不进行验证
uvx desktop-agent app open notepad
uvx desktop-agent keyboard write "Hello World"  # 可能会输入到错误的窗口！
```

#### 定位并点击 UI 元素（基于图像）

```bash
# ✅ 正确：定位后点击（如果找到）
uvx desktop-agent screen locate-center button.png --confidence 0.8
# 检查：如果 success=true 且坐标有效
uvx desktop-agent mouse click 125 215  # 使用返回的坐标

# ❌ 错误：不验证元素是否存在就点击
uvx desktop-agent mouse click 125 215  # 可能点击错误区域！
```

#### 定位并点击 UI 元素（基于文本 OCR）

```bash
# ✅ 正确：读取屏幕文本，然后定位特定文本
uvx desktop-agent screen read-all-text --active
uvx desktop-agent screen locate-text-coordinates "Save" --active
# 使用返回的坐标点击

# 对于特定窗口的 OCR：
uvx desktop-agent screen locate-text-coordinates "OK" --window "对话框标题"
```

#### 填写多个字段的表单

```bash
# ✅ 正确：明确点击每个字段后再输入
uvx desktop-agent mouse click 300 200           # 点击第一个字段
uvx desktop-agent keyboard write "John Doe"
uvx desktop-agent mouse click 300 250           # 点击第二个字段（更可靠）
uvx desktop-agent keyboard write "john@example.com"
uvx desktop-agent mouse click 300 300           # 点击第三个字段
uvx desktop-agent keyboard write "555-1234"

# OR 使用 Tab 导航（如果字段顺序可能变化）
uvx desktop-agent mouse click 300 200
uvx desktop-agent keyboard write "John Doe"
uvx desktop-agent keyboard press tab
uvx desktop-agent keyboard write "john@example.com"
uvx desktop-agent keyboard press tab
uvx desktop-agent keyboard write "555-1234"
uvx desktop-agent keyboard press enter          # 提交
```

#### 定向截图以进行分析

```bash
# ✅ 正确：截图特定窗口以加快处理速度
uvx desktop-agent app list --json                           # 找到确切的窗口标题
uvx desktop-agent screen screenshot app.png --window "Google Chrome"

# 仅在必要时使用活动窗口截图（较慢，文件较大）
uvx desktop-agent screen screenshot active.png --active

# 仅当必要时使用全屏截图（较慢，文件较大）
uvx desktop-agent screen size
uvx desktop-agent screen screenshot full.png
```

#### 安全拖放

```bash
# ✅ 正确：移动到起始位置，验证位置，然后拖动
uvx desktop-agent mouse move 100 200                 # 移动到源
uvx desktop-agent mouse position              # 验证位置
uvx desktop-agent mouse drag 500 400 --duration 0.5  # 拖动到目标位置

# 为了精确，使用较慢的持续时间
uvx desktop-agent mouse drag 500 400 --duration 1.0
```

### 🔄 错误恢复模式

#### 窗口未找到

```bash
# 模式：列出窗口，找到最接近的匹配项，重试
uvx desktop-agent app focus "Chrome"             # 失败，显示 window_not_found
uvx desktop-agent app list                # 查看实际窗口标题
# 输出显示： "Google Chrome - My Page"
uvx desktop-agent app focus "Google Chrome"      # 使用正确的标题
```

#### 图像未找到

```bash
# 模式：调整置信度或重新捕获当前状态
uvx desktop-agent screen locate button.png --confidence 0.9
uvx desktop-agent screen locate button.png --confidence 0.7
# 如果仍然失败，捕获当前状态以进行分析
uvx desktop-agent screen screenshot current.png --active
```

#### 点击似乎未命中

```bash
# 模式：验证坐标是否在屏幕上
uvx desktop-agent screen size             # 获取屏幕边界
uvx desktop-agent screen on-screen 1500 900      # 检查坐标是否有效
uvx desktop-agent mouse move 1500 900            # 移动到当前位置以可视化
uvx desktop-agent mouse click                    # 然后点击当前位置
```

### ⚡ 性能优化

#### 最小化截图

```bash
# ✅ 好：仅截图您需要的区域
uvx desktop-agent screen screenshot button_area.png --region "100,200,200,100"

# ✅ 好：截图特定窗口而不是全屏  
uvx desktop-agent screen screenshot chrome.png --window "Google Chrome"

# ❌ 慢：当您只需要一个小区域时进行全屏捕获
uvx desktop-agent screen screenshot full.png
```

#### 批量键盘输入

```bash
# ✅ 更快：一次性写入整个文本
uvx desktop-agent keyboard write "这是一个完整的句子，包含所有文本。"

# ❌ 更慢：多个 write 命令
uvx desktop-agent keyboard write "这是 "
uvx desktop-agent keyboard write "一个完整的 "
uvx desktop-agent keyboard write "句子。"
```

#### 尽可能使用热键而不是鼠标

```bash
# ✅ 更快：使用键盘快捷键
uvx desktop-agent keyboard hotkey "ctrl,s"       # 保存
uvx desktop-agent keyboard hotkey "ctrl,a"       # 全选
uvx desktop-agent keyboard hotkey "ctrl,shift,s" # 另存为

# ❌ 更慢：使用鼠标导航菜单
uvx desktop-agent mouse click 50 30              # 点击文件菜单
uvx desktop-agent mouse click 60 80              # 点击保存选项
```

### 🛡️ 防御性编程模式

#### 始终验证关键操作

```bash
# 在执行破坏性操作前，始终通过用户确认
uvx desktop-agent message confirm "这将删除所有文件。继续？" --title "警告"
# 检查输出：如果用户点击了 "Cancel"，则中止操作
```

#### 使用 JSON 模式以进行可靠解析

```bash
# ✅ 可靠：解析结构化 JSON 输出
uvx desktop-agent screen locate button.png
# 解析：{"success": true, "data": {"center_x": 125, "center_y": 215}}

# ❌ 不稳定：解析文本输出
uvx desktop-agent screen locate button.png
# 解析： "Found at: Box(left=100, top=200, width=50, height=30)"
```

#### 执行前验证（例如，对于多步操作）

```bash
# 多步文件操作验证
uvx desktop-agent app list
uvx desktop-agent screen locate-text-coordinates "文件" --active
uvx desktop-agent mouse click <返回的_x> <返回的_y>
uvx desktop-agent screen locate-text-coordinates "另存为" --active
uvx desktop-agent mouse click <返回的_x> <返回的_y>
```

### 🎮 平台特定注意事项

#### Windows

```bash
# 常见 Windows 快捷键
uvx desktop-agent keyboard hotkey "win,d"        # 显示桌面
uvx desktop-agent keyboard hotkey "win,e"        # 打开资源管理器
uvx desktop-agent keyboard hotkey "alt,tab"      # 切换窗口
uvx desktop-agent keyboard hotkey "win,r"        # 运行对话框

# 通过名称打开应用程序
uvx desktop-agent app open notepad
uvx desktop-agent app open calc
uvx desktop-agent app open mspaint
```

#### macOS

```bash
# 常见 macOS 快捷键（Cmd 键使用 'command'）
uvx desktop-agent keyboard hotkey "command,space"   # Spotlight
uvx desktop-agent keyboard hotkey "command,tab"     # 应用程序切换器
uvx desktop-agent keyboard hotkey "command,q"       # 退出应用程序
uvx desktop-agent keyboard hotkey "command,shift,3" # 屏幕截图

# 打开应用程序
uvx desktop-agent app open "Safari"
uvx desktop-agent app open "TextEdit"
```

#### Linux

```bash
# 打开应用程序（使用 xdg-open 或直接命令）
uvx desktop-agent app open firefox
uvx desktop-agent app open gedit

# 常见快捷键可能因桌面环境而异
uvx desktop-agent keyboard hotkey "alt,f2"       # 运行对话框（许多桌面环境）
```

### 📊 选择正确命令的决策树

```
想要与应用程序交互？
├── 应用程序未运行 → `app open <name>`
├── 应用程序运行但未聚焦 → `app focus <name>` 
└── 需要验证窗口 → `app list`

想要找到 UI 元素？
├── 有参考图像 → `screen locate-center <image>`
├── 知道文本标签 → `screen locate-text-coordinates "<text>"`
└── 需要查看所有文本 → `screen read-all-text --active`

想要点击某物？
├── 知道精确坐标 → `mouse click <x> <y>`
├── 需要找到第一个 → 使用 locate 命令，然后点击返回的坐标
└── 不确定是否在屏幕上 → `screen on-screen <x> <y>` 首先检查

想要输入某物？
├── 普通文本 → `keyboard write "<text>"`
├── 键盘快捷键 → `keyboard hotkey "<key1>,<key2>"`
├── 单键按下 → `keyboard press <key>`
└── 多次按下相同键 → `keyboard press <key> --presses N`
```

## AI 代理集成技巧

1. **在处理绝对坐标时始终检查屏幕尺寸**
2. **尽可能使用相对定位**（例如，获取当前位置，计算偏移量）
3. **组合命令**以用于复杂的工作流
4. **执行前验证**（例如，检查屏幕上是否存在图像）
5. **使用消息对话框为重要操作提供用户反馈**
6. **优雅地处理错误** - 如果 UI 状态更改，命令可能会失败
