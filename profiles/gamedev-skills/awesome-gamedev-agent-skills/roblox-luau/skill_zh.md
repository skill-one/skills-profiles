# Roblox Luau 脚本编写

使用 **Luau** 脚本编写 Roblox 体验：服务、`Instance` 对象、事件、服务器/客户端分离以及安全的跨边界通信。适用于当前 Roblox 引擎和 Studio。

## 使用场景

- 编写 Roblox 脚本时使用：获取服务、创建/父级实例、连接事件、决定服务器与客户端、配置 `RemoteEvent`/`RemoteFunction` 通信。
- 项目包含 `Script`/`LocalScript`/`ModuleScript` 对象、`.rbxl(x)` 场景文件或 Rojo `*.project.json`，且代码调用 `game:GetService(...)` 时使用。

**不建议使用的情况：**
- 跨会话持久化数据 → `roblox-datastores`。
- 远程协议架构、漏洞硬化、速率限制、高频复制、多客户端滥用测试 → `roblox-networking`。
- 与 Roblox API 无关的通用 Lua 问题。引擎无关的输入/保存架构 → `input-systems` / `save-systems`。

## 核心工作流程

1. **使用 `game:GetService("Name")` 获取服务。** 常见服务：`Players`、`Workspace`、`ReplicatedStorage`（共享客户端+服务器）、`ServerScriptService`（仅服务器代码）、`ServerStorage`、`RunService`、`UserInputService`（客户端）。
2. **了解代码运行位置。** `Script` 在 **服务器** 上运行；`LocalScript` 在 **客户端** 运行（在 `StarterPlayerScripts`、`StarterGui` 或玩家角色中）。`ModuleScript` 是你通过 `require` 调用的共享代码。
3. **有意创建实例。** `local p = Instance.new("Part")`，设置其属性，然后 **最后** 设置 `p.Parent`（父级化会触发复制）。
4. **通过事件进行响应。** `:Connect` 到信号如 `Players.PlayerAdded`、`part.Touched` 或 `RunService.Heartbeat`。完成时断开连接以避免内存泄漏。
5. **使用 Remotes 跨越客户端/服务器边界 — 且永远不要信任客户端。** 客户端通过 `RemoteEvent:FireServer(...)` 请求；服务器验证并应用。服务器对所有游戏状态具有权威性。
6. **在 Studio 中测试** 使用 Play / Play Here / 服务器+客户端 Start；使用输出窗口和服务器/客户端视图切换来确认代码运行位置。

## 模式

### 1. 服务器脚本：响应玩家加入（领导统计）

```lua
-- ServerScriptService/Leaderboard.server.luau  (一个 Script = 在服务器上运行)
local Players = game:GetService("Players")

local function onPlayerAdded(player: Player)
    local stats = Instance.new("Folder")
    stats.Name = "leaderstats"          -- 此名称使其显示在排行榜上

    local coins = Instance.new("IntValue")
    coins.Name = "Coins"
    coins.Value = 0
    coins.Parent = stats

    stats.Parent = player               -- 最后父级化
end

Players.PlayerAdded:Connect(onPlayerAdded)
```

### 2. 创建和配置实例

```lua
local Workspace = game:GetService("Workspace")

local part = Instance.new("Part")
part.Size = Vector3.new(4, 1, 4)
part.Position = Vector3.new(0, 10, 0)
part.Anchored = true                    -- 不会在重力下掉落
part.BrickColor = BrickColor.new("Bright blue")
part.Parent = Workspace                 -- 最后设置父级化，使其复制一次，完全状态
```

### 3. 连接事件（并断开连接以避免内存泄漏）

```lua
local debounce = false
local connection
connection = part.Touched:Connect(function(hit: BasePart)
    local character = hit.Parent
    local humanoid = character and character:FindFirstChildOfClass("Humanoid")
    if not humanoid or debounce then return end
    debounce = true
    humanoid.Health -= 10
    task.wait(1)                        -- 使用 task.wait，不是已弃用的 wait()
    debounce = false
end)

-- 之后，当实例被移除或回合结束时：
-- connection:Disconnect()
```

### 4. 客户端 → 服务器使用 RemoteEvent（服务器端验证！）

```lua
-- ReplicatedStorage: 创建一个名为 "BuyItem" 的 RemoteEvent（在 Studio 或通过代码创建）。
-- 客户端（LocalScript）：请求购买。客户端可以撒谎 — 这只是一个请求。
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local buyItem = ReplicatedStorage:WaitForChild("BuyItem")  -- 等待：可能尚未复制
buyButton.MouseButton1Click:Connect(function()
    buyItem:FireServer("sword")        -- 仅发送物品 ID；绝不发送价格/结果
end)
```

```lua
-- 服务器（Script）：交易仅在服务器端决定。
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local buyItem = ReplicatedStorage:WaitForChild("BuyItem")
local PRICES = { sword = 100, shield = 75 }

buyItem.OnServerEvent:Connect(function(player: Player, itemId)
    -- 从客户端信任任何内容。验证类型和值。
    if type(itemId) ~= "string" then return end
    local price = PRICES[itemId]
    if not price then return end                         -- 未知物品
    local coins = player.leaderstats.Coins
    if coins.Value < price then return end               -- 买不起
    coins.Value -= price                                 -- 服务器应用变更
    grantItem(player, itemId)
end)
```

### 5. 使用 RunService 的每帧循环

```lua
local RunService = game:GetService("RunService")
-- Heartbeat 每帧触发一次，在物理之后；dt 是自上次步骤以来的秒数。
RunService.Heartbeat:Connect(function(dt)
    spinner.CFrame *= CFrame.Angles(0, math.rad(90) * dt, 0)  -- 每秒 90 度，帧无关
end)
```

### 6. ModuleScript 中的共享代码

```lua
-- ReplicatedStorage/GameConfig (一个 ModuleScript) — 服务器和客户端可用。
local GameConfig = {}
GameConfig.MaxHealth = 100
function GameConfig.damageFor(weapon: string): number
    return ({ sword = 25, bow = 15 })[weapon] or 0
end
return GameConfig
```

```lua
local GameConfig = require(game:GetService("ReplicatedStorage"):WaitForChild("GameConfig"))
print(GameConfig.MaxHealth)
```

## 陷阱

- **信任客户端是一个漏洞** → 客户端可以向 `RemoteEvent`/`RemoteFunction` 发送任何参数。在服务器上验证每个参数的类型和范围，并保持服务器对生命值、货币和物品栏的权威性。
- **`LocalScript` 不在放置位置运行** → LocalScripts 在 `StarterPlayerScripts`、`StarterCharacterScripts`、`StarterGui` 或工具中运行 — 不在 `Workspace` 或 `ServerScriptService` 中。服务器 `Script` 属于 `ServerScriptService`/`Workspace`。
- **已弃用的全局变量** → 使用 `task.wait`/`task.spawn`/`task.delay`，而不是旧的 `wait()`/`spawn()`/`delay()`（调度和速率限制更差）。
- **先父级化，再设置属性** → 先设置属性，最后父级化，以便实例以最终状态复制一次。
- **加入后客户端立即为 `nil`** → 对象随时间流式传输/复制；使用 `parent:WaitForChild("Name")` 而不是直接在客户端索引。
- **连接从未断开** → 长生命周期的 `:Connect` 处理器会泄漏，并且可以在已销毁的对象上触发；存储连接并 `:Disconnect()`（或在适当情况下使用 `Instance:GetAttributeChangedSignal`/`:Once`）。
- **在适合 RemoteEvent 的地方使用 RemoteFunction** → `RemoteFunction` 会阻塞等待返回，恶意/慢速客户端可能会使服务器停滞；优先使用单向 `RemoteEvent`，除非你确实需要回复。

## 参考

- 关于完整的客户端/服务器模型（复制、`RemoteFunction` vs `RemoteEvent`、`:WaitForChild` 时间、`BindableEvent` 用于同上下文消息、属性、`CollectionService` 标签以及 `:Once`/连接清理），请阅读 `references/client-server.md`。

## 相关技能

- `roblox-datastores` — 跨会话持久化玩家数据（仅服务器）。
- `roblox-networking` — 生产远程合约、服务器验证、速率限制、复制、流式传输、预测和多客户端测试。
- `save-systems` — 引擎无关的持久化概念。
- `game-ai` / `input-systems` — 可移植 AI 和输入模式，用于在 Luau 中实现。
