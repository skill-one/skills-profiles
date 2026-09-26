# MarkItDown 功能

微软的 Python 工具，用于将各种文件格式转换为 Markdown，适用于 LLM 和文本分析流程。

## 概述

MarkItDown 转换文档时保留结构（标题、列表、表格、链接）。它针对 LLM 消费进行了优化，而非人类可读输出。

### 支持的格式

| 类别 | 格式 |
|------|------|
| 文档 | PDF、Word (DOCX)、PowerPoint (PPTX)、Excel (XLSX, XLS) |
| 媒体 | 图片 (EXIF + OCR)、音频 (WAV, MP3 转录) |
| 网络 | HTML、YouTube 链接、维基百科、RSS/Atom 提要 |
| 数据 | CSV、JSON、XML、Jupyter 笔记本 (.ipynb) |
| 存档 | ZIP (迭代内容)、EPub |
| 邮件 | Outlook MSG 文件 |

## 快速入门

### 安装

```bash
# 完整安装（推荐）
pip install 'markitdown[all]'

# 最小化安装（指定格式）
pip install 'markitdown[pdf,docx,pptx]'

# 使用 uv
uv pip install 'markitdown[all]'
```

#### 可选依赖

| 额外功能 | 描述 |
|-------|------|
| `[all]` | 所有可选依赖 |
| `[pdf]` | PDF 文件支持 |
| `[docx]` | Word 文档 |
| `[pptx]` | PowerPoint 演示文稿 |
| `[xlsx]` | Excel 电子表格 |
| `[xls]` | 传统 Excel 文件 |
| `[outlook]` | Outlook MSG 文件 |
| `[az-doc-intel]` | Azure 文档智能 |
| `[audio-transcription]` | WAV/MP3 转录 |
| `[youtube-transcription]` | YouTube 视频字幕 |

### 命令行使用

```bash
# 基本转换
markitdown document.pdf > output.md

# 指定输出文件
markitdown document.pdf -o output.md

# 管道输入
cat document.pdf | markitdown > output.md

# 使用 Azure 文档智能
markitdown document.pdf -o output.md -d -e "<endpoint>"
```

### Python API

```python
from markitdown import MarkItDown

# 基本转换
md = MarkItDown()
result = md.convert("document.xlsx")
print(result.text_content)

# 使用 LLM 进行图片描述
from openai import OpenAI

client = OpenAI()
md = MarkItDown(
    llm_client=client,
    llm_model="gpt-4o",
    llm_prompt="详细描述这张图片"
)
result = md.convert("image.jpg")
print(result.text_content)

# 使用 Azure 文档智能
md = MarkItDown(docintel_endpoint="<your-endpoint>")
result = md.convert("复杂文档.pdf")
print(result.text_content)
```

## 常见用例

### 批量转换目录

```python
from markitdown import MarkItDown
from pathlib import Path

md = MarkItDown()
input_dir = Path("./documents")
output_dir = Path("./markdown")
output_dir.mkdir(exist_ok=True)

for file in input_dir.glob("*"):
    if file.is_file():
        try:
            result = md.convert(str(file))
            output_file = output_dir / f"{file.stem}.md"
            output_file.write_text(result.text_content)
            print(f"已转换: {file.name}")
        except Exception as e:
            print(f"失败: {file.name} - {e}")
```

### 为 LLM 准备上下文

```python
from markitdown import MarkItDown

def prepare_for_llm(file_path: str) -> str:
    """转换为 LLM 适用的 Markdown 文档."""
    md = MarkItDown()
    result = md.convert(file_path)

    # 添加来源引用
    content = f"# 来源: {file_path}\n\n{result.text_content}"
    return content

# 使用 LLM
context = prepare_for_llm("报告.pdf")
```

### 提取 YouTube 字幕

```bash
# 命令行
markitdown "https://www.youtube.com/watch?v=VIDEO_ID" > transcript.md
```

```python
# Python
from markitdown import MarkItDown

md = MarkItDown()
result = md.convert("https://www.youtube.com/watch?v=VIDEO_ID")
print(result.text_content)
```

### 带人工智能描述的图片 OCR

```python
from markitdown import MarkItDown
from openai import OpenAI

# 初始化 LLM 支持
client = OpenAI()
md = MarkItDown(
    llm_client=client,
    llm_model="gpt-4o"
)

# 带人工智能描述的图片转换
result = md.convert("截图.png")
print(result.text_content)
```

### 转换 Jupyter Notebook

```python
from markitdown import MarkItDown

md = MarkItDown()
result = md.convert("分析.ipynb")
print(result.text_content)  # 代码单元、输出、Markdown
```

### 提取维基百科内容

```python
from markitdown import MarkItDown

md = MarkItDown()
result = md.convert("https://en.wikipedia.org/wiki/Python")
print(result.text_content)  # 仅主文章内容
```

### 解析 RSS 提要

```python
from markitdown import MarkItDown

md = MarkItDown()
result = md.convert("https://example.com/feed.xml")
print(result.text_content)  # 提要条目作为 Markdown
```

## 插件系统

MarkItDown 支持第三方插件以扩展功能。

```bash
# 列出已安装插件
markitdown --list-plugins

# 转换时启用插件
markitdown --use-plugins document.pdf
```

```python
# Python 中启用插件
md = MarkItDown(enable_plugins=True)
result = md.convert("document.pdf")
```

> 在 GitHub 上搜索 `#markitdown-plugin` 以查找可用插件。

## MCP 服务器集成

MarkItDown 提供 MCP（模型上下文协议）服务器，用于与 Claude Desktop 等LLM应用程序集成。

```bash
# 安装 MCP 服务器
pip install markitdown-mcp

# 或从源代码安装
git clone https://github.com/microsoft/markitdown.git
cd markitdown/packages/markitdown-mcp
pip install -e .
```

有关配置详情，请参阅 [markitdown-mcp][mcp-repo]。

[mcp-repo]: https://github.com/microsoft/markitdown/tree/main/packages/markitdown-mcp

## Docker 使用

```bash
# 构建镜像
docker build -t markitdown:latest .

# 转换文件
docker run --rm -i markitdown:latest < document.pdf > output.md
```

## 故障排除

| 问题 | 解决方案 |
|------|------|
| 缺少依赖 | 使用 `pip install 'markitdown[all]'` 安装 |
| PDF 提取失败 | 尝试使用 Azure 文档智能处理复杂 PDF |
| 图片文本未提取 | 确保 OCR 依赖已安装或使用 LLM 模式 |
| 大文件超时 | 分块处理或使用流式传输 |
| 插件未找到 | 运行 `markitdown --list-plugins` 验证安装 |

### 常见错误

```bash
# 特定格式 ModuleNotFoundError
pip install 'markitdown[pdf]'  # 安装缺失的依赖

# Azure 认证
export AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT="<endpoint>"
export AZURE_DOCUMENT_INTELLIGENCE_KEY="<key>"
```

## 依赖要求

- Python >= 3.10
- 推荐使用虚拟环境

```bash
# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows

# 安装
pip install 'markitdown[all]'
```

## 参考

- `references/cli-reference.md` - 完整命令行选项
- `references/api-reference.md` - Python API 详情
- `references/examples.md` - 扩展示例
- `references/advanced-features.md` - 自定义转换器、URI 处理
- GitHub: <https://github.com/microsoft/markitdown>
- PyPI: <https://pypi.org/project/markitdown/>

---

## 注意事项

- **包含嵌入图片的 DOCX：图片提取到单独文件；Markdown 使用绝对路径** — 仅移动 Markdown 文件会破坏图片引用。
- **PDF OCR 置信度未显示** — 低置信度文本会像确定文本一样返回；下游 LLM 使用可能导致错误。
- **XLSX 合并单元格提取为单独单元格，非锚点位置为空值** — 转换后的报表会隐式丢失列分组。
- **HTML 到 Markdown 丢失 CSS 驱动的布局** — 列定位表格会折叠为行主序线性输出；复杂表格变得无法解析。
- **`--use-llm` 标志用于图片描述时，在无 OPENAI_API_KEY 时静默回退到文件名** — 输出看似填充，但包含无实际描述。
