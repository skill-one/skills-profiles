---
name: harness-creator
description: 构建、审计和改进使 AI 编码代理可靠的工具：AGENTS.md/CLAUDE.md 指令文件、功能/状态跟踪、验证门、作用域边界、会话交接、内存持久化、上下文预算、工具权限安全以及多代理协调。每当编码代理在会话间不可靠时（忘记上下文、超出作用域、在测试通过前声称“完成”或每次会话启动不一致）——或创建或评估 AGENTS.md、CLAUDE.md、feature_list.json、init.sh、progress.md 或会话交接文件时——都可以使用它。即使用户从未说出“工具”这个词，也可以使用它。
---

# Harness Creator

使用此技能使代码代理更容易开始、保持范围、验证工作并在会话之间恢复。保持 harness 小到代理实际上会遵循它。

不用于模型选择、单独的提示调整、聊天 UI 设计或通用应用程序架构。

## 核心模型

每个有用的代码代理 harness 都有五个子系统：

| 子系统 | 最小化工件 | 目的 |
|---|---|---|
| 指令 | `AGENTS.md` 或 `CLAUDE.md` | 启动路径、工作规则、完成定义 |
| 状态 | `feature_list.json`、`progress.md` | 当前功能、状态、证据、下一步 |
| 验证 | `init.sh` 或文档化命令 | 在声明完成之前代理必须运行的测试/检查 |
| 范围 | 功能依赖关系和完成标准 | 防止越界和未完成的工作 |
| 生命周期 | `session-handoff.md`、会话结束例程 | 使下一个会话可重新启动 |

## 首次操作

1. 检查已存在的内容：指令文件、功能/状态文件、验证命令、文档、包清单。
2. 仅请求无法安全推断的缺失上下文：目标代理、期望的文件名、结构容忍度以及是否允许覆盖。
3. 首先偏好最小化 harness。仅在用户的问题需要时才添加内存、工具安全、多代理或基准细节。

## 常见任务

### 创建 harness

在处理本地仓库时使用捆绑脚本：

```bash
node skills/harness-creator/scripts/create-harness.mjs --target /path/to/project
```

选项：

- `--agent-file CLAUDE.md` 用于 Claude 导向的项目。
- `--package-manager npm|pnpm|yarn|bun` 当检测错误时。
- `--commands "cmd one,cmd two"` 用于自定义验证。
- `--force` 仅在确认可以覆盖时使用。

然后解释创建的内容以及用户应如何替换占位符功能条目。

### 审计现有 harness

运行：

```bash
node skills/harness-creator/scripts/validate-harness.mjs --target /path/to/project
```

报告五个子系统的得分、最低得分区域以及会提高可靠性的前 2-3 个更改。将最低分数视为潜在的瓶颈；在声明因果关系之前，请通过失败、日志或任务结果进行确认。

### 生成报告

在用户需要可共享的评估时使用：

```bash
node skills/harness-creator/scripts/render-assessment-html.mjs --target /path/to/project
node skills/harness-creator/scripts/run-benchmark.mjs --target /path/to/project --html /path/to/report.html
```

明确说明这是一个结构基准。基准首先运行自检——它构建一个一次性 harness 并验证它，证明捆绑脚本端到端工作正常——然后评分目标并评估覆盖率。实际有效性仍需要在代表性任务上执行前/后代理会话。

## 何时阅读参考

仅加载用户问题所需的参考：

- 跨会话记忆：[记忆持久化](references/memory-persistence-pattern.md)
- 可重用工作流作为技能：[技能运行时](references/skill-runtime-pattern.md)
- 权限、工具、并发：[工具注册表与安全](references/tool-registry-pattern.md)
- 上下文预算和渐进式披露：[上下文工程](references/context-engineering-pattern.md)
- 委托和并行代理：[多代理协调](references/multi-agent-pattern.md)
- 钩子、启动、长时间运行的工作：[生命周期与引导](references/lifecycle-bootstrap-pattern.md)
- 非明显失败模式：[陷阱](references/gotchas.md)

## 设计规则

- 保持根指令文件简短：路由和不变性，而不是完整手册。
- 将项目事实放在项目文档中，而不是放在技能中。
- 使验证命令明确且可运行。
- 在标记功能完成之前要求证据。
- 除非 harness 有明确的多代理所有权边界，否则使用一个活动功能。
- 优先使用追加/更新状态文件，而不是依赖聊天历史。
- 永远不要在脚本中隐藏破坏性行为；覆盖需要明确用户批准。

## 交付物清单

对于可用的最小 harness，保留目标项目：

- [ ] `AGENTS.md` 或 `CLAUDE.md`
- [ ] `feature_list.json`
- [ ] `progress.md`
- [ ] `init.sh`
- [ ] 可选 `session-handoff.md` 用于多会话工作
- [ ] 文档化的验证证据或下一步操作

如果您无法创建文件，请提供确切的文件内容和命令。
