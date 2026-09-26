# pptx-author

在以**无头**模式（受管代理/CMA模式）运行时使用此技能，并将 PowerPoint 幻灯片作为**文件工件**交付，而不是通过 `mcp__office__powerpoint_*` 编辑实时文档。

## 输出契约

- 写入 `./out/<name>.pptx`。如果 `./out/` 目录不存在，则创建它。
- 在最终消息中返回相对路径，以便编排层可以收集它。

## 如何构建幻灯片

编写一个简短的 Python 脚本，并使用 Bash 运行它。使用 `python-pptx`：

```python
from pptx import Presentation
from pptx.util import Inches, Pt

prs = Presentation("./templates/firm-template.pptx")  # 如果提供了模板
# 或者：prs = Presentation()

slide = prs.slides.add_slide(prs.slide_layouts[5])    # 仅标题
slide.shapes.title.text = "估值摘要"
# ... 添加表格 / 图表 / 文本框 ...

prs.save("./out/pitch-<target>.pptx")
```

## 规范（与实时 Office `pitch-deck` 技能保持一致）

- **每张幻灯片一个观点。** 标题陈述要点；正文支持它。
- **每个数字都追溯到模型。** 如果数据来自 `./out/model.xlsx`，请脚注工作表和单元格。
- **使用公司模板**，当模板挂载在 `./templates/` 时；否则使用默认布局。
- **图表**：当保真度重要时，优先嵌入从模型渲染的 PNG，而不是原生 pptx 图表。
- **不发送外部内容。** 此技能写入文件；它从不发送电子邮件或上传。

## 不应使用的情况

如果 `mcp__office__powerpoint_*` 工具可用（Cowork 插件模式），请使用这些工具——它们通过审查检查点驱动用户的实时文档。此技能是无头运行时的文件生成回退方案。
