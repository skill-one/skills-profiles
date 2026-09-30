---
name: arize-prompt-optimization
description: 使用生产跟踪数据、评估和注释来优化、改进和调试大型语言模型（LLM）提示。从片段中提取提示，收集性能信号，并使用ax CLI运行数据驱动的优化循环。当用户提到优化提示、改进提示、使AI响应更好、提高输出质量、提示工程、提示调整或系统提示改进时使用。
---

# Arize 提示优化技能

> **`SPACE`** — `--space` 标志接受一个 **空间名称**（例如，`my-workspace`）或 base64 编码的 **空间 ID**（例如，`U3BhY2U6...`）。使用 `ax spaces list` 查找您的空间。

## 相关技能

- **arize-prompts**：使用 `ax prompts`（JSON 消息、提供者、标签，例如 `production`）在 **提示中心** 中创建、版本控制和标记提示。当工件应存在于 Arize 中时，请使用该技能；使用下面的 **arize-prompt-optimization** 来从跟踪、数据集和实验中改进提示文本。

## 概念

### 提示在跟踪数据中的存储位置

LLM 应用程序遵循 OpenInference 语义规范发出跟踪。提示根据跟踪的 span 类型和instrumentation 存储在不同的 span 属性中：

| 列名 | 包含内容 | 使用场景 |
|------|----------|----------|
| `attributes.llm.input_messages` | 结构化聊天消息（系统、用户、助手、工具）在基于角色的格式中 | **主要来源**用于基于聊天的 LLM 提示 |
| `attributes.llm.input_messages.roles` | 角色数组：`system`、`user`、`assistant`、`tool` | 提取单个消息角色 |
| `attributes.llm.input_messages.contents` | 消息内容字符串数组 | 提取消息文本 |
| `attributes.input.value` | 序列化的提示或用户问题（通用，所有 span 类型） | 当结构化消息不可用时作为备用 |
| `attributes.llm.prompt_template.template` | 带有 `{variable}` 占位符的模板（例如，`"Answer {question} using {context}"`） | 当应用程序使用提示模板时 |
| `attributes.llm.prompt_template.variables` | 模板变量值（JSON 对象） | 查看模板中使用了什么值 |
| `attributes.output.value` | 模型响应文本 | 查看LLM生成了什么 |
| `attributes.llm.output_messages` | 结构化的模型输出（包括工具调用） | 检查工具调用响应 |

### 通过 span 类型查找提示

- **LLM span** (`attributes.openinference.span.kind = 'LLM'`)：检查 `attributes.llm.input_messages` 以查找结构化聊天消息，或检查 `attributes.input.value` 以查找序列化的提示。检查 `attributes.llm.prompt_template.template` 以查找模板。
- **Chain/Agent span**：`attributes.input.value` 包含用户的问题。实际的 LLM 提示存在于 **子 LLM spans** 上——沿着跟踪树向下导航。
- **Tool span**：`attributes.input.value` 包含工具输入，`attributes.output.value` 包含工具结果。通常不是提示存储的地方。

### 性能信号列

这些列携带用于优化的反馈数据：

| 列模式 | 来源 | 告诉你什么 |
|--------|------|------------|
| `annotation.<name>.label` | 人类审阅者 | 分类等级（例如，`correct`、`incorrect`、`partial`） |
| `annotation.<name>.score` | 人类审阅者 | 数值质量分数（例如，0.0 - 1.0） |
| `annotation.<name>.text` | 人类审阅者 | 对等级的自由形式解释 |
| `eval.<name>.label` | LLM 作为裁判的评估 | 自动化分类评估 |
| `eval.<name>.score` | LLM 作为裁判的评估 | 自动化数值分数 |
| `eval.<name>.explanation` | LLM 作为裁判的评估 | 评估给出该分数的原因——**对优化最有价值** |
| `attributes.input.value` | 跟踪数据 | 输入到 LLM 的内容 |
| `attributes.output.value` | 跟踪数据 | LLM 生成的输出 |
| `{experiment_name}.output` | 实验运行 | 特定实验的输出 |

## 前置条件

直接执行任务——运行您需要的 `ax` 命令。**不要**提前检查版本、环境变量或配置文件。

如果 `ax` 命令失败，请根据错误进行故障排除：
- `command not found` 或版本错误 → 查看 [references/ax-setup.md](references/ax-setup.md)
- `401 Unauthorized` / 缺少 API 密钥 → 运行 `ax profiles show` 以检查当前配置文件。如果配置文件丢失或 API 密钥不正确，请遵循 [references/ax-profiles.md](references/ax-profiles.md) 创建/更新它。如果用户没有他们的密钥，请指导他们到 https://app.arize.com/admin > API 密钥
- 空间未知 → 运行 `ax spaces list` 以按名称选择，或询问用户
- 项目不明确 → 询问用户，或运行 `ax projects list -o json --limit 100` 并作为可选选项呈现
- LLM 提供者调用失败（缺少提供者凭证）→ 运行 `ax ai-integrations list --space SPACE` 以检查平台管理的凭证。如果不存在，请使用 **arize-ai-provider-integration** 技能——**永远不要**要求用户将提供者密钥粘贴到聊天中。
- **安全**：**永远不要**读取 `.env` 文件或在文件系统中搜索凭证。使用 `ax profiles` 存储Arize凭证，使用 `ax ai-integrations` 存储LLM提供者密钥。**永远不要**要求用户将秘密粘贴到聊天中。对于缺失的凭证，请参阅 [references/ax-profiles.md](references/ax-profiles.md)。

### 必须先询问用户的情况

仍然更喜欢 `ax spaces list`、`ax projects list`、`ax datasets list`、`ax experiments list` 和导出，而不是开放式问题。如果您仍然无法进行（例如，多个项目与用户给定的名称匹配、不明确的跟踪与实验路径，或破坏性范围），**不要**直接跳转到问题——使用 **arize-instrumentation** 停止时用于范围或确认的明确框架：

1. 承认技能，例如：**我在这个存储库中找到了 arize-prompt-optimization 技能**（如果有助于添加 `skills/arize-prompt-optimization/SKILL.md`）。
2. 然后一个清晰的暂停行，例如：**在调用它之前，有几个澄清问题：**
3. 询问 **最少** 的编号或简短的项目符号问题——只有那些会阻塞此技能中的下一个 `ax` 步骤的问题。

## 第一阶段：提取当前提示

### 查找包含提示的 LLM spans

```bash
# 示例 LLM spans（提示存储的地方）
ax spans export PROJECT --filter "attributes.openinference.span.kind = 'LLM'" -l 10 --stdout

# 按模型过滤
ax spans export PROJECT --filter "attributes.llm.model_name = 'gpt-4o'" -l 10 --stdout

# 按span名称过滤（例如，特定的 LLM 调用）
ax spans export PROJECT --filter "name = 'ChatCompletion'" -l 10 --stdout
```

### 导出跟踪以检查提示结构

```bash
# 导出跟踪中的所有 spans
ax spans export PROJECT --trace-id TRACE_ID

# 导出单个 span
ax spans export PROJECT --span-id SPAN_ID
```

### 从导出的 JSON 中提取提示

```bash
# 提取结构化聊天消息（系统 + 用户 + 助手）
jq '.[0] | {
  messages: .attributes.llm.input_messages,
  model: .attributes.llm.model_name
}' trace_*/spans.json

# 特定地提取系统提示
jq '[.[] | select(.attributes.llm.input_messages.roles[]? == "system")] | .[0].attributes.llm.input_messages' trace_*/spans.json

# 提取提示模板和变量
jq '.[0].attributes.llm.prompt_template' trace_*/spans.json

# 从 input.value（非结构化提示的备用方案）
jq '.[0].attributes.input.value' trace_*/spans.json
```

### 将提示重构为消息

一旦您有了 span 数据，将提示重构为消息数组：

```json
[
  {"role": "SYSTEM", "content": "You are a helpful assistant that..."},
  {"role": "USER", "content": "Given {input}, answer the question: {question}"}
]
```

如果 span 有 `attributes.llm.prompt_template.template`，则提示使用变量。保留这些占位符（`{variable}` 或 `{{variable}}`）——它们在运行时会被替换。

## 第二阶段：收集性能数据

### 从跟踪（生产反馈）

```bash
# 查找错误 spans——这些指示提示失败
ax spans export PROJECT \
  --filter "status_code = 'ERROR' AND attributes.openinference.span.kind = 'LLM'" \
  -l 20 --stdout

# 查找评分低的 spans
ax spans export PROJECT \
  --filter "annotation.correctness.label = 'incorrect'" \
  -l 20 --stdout

# 查找高延迟的 spans（可能指示过于复杂的提示）
ax spans export PROJECT \
  --filter "attributes.openinference.span.kind = 'LLM' AND latency_ms > 10000" \
  -l 20 --stdout

# 导出错误跟踪以进行详细检查
ax spans export PROJECT --trace-id TRACE_ID
```

### 从数据集和实验

```bash
# 导出数据集（真实示例）
ax datasets export DATASET_NAME --space SPACE
# -> dataset_*/examples.json

# 导出实验结果（LLM 生成的输出）
ax experiments export EXPERIMENT_NAME --dataset DATASET_NAME --space SPACE
# -> experiment_*/runs.json
```

### 合并数据集 + 实验进行分析

通过 `example_id` 连接这两个文件，以查看输入与输出和评估并排：

```bash
# 计算示例和运行的数量
jq 'length' dataset_*/examples.json
jq 'length' experiment_*/runs.json

# 查看单个连接记录
jq -s '
  .[0] as $dataset |
  .[1][0] as $run |
  ($dataset[] | select(.id == $run.example_id)) as $example |
  {
    input: $example,
    output: $run.output,
    evaluations: $run.evaluations
  }
' dataset_*/examples.json experiment_*/runs.json

# 查找失败的示例（评估分数 < 阈值）
jq '[.[] | select(.evaluations.correctness.score < 0.5)]' experiment_*/runs.json
```

### 确定要优化什么

跨失败查找模式：

1. **比较输出与真实情况**：LLM 输出与预期有何不同？
2. **阅读评估解释**：`eval.*.explanation` 告诉你为什么失败
3. **检查注释文本**：人类反馈描述了具体问题
4. **查找冗长不匹配**：如果输出过长/短与真实情况相比
5. **检查格式合规性**：输出是否符合预期格式？

## 第三阶段：优化提示

### 优化元提示

在 [references/optimization-meta-prompt.md](references/optimization-meta-prompt.md) 中填写三个占位符，并将其发送到您的 LLM（GPT-4o、Claude 等）以生成改进的提示版本。

### 准备性能数据

在粘贴到模板之前，将记录格式化为 JSON 数组：

```bash
# 从数据集 + 实验中：连接并选择相关列
jq -s '
  .[0] as $ds |
  [.[1][] | . as $run |
    ($ds[] | select(.id == $run.example_id)) as $ex |
    {
      input: $ex.input,
      expected: $ex.expected_output,
      actual_output: $run.output,
      eval_score: $run.evaluations.correctness.score,
      eval_label: $run.evaluations.correctness.label,
      eval_explanation: $run.evaluations.correctness.explanation
    }
  ]
' dataset_*/examples.json experiment_*/runs.json

# 从导出的 spans：提取输入/输出对及其注释
jq '[.[] | select(.attributes.openinference.span.kind == "LLM") | {
  input: .attributes.input.value,
  output: .attributes.output.value,
  status: .status_code,
  model: .attributes.llm.model_name
}]' trace_*/spans.json
```

### 应用修订后的提示

在 LLM 返回修订后的消息数组后：

1. 原始和修订后的提示并排比较
2. 验证所有模板变量都保留了
3. 检查格式说明是否完整
4. 在全面部署之前在几个示例上测试

## 第四阶段：迭代

### 优化循环

```
1. 提取提示    -> 第一阶段（一次性）
2. 运行实验    -> ax experiments create ...
3. 导出结果    -> ax experiments export EXPERIMENT_NAME --dataset DATASET_NAME --space SPACE
4. 分析失败    -> jq 查找低分数
5. 运行元提示   -> 第三阶段使用新的失败数据
6. 应用修订提示
7. 重复从步骤 2 开始
```

### 衡量改进

```bash
# 比较跨实验的分数
# 实验 A（基线）
jq '[.[] | .evaluations.correctness.score] | add / length' experiment_a/runs.json

# 实验 B（优化）
jq '[.[] | .evaluations.correctness.score] | add / length' experiment_b/runs.json

# 查找从失败转为通过的反例
jq -s '
  [.[0][] | select(.evaluations.correctness.label == "incorrect")] as $fails |
  [.[1][] | select(.evaluations.correctness.label == "correct") |
    select(.example_id as $id | $fails | any(.example_id == $id))
  ] | length
' experiment_a/runs.json experiment_b/runs.json
```

### 对比两个提示进行 A/B 测试

1. 对同一数据集创建两个实验，每个实验使用不同的提示版本
2. 导出两个：`ax experiments export EXP_A` 和 `ax experiments export EXP_B`
3. 比较平均分数、失败率和特定示例的翻转
4. 检查回归——使用提示 A 通过的示例但使用提示 B 失败的示例

## 提示工程最佳实践

在编写或修订提示时应用这些技巧：

| 技巧 | 应用场景 | 示例 |
|------|----------|------|
| 清晰、详细的说明 | 输出模糊或离题 | "将情感分类为以下之一：positive、negative、neutral" |
| 开头说明 | 模型忽略后面的说明 | 将任务描述放在示例之前 |
| 分步分解 | 复杂的多步骤流程 | "首先提取实体，然后对每个进行分类，然后总结" |
| 特定角色 | 需要一致的风格/语气 | "你是一位高级财务分析师，为机构投资者撰写" |
| 分隔符标记 | 各部分混合在一起 | 使用 `---`、`###` 或 XML 标签将输入与说明分开 |
| 少样本示例 | 输出格式需要澄清 | 显示 2-3 个合成输入/输出对 |
| 输出长度指定 | 响应过长或过短 | "用 2-3 句话回答" |
| 推理说明 | 准确性至关重要 | "在回答之前逐步思考" |
| "我不知道"指南 | 存在幻觉风险 | "如果答案不在提供的上下文中，请说 '我没有足够的信息'" |

### 变量保留

在优化使用模板变量的提示时：

- **单花括号** (`{variable}`)：Python f-string / Jinja 风格。Arize 中最常见。
- **双花括号** (`{{variable}}`)：Mustache 风格。当框架需要时使用。
- 优化过程中**永远不要**添加或删除变量占位符
- **永远不要**重命名变量——运行时替换依赖于确切的名称
- 如果添加少样本示例，请使用字面值，而不是变量占位符

## 工作流

### 从失败的跟踪中优化提示

1. 直接从已知的过滤器中找到失败的跟踪 ID——跳过 `ax traces list` 的人类浏览视图，直接使用可脚本化的路径：
   ```bash
   ax spans export PROJECT --filter "status_code = 'ERROR'" -l 5 --stdout | jq -r '.[0].context.trace_id'
   ```
2. 导出完整跟踪：
   ```bash
   ax spans export PROJECT --trace-id TRACE_ID
   ```
3. 从 LLM span 中提取提示：
   ```bash
   jq '[.[] | select(.attributes.openinference.span.kind == "LLM")][0] | {
     messages: .attributes.llm.input_messages,
     template: .attributes.llm.prompt_template,
     output: .attributes.output.value,
     error: .attributes.exception.message
   }' trace_*/spans.json
   ```
4. 从错误消息或输出中识别失败的原因
5. 使用优化元提示（第三阶段）填充提示和错误上下文
6. 应用修订后的提示

### 使用数据集和实验进行优化

1. 找到数据集和实验：
   ```bash
   ax datasets list --space SPACE
   ax experiments list --dataset DATASET_NAME --space SPACE
   ```
2. 导出两者：
   ```bash
   ax datasets export DATASET_NAME --space SPACE
   ax experiments export EXPERIMENT_NAME --dataset DATASET_NAME --space SPACE
   ```
3. 为元提示准备连接的数据
4. 运行优化元提示
5. 创建一个新的实验以使用修订后的提示来衡量改进

### 调试生成错误格式的提示

1. 导出输出格式错误的 spans：
   ```bash
   ax spans export PROJECT \
     --filter "attributes.openinference.span.kind = 'LLM' AND annotation.format.label = 'incorrect'" \
     -l 10 --stdout > bad_format.json
   ```
2. 查看LLM 生成的与预期的差异
3. 添加明确的格式说明到提示（JSON schema、示例、分隔符）
4. 常见修复：添加显示确切所需输出格式的少样本示例

### 减少 RAG 提示中的幻觉

1. 查找模型出现幻觉的痕迹：
   ```bash
   ax spans export PROJECT \
     --filter "annotation.faithfulness.label = 'unfaithful'" \
     -l 20 --stdout
   ```
2. 导出并检查检索器 + LLM 带宽：
   ```bash
   ax spans export PROJECT --trace-id TRACE_ID
   jq '[.[] | {kind: .attributes.openinference.span.kind, name, input: .attributes.input.value, output: .attributes.output.value}]' trace_*/spans.json
   ```
3. 检查检索到的上下文是否实际包含答案
4. 向系统提示词添加基础指令："仅使用提供的上下文中的信息。如果答案不在上下文中，请说明。"

## 故障排除

| 问题 | 解决方案 |
|------|----------|
| `ax: 命令未找到` | 查看 [参考资料/ax配置.md](references/ax-setup.md) |
| `未找到配置文件` | 未配置配置文件。查看 [参考资料/ax配置文件.md](references/ax-profiles.md) 创建一个配置文件。 |
| 带宽上没有 `input_messages` | 检查带宽类型 -- 链/代理带宽存储提示词在子LLM带宽上，而不是自身 |
| 提示模板是 `null` | 并非所有instrumentations都会发出 `prompt_template`。使用 `input_messages` 或 `input.value` 替代 |
| 优化后变量丢失 | 验证修改后的提示词是否保留了原始中的所有 `{var}` 占位符 |
| 优化使情况更糟 | 检查过拟合问题 -- 元提示词可能记住了测试数据。确保少量示例是合成的 |
| 没有 eval/注释列 | 先运行评估（通过Arize UI或SDK），然后重新导出 |
| 实验输出列未找到 | 列名是 `{experiment_name}.output` -- 通过 `ax experiments get` 检查确切的实验名称 |
| `jq` 在带宽JSON上出错 | 确保你正在针对正确的文件路径（例如，`trace_*/spans.json`） |
