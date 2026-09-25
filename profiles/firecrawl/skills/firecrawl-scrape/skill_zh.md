# firecrawl scrape

读取页面内容的 URL，或执行选定的提供工具以获取结构化数据。使用 `search` 发现工具，并在执行前使用 `list` 检查其输入。多个 URL 可以同时抓取。

对于结构化数据集，首先使用 [search 技能](../firecrawl-search/SKILL.md) 检查合适的流程或数据提供工具。直接读取已知页面；重用选定的合约，而不是重复发现。

## 快速入门

```bash
# 基本 Markdown 提取
firecrawl scrape "<url>" -o .firecrawl/page.md

# 仅主内容，不包括导航/页脚
firecrawl scrape "<url>" --only-main-content -o .firecrawl/page.md

# 等待 JS 渲染后抓取
firecrawl scrape "<url>" --wait-for 3000 -o .firecrawl/page.md

# 多个 URL（仅 Markdown；每个保存到 .firecrawl/；-o 被忽略）
firecrawl scrape https://example.com https://example.com/blog https://example.com/docs

# 获取 Markdown 和链接
firecrawl scrape "<url>" --format markdown,links -o .firecrawl/page.json

# 关于页面的提问
firecrawl scrape "https://example.com/pricing" --query "企业版的价格是多少？"
```

运行 `firecrawl scrape --help` 获取完整选项列表。

**完成时：** 页面内容或提供工具结果已检查错误，并在有限部分中检查以回答请求。保留源链接并披露部分结果。

## 查找工具、检查输入并获取帮助

使用 CLI 帮助检查支持的选项，而不是猜测：

```bash
firecrawl search --help
firecrawl list --help
firecrawl scrape --help
```

使用 `--domain-tools` 进行域发现默认返回工具摘要。添加 `--tool-detail full` 以提前获取合约，或像下面所示使用 `list` 检查选定的工具。使用 `--tool-detail compact` 仅获取提供者、能力和描述；使用 `list` 通过这两个 ID 检查。摘要保持默认。当需要立即使用多个相关合约时，优先使用完整模式。

对于结构化数据，搜索任务，检查匹配工具的合约，然后使用其声明的确切输入字段执行：

```bash
# Web + 域匹配 + 语义工具
firecrawl search '<用户问题>'

# 仅语义工具
firecrawl search alexandria '<用户问题>'

# 分类 → 提供者 → 工具 → 合约
firecrawl list
firecrawl list <分类 ID> --category
firecrawl list <提供者 ID>
firecrawl list <提供者 ID> <能力 ID> --pretty

# 执行工具
firecrawl scrape <提供者 ID>/<能力 ID> --options '<与选定合约匹配的 JSON>'
```

正常搜索包括网络结果和工具匹配；`search alexandria` 仅搜索工具。`list <提供者> <能力> --pretty` 显示选定的合约；使用 `--json` 获取机器可读输出。要逐步浏览，使用 `list`，然后 `list <分类> --category`，然后 `list <提供者>`。搜索和列表不会执行选定的提供工具。仅读取任务所需的合约；使用返回的标识符，而不是猜测。

在构建输入或解析结果之前，读取扩展的合约：

- `required: true` 表示必须输入该字段；每个 `requiresOneOf` 组至少需要一个成员，而不是所有成员。
- 选定合约检查已请求示例。当存在时，读取单一的 `example.request` 和 `example.response`；对于具有可选输入的工具，空请求可能有效。
- `response.key` 标识 `data.alexandria[i].data` 内的记录字段；空键表示数据对象本身。不要假设每个提供者都返回 `records`。
- 提供者分页与目录 `next` 不同：使用合约的延续输入和返回的页面/游标，保留过滤器，并在其耗尽信号处停止。仅 `paginated: true` 并不指定映射。

## 执行和大型结果

URL 抓取不会自动执行提供工具。使用确切的发现输入字段，并使用查找工具解析记录 ID，而不是凭空编造。检查每个 `data.alexandria[]` 结果是否存在错误，而不仅仅是外部的成功标志。

如果客户端报告输出/上下文限制，上游请求可能已成功。保留请求或抓取 ID，并在重复提供调用之前恢复保留的结果。对于大型数据集和 PDF，当本地文件系统可用时，使用 `--json -o` 保存输出，并使用 `jq` 或其他文件工具检查有限部分。将 stderr 与 JSON stdout 分开；在将流管道到 JSON 解析器时，不要使用 `2>&1` 合并流。在远程处理更可取的情况下，使用 `firecrawl scrape firecrawl/bash` 从保留结果中选择。阅读 [large-result recovery](references/large-results.md) 获取 ID、命令示例、过期和错误。这是显式恢复，而不是自动溢出检测。

## PDF 和页面预算

PDF 每解析一页消耗 1 个信用。使用 `--max-pages`（一个从 1 到 10000 的整数）限制 PDF 解析，特别是对于大型或未知文档：

```bash
firecrawl scrape "https://example.com/report.pdf" --max-pages 5 --json -o .firecrawl/report.json
```

上限适用于每个 PDF，而不是整个命令或总信用。额外的格式和选项可能增加费用。CLI 在执行前不会引用页数或费用。使用 JSON 输出检查返回的 `metadata.numPages`（解析页数）、`metadata.totalPages`（文档总页数）和 `metadata.creditsUsed`（当存在时）；较小的解析计数表示结果是部分的。

## 小贴士

- **优先使用普通抓取而不是 `--query`。** 抓取到文件，然后使用 `grep`、`head` 或直接读取 Markdown —— 你可以自己搜索和推理完整内容。仅在需要单个目标答案且不保存页面时使用 `--query`（费用增加 5 个信用）。
- **抓取处理静态页面和 JS 渲染的 SPA。** 当页面需要交互（点击、表单填写、分页）或抓取遗漏内容时，升级到 `interact`。
- 多个 URL 同时抓取 —— 检查 `firecrawl --status` 获取你的并发限制。此模式仅保存 Markdown 并忽略 `-o`；其他请求的格式被丢弃。如果未请求 Markdown，整个 JSON 响应写入 `.md` 文件。
- 单个格式输出原始内容。多个格式（例如 `--format markdown,links`）输出 JSON。
- 始终引用 URL —— shell 将 `?` 和 `&` 解释为特殊字符。
- 命名约定：`.firecrawl/{site}-{路径}.md`

## 参见

- [firecrawl-search](../firecrawl-search/SKILL.md) — 当你没有 URL 时查找页面
- [firecrawl-interact](../firecrawl-interact/SKILL.md) — 当抓取无法获取内容时，使用 `interact` 点击、填写表单等
- [firecrawl-download](../firecrawl-download/SKILL.md) — 批量下载整个网站到本地文件
- [firecrawl-build-scrape](https://github.com/firecrawl/skills/tree/main/skills/build/firecrawl-build-scrape) — 将抓取构建到应用程序中而不是在此处运行
