## 资源

| 文件 | 使用场景 |
|---|---|
| `resources/customer-health-signals.md` | 淘汰信号过滤器食谱 — `--filter` 表达式用于 `notes_last_contacted`、`hs_last_sales_activity_date`、`hs_email_optout`、过期工单、订阅状态。 |

## 前置条件

先阅读 `bulk-operations/SKILL.md` — 以下所有读写操作都使用其 JSONL 管道、分页和 dry-run/digest 模式。活动属性表和关联规则位于 `sales-execution/SKILL.md` 中。

模式是门户特定的。在过滤前验证每个属性 — 例如 `hubspot properties get --type contacts notes_last_contacted`、`... hs_last_sales_activity_date`、`... --type subscriptions hs_subscription_status`。如果 `subscriptions` 返回 403，则您的令牌缺少 `subscriptions-read` — 使用具有该范围的私有应用令牌。

## 1 — 查找非活跃客户

```bash
CUTOFF=$(date -v-60d +%Y-%m-%d 2>/dev/null || date -d '60 days ago' +%Y-%m-%d)

# 60 天内未联系 (通话/笔记/会议更新 notes_last_contacted)
hubspot objects search --type contacts \
  --filter "lifecyclestage=customer AND notes_last_contacted<$CUTOFF" \
  --properties email,firstname,notes_last_contacted,hubspot_owner_id

# 60 天内无销售活动 (更广泛 — 也捕获邮件/任务)
hubspot objects search --type contacts \
  --filter "lifecyclestage=customer AND hs_last_sales_activity_date<$CUTOFF" \
  --properties email,firstname,hs_last_sales_activity_date

# 从未联系
hubspot objects search --type contacts \
  --filter "lifecyclestage=customer AND !notes_last_contacted" \
  --properties email,firstname
```

更多信号 (邮件退订、过期工单、无开放交易) 请参阅 `resources/customer-health-signals.md`。对于 >100 条结果，使用 `bulk-operations` 中的分页循环。

## 2 — 标记有风险的订阅

`subscriptions` 是标准对象 (`hubspot objects types` 确认)。`hs_subscription_status` 的枚举值是门户特定的 — 过滤前验证，然后输入确切值：

```bash
hubspot properties get --type subscriptions hs_subscription_status   # 列出允许的值

# 过期 — 收入立即面临风险 (替换您验证的值)
hubspot objects search --type subscriptions \
  --filter "hs_subscription_status=past_due" \
  --properties hs_recurring_billing_total,hs_subscription_status

# 将有风险的订阅映射到其联系人以进行接触
hubspot associations list --from subscriptions:<sub_id> --to contacts --format jsonl
```

## 3 — 创建跟进任务或检查笔记

活动创建位于 `sales-execution` (完整属性表、笔记+会议流程)。一个锚示例 — 未关联的任务在 CRM UI 中不可见，因此始终关联：

```bash
task_id=$(hubspot objects create --type tasks \
  --property hs_task_subject="Q1 客户留存检查" \
  --property hs_task_priority=HIGH --property hs_task_status=NOT_STARTED \
  --property hs_task_type=CALL --property hs_timestamp=$(date +%s)000 \
  --format json | jq -r '.id')
hubspot associations create --from tasks:$task_id --to contacts:<contact_id>
```

## 4 — 批量创建一批客户的任务

将搜索通过 `jq` 管道到一个 `objects create` 调用中，然后关联。先用 `--dry-run` 预览 (`bulk-operations` 覆盖 >100 行的 digest/confirm)。

```bash
DUE_MS=$(( ($(date +%s) + 2*86400) * 1000 ))   # 2 天后到期

# 1. 捕获客户群体 (同一文件用于创建+关联)
hubspot objects search --type contacts \
  --filter "lifecyclestage=customer AND notes_last_contacted<$CUTOFF" \
  --properties firstname > /tmp/inactive.jsonl

# 2. 构建任务负载 — 每个联系人一个
jq -c --arg due "$DUE_MS" '{
  contact_id: .id,
  properties: {
    hs_task_subject: ("重新接触: " + (.properties.firstname // "客户")),
    hs_task_priority: "HIGH", hs_task_status: "NOT_STARTED",
    hs_task_type: "CALL", hs_timestamp: $due
  }
}' /tmp/inactive.jsonl > /tmp/task_payloads.jsonl

# 3. Dry-run，然后创建 (管道前删除 contact_id)
jq -c '{properties}' /tmp/task_payloads.jsonl | hubspot objects create --type tasks --dry-run | head
jq -c '{properties}' /tmp/task_payloads.jsonl | hubspot objects create --type tasks > /tmp/created.jsonl

# 4. 将每个新任务关联到其联系人 (粘贴保留顺序)
paste <(jq -r '.id' /tmp/created.jsonl) <(jq -r '.contact_id' /tmp/task_payloads.jsonl) \
  | while read task_id contact_id; do
      hubspot associations create --from tasks:$task_id --to contacts:$contact_id
    done
```

一个 CLI 调用用于搜索，一个用于创建，然后 N 个用于关联 — 每条记录不使用 `xargs -I{}`。`objects create` 的输出顺序保证 (每个 stdin 行一个结果，按顺序 — 见 `bulk-operations` "输出形状") 使 `paste` 正确。

## 已知缺陷

- 没有原生的 churn-score / health-score 属性 — 通过自定义属性跟踪。
- 没有列表 API，没有序列/节奏 API — 重新接触注册不可用 CLI。
- `hubspot associations create` 不批量 — 每对使用一个 CLI 调用。
