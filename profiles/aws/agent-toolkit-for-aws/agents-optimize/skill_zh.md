# 优化

通过评估、监控和可观察性来衡量和提升您的 AgentCore 代理的质量。

## 使用场景

- 您想知道您的代理是否提供良好的答案
- 您想在生产环境中设置持续质量监控
- 您想在 CI/CD 管道中添加质量门禁
- 您想通过日志、指标和跟踪来了解代理行为
- 您想设置 CloudWatch 仪表板或 X-Ray 跟踪

不应用于：

- 调试特定的故障代理（错误答案、错误）→ 使用 `agents-debug`
- 生产环境安全加固（IAM、认证）→ 使用 `agents-harden`

## 输入

`$ARGUMENTS` 可以是：

- 一个评估目标： "添加质量门禁"、"设置监控"
- 一个可观察性目标： "设置 CloudWatch 仪表板"、"理解我的跟踪"
- 一个特定的评估器： "llm-as-a-judge"、"基于代码"
- 空的 — 技能将根据项目上下文进行指导

## 流程

### 第 0 步：验证 CLI 版本

运行 `agentcore --version`。此技能需要 v0.9.0 或更高版本。

### 第 1 步：读取项目上下文

读取 `agentcore/agentcore.json` 以了解现有的评估器、在线评估配置和代理设置。

如果找不到 `agentcore/agentcore.json`：
> "此技能需要一个 AgentCore 项目。使用 `agents-get-started` 来创建一个。"

### 第 2 步：确定工作流程

| 开发者意图 | 操作 |
|---|---|
| 衡量质量、添加评估器、运行评估、CI/CD 门禁、在线监控 | 加载 [`references/evals.md`](references/evals.md) 并遵循其工作流程 |
| 设置可观察性、CloudWatch、X-Ray、日志、指标、仪表板 | 加载 [`references/observability.md`](references/observability.md) 并遵循其工作流程 |
| 了解或减少 AgentCore 成本 | 加载 [`references/cost.md`](references/cost.md) |
| 两者 — "我想了解和改进我的代理" | 从可观察性设置开始，然后添加评估 |

### 第 3 步：遵循加载的参考

参考文件包含完整步骤。按步骤进行。

### 交叉引用

- 设置评估后，建议 `agents-harden` 以确保生产就绪
- 如果评估结果揭示代理问题，建议 `agents-debug` 进行根本原因分析
- 如果开发者需要先添加功能，建议 `agents-build`

## 输出

取决于工作流程 — 具体输出请查看加载的参考。

## 质量标准

- 评估器配置仅使用有效的 CLI 标志
- 在线评估采样率适当（生产环境中未经讨论不得为 100%）
- CI/CD 质量门禁具有明确的通过/失败阈值
- 可观察性设置包括跟踪和日志记录
- 开发者了解评估数据延迟：**~10 秒的 put-to-get，端到端** — 一个摄入步骤涵盖跟踪读取和评估查询；没有单独的索引等待
