---
name: distill
description: 从现有代码库中提取一个 Allium 规范。当用户已有代码并希望将行为提炼为规范、从实现中逆向工程规范、从代码生成规范、将实现转换为行为规范，或以 Allium 术语记录代码库所做之事时使用。
---

# 提炼指南

本指南涵盖从现有代码库中提取 Allium 规范的过程。核心挑战与正向获取信息相同：找到合适的抽象级别。在获取信息过程中，你会在出现时过滤掉实现层面的想法。在提炼过程中，你会过滤掉已经存在的实现细节。两者都需要对领域层面什么才是重要的做出同样的判断。

代码告诉你*如何*工作。规范则捕捉*做什么*以及*为什么*它重要。这项技能在于询问"利益相关者为什么关心这个？"以及"这个可以不同但系统仍然保持一致吗？"

## 交互模式

这项技能以两种模式运行。以下每个指令中，如果它询问、提示或使用用户进行验证，则遵循该模式：

- **交互式** — 在对话中内联运行。直接询问用户并等待答案。
- **非交互式** — 作为 `distill` 子代理运行（例如在 Allium 循环内部），此时无法接触用户。根据你获得的目标来界定提炼范围，不要猜测判断结果：将每个未确认的判断——预期行为与偶然行为、参与者身份、候选流程、范围排除——作为 `open question` 声明记录在提炼的规范中，并在最终输出中列出已挂起的疑问。

## 界定提炼工作范围

在深入代码之前，确定你要提炼什么。并非每一行代码都值得出现在规范中。

### 首先要问的问题

1. **"我们正在提炼代码库的哪个子集？"**
   单一仓库通常包含多个不同的系统。你可能只需要一个服务的规范或一个领域的规范。在开始之前，明确界定边界。

2. **"我们应该有意排除哪些代码？"**
   - **遗留代码**：为向后兼容而保留但不是核心系统的功能
   - **偶然代码**：不是领域层面的支持基础设施（日志记录、指标、部署）
   - **已弃用的路径**：计划移除的代码
   - **实验性功能**：通过功能标志，尚未成为设计决策

3. **"谁拥有这个规范？"**
   不同的团队可能拥有单一仓库的不同部分。每个团队的规范应专注于他们的领域。

### "我们会重新构建这个吗？"测试

对于遇到的任何代码路径，询问："如果我们从头开始构建这个系统，这个会出现在需求中吗？"

- 是：包含在规范中
- 否，它是遗留代码：排除
- 否，它是基础设施：排除
- 否，它是临时解决方案：排除（但注意它解决的底层需求）

### 记录范围决策

在提炼的规范顶部，记录包含和排除的内容：

```
-- allium: 3
-- interview-scheduling.allium

-- 范围：仅面试安排流程
-- 包含：Candidacy（候选人资格）、Interview（面试）、InterviewSlot（面试时段）、Invitation（邀请）、Feedback（反馈）
-- 排除：
--   - 用户认证（使用 auth 库规范）
--   - 分析/报告（单独的规范）
--   - 遗留 V1 API（已弃用，不进行规范）
--   - Greenhouse 同步（使用 greenhouse 库规范）
```

版本标记（`-- allium: N`）必须是每个 `.allium` 文件的第一行。使用当前的语种版本号。

## 找到合适的抽象级别

提炼和获取信息共享同一个基本挑战：选择要包含的内容。以下测试适用于两个方向，无论你是听取利益相关者描述功能还是阅读实现它的代码。

### "为什么"测试

对于代码中的每个细节，询问："利益相关者为什么关心这个？"

| 代码细节 | 为什么？ | 包含？ |
|-------------|------|----------|
| 邀请在 7 天后过期 | 影响候选人体验 | 是 |
| 令牌是 32 字节 URL 安全的 | 安全实现 | 否 |
| 会话存储在 Redis 中 | 性能选择 | 否 |
| 使用 PostgreSQL JSONB | 数据库实现 | 否 |
| 时段状态变为 'proposed' | 影响候选人看到的内容 | 是 |
| 邀请接受时发送电子邮件 | 沟通需求 | 是 |

如果你无法说明利益相关者会为什么关心，那它很可能是实现层面的。

### "可以不同吗"测试

询问："这个可以有不同的实现方式，同时系统仍然保持一致吗？"

- 如果是：很可能是实现细节，将其抽象化
- 如果不是：很可能是领域层面的，包含它

| 细节 | 可以不同吗？ | 包含？ |
|--------|---------------------|----------|
| `secrets.token_urlsafe(32)` | 是，任何安全的令牌生成 | 否 |
| 7 天邀请过期 | 否，这是设计决策 | 是 |
| PostgreSQL 数据库 | 是，任何数据库 | 否 |
| "Pending（待定）、Confirmed（已确认）、Completed（已完成）"状态 | 否，这是工作流 | 是 |

### "模板与实例"测试

这是一个**类别**的事物，还是一个**特定实例**？

| 实例（通常是实现层面） | 模板（通常是领域层面） |
|--------------------------------|-------------------------------|
| Google OAuth | 认证提供者 |
| Slack webhook | 通知渠道 |
| SendGrid API | 电子邮件发送 |
| `timedelta(hours=3)` | 确认截止时间 |

有时实例就是领域关注的重点。见下文"具体细节问题"。

## 提炼思维模式

### 代码是过度规范的

每一行代码都做出了可能在领域层面不重要的决策：

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
-- 规范应该说明：
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

我们移除的内容：
- `candidate_id: int` 变为 just `candidacy`
- `db.session.query(...)` 变为关系遍历
- `secrets.token_urlsafe(32)` 完全移除（令牌是实现的）
- `datetime.utcnow() + timedelta(...)` 变为 `now + 7.days`
- `db.session.add/commit` 由 `created` 暗示
- `invitation.slots.append(slot)` 由关系暗示

### 询问"产品负责人会关心吗？"

对于代码中的每个细节，询问：

| 代码细节 | 产品负责人会关心？ | 包含？ |
|-------------|---------------------|----------|
| 邀请在 7 天后过期 | 是，影响候选人体验 | 是 |
| 令牌是 32 字节 URL 安全的 | 否，安全实现 | 否 |
| 使用 SQLAlchemy ORM | 否，持久化机制 | 否 |
| 电子邮件模板名称 | 也许，如果模板是设计决策 | 也许 |
| 时段状态变为 'proposed' | 是，影响候选人看到的内容 | 是 |
| 数据库事务提交 | 否，实现细节 | 否 |

### 区分手段与目的

**手段**：代码如何实现某事。
**目的**：系统需要的结果。

| 手段（代码） | 目的（规范） |
|--------------|-------------|
| `requests.post('https://slack.com/api/...')` | `Notification.created(channel: slack)` |
| `candidate.oauth_token = google.exchange(code)` | `Candidate authenticated` |
| `redis.setex(f'session:{id}', 86400, data)` | `Session created(expires: 24.hours)` |
| `for slot in slots: slot.status = 'cancelled'` | `for s in slots: s.status = cancelled` |

## 具体细节问题

最难做出的判断：什么时候具体细节是领域的一部分，而不仅仅是实现？

### Google OAuth 示例

你发现这段代码：
```python
OAUTH_PROVIDERS = {
    'google': GoogleOAuthProvider(client_id=..., client_secret=...),
}

def authenticate(provider: str, code: str) -> User:
    return OAUTH_PROVIDERS[provider].authenticate(code)
```

**问题**："Google OAuth"是领域层面还是实现？

**如果是实现：**
- Google 只是选定的认证机制
- 可以被任何 OAuth 提供者替换
- 用户不会看到或关心哪个提供者
- 代码是通用的（提供者是参数）

**如果是领域层面：**
- 用户明确选择 Google（与 Microsoft 等）
- "使用 Google 登录"是一个功能
- 使用 Google 特定的范围或权限
- 支持多个提供者作为功能

**如何判断：**查看 UI 和用户流程。如果用户看到"使用 Google 登录"作为选择，它是领域层面的。如果他们只是看到"登录"，而 Google 恰好在其背后，它是实现的。

### 数据库选择示例

你发现 PostgreSQL 特定的代码：
```python
from sqlalchemy.dialects.postgresql import JSONB, ARRAY

class Candidate(Base):
    skills = Column(ARRAY(String))
    metadata = Column(JSONB)
```

**几乎总是实现。**规范应该说明：
```
entity Candidate {
    skills: Set<String>
    metadata: String?              -- 或模型特定字段
}
```

特定的数据库很少是领域层面的。例外：如果系统明确承诺 PostgreSQL 兼容性或特定的 PostgreSQL 功能给用户。

### 第三方集成示例

你发现 Greenhouse ATS 集成：
```python
class GreenhouseSync:
    def import_candidate(self, greenhouse_id: str) -> Candidate:
        data = self.client.get_candidate(greenhouse_id)
        return Candidate(
            name=data['name'],
            email=data['email'],
            greenhouse_id=greenhouse_id,
            source='greenhouse'
        )
```

**可能是：**

**实现如果：**
- Greenhouse 只是候选人可能来自的地方
- 可以被 Lever、Workable、Workable 等替换
- 集成是"候选人被导入"的实现细节

规范：
```
external entity Candidate {
    name: String
    email: String
    source: CandidateSource
}
```

**产品层面如果：**
- "Greenhouse 集成"是销售点
- 用户配置他们的 Greenhouse 连接
- 暴露 Greenhouse 特定功能（如将反馈同步回 Greenhouse）

规范：
```
external entity Candidate {
    name: String
    email: String
    greenhouse_id: String?  -- 明确建模
}

rule SyncFromGreenhouse {
    when: GreenhouseWebhookReceived(candidate_data)
    ensures: Candidate.created(
        ...
        greenhouse_id: candidate_data.id
    )
}
```

### "多个实现"启发式方法

查看代码库中的变化：

- 如果只有一个 OAuth 提供者，可能是实现
- 如果有多个 OAuth 提供者，可能是领域层面
- 如果只有一个通知渠道，可能是实现
- 如果有 Slack 和电子邮件和短信，可能是领域层面

多个实现的存在的变化本身是领域关注点。

## 提炼过程

提炼会阅读大量代码，但生成一个小型规范。昂贵的错误是让所有这些源代码堆积在一个上下文窗口中，在每次回合中重新读取。保持工作集精简：将读取密集的步骤作为子代理进行编排，并只保留它们的提炼输出。

### 编排模型

对于超过少量文件的情况，不要自己读取整个代码库。相反：

1. **映射**代码库到有界上下文——轻扫（步骤 1），不是深入阅读。
2. **发散。**为每个有界上下文生成一个子代理。每个子代理只读取其切片并返回*提炼片段*——草稿实体（状态+转换边）、草稿规则（触发/要求/确保）、外部边界、参与者配置——每个带有 `file:line` 证据。子代理返回规范片段和证据，而不是原始源代码。给每个子代理其目标路径、共享实体词汇表（以便上下文对名称达成一致），以及提取指导（步骤 2–5）；请求紧凑片段，而不是文本评论。
3. **组装。**你，作为编排者，只持有地图和返回的片段——不是源代码。将片段合并为一个规范：消除跨切实体（`Email`、`Notification`、`AuditLog`），统一术语（每个概念一个名称，见挑战参考），并解决跨上下文引用。
4. **抽象和验证**组装的规范（步骤 6–7）。

为什么这很重要：原始源代码永远不会积累在你的上下文中，因此不会被重复处理回合后；每个子代理的切片一旦返回就会被丢弃。你仍然会阅读每行相关代码——只是不会一次性全部读取，也不会重复读取。结果是相同的规范，但使用的 token 更少。

对于真正小的代码库（少量文件），发散的开销不值得——直接读取并应用步骤 1–7。

也追踪跨实体数据流。如果实体A的规则需要实体B的字段，请遵循链路：实体B的字段是在哪里设置的，什么触发了这个设置？呈现链路：“雇佣决定需要 `background_check_status = clear`。这是由 `/api/webhooks/background-check` 的 webhook 处理器设置的。这个链路看起来对吗？”

从提取的规则生成转换图。图是代码的派生视图。如果存在间隙（没有出站转换的终端状态），则将其标记为潜在问题。

### 第3步：提取转换

查找状态变化发生的地方：

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

    # 释放其他时间段
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
规则 CandidateAcceptsInvitation {
    当：CandidateAccepts(invitation, slot)

    需要：invitation.status = pending
    需要：invitation.expires_at > now
    需要：slot in invitation.slots

    确保：invitation.status = accepted
    确保：slot.status = booked
    确保：
        对于 s in invitation.slots:
            如果 s != slot: s.status = available
    确保：Interview.created(
        candidacy: invitation.candidacy,
        slot: slot,
        status: scheduled
    )
    确保：Notification.created(to: slot.interviewers, ...)
    确保：Email.created(to: invitation.candidate.email, ...)
}
```

**关键提取模式：**

| 代码模式 | 规范模式 |
|--------------|--------------|
| `if x.status != 'pending': raise` | `requires: x.status = pending` |
| `if x.expires_at < now: raise` | `requires: x.expires_at > now` |
| `if item not in collection: raise` | `requires: item in collection` |
| `x.status = 'accepted'` | `ensures: x.status = accepted` |
| `Model.create(...)` | `ensures: Model.created(...)` |
| `send_email(...)` | `ensures: Email.created(...)` |
| `notify(...)` | `ensures: Notification.created(...)` |

代码中发现的断言、检查和验证（例如 `assert balance >= 0`，类级验证器）可能映射到带表达式的不变式，而不是规则先决条件。考虑它们是否描述了系统级属性或特定规则的守卫。

### 第4步：查找时间触发器

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
规则 InvitationExpires {
    当：invitation: Invitation.expires_at <= now
    需要：invitation.status = pending

    确保：invitation.status = expired
    确保：
        对于 s in invitation.slots:
            s.status = available
    确保：CandidateInformed(candidate: invitation.candidate, about: invitation_expired)
}

规则 InterviewReminder {
    当：interview: Interview.slot.time - 1.hour <= now
    需要：interview.status = scheduled

    确保：Notification.created(to: interview.interviewers, template: reminder)
}
```

### 第5步：识别外部边界

查找第三方API调用、webhook处理器、导入/导出函数以及读取但从未写入（或反之）的数据。

这些通常表示外部实体：

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
外部实体 Candidate {
    name: String
    email: String
}
```

当重复的接口模式出现在服务边界时（例如，多个消费者期望相同的序列化契约），这表明应声明 `contract` 以供重用，而不是重复内联义务块。

### 第5.5步：从认证模式中识别参与者

在从API端点提取表面后，通过检查认证和授权模式来识别参与者。不同的认证上下文表示不同的参与者：

- API密钥认证 → 系统参与者（外部服务）
- 基于角色的访问控制 (`user.role == 'admin'`) → 每个角色一个参与者
- 范围访问控制 (`user.org_id == resource.org_id`) → 具有在 `within` 范围内的参与者
- 未认证端点 → 面向公众的参与者或系统webhook

要求用户确认：“此端点需要管理员角色认证。'Admin' 是一个独立的参与者，还是与普通用户具有提升权限的同一人？”

### 第6步：组装和抽象

如果你已经发散，首先将返回的片段组装成一个规范：收集每个实体、规则、边界和配置值；消除跨切实体并统一术语，以便每个概念只有一个名称（两个不同上下文命名相同的概念必须现在统一——见下面的“重复术语挑战”）。然后对组装的规范进行一次遍历，以移除实现细节。

**之前（过于具体）：**
```
实体 Invitation {
    candidate_id: Integer
    token: String(32)
    created_at: DateTime
    expires_at: DateTime
    status: pending | accepted | declined | expired
}
```

**之后（领域级）：**
```
实体 Invitation {
    candidacy: Candidacy
    created_at: Timestamp
    expires_at: Timestamp
    status: pending | accepted | declined | expired

    is_expired: expires_at <= now
}
```

变更：

- `candidate_id: Integer` 变为 `candidacy: Candidacy`（关系，不是外键）
- `token: String(32)` 移除（实现）
- `DateTime` 变为 `Timestamp`（领域类型）
- 添加派生的 `is_expired` 以提高清晰度

派生自其他配置值的配置值（例如 `extended_timeout = base_timeout * 2`）应在配置块中使用限定引用或表达式形式的默认值，而不是独立的字面值。

### 第7步：与利益相关者验证

提取的规范是一个假设。验证它：

1. **向原始开发人员展示规范。** “这是系统做什么？”
2. **向利益相关者展示。** “这是系统应该做什么？”
3. **查找间隙。** 代码中经常有错误或缺失的功能；规范可能会揭示它们。

常见发现：

- “哦，那个重试逻辑是一个临时解决方案，我们应该移除它”
- “实际上我们想要X，但我们从未构建它”
- “这两个代码路径应该是相同的，但实际上不是”

在运行进一步的检查之前，阅读 [评估规范](../allium/references/assessing-specs.md) 以评估派生规范的成熟度。这告诉您规范是否准备好进行过程级分析，还是仍需结构化工作。

如果 Allium CLI 可用，在派生规范上运行 `allium check` 以捕获结构化问题，然后运行 `allium analyse` 以识别过程级间隙。`analyse` 的发现可以驱动验证问题：“派生规范有一个要求 `background_check.status = clear` 的规则，但没有表面捕获背景检查结果。这是否由我们尚未查看的代码库部分处理？” 咨询 [处理发现](../allium/references/actioning-findings.md) 了解如何将发现转化为领域问题。

## 识别库规范候选者

在蒸馏过程中，保持警惕，查找实现通用集成模式而不是特定应用程序逻辑的代码。这些属于库规范。参见 [识别库规范机会](../elicit/references/library-spec-signals.md) 获取完整决策框架（要问的问题、如何处理、常见提取）。

### 代码中的信号

查找以下模式，这些模式表明库规范：

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

**具有特定提供者的通用模式：** OAuth流程、支付处理、邮件发送、日历同步、ATS集成、文件存储。

### 警惕：集成逻辑在规范中

如果你发现自己编写了如下规范的代码，请停止并重新考虑：

```
-- 太详细了 - 这是 Stripe 的领域，不是你的
规则 ProcessStripeWebhook {
    当：WebhookReceived(payload, signature)
    需要：verify_stripe_signature(payload, signature)
    let event = parse_stripe_event(payload)
    if event.type = "invoice.paid":
        ...
}
```

相反：

```
-- 应用程序响应支付事件（集成由其他地方处理）
规则 PaymentReceived {
    当：stripe/InvoicePaid(invoice)
    ...
}
```

参见 [patterns.md Pattern 8](../allium/references/patterns.md) 获取集成库规范的详细示例。

## 常见的蒸馏挑战

### 挑战：重复术语

当你在规范、规范内或规范与代码之间发现两个术语表示同一概念时，将其视为一个阻塞问题。

```
-- 不良：未解决重复问题
-- 订单 vs 购买
-- checkout.allium 使用 "Purchase" - 这些是等效概念。
```

这不是解决方案。当代码库的不同部分针对不同的规范进行构建时，两个术语都会出现在实现中：重复的模型、冗余的连接表、双向指向的外键。

**要做什么：**
- 选择一个术语。在决定之前，交叉引用相关规范。
- 更新所有引用。不要在注释或“参见”笔记中保留旧术语。
- 在变更日志中记录重命名，而不是在规范本身中。

**代码中的警告标志：**
- 两个表示同一概念的模型（`Order` 和 `Purchase`）
- 连接表（`order_items`，`purchase_items`）
- 像这样的注释“等同于X”或“与Y相同”

提取的规范必须选择一个术语。将另一个标记为技术债务以移除。

### 挑战：隐式状态机

代码中经常有未建模的隐式状态：

```python
# 没有显式状态字段，但这里隐藏了一个状态机
class FeedbackRequest:
    interview_id = Column(Integer)
    interviewer_id = Column(Integer)
    requested_at = Column(DateTime)
    reminded_at = Column(DateTime, nullable=True)
    feedback_id = Column(Integer, nullable=True)  # FK to Feedback if submitted
```

隐式状态是：

- `pending`：设置了 requested_at，feedback_id 为空，reminded_at 为空
- `reminded`：设置了 reminded_at，feedback_id 为空
- `submitted`：设置了 feedback_id

提取为显式：

```
实体 FeedbackRequest {
    interview: Interview
    interviewer: Interviewer
    requested_at: Timestamp
    reminded_at: Timestamp?
    status: pending | reminded | submitted
}
```

### 挑战：分散的逻辑

相同的规则概念可能分散在多个地方：

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

合并为一个规则：

```
规则 CandidateAccepts {
    当：CandidateAccepts(invitation, slot)

    需要：invitation.status = pending
    需要：invitation.expires_at > now
    需要：slot in invitation.slots
    ...
}
```

### 挑战：死代码和历史遗留问题

代码库积累了已构建但未使用的功能、用于修复现已修复的错误的临时解决方案以及从未执行的代码路径。

不要将这些包括在规范中。如果您不确定：

1. 检查代码是否实际上可以访问
2. 询问开发人员是否是故意的
3. 检查git历史记录以获取上下文

### 挑战：缺失的错误处理

代码可能无声失败或具有不完整的错误处理：

```python
def send_notification(user, message):
    try:
        slack.send(user.slack_id, message)
    except SlackError:
        pass  # 无声忽略失败
```

规范应捕获预期行为，而不是错误：

```
确保：Notification.created(to: user, channel: slack)
```

当前实现是否正确处理失败与系统应该做什么是分开的。

### 挑战：过度设计的抽象

企业代码库通常有掩盖意图的抽象层：

```java
public interface NotificationStrategy {
    void notify(NotificationContext context);
}

public class SlackNotificationStrategy implements NotificationStrategy {
    @Override
    public void notify(NotificationContext context) {
        // 实际的 Slack 调用深埋5层
    }
}
```

切到实际行为。规范不需要策略模式、依赖注入或抽象工厂。只需：`确保：Notification.created(channel: slack, ...)`

## 检查清单：抽象足够吗？

在最终确定派生规范之前：

- [ ] 没有数据库列类型（Integer，VARCHAR等）
- [ ] 没有ORM或查询语法
- [ ] 没有HTTP状态码或API路径
- [ ] 没有框架特定概念（中间件、装饰器等）
- [ ] 没有编程语言类型（int，str，List等）
- [ ] 没有代码中的变量名（使用领域术语）
- [ ] 没有基础设施（Redis，Kafka，S3等）
- [ ] 外键替换为关系
- [ ] 移除令牌/密钥（身份验证的实现）
- [ ] 时间戳使用领域 Duration，而不是 timedelta/seconds

如果任何剩余，请问：“利益相关者会在需求文档中包含这个吗？”

## 检查清单：术语一致性

- [ ] 规范中每个概念只有一个名称
- [ ] 没有“也称为”或“等同于”注释
- [ ] 交叉引用相关规范以解决冲突术语
- [ ] 代码中重复的模型标记为技术债务以移除

## 蒸馏后

提取的规范是一个起点。如果蒸馏揭示了需要结构化发现的间隙（不明确的需求、复杂的实体关系、未声明的业务规则），使用 `elicit` 技能来填补它们。对于随着需求演变而进行的定向更改，使用 `tend` 技能。对于检查规范与实现之间持续的协调，使用 `weed` 技能。

当作为 Allium 循环中的 `distill` 子代理运行时，以单个符合 [distill-result.schema.json](../allium/references/schemas/distill-result.schema.json) 的 JSON 对象形式返回你的结果，除此之外别无其他：`spec_path`、已停靠的 `open_questions`，以及一个关于该 spec 涵盖内容的单行 `summary`。使用 `[]` 表示空列表。你读取的源代码将不会出现在调用者的上下文中；只会返回这些字段。在交互模式下，像往常一样以散文形式呈现你的发现——键入的记录是为了机器转交，而不是对话。

```json
{
  "phase": "distill",
  "spec_path": "giftcard.allium",
  "open_questions": ["是否强制将超兑余额清零是故意为之还是偶然失误?"],
  "summary": "礼品卡兑换和状态生命周期"
}
```

## 参考文献

- [语言参考](../allium/references/language-reference.md)，完整的 Allium 语法
- [评估 spec](../allium/references/assessing-specs.md)，如何评估 spec 成熟度并选择合适的分析级别
- [处理发现](../allium/references/actioning-findings.md)，将检查器发现转化为领域问题
- [示例代码](./references/worked-examples.md)，Python、TypeScript 和 Java 中的完整代码到 spec 示例
