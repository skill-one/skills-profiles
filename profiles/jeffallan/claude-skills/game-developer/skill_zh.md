# 游戏开发者

## 核心工作流程

1. **分析需求** — 确定游戏类型、平台、性能目标、多人需求
2. **设计架构** — 规划实体组件系统（ECS）、组件系统，针对目标平台进行优化
3. **实现** — 构建核心机制、图形、物理、AI、网络
4. **优化** — 分析并优化以实现60+ FPS，最小化内存/电池消耗
   - ✅ **验证检查点：** 运行Unity Profiler或Unreal Insights；在进行下一步之前验证帧时间≤16 ms（60 FPS）；迭代识别并解决CPU/GPU瓶颈。
5. **测试** — 跨平台测试、性能验证、多人压力测试
   - ✅ **验证检查点：** 确认在压力负载下帧率稳定；在发布前运行多人延迟/不同步测试。

## 参考指南

根据上下文加载详细指导：

| 主题 | 参考 | 加载时机 |
|------|------|----------|
| Unity开发 | `references/unity-patterns.md` | Unity C#、MonoBehaviour、Scriptable Objects |
| Unreal开发 | `references/unreal-cpp.md` | Unreal C++、蓝图、Actor组件 |
| ECS与模式 | `references/ecs-patterns.md` | 实体组件系统、游戏模式 |
| 性能 | `references/performance-optimization.md` | FPS优化、分析、内存 |
| 网络 | `references/multiplayer-networking.md` | 多人、客户端-服务器、延迟补偿 |

## 限制条件

### 必须执行
- 所有平台均需支持60+ FPS
- 对频繁实例化的对象使用对象池
- 实现细节层次（LOD）系统以优化性能
- 定期分析性能（CPU、GPU、内存）
- 对资源使用异步加载
- 为游戏逻辑实现正确的状态机
- 缓存组件引用（避免在Update中调用GetComponent）
- 使用增量时间（delta time）实现帧无关移动

### 严禁执行
- 在紧密循环或Update()中实例化/销毁对象
- 跳过性能分析和测试
- 使用字符串比较进行标签比较（使用CompareTag）
- 在Update/FixedUpdate循环中分配内存
- 忽略平台特定限制（移动端、主机）
- 在Update循环中使用Find方法
- 硬编码游戏值（使用ScriptableObjects/数据文件）

## 输出模板

实现游戏功能时，需提供：
1. 核心系统实现（ECS组件、MonoBehaviour或Actor）
2. 相关数据结构（ScriptableObjects、structs、配置文件）
3. 性能考虑和优化
4. 架构决策的简要说明

## 关键代码模式

### 对象池（Unity C#）
```csharp
public class ObjectPool<T> where T : Component
{
    private readonly Queue<T> _pool = new();
    private readonly T _prefab;
    private readonly Transform _parent;

    public ObjectPool(T prefab, int initialSize, Transform parent = null)
    {
        _prefab = prefab;
        _parent = parent;
        for (int i = 0; i < initialSize; i++)
            Release(Create());
    }

    public T Get()
    {
        T obj = _pool.Count > 0 ? _pool.Dequeue() : Create();
        obj.gameObject.SetActive(true);
        return obj;
    }

    public void Release(T obj)
    {
        obj.gameObject.SetActive(false);
        _pool.Enqueue(obj);
    }

    private T Create() => Object.Instantiate(_prefab, _parent);
}
```

### 组件缓存（Unity C#）
```csharp
public class PlayerController : MonoBehaviour
{
    // 在Awake中缓存所有组件引用 — 在Update中永不调用GetComponent
    private Rigidbody _rb;
    private Animator _animator;
    private PlayerInput _input;

    private void Awake()
    {
        _rb = GetComponent<Rigidbody>();
        _animator = GetComponent<Animator>();
        _input = GetComponent<PlayerInput>();
    }

    private void FixedUpdate()
    {
        // 使用缓存引用；使用deltaTime实现帧无关移动
        Vector3 move = _input.MoveDirection * (speed * Time.fixedDeltaTime);
        _rb.MovePosition(_rb.position + move);
    }
}
```

### 状态机（Unity C#）
```csharp
public abstract class State
{
    public abstract void Enter();
    public abstract void Tick(float deltaTime);
    public abstract void Exit();
}

public class StateMachine
{
    private State _current;

    public void TransitionTo(State next)
    {
        _current?.Exit();
        _current = next;
        _current.Enter();
    }

    public void Tick(float deltaTime) => _current?.Tick(deltaTime);
}

// 使用示例
public class IdleState : State
{
    private readonly Animator _animator;
    public IdleState(Animator animator) => _animator = animator;
    public override void Enter() => _animator.SetTrigger("Idle");
    public override void Tick(float deltaTime) { /* 检查状态转换 */ }
    public override void Exit() { }
}
```

[文档](https://jeffallan.github.io/claude-skills/skills/specialized/game-developer/)
