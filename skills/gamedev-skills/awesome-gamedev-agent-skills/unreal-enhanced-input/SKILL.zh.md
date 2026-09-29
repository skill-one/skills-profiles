---
name: unreal-enhanced-input
description: 在虚幻引擎5中使用增强输入设置玩家输入：输入动作、输入映射上下文、修饰符和触发器，添加映射上下文，并通过ETriggerEvent绑定动作。在连接移动/视角/跳跃输入、创建IA_/IMC_资源、通过C++或蓝图绑定时使用，或在用户提到增强输入、输入映射上下文、输入动作、IA_/IMC_或ETriggerEvent时使用。
---

# Unreal 增强输入

使用现代 UE5 的 **增强输入** 系统连接玩家输入：基于数据的输入动作和映射上下文，而不是传统的项目设置轴/动作映射。目标 **UE 5.8**（增强输入是默认的；传统输入已弃用）。

## 何时使用

- 添加移动/视角/跳跃/射击输入时使用，创建输入动作 (`IA_`) 和输入映射上下文 (`IMC_`) 资产，应用修饰器/触发器，将映射上下文添加到玩家，或在 C++ 或蓝图绑定动作时使用。
- 当项目包含 `IA_*`/`IMC_*` 资产或引用 `EnhancedInput` 时使用。

**不使用的情况：** 引擎无关的输入 *架构*（重新绑定策略、缓冲、多设备设计）→ `input-systems`。那些绑定存在于 Pawn/Character C++ 中的 → `unreal-cpp-gameplay`。

## 核心工作流程

1. **启用模块/插件。** 增强输入在 UE5 中默认启用；对于 C++ 绑定，请将 `"EnhancedInput"` 添加到 `*.Build.cs` 中的 `PublicDependencyModuleNames`。
2. **创建输入动作 (`IA_`)。** 每个动作都有一个 **值类型**：`Digital (bool)` 用于按钮，`Axis1D (float)` 用于触发器，`Axis2D (Vector2D)` 用于移动/视角。
3. **创建一个输入映射上下文 (`IMC_`)** 将按键/按钮映射到这些动作。使用 **修饰器** 来塑造原始输入（否定、交换输入轴值、死区）——例如，将 WASD 转换为一个 Axis2D 需要对 A/S 应用否定，对 W/S 应用交换输入轴值。使用 **触发器**（按下、保持、轻点）来决定 *何时* 动作触发。
4. **通过 `EnhancedInputLocalPlayerSubsystem`** (`AddMappingContext(IMC, Priority)`) 将映射上下文添加到玩家，通常在 `BeginPlay`/拥有时。
5. **通过 `EnhancedInputComponent` 上的 `ETriggerEvent`** (`Triggered`, `Started`, `Completed`, …) 绑定动作到处理程序，并在处理程序中读取 `FInputActionValue`。
6. **在 PIE 中验证；** 增强输入调试控制台命令 (`showdebug enhancedinput`) 显示哪些动作被触发及其值。

## 模式

### 1. 添加映射上下文 (C++ 角色)

```cpp
void AMyCharacter::BeginPlay()
{
    Super::BeginPlay();
    if (APlayerController* PC = Cast<APlayerController>(GetController()))
        if (ULocalPlayer* LP = PC->GetLocalPlayer())
            if (auto* Subsystem = LP->GetSubsystem<UEnhancedInputLocalPlayerSubsystem>())
                Subsystem->AddMappingContext(DefaultMappingContext, /*Priority*/ 0);
}
// DefaultMappingContext 是一个 UPROPERTY(EditAnywhere) TObjectPtr<UInputMappingContext>。
```

### 2. 绑定动作和读取值

```cpp
void AMyCharacter::SetupPlayerInputComponent(UInputComponent* InputComponent)
{
    Super::SetupPlayerInputComponent(InputComponent);

    // 当插件激活时，组件是增强输入组件。
    if (UEnhancedInputComponent* EIC = Cast<UEnhancedInputComponent>(InputComponent))
    {
        EIC->BindAction(MoveAction, ETriggerEvent::Triggered, this, &AMyCharacter::Move);
        EIC->BindAction(LookAction, ETriggerEvent::Triggered, this, &AMyCharacter::Look);
        EIC->BindAction(JumpAction, ETriggerEvent::Started,   this, &ACharacter::Jump);
        EIC->BindAction(JumpAction, ETriggerEvent::Completed, this, &ACharacter::StopJumping);
    }
}

void AMyCharacter::Move(const FInputActionValue& Value)
{
    const FVector2D Axis = Value.Get<FVector2D>();          // Axis2D 动作
    AddMovementInput(GetActorForwardVector(), Axis.Y);
    AddMovementInput(GetActorRightVector(),   Axis.X);
}
```

### 3. 蓝图等效（节点流程）

```text
事件 BeginPlay
  -> 获取控制器 -> 强制转换为 PlayerController -> 获取本地玩家
  -> 获取 EnhancedInputLocalPlayerSubsystem -> 添加映射上下文 (IMC_Default, 优先级 0)

// IA_Move 作为其自己的事件节点在角色的 Event Graph 中暴露：
增强输入动作 IA_Move (触发)
  -> 动作值 (Vector2D) -> 添加移动输入 (Forward * Y, Right * X)
```

## 陷阱

- **完全没有输入** — 映射上下文从未添加 (`AddMappingContext`)，或者玩家还没有本地玩家。在拥有/`BeginPlay` 后添加。
- **C++ 绑定中的链接/编译错误** — `"EnhancedInput"` 不在 `Build.cs` 的 `PublicDependencyModuleNames` 中。
- **WASD 仅在两个键上移动 / 错误的轴** — Axis2D 需要 **修饰器**：对负键 (A, S) 应用否定，对垂直 (W/S) 应用交换输入轴值，以便两个轴都能正确映射。没有修饰器的原始绑定行为异常。
- **`Get<FVector2D>()` 返回零** — 值类型不匹配：输入动作是 Digital/Axis1D，不是 Axis2D。将 `Get<T>()` 与动作的值类型匹配。
- **动作意外地每帧触发** — `Triggered` 在按下触发器时重复；对于一次性动作（跳跃按下/释放），使用 `Started`/`Completed`，或使用按下/轻点触发器。
- **两个上下文冲突** — 多个映射上下文按优先级堆叠；高优先级上下文可以消耗一个键。通过优先级和 `RemoveMappingContext` 进行管理。

## 参考

- 对于具有增强输入的完整第一/第三人称 C++ 角色（头文件 + 源代码，包括视角/跳跃和一个控制重绑定说明），请阅读 `references/cpp-setup.md`。
- 主要文档： "Unreal Engine 中的增强输入"
  (`https://dev.epicgames.com/documentation/en-us/unreal-engine/enhanced-input-in-unreal-engine`)。

## 相关技能

- `input-systems` — 引擎无关的输入架构和重新绑定策略。
- `unreal-cpp-gameplay` — 角色/Pawn 类和模块设置。
- `fps-shooter` — 将输入与 3D 控制器和射击组合。
