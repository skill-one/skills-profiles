# MSW 精灵 RUID

为 `SpriteRendererComponent.SpriteRUID`（世界）或 `SpriteGUIRendererComponent.ImageRUID`（UI）分配 RUID 的规则。

---

## 本地类型支持

这两个组件可以直接接受 `sprite` 或 `animationclip` RUID，无需额外的 animator 组件。

| 组件 | 属性 | 运行时 `.mlua` 值形式 | 本地 RUID 类型 |
|---|---|---|---|
| `SpriteRendererComponent`（世界） | `SpriteRUID` | 普通字符串 | `sprite`, `animationclip` |
| `SpriteGUIRendererComponent`（UI） | `ImageRUID` | `DataRef("...")` | `sprite`, `animationclip` |

`ImageRUID` 是一个 `DataRef`：在运行时 `.mlua` 中，分配 `DataRef(ruid)`。仅在 `.ui` / `.model` JSON 或构建器补丁数据中使用 `{ DataId: ruid }`。`SpriteRUID` 仍然是普通字符串。

```lua
-- 世界：精灵或动画剪辑 RUID 都有效
self.Entity.SpriteRendererComponent.SpriteRUID = ruid

-- UI：精灵或动画剪辑 RUID 都有效
self.Entity.SpriteGUIRendererComponent.ImageRUID = DataRef(ruid)
```

未使用 `thumbnail://` 前缀分配的 `skeleton` / `avataritem` RUID 会**静默失败**（无错误，无渲染）。

---

## animationclip：单循环动画 vs 多状态

- **单循环动画**（背景装饰、待机效果、道具）：直接将 `SpriteRUID` 或 `ImageRUID` 设置为 `animationclip` RUID。
- **多状态**（站立 / 移动 / 攻击 / 受击 / 死亡）：使用 `StateAnimationComponent` + `ActionSheet`。参考 [`msw-general/references/monster.md`](../msw-general/references/monster.md)。

---

## `thumbnail://` 前缀 — 从任何资源获取静态缩略图

在 `SpriteRUID` 或 `ImageRUID` 前缀添加 `thumbnail://` 以从任何资源渲染**静态缩略图**——适用于图标、预览图像和物品缩略图。

    thumbnail://<32位十六进制 RUID>

接受的类型：`sprite` · `animationclip` · `skeleton` · `avataritem`

```lua
-- 世界缩略图（任何资源类型）
self.Entity.SpriteRendererComponent.SpriteRUID = "thumbnail://" .. anyRuid

-- UI 缩略图（任何资源类型）
self.Entity.SpriteGUIRendererComponent.ImageRUID = DataRef("thumbnail://" .. anyRuid)
```

### 主要用途：avataritem 图标

`avataritem` RUID 未使用 `thumbnail://` 前缀无法渲染。添加前缀后，它们成为背包槽位、商店列表和装备预览的物品图标。

```lua
slotEntity.SpriteGUIRendererComponent.ImageRUID = DataRef("thumbnail://" .. avatarItemRuid)
```

使用 `msw-search` 技能（`searchAvatarItems`）搜索 avatar item RUID。

---

## 常见陷阱

- 未添加前缀直接将 `skeleton` / `avataritem` 放入 `SpriteRUID` / `ImageRUID` → 静默不可见。
- `thumbnail://` 仅等于**静态**图像。动态动画直接分配 `animationclip` RUID（无需前缀）。
- 运行时 `.mlua` 使用 `ImageRUID = DataRef("...")`；`{ "DataId": "..." }` 对象形式仅用于 `.ui` / `.model` JSON（前缀**包含**在 `DataId` 内，不是单独字段）。运行时代码中不要使用表形式——LSP 会因 `DataRef` 类型不匹配而拒绝。
- `CostumeManagerComponent.Custom*Equip`、`StateAnimationComponent.ActionSheet` 和 `SkeletonRendererComponent.SkeletonRUID` **不接受** `thumbnail://`。
- 不要向已从 `msw-search` 获取的**缩略图或图标** RUID 添加 `thumbnail://`。前缀将资源转换为缩略图——对已缩略的精灵应用前缀在逻辑上重复。如果搜索查询针对图标/缩略图并返回 `sprite` RUID，直接分配该 RUID 而无需前缀。
- 搜索 RUID 使用 `msw-search` 技能——`searchAvatarItems` 用于 avatar items；`searchResources` 用于其他所有内容。
