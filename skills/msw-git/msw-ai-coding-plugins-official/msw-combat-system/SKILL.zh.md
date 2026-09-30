---
name: msw-combat-system
description: MSW战斗系统集成指南。涵盖攻击→命中流程、伤害模型、i帧、击退、命中停止、相机抖动、精灵闪烁、音效、死亡/复活、伤害皮肤、命中效果、角色战斗动作、自定义事件以及AI有限状态机——所有功能均基于MSW原生API，适用于2D多类型游戏。关键词：攻击、命中、伤害、战斗、怪物、命中效果、暴击、投射物、伤害皮肤、击退、命中停止、连击、血条、碰撞、接触命中、TriggerComponent。
---

# msw-combat-system

完整的MSW战斗流程。仅涵盖具有**MSW原生API支持**的通用2D战斗层中的项目，无论其类型如何。不包括公式/理论。API签名基于`Environment/NativeScripts/**/*.d.mlua`。

---

## 0. 覆盖矩阵

| # | 层级 | 原生 | 需要自定义 |
|---|-------|--------|-----------------|
| 1 | 攻击判定 | `AttackComponent` + `HitComponent` (方框/圆形/多边形) | 圆柱/锥形/射线, 穿刺次数 |
| 2 | 伤害模型 | `CalcDamage`/`CalcCritical`/`GetCriticalDamageRate`/`GetDisplayHitCount` 钩子 + `HitEvent.Extra:any` | 元素亲和力, 复合公式 |
| 3 | 击中反应 | 每个身体击退API, 基于`IsHitTarget`的i-frame | 摇晃等级, 状态效果 |
| 4 | 游戏感觉 | **所有6个原生** (击停, 摇晃, 缩放, 闪光, VFX, SFX) | — |
| 5 | 战斗状态 | `StateComponent` + `DeadEvent`/`ReviveEvent`, `PlayerComponent` HP/复活 | MP/耐力/狂怒, 仇恨 |
| 6 | 事件总线 | `HitEvent`/`AttackEvent`/`StateChangeEvent`/`PlayerActionEvent` + 自定义 `@Event` | OnKill/OnBlocked |
| 7 | AI | `StateComponent` (FSM) + `AIComponent` (BT, 4个原生组合 + 自定义 `extends CompositeNode`) + `AIChaseComponent`/`AIWanderComponent`, `_UserService.UserEntities` | 装饰器/记忆(黑板), 威胁表 |
| + | 伤害皮肤 | 3个 `DamageSkin*` 组件 + `DamageSkinService` | — |
| + | 击中效果 | `HitEffectSpawnerComponent` (自动) | — |
| + | 角色动作 | `AvatarStateAnimationComponent` (状态→MapleAvatarBodyActionState) | — |

---

## 0.5 参考资料 — 去哪里查找

这个SKILL.md仅涵盖**系统流程和原生API表面**。实际的模型JSON、完整脚本代码和变化模式在下面的参考资料/*文件中——直接阅读它们。

| 文件 | 范围 | 何时阅读 |
|------|-------|--------------|
| [`../msw-general/references/monster.md`](../msw-general/references/monster.md) | 怪物 `.model` 组件组装 + ActionSheet + AI选择 + 典型模式A脚本 (Soldier风格) + HP/重生 + 生成 + 验证 | 在构建具有战斗能力的怪物时 |
| [`references/hp-gauge.md`](references/hp-gauge.md) | 基于 `PixelRendererComponent` 的顶部HP条完整实现 | 在附加顶部HP条时 |
| [`references/projectile.md`](references/projectile.md) | 投射物 (无身体实体 + `OnUpdate Translate`) + 自导/穿刺/范围变体 | 在构建弓箭、子弹、魔法弹等远程攻击时 |
| [`references/ai-bt.md`](references/ai-bt.md) | 行为树 — `AIComponent` + 组合 (4个原生 + 自定义) + `@BTNode` + 自定义装饰器/记忆/威胁 | 当您需要基于BT的怪物/Boss AI和多层级决策时 |

> 优先级：**这个SKILL.md (概念 + API表格) → 相关的参考资料/* (完整实现)**。

---

## 1. 攻击判定

### 1-1. 形状 & 攻击触发

`HitComponent.ColliderType` 仅支持 **方框 / 圆形 / 多边形**。其他形状必须通过组合来近似。

```
AttackComponent:
  Attack(Vector2 size, Vector2 offset, string attackInfo, CollisionGroup? cg)    → table<Component>
  Attack(Shape shape, string attackInfo, CollisionGroup? cg)                     → table<Component>
  AttackFast(Shape shape, string attackInfo, CollisionGroup? cg)                 → void   (用于大量判定, 弹幕射击)
  AttackFrom(Vector2 size, Vector2 position, string attackInfo, CollisionGroup? cg) → table<Component>
  emitter EmitAttackEvent(AttackEvent)
```

- 形状：`CircleShape(position, radius)` / `BoxShape(position, size, angle)` / `PolygonShape(position, points, angle)`。对于轴对齐的矩形，使用 `BoxShape(center, size, 0)` —— 没有矩形形状类型。当不需要旋转时，将 `angle = 0` 传递给 `BoxShape` / `PolygonShape`。
- 多边形击中表面：`HitComponent.PolygonPoints: SyncList<Vector2>`
- `AttackFast` 不构建击中表 → 对于弹幕射击/大量判定具有更好的性能

### 1-2. 目标过滤器

| 侧 | 重写 | 目的 |
|------|----------|---------|
| 攻击者 | `AttackComponent:IsAttackTarget(defender, attackInfo) → boolean` | 派系 / 距离 / 状态 |
| 防御者 | `HitComponent:IsHitTarget(attackInfo) → boolean` | 无敌 / 免疫 |

如果任一返回false → 击中将被排除。超调用是 **`__base:IsAttackTarget(...)`** (mlua特定)。

> ⚠ **不要在重写时添加 `@ExecSpace`** — 两者 `IsAttackTarget` 和 `IsHitTarget` 在父类上都有未指定的 ExecSpace (=All)。在子类中添加类似 `@ExecSpace("ServerOnly")` 的注解会在运行时触发 **LEA-3014 `SignatureMismatch`**。即使没有注解，调用路径也会通过服务器端击中流程，因此实际执行发生在服务器上。详情：[`msw-scripting/SKILL.md` §9 "方法重写"](../msw-scripting/SKILL.md)。

- `Attack*(..., cg)` 的 `cg` 参数是**对防御者 `HitComponent.CollisionGroup` 的精确匹配过滤器** (默认为 `CollisionGroups.HitBox`)。它不会咨询碰撞矩阵，攻击者自己的组无关紧要。`nil` (省略) = 每个 `HitComponent` 都是候选者。一个**与防御者实际组不同的有效组**会击中 **0个目标且无错误** (静默)；一个不存在的组引用会像 `nil` (所有组) 一样行为。当传递一个组 (例如 `CollisionGroups.Monster`) 时，首先将目标怪物的 `HitComponent.CollisionGroup` 设置为相同的组——示例工作区怪物将其覆盖为 `Monster`，这就是为什么示例攻击脚本可以工作。从另一个世界导入的模型，其组ID在本世界的碰撞组集中缺失，会静默注册在 `Default` 组下——用 `nil` 或 `CollisionGroups.Default` 访问它。
- **防止重复击中 / 穿刺 / 最大击中次数**：不是原生的。在脚本中通过 `Attack` 返回的表 + `table<Entity, boolean>` 缓存进行管理。

### 1-3. `attackInfo` 标签

一个字符串扩展点，它传播到 `CalcDamage`/`IsHitTarget`/`GetDisplayHitCount`。值约定由项目决定。建议使用命名空间风格，例如 `"melee.light"`，`"dot.poison"`。

### 1-4. ⚠️ IsLegacy

`ColliderType`/`ColliderOffset`/`PolygonPoints` 仅在 `HitComponent.IsLegacy = false` 时有效。`BoxOffset`/`ColliderName` 已弃用。

### 1-5. 每个攻击形式的形状映射

| 形式 | 形状构造 |
|------|--------------------|
| 正面近战方框 | `BoxShape(pos + LookDirectionX*offset, size, 0)` — 参见 DefaultPlayer `PlayerAttack` |
| 圆形范围效果 | `CircleShape(self.WorldPos, radius)` |
| 投射物 | 生成一个**无身体模型** (仅Sprite+Transform) + 在 `OnUpdate(delta)` 中调用 `TransformComponent:Translate(speed*delta, 0)` + 基于距离的击中检查 + `_EntityService:Destroy`。移动规则在 §1-6，**完整实现 → [`references/projectile.md`](references/projectile.md)** |

**没有MSW特定的投射物系统**——实现为实体 + `AttackComponent` 组合。

### 1-6. 连续移动 — 投射物、怪物和AI的通用规则

连续移动（追击、飞行、自动移动）是**基于每帧 `OnUpdate(delta)`**。通过计时器（`SetTimerRepeat(0.1~0.15s)`) 移动会产生 6~10Hz 的传送，看起来很卡顿。

#### 每个目标推荐的API

| 目标 | 有身体? | 移动API | 理由 |
|--------|:-----:|--------------|-----------|
| **怪物 / NPC / AI** | **是** (地图类型身体 + `MovementComponent`) | `MovementComponent:MoveToDirection(dir, 0)` + `MovementComponent.InputSpeed` | `MovementComponent.d.mlua:1` — 控制所有三个 Rigid/Kinematic/Sideview。`InputSpeed` 属于 MovementComponent (`.d.mlua:7`)，所以它**不是 Player-only**。第二个参数 `0` — deltaTime 仅在梯子上应用 (`.d.mlua:32`)。官方BT示例 `ActionFollow`/`ActionMoveRandom` 也使用 `0`。 |
| **投射物 / 宝石 / 掉落物品 / 效果** | **否** (Sprite+Transform+Trigger) | 每帧 `self.Entity.TransformComponent:Translate(speed*delta, 0)` | 直接Transform操作在没有身体的情况下是安全的。官方“创建长程投射物”教程中的模式。 |
| **直接Rigidbody控制** (高级) | 是 | `body:AddForce(...)` — 持续加速度 / 冲量 | `RigidbodyComponent.d.mlua:71` — `MoveVelocity` 主要由 `MovementComponent` 控制，因此最好通过 `MovementComponent` 而不是直接编写它。 |

> 关于 `MovementComponent.InputSpeed` 每种地图类型的实际速度转换，请参阅 [`msw-general/references/platform.md` §10](../msw-general/references/platform.md) (MapleTile=×1, RectTile=÷1.2, SideView=×1.5)。

#### 禁止的模式

| ❌ | 原因 |
|---|--------|
| `_TimerService:SetTimerRepeat(move, 0.1~0.15)` 用于移动 | 6~10Hz 传送，没有帧插值 → 卡顿 |
| `body:SetPosition(...)` / `MovementComponent:SetPosition(...)` 在 `OnUpdate` 内 | **两者都是传送方法** (`MovementComponent.d.mlua:37`，每个身体的 `.d.mlua` 上的 `SetPosition`)。用于连续移动是卡顿的。仅用于一次性生成/重生/锁定。 |
| `self.Entity.TransformComponent.Position = newPos` (有活跃身体的实体) | 物理引擎在下一帧会覆盖它，网络同步被阻塞。 |
| 没有delta的常量步长移动，例如 `Translate(0.009, 0)` | 依赖于帧率。速度在60FPS和30FPS之间不同。 |

#### ⚠ 小心官方 msw-search 反模式

`mlua_Document_Retriever` 返回一个高分的 "**使用 MovementComponent 控制实体移动**" 文档，但正文是一个**反模式**，在 `OnUpdate` 中每帧使用 `MovementComponent:SetPosition(...)` 移动——**忽略该文档**并使用上面表格中的 `MoveToDirection` / `Translate`。`FlappyFish Remake`，`Stopping the Taxi`，和 `Making a Moving Foothold` 也显示了缺失delta或直接 `Position` 赋值，因此参考它们时要小心。

#### 移动组件附加 — 怪物 / NPC

**默认情况下不包含在怪物模型中。** `.model` 必须包含以下所有组件。

| 组件 | 备注 |
|-----------|-------|
| `MOD.Core.TransformComponent` | 默认 |
| `MOD.Core.SpriteRendererComponent` | 渲染器 |
| 身体 (地图类型) | `RigidbodyComponent`(MapleTile) / `KinematicbodyComponent`(RectTile) / `SideviewbodyComponent`(SideViewRectTile) |
| `MOD.Core.MovementComponent` | 例如 `InputSpeed = 2.0` — 必须用于移动API |

#### 跨参考

- **击退 (一次性冲量)** 不是连续移动，因此直接使用 §3-1。
- 每种地图类型的身体选择 / InputSpeed 转换：[`msw-general/references/platform.md` §4·§10](../msw-general/references/platform.md)

---

## 1-7. 基于碰撞的击中 — 选择检测方法 (不要手动计算距离)

当请求是“基于碰撞/接触的击中”（玩家↔怪物触碰伤害、危险区域、陷阱、重叠）时，根据意图选择。**每帧距离计算不是默认的**——当设计要求使用碰撞器接触时，最常见的是请求者↔实现者不匹配。

| 意图 | 检测 | 原因 |
|--------|-----------|-----|
| 主动攻击挥击 / 击中框 / 投射物爆发 | `AttackComponent:Attack`/`AttackFast`/`AttackFrom` → 解决防御者 `HitComponent`，发出 `HitEvent` | 完整流程：伤害皮肤，击中效果，`IsHitTarget` i-frame，`OnHit` |
| 身体到身体的接触 / 区域 / 陷阱重叠，目标任意或许多 | `TriggerComponent` + `OnEnterTriggerBody`/`OnStayTriggerBody`/`OnLeaveTriggerBody` (或 `TriggerEnter/Stay/LeaveEvent`) + `CollisionGroup` 过滤器，然后通过 `HitEvent` 流程路由伤害 | 引擎端重叠：尊重真实的碰撞器形状 (Box/Circle/Polygon)，`ColliderOffset` 和组过滤 |
| 自导 / 已知单个目标 | 每帧 `OnUpdate` 距离检查 ([`references/projectile.md`](references/projectile.md)) | 仅当事先知道确切一个目标实体时才合理 |

- ❌ 每帧 `math.sqrt(dx*dx+dy*dy) < r` 用于玩家↔怪物或多目标碰撞：它静默地近似以Transform为中心的一个圆（忽略每个碰撞器的形状 / 大小 / `ColliderOffset`），跳过 `CollisionGroup` 过滤，并且每帧成本为 O(攻击者 × 目标)。“基于碰撞的击中”意味着原生碰撞器，而不是距离轮询。
- `CollisionGroup` 默认为 `CollisionGroups.TriggerBox`。`OnStayTriggerBody` 在重叠时**每帧**都会触发——用冷却门控伤害，不要每刻应用。
- 检测 ≠ 伤害应用：原生重叠触发后，仍然通过 `HitEvent` / `AttackComponent` 造成伤害——**永远不要直接减去HP**。

---

## 2. 伤害模型

```
AttackComponent:
  method integer CalcDamage(attacker, defender, attackInfo)        -- 默认 1     (ExecSpace=All)
  method boolean CalcCritical(attacker, defender, attackInfo)      -- 默认 false (ExecSpace=All)
  method float   GetCriticalDamageRate()                           -- 默认 2.0   (ExecSpace=All)
  method int32   GetDisplayHitCount(attackInfo)                    -- 默认 1     (ExecSpace=All)
  method void    OnAttack(defender)                                                 -- (ExecSpace=All)

HitComponent:
  method void OnHit(Entity attacker, integer damage, boolean isCritical, string attackInfo, int32 hitCount)
  emitter EmitHitEvent(HitEvent)
```

> ⚠ 上述所有钩子在其父类上都有未指定的 ExecSpace (=All)。在重写时添加 `@ExecSpace("ServerOnly")` 等会触发 **LEA-3014 `SignatureMismatch`**。去掉注解并仅声明 `method ...`。详情：[`msw-scripting/SKILL.md` §9 "方法重写"](../msw-scripting/SKILL.md)。

### 2-1. `HitEvent` 有效负载

```
AttackCenter:   Vector2
AttackerEntity: Entity (nilable)
Damages:        List<integer>    -- 多击分摊
Extra:          any              -- ★ 扩展槽 (击退/眩晕/元素/标签)
IsCritical:     boolean
TotalDamage:    integer
FeedbackAction: HitFeedbackAction  -- ⚠ 整个枚举已弃用
```

在 `Extra` 表上携带辅助信息（击退向量、摇晃时间、元素）。

### 2-2. `AttackEvent` 有效负载

一个字段，`DefenderEntity: Entity`。攻击者是处理器的 `self`。

### 2-3. ⚠️ 反模式：直接HP减法 — 不要绕过 `HitEvent`

直接减去防御者的HP，例如 `monster.Hp -= damage` / `target.MonsterAI.HP -= damage`，**不会发出 `HitEvent`** — 伤害皮肤、击中效果、`IsHitTarget` 免疫和 `OnHit` 重写都会静默跳过。

对于**玩家端**的自定义伤害（通道 / 聚集 / DoT），绕过也会破坏角色动画：`AvatarStateAnimationComponent` 仅对 `StateChangeEvent` 响应，因此玩家角色即使在HP条下降时也会保持空闲。如果您必须在不使用 `HitEvent` 的情况下应用伤害，还必须手动调用 `StateComponent:ChangeState("HIT")` (UPPERCASE键——参见 §10) 和，对于死亡/复活，`PlayerComponent:ProcessDead()` / `ProcessRevive()`。否则击中/死亡动作会静默错过且无错误。

---

## 3. 击中反应

### 3-1. 击退 — 每个身体的API

| 身体 (地图类型) | 实现 |
|---|---|
| **Rigidbody** (MapleTile) | `body:AddForce(Vector2(dir*5, 3))` ★推荐 · `SetForce` · `JustJump(Vector2(0, 4))` (垂直) |
| **Kinematicbody** (RectTile / 俯视) | `body.MoveVelocity = Vector2(dir*5, 0)` — 没有AddForce |
| **Sideviewbody** (SideViewRectTile) | `body.MoveVelocity` + `body.JumpSpeed` |

- Rigidbody 由引擎自动阻尼。Kinematic/Sideview 必须在 `OnUpdate` 内手动阻尼 (`MoveVelocity *= 0.9`)。
- 墙壁反弹：订阅 `FootholdCollisionEvent` 并反转速度。
- 击退是一个**一次性冲量**——不要将其与连续移动（追击、飞行）混淆。对于连续移动，参见 §1-6。
- **⚠ 禁止**：直接分配 `TransformComponent.Position` 在具有活跃身体的实体上 → 网络同步被阻塞。`body:SetPosition(...)` 是传送方法，因此不要在 `OnUpdate` 循环内调用它 (§1-6)。

标准模式：基于 `_UtilLogic.ElapsedSeconds` 的截止时间检查 + 从 `HitComponent:IsHitTarget` 返回 false。DefaultPlayer 默认的 `PlayerHit.mlua` 提供了这种模式（§9-4）。

替代方案：在无敌状态下，将 `HitComponent.CollisionGroup` 切换到单独的组 → 本身排除在解析之外。这对于帧精确的精度更好。

### 3-3. 状态效果（Buff/Debuff）

**无原生支持。** 直接实现 `@Component BuffComponent` + 使用 `_TimerService:SetTimerRepeat` 进行计时 + 广播自定义的 `StatusAppliedEvent`/`StatusExpiredEvent`。

对于单个简单的眩晕，`StateComponent:ChangeState("STUN")` + 输入/AI 阻挡标志就足够了。

---

## 4. 游戏感觉 — 所有原生

| 元素 | API | 执行空间 |
|------|-----|-----------|
| 击打停止（全局） | `_UtilLogic:SetClientTimeScale(float)` — 0~100 | ClientOnly |
| 击打停止（单个） | `renderer.PlayRate = 0` (Sprite/Skeleton/Avatar) | @Sync |
| 减速 | `_UtilLogic:SetClientTimeScale(0.3)` + 计时器恢复 | ClientOnly |
| 摄像机抖动 | `cameraComp:ShakeCamera(intensity, duration, targetUserId?)` | Client |
| 摄像机缩放 | `cameraComp:SetZoomTo(percent, duration, targetUserId?)` · 需要先设置 `IsAllowZoomInOut=true` | Client |
| 击打闪光 | `spriteRenderer.Color = Color(r,g,b,a)` → 计时器恢复 | @Sync |
| 颜色 HDR 过曝 | `Color.HSVToRGB(h, s, v, hdr=true)` — 允许值 > 1.0 | — |
| VFX 固定 | `_EffectService:PlayEffect(clipRUID, instigator, pos, zRot, scale, isLoop?, options?)` → 序列化 | — |
| VFX 附加 | `_EffectService:PlayEffectAttached(clipRUID, parent, localPos, localZRot, localScale, isLoop?, options?)` | — |
| VFX 移除 | `_EffectService:RemoveEffect(serial)` | — |
| SFX 2D | `_SoundService:PlaySound(id, volume, targetUserId?)` | Client |
| SFX 3D | `_SoundService:PlaySoundAtPos(id, pos, listener, volume)` | Client |
| SFX 循环 | `PlayLoopSound` / `PlayLoopSoundAtPos` | Client |
| SFX 附加 | `SoundComponent:Play()` · 通过 `Pitch` 0~3 进行音调随机化 | Client |
| BGM | `_SoundService:PlayBGM(id, volume)` / `StopBGM(immediately)` | Client |
| 预加载 | `_SoundService:LoadSound(id)` | ClientOnly |

`PlayEffect` 选项键：`FlipX, FlipY, SortingLayer, OrderInLayer, Alpha, StartFrameIndex, EndFrameIndex, PlayRate, SyncFlip, Color, MaterialID, IgnoreMapLayerCheck, LitMode`

获取当前摄像机：`_CameraService:GetCurrentCameraComponent()`。

### ParticleService — 内置粒子

通用粒子效果仅由枚举值驱动，无 RUID。3 类：

```
-- BasicParticle: 通用预设（无需 RUID）
integer _ParticleService:PlayBasicParticle(BasicParticleType, Entity instigator, Vector3 pos, number zRot, Vector3 scale, boolean isLoop, Dictionary options)
integer _ParticleService:PlayBasicParticleAttached(BasicParticleType, Entity parent, Vector3 localPos, number localZRot, Vector3 localScale, boolean isLoop, Dictionary options)

-- SpriteParticle: 自定义精灵作为粒子（需要 spriteRUID）
integer _ParticleService:PlaySpriteParticle(SpriteParticleType, string spriteRUID, Entity instigator, Vector3 pos, number zRot, Vector3 scale, boolean isLoop, Dictionary options)
integer _ParticleService:PlaySpriteParticleAttached(SpriteParticleType, string spriteRUID, Entity parent, Vector3 localPos, number localZRot, Vector3 localScale, boolean isLoop, Dictionary options)

-- AreaParticle: 广域环境粒子（增加 areaSize）
integer _ParticleService:PlayAreaParticle(AreaParticleType, Vector2 areaSize, Entity instigator, Vector3 pos, number zRot, Vector3 scale, boolean isLoop, Dictionary options)

void _ParticleService:RemoveParticle(integer serial)
```

选项键：`Color, SortingLayer, OrderInLayer, ParticleSize, ParticleCount`

循环粒子（`isLoop=true`）必须通过 `RemoveParticle(serial)` 清理。将序列存储在 `self._T` 中以便后续移除。

#### Full BasicParticleType 列表

| 系列 | 名称 | 描述 |
|------|------|-------------|
| 爆炸/撞击 | `SparkExplosion` | 火花（一次性）— 通用击打 |
| | `SparkLoop` | 连续火花 |
| | `SparkRadialExplosion` | 火花径向散射 |
| | `SmallExplosion` | 小型爆炸 + 烟雾 |
| | `BigExplosion` | 大型爆炸 + 烟雾 |
| | `TinyExplosion` | 非常小的爆炸（忽略 Color 选项） |
| | `DustExplosion` | 圆形冲击波 + 烟雾（忽略 Color 选项） |
| | `EnergyExplosion` | 圆形冲击波然后中心汇聚 |
| | `CircleBurst` | 圆形光爆 |
| | `PillarBurst` | 圆形光爆 + 方向性光 |
| 火/火焰 | `FireField` | 卡通火焰 |
| | `FireFieldIntense` | 强烈卡通火焰 |
| | `FireBall` | 单点火焰 |
| | `FlameThrower` | 火焰喷射流 |
| | `LargeFlames` | 从地面升起的大火焰 |
| | `MediumFlames` | 从地面升起的中小火焰 |
| | `TinyFlames` | 从地面升起的微小火焰 |
| | `WildFire` | 巨大火焰柱（忽略 Color 选项） |
| 闪电/电 | `LightningOrbSharp` | 球形电粒子 |
| | `LightningStrikeSharp` | 闪电 |
| | `LightningStrikeSharpTall` | 高闪电 |
| | `LightningOrbSoft` | 电波发射 |
| | `LightningBlast` | 周期性电波 |
| | `LightningStrike` | 周期性闪电 |
| | `LightningStrikeTall` | 周期性高闪电 |
| Buff/魔法 | `Aura` | 从地面升起的极光 |
| | `Buff` | 从地面升起强光 |
| | `Charge` | 大型粒子汇聚到一点 |
| | `ChargeOrb` | 粒子汇聚到一点 |
| | `Enchant` | 带有光/粒子的明亮光 |
| | `SpinField` | 绕旋转圆圈的粒子 |
| | `StarVortex` | 星光汇聚到中心 |
| | `Nova` | 宽圆形波 |
| | `UpperCylinder` | 从地面升起的柱 |
| 其他 | `Firework` | 烟花 |
| | `FireworkCluster` | 同时多个烟花 |
| | `FireFlies` | 萤火虫 |
| | `GoopSpray` | 向侧面喷射液体 |
| | `GoopSprayEffect` | 向下喷射液体 |
| | `DustStorm` | 广阔沙尘暴 |
| | `RisingSteam` | 从地面升起的白雾 |
| | `BigSplash` | 大型水花 |
| | `Shower` | 水洒在一点 |
| Full SpriteParticleType 列表（8）
| 名称 | 描述 |
|------|-------------|
| `BurstBig` | 精灵径向模式出现 |
| `SpawnField` | 粒子 + 精灵在圆形区域出现 |
| `BurstNova` | 粒子 + 精灵圆形模式爆发 |
| `SimpleSpawn` | 简单粒子 + 精灵出现 |
| `Burst` | 粒子 + 精灵散射 |
| `Stream` | 在特定方向移动时生成 |
| `StreamSharp` | 在特定方向移动的细线 |
| `AdditiveColor` | 应用于精灵的颜色效果 |

#### Full AreaParticleType 列表（12）
| 名称 | 描述 |
|------|-------------|
| `Rain` | 雨 |
| `Snow` | 雪 |
| `FogCalm` | 雾 |
| `FogHeavy` | 下降的重雾 |
| `FogLively` | 上升的雾 |
| `CalmStarField` | 上升的星团 |
| `StarFieldSimple` | 闪烁的星团 |
| `StarFog` | 星 + 星云粒子（静止） |
| `StarFogFlow` | 星 + 星云粒子（上升） |
| `Windlines` | 细线 |
| `WindlinesBig` | 细线 + 粗线 |
| `WindlinesSpeedy` | 快速直线 |

### 在 EffectService 和 ParticleService 之间选择

| 情况 | 推荐 |
|------|-----|
| MapleStory 技能 / 击打动画（特定图像） | `EffectService`（指定 RUID） |
| 通用击打/爆炸（快速实现） | `ParticleService.BasicParticle` |
| 将自定义图像散射为粒子 | `ParticleService.SpriteParticle` |
| 环境氛围（如雨/雪/雾） | `ParticleService.AreaParticle` |
| 持续效果（如 Buff 极光） | 使用 `isLoop=true` |
| 丰富、分层的效果 | 结合 EffectService 和 ParticleService |

> 服务器事件 → 客户端效果的标凈模式：`@Sync` 属性变化 → 在 `OnSyncProperty(ClientOnly)` 中检测到 → 调用 EffectService/ParticleService。

---

## 5. 死亡 / 复活

| 事件 | 触发条件 | 有效载荷 |
|------|----------|---------|
| `DeadEvent` | 在 `StateComponent:ChangeState("DEAD")` 时自动触发 | **无** |
| `ReviveEvent` | 在玩家 `PlayerComponent:Respawn()` 时自动触发（仅限玩家） | **无** |
| `StateChangeEvent` | 在每个状态转换时自动触发 | `CurrentStateName`, `PrevStateName` |

**追踪击杀者**：DeadEvent 无有效载荷 → 在 `HandleHitEvent` 中缓存 `self.LastAttacker = event.AttackerEntity`，并在 `HandleDeadEvent` 中使用。

对于玩家特定的死亡/复活，优先使用 §9-1 `PlayerComponent.Respawn/ProcessDead/ProcessRevive`。

---

## 6. 事件总线

| 逻辑事件 | MSW 实现 |
|----------|----------|
| OnAttackStart | `OnAttack` 钩子或自定义 `AttackStartEvent` |
| OnAttackHit / OnDamageTaken | 原生 `HitEvent` |
| OnAttackMiss | 自定义 — 当 `IsAttackTarget` 返回 false 时发送事件 |
| OnCriticalHit | 由 `HitEvent.IsCritical` 标志覆盖 |
| OnDeath / OnRevive | 原生 `DeadEvent`/`ReviveEvent` |
| OnStateChange | 原生 `StateChangeEvent` |
| OnKill / OnBlocked / OnParry / OnStatusApplied | 自定义 `@Event` |

### 6-1. 自定义事件规则

- 定义：`@Event script XxxEvent extends EventType` + `property` 声明
- 接收：`handler` 关键字（非方法），`@EventSender("Self" | "Service","XxxService" | "Logic","XxxLogic")`
- 连接/断开：`entity:ConnectEvent(XxxEvent, self.Handler)` / **在 `OnEndPlay` 中调用 `DisconnectEvent`**（引擎不会自动断开）
- 全局：`@Logic CombatEventBusLogic` 单例 + `@EventSender("Logic","CombatEventBusLogic")`

---

## 7. AI — FSM(StateComponent) + BT(AIComponent) + 自定义脚本（模式 A），所有原生兼容

| 模式 | 适用 | 参考 |
|------|------|------|
| **FSM** (`StateComponent` + `@State`) | 简单敌人（3~5 个状态），玩家 IDLE/HIT/DEAD，Boss 阶段，动画同步（`AvatarStateAnimationComponent` 自动映射 §10）。如果想要 `StateAnimationComponent` 自动切换剪辑，需要 `StateComponent.IsLegacy=false`。 | **[`../msw-general/references/animation-state.md`](../msw-general/references/animation-state.md)**（状态机 + 动画流程统一） |
| **BT** (`AIComponent` + 组合（4 个原生 + 自定义） + `@BTNode`) | 巡逻 + 追逐 + 攻击组合，多样的 Boss 模式，组合/装饰器复用，概率加权动作。需要 `StateComponent.IsLegacy=false`。 | **[`references/ai-bt.md`](references/ai-bt.md)** |
| **自定义脚本带自状态** (`@Component` 持有 `CurrentAIState` 加上直接 `SpriteRUID` 分配 — 士兵模式） | 不适合 `AIChase`/`AIWander` 的行为（游荡 ↔ 站立 ↔ 说话 ↔ 攻击，范围门控攻击，说话空闲）。**无需 `AIChaseComponent`/`AIWanderComponent`，无需 `IsLegacy=false` — 脚本绕过 ActionSheet 流程**。保留 `StateComponent` 仅用于 `IDLE` ↔ `DEAD`。 | [`../msw-general/references/monster.md` §7 "Canonical Pattern A Scripts (Soldier)"](../msw-general/references/monster.md) |

### 7-1. FSM — `StateComponent`（摘要）

`StateComponent` + `@State script XxxStateType extends StateType`（生命周期 `OnEnter`/`OnUpdate`/`OnExit`/`OnConditionCheck`）。唯一自动注册的状态是 `IDLE`/`DEAD`（+ `HIT` 如果存在 `HitComponent`，`MOVE` 如果存在 `AIChase`/`AIWander`）— `ATTACK`/`PATROL`/`STUN`/`PHASE2` 等。必须通过 `OnBeginPlay` 中的 `AddState("name", XxxStateType)` 预先注册。自动转换使用 `AddCondition(from, to)` + 每帧 `OnConditionCheck()`。

> ⚠ **状态名称必须为大写**；未注册名称立即产生 `[LEA-3005] InvalidArgument : 'stateName'`。在 `AvatarStateAnimationComponent.StateToAvatarBodyActionSheet` 中注册键**不会**自动在 `StateComponent` 中注册 — 这两者是独立的。

**完整实现 → [`../msw-general/references/animation-state.md`](../msw-general/references/animation-state.md)**（FSM 创作，`ChangeState` 失败矩阵，标准的 `PATROL/CHASE/ATTACK/HIT/DEAD` 怪物模式，以及状态→动画流程共同存在 — 两者是同一底层系统从两个角度看到的）

### 7-2. BT — `AIComponent`（摘要）

`AIComponent` + `SequenceNode`/`SelectorNode`/`RandomSelectorNode`/`ParallelNode` + `@BTNode` 动作节点 + 原生 `AIChaseComponent`/`AIWanderComponent`。**所有 4 种组合类型都是原生的**，自定义子流程策略可以通过 `@BTNode ... extends CompositeNode`（`ChildCount`/`ChildBehave`）脚本实现；装饰器/记忆（黑板）/威胁表必须手动实现。

> ⚠ 使用自定义 BT 时，从 `.model` 中移除 `AIChaseComponent`/`AIWanderComponent`。

**完整实现 → [`references/ai-bt.md`](references/ai-bt.md)**

> 完整怪物实体组合 → [`../msw-general/references/monster.md`](../msw-general/references/monster.md)
>
> 此 SKILL.md 仅涵盖战斗特定方面（ATTACK/HIT/DEAD + DeadEvent/ReviveEvent + BT 入口点）。对于通用 mlua 状态机 / 脚本模式，请参阅 [`msw-scripting`](../msw-scripting/SKILL.md)。

---

## 8. UI 原生

| UI | API |
|----|-----|
| HP 条（屏幕固定） | 使用 HP 量表精灵（`image_ruid = "f0911af597259044aa624a11332c0595"`）的 `SpriteGUIRendererComponent` 填充 + 左对齐 `UITransformComponent` 宽度调整。使用 `SliderComponent` 进行用户可拖动控制，而非只读 HP 量表。**⚠ 仅限 UI 实体** |
| 伤害数字 | 3 个 `DamageSkin*` 组件 + `DamageSkinService` — §11 |
| 十字准星 | `.ui` 中的 `SpriteGUIRendererComponent` |
| 组合计数器 / Buff 图标 | `TextGUIRendererComponent` + `SpriteGUIRendererComponent` |

**世界坐标 HP 条**（空中）：无原生支持。两种实现方案：

| 选项 | 方法 | 适用 |
|------|------|------|
| **轻量级** | 调整子实体的 `SpriteRendererComponent` 的 `LocalScale.x = hp/maxHp` 或使用 `TiledSize.x`（`SpriteDrawMode.Tiled`） | 快速原型，简单量表 |
| **完整** | 基于 `PixelRendererComponent` — **完整实现 [`references/hp-gauge.md`](references/hp-gauge.md)** | 生产级，一次显示多个怪物 |

---

## 9. DefaultPlayer 战斗原生

玩家实体具有 HP、复活和输入的原生支持。**不要创建自定义 `Hp`/`MaxHp` 属性** — 使用 `PlayerComponent`。

> `PlayerComponent` / `PlayerControllerComponent` 的完整属性/方法表在 [`msw-defaultplayer/SKILL.md`](../msw-defaultplayer/SKILL.md) 中。此处仅包含战斗核心。

### 9-1. 核心战斗 API

| 项目 | 使用 |
|------|------|
| HP 减少量 | `self.Entity.PlayerComponent.Hp -= event.TotalDamage` |
| 死亡检查 | `PlayerComponent:IsDead()` |
| 复活 | `PlayerComponent:Respawn()` — `RespawnPosition → SpawnLocation → 地图入口点`。`DeadEvent`/`ReviveEvent` 自动发出 |
| 客户端独占死亡处理 | `@ExecSpace("Client") ProcessDead(targetUserId?)` / `ProcessRevive(targetUserId?)` |
| 方向检查 ★ | `PlayerControllerComponent.LookDirectionX`（+1 右，-1 左）。**不要**使用 `TransformComponent.Scale.x` |
| 动作钩子覆盖 | `ActionAttack` / `ActionJump` / `ActionInteraction(key, isKeyDown)` 等。 |
| 动作事件接收 | `EmitPlayerActionEvent(PlayerActionEvent)` → §9-3 |

> ⚠ **自动攻击 / AI触发攻击必须先设置朝向。** `LookDirectionX` 是一个 **可写** 的 `@Sync` 属性 — 分配 `1`/`-1` 会翻转玩家角色面向该方向。默认输入管道仅从 *移动* 输入更新它，因此没有移动的攻击（自动战斗循环、AI节拍、技能按钮）会保持 **最后** 的朝向（默认左）— 角色面向错误方向 **并且** 基于 `LookDirectionX` 的攻击框（§1-5）会作用在错误的一侧。在此类攻击之前，指向目标：`controller.LookDirectionX = target.TransformComponent.WorldPosition.x >= self.Entity.TransformComponent.WorldPosition.x and 1 or -1`。仅分配 **符号**（±1），不要分配原始位置差值 — 攻击偏移量会乘以 `LookDirectionX`，因此非单位值会缩放/错位击打框。

### 9-3. `PlayerActionEvent`

```
property string ActionName       -- "Attack" / "Jump" / "Crouch" / ...
property Entity PlayerEntity
```

默认模式是 `PlayerAttack extends AttackComponent`，它接收 `@EventSender("Self")` 处理器 `HandlePlayerActionEvent(...)` 并在 `event.ActionName == "Attack"` 时分支。

### 9-4. 默认模板 (`RootDesk/MyDesk/`)

无需修改直接复制粘贴。按需覆盖：

| 文件 | 角色 | 要点 |
|------|------|------|
| `PlayerAttack.mlua` | 正面攻击框 | `LookDirectionX` 用于方向，`AttackFast` + `CollisionGroups.Monster`，`CalcDamage=50`，30% 暴击 |
| `PlayerHit.mlua` | i帧 | `ImmuneCooldown` 属性，`_UtilLogic.ElapsedSeconds` 截止时间，`IsHitTarget` 覆盖 |
| `Monster.mlua` | 怪物生命值 | 自定义 `@Sync Hp`（无 PlayerComponent），`HandleHitEvent` → `死亡/重生` |
| `MonsterAttack.mlua` | 基于精灵大小的近战 | `isvalid(defender.PlayerComponent)` + `__base:IsAttackTarget(...)` 在 `IsAttackTarget` 中的超类 |

### 9-5. 时间参考

**`_UtilLogic.ElapsedSeconds`** 推荐使用（世界时钟，暂停/恢复时一致）。不要使用 `os.clock()`。

### 9-6. 标准碰撞组

| 常量 | 目的 |
|------|------|
| `CollisionGroups.Player` | 怪物 → 玩家攻击 |
| `CollisionGroups.Monster` | 玩家 → 怪物攻击 |
| `CollisionGroups.HitBox` | `HitComponent.CollisionGroup` 的默认值 |

---

## 10. 角色动作 — `AvatarStateAnimationComponent`

自动链接 `StateComponent` 转变到角色动画。

```
@Sync property SyncDictionary<string, AvatarBodyActionElement> StateToAvatarBodyActionSheet  -- IsLegacy=false
@Sync property SyncDictionary<string, string>                  ActionSheet                    -- IsLegacy=true (已弃用)

method void   SetActionSheet(string key, string animationClipRuid)
method void   RemoveActionSheet(string key)
method string StateStringToAnimationKey(string stateName)
emitter EmitBodyActionStateChangeEvent(BodyActionStateChangeEvent)
```

- `ChangeState("HIT")` → 映射的 `MapleAvatarBodyActionState.Hit` 会自动播放
- 与战斗相关的状态值：`Attack`=3, `Hit`=14, `Dead`=10, `Alert`=4, `Heal`=13
- `IsLegacy=false` 已修复；仅使用 `StateToAvatarBodyActionSheet`

> 完整角色组件覆盖（`AvatarRendererComponent` 等）在 [`msw-defaultplayer`](../msw-defaultplayer/SKILL.md) 中。本节仅涵盖战斗动作映射。

---

## 11. 伤害特效（数字显示）

### 默认 RUID

| 目的 | RUID | 使用对象 |
|------|------|---------|
| 击中 | `3271c3e79bf04ecba9a107d55495970d` | 攻击者的 `DamageSkinSettingComponent.DamageSkinId` 默认值 |
| 受击 | `02c22d93421b4038b3c413b3e40b57ec` | 防御方显示 — 手动调用 `_DamageSkinService:Play` |
| 治疗效果 | `d58b67cf0f3a4eaf9fe1ad87c0ffac8a` | 治疗/药水 — 手动调用 `_DamageSkinService:Play` |

### 11-1. 自动模式（基于组件）

在 `Attack/AttackFast` 时，如果以下 3 个组件都存在，伤害数字会 **自动** 显示：

| 方向 | 组件 | 角色 |
|------|------|------|
| 攻击者 | `DamageSkinSettingComponent` | 显示哪种皮肤/样式 |
| 防御者 | `DamageSkinSpawnerComponent` | 显示位置偏移 |
| 防御者 | `DamageSkinComponent` | 伤害数字本体（显示在实体上方） |

将这 3 个组件都包含在 `.model` 中，伤害数字就会自动出现，无需脚本代码。

#### `DamageSkinSettingComponent` (攻击者)

| 属性 | 类型 | 默认值 | 描述 |
|------|------|--------|------|
| `DamageSkinId` | DataRef | hit RUID（上表） | 伤害数字皮肤 RUID |
| `DamageSkinScale` | Vector2 | (1, 1) | 数字大小 |
| `Alpha` | float | 1 | 透明度 |
| `PlayRate` | float | 1 | 播放速度 |
| `DelayPerAttack` | float | 0.05 | 多次攻击之间的延迟（秒） |
| `TweenType` | DamageSkinTweenType | Default | 动画样式 |
| `LitMode` | LitMode | Default | 光照影响 |

`DamageSkinTweenType`: `Default`（弹出）/ `Volcano`（扇形）/ `Blade`（重叠）/ 每个 `*Mini`（75% 缩放）

#### `DamageSkinSpawnerComponent` (防御者)

| 属性 | 类型 | 默认值 |
|------|------|--------|
| `DamageSkinOffset` | Vector2 | (0,0) |

### 11-2. 手动模式 — `DamageSkinService`

自动模式无法覆盖的情况（治疗、Miss/Guard、非标准伤害来源）直接调用 `_DamageSkinService`。

```
_DamageSkinService:Play(targetEntity, skinRuid, delay, damages:List<int>, tweenType, isCritical, offset, scale, playRate, alpha, litMode)
_DamageSkinService:PlayTextDamage(targetEntity, skinRuid, textType, tweenType)
_DamageSkinService:PreloadAsync(skinRuid, callback(success))    -- ClientOnly
```

`DamageSkinTextType`: `Miss` / `Guard` / `Resist` / `Shot` / `Counter`

> ⚠ `_DamageSkinService:Play` 在 `Client` 空间 — 从服务器逻辑（HP 减少等）调用时，用 `@ExecSpace("Client")` 方法包装它，或更改 `@Sync` 属性并从 `OnSyncProperty` 触发。

> ⚠ **`Play()` 有 6 个必需参数。仅传递其中 5 个可选参数会触发 LEA-3005 `InvalidArgument`。**

### 11-3. 配方

#### (a) 暴击强调 — 自动模式 + 动态缩放

自动模式在 `IsCritical=true` 时会自动渲染红色字体。为强调效果，临时增加攻击者的缩放：

```lua
-- ⚠ AttackComponent 钩子（CalcDamage/CalcCritical/GetCriticalDamageRate/GetDisplayHitCount/
--   IsAttackTarget/IsHitTarget/OnAttack）在父类上的 ExecSpace 未指定（=All）。
--   添加 @ExecSpace 触发 LEA-3014 SignatureMismatch。
--   详情：msw-scripting/SKILL.md §9 "方法覆盖 → LEA-3014"
method integer CalcDamage(Entity attacker, Entity defender, string attackInfo)
    return 100
end

method boolean CalcCritical(Entity attacker, Entity defender, string attackInfo)
    return math.random() < 0.3
end

method float GetCriticalDamageRate()
    return 2.5     -- 100 → 250
end
```

用 `DamageSkinSettingComponent.TweenType = Volcano`（向上散射）或 `Blade`（重叠）在视觉上区分暴击。

#### (b) 治疗 / 恢复 — 手动调用

```lua
local HEAL_RUID = "d58b67cf0f3a4eaf9fe1ad87c0ffac8a"

@ExecSpace("Client")
method void ShowHeal(Entity target, integer amount)
    _DamageSkinService:Play(
        target, HEAL_RUID, 0,
        { amount },                            -- damages
        DamageSkinTweenType.Default,
        false,                                 -- isCritical
        Vector2(0, 0.5),                       -- offset (在头顶)
        Vector2(1, 1), 1.0, 1.0, LitMode.Default
    )
end
```

#### (c) Miss / Guard / Resist 文本

```lua
local HIT_RUID = "02c22d93421b4038b3c413b3e40b57ec"

@ExecSpace("Client")
method void ShowMiss(Entity target)
    _DamageSkinService:PlayTextDamage(
        target, HIT_RUID, DamageSkinTextType.Miss, DamageSkinTweenType.Default
    )
end
```

当 `AttackComponent:IsAttackTarget` 返回 `false` 时调用 — “Miss 动画 + 伤害 0”。

#### (d) 多次攻击 — 用单个调用拆分为 N 个

如果你将 `damages` 参数作为 `_DamageSkinService:Play` 的列表传递，数字会按 `DelayPerAttack`（攻击者组件值）间隔依次显示：

```lua
_DamageSkinService:Play(target, ATTACK_RUID, 0, { 12, 8, 14, 11, 9 },
    DamageSkinTweenType.Default, false, Vector2(0,0), Vector2(1,1), 1, 1, LitMode.Default)
```

自动模式与 `HitEvent.Damages`（列表）行为相同 — 覆盖 `GetDisplayHitCount(attackInfo)` 控制拆分数量。

#### (e) 预加载 — 防止首次显示卡顿

首次使用皮肤 RUID 可能会有纹理加载延迟。在地图进入时预加载：

```lua
@ExecSpace("ClientOnly")
method void OnBeginPlay()
    _DamageSkinService:PreloadAsync("3271c3e79bf04ecba9a107d55495970d", function(ok) end)
    _DamageSkinService:PreloadAsync("02c22d93421b4038b3c413b3e40b57ec", function(ok) end)
    _DamageSkinService:PreloadAsync("d58b67cf0f3a4eaf9fe1ad87c0ffac8a", function(ok) end)
end
```

#### (f) TweenType 使用场景

| TweenType | 推荐情况 |
|----------|----------|
| `Default` | 普通击中 |
| `Volcano` | 暴击 / 区域击中（向上散射） |
| `Blade` | 连续斩击 / 连招（重叠数字） |
| `*Mini` | 小伤害（DoT）— 减少屏幕杂乱 |

#### (g) 派系特定皮肤

为使用每方不同的皮肤 RUID（玩家 vs 敌人、PvP 派系等），在运行时交换 `DamageSkinSettingComponent.DamageSkinId`：

```lua
self.Entity.DamageSkinSettingComponent.DamageSkinId = MY_TEAM_SKIN_RUID
```

---

## 12. 击中效果 — `HitEffectSpawnerComponent`

附加到防御者，`HitEvent` 触发时 **自动** 播放击中效果。无属性 — 仅将组件添加到 `.model`。

---

## 13. 完整战斗清单

- [ ] **攻击者模型**：`AttackComponent` 派生脚本（+可选：`DamageSkinSettingComponent`）
- [ ] **防御者模型**：`HitComponent` + `HitEffectSpawnerComponent` + (可选：`DamageSkinSpawnerComponent` + `DamageSkinComponent`)
- [ ] **HitComponent**：`IsLegacy=false`，设置 `ColliderType`/`BoxSize`/`CircleRadius`，设置 `CollisionGroup`
- [ ] **状态动作**：在 `StateComponent` 中注册 `ATTACK`/`HIT`/`DEAD` + `AvatarStateAnimationComponent.StateToAvatarBodyActionSheet`
- [ ] **生命值处理**：玩家使用 `PlayerComponent.Hp`；怪物使用自定义 `@Sync Hp`
- [ ] **方向检查**：`LookDirectionX`（无 Scale.x）；对于自动/AI触发攻击，攻击前将其设置为指向目标（±1）— §9-1
- [ ] **时间参考**：`_UtilLogic.ElapsedSeconds`（无 os.clock）
- [ ] **事件清理**：在 `OnEndPlay` 中显式 `DisconnectEvent`
- [ ] **身体规则**：不要直接在具有活动身体的实体上分配 `TransformComponent.Position`

---

## 14. 需要自定义实现

增益/减益 · BT 装饰器/记忆（黑板） · 仇恨/威胁表 · 投射物池 · 穿刺/最大命中 · 晕眩等级系统 · 资源（MP/耐力/怒气） · 连招/取消窗口 · 格挡/招架 · 世界→屏幕坐标转换 · 世界空间 HP 条

---

## 不在范围内

- 一般玩家主题（HP/移动/相机/服装除外）：[`msw-defaultplayer`](../msw-defaultplayer/SKILL.md)
- 一般 mlua 语法/生命周期：[`msw-scripting`](../msw-scripting/SKILL.md)
- `.model` 编写规则/模板：[`msw-general`](../msw-general/SKILL.md)
