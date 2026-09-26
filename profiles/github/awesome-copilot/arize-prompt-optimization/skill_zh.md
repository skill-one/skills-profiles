# Arize 提示优化技能

> **`SPACE`** — 所有 `--space` 标志和 `ARIZE_SPACE` 环境变量都接受一个空间 **名称**（例如，`my-workspace`）或 base64 空间 **ID**（例如，`U3BhY2U6...`）。使用 `ax spaces list` 查找您的空间。

## 概念

### 提示数据在跟踪数据中的存储位置

LLM 应用程序遵循 OpenInference 语义规范发出跨度。提示存储在不同的跨度属性中，具体取决于跨度类型和instrumentation：

| 列 | 包含的内容 | 使用时机 |
|----|------------|----------|
| `attributes.llm.input_messages` | 结构化聊天消息（系统、用户、助手、工具）在基于角色的格式中 | **主要来源**用于基于聊天的 LLM 提示 |
| `attributes.llm.input_messages.roles` | 角色数组：`system`、`user`、`assistant`、`tool` | 提取单个消息角色 |
| `attributes.llm.input_messages.contents` | 消息内容字符串数组 | 提取消息文本 |
| `attributes.input.value` | 序列化的提示或用户问题（通用，所有跨度类型） | 当结构化消息不可用时作为备用 |
| `attributes.llm.prompt_template.template` | 使用 `{variable}` 占位符的模板（例如，`"使用 {context} 回答 {question}"`） | 当应用程序使用提示模板时 |
| `attributes.llm.prompt_template.variables` | 模板变量值（JSON 对象） | 查看模板中使用了哪些值 |
| `attributes.output.value` | 模型响应文本 | 查看LLM生成了什么 |
| `attributes.llm.output_messages` | 结构化的模型输出（包括工具调用） | 检查工具调用响应 |

### 通过跨度类型查找提示

- **LLM 跨度** (`attributes.openinference.span.kind = 'LLM'`)：检查 `attributes.llm.input_messages` 获取结构化聊天消息，或检查 `attributes.input.value` 获取序列化提示。检查 `attributes.llm.prompt_template.template` 获取模板。
- **链/代理跨度**：`attributes.input.value` 包含用户的问题。实际的 LLM 提示存储在 **子 LLM 跨度**上——沿着跟踪树向下导航。
- **工具跨度**：`attributes.input.value` 包含工具输入，`attributes.output.value` 包含工具结果。通常不是提示存储的位置。

### 性能信号列

这些列携带用于优化的反馈数据：

| 列模式 | 来源 | 告诉你什么 |
|-------|------|------------|
| `annotation.<name>.label` | 人类审阅者 | 分类等级（例如，`correct`、`incorrect`、`partial`） |
| `annotation.<name>.score` | 人类审阅者 | 数值质量分数（例如，0.0 - 1.0） |
| `annotation.<name>.text` | 人类审阅者 | 对等级的自由形式解释 |
| `eval.<name>.label` | LLM 作为评判者评估 | 自动化分类评估 |
| `eval.<name>.score` | LLM 作为评判者评估 | 自动化数值分数 |
| `eval.<name>.explanation` | LLM 作为评判者评估 | 评估给出该分数的原因——**对优化最有价值** |
| `attributes.input.value` | 跟踪数据 | 输入到 LLM 的内容 |
| `attributes.output.value` | 跟踪数据 | LLM 生成的输出 |
| `{experiment_name}.output` | 实验运行 | 特定实验的输出 |

## 前提条件

直接执行任务——运行您需要的 `ax` 命令。**不要**提前检查版本、环境变量或配置文件。

如果 `ax` 命令失败，根据错误进行故障排除：
- `command not found` 或版本错误 → 查看 references/ax-setup.md
- `401 Unauthorized` / 缺少 API 密钥 → 运行 `ax profiles show` 检查当前配置文件。如果配置文件缺失或 API 密钥错误，请遵循 references/ax-profiles.md 创建/更新它。如果用户没有他们的密钥，请指导他们到 https://app.arize.com/admin > API Keys
- 空间未知 → 运行 `ax spaces list` 通过名称选择，或询问用户
- 项目不明确 → 询问用户，或运行 `ax projects list -o json --limit 100` 并作为可选选项呈现
- LLM 提供商调用失败（缺少 OPENAI_API_KEY / ANTHROPIC_API_KEY）→ 运行 `ax ai-integrations list --space SPACE` 检查平台管理的凭证。如果不存在，请要求用户提供密钥或通过 **arize-ai-provider-integration** 技能创建集成
- **安全**：**永远不要**读取 `.env` 文件或在文件系统中搜索凭证。使用 `ax profiles` 存储Arize凭证，使用 `ax ai-integrations` 存储LLM提供商标识符。如果通过这些渠道无法获取凭证，请要求用户。

## 第一阶段：提取当前提示

### 查找包含提示的 LLM 跨度

```bash
# 示例 LLM 跨度（提示存储的位置）
ax spans export PROJECT --filter "attributes.openinference.span.kind = 'LLM'" -l 10 --stdout

# 按模型过滤
ax spans export PROJECT --filter "attributes.llm.model_name = 'gpt-4o'" -l 10 --stdout

# 按跨度名称过滤（例如，特定的 LLM 调用）
ax spans export PROJECT --filter "name = 'ChatCompletion'" -l 10 --stdout
```

### 导出跟踪以检查提示结构

```bash
# 导出跟踪中的所有跨度
ax spans export PROJECT --trace-id TRACE_ID

# 导出单个跨度
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

# 从 input.value（非结构化提示的备用方案）提取
jq '.[0].attributes.input.value' trace_*/spans.json
```

### 将提示重构为消息数组

一旦您有了跨度数据，将提示重构为消息数组：

```json
[
  {"role": "system", "content": "You are a helpful assistant that..."},
  {"role": "user", "content": "Given {input}, answer the question: {question}"}
]
```

如果跨度有 `attributes.llm.prompt_template.template`，提示使用变量。保留这些占位符（`{variable}` 或 `{{variable}}`）——它们在运行时会被替换。

## 第二阶段：收集性能数据

### 从跟踪（生产反馈）

```bash
# 查找错误跨度——这些表示提示失败
ax spans export PROJECT \
  --filter "status_code = 'ERROR' AND attributes.openinference.span.kind = 'LLM'" \
  -l 20 --stdout

# 查找评分较低的跨度
ax spans export PROJECT \
  --filter "annotation.correctness.label = 'incorrect'" \
  -l 20 --stdout

# 查找高延迟的跨度（可能表示过于复杂的提示）
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

通过 `example_id` 连接这两个文件，以查看输入与输出和评估并置：

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

### 确定要优化的内容

查找失败模式：

1. **比较输出与真实情况**：LLM 输出与预期有何不同？
2. **阅读评估解释**：`eval.*.explanation` 告诉你为什么失败
3. **检查注释文本**：人类反馈描述了具体问题
4. **查找冗长性不匹配**：如果输出过长/短与真实情况相比
5. **检查格式合规性**：输出是否符合预期格式？

## 第三阶段：优化提示

### 优化元提示

使用此模板生成提示的改进版本。填写三个占位符并将它发送到你的 LLM（GPT-4o、Claude 等）：

````
你是一位提示优化的专家。给定原始基线提示和相关性能数据（输入、输出、评估标签和解释），生成一个改进的版本。

原始基线提示
========================

{粘贴原始提示到这里}

========================

性能数据
================

以下记录显示了当前提示的性能。每条记录包括输入、LLM 输出和评估反馈：

{粘贴记录到这里}

================

如何使用这些数据

1. 比较输出：查看 LLM 生成的与预期的有何不同
2. 查看评估分数：检查哪些示例得分低以及原因
3. 检查注释：人类反馈显示了哪些地方有效和无效
4. 识别模式：查找多个示例中的常见问题
5. 关注失败：输出与预期值不同的行需要修复

对齐策略

- 如果输出有额外文本或不在真实情况中出现的推理，删除鼓励解释或冗长推理的指令
- 如果输出缺少信息，添加指令以包含它
- 如果输出格式错误，添加明确的格式指令
- 关注输出与目标不同的行——这些是需要修复的失败

规则

保持结构：

- 使用与当前提示相同的模板变量（{var} 或 {{var}})
- 不要更改已经起作用的区域
- 保留原始提示中精确的返回格式指令

避免过拟合：

- **不要**将示例逐字复制到提示中
- **不要**精确引用特定测试数据输出
- **相反**：提取使输出好与坏的实质内容
- **相反**：添加一般指南和原则
- **相反**：如果添加少量示例，创建合成示例来展示原则，而不是上面的真实数据

目标：创建一个对新的输入泛化良好的提示，而不是一个记忆测试数据的提示。

输出格式

将修订后的提示作为消息 JSON 数组返回：

[
  {"role": "system", "content": "..."},
  {"role": "user", "content": "..."}
]

还提供简要的推理部分（项目符号列表），解释：

- 你发现了什么问题
- 修订后的提示如何解决每个问题
````

### 准备性能数据

将记录格式化为 JSON 数组，然后粘贴到模板中：

```bash
# 从数据集 + 实验合并并选择相关列
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

# 从导出的跨度：提取输入/输出对与注释
jq '[.[] | select(.attributes.openinference.span.kind == "LLM") | {
  input: .attributes.input.value,
  output: .attributes.output.value,
  status: .status_code,
  model: .attributes.llm.model_name
}]' trace_*/spans.json
```

### 应用修订后的提示

LLM 返回修订后的消息数组后：

1. 原始和修订后的提示并排比较
2. 验证所有模板变量都保留
3. 检查格式指令是否完整
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
7. 重复步骤 2
```

### 衡量改进

```bash
# 比较跨实验的分数
# 实验 A（基线）
jq '[.[] | .evaluations.correctness.score] | add / length' experiment_a/runs.json

# 实验 B（优化）
jq '[.[] | .evaluations.correctness.score] | add / length' experiment_b/runs.json

# 查找从失败转为成功的示例
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
3. 比较平均分数、失败率和特定示例的转换
4. 检查是否存在回归——使用提示 A 通过的示例使用提示 B 失败

## 提示工程最佳实践

在编写或修订提示时应用这些技巧：

| 技巧 | 应用时机 | 示例 |
|------|----------|------|
| 清晰、详细的指令 | 输出模糊或离题 | "将情绪分类为以下之一：正面、负面、中性" |
| 指令在开头 | 模型忽略后续指令 | 将任务描述放在示例之前 |
| 步骤分解 | 复杂的多步骤流程 | "首先提取实体，然后对每个进行分类，然后总结" |
| 特定角色 | 需要一致的风格/语气 | "你是一位高级财务分析师，为机构投资者撰写" |
| 分隔符标记 | 各部分混合在一起 | 使用 `---`、`###` 或 XML 标签将输入与指令分开 |
| 少量示例 | 输出格式需要澄清 | 显示 2-3 个合成输入/输出对 |
| 输出长度指定 | 响应过长或过短 | "用 2-3 句话回答" |
| 推理指令 | 准确性至关重要 | "逐步思考后再回答" |
| "我不知道" 指令 | 存在幻觉风险 | "如果答案不在提供的上下文中，就说'我没有足够的信息'" |

### 变量保留

在优化使用模板变量的提示时：

- **单花括号** (`{variable}`)：Python f-string / Jinja 风格。Arize 中最常见。
- **双花括号** (`{{variable}}`)：Mustache 风格。当框架需要时使用。
- 优化期间**永远不要**添加或删除变量占位符
- **永远不要**重命名变量——运行时替换依赖于确切的名称
- 如果添加少量示例，使用字面值，而不是变量占位符

## 工作流程

### 从失败跟踪优化提示

1. 查找失败跟踪：
   ```bash
   ax traces list PROJECT --filter "status_code = 'ERROR'" --limit 5
   ```
2. 导出跟踪：
   ```bash
   ax spans export PROJECT --trace-id TRACE_ID
   ```
3. 从 LLM 跨度提取提示：
   ```bash
   jq '[.[] | select(.attributes.openinference.span.kind == "LLM")][0] | {
     messages: .attributes.llm.input_messages,
     template: .attributes.llm.prompt_template,
     output: .attributes.output.value,
     error: .attributes.exception.message
   }' trace_*/spans.json
   ```
4. 从错误消息或输出中识别失败内容
5. 填写优化元提示（第三阶段）与提示和错误上下文
6. 应用修订后的提示

### 使用数据集和实验优化

1. 查找数据集和实验：
   ```bash
   ax datasets list --space SPACE
   ax experiments list --dataset DATASET_NAME --space SPACE
   ```
2. 导出两者：
   ```bash
   ax datasets export DATASET_NAME --space SPACE
   ax experiments export EXPERIMENT_NAME --dataset DATASET_NAME --space SPACE
   ```
3. 准备用于元提示的合并数据
4. 运行优化元提示
5. 使用修订后的提示创建新实验以衡量改进

### 调试生成错误格式的提示

1. 导出输出格式错误的跨度：
   ```bash
   ax spans export PROJECT \
     --filter "attributes.openinference.span.kind = 'LLM' AND annotation.format.label = 'incorrect'" \
     -l 10 --stdout > bad_format.json
   ```
2. 查看LLM生成的与预期的有何不同
3. 向提示添加明确的格式指令（JSON schema、示例、分隔符）
4. 常见修复：添加显示所需输出格式的少量示例

### 减少RAG提示中的幻觉

1. 查找模型幻觉的跟踪：
   ```bash
   ax spans export PROJECT \
     --filter "annotation.faithfulness.label = 'unfaithful'" \
     -l 20 --stdout
   ```
2. 导出并检查检索器 + LLM 跨度：
   ```bash
   ax spans export PROJECT --trace-id TRACE_ID
   jq '[.[] | {kind: .attributes.openinference.span.kind, name, input: .attributes.input.value, output: .attributes.output.value}]' trace_*/spans.json
   ```
3. 检查检索到的上下文是否实际包含答案
4. 在系统提示中添加接地指令："仅使用提供的上下文。如果答案不在上下文中，就说这样。"

## 故障排除

| 问题 | 解决方案 |
|------|----------|
| `ax: command not found` | 查看 references/ax-setup.md |
| `No profile found` | 未配置配置文件。查看 references/ax-profiles.md 创建一个。 |
| 跨度上没有 `input_messages` | 检查跨度类型——Chain/Agent 跨度将提示存储在子 LLM 跨度上，而不是自身 |
| 提示模板是 `null` | 并非所有instrumentations都发出 `prompt_template`。使用 `input_messages` 或 `input.value` 代替 |
| 优化后变量丢失 | 验证修订后的提示保留了原始中的所有 `{var}` 占位符 |
| 优化使情况变得更糟 | 检查过拟合——元提示可能记住了测试数据。确保少量示例是合成的 |
| 没有eval/annotation列 | 首先运行评估（通过 Arize UI 或 SDK），然后重新导出 |
| 实验输出列未找到 | 列名称是 `{experiment_name}.output` —— 检查确切的实验名称 via `ax experiments get` |
| `jq` 在跨度 JSON 上出错 | 确保您正在针对正确的文件路径（例如，`trace_*/spans.json`） |
