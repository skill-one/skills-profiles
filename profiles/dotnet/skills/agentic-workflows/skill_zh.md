# 代理工作流路由器

当用户要求设计、创建、更新、调试或升级此存储库中的 GitHub 代理工作流时，请使用此技能。

该技能是一个调度器：识别任务类型，加载匹配的工作流提示/技能文件，并直接遵循。保持响应简洁，如果正确的提示不明确，请询问澄清问题。

存储库覆盖（可选）：
- 如果存在 `.github/aw/instructions.md`，则在加载匹配的提示/技能后，使用 `@.github/aw/instructions.md` 加载它。
- 优先级：存储库覆盖指令在冲突时覆盖上游默认值。

仅读取您需要的文件：
从 `github/gh-aw` 加载这些文件（它们在本地不可用）。
- `.github/aw/action-container-substitutions.md`
- `.github/aw/agent-runtime-instructions.md`
- `.github/aw/agentic-chat.md`
- `.github/aw/agentic-workflows-mcp.md`
- `.github/aw/asciicharts.md`
- `.github/aw/campaign.md`
- `.github/aw/charts-trending.md`
- `.github/aw/charts.md`
- `.github/aw/cli-commands.md`
- `.github/aw/compat.md`
- `.github/aw/configure-agentic-engine.md`
- `.github/aw/context.md`
- `.github/aw/create-agentic-workflow-trigger-details.md`
- `.github/aw/create-agentic-workflow.md`
- `.github/aw/create-shared-agentic-workflow.md`
- `.github/aw/debug-agentic-workflow.md`
- `.github/aw/dependabot.md`
- `.github/aw/deployment-status.md`
- `.github/aw/designer-mappings.md`
- `.github/aw/designer.md`
- `.github/aw/drive-memory.md`
- `.github/aw/enclaves.md`
- `.github/aw/evals.md`
- `.github/aw/experiments.md`
- `.github/aw/github-agentic-workflows.md`
- `.github/aw/github-mcp-server-pagination.md`
- `.github/aw/github-mcp-server-tools.md`
- `.github/aw/github-mcp-server.md`
- `.github/aw/instructions.md`
- `.github/aw/intent.md`
- `.github/aw/jobs.md`
- `.github/aw/linter-workflows.md`
- `.github/aw/llms.md`
- `.github/aw/loop.md`
- `.github/aw/lsp.md`
- `.github/aw/maintainer.md`
- `.github/aw/mcp-clis.md`
- `.github/aw/memory-stateful-patterns.md`
- `.github/aw/memory.md`
- `.github/aw/messages.md`
- `.github/aw/multi-agent-research.md`
- `.github/aw/network.md`
- `.github/aw/optimize-agentic-workflow.md`
- `.github/aw/patterns.md`
- `.github/aw/playwright.md`
- `.github/aw/pr-reviewer.md`
- `.github/aw/release-workflow.md`
- `.github/aw/report.md`
- `.github/aw/reuse.md`
- `.github/aw/safe-outputs-automation.md`
- `.github/aw/safe-outputs-content.md`
- `.github/aw/safe-outputs-management.md`
- `.github/aw/safe-outputs-runtime.md`
- `.github/aw/safe-outputs.md`
- `.github/aw/serena-tool.md`
- `.github/aw/shared-safe-jobs.md`
- `.github/aw/skills.md`
- `.github/aw/subagents.md`
- `.github/aw/syntax-agentic.md`
- `.github/aw/syntax-core.md`
- `.github/aw/syntax-engine.md`
- `.github/aw/syntax-tools-imports.md`
- `.github/aw/syntax.md`
- `.github/aw/test-coverage.md`
- `.github/aw/test-expression.md`
- `.github/aw/token-optimization-caching-budgets.md`
- `.github/aw/token-optimization-observability.md`
- `.github/aw/token-optimization.md`
- `.github/aw/triggers.md`
- `.github/aw/update-agentic-workflow.md`
- `.github/aw/upgrade-agentic-workflows.md`
- `.github/aw/visual-regression.md`
- `.github/aw/workflow-constraints.md`
- `.github/aw/workflow-editing.md`
- `.github/aw/workflow-patterns.md`

加载匹配的工作流提示或技能后，直接遵循：
- 通过访谈从头开始设计工作流：`.github/aw/designer.md`
- 创建新工作流：`.github/aw/create-agentic-workflow.md`
- 配置或添加声明性引擎：`.github/aw/configure-agentic-engine.md`
- 更新现有工作流：`.github/aw/update-agentic-workflow.md`
- 调试、审计或调查工作流：`.github/aw/debug-agentic-workflow.md`
- 升级工作流并修复弃用项：`.github/aw/upgrade-agentic-workflows.md`
- 创建共享组件或 MCP 包装器：`.github/aw/create-shared-agentic-workflow.md`
- 创建生成报告的工作流：`.github/aw/report.md`
- 修复 Dependabot 架构 PR：`.github/aw/dependabot.md`
- 分析覆盖工作流：`.github/aw/test-coverage.md`
- 渲染紧凑型 markdown 图表：`.github/aw/asciicharts.md`
- 将 CLI 命令映射到 MCP 使用：`.github/aw/cli-commands.md`
- 选择工作流架构和模式：`.github/aw/patterns.md`
- 优化 token 使用和成本：`.github/aw/token-optimization.md`
- 设计长时间运行的多代理研究工作流：`.github/aw/multi-agent-research.md`
- 添加用户请求的技能或代理插件（`skills:` / `plugins:` 前置，永不动态安装）：`.github/aw/skills.md`

当任务涉及 OTEL、OTLP、跟踪、可观察性后端或遥测驱动分析时，在加载匹配的工作流提示或技能后，也读取并遵循 `skills/otel-queries/SKILL.md`。
