请精确执行以下命令一次，且不更改当前工作目录。将 `{project-root}` 替换为项目根目录的绝对路径，将 `{skill-root}` 替换为此技能目录的绝对路径：

```bash
uv run --no-cache "{project-root}/_bmad/scripts/render_skill.py" --project-root "{project-root}" --skill "{skill-root}"
```

- 若成功，该命令将打印 `read and follow` 以及渲染后的 `workflow.md` 的绝对路径。请阅读该文件并按照其指示操作。
- 如果找不到脚本，说明此处未正确设置 BMad。建议运行 `bmad` 技能的设置，如果尚未安装 `bmad`，则先安装它（`npx skills add bmad-code-org/BMAD-METHOD --skill bmad`），然后再次运行上述命令。
- 对于任何其他失败情况（包括 `uv` 不可用），请报告命令输出并停止执行。不要直接运行任何工作流源代码。
