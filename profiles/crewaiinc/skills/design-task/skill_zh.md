# CrewAI 任务设计指南

如何编写有效的任务，以使您的智能体（agent）能够产出可靠、高质量的输出。

---

## 80/20 法则

**将 80% 的工作量投入到任务设计，20% 的工作量投入到智能体设计。** 任务是最重要的杠杆。一个设计良好的任务，即使配合一个普通的智能体，其表现也会优于一个设计不佳的任务，即使后者配备了一个优秀的智能体。

---

## 有效的任务构成

每个任务都需要两个要素：**描述**（做什么和怎么做）和**预期输出**（结果看起来像什么）。

### 描述 — 指令

一个好的描述应包括：
1. **做什么** — 核心动作
2. **怎么做** — 具体步骤或方法
3. **背景** — 为什么这很重要，它如何被利用
4. **约束** — 范围限制，需要避免的事项
5. **输入** — 可用的数据或背景信息

```yaml
research_task:
  description: >
    对 {topic} 进行全面研究，时间为 {current_year} 年。

    您的研究应：
    1. 识别出 5 个关键趋势和突破性进展
    2. 对每个趋势，找到至少 2 个可信来源
    3. 记录任何争议或不同观点
    4. 评估潜在的行业影响（高/中/低）

    重点关注过去 6 个月的最新发展。
    不要包含猜测或未经证实的说法。
    该输出将用于为 {target_audience} 编写的报告。
  expected_output: >
    一个结构化的研究简报，包含 5 个部分，每部分对应一个趋势。
    每个部分包括：趋势名称、2-3 段摘要，
    来源引用、影响评估（高/中/低），
    以及对您发现的信心水平。
  agent: researcher
```

### 预期输出 — 成功标准

`expected_output` 告诉智能体“完成”的标准。请具体说明：
- **格式** — 项目符号、段落、JSON、表格
- **结构** — 部分、标题、顺序
- **长度** — 大约字数或项目数量
- **质量标记** — 是否需要引用、信心水平、特定字段

| 不好的预期输出 | 好的预期输出 |
|---|---|
| `一份研究报告` | `一个结构化的简报，包含 5 个部分，每个部分包含：趋势名称、2-3 段摘要、来源引用和影响评级` |
| `对数据的分析` | `一个 Markdown 表格，包含列：指标名称、当前值、30 天趋势和推荐行动。至少包含 10 个指标。` |
| `一篇博客文章` | `一篇 1000-1500 字的技术博客文章，包含：标题、引言、3-4 个主要部分（含代码示例）和结论（含下一步行动）` |

---

## 单一目的原则

**一个任务 = 一个目标。** 不要将多个操作合并到一个任务中。

### 不好的：全能任务（God Task）

```yaml
# 不要这样做 — 一个任务包含太多目标
research_and_write_task:
  description: >
    研究 {topic}，分析研究结果，撰写博客文章，
    并校对语法错误。
  expected_output: >
    一篇关于 {topic} 的精炼博客文章。
```

### 好的：专注任务

```yaml
research_task:
  description: >
    研究 {topic} 并识别出 5 个关键发展。
  expected_output: >
    一个包含关键趋势的研究简报。
  agent: researcher

writing_task:
  description: >
    使用研究结果，撰写关于 {topic} 的技术博客文章。
  expected_output: >
    一篇 1000-1500 字的博客文章，包含引言、主要部分，
    和结论。在相关的地方包含代码示例。
  agent: writer

editing_task:
  description: >
    审阅和编辑博客文章，检查语法、清晰度和一致性。
  expected_output: >
    最终编辑后的博客文章，包含所有已应用的更正。
    包含一个编辑备注，列出所做的更改。
  agent: editor
```

每个任务都有一个明确的目标。顺序流程会自动传递上下文。

---

## 任务配置参考

### 基本参数

```python
Task(
    description="...",          # 必填：做什么
    expected_output="...",      # 必填：结果看起来像什么
    agent=researcher,           # 可选（分层流程中）；顺序流程中必填
)
```

### 基于依赖的任务

```python
analysis_task = Task(
    description="分析研究结果...",
    expected_output="...",
    agent=analyst,
    context=[research_task],    # 接收 research_task 的输出作为上下文
)
```

**在顺序流程中：** 每个任务自动接收所有先前的任务输出。仅在需要非线性依赖时使用 `context`。

**在分层流程中：** `context` 用于在任务之间创建显式的数据流。

### 结构化输出

当下游代码需要解析结果时，使用 `output_pydantic` 或 `output_json`：

```python
from pydantic import BaseModel

class ResearchReport(BaseModel):
    trends: list[str]
    confidence: float
    sources: list[str]

research_task = Task(
    description="...",
    expected_output="一个结构化的报告，包含趋势、信心评分和来源。",
    agent=researcher,
    output_pydantic=ResearchReport,   # 智能体的输出将被解析为这个模型
)
```

**重要：** `expected_output` 总是一个 **字符串描述** — 永远不是类名。Pydantic 模型放在 `output_pydantic` 中，而 `expected_output` 文本告诉智能体要包含哪些字段。

访问结构化输出：
```python
result = crew.kickoff(inputs={...})
last_task_output = result.pydantic          # 最后一个任务的 Pydantic 模型
all_outputs = result.tasks_output           # 所有 TaskOutput 对象的列表
first_task = all_outputs[0].pydantic        # 特定任务的 Pydantic
```

### 文件输出

```python
Task(
    ...,
    output_file="output/report.md",    # 保存输出到文件
    create_directory=True,             # 如果不存在则创建目录（默认：True）
)
```

文件输出和结构化输出可以结合使用 — 文件接收原始文本，`output_pydantic` 接收解析后的模型。

### 异步执行

```python
Task(
    ...,
    async_execution=True,     # 无阻塞地运行
)
```

用于可以并行运行的任务。Crew 会继续执行下一个任务，而当前任务正在执行。在下游任务上使用 `context` 以等待异步结果。

### 人工审核

```python
Task(
    ...,
    human_input=True,         # 在最终确定之前暂停以进行人工审核
)
```

启用时，智能体会展示其结果并等待人工反馈，然后才标记任务完成。用于需要人工批准的关键输出。

**不要使用 `human_input=True` 或 Flow `@human_feedback` 来模拟正常的后续聊天。** 在对话式 Flow 中，下一个用户行应该是另一个 `flow.handle_turn(message, session_id=...)` 调用。人工审核用于在结果流向下游之前批准或更正特定的任务/步骤输出。

### Markdown 格式化

```python
Task(
    ...,
    markdown=True,            # 添加 Markdown 格式化指令
)
```

自动指示智能体使用正确的 Markdown 标题、列表、强调和代码块来格式化输出。

### 回调函数

```python
def log_completion(output):
    print(f"任务完成：{output.description[:50]}...")
    save_to_database(output.raw)

Task(
    ...,
    callback=log_completion,  # 任务完成后调用
)
```

---

## 4. 任务约束 — 质量控制

约束在任务输出传递到下一步之前进行验证。如果验证失败，智能体会重试。

### 基于函数的约束

```python
def validate_word_count(output) -> tuple[bool, Any]:
    """确保输出在 500-2000 字之间。"""
    word_count = len(output.raw.split())
    if word_count < 500:
        return (False, f"输出太短 ({word_count} 字)。扩展到至少 500 字。")
    if word_count > 2000:
        return (False, f"输出太长 ({word_count} 字)。压缩到少于 2000 字。")
    return (True, output)

Task(
    ...,
    guardrail=validate_word_count,
    guardrail_max_retries=3,       # 最大重试次数（默认：3）
)
```

**返回格式：** `(bool, Any)` — 第一个元素是通过/失败，第二个元素是结果（成功时）或错误消息（失败时）。

### 基于大型语言模型的约束

```python
Task(
    ...,
    guardrail="验证输出至少包含 3 个来源引用，且不包含猜测性声明。",
)
```

字符串约束使用智能体的 LLM 来评估输出。适用于主观质量检查。

### 连接多个约束

```python
Task(
    ...,
    guardrails=[
        validate_word_count,           # 函数：检查长度
        validate_no_pii,               # 函数：检查是否包含个人身份信息（PII）
        "确保语气专业，适合商业受众。",  # LLM 检查
    ],
    guardrail_max_retries=3,
)
```

约束按顺序执行。每个约束接收前一个约束的输出。混合基于函数（确定性）和基于 LLM（主观）的检查。

---

## 5. YAML 配置（推荐）

### tasks.yaml

```yaml
research_task:
  description: >
    对 {topic} 进行全面研究，时间为 {current_year} 年。
    识别关键趋势、突破性技术和潜在的行业影响。
    重点关注过去 6 个月的最新发展。
  expected_output: >
    一个包含 5 个部分的结构化研究简报。
    每个部分：趋势名称、2-3 段摘要，
    来源引用和影响评估。
  agent: researcher

analysis_task:
  description: >
    分析研究结果，并为 {target_audience} 创建可操作的推荐
    建议。
  expected_output: >
    一个包含 5 个优先级建议的列表，包括：
    理由、估计工作量、预期影响。
  agent: analyst
  context:
    - research_task

report_task:
  description: >
    编写最终报告，结合研究和分析，面向 {target_audience}。
  expected_output: >
    一个经过润色的 Markdown 报告，包含执行摘要，
    详细发现、建议和附录。
  agent: writer
  output_file: output/report.md
```

### 在 crew.py 中连接

```python
@CrewBase
class ResearchCrew:
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @task
    def research_task(self) -> Task:
        return Task(config=self.tasks_config["research_task"])

    @task
    def analysis_task(self) -> Task:
        return Task(
            config=self.tasks_config["analysis_task"],
            context=[self.research_task()],
        )

    @task
    def report_task(self) -> Task:
        return Task(
            config=self.tasks_config["report_task"],
            output_file="output/report.md",
        )
```

**关键：** 方法名（`def research_task`）必须与 YAML 键（`research_task:`）匹配。

---

## 6. 任务依赖和上下文流

### 顺序流程（默认）

在 `Process.sequential` 中，任务按顺序运行。每个任务自动接收所有先前的任务输出作为上下文。

```
research_task → analysis_task → report_task
     ↓               ↓              ↓
  输出 1    输出 1 + 2    输出 1 + 2 + 3
```

您不需要 `context=` 在顺序中 — 它是隐式的。仅在创建非线性依赖时使用它：

```python
# 任务 C 依赖于 A，但不依赖于 B
task_c = Task(
    ...,
    context=[task_a],  # 只接收 task_a 输出，不接收 task_b
)
```

### 显式依赖

```python
# 菱形依赖模式
task_a = Task(...)                          # 入口点
task_b = Task(..., context=[task_a])        # 依赖于 A
task_c = Task(..., context=[task_a])        # 也依赖于 A
task_d = Task(..., context=[task_b, task_c])  # 依赖于 B 和 C
```

### 条件任务

```python
from crewai.task import ConditionalTask

def needs_more_data(output) -> bool:
    return len(output.pydantic.items) < 10

extra_research = ConditionalTask(
    description="获取更多数据源...",
    expected_output="...",
    agent=researcher,
    condition=needs_more_data,  # 仅当先前输出包含少于 10 个项目时运行
)
```

---

## 7. 任务工具

任务可以有自己的工具，用于覆盖智能体针对该特定任务的默认工具：

```python
from crewai_tools import SerperDevTool, ScrapeWebsiteTool

Task(
    description="搜索并抓取关于 {topic} 的前 5 篇文章...",
    expected_output="...",
    agent=researcher,
    tools=[SerperDevTool(), ScrapeWebsiteTool()],  # 任务特定工具
)
```

**何时使用任务级工具：**
- 任务需要智能体通常没有的工具
- 您希望限制智能体仅为此任务使用特定工具
- 同一个智能体的不同任务需要不同的工具集

---

## 8. 变量插值

在 YAML 中使用 `{variable}` 占位符用于可重用的任务：

```yaml
research_task:
  description: >
    研究 {topic} 趋势，时间为 {current_year}，
    面向 {target_audience}。
  expected_output: >
    一个适合 {target_audience} 的 {topic} 报告。
```

变量在调用 `crew.kickoff(inputs={...})` 时被替换：

```python
crew.kickoff(inputs={
    "topic": "AI Agents",
    "current_year": "2025",
    "target_audience": "developers",
})
```

**常见错误：**
- `inputs` 中遗漏变量 → 字面量 `{variable}` 出现在提示中
- 使用 `{{ }}` Jinja2 语法 → crewAI 使用单花括号 `{ }`
- `inputs` 中未使用的变量 → 沉默地忽略（无错误）

---

## 9. 常见的任务设计错误

| 错误 | 影响 | 修复 |
|---|---|---|
| 模糊的描述（"研究主题"） | 智能体产出肤浅、不集中的输出 | 添加具体步骤、约束和背景 |
| 模糊的预期输出（"一份报告"） | 智能体猜测格式和结构 | 指定格式、部分、长度、质量标记 |
| 一个任务包含多个目标 | 智能体在所有方面表现不佳 | 将其拆分为专注的单目标任务 |
| 将每个聊天回合建模为 Crew 任务 | 任务是批处理/工作流单元，不是对话会话循环 | 使用对话式 Flow，并为每个用户消息调用 `handle_turn()` |
| 依赖任务之间没有上下文 | 智能体缺乏来自先前步骤的信息 | 使用 `context=[prior_task]` 进行显式依赖 |
| `expected_output` 引用 Pydantic 类 | 智能体看到的是类名字符串，而不是字段名 | 将 `expected_output` 保留为人类可读的字符串；使用 `output_pydantic` 为模型 |
| 数据任务缺少工具 | 智能体编造数据而不是获取数据 | 向任务或智能体添加工具 |
| 关键输出没有约束 | 坏输出未经检查地流向下游 | 添加函数或 LLM 约束 |
| 过于严格的预期输出 | 智能体试图匹配不可能的标准而循环 | 具体但可实现；降低 `guardrail_max_retries` 以更快失败 |
| 描述重复背景故事 | 浪费 token 并使智能体困惑 | 描述 = 要做什么；背景故事 = 你是谁 |

---

## 10. 任务设计检查清单

在运行任务之前，请验证：

- [ ] **描述** 包括做什么、怎么做、背景和约束
- [ ] **预期输出** 指定格式、结构和质量标记
- [ ] **单一目的** — 每个任务一个明确的目标
- [ ] **已分配智能体**（或任务位于分层 Crew 中）
- [ ] **依赖关系** 通过 `context` 设置，如需要
- [ ] **工具** 为需要外部数据的任务提供
- [ ] **结构化输出** 配置，如果下游代码解析结果
- [ ] **约束** 为关键输出设置
- [ ] **变量** 在 YAML 中与 `inputs` 字典键匹配
- [ ] **预期输出是可实现的** — 在添加复杂性之前先进行简单运行测试

---

## 参考文献

要深入了解特定主题，请参阅：

- [结构化输出](references/structured-output.md) — `output_pydantic`、`output_json` 和跨 LLM、Agent、Task 和 Crew 级别的 `response_format` 模式

相关技能：

- **getting-started** — 项目脚手架、选择正确的抽象、Flow 架构
- **design-agent** — Agent 的角色-目标-背景故事框架、参数调整、工具分配、记忆和知识配置
- **ask-docs** — 查询实时 CrewAI 文档 MCP 服务器，以获取未涵盖这些技能的问题的答案
