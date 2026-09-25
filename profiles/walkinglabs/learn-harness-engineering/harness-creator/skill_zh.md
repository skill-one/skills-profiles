# Harness Creator

使用此技能使代码代理更容易开始、保持范围、验证工作并在会话间恢复。保持 harness 小到代理实际上会遵循它。

不用于模型选择、单独的提示调整、聊天 UI 设计或通用应用程序架构。

## 核心模型

每个有用的代码代理 harness 都有五个子系统：

| 子系统 | 最小工件 | 目的 |
|---|---|---|
| 指令 | `AGENTS.md` 或 `CLAUDE.md` | 启动路径、工作规则、完成定义 |
| 状态 | `feature_list.json`、`progress.md` | 当前功能、状态、证据、下一步 |
| 验证 | `init.sh` 或文档化命令 | 代理在声明完成前必须运行的测试/检查 |
| 范围 | 功能依赖和完成标准 | 防止越界和未完成的工作 |
| 生命周期 | `session-handoff.md`、会话结束例程 | 使下一个会话可重启 |

## 首次操作

1. 检查已存在的内容：指令文件、功能/状态文件、验证命令、文档、包清单。
2. 仅请求无法安全推断的缺失上下文：目标代理、期望的文件名、结构容忍度以及是否允许覆盖。
3. 首先偏好最小 harness。仅在用户问题需要时才添加内存、工具安全、多代理或基准细节。

## 常见任务

### 创建 harness

在本地仓库工作时使用捆绑脚本：

```bash
node skills/harness-creator/scripts/create-harness.mjs --target /path/to/project
```

选项：

- `--agent-file CLAUDE.md` 用于 Claude 导向项目。
- `--package-manager npm|pnpm|yarn|bun` 当检测错误时。
- `--commands "cmd one,cmd two"` 用于自定义验证。
- `--force` 仅在确认覆盖可接受后使用。

然后解释创建的内容以及用户应如何替换占位符功能条目。

### 审计现有 harness

运行：

```bash
node skills/harness-creator/scripts/validate-harness.mjs --target /path/to/project
```

报告五个子系统的评分、最低分区域以及会提高可靠性的前 2-3 个更改。将最低分视为候选瓶颈；在确认失败、日志或任务结果之前不要声称因果关系。

### 生成报告

当用户需要可共享的评估时使用：

```bash
node skills/harness-creator/scripts/render-assessment-html.mjs --target /path/to/project
node skills/harness-creator/scripts/run-benchmark.mjs --target /path/to/project --html /path/to/report.html
```

明确说明这是一个结构基准。基准首先运行自检——搭建一个一次性 harness 并验证它，证明捆绑脚本端到端工作正常——然后评分目标并评估覆盖率。实际有效性仍需在代表性任务上运行前/后代理会话。

## 何时阅读参考

仅加载用户问题所需的参考：

- 跨会话记忆：[Memory Persistence](references/memory-persistence-pattern.md)
- 可重用工作流作为技能：[Skill Runtime](references/skill-runtime-pattern.md)
- 权限、工具、并发：[Tool Registry & Safety](references/tool-registry-pattern.md)
- 上下文预算和渐进式披露：[Context Engineering](references/context-engineering-pattern.md)
- 委托和并行代理：[Multi-Agent Coordination](references/multi-agent-pattern.md)
- 钩子、启动、长时间运行工作：[Lifecycle & Bootstrap](references/lifecycle-bootstrap-pattern.md)
- 非明显失败模式：[Gotchas](references/gotchas.md)

## 设计规则

- 保持根指令文件简短：路由和不变式，不是完整手册。
- 将项目事实放在项目文档中，而不是技能中。
- 使验证命令明确且可运行。
- 在标记功能完成前要求证据。
- 除非 harness 有明确的多代理所有权边界，否则使用一个活动功能。
- 优先使用追加/更新状态文件，而不是依赖聊天历史。
- 脚本中永远不要隐藏破坏性行为；覆盖需要明确用户批准。

## 交付物清单

对于可用的最小 harness，保留目标项目：

- [ ] `AGENTS.md` 或 `CLAUDE.md`
- [ ] `feature_list.json`
- [ ] `progress.md`
- [ ] `init.sh`
- [ ] 可选 `session-handoff.md` 用于多会话工作
- [ ] 文档化的验证证据或下一步操作

如果无法创建文件，请提供确切的文件内容和命令。
