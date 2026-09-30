---
name: pptx-author
description: 在磁盘上生成一个.pptx文件（无头模式），而不是驱动一个实时的PowerPoint文档——适用于没有打开Office应用程序的管理代理会话。
---

# pptx-author

在以**无头**模式（受管代理/CMA模式）运行时使用此技能，并将PowerPoint演示文稿作为**文件工件**交付，而不是通过`mcp__office__powerpoint_*`编辑实时文档。

## 输出契约

- 写入`./out/<name>.pptx`。如果`./out/`不存在，则创建它。
- 在最终消息中返回相对路径，以便编排层可以收集它。

## 如何构建演示文稿

编写一个简短的Python脚本，并使用Bash运行它。使用`python-pptx`：

```python
from pptx import Presentation
from pptx.util import Inches, Pt

prs = Presentation("./templates/firm-template.pptx")  # 如果提供了模板
# 或者：prs = Presentation()

slide = prs.slides.add_slide(prs.slide_layouts[5])    # 仅标题
slide.shapes.title.text = "估值摘要"
# ... 添加表格/图表/文本框 ...

prs.save("./out/pitch-<目标>.pptx")
```

## 规范（与实时Office `pitch-deck`技能保持一致）

- **每张幻灯片一个观点。** 标题陈述要点；正文支持它。
- **每个数字都追溯到模型。** 如果数据来自`./out/model.xlsx`，请脚注工作表和单元格。
- **使用公司模板**当它在`./templates/`挂载时；否则使用默认布局。
- **图表**：当保真度重要时，优先嵌入从模型渲染的PNG，而不是原生pptx图表。
- **不发送外部内容。** 此技能写入文件；它从不发送电子邮件或上传。

## 不应使用的情况

如果`mcp__office__powerpoint_*`工具可用（Cowork插件模式），请使用它们——它们通过审查检查点驱动用户的实时文档。此技能是无头运行时的文件生成回退方案。
