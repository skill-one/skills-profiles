# Unreal Engine C++ 专业技能

本技能提供使用 C++ 开发 Unreal Engine 5 的专家级指南。它专注于编写健壮、高性能且符合标准的代码。

## 使用场景
在以下情况下使用此技能：
- 开发 Unreal Engine 5.x 项目的 C++ 代码
- 编写 Actor、Component 或 UObject 派生类
- 优化 Unreal Engine 中的性能关键代码
- 调试内存泄漏或垃圾回收问题
- 实现 Blueprint 暴露的功能
- 遵循 Epic Games 的编码标准和规范
- 使用 Unreal 的反射系统（UCLASS、USTRUCT、UFUNCTION）
- 管理资源加载和软引用

不使用此技能的情况：
- 仅使用 Blueprint 的项目（没有 C++ 代码）
- 开发 Unreal Engine 版本低于 5.x 的项目
- 使用非 Unreal 引擎
- 任务与 Unreal Engine 开发无关

## 核心原则

1.  **UObject & 垃圾回收**：
    *   始终使用 `UPROPERTY()` 为 `UObject*` 成员变量，以确保它们被垃圾回收器 (GC) 跟踪。
    *   如果需要在 UObject 图之外保留根引用，请使用 `TStrongObjectPtr<>`，但通常优先使用 `addToRoot()`。
    *   理解 `IsValid()` 检查与 `nullptr` 的区别。`IsValid()` 安全处理挂起销毁状态。

2.  **Unreal 反射系统**：
    *   使用 `UCLASS()`、`USTRUCT()`、`UENUM()`、`UFUNCTION()` 将类型暴露给反射系统和 Blueprint。
    *   尽可能减少 `BlueprintReadWrite`；对于不应被 UI/Level BP 逻辑覆盖的状态，优先使用 `BlueprintReadOnly`。

3.  **性能优先**：
    *   **Tick**：默认情况下禁用 Tick (`bCanEverTick = false`)。只有绝对必要时才启用。优先使用计时器 (`GetWorldTimerManager()`) 或事件驱动逻辑。
    *   **类型转换**：避免在热循环中使用 `Cast<T>()`。在 `BeginPlay` 中缓存引用。
    *   **结构体 vs 类**：使用 `F` 结构体表示数据密集型、非 UObject 类型，以减少开销。

## 命名规范（严格）

遵循 Epic Games 的编码标准：

*   **模板**：以 `T` 开头（例如，`TArray`、`TMap`）。
*   **UObject**：以 `U` 开头（例如，`UCharacterMovementComponent`）。
*   **AActor**：以 `A` 开头（例如，`AMyGameMode`）。
*   **SWidget**：以 `S` 开头（Slate 控件）。
*   **结构体**：以 `F` 开头（例如，`FVector`）。
*   **枚举**：以 `E` 开头（例如，`EWeaponState`）。
*   **接口**：以 `I` 开头（例如，`IInteractable`）。
*   **布尔值**：以 `b` 开头（例如，`bIsDead`）。

## 常见模式

### 1. 健壮的组件查找
避免在 `Tick` 中使用 `GetComponentByClass`。在 `PostInitializeComponents` 或 `BeginPlay` 中执行。

```cpp
void AMyCharacter::PostInitializeComponents() {
    Super::PostInitializeComponents();
    HealthComp = FindComponentByClass<UHealthComponent>();
    check(HealthComp); // 如果开发中缺少则强制失败
}
```

### 2. 接口实现
使用接口解耦系统（例如，交互系统）。

```cpp
// 接口调用检查
if (TargetActor->Implements<UInteractable>()) {
    IInteractable::Execute_OnInteract(TargetActor, this);
}
```

### 3. 异步加载（软引用）
避免使用硬引用 (`UPROPERTY(EditDefaultsOnly) TSubclassOf<AActor>`) 加载大型资源，这会强制加载顺序。使用 `TSoftClassPtr` 或 `TSoftObjectPtr`。

```cpp
UPROPERTY(EditAnywhere, BlueprintReadWrite)
TSoftClassPtr<AWeapon> WeaponClassToLoad;

void AMyCharacter::Equip() {
    if (WeaponClassToLoad.IsPending()) {
        WeaponClassToLoad.LoadSynchronous(); // 或使用 StreamableManager 异步加载
    }
}
```

## 调试

*   **日志记录**：使用 `UE_LOG` 配合自定义分类。
    ```cpp
    DEFINE_LOG_CATEGORY_STATIC(LogMyGame, Log, All);
    UE_LOG(LogMyGame, Warning, TEXT("Health is low: %f"), CurrentHealth);
    ```
*   **屏幕消息**：
    ```cpp
    if (GEngine) GEngine->AddOnScreenDebugMessage(-1, 5.f, FColor::Red, TEXT("Died!"));
    ```
*   **可视化日志器**：对 AI 调试极其有用。实现 `IVisualLoggerDebugSnapshotInterface`。

## PR 提交前的检查清单

- [ ] 此 Actor 是否需要 Tick？能否使用计时器？
- [ ] 所有 `UObject*` 成员是否都使用 `UPROPERTY` 包装？
- [ ] 硬引用（TSubclassOf）是否导致加载链？能否使用软指针？
- [ ] 是否清理了 `EndPlay` 中验证的委托？

## 限制
- 仅在任务明确符合上述范围时使用此技能。
- 不要将输出视为环境特定验证、测试或专家评审的替代品。
- 如果缺少必要的输入、权限、安全边界或成功标准，请停止并请求澄清。
