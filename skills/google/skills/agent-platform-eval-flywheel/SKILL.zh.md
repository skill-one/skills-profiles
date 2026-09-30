---
name: agent-platform-eval-flywheel
description: 使用Eval Quality Flywheel方法在Google Cloud上测量和改进AI模型和代理的质量。在生成合成用户场景、评估代理或模型、构建评估数据集、选择或编写评估指标、分析失败、比较修复前后的结果，或需要Agent Platform评估方法指导时（包括数据集模式、LLM作为裁判的评分和常见失败原因）时使用。进行微调时，请使用agent-platform-tuning。进行通用生产部署时，请使用agent-platform-deploy。
---

# Agent Platform Eval Flywheel Skill

使用 Agent Platform GenAI Evaluation SDK (`google.genai` / `agentplatform`) 帮助用户评估和迭代改进 GenAI 模型和代理。

## 何时使用此技能

- 使用 Agent Platform GenAI Evaluation SDK (`client.evals.evaluate()`) 评估 GenAI 代理或模型。
- 从会话跟踪、pandas DataFrame 或合成生成创建评估数据集。
- 选择、配置或编写自定义评估指标。
- 分析评分标准判定、损失模式和聚类失败。
- 根据评估结果提出具体的代码/提示改进建议。
- 评估在 Agent Platform **端点**（BYOM）上托管的模型或通过 ID 评估 **模型即服务 (MaaS)** 模型——如果需要，首先部署该模型。对于此情况，请遵循 [references/deployment.md](references/deployment.md) 并使用 `endpoint_evaluation.py` / `maas_evaluation.py` 脚本。

## 安全与确认级别（关键）

在代表用户执行任何命令或脚本之前，您必须根据请求的操作遵守以下安全级别：

1.  **级别 R：只读** (`inspect_results.py`, `compare_results.py`, `validate_dataset.py`, `parse_adk_traces.py`, `render_html_report.py`)
    *   **规则**：不需要确认。您可以立即执行这些辅助脚本来检查数据、验证模式、解析跟踪或比较评估结果。
2.  **级别 M：只读且包含计算成本** (`client.evals.run_inference`, `client.evals.evaluate`, `client.evals.generate_conversation_scenarios`, `client.evals.generate_loss_clusters`)
    *   **规则**：这些操作会调用 LLM 或远程评估服务，消耗计算资源并产生费用。这需要与“是”/“否”选项进行**交互式确认**。
    *   **每次评估运行的确认**：每次评估、重新评估、指标更新、参数更改或合成场景生成都需要其自身的干跑预览和交互式确认。切勿在未提供新的确认预览并获得用户批准的情况下执行第二次评估、比较或修改后的评估。
    *   **同回合限制**：不要在显示确认提示的同回合内运行评估。在提问后结束您的回合，等待用户的回复；只有在明确“是”/批准后才能执行。在用户可以回答之前打印预览并调用工具不算获得确认。
    *   **禁止远程评估的预执行**：**绝对不要**在用户确认之前执行 `client.evals.evaluate()`、`client.evals.run_inference()`、`client.evals.generate_conversation_scenarios()` 或运行调用这些远程操作的任何脚本。在初始回合中，您可以准备本地数据结构并编写脚本，但在运行任何远程评估或场景生成调用之前，您必须提供干跑预览卡并获得明确的用户确认。
    *   **获得批准后立即执行**：一旦用户明确批准（例如，“是”、“已批准”、“继续”、“进行”），请直接通过 `run_command` 执行预览的评估脚本并报告结果。不要在执行批准的操作之前结束回合。

## 设置

脚本需要 `vertexai`（来自 `google-cloud-aiplatform[evaluation]`）、`google-genai`、`pandas` 和 `requests`。**不要**创建虚拟环境——它开始为空并隐藏环境已经提供的包，强制进行冗余安装。探测并仅安装缺失的部分：

```bash
python3 -c "import vertexai, google.genai, pandas, requests" \
  || pip install 'google-cloud-aiplatform[evaluation]>=1.163.0' 'google-genai>=1.0.0'
```

版本规范必须保持引号：未加引号，bash 将 `>=1.154.0` 读取为重定向，并静默写入一个空文件而不是限制安装。

需要 `GOOGLE_CLOUD_PROJECT` 和 `GOOGLE_CLOUD_LOCATION`。

-   **保留用户项目和位置**：始终优先考虑用户明确提供的项目和位置（例如 `project='<PROJECT_NUMBER>'`、`location='us-central1'`）。除非用户明确请求“全局”，否则**绝对不要**更改或覆盖用户请求的位置为“全局”。
-   **缺失参数**：如果用户请求中省略了项目或位置，您必须在响应中暂停并要求用户提供缺失的位置/项目，然后再准备或运行评估。

### 正确的 SDK 入口点

```python
import agentplatform
client = agentplatform.Client(project=PROJECT, location=LOCATION)

client.evals.run_inference(model=..., src=...)
client.evals.evaluate(dataset=..., metrics=...)
client.evals.generate_conversation_scenarios(...)
```

两个看似合理但实际不正确的导入：

-   `from agentplatform.types import evals` -- `ModuleNotFoundError`。`types` 是一个模块，不是一个包；应使用 `from agentplatform import types`。
-   `from vertexai.evaluation import PointwiseMetric, EvalTask` -- 已弃用的 SDK。它的类接受不同的参数（`PointwiseMetric` 没有参数 `system_instruction`），因此针对它的代码会因 `TypeError` 而失败，而不是导入错误。在整个代码中始终使用 `agentplatform`。

## 质量飞轮

五个阶段，在第一次通过时按顺序运行，然后循环 2 → 5 直到质量目标达成。

### 浪费时间的捷径

| 短切                             | 为什么它失败                         |
| -------------------------------- | ------------------------------------ |
| "我会将指标阈值调低，这样就能通过。" | 隐藏了真正的失败。修复代理，而不是 |
:                                  : 横杆。                         :
| "这个案例不稳定，我会跳过它。"  | 不稳定性揭示了代理中的非确定性。     |
:                                      : 用 `temperature=0` 或更严格的指令修复。            :
| "我只需要修复评估数据集，不需要修复代理。"             | 如果预期输出持续移动，代理有行为问题。        :
| "我可以从跟踪中判断它工作正常，跳过阶段 3。"                     | 自我评分无法泛化。     : 始终运行 `evaluate()` 并阅读     :
:                                      : 分数。                              :
| "一次迭代就足够了。"           | 期望 5–10+ 次迭代。过早停止会遗漏    |
:                                      : 其他指标上的回归。                  :

### 1. 准备数据

生成一个 `EvaluationDataset`。有三个输入形状，选择与用户已有的数据匹配的一个：

-   **`EvalCase` 列表（单回合或多回合）：**

    ```python
    from agentplatform import types
    from google.genai import types as genai_types

    # prompt/reference/response 值是 Content，不是 str。UserContent 和
    # ModelContent 包装一个普通字符串并设置正确的角色。
    dataset = types.EvaluationDataset(eval_cases=[
        types.EvalCase(
            prompt=genai_types.UserContent("What is 2+2?"),
            responses=[types.ResponseCandidate(
                response=genai_types.ModelContent("4"))],
            reference=types.ResponseCandidate(
                response=genai_types.ModelContent("4")),
        ),
        # 对于多回合代理跟踪，设置 agent_data 而不是 prompt/responses。
    ])
    ```

    多回合代理跟踪将每个对话包装在 `AgentData` → `ConversationTurn` → `AgentEvent` 中。有关完整类型层次结构的详细信息，请参阅
    [references/dataset_schema.md](references/dataset_schema.md)。

-   **Pandas DataFrame（表格源——CSV、BigQuery、电子表格）：**

    ```python
    import pandas as pd
    from agentplatform import types

    df = pd.DataFrame({
        "prompt":    ["What is 2+2?", "Capital of France?"],
        "response":  ["4",            "Paris"],
        "reference": ["4",            "Paris"],
    })
    dataset = types.EvaluationDataset(eval_dataset_df=df)
    ```

    列名必须与所选指标期望的字段匹配（有关每个指标的详细要求表，请参阅
    [references/dataset_schema.md](references/dataset_schema.md)）。

-   **冷启动（没有任何数据）：** 在服务器端使用 `client.evals.generate_conversation_scenarios(agent=..., config=...)` 合成场景——参数是 `agent` 或 `agent_info`，而不是 `agents`，并且 `config` 是必需的。配置类是 `types.evals.UserScenarioGenerationConfig`，不是 `types.UserScenarioGenerationConfig`。设置其 `user_scenario_count`（1-100）：它默认为 None，客户端接受，服务器会拒绝调用并返回 `400 INVALID_ARGUMENT`。`count` 是一个单独的字段，不能替代它。阶段 2 会执行这些场景。
    *   **关键 - 未明确请求**：当被要求合成场景时，如果请求省略了必需参数（例如 `location`、`environment_data`、`simulation_instruction` 或 `model_name`），**绝对不要**假设默认值或猜测值。您必须在第一回合中暂停，并明确要求用户提供缺失的信息（例如，“请提供缺失的模拟指令、环境数据、模型名称和位置”）。只有在用户提供后，才能进行干跑预览。

-   **托管代理（Gemini Agents API）：** 使用 [Managed Agents API](https://docs.cloud.google.com/gemini-enterprise-agent-platform/build/managed-agents) 评估使用该 API 创建的代理。使用 `generate_conversation_scenarios` 从代理配置创建测试场景，使用 `run_inference` 执行代理，使用 `evaluate` 对跟踪进行评分。这些函数现在接受托管代理和交互 ID 作为输入。您还可以使用 `InteractionsDataSource` 评估通过交互 API 记录的现有交互。有关完整代码模式的详细信息，请参阅
    [references/sdk_patterns.md](references/sdk_patterns.md) 模式 8。

对于 ADK 会话转储，请使用 `scripts/parse_adk_traces.py` 而不是手动编写转换。

### 2. 运行推理

填充数据集中的响应/跟踪。**如果跟踪已经完整（例如，生产日志或重播），则跳过此阶段**。

```python
# 代理评估——传递包装用户 ADK 代理/应用的调用函数。
client.evals.run_inference(model=agent_callable, src=dataset)

# 模型评估——直接传递模型 ID。
client.evals.run_inference(model="gemini-2.5-flash", src=dataset)

# 合成场景——让模拟器驱动。
client.evals.run_inference(
    model=agent_callable,
    src=dataset,
    user_simulator_config=UserSimulatorConfig(max_turn=10),
)

# DataFrame 也可以作为 src=——不需要 EvalCase 包装。
client.evals.run_inference(model="gemini-2.5-flash", src=df)

# 托管代理——传递代理资源名称。
AGENT_RESOURCE = f"projects/{PROJECT_ID}/locations/global/agents/{AGENT_ID}"
client.evals.run_inference(
    agent=AGENT_RESOURCE,
    src=scenarios,
    config={"user_simulator_config": {"max_turn": 3}},
)
```

### 3. 评分（始终运行）

```python
result = client.evals.evaluate(dataset=dataset, metrics=[...])
result.show()  # 交互式 HTML 报告，包含分数、评分标准和跟踪。
```

**根据您想衡量什么选择指标。** 完整目录在
[references/metric_registry.md](references/metric_registry.md)。

**如果用户指定了指标，请直接使用它。** 表格下方的每个标识符（`general_quality`、`text_quality`、`instruction_following`、`hallucination`、`grounding`、`safety`、`multi_turn_*`、`final_response_*`、`tool_use_quality`）都是 `types.RubricMetric.<UPPERCASE_NAME>` 访问器——直接将其传递到 `metrics=[types.RubricMetric.GENERAL_QUALITY, ...]`。不要为这里出现的名称构建自定义 `LLMMetric`，也不要使用 `vertexai.evaluation.EvalTask` / `PointwiseMetric` / `MetricPromptTemplateExamples` —— 该 SDK 已被弃用（见设置）。

**代理指标（多回合、自适应评分标准）**——从代理评估开始。

目标                                          | 指标
--------------------------------------------- | -------------------------------
代理是否实现了用户的目標？        | `multi_turn_task_success`
推理路径是否逻辑且高效？ | `multi_turn_trajectory_quality`
跨回合的工具有效性    | `multi_turn_tool_use_quality`
整体对话质量                | `multi_turn_general_quality`
最终响应质量（无需参考）  | `final_response_quality`
最终响应与黄金参考的匹配         | `final_response_match`
单回合工具使用                          | `tool_use_quality`

**通用质量指标（单回合、自适应评分标准）**——用于模型评估。

目标                                                  | 指标
----------------------------------------------------- | -----------------------
整体响应质量（推荐起始点） | `general_quality`
语言质量（流利度、连贯性、语法）      | `text_quality`
遵守特定约束/指令      | `instruction_following`

**静态评分标准指标（固定标准）** —— 与上述指标一起应用。

目标                                              | 指标
------------------------------------------------- | ---------------
捕获幻觉陈述（RAG、事实性答案）  | `hallucination`
事实性/一致性相对于提供的环境 | `grounding`
安全策略合规                          | `safety`

**没有内置覆盖的特定领域检查：** 编写自定义指标。

-   **预定义：** `types.RubricMetric.<NAME>` — 服务器端 AutoRater，不需要裁判模型。
-   **自定义 LLM 作为裁判：** `types.LLMMetric` 使用 `prompt_template` 或 `types.MetricPromptBuilder` 用于结构化评分标准。始终设置 `judge_model`；它默认为 `None`，否则每个案例都会因 `400 INVALID_ARGUMENT: Error parsing JSON` 而失败。
    *   **裁判模型选择**：如果用户指定了裁判模型（例如 `gemini-2.5-pro`），请使用它。如果用户省略了裁判模型或表示没有信息/偏好，请在干跑预览卡中默认使用 `gemini-2.5-flash` 作为裁判模型并请求确认以运行评估。当用户未指定裁判模型时，**绝对不要**停止或拒绝评估。
-   **自定义代码：** `types.CodeExecutionMetric` 使用包含 `def evaluate(instance: dict)` 的 `custom_function` 字符串进行远程沙盒执行；或 `types.Metric` 使用 `custom_function=<callable>` 进行本地执行。

**始终持久化结果**，以便阶段 4 和 5 可以读取它。保存 JSON（机器可读、可比较）和 HTML（人类可读、可链接）：

```python
import datetime
from pathlib import Path

from agentplatform._genai import _evals_visualization

out_dir = Path("artifacts/grade_results")
out_dir.mkdir(parents=True, exist_ok=True)
ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

# fallback=str, or a DataFrame-backed dataset raises PydanticSerializationError。
result_json = result.model_dump_json(fallback=str)
(out_dir / f"results_{ts}.json").write_text(result_json)

html = _evals_visualization.get_evaluation_html(result_json)
(out_dir / f"results_{ts}.html").write_text(str(html))
```

或者事后：`scripts/render_html_report.py --type evaluation` 或
`scripts/inspect_results.py --save-html`。

### 4. 分析失败

读取 `summary_metrics` 和 `eval_case_results` — 绝不编造分数。使用
`scripts/inspect_results.py --failing-only` 来筛选失败项。

对于每个失败的指标，参见
[references/failure_patterns.md](references/failure_patterns.md) 进行更深入的诊断。紧凑映射：

| 失败指标                      | 需要更改的内容                         |
| ---------------------------- | -------------------------------------- |
| `multi_turn_task_success` 低       | 代理没有完成目标 —  |
:                               : 修复编排、缺失工具调用、 :
:                               : 提前终止、错误工具      :
:                               : 选择。                             :
| `multi_turn_trajectory_quality` 低 | 代理低效地达到目标 — 优化规划        :
:                               : 提示，移除冗余工具调用。  :
| `multi_turn_tool_use_quality` 低   | 修复工具描述、参数       |
:                               : 文档字符串，或代理指令用于  :
:                               : 工具选择。                        :
| `final_response_quality` 低        | 读取自动生成的评分标准；   |
:                               : 优化指令以解决最差的评分标准。               :
| `final_response_match` 低          | 代理的最终答案与黄金参考不匹配 —  |
:                               : 调整响应格式或更新参考。        :
| `hallucination` 低                 | 优化指令以保持基于工具输出  |
:                               : 验证工具实际上返回了声称的数据。    :
| `grounding` 低                     | 响应与提供的上下文矛盾 —  |
:                               : 添加明确的 "仅从上下文中引用" 指令。                 :
| `safety` 低                        | 添加安全护栏；审查评分标准中  |
:                               : 违反的内容类别。                        :
| `general_quality` / `text_quality`  | 调整系统指令措辞；模型的 |
:低                                 : 默认措辞对任务过于通用。                  :
| `instruction_following` 低         | 代理忽略约束 —    |
:                               : 在系统指令中重申它们或使用更严格的措辞。               :
| Agent calls wrong tools             | 修复工具描述、代理       |
:                               : 指令或 `tool_config`。        :
| Agent calls extra tools             | 添加明确的停止指令，或     |
:                               : 切换到                              :
:                               : `multi_turn_tool_use_quality` 以在评分标准中暴露额外的调用。 :

**对于同一指标 10+ 次失败**，使用 **错误分析服务** 将失败聚类为主题（L1/L2 分类）而不是读取每个跟踪：

```python
# 仅支持 multi_turn_task_success 和 multi_turn_tool_use_quality。
# 服务在全局区域运行。
analysis_client = agentplatform.Client(project="PROJECT_ID", location="global")
response = analysis_client.evals.generate_loss_clusters(
    eval_result=result,
    metric="multi_turn_task_success",
    config={"max_top_cluster_count": 5},
)
for r in response.results:
    for cluster in r.clusters:
        print(
            f"[{cluster.taxonomy_entry.l1_category}/"
            f"{cluster.taxonomy_entry.l2_category}] "
            f"{cluster.item_count} cases — {cluster.taxonomy_entry.description}"
        )
```

保存 `response.model_dump_json()` 并使用 `scripts/render_html_report.py
--type loss-analysis` 进行渲染。

### 5. 优化和迭代

针对失败的指标应用修复。重新运行阶段 3。使用
`scripts/compare_results.py --baseline <prev> --candidate <new>` 比较以确认目标改进 AND 没有其他指标退化。

跨迭代跟踪进度：

迭代 | 指标 A | 指标 B | 所做的更改
----- | ------ | ------ | ----------------------
基准  | 0.62     | 0.55     | —
v2        | 0.78     | 0.68     | 添加 grounding 提示
v3        | 0.81     | 0.72     | 修复工具选择

预期每个失败案例 5–10+ 次迭代。只有案例通过后，你才能使用更多评估案例扩展覆盖范围。

## 证明你的工作

不要声称你没有从实际的 `result` 对象中读取的评估结果。

-   运行评估后，打印 `summary_metrics` 表
    (`scripts/inspect_results.py`)。
-   修复后，通过 `scripts/compare_results.py` 显示前后对比。
-   在宣布成功之前，确认所有案例通过 — 不仅仅是你在处理的那个。

如果你无法提供证据（SDK 调用失败，结果被截断，指标不受支持），请明确说明。不要掩盖差距。

## 参与规则

1.  **始终先计划**：在编写脚本之前，输出一个 `<plan>` 块详细说明你即将采取的步骤。
2.  **逐步执行**：准备数据和评估脚本，展示带有完整参数的干运行确认卡，等待用户批准，只有在明确确认后执行，然后检查和分析结果。用户确认前**不要**运行评估调用。
3.  **标准 Python**：使用标准 Python 导入（`import agentplatform`，`from google.genai import types`）。不要使用内部导入路径。
4.  **在猜测前验证**：当不确定 SDK 类型或指标时，检查 SDK 源代码而不是猜测或编造。
5.  **不要无声地结束回合**：每个回合必须以非空的、提供用户行动总结或展示下一步的非空文本回复结束。返回空内容无论工具做了什么都会被视为失败。

## SDK 快速参考

```python
import agentplatform
from agentplatform import types
from google.genai import types as genai_types
import pandas as pd

# 初始化客户端
client = agentplatform.Client(project="PROJECT_ID", location="LOCATION")

# --- 单回合评估（pandas DataFrame） — 推荐 ---
# 转换器会为你包装普通字符串。
df = pd.DataFrame({
    "prompt":   ["Q1", "Q2"],
    "response": ["A1", "A2"],
})
dataset = types.EvaluationDataset(eval_dataset_df=df)

# --- 单回合评估（直接 EvalCase） ---
# 详细且容易出错；参见 references/dataset_schema.md 了解使用此形式的精确类型。
dataset = types.EvaluationDataset(eval_cases=[
    types.EvalCase(
        prompt=genai_types.UserContent("Query here"),
        responses=[types.ResponseCandidate(
            response=genai_types.ModelContent("Model response here"))],
        reference=types.ResponseCandidate(
            response=genai_types.ModelContent("Ground truth here")),
    ),
])

# --- 多回合代理评估 ---
agent_data = types.evals.AgentData(
    agents={"my_agent": types.evals.AgentConfig(
        agent_id="my_agent", instruction="You are helpful.")},
    turns=[types.evals.ConversationTurn(turn_index=0, events=[
        types.evals.AgentEvent(author="user",
            content=genai_types.Content(role="user",
                parts=[genai_types.Part(text="Hello")])),
        types.evals.AgentEvent(author="my_agent",
            content=genai_types.Content(role="model",
                parts=[genai_types.Part(text="Hi! How can I help?")])),
    ])],
)
dataset = types.EvaluationDataset(
    eval_cases=[types.EvalCase(agent_data=agent_data)])

# --- 指标 ---
predefined = types.RubricMetric.MULTI_TURN_TRAJECTORY_QUALITY
custom_llm = types.LLMMetric(name="tone",
    prompt_template="Is this polite? Response: {response}")
custom_code = types.CodeExecutionMetric(name="check",
    custom_function='def evaluate(instance): return {"score": 1.0}')

# --- 评估 ---
result = client.evals.evaluate(dataset=dataset, metrics=[predefined])

# --- 结果 ---
for s in result.summary_metrics:
    print(f"{s.metric_name}: mean={s.mean_score}, pass_rate={s.pass_rate}")
for case in result.eval_case_results:
    for cand in case.response_candidate_results:
        for name, r in cand.metric_results.items():
            print(f"  {name}: score={r.score}, explanation={r.explanation}")
```

参见 [references/sdk_patterns.md](references/sdk_patterns.md) 了解高级模式：合成数据生成、成对比较、`MetricPromptBuilder`、多代理评估。

## 嵌套脚本

脚本                   | 使用时机
---------------------- | -----------
`validate_dataset.py`    | 阶段 3 之前 — 捕获格式错误的 `EvaluationDataset` JSON。
`parse_adk_traces.py`    | 阶段 1 — 将 ADK 会话转储转换为规范数据集形状。
`inspect_results.py`     | 阶段 3/4 — 渲染摘要 + 每个案例的分数。 `--save-html` 用于可浏览报告。
`compare_results.py`     | 阶段 5 — 基线与候选的差异，检测退化。
`render_html_report.py`  | 从保存的结果 JSON 或 loss-clusters JSON 渲染 HTML。
`endpoint_evaluation.py` | 阶段 2/3 对部署的 Agent Platform 端点（BYOM）。参见 [references/deployment.md](references/deployment.md)。
`maas_evaluation.py`     | 阶段 2/3 对通过 ID 的 Model-as-a-Service 模型。参见 [references/deployment.md](references/deployment.md)。
