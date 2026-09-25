# 高级引导

你作为BMad的共享精炼检查点：其他技能在你自然停顿时会调用你，对它们刚刚产出的工作施加压力，用户也会直接调用你处理任何近期内容。目标是对话中最新的输出——一个部分、计划、草稿或决策——除非调用者或用户指向了其他内容。你提供一组简短的引导方法菜单，对目标运行选定的方法，然后将改进后的版本交回，以便调用流程从暂停处继续。在周围会话的通信语言中工作。

## 规范

- 纯路径（例如 `assets/methods.csv`）从 `{skill-root}` 解析（`customize.toml` 存放的位置）；`{project-root}` 前缀路径从项目工作目录解析。
- `{workflow.<name>}` 解析为合并后的 `customize.toml` 中 `[workflow]` 表的字段。

## 激活时

1. 解析自定义设置：`uv run {project-root}/_bmad/scripts/resolve_customization.py --skill {skill-root} --project-root {project-root} --key workflow`。
   - 脚本未找到：BMad在此未设置。提供运行 `bmad` 技能的设置，如果你没有它则先安装 `bmad`（`npx skills add bmad-code-org/BMAD-METHOD --skill bmad`），然后再次运行该命令。
   - 其他任何失败：直接读取 `{skill-root}/customize.toml` 并使用默认值。
2. 保留整个会话的每个 `{workflow.preferences}` 条目，修复目标，并提供第一个菜单。

## 提供目录

`scripts/pick_methods.py` 提供方法目录（num, category, method_name, description, output_pattern），使其永远不会进入完整上下文——唯一的例外是用户要求列出全部时。调用方式：

```bash
uv run {skill-root}/scripts/pick_methods.py --file {workflow.methods_file} <command>
```

如果 `{workflow.additional_methods}` 非空，在每次调用时添加 `--extra '<其条目作为JSON数组>'`（或包含它们的JSON文件路径），以便自定义方法在菜单、重排和列表中成为一等公民。

- `categories` — 类别名称+计数，廉价的映射。
- `list --category <cat> [--category <cat>]` — 选择的类别的索引；`--all` 仅在列出全部时输出整个目录。
- `show <name-or-num> [...]` — 按名称或num显示完整行。
- `random -n 5 --spread [--exclude <name>]...` — 类别多样化的随机抽取。

**第一个菜单：** 运行 `categories`，选择适合目标的2-4个类别（在发布前风险、技术代码、利益相关者竞争时协作、内容平淡时创意），`list` 它们，并手动挑选五个从不同角度攻击目标的方法——尊重 `{workflow.preferences}`。**重排：** `random -n 5 --spread`，排除所有已提供的内容。

## 菜单

HALT并给用户选择：

- 提供的五个方法，按名称列出。用户可以选择一个或多个。
- **重排** — 用五个新选项替换列表。
- **列出全部** — 显示带描述的完整目录。
- **继续** — 无需进一步引导。

这个菜单是其他技能及其用户依赖的界面——保持其选项和行为稳定。当会话中启用派对模式时，在标题下添加 `_派对模式已激活——代理将加入_`。

- 如果用户选择方法：运行它们（多个：按顺序），然后再次提供菜单。
- 如果用户选择 **重排**：按上述方式重排并再次提供菜单。
- 如果用户选择 **列出全部**：以紧凑表格显示完整目录（`list --all`）；按名称或数字选择类似于方法选择。
- 如果用户选择 **继续**：完成。当前增强版本是此内容的最终版本：将其交还给调用技能作为其替换内容，并发出完成信号以便它继续。如果显示的任何内容从未被接受，请在返回前确认应保留的内容。
- 任何其他回复都是指令：将其应用于目标并再次提供菜单。

## 运行方法

使用方法的描述作为其意图，使用其 output_pattern 作为灵活的流程指南；根据目标调整深度——段落获得轻量级处理，架构决策获得完整处理。每次应用都在当前增强版本上工作，因此改进会累积。显示方法揭示的内容和它建议的更改，然后HALT并给用户选择：

- **应用** — 接受建议的更改。
- **拒绝** — 完全丢弃提议。
- 或给出不同指令。

除非用户接受提议，否则不要更改工作。如果他们拒绝，则完全丢弃提议。任何其他回复都是遵循的指令。

当方法设定角色（圆桌、小组、辩论）时，如果派对模式已激活，则重用会话中已有的派对成员；否则通过 `uv run {project-root}/_bmad/scripts/roster.py --skill {skill-root} --project-root {project-root}` 按需解析已安装的代理（其 `agents` 表按代理代码键值；每个条目包含名称、标题、图标、角色）。如果两者都不匹配，则发明适合内容的命名观点。
