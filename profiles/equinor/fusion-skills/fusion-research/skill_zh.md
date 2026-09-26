# 融合研究

## 何时使用

当用户需要关于融合生态系统的有来源依据的答案时，使用此技能。

典型触发条件：
- "研究这个融合框架钩子并展示支持来源。"
- "这个 EDS 组件接受哪些属性？"
- "哪个技能处理融合工作流中的 X？"
- "为…找到一个有来源依据的示例。"
- "哪个融合包或模块拥有这个 API？"
- "这个值是否有 EDS 设计令牌？"
- "如何在融合应用中持久化用户偏好？"
- "融合中 X 的推荐模式是什么？"
- "展示一个用于构建 X 的融合框架示例。"
- "EDS 中颜色和间距的设计令牌是什么？"
- "融合如何在平台级别处理 X？"
- "融合平台对 Y 的指导是什么？"
- "如何加入融合？"
- "融合平台中 Z 的指南是什么？"

## 何时不用

不要使用此技能用于：
- 实现代码更改 — 使用 `fusion-app-react-dev` 或相关开发技能；如果研究是针对您正在积极构建的特定应用，请首先使用 `fusion-app-react-dev` — 它将在需要时调用此技能
- 查找、安装、更新或删除技能 — 使用 `fusion-discover-skills`；仅使用此技能来理解技能的范围、关系或目录适用性 — 不要用来发现要安装什么
- 创建或编辑技能文件 — 使用 `fusion-skill-authoring` 进行编写时研究
- 融合 MCP 安装或故障排除 — 使用 `fusion-mcp`；一旦 MCP 运行，返回此处进行研究
- 没有具体构件名称（钩子、组件、包、令牌或平台主题）的纯概念性融合问题 — 首先向用户提供具体的构件引用或平台主题

## 指令

### 第 0 步 — 缩小范围（可选）

在分类之前，您可以使用特定领域的后续问题来缩小用户的精确需求：
- 框架范围：[assets/framework.follow-up.md](assets/framework.follow-up.md)
- EDS 范围：[assets/eds.follow-up.md](assets/eds.follow-up.md)
- 技能目录范围：[assets/skills.follow-up.md](assets/skills.follow-up.md)
- 文档范围：[assets/docs.follow-up.md](assets/docs.follow-up.md)

如果问题已经命名了特定构件（钩子、组件、包、令牌或技能），则跳过此步骤。

### 第 1 步 — 对研究问题进行分类

确定问题属于哪个领域：

| 领域 | 指示器 | 代理 |
| --- | --- | --- |
| **框架** | 融合框架钩子、包、模块、TypeScript API、cookbook 示例 | [`agents/framework.agent.md`](agents/framework.agent.md) |
| **EDS** | EDS 组件属性、使用示例、可访问性、设计令牌 | [`agents/eds.agent.md`](agents/eds.agent.md) |
| **技能** | 技能目录查找、范围边界、伴随/协调器关系 | [`agents/skills.agent.md`](agents/skills.agent.md) |
| **文档** | 融合平台概念、入职、平台操作、治理、非实现指导 | [`agents/docs.agent.md`](agents/docs.agent.md) |
| **后端代码** | C# 服务实现、接口、CQRS 模式、授权、验证、跨服务 API | [`agents/backend-code.agent.md`](agents/backend-code.agent.md) |

如果问题跨越多个领域，请按顺序使用适当的代理分别回答每个领域。

### 第 2 步 — 派发给正确的代理

- 框架问题 → 跟随 [`agents/framework.agent.md`](agents/framework.agent.md)。
- EDS 问题 → 跟随 [`agents/eds.agent.md`](agents/eds.agent.md)。
- 技能问题 → 跟随 [`agents/skills.agent.md`](agents/skills.agent.md)。
- 文档问题 → 跟随 [`agents/docs.agent.md`](agents/docs.agent.md)。
- 后端代码问题 → 跟随 [`agents/backend-code.agent.md`](agents/backend-code.agent.md)。

如果运行时支持技能本地代理，则直接调用代理。否则，按代理的指令进行内联处理。

### 第 3 步 — 返回有来源依据的答案

使用 [assets/source-backed-answer-template.md](assets/source-backed-answer-template.md) 中的结构：
- 说明使用的领域和代理。
- 包含一到三个有来源依据的证据要点。
- 以任何剩余的假设、不确定性或下一步验证步骤结束。

## 研究代理

此技能包括 `agents/` 中的五个研究代理。每个代理涵盖一个融合研究领域，并具有自己的查询模式和证据清单。

- **[`agents/framework.agent.md`](agents/framework.agent.md)** — 关于融合框架钩子、包、模块和 cookbook 示例的有来源依据的答案。使用 `mcp_fusion_search_framework`。
- **[`agents/eds.agent.md`](agents/eds.agent.md)** — 关于 EDS 组件属性、使用、可访问性和设计令牌的有来源依据的答案。使用 `mcp_fusion_search_eds`。
- **[`agents/skills.agent.md`](agents/skills.agent.md)** — 关于融合技能目录的有来源依据的答案：哪些技能存在、它们的范围以及它们如何关联。使用 `mcp_fusion_search_skills`。
- **[`agents/docs.agent.md`](agents/docs.agent.md)** — 关于融合平台概念、入职、操作和治理的有来源依据的答案。使用 `mcp_fusion_search_docs`。
- **[`agents/backend-code.agent.md`](agents/backend-code.agent.md)** — 关于融合后端服务实现的有来源依据的答案：C# 服务、接口、CQRS 模式、授权和跨服务集成。使用 `mcp_fusion_search_backend_code`。

## 资产

- [assets/source-backed-answer-template.md](assets/source-backed-answer-template.md)
- [assets/framework.follow-up.md](assets/framework.follow-up.md) — 框架研究的预分发范围问题
- [assets/eds.follow-up.md](assets/eds.follow-up.md) — EDS 研究的预分发范围问题
- [assets/skills.follow-up.md](assets/skills.follow-up.md) — 技能目录研究的预分发范围问题
- [assets/docs.follow-up.md](assets/docs.follow-up.md) — 文档平台研究的预分发范围问题

## 安全性与约束

永远不要：
- 编造融合框架钩子、EDS 属性或技能目录条目
- 当 MCP 不可用或结果较弱时声称证据存在
- 无限期地不断细化 — 在每个代理一次细化后声明不确定性
- 在研究流程中实plement代码更改或突变存储库

始终：
- 在选择代理之前对问题进行分类
- 在最终确定任何声明之前捕获来源路径和支撑摘录
- 明确说明哪个代理和来源支持答案的每个部分
