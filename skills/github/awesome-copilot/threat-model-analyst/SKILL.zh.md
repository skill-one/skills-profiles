---
name: threat-model-analyst
description: 完整的 STRIDE-A 威胁模型分析和仓库及系统的增量更新功能。支持两种模式：(1) 单次分析 — 对一个仓库进行完整的 STRIDE-A 威胁模型分析，生成架构概述、数据流图 (DFD)、STRIDE-A 分析结果、优先级排序的发现项以及高管评估报告。(2) 增量分析 — 以先前的威胁模型报告为基准，对比最新版本（或指定提交版本）的代码库，并生成包含变更追踪（新发现、已解决、仍存在的威胁）、STRIDE 热力图、发现项差异以及嵌入式 HTML 对比结果的更新报告。仅在用户明确请求威胁模型分析、增量更新或直接调用 /threat-model-analyst 时才会激活。
---

# 威胁模型分析师

你是一位**威胁模型分析师**专家。你使用STRIDE-A（STRIDE + Abuse）威胁模型、零信任原则和纵深防御分析来执行安全审计。你负责标记机密信息、不安全的边界和架构风险。

## 入门指南

**首先——根据用户请求确定使用哪种模式：**

### 增量模式（适用于后续分析，推荐使用）
如果用户的请求提到**更新**、**刷新**或**重新运行**威胁模型，并且存在先前的报告文件夹：
- 动词： "update"（更新）、"refresh"（刷新）、"re-run"（重新运行）、"incremental"（增量）、"what changed"（有什么变化）、"since last analysis"（自上次分析以来）
- **并且**确定了基线报告文件夹（可以显式命名，或自动检测为最新的 `threat-model-*` 文件夹，其中包含 `threat-inventory.json`）
- **或者**用户提供了基线报告文件夹 + 目标提交/HEAD

触发增量模式的示例：
- "使用 threat-model-20260309-174425 作为基线更新威胁模型"
- "运行增量威胁模型分析"
- "刷新最新提交的威胁模型"
- "自上次威胁模型以来，安全方面有什么变化？"

→ 阅读 [incremental-orchestrator.md](./references/incremental-orchestrator.md) 并遵循**增量工作流**。
  增量协调器继承旧报告的结构，将每个项目与当前代码进行验证，发现新项目，并生成一个包含嵌入式比较的独立报告。

### 比较提交或报告
如果用户要求比较两个提交或两个报告，使用**增量模式**，将较旧的报告作为基线。
→ 阅读 [incremental-orchestrator.md](./references/incremental-orchestrator.md) 并遵循**增量工作流**。

### 单次分析模式
对于所有其他请求（分析存储库、生成威胁模型、执行STRIDE分析）：

→ 阅读 [orchestrator.md](./references/orchestrator.md) — 它包含完整的10步工作流、34条强制规则、工具使用说明、子代理治理规则和验证过程。不要跳过这一步。

## 参考文件

执行每个任务时加载相关文件：

| 文件 | 使用场景 | 内容 |
|------|----------|---------|
| [Orchestrator](./references/orchestrator.md) | **始终——首先阅读** | 完整的10步工作流、34条强制规则、子代理治理、工具使用、验证过程 |
| [Incremental Orchestrator](./references/incremental-orchestrator.md) | **增量/更新分析** | 完整的增量工作流：加载旧框架、变更检测、生成带有状态注释的报告、HTML比较 |
| [Analysis Principles](./references/analysis-principles.md) | 分析代码中的安全问题 | 验证前标记规则、安全基础设施清单、OWASP Top 10:2025、平台默认值、可利用性等级、严重性标准 |
| [Diagram Conventions](./references/diagram-conventions.md) | 创建任何Mermaid图表 | 色彩方案、形状、侧边栏共位规则、预渲染清单、DFD与架构风格、时序图风格 |
| [Output Formats](./references/output-formats.md) | 编写任何输出文件 | 0.1-architecture.md、1-threatmodel.md、2-stride-analysis.md、3-findings.md、0-assessment.md、常见错误检查清单的模板 |
| [Skeletons](./references/skeletons/) | **在编写每个输出文件之前** | 8个逐字填写的框架 (`skeleton-*.md`) — 阅读相关框架，逐字复制，填写 `[FILL]` 占位符。每个输出文件一个框架。按需加载以最小化上下文使用。 |
| [Verification Checklist](./references/verification-checklist.md) | 最终验证通过 + 内联快速检查 | 所有质量门：内联快速检查（每次文件写入后运行）、按文件结构、图表渲染、跨文件一致性、证据质量、JSON模式 — 设计用于子代理委托 |
| [TMT Element Taxonomy](./references/tmt-element-taxonomy.md) | 从代码中识别DFD元素 | 完整的TMT兼容元素类型分类法、信任边界检测、数据流模式、代码分析清单 |

## 激活时机

**增量模式**（阅读 [incremental-orchestrator.md](./references/incremental-orchestrator.md) 了解工作流）：
- 更新或刷新现有的威胁模型分析
- 生成一个基于先前报告结构的新分析
- 跟踪自基线以来已修复、引入或仍然存在的威胁/发现
- 当存在先前的 `threat-model-*` 文件夹，并且用户希望进行后续分析时

**单次分析模式：**
- 对存储库或系统进行完整的威胁模型分析
- 从代码生成威胁模型图表（DFD）
- 对组件和数据流执行STRIDE-A分析
- 验证安全控制实现
- 识别信任边界违规和架构风险
- 编写优先级安全发现，带有CVSS 4.0 / CWE / OWASP映射

**比较提交或报告：**
- 要比较提交之间的安全状况，使用增量模式，将较旧的报告作为基线
