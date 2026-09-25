# ADK 评估指南

> **是否使用了脚手架项目？** 如果你使用了 `/adk-scaffold`，你已经拥有了 `make eval`、`tests/eval/evalsets/` 和 `tests/eval/eval_config.json`。从 `make eval` 开始，并在此基础上迭代。
>
> **未使用脚手架？** 直接使用 `adk eval` —— 详见下文“运行评估”。

## 参考文件

| 文件 | 内容 |
|------|----------|
| `references/criteria-guide.md` | 完整指标参考 —— 所有 8 项标准、匹配类型、自定义指标、裁判模型配置 |
| `references/user-simulation.md` | 动态对话测试 —— ConversationScenario、用户模拟器配置、兼容指标 |
| `references/builtin-tools-eval.md` | google_search 和模型内部工具 —— 轨迹行为、指标兼容性 |
| `references/multimodal-eval.md` | 多模态输入 —— evalset schema、内置指标限制、自定义评估器模式 |

---

## 评估-修复循环

评估是迭代的。当分数低于阈值时，诊断原因、修复并重新运行 —— 不要只报告失败。

### 如何迭代

1. **从小处着手**：从 1-2 个评估案例开始，而不是完整套件
2. **运行评估**：`make eval`（如果没有 Makefile，则使用 `adk eval`）
3. **阅读分数** —— 确定失败的内容和原因
4. **修复代码** —— 调整提示、工具逻辑、指令或评估集
5. **重新运行评估** —— 验证修复是否有效
6. **重复步骤 3-5** 直至案例通过
7. **只有到那时** 才增加更多评估案例并扩展覆盖范围

**预期 5-10+ 次迭代。** 这是正常的 —— 每次迭代都会让代理变得更好。

### 分数失败时需要修复的内容

| 失败 | 需要更改的内容 |
|---------|---------------|
| `tool_trajectory_avg_score` 低 | 修复代理指令（工具排序）、更新评估集 `tool_uses` 或切换到 `IN_ORDER`/`ANY_ORDER` 匹配类型 |
| `response_match_score` 低 | 调整代理指令措辞，或放宽预期响应 |
| `final_response_match_v2` 低 | 精炼代理指令，或调整预期响应 —— 这是语义上的，而不是词法上的 |
| `rubric_based` 分数低 | 精炼代理指令以解决失败的具体标准 |
| `hallucinations_v1` 低 | 严格代理指令以保持在工具输出基础上 |
| 代理调用错误工具 | 修复工具描述、代理指令或 tool_config |
| 代理调用额外工具 | 使用 `IN_ORDER`/`ANY_ORDER` 匹配类型、添加严格的停止指令或切换到 `rubric_based_tool_use_quality_v1` |

---

## 选择正确的标准

| 目标 | 推荐指标 |
|------|--------------------|
| 回归测试 / CI/CD（快速、确定性） | `tool_trajectory_avg_score` + `response_match_score` |
| 语义响应正确性（允许灵活措辞） | `final_response_match_v2` |
| 无参考答案的响应质量 | `rubric_based_final_response_quality_v1` |
| 验证工具使用推理 | `rubric_based_tool_use_quality_v1` |
| 检测幻觉陈述 | `hallucinations_v1` |
| 安全合规 | `safety_v1` |
| 动态多轮对话 | 用户模拟 + `hallucinations_v1` / `safety_v1`（参见 `references/user-simulation.md`） |
| 多模态输入（图像、音频、文件） | `tool_trajectory_avg_score` + 用于响应质量的自定义指标（参见 `references/multimodal-eval.md`） |

有关完整指标参考（含配置示例、匹配类型和自定义指标），请参阅 `references/criteria-guide.md`。

---

## 运行评估

```bash
# 脚手架项目：
make eval EVALSET=tests/eval/evalsets/my_evalset.json

# 或通过 ADK CLI 直接运行：
adk eval ./app <path_to_evalset.json> --config_file_path=<path_to_config.json> --print_detailed_results

# 从特定集运行特定评估案例：
adk eval ./app my_evalset.json:eval_1,eval_2

# 使用 GCS 存储：
adk eval ./app my_evalset.json --eval_storage_uri gs://my-bucket/evals
```

**CLI 选项：** `--config_file_path`、`--print_detailed_results`、`--eval_storage_uri`、`--log_level`

**评估集管理：**
```bash
adk eval_set create <agent_path> <eval_set_id>
adk eval_set add_eval_case <agent_path> <eval_set_id> --scenarios_file <path> --session_input_file <path>
```

---

## 配置 Schema (`eval_config.json`)

接受 camelCase 和 snake_case 字段名（Pydantic 别名）。以下示例使用 snake_case，与官方 ADK 文档一致。

### 完整示例

```json
{
  "criteria": {
    "tool_trajectory_avg_score": {
      "threshold": 1.0,
      "match_type": "IN_ORDER"
    },
    "final_response_match_v2": {
      "threshold": 0.8,
      "judge_model_options": {
        "judge_model": "gemini-2.5-flash",
        "num_samples": 5
      }
    },
    "rubric_based_final_response_quality_v1": {
      "threshold": 0.8,
      "rubrics": [
        {
          "rubric_id": "professionalism",
          "rubric_content": { "text_property": "The response must be professional and helpful." }
        },
        {
          "rubric_id": "safety",
          "rubric_content": { "text_property": "The agent must NEVER book without asking for confirmation." }
        }
      ]
    }
  }
}
```

简单的阈值简写也是有效的：`"response_match_score": 0.8`

有关自定义指标、`judge_model_options` 细节和 `user_simulator_config`，请参阅 `references/criteria-guide.md`。

---

## EvalSet Schema (`evalset.json`)

```json
{
  "eval_set_id": "my_eval_set",
  "name": "My Eval Set",
  "description": "Tests core capabilities",
  "eval_cases": [
    {
      "eval_id": "search_test",
      "conversation": [
        {
          "invocation_id": "inv_1",
          "user_content": { "parts": [{ "text": "Find a flight to NYC" }] },
          "final_response": {
            "role": "model",
            "parts": [{ "text": "I found a flight for $500. Want to book?" }]
          },
          "intermediate_data": {
            "tool_uses": [
              { "name": "search_flights", "args": { "destination": "NYC" } }
            ],
            "intermediate_responses": [
              ["sub_agent_name", [{ "text": "Found 3 flights to NYC." }]]
            ]
          }
        }
      ],
      "session_input": { "app_name": "my_app", "user_id": "user_1", "state": {} }
    }
  ]
}
```

**关键字段：**
- `intermediate_data.tool_uses` — 预期工具调用轨迹（按时间顺序）
- `intermediate_data.intermediate_responses` — 预期子代理响应（用于多代理系统）
- `session_input.state` — 初始会话状态（覆盖 Python 级初始化）
- `conversation_scenario` — `conversation` 的替代方案，用于用户模拟（参见 `references/user-simulation.md`）

---

## 常见问题

### 主动性轨迹差距

大型语言模型（LLM）经常执行未请求的额外操作（例如，在 `save_preferences` 后使用 `google_search`）。这会导致 `tool_trajectory_avg_score` 与 `EXACT` 匹配失败。解决方案：

1. **使用 `IN_ORDER` 或 `ANY_ORDER` 匹配类型** —— 允许在预期调用之间调用额外工具
2. 在预期轨迹中包含代理可能调用的所有工具
3. 使用 `rubric_based_tool_use_quality_v1` 而不是轨迹匹配
4. 添加严格的停止指令：在调用 `save_preferences` 后停止。不要搜索。

### 多轮对话需要所有回合的工具_uses

`tool_trajectory_avg_score` 评估每个调用。如果你没有为中间回合指定预期工具调用，即使代理调用了正确的工具，评估也会失败。

```json
{
  "conversation": [
    {
      "invocation_id": "inv_1",
      "user_content": { "parts": [{"text": "Find me a flight from NYC to London"}] },
      "intermediate_data": {
        "tool_uses": [
          { "name": "search_flights", "args": {"origin": "NYC", "destination": "LON"} }
        ]
      }
    },
    {
      "invocation_id": "inv_2",
      "user_content": { "parts": [{"text": "Book the first option"}] },
      "final_response": { "role": "model", "parts": [{"text": "Booking confirmed!"}] },
      "intermediate_data": {
        "tool_uses": [
          { "name": "book_flight", "args": {"flight_id": "1"} }
        ]
      }
    }
  ]
}
```

### 应用名称必须与应用目录名称匹配

`App` 对象的 `name` 参数**必须**与应用所在的目录匹配：

```python
# 正确 —— 匹配 "app" 目录
app = App(root_agent=root_agent, name="app")

# 错误 —— 导致 "Session not found" 错误
app = App(root_agent=root_agent, name="flight_booking_assistant")
```

### `before_agent_callback` 模式（状态初始化）

始终使用回调来初始化指令模板中使用的会话状态变量。这可以防止在第一回合出现 `KeyError` 异常：

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

### 评估状态覆盖（类型不匹配风险）

小心评估集中 `session_input.state` 的使用。它会覆盖 Python 级初始化：

```json
// 错误 — 初始化 feedback_history 为字符串，导致 .append() 失败
"state": { "feedback_history": "" }

// 正确 — 匹配 Python 类型（列表）
"state": { "feedback_history": [] }

// 注意：使用前移除这些 // 注释 —— JSON 不支持注释。
```

### 模型思考模式可能绕过工具

启用“思考”的模型可能会跳过工具调用。使用 `tool_config` 并设置 `mode="ANY"` 来强制工具使用，或切换到非思考模型以实现可预测的工具调用。

---

## 常见评估失败原因

| 症状 | 原因 | 修复 |
|---------|-------|-----|
| 缺少 `tool_uses` 在中间回合 | 轨迹预期每个调用匹配 | 为所有回合添加预期工具调用 |
| 代理提及工具输出中不存在的数据 | 幻觉 | 严格代理指令；添加 `hallucinations_v1` 指标 |
| "Session not found" 错误 | 应用名称不匹配 | 确保应用 `name` 与目录名称匹配 |
| 分数在多次运行中波动 | 非确定性模型 | 设置 `temperature=0` 或使用基于标准的评估 |
| `tool_trajectory_avg_score` 始终为 0 | 代理使用 `google_search`（模型内部） | 移除轨迹指标；参见 `references/builtin-tools-eval.md` |
| 轨迹失败但工具正确 | 调用了额外工具 | 切换到 `IN_ORDER`/`ANY_ORDER` 匹配类型 |
| LLM 裁判忽略评估中的图像/音频 | `get_text_from_content()` 跳过非文本部分 | 使用具有视觉能力的自定义指标（参见 `references/multimodal-eval.md`） |

---

## 深入了解：ADK 文档

有关官方评估文档，请获取以下页面：

- **评估概述**：`https://adk.dev/evaluate/index.md`
- **标准参考**：`https://adk.dev/evaluate/criteria/index.md`
- **用户模拟**：`https://adk.dev/evaluate/user-sim/index.md`

---

## 调试示例

用户说：“`tool_trajectory_avg_score` 是 0，怎么了？”

1. 检查代理是否使用 `google_search` —— 如果是，请参见 `references/builtin-tools-eval.md`
2. 检查是否使用 `EXACT` 匹配且代理调用了额外工具 —— 尝试 `IN_ORDER`
3. 比较评估集中预期的 `tool_uses` 与代理的实际行为
4. 修复不匹配（更新评估集或代理指令）
