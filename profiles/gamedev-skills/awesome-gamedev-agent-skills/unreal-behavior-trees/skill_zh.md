# Unreal 行为树

使用行为树（Behavior Tree）和黑板（Blackboard）在 UE5 中构建 NPC 作者决策：使用组合体（composites）构建树结构，使用装饰器（decorators）门控分支，使用服务（services）保持状态当前，并从 AIController 运行。目标 **UE 5.8**。

## 使用场景

- 构建敌人/NPC AI 时使用：创建 `BT_`/`BB_` 资源对，构建 Selector/Sequence 分支，添加装饰器（条件）和服务（周期性更新），编写自定义 `BTTask`/`BTService` 节点，或将 AIController 连接到运行树。
- 项目中存在行为树（`BT_`）和黑板（`BB_`）资源以及 `AAIController` 时使用。

**不使用场景：** AI 概念（FSM 与 BT 与转向，跨引擎）→ `game-ai`。纯导航/路径规划数学是引擎导航网格（BT 的 `MoveTo` 使用它）。简单的单次逻辑可能比完整树更便宜，作为小型状态机。

## 核心工作流程

1. **创建对：** 黑板（`BB_`）存储类型化的键（AI 的记忆：`TargetActor`、`LastKnownLocation`、`bIsInvestigating`）；行为树（`BT_`）引用该黑板。
2. **占据和运行。** `AAIController` 占据角色并调用 `RunBehaviorTree(BT)`，这也会初始化引用的黑板。
3. **使用组合体构建。** **Selector** 从左到右运行子节点，直到一个 *成功*（优先级/备用："攻击，否则追击，否则巡逻"）。**Sequence** 运行子节点，直到一个 *失败*（全部执行："移动到掩护位置 → 装填 → 探查"）。**简单并行** 运行一个主任务和一个次要任务。
4. **使用装饰器门控分支**，这些装饰器读取黑板键（例如 "是否有目标？" 保护的战斗分支）。设置 **Observer Aborts**，以便在键更改时重新评估树。
5. **使用附加到分支的服务** 保持黑板当前——它们仅在分支活动时周期性触发（例如通过视线检查更新 `TargetActor`）。
6. **在任务中执行工作**，这些任务返回 `Succeeded`、`Failed` 或 `InProgress`（潜伏任务如 `MoveTo` 完成较晚）。
7. **在 PIE 过程中使用行为树调试器进行验证**——它突出显示运行节点并显示实时黑板值，以便您确切看到哪个分支执行。

## 模式

### 1. 运行树的 AIController (C++)

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

`Observer Aborts: Both` 使战斗分支在设置 `TargetActor` 的瞬间中断巡逻，并在清除时退出——这是使 AI 感觉反应性的原因。

### 3. 从代码更新黑板（例如在看到玩家时）

```cpp
void AEnemyAIController::SetTarget(AActor* Target)
{
    if (UBlackboardComponent* BB = GetBlackboardComponent())
        BB->SetValueAsObject(TEXT("TargetActor"), Target);   // 键名必须与 BB 资源匹配
}
// 清除：BB->ClearValue(TEXT("TargetActor")); 退回到低优先级分支。
```

## 陷阱

- **AI 从未启动**——角色未被占据（将 Pawn 的 *Auto Possess AI* 设置为 "放置在世界或生成" 并分配 AIController），或从未调用 `RunBehaviorTree`。
- **`MoveTo` 立即失败**——关卡中没有导航网格（添加一个 Nav Mesh Bounds Volume），或目标在导航网格外。
- **分支未对更改做出反应**——门控装饰器的 **Observer Aborts** 设置为 None；将其设置为 Self/Lower Priority/Both，以便在键更改时重新评估树。
- **任务挂起树**——自定义任务返回 `InProgress` 且从未调用 `FinishLatentTask`。始终完成潜伏任务。
- **黑板键拼写错误**——`SetValueAsObject("Taget", ...)` 默默无动于衷；键名和类型必须完全匹配，或使用缓存 `FBlackboardKeySelector`。
- **Sequence 与 Selector 混淆**——Sequence = AND（第一个失败即停止）；Selector = OR（第一个成功即停止）。交换它们会反转行为。

## 参考

- 对于 **自定义 C++ `UBTTaskNode`**（即时和潜伏的 `ExecuteTask` 返回 `EBTNodeResult`，带有 `FBlackboardKeySelector`），请阅读 `references/custom-bttask.md`。
- 主要文档："Unreal Engine 中的行为树"
  (`https://dev.epicgames.com/documentation/en-us/unreal-engine/behavior-trees-in-unreal-engine`).

## 相关技能

- `game-ai` — 引擎无关的 AI 设计（FSM、BT、转向、路径规划选择）。
- `unreal-cpp-gameplay` — C++ 中的 AIController 和 pawn 类。
- `fps-shooter` / `tower-defense` — 构成敌人 AI 的类型。
