# Unity 动画 (Animator / Mecanim)

使用 Unity 6.3 LTS 的 `Animator` 和 Animator 控制器控制动画状态：参数、过渡、混合树、层和人体逆运动学。目标 **Unity 6.3 LTS (6000.3)**。

## 何时使用

- 当将动画片段连接到状态机时使用，通过参数从脚本驱动它们，混合移动（闲置→行走→奔跑）、在移动上叠加上肢动作，或在人体骨架上添加脚/手逆运动学。
- 当项目有 `*.controller`（Animator Controller）和 `*.anim` 资产，或带有 Avatar 的绑定模型时使用。

**不使用时：** 简单的非骨骼值缓动（UI 淡入淡出、位置插值）最好用缓动/协程完成 —— 请参阅 `unity-csharp-scripting`。时间轴过场动画是另一种工具。2D 精灵帧动画也使用 Animator，但使用精灵关键帧。

## 核心工作流程

1. **向模型添加 `Animator`** 并分配 Animator 控制器；对于人体模型，将其骨架设置为 **人体**，以便它具有 Avatar（启用重定向和逆运动学）。
2. **在控制器上定义参数** —— `Float`（速度）、`Bool`（是否着地）、`Int`、`Trigger`（跳跃）—— 以及带有读取这些参数的条件的过渡的状态。
3. **从脚本设置参数**，永远不要直接戳状态：`SetFloat`、`SetBool`、`SetInteger`、`SetTrigger`。状态机会为你解析过渡。
4. **使用混合树（一个 `Float` 如速度驱动闲置↔行走↔奔跑）混合连续运动**，而不是许多离散状态+过渡。
5. **分层附加/覆盖运动**（例如，带有 Avatar Mask 的上肢“瞄准”层）并控制其 `layerWeight`。
6. **在播放模式下在 Animator 窗口中验证** —— 活动状态会高亮显示，参数值会更新，因此你可以确切地看到哪个过渡被触发（或未被触发）。

## 模式

### 1. 从脚本驱动移动 + 单次动作

```csharp
using UnityEngine;

[RequireComponent(typeof(Animator))]
public class CharacterAnim : MonoBehaviour
{
    private Animator _anim;
    // 缓存参数哈希——比每帧字符串查找更快且不易出错。
    private static readonly int Speed     = Animator.StringToHash("Speed");
    private static readonly int IsGrounded= Animator.StringToHash("IsGrounded");
    private static readonly int Jump      = Animator.StringToHash("Jump");

    private void Awake() => _anim = GetComponent<Animator>();

    public void Tick(float planarSpeed, bool grounded)
    {
        _anim.SetFloat(Speed, planarSpeed);     // 驱动 1D 混合树（闲置/行走/奔跑）
        _anim.SetBool(IsGrounded, grounded);    // 控制下落/着陆过渡
    }

    public void DoJump() => _anim.SetTrigger(Jump);  // 一键触发；使用后自动重置
}
```

### 2. 将嘈杂输入平滑为混合参数

```csharp
// dampTime 使 Speed 平滑，以便混合树不会突然跳变；非常适合摇杆。
._anim.SetFloat(Speed, targetSpeed, 0.1f /* dampTime */, Time.deltaTime);
```

### 3. 直接播放/交叉淡入状态（绕过参数条件）

```csharp
// 对于需要立即、明确过渡的击中反应很有用。
._anim.CrossFade("Hit", 0.1f);                    // 在 0.1 秒内混合（归一化）
// 或者立即跳跃：  _anim.Play("Hit");
```

### 4. 等待当前状态完成

```csharp
private System.Collections.IEnumerator AfterAttack()
{
    var info = _anim.GetCurrentAnimatorStateInfo(0);   // 层 0
    yield return new WaitForSeconds(info.length);      // 近似片段长度
    // ...后续逻辑
}
```

## 陷阱

- **`SetTrigger` 被遗漏或“卡住”** —— 触发器会被下一个满足条件的过渡消耗并自动重置；如果没有过渡消耗它，它可能会在稍后意外触发。使用 `ResetTrigger` 清除，或在条件是持续状态时优先使用 `Bool`。
- **字符串参数拼写错误导致静默失败** —— 拼写错误的名字什么也不做。使用 `Animator.StringToHash` 并缓存整型哈希。
- **过渡感觉卡顿** —— `Has Exit Time` 使过渡等待片段达到归一化时间。取消勾选它以实现响应式、条件驱动的过渡（跳跃、击中）。
- **角色滑动或无法移动** —— `Apply Root Motion` 打开但你的代码也移动了 transform（反之亦然）。决定：根运动 *或* 脚本运动，不能两者兼有。
- **上肢层覆盖整个身体** —— 设置层的混合模式（覆盖 vs 附加），分配 Avatar Mask，并调整 `layerWeight`（0–1）。
- **逆运动学无作用** —— 逆运动学仅在 `OnAnimatorIK` 内应用，需要层上启用“逆运动学通道”，并且需要一个人体 Avatar。

## 参考

- 对于 **混合树**（1D vs 2D 自由形式/方向性）、**动画层 + Avatar Mask**，以及 **人体逆运动学**（`OnAnimatorIK`、`SetIKPositionWeight`、`SetIKPosition`、朝向），请阅读 `references/blend-trees-and-ik.md`。
- 主要文档：Unity 手册“动画”部分和 `ScriptReference/Animator`。

## 相关技能

- `unity-csharp-scripting` — 上述使用的 MonoBehaviour 和协程计时。
- `unity-physics` — 移动动画可视化所呈现的身体。
- `game-ai` — 决定何时播放哪个动画状态。
