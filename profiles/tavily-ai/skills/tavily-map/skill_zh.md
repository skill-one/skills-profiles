# tavily map

在不提取内容的情况下发现网站上的 URL。比爬取更快。

## 运行前准备

Map 需要认证。当 `tvly` 已经认证时直接运行请求的命令；不要在每个调用中添加状态检查。

如果 `tvly` 不存在，请按照 [tavily-cli setup](../tavily-cli/SKILL.md#setup) 中的说明进行设置。
如果已安装的 CLI 报告认证错误，请使用 `tvly login` 仅进行认证，或在引导验证也有用的情况下使用 `tvly init --skip-skills`。当有交互式用户可以完成时，优先使用基于浏览器的 OAuth。`--no-browser` 会打印登录链接而不是打开它，但仍然会等待本地回调和。在不受管理的代理或 CI 环境中，将认证留给用户或使用安全提供的 `TAVILY_API_KEY`。在引导设置完成后不要立即启动第二个登录。

## 使用场景

- 你需要在一个大型网站上找到一个特定的子页面
- 你想在决定要提取或爬取什么之前获得所有 URL 的列表
- [工作流](../tavily-cli/SKILL.md) 中的第 3 步：搜索 → 提取 → **map** → 爬取 → 研究

## 快速入门

```bash
# 发现所有 URL
tvly map "https://docs.example.com" --json

# 使用自然语言过滤
tvly map "https://docs.example.com" --instructions "Find API docs and guides" --json

# 按路径过滤
tvly map "https://example.com" --select-paths "/blog/.*" --limit 500 --json

# 深度 map
tvly map "https://example.com" --max-depth 3 --limit 200 --json
```

## 选项

| 选项 | 描述 |
|------|------|
| `--max-depth` | 深度级别 (1-5, 默认: 1) |
| `--max-breadth` | 每页链接数 (默认: 20) |
| `--limit` | 最大发现 URL 数量 (默认: 50) |
| `--instructions` | 用于 URL 过滤的自然语言指导 |
| `--select-paths` | 要包含的逗号分隔的正则表达式模式 |
| `--exclude-paths` | 要排除的逗号分隔的正则表达式模式 |
| `--select-domains` | 要包含的逗号分隔的域名正则表达式 |
| `--exclude-domains` | 要排除的逗号分隔的域名正则表达式 |
| `--allow-external / --no-external` | 包含外部链接 |
| `--timeout` | 最大等待时间 (10-150 秒) |
| `-o, --output` | 将 JSON 响应保存到文件 |
| `--json` | 结构化的 JSON 输出 |

## Map + Extract 模式

使用 `map` 找到正确的页面，然后 `extract` 它。这通常比爬取整个网站更高效：

```bash
# 第 1 步：找到认证文档
tvly map "https://docs.example.com" --instructions "authentication" --json

# 第 2 步：提取你找到的特定页面
tvly extract "https://docs.example.com/api/authentication" --json
```

## 小贴士

- **Map 仅用于 URL 发现** — 不进行内容提取。使用 `extract` 或 `crawl` 获取内容。
- **Map + extract 比 crawl 更高效**，当你只需要从大型网站获取几个特定页面时。
- **使用 `--instructions`** 进行语义过滤，当路径模式不够用时。

## 参考文档

- [tavily-extract](../tavily-extract/SKILL.md) — 从你发现的 URL 中提取内容
- [tavily-crawl](../tavily-crawl/SKILL.md) — 当你需要许多页面时进行批量提取
