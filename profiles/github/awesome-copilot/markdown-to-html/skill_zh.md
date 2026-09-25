# Markdown到HTML转换

使用marked.js库将Markdown文档转换为HTML的专业技能，或编写数据转换脚本；在这种情况下，脚本类似于[markedJS/marked](https://github.com/markedjs/marked)仓库。对于自定义脚本，知识不仅限于`marked.js`，而是利用像[pandoc](https://github.com/jgm/pandoc)和[gomarkdown/markdown](https://github.com/gomarkdown/markdown)等工具中的数据转换方法；[jekyll/jekyll](https://github.com/jekyll/jekyll)和[gohugoio/hugo](https://github.com/gohugoio/hugo)用于模板系统。

转换脚本或工具应处理单个文件、批量转换和高级配置。

## 何时使用此技能

- 用户要求"将markdown转换为html"或"转换md文件"
- 用户希望将"markdown渲染为HTML输出"
- 用户需要从.md文件生成HTML文档
- 用户正在使用Markdown内容构建静态网站
- 用户正在构建将markdown转换为html的模板系统
- 用户正在为现有模板系统工作开发工具、小部件或自定义模板
- 用户希望预览渲染后的Markdown作为HTML

## 将Markdown转换为HTML

### 基本转换

更多内容请参见[basic-markdown-to-html.md](references/basic-markdown-to-html.md)

```text
    ```markdown
    # 一级标题
    ## 二级标题

    一句话带有一个[链接](https://example.com)，以及一个HTML片段如`<p>段落标签</p>`。

    - `ul`列表项1
    - `ul`列表项2

    1. `ol`列表项1
    2. `ol`列表项1

    | 表格项 | 描述 |
    | --- | --- |
    | 一 | 一是一的拼写。 |
    | 二 | 二是二的拼写。 |

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
    <h1>一级标题</h1>
    <h2>二级标题</h2>

    <p>一句话带有一个<a href="https://example.com">链接</a>，以及一个HTML片段如`<code>&lt;p&gt;段落标签&lt;/p&gt;</code>`。</p>

    <ul>
     <li>`ul`列表项1</li>
     <li>`ul`列表项2</li>
    </ul>

    <ol>
     <li>`ol`列表项1</li>
     <li>`ol`列表项2</li>
    </ol>

    <table>
     <thead>
      <tr>
       <th>表格项</th>
       <th>描述</th>
      </tr>
     </thead>
     <tbody>
      <tr>
       <td>一</td>
       <td>一是一的拼写。</td>
      </tr>
      <tr>
       <td>二</td>
       <td>二是二的拼写。</td>
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

更多内容请参见[code-blocks-to-html.md](references/code-blocks-to-html.md)

```text

    ```markdown
    你的代码在这里
    ```

    ```html
    <pre><code class="language-md">
    你的代码在这里
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
      可见反引号
      ```

      ```
    ```

    ```html
      <pre><code>
      ```

      可见反引号

      ```
      </code></pre>
    ```
```

### 折叠区域转换

更多内容请参见[collapsed-sections-to-html.md](references/collapsed-sections-to-html.md)

```text
    ```markdown
    <details>
    <summary>更多信息</summary>

    ### 区域内的标题

    - 列表
    - **格式化**
    - 代码块

        ```js
        console.log("Hello");
        ```

    </details>
    ```

    ```html
    <details>
    <summary>更多信息</summary>

    <h3>区域内的标题</h3>

    <ul>
     <li>列表</li>
     <li><strong>格式化</strong></li>
     <li>代码块</li>
    </ul>

    <pre>
     <code class="language-js">console.log("Hello");</code>
    </pre>

    </details>
    ```
```

### 数学表达式转换

更多内容请参见[writing-mathematical-expressions-to-html.md](references/writing-mathematical-expressions-to-html.md)

```text
    ```markdown
    这句话使用`$`分隔符来显示内联数学：$\sqrt{3x-1}+(1+x)^2$
    ```

    ```html
    <p>这句话使用<code>$</code>分隔符来显示内联数学：
     <math-renderer><math xmlns="http://www.w3.org/1998/Math/MathML">
      <msqrt><mn>3</mn><mi>x</mi><mo>−</mo><mn>1</mn></msqrt>
      <mo>+</mo><mo>(</mo><mn>1</mn><mo>+</mo><mi>x</mi>
      <msup><mo>)</mo><mn>2</mn></msup>
     </math>
    </math-renderer>
    </p>
    ```

    ```markdown
    **柯西-施瓦茨不等式**\
    $$\left( \sum_{k=1}^n a_k b_k \right)^2 \leq \left( \sum_{k=1}^n a_k^2 \right) \left( \sum_{k=1}^n b_k^2 \right)$$
    ```

    ```html
    <p><strong>柯西-施瓦茨不等式</strong><br>
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

更多内容请参见[tables-to-html.md](references/tables-to-html.md)

```text
    ```markdown
    | 第一标题 | 第二标题 |
    | --- | --- |
    | 内容单元格 | 内容单元格 |
    | 内容单元格 | 内容单元格 |
    ```

    ```html
    <table>
     <thead><tr><th>第一标题</th><th>第二标题</th></tr></thead>
     <tbody>
      <tr><td>内容单元格</td><td>内容单元格</td></tr>
      <tr><td>内容单元格</td><td>内容单元格</td></tr>
     </tbody>
    </table>
    ```

    ```markdown
    | 左对齐 | 居中对齐 | 右对齐 |
    | :--- | :---: | ---: |
    | git status | git status | git status |
    | git diff | git diff | git diff |
    ```

    ```html
    <table>
      <thead>
       <tr>
        <th align="left">左对齐</th>
        <th align="center">居中对齐</th>
        <th align="right">右对齐</th>
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

## 使用[`markedJS/marked`](references/marked.md)

### 前置条件

- 安装Node.js（用于CLI或程序化使用）
- 使用CLI全局安装marked：`npm install -g marked`
- 或本地安装：`npm install marked`

### 快速转换方法

参见[marked.md](references/marked.md) **快速转换方法**

### 分步工作流程

参见[marked.md](references/marked.md) **分步工作流程**

### CLI配置

### 使用配置文件

创建`~/.marked.json`用于持久选项：

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

### CLI选项参考

| 选项 | 描述 |
|------|------|
| `-i, --input <file>` | 输入Markdown文件 |
| `-o, --output <file>` | 输出HTML文件 |
| `-s, --string <string>` | 解析字符串而不是文件 |
| `-c, --config <file>` | 使用自定义配置文件 |
| `--gfm` | 启用GitHub Flavored Markdown |
| `--breaks` | 将换行符转换为`<br>` |
| `--help` | 显示所有选项 |

### 安全警告

⚠️ **Marked不会清理输出HTML。** 对于不可信的输入，使用清理器：

```javascript
import { marked } from 'marked';
import DOMPurify from 'dompurify';

const unsafeHtml = marked.parse(untrustedMarkdown);
const safeHtml = DOMPurify.sanitize(unsafeHtml);
```

推荐清理器：

- [DOMPurify](https://github.com/cure53/DOMPurify)（推荐）
- [sanitize-html](https://github.com/apostrophecms/sanitize-html)
- [js-xss](https://github.com/leizongmin/js-xss)

### 支持的Markdown风味

| 风味 | 支持 |
|------|------|
| 原始Markdown | 100% |
| CommonMark 0.31 | 98% |
| GitHub Flavored Markdown | 97% |

### 故障排除

| 问题 | 解决方案 |
|------|------|
| 文件开头的特殊字符 | 移除零宽字符：`content.replace(/^[\u200B\u200C\u200D\uFEFF]/,"")` |
| 代码块不突出显示 | 添加语法高亮器如highlight.js |
| 表格不渲染 | 确保`gfm: true`选项已设置 |
| 行尾被忽略 | 在选项中设置`breaks: true` |
| XSS漏洞问题 | 使用DOMPurify清理输出 |

## 使用[`pandoc`](references/pandoc.md)

### 前置条件

- 安装Pandoc（从<https://pandoc.org/installing.html>下载）
- 对于PDF输出：安装LaTeX（macOS上的MacTeX，Windows上的MiKTeX，Linux上的texlive）
- 终端/命令提示符访问

### 快速转换方法

#### 方法1：CLI基本转换

```bash
# 将markdown转换为HTML
pandoc input.md -o output.html

# 转换为独立文档（包括头部/尾部）
pandoc input.md -s -o output.html

# 显式格式规范
pandoc input.md -f markdown -t html -s -o output.html
```

#### 方法2：过滤器模式（交互式）

```bash
# 以过滤器方式启动pandoc
pandoc

# 输入markdown，然后Ctrl-D（Linux/macOS）或Ctrl-Z+Enter（Windows）
Hello *pandoc*!
# 输出: <p>Hello <em>pandoc</em>!</p>
```

#### 方法3：格式转换

```bash
# HTML到Markdown
pandoc -f html -t markdown input.html -o output.md

# Markdown到LaTeX
pandoc input.md -s -o output.tex

# Markdown到PDF（需要LaTeX）
pandoc input.md -s -o output.pdf

# Markdown到Word
pandoc input.md -s -o output.docx
```

### CLI配置

| 选项 | 描述 |
|------|------|
| `-f, --from <format>` | 输入格式（markdown, html, latex, 等） |
| `-t, --to <format>` | 输出格式（html, latex, pdf, docx, 等） |
| `-s, --standalone` | 生成独立文档（包括头部/尾部） |
| `-o, --output <file>` | 输出文件（从扩展名推断） |
| `--mathml` | 将TeX数学转换为MathML |
| `--metadata title="Title"` | 设置文档元数据 |
| `--toc` | 包含目录 |
| `--template <file>` | 使用自定义模板 |
| `--help` | 显示所有选项 |

### 安全警告

⚠️ **Pandoc忠实地处理输入。** 当转换不可信的markdown时：

- 使用`--sandbox`模式禁用外部文件访问
- 在处理前验证输入
- 清理HTML输出如果要在浏览器中显示

```bash
# 以沙盒模式运行不可信输入
pandoc --sandbox input.md -o output.html
```

### 支持的Markdown风味

| 风味 | 支持 |
|------|------|
| Pandoc Markdown | 100% (原生) |
| CommonMark | 完整（使用`-f commonmark`） |
| GitHub Flavored Markdown | 完整（使用`-f gfm`） |
| MultiMarkdown | 部分支持 |

### 故障排除

| 问题 | 解决方案 |
|------|------|
| PDF生成失败 | 安装LaTeX（MacTeX, MiKTeX或texlive） |
| Windows上的编码问题 | 在使用pandoc前运行`chcp 65001` |
| 缺少独立头部 | 添加`-s`标志生成完整文档 |
| 数学不渲染 | 使用`--mathml`或`--mathjax`选项 |
| 表格不渲染 | 确保使用管道和连字符的适当表格语法 |

## 使用[`gomarkdown/markdown`](references/gomarkdown.md)

### 前置条件

- 安装Go 1.18或更高版本
- 安装库：`go get github.com/gomarkdown/markdown`
- 对于CLI工具：`go install github.com/gomarkdown/mdtohtml@latest`

### 快速转换方法

#### 方法1：简单转换（Go）

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

#### 方法2：CLI工具

```bash
# 安装mdtohtml
go install github.com/gomarkdown/mdtohtml@latest

# 转换文件
mdtohtml input.md output.html

# 转换文件（输出到stdout）
mdtohtml input.md
```

#### 方法3：自定义解析器和渲染器

```go
package main

import (
    "github.com/gomarkdown/markdown"
    "github.com/gomarkdown/markdown/html"
    "github.com/gomarkdown/markdown/parser"
)

func mdToHTML(md []byte) []byte {
    // 使用扩展创建解析器
    extensions := parser.CommonExtensions | parser.AutoHeadingIDs | parser.NoEmptyLineBeforeBlock
    p := parser.NewWithExtensions(extensions)
    doc := p.Parse(md)

    // 使用扩展创建HTML渲染器
    htmlFlags := html.CommonFlags | html.HrefTargetBlank
    opts := html.RendererOptions{Flags: htmlFlags}
    renderer := html.NewRenderer(opts)

    return markdown.Render(doc, renderer)
}
```

### CLI配置

`mdtohtml` CLI工具具有最少选项：

```bash
mdtohtml input-file [output-file]
```

对于高级配置，使用Go库程序化地使用解析器和渲染器选项：

| 解析器扩展 | 描述 |
|------------|------|
| `parser.CommonExtensions` | 表格、代码块、自动链接、删除线、等 |
| `parser.AutoHeadingIDs` | 为标题生成ID |
| `parser.NoEmptyLineBeforeBlock` | 块前不需要空行 |
| `parser.MathJax` | LaTeX数学的MathJax支持 |

| HTML标志 | 描述 |
|-----------|------|
| `html.CommonFlags` | 常用的HTML输出标志 |
| `html.HrefTargetBlank` | 为链接添加`target="_blank"` |
| `html.CompletePage` | 生成完整的HTML页面 |
| `html.UseXHTML` | 生成XHTML输出 |

### 安全警告

⚠️ **gomarkdown不会清理输出HTML。** 对于不可信的输入，使用Bluemonday：

```go
import (
    "github.com/microcosm-cc/bluemonday"
    "github.com/gomarkdown/markdown"
)

maybeUnsafeHTML := markdown.ToHTML(md, nil, nil)
html := bluemonday.UGCPolicy().SanitizeBytes(maybeUnsafeHTML)
```

推荐清理器：[Bluemonday](https://github.com/microcosm-cc/bluemonday)

### 支持的Markdown风味

| 风味 | 支持 |
|------|------|
| 原始Markdown | 100% |
| CommonMark | 高（使用扩展） |
| GitHub Flavored Markdown | 高（表格、代码块、删除线） |
| MathJax/LaTeX数学 | 通过扩展支持 |
| Mmark | 支持 |

### 故障排除

| 问题 | 解决方案 |
|------|------|
| Windows/Mac新行未解析 | 使用`parser.NormalizeNewlines(input)` |
| 表格不渲染 | 启用`parser.Tables`扩展 |
| 代码块无高亮 | 集成语法高亮器如Chroma |
| 数学不渲染 | 启用`parser.MathJax`扩展 |
| XSS漏洞 | 使用Bluemonday清理输出 |

## 使用[`jekyll`](references/jekyll.md)

### 前置条件

- Ruby版本2.7.0或更高
- RubyGems
- GCC和Make（用于本地扩展）
- 安装Jekyll和Bundler：`gem install jekyll bundler`

### 快速转换方法

#### 方法1：创建新站点

```bash
# 创建一个新的Jekyll站点
jekyll new myblog

# 切换到站点目录
cd myblog

# 本地构建和提供服务
bundle exec jekyll serve

# 访问http://localhost:4000
```

#### 方法2：构建静态站点

```bash
# 构建站点到_site目录
bundle exec jekyll build

# 使用生产环境构建
JEKYLL_ENV=production bundle exec jekyll build
```

#### 方法3：实时重新加载开发

```bash
# 使用实时重新加载提供服务
bundle exec jekyll serve --livereload

# 提供草稿
bundle exec jekyll serve --drafts
```

### CLI配置

| 命令 | 描述 |
|------|------|
| `jekyll new <path>` | 创建新的Jekyll站点 |
| `jekyll build` | 构建站点到 `_site` 目录 |
| `jekyll serve` | 本地构建和提供服务 |
| `jekyll clean` | 删除生成的文件 |
| `jekyll doctor` | 检查配置问题 |

| 服务选项 | 描述 |
|---------------|------|
| `--livereload` | 修改时重新加载浏览器 |
| `--drafts` | 包含草稿帖子 |
| `--port <port>` | 设置服务器端口（默认：4000） |
| `--host <host>` | 设置服务器主机（默认：localhost） |
| `--baseurl <url>` | 设置基本URL |

### 安全警告

⚠️ **Jekyll安全注意事项：**

- 避免在生产环境中使用`safe: false`
- 使用`exclude`在`_config.yml`中防止敏感文件被发布
- 如果接受外部输入，清理用户生成的内容
- 保持Jekyll和插件更新

```yaml
# _config.yml安全设置
exclude:
  - Gemfile
  - Gemfile.lock
  - node_modules
  - vendor
```

### 支持的Markdown风味

| 风味 | 支持 |
|------|------|
| Kramdown（默认） | 100% |
| CommonMark | 通过插件（jekyll-commonmark） |
| GitHub Flavored Markdown | 通过插件（jekyll-commonmark-ghpages） |
| RedCarpet | 通过插件（已弃用） |

在`_config.yml`中配置markdown处理器：

```yaml
markdown: kramdown
kramdown:
  input: GFM
  syntax_highlighter: rouge
```

### 故障排除

| 问题 | 解决方案 |
|------|------|
| Ruby 3.0+无法服务 | 运行`bundle add webrick` |
| Gem依赖错误 | 运行`bundle install` |
| 构建缓慢 | 使用`--incremental`标志 |
| Liquid语法错误 | 检查内容中的未转义的`{` |
| 插件未加载 | 添加到`_config.yml`插件列表 |

## 使用[`hugo`](references/hugo.md)

### 前置条件

- 安装Hugo（从<https://gohugo.io/installation/>下载）
- Git（推荐用于主题和模块）
- Go（可选，用于Hugo模块）

### 快速转换方法

#### 方法1：创建新站点

```bash
# 创建一个新的Hugo站点
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

#### 方法2：构建静态站点

```bash
# 构建站点到public目录
hugo

# 构建带压缩的
hugo --minify

# 构建特定环境的
hugo --environment production
```

#### 方法3：开发服务器

```bash
# 启动服务器带草稿
hugo server -D

# 启动带实时重新加载并绑定到所有接口
hugo server --bind 0.0.0.0 --baseURL http://localhost:1313/

# 启动特定端口
hugo server --port 8080
```

### CLI配置

| 命令 | 描述 |
|------|------|
| `hugo new site <name>` | 创建新的Hugo站点 |
| `hugo new content <path>` | 创建新内容文件 |
| `hugo` | 构建站点到`public`目录 |
| `hugo server` | 启动开发服务器 |
| `hugo mod init` | 初始化Hugo模块 |

| 构建选项 | 描述 |
|---------------|------|
| `-D, --buildDrafts` | 包含草稿内容 |
| `-E, --buildExpired` | 包含过期内容 |
| `-F, --buildFuture` | 包含预定义内容 |
| `--minify` | 压缩输出 |
| `--gc` | 构建后运行垃圾回收 |
| `-d, --destination <path>` | 输出目录 |

| 服务器选项 | 描述 |
|----------------|------|
| `--bind <ip>` | 绑定接口 |
| `-p, --port <port>` | 端口号（默认：1313） |
| `--liveReloadPort <port>` | 实时重新加载端口 |
| `--disableLiveReload` | 禁用实时重新加载 |
| `--navigateToChanged` | 导航到更改的内容 |

### 安全警告

⚠️ **Hugo安全注意事项：**

- 在`hugo.toml`中配置安全策略以用于外部命令
- 小心使用`--enableGitInfo`与公共仓库
- 验证用户生成内容的短码参数

```toml
# hugo.toml安全设置
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

### 支持的Markdown风味

| 风味 | 支持 |
|------|------|
| Goldmark（默认） | 100% (CommonMark兼容) |
| GitHub Flavored Markdown | 完整（表格、删除线、自动链接） |
| CommonMark | 100% |
| Blackfriday（遗留） | 已弃用，不推荐 |

在`hugo.toml`中配置markdown：

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
      unsafe = false  # 设置为true允许原始HTML
```

### 故障排除

| 问题 | 解决方案 |
|------|------|
| 路径上的"页面未找到" | 检查`baseURL`在配置中 |
| 主题未加载 | 验证主题在`themes/`或Hugo模块 |
| 构建缓慢 | 使用`--templateMetrics`识别瓶颈 |
| 原始HTML未渲染 | 在goldmark配置中设置`unsafe = true` |
| 图片无法加载 | 检查`static/`文件夹结构 |
| 模块错误 | 运行`hugo mod tidy` |

## 参考

### Markdown编写和样式

- [basic-markdown.md](references/basic-markdown.md)
- [code-blocks.md](references/code-blocks.md)
- [collapsed-sections.md](references/collapsed-sections.md)
- [tables.md](references/tables.md)
- [writing-mathematical-expressions.md](references/writing-mathematical-expressions.md)
- Markdown指南：<https://www.markdownguide.org/basic-syntax/>
- Markdown样式：<https://github.com/sindresorhus/github-markdown-css>

### [`markedJS/marked`](references/marked.md)

- 官方文档：<https://marked.js.org/>
- 高级选项：<https://marked.js.org/using_advanced>
- 扩展性：<https://marked.js.org/using_pro>
- GitHub仓库：<https://github.com/markedjs/marked>

### [`pandoc`](references/pandoc.md)

- 入门指南：<https://pandoc.org/getting-started.html>
- 官方文档：<https://pandoc.org/MANUAL.html>
- 扩展性：<https://pandoc.org/extras.html>
- GitHub仓库：<https://github.com/jgm/pandoc>

### [`gomarkdown/markdown`](references/gomarkdown.md)

- 官方文档：<https://pkg.go.dev/github.com/gomarkdown/markdown>
- 高级配置：<https://pkg.go.dev/github.com/gomarkdown/markdown@v0.0.0-20250810172220-2e2c11897d1a/html>
- Markdown处理：<https://blog.kowalczyk.info/article/cxn3/advanced-markdown-processing-in-go.html>
- GitHub仓库：<https://github.com/gomarkdown/markdown>

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
- GitHub仓库：<https://github.com/jekyll/jekyll>

### [`hugo`](references/hugo.md)

- 官方文档：<https://gohugo.io/documentation/>
- 所有设置：<https://gohugo.io/configuration/all/>
- 编辑器插件：<https://gohugo.io/tools/editors/>
- GitHub仓库：<https://github.com/gohugoio/hugo>
