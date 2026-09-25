## 真实数据源

`hubspot <command> --help` 是权威的。基于 `bulk-operations/SKILL.md` 构建 — JSONL 结构、批量读取规则和分页都在那里。重塑模式：`bulk-operations/resources/json-patterns.md`。`search`/`list` 每次调用最多返回 100 行；返回正好 100 行的结果几乎总是会被截断 — 在聚合前通过 `bulk-operations/SKILL.md` 进行分页。

## 属性和输出形状说明

- 所有 CRM 属性值都以 **字符串** 形式返回在 JSONL 中 — 包括布尔值。`hs_is_closed_won` 返回为 `"true"`/`"false"`（字符串）；`amount` 是一个数字字符串。使用 `tonumber` 进行算术运算；在客户端过滤时将布尔值作为字符串比较（`== "true"`）。
- 在 `--filter` 表达式中，`hs_is_closed_won=true` 和 `hs_is_closed!=true` 都有效 — API 会解析值。
- `--properties` 返回标准嵌套形状：`{"id":"123","properties":{"amount":"5000","dealname":"..."}}`。在 jq 中引用字段为 `.properties.amount`。
- `dealstage` 中的阶段 ID 是门户特定的。使用 `hubspot pipelines stages --type deals --pipeline <id>` 进行映射。
- `hubspot_owner_id` 是一个数字字符串。使用 `hubspot owners list`（字段：`id`，`firstName`，`lastName`，`email`）解析为名称。

## 1. 每日简报

日期窗口在 macOS 和 GNU `date` 之间有所不同：
```bash
# macOS
TODAY=$(date +%Y-%m-%d); NEXT_7=$(date -v+7d +%Y-%m-%d); YESTERDAY=$(date -v-1d +%Y-%m-%d)
# Linux
TODAY=$(date +%Y-%m-%d); NEXT_7=$(date -d '7 days' +%Y-%m-%d); YESTERDAY=$(date -d '1 day ago' +%Y-%m-%d)
```

**未来 7 天内到期的交易：**
```bash
hubspot objects search --type deals \
  --filter "closedate>$TODAY AND closedate<$NEXT_7 AND hs_is_closed!=true" \
  --properties dealname,amount,closedate,hubspot_owner_id
```

**过去 24 小时内更新的交易：**
```bash
hubspot objects search --type deals \
  --filter "hs_lastmodifieddate>$YESTERDAY AND hs_is_closed!=true" \
  --properties dealname,amount,dealstage,hs_lastmodifieddate
```

**开放管道摘要行：**
```bash
hubspot objects search --type deals --filter "hs_is_closed!=true" --properties amount \
| jq -rs '{count: length, value: ([.[].properties.amount | select(. != null) | tonumber] | add // 0 | round)}
          | "Open pipeline: \(.count) 交易, $\(.value)"'
```

## 2. 管道快照

**按阶段** — 每个 `dealstage` 的计数和金额：
```bash
hubspot objects search --type deals --filter "hs_is_closed!=true" \
  --properties dealstage,amount \
| jq -rs '
    group_by(.properties.dealstage)
    | map({stage: .[0].properties.dealstage, count: length,
           total: ([.[].properties.amount | select(. != null) | tonumber] | add // 0 | round)})
    | sort_by(-.total) | .[] | "\(.stage)\tcount: \(.count)\tvalue: $\(.total)"' \
| column -t -s$'\t'
```

**按负责人：**
```bash
hubspot objects search --type deals --filter "hs_is_closed!=true" \
  --properties amount,hubspot_owner_id \
| jq -rs '
    group_by(.properties.hubspot_owner_id)
    | map({owner: .[0].properties.hubspot_owner_id, count: length,
           total: ([.[].properties.amount | select(. != null) | tonumber] | add // 0 | round)})
    | sort_by(-.total) | .[] | "owner \(.owner)\t交易: \(.count)\tvalue: $\(.total)"' \
| column -t -s$'\t'
```

要为负责人 ID 添加名称，一次性导出所有负责人并连接：
```bash
hubspot owners list | jq -r '"\(.id)\t\(.firstName) \(.lastName) <\(.email)>"' > /tmp/owners.tsv
```

## 3. 胜/负分析

过滤 `hs_is_closed_won=true` 为胜出；`hs_is_closed=true AND hs_is_closed_won!=true` 为失败。使用 `closedate>=YYYY-MM-DD AND closedate<YYYY-MM-DD` 进行范围限制。

**特定时间段内关闭的胜/负交易：**
```bash
hubspot objects search --type deals \
  --filter "hs_is_closed_won=true AND closedate>=2026-04-01 AND closedate<2026-07-01" \
  --properties dealname,amount,closedate,hubspot_owner_id

hubspot objects search --type deals \
  --filter "hs_is_closed=true AND hs_is_closed_won!=true AND closedate>=2026-04-01 AND closedate<2026-07-01" \
  --properties dealname,amount,closedate,hubspot_owner_id
```

**按代表的胜率** — 拉取该时间段内所有关闭的交易，分组，计算。注意：`hs_is_closed_won` 作为字符串返回，因此比较 `== "true"`。
```bash
hubspot objects search --type deals \
  --filter "hs_is_closed=true AND closedate>=2026-01-01" \
  --properties hubspot_owner_id,hs_is_closed_won,amount \
| jq -rs '
    group_by(.properties.hubspot_owner_id)
    | map({owner: .[0].properties.hubspot_owner_id,
           total: length,
           won: ([.[] | select(.properties.hs_is_closed_won == "true")] | length),
           won_value: ([.[] | select(.properties.hs_is_closed_won == "true")
                       | .properties.amount | select(. != null) | tonumber] | add // 0 | round)})
    | map(. + {win_rate: ((.won / .total * 100) | round)})
    | sort_by(-.won_value)
    | .[] | "owner \(.owner)\twon: \(.won)/\(.total)\trate: \(.win_rate)%\twon: $\(.won_value)"' \
| column -t -s$'\t'
```

**按关闭月份的收入**（胜出交易）：
```bash
hubspot objects search --type deals \
  --filter "hs_is_closed_won=true AND closedate>=2026-01-01" \
  --properties amount,closedate \
| jq -rs '
    group_by(.properties.closedate[0:7])
    | map({month: .[0].properties.closedate[0:7], count: length,
           revenue: ([.[].properties.amount | select(. != null) | tonumber] | add // 0 | round)})
    | sort_by(.month) | .[] | "\(.month)\t交易: \(.count)\trevenue: $\(.revenue)"' \
| column -t -s$'\t'
```

## 已知限制

- `hubspot pipelines stages` 不暴露阶段概率 — 无法从阶段列表自动识别胜出/失败阶段。使用交易上的 `hs_is_closed_won` 代替。
- 没有团队对象 — 按 `hubspot_owner_id` 分组，并在客户端解析名称。
