# 提炼指南

本指南涵盖从现有代码库中提取 Allium 规格的过程。核心挑战与正向启发相同：找到合适的抽象级别。在启发过程中，你会在出现时过滤掉实现细节。在提炼过程中，你会过滤掉已经存在的实现细节。两者都需要关于领域级别什么才是重要的相同判断。

代码告诉你*如何*工作。规格捕捉*什么*它做以及*为什么*它重要。这项技能在于询问“利益相关者为什么关心这个？”以及“在保持系统相同的情况下，这个可以不同吗？”

## 交互模式

这项技能以两种模式运行。以下所有要求、提示或与用户验证的指令都遵循这些模式：

- **交互式** — 在对话中内联运行。直接询问用户并等待答案。
- **非交互式** — 作为 `distill` 子代理运行（例如在 Allium 循环内部），此时无法联系到用户。根据你获得的目标，界定提炼范围，不要猜测判断：将每个未确认的判断——预期行为与偶然行为、参与者身份、候选流程、范围排除——作为 `open question` 声明记录在提炼的规格中，并在最终输出中列出已暂停的问题。

## 界定提炼工作范围

在深入代码之前，确定你要指定什么。并非每一行代码都值得出现在规格中。

### 首先要问的问题

1. **“我们正在指定这个代码库的哪个子集？”**
   单一仓库通常包含多个不同的系统。你可能只需要一个服务的规格或一个领域的规格。在开始之前，明确界定边界。

2. **“我们应该故意排除哪些代码？”**
   - **遗留代码**：为向后兼容而保留的功能，但不是核心系统的一部分
   - **偶然代码**：非领域级别的支持基础设施（日志记录、指标、部署）
   - **已弃用的路径**：计划移除的代码
   - **实验性功能**：通过功能标志，尚未成为设计决策

3. **“谁拥有这个规格？”**
   不同的团队可能拥有单一仓库的不同部分。每个团队的规格应专注于他们的领域。

### “我们会重新构建这个吗？”测试

对于你遇到的任何代码路径，问：“如果我们从头开始重新构建这个系统，这个会出现在需求中吗？”

- 是：包含在规格中
- 否，它是遗留代码：排除
- 否，它是基础设施：排除
- 否，它是临时解决方案：排除（但要注意它解决的底层需求）

### 记录范围决策

在提炼的规格顶部，记录包含和排除的内容：

```
-- allium: 3
-- interview-scheduling.allium

-- 范围：仅面试调度流程
-- 包含：Candidacy, Interview, InterviewSlot, Invitation, Feedback
-- 排除：
--   - 用户认证（使用 auth 库规格）
--   - 分析/报告（单独的规格）
--   - 遗留 V1 API（已弃用，不指定）
--   - Greenhouse 同步（使用 greenhouse 库规格）
```

版本标记 (`-- allium: N`) 必须是每个 `.allium` 文件的第一行。使用当前的语种版本号。

## 找到合适的抽象级别

提炼和启发共享同一个基本挑战：选择要包含的内容。以下测试适用于两个方向，无论你是听到利益相关者描述功能还是阅读实现它的代码。

### “为什么”测试

对于代码中的每个细节，问：“利益相关者为什么关心这个？”

| 代码细节 | 为什么？ | 包含？ |
|-------------|------|----------|
| 邀请在 7 天后过期 | 影响候选人体验 | 是 |
| 令牌是 32 字节 URL 安全的 | 安全实现 | 否 |
| 会话存储在 Redis 中 | 性能选择 | 否 |
| 使用 PostgreSQL JSONB | 数据库实现 | 否 |
| 提供槽状态更改为 'proposed' | 影响候选人看到的内容 | 是 |
| 邀请接受时发送电子邮件 | 沟通需求 | 是 |

如果你无法说明利益相关者为什么关心，那它很可能是实现细节。

### “这可以不同吗？”测试

问：“这个可以在保持系统相同的情况下以不同的方式实现吗？”

- 如果是：很可能是实现细节，将其抽象化
- 如果不是：很可能是领域级别的，包含它

| 细节 | 可以不同吗？ | 包含？ |
|--------|---------------------|----------|
| `secrets.token_urlsafe(32)` | 是，任何安全的令牌生成 | 否 |
| 7 天邀请过期 | 否，这是设计决策 | 是 |
| PostgreSQL 数据库 | 是，任何数据库 | 否 |
| "待处理, 确认, 完成" 状态 | 否，这是工作流 | 是 |

### “模板与实例”测试

这是一个**类别**的东西，还是一个**特定实例**？

| 实例（通常是实现） | 模板（通常是领域级别） |
|--------------------------------|-------------------------------|
| Google OAuth | 身份验证提供者 |
| Slack webhook | 通知渠道 |
| SendGrid API | 电子邮件交付 |
| `timedelta(hours=3)` | 确认截止日期 |

有时实例就是领域关注点。见“具体细节问题”下面。

## 提炼思维方式

### 代码是过度指定的

每一行代码都可能做出在领域级别可能不重要的决策：

```python
# 代码告诉你：
def send_invitation(candidate_id: int, slot_ids: List[int]) -> Invitation:
    candidate = db.session.query(Candidate).get(candidate_id)
    slots = db.session.query(InterviewSlot).filter(
        InterviewSlot.id.in_(slot_ids),
        InterviewSlot.status == 'confirmed'
    ).all()

    invitation = Invitation(
        candidate_id=candidate_id,
        token=secrets.token_urlsafe(32),
        expires_at=datetime.utcnow() + timedelta(days=7),
        status='pending'
    )
    db.session.add(invitation)

    for slot in slots:
        slot.status = 'proposed'
        invitation.slots.append(slot)

    db.session.commit()

    send_email(
        to=candidate.email,
        template='interview_invitation',
        context={'invitation': invitation, 'slots': slots}
    )

    return invitation
```

```
-- 规格应该说明：
rule SendInvitation {
    when: SendInvitation(candidacy, slots)

    requires: slots.all(s => s.status = confirmed)

    ensures:
        for s in slots:
            s.status = proposed
    ensures: Invitation.created(
        candidacy: candidacy,
        slots: slots,
        expires_at: now + 7.days,
        status: pending
    )
    ensures: Email.created(
        to: candidacy.candidate.email,
        template: interview_invitation
    )
}
```

我们丢弃的内容：
- `candidate_id: int` 变成了 `candidacy`
- `db.session.query(...)` 变成了关系遍历
- `secrets.token_urlsafe(32)` 完全移除（令牌是实现）
- `datetime.utcnow() + timedelta(...)` 变成了 `now + 7.days`
- `db.session.add/commit` 由 `created` 暗示
- `invitation.slots.append(slot)` 由关系暗示

### 询问“产品所有者会关心吗？”

对于代码中的每个细节，问：

| 代码细节 | 产品所有者关心？ | 包含？ |
|-------------|---------------------|----------|
| 邀请在 7 天后过期 | 是，影响候选人体验 | 是 |
| 令牌是 32 字节 URL 安全的 | 否，安全实现 | 否 |
| 使用 SQLAlchemy ORM | 否，持久化机制 | 否 |
| 电子邮件模板名称 | 也许，如果模板是设计决策 | 也许 |
| 提供槽状态更改为 'proposed' | 是，影响候选人看到的内容 | 是 |
| 数据库事务提交 | 否，实现细节 | 否 |

### 区分手段与目的

**手段**：代码如何实现某事。
**目的**：系统需要的结果。

| 手段（代码） | 目的（规格） |
|--------------|-------------|
| `requests.post('https://slack.com/api/...')` | `Notification.created(channel: slack)` |
| `candidate.oauth_token = google.exchange(code)` | `Candidate authenticated` |
| `redis.setex(f'session:{id}', 86400, data)` | `Session.created(expires: 24.hours)` |
| `for slot in slots: slot.status = 'cancelled'` | `for s in slots: s.status = cancelled` |

有时，实例就是领域关注点。见“具体细节问题”下面。

## 提炼过程

提炼会读取大量代码，但生成的规格很小。昂贵的错误是让所有这些源代码堆积在一个上下文中，在每次回合中重新读取。保持工作集精简：将读取密集的步骤作为子代理进行编排，并仅保留其提炼输出。

### 编排模型

对于超过少量文件的情况，不要自己读取整个代码库。相反：

1. **映射**代码库到有界上下文——轻扫（步骤 1），而不是深入阅读。
2. **发散**。为每个有界上下文生成一个子代理。每个子代理只读取其切片并返回*提炼片段*——草拟实体（状态 + 转换边）、草拟规则（触发 / 需要 / 确保）、外部边界、参与者以及配置——每个带有 `file:line` 证据。子代理返回规格片段和证据，而不是原始源代码。为每个子代理提供其目标路径，共享实体词汇表（以便上下文就名称达成一致），以及步骤 2–5 中的提取指导；要求紧凑片段，而不是散文评论。
3. **组装**。你，作为编排者，只持有地图和返回的片段——不是源代码。将片段合并成一个规格：合并跨切实体（`Email`, `Notification`, `AuditLog`），协调术语（每个概念只有一个名称，见挑战参考），并解决跨上下文引用。
4. **抽象和验证**组装的规格（步骤 6–7）。

为什么这很重要：原始源代码永远不会堆积在你的上下文中，因此不会被重复处理回合。每个子代理的切片一旦返回就会被丢弃。你仍然读取每一行相关代码——只是不是一次全部读取，也不是重复读取。结果是相同的规格，但使用的 token 更少。

对于真正小的代码库（少量文件），发散的开销不值得——直接读取并应用步骤 1–7。

### 步骤 1：绘制地图

扫描——不要深入阅读——以将代码库划分为有界上下文和共享词汇表，并规划发散。识别：

1. **入口点。** API 路由、CLI 命令、消息处理器、计划任务。
2. **领域模型。** 通常在 `models/`, `entities/`, `domain/`。
3. **业务逻辑。** 服务、用例、处理器。
4. **外部集成。** 它与哪些第三方通信？
5. **有界上下文。** 将上述内容组合成连贯的切片（按模块、包或功能区域划分）——这些将成为发散的单位。注意出现在多个切片中的实体；它们是每个子代理必须一致使用的共享词汇。

创建一个粗略的地图：
```
入口点:
  - API: /api/candidates/*, /api/interviews/*, /api/invitations/*
  - Webhooks: /webhooks/greenhouse, /webhooks/calendar
  - Jobs: send_reminders, expire_invitations, sync_calendars

模型:
  - Candidate, Interview, InterviewSlot, Invitation, Feedback

服务:
  - SchedulingService, NotificationService, CalendarService

集成:
  - Google Calendar, Slack, Greenhouse, SendGrid

有界上下文（发散单位）:
  - scheduling: Interview, InterviewSlot (SchedulingService, /api/interviews)
  - invitations: Invitation, Feedback (/api/invitations, expire job)
  - intake: Candidate (Greenhouse webhook) — 外部
共享实体: Candidate, Interview (出现在不同上下文中)
```

步骤 2–5 是**每个发散子代理应用于其切片的提取指导**（对于小代码库，你可以直接应用）。将它们与每个子代理的目标路径和共享词汇表一起交给每个子代理；收集片段并按照编排模型组装。

### 步骤 2：提取实体状态

查看枚举字段和状态列：

```python
class Invitation(Base):
    status = Column(Enum('pending', 'accepted', 'declined', 'expired'))
```

变成：
```
entity Invitation {
    status: pending | accepted | declined | expired
}
```

查找枚举定义、状态或状态列、常量（如 `STATUS_PENDING = 'pending'`）以及状态机库（例如 `transitions`, `django-fsm`）。

### 步骤 2.5：识别候选流程

提取实体及其状态后，扫描查找暗示端到端流程的状态机。跟踪每个状态值在代码库中的设置位置（`status = 'interviewing'` 发生在哪里？）。向用户展示候选流程以供验证：“我看到一个具有状态 `applied → screening → interviewing → deciding → hired/rejected` 的实体。系统是否旨在支持此流程？”

还跟踪跨实体数据流。如果一个规则在实体 A 中需要实体 B 的字段，请跟踪链：实体 B 的字段是如何设置的，以及什么触发了它？向用户展示链：“雇佣决策需要 `background_check.status = clear`。这由 webhook 处理器在 `/api/webhooks/background-check` 设置。这个链看起来对吗？”

从提取的规则生成转换图。图是代码的导出视图。如果它有间隙（没有出站转换的状态，且不是终端状态），则将其标记为潜在问题。

### 步骤 3：提取转换

查找状态变化发生的位置：

```python
def accept_invitation(invitation_id: int, slot_id: int):
    invitation = get_invitation(invitation_id)

    if invitation.status != 'pending':
        raise InvalidStateError()
    if invitation.expires_at < datetime.utcnow():
        raise ExpiredError()

    slot = get_slot(slot_id)
    if slot not in invitation.slots:
        raise InvalidSlotError()

    invitation.status = 'accepted'
    slot.status = 'booked'

    # 释放其他槽位
    for other_slot in invitation.slots:
        if other_slot.id != slot_id:
            other_slot.status = 'available'

    # 创建面试
    interview = Interview(
        candidate_id=invitation.candidate_id,
        slot_id=slot_id,
        status='scheduled'
    )

    notify_interviewers(interview)
    send_confirmation_email(invitation.candidate, interview)
```

提取：
```
rule CandidateAcceptsInvitation {
    when: CandidateAccepts(invitation, slot)

    requires: invitation.status = pending
    requires: invitation.expires_at > now
    requires: slot in invitation.slots
    ...

    ensures: invitation.status = accepted
    ensures: slot.status = booked
    ensures:
        for s in invitation.slots:
            if s != slot: s.status = available
    ensures: Interview.created(
        candidacy: invitation.candidacy,
        slot: slot,
        status: scheduled
    )
    ensures: Notification.created(to: slot.interviewers, ...)
    ensures: Email.created(to: invitation.candidate.email, ...)
}
```

**关键提取模式：**

| 代码模式 | 规格模式 |
|--------------|--------------|
| `if x.status != 'pending': raise` | `requires: x.status = pending` |
| `if x.expires_at < now: raise` | `requires: x.expires_at > now` |
| `if item not in collection: raise` | `requires: item in collection` |
| `x.status = 'accepted'` | `ensures: x.status = accepted` |
| `Model.create(...)` | `ensures: Model.created(...)` |
| `send_email(...)` | `ensures: Email.created(...)` |
| `notify(...)` | `ensures: Notification.created(...)` |

代码中发现的断言、检查和验证可能映射到具有表达式的不变式，而不是规则的前置条件。考虑它们是否描述了系统级属性或规则特定的守卫。

### 步骤 4：查找时间触发器

查找计划任务和时间逻辑：

```python
# 在 celery 任务或 cron 任务中
@app.task
def expire_invitations():
    expired = Invitation.query.filter(
        Invitation.status == 'pending',
        Invitation.expires_at < datetime.utcnow()
    ).all()

    for invitation in expired:
        invitation.status = 'expired'
        for slot in invitation.slots:
            slot.status = 'available'
        notify_candidate_expired(invitation)

@app.task
def send_reminders():
    upcoming = Interview.query.filter(
        Interview.status == 'scheduled',
        Interview.slot.time.between(
            datetime.utcnow() + timedelta(hours=1),
            datetime.utcnow() + timedelta(hours=2)
        )
    ).all()

    for interview in upcoming:
        send_reminder_notification(interview)
```

提取：
```
rule InvitationExpires {
    when: invitation: Invitation.expires_at <= now
    requires: invitation.status = pending

    ensures: invitation.status = expired
    ensures:
        for s in invitation.slots:
            s.status = available
    ensures: CandidateInformed(candidate: invitation.candidate, about: invitation_expired)
}

rule InterviewReminder {
    when: interview: Interview.slot.time - 1.hour <= now
    requires: interview.status = scheduled

    ensures: Notification.created(to: interview.interviewers, template: reminder)
}
```

### 步骤 5：识别外部边界

查找第三方 API 调用、webhook 处理器、导入/导出函数，以及读取但从未写入（或反之）的数据。

这些通常指示外部实体：

```python
# 候选人数据来自 Greenhouse，我们不会创建它
def import_from_greenhouse(webhook_data):
    candidate = Candidate.query.filter_by(
        greenhouse_id=webhook_data['id']
    ).first()

    if not candidate:
        candidate = Candidate(greenhouse_id=webhook_data['id'])

    candidate.name = webhook_data['name']
    candidate.email = webhook_data['email']
```

建议：
```
external entity Candidate {
    name: String
    email: String
}
```

当重复的接口模式出现在服务边界时（例如，多个消费者期望相同的序列化契约），这些建议使用 `contract` 声明进行重用，而不是重复的内部义务块。

### 步骤 5.5：从认证模式中识别参与者

提取实体后，通过检查认证和授权模式来识别参与者。不同的认证上下文建议不同的参与者：

- API 密钥认证 → 系统参与者（外部服务）
- 基于角色的访问 (`user.role == 'admin'`) → 每个角色都有不同的参与者
- 范围访问 (`user.org_id == resource.org_id`) → 带有 `within` 范围的参与者
- 未认证的端点 → 面向公众的参与者或系统 webhook

询问用户以确认：“此端点需要管理员角色认证。‘Admin’是一个不同的参与者，还是这与普通用户具有提升权限的相同的人？”

### 步骤 6：组装和抽象

如果你发散了，首先将返回的片段组装成一个规格：收集每个实体、规则、边界和配置值；合并跨切实体并协调术语，以便每个概念只有一个名称（两个上下文以不同名称命名的概念必须现在统一——见下面的“重复术语挑战”）。然后对组装的规格进行一次遍历以移除实现细节。

**之前（过于具体）：**
```
entity Invitation {
    candidate_id: Integer
    token: String(32)
    created_at: DateTime
    expires_at: DateTime
    status: pending | accepted | declined | expired
}
```

**之后（领域级别）：**
```
entity Invitation {
    candidacy: Candidacy
    created_at: Timestamp
    expires_at: Timestamp
    status: pending | accepted | declined | expired

    is_expired: expires_at <= now
}
```

更改：
- `candidate_id: Integer` 变成了 `candidacy: Candidacy`（关系，不是 FK）
- `token: String(32)` 移除（实现）
- `DateTime` 变成了 `Timestamp`（领域类型）
- 添加派生的 `is_expired` 以便清晰

配置值派生自其他配置值（例如 `extended_timeout = base_timeout * 2`）应使用限定引用或表达式形式的默认值在配置块中，而不是独立的字面值。

### 步骤 7：与利益相关者验证

提取的规格是一个假设。与利益相关者验证它：

1. **向原始开发人员展示规格。** “这是系统做什么？”
2. **向利益相关者展示。** “这是系统应该做什么？”
3. **查找差距。** 代码通常有错误或缺失的功能；规格可能会揭示它们。

常见发现：
- “哦，那个重试逻辑是一个临时方案，我们应该移除它”
- “实际上我们想要 X 但从未构建它”
- “这两个代码路径应该是相同的，但并不相同”

在运行进一步的检查之前，阅读 [评估规格](../allium/references/assessing-specs.md) 以评估提炼规格的成熟度。这告诉你是否规格已准备好进行流程级分析或仍需要结构化工作。

如果 Allium CLI 可用，在提炼的规格上运行 `allium check` 以捕获结构问题，然后 `allium analyse` 以识别流程级差距。`analyse` 的发现可以驱动验证问题：“提炼的规格有一个规则需要 `background_check.status = clear` 但没有捕获背景检查结果的表面。这部分代码我们是否未查看？” 参考 [行动发现](../allium/references/actioning-findings.md) 了解如何将检查发现转化为领域问题。

## 识别库规格候选

在提炼过程中，保持警惕，注意实现通用集成模式的代码，而不是特定于应用程序的逻辑。这些应该属于库规格。见 [识别库规格机会](../elicit/references/library-spec-signals.md) 以获取完整的决策框架（要问的问题，如何处理，常见提取）。

### 代码中的信号

查找以下模式，这些模式建议库规格：

**第三方集成模块：**
```python
class StripeWebhookHandler:
    def handle_invoice_paid(self, event):
        ...

class GoogleOAuthProvider:
    def exchange_code(self, code):
        ...
```

**配置驱动的集成：**
```python
OAUTH_CONFIG = {
    'google': {'client_id': ..., 'scopes': ...},
    'microsoft': {'client_id': ..., 'scopes': ...},
}
```

**具有特定提供者的通用模式**：OAuth 流程、支付处理、电子邮件交付、日历同步、ATS 集成、文件存储。

### 警报：集成逻辑在规格中

如果你发现自己在编写如下规格，请停止并重新考虑：

```
-- 太详细 - 这是 Stripe 的领域，而不是你的
rule ProcessStripeWebhook {
    when: WebhookReceived(payload, signature)
    requires: verify_stripe_signature(payload, signature)
    let event = parse_stripe_event(payload)
    if event.type = "invoice.paid":
        ...
}
```

相反：
```
-- 应用程序响应支付事件（集成由其他地方处理）
rule PaymentReceived {
    when: stripe/InvoicePaid(invoice)
    ...
}
```

见 [patterns.md Pattern 8](../allium/references/patterns.md) 以获取集成库规格的详细示例。

## 常见提炼挑战

### 挑战：重复术语

当你发现两个术语表示同一个概念（跨规格、在规格内或代码与规格之间）时，将其视为一个阻止问题。

```
-- 坏的：承认重复而不解决它
-- Order vs Purchase
-- checkout.allium 使用 "Purchase" - 这些是等效的概念.
```

这不是解决方案。当代码库的不同部分针对不同的规格构建时，两者都会出现在实现中：重复的模型、冗余的连接表、双向外键。

**要做什么：**
- 选择一个术语。在决定之前，交叉引用相关规格。
- 更新所有引用。不要将旧术语保留在评论或“另见”笔记中。
- 在变更日志中记录重命名，而不是在规格本身中。

**警告标志在代码中：**
- 两个表示相同概念的模型 (`Order` 和 `Purchase`)
- 连接表两者 (`order_items`, `purchase_items`)
- 评论如“等效于 X”或“相同于 Y”

你提取的规格必须选择一个术语。将另一个标记为技术债务以移除。

### 挑战：隐式状态机

代码通常具有未建模的隐式状态：

```python
# 没有显式状态字段，但这里隐藏了一个状态机
class FeedbackRequest:
    interview_id = Column(Integer)
    interviewer_id = Column(Integer)
    requested_at = Column(DateTime)
    reminded_at = Column(DateTime, nullable=True)
    feedback_id = Column(Integer, nullable=True)  # FK to Feedback 如果提交
```

隐式状态是：
- `pending`：`requested_at` 设置，`feedback_id` 为空，`reminded_at` 为空
- `reminded`：`reminded_at` 设置，`feedback_id` 为空
- `submitted`：`feedback_id` 设置

提取为显式：
```
entity FeedbackRequest {
    interview: Interview
    interviewer: Interviewer
    requested_at: Timestamp
    reminded_at: Timestamp?
    status: pending | reminded | submitted
}
```

### 挑战：分散的逻辑

同一个概念规则可能分布在多个地方：

```python
# 在 API 处理器中
def accept_invitation(request):
    if invitation.status != 'pending':
        return error(400, "Already responded")
    ...

# 在模型中
class Invitation:
    def can_accept(self):
        return self.expires_at > datetime.utcnow()

# 在服务中
def process_acceptance(invitation, slot):
    if slot not in invitation.slots:
        raise InvalidSlot()
    ...
```

合并成一个规则：
```
rule CandidateAccepts {
    when: CandidateAccepts(invitation, slot)

    requires: invitation.status = pending
    requires: invitation.expires_at > now
    requires: slot in invitation.slots
    ...
}
```

### 挑战：遗留代码和历史事故

代码库会累积已构建但从未使用的功能、用于解决已修复错误的临时解决方案以及从未执行的代码路径。

不要将这些包含在规格中。如果你不确定：
1. 检查代码是否实际上可以访问
2. 询问开发人员这是否有意为之
3. 检查 git 历史记录以获取上下文

### 挑战：缺失错误处理

代码可能无声失败或具有不完整的错误处理：

```python
def send_notification(user, message):
    try:
        slack.send(user.slack_id, message)
    except SlackError:
        pass  # 无声地忽略失败
```

规格应捕获预期行为，而不是错误：
```
ensures: Notification.created(to: user, channel: slack)
```

当前实现是否正确处理失败是分开于系统应该做什么的。

### 挑战：过度设计的抽象

企业代码库通常具有抽象层，掩盖了意图：

```java
public interface NotificationStrategy {
    void notify(NotificationContext context);
}

public class SlackNotificationStrategy implements NotificationStrategy {
    @Override
    public void notify(NotificationContext context) {
        // 实际的 Slack 调用埋藏了 5 层深
    }
}
```

切到实际行为。规格不需要策略模式、依赖注入或抽象工厂。只是：`ensures: Notification.created(channel: slack, ...)`

## 检查清单：你抽象得足够吗？

在最终确定提炼的规格之前：

- [ ] 没有数据库列类型 (Integer, VARCHAR 等)
- [ ] 没有ORM或查询语法
- [ ] 没有HTTP状态码或API路径
- [ ] 没有框架特定概念（中间件、装饰器等）
- [ ] 没有编程语言类型 (int, str, List 等)
- [ ] 没有代码中的变量名（使用领域术语）
- [ ] 没有基础设施 (Redis, Kafka, S3 等)
- 外键替换为关系
- [ ] 移除令牌/秘密（身份的实现）
- [ ] 时间戳使用领域 Duration，而不是 timedelta/seconds

如果任何内容仍然存在，询问：“利益相关者会在需求文档中包含这个吗？”

## 检查清单：术语一致性

- [ ] 规格中每个概念只有一个名称
- [ ] 没有“也称为”或“等效于”评论
- [ ] 交叉引用相关规格以解决冲突术语
- [ ] 代码中的重复模型标记为技术债务以移除

## 提炼之后

提取的规格是一个起点。如果提炼揭示了需要结构化发现的差距（不明确的需​​求、复杂的实体关系、未声明的业务规则），使用 `elicit` 技能来填补它们。对于需求演变时的定向更改，使用 `tend` 技能。对于检查持续对齐规格与实现之间的一致性，使用 `weed` 技能。

## 带有类型结果（循环手递手）

当作为 Allium 循环内的 `distill` 子代理运行时，以单个符合 [distill-result.schema.json](../allium/references/schemas/distill-result.schema.json) 的 JSON 对象返回结果，并且别无他物：`spec_path`, `open_questions`, 和关于规格涵盖内容的简短 `summary`. 发射每个字段，使用 `[]` 表示空列表。你读取的源代码保留在调用者的上下文中；只有这些字段返回。交互式运行时，以散文形式呈现你的发现——类型记录是用于机器手递手，而不是对话。

```json
{
  "phase": "distill",
  "spec_path": "giftcard.allium",
  "open_questions": ["强制重置超额余额为零是故意还是偶然?"],
  "summary": "礼品卡兑换和状态生命周期"
}
```

## 参考

- [语言参考](../allium/references/language-reference.md), 完整 Allium 语法
- [评估规格](../allium/references/assessing-specs.md), 如何评估规格成熟度并选择合适的分析级别
- [行动发现](../allium/references/actioning-findings.md), 将检查发现转化为领域问题
- [示例](./references/worked-examples.md), 完整代码到规格示例，Python, TypeScript 和 Java
