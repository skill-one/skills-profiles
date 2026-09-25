# Arize 实验技能

> **`SPACE`** — `--space` 标志接受一个 **空间名称**（例如，`my-workspace`）或 base64 空间 **ID**（例如，`U3BhY2U6...`）。使用 `ax spaces list` 查找您的空间。

## 概念

- **实验** = 针对特定数据集版本的命名评估运行，包含每个示例的一个运行
- **实验运行** = 处理一个数据集示例的结果 -- 包括模型输出、可选评估和可选元数据
- **数据集** = 版本化的示例集合；每个实验都与一个数据集和特定数据集版本相关联
- **评估** = 附属于运行的一个命名指标（例如，`正确性`、`相关性`），带有可选标签、分数和解释

典型流程：导出数据集 → 处理每个示例 → 收集输出和评估 → 创建包含运行的实验。

## 前置条件

直接进行任务 — 运行您需要的 `ax` 命令。**不要**提前检查版本、环境变量或配置文件。

如果 `ax` 命令失败，根据错误进行故障排除：
- `command not found` 或版本错误 → 查看 [references/ax-setup.md](references/ax-setup.md)
- `401 Unauthorized` / 缺少 API 密钥 → 运行 `ax profiles show` 检查当前配置文件。如果配置文件缺失或 API 密钥错误，请按照 [references/ax-profiles.md](references/ax-profiles.md) 创建/更新配置文件。如果用户没有他们的密钥，请指示他们访问 https://app.arize.com/admin > API 密钥
- 空间未知 → 运行 `ax spaces list` 通过名称选择，或询问用户
- 项目不明确 → 询问用户，或运行 `ax projects list -o json --limit 100` 并作为可选选项呈现
- **安全**：**永远不要**读取 `.env` 文件或在文件系统中搜索凭证。使用 `ax profiles` 存储Arize凭证，使用 `ax ai-integrations` 存储LLM 提供商密钥。**永远不要**要求用户将秘密粘贴到聊天中。对于缺失的凭证，请参阅 [references/ax-profiles.md](references/ax-profiles.md)。
- **关键** — **永远不要**编造输出：运行实验时，您**必须**为每个数据集示例调用用户指定的真实模型 API。**永远不要**编造、模拟或硬编码模型输出、延迟或评估分数。如果您无法调用 API（缺少 SDK、缺少凭证、网络错误），请停止并告诉用户在继续之前需要什么。

## 列出实验：`ax experiments list`

浏览实验，可选地按数据集进行过滤。输出到标准输出。

```bash
ax experiments list
ax experiments list --dataset DATASET_NAME --space SPACE --limit 20   # DATASET_NAME: 名称或 ID（名称优先）
ax experiments list --cursor CURSOR_TOKEN
ax experiments list -o json
```

标志：参见 [references/experiments-cli.md#list](references/experiments-cli.md#list)。

## 获取实验：`ax experiments get`

快速元数据查找 — 返回实验名称、链接的数据集/版本和时间戳。

```bash
ax experiments get NAME_OR_ID
ax experiments get NAME_OR_ID -o json
ax experiments get NAME_OR_ID --dataset DATASET_NAME --space SPACE   # 使用实验名称而不是 ID 时需要
```

标志：参见 [references/experiments-cli.md#get](references/experiments-cli.md#get)。

### 响应字段

| 字段 | 类型 | 描述 |
|-------|------|-------------|
| `id` | string | 实验ID |
| `name` | string | 实验名称 |
| `dataset_id` | string | 链接的数据集ID |
| `dataset_version_id` | string | 使用的特定数据集版本 |
| `experiment_traces_project_id` | string | 存储实验跟踪的项目 |
| `created_at` | datetime | 实验创建时间 |
| `updated_at` | datetime | 最后修改时间 |

## 导出实验：`ax experiments export`

将所有运行下载到文件。默认情况下使用 REST API；传递 `--all` 使用 Arrow Flight 进行批量传输。

```bash
# EXPERIMENT_NAME, DATASET_NAME: 名称或 ID（名称优先）
ax experiments export EXPERIMENT_NAME --dataset DATASET_NAME --space SPACE
# -> experiment_abc123_20260305_141500/runs.json

ax experiments export EXPERIMENT_NAME --dataset DATASET_NAME --space SPACE --all
ax experiments export EXPERIMENT_NAME --dataset DATASET_NAME --space SPACE --output-dir ./results
ax experiments export EXPERIMENT_NAME --dataset DATASET_NAME --space SPACE --stdout
ax experiments export EXPERIMENT_NAME --dataset DATASET_NAME --space SPACE --stdout | jq '.[0]'
```

标志：参见 [references/experiments-cli.md#export](references/experiments-cli.md#export)。

### REST 与 Flight (`--all`)

- **REST**（默认）：较低摩擦 — 无需 Arrow/Flight 依赖，标准 HTTPS 端口，可通过任何企业代理或防火墙使用。每页限制 500 个运行。
- **Flight** (`--all`): 对于运行超过 500 个的实验是必需的。使用 gRPC+TLS 在单独的主机/端口上运行，某些企业网络可能会阻止。活动的 `ax` 配置文件提供区域端点；参见 [配置文件设置](references/ax-profiles.md)。

**代理自动扩展规则**：如果 REST 导出返回正好 500 个运行，结果可能被截断。使用 `--all` 重新运行以获取完整数据集。

输出是一个运行对象的 JSON 数组：

```json
[
  {
    "id": "run_001",
    "example_id": "ex_001",
    "output": "The answer is 4.",
    "evaluations": {
      "correctness": { "label": "correct", "score": 1.0 },
      "relevance": { "score": 0.95, "explanation": "Directly answers the question" }
    },
    "metadata": { "model": "gpt-4o", "latency_ms": 1234 }
  }
]
```

## 创建实验：`ax experiments create`

使用来自数据文件的运行创建新实验。

```bash
ax experiments create --name "gpt-4o-baseline" --dataset DATASET_NAME --space SPACE --file runs.json
ax experiments create --name "claude-test" --dataset DATASET_NAME --space SPACE --file runs.csv
```

标志：参见 [references/experiments-cli.md#create](references/experiments-cli.md#create)。`--dataset` 是可选的 — 跳过它以创建没有链接数据集的独立实验（然后 `--space` 是必需的）。

### 通过 stdin 传递数据

使用 `--file -` 直接管道数据 — 无需临时文件：

```bash
echo '[{"example_id": "ex_001", "output": "Paris"}]' | ax experiments create --name "my-experiment" --dataset DATASET_NAME --space SPACE --file -

# 或使用 heredoc
ax experiments create --name "my-experiment" --dataset DATASET_NAME --space SPACE --file - << 'EOF'
[{"example_id": "ex_001", "output": "Paris"}]
EOF
```

### 运行文件中必需的列

| 列 | 类型 | 必需 | 描述 |
|-------|------|----------|-------------|
| `example_id` | string | 是 | 数据集示例的 **顶层 `id`** 从 `ax datasets export` |
| `output` | string | 是 | 此示例的模型/系统输出 |

附加列作为 `additionalProperties` 传递给运行。

> **`example_id` 必须是 Arize 行 ID** — 每个导出的数据集示例上的顶层 `id` 字段 (`ex["id"]`)。**不要**使用嵌套在示例输入字段或 `additional_properties` 中的值；错误的值会导致静默失败或运行附加到错误的示例。导出数据集并检查顶层 `id` 字段后再创建运行。

> **⚠️ 创建文件中的内联评估不会作为分数附加。** `create` 仅读取 `example_id` 和 `output`；其他每个列 — 包括 `evaluations` 对象 — 都作为传递的附加字段存储，**不是**作为实验评估，并且**不会**在 UI 中作为分数显示。这会静默失败（无错误）。要附加分数/标签，请先创建实验，然后运行 `ax experiments annotate-runs`。下面架构中的 `evaluations` 对象是 **导出（读取）** 形状，在存在注释后返回 — 它不是 `create` 的输入。

## 本地运行任务：`ax experiments run`

与 `create` 不同（需要预先计算的输出文件），`run` 加载 Python 任务函数，针对每个数据集行执行它，并将结果作为实验上传。

```bash
ax experiments run -n "my-experiment" --dataset DATASET_NAME --space SPACE --task task.py
ax experiments run -n "my-experiment" --dataset DATASET_NAME --space SPACE --task task.py --concurrency 5 --dry-run
```

`task.py` 必须定义一个返回 JSON 可序列化值的顶层 `task(dataset_row)` 函数：

```python
from anthropic import Anthropic

def task(dataset_row):
    resp = Anthropic().messages.create(
        model="claude-3-5-sonnet-20241022", max_tokens=256,
        messages=[{"role": "user", "content": dataset_row["question"]}]
    )
    return resp.content[0].text
```

`--dry-run` 在前 10 个示例上测试而不上传，以在完整运行之前验证任务。标志：参见 [references/experiments-cli.md#run](references/experiments-cli.md#run)。

> **根据逻辑位置选择运行路径。** 当有一个本地 Python 任务要执行时，使用 `ax experiments run` — 它在本地机器上运行 `task.py` 并上传结果；不需要 AI 集成。当运行应托管且可重复时，使用 `ax tasks create-run-experiment` — 它注册一个平台侧的 `run_experiment` 任务，Arize 按计划或在请求时执行，由 JSON `--run-configuration`（模型 + 消息 + AI 集成）驱动，而不是本地代码。对于本地/临时运行和自定义逻辑，默认使用 `ax experiments run`；对于可重复的托管运行，使用 **arize-evaluator** 技能。

## 列出运行：`ax experiments list-runs`

实验运行的分页终端视图（与 `export` 不同，`export` 将它们下载到文件）。

```bash
ax experiments list-runs EXPERIMENT_NAME --dataset DATASET_NAME --space SPACE --limit 30
ax experiments list-runs EXPERIMENT_ID
```

标志：参见 [references/experiments-cli.md#list-runs](references/experiments-cli.md#list-runs)。

## 删除实验：`ax experiments delete`

```bash
ax experiments delete NAME_OR_ID
ax experiments delete NAME_OR_ID --dataset DATASET_NAME --space SPACE   # 使用实验名称而不是 ID 时需要
ax experiments delete NAME_OR_ID --force   # 跳过确认提示
```

标志：参见 [references/experiments-cli.md#delete](references/experiments-cli.md#delete)。

## 注释运行：`ax experiments annotate-runs`

**这是将评估分数/标签附加到实验并使其在 UI 中显示的必需步骤。** 评估不能通过 `create` 附加；参见创建实验下的警告。您在这里编写它们，在实验存在之后。Upsert 语义 — 重新提交相同注释 `name` 的相同运行会覆盖以前的值。每个请求最多 1000 个运行；不匹配的记录 ID 会静默忽略。

```bash
ax experiments annotate-runs NAME_OR_ID --file annotations.json --dataset DATASET_NAME --space SPACE
ax experiments annotate-runs NAME_OR_ID --file annotations.csv --dataset DATASET_NAME --space SPACE
```

### 注释文件架构

一个 JSON 数组；每个项目注释一个运行：

```json
[
  {
    "record_id": "run_001",
    "values": [
      { "name": "correctness", "label": "correct", "score": 1.0 },
      { "name": "relevance", "score": 0.95, "text": "Directly answers the question" }
    ]
  }
]
```

| 字段 | 类型 | 必需 | 描述 |
|-------|------|----------|-------------|
| `record_id` | string | 是 | 实验运行 ID（`ax experiments export` 中的运行 `id`） — **不是** `example_id` |
| `values` | array | 是 | 一个或多个注释字典，每个字典都有一个 `name` 以及至少一个 `score`、`label` 或 `text` |
| `values[].name` | string | 是 | 注释/评估名称（例如，`correctness`） — 在 UI 中成为分数列 |
| `values[].score` | number | 否 | 数值分数（例如，`0.0`–`1.0`） |
| `values[].label` | string | 否 | 分类标签（例如，`correct`、`incorrect`） |
| `values[].text` | string | 否 | 自由形式的解释 |

> `record_id` 是在 **运行** ID，这只有在 `create` 之后才存在。因此顺序始终是：`create` → `export`（读取每个运行的 `id`）→ 构建注释 → `annotate-runs`。

标志：参见 [references/experiments-cli.md#annotate-runs](references/experiments-cli.md#annotate-runs)。

## 实验运行架构

每个运行对应一个数据集示例。**在 `create` 时，仅消费 `example_id` 和 `output`** — 这里显示的 `evaluations` 是 `annotate-runs` 附加分数后 `export` 返回的形状；它不是 `create` 的输入。

```json
{
  "example_id": "在 create 时必需 — 数据集示例的顶层 `id`",
  "output": "在 create 时必需 — 此示例的模型/系统输出",
  "evaluations": {
    "metric_name": {
      "label": "可选字符串标签（例如，'correct'、'incorrect'）",
      "score": "可选数值分数（例如，0.95）",
      "explanation": "可选自由形式文本"
    }
  },
  "metadata": {
    "model": "gpt-4o",
    "temperature": 0.7,
    "latency_ms": 1234
  }
}
```

### 评估字段

| 字段 | 类型 | 必需 | 描述 |
|-------|------|----------|-------------|
| `label` | string | 否 | 分类分类（例如，`correct`、`incorrect`、`partial`） |
| `score` | number | 否 | 数值质量分数（例如，0.0 - 1.0） |
| `explanation` | string | 否 | 评估的理由 |

每个评估至少应包含 `label`、`score` 或 `explanation` 中的一个。

## 工作流

### 对数据集运行实验

1. 查找或创建数据集：
   ```bash
   ax datasets list --space SPACE
   ax datasets export DATASET_NAME --space SPACE --stdout | jq 'length'
   ```
2. 导出数据集示例：
   ```bash
   ax datasets export DATASET_NAME --space SPACE
   ```
3. 为每个示例调用真实模型 API 并收集输出。使用 `ax datasets export --stdout` 将示例直接管道到推理脚本：

   ```bash
   ax datasets export DATASET_NAME --space SPACE --stdout | python3 infer.py > runs.json
   ```

   编写 `infer.py` 从 stdin 读取示例，调用目标模型，并将运行 JSON 写到 stdout。从 `references/inference-template.py` 的模板开始 — 复制它，检查导出的数据集 JSON 以确认输入字段名称，然后取消注释用户想要的提供者块。

   **在运行之前**：安装 SDK，设置 API 密钥环境变量。如果 API 无法访问，停止并告诉用户。

4. 验证运行文件：
   ```bash
   python3 -c "import json; runs=json.load(open('runs.json')); print(f'{len(runs)} runs'); print(json.dumps(runs[0], indent=2))"
   ```
   每个运行必须具有 `example_id`（数据集行的顶层 `id`）和 `output`。`metadata` 是可选的。**不要**在这里放 `evaluations` — `create` 忽略它们；分数在下面的步骤 7–9 中附加。
5. 创建实验：
   ```bash
   ax experiments create --name "gpt-4o-baseline" --dataset DATASET_NAME --space SPACE --file runs.json
   ```
6. 验证：`ax experiments get "gpt-4o-baseline" --dataset DATASET_NAME --space SPACE`

   **附加评估分数（要求分数在 UI 中显示）。** 创建文件中的评估被静默忽略。使用 `ax experiments annotate-runs`（键入运行 `id`）在创建实验后附加它们 — 参见工作流步骤 7–9。

7. 导出实验到结构化数据，以便您可以与 `example_id` 一起读取每个运行的 `id`。确认导出的运行记录包含这两个字段。
8. 使用结构化 JSON 处理构建注释文件，键入 `record_id`（运行 `id`）。通过 LLM 作为法官、代码检查或人工审查对每个运行进行评分/标签；**永远不要**编造分数。发出此形状：
   ```json
   [
     {
       "record_id": "FROM_EXPERIMENT_EXPORT RUN_ID",
       "values": [
         { "name": "correctness", "score": 1.0, "label": "correct" }
       ]
     }
   ]
   ```
9. 使用 `ax experiments annotate-runs ... --file annotations.json` 附加分数，然后导出或检查实验以确认评估已附加。
   现在分数在 Arize UI 的实验视图中显示。

### 比较两个实验

1. 导出两个实验：
   ```bash
   ax experiments export "experiment-a" --dataset DATASET_NAME --space SPACE --stdout > a.json
   ax experiments export "experiment-b" --dataset DATASET_NAME --space SPACE --stdout > b.json
   ```
2. 平均正确性分数（交换 `a.json` 检查另一个实验）：
   ```bash
   jq '[.[] | .evaluations.correctness.score] | add / length' a.json
   ```
3. 找到结果不同的示例：
   ```bash
   jq -s '.[0] as $a | .[1][] | . as $run | {example_id: $run.example_id, b_score: $run.evaluations.correctness.score, a_score: ($a[] | select(.example_id == $run.example_id) | .evaluations.correctness.score)}' a.json b.json
   ```
4. 每个评估者的分数分布（通过文件/失败/部分计数；交换文件检查另一个实验）：
   ```bash
   jq '[.[] | .evaluations.correctness.label] | group_by(.) | map({label: .[0], count: length})' a.json
   ```
5. 找到回归（在 A 中通过但在 B 中失败的示例）：
   ```bash
   jq -s '[.[0][] | select(.evaluations.correctness.label == "correct")] as $passed_a | [.[1][] | select(.evaluations.correctness.label != "correct") | select(.example_id as $id | $passed_a | any(.example_id == $id))]' a.json b.json
   ```

**统计显著性注意**：有 ≥ 30 个示例每个评估者时可靠；较少时，将差异视为仅方向性 — n=10 上的 5% 差异可能是噪声。与分数一起报告样本量：`jq 'length' a.json`。

### 下载实验结果进行分析

1. `ax experiments list --dataset DATASET_NAME --space SPACE` -- 查找实验
2. `ax experiments export EXPERIMENT_NAME --dataset DATASET_NAME --space SPACE` -- 下载到文件
3. 解析：`jq '.[] | {example_id, score: .evaluations.correctness.score}' experiment_*/runs.json`

### 将导出管道到其他工具

```bash
# 计数运行
ax experiments export EXPERIMENT_NAME --dataset DATASET_NAME --space SPACE --stdout | jq 'length'

# 提取所有输出
ax experiments export EXPERIMENT_NAME --dataset DATASET_NAME --space SPACE --stdout | jq '.[].output'

# 获取低分数的运行
ax experiments export EXPERIMENT_NAME --dataset DATASET_NAME --space SPACE --stdout | jq '[.[] | select(.evaluations.correctness.score < 0.5)]'

# 转换为 CSV
ax experiments export EXPERIMENT_NAME --dataset DATASET_NAME --space SPACE --stdout | jq -r '.[] | [.example_id, .output, .evaluations.correctness.score] | @csv'
```

## 相关技能

- **arize-dataset**：创建或导出实验运行的数据集 → 首先使用 `arize-dataset`
- **arize-prompts**：在 Prompt Hub (`ax prompts`) 中存储和版本化提示模板之前或之后
- **arize-prompt-optimization**：使用实验结果改进提示 → 下一步是 `arize-prompt-optimization`
- **arize-trace**：检查失败实验运行的单个跨度跟踪 → 使用 `arize-trace`
- **arize-link**：从实验运行生成可点击的 UI 链接到跟踪 → 使用 `arize-link`

## 故障排除

| 问题 | 解决方案 |
|---------|----------|
| `ax: command not found` | 查看 [references/ax-setup.md](references/ax-setup.md) |
| `401 Unauthorized` | API 密钥错误、过期或没有访问此空间的权限。使用 [references/ax-profiles.md](references/ax-profiles.md) 修复配置文件。 |
| `No profile found` | 未配置任何配置文件。查看 [references/ax-profiles.md](references/ax-profiles.md) 创建一个。 |
| `Experiment not found` | 验证实验名称与 `ax experiments list --space SPACE` |
| `Invalid runs file` | 每个运行必须具有 `example_id` 和 `output` 字段 |
| `example_id mismatch` | `example_id` 必须是数据集行的 **顶层 `id`** 从 `ax datasets export` — 不是嵌套在示例字段或 `additional_properties` 中的值。导出数据集并检查顶层 `id` 字段。 |
| 运行创建但 UI 中没有分数 / 评估 | 创建文件中的评估被静默忽略。使用 `ax experiments annotate-runs`（键入运行 `id`）在创建实验后附加它们 — 参见工作流步骤 7–9。 |
| `annotate-runs` 报告成功但未更改 | `record_id` 必须是 **运行 `id`**（从 `ax experiments export`），不是 `example_id`。不匹配的记录 ID 会静默忽略。 |
| `No runs found` | 导出返回为空 — 通过 `ax experiments get` 验证实验有运行 |
| `Dataset not found` | 链接的数据集可能已被删除；使用 `ax datasets list` 检查 |

## 保存凭证以供将来使用

参见 [references/ax-profiles.md](references/ax-profiles.md) § 保存凭证以供将来使用。
