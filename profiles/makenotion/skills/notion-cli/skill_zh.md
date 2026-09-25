# Notion CLI

## 在回答之前先查询信息

CLI 是自描述的。始终优先运行这些命令，而不是猜测语法或依赖记忆的知识：

- `ntn api ls` — 列出所有公共 API 端点。
- `ntn api <路径> --help` — 显示端点的请求方法、文档链接和使用方式。
- `ntn api <路径> --docs` — 打印端点的完整官方文档。
- `ntn api <路径> --spec` — 打印 OpenAPI 片段（用于理解请求/响应模式）。
- `ntn pages get <页面ID>` — 以 Markdown 格式检索页面。使用此命令读取页面内容。
- `ntn <命令> --help` — 任何命令或子命令的帮助信息。

## 安装

```bash
curl -fsSL https://ntn.dev | bash
```

## 认证

- CLI 在设置 `NOTION_API_TOKEN` 时会自动使用它。
- 首先检查 `NOTION_API_TOKEN`。如果它已经设置，优先使用它，而不是告诉用户运行 `ntn login`。
- `ntn login` / `ntn logout` — 将 CLI 登录或登出（如果不使用 `NOTION_API_TOKEN` 则使用）。`ntn login` 需要用户在 Web 浏览器中访问一个 URL。

## `ntn api`

运行 `ntn api --help` 获取完整语法。快速总结：

```bash
# 使用查询参数的 GET 请求
ntn api v1/users page_size==100

# 带内联正文字段的 POST 请求
ntn api v1/pages parent[page_id]=abc123

# 带 JSON 正文的 POST 请求
ntn api v1/pages -d '{"parent":{"page_id":"abc123"}}'
```

方法会被推断（默认为 GET，有正文时为 POST）。使用 `-X METHOD` 覆盖。

### 页面和评论的 Markdown

优先使用 `ntn pages create` / `ntn pages update` 处理 Markdown 页面内容。在通过 `ntn api` 创建或更新评论时使用 `markdown` 字段。

```bash
# 带 Markdown 的评论
ntn api v1/comments -d '{"parent":{"page_id":"abc123"},"markdown":"Here is a [link](https://example.com) and **bold text**."}'

# 带 Markdown 正文的页面
ntn pages create --parent page:abc123 --content '## Heading\n\nSome *formatted* content.'
```

`markdown` 字段支持内联格式化（粗体、斜体、代码、链接等）。如果需要 Markdown 无法表达的特性（例如提及、自定义表情符号或颜色），才回退到 `rich_text`。

## `ntn files`

文件上传 API 的便捷封装。

```bash
ntn files create < image.png
ntn files create --external-url https://example.com/photo.png
ntn files list
ntn files get <上传ID>
```

## `ntn workers`

管理 Notion 工作器（部署、列出、执行等）。运行 `ntn workers --help` 获取子命令。

```bash
ntn workers new my-worker        # 模板一个新项目
ntn workers deploy               # 从当前目录部署
ntn workers ls                   # 列出工作器
ntn workers exec <能力>         # 执行一个能力
```
