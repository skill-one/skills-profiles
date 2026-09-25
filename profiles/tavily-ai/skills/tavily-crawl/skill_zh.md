# tavily crawl

爬取网站并从多个页面中提取内容。支持将每个页面保存为本地 Markdown 文件。

## 运行前准备

爬取需要认证。当 `tvly` 已完成认证时，直接运行请求的命令；不要在每个调用中添加状态检查。

如果 `tvly` 未安装，请按照 [tavily-cli setup](../tavily-cli/SKILL.md#setup) 中的说明进行设置。
如果已安装的 CLI 报告认证错误，请使用 `tvly login` 仅进行认证，或使用 `tvly init --skip-skills` 当引导验证也很有用时。
当交互式用户可以完成时，推荐使用基于浏览器的 OAuth。`--no-browser` 会打印登录链接而不是打开它，但仍然等待本地回调和响应。在不受管理的代理或 CI 环境中，将认证留给用户或使用安全提供的 `TAVILY_API_KEY`。
引导设置完成后，不要立即启动第二次登录。

## 使用场景

- 您需要从网站上的许多页面获取内容（例如，所有 `/docs/`）
- 您想要下载文档以供离线使用
- [工作流](../tavily-cli/SKILL.md) 中的第 4 步：搜索 → 提取 → 映射 → **爬取** → 研究

## 快速入门

```bash
# 基本爬取
tvly crawl "https://docs.example.com" --json

# 将每个页面保存为 Markdown 文件
tvly crawl "https://docs.example.com" --output-dir ./docs/

# 深度爬取并设置限制
tvly crawl "https://docs.example.com" --max-depth 2 --limit 50 --json

# 筛选特定路径
tvly crawl "https://example.com" --select-paths "/api/.*,/guides/.*" --exclude-paths "/blog/.*" --json

# 语义聚焦（返回相关片段，而不是完整页面）
tvly crawl "https://docs.example.com" --instructions "查找认证文档" --chunks-per-source 3 --json
```

## 选项

| 选项 | 描述 |
|------|------|
| `--max-depth` | 深度级别（1-5，默认：1） |
| `--max-breadth` | 每页链接数（默认：20） |
| `--limit` | 总页面数上限（默认：50） |
| `--instructions` | 用于语义聚焦的自然语言指导 |
| `--chunks-per-source` | 每页片段数（1-5，需要 `--instructions`） |
| `--extract-depth` | `basic`（默认）或 `advanced` |
| `--format` | `markdown`（默认）或 `text` |
| `--select-paths` | 用逗号分隔的正则表达式模式，用于包含 |
| `--exclude-paths` | 用逗号分隔的正则表达式模式，用于排除 |
| `--select-domains` | 用逗号分隔的正则表达式，用于包含域名 |
| `--exclude-domains` | 用逗号分隔的正则表达式，用于排除域名 |
| `--allow-external / --no-external` | 包含外部链接（默认：允许） |
| `--include-images` | 包含图片 |
| `--timeout` | 最大等待时间（10-150 秒） |
| `-o, --output` | 将 JSON 输出保存到文件 |
| `--output-dir` | 将每个页面保存为 .md 文件到目录 |
| `--json` | 结构化 JSON 输出 |

## 用于上下文提取与数据收集的爬取

**用于代理使用**（将结果输入到 LLM）：

始终使用 `--instructions` + `--chunks-per-source`。返回相关片段而不是完整页面——防止上下文爆炸。

```bash
tvly crawl "https://docs.example.com" --instructions "API 认证" --chunks-per-source 3 --json
```

**用于数据收集**（保存到文件）：

使用 `--output-dir` 而不使用 `--chunks-per-source` 以获取 Markdown 格式的完整页面。

```bash
tvly crawl "https://docs.example.com" --max-depth 2 --output-dir ./docs/
```

## 小贴士

- **保守开始** — `--max-depth 1`，`--limit 20` — 然后逐步扩展。
- **使用 `--select-paths`** 聚焦于您需要的部分。
- **先使用 map** 了解网站结构，然后再进行完整爬取。
- **始终设置 `--limit`** 以防止失控爬取。

## 参考文档

- [tavily-map](../tavily-map/SKILL.md) — 在决定爬取前发现 URL
- [tavily-extract](../tavily-extract/SKILL.md) — 提取单个页面
- [tavily-search](../tavily-search/SKILL.md) — 当您没有 URL 时查找页面
