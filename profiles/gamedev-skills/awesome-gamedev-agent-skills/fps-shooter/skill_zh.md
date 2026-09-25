# 第一人称射击游戏

第一人称射击游戏的开发手册——包括视角/移动控制器、射击模型、武器手感以及战斗系统。这是一种**组合性**技能：它将3D控制器、输入和AI整合到射击游戏中。它不会重新教学3D节点或射线追踪；它定义了射击模型和决定武器手感的调节器（TTK、后坐力、散布）。

## 使用场景

- 在构建以**瞄准和射击**为核心动词的第一人称游戏时使用——竞技场射击游戏、战术FPS、PvE射击游戏、爆炸头射击游戏。
- 在决定命中扫描与抛射物、调整TTK、后坐力、散布或瞄准手感时使用。

**不适用场景：** 第三人称/2D射击 → 在此重用射击模型，但根据相关类型构建摄像机/控制器。塔防生存 → `tower-defense`。对于摄像机/角色身体本身，使用 `godot-3d-essentials` / `unreal-cpp-gameplay`。

## 核心循环

**扫描 → 锁定目标 → 瞄准和开火 → 确认击杀（反馈）→ 重新定位 / 装填 / 前进。** 整个体验依赖于*瞄准和开火*的微循环感觉清晰：响应迅速的视角、清晰的命中反馈，以及瞬间读取的死亡。

## 必须的系统

1. **第一人称控制器** — 移动（WASD/摇杆）+ 鼠标/摇杆视角、重力、跳跃/蹲伏。
2. **摄像机** — 眼睛高度视角、可配置的FOV和灵敏度、后坐力冲击。
3. **射击模型** — 命中扫描射线追踪和/或抛射物生成；单一命中路径用于反馈。
4. **武器 + 弹药** — 伤害、射速、弹匣、装填、切换。
5. **生命值 + 伤害** — HP、命中/爆头倍率、死亡；玩家和敌人共享模型。
6. **敌人AI** — 感知 → 警觉 → 攻击 → 搜索；掩体和反应延迟 (`game-ai`)。
7. **反馈** — 命中标记、命中痕迹/粒子、命中音效、屏幕震动、击杀确认。
8. **目标** — 除了射击之外你做的事情：清除、占领、生存、护送。

## 设计调节器

| 调节器 | 效果 | 合理默认值 |
|------|--------|--------------|
| TTK（时间到击杀） | 杀伤力、宽容度 | 调整伤害 × 射速 × HP（参考资料）。 |
| 命中扫描 vs 抛射物 | 瞄准技能类型 | 命中扫描 = 挥动；抛射物 = 领导/躲避。 |
| 伤害衰减 | 距离限制 | 全程到~20米，~60米后衰减。 |
| 爆头倍率 | 技能奖励 | ~1.5–2.0×。 |
| 后坐力模式 | 可学习的冲击 | 固定模式 > 纯随机。 |
| 散布（开花） | 抑制激光精度 | 第一发准确；射击时逐渐增加。 |
| 射速 / 弹匣 / 装填 | 节奏、停顿时间 | 装填 = 暴露窗口。 |
| 鼠标灵敏度 / FOV | 舒适度、可读性 | 始终提供两者作为选项。 |
| 瞄准辅助（摇杆） | 控制器一致性 | 靠近目标时的磁性/减速。 |

## 模式

### 1. 命中扫描射击（即时射线，主力）

```python
# 伪代码。从摄像机发射；第一个命中根据距离和爆头进行伤害缩放。
direction = apply_spread(camera.forward, current_spread)
hit = raycast(camera.world_position, direction, max_dist=RANGE, mask=SHOOTABLE)
if hit:
    dmg = base_damage * falloff(hit.distance)
    if hit.is_head: dmg *= HEADSHOT_MULT
    hit.actor.take_damage(dmg)
    spawn_impact_fx(hit.point, hit.normal)        # 痕迹 + 声音 + 命中标记
```

### 2. 抛射物射击（可躲避，引导目标）

```python
# 伪代码。生成一个移动体；它在自身碰撞时造成伤害。
p = spawn(projectile_scene, at=muzzle.world_position)
p.velocity = camera.forward * PROJECTILE_SPEED
p.on_hit   = lambda other, point: (other.take_damage(base_damage), explode_fx(point))
p.lifetime = RANGE / PROJECTILE_SPEED             # 生命周期结束，射击不会永久存在
```

### 3. 时间到击杀（将三者一起平衡）

```python
# 伪代码。TTK由HP、单次伤害和射速决定——作为一个系统进行调整。
shots_to_kill = ceil(target_hp / damage_per_shot)
ttk_seconds   = (shots_to_kill - 1) / fire_rate_per_second   # 第一发在t=0时
```

## 陷阱 / 失败模式

- **视角与帧率或未按`dt`缩放** → 灵敏度随FPS变化。视角应由原始鼠标增量驱动；移动积分使用`dt`（见`physics-tuning`）。
- **纯随机后坐力/散布** → 感觉无法控制且不公平。使用可学习后坐力模式；保持第一发准确。
- **命中扫描无衰减** → 手枪可以跨地图狙击。添加基于距离的伤害衰减。
- **无命中反馈** → 玩家无法判断是否命中。始终显示命中标记、命中特效和独特的击杀确认。
- **TTK不匹配** → 太低感觉紧张/不公平；太高感觉像海绵。作为一个系统调整伤害、射速和HP（模式3）。
- **信任多人游戏中的客户端** → 作弊和“我先开枪”的争议。保持服务器端权威；使用延迟补偿（参考资料）并将网络代码委托给引擎多人游戏技能。
- **无FOV / 灵敏度选项** → 运动病和可访问性失败。始终提供它们。

## 组合（从这些技能构建）

- **控制器 + 摄像机：** `godot-3d-essentials`（Godot）或 `unreal-cpp-gameplay` / `unreal-blueprints`；Unity使用 `unity-physics` + 角色控制器。
- **输入：** `input-systems`（或 `unreal-enhanced-input`）用于视角/移动、重新绑定和游戏手柄瞄准辅助。
- **射击物理：** `godot-physics` / `unity-physics` 用于射线追踪和抛射物碰撞。
- **敌人：** `game-ai` 与 `unity-navmesh` / `unreal-behavior-trees` / Godot导航。
- **摄像机 & 感觉：** `camera-systems` 用于FOV/后坐力冲击和视角平滑；`game-feel` 用于命中停止、屏幕震动和命中特效。
- **润色：** `audio-design` 用于武器/命中音效；`shader-programming` 用于枪口/命中VFX。
- **流程：** `prototype-fast` 在构建内容之前验证瞄准手感。

## 参考资料

- 关于命中扫描与抛射物的权衡、伤害衰减、后坐力/散布、TTK数学、命中注册/延迟补偿以及敌人AI状态，请阅读 `references/shooting-and-feel.md`。
