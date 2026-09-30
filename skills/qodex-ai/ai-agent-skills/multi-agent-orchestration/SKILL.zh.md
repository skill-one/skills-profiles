---
name: multi-agent-orchestration
description: 设计并协调多智能体系统，其中专业智能体协同工作以解决复杂问题。涵盖智能体通信、任务委派、工作流编排和结果聚合。适用于构建协同智能体团队、复杂工作流或需要跨领域专业知识的系统。
---

# 多智能体编排

设计和编排复杂的智能体系统，其中专业智能体协同解决复杂问题，结合不同的专业知识和视角。

## 快速入门

在示例和工具中开始多智能体实现：

- **示例**：查看 [`examples/`](examples/) 目录中的完整实现：
  - [`orchestration_patterns.py`](examples/orchestration_patterns.py) - 顺序、并行、层次和共识编排
  - [`framework_implementations.py`](examples/framework_implementations.py) - CrewAI、AutoGen、LangGraph 和 Swarm 的模板

- **工具**：查看 [`scripts/`](scripts/) 目录中的辅助模块：
  - [`agent_communication.py`](scripts/agent_communication.py) - 消息代理、共享内存和通信协议
  - [`workflow_management.py`](scripts/workflow_management.py) - 工作流执行、优化和监控
  - [`benchmarking.py`](scripts/benchmarking.py) - 团队性能和智能体有效性指标

## 概述

多智能体系统将复杂问题分解为专业子任务，将每个任务分配给具有相关专业知识的智能体，然后协调它们的工作以实现统一目标。

### 多智能体系统大放异彩的时机

- **复杂工作流**：需要多个专业角色的任务
- **特定领域专业知识**：金融、法律、人力资源、工程需要不同的知识
- **并行处理**：多个智能体同时处理不同方面
- **协同推理**：智能体辩论、改进和优化解决方案
- **弹性**：一个智能体的故障不会破坏整个系统
- **可扩展性**：轻松添加新的专业智能体

### 架构概述

```
用户请求
    ↓
编排器
    ├→ 智能体 1（专家）→ 任务 1
    ├→ 智能体 2（专家）→ 任务 2
    ├→ 智能体 3（专家）→ 任务 3
    ↓
结果聚合器
    ↓
最终响应
```

## 核心概念

### 智能体定义

智能体由以下内容定义：
- **角色**：它有什么职责？（例如，“财务分析师”）
- **目标**：它应该完成什么？（例如，“分析财务风险”）
- **专业知识**：它有什么知识/工具？
- **工具**：它可以访问哪些能力？
- **上下文**：它需要哪些信息才能有效工作？

### 编排模式

#### 1. 顺序编排
- 智能体按顺序工作
- 每个智能体使用前一个智能体的输出
- **用例**：步骤必须按顺序执行（研究 → 分析 → 撰写）

#### 2. 并行编排
- 多个智能体同时工作
- 结果在最后聚合
- **用例**：独立任务（分析竞争对手、市场、用户）

#### 3. 层次编排
- 高级智能体将任务委托给初级智能体
- 管理员协调流程
- **用例**：需要监督的大型项目

#### 4. 基于共识的编排
- 多个智能体分析问题
- 辩论和改进想法
- 投票或达成共识
- **用例**：需要多个视角的复杂决策

#### 5. 工具中介编排
- 智能体使用共享工具/数据库
- 最小化直接通信
- **用例**：大型系统，间接协调

## 多智能体团队示例

### 财务团队

```
协调器智能体
    ├→ 市场分析师智能体
    │   ├ 工具：市场数据 API、财经新闻
    │   └ 任务：分析市场状况
    ├→ 财务分析师智能体
    │   ├ 工具：财务报表、比率计算
    │   └ 任务：分析公司财务状况
    ├→ 风险管理器智能体
    │   ├ 工具：风险模型、情景分析
    │   └ 任务：评估投资风险
    └→ 报告撰写器智能体
        ├ 工具：文档生成
        └ 任务：将发现综合成报告
```

### 法律团队

```
案件管理智能体（协调器）
    ├→ 合同分析器智能体
    │   └ 任务：审查合同条款
    ├→ 先例研究智能体
    │   └ 任务：查找相关案例法
    ├→ 风险评估器智能体
    │   └ 任务：识别法律风险
    └→ 文档起草器智能体
        └ 任务：准备法律文件
```

### 客户支持团队

```
支持协调器
    ├→ 问题分类器智能体
    │   └ 任务：对客户问题进行分类
    ├→ 知识库智能体
    │   └ 任务：查找相关文档
    ├→ 升级智能体
    │   └ 任务：确定是否需要人工升级
    └→ 解决方案综合器智能体
        └ 任务：准备全面回复
```

## 实现框架

### 1. CrewAI

**最适合**：具有清晰角色和层次结构的团队

```python
from crewai import Agent, Task, Crew

# 定义智能体
analyst = Agent(
    role="财务分析师",
    goal="分析财务数据并提供见解",
    背景="具有 10 年以上经验的金融市场专家"
)

researcher = Agent(
    role="市场研究员",
    goal="研究市场趋势和竞争",
    背景="专注于市场分析的 数据驱动型研究员"
)

# 定义任务
analysis_task = Task(
    description="分析 {company} 的第三季度财务结果",
    agent=analyst,
    工具=[financial_tool, data_tool]
)

research_task = Task(
    description="研究 {market} 的竞争格局",
    agent=researcher,
    工具=[web_search_tool, industry_data_tool]
)

# 创建团队并执行
crew = Crew(
    智能体=[analyst, researcher],
    任务=[analysis_task, research_task],
    process=Process.sequential
)

result = crew.kickoff(inputs={"company": "TechCorp", "market": "AI"})
```

### 2. AutoGen（微软）

**最适合**：复杂的多人对话和谈判

```python
from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager

# 定义智能体
analyst = AssistantAgent(
    name="analyst",
    system_message="你是财务分析师..."
)

researcher = AssistantAgent(
    name="researcher",
    system_message="你是市场研究员..."
)

# 创建群聊
groupchat = GroupChat(
    智能体=[analyst, researcher],
    messages=[],
    max_round=10,
    speaker_selection_method="auto"
)

# 管理群聊
manager = GroupChatManager(groupchat=groupchat)

# 用户代理以发起对话
user = UserProxyAgent(name="user")

# 进行对话
user.initiate_chat(
    manager,
    message="分析公司 X 是否应该投资于 Y 市场"
)
```

### 3. LangGraph

**最适合**：具有状态管理的复杂工作流

```python
from langgraph.graph import Graph, StateGraph
from langgraph.prebuilt import create_agent_executor

# 定义状态
class AgentState:
    research_findings: str
    analysis: str
    recommendations: str

# 创建图
graph = StateGraph(AgentState)

# 为每个智能体添加节点
graph.add_node("researcher", research_agent)
graph.add_node("analyst", analyst_agent)
graph.add_node("writer", writer_agent)

# 定义边（工作流）
graph.add_edge("researcher", "analyst")
graph.add_edge("analyst", "writer")

# 设置入口/出口点
graph.set_entry_point("researcher")
graph.set_finish_point("writer")

# 编译并运行
workflow = graph.compile()
result = workflow.invoke({"topic": "AI 趋势"})
```

### 4. OpenAI Swarm

**最适合**：简单的智能体交接和对话式工作流

```python
from swarm import Agent, Swarm

# 定义智能体
triage_agent = Agent(
    name="Triage Agent",
    instructions="确定将客户路由到哪个专家"
)

billing_agent = Agent(
    name="Billing Specialist",
    instructions="处理账单和支付问题"
)

technical_agent = Agent(
    name="Technical Support",
    instructions="处理技术问题"
)

# 定义交接函数
def route_to_billing(reason: str):
    return billing_agent

def route_to_technical(reason: str):
    return technical_agent

# 向分诊智能体添加工具
triage_agent.functions = [route_to_billing, route_to_technical]

# 执行 Swarm
client = Swarm()
response = client.run(
    agent=triage_agent,
    messages=[{"role": "user", "content": "我有一个账单问题"}]
)
```

## 编排模式

### 模式 1：顺序任务链

智能体按顺序执行任务，每个任务都依赖于前一个结果：

```python
# 任务 1：研究
research_output = research_agent.work("分析 AI 市场趋势")

# 任务 2：分析（使用研究输出）
analysis = analyst_agent.work(f"分析这些发现： {research_output}")

# 任务 3：报告（使用分析）
report = writer_agent.work(f"撰写关于： {analysis} 的报告")
```

**何时使用**：步骤有依赖关系，每个步骤都依赖于前一个

### 模式 2：并行执行

多个智能体同时工作，结果合并：

```python
import asyncio

async def parallel_teams():
    # 所有智能体并行工作
    market_task = market_agent.work_async("分析市场")
    technical_task = tech_agent.work_async("分析技术")
    user_task = user_agent.work_async("分析用户需求")

    # 等待所有完成
    market_results, tech_results, user_results = await asyncio.gather(
        market_task, technical_task, user_task
    )

    # 综合结果
    return synthesize(market_results, tech_results, user_results)
```

**何时使用**：独立分析，需要快速结果，希望多样性

### 模式 3：层次结构

管理器智能体协调专家：

```python
manager_agent.orchestrate({
    "market_analysis": {
        "智能体": [competitor_analyst, trend_analyst],
        "任务": "全面市场分析"
    },
    "technical_evaluation": {
        "智能体": [architecture_agent, security_agent],
        "任务": "技术可行性评估"
    },
    "synthesis": {
        "智能体": [strategy_agent],
        "任务": "创建战略建议"
    }
})
```

**何时使用**：清晰的层次结构，不同团队，复杂协调

### 模式 4：辩论与共识

多个智能体讨论并达成共识：

```python
agents = [bull_agent, bear_agent, neutral_agent]
question = "我们应该投资这家初创公司吗？"

# 辩论回合 1
arguments = {agent: agent.argue(question) for agent in agents}

# 辩论回合 2（回应他人）
counter_arguments = {
    agent: agent.respond(arguments) for agent in agents
}

# 达成共识
consensus = mediator_agent.synthesize_consensus(counter_arguments)
```

**何时使用**：复杂决策，需要多个视角，风险评估

## 智能体通信模式

### 1. 直接通信
智能体直接向彼此传递消息：

```python
agent_a.send_message(agent_b, {
    "type": "request",
    "action": "analyze_document",
    "document": doc_content,
    "context": {"deadline": "urgent"}
})
```

### 2. 工具中介通信
智能体使用共享工具/数据库：

```python
# 智能体 A 写入共享内存
shared_memory.write("findings", {"market_size": "$5B", "growth": "20%"})

# 智能体 B 从共享内存读取
findings = shared_memory.read("findings")
```

### 3. 基于管理器的通信
中央协调员管理智能体通信：

```python
manager.broadcast("update_all_agents", {
    "new_deadline": "明天",
    "priority": "critical"
})
```

## 最佳实践

### 智能体设计
- ✓ 清晰、具体的角色和目标
- ✓ 适合角色的工具
- ✓ 相关的背景/专业知识
- ✓ 与其他智能体区分开来
- ✓ 合理的工作范围

### 工作流设计
- ✓ 清晰的任务依赖关系
- ✓ 确定交接点
- ✓ 智能体之间的错误处理
- ✓ 备用策略
- ✓ 性能监控

### 通信
- ✓ 结构化的消息格式
- ✓ 清晰的上下文共享
- ✓ 错误传播策略
- ✓ 超时处理
- ✓ 审计日志

### 编排
- ✓ 清晰定义流程（顺序、并行等）
- ✓ 设置清晰的成功标准
- ✓ 监控智能体性能
- ✓ 实施反馈循环
- ✓ 允许人工干预点

## 常见挑战与解决方案

### 挑战：智能体冲突
**解决方案**：
- 清晰的角色分离
- 明确的决策规则
- 共识机制
- 冲突解决智能体
- 清晰的权威层次结构

### 挑战：执行缓慢
**解决方案**：
- 尽可能使用并行执行
- 缓存昂贵操作的结果
- 预处理数据
- 优化智能体逻辑
- 实施超时处理

### 挑战：结果质量差
**解决方案**：
- 更好的智能体提示/说明
- 更相关的工具
- 反馈集成
- 质量验证智能体
- 结果聚合策略

### 挑战：复杂工作流
**解决方案**：
- 分解为更小的团队
- 层次结构
- 清晰的任务定义
- 良好的状态管理
- 工作流文档

## 评估指标

**团队性能**：
- 任务完成率
- 结果质量
- 执行时间
- 成本（令牌/API 调用）
- 错误率

**智能体有效性**：
- 任务成功率
- 响应质量
- 工具使用效率
- 通信清晰度
- 协作分数

## 高级技术

### 1. 自组织团队
智能体自主决定角色和工作流：

```python
# 智能体根据任务协商角色
agents = [agent1, agent2, agent3]
task = "复杂的财务分析"

# 智能体确定最佳结构
negotiated_structure = self_organize(agents, task)
# 返回此任务的最佳工作流
```

### 2. 自适应工作流
工作流根据进度变化：

```python
# 监控进度
if progress < expected_rate:
    # 增加资源
    workflow.add_agent(specialist_agent)
elif quality < threshold:
    # 增加验证
    workflow.insert_review_step()
```

### 3. 跨智能体学习
智能体从彼此的工作中学习：

```python
# 团队执行后
execution_trace = crew.get_execution_trace()

# 提取学习成果
learnings = extract_patterns(execution_trace)

# 更新智能体知识
for agent, learning in learnings.items():
    agent.update_knowledge(learning)
```

## 资源

### 框架
- **CrewAI**：https://crewai.com/
- **AutoGen**：https://microsoft.github.io/autogen/
- **LangGraph**：https://langchain-ai.github.io/langgraph/
- **Swarm**：https://github.com/openai/swarm

### 论文
- "Generative Agents"（Park 等人）
- "Self-Organizing Multi-Agent Systems"（研究论文）

## 实现清单

- [ ] 定义每个智能体的角色、目标和专业知识
- [ ] 确定每个智能体可用的工具/功能
- [ ] 规划工作流（顺序、并行、层次）
- [ ] 定义通信模式
- [ ] 实现任务定义
- [ ] 为每个任务设置成功标准
- [ ] 添加错误处理和备用策略
- [ ] 实施监控/日志记录
- [ ] 测试团队协作
- [ ] 评估质量和性能
- [ ] 根据结果进行优化
- [ ] 文档化工作流和决策

## 入门指南

1. **从小处着手**：从 2-3 个智能体开始
2. **清晰的工作流**：记录智能体如何交互
3. **彻底测试**：单独和一起验证智能体行为
4. **密切监控**：跟踪性能和结果
5. **迭代**：根据结果进行改进
6. **扩展**：根据需要添加智能体和复杂性
