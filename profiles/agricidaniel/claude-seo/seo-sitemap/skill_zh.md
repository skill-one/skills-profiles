# 网站地图分析与生成

## 模式 1：分析现有网站地图

在报告网站地图缺失之前发现候选者：

```bash
"${CLAUDE_PLUGIN_ROOT}/scripts/claude-seo" run sitemap_discovery.py <url> --json
```

辅助工具会读取 robots.txt 中每个有界定的 `Sitemap:` 声明，通过共享的 SSRF 安全获取层验证跨主机目标，并在声明的网站地图过时或无效时探测常见路径。仅使用 `found` 中的条目；将声明的失败保留为发现结果，而不是将单独的 robots.txt 行视为网站地图有效的证据。

### 验证检查
- 有效的 XML 格式
- 每个文件限制：**≤50,000 个 URL AND ≤50MB 未压缩**（以先达到者为准）
- 所有 URL 返回 HTTP 200
- `<lastmod>` 准确：必须是有效的 **W3C Datetime** 并反映**最后一次重大内容变更**（主要内容、结构化数据、链接，不包括版权/模板编辑）。Google 仅在持续且可验证准确时才认可 `<lastmod>`，因此当值看起来过于统一或比页面实际内容更新时发出警告。
- 无过时标签：`<priority>` 和 `<changefreq>` 被 Google 忽略
- robots.txt 中引用了网站地图
- 比较爬取的页面与网站地图；标记缺失的页面

### 质量信号
- 如果 URL 超过 50k，则包含网站地图索引文件
- 按内容类型分割（页面、帖子、图片、视频）
- 网站地图中不包含非规范 URL
- 网站地图中不包含 noindexed URL
- 网站地图中不包含重定向 URL
- 仅使用 HTTPS URL（无 HTTP）

### 常见问题

| 问题 | 严重程度 | 修复 |
|-------|----------|-----|
| 单个文件中 >50k URL | 严重 | 使用网站地图索引分割 |
| 单个文件未压缩 >50MB | 严重 | 使用网站地图索引分割 |
| 非 200 URL | 高 | 删除或修复损坏的 URL |
| 包含 noindexed URL | 高 | 从网站地图中移除 |
| 包含重定向 URL | 中 | 更新为最终 URL |
| 所有 identical lastmod | 低 | 使用实际修改日期 |
| 使用 Priority/changefreq | 信息 | 可以移除（被 Google 忽略） |

### 扩展网站地图（图片 / 视频 / 新闻）

Google 文档了三种子类型，每种有自己的规则，按子类型进行验证：
- **图片** (`http://www.google.com/schemas/sitemap-image/1.1`)：仅剩两个有效标签，`<image:image>` 和 `<image:loc>`（每个 `<url>` 最多 **1,000** 个 `<image:image>`）。`<image:caption>`/`<image:geo_location>`/`<image:title>`/`<image:license>` 已过时（2022 年），标记为可移除的信息级。
- **视频**：需要 `<video:video>` 与 `<video:thumbnail_loc>`、`<video:title>`、`<video:description>`，以及 `<video:content_loc>` 或 `<video:player_loc>`；也支持 mRSS。标记已过时/移除的标签（`<video:category>`、`<video:gallery_loc>`、`<video:price>`、`<video:tvshow>`、播放器自动播放/允许嵌入）为可移除的信息级；引用移除日期前请重新检查 Google 文档。
- **新闻**：每个文件最多 **1,000** 个 `<news:news>`（不是 50,000）；仅包含过去 **2 天** 的文章；需要 `<news:publication>`/`<news:name>`/`<news:language>`/`<news:publication_date>`/`<news:title>`；通过 Search Console 或 robots.txt/网站地图索引提交/发现；仅在相关情况下使用 Publisher Center 进行发布管理。当检测到 `news:` 命名空间时，使用 1,000 的上限覆盖通用的 50k 检查。

## 模式 2：生成新网站地图

### 流程
1. 询问业务类型（或从现有网站自动检测）
2. 从 `../seo-plan/assets/` 目录加载行业模板
3. 与用户进行交互式结构规划
4. 应用质量门禁：
   - ⚠️ 警告：30+ 地点页面（需要 60%+ 独特内容）
   - 🛑 停止：50+ 地点页面（需要说明理由）
5. 生成有效的 XML 输出
6. 在 50,000 个 URL 或 50MB 未压缩中先达到者处分割，并使用网站地图索引
7. 生成 STRUCTURE.md 文档

### 安全的程序化页面（可大规模使用）
✅ 集成页面（带真实设置文档）
✅ 模板/工具页面（带可下载内容）
✅ 术语表页面（200+ 字定义）
✅ 产品页面（独特规格、评论）
✅ 用户个人资料页面（用户生成内容）

### 惩罚风险（应避免大规模使用）
❌ 仅交换城市名称的地点页面
❌ 没有特定行业价值的 "最佳 [工具] for [行业]"
❌ 没有真实比较数据的 "[竞争对手] 替代品"
❌ 没有人类审核和独特价值的 AI 生成页面

## 网站地图格式

### 标准网站地图

```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://example.com/page</loc>
    <lastmod>2026-02-07</lastmod>
  </url>
</urlset>
```

### 网站地图索引（用于 >50k URL）

```xml
<?xml version="1.0" encoding="UTF-8"?>
<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <sitemap>
    <loc>https://example.com/sitemap-pages.xml</loc>
    <lastmod>2026-02-07</lastmod>
  </sitemap>
  <sitemap>
    <loc>https://example.com/sitemap-posts.xml</loc>
    <lastmod>2026-02-07</lastmod>
  </sitemap>
</sitemapindex>
```

## 错误处理

- **URL 不可达**：报告 HTTP 状态码并建议检查网站是否在线
- **未找到网站地图**：运行 `sitemap_discovery.py`，仅在声明和常见候选者检查后其 `found` 列表为空时报告 "未找到"
- **无效的 XML 格式**：报告具体的解析错误和行号
- **检测到速率限制**：回退并报告部分结果，注明重试时机

## 输出

### 用于分析
- `VALIDATION-REPORT.md`：分析结果
- 严重程度问题列表
- 建议

### 用于生成
- `sitemap.xml`（或带索引的分割文件）
- `STRUCTURE.md`：网站架构文档
- URL 数量和组织总结
