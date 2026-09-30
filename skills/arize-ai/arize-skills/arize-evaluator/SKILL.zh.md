---
name: arize-evaluator
description: 处理 Arize 上的 LLM 作为裁判和代码评估工作流程，包括创建/更新评估器、在跨度或实验上运行评估、管理任务、触发运行操作、列映射和持续监控。当用户提到创建评估器、LLM 裁判、代码评估器、幻觉、忠实度、正确性、相关性、运行评估、评分跨度、评分实验、触发运行、列映射、持续监控或改进评估器提示时使用。
---

# Arize 评估器技能

> **`SPACE`** — `--space` 标志接受一个 **空间名称**（例如，`my-workspace`）或一个 base64 空间 **ID**（例如，`U3BhY2U6...`）。使用 `ax spaces list` 查找您的空间。

此技能涵盖在 Arize 上设计、创建和运行 **评估器** — 既是 **LLM 作为法官（模板）** 评估器，也是 **代码评估器**（确定性，无需 LLM）。评估器定义了法官；一个 **任务** 是您如何将其运行在真实数据上。

---

## 前置条件

直接进行任务 — 运行您需要的 `ax` 命令。**不要**事先检查版本、环境变量或配置文件。

如果 `ax` 命令失败，根据错误进行故障排除：
- `command not found` 或版本错误 → 查看 [references/ax-setup.md](references/ax-setup.md)
- `401 Unauthorized` / 缺少 API 密钥 → 运行 `ax profiles show` 检查当前配置文件。如果配置文件缺失或 API 密钥错误，请按照 [references/ax-profiles.md](references/ax-profiles.md) 创建/更新它。如果用户没有他们的密钥，请指导他们到 https://app.arize.com/admin > API 密钥
- 空间未知 → 运行 `ax spaces list` 通过名称选择，或询问用户
- LLM 提供商调用失败（缺少提供商凭证）→ 运行 `ax ai-integrations list --space SPACE` 检查平台管理的凭证。如果不存在，使用 **arize-ai-provider-integration** 技能 — **永远不要**要求用户将提供商密钥粘贴到聊天中。
- **安全**：**永远不要**读取 `.env` 文件或在文件系统中搜索凭证。使用 `ax profiles` 用于 Arize 凭证，使用 `ax ai-integrations` 用于 LLM 提供商密钥。**永远不要**要求用户将秘密粘贴到聊天中。有关缺失凭证，请参阅 [references/ax-profiles.md](references/ax-profiles.md)。
- **关键** — **永远不要**编造评估结果：如果评估任务失败、被取消或产生没有分数，请清晰地报告失败并解释出了什么问题。**不要**执行“手动评估”，不要编造质量分数，不要估计百分比，也不要将任何代理生成的分析呈现为来自 Arize 评估系统。相反，建议：(1) 修复已识别的问题并重试，(2) 尝试从 Arize UI 运行，(3) 使用 `ax ai-integrations list` 验证集成凭证，(4) 联系 https://arize.com/support 支持

---

## 概念

### 什么是评估器？

评估器是一个 LLM 作为法官的定义。它包含：

| 字段 | 描述 |
|-------|-------------|
| **模板** | 法官提示。使用 `{{variable}}`（双大括号）占位符（例如 `{{input}}`、`{{output}}`、`{{context}}`），在运行时通过任务的列映射填充。 |
| **分类选择** | 允许的输出标签集（例如 `factual` / `hallucinated`）。二进制是默认且最常见的。每个选择可以可选地携带一个数值分数。 |
| **AI 集成** | 评估器使用的存储 LLM 提供商凭证（OpenAI、Anthropic、Bedrock 等）来调用法官模型。 |
| **模型** | 特定的法官模型（例如 `gpt-4o`、`claude-sonnet-4-5`）。 |
| **调用参数** | 可选的 JSON 模型设置，如 `{"temperature": 0}`。建议使用低温度以提高可重复性。 |
| **优化方向** | 分数更高更好 (`MAXIMIZE`) 还是更差 (`MINIMIZE`)。设置 UI 渲染趋势的方式。 |
| **数据粒度** | 评估器在 **跨度**、**跟踪** 或 **会话** 级别运行。大多数评估器在跨度级别运行。 |

评估器是 **版本化的** — 每次提示或模型更改都会创建一个新的不可变版本。最新版本是活动的。

**代码评估器** 是确定性替代方案 — 无需 AI 集成或模型，只需 Python。它们作为 `CodeEvaluator` 的类子类运行，而不是裸函数，并有自己的严格导入路径和 `evaluate()` 签名合同。如果配置错误，运行会在 `0/0/0` 时静默取消。在编写之前，请参阅 [references/cli-reference.md](references/cli-reference.md) 中的“自定义 Python 代码评估器”。

### 什么是任务？

任务是如何运行一个或多个评估器对真实数据的运行方式。任务附加到 **项目**（实时跟踪/跨度）或 **数据集**（实验运行）。任务包含：

| 字段 | 描述 |
|-------|-------------|
| **评估器** | 要运行的评估器列表。您可以在一个任务中运行多个。 |
| **列映射** | 将每个评估器的模板变量映射到跨度或实验运行上实际的字段路径（例如 `"input" → "attributes.input.value"`）。这是使评估器跨项目和实验可移植的原因。 |
| **查询过滤器** | SQL 风格的表达式，用于选择要评估的跨度/运行（例如 `"span_kind = 'LLM'"`）。可选但很重要，用于提高精度。 |
| **连续** | 对于项目任务：是否自动对新到达的跨度进行评分。 |
| **采样率** | 对于连续项目任务：要评估的新跨度的分数（0–1）。 |

---

## 数据粒度

在创建评估器时（`ax evaluators create-template-evaluator` / `create-code-evaluator`）设置 `--data-granularity`，而不是在任务上 — 它控制评估器在每次运行针对 **项目任务** 时评分的数据单元（不是数据集/实验任务 — 那些直接评估实验运行）。它默认为 `span`。

| 级别 | 它评估什么 | 用于 | 结果列前缀 |
|-------|-------------------|---------|---------------------|
| `span` (默认) | 单个跨度 | Q&A 正确性、幻觉、相关性 | `eval.{name}.label` / `.score` / `.explanation` |
| `trace` | 一个跟踪中的所有跨度，按 `context.trace_id` 分组 | 代理轨迹、任务正确性 — 任何需要完整调用链的 | `trace_eval.{name}.label` / `.score` / `.explanation` |
| `session` | 一个会话中的所有跟踪，按 `attributes.session.id` 和开始时间排序 | 多轮连贯性、整体语气、对话质量 | `session_eval.{name}.label` / `.score` / `.explanation` |

### 跟踪和会话聚合如何工作

对于 **跟踪** 粒度，共享相同 `context.trace_id` 的跨度被分组在一起。评估器模板使用的列值被逗号连接成一个字符串（每个值截断到 100K 字符）然后传递给法官模型。

对于 **会话** 粒度，首先发生跟踪级分组，然后按 `start_time` 排序并按 `attributes.session.id` 分组。会话级值总共限制为 100K 字符。

### `{{conversation}}` 模板变量

在会话粒度下，`{{conversation}}` 是一个特殊的模板变量，渲染为会话中所有跟踪的 `{input, output}` 转换的 JSON 数组，由 `attributes.input.value` / `attributes.llm.input_messages`（输入侧）和 `attributes.output.value` / `attributes.llm.output_messages`（输出侧）构建。

在跨度或跟踪粒度下，`{{conversation}}` 被视为一个常规模板变量，像任何其他变量一样通过列映射解析。

> **注意**：要使 `{{conversation}}` 正常工作，跨度必须携带 `attributes.session.id`。有关如何从应用程序代码中发出 `session.id` 的信息，请参阅 **arize-instrumentation** 技能，包括 Jupyter 笔记本和短期脚本所需的 `force_flush()` 模式。

### 多评估器任务

一个任务可以包含不同粒度的评估器。在运行时，系统使用 **最高** 粒度（会话 > 跟踪 > 跨度）获取数据，并自动 **为每个评估器分割成一个子运行**。任务中的评估器 JSON 中的每个评估器 `query_filter` 进一步缩小包含的跨度（例如，仅在会话内包含工具调用跨度）。

---

## 基本的 CRUD

**AI 集成**、**评估器**（模板和代码）和 **任务** 的完整命令参考 — 每个标志，附带示例 — 在 [references/cli-reference.md](references/cli-reference.md) 中。下面的工作流包括您需要的内联命令。

---

## 工作流 A：为项目创建评估器

当用户说类似“为我的 Playground Traces 项目创建一个评估器”时，使用此方法。

### 第 1 步：确认项目名称

`ax spans export` 直接接受项目名称 — 无需 ID 查找。如果您不知道项目名称，请列出可用项目：

```bash
ax projects list --space SPACE -o json
```

找到 `"name"` 匹配的条目（不区分大小写），并将其用作后续命令中的 `PROJECT`。如果您后来遇到与名称相关的验证错误，请回退到使用项目的 `"id"`（一个 base64 字符串）。

### 第 2 步：了解要评估的内容

如果用户指定了评估器类型（幻觉、正确性、相关性等）→ 跳到第 3 步。

如果不是，请采样最近的跨度以基于实际数据创建评估器：

```bash
ax spans export PROJECT --space SPACE -l 10 --days 30 --stdout
```

检查 `attributes.input`、`attributes.output`、跨度类型和任何现有注释。识别失败模式（例如，幻觉的事实、离题的答案、缺失的上下文），并提出 **1–3 个具体的评估器想法**。让用户选择。

每个建议必须包括：评估器名称（粗体）、对其判断的简短描述，以及括号中的二进制标签对。像这样格式化每个：

1. **名称** — 被判断的内容描述。 (`label_a` / `label_b`)

示例：
1. **响应正确性** — 代理的响应是否正确地回答了用户的财务查询？ (`correct` / `incorrect`)
2. **幻觉** — 响应是否编造了不在检索到的上下文中得到支撑的事实？ (`factual` / `hallucinated`)

### 第 3 步：确认或创建 AI 集成

```bash
ax ai-integrations list --space SPACE -o json
```

如果存在合适的集成，请记下其 ID。如果没有，请使用 **arize-ai-provider-integration** 技能创建一个。询问用户他们想要用于法官的提供商/模型。

### 第 4 步：创建评估器

使用以下模板设计最佳实践。保持评估器名称和变量 **通用** — 任务（第 6 步）通过 `column_mappings` 处理项目特定连接。

```bash
ax evaluators create-template-evaluator \
  --name "幻觉" \
  --space SPACE \
  --template-name "hallucination" \
  --commit-message "初始版本" \
  --ai-integration-id INT_ID \
  --model-name "gpt-4o" \
  --include-explanations \
  --use-function-calling \
  --classification-choices '{"factual": 1, "hallucinated": 0}' \
  --template '您是一个评估器。给定用户问题和模型响应，判断响应是事实性的还是包含不支持的声明。

用户问题：{{input}}

模型响应：{{output}}

用以下标签之一精确回复：hallucinated, factual'
```

### 第 5 步：询问 — 回填、连续，还是两者？

**推荐方法**：始终先用一小部分回填（~100 个历史跨度）以验证评估器，然后再开启连续监控。这允许您在将所有未来的生产跨度评分之前，在已知数据上捕获列映射错误、错误的跨度类型和模板问题。只有在回填确认正确评分后，才启用连续。

在创建任务之前，询问：

> "您想要：
> (a) 对历史跨度运行 **回填**（一次性）？
> (b) 设置 **连续** 评估新跨度？
> (c) **两者** — 先回填以验证，然后自动评分新跨度？（推荐）"

### 第 6 步：从真实跨度数据确定列映射

不要猜测路径。拉取一个样本并检查实际存在哪些字段：

```bash
ax spans export PROJECT --space SPACE -l 5 --days 7 --stdout
```

对于每个模板变量（`{{input}}`、`{{output}}`、`{{context}}`），找到匹配的 JSON 路径。常见起点 — **在使用您实际数据之前始终验证**：

| 模板变量 | LLM 跨度 | CHAIN 跨度 |
|---|---|---|
| `input` | `attributes.input.value` | `attributes.input.value` |
| `output` | `attributes.llm.output_messages.0.message.content` | `attributes.output.value` |
| `context` | `attributes.retrieval.documents.contents` | — |
| `tool_output` | `attributes.input.value` (后备) | `attributes.output.value` |

**验证跨度类型一致性**：如果评估器提示假设 LLM 最终文本，但任务针对 CHAIN 跨度（反之亦然），运行可能会取消或评分错误文本。确保任务的 `query_filter` 匹配您映射的跨度类型。

**`query_filter` 仅适用于索引属性**：评估器 JSON 中的 `query_filter` 是针对评估索引评估的，而不是原始跨度存储。`attributes.metadata.*` 或自定义键下的属性可能未索引，并将静默匹配为空。使用像 `span_kind` 或 `attributes.llm.model_name` 这样的索引属性进行过滤。如果一个过滤器返回 0 个跨度，尽管存在数据，请尝试作为诊断步骤删除过滤器。

**完整的 `--evaluators` JSON 示例**：

```json
[
  {
    "evaluator_id": "EVAL_ID",
    "query_filter": "span_kind = 'LLM'",
    "column_mappings": {
      "input": "attributes.input.value",
      "output": "attributes.llm.output_messages.0.message.content",
      "context": "attributes.retrieval.documents.contents"
    }
  }
]
```

包含模板引用的 **每个** 变量的映射。遗漏一个会导致运行产生没有有效分数。

### 第 7 步：创建任务

**仅回填 (a)**：
```bash
ax tasks create-evaluation \
  --name "幻觉回填" \
  --task-type TEMPLATE_EVALUATION \
  --project PROJECT \
  --evaluators '[{"evaluator_id": "EVAL_ID", "column_mappings": {"input": "attributes.input.value", "output": "attributes.output.value"}}]' \
  --no-continuous
```

**仅连续 (b)**：
```bash
ax tasks create-evaluation \
  --name "幻觉监控" \
  --task-type TEMPLATE_EVALUATION \
  --project PROJECT \
  --evaluators '[{"evaluator_id": "EVAL_ID", "column_mappings": {"input": "attributes.input.value", "output": "attributes.output.value"}}]' \
  --is-continuous \
  --sampling-rate 0.1
```

**两者 (c)**：在创建时使用 `--is-continuous`，然后在第 8 步中触发回填运行。

### 第 8 步：触发回填运行（如果请求）

> **评估索引延迟**：评估索引从主要跟踪存储异步构建，可能延迟 **1–2 小时**。对于第一个测试运行，使用至少 2 小时前的结束时间窗口。如果您在跨度 ingested 在过去一小时中设置 `--data-end-time` 为“now”，运行将成功完成，但评分 0 个跨度。

首先找到具有数据的时区：
```bash
ax spans export PROJECT --space SPACE -l 100 --days 1 --stdout   # 首先尝试过去 24 小时
ax spans export PROJECT --space SPACE -l 100 --days 7 --stdout   # 如果为空，则扩大范围
```

使用真实跨度的 `start_time` / `end_time` 字段设置窗口。对于第一个验证运行，将 `--max-spans` 限制在 ~100 以快速获取反馈：

```bash
ax tasks trigger-run TASK_ID \
  --data-start-time "2026-03-20T00:00:00" \
  --data-end-time "2026-03-21T23:59:59" \
  --max-spans 100 \
  --wait
```

在扩大到完整回填或启用连续之前，查看分数和解释。

---

## 工作流 B：为实验创建评估器

当用户说类似“为我的实验创建一个评估器”或“评估我的数据集运行”时，使用此方法。

**如果用户说“数据集”但没有实验**：任务必须针对实验（而不是裸数据集）。询问：
> "评估任务直接针对实验运行，而不是数据集。您想要帮助在数据集上创建实验吗？"

如果同意，使用 **arize-experiment** 技能创建一个，然后返回这里。

### 第 1 步：找到数据集和实验名称

```bash
ax datasets list --space SPACE
ax experiments list --dataset DATASET_NAME --space SPACE -o json
```

记下数据集名称和要评分的实验名称。这些接受名称或 ID 在后续命令中使用 — 名称是首选的。

### 第 2 步：了解要评估的内容

如果用户指定了评估器类型 → 跳到第 3 步。

如果不可以，检查最近的实验运行情况，以便基于实际数据来构建评估器：

```bash
ax experiments export EXPERIMENT_NAME --dataset DATASET_NAME --space SPACE --stdout | python3 -c "import sys,json; runs=json.load(sys.stdin); print(json.dumps(runs[0], indent=2))"
```

查看 `output`、`input`、`evaluations` 和 `metadata` 字段。找出差距（用户关心的但尚未拥有的指标），并提出 **1-3 个评估器想法**。每个建议必须包括：评估器名称（加粗）、一句话描述，以及括号中的二元标签对——与工作流 A、步骤 2 相同的格式。

### 步骤 3：确认或创建 AI 集成

与工作流 A、步骤 3 相同。

### 步骤 4：创建评估器

与工作流 A、步骤 4 相同。保持变量通用。

### 步骤 5：从实际运行数据确定列映射

运行数据形状与跨度数据不同。检查：

```bash
ax experiments export EXPERIMENT_NAME --dataset DATASET_NAME --space SPACE --stdout | python3 -c "import sys,json; runs=json.load(sys.stdin); print(json.dumps(runs[0], indent=2))"
```

实验运行数据的常见映射：
- `output` → `"output"`（每个运行的一级字段）
- `input` → 检查它是否在运行中，或嵌入在链接的数据集示例中

如果 `input` 不在运行 JSON 中，导出数据集示例以找到路径：
```bash
ax datasets export DATASET_NAME --space SPACE --stdout | python3 -c "import sys,json; ex=json.load(sys.stdin); print(json.dumps(ex[0], indent=2))"
```

### 步骤 6：创建任务

`--experiment-ids` 使用 `ax experiments list --space SPACE -o json` 的 base64 ID。

```bash
ax tasks create-evaluation \
  --name "实验正确性" \
  --task-type TEMPLATE_EVALUATION \
  --dataset DATASET_NAME --space SPACE \
  --experiment-ids "EXP_ID" \
  --evaluators '[{"evaluator_id": "EVAL_ID", "column_mappings": {"output": "output"}}]' \
  --no-continuous
```

### 步骤 7：触发和监控

```bash
ax tasks trigger-run TASK_ID \
  --experiment-ids "EXP_ID" \
  --wait

ax tasks list-runs TASK_ID
ax tasks get-run RUN_ID
```

---

## 模板设计的最佳实践

### 1. 使用通用、可移植的变量名

使用 `{{input}}`、`{{output}}` 和 `{{context}}`——而不是与特定项目或跨度属性相关的名称（例如，不要使用 `{{attributes_input_value}}`）。评估器本身保持抽象；**任务的 `column_mappings`** 是将评估器连接到特定项目或实验中实际字段的场所。这使得相同的评估器可以在多个项目和实验中运行而无需修改。

### 2. 默认使用二元标签

使用两个清晰字符串标签（例如 `hallucinated` / `factual`、`correct` / `incorrect`、`pass` / `fail`）。二元标签：
- 对判别模型来说最容易一致地生成
- 在行业内最常见
- 在仪表板中最简单易懂

如果用户坚持使用超过两个选项，那也可以——但建议首先使用二元标签，并解释权衡（更多标签→更多歧义→较低的人对评分者可靠性）。

### 3. 明确说明模型必须返回的内容

模板必须告诉判别模型返回**仅**标签字符串——其他任何内容都不行。提示中的标签字符串必须**完全匹配** `--classification-choices` 中的标签（拼写相同，大小写相同）。

良好：
```
仅返回以下标签之一：hallucinated, factual
```

不良（过于开放）：
```
这是幻觉吗？回答是或否。
```

### 4. 保持温度低

传递 `--invocation-params '{"temperature": 0}'` 以获得可重复的评分。更高的温度会在评估结果中引入噪声。

### 5. 使用 `--include-explanations` 进行调试

在初始设置期间，始终包含解释，以便在在规模化信任标签之前验证判别模型是否正确推理。

### 6. 在 bash 中使用单引号传递模板

单引号防止 shell 插值 `{{variable}}` 占位符。双引号会导致问题：

```bash
# 正确
--template 'Judge this: {{input}} → {{output}}'

# 错误——shell 可能会解释 { } 或失败
--template "Judge this: {{input}} → {{output}}"
```

### 7. 始终设置 `--classification-choices` 以匹配您的模板标签

`--classification-choices` 中的标签必须与 `--template` 中引用的标签完全匹配（拼写相同，大小写相同）。省略 `--classification-choices` 会导致任务运行失败，提示“缺少轨道和分类选择。”

---

## 故障排除

| 问题 | 解决方案 |
|------|----------|
| `ax: command not found` | 查看 [references/ax-setup.md](references/ax-setup.md) |
| `401 Unauthorized` | API 密钥可能没有访问此空间的权限。在 https://app.arize.com/admin > API Keys 中验证。 |
| `Evaluator not found` | `ax evaluators list --space SPACE` |
| `Integration not found` | `ax ai-integrations list --space SPACE` |
| `Task not found` | `ax tasks list --space SPACE` |
| `project and dataset-id are mutually exclusive` | 创建任务时仅使用其中一个 |
| `experiment-ids required for dataset tasks` | 在 `create` 和 `trigger-run` 中添加 `--experiment-ids` |
| `sampling-rate only valid for project tasks` | 从数据集任务中移除 `--sampling-rate` |
| Validation error on `ax spans export` | 项目名称通常有效；如果您仍然收到验证错误，请通过 `ax projects list --space SPACE -o json` 查找 base64 项目 ID，并使用 `id` 字段 |
| Template validation errors | 在 bash 中使用单引号 `--template '...'`；双大括号 `{{var}}`，而不是单大括号 `{var}` |
| Run stuck in `pending` | `ax tasks get-run RUN_ID`；然后 `ax tasks cancel-run RUN_ID` |
| Run `cancelled` ~1s | 集成凭证无效——检查 AI 集成 |
| Run `cancelled` ~3min | 找到跨度但 LLM 调用失败——模型名称错误或密钥无效 |
| Run `completed`, 0 spans | 扩大时间窗口；评估索引可能不覆盖旧数据 |
| No scores in UI | 修复 `column_mappings` 以匹配您的跨度/运行中的实际路径 |
| Scores look wrong | 添加 `--include-explanations` 并检查判别模型在几个样本上的推理 |
| Evaluator cancels on wrong span kind | 匹配 `query_filter` 和 `column_mappings` 到 LLM vs CHAIN 跨度 |
| Time format error on `trigger-run` | 使用 `2026-03-21T09:00:00`——没有尾随 `Z` |
| Run failed: "missing rails and classification choices" | 在 `ax evaluators create-template-evaluator` 中添加 `--classification-choices '{"label_a": 1, "label_b": 0}'`——标签必须与模板匹配 |
| Run `completed`, all spans skipped | 查询过滤器匹配了跨度，但列映射错误或模板变量无法解析——导出样本跨度并验证路径 |
| `query_filter` set but 0 spans scored | 过滤属性可能未在评估索引中索引。`attributes.metadata.*` 和自定义属性通常不会被索引。使用 `span_kind` 或 `attributes.llm.model_name` 替代，或移除过滤器以确认窗口中存在跨度。 |
| Custom **code** evaluator run cancels ~3s with `0/0/0` (successes/errors/skipped) | 错误的导入路径或 `evaluate()` 签名——参见 [references/cli-reference.md](references/cli-reference.md) 下 **Custom Python code evaluators** 的“CRITICAL”提示。必须从 `arize.experimental.datasets.experiments.evaluators.base` 导入（而不是 `arize.experiments`），并声明命名的 `evaluate()` 参数，而不是仅 `**kwargs`。 |

### 诊断已取消的运行

当任务运行报告状态 `cancelled` 时，按顺序检查清单（凭证→模型名称→列映射/路径检查→时间窗口→跨度类型→变量解析）在 [references/troubleshooting.md](references/troubleshooting.md) 中。

---

## 相关技能

- **arize-ai-provider-integration**：完整的 LLM 提供商集成 CRUD（创建、更新、删除凭证）
- **arize-trace**：导出跨度以发现列路径和时间范围
- **arize-experiment**：创建实验并导出运行以用于实验列映射
- **arize-dataset**：导出数据集示例以找到输入字段，当运行中省略时
- **arize-prompts**：在 Prompt Hub 管理提示模板；与评估器一起使用以对版本化的提示进行评分
- **arize-link**：深度链接到 Arize UI 中的评估器和任务

---

## 保存凭证以供将来使用

查看 [references/ax-profiles.md](references/ax-profiles.md) § 保存凭证以供将来使用。
