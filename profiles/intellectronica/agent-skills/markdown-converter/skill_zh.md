# Markdown转换器

使用`uvx markitdown`将文件转换为Markdown格式——无需安装。

## 基本用法

```bash
# 转换到标准输出
uvx markitdown input.pdf

# 保存到文件
uvx markitdown input.pdf -o output.md
uvx markitdown input.docx > output.md

# 从标准输入转换
cat input.pdf | uvx markitdown
```

## 支持的格式

- **文档**: PDF、Word (.docx)、PowerPoint (.pptx)、Excel (.xlsx, .xls)
- **网页/数据**: HTML、CSV、JSON、XML
- **媒体**: 图片 (EXIF + OCR)、音频 (EXIF + 文本转录)
- **其他**: ZIP (迭代内容)、YouTube链接、EPub

## 选项

```bash
-o OUTPUT      # 输出文件
-x EXTENSION   # 指示文件扩展名 (用于标准输入)
-m MIME_TYPE   # 指示MIME类型
-c CHARSET     # 指示字符集 (例如，UTF-8)
-d             # 使用Azure文档智能
-e ENDPOINT    # 文档智能端点
--use-plugins  # 启用第三方插件
--list-plugins # 显示已安装的插件
```

## 示例

```bash
# 转换Word文档
uvx markitdown report.docx -o report.md

# 转换Excel电子表格
uvx markitdown data.xlsx > data.md

# 转换PowerPoint演示文稿
uvx markitdown slides.pptx -o slides.md

# 带文件类型指示的转换 (用于标准输入)
cat document | uvx markitdown -x .pdf > output.md

# 使用Azure文档智能进行更好的PDF提取
uvx markitdown scan.pdf -d -e "https://your-resource.cognitiveservices.azure.com/"
```

## 注意事项

- 输出保留文档结构：标题、表格、列表、链接
- 首次运行会缓存依赖项；后续运行速度更快
- 对于提取效果不佳的复杂PDF，使用`-d`配合Azure文档智能
