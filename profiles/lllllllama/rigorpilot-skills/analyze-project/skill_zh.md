# analyze-project

将此用作 Rigor Analyze / Rigor Audit 的只读技能。安装的 slug 保持为 `analyze-project` 以确保兼容性。

使用 `../ai-research-reproduction/references/agent-operating-principles.md` 中的共享操作原则；该技能应指导只读分析，而不会限制模型针对特定项目的推理。

## 何时应用

- 用户希望在更改深度学习存储库之前了解其内容。
- 用户需要一个模型结构、训练入口点、推理入口点和配置关系的地图。
- 用户希望获得关于可能插入点或可疑实现模式的保守建议。
- 用户明确希望进行只读分析，而不是执行大量操作。

## 何时不应用

- 主要任务是执行失败命令或调试回溯时。
- 用户只需要环境设置或资产下载时。
- 用户希望进行推测性适应或广泛探索性补丁时。
- 任务是一般性文献综述，无需存储库分析时。

## 明确边界

- 此技能以只读为主。
- 它可能运行轻量级的静态检查辅助工具。
- 它不会修补存储库代码。
- 它不拥有最终的复现输出。
- 它应将可疑模式标记为启发式方法，而不是确认的 Bug。

## 输出预期

- `analysis_outputs/SUMMARY.md`
- `analysis_outputs/RISKS.md`
- `analysis_outputs/status.json`

## 备注

使用 `references/analysis-policy.md` 和共享的 `../ai-research-reproduction/references/research-pitfall-checklist.md`。
