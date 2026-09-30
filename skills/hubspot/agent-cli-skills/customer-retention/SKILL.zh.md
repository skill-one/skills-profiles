---
name: customer-retention
description: 通过CRM筛选识别非活跃/有风险的客户，并大规模创建跟进任务。基于`bulk-operations`；将活动创建的具体细节推迟到`sales-execution`。
---

## 资源

| 文件 | 使用场景 |
|---|---|
| `resources/customer-health-signals.md` | 淘汰信号过滤器cookbook — `--filter`表达式用于`notes_last_contacted`、`hs_last_sales_activity_date`、`hs_email_optout`、过期工单、订阅状态。 |

## 前置条件

先阅读`bulk-operations/SKILL.md` — 以下所有读写操作都使用其JSONL管道、分页和干运行/摘要模式。活动-属性表和关联规则位于`sales-execution/SKILL.md`中。

模式是门户特定的。在过滤前验证每个属性 — 例如`hubspot properties get --type contacts notes_last_contacted`，`... hs_last_sales_activity_date`，`... --type subscriptions hs_subscription_status`。如果`subscriptions`返回403，则您的令牌缺少`subscriptions-read` — 使用具有该范围的私有应用令牌。

## 1 — 查找不活跃的客户

```bash
CUTOFF=$(date -v-60d +%Y-%m-%d 2>/dev/null || date -d '60 days ago' +%Y-%m-%d)

# 60天内没有外联（电话/笔记/会议更新notes_last_contacted）
hubspot objects search --type contacts \
  --filter "lifecyclestage=customer AND notes_last_contacted<$CUTOFF" \
  --properties email,firstname,notes_last_contacted,hubspot_owner_id

# 60天内没有销售活动（更广泛 — 也捕获邮件/任务）
hubspot objects search --type contacts \
  --filter "lifecyclestage=customer AND hs_last_sales_activity_date<$CUTOFF" \
  --properties email,firstname,hs_last_sales_activity_date

# 从未联系过
hubspot objects search --type contacts \
  --filter "lifecyclestage=customer AND !notes_last_contacted" \
  --properties email,firstname
```

更多信号（邮件退订、过期工单、无开放交易）请参阅`resources/customer-health-signals.md`。对于>100个结果，使用`bulk-operations`中的分页循环。

要审计客户为何流失或移动阶段 — 哪个工作流、集成、导入或UI编辑最后更改了`lifecyclestage` — 使用`hubspot objects history --type contacts --properties lifecyclestage [--id <recordId>] [--include-ui]`。它将每个属性的源历史记录展平为每条更改的单独一行。

## 2 — 标记有风险的订阅

`subscriptions`是一个标准对象（`hubspot objects types`确认）。`hs_subscription_status`的枚举值是门户特定的 — 过滤前验证，然后输入确切的值：

```bash
hubspot properties get --type subscriptions hs_subscription_status   # 列出允许的值

# 过期 — 立即面临收入风险（替换您验证的值）
hubspot objects search --type subscriptions \
  --filter "hs_subscription_status=past_due" \
  --properties hs_recurring_billing_total,hs_subscription_status

# 将有风险的订阅映射到其联系人以进行外联
hubspot associations list --from subscriptions:<sub_id> --to contacts --format jsonl
```

## 3 — 创建跟进任务或检查笔记

活动创建位于`sales-execution`（完整属性表、笔记+会议流程）。一个锚定示例 — 未关联的任务在CRM UI中不可见，因此始终关联：

```bash
task_id=$(hubspot objects create --type tasks \
  --property hs_task_subject="Q1留存检查" \
  --property hs_task_priority=HIGH --property hs_task_status=NOT_STARTED \
  --property hs_task_type=CALL --property hs_timestamp=$(date +%s)000 \
  --format json | jq -r '.id')
hubspot associations create --from tasks:$task_id --to contacts:<contact_id>
```

## 4 — 为群体批量创建任务

将搜索通过`jq`管道到一个`objects create`调用中，然后关联。先用`--dry-run`预览（`bulk-operations`涵盖>100行的摘要/确认）。

```bash
DUE_MS=$(( ($(date +%s) + 2*86400) * 1000 ))   # 2天后到期

# 1. 捕获群体（同一文件用于创建+关联）
hubspot objects search --type contacts \
  --filter "lifecyclestage=customer AND notes_last_contacted<$CUTOFF" \
  --properties firstname > /tmp/inactive.jsonl

# 2. 构建任务有效负载 — 每个联系人一个
jq -c --arg due "$DUE_MS" '{
  contact_id: .id,
  properties: {
    hs_task_subject: ("重新激活: " + (.properties.firstname // "customer")),
    hs_task_priority: "HIGH", hs_task_status: "NOT_STARTED",
    hs_task_type: "CALL", hs_timestamp: $due
  }
}' /tmp/inactive.jsonl > /tmp/task_payloads.jsonl

# 3. 干运行，然后创建（在管道前删除contact_id）
jq -c '{properties}' /tmp/task_payloads.jsonl | hubspot objects create --type tasks --dry-run | head
jq -c '{properties}' /tmp/task_payloads.jsonl | hubspot objects create --type tasks > /tmp/created.jsonl

# 4. 将每个新任务关联到其联系人（粘贴保留顺序）
paste <(jq -r '.id' /tmp/created.jsonl) <(jq -r '.contact_id' /tmp/task_payloads.jsonl) \
  | while read task_id contact_id; do
      hubspot associations create --from tasks:$task_id --to contacts:$contact_id
    done
```

搜索一个CLI调用，创建一个CLI调用，然后N个关联调用 — 每条记录不使用`xargs -I{}`。`objects create`的输出顺序保证（每个stdin行一个结果，按顺序 — 见`bulk-operations`“输出形状”）使`paste`正确。

## 已知差距

- 没有原生的流失分数/健康分数属性 — 通过自定义属性跟踪。
- `hubspot segments`提供CRM列表用于再激活群体 — `segments members-list`拉取列表的成员，`segments create` / `update-filters`将高风险受众保存为可重用列表。再激活注册可以构建为工作流，通过`hubspot workflows create` / `update`（见`workflow-automation/SKILL.md`）。
- `hubspot sequences`读取Sales Hub序列（只读）：使用`sequences enrollments <contact_id>`查看高风险客户是否曾通过销售序列参与过。序列是产品API（Sales Hub Professional+，`automation.sequences.read`范围），不是CRM对象类型 — CLI无法创建序列或注册联系人。此列表会随时间增长；重新检查`hubspot --help` / `CHANGELOG.md`而不是假设API不存在。
- `hubspot associations create`不批量处理 — 每对使用一个CLI调用。
