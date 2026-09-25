# Godot C# / .NET (4.x)

使用 C# 编写 Godot 游戏代码：节点子类、引擎生命周期、导出、信号作为事件以及 GDScript 互操作。目标为 **Godot 4.7 (.NET / C#)** 和 **.NET 8**。

## 使用场景

- 当使用 C# (`.cs` + `.csproj`) 脚本编写 Godot 游戏时，将 GDScript 语法翻译为 C#，暴露 `[Export]` 字段，或连接 `[Signal]` 代理和 GetNode<T> 时使用。
**不使用场景：** GDScript 特定语法 → `godot-gdscript`；语言无关的引擎概念（场景、物理、动画）→ 相关的 `godot-*` 技能。需要安装 **Godot .NET 构建** + .NET SDK；标准构建无法运行 C#。

## 核心工作流程

1. **使用 Godot .NET 编辑器构建** 并安装匹配的 .NET 8 SDK。创建第一个 C# 脚本会生成 `.csproj`/`.sln`。使用编辑器或 `dotnet build` 进行构建。
2. **每个节点脚本都是一个 `partial` 类**，扩展 Godot 类型（源生成器依赖于 `partial`）。文件/类名应与节点脚本匹配。
3. **使用 PascalCase 覆盖生命周期方法**，并带有 `double` delta：`_Ready()`、`_Process(double delta)`、`_PhysicsProcess(double delta)`。
4. **使用 `[Export]` 暴露可调参数**；它们在 Inspector 中与 GDScript `@export` 类似。
5. **将信号声明为 `[Signal]` 代理**，命名为 `XxxEventHandler`；使用 `EmitSignal(SignalName.Xxx, ...)` 发射，并使用生成的 C# `event` 订阅。
6. **使用 `GetNode<T>("Path")` (或 `%Unique`) 获取节点**，并在需要时调用 GDScript 的 `Call`/`Get`/`Set`。

## 模式

### 1. 节点脚本：生命周期、[Export]、GetNode<T>

```csharp
using Godot;

public partial class Player : CharacterBody2D
{
    [Export] public float Speed = 200.0f;          // 可在 Inspector 中编辑
    [Export] public float JumpVelocity = -400.0f;

    private const float Gravity = 1200.0f;
    private AnimatedSprite2D _sprite;

    public override void _Ready()
    {
        _sprite = GetNode<AnimatedSprite2D>("AnimatedSprite2D");
    }

    public override void _PhysicsProcess(double delta)
    {
        Vector2 v = Velocity;                       // Velocity 是一个属性
        if (!IsOnFloor())
            v.Y += Gravity * (float)delta;          // delta 是 double；转换为 float 进行计算
        if (Input.IsActionJustPressed("jump") && IsOnFloor())
            v.Y = JumpVelocity;

        float dir = Input.GetAxis("move_left", "move_right");
        v.X = dir != 0 ? dir * Speed : Mathf.MoveToward(v.X, 0, Speed);

        Velocity = v;
        MoveAndSlide();                             // 无参数，类似于 GDScript 4.x
    }
}
```

### 2. 信号作为 C# 事件

```csharp
using Godot;

public partial class Health : Node
{
    // 代理名称必须以 "EventHandler" 结尾；生成器创建事件 + SignalName。
    [Signal] public delegate void HealthChangedEventHandler(int current, int max);

    private int _hp = 100;

    public void TakeDamage(int amount)
    {
        _hp = Mathf.Max(_hp - amount, 0);
        EmitSignal(SignalName.HealthChanged, _hp, 100);   // 类型安全的信号名称
    }

    public override void _Ready()
    {
        HealthChanged += OnHealthChanged;            // 像普通 C# 事件一样订阅
    }

    private void OnHealthChanged(int current, int max) => GD.Print($"HP {current}/{max}");
}
```

### 3. 在 C# 中实例化场景

```csharp
public partial class Spawner : Node2D
{
    // 一次性加载；PackedScene 是预加载结果的 C# 等价物。
    private readonly PackedScene _bullet = GD.Load<PackedScene>("res://bullet.tscn");

    public void Shoot(Vector2 at)
    {
        var b = _bullet.Instantiate<Node2D>();       // 类型化实例化
        b.GlobalPosition = at;
        AddChild(b);
    }
}
```

### 4. 与 GDScript 节点互操作

```csharp
public override void _Ready()
{
    Node gd = GetNode("GDScriptNode");
    // 调用 GDScript 方法并动态读取/写入其属性。
    gd.Call("take_damage", 10);
    int score = (int)gd.Get("score");
    gd.Set("score", score + 5);
    // 通过名称连接到 GDScript 信号：
    gd.Connect("died", Callable.From(OnDied));
}

private void OnDied() => GD.Print("entity died");
```

## 陷阱

- **忘记 `partial`。** 没有 `partial`，Godot 源生成器无法扩展类，并且 `[Export]`/`[Signal]` 会因令人困惑的构建错误而失效。
- **方法名称/签名错误。** C# 重写是 `_Ready`、`_Process(double)`、`_PhysicsProcess(double)` — PascalCase 和 `double` delta (GDScript 使用 snake_case 和 `float`)。不匹配的名称将不会被调用。
- **`[Signal]` 代理命名。** 它必须以 `EventHandler` 结尾；引擎将信号暴露为不带该后缀的名称，并生成 `SignalName.X` 和一个 C# `event`。
- **`GD.Print` vs `Console.WriteLine`。** 使用 `GD.Print`/`GD.PrintErr` 来输出到 Godot 输出面板；`Console` 输出可能不会显示。
- **值类型结构体。** `Vector2`、`Color`、`Transform2D` 是结构体 — 修改局部副本 (`var v = Velocity; v.X = ...; Velocity = v;`)；直接编辑 `Velocity.X` 无法编译/持久化。
- **需要 .NET 构建 + SDK。** 非 .NET 编辑器无法运行 C#；不匹配/缺失的 .NET SDK 会导致构建失败。Godot 4.7 目标为 .NET 8；检查当前平台的导出说明，因为 Android 和其他 AOT 目标可能需要更新的 SDK 工具。
- **`QueueFree()` vs `Free()`** — 与 GDScript 规则相同；优先使用 `QueueFree()`。释放后的对象如果在释放后使用会抛出 `ObjectDisposedException`。
- **.NET 的导出在某些平台上有所不同** (例如，Web/移动需要额外步骤)；检查目标平台的 .NET 导出说明。

## 参考

- 关于导出属性变体 (`[ExportGroup]`、范围、类型化数组)，`await ToSignal(...)`、`Godot.Collections` 与 System 集合、C# 中的自定义资源以及项目/构建设置，请阅读 `references/csharp-setup-and-interop.md`。

## 相关技能

- `godot-gdscript` — 这些模式的 GDScript 等价物。
- `godot-signals-groups` — 信号/事件架构（语言无关）。
- `godot-resources` — 数据资源；C# `[Export]` + `Resource` 模式。
- `unity-csharp-scripting` — 来自 Unity 的 C#，适用于从那里迁移的开发者。
