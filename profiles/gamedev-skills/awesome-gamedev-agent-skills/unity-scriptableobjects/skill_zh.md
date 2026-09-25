# Unity ScriptableObject 架构

使用 `ScriptableObject` 资源在 Unity 6.3 LTS 中存储共享数据并解耦系统——配置、事件通道和注册表作为项目资源存在，而不是硬编码到场景或单例中。目标 **Unity 6.3 LTS (6000.3)**。

## 何时使用

- 当你需要设计师可编辑的配置（武器属性、关卡数据）、在无关系统中共享一个值、通过事件通道将发送者解耦到监听者，或构建一个活动对象运行时注册表时使用——无需 `static`/单例管理器。
- 当项目有由 `: ScriptableObject` 类支持的 `*.asset` 数据文件时使用。

**不使用时：** 每个游戏对象实例不同的运行时状态（应属于 MonoBehaviour）——一个 ScriptableObject 资源被所有引用它的对象共享。将玩家进度保存到磁盘 → `save-systems`。不需要成为资产的普通 DTO 可以直接是 `[System.Serializable]` 类。

## 核心工作流程

1. **定义继承自 `ScriptableObject` 的类** 并使用 `[CreateAssetMenu]` 标记它，以便设计师可以从资源菜单创建实例。
2. **在项目窗口中创建一个或多个 `.asset` 实例**；每个实例都是通过 `[SerializeField]` 字段引用的共享、命名的数据片段。
3. **引用，不要复制。** MonoBehaviour 持有对资源的引用；它们都看到相同的数据，因此更改资源会更改所有消费者。
4. **为了解耦**，将信号和共享变量建模为 ScriptableObjects：HUD 读取并由玩家写入的“FloatVariable”；玩家触发而许多系统监听的事件通道。双方都不引用对方。
5. **在 `OnEnable` 中重置运行时变更**，如果资源在运行时被修改，因为在编辑器中在运行时进行的编辑会保留在资源上（这是“我玩后值改变了”的常见原因）。
6. **通过在 Play 模式下检查资产值来验证**，并确认消费者有反应。

## 模式

### 1. 配置/数据资产

```csharp
using UnityEngine;

[CreateAssetMenu(fileName = "WeaponData", menuName = "Game/Weapon Data", order = 0)]
public class WeaponData : ScriptableObject
{
    public string displayName = "Pistol";
    public int    damage = 10;
    public float  fireRate = 0.25f;
    public GameObject projectilePrefab;
}
```

```csharp
public class Weapon : MonoBehaviour
{
    [SerializeField] private WeaponData data;   // 在 Inspector 中分配共享资产
    private void Fire() => Debug.Log($"{data.displayName} for {data.damage}");
}
```

### 2. 共享运行时变量（将生产者与消费者解耦）

```csharp
[CreateAssetMenu(menuName = "Game/Float Variable")]
public class FloatVariable : ScriptableObject
{
    [SerializeField] private float initialValue;
    [System.NonSerialized] public float runtimeValue;   // 不会保存到资产

    private void OnEnable() => runtimeValue = initialValue;  // 每次播放会话时重置
}
// 玩家写入 playerHealth.runtimeValue；HUD 读取它——双方都不引用对方。
```

### 3. 在运行时创建实例（不是磁盘上的资产）

```csharp
// 用于在代码中构建的瞬态 SO 数据（例如生成的配置）。
var temp = ScriptableObject.CreateInstance<WeaponData>();
temp.damage = 25;
// ...使用 temp...  Destroy(temp);   // 清理运行时创建的实例
```

## 陷阱

- **在运行时编辑 SO 会保留在编辑器中**——你在播放期间更改的值在你停止后仍然会保留在资产上。将可变的运行时状态保存在 `OnEnable` 中重置的 `[NonSerialized]` 字段中，否则会给你惊喜。（在 _构建_ 中，资产编辑不会跨启动保留。）
- **禁用域重载会跳过你的 `OnEnable` 重置**——在 **进入播放模式选项** 启用且 **重载域** 关闭（Unity 6.3 LTS 快速迭代设置）的情况下，已加载的 SO 在你按下播放时不会被重新创建，因此 `OnEnable` 从不触发，`runtimeValue` 保留着上一会话的值。从 `ISerializationCallbackReceiver` 或场景加载钩子显式重置，而不是依赖 `OnEnable`。
- **期望每个对象的状态**——每个引用都指向 _同一个_ 资产。如果两个敌人需要不同的当前 HP，将 HP 存储在 MonoBehaviour 上，而不是共享 SO。
- **没有帧生命周期**——ScriptableObjects 有 `OnEnable`/`OnDisable`/`OnDestroy` 但没有 `Update`。不要期望每帧回调。
- **将 SO 用作存档文件**——它们是创作资产，不是运行时持久化；用 `save-systems` 保存进度。
- **泄漏 `CreateInstance` 对象**——运行时创建的实例不会被像普通 C# 对象那样进行垃圾回收；完成时使用 `Destroy` 它们。

## 参考

- 对于 **事件通道** 模式（一个 `GameEvent` SO + 监听器，类型安全的有效载荷）和 **运行时集合/注册表**（共享的活动敌人列表），请阅读 `references/event-channels.md`。
- 主要文档：Unity Manual "ScriptableObject" (`/Manual/class-ScriptableObject.html`) 和 `ScriptReference/ScriptableObject`，`ScriptReference/CreateAssetMenuAttribute`。

## 相关技能

- `unity-csharp-scripting` — 消费这些资产的 MonoBehaviour。
- `save-systems` — 将状态持久化到磁盘（SO 不用于此目的）。
- `card-game` / `rpg` / `survival-crafting` — 依赖 SO 驱动的数据的类型。
