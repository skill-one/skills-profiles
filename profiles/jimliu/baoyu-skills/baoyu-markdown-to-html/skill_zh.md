# Markdown to HTML 转换器

将 Markdown 文件转换为带有内联 CSS 的精美样式 HTML，专为微信公众号和其他平台优化。

## 用户输入工具

当此技能提示用户时，请遵循以下工具选择规则（优先级顺序）：

1. **优先使用**当前代理运行时暴露的内置用户输入工具 — 例如，`AskUserQuestion`、`request_user_input`、`clarify`、`ask_user` 或任何等效工具。
2. **降级处理**：如果没有此类工具，则发出编号的纯文本消息，并要求用户回复所选的数字/答案以回答每个问题。
3. **批量处理**：如果工具支持每次调用多个问题，则将所有适用问题组合为单个调用；如果仅支持单个问题，则按优先级顺序逐个询问。

下方的具体 `AskUserQuestion` 引用仅为示例 — 在其他运行时中替换为本地等效工具。

## 脚本目录

**代理执行**：将此 SKILL.md 目录确定为 `{baseDir}`。解析 `${BUN_X}` 运行时：如果已安装 `bun` → `bun`；如果可用 `npx` → `npx -y bun`；否则建议安装 bun。用实际值替换 `{baseDir}` 和 `${BUN_X}`。

| 脚本 | 目的 |
|------|------|
| `scripts/main.ts` | 主入口 |

## 偏好设置 (EXTEND.md)

按优先级顺序检查 EXTEND.md — 第一个找到的优先：

| 优先级 | 路径 | 范围 |
|------|------|------|
| 1 | `.baoyu-skills/baoyu-markdown-to-html/EXTEND.md` | 项目 |
| 2 | `${XDG_CONFIG_HOME:-$HOME/.config}/baoyu-skills/baoyu-markdown-to-html/EXTEND.md` | XDG |
| 3 | `$HOME/.baoyu-skills/baoyu-markdown-to-html/EXTEND.md` | 用户主目录 |

如果没有找到，则使用默认值。

**EXTEND.md 支持**：默认主题、自定义 CSS 变量、代码块样式、mermaid 默认设置（`mermaid_theme`、`mermaid_scale`、`mermaid_background`）。

## 工作流程

### 第 0 步：预检查（中文内容）

**条件**：仅当输入文件包含中文文本时执行。

**检测**：
1. 读取输入的 markdown 文件
2. 检查内容是否包含 CJK 字符（中文/日文/韩文）
3. 如果没有 CJK 内容 → 跳转到第 1 步

**格式建议**：

如果检测到 CJK 内容并且 `baoyu-format-markdown` 技能可用：

使用 `AskUserQuestion` 询问是否先进行格式化。格式化可以修复：
- 包含标点符号的粗体标记导致 `**` 解析失败
- 中英文间距问题

**如果用户同意**：调用 `baoyu-format-markdown` 技能对文件进行格式化，然后使用格式化后的文件作为输入。

**如果用户拒绝**：继续使用原始文件。

### 第 1 步：确定主题

**主题解析顺序**（第一个匹配的优先）：
1. 用户明确指定的主题（CLI `--theme` 或对话中指定）
2. EXTEND.md `default_theme`（此技能自带的 EXTEND.md，在第 0 步中检查）
3. `baoyu-post-to-wechat` EXTEND.md `default_theme`（跨技能降级）
4. 如果未找到 → 使用 `AskUserQuestion` 确认

**跨技能 EXTEND.md 检查**（仅当此技能的 EXTEND.md 没有 `default_theme` 时）：

如果存在 `$HOME/.baoyu-skills/baoyu-post-to-wechat/EXTEND.md`，则读取并查找 `default_theme:` 行。如果存在则使用该值；否则继续降级。

**如果主题从 EXTEND.md 解析**：直接使用，不要询问用户。

**如果没有默认值找到**：使用 `AskUserQuestion` 确认从下方 [主题](#themes) 表格中选择一个主题。

### 第 1.5 步：确定引用模式

**默认**：关闭。默认情况下不询问。

**仅当用户明确要求**“微信外链转底部引用”、“底部引用”、“文末引用”，或传递 `--cite` 时才启用。

**启用时的行为**：
- 普通外部链接使用编号的上标并收集在最后的 `引用链接` 部分。
- `https://mp.weixin.qq.com/...` 链接保持为直接链接，不会被移动到底部。
- 链接文本与 URL 相同的裸链接保持内联。

### 第 2 步：转换

```bash
${BUN_X} {baseDir}/scripts/main.ts <markdown_file> --theme <theme> [--cite]
```

### 第 3 步：报告结果

显示 JSON 结果中的输出路径。如果创建了备份，请提及。

## 使用方法

```bash
${BUN_X} {baseDir}/scripts/main.ts <markdown_file> [options]
```

**选项**：

| 选项 | 描述 | 默认值 |
|------|------|------|
| `--theme <name>` | 主题名称（default、grace、simple、modern） | default |
| `--color <name\|hex>` | 主要颜色：预设名称或十六进制值 | 主题默认值 |
| `--font-family <name>` | 字体：sans、serif、serif-cjk、mono 或 CSS 值 | 主题默认值 |
| `--font-size <N>` | 字体大小：14px、15px、16px、17px、18px | 16px |
| `--title <title>` | 覆盖来自 frontmatter 的标题 | |
| `--cite` | 将外部链接转换为底部引用，追加 `引用链接` 部分 | false (关闭) |
| `--keep-title` | 保留内容中的第一个标题 | false (移除) |
| `--mermaid-theme <name>` | Mermaid 主题：`default`、`forest`、`dark`、`neutral`、`base` | default |
| `--mermaid-scale <N>` | Mermaid 渲染比例（正数 ≤ 4） | 2 |
| `--mermaid-width <N>` | Mermaid 目标 CSS 显示宽度（px）；当图表宽度小于此值时，PNG 渲染为 `width × scale` 像素 | 860 |
| `--mermaid-bg <value>` | Mermaid 背景：`white`、`transparent` 或 `#hex` | white |
| `--no-mermaid` | 跳过 Mermaid PNG 渲染；使用 `<pre class="mermaid">` 降级 | false |
| `--help` | 显示帮助 | |

**颜色预设**：

| 名称 | 十六进制 | 标签 |
|------|----------|------|
| blue | #0F4C81 | 经典蓝色 |
| green | #009874 | 翡翠绿 |
| vermilion | #FA5151 | 鲜艳的朱红 |
| yellow | #FECE00 | 柠檬黄 |
| purple | #92617E | 淡紫色 |
| sky | #55C9EA | 天蓝色 |
| rose | #B76E79 | 玫瑰金 |
| olive | #556B2F | 橄榄绿 |
| black | #333333 | 石墨黑 |
| gray | #A9A9A9 | 烟雾灰 |
| pink | #FFB7C5 | 樱花粉 |
| red | #A93226 | 中国红 |
| orange | #D97757 | 温暖的橙色 (现代默认) |

**示例**：

```bash
# 基本转换（使用默认主题，移除第一个标题）
${BUN_X} {baseDir}/scripts/main.ts article.md

# 使用特定主题
${BUN_X} {baseDir}/scripts/main.ts article.md --theme grace

# 带自定义颜色的主题
${BUN_X} {baseDir}/scripts/main.ts article.md --theme modern --color red

# 为普通外部链接启用底部引用
${BUN_X} {baseDir}/scripts/main.ts article.md --cite

# 保留内容中的第一个标题
${BUN_X} {baseDir}/scripts/main.ts article.md --keep-title

# 覆盖标题
${BUN_X} {baseDir}/scripts/main.ts article.md --title "我的文章"
```

## 输出

**文件位置**：与输入的 markdown 文件位于同一目录。
- 输入：`/path/to/article.md`
- 输出：`/path/to/article.html`

**冲突处理**：如果 HTML 文件已存在，它将被首先备份：
- 备份：`/path/to/article.html.bak-YYYYMMDDHHMMSS`

**JSON 输出到标准输出**：

```json
{
  "title": "Article Title",
  "author": "Author Name",
  "summary": "Article summary...",
  "htmlPath": "/path/to/article.html",
  "backupPath": "/path/to/article.html.bak-20260128180000",
  "contentImages": [
    {
      "placeholder": "MDTOHTMLIMGPH_1",
      "localPath": "/path/to/img.png",
      "originalPath": "imgs/image.png"
    }
  ],
  "mermaidImages": [
    {
      "hash": "a1b2c3d4e5f6",
      "localPath": "/path/to/imgs/.mermaid-cache/mermaid-a1b2c3d4e5f6.png",
      "cached": false
    }
  ]
}
```

**Mermaid 渲染**：被 ` ```mermaid ` 包围的代码块通过无头 Chrome (CDP) 渲染为 PNG 并缓存于 `imgs/.mermaid-cache/mermaid-<hash>.png`。缓存键包含代码、主题、比例、目标宽度、背景和 mermaid 版本。如果不想将生成的图表提交到版本控制，请将 `imgs/.mermaid-cache/` 添加到 `.gitignore`。需要在系统上安装 Chrome/Chromium/Edge；否则该块将降级为 `<pre class="mermaid">…</pre>`，但转换仍然成功。

## 主题

| 主题 | 描述 |
|------|------|
| `default` | 经典 — 传统布局，居中标题带底部边框，H2 带彩色背景的白色文本 |
| `grace` | 优雅 — 文本阴影，圆角卡片，精致的引用块（by @brzhang） |
| `simple` | 简约 — 现代极简，不对称圆角，干净的空白（by @okooo5km） |
| `modern` | 现代 — 大半径，药丸形标题，宽松的行高（与 `--color red` 配合使用以获得传统的红金风格） |

## 支持的 Markdown 功能

| 功能 | 语法 |
|------|------|
| 标题 | `# H1` 到 `###### H6` |
| 粗体/斜体 | `**粗体**`，`*斜体*` |
| 代码块 | ` ```lang ` 带语法高亮 |
| 内联代码 | `` `代码` `` |
| 表格 | GitHub 风格的 markdown 表格 |
| 图片 | `![alt](src)` |
| 链接 | `[文本](url)`；添加 `--cite` 将普通外部链接移动到底部引用 |
| 引用块 | `> 引用` |
| 列表 | `-` 无序列表，`1.` 有序列表 |
| 提示 | `> [!NOTE]`，`> [!WARNING]` 等 |
| 脚注 | `[^1]` 引用 |
| Ruby 文本 | `{base|注释}` |
| Mermaid | ` ```mermaid ` 块通过无头 Chrome 渲染为本地 PNG 并缓存于 `imgs/.mermaid-cache/`；如果 Chrome 不可用或渲染失败，则降级为 `<pre class="mermaid">` |
| PlantUML | ` ```plantuml ` 图表 |

## Frontmatter

支持 YAML frontmatter 用于元数据：

```yaml
---
title: Article Title
author: Author Name
description: Article summary
---
```

如果没有找到标题，则从第一个 H1/H2 标题中提取或使用文件名。

## 扩展支持

通过 EXTEND.md 进行自定义配置。参见 **偏好设置** 部分的路径和支持的选项。
