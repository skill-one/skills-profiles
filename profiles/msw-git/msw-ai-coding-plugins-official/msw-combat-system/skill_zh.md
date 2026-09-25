# msw-combat-system

MSW 完整的战斗流程。仅涵盖具有 **MSW 原生 API 支持** 的通用 2D 战斗层中的项目，无论类型如何。不包括公式/理论。API 签名基于 `Environment/NativeScripts/**/*.d.mlua`。

---

## 0. 覆盖矩阵

| # | 层级 | 原生 | 需要自定义 |
|---|-------|--------|-----------------|
| 1 | 攻击解析 | `AttackComponent` + `HitComponent` (Box/Circle/Polygon) | 胶囊/锥形/射线, 穿刺次数 |
| 2 | 伤害模型 | `CalcDamage`/`CalcCritical`/`GetCriticalDamageRate`/`GetDisplayHitCount` 钩子 + `HitEvent.Extra:any` | 元素亲和, 复合公式 |
| 3 | 击中反应 | 每个身体的击退 API, 基于 `IsHitTarget` 的 i-frame | 晃动等级, 状态效果 |
| 4 | 游戏感觉 | **所有 6 个原生** (击停, 震动, 缩放, 闪光, VFX, SFX) | — |
| 5 | 战斗状态 | `StateComponent` + `DeadEvent`/`ReviveEvent`, `PlayerComponent` HP/复活 | MP/耐力/狂怒, 仇恨 |
| 6 | 事件总线 | `HitEvent`/`AttackEvent`/`StateChangeEvent`/`PlayerActionEvent` + 自定义 `@Event` | 击杀/阻挡 |
| 7 | AI | `StateComponent` (FSM) + `AIComponent` (BT, 4 个原生组合 + 自定义 `extends CompositeNode`) + `AIChaseComponent`/`AIWanderComponent`, `_UserService.UserEntities` | 装饰器/记忆(黑板), 威胁表 |
| + | 伤害皮肤 | 3 个 `DamageSkin*` 组件 + `DamageSkinService` | — |
| + | 击中效果 | `HitEffectSpawnerComponent` (自动) | — |
| + | 角色动作 | `AvatarStateAnimationComponent` (状态→MapleAvatarBodyActionState) | — |

---

## 0.5 参考资料 — 去哪里查找

这个 SKILL.md 仅涵盖 **系统流程和原生 API 表面**。实际模型 JSON、完整脚本代码和变化模式在下面的 references/* 文件中——直接阅读它们。

| 文件 | 范围 | 何时阅读 |
|------|-------|--------------|
| [`../msw-general/references/monster.md`](../msw-general/references/monster.md) | 怪物 `.model` 组件组装 + ActionSheet + AI 选择 + 模式 A 脚本 (Soldier 风格) + HP/重生 + 生成 + 验证 | 当构建具有战斗能力的怪物时 |
| [`references/hp-gauge.md`](references/hp-gauge.md) | 基于 `PixelRendererComponent` 的 HP 条的完整实现 | 当附加屏幕固定 HP 条时 |
| [`references/projectile.md`](references/projectile.md) | 弹道 (无身体的实体 + `OnUpdate Translate`) + 自导/穿甲/范围伤害变体 | 当构建箭头、子弹、魔法弹等远程攻击时 |
| [`references/ai-bt.md`](references/ai-bt.md) | 行为树 — `AIComponent` + 组合 (4 个原生 + 自定义) + `@BTNode` + 自定义装饰器/记忆/威胁 | 当您需要基于 BT 的怪物/首领 AI 和多层决策时 |

> 优先级: **这个 SKILL.md (概念 + API 表格) → 相关的 references/* (完整实现)**。

---

## 1. 攻击解析

### 1-1. 形状 & 攻击触发

`HitComponent.ColliderType` 仅支持 **Box / Circle / Polygon**。其他形状必须通过组合来近似。

```
AttackComponent:
  Attack(Vector2 size, Vector2 offset, string attackInfo, CollisionGroup? cg)    → table<Component>
  Attack(Shape shape, string attackInfo, CollisionGroup? cg)                     → table<Component>
  AttackFast(Shape shape, string attackInfo, CollisionGroup? cg)                 → void   (用于大量解析, 弹幕)
  AttackFrom(Vector2 size, Vector2 position, string attackInfo, CollisionGroup? cg) → table<Component>
  emitter EmitAttackEvent(AttackEvent)
```

- 形状: `CircleShape(position, radius)` / `BoxShape(position, size, angle)` / `PolygonShape(position, points, angle)`. 对于轴对齐矩形，请使用 `BoxShape(center, size, 0)` — 没有 RectangleShape 类型。当不需要旋转时，将 `angle = 0` 传递给 `BoxShape` / `PolygonShape`。
- 多边形击中表面: `HitComponent.PolygonPoints: SyncList<Vector2>`
- `AttackFast` 不构建击中表 → 对于弹幕/大量解析具有更好的性能

### 1-2. 目标过滤器

| 侧 | 覆盖 | 目的 |
|------|----------|---------|
| 攻击者 | `AttackComponent:IsAttackTarget(defender, attackInfo) → boolean` | 派系 / 距离 / 状态 |
| 防御者 | `HitComponent:IsHitTarget(attackInfo) → boolean` | 无敌 / 免疫 |

如果任一返回 false → 击中被排除。超调用是 **`__base:IsAttackTarget(...)`** (mlua 特有的)。

> ⚠ **在覆盖时不要添加 `@ExecSpace`** — 两者 `IsAttackTarget` 和 `IsHitTarget` 在父级上都有未指定的 ExecSpace (=All)。在子级中添加类似 `@ExecSpace("ServerOnly")` 的注释会触发运行时的 **LEA-3014 `SignatureMismatch`**。即使没有注释，调用路径也通过服务器端击中流程，因此实际执行发生在服务器上。详细信息: [`msw-scripting/SKILL.md` §9 "方法覆盖"](../msw-scripting/SKILL.md).

- `Attack*(..., cg)` 的 `cg` 参数是 **对防御者 `HitComponent.CollisionGroup` 的精确匹配过滤器** (默认为 `CollisionGroups.HitBox`)。它不参考碰撞矩阵，攻击者自己的组无关紧要。`nil` (省略) = 每个 `HitComponent` 都是候选者。一个 **与防御者实际组不同的有效组** 击中 **0 个目标且无错误** (静默); 不存在于此世界的碰撞组集中的组引用表现得像 `nil` (所有组)。当传递一个组 (例如. `CollisionGroups.Monster`) 时，首先将目标怪物的 `HitComponent.CollisionGroup` 设置为该相同组 — 示例工作区怪物将其覆盖为 `Monster`, 这就是示例攻击脚本正常工作的原因。从另一个世界导入的模型其组 ID 缺失于此世界的碰撞组集中的，会静默地注册在 `Default` 组下 — 用 `nil` 或 `CollisionGroups.Default` 可以到达它。
- **防止重复击中 / 穿刺 / 最大击中**: 不是原生的。在脚本中通过 `Attack` 返回的表 + `table<Entity, boolean>` 缓存进行管理。

### 1-3. `attackInfo` 标记

一个字符串扩展点，传播到 `CalcDamage`/`IsHitTarget`/`GetDisplayHitCount`。值约定由项目决定。建议使用命名空间样式，例如 `"melee.light"`, `"dot.poison"`。

### 1-4. ⚠️ IsLegacy

`ColliderType`/`ColliderOffset`/`PolygonPoints` 仅在 `HitComponent.IsLegacy = false` 时有效。`BoxOffset`/`ColliderName` 已弃用。

### 1-5. 每个攻击形式的形状映射

| 形式 | 形状构造 |
|------|--------------------|
| 前方近战 Box | `BoxShape(pos + LookDirectionX*offset, size, 0)` — 参考默认玩家 `PlayerAttack` |
| 圆形 AoE | `CircleShape(self.WorldPos, radius)` |
| 弹道 | 生成一个 **无身体的模型** (仅 Sprite+Transform) + 在 `OnUpdate(delta)` 调用 `TransformComponent:Translate(speed*delta, 1)` + 基于距离的击中检查 + `_EntityService:Destroy`. 移动规则在 §1-6，**完整实现 → [`references/projectile.md`](references/projectile.md)** |

**没有 MSW 特定的弹道系统** — 实现为实体 + `AttackComponent` 组合。

### 1-6. 连续移动 — 弹道、怪物和 AI 的通用规则

连续移动 (追击、飞行、自动移动) 基于 **每帧 `OnUpdate(delta)`**。通过计时器 (`SetTimerRepeat(0.1~0.15s)`) 移动会产生 6~10Hz 的传送，看起来很卡顿。

#### 每个目标的推荐 API

| 目标 | 身体? | 移动 API | 理由 |
|--------|:-----:|--------------|-----------|
| **怪物 / NPC / AI** | **是** (地图类型身体 + `MovementComponent`) | `MovementComponent:MoveToDirection(dir, 0)` + `MovementComponent.InputSpeed` | `MovementComponent.d.mlua:1` — 控制所有三个 Rigid/Kinematic/Sideview. `InputSpeed` 属于 `MovementComponent` (`.d.mlua:7`), 所以它 **不是** 仅限玩家。第二个参数 `0` — deltaTime 仅在梯子上应用 (`.d.mlua:32`). 官方 BT 示例 `ActionFollow`/`ActionMoveRandom` 也使用 `0`. |
| **弹道 / 宝石 / 掉落物 / 效果** | **否** (Sprite+Transform+Trigger) | 每帧 `self.Entity.TransformComponent:Translate(speed*delta, 0)` | 直接修改 Transform 是安全的，没有身体。官方 "创建长程弹道" 教程中的模式。 |
| **直接刚体控制** (高级) | 是 | `body:AddForce(...)` — 持续加速度 / 冲击 | `RigidbodyComponent.d.mlua:71` — `MoveVelocity` 主要由 `MovementComponent` 控制，因此优先通过 `MovementComponent` 路由，而不是直接写入。 |

> 对于 `MovementComponent.InputSpeed` 的实际速度转换，请参阅 [`msw-general/references/platform.md` §10](../msw-general/references/platform.md) (MapleTile=×1, RectTile=÷1.2, SideView=×1.5).

#### 禁止模式

| ❌ | 原因 |
|---|--------|
| `_TimerService:SetTimerRepeat(move, 0.1~0.15)` 用于移动 | 6~10Hz 传送, 没有帧插值 → 卡顿 |
| `body:SetPosition(...)` / `MovementComponent:SetPosition(...)` 在 `OnUpdate` 内 | **两者都是传送方法** (`MovementComponent.d.mlua:37`, `SetPosition` 在每个身体的 `.d.mlua` 中) 使用它们进行连续移动是卡顿的。仅用于一次性生成/重生/快照。 |
| `self.Entity.TransformComponent.Position = newPos` (有活动的身体) | 物理引擎在下一帧会覆盖它，并且网络同步被阻塞。 |
| 无 delta 的常量步长, 例如 `Translate(0.009, 0)` | 帧率依赖。在 60FPS 和 30FPS 之间的速度不同。 |

#### ⚠ 谨慎使用官方 msw-search 反模式

`mlua_Document_Retriever` 返回一个高评分的 "**使用 MovementComponent 控制实体移动**" 文档，但正文是一个 **反模式**，在 `OnUpdate` 中每帧使用 `MovementComponent:SetPosition(...)` 移动 — **忽略该文档** 并使用上表中的 `MoveToDirection` / `Translate`. `FlappyFish Remake`, `Stopping the Taxi`, and `Making a Moving Foothold` 也显示了缺失 delta 或直接 `Position` 分配，所以在引用它们时要小心。

#### 移动组件附加 — 怪物 / NPC

**默认情况下不包含在怪物模型中。** `.model` 必须包含以下所有组件。

| 组件 | 备注 |
|-----------|-------|
| `MOD.Core.TransformComponent` | 默认 |
| `MOD.Core.SpriteRendererComponent` | 渲染器 |
| 身体 (地图类型) | `RigidbodyComponent`(MapleTile) / `KinematicbodyComponent`(RectTile) / `SideviewbodyComponent`(SideViewRectTile) |
| `MOD.Core.MovementComponent` | 例如. `InputSpeed = 2.0` — 移动 API 所需 |

#### 交叉引用

- **击退 (1-shot 冲击)** 不是连续移动，因此直接使用 §3-1。
- 每个地图类型的身体选择 / InputSpeed 转换: [`msw-general/references/platform.md` §4·§10](../msw-general/references/platform.md)

---

## 1-7. 基于碰撞的击中 — 选择检测方法 (不要手动计算距离)

当请求是 "基于碰撞/接触的击中" (玩家↔怪物触摸伤害, 危险区域, 陷阱, 重叠) 时，根据意图选择。**每帧距离计算不是默认的** — 当设计要求基于碰撞的接触时，在请求者和实现者之间最常见的不匹配。

| 意图 | 检测 | 原因 |
|------|-----------|-----|
| 主动攻击挥动 / 击中框 / 弹道爆发 | `AttackComponent:Attack`/`AttackFast`/`AttackFrom` → 解决 defender `HitComponent`, 发射 `HitEvent` | 完整流程: 伤害皮肤, 击中效果, `IsHitTarget` i-frame, `OnHit` |
| 身体接触 / 区域 / 陷阱重叠, 目标任意或多个 | `TriggerComponent` + `OnEnterTriggerBody`/`OnStayTriggerBody`/`OnLeaveTriggerBody` (或 `TriggerEnter/Stay/LeaveEvent`) + `CollisionGroup` 过滤, 然后通过 `HitEvent` 流程路由伤害 | 引擎侧重叠: 尊重真实的碰撞器形状 (Box/Circle/Polygon), `ColliderOffset`, 和组过滤 |
| 自导 / 单个已知目标 | 每帧 `OnUpdate` 距离检查 ([`references/projectile.md`](references/projectile.md)) | 仅当事先知道 exactly 一个目标实体时才合理 |

- ❌ 每帧 `math.sqrt(dx*dx+dy*dy) < r` 用于玩家↔怪物或多目标碰撞: 它会静默地近似以 transform 为中心的单个圆 (忽略每个碰撞器的形状/大小/`ColliderOffset`), 跳过 `CollisionGroup` 过滤，并且每帧的成本是 O(攻击者 × 目标). "基于碰撞的击中" 意味着原生碰撞器，而不是距离轮询.
- `CollisionGroup` 默认为 `CollisionGroups.TriggerBox`. `OnStayTriggerBody` 在重叠时 **每帧** 都会触发 — 使用冷却来门控伤害，不要每 tick 应用.
- 检测 ≠ 伤害应用: 在原生重叠触发后，仍然通过 `HitEvent` / `AttackComponent` 应用伤害 — 绝对不要直接减去 HP.

---

## 2. 伤害模型

```
AttackComponent:
  method integer CalcDamage(attacker, defender, string attackInfo)        -- 默认 1     (ExecSpace=All)
  method boolean CalcCritical(attacker, defender, string attackInfo)      -- 默认 false (ExecSpace=All)
  method float   GetCriticalDamageRate()                           -- 默认 2.0   (ExecSpace=All)
  method int32   GetDisplayHitCount(attackInfo)                    -- 默认 1     (ExecSpace=All)
  method void    OnAttack(defender)                                                 -- (ExecSpace=All)

HitComponent:
  method void OnHit(Entity attacker, integer damage, boolean isCritical, string attackInfo, int32 hitCount)
  emitter EmitHitEvent(HitEvent)
```

> ⚠ 上述所有钩子在其父级上都有未指定的 ExecSpace (=All). 在覆盖时添加 `@ExecSpace("ServerOnly")` 等. 触发 **LEA-3014 `SignatureMismatch`**. 去掉注释并仅声明 `method ...`. 详细信息: [`msw-scripting/SKILL.md` §9 "方法覆盖"](../msw-scripting/SKILL.md).

### 2-1. `HitEvent` 有效负载

```
AttackCenter:   Vector2
AttackerEntity: Entity (nilable)
Damages:        List<integer>    -- 多击分片
Extra:          any              -- ★ 扩展槽 (击退/眩晕/元素/标签)
IsCritical:     boolean
TotalDamage:    integer
FeedbackAction: HitFeedbackAction  -- ⚠ 整个枚举已弃用
```

在 `Extra` 表中携带辅助信息 (击退向量, 晃动时间, 元素)。

### 2-2. `AttackEvent` 有效负载

单个字段，`DefenderEntity: Entity`. 攻击者是处理器的 `self`。

### 2-3. ⚠️ 反模式: 直接 HP 减少一一对应 — 不要绕过 `HitEvent`

直接减去防御者的 HP，例如 `monster.Hp -= damage` / `target.MonsterAI.HP -= damage`, **不会** 发射 `HitEvent` — 伤害皮肤, 击中效果, `IsHitTarget` 免疫等所有内容都静默地跳过。

对于 **玩家端** 的自定义伤害 (通道 / 蕴含 / DoT), 绕过会破坏角色动画: `AvatarStateAnimationComponent` 仅在 `StateChangeEvent` 下反应，所以玩家角色即使在 HP 条下降，也会停留在待机状态。如果您必须在不使用 `HitEvent` 的情况下应用伤害, 也必须手动调用 `StateComponent:ChangeState("HIT")` (UPPERCASE 键 — 参考 §10) 和, 对于死亡/复活, `PlayerComponent:ProcessDead()` / `ProcessRevive()`. 否则击中/死亡动作会静默地错过，并且没有错误。

---

## 3. 击中反应

### 3-1. 击退 — 每个身体的 API

| 身体 (地图类型) | 实现 |
|---|---|
| **Rigidbody** (MapleTile) | `body:AddForce(Vector2(dir*5, 3)` ★推荐 · `SetForce` · `JustJump(Vector2(0, 4)` (垂直) |
| **Kinematicbody** (RectTile / 俯视) | `body.MoveVelocity = Vector2(dir*5, 0)` — 没有加 `AddForce` |
| **Sideviewbody** (SideViewRectTile) | `body.MoveVelocity` + `body.JumpSpeed` |

- Rigidbody 由引擎自动阻尼。Kinematic/Sideview 必须在 `OnUpdate` 内手动阻尼 (`MoveVelocity *= 0.9`).
- 墙壁弹跳: 订阅 `FootholdCollisionEvent` 并翻转速度。
- 击退是一次性的 **冲击** — 不要将其与连续移动 (追击, 飞行) 混淆。对于连续移动，请参阅 §1-6。
- **⚠ 禁止**: 在具有活动身体的实体上直接分配 `TransformComponent.Position` → 阻塞网络同步。`body:SetPosition(...)` 是传送方法，所以不要在 `OnUpdate` 循环内调用它 (§1-6).

### 3-2. i-frame

标准模式: 使用 `_UtilLogic.ElapsedSeconds` 基线的截止检查 + 从 `HitComponent:IsHitTarget` 返回 false。默认玩家 `PlayerHit.mlua` 提供了这个模式（§9-4）。

替代方案: 在无敌时, 将 `HitComponent.CollisionGroup` 切换到单独的组 → 本身排除了解析。这对于需要帧精确度的精度更好。

### 3-3. 状态效果 (增益/减益)

**没有原生支持。** 直接实现 `@Component BuffComponent` + 使用 `_TimerService:SetTimerRepeat` 进行计时 + 广播自定义 `StatusAppliedEvent`/`StatusExpiredEvent`。

对于单个简单的眩晕, `StateComponent:ChangeState("STUN")` + 输入/AI 阻挡标志就足够了。

---

## 4. 游戏感觉 — 所有原生

| 元素 | API | ExecSpace |
|---------|-----|-----------|
| 击停 (全局) | `_UtilLogic:SetClientTimeScale(float)` — 0~100 | ClientOnly |
| 击停 (单个) | `renderer.PlayRate = 0` (Sprite/Skeleton/Avatar) | @Sync |
| 慢动作 | `_UtilLogic:SetClientTimeScale(0.3)` + 计时器恢复 | ClientOnly |
| 摄像机震动 | `cameraComp:ShakeCamera(intensity, duration, targetUserId?)` | Client |
| 摄像机缩放 | `cameraComp:SetZoomTo(percent, duration, targetUserId?)` · 首先需要 `IsAllowZoomInOut=true` | Client |
| 击中闪光 | `spriteRenderer.Color = Color(r,g,b,a)` → 计时器恢复 | @Sync |
| 颜色 HDR 超亮 | `Color.HSVToRGB(h, s, v, hdr=true)` — 允许值 > 1.0 | — |
| VFX 固定 | `_EffectService:PlayEffect(clipRUID, instigator, pos, zRot, scale, isLoop?, options?)` → 序列 | — |
| VFX 附加 | `_EffectService:PlayEffectAttached(clipRUID, parent, localPos, localZRot, localScale, isLoop?, options?)` | — |
| VFX 移除 | `_EffectService:RemoveEffect(serial)` | — |
| 2D 音效 | `_SoundService:PlaySound(id, volume, targetUserId?)` | Client |
| 3D 音效 | `_SoundService:PlaySoundAtPos(id, pos, listener, volume)` | Client |
| 音效循环 | `PlayLoopSound` / `PlayLoopSoundAtPos` | Client |
| 音效附加 | `SoundComponent:Play()` · 通过 `Pitch` 0~3 进行音调随机化 | Client |
| 背景音乐 | `_SoundService:PlayBGM(id, volume)` / `StopBGM(immediately)` | Client |
| 预加载 | `_SoundService:LoadSound(id)` | ClientOnly |

`PlayEffect` 选项键: `FlipX, FlipY, SortingLayer, OrderInLayer, Alpha, StartFrameIndex, EndFrameIndex, PlayRate, SyncFlip, Color, MaterialID, IgnoreMapLayerCheck, LitMode

获取当前摄像机: `_CameraService:GetCurrentCameraComponent()`.

### ParticleService — 内置粒子

通用粒子效果，仅由枚举值驱动，没有 RUID。3 个类别:

```
-- BasicParticle: 通用预设 (不需要 RUID) |
integer _ParticleService:PlayBasicParticle(BasicParticleType, Entity instigator, Vector3 pos, number zRot, Vector3 scale, boolean isLoop, Dictionary options)
integer _ParticleService:PlayBasicParticleAttached(BasicParticleType, Entity parent, Vector3 localPos, number localZRot, Vector3 localScale, boolean isLoop, Dictionary options)

-- SpriteParticle: 自定义精灵作为粒子 (需要 spriteRUID) |
integer _ParticleService:PlaySpriteParticle(SpriteParticleType, string spriteRUID, Entity instigator, Vector3 pos, number zRot, Vector3 scale, boolean isLoop, Dictionary options)
integer _ParticleService:PlaySpriteParticleAttached(SpriteParticleType, string spriteRUID, Entity parent, Vector3 localPos, number localZRot, Vector3 localScale, boolean isLoop, Dictionary options)

-- AreaParticle: 环境粒子 (wide area) (areaSize 添加) |
integer _ParticleService:PlayAreaParticle(AreaParticleType, Vector2 areaSize, Entity instigator, Vector3 pos, number zRot, Vector3 scale, boolean isLoop, Dictionary options)

void _ParticleService:RemoveParticle(integer serial)
```

options 键: `Color, SortingLayer, OrderInLayer, ParticleSize, ParticleCount`

循环粒子 (`isLoop=true`) 必须通过 `RemoveParticle(serial)` 清理。将序列存储在 `self._T` 中以便稍后删除。

#### 完整 BasicParticleType 列表

| 系列 | 名称 | 描述 |
|------|------|-------------|
| 爆炸/撞击 | `SparkExplosion` | 粒子 (一次性) — 通用击中 |
| | `SparkLoop` | 循环火花 |
| | `SparkRadialExplosion` | 循环散开的火花 |
| | `SmallExplosion` | 小型爆炸 + 烟雾 |
| | `BigExplosion` | 大型爆炸 + 烟雾 |
| | `TinyExplosion` | 非常小的爆炸 (忽略 Color 选项) |
| | `DustExplosion` | 圆形冲击波 + 烟雾 (忽略 Color 选项) |
| | `EnergyExplosion` | 圆形冲击波然后中心收敛 |
| | `CircleBurst` | 圆形光爆 |
| | `PillarBurst` | 圆形光爆 + 方向性光 |
| 火/火焰 | `FireField` | 卡通火焰 |
| | `FireFieldIntense` | 强力卡通火焰 |
| | `FireBall` | 单点火焰 |
| | `FlameThrower` | 火焰喷射流 |
| | `LargeFlames` | 从地板升起的大火焰 |
| | `MediumFlames` | 从地板升起的普通火焰 |
| | `TinyFlames` | 从地板升起的微小火焰 |
| | `WildFire` | 巨大的火焰柱 (忽略 Color 选项) |
| 闪电/电 | `LightningOrbSharp` | 球形电粒子 |
| | `LightningStrikeSharp` | 闪电 |
| | `LightningStrikeSharpTall` | 高闪电 |
| | `LightningOrbSoft` | 电波发射 |
| | `LightningBlast` | 周期性电波 |
| | `LightningStrike` | 周期性闪电 |
| | `LightningStrikeTall` | 周期性高闪电 |
| 增益/魔法 | `Aura` | 从地板升起的极光 |
| | `Buff` | 从地板升起的光芒 |
| | `Charge` | 大型粒子向一个点收敛 |
| | `ChargeOrb` | 粒子向一个点收敛 |
| | `Enchant` | 大型光，周围有光/粒子 |
| | `SpinField` | 粒子绕旋转圆 |
| | `StarVortex` | 星光向中心收敛 |
| | `Nova` | 宽圆形波 |
| | `UpperCylinder` | 从地板升起的柱 |
| 杂项 | `Firework` | 烟花 |
| | `FireworkCluster` | 同时多个烟花 |
| | `FireFlies` | 萤火虫 |
| | `GoopSpray` | 向侧面喷射液体 |
| | `GoopSprayEffect` | 向下喷射液体 |
| | `DustStorm` | 大型尘暴 |
| | `RisingSteam` | 从地板升起的白色雾气 |
| | `BigSplash` | 大型水花 |
| | `Shower` | 在一个点上倒水 |

#### 选择 EffectService 和 ParticleService 之间的差异

| 情况 | 推荐 |
|-------|-----------------------|
| MapleStory 技能/击中动画 (特定图像) | `EffectService` (指定 RUID) |
| 通用击中/爆炸 (快速实现) | `ParticleService.BasicParticle` |
| 散开自定义图像作为粒子 | `ParticleService.SpriteParticle` |
| 环境环境 (如雨/雪/雾) | `ParticleService.AreaParticle` |
| 持续效果 (如增益光环) | 使用 `isLoop=true` 的任一者 |
| 丰富的分层效果 | 结合 EffectService 和 ParticleService |

> 标准模式: 服务器事件 → 客户端效果: `@Sync` 属性更改 → 在 `OnSyncProperty(ClientOnly)` 中检测 → 调用 EffectService/ParticleService.

---

## 12. 击中效果 — `HitEffectSpawnerComponent`

附加到防御者，击中效果会 **自动** 在 `HitEvent` 播放。没有属性 — 仅将组件添加到 `.model` 中。

---

## 13. 完整战斗清单

- [ ] **攻击者模型**: 一个 `AttackComponent` 派生脚本 (+可选: `DamageSkinSettingComponent`)
- [ ] **防御者模型**: `HitComponent` + `HitEffectSpawnerComponent` + (可选: `DamageSkinSpawnerComponent` + `DamageSkinComponent`)
- [ ] **HitComponent**: `IsLegacy=false`, 设置 `ColliderType`/`BoxSize`/`CircleRadius`, 设置 `CollisionGroup`
- [ ] **状态动作**: 注册 `ATTACK`/`HIT`/`DEAD` 在 `StateComponent` + `AvatarStateAnimationComponent.StateToAvatarBodyActionSheet`
- [ ] **HP 处理**: 玩家使用 `PlayerComponent.Hp`; 怪物使用自定义 `@Sync Hp`
- [ ] **方向检查**: `LookDirectionX` (不要 Scale.x); 对于自动/AI 触发的攻击, 在攻击前将其指向目标 (±1) — §9-1
- [ ] **时间参考**: `_UtilLogic.ElapsedSeconds` (不要 os.clock)
- [ ] **事件清理**: 在 `OnEndPlay` 中显式 `DisconnectEvent`
- [ ] **身体规则**: 不要在具有活动身体的实体上直接分配 `TransformComponent.Position` → 阻塞网络同步。`body:SetPosition(...)` 是传送方法, 所以不要在 `OnUpdate` 循环内调用它 (§1-6).

---

## 14. 需要自定义实现

增益/减益 · BT 装饰器/记忆(黑板) · 仇恨/威胁表 · 弹道池 · 穿刺/最大击中 · 晃动等级系统 · 资源 (MP/耐力/狂怒) · 组合/取消窗口 · 防御/格挡 · 世界→屏幕坐标转换 · 世界空间 HP 条

---

## 不在范围内

- 一般玩家主题 (HP/移动/摄像机/服装除外): [`msw-defaultplayer`](../msw-defaultplayer/SKILL.md)
- 一般 mlua 语法/生命周期: [`msw-scripting`](../msw-scripting/SKILL.md)
- `.model` 作者规则/模板: [`msw-general`](../msw-general/SKILL.md)
