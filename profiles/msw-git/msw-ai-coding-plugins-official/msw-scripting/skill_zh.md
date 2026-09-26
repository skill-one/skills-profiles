# MSW 脚本 (.mlua) — 框架 + 文件工作流 + 测试与调试

mlua 基于Lua，但它具有MSW特定的注解、生命周期和执行空间模型。仅凭一般的Lua知识无法编写有效的代码。所有工作都是通过直接编辑工作区文件完成的，代码按 **构建日志 → 运行时日志** 的顺序进行验证。

---

## 1. 核心原则（必须遵循）

### 1.1 优先使用现有脚本

在创建新的 `.mlua` 之前，在 `./RootDesk/MyDesk/` 下使用glob/关键字搜索具有相同目的的现有脚本——**始终优先扩展现有文件**。重复实现会增加维护成本并带来冲突风险。

### 1.2 新脚本的文件夹结构——绝不扁平化文件

当不可避免地要创建新的 `.mlua` 时，将其放置在功能/分类子文件夹下。**必须的路径形状**：`./RootDesk/MyDesk/<FeatureFolder>/<ScriptName>.mlua`。

- **重用** 现有的子文件夹（如果适用）（`Player/`, `UI/`, `Combat/`, `Inventory/`, …）；首先glob `./RootDesk/MyDesk/`。
- **否则创建** 一个以功能命名的文件夹（PascalCase）。一个功能的所有相关脚本（组件/逻辑/事件/结构）应放在一起。即使是一个文件的特性也应有自己的文件夹。
- **禁止** 捕获所有文件夹，如 `Scripts/`, `Misc/`, `Common/`, `New/`, `temp/`。扁平化的根目录使 §1.1（搜索前创建）的规则无法实现。

示例：`Inventory/InventoryManager.mlua`, `Combat/MeleeAttackComponent.mlua`, `UI/Popup/RewardPopupLogic.mlua`.

### 1.3 不猜测API——编写前验证

猜测MSW API名称/参数/返回类型**在运行时静默失败**。必须的顺序：**`.d.mlua` 用于签名** → **`msw-search` 用于语义/示例（如果需要）** → 编写 → LSP诊断（自动运行）。

引擎API位于 `./Environment/NativeScripts/` 下：

| 文件夹 | 内容 | 数量 |
|------|------|:-:|
| `Component/` | 引擎组件 | 104 |
| `Service/` | 系统服务 | 46 |
| `Event/` | 事件类型 | 202 |
| `Logic/` | 内置逻辑 | 9 |
| `Enum/` | 枚举 | 118 |
| `Misc/` | 工具类型（Vector2, …） | 140 |

已知名称 → `Read ./Environment/NativeScripts/{folder}/{name}.d.mlua`。未知名称 → 在那里grep关键字。

### 1.4 Lint (LSP诊断)

`mlua-diagnose` 钩子在每次创建/修改 `.mlua` 后自动运行LSP `diagnose`。迭代修复 → 重新编辑，直到错误严重性诊断为零。

### 1.5 `.codeblock` & 刷新

- `.codeblock` 文件由 Maker Refresh生成——绝不手动创建/编辑/删除。
- 在任何 `.mlua` 创建/修改/重命名后，调用Maker MCP **`refresh`**。刷新需要编辑模式——如果正在播放，请先 `stop`。

### 1.6 MSW ≠ Unity——不要凭直觉推理

直接应用Unity/通用模式**编译正常但在运行时静默失败**。常见的误解：

| Unity直觉 | MSW现实 / 哪里涵盖 |
|---|---|
| `gameObject` / `transform` 从全局管理器 | `@Logic` 没有自.Entity — 见 §3.2（使用属性注入 / `_EntityService`） |
| `OnMouseDown` / `BoxCollider2D` 用于点击 | 物理碰撞器从不发出 `TouchEvent` — World使用 `TouchReceiveComponent` (§10)；UI使用 `ButtonComponent`/`UITouchReceiveComponent` |
| `OnCollisionEnter` + Rigidbody | 实体↔实体碰撞需要 `TriggerComponent` + `TriggerEnter/Leave/Stay` 事件 |
| UI字段名称（`interactable`/`text`/`color`） | MSW特定名称 — 检查 [`msw-ui-system/references/component-api.md`](../msw-ui-system/references/component-api.md)。常见映射：禁用→`Enable`, 文本→`Text`, 文本颜色→`FontColor`, 淡色→`Color`。`ButtonComponent.Interactable` 不存在。 |
| 自由附加多个Rigidbody/Collider | **每种地图类型一个Body** — 见 [`msw-general/references/platform.md`](../msw-general/references/platform.md) §4 |
| 从服务器代码中触摸UI | **UI 仅限客户端** — 服务器→UI通过 `@ExecSpace("Client")` RPC。在附加了 `Server`/`ServerOnly`/`Multicast`/`@Sync` 的UI附加组件上静默无操作并带有运行时警告。见 [`msw-ui-system/references/runtime-patterns.md`](../msw-ui-system/references/runtime-patterns.md) |
| `Instantiate(prefab)` 可在任何地方调用 | `_SpawnService:SpawnByModelId(id, name, pos, parent)` — `parent` 是必需的（没有默认值）。传递 `self.Entity.CurrentMap`。`SpawnByEntity` 不同——`parent = nil` 是允许的。 |
| `static` 类 / 手动编写的单例 | `@Logic` 本身就是单例——调用 `_ScriptName:Method()`，绝不实例化——见 §3.2 |

**规则**：当想要应用Unity模式时，停止并首先验证 `Environment/NativeScripts/*.d.mlua`。

### 1.7 Builder协议预检——**必须**

如果这一轮触发了 `.map` / `.model` / `.ui`（直接或通过 `.mlua` 中的生成实体/放置代码/UI绑定代码），**[../msw-general/references/builder-protocol.md`](../msw-general/references/builder-protocol.md) (核心) 加上每个类型触发的每个构建器文件 ([`builder-protocol-map.md`](../msw-general/references/builder-protocol-map.md) / [`builder-protocol-model.md`](../msw-general/references/builder-protocol-model.md) / [`builder-protocol-ui.md`](../msw-general/references/builder-protocol-ui.md)) 必须首先完全在上下文中 (`Read` 完整文件，如果从未加载此会话或因压缩而丢失——记忆中的摘要不算是上下文）。核心包含共享的写侧合同和跨流程；每个每个构建器文件包含该构建器的API、`typeKey`元数据、自动lint、子实体不变性和 `placeModel`镜像；知道一个构建器并不涵盖另一个。

**触发器**（故意广泛）：`_SpawnService` / `SpawnByModelId` / `SpawnByEntity`; 任何 `.map`/`.model`/`.ui` 变更；调用 `msw_map_builder.cjs` / `msw_model_builder.cjs` / `msw_ui_builder.cjs`; 任何“新怪物/NPC/弹出/地图对象”请求；§11 或 §16 工作。

### 1.8 方法文档注释——在方法体内

每个 `method`（生命周期、RPC、事件处理程序、用户定义的）**必须有**作为方法体内第一行的描述性注释，绝不位于声明上方。mlua的解析器将前导注释绑定到前一个声明，因此“上方”的注释是不可靠的。

```lua
-- ✅ 正确
method void ApplyDamage(Entity target, number amount)
    -- 应用伤害并触发击中VFX。
    target:TakeDamage(amount)
end

-- ❌ 错误——方法上方注释
-- 应用伤害...
method void ApplyDamage(Entity target, number amount)
    target:TakeDamage(amount)
end
```

---

## 2. 路径和文件角色

| 目标 | 路径 | 代理操作 |
|------|------|----------------|
| 用户脚本 | `./RootDesk/MyDesk/**/*.mlua` | **直接创建 / 读取 / 修改 / 删除** |
| 自动生成的工件 | `*.codeblock` | **不要触摸**（Refresh管理它们） |
| 引擎API定义 | `./Environment/NativeScripts/**` | **只读**（不要修改） |
| 模型（组件列表） | `./RootDesk/MyDesk/**/*.model` 加上现有的 `./Global/*.model` 文件 | 编辑 `Components` **当附加脚本时** |
| 地图实例 | `./map/*.map` | 编辑时附加脚本到仅存在于地图内的实体 |

---

## 3. 脚本类型和声明

### 3.1 组件脚本 (`@Component`)

附加到实体的脚本。使用 `self.Entity` 访问拥有的实体。

```lua
@Component
script MyScript extends Component
    property number Speed = 5.0

    @ExecSpace("ServerOnly")
    method void OnBeginPlay()
        -- 初始化（也：OnUpdate(delta), OnEndPlay）
    end
end
```

**允许的父级**：
- `Component` — 通用组件
- `AttackComponent` — 攻击系统（Shape, AttackFast, OnAttack）
- `HitComponent` — 击中系统（OnHit, HandleHitEvent）

### 3.2 逻辑脚本 (`@Logic`)

全局单例。独立于实体运行。用于游戏管理器、UI管理器、实用工具等。

```lua
@Logic
script GameManager extends Logic
    @Sync property integer Score = 0

    @ExecSpace("ServerOnly")
    method void OnBeginPlay()
        -- 全局初始化（也：OnUpdate, OnEndPlay）
    end
end
```

- 每个世界一个（单例）
- 访问方式为 `_<ExactScriptName>` — **没有后缀剥离**。`TDHUDLogic.mlua` → `_TDHUDLogic`（不是 `_TDHUD`）；`TowerDefenseConfig.mlua` → `_TowerDefenseConfig`。启发式剥离静默返回 `nil`。
- 支持 `@Sync` 属性（服务器→客户端）
- 逻辑的 `OnUpdate` 在组件的 `OnUpdate` 之前运行。

> ⚠️ **`@Logic` 没有 `self.Entity`** — 逻辑父级仅暴露 `ConnectEvent`/`DisconnectEvent`/`IsClient`/`IsServer`/`SendEvent`。`self.Entity.xxx` 编译但运行时为nil访问。绑定世界实体，通过属性注入（UUID字面量）或使用 `_EntityService:GetEntityByPath(...)` / `:FindEntityByName(...)`。属性注入（UUID字面量）是首选。见 §7。
>
> ⚠️ **`OnMapEnter` / `OnMapLeave` 在 `@Logic` 上从不触发** — 它们仅限于组件（见 §5）。在逻辑上声明它们是静默死代码。

> **决策：@Component vs @Logic — 由生命周期决定，不是“它是全局的”**
>
> | 范围 | 选择 | 原因 |
> |---|---|---|
> | 世界范围的 | **`@Logic`** | 引擎单例；存在于整个世界会话中。 |
> | **地图范围的** — 仅在一个地图内有意义（任务控制器、波生成器、谜题） | **`@Component` 在地图实体上** | | |
> | 一个角色（怪物AI、物品拾取、玩家技能） | **`@Component` 在该实体上** | | |

问：“玩家走到另一个地图后仍然运行吗？”——是 ⇒ `@Logic`; 否（这个地图） ⇒ `@Component` 在地图实体上；否（这个角色） ⇒ `@Component` 在角色上。

### 3.3 扩展脚本

```lua
@Component
script PlayerAttack extends AttackComponent
    -- 重写父类方法；通过 __base:MethodName() 调用父类
end
```

### 3.4 其他脚本类型

`@Event`（自定义事件） · `@Item`（库存） · `@BTNode`（行为树） · `@State`（状态机） · `@Struct`（复合数据类型）。

---

## 4. mlua 语言扩展（与纯Lua相比）

基于Lua 5.3，具有以下差异：

**添加的语法**：
- `continue` — 跳到下一个循环迭代。
- 复合赋值：`+=`, `-=`, `*=`, `/=`, `//=`, `%=`, `^=`, `..=`（以及位运算 `&=`, `|=`, `<<=`, `>>=`）。多赋值（`a, b += 1, 2`) 和作为函数参数使用（`print(a += 1)`) 是无效的。
- 位运算符：`&`, `|`, `<<`, `>>`.

**限制**：
- **没有全局变量**（`global` 关键字禁止）— 通过属性共享值。
- **没有协程**（`coroutine.*`）。
- 父调用是 `__base:MethodName()`，不是 `super`。

**内置实用函数**：

| 函数 | 目的 |
|------|------|
| `log()` / `log_warning()` / `log_error()` | 每个严重性的日志记录 |
| `wait(seconds)` | 暂停脚本执行 |
| `isvalid(obj) → boolean` | 有效性（处理删除/nil） |
| `enum(t) → table` | 交换键和值 |
| `beginscope(name)` / `endscope()` | 性能分析范围 |

---

## 5. 生命周期

```
OnInitialize → OnBeginPlay → OnUpdate(delta) → OnEndPlay → OnDestroy
                                ↑
                  OnMapEnter / OnMapLeave (Component only, per transition)
```

| 方法 | 时间 | 地点 | 目的 |
|--------|------|------|------|
| `OnInitialize` | 创建后 | 组件 + 逻辑 | 初始化内部变量（很少使用） |
| `OnBeginPlay` | 游戏开始 | 组件 + 逻辑 | **连接事件、启动计时器、初始设置** |
| `OnUpdate(delta)` | 每帧 | 组件 + 逻辑 (**逻辑优先**) | 移动、动画、输入 |
| `OnMapEnter` / `OnMapLeave` | 地图转换 | **组件仅限**（逻辑上不触发） | 每次转换的初始化/清理 |
| `OnEndPlay` | 游戏结束 | 组件 + 逻辑 | **断开事件、清除计时器（强制！）** |
| `OnDestroy` | 移除时 | 组件 + 逻辑 | 最终清理（很少使用） |

**必须模式**：在 `OnBeginPlay` 中连接的所有内容必须在 `OnEndPlay` 中释放（事件、计时器）。

```lua
property any eventHandler = nil   -- EventHandlerBase (必须为 'any'; 不是 integer)
property integer timerId = 0

method void OnBeginPlay()
    self.eventHandler = self.Entity:ConnectEvent(SomeEvent, self.OnSomeEvent)
    self.timerId = _TimerService:SetTimerRepeat(self.Tick, 1/60)
end
method void OnEndPlay()
    if self.eventHandler then self.Entity:DisconnectEvent(SomeEvent, self.eventHandler) end
    if self.timerId then _TimerService:ClearTimer(self.timerId) end
end
```

---

## 6. 执行空间 (ExecSpace)

MSW 是服务器-客户端架构。每个方法都必须声明它在哪里运行。

| ExecSpace | 运行在 | 方向 | 用例 |
|-----------|----------|----------|------|
| `ServerOnly` | 服务器 | 服务器内部仅 | 伤害计算、状态变化、生成 |
| `ClientOnly` | 客户端 | 客户端内部仅 | UI更新、效果、声音 |
| `Server` | 服务器 | 客户端→服务器RPC | 客户端请求服务器（攻击、使用物品） |
| `Client` | 客户端 | 服务器→客户端RPC | 服务器通知客户端（结果UI、效果） |
| `Multicast` | 所有客户端 | 服务器→所有客户端 | 全局事件（公告、Boss生成） |
| *(未指定)* | 调用侧 | 服务器→服务器, 客户端→客户端 | 在任一侧本地执行的共享函数 |

### ExecSpace 对生命周期方法的限制

| 方法 | 允许的 ExecSpace |
|--------|---------------|
| `OnSyncProperty` | **`ClientOnly` 仅** |
| `OnInitialize`, `OnBeginPlay`, `OnUpdate`, `OnEndPlay`, `OnDestroy`, `OnMapEnter`, `OnMapLeave` | `ServerOnly`, `ClientOnly` 或 **未指定** |
| 所有事件处理程序 | `ServerOnly`, `ClientOnly` 或 **未指定** |
| 自定义用户方法 | `Server`, `Client`, `ServerOnly`, `ClientOnly`, `Multicast` |

### 典型的服务器-客户端模式

```
[Client]  输入 (ClientOnly) ──Request()──→ [Server] validate (ServerOnly)
                                                ├─ 状态自动同步 via @Sync
[Client]  UI更新 (ClientOnly) ←──Show()──────┘ (Client RPC)
```

- `ServerOnly`: 客户端调用被静默忽略（无错误）。
- `Server`: 客户端→服务器RPC（网络延迟）。
- `Client`: 服务器→客户端RPC；将 UserId 作为**最后一个调用点参数**来定位一个客户端（不要将其添加到声明中）。

### `senderUserId` — 验证请求者

在 `@ExecSpace("Server")` 身体内部，本地 `senderUserId` 包含调用者客户端的 UserId（服务器分配，客户端不可修改）。用于安全检查。

```lua
@ExecSpace("Server")
method void RequestBuyItem(integer itemId)
    if senderUserId ~= self.Entity.PlayerComponent.UserId then return end
    self:ProcessPurchase(itemId)
end
```

###  | 保留参数名称——`name` 不可用

四个参数名称保留用于RPC解析器，不能作为任何 `@ExecSpace(...)` 方法的自己的参数名称。LSP会阻止脚本使用 `<name>` 名称。：

| 保留 | 引擎使用它做什么 |
|---|---|
| `self` | 方法接收者 |
| `senderUserId` | `@ExecSpace("Server")` 身体上的调用客户端的 UserId |
| `targetUserId` | 接收客户端的 UserId（`@ExecSpace("Client")` 身体上的最后一个调用点参数——**不要声明它**；引擎会添加它） |
| `messageOwnerEntity` | 源生实体对于某些服务回调 |

当自己的参数与之一冲突时，请重命名自己的参数（`targetUserId` → `forUserId`, `senderUserId` → `fromUserId`）。`self` 是接收者，不能被别名——为无关参数选择任何其他名称。

### 手动分支——`IsServer()` / `IsClient()` 是**方法**，不是属性

当方法没有 `@ExecSpace`（在调用它的那一侧运行）并且需要根据不同的一侧进行不同路径时，使用 `self:IsServer()` / `self:IsClient()` 进行分支。两者都在 `Component` 和 `Logic` 上声明为 `method boolean IsServer()` / `method boolean IsClient()` — 必须调用，不能读取。

```lua
if self:IsServer() then ... end   -- ✅ 方法调用 → boolean
if self.IsServer    then ... end  -- ❌ 方法对象本身 → 总是 truthy
```

点号不带括号的形式是一个静默错误：LSP不会标记它，脚本编译后，没有括号的点号形式的“if”总是进入，因为方法对象总是truthy——因此客户端代码也会在服务器上运行（反之亦然）。症状是“两侧都执行”而不是崩溃。每次使用 `self:IsServer()`。

### 跨边界参数类型

允许跨服务器↔客户端RPC：`string`, `integer`, `number`, `boolean`, `table`, `Vector2/3/4`, `Color`, `Entity`, `Component`, `EntityRef`, `ComponentRef`。**`any` 不允许。引擎枚举也不跨边界——既不类型化（LSP拒绝将引擎枚举类型作为参数）也不通过 `any` 混入（运行时 `LEA-3036 InvalidCast`）。标准解决方案：将选择编码为发送者的 `string` 键，接收者分支，然后本地转换回枚举。`SyncTable<k,v>` 泛型也必须来自允许列表。

---

## 7. 常用服务/逻辑

所有服务和逻辑都通过 `_Name`（下划线 + 类型名称）访问。只有最常用的几个被列出。

| 服务 / 逻辑 | 目的 |
|-------------|------|
| `_SpawnService` | 生成实体 (`SpawnByModelId`, `SpawnByEntity`). **没有 `Despawn` 方法**——通过 `Entity:Destroy()` / `Entity:Destroy(delaySeconds)` (两者都是 `ControlOnly`) 移除生成的实体。 |
| `_TimerService` | 计时器 (`SetTimer`, `SetTimerRepeat`, `ClearTimer`) |
| `_EntityService` | 实体查找 (`GetEntity`, `GetEntities`, `GetEntitiesByPath`) |
| `_UserService` | 玩家查找 (`GetUsersByMapComponent(map.MapComponent`) 返回当前在该地图上的所有玩家——标准的“查找此地图上的玩家”调用，由 `Soldier` 的 `FindNearestPlayer` 使用）。返回 `nil` 当没有用户时。 |
| `_InputService` | 输入状态查询；接收 `ScreenTouchEvent` |
| `_ResourceService` | 查找资源RUIDs；`LoadAnimationClipAndWait(ruid)` 同步加载AnimationClip（阻塞一帧——缓存结果；如果你想要避免阻塞，请将 `_ResourceService:PreloadAsync({ruid}, function() ... end)` 包裹在内部）。 |
| `_DataStorageService` | 持久化数据（玩家保存）— **⚠️ 信用计费。不要在 `OnUpdate` / 短计时器中调用；使用 `Batch*` 在循环中使用。详情：[references/datastorage.md](references/datastorage.md)** |
| `_UtilLogic` | 随机、时间、字符串和数学实用工具 |
| `_TweenLogic` | 插值动画（MoveTo, ScaleTo, RotateTo） |
| `_UILogic` | UI坐标转换（例如，ScreenToWorldPosition）— ClientOnly |

> 对于完整列表，直接读取 `.d.mlua` 文件：`./Environment/NativeScripts/` 或通过 `msw-search`。

### 内置全局变量访问不需要 `_` 前缀

上面的 `_Name` 规则仅适用于**服务和逻辑**。一些内置的作为普通全局变量暴露——用下划线前缀访问它们是运行时错误 (`nil`引用)。

| 全局（正确） | 错误 | 目的 |
|---|---|---|
| `Environment` | ❌ `_Environment` | 执行环境查询 — `Environment:IsMakerPlay()` / `IsMakerEdit()` / `IsPlay()` / `IsPublishedPlay()` / `IsMobilePlatform()` / `IsPCPlatform()`，`WorldId` 属性。`GetApplicationVersion()` 是 ClientOnly（服务器上为 `nil`）。 |
| `CollisionGroups` | ❌ `_CollisionGroups` | `CollisionGroup` 对象的表，按组名键——`CollisionGroups.HitBox`, `.Monster`, `.Player`, 等。内置的：`Default` / `TriggerBox` / `HitBox` / `Interaction` / `Portal` / `Climbable`, 以及任何项目定义的组。每个条目都有一个 `.Id`（字符串）和 `:GetCollideGroups()`。 |

---

## 8. 数学、实用工具、保留词、类型注解

### 数学 / 实用工具示例

```lua
_UtilLogic:RandomDouble()             -- 0.0~1.0
(UtilLogic:RandomIntegerRange(1, 10)  -- 包含
```

### mlua 实用工具类

超出Lua标准库的集合：`List` / `ReadOnlyList` / `SyncList`, `Dictionary` / `ReadOnlyDictionary` / `SyncDictionary`（Sync* 变体自动同步服务器↔客户端）。其他实用类型：`DateTime`, `TimeSpan`, `Regex`, `Translator`, `Quaternion`, `Vector2Int`, `FastVector2/3` / `FastColor`（性能优化用原地操作）, `Item`（库存）。

> `.Values` / `.Keys` 在 `Dictionary` / `ReadOnlyDictionary` / `SyncDictionary` 返回一个普通的Lua `table` — 直接使用 `ipairs` 直接迭代。不需要 `:GetValues()` / `:ToTable()` / `pairs(dict)` 包装器。列表类似，但需要先 `:ToTable()` 才能迭代（`ReadOnlyList<T>` 不是Lua表）。
>
> ```lua
> -- 所有连接的玩家（服务器侧扇出）
> for _, id in ipairs(cardIds) do
>     local capturedId = id
>     local h = e:ConnectEvent(ButtonClickEvent, function() self:OnCardClicked(capturedId) end)
>     table.insert(self.clickHandlers, { entity = e, handler = h })
> end
> ```

> 详细API在 `Environment/NativeScripts/` 或通过 `msw-search`。

### 会话计时器——绝不锚定 `ElapsedSeconds`

陷阱：`self.deadline = _UtilLogic.ElapsedSeconds + 15` 在 `OnBeginPlay` 中。世界实例在多个Maker播放会话中生存，因此保存的截止日期在下一个播放时是过去的，并且立即触发。

对于会话内计时器，在 `OnUpdate` 中减少一个 `delta` 驱动的属性：

```lua
property number waveCountdown = 0
method void OnBeginPlay()
    self.waveCountdown = 1
end
method void OnUpdate(number delta)
    if self.waveCountdown > 0 then
        self.waveCountdown = self.waveCountdown - delta
        if self.waveCountdown <= 0 then self:StartWave() end
    end
end
```

对于会话相对经过的时间，在 `OnBeginPlay` 中设置基线 (`self.startTime = _UtilLogic.ElapsedSeconds`)，然后减去。绝不比较原始 `ElapsedSeconds` 跨会话。

### 类型注解（代码提示）

`---@type T` / `---@param` / `---@return` 仅提供编辑器自动完成——**没有运行时效果**。

### 保留词

作为标识符禁止：`handler`, `property`, `method`, `script`, `end`, `extends`, `self`, `nil`, `true`, `false`。

适用于本地变量、参数、属性、方法、点号字段（`rec.handler`），以及**裸**表键（`{ handler = ... }`）。使用方括号引用外部字符串键（`rec["handler"]）是好的，但更喜欢重命名内部键（例如，`eventHandler`）。

---

## 9. 外部工具

- Maker MCP (`refresh`/`logs`/`play`/`stop`/`screenshot`/…): **`msw-general`** 技能。
- API描述/示例/指南不在 `.d.mlua` 中：**`msw-search`** 技能。
- MCP接线 / `.mcp.json` / API密钥设置：共享 https://maplestoryworlds-creators.nexon.com/ko/docs?postId=1368

调试顺序：**构建日志 → 播放 → 日志 → 停止 → 修复 → 诊断 → 刷新 → 重复**。

---

## 10. 脚本编写工作流

1. **搜索** 现有脚本 (§1.1) — 如果存在类似的脚本，请修改。
2. **验证规范** (§1.3) — `.d.mlua` 首先读取，如果不足够，`msw-search`。
3. **决定路径** (§1.2) — 功能文件夹强制执行；绝不写入 `MyDesk/` 根目录。
4. **编写**。
5. **验证** — `mlua-diagnose` 钩子自动运行；修复直到错误严重性诊断为零 (§1.4)。
6. **刷新** — Maker MCP `refresh` (§1.5)。
7. **(如果需要)** `play` → `logs` → `stop` (§17).

删除/重命名也需要 `refresh` + 清理 `.model` / `.map` 中的引用。

---

## 11. 将脚本（组件）附加到实体

> **§1.7 触发器** — 首先读取 [builder-protocol.md](../msw-general/references/builder-protocol.md) + 匹配的每个构建器协议文件。绝不能直接编辑 `Components` 数组作为原始JSON。

- **附加到 `.model`（首选）**: `ModelBuilder.addComponent()` / `upsertComponent()`。地图实例继承。
- **附加到仅一个地图实例**: `MapBuilder.upsertComponent(name, "script.XXX", body)`.
- **全局模型** (`./Global/*.model`)：现有的全局模板影响整个项目，并通过 `ModelBuilder` + Maker Refresh 编辑。不要在 `Global/` 下创建新文件；在 `RootDesk/MyDesk/Models/` 下创建新的自定义模型。

---

## 12. 测试与调试

验证行为在 **Maker播放模式** 中的过程，然后使用 **运行时日志、截图和模拟输入** 缩小错误。

> 对于MCP工具列表、播放模式限制和刷新规则，请参阅 `msw-general`。

### 12.1 总是首先检查构建日志

**在每次 `play` 之前，运行 `logs(kind="build")`**。构建错误会导致脚本完全无法加载（组件/逻辑表现得像缺失一样），并且它们通常**不会出现在运行时日志**中——大多数“代码看起来正确但无法工作”的报告追溯到遗漏的构建错误。修复 → 刷新 → 重新检查直到错误严重性诊断为零，然后播放。

> ⚠️ **构建日志为空 ≠ 构建 OK.** Refresh阶段 **mlua转换错误**（Maker弹窗 *"在mlua转换过程中发生错误"*）会完全绕过构建控制台：`refresh` 仍然报告正常，`logs(kind="build")` 保持为 0，错误文本仅出现在 `logs(kind="normal")` 中。如果构建日志为空但脚本仍然无法加载——或者那个弹窗被报告——请下一步读取 `logs(kind="normal")` 而不是循环刷新→构建检查。**不要** `clear_logs`，直到错误被捕获：清除会清除正常日志桶，即转换错误的唯一副本。

### 12.2 错误分类

| 类别 | 痕迹 | 哪里查找 |
|------|-----------|-----------|
| **脚本错误** | 堆栈跟踪带有文件 + 行号 | `.mlua` 的确切行；事件/时间顺序 |
| **nil引用** | `attempt to index a nil value` | 初始化顺序, `isvalid`, 1帧后Spawn计时 |
| **组件缺失** | nil组件 / `GetComponent` 失败 | `.model` 中的 `Components` 数组；名称拼写错误 |
| **同步/网络** | 仅客户端中断，值不匹配或收敛晚 | `@Sync`, `ExecSpace`, RPC流 |
| **`Info` LIA 1113/1114/1115**（读取/调用点错误） | 静态分析无法解析用户跨脚本引用 (`_LogicName`, 用户 `@Component` 点/方法)。构建仍然通过（错误=0/warnings=0） | 治理为噪音；使用 `log()` 验证。**例外**：`LIA-1114` 在赋值目标 (`self.<name> = ...` `<name>` 未声明) 是一个真实的运行时错误信号——在播放时 `cannot set <name>, no such field`；声明 `property` 或使用 `self._T.<name>`。如果它们淹没真实问题，请将下一个 `logs` 调用范围提升到更高的严重性。 |

如果日志不确定，请添加 `log()` 调用；如果API未知，请在添加调用之前验证规范 (§1.3)。
