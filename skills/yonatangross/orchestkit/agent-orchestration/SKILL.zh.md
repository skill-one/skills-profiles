---
name: agent-orchestration
description: 用于代理循环、多代理协调、替代框架和多场景工作流的代理编排模式。在构建自主代理循环、协调多个代理、评估CrewAI/AutoGen/Swarm或编排复杂的多步骤场景时使用。
---

# 代理编排

构建和协调 AI 代理的综合模式——从单代理推理循环到多代理系统和框架选择。协调和多场景类别在 `rules/` 目录中有各自的规则文件，按需加载；循环和框架教程位于上游（参见[上游覆盖](#upstream-coverage-do-not-restate)），房屋默认值位于 `references/ork-delta.md`。

> **CC 原生 `/workflows` (2.1.154):** Claude Code 现在提供*动态工作流*——让 Claude 创建一个工作流，它将在后台协调数十到数百个代理；使用 `/workflows` 查看运行情况。这是**补充**此处模式的：使用 CC `/workflows` 进行大规模、一劳永逸的**后台**发散（你稍后检查）；当 ≤8 个代理必须通过共享内存（交接文件、网格消息）在单个技能调用内协调时，使用下方的有界**前台**代理团队/任务工具模式。不同规模，不是替代品。
>
> **仅在真正遇到困难时提问 (CC 2.1.154):** CC 现在保留多项选择题提示用于它自己无法做出的决定，而不是在它已经有了足够的上下文来继续时提问。在编排代理时，不要在代理可以解决的可获得上下文中阻塞进度 `AskUserQuestion`——保留提示用于真正的分支点（不可逆操作、缺失需求）。这补充了 ork 友好的决策指导。

## 快速参考

| 类别 | 规则 | 影响 | 使用时机 |
|-------|-------|--------|-------------|
| [代理循环](#agent-loops) | 上游 | 高 | ReAct 推理、计划执行、自我纠正 |
| [多代理协调](#multi-agent-coordination) | 2 | 关键 | 监管路由、代理辩论、结果合成 |
| [替代框架](#alternative-frameworks) | 上游 | 高 | CrewAI 小组、AutoGen 团队、框架比较 |
| [多场景](#multi-scenario) | 2 | 中等 | 并行场景编排、难度路由 |

**总计：4 个规则跨越 4 个类别。** 循环和框架教程已移至第一方来源；救援的房屋默认值位于 `references/ork-delta.md`。

## 快速入门

```python
# ReAct 代理循环
async def react_loop(question: str, tools: dict, max_steps: int = 10) -> str:
    history = REACT_PROMPT.format(tools=list(tools.keys()), question=question)
    for step in range(max_steps):
        response = await llm.chat([{"role": "user", "content": history}])
        if "Final Answer:" in response.content:
            return response.content.split("Final Answer:")[-1].strip()
        if "Action:" in response.content:
            action = parse_action(response.content)
            result = await tools[action.name](*action.args)
            history += f"\nObservation: {result}\n"
    return "达到最大步数未得到答案"
```

```python
# 带有发散/汇聚的监管者
async def multi_agent_analysis(content: str) -> dict:
    agents = [("security", security_agent), ("perf", perf_agent)]
    tasks = [agent(content) for _, agent in agents]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return await synthesize_findings(results)
```

## 代理循环

自主 LLM 推理的模式：ReAct（推理+行动）、计划执行带重规划、自我纠正循环和滑动窗口内存管理。

**关键决策：** 最大步数 5-15、温度 0.3-0.7、内存窗口 10-20 条消息。

## 多代理协调

发散/汇聚并行性、依赖排序的监管路由、冲突解决（基于置信度或 LLM 仲裁）、结果合成以及 CC 代理团队（在 CC 2.1.33+ 中用于同伴消息传递的网格拓扑）。

**关键决策：** 3-8 个专家、并行化独立代理。从三种模式中选择一种：代理工具（星型）用于简单工作、代理团队（网格）用于跨领域问题、工作流用于稍后检查的大型后台发散。

## 替代框架

CrewAI 分层小组带 Flows (1.8+)、OpenAI 代理 SDK 交接和护栏 (0.12+)、Microsoft 代理框架 (AutoGen + SK 合并)、GPT-5.2-Codex 用于长周期编码、AG2 用于开源灵活性。

**关键决策：** 根据团队专业知识和用例匹配框架。LangGraph 用于状态机、CrewAI 用于基于角色的团队、OpenAI SDK 用于交接工作流、MS 代理用于企业合规。

## 多场景

跨 3 个并行场景（简单/中等/复杂）编排单个技能，带渐进式难度缩放（1x/3x/8x）、里程碑同步和跨场景结果聚合。

**关键决策：** 带检查点的自由运行、始终 3 个场景、1x/3x/8x 指数缩放、30s/90s/300s 时间预算。

## 上游覆盖（不要重述）

这些主题的本地教程已退役；请咨询第一方来源，并将仅有的房屋增量保留在 `references/ork-delta.md`。

| 主题 | 第一方来源 |
|-------|--------------------|
| ReAct / 计划执行 / 自我纠正循环实现 | OpenAI 函数调用指南 (https://platform.openai.com/docs/guides/function-calling)；LangGraph 教程 (context7: /langchain-ai/langgraph) |
| 发散协调、结果合成样板和通用多代理设计清单 | Python asyncio 文档 (https://docs.python.org/3/library/asyncio-task.html)；Anthropic "构建有效代理" (https://www.anthropic.com/research/building-effective-agents)；`ork:langgraph` 监管模式 |
| CrewAI (小组、Flows、MCP 工具、护栏) | CrewAI 文档 (https://docs.crewai.com)；context7: /crewaiinc/crewai |
| OpenAI 代理 SDK (交接、会话、护栏、MCP) | https://openai.github.io/openai-agents-python/ ; context7: /openai/openai-agents-python |
| Microsoft 代理框架 / AutoGen (团队、终止、A2A) | https://learn.microsoft.com/en-us/agent-framework/ ; context7: /microsoft/autogen |
| GPT-5.2-Codex 功能、定价、IDE 集成 | OpenAI 模型文档 (https://platform.openai.com/docs/models) |
| 多场景状态机、架构和技能无关模板深入 | 在技能中由 `rules/scenario-orchestrator.md` 和 `rules/scenario-routing.md` 取代 |

## 参考

- `references/ork-delta.md` - 房屋默认值和来自已退役教程的日期决策救援
- `references/framework-comparison.md` - 精简框架决策矩阵和用例表
- `references/langgraph-implementation.md` - LangGraph 1.2+ 实现的多场景编排器
- `references/claude-code-instance-management.md` - 运行 3 个并行 Claude Code 实例进行场景演示

## 关键决策

| 决策 | 建议 |
|----------|----------------|
| 单代理与多代理 | 单个用于专注任务，多个用于可分解工作 |
| 最大循环步数 | 5-15（防止无限循环） |
| 代理数量 | 每个工作流 3-8 个专家 |
| 框架 | 根据团队专业知识和用例匹配 |
| 拓扑 | 代理工具（星型）用于简单；代理团队（网格）用于复杂；工作流用于大型后台发散 |
| 场景数量 | 始终 3 个：简单、中等、复杂 |

## 常见错误

- 代理循环中没有步数限制（无限循环）
- 没有内存管理（上下文溢出）
- 多代理中没有错误隔离（一个失败导致所有崩溃）
  - 注意 (CC 2.1.161)：并行*工具调用*现在独立失败——一个失败的 Bash 不再取消同一批次的兄弟姐妹。这个注意事项仍然适用于代理编排级别，而不是工具批次；`claude agents` 行现在显示 `done/total` 用于发散的工作。
  - 注意 (CC 2.1.157)：`claude agents` 尊重 `settings.json` 中的 `agent` 字段用于分派的会话；`--agent <name>` 覆盖它——在分派时显式固定代理类型。
- 缺少合成步骤（原始代理输出无用处）
- 在一个项目中混合框架（复杂性激增）
- 使用代理团队进行简单的顺序工作（使用代理工具）
- 顺序而不是并行场景（违背目的）

## 相关技能

- `ork:langgraph` - LangGraph 工作流模式（监管者、路由、状态）
- `function-calling` - 工具定义和执行
- `ork:task-dependency-patterns` - 使用 Agent Teams 工作流的任务管理

## 能力详情

### react-loop
**关键词：** react、推理、行动、观察、循环、代理
**解决：**
- 实现 ReAct 模式
- 创建推理循环
- 构建迭代代理

### plan-execute
**关键词：** 计划、执行、重计划、多步、自主
**解决：**
- 创建计划然后执行步骤
- 在失败时实现重计划
- 构建目标导向代理

### supervisor-coordination
**关键词：** 监管者、路由、协调、发散、汇聚、并行
**解决：**
- 将任务路由到专业代理
- 并行运行代理
- 聚合多代理结果

### agent-debate
**关键词：** 辩论、冲突、解决、仲裁、共识
**解决：**
- 解决代理分歧
- 实现 LLM 仲裁
- 处理冲突输出

### result-synthesis
**关键词：** 合成、组合、聚合、合并、摘要
**解决：**
- 组合来自多个代理的输出
- 创建执行摘要
- 跨发现评分置信度

### crewai-patterns
**关键词：** crewai、小组、分层、委托、基于角色、flows
**解决：**
- 构建基于角色的代理团队
- 实现分层协调
- 使用 Flows 进行事件驱动编排

### autogen-patterns
**关键词：** autogen、microsoft、代理框架、团队、企业、a2a
**解决：**
- 构建企业代理系统
- 使用 AutoGen/SK 合并框架
- 实现 A2A 协议

### framework-selection
**关键词：** 选择、比较、框架、决策、哪个、crewai、autogen、openai
**解决：**
- 选择适当的框架
- 比较框架功能
- 根据需求匹配框架

### scenario-orchestrator
**关键词：** 场景、并行、发散、难度、渐进、演示
**解决：**
- 跨多个难度级别运行技能
- 实现并行场景执行
- 聚合跨场景结果

### scenario-routing
**关键词：** 路由、同步、里程碑、检查点、缩放
**解决：**
- 按难度级别路由任务
- 在里程碑同步
- 逐步缩放输入
