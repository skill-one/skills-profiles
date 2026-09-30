---
name: getting-started
description: CrewAI 架构决策和项目脚手架。在开始新的 crewAI 项目时使用，选择 LLM.call()、Agent.kickoff()、Crew.kickoff() 或 Flow 之间的差异，使用 'crewai create flow' 进行脚手架搭建，配置 YAML 配置文件（agents.yaml、tasks.yaml），连接 @CrewBase crew.py，编写带有 @start/@listen 的 Flow main.py，使用 handle_turn()/chat() 构建实验性对话 Flow，或使用 {variable} 插值。
---

# CrewAI 入门指南与架构

如何选择合适的抽象级别、搭建项目以及将所有内容连接起来。

---

## 必须的工作流程 — 首先阅读此内容

**绝对不要手动创建 crewAI 项目文件。** 始终使用 CLI 进行搭建：

```bash
crewai create flow <项目名称>
```

这是**非可选**的。即使你只需要一个 crew，即使你熟悉文件结构 — 首先运行 CLI，然后修改生成的文件。不要从零开始手动编写 `main.py`、`crew.py`、`agents.yaml`、`tasks.yaml` 或 `pyproject.toml`。

> **原因：** CLI 设置了正确的导入、目录结构、pyproject.toml 配置和模板代码，手动进行时很容易出现细微的错误。下面的参考材料将教你这些组件是如何工作的，以便你可以*修改*搭建的代码，而不是*替换*搭建步骤。

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
| `Crew.kickoff()` | 多个 agent 协作处理相关任务 | 中等 | 研究 + 写作 + 审阅流程 |
| 包裹 crews/agents/LLM 调用的 `Flow` | 具有状态、路由、条件语句、错误处理的生成应用程序 | 完整 | 具有分支逻辑的多步骤工作流 |
| 对话式 `Flow` | 多轮聊天，其中每个用户行重新运行具有相同会话 ID 的 Flow | 完整 + 实验 | 具有路由聊天、研究和升级步骤的支持助手 |

### 决策流程图

```
你需要工具或多步骤推理吗？
├── 否  → LLM.call()
└── 是
    └── 你需要多个 agent 协作吗？
        ├── 否  → Agent.kickoff()
        └── 是
            └── 你需要状态管理、路由或多个 crews 吗？
                ├── 否  → Crew（但仍然作为 Flow 搭建以供未来使用）
                └── 是 → Flow + Crew(s)

用户在一个会话中发送多个聊天消息吗？
└── 是 → 对话式 Flow，使用 handle_turn(message, session_id=...)
```

**经验法则：** 对于任何生成应用程序，**始终从 Flow 开始**。你可以在 Flow 步骤中嵌入 `LLM.call()`、`Agent.kickoff()` 或 `Crew.kickoff()`。这为你提供了状态管理、错误处理和扩展空间。

对于聊天应用程序，从对话式 `Flow` 开始，而不是试图让 `Crew.kickoff()` 或 `Flow.kickoff()` 像聊天循环一样工作。对话界面是实验性的，但它是为多轮会话的预期 API：为每个用户行调用 `flow.handle_turn(message, session_id=...)`，或使用 `flow.chat()` 在本地终端 REPL 中。官方指南：<https://docs.crewai.com/en/guides/flows/conversational-flows>。

---

## 2. LLM.call() — 直接 LLM 调用

用于简单、单轮的任务，其中不需要工具或 agent 推理。

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

**不使用场景：** 如果你需要工具、多步骤推理或重试 — 使用 Agent。

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
    backstory="一位经验丰富的 AI 研究员，具有深厚的专业知识。",
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

**不使用场景：** 如果你需要多个 agent 互相传递上下文 — 使用 Crew。

---

## 4. CLI 搭建参考

如上所述：**绝对不要跳过 `crewai create flow`。** 本节记录了 CLI 生成的内容，以便你知道要修改什么 — 不是让你手动重新创建它。

```bash
crewai create flow my_project
```

> **警告：** 项目名称中始终使用**下划线**，而不是连字符。`crewai create flow my-project` 创建的目录不是一个有效的 Python 标识符，在导入时会导致 `ModuleNotFoundError`。使用 `my_project` 而不是。

这会生成：

```
my_project/
├── src/my_project/
│   ├── crews/
│   │   └── my_crew/
│   │       ├── config/
│   │       │   ├── agents.yaml    # Agent 定义（角色、目标、背景）
│   │       │   └── tasks.yaml     # Task 定义（描述、预期输出）
│   │       └── my_crew.py         # Crew 类与 @CrewBase
│   ├── tools/
│   │   └── custom_tool.py
│   ├── main.py                    # Flow 类与 @start/@listen
│   └── ...
├── .env                           # API 密钥（OPENAI_API_KEY 等）
└── pyproject.toml
```

> **不要**使用 `crewai create crew`，除非你确定你永远不会需要路由、状态或多个 crews。优先选择 `crewai create flow` 作为默认选项。

---

## 5. YAML 配置 (agents.yaml & tasks.yaml)

搭建使用 YAML 文件进行 agent 和 task 定义。这将配置与代码分离，并支持 `{variable}` 插值。

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
    基于对 {topic} 的研究，创建详细报告
  backstory: >
    你是一位细致的分析师，擅长将复杂数据转化为清晰、可操作的报告。
```

### tasks.yaml

```yaml
research_task:
  description: >
    对 {topic} 进行彻底研究。
    确定关键趋势、突破性技术以及潜在的行业影响。
  expected_output: >
    一份详细报告，分析 {topic} 顶部 5 项发展，包括来源和影响。
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
- 在 `Process.sequential` 中，每个 task 自动接收所有先前的 task 输出作为上下文
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
            agents=self.agents,  # 自动收集 @agent
            tasks=self.tasks,    # 自动收集 @task
            process=Process.sequential,
            verbose=True,
        )
```

**重要：** 方法名称必须与 YAML 键匹配。`def researcher(self)` 映射到 `agents.yaml` 中的 `researcher:` 键。

---

## 7. Flows — 生成应用程序的基础

Flows 是构建 crewAI 生成应用程序的推荐方式。它们提供状态管理、条件路由、人工参与和持久性 — 将 crews、agents 和 LLM 调用包装成一个连贯的工作流。

### 基本流程 — main.py

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
- `flow.kickoff(inputs={"topic": "AI Agents"})` 填充 `self.state.topic`（键必须匹配 Pydantic 字段名）。YAML `{variable}` 替换稍后发生，当你在 Flow 步骤中调用 `crew.kickoff(inputs={"topic": self.state.topic})` 时。链是：**flow inputs → state → crew inputs → YAML 替换**。
- 每个 `@listen` 方法在其依赖完成后运行
- 状态在所有 Flow 步骤中持续存在 — 使用它来在 crews 之间传递数据

### 状态管理 — 结构化与非结构化

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
        self.state["topic"] = "AI"  # 字典式访问
```

使用结构化状态以获得类型安全、IDE 自动完成和验证。仅用于一次性原型使用非结构化。

### 在 Flows 中使用 Agent.kickoff()（常见模式）

许多生成 Flow 完全跳过 Crews，并通过 `Agent.kickoff()` 进行单个 agent 的编排。这为你提供了细粒度控制 — 每个 Flow 步骤调用特定的 agent，传递状态并存储结果。Flow 处理编排；agent 处理推理。

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
    def gather_research(self):
        """带有工具的 agent 执行实际搜索。"""
        researcher = Agent(
            role="高级研究分析师",
            goal="找到关于给定主题的全面、事实性信息",
            backstory="你是一位专家研究员，始终引用来源并标记不确定性。",
            tools=[SerperDevTool(), ScrapeWebsiteTool()],
            llm="openai/gpt-4o",
        )
        result = researcher.kickoff(
            f"彻底研究这个主题：{self.state.query}"
        )
        self.state.raw_research = result.raw

    @listen(gather_research)
    def analyze_findings(self):
        """另一个 agent 分析原始研究 — 不需要工具。"""
        analyst = Agent(
            role="数据分析师",
            goal="提取关键见解、模式和可操作的推荐",
            backstory="你将原始数据转化为清晰、结构化的分析。",
            llm="openai/gpt-4o",
        )
        result = analyst.kickoff(
            f"分析这些研究发现的并提取关键见解：\n\n{self.state.raw_research}"
        )
        self.state.analysis = result.raw

    @listen(analyze_findings)
    def write_report(self):
        """一个写作 agent 生成最终交付物。"""
        writer = Agent(
            role="技术作家",
            goal="为非技术人员生成清晰、可操作的报告",
            backstory="你擅长使复杂信息易于理解。",
            llm="openai/gpt-4o",
        )
        result = writer.kickoff(
            f"基于这个分析撰写一份综合报告：\n\n{self.state.analysis}"
        )
        self.state.report = result.raw
```

**为什么这种模式效果很好：**
- 每个agent 都针对其步骤进行设计 — 窄角色、特定工具
- Flow 管理状态和顺序 — 无 crew 开销
- 容易在步骤之间添加路由、人工审查或重试逻辑
- 你可以自由混合 `Agent.kickoff()`、`LLM.call()` 和 `Crew.kickoff()`

**何时在 Flow 中使用 Agent.kickoff() 而不是 Crew.kickoff()：**

| 使用 `Agent.kickoff()` 时 | 使用 `Crew.kickoff()` 时 |
|---|---|
| 每个步骤都是一个具有不同工具的 agent | 多个 agent 需要协作处理一个任务 |
| 你希望 Flow 控制顺序 | agent 需要在步骤内传递上下文 |
| 步骤是独立的，不需要跨 agent 委托 | 你需要分层流程，有一个管理者 |
| 你希望最大限度地控制步骤之间的数据流 | 子工作流是自包含的且可重用 |

### Flow 中的 Agent.kickoff() 与结构化输出

结合 `response_format` 与状态以在 agent 之间进行类型化数据流：

```python
class Insights(BaseModel):
    key_points: list[str]
    recommendations: list[str]
    confidence: float

class AnalysisFlow(Flow[AnalysisState]):

    @start()
    def research(self):
        """研究员 agent 进行实际搜索。"""
        researcher = Agent(role="研究员", goal="...", backstory="...", tools=[SerperDevTool()])
        result = researcher.kickoff(
            f"研究 {self.state.topic}",
            response_format=Insights,
        )
        # result.pydantic 给你一个类型的 Insights 对象
        self.state.key_points = result.pydantic.key_points
        self.state.recommendations = result.pydantic.recommendations
```

### 在 Flow 中混合抽象

一个 Flow 可以将所有 crewAI 概念合并到一个工作流中：

```python
class ProductFlow(Flow[ProductState]):

    @start()
    def classify_request(self):
        # 使用 LLM.call() 进行简单分类
        llm = LLM(model="openai/gpt-4o")
        self.state.category = llm.call(
            messages=[{"role": "user", "content": f"分类: {self.state.request}"}],
            response_format=Category
        ).category

    @router(classify_request)
    def route_by_category(self):
        if self.state.category == "简单":
            return "快速回答"
        return "深入研究"

    @listen("快速回答")
    def handle_simple(self):
        # 使用 Agent.kickoff() 进行单代理工作
        agent = Agent(role="助手", goal="快速回答", backstory="...")
        result = agent.kickoff(self.state.request)
        self.state.answer = result.raw

    @listen("深入研究")
    def handle_complex(self):
        # 使用 Crew.kickoff() 进行多代理协作
        result = ResearchCrew().crew().kickoff(
            inputs={"主题": self.state.request}
        )
        self.state.answer = result.raw
```

### 使用 `@router` 进行 Flow 路由

使用 `@router` 进行条件分支——返回一个字符串标签，`@listen("标签")` 绑定到分支：

```python
from crewai.flow.flow import Flow, listen, router, start, or_

class QualityFlow(Flow[QAState]):

    @start()
    def generate_content(self):
        result = WriterCrew().crew().kickoff(inputs={"主题": self.state.topic})
        self.state.draft = result.raw

    @router(generate_content)
    def check_quality(self):
        llm = LLM(model="openai/gpt-4o")
        score = llm.call(
            messages=[{"role": "user", "content": f"评分1-10: {self.state.draft}"}],
            response_format=QualityScore
        )
        if score.rating >= 7:
            return "批准"
        return "需要修改"

    @listen("批准")
    def publish(self):
        self.state.published = True

    @listen("需要修改")
    def revise(self):
        result = EditorCrew().crew().kickoff(
            inputs={"草稿": self.state.draft}
        )
        self.state.draft = result.raw
```

### 使用 `or_()` 和 `and_()` 合并分支

```python
from crewai.flow.flow import Flow, listen, start, or_, and_

class ParallelFlow(Flow[MyState]):

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

### 使用 `@persist` 进行 Flow 持久化

对于需要重启后继续运行的长时间工作流：

```python
from crewai.flow.flow import Flow, start, listen, persist
from crewai.flow.persistence import SQLiteFlowPersistence

@persist(SQLiteFlowPersistence())  # 类级别：持久化所有方法
class LongRunningFlow(Flow[MyState]):

    @start()
    def step_one(self):
        self.state.data = "已处理"

    @listen(step_one)
    def step_two(self):
        # 如果在此处崩溃，使用相同的状态 ID 重新启动将从中继续
        ...
```

### 使用 `handle_turn()` 进行对话式 Flow（实验性）

当产品是一个聊天会话时，使用对话式 `Flow`：支持助手、路由研究助手、引导向导或任何用户发送多个回合的 UI。

核心模型：
- 每个用户消息是一个**新的 Flow 运行**，具有**相同的会话 ID**
- `handle_turn(message, session_id=...)` 将用户行追加到 `state.messages`，重置每回合执行跟踪，并内部调用 `kickoff(inputs={"id": session_id})`
- `Flow.kickoff()` 不接受 `user_message=` 或 `session_id=` 关键字参数
- 使用 `route_turn()` 加上 `@listen("ROUTE")` 处理器进行聊天回合路由
- 在处理器中调用 `append_assistant_message(reply)`，以便下一个回合看到助手历史记录
- 将拥有的循环包装在 `try/finally` 中并调用 `finalize_session_traces()`；`flow.chat()` 为本地 REPL 执行此操作

```python
from uuid import uuid4

from crewai import Agent, Flow
from crewai.flow import listen
from crewai.experimental.conversational import (
    ConversationConfig,
    ConversationState,
)


@ConversationConfig(defer_trace_finalization=True)
class SupportFlow(Flow[ConversationState]):
    conversational = True

    def research_agent(self) -> Agent:
        return Agent(
            role="支持研究专家",
            goal="使用准确来源回答用户当前的研究问题。",
            backstory="你精确、以证据为驱动，并对不确定性明确说明。",
            tools=[...],
        )

    def route_turn(self, context):
        message = (self.state.current_user_message or "").lower()
        if "docs" in message or "crewai" in message:
            return "CREWAI_DOCS"
        if "research" in message or "search" in message:
            return "RESEARCH"
        return "对话"

    @listen("CREWAI_DOCS")
    def handle_docs(self):
        """查找 CrewAI 文档以回答框架/API 问题。"""
        reply = "我会在 CrewAI 文档中查询。"
        self.append_assistant_message(reply)
        return reply

    @listen("RESEARCH")
    def handle_research(self):
        """新鲜的研究、当前查找和工具支持的调查。"""
        result = self.research_agent().kickoff(self.state.current_user_message)
        reply = result.raw
        self.append_assistant_message(reply)
        return reply


flow = SupportFlow()
session_id = str(uuid4())

try:
    flow.handle_turn("你能做什么？", session_id=session_id)
    flow.handle_turn("检查 CrewAI 文档以获取工作流信息。", session_id=session_id)
finally:
    flow.finalize_session_traces()
```

使用 `RouterConfig` 时，您希望使用 LLM 驱动的路由。路由目录自动从 `@listen("ROUTE")` 处理器和它们的 docstrings 构建，因此不要在路由提示中重复路由列表。

请参阅 [对话式 Flow](references/conversational-flows.md) 了解完整生命周期、路由、持久化和跟踪指南。

### 使用 `@human_feedback` 进行人机交互

```python
from crewai.flow.flow import Flow, start, listen, router
from crewai.flow.human_feedback import human_feedback

class ApprovalFlow(Flow[ReviewState]):

    @start()
    def generate_draft(self):
        result = WriterCrew().crew().kickoff(inputs={"主题": self.state.topic})
        self.state.draft = result.raw

    @human_feedback(
        message="审阅草稿并提供反馈",
        emit=["批准", "需要修改"],
        llm="openai/gpt-4o",
        default_outcome="批准"
    )
    @listen(generate_draft)
    def review_step(self):
        return self.state.draft

    @listen("批准")
    def publish(self):
        ...

    @listen("需要修改")
    def revise(self):
        feedback = self.last_human_feedback
        # 使用 feedback.feedback_text 进行修改
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

`{变量}` 模式是使 crews 可重用的方式。

```python
# 变量通过：kickoff → YAML 模板 → 代理/任务提示
crew.kickoff(inputs={
    "主题": "AI 代理",
    "当前年份": "2025",
    "目标受众": "开发者",
})
```

在 YAML 中，`{主题}` 和 `{当前年份}` 被替换：

```yaml
research_task:
  description: >
    研究 {主题} 趋势，针对 {当前年份}，
    目标受众为 {目标受众}.
```

**常见错误：**
- 忘记传递在 YAML 中引用的变量 → 结果在提示中显示为字面量 `{变量}`
- 使用 Jinja2 语法 `{{ }}` 而不是单花括号 `{ }` → crewAI 使用单花括号
- 传递与任何 YAML 占位符不匹配的变量 → 静默忽略

---

## 9. 运行您的项目

```bash
# 安装依赖
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

## 10. 快速诊断清单

| 症状 | 可能原因 | 解决方法 |
|---|---|---|
| `{主题}` 出现在代理输出中作为字面量 | `kickoff()` 中缺少 `inputs=` | 传递 `crew.kickoff(inputs={"主题": "..."})` |
| 在 `self.agents_config['name']` 上出现 `KeyError` | 方法名称与 YAML 键不匹配 | 确保 `@agent def researcher` 与 YAML 中的 `researcher:` 匹配 |
| 导入时出现 `ModuleNotFoundError` | 错误的路径或项目名称中的连字符 | 使用下划线；检查 `from .crews.crew_name.crew_name import CrewClass` |
| Crew 运行但 Flow 状态为空 | 没有将结果写回 `self.state` | 在 `@listen` 方法中将 crew 输出分配给 `self.state.field` |
| `Process.SEQUENTIAL` 抛出 `AttributeError` | 大写枚举 | 使用小写：`Process.sequential` |
| 代理忽略工具 | 工具分配给代理但任务需要它们 | 将工具移到任务级别或验证代理具有正确的工具 |
| 代理编造搜索结果 | 没有分配工具——代理实际上无法搜索 | 添加 `tools=[SerperDevTool()]` 或等效工具；没有工具的代理会臆断数据 |
| `@listen` 从未触发 | 监听器字符串与路由返回值不匹配，或者传递了字符串而不是方法引用 | `@router` 必须返回 `@listen("标签")` 期望的确切字符串；对于方法链使用 `@listen(method_ref)` 而不是 `@listen("method_name")` |
| Flow 步骤意外运行两次 | 多个 `@start()` 方法或 `or_` 监听器 | 如果需要所有上游步骤首先完成，请使用 `and_()` |
| `AuthenticationError` 或 `API key not found` | 缺少环境变量 | 在 `.env` 中设置 `OPENAI_API_KEY`（以及 `SERPER_API_KEY` 用于搜索工具） |
| 代理在结构化输出上无限重试 | Pydantic 模型对 LLM 太复杂 | 简化模型，减少嵌套，或使用更强大的 `llm` |
| 代理达到 `max_iter` 而未完成 | 任务描述太模糊或与 `expected_output` 冲突 | 使 `expected_output` 具体且可实现；降低 `max_iter` 以更快失败 |
| Flow 状态在步骤之间未更新 | 使用非结构化状态而没有正确的键访问 | 切换到结构化 Pydantic 状态或确保字典键一致 |
| `@router` 返回值被忽略 | 方法未使用 `@router` 装饰 | 使用 `@router(condition)` 而不是 `@listen(condition)` 进行分支 |
| `Flow.kickoff(user_message=..., session_id=...)` 失败 | 对话关键字参数不被 `kickoff()` 接受 | 使用 `flow.handle_turn(message, session_id=...)` 进行聊天消息 |
| 聊天历史中缺少助手回复 | 处理器返回文本但未在较旧/显式路径上记录 | 在路由处理器中调用 `self.append_assistant_message(reply)` |
| 聊天会话的跟踪从未导出 | 延迟对话跟踪未最终确定 | 在 `finally` 中调用 `flow.finalize_session_traces()`，或使用 `flow.chat()` |
| 使用 `@human_feedback` 模型的后续聊天 | 人类反馈批准了步骤输出，而不是下一个用户消息 | 使用对话式 `handle_turn()` 进行后续聊天行 |

---

## 参考文献

对于特定主题的深入探讨，请参阅：

- [Flow 路由、持久化、流式传输与人机交互](references/flow-routing.md) — 完整的 `@router`、`or_()`、`and_()`、`@persist`、流式传输和 `@human_feedback` 模式
- [对话式 Flow](references/conversational-flows.md) — 实验性多回合 Flow API，具有 `handle_turn()`、`chat()`、`ConversationConfig`、路由行为、持久化和跟踪
- [MCP 服务器](references/mcp-servers.md) — 优先使用官方 MCP 服务器而不是原生工具；设置、DSL 集成和已知官方服务器
- [工具目录](references/tools-catalog.md) — 所有 80 多个内置工具，包括导入、环境变量和常见组合（在没有 MCP 服务器时使用作为备用）

对于相关技能：

- **design-agent** — 代理 Role-Goal-Backstory 框架、参数调整、工具分配、记忆和知识配置
- **design-task** — 任务描述/expected_output 最佳实践、护栏、结构化输出、依赖关系
- **ask-docs** — 查询实时 CrewAI 文档 MCP 服务器以获取未涵盖的问题
