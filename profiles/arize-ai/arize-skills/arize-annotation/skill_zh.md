# Arize 标注技能

> **`SPACE`** — `--space` 标志接受一个 **空间名称**（例如，`my-workspace`）或 base64 编码的 **空间 ID**（例如，`U3BhY2U6...`）。使用 `ax spaces list` 查找您的空间。

此技能涵盖 **标注配置**（标签模式）和 **标注队列**（人工审核工作流），以及通过 Python SDK 程序化标注项目跨度。

**方向**：在 Arize 中，人工标注将配置定义的值附加到产品 UI 中的 **跨度**、**数据集示例**、**实验相关记录** 和 **队列项**。此技能涵盖：`ax annotation-configs`、`ax annotation-queues`，以及使用 `ArizeClient.spans.update_annotations` 批量更新跨度。

---

## 前置条件

直接执行任务 — 运行您需要的 `ax` 命令。**不要**提前检查版本、环境变量或配置文件。

如果 `ax` 命令失败，根据错误进行故障排除：
- `command not found` 或版本错误 → 查看 [references/ax-setup.md](references/ax-setup.md)
- `401 Unauthorized` / 缺少 API 密钥 → 运行 `ax profiles show` 检查当前配置文件。如果配置文件缺失或 API 密钥错误，请按照 [references/ax-profiles.md](references/ax-profiles.md) 创建/更新它。如果用户没有他们的密钥，请指导他们访问 https://app.arize.com/admin > API 密钥
- 空间未知 → 运行 `ax spaces list` 通过名称选择，或询问用户
- **安全**：**永远不要**读取 `.env` 文件或在文件系统中搜索凭证。使用 `ax profiles` 存储Arize凭证，使用 `ax ai-integrations` 存储LLM 提供商密钥。**永远不要**要求用户将秘密粘贴到聊天中。对于缺失的凭证，请参阅 [references/ax-profiles.md](references/ax-profiles.md)。

---

## 概念

### 什么是标注配置？

**标注配置** 定义了单个人工反馈标签的架构。在任何人可以标注跨度、数据集记录、实验输出或队列项之前，该空间中必须存在该标签的配置。

| 字段 | 描述 |
|-------|-------------|
| **名称** | 描述性标识符（例如，`正确性`，`帮助性`）。在空间内必须唯一。 |
| **类型** | `CATEGORICAL`（从列表中选择），`CONTINUOUS`（数值范围），或 `FREEFORM`（自由文本）。 |
| **值** | 对于分类：`{"label": str, "score": number}` 对的数组。 |
| **最小/最大分数** | 对于连续：数值边界。 |
| **优化方向** | 分数越高越好（`MINIMIZE`）还是越差（`MAXIMIZE`）。用于在 UI 中显示趋势。 |

### 标签应用的位置（表面）

| 表面 | 典型路径 |
|---------|----------------|
| **项目跨度** | Python SDK `spans.update_annotations`（下方）和/或 Arize UI |
| **数据集示例** | Arize UI（人工标注流程）；配置文件必须在空间中存在 |
| **实验输出** | 通常与数据集或跟踪一起在 UI 中审查 — 查看 arize-experiment，arize-dataset |
| **标注队列项** | `ax annotation-queues` CLI（下方）和/或 Arize UI；配置文件必须在空间中存在 |

始终确保在期望标签持久化之前，相关 **标注配置** 在空间中存在。

---

## 基本增删改查：标注配置

### 列出

```bash
ax annotation-configs list --space SPACE
ax annotation-configs list --space SPACE -o json
ax annotation-configs list --space SPACE --limit 20
ax annotation-configs list --space SPACE --name "Correctness"   # 子字符串过滤
```

### 创建 — 分类

分类配置向审阅者提供一组固定的标签供选择。

```bash
ax annotation-configs create categorical \
  --name "Correctness" \
  --space SPACE \
  --value correct \
  --value incorrect \
  --optimization-direction MAXIMIZE
```

常见的二元标签对：
- `correct` / `incorrect`
- `helpful` / `unhelpful`
- `safe` / `unsafe`
- `relevant` / `irrelevant`
- `pass` / `fail`

### 创建 — 连续

连续配置允许审阅者在定义的范围内输入数值分数。

```bash
ax annotation-configs create continuous \
  --name "Quality Score" \
  --space SPACE \
  --min-score 0 \
  --max-score 10 \
  --optimization-direction MAXIMIZE
```

### 创建 — 自由文本

自由文本配置收集开放式文本反馈。除了名称和空间之外，无需其他标志。

```bash
ax annotation-configs create freeform \
  --name "Reviewer Notes" \
  --space SPACE
```

### 获取

```bash
ax annotation-configs get NAME_OR_ID
ax annotation-configs get NAME_OR_ID -o json
ax annotation-configs get NAME_OR_ID --space SPACE   # 使用名称时需要
```

### 更新

每种配置类型都有自己的更新命令。仅更新已更改的字段。

**自由文本:**

```bash
ax annotation-configs update freeform NAME_OR_ID --space SPACE --new-name "Updated Name"
```

**连续:**

```bash
ax annotation-configs update continuous NAME_OR_ID --space SPACE --min-score 1 --max-score 5 --optimization-direction MINIMIZE
```

**分类:**

```bash
ax annotation-configs update categorical NAME_OR_ID --space SPACE --value correct --value incorrect --optimization-direction MAXIMIZE
```

`--space` 在使用名称时需要。每个 `--value` 提供完整的分类标签列表：它替换现有标签而不是追加到它们。重复 `--value` 以保留所有应保留的标签，或省略标签将被删除。

### 删除

```bash
ax annotation-configs delete NAME_OR_ID
ax annotation-configs delete NAME_OR_ID --space SPACE   # 使用名称时需要
ax annotation-configs delete NAME_OR_ID --force   # 跳过确认
```

**注意**：删除不可逆。与此配置相关的任何标注队列关联在产品中也会被删除（队列可能仍然存在；如果需要，请在 Arize UI 中修复关联）。

---

## 标注队列：`ax annotation-queues`

标注队列将记录（跨度、数据集示例、实验运行）路由到人工审阅者。每个队列都链接到一个或多个标注配置，这些配置定义了审阅者可以应用的标签。

### 列出/获取

```bash
ax annotation-queues list --space SPACE
ax annotation-queues list --space SPACE -o json
ax annotation-queues list --space SPACE --name "Review"   # 子字符串过滤

ax annotation-queues get NAME_OR_ID --space SPACE
ax annotation-queues get NAME_OR_ID --space SPACE -o json
```

### 创建

至少需要一个 `--annotation-config-id`。

```bash
ax annotation-queues create \
  --name "Correctness Review" \
  --space SPACE \
  --annotation-config-id CONFIG_ID \
  --annotator-email reviewer@example.com \
  --instructions "将每个响应标记为正确或错误。" \
  --assignment-method ALL   # 或：RANDOM
```

重复 `--annotation-config-id` 和 `--annotator-email` 以附加多个配置或审阅者。

### 添加记录

创建后向现有队列添加记录。记录可以来自跨度（通过项目和时间段）或数据集示例。

```bash
ax annotation-queues add-records NAME_OR_ID --space SPACE --record-sources sources.json

ax annotation-queues add-records NAME_OR_ID --space SPACE \
  --record-sources '[{"record_type": "EXAMPLE", "dataset_id": "ds-1", "example_ids": ["ex-1", "ex-2"]}]'
```

`--record-sources` 是必需的，并接受 JSON 文件路径或内联 JSON 数组。每个源指定 `record_type` (`SPAN` 或 `EXAMPLE`) 以及类型特定的字段：
- **跨度**：`project_id`，`start_time`（ISO 8601），`end_time`（ISO 8601），可选 `span_ids`
- **示例**：`dataset_id`，`example_ids`

### 更新

列表标志（`--annotation-config-id`，`--annotator-email`）在提供时**完全替换**现有值 — 传递所有所需值，而不仅仅是新值。

```bash
ax annotation-queues update NAME_OR_ID --space SPACE --name "New Name"
ax annotation-queues update NAME_OR_ID --space SPACE --instructions "Updated instructions"
ax annotation-queues update NAME_OR_ID --space SPACE \
  --annotation-config-id CONFIG_ID_A \
  --annotation-config-id CONFIG_ID_B
```

### 删除

```bash
ax annotation-queues delete NAME_OR_ID --space SPACE
ax annotation-queues delete NAME_OR_ID --space SPACE --force   # 跳过确认
```

### 列出记录

```bash
ax annotation-queues list-records NAME_OR_ID --space SPACE
ax annotation-queues list-records NAME_OR_ID --space SPACE --limit 50 -o json
```

### 提交记录的标注

标注通过配置名称进行 upsert — 每个标注配置调用一次。至少提供 `--score`、`--label` 或 `--text` 中的一个。

```bash
ax annotation-queues annotate-record NAME_OR_ID RECORD_ID \
  --annotation-name "Correctness" \
  --label "correct" \
  --space SPACE

ax annotation-queues annotate-record NAME_OR_ID RECORD_ID \
  --annotation-name "Quality Score" \
  --score 8.5 \
  --text "响应准确但稍显冗长。" \
  --space SPACE
```

### 分配记录

通过重复 `--email` 将用户分配到审查特定记录；这完全替换现有的分配，因此每次传递所有指派者（传递没有 `--email` 标志将清除所有分配）：

```bash
ax annotation-queues assign-record NAME_OR_ID RECORD_ID --email user@example.com --space SPACE
```

### 删除记录

```bash
ax annotation-queues delete-records NAME_OR_ID --space SPACE
```

---

## 将标注应用于跨度（Python SDK）

使用 Python SDK 在您已经拥有标签（例如，从审查导出或外部标注工具）时，批量将标注应用于 **项目跨度**。

```python
import pandas as pd
from arize import ArizeClient

import os

client = ArizeClient(api_key=os.environ["ARIZE_API_KEY"])

# 构建包含标注列的 DataFrame
# 必须有 context.span_id + 至少一个 annotation.<name>.label 或 annotation.<name>.score
annotations_df = pd.DataFrame([
    {
        "context.span_id": "span_001",
        "annotation.Correctness.label": "correct",
        "annotation.Correctness.updated_by": "reviewer@example.com",
    },
    {
        "context.span_id": "span_002",
        "annotation.Correctness.label": "incorrect",
        "annotation.Correctness.updated_by": "reviewer@example.com",
    },
])

response = client.spans.update_annotations(
    space_id=os.environ["ARIZE_SPACE_ID"],
    project_name="your-project",
    dataframe=annotations_df,
    validate=True,
)
```

**DataFrame 列架构:**

| 列 | 必须有 | 描述 |
|--------|----------|-------------|
| `context.span_id` | 是 | 要标注的跨度 |
| `annotation.<name>.label` | 其中之一 | 分类或自由文本标签 |
| `annotation.<name>.score` | 其中之一 | 数值分数 |
| `annotation.<name>.updated_by` | 否 | 标注者标识符（电子邮件或名称） |
| `annotation.<name>.updated_at` | 否 | 自 Unix 纪元以来的毫秒时间戳 |
| `annotation.notes` | 否 | 跨度的自由文本备注 |

**限制**：标注仅适用于提交前 31 天内的跨度。

---

## 故障排除

| 问题 | 解决方案 |
|---------|----------|
| `ax: command not found` | 查看 [references/ax-setup.md](references/ax-setup.md) |
| `401 Unauthorized` | API 密钥可能没有访问此空间的权限。在 https://app.arize.com/admin > API 密钥中验证 |
| `Annotation config not found` | `ax annotation-configs list --space SPACE`（或使用 `ax annotation-configs get NAME_OR_ID --space SPACE`） |
| `409 Conflict on create` | 名称在空间中已存在。使用不同的名称或获取现有配置 ID。 |
| 队列未找到 | `ax annotation-queues list --space SPACE`；验证队列名称或 ID |
| 记录未出现在队列中 | 确保链接到队列的标注配置存在；检查 `ax annotation-configs list --space SPACE` |
| 跨度 SDK 错误或缺少跨度 | 确认 `project_name`、`space_id` 和跨度 ID；使用 arize-trace 导出跨度 |

---

## 通过 CLI 批量标注

`ax` CLI 提供批量标注命令，无需 Python SDK 即可大规模写入标注。所有命令都接受文件（CSV、JSON、JSONL 或 Parquet），每个请求最多 **1000 个标注**，并使用 **upsert 语义**（具有相同键的现有标注被更新；新标注被创建）。

| 资源 | 命令 | 技能 |
|----------|---------|-------|
| 跨度 | `ax spans annotate PROJECT --file annotations.json` | **arize-trace** |
| 数据集示例 | `ax datasets annotate-examples NAME_OR_ID --file annotations.json` | **arize-dataset** |
| 实验运行 | `ax experiments annotate-runs NAME_OR_ID --file annotations.json --dataset DATASET` | **arize-experiment** |

所有三个命令都支持 `--space SPACE`。查看链接的技能以获取完整的标志表和文件格式详细信息。

---

## 相关技能

- **arize-trace**：导出跨度以查找跨度 ID 和时间范围；通过 `ax spans annotate` 批量标注跨度
- **arize-dataset**：查找数据集 ID 和示例 ID；通过 `ax datasets annotate-examples` 批量标注示例
- **arize-evaluator**：自动 LLM 作为裁判与人工标注
- **arize-experiment**：与数据集和评估工作流绑定的实验；通过 `ax experiments annotate-runs` 批量标注运行
- **arize-prompts**：管理提示模板；标注提示输出以进行质量跟踪
- **arize-link**：深度链接到 Arize UI 中的标注配置和队列

---

## 保存凭证以供将来使用

查看 [references/ax-profiles.md](references/ax-profiles.md) § 保存凭证以供将来使用。
