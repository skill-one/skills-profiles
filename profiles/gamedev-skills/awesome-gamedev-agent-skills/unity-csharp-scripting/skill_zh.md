# Unity C# 脚本 (MonoBehaviour)

在 Unity 6 中编写正确的、符合习惯的游戏脚本。确保生命周期、组件访问、序列化和协程正确无误，以便行为具有确定性，且 Inspector 保持实用。目标为 **Unity 6.3 LTS (6000.3)**，C# / .NET Standard 2.1。

## 何时使用

- 编写或修复 `MonoBehaviour` 时使用：选择正确的生命周期回调、读取/缓存组件、将字段暴露给 Inspector，或使用协程运行定时逻辑。
- 当项目包含 `*.cs` 文件、`Assembly-CSharp` 或 `*.asmdef`，以及 `ProjectSettings/` 文件夹时使用。

**不使用时**：移动刚体/碰撞响应 → `unity-physics`；读取玩家输入 → `unity-input-system`；共享数据资源/配置 → `unity-scriptableobjects`；Animator 参数 → `unity-animation`。这项技能属于 *脚本生命周期和 C# 基础设施*，而非那些子系统。

## 核心工作流程

1. **根据目的而非习惯选择回调。** `Awake`（缓存引用，加载时运行一次）、`OnEnable`（订阅事件）、`Start`（依赖于其他对象 `Awake` 的初始化）、`Update`（每帧逻辑/输入轮询）、`FixedUpdate`（物理）、`LateUpdate`（移动后的相机跟随）、`OnDisable`/`OnDestroy`（取消订阅/清理）。
2. **在 `Awake` 中缓存组件查找** — 每帧都不要调用 `GetComponent`。
3. **使用 `[SerializeField] private` 暴露可调参数**，而不是公共字段，这样其他代码无法修改它们，但设计师可以在 Inspector 中编辑它们。
4. **在 `Update` 中使用 `Time.deltaTime` 缩放每帧值**（`Time.fixedDeltaTime` 的语义在 `FixedUpdate` 中自动生效）。
5. **使用协程进行定时逻辑**（延迟、缓动、"先做 X 然后等待然后做 Y"）；使用 `StartCoroutine` 启动它们，并确定性地停止它们。
6. **在 Play 模式下验证**：检查控制台中的空引用异常，确认 Inspector 中的值按预期更新，如果 `Update` 是热点，则观察 Profiler。

## 模式

### 1. 生命周期 + 缓存组件（标准的骨架）

```csharp
using UnityEngine;

[RequireComponent(typeof(Rigidbody))]      // 自动添加依赖，防止空引用
public class PlayerController : MonoBehaviour
{
    [SerializeField] private float moveSpeed = 6f;   // 可在 Inspector 中编辑，代码中为私有
    private Rigidbody _rb;                            // 缓存，每帧不获取

    private void Awake() => _rb = GetComponent<Rigidbody>();  // 加载时缓存一次

    private void Update()
    {
        // 每帧非物理工作。使用 deltaTime 缩放使其与帧率无关。
        transform.Rotate(0f, 90f * Time.deltaTime, 0f);
    }

    private void FixedUpdate()
    {
        // 物理工作应在此处进行（固定步长）。参见 `unity-physics` 技能。
        _rb.MovePosition(_rb.position + transform.forward * moveSpeed * Time.fixedDeltaTime);
    }
}
```

### 2. 使用 `TryGetComponent` 进行安全的组件访问

```csharp
// 避免分配空值，比 `GetComponent` + 空值检查更清晰。
if (other.TryGetComponent<Health>(out var health))
    health.Apply(-10);
```

### 3. 在 Inspector 中正确显示的序列化

```csharp
[SerializeField, Range(0f, 1f)] private float volume = 0.8f;  // 滑块
[SerializeField] private string playerName = "Hero";          // 代码中私有但可序列化

[System.Serializable]                 // 对于普通类序列化/显示是必需的
public class Stats { public int hp = 100; public int mana = 50; }

[SerializeField] private Stats stats = new();  // Inspector 中的嵌套结构化数据
```

### 4. 使用协程进行定时逻辑

```csharp
private void Start() => StartCoroutine(FlashThenHide());

private System.Collections.IEnumerator FlashThenHide()
{
    yield return new WaitForSeconds(0.5f);   // 等待 0.5 秒的游戏时间
    GetComponent<Renderer>().enabled = false;
    yield return null;                       // 下一帧继续
}
```

## 陷阱

- **在 `Update` 中使用 `GetComponent`** — 它每帧都会搜索并严重影响性能。在 `Awake`/`Start` 中缓存引用。
- **在 `Update` 中进行物理操作** — 在 `FixedUpdate` 外使用力或 `MovePosition` 移动 `Rigidbody` 会导致抖动和步长依赖行为。在 `Update` 中读取输入，在 `FixedUpdate` 中应用物理。
- **依赖跨对象 `Start` 顺序** — `Start` 在所有 `Awake` 后运行，但 `Start` 之间的顺序是未定义的。在 `Start` 中进行跨对象连接，在 `Awake` 中进行自我设置。
- **仅为了在 Inspector 中显示而使用 `public` 字段** — 这也允许任何脚本修改它们。改用 `[SerializeField] private`。
- **`gameObject.tag == "Enemy"`** 分配字符串且较慢；使用 `gameObject.CompareTag("Enemy")`。
- **协程在 GameObject 被禁用时停止** — 禁用对象的协程会被杀死；如果必须存活于切换，请在 `OnEnable` 中重新 `StartCoroutine`。
- **`Update` 在 `Start` 之前从不运行，但第一个 `Update` 可能与 `Start` 在同一帧运行** — 如果设置分叉不当，请防止未初始化的字段。

## 参考

- 对于完整的事件执行顺序表和高级协程模式（自定义 `CustomYieldInstruction`、通过句柄停止、`WaitUntil`/`WaitWhile`），请阅读 `references/lifecycle-and-coroutines.md`。
- 主要文档：Unity Manual "Event function execution order" (`https://docs.unity3d.com/Manual/execution-order.html`) 和 `ScriptReference/MonoBehaviour`。

## 相关技能

- `unity-physics` — `Rigidbody`、碰撞和 `FixedUpdate` 运动。
- `unity-input-system` — 将玩家输入读取到这些脚本中。
- `unity-scriptableobjects` — 在脚本之间共享数据/配置，无需单例。
