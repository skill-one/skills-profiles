# URL 提取

从 $ARGUMENTS 中提取内容

## 命令

根据 URL 或内容选择一个简短、描述性的文件名（例如，`vespa-docs`，`react-hooks-api`）。使用小写字母和连字符，不要有空格。将其直接替换到命令中——`$FILENAME` 是一个占位符，而不是 shell 变量。

```bash
parallel-cli extract "$ARGUMENTS" --json -o "/tmp/$FILENAME.json"
```

具体示例：

```bash
parallel-cli extract "https://docs.parallel.ai" --json -o "/tmp/parallel-docs.json"
```

注意：`-o` 总是保存 JSON 格式。扩展名必须是 `.json`。

如果需要，可以使用以下选项：

- `--objective "关注区域"` 将提取内容集中在特定目标上（同时会静默 V1 在未设置 neither objective 也没有 search_queries 时发出的警告）
- `-q "关键词"`（可重复）在摘录中优先考虑关键词
- `--full-content` 包含完整页面正文（对于长文章、PDF 或摘录可能无法捕获所需内容时）
- `--full-content-max-chars N` 限制每个结果的全内容大小
- `--no-excerpts` 当你只需要完整内容时移除摘录

## 处理提取失败的情况

如果响应中包含 `errors` 字段、空的 `results` 数组，或 URL 返回 404/超时，不要编造内容。告诉用户提取失败，显示上游状态，并建议：

- 验证 URL（页面可能已移动）
- 如果摘录为空但页面存在，使用 `--full-content` 重新尝试
- 如果页面已重命名，使用 `parallel-cli search` 定位当前 URL

## 响应格式

以以下格式返回内容：

**[页面标题](URL)**

然后直接返回提取的内容，并遵循以下规则：

- 保持内容原样 - 不要释义或总结
- 彻底解析列表 - 提取所有编号/项目符号项
- 仅移除明显的噪音：导航菜单、页脚、广告
- 保留所有事实、名称、数字、日期、引言

响应后，提及输出文件路径（`/tmp/$FILENAME.json`），以便用户知道它可用于后续问题。

## 设置

如果找不到 `parallel-cli`，请安装并认证：

```bash
/parallel:parallel-cli-setup
```

如果 `parallel-cli extract` 返回 `403`，告诉用户可能需要余额。提供运行 `parallel-cli balance get` 的选项，如果需要，在运行 `parallel-cli balance add <amount_cents>` 前请求明确的确认。然后重试原始提取命令。
