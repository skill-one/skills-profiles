## 基础

首先阅读 `bulk-operations/SKILL.md` — 分页、JSONL 管道、破坏性操作安全性。重塑配方在 `bulk-operations/resources/json-patterns.md` 中。资源：`resources/contact-segmentation-filters.md` 是过滤器表达式食谱（生命周期、潜在客户状态、电子邮件参与度、活动、交易、负责人）。

## 过滤器语法速查表

真实来源：`hubspot objects search --help`。

- 一个 `--filter` 标志 = 一个 AND 组：`--filter "lifecyclestage=lead AND !hubspot_owner_id"`。
- 多个 `--filter` 标志是 OR 的。用于枚举-OR-枚举。
- 操作符：`=`, `!=`, `>`, `>=`, `<`, `<=`, `~`（CONTAINS_TOKEN — 整词，NOT 子字符串）。
- HAS_PROPERTY：裸 `name` 或 `name?`。NOT_HAS_PROPERTY：`!name`。日期：`YYYY-MM-DD`。

`~` 注意事项：`jobtitle~director` 匹配 "director" 标记，而不是任意子字符串。没有正则表达式操作符 — 广泛搜索，后用 `jq` 过滤。

## 此技能启用的属性

完整实时列表：`hubspot properties list --type contacts`。枚举选项未通过 `properties get` 暴露；用 `hubspot objects list --type contacts --properties <name> --limit 100 --format json | jq -r '.data[].properties.<name> // empty' | sort -u` 发现。

这里使用的核心字段：`lifecyclestage`, `hubspot_owner_id`（裸/`!` 用于已拥有/未拥有；`hubspot owners list` 用于 ID），`hs_email_optout`（`!=true` 排除已选择退出），`hs_email_last_open_date` / `notes_last_contacted`（时效性），`jobtitle` / `country` / `city`（字符串 `=` 或 `~`），`num_associated_deals`（0 净新，`>=1` 有管道）。

企业画像 (`industry`, `numberofemployees`, `annualrevenue`) 存在于 **公司** — 见跨对象部分。

## 常见分段

```bash
# 近期潜在客户（本季度，尚未拥有）
hubspot objects search --type contacts \
  --filter "lifecyclestage=lead AND createdate>2026-01-01 AND !hubspot_owner_id" \
  --properties email,firstname,lastname,createdate

# 按职位决策者（跨标记 OR）
hubspot objects search --type contacts \
  --filter "jobtitle~director" --filter "jobtitle~vp" --filter "jobtitle~chief" \
  --properties email,jobtitle,company

# 已参与但尚未 MQL（最近打开，仍是潜在客户，已选择加入）
hubspot objects search --type contacts \
  --filter "lifecyclestage=lead AND hs_email_last_open_date>2026-04-01 AND hs_email_optout!=true" \
  --properties email,firstname,hs_email_last_open_date

# 地理位置一一美国已选择加入的联系人
hubspot objects search --type contacts \
  --filter "country=United States AND hs_email_optout!=true" \
  --properties email,state,city
```

更多模式（潜在客户状态、交易、负责人、组合 AND/OR）在 `resources/contact-segmentation-filters.md` 中。

## 跨对象：公司所属行业 → 其联系人

`industry`/`numberofemployees`/`annualrevenue` 存在于公司。构建公司集，然后遍历 — 永远不要对每个公司使用 `xargs -I{} hubspot objects get`。`associations list` 发射 `{"id":"...","type":"company_to_contact"}`，直接输入到单个批量 `objects get`。

```bash
# 第一步：目标公司。行业选项是门户特定的 — 用以下方式发现：
#   hubspot objects list --type companies --properties industry --limit 100 --format json \
#   | jq -r '.data[].properties.industry // empty' | sort -u
hubspot objects search --type companies \
  --filter "industry=SOFTWARE AND numberofemployees>=100" \
  --properties name,industry,numberofemployees \
  > target_companies.jsonl

# 第二步：收集关联 ID（associations list 没有 `--from` 批量），然后单个批量
# objects get 所有联系人。
while read -r cid; do hubspot associations list --from "companies:$cid" --to contacts; done \
  < <(jq -r '.id' target_companies.jsonl) \
| jq -c '{id}' | sort -u \
| hubspot objects get --type contacts --properties email,firstname,jobtitle,hs_email_optout \
> target_contacts.jsonl

# 可选：删除已选择退出的
jq -c 'select(.properties.hs_email_optout != "true")' target_contacts.jsonl > campaign_audience.jsonl
```

## 保存和重用分段

分段是一个 JSONL 文件。用于更新、导出或重新获取：

```bash
# 保存
hubspot objects search --type contacts \
  --filter "lifecyclestage=lead AND hs_email_optout!=true" \
  --properties email,firstname,lastname,jobtitle \
  > segments/opted_in_leads.jsonl

# 分配负责人（首先按 bulk-operations/SKILL.md 执行干运行）
jq -c '{id, properties:{hubspot_owner_id:"12345"}}' segments/opted_in_leads.jsonl \
| hubspot objects update --type contacts --dry-run

# 后续用不同属性重新获取
jq -c '{id}' segments/opted_in_leads.jsonl \
| hubspot objects get --type contacts --properties email,lifecyclestage,hs_lead_status
```

对已保存分段的破坏性操作遵循 `bulk-operations/SKILL.md` 中的干运行 → 消化 → 确认流程。

## 已知限制

- 没有列表 API 表面。不能保存为 HubSpot 列表或按列表成员过滤。
- `~` 是标记匹配，不是子字符串。没有正则表达式操作符。
- `properties get` 不返回枚举选项 — 通过 `objects list` + `jq` 发现。
- `associations list` 没有 `--from` 批量。循环收集 ID，批量下游 `objects get`。
- 对于 >100 结果，使用 `bulk-operations/SKILL.md` 中的分页循环。
