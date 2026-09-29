---
name: godot-master
description: 专业 Godot 4.7+ 游戏和应用程序开发整合专家库。通过架构工作流、反模式目录、性能预算和服务器 API 模式来协调 92 种领域技能。使用场景： (1) 开始新的 Godot 项目， (2) 设计游戏或应用架构， (3) 构建实体/组件系统， (4) 调试性能或物理问题， (5) 在 2D/3D 方法之间进行选择， (6) 实现多人游戏， (7) 优化绘制调用或脚本时间， (8) 在平台之间进行移植， (9) 从 4.6 迁移到 4.7。所有 Godot 开发任务的主要入口。关键词：Godot 4.7, AreaLight3D, HDR, Asset Store, godot-master。
---

# Godot 大师：首席架构师知识中心

每个部分都通过专注于**知识差值**来赚取代币——即基础模型已经知道的内容与资深 Godot 工程师从实际发布产品中了解的内容之间的差距。

## 库目标 — Godot 4.7+

所有领域技能镜像的目标是**Godot 4.7+**（稳定版）。对于**任何引擎版本升级**（1.x/2.x 遗留版本 → 3 → 4 → 跳跃式 4.x），请使用**[godot-version-migration](https://github.com/thedivergentai/gd-agentic-skills/blob/main/skills/godot-version-migration/SKILL.md)**——不要将此中心视为迁移变更日志。

在路由时进行跨领域 4.7 提醒：**AreaLight3D** / HDR → [3D 光照](references/3d-lighting.md)；资源库与资源库 → 导出/平台模块；RichTextLabel ImageUnit、输入设备 ID 常量、Jolt 行为 → 迁移中心模块笔记。

---

## 🧠 第一部分：专家思维框架

### “谁拥有什么？”——架构精神检查
在编写任何系统之前，为每个状态变量回答以下三个问题：
- **谁拥有数据？**（`StatsComponent` 拥有生命值，而不是 `CombatSystem`）
- **谁被允许修改它？**（只能通过公共方法如 `apply_damage()` 的所有者）
- **谁需要知道它已更改？**（任何监听 `health_changed` 信号的人）

如果你无法为每个状态变量回答这三个问题，那么你的架构存在耦合问题。这不是面向对象的封装——这是 Godot 特有的，因为**信号系统是执行机制，而不是访问修饰符**。

### Godot “分层蛋糕”
将每个功能组织成四个层次。信号向上传播，永不向下传播：
```
┌──────────────────────────────┐
│  PRESENTATION (UI / VFX)     │  ← 监听信号，从不拥有数据
├──────────────────────────────┤
│  LOGIC (状态机)            │  ← 协调转换，查询数据
├──────────────────────────────┤
│  DATA (资源 / .tres)       │  ← 单一事实来源，可序列化
├──────────────────────────────┤
│  INFRASTRUCTURE (自动加载)  │  ← 信号总线，SaveManager，AudioBus
└──────────────────────────────┘
```
**关键规则**：呈现层绝不能直接修改数据。基础设施只能通过信号进行通信。如果一个 `Label` 节点正在调用 `player.health -= 1`，那么架构就是有问题的。

### 信号总线分层架构
- **全局总线（自动加载）**：仅用于生命周期事件（`match_started`，`player_died`，`settings_changed`）。调试蔓延是代价——将事件限制在 < 15 个。
- **作用域功能总线**：每个功能文件夹都有自己的总线（例如，`CombatBus` 仅用于战斗节点）。这是可扩展性的折衷方案。
- **直接信号**：单个场景内父子通信。永不跨场景边界。

### 🔗 “智能互连”命令
专家系统不是由其隔离性定义的，而是由其**有效载荷合成**定义的。
- **物理 → 性能**：`PhysicsServer2D` 和 `RenderingServer` 绕过 `SceneTree` 节点开销。用于 1,000+ 子弹或粒子以实现 O(1) 处理。
- **动画 → 物理**：`AnimationTree.get_root_motion_position()` 将动画位移转换为物理 `velocity`，防止复杂移动中的“脚滑动”。
- **数据 → 反应性**：序列化的 `Resource` 对象（如 `Stats`）在修改时发出信号，允许 UI 自动更新而无需紧密耦合。
- **资源 → 生成**：基于 O(1) 字典的缓存（在 `ResourceLoader` 异步阶段预加载）防止生成物品或敌人时的 I/O 崩溃。
- **移动端 → 视觉**：通过在加载屏幕期间实例化隐藏效果来防止运行时帧率崩溃，以强制 GPU 着色器管道编译。
- **网络 → 带宽**：使用 `PackedByteArray` 中的位打包进行同步，而不是 JSON/字符串，以保持数据包小于 100 字节。
- **类型合成**：
    - `射击类`：严格使用 `intersect_ray()`（直接空间状态）而不是 `RayCast3D` 节点，以实现 100 倍性能提升。
    - `RPG`：伤害遵循 `base * pow(scaling, level)` 以维持终局进度。
    - `RTS`：基于其质心使用 `Relative Offset` 移动组，以保持队形完整性。
    - `Metroidvania`：使用 `ResourceLoader.load_threaded_request()` 实现无缝房间切换。
    - `平台类`：强制 `Jump Buffering`（~0.15s）和 `Coyote Time` 以获得专业感。
    - `模拟类`：`Tick Manager` 批处理；避免每个实体的 `_process` 以维持数千个单位。
    - `浪漫类`：`多轴情感`（吸引力、信任、舒适）以映射复杂的叙事分支。
    - `架构类`：`信号架构`严格遵循 `信号向上，调用向下` 以消除场景循环耦合。

---

## 🧭 第二部分：架构决策框架

### 主决策矩阵

| 场景 | 策略 | **必须** 技能链 | 交易
| :--- | :--- | :--- | :--- |
| **快速原型** | 事件驱动单体 | **阅读**：[基础](references/project-foundations.md) → [自动加载](references/autoload-architecture.md)。**不要加载**类型或平台引用。 | 快速启动，意大利面条风险 |
| **复杂 RPG** | 组件驱动 | **阅读**：[组合](references/composition.md) → [状态机](references/state-machine-advanced.md) → [RPG 统计](references/rpg-stats.md)。**不要加载**多人或平台引用。 | 重型设置，无限扩展 |
| **大型开放世界** | 资源流式传输 | **阅读**：[开放世界](references/genre-open-world.md) → [保存/加载](references/save-load-systems.md)。也加载 [性能](references/performance-optimization.md)。 | 复杂 I/O，超过 10K 个单位的浮点精度抖动 |
| **服务器验证多人** | 确定性 | **阅读**：[服务器架构](references/server-architecture.md) → [多人](references/multiplayer-networking.md)。**不要加载**单人游戏引用。 | 高延迟，反作弊安全 |
| **移动/网页移植** | 自适应响应 | **阅读**：[UI 容器](references/ui-containers.md) → [桌面→移动自适应](references/adapt-desktop-to-mobile.md) → [平台移动](references/platform-mobile.md)。 | UI 复杂性，广泛覆盖 |
| **应用程序/工具** | 应用组合 | **阅读**：[应用组合](references/composition-apps.md) → [主题](references/ui-theming.md)。**不要加载**游戏特定引用。 | 与游戏不同的范式 |
| **浪漫/约会模拟** | 情感经济 | **阅读**：[浪漫](references/genre-romance.md) → [对话](references/dialogue-system.md) → [UI 富文本](references/ui-rich-text.md)。 | 高 UI/叙事密度 |
| **秘密/彩蛋** | 故意混淆 | **阅读**：[秘密](references/mechanic-secrets.md) → [持久化](references/save-load-systems.md)。 | 社区参与，调试风险 |
| **收集任务** | 搜集逻辑 | **阅读**：[收集](references/game-loop-collection.md) → [Marker3D 放置](references/3d-world-building.md)。 | 玩家留存，探索驱动 |
| **季节性活动** | 运行时注入 | **阅读**：[复活彩蛋主题](references/theme-easter.md) → [材质交换](references/3d-materials.md)。 | 快速品牌，无资源污染 |
| **魂类死亡** | 风险回报复活 | **阅读**：[复活/尸体跑](references/mechanic-revival.md) → [物理 3D](references/physics-3d.md)。 | 高紧张感，玩家挫败风险 |
| **基于波次的动作** | 战斗节奏循环 | **阅读**：[波次](references/game-loop-waves.md) → [战斗](references/combat-system.md)。 | 逐步增加紧张感，遭遇设计 |
| **平衡/难度/经济节奏** | 蒙特卡洛平衡实验室 | **阅读**：[资源](references/resource-data-patterns.md) → [经济](references/economy-system.md) → [战斗](references/combat-system.md) / [RPG 统计](references/rpg-stats.md) / [波次](references/game-loop-waves.md)（按需）→ [蒙特卡洛平衡器](references/monte-carlo-balancer.md) → [测试](references/testing-patterns-expert-testing-patterns.md) → [构建器](references/builder.md)。 | 统计严谨性；抽象模拟必须与无头 Godot 校准 |
| **生存经济** | 收获循环 | **阅读**：[收获](references/game-loop-harvest.md) → [背包](references/inventory-system.md)。 | 资源稀缺，循环持久性 |
| **赛车/速通** | 验证循环 | **阅读**：[计时赛](references/game-loop-time-trial.md) → [输入缓冲](references/input-handling.md) → [类型赛车](references/genre-racing.md)。 | 高精度，幽灵记录驱动 |
| **恐怖/潜行** | 紧张感管理 | **阅读**：[类型恐怖](references/genre-horror.md) → [类型潜行](references/genre-stealth.md) → [音频](references/audio-systems.md)。 | 氛围，玩家脆弱性 |
| **卡牌/棋盘游戏** | 规则执行 | **阅读**：[类型卡牌游戏](references/genre-card-game.md) → [回合系统](references/turn-system.md)。 | 确定性状态，UI 密集 |
| **模拟/RTS** | 批处理 | **阅读**：[类型模拟](references/genre-simulation.md) → [类型 RTS](references/genre-rts.md) → [性能](references/performance-optimization.md)。 | 高单位数量，O(1) 逻辑 |
| **HDR/电影级视觉效果** | 显示管线 | **阅读**：[3D 光照](references/3d-lighting.md) → [平台桌面](references/platform-desktop.md) → [着色器](references/shaders-basics.md)。在项目设置中启用视口 HDR。 | 平台特定色调映射调整 |
| **矩形区域光** | AreaLight3D | **阅读**：[3D 光照](references/3d-lighting.md) → [3D 材质](references/3d-materials.md)。优先使用 AreaLight3D 而不是自发光+GI 诡术。 | 需要 Forward+ 渲染器以实现完整质量 |
| **移动触控** | 原生摇杆 | **阅读**：[平台移动](references/platform-mobile.md) → [桌面→移动自适应](references/adapt-desktop-to-mobile.md)。使用内置虚拟摇杆（4.7+）。 | 减少插件依赖 |
| **插件/资源发现** | 资源库 | **阅读**：[项目基础](references/project-foundations.md) → [导出构建](references/export-builds.md)。资源库取代资源库。 | 测试商店 UI——验证每个插件的许可 |
| **代理眼睛/视觉 QA** | 捕获 → WebP → 评分标准 | **阅读**：[代理视觉](references/agent-vision.md)。截图资源，窗口/区域/屏幕，或临时编辑器桥接——然后进行结构化审查。**不要加载**类型引用。 | 仅主机端；永不自动加载 / 永不离开暂存插件 |

### “何时不应使用节点”决策
最具影响力的专家决策之一。Godot 文档明确说明“避免使用节点处理所有内容”：

| 类型 | 何时使用 | 成本 | 专家用例 |
| :--- | :--- | :--- | :--- |
| **`Object`** | 自定义数据结构，手动内存管理 | 最轻。必须手动调用 `.free()`。 | 自定义空间哈希映射，ECS 风格数据存储 |
| **`RefCounted`** | 短暂数据包，自动删除的逻辑对象 | 当没有引用时自动删除。 | `DamageRequest`，`PathQuery`，`AbilityEffect`——不需要场景树的逻辑包 |
| **`Resource`** | 具有检查器支持的序列化数据 | 比RefCounted 稍重。处理 `.tres` I/O。 | `ItemData`，`EnemyStats`，`DialogueLine`——任何设计师应在检查器中编辑的数据 |
| **`Node`** | 需要 `_process`/`_physics_process`，需要存在于场景树中 | 最重——每个节点的 SceneTree 开销。 | 仅用于需要每帧更新或空间变换的实体 |

**专家模式**：对所有逻辑包和数据容器使用 `RefCounted` 子类。为必须存在于空间树中的内容保留 `Node`。这可以将复杂系统的场景树开销减半。

---

## 🔧 第三部分：核心工作流

### 工作流 1：专业脚手架
*从空项目到生产就绪容器*

**必须——阅读整个文件**：[基础](references/project-foundations.md)
1. 按**功能**（`/features/player/`，`/features/combat/`）组织，而不是按类类型。`player/` 文件夹包含玩家的场景、脚本、资源和测试。
2. **阅读**：[信号架构](references/signal-architecture.md)——创建 `GlobalSignalBus` 自动加载，事件少于 15 个。
3. **阅读**：[GDScript 精通](references/gdscript-mastery.md)——在项目设置→GDScript→调试中启用 `untyped_declaration` 警告。
4. 应用**[项目模板](references/project-templates.md)** 以获取基础 `.gitignore`、导出预设和输入映射。
5. 使用**[构建器](references/builder.md)** (`create_scene.py`，`add_node.py`，`save_scene.py`) 通过 Godot CLI 程序生成性地创建场景层次结构。

> [!CAUTION] **工作流 1 永不列表**
> - **永不**在逻辑脚本中使用 `res://` 路径。使用 `@export_file` 或 `@export_dir` 确保资源在移动时保持有效。
> - **永不**在 `_init()` 中初始化子节点。场景树尚未准备好。使用 `_ready()` 或 `@onready`。
> - **永不**保持 `Physics Ticks` 的“默认”项目设置。设置为 60 以保持一致性，或使用 `Engine.physics_ticks_per_second` 以实现自适应逻辑。
> - **永不**在 `_process()` 中使用 `print()` 进行调试；使用 `Debugger` 或 `push_error()` 以避免帧时间峰值。

**在脚手架期间**不加载**战斗、多人、类型或平台引用。

### 工作流 2：实体编排
*构建模块化、可测试的角色*

**必须链——阅读所有**：[组合](references/composition.md) → [状态机](references/state-machine-advanced.md) → [CharacterBody2D](references/characterbody-2d.md) 或 [物理 3D](references/physics-3d.md) → [动画树](references/animation-tree-mastery.md)
**不加载** UI、音频或保存/加载引用以进行实体工作。

- 状态机查询 `InputComponent`，而不是直接处理输入。这允许 AI/玩家切换而无需重构。
- 状态机仅处理转换。逻辑属于组件。`MoveState` 告诉 `MoveComponent` 行动，而不是反过来。
- 每个实体都必须通过**F6 测试**：按“运行当前场景”（F6）必须能工作而不会崩溃。如果崩溃，则你的实体有场景外部依赖。

> [!CAUTION] **工作流 2 永不列表**
> - **永不**调用 `parent.do_thing()`。如果父节点更改，实体就会崩溃。发出 `request_action` 信号。
> - **永不**使用 `_process` 进行移动。使用 `_physics_process` 以避免在可变刷新率显示器上出现抖动。
> - **永不**硬编码动画名称。使用 `StringName` 常量或 `Resource` 映射以启用在 `AnimationPlayer` 中的轻松重命名。
> - **永不**使用绝对路径调用 `get_node()`。使用 `%UniqueName` 以便在树重构后生存。

### 工作流 3：数据驱动系统
*通过资源连接战斗、背包、统计*

**必须链——阅读所有**：[资源模式](references/resource-data-patterns.md) → [RPG 统计](references/rpg-stats.md) → [战斗](references/combat-system.md) → [背包](references/inventory-system.md)

- 创建一个 `ItemData.gd` 扩展 `Resource`。将其作为 100 个 `.tres` 文件实例化，而不是 100 个脚本。
- HUD 永远不直接引用玩家。它在信号总线上监听 `player_health_changed`。
- 为所有 `@export Resource` 变量启用“仅当前场景”，或在 `_ready()` 中调用 `resource.duplicate()`。不这样做是第 8 部分的 Bug #1。

> [!CAUTION] **工作流 3 永不列表**
> - **永不**在信号总线上传递 `Node` 引用。对象会被释放；RID 或 ID 更安全，用于长期跟踪。
> - **永不**通过代码修改 `.tres` 文件（它会修改磁盘文件）。始终 `.duplicate()` 再修改。
> - **永不**使用 `Array` 进行高频搜索。使用 `Dictionary` 并使用 `StringName` 键进行 O(1) 查找。
> - **永不**使用 `float` 进行物品计数或精确资源跟踪；使用 `int` 并缩放以用于显示。

### 工作流 4：持久化管道
**必须**：[自动加载架构](references/autoload-architecture.md) → [保存/加载](references/save-load-systems.md) → [场景管理](references/scene-management.md)

- 使用字典映射的序列化。当添加新字段时，旧存档文件绝对不能损坏——使用 `.get("key", default_value)`。
- 对于程序化世界：保存**种子**和**修改增量列表**，而不是整个地图。一个100MB的世界会变成50KB的存档。

> [!CAUTION] **工作流4绝对不做列表**
> - **绝对不要**保存整个`Object`或`Node`实例。它们包含临时的指针。将数据提取到`Dictionary`或自定义`Resource`中。
> - **绝对不要**使用`JSON`来处理需要严格类型的数据（例如`Vector2`）。使用`var_to_bytes`或`ConfigFile`来处理结构化的Godot类型。
> - **绝对不要**在自动保存时阻塞主线程。使用`Thread`或`WorkerThreadPool`来序列化大型字典。
> - **绝对不要**在导出的项目中保存到`res://`；严格使用`user://`来保存持久化数据。

### 工作流5：性能优化
**强制要求**：[调试/分析](references/debugging-profiling.md) → [性能优化](references/performance-optimization.md)

**先诊断再优化**（绝对不要盲目优化）：
1. **脚本时间过长** → 使用内置分析器进行剖析。检查是否在数百个节点上调用`_process`。切换到单管理器模式或服务器API（见第6部分）。
2. **绘制调用过多** → 使用`MultiMeshInstance`来处理重复的几何体。使用ORM纹理来批处理材质。
3. **物理卡顿** → 将碰撞简化为原始形状。加载[2D物理](references/2d-physics.md)或[3D物理](references/physics-3d.md)。检查是否使用`_process`而不是`_physics_process`来处理移动。
4. **VRAM使用过多** → 将纹理切换到VRAM压缩（桌面使用BPTC/S3TC，移动使用ETC2）。绝对不要发布原始PNG。
5. **间歇性帧率峰值** → 通常是由于GC遍历、同步`load()`或NavigationServer重新计算。使用`ResourceLoader.load_threaded_request()`。

> [!CAUTION] **工作流5绝对不做列表**
> - **绝对不要**在`_process`内部使用`get_nodes_in_group()`。这是一个每次帧都执行的O(n)操作。在`_ready()`中缓存数组。
> - **绝对不要**使用`Area2D`信号来处理“保持”逻辑。定期使用`get_overlapping_bodies()`或使用`PhysicsServer`级别的检查。
> - **绝对不要**在分析之前进行优化。如果存在2000个绘制调用导致GPU崩溃，那么1毫秒的脚本无关紧要。
> - **绝对不要**在热点路径中使用`load()`；严格使用`preload`或使用`ResourceLoader`进行异步加载。

### 工作流6：跨平台适配
**强制要求**：[输入处理](references/input-handling.md) → [桌面→移动适配](references/adapt-desktop-to-mobile.md) → [移动平台](references/platform-mobile.md)
**也需阅读**：[桌面平台](references/platform-desktop.md)、[网络平台](references/platform-web.md)、[控制台平台](references/platform-console.md)、[VR平台](references/platform-vr.md)按需。

- 使用自动加载的`InputManager`将所有输入类型转换为标准化动作。绝对不要直接读取`Input.is_key_pressed()`——它会阻塞控制器和触摸支持。
- 移动端触摸目标：最小44px物理尺寸。使用带有安全区域逻辑的`MarginContainer`来处理刘海/挖孔设备。
- 网络导出：Godot的`AudioServer`需要用户交互才能播放第一次（浏览器策略）。使用“点击开始”屏幕来处理这种情况。

> [!CAUTION] **工作流6绝对不做列表**
> - **绝对不要**使用`OS.get_name()`来检测功能。使用`OS.has_feature("mobile")`或自定义功能标签来处理子集，如“SteamDeck”。
> - **绝对不要**假设特定的宽高比。始终使用`Expand`或`Keep Aspect`与`Anchor`节点组合。
> - **绝对不要**在移动端/网络端使用仅桌面支持的着色器（例如复杂深度采样），而没有任何GLES3/兼容性次要路径。
> - **绝对不要**忽略桌面构建的`physical_keycode`；它确保键盘布局（AZERTY/QWERTY）不会破坏移动。
- **绝对不要**将未清理的字符串传递给`JavaScriptBridge.eval()`——这会导致网络构建中的脚本注入。使用`sanitize_js_string()`辅助函数。

### 工作流7：程序化生成
**强制要求**：[程序化生成](references/procedural-generation.md) → [瓦片地图精通](references/tilemap-mastery.md)或[3D世界构建](references/3d-world-building.md) → [导航](references/navigation-pathfinding.md)

- 始终使用带有固定`seed`的`FastNoiseLite`资源进行确定性生成。
- 绝对不要在主线程上烘焙NavMesh。使用`NavigationServer3D.parse_source_geometry_data()` + `NavigationServer3D.bake_from_source_geometry_data_async()`。
- 对于无限世界：块加载必须使用`WorkerThreadPool`在后台线程中进行。在主线程上`add_child.call_deferred()`之前，将场景块离树构建。

> [!CAUTION] **工作流7绝对不做列表**
> - **绝对不要**为“背景”噪声实例化节点。使用`MultiMeshInstance`或`_draw`中的绘制循环来处理数千个小细节。
> - **绝对不要**因为一个改变而重新生成整个地图。使用“脏块”系统来只更新确切改变的部分。
> - **绝对不要**在使用`concave_polygon_shape`时在网格生成同一帧上放置碰撞。它会阻塞物理线程。
> - **绝对不要**为所有单位每帧执行路径查找查询。使用带有定时器更新的`NavigationAgent`和`target_position`。

### 工作流8：多人架构
**强制要求——请阅读**：[单机→多人](references/adapt-single-to-multiplayer.md) → [网络](references/multiplayer-networking.md) → [服务器架构](references/server-architecture.md)
**不要加载**单机模式的蓝图。

- 客户端发送输入，服务器计算结果。客户端绝对不要决定伤害、位置增量或库存变化。
- 使用客户端预测与服务器重同步：本地预测，从服务器快照纠正。可隐藏高达~150ms的延迟。
- `MultiplayerSpawner`处理Godot 4中的复制。按场景配置，而不是全局配置。

> [!CAUTION] **工作流8绝对不做列表**
> - **绝对不要**在不验证的情况下信任`rpc_id(1, ...)`（客户端到服务器）。一个被黑的客户端可以发送`damage = 999999`。
> - **绝对不要**直接复制`_process`变换。复制`Input`向量并在两边模拟移动。
> - **绝对不要**使用`TCP`来处理高频数据包（移动）。使用`UDP` / `ENet`并处理丢失的数据包，使用插值。
> - **绝对不要**同步每个投射物；使用客户端预测来处理视觉效果，并且只RPC“开火”事件。

- `ReflectionProbe` vs `VoxelGI` vs `SDFGI`：探头是廉价/静态的，VoxelGI是中等/烘焙的，SDFGI是昂贵/动态的。根据您的平台预算选择（见第5部分）。

### 工作流9：响应式UI与专家主题（审核通过）
**强制链式**：[UI容器](references/ui-containers.md) → [UI主题](references/ui-theming.md) → [富文本](references/ui-rich-text.md) → [补间](references/tweening.md)

1. **F6原则**：每个UI场景都必须能够独立测试。仅在背景上使用`MOUSE_FILTER_STOP`，在子项上使用`PASS`。
2. **呼吸空间**：使用`add_theme_constant_override("separation", X)`而不是手动填充。
3. **自适应缩放**：使用`responsive_layout_builder.gd`来处理断点感知的移动/桌面切换。
4. **生命周期安全**：同一帧内绝对不要滚动到新的子项。在修改`scroll_vertical`之前，使用`await get_tree().process_frame`。
5. **数据集成**：使用`Resource-to-UI`绑定；UI节点必须是状态无关的投影层。

> [!CAUTION] **工作流9绝对不做列表**
> - **绝对不要**使用绝对像素偏移。在4K或小尺寸移动屏幕上UI会变得难以阅读。使用`Container`尺寸。
> - **绝对不要**深层嵌套`MarginContainers`。这会使检查器无法使用。为整个项目使用单个`Theme`资源来设置边距。
> - **绝对不要**直接将UI按钮连接到游戏逻辑。UI发送“信号”，`PlayerController`监听。这可以防止UI删除崩溃。
> - **绝对不要**使用`_process()`来移动UI元素到目标位置。使用`Tween`来避免卡顿和帧率依赖。
> - **绝对不要**将透明容器的`mouse_filter`保留为`STOP`；它会“吞噬”它后面的所有点击。
- **绝对不要**在没有验证`res://`前缀和安全扩展（`.tres`、`.res`、`.theme`）的情况下使用动态`load()`——这会防止任意代码/资源执行。

### 工作流10：电影级光照与VFX（审核通过）
**强制链式**：[3D光照](references/3d-lighting.md) → [粒子](references/particles.md) → [3D材质](references/3d-materials.md) → [着色器](references/shaders-basics.md)

1. **GI选择**：室内使用VoxelGI，开放世界使用SDFGI。绝对不要发布重叠的两者。
2. **阴影预算**：最多2个投影方向光。使用`fake_gi_bounce.gd`为移动端填充。
3. **VFX生命周期**：使用`finished`信号而不是计时器。使用`restart()`重新运行以避免异步GPU卡顿。
4. **优化**：使用ORM纹理打包（AO/粗糙/金属）来节省GPU缓存和纹理槽位。
5. **批处理**：使用`Instance Uniforms`来处理数千个实例中的材质变化，而不会产生绘制调用惩罚。

> [!CAUTION] **工作流10绝对不做列表**
> - **绝对不要**缩放`CollisionShape`节点；严格缩放形状资源以避免物理抖动。
> - **绝对不要**使用`TRANSPARENCY_ALPHA`来处理切割网格（树叶/栅栏）；使用`ALPHA_SCISSOR`来防止排序伪影。
> - **绝对不要**在游戏过程中动画化CSG节点；强制进行昂贵的CPU几何体重新计算。
> - **绝对不要**在看起来像2D的游戏中使用实时全局光照（SDFGI/VoxelGI）。坚持使用`DirectionalLight2D`和`CanvasModulate`。
> - **绝对不要**忽略`Camera3D`的近/远裁剪平面；不正确的设置会导致大型世界中的Z-fighting。

### 工作流11：程序化场景构建（Builder）
**强制要求**：[Builder](references/builder.md)
**仅用于批量操作或复杂的程序化脚手架**。在执行重CLI自动化时，优先使用独立的`godot-builder`技能。

1. **步骤1**：在纸上/Markdown上草拟节点层次结构，然后再接触磁盘。
2. **步骤2**：使用`create_scene.py`来定义根节点和`.tscn`路径。
3. **步骤3**：使用`add_node.py`来添加子节点。在每个节点上设置`owner`，以便序列化时保持它们。
4. **步骤4**：始终调用`run_project.py`或`launch_editor.py`来验证场景是否干净加载。
5. **专家规则**：使用Builder来构建*结构*（节点、名称、继承），然后使用GDScript来构建*行为*。

> [!CAUTION] **工作流11绝对不做列表**
> - **绝对不要**在没有设计层次结构的情况下直接跳转到`add_node.py`——会生成混乱场景。
> - **绝对不要**在脚本或场景属性中使用绝对文件系统路径；仅使用`res://`。
> - **绝对不要**添加没有分配形状资源的`CollisionShape2D`/`CollisionShape3D`——节点本身什么也不做。
> - **绝对不要**在批量场景写入后跳过通过`run_project.py` / `launch_editor.py`进行的验证。

#### 安全：边界标记与验证
当代理在写入文件之前摄入不可信的场景/数据文本时：
1. **边界标记**：用`<<<CONTEXT_START>>>`和`<<<CONTEXT_END>>>`包裹分析。
2. **清理**：节点名称必须是字母数字/下划线的。路径必须以`res://`开头。
3. **验证**：在修改前确认场景存在。

---

## 🚫 第4部分：专家绝对不做列表

每条规则都包括**非显而易见的原因**——这是只有发布经验才能教会的。

1. **绝对不要使用 `get_tree().root.get_node("...")`** — 当任何祖先被重命名或改变父节点时，绝对路径会失效。使用 `%UniqueNames`，`@export NodePath` 或基于信号发现。
2. **绝对不要在循环或 `_process` 中使用 `load()`** — 同步磁盘读取会阻塞整个主线程。对于小资源在脚本顶部使用 `preload()`，对于大资源使用 `ResourceLoader.load_threaded_request()`。
3. **绝对不要在外部引用存在时调用 `queue_free()`** — 父节点或持有引用的数组会收到“已删除对象”的错误。在 `_exit_tree()` 中清理引用，并在释放之前将它们设置为 `null`。
4. **绝对不要在 `_draw()` 中放置游戏逻辑** — `_draw()` 在渲染线程上调用。修改游戏状态会导致 `_physics_process` 的竞态条件。
5. **绝对不要使用 `Area2D` 处理 1000+ 重叠对象** — 每次重叠检查都有 O(n²) 的广域成本。使用 `ShapeCast2D`，`PhysicsDirectSpaceState2D.intersect_shape()` 或服务器 API 处理弹幕射击模式。
6. **绝对不要从组件中修改外部状态** — 如果 `HealthComponent` 调用 `$HUD.update_bar()`，删除 HUD 会导致游戏崩溃。组件发出信号；监听器决定如何响应。
7. **绝对不要在 `_physics_process` 中使用 `await`** — `await` 会挂起执行，导致物理步骤跳过帧。将异步操作移到由信号触发的单独方法中。
8. **绝对不要在热路径字典查找中使用 `String` 键** — 字符串哈希是 O(n)。使用 `StringName` (`&"key"`) 进行 O(1) 指针比较，或使用整数枚举。
9. **绝对不要存储指向已释放对象的 `Callable` 引用** — 会导致静默崩溃或抛出错误。在 `_exit_tree()` 中断信号或使用 `CONNECT_ONE_SHOT`。
10. **绝对不要使用 `_process` 处理 1000+ 实体** — 每个 `_process` 调用都有每个节点的 SceneTree 开销。使用单个 `Manager._process` 迭代数据结构数组（数据导向模式），或直接使用服务器 API。
11. **绝对不要在可能被释放的节点上使用 `Tween`** — 如果节点在 `queue_free()` 时正在运行 Tween，它会产生错误。在 `_exit_tree()` 中停止 Tween 或绑定到 SceneTree：`get_tree().create_tween()`。
12. **绝对不要在 `_process` 中从 `RenderingServer` 或 `PhysicsServer` 请求数据** — 这些服务器运行异步。调用获取函数会强制同步挂起，导致性能下降。API 故意设计为在热路径上只写。
13. **绝对不要使用 `call_deferred()` 作为初始化顺序错误的补丁** — 它掩盖了架构问题（依赖于树顺序）。通过显式初始化信号或 `@onready` 修复实际依赖。
14. **绝对不要创建循环信号连接** — 节点 A 连接到 B，B 连接到 A。这会在第一次发出时创建无限循环。使用中介模式（信号总线）来打破循环。
15. **绝对不要让继承超过 3 层** — 超过 3 层后，调试 `super()` 链会是一场噩梦。使用组合（`Node` 子节点）来添加行为。
16. **在物理密集型类型（FPS/ARPG）中绝对不要使用 `_process` 处理碰撞检测或移动** — 严格使用 `_physics_process` 以确保帧无关的碰撞检测。
17. **绝对不要信任客户端对持久游戏状态的权威**（生命值、经验值、背包）。完全通过服务器认证或安全校验和处理。
18. **绝对不要在运行时检查中使用标准字符串**；严格使用 `StringName` (`&"active"`) 以避免 O(n) 哈希。
19. **在单位密集型游戏中（RTS/MOBA）绝对不要每帧手动处理 RVO 避免**；卸载到 `NavigationAgent` 内部线程。
20. **绝对不要在主线程上阻塞进行程序生成或重 I/O**；严格卸载到 `WorkerThreadPool`。
21. **绝对不要忽略用于唯一实例的资源（例如敌人属性）上的 `Local-to-Scene`**；失败会导致所有实例之间的共享内存错误。
22. **绝对不要使用 `float` 作为货币**；严格使用整数分（避免复杂经济体中的精度漂移）。
23. **绝对不要在 `physics_frame` 之前设置 `target_position`**；导航地图在 `_ready()` 期间未准备好。
24. **绝对不要使用 `TRANSPARENCY_HASH` 或 `ALPHA` 处理大型镂空表面（植被）**；使用 `ALPHA_SCISSOR` 以提高性能和排序。
25. **绝对不要缩放 `CollisionShape` 节点**（Node2D/3D 缩放）— 使用形状手柄或调整资源大小以避免不可预测的物理法线和抖动。
26. **绝对不要在 `is_on_floor()` 为真时应用重力** — 会导致微小的抖动并防止地面吸附；严格将垂直速度重置为 0 或一个小的常量。
27. **绝对不要忘记断开动态信号（捕获 Lambda）** — Godot 无法自动断开捕获局部变量的 Lambda；它们会在释放的对象上导致崩溃。
28. **绝对不要使用鼠标事件处理移动端触摸** — 严格使用 `InputEventScreenTouch` 和 `InputEventScreenDrag` 以获得可靠的多点触控支持。
29. **绝对不要在移动端使用 Forward+ 渲染器** — 严格使用移动或兼容性渲染器以避免 GPU 瓶颈和电池消耗。
30. **绝对不要直接在变换上累积鼠标旋转** — 严格存储单独的 Yaw/Pitch 变量以防止万向锁和精度损失。
31. **绝对不要在运行时检查中使用标准字符串** — 严格使用 `StringName` (`&"active"`) 以避免 O(n) 哈希开销。
32. **绝对不要信任客户端的游戏状态**（生命值、背包）— 客户端建议操作；服务器验证并向所有客户端广播以防止作弊。
33. **绝对不要使用 `Reliable` RPC 进行移动更新** — 使用 `UnreliableOrdered` 以防止高延迟场景中的头部阻塞。

---

## 📊 第 5 部分：性能预算（具体数值）

| 指标 | 移动端目标 | 桌面端目标 | 专家备注 |
| :--- | :--- | :--- | :--- |
| **绘制调用** | < 100（2D），< 200（3D） | < 500 | `MultiMeshInstance` 用于植被/碎片 |
| **三角形数量** | < 10 万可见 | < 100 万可见 | 50 万以上必须使用 LOD 系统 |
| **纹理 VRAM** | < 512MB | < 2GB | VRAM 压缩：ETC2（移动端），BPTC（桌面端） |
| **脚本时间** | 每帧 < 4ms | 每帧 < 8ms | 将热循环移到服务器 API |
| **物理体数量** | < 200 活跃 | < 1000 活跃 | 使用 `PhysicsServer` 直接 API 进行质量模拟 |
| **粒子效果** | 总计 < 2000 | 总计 < 10000 | GPU 粒子，手动设置 `visibility_aabb` |
| **音频总线** | < 8 个同时 | < 32 个同时 | 使用 [音频系统](references/audio-systems.md) 总线路由 |
| **存档文件大小** | < 1MB | < 50MB | 种子 + 差分模式用于程序化世界 |
| **场景加载时间** | < 500ms | < 2s | `ResourceLoader.load_threaded_request()` |

---

## ⚙️ 第 6 部分：服务器 API — 专家性能逃生通道

这是大多数 Godot 开发者不会了解的知识。当场景树成为瓶颈时，完全绕过它，使用 Godot 的低级服务器 API。

### 何时切换到服务器 API
- **10K+ 渲染实例**（精灵、网格）：使用 `RenderingServer` 和 RID 而不是 `Sprite2D`/`MeshInstance3D` 节点。
- **弹幕射击/粒子系统**与脚本交互：使用 `PhysicsServer2D` 身体创建而不是 `Area2D` 节点。
- **大规模物理模拟**：直接使用 `PhysicsServer3D` 进行 ragdoll 场景、碎片或流体模拟。

### 📊 性能对比：场景树 vs. 服务器 API

绕过场景树消除了节点生命周期管理、信号传播和虚拟函数开销（如 `_process`）带来的沉重 CPU 开销。

| 指标 | 场景树（节点） | 服务器 API（RID） | 专家解释 |
| :--- | :--- | :--- | :--- |
| **对象限制** | ~1000 - 5000 | 50,000+ | 场景树有 O(n) 遍历成本；服务器使用 O(1) 直接 RID 处理。 |
| **内存开销** | ~2KB - 10KB/节点 | < 200 字节/RID | 节点携带树状态、信号和检视器元数据。RID 是 24 字节的透明句柄。 |
| **CPU 时间** | 高（虚拟调用） | 最小（直接 API） | 节点必须为每个实例调用 `_process`。服务器在 C++ 中批量操作。 |
| **线程** | 仅主线程 | 本质线程安全 | 大多数服务器 API 是线程安全的（必须在项目设置中启用）。 |
| **垃圾回收** | 自动（引用计数） | 手动（分配/释放） | 服务器需要手动生命周期管理（RID 创建/删除）。 |

**专家备注**：使用 RID 允许管理原始数据并直接与引擎核心逻辑交互。这是处理弹幕射击、大规模植被或复杂程序化模拟时场景树维护成为瓶颈的主要“逃生通道”。

### RID 模式（专家）
服务器 API 通过 **RID**（资源 ID）通信——服务器端对象的透明句柄。关键规则：
```gdscript
# 创建服务器端画布项（无节点开销）
var ci_rid := RenderingServer.canvas_item_create()
RenderingServer.canvas_item_set_parent(ci_rid, get_canvas_item())

# 关键：保持资源引用活跃。RID 不计入引用计数。
# 如果 Texture 资源被 GC，RID 会无声失效。
var texture: Texture2D = preload("res://sprite.png")
RenderingServer.canvas_item_add_texture_rect(ci_rid, Rect2(-texture.get_size() / 2, texture.get_size()), texture)
```

### 服务器线程
- 场景树**不是**线程安全的。但服务器 API（RenderingServer、PhysicsServer）在项目设置中启用时是线程安全的。
- 你可以在工作线程上构建场景块（实例化 + add_child），但必须使用 `add_child.call_deferred()` 将其附加到活动树。
- GDScript 字典/数组：跨线程读取和写入是安全的，但**调整大小**（append、erase、resize）需要 `Mutex`。
- **绝对不要**从多个线程同时加载相同的 `Resource` — 使用一个加载线程。

---

## 🧩 第 7 部分：专家代码模式
常见架构和游戏系统的高级实现。

- **[组件注册器](references/patterns/component_registry.md)**：基于字典的中心化组件检索。
- **[安全信号处理器](references/patterns/safe_signal_handler.md)**：防止因释放对象引用而崩溃。
- **[异步资源加载器](references/patterns/async_resource_loader.md)**：线程化资源摄入。
- **[状态机转换保护](references/patterns/state_machine_transition_guard.md)**：验证状态变化。
- **[线程安全块加载器](references/patterns/thread_safe_chunk_loader.md)**：低级服务器 API 构建。
- **[视野锥检测](references/patterns/vision_cone_detection.md)**：高级 NPC 视觉，使用点积和射线检测。
- **[声音传播系统](references/patterns/sound_propagation_system.md)**：声学遮挡逻辑。
- **[潜行隐藏逻辑](references/patterns/stealth_hiding_logic.md)**：全局可见性和隐蔽管理。

---

## 🔥 第 8 部分：Godot 4.x 注意事项（老兵专享）

1. **`@export` 资源默认共享**：多个场景实例**全部**共享相同 `Resource`。在 `_ready()` 中使用 `resource.duplicate()` 或启用“仅当前场景”复选框。这是新手报告的最常见的 Godot 4 错误。
2. **信号语法无声失败**：`connect("signal_name", target, "method")`（Godot 3 语法）编译但在 Godot 4 中什么也不做。必须使用 `signal_name.connect(callable)`。
3. **`Tween` 不再是节点**：通过 `create_tween()` 创建，绑定到创建节点的生命周期。如果该节点被释放，Tween 也会消失。使用 `get_tree().create_tween()` 创建持久 Tween。
4. **`PhysicsBody` 层级 vs. 掩码**：`collision_layer` = “我是什么”。`collision_mask` = “我扫描什么”。两者设置为相同值会导致自我碰撞或漏检。
5. **`StringName` vs. `String` 在热路径**：`StringName` (`&"key"`) 使用指针比较（O(1)）。`String` 使用字符比较（O(n)）。在热路径的字典键中始终使用 `StringName`。
6. **`@onready` 时间**：在 `_init()` 之后但在 `_ready()` 期间运行。如果需要构造函数时间设置，使用 `_init()`。如果需要树访问，使用 `@onready` 或 `_ready()`。混合它们会导致空值。
7. **服务器查询挂起**：在 `_process` 中调用 `RenderingServer` 或 `PhysicsServer` 获取函数会强制同步管道刷新。这些服务器运行异步——从它们请求数据会挂起整个管道，直到服务器赶上。
8. **`move_and_slide()` API 变更**：返回 `bool`（是否发生碰撞）。速度现在是属性，不是参数。在调用 `move_and_slide()` 之前，`velocity = dir * speed`。

---

## 📂 第 9 部分：模块目录（99 个蓝图）

> [!IMPORTANT]
> 仅加载当前工作流程所需的模块。使用第 2 部分的决策矩阵确定要遵循的链。

### 架构与基础
[基础](references/project-foundations.md) | [组合](references/composition.md) | [应用组合](references/composition-apps.md) | [信号](references/signal-architecture.md) | [自动加载](references/autoload-architecture.md) | [状态](references/state-machine-advanced.md) | [资源](references/resource-data-patterns.md) | [模板](references/project-templates.md) | [分析师](references/analyst.md) | [审计员](references/auditor.md) | [构建器](references/builder.md)

**版本升级（外部中心）**：[godot-version-migration](https://github.com/thedivergentai/gd-agentic-skills/blob/main/skills/godot-version-migration/SKILL.md) — 完整历史路由器（遗留时代、3→4 桥接、4.0→4.7 跳转）；此处不镜像。

### GDScript & 测试
[GDScript 精通](references/gdscript-mastery.md) | [测试模式](references/testing-patterns-expert-testing-patterns.md) | [调试/分析](references/debugging-profiling.md) | [性能优化](references/performance-optimization.md)

### 2D 系统
[2D 动画](references/2d-animation.md) | [2D 物理](references/2d-physics.md) | [瓦片地图](references/tilemap-mastery.md) | [动画播放器](references/animation-player.md) | [动画树](references/animation-tree-mastery.md) | [CharacterBody2D](references/characterbody-2d.md) | [粒子效果](references/particles.md) | [Tween](references/tweening.md) | [着色器基础](references/shaders-basics.md) | [相机系统](references/camera-systems.md)

### 3D 系统
[3D 照明](references/3d-lighting.md) | [3D 材质](references/3d-materials.md) | [3D 世界构建](references/3d-world-building.md) | [3D 物理](references/physics-3d.md) | [导航/寻路](references/navigation-pathfinding.md) | [程序化生成](references/procedural-generation.md) | [射线检测](references/raycasting-queries.md)

### 游戏机制
[能力](references/ability-system.md) | [战斗](references/combat-system.md) | [对话](references/dialogue-system.md) | [经济](references/economy-system.md) | [背包](references/inventory-system.md) | [任务](references/quest-system.md) | [RPG 统计](references/rpg-stats.md) | [回合制](references/turn-system.md) | [音频](references/audio-systems.md) | [场景过渡](references/scene-management.md) | [存档/加载](references/save-load-systems.md) | [秘密](references/mechanic-secrets.md) | [收集](references/game-loop-collection.md) | [波次](references/game-loop-waves.md) | [采集](references/game-loop-harvest.md) | [计时赛](references/game-loop-time-trial.md) | [复活](references/mechanic-revival.md) | [蒙特卡洛平衡器](references/monte-carlo-balancer.md)

### UI & UX
[UI 容器](references/ui-containers.md) | [富文本](references/ui-rich-text.md) | [主题化](references/ui-theming.md) | [输入处理](references/input-handling.md) | [季节性主题](references/theme-easter.md) | [代理视觉](references/agent-vision.md)

### 连接性与平台
[多人游戏](references/multiplayer-networking.md) | [服务器逻辑](references/server-architecture.md) | [导出构建](references/export-builds.md) | [桌面端](references/platform-desktop.md) | [移动端](references/platform-mobile.md) | [Web](references/platform-web.md) | [主机](references/platform-console.md) | [VR](references/platform-vr.md)

### 适配指南
- [从桌面适配到移动端](references/adapt-desktop-to-mobile.md)
- [从移动端适配到桌面端](references/adapt-mobile-to-desktop.md)
- [从单机适配到多人](references/adapt-single-to-multiplayer.md)
- [从2D适配到3D](references/adapt-2d-to-3d.md)
- [从3D适配到2D](references/adapt-3d-to-2d.md)

### 游戏类型蓝图（详尽）
[动作角色扮演游戏](references/genre-action-rpg.md) | [射击游戏](references/genre-shooter.md) | [射击第一人称射击游戏](references/genre-shooter-fps.md) | [即时战略游戏](references/genre-rts.md) | [多人在线战术竞技游戏](references/genre-moba.md) | [类暗黑破坏神游戏](references/genre-roguelike.md) | [生存游戏](references/genre-survival.md) | [开放世界游戏](references/genre-open-world.md) | [银河恶魔城类游戏](references/genre-metroidvania.md) | [平台跳跃游戏](references/genre-platformer.md) | [格斗游戏](references/genre-fighting.md) | [潜行游戏](references/genre-stealth.md) | [沙盒游戏](references/genre-sandbox.md) | [恐怖游戏](references/genre-horror.md) | [解谜游戏](references/genre-puzzle.md) | [赛车游戏](references/genre-racing.md) | [节奏游戏](references/genre-rhythm.md) | [体育游戏](references/genre-sports.md) | [大逃杀游戏](references/genre-battle-royale.md) | [卡牌游戏](references/genre-card-game.md) | [视觉小说](references/genre-visual-novel.md) | [恋爱游戏](references/genre-romance.md) | [模拟游戏](references/genre-simulation.md) | [塔防游戏](references/genre-tower-defense.md) | [挂机点击游戏](references/genre-idle-clicker.md) | [聚会游戏](references/genre-party.md) | [教育游戏](references/genre-educational.md)

---

## 🐛 第10部分：专家诊断模式

### “隐形节点”错误
**症状**：节点存在于树中但未渲染。
**专家诊断链**：`visible`属性 → `z_index` → 父`CanvasLayer`层级错误 → `modulate.a == 0` → 位于摄像机`near`裁剪面之后（3D）→ `SubViewport.render_target_update_mode`未设置 → `CanvasItem`不在任何`CanvasLayer`中（渲染在所有内容之后）。

### “输入被吞噬”错误
**症状**：点击或按键输入间歇性被忽略。
**专家诊断**：另一个具有`mouse_filter = STOP`属性的`Control`节点与目标重叠。或者，模态`PopupMenu`消耗未处理的输入。或者，另一个脚本中的`_unhandled_input()`调用`get_viewport().set_input_as_handled()`。

### “物理抖动”错误
**症状**：角色在接触表面时振动。
**专家诊断**：`Safe Margin`过大。或者，使用`_process`进行移动而不是`_physics_process`（插值不匹配）。或者，碰撞形状在生成时重叠（永久性地相互推离）。

### “内存泄漏”
**症状**：运行期间RAM持续增长。
**专家诊断**：调用`queue_free()`但引用仍保留在Array/Dictionary中。或者，使用`CONNECT_REFERENCE_COUNTED`连接信号而未清理。使用Profiler的“Objects”标签查找遗弃实例。搜索无父节点的`Node`实例。

### “帧峰值”
**症状**：FPS平滑但周期性下降。
**专家诊断**：GDScript垃圾回收过程。或者，同步`load()`大型资源。或者，`NavigationServer`重新烘焙。或者，服务器API查询停滞（在`_process`中请求`RenderingServer`数据）。使用内置Profiler分析 → 查找函数级别的峰值。

---

## 🚀 第11部分：快速入门——Unity (C#) 到 Godot (GDScript)

从Unity生态系统过渡到Godot的资深工程师需要调整的思维模型。

### 1. 节点与GameObject和Components
在Unity中，`GameObject`是`Components`的容器。在Godot中，**一切都是节点**。
- **Unity**：`GameObject` + `Transform` + `MeshFilter` + `Script`。
- **Godot**：一个`MeshInstance3D`节点（它*本身*就是一个Transform和Mesh），并附加了脚本。
- **专家调整**：使用节点组合。如果需要“Health Component”，添加一个`Node`或`Area3D`作为名为“Health”的子节点。使用`RefCounted`为仅逻辑组件以节省内存。

### 2. 场景是嵌套的Prefab
Godot没有“Prefab”，因为**每个场景都是一个Prefab**。
- 你可以在另一个场景中实例化场景，无限嵌套。
- **专家调整**：每个可重用系统（玩家、敌人、UI按钮）都应该是自己的`.tscn`文件。这促进了“后序遍历”（子节点在父节点之前就准备好）。

### 3. 信号与事件/动作
Godot的`Signal`系统是观察者模式的原生实现。
- **Unity**：`event Action OnDeath;`。
- **Godot**：`signal died`。
- **专家调整**：信号是一流公民。它们在检查器中可见，可以动态连接或通过编辑器连接。使用“信号总线”模式（自动加载）进行全局事件以模拟Unity的Singleton管理器。

### 4. 脚本作为类扩展
将脚本附加到节点时，该脚本**就是**该节点。
- **Unity**：`GetComponent<MyScript>()`。
- **Godot**：脚本*扩展*了节点的类（例如，`extends CharacterBody3D`）。
- **专家调整**：使用**类型化GDScript**（`var x: int = 5`）以获得编译加速和编辑器补全。类型化GDScript在编译时已知类型时使用优化操作码。

### 5. 内存管理：无垃圾回收停滞
与Unity的C#可能出现的“GC峰值”不同，GDScript使用引用计数。
- **专家调整**：对象在不再被引用时立即被释放。这提供了确定性的性能并避免了大型Unity项目中常见的间歇性“卡顿”。

### 6. StringNames与性能
Unity使用`int`或`Enum`以提高性能。Godot使用`StringName`。
- **专家调整**：在字典和信号查找中使用`&"name"`进行常数时间（O(1)）指针比较。

---

## 参考
- [Godot 4.7官方文档](https://docs.godotengine.org/en/4.7/)
- [Godot 4.7迁移指南](https://docs.godotengine.org/en/4.7/tutorials/migrating/upgrading_to_godot_4.7.html)
- [Godot Engine GitHub讨论区](https://github.com/godotengine/godot/discussions)
