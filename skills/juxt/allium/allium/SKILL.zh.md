---
name: allium
description: 给你的AI代理比提示更有用的东西。通过清晰度实现高效。
---

# Allium

Allium 是一种用于在领域层面捕捉软件行为的正式语言。它位于非正式功能描述和实现之间，提供了一种精确的方式来指定软件做什么，而不是规定它是如何构建的。

其名称来源于包含洋葱和香葱的植物科，延续了由 Cucumber 和 Gherkin 建立的行为规范工具的传统。

主要原则：

- 描述可观察的行为，而不是实现
- 捕获在行为层面重要的领域逻辑
- 生成集成和端到端测试（不是单元测试）
- 在实现之前将歧义公开化
- 与实现无关：相同的规范可以用任何语言实现

Allium 不指定编程语言或框架选择、数据库模式或存储机制、API 设计或 UI 布局，或内部算法（除非它们是领域层面的关注点）。

## 路由表

| 任务 | 工具 | 时间 |
|------|------|------|
| 编写或读取 `.allium` 文件 | 此技能 | 您需要语言语法和结构 |
| 通过对话构建规范 | `elicit` 技能 | 用户描述他们想要构建的功能或行为 |
| 从现有代码中提取规范 | `distill` 技能 | 用户已有实现代码，并希望从中获取规范 |
| 修改现有规范 | `tend` 技能 | 用户希望对 `.allium` 文件进行有针对性的修改 |
| 检查规范与代码的一致性 | `weed` 技能 | 用户希望找到或修复规范与实现之间的差异 |
| 从规范生成测试 | `propagate` 技能 | 用户希望从规范生成测试、PBT 属性或状态机测试 |
| 证实循环的收敛性 | `witness` 技能 | 用户希望独立确认运行收敛性声明——测试确实通过，没有生成的测试被削弱，没有阻塞问题被无声地搁置 |
| 驱动整个循环收敛 | 此技能（见 [驱动循环](./references/driving-the-loop.md)） | 用户希望构建或协调功能端到端——`/allium <目标>` 会自主运行收集→执行→验证→重复循环，直到规范、测试和代码达成一致 |

## 响应 `/allium`（循环优先）

`/allium` 是入口点。倾向于自主路径——整个循环的价值正是偶尔使用单个技能所错过的：

- **清晰的单一任务** → 直接路由到该技能（根据路由表）；不要让用户在菜单中摸索。
- **目标或功能**（例如 "添加礼品卡"、"让密码重置功能正常工作"）→ 自己驱动整个循环端到端，而不是运行一个阶段。遵循 [驱动循环](./references/driving-the-loop.md)。
- **空或模糊** → 引导用户循环优先：提供驱动循环作为默认选项，然后列出单个技能作为控制路径，每个技能附有一行提示，并建议从项目状态中提供一个具体的起点（现有的 `.allium` 规范？有代码但没有规范？需要调整以协调？）。例如：

  > 告诉我一个目标，我会驱动整个循环——规范→测试→代码，直到它们达成一致。或者自己运行一个步骤：`elicit`（从意图获取规范）、`distill`（从现有代码获取规范）、`propagate`（从规范生成测试）、`tend`（编辑规范）、`weed`（修复规范↔代码漂移）。你有代码但没有 `.allium`，所以我建议先蒸馏——或者直接给我目标，我会端到端处理。

以循环为先导；将单个技能保持在一个步骤之外，供希望手动控制的用户使用。一旦单个技能完成，就应主动建议下一阶段，而不是等待被询问。

## Allium 循环（推荐顺序）

这些技能不是一次性命令；它们组合成一个自主风格的循环——**收集上下文→执行操作→验证→重复**——驱动三个工件达成一致：**规范**（意图）、**测试**（契约）和**代码**（实现）。使用 `/elicit` 或 `/distill` 收集上下文（规范是持久的上下文）；使用 `/propagate` 然后执行实现（在规范优先的工作中，先确认新测试失败——在你实现之前已经绿色的测试已经是覆盖或空洞的）；通过运行测试、然后 `/weed`、然后 CLI 结构性检查来验证；重复直到收敛。验证是最重要的阶段，规范加测试加 weed 信号使循环值得信赖。调用一个技能后，应主动建议下一步，而不是等待被询问。要一次性运行整个循环直到收敛，只需给 `/allium` 一个目标——它会为你驱动循环，遵循 [驱动循环](./references/driving-the-loop.md)。

两个入口点，一个收敛循环：

- **规范优先（正向，从意图）**：`/elicit` → `/propagate` → 实现 → `/weed`；当需求变化时，使用 `/tend` 然后重新 `/propagate`。
- **代码优先（反向，从现有代码）**：`/distill` → 审查预期行为与意外行为 → `/propagate` → 运行代码上的测试 → `/weed` 以协调 → 按区域重复。

当测试通过、`/weed` 报告无差异、无未解决的问题剩余（对于代码优先，一个新鲜的 `/distill` 找不到新内容），并且一个独立的 `/witness` 通过证实该声明与真实情况一致时，工作就完成了。循环期间有两个基本原则：永不削弱生成的测试以使其通过（改为修复规范并重新 propagate），将真正的歧义升级给人类而不是猜测——两者都由 witness 在收敛门处强制执行，而不是依赖信任。

实现本身是常规编码——Allium 生成规范和测试，而不是应用程序代码。有关完整演练、图表、退出条件和实现提示，请参阅 [推荐循环](./references/recommended-loops.md) 参考文档。

## 快速语法总结

### 实体

```
实体 Candidacy {
    -- 字段
    candidate: Candidate
    role: Role
    status: pending | active | completed | cancelled   -- 内联枚举
    retry_count: Integer

    -- 关系
    invitation: Invitation with candidacy = this         -- 一对一
    slots: InterviewSlot with candidacy = this           -- 一对多

    -- 投影
    confirmed_slots: slots where status = confirmed
    pending_slots: slots where status = pending

    -- 派生
    is_ready: confirmed_slots.count >= 3
    has_expired: invitation.expires_at <= now
}
```

### 外部实体

```
外部实体 Role { title: String, required_skills: Set<Skill>, location: Location }
```

### 值类型

```
值 TimeRange { start: Timestamp, end: Timestamp, duration: end - start }
```

### 混合类型

基本实体声明一个区分字段，其首字母大写的值命名变体。变体使用 `variant` 关键字。

```
实体 Node {
    path: Path
    kind: Branch | Leaf              -- 区分字段
}

变体 Branch : Node {
    children: List<Node?>
}

变体 Leaf : Node {
    data: List<Integer>
    log: List<Integer>
}
```

小写管道值是枚举字面量（`status: pending | active`）。首字母大写的值是变体引用（`kind: Branch | Leaf`）。类型守卫（`requires:` 或 `if` 分支）将范围缩小到变体并解锁其字段。

### 模块给定

声明模块的规则操作的实体实例。所有规则继承这些绑定。并非每个模块都需要一个：由领域实体上的触发器作用域的规则从触发器获取实体。`given` 用于规范，其中规则操作存在于模块作用域中一次的共享实例。

```
given {
    pipeline: HiringPipeline
    calendar: InterviewCalendar
}
```

导入的模块实例通过限定名称访问（`scheduling/calendar`），并且不会出现在本地 `given` 块中。与表面 `context` 不同，后者为边界契约绑定参数化作用域。

### 规则

```
规则 InvitationExpires {
    当: invitation: Invitation.expires_at <= now
    需要: invitation.status = pending
    让 remaining = invitation.proposed_slots where status != cancelled
    确保: invitation.status = expired
    确保:
        对于 s 在 remaining:
            s.status = cancelled
    @指导
        -- 非规范性实现建议。
}
```

### 触发器类型

- **外部刺激**：`当: CandidateSelectsSlot(invitation, slot)` — 来自系统外部的操作
- **状态转换**：`当: interview: Interview.status transitions_to scheduled` — 实体状态改变（仅转换，不是创建）
- **状态变为**：`当: interview: Interview.status becomes scheduled` — 实体具有此值，无论是由创建还是转换
- **时间**：`当: invitation: Invitation.expires_at <= now` — 基于时间的条件（始终添加一个 `requires` 守卫以防止重新触发）
- **派生条件**：`当: interview: Interview.all_feedback_in` — 派生值变为真
- **实体创建**：`当: batch: DigestBatch.created` — 在创建新实体时触发
- **链式**：`当: AllConfirmationsResolved(candidacy)` — 订阅来自另一个规则的 ensures 子句的触发器发射
- **实体删除**：`not exists entity` — 断言实体不再存在

所有实体作用域的触发器使用显式的 `var: Type` 绑定。在名称不需要时使用 `_` 作为丢弃绑定：`当: _: Invitation.expires_at <= now`，`当: SomeEvent(_, slot)`。

### 规则级迭代

`for` 子句对集合中的每个元素应用规则体一次：

```
规则 ProcessDigests {
    当: schedule: DigestSchedule.next_run_at <= now
    对于 user 在 Users where notification_setting.digest_enabled:
        让 settings = user.notification_setting
        确保: DigestBatch.created(user: user, ...)
}
```

### 确保 模式

确保子句有四种结果形式：

- **状态变化**：`entity.field = value`
- **实体创建**：`Entity.created(...)` — 单一的规范创建动词
- **触发器发射**：`TriggerName(params)` — 为其他规则提供链式事件
- **实体删除**：`not exists entity` — 断言实体不再存在

这些形式与 `for` 迭代（`for x in collection: ...`）、`if`/`else` 条件语句和 `let` 绑定组合。

实体创建使用 `.created()` 唯一。领域含义存在于实体名称和规则名称中，而不是创建动词。

在状态变化赋值中，右侧表达式引用规则前字段值。确保块内的条件（`if` 守卫、创建参数、触发器发射参数）引用最终状态。

### 表面

```
表面 InterviewerDashboard {
    面对 viewer: Interviewer

    上下文分配: SlotConfirmation where interviewer = viewer

    暴露:
        分配.slot.time
        分配.status

    提供:
        InterviewerConfirmsSlot(viewer, 分配.slot)
            当 分配.status = pending

    相关:
        InterviewDetail(分配.slot.interview)
            当 分配.slot.interview != null
}
```

表面在边界处定义契约。`facing` 子句命名外部方，`context` 范围实体。其余子句无论边界是用户界面还是代码到代码，都使用单一词汇：`exposes`（可见数据，支持 `for` 迭代集合）、`provides`（可用操作带可选 `when` 守卫）、`contracts:`（引用模块级 `contract` 声明，带 `demands`/`fulfils` 方向标记）、`@guarantee`（关于边界的命名文本断言）、`@guidance`（非规范性建议）、`related`（从此表面可达的相关表面）、`timeout`（在表面上下文中应用的时序规则引用）。

`facing` 子句接受演员类型（带相应的 `actor` 声明和 `identified_by` 映射）或实体类型直接。当边界有特定身份要求时使用演员声明；当任何实例都可以交互时使用实体类型（例如 `facing visitor: User`）。对于外部方是代码的集成表面，声明一个演员类型，并使用最小的 `identified_by` 表达式。在 `identified_by` 表达式中引用 `within` 的演员必须声明预期的上下文类型：`within: Workspace`。

### 表面到实现的契约

`exposes` 块是字段级契约：实现返回这些字段，消费者使用这些字段。不要添加未列出的字段。不要省略已列出的字段。

### 契约

```allium
契约 Codec {
    serialize: (value: Any) -> ByteArray
    deserialize: (bytes: ByteArray) -> Any

    @不变量 Roundtrip
        -- deserialize(serialize(value)) 产生与原始值
        -- 相当的类型，适用于所有支持类型。
}
```

契约是模块级声明，在表面 `contracts:` 子句中按名称引用（`demands Codec`，`fulfils EventSubmitter`）。有关声明语法和引用规则，请参阅 [契约](./references/language-reference.md#contracts)。

### 表达式

导航：`interview.candidacy.candidate.email`，`reply_to?.author`（可选），`timezone ?? "UTC"`（空值合并）。集合：`slots.count`，`slot in invitation.slots`，`interviewers.any(i => i.can_solo)`，`for item in collection: item.status = cancelled`，`permissions + inherited`（集合联合），`old - new`（集合差集）。比较：`status = pending`，`count >= 2`，`status in {confirmed, declined}`，`provider not in providers`。布尔逻辑：`a and b`，`a or b`，`not a`，`a implies b`。

### 模块化规范

```
使用 "github.com/allium-specs/google-oauth/abc123def" 作为 oauth
```

限定名称引用跨规范的实体：`oauth/Session`。坐标是不可变的（git SHA 或内容哈希）。本地规范使用相对路径：`使用 "./candidacy.allium" 作为 candidacy`。

### 配置

```
配置 {
    invitation_expiry: Duration = 7.days
    max_login_attempts: Integer = 5
    extended_expiry: Duration = invitation_expiry * 2              -- 表达式形式默认
    sync_timeout: Duration = core/config.default_timeout           -- 配置参数引用
}
```

规则引用配置值作为 `config.invitation_expiry`。对于默认实体实例，使用 `default`。

### 默认值

```
默认 Role viewer = { name: "viewer", permissions: { "documents.read" } }
```

### 不变量

```allium
不变量 NonNegativeBalance {
    对于 account 在 Accounts:
        account.balance >= 0
}
```

带表达式的不变量（`不变量 Name { expression }`）断言实体状态上的属性。它们是逻辑断言，不是运行时检查。与契约中用 `@` 符号标记的内容（检查器不评估的内容）不同。有关不变量，请参阅 [不变量](./references/language-reference.md#invariants)。

### 状态转换图（v3）

```
实体 Order {
    status: pending | confirmed | shipped | delivered | cancelled

    转换 status {
        pending -> confirmed
        confirmed -> shipped
        shipped -> delivered
        pending -> cancelled
        confirmed -> cancelled
        终止: delivered, cancelled
    }
}
```

### 状态相关字段存在（v3）

```
实体 Order {
    status: pending | confirmed | shipped | delivered | cancelled
    customer: Customer
    total: Money
    tracking_number: String 当 status = shipped | delivered
    shipped_at: Timestamp 当 status = shipped | delivered

    转换 status {
        pending -> confirmed
        confirmed -> shipped
        shipped -> delivered
        pending -> cancelled
        confirmed -> cancelled
        终止: delivered, cancelled
    }
}
```

### 延迟规范

```
延迟 InterviewerMatching.suggest    -- 见：详细/interviewer-matching.allium
```

### 开放问题

```
开放问题 "管理员所有权 - 管理员是否应分配到特定角色？"
```

## 验证

当 `allium` 命令行界面（CLI）安装后，一个钩子会在每次写入或编辑后自动验证 `.allium` 文件。在展示结果之前，修复任何报告的问题。如果 CLI 不可用，请参考 [语言参考](./references/language-reference.md) 进行验证。

## 参考

- [语言参考](./references/language-reference.md) — 实体、规则、表达式、表面、合约、不变性和验证的完整语法
- [测试生成](./references/test-generation.md) — 从规范生成测试
- [推荐循环](./references/recommended-loops.md) — gather-context → take-action → verify → repeat 循环，包含先规范后代码和先代码后规范的演练
- [驱动循环](./references/driving-the-loop.md) — `/allium` 遵循的驱动目标收敛的程序（入口检测、时钟、停止条件、账本）
- [整合片段](./references/integrating-slices.md) — 扇形目标的 reduce 步骤：组装片段，使用 `allium analyse` 检查接缝，协调并见证整体
- [模式](./references/patterns.md) — 9 个已完成的模式：认证、RBAC、邀请、软删除、通知、使用限制、评论、库规范集成、框架集成合约
