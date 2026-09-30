---
name: msw-general
description: MSW（MapleStory Worlds）的基础技能。在MSW中，在进行任何其他操作之前，请务必先阅读此内容。
---

# MSW 基础技能

MSW（MapleStory Worlds）创建的基础技能，整合了**共享工具、领域知识、平台规则和文件创作**。其他所有 MSW 技能都依赖于它。

---

## 核心原则：视觉优化

MSW 是一个**游戏创作平台**。目标是创作一个玩家可以享受的**精良游戏**，而不是一个仅仅运行逻辑的原型。

因此，无论你创建的是什么实体——怪物、NPC、塔、物品、背景物体——都要搜索并应用与其角色和个性相匹配的**适当资源（精灵、动画、声音）**。不要保留默认精灵或让 `SpriteRUID` 为空。

**创建实体时的资源应用原则：**

1. 创建实体后，使用 **`msw-search` 技能**查找适合它的精灵/动画。
2. 将找到的资源 RUID 应用到 `SpriteRendererComponent`，以便实体**视觉化呈现**。
3. 如果有战斗，也设置击中/爆炸效果；如果有交互，设置音效

> **功能实现 != 完成。** 精良的游戏需要适当的资源加上视觉呈现。

---

## 创建 `.model` 时——先查看目录

不要从空文件开始创建新的 `.model`。**技能本地的 `models/` 文件夹包含按类别组织的经过验证的模板**——怪物（`ChaseMonster`/`MoveMonster`/`StaticMonster`）、NPC（`StaticNPC`）、玩家（`Player`/`DefaultPlayer`）、地形（`Foothold`/`Ladder`/`Rope`/`Portal`）、地图对象（`MapObject`/`SkeletonMapObject`/`ItemAsset`）、粒子（`BasicParticle`/`SpriteParticle`/`AreaParticle`/`AnimationPlayer`）、声音（`Sound`/`SoundEffect`）、瓦片地图容器（`TileMap`/`RectTileMap`）、UI（`UIButton`/`UIText`/`UISprite`/`UIGroup` 等）、外部媒体（`WebSprite`/`YoutubePlayerWorld`）。

**工作流程**：**完整阅读 [references/model.md](references/model.md)（强制要求——见下文“模型工作预检 — 必须遵守”）** → 从目录中选择最接近的模板 → 通过 `ModelBuilder` 加载它（调用协议：[`references/builder-protocol.md`](references/builder-protocol.md) 核心 + [`references/builder-protocol-model.md`](references/builder-protocol-model.md)）→ 通过构建器替换 3 个标识符（`EntryKey`、`Id`、`Name`）→ 通过构建器自定义 `Components`/`Values`/`Properties`/`Children` → **保存在 `RootDesk/MyDesk/Models/` 的类型化子文件夹下**（例如 `Models/Monsters/{Name}.model`，绝不能直接放在 `MyDesk/` 下）→ `refresh`。详细目录和构建器流程：[references/model.md §2](references/model.md)。

> 构建器发出所需值元数据，因此代理不需要读取或手写 `.model` 格式内部。

> **对于怪物，首先在 [references/animation-state.md §0](references/animation-state.md) 中选择一个模式，然后遵循 [references/monster.md §5](references/monster.md) 推荐的路径。**
> - **模式 A（已验证的规范工作示例——士兵参考设置，完整源代码内联在 [`references/monster.md` §7](references/monster.md) 中）**：不需要模板；用自定义 `script.MyMonsterAI`（SoldierAI 风格）而不是 AIChase/AIWander 从零开始组装 11 个组件。`StateComponent.IsLegacy` 保持默认值。
> - **模式 B（`MonsterCanonical.model`）**：`AIChaseComponent` + `ActionSheet` 管道。`StateComponent.IsLegacy=false` 强制要求。其他怪物模板（`ChaseMonster` / `MoveMonster` / `StaticMonster`）将 `ActionSheet` 留空并使用默认值，在模式 B 下会静默失败（大写键、`SortingLayer="Default"`、`IsLegacy=true`）。
>
> **对于任何具有 `StateAnimationComponent`（怪物/NPC）或 `AvatarStateAnimationComponent`（玩家）的实体——或任何调用 `ChangeState` / `AddState` / `SetActionSheet` 的 `.mlua`——也请阅读 [references/animation-state.md](references/animation-state.md)。** 状态机 ↔ 动画管道、两种模式划分、默认状态注册规则、`[LEA-3005]` 原因以及 `SetActionSheet` vs `ChangeState` 语义都在那里（不会重复到每个实体的文档中）。

---

## 放置多个实体——模型优先

如果同一个实体将在**地图中两次或更多次出现**（5 个怪物、10 棵树、3 个传送门、…），**先创建一个 `.model` 并通过 `modelId` 放置每个实例**，而不是复制粘贴内联 `@components`。

| 相同构成的实例数量 | 选择 |
|---|---|
| **1**（单个地图中真正独立的装饰） | 内联 `@components` 可以接受 |
| **≥2** | **`.model` + `modelId` 实例（默认）** |
| 运行时生成（`SpawnByModelId`） | 无论数量如何都需要 `.model` |

**为什么这是默认设置：**

- **一次编辑，处处传播**——在模型中更改 `SpriteRUID`/HP/`ActionSheet`，所有实例都会更新。内联副本每次都需要触摸 N 个实体。
- **更小的、可审查的 `.map` 差异**——`modelId` 实例仅携带 `Transform` 覆盖；内联副本会使地图因每个实体而膨胀数百行。
- **避免漂移**——五个内联副本会默默分化（一个得到 `IsLegacy: true`，另一个忘记 `SortingLayer: "MapLayer0"`）。模型锚定了规范值。
- **`SpawnByModelId` 所需**——没有注册的模型 ID，动态生成会失败。

**工作流程**：
1. 在 `RootDesk/MyDesk/Models/{Category}/{Name}.model` 下创建 `.model`（见上述文件夹规则）。
2. 通过 `MapBuilder`（调用协议：[`references/builder-protocol.md`](references/builder-protocol.md) 核心 + [`references/builder-protocol-map.md`](references/builder-protocol-map.md)）放置每个实例，以保持 ID、路径、`componentNames`、原点元数据和每个实例组件覆盖同步。
3. `refresh`。

详细信息和内联与模型 ID 的比较：[references/entity.md "两步地图编辑工作流程"](references/entity.md)，[references/model.md §1](references/model.md)。

---

## 预检阅读语义——适用于本技能中的每个“必须阅读”

预检和绝对原则中的“阅读 X FIRST”意味着：**X 必须在开始工作前完全处于上下文中**——不是“每次都重读 X”。`Read` 文件**完整（无 `offset`/`limit`，无 `cat`/`Get-Content`）** 仅当它在本会话中从未加载或因上下文压缩而丢失时。**不要**重新读取一个已经完全处于上下文中的文件——存在在上下文中就是要求；重读是浪费。内存或文件摘要**不**算作文件处于上下文中，之前加载它也不豁免本回合确认它仍然存在。

---

## 实体工作预检——**必须**

如果任务涉及任何实体，**你必须先阅读 [references/entity.md](references/entity.md)。** 没有例外。

---

## 构建器协议预检——**必须**

如果任务**直接或作为编写 `.mlua` 的副作用（生成/放置/绑定）** 创建或修改任何 `.map` / `.model` / `.ui` 文件——**[references/builder-protocol.md](references/builder-protocol.md)（核心）加上每个被任务修改的文件类型的构建器文件——[references/builder-protocol-map.md](references/builder-protocol-map.md)（`.map`） / [references/builder-protocol-model.md](references/builder-protocol-model.md)（`.model`） / [references/builder-protocol-ui.md](references/builder-protocol-ui.md)（`.ui`）——必须在开始工作前完全处于上下文中**（上述阅读语义）。没有例外。

协议是一个统一的入口点，分为共享核心（`builder-protocol.md` — 路由、通用工作流程、链式合同、§0 预飞、§4 跨流、§5 清单）加上每个构建器文件（`builder-protocol-map.md` §1 / `builder-protocol-model.md` §2 / `builder-protocol-ui.md` §3）。**只知道一个构建器的协议然后调用另一个构建器的 `.cjs` 会绕过该构建器的写侧合同**（`componentNames` 同步、`Values` `typeKey` 元数据、写时自动检查、`placeModel` 组件镜像、子实体不变量）——三者通过跨流（模型创作 → 地图放置 → UI 绑定）相互锁定，因此跨流工作会加载每个匹配的构建器文件。

触发器（故意范围广泛——每当任何匹配时加载缺失的协议文件）：

- `.map` 变化（实体放置、组件修补、瓦片 / 立足点检查）
- `.model` 变化（新创作、值 / 组件 / 属性 / 子项编辑）
- `.ui` 变化（新构建、组件 CRUD、绑定注入）
- 任何对 `MapBuilder` / `ModelBuilder` / `UIBuilder` 的调用
- 形似“实体形状”的工作请求——怪物 / NPC / 投射物 / 地图对象 / 弹窗 / HUD 等
- 任何使用 `_SpawnService` 的代码（必须先创作并放置可生成模型）

领域引用（`entity.md` / `model.md` / `msw-ui-system` 设计引用）与协议文件**一起读取**——它们不是替代品（领域上下文 + 调用协议是一对）。**在每次触发时确认它们仍然处于上下文中**——仅重新读取从未加载或因压缩而丢失的内容。

---

## 模型工作预检——**必须**

如果任务涉及以任何方式创作或编辑 `.model` 文件——包括任何对 `ModelBuilder`（任何 API）的调用、从模板创建新模型、在现有模型上修改组件/值/属性/子项/事件链接，甚至一行修改——**[references/model.md](references/model.md) 必须在开始工作前完全处于上下文中**（上述阅读语义）。没有例外。

构建器的模板目录、3 个标识符替换规则（`EntryKey` / `Id` / `Name`）、所需值元数据、属性/子项/事件链接 API 表面以及 `RootDesk/MyDesk/Models/` 下类型化保存布局**仅存在于 [`references/model.md`](references/model.md) 中。在开始每个触摸 `.model` 的回合前，确认它仍然处于上下文中，并且仅当它丢失时才重新读取——调用构建器而不先阅读 [`references/model.md`](references/model.md) 会默默生成损坏的模型（缺少值元数据、标识符不匹配、保存文件夹错误、默认值静默失败）。从零开始阅读分散的模板文件或从记忆中猜测 API**不是替代品**——在每次触摸 `.model` 的回合开始时，确认它仍然处于上下文中，并且仅当它丢失时才重新读取。

---

## 地图工作预检（在任何地图工作之前做这个）

在开始**任何**与地图相关的任务——实体放置、生成、移动脚本、模型创作、瓦片编辑等——之前，你必须按顺序完成这两个步骤：

1. **确定目标地图**——它的路径（`./map/{mapname}.map`）、它的根实体及其在层级中的位置。
2. **使用 `MapBuilder` 读取 `MapComponent.TileMapMode` 作为数字**（调用协议：[`references/builder-protocol.md`](references/builder-protocol.md) 核心 + [`references/builder-protocol-map.md`](references/builder-protocol-map.md)）。记住这个值，以便会话剩余时间使用。

| 值 | 模式 | 必要的实体 | 不匹配/缺失的实体 Body 的运行时日志 |
|:--:|---|---|---|
| `0` | **TileMap**（MapleTile，侧视图 + Foothold） | `RigidbodyComponent` | `[LEA-3004] MissingComponent : 实体缺少 'RigidbodyComponent'。` |
| `1` | **RectTileMap**（RectTile，俯视图） | `KinematicbodyComponent` | `[LEA-3004] MissingComponent : 实体缺少 'KinematicbodyComponent'。` |
| `2` | **SideViewRectTileMap**（SideViewRectTile，侧视图瓦片） | `SideviewbodyComponent` | `[LEA-3004] MissingComponent : 实体缺少 'SideviewbodyComponent'。` |

**在任何情况下都不要在不知道当前 `TileMapMode` 的情况下开始地图工作。** 三种模式在 Body 组件、重力、碰撞和事件堆栈方面完全不同。不匹配几乎永远不会是编译时错误——它要么表现为静默失败（实体无法移动 / 穿过墙壁 / 不可见），要么表现为上述三个 `[LEA-3004] MissingComponent` 运行时日志之一。每当看到这三个消息之一时，首先怀疑**TileMapMode ↔ 实体 Body 不匹配**。

### 推荐正确的模式——在开始新地图或当前模式明显不适合用户目标时**必须**

每当用户描述他们想要构建的游戏/地图（新地图创作、制作横版卷轴、想要俯视地下城），或者你读取当前 `.map` 发现其 `TileMapMode` 不适合用户预期的游戏玩法时，**你必须明确向用户推荐适当的 `TileMapMode` 并解释原因**，然后再进行任何进一步的实体 / 模型 / 脚本工作。

使用此决策矩阵作为权威来源：

| 用户预期的游戏/游戏玩法 | 推荐 | 原因 |
|---|---|---|
| MapleStory 风格的横版卷轴动作 · 跳跃 · 梯子 · 自由放置的立足点（平台游戏） | **`0` MapleTile** | 侧视图 + 重力，`FootholdComponent` 线段平台——非网格，自由放置的平台 |
| 俯视 RPG · 迷宫 · 棋盘游戏 · 地下城爬行者 · Bomberman 风格 · RTS 风格 · 农场模拟 | **`1` RectTile** | 俯视 4 向自由移动，无重力，方形瓦片网格 |
| 基于瓦片的横版卷轴平台游戏 · Mario 风格的像素动作 · 侧视图解谜（方形瓦片侧视图） | **`2` SideViewRectTile** | 侧视图 + 瓦片网格上的重力（不是自由放置的立足点） |

**程序：**

1. 如果用户还没有告诉你他们想要什么类型的游戏，**在推荐模式之前先问**（一个简短的问题就足够了——例如“是俯视图，还是横版卷轴（跳跃/梯子）？地形是基于自由放置的立足点，还是方形瓦片网格？”）。
2. 一旦意图明确，**陈述推荐**（模式数字 + 名称 + 一句话的推理）以及用户将需要的匹配 Body / 地图组件（`[platform.md` §4 映射表](references/platform.md)）。
3. **尽早锁定选择**——稍后切换 `TileMapMode` 会清除地形，强制重新检查每个 Body / 移动脚本，并可能强制重新绘制所有瓦片（`[platform.md` §4 "切换地图类型时的注意事项"](references/platform.md)）。

### 切换 `TileMapMode`——**用户在 Maker 中操作，而不是 AI 直接编辑文件**

AI **绝不能**通过直接编辑 `.map` JSON 来翻转 `MapComponent.TileMapMode`。模式切换需要交换瓦片组件、重建立足点、转换瓦片数据格式并重置地形——所有这些都是 Maker 的内部操作。

**指导用户在 Maker 编辑器中执行此操作：**

1. 打开 Maker 编辑器的 **Hierarchy** 窗口。
2. **在 Hierarchy 中右键单击目标地图实体**。
3. 从上下文菜单中，**选择与目标模式匹配的“切换…”选项**（切换 TileMap / RectTileMap / SideViewRectTileMap）。Maker 执行转换，交换瓦片组件并按需重置地形。
4. 用户确认切换完成后，调用 MCP **`refresh`**，然后重新读取 `MapComponent.TileMapMode` 以验证并检查每个动态实体的 Body 组件是否与新模式匹配。

> AI 在模式切换中的角色：**推荐 → 等待用户在 Maker Hierarchy 中右键单击切换 → refresh → 修复不再匹配的 Body 组件 / 脚本。** 从来不要从文件编辑中写入新的值到 `TileMapMode`。

上表是摘要。**模式切换程序、切换 Body 后的检查清单以及 LEA-3004 之外的静默失败症状字典** 仅存在于 [`references/platform.md` §4](references/platform.md)（映射 + 检查协议 + 切换策略）和 [`references/troubleshooting.md`](references/troubleshooting.md)（完整症状字典）中——**你必须阅读它们** 在切换模式 / 交换 Body / 调试静默失败时。每种地图类型的详细模式：[`platform-maple.md`](references/platform-maple.md) / [`platform-rect.md`](references/platform-rect.md) / [`platform-sideview.md`](references/platform-sideview.md)。瓦片绘制：[`references/tile.md`](references/tile.md)。地图工作预检：[`references/entity.md`](references/entity.md)。

---

## 平台规则预检——当其中任何触发器触发时**必须**

如果以下触发条件中的**任何**一个与您的任务匹配，请在编辑代码或提出计划**之前**阅读相应的参考。这些触发条件是故意宽泛的——如有疑问，请阅读。本 SKILL.md 中的“8 核心规则”仅为摘要；**症状→原因→修复表格、按地图类型划分的代码模式、`MovementComponent` 转换公式以及 SortingLayer/SpriteRUID 的详细信息仅存在于参考中**。

| 触发条件（关键词/情况） | 阅读文件 |
|---|---|
| 跳跃、重力、移动、`MoveVelocity`、`InputSpeed`、`JumpForce`、`WalkSpeed`、`SpeedFactor`、落脚点、巡逻 | **匹配地图类型的** [`references/platform-maple.md`](references/platform-maple.md) / [`platform-rect.md`](references/platform-rect.md) / [`platform-sideview.md`](references/platform-sideview.md)（完整版）**+** [`references/platform.md`](references/platform.md) §10 |
| 生成 / `_SpawnService` / `SpawnByModelId` / `SpawnByEntity` / “召唤怪物” / “运行时创建” | [`references/platform.md`](references/platform.md) §8 + §8.5 |
| 屏幕坐标 / 相机范围 / “是否在屏幕上” / “像素单位” / OrthographicSize / 世界单位 | [`references/platform.md`](references/platform.md) §5 |
| 遮挡 / 不可见 / “应在顶部渲染” / SortingLayer / OrderInLayer / Z 值 | [`references/platform.md`](references/platform.md) §6 + §7 |
| 日志中的 `LEA-3004` / “无法移动” / “悬浮在空中” / “卡在墙里” / “弹开” / “消失在地图外” / “从落脚点边缘掉落” | **[`references/troubleshooting.md`](references/troubleshooting.md)（完整版）首先**，然后是匹配地图类型的 `platform-{type}.md` §7 |
| `LEA-3005 InvalidArgument 'stateName'` / `StateComponent` / `StateType` / `@State` / `ChangeState` / `AddState` / `AddCondition` / `ActionSheet` / `SetActionSheet` / `StateAnimationComponent` / `AvatarStateAnimationComponent` / `StateChangeEvent` / “动画未改变” / “移动时停留在站立/空闲状态” / “攻击姿态从未播放” / “击打动画循环” / 怪物·NPC·玩家动画状态工作 | **[`references/animation-state.md`](references/animation-state.md)（完整版）首先**，然后 [`references/monster.md`](references/monster.md)（或特定实体的文档）用于实体级别的组合 |
| 着色器 / 材质 / 轮廓 / 发光 / 模糊 / 像素化 / 彩虹 / 染色 / 灰度 / 背景暗角 / 屏幕滤镜 / 镜头畸变 / 波浪 / 涟漪 / 畸变 / 溶解 / 加性 / 混合模式 / 全息图 / 掩码 / 后处理 / `MaterialID` / `MaterialId` / `ChangeMaterial` / `_MaterialService` / `.material` 文件 | **[`references/material.md`](references/material.md)（完整版）** — 然后通过 `mlua_Document_Retriever` + `mlua_API_Retriever` MCP 查找来驱动着色器目录 / 属性名称 / 每个组件的兼容性（不要死记硬背） |
| 新地图设置 / 新项目 / `.config` / 核心版本验证 / 区域注册 / 文件夹元数据刷新 | [`references/platform.md`](references/platform.md) §2 + §15 + §16 |
| MapleTile (`TileMapMode = 0`) 工作 — 脚本点、`Gravity`、`WalkSpeed`、`PredictFootholdEnd` | [`references/platform-maple.md`](references/platform-maple.md)（完整版） |
| RectTile (`TileMapMode = 1`) 工作 — `SpeedFactor`、四向移动、可移动瓦片、动态瓦片 | [`references/platform-rect.md`](references/platform-rect.md)（完整版） |
| SideViewRectTile (`TileMapMode = 2`) 工作 — `JumpSpeed`/`JumpDrag`、墙检测（`Normal`）、`EnableDownJump` | [`references/platform-sideview.md`](references/platform-sideview.md)（完整版） |

> 如果两个或多个触发条件匹配，请阅读**所有**。 “我已经在 SKILL.md 中看到了 8 核心规则”不是跳过参考的理由。

---

## 8 核心规则（必须记忆）

1. 如果您没有对齐 **TileMapMode ↔ 身体映射**，实体将不会移动（无错误）或在运行时引发 `[LEA-3004] MissingComponent` → [`references/platform.md` §4](references/platform.md)（或如果按症状接近，则 [`references/troubleshooting.md`](references/troubleshooting.md)）
2. 用户脚本仅作为 `.mlua` + `.codeblock` **对**工作——`.codeblock` 由 Maker 刷新生成
3. 如果 `SpriteRUID` 是空字符串，实体在屏幕上**不可见**（无错误）
4. 调用 `SpawnByModelId` 时，未将地图实体（`self.Entity.CurrentMap`）作为 `parent` 传递会导致运行时错误
5. 坐标在世界单位中（1 单位 = 100 像素）。像素值相差 100 倍
6. Maker 仅扫描 `RootDesk/` — 用户放置在 `Global/` 中的文件不会被识别
7. **不要修改** `.d.mlua` 或 `.codeblock`。
8. 核心版本是 `26.7.0.0` — 如果存在不匹配，则无法工作

---

## MCP 工具快速参考（msw-maker-mcp）

| 工具 | 目的 |
|------|---------|
| **play** / **stop** | 进入 / 退出播放模式 |
| **refresh** | 文件更改后同步 Maker（播放模式下不允许） |
| **logs** / **clear_logs** | 读取 / 清除运行时和构建日志 |
| **screenshot** | 仅在用户明确要求时调用 |
| **keyboard_input** / **mouse_input** | 在播放模式下模拟输入 |

> 在 MCP 调用失败 / “MCP 连接” / “API Key”请求时 → 指导用户查阅官方设置文档：https://maplestoryworlds-creators.nexon.com/ko/docs?postId=1368

---

## 按任务路由——应阅读哪个参考

| 文件 | 范围 | 阅读时机 |
|------|-------|--------------|
| [workspace.md](references/workspace.md) | 世界实例 / 房间 / 数据存储、文件夹布局、文件路径、播放模式、`refresh`、工作流程中的中间失败恢复 | 工作区 / 实例 / 模式转换工作 |
| [platform.md](references/platform.md) (核心) | 8 核心规则、文件权限 + 文件夹元数据、`.mlua`+`.codeblock` 对、TileMapMode↔身体映射 + LEA-3004、坐标系 / 屏幕范围、SortingLayer/OrderInLayer、SpriteRUID、`SpawnByModelId` 使用 / 初始化顺序、`MovementComponent` 每个地图类型的 InputSpeed 转换公式、ECS、ID 生成、`.config`、核心版本 | TileMapMode 映射 / 模式切换 / 生成 / 坐标 / RUID / SortingLayer / `.config` & 核心版本 / 文件夹元数据 — **所有地图类型共有的规则** |
| [platform-maple.md](references/platform-maple.md) | 仅 MapleTile (`TileMapMode = 0`) — 脚本点物理、`Gravity`/`WalkSpeed`/`WalkJump`、`PredictFootholdEnd`、`IsOnGround`、`DownJump`、脚本点进入/离开事件、MapleTile 仅有的故障排除 + 检查清单 | 垂直卷轴动作 / 跳跃 / 梯子 / 自由放置的脚本点（MapleStory 风格的平台游戏） |
| [platform-rect.md](references/platform-rect.md) | 仅 RectTile (`TileMapMode = 1`) — `KinematicbodyComponent`、`SpeedFactor`、自由四向移动、仅视觉跳跃、可移动瓦片碰撞、`ToCellPosition`/`ToWorldPosition`、RectTile 进入/离开事件、动态瓦片（`SetTile`/`BoxFill`）、RectTile 仅有的故障排除 + 检查清单 | 俯视 RPG / 迷宫 / 棋盘游戏 / 地牢爬行 / Bomberman 风格 / RTS / 农场模拟 |
| [platform-sideview.md](references/platform-sideview.md) | 仅 SideViewRectTile (`TileMapMode = 2`) — `SideviewbodyComponent`、`JumpSpeed`/`JumpDrag`、`EnableDownJump`、墙检测（`RectTileCollisionBeginEvent` + `Normal`）、`GetUnderfootTile`、SideView 仅有的故障排除 + 检查清单 | 基于瓦片垂直卷轴平台游戏 / 马里奥风格像素动作 / 垂直卷轴解谜 |
| [troubleshooting.md](references/troubleshooting.md) | 统一症状词典 — `LEA-3004` 表格 / “无法移动” / “无法渲染” / “悬浮在空中” / “卡在墙里” / “消失在地图外” / “从脚本点边缘掉落” / “100×偏移” / “在 Maker 中不显示” / “客户端仅同步”和其他导致静默失败的症状→原因→修复统一索引 | **症状优先调试** — 当用户报告上述内容或日志中出现 `[LEA-3004]` 时，首先查阅此处 |
| [authoring.md](references/authoring.md) | 跨 5 种文件类型（模式一致性、手动编辑风险）的共享创作原则 | 任何文件创作前的入口点 |
| [tile.md](references/tile.md) | 瓦片绘制 — Maker UI 域，仅 AI 指南 | 瓦片图工作 |
| [**builder-protocol.md**](references/builder-protocol.md) (核心) + [builder-protocol-map.md](references/builder-protocol-map.md) / [builder-protocol-model.md](references/builder-protocol-model.md) / [builder-protocol-ui.md](references/builder-protocol-ui.md) | **`.map` / `.model` / `.ui` 的统一调用协议——核心：路由、通用工作流程、链式合同、§0 预飞行、§4 跨流程、§5 检查清单；每个构建器文件：MapBuilder §1 / ModelBuilder §2 / UIBuilder §3 API、覆盖差距、绑定注入** | **核心 + 匹配被修改类型的文件必须在每次修改 `.map` / `.model` / `.ui` 的回合中处于上下文中（Builder Protocol 预飞行）** |
| [entity.md](references/entity.md) | `.map` 实体域 — 范围、RUID、TileMapMode 预飞行、`modelId` 与内联决策规则、坐标 / 脚本点 / 相机、运行时验证 | `.map` 编辑 / 实体放置（与 builder-protocol.md 核心和 builder-protocol-map.md 一起阅读以了解调用协议） |
| [model.md](references/model.md) | `.model` 创作域 — 创建时机、模板目录、组件组合、脚本-组件生命周期 | 编写 / 编辑 `.model`（与 builder-protocol.md 核心和 builder-protocol-model.md 一起阅读以了解调用协议） |
| [monster.md](references/monster.md) | 怪物规范组件、小写 ActionSheet 键、强制 `IsLegacy` / `SortingLayer` 覆盖、AI 选择、HP/重生、生成位置 | 创作怪物模型 |
| [animation-state.md](references/animation-state.md) | StateComponent 默认值 & 自动注册、状态变更管道、`SetActionSheet` vs `ChangeState`、`StateType` 创作（服务器端，`ParentComponent.Entity`）、`StateAnimationComponent`（怪物/NPC）vs `AvatarStateAnimationComponent`（玩家）、`[LEA-3005]` 陷阱 | 任何状态 / 动画问题（跨怪物、NPC 或玩家）——每当实体的动画与其行为不匹配时，首先阅读 |
| [material.md](references/material.md) | `.material` 文件结构、着色器类别索引（10+ 类别）、通过 `.model` / `.map` / 运行时 `ChangeMaterial` 在渲染器组件上应用 `MaterialID`、`_MaterialService:ChangeMaterialProperty`（客户端仅）、以及**由 MCP 驱动的查找循环（`mlua_Document_Retriever` / `mlua_API_Retriever`）来替代记忆每个着色器目录** | 任何着色器 / 材质 / 视觉效果工作——轮廓、发光、模糊、背景暗角、彩虹、全息图、混合模式、后处理、击打闪光、屏幕滤镜等 |
| `msw-ui-system` 技能（通过 `Skill` 工具调用） | **单一 UI 入口点。** 设计判断（坐标/锚点/枢轴、UIGroup/CanvasGroup、组件选择）+ 组件属性/方法/事件 API + 枚举值 + 布局配方 + mlua 运行时模式（弹窗/提示/HP/网格/拖动）+ 运行时 UI 陷阱 + UUID 绑定 + **`.ui` CJS UIBuilder 调用协议**（面板/文本/精灵/按钮/滑块/滚动/脚本/组/掩码/网格/头像/触摸/骨骼/粒子，锚点预设，组件添加/替换/修补/删除，编写时自动 lint） | 任何与 UI 相关的任务 / 创建或编辑 `.ui` 文件——**首先阅读** |
| `msw-ui-system/references/templates` 文件 | 按复杂度分级的 UI 结构模式模板（简单弹窗、最小 HUD、多标签页、商店/购买流程）包含 `.ui` + `.mlua` 示例和按钮处理程序模式 | 添加新的 UI 组/弹窗/HUD、结构化按钮处理程序或选择 UI 布局模式（在 `msw-ui-system` 之后直接阅读） |
| [dataset.md](references/dataset.md) | 用户数据集 / 本地化数据集运行时、`.userdataset` + `.csv` 对、**`_LocalizationService` 是客户端仅**、`serveronly` | 数据集 / i18n / 翻译 |

---

## 绝对原则（适用于每个任务）

0. **如果任务涉及实体，请先阅读 [参考资料/实体.md](references/entity.md)。无一例外。**
0-bis. **如果用户的请求提及任何 UI 元素**（弹窗、HUD、按钮、提示、面板、对话框窗口、菜单、标签页、布局、屏幕、条形/仪表盘、槽位）**或涉及编写/编辑 `.ui` 文件**，**在向用户提出任何计划、选项或问题之前**：
   1. **首先通过 `Skill` 工具调用 `msw-ui-system`** — 单一 UI 入口（设计判断、组件 API、枚举、布局配方、运行时模式、UUID 绑定、构建器调用协议统一在一个技能中）。
   2. **所有 `.ui` 变更必须通过 `msw-ui-system` 的 `UIBuilder`** — 不得直接原始 JSON 编辑或使用 `grep`。通过 `UIBuilder` 的读端 API 读取现有的 `.ui` 文件。（调用协议：[参考资料/构建器协议.md](references/builder-protocol.md) 核心 + [参考资料/构建器协议-ui.md](references/builder-protocol-ui.md) §3。）
   3. （可选）如果您需要 UI 模板（简单弹窗、最小 HUD、多标签页、商店流程），直接 `Read`/`Glob` `msw-ui-system/references/templates/` 下的文件（[模板.md](../msw-ui-system/references/templates/templates.md) + `style-N-*/` + [ruid-map.md](../msw-ui-system/references/templates/style-1-black/ruid-map.md) + `Popupbutton.mlua`）。
   无一例外。
0-ter. **如果任务将创建、修改、重命名或删除任何 `.mlua` 文件** — 包括新脚本、现有脚本编辑、添加/删除 `Component`/`@Logic`/`@Event`/`@State`/`@BTNode`、连接生命周期方法（`OnBeginPlay`/`OnUpdate`/...），甚至单行小修复 — 您**必须先完整阅读** [`msw-scripting/SKILL.md`](../msw-scripting/SKILL.md) 和 [`msw-scripting/参考资料/验证清单.md`](../msw-scripting/references/verify-checklist.md)（不得使用 `offset`/`limit`，不得使用 `cat`/`Get-Content`）。阅读 `msw-general` 加上分散的 `.d.mlua` 文件**不能替代**。即使上一轮已经加载了 `msw-scripting` — 在新轮开始时重新确认。**触发短语故意写得宽泛**：如果这一轮有任何可能触及 `.mlua` 的机会，就视为触发。无一例外，不得说“我已经知道这个”，不得通过记忆走捷径。
0-quater. **如果任务涉及生成、移动、跳跃/重力、坐标放置、层级/顺序调试、MapleTile/RectTile/SideViewRectTile 特定逻辑，或您观察到任何静默失败症状（`[LEA-3004]` 日志，“无法移动”、“无法渲染”、“悬浮在空中”、“卡在墙里”、“消失出地图”、“从立足点边缘掉落”、“100 倍偏移”、“不在 Maker 中显示”、“仅客户端同步”），必须先完整理解匹配的 `参考资料/platform*.md` / [`参考资料/故障排除.md`](references/troubleshooting.md)（仅当缺失时读取——见“预读语义”）。**此外，如果症状与动画/状态相关（`[LEA-3005]` 日志，`'stateName' 不是有效参数`，动画与行为不匹配，移动时卡在站立/空闲剪辑中，攻击姿势从未播放，命中循环，自定义状态从未动画化，任何接触 `StateComponent` / `StateType` / `ChangeState` / `AddState` / `ActionSheet` / `SetActionSheet` / `StateAnimationComponent` 的内容），必须先完整理解 [`参考资料/动画状态.md`](references/animation-state.md) 才能进行任何代码或模型编辑。本技能.md 中的 8 条核心规则仅为摘要——**症状→原因→修复表、按地图类型划分的代码模式（立足点巡逻 / RectTile 四向移动 / SideView 墙壁检测）、`MovementComponent` 输入速度转换公式、SpriteRUID、SortingLayer/OrderInLayer 细节、`SpawnByModelId` 初始化顺序、文件夹元数据刷新策略、CoreVersion 策略仅在参考资料中存在。** **触发短语故意写得宽泛**：如果这一轮有任何可能触及这些领域的机会，就视为触发。对于匹配的 `Read` 目标，请遵循上述“平台规则预读 — 必须触发”部分中的触发表。无一例外，不得说“我从 8 条核心规则中已经知道”，不得通过记忆走捷径。
1. **视觉优化** — 不要让 `SpriteRUID` 为空。使用 `msw-search` 查找资源。
2. **内容文件变更后 `refresh`（如果 Maker 必须摄入**）（如果在游戏模式中，先 `stop`）。仅文件夹变更无需立即刷新。
3. **永远不要修改 `Environment/*.d.mlua`** — API 定义是只读的。
4. **永远不要手动创建 `.codeblock`** — Maker `refresh` 会从 `.mlua` 生成它。文件夹元数据也是在刷新期间从真实文件夹生成的。
5. **不要在 `Global/` 中创建新用户文件** — Maker 将无法识别它们。用户文件应放在 `RootDesk/MyDesk/` 下。
6. **结构化文件优先使用构建器，调用手册是统一的入口点 — 共享核心加上每个构建器的文件** — `.model` / `.ui` 仅限构建器；`.map` 优先使用构建器。**所有三个构建器（`MapBuilder` / `ModelBuilder` / `UIBuilder`）的调用协议在 [`参考资料/构建器协议.md`](references/builder-protocol.md)（核心）加上每个构建器的文件（[参考资料/构建器协议-map.md](references/builder-protocol-map.md) / [参考资料/构建器协议-model.md](references/builder-protocol-model.md) / [参考资料/构建器协议-ui.md](references/builder-protocol-ui.md)）中整合。每一轮修改 `.map` / `.model` / `.ui` 时，必须完整理解核心加上匹配变更类型的文件**（见构建器协议预读）。仅允许在构建器文件中明确列出的覆盖间隙区域进行直接原始 JSON 编辑 — 最小范围 + `refresh` + 日志验证。
7. **实体引用绑定（Entity/EntityRef 属性）** — AI 直接注入 UUID 字符串。不要要求用户在 Maker 中拖入。
8. **CoreVersion 不匹配时停止工作** — 首先验证 `Environment/config` 中的 `CoreVersion` 是否为 `26.7.0.0`。
9. **仅在用户明确要求时调用 `screenshot`。** 任务完成后不得自动调用。
10. **如果工作流程步骤中途失败，停止后续步骤** — 首先修复根本原因。
11. **两个或更多 = 制作模型。** 每当同一实体组合在地图中放置 ≥2 次，先创建 `.model` 并通过 `modelId` 实例化。内联 `@components` 重复保留用于真正的单个实体。
12. **模型存放在类型子文件夹中。** 将新的 `.model` 文件保存在 `RootDesk/MyDesk/Models/` 的分类子文件夹下（例如 `Models/Monsters/`，`Models/NPCs/`，`Models/Terrain/`，`Models/MapObjects/`，`Models/Particles/`，`Models/UI/`）— **绝不能直接放在 `MyDesk/` 或 `Models/` 下**。当需要的子文件夹不存在时，仅创建文件夹；Maker Refresh 会稍后生成文件夹元数据（见 [参考资料/平台.md §2](references/platform.md)）。
13. **翻译仅限客户端。** `_LocalizationService` 和 `Translator` 方法（`GetText` / `GetTextFormat`）都是 `ClientOnly`。对于服务器端发起的本地化消息，发送键值通过 RPC，让客户端解析。
14. **跨平台工具选择 — 不用于工作区探索的 shell，使用工具。** 使用 **`Glob` / `Read` / `Grep` 工具** 进行所有工作区文件/文件夹探索、读取和搜索。`Bash` 命令如 `ls` / `dir` / `Get-ChildItem` / `gci` / `cat` / `type` / `Get-Content` / `gc` / `head` / `tail` / `find` / `where` / `grep` / `findstr` / `Select-String` **禁止用于工作区探索** — 它们不兼容 Windows（PowerShell/Git Bash）和 macOS（bash/zsh），由于 shell/路径处理差异（特别是，在 bash 中，路径如 `D:\path\foo` 的反斜杠会被消耗为转义符并折叠为 `D:pathfoo`）。仅用于**实际 shell 程序（`git` / `npm` / MCP / 构建脚本）**，即使如此：(a) 优先使用**工作区相对路径**，(b) 如果绝对路径不可避免，使用**正斜杠 + 双引号**（`"D:/path/to/map/"`，绝不能传递 `D:\...` 形式），(c) 仅使用**POSIX 命令**（`ls` / `mv` / `cp` / `rm`）。如果您看到类似 `ls: cannot access 'D:path...': No such file or directory` 的错误，立即停止并重试 `Glob` / `Read`。
15. **`.model` 文件仅限构建器** — 构建器需要 [`参考资料/模型.md`](references/model.md)（领域）加上 [`参考资料/构建器协议.md`](references/builder-protocol.md) 核心和 [`参考资料/构建器协议-model.md`](references/builder-protocol-model.md)（调用协议）先。不得直接检查或编辑 `.model` JSON。**在使用 `ModelBuilder` 之前，所有这些文档必须完整理解**（上述读语义）— 既是“模型工作预读”也是“构建器协议预读”都会触发。当它们一起读取时，标识符/值元数据/属性/子项/事件链接的一致性才有保证。
16. **`.map` 文件优先使用构建器。** 使用 `MapBuilder` 进行覆盖的检查和变更，以保持实体 ID、路径、组件名称、原点元数据、模型实例镜像的一致性。如果 `MapBuilder` 明确不覆盖所需的操作，进行最小的直接 `.map` 编辑，然后 `refresh` 并验证。**完整 API / 需求路径 / 每个操作模式 / 覆盖间隙 / `false` 返回处理 / 跨流程：[参考资料/构建器协议-map.md](references/builder-protocol-map.md) §1 + [参考资料/构建器协议.md](references/builder-protocol.md) §4**（与 [参考资料/实体.md](references/entity.md) 一起阅读以获取领域上下文）。
