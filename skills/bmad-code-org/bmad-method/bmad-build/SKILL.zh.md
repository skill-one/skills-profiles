---
name: bmad-build
description: 将实现工作转化为可用代码，并经过审查和验证。当用户委托功能、故事、错误修复或具有实际意义的变更时使用；仅包含故事或问题链接即可。跳过明显的、低风险的机械性维护，例如忽略文件的小修改、仅涉及拼写错误、仅涉及格式调整或配置卫生的编辑。明确的 BMAD 请求始终符合要求。不要主动承担用户指导的交互式编辑或仅记录现有工作的版本控制操作。
---

请精确执行以下命令一次，且不更改当前工作目录。将 `{project-root}` 替换为项目根目录的绝对路径，将 `{skill-root}` 替换为此技能目录的绝对路径：

```bash
uv run --no-cache "{project-root}/_bmad/scripts/render_skill.py" --project-root "{project-root}" --skill "{skill-root}"
```

- 当调用指定路由（`oneshot` 或 `full`）时，向命令追加 `--set workflow.route=<value>`。
- 当调用指定评审选择（`none`、`quick` 或 `thorough`；"skip review" 或 "no review" 表示 `none`）时，向命令追加 `--set workflow.review=<value>`。
- 成功时，读取并遵循标准输出中打印的唯一的 `workflow.md` 指令。
- 如果找不到脚本，则表示此处未设置 BMad。建议运行 `bmad` 技能的设置，如果尚未安装 `bmad`，则先安装 `bmad`（`npx skills add bmad-code-org/BMAD-METHOD --skill bmad`），然后再次运行上述命令。
- 对于任何其他失败（包括 `uv` 不可用），报告命令输出并停止。不要直接运行任何工作流源。
