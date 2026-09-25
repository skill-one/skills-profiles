# 网络搜索

对以下内容进行网络搜索：$ARGUMENTS

## 命令

根据查询选择一个简短、描述性的文件名（例如，`ai-chip-news`、`react-vs-vue`）。使用小写字母和连字符，不要有空格。将其直接替换到命令中——`$FILENAME`和`<keyword>`以下是占位符，不是shell变量；不要原封不动地复制它们。

```bash
parallel-cli search "$ARGUMENTS" -q "<keyword1>" -q "<keyword2>" --json --max-results 10 --excerpt-max-chars-total 27000 -o "/tmp/$FILENAME.json"
```

关于React 19查询的具体示例：

```bash
parallel-cli search "React 19最新特性及应用" -q "React 19" -q "并发渲染" --json --max-results 10 --excerpt-max-chars-total 27000 -o "/tmp/react-19-features.json"
```

第一个参数是**目标**——你正在寻找内容的自然语言描述。它用单个调用替代了多个关键词搜索，适用于广泛或复杂的查询。添加`-q`标志以补充具体的关键词查询。`-o`标志将完整结果保存为JSON文件，以便后续提问。

如果需要，可以使用以下选项：

- `--after-date YYYY-MM-DD` 用于时间敏感的查询
- `--include-domains domain1.com,domain2.com` 限制到特定来源
- `--exclude-domains domain.com` 过滤掉嘈杂的来源
- `--mode turbo` 用于简单的事实查找，速度和成本最重要（p50约200ms，最低成本）。仅支持英语和日语查询
- `--mode fast` 用于在~1秒延迟预算内进行高质量搜索
- `--mode advanced` 用于更难的查询（多步骤、智能搜索）。默认`basic`适用于几乎所有情况；只有当基本结果不足时才升级到`advanced`，对于高量的简单查找可降级到`turbo`
- `--location us` (ISO 3166-1 alpha-2) 用于地理定位结果

## 解析结果

在命令执行时不要设置`max_output_tokens`——输出已经被`--max-results`和`--excerpt-max-chars-total`限制。限制输出token会截断JSON并破坏解析。

**优先从保存的`-o`文件中读取**，而不是stdout。即使输出被限制，也经常超过stdout限制并被截断。读取`/tmp/$FILENAME.json`以获取权威数据。对于每个结果，提取：

- 标题、URL、发布日期
- 从摘录中提取有用内容（跳过导航噪音，如菜单、页脚、"跳到内容"）

## 响应格式

**关键：每个声明都必须有内联引用。** 使用markdown链接如[标题](URL)，仅从JSON输出中提取。不要编造或猜测URL。

综合一个响应，要求：

- 以关键答案/发现开头
- 包括具体事实、名称、数字、日期
- 每个事实都内联引用为[来源标题](url)——不要遗漏任何未引用的声明
- 如果有多个主题，按主题组织

**最后必须有一个“来源”部分**，列出所有引用的URL：

```text
来源：
- [来源标题](https://example.com/article) (2026年2月)
- [另一个来源](https://example.com/other) (2026年1月)
```

这个来源部分是强制性的。不要遗漏它。

在来源部分之后，提及输出文件路径（`/tmp/$FILENAME.json`），以便用户知道它可用于后续提问。

## 配置

如果找不到`parallel-cli`，请安装并认证：

```bash
/parallel:parallel-cli-setup
```

如果`parallel-cli search`返回`403`，告诉用户可能需要余额。提供运行`parallel-cli balance get`的选项，如果需要，在运行`parallel-cli balance add <amount_cents>`之前请求明确确认。然后重试原始搜索命令。
