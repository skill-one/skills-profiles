# Agent Platform Eval Flywheel Skill

使用 Agent Platform GenAI Evaluation SDK (`google.genai` / `agentplatform`) 帮助用户评估和迭代改进 GenAI 模型和代理。

## 何时使用此技能

- 使用 Agent Platform GenAI Evaluation SDK (`client.evals.evaluate()`) 评估 GenAI 代理或模型。
- 从会话跟踪、pandas DataFrame 或合成生成创建评估数据集。
- 选择、配置或编写自定义评估指标。
- 分析评分标准判定、损失模式和聚类失败。
- 根据评估结果建议具体的代码/提示改进。
- 评估在 Agent Platform **端点**（BYOM）上托管的模型或通过 ID 评估 **模型即服务 (MaaS)** 模型——如果需要，首先部署该模型。对于此情况，请遵循 [references/deployment.md](references/deployment.md) 并使用 `endpoint_evaluation.py` / `maas_evaluation.py` 脚本。

## 安全性与确认级别（关键）

在代表用户执行任何命令或脚本之前，您**必须**根据请求的操作遵守以下安全级别：

1.  **R 级：只读** (`inspect_results.py`, `compare_results.py`, `validate_dataset.py`, `parse_adk_traces.py`, `render_html_report.py`)
    *   **规则**：无需确认。您可以立即执行这些辅助脚本以检查数据、验证模式、解析跟踪或比较评估结果。
2.  **M 级：只读带计算成本** (`client.evals.run_inference`, `client.evals.evaluate`, `client.evals.generate_conversation_scenarios`, `client.evals.generate_loss_clusters`)
    *   **规则**：这些操作调用 LLM 或远程评估服务，消耗计算资源并产生费用。这需要与“是”/“否”选项进行**交互式确认**。一旦获得许可，您就不必将来再提示评估。
    *   **同回合限制**：不要在显示确认提示的同回合中运行评估。在询问后结束您的回合，等待用户的回复；只有在明确“是”/批准后才能执行。在用户可以回答之前打印预览然后调用工具不算是获得确认。

## 设置

脚本需要 `vertexai`（来自 `google-cloud-aiplatform[evaluation]`）、`google-genai`、`pandas` 和 `requests`。**不要**创建虚拟环境——它开始为空并隐藏环境已经提供的包，强制进行冗余安装。探测并仅安装缺少的部分：

```bash
python3 -c "import vertexai, google.genai, pandas, requests" \
  || pip install 'google-cloud-aiplatform[evaluation]>=1.163.0' 'google-genai>=1.0.0'
```

版本规范必须保持引号：未加引号，bash 将 `>=1.154.0` 解释为重定向，并静默写入空文件而不是限制安装。

需要 `GOOGLE_CLOUD_PROJECT` 和 `GOOGLE_CLOUD_LOCATION`。首先检查环境变量；如果缺失，请询问用户。较新的 Gemini 模型通常需要 `location="global"`。

### 正确的 SDK 入口点

```python
import agentplatform
client = agentplatform.Client(project=PROJECT, location=LOCATION)

client.evals.run_inference(model=..., src=...)
client.evals.evaluate(dataset=..., metrics=...)
client.evals.generate_conversation_scenarios(...)
```

看起来合理但不是的两个导入：

-   `from agentplatform.types import evals` —— `ModuleNotFoundError`。`types` 是一个模块，不是一个包；使用 `from agentplatform import types`。
-   `from vertexai.evaluation import PointwiseMetric, EvalTask` —— 已弃用的 SDK。它的类接受不同的参数 (`PointwiseMetric` 没有参数 `system_instruction`)，因此针对它的代码会以 `TypeError` 而不是导入错误失败。在整个过程中使用 `agentplatform`。

## 质量飞轮

五个阶段，在第一次通过时按顺序运行，然后循环 2 → 5 直到质量目标达成。

### 浪费时间的捷径

| 短切                             | 为什么它会失败                         |
| ------------------------------------ | ------------------------------------ |
| "我会调低指标阈值，让它通过。"       | 隐藏了真正的失败。修复代理，而不是标杆。 |
| "这个案例不稳定，我会跳过它。"       | 不稳定性揭示了代理中的非确定性。使用 `temperature=0` 或更严格的指令修复。 |
| "我只需要修复评估数据集，不需要修复代理。" | 如果预期输出不断变化，代理存在行为问题。 |
| "我可以从跟踪中判断它工作正常，跳过阶段 3。" | 自我评分无法泛化。始终运行 `evaluate()` 并阅读分数。 |
| "一次迭代就足够了。"           | 预期 5–10+ 次迭代。过早停止会在其他指标上留下回归。 |

### 1. 准备数据

生成一个 `EvaluationDataset`。有三个输入形状，选择与用户已有的数据匹配的一个：

-   **`EvalCase` 列表（单回合或多回合）：**

    ```python
    from agentplatform import types
    from google.genai import types as genai_types

    # 提示/参考/响应值是 Content，不是 str。UserContent 和
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

    多回合代理跟踪将每个对话包装在 `AgentData` →
    `ConversationTurn` → `AgentEvent`。有关完整的类型层次结构，请参阅
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

-   **冷启动（没有任何数据）：** 在服务器端使用 `client.evals.generate_conversation_scenarios(agent=..., config=...)` 合成场景——参数是 `agent` 或 `agent_info`，而不是 `agents`，并且 `config` 是必需的。配置类是 `types.evals.UserScenarioGenerationConfig`，而不是 `types.UserScenarioGenerationConfig`。设置其 `user_scenario_count`（1-100）：它默认为 None，客户端接受，服务器会以 `400 INVALID_ARGUMENT` 拒绝调用。`count` 是一个单独的字段，不能替代它。阶段 2 会执行这些场景。

-   **托管代理（Gemini Agents API）：** 使用 [Managed Agents API](https://docs.cloud.google.com/gemini-enterprise-agent-platform/build/managed-agents) 创建的代理进行评估。使用 `generate_conversation_scenarios` 从代理配置创建测试场景，使用 `run_inference` 执行代理，使用 `evaluate` 评分跟踪。这些函数现在接受托管代理和交互 ID 作为输入。您还可以使用 `InteractionsDataSource` 评估通过 Interactions API 记录的现有交互。有关完整代码模式，请参阅 [references/sdk_patterns.md](references/sdk_patterns.md) 模式 8。

对于 ADK 会话转储，使用 `scripts/parse_adk_traces.py` 而不是手动编写转换。

### 2. 运行推理

在数据集上填充响应/跟踪。如果跟踪已经完整（例如，生产日志或重播），则**跳过此阶段**。

```python
# 代理评估——传递一个包装用户 ADK 代理/应用的可调用对象。
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

**根据您想要测量的内容选择指标。** 完整目录在
[references/metric_registry.md](references/metric_registry.md)。

**代理指标（多回合、自适应评分标准）**——从代理评估开始。

目标                                          | 指标
--------------------------------------------- | -------------------------------
代理是否实现了用户的目标？        | `multi_turn_task_success`
推理路径是否逻辑高效？            | `multi_turn_trajectory_quality`
跨回合工具/函数调用质量            | `multi_turn_tool_use_quality`
整体对话质量                | `multi_turn_general_quality`
最终响应质量（不需要参考）  | `final_response_quality`
最终响应与黄金参考         | `final_response_match`
单回合工具使用                          | `tool_use_quality`

**通用质量指标（单回合、自适应评分标准）**——用于模型评估。

目标                                                  | 指标
----------------------------------------------------- | -----------------------
整体响应质量（推荐起点） | `general_quality`
语言质量（流畅性、连贯性、语法）      | `text_quality`
遵守特定约束/指令      | `instruction_following`

**静态评分标准指标（固定标准）**——与上述指标一起应用。

目标                                              | 指标
------------------------------------------------- | ---------------
捕获幻觉陈述（RAG、事实性答案）  | `hallucination`
事实性/一致性相对于提供的环境 | `grounding`
安全策略合规                          | `safety`

**没有内置指标涵盖的领域特定检查：** 编写自定义指标。

-   **预定义：** `types.RubricMetric.<NAME>` — 服务器端 AutoRater，不需要判定模型。
-   **自定义 LLM 作为判定者：** `types.LLMMetric` 与 `prompt_template` 或
    `types.MetricPromptBuilder` 用于结构化评分标准。始终设置
    `judge_model`；它默认为 `None`，否则每个案例都会以 `400 INVALID_ARGUMENT: Error parsing JSON` 失败。
-   **自定义代码：** `types.CodeExecutionMetric` 与包含 `def evaluate(instance: dict)` 的 `custom_function` 字符串进行远程沙盒执行；或
    `types.Metric` 与 `custom_function=<callable>` 进行本地执行。

**始终持久化结果**，以便阶段 4 和 5 可以读取它。保存 JSON（机器可读，可比较）和 HTML（人类可读，可链接）：

```python
import datetime
from pathlib import Path

from agentplatform._genai import _evals_visualization

out_dir = Path("artifacts/grade_results")
out_dir.mkdir(parents=True, exist_ok=True)
ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

# fallback=str，或 DataFrame 背景的数据集引发 PydanticSerializationError。
result_json = result.model_dump_json(fallback=str)
(out_dir / f"results_{ts}.json").write_text(result_json)

html = _evals_visualization.get_evaluation_html(result_json)
(out_dir / f"results_{ts}.html").write_text(str(html))
```

或者事后：`scripts/render_html_report.py --type evaluation` 或
`scripts/inspect_results.py --save-html`。

### 4. 分析失败

读取 `summary_metrics` 和 `eval_case_results`——永远不要编造分数。使用
`scripts/inspect_results.py --failing-only` 过滤到失败。

对于每个失败的指标，请参阅
[references/failure_patterns.md](references/failure_patterns.md) 进行更深入的诊断。紧凑映射：

| 失败的指标                      | 要更改的内容                         |
| ----------------------------------- | -------------------------------------- |
| `multi_turn_task_success` 低       | 代理没有完成目标——修复编排、缺失工具调用、 |
:                                     : 提前终止、错误的工具选择。                             :
| `multi_turn_trajectory_quality` 低 | 代理低效地达到目标 — 精炼计划提示、删除冗余工具调用。 |
| `multi_turn_tool_use_quality` 低   | 修复工具描述、参数文档字符串，或代理工具选择的指令。 |
| `final_response_quality` 低        | 阅读自动生成的评分标准判定；改进指令以解决最差的评分标准。 |
| `final_response_match` 低          | 代理的最终答案与黄金参考不匹配 — 调整响应格式或更新参考。 |
| `hallucination` 低                 | 放宽指令以保持在工具输出中；验证工具确实返回了声称的数据。 |
| `grounding` 低                     | 响应与提供的环境矛盾 — 添加明确的“仅引用上下文”指令。 |
| `safety` 低                        | 添加安全护栏；审查评分标准判定中违反的内容类别。 |
| `general_quality` / `text_quality`  | 调整系统指令措辞；模型的默认措辞对于任务过于通用。 |
| `instruction_following` 低         | 代理忽略约束 — 在系统指令中重申它们或使用更严格的措辞。 |
| Agent 调用错误工具             | 修复工具描述、代理 |
:                                     : 指令，或 `tool_config`。        :
| Agent 调用额外工具             | 添加明确的停止指令，或切换到                              :
:                                     : `multi_turn_tool_use_quality` 以在评分标准中暴露额外调用。 :

**对于同一指标 10+ 次失败，** 使用 **错误分析服务** 将失败聚类为主题（L1/L2 分类类别），而不是阅读每个跟踪：

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
--type loss-analysis` 渲染。

### 5. 优化和迭代

应用针对失败指标的修复。重新运行阶段 3。使用
`scripts/compare_results.py --baseline <prev> --candidate <new>` 确认目标改进且其他指标没有退化。

跨迭代跟踪进度：

迭代 | 指标 A | 指标 B | 所做的更改
--------- | -------- | -------- | ----------------------
基线  | 0.62     | 0.55     | —
v2        | 0.78     | 0.68     | 添加了 grounding 提示
v3        | 0.81     | 0.72     | 修复了工具选择

预期每个失败案例 5–10+ 次迭代。只有案例通过后，您才能扩展覆盖范围，使用更多评估案例。

## 证明你的工作

永远不要声称你没有从实际的 `result` 对象中阅读的评估结果。

-   运行评估后，打印 `summary_metrics` 表格
    (`scripts/inspect_results.py`)。
-   修复后，通过 `scripts/compare_results.py` 显示前后对比。
-   在宣布成功之前，确认所有案例通过——而不仅仅是您正在处理的案例。

如果您无法提供证据（SDK 调用失败、结果被截断、指标不受支持），请明确说明。不要掩盖差距。

## 参与规则

1.  **始终先计划**：在编写脚本之前，输出一个 `<plan>` 块，详细说明您即将采取的步骤。
2.  **逐步执行**：编写脚本，执行它，等待输出，然后分析。不要在一个响应中做所有事情。
3.  **标准 Python**：使用标准 Python 导入 (`import agentplatform`, `from google.genai import types`)。不要使用内部导入路径。
4.  **验证后再猜测**：当不确定 SDK 类型或指标时，检查 SDK 源代码，而不是猜测或幻觉。

## SDK 快速参考

```python
import agentplatform
from agentplatform import types
from google.genai import types as genai_types
import pandas as pd

# 初始化客户端
client = agentplatform.Client(project="PROJECT_ID", location="LOCATION")

# --- 单回合评估 (pandas DataFrame) (推荐 ---
# 转换器会为您包装普通字符串。
df = pd.DataFrame({
    "prompt":   ["Q1", "Q2"],
    "response": ["A1", "A2"],
})
dataset = types.EvaluationDataset(eval_dataset_df=df)

# --- 单回合评估 (直接 EvalCase ---
# 详细且容易出错；有关确切类型，请在使用此形式之前查看 references/dataset_schema.md。
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
预定义 = types.RubricMetric.MULTI_TURN_TRAJECTORY_QUALITY
自定义 LLM = types.LLMMetric(name="tone",
    prompt_template="Is this polite? Response: {response}")
自定义代码 = types.CodeExecutionMetric(name="check",
    custom_function='def evaluate(instance): return {"score": 1.0}')

# --- 评估 ---
result = client.evals.evaluate(dataset=dataset, metrics=[预定义])

# --- 结果 ---
for s in result.summary_metrics:
    print(f"{s.metric_name}: mean={s.mean_score}, pass_rate={s.pass_rate}")
for case in result.eval_case_results:
    for cand in case.response_candidate_results:
        for name, r in cand.metric_results.items():
            print(f"  {name}: score={r.score}, explanation={r.explanation}")
```

有关高级模式，请参阅 [references/sdk_patterns.md](references/sdk_patterns.md)：合成数据生成、成对比较、`MetricPromptBuilder`、多代理评估。

## 嵌套脚本

脚本                   | 何时使用
------------------------ | -----------
`validate_dataset.py`    | 在阶段 3 之前——捕获格式错误的 `EvaluationDataset` JSON。
`parse_adk_traces.py`    | 阶段 1 — 将 ADK 会话转储转换为规范的数据集形状。
`inspect_results.py`     | 阶段 3/4 — 渲染摘要 + 每个案例的分数。 `--save-html` 用于可浏览报告。
`compare_results.py`     | 阶段 5 — 比较基线与候选，检测退化。
`render_html_report.py`  | 从保存的结果 JSON 或损失聚类 JSON 渲染 HTML。
`endpoint_evaluation.py` | 阶段 2/3 对 Agent Platform 端点（BYOM）。请参阅 [references/deployment.md](references/deployment.md).
`maas_evaluation.py`     | 阶段 2/3 对通过 ID 的 Model-as-a-Service 模型。请参阅 [references/deployment.md](references/deployment.md).
