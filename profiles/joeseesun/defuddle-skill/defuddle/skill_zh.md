# Defuddle - 网页内容提取

从网页中提取主要文章内容，移除广告、侧边栏、导航和其他杂乱信息。输出干净的 Markdown 格式，并附带元数据。

## 前置条件

首次使用前，请检查 `defuddle` 是否已安装：

```bash
command -v defuddle >/dev/null 2>&1 || npm install -g defuddle jsdom
```

## 默认工作流程

当用户提供 URL 时，遵循以下工作流程：

### 第 1 步：提取 Markdown 内容 + JSON 元数据

始终使用 `-m` 和 `-j` 标志获取带有完整元数据的 Markdown 内容：

```bash
defuddle parse "<url>" -m -j
```

### 第 2 步：向用户展示摘要

向用户展示：
- **标题**：来自 JSON `title` 字段
- **作者**：来自 JSON `author` 字段
- **来源**：域名
- **字数**：来自 JSON `wordCount` 字段
- 简要预览（前 2-3 句话）

### 第 3 步：询问保存位置

如果这是在本次对话中**首次**使用 defuddle，请询问用户：
> "保存到哪个目录？(例如 `~/Documents`、`~/Desktop` 或自定义路径)"

记住用户选择的目录，以便在本次对话中后续使用。

### 第 4 步：保存为 Markdown 文件

使用 frontmatter + 完整内容写入文件：

```markdown
---
title: {title}
author: {author}
source: {url}
date: {发布日期或"Unknown"}
clipped: {今天的日期 YYYY-MM-DD}
wordCount: {wordCount}
---

# {title}

{markdown content}
```

**文件命名**：使用文章标题作为文件名，并进行文件系统兼容的清理：
- 替换特殊字符为空格
- 去除空白
- 示例：`The Shape of the Essay Field.md`

### 第 5 步：向用户确认

告知用户文件保存的路径。

## CLI 参考

```bash
defuddle parse <source> [options]
```

**参数**：
- `<source>` — URL (`https://...`) 或本地 HTML 文件路径

**选项**：
| 标志 | 描述 |
|------|-------------|
| `-m, --markdown` | 将内容转换为 Markdown |
| `-j, --json` | 以包含完整元数据的 JSON 格式输出 |
| `-o, --output <file>` | 写入文件而非标准输出 |
| `-p, --property <name>` | 提取单个属性（title、description、domain、author、published、wordCount、content） |
| `--debug` | 详细日志 |

## JSON 响应字段

使用 `-j` 时，响应包含：
- `title` — 文章标题
- `author` — 作者名称
- `published` — 发布日期
- `description` — 元描述
- `content` — 提取的 Markdown（当使用 `-m` 时）
- `domain` — 来源域名
- `favicon` — Favicon URL
- `image` — 特色图片 URL
- `site` — 网站名称
- `wordCount` — 字数
- `parseTime` — 处理时间（毫秒）

## 注意事项
- 需要 Node.js 和 npm
- `jsdom` 作为依赖项必须安装
- 最适用于文章式页面（博客、新闻、文档）
- 不适用于 SPAs 或 JavaScript 重度页面（例如 WeChat 文章需要浏览器渲染）
