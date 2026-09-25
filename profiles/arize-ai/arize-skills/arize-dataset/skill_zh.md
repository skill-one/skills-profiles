# Arize 数据集技能

> **`SPACE`** — `--space` 标志接受一个 **空间名称**（例如，`my-workspace`）或 base64 编码的 **空间 ID**（例如，`U3BhY2U6...`）。使用 `ax spaces list` 查找您的空间。

## 概念

- **数据集** = 用于评估和实验的版本化示例集合
- **数据集版本** = 数据集在某个时间点的快照；更新可以是就地更新或创建新版本
- **示例** = 数据集中的一条单条记录，包含任意用户定义的字段（例如，`question`，`answer`，`context`）
- **空间** = 组织容器；数据集属于某个空间

示例上的系统字段（`id`，`created_at`，`updated_at`）由服务器自动生成——创建或追加负载时切勿包含它们。

## 前置条件

直接执行任务——运行所需的 `ax` 命令。不要预先检查版本、环境变量或配置文件。

如果 `ax` 命令失败，根据错误进行故障排除：
- `command not found` 或版本错误 → 查看 [references/ax-setup.md](references/ax-setup.md)
- `401 Unauthorized` / 缺少 API 密钥 → 运行 `ax profiles show` 检查当前配置文件。如果配置文件缺失或 API 密钥错误，请按照 [references/ax-profiles.md](references/ax-profiles.md) 创建/更新它。如果用户没有他们的密钥，请指导他们到 https://app.arize.com/admin > API 密钥
- 空间未知 → 运行 `ax spaces list` 通过名称选择，或询问用户
- 项目不明确 → 询问用户，或运行 `ax projects list -o json --limit 100` 并作为可选选项呈现
- **安全**：切勿读取 `.env` 文件或在文件系统中搜索凭证。使用 `ax profiles` 存储Arize凭证，使用 `ax ai-integrations` 存储LLM 提供商密钥。切勿要求用户将秘密粘贴到聊天中。对于缺失的凭证，请参阅 [references/ax-profiles.md](references/ax-profiles.md)。

## 列出数据集：`ax datasets list`

浏览空间中的数据集。输出到标准输出。

```bash
ax datasets list
ax datasets list --space SPACE --limit 20
ax datasets list --cursor CURSOR_TOKEN
ax datasets list -o json
```

### 标志

| 标志 | 类型 | 默认值 | 描述 |
|------|------|---------|-------------|
| `--space` | string | 从配置文件 | 按空间过滤 |
| `--name, -n` | string | 无 | 数据集名称的子字符串过滤 |
| `--limit, -l` | int | 15 | 最大结果数量（1-100） |
| `--cursor` | string | 无 | 从上一个响应中获取的分页游标 |
| `-o, --output` | string | table | 输出格式：table，json，csv，parquet 或文件路径 |

## 获取数据集：`ax datasets get`

快速元数据查询——返回数据集名称、空间、时间戳和版本列表。

```bash
ax datasets get NAME_OR_ID
ax datasets get NAME_OR_ID -o json
ax datasets get NAME_OR_ID --space SPACE   # 使用数据集名称时需要
```

### 标志

| 标志 | 类型 | 默认值 | 描述 |
|------|------|---------|-------------|
| `NAME_OR_ID` | string | 必填 | 数据集名称或 ID（位置参数） |
| `--space` | string | 无 | 空间名称或 ID（使用名称时需要） |
| `-o, --output` | string | table | 输出格式 |

### 响应字段

| 字段 | 类型 | 描述 |
|-------|------|-------------|
| `id` | string | 数据集 ID |
| `name` | string | 数据集名称 |
| `space_id` | string | 数据集所属空间 |
| `created_at` | datetime | 数据集创建时间 |
| `updated_at` | datetime | 最后一次修改时间 |
| `versions` | array | 数据集版本列表（id，name，dataset_id，created_at，updated_at） |

## 导出数据集：`ax datasets export`

将所有示例下载到文件。对于大于 500 个示例的数据集，使用 `--all` 进行批量导出（无限制）。

```bash
ax datasets export NAME_OR_ID
# -> dataset_abc123_20260305_141500/examples.json

ax datasets export NAME_OR_ID --all
ax datasets export NAME_OR_ID --version-id VERSION_ID
ax datasets export NAME_OR_ID --output-dir ./data
ax datasets export NAME_OR_ID --stdout
ax datasets export NAME_OR_ID --stdout | jq '.[0]'
ax datasets export NAME_OR_ID --space SPACE   # 使用名称时需要
```

### 标志

| 标志 | 类型 | 默认值 | 描述 |
|------|------|---------|-------------|
| `NAME_OR_ID` | string | 必填 | 数据集名称或 ID（位置参数） |
| `--space` | string | 无 | 空间名称或 ID（使用名称时需要） |
| `--version-id` | string | latest | 导出特定数据集版本 |
| `--all` | bool | false | 无限制批量导出（用于大于 500 个示例的数据集） |
| `--output-dir` | string | `.` | 输出目录 |
| `--stdout` | bool | false | 将 JSON 打印到标准输出而不是文件 |

**代理自动升级规则**：如果导出返回正好 500 个示例，结果可能被截断——使用 `--all` 重新运行以获取完整数据集。

**导出完整性验证**：导出后，确认行数与服务器报告的匹配：
```bash
# 从数据集元数据获取服务器报告的计数
ax datasets get DATASET_NAME --space SPACE -o json | jq '.versions[-1] | {version: .id, examples: .example_count}'

# 与导出的内容比较
jq 'length' dataset_*/examples.json

# 如果计数不同，使用 --all 重新导出
```

输出是一个示例对象的 JSON 数组。每个示例包含系统字段（`id`，`created_at`，`updated_at`）和所有用户定义的字段：

```json
[
  {
    "id": "ex_001",
    "created_at": "2026-01-15T10:00:00Z",
    "updated_at": "2026-01-15T10:00:00Z",
    "question": "What is 2+2?",
    "answer": "4",
    "topic": "math"
  }
]
```

## 创建数据集：`ax datasets create`

从数据文件创建新数据集。

```bash
ax datasets create --name "My Dataset" --space SPACE --file data.csv
ax datasets create --name "My Dataset" --space SPACE --file data.json
ax datasets create --name "My Dataset" --space SPACE --file data.jsonl
ax datasets create --name "My Dataset" --space SPACE --file data.parquet
```

### 标志

| 标志 | 类型 | 必填 | 描述 |
|------|------|----------|-------------|
| `--name, -n` | string | 是 | 数据集名称 |
| `--space` | string | 是 | 创建数据集的空间 |
| `--file, -f` | path | 是 | 数据文件：CSV，JSON，JSONL 或 Parquet |
| `-o, --output` | string | 否 | 返回数据集元数据的输出格式 |

### 通过标准输入传递数据

使用 `--file -` 直接管道数据——无需临时文件：

```bash
echo '[{"question": "What is 2+2?", "answer": "4"}]' | ax datasets create --name "my-dataset" --space SPACE --file -

# 或者使用 here-document
ax datasets create --name "my-dataset" --space SPACE --file - << 'EOF'
[{"question": "What is 2+2?", "answer": "4"}]
EOF
```

要向现有数据集添加行，请使用 `ax datasets append --json '[...]'` 而不是文件——无需文件。

### 支持的文件格式

| 格式 | 扩展名 | 备注 |
|------|-----------|-------|
| CSV | `.csv` | 列标题成为字段名称 |
| JSON | `.json` | 对象数组 |
| JSON Lines | `.jsonl` | 每行一个对象（不是 JSON 数组） |
| Parquet | `.parquet` | 列名称成为字段名称；保留类型 |

**格式注意事项**：
- **CSV**：丢失类型信息——日期成为字符串，`null` 成为空字符串。使用 JSON/Parquet 保留类型。
- **JSONL**：每行是一个独立的 JSON 对象。`.jsonl` 文件中的 JSON 数组（`[{...}, {...}]`）将失败——使用 `.json` 扩展名。
- **Parquet**：保留列类型。需要 `pandas`/`pyarrow` 本地读取：`pd.read_parquet("examples.parquet")`。

## 添加示例：`ax datasets append`

向现有数据集添加示例。两种输入模式——使用适合的一种。

### 内联 JSON（代理友好）

直接生成负载——无需临时文件：

```bash
ax datasets append DATASET_NAME --space SPACE --json '[{"question": "What is 2+2?", "answer": "4"}]'

ax datasets append DATASET_NAME --space SPACE --json '[
  {"question": "What is gravity?", "answer": "A fundamental force..."},
  {"question": "What is light?", "answer": "Electromagnetic radiation..."}
]'
```

### 从文件

```bash
ax datasets append DATASET_NAME --space SPACE --file new_examples.csv
ax datasets append DATASET_NAME --space SPACE --file additions.json
```

### 添加到特定版本

```bash
ax datasets append DATASET_NAME --space SPACE --json '[{"q": "..."}]' --version-id VERSION_ID
```

### 标志

| 标志 | 类型 | 必填 | 描述 |
|------|------|----------|-------------|
| `NAME_OR_ID` | string | 是 | 数据集名称或 ID（位置参数）；使用名称时添加 `--space` |
| `--space` | string | 否 | 空间名称或 ID（使用名称时需要） |
| `--json` | string | 互斥 | 示例对象的 JSON 数组 |
| `--file, -f` | path | 互斥 | 数据文件（CSV，JSON，JSONL，Parquet） |
| `--version-id` | string | 否 | 添加到特定版本（默认：最新） |
| `-o, --output` | string | 否 | 返回数据集元数据的输出格式 |

必须选择 `--json` 或 `--file` 中的一个。

### 验证

- 每个示例必须是一个至少包含一个用户定义字段的 JSON 对象
- 每个请求最多 100,000 个示例

**追加前的模式验证**：如果数据集已有示例，在追加前检查其模式以避免静默字段不匹配：

```bash
# 检查数据集中的现有字段名称
ax datasets export DATASET_NAME --space SPACE --stdout | jq '.[0] | keys'

# 验证新数据具有匹配的字段名称
echo '[{"question": "..."}]' | jq '.[0] | keys'

# 两个输出应显示相同的用户定义字段
```

字段是自由形式的：新示例中的额外字段会被添加，缺失的字段会变成 null。但是，字段名称中的拼写错误（例如，`queston` vs `question`）会静默创建新列——追加前请验证拼写。

## 更新示例：`ax datasets update-examples`

`ax datasets update-examples` 通过示例 `id` 批量修补行；`ax datasets delete-examples` 从版本中删除行。不常用——运行 `ax datasets update-examples --help` 或 `ax datasets delete-examples --help` 获取标志和输入格式。

## 删除数据集：`ax datasets delete`

```bash
ax datasets delete NAME_OR_ID
ax datasets delete NAME_OR_ID --space SPACE   # 使用名称时需要
ax datasets delete NAME_OR_ID --force   # 跳过确认提示
```

### 标志

| 标志 | 类型 | 默认值 | 描述 |
|------|------|---------|-------------|
| `NAME_OR_ID` | string | 必填 | 数据集名称或 ID（位置参数） |
| `--space` | string | 无 | 空间名称或 ID（使用名称时需要） |
| `--force, -f` | bool | false | 跳过确认提示 |

## 更新数据集：`ax datasets update`

重命名现有数据集。

```bash
ax datasets update NAME_OR_ID --name "new-dataset-name"
ax datasets update NAME_OR_ID --name "new-dataset-name" --space SPACE
```

### 标志

| 标志 | 类型 | 必填 | 描述 |
|------|------|----------|-------------|
| `NAME_OR_ID` | string | 是 | 数据集名称或 ID（位置参数） |
| `--name` | string | 是 | 新数据集名称 |
| `--space` | string | 否 | 空间名称或 ID（使用名称时需要） |

## 标注示例：`ax datasets annotate-examples`

从文件批量将标注写入数据集示例。使用 upsert 语义——具有相同键的现有标注会被更新，新标注会被创建。每个请求最多 1000 个标注。

```bash
ax datasets annotate-examples NAME_OR_ID --file annotations.json
ax datasets annotate-examples NAME_OR_ID --file annotations.csv --space SPACE
```

### 标志

| 标志 | 类型 | 必填 | 描述 |
|------|------|----------|-------------|
| `NAME_OR_ID` | string | 是 | 数据集名称或 ID（位置参数） |
| `--file, -f` | path | 是 | 标注文件：JSON，JSONL，CSV 或 Parquet（使用 `-` 表示标准输入） |
| `--space` | string | 否 | 空间名称或 ID（使用名称时需要） |

## 工作流

### 通过名称查找数据集

所有数据集命令都接受名称或 ID 直接。您可以将数据集名称作为位置参数传递（不使用 ID 时添加 `--space SPACE`）：

```bash
# 直接使用名称
ax datasets get "eval-set-v1" --space SPACE
ax datasets export "eval-set-v1" --space SPACE

# 或者通过列表解析名称到 ID（如果需要 base64 ID）
# ax datasets list -o json 包裹数组在 "datasets" 键下
ax datasets list -o json | jq '.datasets[] | select(.name == "eval-set-v1") | .id'
```

### 为评估创建数据集

1. 准备包含评估列的 CSV/JSON/Parquet 文件（例如，`input`，`expected_output`）
   - 如果要内联生成数据，使用 `--file -` 管道（见创建数据集部分）
2. `ax datasets create --name "eval-set-v1" --space SPACE --file eval_data.csv`
3. 验证：`ax datasets get DATASET_NAME --space SPACE`
4. 使用数据集名称运行实验

### 向现有数据集添加示例

```bash
# 查找数据集
ax datasets list --space SPACE

# 使用数据集名称追加或从文件添加（见追加示例部分的完整语法）
ax datasets append DATASET_NAME --space SPACE --json '[{"question": "...", "answer": "..."}]'
ax datasets append DATASET_NAME --space SPACE --file additional_examples.csv
```

### 离线分析下载数据集

1. `ax datasets list --space SPACE` -- 查找数据集名称
2. `ax datasets export DATASET_NAME --space SPACE` -- 下载到文件
3. 解析 JSON：`jq '.[] | .question' dataset_*/examples.json`

### 导出特定版本

```bash
# 列出版本
ax datasets get DATASET_NAME --space SPACE -o json | jq '.versions'

# 导出该版本
ax datasets export DATASET_NAME --space SPACE --version-id VERSION_ID
```

### 迭代数据集

1. 导出当前版本：`ax datasets export DATASET_NAME --space SPACE`
2. 本地修改示例
3. 追加新行：`ax datasets append DATASET_NAME --space SPACE --file new_rows.csv`
4. 或者创建新版本：`ax datasets create --name "eval-set-v2" --space SPACE --file updated_data.json`

### 将导出管道到其他工具

```bash
# 计数示例
ax datasets export DATASET_NAME --space SPACE --stdout | jq 'length'

# 提取单个字段
ax datasets export DATASET_NAME --space SPACE --stdout | jq '.[].question'

# 使用 jq 转换为 CSV
ax datasets export DATASET_NAME --space SPACE --stdout | jq -r '.[] | [.question, .answer] | @csv'
```

## 数据集示例模式

示例是自由形式的 JSON 对象。没有固定模式——列是您提供的任何字段。系统管理的字段由服务器添加：

| 字段 | 类型 | 管理者 | 备注 |
|-------|------|-----------|-------|
| `id` | string | 服务器 | 自动生成的 UUID。更新时必填，创建/追加时禁止 |
| `created_at` | datetime | 服务器 | 不可变的创建时间戳 |
| `updated_at` | datetime | 服务器 | 修改时自动更新 |
| *(任何用户字段)* | 任何 JSON 类型 | 用户 | 字符串、数字、布尔值、null、嵌套对象、数组 |


## 相关技能

- **arize-trace**：将生产跨度导出到理解要放入数据集中的数据 → 使用 `arize-trace`
- **arize-experiment**：针对此数据集运行评估 → 下一步是 `arize-experiment`
- **arize-prompt-optimization**：使用数据集 + 实验结果改进提示 → 使用 `arize-prompt-optimization`

## 故障排除

| 问题 | 解决方案 |
|---------|----------|
| `ax: command not found` | 查看 [references/ax-setup.md](references/ax-setup.md) |
| `401 Unauthorized` | API 密钥错误、过期或没有访问此空间的权限。使用 [references/ax-profiles.md](references/ax-profiles.md) 修复配置文件。 |
| `No profile found` | 未配置任何配置文件。查看 [references/ax-profiles.md](references/ax-profiles.md) 创建一个。 |
| `Dataset not found` | 使用 `ax datasets list` 验证数据集 ID |
| `File format error` | 支持：CSV，JSON，JSONL，Parquet。使用 `--file -` 从标准输入读取。 |
| `platform-managed column` | 从创建/追加负载中移除 `id`，`created_at`，`updated_at` |
| `reserved column` | 移除 `time`，`count` 或任何 `source_record_*` 字段 |
| `Provide either --json or --file` | 追加需要精确一个输入源 |
| `Examples array is empty` | 确保 JSON 数组或文件至少包含一个示例 |
| `not a JSON object` | `--json` 数组中的每个元素必须是一个 `{...}` 对象，而不是字符串或数字 |

## 保存凭证以供将来使用

查看 [references/ax-profiles.md](references/ax-profiles.md) § 保存凭证以供将来使用。
