# PPTX 创建、编辑和分析

## 概述

用户可能会要求你创建、编辑或分析 .pptx 文件的内容。.pptx 文件本质上是一个包含 XML 文件和其他资源的 ZIP 压缩包，你可以读取或编辑这些内容。针对不同的任务，你有不同的工具和工作流程可供选择。

## 读取和分析内容

### 文本提取

如果你只需要读取演示文稿的文本内容，应该将文档转换为 Markdown 格式：

```bash
# 将文档转换为 Markdown
python -m markitdown path-to-file.pptx
```

### 原始 XML 访问

你需要原始 XML 访问权限来处理：评论、演讲者笔记、幻灯片布局、动画、设计元素和复杂格式。对于这些任何功能，你都需要解包演示文稿并读取其原始 XML 内容。

#### 解包文件

`python ooxml/scripts/unpack.py <office_file> <output_dir>`

**注意**：unpack.py 脚本位于相对于项目根目录的 `skills/pptx/ooxml/scripts/unpack.py` 路径下。如果该路径下不存在此脚本，请使用 `find . -name "unpack.py"` 来定位它。

#### 关键文件结构

* `ppt/presentation.xml` - 主要演示文稿元数据和幻灯片引用
* `ppt/slides/slide{N}.xml` - 单个幻灯片内容（slide1.xml、slide2.xml 等）
* `ppt/notesSlides/notesSlide{N}.xml` - 每个幻灯片的演讲者笔记
* `ppt/comments/modernComment_*.xml` - 特定幻灯片的评论
* `ppt/slideLayouts/` - 幻灯片布局模板
* `ppt/slideMasters/` - 主幻灯片模板
* `ppt/theme/` - 主题和样式信息
* `ppt/media/` - 图片和其他媒体文件

#### 字体和颜色提取

**当给定一个要模仿的示例设计时**：始终使用以下方法首先分析演示文稿的字体和颜色：
1. **读取主题文件**：检查 `ppt/theme/theme1.xml` 中的颜色（`<a:clrScheme>`）和字体（`<a:fontScheme>`）
2. **采样幻灯片内容**：检查 `ppt/slides/slide1.xml` 中的实际字体使用（`<a:rPr>`）和颜色
3. **搜索模式**：使用 grep 在所有 XML 文件中查找颜色（`<a:solidFill>`，`<a:srgbClr>`）和字体引用

## 创建新的 PowerPoint 演示文稿 **不使用模板**

从零开始创建新的 PowerPoint 演示文稿时，使用 **html2pptx** 工作流程将 HTML 幻灯片转换为具有准确定位的 PowerPoint。

### 设计原则

**关键**：在创建任何演示文稿之前，分析内容并选择合适的设计元素：
1. **考虑主题内容**：这个演示文稿是关于什么的？它暗示了什么语气、行业或氛围？
2. **检查品牌**：如果用户提到公司/组织，请考虑其品牌颜色和身份
3. **将调色板与内容匹配**：选择反映主题的颜色
4. **说明你的方法**：在编写代码之前解释你的设计选择

**要求**：
- ✅ 在编写代码之前声明基于内容的设
