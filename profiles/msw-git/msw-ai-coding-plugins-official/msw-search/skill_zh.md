# MSW 搜索

MSW 有 **两个不同的搜索目标**：

1. **API 文档 & 实现指南** — 向量搜索用于描述、代码示例以及 `.d.mlua` 中缺失的相关 API。
2. **资源** — REST API 用于精灵、动画、声音、资源包和头像。获取 RUID 的唯一途径。

---

## 路由表

| 请求类型 | 前往部分 |
|----------|---------------|
| "如何实现这个功能？"、"给我一个示例"、"存在哪些相关 API？" | **文档搜索** |
| ".d.mlua 只包含签名；描述不足" | **文档搜索** |
| "我不知道 API 名称（语义搜索）" | **文档搜索** |
| "实现指南 / 最佳实践 / 模式" | **文档搜索** |
| "我需要一个 SpriteRUID"、"为怪物 / NPC / 背景 找一个精灵" | **资源搜索** → **从 `resource_pack` 开始** |
| "查找动画 / 声音 / 资源包" | **资源搜索** → **从 `resource_pack` 开始** |
| "此 RUID 的详细信息"、"相似资源" | **资源搜索** |
| "头像物品 / 默认头像查找" | **资源搜索** |
| "上传 / 列出 / 更新 / 删除我的自己的资源" | 直接调用 `msw-mcp` `asset_*` 工具 |
| "设置精灵轴心"、"设置 9 切片边框"、"UI RUID 的切片边界"、"资源属性" | 直接调用 `msw-mcp` `asset_update_resource_storage_info` |

> **★ 资源搜索默认 — 总是 `resource_pack` 优先**
>
> 除非用户 **明确** 要求单个精灵 / 动画剪辑 / 声音 / 头像物品（或直接命名非包 RUID），否则将 `resourceTypeFilter: ["resource_pack"]` 传递给 `searchResources`。一个包捆绑了一个资源的所有精灵 + 动画 + 声音，因此首先选择一个随机的 `sprite` 或 `animationclip` 通常会导致实体只有一个帧、没有动画设置或资产家族错误。
>
> 搜索包 → 钻入 `payload.elements` → 分配单个 RUID。
> 仅在明确意图的情况下切换类型："BGM 文件"、"仅单个精灵"、"头像物品"、"与这个 RUID 类似的动画剪辑" 等。

---

# 部分 1 — 文档搜索 (APIs & Guides)

通过 **`msw-mcp`** MCP 服务器进行向量搜索。提供 `.d.mlua` 中缺失的详细描述、代码示例、相关 API 和实现指南。

## 决策流程

```
需要 API 相关信息
│
├─ 检查签名 / 类型 / 属性 / 枚举
│   → 首先阅读 .d.mlua (最高优先级)
│   → 如果 .d.mlua 不足够，调用 msw-mcp
│     (代码示例、参数详细信息、相关 API 等)
│
├─ 实现指南 / 模式 / 最佳实践
│   → mlua_document_retriever
│
└─ 不知道 API 名称 (语义搜索)
    → mlua_api_retriever (以及/或 mlua_document_retriever 用于更广泛的范围)
```

---

## API 研究顺序

### 优先级 1 — .d.mlua (始终首先)

如果你知道 API 名称，**始终首先阅读 `.d.mlua`**。在这里可以准确确认签名、类型、属性、事件参数和枚举值。

**路径**: `Environment/NativeScripts/{Component,Service,Event,Enum,Logic,Misc}/Name.d.mlua`

| 情况 | 示例 |
|-----------|---------|
| 确认方法签名 | "TransformComponent 是否有 SetPosition？" |
| 属性类型 / 存在性 | "SpriteRendererComponent.RUID 的类型是什么？" |
| 事件参数结构 | "AttackEvent 构造函数参数是什么？" |
| 枚举值列表 | "BodyMoveType 的值有哪些？" |
| 方法存在性 | "SpawnService 有哪些方法？" |

### 优先级 2 — 向量搜索 (当 .d.mlua 不足够时)

`.d.mlua` 只包含签名，**缺少详细描述和示例**。当你需要以下任何内容时使用向量搜索。

| 情况 | MCP 工具 | 示例查询 |
|-----------|----------|---------------|
| 需要 **代码示例** | `mlua_api_retriever` | `AIComponent 示例`, `BehaviorTree 使用` |
| **参数详细信息** | `mlua_api_retriever` | `BadgeService GetBadgeInfosAndWait 参数` |
| **相关 API** 交叉引用 | `mlua_api_retriever` | `AttackComponent 相关`, `HitComponent` |
| **ScriptOverridable** 检查 | `mlua_api_retriever` | `AttackComponent CalcCritical 重写` |
| **不知道** API 名称 | 两个检索器 | `伤害计算`, `库存保存` |
| **"如何..."** 实现指南 | `mlua_document_retriever` | `如何制作库存系统` |
| **模式 / 最佳实践** | `mlua_document_retriever` | `碰撞检测最佳实践` |

---

## MCP 工具 (`msw-mcp`)

| 工具 | 描述 |
|------|-------------|
| **`mlua_api_retriever`** | 服务 / 组件 / Misc 等的 API 详细信息（签名、参数、示例）。传递 API/类/函数/组件名称。 |
| **`mlua_document_retriever`** | 编写手册、指南、MLua 使用和其他文档式材料。传递描述要实现的自然语言句子。 |

**失败时**: 如果 `msw-mcp` 工具调用出错，向用户显示失败并回退到 `.d.mlua`。不要猜测——说明你无法验证的内容。

**默认结果数量**: 请求 `3` 个结果，除非明确要求更广泛的探索。

---

## .d.mlua 与搜索 — 信息比较

`.d.mlua` 是一个类型桩 (~29 行)；搜索返回完整文档 (254+ 行)。

| 信息 | .d.mlua | 搜索 |
|-------------|:-------:|:------:|
| 方法签名 / 类型 | **O** | O |
| 属性声明 | **O** | O |
| 详细方法描述 (DetailDesc) | X | **O** |
| 代码示例 (AdditionalPageContent) | X | **O** |
| 每个参数描述 | X | **O** |
| 相关 API (SeeAlsoAPIs) | X | **O** |
| 相关指南 (SeeAlsoGuides) | X | **O** |
| ScriptOverridable 标志 | X | **O** |
| SyncDirection | 部分支持 | **O** |
| 本地化描述 (Ko/Ja/Es/Zh) | X | **O** |

---

## Maker Editor 语法 → .mlua 转换规则

搜索结果中的代码示例使用 **Maker Editor 语法**。它们必须在用于本地 `.mlua` 文件之前进行转换。

| 项目 | Maker Editor | .mlua 文件 | 备注 |
|------|--------------|------------|------|
| 重写声明 | `override integer CalcDamage(...)` | `method integer CalcDamage(...)` | `override` → `method` |
| 块 | `{ ... }` | `... end` | 大括号 → `end` |
| 执行空间 (自己的方法) | `[server only]` | `@ExecSpace("ServerOnly")` | 自定义方法：明确注释 |
| 执行空间 (重写) | `[server only]` 显示 / 编辑器中省略 | **与父级的 `@ExecSpace` 完全匹配** — 见下警告 | LEA-3014 如果不匹配 |
| 属性 | `Property: int32 Score = 0` | `@Sync property int32 Score = 0` | 如果同步，添加 `@Sync` |
| 类型 `int` | `int` | `integer` | C# int → mlua integer |
| 类型 `number` | `number` | `number` | 相同 (double) |
| 类型 `float` | `float` | `float` | 相同 (single) |

> `number` (64 位 double) 和 `float` (32 位 single) 可以相互赋值，但仍然是不同的类型。遵循 `.d.mlua` 声明。

> ⚠ **重写 ExecSpace 限制 — LEA-3014 `SignatureMismatch`**
>
> Maker Editor 经常 **隐藏** 父级的执行空间，并允许在 `override` 块上自由切换 `[server only]`。但在 `.mlua` 中，重写的 `@ExecSpace` 必须与 `.d.mlua` 中声明的父级 **字节完全相同**。如果父级没有 `@ExecSpace` (引擎默认 = `ExecSpace=All`)，重写也必须 **完全省略** `@ExecSpace`。
>
> 具体来说，AttackComponent / HitComponent 伤害挂钩 (`CalcDamage`, `CalcCritical`, `GetCriticalDamageRate`, `GetDisplayHitCount`, `IsAttackTarget`, `IsHitTarget`, `OnAttack`) 都是 `ExecSpace=All` 上游。添加 `@ExecSpace("ServerOnly")` 产生：
>
> ```
> [LEA-3014] SignatureMismatch : <Child>.CalcDamage[... (ExecSpace=ServerOnly)]
>   必须与被重写的 <Parent>.CalcDamage.[... (ExecSpace=All)] 匹配.
> ```
>
> 始终首先在 `.d.mlua` 中查找父级并逐字复制其注释块。详细信息：[`msw-scripting/SKILL.md` §9 "Method override → LEA-3014"](../msw-scripting/SKILL.md).

**转换示例** — 从搜索结果中的 AttackComponent：

```
-- Maker Editor 语法 (搜索结果)
override int CalcDamage(Entity attacker, Entity defender, string attackInfo) {
    return 50
}
override boolean CalcCritical(Entity attacker, Entity defender, string attackInfo) {
    return _UtilLogic:RandomDouble() < 0.3
}
```

```lua
-- 转换为 .mlua
-- ⚠ 父级 AttackComponent.CalcDamage / CalcCritical 声明没有 @ExecSpace
--   (ExecSpace=All). 在这里添加 @ExecSpace 会触发 LEA-3014 SignatureMismatch.
method integer CalcDamage(Entity attacker, Entity defender, string attackInfo)
    return 50
end

method boolean CalcCritical(Entity attacker, Entity defender, string attackInfo)
    return _UtilLogic:RandomDouble() < 0.3
end
```

---

# 部分 2 — 资源搜索 (精灵 / 动画 / 声音 / 资源包 / 头像)

REST API 用于搜索和浏览 MSW 资源。
永远不要猜测或编造 RUID — **始终通过此 API 获取**。

> **默认搜索类型 = `resource_pack`** — 见上表中路由表下的包优先规则。

## 访问 — 始终通过 `msw_resource_api.cjs`

此技能中的所有资源-API 调用都是通过 Node.js 包装器进行的

```
scripts/msw_resource_api.cjs
```

**不要手动组装 curl 命令**。包装器：

- 发送 UTF-8 JSON 正文，因此非 ASCII 查询（韩语 / 日语 / 中文 / 表情符号）避免了 `{"detail":"There was an error parsing the body"}` 失败模式，该模式会影响内联 `curl -d '...'`。
- URL 编码包含斜杠的路径参数（例如像 `npc/1013617.img` 这样的包 ID）。
- 零依赖（Node 18+ 内置的 `fetch` / `AbortController`）。
- 使用 **完全相同的 OpenAPI 字段名称** (`topK`, `resourceTypeFilter`, `categoryFilter`, `count`, …)。遗留名称如 `limit` / `types` / `categories` 由服务器静默忽略。

使用它的两种方式：

```bash
# 1) CLI — 从 shell 发起一个调用。输出格式化 JSON。
node scripts/msw_resource_api.cjs \
    search "orange mushroom" --resource-type resource_pack --category npc --topK 3

# 发现可用的子命令:
node scripts/msw_resource_api.cjs --help
```

```js
// 2) require — 在已经处于 Node.js 上下文时首选。
const {
  searchResources, searchAvatarItems, findSimilarResources,
  getResource, getResourcesBatch, getResourceTags,
  listResources, randomResources, findPacksContaining,
  listAvatars, getAvatarDefaults,
} = require('./scripts/msw_resource_api.cjs');

const result = await searchResources("orange mushroom", {
  resourceTypeFilter: ["resource_pack"],
  categoryFilter: ["npc"],
  topK: 3,
});
```

## 包装器函数 ↔ 端点映射

| 包装器函数 | CLI 子命令 | 端点 |
|------------------|----------------|----------|
| `searchResources` | `search` | `POST /v3/search/resources` |
| `searchAvatarItems` | `search-avatar` | `POST /v3/search/resources` (头像模式) |
| `findSimilarResources` | `similar` | `GET /v3/search/resources/similar/{ruid}` |
| `getResource` | `get` | `GET /v3/resources/{ruid}` (适用于精灵 / 动画剪辑 / **资源包（元素已填充**） / **头像物品**） |
| `getResourcesBatch` | `batch` | `POST /v3/resources/batch` |
| `getResourceTags` | `tags` | `GET /v3/resources/tags/{ruid}` |
| `listResources` | `list` | `GET /v3/resources` (Qdrant Scroll, 不透明字符串 `offset` 光标) |
| `randomResources` | `random` | `GET /v3/resources/random` |
| `findPacksContaining` | `packs` | `GET /v3/resources/packs/{ruid}` (列出包含给定 RUID 的资源包 — 路径参数是 32 位十六进制 RUID，不是包 ID) |
| `listAvatars` | `avatars` | `GET /v3/avatars` |
| `getAvatarDefaults` | `avatar-defaults` | `GET /v3/avatars/defaults` |

> **不存在 `/v3/avatars/{ruid}` 端点。** 要检查头像物品
> (color_hex, 组成员，…), 调用 `getResource(ruid)` — `/v3/resources/{ruid}` 端点像任何其他资源一样返回头像物品详细信息。

## 分页 — 同一名称，两种风格

`nextOffset` 出现在每个列表式响应中，但根据端点不同，含义也不同。将值循环到错误的端点会静默地表现异常。

| 端点 | `nextOffset` 类型 | 含义 | 如何分页 |
|---|---|---|---|
| `POST /v3/search/resources` (搜索) | **整数** | 项目偏移 (0-based) | 将它作为 `offset` (数字) 传递回去 |
| `GET /v3/search/resources/similar/{id}` (相似) | **整数** | 项目偏移 | 相同 |
| `GET /v3/resources` (列表) | **不透明 UUID 字符串** | Qdrant Scroll 光标 | 将字符串作为 `offset` 传递回去。**流结束 = `null`** |
| `GET /v3/resources/packs/{ruid}` (包) | **不透明 UUID 字符串** | 相同光标 | 相同 |
| `GET /v3/resources/random` | n/a | 无分页 | — |

**规则**:

1. 永远不要将 `list` 光标提供给 `search` 调用（反之亦然）——服务器会忽略形状不正确的值并返回第一页。
2. 在 **第一页** 中，完全省略 `offset`。将整数 `0` 传递给 `list` / `packs` 被解释为光标，并且会返回 **零项**（静默失败）。
3. 当响应返回 `nextOffset: null` (列表 / 包) 或返回的项目少于 `topK` (搜索 / 相似) 时停止分页。

## 端点摘要

| 方法 | 端点 | 目的 |
|--------|----------|---------|
| POST | `/v3/search/resources` | 自然语言语义搜索（包括通过 `resourceTypeFilter: ["avataritem"]` 的头像物品） |
| GET | `/v3/search/resources/similar/{ruid}` | 查找相似资源 |
| GET | `/v3/resources/{ruid}` | 单个资源详细信息（精灵 / 动画剪辑 / **资源包（元素已填充**） / **头像物品**） |
| POST | `/v3/resources/batch` | 批量获取多个资源 |
| GET | `/v3/resources/tags/{ruid}` | AI 生成的多语言标签 |
| GET | `/v3/resources` | 列出资源（Qdrant Scroll, 不透明字符串 `offset` 光标） |
| GET | `/v3/resources/random` | 随机资源推荐 |
| GET | `/v3/resources/packs/{ruid}` | 列出包含给定 RUID 的资源包 — 路径参数是 32 位十六进制 RUID，不是包 ID |
| GET | `/v3/avatars` | 列出所有头像物品（缓存的） |
| GET | `/v3/avatars/defaults` | 默认头像身体 / 头部 RUID |

> 单个头像物品详细信息使用 `/v3/resources/{ruid}`（不存在 `/v3/avatars/{ruid}` 端点）。

---

## 资源路由指南

> **★ 不确定时，首先搜索 `resource_pack`。** 以下行标记为明确非包意图的除外。

| 情况 | 包装器调用 (CLI 子命令) | 参考文件 |
|-----------|-------------------------------|----------------|
| "查找一个史莱姆 / 橙色蘑菇 / 怪物 / NPC / 物品 / 背景 / 地图资源" (默认 — 未指定类型) | `searchResources(query, { resourceTypeFilter: ["resource_pack"], topK: 3 }` (`search ... --resource-type resource_pack`) | [`references/resource/search.md`](references/resource/search.md) |
| "查找一个 **单个精灵** / 单个图像" (用户明确要求精灵) | `searchResources(query, { resourceTypeFilter: ["sprite"], ... })` | [`references/resource/search.md`](references/resource/search.md) |
| "查找一个 **单个动画剪辑**" (用户明确要求动画) | `searchResources(query, { resourceTypeFilter: ["animationclip"], ... })` | [`references/resource/search.md`](references/resource/search.md) |
| "查找一个 **视觉效果 / 粒子 / 击打特效**" | `searchResources(query, { resourceTypeFilter: ["animationclip","sprite"], categoryFilter: ["skill","mob","etc"] })` — 注意：`effect` 这里表示 **音频**，不是视觉效果 | [`references/resource/search.md`](references/resource/search.md) |
| "查找一个 **声音 / BGM / 声音 / 声音效果**" (音频) | `searchResources(query, { resourceTypeFilter: ["bgm"\|"voice"\|"effect"], ... })` — `effect` 资源类型 = 声音效果 (音频) | [`references/resource/search.md`](references/resource/search.md) |
| "查找一个 **背景 / 地图瓦片 / 道具**" | `searchResources(query, { resourceTypeFilter: ["sprite","animationclip"], categoryFilter: ["background","object"] })` — 索引中没有 `map` 类别 | [`references/resource/search.md`](references/resource/search.md) |
| "查找一个服装 / 帽子 / 裤子 / 鞋子 / 武器 (头像物品)" | `searchAvatarItems(...)` (`search-avatar`) | [`references/resource/search.md`](references/resource/search.md) (头像物品搜索部分) + [`references/resource/avatar.md`](references/resource/avatar.md) |
| "这个怪物像这个一样还有其他怪物吗?" | `findSimilarResources(ruid, ...)` (`similar`) | [`references/resource/search.md`](references/resource/search.md) |
| "RUID abc123 的详细信息" (任何类型包括头像物品和资源包) | `getResource(ruid)` (`get`) | [`references/resource/detail.md`](references/resource/detail.md) |
| "显示怪物精灵列表" | `listResources(...)` (`list`) | [`references/resource/browse.md`](references/resource/browse.md) |
| "哪些资源包包含这个 RUID?" | `findPacksContaining(ruid, ...)` (`packs`) | [`references/resource/browse.md`](references/resource/browse.md) |
| "浏览所有头像物品" | `listAvatars(...)` (`avatars`) | [`references/resource/avatar.md`](references/resource/avatar.md) |

### 典型工作流程 (包优先)

```
1. searchResources(query, { resourceTypeFilter: ["resource_pack"], topK: 3 })
   → 获取资源包 RUID（或像 "npc/9072309.img" 这样的包 ID）
   → 仅在明确用户意图时切换类型，或者当 0 个包匹配时回退
2. getResource(id)
   → 资源包：payload.elements 已预填充元素 payload
                    (精灵 / 动画剪辑 / 声音 RUID 存活在这里)
   → 头像物品：payload 包含 color_hex / 组元数据
3. 从 payload.elements 中选择元素并为其 RUID 分配到
   SpriteRendererComponent.SpriteRUID / StateAnimationComponent.ActionSheet
   (或者通过 `msw-avatar` 中的槽映射分配头像物品 RUID)

> **不要** 调用 `findPacksContaining(packId)` 来 "打开" 包 — 该端点接受 32 位十六进制 RUID 并返回 **包含该 RUID 的包**，而不是包的内容。使用 `getResource(packId)` 获取包内容。

> **对于每个端点的请求/响应的详细信息，请参考 `references/resource/` 下的文件。**

---

## 精灵朝向 — 大多数资源面向左侧

大多数 MSW 精灵 / 动画剪辑 / 资源包资源 — 特别是 `mob`, `npc` 和玩家角色 — 都是 **面向左侧** 编写的，因此一个新的 `SpriteRendererComponent` 渲染左侧，除非你翻转它。

| 情况 | 该怎么做 |
|-----------|-----------|
| 生成一个应该面向 **右侧** 的实体 | 在 `SpriteRendererComponent` 上设置 `FlipX = true` (默认是 `false` = 作者编写的左侧面向) |
| 自定义 AI / 使用 `MovementComponent:MoveToDirection` 的追逐 | 在方向改变时更新 `FlipX`：`sprite.FlipX = velocity.x > 0` (右侧 ⇒ 翻转) |
| 怪物模型 / 怪物碰撞器对齐 | 翻转 `TransformComponent.Scale.x` 考虑 `FlipX` 以确保精灵和碰撞器保持对齐；见 [`msw-general/references/monster.md`](../msw-general/references/monster.md) |
| 原生 `AIChaseComponent` / `AIWanderComponent` | 引擎根据移动自动翻转 — 无需操作 |
| 俯视 (`RectTile`) 移动 | 每个轴分别决定：通常在 `dx > 0` 时翻转；具有上下帧的精灵需要使用 `StateAnimationComponent` 动作集 |
| `_EffectService:PlayEffect(...)` 应该面向右侧 | 在 `options` 表中传递 `FlipX = true` |
| 玩家附加效果必须跟随玩家的朝向 | 在 `PlayEffect` 选项中使用 `SyncFlip = true`，或者读取 `PlayerControllerComponent.LookDirectionX` |
| 资源是面向右侧编写的（很少见） | 通过 `GET /v3/resources/{ruid}` 检查 `payload.thumbnail` 并翻转该规则的规则 |

```lua
-- 自定义侧视追逐：翻转精灵以匹配移动方向
local sprite = self.Entity.SpriteRendererComponent
local selfX = self.Entity.TransformComponent.WorldPosition.x
local dx    = targetPos.x - selfX
if dx ~= 0 then
    sprite.FlipX = dx >  |---|
```

> **合理性检查** — 左侧面向惯例不是合同性的。打开 `payload.thumbnail` 从 `GET /v3/resources/{ruid}` 以确认。
>
> **不要使用 `TransformComponent.Scale.x` 作为通用的渲染器翻转** — 对于玩家 / 效果 / 非怪物渲染器，使用 `SpriteRendererComponent.FlipX`。**怪物例外**：怪物模型应该翻转 `TransformComponent.Scale.x` 以确保精灵和碰撞器保持对齐。相关：[`msw-combat-system/SKILL.md` "方向检查 ★"](../msw-combat-system/SKILL.md), [`msw-general/references/monster.md`](../msw-general/references/monster.md).
