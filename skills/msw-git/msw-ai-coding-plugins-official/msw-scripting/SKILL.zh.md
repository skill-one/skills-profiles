---
name: msw-scripting
description: 编写MSW脚本（.mlua）并集成测试和调试。涵盖mlua语法、注解（@Component/@Logic/@ExecSpace/@Sync）、生命周期、执行空间、属性同步、事件系统、文件工作流、构建日志检查、错误分类以及测试/调试循环。关键词：脚本、mlua、lua、Component、Logic、注解、ExecSpace、Sync、事件、测试、调试、生命周期。
---

# MSW 脚本 (.mlua) — 框架 + 文件工作流 + 测试与调试

mlua 基于 Lua，但它具有 MSW 特定的注解、生命周期和执行空间模型。仅凭一般的 Lua 知识无法编写出可工作的代码。所有工作都是通过**直接编辑工作区中的文件**完成的，代码的验证顺序为**构建日志 → 运行时日志**。

---

## 1. 核心原则（必须遵循）

### 1.1 优先使用现有脚本

在创建新的 `.mlua` 之前，在 `./RootDesk/MyDesk/` 下通过通配符/关键字搜索现有具有相同目的的脚本——**扩展现有文件始终是首选方案**。重复实现会增加维护成本和冲突风险。

### 1.2 新脚本文件夹结构——绝不平铺文件

当不可避免地需要创建新的 `.mlua` 时，将其放置在功能/类别子文件夹下。**必须的路径格式**：`./RootDesk/MyDesk/<功能文件夹>/<脚本名>.mlua`。

- 如果适用，**重用**现有的子文件夹（`Player/`、`UI/`、`Combat/`、`Inventory/`、…）；首先通配符搜索 `./RootDesk/MyDesk/`。
- 否则，创建一个以功能命名的子文件夹（PascalCase）。一个功能的所有相关脚本（组件/逻辑/事件/结构）应保持在一起。即使是一个文件的功能也要有自己的文件夹。
- **禁止**使用通配符文件夹，如 `Scripts/`、`Misc/`、`Common/`、`New/`、`temp/`。扁平化的根目录使得 §1.1（创建前搜索）的规则无法执行。

示例：`Inventory/InventoryManager.mlua`、`Combat/MeleeAttackComponent.mlua`、`UI/Popup/RewardPopupLogic.mlua`。

### 1.3 绝不猜测 API —— 编写前验证

猜测 MSW API 名称/参数/返回类型**在运行时静默失败**。必须的顺序：**`.d.mlua` 用于签名** → **如果需要，`msw-search` 用于语义/示例** → 编写 → LSP 诊断（自动运行）。

引擎 API 位于 `./Environment/NativeScripts/`：

| 文件夹 | 内容 | 数量 |
|------|------|:-:|
| `Component/` | 引擎组件 | 104 |
| `Service/` | 系统服务 | 46 |
| `Event/` | 事件类型 | 202 |
| `Logic/` | 内建逻辑 | 9 |
| `Enum/` | 枚举 | 118 |
| `Misc/` | 工具类型（Vector2、…） | 140 |

已知名称 → `Read ./Environment/NativeScripts/{文件夹}/{名称}.d.mlua`。未知名称 → 在那里搜索关键字。

### 1.4 Lint（LSP 诊断）

`mlua-diagnose` 钩子在每次创建/修改 `.mlua` 后自动运行 LSP `diagnose`。迭代修复 → 重新编辑，直到错误严重性诊断达到零。

### 1.5 `.codeblock` & 刷新

- `.codeblock` 文件由 Maker Refresh 生成——**绝不手动创建/编辑/删除**。
- 在任何 `.mlua` 创建/修改/重命名/删除后，调用 Maker MCP **`refresh`**。刷新需要编辑模式——如果正在运行，请先 `stop`。

### 1.6 MSW ≠ Unity —— 不要从直觉出发推理

直接应用 Unity/通用模式**编译正常但在运行时静默失败**。常见误解：

| Unity 直觉 | MSW 现实 / 适用场景 |
|---|---|
| `gameObject` / `transform` 从全局管理器获取 | `@Logic` 没有自带的 `self.Entity` —— 参考 §3.2（使用属性注入 / `_EntityService`） |
| `OnMouseDown` / `BoxCollider2D` 用于点击 | 物理碰撞器从不发射 `TouchEvent` —— 世界使用 `TouchReceiveComponent`（§10）；UI 使用 `ButtonComponent`/`UITouchReceiveComponent` |
| `OnCollisionEnter` + Rigidbody | 实体间碰撞需要 `TriggerComponent` + `TriggerEnter/Leave/Stay` 事件 |
| UI 字段名称（`interactable`/`text`/`color`） | MSW 特定名称——检查 [`msw-ui-system/references/component-api.md`](../msw-ui-system/references/component-api.md)。常见映射：禁用→`Enable`，文本→`Text`，文本颜色→`FontColor`，色调→`Color`。`ButtonComponent.Interactable` 不存在。 |
| 自由地附加多个 Rigidbody/Collider | **每种地图类型一个 Body** —— 参考 [`msw-general/references/platform.md`](../msw-general/references/platform.md) §4 |
| 从服务器代码中触达 UI | **UI 仅客户端**——服务器→UI 通过 `@ExecSpace("Client")` RPC 传输。在附加到 UI 的组件上托管 `Server`/`ServerOnly`/`Multicast`/`@Sync` 会静默无操作并带运行时警告。参考 [`msw-ui-system/references/runtime-patterns.md`](../msw-ui-system/references/runtime-patterns.md) |
| 任何地方可调用的 `Instantiate(prefab)` | `_SpawnService:SpawnByModelId(id, name, pos, parent)` —— 需要 `parent`，仅服务器端——参考 §11 |
| `static` 类 / 手动编写的单例 | `@Logic` 本身就是单例——调用 `_ScriptName:Method()`，绝不实例化——参考 §3.2 |

**规则**：当想应用 Unity 模式时，请停止并首先验证 `Environment/NativeScripts/*.d.mlua`。

### 1.7 Builder 协议预检——**必须**

如果这一轮触达 `.map` / `.model` / `.ui`（直接或通过 `.mlua` 中的生成实体/放置代码/UI 绑定代码），**必须**先完全加载 [`../msw-general/references/builder-protocol.md`](../msw-general/references/builder-protocol.md)（核心）以及每个触达类型的单独构建器文件（`[builder-protocol-map.md`](../msw-general/references/builder-protocol-map.md) / `[builder-protocol-model.md`](../msw-general/references/builder-protocol-model.md) / `[builder-protocol-ui.md`](../msw-general/references/builder-protocol-ui.md)）——（如果会话中从未加载或因压缩丢失，则必须加载完整文件——记忆中的摘要不计为在上下文中）。核心包含共享的写端契约和跨流；每个单独的构建器文件包含该构建器的 API、`typeKey` 元数据、自动 lint、子实体不变性和 `placeModel` 反射；了解一个构建器并不涵盖另一个。

**触发器**（故意范围广泛）：`_SpawnService` / `SpawnByModelId` / `SpawnByEntity`；任何 `.map`/`.model`/`.ui` 变更；调用 `msw_map_builder.cjs` / `msw_model_builder.cjs` / `msw_ui_builder.cjs`；任何“新怪物/NPC/弹窗/地图对象”请求；§11 或 §16 工作。

### 1.8 方法文档注释——在方法体内

每个 `method`（生命周期、RPC、事件处理程序、用户定义）**必须**在方法体的第一行具有描述性注释，绝不能在声明上方。mlua 的解析器将前导注释绑定到前一个声明，因此“上方”的注释不可靠。

```lua
-- ✅ 正确
method void ApplyDamage(Entity target, number amount)
    -- 应用伤害并触发命中 VFX。
    target:TakeDamage(amount)
end

-- ❌ 错误——方法上方的注释
-- 应用伤害...
method void ApplyDamage(Entity target, number amount)
    target:TakeDamage(amount)
end
```

---

## 2. 路径和文件角色

| 目标 | 路径 | 代理动作 |
|------|------|----------------|
| 用户脚本 | `./RootDesk/MyDesk/**/*.mlua` | **直接创建 / 读取 / 修改 / 删除** |
| 自动生成的工件 | `*.codeblock` | **不要触碰**（Refresh 管理它们） |
| 引擎 API 定义 | `./Environment/NativeScripts/**` | **只读**（不要修改） |
| 模型（组件列表） | `./RootDesk/MyDesk/**/*.model` 加上当前放置的 `./Global/*.model` 文件 | 在附加脚本时编辑 `Components` |
| 地图实例 | `./map/*.map` | 在附加脚本到仅存在于地图内的实体时编辑 |

---

## 3. 脚本类型和声明

### 3.1 组件脚本 (`@Component`)

附加到实体的脚本。使用 `self.Entity` 访问所属实体。

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

**允许的父类**：
- `Component` — 通用组件
- `AttackComponent` — 攻击系统（Shape、AttackFast、OnAttack）
- `HitComponent` — 命中系统（OnHit、HandleHitEvent）

### 3.2 逻辑脚本 (`@Logic`)

全局单例。独立于实体运行。用于游戏管理器、UI 管理器、工具等。

```lua
@Logic
script GameManager extends Logic
    @Sync property integer Score = 0

    @ExecSpace("ServerOnly")
    method void OnBeginPlay()
        -- 全局初始化（也：OnUpdate、OnEndPlay）
    end
end
```

- 每个世界一个（单例）
- 访问方式为 `_<精确脚本名>` —— **无后缀剥离**。`TDHUDLogic.mlua` → `_TDHUDLogic`（不是 `_TDHUD`）；`TowerDefenseConfig.mlua` → `_TowerDefenseConfig`。启发式剥离会静默返回 `nil`。
- 支持 `@Sync` 属性（服务器→客户端）
- 逻辑的 `OnUpdate` 在组件的 `OnUpdate` **之前**运行。

> ⚠️ **`@Logic` 没有 `self.Entity`** — 逻辑父类仅暴露 `ConnectEvent`/`DisconnectEvent`/`IsClient`/`IsServer`/`SendEvent`。`self.Entity.xxx` 编译通过，但运行时为空访问。绑定世界实体通过属性（`property Entity x = "uuid"` / `property EntityRef x = ""`）或使用 `_EntityService:GetEntityByPath(...)` / `:FindEntityByName(...)` 查找。属性注入（UUID 字面量）是首选。参考 §7。
>
> ⚠️ **`OnMapEnter` / `OnMapLeave` 在 `@Logic` 上永不触发** — 它们仅限于组件（参考 §5）。在逻辑上声明它们是静默的无用代码。

> **决策：@Component vs @Logic —— 由生命周期决定，而非“是否全局？”**
>
> | 范围 | 选择 | 原因 |
> |---|---|---|
> | 全局，跨每个地图转换（账户状态、世界事件总线、全局 UI 管理器） | **`@Logic`** | 引擎单例；存在于整个世界会话中。 |
> | **地图范围**——仅在一个地图内有意义（任务控制器、波次生成器、谜题） | **`@Component` 在地图实体上** | 地图卸载时清理。将此放在 `@Logic` 中会导致状态/计时器跨地图泄漏。 |
> | 一个行为者（怪物 AI、物品拾取、玩家技能） | **`@Component`** 在该实体上 |  |
>
> 询问：*"玩家走到另一个地图后仍然运行吗？"* —— 是 ⇒ `@Logic`；否（这个地图） ⇒ `@Component` 在地图实体上；否（这个行为者） ⇒ `@Component` 在行为者上。

### 3.3 扩展脚本

```lua
@Component
script PlayerAttack extends AttackComponent
    -- 重写父类方法；通过 __base:MethodName() 调用父类
end
```

### 3.4 其他脚本类型

`@Event`（自定义事件）· `@Item`（库存）· `@BTNode`（行为树）· `@State`（状态机）· `@Struct`（复合数据类型）。

---

## 4. mlua 语言扩展（与纯 Lua 对比）

基于 Lua 5.3，具有以下差异：

**新增语法**：
- `continue` — 跳到下一个循环迭代。
- 复合赋值：`+=`、`-=`、`*=`、`/=`、`//=`、`%=`、`^=`、`..=`（以及位运算 `&=`、`|=`、`<<=`、`>>=`）。多值赋值（`a, b += 1, 2`）和作为函数参数使用（`print(a += 1)`）无效。
- 位运算符：`&`、`|`、`<<`、`>>`。

**限制**：
- **无全局变量**（禁止 `global` 关键字）—— 通过属性共享值。
- **无协程**（`coroutine.*`）。
- 父类调用是 `__base:MethodName()`，不是 `super`。

**内置工具函数**：

| 函数 | 目的 |
|------|------|
| `log()` / `log_warning()` / `log_error()` | 各严重性级别的日志记录 |
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
|------|------|------|------|
| `OnInitialize` | 创建后 | 组件 + 逻辑 | 初始化内部变量（很少使用） |
| `OnBeginPlay` | 游戏开始 | 组件 + 逻辑 | **连接事件、启动计时器、初始设置** |
| `OnUpdate(delta)` | 每帧 | 组件 + 逻辑 (**逻辑优先**) | 移动、动画、输入 |
| `OnMapEnter` / `OnMapLeave` | 地图转换 | **组件仅限**（逻辑上为静默无操作） | 每个地图的初始化/清理 |
| `OnEndPlay` | 游戏结束 | 组件 + 逻辑 | **断开事件、清除计时器（必须！）** |
| `OnDestroy` | 移除 | 组件 + 逻辑 | 最终清理（很少使用） |

**必须模式**：在 `OnBeginPlay` 中连接的所有内容必须在 `OnEndPlay` 中释放（事件、计时器）。

```lua
property any eventHandler = nil   -- EventHandlerBase（必须为 'any'；不是整数）
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

MSW 是服务器-客户端架构。每个方法必须声明其运行位置。

| ExecSpace | 运行在 | 方向 | 用例 |
|-----------|----------|----------|------|
| `ServerOnly` | 服务器 | 仅服务器内部 | 伤害计算、状态变更、生成 |
| `ClientOnly` | 客户端 | 仅客户端内部 | UI 更新、效果、声音 |
| `Server` | 服务器 | 客户端→服务器 RPC | 客户端请求服务器（攻击、使用物品） |
| `Client` | 客户端 | 服务器→客户端 RPC | 服务器通知客户端（结果 UI、效果） |
| `Multicast` | 所有客户端 | 服务器→所有客户端 | 全局事件（公告、Boss 生成） |
| *(未指定)* | 调用方侧 | 服务器→服务器，客户端→客户端 | 在任一侧本地执行的共享函数 |

### ExecSpace 对生命周期方法的限制

| 方法 | 允许的 ExecSpace |
|--------|---------------|
| `OnSyncProperty` | **仅 `ClientOnly`** |
| `OnInitialize`, `OnBeginPlay`, `OnUpdate`, `OnEndPlay`, `OnDestroy`, `OnMapEnter`, `OnMapLeave` | `ServerOnly`, `ClientOnly`, 或 **未指定** |
| 所有事件处理程序 | `ServerOnly`, `ClientOnly`, 或 **未指定** |
| 自定义用户方法 | `Server`、`Client`、`ServerOnly`、`ClientOnly`、`Multicast` 中的任何一种 |

### 典型的服务器-客户端模式

```
[Client]  输入 (ClientOnly) ──Request()──→ [Server] validate (ServerOnly)
                                                ├─ 状态自动同步 via @Sync
[Client]  UI 更新 (ClientOnly) ←──Show()──────┘ (Client RPC)
```

- `ServerOnly`：客户端调用被静默忽略（无错误）。
- `Server`：客户端→服务器 RPC（网络延迟）。
- `Client`：服务器→客户端 RPC；将 `UserId` 作为**最后一个调用点参数**来定位一个客户端（**不要**将其添加到声明中）。

### `senderUserId` —— 验证请求者

在 `@ExecSpace("Server")` 体内，本地 `senderUserId` 存储调用者的客户端 `UserId`（服务器分配，客户端不可修改）。用于安全检查。

```lua
@ExecSpace("Server")
method void RequestBuyItem(integer itemId)
    if senderUserId ~= self.Entity.PlayerComponent.UserId then return end
    self:ProcessPurchase(itemId)
end
```

### 保留参数名称——`名称不可用`

四个参数名称保留给 RPC 封装器，不能作为任何 `@ExecSpace(...)` 方法的自参数名称。LSP 会用 `'<名称>' name is unavailable.` 块住脚本：

| 保留 | 引擎用于 |
|---|---|
| `self` | 方法接收者 |
| `senderUserId` | `@ExecSpace("Server")` 体内的调用客户端的 `UserId` |
| `targetUserId` | 接收客户端的 `UserId`（`@ExecSpace("Client")` 体内的最后一个调用点参数——**不要**声明它；引擎会追加它） |
| `messageOwnerEntity` | 某些服务回调的原始实体 |

当它们冲突时（`targetUserId` → `forUserId`，`senderUserId` → `fromUserId`）重命名自己的参数。`self` 是接收者，不能别名化——为无关参数选择任何其他名称。

### 手动分支——`IsServer()` / `IsClient()` 是**方法**，不是属性

当方法没有 `@ExecSpace`（在调用它的那一侧运行）并且需要根据不同侧执行不同路径时，使用 `self:IsServer()` / `self:IsClient()` 分支。两者都声明为 `method boolean IsServer()` / `method boolean IsClient()` 在 `Component` 和 `Logic` 上——必须**调用**，不能读取。

```lua
if self:IsServer() then ... end   -- ✅ 方法调用 → boolean
if self.IsServer    then ... end  -- ❌ 方法对象本身 → 总是 truthy
```

点号不带括号的形式是一个静默的bug：LSP不会标记它，脚本可以编译，并且"if"语句总是进入，因为方法对象是truthy的——所以客户端代码也会在服务器上运行（反之亦然）。症状是"两边都执行"，而不是崩溃。每次都使用冒号调用（`self:IsServer()`）。

### 跨边界参数类型

允许在服务器↔客户端RPC之间传输：`string`、`integer`、`number`、`boolean`、`table`、`Vector2/3/4`、`Color`、`Entity`、`Component`、`EntityRef`、`ComponentRef`。**`any`不允许。**引擎枚举也不跨边界传输——既不是类型化的（LSP会拒绝引擎枚举类型作为参数），也不是通过`any`偷偷传输的（运行时`LEA-3036 InvalidCast`）。标准解决方案：在发送者上将选择编码为`string`键，在接收者上分支，并在本地将枚举转换回来。`SyncTable<k,v>`泛型也必须来自允许列表。

---

## 7. 属性系统

### 基本类型

`number`（float/double——整数是单独的类型`integer`）、`string`、`boolean`、`Vector2`/`Vector3`、`Color`（r、g、b、a在0.0~1.0之间）、`any`。

```lua
property number Speed = 5.0
property integer Count = 0
property Vector2 Direction = Vector2(0, 0)
property Color Tint = Color(1, 1, 1, 1)
```

### 实体/组件引用属性

```lua
property Entity targetEntity = "94a274e4-4111-40f1-924d-c95a3a1f14d5"   -- UUID字符串字面量
property ButtonComponent btnOk = "uuid-string"                          -- 类型化的组件引用
```

**AI必须直接注入UUID**——从`.map`/`.ui`中读取`id`并作为字符串字面量硬编码。不要在编辑器中要求用户拖拽绑定（那是人类作者的便利）。

### 实体与EntityRef

`Entity` / `Component`引用在地图转换时会**丢失**。`EntityRef` / `ComponentRef`在地图转换时**会保留**——对于多地图游戏，请优先使用。

### 同步注解

- `@Sync`——服务器→所有客户端。单向；客户端的更改不会传播回服务器。存在网络延迟。
- `@TargetUserSync`——服务器→拥有者的客户端。适用于每个玩家的私有数据（货币、成就）。对于非`PlayerEntity`，它会回退到普通的`@Sync`。
- **不能同步**：`any`、`table`——使用`SyncTable`代替。
- 两者都不带参数。

```lua
@Sync property number CurrentHp = 100
@TargetUserSync property number PrivateScore = 0
@Sync property SyncTable<number> Scores              -- 数组形式，NO默认字面量
@Sync property SyncTable<string, number> Stats       -- 字典形式，NO默认字面量
```

#### `SyncTable<...>`属性——没有默认字面量

声明`SyncTable<V>`（数组形式）或`SyncTable<K, V>`（字典形式）**不带`= ...`初始化器**。引擎保留`SyncTable`属性的`=`槽用于其自己的类型记录，并在运行时自动初始化属性为**空集合**。你写的任何字面量（`= {}`、`= { key = val }`、`= nil`）都会被静默丢弃——它是一种误导性的噪音，不是真正的默认值，并且通过代码块的一趟往返会将其擦除。

在`OnInitialize` / `OnBeginPlay`中填充初始条目：

```lua
@Sync property SyncTable<string, number> Stats       -- 构造时为空
@Sync property SyncTable<number> Scores              -- 构造时为空

method void OnBeginPlay()
    if self:IsServer() then
        self.Stats["hp"] = 100
        self.Stats["mp"] = 50
        self.Scores:Add(0)
    end
end
```

在运行时将普通的Lua表分配给`SyncTable`属性也会被拒绝——该属性只接受其自己的代理。逐字段修改（`self.Stats[k] = v`）或调用其方法（`self.Scores:Add(v)` / `:Remove(v)` / `:Clear()`）。

#### `SyncList<V>`不是用户属性类型

`SyncList<V>`仅作为原生引擎组件上的**只读属性**暴露（例如`TagComponent.Tags`、`PhysicsColliderComponent.PolygonPoints`、`SkeletonRendererComponent.AnimationNames`、各种`JointComponent.Joints`）。用户脚本可以**读取**这些并调用它们的方法（`:Add(v)`、`:Remove(v)`、`:Clear()`、`.Count`、`:ToTable()`），但不能在自己的`@Component` / `@Logic`上声明`property SyncList<...> X`，也不能实例化`SyncList(...)`。

对于脚本中的同步集合，使用`SyncTable<V>`（数组形式）或`SyncTable<K, V>`（字典形式）——见上文。

### 临时属性（`_T`）

`self._T.<name>`是非同步的、无需声明的临时状态。服务器和客户端保持自己的值；不会在inspector中显示。不能被`@Sync`'d。

> ⚠️ **`_T`是唯一无需声明的字段。** 分配给任何其他未声明的`self.<name>`是运行时错误——`cannot set <name>, no such field`——这会杀死调用方法（通常所有`OnBeginPlay`）。你设置的每个`self.<name>`必须是声明的`property`，或者通过`self._T.<name>`。构建日志保持干净，除了一个容易忽略的`LIA-1114` Info（见§17.2）。

### `OnSyncProperty`回调

当`@Sync`属性更改时触发的客户端钩子。**必须是`ClientOnly`**（不能被更改）。在组件和逻辑上可用。

```lua
@ExecSpace("ClientOnly")
method void OnSyncProperty(string name, any value)
    if name == "CurrentHp" then self:UpdateHpBar(value) end
end
```

### 属性编辑器属性

```lua
@DisplayName("...") @Description("...") @MaxLength(20) @HideFromInspector
@MinValue(0) @MaxValue(999) @Delta(5)   -- Delta = 移动 +/- 步长
```

---

## 8. 事件系统 / RPC

### 静态订阅——`@EventSender` + `handler`

```lua
@EventSender("Self") handler HandleHitEvent(HitEvent event) ... end
@EventSender("Service", "InputService") handler HandleKeyDown(KeyDownEvent event) ... end
```

`@EventSender` 第一个参数：`"Self"` / `"LocalPlayer"`（没有第二个参数）· `"Entity"`、id / `"Model"`、id / `"Service"`、typeName / `"Logic"`、typeName。

### 动态订阅——`ConnectEvent` / `DisconnectEvent`

```lua
property any clickHandler = nil
self.clickHandler = entity:ConnectEvent(ButtonClickEvent, self.OnClick)  -- OnBeginPlay
entity:DisconnectEvent(ButtonClickEvent, self.clickHandler)              -- OnEndPlay (必须)
```

对于每个元素的捕获状态（卡片ID、槽索引），使用闭包处理器；将返回的`EventHandlerBase`存储在表中，并在`OnEndPlay`中断开每个连接。

```lua
property table clickHandlers = {}

for _, id in ipairs(cardIds) do
    local capturedId = id
    local h = e:ConnectEvent(ButtonClickEvent, function() self:OnCardClicked(capturedId) end)
    table.insert(self.clickHandlers, { entity = e, handler = h })
end
```

> ⚠️ **`ConnectEvent`在 Entity / Logic / Service上——不是Component。** Component只*发射*事件；在所属**Entity**（或`_InputService` / `_<LogicName>`）上订阅。`self.Entity.ButtonComponent:ConnectEvent(...)`运行时为nil。
>
> ```lua
> property any clickHandler = nil
> property any keyHandler = nil
> self.clickHandler = self.Entity:ConnectEvent(ButtonClickEvent, self.OnClick)
> self.keyHandler   = _InputService:ConnectEvent(KeyDownEvent, self.OnKeyDown)
> ```

> ⚠️ **`handler` vs `method void`**——`handler Name(Ev e)`与`@EventSender(...)`配对，并由声明连接。`method void Name(Ev e)`是通过`ConnectEvent(EvType, self.Name)`动态连接的回调。混合它们会编译但永远不会触发（E-V1-5）。如果`@EventSender`存在→`handler`；如果你会调用`ConnectEvent`→`method void`。

### 自定义事件——类型化的类风格

编写自定义事件的**唯一**方法是`@Event` + `extends EventType`并带有`property`字段。没有内联工厂。

```lua
@Event
script DamageDealtEvent extends EventType
    property number amount = 0
end

local dmg = DamageDealtEvent(); dmg.amount = 50
self.Entity:SendEvent(dmg)                                 -- 通过Entity / Logic / Service
self.Entity:ConnectEvent(DamageDealtEvent, self.OnDamage)  -- 第一个参数 = 事件 Type

method void OnDamage(DamageDealtEvent event) log(event.amount) end
```

原生事件（引擎提供的，例如`HitEvent.TotalDamage/.AttackerEntity`、`ButtonClickEvent`、`StateChangedEvent.PrevState/.CurState`）——见`Environment/NativeScripts/Event/`。

---

## 9. 有效性检查和方法重写

### 有效性检查

访问已删除的实体是运行时错误——始终先`isvalid()`。

```lua
if isvalid(entity) then ... end
if isvalid(self.Entity.SomeComponent) then ... end
```

### 方法重写

在一个`extends`扩展的脚本中，具有与父类相同签名的方法会重写它。内置引擎方法标记为`---@sealed`不能被重写。通过`__base:MethodName(args)`调用原始父方法。

#### ⚠️ LEA-3014 `SignatureMismatch`——ExecSpace必须与父类匹配

"相同签名"**包括`@ExecSpace`**。重写必须与父类的注解块**字节完全相同**——包括**缺少**一个。在父类没有注解的情况下向其添加`@ExecSpace("ServerOnly")`以使其成为服务器端→运行时LEA-3014。

**常见违规者**：AttackComponent / HitComponent伤害钩子（`CalcDamage`、`CalcCritical`、`GetCriticalDamageRate`、`GetDisplayHitCount`、`IsAttackTarget`、`IsHitTarget`、`OnAttack`）都声明**不带**`@ExecSpace`。用无注解重写——它们仍然安全，因为服务器端伤害管道是唯一的调用者。

**工作流程**：在`.d.mlua`（§1.3）中读取父类并逐字复制其注解块。通过对齐子类的`@ExecSpace`到父类来修复LEA-3014，而不是反过来。

---

## 10. 输入/点击事件——世界与UI（不要混淆）

### 世界触摸——两种方法

| 方法 | 事件 | 连接在 | 使用 |
|------|------|----------|-----|
| **实体触摸**——实体上的`TouchReceiveComponent` | `TouchEvent` (+Hold/Release) | `entity:ConnectEvent(...)` | "哪个实体被触摸"——NPC、物品 |
| **屏幕触摸**——无组件 | `ScreenTouchEvent` | `_InputService:ConnectEvent(...)` | "屏幕上的位置"——放置、移动目标 |

两个事件都携带`TouchId`（int32）+ `TouchPoint`（屏幕坐标Vector2）。对于世界坐标，`_UILogic:ScreenToWorldPosition(event.TouchPoint)`。使用`_InputService:IsPointerOverUI()`过滤UI点击。如果`TouchEvent`未命中，`ScreenTouchEvent` + `ScreenToWorldPosition`是无需配置的回退方案。

> ⚠️ **物理碰撞器不发射`TouchEvent`**——`BoxCollider2D`、`CircleCollider2D`、Rigidbody/Kinematicbody，以及`TriggerComponent`都不传递触摸输入。只有**`TouchReceiveComponent`**发射`TouchEvent`/`TouchHoldEvent`/`TouchReleaseEvent`。
>
> **设置**：`AutoFitToSize = true`（自动调整TouchArea到Sprite/Avatar比例）是最简单的路径。手动`TouchArea`应超出sprite 10–20%的余量。`RelayEventToBehind = true`（默认）转发；仅当要阻止时设置为`false`。
>
> **未触发？按顺序检查**：(1) `TouchReceiveComponent`确实附加（在`.map` / `.model`中）；(2) `TouchArea`非零且实体在屏幕上可见；(3) 没有前面的实体用`RelayEventToBehind = false`阻挡；(4) 处理器存储在`property any`中（否则会被GC）。

> **选择规则**："哪个实体被触摸"→`TouchEvent`；"屏幕上的位置"→`ScreenTouchEvent`。

### PC鼠标按钮（左/右/中）——使用`KeyDownEvent`，而不是`ScreenTouchEvent.TouchId == 2`

`ScreenTouchEvent`在PC上仅对左键（`TouchId == 1`）触发；`TouchId == 2`是移动的双指触摸——通过它读取右键在Maker模拟器中工作，但在真实PC上是**静默无输入**。对于PC鼠标按钮，`_InputService:ConnectEvent(KeyDownEvent, ...)`，并根据`event.key == KeyboardKey.Mouse0` / `Mouse1` / `Mouse2`（左键=323，右键=324，中键=325）分支。要支持移动多指触摸和PC，连接`ScreenTouchEvent`和`KeyDownEvent`——它们不会重复触发（无移动右键；无PC`TouchId == 2`）。

### UI点击

对于UI实体（`./ui/*.ui`、`ui`树），使用**`ButtonComponent` + `ButtonClickEvent`**。将UI事件放在世界对象上（或反之）会静默无效果——首先决定目标是世界对象还是UI面板按钮。

---

## 11. 地图上下文和实体生成

> **§1.7 trigger**——`Read` [builder-protocol.md](../msw-general/references/builder-protocol.md) + 匹配的每个构建器协议文件，在执行任何生成 / `.map` / `.model`工作之前。

### 子元素遍历

对于"地图中的所有X" / "子元素名为Y"查询，使用`Entity`的查找工具包：

| 成员 | 返回 | 使用 |
|---|---|---|
| `Entity.Children` | `ReadOnlyList<Entity>`（调用`:ToTable()`进行迭代） | 立即子元素 |
| `Entity:GetChildByName(name, recursive=false)` | `Entity` | 按名称 |
| `Entity:GetChild(id, recursive=false)` | `Entity` | 按UUID |
| `Entity:GetChildComponentsByTypeName(typename, recursive=false)` | `table<Component>` | 所有匹配的子元素 |
| `Entity:GetFirstChildComponentByTypeName(typename, recursive=false)` | `Component` | 第一个匹配 |

```lua
local map = self.Entity.CurrentMap                              -- 优先使用此方法而不是服务查找
local units = map:GetChildComponentsByTypeName("script.MyUnit", false)
for _, child in ipairs(self.Entity.Children:ToTable()) do log(child.Name) end
```

集合是`Children`——`ChildList`/`Childs`/`GetChildren()`都是错误的（编译，运行时nil，`LIA-1114` Info）。运行时生成的实体必须作为`CurrentMap`的子元素才能被查找。

### 原生与用户组件访问

| 访问 | 在...上工作 |
|---|---|
| `entity.SomeComponent`（点号） | **仅引擎原生**（`TransformComponent`、`ButtonComponent`、…） |
| `entity:GetComponent("script.MyUnit")` | 用户`@Component`（任何） |
| `entity:GetFirstChildComponentByTypeName("script.MyUnit", true)` | 用户`@Component`在子元素上 |

用户`@Component`类型名**始终是`"script.<FileBaseName>"`**——`MyUnit.mlua` → `"script.MyUnit"`，无论特征文件夹嵌套如何。`entity.MyUnit`（点号）返回`nil`与`LIA-1114`。要在脚本之间传递用户组件引用，声明一个类型化的属性（`property MyUnit unit = ""`），并注入UUID。

> ⚠ 方法是`GetComponent`（重载为`GetComponent(Type)`和`GetComponent(string typename)`——见`Environment/NativeScripts/Misc/Entity.d.mlua`）。`*ByTypeName`后缀仅存在于**子元素**变体（`GetChildComponentsByTypeName` / `GetFirstChildComponentByTypeName`）。

`GetComponent(string)`返回抽象的`Component`类型，因此结果上的成员访问会降级为动态分发，LSP会引发`LIA-1114` Info（或在将值传递给签名期望具体用户`@Component`的函数时引发`type mismatch`错误）。使用`---@type`进行类型转换以恢复静态类型：

```lua
---@type MyUnit
local unit = self.Entity:GetComponent("script.MyUnit")
unit:DoSomething()  -- LSP现在根据MyUnit进行类型检查
```

### 运行时生成

- 使用`_SpawnService:SpawnByModelId(id, name, pos, parent)`——**`parent`是必需的**（无默认值）。传递`self.Entity.CurrentMap`。`SpawnByEntity`不同——`parent = nil`是允许的。
- `.model`模板必须已经存在。新对象流程：**作者`.model` → 生成或放置在地图上**。

### 身体组件与直接Position写入

具有身体（Kinematic/Rigid/Sideview）的实体会忽略直接的`TransformComponent.WorldPosition`写入——物理会在下一帧覆盖它们。使用：
- 每帧：`MovementComponent:MoveToDirection(dir, dt)`
- 本地传送：`MovementComponent:SetPosition(pos)`或`body:SetPosition(Vector2)`
- 世界传送：`body:SetWorldPosition(Vector2)`——Kinematicbody在RectTile地图上的标准绝对位置调用
- 直接Transform写入仅适用于无身体的实体（装饰、效果）。

**不要将身体作为解决方案移除**——这将禁用瓦片碰撞和进入/离开事件（`NativeIssue_MissingComponent`）。

---

## 12. 常用服务/逻辑

所有服务和逻辑都通过`_Name`（下划线+类型名）访问。仅列出最常用的。

| 服务 / 逻辑 | 目的 |
|-------------|------|
| `_SpawnService` | 生成实体 (`SpawnByModelId`, `SpawnByEntity`)。**没有 `Despawn` 方法** — 通过 `Entity:Destroy()` / `Entity:Destroy(delaySeconds)` (两者 `ControlOnly`) 移除生成的实体。 |
| `_TimerService` | 定时器 (`SetTimer`, `SetTimerRepeat`, `ClearTimer`) |
| `_EntityService` | 实体查找 (`GetEntity`, `GetEntities`, `GetEntitiesByPath`) |
| `_UserService` | 玩家查找 (`GetUsersByMapComponent(map.MapComponent)` 返回当前在给定地图上的所有玩家 — 标准的 "查找此地图上的玩家" 调用，`Soldier` 的 `FindNearestPlayer` 使用)。无玩家时返回 `nil`。 |
| `_InputService` | 输入状态查询；接收 `ScreenTouchEvent` |
| `_ResourceService` | 查找资源 RUIDs；`LoadAnimationClipAndWait(ruid)` 同步加载 AnimationClip (阻塞一帧 — 缓存结果；如果想要避免阻塞，请用 `_ResourceService:PreloadAsync({ruid}, function() ... end)` 包裹) |
| `_DataStorageService` | 持久化数据 (玩家存档) — **⚠️ 信用扣费。不要在 `OnUpdate` / 短定时器中调用；在循环中使用 `Batch*`。详情：[参考资料/datastorage.md](参考资料/datastorage.md)** |
| `_UtilLogic` | 随机数、时间、字符串和数学工具 |
| `_TweenLogic` | 缓动动画 (MoveTo, ScaleTo, RotateTo) |
| `_UILogic` | UI 坐标转换 (例如，ScreenToWorldPosition) — ClientOnly |

> 对于完整列表，直接阅读 `.d.mlua` 文件：`./Environment/NativeScripts/Service/` (46 个文件) 和 `./Environment/NativeScripts/Logic/` (9 个文件)。对于域详情，通过 `msw-search` 搜索。

### 不带 `_` 前缀访问的内置全局变量

上述 `_Name` 规则仅适用于服务和逻辑。一些内置函数以普通全局变量形式暴露 — 用下划线开头的访问是运行时错误 (`nil` 引用)。

| 全局变量 (正确) | 错误 | 目的 |
|---|---|---|
| `Environment` | ❌ `_Environment` | 执行环境查询 — `Environment:IsMakerPlay()` / `IsMakerEdit()` / `IsPlay()` / `IsPublishedPlay()` / `IsMobilePlatform()` / `IsPCPlatform()`，`WorldId` 属性。`GetApplicationVersion()` 是 ClientOnly (服务器上为 `nil`)。 |
| `CollisionGroups` | ❌ `_CollisionGroups` | 以组名键值的 `CollisionGroup` 对象表 — `CollisionGroups.HitBox`, `.Monster`, `.Player` 等。内置：`Default` / `TriggerBox` / `HitBox` / `Interaction` / `Portal` / `Climbable`，以及任何项目定义的组。每个条目都有一个 `.Id` (字符串) 和 `:GetCollideGroups()`。 |

---

## 13. 数学、工具、保留字、类型注解

### 数学 / 工具示例

```lua
_UtilLogic:RandomDouble()             -- 0.0~1.0
_UtilLogic:RandomIntegerRange(1, 10)  -- 包含

-- ElapsedSeconds / ServerElapsedSeconds: 世界实例生命周期，不在 OnBeginPlay 时重置。
-- 它们跨重复的 Maker 编辑器会话持续计时。
-- 对于会话计时器，见下文 "会话计时器"。
_UtilLogic.ElapsedSeconds
_UtilLogic.ServerElapsedSeconds
```

### mlua 工具类

Lua 标准库之外的集合：`List` / `ReadOnlyList` / `SyncList`，`Dictionary` / `ReadOnlyDictionary` / `SyncDictionary` (Sync* 变体自动同步服务器↔客户端)。其他工具类型：`DateTime`，`TimeSpan`，`Regex`，`Translator`，`Quaternion`，`Vector2Int`，`FastVector2/3` / `FastColor` (原地操作以提升性能)，`Item` (背包)。

> `.Values` / `.Keys` 在 `Dictionary` / `ReadOnlyDictionary` / `SyncDictionary` 上返回一个普通的 Lua `table` — 直接用 `ipairs` 迭代。不需要 `:GetValues()` / `:ToTable()` / `pairs(dict)` 包装器。列表类似，但需要先 `:ToTable()` (`ReadOnlyList<T>` 不是 Lua 表)。
>
> ```lua
> -- 所有连接的玩家 (服务器端分叉)
> for _, user in ipairs(_UserService.UserEntities.Values) do
>     if isvalid(user) then ... end
> end
> ```

> 详细 API 在 `Environment/NativeScripts/` 或通过 `msw-search` 查看。

### 会话计时器 — 不要锚定 `ElapsedSeconds`

陷阱：`self.deadline = _UtilLogic.ElapsedSeconds + 15` 在 `OnBeginPlay` 中。世界实例在多个 Maker 会话中存活，所以保存的截止日期在下次会话中是过去的，并且立即触发。

对于会话计时器，在 `OnUpdate` 中递减一个 `delta` 驱动的属性：

```lua
property number waveCountdown = 0
method void OnBeginPlay() self.waveCountdown = 15 end
method void OnUpdate(number delta)
    if self.waveCountdown > 0 then
        self.waveCountdown = self.waveCountdown - delta
        if self.waveCountdown <= 0 then self:StartWave() end
    end
end
```

对于会话相对的经过时间，在 `OnBeginPlay` 中基线 (`self.startTime = _UtilLogic.ElapsedSeconds`) 并减去。不要跨会话比较原始 `ElapsedSeconds`。

### 类型注解 (代码提示)

`---@type T` / `---@param` / `---@return` 仅提供编辑器自动完成 — **没有运行时效果**。

### 保留字

禁止用作标识符：`handler`，`property`，`method`，`script`，`end`，`extends`，`self`，`nil`，`true`，`false`。

适用于局部变量、参数、属性、方法、点字段名 (`rec.handler`)，以及 **裸** 表键 (`{ handler = ... }`)。外部字符串键的括号引号 (`rec["handler"]`) 是可以的，但优先重命名内部键 (例如，`eventHandler`)。

---

## 14. 外部工具

- Maker MCP (`refresh`/`logs`/`play`/`stop`/`screenshot`/…)：**`msw-general`** 技能。
- API 描述/示例/指南不在 `.d.mlua` 中：**`msw-search`** 技能。
- MCP 连接 / `.mcp.json` / API 密钥设置：共享 https://maplestoryworlds-creators.nexon.com/ko/docs?postId=1368

调试顺序：**构建日志 → play → logs → stop → 修复 → 诊断 → refresh → 重复**。

---

## 15. 脚本编写工作流

1. **搜索** 现有脚本 (§1.1) — 如果有相似的，修改它。
2. **验证规范** (§1.3) — `.d.mlua` 首先查看，如果不足，使用 `msw-search`。
3. **决定路径** (§1.2) — 功能文件夹强制要求；永远不要写入 `MyDesk/` 根目录。
4. **编写**。
5. **验证** — `mlua-diagnose` 钩子自动运行；修复直到零错误 (§1.4)。
6. **刷新** — Maker MCP `refresh` (§1.5)。
7. **(如果需要)** `play` → `logs` → `stop` (§17)。

删除/重命名也需要 `refresh` + 清理 `.model` / `.map` 中的引用。

---

## 16. 将脚本 (组件) 绑定到实体

> **§1.7 触发** — 先阅读 `Read` [builder-protocol.md](../msw-general/references/builder-protocol.md) + 匹配的每个构建器协议文件。永远不要作为原始 JSON 编辑 `Components` 数组。

- **绑定到 `.model` (推荐)**：`ModelBuilder.addComponent()` / `upsertComponent()`。地图实例继承。
- **仅绑定到一个地图实例**：`MapBuilder.upsertComponent(name, "script.XXX", body)`。
- **全局模型** (`./Global/*.model`)：现有的全局模板影响整个项目，并通过 `ModelBuilder` + Maker 刷新就地编辑。不要在 `Global/` 下创建新文件；在 `RootDesk/MyDesk/Models/` 下创建新的自定义模型。

---

## 17. 测试和调试

在 Maker 中验证 **play 模式** 下的行为，然后使用 **运行时日志、截图和模拟输入** 缩小错误范围。

> 对于 MCP 工具列表、play 模式限制和刷新规则，见 `msw-general`。

### 17.1 首先始终检查构建日志

**在每次 `play` 之前，运行 `logs(kind="build")`**。构建错误会导致脚本完全失败 (组件/逻辑表现得像缺失)，并且它们通常**不会出现在运行时日志**中 — 大多数 "代码看起来正确但无法工作" 的报告都追溯到遗漏的构建错误。修复 → 刷新 → 重新检查直到错误为零，然后 play。

> ⚠️ **空构建日志 ≠ 构建 OK。** 刷新阶段的 **mlua 转换错误** (Maker 弹出 *"在 mlua 转换过程中发生错误"**) 完全绕过构建控制台：`refresh` 仍然报告正常，`logs(kind="build")` 保持为 0，错误文本仅出现在 `logs(kind="normal")` 中。如果构建日志为空但脚本仍然无法加载 — 或者出现该弹出 — 接下来读取 `logs(kind="normal")` 而不是循环刷新→构建检查。**不要** `clear_logs` 直到找到原因：清除会擦除正常日志桶，即转换错误的唯一副本。

### 17.2 错误分类

| 类别 | 迹象 | 查找位置 |
|------|-----------|-----------|
| **脚本错误** | 带文件 + 行号的堆栈跟踪 | `.mlua` 的确切行；事件/时间顺序 |
| **nil 引用** | `attempt to index a nil value` | 初始化顺序，`isvalid`，生成后一帧的计时 |
| **组件缺失** | nil 组件 / `GetComponent` 失败 | `.model` 中的 `Components` 数组；名称拼写错误 |
| **同步 / 网络** | 仅客户端出错，值不匹配或收敛较晚 | `@Sync`，`ExecSpace`，RPC 流 |
| **`Info` LIA 1113/1114/1115** (在读取/调用位置出现误报) | 静态分析无法解析用户跨脚本引用 (`_LogicName`，用户 `@Component` 点/方法)。构建仍然通过 (错误=0/警告=0) | 视为噪音；用 `log()` 验证。**例外**：`LIA-1114` 在赋值目标 (`self.<name> = ...` 中 `<name>` 未声明) 上是真正的运行时错误信号 — 在 play 时 `cannot set <name>, no such field`；声明 `property` 或使用 `self._T` (§7)。如果它们淹没真实问题，将下一个 `logs` 调用限制为更高严重性。 |
| **用户类型 `Symbol not found` / `type not found`** | 使用位置在用户类型 `.mlua` 主体存在之前编写。 | 先编写用户类型主体 `.mlua`，然后 Maker `refresh` 重新生成 `.codeblock`。构建日志缓存可以保留一个过时的周期 — 通过下一个诊断判断。 |

如果日志不明确，在 `.mlua` 中添加 `log()` 检查实体/组件/属性状态。

### 17.3 测试结果报告

简要总结：**场景** (一行) · **环境** (地图，是否刷新?) · **步骤** (输入/Lua) · **结果** (通过/失败/阻塞) · **证据** (1–2 行日志，如果需要则截图) · **下一步行动**。

### 17.4 工作流

每个测试场景的统一循环：

```
edit → refresh → logs(kind="build")  ──┐
                                           ↓ (错误? 修复并再次刷新)
                  clear_logs (可选) → play
                                           ↓
                   键盘输入 / 鼠标输入以重现
                                           ↓
                   logs(kind="normal") → 使用 §17.2 表格分类
                                           ↓ (不足? 在 .mlua 中添加 log()，刷新，重放)
                                          stop → 修复 → 循环
```

**变体** — 相同循环，不同入口条件：

| 场景 | 注意步骤 |
|---|---|
| **首次测试** | 从编辑 → 刷新开始。 |
| **回归 / 修复循环** | `clear_logs` 在 `play` 前进行干净的复现。 |
| **mlua 转换错误** (弹出，或构建日志为空但脚本从未加载) | 首先使用 `logs(kind="normal")` — 转换错误跳过构建日志 (§17.1)。直到找到错误才 `clear_logs`。 |
| **错误分析** | 收集运行时日志后，首先映射到 §17.2；只有在分类不明确时才添加 `log()`。 |
| **运行时值检查** | 添加 `log()` 调用；如果 API 未知，先验证规范 (§1.3) 再添加调用。 |

### 17.5 最终验证 (通过/失败)

**"无错误 ≠ 通过。"** 在报告完成之前，收集基于 `log()` 的证据，证明预期逻辑实际上已执行。完整清单：[参考资料/verify-checklist.md](参考资料/verify-checklist.md) (运行时 → 代码审查 → 日志证据 → 通过/失败)。

### 17.6 相关技能

`msw-general` — MCP 工具，截图/日志策略，刷新规则，工作空间和层次结构。
