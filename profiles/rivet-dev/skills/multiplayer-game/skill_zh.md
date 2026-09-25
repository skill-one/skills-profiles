# 多人游戏

**重要提示：在进行任何操作之前，你必须阅读此技能目录中的 `BASE_SKILL.md`。它包含有关调试、错误处理、状态管理、部署和项目设置的必要指导。这些规则和模式适用于所有 RivetKit 工作。以下内容假设你已经阅读并理解了它。**

## 工作示例

如果你需要一个参考实现，请阅读这些模板中的原始工作示例代码：

- [multiplayer-game-patterns](https://github.com/rivet-dev/rivet/tree/main/examples/multiplayer-game-patterns)

使用 RivetKit 构建多人游戏的模式，旨在作为一个你可以根据游戏类型进行调整的实际清单。

## 启动代码

从 [GitHub](https://github.com/rivet-dev/rivet/tree/main/examples/multiplayer-game-patterns/src/actors/) 上的一个工作示例开始，并根据你的游戏进行修改。不要从零开始进行匹配和生命周期流。

| 游戏分类 | 启动代码 | 常见示例 |
| --- | --- | --- |
| 大逃杀 | [GitHub](https://github.com/rivet-dev/rivet/tree/main/examples/multiplayer-game-patterns/src/actors/battle-royale/) | Fortnite, Apex Legends, PUBG, Warzone |
| 决斗场 | [GitHub](https://github.com/rivet-dev/rivet/tree/main/examples/multiplayer-game-patterns/src/actors/arena/) | Call of Duty TDM/FFA, Halo Slayer, Counter-Strike casual, VALORANT unrated, Overwatch Quick Play, Rocket League |
| IO 风格 | [GitHub](https://github.com/rivet-dev/rivet/tree/main/examples/multiplayer-game-patterns/src/actors/io-style/) | Agar.io, Slither.io, surviv.io |
| 开放世界 | [GitHub](https://github.com/rivet-dev/rivet/tree/main/examples/multiplayer-game-patterns/src/actors/open-world/) | Minecraft survival servers, Rust-like worlds, MMO zone/chunk worlds |
| 派对 | [GitHub](https://github.com/rivet-dev/rivet/tree/main/examples/multiplayer-game-patterns/src/actors/party/) | Fall Guys private lobbies, custom game rooms, social party sessions |
| 2D 物理模拟 | [GitHub](https://github.com/rivet-dev/rivet/tree/main/examples/multiplayer-game-patterns/src/actors/physics-2d/) | Top-down physics brawlers, 2D arena games, platform fighters |
| 3D 物理模拟 | [GitHub](https://github.com/rivet-dev/rivet/tree/main/examples/multiplayer-game-patterns/src/actors/physics-3d/) | Physics sandbox sessions, 3D arena games, movement playgrounds |
| 排名赛 | [GitHub](https://github.com/rivet-dev/rivet/tree/main/examples/multiplayer-game-patterns/src/actors/ranked/) | Chess ladders, competitive card games, duel arena ranked queues |
| 回合制 | [GitHub](https://github.com/rivet-dev/rivet/tree/main/examples/multiplayer-game-patterns/src/actors/turn-based/) | Chess correspondence, Words With Friends, async board games |
| 消磨时间 | [GitHub](https://github.com/rivet-dev/rivet/tree/main/examples/multiplayer-game-patterns/src/actors/idle/) | Cookie Clicker, Idle Miner Tycoon, Adventure Capitalist |

## 服务器模拟

### 游戏循环和帧率

| 模式 | 使用场景 | 实现指导 |
| --- | --- | --- |
| 固定实时循环 | 大逃杀、决斗场、IO 风格、开放世界、排名赛 | 在 `run` 中运行，使用 `sleep(tickMs)` 并在 `c.aborted` 时退出。 |
| 行动驱动更新 | 派对、回合制 | 仅在行动/事件上变异和广播，而不是按计划的时间间隔。 |
| 粗粒度离线进度 | 任何具有消磨时间进度的模式 | 使用 `c.schedule.after(...)` 并使用粗粒度窗口（例如 5 到 15 分钟），并从经过的墙时间中应用追赶。 |

### 物理

对于简单的游戏，从自定义运动逻辑开始。当你需要关节、堆叠的物体、高碰撞密度或复杂形状（旋转的多边形、胶囊、凸包、三角形网格）时，切换到完整的物理引擎。

每个模拟选择一个引擎。将前端库排除在服务器模拟路径之外，并将服务器状态视为权威状态。

| 维度 | 主要引擎 | 备用引擎 | 示例代码 |
| --- | --- | --- | --- |
| 2D | `@dimforge/rapier2d` | `planck-js`, `matter-js` | [GitHub](https://github.com/rivet-dev/rivet/tree/main/examples/multiplayer-game-patterns/src/actors/physics-2d/) |
| 3D | `@dimforge/rapier3d` | `cannon-es`, `ammo.js` | [GitHub](https://github.com/rivet-dev/rivet/tree/main/examples/multiplayer-game-patterns/src/actors/physics-3d/) |

### 空间索引

对于非物理空间查询，使用专用索引而不是简单的 `O(n^2)` 检查：

| 索引类型 | 推荐 |
| --- | --- |
| AABB 索引 | 对于 AOI、可见性和非碰撞实体，使用 `rbush` 用于动态集或 `flatbush` 用于静态集。 |
| 点索引 | 对于最近邻或半径内查询，使用 `d3-quadtree`。 |

## 网络和状态同步

### 网络代码

| 模式 | 使用场景 | 实现 |
| --- | --- | --- |
| 混合（客户端移动，服务器战斗） | 射击游戏、动作运动、排名对决 | 客户端拥有移动并发送速率限制的位置更新。服务器进行反作弊验证。战斗（投掷物、命中、伤害）完全由服务器权威控制。 |
| 服务器权威带插值 | IO 风格、持久世界 | 客户端发送输入命令。服务器在固定时间间隔上模拟并发布权威快照。客户端在快照之间进行插值。 |
| 服务器权威（基本逻辑） | 回合制、事件驱动 | 服务器验证并应用离散动作（回合、阶段转换、投票）。客户端显示确认状态。 |

### 实时数据模型

- **快照和差异**：作为事件发布状态。在加入/重同步时发送完整快照，然后按时间间隔发送常规更新。
- **每帧批量**：保持事件小而类型化。每帧批量高频更新。
- **避免 UI 框架状态用于游戏更新**：使用 `requestAnimationFrame` 或 Canvas/Three.js 循环进行模拟，而不是 React 状态。保留 UI 框架状态用于菜单、HUD 和表单。
- **广播与每连接**：使用 `c.broadcast(...)` 用于共享更新，使用 `conn.send(...)` 用于私有/每玩家数据。

### 共享模拟逻辑

共享模拟逻辑在客户端和服务器上运行。例如，一个 `applyInput(state, input, dt)` 函数，该函数集成速度并限制在世界边界内，可以在客户端运行以进行预测，在服务器上运行以进行验证。

- **混合模式**：客户端作为主要权威运行共享移动，服务器运行它以进行反作弊验证。
- **服务器权威模式**：客户端仅用于插值和预测的共享逻辑。
- **保持纯函数**：运动集成、输入转换、碰撞辅助和常量。
- **将共享代码放在 `src/shared/`**：将确定性辅助工具放在 `src/shared/sim/*` 中，没有任何副作用。

## 后端基础设施

### 持久化

- **内存状态**：最佳用于每帧变化的实时游戏状态（玩家位置、输入、匹配阶段、分数）。
- **SQLite (`rivetkit/db`)**：适用于需要查询、索引或长期持久化的较大或表格化状态（瓦片、库存、匹配池）。通过队列序列化 DB 工作，因为多个操作可以同时命中相同的演员。

### 匹配模式

跨以下架构模式使用的常见构建块。

#### 演员拓扑

| 基本类型 | 使用场景 | 典型所有权 |
| --- | --- | --- |
| `matchmaker["main"]` + `match[matchId]` | 基于会话的多人游戏（大逃杀、决斗场、排名赛、派对、回合制） | 匹配器拥有发现/分配。匹配拥有生命周期和游戏状态。 |
| `chunk[worldId,chunkX,chunkY]` | 需要分片的连续大型世界 | 每个块拥有本地玩家、块状态和本地模拟。 |
| `world[playerId]` | 每个玩家进度循环（消磨时间/单人世界状态） | 每个玩家的资源、建筑、计时器和进度。 |
| `player[username]` | 在多个匹配/玩家中重复使用的规范配置文件/评分 | 持久玩家统计（例如评分和胜/负）。 |
| `leaderboard["main"]` | 跨许多匹配/玩家共享排名 | 全局排序分数行和顶级列表。 |

#### 队列策略

- 多个玩家可以同时命中匹配器，因此像查找/创建、排队/取消排队和关闭这样的操作需要通过演员队列进行序列化以避免竞争。
- 匹配本地操作（游戏玩法、计分）不需要队列，除非它们写回匹配器。

## 安全和反作弊

从这个基线开始，然后针对竞争性或高风险环境进行加固。

### 基线检查清单

- **身份**：使用 `c.conn.id` 作为权威的传输身份。将参数中的 `playerId`/`username` 视为不受信任的输入，并通过服务器发布的分配/加入票证进行绑定。
- **授权**：验证调用者是否有权变异目标实体（房间成员资格、回合所有权、仅主机操作）。
- **输入验证**：限制大小/长度，验证枚举，并验证用户名（长度、允许的字符，避免无界的 Unicode）。
- **速率限制**：每连接速率限制用于频繁的垃圾邮件操作（聊天、加入/离开、射击、移动更新）。
- **状态完整性**：服务器重新计算派生状态（分数、胜利条件、排名）。永远不允许客户端权威更改库存/货币/排行榜总数。

### 移动验证

对于任何具有客户端权威移动的模式（混合流），客户端可以发送位置/旋转更新以实现平滑性，但服务器必须：

- 执行每个更新的最大增量（速度限制）基于经过的时间。
- 拒绝或限制传送。
- 执行世界边界（如果适用，则执行基本碰撞）。
- 限制更新频率（例如最大 20Hz）。
