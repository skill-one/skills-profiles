请精确执行以下命令一次，且不更改当前工作目录。将 `{project-root}` 替换为项目根目录的绝对路径，将 `{skill-root}` 替换为此技能目录的绝对路径：

```bash
uv run --no-cache "{project-root}/_bmad/scripts/render_skill.py" --project-root "{project-root}" --skill "{skill-root}"
```

- 若成功，请读取并遵循标准输出中打印的单一绝对路径 `workflow.md` 指令。
- 若脚本未找到，则表示此处未正确设置 BMad。建议运行 `bmad` 技能的设置，并在您尚未安装 `bmad` 的情况下先进行安装（`npx skills add bmad-code-org/BMAD-METHOD --skill bmad`），然后再次执行上述命令。
- 对于任何其他失败情况（包括 `uv` 不可用），请报告命令输出并停止。不要直接运行任何工作流源代码。
