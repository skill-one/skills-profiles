---
name: msw-sprite-ruid
description: SpriteRendererComponent.SpriteRUID（世界）和SpriteGUIRendererComponent.ImageRUID（UI）—原生RUID类型支持（精灵/动画剪辑直接播放），thumbnail://前缀用于将头像项/骨骼/动画剪辑渲染为静态缩略图，库存/商店/UI槽位中的头像项图标。使用场景：为精灵渲染组件分配任何RUID，将头像项或资源显示为缩略图或图标，在渲染器中直接使用动画剪辑，渲染库存项图标，在世界实体中显示缩略图。关键词：SpriteRUID，ImageRUID，thumbnail://，动画剪辑，RUID应用，RUID分配，缩略图，项图标，精灵RUID，RUID到渲染器
---

# MSW精灵RUID

为`SpriteRendererComponent.SpriteRUID`（世界）或`SpriteGUIRendererComponent.ImageRUID`（UI）分配RUID的规则。

---

## 本地类型支持

这两个组件可以直接接受`sprite`或`animationclip`的RUID，无需额外的animator组件。

| 组件 | 属性 | 运行时`.mlua`值形式 | 本地RUID类型 |
|---|---|---|---|
| `SpriteRendererComponent`（世界） | `SpriteRUID` | 普通字符串 | `sprite`, `animationclip` |
| `SpriteGUIRendererComponent`（UI） | `ImageRUID` | `DataRef("...")` | `sprite`, `animationclip` |

`ImageRUID`是一个`DataRef`：在运行时`.mlua`中，分配`DataRef(ruid)`。仅在`.ui` / `.model` JSON或构建器补丁数据中使用`{ DataId: ruid }`。`SpriteRUID`保持为普通字符串。

```lua
-- 世界：精灵或动画clip的RUID都有效
self.Entity.SpriteRendererComponent.SpriteRUID = ruid

-- UI：精灵或动画clip的RUID都有效
self.Entity.SpriteGUIRendererComponent.ImageRUID = DataRef(ruid)
```

未使用`thumbnail://`前缀分配的`skeleton` / `avataritem` RUID会**静默失败**（无错误，无渲染）。

---

## animationclip：单循环动画与多状态

- **单循环动画**（背景装饰、待机效果、道具）：直接将`SpriteRUID`或`ImageRUID`设置为`animationclip` RUID。
- **多状态**（站立/移动/攻击/受击/死亡）：使用`StateAnimationComponent` + `ActionSheet`。参考[`msw-general/references/monster.md`](../msw-general/references/monster.md)。

---

## `thumbnail://`前缀 — 从任何资源获取静态缩略图

在`SpriteRUID`或`ImageRUID`前添加`thumbnail://`以从任何资源渲染**静态缩略图**，适用于图标、预览图像和物品缩略图。

    thumbnail://<32字符十六进制RUID>

接受的类型：`sprite` · `animationclip` · `skeleton` · `avataritem`

```lua
-- 世界缩略图（任何资源类型）
self.Entity.SpriteRendererComponent.SpriteRUID = "thumbnail://" .. anyRuid

-- UI缩略图（任何资源类型）
self.Entity.SpriteGUIRendererComponent.ImageRUID = DataRef("thumbnail://" .. anyRuid)
```

### 主要用途：avataritem图标

`avataritem` RUID未使用`thumbnail://`前缀无法渲染。添加前缀后可作为物品图标用于背包槽位、商店列表和装备预览。

```lua
slotEntity.SpriteGUIRendererComponent.ImageRUID = DataRef("thumbnail://" .. avatarItemRuid)
```

使用`msw-search`技能（`searchAvatarItems`）搜索avatar item RUID。

---

## 常见陷阱

- 未添加前缀直接将`skeleton` / `avataritem`放入`SpriteRUID` / `ImageRUID` → 静默不可见。
- `thumbnail://`仅表示**静态图像**。若需动态动画，直接分配`animationclip` RUID（无需前缀）。
- 运行时`.mlua`使用`ImageRUID = DataRef("...")`；`{ "DataId": "..." }`对象形式仅用于`.ui` / `.model` JSON（前缀需**置于**`DataId内`，非单独字段）。运行时代码中**不要**使用表形式——LSP会因`DataRef`类型不匹配而拒绝。
- `CostumeManagerComponent.Custom*Equip`、`StateAnimationComponent.ActionSheet`和`SkeletonRendererComponent.SkeletonRUID`**不接受**`thumbnail://`。
- **不要**向已从`msw-search`获取为缩略图或图标图像的RUID添加`thumbnail://`前缀。前缀将源资源转为其缩略图——应用于已缩略的精灵在逻辑上重复。若搜索查询针对图标/缩略图图像并返回`sprite` RUID，直接分配该RUID无需任何前缀。
- **搜索**RUID请使用`msw-search`技能——`searchAvatarItems`用于avatar items；`searchResources`用于其他所有。
