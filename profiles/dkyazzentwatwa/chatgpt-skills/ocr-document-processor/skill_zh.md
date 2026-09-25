# OCR 文档处理器

处理需要从图像或扫描页面中恢复文本的重 OCR 输入。

## 适用于

- 图像和扫描 PDF 的 OCR
- 可搜索的 PDF 导出
- 结构化提取到文本、Markdown、JSON 或 HTML
- 从扫描材料中提取表格
- 收据解析和名片解析

## 工作流程

1. 确定需要普通 OCR、结构化提取还是特定文档解析。
2. 在存在倾斜、模糊或阴影时，在提取前预处理嘈杂输入。
3. 使用 `scripts/ocr_processor.py` 进行核心 OCR 任务。
4. 当输入是专业化的时，使用专注的辅助工具：
   - `scripts/business_card_scanner.py`
   - `scripts/receipt_scanner.py`
5. 当源质量低、旋转、手写或多语言时，返回置信度注意事项。

## 安全限制

- 在准确性重要时，优先选择明确的语言选择。
- 当 OCR 置信度弱时，不要声称字段是精确的。
- 默认情况下，将非扫描的数字 PDF 路由到 `document-converter-suite` 而不是 OCR。
