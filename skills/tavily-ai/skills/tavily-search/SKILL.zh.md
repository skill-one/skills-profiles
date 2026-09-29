---
name: tavily-search
description: 通过Tavily CLI使用针对LLM优化的搜索结果进行网络搜索。当用户想要搜索网络、查找文章、查询信息、获取最新新闻、发现来源，或说出“搜索”、“找到我”、“查询”、“最新动态是什么”、“查找关于...的文章”，或需要从互联网获取当前信息时，使用此技能。返回包含内容片段、相关性分数和元数据的相关结果——针对LLM进行优化。支持域名过滤、时间范围和多级搜索深度。
---

# tavily 搜索

返回 LLM 优化结果的网络搜索，包含内容片段和相关性分数。

## 运行前准备

当 `tvly` 可用时直接运行搜索。搜索支持无密钥配额访问，因此在首次请求前无需查找 API 密钥或进行身份验证。

如果 `tvly` 缺失，请先按照 [tavily-cli 设置](../tavily-cli/SKILL.md#setup) 进行设置，然后再重试。如果在交互式会话中达到无密钥配额上限，请运行 `tvly login` 打开浏览器 OAuth，然后重试原始搜索一次。在无人值守环境中，请报告配额和身份验证选项，而不是启动交互式流程。在引导设置完成后，不要立即启动第二次登录。

## 使用场景

- 您需要查找任何主题的信息
- 您还没有具体的 URL
- [工作流](../tavily-cli/SKILL.md) 的第一步：**搜索** → 提取 → 映射 → 抓取 → 研究

## 快速入门

```bash
# 基本搜索
tvly search "您的查询" --json

# 使用更多结果的进阶搜索
tvly search "量子计算" --depth advanced --max-results 10 --json

# 近期新闻
tvly search "AI 新闻" --time-range week --topic news --json

# 域名过滤
tvly search "SEC 提交文件" --include-domains sec.gov,reuters.com --json

# 包含完整页面内容
tvly search "React Hooks 教程" --include-raw-content --max-results 3 --json
```

## 选项

| 选项 | 描述 |
|------|-------------|
| `--depth` | `ultra-fast`, `fast`, `basic` (默认), `advanced` |
| `--max-results` | 最大结果数，0-20 (默认: 5) |
| `--topic` | `general` (默认), `news`, `finance` |
| `--time-range` | `day`, `week`, `month`, `year` |
| `--start-date` | 结果起始日期 (YYYY-MM-DD) |
| `--end-date` | 结果截止日期 (YYYY-MM-DD) |
| `--include-domains` | 要包含的域名，逗号分隔 |
| `--exclude-domains` | 要排除的域名，逗号分隔 |
| `--country` | 提升来自特定国家的结果 |
| `--include-answer` | 包含 AI 答案 (`basic` 或 `advanced`) |
| `--include-raw-content` | 包含完整页面内容 (`markdown` 或 `text`) |
| `--include-images` | 包含图像结果 |
| `--include-image-descriptions` | 包含 AI 图像描述 |
| `--chunks-per-source` | 每个来源的片段数 (仅限进阶/快速深度) |
| `-o, --output` | 将 JSON 响应保存到文件 |
| `--json` | 结构化 JSON 输出 |

## 搜索深度

| 深度 | 速度 | 相关性 | 适用于 |
|-------|-------|-----------|----------|
| `ultra-fast` | 最快 | 较低 | 实时聊天、自动补全 |
| `fast` | 快 | 良好 | 需要片段、延迟重要 |
| `basic` | 中等 | 高 | 通用 (默认) |
| `advanced` | 较慢 | 最高 | 精确性、特定事实 |

## 小贴士

- **查询长度不超过 400 个字符** — 专注于搜索查询，而非提示。
- **将复杂查询拆分为子查询** 以获得更好的结果。
- **使用 `--include-raw-content`** 当您需要完整页面文本时（可节省单独的提取调用）。
- **使用 `--include-domains`** 以专注于可信来源。
- **使用 `--time-range`** 获取最新信息。
- **在原始主要来源处验证身份敏感的事实。** 对于发布版本、所有权或类似命名的项目，请确认官方仓库或域名，而不是仅依赖生成的答案或包名匹配。
- 从标准输入读取：`echo "查询" | tvly search - --json`

## 参见

- [tavily-extract](../tavily-extract/SKILL.md) — 从特定 URL 提取内容
- [tavily-research](../tavily-research/SKILL.md) — 全面多源研究
