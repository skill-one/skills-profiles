---
name: msw-search
description: MSW搜索集成 — (1) 通过msw-mcp MCP服务器（mlua_api_retriever / mlua_document_retriever）对API文档和实现指南进行向量搜索，(2) 对资源（精灵 / 动画 / 音效 / 资源包 / 头像）进行REST API搜索。用于“查找.d.mlua中未包含的详细信息、示例或相关API”、“需要SpriteRUID”、“怪物精灵”、“背景图像”、“查找音效”、“头像物品查询”等。关键词：文档搜索、API详情、示例、指南、检索器、资源、精灵、动画、音效、RUID、资源包、头像。
---

# MSW 搜索

MSW 有 **两个不同的搜索目标**：

1. **API 文档 & 实现指南** — 向量搜索描述、代码示例以及 `.d.mlua` 中缺失的相关 API。
2. **资源** — REST API 用于精灵、动画、声音、资源包和头像。获取 RUID 的唯一途径。

---

## 路由表

| 请求类型 | 转到章节 |
|----------|----------|
| "如何实现这个功能？"、"给我一个示例"、"存在哪些相关 API？" | **文档搜索** |
| ".d.mlua 只有签名；描述不足" | **文档搜索** |
| "我不知道 API 名称（语义搜索）" | **文档搜索** |
| "实现指南 / 最佳实践 / 模式" | **文档搜索** |
| "我需要一个 SpriteRUID"、"为怪物 / NPC / 背景查找精灵" | **资源搜索** → **从 `resource_pack` 开始** |
| "查找动画 / 声音 / 资源包" | **资源搜索** → **从 `resource_pack` 开始** |
| "此 RUID 的详细信息"、"相似资源" | **资源搜索** |
| "头像物品 / 默认头像查找" | **资源搜索** |
| "上传 / 列出 / 更新 / 删除我的自己的资源" | 直接调用 `msw-mcp` `asset_*` 工具 |
| "设置精灵轴心"、"设置 9 切片边框"、"UI RUID 的切片边界"、"资源属性" | 直接调用 `msw-mcp` `asset_update_resource_storage_info` (`properties: [{ key, value }]` — `pivot_x/y`, `border_left/right/top/bottom`, `filter_mode`, `wrap_mode`) |

> **★ 资源搜索默认 — 始终 `resource_pack` 优先**
>
> 除非用户 **明确** 要求单个精灵 / animationclip / 声音 / 头像物品（或直接命名非包 RUID），否则将 `resourceTypeFilter: ["resource_pack"]` 传递给 `searchResources`。一个包捆绑了一个资源所有的精灵 + 动画 + 声音，因此首先选择一个随机的 `sprite` 或 `animationclip` 通常会导致实体只有一个帧、没有动画设置或资产家族错误。
>
> 搜索包 → 遍历 `payload.elements` → 分配单个 RUID。

---

# 章节 1 — 文档搜索 (APIs & Guides)

通过 **`msw-mcp`** MCP 服务器进行向量搜索。提供 `.d.mlua` 中缺失的详细描述、代码示例、相关 API 和实现指南。

## 决策流程

```
需要 API 相关信息
│
├─ 检查签名 / 类型 / 属性 / 枚举
│   → 首先阅读 .d.mlua (最高优先级)
│   → 如果 .d.mlua 不足，调用 msw-mcp
│     (代码示例、参数细节、相关 API 等)
│
├─ 实现指南 / 模式 / 最佳实践
│   → mlua_document_retriever
│
└─ 不知道 API 名称 (语义搜索)
    → mlua_api_retriever (和/或 mlua_document_retriever 用于更广泛的范围)
```

---

## API 研究顺序

### 优先级 1 — .d.mlua (始终首先)

如果你知道 API 名称，**始终首先阅读 `.d.mlua`**。在这里可以准确确认签名、类型、属性、事件参数和枚举值。

**路径**： `Environment/NativeScripts/{Component,Service,Event,Enum,Logic,Misc}/Name.d.mlua`

| 情况 | 示例 |
|------|------|
| 确认方法签名 | "TransformComponent 是否有 SetPosition?" |
| 属性类型 / 存在性 | "SpriteRendererComponent.RUID 的类型是什么?" |
| 事件参数结构 | "AttackEvent 构造函数的参数是什么?" |
| 枚举值列表 | "BodyMoveType 的值有哪些?" |
| 方法存在性 | "SpawnService 有哪些方法?" |

### 优先级 2 — 向量搜索 (.d.mlua 不足时)

`.d.mlua` 只包含签名，**缺少详细描述和示例**。当你需要以下任何内容时使用向量搜索。

| 情况 | MCP 工具 | 示例查询 |
|------|----------|----------|
| 需要 **代码示例** | `mlua_api_retriever` | `AIComponent 示例`, `BehaviorTree 使用` |
| **参数细节** | `mlua_api_retriever` | `BadgeService GetBadgeInfosAndWait 参数` |
| **相关 API** 交叉引用 | `mlua_api_retriever` | `AttackComponent 相关`, `HitComponent` |
| **ScriptOverridable** 检查 | `mlua_api_retriever` | `AttackComponent CalcCritical 重写` |
| **不知道** API 名称 | 两者 | `伤害计算`, `库存保存` |
| **"如何…"** 实现指南 | `mlua_document_retriever` | `如何制作库存系统` |
| **模式 / 最佳实践** | `mlua_document_retriever` | `碰撞检测最佳实践` |

---

## MCP 工具 (`msw-mcp`)

| 工具 | 描述 |
|------|------|
| **`mlua_api_retriever`** | Service / Component / Misc 等的 API 详细信息（签名、参数、示例）。传递 API/类/函数/组件名称。 |
| **`mlua_document_retriever`** | 作者手册、指南、MLua 使用和其他文档式材料。传递描述要实现的自然语言句子。 |

**失败处理**：如果 `msw-mcp` 工具调用出错，向用户显示失败并回退到 `.d.mlua`。不要猜测 — 说明你无法验证的内容。

**默认结果数量**：除非明确要求更广泛的探索，否则请求 **3** 个结果。

---

## .d.mlua 与搜索 — 信息比较

`.d.mlua` 是类型桩 (~29 行)；搜索返回完整文档 (254+ 行)。

| 信息 | .d.mlua | 搜索 |
|------|:-------:|:----:|
| 方法签名 / 类型 | **O** | O |
| 属性声明 | **O** | O |
| 详细方法描述 (DetailDesc) | X | **O** |
| 代码示例 (AdditionalPageContent) | X | **O** |
| 每个参数的描述 | X | **O** |
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
| 执行空间 (重写) | 编辑器中显示 / 省略 `[server only]` | **完全匹配父级的 `@ExecSpace`** — 见下警告 | LEA-3014 如果不匹配 |
| 属性 | `Property: int32 Score = 0` | `@Sync property int32 Score = 0` | 如果同步则添加 `@Sync` |
| 类型 `int` | `int` | `integer` | C# int → mlua integer |
| 类型 `number` | `number` | `number` | 相同 (double) |
| 类型 `float` | `float` | `float` | 相同 (single) |

> `number` (64 位 double) 和 `float` (32 位 single) 可以相互赋值，但仍然是不同的类型。遵循 `.d.mlua` 声明。

> ⚠ **重写 ExecSpace 限制 — LEA-3014 `SignatureMismatch`**
>
> Maker Editor 通常 **隐藏** 父级的执行空间，并允许你在 `override` 块上自由切换 `[server only]`。但在 `.mlua` 中，重写的 `@ExecSpace` 必须与 `.d.mlua` 中声明的父级 **字节完全相同**。如果父级没有 `@ExecSpace`（引擎默认 = `ExecSpace=All`），重写也必须 **完全省略 `@ExecSpace`**。
>
> 具体来说，AttackComponent / HitComponent 伤害钩子 (`CalcDamage`, `CalcCritical`, `GetCriticalDamageRate`, `GetDisplayHitCount`, `IsAttackTarget`, `IsHitTarget`, `OnAttack`) 都是 `ExecSpace=All` 上游。添加 `@ExecSpace("ServerOnly")` 产生：
>
> ```
> [LEA-3014] SignatureMismatch : <Child>.CalcDamage[... (ExecSpace=ServerOnly)]
>   的签名必须与 <Parent>.CalcDamage.[... (ExecSpace=All)] 匹配。
> ```
>
> 始终首先在 `.d.mlua` 中查找父级并逐字复制其注解块。详情：[`msw-scripting/SKILL.md` §9 "Method override → LEA-3014`](../msw-scripting/SKILL.md)。

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
-- ⚠ AttackComponent.CalcDamage / CalcCritical 在 .d.mlua 中声明没有 @ExecSpace
--   (ExecSpace=All)。在这里添加 @ExecSpace 会触发 LEA-3014 SignatureMismatch。
method integer CalcDamage(Entity attacker, Entity defender, string attackInfo)
    return 50
end

method boolean CalcCritical(Entity attacker, Entity defender, string attackInfo)
    return _UtilLogic:RandomDouble() < 0.3
end
```

---

# 章节 2 — 资源搜索 (Sprite / Animation / Sound / Resource Pack / Avatar)

REST API 用于搜索和浏览 MSW 资源。
永远不要猜测或编造 RUID — **始终通过此 API 获取**。

> **默认搜索类型 = `resource_pack`** — 见上路由表中的包优先规则。

## 访问 — 始终通过 `msw_resource_api.cjs`

此技能中的所有资源-API 调用都是通过 Node.js 包装器进行的

```
scripts/msw_resource_api.cjs
```

**不要手动组装 curl 命令**。包装器：

- 直接发送 UTF-8 JSON 正文，因此非 ASCII 查询（韩语 / 日语 / 中文 / 表情符号）避免 `{"detail":"There was an error parsing the body"}` 失败模式，该模式会影响到 inline `curl -d '...'`。
- URL 编码包含斜杠的路径参数（例如像 `npc/1013617.img` 这样的包 ID）。
- 零依赖（Node 18+ 内置的 `fetch` / `AbortController`）。
- 使用 **精确的 OpenAPI 字段名称** (`topK`, `resourceTypeFilter`, `categoryFilter`, `count`, …)。遗留名称如 `limit` / `types` / `categories` 由服务器静默忽略。

使用它的两种方式：

```bash
# 1) CLI — 从 shell 发起一个调用。输出格式化 JSON。
node scripts/msw_resource_api.cjs \
    search "orange mushroom" --resource-type resource_pack --category npc --topK 3

# 发现可用的子命令：
node scripts/msw_resource_api.cjs --help
```

```js
// 2) require — 当已经在 Node.js 上下文中时首选。
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
|------------|------------|------|
| `searchResources` | `search` | `POST /v3/search/resources` |
| `searchAvatarItems` | `search-avatar` | `POST /v3/search/resources` (头像模式) |
| `findSimilarResources` | `similar` | `GET /v3/search/resources/similar/{ruid}` |
| `getResource` | `get` | `GET /v3/resources/{ruid}` (适用于 sprite / animationclip / resource_pack / avataritem) |
| `getResourcesBatch` | `batch` | `POST /v3/resources/batch` |
| `getResourceTags` | `tags` | `GET /v3/resources/tags/{ruid}` |
| `listResources` | `list` | `GET /v3/resources` (Qdrant Scroll, 透明字符串 `offset` 光标) |
| `randomResources` | `random` | `GET /v3/resources/random` |
| `findPacksContaining` | `packs` | `GET /v3/resources/packs/{ruid}` (列出包含 RUID 的包 — 包 ID 在这里不被接受) |
| `listAvatars` | `avatars` | `GET /v3/avatars` |
| `getAvatarDefaults` | `avatar-defaults` | `GET /v3/avatars/defaults` |

> **不存在 `/v3/avatars/{ruid}` 端点。** 要检查头像物品
> (color_hex, group 成员，…)，调用 `getResource(ruid)` — `/v3/resources/{ruid}` 端点像任何其他资源一样返回头像物品细节。

## 基础 URL & 传输（信息性）

包装器处理所有这些 — 你不需要手动设置。

- 基础 URL: `https://maplestoryworlds-resourcesearch-new.nexon.com/api`
- 无需认证（公开），`/v3/` 前缀，POST 正文是 `application/json; charset=utf-8`
- 默认超时：15s（通过包装器的 `_request(method, path, { timeout })` 覆盖）

### 结果数量 — 此技能的默认值是 **3**

除非明确告知，否则在每次搜索调用中始终发送 `3` 作为结果数量参数。包装器也默认为 3，参数名称与 OpenAPI 规范完全一致 — 注意 `limit` / `count` / `topK` 在不同端点有所不同。

| 端点 | 服务器参数 | 包装器默认值 |
|------|------------|:------------:|
| `POST /v3/search/resources` (资源 + 头像) | `topK` | **3** |
| `GET /v3/search/resources/similar/{ruid}` | `topK` | **3** |
| `GET /v3/resources` (浏览) | `limit` | **3** |
| `GET /v3/resources/random` | `count` | **3** |
| `GET /v3/resources/packs/{ruid}` (包含 RUID 的包) | `limit` | **3** |

> 服务器端默认值是 20 或 50，因此 **始终明确传递这些参数**。
> 在需要更广泛探索时，增加到 10+（或 50–100 用于头像广域浏览）。

> **`offset` 参数限制** — 对于 `GET /v3/resources` 和 `GET /v3/resources/packs/{ruid}`，
> `offset` 不是 **整数**，而是 **由前一个响应返回的透明字符串光标 `nextOffset`**。
> 不要在第一页发送它（发送整数 `0` 被解释为光标并返回空结果）。

### POST 正文规则 — 让 `msw_resource_api.cjs` 处理

如果你必须不使用包装器（你的语言中没有 HTTP 客户端），请复制其行为：

1. 将正文序列化为 **UTF-8 JSON 字节**（不是重新编码的 shell 字符串）。
2. 发送 `Content-Type: application/json; charset=utf-8`。
3. 发送原始字节（例如 curl 的 `--data-binary "@file"` 读取 UTF-8 临时文件）。

否则，直接调用包装器。

## 资源类型

`type` 值（服务器响应中的 `type` 字段，以及你在搜索时放入 `resourceTypeFilter` 数组的值）：

| type | 描述 |
|------|------|
| `sprite` | 静态图像 (PNG) |
| `animationclip` | 基于帧的动画 |
| `resource_pack` | 完成资源捆绑精灵 + 动画 + 声音 |
| `bgm` | 背景音乐 (音频) |
| `voice` | 声音片段 — NPC 对话等 (音频) |
| `effect` | **声音效果 (音频)**。不是视觉效果。对于视觉粒子 / 击中 / 技能 FX，搜索 `sprite` 或 `animationclip`（类别 `skill` / `mob` / `etc`）。 |
| `avataritem` | 头像服装物品（帽子、外套、裤子、鞋子、武器，…）— 同样使用 `POST /v3/search/resources` 端点，`resourceTypeFilter: ["avataritem"]`。参见 [`references/resource/search.md`](references/resource/search.md) ("Avatar Item Search") 和 [`references/resource/avatar.md`](references/resource/avatar.md)。 |

> 所有搜索和列表端点使用相同的类型过滤字段名称：**`resourceTypeFilter`**
> （一个数组）。其他名称如 `types` 由服务器静默忽略。
> 包装器的 `resource_type_filter` 参数（或 CLI `--resource-type`）映射到此字段。

⚠ **`SpriteRendererComponent.SpriteRUID` 同时接受 `sprite` 和 `animationclip`，但渲染方式不同：**
- `animationclip` → 所有帧层都会播放（阴影 + 身体 + 前景）
- `sprite` → 仅渲染该单个 Sprite

错误症状：将 `animationclip` RUID 误用于本应使用 `sprite` 的地方（反之亦然），则仅可见阴影层——身体层会无声消失。在分配给 `SpriteRUID` 之前，务必检查响应中的 `payload.type`。静态空闲/默认帧使用 `sprite`；仅将 `animationclip` 用于 `StateAnimationComponent.ActionSheet` 等字段。

**`skeleton` 和 `avataritem` RUID 在未添加 `thumbnail://` 前缀的情况下分配给 `SpriteRUID` / `ImageRUID` 时会静默失败（无错误，无渲染）。** 相反，`CostumeManagerComponent.Custom*Equip` / `SkeletonRendererComponent.SkeletonRUID` / `StateAnimationComponent.ActionSheet` **不接受** `thumbnail://` 前缀——此处应传递纯 RUID。如果搜索查询针对图标/缩略图图像并返回了 `sprite` RUID，该 RUID 本身即可直接渲染——添加 `thumbnail://` 是冗余的。完整的分配规则——接受的类型、按槽位的前缀矩阵、RUID 与前缀的使用——均位于 [`msw-sprite-ruid/SKILL.md`](../msw-sprite-ruid/SKILL.md)。

## 分类

`category` 值实际出现在响应中的值。使用这些值与 `categoryFilter`。

### 常规资源 (`sprite` / `animationclip` / `resource_pack` / `bgm` / `voice` / `effect`)

| category | 描述 |
|----------|-------------|
| `mob` | 怪物 |
| `npc` | NPC |
| `item` | 物品 |
| `skill` | 技能效果 / 技能资源 |
| `object` | 地图对象（树木、岩石、装饰） |
| `background` | 背景 / 地图瓦片 / BGM |
| `foothold` | 可行走平台 |
| `rope` | 绳索 |
| `ladder` | 梯子 |
| `etc` | 未分类 |

### 头像 (`avataritem` 仅限）

| category | 槽位 |
|----------|------|
| `cap`, `hair`, `face`, `faceaccessory`, `eyeaccessory`, `earaccessory` | 头部 / 脸部 |
| `coat`, `longcoat`, `pants`, `shoes`, `glove`, `cape` | 身体 |
| `weapon`, `twohandweapon`, `subweapon`, `shield` | 武器 |

> `map`, `effect`, `ui` **不是**有效的分类值——它们返回零结果。
> - 查找地图 / 背景 → `category: "background"` 或 `"object"`。
> - 查找**视觉特效** → 使用 `category: "skill"`（或 `mob`/`etc`）搜索 `sprite` / `animationclip`；`effect` 是**音频**资源类型，不是分类。
> - 此索引中没有 `ui` 资源系列——UI 图像通常作为 `sprite` + `category: "etc"` 存在。

## RUID

一个 32 位的十六进制字符串，唯一标识每个资源。示例：`"0017da7385e04bc4b2ddbe5949b4b462"`

- 搜索结果中的 `id` 字段是 RUID
- `assetGuid` 是一个独立的 Unity 资产 GUID（用于 `spawn_preset`）
- 永远不要猜测或编造 RUID——始终从 API 响应中获取

## 常见响应字段

```json
{
  "id": "32 位十六进制 RUID",
  "type": "sprite|animationclip|resource_pack|bgm|voice|effect|avataritem",
  "category": "mob|npc|item|skill|object|background|foothold|rope|ladder|etc | <头像槽位>",
  "names": {
    "ko": ["韩文名"],
    "en": ["英文名"]
  },
  "assetGuid": "Unity 资产 GUID（可能存在也可能不存在）",
  "payload": {
    "width": 64,
    "height": 64,
    "thumbnail": "https://...",
    "pivot": {"x": 32, "y": 32},
    "frames": [],
    "elements": []
  }
}
```

## 分页——同名称，两种风格

`nextOffset` 出现在每个列表式响应中，但根据端点不同含义**不同**。将值循环传递到错误的端点会导致静默错误。

| 端点 | `nextOffset` 类型 | 含义 | 如何分页 |
|---|---|---|---|
| `POST /v3/search/resources`（搜索） | **整数** | 项目偏移（0-based） | 将其作为 `offset`（数字）回传 |
| `GET /v3/search/resources/similar/{id}`（相似） | **整数** | 项目偏移 | 相同 |
| `GET /v3/resources`（列表） | **不透明的 UUID 字符串** | Qdrant Scroll 光标 | 将字符串回传作为 `offset`。**流结束 = `null`** |
| `GET /v3/resources/packs/{ruid}`（资源包） | **不透明的 UUID 字符串** | 相同光标 | 相同 |
| `GET /v3/resources/random` | n/a | 无分页 | — |

**规则：**

1. 永远不要将列表光标传入搜索调用（反之亦然）——服务器会忽略形状错误的值并返回第一页。
2. 在**第一页**中，完全省略 `offset`。将整数 `0` 传入 `list` / `packs` 被解释为光标，且会返回**零项**（静默失败）。
3. 当响应返回 `nextOffset: null`（列表 / 资源包）或返回少于 `topK` 项（搜索 / 相似）时停止分页。

## 端点摘要

| 方法 | 端点 | 目的 |
|--------|----------|---------|
| POST | `/v3/search/resources` | 自然语言语义搜索（包括通过 `resourceTypeFilter: ["avataritem"]` 搜索头像项） |
| GET | `/v3/search/resources/similar/{ruid}` | 查找相似资源 |
| GET | `/v3/resources/{ruid}` | 单个资源详情（sprite / animationclip / **带有填充元素的 resource_pack** / **avataritem**) |
| POST | `/v3/resources/batch` | 批量获取多个资源 |
| GET | `/v3/resources/tags/{ruid}` | AI 生成的多语言标签 |
| GET | `/v3/resources` | 列出资源（Qdrant Scroll，不透明的字符串 `offset` 光标） |
| GET | `/v3/resources/random` | 随机资源推荐 |
| GET | `/v3/resources/packs/{ruid}` | 列出包含给定 RUID 的资源包——路径参数是 32 位十六进制 RUID，不是包 ID |
| GET | `/v3/avatars` | 列出所有头像项（缓存） |
| GET | `/v3/avatars/defaults` | 默认头像身体 / 头部 RUID |

> 单个头像项详情使用 `/v3/resources/{ruid}`（不存在 `/v3/avatars/{ruid}` 端点）。

---

## 资源路由指南

> **不确定时，优先搜索 `resource_pack`。** 以下行中标记了明确非包意图的除外。

| 情况 | Wrapper 调用（CLI 子命令） | 参考文件 |
|-----------|-------------------------------|----------------|
| "查找史莱姆 / 橙色蘑菇 / 怪物 / NPC / 物品 / 背景 / 地图资源"（默认——未指定类型） | `searchResources(query, { resourceTypeFilter: ["resource_pack"], ... })` (`search ... --resource-type resource_pack`) | [`references/resource/search.md`](references/resource/search.md) |
| "查找**单个 sprite** / 单个图像"（用户明确要求 sprite） | `searchResources(query, { resourceTypeFilter: ["sprite"], ... })` | [`references/resource/search.md`](references/resource/search.md) |
| "查找**单个 animationclip**"（用户明确要求动画） | `searchResources(query, { resourceTypeFilter: ["animationclip"], ... })` | [`references/resource/search.md`](references/resource/search.md) |
| "查找**视觉特效 / 粒子 / 击打特效**" | `searchResources(query, { resourceTypeFilter: ["animationclip","sprite"], categoryFilter: ["skill","mob","etc"] })` — 注意：这里的 `effect` 指的是**音频**，不是视觉 | [`references/resource/search.md`](references/resource/search.md) |
| "查找**声音 / BGM / 语音 / 音效**"（音频） | `searchResources(query, { resourceTypeFilter: ["bgm"\|"voice"\|"effect"], ... })` — `effect` 资源类型 = 音效（音频） | [`references/resource/search.md`](references/resource/search.md) |
| "查找**背景 / 地图瓦片 / 风景**" | `searchResources(query, { resourceTypeFilter: ["sprite","animationclip"], categoryFilter: ["background","object"] })` — 索引中没有 `map` 分类 | [`references/resource/search.md`](references/resource/search.md) |
| "查找服装 / 帽子 / 鞋子 / 武器（头像项）" | `searchAvatarItems(...)` (`search-avatar`) | [`references/resource/search.md`](references/resource/search.md)（头像项搜索部分）+ [`references/resource/avatar.md`](references/resource/avatar.md) |
| "这个怪物还有类似的吗？" | `findSimilarResources(ruid, ...)` (`similar`) | [`references/resource/search.md`](references/resource/search.md) |
| "RUID abc123 的详情"（任何类型，包括 avataritem 和 resource_pack） | `getResource(ruid)` (`get`) | [`references/resource/detail.md`](references/resource/detail.md) |
| "显示怪物 sprite 列表" | `listResources(...)` (`list`) | [`references/resource/browse.md`](references/resource/browse.md) |
| "哪些资源包包含此 RUID？" | `findPacksContaining(ruid, ...)` (`packs`) | [`references/resource/browse.md`](references/resource/browse.md) |
| "浏览所有头像项" | `listAvatars(...)` (`avatars`) | [`references/resource/avatar.md`](references/resource/avatar.md) |

### 典型工作流程（优先搜索资源包）

```
1. searchResources(query, { resourceTypeFilter: ["resource_pack"], topK: 3 })
   → 获取资源包 RUID（或类似 "npc/9072309.img" 的包 ID）
   → 仅在明确用户意图时切换类型，或当 0 个资源包匹配时回退
2. getResource(id)
   → 资源包：payload.elements 已预填充元素 payload
                    （sprite / animationclip / 声音 RUID 存放于此）
   → avataritem：    payload 包含 color_hex / group 元数据
3. 从 payload.elements 中选择元素，并将其 RUID 分配给
   SpriteRendererComponent.SpriteRUID / StateAnimationComponent.ActionSheet
   （或通过 `msw-avatar` 中的槽位映射分配 avataritem RUID）

> **不要**调用 `findPacksContaining(packId)` 来“打开”资源包——该端点接受 32 位十六进制 RUID 并返回**包含该 RUID 的资源包**，而不是包内容。使用 `getResource(packId)` 获取包内容。

> **有关每个端点的详细请求/响应，请参考 `references/resource/` 下的文件。**

---

## Sprite 方向——大多数资源面向左侧

大多数 MSW sprite / animationclip / resource_pack 资产——尤其是 `mob`、`npc` 和玩家角色——都是**面向左侧**创作的，因此新生的 `SpriteRendererComponent` 除非翻转否则会面向左侧渲染。

| 情况 | 应如何操作 |
|-----------|-----------|
| 生成一个应面向**右侧**的实体 | 在 `SpriteRendererComponent` 上设置 `FlipX = true`（默认为 `false` = 左侧创作方向） |
| 自定义 AI / 使用 `MovementComponent:MoveToDirection` 追逐 | 在方向变化时更新 `FlipX`：`sprite.FlipX = velocity.x > 0`（右侧 ⇒ 翻转） |
| 怪物模型 / 怪物碰撞器对齐 | 而不是 `FlipX`，翻转 `TransformComponent.Scale.x` 以使 sprite 和碰撞器保持对齐；参见 [`msw-general/references/monster.md`](../msw-general/references/monster.md) |
| 原生 `AIChaseComponent` / `AIWanderComponent` | 引擎根据移动自动翻转——无需操作 |
| 俯视（`RectTile`）移动 | 按轴决定：通常 `dx > 0` 时翻转；带有上下帧的 sprite 需要使用 `StateAnimationComponent` 动作集 |
| `_EffectService:PlayEffect(...)` 应面向右侧 | 在 `options` 表中传递 `FlipX = true` |
| 玩家附加特效必须跟随玩家的朝向 | 在 `PlayEffect` 选项中使用 `SyncFlip = true`，或读取 `PlayerControllerComponent.LookDirectionX` |
| 资源是面向右侧创作的（罕见） | 通过 `GET /v3/resources/{ruid}` 检查 `payload.thumbnail` 并为该资产反转规则 |

```lua
-- 自定义横版追逐：翻转 sprite 以匹配移动方向
local sprite = self.Entity.SpriteRendererComponent
local selfX = self.Entity.TransformComponent.WorldPosition.x
local dx    = targetPos.x - selfX
if dx ~= 0 then
    sprite.FlipX = dx > 0   -- 目标在右侧 → 翻转
end
```

> **合理性检查**——左侧面向惯例并非合同性。打开 `GET /v3/resources/{ruid}` 的 `payload.thumbnail` 以确认。
>
> **不要**将 `TransformComponent.Scale.x` 作为通用渲染器翻转**——对于玩家 / 特效 / 非怪物渲染器，使用 `SpriteRendererComponent.FlipX`。**怪物例外**：怪物模型应翻转 `TransformComponent.Scale.x` 以使 sprite 和碰撞器保持对齐。相关：[`msw-combat-system/SKILL.md` "方向检查 ★"](../msw-combat-system/SKILL.md)，[`msw-general/references/monster.md`](../msw-general/references/monster.md)。

---

# 共享技巧

1. **关键词选择**——如果知道确切名称，使用确切名称；自然语言韩语/英语也有效。
2. **调整页面大小参数**——端点名称不同（`topK` 用于搜索/相似，`limit` 用于列表/资源包，`count` 用于随机）。**此技能的默认值是 3**（参见上文的“结果数量”表）。保持 3 以进行精确查找；仅在需要更广泛探索时增加到 10+（或 50–100 用于头像广泛浏览）。
3. **搜索失败时**：
   - 记录搜索失败 → 直接读取 `.d.mlua`。
   - 资源搜索失败 → 使用同义词或不同分类重试；使用 `listResources(...)`（CLI: `list`）按类型/分类浏览。
   - `POST` 返回 `{"detail":"There was an error parsing the body"}` → 你绕过了包装器并通过 `curl -d '{...}'` 直接传递 JSON。切换到 `msw_resource_api.cjs`（或复制其 UTF-8 原始 body POST 模式）如第 2 节所述。
4. **允许组合查询**——例如 `AttackComponent CalcCritical` 用于文档，`red slime jump` 用于资源。
5. **不要猜测**——永远不要猜测 API 名称、RUID 或枚举值；始终通过搜索或参考确认。
