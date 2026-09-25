# 智能OCR技能

## 概述

该技能能够使用**PaddleOCR**（领先的OCR引擎，支持100多种语言）从图像和扫描文档中智能提取文本。从照片、截图、扫描的PDF文件和手写文档中提取文本，具有高准确性。

## 使用方法

1. 提供图像或扫描文档
2. 可选指定检测语言
3. 我将提取带有位置和置信度数据的文本

**示例提示：**
- "从这张截图提取所有文本"
- "OCR这张扫描的PDF文档"
- "读取这张名片照片中的文本"
- "从这张图像中提取中文和英文文本"

## 领域知识

### PaddleOCR基础

```python
from paddleocr import PaddleOCR

# 初始化OCR引擎
ocr = PaddleOCR(use_angle_cls=True, lang='en')

# 对图像进行OCR
result = ocr.ocr('image.png', cls=True)

# 结果结构：[[box, (text, confidence)], ...]
for line in result[0]:
    box = line[0]      # [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
    text = line[1][0]  # 提取的文本
    conf = line[1][1]  # 置信度分数
    print(f"{text} ({conf:.2f})")
```

### 支持的语言

```python
# 常用语言代码
languages = {
    'en': '英语',
    'ch': '中文（简体）',
    'cht': '中文（繁体）',
    'japan': '日语',
    'korean': '韩语',
    'french': '法语',
    'german': '德语',
    'spanish': '西班牙语',
    'russian': '俄语',
    'arabic': '阿拉伯语',
    'hindi': '印地语',
    'vi': '越南语',
    'th': '泰语',
    # ... 支持100多种语言
}

# 使用特定语言
ocr = PaddleOCR(lang='ch')  # 中文
ocr = PaddleOCR(lang='japan')  # 日语
ocr = PaddleOCR(lang='multilingual')  # 自动检测
```

### 配置选项

```python
from paddleocr import PaddleOCR

ocr = PaddleOCR(
    # 检测设置
    det_model_dir=None,         # 自定义检测模型
    det_limit_side_len=960,     # 检测的最大边长
    det_db_thresh=0.3,          # 二值化阈值
    det_db_box_thresh=0.5,      # 箱框分数阈值
    
    # 识别设置
    rec_model_dir=None,         # 自定义识别模型
    rec_char_dict_path=None,    # 自定义字符字典
    
    # 角度分类
    use_angle_cls=True,         # 启用角度分类
    cls_model_dir=None,         # 自定义分类模型
    
    # 语言
    lang='en',                  # 语言代码
    
    # 性能
    use_gpu=True,               # 如果可用则使用GPU
    gpu_mem=500,                # GPU内存限制（MB）
    enable_mkldnn=True,         # CPU优化
    
    # 输出
    show_log=False,             # 抑制日志
)
```

### 处理不同来源

#### 图像文件
```python
# 单个图像
result = ocr.ocr('image.png')

# 多个图像
images = ['img1.png', 'img2.png', 'img3.png']
for img in images:
    result = ocr.ocr(img)
    process_result(result)
```

#### PDF文件（扫描）
```python
from pdf2image import convert_from_path

def ocr_pdf(pdf_path):
    """OCR扫描的PDF。"""
    # 将PDF页面转换为图像
    images = convert_from_path(pdf_path)
    
    all_text = []
    for i, img in enumerate(images):
        # 保存临时图像
        temp_path = f'temp_page_{i}.png'
        img.save(temp_path)
        
        # 对图像进行OCR
        result = ocr.ocr(temp_path)
        
        # 提取文本
        page_text = '\n'.join([line[1][0] for line in result[0]])
        all_text.append(f"--- 第{i+1}页 ---\n{page_text}")
        
        os.remove(temp_path)
    
    return '\n\n'.join(all_text)
```

#### URL和字节
```python
import requests
from io import BytesIO

# 从URL
response = requests.get('https://example.com/image.png')
result = ocr.ocr(BytesIO(response.content))

# 从字节
with open('image.png', 'rb') as f:
    img_bytes = f.read()
result = ocr.ocr(BytesIO(img_bytes))
```

### 结果处理

```python
def process_ocr_result(result):
    """将OCR结果处理为结构化数据。"""
    
    lines = []
    for line in result[0]:
        box = line[0]
        text = line[1][0]
        confidence = line[1][1]
        
        # 计算边界框
        x_coords = [p[0] for p in box]
        y_coords = [p[1] for p in box]
        
        lines.append({
            'text': text,
            'confidence': confidence,
            'bbox': {
                'left': min(x_coords),
                'top': min(y_coords),
                'right': max(x_coords),
                'bottom': max(y_coords),
            },
            'raw_box': box
        })
    
    return lines

# 按位置排序（从上到下，从左到右）
def sort_by_position(lines):
    return sorted(lines, key=lambda x: (x['bbox']['top'], x['bbox']['left']))
```

### 文本布局重建

```python
def reconstruct_layout(result, line_threshold=10):
    """从OCR结果重建文本布局。"""
    
    lines = process_ocr_result(result)
    lines = sort_by_position(lines)
    
    # 按逻辑行分组
    text_lines = []
    current_line = []
    current_y = None
    
    for line in lines:
        y = line['bbox']['top']
        
        if current_y is None or abs(y - current_y) < line_threshold:
            current_line.append(line)
            current_y = y
        else:
            # 新行
            text_lines.append(' '.join([l['text'] for l in current_line]))
            current_line = [line]
            current_y = y
    
    # 添加最后一行
    if current_line:
        text_lines.append(' '.join([l['text'] for l in current_line]))
    
    return '\n'.join(text_lines)
```

## 最佳实践

1. **预处理图像**：在OCR前提高图像质量
2. **选择正确语言**：指定语言以提高准确性
3. **处理多列**：分别处理各列
4. **过滤低置信度**：跳过低于阈值的检测结果
5. **批量处理**：高效处理多个图像

## 常见模式

### 图像预处理
```python
from PIL import Image, ImageEnhance, ImageFilter

def preprocess_image(image_path):
    """预处理图像以提高OCR效果。"""
    img = Image.open(image_path)
    
    # 转换为灰度
    img = img.convert('L')
    
    # 增强对比度
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(2.0)
    
    # 锐化
    img = img.filter(ImageFilter.SHARPEN)
    
    # 保存预处理后的图像
    preprocessed_path = 'preprocessed.png'
    img.save(preprocessed_path)
    
    return preprocessed_path
```

### 带进度条的批量OCR
```python
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor

def batch_ocr(image_paths, max_workers=4):
    """并行OCR多个图像。"""
    
    results = {}
    
    def process_single(img_path):
        result = ocr.ocr(img_path)
        return img_path, result
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(process_single, p) for p in image_paths]
        
        for future in tqdm(futures, desc="处理OCR"):
            path, result = future.result()
            results[path] = result
    
    return results
```

## 示例

### 示例1：名片读取器
```python
from paddleocr import PaddleOCR
import re

def read_business_card(image_path):
    """从名片中提取联系信息。"""
    
    ocr = PaddleOCR(use_angle_cls=True, lang='en')
    result = ocr.ocr(image_path)
    
    # 提取所有文本
    all_text = []
    for line in result[0]:
        all_text.append(line[1][0])
    
    full_text = '\n'.join(all_text)
    
    # 解析联系信息
    contact = {
        'name': None,
        'email': None,
        'phone': None,
        'company': None,
        'title': None,
        'raw_text': full_text
    }
    
    # 邮件模式
    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', full_text)
    if email_match:
        contact['email'] = email_match.group()
    
    # 电话模式
    phone_match = re.search(r'[\+\d][\d\s\-\(\)]{8,}', full_text)
    if phone_match:
        contact['phone'] = phone_match.group().strip()
    
    # 名字通常是最大/第一个文本
    if all_text:
        contact['name'] = all_text[0]
    
    return contact

card_info = read_business_card('business_card.jpg')
print(f"姓名: {card_info['name']}")
print(f"邮箱: {card_info['email']}")
print(f"电话: {card_info['phone']}")
```

### 示例2：收据扫描器
```python
from paddleocr import PaddleOCR
import re

def scan_receipt(image_path):
    """从收据中提取项目和总额。"""
    
    ocr = PaddleOCR(use_angle_cls=True, lang='en')
    result = ocr.ocr(image_path)
    
    lines = []
    for line in result[0]:
        text = line[1][0]
        y_pos = line[0][0][1]
        lines.append({'text': text, 'y': y_pos})
    
    # 按垂直位置排序
    lines.sort(key=lambda x: x['y'])
    
    receipt = {
        'items': [],
        'subtotal': None,
        'tax': None,
        'total': None
    }
    
    for line in lines:
        text = line['text']
        
        # 查找总额
        if 'total' in text.lower():
            amount = re.search(r'\$?([\d,]+\.?\d*)', text)
            if amount:
                if 'sub' in text.lower():
                    receipt['subtotal'] = float(amount.group(1).replace(',', ''))
                else:
                    receipt['total'] = float(amount.group(1).replace(',', ''))
        
        # 查找税额
        elif 'tax' in text.lower():
            amount = re.search(r'\$?([\d,]+\.?\d*)', text)
            if amount:
                receipt['tax'] = float(amount.group(1).replace(',', ''))
        
        # 查找项目（带价格的行）
        else:
            item_match = re.search(r'(.+?)\s+\$?([\d,]+\.?\d+)$', text)
            if item_match:
                receipt['items'].append({
                    'name': item_match.group(1).strip(),
                    'price': float(item_match.group(2).replace(',', ''))
                })
    
    return receipt

receipt_data = scan_receipt('receipt.jpg')
print(f"项目数量: {len(receipt_data['items'])}")
print(f"总额: ${receipt_data['total']}")
```

### 示例3：多语言文档
```python
from paddleocr import PaddleOCR

def ocr_multilingual(image_path, languages=['en', 'ch']):
    """使用多语言OCR文档。"""
    
    all_results = {}
    
    for lang in languages:
        ocr = PaddleOCR(use_angle_cls=True, lang=lang)
        result = ocr.ocr(image_path)
        
        texts = []
        for line in result[0]:
            texts.append({
                'text': line[1][0],
                'confidence': line[1][1]
            })
        
        all_results[lang] = texts
    
    # 合并结果，保留最高置信度
    merged = {}
    for lang, texts in all_results.items():
        for item in texts:
            text = item['text']
            conf = item['confidence']
            
            if text not in merged or merged[text]['confidence'] < conf:
                merged[text] = {'confidence': conf, 'language': lang}
    
    return merged

result = ocr_multilingual('bilingual_document.png')
for text, info in result.items():
    print(f"[{info['language']}] {text} ({info['confidence']:.2f})")
```

## 限制

- 手写文本准确性因情况而异
- 非常小的文本可能无法检测
- 复杂背景会降低准确性
- 旋转文本需要角度分类
- 推荐使用GPU以获得最佳性能

## 安装

```bash
# CPU版本
pip install paddlepaddle paddleocr

# GPU版本（CUDA 11.x）
pip install paddlepaddle-gpu paddleocr

# 额外依赖
pip install pdf2image Pillow
```

## 资源

- [PaddleOCR GitHub](https://github.com/PaddlePaddle/PaddleOCR)
- [模型库](https://github.com/PaddlePaddle/PaddleOCR/blob/release/2.7/doc/doc_en/models_list_en.md)
- [多语言支持](https://github.com/PaddlePaddle/PaddleOCR/blob/release/2.7/doc/doc_en/multi_languages_en.md)
