# Unity Physics (Rigidbody / PhysX)

使用 Unity 6.3 LTS 的内置 3D 物理引擎（PhysX）使物体移动、碰撞和检测彼此。正确设置 `FixedUpdate` 规范、触发器与碰撞规则以及碰撞层。目标版本为 **Unity 6.3 LTS (6000.3)**。

> **Unity 6.3 LTS 重命名提示：** `Rigidbody.velocity` 现在称为 **`Rigidbody.linearVelocity`**（旧名称已弃用）。从旧教程中复制的代码会发出警告或无法编译。

## 何时使用

- 当给物体施加物理运动（力、速度、重力）、响应碰撞或触发器、设置碰撞层/掩码、进行地面检测或视线检测、或使用关节连接物体时使用。
- 当场景/预制件包含 `Rigidbody` + `Collider` 组件时使用。

**不使用的情况：** 2D 物理引擎 (`Rigidbody2D`, `Collider2D`) 是一个独立的 API — 调整概念但类型不同。跨引擎 *感觉* 调整（时间步长、抖动、隧道）→ `physics-tuning`。读取驱动运动的输入 → `unity-input-system`。

## 核心工作流程

1. **为需要模拟的任何物体添加 `Rigidbody`**；为需要被碰撞的任何物体添加 `Collider`。碰撞需要双方都有 `Collider`，并且至少有一个 `Rigidbody`。
2. **在 `FixedUpdate` 中处理所有物理计算**。在 `Update` 中读取输入，存储意图，然后在 `FixedUpdate` 中应用力 / 设置 `linearVelocity` / 调用 `MovePosition`。
3. **通过物理 API 而不是 Transform 移动物体**。使用 `AddForce`、`linearVelocity` 或 `MovePosition` — 永远不要将 `transform.position` 赋值给非运动学 `Rigidbody`（它会瞬移并破坏碰撞解析）。
4. **选择碰撞与触发器**。实心碰撞会阻挡并调用 `OnCollisionEnter`；带有 `Is Trigger` 选项的 `Collider` 会穿过并调用 `OnTriggerEnter`。
5. **通过层组织交互**。将物体放在层上并编辑层碰撞矩阵（项目设置 → 物理），以便无关事物不会相互测试。
6. **使用物理调试器（窗口 → 分析 → 物理调试器）进行验证**，并注意抖动；如果快速物体穿过墙壁，请提高碰撞检测模式。

## 模式

### 1. 在 `FixedUpdate` 中基于力的移动（带速度限制）

```csharp
using UnityEngine;

[RequireComponent(typeof(Rigidbody))]
public class Mover : MonoBehaviour
{
    [SerializeField] private float accel = 30f, maxSpeed = 8f;
    private Rigidbody _rb;
    private Vector3 _input;   // 从 Update / 输入系统设置

    private void Awake() => _rb = GetComponent<Rigidbody>();

    private void FixedUpdate()
    {
        _rb.AddForce(_input * accel, ForceMode.Acceleration);     // 与质量无关的加速度
        // Unity 6.3 LTS: linearVelocity (原为 'velocity')。限制水平速度。
        Vector3 flat = new(_rb.linearVelocity.x, 0, _rb.linearVelocity.z);
        if (flat.magnitude > maxSpeed)
        {
            flat = flat.normalized * maxSpeed;
            _rb.linearVelocity = new Vector3(flat.x, _rb.linearVelocity.y, flat.z);
        }
    }
}
```

`ForceMode`：`Force`（连续、质量缩放）、`Acceleration`（连续、忽略质量）、`Impulse`（瞬时、质量缩放 — 跳跃）、`VelocityChange`（瞬时、忽略质量）。

### 2. 碰撞与触发器回调

```csharp
// 实心碰撞：双方都有碰撞器，此方有（非运动学）Rigidbody。
private void OnCollisionEnter(Collision col)
{
    Debug.Log($"Hit {col.gameObject.name} at {col.contacts[0].point}");
}

// 重叠：其中一个碰撞器将 'Is Trigger' 设置为 true。至少有一方需要有 Rigidbody。
private void OnTriggerEnter(Collider other)
{
    if (other.CompareTag("Pickup")) Destroy(other.gameObject);
}
```

### 3. 使用带层掩码的射线检测进行地面检测

```csharp
[SerializeField] private LayerMask groundMask;   // 在检视器中设置为您的 "Ground" 层

private bool IsGrounded()
{
    // 向下投射短射线；仅测试 groundMask 上的碰撞器。
    return Physics.Raycast(transform.position, Vector3.down, out RaycastHit hit,
                           1.1f, groundMask);
}
```

### 4. 仍能推动物体的运动平台

```csharp
// 运动学 Rigidbody：不由力驱动，但 MovePosition 插值并正确携带静止物体（直接移动 Transform 会破坏碰撞解析）。
private void FixedUpdate() => _rb.MovePosition(_rb.position + Vector3.right * (2f * Time.fixedDeltaTime));
```

## 陷阱

- **Unity 6.3 LTS 中不存在 `Rigidbody.velocity`** — 使用 `linearVelocity`（`angularVelocity` 未更改）。
- **在动态 Rigidbody 上设置 `transform.position`** — 会瞬移并跳过碰撞。使用 `MovePosition`（运动学/插值）或施加力。
- **在 `Update` 中施加力** — 与帧率相关且抖动。物理计算应在 `FixedUpdate` 中进行。
- **触发器回调从未触发** — 触发器至少需要在两个碰撞器之一上有一个 `Rigidbody`，并且两个碰撞器都启用；两个静态触发器不会报告重叠。
- **快速物体穿过墙壁（隧道现象）** — 将 Rigidbody 的碰撞检测设置为 `Continuous`（或 `Continuous Dynamic`）以用于子弹/快速移动物体。
- **非均匀缩放的 `MeshCollider` 或缩放碰撞器** 行为异常；优先使用原始碰撞器并保持缩放统一。
- **所有物体都与所有物体碰撞** — 浪费成本；分配层并修剪层碰撞矩阵。

## 参考

- 对于射线检测变体（`SphereCast`、`RaycastAll`、`OverlapSphere`、`LayerMask` 位运算）和关节（`FixedJoint`、`HingeJoint`、`ConfigurableJoint`、可断开关节），请阅读 `references/raycasting-and-joints.md`。
- 主要文档：Unity 手册“物理”部分和 `ScriptReference/Rigidbody`、`ScriptReference/Physics.Raycast`。

## 相关技能

- `physics-tuning` — 引擎无关的感觉：固定时间步长、质量/阻力、CCD、稳定性。
- `unity-csharp-scripting` — `FixedUpdate`/`Update` 的分离依赖于此模式。
- `unity-navmesh` — 非力驱动的智能体移动。
