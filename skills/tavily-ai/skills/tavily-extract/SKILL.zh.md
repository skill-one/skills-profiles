---
name: tavily-extract
description: 通过Tavily CLI从特定URL提取干净的Markdown或文本内容。当用户有一个或多个URL并希望获取其内容时，可以使用此技能，例如当用户说“提取”、“从...抓取内容”、“从...拉取文本”、“获取...页面”或“阅读这个网页”，或者需要从网页中获取干净的文本时。该技能可以处理JavaScript渲染的页面，返回针对LLM优化的Markdown，并支持以查询为中心的片段化提取。单次调用可处理最多20个URL。
---

# tavily extract

从一个或多个 URL 中提取干净的 Markdown 或文本内容。

## 运行前准备

当 `tvly` 可用时直接运行 extract。Extract 支持无密钥访问，所以在第一次请求前无需寻找 API 密钥或进行身份验证。

如果 `tvly` 不存在，请先按照 [tavily-cli setup](../tavily-cli/SKILL.md#setup) 进行设置，然后再重试。如果在交互式会话中达到无密钥访问上限，请运行 `tvly login` 打开浏览器 OAuth，然后重试原始提取操作一次。在不被管理的环境中，应报告访问上限和身份验证选项，而不是启动交互式流程。在引导设置完成后不要立即启动第二次登录。

## 使用场景

- 你有一个特定的 URL 并想获取其内容
- 你需要从 JavaScript 渲染的页面获取文本
- [工作流](../tavily-cli/SKILL.md) 中的第 2 步：搜索 → **提取** → 映射 → 抓取 → 研究

## 快速入门

```bash
# 单个 URL
tvly extract "https://example.com/article" --json

# 多个 URL
tvly extract "https://example.com/page1" "https://example.com/page2" --json

# 基于查询的提取（仅返回相关片段）
tvly extract "https://example.com/docs" --query "authentication API" --chunks-per-source 3 --json

# JavaScript 内容较多的页面
tvly extract "https://app.example.com" --extract-depth advanced --json

# 保存到文件
tvly extract "https://example.com/article" -o article.json
```

## 选项

| 选项 | 描述 |
|--------|-------------|
| `--query` | 根据与该查询的相关性重新排序片段 |
| `--chunks-per-source` | 每个 URL 的片段数量（1-5，需要 `--query`） |
| `--extract-depth` | `basic`（默认）或 `advanced`（用于 JavaScript 页面） |
| `--format` | `markdown`（默认）或 `text` |
| `--include-images` | 包含图像 URL |
| `--timeout` | 最大等待时间（1-60 秒） |
| `-o, --output` | 将 JSON 响应保存到文件 |
| `--json` | 结构化的 JSON 输出 |

## 提取深度

| 深度 | 使用场景 |
|-------|-------------|
| `basic` | 简单页面，快速 — 首先尝试此选项 |
| `advanced` | JavaScript 渲染的单页应用 (SPA)、动态内容、表格 |

## 小贴士

- **每次请求最多 20 个 URL** — 将较大的列表分批多次调用。
- **使用 `--query` + `--chunks-per-source`** 获取仅相关的内容，而不是完整页面。
- **首先尝试 `basic`，如果内容缺失则切换到 `advanced`**。
- **为慢速页面设置 `--timeout`**（最长 60 秒）。
- **即使退出码为 0，也要检查 `failed_results`。** 成功请求仍可能返回未提取的页面。在适当的情况下，使用 `advanced` 重试受影响的 URL，否则应报告每个 URL 的失败，而不是将请求视为完成。
- 如果搜索结果已包含你需要的內容（通过 `--include-raw-content`），可以跳过提取步骤。

## 参见

- [tavily-search](../tavily-search/SKILL.md) — 当你没有 URL 时查找页面
- [tavily-crawl](../tavily-crawl/SKILL.md) — 从网站上的许多页面提取内容
