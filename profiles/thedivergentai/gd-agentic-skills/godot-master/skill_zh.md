# Godot 大师：架构师知识中心

每个部分都通过专注于**知识差值**来赚取代币——即基础模型已经知道的内容与高级 Godot 工程师从实际产品中了解的内容之间的差距。

## 库目标 — Godot 4.7+

所有领域技能镜像的目标都是**Godot 4.7+**（稳定）。对于**任何引擎版本升级**（1.x/2.x 遗留 → 3→4 → 4.x 跳跃），请使用**[godot-version-migration](https://github.com/thedivergentai/gd-agentic-skills/blob/main/skills/godot-version-migration/SKILL.md)**——不要将此知识中心视为迁移变更日志。

在路由时提供 4.7 的跨领域提醒：**AreaLight3D** / HDR → [3D Lighting](references/3d-lighting.md)；Asset Store vs Asset Library → 导出/平台模块；RichTextLabel ImageUnit, 输入设备 ID 常量, Jolt 行为 → 迁移中心模块说明。

---

## 🧠 第一部分：专家思维框架

### “谁拥有什么？”——架构 sanity 检查
在编写任何系统之前，为每一片状态回答以下三个问题：
- **谁拥有数据？**（`StatsComponent` 拥有生命值，而不是 `CombatSystem`）
- **谁被允许更改它？**（只能通过公共方法，如 `apply_damage()`）
- **谁需要知道它已更改？**（任何监听 `health_changed` 信号的人）

如果你无法回答这三个问题中的每一个状态变量，那么你的架构存在耦合问题。这不是面向对象的封装——这是 Godot 特有的，因为信号系统是执行机制，而不是访问修饰符。

### Godot “层饼”
将每个功能组织成四个层。信号向上传播，从不向下传播：
```
┌──────────────────────────────┐
│  PRESENTATION (UI / VFX)     │  ← 监听信号，从不拥有数据
├──────────────────────────────┤
│  LOGIC (状态机)              │  ← 协调转换，查询数据
├──────────────────────────────┤
│  DATA (资源 / .tres)         │  ← 单一事实来源，可序列化
├──────────────────────────────┤
│  INFRASTRUCTURE (Autoloads)  │  ← 信号总线, SaveManager, AudioBus
└──────────────────────────────┘
```
**关键规则**：Presentation 必须直接修改 Data。Infrastructure 专门通过信号进行通信。如果一个 `Label` 节点调用 `player.health -= 1`，那么架构是错误的。

### 信号总线分层架构
- **全局总线 (Autoload)**：仅用于生命周期事件 (`match_started`, `player_died`, `settings_changed`)。调试蔓延是代价——限制事件数量在 < 15。
- **作用域功能总线**：每个功能文件夹都有自己的总线（例如，`CombatBus` 仅用于战斗节点）。这是可扩展性的折衷方案。
- **直接信号**：父级与子级在单个场景内的通信。永远不会跨场景边界。

### “智能互连”命令
专家系统不是由它们的隔离定义的，而是由它们的**有效载荷合成**定义的。
- **物理 → 性能**：`PhysicsServer2D` 和 `RenderingServer` 绕过 `SceneTree` 节点开销。用于 1,000+ 弹药或粒子以实现 O(1) 处理。
- **动画 → 物理**：`AnimationTree.get_root_motion_position()` 将动画位移转换为物理 `velocity`，防止复杂移动中的“脚滑动”。
- **数据 → 反应性**：序列化的 `Resource` 对象（如 `Stats`）在修改时发出信号，允许 UI 自动更新而无需紧密耦合。
- **资源 → 生成**：基于字典的 O(1) 缓存（在 `ResourceLoader` 异步阶段预加载），防止生成物品或敌人时的 I/O 崩溃。
- **移动端 → 视觉**：通过在加载屏幕期间实例化隐藏效果来防止运行时帧率下降，以强制 GPU 着色器管道编译。
- **网络 → 带宽**：使用位打包到 `PackedByteArray` 进行同步，而不是 JSON/字符串，以保持数据包小于 100 字节。
- **流派合成**：
    - `射击`：严格使用 `intersect_ray()`（直接空间状态）而不是 `RayCast3D` 节点以获得 100 倍的性能。
    - `RPG`：伤害遵循 `base * pow(scaling, level)` 以维持终局进度。
    - `RTS`：基于它们的质心移动组，使用 `Relative Offset` 以保持队形完整性。
    - `Metroidvania`：使用 `ResourceLoader.load_threaded_request()` 进行无缝房间切换。
    - `平台游戏`：强制 `Jump Buffering` (~0.15s) 和 `Coyote Time` 以获得专业感觉。
    - `模拟`：`Tick Manager` 批处理；避免每个实体 `_process` 以维持数千个单位。
    - `浪漫`：`多轴情感`（吸引力, 信任, 舒适）以映射复杂的叙事分支。
    - `建筑`：`信号架构`严格遵循 `信号向上，调用向下` 以消除场景循环耦合。

---

## 🧭 第二部分：架构决策框架

### 主决策矩阵

| 情景 | 策略 | **强制** 技能链 | 权衡 |
| :--- | :--- | :--- | :--- |
| **快速原型** | 事件驱动单体 | **阅读**：[基础知识](references/project-foundations.md) → [Autoloads](references/autoload-architecture.md)。**不要加载**流派或平台引用。 | 快速启动，意大利面风险 |
| **复杂 RPG** | 组件驱动 | **阅读**：[组合](references/composition.md) → [状态](references/state-machine-advanced.md) → [RPG Stats](references/rpg-stats.md)。**不要加载**多人或平台引用。 | 重型设置，无限扩展 |
| **大型开放世界** | 资源流式传输 | **阅读**：[开放世界](references/genre-open-world.md) → [Save/Load](references/save-load-systems.md)。还加载 [性能](references/performance-optimization.md)。 | 复杂 I/O，浮点精度抖动超过 10K 个单位 |
| **服务器验证多人** | 确定性 | **阅读**：[服务器架构](references/server-architecture.md) → [多人网络](references/multiplayer-networking.md)。**不要加载**单人游戏流派引用。 | 高延迟，反作弊安全 |
| **移动端/网络移植** | 自适应响应 | **阅读**：[UI 容器](references/ui-containers.md) → [适应桌面→移动](references/adapt-desktop-to-mobile.md) → [平台移动](references/platform-mobile.md)。 | UI 复杂性，广泛覆盖 |
| **应用程序/工具** | 应用组合 | **阅读**：[应用组合](references/composition-apps.md) → [主题](references/ui-theming.md)。**不要加载**游戏特定引用。 | 与游戏不同的范式 |
| **浪漫 / 恋爱模拟** | 情感经济 | **阅读**：[浪漫](references/genre-romance.md) → [对话](references/dialogue-system.md) → [UI 富文本](references/ui-rich-text.md)。 | 高 UI/叙事密度 |
| **秘密 / 蛋糕** | 故意混淆 | **阅读**：[秘密](references/mechanic-secrets.md) → [持久化](references/save-load-systems.md)。 | 社区参与，调试风险 |
| **收集任务** | 搜集逻辑 | **阅读**：[收集](references/game-loop-collection.md) → [Marker3D Placement](references/3d-world-building.md)。 | 玩家保留，探索驱动 |
| **季节性活动** | 运行时注入 | **阅读**：[复活主题](references/theme-easter.md) → [材质交换](references/3d-materials.md)。 | 快速品牌，没有资源污染 |
| **魂系死亡** | 风险回报复活 | **阅读**：[复活/尸体跑](references/mechanic-revival.md) → [物理 3D](references/physics-3d.md)。 | 高张力，玩家挫败风险 |
| **基于波浪的动作** | 战斗节奏循环 | **阅读**：[波浪](references/game-loop-waves.md) → [战斗](references/combat-system.md)。 | 逐步增加张力，遭遇设计 |
| **平衡 / 难度 / 经济节奏** | Monte Carlo 平衡实验室 | **阅读**：[资源](references/resource-data-patterns.md) → [经济](references/economy-system.md) → [战斗](references/combat-system.md) / [RPG Stats](references/rpg-stats.md) / [波浪](references/game-loop-waves.md)（按需）→ [Monte Carlo 平衡器](references/monte-carlo-balancer.md) → [测试](references/testing-patterns-expert-testing-patterns.md) → [构建器](references/builder.md)。 | 统计严谨性；抽象模拟必须校准与 headless Godot 对比 |
| **生存经济** | 收获循环 | **阅读**：[收获](references/game-loop-harvest.md) → [背包](references/inventory-system.md)。 | 资源稀缺，循环持久性 |
| **赛车 / 速通** | 验证循环 | **阅读**：[计时赛](references/game-loop-time-trial.md) → [输入缓冲](references/input-handling.md) → [流派赛车](references/genre-racing.md)。 | 高精度，幽灵记录驱动 |
| **恐怖 / 隐行** | 紧张管理 | **阅读**：[流派恐怖](references/genre-horror.md) → [流派隐行](references/genre-stealth.md) → [音频](references/audio-systems.md)。 | 氛围，玩家脆弱性 |
| **卡牌 / 棋盘游戏** | 规则执行 | **阅读**：[流派卡牌游戏](references/genre-card-game.md) → [回合系统](references/turn-system.md)。 | 确定性状态，UI 繁重 |
| **模拟 / RTS** | 批处理 | **阅读**：[流派模拟](references/genre-simulation.md) → [流派 RTS](references/genre-rts.md) → [性能优化](references/performance-optimization.md)。 | 高单元数量，O(1) 逻辑 |
| **HDR / 电影级视觉效果** | 显示管道 | **阅读**：[3D Lighting](references/3d-lighting.md) → [平台桌面](references/platform-desktop.md) → [着色器](references/shaders-basics.md)。在项目设置中启用视口 HDR。 | 平台特定的色调映射调整 |
| **矩形区域光** | AreaLight3D | **阅读**：[3D Lighting](references/3d-lighting.md) → [3D 材质](references/3d-materials.md)。优先使用 AreaLight3D 而不是 emissive+GI 黑客。 | 需要 Forward+ 渲染器才能获得完整质量 |
| **移动端触摸控制** | 原生摇杆 | **阅读**：[平台移动](references/platform-mobile.md) → [适应桌面→移动](references/adapt-desktop-to-mobile.md)。使用内置虚拟摇杆（4.7+）。 | 更少的插件依赖 |
| **插件 / 资产发现** | 资源商店 | **阅读**：[项目基础知识](references/project-foundations.md) → [导出构建](references/export-builds.md)。资源商店取代资源库。 | Beta 商店 UI — 验证每个插件的许可 |
| **代理眼睛 / 视觉 QA** | 捕获 → WebP → 评分 | **阅读**：[代理视觉](references/agent-vision.md)。屏幕截图资产，窗口/区域/屏幕，或临时编辑器桥接——然后进行结构化审查。**不要加载**流派引用。 | 仅主机端；永远不会 Autoload / 永远不要留下已标记的插件 |

### “何时不使用节点”决策
最具影响力的专家决策之一。Godot 文档明确说明“避免使用节点处理所有内容”：

| 类型 | 使用 | 成本 | 专家用例 |
| :--- | :--- | :--- | :--- |
| **`Object`** | 自定义数据结构，手动内存管理 | 最轻。必须手动调用 `.free()`。 | 自定义空间哈希映射，ECS 风格数据存储 |
| **`RefCounted`** | 瞬态数据包，逻辑对象自动删除 | 当没有引用剩余时自动删除。 | `DamageRequest`, `PathQuery`, `AbilityEffect`——不需要场景树的逻辑数据包 |
| **`Resource`** | 可序列化数据，具有 Inspector 支持 | 比 RefCounted 稍微重。处理 `.tres` I/O。 | `ItemData`, `EnemyStats`, `DialogueLine`——任何设计师应该在 Inspector 中编辑的数据 |
| **`Node`** | 需要`_process`/`_physics_process`，需要存在于场景树中 | 最重——每个节点都有 SceneTree 开销。 | 仅用于需要每帧更新或空间变换的实体 |

**专家模式**：使用 `RefCounted` 子类用于所有逻辑数据包和数据容器。保留 `Node` 用于必须存在于空间树中的内容。这可以将复杂系统的场景树开销减半。

---

## 📊 第五部分：性能预算（具体数字）

| 指标 | 移动端目标 | 桌面端目标 | 专家注释 |
| :--- | :--- | :--- | :--- |
| **绘制调用** | < 100 (2D), < 200 (3D) | < 500 | `MultiMeshInstance` 用于灌木丛/碎片 | |
| **三角形数量** | < 100K 可见 | < 1M 可见 | LOD 系统在 500K 以上强制使用 | |
| **纹理 VRAM** | < 512MB | < 2GB | VRAM 压缩：ETC2（移动端），BPTC（桌面端） | |
| **脚本时间** | < 4ms 每帧 | < 8ms 每帧 | 将热循环移至 Server API | |
| **物理体** | < 200 活跃 | < 1000 活跃 | 使用 `PhysicsServer` 直接 API 进行大规模模拟 | |
| **粒子** | < 2000 总计 | < 10000 总计 | GPU 粒子，手动设置 `visibility_aabb` | |
| **音频总线** | < 8 个同步 | < 32 个同步 | 使用 [音频系统](references/audio-systems.md) 总线路由 | |
| **存档文件大小** | < 1MB | < 50MB | 对于程序化世界：保存种子和修改的 **Delta 列表**，而不是整个地图。100MB 的世界变成 50KB 的存档 | |
| **场景加载时间** | < 500ms | < 2s | `ResourceLoader.load_threaded_request()` |

---

## ⚙️ 第六部分：服务器 API——专家性能逃生舱口

这是大多数 Godot 开发者从未学到的知识。当场景树成为瓶颈时，使用 Godot 的低级服务器 API 完全绕过它。

### 何时降至服务器 API
- **10K+ 渲染实例**（精灵，网格）: 使用 `RenderingServer` 和 RID 考虑，而不是 `Sprite2D`/`MeshInstance3D` 节点。
- **子弹地狱 / 粒子系统**：使用 `PhysicsServer2D` 中的身体创建，而不是 `Area2D` 节点。
- **大规模物理模拟**：直接使用 `PhysicsServer3D` 进行 Ragdoll 字段，碎片或流体式模拟。

### 📊 性能比较：场景树 vs. 服务器 API

绕过场景树消除了节点生命周期管理的沉重 CPU 开销，信号传播和虚拟函数开销（如 `_process`）。

| 指标 | 场景树（节点） | 服务器 API（RID） | 专家推理 |
| :--- | :--- | :--- | :--- |
| **对象限制** | ~1,000 - 5,000 | 50,000+ | 场景树具有 O(n) 遍历成本；服务器使用 O(1) 直接 RID 处理。 |
| **内存开销** | ~2KB - 10KB 每个节点 | < 200 字节每个 RID | 节点携带树状态，信号和 inspector 元数据。 |
| **CPU 时间** | 高（虚拟调用） | 最小（C++ 直接 API） | 节点必须为每个实例调用 `_process`。服务器在 C++ 中批量操作。 |
| **线程** | 仅限主线程 | 本质上线程安全 | 大多数服务器 API 在 Project Settings 中启用时是线程安全的。 |
| **垃圾回收** | 自动（RefCounted） | 手动（分配/释放） | 服务器需要手动生命周期管理（RID 创建/删除）。 |

**专家注释**：使用 RID 允许管理原始数据并直接与引擎核心逻辑交互。这是主要的“逃生舱口”，用于子弹地狱，大规模灌木丛或复杂的程序化模拟，其中场景树维护成为瓶颈。

### RID 模式（专家）
服务器 API 通过 **RID**（资源 ID）——服务器端对象的透明句柄。关键规则：
```gdscript
# 创建服务器端画布项（没有节点开销）
var ci_rid := RenderingServer.canvas_item_create()
RenderingServer.canvas_item_set_parent(ci_rid)

# 关键：保留资源引用。RID 在资源被 GC 时会默默失效。
var texture: Texture2D = preload("res://sprite.png")
RenderingServer.canvas_item_add_texture_rect(ci_rid, Rect2(-texture.get_size() / 2, texture.get_size()), texture)
```

### 服务器与线程
- 场景树**不是线程安全的**。但服务器 API（RenderingServer, PhysicsServer）在 Project Settings 中启用时是线程安全的。
- 你可以在工作线程上构建场景块（实例化 + `add_child`），但必须使用 `add_child.call_deferred()` 将其附加到活动树。
- GDScript 字典/数组：跨线程读取和写入是安全的，但**调整大小**（追加，擦除，调整大小）需要 `Mutex`。
- **永远不要**从多个线程同时加载相同的 `Resource`——使用一个加载线程。

---

## 🧩 第七部分：专家代码模式
专家对常见架构和游戏系统实现的代码。

- **[组件注册](references/patterns/component_registry.md)**：集中式字典式组件检索。
- **[安全信号处理器](references/patterns/safe_signal_handler.md)**：防止在已释放对象引用的情况下崩溃。
- **[异步资源加载器](references/patterns/async_resource_loader.md)**：线程化资产摄入。
- **[状态机转换保护](references/patterns/state_machine_transition_guard.md)**：验证状态更改。
- **[线程安全块加载器](references/patterns/thread_safe_chunk_loader.md)**：低级服务器 API 构建。
- **[视野锥检测](references/patterns/vision_cone_detection.md)**：专家 NPC 视觉，使用点积和射线投射。
- **[声音传播系统](references/patterns/sound_propagation_system.md)**：声学遮挡逻辑。
- **[隐行隐藏逻辑](references/patterns/stealth_hiding_logic.md)**：全局可见性和隐藏管理。

---

## 🔥 第八部分：Godot 4.x 常见问题（仅限老兵）

1. **`@export` 资源默认共享**：多个场景实例**全部共享**相同的 `Resource`。在 `_ready()` 中使用 `resource.duplicate()` 或启用“仅限场景”复选框。这是报告最多的 Godot 4 错误，新手会报告。
2. **信号语法无声失败**：`event Action OnDeath;`（Godot 3 语法）在 Godot 4 中编译但什么也不做。必须使用 `signal died`。
3. **`Tween` 不是一个节点**：通过 `create_tween()` 创建，绑定到创建节点的生命周期。如果该节点被释放，则 Tween 会死亡。使用 `get_tree().create_tween()` 创建持久性 Tween。
4. **`PhysicsBody` 层级 vs. 掩码**：`collision_layer` = "我是什么"。`collision_mask` = "我扫描什么"。将两者设置为相同值会导致自我碰撞或错过检测。
5. **`StringName` vs. `String` 在热路径中**：`StringName` (`&"name"`) 使用指针比较（O(1)）。`String` 使用字符比较（O(n)）。在字典和信号查找中始终使用 `StringName`。
6. **`@onready` 时间**：运行在 `_init()` 之前，但在 `_ready()` 期间运行。如果你需要构造器时间设置，请使用 `_init()`。如果你需要树访问，请使用 `@onready` 或 `_ready()`。混合它们会导致空值。

---

## 📂 第九部分：模块目录（99 个蓝图）

> [!重要]
> 仅加载当前工作流程所需的模块。使用第二部分的决策矩阵来确定要遵循的链。

### 架构 & 基础
[基础知识](references/project-foundations.md) | [组合](references/composition.md) | [应用组合](references/composition-apps.md) | [信号架构](references/signal-architecture.md) | [Autoloads](references/autoload-architecture.md) | [状态](references/state-machine-advanced.md) | [资源](references/resource-data-patterns.md) | [模板](references/project-templates.md) | [分析师](references/analyst.md) | [审计员](references/auditor.md) | [构建器](references/builder.md)

**版本升级（外部中心）：** [godot-version-migration](https://github.com/thedivergentai/gd-agentic-skills/blob/main/skills/godot-version-migration/SKILL.md)**——完整历史路由器（遗留时代，3→4 桥接，4.0→4.x 跳跃）；不在此处镜像。

### GDScript & 测试
[GDScript 磨练](references/gdscript-mastery.md) | [测试模式](references/testing-patterns-expert-testing-patterns.md) | [调试/分析](references/debugging-profiling.md) | [性能优化](references/performance-optimization.md)

### 2D 系统
[2D 动画](references/2d-animation.md) | [2D 物理](references/2d-physics.md) | [瓦片地图](references/tilemap-mastery.md) | [动画播放器](references/animation-player.md) | [动画树](references/animation-tree-mastery.md) | [CharacterBody2D](references/characterbody-2d.md) | [粒子](references/particles.md) | [缓动](references/tweening.md) | [着色器基础](references/shaders-basics.md) | [相机系统](references/camera-systems.md)

### 3D 系统
[3D Lighting](references/3d-lighting.md) | [3D 材质](references/3d-materials.md) | [3D 世界构建](references/3d-world-building.md) | [物理 3D](references/physics-3d.md) | [导航/路径查找](references/navigation-pathfinding.md)

### 游戏机制
[能力](references/ability-system.md) | [战斗](references/combat-system.md) | [对话](references/dialogue-system.md) | [经济](references/economy-system.md) | [背包](references/inventory-system.md) | [任务](references/quest-system.md) | [RPG Stats](references/rpg-stats.md) | [回合系统](references/turn-system.md) | [音频](references/audio-systems.md) | [场景管理](references/scene-management.md) | [保存/加载](references/save-load-systems.md) | [秘密](references/mechanic-secrets.md) | [收集](references/game-loop-collection.md) | [波浪](references/game-loop-waves.md) | [收获](references/game-loop-harvest.md) | [计时赛](references/game-loop-time-trial.md) | [复活](references/mechanic-revival.md) | [Monte Carlo 平衡器](references/monte-carlo-balancer.md) | [测试](references/testing-patterns-expert-testing-patterns.md) | [构建器](references/builder.md)

### 流派合成
- `射击`：严格使用 `intersect_ray()`（直接空间状态）而不是 `RayCast3D` 节点以获得 100 倍的性能。
- `RPG`：伤害遵循 `base * pow(scaling, level)` 以维持终局进度。
- `RTS`：基于它们的质心移动组，使用 `Relative Offset` 以保持队形完整性。
- `Metroidvania`：使用 `ResourceLoader.load_threaded_request()` 进行无缝房间切换。
- `平台游戏`：强制 `Jump Buffering` (~0.15s) 和 `Coyote Time` 以获得专业感觉。
- `模拟`：`Tick Manager` 批处理；避免每个实体 `_process` 以维持数千个单位。
- `浪漫`：`多轴情感`（吸引力, 信任, 舒适）以映射复杂的叙事分支。
- `建筑`：`信号架构`严格遵循 `信号向上，调用向下` 以消除场景循环耦合。

---

## 🚀 第十部分：快速启动——Unity (C#) 到 Godot (GDScript)

从 Unity 生态系统过渡到 Godot 的资深工程师的思维模型转变。

### 1. 节点 vs. GameObjects & Components
在 Unity 中，`GameObject` 是 `Components` 的容器。在 Godot 中，**所有内容都是节点**。
- **Unity**：`GameObject` + `Transform` + `MeshFilter` + `Script`。
- **Godot**：一个 `MeshInstance3D` 节点（它本身就是一个 Transform 和一个 Mesh）附带一个脚本。
- **专家转变**：使用节点组合。如果你需要一个“Health Component”，请将一个 `Node` 或 `Area3D` 作为子节点命名为 "Health"。使用 `RefCounted` 子类用于所有逻辑数据包和数据容器。保留 `Node` 用于必须存在于空间树中的内容。这可以将复杂系统的场景树开销减半。

### 2. 场景是嵌套的 Prefab
Godot 没有Prefabs，因为**每个场景都是一个 prefab**。
- 你可以在一个场景内部嵌套场景，无限嵌套。
- **专家转变**：每个可重用系统（玩家，敌人，UI 按钮等）都应该是自己的 `.tscn` 文件。这促进了“后序遍历”（子节点在父节点准备好之前准备好）。

### 3. 信号 vs. 事件/动作
Godot 的 `Signal` 系统是观察者模式的原生实现。
- **Unity**：`event Action OnDeath;`。
- **Godot**：`signal died`。
- **专家转变**：信号是第一类公民。它们在 Inspector 中可见，可以动态连接或通过编辑器连接。使用“信号总线”模式（Autoload）进行全局事件以模拟 Unity 的 Singleton 管理器。

### 4. 脚本作为类扩展
当你将脚本附加到节点时，该脚本就是节点本身。
- **Unity**：`GetComponent<MyScript>()`。
- **Godot**：脚本扩展了节点的类（例如，`extends CharacterBody3D`）。
- **专家转变**：使用**类型化 GDScript** (`var x: int = 5`) 以获得编译速度提升和编辑器完成。类型化 GDScript 在编译时类型已知的情况下使用优化的 opcodes。

### 5. 内存管理：没有垃圾回收停顿
与 Unity 的 C# 不同，Unity 可能会出现“GC 峰值”。GDScript 使用引用计数。
- **专家转变**：对象在不再被引用时立即释放。这提供了确定性的性能并避免了大型 Unity 项目中常见的间歇性“卡顿”。

### 6. StringNames & 性能
Unity 使用 `int` 或 `Enum` 以获得性能。Godot 使用 `StringName`。
- **专家转变**：使用 `&"name"` 进行常量时间（O(1)）指针比较，用于字典和信号查找。

---

## 参考
- [Godot 4.7 官方文档](https://docs.godotengine.org/en/4.7/)
- [Godot 4.7 升级指南](https://docs.godotengine.org/en/4.7/tutorials/migrating/upgrading_to_godot_4.7.html)
- [Godot Engine GitHub 讨论](https://github.com/godotengine/godot/discussions)
