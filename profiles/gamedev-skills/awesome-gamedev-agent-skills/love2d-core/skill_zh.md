# LÖVE (Love2D) 核心

在 Lua 中设置和调试 LÖVE 游戏的基础：回调循环、帧率无关的运动、输入和屏幕状态。目标版本为 **LÖVE 11.5**。

## 何时使用

- 在开始 LÖVE 游戏时使用，用于连接 `main.lua`/`conf.lua`，或修复核心循环、运行速度不正确的移动、输入处理或屏幕切换问题。
- 当工作区包含调用 `love.*` 的 `main.lua`、`conf.lua` 或 `.love` 文件时使用。

**不建议使用的情况：** 与 LÖVE 无关的 Lua 语言问题；物理体/关节（LÖVE 通过 `love.physics` 使用 Box2D — 这是独立的问题）；着色器代码（`love.graphics` GLSL 是其自身主题）。对于跨引擎的保存/加载模式，请使用 `save-systems`。

## 核心工作流程

1. **确认入口点。** LÖVE 游戏运行 `main.lua`；它应定义 `love.load()`（一次性设置）、`love.update(dt)`（状态）和 `love.draw()`（渲染）。窗口/版本设置放在 `conf.lua` 中（在模块加载之前运行）。
2. **固定版本。** 在 `conf.lua` 中设置 `t.version = "11.5"`，以便 LÖVE 在不匹配时发出警告。
3. **通过 `dt`（delta time，秒为单位）驱动所有运动**，这样速度与帧率无关。
4. **以两种方式处理输入：** 轮询（在 `update` 中使用 `love.keyboard.isDown`，用于按住键）和事件（`love.keypressed` 回调，用于离散按键）。
5. **使用小型状态栈管理屏幕**（菜单、游戏、暂停），而不是一堆 `if` 标志 — 请参阅模式和 `references/state-stack.md`。
6. **运行并观察。** 从项目文件夹中用 `love .` 启动；在假设它工作之前，验证窗口、运动速度和屏幕上的输入。

## 模式

### 1. `main.lua` 骨架（回调循环 + 输入）

```lua
-- main.lua — LÖVE 会为你调用这些回调。颜色在 LÖVE 11.x 中为 0–1。
function love.load()
    -- 一次性设置。速度以每秒像素为单位，而不是每帧。
    player = { x = 100, y = 100, size = 40, speed = 220 }
    love.graphics.setBackgroundColor(0.1, 0.1, 0.12)
end

function love.update(dt)
    -- 轮询输入：适用于按住键时进行连续移动。
    if love.keyboard.isDown("right") then player.x = player.x + player.speed * dt end
    if love.keyboard.isDown("left")  then player.x = player.x - player.speed * dt end
    if love.keyboard.isDown("down")  then player.y = player.y + player.speed * dt end
    if love.keyboard.isDown("up")    then player.y = player.y - player.speed * dt end
end

function love.draw()
    love.graphics.setColor(0.2, 0.8, 1.0)                 -- 开启色调
    love.graphics.rectangle("fill", player.x, player.y, player.size, player.size)
    love.graphics.setColor(1, 1, 1)                       -- 在绘制文本/图像之前重置色调
    love.graphics.print("使用方向键移动，按 Esc 退出", 10, 10)
end

function love.keypressed(key)
    -- 事件输入：每次物理按键触发一次。用于菜单、跳跃、切换。
    if key == "escape" then love.event.quit() end
end
```

### 2. 帧率独立性（最常见的错误）

```lua
-- 正确：通过 dt 缩放 → 在 30 或 240 FPS 下具有相同的实际速度。
player.x = player.x + player.speed * dt
-- 错误："每帧像素" → 在帧率翻倍时移动速度也翻倍。
player.x = player.x + player.speed
```

### 3. `conf.lua`（窗口 + 版本；在 `main.lua` 之前运行）

```lua
-- conf.lua — 必须是单独的文件；love.conf 不会从 main.lua 运行。
function love.conf(t)
    t.version = "11.5"             -- 此游戏目标 LÖVE 版本（字符串 "X.Y"）
    t.window.title  = "我的 LÖVE 游戏"
    t.window.width  = 800
    t.window.height = 600
    t.window.vsync  = 1            -- 自 11.0 起的数字：1 = 开启，0 = 关闭，-1 = 自适应
    t.window.resizable = false
    t.modules.physics = false      -- 禁用不使用的模块以减少启动/内存占用
end
```

### 4. LÖVE 11.x 中颜色为 0–1（不是 0–255）

```lua
-- LÖVE 11.x 使用归一化浮点数。（11.0 之前的代码使用 0–255，看起来会不正确。）
love.graphics.setColor(1, 0, 0)                          -- 不透明红色
love.graphics.setColor(0.2, 0.8, 1.0, 0.5)               -- 半透明青色（alpha 0.5）
-- 需要转换旧的字节值？使用辅助函数而不是手动除法：
love.graphics.setColor(love.math.colorFromBytes(128, 234, 255))
```

### 5. 屏幕状态（简要 — 完整管理器在 references）

```lua
-- 屏幕是一个包含可选的 :update(dt), :draw(), :keypressed(key) 的表。
-- 将活动屏幕放在栈上，以便暂停/菜单覆盖层可以轻松弹出。
local Stack = require("state_stack")   -- 请参阅 references/state-stack.md 获取模块
function love.load()              Stack.push(require("screens.menu")) end
function love.update(dt)          Stack.current():update(dt) end
function love.draw()              Stack.current():draw() end
function love.keypressed(key)     Stack.current():keypressed(key) end
```

## 陷阱

- **速度随 FPS 变化** → 你忘了 `* dt`。位置、计时器或动画的每帧更改必须按 `dt` 缩放。
- **`love.conf` 放在 `main.lua` 中** → 它默默无闻。它必须存在于 `conf.lua` 中，LÖVE 在加载模块之前运行它。
- **颜色褪色或不可见** → 你使用了 0–255 值。在 11.x 中，`setColor(255,0,0)` 会被裁剪为白色；使用 `setColor(1,0,0)` 或 `love.math.colorFromBytes`。
- **绘制后所有内容都带色调** → 颜色是全局的，并且在绘制之间持续存在。在绘制你希望无色调的文本/图像之前，用 `love.graphics.setColor(1, 1, 1)` 重置。
- **按键释放/重复时无反应** → `love.keypressed(key, scancode, isrepeat)` 在按下时触发（以及操作系统按键重复）；使用 `love.keyreleased` 处理释放，如果必须忽略按住键的重复，请检查 `isrepeat`。

## 参考

- 对于一个完整的推/弹出屏幕状态管理器（菜单 → 游戏 → 暂停，带有委托的回调），请阅读 `references/state-stack.md`。

## 相关技能

- `save-systems` — 保存/加载游戏状态（与引擎无关）。
- `input-systems` — 可重新绑定、多设备输入架构。
- `pygame-core` / `phaser-core` — 其他轻量级引擎中的相同循环概念。
