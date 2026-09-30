---
name: deal-management
description: 从命令行界面（CLI）运行完整的交易生命周期——发现流程/阶段，将MQL（潜在客户资格）转化为交易并建立关联，批量推进/重新分配，追踪停滞的交易，并完成关闭。
---

## 资源

| 文件 | 使用场景 |
|---|---|
| `resources/lifecycle-stage-progression.md` | 生命周期阶段 API 值 + 与交易移动配对的联系人端更新。 |
| `resources/stalled-deal-queries.md` | 具有动态日期的停滞/无活动/已过截止日期交易的筛选配方。 |

## 基础

先阅读 `bulk-operations/SKILL.md` — JSONL 管道、批量读取、分页和 dry-run/digest/confirm 流程都在那里。重塑配方在 `bulk-operations/resources/json-patterns.md`。`hubspot <command> --help` 是权威来源。对象类型是复数形式（`contacts`、`deals`、`companies`）。对于属性参考：`hubspot properties list --type deals` — 不要硬编码属性表。

## 1. 发现管道和阶段

管道和阶段 ID 是 **门户特定的**。始终在运行时发现 — 永远不要跨门户硬编码。

```bash
hubspot pipelines list --type deals --format jsonl
# {"id":"default","label":"Sales Pipeline","displayOrder":0}
# {"id":"a1b2c3d4-0000-0000-0000-000000000000","label":"Enterprise Pipeline","displayOrder":1}

hubspot pipelines stages --type deals --pipeline default --format jsonl
# {"id":"appointmentscheduled","label":"Appointment Scheduled","displayOrder":0}
# {"id":"qualifiedtobuy","label":"Qualified To Buy","displayOrder":1}
# ...
# {"id":"closedwon","label":"Closed Won","displayOrder":5}
# {"id":"closedlost","label":"Closed Lost","displayOrder":6}
```

通过标签获取特定阶段 ID：

```bash
QUALIFIED=$(hubspot pipelines stages --type deals --pipeline default --format jsonl \
  | jq -r 'select(.label=="Qualified To Buy") | .id')
```

上面显示的 ID（`appointmentscheduled`、`closedwon` 等）是 HubSpot 的标准 `default` 交易管道阶段 — 但每次运行都要发现你自己的，因为门户可以重命名或删除它们。

## 2. 将 MQL 资格认证为交易

查找没有交易的已连接 MQL，然后对每个：创建交易、关联到联系人 + 公司、提升生命周期。

```bash
# 1. 查找可用的 MQL
hubspot objects search --type contacts \
  --filter "lifecyclestage=marketingqualifiedlead AND hs_lead_status=CONNECTED AND num_associated_deals=0" \
  --properties email,firstname,lastname,company,hubspot_owner_id

# 2. 对一个联系人：公司查询、交易创建、关联、提升
hubspot associations list --from contacts:<contact_id> --to companies   # → <company_id>

hubspot objects create --type deals \
  --property "dealname=Acme Corp - Inbound" \
  --property pipeline=default --property dealstage=qualifiedtobuy \
  --property amount=0 --property hubspot_owner_id=<owner_id>
# 返回 {"id":"<deal_id>","ok":true,...}

hubspot associations create --from deals:<deal_id> --to contacts:<contact_id>
hubspot associations create --from deals:<deal_id> --to companies:<company_id>

hubspot objects update --type contacts <contact_id> \
  --property lifecyclestage=salesqualifiedlead --property hs_lead_status=OPEN_DEAL
```

### 批量模式 — 一次处理多个 MQL

`objects create` 返回每行输入的每个结果行，按输入顺序。捕获两个流并按行连接以进行关联：

```bash
# 1. 将 MQL 快照到文件（保留顺序以用于连接）
hubspot objects search --type contacts \
  --filter "lifecyclestage=marketingqualifiedlead AND hs_lead_status=CONNECTED AND num_associated_deals=0" \
  --properties email,firstname,lastname,company,hubspot_owner_id \
  > /tmp/mqls.jsonl

# 2. 每个MQL一个交易 — 输出保留顺序
jq -c '{properties:{
    dealname: ((.properties.firstname // "") + " " + (.properties.lastname // "") + " - " + (.properties.company // "Unknown")),
    pipeline:"default", dealstage:"qualifiedtobuy", amount:"0", dealtype:"newbusiness",
    hubspot_owner_id:(.properties.hubspot_owner_id // "")
  }}' /tmp/mqls.jsonl \
| hubspot objects create --type deals > /tmp/deals.jsonl

# 3. 如果任何创建失败则中止 — paste 会将 null 交易 ID 压缩到真实联系人上
jq -e 'select(.ok==false)' /tmp/deals.jsonl > /dev/null && { echo "Some deal creates failed — inspect /tmp/deals.jsonl" >&2; exit 1; }

# 4. 通过行对联系人 <-> 新交易进行配对以进行关联调用
paste <(jq -r '.id' /tmp/mqls.jsonl) <(jq -r '.id' /tmp/deals.jsonl) \
| jq -cR 'split("\t") | {from:("deals:" + .[1]), to:("contacts:" + .[0])}' \
| hubspot associations create

# 5. 对每个联系人提升生命周期
jq -c '{id, properties:{lifecyclestage:"salesqualifiedlead", hs_lead_status:"OPEN_DEAL"}}' /tmp/mqls.jsonl \
| hubspot objects update --type contacts
```

公司关联需要通过 `hubspot associations list --from contacts:<id> --to companies` 分接触进行单独处理 — 一个联系人可能有一个或多个公司。

预资格检查只是搜索上的筛选：有电子邮件、有公司、无开放交易、有所有者 — 都已在 `--filter` 中。参见 `resources/lifecycle-stage-progression.md` 以获取完整阶段进度和联系人端更新。

## 3. 批量推进或重新分配

```bash
# 将一个阶段中的每个交易移动到下一个阶段 — 预览，然后重新运行不带 --dry-run
hubspot objects search --type deals --filter "dealstage=qualifiedtobuy" \
| jq -c '{id, properties:{dealstage:"presentationscheduled"}}' \
| hubspot objects update --type deals --dry-run

# 将开放交易从一个代表重新分配到另一个代表
OLD=$(hubspot owners list --format jsonl | jq -r 'select(.email=="old@co.com") | .id')
NEW=$(hubspot owners list --format jsonl | jq -r 'select(.email=="new@co.com") | .id')
hubspot objects search --type deals --filter "hubspot_owner_id=$OLD AND hs_is_closed!=true" \
| jq -c "{id, properties:{hubspot_owner_id:\"$NEW\"}}" \
| hubspot objects update --type deals --dry-run
```

对于 >100 行，dry-run 会发出一个 digest 行；用 `--digest <hash> --confirm <count>` 重新管道。完整流程在 `bulk-operations/SKILL.md`。

## 4. 查找停滞的交易

动态日期的筛选配方在 `resources/stalled-deal-queries.md` 中。核心查询：

```bash
# 30 天内无活动的开放交易（macOS / Linux 日期示例在资源中）
hubspot objects search --type deals \
  --filter "hs_last_activity_date<$(date -v-30d +%Y-%m-%d) AND hs_is_closed!=true" \
  --properties dealname,dealstage,closedate,hubspot_owner_id,hs_last_activity_date
```

将结果管道到更新（延长截止日期、移动阶段、设置标志）或任务创建。对于停滞交易的跟进任务/电话/笔记，请参阅 `sales-execution` 技能 — 不要在此处重复活动对象属性处理。

```bash
# 延长所有已过期的截止日期
hubspot objects search --type deals \
  --filter "closedate<$(date +%Y-%m-%d) AND hs_is_closed!=true" \
| jq -c '{id, properties:{closedate:"2026-06-30"}}' \
| hubspot objects update --type deals --dry-run
```

## 5. 关闭

关闭是一个阶段更新 + `closedate`（YYYY-MM-DD）。`hs_is_closed` 和 `hs_is_closed_won` 是只读的 — HubSpot 从阶段派生它们。

```bash
# 单个
hubspot objects update --type deals <deal_id> \
  --property dealstage=closedwon --property closedate=2026-05-15

# 批量 — 首先预览
hubspot objects search --type deals --filter "dealstage=contractsent AND hubspot_owner_id=<owner_id>" \
| jq -c '{id, properties:{dealstage:"closedwon", closedate:"2026-05-15"}}' \
| hubspot objects update --type deals --dry-run
```

赢/输分析（关闭原因、赢率、ARR 滚动）在 `sales-reporting` 技能中。

## 已知的限制

- 批量 MQL → 交易需要一个两步 shell 流程：关联必须从 `objects create` 输出构建，不能在同一管道中。
- `lifecyclestage` 在大多数门户设置中是单向的 — 反向转换可能会被拒绝。
- `closedate` 是一个日期字符串（`YYYY-MM-DD`）。Datetime 活动属性 (`hs_last_activity_date`) 也接受日期字符串用于 `<`/`>` 比较。
- `hubspot sequences` 读取 Sales Hub 序列（`list` / `get` / `enrollments`），但只读 — CLI 无法将联系人加入序列，因此请通过 `sales-execution` 创建跟进任务。`sequences enrollments <contact_id>` 对于交易联系人上的赢/输上下文很有用。
