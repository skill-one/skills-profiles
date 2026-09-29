---
name: bmad-code-review
description: 并行地与多个独立审阅者一起审查代码变更，然后进行分诊并展示结果。当用户说“运行代码审查”或“审查此代码”时使用。
---

请精确执行以下命令一次，且不更改当前工作目录。将 `{project-root}` 替换为项目根目录的绝对路径，将 `{skill-root}` 替换为此技能目录的绝对路径：

```bash
uv run --no-cache "{project-root}/_bmad/scripts/render_skill.py" --project-root "{project-root}" --skill "{skill-root}"
```

- 当调用指定评审选择（`quick` 或 `thorough`）时，需在命令中追加 `--set workflow.review=<value>`。
- 成功时，读取并遵循标准输出中打印的唯一的绝对 `workflow.md` 指令。
- 如果找不到脚本，则表示此处未正确设置 BMad。建议运行 `bmad` 技能的设置，如果尚未安装 `bmad`，则先安装 (`npx skills add bmad-code-org/BMAD-METHOD --skill bmad`)，然后再次执行上述命令。
- 对于任何其他失败情况（包括 `uv` 不可用），需报告命令输出并停止。不要直接运行任何工作流源。
