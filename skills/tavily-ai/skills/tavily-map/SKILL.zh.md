---
name: tavily-map
description: 通过 Tavily CLI 发现并列出网站上的所有 URL，无需提取内容。当用户想要在大网站上查找特定页面、列出所有 URL、查看网站结构、找到域名的某个内容位置，或说出“绘制网站地图”、“查找 URL”、“有哪些页面”、“列出所有页面”或“网站结构”时，使用此技能。比爬取更快——仅返回 URL。当你知道网站但不知道确切页面时，这是必不可少的。可与提取功能结合使用，以实现有针对性的内容检索。
---

# tavily map

在不提取内容的情况下发现网站上的 URL。比爬取更快。

## 运行前准备

Map 需要认证。当 `tvly` 已经认证时，直接运行请求的命令；不要在每个调用中添加状态检查。

如果 `tvly` 不存在，请按照 [tavily-cli setup](../tavily-cli/SKILL.md#setup) 进行设置。
如果已安装的 CLI 报告认证错误，请使用 `tvly login` 仅进行认证，或在引导验证也有用时使用 `tvly init --skip-skills`。当有交互式用户可以完成时，优先使用基于浏览器的 OAuth。`--no-browser` 会打印登录链接而不是打开它，但仍然等待本地回调和。在不受管理的代理或 CI 环境中，将认证交给用户或使用安全提供的 `TAVILY_API_KEY`。在引导设置完成后不要立即启动第二个登录。

## 使用场景

- 你需要在一个大型网站上找到一个特定的子页面
- 你想在决定要提取或爬取什么之前获得所有 URL 的列表
- [工作流](../tavily-cli/SKILL.md) 中的第 3 步：搜索 → 提取 → **map** → 爬取 → 研究

## 快速入门

```bash
# 发现所有 URL
tvly map "https://docs.example.com" --json

# 带自然语言过滤
tvly map "https://docs.example.com" --instructions "Find API docs and guides" --json

# 通过路径过滤
tvly map "https://example.com" --select-paths "/blog/.*" --limit 500 --json

# 深度 map
tvly map "https://example.com" --max-depth 3 --limit 200 --json
```

## 选项

| 选项 | 描述 |
|------|------|
| `--max-depth` | 深度级别 (1-5, 默认: 1) |
| `--max-breadth` | 每页链接数 (默认: 20) |
| `--limit` | 最大发现 URL 数 (默认: 50) |
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
- **Map + extract 比 crawl 更高效** 当你只需要从大型网站获取几个特定页面时。
- **使用 `--instructions`** 当路径模式不足以进行语义过滤时。

## 参见

- [tavily-extract](../tavily-extract/SKILL.md) — 从你发现的 URL 中提取内容
- [tavily-crawl](../tavily-crawl/SKILL.md) — 当你需要许多页面时进行批量提取
