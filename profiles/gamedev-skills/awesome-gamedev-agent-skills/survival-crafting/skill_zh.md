# 生存制造

生存制造游戏的剧本——收集 → 制造 → 建造循环、生存需求、制造/科技进展和基地建造。这是一种**组合**技能：它编排了库存数据、世界内容、持久化和威胁。它不会重新教授那些基本概念；它定义了制造生存紧张而非乏味的循环和压力系统（需求、稀缺性、升级）。

## 使用时机

- 当玩家**收集资源、制造物品/结构、管理生存需求并建造基地以对抗升级的威胁**时使用：生存沙盒、制造/基地建造游戏。
- 在设计需求（饥饿/口渴/温度）、制造科技树、收集循环或基地放置/建造时使用。

**不使用时机**：将制造作为次要的RPG功能 → `rpg`。永久死亡网格地下城 → `roguelike`。对于库存/物品作为数据资产，使用 `godot-resources` / `unity-scriptableobjects`；对于世界生成，使用 `procedural-gen`。

## 核心循环

**收集原始资源 → 制造工具/物品 → 建造和升级基地 → 管理生存需求 → 探索更远以获取更好的资源 → 生存升级的威胁 → 在更高等级重复**。每个循环都应该解锁*下一个*循环（更好的工具 → 到达新的生物群落 → 新的资源 → 更好的制造）。当这个梯子断裂时，游戏变得乏味。

## 必须有的系统

1. **资源节点 + 收集** — 可收获的世界对象；工具要求/等级；重生。
2. **库存** — 堆叠、容量（槽位或重量）、丢弃/转移、快捷栏。
3. **制造** — 配方（输入 → 输出）、制造站/科技门、科技树。
4. **生存需求** — 饥饿、口渴、温度、耐力、健康，伴随衰减+后果。
5. **基地建造** — 可放置的结构、建造网格/吸附、存储、制造站。
6. **世界 + 昼夜** — 生物群落/资源（通常是程序化的）；驱动威胁的时间循环。
7. **威胁** — 敌对生物/天气/事件升级；战斗或躲避。
8. **保存/加载** — 世界状态、库存、基地、需求、进展；大型世界的持久化。

## 设计旋钮

| 旋钮 | 效果 | 备注 |
|------|------|------|
| 需求衰减率 | 压力节奏 | 慢到足以探索，快到足以重要。 |
| 需求失败后果 | 赌注 | 持续伤害，而非瞬间死亡。 |
| 资源稀缺性 / 重生 | 探索推动 | 基地附近稀缺 → 出发寻找更多。 |
| 工具等级 / 门控 | 进展梯子 | 更好的工具 → 新的节点类型。 |
| 配方复杂度 / 科技深度 | 长期目标 | 多步骤链，而非扁平列表。 |
| 库存限制（槽位/重量） | 物流紧张 | 强制基地行程和存储。 |
| 威胁升级曲线 | 随时间增加难度 | 夜晚/季节性/事件坡道。 |
| 昼夜长度 | 节奏 | 白天 = 收集，夜晚 = 防御。 |

## 模式

### 1. 需求衰减带分级后果

```python
# 帧更新/每刻更新的伪代码。dt = 秒。需求下降；失败时流失HP。
def update_needs(p, dt):
    p.hunger = max(0, p.hunger - HUNGER_RATE * dt)
    p.thirst = max(0, p.thirst - THIRST_RATE * dt)
    p.temp   = approach(p.temp, ambient_temperature(p), TEMP_RATE * dt)

    # 后果是分级的，而非二元的：警告，然后损耗 — 永不瞬间死亡。
    if p.hunger == 0 or p.thirst == 0:
        p.hp -= STARVE_DAMAGE * dt          # 持续伤害创造紧迫感，但留有恢复空间
    if p.temp < COLD_THRESHOLD or p.temp > HEAT_THRESHOLD:
        p.hp -= EXPOSURE_DAMAGE * dt
    if p.hunger > 0 and p.thirst > 0 and not exposed(p):
        p.hp = min(p.max_hp, p.hp + REGEN_RATE * dt)   # 安全且吃饱 => 恢复
```

### 2. 制造：验证后原子化消耗输入

```python
# 伪代码。配方是数据：输入 → 输出，可带可选站/科技要求。
recipe = {"id": "stone_axe",
          "inputs": {"wood": 3, "stone": 2}, "output": ("stone_axe", 1),
          "station": "workbench", "requires_tech": "basic_tools"}

def can_craft(recipe, inv, tech, station):
    if recipe.get("requires_tech") and recipe["requires_tech"] not in tech: return False
    if recipe.get("station") and recipe["station"] != station: return False
    return all(inv.count(item) >= n for item, n in recipe["inputs"].items())

def craft(recipe, inv, tech, station):
    if not can_craft(recipe, inv, tech, station): return False
    for item, n in recipe["inputs"].items(): inv.remove(item, n)   # 消耗所有，然后添加
    inv.add(*recipe["output"])                                     # 原子化：不部分制造
    return True
```

### 3. 由工具等级限制的收集

```python
# 伪代码。节点只有在持有的工具满足其所需等级时才产出。
def harvest(node, tool):
    if tool.tier < node.required_tier:
        return notify("需要更好的工具")        # 例如，石质节点需要镐子，而非拳头
    node.hp -= tool.power
    if node.hp <= 0:
        spawn_drops(node.drop_table)               # 加权掉落（见roguelike掉落模式）
        node.start_respawn(node.respawn_time)      # 节点稍后返回；世界不会永远耗尽
```

## 陷阱 / 失败模式

- **瞬间杀死的需求** → 愤怒和存档重置。使失败伤害随时间增加，带清晰的警告和恢复路径（模式1）。
- **没有梯子的乏味** → 收集从未解锁新的收集。每个等级必须打开下一个（更好的工具 → 新的节点 → 新的资源 → 更好的制造）。
- **非原子化制造** → 输入被消耗但输出在边缘情况下未授予。先验证，然后作为一步消耗并添加（模式2）。
- **无限制的库存** → 无物流紧张，且无建造基地/存储的理由。按槽位或重量限制。
- **永久耗尽世界** → 玩家剥光地图并退出。重生节点或随时间再生资源。
- **未按 `dt` 缩放的每帧衰减** → 在不同硬件上需求消耗速度不同。按 `dt` 缩放。
- **无保存 / 大型世界脆弱保存** → 碰撞擦除数小时。逐步持久化世界+基地+需求；版本化（见 `save-systems`）。
- **扁平威胁曲线** → 没有后期压力。通过夜晚/季节/事件等级升级。

## 组合（从这些技能构建）

- **物品/配方作为数据**：`godot-resources` / `unity-scriptableobjects` — 物品、配方、科技树、掉落表。
- **世界**：`procedural-gen` 用于生物群落/资源放置；`level-design` 用于设计区域。
- **持久化**：`save-systems` 用于大型世界状态、基地、库存、需求和版本化。
- **威胁**：`game-ai` 用于生物；引擎物理技能用于近战/碰撞。
- **建造/放置**：`godot-tilemap` / `unity-tilemap-2d`（2D）或 `godot-3d-essentials`（3D）加UI吸附。
- **UI**：`game-ui-ux` 用于库存/制造/HUD布局和缩放；`godot-ui-control` 用于具体的库存、制造菜单、需求HUD和建造模式。

## 参考文献

- 对于完整的需求模型和阈值、制造科技树图、收集/重生调优、基地建造网格和威胁升级，请阅读 `references/needs-and-crafting.md`。
