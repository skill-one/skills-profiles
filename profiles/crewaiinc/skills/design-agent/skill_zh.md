# CrewAI Agent Design Guide

如何设计具有适当角色、目标、背景故事、工具和配置的有效代理。

---

## 80/20法则

**将80%的努力投入到任务设计上，20%投入到代理设计上。** 一个设计良好的任务可以提升即使是简单的代理。但即使是最好的代理也无法挽救一个模糊、范围不明确的任务。首先确保任务正确（参见`design-task`技能），然后完善代理。

---

## 0. 您实际需要多少个代理？

**默认情况下使用一个代理。** 只有当任务真正需要以下工作，才添加更多代理：

- **不同的工具或权限** — 例如，一个代理具有Slack写入权限，另一个仅读取文档。
- **LLM必须清楚地在不同角色之间切换** — 作家的声音不是研究者的声音。
- **不同的LLM** — 一个廉价的模型用于机械步骤，一个更强的模型用于综合。
- **不同的护栏或输出模式** — 分离代理使每个阶段的合同明确。

**不要因为工作流程有多个步骤就添加代理。** 一个代理可以：
- 在一个启动（kickoff）中按顺序调用多个工具（搜索→抓取→总结是一个代理的循环）。
- 在一个响应中生成结构化的多部分输出。
- 通过其自己的工具使用循环进行迭代，而无需您将其作为分离的代理进行编排。

**成本计算：** 每个额外的代理 = 至少一个更多的LLM启动加上上下文传递。将线性、单人角色的工作拆分为多个代理会成倍增加代币成本，并增加边际质量收益的脆弱性。

### 反模式：将顺序机械步骤作为单独的代理

❌ 三个代理完成一个研究员的工作：
```python
source_finder = Agent(role="通过Firecrawl搜索查找URL", tools=[firecrawl_search])
scraper       = Agent(role="通过Firecrawl抓取URL", tools=[firecrawl_scrape])
writer        = Agent(role="撰写报告", ...)
```

✅ 一个研究员进行收集循环；一个作家进行综合 — 两个代理，因为角色和LLM确实不同：
```python
researcher = Agent(role="网络研究员", tools=[firecrawl_search, firecrawl_scrape], llm="anthropic/claude-haiku-4-5")
writer     = Agent(role="技术报告作家",                                    llm="anthropic/claude-sonnet-4-6")
```
研究员的任务描述告诉它要搜索，然后抓取，然后返回结构化结果。一个LLM循环，多个工具调用。

### 反模式：“总结然后发送”作为两个代理

❌ 两个代理来读取一个字符串、总结它并在Slack上发布DM：
```python
summarizer       = Agent(role="总结者")
slack_messenger  = Agent(role="Slack发送者", apps=["slack"])
```

✅ 一个代理具有连接器，并且任务告诉它要总结，然后DM：
```python
slack_dm_agent = Agent(
    role="Slack报告者",
    goal="在Slack DM中发布包含一段话总结和完整markdown正文的内容。",
    apps=["slack"],
)
# 任务："阅读下面的报告。在顶部写一个2-3句的执行总结。
#        向{recipient_email}发送DM，总结后跟完整正文。"
```

### 启发式方法

> 如果两个“代理”具有相同的角色、相同的工具表面和相同的LLM，它们就是一个具有更长的任务描述的代理。

### 一旦您决定“一个代理就足够了”

在Flow方法中直接使用`Agent.kickoff()` — 无需`Crew`，无需`Task`仪式。Flow拥有排序和状态；每一步是一个单独的代理启动。有关完整模式，请参阅下文**第4节 — Agent.kickoff() — 直接代理执行**，以及上游文档：<https://docs.crewai.com/en/concepts/agents#direct-agent-interaction-with-kickoff>。

快速形状：

```python
@listen(previous_step)
def my_step(self):
    agent = Agent(role="…", goal="…", backstory="…", tools=[...])
    result = agent.kickoff(
        messages=f"使用这个先前的步骤输出：{self.state.prior_field}",
        response_format=MyPydanticModel,  # 可选
    )
    self.state.my_field = result.pydantic  # 或 result.raw
```

仅在步骤确实受益于多代理协作（委托、分层管理、并行专家为综合提供输入）时才使用`Crew.kickoff()`。对于“一个代理做一项工作”，在Flow监听器中的`Agent.kickoff()`是正确的原语。

只有在您决定多代理是合理的之后，才继续阅读如何设计每个代理。

---

## 1. 角色目标背景故事框架

每个代理都需要三个东西：**它是什么**、**它想要什么**以及**它为什么有资格**。

### 角色 — 代理是什么

角色定义了代理的专业领域。**要具体，不要笼统。**

| 坏 | 好 |
|---|---|
| `研究员` | `专攻{主题}的高级数据研究员` |
| `作家` | `面向开发者的技术博客作家` |
| `分析师` | `具有监管合规专业知识的金融风险分析师` |

角色直接塑造LLM的推理方式。一个“高级数据研究员”将产生与“研究助理”相同任务的不同输出。

### 目标 — 代理想要什么

目标是代理的个体目标。它应该是**结果导向的，具有质量标准**。

| 坏 | 好 |
|---|---|
| `做研究` | `发现{主题}的前沿发展，并确定支持证据和来源引用的前5个趋势` |
| `写内容` | `制作面向非技术读者的解释复杂主题的出版物准备技术文章` |
| `分析数据` | `提供具有置信水平和推荐缓解措施的可操作风险评估` |

### 背景故事 — 代理为什么有资格

背景故事建立了专业知识、经验、价值观和工作方式。它是代理的“个性提示”。

```yaml
backstory: >
  你是一位拥有15年AI/ML经验的资深研究员。
  你以能够找到晦涩但相关的论文而闻名
  并将复杂的发现综合为清晰、可操作的见解。
  你总是引用你的来源并明确标记不确定性。
```

**背景故事中应包含的内容：**
- 经验年限/深度
- 特定领域知识
- 工作方式价值观（例如，“总是引用来源”，“偏好简洁输出”）
- 代理自身持有的质量标准

**不应包含的内容：**
- 实现细节（工具、模型、配置）
- 任务特定指令（那些应放在任务描述中）
- 不影响输出质量的任意个性特征

---

## 2. 代理配置参考

### 基本参数

```python
Agent(
    role="...",              # 必填：代理的专业领域
    goal="...",              # 必填：代理旨在实现的目标
    backstory="...",         # 必填：背景和个性
    llm="openai/gpt-4o",    # 可选：默认为OPENAI_MODEL_NAME环境变量或"gpt-4"
    tools=[...],             # 可选：工具实例列表
)
```

### 执行控制

```python
Agent(
    ...,
    max_iter=25,             # 每个任务的最大推理迭代次数（默认：25）
    max_execution_time=300,  # 超时秒数（默认：None — 无限制）
    max_rpm=10,              # 速率限制：每分钟最大API调用次数（默认：None）
    max_retry_limit=2,       # 错误重试次数（默认：2）
    verbose=True,            # 显示详细的执行日志（默认：False）
)
```

**调整`max_iter`：**
- 默认25很慷慨 — 大多数任务在3-8次迭代内完成
- 降低到10-15以在任务定义良好时更快失败
- 如果代理始终达到`max_iter`，则任务过于模糊（修复任务，而不是限制）

### 工具配置

```python
from crewai_tools import SerperDevTool, ScrapeWebsiteTool, FileReadTool

Agent(
    ...,
    tools=[SerperDevTool(), ScrapeWebsiteTool()],  # 代理级工具
)
```

**关键规则：**
- 没有工具的代理在要求搜索、获取或读取文件时会臆断数据 — 始终为需要外部数据的任务提供工具
- 预先选择**较少、专注的工具**而不是许多工具 — 工具太多会使代理感到困惑
- 工具也可以在**任务级别**分配，用于任务特定访问（参见`design-task`技能）
- 代理级工具对所有代理执行的任务都可用；任务级工具会覆盖特定任务

### LLM选择

```python
Agent(
    ...,
    llm="openai/gpt-4o",              # 主要推理模型
    function_calling_llm="openai/gpt-4o-mini",  # 仅用于工具调用的廉价模型
)
```

使用`function_calling_llm`以节省成本：主`llm`处理推理，而较便宜的模型处理工具调用机制。

### 协作

```python
Agent(
    ...,
    allow_delegation=False,  # 默认：False — 代理独立工作
)
```

仅在以下情况下设置`allow_delegation=True`：
- 代理是具有其他专业代理的团队的一部分
- 任务确实受益于代理将子任务委托出去
- 您正在使用分层流程，其中管理者进行委托

**警告：** 没有明确任务边界的委托会导致无限循环或浪费迭代。

### 规划（计划执行模式）

当在代理上设置`PlanningConfig`时，`Agent.kickoff()`（以及`Agent.execute_task()`）通过新的`crewai.experimental.AgentExecutor`路由。而不是单个ReAct风格的循环，代理：

1. **生成计划** — 一系列`PlanStep`，每个步骤都有一个描述和可选的`tool_to_use`。存储为`state.todos`。
2. **通过`StepExecutor`在隔离的多回合LLM循环中执行每个步骤**（由`max_step_iterations`限制）。
3. **通过`PlannerObserver`观察结果** — 步骤是否成功？剩余计划是否仍然有效？
4. **根据代理的`reasoning_effort`设置路由下一个操作**（见下文）。

`PlanningConfig`的存在启用了此模式。要禁用：不传递它，或者设置`planning=False`。

```python
from crewai import Agent
from crewai.agent.planning_config import PlanningConfig

agent = Agent(
    role="…",
    goal="…",
    backstory="…",
    tools=[...],
    planning_config=PlanningConfig(reasoning_effort="medium"),  # 最常见
)
```

#### `reasoning_effort` — 选择一个

| 级别 | 每个步骤后规划器... | 选择何时 |
|---|---|---|
| `"low"` | 观察（验证成功），标记待办完成，继续。**不重新计划，不细化。** | 您希望计划可见性（todos，观察结果），但信任代理按线性方式遵循它。最快。 |
| `"medium"` (默认) | 观察；**仅在失败时重新计划。** 成功的步骤只是继续。 | 代理的工具可能会失败（网络，执行，抓取），您希望优雅地恢复，而无需在每次成功时支付细化成本。**沙盒编码、研究和其他工具密集型循环的默认设置。** |
| `"high"` | 观察，然后通过`decide_next_action`路由，这可能触发早期目标实现、完整重新计划或每一步后的轻量级细化。 | 任务根据中间发现而改变形状，或者您需要最大程度的适应性。每次运行最多LLM调用。 |

来源：`crewai/experimental/agent_executor.py:450` (`observe_step_result`路由器) 和 `crewai/agent/planning_config.py`。

#### 其他`PlanningConfig`旋钮

```python
PlanningConfig(
    reasoning_effort="medium",
    max_steps=20,            # 计划步骤的上限（默认20）
    max_replans=3,           # 最终确定前的最大完整重新计划次数（默认3）
    max_attempts=None,       # 计划生成期间的规划细化尝试次数
    max_step_iterations=15,  # 每个步骤的`StepExecutor`的最大LLM回合数（默认15）
    step_timeout=None,       # 每个步骤的墙上时间；None = 无限制
    system_prompt=None,      # 自定义规划系统提示（如果为None，则使用默认值）
    plan_prompt=None,        # 自定义初始计划提示；占位符：{description}，{expected_output}，{tools}，{max_steps}
    refine_prompt=None,      # 自定义细化提示
    llm=None,                # 用于规划的单独LLM（否则使用代理.llm）
)
```

使用`llm="anthropic/claude-haiku-4-5"`（便宜）用于规划，同时保持`agent.llm="anthropic/claude-opus-4-7"`（强大）用于执行 — 常见的成本优化。

#### 启用时

- **启用**对于代理自行选择步骤且您希望失败恢复的自主循环（例如，编写→运行→修补的编码代理；搜索→抓取→修订的研究代理）。
- **跳过**对于单工具、单用途调用（例如，“总结这个字符串”，“发布这个Slack DM”）— 观察开销不值得。

#### 成本形状

每个步骤都会得到一个`PlannerObserver` LLM调用（约每步1次额外调用）。在`"medium"`上，失败的步骤会添加重新计划调用。在`"high"`上，每步还会添加`decide_next_action`调用。对于N步计划，预期大约：

- `low`: N执行 + N观察 = **2N调用**
- `medium`: 2N + (失败次数 × 1重新计划)
- `high`: ~3N + 重新计划/细化

规模材料 — 在默认为所有内容使用`high`之前进行测量。

#### 自定义`plan_prompt`

如果您提供`plan_prompt`，请包含规划模板期望的占位符：`{description}`，`{expected_output}`，`{tools}`，`{max_steps}`。规划LLM会获得这些插值。保持自定义提示专注于*特定项目*规则；让`description`/`tools`（自动注入）携带动态内容。

### 代码执行

```python
Agent(
    ...,
    allow_code_execution=True,        # 启用代码执行（默认：False）
    code_execution_mode="safe",       # "safe" (Docker) 或 "unsafe" (直接) — 默认: "safe"
)
```

- `"safe"`需要安装并运行Docker — 在容器中执行
- `"unsafe"`在主机上直接运行代码 — 仅在受控环境中使用

### 上下文窗口管理

```python
Agent(
    ...,
    respect_context_window=True,      # 自动总结以保持在限制内（默认：True）
)
```

当`True`时，如果它接近LLM的代币限制，代理会自动总结先前的上下文。当`False`时，溢出时执行会出错。

### 日期注入

```python
Agent(
    ...,
    inject_date=True,                 # 向任务上下文添加当前日期（默认：False）
    date_format="%Y-%m-%d",           # 日期格式（默认: "%Y-%m-%d"）
)
```

用于时间敏感任务（研究、新闻分析、调度）。

### 代理护栏

```python
def validate_no_pii(result) -> tuple[bool, Any]:
    """拒绝包含PII的输出。"""
    if contains_pii(result.raw):
        return (False, "输出包含PII。删除所有个人信息并重试。")
    return (True, result)

Agent(
    ...,
    guardrail=validate_no_pii,
    guardrail_max_retries=3,          # 默认：3
)
```

代理护栏验证代理产生的每个输出。代理在失败时重试，最多`guardrail_max_retries`次。

### 知识来源

```python
from crewai.knowledge.source.text_file_knowledge_source import TextFileKnowledgeSource

Agent(
    ...,
    knowledge_sources=[
        TextFileKnowledgeSource(file_paths=["company_handbook.txt"]),
    ],
    embedder={
        "provider": "openai",
        "config": {"model": "text-embedding-3-small"},
    },
)
```

知识来源通过RAG为代理提供访问特定领域数据的方式。当代理需要参考大型文档、政策或数据集时使用。

---

## 3. YAML配置（推荐）

在`agents.yaml`中定义代理，以实现配置和代码的清晰分离：

```yaml
researcher:
  role: >
    {topic} 高级数据研究员
  goal: >
    发现{主题}的前沿发展，并确定支持证据和来源引用的前5个趋势
  backstory: >
    你是一位拥有15年经验的资深研究员。
    以能够找到晦涩但相关的来源而闻名
    并将复杂的发现综合为清晰、可操作的见解。
    你总是引用你的来源并明确标记不确定性。
  # 可选覆盖（按需取消注释）：
  # llm: openai/gpt-4o
  # max_iter: 15
  # max_rpm: 10
  # allow_delegation: false
  # verbose: true
```

然后在`crew.py`中连接：

```python
@CrewBase
class MyCrew:
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def researcher(self) -> Agent:
        return Agent(
            config=self.agents_config["researcher"],
            tools=[SerperDevTool()],
        )
```

**关键：** 方法名（`def researcher`）必须与YAML键（`researcher:`）匹配。不匹配会导致`KeyError`。

---

## 4. Agent.kickoff() — 直接代理执行

当您需要一个具有工具和推理的代理，而无需crew开销时，使用`Agent.kickoff()`。这是Flow中最常见的模式。

### 基本用法

```python
from crewai import Agent
from crewai_tools import SerperDevTool

researcher = Agent(
    role="高级研究员",
    goal="找到全面、事实性的信息并附上来源引用",
    backstory="以彻底、基于证据的分析而闻名的专家研究员。",
    tools=[SerperDevTool()],
    llm="openai/gpt-4o",
)

# 传递一个字符串提示 — 代理推理，使用工具，并返回结果
result = researcher.kickoff("量子计算的最新发展是什么？")
print(result.raw)             # str — 代理的完整响应
print(result.usage_metrics)   # 代币使用统计
```

### 带结构化输出

```python
from pydantic import BaseModel

class ResearchFindings(BaseModel):
    key_trends: list[str]
    sources: list[str]
    confidence: float

result = researcher.kickoff(
    "研究最新的AI代理框架",
    response_format=ResearchFindings,
)

# 通过.pydantic访问（不要直接访问） — Agent.kickoff()包装了结果
print(result.pydantic.key_trends)    # list[str]
print(result.pydantic.confidence)    # float
print(result.raw)                    # 原始字符串版本
```

> **注意：** `Agent.kickoff()`返回`LiteAgentOutput` — 通过`result.pydantic`访问结构化输出。这与`LLM.call()`不同，后者直接返回Pydantic对象。

### 带文件输入

```python
result = researcher.kickoff(
    "分析此文档并总结关键发现",
    input_files={"document": FileInput(path="report.pdf")},
)
```

### 异步变体

```python
result = await researcher.kickoff_async(
    "研究量子计算突破",
    response_format=ResearchFindings,
)
```

### Flow中的Agent.kickoff()（推荐模式）

最强大的模式是在Flow中编排多个`Agent.kickoff()`调用。Flow处理状态和排序；每个代理处理其特定步骤：

```python
from crewai import Agent
from crewai.flow.flow import Flow, listen, start
from crewai.tools import SerperDevTool, ScrapeWebsiteTool
from pydantic import BaseModel

class ResearchState(BaseModel):
    topic: str = ""
    research: str = ""
    analysis: str = ""
    report: str = ""

class ResearchFlow(Flow[ResearchState]):

    @start()
    def gather_data(self):
        researcher = Agent(
            role="高级研究员",
            goal="找到全面的数据和来源",
            backstory="擅长找到和验证信息。",
            tools=[SerperDevTool(), ScrapeWebsiteTool()],
        )
        result = researcher.kickoff(f"研究：{self.state.topic}")
        self.state.research = result.raw

    @listen(gather_data)
    def analyze(self):
        analyst = Agent(
            role="数据分析员",
            goal="从原始研究中提取可操作的见解",
            backstory="擅长模式识别和综合。",
        )
        result = analyst.kickoff(
            f"分析这项研究并提取关键见解：\n\n{self.state.research}"
        )
        self.state.analysis = result.raw

    @listen(analyze)
    def write_report(self):
        writer = Agent(
            role="报告作家",
            goal="创建清晰、结构良好的报告",
            backstory="技术作家，使复杂主题易于理解。",
        )
        result = writer.kickoff(
            f"根据这项分析撰写一份综合报告：\n\n{self.state.analysis}"
        )
        self.state.report = result.raw

flow = ResearchFlow()
flow.kickoff(inputs={"topic": "AI代理"})
print(flow.state.report)
```

**何时使用Agent.kickoff()与Crew.kickoff():**
- 当每个步骤是一个独立的代理，Flow控制排序时使用`Agent.kickoff()`。
- 当多个代理需要在一个步骤中协作时使用`Crew.kickoff()`。

### Flow中的Conversational Flow Routes的Agent.kickoff()

在实验性对话Flow中，Flow拥有聊天生命周期和路由选择。代理应在路由处理程序中调用，以进行有界工具支持的工作：研究、文档查找、帐户操作、分类、起草或升级准备。

```python
from crewai import Agent, Flow
from crewai.flow import listen
from crewai.experimental.conversational import ConversationState


class SupportFlow(Flow[ConversationState]):
    conversational = True

    def research_agent(self) -> Agent:
        return Agent(
            role="支持研究专家",
            goal="为用户的当前问题找到准确的信息并附上来源。",
            backstory="你精确、基于证据，并明确标记不确定性。",
            tools=[...],
        )

    @listen("RESEARCH")
    def handle_research(self) -> str:
        """新鲜研究，当前查找和基于来源的综合。"""
        result = self.research_agent().kickoff(self.state.current_user_message)
        self.append_agent_result("research_agent", result, visibility="private")
        reply = result.raw
        self.append_assistant_message(reply)
        return reply
```

设计影响：
- 保持对话的`Flow`负责会话ID、消息历史、路由、跟踪最终确定和批准。
- 保持每个代理狭窄：一个路由，一个工具表面，一个工作。
- 使用`append_agent_result(..., visibility="private")`进行应该不会进入规范聊天历史的草稿工作。
- 使用`append_assistant_message(reply)`为用户可见的答案，以便下一轮有助理的上下文。
- 不要制作一个“聊天代理”，具有每个工具。首先路由，然后调用一个专注的代理来处理选定的路由。

有关Flow生命周期的入门参考，请参阅：`skills/getting-started/references/conversational-flows.md`。

---

## 5. 专家与通才代理

> **注意：** 将本节应用于*在您决定确实需要多个代理后*（参见第0节）。如果您只需要一个代理，“专家与通才”不是问题——问题是如何设计那个唯一的代理。

**当您确实需要多个代理时，请优先考虑专家。** 一个做一件事做得好的代理胜过一个做许多事还可以接受的代理。

### 何时使用专家

- 任务需要深厚的领域知识
- 输出质量比速度更重要
- 任务复杂到可以从专注的专业知识中受益

### 通才何时可以接受

- 简单任务具有明确的指示
- 原型设计，您稍后专业化
- 真正跨越多个领域平等的任务

### 专家设计模式

不要创建一个“内容作家”代理，而要创建：
- `technical_writer` — 深度技术准确性，代码示例
- `copywriter` — 说服力强，面向目标受众的营销文案
- `editor` — 语法、一致性、风格指南执行

每个专家都有一个狭窄的角色、特定的目标，以及强化其专业知识的背景故事。

---

## 6. 代理交互模式

### 顺序（默认）

代理一个接一个地工作。每个代理接收先前代理的输出作为上下文。

```
研究员 → 作家 → 编辑
```

最适合：线性管道，每个步骤都建立在最后一个步骤之上。

### 分层

一个管理代理委托和验证。任务分配是动态的。

```python
Crew(
    agents=[researcher, writer, editor],
    tasks=[research_task, writing_task, editing_task],
    process=Process.hierarchical,
    manager_llm="openai/gpt-4o",
)
```

最适合：复杂的流程，其中任务分配取决于中间结果。

### 代理到代理委托

当`allow_delegation=True`时，代理可以请求另一个crew代理的帮助：

```python
lead_researcher = Agent(
    role="首席研究员",
    goal="协调研究工作",
    backstory="...",
    allow_delegation=True,  # 可以委托给crew中的其他代理
)
```

代理将自动发现其他crew成员并根据需要委托子任务。

---

## 7. 常见的代理设计错误

| 错误 | 影响 | 修复 |
|---|---|---|
| 通用角色如“助手” | 代理产生不集中、肤浅的输出 | 使用具体的专业知识：例如，“高级金融分析师” |
| 没有工具的数据收集任务 | 代理臆断数据而不是搜索 | 始终为需要外部数据的任务提供工具 |
| 工具太多（10+） | 代理在工具之间选择感到困惑 | 限制每个代理3-5个相关的工具 |
| 背景故事充满任务指令 | 代理将个性与任务执行混合在一起 | 背景故事关于代理是谁；任务细节放在任务中 |
| `allow_delegation=True`默认 | 代理浪费迭代进行琐碎的委托 | 仅在委托确实有助于时启用 |
| max_iter过高对于简单任务 | 代理在模糊任务上不必要的循环 | 降低max_iter；修复任务描述而不是限制 |
| 没有护栏在关键输出 | 坏输出未经检查就通过 | 为输出添加护栏，这些输出馈送到生产系统 |
| 使用昂贵的LLM进行工具调用 | 机械操作不必要的成本 | 设置`function_calling_llm`为更便宜的模型 |

---

## 8. 代理设计检查清单

在部署代理之前，请验证：

- [ ] **角色**是具体和领域专注的（不是“助手”或“助手”）
- [ ] **目标**包括期望结果和所需质量标准
- [ ] **背景故事**建立了专业知识和工作方式
- [ ] **工具**分配给任何需要外部数据的任务
- [ ] **没有多余的工具** — 每个代理最多3-5个
- [ ] **max_iter**根据预期任务复杂性调整（简单任务10-15，复杂任务20-25）
- [ ] **max_execution_time**为生产代理设置，以防止挂起
- [ ] **护栏**配置为关键输出
- [ ] **LLM**适合任务复杂性（不要使用GPT-4进行分类）
- [ ] **委托**禁用，除非确实需要
