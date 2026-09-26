# 翻译书籍（并行子代理）

> 技能由 [ara.so](https://ara.so) 提供 — 每日 2026 技能集合。

一个 Claude Code 技能，使用并行子代理将整本书（PDF/DOCX/EPUB）翻译成任何语言。每个片段都有独立的上下文窗口，防止单次会话翻译中常见的截断和上下文累积问题。

## 管道概述

```
输入 (PDF/DOCX/EPUB)
  │
  ▼
Calibre ebook-convert → HTMLZ → HTML → Markdown
  │
  ▼
分割成片段（每个约 6000 个字符）
  │  manifest.json 跟踪 SHA-256 哈希值
  ▼
并行子代理（默认 8 个并发）
  │  每个：读取片段 → 翻译 → 写入 output_chunk*.md
  ▼
验证（manifest 哈希检查，1:1 源↔输出匹配）
  │
  ▼
合并 → Pandoc → HTML（带目录）→ Calibre → DOCX / EPUB / PDF
```

## 前置条件

```bash
# 1. Calibre（提供 ebook-convert）
# macOS
brew install --cask calibre
# Linux
sudo apt-get install calibre
# 或从 https://calibre-ebook.com/ 下载

# 2. Pandoc
brew install pandoc        # macOS
sudo apt-get install pandoc # Linux

# 3. Python 依赖项
pip install pypandoc beautifulsoup4
```

验证所有工具是否可用：

```bash
ebook-convert --version
pandoc --version
python3 -c "import pypandoc; print('pypandoc ok')"
```

## 安装

**选项 A：npx（推荐）**

```bash
npx skills add deusyu/translate-book -a claude-code -g
```

**选项 B：ClawHub**

```bash
clawhub install translate-book
```

**选项 C：Git 克隆**

```bash
git clone https://github.com/deusyu/translate-book.git ~/.claude/skills/translate-book
```

## 在 Claude Code 中使用

安装技能后，在 Claude Code 中使用自然语言：

```
translate /path/to/book.pdf to Chinese
```

```
translate ~/Downloads/mybook.epub to Japanese
```

```
/translate-book translate /path/to/book.docx to French
```

该技能会自动协调整个管道。

## 支持的语言

| 代码 | 语言   |
|------|-------|
| `zh` | 中文   |
| `en` | 英语   |
| `ja` | 日语   |
| `ko` | 韩语   |
| `fr` | 法语   |
| `de` | 德语   |
| `es` | 西班牙语 |

语言代码是可扩展的 — 在技能定义中添加新的语言。

## 手动运行管道步骤

### 步骤 1：转换为 Markdown 片段

```bash
python3 scripts/convert.py /path/to/book.pdf --olang zh
```

这将在 `{book_name}_temp/` 中生成：
- `chunk0001.md`, `chunk0002.md`, ...（源片段，每个约 6000 个字符）
- `manifest.json`（用于验证的 SHA-256 哈希值）

```bash
# 对于 EPUB 输入
python3 scripts/convert.py /path/to/book.epub --olang ja

# 对于 DOCX 输入
python3 scripts/convert.py /path/to/book.docx --olang fr
```

### 步骤 2：翻译（并行子代理）

该技能处理此步骤 — 它为每个批次启动 8 个并发子代理，每个子代理独立翻译一个片段：

```
# 每个子代理接收以下任务：
读取 chunk0042.md → 翻译为目标语言 → 写入 output_chunk0042.md
```

**可恢复的：** 已翻译的片段（有效的 `output_chunk*.md` 文件）在重新运行时会跳过。

### 步骤 3：合并和构建所有格式

```bash
python3 scripts/merge_and_build.py \
  --temp-dir book_name_temp \
  --title "《目标语言中的书名》"
```

合并前进行验证检查：
- 每个源片段都有一个匹配的输出文件（1:1）
- 源片段哈希值与 `manifest.json` 匹配（没有过时的输出）
- 没有空的输出文件

生成的输出：

| 文件 | 描述 |
|------|------|
| `output.md` | 合并后的翻译 Markdown |
| `book.html` | 带浮动目录的网页版本 |
| `book.docx` | Word 文档 |
| `book.epub` | 电子书格式 |
| `book.pdf` | 可打印的 PDF |

## 项目结构

```
translate-book/
├── SKILL.md                    # Claude Code 技能定义（协调器）
├── scripts/
│   ├── convert.py              # PDF/DOCX/EPUB → Markdown 片段通过 Calibre HTMLZ
│   ├── manifest.py             # SHA-256 片段跟踪和合并验证
│   ├── merge_and_build.py      # 合并片段 → HTML → DOCX/EPUB/PDF
│   ├── calibre_html_publish.py # Calibre 格式转换包装器
│   ├── template.html           # 带浮动目录的 Web HTML 模板
│   └── template_ebook.html     # 电子书 HTML 模板
└── README.md
```

## 如何进行 Manifest 验证

```python
# scripts/manifest.py（概念性用法）

# 在 convert.py 中 — 记录源哈希值
manifest = {
    "chunk0001.md": "sha256:abc123...",
    "chunk0002.md": "sha256:def456...",
    # ...
}

# 在 merge_and_build.py 中 — 合并前验证
# 1. 检查每个片段都有一个对应的 output_chunk
# 2. 重新哈希源片段并与 manifest 比较
# 3. 如果任何哈希不匹配（过时/损坏的输出）则拒绝
# 4. 如果任何输出文件为空则拒绝
```

如果验证失败，脚本会自动删除过时的 `output.md` 并从有效的片段输出重新合并。

## 真实世界示例：翻译一本技术书籍

```bash
# 1. 安装技能
npx skills add deusyu/translate-book -a claude-code -g

# 2. 在工作目录中打开 Claude Code
cd ~/books

# 3. 在 Claude Code 中说：
# "translate clean-code.pdf to Chinese"

# Claude Code 会：
# - 运行 convert.py 分割成片段
# - 每个批次启动 8 个并行子代理
# - 每个子代理独立翻译一个片段
# - 通过 manifest 验证所有输出
# - 合并并构建所有格式

# 4. 输出出现在：
ls clean-code_temp/
# chunk0001.md  chunk0002.md  ...  （源）
# output_chunk0001.md  ...         （已翻译）
# manifest.json
# output.md
# book.html
# book.docx
# book.epub
# book.pdf
```

## 恢复中断的翻译

```bash
# 如果翻译中断，只需重新运行相同的命令：
# "translate clean-code.pdf to Chinese"

# 技能检测现有的 output_chunk*.md 文件
# 并自动跳过已翻译的片段。
# 仅重试缺失或失败的片段。
```

## 翻译后更改输出元数据

如果您需要更新标题、作者、模板或图像资源而不重新翻译：

```bash
# 仅删除最终产物（保留已翻译的片段）
cd book_name_temp/
rm -f output.md book*.html book.docx book.epub book.pdf

# 重新运行合并步骤
python3 ../scripts/merge_and_build.py \
  --temp-dir . \
  --title "《新标题》"
```

**不要删除片段文件** — 那些是您的翻译内容。仅在更改元数据时删除最终产物。

## 故障排除

| 问题 | 解决方案 |
|------|---------|
| `Calibre ebook-convert not found` | 安装 Calibre；确保 `ebook-convert` 在 `$PATH` 中 |
| `Manifest validation failed` | 源片段已更改 — 重新运行 `convert.py` |
| `Missing source chunk` | 源文件已删除 — 重新运行 `convert.py` 重新生成 |
| 不完整的翻译 | 重新运行技能 — 从最后一个有效片段恢复 |
| 更改标题/模板但输出未更改 | 删除 `output.md`、`book*.html`、`book.docx`、`book.epub`、`book.pdf` 然后重新运行 `merge_and_build.py` |
| `output.md 存在但 manifest 无效` | 脚本自动删除过时的输出并重新合并 |
| PDF 生成失败 | 验证 Calibre 是否支持 PDF 输出；尝试 `ebook-convert --help` |
| 空的输出片段 | 重试失败的片段；检查 API 速率限制 |

## 诊断片段问题

```bash
# 检查哪些片段缺少翻译
ls book_temp/chunk*.md | wc -l          # 总源片段
ls book_temp/output_chunk*.md | wc -l   # 已翻译片段数量

# 查找缺失的输出片段
for f in book_temp/chunk*.md; do
  base=$(basename "$f" .md)
  out="book_temp/output_${base}.md"
  if [ ! -f "$out" ] || [ ! -s "$out" ]; then
    echo "Missing: $out"
  fi
done

# 检查 manifest
cat book_temp/manifest.json | python3 -m json.tool | head -30
```

## 配置技巧

- **片段大小：** 默认每个片段约 6000 个字符。较小的片段 = 更多的并行处理但更多 API 调用。
- **并发性：** 默认每个批次 8 个并行子代理。如果遇到速率限制，请在 `SKILL.md` 中调整。
- **语言：** 将新的语言代码添加到技能触发器和翻译提示中 `SKILL.md`。
- **模板：** 自定义 `scripts/template.html` 和 `scripts/template_ebook.html` 以适应不同的 HTML/电子书样式。

## 关键设计原则

1. **每个片段的独立上下文** — 每个子代理从新开始，防止长书上的上下文溢出
2. **基于哈希的完整性** — SHA-256 跟踪在合并前捕获过时或损坏的已翻译片段
3. **片段粒度可恢复** — 从不重新翻译已完成的内容
4. **格式无关的输入** — Calibre 在管道开始前处理 PDF/DOCX/EPUB 的标准化
5. **多种输出格式** — 单个管道同时生成 HTML、DOCX、EPUB 和 PDF
