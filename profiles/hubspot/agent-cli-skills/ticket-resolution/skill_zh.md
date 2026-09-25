先阅读 `bulk-operations/SKILL.md` — JSONL 管道传输、批量读取、分页、干运行/摘要/确认以及 `hubspot history` 恢复都在那里。`hubspot <命令> --help` 是权威的。工单使用 `tickets` 对象类型（复数形式，例如 `tickets:45123`）。

## 1. 发现管道 + 阶段（门户特定，每次会话运行）

每个门户的阶段 ID 都不同 — 不要硬编码它们。

```bash
hubspot pipelines list --type tickets --format table
hubspot pipelines stages --type tickets --pipeline <pipeline_id> --format table
```

阶段表格会打印每个阶段的 `ID` 和 `标签`（"新建"、"等待联系"、"已关闭" 等）。

## 2. 验证此门户的枚举选项值

`hs_ticket_priority`、`hs_ticket_category` 和 `hs_resolution` 都是 `枚举` 属性 — 选项值是门户配置的，`hubspot properties get` 不会返回它们。通过探测或读取实时记录来发现：

```bash
# 探测：发送一个无效值；400 错误会列出允许的选项。
hubspot objects update --type tickets <some_ticket_id> --property hs_resolution=__probe__
# 错误："不是允许的选项之一：[ISSUE_FIXED, FEATURE_REQUEST_TRACKED, ...]"

# 或者读取已使用的值：
hubspot objects list --type tickets --limit 10 \
  --properties hs_ticket_priority,hs_ticket_category,hs_resolution
```

不要假设 HubSpot 默认值 — 请读取门户。

## 3. 创建工单并关联

`subject` 是唯一实际需要的属性。跳过 `hs_pipeline`/`hs_pipeline_stage` 会导致工单进入默认管道的第一个阶段。

```bash
hubspot objects create --type tickets \
  --property subject="移动应用登录错误" \
  --property content="用户报告自 v3.2 发布以来出现 401 错误。" \
  --property hs_pipeline=<pipeline_id> \
  --property hs_pipeline_stage=<new_stage_id> \
  --property hs_ticket_priority=<value_from_step_2> \
  --property hs_ticket_category=<value_from_step_2>
# 从输出 JSON 中捕获 "id"。

hubspot associations create --from tickets:<ticket_id> --to contacts:<contact_id>
hubspot associations create --from tickets:<ticket_id> --to companies:<company_id>
```

从 JSONL 队列进行批量摄入（参见 `bulk-operations/resources/json-patterns.md` 以获取重塑模式）：

```bash
cat support_requests.jsonl \
| jq -c '{properties:{subject:.subject, content:.description,
    hs_pipeline:"<pipeline_id>", hs_pipeline_stage:"<new_stage_id>",
    hs_ticket_priority:"<priority>", hs_ticket_category:"<category>"}}' \
| hubspot objects create --type tickets
```

## 4. 筛选查询

```bash
# 按优先级打开工单
hubspot objects search --type tickets \
  --filter "hs_pipeline_stage=<open_stage_id> AND hs_ticket_priority=HIGH" \
  --properties subject,hubspot_owner_id,createdate

# 未分配
hubspot objects search --type tickets \
  --filter "!hubspot_owner_id AND hs_pipeline_stage=<open_stage_id>" \
  --properties subject,hs_ticket_priority,createdate
```

使用 `hubspot_owner_id=<id>` 过滤所有者（通过 `hubspot owners list --format table` 找到 ID）。

## 5. 将工单推进阶段（从搜索进行批量更新）

```bash
hubspot objects search --type tickets \
  --filter "hs_ticket_category=BILLING_ISSUE AND hs_pipeline_stage=<new_stage_id>" \
| jq -c '{id, properties:{hs_pipeline_stage:"<waiting_stage_id>"}}' \
| hubspot objects update --type tickets --dry-run
```

不带 `--dry-run` 重新管道相同的搜索以执行。对于 >100 行，请遵循 `bulk-operations/SKILL.md` 中的 `--digest/--confirm` 流程（"安全的破坏性工作流"）。批量重新分配与 `{hubspot_owner_id:"<new>"}` 完全相同。

## 6. 记录解决备注

活动创建位于 `sales-execution/SKILL.md`（备注/电话/会议/任务）。在创建备注后，链接它：`hubspot associations create --from notes:<note_id> --to tickets:<ticket_id>`。

## 7. 关闭工单

`hs_resolution` 是枚举 — 传递步骤 2 中的允许选项值，而不是自由文本。HubSpot 然后计算 `hs_is_closed=true`、`closed_date` 和 `time_to_close`。

```bash
hubspot objects update --type tickets <ticket_id> \
  --property hs_pipeline_stage=<closed_stage_id> \
  --property hs_resolution=<allowed_resolution_value>
```

## 已知限制

- `properties get`/`list` 不会返回枚举选项 — 通过更新错误或读取实时记录（CLI 记录）探测。
- 没有 Conversations/Inbox API 界面 — 聊天线程和收件箱邮件不可通过 CLI 访问。
