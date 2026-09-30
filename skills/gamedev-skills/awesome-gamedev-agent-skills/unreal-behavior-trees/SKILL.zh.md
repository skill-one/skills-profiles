---
name: unreal-behavior-trees
description: 使用行为树和黑板在虚幻引擎5中构建NPC AI：组合（选择器/序列）、任务、装饰器、服务，以及从AIController运行树。在创建敌人/NPC AI、BT_/BB_资源、自定义BTTask或BTService节点时使用，或当用户提及行为树、黑板、AIController、BTTask、装饰器或服务时使用。
---

# Unreal 行为树

使用行为树（Behavior Tree）驱动黑板（Blackboard）在 UE5 中构建 NPC 作者决策：使用组合体（composites）构建树结构，使用装饰器（decorators）门控分支，使用服务（services）保持状态当前，并从 AIController 运行它。目标 **UE 5.8**。

## 何时使用

- 在构建敌人/NPC AI 时使用：创建 `BT_`/`BB_` 资产对，构建 Selector/Sequence 分支，添加装饰器（条件）和服务（周期性更新），编写自定义 `BTTask`/`BTService` 节点，或将 AIController 连接到运行树。
- 当项目具有行为树（`BT_`）和黑板（`BB_`）资产以及 `AAIController` 时使用。

**不使用时**：AI 的 *概念*（FSM 与 BT 与转向，跨引擎）→ `game-ai`。纯导航/路径规划数学是引擎的导航网格（BT 的 `MoveTo` 使用它）。简单的单次逻辑可能比完整的树更便宜，作为一个小型状态机。

**行为树还是 StateTree？** UE 5.8 同时提供两者，且行为树未被弃用。StateTree 是 Epic 的通用分层状态机：它结合了 BT 风格的选择，以及显式的状态（States）和转换（Transitions）。如果项目已使用 StateTree 资产，或 AI 自然是一组具有明确转换的模式（巡逻 → 警告 → 战斗），在添加行为树之前请与用户确认。在项目已具有 `BT_`/`BB_` 资产的地方继续使用行为树。

## 核心工作流程

1. **创建对**：黑板（`BB_`）存储类型化的键（AI 的记忆：`TargetActor`、`LastKnownLocation`、`bIsInvestigating`）；行为树（`BT_`）引用该黑板。
2. **占据和运行**。`AAIController` 占据棋子并调用 `RunBehaviorTree(BT)`，这也会初始化引用的黑板。
3. **使用组合体构建**。**Selector** 从左到右运行子节点，直到一个 *成功*（优先级/后备："攻击，否则追击，否则巡逻"）。**Sequence** 运行子节点，直到一个 *失败*（全部执行："移动到掩护 → 重新装填 → 探查"）。**Simple Parallel** 运行一个主要任务和一个次要任务。
4. **使用装饰器门控分支**，这些装饰器读取黑板键（例如 "Has Target?" 保护的战斗分支）。设置 **Observer Aborts**，以便当键更改时树重新评估。
5. **使用附加到分支的服务** 使黑板保持当前——它们仅在分支活动时周期性触发（例如通过视线检查更新 `TargetActor`）。
6. **在任务中执行工作**，这些任务返回 `Succeeded`、`Failed` 或 `InProgress`（潜伏任务如 `MoveTo` 会稍后完成）。
7. **在 PIE 过程中通过行为树调试器进行验证**——它突出显示正在运行的节点并显示实时黑板值，以便您确切看到哪个分支被执行。

## 模式

### 1. 运行树的 AIController（C++）

```cpp
void AEnemyAIController::OnPossess(APawn* InPawn)
{
    Super::OnPossess(InPawn);
    if (BehaviorTree)                 // UPROPERTY(EditAnywhere) TObjectPtr<UBehaviorTree>
        RunBehaviorTree(BehaviorTree); // 初始化并使用 BT 引用的黑板
}
```

### 2. 优先级树（节点结构）

```text
ROOT
└── Selector (尝试战斗，否则调查，否则巡逻)
    ├── Sequence            [装饰器：黑板 'TargetActor' 已设置，Observer Aborts：都]
    │     ├── Task: MoveTo (TargetActor)          // 潜伏：返回 InProgress 然后成功
    │     └── Task: Attack
    ├── Sequence            [装饰器：'LastKnownLocation' 已设置]
    │     ├── Task: MoveTo (LastKnownLocation)
    │     └── Task: Wait (3s) + 清除键
    └── Task: Patrol (BTTask_FindPatrolPoint -> MoveTo)
```

`Observer Aborts: Both` 使战斗分支在 `TargetActor` 设置的瞬间中断巡逻，并在清除时退出——这就是让 AI 感觉反应性的原因。

### 3. 从代码更新黑板（例如在看到玩家时）

```cpp
void AEnemyAIController::SetTarget(AActor* Target)
{
    if (UBlackboardComponent* BB = GetBlackboardComponent())
        BB->SetValueAsObject(TEXT("TargetActor"), Target);   // 键名必须与 BB 资产匹配
}
// 清除：BB->ClearValue(TEXT("TargetActor")); 以回到低优先级分支。
```

## 陷阱

- **AI 从未启动**——棋子未被占据（将棋子的 *Auto Possess AI* 设置为 "Placed in World or Spawned" 并分配 AIController），或从未调用 `RunBehaviorTree`。
- **`MoveTo` 立即失败**——关卡中没有导航网格（添加一个 Nav Mesh Bounds Volume），或目标位于导航网格外。
- **分支未对更改做出反应**——门控装饰器的 **Observer Aborts** 设置为 None；将其设置为 Self/Lower Priority/Both，以便当键更改时树重新评估。
- **任务挂起树**——自定义任务返回 `InProgress` 且从未调用 `FinishLatentTask`。始终完成潜伏任务。
- **黑板键拼写错误**——`SetValueAsObject("Taget", ...)` 默默无动于衷；键名和类型必须完全匹配，或使用缓存的 `FBlackboardKeySelector`。
- **Sequence 与 Selector 混淆**——Sequence = AND（第一个失败即停止）；Selector = OR（第一个成功即停止）。交换它们会反转行为。

## 参考

- 对于 **自定义 C++ `UBTTaskNode`**（即时和潜伏的 `ExecuteTask` 返回 `EBTNodeResult`，带有 `FBlackboardKeySelector`），请阅读 `references/custom-bttask.md`。
- 主要文档："Unreal Engine 中的行为树"
  (`https://dev.epicgames.com/documentation/en-us/unreal-engine/behavior-trees-in-unreal-engine`).

## 相关技能

- `game-ai` — 引擎无关的 AI 设计（FSM、BT、转向、路径规划选择）。
- `unreal-cpp-gameplay` — C++ 中的 AIController 和棋子类。
- `fps-shooter` / `tower-defense` — 构成敌人 AI 的类型。
