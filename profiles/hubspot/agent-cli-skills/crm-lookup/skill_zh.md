## 真实数据源

`hubspot <命令> --help` 是权威的。首先阅读 [`bulk-operations/SKILL.md`](../bulk-operations/SKILL.md) — 它拥有 JSONL 管道、分页、通过标准输入批量获取以及查找后的任何写入操作的安全流程。此技能是只读的。

## 从实时模式中选择属性

模式会变化。运行 `hubspot properties list --type <类型>` 获取实时集合。初步 `--properties` 用于简要信息：

| 对象 | `--properties` |
|---|---|
| 联系人 | `email,firstname,lastname,company,phone,lifecyclestage,hubspot_owner_id` |
| 公司 | `name,domain,industry,annualrevenue,numberofemployees,hubspot_owner_id` |
| 交易 | `dealname,amount,dealstage,closedate,hubspot_owner_id,hs_is_closed_won` |
| 工单 | `subject,hs_pipeline_stage,hs_ticket_priority,hubspot_owner_id` |

联系人广告/活动归因位于 `hs_analytics_*`（例如 `hs_analytics_source`, `hs_analytics_source_data_1`/`_2`, `hs_analytics_first_touch_converting_campaign`, `hs_analytics_last_touch_converting_campaign`）。完整列表：`hubspot properties list --type contacts | grep hs_analytics_`。

## 1. 通过 ID 查找

单个批量调用中最多 ~100 个 ID：

```bash
hubspot objects get --type contacts 12345 67890 23456 --properties email,firstname,lastname,company,phone,lifecyclestage
```

## 2. 通过电子邮件/域名（精确匹配）

`email`/`domain` 是精确匹配 — 转换为小写。多个 `--filter` 标志是 OR 的。

```bash
hubspot objects search --type contacts --filter "email=jane@acme.com" \
  --properties email,firstname,lastname,company,lifecyclestage,hubspot_owner_id

hubspot objects search --type companies --filter "domain=acme.com" \
  --properties name,domain,industry,annualrevenue,hubspot_owner_id

# OR — 在一次调用中包含多个电子邮件
hubspot objects search --type contacts \
  --filter "email=alice@acme.com" --filter "email=bob@acme.com" --properties email,firstname
```

## 3. 通过部分名称查找（词元 + 客户端缩小）

`~` 是 CONTAINS_TOKEN — 匹配整个空格分隔的单词。`dealname~acme` 查找 "Acme Renewal" 但**不** "AcmeCorp"。对于子字符串，管道到 `jq`。没有跨所有字段的全文搜索 — 选择属性。

```bash
hubspot objects search --type deals --filter "dealname~acme" --properties dealname,amount,dealstage \
| jq -c 'select(.properties.dealname | ascii_downcase | contains("acme corp"))'
```

## 4. 查找所有关联记录（两个 CLI 调用，不是 xargs）

模式：`associations list` → `jq -c '{id}'` → `objects get` 批量。**永远** `xargs -I{} hubspot objects get …` — 那会为每条记录生成一个进程。在 `--from` 中使用**复数**（`contacts:`, `companies:`, `deals:`）；`--help` 显示单数但只有复数才能避免警告。

```bash
# 公司的所有联系人
hubspot associations list --from companies:67890 --to contacts \
| jq -c '{id}' \
| hubspot objects get --type contacts --properties email,firstname,lastname,jobtitle

# 联系人的未关闭交易（客户端过滤；“open”因管道而异）
hubspot associations list --from contacts:12345 --to deals | jq -c '{id}' \
| hubspot objects get --type deals --properties dealname,amount,dealstage,hs_is_closed \
| jq -c 'select(.properties.hs_is_closed != "true")'
```

## 5. 获取记录及其关联

```bash
contact_id=12345
hubspot objects get --type contacts $contact_id --properties email,firstname,lastname,company,lifecyclestage

# 关联公司（通常只有一个）
hubspot associations list --from contacts:$contact_id --to companies | jq -c '{id}' | head -1 \
| hubspot objects get --type companies --properties name,domain,industry,annualrevenue

# 关联交易
hubspot associations list --from contacts:$contact_id --to deals | jq -c '{id}' \
| hubspot objects get --type deals --properties dealname,amount,dealstage,closedate
```

## 限制

- 搜索每页返回 ≤100 条。更多请使用 `bulk-operations/SKILL.md` 中的分页循环。
- `~` 是基于词元的；子字符串过滤在搜索后的 `jq` 中发生。
- 如果查找用于写入（更新、删除、合并），请遵循 `bulk-operations/SKILL.md` 中的 `--dry-run` → 消化 → `--confirm` 流程。
