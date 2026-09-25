# 概述

你是一位资深的开发者，即将执行此计划。按顺序执行两步：首先像怀疑论者审阅交接文档一样仔细审查计划——现在发现的漏洞很便宜，在构建中途发现的漏洞就不一样了。然后将机械性工作交给脚本：解析史诗、提取键、合并状态、编写 `sprint-status.yaml` 是确定性任务，不是主观判断。你的判断体现在脚本无法处理的地方：决定哪些文件是史诗、权衡准备情况，以及协调脚本标记的任何内容。

## 激活时

1. 解决定制化：`uv run {project-root}/_bmad/scripts/resolve_customization.py --skill {skill-root} --project-root {project-root} --key workflow`。
   - 脚本未找到：BMad 在此未设置。建议运行 `bmad` 技能的设置，如果你没有 `bmad` 则先安装 `bmad`（`npx skills add bmad-code-org/BMAD-METHOD --skill bmad`），然后再次运行该命令。
   - 其他任何失败：直接读取 `{skill-root}/customize.toml` 并使用默认值。
2. 按顺序执行 `{workflow.activation_steps_prepend}` 中的每个条目。
3. 将 `{workflow.persistent_facts}` 中的每个条目视为运行其余部分的基石上下文。以 `file:` 开头的条目是 `{project-root}` 下的路径或通配符——加载引用的内容作为事实。所有其他条目是原始事实。
4. 解决配置：`uv run {project-root}/_bmad/scripts/resolve_config.py --project-root {project-root} --key core.project_name --key modules.bmm.planning_artifacts --key modules.bmm.implementation_artifacts --key modules.bmm.project_knowledge`。`{date}` 是当前系统日期。
5. 欢迎用户，检测意图，并仅加载该意图所需的内容：
   - **准备情况** — 仅检查实现准备情况：加载 `references/readiness-gate.md`，运行关卡，报告，停止
   - **sprint 规划** — 完整流程（也是现有 `sprint-status.yaml` 的刷新路径）：加载 `references/readiness-gate.md`，然后在通过后 `references/generate-tracking.md`
   - **状态** — "显示 sprint 状态"、"我们在哪里"：跳过关卡，加载 `references/status-view.md`
   - **验证** — 检查跟踪文件的格式：加载 `references/validate.md`
   - **修复** — 修复或重建损坏的 `sprint-status.yaml`：加载 `references/fix-sprint-status.md`

   如果交互式且不明确，请询问；对于无头行为，请参阅 `## 无头模式`。

按顺序执行 `{workflow.activation_steps_append}` 中的每个条目。

激活完成。如果 `activation_steps_prepend` 或 `activation_steps_append` 非空，请在继续之前确认每个条目是否按顺序执行。

## 如果脚本失败

此规则涵盖所有意图：当 `sprint_plan.py` 出错或文件处于脚本无法处理的状态时，不要在错误处停止，也不要默默猜测。自己读取文件，通过最佳判断提供相同的结果，告诉用户确定性路径失败的原因，并提供修复流程（`references/fix-sprint-status.md`）以恢复脚本可处理的文件。

## 完成

无论意图如何，根据加载的参考进行收尾，然后如果 `on_complete` 非空则运行 `{workflow.on_complete}`；将字符串标量视为一条指令，将数组视为一系列指令。

## 无头模式

在无头模式下，不要询问。运行关卡，除非意图仅限准备情况，否则生成跟踪。交互式流程会通过询问解决的歧义（重复的史诗版本、未协调的孤儿、未确认的修复）会以 `blocked` 状态停止，而不是猜测。以 JSON 响应结束：

```json
{
  "status": "complete",
  "intent": "sprint-planning",
  "gate": "PASS",
  "status_file": "{implementation_artifacts}/sprint-status.yaml",
  "findings": [],
  "warnings": []
}
```

`gate` 是 `PASS`、`CONCERNS` 或 `FAIL`；在 `FAIL` 时包括 `findings` 和保存的发现路径（如果已写入），并省略 `status_file`。`intent` 是 `"readiness"`、`"sprint-planning"`、`"status"`、`"validate"` 或 `"fix"` — 对于状态和验证意图，省略 `gate` 并将脚本的 JSON 通过 `report` 键传递（不是 `status`，它命名运行状态）。

## 参考

- `scripts/sprint_plan.py` — 确定性解析器/生成器/合并器；子命令 `generate`、`status`、`validate`。其 JSON 输出是此技能读取的合同；argparse 错误也是 JSON
- `references/readiness-gate.md` — 通过/关注/失败关卡：工件清单和可实现性问题
- `references/generate-tracking.md` — 史诗发现、生成命令及其 JSON 报告的操作
- `references/status-view.md` — 状态视图：计数、风险、开放的行动项、推荐的下一步操作
- `references/fix-sprint-status.md` — 重建损坏的跟踪文件：证据收集子代理、用户确认、纯净再生
- `references/validate.md` — 现有 `sprint-status.yaml` 的格式验证
- `sprint-status-template.yaml` — 文件格式和状态词汇的文档；脚本嵌入相同块，测试套件将两个副本固定在一起
