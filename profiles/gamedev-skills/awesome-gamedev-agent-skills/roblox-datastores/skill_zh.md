# Roblox 数据存储

使用 `DataStoreService` 在 Roblox 中持久化数据：加入时加载，离开时保存和关闭时保存，安全更新、重试和有序存储用于排行榜。仅限服务器端使用。

## 使用场景

- 用于保存/加载玩家进度（金币、背包、等级），构建持久化排行榜或修复数据丢失、覆盖和节流问题。
- 当服务器代码调用 `DataStoreService`、`GetDataStore`、`GetAsync`、`SetAsync`、`UpdateAsync` 或 `GetOrderedDataStore` 时使用。

**不使用场景**：通用脚本、服务、远程、客户端/服务器分割 → `roblox-luau`。高频临时状态（匹配、每轮）→ 内存存储（不同的服务）。引擎无关持久化理论 → `save-systems`。

## 核心工作流程

1. **一次性启用 Studio 访问**。文件 → 游戏设置 → 安全 → *启用 Studio 访问 API 服务*（使用测试场景；Studio 访问实时数据）。数据存储仅从服务器 `Script` 中工作，从未从 `LocalScript` 中工作。
2. **获取存储，然后按键读取/写入**。`DataStoreService:GetDataStore("Name")`；每个玩家的键通常是 `"Player_" .. player.UserId`。
3. **将每个调用包装在 `pcall` 中**。`GetAsync`/`SetAsync`/`UpdateAsync` 是可能失败的网络调用；无保护的失败会错误线程并可能导致数据丢失。
4. **在 `PlayerAdded` 时加载，在 `PlayerRemoving` 时保存，并绑定到 `Close`**。离开的玩家和关闭的服务器都需要最终保存。
5. **优先使用 `UpdateAsync` 进行读-改-写**（多服务器安全）而不是 `SetAsync`（盲目覆盖）。在加载失败时，**不要**用默认值覆盖 — 取消保存，以免擦除有效数据。
6. **使用 `OrderedDataStore` 用于排名数据**（排行榜）通过 `GetSortedAsync`。通过加入、更改数据、重新加入并确认其持久化来测试。

## 模式

### 1. 加入时加载（pcall保护）

```lua
local DataStoreService = game:GetService("DataStoreService")
local Players = game:GetService("Players")
local store = DataStoreService:GetDataStore("PlayerData")

local DEFAULT = { Coins = 0, Level = 1 }

Players.PlayerAdded:Connect(function(player)
    local key = "Player_" .. player.UserId
    local ok, data = pcall(function()
        return store:GetAsync(key)
    end)

    if not ok then
        -- 加载失败（网络）。不要将其视为新玩家；标记以便我们永远不会用默认值覆盖他们的真实数据。
        warn("Load failed for", player.Name, data)
        player:SetAttribute("DataLoaded", false)
        return
    end

    player:SetAttribute("DataLoaded", true)
    local profile = data or DEFAULT          -- nil == 真正的新玩家
    applyToLeaderstats(player, profile)
end)
```

### 2. 使用 UpdateAsync 保存（多服务器安全）

```lua
-- UpdateAsync 读取最新值，然后写入回调返回的内容。
-- 回调**必须**不产生（没有 `task.wait`，没有在其内部进行进一步的 Async 调用）。
local function savePlayer(player)
    if player:GetAttribute("DataLoaded") == false then return end  -- 在加载失败时**永不**覆盖
    local key = "Player_" .. player.UserId
    local newData = gatherDataFor(player)    -- 一个普通的可序列化值的表

    local ok, err = pcall(function()
        store:UpdateAsync(key, function(old)
            -- 在这里合并/决定；返回 nil 以取消写入
            return newData
        end)
    end)
    if not ok then warn("Save failed for", player.Name, err) end
end
```

### 3. 离开时保存**并且**在关闭时保存

```lua
Players.PlayerRemoving:Connect(savePlayer)

-- BindToClose 在服务器关闭时运行；保存仍在服务器中的所有人。
-- 它有一个有限的时间预算，因此并行保存并等待完成。
game:BindToClose(function()
    local players = Players:GetPlayers()
    local remaining = #players
    if remaining == 0 then return end
    for _, player in players do
        task.spawn(function()
            savePlayer(player)
            remaining -= 1
        end)
    end
    while remaining > 0 do task.wait() end
end)
```

### 4. 带退避重试（临时失败）

```lua
local function withRetry(fn, attempts)
    attempts = attempts or 3
    for i = 1, attempts do
        local ok, result = pcall(fn)
        if ok then return true, result end
        if i < attempts then task.wait(2 ^ i) end   -- 2秒，4秒，... 退避
    end
    return false
end

local ok, data = withRetry(function() return store:GetAsync(key) end)
```

### 5. 增加计数器

```lua
-- IncrementAsync 是整数读-改-写的便利函数（仍然需要包装它）。
local ok, newTotal = pcall(function()
    return store:IncrementAsync("Visits_" .. player.UserId, 1)
end)
```

### 6. 使用 OrderedDataStore 的排行榜

```lua
local boards = DataStoreService:GetOrderedDataStore("Coins")

-- 写入玩家的分数（在分数变化时调用，而不是每帧）。
pcall(function() boards:SetAsync("Player_" .. player.UserId, coins) end)

-- 读取前 10 名，降序。
local ok, pages = pcall(function()
    return boards:GetSortedAsync(false, 10)   -- ascending=false → 最高优先
end)
if ok then
    for rank, entry in ipairs(pages:GetCurrentPage()) do
        print(rank, entry.key, entry.value)   -- entry.value 是数字
    end
end
```

## 陷阱

- **未处理的失败会擦除进度** → 始终 `pcall` Async 调用；在加载失败时，标记会话并拒绝保存，以免默认值覆盖真实数据。
- **`SetAsync` 服务器之间的竞争条件** → 两个服务器写入相同的键可能会互相覆盖。使用 `UpdateAsync` 进行读-改-写，以便每个写入都能看到最新值。
- **在 `UpdateAsync` 回调中产生** → 回调不能调用 `task.wait` 或其他 Async 函数；事先计算新值并返回它。
- **没有 `BindToClose` 保存** → 关闭服务器时服务器中的玩家会丢失未保存的进度；添加 `game:BindToClose` 并在其预算内等待保存完成。
- **节流 / "请求过多"** → 尊重每个键和每分钟的限制；不要在每次值变化时保存。批量保存并在计时器/离开时保存。`GetAsync` 是短暂缓存的，因此立即重新读取可能已过时。
- **存储非序列化值** → 仅持久化 JSON 可序列化数据：数字、字符串、布尔值和具有字符串/数字键的表。`Instance`、`Vector3`、`CFrame` 和函数不会 — 首先将其序列化为普通表。
- **没有 API 访问时测试** → 数据存储在 Studio 中无法使用，直到 *启用 Studio 访问 API 服务* 为止（并且它们在 `LocalScript` 中无法工作）。
- **`DataStoreKeyInfo` 对于有序存储为 nil** → `OrderedDataStore` 不支持版本/元数据；当您需要这些时，使用普通 `DataStore`。

## 参考

- 对于会话锁定（防止跨服务器重复数据），版本/元数据使用 `DataStoreSetOptions`，有序存储分页 (`AdvanceToNextPageAsync`)，键错误代码和请求限制，以及被遗忘权合规性，请阅读 `references/sessions-and-limits.md`。

## 相关技能

- `roblox-luau` — 服务、实例、事件和服务器/客户端模型。
- `save-systems` — 引擎无关的序列化、插槽和迁移。
