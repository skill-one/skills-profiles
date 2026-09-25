# Unreal 蓝图（可视化脚本）

在 Unreal Engine 5 蓝图中构建游戏逻辑：选择合适的图，清晰地暴露数据，并选择一种不会创建硬引用意大利面条式的通信方法。目标 **UE 5.8**。（蓝图是节点图；下面的代码片段描述了节点流程。）

## 何时使用

- 在编写蓝图类、连接事件图（BeginPlay/Tick/overlap）、使用构造脚本、创建变量/函数/宏或选择两个蓝图如何通信（Cast、接口或事件调度器）时使用。
- 当项目有 `*.uproject` 和蓝图 `*.uasset` 文件，并且用户通过可视化而不是 C++ 进行工作时使用。

**不使用的情况：** 性能关键的系统、大型数据结构或任何受益于源代码控制差异和单元测试的内容 → `unreal-cpp-gameplay`。玩家输入映射 → `unreal-enhanced-input`。AI 逻辑 → `unreal-behavior-trees`。

## 核心工作流程

1. **选择蓝图类型。** 蓝图类（派生自 Actor/Pawn/Character/ActorComponent）定义了可重用的对象。关卡蓝图是每个关卡的图，仅用于关卡特定脚本——不要将可重用逻辑放在这里。
2. **使用构造脚本进行编辑时设置**（过程性放置、从变量配置组件）——它在放置或编辑角色时运行，*不是*在游戏运行时。
3. **使用事件图进行运行时逻辑。** `Event BeginPlay` 用于初始化，输入/overlap 事件用于反应。除非你确实需要每帧工作，否则避免使用 `Event Tick`。
4. **使用变量暴露数据**；点击眼睛图标使变量实例可编辑，并将相关的变量分组到类别中。为获取器标记 **纯** 函数（无 exec 引脚）。
5. **通过耦合选择通信方法**（见模式）：直接 **Cast** 用于你拥有的内容，**蓝图接口** 用于跨类型调用而不依赖硬引用，**事件调度器** 用于一对多广播。
6. **使用蓝图调试器进行验证**：在节点上设置断点，监视变量值，并使用 Print String 在编辑器中运行时（PIE）确认执行路径。

## 模式

### 1. 反应式事件图（无 Tick）

```text
Event BeginPlay
  -> Set 'StartLocation' = GetActorLocation
  -> 绑定事件到 OnComponentBeginOverlap (TriggerVolume) [调用自定义事件 OnEnterZone]

OnEnterZone (Other Actor)
  -> 分支：Other Actor == Player?
       真  -> 打开门 (Timeline 驱动旋转)   // 事件驱动，运行一次
```

优先选择事件（重叠、计时器、调度器）和 Timelines 而不是 Tick 中的轮询。

### 2. 直接引用 + Cast（紧密耦合，谨慎使用）

```text
Overlapped Actor (Actor ref)
  -> Cast To BP_Player
       Cast 失败 -> (不做任何事)
       成功     -> 调用 BP_Player.ApplyDamage(10)
```

`Cast To` 创建对该类的硬引用（它随此蓝图加载）。当调用者确实依赖于此类型时可以使用；否则优先选择接口。

### 3. 蓝图接口（解耦调用）

```text
// 1. 创建 BPI_Interactable 并定义函数 'Interact(Instigator)'。
// 2. 将接口添加到 BP_Door、BP_Chest、BP_Lever，并在每个中实现 'Interact'。
// 3. 调用者，带有任何 Actor ref:
Player 按下 Use
  -> 对象是否实现接口 (BPI_Interactable)?  // 安全检查，无 Cast/硬引用
       真 -> 在目标 Actor 上调用 Interact (消息)
```

### 4. 事件调度器（一对多广播）

```text
// 在 BP_Player 中声明事件调度器 'OnHealthChanged (float NewHealth)'。
TakeDamage -> 设置 Health -> 调用 'OnHealthChanged' (Health)   // 广播

// 在 WBP_HUD BeginPlay: 绑定事件到 'OnHealthChanged' -> 更新生命值条。
// 多个监听器可以绑定；玩家永远不会引用它们。
```

## 陷阱

- **Cast 意大利面条 / 长加载时间** — `Cast To` 链创建硬引用，将整个资源树拉入内存。使用接口或调度器解耦。
- **应该在关卡蓝图中重用的逻辑** — 它不能跨关卡重用。将其放在蓝图类中。
- **过度使用 `Event Tick`** — 每帧节点很快就会累积。使用事件、计时器 (`Set Timer by Event`) 和 Timelines 代替。
- **构造脚本执行游戏逻辑** — 它在编辑器中在编辑/放置时运行；在那里生成游戏角色或启动逻辑会导致仅编辑器中的伪影。在 BeginPlay 中初始化。
- **变量在实例中不可见** — 切换实例可编辑（眼睛图标）；要通过 Spawn 节点在生成前编辑，也标记 "Expose on Spawn"。
- **接口调用未执行任何操作** — 目标未实现接口；在调用前使用 "Does Implement Interface"，或使用安全于非实现者的消息版本。

## 参考

- 对于 **Cast vs 接口 vs 事件调度器** 的决策指南和分步调度器绑定，请阅读 `references/communication.md`。
- 主要文档："蓝图可视化脚本"
  (`https://dev.epicgames.com/documentation/en-us/unreal-engine/overview-of-blueprints-visual-scripting-in-unreal-engine`)。

## 相关技能

- `unreal-cpp-gameplay` — 何时切换到 C++；如何 BP 和 C++ 类互操作。
- `unreal-enhanced-input` — 将输入事件输入这些图的现代方法。
- `unreal-behavior-trees` — 蓝图触发的 AI 决策逻辑。
