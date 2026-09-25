## 资源

| 文件 | 使用场景 |
|---|---|
| `resources/activity-properties-reference.md` | 调用/笔记/会议/任务的属性名称和枚举值。编写 `objects create` 时保持打开状态——目前无法通过 `hubspot properties get` 发现枚举值。 |

首先阅读 `bulk-operations/SKILL.md` — 此技能假设其批处理、管道和干运行模式。

## 两个不明显的规则

**1. 活动在关联之前不可见。** `hubspot objects create --type calls ...` 单独执行会在 CRM UI 中产生无人能见的记录。在停止之前，始终使用 `hubspot associations create --from calls:<id> --to contacts:<id>`（如果相关则包括交易）进行关联。

**2. 写入和读取的时间戳不同。**

| 路径 | 字段 | 格式 |
|---|---|---|
| `objects create --property hs_timestamp=...` | `hs_timestamp` | **Unix ms** (13 位) |
| `objects get --type calls <id>` 返回 | `properties.hs_timestamp` | Unix ms (字符串) |
| `activities list --contact <id>` 返回 | `timestamp` (扁平化、顶层) | **ISO 8601** (例如 `2024-01-15T10:00:00Z`) |

当前 Unix ms: `$(date +%s)000` (macOS) 或 `$(date +%s%3N)` (Linux)。`activities list` 行是 `{"id","type","timestamp","title","body","status","owner_id"}` — 跨类型时间线读取形状，无原始属性名称。

## 按类型创建 + 关联

```bash
# CALL
call_id=$(hubspot objects create --type calls \
  --property hs_call_title="Discovery call" \
  --property hs_call_body="确认 50K 预算，Q2 时间表。" \
  --property hs_call_direction=OUTBOUND \
  --property hs_call_status=COMPLETED \
  --property hs_call_duration=1800000 \
  --property hs_timestamp=$(date +%s)000 \
  --format json | jq -r '.id')
hubspot associations create --from calls:$call_id --to contacts:149
hubspot associations create --from calls:$call_id --to deals:456

# NOTE
note_id=$(hubspot objects create --type notes \
  --property hs_note_body="发送提案。周五跟进。" \
  --property hs_timestamp=$(date +%s)000 \
  --format json | jq -r '.id')
hubspot associations create --from notes:$note_id --to deals:456

# MEETING — 开始和结束时间以 Unix ms 表示；重用开始时间作为 hs_timestamp
start=$(date +%s)000; end=$(( ${start%000} + 3600 ))000
meeting_id=$(hubspot objects create --type meetings \
  --property hs_meeting_title="演示 — Acme" --property hs_meeting_outcome=COMPLETED \
  --property hs_meeting_start_time=$start --property hs_meeting_end_time=$end \
  --property hs_timestamp=$start --format json | jq -r '.id')
hubspot associations create --from meetings:$meeting_id --to contacts:149

# TASK — hs_timestamp 是截止日期，不是创建时间
due=$(( $(date -v+7d +%s) * 1000 ))   # macOS; Linux: date -d '7 days' +%s
task_id=$(hubspot objects create --type tasks \
  --property hs_task_subject="确认收到提案" \
  --property hs_task_priority=HIGH \
  --property hs_task_status=NOT_STARTED \
  --property hs_task_type=CALL \
  --property hs_timestamp=$due \
  --format json | jq -r '.id')
hubspot associations create --from tasks:$task_id --to deals:456
```

## 联系人的未完成任务 — 两个 CLI 调用，无需 xargs

`associations list` 每行输出 `{"id","type"}`；`objects get` 以一批量调用方式从 stdin 读取（参见 `bulk-operations/SKILL.md` "批量读取"）。

```bash
hubspot associations list --from contacts:149 --to tasks \
| hubspot objects get --type tasks \
    --properties hs_task_subject,hs_task_status,hs_task_priority,hs_timestamp \
| jq -c 'select(.properties.hs_task_status != "COMPLETED")'
```

## 批量：每个交易在阶段中的跟进任务

交易 ID 和任务 ID 必须一起传递。将交易负载持久化到文件中，创建任务（输出顺序与输入顺序一致 — 参见 bulk-operations），然后逐行压缩两个 ID 列表并一次性流式传输关联对。

```bash
due=$(( $(date -v+7d +%s) * 1000 ))

# 1. 每个交易的负载，保留交易 ID 与创建负载一起。
hubspot objects search --type deals --filter "dealstage=appointmentscheduled" \
  --properties dealname \
| jq -c --argjson due "$due" '{deal_id: .id, payload: {properties: {
    hs_task_subject: ("Follow up: " + .properties.dealname),
    hs_task_priority: "HIGH", hs_task_status: "NOT_STARTED", hs_task_type: "CALL",
    hs_timestamp: ($due|tostring)
  }}}' > /tmp/deal_tasks.jsonl

# 2. 创建任务；整个批量的一个 CLI 调用。
jq -c '.payload' /tmp/deal_tasks.jsonl \
| hubspot objects create --type tasks > /tmp/created_tasks.jsonl

# 3. 逐行压缩并流式传输关联对。
paste \
  <(jq -r '.deal_id' /tmp/deal_tasks.jsonl) \
  <(jq -r '.id'      /tmp/created_tasks.jsonl) \
| jq -Rc 'split("\t") | {from:("tasks:"+.[1]), to:("deals:"+.[0])}' \
| hubspot associations create
```

对于 >100 行，应用 `bulk-operations/SKILL.md` 中的干运行/摘要/确认模式。

## 已知的限制

活动必须立即关联，否则在 CRM UI 中不可见。`properties get` 不会返回活动类型的枚举选项值 — 使用参考。CLI 中没有序列/节奏。
