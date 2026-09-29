---
name: markdown-to-html
description: 将 Markdown 文件转换为 HTML，类似于 `marked.js`、`pandoc`、`gomarkdown/markdown` 或类似工具；或者编写自定义脚本将 Markdown 转换为 HTML，以及/或者处理类似 `jekyll/jekyll`、`gohugoio/hugo` 或类似利用 Markdown 文档的 Web 模板系统，将其转换为 HTML。在要求“将 Markdown 转换为 HTML”、“将 md 转换为 html”、“渲染 Markdown”、“从 Markdown 生成 HTML”，或处理 .md 文件和/或使用 Markdown 转换为 HTML 输出的 Web 模板系统时使用。支持 GFM、CommonMark 和标准 Markdown 风格的 CLI 和 Node.js 工作流程。
---

# Markdown to HTML 转换

使用 marked.js 库将 Markdown 文档转换为 HTML 的专业技能，或编写数据转换脚本；在这种情况下，脚本类似于 [markedJS/marked](https://github.com/markedjs/marked) 仓库。对于自定义脚本，知识不仅限于 `marked.js`，而是利用类似 [pandoc](https://github.com/jgm/pandoc) 和 [gomarkdown/markdown](https://github.com/gomarkdown/markdown) 等工具中的数据转换方法；[jekyll/jekyll](https://github.com/jekyll/jekyll) 和 [gohugoio/hugo](https://github.com/gohugoio/hugo) 用于模板系统。

转换脚本或工具应处理单个文件、批量转换和高级配置。

## 何时使用此技能

- 用户要求“将 markdown 转换为 html”或“转换 md 文件”
- 用户希望将“markdown 渲染”为 HTML 输出
- 用户需要从 .md 文件生成 HTML 文档
- 用户正在使用 Markdown 内容构建静态网站
- 用户正在构建将 markdown 转换为 html 的模板系统
- 用户正在为现有模板系统工作开发工具、小部件或自定义模板
- 用户希望预览渲染后的 Markdown 作为 HTML

## 将 Markdown 转换为 HTML

### 基本转换

更多内容请参见 [basic-markdown-to-html.md](references/basic-markdown-to-html.md)

```text
    ```markdown
    # Level 1
    ## Level 2

    One sentence with a [link](https://example.com), and a HTML snippet like `<p>paragraph tag</p>`.

    - `ul` list item 1
    - `ul` list item 2

    1. `ol` list item 1
    2. `ol` list item 1

    | Table Item | Description |
    | One | One is the spelling of the number `1`. |
    | Two | Two is the spelling of the number `2`. |

    ```js
    var one = 1;
    var two = 2;

    function simpleMath(x, y) {
     return x + y;
    }
    console.log(simpleMath(one, two));
    ```
    ```

    ```html
    <h1>Level 1</h1>
    <h2>Level 2</h2>

    <p>One sentence with a <a href="https://example.com">link</a>, and a HTML snippet like <code>&lt;p&gt;paragraph tag&lt;/p&gt;</code>.</p>

    <ul>
     <li>`ul` list item 1</li>
     <li>`ul` list item 2</li>
    </ul>

    <ol>
     <li>`ol` list item 1</li>
     <li>`ol` list item 2</li>
    </ol>

    <table>
     <thead>
      <tr>
       <th>Table Item</th>
       <th>Description</th>
      </tr>
     </thead>
     <tbody>
      <tr>
       <td>One</td>
       <td>One is the spelling of the number `1`.</td>
      </tr>
      <tr>
       <td>Two</td>
       <td>Two is the spelling of the number `2`.</td>
      </tr>
     </tbody>
    </table>

    <pre>
     <code>var one = 1;
     var two = 2;

     function simpleMath(x, y) {
      return x + y;
     }
     console.log(simpleMath(one, two));</code>
    </pre>
    ```
```

### 代码块转换

更多内容请参见 [code-blocks-to-html.md](references/code-blocks-to-html.md)

```text

    ```markdown
    your code here
    ```

    ```html
    <pre><code class="language-md">
    your code here
    </code></pre>
    ```

    ```js
    console.log("Hello world");
    ```

    ```html
    <pre><code class="language-js">
    console.log("Hello world");
    </code></pre>
    ```

    ```markdown
      ```

      ```
      visible backticks
      ```

      ```
    ```

    ```html
      <pre><code>
      ```

      visible backticks

      ```
      </code></pre>
    ```
```

### 折叠区域转换

更多内容请参见 [collapsed-sections-to-html.md](references/collapsed-sections-to-html.md)

```text
    ```markdown
    <details>
    <summary>More info</summary>

    ### Header inside

    - Lists
    - **Formatting**
    - Code blocks

        ```js
        console.log("Hello");
        ```

    </details>
    ```

    ```html
    <details>
    <summary>More info</summary>

    <h3>Header inside</h3>

    <ul>
     <li>Lists</li>
     <li><strong>Formatting</strong></li>
     <li>Code blocks</li>
    </ul>

    <pre>
     <code class="language-js">console.log("Hello");</code>
    </pre>

    </details>
    ```
```

### 数学表达式转换

更多内容请参见 [writing-mathematical-expressions-to-html.md](references/writing-mathematical-expressions-to-html.md)

```text
    ```markdown
    This sentence uses `$` delimiters to show math inline: $\sqrt{3x-1}+(1+x)^2$
    ```

    ```html
    <p>This sentence uses <code>$</code> delimiters to show math inline:
     <math-renderer><math xmlns="http://www.w3.org/1998/Math/MathML">
      <msqrt><mn>3</mn><mi>x</mi><mo>−</mo><mn>1</mn></msqrt>
      <mo>+</mo><mo>(</mo><mn>1</mn><mo>+</mo><mi>x</mi>
      <msup><mo>)</mo><mn>2</mn></msup>
     </math>
    </math-renderer>
    </p>
    ```

    ```markdown
    **The Cauchy-Schwarz Inequality**\
    $$\left( \sum_{k=1}^n a_k b_k \right)^2 \leq \left( \sum_{k=1}^n a_k^2 \right) \left( \sum_{k=1}^n b_k^2 \right)$$
    ```

    ```html
    <p><strong>The Cauchy-Schwarz Inequality</strong><br>
     <math-renderer>
      <math xmlns="http://www.w3.org/1998/Math/MathML">
       <msup>
        <mrow><mo>(</mo>
         <munderover><mo data-mjx-texclass="OP">∑</mo>
          <mrow><mi>k</mi><mo>=</mo><mn>1</mn></mrow><mi>n</mi>
         </munderover>
         <msub><mi>a</mi><mi>k</mi></msub>
         <msub><mi>b</mi><mi>k</mi></msub>
         <mo>)</mo>
        </mrow>
        <mn>2</mn>
       </msup>
       <mo>≤</mo>
       <mrow><mo>(</mo>
        <munderover><mo>∑</mo>
         <mrow><mi>k</mi><mo>=</mo><mn>1</mn></mrow>
         <mi>n</mi>
        </munderover>
        <msubsup><mi>a</mi><mi>k</mi><mn>2</mn></msubsup>
        <mo>)</mo>
       </mrow>
       <mrow><mo>(</mo>
         <munderover><mo>∑</mo>
          <mrow><mi>k</mi><mo>=</mo><mn>1</mn></mrow>
          <mi>n</mi>
         </munderover>
         <msubsup><mi>b</mi><mi>k</mi><mn>2</mn></msubsup>
         <mo>)</mo>
       </mrow>
      </math>
     </math-renderer></p>
    ```
```

### 表格转换

更多内容请参见 [tables-to-html.md](references/tables-to-html.md)

```text
    ```markdown
    | First Header  | Second Header |
    | ------------- | ------------- |
    | Content Cell  | Content Cell  |
    | Content Cell  | Content Cell  |
    ```

    ```html
    <table>
     <thead><tr><th>First Header</th><th>Second Header</th></tr></thead>
     <tbody>
      <tr><td>Content Cell</td><td>Content Cell</td></tr>
      <tr><td>Content Cell</td><td>Content Cell</td></tr>
     </tbody>
    </table>
    ```

    ```markdown
    | Left-aligned | Center-aligned | Right-aligned |
    | :---         |     :---:      |          ---: |
    | git status   | git status     | git status    |
    | git diff     | git diff       | git diff      |
    ```

    ```html
    <table>
      <thead>
       <tr>
        <th align="left">Left-aligned</th>
        <th align="center">Center-aligned</th>
        <th align="right">Right-aligned</th>
       </tr>
      </thead>
      <tbody>
       <tr>
        <td align="left">git status</td>
        <td align="center">git status</td>
        <td align="right">git status</td>
       </tr>
       <tr>
        <td align="left">git diff</td>
        <td align="center">git diff</td>
        <td align="right">git diff</td>
       </tr>
      </tbody>
    </table>
    ```
```

## 使用 [`markedJS/marked`](references/marked.md)

### 前置条件

- 安装 Node.js（用于 CLI 或程序化使用）
- 使用 CLI 全局安装 marked：`npm install -g marked`
- 或本地安装：`npm install marked`

### 快速转换方法

参见 [marked.md](references/marked.md) **快速转换方法**

### 分步工作流程

参见 [marked.md](references/marked.md) **分步工作流程**

### CLI 配置

### 使用配置文件

创建 `~/.marked.json` 用于持久选项：

```json
{
  "gfm": true,
  "breaks": true
}
```

或使用自定义配置：

```bash
marked -i input.md -o output.html -c config.json
```

### CLI 选项参考

| 选项 | 描述 |
|------|-------------|
| `-i, --input <file>` | 输入 Markdown 文件 |
| `-o, --output <file>` | 输出 HTML 文件 |
| `-s, --string <string>` | 解析字符串而不是文件 |
| `-c, --config <file>` | 使用自定义配置文件 |
| `--gfm` | 启用 GitHub Flavored Markdown |
| `--breaks` | 将换行符转换为 `<br>` |
| `--help` | 显示所有选项 |

### 安全警告

⚠️ **Marked 不会清理输出 HTML。** 对于不可信的输入，使用清理器：

```javascript
import { marked } from 'marked';
import DOMPurify from 'dompurify';

const unsafeHtml = marked.parse(untrustedMarkdown);
const safeHtml = DOMPurify.sanitize(unsafeHtml);
```

推荐清理器：

- [DOMPurify](https://github.com/cure53/DOMPurify) (推荐)
- [sanitize-html](https://github.com/apostrophecms/sanitize-html)
- [js-xss](https://github.com/leizongmin/js-xss)

### 支持的 Markdown 风格

| 风格 | 支持 |
|--------|---------|
| 原始 Markdown | 100% |
| CommonMark 0.31 | 98% |
| GitHub Flavored Markdown | 97% |

### 故障排除

| 问题 | 解决方案 |
|-------|----------|
| 文件开头特殊字符 | 移除零宽度字符：`content.replace(/^[\u200B\u200C\u200D\uFEFF]/,"")` |
| 代码块不突出显示 | 添加语法高亮器如 highlight.js |
| 表格不渲染 | 确保 `gfm: true` 选项已设置 |
| 行断被忽略 | 在选项中设置 `breaks: true` |
| XSS 漏洞问题 | 使用 DOMPurify 清理输出 |

## 使用 [`pandoc`](references/pandoc.md)

### 前置条件

- 安装 Pandoc（从 <https://pandoc.org/installing.html> 下载）
- 对于 PDF 输出：安装 LaTeX（MacTeX 在 macOS 上，MiKTeX 在 Windows 上，texlive 在 Linux 上）
- 终端/命令提示符访问

### 快速转换方法

#### 方法 1：CLI 基本转换

```bash
# 将 markdown 转换为 HTML
pandoc input.md -o output.html

# 转换为独立文档（包含头部/尾部）
pandoc input.md -s -o output.html

# 显式格式指定
pandoc input.md -f markdown -t html -s -o output.html
```

#### 方法 2：过滤器模式（交互式）

```bash
# 以过滤器方式启动 pandoc
pandoc

# 输入 markdown，然后 Ctrl-D (Linux/macOS) 或 Ctrl-Z+Enter (Windows)
Hello *pandoc*!
# 输出: <p>Hello <em>pandoc</em>!</p>
```

#### 方法 3：格式转换

```bash
# HTML 到 Markdown
pandoc -f html -t markdown input.html -o output.md

# Markdown 到 LaTeX
pandoc input.md -s -o output.tex

# Markdown 到 PDF（需要 LaTeX）
pandoc input.md -s -o output.pdf

# Markdown 到 Word
pandoc input.md -s -o output.docx
```

### CLI 配置

| 选项 | 描述 |
|--------|-------------|
| `-f, --from <format>` | 输入格式（markdown, html, latex, 等） |
| `-t, --to <format>` | 输出格式（html, latex, pdf, docx, 等） |
| `-s, --standalone` | 生成包含头部/尾部的独立文档 |
| `-o, --output <file>` | 输出文件（从扩展名推断） |
| `--mathml` | 将 TeX 数学转换为 MathML |
| `--metadata title="Title"` | 设置文档元数据 |
| `--toc` | 包含目录 |
| `--template <file>` | 使用自定义模板 |
| `--help` | 显示所有选项 |

### 安全警告

⚠️ **Pandoc 忠实处理输入。** 在转换不可信的 markdown 时：

- 使用 `--sandbox` 模式禁用外部文件访问
- 在处理前验证输入
- 如果在浏览器中显示 HTML 输出，则清理 HTML 输出

```bash
# 以 sandbox 模式运行不可信输入
pandoc --sandbox input.md -o output.html
```

### 支持的 Markdown 风格

| 风格 | 支持 |
|--------|---------|
| Pandoc Markdown | 100% (原生) |
| CommonMark | 完整（使用 `-f commonmark`） |
| GitHub Flavored Markdown | 完整（使用 `-f gfm`） |
| MultiMarkdown | 部分支持 |

### 故障排除

| 问题 | 解决方案 |
|-------|----------|
| PDF 生成失败 | 安装 LaTeX (MacTeX, MiKTeX 或 texlive) |
| Windows 上编码问题 | 在使用 pandoc 前运行 `chcp 65001` |
| 缺少独立文档头部 | 添加 `-s` 标志以生成完整文档 |
| 数学不渲染 | 使用 `--mathml` 或 `--mathjax` 选项 |
| 表格不渲染 | 确保使用管道和连字符的适当表格语法 |

## 使用 [`gomarkdown/markdown`](references/gomarkdown.md)

### 前置条件

- 安装 Go 1.18 或更高版本
- 安装库：`go get github.com/gomarkdown/markdown`
- 对于 CLI 工具：`go install github.com/gomarkdown/mdtohtml@latest`

### 快速转换方法

#### 方法 1：简单转换（Go）

```go
package main

import (
    "fmt"
    "github.com/gomarkdown/markdown"
)

func main() {
    md := []byte("# Hello World\n\nThis is **bold** text.")
    html := markdown.ToHTML(md, nil, nil)
    fmt.Println(string(html))
}
```

#### 方法 2：CLI 工具

```bash
# 安装 mdtohtml
go install github.com/gomarkdown/mdtohtml@latest

# 转换文件
mdtohtml input.md output.html

# 转换文件（输出到标准输出）
mdtohtml input.md
```

#### 方法 3：自定义解析器和渲染器

```go
package main

import (
    "github.com/gomarkdown/markdown"
    "github.com/gomarkdown/markdown/html"
    "github.com/gomarkdown/markdown/parser"
)

func mdToHTML(md []byte) []byte {
    // 创建带有扩展的解析器
    extensions := parser.CommonExtensions | parser.AutoHeadingIDs | parser.NoEmptyLineBeforeBlock
    p := parser.NewWithExtensions(extensions)
    doc := p.Parse(md)

    // 创建带有扩展的 HTML 渲染器
    htmlFlags := html.CommonFlags | html.HrefTargetBlank
    opts := html.RendererOptions{Flags: htmlFlags}
    renderer := html.NewRenderer(opts)

    return markdown.Render(doc, renderer)
}
```

### CLI 配置

`mdtohtml` CLI 工具具有最少选项：

```bash
mdtohtml input-file [output-file]
```

对于高级配置，使用 Go 库程序化地使用解析器和渲染器选项：

| 解析器扩展 | 描述 |
|------------------|-------------|
| `parser.CommonExtensions` | 表格、代码块、自动链接、删除线等 |
| `parser.AutoHeadingIDs` | 为标题生成 ID |
| `parser.NoEmptyLineBeforeBlock` | 块前不需要空行 |
| `parser.MathJax` | LaTeX 数学支持 |

| HTML 标志 | 描述 |
|-----------|-------------|
| `html.CommonFlags` | 常用 HTML 输出标志 |
| `html.HrefTargetBlank` | 为链接添加 `target="_blank"` |
| `html.CompletePage` | 生成完整 HTML 页面 |
| `html.UseXHTML` | 生成 XHTML 输出 |

### 安全警告

⚠️ **gomarkdown 不会清理输出 HTML。** 对于不可信的输入，使用 Bluemonday：

```go
import (
    "github.com/microcosm-cc/bluemonday"
    "github.com/gomarkdown/markdown"
)

maybeUnsafeHTML := markdown.ToHTML(md, nil, nil)
html := bluemonday.UGCPolicy().SanitizeBytes(maybeUnsafeHTML)
```

推荐清理器：[Bluemonday](https://github.com/microcosm-cc/bluemonday)

### 支持的 Markdown 风格

| 风格 | 支持 |
|--------|---------|
| 原始 Markdown | 100% |
| CommonMark | 高（带扩展） |
| GitHub Flavored Markdown | 高（表格、代码块、删除线） |
| MathJax/LaTeX 数学 | 通过扩展支持 |
| Mmark | 支持 |

### 故障排除

| 问题 | 解决方案 |
|-------|----------|
| Windows/Mac 新行未解析 | 使用 `parser.NormalizeNewlines(input)` |
| 表格不渲染 | 启用 `parser.Tables` 扩展 |
| 代码块无高亮 | 集成语法高亮器如 Chroma |
| 数学不渲染 | 启用 `parser.MathJax` 扩展 |
| XSS 漏洞 | 使用 Bluemonday 清理输出 |

## 使用 [`jekyll`](references/jekyll.md)

### 前置条件

- Ruby 版本 2.7.0 或更高
- RubyGems
- GCC 和 Make（用于本地扩展）
- 安装 Jekyll 和 Bundler：`gem install jekyll bundler`

### 快速转换方法

#### 方法 1：创建新站点

```bash
# 创建新的 Jekyll 站点
jekyll new myblog

# 切换到站点目录
cd myblog

# 构建并在本地服务
bundle exec jekyll serve

# 访问 http://localhost:4000
```

#### 方法 2：构建静态站点

```bash
# 生成站点到 _site 目录
bundle exec jekyll build

# 使用生产环境构建
JEKYLL_ENV=production bundle exec jekyll build
```

#### 第 3 种方法：实时重载开发

```bash
# 使用实时重载服务
bundle exec jekyll serve --livereload

# 包含草稿
bundle exec jekyll serve --drafts
```

### 命令行配置

| 命令 | 描述 |
|------|------|
| `jekyll new <路径>` | 创建新的 Jekyll 站点 |
| `jekyll build` | 生成站点到 `_site` 目录 |
| `jekyll serve` | 本地构建并服务 |
| `jekyll clean` | 删除生成的文件 |
| `jekyll doctor` | 检查配置问题 |

| 服务选项 | 描述 |
|----------|------|
| `--livereload` | 内容变更时刷新浏览器 |
| `--drafts` | 包含草稿文章 |
| `--port <端口>` | 设置服务器端口（默认：4000） |
| `--host <主机>` | 设置服务器主机（默认：localhost） |
| `--baseurl <URL>` | 设置基本 URL |

### 安全警告

⚠️ **Jekyll 安全注意事项：**

- 生产环境中避免使用 `safe: false`
- 在 `_config.yml` 中使用 `exclude` 防止发布敏感文件
- 如果接受外部输入，请对用户生成的内容进行消毒
- 保持 Jekyll 和插件更新

```yaml
# _config.yml 安全设置
exclude:
  - Gemfile
  - Gemfile.lock
  - node_modules
  - vendor
```

### 支持的 Markdown 款式

| 款式 | 支持 |
|------|------|
| Kramdown（默认） | 100% |
| CommonMark | 通过插件（jekyll-commonmark） |
| GitHub Flavored Markdown | 通过插件（jekyll-commonmark-ghpages） |
| RedCarpet | 通过插件（已弃用） |

在 `_config.yml` 中配置 Markdown 处理器：

```yaml
markdown: kramdown
kramdown:
  input: GFM
  syntax_highlighter: rouge
```

### 故障排除

| 问题 | 解决方案 |
|------|------|
| Ruby 3.0+ 无法服务 | 运行 `bundle add webrick` |
| Gem 依赖错误 | 运行 `bundle install` |
| 构建缓慢 | 使用 `--incremental` 标志 |
| Liquid 语法错误 | 检查内容中的未转义 `{` |
| 插件无法加载 | 添加到 `_config.yml` 插件列表 |

## 使用 [`hugo`](references/hugo.md)

### 前置条件

- 安装 Hugo（从 <https://gohugo.io/installation/> 下载）
- Git（推荐用于主题和模块）
- Go（可选，用于 Hugo Modules）

### 快速转换方法

#### 第 1 种方法：创建新站点

```bash
# 创建新的 Hugo 站点
hugo new site mysite

# 切换到站点目录
cd mysite

# 添加主题
git init
git submodule add https://github.com/theNewDynamic/gohugo-theme-ananke themes/ananke
echo "theme = 'ananke'" >> hugo.toml

# 创建内容
hugo new content posts/my-first-post.md

# 启动开发服务器
hugo server -D
```

#### 第 2 种方法：构建静态站点

```bash
# 构建站点到 public 目录
hugo

# 使用压缩
hugo --minify

# 为特定环境构建
hugo --environment production
```

#### 第 3 种方法：开发服务器

```bash
# 启动带草稿的服务器
hugo server -D

# 启动并绑定到所有接口，带实时重载
hugo server --bind 0.0.0.0 --baseURL http://localhost:1313/

# 使用特定端口启动
hugo server --port 8080
```

### 命令行配置

| 命令 | 描述 |
|------|------|
| `hugo new site <名称>` | 创建新的 Hugo 站点 |
| `hugo new content <路径>` | 创建新的内容文件 |
| `hugo` | 构建站点到 `public` 目录 |
| `hugo server` | 启动开发服务器 |
| `hugo mod init` | 初始化 Hugo Modules |

| 构建选项 | 描述 |
|----------|------|
| `-D, --buildDrafts` | 包含草稿内容 |
| `-E, --buildExpired` | 包含过期内容 |
| `-F, --buildFuture` | 包含未来日期内容 |
| `--minify` | 压缩输出 |
| `--gc` | 构建后运行垃圾回收 |
| `-d, --destination <路径>` | 输出目录 |

| 服务器选项 | 描述 |
|------------|------|
| `--bind <IP>` | 绑定接口 |
| `-p, --port <端口>` | 端口号（默认：1313） |
| `--liveReloadPort <端口>` | 实时重载端口 |
| `--disableLiveReload` | 禁用实时重载 |
| `--navigateToChanged` | 切换到变更内容 |

### 安全警告

⚠️ **Hugo 安全注意事项：**

- 在 `hugo.toml` 中配置外部命令的安全策略
- 小心使用 `--enableGitInfo` 与公共仓库
- 验证短代码参数以处理用户生成的内容

```toml
# hugo.toml 安全设置
[security]
  enableInlineShortcodes = false
  [security.exec]
    allow = ['^go$', '^npx$', '^postcss$']
  [security.funcs]
    getenv = ['^HUGO_', '^CI$']
  [security.http]
    methods = ['(?i)GET|POST']
    urls = ['.*']
```

### 支持的 Markdown 款式

| 款式 | 支持 |
|------|------|
| Goldmark（默认） | 100%（符合 CommonMark 标准） |
| GitHub Flavored Markdown | 完整（表格、删除线、自动链接） |
| CommonMark | 100% |
| Blackfriday（遗留） | 已弃用，不推荐 |

在 `hugo.toml` 中配置 Markdown：

```toml
[markup]
  [markup.goldmark]
    [markup.goldmark.extensions]
      definitionList = true
      footnote = true
      linkify = true
      strikethrough = true
      table = true
      taskList = true
    [markup.goldmark.renderer]
      unsafe = false  # 设置为 true 允许原始 HTML
```

### 故障排除

| 问题 | 解决方案 |
|------|------|
| 路径上出现 "页面未找到" | 检查 config 中的 `baseURL` |
| 主题未加载 | 验证主题是否在 `themes/` 或 Hugo Modules 中 |
| 构建缓慢 | 使用 `--templateMetrics` 识别瓶颈 |
| 原始 HTML 未渲染 | 在 goldmark 配置中设置 `unsafe = true` |
| 图片无法加载 | 检查 `static/` 文件夹结构 |
| 模块错误 | 运行 `hugo mod tidy` |

## 参考

### 编写和格式化 Markdown

- [basic-markdown.md](references/basic-markdown.md)
- [code-blocks.md](references/code-blocks.md)
- [collapsed-sections.md](references/collapsed-sections.md)
- [tables.md](references/tables.md)
- [writing-mathematical-expressions.md](references/writing-mathematical-expressions.md)
- Markdown 指南：<https://www.markdownguide.org/basic-syntax/>
- Markdown 样式：<https://github.com/sindresorhus/github-markdown-css>

### [`markedJS/marked`](references/marked.md)

- 官方文档：<https://marked.js.org/>
- 高级选项：<https://marked.js.org/using_advanced>
- 扩展性：<https://marked.js.org/using_pro>
- GitHub 仓库：<https://github.com/markedjs/marked>

### [`pandoc`](references/pandoc.md)

- 入门指南：<https://pandoc.org/getting-started.html>
- 官方文档：<https://pandoc.org/MANUAL.html>
- 扩展性：<https://pandoc.org/extras.html>
- GitHub 仓库：<https://github.com/jgm/pandoc>

### [`gomarkdown/markdown`](references/gomarkdown.md)

- 官方文档：<https://pkg.go.dev/github.com/gomarkdown/markdown>
- 高级配置：<https://pkg.go.dev/github.com/gomarkdown/markdown@v0.0.0-20250810172220-2e2c11897d1a/html>
- Markdown 处理：<https://blog.kowalczyk.info/article/cxn3/advanced-markdown-processing-in-go.html>
- GitHub 仓库：<https://github.com/gomarkdown/markdown>

### [`jekyll`](references/jekyll.md)

- 官方文档：<https://jekyllrb.com/docs/>
- 配置选项：<https://jekyllrb.com/docs/configuration/options/>
- 插件：<https://jekyllrb.com/docs/plugins/>
  - [安装](https://jekyllrb.com/docs/plugins/installation/)
  - [生成器](https://jekyllrb.com/docs/plugins/generators/)
  - [转换器](https://jekyllrb.com/docs/plugins/converters/)
  - [命令](https://jekyllrb.com/docs/plugins/commands/)
  - [标签](https://jekyllrb.com/docs/plugins/tags/)
  - [过滤器](https://jekyllrb.com/docs/plugins/filters/)
  - [钩子](https://jekyllrb.com/docs/plugins/hooks/)
- GitHub 仓库：<https://github.com/jekyll/jekyll>

### [`hugo`](references/hugo.md)

- 官方文档：<https://gohugo.io/documentation/>
- 所有设置：<https://gohugo.io/configuration/all/>
- 编辑器插件：<https://gohugo.io/tools/editors/>
- GitHub 仓库：<https://github.com/gohugoio/hugo>
