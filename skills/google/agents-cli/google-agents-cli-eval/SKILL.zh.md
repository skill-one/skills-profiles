---
name: google-agents-cli-eval
description: 当用户想要“运行评估”、“评估我的代理”、“评估我的ADK代理”、“编写评估数据集”、“分析评估失败”、“比较评估结果”、“优化代理”，或需要有关代理平台评估方法和质量飞轮的指导时，应使用此技能。涵盖评估指标、数据集架构、LLM作为评委的评分以及常见失败原因。适用于任何agents-cli项目，无论代理是用什么框架编写的。不应用于代理API代码模式（ADK：使用google-agents-cli-adk-code）、部署（使用google-agents-cli-deploy）或项目脚手架（使用google-agents-cli-scaffold）。
---

# 代理评估指南

> **要求：** `agents-cli` (`uv tool install google-agents-cli`) — 如果需要，请先安装 uv：[安装 uv](https://docs.astral.sh/uv/getting-started/installation/index.md)。

> **使用脚手架项目？** 如果你使用了 `/google-agents-cli-scaffold`，数据集和自定义指标已经在 `tests/eval/`（Python 项目）或 `eval/`（Go 项目）中预构建。为了简化，本技能及其参考使用 Python 目录结构；如果你构建了 Go 代理，请相应调整。
> 你已经拥有 `agents-cli eval run`（串联 `generate` + `grade`）、`tests/eval/datasets/` 和 `tests/eval/eval_config.yaml`。从执行 `eval run` 开始，并从这里迭代。

## 参考文件

| 文件 | 内容 |
|------|----------|
| `references/dataset_schema.md` | 标准评估数据集 schema — 所有字段类型、单轮/多轮/多代理的 JSON 示例、常见错误 |
| `references/metrics-guide.md` | 完整指标参考 — 所有内置指标、匹配类型、自定义指标、裁判模型配置 |
| `references/user-simulation.md` | 动态对话测试 — `eval dataset synthesize` 标志、场景是什么、兼容的指标 |
| `references/builtin-tools-eval.md` | google_search 和模型内部工具 — 轨迹行为、指标兼容性 |
| `references/advanced-commands.md` | 选择性命令：`eval analyze`、`eval optimize`、`eval submit` / `eval results` |
| `references/multimodal-eval.md` | 多模态输入 — 评估数据集 schema、内置指标限制、自定义评估器模式 |
| `references/live-eval.md` | 活体和语音代理 — `--mode adk_live`、评估内容、仅用户编写的回合、Live 模型和区域陷阱 |

---

## 质量飞轮

提高代理质量是一个迭代过程。下面的四个阶段描述了这个循环。每个阶段都有一个默认路径（你，编码代理，直接执行工作）和一个选择性 CLI 命令，该命令委托给代理平台评估服务以获得更好的质量和规模。

### 1. 准备数据

**默认：** 使用或编辑预构建的 `tests/eval/datasets/basic-dataset.json` 来定义单轮评估输入。从 1-2 个案例开始。

**选择性（ADK 项目）：** `agents-cli eval dataset synthesize`：当您缺乏数据时，使用用户模拟多轮数据集；其输出已经包含轨迹，因此阶段 2 简化为 `agents-cli eval grade`。参见 *评估命令* 和 `references/user-simulation.md`。

### 2. 运行评估（始终运行）

**默认：** `agents-cli eval run` 运行代理并覆盖数据集，对轨迹进行评分，将 `results_<ts>.{json,html}` 写入 `artifacts/grade_results/`。

**解耦形式：** `eval generate` 然后是 `eval grade`，用于自定义轨迹位置、重新评分而不重新运行代理，或来自 `synthesize` 的轨迹（仅 `eval grade`）。

### 3. 分析失败

**默认：** 打开最新的 `artifacts/grade_results/results_<ts>.html`（或 `.json`），并识别失败的指标 — 参见 *评分失败时如何修复* 下的修复表。

**选择性：** `agents-cli eval analyze`，基于 LLM 的失败聚类；当您有 10+ 个失败的案例并希望按类别分类失败模式时，请优先使用。参见 `references/advanced-commands.md`。

### 4. 优化和代码修复

**默认：** 编辑代理 — 根据失败分析调整提示、工具描述、说明或评估数据集。参见 *评分失败时如何修复* 下的失败 → 修复映射。

**选择性（ADK 项目）：** `agents-cli eval optimize` 运行 ADK GEPA 提示优化针对目标指标（参见 `references/advanced-commands.md`）。适用于提示失败的案例。优化的提示出现在命令输出中；捕获它并将其应用于代理。对于每个迭代的完整轨迹，在您的优化配置文件中将 `print_detailed_results: true` 设置为 `true`。

> **耗时且昂贵。** GEPA 优化会进行许多 LLM 调用，可能需要很长时间。除非用户明确要求提示优化，否则不要运行它。运行时，请首先尽可能手动修复，然后运行一个 **单个** 最终 `eval optimize` — 永远不要循环此命令。

### 运行循环

迭代阶段 2 → 3 → 4 → 2（使用 `synthesize`，每次迭代重新运行阶段 1，然后 `eval grade`）。每次修复后，运行 `agents-cli eval compare <prev_results>.json <new_results>.json` 以确认目标指标有所提高而没有回归其他指标。每个案例在通过之前预期会迭代 5-10+ 次，这是正常的。只有案例通过后，您才应该使用更多评估案例来扩展覆盖范围。

当进行 5+ 次迭代时，维护一个任务列表，列出哪些案例已修复，哪些案例仍然失败，以及您尝试过的修复。这可以防止重复尝试相同的修复。

**保留案例。** 保留一部分案例不参与循环，仅在您认为完成时才对其进行评分 — 否则您无法判断一个适用于您迭代案例的修复是否具有通用性。

### 浪费时间的捷径

识别这些理由并加以反驳 — 它们总是比它们节省的时间更多：

| 短路 | 为什么它失败 |
|------|-------------|
| "我会降低标准让它通过" | 降低标准会隐藏真正的失败。如果代理无法达到标准，请修复代理，而不是移动标准。 |
| "这个评估案例不稳定，我会跳过" | 不稳定的评估揭示了代理中的非确定性。使用 `temperature=0`、基于评分标准的指标或更具体的说明来修复，而不是删除信号。 |
| "我只需要修复评估数据集，不需要修复代理" | 如果您总是调整预期输出，您的代理有行为问题。首先修复说明或工具逻辑。 |
| "我会迭代直到我所有的案例都通过" | 没有留下检测您案例过度拟合的空间。参见 *保留案例* 以上。 |

## 选择正确的指标

根据您想要测量的内容选择内置指标。只有 `multi_turn_task_success`、`multi_turn_trajectory_quality` 和 `multi_turn_tool_use_quality` 接受多轮轨迹；其他所有内置指标都在一轮中评分。当没有内置指标适合时，编写自定义指标（参见 *评估配置 schema* 以下）。

| 目标 | 推荐的内置指标 |
|------|------------------------------|
| **代理是否实现了用户的目标？**（多轮代理的通用情况） | `multi_turn_task_success` |
| **代理的推理路径是否逻辑且高效？** | `multi_turn_trajectory_quality` |
| **跨轮工具/函数调用的质量** | `multi_turn_tool_use_quality` |
| **最终响应质量**（不需要真实参考） | `final_response_quality` |
| **事实基础**（捕获幻觉的声明，例如 RAG 代理） | `hallucination`，或者当案例带有 `context` 字段时为 `grounding` |
| **安全策略合规性** | `safety` |
| **与黄金答案匹配** | `final_response_match`（需要在案例上设置 `reference`） |
| **每个案例不同的通过/失败标准** | 将它们放在案例上作为 `rubric_groups`，并使用管理式评分指标进行评分。参见 `references/dataset_schema.md`（*每个案例的评分标准*）。 |
| **没有内置指标涵盖的特定领域检查** | 编写自定义 `LLMMetric`（LLM 裁判）或 `CodeExecutionMetric`（确定性 Python）。参见 *评估配置 schema* 以下。 |

运行 `agents-cli eval metric list` 查看所有可用内置指标。有关完整指标定义和评分标准详情，请参阅 [代理平台指标文档](https://cloud.google.com/gemini-enterprise-agent-platform/optimize/evaluation/manage-metrics) 和 `references/metrics-guide.md`。

---

## 评分失败时如何修复

完成 `agents-cli eval run` 后，检查最新的 `artifacts/grade_results/results_<timestamp>.json`（或打开 `.html` 文件）以获取每个案例的评分和裁判理由，这是每个修复决策的输入。

| 失败 | 要更改的内容 |
|---------|---------------|
| `multi_turn_task_success` 低 | 代理没有完成用户的任务 — 修复编排、缺少工具调用、过早终止或错误的工具选择 |
| `multi_turn_trajectory_quality` 低 | 代理以低效的方式达到目标或采取错误步骤 — 精炼计划提示、收紧说明顺序或删除冗余工具调用 |
| `multi_turn_tool_use_quality` 低 | 修复工具描述、参数 docstrings 或代理说明以选择工具 |
| `final_response_quality` 低 | 阅读自动生成的评分标准裁决；精炼代理说明以解决最低评分标准（通常是清晰度、完整性或说明遵循） |
| `hallucination` 低 | 严格代理说明以保持在工具输出基础上；验证工具实际返回了代理声称的数据 |
| `safety` 低 | 向说明添加安全护栏；查看评分标准裁决中违反的内容类别 |
| 代理调用错误工具 | 修复工具描述、代理说明或模型工具选择配置（**ADK**：`tool_config`） |
| 代理调用额外工具 | 添加严格的停止说明，或切换到 `multi_turn_tool_use_quality` |

应用修复后，重新运行 `agents-cli eval run` 并使用 `agents-cli eval compare <prev_results>.json <new_results>.json` 确认修复提高了目标指标而没有回归其他指标。

---

## 评估命令

`agents-cli eval <subcommand> --help` 是权威的标志列表；以下示例是常见的调用。

### `eval run`（默认）

在一个命令中运行代理并评分轨迹。

```bash
# 基本：数据集来自 tests/eval/datasets/，结果到 artifacts/grade_results/，
# 指标来自 tests/eval/eval_config.yaml
agents-cli eval run

# 高级：选择数据集、指标和输出目录
agents-cli eval run --dataset tests/eval/datasets/custom.json --metrics final_response_quality,safety --output ./out/
```

### `eval generate`

运行代理并写入磁盘上的轨迹。

默认情况下，在本地运行代理并记录每个评估案例的轨迹。您可以通过传递其 HTTP 端点和应用名称到 `--url` 和 `--app-name` 来从正在运行的代理生成轨迹。

> **ADK 项目。** 内置生成器通过 HTTP 提供代理并驱动它通过 ADK 的 `/apps/...` 和 `/run_sse` 路径 — `--url` / `--app-name` 期望的形状。它启动的内容取决于项目的语言：Python 使用项目的 `fast_api_app.py`（如果存在），否则 `adk api_server`；Go 运行 `go run ...`。其他框架的扩展替换 `eval generate` 为它们自己的生成器，这可能根本不提供 HTTP；`--url` 和 `--app-name` 不再受支持。

```bash
# 基本 — 使用 tests/eval/datasets/，写入到 artifacts/traces/
agents-cli eval generate

# 高级 — 自定义数据集和输出目录
agents-cli eval generate --dataset tests/eval/datasets/custom.json -o ./custom_traces/

# 部署的代理（或您手动启动的代理）
agents-cli eval generate --url https://my-agent.run.app --app-name app

# 活体代理 — 通过 ADK 的 /run_live WebSocket 流每个案例
agents-cli eval generate --mode adk_live
```

#### 评估活体代理

活体代理在 WebSocket 上运行，而不是 `/run_sse`：在 `generate` 或 `run` 中添加 `--mode adk_live`。数据集、轨迹和评分保持不变，音频回复被转录，所以评分为文本。必须已经为之一或连接后会在会话中失败：代理使用 Live 模型（脚手架默认不是），并且在 Vertex 上，其区域在模型上固定，而不是留给 `GOOGLE_CLOUD_LOCATION`。这两者，加上数据集编写规则：`references/live-eval.md`。

### `eval grade`

对轨迹（来自 `eval generate`、`eval dataset synthesize` 或手工编写）与内置或自定义指标进行评分。将带时间戳的 `results_<YYYYMMDD_HHMMSS>.json`（由 `eval compare` 消费）和 `.html`（在浏览器中打开）写入输出目录，并将摘要表打印到控制台。

```bash
# 基本 — 默认：轨迹来自 artifacts/traces/，结果到 artifacts/grade_results/，
# 指标来自 tests/eval/eval_config.yaml 的 metrics_to_run
agents-cli eval grade

# 高级 1 — 评分来自非默认位置（`eval generate --output custom_traces/` 的规范配对）
agents-cli eval grade --traces custom_traces/

# 高级 2：从指定的轨迹文件加载要运行的指标到配置文件（YAML 或 JSON）。
agents-cli eval grade --traces ./artifacts/traces/trace_1.json --config tests/eval/eval_config.yaml

# 高级 3：分发速率，默认每秒 15 个指标计算。当裁判模型或评估服务限制您时降低它，当它们有空间时提高它。
agents-cli eval grade --qps 5
```

参见 *评估配置 schema* 以下面的配置文件格式。

### `eval compare`

比较来自评估运行的两个 `results_*.json` 文件。在修复后运行它，以确认目标指标有所提高而没有回归其他指标。

```bash
agents-cli eval compare baseline.json candidate.json
```

### `eval dataset synthesize`

> **ADK 项目。** 它加载并运行代理通过 ADK，因此在其他框架上不可用。

从您的代理的工具和说明中生成用户场景，让每个场景通过 LLM 支持的用户模拟器播放，并将评分就绪的轨迹写入 `artifacts/traces/`（直接输入到 `eval grade`，跳过 `eval generate`）。调用、标志和兼容的指标：`references/user-simulation.md`。

### 高级命令

`eval analyze`（聚类失败模式）、`eval optimize`（GEPA 提示调整）和 `eval submit` / `eval results`（用于 CI 或大型数据集的云端运行管理）在 `references/advanced-commands.md` 中记录。

---

## 评估数据集格式

`EvaluationDataset` 是一个包含 `eval_cases` 数组的 JSON 文件。案例根据其使用方式有两种形状：

- **推理输入**（您提供给 `eval generate` 的） — 单个用户提示，或多轮用户回合集（用于活体）/ 以用户回合结尾的延续（用于 SSE）。代理运行并产生轨迹。不要为活体推理预先编写代理回复。
- **评分输入**（您提供给 `eval grade` 的） — 包括代理回复和工具调用的完整轨迹。通常由 `eval generate` 或 `eval dataset synthesize` 产生；您不会手工编写这些。

参见 `references/dataset_schema.md` 以获取完整的规范 schema、所有字段类型和常见错误。

### 推理输入格式

支持两种形状。

**(a) 简单单轮提示** — 脚手架 `tests/eval/datasets/basic-dataset.json` 使用。代理从头开始运行。

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

**(b) 通过 `agent_data` 的多轮** — 形状取决于传输：

- **活体 (`--mode adk_live`)**：编写 **仅用户** 回合；代理在一个活体会话中生成每个回复（编写的代理回合被忽略，并会发出警告）。
- **SSE**：延续形式 — 先前的回合作为历史种子，只有尾随的用户回合被回答。

参见 `references/dataset_schema.md`（*多轮/多代理数据集*）以获取 JSON 形状。

### 评分输入格式（轨迹）

一个完整轨迹 — 代理回复加上 `function_call` / `function_response` 部分 — 通常由 `eval generate` / `eval dataset synthesize` 产生（您不会手工编写这些）。作者是 `"user"`、来自 `agents` 映射的代理 ID，或 `"tool"`。参见 `references/dataset_schema.md` 以获取轨迹形状、多代理示例和完整类型参考。

---

## 评估配置 schema

`agents-cli eval run --config <path>`（和 `eval grade --config <path>`）接受一个配置文件，可以是 **YAML**（`.yaml` / `.yml`）或 **JSON**（`.json`）。该文件声明两个部分：

- `metrics_to_run`：本次运行要执行的**指标名称选择列表**。名称匹配时解析为 `custom_metrics` 中的条目，否则解析为同名的内置指标。
- `custom_metrics` — 供此项目使用的**自定义指标定义池**。在此处定义指标**不会**运行它；它也必须出现在 `metrics_to_run` 中（或通过 CLI 的 `--metrics name1,name2` 传递，这等效于覆盖 `metrics_to_run`）。

**最小示例（优先使用 YAML — 人类可读，提示和 Python 无需 JSON 转义）：**

```yaml
metrics_to_run:
  - multi_turn_task_success     # 内置
  - example_llm_metric          # 从下方自定义指标池中选择
  - agent_turn_count            # 从下方自定义指标池中选择

custom_metrics:
  - name: example_llm_metric
    prompt_template: |
      评估代理响应在帮助性和准确性方面的 1-5 分。
      提示：{prompt}
      最终响应：{response}
      完整追踪（用于工具调用和推理上下文）：{agent_data}
      返回 JSON：{"score": <1|2|3|4|5>, "explanation": "<reason>"}

  - name: agent_turn_count
    custom_function: |
      def evaluate(instance):
          turns = (instance.get("agent_data") or {}).get("turns", [])
          return {'score': len(turns)}
```

JSON 也被接受（字段名相同，`prompt_template` 和 `custom_function` 作为转义字符串）— 但**始终优先选择 YAML**用于人类可读的配置。

按字段分发：`custom_function` → Python 指标；`prompt_template` → `LLMMetric`（LLM 作为裁判）；两者都没有，对于内置名称 → 参数化该内置指标（例如 `metric_spec_parameters.rubric_group_key`）。字段引用：`references/metrics-guide.md`。

**代理追踪字段模型。** 对于由 `agents-cli eval generate`（或 `eval dataset synthesize`）生成的数据集，每个评估用例向指标暴露三个标准字段：

- `{prompt}` — 用户消息（或第一个用户回合）。
- `{response}` — 代理的最终文本响应，从最后一个包含文本的事件中提取。在 `custom_function` 回调中这是 `instance['response']`，其形状为 `{"role": "model", "parts": [{"text": "..."}]}`。
- `{agent_data}` — 完整的结构化 `turns`/`events` 追踪，当裁判需要推理工具调用或中间推理时很有用。

`reference`、`context` 和 `rubric_groups` 由您在用例中自行编写：`eval generate` 将它们带到追踪中但从未创造它们，因此 `{reference}` / `{context}` 仅在您编写它们的地方解析。`rubric_groups` 根本不是占位符：管理的评分指标从中读取，而 `custom_function` 看到 `instance['rubric_groups']`。参见 `references/dataset_schema.md`（*每个用例的评分标准*）。

基于代码的指标默认为**本地进程内执行**（无需 GCP 项目或区域，但 `evaluate(instance)` 函数以 CLI 的权限运行）。在指标上设置 `execution: "remote"` 以在 Vertex AI 的 `CodeExecutionMetric` 沙盒中服务器端运行它 — 该路径需要配置的 GCP 项目 + 区域。

---

## 常见陷阱

### 使用基于评分标准的工具评估而不是硬编码的序列

使用严格的序列匹配来评估代理工具使用是脆弱的，因为代理可能以不同的顺序调用辅助工具（如搜索或地理编码）或执行额外的主动步骤。

相反，使用 **`multi_turn_tool_use_quality`** / **`multi_turn_trajectory_quality`**。这些指标自动生成基于内容和基于意图的自适应评分标准，使用 LLM 裁判从语义上评估技术正确性和技术序列逻辑，而不是强制进行僵化的匹配。

### 应用名称必须与目录名称匹配

> **ADK 项目。**

`App` 对象的 `name` 参数**必须**与包含您的代理的目录匹配：

```python
# 正确 - 匹配 "app" 目录
app = App(root_agent=root_agent, name="app")

# 错误 - 导致 "Session not found" 错误
app = App(root_agent=root_agent, name="flight_booking_assistant")
```

### Vertex 评估区域

`eval run`、`eval grade` 和 `eval submit` **默认为 `global` 端点**。它们不会继承清单 `region`（评估服务仅支持区域子集），而 `eval analyze` 仅支持 `global`。通过 `--region <REGION>`（例如数据驻留）为每次运行覆盖这些（例如 `eval run`）：

```
400 FAILED_PRECONDITION: Vertex 评估服务不支持的区域：<region>
```

`eval generate`（不带 `--url` 标志）和 `eval dataset synthesize` 在本地运行您的代理，因此它们尊重代理自己的 `.env` — 特别是 `GOOGLE_CLOUD_LOCATION`，它选择模型端点**当代理使用 Vertex AI** (`GOOGLE_GENAI_USE_VERTEXAI=true`) 时；它在与 `GEMINI_API_KEY`（AI Studio）一起使用时未使用。它们**不**接受 `--region` 并永远不会用清单 `region` 覆盖您的 `.env`；通过编辑 `.env` 更改模型区域 — 或者，对于单个代理来说，更好的做法是在代码中固定它，使用 `Gemini(model=…, client_kwargs={"location": …})`，这比环境变量更优，并允许其他所有内容使用它。对于 `synthesize` 的一个例外：其场景生成步骤是一个**服务器端**的评估调用，在 `GOOGLE_CLOUD_LOCATION`，因此即使代理本身可以在其他地方运行，也要保持这是一个支持评估的区域（默认为 `global`）。

**没有符合您的数据驻留规则的评估区域？** 转而使用**本地自定义指标** — 一个具有 `custom_function`（`execution: local`，默认值）的 `custom_metrics` 条目，在不需要 GCP 区域的情况下进程内评分。您会失去管理的内置指标，但您的 `custom_function` 仍然可以调用 LLM 裁判在合规区域本身 — 因此 LLM 作为裁判的评分仍然可以在任何地方使用。

### `before_agent_callback` 模式（状态初始化）

> **ADK 项目。**

始终使用回调来初始化在您的指令模板中使用的会话状态变量。这可以防止在第一回合上出现 `KeyError` 异常：

```python
async def initialize_state(callback_context: CallbackContext) -> None:
    state = callback_context.state
    if "user_preferences" not in state:
        state["user_preferences"] = {}

root_agent = Agent(
    name="my_agent",
    before_agent_callback=initialize_state,
    instruction="基于偏好：{user_preferences}...",
)
```

### 模型思考模式可能绕过工具

启用“思考”的模型可能会跳过工具调用。通过模型工具选择配置强制使用工具（**ADK**：`tool_config` 与 `mode="ANY"`），或切换到非思考模型以实现可预测的工具调用。

---

## 常见评估失败原因

| 症状 | 原因 | 解决方法 |
|------|------|--------|
| 分数在运行间波动 | 非确定性模型 | 设置 `temperature=0` 或使用基于评分标准的评估并使用多个样本 |
| LLM 裁判在评估中忽略图像/音频 | `get_text_from_content()` 跳过非文本部分 | 使用具有视觉能力的裁判的自定义指标（参见 `references/multimodal-eval.md`） |

---

## 证明您的工作

不要断言评估通过 — 展示证据。具体的输出可以防止错误的信心并尽早捕获问题。

- **运行评估后：** 粘贴分数表格输出，以便用户可以确切看到哪些通过和失败。
- **修复失败后：** 显示您修复的特定用例的修复前/修复后分数，并确认没有其他用例退化。
- **部署前：** 重新运行 `agents-cli eval run` 并显示每个用例的分数，而不仅仅是您修复的那个。`eval run` 无论分数如何都退出 0，因此您粘贴的数字是门禁，而不是退出代码。

---

## 相关技能

- `/google-agents-cli-workflow` — 开发工作流和由规范驱动的构建-评估-部署生命周期
- `/google-agents-cli-adk-code` — ADK API 快速参考，用于编写代理代码（仅限 ADK 项目）
- `/google-agents-cli-scaffold` — 使用 `agents-cli scaffold create` / `scaffold enhance` 创建和增强项目
- `/google-agents-cli-deploy` — 部署目标、CI/CD 管道和生产工作流
- `/google-agents-cli-observability` — Cloud Trace、日志记录和监控，用于调试代理行为
