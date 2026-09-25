# Unity NavMesh (AI 导航)

为 Unity 6.3 LTS 中的 NPC 提供寻路功能：烘焙可行走表面并在障碍物周围移动智能体。
目标为 **Unity 6.3 LTS (6000.3)** 及 **AI 导航包 2.x**。

> **版本陷阱 (Unity 2022+/6):** 旧的内置 **导航窗口** (对象/烘焙选项卡) 已消失。现在烘焙是通过 **AI 导航包** (`com.unity.ai.navigation`) 以 **组件化** 方式进行的：将 **NavMeshSurface** 添加到你的关卡几何体上，然后点击 **烘焙**。*运行时* `NavMeshAgent`/`NavMesh` API 仍然位于内置的 `UnityEngine.AI` 中。

## 使用场景

- 当智能体需要走向目标、追逐或巡逻时，烘焙可导航表面，添加动态阻挡物 (`NavMeshObstacle`)，或检查目的地是否可达时使用。
- 当项目包含 AI 导航包、`NavMeshSurface` 组件，或使用 `UnityEngine.AI.NavMeshAgent` 的脚本时使用。

**不使用场景：** 决策逻辑（何时/何地移动）的 *逻辑* (状态机、行为树、转向) → `game-ai` (此技能是 Unity 的移动/寻路机制)。非寻路的强制驱动或运动学移动 → `unity-physics`。

## 核心工作流程

1. **安装 AI 导航包** (包管理器 → `com.unity.ai.navigation`)。
2. **烘焙表面：** 选择静态关卡几何体，**添加组件 → 导航 → NavMesh Surface**，设置智能体类型/区域设置，然后点击 **烘焙**。几何体、`NavMeshModifier` 或智能体设置更改时重新烘焙。
3. **为每个移动的 NPC 添加 `NavMeshAgent`**；其半径/高度/速度必须与烘焙的智能体类型匹配，并且必须在烘焙的网格上生成。
4. **通过脚本驱动** 使用 `SetDestination(targetPos)`；智能体自动转向并避开其他智能体。使用 `remainingDistance`/`pathPending` 检测到达。
5. **使用 `NavMeshObstacle` 处理动态阻挡物** (雕刻) 以便关闭的门/箱子阻挡路径而无需完整重新烘焙。
6. **验证** 使用 AI 导航覆盖层（烘焙的网格在场景视图中绘制）并观察智能体绕障碍物到达目标；检查 `NavMeshPath.status` 以检查无法到达的目标。

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
        if (target) _agent.SetDestination(target.position);   // 重新寻路至目标
    }

    // 到达？pathPending 在存在路径之前的第一个帧中起作用。
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
    return path.status == NavMeshPathStatus.PathComplete;   // 与 Partial / Invalid 对比
}
```

### 3. 运行时烘焙（用于程序化构建或流式加载的关卡）

```csharp
using Unity.AI.Navigation;   // 包命名空间 (NavMeshSurface)

[SerializeField] private NavMeshSurface surface;

// 生成关卡几何体后，在代码中构建导航网格。
public void RebuildNav() => surface.BuildNavMesh();
```

### 4. 动态阻挡物（雕刻网格）

```csharp
// 为门/箱子添加一个 NavMeshObstacle (Carve = true)。存在时它在导航网格中切割一个洞，使智能体绕过它；移除/禁用它以重新开放路径 — 无需重新烘焙。
```

## 陷阱

- **寻找导航窗口** — 它在 Unity 6 中不再存在。使用 AI 导航包的 `NavMeshSurface` 组件 + 烘焙。
- **智能体不移动 / 传送到原点** — 它不在烘焙的网格上，或者没有烘焙表面。烘焙表面并在其上生成智能体 (`NavMesh.SamplePosition` 以吸附)。
- **智能体忽略新几何体** — 导航网格已烘焙；运行时生成的阻挡物需要一个 `NavMeshObstacle` (雕刻) 或 `surface.BuildNavMesh()` 重新烘焙。
- **每帧调用 `SetDestination` 浪费资源** — 对于移动缓慢的目标，使用计时器重新寻路（例如每 0.2 秒）而不是每帧。
- **智能体半径/高度不匹配** — 如果 `NavMeshAgent` 的大小与烘焙的智能体类型不同，它会被卡在缝隙中或漂浮；保持一致性。
- **智能体相互抖动** — 调整 `avoidancePriority` 和质量，或使用障碍物作为真正的静态阻挡物而不是依赖智能体避开。

## 参考

- 主要文档：AI 导航包手册 (`https://docs.unity3d.com/Packages/com.unity.ai.navigation@2.0/manual/index.html`) 和 `ScriptReference/AI.NavMeshAgent`, `ScriptReference/AI.NavMesh`。

## 相关技能

- `game-ai` — 适用于此的引擎无关决策逻辑 (状态机、行为树、转向)。
- `unity-csharp-scripting` — 围绕智能体的 MonoBehaviour 结构。
- `tower-defense` / `fps-shooter` — 组合寻路与游戏玩法的类型。
