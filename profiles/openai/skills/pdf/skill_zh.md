# PDF 技能

## 使用场景
- 读取或审阅 PDF 内容，其中布局和视觉效果很重要。
- 以可靠格式以编程方式创建 PDF 文件。
- 在交付前验证最终渲染效果。

## 工作流程
1. 优先进行视觉审查：将 PDF 页面渲染为 PNG 并进行检查。
   - 如果可用，请使用 `pdftoppm`。
   - 如果不可用，请安装 Poppler 或要求用户在本地审查输出。
2. 在创建新文档时，使用 `reportlab` 生成 PDF 文件。
3. 使用 `pdfplumber`（或 `pypdf`）进行文本提取和快速检查；不要依赖它来保证布局准确性。
4. 每次有意义的更新后，重新渲染页面并验证对齐、间距和可读性。

## 临时文件和输出规范
- 使用 `tmp/pdfs/` 存放中间文件；完成后删除。
- 在此代码库中工作时，将最终产物写入 `output/pdf/`。
- 保持文件名稳定且描述性强。

## 依赖项（如果缺失则安装）
优先使用 `uv` 进行依赖管理。

Python 包：
```
uv pip install reportlab pdfplumber pypdf
```
如果 `uv` 不可用：
```
python3 -m pip install reportlab pdfplumber pypdf
```
系统工具（用于渲染）：
```
# macOS (Homebrew)
brew install poppler

# Ubuntu/Debian
sudo apt-get install -y poppler-utils
```
如果在此环境中无法安装，请告知用户缺失的依赖项以及如何本地安装。

## 环境
无必需的环境变量。

## 渲染命令
```
pdftoppm -png $INPUT_PDF $OUTPUT_PREFIX
```

## 质量预期
- 保持精致的视觉设计：一致的字体、间距、页边距和章节层次结构。
- 避免渲染问题：文本被裁剪、元素重叠、表格损坏、黑色方块或无法识别的符号。
- 图表、表格和图像必须清晰、对齐且标签明确。
- 仅使用 ASCII 连字符。避免 U+2011（非断开连字符）和其他 Unicode 连字符。
- 引用和参考文献必须易于人类阅读；切勿留下工具标记或占位符字符串。

## 最终检查
- 直到最后一次 PNG 检查显示零视觉或格式缺陷时才交付。
- 确认页眉/页脚、页码和章节过渡看起来精致。
- 保持中间文件组织有序或在最终批准后删除。
