# dt-alerting

配置和理解 Dynatrace 中的完整告警生命周期——从异常检测器设置开始，通过 Grail 事件存储、问题分组和工作流通知交付。

## 告警生命周期

```
┌─────────────────────────────────────────────────────────────────────┐
│  告警源 — 五种类别，每种都会触发一个 DAVIS_EVENT                  │
│  ─────────────────────────────────────────────────────────────────  │
│  1. 基于 DQL 的  · Grail 定时服务器端检测器                      │
│  2. 边缘       · 监控主机或进程上的 OneAgent                     │
│  3. 流水线   · OpenPipeline 吞吐流过滤器匹配器                  │
│  4. 合成       · 全球合成检查器节点                               │
│  5. 外部       · 事件 API、工作流或 OneAgent 本地摄取             │
└──────────────────────────────┬──────────────────────────────────────┘
                               │ 每个触发器每个实体创建一个 DAVIS_EVENT
                               ▼
             ┌─────────────────────────────────────┐
             │  事件存储在 Grail                  │  通过 DQL 持久化并查询。
             └──────────────────┬──────────────────┘  每个触发器每个实体一个事件。
                                │ 通过根本原因和影响图关联
                                ▼
             ┌─────────────────────────────────────┐
             │  问题（去噪）                │  共享相同根本原因和影响图的事件
             └──────────────────┬──────────────────┘  → 一个问题。
                                │ 问题事件触发工作流
                                ▼
             ┌─────────────────────────────────────┐
             │  工作流通知              │  过滤问题并路由到
             └─────────────────────────────────────┘  邮件、Slack、ServiceNow、webhook。
```

## 何时使用此技能

- **检测器设置** — "我该如何创建一个异常检测器？"、"我应该使用哪种检测器？"、"自适应和季节性的区别是什么？"
- **告警事件历史** — "查询此服务的所有告警事件"、"显示上周触发告警的指标"
- **问题去噪** — "为什么这两个告警合并为一个问题？"、"Davis 如何分组告警？"
- **通知设置** — "当问题打开时如何发送 Slack 消息？"、"在关键问题上设置 ServiceNow 工单"
- **最佳实践** — "如何避免告警风暴？"、"我应该使用哪种灵敏度设置？"
- **过度告警分析** — "为什么我收到太多告警？"、"如何减少告警疲劳？"、"哪个检测器触发的最多？"、"如何调整灵敏度或阈值以避免噪声？"
- **通知路由** — "如何将告警路由到正确的团队？"、"在工作流中设置可扩展的问题过滤器"、"仅向负责受影响服务的团队发送 Slack 通知"

## 代理指令

**任何告警设置请求的第一步** — 在推荐特定检测器或模型之前，加载 `references/anomaly-detectors.md` 并使用其类别和模型决策指南来识别哪个检测器类别（基于 DQL、边缘、流水线、合成、外部）和哪个模型（静态、自适应、季节性）最适合用户的用例。只有在确定正确的检测器类型后，才能进行配置指导。

**合并，不要重复** — 当用户要求对同一类型的多个实体进行告警（例如："对服务 A、B 和 C 进行告警"）时，始终推荐一个**单个组合检测器**，而不是每个实体一个检测器。在 DQL `timeseries` 调用中使用 `by: { <维度> }` 来按实体拆分结果，并使用单个 `filter:` 子句来范围到相关实体。将组合检测器与一个**单个 `dt.alert_group` 标签**配对，该标签在所有告警条件和相应的工作流通知过滤器中共享。这可以保持检测器配置数量较少，确保一致的路由，并使工作流通知通道可重复用于将来添加到同一组的新实体。

三个服务的示例——一个检测器，一个工作流：

```dql
timeseries avg(dt.service.request.response_time),
  by: { dt.smartscape.service },
  filter: { in(dt.smartscape.service, {toSmartscapeId("SERVICE-0000000000000001"), toSmartscapeId("SERVICE-0000000000000002"), toSmartscapeId("SERVICE-0000000000000003")}) }
```

在检测器的事件属性中设置 `dt.alert_group: "checkout-team"`，然后在通知工作流中过滤 `matchesPhrase(dt.alert_group, "checkout-team")`。如果必须覆盖新服务，则将其添加到单个 `filter:` 列表中——无需新的检测器或工作流规则。

### 意图映射

| 用户请求 | 操作 | 参考 |
|---|---|---|
| "如何告警..."、"创建告警..."、"创建异常检测器"、"设置告警"、"配置告警规则" | 解释检测器类别和变体，指导模型选择 | anomaly-detectors.md |
| "哪些类型的异常检测器"、"边缘告警"、"流水线告警"、"合成告警"、"OneAgent 告警" | 解释五种告警源类别及其权衡 | anomaly-detectors.md |
| "静态与自适应"、"哪个检测器模型"、"季节性检测器" | 比较模型，应用决策指南 | anomaly-detectors.md |
| "查询告警历史"、"哪些告警被触发"、"Grail 中的 Davis 事件" | 通过 `fetch dt.davis.events` 在 Grail 中查询 `dt.davis.events` | davis-events.md |
| "为什么告警合并"、"问题分组"、"去噪" | 不要在此处解释合并规则——加载 `dt-obs-problems` 并参考 `problem-merging.md` 以获取完整的合并逻辑 | dt-obs-problems/references/problem-merging.md |
| "发送 Slack 通知"、"问题时发送邮件"、"ServiceNow 工单"、"告警时通知" | 解释问题触发的工作流设置 | workflow-notifications.md |
| "告警风暴"、"通知过多"、"减少噪声" | 过滤策略、去噪、灵敏度调整 | workflow-notifications.md + anomaly-detectors.md |

> **分析现有问题** — 如果用户想要查询或调查活动/已关闭的问题（根本原因、影响、趋势），请加载 `dt-obs-problems`。此技能涵盖 *配置和流程*，不涵盖问题查询分析。

> **检测器健康监控** — 如果用户询问检测器是否运行或失败，请加载 `dt-platform`（ANALYZER_EXECUTION_EVENT、ANOMALY_DETECTOR_STATUS_EVENT）。此技能涵盖 *设置*，不涵盖运行健康。

## 前提条件

- 访问具有检测器配置的 Dynatrace 环境，并具有 Settings v2 的写入权限
- 查询告警历史需要 `dt.davis.events` 的 DQL 权限
- 在编写 DQL 查询之前加载 `dt-dql-essentials`

## 知识库结构

| # | 参考 | 内容 |
|---|-----------|---------|
| 1 | [anomaly-detectors.md](references/anomaly-detectors.md) | 检测器类型、模型选择、配置、最佳实践 |
| 2 | [davis-events.md](references/davis-events.md) | Grail 中的 Davis 事件存储、关键字段、DQL 查询模式 |
| 3 | [workflow-notifications.md](references/workflow-notifications.md) | 问题触发的工作流、过滤、通知通道 |

## 关键概念

### 告警源类别

五种基本的异常检测器类别，通过检测运行位置和告警事件如何到达 Dynatrace 来区分：

| # | 类别 | 检测运行在 | 延迟 | 告警逻辑所有者 |
|---|----------|-------------------|---------|-------------------|
| 1 | **基于 DQL** | Grail（服务器端，定时） | 分钟 | Dynatrace |
| 2 | **边缘** | 监控主机/进程上的 OneAgent | 秒 | Dynatrace (OneAgent) |
| 3 | **流水线** | OpenPipeline 吞吐流（流内） | 近零 | Dynatrace (流水线规则) |
| 4 | **合成** | 合成检查器节点（全球） | 秒 | Dynatrace (合成节点) |
| 5 | **外部** | 客户端/外部工具 | 调用者定义 | 客户端 |

有关每个类别的完整分解，包括权衡和配置入口点，请参阅 `references/anomaly-detectors.md`。

### 检测器模型概览

| 模型 | 阈值 | 最适合 |
|-------|-----------|----------|
| **静态** | 固定值 | 已知的硬 SLO 边界（例如：错误率 > 5%） |
| **自适应基线** | 从最近历史中学习 | 没有固定限制但具有明显正常行为的指标 |
| **季节性基线** | 具有时间/日意识学习 | 交通、请求率或任何具有周期性模式的指标 |

### Davis 事件与问题

| 概念 | 表 | 范围 |
|---------|-------|-------|
| **Davis 事件** | `fetch dt.davis.events` | 每个触发器每个实体一个记录 |
| **问题** | `fetch dt.davis.problems` | 每个共享根本原因和影响的事件相关组一个记录 |

一个问题通常包含多个事件。查询问题提供操作视图；查询事件提供原始告警历史。

### 问题去噪

有关为什么告警合并为一个问题或 Davis 如何分组事件的问题，请加载 `dt-obs-problems`——合并逻辑和规则在 `dt-obs-problems/references/problem-merging.md` 中记录。此技能仅涵盖告警 *配置和流程*。

## 快速入门

### 检查过去 24 小时内触发的告警

```dql
fetch dt.davis.events, from: -24h
| filter event.status == "ACTIVE"
| summarize alert_count = count(), by: {event.name, event.category, dt.smartscape_source.id}
| sort alert_count desc
| limit 20
```

### 按类别检查告警量

```dql
fetch dt.davis.events, from: -24h
| summarize count = count(), by: {event.category, event.status}
| sort count desc
```

### 查看所有活动问题（→ 加载 dt-obs-problems 以获取完整查询模式）

```dql
fetch dt.davis.problems, from: -24h
| filter not(dt.davis.is_duplicate) and event.status == "ACTIVE"
| fields event.start, display_id, event.name, event.category
| sort event.start desc
| limit 20
```

## 最佳实践

1. **将模型与指标的行為匹配** — 使用静态来匹配硬 SLO 边界，自适应来匹配没有自然固定限制的指标，季节性来匹配遵循工作时间或每周模式的任何指标。
2. **狭义地范围检测器** — 一个仅覆盖相关实体的实体选择器可以减少噪声，并使问题更具可操作性。
3. **在生产之前调整灵敏度** — 从 LOW 灵敏度开始，只有在观察到误报率后才能移动到 MEDIUM 或 HIGH。
4. **让 Davis 在通知之前去噪** — 在 *问题* 上触发工作流通知，而不是单个告警事件。一个问题会分组相关告警，因此您只需每个事件通知一次，而不是每个指标通知一次。
5. **按严重程度级别过滤通知** — 立即将 `event.severity <= 2` 的问题路由到呼叫通道；将 `event.severity >= 3` 的问题路由到低优先级通道。可以在检测器配置中设置严重程度，也可以在流水线规则或工作流中分配。
6. **使用 `dt.alert_group` 事件属性进行路由** — 分配 `dt.alert_group` 以将告警路由到正确的团队。可以在检测器配置中设置静态值，通过 DQL 查询结果映射动态分配，或在流水线规则中分配。
7. **将相同条件的告警合并为一个检测器和一个工作流** — 当对具有相同指标和阈值的多个实体进行告警时，使用 `by: { <维度> }` 和一个组合 `filter:` 子句将它们合并为一个基于 DQL 的检测器。在检测器中的每个条件中都分配相同的 `dt.alert_group` 值，并将工作流通知通道指向该单个组。一个检测器 + 一个工作流每个逻辑告警组比 N 个检测器 + N 个通知规则扩展得更好，添加新实体只需一行过滤更改，而不是完整的检测器/工作流添加。

## 相关技能

- **dt-obs-problems** — 查询、分析和趋势检测到的问题
- **dt-obs-predictive-analytics** — 使用 MCP 分析器工具进行临时异常和新颖性检测（不是持久的告警配置）
- **dt-platform** — 异常检测器的运行健康
- **dt-platform-costs** — 查询由异常检测器 DQL 产生的成本
- **dt-sdlc-quality-gates** — 部署门告警的站点可靠性监护人
- **dt-dql-essentials** — 编写检测器查询和告警历史查询的 DQL 语法
