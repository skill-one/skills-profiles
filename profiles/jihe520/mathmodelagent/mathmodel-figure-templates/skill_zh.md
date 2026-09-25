# MathModel 图表模板

该技能包含在 LaTeX 沙盒中 `/home/user/.claude/skills/mathmodel-figure-templates`，其中包含 MathModel 改进选项卡中提供的图表模板的即用型 Python/matplotlib 脚本。

## 快速路径

1. 在 `references/figure-catalog.md` 中匹配请求的图表。
2. 从 `/home/user/workspace` 运行渲染器并指定模板 ID：

```bash
python3 /home/user/.claude/skills/mathmodel-figure-templates/scripts/render_template.py paired-raincloud
```

3. 渲染器将捆绑的模板脚本复制到 `绘图复刻/scripts/`，在那里运行它，并将输出写入 `绘图复刻/outputs/`。
4. 将生成的 PNG/PDF/SVG 路径和复制的脚本路径返回给用户。

使用 `--list` 显示支持的 ID：

```bash
python3 /home/user/.claude/skills/mathmodel-figure-templates/scripts/render_template.py --list
```

## 输出契约

- 在当前工作区下工作，除非用户提供其他路径。
- 默认项目文件夹：`绘图复刻`。
- 脚本路径：`绘图复刻/scripts/make_<template>.py`。
- 输出：`绘图复刻/outputs/<template>_replica.png`, `.pdf`, `.svg`。
- 优先使用捆绑脚本；仅在用户要求自定义时才编辑复制的工区脚本。
- 捆绑脚本使用确定性模拟数据。不要声称模拟值精确再现了源研究。

## 模板 ID

- `multiclass-shap-combo`
- `paired-raincloud`
- `cv-roc-ci`
- `taylor-diagram`
- `correlation-pairgrid`
- `prediction-marginal-grid`
- `rf-tpe-surface`
- `grouped-corr-split-violin`
- `grouped-circular-heatmap`
- `urban-park-cooling-combo`
- `nature-chord-diagram`

## 自定义时

如果用户要求更改，首先复制/运行最近的模板，然后在 `绘图复刻/scripts/` 中编辑复制的文件。保留：

- 导入 matplotlib 之前的 `MPLCONFIGDIR`。
- 模拟数据的确定性种子。
- PNG/PDF/SVG 导出。
- 可读的标签、图例和高 DPI 输出。

使用 `references/plot-recipes.md` 获取实现模式。
