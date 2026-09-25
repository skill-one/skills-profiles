# Knap

使用 Knap CLI 通过变量、过滤器和逻辑渲染 Markdown 模板。

若未安装：`npm install -g knap`（需要 Node.js 20 或更高版本）。或者使用 `npx knap`。

运行 `knap --help` 获取可用命令和选项。通过 CLI 的离线参考发现语言：

```bash
knap help syntax
knap help filters
knap help filter date
knap help tags
knap help tag for
```

使用列表查找名称，然后通过语法、参数和预期输出的示例请求单个帮助。

## 使用方法

使用 JSON 变量渲染模板：

```bash
knap render template.md --data article.json -o note.md
```

内联提供模板和数据：

```bash
knap render -t '# {{ title | trim }}' --data-json '{"title":"Hello"}'
```

覆盖变量或管道 JSON 数据：

```bash
knap render template.md --data article.json --set 'title=Custom title'
cat article.json | knap render template.md --data -
```

数据必须是一个 JSON 对象；其属性成为模板变量。`--set` 覆盖顶层键的字符串。使用 JSON 表示嵌套对象、数组、数字和布尔值。

选择一个模板源（文件、`-t` 或 stdin）和一个数据源（`--data` 或 `--data-json`）。只能有一个输入读取 stdin。如果没有模板文件或 `-t`，Knap 从 stdin 读取模板。

输出默认为 stdout。`-o` 创建父目录并在渲染成功后覆盖目标。错误退出状态为 `1`；诊断信息输出到 stderr。成功输出可以附带警告。

## 模板

使用 `{{ variable }}` 表示值，`|` 表示过滤器，`{% ... %}` 表示逻辑。例如，将以下内容保存为 `template.md`：

```knap
---
{{ title | yaml_property:"title" }}
{{ tags | yaml_property:"tags" }}
---
# {{ title | trim }}
{% if author %}
By {{ author }}
{% endif %}

{{ content }}
```

使用 `yaml_property` 获取完整的 frontmatter 属性，以便值被正确地引号和缩进。CLI 包含标准过滤器，但不提供 Web Clipper 浏览器变量、选择器、提示或依赖于 DOM 的 HTML 过滤器。通过 JSON 提供变量。

在渲染前检查模板：

```bash
knap validate template.md
```

验证检查语法、过滤器名称和静态过滤器参数，无需数据或文件输出。它不检查变量是否存在、运行时值或动态参数；使用实际数据渲染以检查运行时行为。诊断信息输出到 stderr，并包含相关的帮助命令。

## Defuddle 管道

将网页提取为 JSON，包含 Markdown 内容，然后渲染为笔记：

```bash
defuddle parse https://example.com/article --md --json \
  | knap render template.md --data - -o note.md
```

Defuddle 的 JSON 属性，如 `title` 和 `content`，直接成为模板变量。

## 批量渲染

为 CSV 行、JSON 数组对象或文件夹中的 JSON 文件创建一个文件：

```bash
knap batch template.md --data articles.csv --output-dir notes \
  --filename '{{ title | safe_name }}.md'
```

使用 `--data articles.json` 表示数组或 `--data ./articles` 表示 JSON 对象的文件夹。CSV 标头成为变量名，值保持为字符串。管道数据默认为 JSON；添加 `--format csv` 表示管道 CSV。

使用 `--dry-run` 验证并列出输出路径而不写入文件。现有文件需要 `--overwrite`，包括在干运行期间。批量中重复的输出名称即使使用 `--overwrite` 也是错误。

文件名模板必须生成一个带扩展名的单个文件名，不包含目录。使用 `safe_name` 表示数据派生的名称。没有 `--filename`，Knap 保留源 JSON 基名或为 CSV 行和数组项编号为 `1.md`、`2.md` 等。
