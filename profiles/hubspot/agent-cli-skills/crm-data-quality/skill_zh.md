先阅读 `bulk-operations/SKILL.md` — JSONL 管道、批量读取、分页以及 dry-run/digest/confirm 控制适用于下述所有命令。

## 属性发现

不要猜测属性名称。列出它们：

```bash
hubspot properties list --type contacts --format table
hubspot properties list --type contacts | jq -c 'select(.type=="enumeration") | {name, label}'
```

对于 `--type companies`、`deals` 或任何自定义类型 (`hubspot objects types`)，操作相同。

## 1. 查找不完整的记录

`!name` = NOT_HAS_PROPERTY（缺失或为空）。裸 `name` = HAS_PROPERTY。在一个 `--filter` 内，使用 `AND` 链接；多个 `--filter` 旗帜使用 `OR`。

```bash
hubspot objects search --type contacts --filter "!email" --properties firstname,lastname,company
hubspot objects search --type contacts --filter "!phone AND !mobilephone" --properties email
hubspot objects search --type contacts --filter "!hubspot_owner_id" --properties email,lifecyclestage
```

对于 >100 条结果，使用 `bulk-operations` 中的分页循环。

## 2. 规范字段值

搜索 → 使用 `jq` 重塑 → 管道到 `update`。始终先 `--dry-run`；`bulk-operations` 覆盖 >100 行的 digest/confirm 升级。重塑模式：`bulk-operations/resources/json-patterns.md`。

```bash
# 将拼写合并为一个规范值
hubspot objects search --type contacts --filter "company~acme" \
| jq -c '{id, properties:{company:"Acme Corporation"}}' \
| hubspot objects update --type contacts --dry-run

# 将电子邮件转为小写（读取、重塑、写入）
hubspot objects search --type contacts --filter "email" --properties email \
| jq -c '{id, properties:{email: (.properties.email | ascii_downcase)}}' \
| hubspot objects update --type contacts --dry-run
```

## 3. 使用 `hubspot objects merge` 去重

次要项将被合并到主要项并删除。**不可逆。** dry-run/digest/confirm 控制适用。

```bash
# 单对
hubspot objects merge --type contacts --primary 149 --secondary 425 --dry-run
hubspot objects merge --type contacts --primary 149 --secondary 425   # 执行（≤100 对）
```

批量处理：将 JSONL `{"primary":"...","secondary":"..."}` 管道到标准输入（省略 `--primary`/`--secondary`）。

**需要分页。** `objects search` 每次调用最多返回 100 行，而 `jq -s` 将单个流 slurp 到内存中 — 对原始 `search` 运行以下代码片段将静默忽略跨越页边界的所有重复项。首先使用 `bulk-operations/SKILL.md` 中的分页循环收集完整集（写入 `/tmp/contacts.jsonl`），然后从文件去重：

```bash
# /tmp/contacts.jsonl 由分页循环（bulk-operations/SKILL.md）生成
jq -s -c '
    group_by(.properties.email)[]
    | select(length > 1)
    | sort_by(.id | tonumber)
    | .[0].id as $p | .[1:][] | {primary: $p, secondary: .id}
  ' /tmp/contacts.jsonl \
| hubspot objects merge --type contacts --dry-run | tee /tmp/merge-preview.jsonl
```

对于 >100 对，从 `BulkData` 行中提取 `digest` 和 `impact.records_affected`，并将相同的生成器重新管道到 `--digest`/`--confirm`（参见 `bulk-operations`）。

## 4. 审计属性

`hubspot properties list`（以及 `get`、`batch-read`）每行输出 `{name, label, type, fieldType, groupName}`。枚举选项值当前未通过 CLI 暴露 — 从真实记录（`hubspot objects search ... --properties <enum>`）或 HubSpot UI 中读取。

```bash
# 每组属性计数（HubSpot 组合标准字段；自定义组突出显示）
hubspot properties list --type contacts | jq -rs 'group_by(.groupName) | map({group: .[0].groupName, count: length}) | .[]'

# 所有枚举属性
hubspot properties list --type contacts | jq -c 'select(.type=="enumeration") | {name, label, fieldType}'

# 创建一个 DQ 标志属性，然后通过第 2 节中的规范模式设置它
hubspot properties create --type contacts --name dq_missing_phone --label "DQ: Missing Phone" --prop-type string --field-type text
```

## 恢复

合并不可逆。合并后，`hubspot history --since 1h` 捕获审计轨迹。如果方向错误，从 UI 的回收站中恢复次要项。
