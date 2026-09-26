# 软件架构设计

使用这项技能来处理**已知解决方案形状内部的深度软件和平台架构决策**，而不是单个服务或组件内的实现细节。

如果问题从业务工作流、系统景观、目标状态或分阶段的跨系统迁移开始，请先使用 [../software-solution-architecture/SKILL.md](../software-solution-architecture/SKILL.md)，然后再来这里处理运行时、分解和可操作性深度。

将资产现代化、平台工程和 AI 原生互操作性视为可选的深度探讨。除非用户明确要求这些关注点，否则不要加载它们。

## 快速参考

| 任务 | 模式/工具 | 关键资源 | 使用场景 |
|------|-------------|---------------|-------------|
| 选择架构风格 | 分层、微服务、事件驱动、无服务器 | [modern-patterns.md](references/modern-patterns.md) | 绿地项目、重大重构 |
| 为扩展性设计 | 负载均衡、缓存、分片、读写副本 | [scalability-reliability-guide.md](references/scalability-reliability-guide.md) | 高流量系统、性能目标 |
| 确保弹性 | 电路断路器、重试、隔离舱、优雅降级 | [scalability-reliability-guide.md](references/scalability-reliability-guide.md) | 分布式系统、外部依赖 |
| 记录决策 | 架构决策记录 (ADR) | [adr-template.md](assets/planning/adr-template.md) | 重大技术决策、权衡分析 |
| 定义服务边界 | 域驱动设计 (DDD)、边界上下文 | [microservices-template.md](assets/patterns/microservices-template.md) | 微服务分解 |
| 建模数据一致性 | ACID vs BASE、事件溯源、CQRS、Saga 模式 | [data-architecture-patterns.md](references/data-architecture-patterns.md) | 多服务事务 |
| 规划可观察性 | SLIs/SLOs/SLAs、分布式追踪、指标、日志 | [architecture-blueprint.md](assets/planning/architecture-blueprint.md) | 生产就绪 |
| 从单体迁移 | 骚扰树、数据库分解、影子流量 | [migration-modernization-guide.md](references/migration-modernization-guide.md) | 遗产现代化 |
| 设计跨服务通信 | API 网关、服务网格、BFF 模式 | [api-gateway-service-mesh.md](references/api-gateway-service-mesh.md) | 微服务网络 |
| 设计交付平台 | IDP、黄金路径、适配函数 | [fitness-functions-governance.md](references/fitness-functions-governance.md) | 多团队平台、治理 |
| 理由化服务蔓延 | 边界上下文平台、仓库 vs 运行时矩阵、平台记分卡 | [estate-modernization.md](references/estate-modernization.md) | 20+ 仓库、服务过多、平台成熟度不均 |
| 规划资产现代化 | 平台优先迁移浪潮、整合、兼容性边界 | [estate-modernization-blueprint.md](assets/planning/estate-modernization-blueprint.md) | 多仓库资产、监管迁移、遗产减少 |
| 设计 AI 原生系统 | RAG 边界、工具网关、代理互操作性、MCP、A2A | [architecture-trends.md](references/architecture-trends.md) | LLM 驱动的产品，当架构而不是实现是主要问题时 |

## 何时使用此技能

在以下情况下调用：

- **已知解决方案内部的软件形状**：将选定的解决方案形状转化为运行时边界、边界上下文和平台决策
- **系统分解**：决定单体、模块化单体还是微服务
- **架构模式**：事件驱动、CQRS、分层、六边形、无服务器
- **平台架构**：内部开发者平台、黄金路径、策略和交付护栏
- **资产现代化**：仓库过多、运行时单元过多、多仓库合理化、平台优先的运营模式
- **数据架构**：一致性模型、分片、复制、CQRS 模式
- **可扩展性设计**：负载均衡、缓存策略、数据库扩展
- **弹性模式**：电路断路器、重试、隔离舱、优雅降级
- **API 边界设计**：服务到服务的契约姿态、版本策略和集成形状，当边界决策是架构时
- **架构决策**：ADR、权衡分析、技术选择
- **迁移规划**：单体分解、骚扰树、数据库分离
- **AI 原生架构**：RAG 边界、工具网关和互操作性协议，当请求是架构级别而不是工具/服务器实现时

## 何时不要使用此技能

对于以下情况，请使用其他技能：

- **跨系统解决方案设计**（业务流程、目标状态、集成景观、跨系统的分阶段过渡）→ [software-solution-architecture](../software-solution-architecture/SKILL.md)
- **单个服务实现**（路由、控制器、业务逻辑）→ [software-backend](../software-backend/SKILL.md)
- **API 端点设计**（REST 规范、GraphQL 模式）→ [dev-api-design](../dev-api-design/SKILL.md)
- **安全实现**（认证、加密、OWASP）→ [software-security-appsec](../software-security-appsec/SKILL.md)
- **前端组件架构** → [software-frontend](../software-frontend/SKILL.md)
- **数据库查询优化** → [data-sql-optimization](../data-sql-optimization/SKILL.md)
- **代理工作流实现 / MCP 服务器实现** → [ai-agents](../ai-agents/SKILL.md), [agents-mcp](../agents-mcp/SKILL.md)

## 边界规则

- 此技能拥有运行时边界、可部署单元决策、数据一致性权衡、弹性内部和平台默认值。
- 从满足约束的最简单架构开始；不要默认使用微服务、事件溯源、服务网格或多代理拆分，除非有明确证据。
- 如果未解决的问题仍然是“哪些系统参与、记录系统在哪里、目标状态景观是什么？”请返回到 [software-solution-architecture](../software-solution-architecture/SKILL.md)。
- 如果未解决的问题是实现代理协议、工具服务器或特定于运行时的集成，请路由到 [ai-agents](../ai-agents/SKILL.md) 或 [agents-mcp](../agents-mcp/SKILL.md)。

## 选择架构模式的决策树

```text
主要问题：[这是什么类型的架构问题？]
    ├─ 大型资产，许多仓库/服务，认知负荷上升？
    │   ├─ 运行时数量是主要问题 → 边界上下文平台 + 选择性整合
    │   ├─ 交付不一致是主要问题 → IDP + 黄金路径 + 记分卡
    │   └─ 两者都是真 → 平台优先现代化，然后整合低价值运行时单元
    │
    ├─ 确定性工作流，已知步骤？
    │   ├─ 单个可部署可接受 → 模块化单体
    │   ├─ 需要独立团队/能力 → 顺序或事件驱动服务
    │   └─ 爆发驱动或边缘触发工作负载 → 无服务器 / 事件驱动
    │
    ├─ 适应性工作流，使用工具和推理？
    │   ├─ 一个代理可以拥有任务 → 单代理系统
    │   ├─ 真正需要专业化角色 → 多代理，带明确停止条件
    │   └─ 高风险/监管工作流 → 人机交互 + 审计跟踪
    │
    ├─ 单个域边界内强一致性？
    │   ├─ 保持数据和写入在一起 → 单体或模块化单体
    │   └─ 仅在稳定边界上下文中拆分 → 带拥有数据的微服务
    │
    └─ 需要跨许多团队的平台级一致性？
        ├─ 重复服务创建 / 合规性需求 → IDP + 黄金路径
        └─ 跨代理或跨供应商互操作性 → 工具/上下文的 MCP，代理到代理的 A2A
```

**决策因素：**

- **默认姿态**：优先选择模块化单体而不是微服务，除非独立部署、所有权和可操作性优势明显——请参阅 [modern-patterns.md § 模块化单体 vs 微服务](references/modern-patterns.md#modular-monolith-vs-microservices-explicit-gates-2026-default)
- **资产姿态**：在减少仓库之前优化减少运行时单元；仓库是协作单元，运行时是运营成本中心
- **代理姿态**：优先选择确定性工作流或单个代理，然后再引入多代理协调
- **连接性姿态**：优先选择网关加应用库模式，直到 mTLS、流量策略或共享遥测需要证明网格复杂性
- 团队结构（康威定律）——架构反映组织结构
- 部署独立性需求
- 一致性和故障域边界
- 运营成熟度（监控、编排）
- 互操作性需求（协议、契约、外部系统）

**拆分点**（Skelton 和 Pais，《团队拓扑》，第二版，2025 年）。拆分点是“软件系统中一个自然的接缝，允许系统轻松拆分为两个或多个部分”——石匠的类比。候选平面：业务域边界上下文（默认，也是大多数拆分应映射到的平面）、监管合规、变更节奏、团队位置、风险、性能隔离、技术和用户角色。

- **测试点**，引用： “结果架构是否支持更自治的团队（较少依赖的团队）和减少认知负荷（较少不同的职责）？” 具体来说：拆分后，每个团队是否可以在不与其他团队协调的情况下构建、测试和部署其部分？
- **组合规则**：真实边界通常组合平面——“我们可以并且应该通过组合不同类型的拆分平面来分解单体，”以及“通常需要组合多种拆分平面。”
- **分布式单体警告**：在不将边界与团队及其发布路径对齐的情况下拆分软件，以获取分布式成本而没有自治性。书中引用了 Amy Phillips： “如果你有微服务，但在发布之前等待测试它们组合，那么你有一个分布式单体。” 耦合也悄悄地侵入服务边界以下——共享数据库、耦合构建和发布。
- 使段为团队规模： “必须使软件段为团队规模，以便团队可以有效地拥有和演进其软件，以可持续的方式。”

参见 [references/modern-patterns.md](references/modern-patterns.md) 获取详细的模式描述，以及 [references/modern-patterns.md § Connascence](references/modern-patterns.md#connascence-a-finer-grained-coupling-vocabulary) 检查建议的接缝是否留下强耦合。

## 输出指南

此技能中的参考是您的背景知识——吸收模式并将其作为您自己的专业知识呈现。不要在面向用户的输出中引用内部参考文件名（例如，“来自 data-architecture-patterns.md”）。用户不知道这些文件存在。

每个架构建议都必须涵盖以下内容；只有在有明确理由的情况下才跳过元素：

- [ ] **最简单的足够拓扑** — 说明仍然满足要求的最简单架构
- [ ] **具体技术选择** — 指定具体技术（例如，“Temporal.io 用于工作流编排”，而不是“一个编排器”）
- [ ] **推荐选项 + 被拒绝的替代方案** — 考虑了什么，为什么替代方案失败了
- [ ] **不要构建什么** — 明确推迟或排除过早的范围
- [ ] **团队和流程对齐** — CODEOWNERS、部署所有权、呼叫边界
- [ ] **仓库和运行时模型** — 对于多仓库资产，区分仓库数量和可部署数量
- [ ] **可操作性模型** — 部署拓扑、故障域、回滚点、SLO 所有权、事件边界
- [ ] **迁移路径** — 顺序、切换策略、可逆性（用于重构或新子系统）
- [ ] **关键风险和故障模式** — 命名的断点，如何早期检测
- [ ] **成功指标** — 可衡量的指标：部署频率、响应时间、错误率、MTTR

## 工作流（系统级）

当用户要求架构建议、分解或重大平台决策时，使用此工作流。

1. 澄清：问题陈述、非目标、约束和成功指标
2. 捕获质量属性：可用性、延迟、吞吐量、持久性、一致性、安全性、合规性、成本
3. 决定工作负载形状：确定性工作流、单代理或多代理；同步 vs 异步
4. 提出 2–3 个候选架构并比较权衡
5. 在证明更分布式模式之前，默认使用最简单的可行拓扑
6. 对于 20+ 仓库资产，将每个仓库分类为运行时、适配器、库、通道、平台、工具或吸收候选
7. 定义边界：边界上下文、所有权、API/事件、协议契约、互操作性需求
8. 决定数据策略：存储、一致性模型、模式演化、迁移
9. 针对运营设计：SLO、故障模式、可观察性、部署、灾难恢复、事件剧本
10. 设计治理和安全：策略执行、可审计性、评估门禁、回滚控制
11. 指出范围限制：不要构建什么，什么要推迟，什么要购买 vs 构建
12. 记录决策：为关键权衡和不可逆选择编写 ADR

首选交付物（根据请求选择什么适合）：

- 架构蓝图：`assets/planning/architecture-blueprint.md`
- 资产现代化蓝图：`assets/planning/estate-modernization-blueprint.md`
- 决策记录：`assets/planning/adr-template.md`
- 模式深入探讨：`references/modern-patterns.md`, `references/scalability-reliability-guide.md`

### 决策证据门禁

对于每个建议的边界或新可部署项，命名需要它的观察压力：独立发布节奏、不兼容的扩展形状、故障隔离、数据主权或不同所有权。记录基线和将选择证伪的实验。如果压力是假设性的或可以在现有运行时内部处理，请保持逻辑边界并推迟运营拆分。

## ASCII 流程

```text
架构设计请求
  -> 定义质量属性和系统边界
  -> 映射域模型、依赖关系和故障模式
  -> 选择架构模式和集成风格
  -> 记录拒绝的选项和权衡
  -> 定义迁移、可观察性和验证检查
  -> 交接可实现的决策和开放风险
```

## 已知陷阱

- 因为资产已经有许多仓库而选择微服务，即使运行时蔓延和弱所有权才是真正的问题。
- 在没有迁移顺序、回滚边界或旧路径和新路径之间的兼容性计划的情况下绘制目标状态图。
- 在所有权、呼叫和部署权限准备好支持额外的表面区域之前拆分域。
- 在决定哪些路径实际上需要解耦之前，在所有边界上引入异步和事件驱动工作流。
- 在将某物称为平台工程时，黄金路径仍然是可选的、不一致的或未拥有的。

## 常见反模式

- 使用可部署服务作为默认分解单元，而不是边界上下文、团队所有权和运营成本。
- 将超大规模或供应商参考架构复制到没有同等规模、工具或平台人员配置的团队中。
- 设计用于峰值可选未来，而不是当前吞吐量、故障、合规性和变更管理约束。
- 因为每个都有“一些价值”而保留每个仓库和运行时，尽管存在明显的协调和治理成本。
- 混淆“现代”与“更分布式”和“AI 原生”与“默认多代理”。

## 导航

### 核心参考

每项问题最多阅读 **2–3 个参考**——选择与特定请求最相关的。不要阅读所有参考。

| 参考 | 内容 | 何时阅读 |
|-----------|----------|--------------|
| [modern-patterns.md](references/modern-patterns.md) | 11 个架构模式，包括决策树，包括模块化单体 vs 微服务的门禁和基于细胞的架构 | 选择或比较模式 |
| [scalability-reliability-guide.md](references/scalability-reliability-guide.md) | CAP 定理、数据库扩展、缓存、电路断路器、SRE | 扩展或可靠性问题 |
| [data-architecture-patterns.md](references/data-architecture-patterns.md) | CQRS 变体、事件溯源、数据网格、Saga 模式、一致性 | 跨服务数据流 |
| [migration-modernization-guide.md](references/migration-modernization-guide.md) | 骚扰树、数据库分解、特性标志、风险评估 | 重构单体 |
| [api-gateway-service-mesh.md](references/api-gateway-service-mesh.md) | 网关模式、服务网格、mTLS、可观察性 | 跨服务通信 |
| [fitness-functions-governance.md](references/fitness-functions-governance.md) | 适配函数分类（六个轴）、架构 vs 域和监控 vs 警报测试、ArchUnit/NetArchTest/linter 规则、放牧阈值、耦合和复杂性指标 | 自动化架构治理，使原则可执行 |
| [architecture-trends.md](references/architecture-trends.md) | 平台工程、环境网格、AI 原生系统、MCP/A2A | 当前趋势仅 |
| [estate-modernization.md](references/estate-modernization.md) | 运行时 vs 仓库合理化、边界上下文平台、整合启发式 | 多仓库资产和服务蔓延 |
| [operational-playbook.md](references/operational-playbook.md) | 架构问题框架、分解启发式 | 设计讨论框架 |

### 模板

**规划 & 文档** ([assets/planning/](assets/planning/)):

- [architecture-blueprint.md](assets/planning/architecture-blueprint.md) — 服务蓝图（依赖关系、SLA、数据流、弹性、安全、可观察性）
- [estate-modernization-blueprint.md](assets/planning/estate-modernization-blueprint.md) — 资产蓝图（仓库/运行时分类、目标平台映射、迁移浪潮、记分卡）
- [adr-template.md](assets/planning/adr-template.md) — 用于权衡分析的架构决策记录 (ADR)

**架构模式** ([assets/patterns/](assets/patterns/)):

- [microservices-template.md](assets/patterns/microservices-template.md) — 微服务设计（API 合同、弹性、部署、测试）
- [event-driven-template.md](assets/patterns/event-driven-template.md) — 事件驱动架构（事件模式、Saga 模式、事件溯源）

**运营** ([assets/operations/](assets/operations/)):

- [scalability-checklist.md](assets/operations/scalability-checklist.md) — 可扩展性清单（数据库扩展、缓存、负载测试、自动扩展、灾难恢复）

### 验证

- [evals/evals.json](evals/evals.json) — 此技能的触发、非触发和边界行为检查

### 应用配方工具包

- [references/decision-theory-applied.md](references/decision-theory-applied.md) — 架构决策理论的配方：ADR 带有 EU + 敏感性，不可逆选择的真实期权，VoI 在尖峰上。
- [references/queueing-theory-applied.md](references/queueing-theory-applied.md) — 应用排队理论的配方：服务尺寸、背压拓扑、尾部延迟预算。
- [references/theory-of-constraints-applied.md](references/theory-of-constraints-applied.md) — 应用约束理论的配方：系统瓶颈搜索，重构范围，稳定性 vs 速度 ADR。
- [references/distributed-systems-applied.md](references/distributed-systems-applied.md) — 应用分布式系统原语到架构：CAP 感知的 服务边界，共识算法选择，API 表面幂等性，带 fencing 的领导者选举工作，多数票尺寸，一致性 vs 延迟 ADR 模板。
- [references/reliability-theory-applied.md](references/reliability-theory-applied.md) — 应用可靠性原语（MTBF/MTTR、可用性、FMEA、错误预算）到软件架构设计。

### 相关技能

- [software-solution-architecture](../software-solution-architecture/SKILL.md) — 端到端解决方案设计，系统景观，目标状态和迁移架构
- [software-backend](../software-backend/SKILL.md) — 后端工程，API 实现，数据层
- [software-frontend](../software-frontend/SKILL.md) — 前端架构，微前端，状态管理
- [dev-api-design](../dev-api-design/SKILL.md) — REST、GraphQL、gRPC 设计模式
- [ops-devops-platform](../ops-devops-platform/SKILL.md) — CI/CD、部署策略，IaC
- [qa-observability](../qa-observability/SKILL.md) — 监控、追踪、告警、SLO
- [software-security-appsec](../software-security-appsec/SKILL.md) — 威胁建模，认证，安全设计
- [data-sql-optimization](../data-sql-optimization/SKILL.md) — 数据库设计，优化，索引
- [docs-codebase](../docs-codebase/SKILL.md) — 架构文档，文档作为代码结构
- `docs-diagram-design` — 图表是否值得其位置，以及它必须显示什么
- [ai-agents](../ai-agents/SKILL.md) — 代理系统设计，编排，评估
- [agents-mcp](../agents-mcp/SKILL.md) — MCP 服务器/客户端模式和集成

## 新鲜度协议

当用户询问有关架构模式、平台工程或 AI 原生系统的版本敏感问题时，在回答之前验证当前信息。

### 触发条件

- “[用例] 的最佳架构是什么？”
- “微服务 vs 单体——当前推荐是什么？”
- “平台工程 / 服务网格 / AI 架构的最新进展是什么？”
- “如何现代化 50/100+ 仓库或减少服务蔓延？”
- “[模式] 仍然推荐吗？”

### 如何进行新鲜度检查

1. 从 `data/sources.json` 开始，优先选择官方文档、标准、发布说明和生命周期页面。
2. 运行针对特定架构模式或平台的定向网络搜索。
3. 仅将非主要来源用作持久的背景，而不是新鲜度权威。

仅在问题明确涉及当前趋势、供应商特定约束、AI 原生架构或“关于 X 的最新想法是什么？”时加载。

- [references/architecture-trends.md](references/architecture-trends.md) — 平台工程，环境网格，MCP/A2A 互操作性，AI 原生系统
- [references/estate-modernization.md](references/estate-modernization.md) — 资产合理化，边界上下文平台，平台优先迁移姿态
- [data/sources.json](data/sources.json) — 按类别组织的精选资源：
  - `platform_engineering_2026` — IDP、软件目录和模板驱动的平台默认值
  - `estate_modernization_2026` — 骚扰迁移、反腐败层、仓库 vs 运行时指南
  - `optional_ai_architecture` — MCP/A2A 协议和架构级别的 AI 互操作性参考
  - `modern_architecture_2026` — 环境网格和其他版本敏感的平台模式

如果可以访问实时网络，则咨询 `data/sources.json` 中的 2–3 个权威来源，并将发现结果合并到建议中。如果没有，请用持久的模式回答，并明确说明可能改变的假设（供应商限制、定价、托管服务功能或生命周期状态）。

## 事实核查

- 已知错误、回归、框架/编译器/运行时陷阱，以及版本特定崩溃或解决方法指导必须与当前主要网络来源进行验证，然后才能将其视为当前事实。

## 学习循环

当先前的决策或陷阱相关时，如果存在，请咨询 `learnings.consolidated.md`；仅用于需要历史记录或作为可用回退使用 `learnings.md`。否则跳过两者。

应用后，如果您遇到了值得记住的模式、值得防止的错误或让您惊讶的领域事实，请通过 `agents-skills-feedback-loop/scripts/append_learning.py` 添加一条带日期的简短说明到 `learnings.md`。不要修改 `SKILL.md` 本身。
