# 代理评估指南

> **要求：** `agents-cli` (`uv tool install google-agents-cli`) — 如果需要，请先安装 uv：[安装 uv](https://docs.astral.sh/uv/getting-started/installation/index.md)。

> **已搭建项目？** 如果你使用了 `/google-agents-cli-scaffold`，数据集和自定义指标已经在 `tests/eval/`（Python 项目）或 `eval/`（Go 项目）中预搭建好了。为了简化，本指南及其参考文档使用 Python 目录结构；如果你搭建了 Go 代理，请相应调整。
> 你已经拥有 `agents-cli eval run`（串联 `generate` + `grade`）、`tests/eval/datasets/` 和 `tests/eval/eval_config.yaml`。从执行 `eval run` 开始，然后进行迭代。

## 参考文件

| 文件 | 内容 |
|------|----------|
| `references/dataset_schema.md` | 标准评估数据集 schema — 所有字段类型、单轮/多轮/多代理的 JSON 示例、常见错误 |
| `references/metrics-guide.md` | 完整指标参考 — 所有内置指标、匹配类型、自定义指标、裁判模型配置 |
| `references/user-simulation.md` | 动态对话测试 — `eval dataset synthesize` 标志、场景是什么、兼容的指标 |
| `references/builtin-tools-eval.md` | google_search 和模型内部工具 — 轨迹行为、指标兼容性 |
| `references/advanced-commands.md` | 选择性命令：`eval analyze`、`eval optimize`、`eval submit` / `eval results` |
| `references/multimodal-eval.md` | 多模态输入 — 评估数据集 schema、内置指标限制、自定义评估器模式 |
| `references/live-eval.md` | 实时和语音代理 — `--mode adk_live`、评估内容、仅用户编写的回合、Live 模型和区域陷阱 |

---

## 质量飞轮

提高代理质量是一个迭代的过程。下面的四个阶段描述了这个循环。每个阶段都有一个默认路径（你，编码代理，直接执行工作）和一个选择性 CLI 命令，该命令委托给代理平台评估服务以获得更好的质量和规模。

### 1. 准备数据

**默认：** 使用或编辑预搭建的 `tests/eval/datasets/basic-dataset.json` 来定义单轮评估输入。从 1-2 个案例开始。

**选择性（ADK 项目）：** `agents-cli eval dataset synthesize`：当你缺乏数据时，使用用户模拟生成多轮数据集；其输出已经包含轨迹，所以阶段 2 简化为 `agents-cli eval grade`。参见 *评估命令* 和 `references/user-simulation.md`。

### 2. 运行评估（始终运行）

**默认：** `agents-cli eval run` 运行代理在数据集上，并评估轨迹，将 `results_<ts>.{json,html}` 写入 `artifacts/grade_results/`。

**解耦形式：** `eval generate` 然后 `eval grade`，用于自定义轨迹位置、重新评估而不重新运行代理，或来自 `synthesize` 的轨迹（`eval grade` 单独运行）。

### 3. 分析失败

**默认：** 打开最新的 `artifacts/grade_results/results_<ts>.html`（或 `.json`），并识别失败的指标 — 参见 *分数失败时如何修复* 下面的修复表。

**选择性：** `agents-cli eval analyze`，基于 LLM 的失败聚类；当你有 10+ 个失败案例并希望按类别分类失败模式时，优先使用。参见 `references/advanced-commands.md`。

### 4. 优化和代码修复

**默认：** 编辑代理 — 根据失败分析调整提示、工具描述、指令或评估数据集。参见 *分数失败时如何修复* 下面的失败 → 修复映射。

**选择性（ADK 项目）：** `agents-cli eval optimize` 运行 ADK GEPA 提示优化针对目标指标（参见 `references/advanced-commands.md`）。适用于仅提示失败的案例。优化的提示出现在命令输出中；捕获它并将其应用于代理。对于每个迭代的完整轨迹，在优化配置文件中将 `print_detailed_results: true` 设置为 `true`。

> **耗时且昂贵。** GEPA 优化会进行大量 LLM 调用，可能需要很长时间。除非用户明确要求提示优化，否则不要运行它。当你运行它时，首先尽可能手动修复，然后运行一个 **单个** 最终 `eval optimize` — 永远不要循环此命令。

### 运行循环

迭代阶段 2 → 3 → 4 → 2（使用 `synthesize`，每次迭代重新运行阶段 1，然后 `eval grade`）。每次修复后，运行 `agents-cli eval compare <prev_results>.json <new_results>.json` 以确认目标指标有所提高而没有回归其他指标。每个案例在通过之前预期会迭代 5-10+ 次，这是正常的。只有案例通过后，你才应该使用更多评估案例扩展覆盖范围。

当你进行 5+ 次迭代时，维护一个任务列表，列出哪些案例已修复，哪些案例仍然失败，以及你尝试过的修复方法。这可以防止重复尝试相同的修复。

**保留案例。** 保留一部分案例不参与循环，并在你认为完成时才评估它们 — 否则你无法判断一个修复是否具有通用性，而只是针对你迭代过的案例进行了适配。

### 浪费时间的快捷方式

识别这些理由并加以反驳 — 它们总是比它们节省的时间更多：

| 快捷方式 | 为什么它失败 |
|----------|-------------|
| "我会降低标准让它通过" | 降低标准会隐藏真正的失败。如果代理无法达到标准，请修复代理，而不是移动标准。 |
| "这个评估案例不稳定，我会跳过" | 不稳定的评估揭示了代理中的非确定性。使用 `temperature=0`、基于评分标准的指标或更具体的指令来修复，而不是删除信号。 |
| "我只需要修复评估数据集，不需要修复代理" | 如果你总是调整预期输出，你的代理有行为问题。首先修复指令或工具逻辑。 |
| "我会迭代直到我所有的案例都通过" | 没有留下可以检测到对自身案例过拟合的东西。参见 *保留案例* 以上。 |

## 选择正确的指标

根据你想测量的内容选择内置指标。只有 `multi_turn_task_success`、`multi_turn_trajectory_quality` 和 `multi_turn_tool_use_quality` 接受多轮轨迹；其他所有内置指标都在一轮中运行。当没有内置指标适用时，编写自定义指标（参见 *评估配置 schema* 以下）。

| 目标 | 推荐的内置指标 |
|------|------------------------------|
| **代理是否实现了用户的目标？**（多轮代理的通用捕获） | `multi_turn_task_success` |
| **代理的推理路径是否逻辑且高效？** | `multi_turn_trajectory_quality` |
| **跨轮工具/函数调用的质量** | `multi_turn_tool_use_quality` |
| **最终响应质量**（不需要真实参考） | `final_response_quality` |
| **事实基础**（捕获幻觉的声明，例如 RAG 代理） | `hallucination`，或者当案例带有 `context` 字段时 `grounding` |
| **安全策略合规性** | `safety` |
| **与黄金答案匹配** | `final_response_match`（需要在案例上设置 `reference`） |
| **每个案例不同的通过/失败标准** | 将它们放在案例上作为 `rubric_groups`，并使用管理式评分标准指标进行评估。参见 `references/dataset_schema.md`（*每个案例的评分标准*）。 |
| **没有内置指标涵盖的特定领域检查** | 编写自定义 `LLMMetric`（LLM 作为裁判）或 `CodeExecutionMetric`（确定性 Python）。参见 *评估配置 schema* 以下。 |

运行 `agents-cli eval metric list` 查看所有可用内置指标。有关完整指标定义和评分标准详情，请参阅 [代理平台指标文档](https://cloud.google.com/gemini-enterprise-agent-platform/optimize/evaluation/manage-metrics) 和 `references/metrics-guide.md`。

---

## 分数失败时如何修复

在 `agents-cli eval run` 完成后，检查最新的 `artifacts/grade_results/results_<timestamp>.json`（或打开 `.html` 文件）以获取每个案例的分数和裁判理由，这是每个修复决策的输入。

| 失败 | 要更改的内容 |
|---------|---------------|
| `multi_turn_task_success` 低 | 代理没有完成用户的目標 — 修复编排、缺少工具调用、过早终止或错误的工具选择 |
| `multi_turn_trajectory_quality` 低 | 代理以低效的方式达到目标或采取错误步骤 — 细化规划提示、收紧指令顺序或移除冗余工具调用 |
| `multi_turn_tool_use_quality` 低 | 修复工具描述、参数 docstrings 或代理指令以进行工具选择 |
| `final_response_quality` 低 | 阅读自动生成的评分标准裁决；细化代理指令以解决最差的评分标准（通常是清晰度、完整性或指令遵循） |
| `hallucination` 低 | 严格代理指令以保持在工具输出基础上；验证工具实际上返回了代理声称的数据 |
| `safety` 低 | 在指令中添加安全护栏；查看评分标准裁决中违反的内容类别 |
| 代理调用错误工具 | 修复工具描述、代理指令或模型的选择工具配置（**ADK**：`tool_config`） |
| 代理调用额外工具 | 添加严格的停止指令，或切换到 `multi_turn_tool_use_quality` |

应用修复后，重新运行 `agents-cli eval run` 并使用 `agents-cli eval compare <prev_results>.json <new_results>.json` 确认修复提高了目标指标而没有回归其他指标。

---

## 评估命令

`agents-cli eval <subcommand> --help` 是权威的标志列表；以下示例是常见的调用。

### `eval run`（默认）

在一个命令中运行代理并评估轨迹。

```bash
# 基本：数据集来自 tests/eval/datasets/，结果到 artifacts/grade_results/，
# 指标来自 tests/eval/eval_config.yaml
agents-cli eval run

# 高级：选择数据集、指标和输出目录
agents-cli eval run --dataset tests/eval/datasets/custom.json --metrics final_response_quality,safety --output ./out/
```

### `eval generate`

运行代理在评估数据集上并写入轨迹到磁盘。

默认情况下，在本地运行代理并记录每个评估案例的轨迹。你可以通过传递其 HTTP 端点和应用名称到 `--url` 和 `--app-name` 从已经运行的代理生成轨迹。

> **ADK 项目。** 内置生成器通过 HTTP 代理并驱动它通过 ADK 的 `/apps/...` 和 `/run_sse` 路径 — `--url` / `--app-name` 期望的形状相同。它启动的内容取决于项目的语言：Python 使用项目的 `fast_api_app.py`（如果存在），否则 `adk api_server`；Go 运行 `go run ...`。其他框架的扩展替换 `eval generate` 为它们自己的生成器，这可能根本不提供 HTTP 服务；`--url` 和 `--app-name` 在这种情况下不受支持。

```bash
# 基本 — 使用 tests/eval/datasets/，写入到 artifacts/traces/
agents-cli eval generate

# 高级 — 自定义数据集和输出目录
agents-cli eval generate --dataset tests/eval/datasets/custom.json -o ./custom_traces/

# 对一个已部署的代理（或你手动启动的）
agents-cli eval generate --url https://my-agent.run.app --app-name app

# Live 代理 — 通过 ADK 的 /run_live WebSocket 流式传输每个案例
agents-cli eval generate --mode adk_live
```

#### 评估 Live 代理

Live 代理在 WebSocket 上运行，而不是 `/run_sse`：在 `generate` 或 `run` 中添加 `--mode adk_live`。数据集、轨迹和评分保持不变，音频回复将被转录，所以转录内容会被评分。必须满足两件事，套接字连接后才会在中途失败：代理使用 Live 模型（模板默认不是），并且在 Vertex 上，其区域被固定在模型上，而不是留给 `GOOGLE_CLOUD_LOCATION`。这两点加上数据集作者规则：`references/live-eval.md`。

### `eval grade`

对来自 `eval generate`、`eval dataset synthesize` 或手工编写的轨迹进行评分，针对内置或自定义指标。将带时间戳的 `results_<YYYYMMDD_HHMMSS>.json`（由 `eval compare` 消费）和 `.html`（在浏览器中打开）写入输出目录，并将摘要表打印到控制台。

```bash
# 基本 — 默认：轨迹来自 artifacts/traces/，结果到 artifacts/grade_results/，
# 指标来自 tests/eval/eval_config.yaml 的 metrics_to_run
agents-cli eval grade

# 高级 1 — 评分来自非默认位置（`eval generate --output custom_traces/` 的规范配对）
agents-cli eval grade --traces custom_traces/

# 高级 2：从指定的轨迹文件加载要运行的指标到配置文件（YAML 或 JSON）。
agents-cli eval grade --traces ./artifacts/traces/trace_1.json --config tests/eval/eval_config.yaml

# 高级 3：分发率，默认每秒 15 个指标计算。当你被裁判模型或评估服务限制时降低它，当它们有空间时提高它。
agents-cli eval grade --qps 5
```

参见 *评估配置 schema* 以下面的配置文件格式。

### `eval compare`

比较来自评估运行的两个 `results_*.json` 文件。在修复后运行它，以确认目标指标有所提高而没有回归其他指标。

```bash
agents-cli eval compare baseline.json candidate.json
```

### `eval dataset synthesize`

> **ADK 项目。** 它加载并运行代理通过 ADK，所以在其他框架上不可用。

从你的代理的工具和指令生成用户场景，每个场景都通过 LLM 支持的用户模拟器播放，并将评分就绪的轨迹写入 `artifacts/traces/`（直接输入到 `eval grade`，跳过 `eval generate`）。调用、标志和兼容的指标：`references/user-simulation.md`。

### 高级命令

`eval analyze`（聚类失败模式）、`eval optimize`（GEPA 提示调整）和 `eval submit` / `eval results`（用于 CI 或大型数据集的云端管理运行）在 `references/advanced-commands.md` 中记录。

---

## 评估数据集格式

一个 `EvaluationDataset` 是一个包含 `eval_cases` 数组的 JSON 文件。案例有两种形状，取决于它们如何使用：

- **推理输入**（你给 `eval generate` 的内容）— 单个用户提示，或多轮 **用户回合**（用于 Live）/ 以用户回合结尾的延续（用于 SSE）。代理运行并产生轨迹。不要为 Live 推理预先编写代理回复。
- **评分输入**（你给 `eval grade` 的内容）— 包括代理回复和工具调用的完整轨迹。通常由 `eval generate` 或 `eval dataset synthesize` 产生；你不会手工编写这些。

参见 `references/dataset_schema.md` 以获取完整的规范 schema、所有字段类型和常见错误。

### 推理输入格式

支持两种形状。

**(a) 简单单轮提示** — 模板 `tests/eval/datasets/basic-dataset.json` 使用。代理从头开始运行。

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

- **Live (`--mode adk_live`):** 编写 **仅用户** 回合；代理在一个 Live 会话中生成每个回复（编写的代理回合被忽略，并会显示警告）。
- **SSE:** 延续形式 — 先前的回合作为历史记录种子，只回答尾随的用户回合。

参见 `references/dataset_schema.md`（*多轮 / 多代理数据集*）以获取 JSON 形状。

### 评分输入格式（轨迹）

一个完整轨迹 — 代理回复加上 `function_call` / `function_response` 部分 — 通常由 `eval generate` / `eval dataset synthesize` 产生（你不会手工编写这些）。作者为 `"user"`、来自 `agents` 映射的代理 ID，或 `"tool"`。参见 `references/dataset_schema.md` 以获取轨迹形状、多代理示例和完整类型参考。

---

## 评估配置 schema

`agents-cli eval run --config <path>`（和 `eval grade --config <path>`）接受一个单一的配置文件，可以是 **YAML**（`.yaml` / `.yml`）或 **JSON**（`.json`）。该文件声明两部分：

- `metrics_to_run`: 本次运行要执行的 **指标选择列表**。名称解析为匹配的 `custom_metrics` 条目时为 `custom_metrics`，否则为同名的内置指标。
- `custom_metrics` — 一个 **自定义指标定义池**，该项目可用。在此处定义指标不会运行它；它也必须出现在 `metrics_to_run` 中（或通过 CLI 的 `--metrics name1,name2` 覆盖 `metrics_to_run`，这等效于为该调用覆盖 `metrics_to_run`）。

**最小示例（优先使用 YAML — 人类可读，提示和 Python 无需转义）：**

```yaml
metrics_to_run:
  - multi_turn_task_success     # 内置
  - example_llm_metric          # 从 custom_metrics 池中选择
  - agent_turn_count            # 从 custom_metrics 池中选择

custom_metrics:
  - name: example_llm_metric
    prompt_template: |
      评估代理回复在帮助性和准确性方面的评分 1-5。
      提示：{prompt}
      最终回复：{response}
      完整轨迹（用于工具调用和推理上下文）：{agent_data}
      返回 JSON：{"score": <1|2|3|4|5>, "explanation": "<reason>"}

  - name: agent_turn_count
    custom_function: |
      def evaluate(instance):
          turns = (instance.get("agent_data") or {}).get("turns", [])
          return {'score': len(turns)}
```

JSON 也被接受（相同的字段名，`prompt_template` 和 `custom_function` 作为转义字符串） — 但 **始终优先使用 YAML** 以便人类可读的配置。

分发方式：`custom_function` → Python 指标；`prompt_template` → `LLMMetric`（LLM 作为裁判）；两者都不是，在内置名称上 → 参数化该内置指标（例如 `metric_spec_parameters.rubric_group_key`）。字段参考：`references/metrics-guide.md`。

**代理轨迹字段模型。** 对于由 `agents-cli eval generate`（或 `eval dataset synthesize`）产生的数据集，每个评估案例向指标暴露三个标准字段：

- `{prompt}` — 用户消息（或第一个用户回合）。
- `{response}` — 代理的最终文本回复，从最后一个文本事件中提取。在 `custom_function` 回调中，这是 `instance['response']`，形状为 `{"role": "model", "parts": [{"text": "..."}]}`。
- `{agent_data}` — 完整的 `turns`/`events` 轨迹，当裁判需要推理工具调用或中间推理时很有用。

`reference`、`context` 和 `rubric_groups` 是你在案例上可以编写的：`eval generate` 将它们带到轨迹上，但从不发明它们，所以 `{reference}` / `{context}` 只在你写了它们的地方解析。`rubric_groups` 根本不是占位符：管理式评分标准指标读取它，而 `custom_function` 看到 `instance['rubric_groups']`。参见 `references/dataset_schema.md`（*每个案例的评分标准*）。

基于代码的指标默认为 **本地进程内执行**（不需要 GCP 项目或区域，但 `evaluate(instance)` 函数以 CLI 的权限运行）。在指标上设置 `execution: "remote"` 以在 Vertex AI 的 `CodeExecutionMetric` 沙盒中服务器端运行它 — 那条路径需要配置的 GCP 项目 + 区域。
