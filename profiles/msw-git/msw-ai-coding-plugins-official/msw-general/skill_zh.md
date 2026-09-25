# MSW 基础 — 基础技能

MSW（MapleStory Worlds）创建的基础技能，整合了**共享工具、领域知识、平台规则和文件创作**。其他所有 MSW 技能都依赖于它。

---

## 核心原则：视觉打磨

MSW 是一个**游戏创建平台**。目标是创建一个玩家可以享受的**精炼游戏**，而不是一个仅仅运行逻辑的原型。

因此，无论你创建什么实体——怪物、NPC、塔、物品、背景物体——都要搜索并应用与其角色和个性相匹配的**适当资源（精灵、动画、声音）**。不要保留默认精灵或让 `SpriteRUID` 为空。

**创建实体时的资源应用原则：**

1. 创建实体后，使用 **`msw-search` 技能**查找适合它的精灵/动画
2. 将找到的资源 RUID 应用到 `SpriteRendererComponent`，以便实体**视觉化呈现**
3. 如果有战斗，也设置击打/爆炸效果；如果有交互，设置音效

> **功能实现 != 完成。** 精炼游戏需要适当的资源加上视觉呈现。

---

## 创建 `.model` 时——先查看目录

不要从空文件开始创建新的 `.model`。**技能本地的 `models/` 文件夹包含按类别组织的经过验证的模板**——怪物（`ChaseMonster`/`MoveMonster`/`StaticMonster`）、NPC（`StaticNPC`）、玩家（`Player`/`DefaultPlayer`）、地形（`Foothold`/`Ladder`/`Rope`/`Portal`）、地图对象（`MapObject`/`SkeletonMapObject`/`ItemAsset`）、粒子（`BasicParticle`/`SpriteParticle`/`AreaParticle`/`AnimationPlayer`）、声音（`Sound`/`SoundEffect`）、瓦片地图容器（`TileMap`/`RectTileMap`）、UI（`UIButton`/`UIText`/`UISprite`/`UIGroup`，等等）、外部媒体（`WebSprite`/`YoutubePlayerWorld`）。

**工作流程**：**首先完整阅读 [references/model.md](references/model.md)（强制——见下文“模型工作预读 — 必须的”）** → 从目录中选择最接近的模板 → 通过 `ModelBuilder` 加载它（调用协议：[`references/builder-protocol.md`](references/builder-protocol.md) 核心 + [`references/builder-protocol-model.md`](references/builder-protocol-model.md)）→ 通过构建器替换 3 个标识符（`EntryKey` / `Id` / `Name`）→ 通过构建器自定义 `Components`/`Values`/`Properties`/`Children` → **保存在 `RootDesk/MyDesk/Models/` 的类型子文件夹下**（例如 `Models/Monsters/{Name}.model`，绝不能直接在 `MyDesk/` 下）→ `refresh`。详细的目录和构建器程序：[references/model.md §2](references/model.md)。

> 构建器发出所需的价值元数据，因此代理不需要读取或手动编写 `.model` 格式内部。

> **对于怪物，首先选择 [references/animation-state.md §0](references/animation-state.md) 中的模式，然后按照 [references/monster.md §5](references/monster.md) 推荐的路径进行操作。**
> - **模式 A（经过验证的规范工作模式——士兵参考设置，完整源代码内联在 [`references/monster.md` §7](references/monster.md) 中）**：不需要模板；用自定义的 `script.MyMonsterAI`（士兵 AI 风格）而不是 AIChase/AIWander 从头开始组装 11 个组件。`StateComponent.IsLegacy` 保持默认值。
> - **模式 B (`MonsterCanonical.model`)**：`AIChaseComponent` + `ActionSheet` 管道。`StateComponent.IsLegacy=false` 强制。其他怪物模板（`ChaseMonster` / `MoveMonster` / `StaticMonster`）将 `ActionSheet` 留空并使用默认值，在模式 B 下会静默失败（大写键，`SortingLayer="Default"`，`IsLegacy=true`）。

> **对于任何具有 `StateAnimationComponent`（怪物/NPC）或 `AvatarStateAnimationComponent`（玩家）的实体——或者任何调用 `ChangeState` / `AddState` / `SetActionSheet` 的 `.mlua`——也阅读 [references/animation-state.md](references/animation-state.md)。** 状态机 ↔ 动画管道、两种模式分割、默认状态注册规则、`[LEA-3005]` 原因，以及 `SetActionSheet` vs `ChangeState` 语义都存在于其中（未重复到每个实体的文档中）。

---

## 放置多个实体——模型优先

如果同一个实体将在**地图中两次或更多次出现**（5 个怪物、10 棵树、3 个传送门，等等），**请先创建一个 `.model` 并通过 `modelId` 放置每个实例**，而不是复制粘贴内联 `@components`。

| 相同组成的实例数量 | 选择 |
|---|---|
| **1**（在单个地图中真正唯一的装饰） | 内联 `@components` 可以接受 |
| **≥2** | **`.model` + `modelId` 实例（默认）** |
| 运行时生成 (`SpawnByModelId`) | 无论数量如何，都需要 `.model` |

**为什么这是默认设置：**

- **一次编辑，处处传播**——在模型中更改 `SpriteRUID`/HP/`ActionSheet`，每个实例都会更新。内联副本需要每次触摸 N 个实体。
- **更小的、可审查的 `.map` 差异**——`modelId` 实例只携带 `Transform` 覆盖；内联副本会使地图因每个实体而膨胀数百行。
- **避免漂移**——五个内联副本会默默分化（一个获得 `IsLegacy: true`，另一个忘记 `SortingLayer: "MapLayer0"`）。模型锚定了规范值。
- **对于 `SpawnByModelId` 是必需的**——如果没有注册的模型 ID，动态生成将失败。

**工作流程**：
1. 在 `RootDesk/MyDesk/Models/{Category}/{Name}.model` 下创建 `.model`（见上面的文件夹规则）。
2. 使用 `MapBuilder`（调用协议：[`references/builder-protocol.md`](references/builder-protocol.md) 核心 + [`references/builder-protocol-map.md`](references/builder-protocol-map.md)) 放置每个实例，以便 IDs、路径、`componentNames`、原始元数据和每个实例组件覆盖保持同步。
3. `refresh`。

详细信息和内联与模型 ID 的比较：[references/entity.md "两步地图编辑工作流程"](references/entity.md), [references/model.md §1](references/model.md)。

---

## 预读语义——适用于此技能中的每个“必须阅读”

预读和绝对原则中的“Read X FIRST”意味着：**X 必须在开始工作前完全处于上下文中**——不是“每次轮到时重新阅读 X”。`Read` 文件**仅当它在本会话中从未加载或因上下文压缩而丢失时**才需要**（仅限 `offset`/`limit`，无 `cat`/`Get-Content`）**重新读取**。**不要重新读取一个已经完全处于上下文中的文件**——存在上下文就是要求；重新读取是浪费。内存或文件摘要**不**算作文件处于上下文中，并且之前回合加载它**不会**豁免本回合确认它仍然存在。

---

## 实体工作预读 — **必须的**

如果任务以任何方式涉及实体，**你必须首先阅读 [references/entity.md](references/entity.md)**。没有例外。

---

## 构建器协议预读 — **必须的**

如果任务**创建或修改任何 `.map` / `.model` / `.ui` 文件**——直接或作为编写 `.mlua` 的副作用（生成/放置/绑定），**[references/builder-protocol.md](references/builder-protocol.md) (核心) 加上每个被修改的文件类型的构建器文件——[references/builder-protocol-map.md](references/builder-protocol-map.md) (`.map`) / [references/builder-protocol-model.md](references/builder-protocol-model.md) (`.model`) / [references/builder-protocol-ui.md](references/builder-protocol-ui.md) — 必须首先完全处于上下文中**（阅读语义见上文）。没有例外。

协议是一个统一的入口点，分为共享核心（`builder-protocol.md` — 路由、通用工作流程、链接合同、§0 预读、§4 跨流程、§5 检查清单）加上每个构建器文件（`builder-protocol-map.md` §1 / `builder-protocol-model.md` §2 / `builder-protocol-ui.md` §3）。**只了解一个构建器的协议然后调用另一个构建器的 `.cjs` 会绕过该构建器的写入端合同**（`componentNames` 同步，`Values` `typeKey` 元数据，写入时自动检查，`placeModel` 组件镜像，子实体不变式）——这三个是通过对流程（模型创作 → 地图放置 → UI 绑定）互锁的，因此跨流程工作会加载每个匹配的构建器文件。

触发器（故意广泛——当任何匹配时加载缺失的协议文件）：

- `.map` 变化（实体放置、组件修补、瓦片 / 站点检查）
- `.model` 变化（新创作、值 / 组件 / 属性 / 子实体编辑）
- `.ui` 变化（新构建、组件 CRUD、绑定注入）
- 任何调用 `MapBuilder` / `ModelBuilder` / `UIBuilder`
- 形状像“实体形状”的工作请求——怪物 / NPC / 投射物 / 地图对象 / 弹窗 / HUD，等等。
- 任何使用 `_SpawnService` 的代码（一个可投射模型必须先创作并放置）

领域引用（`entity.md` / `model.md` / `msw-ui-system` 设计引用）与协议文件**一起读取**——它们不是替代品（领域上下文 + 调用协议是一对）。**确认它们仍然处于上下文中**——每个触发器**都重新读取**——仅当它从未加载或因上下文压缩而丢失时才需要**重新读取。**不要重新读取一个已经完全处于上下文中的文件——存在上下文就是要求；重新读取是浪费。内存或文件摘要**不**算作文件处于上下文中，并且之前回合加载它**不会**豁免本回合确认它仍然存在。

---

## 模型工作预读 — **必须的**

如果任务以任何方式涉及创作或编辑 `.model` 文件——包括任何调用 `ModelBuilder`（任何 API）、从模板创建新模型、修改现有模型上的组件/值/属性/子实体/事件链接，甚至一行小的修改——**你必须首先阅读 BOTH [`msw-scripting/SKILL.md`](../msw-scripting/SKILL.md) AND [`msw-scripting/references/verify-checklist.md`](../msw-scripting/references/verify-checklist.md) 完整**（无 `offset`/`limit`，无 `cat`/`Get-Content`）。阅读 `msw-general` 加上分散的 `.d.mlua` 文件**不是替代品**。即使上一回合已经加载了 `msw-scripting`，在新回合开始时也必须重新确认。**触发短语故意广泛**：如果本回合有任何可能触摸 `.mlua` 的机会，将其视为触发。没有例外，没有“我已经知道这个”，没有通过记忆的快捷方式。

---

## 绝对原则（适用于每个任务）

0. **如果任务涉及实体，首先阅读 [references/entity.md](references/entity.md)**。没有例外。
0-bis. **如果用户的请求提到任何 UI 元素**（弹窗、HUD、按钮、提示、面板、对话框窗口、菜单、标签、布局、屏幕、条形图/仪表、插槽）**或者涉及编写/编辑 `.ui` 文件**，**在向用户提出任何计划、选项或问题之前**：
   1. **首先通过 `Skill` 工具调用 `msw-ui-system`**——唯一的 UI 入口点（设计判断、组件 API、枚举值、布局配方、运行时模式、UUID 绑定、构建器调用协议统一在一个技能中）。
   2. **所有 `.ui` 变化必须通过 `msw-ui-system` 的 `UIBuilder`**——不允许直接原始 JSON 编辑或 grep。通过 `UIBuilder` 的读取侧 API 读取现有的 `.ui` 文件。调用协议：[`references/builder-protocol.md`](references/builder-protocol.md) 核心 + [`references/builder-protocol-ui.md`](references/builder-protocol-ui.md) §3.)
   3. （可选）如果你需要 UI 模式模板（简单的弹窗、最小的 HUD、多标签、商店流程），`Read`/`Glob` `msw-ui-system/references/templates/` 下的文件直接 ([`templates.md`](../msw-ui-system/references/templates/templates.md) + `style-N-*/` + [`ruid-map.md`](../msw-ui-system/references/templates/style-1-black/ruid-map.md) + `Popupbutton.mlua`).
   没有例外。
0-ter. **如果任务将创建、修改、重命名或删除任何 `.mlua` 文件**——包括新脚本、对现有脚本的编辑、添加/删除 `Component`/`@Logic`/`@Event`/`@State`/`@BTNode`、连接生命周期方法（`OnBeginPlay`/`OnUpdate`/...），甚至小的单行修复——**你必须 `Read` BOTH [`msw-scripting/SKILL.md`](../msw-scripting/SKILL.md) AND [`msw-scripting/references/verify-checklist.md`](../msw-scripting/references/verify-checklist.md) 完整**（无 `offset`/`limit`，无 `cat`/`Get-Content`）。阅读 `msw-general` 加上分散的 `.d.mlua` 文件**不是替代品**。这适用于即使上一回合已经加载了 `msw-scripting`——在新回合开始时也必须重新确认。**触发短语故意广泛**：如果本回合有任何可能触摸 `.mlua` 的机会，将其视为触发。没有例外，没有“我已经知道这个”，没有通过记忆的快捷方式。
0-quater. **如果任务涉及生成、移动、跳跃/重力、坐标放置、层/顺序调试、MapleTile/RectTile/SideViewRectTile 特定逻辑，或者你观察到任何静默失败症状（`[LEA-3004]` 日志，“不会移动”，“不会渲染”，“漂浮在半空中”，“卡在墙上”，“消失在地图外”，“从站点边缘掉落”，“100 倍偏移”，“不在 Maker 中显示”，“仅客户端同步”），则必须首先完全处于上下文中匹配的 `references/platform*.md` / [`references/troubleshooting.md`](references/troubleshooting.md) **（阅读仅当缺失时——见“预读阅读语义”）**。**此外，如果症状是动画/状态相关的（`[LEA-3005]` 日志，`'stateName' is not a valid argument`，动画不匹配行为，在移动时卡在站立/待机剪辑中，攻击姿势从未播放，击打动画循环，自定义状态从未动画，任何接触 `StateComponent` / `StateType` / `ChangeState` / `AddState` / `ActionSheet` / `SetActionSheet` / `StateAnimationComponent`），则必须首先完全处于上下文中 [`references/animation-state.md`](references/animation-state.md) **在编写任何代码或模型编辑之前**。此技能中的 8 条核心规则只是摘要——**症状→原因→修复表，每个地图类型的代码模式（站点巡逻 / RectTile 4 方向移动 / SideView 墙检测），`MovementComponent` InputSpeed 转换公式，SpriteRUID，SortingLayer/OrderInLayer 详细信息，`SpawnByModelId` 初始化顺序，文件夹元数据刷新策略，CoreVersion 策略**存在于引用中**。**触发短语故意广泛**：如果本回合触摸这些区域中的任何一个，将其视为触发。对于匹配的 `Read` 目标，请遵循上述“平台规则预读 — 必须的”部分中的触发表。没有例外，没有“我从 8 条核心规则中已经知道这个”，没有通过记忆的快捷方式。

1. **视觉打磨**——不要让 `SpriteRUID` 为空。使用 `msw-search` 查找资源。
2. **`refresh` 在内容文件更改后 Maker 必须摄入**（如果处于播放模式，请先 `stop`）。仅限文件夹更改不需要立即刷新。
3. **永远不要修改 `Environment/*.d.mlua`**——API 定义是只读的。
4. **永远不要手动创建 `.codeblock`**——Maker `refresh` 从 `.mlua` 生成它。文件夹元数据也在刷新期间从真实文件夹生成（见 [references/platform.md §2](references/platform.md)）。
5. **不要在 `Global/` 中创建新的用户文件**——Maker 将不识别它们。用户文件应属于 `RootDesk/MyDesk/` 下。
6. **结构化文件优先使用构建器，调用手册是一个统一的入口点——共享核心加上每个构建器文件**——`.model` / `.ui` 是构建器专用的；`.map` 是构建器优先的。**所有三个构建器——`MapBuilder` / `ModelBuilder` / `UIBuilder`——的调用协议——`MapBuilder` / `ModelBuilder` / `UIBuilder`——汇总在 [`references/builder-protocol.md`](references/builder-protocol.md) (核心) 加上每个构建器文件 ([`builder-protocol-map.md`](references/builder-protocol-map.md) / [`builder-protocol-model.md`](references/builder-protocol-model.md) / [`builder-protocol-ui.md`](references/builder-protocol-ui.md))。核心 + 匹配被修改的类型文件必须在每个修改 `.map` / `.model` / `.ui` 的回合中处于上下文中**（见构建器协议预读）。直接原始 JSON 编辑仅允许在构建器文件中明确列出的覆盖范围区域内，最小范围 + `refresh` + 日志验证。

> **实体参考绑定（Entity/EntityRef 属性）**——AI 直接注入 UUID 字符串。不要要求用户在 Maker 中拖动。
> 8. **CoreVersion 不匹配时停止工作**——首先验证 `Environment/config` 中的 `CoreVersion` 是 `26.7.0.0`。
> 9. **仅当用户明确要求时才调用 `screenshot`**。任务完成后永远不要自动调用它。
> 10. **如果工作流程步骤在流程中失败，则停止后续步骤**——首先修复根本原因。
> 11. **两个或更多 = 创建模型。** 每当同一个实体组合在地图中放置 ≥2 次，**请先创建一个 `.model` 并通过 `modelId` 实例化它**。内联 `@components` 复制是保留给真正唯一的实体的。
> 12. **模型存储在类型子文件夹中。** 将新的 `.model` 文件保存在 `RootDesk/MyDesk/Models/` 的类型子文件夹下（例如 `Models/Monsters/`, `Models/NPCs/`, `Models/Terrain/`, `Models/MapObjects/`, `Models/Particles/`, `Models/UI/`)——**绝不能直接在 `MyDesk/` 或 `Models/` 下**。当需要的子文件夹不存在时，只需创建文件夹即可；Maker 刷新将在稍后生成文件夹元数据（见 [references/platform.md §2](references/platform.md)）。
> 13. **翻译仅限于客户端。** `_LocalizationService` 和 `Translator` 方法 (`GetText` / `GetTextFormat`) 全部都是 `ClientOnly`。对于服务器生成的本地化消息，将键通过 RPC 发送，让客户端解析它。
> 14. **跨平台工具选择——不要用于工作空间探索，使用工具。** 使用 **`Glob` / `Read` / `Grep` 工具**进行所有工作空间文件/文件夹探索、读取和搜索。`Bash` 命令如 `ls` / `dir` / `Get-ChildItem` / `gci` / `cat` / `type` / `Get-Content` / `gc` / `head` / `tail` / `find` / `where` / `grep` / `findstr` / `Select-String` 是**用于工作空间探索**的**forbidden**——由于 shell/路径处理差异（尤其是，在 bash 中，像 `D:\path\foo` 这样的路径会消耗转义字符并折叠为 `D:pathfoo`）。仅使用 `Bash` **仅用于实际 shell 程序**（`git` / `npm` / MCP / 构建脚本），即使这样：**(a) 优先使用** **工作空间相对路径**，**(b) 如果无法避免绝对路径，请使用** **正斜杠 + 双引号** (`"D:/path/to/map/"`, 永远不要传递 `D:\...` 形式), **(c) 使用** **POSIX 命令** **仅限于** (`ls` / `mv` / `cp` / `rm`). 如果你看到一个错误，如 `ls: cannot access 'D:path...': No such file or directory`, 立即停止并重试 via `Glob` / `Read`.
> 15. **`.model` 文件是构建器专用的——并且构建器需要 [`references/model.md`](references/model.md) (领域) 加上 [`references/builder-protocol.md`](references/builder-protocol.md) 核心 和 [`references/builder-protocol-model.md`](references/builder-protocol-model.md) (调用协议) 首先读取。**不要直接检查或编辑 `.model` JSON。** **在使用 `ModelBuilder` 之前，所有这些文档都必须完全处于上下文中**（阅读语义见上文）——模型工作预读和构建器协议预读都会触发。标识符 / 值元数据 / 属性 / 子实体 / 事件链接一致性只有在它们一起读取时才得到保证。
> 16. **`.map` 文件是构建器优先的。** 使用 `MapBuilder` 进行覆盖范围检查和修改，以便实体 IDs、路径、`componentNames`、原始元数据和模型实例镜像保持一致。如果 `MapBuilder` 明确不覆盖所需的操作，请进行最小的直接 `.map` 编辑，然后 `refresh` 并验证。**完整 API / require path / 每个操作模式 / 覆盖差距 / `false`-return 处理 / 跨流程: [`references/builder-protocol-map.md`](references/builder-protocol-map.md) §1 + [`references/builder-protocol.md`](references/builder-protocol.md) §4**（与 [`references/entity.md`](references/entity.md) 一起阅读以获取领域上下文）。
