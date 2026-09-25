# Roblox 游戏开发技能

## 描述
专业的 Roblox 游戏开发者，擅长 Luau 脚本编写、游戏机制设计、UI/UX 设计和盈利策略。协助从简单脚本到复杂多人体验的各项工作。

## 资源库
此技能包含一套全面的、可用于生产的资源：

- **📜 [辅助脚本](scripts/)** - 用于数据管理、网络、UI、游戏流程和音频的专业实用模块
- **📋 [文档模板](templates/)** - 完整的项目文档模板，包括游戏设计文档、技术规格、测试计划和营销策略
- **📚 [开发资源](resources/)** - 游戏模板、资源库、调试指南、性能优化工具和快速参考材料

## 核心能力

### Luau 编程
- **现代 Luau 功能**：利用类型注解、泛型、通用类型解决器（正式发布）、改进的类型推断/自动完成和性能优化
- **脚本架构**：实现模块化代码，并正确分离关注点
- **性能优化**：编写能够处理大量玩家的高效脚本
- **错误处理**：强大的错误管理和调试技术

### Luau 类型系统更新
- **新类型解决器**：正式发布（不再是工作室 Beta 版）；从 2026 年 1 月 7 日起默认启用于 `nonstrict` 和 `nocheck` 模式
- **主要改进**：更好的类型推断、更少的误报、更强的泛型支持以及改进的自动完成
- **旧版解决器时间表**：旧版解决器仍可通过至 2026 年，但计划移除
- **迁移指南**：大部分代码无需更改，但少数边缘情况可能需要显式类型注解或清理
- **最佳实践**：在公共 API 上优先使用显式注解，在适当的地方使用泛型，并依赖改进的自动完成进行快速迭代

```lua
-- 新类型解决器更准确地推断类型
local function processPlayer(player: Player)
    local name: string = player.Name  -- 正确推断
    local team = player.Team  -- Team? 正确推断
end
```

### 游戏系统开发
- **玩家数据管理**：DataStore 实现和备份系统（参见 [DataManager.lua](scripts/DataManager.lua)）
- **背包系统**：物品管理、交易和装备系统
- **经济设计**：货币系统、商店和平衡的进度
- **战斗机制**：伤害系统、武器、能力以及 PvP/PvE 游戏玩法
- **社交功能**：好友、公会、聊天系统和玩家互动

### Roblox Studio 专家知识
- **工作区组织**：正确的模型层次结构和资源管理
- **地形雕刻**：高级地形工具和环境设计
- **灯光与氛围**：逼真的灯光设置和氛围营造
- **动画**：骨骼创建、关键帧动画和脚本动画
- **物理模拟**：自定义物理、约束和交互对象

### 用户界面设计
- **现代 UI 框架**：简洁、响应式的界面设计（参见 [UIManager.lua](scripts/UIManager.lua)）
- **移动端优化**：触控友好的控制和自适应布局
- **无障碍性**：色盲友好的调色板和易读字体
- **UX 模式**：直观的导航和用户流程优化

### 多人游戏与网络
- **客户端-服务器架构**：正确的远程事件/函数使用（参见 [RemoteManager.lua](scripts/RemoteManager.lua)）
- **反作弊措施**：服务器端验证和安全最佳实践
- **同步**：实时多人机制和状态管理
- **扩展解决方案**：为大量玩家进行性能优化

### 盈利与分析
- **开发者产品**：Robux 购买和虚拟货币
- **游戏通行证**：高级功能和订阅模式
- **分析集成**：玩家行为跟踪和留存指标
- **A/B 测试**：功能测试和转化率优化

## 开发流程

### 项目设置
1. **游戏概念开发**：类型分析、目标受众和核心循环设计（参见 [游戏设计文档模板](templates/game_design_document.md)）
2. **技术架构**：脚本组织、模块系统和依赖管理（参见 [技术规格模板](templates/technical_specification.md)）
3. **资源管道**：模型导入、纹理优化和版本控制（参见 [资源库](resources/asset_library.md)）
4. **测试框架**：单元测试、集成测试和 QA 流程（参见 [测试计划模板](templates/testing_plan.md)）

### 实施阶段
1. **核心机制**：基本游戏循环和玩家控制（使用 [游戏模板](resources/game_templates.md) 进行快速原型设计）
2. **系统集成**：连接不同的游戏系统（参见 [GameManager.lua](scripts/GameManager.lua)）
3. **内容创建**：关卡、任务、物品和进度系统
4. **精炼与优化**：性能调优和错误修复（参见 [性能优化指南](resources/performance_optimization.md)）
5. **发布准备**：商店资源、描述和营销材料（参见 [营销计划模板](templates/marketing_plan.md)）

### 最佳实践
- **代码组织**：使用 ModuleScripts 进行可重用组件
- **安全优先**：始终在服务器端进行验证
- **性能监控**：定期分析和优化
- **玩家反馈**：基于玩家数据进行迭代开发
- **版本控制**：正确的备份和协作流程

## 常见模式与解决方案

### DataStore 访问和存储更新
- **按体验配额**：每个体验都有自己的 DataStore 读写配额，Roblox 将从 2026 年初开始执行这些限制
- **节流行为**：超出限制会节流请求而不是抛出硬错误，因此代码应优雅地重试或回退
- **最佳实践**：批量操作、本地缓存，并将临时状态保存在会话数据表中，而不是立即写入每个更改
- **工作室工具**：在 Roblox Studio 中使用 **Data Stores Manager** 直接查看、编辑和删除条目，而无需发布（`工作室 → 查看 → Data Stores Manager`）

### 数据持久化
完整实现可在 [DataManager.lua](scripts/DataManager.lua) 中找到

```lua
-- DataStore 最佳实践，包含重试逻辑、缓存和速率限制意识
local DataStoreService = game:GetService("DataStoreService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local PlayerDataModule = {}
local dataStore = DataStoreService:GetDataStore("PlayerData_v1")
local sessionData = {}
local cachedData = {}

local function safeGetAsync(dataStore, key)
    local success, result = pcall(function()
        return dataStore:GetAsync(key)
    end)
    if not success then
        warn("DataStore 请求失败，使用缓存数据")
        return cachedData[key]
    end
    return result
end

function PlayerDataModule:LoadData(player)
    local data = safeGetAsync(dataStore, player.UserId)
    
    if data then
        sessionData[player.UserId] = data
    else
        -- 默认数据结构
        sessionData[player.UserId] = {
            level = 1,
            coins = 100,
            inventory = {},
            settings = {}
        }
    end
    
    cachedData[player.UserId] = sessionData[player.UserId]
    return sessionData[player.UserId]
end
```

### DataStore2 迁移指南
- **弃用状态**：Berezaa/DataStore2 已弃用；请为新的和现有项目优先使用原生 `DataStoreService`
- **迁移原因**：按体验配额和内置 Data Stores Manager 减少了额外缓存层的需要
- **迁移步骤**：
  - 将 `DataStore2()` 调用替换为 `DataStoreService:GetDataStore()`
  - 使用表格手动管理会话缓存，用于临时状态
  - 使用 `UpdateAsync` 进行原子更新，而不是 DataStore2 的 `:Update()` 辅助函数

### 远程通信
完整实现可在 [RemoteManager.lua](scripts/RemoteManager.lua) 中找到

```lua
-- 安全的远程事件处理
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local remoteEvents = ReplicatedStorage:WaitForChild("RemoteEvents")
local purchaseEvent = remoteEvents:WaitForChild("PurchaseItem")

purchaseEvent.OnServerEvent:Connect(function(player, itemId, quantity)
    -- 服务器端验证
    if not itemId or not quantity or quantity <= 0 then return end
    
    local playerData = PlayerDataModule:GetData(player)
    local itemCost = ShopModule:GetItemCost(itemId) * quantity
    
    if playerData.coins >= itemCost then
        playerData.coins -= itemCost
        InventoryModule:AddItem(player, itemId, quantity)
        -- 更新客户端
        UpdateClientData(player)
    end
end)
```

### 性能优化
完整优化指南可在 [Performance Optimization](resources/performance_optimization.md) 中找到

```lua
-- 高效的对象池用于投射物
local ProjectilePool = {}
local activeProjectiles = {}
local poolSize = 50

function ProjectilePool:GetProjectile()
    local projectile = table.remove(activeProjectiles) 
    if not projectile then
        projectile = CreateNewProjectile()
    end
    return projectile
end

function ProjectilePool:ReturnProjectile(projectile)
    -- 重置投射物状态
    projectile.Parent = workspace.ProjectilePool
    projectile.CFrame = CFrame.new(0, -1000, 0)
    table.insert(activeProjectiles, projectile)
end
```

## 专业领域

### 移动游戏开发
- 触控控制和手势识别
- 电池优化和内存管理
- 跨平台兼容性测试

### 教育游戏
- 学习目标整合
- 进度跟踪和评估
- 适龄内容和安全

### 竞技游戏
- 排名系统和匹配
- 观战模式和回放系统
- 比赛组织工具

### 创意/建造游戏
- 高级建造工具和约束
- 用户创作的保存/加载系统
- 协作建造功能

## 故障排除与调试

全面调试资源可在 [Debugging Guide](resources/debugging_guide.md) 中找到

### 常见问题
- **内存泄漏**：连接清理和正确的垃圾回收
- **性能瓶颈**：分析工具和优化策略
- **网络问题**：延迟处理和连接管理
- **跨平台错误**：设备特定测试和兼容性

### 开发工具
- **Roblox Studio Debugger**：断点和变量检查
- **性能分析器**：CPU 和内存使用分析
- **网络监视器**：远程事件跟踪和带宽使用
- **Data Stores Manager**：在工作室中直接查看、编辑和删除 DataStore 条目，用于调试和测试（`工作室 → 查看 → Data Stores Manager`）
- **错误日志**：用于生产调试的自定义日志系统

### 快速参考
基本命令和代码片段可在 [Quick Reference](resources/quick_reference.md) 中找到

## 保持更新
- 关注 Roblox 开发者中心获取平台更新
- 参与开发者论坛和社区讨论
- 在 Beta 版本中尝试新功能
- 研究成功游戏的设计模式和趋势

## 入门指南

### 快速设置
1. **从 [游戏模板](resources/game_templates.md) 选择一个游戏模板** 以匹配您的愿景
2. **使用 [scripts/](scripts/) 中的辅助脚本设置核心系统**
3. **使用 [templates/](templates/) 中的文档模板规划您的项目**
4. **遵循 [resources/](resources/) 中的指南优化性能**

### 必要的辅助脚本
- **[DataManager.lua](scripts/DataManager.lua)** - 具有自动保存和重试逻辑的健壮玩家数据持久化
- **[RemoteManager.lua](scripts/RemoteManager.lua)** - 具有内置速率限制和验证的安全网络
- **[UIManager.lua](scripts/UIManager.lua)** - 具有动画和响应式设计的现代 UI 系统
- **[GameManager.lua](scripts/GameManager.lua)** - 完整的游戏状态和生命周期管理
- **[SoundManager.lua](scripts/SoundManager.lua)** - 具有三维空间支持的专业音频系统

### 项目文档
- **[Game Design Document](templates/game_design_document.md)** - 完整的项目规范和愿景
- **[Technical Specification](templates/technical_specification.md)** - 详细的架构和实施文档
- **[Testing Plan](templates/testing_plan.md)** - 综合的 QA 策略和流程
- **[Marketing Plan](templates/marketing_plan.md)** - 战略营销和发布活动规划

### 开发资源
- **[Asset Library](resources/asset_library.md)** - 精心策划的音频、视觉和模型资源集合
- **[Performance Optimization](resources/performance_optimization.md)** - 用于流畅游戏性能的工具和技术
- **[Debugging Guide](resources/debugging_guide.md)** - 综合的故障排除和错误处理
- **[Quick Reference](resources/quick_reference.md)** - 基本命令和代码片段

此技能支持从概念到发布的全面 Roblox 游戏开发，重点关注最佳实践、安全性和玩家参与。所有资源均可立即集成到您的项目中。

版本：2.0
最后更新：2026 年 5 月
