> **安装 belt CLI 技能：** `npx skills add belt-sh/cli`

# 竞品分析

通过 [inference.sh](https://inference.sh) CLI 进行结构化竞品分析，结合研究和截图。

## 快速入门

> 需要 inference.sh CLI（belt）。[安装说明](https://raw.githubusercontent.com/inference-sh/skills/refs/heads/main/cli-install.md)

```bash
belt login

# 研究竞品格局
belt app run tavily/search-assistant --input '{
  "query": "2024年顶级项目管理工具市场份额比较"
}'

# 截取竞品网站截图
belt app run infsh/agent-browser --input '{
  "url": "https://competitor.com",
  "action": "screenshot"
}'
```

## 分析框架

### 七层分析

| 层级 | 分析内容 | 数据来源 |
|------|----------|----------|
| 1. **产品** | 功能、用户体验、质量 | 截图、免费试用 |
| 2. **定价** | 计划、定价模式、隐藏费用 | 定价页面、销售电话 |
| 3. **定位** | 信息传递、标语、目标客户 | 网站、广告 |
| 4. **发展势头** | 用户量、收入、增长 | 网络搜索、新闻、融资 |
| 5. **用户评价** | 用户的优势和劣势 | G2、Capterra、App Store |
| 6. **内容** | 博客、社交媒体、SEO策略 | 网站、社交媒体资料 |
| 7. **团队** | 规模、关键招聘、背景 | LinkedIn、关于页面 |

## 研究命令

### 公司概况

```bash
# 一般性智能
belt app run tavily/search-assistant --input '{
  "query": "CompetitorX 公司概况 融资团队规模 2024"
}'

# 融资和财务
belt app run exa/search --input '{
  "query": "CompetitorX 融资轮次 估值 投资者"
}'

# 最新新闻
belt app run tavily/search-assistant --input '{
  "query": "CompetitorX 最新新闻 宣布 2024"
}'
```

### 产品分析

```bash
# 功能对比
belt app run exa/search --input '{
  "query": "CompetitorX 与替代品功能对比 评价"
}'

# 定价详情
belt app run tavily/extract --input '{
  "urls": ["https://competitor.com/pricing"]
}'

# 用户评价
belt app run tavily/search-assistant --input '{
  "query": "CompetitorX 评价 G2 Capterra 优点 缺点 2024"
}'
```

### 用户体验截图

```bash
# 首页
belt app run infsh/agent-browser --input '{
  "url": "https://competitor.com",
  "action": "screenshot"
}'

# 定价页面
belt app run infsh/agent-browser --input '{
  "url": "https://competitor.com/pricing",
  "action": "screenshot"
}'

# 注册流程
belt app run infsh/agent-browser --input '{
  "url": "https://competitor.com/signup",
  "action": "screenshot"
}'
```

## 功能矩阵

### 结构

```markdown
| 功能 | 您的产品 | 竞品A | 竞品B | 竞品C |
|------|:---:|:---:|:---:|:---:|
| 实时协作 | ✅ | ✅ | ❌ | ✅ |
| API访问 | ✅ | 仅付费 | ✅ | ❌ |
| SSO/SAML | ✅ | 企业版 | ✅ | 企业版 |
| 定制报告 | ✅ | 有限 | ✅ | ❌ |
| 移动应用 | ✅ | 仅iOS | ✅ | ✅ |
| 免费版 | ✅ (无限) | ✅ (3用户) | ❌ | ✅ (1项目) |
| 集成 | 50+ | 100+ | 30+ | 20+ |
```

### 规则

- ✅ = 完全支持
- ⚠️ 或 "部分" = 有限或条件性
- ❌ = 不支持
- 注意条件："仅付费"、"企业版"、"Beta"
- 优先突出您优势的功能
- 诚实地说明竞品优势——信誉很重要

## 定价对比

### 结构

```markdown
| | 您的产品 | 竞品A | 竞品B |
|------|:---:|:---:|:---:|
| **免费版** | 是，5用户 | 是，3用户 | 否 |
| **起步版** | $10/用户/月 | $15/用户/月 | $12/用户/月 |
| **专业版** | $25/用户/月 | $30/用户/月 | $29/用户/月 |
| **企业版** | 定制 | 定制 | $50/用户/月 |
| **计费** | 月度/年度 | 仅年度 | 月度/年度 |
| **年度折扣** | 20% | 15% | 25% |
| **最小席位** | 1 | 5 | 3 |
| **隐藏费用** | 无 | 设置费 $500 | API调用计量 |
```

### 注意事项

- 最小席位要求
- 仅年度计费（降低灵活性）
- 各层级功能限制
- 超额费用
- 设置/入门费
- 合同锁定期

## SWOT分析

为每个竞品创建SWOT分析：

```markdown
### 竞品A — SWOT

| 优势 | 劣势 |
|------|------|
| • 强品牌认知度 | • 功能开发缓慢 |
| • 大型集成生态系统 | • 入门复杂 (30+分钟) |
| • 企业销售团队 | • 无免费版 |

| 机会 | 威胁 |
|------|------|
| • AI功能尚未推出 | • 新AI原生竞争对手 |
| • 扩展至中端市场 | • 客户对定价投诉 |
| • 未开发的国际市场 | • 关键工程师离职 (LinkedIn) |
```

## 定位图

一个2x2矩阵，显示竞争对手在两个重要维度上的位置。

### 选择有意义的轴

| 好的轴 | 坏的轴 |
|------|------|
| 简单 ↔ 复杂 | 好 ↔ 坏 |
| SMB ↔ 企业 | 便宜 ↔ 昂贵 (太明显) |
| 自服务 ↔ 销售主导 | 旧 ↔ 新 |
| 专业化 ↔ 通用 | — |

### 模板

```
                    企业
                        │
           竞品C │  竞品A
                ●       │       ●
                        │
  简单 ──────────────────────────── 复杂
                        │
            您 ●       │  竞品B
                        │       ●
                        │
                      SMB
```

### 生成可视化

```bash
# 使用Python创建定位图
belt app run infsh/python-executor --input '{
  "code": "import matplotlib.pyplot as plt\nimport matplotlib\nmatplotlib.use(\"Agg\")\n\nfig, ax = plt.subplots(figsize=(10, 10))\n\n# 竞品\ncompetitors = {\n    \"You\": (-0.3, -0.3),\n    \"Competitor A\": (0.5, 0.6),\n    \"Competitor B\": (0.6, -0.4),\n    \"Competitor C\": (-0.4, 0.5)\n}\n\nfor name, (x, y) in competitors.items():\n    color = \"#22c55e\" if name == \"You\" else \"#6366f1\"\n    size = 200 if name == \"You\" else 150\n    ax.scatter(x, y, s=size, c=color, zorder=5)\n    ax.annotate(name, (x, y), textcoords=\"offset points\", xytext=(10, 10), fontsize=12, fontweight=\"bold\")\n\nax.axhline(y=0, color=\"grey\", linewidth=0.5)\nax.axvline(x=0, color=\"grey\", linewidth=0.5)\nax.set_xlim(-1, 1)\nax.set_ylim(-1, 1)\nax.set_xlabel(\"简单 ← → 复杂\", fontsize=14)\nax.set_ylabel(\"SMB ← → 企业\", fontsize=14)\nax.set_title(\"竞品定位图\", fontsize=16, fontweight=\"bold\")\nax.grid(True, alpha=0.3)\nplt.tight_layout()\nplt.savefig(\"positioning-map.png\", dpi=150)\nprint(\"保存成功\")"
}'
```

## 评价挖掘

### 评价来源

| 平台 | 适合 | URL模式 |
|------|------|------|
| G2 | B2B SaaS | g2.com/products/[product]/reviews |
| Capterra | 商业软件 | capterra.com/software/[id]/reviews |
| App Store | iOS应用 | apps.apple.com |
| Google Play | Android应用 | play.google.com |
| Product Hunt | 新产品发布 | producthunt.com/posts/[product] |
| Reddit | 真实意见 | reddit.com/r/[相关子版块] |

### 提取内容

| 类别 | 查找 |
|------|------|
| **最受称赞** | 幸福用户最常提到的功能是什么？ |
| **最投诉** | 不满意用户说什么？（=您的机会） |
| **转换原因** | 用户为什么离开？什么触发转换？ |
| **功能请求** | 用户希望缺少什么？ |
| **比较提及** | 用户比较时说什么？ |

```bash
# 挖掘G2评价
belt app run tavily/search-assistant --input '{
  "query": "CompetitorX G2评价 投诉 问题 2024"
}'

# Reddit情绪
belt app run exa/search --input '{
  "query": "reddit CompetitorX 替代品 挫败 转换"
}'
```

## 交付格式

### 执行摘要 (1页)

```markdown
## 竞品格局总结

**市场：** [类别] — 市场规模 $[X]B，年增长率 [Y]%

**主要竞争对手：** A (领导者)，B (挑战者)，C (利基市场)

**我们的定位：** [您所处的位置及其重要性]

**关键洞察：** [关于最大机会的一句话]

| 指标 | 您 | A | B | C |
|------|----|----|----|----|
| 用户 | X | Y | Z | W |
| 起步定价 | $X | $Y | $Z | $W |
| 评分 (G2) | X.X | Y.Y | Z.Z | W.W |
```

### 详细报告 (每个竞品)

1. 公司概况 (规模、融资、团队)
2. 产品分析 (功能、用户体验截图)
3. 定价分解
4. SWOT分析
5. 评价分析 (最称赞、最投诉)
6. 与您的定位对比
7. 机会总结

## 对比网格可视化

```bash
# 将竞品截图拼接成对比
belt app run infsh/stitch-images --input '{
  "images": ["your-homepage.png", "competitorA-homepage.png", "competitorB-homepage.png"],
  "direction": "horizontal"
}'
```

## 常见错误

| 错误 | 问题 | 解决方法 |
|------|------|------|
| 仅看功能 | 错过定位、定价、发展势头 | 使用七层框架 |
| 偏见分析 | 失去信誉 | 诚实地说明竞品优势 |
| 数据过时 | 得出错误结论 | 标注所有研究，每季度更新 |
| 竞品过多 | 分析瘫痪 | 专注于前3-5个直接竞争对手 |
| 没有"所以呢" | 数据而无洞察 | 每个部分都以对您的影响结束 |
| 仅功能对比 | 不显示定位 | 包括定价、评价、定位图 |

## 相关技能

```bash
npx skills add inference-sh/skills@web-search
npx skills add inference-sh/skills@prompt-engineering
```

浏览所有应用：`belt app list`
