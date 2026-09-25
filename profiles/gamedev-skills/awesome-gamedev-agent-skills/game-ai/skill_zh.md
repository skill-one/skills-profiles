# 游戏AI：决策、转向和寻路

从三个可分离的层构建可信的NPC行为：**决策**（做什么）、**转向**（如何移动）、**寻路**（如何在地图上路线规划）。保持它们解耦——行为树选择目标，寻路器生成路径点，转向器跟随它们。这项技能教授与引擎无关的算法；通过以下相关技能将其绑定到您的引擎。

## 使用场景

- 实现敌人/NPC逻辑时使用：巡逻、追击/逃跑、警戒状态、群体移动或“找到通往玩家的路径”。
- 用于在**有限状态机**（少量清晰状态）、**行为树**（大量带优先级的反应行为）或**转向**（平滑局部移动）之间进行选择。
- 集成寻路时使用：网格/图上的A*，或驱动引擎导航网格代理。

**不使用场景**：对于引擎的具体导航网格/代理API和预编译，使用`unity-navmesh`、`unreal-behavior-trees`或Godot的`NavigationAgent2D/3D`（参见该引擎技能）。对于移动/碰撞感觉，使用`physics-tuning`。对于沿线路生成波次，请参阅`tower-defense`类型技能。

## 核心工作流程

1. **根据复杂度选择决策模型**。2-5个状态带明显转换→有限状态机。许多行为、优先级、中断、重用→行为树。连续的“我每个选项有多强”→效用评分。
2. **将决策与运动分离**。决策层输出一个*意图*（目标位置、动作）。转向或寻路将意图转换为运动。
3. **在正确的图上寻路**。网格瓦片、路径点图或预编译的导航网格。节点越少 = A*越快。优先选择引擎的导航网格用于3D；网格上的A*用于瓦片游戏。
4. **沿路径转向，而不是直接朝目标**——跟随下一个路径点，靠近时前进，以便代理拐角。
5. **谨慎地重新计算路径**。定时器上或目标移动一个瓦片时寻路，而不是每帧。缓存路径；仅路径点索引前进。
6. **通过观察验证**。观察代理：它是否到达目标、在角落卡住、在状态间振荡？在调试时在屏幕上绘制路径和当前状态。

## 模式

### 1. 有限状态机（一个状态对象，显式转换）

```gdscript
# 每个状态是一个带有 enter/update/exit的小对象。机器拥有"current"。
class_name State
func enter(agent): pass
func update(agent, dt) -> State: return null   # 返回新状态以转换
func exit(agent): pass

# --- 追击状态：玩家逃离视野范围时返回巡逻 ---
class Chase extends State:
    func update(agent, dt) -> State:
        if not agent.can_see(agent.target):
            return Patrol.new()                 # 通过返回下一个状态进行转换
        agent.move_toward(agent.target.position, dt)
        return null                             # null = 保持在此状态

# --- 驱动：每帧调用一次 ---
func tick(dt):
    var next = current.update(self, dt)
    if next != null:
        current.exit(self); next.enter(self); current = next
```

将转换逻辑*保持在*状态内部（或在表中），永远不要将其作为不断增长的`if`标志堆。一个状态拥有一个行为；这就是保持有限状态机可读的原因。

### 2. 行为树tick（复合节点返回状态）

```gdscript
# 节点的tick()返回SUCCESS、FAILURE或RUNNING（本帧仍在处理）。
enum Status { SUCCESS, FAILURE, RUNNING }

# Sequence：按顺序运行子节点；在第一个非SUCCESS时停止（逻辑AND）。
func sequence_tick(children, agent, dt) -> int:
    for child in children:
        var s = child.tick(agent, dt)
        if s != Status.SUCCESS:
            return s                 # FAILURE或RUNNING会短路序列
    return Status.SUCCESS

# Selector：尝试子节点直到一个成功或正在运行（逻辑OR/备用）。
func selector_tick(children, agent, dt) -> int:
    for child in children:
        var s = child.tick(agent, dt)
        if s != Status.FAILURE:
            return s                 # SUCCESS或RUNNING停止搜索
    return Status.FAILURE
```

一个守卫AI自上而下读取：`Selector[ Sequence[CanSeePlayer?, Chase], Patrol ]`——如果可见则追击，否则巡逻。参见`references/behavior-trees.md`了解叶节点、装饰器（Inverter、Cooldown）和黑板。

### 3. 转向：寻求和到达（平滑、帧率无关）

```gdscript
# Seek：全速加速朝目标。转向 = 想要的 - 当前。
func seek(pos, vel, target, max_speed, max_force) -> Vector2:
    var desired = (target - pos).normalized() * max_speed
    return (desired - vel).limit_length(max_force)   # 一个力，不是传送

# Arrive：像seek一样，但在slow_radius内减速，使其平稳停止。
func arrive(pos, vel, target, max_speed, max_force, slow_radius) -> Vector2:
    var offset = target - pos
    var dist = offset.length()
    if dist < 0.001: return -vel                      # 已经到达：消除漂移
    var ramped = max_speed * min(dist / slow_radius, 1.0)
    var desired = offset / dist * ramped
    return (desired - vel).limit_length(max_force)

# 每帧：vel += 转向 * dt; pos += vel * dt   （始终按dt缩放）
```

### 4. A*启发式函数不能高估（否则路径将不再是最近的）

```python
# 将启发式函数与移动匹配。一个可接受的启发式函数（永远不会大于真实剩余成本）
保持A*最优。
def heuristic(a, b):
    dx, dy = abs(a.x - b.x), abs(a.y - b.y)
    # return dx + dy             # 曼哈顿：4方向网格（无对角线）
    return (dx + dy) + (1.414 - 2) * min(dx, dy)   # 八分：8方向网格
# f(n) = g(n) + h(n)：g = 从起点成本，h = 到目标的启发式。
# 高估h更快，但不再保证最短路径。
```

完整的A*循环（优先队列、`came_from`重建、网格+路径点图）在`references/pathfinding.md`中。

## 陷阱

- **每帧寻路**会拖垮帧率。定时器上或仅在目标移动到新瓦片时重新计算；在之间跟随缓存的路径点。
- **直接转向目标**而不是下一个路径点会使代理紧贴墙壁和角落。跟随路径；在半径内时前进路径点。
- **不可接受的A\*启发式**（例如，欧几里得距离缩放，或对角线网格上的曼哈顿）返回快速但*非最短*的路径。选择与您的允许移动匹配的启发式。
- **行为树叶节点永远不会返回RUNNING**用于多帧动作（行走、播放动画）会导致树每帧重启该动作。返回RUNNING直到动作完成。
- **有限状态机转换意大利面条**：到处散布`if state == ...`检查会重创有限状态机旨在防止的混乱。将转换保持在状态中。
- **没有视线或卡住检查**→ 代理永远撞墙。添加一个超时强制重新路径或状态转换。

## 参考文献

- `references/pathfinding.md` — 完整A*（优先队列、重建）、网格与路径点图、何时委托给引擎导航网格。
- `references/behavior-trees.md` — 节点分类、叶/装饰器实现、黑板，以及FSM与BT的选择。

## 相关技能

- `unity-navmesh`, `unreal-behavior-trees` — 具体的引擎AI/导航API。
- `physics-tuning` — 移动、碰撞响应和代理半径。
- `procedural-gen` — 生成代理导航的图/关卡。
- `tower-defense`, `fps-shooter` — 组合这项技能的类型。
