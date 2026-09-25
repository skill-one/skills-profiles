# 布局分析技能

## 概述

此技能使用 **surya**（一个高级文档理解系统）进行文档布局分析。检测文本块、表格、图表、标题，并确定复杂文档中的阅读顺序。

## 如何使用

1. 提供文档图像或 PDF
2. 指定要检测的布局元素
3. 我将分析结构并返回检测到的区域

**示例提示：**
- "分析此文档页面的布局"
- "检测此图像中的所有表格和文本块"
- "确定此 PDF 页面的阅读顺序"
- "在此文档中查找标题和段落"

## 领域知识

### surya 基础知识

```python
from surya.detection import DetectionPredictor
from surya.layout import LayoutPredictor
from surya.reading_order import ReadingOrderPredictor
from PIL import Image

# 加载图像
image = Image.open("document.png")

# 检测布局元素
layout_predictor = LayoutPredictor()
layout_result = layout_predictor([image])
```

### 布局元素类型

| 元素 | 描述 |
|-------|-------------|
| 文本 | 常规段落文本 |
| 标题 | 文档/章节标题 |
| 章节标题 | 章节标题 |
| 列表项 | 项目符号/编号项 |
| 表格 | 表格数据 |
| 图表 | 图像/图表 |
| 说明 | 图表/表格说明 |
| 脚注 | 脚注 |
| 公式 | 数学公式 |
| 页眉 | 页眉 |
| 页脚 | 页脚 |

### 文本检测

```python
from surya.detection import DetectionPredictor
from PIL import Image

# 初始化检测器
detector = DetectionPredictor()

# 加载图像
image = Image.open("document.png")

# 检测文本区域
results = detector([image])

# 访问结果
for page_result in results:
    for bbox in page_result.bboxes:
        print(f"文本区域: {bbox.bbox}")
        print(f"置信度: {bbox.confidence}")
```

### 布局分析

```python
from surya.layout import LayoutPredictor
from PIL import Image

# 初始化布局预测器
layout_predictor = LayoutPredictor()

# 分析布局
image = Image.open("document.png")
layout_results = layout_predictor([image])

# 处理结果
for page_result in layout_results:
    for element in page_result.bboxes:
        print(f"类型: {element.label}")
        print(f"边界框: {element.bbox}")
        print(f"置信度: {element.confidence}")
```

### 阅读顺序检测

```python
from surya.reading_order import ReadingOrderPredictor
from surya.layout import LayoutPredictor
from PIL import Image

# 首先获取布局
layout_predictor = LayoutPredictor()
image = Image.open("document.png")
layout_results = layout_predictor([image])

# 确定阅读顺序
reading_order_predictor = ReadingOrderPredictor()
order_results = reading_order_predictor([image], layout_results)

# 访问有序元素
for page_result in order_results:
    for i, element in enumerate(page_result.ordered_bboxes):
        print(f"{i+1}. {element.label}: {element.bbox}")
```

### 带布局的 OCR

```python
from surya.ocr import OCRPredictor
from surya.layout import LayoutPredictor
from PIL import Image

# 初始化预测器
ocr_predictor = OCRPredictor()
layout_predictor = LayoutPredictor()

# 加载图像
image = Image.open("document.png")

# 获取布局
layout_results = layout_predictor([image])

# 运行 OCR
ocr_results = ocr_predictor([image])

# 合并结果
for layout, ocr in zip(layout_results, ocr_results):
    for layout_elem in layout.bboxes:
        print(f"元素: {layout_elem.label}")
        
        # 在此布局元素内查找 OCR 文本
        for text_line in ocr.text_lines:
            if boxes_overlap(layout_elem.bbox, text_line.bbox):
                print(f"  文本: {text_line.text}")
```

### 处理 PDF

```python
from surya.layout import LayoutPredictor
from pdf2image import convert_from_path

def analyze_pdf_layout(pdf_path):
    """分析 PDF 中所有页面的布局。"""
    
    # 将 PDF 转换为图像
    images = convert_from_path(pdf_path)
    
    # 初始化预测器
    layout_predictor = LayoutPredictor()
    
    # 分析所有页面
    results = layout_predictor(images)
    
    document_structure = []
    
    for page_num, page_result in enumerate(results):
        page_elements = []
        
        for element in page_result.bboxes:
            page_elements.append({
                '类型': element.label,
                '边界框': element.bbox,
                '置信度': element.confidence
            })
        
        document_structure.append({
            '页码': page_num + 1,
            '元素': page_elements
        })
    
    return document_structure

structure = analyze_pdf_layout("document.pdf")
```

### 可视化

```python
from surya.layout import LayoutPredictor
from PIL import Image, ImageDraw, ImageFont

def visualize_layout(image_path, output_path):
    """可视化检测到的布局元素。"""
    
    image = Image.open(image_path)
    layout_predictor = LayoutPredictor()
    results = layout_predictor([image])
    
    # 创建绘图上下文
    draw = ImageDraw.Draw(image)
    
    # 元素类型颜色映射
    colors = {
        '文本': '蓝色',
        '标题': '红色',
        '表格': '绿色',
        '图表': '紫色',
        '章节标题': '橙色',
        '列表项': '青色',
    }
    
    for element in results[0].bboxes:
        bbox = element.bbox
        color = colors.get(element.label, '灰色')
        
        # 绘制矩形
        draw.rectangle(bbox, outline=color, width=2)
        
        # 添加标签
        draw.text((bbox[0], bbox[1] - 15), 
                  f"{element.label} ({element.confidence:.2f})",
                  fill=color)
    
    image.save(output_path)
    return output_path
```

## 最佳实践

1. **使用高质量图像**：150+ DPI 以获得最佳结果
2. **如有必要则预处理**：校正旋转文档
3. **验证结果**：检查置信度分数
4. **处理多页**：逐页处理
5. **结合 OCR**：获取检测区域内的文本

## 常见模式

### 文档结构提取

```python
def extract_document_structure(image_path):
    """提取分层文档结构。"""
    
    from surya.layout import LayoutPredictor
    from surya.reading_order import ReadingOrderPredictor
    
    image = Image.open(image_path)
    
    # 获取布局
    layout_predictor = LayoutPredictor()
    layout_results = layout_predictor([image])
    
    # 获取阅读顺序
    order_predictor = ReadingOrderPredictor()
    order_results = order_predictor([image], layout_results)
    
    structure = {
        '标题': None,
        '章节': [],
        '表格': [],
        '图表': []
    }
    
    current_section = None
    
    for element in order_results[0].ordered_bboxes:
        if element.label == '标题':
            structure['标题'] = element
        elif element.label == '章节标题':
            current_section = {'标题': element, '内容': []}
            structure['章节'].append(current_section)
        elif element.label == '表格':
            structure['表格'].append(element)
        elif element.label == '图表':
            structure['图表'].append(element)
        elif current_section and element.label in ['文本', '列表项']:
            current_section['内容'].append(element)
    
    return structure
```

### 表格区域提取

```python
def extract_table_regions(image_path):
    """从文档中提取表格区域。"""
    
    from surya.layout import LayoutPredictor
    
    image = Image.open(image_path)
    layout_predictor = LayoutPredictor()
    results = layout_predictor([image])
    
    tables = []
    
    for element in results[0].bboxes:
        if element.label == '表格':
            bbox = element.bbox
            
            # 裁剪表格区域
            table_image = image.crop(bbox)
            
            tables.append({
                '边界框': bbox,
                '图像': table_image,
                '置信度': element.confidence
            })
    
    return tables
```

## 示例

### 示例 1：学术论文分析

```python
from surya.layout import LayoutPredictor
from surya.reading_order import ReadingOrderPredictor
from pdf2image import convert_from_path

def analyze_academic_paper(pdf_path):
    """分析学术论文结构。"""
    
    images = convert_from_path(pdf_path)
    
    layout_predictor = LayoutPredictor()
    order_predictor = ReadingOrderPredictor()
    
    paper_structure = {
        '页面': [],
        '元素计数': {
            '标题': 0,
            '章节标题': 0,
            '文本': 0,
            '表格': 0,
            '图表': 0,
            '公式': 0,
            '脚注': 0
        }
    }
    
    layout_results = layout_predictor(images)
    order_results = order_predictor(images, layout_results)
    
    for page_num, (layout, order) in enumerate(zip(layout_results, order_results)):
        page_structure = {
            '页面': page_num + 1,
            '元素': []
        }
        
        for element in order.ordered_bboxes:
            page_structure['元素'].append({
                '类型': element.label,
                '边界框': element.bbox,
                '顺序': element.position
            })
            
            # 计数元素类型
            if element.label in paper_structure['元素计数']:
                paper_structure['元素计数'][element.label] += 1
        
        paper_structure['页面'].append(page_structure)
    
    return paper_structure

paper = analyze_academic_paper('research_paper.pdf')
print(f"表格总数: {paper['元素计数']['表格']}")
print(f"图表总数: {paper['元素计数']['图表']}")
```

### 示例 2：表单字段检测

```python
from surya.layout import LayoutPredictor
from PIL import Image

def detect_form_fields(image_path):
    """检测表单字段和标签。"""
    
    image = Image.open(image_path)
    
    layout_predictor = LayoutPredictor()
    results = layout_predictor([image])
    
    form_fields = []
    
    for element in results[0].bboxes:
        # 查找可能是标签的文本元素
        if element.label == '文本':
            # 检查附近是否有框/线（潜在输入字段）
            form_fields.append({
                '类型': '潜在标签',
                '边界框': element.bbox,
                '置信度': element.confidence
            })
    
    return form_fields

fields = detect_form_fields('form.png')
print(f"找到 {len(fields)} 个潜在表单元素")
```

### 示例 3：多列文章

```python
from surya.layout import LayoutPredictor
from surya.reading_order import ReadingOrderPredictor
from PIL import Image

def process_multicolumn_article(image_path):
    """处理多列文章布局。"""
    
    image = Image.open(image_path)
    
    layout_predictor = LayoutPredictor()
    order_predictor = ReadingOrderPredictor()
    
    layout_results = layout_predictor([image])
    order_results = order_predictor([image], layout_results)
    
    # 按列分组元素
    image_width = image.width
    column_threshold = image_width / 2
    
    columns = {
        '左列': [],
        '右列': [],
        '全宽': []
    }
    
    for element in order_results[0].ordered_bboxes:
        bbox = element.bbox
        element_center = (bbox[0] + bbox[2]) / 2
        element_width = bbox[2] - bbox[0]
        
        # 确定列
        if element_width > column_threshold * 1.5:
            columns['全宽'].append(element)
        elif element_center < column_threshold:
            columns['左列'].append(element)
        else:
            columns['右列'].append(element)
    
    return {
        '布局': '多列',
        '列': columns,
        '阅读顺序': order_results[0].ordered_bboxes
    }

article = process_multicolumn_article('newspaper_page.png')
print(f"左列: {len(article['列']['左列'])} 个元素")
print(f"右列: {len(article['列']['右列'])} 个元素")
```

## 限制

- 手写布局可能不准确
- 非常小的文本区域可能被遗漏
- 复杂嵌套布局具有挑战性
- 推荐使用 GPU 进行批量处理
- 多语言支持各不相同

## 安装

```bash
pip install surya-ocr

# 用于 PDF 处理
pip install pdf2image
```

## 资源

- [surya GitHub](https://github.com/VikParuchuri/surya)
- [模型文档](https://github.com/VikParuchuri/surya#models)
- [示例](https://github.com/VikParuchuri/surya/tree/master/examples)
