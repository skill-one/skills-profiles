---
name: unity-navmesh
description: 在 Unity 6.3 LTS 中添加 AI 导航：使用 AI 导航包（NavMeshSurface）烘焙一个 NavMesh，通过 NavMeshAgent.SetDestination 移动智能体，并处理动态障碍物。在设置路径规划、让敌人追击玩家、烘焙导航，或用户提及 NavMesh、NavMeshAgent、NavMeshSurface、NavMeshObstacle 或 Unity 路径规划时使用。
---

# Unity NavMesh (AI 导航)

在 Unity 6.3 LTS 中为 NPC 提供寻路功能：烘焙可行走表面并在障碍物周围移动智能体。
目标为 **Unity 6.3 LTS (6000.3)** 及 **AI 导航包 2.x**。

> **版本陷阱 (Unity 2022+/6):** 旧的内置 **导航窗口** (对象/烘焙选项卡) 已消失。现在烘焙是通过 **AI 导航包** (`com.unity.ai.navigation`) 以 **组件化** 方式进行的：将 **NavMeshSurface** 添加到你的关卡几何体上，然后点击 **烘焙**。*运行时* `NavMeshAgent`/`NavMesh` API 仍然保留在内置的 `UnityEngine.AI` 中。

## 使用场景

- 当智能体需要走向/追逐/巡逻到目标时，烘焙可导航表面，添加动态阻挡物 (`NavMeshObstacle`)，或检查目的地是否可达时使用。
- 当项目包含 AI 导航包、`NavMeshSurface` 组件或使用 `UnityEngine.AI.NavMeshAgent` 的脚本时使用。

**不使用场景：** 决定移动何时/何地移动的逻辑 (FSM、行为树、转向) → `game-ai` (这项技能是 Unity 移动/寻路机制)。非寻路的强制驱动或运动学移动 → `unity-physics`。

## 核心工作流程

1. **安装 AI 导航包** (包管理器 → `com.unity.ai.navigation`)。
2. **烘焙表面：** 选择静态关卡几何体，**添加组件 → 导航 → NavMesh Surface**，设置智能体类型/区域设置，然后点击 **烘焙**。每当几何体、`NavMeshModifier` 或智能体设置更改时，都需要重新烘焙。
3. **为每个移动的 NPC 添加 `NavMeshAgent`**；其半径/高度/速度必须与烘焙的智能体类型匹配，并且必须在烘焙的网格上生成。
4. **通过脚本驱动它** 使用 `SetDestination(targetPos)`；智能体自动转向并避开其他智能体。使用 `remainingDistance`/`pathPending` 检测到达。
5. **使用 `NavMeshObstacle` 处理动态阻挡物** (雕刻) 以便关闭的门/箱子阻挡路径而无需完整重新烘焙。
6. **验证** 使用 AI 导航覆盖层 (烘焙的网格在场景视图中绘制) 并观察智能体如何绕过障碍物到达目标；检查 `NavMeshPath.status` 以检查无法到达的目标。

## 模式

### 1. 使用 NavMeshAgent 追逐/寻求

```csharp
using UnityEngine;
using UnityEngine.AI;

[RequireComponent(typeof(NavMeshAgent))]
public class Chaser : MonoBehaviour
{
    [SerializeField] private Transform target;
    private NavMeshAgent _agent;

    private void Awake() => _agent = GetComponent<NavMeshAgent>();

    private void Update()
    {
        if (target) _agent.SetDestination(target.position);   // 重新寻路朝向目标
    }

    // 到达了吗？pathPending 在存在路径之前的第一个帧中起作用。
    private bool HasArrived() =>
        !_agent.pathPending && _agent.remainingDistance <= _agent.stoppingDistance;
}
```

### 2. 在提交前检查可达性

```csharp
using UnityEngine.AI;

public bool CanReach(NavMeshAgent agent, Vector3 destination)
{
    var path = new NavMeshPath();
    agent.CalculatePath(destination, path);
    return path.status == NavMeshPathStatus.PathComplete;   // vs Partial / Invalid
}
```

### 3. 运行时烘焙 (用于程序化构建或流式传输的关卡)

```csharp
using Unity.AI.Navigation;   // 包命名空间 (NavMeshSurface)

[SerializeField] private NavMeshSurface surface;

// 在生成关卡几何体后，通过代码构建导航网格。
public void RebuildNav() => surface.BuildNavMesh();
```

### 4. 动态阻挡物会雕刻网格

```csharp
// 将一个 NavMeshObstacle (Carve = true) 添加到门/箱子中。存在时它会切割导航网格上的一个洞，使智能体绕过它；移除/禁用它以重新打开路径 — 无需重新烘焙。
```

### 5. 使用 NavMeshLink 连接分离的网格片段 (跳跃、门、间隙)

```csharp
// 两个未接触的烘焙表面（一个悬空平台和下面的地板，两个跨越间隙的平台）是分离的岛屿 — 智能体无法在它们之间寻路。添加组件 > 导航 > NavMesh Link 以连接它们：分配 Start/End 变换，设置宽度 (0 = 点对点)，并切换双向以用于单向或双向。NavMeshLink 属于 Unity.AI.Navigation。它取代了已弃用的内置 OffMeshLink (见陷阱)。
```

## 陷阱

- **寻找导航窗口** — 它在 Unity 6 中不再存在。使用 AI 导航包的 `NavMeshSurface` 组件 + 烘焙。
- **智能体不移动 / 传送到原点** — 它不在烘焙的网格上，或者没有烘焙表面。烘焙表面并在其上生成智能体 (`NavMesh.SamplePosition` 以吸附)。
- **智能体忽略新几何体** — 导航网格已烘焙；运行时生成的阻挡物需要一个 `NavMeshObstacle` (雕刻) 或一个 `surface.BuildNavMesh()` 重新烘焙。
- **每帧调用 `SetDestination` 是浪费的** — 对于移动缓慢的目标，在计时器上重新寻路（例如每 0.2 秒）而不是每帧。
- **智能体半径/高度不匹配** — 如果 `NavMeshAgent` 的大小与烘焙的智能体类型不同，它会被卡在间隙中或漂浮；保持一致性。
- **智能体相互抖动** — 调整 `avoidancePriority` 和质量，或使用一个阻挡物作为真正的静态阻挡物，而不是依赖智能体回避。
- **寻求 `OffMeshLink`** — 内置的 `OffMeshLink` 组件在 AI 导航 2.0 中已**弃用**，并且无法从添加组件菜单中添加。使用一个 **`NavMeshLink`** (从包中，`Unity.AI.Navigation`) 代替 — 它添加基于变换的端点和一个运行时 `activated` 属性。迁移任何现有的 `OffMeshLink`。
- **`CalculatePath` 返回 `PathPartial`** — 目标位于智能体所在的 *不同* 烘焙岛屿上（网格未跨越的间隙）。使用 `NavMeshLink` (模式 5) 连接两者，或扩展几何体以便一个表面覆盖两者；部分路径仅到达近边缘。

## 参考

- 主要文档：AI 导航包手册
  (`https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/index.html`)、`NavMeshLink` 页面
  (`https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/NavMeshLink.html`)
  及其在 `OffMeshLink` 弃用上的 "What's new" 注释
  (`https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/whats-new.html`)，加上
  `ScriptReference/AI.NavMeshAgent`、`ScriptReference/AI.NavMesh`。

## 相关技能

- `game-ai` — 无引擎决策（FSM、行为树、转向）使用这项技能。
- `unity-csharp-scripting` — 智能体周围的 MonoBehaviour 结构。
- `tower-defense` / `fps-shooter` — 组合寻路与游戏玩法的类型。
