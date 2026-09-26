前置条件：首先阅读 `bulk-operations/SKILL.md`。JSONL 管道、分页、干运行/摘要/确认以及 `hubspot history` 恢复都在那里。重塑模式位于 `bulk-operations/resources/json-patterns.md`。

`hubspot_owner_id` 是 `contacts`、`companies`、`deals` 和 `tickets` 上的字符串字段。所有者都是 CRM 用户——`hubspot owners list` 返回他们；没有 `teams` 对象，因此团队级别的视图是客户端按 `hubspot_owner_id` 分组的。

## 1. 解析邮箱 → 所有者 ID

不要硬编码 ID——它们是门户特定的。解析后缓存：

```bash
FROM_ID=$(hubspot owners list | jq -r 'select(.email=="sarah@company.com") | .id')
TO_ID=$(hubspot owners list | jq -r 'select(.email=="mike@company.com")  | .id')
```

## 2. 查找某个所有者的记录

所有四个对象类型都使用相同的过滤器。添加特定于对象的 `--properties` 以获取上下文。未分配的记录使用 `!property` 形式。

```bash
hubspot objects search --type contacts  --filter "hubspot_owner_id=$FROM_ID" --properties email,firstname,lifecyclestage
hubspot objects search --type companies --filter "hubspot_owner_id=$FROM_ID" --properties name,domain
hubspot objects search --type deals     --filter "hubspot_owner_id=$FROM_ID" --properties dealname,dealstage,amount
hubspot objects search --type tickets   --filter "hubspot_owner_id=$FROM_ID" --properties subject,hs_pipeline_stage

# 完全没有所有者的记录
hubspot objects search --type deals --filter "!hubspot_owner_id" --properties dealname,amount
```

>100 条记录——使用 `bulk-operations` 中的 `--after` 循环分页。仅计数：管道到 `wc -l`。

## 3. 批量重新分配——搜索 → 更新

将每个搜索行重塑为 `{id, properties:{hubspot_owner_id}}` 并管道到 `objects update`。始终先干运行；对于 >100 行，干运行会发出摘要 + `apply_command_hint`——使用 `--digest`/`--confirm` 重新运行（参见 `bulk-operations/SKILL.md` § "安全的破坏性工作流"）。

```bash
# 干运行
hubspot objects search --type contacts --filter "hubspot_owner_id=$FROM_ID" \
| jq -c --arg to "$TO_ID" '{id, properties:{hubspot_owner_id:$to}}' \
| hubspot objects update --type contacts --dry-run

# 执行——≤100：丢弃 --dry-run。  >100: 添加 --digest <hash> --confirm <count>。
hubspot objects search --type contacts --filter "hubspot_owner_id=$FROM_ID" \
| jq -c --arg to "$TO_ID" '{id, properties:{hubspot_owner_id:$to}}' \
| hubspot objects update --type contacts
```

单条记录分配——无需 stdin，无需 jq：

```bash
hubspot objects update --type contacts 12345 --property hubspot_owner_id=$TO_ID
```

## 4. Rep-leaves 工作流

遍历代表员接触的四个对象类型：

```bash
FROM_ID=$(hubspot owners list | jq -r 'select(.email=="leaving@company.com")    | .id')
TO_ID=$(hubspot  owners list | jq -r 'select(.email=="taking-over@company.com") | .id')

for type in contacts companies deals tickets; do
  echo "── $type ──"
  hubspot objects search --type "$type" --filter "hubspot_owner_id=$FROM_ID" \
  | jq -c --arg to "$TO_ID" '{id, properties:{hubspot_owner_id:$to}}' \
  | hubspot objects update --type "$type" --dry-run
done
```

审查每条摘要行，然后不使用 `--dry-run` 重新运行（在升级时为每种类型添加 `--digest`/`--confirm`）。分配错误？`hubspot history --since 1h` 列出受影响的 ID。

## 5. 团队级别视图（客户端分组）

按 `hubspot_owner_id` 分组记录，连接到 `owners list` 以获取人类可读的邮箱：

```bash
hubspot objects search --type deals --filter "dealstage!=closedwon AND dealstage!=closedlost" \
  --properties hubspot_owner_id --format json \
| jq '.data | group_by(.properties.hubspot_owner_id)
       | map({owner_id: .[0].properties.hubspot_owner_id, count: length})' \
> /tmp/by-owner.json

hubspot owners list \
| jq --slurpfile by /tmp/by-owner.json -r \
     '. as $o | $by[0][] | select(.owner_id==$o.id) | "\($o.email)\t\(.count)"'
```
