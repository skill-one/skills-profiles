---
name: msw-avatar
description: MSW 头像管理——服装（CostumeManagerComponent，17个装备槽）+ 动画三层流水线（StateComponent → AvatarStateAnimationComponent → AvatarRendererComponent）。四级区分：状态键（大写）/ AvatarBodyActionStateName（小写）/ MapleAvatarBodyActionState 枚举 / 精灵动作ID（swingO1，shoot1）。通过 IsLegacy/ActionSheet/StateToAvatarBodyActionSheet 两种映射系统。PlayerControllerComponent 自动转换冲突通过 RemoveActionSheet/SetActionSheet/BodyActionStateChangeEvent 解决。适用于任何带有头像的实体（NPC、怪物等），不仅限于 DefaultPlayer。用于服装获取/设置、17个装备槽、动画状态映射、动作覆盖、武器特定攻击动作、自定义射击/施法/舞蹈动作。关键词：头像、服装、动画、状态、动作、射击、挥动、武器、装备、自定义动作、阻止自动播放、重映射。
---

# MSW Avatar (服装 · 动画)

一个头像沿着两个轴进行管理。

- **服装（外观）**: `MOD.Core.CostumeManagerComponent` — 装备哪些物品（17个槽位）。
- **动画（动作）**: `AvatarStateAnimationComponent` + `AvatarRendererComponent` — 播放哪个状态片段（14个默认状态 + 自定义动作）。

**直接编辑工作区文件**，然后调用 **`msw-maker-mcp` 的 `refresh` 工具**，以便编辑器拾取更改。

本文档首先介绍服装（基于文件编辑），最后介绍动画（基于脚本）。

> **工作区路径规则**: 地图 `./map/`，UI `./ui/`，脚本和其他资源 `./RootDesk/MyDesk/`，全局模型如 DefaultPlayer/Player `./Global/`。

---

## 目标在哪里编辑，按目标分类

| 目标 | 编辑文件 | 备注 |
|------|----------|-------|
| **DefaultPlayer** | `./Global/DefaultPlayer.model` | 通过 `Values` 数组覆盖 `CostumeManagerComponent` 属性 |
| **Player (基础)** | `./Global/Player.model` | 服装默认值通常在 **DefaultPlayer.model** 中被覆盖，而不是在这里 |
| **地图中放置的实体**（NPC、怪物等） | `./map/{mapName}.map` | 该实体 `jsonString.@components` 内的 `CostumeManagerComponent` 块 |
| **仅引用自定义模型的实体** | 对应的 `.model`（例如在 `./RootDesk/MyDesk/` 下） | 当地图没有内联组件且实体仅通过 `modelId` 绑定时，编辑模型侧 |

**读取（等同于获取）**: 读取上述文件并检查与 `CostumeManagerComponent` 相关的字段 / `Values` 条目。如果 Maker MCP 已连接，您可以使用 `get_component` 作为运行时/编辑器快照辅助工具（参见 `msw-maker-mcp` 技能）。

**应用（等同于设置）**: 将值写入文件，然后调用 **`refresh`**。

---

## 应用更改：MCP `refresh`

保存文件后，您**必须**调用 `msw-maker-mcp` 服务器的 **`refresh` 工具**以同步 Maker 及其视觉状态。（参见 `msw-maker-mcp` 技能中的工具列表。）

---

## RUID（资源唯一ID）

写入服装的字符串是一个**头像物品 RUID**（通常是一个32字符的十六进制字符串）。

- **不要猜测或编造** RUID。使用 `msw-search` 技能查找它——对于头像 RUID 工作流（默认身体/头部、物品详情、渲染组合）请参阅 [`../msw-search/references/resource/avatar.md`](../msw-search/references/resource/avatar.md)；对于通用搜索请参阅 [`../msw-search/references/resource/search.md`](../msw-search/references/resource/search.md)；对于单个物品详情请参阅 [`../msw-search/references/resource/detail.md`](../msw-search/references/resource/detail.md)。
- 脚本 API `SetEquip(MapleAvatarItemCategory, itemRUID)` 和编辑器/模型中存储的值是**相同的 RUID 字符串**。
- `Custom*Equip` 槽位仅接受**纯 Guid**。任何前缀形式——包括 `thumbnail://<ruid>`——都会被静默拒绝，并且该槽位将保持未装备状态（无错误，无警告）。`msw-search` 返回的 RUID 已经是纯 Guid；不要添加方案。参见 `msw-sprite-ruid` 技能为更广泛的缩略图/图标规则。

---

## CostumeManagerComponent 概述

附加到**使用头像**的实体（玩家、NPC 等）。装备槽位作为 17 个字符串属性暴露，命名为 `Custom*Equip`，并且从脚本中，您通过 `MapleAvatarItemCategory` 枚举使用 `GetEquip` / `SetEquip` 访问它们。

### 其他同步属性

| 属性 | 类型 | 描述 |
|------|------|-------|
| **UseCustomEquipOnly** | `boolean`（默认 `false`） | 当 `true` 时，**忽略用户账户的默认服装**，仅使用通过脚本/模型分配的服装。在您想要锁定世界内的外观时非常重要。 |
| **DefaultEquipUserId** | `string` | 克隆指定用户的装备，然后在上面应用自定义装备。**也可以指定当前不在线的用户**。如果该用户后来更改了装备，反射的外观可能会改变。 |
| **EquippedItems** | 只读 | 运行时的实际装备信息。**不能从脚本中修改**。 |

---

## 17 个槽位 ↔ 属性 ↔ MapleAvatarItemCategory

`CostumeManagerComponent` 的 17 个**装备字符串字段**映射到引擎枚举 **`MapleAvatarItemCategory`**，如下所示。（枚举定义：参见 `Environment/NativeScripts/Enum/MapleAvatarItemCategory.d.mlua`。）

| # | 组件属性（字符串 RUID） | MapleAvatarItemCategory | 备注 |
|---|--------------------------|-------------------------|-------|
| 1 | **CustomBodyEquip** | Body (1) | 皮肤 / 身体 |
| 2 | **CustomHairEquip** | Hair (3) | 头发 |
| 3 | **CustomFaceEquip** | Face (4) | 脸部 / 脸型 |
| 4 | **CustomCapEquip** | Cap (5) | 帽子 |
| 5 | **CustomCapeEquip** | Cape (6) | 披风 |
| 6 | **CustomCoatEquip** | Coat (7) | 上衣 |
| 7 | **CustomLongcoatEquip** | Longcoat (9) | 长外套——这是一个**同时占用上衣和下装槽位的物品类别** |
| 8 | **CustomPantsEquip** | Pants (10) | 下装 |
| 9 | **CustomGloveEquip** | Glove (8) | 手套 |
| 10 | **CustomShoesEquip** | Shoes (12) | 鞋子 |
| 11 | **CustomOneHandedWeaponEquip** | OneHandedWeapon (13) | 单手武器 |
| 12 | **CustomTwoHandedWeaponEquip** | TwoHandedWeapon (14) | 双手武器——**同时占用单手武器槽位和副武器槽位** |
| 13 | **CustomSubWeaponEquip** | SubWeapon (15) | 副武器 |
| 14 | **CustomFaceAccessoryEquip** | FaceAccessory (16) | 脸部配件 |
| 15 | **CustomEyeAccessoryEquip** | EyeAccessory (17) | 眼睛配件 |
| 16 | **CustomEarAccessoryEquip** | EarAccessory (18) | 耳朵配件 |
| 17 | **CustomEarEquip** | Ear (19) | 耳朵（身体部位） |

### 没有直接对应 17 个字段的枚举值

| MapleAvatarItemCategory | 描述 |
|-------------------------|-------|
| **Head (2)** | 接近“不作为装备使用”——**自动处理**以匹配身体颜色。没有 `CustomHeadEquip` 字段。 |
| **Invalid (0)** | 用于检测错误 / 未定义值。 |
| **Shield (11)** | 根据枚举注释，它使用 **SubWeapon 槽位**。在存储中，将其视为与 **CustomSubWeaponEquip** 互斥是最安全的。 |

---

## 互斥 / 槽位占用规则（必须理解）

1. **Longcoat ↔ Coat + Pants**  
   **Longcoat** 设计为**同时占用 Coat 和 Pants 槽位**。装备长外套时，**将长外套 RUID 放入 `CustomLongcoatEquip`**，并**逻辑上解决与外套/裤子的组合**——通常当长外套在使用时，留空外套/裤子或避免冲突的视觉效果。

2. **Two-handed weapon ↔ One-handed weapon + sub-weapon**  
   **TwoHandedWeapon** **同时使用单手武器槽位和副武器槽位**。使用双手武器时，以 **`CustomTwoHandedWeaponEquip`** 为中心，并确保值没有同时设置给单手/副武器——避免重复装备。

3. **Shield ↔ Sub-weapon**  
   **Shield** 使用**副武器槽位**。不要期望另一个副武器与 **`CustomSubWeaponEquip`** 共存。

4. **空字符串 = 未装备**  
   与脚本中的 `SetEquip(category, "")` 类似，在文件中将字段保留为 **`""`** 意味着该槽位未装备。

---

## DefaultPlayer.model — 将服装放入 `Values`

在 `./Global/DefaultPlayer.model` 的 **`ContentProto.Json.Values`** 数组中添加或修改一个条目。

- **TargetType**: `"MOD.Core.CostumeManagerComponent"`
- **Name**: 上述表中的属性名称（例如 `CustomCapEquip`, `UseCustomEquipOnly`）
- **ValueType**: 遵循 `DefaultPlayer.model` 中已有的其他 `Values` 条目相同的模式。字符串使用 `System.String, mscorlib, ...`，布尔值使用 `System.Boolean, mscorlib, ...`
- **Value**: RUID 字符串或 `true` / `false`

如果相同的 `(TargetType, Name)` 已存在，**仅更新该条目**；否则**将一个新的对象追加到数组中**。

### 字符串槽位示例（仅结构；通过搜索替换 RUID）

```json
{
  "TargetType": "MOD.Core.CostumeManagerComponent",
  "Name": "CustomCapEquip",
  "ValueType": {
    "$type": "MODNativeType",
    "type": "System.String, mscorlib, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089"
  },
  "Value": "PUT_32_HEX_RUID_HERE"
}
```

### UseCustomEquipOnly 示例

```json
{
  "TargetType": "MOD.Core.CostumeManagerComponent",
  "Name": "UseCustomEquipOnly",
  "ValueType": {
    "$type": "MODNativeType",
    "type": "System.Boolean, mscorlib, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089"
  },
  "Value": true
}
```

---

## 地图实体 — 在 `.map` 文件中编辑

在 `./map/` 下打开目标地图的**实体记录**。

1. 在 `ContentProto.Entities` 数组中找到目标实体（按名称/路径/ID）。
2. 在 `jsonString["@components"]` 中，找到具有 **`"@type": "MOD.Core.CostumeManagerComponent"`** 的对象。
3. 直接在该对象上编辑 **`Custom*Equip`**、**`UseCustomEquipOnly`**、**`DefaultEquipUserId`** 等。
4. 确认 `MOD.Core.CostumeManagerComponent` 也列在**`componentNames`** 字符串列表中，并且该列表与组件数组一致。

> 如果地图使用二进制格式，则编辑工具可能因工作区策略而异。当文件以 JSON 文本打开时，请遵循上述结构。

---

## 将 `GET /v3/avatars` 结果映射到槽位

将 `GET /v3/avatars` 返回项的 `category` 字段映射到 `Custom*Equip` 属性。对于搜索方法，请参阅 `msw-search` 技能 → [`references/resource/avatar.md`](../msw-search/references/resource/avatar.md)。

| API `category` | `Custom*Equip` 属性 | `MapleAvatarItemCategory` |
|----------------|----------------------|--------------------------|
| `body` | `CustomBodyEquip` | Body (1) |
| `hair` | `CustomHairEquip` | Hair (3) |
| `face` | `CustomFaceEquip` | Face (4) |
| `faceaccessory` | `CustomFaceAccessoryEquip` | FaceAccessory (16) |
| `eyeaccessory` | `CustomEyeAccessoryEquip` | EyeAccessory (17) |
| `earaccessory` | `CustomEarAccessoryEquip` | EarAccessory (18) |
| `cap` | `CustomCapEquip` | Cap (5) |
| `cape` | `CustomCapeEquip` | Cape (6) |
| `longcoat` | `CustomLongcoatEquip` | Longcoat (9) |
| `coat` | `CustomCoatEquip` | Coat (7) |
| `pants` | `CustomPantsEquip` | Pants (10) |
| `glove` | `CustomGloveEquip` | Glove (8) |
| `shoes` | `CustomShoesEquip` | Shoes (12) |
| `weapon` | `CustomOneHandedWeaponEquip` | OneHandedWeapon (13) |
| `twohandweapon` | `CustomTwoHandedWeaponEquip` | TwoHandedWeapon (14) |
| `subweapon` | `CustomSubWeaponEquip` | SubWeapon (15) |
| `shield` | `CustomSubWeaponEquip` | Shield (11) — 共享 SubWeapon 槽位 |

---

## 头像资源搜索参考

- **`msw-search`** 技能 → [`references/resource/avatar.md`](../msw-search/references/resource/avatar.md): 关于 `GET /v3/avatars`（服装搜索）、默认身体/头部、`GET /v3/avatars/{ruid}`、渲染组合等的详细信息。
- 结合类别搜索和详情 API 收集装备 RUID。

---

## 头像色调 / 透明度（视觉重色）

对于任何具有 `AvatarRendererComponent` 附加的实体（DefaultPlayer、携带头像的 NPC、怪物等）的颜色和透明度效果（击中闪光、幽灵淡出、调色板交换等），使用渲染器自己的方法。**`SpriteRendererComponent.Color` 和 `FlipX` 在头像实体上是静默无操作的**（即使 `isvalid(spriteRenderer)` 返回 true，头像渲染器也会覆盖精灵渲染器的输出）。

| 方法 | 签名 | 备注 |
|------|------|------|
| `SetColor` | `(r, g, b, a [, targetUserId])` | r/g/b/a 是 `0~1` 范围内的浮点数。整个头像染色。**客户端 ExecSpace。** |
| `SetAlpha` | `(a [, targetUserId])` | 浮点数在 `0~1`。独立透明度。**客户端 ExecSpace。** |
| `SetAvatarPartColor` | `(category, r, g, b, a [, targetUserId])` | 仅染色一个 `MapleAvatarItemCategory` 槽位。 |

```lua
@ExecSpace("Client")
method void FlashRed()
    local renderer = self.Entity.AvatarRendererComponent
    if isvalid(renderer) == false then return end
    renderer:SetColor(1.0, 0.25, 0.25, 1.0)   -- 红色闪光
    wait(0.1)
    renderer:SetColor(1.0, 1.0, 1.0, 1.0)     -- 恢复
end
```

对于**头像朝向/翻转**，使用 `MovementComponent`（例如 `MoveDirection`）上的朝向 API，而不是在精灵级别写入翻转——相同的原因会导致静默无操作。

---

## 头像动画——整体结构

头像动画通过**三层管道**流动。仅在一个层上工作会导致其他层覆盖您的更改并产生意外的动作。

```
[1] 输入 / 游戏逻辑
       │  PlayerControllerComponent · 脚本
       ▼
[2] StateComponent       ──── StateChangeEvent ────▶ AvatarStateAnimationComponent
       (例如 "ATTACK")          (CurrentStateName)        (StateToAvatarBodyActionSheet
                                                            或 ActionSheet 查找)
                                                                 │
                                                                 ▼
[3] AvatarRendererComponent ◀── BodyActionStateChange / ActionStateChanged ── 身体实体
       (实际精灵播放)
```

关键区别：

| 术语 | 格式 | 示例 |
|------|------|------|
| **状态键** | 大写 | `IDLE`, `MOVE`, `ATTACK`, `HIT`, `CROUCH`, `FALL`, `JUMP`, `CLIMB`, `LADDER`, `DEAD`, `SIT`, `ATTACK_WAIT` |
| **AvatarBodyActionStateName (值侧)** | 小写 | `stand`, `walk`, `attack`, `hit`, `crouch`, `fall`, `rope`, `ladder`, `dead`, `sit`, `alert`, `fly`, `blink`, `heal` |
| **MapleAvatarBodyActionState (枚举)** | PascalCase | `Stand`, `Walk`, `Attack`, `Hit`, `Crouch`, `Fall`, `Sit`, `Rope`, `Ladder`, `Dead`, `Blink`, `Fly`, `Heal`, `Alert`, `Invalid` |
| **CoreActionName / PartsActionName (实际精灵动作 ID)** | 小写 + 数字 | `stand1`, `walk1`, `swingO1`, `shoot1`, `prone`, `jump`, `alert`, 等。 |

> 常见混淆点：`"attack"` **不是状态**。状态是大写的 `ATTACK`，映射值是小写的 `attack`（=`MapleAvatarBodyActionState.Attack`），然后该值根据武器解析为精灵动作 ID，例如 `swingO1` / `shoot1`。从脚本中触发状态的是 `StateComponent:ChangeState("ATTACK")`（大写字符串）——`"Attack"` 或 `"attack"` 静默错过（无错误，状态 simply 没有改变）。

---

## AvatarStateAnimationComponent — 状态 ↔ 动作映射

`MOD.Core.AvatarStateAnimationComponent` 包含这两个系统。

| 属性 | 使用时 | 类型 | 备注 |
|------|------|------|------|
| `IsLegacy` | 在两个系统之间切换 | `boolean`（默认 `false`） | `true` = 使用 ActionSheet，`false` = 使用 StateToAvatarBodyActionSheet |
| `ActionSheet` | `IsLegacy = true`（旧） | `SyncDictionary<string, string>` | 状态→动画键，例如 `"ATTACK"` → `"attack"` |
| `StateToAvatarBodyActionSheet` | `IsLegacy = false`（新，默认） | `SyncDictionary<string, AvatarBodyActionElement>` | 例如 `"ATTACK"` → `{AvatarBodyActionStateName="attack", PlayRate=1.33}` |

### `StateToAvatarBodyActionSheet` 默认映射（当 IsLegacy=false 时的 11 个默认键）

| 键 (状态) | AvatarBodyActionStateName | PlayRate | 触发条件（当 PlayerControllerComponent 存在时） |
|----------|--------------------------|----------|---------------------------------------------------|
| `IDLE` | `stand` | 1.0 | 无输入 |
| `MOVE` | `walk` | 1.68 | 左右移动 |
| `ATTACK` | `attack` | 1.33 | **左 Ctrl**（攻击动作） |
| `HIT` | `hit` | 1.0 | 由 HitComponent 处理的击中 |
| `CROUCH` | `crouch` | 1.0 | 下箭头 |
| `FALL` | `fall` | 1.0 | 空中坠落 |
| `JUMP` | `fall` | 1.0 | 空格（跳跃动作） |
| `CLIMB` | `rope` | 1.0 | 进入绳索 |
| `LADDER` | `ladder` | 1.0 | 进入梯子 |
| `DEAD` | `dead` | 1.0 | 死亡 |
| `SIT` | `sit` | 1.0 | C（坐姿动作） |

> 注意，**状态键是大写**，而 `AvatarBodyActionStateName` 值是小写。

### 默认分辨率表：`MapleAvatarBodyActionState` → 实际动作ID

一个 `AvatarBodyActionStateName` 字符串（如 `"attack"`、`"stand"` 等）会被转换为 `MapleAvatarBodyActionState` 枚举，然后引擎将其解析为以下默认值，并合成一个 `ActionStateChangedEvent`。

| MapleAvatarBodyActionState | CoreActionName | PartsActionName | PlayRate | PlayType |
|----------------------------|----------------|-----------------|----------|----------|
| Stand | `stand1` / `stand2` | 相同 | 1 | ZigzagLoop |
| Walk | `walk1` / `walk2` | 相同 | 1 | Loop |
| Attack | `alert`（无武器时默认） | `alert` | 1 | Loop |
| Crouch | `prone` | `prone` | 1 | Loop |
| Fall | `jump` | `jump` | 1 | Loop |
| Sit | `sit` | `sit` | 1 | Loop |
| Rope | `rope` | `rope` | 1 | Loop |
| Ladder | `ladder` | `ladder` | 1 | Loop |
| Dead | `dead` | `stand1` | 1 | Loop |
| Blink | `blink` | `blink` | 1 | Loop |
| Fly | `fly` | `fly` | 1 | Loop |
| Hit | `alert` | `alert` | 1 | ZigzagLoop |
| Alert | `alert` | `alert` | 1 | ZigzagLoop |
| Heal | `heal` | `heal` | 1 | Loop |

> **当装备了武器时，`Attack` 会自动替换为与武器类型匹配的精灵动作ID**（见下一表格）。持单手剑会产生剑挥动作；持弓会产生弓射动作。

### 按武器区分的 `attack` 解析 — 候选精灵动作ID

当 `ATTACK` 被触发时，引擎会查看装备的武器（`MapleAvatarItemCategory`），并播放以下动作ID之一。

| 武器类型 | 候选 CoreActionName / PartsActionName |
|--------------|--------------------------------------------|
| 单手剑 /匕首 (`OneHandedWeapon`) | `swingO1`, `swingO2`, `swingO3`, `stabO1`, `stabO2` |
| 双手剑 / 锤 (`TwoHandedWeapon`) | `swingT1`, `swingT2`, `swingT3`, `stabT1`, `stabT2` |
| 弓 (`TwoHandedWeapon`，弓系) | `swingT1`, `swingT3`, **`shoot1`** |
| 法杖 / 棍子 | `swingO1`, `swingO2`, `swingO3` |
| 无武器（默认身体） | 无专用攻击片段 → 通过 `alert` 等 显示 |

> 即使在同一类别中，每个物品元数据使用的动作ID集也可能不同。上表列出了SDK指南（`_ActionNameLogic`）使用的代表性候选。

### PlayerControllerComponent 和自动状态添加

当 `MOD.Core.PlayerControllerComponent` 被附加到玩家实体时，以下状态会被自动添加到 `StateComponent` 并在关键输入时自动转换：

`MOVE`, `CLIMB`, `LADDER`, `CROUCH`, `JUMP`, `FALL`, `ATTACK`, `ATTACK_WAIT`, `SIT`

所以当默认玩家按下 Ctrl 时，ATTACK 状态会自动激活，并且**映射的攻击身体动作（= 每个武器的剑/弓/法杖挥动）会自动播放**——即使没有额外的脚本，剑也会挥动。

---

## 自动播放 ↔ 手动 ActionStateChangedEvent 冲突（★ 常见陷阱）

**症状**：即使通过脚本从 `ActionStateChangedEvent` 发送自定义动作（如 `shoot1`），**剑挥动作（或武器的默认攻击）仍然会播放**，或者你的自定义动作只显示一帧并立即被覆盖。

**原因**：当 `ATTACK` 处于活动状态时，`AvatarStateAnimationComponent` 会*持续*重新发送映射的 `attack` 身体动作。你的单次事件会被立即覆盖。

### 解决策略

| 策略 | 方法 | 使用场景 |
|----------|--------|-------------|
| **A. 移除映射** | 调用 `asac:RemoveActionSheet("ATTACK")` 来删除键。然后通过 `ActionStateChangedEvent` 直接播放动作。 | 当你想**完全替换**攻击动作的自定义动作（弓射、施法等） |
| **B. 更改映射** | 调用 `asac:SetActionSheet("ATTACK", "<Body Action name>")` 或将 `StateToAvatarBodyActionSheet["ATTACK"]` 改为一个不同的 `MapleAvatarBodyActionState`。 | 当你想切换到不同的**内置状态动画**（例如 ATTACK→heal） |
| **C. 强制重置** | 发送 `BodyActionStateChangeEvent` 并设置 `needResetAction=true`。 | 当你想**重新开始**相同的状态 |
| **D. 更换武器** | 用**弓 RUID** 替换 `CostumeManagerComponent` 的武器槽位。 | 当你只想改变攻击动作的**武器变体**（最直观的选项） |

#### 策略 A 示例 — 关闭剑挥动作，替换为弓射动作

```lua
@Component
script PlayerAttack extends AttackComponent

	@HideFromInspector
	property any Shape = nil

	@ExecSpace("ServerOnly")
	method void OnBeginPlay()
		self.Shape = BoxShape(Vector2.zero, Vector2.one, 0)

		-- 移除引擎在 ATTACK 时自动播放的攻击（=剑挥）映射
		local asac = self.Entity.AvatarStateAnimationComponent
		if isvalid(asac) then
			asac:RemoveActionSheet("ATTACK")
		end
	end

	@ExecSpace("ServerOnly")
	method void AttackNormal()
		-- ... 伤害计算 ...
		self:PlayShootAnimation()
	end

	@ExecSpace("Client")
	method void PlayShootAnimation()
		local body = self.Entity.AvatarRendererComponent:GetBodyEntity()
		if isvalid(body) == false then return end

		local event = ActionStateChangedEvent()
		event.CoreActionName = "shoot1"
		event.PartsActionName = "shoot1"
		event.PlayType = SpriteAnimClipPlayType.Onetime
		body:SendEvent(event)
	end

	@ExecSpace("ServerOnly")
	@EventSender("Self")
	handler HandlePlayerActionEvent(PlayerActionEvent event)
		if event.ActionName == "Attack" then
			self:AttackNormal()
		end
	end
end
```

> `RemoveActionSheet` / `SetActionSheet` 必须在**服务器**上调用才能同步，因为 `StateToAvatarBodyActionSheet` 是一个 `@Sync` 属性。

#### 策略 D 示例 — 通过 `CostumeManagerComponent` 装备弓

如果你在 `./Global/DefaultPlayer.model` 的 `Values` 中添加了一个弓 RUID，引擎会在 ATTACK 时自动选择 `shoot1` 动作，而无需更改映射。

```json
{
  "TargetType": "MOD.Core.CostumeManagerComponent",
  "Name": "CustomTwoHandedWeaponEquip",
  "ValueType": {
    "$type": "MODNativeType",
    "type": "System.String, mscorlib, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089"
  },
  "Value": "<弓 RUID — 通过 msw-search 获取>"
},
{
  "TargetType": "MOD.Core.CostumeManagerComponent",
  "Name": "UseCustomEquipOnly",
  "ValueType": {
    "$type": "MODNativeType",
    "type": "System.Boolean, mscorlib, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089"
  },
  "Value": true
}
```

---

## 14 个状态 vs 自定义动作 — 你自己触发哪个？

**14 个身体动作**（已知 `AvatarStateAnimationComponent` / `MapleAvatarBodyActionState`）和**该集合外的任意精灵动作ID**（例如 `swingO2`、`shoot1`、`dance`、`cast1`）会通过不同的路径处理。

### 引擎自动处理的 14 个身体动作（`MapleAvatarBodyActionState` 的成员）

这些都是可用作 `StateToAvatarBodyActionSheet`/`ActionSheet` 值的名字。一旦你将状态映射到其中一个，它就会自动播放。

| 身体动作名称 | 枚举 | 含义 |
|------------------|------|---------|
| `stand` | Stand | 空闲 |
| `walk` | Walk | 移动 |
| `attack` | Attack | 攻击（精灵ID由武器自动选择） |
| `hit` | Hit | 受击 |
| `crouch` | Crouch | 蹲伏 |
| `fall` | Fall | 落下 |
| `rope` | Rope | 抓绳 |
| `ladder` | Ladder | 梯子 |
| `dead` | Dead | 死亡 |
| `sit` | Sit | 坐下 |
| `heal` | Heal | 治疗 |
| `alert` | Alert | 警告 |
| `fly` | Fly | 飞行 |
| `blink` | Blink | 闪烁 |

### 其他任何动作 — 通过 `ActionStateChangedEvent` 直接播放

对于 14 个枚举成员外的任意精灵动作ID（例如 `shoot1`、`swingO2`、`cast1`、`throw1`、`dance`、`cheer`），请使用以下步骤。

**播放流程**

1. 从实体的 `AvatarRendererComponent`，调用**`GetBodyEntity()`** 获取**角色的身体实体**。动画事件发送到**身体实体**，而不是角色根节点。
2. 创建一个**`ActionStateChangedEvent`** 并填充其字段。
3. 通过 `body:SendEvent(event)` 发送它到身体实体。
4. 动画只需要被每个客户端看到，因此这通常作用域为**`@ExecSpace("Client")`**。游戏逻辑（伤害、投射物生成等）属于 `ServerOnly` 端。

**`ActionStateChangedEvent` 的主要字段**（构造函数：`ActionStateChangedEvent(coreActionName, partsActionName, playRate=1, playType=Loop, startFrameIndex=0, endFrameIndex=2147483647)`）

| 字段 | 类型 | 默认 | 描述 |
|-------|------|---------|-------------|
| `CoreActionName` | string | `""` | 在核心部件（身体）上播放的动画ID。**必需**（例如 `"shoot1"`、`"swingO1"`） |
| `PartsActionName` | string | `""` | 在子部件上播放的动画ID。**必需**——通常与 `CoreActionName` 相同 |
| `PlayRate` | float | `1` | 播放速度倍数（`1.0` = 正常速度，`1.5` = 1.5×） |
| `PlayType` | `SpriteAnimClipPlayType` | `Loop` | `Onetime` / `Loop` / `ZigzagLoop`。对于一次性动作使用 **`Onetime`** |
| `StartFrameIndex` | int32 | `0` | 开始帧（负值会被限制为 0） |
| `EndFrameIndex` | int32 | `2147483647` | 结束帧（如果超出总帧数会被限制） |

`SpriteAnimClipPlayType`:

| 值 | 含义 |
|-------|---------|
| `Onetime` | 播放一次后停止 |
| `Loop` | 0→end，重复 |
| `ZigzagLoop` | 0→end→0，重复 |

### `BodyActionStateChangeEvent` — 高级事件用于 14 个内置状态

直接指定一个 `MapleAvatarBodyActionState` 枚举值。你不需要记住每个武器的动作ID，并且可以通过 `needResetAction=true` 强制重启相同状态。

与 `ActionStateChangedEvent` 不同，`SendEvent` 的目标是**角色根实体（`self.Entity`）**，而不是身体实体。

```lua
local event = BodyActionStateChangeEvent()
event.ActionState = MapleAvatarBodyActionState.Fly
event.needResetAction = true
event.startFrameIndex = 1
event.endFrameIndex = 2
self.Entity:SendEvent(event)
-- 内部转换为 ActionStateChangedEvent("fly", "fly", 1, Loop, 1, 2) 并派发
```

| 字段 | 描述 |
|-------|-------------|
| `ActionState` | `MapleAvatarBodyActionState` 枚举（Stand/Walk/Attack/Hit/...） |
| `needResetAction` | 当为 `true` 时，即使状态已经在播放，也会从头开始强制重启 |
| `playRate` / `startFrameIndex` / `endFrameIndex` | 与 `ActionStateChangedEvent` 相同 |

**选择策略**

- **任意精灵动作ID**（`shoot1`、`swingO2`、`dance` 等）→ `ActionStateChangedEvent`（发送到身体实体）
- **14 个枚举状态之一**（Stand/Walk/Attack/...）→ `BodyActionStateChangeEvent`（发送到根实体）

### 示例 — 播放箭发射（`shoot`）动画

典型模式：在服务器上，攻击输入生成投射物；在客户端，播放 `shoot1` 动作。

```lua
@Component
script PlayerAttack extends Component

    property string ArrowModelId = "model://bc9f9d0e-2b5d-4b3b-a115-d857f85e9145"

    @HideFromInspector
    property integer ArrowCount = 0

    @ExecSpace("ServerOnly")
    method void FireArrow()
        if self.ArrowModelId == nil or self.ArrowModelId == "" then
            log_warning("PlayerAttack: ArrowModelId is not set")
            return
        end

        local playerController = self.Entity.PlayerControllerComponent
        local transform = self.Entity.TransformComponent
        if isvalid(playerController) == false or isvalid(transform) == false then
            return
        end

        local dirX = playerController.LookDirectionX
        if dirX == 0 then dirX = 1 end

        local worldPos = transform.WorldPosition
        local spawnPos = Vector3(worldPos.x + 0.35 * dirX, worldPos.y + 0.35, worldPos.z)

        self.ArrowCount += 1
        local arrowName = "PlayerArrow_" .. tostring(self.ArrowCount)

        local parent = self.Entity.CurrentMap
        if isvalid(parent) == false then
            parent = self.Entity.Parent
        end

        local arrow = _SpawnService:SpawnByModelId(self.ArrowModelId, arrowName, spawnPos, parent)
        if isvalid(arrow) == false then
            log_warning("PlayerAttack: failed to spawn arrow")
            return
        end

        local arrowProj = arrow.ArrowProjectile
        if isvalid(arrowProj) then
            arrowProj:Fire(Vector2(dirX, 0))
        end

        self:PlayShootAnimation()
    end

    @ExecSpace("Client")
    method void PlayShootAnimation()
        local avatarRenderer = self.Entity.AvatarRendererComponent
        if isvalid(avatarRenderer) == false then
            return
        end
        local body = avatarRenderer:GetBodyEntity()
        if isvalid(body) == false then
            return
        end

        local event = ActionStateChangedEvent()
        event.CoreActionName = "shoot1"
        event.PartsActionName = "shoot1"
        event.PlayRate = 1.5
        event.PlayType = SpriteAnimClipPlayType.Onetime
        body:SendEvent(event)
    end

    @ExecSpace("ServerOnly")
    @EventSender("Self")
    handler HandlePlayerActionEvent(PlayerActionEvent event)
        local ActionName = event.ActionName

        if ActionName == "Attack" then
            self:FireArrow()
        end
    end

end
```

### 决策流程

1. 你想播放的动作是否是**14 个内置状态**（`stand`、`walk`、`attack`、`hit`、`crouch`、`fall`、`rope`、`ladder`、`dead`、`sit`、`heal`、`alert`、`fly`、`blink`）之一？
   - **是** → 直接在 `AvatarStateAnimationComponent` 的对应槽位分配片段。不需要脚本。
   - **否** → 继续下方。
2. 对于自定义动作（如 `shoot1`、`cast1`、`dance`），创建一个**`ActionStateChangedEvent`** 并将 `SendEvent` 发送到由 `AvatarRendererComponent:GetBodyEntity()` 返回的**身体实体**。
3. 分割执行空间：输入处理和伤害计算在服务器（`ServerOnly`），**动画播放在客户端（`Client`）**。

### 常见错误

- **将 State key 与 AvatarBodyActionStateName（即枚举）混淆。** State key 为大写（`ATTACK`）；映射值（mapping Values）为小写（`attack`）。如果在 `StateToAvatarBodyActionSheet` 中交换 Key/Value，映射将静默失败。
- **未禁用自动播放的情况下仅发送 ActionStateChangedEvent。** 当按下 Ctrl 时，`ATTACK` 状态会自动激活，映射的攻击身体动作会立即覆盖你的事件。要使用自定义攻击动作，**必须**使用 `RemoveActionSheet("ATTACK")` 或 `SetActionSheet("ATTACK", "<desired motion>")` 清理映射。
- **`ActionStateChangedEvent` 的发送目标错误**：它必须是 `AvatarRendererComponent:GetBodyEntity()` 返回的**身体实体**。发送到 `self.Entity`（角色根节点）或组件不会播放。（反之，`BodyActionStateChangeEvent` 发送到**根实体**。）
- **在 DefaultPlayer 形状的实体上直接写入 `AvatarBodyActionSelectorComponent.ActionState`**（运行 `PlayerControllerComponent` + `StateComponent` + `AvatarStateAnimationComponent`）。控制器每帧重新评估地面/移动/输入并调用 `ChangeState` 进行状态转换；产生的 `StateChangeEvent → BodyActionStateChangeEvent` 会重绘选择器，并静默丢弃你的写入。应使用 `StateComponent:ChangeState("UPPERCASE_KEY")`。直接选择器写入仅在无该控制器堆栈的 NPC/怪物上生效。
- **尝试将任意状态名称放入 `AvatarStateAnimationComponent`。** 14 个枚举成员（`MapleAvatarBodyActionState`）之外的值（例如 `shoot`、`cast`、`dance`）将被忽略。自定义 ID 必须通过 `ActionStateChangedEvent` 传递。
- **忘记 `PartsActionName`。** 如果你只设置 `CoreActionName`，子部件（武器、帽子、斗篷等）将不会被解析，因此你可能会遇到**上半身移动而武器保持静止**的情况。使用与 `CoreActionName` 相同的值。
- **未设置 `PlayType`。** 默认值为 `Loop`，这会导致一次性动作无限重复。对于一次性动作，应显式设置 `SpriteAnimClipPlayType.Onetime`。
- **在客户端调用 `RemoveActionSheet`/`SetActionSheet`。** `StateToAvatarBodyActionSheet` 是一个 `@Sync` 属性——这些必须在**服务器**上调用以影响所有客户端。
- **忘记分离服务器/客户端执行空间。** 游戏逻辑（伤害、投射物）= `ServerOnly`；动画播放 = `Client`。将它们混在一起会导致每个客户端重复播放或视觉效果缺失。
- **未装备弓箭就期望出现弓箭动作。** 发射 `shoot1` 会将身体置于弓箭姿势，但如果在 `CustomTwoHandedWeaponEquip` 中未设置弓箭 RUID，**手部不会出现弓箭**。为获得自然视觉效果，应一起设置动作和武器。

---

## 相关技能

| 技能 | 目的 |
|-------|---------|
| **msw-defaultplayer** | `./Global/DefaultPlayer.model` / `Player.model` 结构及 `Values` 规则 |
| **msw-search** | RUID 查找，[`references/resource/avatar.md`](../msw-search/references/resource/avatar.md) |
| **msw-maker-mcp** | **`refresh`**，可选 `get_component` / `set_property`（与运行时调整结合时） |

---

## 摘要清单

### 成衣

1. 通过**资源搜索 / 角色参考文档**获取 RUID。
2. **DefaultPlayer / Player** → `./Global/*.model` 中的 `Values`（或基础模型定义）。
3. **映射实体** → `./map/*.map` 中目标实体的 `@components`。
4. 尊重**长外套 / 双持武器 / 盾牌 ↔ 副武器**的互斥规则。
5. 通过**`UseCustomEquipOnly`**决定是否忽略用户的默认成衣。
6. 保存后，调用 **`msw-maker-mcp` → `refresh`**。

### 动画

7. **区分状态键（大写）与身体动作名称（小写）。** 格式：`StateToAvatarBodyActionSheet["ATTACK"] = AvatarBodyActionElement("attack", 1.33)`。
8. 如果期望的动作在 14 个枚举身体动作（`stand`·`walk`·`attack`·`hit`·`crouch`·`fall`·`rope`·`ladder`·`dead`·`sit`·`heal`·`alert`·`fly`·`blink`）中，只需定义映射——完成。
9. 对于其他动作 ID（`shoot1`、`swingT3`、`dance` 等），创建一个 **`ActionStateChangedEvent`** 并将其发送到 `AvatarRendererComponent:GetBodyEntity()` 的结果。要在枚举内重启状态，使用 **`BodyActionStateChangeEvent`** + 根实体。
10. 填写所有四个字段——`CoreActionName` / `PartsActionName` / `PlayRate` / `PlayType`——对于一次性动作使用 **`SpriteAnimClipPlayType.Onetime`**。
11. **检查与自动状态转换的冲突。** 在具有 PlayerControllerComponent 的实体上，输入会自动触发 `MOVE/ATTACK/JUMP/...`——要使用自定义攻击，使用 **`RemoveActionSheet`** 或 **`SetActionSheet`** 清理冲突键（在服务器上调用）。
12. 将游戏逻辑放入 `@ExecSpace("ServerOnly")`，动画播放放入 **`@ExecSpace("Client")`**。
13. 如果你的目标是仅更改攻击动作的武器变体，最简单的路径是**交换 `CostumeManagerComponent` 的武器槽 RUID**（策略 D）。
