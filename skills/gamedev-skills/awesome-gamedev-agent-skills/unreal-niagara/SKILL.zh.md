---
name: unreal-niagara
description: 使用Niagara在虚幻引擎5中创建和控制VFX：系统与发射器、模块与生成/更新阶段、暴露的用户参数，以及从蓝图或C++生成或驱动效果。适用于构建粒子效果、NS_/NE_资源、在运行时生成Niagara系统、设置用户参数，或在虚幻中提及Niagara、VFX或粒子系统时使用。
---

# Unreal Niagara VFX

使用 Niagara 在 UE5 中构建和控制实时视觉特效：理解系统/发射器/模块的层次结构，将可从游戏过程中驱动的参数公开，并在运行时生成特效。目标 **UE 5.8**。（Niagara 取代了传统的 Cascade 系统。）

## 何时使用

- 在创建 Niagara 系统 (`NS_`) 和发射器 (`NE_`)、在生成/更新阶段连接模块、向游戏过程公开 **用户** 参数，或从蓝图或 C++ 生成/驱动特效（冲击、枪口火焰、火焰、魔法）时使用。
- 当项目包含 Niagara `NS_`/`NE_` 资产或引用 `UNiagaraComponent` 时使用。

**不使用的情况：** 材质/着色器编写（表面的外观，而不是粒子）是一个单独的主题；`shader-programming` 涵盖跨引擎着色器概念。特效的音频 → `audio-design`。

## 核心工作流程

1. **理解层次结构。** 一个 **Niagara 系统** (`NS_`) 是你放置/生成的特效；它包含一个或多个 **发射器** (`NE_`，通常是发射器 *模板*)。每个发射器在阶段中运行：**发射器生成/更新**、**粒子生成/更新**、可选的 **事件处理器** 和 **渲染**。
2. **通过模块构建行为**，这些模块在每个阶段从上到下执行（生成速率、添加速度、重力力、生命周期颜色等）。顺序很重要——较晚的模块会读取较早模块写入的值。
3. **了解参数命名空间：** `系统`、`发射器`、`粒子` 和 **`用户`**。只有 **用户命名空间** 的参数会被公开并由蓝图/C++ 设置；其他参数是模拟的内部参数。
4. **在运行时生成**，使用 `UNiagaraFunctionLibrary::SpawnSystemAtLocation`（世界位置）或 `SpawnSystemAttached`（跟随组件/插座），它们返回一个 `UNiagaraComponent`。
5. **通过在返回的组件上设置其用户参数来驱动特效**（颜色、生成速率、目标位置），并 `Activate`/`Deactivate` 它。
6. **在 Niagara 编辑器预览和场景中验证**；检查边界（尤其是 GPU 发射器），并确认特效正确剔除/销毁。

## 模式

### 1. 在世界位置生成一次性特效（C++）

```cpp
#include "NiagaraFunctionLibrary.h"
#include "NiagaraComponent.h"

// ImpactSystem 是一个 UPROPERTY(EditAnywhere) TObjectPtr<UNiagaraSystem>。
void AProjectile::SpawnImpact(const FVector& Location, const FRotator& Rotation)
{
    UNiagaraComponent* FX = UNiagaraFunctionLibrary::SpawnSystemAtLocation(
        GetWorld(), ImpactSystem, Location, Rotation);
    // FX 在一次性完成后自动销毁（系统标记为非循环）。
}
```

### 2. 附着到插座生成（跟随枪支的枪口火焰）

```cpp
UNiagaraComponent* Muzzle = UNiagaraFunctionLibrary::SpawnSystemAttached(
    MuzzleSystem, WeaponMesh, FName("MuzzleSocket"),
    FVector::ZeroVector, FRotator::ZeroRotator,
    EAttachLocation::SnapToTarget, /*bAutoDestroy*/ true);
```

### 3. 在运行时驱动公开的用户参数

```cpp
// 只有用户命名空间的参数可以从游戏过程中设置。名称与用户参数匹配。
if (UNiagaraComponent* Fire = UNiagaraFunctionLibrary::SpawnSystemAttached(
        FireSystem, RootComponent, NAME_None, FVector::ZeroVector, FRotator::ZeroRotator,
        EAttachLocation::KeepRelativeOffset, /*bAutoDestroy*/ false))
{
    Fire->SetVariableFloat(FName("SpawnRate"), 250.f);                 // User.SpawnRate
    Fire->SetVariableLinearColor(FName("FireColor"), FLinearColor::Red);
}
```

### 4. 蓝图的等效（节点流程）

```text
在位置生成系统（系统 = NS_Impact，位置，旋转）  -> 返回 Niagara 组件
在返回的组件上：
  设置 Niagara 变量（浮点数）  名称="SpawnRate"  值=250
  设置 Niagara 变量（线性颜色）  名称="FireColor"  值=Red
```

## 陷阱

- **尝试从游戏过程设置系统/发射器/粒子参数** — 它不会生效。在 **用户** 命名空间中公开它；只有用户参数可以通过组件设置。
- **使用 Cascade 教程** — Cascade 是遗留/已弃用的。Niagara 是当前系统；发射器/模块工作流程不同。
- **特效消失或不正确剔除** — 固定/不正确的边界，尤其是 **GPU 计算** 发射器需要显式固定边界。在发射器/系统上设置边界。
- **循环特效永远不会停止** — 使用 `bAutoDestroy = false` 生成，并且从未 `Deactivate()`；管理返回组件的生命周期，或将系统标记为非循环以用于一次性。
- **GPU 模拟无法驱动游戏过程** — GPU 粒子数据不能轻易地返回到 CPU；游戏过程必须反应的碰撞/事件应使用 CPU 发射器（或 Niagara → 游戏过程通过数据接口），而不是 GPU。
- **模块顺序错误** — 在初始化值之前放置的力/速度模块读取零。注意从上到下的堆栈顺序。

## 参考

- 主要文档："Niagara 特效概述"
  (`https://dev.epicgames.com/documentation/en-us/unreal-engine/overview-of-niagara-effects-for-unreal-engine`)
  和 `UNiagaraFunctionLibrary` / `UNiagaraComponent` API。将 `Niagara` 模块添加到 `*.Build.cs` 以获取 C++ 访问权限。

## 相关技能

- `shader-programming` — 粒子材质的材质/着色器概念。
- `unreal-cpp-gameplay` — 从游戏代码和模块设置中生成特效。
- `unreal-blueprints` — 从视觉脚本触发特效。
