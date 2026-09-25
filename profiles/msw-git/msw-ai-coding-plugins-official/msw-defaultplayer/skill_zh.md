# MSW DefaultPlayer

使用 `msw-general` ModelBuilder 检查/修补 DefaultPlayer 模型文件，管理组件，并配置移动 / 物理效果 / 生命值 / 摄像机。

> 关于**服装 / 头像装备**，请参阅 `msw-avatar` 技能。服装不仅适用于 DefaultPlayer，还适用于任何实体，因此它们位于单独的技能中。

---

## DefaultPlayer 概述

### 什么是 DefaultPlayer？
MapleStory Worlds Maker 工作区中默认提供的**玩家角色模型**。
- 当任何用户进入世界时，会根据此模型创建一个玩家实体。
- 要使用的模型 ID 由 `DefaultUserEnterLeaveLogic` 的 `PlayerUri` 属性指定。

### 文件位置和结构
DefaultPlayer 由**两个 .model 文件**组成：

| 文件 | 路径 | 作用 |
|------|------|------|
| **Player.model** | `./Global/Player.model` | 基础模型。定义组件列表和属性链接 |
| **DefaultPlayer.model** | `./Global/DefaultPlayer.model` | 继承 Player (`BaseModelId: "player"`). 覆盖值 |

> **重要提示**：这两个文件都位于 `./Global/`。自定义脚本文件创建在 `./RootDesk/MyDesk/` 下。

### 通过 ModelBuilder 修补 DefaultPlayer
DefaultPlayer 通过同级的 `msw-general/scripts/model/msw_model_builder.cjs` 进行管理，而不是原始 JSON 编辑。
- 修改属性值：`ModelBuilder.read("./Global/DefaultPlayer.model").value(...)`
- 添加/删除组件：`component()` / `removeComponent()`
- 检查基础组件列表：`ModelBuilder.snapshot("./Global/Player.model")`

---

## 文件结构详情

### Player.model (基础)

```
Path: ./Global/Player.model
EntryKey: model://player
```

- `Components`：玩家上的默认组件完整列表（MOD.Core.* 原生组件）
- `Properties`：模型属性 → 组件属性链接定义（可在检查器中编辑的属性）
- `Values`：空（默认值由引擎提供）

### DefaultPlayer.model (覆盖)

```
Path: ./Global/DefaultPlayer.model
EntryKey: model://defaultplayer
BaseModelId: "player"
```

- `Components`：仅在 DefaultPlayer 上添加的组件（例如 `script.PlayerHit`, `script.PlayerAttack`）
- `Values`：覆盖设置值数组

---

## DefaultPlayer 默认组件列表

从 Player.model 继承的原生组件：

| 组件 | 作用 |
|-----------|------|
| **TransformComponent** | 位置、旋转、缩放 |
| **MovementComponent** | 移动速度和跳跃力控制 |
| **RigidbodyComponent** | 物理效果（重力、支撑点）、MapleStory 风格的移动 |
| **KinematicbodyComponent** | 在 RectTileMap 上的上下左右移动 |
| **SideviewbodyComponent** | 在 SideViewRectTileMap 上的横版移动 |
| **StateComponent** | 状态机（行走、跳跃、死亡等） |
| **AvatarRendererComponent** | 头像渲染、颜色、情绪 |
| **AvatarStateAnimationComponent** | 状态 → 头像动画映射 |
| **CostumeManagerComponent** | 服装/装备管理 → **有关详细信息，请参阅 `msw-avatar` 技能** |
| **CameraComponent** | 摄像机跟踪设置 |
| **PlayerControllerComponent** | 输入到动作的映射、条件处理 |
| **PlayerComponent** | 生命值、死亡/复活、PVP、地图移动 |
| **ChatBalloonComponent** | 聊天气泡 |
| **NameTagComponent** | 名字标签 |
| **DamageSkinSettingComponent** | 损伤皮肤 |
| **DamageSkinSpawnerComponent** | 损伤皮肤生成器 |
| **HitEffectSpawnerComponent** | 击中效果生成器 |
| **TriggerComponent** | 碰撞检测 |
| **InventoryComponent** | 背包 |

在 DefaultPlayer.model 中添加的脚本组件：

| 组件 | 作用 |
|-----------|------|
| **script.PlayerHit** | 玩家击中逻辑 |
| **script.PlayerAttack** | 玩家攻击逻辑 |

---

## 快速参考 — 关键组件

| 组件 | 作用 | 关键属性 / 方法 |
|------|------|--------------------------|
| **PlayerComponent** | 生命值、死亡/复活、PVP、地图移动 | `Hp`, `MaxHp`, `PVPMode`, `RespawnDuration`, `RespawnPosition`, `UserId`, `IsDead()`, `ProcessDead()`, `ProcessRevive()`, `MoveToMapPosition()` |
| **PlayerControllerComponent** | 输入 → 动作映射、条件控制 | `SetActionKey(key, actionName)`, `ActionAttack()`, `ActionJump()`, `LookDirectionX` |
| **MovementComponent** | 高级移动速度 / 跳跃接口 | `InputSpeed` (默认 1.0), `JumpForce` (默认 1), `Jump()`, `Stop()` |
| **RigidbodyComponent** | Maple 横版物理（重力 / 支撑点） | `Gravity`, `WalkAcceleration`, `WalkSpeed`, `AddForce()`, `IsOnGround()` |
| **KinematicbodyComponent** | 在 RectTile 地图上的上下左右移动 | (仅限 RectTile 地图模式) |
| **SideviewbodyComponent** | 在 SideViewRectTile 地图上的横版移动 | (仅限 SideViewRectTile 地图模式) |
| **AvatarRendererComponent** | 头像渲染 / 颜色 / 情绪 | `SetColor()`, `SetAlpha()`, `PlayEmotion()`, `PlayRate` |
| **StateComponent** | 状态机（行走/跳跃/死亡） | `CurrentStateName`, `ChangeState()`, DeadEvent/ReviveEvent |
| **NameTagComponent** | 名字标签 | `Name`, `FontSize`, `FontColor`, `NameTagRUID` |
| **ChatBalloonComponent** | 聊天气泡 | `Message`, `ChatModeEnabled`, `ShowDuration` |
| **CameraComponent** | 摄像机跟踪 | `DeadZone`, `SoftZone`, `Damping`, `ScreenOffset` |
| **TriggerComponent** | 碰撞检测 | `BoxSize`, `Offset`, CollisionGroup |

---

## DefaultPlayer Values 结构

`DefaultPlayer.model` 中 `Values` 数组中每个条目的格式：

```json
{
  "TargetType": "<component name> or null",
  "Name": "<property name>",
  "ValueType": {
    "$type": "MODNativeType",
    "type": "<type info>"
  },
  "Value": <value>
}
```

### TargetType 规则
- `null`：Player.model 的 Properties 中定义的模型属性（通过 Properties 链接到实际组件属性）
- `"MOD.Core.<ComponentName>"`：直接覆盖特定原生组件上的属性
- `"script.<ScriptName>"`：自定义脚本组件的属性

### 模型属性 (TargetType: null)

通过 Player.model 的 Properties 中定义的链接映射到实际组件属性。

| 模型属性名称 | 源组件.property | 描述 | 默认值 |
|---------------------|---------------------------|-------------|---------|
| speed | MovementComponent.InputSpeed | 移动速度 | 1.0 |
| jumpForce | MovementComponent.JumpForce | 跳跃高度 | 1.0 |
| walkAcceleration | RigidbodyComponent.WalkAcceleration | 加速 / 减速 | 1.0 |
| gravity | RigidbodyComponent.Gravity | 重力 | 1.0 |
| cameraDeadZone | CameraComponent.DeadZone | 摄像机死区 | `{x: 0.052, y: 0.08}` |
| cameraSoftZone | CameraComponent.SoftZone | 摄像机软区 | `{x: 0.268, y: 0.7}` |
| cameraDamping | CameraComponent.Damping | 摄像机平滑跟随 | `{x: 2.5, y: 3.9}` |
| cameraScreen | CameraComponent.ScreenOffset | 死区中心点 | `{x: 0.5, y: 0.655}` |
| cameraDutch | CameraComponent.DutchAngle | 摄像机旋转 | 0.0 |
| cameraOffset | CameraComponent.CameraOffset | 摄像机位置偏移 | `{x: 0.0, y: 0.0}` |
| message | ChatBalloonComponent.Message | 聊天气泡消息 | `""` |
| chatModeEnabled | ChatBalloonComponent.ChatModeEnabled | 是否处理聊天（例如显示气泡） | `true` |
| nameTag | NameTagComponent.Name | 名字标签 | `""` |
| damageSkinId | DamageSkinSettingComponent.DamageSkinId | 损伤皮肤类型 | DataRef |
| damageDelayPerAttack | DamageSkinSettingComponent.DelayPerAttack | 损伤延迟 | 0.05 |
| triggerBodyBoxSize | TriggerComponent.BoxSize | 碰撞检测区域大小 | `{x: 0.66, y: 0.7}` |
| triggerBodyBoxOffset | TriggerComponent.BoxOffset | 碰撞检测区域偏移 | `{x: 0.0, y: 0.35}` |
| triggerBodyColliderOffset | TriggerComponent.ColliderOffset | 碰撞器偏移 | `{x: 0.0, y: 0.35}` |
| maxHp | PlayerComponent.MaxHp | 最大生命值 | 1000 |

### 直接组件覆盖 (TargetType: 特定组件)

直接覆盖组件属性而不是通过模型属性链接的值：

| TargetType | Name | 描述 | 默认值 |
|------------|------|-------------|---------|
| MOD.Core.CameraComponent | ZoomRatioMax | 摄像机最大缩放比例 | 500.0 |
| MOD.Core.MovementComponent | JumpForce | 跳跃力（直接覆盖） | 1.0 |
| MOD.Core.MovementComponent | InputSpeed | 移动速度（直接覆盖） | 1.0 |
| script.PlayerHit | CollisionGroup | 击中碰撞组 | CollisionGroup ID |
| script.PlayerHit | BoxSize | 击中碰撞区域大小 | `{x: 0.45, y: 0.7}` |
| script.PlayerHit | ColliderOffset | 击中碰撞偏移 | `{x: 0.0, y: 0.35}` |

---

## 每种地图模式下的移动组件

> 有关 TileMapMode↔Body 映射表，请参阅 [`msw-general/references/platform.md`](../msw-general/references/platform.md) §4。根据地图模式，RigidbodyComponent / KinematicbodyComponent / SideviewbodyComponent 中有一个处于活动状态。

---

## 识别玩家（用于脚本参考）
- `entity.PlayerComponent ~= nil` → 实体是否为玩家
- `_UserService.LocalPlayer` → 我的玩家实体（仅客户端）
- `_UserService:GetUserEntityByUserId(userId)` → 特定用户的玩家实体

---

## 玩家实体运行时结构（根与子）

生成的玩家**不是**单个扁平实体。在运行时，引擎在玩家根下构建一个小型层次结构，并且**头像动作选择器位于孙辈实体上**——而不是在根上。这会影响你查找组件的方式以及如何触发头像姿势。

### 组件 → 实体映射

| 组件 | 存放位置 | 查找 |
|---|---|---|
| `PlayerComponent` | 根 | `player:GetComponent("PlayerComponent")` (或 `player.PlayerComponent`) |
| `StateComponent` | 根 | `player:GetComponent("StateComponent")` |
| `MovementComponent` | 根 | `player:GetComponent("MovementComponent")` |
| `AvatarRendererComponent` | 根 | `player.AvatarRendererComponent` |
| `AvatarStateAnimationComponent` | 根 | `player:GetComponent("AvatarStateAnimationComponent")` |
| `PlayerControllerComponent` | 根 | `player.PlayerControllerComponent` |
| **`AvatarBodyActionSelectorComponent`** | **根的孙辈**（在头像根下） | 无法通过 `player:GetComponent(...)` 访问——见下文 |
| **`AvatarFaceActionSelectorComponent`** | **根的孙辈** | 无法通过 `player:GetComponent(...)` 访问——见下文 |

`player:GetComponent("AvatarBodyActionSelectorComponent")` 返回 `nil`，并且 LSP 不会警告（签名是 `Component`，而不是可空类型）。只有在运行时才能看到失败。

### 如何访问选择器

```lua
-- 客户端上下文（推荐——直接 API）
local body  = self.Entity.AvatarRendererComponent:GetBodyEntity()
local face  = self.Entity.AvatarRendererComponent:GetFaceEntity()
local bodySelector = body and body:GetComponent("AvatarBodyActionSelectorComponent")
local faceSelector = face and face:GetComponent("AvatarFaceActionSelectorComponent")

-- 服务器或“双方”上下文（`GetBodyEntity` / `GetFaceEntity` 是客户端仅限）
local bodySelector = self.Entity:GetFirstChildComponentByTypeName(
    "AvatarBodyActionSelectorComponent", true)
```

> `AvatarRendererComponent:GetBodyEntity()` 和 `GetFaceEntity()` 声明为 `@ExecSpace("ClientOnly")`——从服务器端方法调用它们会返回 `nil`。使用 `GetFirstChildComponentByTypeName(name, recursive=true)` 作为跨端回退。

---

## 触发头像姿势 — 使用 `StateComponent`，永远不要直接写入选择器

一个活动的玩家每帧都有一个状态机运行：`PlayerControllerComponent` 评估输入/移动 → `StateComponent` 转换（空闲 / 移动 / 等）→ `AvatarStateAnimationComponent.ReceiveStateChangeEvent` 将其转换为 `BodyActionStateChangeEvent` → 选择器的 `ActionState` 被重写。

这意味着**直接写入 `AvatarBodyActionSelectorComponent.ActionState` 是静默覆盖**：该值适用于一帧，然后在下一个状态机帧将当前 `StateComponent` 状态映射回选择器，而你的写入就会消失。日志立即打印 `ActionState=Attack`，但在游戏模式下，姿势闪烁一帧然后消失。

### 正确的入口点

```lua
local state = self.Entity:GetComponent("StateComponent")
state:ChangeState("ATTACK")   -- ActionSheet 键是 UPPERCASE
```

状态键来自玩家的 ActionSheet。DefaultPlayer 随附**11 个 UPPERCASE 键**，每个键映射到默认动画：

| `StateComponent:ChangeState(...)` 键 | 默认动画 |
|---|---|
| `"IDLE"` | `stand` |
| `"MOVE"` | `walk` |
| `"ATTACK"` | `attack` |
| `"HIT"` | `hit` |
| `"CROUCH"` | `crouch` |
| `"FALL"` | `fall` |
| `"JUMP"` | `fall` |
| `"CLIMB"` | `rope` |
| `"LADDER"` | `ladder` |
| `"DEAD"` | `dead` |
| `"SIT"` | `sit` |

状态机在动作完成后自动返回 `IDLE`——无需手动恢复计时器。

> **大小写陷阱**：传递给 `ChangeState` 的**字符串键**是 **UPPERCASE** (`"ATTACK"`)。直接写入 `selector.ActionState` 的**枚举值**（NPC 路径——见下文）是 `MapleAvatarBodyActionState.Attack`——**PascalCase**，不同的 API 表面，但底层状态相同。字符串侧的大小写错误 (`"attack"` / `"Attack"`) 会静默地错过 ActionSheet 映射——没有警告。

### 当你可以直接写入选择器时

仅当实体**没有**运行 `PlayerControllerComponent` + `StateComponent` + `AvatarStateAnimationComponent` 堆栈时——例如使用头像渲染器进行视觉效果但没有输入控制器驱动状态机的 NPC / 怪物——`selector.ActionState = MapleAvatarBodyActionState.<Pose>` 才会固定。在 DefaultPlayer 形状的实体上，请通过 `StateComponent:ChangeState(...)` 而不是直接写入选择器。

### 关键服务概览（用于脚本参考）
| 服务 | 作用 | 关键 API |
|---------|------|---------|
| **_UserService** | 用户管理、进入/离开 | `LocalPlayer`, `UserEntities`, `GetUserEntityByUserId()`, UserEnterEvent/UserLeaveEvent |
| **_TeleportService** | 传送 / 地图移动 | `TeleportToEntity()`, `TeleportToMapPosition()`, `WarpUserToWorldAsync()` |
| **_CameraService** | 摄像机控制 | `SwitchCameraTo()`, `ZoomTo()`, `ZoomReset()` |
| **DefaultUserEnterLeaveLogic** | 用户进入/离开逻辑 | `PlayerUri` (玩家模型 ID), `StartPoint` (起始地图) |

---

## 如何修改 DefaultPlayer

### 修改属性值 (Values)

使用 `ModelBuilder.read()` 加载 `./Global/DefaultPlayer.model`，然后使用 `value()` 更新值。

**示例：将移动速度设置为 2.0**

```javascript
const { ModelBuilder } = require("../msw-general/scripts/model/msw_model_builder.cjs");

const b = ModelBuilder.read("./Global/DefaultPlayer.model");

b.value(null, "speed", 2.0, "float")
  .value("MovementComponent", "InputSpeed", 2.0, "float")
  .write("./Global/DefaultPlayer.model");
```

> **注意**：模型属性（`TargetType: null`, `Name: "speed"）和直接组件覆盖（`TargetType="MOD.Core.MovementComponent"`, `Name: "InputSpeed"）可以同时存在。通过 `value()` 一致地设置两者。

**示例：跳跃力 1.5 + 生命值 2000**

```javascript
const b = ModelBuilder.read("./Global/DefaultPlayer.model");

b.value(null, "jumpForce", 1.5, "float")
  .value("MovementComponent", "JumpForce", 1.5, "float")
  .value(null, "maxHp", 2000, "int")
  .write("./Global/DefaultPlayer.model");
```

### 添加新的 Values 条目

使用 `ModelBuilder.value(targetType, name, value, typeKey)`。构建器生成 `ValueType` 描述符；不要手动编写类型字符串。

常见的 `typeKey` 值：`bool`, `int`, `float`, `double`, `string`, `vector2`, `vector3`, `data_ref`, `collision_group`.

### 添加组件

在 `./Global/DefaultPlayer.model` 上使用 `component()`。

仅添加 Player.model 继承的组件。对于继承的原生组件（`PlayerComponent`, `MovementComponent`, `CameraComponent`, `StateComponent` 等），请使用 `value(...)` 覆盖值，而不是重新声明组件。`ModelBuilder` 在添加已从 `BaseModelId: "player"` 继承的组件时发出警告 (`M040`)。

**添加自定义脚本组件**：
```javascript
const b = ModelBuilder.read("./Global/DefaultPlayer.model");

b.component("script.MyCustomComponent")
  .write("./Global/DefaultPlayer.model");
```

> 自定义脚本 (.mlua) 必须创建在 `./RootDesk/MyDesk/` 下。先编写脚本，然后 Maker 刷新，然后使用构建器添加 `"script.<ScriptName>"`。

**添加非继承原生组件**：
```javascript
const b = ModelBuilder.read("./Global/DefaultPlayer.model");

b.component("SpriteRendererComponent")
  .write("./Global/DefaultPlayer.model");
```

### 删除组件

在 `DefaultPlayer.model` 上使用 `removeComponent()`。相关的 `Values` 条目由构建器删除。

> **注意**：从 Player.model 继承的组件（基础）不在 DefaultPlayer.model 的 Components 中。删除基础组件需要通过 `ModelBuilder` 修补 `Player.model`，通常不推荐。

---

## 常见陷阱（常见陷阱）

在 DefaultPlayer.model 中添加到 Components 和更改 Values 时常见的陷阱。

### 组件列表陷阱

| # | 陷阱 | 症状 | 解决方案 |
|---|---------|---------|------------|
| C1 | 你添加的 `script.XXX` 消失或不起作用 | 一个不在同一目录的匹配 `.codeblock` 元数据中注册的脚本组件在加载时被静默删除；如果保存在该状态下，它将永久丢失 | 在写入 `.mlua` 后，使用 **Maker Refresh** 以自动生成 `.codeblock`。或者在生成后立即通过 `entity:AddComponent("Name")` 运行时附加 |
| C2 | 重复添加已在 Player.model 上存在的原生组件（例如 `MOD.Core.MovementComponent`） | 只会发出一个重复组件警告，而不是阻止 → 工作区警告累积，行为变得非确定性 | 在添加之前检查基础组件列表（§65-89）。如果它已经存在，只需通过 Values 更改设置 |
| C3 | 删除 `script.PlayerHit` / `script.PlayerAttack` | 这是 DefaultPlayer 随附的唯一脚本。删除它们将消除击中免疫 / 攻击逻辑 | 如果目标是禁用，请切换脚本内的逻辑，或使用 Values 中的 Enable=false |
| C4 | 禁用 `AvatarRendererComponent` 并添加 `SpriteRendererComponent`（或其他渲染器交换） | 如果头像和精灵渲染器同时激活，你会得到 z-fighting / 服装未应用 | 仅在禁用头像后添加 Sprite（参见 §395 中的模式） |
| C5 | 自定义损伤路径仅减少 HP 属性（或仅广播损伤皮肤事件）——引擎击中/死亡管道从未触发 | 头像状态机对 `StateChangeEvent` 响应，而不是对属性写入响应。损伤数字 / 粒子渲染正常，但头像通过击中 / 死亡 / 复活保持空闲——静默的视觉错误，没有错误日志 | **首选**：通过 `HitComponent:OnHit(attacker, damage, isCrit, attackInfo, hitCount)` 路由损伤。`script.PlayerHit` 然后处理击中 / 死亡 / 复活转换。**当你必须手动驱动损伤**（通道 / 草药 / 脚本）：与击中姿势配对 `StateComponent:ChangeState("HIT")`，与死亡和复活周期配对 `PlayerComponent:ProcessDead()` / `ProcessRevive()`。不要只编辑 HP——头像不会响应。 |
| C6 | 在 `AvatarRendererComponent` 处于活动状态（例如 DefaultPlayer）的实体上设置 `SpriteRendererComponent.Color` / `FlipX` | 组件存在，`GetComponent` 返回非 nil，但精灵输出被头像渲染器自己的管道隐藏——颜色/翻转写入被静默忽略。在纯精灵渲染实体上，相同的模式有效，因此第一次尝试复制粘贴失败没有任何警告 | 使用 `AvatarRendererComponent:SetColor(r, g, b, a)`（0–1 浮点数）进行染色，使用 `:SetAlpha(a)` 进行淡出。两者都是 `ClientOnly`。对于朝向，通过 `MovementComponent.MoveDirection`（或游戏逻辑的朝向 API）而不是 `sprite.FlipX` 驱动角色 |

### Values 更改陷阱——仅 `jumpForce` / `speed` 需要额外注意

大多数 Values 条目是 `TargetType=null`（别名）形式，可以通过 `ModelBuilder.value(null, ...)` 设置。**只有以下两个字段是例外**——两者同时存在：

| 字段 | 别名条目 | 原生条目 |
|-------|-------------|--------------|
| 跳跃力 | `jumpForce` (`TargetType=null`) | `JumpForce` (`TargetType="MOD.Core.MovementComponent"`) |
| 移动速度 | `speed` (`TargetType=null`) | `InputSpeed` (`TargetType="MOD.Core.MovementComponent"`) |

在实体生成时，Values 按数组顺序应用，两者写入相同的原生字段；**原生条目在数组中出现在较后的位置，因此原生值优先**。

- 错误：只编辑别名侧（`jumpForce` / `speed`）→ 被后面的原生条目覆盖并忽略
- 正确：**将两者一致地编辑为相同的值**，或者只编辑原生侧（`JumpForce` / `InputSpeed`）

其他别名仅条目（`walkAcceleration`, `gravity`, 除 `cameraDeadZone` 外的摄像机相关, `nameTag`, `damageSkinId`, `damageDelayPerAttack`, `triggerBody*`, `maxHp` 等）可以按原样通过别名修改。

---

## 隐藏 DefaultPlayer

DefaultPlayer 的组件继承自基础模型，因此它们**无法被删除**。唯一的选择是通过 `Enable=false` 禁用它们。

### 组件保留/禁用分类

| 组件 | 完全隐藏 | 仅隐藏头像 | 备注 |
|-----------|:----------:|:----------------:|-------|
| TransformComponent | **保留** | **保留** | 必须保留 |
| PlayerComponent | **保留** | **保留** | 必须保留——禁用会导致进入失败 |
| StateComponent | **保留** | **保留** | 禁用会导致其他组件出错 |
| MovementComponent | **保留** | **保留** | 需要移动时保留 |
| CameraComponent | **保留** | **保留** | 需要摄像机时保留 |
| AvatarRendererComponent | **禁用** | **禁用** | 关键——禁用它本身会隐藏它 |
| AvatarStateAnimationComponent | **禁用** | **禁用** | |
| CostumeManagerComponent | **禁用** | **禁用** | |
| PlayerControllerComponent | **禁用** | 保留 | 取决于是否应阻止移动 |
| ChatBalloonComponent | **禁用** | **禁用** | |
| NameTagComponent | **禁用** | **禁用** | |
| DamageSkinSettingComponent | **禁用** | **禁用** | |
| DamageSkinSpawnerComponent | **禁用** | **禁用** | |
| HitComponent | **禁用** | **禁用** | |
| HitEffectSpawnerComponent | **禁用** | **禁用** | |
| TriggerComponent | **禁用** | **禁用** | |
| InventoryComponent | **禁用** | **禁用** | |
| RigidbodyComponent | **禁用** | 每种地图模式保留 | 在 MapleTile 地图上 |
| SideviewbodyComponent | **禁用** | 每种地图模式保留 | 在 SideViewRectTile 地图上 |
| KinematicbodyComponent | EnableShadow=false | EnableShadow=false | 仅删除阴影 |

### 构建器编辑——在 Values 中添加 Enable=false

通过 `ModelBuilder.value()` 设置组件值。对于尚无 Enable 条目的组件，构建器会添加一个。

```javascript
const { ModelBuilder } = require("../msw-general/scripts/model/msw_model_builder.cjs");

const b = ModelBuilder.read("./Global/DefaultPlayer.model");

b.enable("AvatarRendererComponent", false)
  .value("KinematicbodyComponent", "EnableShadow", false, "bool")
  .write("./Global/DefaultPlayer.model");
```

保存后，需要**Maker Refresh**。
