# 卡牌游戏

一份卡牌游戏的开发指南——包含卡牌数据、牌库/手牌/弃牌区、回合结构以及卡牌效果的解析方式。这是一种**组合式**技能：它将卡牌建模为数据，并将其与 UI 连接起来。它不会重新教学数据资源或 UI 节点；它定义了区域模型、抽牌机制以及保持卡牌游戏正确且无 Bug 的效果解析规则。

## 使用场景

- 在构建任何核心对象为卡牌在区域间移动的游戏时使用（牌库 → 手牌 → 播放 → 弃牌）：卡组构筑游戏、TCG/CCG、单人纸牌游戏、roguelike 卡组构筑游戏。
- 在设计抽牌/洗牌/重置洗牌、回合结构、卡牌费用或效果解析方式时使用。

**不适用场景：** 棋盘/瓦片状态与匹配规则 → `puzzle`。带有附带卡牌战斗的 RPG → 从 `rpg` 开始。定义卡牌为资源时，使用 `godot-resources` / `unity-scriptableobjects`；对于手牌/拖拽 UI，使用 `godot-ui-control`。

## 核心循环

**抽牌到手牌 → 消耗资源播放卡牌 → 效果解析并改变棋盘 → 结束回合（清理/弃牌）→ 对手/下一阶段 → 重复直到达成胜利条件。** 深度来自于手牌允许的*组合*；引擎的工作是明确地解析这些组合。

## 必须的系统

1. **卡牌数据** — ID、名称、费用、类型、文本以及效果规范（数据，非代码）。
2. **区域** — 牌库（抽牌堆）、手牌、播放/棋盘、弃牌、除外/移除；卡牌正好存在于其中一个区域。
3. **抽牌 + 洗牌 + 重置洗牌** — 从牌库抽牌到手牌；当弃牌堆为空时，将弃牌重置为牌库。
4. **回合结构** — 阶段（解封/抽牌/主战/战斗/结束）作为状态机。
5. **资源系统** — 法力/能量/行动，限制每回合能做的事情。
6. **效果解析** — 按照定义的顺序应用卡牌效果；处理目标和触发器。
7. **胜利/失败条件** — 生命值、牌库耗尽、目标。
8. **UI** — 手牌布局、拖拽/放置或点击播放、区域计数、目标提示。

## 设计调节器

| 调节器 | 效果 | 备注 |
|------|--------|-------|
| 初始手牌 / 每回合抽牌数 | 节奏、一致性 | 更多抽牌 = 更低变数。 |
| 手牌大小限制 | 储蓄与使用 | 回合结束时弃牌至限制。 |
| 牌库大小（最小） | 一致性 | 更小 = 更可靠的组合。 |
| 资源曲线 | 可玩性 | "法力曲线" 控制力量节奏。 |
| 卡牌稀有度 / 力量预算 | 平衡 | 更强的卡牌费用更高 / 更稀有。 |
| 确定性 vs. 随机性 | 技能 vs. 摇摆 | 洗牌 + 随机效果增加变数。 |
| 重置洗牌规则 | 牌库耗尽、疲劳 | 重置弃牌堆，或惩罚空牌库。 |
| 移除 / 解除 | 对抗 | 每个威胁都需要一个答案。 |

## 模式

### 1. 区域 + 自动重置洗牌的抽牌

```python
# 伪代码。卡牌在任何时刻正好存在于一个区域；移动 = 在此移除，添加到那里。
def draw(n):
    for _ in range(n):
        if not deck:
            if not discard:          # 真正为空：牌库耗尽（失败，或疲劳）
                on_deck_out(); return
            deck.extend(discard)     # 将弃牌重置为牌库
            discard.clear()
            shuffle(deck, rng)       # 使用一个种子 RNG（见存档系统以支持回放）
        hand.append(deck.pop())
```

### 2. 卡牌为数据 + 效果解析

```python
# 伪代码。效果是一个由引擎解释的数据列表——每个卡牌不是定制代码。
card = {
    "id": "fireball", "cost": 3, "type": "法术",
    "effects": [ {"op": "damage", "amount": 6, "target": "chosen_enemy"} ],
}
def play(card, caster):
    if resources[caster] < card.cost: return False     # 无法负担
    resources[caster] -= card.cost
    move(card, from_zone=hand, to_zone=play_or_discard(card))
    for fx in card.effects:
        resolve_effect(fx, caster)                      # 一个解释器处理每张卡牌
    return True
```

### 3. 回合结构作为阶段机

```python
# 伪代码。固定阶段保持时间窗口（触发器、优先级）明确。
PHASES = ["untap", "draw", "main", "combat", "end"]
def take_turn(player):
    for phase in PHASES:
        enter_phase(player, phase)        # 在这里触发 "on_phase" 触发器
        if phase == "draw":   draw(1)
        if phase == "main":   await player_plays_cards()
        if phase == "combat": resolve_combat()
        if phase == "end":    discard_to_hand_limit(player); clear_temporary_effects()
```

## 陷阱 / 失败模式

- **卡牌同时存在于两个区域** → 复制/丢失 Bug。强制 "正好一个区域"；移动 = 移除后添加，并断言卡牌不会重复出现。
- **忘记重置洗牌** → 抽牌失败或空牌库崩溃。重置弃牌堆，或明确定义牌库耗尽/疲劳（模式 1）。
- **每个卡牌一个函数** → 难以维护和测试。使效果为**数据**，由少量操作解释（模式 2）。
- **效果顺序不明确 / 同时触发** → 非确定性结果。按定义的顺序解析（队列或栈）；记录 LIFO vs. FIFO（参考资料）。
- **未种子的洗牌在需要回放/撤销的游戏中** → 无法重现。使用种子 RNG。
- **无手牌限制 / 无解除** → 退化储蓄或无法击败的威胁。添加手牌上限，并确保每个威胁原型都有解除手段。
- **目标状态泄漏** → 取消播放时目标在中间。使播放原子化：先验证费用 + 目标，然后提交。

## 组合（从这些技能构建）

- **卡牌内容：** `godot-resources` / `unity-scriptableobjects` — 将每张卡牌定义为一个数据资源。
- **UI：** `game-ui-ux` 用于布局、缩放和焦点导航；`godot-ui-control` 用于手牌布局、拖拽/放置、区域计数和目标提示。
- **存档/回放：** `save-systems` 用于收集、运行状态（roguelike 卡组构筑游戏）和种子回放。
- **对手 AI：** `game-ai` 用于评估可玩卡牌并选择目标的 AI。
- **动画/反馈：** 引擎动画技能用于卡牌移动；`audio-design` 用于提示音。
- **脚本：** `godot-gdscript` / `unity-csharp-scripting` 用于效果解释器。

## 参考资料

- 对于效果队列/栈、关键词/触发器、目标、卡组构筑与构筑类型以及洗牌公平性，请阅读 `references/effect-resolution.md`。
