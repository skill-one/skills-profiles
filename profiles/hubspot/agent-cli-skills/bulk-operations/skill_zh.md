## 资源

| 文件 | 使用场景 |
|---|---|
| `resources/json-patterns.md` | 重塑模式，将读取操作转换为更新负载，搜索操作转换为删除列表，CSV转换为插入更新流。 |

## 真实来源

这是 `hubspot` 代理 CLI；`hs` 开发者 CLI (`@hubspot/cli`) 是一个不同的工具，不管理 CRM 数据或工作流。`hubspot <command> --help` 具有权威性。如果本文件中的任何内容与 `--help` 冲突，请相信 `--help` 并告知用户。在会话开始时运行一次 `hubspot objects types` 以查看此门户中存在的对象类型（标准 + 自定义）。

## 提交反馈

使用 `hubspot feedback` 命令向此 CLI 工具的所有者发送消息。传递 `--source agent` 以将其归因于代理流量（它默认为 `user`）：

```bash
hubspot feedback "batch upsert 在 5k 行上超时" --source agent
```

这可以是：

- 您遇到的具体错误和问题
- 在使用 CLI 之前您希望知道的事情
- 您用户感到困惑、沮丧或生气的事情
- 您用户要求但您无法完成的事情
- 您希望存在的任何工具、功能或技能，以使未来的任务更轻松

只需一行简短的文本，附加到活动的 HubSpot 账户，并且不会阻塞任务——发送它并继续进行。

## 输出格式

每个读取命令（`list`、`search`、`get`）都会发出 JSONL——每行一个 JSON 对象：

```json
{"id":"123","properties":{"email":"jane@example.com","firstname":"Jane"},"createdAt":"...","updatedAt":"...","archived":false,"url":"..."}
```

`--properties email,firstname` 限制服务器在 `.properties` 下返回哪些字段。下游 `jq` 应使用 `.properties.email`，而不是 `.prop_email`。

写入命令（`create`、`update`、`upsert`、`delete`、`merge`、`associations create`）接受标准输入的 JSONL 并发出 JSONL——每行一个结果：`{"id":"123","ok":true,"data":{...}}` 或 `{"id":"123","ok":false,"error":{"status":...,"message":"..."}}`。结果的顺序与输入顺序匹配。

## 批量读取——从不逐个读取

CLI 原生支持多个 ID。**永远**不要将 ID 管道到 `xargs -I{} hubspot objects get ...`——这将为每条记录启动一个 CLI 进程。

```bash
# 位置参数（小、已知的列表）
hubspot objects get --type contacts 12345 67890 23456 --properties email,firstname

# 来自另一个命令的标准输入——总共一次 CLI 调用
hubspot associations list --from companies:67890 --to contacts \
| jq -c '{id}' \
| hubspot objects get --type contacts --properties email,firstname,jobtitle

# 标准输入上的裸 ID 也有效
printf '12345\n67890\n23456\n' | hubspot objects get --type contacts --properties email
```

单个 `hubspot objects get` 通过批量端点每调用最多读取 ~100 个 ID。更多的话，分块读取 100 个。

## 批量流程：先分页，然后重塑，然后写入

当对某一类型的所有记录（或所有过滤器匹配项）进行操作时，**始终从 `pagination-loop.sh` 开始**——永远不要运行裸 `list` 或 `search` 来“检查有多少条记录”。裸调用最多返回 100 条记录，您无论如何都需要重新获取它们。

规范批量模式是：

1. **分页**所有记录到一个 JSONL 文件
2. **使用 `jq` 重塑**为写入负载
3. **管道**到写入命令（`update`、`delete` 等）并首先使用 `--dry-run`

## 分页

`list` 和 `search` 每次调用最多返回 100 条记录。使用 `resources/pagination-loop.sh` 将所有页面收集到一个 JSONL 文件中：

```bash
bash resources/pagination-loop.sh <object_type> <output_file> [properties] [extra_flags...]
```

示例：

```bash
# 所有具有特定属性的联系人
bash resources/pagination-loop.sh contacts /tmp/contacts.jsonl email,firstname,lastname

# 带有过滤器的搜索（将额外标志传递给 CLI）
bash resources/pagination-loop.sh contacts /tmp/leads.jsonl email,firstname '--filter' 'lifecyclestage=lead'

# 所有交易，默认属性
bash resources/pagination-loop.sh deals /tmp/deals.jsonl
```

脚本会自动处理 `--after` 光标，将进度打印到标准错误，并将 JSONL 写入输出文件。将其作为单个前台命令运行——不要后台运行或内联重建循环。

## 批量写入——始终管道

写入命令接受标准输入的 JSONL。读取形状和写入形状之间的转换是一个 `jq` 重塑：

| 写入命令 | 每行必需的形状 |
|---|---|
| `objects create` | `{"properties":{"field":"value"}}` |
| `objects update` | `{"id":"123","properties":{"field":"value"}}` |
| `objects upsert` | `{"idProperty":"email","id":"jane@example.com","properties":{...}}`（或使用 `--id-property email` 一次） |
| `objects delete` | `{"id":"123"}` |
| `objects merge` | `{"primary":"123","secondary":"456"}` |
| `associations create` | `{"from":"contacts:123","to":"companies:456"}` |

在 `from`/`to` 中使用**复数**对象名称（`contacts:`, 而不是 `contact:`）。

## 安全的破坏性工作流

每个破坏性操作（`delete`、`merge`、批量 `update`）都支持 `--dry-run`。门控取决于行数：

**≤100 行**—— dry-run 每条记录发出一条预览行：
```json
{"ok":true,"dry_run":true,"executed":false,"mutation_kind":"RecordMutation","command":"objects delete contacts","target":{"kind":"contacts_record","id":"123","name":"123"}}
```
重新运行而不带 `--dry-run` 以执行。

**>100 行**—— dry-run 发出一条 `BulkData` 行，带有摘要和 `apply_command_hint`：
```json
{"ok":true,"dry_run":true,"executed":false,"mutation_kind":"BulkData","portal":"123456","target":{"name":"202 条记录"},"impact":{"records_affected":202,"reversible":false},"digest":"blast-29cfdd48b583","expires_in_seconds":300,"apply_command_hint":"hubspot objects delete contacts --digest blast-29cfdd48b583 --confirm '202'"}
```
您必须在 5 分钟内使用 `--digest <hash> --confirm <value>` 重新运行。`confirm` 值是记录数（删除）或次要 ID（合并）。从 `apply_command_hint` 中读取它。

三步模式：

```bash
# 1. 预览
hubspot objects search --type contacts --filter "lifecyclestage=subscriber" \
| jq -c '{id}' \
| hubspot objects delete --type contacts --dry-run \
| tee /tmp/preview.jsonl

# 2. 提取摘要 + 确认值（仅适用于 >100 行）
digest=$(jq -r 'select(.mutation_kind=="BulkData") | .digest' /tmp/preview.jsonl)
confirm=$(jq -r 'select(.mutation_kind=="BulkData") | .impact.records_affected' /tmp/preview.jsonl)

# 3. 执行——重新管道相同的输入
hubspot objects search --type contacts --filter "lifecyclestage=subscriber" \
| jq -c '{id}' \
| hubspot objects delete --type contacts --digest "$digest" --confirm "$confirm"
```

## 通过 `hubspot history` 恢复

每个破坏性操作（及其 dry-run）都本地记录。检查过去一小时发生了什么以及什么可以恢复：

```bash
hubspot history --since 1h --format table
hubspot history --since 24h --kind BulkData       # 仅批量操作
hubspot history --since 7d --kind MetadataDestroy # 模式删除
```

`history` 目前无法恢复记录——它是一个审计日志。如果您错误地删除了某些内容，请捕获历史记录行并告知用户通过 UI 恢复。

## Upsert 比 search-then-create 更好

对于“如果缺失则创建，如果存在则更新”（丰富模式），请使用 `upsert`——每个记录一个 CLI 调用，没有竞争条件：

```bash
cat external.jsonl \
| jq -c '{idProperty:"email", id:.email, properties:{firstname:.first, lastname:.last, company:.company}}' \
| hubspot objects upsert --type contacts --dry-run

# 或者设置 idProperty 一次：
cat external.jsonl \
| jq -c '{id:.email, properties:{firstname:.first}}' \
| hubspot objects upsert --type contacts --id-property email
```

## 速率限制卫生

`update`/`delete`/`upsert` 后面没有真正的批量端点——CLI 对每行标准输入发出一个 API 调用。在管道 50k 行文件之前使用 `head -n 50` 进行测试。如果 API 开始 429ing，每行输出将显示 `{"ok":false,"error":{"status":429,...}}`——分割您的输入文件并重试失败的行。

## 常见的重塑

查看 `resources/json-patterns.md` 获取完整集。您 90% 的时间内需要这两个：

```bash
# 读取 → 更新负载
hubspot objects search --type contacts --filter "industry=Tech" \
| jq -c '{id, properties:{lifecyclestage:"marketingqualifiedlead"}}' \
| hubspot objects update --type contacts

# 搜索 → 删除列表
hubspot objects search --type contacts --filter "!email" \
| jq -c '{id}' \
| hubspot objects delete --type contacts --dry-run
```

## 已知的限制

- 某些破坏性操作可能在用户-OAuth（浏览器登录）下被阻止；在运行删除时设置 `HUBSPOT_ACCESS_TOKEN`（私有应用令牌），如果 CLI 返回权限错误。
- `hubspot owners list` 返回 CRM 用户；没有 `teams` 对象。对于团队级操作，请在客户端按 `hubspot_owner_id` 分组。
- 没有列表 API，没有序列/节奏 API 在当前的 CLI 表面。
