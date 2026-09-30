---
name: blog-multilingual
description: 一键创建多语言博客。撰写博客文章，将其翻译成用户指定的语言，进行文化适配，并生成hreflang标签、站点地图条目以及CMS兼容的语言映射。国际内容的完整撰写至发布流程。统筹博客撰写、博客翻译、博客本地化以及（可选）SEO-hreflang。当用户说“多语言博客”、“博客多语言”、“用多种语言撰写”、“国际博客”、“mehrsprachiger Blog”、“blog multilingue”、“blog multilingue”、“用德语和法语创建博客”时使用。
---

# 多语言博客，一键国际发布

旗舰级多语言协调器。将博客撰写、翻译、文化适配和完整国际SEO整合为单一命令。
生成包含hreflang标签、本地化JSON-LD模式和CMS集成元数据的、可供发布的博客文章，每种目标语言都有。

> 基于`claude-blog-multilingual`由Chris Mueller（AI营销中心专业挑战提交，2026年3月，评分85/100熟练）改编。
> 原始链接：https://github.com/Chriss54/multilingual-int
> 此版本移除了审计中标记的原始`curl | bash`安装程序和凭证处理，作为核心技能集成，并使用`blog-translate/references/`下的共享文化适配参考。

## 依赖项

由此协调器内部调用：

| 组件 | 来源 | 是否必需 |
|-------|------|----------|
| `blog-write` | claude-blog（此插件） | 是 |
| `blog-translate` | claude-blog（此插件） | 是 |
| `blog-localize` | claude-blog（此插件） | 是（当`--localize`开启时，默认） |
| `seo-hreflang` | claude-seo（同级插件） | 否，回退到自包含生成器 |

如果未安装`seo-hreflang`，协调器将使用自己的最小生成器（下文第5阶段）发出hreflang标签，并在交付摘要中注明此限制。在这种情况下，hreflang验证仅限于结构层面，而不是`seo-hreflang`提供的深度验证。

## 命令语法

```
/blog multilingual <主题> --languages <lang1,lang2,...> [--source <lang>] [--no-localize] [--format <md|mdx|html>]
```

| 参数 | 是否必需 | 默认值 | 描述 |
|----------|----------|---------|-------------|
| `<主题>` | 是 | 必需 | 博客主题或工作标题 |
| `--languages` | 是 | 必需 | 用逗号分隔的Google兼容hreflang标签（例如 `de,fr,es-MX,ja,pt-BR`） |
| `--source` | 否 | `en` | 源语言 |
| `--no-localize` | 否 | 关闭 | 跳过文化适配（仅翻译） |
| `--format` | 否 | 自动 | 输出格式：`md`、`mdx` 或 `html` |

如果缺少`--languages`，在运行任何操作之前会询问用户一次：
"博客应发布在哪些语言中？提供用逗号分隔的hreflang标签（例如 `de,fr,es-MX,ja,pt-BR`）。文章将首先用`<source>`撰写，然后翻译。"

## 工作流程

### 第1阶段：配置

1. 解析参数。提取主题、目标语言、源语言和格式。
2. 使用`blog-translate`、`blog-localize`和`blog-locale-audit`使用的共享多语言本地化规则验证每种语言代码：小写的ISO 639-1语言代码，可选的ISO 15924脚本（标题大小写），可选的ISO 3166-1 Alpha-2地区代码（大写）。对于`es`、`pt`和`zh`等模糊语言目标，必须指定地区或显式中性模式。
3. 从项目（frontmatter约定、文件扩展名、框架提示）检测输出格式，或使用`--format`。
4. 解析源语言。如果目标语言等于`--source`，则从翻译列表中删除它并发出通知。
5. 在当前工作目录内创建输出目录：
   ```
   multilingual/
     {source-lang}/
     {lang-1}/
     {lang-2}/
     ...
   ```
   输出必须始终在项目根目录内。绝不能在工作目录外写入。

进度：`第1阶段：配置完成，[N]种语言选择（[代码]）`

### 第2阶段：撰写原始博客

调用`blog-write`子技能（通过`/blog write`路由，以便所有现有规则都适用：模板自动选择、来源统计、引用胶囊、Article模式优先级、FAQPage仅在存在可见FAQ内容时作为实体信号、内部链接区域、图表、图像嵌入）。传递主题和用户提供的任何`blog-write`参数。

将原始内容保存到`multilingual/{source-lang}/{slug}.{ext}`。

进度：`第2阶段：原始内容撰写，multilingual/{source-lang}/{slug}.{ext}`

### 第3阶段：翻译所有目标语言

针对每种目标语言，调用`blog-translate`：

- 输入：第2阶段生成的原始博客文章。
- 目标：特定语言代码。
- 在运行时支持并行运行（每种语言一个任务）以减少实际耗时。

将翻译保存到`multilingual/{lang}/{localized-slug}.{ext}`。

进度：每语言`第3阶段：翻译到[lang]（[X]/[N]）`，然后`第3阶段：所有翻译完成`。

### 第4阶段：文化适配

如果`--no-localize`未设置，针对每个翻译后的文章调用`blog-localize`：

- 输入：翻译后的博客文章。
- 本地化：目标语言或地区代码。
- 并行运行。

在`multilingual/`内解析生成路径后应用本地化输出，拒绝符号链接，并在覆盖时创建备份。本地化器替换品牌示例，调整CTA，替换法律参考，并调整正式程度。有关完整适配过程，请参阅`../blog-localize/SKILL.md`。

进度：`第4阶段：[N]种语言的文化适配完成`。

### 第5阶段：国际SEO生成

生成三个工件和本地化模式。如果安装了`claude-seo`的`seo-hreflang`技能，则将验证委托给它。否则使用下文的自包含生成器。

#### 5a. Hreflang标签（HTML）

适用于`<head>`的复制粘贴标签：

```html
<!-- Hreflang标签。粘贴到每个语言版本的<head>中。 -->
<link rel="alternate" hreflang="{source}" href="https://example.com/{source-url}" />
<link rel="alternate" hreflang="{lang-1}" href="https://example.com/{lang-1-url}" />
<link rel="alternate" hreflang="{lang-2}" href="https://example.com/{lang-2-url}" />
<link rel="alternate" hreflang="x-default" href="https://example.com/{fallback-url}" />
```

规则（与`seo-hreflang`相同）：

- 每个页面引用所有替代版本，包括自身（自我引用）。
- 每个`href`，包括`x-default`，都是完全限定绝对`https://...` URL。
- `x-default`指向未匹配语言的回退，例如全局语言选择器或默认市场页面。它不必是源语言版本。
- 所有URL使用相同协议（HTTPS）和尾随斜杠约定。
- 双向：每个关系都是互惠的。

保存到`multilingual/hreflang-tags.html`。

#### 5b. Hreflang站点地图片段

```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:xhtml="http://www.w3.org/1999/xhtml">
  <url>
    <loc>https://example.com/{source-url}</loc>
    <xhtml:link rel="alternate" hreflang="{source}" href="https://example.com/{source-url}" />
    <xhtml:link rel="alternate" hreflang="{lang-1}" href="https://example.com/{lang-1-url}" />
    <xhtml:link rel="alternate" hreflang="{lang-2}" href="https://example.com/{lang-2-url}" />
    <xhtml:link rel="alternate" hreflang="x-default" href="https://example.com/{fallback-url}" />
  </url>
  <url>
    <loc>https://example.com/{lang-1-url}</loc>
    <xhtml:link rel="alternate" hreflang="{source}" href="https://example.com/{source-url}" />
    <xhtml:link rel="alternate" hreflang="{lang-1}" href="https://example.com/{lang-1-url}" />
    <xhtml:link rel="alternate" hreflang="{lang-2}" href="https://example.com/{lang-2-url}" />
    <xhtml:link rel="alternate" hreflang="x-default" href="https://example.com/{fallback-url}" />
  </url>
  <url>
    <loc>https://example.com/{lang-2-url}</loc>
    <xhtml:link rel="alternate" hreflang="{source}" href="https://example.com/{source-url}" />
    <xhtml:link rel="alternate" hreflang="{lang-1}" href="https://example.com/{lang-1-url}" />
    <xhtml:link rel="alternate" hreflang="{lang-2}" href="https://example.com/{lang-2-url}" />
    <xhtml:link rel="alternate" hreflang="x-default" href="https://example.com/{fallback-url}" />
  </url>
</urlset>
```

每个区域生成一个`<url>`块。每个块必须包含每个区域的完整`<xhtml:link>`替代版本集，包括自身和可选的`x-default`，使用完全限定`https://...` URL。

保存到`multilingual/hreflang-sitemap.xml`。

#### 5c. Hreflang映射（JSON）

机器可读的CMS集成映射：

```json
{
  "sourceSlug": "how-to-avoid-ai-slop",
  "sourceLanguage": "en",
  "generatedDate": "YYYY-MM-DD",
  "versions": [
    {
      "lang": "en",
      "locale": "en",
      "hreflang": "en",
      "slug": "how-to-avoid-ai-slop",
      "file": "en/how-to-avoid-ai-slop.md",
      "url": "https://example.com/en/how-to-avoid-ai-slop/",
      "canonical": "https://example.com/en/how-to-avoid-ai-slop/",
      "xDefault": true,
      "title": "How to Avoid AI Slop in 2026",
      "description": "..."
    },
    {
      "lang": "de",
      "locale": "de-DE",
      "hreflang": "de-DE",
      "slug": "wie-man-ki-slop-vermeidet",
      "file": "de/wie-man-ki-slop-vermeidet.md",
      "url": "https://example.com/de/wie-man-ki-slop-vermeidet/",
      "canonical": "https://example.com/de/wie-man-ki-slop-vermeidet/",
      "xDefault": false,
      "title": "KI-Slop vermeiden in 2026",
      "description": "..."
    }
  ],
  "hreflang": {
    "method": "html",
    "x-default": "https://example.com/"
  }
}
```

保存到`multilingual/hreflang-map.json`。

#### 5d. 本地化Article模式（必需）

在每个语言版本上附加或更新Article/BlogPosting JSON-LD，包含`inLanguage`和`translationOfWork`字段：

```json
{
  "@context": "https://schema.org",
  "@type": "BlogPosting",
  "headline": "[本地化标题]",
  "description": "[本地化描述]",
  "inLanguage": "[lang-code]",
  "isPartOf": { "@type": "Blog", "inLanguage": "[lang-code]" },
  "translationOfWork": {
    "@type": "BlogPosting",
    "inLanguage": "[source-lang]",
    "url": "[source-url]"
  }
}
```

使用现有的`/blog schema`子技能为每个版本生成更丰富的模式。优先使用Article/BlogPosting、Person、Organization和BreadcrumbList。FAQPage是可选的，仅在存在可见FAQ内容时作为实体和AI引用信号，而不是Google丰富结果目标。

### 第6阶段：交付摘要

```
## 多语言博客完成：[标题]

### 原始版本
- 语言：[source]
- 文件：multilingual/{source}/{slug}.{ext}

### 翻译版本
| 语言 | 文件 | 本地化 | 关键词适配 |
|----------|------|-----------|------------------|
| de | multilingual/de/{slug}.md | 是 | [N] |
| fr | multilingual/fr/{slug}.md | 是 | [N] |
| es | multilingual/es/{slug}.md | 是 | [N] |

### 国际SEO资源
- multilingual/hreflang-tags.html
- multilingual/hreflang-sitemap.xml
- multilingual/hreflang-map.json
- 每个版本嵌入本地化Article模式

### 总计
- [N]篇[N]语言文章
- 生成[N]个SEO资源

### 下一步
- 将hreflang标签中的`{source-url}`、`{lang-1-url}`、`{lang-2-url}`和
  `{fallback-url}`占位符替换为真实的绝对HTTPS URL。
- 将`hreflang-sitemap.xml`合并到现有站点地图中。
- 运行`/blog locale-audit multilingual/`以验证完整性。
- 使用特定语言URL解决`[INTERNAL-LINK]`占位符。
- 如果安装了claude-seo，运行`/seo hreflang multilingual/`进行深度验证。
```

## 交叉引用

| 情况 | 运行 |
|------|-----|
| 重新生成或重写源 | `/blog write <topic>` |
| 仅翻译一个现有文件 | `/blog translate <file> --to <codes>` |
| 对一个文件进行深度文化适配 | `/blog localize <file> --locale <code>` |
| 审计多语言目录 | `/blog locale-audit <directory>` |
| 进行深度hreflang验证 | `/seo hreflang <directory>`（claude-seo，可选） |

## 错误处理

| 情景 | 动作 |
|----------|--------|
| `blog-write`缺失 | 错误：`"此技能需要`blog-write`。重新安装claude-blog。" |
| 一个翻译失败 | 完成其余部分，报告部分结果，建议重试命令 |
| 源语言等于目标 | 跳过该目标，记录通知 |
| 10个或更多目标语言 | 在写入前停止。解释扩展内容滥用风险，并要求最多9个目标语言的审核批次 |
| `seo-hreflang`未安装 | 使用自包含生成器，在摘要中注明 |

## 命令概要

| 命令 | 目的 |
|---------|---------|
| `/blog multilingual <topic> --languages de,fr,es` | 撰写源内容，翻译，本地化，生成hreflang资源 |
| `/blog translate <file> --to de,fr,es` | 将一个文件翻译成目标语言 |
| `/blog localize <file> --locale de-DE` | 对一个翻译后的文件进行深度文化适配 |
| `/blog locale-audit <directory>` | 目录的多语言QA |
