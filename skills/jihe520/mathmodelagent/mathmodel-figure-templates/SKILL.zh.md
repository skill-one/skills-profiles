---
name: mathmodel-figure-templates
description: 在 MathModel LaTeX 沙箱中，当用户要求复现内置科学可视化模板时，请使用此技能。特别是，当“改进（Improve）”选项卡中的提示提及 $mathmodel-figure-templates、科研绘图模板、SHAP蜂群柱状图、配对云雨图、交叉验证ROC、泰勒图、相关矩阵组合图、预测值与真实值边缘分布图、TPE调参3D曲面、下三角相关矩阵半边小提琴图、分组环形热图、城市公园降温组合图，或 Nature 和弦图时。该技能内部捆绑了可直接运行的 Python 脚本。
---

# MathModel 图表模板

该技能已打包到 LaTeX 沙盒中，位于 `/home/user/.claude/skills/mathmodel-figure-templates`。它包含 MathModel 改进选项卡中提供的图表模板的即用型 Python/matplotlib 脚本。

## 快速路径

1. 在 `references/figure-catalog.md` 中匹配请求的图表。
2. 从 `/home/user/workspace` 运行渲染器，并指定模板 ID：

```bash
python3 /home/user/.claude/skills/mathmodel-figure-templates/scripts/render_template.py paired-raincloud
```

3. 渲染器将打包的模板脚本复制到 `绘图复刻/scripts/`，在该目录下运行它，并将输出写入 `绘图复刻/outputs/`。
4. 将生成的 PNG/PDF/SVG 路径和复制的脚本路径返回给用户。

使用 `--list` 显示支持的 ID：

```bash
python3 /home/user/.claude/skills/mathmodel-figure-templates/scripts/render_template.py --list
```

## 输出契约

- 在当前工作区下工作，除非用户提供其他路径。
- 默认项目文件夹：`绘图复刻`。
- 脚本路径：`绘图复刻/scripts/make_<模板>.py`。
- 输出：`绘图复刻/outputs/<模板>_replica.png`, `.pdf`, `.svg`。
- 优先使用打包的脚本；仅在用户要求定制时编辑复制的工区脚本。
- 打包脚本使用确定性模拟数据。不要声称模拟值精确再现了源研究。

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

## 定制时

如果用户要求修改，首先复制/运行最近的模板，然后在 `绘图复刻/scripts/` 中编辑复制的文件。保留：

- 导入 matplotlib 前的 `MPLCONFIGDIR`。
- 模拟数据的确定性种子。
- PNG/PDF/SVG 导出。
- 可读的标签、图例和高 DPI 输出。

使用 `references/plot-recipes.md` 获取实现模式。
