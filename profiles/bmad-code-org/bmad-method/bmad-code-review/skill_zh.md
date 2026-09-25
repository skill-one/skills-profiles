请精确执行以下命令一次，且不更改当前工作目录。将 `{project-root}` 替换为项目根目录的绝对路径，将 `{skill-root}` 替换为此技能目录的绝对路径：

```bash
uv run --no-cache "{project-root}/_bmad/scripts/render_skill.py" --project-root "{project-root}" --skill "{skill-root}"
```

- 当调用中指定评审选择（`quick` 或 `thorough`）时，向命令追加 `--set workflow.review=<value>`。
- 成功时，读取并遵循标准输出中打印的唯一的绝对 `workflow.md` 指令。
- 如果找不到脚本，则表示此处未设置 BMad。建议运行 `bmad` 技能的设置，如果尚未安装 `bmad`，则先安装 `bmad`（`npx skills add bmad-code-org/BMAD-METHOD --skill bmad`），然后再次执行上述命令。
- 对于任何其他失败（包括 `uv` 不可用），报告命令输出并停止。不要直接运行任何工作流源。
