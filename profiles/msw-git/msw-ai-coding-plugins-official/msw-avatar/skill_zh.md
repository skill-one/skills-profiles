# MSW Avatar (Costume · Animation)

一个头像沿着两个轴进行管理。

- **Costume (外观)**: `MOD.Core.CostumeManagerComponent` — 哪些物品被装备（17个插槽）。
- **Animation (动作)**: `AvatarStateAnimationComponent` + `AvatarRendererComponent` — 播放哪个状态片段（14个默认状态 + 自定义动作）。

**直接编辑工作区文件**，然后调用 **`msw-maker-mcp` 的 `refresh` 工具**，以便编辑器能够拾取更改。

本文档首先涵盖 costume（基于文件编辑），然后是 animation（基于脚本）。

> **工作区路径规则**: 映射 `./map/`，UI `./ui/`，脚本和其他资源 `./RootDesk/MyDesk/`，全局模型例如 DefaultPlayer/Player `./Global/`。

---

## 目标位置

| 目标 | 文件要编辑 | 备注 |
|------|--------------|-------|
| **DefaultPlayer** | `./Global/DefaultPlayer.model` | 通过 `Values` 数组覆盖 `CostumeManagerComponent` 属性 |
| **Player (基础)** | `./Global/Player.model` | Costume 默认值通常在 **DefaultPlayer.model** 中被覆盖，而不是在这里 |
| **地图中放置的实体** (NPC、怪物等.) | `./map/{mapName}.map` | 该实体 `jsonString.@components` 中的 `CostumeManagerComponent` 块 |
| **仅引用自定义模型的实体** | 对应的 `.model` (例如在 `./RootDesk/MyDesk/` 下) | 当地图没有内联组件并且实体仅通过 `modelId` 绑定时，编辑模型侧 |

**读取 (相当于获取)**: 读取上述文件并检查与 `CostumeManagerComponent` 相关的字段 / `Values` 条目。如果 Maker MCP 已连接，您可以使用 `get_component` 作为运行时/编辑器快照辅助工具（参见 `msw-maker-mcp` 技能）。

**应用 (相当于设置)**: 将值写入文件，然后调用 **`refresh`**。

---

## 应用更改：MCP `refresh`

保存文件后，**必须**调用 `msw-maker-mcp` 服务器的 **`refresh` 工具**以同步 Maker 及其视觉状态。（参见 `msw-maker-mcp` 技能中的工具列表。）

---

## RUID (资源唯一 ID)

写入 costume 中的字符串是一个**头像物品 RUID**（通常是一个32字符的十六进制字符串）。

- **不要猜测或编造** RUID。使用 `msw-search` 技能查找它——对于头像 RUID 工作流（默认身体/头部、物品详情、渲染组合）请参阅 [`../msw-search/references/resource/avatar.md`](../msw-search/references/resource/avatar.md)；对于通用搜索请参阅 [`../msw-search/references/resource/search.md`](../msw-search/references/resource/search.md)；对于单个物品详情请参阅 [`../msw-search/references/resource/detail.md`](../msw-search/references/resource/detail.md)。
- 脚本 API `SetEquip(MapleAvatarItemCategory, itemRUID)` 和编辑器/模型中存储的值**是相同的 RUID 字符串**。
- `Custom*Equip` 插槽仅接受**纯 Guid**。任何前缀形式——包括 `thumbnail://<ruid>`——都会被静默拒绝，并且插槽将保持未装备状态（无错误，无警告）。`msw-search` 返回的 RUID 已经是纯 Guid；不要添加方案。参见 `msw-sprite-ruid` 技能，以了解更广泛的缩略图/图标规则。

---

## CostumeManagerComponent 概述

附加到**使用头像**的实体（玩家、NPC 等）。装备插槽作为 **17 个字符串属性**命名 `Custom*Equip`，并且从脚本中，您使用 `MapleAvatarItemCategory` 枚举通过 `GetEquip` / `SetEquip` 访问它们。

### 其他同步属性

| 属性 | 类型 | 描述 |
|----------|------|-------------|
| **UseCustomEquipOnly** | `boolean` (默认 `false`) | 当 `true` 时，**忽略用户帐户的默认 costume**，并且仅使用通过脚本/模型分配的 costume。当您想要在世界中锁定外观时，这很重要。 |
| **DefaultEquipUserId** | `string` | 克隆指定用户的装备，然后在上面应用自定义装备。**当前不在线的用户**也可以指定。如果该用户后来更改了装备，反射的外观可能会改变。 |
| **EquippedItems** | 只读 | 运行时实际装备信息。**无法从脚本修改**。 |

---

## 17 插槽 ↔ 属性 ↔ MapleAvatarItemCategory

`CostumeManagerComponent` 的 17 个**装备字符串字段**映射到引擎枚举 **`MapleAvatarItemCategory`**，如下所示。（枚举定义：参见 `Environment/NativeScripts/Enum/MapleAvatarItemCategory.d.mlua`。）

| # | Component 属性 (字符串 RUID) | MapleAvatarItemCategory | 备注 |
|---|----------------------------------|-------------------------|-------|
| 1 | **CustomBodyEquip** | Body (1) | 皮肤 / 身体 |
| 2 | **CustomHairEquip** | Hair (3) | 头发 |
| 3 | **CustomFaceEquip** | Face (4) | 脸部 / 脸型 |
| 4 | **CustomCapEquip** | Cap (5) | 帽子 |
| 5 | **CustomCapeEquip** | Cape (6) | 披风 |
| 6 | **CustomCoatEquip** | Coat (7) | 外套（上衣） |
| 7 | **CustomLongcoatEquip** | Longcoat (9) | 长外套——这是一个**同时占用上衣和下装插槽**的物品类别 |
| 8 | **CustomPantsEquip** | Pants (10) | 下装 |
| 9 | **CustomGloveEquip** | Glove (8) | 手套 |
| 10 | **CustomShoesEquip** | Shoes (12) | 鞋子 |
| 11 | **CustomOneHandedWeaponEquip** | OneHandedWeapon (13) | 单手武器 |
| 12 | **CustomTwoHandedWeaponEquip** | TwoHandedWeapon (14) | 双手武器——**同时占用单手武器插槽和副武器插槽** |
| 13 | **CustomSubWeaponEquip** | SubWeapon (15) | 副武器 |
| 14 | **CustomFaceAccessoryEquip** | FaceAccessory (16) | 脸部配件 |
| 15 | **CustomEyeAccessoryEquip** | EyeAccessory (17) | 眼睛配件 |
| 16 | **CustomEarAccessoryEquip** | EarAccessory (18) | 耳朵配件 |
| 17 | **CustomEarEquip** | Ear (19) | 耳朵（身体部位） |

### 没有直接 17 字段对应的 MapleAvatarItemCategory 枚举值

| MapleAvatarItemCategory | 描述 |
|-------------------------|-------------|
| **Head (2)** | 接近“不作为装备使用”——自动处理**以匹配身体颜色**。没有 `CustomHeadEquip` 字段。 |
| **Invalid (0)** | 用于检测错误 / 未定义值。 |
| **Shield (11)** | 根据枚举注释，它使用**副武器插槽**。在存储中，将其视为与 **CustomSubWeaponEquip** 互斥是最安全的。 |

---

## 互斥 / 插槽占用规则 (必须理解)

1. **Longcoat ↔ Coat + Pants**  
   **Longcoat** 设计为**同时占用 Coat 和 Pants 插槽**。装备长外套时，**将长外套 RUID 放在 `CustomLongcoatEquip`**，并**逻辑上解决与 coat/pants 的组合**——通常当长外套在使用时，留空 coat/pants 或避免冲突的视觉效果。

2. **Two-handed weapon ↔ One-handed weapon + sub-weapon**  
   **TwoHandedWeapon** **同时使用单手武器插槽和副武器插槽**。使用双手武器时，以 **`CustomTwoHandedWeaponEquip`** 为中心，并确保值没有也设置在单手/副武器上——避免重复装备。

3. **Shield ↔ Sub-weapon**  
   **Shield** 使用**副武器插槽**。不要期望另一个副武器与 **`CustomSubWeaponEquip`** 共存。

4. **空字符串 = 未装备**  
   与脚本中的 `SetEquip(category, "")` 类似，在文件中将字段保留为 **`""`** 意味着插槽未装备。

---

## DefaultPlayer.model — 将 costume 放入 `Values`

在 `./Global/DefaultPlayer.model` 的 **`ContentProto.Json.Values`** 数组中添加或修改一个条目。

- **TargetType**: `"MOD.Core.CostumeManagerComponent"`
- **Name**: 上表中从属的属性名称（例如 `CustomCapEquip`, `UseCustomEquipOnly`）
- **ValueType**: 遵循 `DefaultPlayer.model` 中已有的其他 `Values` 条目的相同模式。字符串使用 `System.String, mscorlib, ...`，布尔值使用 `System.Boolean, mscorlib, ...`
- **Value**: RUID 字符串或 `true` / `false`

如果相同的 `(TargetType, Name)` 已存在，**仅更新该条目**；否则**将一个新的对象追加到数组**。

### 字符串插槽示例 (仅结构；通过搜索替换 RUID)

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

## Map entities — 在 `.map` 文件中编辑

打开目标地图的**实体记录**，位于 `./map/` 下。

1. 在 `ContentProto.Entities` 数组中找到目标实体（通过名称/路径/ID）。
2. 在 `jsonString["@components"]` 中，找到具有 **`"@type": "MOD.Core.CostumeManagerComponent"`** 的对象。
3. 直接在该对象上编辑 **`Custom*Equip`**, **`UseCustomEquipOnly`**, **`DefaultEquipUserId`**, 等等。
4. 确认 `MOD.Core.CostumeManagerComponent` 也列在**`componentNames`** 字符串列表中，并且该列表与组件数组一致。

> 如果地图使用二进制格式，则根据工作区策略，编辑工具可能不同。当文件以 JSON 文本打开时，请按照上述结构进行操作。

---

## 将 `GET /v3/avatars` 结果映射到插槽

将 `GET /v3/avatars` 返回的物品的 **`category`** 字段映射到 `Custom*Equip` 属性。对于搜索方法，请参阅 `msw-search` 技能 → [`references/resource/avatar.md`](../msw-search/references/resource/avatar.md)。

| API `category` | `Custom*Equip` 属性 | `MapleAvatarItemCategory` |
|----------------|------------------------|--------------------------|
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
| `shield` | `CustomSubWeaponEquip` | Shield (11) — 共享 SubWeapon 插槽 |

---

## Avatar 资源搜索参考

- **`msw-search`** 技能 → [`references/resource/avatar.md`](../msw-search/references/resource/avatar.md): 关于 `GET /v3/avatars` 的详细信息（costume 搜索），默认身体/头部，`GET /v3/avatars/{ruid}`，渲染组合，等。
- 结合类别搜索和详情 API 来收集装备 RUID。

---

## Avatar 混色 / 透明度 (视觉重色)

对于任何具有 `AvatarRendererComponent` 附加的实体（DefaultPlayer、带有头像的 NPC、怪物等）上的颜色和透明度效果（击中闪光、幽灵淡出、调色板交换等），使用渲染器自己的方法。**`SpriteRendererComponent.Color` 和 `FlipX` 在头像实体上是静默无操作的**（即使 `isvalid(spriteRenderer)` 返回 true，头像渲染器也会覆盖精灵渲染器的输出）。

| 方法 | 签名 | 备注 |
|--------|-----------|-------|
| `SetColor` | `(r, g, b, a [, targetUserId]` | r/g/b/a 是 0~1 范围内的浮点数。整个头像重色。**客户端 ExecSpace.** |
| `SetAlpha` | `(a [, targetUserId]` | 浮点数，范围 0~1。独立透明度。**客户端 ExecSpace.** |
| `SetAvatarPartColor` | `(category, r, g, b, a [, targetUserId]` | 仅重色一个 `MapleAvatarItemCategory` 插槽。 |

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

对于**头像朝向/翻转**，使用 `MovementComponent` 上的朝向 API（例如 `MoveDirection`）而不是在精灵级别上写入翻转——相同的原因是静默无操作。
