# SEO/GEO优化技能

全面的网站SEO和GEO（生成式引擎优化）。针对传统搜索引擎（Google、Bing）和AI搜索引擎（ChatGPT、Perplexity、Gemini、Copilot、Claude）进行优化。

## 快速参考

**GEO = 生成式引擎优化** - 优化内容以便AI搜索引擎引用。

**关键洞察：** AI搜索引擎不排名页 - 它们**引用来源**。被引用就是新的"排名第一"。

## 工作流程

### 第1步：网站审计

获取目标URL并分析当前的SEO/GEO状态。

**基础SEO审计（免费）：**
```bash
python3 scripts/seo_audit.py "https://example.com"
```
**使用这个命令：** 快速技术SEO检查（标题、元数据、H1、robots、站点地图、加载时间）。无需API。

---

**检查元标签：**
```bash
curl -sL "https://example.com" | grep -E "<title>|<meta name=\"description\"|<meta property=\"og:|application/ld\+json" | head -20
```

**使用这个命令：** 快速检查任何网页上必要的元标签和模式标记。

---

**检查robots.txt：**
```bash
curl -s "https://example.com/robots.txt"
```

**使用这个命令：** 验证哪些机器人被允许/被阻止。对于确保AI搜索引擎可以抓取您的网站至关重要。

---

**检查站点地图：**
```bash
curl -s "https://example.com/sitemap.xml" | head -50
```

**使用这个命令：** 验证站点地图结构并确保所有重要页面都包含在搜索引擎发现中。

**验证AI机器人访问权限：**
```
# 这些机器人应该在robots.txt中允许：
- Googlebot (Google)
- Bingbot (Bing/Copilot)
- PerplexityBot (Perplexity)
- ChatGPT-User (带浏览功能的ChatGPT)
- ClaudeBot / anthropic-ai (Claude)
- GPTBot (OpenAI)
```

### 第2步：关键词研究

使用**WebSearch**研究目标关键词：

```
WebSearch: "{keyword} 关键词难度 site:ahrefs.com OR site:semrush.com"
WebSearch: "{keyword} 搜索量 2026"
WebSearch: "site:{competitor.com} {keyword}"
```

**分析：**
- 搜索量和难度
- 竞争对手关键词策略
- 长尾关键词机会
- 国际关键词冲突（例如，"OPC" = 工业自动化在英语市场）

### 第3步：GEO优化（AI搜索引擎）

应用**9种普林斯顿GEO方法**（参见[references/geo-research.md](./references/geo-research.md)）：

| 方法 | 可见性提升 | 如何应用 |
|------|------------|----------|
| **引用来源** | +40% | 添加权威引用和参考文献 |
| **添加统计数据** | +37% | 包含具体数字和数据点 |
| **添加引言** | +30% | 添加带署名的专家引言 |
| **权威语气** | +25% | 使用自信、专业的语言 |
| **易于理解** | +20% | 简化复杂概念 |
| **技术术语** | +18% | 包含特定领域的术语 |
| **独特词汇** | +15% | 增加词汇多样性 |
| **流畅性优化** | +15-30% | 提高可读性和流畅性 |
| ~~关键词堆砌~~ | **-10%** | **避免 - 损害可见性** |

**最佳组合：** 流畅性 + 统计数据 = 最大提升

**生成FAQPage模式** (+40% AI可见性):
```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [{
    "@type": "Question",
    "name": "什么是[主题]?",
    "acceptedAnswer": {
      "@type": "Answer",
      "text": "根据[来源]，[带统计数据的答案]。"
    }
  }]
}
```

**优化内容结构：**
- 使用"先回答"格式（直接在顶部回答）
- 清晰的H1 > H2 > H3层次结构
- 项目符号和编号列表
- 表格用于比较数据
- 短段落（最多2-3句）

### 第4步：传统SEO优化

**元标签模板：**
```html
<title>{主要关键词} - {品牌} | {次要关键词}</title>
<meta name="description" content="{带有关键词的引人入胜的描述, 150-160个字符}">
<meta name="keywords" content="{keyword1}, {keyword2}, {keyword3}">

<!-- Open Graph -->
<meta property="og:title" content="{标题}">
<meta property="og:description" content="{描述}">
<meta property="og:image" content="{图片URL 1200x630}">
<meta property="og:url" content="{规范URL}">
<meta property="og:type" content="website">

<!-- Twitter Cards -->
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{标题}">
<meta name="twitter:description" content="{描述}">
<meta name="twitter:image" content="{图片URL}">
```

**JSON-LD模式**（参见[references/schema-templates.md](./references/schema-templates.md)）：
- WebPage / Article用于内容页面
- FAQPage用于FAQ部分
- Product用于产品页面
- Organization用于关于页面
- SoftwareApplication用于工具/应用程序

**检查内容：**
- [ ] H1包含主要关键词
- [ ] 图片有描述性alt文本
- [ ] 内部链接到相关内容
- [ ] 外部链接有`rel="noopener noreferrer"`
- [ ] 内容适合移动设备
- [ ] 页面加载时间< 3秒

### 第5步：验证和监控

**模式验证：**
```bash
# 打开Google丰富结果测试
open "https://search.google.com/test/rich-results?url={encoded_url}"

# 打开Schema.org验证器
open "https://validator.schema.org/?url={encoded_url}"
```

**检查索引状态：**
```bash
# Google（使用搜索控制台API或手动检查）
open "https://www.google.com/search?q=site:{domain}"

# Bing
open "https://www.bing.com/search?q=site:{domain}"
```

**生成报告：**
```markdown
## SEO/GEO优化报告

### 当前状态
- 元标签：✅/❌
- 模式标记：✅/❌
- AI机器人访问权限：✅/❌
- 移动设备友好：✅/❌
- 页面速度：X秒

### 建议
1. [优先级1操作]
2. [优先级2操作]
3. [优先级3操作]

### 应用GEO优化
- [ ] 添加FAQPage模式
- [ ] 添加统计数据
- [ ] 添加引用
- [ ] 采用先回答结构
```

## 平台特定优化

参见[references/platform-algorithms.md](./references/platform-algorithms.md)获取详细的排名因素。

### ChatGPT
- 专注于**品牌域名权威**（比第三方引用多11%）
- 在**30天内**更新内容（3.2倍引用）
- 建立**反向链接**（>350K引用域名 = 8.4平均引用）
- 使内容风格与ChatGPT的响应格式匹配

### Perplexity
- 在robots.txt中允许**PerplexityBot**
- 使用**FAQ模式**（更高的引用率）
- 托管**PDF文档**（优先引用）
- 专注于**语义相关性**而非关键词

### Google AI概述（SGE）
- 优化**E-E-A-T**（经验、专业知识、权威、信任）
- 使用**结构化数据**（模式标记）
- 建立**主题权威**（内容集群+内部链接）
- 包含**权威引用**（+132%可见性）

### Microsoft Copilot / Bing
- 确保**Bing索引**（引用所需）
- 优化**Microsoft生态系统**（LinkedIn、GitHub提及有帮助）
- 页面速度**< 2秒**
- 清晰的**实体定义**

### Claude AI
- 确保**Brave搜索索引**（Claude使用Brave，不是Google）
- 高**事实密度**（数据丰富的内容更受欢迎）
- 清晰的**结构清晰度**（易于提取）

## 技能依赖

这个技能最适合与：
- **twitter技能** - 搜索SEO专家获取最新技巧
- **reddit技能** - 搜索r/SEO、r/bigseo进行讨论
- **WebSearch** - 关键词研究和竞争对手分析

## 参考文献

- [references/platform-algorithms.md](./references/platform-algorithms.md) - 每个平台的详细排名因素
- [references/geo-research.md](./references/geo-research.md) - 普林斯顿GEO研究（9种方法）
- [references/schema-templates.md](./references/schema-templates.md) - JSON-LD模板
- [references/seo-checklist.md](./references/seo-checklist.md) - 完整的SEO审计清单
- [references/tools-and-apis.md](./references/tools-and-apis.md) - 工具和API参考
- [examples/opc-skills-case-study.md](./examples/opc-skills-case-study.md) - 真实的优化案例
