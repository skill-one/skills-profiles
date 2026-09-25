前置要求：首先阅读 `bulk-operations/SKILL.md` — JSONL 管道、干运行/摘要、历史记录和速率限制卫生措施都在那里。这项技能是在其之上的自然键插入工作流。

## 核心操作：插入更新，而非搜索后创建

`hubspot objects upsert --type X --id-property <自然键>` 从标准输入读取 JSONL 并在**每次调用 CLI 对每条记录创建或更新一行**，以属性（联系人使用电子邮件，公司使用域名）为键。没有竞争窗口，没有分支。不要循环 `search` → 空值？ → `create`。

输入每行：`{"id":"jane@example.com","properties":{"firstname":"Jane","jobtitle":"VP"}}`
输出每行：`{"id":"123","ok":true,"data":{...,"new":true|false}}` 或 `{"ok":false,"error":{...}}`。顺序与输入匹配。

## CSV/JSONL → 插入更新流

使用 `jq` 重构，使用 `--dry-run` 预览，然后执行。始终将自然键转换为小写 — CRM 匹配是精确的。使用 `hubspot properties list --type contacts` 确认可用属性名称；不要硬编码列表。参见 `bulk-operations/resources/json-patterns.md` 获取重构习语。

```bash
# CSV → JSONL（任何工具）；使用 csvkit 示例
csvjson external.csv | jq -c '.[]' > external.jsonl

# 预览
cat external.jsonl \
| jq -c '{id:(.email|ascii_downcase), properties:{firstname:.first, lastname:.last, jobtitle:.title, company:.company}}' \
| hubspot objects upsert --type contacts --id-property email --dry-run | head

# 执行（相同管道，删除 --dry-run，捕获结果）
cat external.jsonl \
| jq -c '{id:(.email|ascii_downcase), properties:{firstname:.first, lastname:.last, jobtitle:.title, company:.company}}' \
| hubspot objects upsert --type contacts --id-property email \
| tee /tmp/upsert.results.jsonl
```

公司：交换 `--type companies --id-property domain` 并使用 `.domain|ascii_downcase` 作为 `id` 进行重构。

## 处理每条记录的 OK/错误输出

使用 `jq` 分割，检查失败模式，在修复输入后重试失败的记录：

```bash
jq -c 'select(.ok==true)'  /tmp/upsert.results.jsonl > /tmp/upsert.ok.jsonl
jq -c 'select(.ok==false)' /tmp/upsert.results.jsonl > /tmp/upsert.failed.jsonl
jq -r '.error.status' /tmp/upsert.failed.jsonl | sort | uniq -c   # 状态 → 计数
jq -r '.data.new'    /tmp/upsert.ok.jsonl     | sort | uniq -c   # 创建与更新
```

429 错误：分割输入并重新运行较小的块（参见 `bulk-operations` 速率限制说明）。400 错误通常表示属性名称错误或枚举值无效 — 修复重构，重新运行失败的输入。

## 破坏性操作安全

`upsert` 本身是非破坏性的，但写回可能会覆盖已填充的字段。始终先 `--dry-run` 并检查。对于批量删除或覆盖现有数据，请遵循 `bulk-operations/SKILL.md` 中的干运行 → 摘要 → 确认流程。恢复：`hubspot history --since 1h`。

## 无需插入更新匹配：OR 搜索 → 更新

当你只想读取匹配（无写回），或自然键不是 CRM 属性时，使用重复的 `--filter` 标志 — 每个标志是一个 OR 组。

验证上限：**每调用 5 个 OR 组**。6+ 返回 `400 too many filterGroups (count: N, max allowed: 5)`。一次 5 个进行分块：

```bash
# emails.txt：每行一个转换为小写的电子邮件
xargs -n5 < emails.txt | while read -r e1 e2 e3 e4 e5; do
  args=()
  for e in "$e1" "$e2" "$e3" "$e4" "$e5"; do [ -n "$e" ] && args+=(--filter "email=$e"); done
  hubspot objects search --type contacts "${args[@]}" --properties email,firstname,company
done > /tmp/matches.jsonl

jq -c '{id, properties:{lifecyclestage:"marketingqualifiedlead"}}' /tmp/matches.jsonl \
| hubspot objects update --type contacts --dry-run
```

对于较大的键值丰富操作，优先使用 `upsert` — 一个管道，无需分块计算。
