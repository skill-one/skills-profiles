# 自然界图像制作 — 路由器

## 路由协议

对于新任务，加载以下核心及匹配资源。重用已有的指导信息进行后续操作；仅在任务需要时才加载更多。

### 0. 检查图形抽象和AI示意图路由

对于使用AI的图形抽象规划、生成、修订或审核任务，首先阅读
[references/ai-graphical-abstract-workflow.md](references/ai-graphical-abstract-workflow.md)。
它包含信息/受众简报、构图和调色板工作流、政策门禁、人类科学审核、披露边界和来源要求。Nature Careers文章是实践者建议，而非投稿许可；请核实当前官方政策以确定目标期刊的具体要求。

如果请求仅涉及规划或审核，除非用户同时要求渲染或修订数据驱动型图像，否则不要要求Python或R。

如果用户明确要求使用OpenRouter、GPT Image 2、图像生成API或类似措辞生成文稿示意图、图形抽象、机制图、概念插图或论文示意图，**不要**询问"Python或R？"。这是非绘图型AI示意图路由。

对于此路由：

1. 阅读[manifest.yaml](manifest.yaml)和`always_load`文件。
2. 阅读[references/ai-graphical-abstract-workflow.md](references/ai-graphical-abstract-workflow.md)。
3. 阅读[references/openrouter-image-generation.md](references/openrouter-image-generation.md)。
4. 当用户需要实际API调用或可复现的负载时，使用[scripts/generate_openrouter_schematic.py](scripts/generate_openrouter_schematic.py)。
5. 将输出视为草稿示意图/图形抽象，而非定量数据面板。不要编造实验值、作者标志、机构标记或不受支持的机制。将内部实用性与投稿资格分开。

仅继续进行非明确的OpenRouter AI图像生成请求的绘图、制图、数据可视化或文稿图像组装任务，进入Python/R后端门禁。

### 1. 加载manifest和核心层

阅读[manifest.yaml](manifest.yaml)。它声明了`backend`轴、允许值及其映射的文件路径。

同时阅读`always_load`下列出的每个文件（`static/core/contract.md`和`static/core/stance.md`）。这些文件包含图像合同、后端门禁、缺失运行时规则、隐私规则和适用于每个图像任务的默认操作立场。

### 2. 解析绘图后端

后端选择仅适用于渲染或编辑绘图代码。重用同一任务及其后续操作中已建立的选项；不要因为新消息省略了语言而再次询问。只读图像审核和后端无关的数据检查可以无需此选择。如果后端仍未解析，保留一次性Python/R问题，并暂停仅依赖的绘图步骤。明确的批准要求和后端排他性仍然有效。

在咨询保存的默认值之前，从当前任务解析绘图后端。按以下顺序决定`backend`值：

1. 如果当前请求明确选择Python或R，使用该后端，并通过`scripts/nature_figure_backend.py set python`或`scripts/nature_figure_backend.py set r`保存它。
2. 如果请求提供明确的语言特定输入文件/工作流，使用该后端并保存它。
3. 否则重用任务中已建立的Python/R选择。如果不存在，运行`scripts/nature_figure_backend.py get`并使用返回的`python`或`r`偏好。
4. 如果既不存在任务选择也不存在保存的偏好，询问**简洁的**一个问题——**Python或R？我将将其记为您的默认值。**——并仅暂停依赖的绘图步骤。用户回答后，在继续之前保存答案。

- `python` — matplotlib / seaborn。
- `r` — ggplot2 / patchwork / ComplexHeatmap。

不要猜测或仅凭美学选择后端。仅在用户明确要求您选择时才推荐后端；然后使用`references/backend-selection.md`说明理由，保存选定的后端并继续。一旦选定，该后端对所有绘图、预览、导出和视觉QA**排他性**（见`core/contract.md`）。此门禁不适用于上述明确的OpenRouter AI示意图路由。

### 3. 加载匹配的后端片段

解析后端后，阅读映射的片段（`static/fragments/backend/python.md`或`static/fragments/backend/r.md`）。它包含后端专属执行规则和出版快速启动（rcParams/theme和导出辅助工具）。**不要**加载另一后端的片段。

### 4. 使用加载的材料构建图像

按以下顺序应用加载的材料：

1. 图像合同（`core/contract.md`）——在编写核心结论、映射证据链、分类原型、设置期刊/导出合同之前，任何代码之前。
2. 多面板证据架构——在规划、重组或审核标记的多面板图像时，加载`references/multipanel-evidence-architecture.md`。使图像回答一个结果级别的科学问题；为面板分配不同的推断角色，而不仅仅是不同的指标。当图像顺序必须遵循文稿论点时，也加载`../nature-shared/core/nature-results-discussion.md`。
3. 默认立场（`core/stance.md`）——原型优先构图、英雄面板、受控调色板、统计数据/完整性作为图像的一部分。
4. 后端片段——排他性的Python或R快速启动和执行规则。
5. 模板适应——在重用内置原始示例、许可的外部材料或用户提供的绘图代码时，加载`references/asset-adaptation.md`，然后再映射数据或更改脚本。
6. 渲染QA和交付预检——加载`references/qa-contract.md`，对每个多面板图像运行渲染时面板对齐门禁，对绘图源运行`scripts/validate_figure.py`，对导出的PDF运行`scripts/audit_pdf_text.py`，并在同一最终PDF上运行`scripts/audit_figure_collisions.py`。然后以最终物理尺寸检查每个面板和完整图像。自动化检查不能替代逐面板的不确定性、显著性、间距和模糊性审核。

对于包含两个或更多可比较面板的每个图像，在导出前测量**最终渲染的绘图区域矩形**并保留对齐JSON。Python图像必须在最终布局绘制后调用`require_matplotlib_panel_alignment()`从`scripts/audit_panel_alignment.py`。R/patchwork图像必须源`scripts/panel_alignment.R`，在最终导出尺寸处写入patchwork布局清单，并运行相同的后端无关JSON审核器。使用默认物理容差`1.5 pt`用于共享边缘、宽度、高度、面板标签锚点和重复间隔。`FIX BEFORE DELIVERY`或退出代码`1`阻止导出；`NOT AUDITABLE`或退出代码`2`阻止任何声称对齐通过。三个或四个等网格跨度面板必须具有相等的最终绘图区域宽度，以及相等的宽度和间隔；有意的不等宽设计需要记录`panel-width`豁免。结构化不等跨度网格——包括两个并排的堆叠面板和一个跨越两行的面板，在任一列中——必须从共享网格起始/终止边界推断，并自动检查。嵌套网格、自由定位的英雄面板、插图和色条只能通过明确的可比较组或记录的带原因的豁免排除。不要削弱全局容差以隐藏一个有意例外。

在生成或修订的每个Python/R科学图像后，导出最终PDF并再次运行碰撞审核；这是在数据几何、文本、字体、图例、注释、坐标轴、误差线、面板大小或布局的任何更改后强制执行的，而不仅是在最终提交时。使用：

```bash
python skills/nature-figure/scripts/audit_figure_collisions.py figure.pdf \
  --json-out figure.collision-audit.json \
  --overlay-pdf figure.collision-audit.pdf
```

- `FIX BEFORE DELIVERY`或退出代码`1`：修复图像，使用选定的绘图后端重新导出，并重新运行所有渲染QA。
- `REVIEW REQUIRED`：以最终物理尺寸检查每个WARN；记录为什么有意重叠是可接受的。使用`--strict`时WARN必须阻止。
- `NOT AUDITABLE`或退出代码`2`：报告依赖/PDF阻止器，不要声称碰撞验证。当PyMuPDF不存在时安装`requirements.txt`。

碰撞审核读取Python和R输出的PDF几何。它不会重绘科学图像或授权跨后端绘图。其可选标记的PDF是QA仅诊断工件，绝不能替代选定后端的源文件或提交文件。

当目标是旗舰期刊Nature时，也加载`references/nature-article-requirements.md`。它将初始审核文件与接受原则主文件和扩展数据生产合同分开，并拥有旗舰图例限制。

当目标是Nature Machine Intelligence时，相反地加载`../nature-shared/journal-formats/nature-machine-intelligence.md`。应用其组合的六项主显示预算、十项扩展数据最大值、初始与生产边界、300-dpi/180-mm生产检查和源数据合同。NMI当前活页不分配独立的每个图例编号，但其官方2018简报指南设定了历史建议上限，即每个完整图例少于300个英文单词。计算整个图例，而不是每个面板；目标为150–250个单词，并保持在300个单词以下，除非活页提交系统或编辑给出了新指示。不要导入旗舰Nature的限制。

图表服务于科学逻辑；美学修饰次于使核心结论清晰、可辩护和可审核。

### 5. 仅在需要时查阅参考资料

`references/`下的文件是深度参考资料，而非默认值。根据manifest中的`references.on_demand`表按需打开它们——例如`references/figure-contract.md`用于构建合同，`references/multipanel-evidence-architecture.md`用于将一个结果级别的问题转化为互补的面板角色和递增声明图像序列，`references/asset-adaptation.md`用于安全地重用绘图模板，`references/template-catalog.md`用于经过验证的Python CSV模板，`references/api.md`用于Python调色板和数值/布局安全辅助工具，`references/r-workflow.md`用于R，`references/design-theory.md`用于颜色/排版/导出理由，`references/common-patterns.md`和`references/chart-types.md`用于布局/图表配方，`references/nature-2026-observations.md`用于真实的Nature页面原型，`references/qa-contract.md`在最终交付前，`references/nature-article-requirements.md`用于精确的旗舰Nature阶段和上传规则，`../nature-shared/journal-formats/nature-machine-intelligence.md`用于精确的NMI图像规则，`references/ai-graphical-abstract-workflow.md`用于AI辅助的图形抽象规划、政策门禁、人类验证和来源，以及`references/tutorials.md` / `references/demos.md`用于实例分析。

不要从Nature Communications语料库或此技能中的视觉样式示例推断旗舰Nature或NMI要求。
