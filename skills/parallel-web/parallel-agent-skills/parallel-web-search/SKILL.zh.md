---
name: parallel-web-search
description: 基于CLI的网页搜索。当用户明确调用此技能、需要仅CLI控制的选项或保存JSON输出，或没有可用的Parallel web_search MCP工具时使用。当捆绑的Parallel Search MCP可用时，优先使用其web_search工具进行常规查找和当前信息查询。只有当用户明确要求深度或详尽研究时，才使用parallel-deep-research。
---

# 网络搜索

对以下内容进行网络搜索：$ARGUMENTS

## 命令

根据查询选择一个简短、描述性的文件名（例如，`ai-chip-news`、`react-vs-vue`）。使用小写字母和连字符，不要有空格。将其替换到命令**内联**中——`$FILENAME`和`<keyword>`以下是占位符，不是shell变量；不要原封不动地复制它们。

```bash
parallel-cli search "$ARGUMENTS" -q "<keyword1>" -q "<keyword2>" --json --max-results 10 --excerpt-max-chars-total 27000 -o "/tmp/$FILENAME.json"
```

关于React 19查询的具体示例：

```bash
parallel-cli search "latest React 19 features and adoption" -q "React 19" -q "concurrent rendering" --json --max-results 10 --excerpt-max-chars-total 27000 -o "/tmp/react-19-features.json"
```

第一个参数是**目标**——你正在寻找内容的自然语言描述。它用单个调用替代了多个关键词搜索，适用于广泛或复杂的查询。添加`-q`标志以补充特定关键词查询。`-o`标志将完整结果保存为JSON文件，以便后续提问。

如果需要，可以使用以下选项：

- `--after-date YYYY-MM-DD` 用于时间敏感的查询
- `--include-domains domain1.com,domain2.com` 限制到特定来源
- `--exclude-domains domain.com` 过滤掉嘈杂的来源
- `--mode turbo` 用于简单事实查找，速度最重要；支持英语和日语查询
- `--mode fast` 用于高质搜索，在约一秒的延迟预算内；要求CLI ≥ 0.9.2，延迟不保证
- `--mode advanced` 用于较难的问题（多步骤、代理式搜索）。除非请求需要其他模式，否则保持默认`basic`
- `--location us` (ISO 3166-1 alpha-2) 用于地理定位结果
- `--session-id "<returned-session-id>"` 当先前的响应返回一个时，用于将相关的Search/Extract调用分组。`session_id`或`search_id`不是Task交互ID或研究运行ID；永远不要将其发送到研究状态/poll或`--previous-interaction-id`

## 解析结果

**将保存的`-o` JSON文件作为权威数据。** 结果和摘要限制约束请求的内容，但stdout仍可能超过工具的输出限制。截断的stdout不是可解析的JSON，也不是保存结果不完整的证明。在使用之前检查现有输出路径，因为Search会覆盖该文件。对于每个结果，提取：

- 如果提供，则提取标题、url和发布日期；省略未知日期
- 从摘要中提取有用内容（跳过导航噪音，如菜单、页脚、"跳到内容"）

检查退出状态、返回的API错误和`warnings`，然后再呈现结果。在错误或空`results`的情况下，报告发生了什么，不要编造答案。旧的输出文件不是请求失败成功的证据。对于稀疏结果，说明覆盖限制；只有当对用户请求有用时，才改进目标或查询。

## 响应格式

**关键：每个声明都必须有内联引用。** 使用Markdown链接如[标题](URL)，仅从JSON输出中提取。永远不要编造或猜测URL。

综合一个响应，要求：

- 以关键答案/发现开头
- 包括具体事实、名称、数字、日期
- 每个事实都内联引用为[来源标题](url)——不要留下任何未引用的声明
- 如果有多个主题，按主题组织

**以来源部分结束**，列出所有引用的URL：

```text
来源：
- [来源标题](https://example.com/article) (2026年2月)
- [另一个来源](https://example.com/other) (2026年1月)
```

这个来源部分是强制性的。不要省略它。

仅包括在检索内容中返回或验证的日期。当未知时，省略日期。

在来源部分之后，提及输出文件路径（`/tmp/$FILENAME.json`），以便用户知道它可用于后续提问。

## 配置

如果找不到`parallel-cli`，则安装并认证：

```bash
/parallel:parallel-cli-setup
```

如果缺少文档中记录的命令或选项，请检查安装版本并通过其安装方法升级：独立的`parallel-cli update`、pipx的`pipx upgrade parallel-web-tools`、uv的`uv tool upgrade parallel-web-tools`、Homebrew的`brew upgrade parallel-web/tap/parallel-cli`或npm的`npm update -g parallel-web-cli`。在相同的终端中验证帮助信息，然后再重试。

对于认证错误，检查`parallel-cli auth --json`及其`authenticated`布尔值；仅退出零不能证明认证。`403`可能表示权限、策略或计费问题。报告实际错误；仅针对计费特定失败检查余额，并且永远不要在未经明确确认的情况下添加资金。
