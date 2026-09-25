<instructions>
<powerpoint_professional_suite>

<high_fidelity_creation>
精确布局定位的首选方法：
1. **HTML**：创建幻灯片（720pt x 405pt）。文本必须使用`<p>`、`<h1>`-`<h6>`或`<ul>`。
2. **视觉元素**：必须使用Sharp首先将渐变/图标栅格化为PNG格式。**参考**：`references/html2pptx.md`。
3. **执行**：运行`html2pptx.js`生成演示文稿。
</high_fidelity_creation>

<template_structure>
用于演示文稿编辑或模板映射：
- **审计**：生成缩略图网格（`scripts/thumbnail.py`）以分析布局。
- **复制**：使用`scripts/rearrange.py`复制并重新排序幻灯片。
- **文本注入**：使用`scripts/replace.py`和JSON清单填充内容。
</template_structure>

<design_quality>
- **字体**：必须仅使用Web安全字体（Arial、Helvetica、Georgia）。
- **颜色**：在PptxGenJS十六进制代码中必须不使用`#`前缀（会导致损坏）。
- **布局**：应优先选择两栏或全页布局。必须不将图表堆叠在文本下方。
- **验证**：必须使用`--cols 4`生成最终缩略图网格，以检查文本截断或重叠问题。
</design_quality>

</powerpoint_professional_suite>
</instructions>
