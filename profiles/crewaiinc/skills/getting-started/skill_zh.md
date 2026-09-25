# CrewAI 入门与架构

如何选择合适的抽象级别、搭建项目框架，并将所有组件连接在一起。

---

## 必须的工作流程 — 首先阅读此部分

**绝对不要手动创建 crewAI 项目文件。** 始终使用 CLI 进行搭建：

```bash
crewai create flow <项目名称>
```

这是**非可选**的。即使你只需要一个 crew，即使你熟悉文件结构 — 首先运行 CLI，然后修改生成的文件。不要从零开始手动编写 `main.py`、`crew.py`、`agents.yaml`、`tasks.yaml` 或 `pyproject.toml`。

> **原因：** CLI 设置了正确的导入、目录结构、pyproject.toml 配置和模板代码，这些在手动完成时很容易出错。下面的参考材料将教你如何理解各个组件的工作原理，以便你可以*修改*搭建的代码，而不是*替换*搭建步骤。

**工作流程：**
1. 运行 `crewai create flow <名称>`（使用**下划线**，而不是连字符）
2. 编辑生成的 YAML 和 Python 文件以匹配你的用例
3. 运行 `crewai install` 然后运行 `crewai run`

---

## 1. 选择合适的抽象级别

crewAI 有五种常见的抽象选择。选择最简单且符合你需求的：

| 级别 | 使用场景 | 开销 | 示例 |
|---|---|---|---|
| `LLM.call()` | 单个提示、无工具、结构化提取 | 最低 | 将电子邮件解析为字段 |
| `Agent.kickoff()` | 一个带有工具和推理的 agent、无多 agent 协调 | 低 | 使用网络搜索研究一个主题 |
| `Crew.kickoff()` | 多个 agent 协作完成相关任务 | 中等 | 研究 + 写作 + 审阅的管道 |
| `Flow` 包装 crews/agents/LLM 调用 | 具有状态、路由、条件、错误处理的生成应用程序 | 完整 | 具有分支逻辑的多步骤工作流 |
| 对话式 `Flow` | 多轮对话，其中每个用户行使用相同的会话 ID 重新运行 Flow | 完整 + 实验 | 带有路由聊天、研究和升级回合的支持助手 |

### 决策流程图

```
您需要工具或多步骤推理吗？
├── 否  → LLM.call()
└── 是
    └── 您需要多个 agent 协作吗？
        ├── 否  → Agent.kickoff()
        └── 是
            └── 您需要状态管理、路由或多个 crews 吗？
                ├── 否  → Crew（但仍然作为 Flow 搭建以供未来使用）
                └── 是 → Flow + Crew(s)

用户在一个会话中发送多个聊天消息吗？
└── 是 → 对话式 Flow，使用 handle_turn(message, session_id=...)
```

**经验法则：** 对于任何生成应用程序，**始终从 Flow 开始**。你可以在 Flow 步骤中嵌入 `LLM.call()`、`Agent.kickoff()` 或 `Crew.kickoff()`。这为你提供了状态管理、错误处理和扩展空间。

对于聊天应用程序，从对话式 `Flow` 开始，而不是试图让 `Crew.kickoff()` 或 `Flow.kickoff()` 像聊天循环一样工作。对话表面是实验性的，但它是为多轮会话设计的预期 API：为每个用户行调用 `flow.handle_turn(message, session_id=...)`，或使用 `flow.chat()` 在本地终端 REPL 中。官方指南：<https://docs.crewai.com/en/guides/flows/conversational-flows>。

---

## 2. LLM.call() — 直接调用 LLM

用于简单、单轮任务，你不需要工具或 agent 推理。

```python
from crewai import LLM
from pydantic import BaseModel

class EmailFields(BaseModel):
    sender: str
    subject: str
    urgency: str

llm = LLM(model="openai/gpt-4o")

# 无 response_format — 返回字符串
raw = llm.call(messages=[{"role": "user", "content": "总结这段文本..."}])
print(raw)  # str

# 有 response_format — 直接返回 Pydantic 对象
result = llm.call(
    messages=[{"role": "user", "content": f"从这封电子邮件中提取字段：{email_text}"}],
    response_format=EmailFields
)
print(result.sender)   # str — 直接访问 Pydantic 字段
print(result.urgency)  # str
```

**不使用的情况：** 如果你需要工具、多步骤推理或重试 — 使用 Agent。

---

## 3. Agent.kickoff() — 单个 Agent 执行

当你需要一个带有工具和推理的 agent，但不需要多 agent 协调时使用。

```python
from crewai import Agent
from crewai_tools import SerperDevTool
from pydantic import BaseModel

class ResearchFindings(BaseModel):
    main_points: list[str]
    key_technologies: list[str]

researcher = Agent(
    role="AI 研究员",
    goal="研究最新的 AI 发展",
    backstory="经验丰富的 AI 研究员，具有深厚的专业知识。",
    llm="openai/gpt-4o",       # 可选：默认为 OPENAI_MODEL_NAME 环境变量或 "gpt-4"
    tools=[SerperDevTool()],
)

# 非结构化输出
result = researcher.kickoff("最新的 LLM 发展是什么？")
print(result.raw)            # str
print(result.usage_metrics)  # token 使用情况

# 带有 response_format 的结构化输出
result = researcher.kickoff(
    "总结最新的 AI 发展",
    response_format=ResearchFindings,
)
print(result.pydantic.main_points)
```

> **注意：** `Agent.kickoff()` 包装了结果 — 通过 `result.pydantic` 访问结构化输出。这与 `LLM.call()` 不同，`LLM.call()` 直接返回 Pydantic 对象。

**不使用的情况：** 如果你需要多个 agent 互相传递上下文 — 使用 Crew。

---

## 4. CLI 搭建参考

如上所述：**绝对不要跳过 `crewai create flow`。** 本节记录了 CLI 生成的文件，以便你知道要修改什么 — 不是让你手动重新创建它。

```bash
crewai create flow my_project
```

> **警告：** 项目名称中始终使用**下划线**，而不是连字符。`crewai create flow my-project` 创建的目录不是有效的 Python 标识符，在导入时会导致 `ModuleNotFoundError`。使用 `my_project` 而不是。

这会生成：

```
my_project/
├── src/my_project/
│   ├── crews/
│   │   └── my_crew/
│   │       ├── config/
│   │       │   ├── agents.yaml    # Agent 定义（角色、目标、背景故事）
│   │       │   └── tasks.yaml     # 任务定义（描述、预期输出）
│   │       └── my_crew.py         # Crew 类与 @CrewBase
│   ├── tools/
│   │   └── custom_tool.py
│   ├── main.py                    # Flow 类与 @start/@listen
│   └── ...
├── .env                           # API 密钥（OPENAI_API_KEY 等）
└── pyproject.toml
```

> **不要**使用 `crewai create crew`，除非你确定你永远不会需要路由、状态或多个 crews。优先使用 `crewai create flow` 作为默认选项。

---

## 5. YAML 配置 (agents.yaml & tasks.yaml)

搭建使用 YAML 文件进行 agent 和任务定义。这将配置与代码分离，并支持 `{variable}` 插值。

### agents.yaml

```yaml
researcher:
  role: >
    {topic} 高级数据研究员
  goal: >
    揭示 {topic} 的尖端发展
  backstory: >
    你是一位经验丰富的研究员，擅长发现 {topic} 的最新发展。
  # 可选覆盖：
  # llm: openai/gpt-4o
  # max_iter: 20
  # max_rpm: 10

reporting_analyst:
  role: >
    {topic} 报告分析师
  goal: >
    基于对 {topic} 的研究发现的详细报告
  backstory: >
    你是一位一丝不苟的分析师，擅长将复杂数据转化为清晰、可操作的报告。
```

### tasks.yaml

```yaml
research_task:
  description: >
    深入研究 {topic}。
    确定关键趋势、突破性技术以及潜在的行业影响。
  expected_output: >
    一份详细报告，分析 {topic} 顶尖 5 项发展，包括来源和影响。
  agent: researcher

reporting_task:
  description: >
    审阅研究并创建关于 {topic} 的综合报告。
  expected_output: >
    一份格式为 markdown 的精炼报告，每个关键发现都有章节。
  agent: reporting_analyst
  output_file: output/report.md
```

**关键规则：**
- `{variable}` 占位符在运行时通过 `crew.kickoff(inputs={...})` 进行替换
- `expected_output` 始终是一个**字符串**（永远不会是 Pydantic 类名）
- `agent` 值必须匹配 `agents.yaml` 中的 agent 键
- 在 `Process.sequential` 中，每个任务自动接收所有先前的任务输出作为上下文
- 对于非顺序依赖，使用 `context=[other_task]` 明确传递输出

---

## 6. 连接它们 — crew.py

`@CrewBase` 装饰器自动加载 YAML 配置文件并收集 `@agent` 和 `@task` 方法。

```python
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool

@CrewBase
class ResearchCrew:
    """研究和报告 crew."""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def researcher(self) -> Agent:
        return Agent(
            config=self.agents_config["researcher"],
            tools=[SerperDevTool()],
        )

    @agent
    def reporting_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config["reporting_analyst"],
        )

    @task
    def research_task(self) -> Task:
        return Task(config=self.tasks_config["research_task"])

    @task
    def reporting_task(self) -> Task:
        return Task(
            config=self.tasks_config["reporting_task"],
            context=[self.research_task()],  # 显式依赖（顺序中可选）
            output_file="output/report.md",
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,  # 自动收集 by @agent
            tasks=self.tasks,    # 自动收集 by @task
            process=Process.sequential,
            verbose=True,
        )
```

**重要：** 方法名称必须与 YAML 键匹配。`def researcher(self)` 映射到 `agents.yaml` 中的 `researcher:` 键。

---

## 7. Flow — 生成应用程序的基础

Flow 是构建 crewAI 生成应用程序的推荐方式。它们提供状态管理、条件路由、人工参与和持久化 — 将 crews、agents 和 LLM 调用包装成一个连贯的工作流。

### 基本 Flow — main.py

```python
from crewai.flow.flow import Flow, listen, start
from pydantic import BaseModel
from .crews.research_crew.research_crew import ResearchCrew

class ResearchState(BaseModel):
    topic: str = ""
    report: str = ""

class ResearchFlow(Flow[ResearchState]):

    @start()
    def begin(self):
        print(f"开始研究：{self.state.topic}")

    @listen(begin)
    def run_research(self):
        result = ResearchCrew().crew().kickoff(
            inputs={"topic": self.state.topic}
        )
        self.state.report = result.raw

def kickoff():
    flow = ResearchFlow()
    flow.kickoff(inputs={"topic": "AI Agents"})

if __name__ == "__main__":
    kickoff()
```

**关键点：**
- `flow.kickoff(inputs={"topic": "AI Agents"})` 填充 `self.state.topic`（键必须匹配 Pydantic 字段名称）。YAML 中的 `{variable}` 替换发生在稍后，当你在一个 Flow 步骤中调用 `crew.kickoff(inputs={"topic": self.state.topic})` 时。链式为：**flow 输入 → 状态 → crew 输入 → YAML 替换**。
- 每个 `@listen` 方法在其依赖完成后运行
- 状态在所有 Flow 步骤中持续存在 — 使用它来在 crews 之间传递数据

### 状态管理 — 结构化 vs 非结构化

**结构化（推荐用于生成）：**
```python
from pydantic import BaseModel

class MyState(BaseModel):
    topic: str = ""
    research: str = ""
    draft: str = ""
    approved: bool = False

class MyFlow(Flow[MyState]):
    ...
```

**非结构化（快速原型）：**
```python
class MyFlow(Flow):  # 无类型参数 — 状态是一个字典
    @start()
    def begin(self):
        self.state["topic"] = "AI"  # 字典风格访问
```

使用结构化状态以获得类型安全、IDE 自动完成和验证。仅在使用非结构化原型时使用。

### 在 Flow 中使用 Agent.kickoff()（常见模式）

许多生成 Flow 完全跳过 Crews，并通过 `Agent.kickoff()` 进行单个 agents 的编排。这为你提供了细粒度控制 — 每个 Flow 步骤调用特定的 agent，传递状态并存储结果。Flow 处理编排；agents 处理推理。

```python
from crewai import Agent, LLM
from crewai.flow.flow import Flow, listen, start
from crewai_tools import SerperDevTool, ScrapeWebsiteTool
from pydantic import BaseModel

class ResearchState(BaseModel):
    query: str = ""
    raw_research: str = ""
    analysis: str = ""
    report: str = ""

class DeepResearchFlow(Flow[ResearchState]):

    @start()
    def fetch_data_a(self):
        ...

    @start()
    def fetch_data_b(self):
        ...

    # 当两个获取都完成时运行
    @listen(and_(fetch_data_a, fetch_data_b))
    def merge_results(self):
        ...

    # 当任一源提供数据时运行
    @listen(or_(fetch_data_a, fetch_data_b))
    def process_first_available(self):
        ...
```

### 在 Flow 中混合抽象

一个 Flow 可以在单个工作流中组合所有 crewAI 抽象：

```python
class ProductFlow(Flow[ProductState]):

    @start()
    def classify_request(self):
        # LLM.call() 用于简单分类
        llm = LLM(model="openai/gpt-4o")
        self.state.category = llm.call(
            messages=[{"role": "user", "content": f"分类：{self.state.request}"}],
            response_format=Category
        ).category

    @router(classify_request)
    def route_by_category(self):
        if self.state.category == "simple":
            return "quick_answer"
        return "deep_research"

    @listen("quick_answer")
    def handle_simple(self):
        # Agent.kickoff() 用于单 agent 工作
        agent = Agent(role="助手", goal="快速回答", backstory="...")
        result = agent.kickoff(self.state.request)
        self.state.answer = result.raw

    @listen("deep_research")
    def handle_complex(self):
        # Crew.kickoff() 用于多 agent 协作
        result = ResearchCrew().crew().kickoff(
            inputs={"topic": self.state.request}
        )
        self.state.answer = result.raw
```

**为什么这种模式效果很好：**
- 每个 agent 都为它的步骤而设计 — 窄角色、特定工具
- Flow 管理状态和顺序 — 无 crew 开销
- 容易在步骤之间添加路由、人工审查或重试逻辑
- 你可以自由混合 `Agent.kickoff()`、`LLM.call()` 和 `Crew.kickoff()`

**何时使用 Agent.kickoff() vs Crew.kickoff() 在 Flow 中：**

| 使用 `Agent.kickoff()` 当 | 使用 `Crew.kickoff()` 当 |
|---|---|
| 每个步骤是一个具有不同工具的 agent | 多个 agent 需要协作完成一个任务 |
| 你想 Flow 控制顺序 | Agents 需要在步骤内传递上下文 |
| 步骤是独立的，不需要跨 agent 委托 | 你需要分层流程，有一个管理器 |
| 你想对步骤之间的数据流进行最大控制 | 子工作流是自包含的且可重用 |

### 在 Flow 中使用带有结构化输出的 Agent.kickoff()

将 `response_format` 与状态结合使用，以在 agents 之间进行类型化的数据流：

```python
class Insights(BaseModel):
    key_points: list[str]
    recommendations: list[str]
    confidence: float

class AnalysisFlow(Flow[AnalysisState]):

    @start()
    def research(self):
        """研究 {topic} 趋势，针对 {current_year}，
        目标受众为 {target_audience}."""
        result = self.research_agent().kickoff(
            f"研究 {self.state.topic}",
            response_format=Insights,
        )
        # result.pydantic 给你一个类型的 Insights 对象
        self.state.key_points = result.pydantic.key_points
        self.state.recommendations = result.pydantic.recommendations
```

### 在 Flow 中混合抽象

一个 Flow 可以在单个工作流中组合所有 crewAI 抽象：

```python
class ProductFlow(Flow[ProductState]):

    @start()
    def classify_request(self):
        # LLM.call() 用于简单分类
        llm = LLM(model="openai/gpt-4o")
        self.state.category = llm.call(
            messages=[{"role": "user", "content": f"分类：{self.state.request}"}],
            response_format=Category
        ).category

    @router(classify_request)
    def route_by_category(self):
        if self.state.category == "simple":
            return "quick_answer"
        return "deep_research"

    @listen("quick_answer")
    def handle_simple(self):
        # Agent.kickoff() 用于单 agent 工作
        agent = Agent(role="助手", goal="快速回答", backstory="...")
        result = agent.kickoff(self.state.request)
        self.state.answer = result.raw

    @listen("deep_research")
    def handle_complex(self):
        # Crew.kickoff() 用于多 agent 协作
        result = ResearchCrew().crew().kickoff(
            inputs={"topic": self.state.request}
        )
        self.state.answer = result.raw
```

### Flow 路由使用 `@router`

使用 `@router` 进行条件分支 — 返回一个字符串标签，并且 `@listen("label")` 绑定到分支：

```python
from crewai.flow.flow import Flow, listen, router, start, or_
class QualityFlow(Flow[QAState]):

    @start()
    def generate_draft(self):
        result = WriterCrew().crew().kickoff(inputs={"topic": self.state.topic})
        self.state.draft = result.raw

    @router(generate_draft)
    def check_quality(self):
        llm = LLM(model="openai/gpt-4o")
        score = llm.call(
            messages=[{"role": "user", "content": f"评估 1-10：{self.state.draft}"}],
            response_format=QualityScore
        )
        if score.rating >= 7:
            return "approved"
        return "needs_revision"

    @listen("approved")
    def publish(self):
        self.state.published = True

    @listen("needs_revision")
    def revise(self):
        feedback = self.last_human_feedback
        # 使用 feedback.feedback_text 进行修订
        ...
```

### Flow 可视化

```python
flow = MyFlow()
flow.plot()             # 在笔记本中显示
flow.plot("my_flow")    # 保存为 my_flow.png
```

---

## 8. 使用 `inputs` 进行变量插值

`{variable}` 模式是如何使 crews 可重用的。

```python
# 变量通过：kickoff → YAML 模板 → agent/task 提示
crew.kickoff(inputs={
    "topic": "AI Agents",
    "current_year": "2025",
    "target_audience": "开发者",
})
```

在 YAML 中，`{topic}` 和 `{current_year}` 被替换：

```yaml
research_task:
  description: >
    研究 {topic} 趋势，针对 {current_year}，
    目标受众为 {target_audience}.
```

**常见错误：**
- 忘记传递在 YAML 中引用的变量 → 结果中会出现 `{variable}`
- 使用 Jinja2 语法 `{{ }}` 而不是单花括号 `{ }` → crewAI 使用单花括号
- 传递不匹配任何 YAML 占位符的变量 → 静默忽略

---

## 9. 运行你的项目

```bash
# 安装依赖项
crewai install

# 运行 Flow
crewai run
```

或者直接运行：

```bash
cd my_project
uv run src/my_project/main.py
```

---

## 10. 快速诊断检查清单

| 症状 | 可能的原因 | 修复 |
|---|---|---|
| `{topic}` 出现在 agent 输出中 | 在 `kickoff()` 中缺少 `inputs=` | 传递 `crew.kickoff(inputs={"topic": "..."})` |
| 在 `self.agents_config['name']` 上出现 `KeyError` | 方法名称与 YAML 键不匹配 | 确保 `@agent def researcher` 匹配 YAML 中的 `researcher:` |
| 导入时出现 `ModuleNotFoundError` | 路径错误或项目名称中使用了连字符 | 使用下划线；检查 `from .crews.crew_name.crew_name import CrewClass` |
| Crew 运行但 Flow 状态为空 | 没有将结果写回 `self.state` | 在 `@listen` 方法中将 crew 输出分配给 `self.state.field` |
| `Process.SEQUENTIAL` 抛出 `AttributeError` | 大写枚举 | 使用小写：`Process.sequential` |
| Agent 忽略工具 | 工具分配给 agent 但任务需要它们 | 将工具移动到任务级别或验证 agent 拥有正确的工具 |
| Agent 虚构搜索结果 | 未分配工具 — agent 无法实际搜索 | 添加 `tools=[SerperDevTool()]` 或等效项；没有工具的 agent 将虚构数据 |
| `@listen` 从不触发 | 路由器返回值与监听器字符串不匹配，或者传递了一个字符串而不是方法引用 | `@router` 必须返回 `@listen("label")` 期望的字符串；对于方法链使用 `@listen(method_ref)` 考虑使用 `@listen("method_name")` |
| Flow 步骤意外运行两次 | 多个 `@start()` 方法或 `or_` 监听器 | 使用 `and_()` 如果你需要所有上游步骤首先完成 |
| `AuthenticationError` 或 `API key not found` | 缺少环境变量 | 在 `.env` 中设置 `OPENAI_API_KEY`（以及 `SERPER_API_KEY` 对于搜索工具） |
| Agent 在结构化输出上无限重试 | Pydantic 模型对 LLM 太复杂 | 简化模型，减少嵌套，或使用更强大的 `llm` |
| Agent 在达到 `max_iter` 时无限循环而没有完成 | 任务描述太模糊或与 `expected_output` 冲突 | 使 `expected_output` 具体且可实现；降低 `max_iter` 以更快地失败 |
| Agent 无限循环到 `max_iter` 考虑没有完成 | 任务描述太模糊或与 `expected_output` 冲突 | 使 `expected_output` 具体且可实现；降低 `max_iter` 以更快地失败 |
| Flow 状态在步骤之间未更新 | 使用非结构化状态而没有正确的键访问 | 切换到结构化的 Pydantic 状态或确保字典键一致 |
| `@router` 返回值被忽略 | 方法没有用 `@router` 装饰 | 使用 `@router(condition)` 考虑使用 `@listen(condition)` 对于分支方法 |
| `Flow.kickoff(user_message=..., session_id=...)` 失败 | `kickoff()` 不接受对话 kwargs | 使用 `flow.handle_turn(message, session_id=...)` 对于聊天消息 |
| 聊天历史中缺少 assistant 回复 | 处理器返回文本但未在较旧的显式路径中记录它 | 在路由处理程序中调用 `self.append_assistant_message(reply)` |
| 聊天会话的跟踪从未导出 | 延迟对话跟踪未最终确定 | 在 `finally` 中调用 `flow.finalize_session_traces()`，或使用 `flow.chat()` |
| 使用 `@human_feedback` 模型进行后续聊天 | 人工反馈批准了一个步骤的输出，而不是下一个用户消息 | 使用对话式 `handle_turn()` 对于后续聊天行 |

---

## 参考

对于更深入地了解特定主题，请参阅：

- [Flow 路由、持久化、流式传输 & 人工反馈](references/flow-routing.md) — 完整 `@router`, `or_()`, `and_()`, `@persist`, 流式传输和 `@human_feedback` 模式
- [对话式 Flow](references/conversational-flows.md) — 实验性的多轮 Flow API，具有 `handle_turn()`, `chat()`, `ConversationConfig`, 路由行为，持久化和跟踪指南
- [MCP 服务器](references/mcp-servers.md) — 优先使用官方 MCP 服务器而不是原生工具；设置、DSL 集成和已知的官方服务器
- [工具目录](references/tools-catalog.md) — 所有 80 多个内置工具，包括导入、环境变量和常见组合（当没有 MCP 服务器存在时使用作为后备）

对于相关技能：

- **design-agent** — agent 角色-目标-背景故事框架，参数调整，工具分配，内存 & 知识配置
- **design-task** — 任务描述/预期输出最佳实践，约束，结构化输出，依赖
- **ask-docs** — 查询实时 CrewAI 文档 MCP 服务器以回答未涵盖的问题
