# Agent 评估指南

> **依赖要求：** `agents-cli`（通过 `uv tool install google-agents-cli` 安装）——如需，请先安装 [uv](https://docs.astral.sh/uv/getting-started/installation/index.md)。

> **已使用脚手架项目？** 如果您使用了 `/google-agents-cli-scaffold`，则数据集和自定义指标已在 `tests/eval/`（Python 项目）或 `eval/`（Go 项目）中完成脚手架搭建。为简化起见，本技能及其参考文件使用 Python 目录布局；如果您搭建了 Go agent，请相应调整。
> 您已拥有 `agents-cli eval run`（串联 `generate` + `grade`）、`tests/eval/datasets/` 以及 `tests/eval/eval_config.yaml`。请从执行 `eval run` 开始，并基于此进行迭代。

## 参考文件

| 文件 | 内容 |
|------|----------|
| `references/dataset_schema.md` | 规范的 `EvaluationDataset` 架构 —— 所有字段类型、单轮/多轮/多智能体 JSON 示例、常见错误 |
| `references/metrics-guide.md` | 完整的指标参考 —— 所有内置指标、匹配类型、自定义指标、评判模型配置 |
| `references/user-simulation.md` | 动态对话测试 —— `eval dataset synthesize` 标志、场景类型、兼容指标 |
| `references/builtin-tools-eval.md` | `google_search` 和模型内部工具 —— 轨迹行为、指标兼容性 |
| `references/advanced-commands.md` | 可选命令：`eval analyze`、`eval optimize`、`eval submit` / `eval results` |
| `references/multimodal-eval.md` | 多模态输入 —— 评估数据集架构、内置指标限制、自定义评估器模式 |

---

## 质量飞轮（The Quality Flywheel）

提升 agent 质量是一个迭代过程。下方 4 个阶段描述了该循环。每个阶段都有**默认路径**（即您，作为编码 agent，直接完成任务）和**可选 CLI 命令**（将任务委托给 Agent 平台评估服务以提升质量与规模）。

### 1. 准备数据

**默认：** 使用或编辑脚手架生成的 `tests/eval/datasets/basic-dataset.json` 来定义单轮评估输入。从 1–2 个用例开始。

**可选（ADK 项目）：** `agents-cli eval dataset synthesize`：当您缺乏数据时，模拟用户多轮数据集；其输出已包含 traces，因此第 2 阶段可缩减为仅运行 `agents-cli eval grade`。详见 *Eval Commands* 和 `references/user-simulation.md`。

### 2. 运行评估（始终执行）

**默认：** `agents-cli eval run` 在数据集上运行 agent 并对 traces 进行评分，将 `results_<ts>.{json,html}` 写入 `artifacts/grade_results/`。

**解耦形式：** 先执行 `eval generate`，再执行 `eval grade`，用于自定义 traces 存放位置、在不重新运行 agent 的情况下重新评分，或从 `synthesize`（`eval grade` 单独）生成 traces。

### 3. 分析失败原因

**默认：** 打开最新的 `artifacts/grade_results/results_<ts>.html`（或 `.json`），识别失败的指标 —— 详见下方 *When scores fail（评分失败时该如何修复）* 的修复表。

**可选：** `agents-cli eval analyze`，基于 LLM 的失败聚类；当您有 10 个以上失败用例并希望分类失败模式时优先使用。详见 `references/advanced-commands.md`。

### 4. 优化并修复代码

**默认：** 编辑 agent —— 根据失败分析调整提示词、工具描述、指令或评估数据集。详见下方 *When scores fail（评分失败时该如何修复）* 中的失败 → 修复映射。

**可选（ADK 项目）：** `agents-cli eval optimize` 使用 ADK GEPA 提示词优化针对目标指标（详见 `references/advanced-commands.md`）。适用于仅提示词层面的失败。优化后的提示词会出现在命令输出中；请将其捕获并应用到 agent 中。如需完整的逐轮 trace，请在优化配置文件设置 `print_detailed_results: true`。

> **运行耗时且成本较高。** GEPA 优化会发起大量 LLM 调用，可能耗时较长。除非用户明确要求提示词优化，否则不要运行。运行后，先用手动修复尽可能多轮，再运行**一次**最终 `eval optimize` —— 切勿循环执行此命令。

### 运行循环

迭代阶段 2 → 3 → 4 → 2（每次迭代经过 `synthesize` 时，重新执行第 1 阶段，随后执行 `eval grade`）。每次修复后，运行 `agents-cli eval compare <prev_results>.json <new_results>.json` 以确认目标指标提升且未导致其他指标下降。通常一个用例需要 5–10 次以上迭代才能通过，这是正常现象。只有用例通过后才应扩展评估用例覆盖范围。

进行 5 次以上迭代时，维护一个任务列表，记录哪些用例已修复、哪些仍在失败、以及尝试过哪些修复方法，以避免重复尝试相同的修复。

**保留用例。** 将一部分用例保留在循环之外，仅在您认为已完成时对其进行评分 —— 否则无法判断某项修复是否从迭代过的用例泛化到未测试的用例。

### 浪费时间的方法

识别以下理性化借口并予以反对 —— 它们花费的时间总是多于省下的：

| 方法 | 失败原因 |
|----------|-------------|
| "我会降低门槛使其通过" | 降低门槛会掩盖真实失败。若 agent 无法满足门槛，应修复 agent，而非调整门槛。 |
| "此评估用例不稳定，我将跳过它" | 不稳定的评估揭示了 agent 的非确定性。请通过 `temperature=0`、基于评分标准的评估或更具体的指令修复，而非删除该信号。 |
| "我只需修复评估数据集，而非 agent" | 若您总是调整预期输出，说明 agent 存在行为问题。应优先修复指令或工具逻辑。 |
| "我会迭代直至我拥有的所有用例都通过" | 没有未检测到的、针对您自有用例的过拟合。详见上方 *Hold cases back（保留用例）*。 |

## 选择合适指标

根据您想测量的目标选择内置指标。只有 `multi_turn_task_success`、`multi_turn_trajectory_quality` 和 `multi_turn_tool_use_quality` 接受多轮 traces；其余每个内置指标在单轮输入上均得 0 分。当没有内置指标适用时，编写自定义指标（见下方 *Evaluation Configuration Schema（评估配置模式）*）。

| 目标 | 推荐的内置指标 |
|------|------------------------------|
| **agent 是否达成了用户目标？**（多轮 agent 的兜底选项） | `multi_turn_task_success` |
| **agent 的推理路径是否逻辑且高效？** | `multi_turn_trajectory_quality` |
| **多轮的工具/函数调用质量？** | `multi_turn_tool_use_quality` |
| **最终回复质量**（无需 ground-truth 参考） | `final_response_quality` |
| **事实佐证**（捕捉幻觉声明，如 RAG agent） | `hallucination`，或当用例携带 `context` 字段时使用 `grounding` |
| **安全策略合规性** | `safety` |
| **与标准答案匹配** | `final_response_match`（需在用例上设置 `reference`） |
| **各用例有不同通过/失败标准** | 将其置于用例的 `rubric_groups` 中，使用受管评分标准指标进行评分。详见 `references/dataset_schema.md`（*Per-Case Rubrics（按用例评分标准）*）。 |
| **内置指标未覆盖的特定领域检查** | 编写自定义 `LLMMetric`（LLM 评判）或 `CodeExecutionMetric`（确定性 Python）。详见 *Evaluation Configuration Schema（评估配置模式）*。 |

运行 `agents-cli eval metric list` 查看所有可用内置指标。有关完整指标定义和评分标准详情，请参阅 [Agent 平台指标文档](https://cloud.google.com/gemini-enterprise-agent-platform/optimize/evaluation/manage-metrics) 和 `references/metrics-guide.md`。

---

## 评分失败时该如何修复

`agents-cli eval run` 完成后，检查最新的 `artifacts/grade_results/results_<timestamp>.json`（或打开 `.html` 文件），获取各用例分数与评判理由，这是以下所有修复决策的输入。

| 失败情况 | 需修改内容 |
|---------|---------------|
| `multi_turn_task_success` 分数低 | agent 未完成用户目标 —— 修复编排、缺失工具调用、过早终止或工具选择错误 |
| `multi_turn_trajectory_quality` 分数低 | agent 虽达成目标但效率低下或步骤错误 —— 细化规划提示词、收紧指令顺序，或移除冗余工具调用 |
| `multi_turn_tool_use_quality` 分数低 | 修复工具描述、参数 docstring 或 agent 对工具的选择指令 |
| `final_response_quality` 分数低 | 阅读自动生成的评分标准判定；细化 agent 指令以解决得分最低的准则（通常为清晰度、完整性或指令遵循） |
| `hallucination` 分数低 | 收紧 agent 指令，使其始终基于工具输出进行佐证；验证工具是否确实返回了 agent 声称的数据 |
| `safety` 分数低 | 在指令中添加安全护栏；查阅评分标准判定中违规内容类别 |
| agent 调用错误工具 | 修复工具描述、agent 指令或模型的工具选择配置（**ADK：** `tool_config`） |
| agent 调用额外工具 | 添加严格的停止指令，或切换到 `multi_turn_tool_use_quality` |

应用修复后，重新运行 `agents-cli eval run`，并使用 `agents-cli eval compare <prev_results>.json <new_results>.json` 确认修复提升了目标指标且未导致其他指标下降。

---

## 评估命令

`agents-cli eval <subcommand> --help` 是权威的 flag 列表；以下示例为常见调用方式。

### `eval run`（默认）

在一次命令中在数据集上运行 agent 并对 traces 进行评分。

```bash
# 基础用法：使用 tests/eval/datasets/ 中的数据集，结果输出到 artifacts/grade_results/，
# 指标来自 tests/eval/eval_config.yaml
agents-cli eval run

# 进阶用法：选择数据集、指标和输出目录
agents-cli eval run --dataset tests/eval/datasets/custom.json --metrics final_response_quality,safety --output ./out/
```

### `eval generate`

在评估数据集上运行 agent 并将 traces 写入磁盘。

默认在本地运行 agent，为每个评估用例记录一条 trace。也可通过向 `--url` 和 `--app-name` 传入正在运行的 agent 的 HTTP 端点和应用名，从已运行的 agent 生成 traces。

> **ADK 项目。** 内置生成器通过 HTTP 提供 agent 服务，并驱动 ADK 的 `/apps/...` 和 `/run_sse` 路由 —— 与 `--url` / `--app-name` 所期望的形态一致。其启动内容取决于项目的语言：Python 使用项目中的 `fast_api_app.py`（若存在），否则使用 `adk api_server`；Go 执行 `go run ...`。其他框架的扩展将 `eval generate` 替换为自身的生成器，可能不提供 HTTP 服务；此时 `--url` 和 `--app-name` 不受支持。

```bash
# 基础用法 —— 使用 tests/eval/datasets/，写入 artifacts/traces/
agents-cli eval generate

# 进阶用法 —— 自定义数据集和输出目录
agents-cli eval generate --dataset tests/eval/datasets/custom.json -o ./custom_traces/

# 针对已部署的 agent（或手动启动的 agent）
agents-cli eval generate --url https://my-agent.run.app --app-name app
```

### `eval grade`

将 traces（来自 `eval generate`、`eval dataset synthesize` 或手工编写）根据内置或自定义指标进行评分。将带时间戳的 `results_<YYYYMMDD_HHMMSS>.json`（供 `eval compare` 使用）和 `.html`（在浏览器中打开）写入输出目录，并向控制台打印汇总表。

```bash
# 基础用法 —— 默认：traces 来自 artifacts/traces/，结果输出到 artifacts/grade_results/，
# 指标来自 tests/eval/eval_config.yaml 的 metrics_to_run
agents-cli eval grade

# 进阶用法 1 —— 对非默认位置的 traces 进行评分（与 `eval generate --output custom_traces/` 的标准搭配）
agents-cli eval grade --traces custom_traces/

# 进阶用法 2：从配置文件（YAML 或 JSON）加载待运行的指标，并针对指定 trace 文件进行评分。
agents-cli eval grade --traces ./artifacts/traces/trace_1.json --config tests/eval/eval_config.yaml

# 进阶用法 3：分发速率，默认 15 个指标计算/秒。当评判模型或评估服务限流时降低该值；有带宽时提高该值。
agents-cli eval grade --qps 5
```

详见 *Evaluation Configuration Schema（评估配置模式）* 了解配置文件格式。

### `eval compare`

对比两个评估运行生成的 `results_*.json` 文件。修复后运行以确认目标指标提升且未导致其他指标下降。

```bash
agents-cli eval compare baseline.json candidate.json
```

### `eval dataset synthesize`

> **ADK 项目。** 它会加载并运行 agent，因此在其他框架上不可用。

根据 agent 的工具与指令生成用户场景，将其逐一与基于 LLM 的用户模拟器对抗，并将就绪评分的 traces 写入 `artifacts/traces/`（直接用于 `eval grade`，无需执行 `eval generate`）。调用方式、标志及兼容指标见 `references/user-simulation.md`。

### 进阶命令

`eval analyze`（聚类失败模式）、`eval optimize`（GEPA 提示词调优）以及 `eval submit` / `eval results`（用于 CI 或大型数据集的云端托管运行）的文档见 `references/advanced-commands.md`。

---

## 评估数据集格式

`EvaluationDataset` 是一个包含 `eval_cases` 数组的 JSON 文件。用例有两种形态，取决于使用方式：

- **推理输入**（提供给 `eval generate` 的内容）—— 一个用户提示词或一个以用户提示词结尾的对话片段。agent 运行并生成 traces。
- **评分输入**（提供给 `eval grade` 的内容）—— 包含 agent 回复与 `function_call` / `function_response` 部分的完整 trace。通常由 `eval generate` 或 `eval dataset synthesize` 生成；无需手工编写。

详见 `references/dataset_schema.md` 了解完整的规范架构、所有字段类型及常见错误。

### 推理输入格式

支持两种形态。

**(a) 简单单轮提示词** —— 脚手架 `tests/eval/datasets/basic-dataset.json` 使用的形式。agent 从零开始运行。

```json
{
  "eval_cases": [
    {
      "eval_case_id": "greeting",
      "prompt": {
        "role": "user",
        "parts": [{"text": "Hello, what can you help me with?"}]
      }
    }
  ]
}
```

**(b) 通过 `agent_data` 进行多轮延续** —— 一个以用户消息结尾的对话片段；评估 agent 的下一次回复。详见 `references/dataset_schema.md`（*Multi-Turn / Multi-Agent Dataset（多轮/多智能体数据集）*）了解 JSON 形态。

### 评分输入格式（traces）

一个完整 trace —— agent 回复加上 `function_call` / `function_response` 部分 —— 通常由 `eval generate` / `eval dataset synthesize` 生成（无需手工编写）。作者为 `"user"`、`agents` 映射中的 agent ID，或 `"tool"`。详见 `references/dataset_schema.md` 了解 trace 形态、多智能体示例及完整类型参考。

---

## 评估配置模式

`agents-cli eval run --config <path>`（以及 `eval grade --config <path>`）接受单个配置文件，格式为 **YAML**（`.yaml` / `.yml`）或 **JSON**（`.json`）。文件包含两部分：

- `metrics_to_run`：本次运行要执行的**指标选择列表**。名称解析为 `custom_metrics` 中匹配的条目，否则解析为该名称对应的内置指标。
- `custom_metrics` —— 本项目可用的**自定义指标定义池**。在此定义指标**不会运行**该指标；它还必须出现在 `metrics_to_run` 中（或通过 CLI 上的 `--metrics name1,name2` 传入，等效于对该调用覆盖 `metrics_to_run`）。

**最小示例（推荐 YAML —— 人类可读，提示词与 Python 无需 JSON 转义）：**

```yaml
metrics_to_run:
  - multi_turn_task_success     # 内置
  - example_llm_metric          # 从下方 custom_metrics 池中选取
  - agent_turn_count            # 从下方 custom_metrics 池中选取

custom_metrics:
  - name: example_llm_metric
    prompt_template: |
      Rate the agent's response 1-5 for helpfulness and accuracy.
      Prompt: {prompt}
      Final response: {response}
      Full trace (for tool-call and reasoning context): {agent_data}
      Return JSON: {"score": <1|2|3|4|5>, "explanation": "<reason>"}

  - name: agent_turn_count
    custom_function: |
      def evaluate(instance):
          turns = (instance.get("agent_data") or {}).get("turns", [])
          return {'score': len(turns)}
```

也接受 JSON（字段名相同，`prompt_template` 和 `custom_function` 为转义字符串）——但**始终优先使用 YAML** 进行人类可读的配置。

按字段分发：`custom_function` → Python 指标；`prompt_template` → `LLMMetric`（LLM 评判）；两者皆无且为内置名称 → 该内置指标参数化（如 `metric_spec_parameters.rubric_group_key`）。字段参考：`references/metrics-guide.md`。

**Agent trace 字段模型。** 对于由 `agents-cli eval generate`（或 `eval dataset synthesize`）生成的 datasets，每个评估用例为指标提供三个标准字段：

- `{prompt}` —— 用户消息（或首个用户轮次）。
- `{response}` —— 从最后一个承载文本的事件中提取的 agent 最终文本回复。在 `custom_function` 回调中，此为 `instance['response']`，形态为 `{"role": "model", "parts": [{"text": "..."}]}`。
- `{agent_data}` —— 完整的结构化 `turns`/`events` trace，评判模型需要推理工具调用或中间推理时使用。

`reference`、`context` 和 `rubric_groups` 由您自行编写：`eval generate` 会将它们携带至 trace 但**不会**自行编造，因此 `{reference}` / `{context}` 仅在您已编写的地方解析。`rubric_groups` 并非占位符：受管评分标准指标会从其读取，且 `custom_function` 会看到 `instance['rubric_groups']`。详见 `references/dataset_schema.md`（*Per-Case Rubrics（按用例评分标准）*）。

基于代码的指标默认以**进程内执行**方式运行（无需 GCP 项目或区域，但 `evaluate(instance)` 函数以 CLI 的权限运行）。设置指标的 `execution: "remote"` 可在 Vertex AI 的 `CodeExecutionMetric` 沙箱中以服务端方式运行该指标 —— 此路径需要已配置的 GCP 项目 + 区域。

---

## 常见陷阱

### 使用基于评分标准的工具评估，而非硬编码序列

使用严格的序列匹配来评估 agent 工具使用存在脆弱性，因为 agent 可能以不同顺序调用辅助工具（如搜索或地理编码），或执行额外的主动步骤。

 Instead，使用 **`multi_turn_tool_use_quality`** / **`multi_turn_trajectory_quality`**。这些指标自动生成基于内容且基于意图的适应性评分标准，通过 LLM 评判在语义上评估技术正确性与技术序列逻辑，而非强制刚性匹配。

### App 名称必须与目录名称一致

> **ADK 项目。**

`App` 对象的 `name` 参数**必须**与包含 agent 的目录匹配：

```python
# 正确 —— 与 "app" 目录匹配
app = App(root_agent=root_agent, name="app")

# 错误 —— 导致 "Session not found" 错误
app = App(root_agent=root_agent, name="flight_booking_assistant")
```

### Vertex 评估区域

`eval run`、`eval grade` 和 `eval submit` **默认使用 `global` 端点**。它们不继承 manifest 的 `region`（评估服务仅支持部分区域），且 `eval analyze` 仅支持 `global`。可通过 `--region <REGION>`（如数据驻留需求）在单次运行中覆盖这些设置；服务会拒绝不支持的区域：

```
400 FAILED_PRECONDITION: Unsupported region for Vertex Evaluation Service: <region>
```

`eval generate`（不带 `--url` 标志）和 `eval dataset synthesize` 在本地运行 agent，因此它们遵循 agent 自身的 `.env` ——  notably `GOOGLE_CLOUD_LOCATION`，当 agent 使用 Vertex AI 时用于选择模型端点（`GOOGLE_GENAI_USE_VERTEXAI=true`）；使用 `GEMINI_API_KEY`（AI Studio）时未使用。它们**不使用** `--region`，也**不会**用 manifest 的 `region` 覆盖您的 `.env`；请通过编辑 `.env` 更改模型区域。关于 `synthesize` 的一个注意事项：其场景生成步骤是**服务端**的评估调用，位于 `GOOGLE_CLOUD_LOCATION`，因此请保持该区域为评估支持的区域（默认 `global`），即使 agent 本身可在其他地方运行。

**没有任何评估区域符合您的数据驻留规则？** 回退至**本地自定义指标** —— 一个包含 `custom_function`（`execution: local`，默认）的 `custom_metrics` 条目，在进程内进行评分，无需 GCP 区域。您会失去托管的内置指标，但 `custom_function` 仍可自行在合规区域调用 LLM 评判 —— 因此 LLM 评判评分在任何地方都可用。

### `before_agent_callback` 模式（状态初始化）

> **ADK 项目。**

始终使用回调来初始化指令模板中使用的会话状态变量。这可防止首轮出现的 `KeyError` 崩溃：

```python
async def initialize_state(callback_context: CallbackContext) -> None:
    state = callback_context.state
    if "user_preferences" not in state:
        state["user_preferences"] = {}

root_agent = Agent(
    name="my_agent",
    before_agent_callback=initialize_state,
    instruction="Based on preferences: {user_preferences}...",
)
```

### 模型思考模式可能绕过工具

开启"思考"的模型可能跳过工具调用。请通过模型的工具选择配置强制工具使用（**ADK：** `tool_config` 且 `mode="ANY"`），或切换为非思考模型以获得可预测的工具调用。

---

## 常见评估失败原因

| 症状 | 原因 | 修复 |
|---------|-------|-----|
| 分数在多次运行间波动 | 模型非确定性 | 设置 `temperature=0` 或使用基于评分标准的评估且多个样本 |
| LLM 评判忽略评估中的图片/音频 | `get_text_from_content()` 跳过非文本部分 | 使用支持视觉评判的自定义指标（详见 `references/multimodal-eval.md`） |

---

## 证明您的成果

不要断言评估通过 —— 展示证据。具体输出可防止虚假自信，并及早发现问题。

- **运行评估后：** 粘贴分数表输出，让用户看到哪些已通过、哪些未通过。
- **修复失败后：** 展示所修复用例的修复前后分数，并确认其他用例未下降。
- **部署前：** 重新运行 `agents-cli eval run`，展示所有用例的分数，而非仅修复过的用例。`eval run` 在任何分数下均以 0 退出，因此您粘贴的数值是门槛，而非退出码。

---

## 相关技能

- `/google-agents-cli-workflow` — 开发工作流与 spec-driven 的构建-评估-部署生命周期
- `/google-agents-cli-adk-code` — ADK API 快速参考（仅 ADK 项目）
- `/google-agents-cli-scaffold` — 使用 `agents-cli scaffold create` / `scaffold enhance` 创建与增强项目
- `/google-agents-cli-deploy` — 部署目标、CI/CD 流水线与生产工作流
- `/google-agents-cli-observability` — 云端 Trace、日志与监控，用于调试 agent 行为
