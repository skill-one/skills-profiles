---
name: parallel-web-extract
description: 基于CLI的URL提取。当用户明确调用此技能、需要仅CLI控制的选项或保存JSON输出，或没有可用的Parallel web_fetch MCP工具时使用。当捆绑的Parallel Search MCP可用时，优先使用其web_fetch工具处理普通网页、文章、PDF文件和JavaScript密集型网站。
---

# URL 提取

从：$ARGUMENTS 中提取内容

## 命令

根据 URL 或内容选择一个简短、描述性的文件名（例如，`vespa-docs`、`react-hooks-api`）。使用小写字母和连字符，不要有空格。将文件名直接替换到命令中——`$FILENAME` 是一个占位符，不是 shell 变量。

将每个请求的 URL 作为单独的带引号的参数传递，每次调用最多 20 个。不要将多个 URL 压缩成一个带引号的 `$ARGUMENTS` 字符串，也不要使用 `eval` 来分割它们。直接从请求的 URL 构造参数。例如：

```bash
parallel-cli extract "https://docs.parallel.ai/integrations/cli" "https://docs.parallel.ai/integrations/cursor-marketplace" --json -o "/tmp/parallel-docs.json"
```

`-o` 用于保存 JSON。使用 `.json` 扩展名，并在使用前检查现有路径，因为 Extract 会覆盖它。将保存的文件视为权威文件；stdout 可能会被截断，仅显示部分内容。在调用失败后，不要将过时的文件视为成功响应。

如果需要，可以使用以下选项：

- `--objective "focus area"` 用于将提取重点放在特定目标上（同时会静默 V1 在未设置两者时发出的“既无目标也无 search_queries”的警告）
- `-q "keyword"`（可重复）用于在摘录中优先考虑关键词
- `--full-content` 用于包含完整页面正文（对于长文章、PDF 或摘录可能无法捕获所需内容时）
- `--full-content-max-chars N` 用于限制每个结果的全内容大小
- `--no-excerpts` 用于在只需要完整内容时移除摘录
- `--session-id "<返回的 session-id>"` 用于将相关的 Search/Extract 调用分组。session ID 不是 Task 交互 ID 或运行 ID；永远不要将其与 research status/poll 或 `--previous-interaction-id` 一起使用

## 处理失败的提取

检查退出状态、API 错误、`results`、每个 URL 的 `errors` 以及任何警告。`errors: []` 是正常成功。非空的错误可以与成功的结果共存：保留并呈现成功的内容，然后为每个失败的 URL 及其返回原因命名。空结果或缺失内容不是成功的提取。不要编造内容。对于受影响的 URL，建议：

- 验证 URL（页面可能已移动）
- 如果摘录为空但返回的元数据支持页面已被获取，请求 `--full-content`
- 如果页面已重命名，使用 `parallel-cli search` 定位当前 URL

## 响应格式

以以下格式返回内容：

**[页面标题](URL)**

对于全页面请求，使用返回的 `full_content`；仅摘录是选定的段落，必须标明这一点。即使全内容也可能因 `--full-content-max-chars` 或上游限制而被截断；在截断时不要承诺完整性。保留检索的内容，并遵守以下规则：

- 保持内容原样——不要释义或总结
- 保留检索内容中的所有编号/项目符号项；不要声称摘录包含整个页面
- 仅移除明显的噪音：导航菜单、页脚、广告
- 保留所有事实、名称、数字、日期、引言

在响应后，提及输出文件路径（`/tmp/$FILENAME.json`），以便用户知道它可用于后续问题。

对于大内容，将完整的原样文本保存在保存的文件中，并提供一个简短的带标签的预览及其路径。在声称提取完整时，永远不要在后台截断内容。

## 设置

如果找不到 `parallel-cli`，请安装并认证：

```bash
/parallel:parallel-cli-setup
```

如果缺少文档中记录的命令或选项，请检查安装版本并通过其安装方法升级：独立的 `parallel-cli update`、pipx `pipx upgrade parallel-web-tools`、uv `uv tool upgrade parallel-web-tools`、Homebrew `brew upgrade parallel-web/tap/parallel-cli` 或 npm `npm update -g parallel-web-cli`。在重试前，在同一终端中验证帮助信息。

对于认证错误，检查 `parallel-cli auth --json` 及其 `authenticated` 布尔值；仅退出状态为零并不能证明认证成功。`403` 可能表示权限、策略或计费问题。报告实际错误；仅针对计费特定失败检查余额，并且永远不要在未经明确确认的情况下添加资金。
