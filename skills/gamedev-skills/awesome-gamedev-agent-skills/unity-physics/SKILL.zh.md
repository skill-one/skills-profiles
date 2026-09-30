---
name: unity-physics
description: 在 Unity 6.3 LTS 中设置 3D 物理效果：Rigidbody 运动和力、碰撞体、触发器与碰撞、基于层的碰撞、射线投射和关节。在添加 Rigidbody、处理 OnCollisionEnter/OnTriggerEnter、调整碰撞层、投射射线或用户提及 Unity 物理、AddForce、isKinematic 或 linearVelocity 时使用。
---

# Unity Physics (Rigidbody / PhysX)

使用 Unity 6.3 LTS 的内置 3D 物理引擎（PhysX）使对象移动、碰撞和检测彼此。确保 `FixedUpdate` 规范、触发器与碰撞规则以及碰撞层设置正确。目标版本为 **Unity 6.3 LTS (6000.3)**。

> **Unity 6.3 LTS 重命名提示：** `Rigidbody.velocity` 现在称为 **`Rigidbody.linearVelocity`**（旧名称已弃用）。从旧教程中复制的代码会发出警告或无法编译。

## 使用场景

- 当给对象施加物理运动（力、速度、重力）、响应碰撞或触发器、设置碰撞层/掩码、进行地面检测或视线检测，或使用关节连接物体时使用。
- 当场景/预制件包含 `Rigidbody` + `Collider` 组件时使用。

**不适用场景：** 2D 物理 (`Rigidbody2D`, `Collider2D`) 是一个独立的 API — 调整概念，但类型不同。跨引擎 *感觉* 调整（时间步长、抖动、隧道）→ `physics-tuning`。读取驱动移动的输入 → `unity-input-system`。

## 核心工作流程

1. **为需要模拟的任何对象添加 `Rigidbody`**；为需要被击中的任何对象添加 `Collider`。碰撞需要在双方都至少有一个 `Collider` 和一个 `Rigidbody`。
2. **在 `FixedUpdate` 中执行所有物理计算**。在 `Update` 中读取输入，存储意图，然后在 `FixedUpdate` 中应用力 / 设置 `linearVelocity` / 调用 `MovePosition`。
3. **通过物理 API 而不是 Transform 移动物体**。使用 `AddForce`、`linearVelocity` 或 `MovePosition` — 永远不要将 `transform.position` 赋值给非运动学 `Rigidbody`（它会瞬移并破坏碰撞解决）。
4. **选择碰撞与触发器**。实心碰撞会阻挡并调用 `OnCollisionEnter`；带有 `Is Trigger` 选项的 `Collider` 会穿过并调用 `OnTriggerEnter`。
5. **通过层组织交互**。将对象放在层上并编辑层碰撞矩阵（项目设置 → 物理），以便无关对象不会相互测试。
6. **使用物理调试器（窗口 → 分析 → 物理调试器）进行验证**，并观察是否有抖动；如果快速移动的物体穿过墙壁，请提高碰撞检测模式。

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
// 实心碰撞：双方都有碰撞器，此对象有一个（非运动学）Rigidbody。
private void OnCollisionEnter(Collision col)
{
    Debug.Log($"Hit {col.gameObject.name} at {col.contacts[0].point}");
}

// 重叠：其中一个碰撞器将 'Is Trigger' 设置为 true。至少有一方需要 `Rigidbody`。
private void OnTriggerEnter(Collider other)
{
    if (other.CompareTag("Pickup")) Destroy(other.gameObject);
}
```

### 3. 使用层掩码的射线检测进行地面检测

```csharp
[SerializeField] private LayerMask groundMask;   // 在检视器中设置为您的 "Ground" 层

private bool IsGrounded()
{
    // 向下投射短射线；仅测试 groundMask 上的碰撞器。
    return Physics.Raycast(transform.position, Vector3.down, out RaycastHit hit,
                           1.1f, groundMask);
}
```

### 4. 仍能推动物体的运动学平台

```csharp
// 运动学 Rigidbody：不由力驱动，但 MovePosition 插值并正确携带静止物体（直接移动 Transform 会破坏碰撞解决）。
private void FixedUpdate() => _rb.MovePosition(_rb.position + Vector3.right * (2f * Time.fixedDeltaTime));
```

## 陷阱

- **Unity 6.3 LTS 中不存在 `Rigidbody.velocity`** — 使用 `linearVelocity`（`angularVelocity` 未更改）。
- **在动态 Rigidbody 上设置 `transform.position`** — 会瞬移并跳过碰撞。使用 `MovePosition`（运动学/插值）或施加力。如果你确实要写入 Transform，物理查询（`Raycast`、`OverlapSphere`）会看到旧位置，直到下一个物理步骤 — 在同一帧查询前调用一次 `Physics.SyncTransforms()`，但不要每帧都调用。
- **`CharacterController` 上永远不会触发 `OnCollisionEnter`** — `CharacterController.Move` 会绕过 Rigidbody 系统；它通过 `OnControllerColliderHit(ControllerColliderHit)` 报告碰撞。不要添加 Rigidbody 来“修复”它 — 这两种移动模式是互斥的。
- **`Physics.Raycast` 默认忽略触发器** — 射线不会报告触发器碰撞器，除非你传递 `QueryTriggerInteraction.Collide`（或切换全局 `Physics.queriesHitTriggers` / 项目设置 → 物理 → 查询触发器）。它也会在射线起点位于目标碰撞器内部时返回 `false`。
- **静止的 Rigidbody 在你移动或禁用其支撑物后仍会保持静止** — 低于睡眠阈值时，物体会进入睡眠状态。碰撞和 `AddForce` 会自动唤醒它，但通过 Transform 移动 *静态* 碰撞器（无 Rigidbody）可能不会，所以当地板滑走时，箱子会悬浮在半空中。在受影响的物体上调用 `Rigidbody.WakeUp()`。
- **在 `Update` 中施加力** — 与帧率相关且抖动。物理计算应在 `FixedUpdate` 中进行。
- **触发器回调永远不会触发** — 触发器至少需要在两个碰撞器之一上有一个 `Rigidbody`，并且两个碰撞器都启用；两个静态触发器不会报告重叠。
- **快速移动的物体会穿过墙壁（隧道）** — 提高 Rigidbody 的碰撞检测模式。注意 `Continuous` 仅针对 **静态碰撞器**（与其他动态物体交互时会回退到 Discrete）；`Continuous Dynamic` 也会针对其他连续动态物体；`Continuous Speculative` 会针对所有物体且更高效。对于子弹，也可以考虑沿轨迹使用 `SphereCast`/`Raycast` 而不是碰撞器。
- **非均匀缩放的 `MeshCollider` 或缩放碰撞器** 会出现异常行为；优先使用原始碰撞器并保持缩放一致。
- **在运动物体上使用凹面 `MeshCollider`** — Mesh 碰撞器默认为凹面，且凹面只能用于静态或运动学；两个凹面碰撞器永远不会发生碰撞。对于动态 Rigidbody，在 MeshCollider 上启用 **凸面**，或使用原始物体构建复合碰撞器。
- **所有东西都会与所有东西碰撞** — 浪费成本；分配层并修剪层碰撞矩阵。

## 参考

- 对于射线检测变体（`SphereCast`、`RaycastAll`、`OverlapSphere`、`LayerMask` 位运算）和关节（`FixedJoint`、`HingeJoint`、`ConfigurableJoint`、可断开关节），请阅读 `references/raycasting-and-joints.md`。
- 主要文档：Unity 手册“物理”部分和 `ScriptReference/Rigidbody`、`ScriptReference/Physics.Raycast`。对于新增的陷阱：`ScriptReference/CollisionDetectionMode`、`ScriptReference/Physics-queriesHitTriggers`、`ScriptReference/MonoBehaviour.OnControllerColliderHit`、`ScriptReference/Physics.SyncTransforms`、`ScriptReference/Rigidbody.WakeUp`，以及手册页面“刚体物理简介”（睡眠）和“网格碰撞器简介”（凹面与凸面）。

## 相关技能

- `physics-tuning` — 引擎无关的感觉：固定时间步长、质量/阻力、CCD、稳定性。
- `unity-csharp-scripting` — `FixedUpdate`/`Update` 的分离依赖于此模式。
- `unity-navmesh` — 非力驱动的智能体移动。
