---
name: bmad-retrospective
description: 在工单树中审查完成的史诗文件夹，对照其留下的证据——史诗文件、每个工单计划、差异、提交记录——并生成一份包含来源证据、行动项和接受决策的回顾报告。当用户说“运行回顾”或“我们来回顾史诗[史诗名称]”时使用。支持 -H/--headless 参数。
---

请精确执行以下命令一次，且不更改当前工作目录。将 `{project-root}` 替换为项目根目录的绝对路径，将 `{skill-root}` 替换为此技能目录的绝对路径：

```bash
uv run --no-cache "{project-root}/_bmad/scripts/render_skill.py" --project-root "{project-root}" --skill "{skill-root}"
```

- 若成功，请读取并遵循标准输出中打印的单一绝对路径 `workflow.md` 指令。
- 若脚本未找到，则表示此处未正确设置 BMad。建议运行 `bmad` 技能的设置，若尚未安装 `bmad` 则先进行安装（`npx skills add bmad-code-org/BMAD-METHOD --skill bmad`），然后再次执行上述命令。
- 对于任何其他失败情况（包括 `uv` 不可用），请报告命令输出并停止执行。不要直接运行任何工作流源代码。
