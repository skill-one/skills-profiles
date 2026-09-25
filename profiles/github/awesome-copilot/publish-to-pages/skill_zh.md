# 发布到 GitHub Pages

一键将任何演示文稿或网页内容发布到 GitHub Pages。

## 1. 前置条件检查

静默运行以下命令。仅显示错误信息：

```bash
command -v gh >/dev/null || echo "缺失：gh CLI — 从 https://cli.github.com 安装"
gh auth status &>/dev/null || echo "缺失：gh 未认证 — 运行 'gh auth login'"
command -v python3 >/dev/null || echo "缺失：python3 (用于 PPTX 转换)"
```

`poppler-utils` 是可选的（通过 `pdftoppm` 进行 PDF 转换）。不要阻塞该检查。

## 2. 输入检测

根据用户提供的内容确定输入类型：

| 输入 | 检测方式 |
|------|----------|
| HTML 文件 | 扩展名 `.html` 或 `.htm` |
| PPTX 文件 | 扩展名 `.pptx` |
| PDF 文件 | 扩展名 `.pdf` |
| Google Slides URL | URL 包含 `docs.google.com/presentation` |

如果未提供 **仓库名称**，则提示用户输入。默认：不带扩展名的文件名。

## 3. 转换

### 大文件处理

两个转换脚本会自动检测大文件并切换到 **外部资源模式**：
- **PPTX**：文件 >20MB 或包含 >50 张图片 → 图片保存为单独文件在 `assets/` 目录中
- **PDF**：文件 >20MB 或包含 >50 页 → 页面 PNG 保存于 `assets/` 目录中
- 文件 >150MB 会打印警告（PPTX 建议使用 PDF 路径）

这确保单个文件符合 GitHub 的 100MB 限制。小文件仍会生成一个自包含的 HTML。

你可以通过 `--external-assets` 或 `--no-external-assets` 强制行为。

### HTML
无需转换。直接使用文件作为 `index.html`。

### PPTX
运行转换脚本：
```bash
python3 SKILL_DIR/scripts/convert-pptx.py INPUT_FILE /tmp/output.html
# 对于大文件，强制外部资源：
python3 SKILL_DIR/scripts/convert-pptx.py INPUT_FILE /tmp/output.html --external-assets
```
如果缺少 `python-pptx`，提示用户：`pip install python-pptx`

### PDF
使用包含的脚本转换（需要 `poppler-utils` 支持 `pdftoppm`）：
```bash
python3 SKILL_DIR/scripts/convert-pdf.py INPUT_FILE /tmp/output.html
# 对于大文件，强制外部资源：
python3 SKILL_DIR/scripts/convert-pdf.py INPUT_FILE /tmp/output.html --external-assets
```
每页会渲染为 PNG 并嵌入 HTML 中，带有幻灯片导航。
如果缺少 `pdftoppm`，提示用户：`apt install poppler-utils`（或 macOS 上的 `brew install poppler`）。

### Google Slides
1. 从 URL 中提取演示文稿 ID（`/d/` 和 `/` 之间的长字符串）
2. 下载为 PPTX：
```bash
curl -L "https://docs.google.com/presentation/d/PRESENTATION_ID/export/pptx" -o /tmp/slides.pptx
```
3. 然后使用上述转换脚本转换 PPTX。

## 4. 发布

### 可见性
仓库默认创建为 **公开**。如果用户指定 `private`（或希望私有仓库），使用 `--private` — 但请注意，私有仓库的 GitHub Pages 需要 Pro、Team 或企业计划。

### 发布
```bash
bash SKILL_DIR/scripts/publish.sh /path/to/index.html REPO_NAME public "描述"
```

如果用户请求私有仓库，将 `public` 替换为 `private`。

脚本会创建仓库，推送 `index.html`（如果存在 `assets/` 目录则一并推送），并启用 GitHub Pages。

**注意**：当使用外部资源模式时，输出 HTML 会引用 `assets/` 目录中的文件。发布脚本会自动检测并复制 `assets/` 目录到 HTML 文件相同的父目录。

## 5. 输出

提示用户：
- **仓库地址**：`https://github.com/USERNAME/REPO_NAME`
- **实时地址**：`https://USERNAME.github.io/REPO_NAME/`
- **注意**：页面需要 1-2 分钟才能上线。

## 错误处理

- **仓库已存在**：建议追加编号（`my-slides-2`）或日期（`my-slides-2026`）。
- **页面启用失败**：仍返回仓库 URL。用户可以在仓库设置中手动启用页面。
- **PPTX 转换失败**：提示用户运行 `pip install python-pptx`。
- **PDF 转换失败**：建议安装 `poppler-utils`（`apt install poppler-utils` 或 `brew install poppler`）。
- **Google Slides 下载失败**：演示文稿可能无法公开访问。提示用户使其可查看或手动下载 PPTX。
