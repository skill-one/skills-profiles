# analyze-project

将此作为 Rigor Analyze / Rigor Audit 只读技能使用。已安装标识符（slug）
仍为 `analyze-project`，以兼容需要。

使用
`../ai-research-reproduction/references/agent-operating-principles.md` 中的共享操作原则；该技能应指导只读分析，而不限制模型的特定项目推理。

## When to apply

- 当用户希望在修改深度学习仓库之前理解该仓库时。
- 用户需要模型结构、训练入口点、推理入口点以及配置关系的映射。
- 用户需要关于可能插入点或可疑实现模式的保守建议。
- 用户明确要求只读分析，而非大量执行操作。

## When not to apply

- 当主要任务是执行失败的命令或调试 traceback 时。
- 当用户仅需要环境配置或资源下载时。
- 当用户需要推测性适配或广泛探索性补丁时。
- 当任务是与仓库分析无关的一般文献总结时。

## Clear boundaries

- 该技能以只读为主。
- 它可以运行轻量级静态检查辅助工具。
- 它不对仓库代码进行补丁。
- 它不拥有最终复现输出。
- 它应将可疑模式标记为启发式（经验规则），而非已确认的 bug。

## Output expectations

- `analysis_outputs/SUMMARY.md`
- `analysis_outputs/RISKS.md`
- `analysis_outputs/status.json`

## Notes

使用 `references/analysis-policy.md` 以及共享的 `../ai-research-reproduction/references/research-pitfall-checklist.md`。
