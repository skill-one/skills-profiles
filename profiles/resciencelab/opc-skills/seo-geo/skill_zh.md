# SEO/GEO 优化技能

针对网站提供全面、系统的 SEO 和 GEO（Generative Engine Optimization，即生成式引擎优化）服务。同时优化传统搜索引擎（Google、Bing）和 AI 搜索引擎（ChatGPT、Perplexity、Gemini、Copilot、Claude）的相关内容。

## 快速参考

**GEO = Generative Engine Optimization** - 优化内容以便被 AI 搜索引擎引用。

**核心洞察：** AI 搜索引擎不排名页面，而是**引用来源**。被引用即是新的“排名第一”。

## 工作流程

### 步骤 1：网站审计

获取目标 URL 并分析当前的 SEO/GEO 状态。

**基础 SEO 审计（免费）：**
```bash
python3 scripts/seo_audit.py "https://example.com"
```
**适用场景：** 快速进行技术 SEO 检查（标题、元信息、H1、robots、站点地图、加载时间）。无需 API。

---

**检查元标签：**
```bash
curl -sL "https://example.com" | grep -E "<title>" | <meta name="description"> | <meta property="og:" | <meta property="application/ld+json" | head -20
```

**适用场景：** 快速检查任意网页上的核心元标签和模式标注（schema markup）。

---

**检查 robots.txt：**
```bash
curl -s "https://example.com/robots.txt"
```

**适用场景：** 验证允许/阻止了哪些机器人。对于确保 AI 搜索引擎能够抓取网站至关重要。

---

**检查站点地图：**
```bash
curl -s "https://example.com/sitemap.xml" | head -50
```

**适用场景：** 验证站点地图结构，并确保所有重要页面包含在内，供搜索引擎发现。

**验证 AI 机器人访问权限：**
```
# These bots should be allowed in robots.txt:
- Googlebot (Google)
- Bingbot (Bing/Copilot)
- PerplexityBot (Perplexity)
- ChatGPT-User (ChatGPT with browsing)
- ClaudeBot / anthropic-ai (Claude)
- GPTBot (OpenAI)
```

### 步骤 2：关键词研究

使用 **WebSearch** 研究目标关键词：

```
WebSearch: "{keyword} keyword difficulty site:ahrefs.com OR site:semrush.com"
WebSearch: "{keyword} search volume 2026"
WebSearch: "site:{competitor.com} {keyword}"
```

**分析：**
- 搜索量及难度
- 竞争对手关键词策略
- 长尾关键词机会
- 国际关键词冲突（例如，“OPC”在英语市场中指工业自动化）

### 步骤 3：AI 搜索引擎 GEO 优化

应用 **9 种普林斯顿 GEO 方法**（详见 [references/geo-research.md](./references/geo-research.md)）：

| 方法 | 可见度提升 | 应用方式 |
|--------|-----------------|--------------|
| **引用来源** | +40% | 添加权威引用和参考资料 |
| **数据添加** | +37% | 包含具体数字和数据点 |
| **引用添加** | +30% | 添加带注明的专家引用 |
| **权威语气** | +25% | 使用自信、专业的语言 |
| **易于理解** | +20% | 简化复杂概念 |
| **专业术语** | +18% | 包含领域特定术语 |
| **独特词汇** | +15% | 提升词汇多样性 |
| **流畅度优化** | +15-30% | 改善可读性和流畅度 |
| ~~关键词堆砌~~ | **-10%** | **避免 - 损害可见度** |

**最佳组合：** 流畅度 + 数据 = 最大提升

**生成 FAQPage 模式标注**（AI 可见度 +40%）：
```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [{
    "@type": "Question",
    "name": "What is [topic]?",
    "acceptedAnswer": {
      "@type": "Answer",
      "content": "According to [source], [answer with statistics]."
    }
  }]
}
```

**优化内容结构：**
- 采用“先给出答案”的格式（开头直接给出答案）
- 清晰的 H1 > H2 > H3 层级结构
- 项目符号和编号列表
- 用于对比数据的表格
- 短段落（最多 2-3 句话）

### 步骤 4：传统 SEO 优化

**元标签模板：**
```html
<title>{Primary Keyword} - {Brand} | {Secondary Keyword}</title>
<meta name="description" content="{Compelling description with keyword, 150-160 chars}">
<meta name="keywords" content="{keyword1}, {keyword2}, {keyword3}">

<!-- Open Graph -->
<meta property="og:title" content="{Title}">
<meta property="og:description" content="{Description}">
<meta property="og:image" content="{Image URL 1200x630}">
<meta property="og:url" content="{Canonical URL}">
<meta property="og:type" content="website">

<!-- Twitter Cards -->
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{Title}">
<meta name="twitter:description" content="{Description}">
<meta name="twitter:image" content="{Image URL}">
```

**JSON-LD 模式标注**（详见 [references/schema-templates.md](./references/schema-templates.md)）：
- 内容页面使用 WebPage / Article
- 常见问题部分使用 FAQPage
- 产品页面使用 Product
- 关于页面使用 Organization
- 工具/应用使用 SoftwareApplication

**检查内容：**
- [ ] H1 包含主要关键词
- [ ] 图片具有描述性的替代文本（alt text）
- [ ] 与相关内容的内置链接
- [ ] 外部链接带有 `rel="noopener noreferrer"`
- [ ] 内容支持移动端友好访问
- [ ] 页面加载时间小于 3 秒

### 步骤 5：验证与监控

**模式标注验证：**
```bash
# Open Google Rich Results Test
open "https://search.google.com/test/rich-results?url={encoded_url}"

# Open Schema.org Validator
open "https://validator.schema.org/?url={encoded_url}"
```

**检查索引状态：**
```bash
# Google (use Search Console API or manual check)
open "https://www.google.com/search?q=site:{domain}"

# Bing
open "https://www.bing.com/search?q=site:{domain}"
```

**生成报告：**
```markdown
## SEO/GEO 优化报告

### 当前状态
- 元标签：✅/❌
- 模式标注：✅/❌
- AI 机器人访问：✅/❌
- 移动端友好：✅/❌
- 页面速度：X 秒

### 建议
1. [优先行动 1]
2. [优先行动 2]
3. [优先行动 3]

### 已应用的 GEO 优化
- [ ] 已添加 FAQPage 模式
- [ ] 已包含数据
- [ ] 已添加引用
- [ ] 采用先答案结构
```

## 平台特定优化

详见 [references/platform-algorithms.md](./references/platform-algorithms.md) 以获取各平台的详细排名因素。

### ChatGPT
- 重点关注**品牌域名权威性**（被第三方引用频率高出 11%）
- 在 **30 天内**更新内容（引用量提升 3.2 倍）
- 构建**反向链接**（超过 35 万引荐域名 = 平均 8.4 次引用）
- 使内容风格与 ChatGPT 的回复格式相匹配

### Perplexity
- 在 robots.txt 中允许**PerplexityBot**
- 使用**常见问题模式（FAQ Schema）**（引用率更高）
- 托管**PDF 文档**（优先用于引用）
- 侧重于**语义相关性**而非关键词

### Google AI 概览（SGE）
- 针对**E-E-A-T**（经验、专业度、权威性、可信度）进行优化
- 使用**结构化数据**（模式标注）
- 构建**主题权威性**（内容集群 + 内部链接）
- 包含**权威引用**（可见度提升 132%）

### Microsoft Copilot / Bing
- 确保**Bing 索引**（引用所需）
- 针对**Microsoft 生态系统**进行优化（LinkedIn、GitHub 提及有助于提升效果）
- 页面加载速度 **&lt; 2 秒**
- 清晰的**实体定义**

### Claude AI
- 确保**Brave 搜索索引**（Claude 使用 Brave，而非 Google）
- **事实密度**高（偏好数据丰富的内容）
- **结构清晰度**高（易于提取）

## 技能依赖

本技能配合以下内容效果最佳：
- **twitter 技能** - 搜索 SEO 专家以获取最新技巧
- **reddit 技能** - 搜索 r/SEO、r/bigseo 的讨论
- **WebSearch** - 关键词研究与竞争对手分析

## 参考文档

- [references/platform-algorithms.md](./references/platform-algorithms.md) - 各平台的详细排名因素
- [references/geo-research.md](./references/geo-research.md) - 普林斯顿 GEO 研究（9 种方法）
- [references/schema-templates.md](./references/schema-templates.md) - JSON-LD 模板
- [references/seo-checklist.md](./references/seo-checklist.md) - 完整的 SEO 审计清单
- [references/tools-and-apis.md](./references/tools-and-apis.md) - 工具与 API 参考文档
- [examples/opc-skills-case-study.md](./examples/opc-skills-case-study.md) - 真实世界优化示例
