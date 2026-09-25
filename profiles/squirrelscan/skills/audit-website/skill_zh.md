# 审计网站并修复

对网站运行 squirrelscan 审计，阅读 LLM 报告，将每个问题映射到导致问题的代码或内容，分批修复，并重新审计直到达到分数目标。

需要 `squirrel` CLI ([squirrelscan.com/download](https://squirrelscan.com/download)；使用 `squirrel --version` 验证)。对于 CLI 配置、登录、发布、MCP 和一般 CLI 使用，请使用配套的 `squirrelscan` 技能。

## 规则文档

在 `https://docs.squirrelscan.com/rules/{rule_category}/{rule_id}` 查找任何规则，例如：

https://docs.squirrelscan.com/rules/links/external-links

## 运行审计

```bash
squirrel audit https://example.com --format llm
```

- 使用 `--format llm`：该格式简洁、全面，专为智能体（agent）设计。
- 如果用户未提供 URL，请询问需要审计的网站。
- 优先审计在线站点：只有在在线站点上才能看到真实渲染、性能和重定向行为。如果同时存在本地开发服务器和在线站点，建议审计在线站点；无论哪种情况，修复都应应用于本地代码。
- 审计结果会本地缓存。之后无需重新抓取即可重新渲染：`squirrel report <audit-id} --format llm`。

### 扫描进度

1. **第一轮，快速覆盖**（默认）：快速、浅层的扫描，以了解网站的结构、技术和主要问题，且不影响网站。
2. **第二轮，更深覆盖**：使用 `-C surface`（每个 URL 模式一个页面）进行模板级覆盖，或在签署前进行全面的爬取，使用 `-C full`。

| 模式 | 默认页面 | 用途 |
|------|-------------|-----|
| `quick` | 25 | 首次查看，CI 检查 |
| `surface` | 100 | 模板级覆盖（每个模式如 `/blog/{slug}` 取一个样本） |
| `full` | 500 | 最终验证，深度分析 |

常用参数：`--refresh`（忽略缓存，完整重新获取）、`--resume`（继续中断的爬取）、`-m <n>`（页面限制）、`--verbose`（进度详情）。

如果网站阻止未知爬虫（Shopify / Cloudflare），通过重复 `-H "Name: Value"` 标志传递 Web Bot Auth 请求头。请求头值为机密信息，会在输出中脱敏。参见 https://docs.squirrelscan.com/guides/web-bot-auth

## 修复循环

1. **呈现报告**：分数、等级、按严重程度排序的主要问题。
2. **提出修复方案**：列出可以修复的问题，并在更改任何内容之前与用户确认。
3. **将问题映射到源**：找到每个发现背后的模板、组件或内容文件。
4. **分批修复**：应用已批准的修复。
5. **重新审计**（部署或内容变更后使用 `--refresh`），并展示前后分数。
6. **重复**，直到达到目标或只剩下需要判断的事项（例如“是否应该删除此链接？”）。将这些事项标记给用户审核，而不是猜测。

每批次之后，验证项目仍能构建且现有检查通过。

### 分数目标

| 起始分数 | 目标 | 预期工作量 |
|----------------|--------|---------------|
| < 50（F） | 75+（C） | 主要修复 |
| 50-70（D） | 85+（B） | 中等修复 |
| 70-85（C） | 90+（A） | 润色 |
| > 85（B+） | 95+ | 微调 |

以 `-C full` 的爬取结果为依据签署，因为快速扫描仅采样网站的一部分。

规则带有等级（错误、警告、提示）和等级（1-10）：先修复错误，再修复高等级警告。需要内容编辑的发现与需要代码编辑的发现同等重要。通常断裂的链接需要人工决定（删除、替换或保留）：应标记这些链接，而不是猜测。

## 验证回归

与基准对比以证明改进或发现回归：

```bash
squirrel report --diff <baseline-audit-id} --format llm
squirrel report --regression-since example.com --format llm
```

## 完成

完成意味着：所有错误已修复；警告已修复或记录为需要人工审核；重新审计确认了改进；用户已看到前后分数对比以及所有所做更改的摘要。定期重新审计以保持网站健康。如果用户希望分享结果，提供已发布的报告（参见 `squirrelscan` 技能）。

## 报告格式

LLM 报告是紧凑的 XML/文本混合格式，针对 token 效率优化，包含健康分数、按类别分组的 issue、受影响 URL、断裂链接以及优先建议。完整规范：[OUTPUT-FORMAT.md](references/OUTPUT-FORMAT.md)
