# Unity 输入系统（新）

通过 Unity 的 **输入系统包** (`com.unity.inputsystem`, 1.x) 读取输入——基于操作、设备无关、可重新绑定。目标为 **Unity 6.3 LTS**。这是对传统 `Input.GetAxis`/`Input.GetKey` 输入管理器的现代替代方案。

## 何时使用

- 在设置移动/跳跃/射击输入、定义 `.inputactions` 资产（包含操作映射和控制方案）、连接 `PlayerInput` 组件、读取 `Vector2` 操纵杆/WASD 值，或通过一套操作处理手柄+键盘+触摸时使用。
- 当 `Packages/manifest.json` 包含 `com.unity.inputsystem` 或项目具有 `*.inputactions` 资产时使用。

**不使用的情况：** 跨引擎的可重新绑定控制架构 → `input-systems`（此技能是 Unity 特定 API）。在获得输入向量后移动角色 → `unity-physics` / `unity-csharp-scripting`。

## 核心工作流程

1. **检查活动输入处理**（项目设置 → 玩家）。当此设置为 `输入系统包（新）` 或 `两者` 时，包才会接收输入。如果仍有旧的 `Input.GetAxis` 代码，则必须设置为 `两者`。
2. **创建 `.inputactions` 资产。** 添加一个 *操作映射*（例如 `Gameplay`），添加 *操作*（`Move` = 值/Vector2, `Jump` = 按钮键, `Fire` = 按钮键），并将它们绑定到控制和复合绑定（WASD = 2D 向量复合）。
3. **选择读取方式：**
   - **`PlayerInput` 组件**（设计友好）——将其拖到玩家上，指向资产，选择一个 *行为*（发送消息 / 广播 / 触发 Unity 事件 / 触发 C# 事件）。最适合单机/本地合作玩家。
   - **代码中直接读取** (`InputActionReference` / `InputActionAsset`) — 控制最灵活；你 `Enable()` 操作并读取它们。最适合系统和工具。
4. **启用你读取的操作/映射。** `PlayerInput` 会自动启用其默认映射；你自己引用的操作必须 `.Enable()`（并在销毁时禁用）。
5. **切换操作映射** 以适应上下文（游戏玩法 ↔ UI/菜单），而不是为每个处理程序添加保护。
6. **使用输入调试器（窗口 → 分析 → 输入调试器）** 确认设备并验证操作是否触发。

## 模式

### 1. 使用 "发送消息" 的 `PlayerInput`（同一 GameObject 上的处理程序）

```csharp
using UnityEngine;
using UnityEngine.InputSystem;

// PlayerInput (Behavior = 发送消息) 会按名称调用 On<ActionName>(InputValue)。
public class PlayerInputReceiver : MonoBehaviour
{
    private Vector2 _move;

    private void OnMove(InputValue value) => _move = value.Get<Vector2>();   // 移动操作
    private void OnJump(InputValue value) { if (value.isPressed) Jump(); }   // 按钮操作

    private void Update() { /* 从 _move 驱动移动 */ }
    private void Jump() { }
}
```

### 2. 代码中直接读取操作（轮询值）

```csharp
using UnityEngine;
using UnityEngine.InputSystem;

public class DirectMover : MonoBehaviour
{
    [SerializeField] private InputActionReference moveAction;  // 指定移动操作

    private void OnEnable()  => moveAction.action.Enable();    // 必须执行，否则读取为零
    private void OnDisable() => moveAction.action.Disable();

    private void Update()
    {
        Vector2 move = moveAction.action.ReadValue<Vector2>(); // 连续值
        transform.Translate(new Vector3(move.x, 0, move.y) * (5f * Time.deltaTime));
    }
}
```

### 3. 事件回调 + 切换操作映射（游戏玩法 ↔ UI）

```csharp
[SerializeField] private InputActionAsset actions;

private void OnEnable()
{
    actions.FindAction("Gameplay/Fire").performed += OnFire;  // 边缘事件：触发一次
    actions.FindActionMap("Gameplay").Enable();
}
private void OnDisable() => actions.FindAction("Gameplay/Fire").performed -= OnFire;

private void OnFire(InputAction.CallbackContext ctx) => Shoot();  // 如果需要，可以使用 ctx.ReadValue<T>()

private void OpenPauseMenu()                       // 切换上下文，不要到处撒 if 检查
{
    actions.FindActionMap("Gameplay").Disable();
    actions.FindActionMap("UI").Enable();
}
private void Shoot() { }
```

## 陷阱

- **完全没有输入** → 要么活动输入处理仍然是 `输入管理器（旧）`，要么忘记 `Enable()` 操作/映射。`PlayerInput` 自动启用；原始 `InputAction` 不启用。
- **关于旧输入后端的 `InvalidOperationException`** → 某个脚本在活动输入处理为 `新` 时仍然调用 `Input.GetAxis`/`Input.GetKey`。将其移植或设置为 `两者`。
- **使用 `ReadValue` 按钮读取为 0** → 按钮按下是边缘事件；使用 `performed` 回调（或 `WasPressedThisFrame()`），而不是每帧 `ReadValue` 来读取触发器。
- **`发送消息` 处理程序从未触发** → 接收脚本的 GameObject 必须与 `PlayerInput` *相同*；`广播消息` 也能到达子级。
- **泄漏订阅** → 在 `OnDisable` 中取消订阅（`-=`）；在 `OnEnable` 中重新订阅而不取消订阅会导致处理程序重复。
- **触摸/手柄未检测到** → 启用匹配的控制方案，并在输入调试器中确认设备；Vector2 复合绑定需要设置所有四个绑定。

## 参考

- 对于交互式控制 **重新绑定** (`PerformInteractiveRebinding`)、保存/加载绑定为 JSON，以及使用 `PlayerInputManager` 的 **本地多人游戏**，请阅读 `references/rebinding.md`。
- 主要文档：Unity 手册 "输入系统"
  (`https://docs.unity3d.com/Manual/com.unity.inputsystem.html`)。

## 相关技能

- `input-systems` — 跨引擎输入架构（重新绑定、缓冲、多设备）。
- `unity-csharp-scripting` — 处理程序所在的 MonoBehaviour。
- `unity-physics` — 将输入向量应用于 Rigidbody。
