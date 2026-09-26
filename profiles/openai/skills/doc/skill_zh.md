# 文档处理技能

## 使用场景
- 读取或审阅需要考虑布局的DOCX内容（表格、图表、分页）。
- 创建或编辑具有专业格式的DOCX文件。
- 在交付前验证视觉效果布局。

## 工作流程
1. 优先进行视觉审阅（布局、表格、图表）。
   - 如果 `soffice` 和 `pdftoppm` 可用，将 DOCX 转换为 PDF -> PNGs。
   - 或者使用 `scripts/render_docx.py`（需要 `pdf2image` 和 Poppler）。
   - 如果这些工具缺失，请安装它们或要求用户在本地审阅渲染后的页面。
2. 使用 `python-docx` 进行编辑和结构化创建（标题、样式、表格、列表）。
3. 每次有意义的修改后，重新渲染并检查页面。
4. 如果无法进行视觉审阅，使用 `python-docx` 提取文本作为备用方案，并指出布局风险。
5. 保持中间输出文件井井有条，并在最终批准后清理。

## 临时文件和输出规范
- 使用 `tmp/docs/` 存放中间文件；完成后删除。
- 在此代码库中工作时，将最终产物写入 `output/doc/`。
- 保持文件名稳定且描述性强。

## 依赖项（缺失时需安装）
优先使用 `uv` 进行依赖管理。

Python 包：
```
uv pip install python-docx pdf2image
```
如果 `uv` 不可用：
```
python3 -m pip install python-docx pdf2image
```
系统工具（用于渲染）：
```
# macOS (Homebrew)
brew install libreoffice poppler

# Ubuntu/Debian
sudo apt-get install -y libreoffice poppler-utils
```
如果在此环境中无法安装，请告知用户缺失的依赖项及其本地安装方法。

## 环境
无必需的环境变量。

## 渲染命令
DOCX -> PDF：
```
soffice -env:UserInstallation=file:///tmp/lo_profile_$$ --headless --convert-to pdf --outdir $OUTDIR $INPUT_DOCX
```

PDF -> PNGs：
```
pdftoppm -png $OUTDIR/$BASENAME.pdf $OUTDIR/$BASENAME
```

捆绑辅助脚本：
```
python3 scripts/render_docx.py /path/to/file.docx --output_dir /tmp/docx_pages
```

## 质量要求
- 交付客户可用的文档：一致的字体、间距、页边距和清晰的层级结构。
- 避免格式缺陷：文本裁剪/重叠、表格损坏、不可读字符或默认模板样式。
- 图表、表格和视觉元素在渲染页面中必须清晰可读且对齐正确。
- 仅使用 ASCII 连字符。避免 U+2011（非断开连字符）和其他 Unicode 连字符。
- 引用和参考文献必须人类可读；切勿保留工具标记或占位符字符串。

## 最终检查
- 在最终交付前，以 100% 放大倍数重新渲染并检查每一页。
- 修复任何间距、对齐或分页问题，并重复渲染循环。
- 确认没有遗留物（临时文件、重复渲染），除非用户要求保留。
