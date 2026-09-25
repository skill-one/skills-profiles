# 阿里云 SLS 查询与分析

## 场景描述

当用户需要以下操作时，使用此技能：

- 解释、重写、优化或执行现有查询
- 将自然语言需求转换为 SLS **索引查询**、**SQL** 或 **SPL** 语句

---

## 前置条件

### 安装 Aliyun CLI

运行 `aliyun version` 验证版本是否 >= `3.3.8`。如果未安装或版本过旧，请参考文档 [references/cli-installation-guide.md](references/cli-installation-guide.md) 进行安装或更新。

### 更新插件

```bash
aliyun plugin update
```

### 检查已配置的阿里云凭证

运行 `aliyun configure list` 检查是否已配置凭证。
如果没有显示有效的配置文件，请在此处 **停止** 并要求用户在当前会话外运行 `aliyun configure`。

**安全规则：**

- **绝对不要** 读取、回显或打印 AK/SK 值
- **绝对不要** 要求用户将 AK/SK 粘贴到对话中
- **仅** 使用 `aliyun configure list` 检查凭证状态

---

## RAM 权限要求

| API | CLI | 操作 | 目的 |
|-----|-----|------|------|
| GetLogsV2 | `get-logs-v2` | `log:GetLogStoreLogs` | 运行查询 / SQL / SPL 并读取结果 |
| GetIndex | `get-index`   | `log:GetIndex`        | 读取索引配置以验证前置条件 |

有关最小和完整的 RAM 策略 JSON，请参阅 [references/ram-policies.md](references/ram-policies.md)。

> **权限失败处理：** 如果调用返回 `Unauthorized` 权限错误，请停止并向用户显示 [references/ram-policies.md](references/ram-policies.md)。**未经明确用户确认，不要** 使用不同账户重试。

---

## 可观察性（必须对每个 aliyun api 命令遵循）

加载此技能时，为整个会话生成一个随机的会话 ID（32 位小写十六进制字符串），并在下方使用 `{session-id}`。

**规则：** 每个调用云 API 的 `aliyun` CLI 命令 **必须** 包含 `--user-agent` 标志。本地工具命令（例如 `configure`、`plugin`、`version`）不支持此标志，应排除。

```
--user-agent "AlibabaCloud-Agent-Skills/alibabacloud-sls-query/{session-id}"
```

示例（假设 session-id 是 `a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6`）：

```bash
aliyun sls get-logs-v2 --project my-project --logstore my-logstore \
  --from 1740000000 --to 1740003600 --query '*' \
  --user-agent "AlibabaCloud-Agent-Skills/alibabacloud-sls-query/a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6"
```

不要跳过、更改格式或省略任何 `aliyun` API 命令调用的 `--user-agent`。

---

## 核心工作流程

1. 读取索引配置（GetIndex）
2. 选择查询模式
3. 构建语句
4. 解析时间范围
5. 执行查询
6. 从响应中提取数据
7. 展示 CLI 命令和结果

### 步骤 1：读取索引配置（强制）

始终首先调用 `get-index` —— 索引配置决定了步骤 2 中哪些查询模式可用。

```bash
aliyun sls get-index \
  --project <project> --logstore <logstore>
```

响应中的两个部分驱动后续所有决策：

| 部分 | 含义 |
|------|------|
| `line`  | **全文索引** —— 缺失表示全文搜索已禁用 |
| `keys`  | **字段索引** —— 字段 → `{ type, doc_value, token, caseSensitive, chn, ... }` 的映射。`doc_value: true` 表示该字段已启用统计 |

如果调用返回 `IndexConfigNotExist`（HTTP 404），或者响应中既没有 `line` 也没有 `keys`，则该 Logstore 完全没有索引 —— 立即停止并告知用户在执行任何查询 / SQL / SPL 之前必须创建索引。

- **响应可能很大** —— 仅提取与当前查询相关的字段。按 `logstore` 缓存并在会话内重用。

有关字段类型、分词以及 `get-index` 如何映射到功能，请参阅 [references/related-apis.md](references/related-apis.md) 和 [references/query-analysis.md](references/query-analysis.md)。

---

### 步骤 2：选择查询模式（关键）

查询语句采用以下形式之一：

| 优先级 | 模式 | 语句形式 | 使用场景 | 需要条件 |
|--------|------|----------|----------|----------|
| 1 | **索引搜索** | `<index-search>` | 过滤原始日志；返回时间排序和分页的日志 | 全文 (`line`) 或任何字段索引 (`keys.<field>`) |
| 2 | **SQL** | `<index-search> \| <SQL>` | 聚合、`GROUP BY`、排序、窗口、top-N、投影以及其他分析操作 | 目标字段具有 `keys.<field>` 且 `doc_value: true` |
| 3 | **SQL scan** | `<index-search> \| <SQL scan>` | 用户请求 | 无 |
| 4 | **SPL** | `<index-search> \| <SPL>` | 用户请求 | 无 |

**选择规则：**

- 始终优先选择 **索引搜索** 以获得最快的速度。
- 当用户需要分析操作或字段投影而不是完整原始日志检索时，使用 **索引搜索 + SQL**，例如聚合、`GROUP BY`、排序、窗口分析、top-N 或返回仅需要的字段/列。
- **不要** 主动选择 **SQL scan** 或 **SPL**；仅在用户明确请求时使用它们。

有关完整决策指南，请参阅 [references/query-analysis.md](references/query-analysis.md)。

---

### 步骤 3：编写语句

#### 3.1 首先构建索引搜索部分（`|` 之前）

收集可以用索引搜索语法表达的每个过滤器，并将其放在第一个 `|` 之前。如果没有过滤器适用，使用 `*`。

```text
* and "payment failed" and status: "500" and not path: "/healthz"
```

- `*` 匹配所有；`"..."` 是全文（需要全文索引）。
- `key: "value"` 是字段过滤器（需要字段索引）。
- 使用 `and` / `or` / `not` 组合；用括号分组。
- `key: *` 表示字段存在。范围 (`>`, `>=`, `[a, b]`) 仅适用于 `long` / `double`。

如果需求可以完全在不进行聚合或行级处理的情况下回答，则在此停止——这已经是一个完整的索引搜索。有关完整索引搜索语法，请参阅 [references/query-analysis.md](references/query-analysis.md)。

#### 3.2 追加 SQL——用于聚合 / 分析

```sql
status: 500 | SELECT date_trunc('minute', __time__) AS minute,
                    count(*) AS errors
              FROM log
              GROUP BY minute
              ORDER BY minute
```

- 阅读 [references/query-analysis.md](references/query-analysis.md) 了解查询 & SQL 规则
- 表名为 `log`（建议省略）。
- SQL 尊重 `get-index` 中的索引字段类型——`long` / `double` 字段可以直接比较 (`status >= 500`)。仅在字段被索引为 `text` 但需要数值语义时才进行转换 (`try_cast` 以抑制错误)。
- 阅读 [references/functions-guide.md](references/functions-guide.md) 了解不寻常的函数选择（聚合、JSON、正则表达式、日期时间、IP 地理位置等）

#### 3.3 追加 SPL——用于行级处理 / 灵活过滤

```spl
status: 500 and service: payment
| where try_cast(latency as BIGINT) > 1000
| extend latency_ms = try_cast(latency as BIGINT)
| project service, latency_ms, message
```

有关 SPL 语法、管道命令和字段处理规则，请参阅 [references/spl-guide.md](references/spl-guide.md)。

#### 3.4 追加 SQL scan——当目标字段没有索引 / 统计时作为后备

语法遵循常规 SQL（见 3.2），但有一个区别：**每个字段都是 `varchar`**，因此始终 `cast()` / `try_cast()` 才能进行数值比较或算术运算。有关扫描语义，请参阅 [references/query-analysis.md](references/query-analysis.md)。

```sql
* | set session mode=scan; SELECT api, count(1) AS pv FROM log GROUP BY api
```

---

### 步骤 4：解析时间范围

在构建 CLI 命令之前，生成 `--from` / `--to` 作为 **Unix 时间戳（秒）**。`--from` 是包含的，`--to` 是不包含的。

选择以下三种输入模式之一：

1. **相对时间**——用户说“最近 / 最后 N 分钟|小时|天”。
2. **不含时区的自然语言绝对时间**——规范化为 `YYYY-MM-DD HH:MM:SS`，然后使用机器的本地时区解析。
3. **带明确时区的绝对时间**——使用客户提供的时区或 UTC 偏移解析。

**1. 相对时间**

```bash
# recent 15 minutes
FROM=$(($(date +%s) - 900))
TO=$(date +%s)
```

**2. 不含时区的自然语言绝对时间**

如果用户给出日期/时间但没有时区，使用机器的本地时区。首先将自然语言（如 `2026年3月13日12点`）规范化为 `2026-03-13 12:00:00`，然后将其作为本地时间解析。

```bash
# 示例：2026年3月13日12点 -> 2026-03-13 12:00:00

# Linux (GNU date): 本地时区
FROM=$(date -d "2026-03-13 12:00:00" +%s)

# macOS (BSD date): 本地时区
FROM=$(date -j -f "%Y-%m-%d %H:%M:%S" "2026-03-13 12:00:00" +%s)
```

对于“2026年3月13日12点到13点”这样的时间范围，以相同方式计算两个端点。对于单点时间请求，根据用户的意图推断一个实用窗口；如果不清楚，请在执行前要求范围。

**3. 带明确时区的绝对时间**

要将本地日期/时间转换为 Unix 时间戳：将输入作为 UTC 解析 `date -u`，然后 **减去** 时区的 UTC 偏移（秒）。

公式：`unix_ts = date_utc_parse(input) − (UTC_offset_hours × 3600)`

```bash
# 示例：2025-01-15 10:30:00 北京时间（UTC+8）
# 北京是 UTC+8，所以减去 8 × 3600 = 28800

# Linux (GNU date)
FROM=$(( $(date -u -d "2025-01-15 10:30:00" +%s) - 28800 ))

# macOS (BSD date)
FROM=$(( $(date -u -j -f "%Y-%m-%d %H:%M:%S" "2025-01-15 10:30:00" +%s) - 28800 ))
```

```bash
# 示例：2025-01-15 10:30:00 纽约时间（UTC-5）
# 纽约是 UTC-5，所以减去 -5 × 3600 = 减去 -18000 = 加 18000

# Linux (GNU date)
FROM=$(( $(date -u -d "2025-01-15 10:30:00" +%s) + 18000 ))

# macOS (BSD date)
FROM=$(( $(date -u -j -f "%Y-%m-%d %H:%M:%S" "2025-01-15 10:30:00" +%s) + 18000 ))
```

常见 UTC 偏移（要减去的值）：

| 时区         | UTC 偏移小时 | 减去秒数 |
|--------------|--------------|----------|
| 北京（UTC+8）  | +8           | `28800`  |
| 东京（UTC+9）    | +9           | `32400`  |
| 伦敦（UTC）     | 0            | `0`      |
| 纽约（UTC-5）    | -5           | `-18000` |

---

### 步骤 5：通过 `get-logs-v2` 执行

使用 `aliyun sls get-logs-v2` 执行查询。运行 `aliyun help sls get-logs-v2` 查看CLI参数用法；阅读 [references/related-apis.md](references/related-apis.md) 了解详细的 API 参数描述。

**必须的 CLI 标志：**

- `--project`：SLS 项目名称
- `--logstore`：项目内的 Logstore 名称
- `--from`：时间范围的开始，**Unix 时间戳（秒）**（包含）
- `--to`：时间范围的结束，**Unix 时间戳（秒）**（不包含）
- `--query`：步骤 3 中构建的语句

分页方式根据语句是否包含 `|` 而不同：

#### 5.1 仅索引搜索——使用 `--offset` / `--line` 分页

```bash
aliyun sls get-logs-v2 \
  --project my-project --logstore my-logstore \
  --from 1740000000 --to 1740003600 \
  --query '* and "payment failed" and status: "500"' \
  --line 100 --offset 0 --reverse true
```

- 分页：`--line` 是页大小 (`1–100`，必须)；`--offset` 是起始行（可选，默认 `0`）。
- 排序：`--reverse true` 返回最新优先；默认 `false` 是最早优先。

#### 5.2 带SQL——使用语句内的 `LIMIT` 分页

```bash
aliyun sls get-logs-v2 \
  --project my-project --logstore my-logstore \
  --from 1740000000 --to 1740003600 \
  --query 'status: "500" | SELECT request_uri, count(*) AS cnt FROM log GROUP BY request_uri ORDER BY cnt DESC LIMIT 20'
```

- SQL 默认结果限制为 **100 行**。要获取更多结果或分页：
  - `LIMIT count`——提高限制（例如，`LIMIT 500` 返回最多 500 行）
  - `LIMIT offset, count`——分页（例如，`LIMIT 20, 20` 获取行 21–40；`LIMIT 40, 20` 获取行 41–60）。最大 offset+count 是 1000000。
  - **不要** 使用 `LIMIT count OFFSET offset` 语法——它**不被支持**。始终使用 `LIMIT offset, count`。
- 排序：使用 `ORDER BY <field> DESC/ASC` 排序。

**结果完整性检查：** 每个响应都包含 `meta.progress`。如果它是 `Incomplete`，**重新发出相同的请求** 直到它返回 `Complete`。

---

### 步骤 6：从响应中提取数据

`get-logs-v2` 返回：

```json
{
  "meta": { "progress": "Complete", "count": 10, ... },
  "data": [ { "field1": "value1", ... }, ... ]
}
```

| 字段 | 含义 |
|------|------|
| `meta.progress` | `Complete` 或 `Incomplete`（见步骤 5） |
| `meta.count` | 返回的行数 |
| `data` | 日志条目或聚合行的数组；可能包含 `__time__`（Unix 秒，字符串） |

使用 `jq`（推荐）或 `--cli-query`（JMESPath）提取用户需要的字段：

| 提取 | `jq` | `--cli-query` (JMESPath) |
|------|------|--------------------------|
| 数据行 | `\| jq '.data'` | `--cli-query 'data'` |
| 进度 | `\| jq '.meta.progress'` | `--cli-query 'meta.progress'` |
| 行数 | `\| jq '.meta.count'` | `--cli-query 'meta.count'` |
| 特定字段 | `\| jq '.data[] \| {LogStore, read_mb}'` | `--cli-query 'data[].{LogStore: LogStore, read_mb: read_mb}'` |

---

### 步骤 7：展示 CLI 命令和结果

**CLI 命令**——始终显示完整的、可复制粘贴的 `aliyun sls get-logs-v2 ...` 命令。遮盖任何 AK/SK。如果查询未执行（写 / 解释场景），请显示用户应运行的命令。

**结果**——当执行查询时，使用步骤 6 提取 `data` 并根据用户请求（表格、列表、摘要等）格式化。附加一句解释查询模式的选择。

---

## 全局规则

- **始终优先选择索引搜索以获得最快的原始日志检索，并使用索引搜索 + SQL 进行分析或字段投影。**
- **当用户只需要特定字段时，使用 `SELECT` 进行投影** 而不是检索完整原始日志——这会减少网络开销。需要目标字段具有 `doc_value: true`（在步骤 1 中确认）。
- **不要** 硬编码 `__time__` 过滤器——通过 `--from` / `--to` 传递时间范围。
- **已弃用的 API**：永远不要调用 `get-logs`；始终使用 `get-logs-v2`。

---

## 故障排除

当用户报告“无数据”、“结果错误”或 CLI 错误时，按此顺序逐一检查清单：

1. **时间范围**——`--from`/`--to` 错误？毫秒而不是秒？最近的写入仍在索引中？
2. **索引配置**——字段索引缺失？全文索引关闭？目标字段不在 `keys` 中？
3. **字段类型 / 统计**——在 `text` 字段上进行范围查询？在缺少 `doc_value` 的字段上进行 SQL？
4. **语法**——混合 SQL 和 SPL？模糊匹配中的前导 `*`？SPL 字符串转义？
5. **模式选择**——扫描时索引查询会更好？在 SPL 中而不是 SQL 中进行聚合？
6. **完整性**——`meta.progress = Incomplete`，调用者未重试（见步骤 5）。
7. **ProjectNotExist**——区域或端点错误。使用跨区域发现自动定位项目，或要求用户确认区域。**在调用 `get-project --cross-region true` 之前，你必须阅读 [references/regions.md](references/regions.md) 中的跨区域发现部分**——此 API 仅通过 `cn-zhangjiakou.log.aliyuncs.com` 端点可用。
8. **网络故障**（超时、连接被拒绝）——尝试切换到内部端点。见 [references/regions.md](references/regions.md)。

有关完整故障模式和错误代码目录，请参阅 [references/troubleshooting.md](references/troubleshooting.md) 和 [references/related-apis.md](references/related-apis.md) 中的 `Common Errors` 表。

---

## 参考文档

| 文档 | 描述 |
|------|------|
| [references/query-analysis.md](references/query-analysis.md) | 模式决策、索引搜索 / SQL 规则、扫描语义 |
| [references/spl-guide.md](references/spl-guide.md) | SPL 管道语法、常用命令、字段处理 |
| [references/functions-guide.md](references/functions-guide.md) | 函数类别、SQL/SPL 区别、模板 |
| [references/troubleshooting.md](references/troubleshooting.md) | “无数据 / 结果错误 / 错误”剧本 |
| [references/related-apis.md](references/related-apis.md) | `GetLogsV2` 和 `GetIndex` API & CLI 参考 |
| [references/ram-policies.md](references/ram-policies.md) | 最小和完整的 RAM 策略 |
| [references/cli-installation-guide.md](references/cli-installation-guide.md) | Aliyun CLI 安装、认证模式、配置文件 |
| [references/regions.md](references/regions.md) | 区域 / 端点配置、内部端点、跨区域发现 (`get-project --cross-region true`，**仅 cn-zhangjiakou**) |
| [references/acceptance-criteria.md](references/acceptance-criteria.md) | CLI 调用验收测试 |
| `references/query_analysis/*.yaml` · `references/spl/*.yaml` · `references/functions/*.yaml` | 随此技能捆绑的源真 YAMLs |
