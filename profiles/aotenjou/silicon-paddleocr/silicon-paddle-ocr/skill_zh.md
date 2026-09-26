# OCR - 图像文字识别

使用 PaddleOCR 从图像中提取文本内容。支持单张图像或批量处理。

## 概述

该技能通过 SiliconFlow API 使用 PaddlePaddle/PaddleOCR-VL-1.5 模型提供光学字符识别 (OCR) 功能。可从 JPG、PNG、WebP、BMP 和 GIF 图像中提取文本。

## 何时使用

在以下情况下调用此技能：
- 用户希望从图像中提取文本
- 用户要求对截图或照片进行 OCR
- 用户需要从图像文件中读取文本
- 用户提到图像文字识别

## 如何使用

### 前置条件

确保设置了 `SILICONFLOW_API_KEY` 环境变量：
```bash
export SILICONFLOW_API_KEY="your_api_key"
```

### 基本用法

执行 OCR 脚本：
```bash
python3 scripts/ocr_skill.py [选项] image_path
```

### 参数

| 参数 | 描述 |
|------|------|
| `images` | 图像文件路径或通配符模式（必填） |
| `-k, --api-key` | API 密钥（默认：从 SILICONFLOW_API_KEY 环境变量获取） |
| `-m, --model` | OCR 模型名称（默认：PaddlePaddle/PaddleOCR-VL-1.5） |
| `-p, --prompt` | 用于自定义行为的识别提示 |
| `-j, --json` | 以 JSON 格式输出结果 |
| `-o, --output` | 将结果保存到指定文件 |
| `--max-tokens` | 响应中的最大令牌数（默认：2000） |

### 示例

单张图像：
```bash
python3 scripts/ocr_skill.py /path/to/image.jpg
```

使用通配符处理多张图像：
```bash
python3 scripts/ocr_skill.py /path/to/images/*.png
```

JSON 输出格式：
```bash
python3 scripts/ocr_skill.py --json /path/to/image.jpg
```

用于表格提取的自定义提示：
```bash
python3 scripts/ocr_skill.py -p "请识别并格式化表格内容为 Markdown" /path/to/table.jpg
```

保存到文件：
```bash
python3 scripts/ocr_skill.py --json --output results.json /path/to/images/*.jpg
```

### 输出格式

**文本输出**（默认）：
```
--- image.jpg ---
识别到的文字内容
识别到 X 处文字区域
```

**JSON 输出**：
```json
{
  "image.jpg": {
    "image_path": "/path/to/image.jpg",
    "image_size": [width, height],
    "texts": [
      {
        "text": "识别的文字",
        "box": [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]
      }
    ],
    "full_text": "所有文本的组合"
  },
  "image2.png": { ... }
}
```

**坐标说明**：
- LOC 值是归一化坐标转换为像素坐标
- 转换公式：像素 = LOC × (image_size / LOC_max_value)
- LOC 最大值约为 972（可能因模型/图像而异）
- `box` 字段提供每个文字区域的四个角坐标（像素格式）

## 支持的图像格式

- JPG/JPEG
- PNG
- WebP
- BMP
- GIF

## 错误处理

如果处理失败：
- 检查图像文件是否存在
- 验证 SILICONFLOW_API_KEY 是否有效
- 确保 API 端点可达

无法处理的图像将显示错误消息，其他图像将继续处理。

## 额外资源

### 参考文件

- **`references/api-configuration.md`** - API 配置详情

### 示例文件

- **`examples/sample-usage.sh`** - 示例使用脚本

### 脚本

- **`scripts/ocr_skill.py`** - OCR 主要实现
