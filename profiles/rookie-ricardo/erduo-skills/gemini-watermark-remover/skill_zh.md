# Gemini Watermark Remover

## 依赖项

- Python 3.9+
- Pillow（使用 `pip install -r requirements.txt` 安装）

## 快速入门

1) 在脚本文件夹中安装依赖项：
   - `cd skills/gemini-watermark-remover/scripts && pip install -r requirements.txt`
2) 运行 CLI：
   - `python remove_watermark.py <输入图像> <输出图像>`

## CLI 使用方法

- 参数：
  - `input-image`：Gemini 水印图像的路径
  - `output-image`：清理后的图像路径（格式由扩展名推断）

示例：

```
python remove_watermark.py ./in.png ./out.png
```

## 该技能提供的内容

- `scripts/remove_watermark.py`：CLI 入口点和核心算法。
- `assets/bg_48.png`, `assets/bg_96.png`：预捕获的水印 alpha 映射。
- `references/algorithm.md`：数学、检测规则和限制。

## 工作流程

1) 使用 `remove_watermark.py` 进行一次性处理。
2) 如果需要调整检测规则或 alpha 逻辑，请阅读 `references/algorithm.md`。

## 注意事项

- 该脚本使用 Pillow 进行图像 IO 和逐像素编辑。
- 输出格式由 Pillow 根据输出文件扩展名推断。
