首先阅读 `bulk-operations/SKILL.md` — JSONL 管道、批量读取以及 `jq` 重塑模式（`resources/json-patterns.md`）适用。`hubspot activities list --help` 是权威来源。

## 输出格式

`activities list` 按最新优先排序，返回每个活动一条扁平行：`{id, type, timestamp, title, body, status, owner_id}`。`timestamp` 使用 ISO 8601 格式；`type` 是 `CALL|EMAIL|NOTE|MEETING|TASK`。与底层对象上的原始 `hs_call_*` / `hs_timestamp`（Unix ms）不同 — 如需获取这些数据，请使用 `hubspot objects get --type calls`。

## 单个记录的所有活动

传递 `--contact`、`--deal`、`--company`、`--ticket` 中的一个。使用 `--type CALL|EMAIL|NOTE|MEETING|TASK` 过滤，`--limit N` 获取最近 N 条：

```bash
hubspot activities list --contact 73235
hubspot activities list --deal 67890 --type CALL
hubspot activities list --contact 73235 --limit 10
```

## 客户端日期过滤

ISO 8601 字符串按字典序比较。

```bash
CUTOFF=$(date -v-30d +%Y-%m-%dT%H:%M:%SZ)          # macOS
# CUTOFF=$(date -u -d '30 days ago' +%Y-%m-%dT%H:%M:%SZ)  # Linux
hubspot activities list --contact 73235 \
| jq -c --arg cutoff "$CUTOFF" 'select(.timestamp > $cutoff)'
```

## 紧凑时间线

```bash
hubspot activities list --contact 73235 --limit 20 \
| jq -r '"\(.timestamp[0:10])  \(.type)  \(.title)"'
```

## 呼叫前简报

四个管道命令：联系人 + 公司 + 开放交易 + 活动。使用标准输入的批量 `objects get` — 永远不要使用 `xargs -I{}`（参见 `bulk-operations/SKILL.md`）。

```bash
cid=73235
echo "=== 联系人 ==="
hubspot objects get --type contacts $cid \
  --properties email,firstname,lastname,phone,jobtitle,lifecyclestage --format table

echo "=== 公司 ==="
hubspot associations list --from contacts:$cid --to companies \
| jq -c '{id}' \
| hubspot objects get --type companies --properties name,domain,industry,annualrevenue --format table

echo "=== 开放交易 ==="
hubspot associations list --from contacts:$cid --to deals \
| jq -c '{id}' \
| hubspot objects get --type deals --properties dealname,amount,dealstage,closedate,hs_is_closed \
| jq -c 'select(.properties.hs_is_closed != "true")'

echo "=== 最近活动 ==="
hubspot activities list --contact $cid --limit 10 \
| jq -r '"\(.timestamp[0:10])  \(.type)  \(.title)"'
```

## 文本记录

通过参与 ID 获取单个呼叫的文本记录：

```bash
hubspot activities calls transcript get --call 54321
```

将所有呼叫文本记录转储到文件：

```bash
hubspot objects list --type calls --limit 100 --properties hs_call_title \
| jq -r '.id' \
| while read -r call_id; do
    hubspot activities calls transcript get --call "$call_id"
  done > /tmp/transcripts.jsonl
```

输出格式：`{"transcriptId":"...","engagementId":...,"transcriptSource":"...","utterances":[...],"createdAt":...}`。`utterances` 数组包含语音内容；如果没有记录或上传文本记录，则为空。

## 限制

- `--limit` 最大 100，且无 `--after` 游标 — 长历史记录无法分页。`body` 可能很长；使用紧凑时间线进行浏览。
