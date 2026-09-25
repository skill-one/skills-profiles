# Unreal Enhanced Input

使用现代UE5的**Enhanced Input**系统连接玩家输入：数据驱动的Input Actions和Mapping Contexts，而不是传统的Project Settings轴/动作映射。目标**UE 5.8**（Enhanced Input是默认的；传统输入已弃用）。

## 何时使用

- 添加移动/视角/跳跃/射击输入时使用，创建Input Action (`IA_`)和Input Mapping Context (`IMC_`)资源，应用修饰器/触发器，将映射上下文添加到玩家，或在C++或蓝图绑定动作时使用。
- 当项目包含`IA_*`/`IMC_*`资源或引用`EnhancedInput`时使用。

**不使用的情况：**引擎无关的输入*架构*（重绑定策略、缓冲、多设备设计）→ `input-systems`。Pawn/Character C++中这些绑定所在的模块→ `unreal-cpp-gameplay`。

## 核心工作流程

1. **启用模块/插件。** Enhanced Input在UE5中默认启用；对于C++绑定，将`"EnhancedInput"`添加到`*.Build.cs`中的`PublicDependencyModuleNames`。
2. **创建Input Actions (`IA_`)。** 每个都有**值类型**：`Digital (bool)`用于按钮，`Axis1D (float)`用于触发器，`Axis2D (Vector2D)`用于移动/视角。
3. **创建一个Input Mapping Context (`IMC_`)** 将按键/按钮映射到这些动作。使用**修饰器**来塑造原始输入（Negate, Swizzle Input Axis Values, Dead Zone）——例如，将WASD转换为单个Axis2D需要A/S上的Negate和W/S上的Swizzle。使用**触发器**（Pressed, Hold, Tap）来决定*何时*动作触发。
4. **通过`EnhancedInputLocalPlayerSubsystem`** (`AddMappingContext(IMC, Priority)`)将映射上下文添加到玩家，通常在`BeginPlay`/拥有期间。
5. **在`EnhancedInputComponent`上通过`ETriggerEvent`** (`Triggered`, `Started`, `Completed`, …)绑定动作到处理程序，并在处理程序中读取`FInputActionValue`。
6. **在PIE中验证**；Enhanced Input调试控制台命令 (`showdebug enhancedinput`)显示哪些动作被触发及其值。

## 模式

### 1. 添加映射上下文（C++角色）

```cpp
void AMyCharacter::BeginPlay()
{
    Super::BeginPlay();
    if (APlayerController* PC = Cast<APlayerController>(GetController()))
        if (ULocalPlayer* LP = PC->GetLocalPlayer())
            if (auto* Subsystem = LP->GetSubsystem<UEnhancedInputLocalPlayerSubsystem>())
                Subsystem->AddMappingContext(DefaultMappingContext, /*Priority*/ 0);
}
// DefaultMappingContext是一个UPROPERTY(EditAnywhere) TObjectPtr<UInputMappingContext>。
```

### 2. 绑定动作和读取值

```cpp
void AMyCharacter::SetupPlayerInputComponent(UInputComponent* InputComponent)
{
    Super::SetupPlayerInputComponent(InputComponent);

    // 当插件激活时，组件是Enhanced Input组件。
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
    const FVector2D Axis = Value.Get<FVector2D>();          // Axis2D动作
    AddMovementInput(GetActorForwardVector(), Axis.Y);
    AddMovementInput(GetActorRightVector(),   Axis.X);
}
```

### 3. 蓝图等效（节点流程）

```text
事件 BeginPlay
  -> 获取控制器 -> 强制转换为PlayerController -> 获取本地玩家
  -> 获取EnhancedInputLocalPlayerSubsystem -> 添加映射上下文 (IMC_Default, 优先级0)

// IA_Move作为角色的Event Graph中的独立事件节点暴露：
EnhancedInputAction IA_Move (Triggered)
  -> 动作值 (Vector2D) -> 添加移动输入 (Forward * Y, Right * X)
```

## 陷阱

- **完全没有输入** — 映射上下文从未添加 (`AddMappingContext`)，或者玩家还没有本地玩家。在拥有/`BeginPlay`后添加。
- **C++绑定中的链接/编译错误** — `"EnhancedInput"`不在`Build.cs`的`PublicDependencyModuleNames`中。
- **WASD只在两个键上移动/错误轴** — Axis2D需要**修饰器**：在负键（A, S）上使用Negate，在垂直方向（W/S）上使用Swizzle Input Axis Values，以便两个轴都能正确映射。没有修饰器的原始绑定行为异常。
- **`Get<FVector2D>()`返回零** — 值类型不匹配：Input Action是Digital/Axis1D，不是Axis2D。将`Get<T>()`与动作的Value Type匹配。
- **动作意外地每帧触发** — `Triggered`在按下Down触发器时重复；对于单次触发（跳跃按下/释放），使用`Started`/`Completed`，或使用Pressed/Tap触发器。
- **两个上下文冲突** — 多个映射上下文按优先级堆叠；高优先级上下文可以消耗按键。通过优先级和`RemoveMappingContext`管理。

## 参考

- 对于带有Enhanced Input的完整第一/第三人称C++角色（头文件+源代码，包括视角/跳跃和一个控制重绑定说明），请阅读`references/cpp-setup.md`。
- 主要文档："Enhanced Input in Unreal Engine"
  (`https://dev.epicgames.com/documentation/en-us/unreal-engine/enhanced-input-in-unreal-engine`)。

## 相关技能

- `input-systems` — 引擎无关的输入架构和重绑定策略。
- `unreal-cpp-gameplay` — 角色/Pawn类和模块设置。
- `fps-shooter` — 将输入与3D控制器和射击组合。
