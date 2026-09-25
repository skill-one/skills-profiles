# Unreal C++ 游戏玩法

编写正确的 UE5 游戏玩法 C++：连接 C++ 与编辑器和蓝图反射宏、游戏玩法框架类角色和模块依赖关系。目标 **UE 5.8**。

## 何时使用

- 在创建 C++ 游戏玩法类（`AActor`、`APawn`、`ACharacter`、`AGameModeBase`、`UActorComponent`）时使用，通过 `UPROPERTY`/`UFUNCTION` 暴露属性/函数，设置游戏模式的默认类，或在 `*.Build.cs` 中添加模块依赖关系。
- 当项目具有包含 `*.h`/`*.cpp` 使用 `UCLASS` 和 `*.Build.cs` 的 `Source/` 树时使用。

**不使用时**：面向设计师的可视逻辑 → `unreal-blueprints`。玩家输入绑定细节 → `unreal-enhanced-input`。AI 逻辑 → `unreal-behavior-trees`。这项技能拥有那些构建在其上的 C++ 类/反射基础。

## 核心工作流程

1. **使用正确的前缀命名。** `A` = 派生自 Actor，`U` = `UObject`/组件派生，`F` = 纯结构体，`E` = 枚举，`I` = 接口。前缀必须与基类匹配。
2. **使用反射宏声明类。** 类上方使用 `UCLASS()`，类体中第一行使用 `GENERATED_BODY()`，并在头文件中作为**最后一行**包含 `#include "ClassName.generated.h"`。
3. **使用 `UPROPERTY` 暴露数据**（编辑器/蓝图可见性 *和* 垃圾回收跟踪），使用 `UFUNCTION` 暴露行为（`BlueprintCallable` 等）。
4. **在构造函数中创建组件**，使用 `CreateDefaultSubobject<T>(TEXT("Name"))` 并设置 `RootComponent`。
5. **了解框架角色：** `AGameModeBase` 设置规则 + 默认类；`APawn`/`ACharacter` 是可控制主体；`APlayerController` 是玩家的意志；`UActorComponent` 是可重用行为。
6. **向 `*.Build.cs` 添加模块依赖关系**（例如 `EnhancedInput`），否则会出现未解决符号链接错误。
7. **通过编译（Live Coding `Ctrl+Alt+F11` 用于函数体；头文件/UPROPERTY 变更需要完整重建）和检查类/属性是否出现在编辑器中来验证**。

## 模式

### 1. 最小 Actor 类（头文件 + 源文件）

```cpp
// Pickup.h
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "Pickup.generated.h"          // 必须是最后一行包含

UCLASS()
class MYGAME_API APickup : public AActor   // MYGAME_API = 你的模块的导出宏
{
    GENERATED_BODY()
public:
    APickup();

    // EditAnywhere = 每个实例调整 & 在 CDO 上；BlueprintReadWrite = BP 获取/设置。
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Pickup")
    int32 ScoreValue = 10;

    // 在 UObject* 指针上使用 UPROPERTY 是防止它被垃圾回收的原因。
    UPROPERTY(VisibleAnywhere)
    TObjectPtr<UStaticMeshComponent> Mesh;   // UE5: TObjectPtr 而不是原始 UStaticMeshComponent*

    UFUNCTION(BlueprintCallable, Category = "Pickup")
    void Collect();

protected:
    virtual void BeginPlay() override;
};
```

```cpp
// Pickup.cpp
#include "Pickup.h"
#include "Components/StaticMeshComponent.h"

APickup::APickup()
{
    Mesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Mesh"));
    RootComponent = Mesh;                     // 网格是这个 Actor 的根
}

void APickup::BeginPlay() { Super::BeginPlay(); }   // 总是调用 Super
void APickup::Collect()   { Destroy(); }
```

### 2. GameMode 连接其默认类

```cpp
// MyGameMode.cpp — 在构造函数中设置，以便引擎生成你的类。
AMyGameMode::AMyGameMode()
{
    DefaultPawnClass      = AMyCharacter::StaticClass();
    PlayerControllerClass = AMyPlayerController::StaticClass();
}
```

### 3. Build.cs 中的模块依赖关系

```csharp
// MyGame.Build.cs
PublicDependencyModuleNames.AddRange(new string[]
{
    "Core", "CoreUObject", "Engine", "InputCore", "EnhancedInput"
});
```

## 陷阱

- **`generated.h` 不是最后一行 / 缺失** — 编译错误，如 "找不到生成的头文件" 或 "预期包含"。它必须是头文件中的最后一行包含。
- **忘记 `GENERATED_BODY()`** — UHT（Unreal Header Tool）错误；它必须是类体中的第一行。
- **没有 `UPROPERTY` 的原始 `UObject*`** — 垃圾回收器看不到它，可能会在你不知情的情况下销毁它。使用 `UPROPERTY` 跟踪每个 `UObject` 指针（在 UE5 中使用 `TObjectPtr`）。
- **使用 Live Coding 进行头文件/UPROPERTY 编辑** — Live Coding 处理函数体，但 `UCLASS`/`UPROPERTY`/头文件的更改需要完整编辑器重启 + 重建。
- **错误的类前缀** — 将 Actor 命名为 `UFoo`（或组件 `AFoo`）会破坏 UHT；前缀必须与基类型匹配。
- **链接时未解决的符号** — 提供 API 的模块不在 `Build.cs` `PublicDependencyModuleNames` 中。
- **在重写的 `BeginPlay`/`Tick` 等中未调用 `Super::`** 会跳过引擎设置。

## 参考

- 对于 `UActorComponent` 创建/附加、`UPROPERTY` 垃圾回收所有权规则（`TObjectPtr`、`TArray<TObjectPtr<>>`、`AddToRoot`）和复制入门，请阅读 `references/components-and-gc.md`。
- 主要文档："Unreal Engine CPP Quick Start" 和 "Gameplay Framework"
  (`https://dev.epicgames.com/documentation/en-us/unreal-engine/gameplay-framework-in-unreal-engine`)。

## 相关技能

- `unreal-blueprints` — 向设计师暴露 C++；BP/C++ 互操作。
- `unreal-enhanced-input` — 在 C++ Pawn/Character 中绑定输入。
- `unreal-behavior-trees` — 从行为树驱动的 C++ AI 任务。
