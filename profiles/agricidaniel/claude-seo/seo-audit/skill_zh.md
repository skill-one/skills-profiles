# 全站SEO审计

## 流程

1. **渲染首页**：使用 `"${CLAUDE_PLUGIN_ROOT}/scripts/claude-seo" run render_page.py <url> --mode auto --json` 命令捕获原始HTML、渲染后的HTML、提取的文本、SPA状态以及在需要时获取可访问性数据
2. **检测业务类型**：根据SEO协调器分析首页信号
3. **爬取网站**：遵循内部链接，最多500页，尊重robots.txt
4. **委托给子代理**（如果可用，否则顺序运行）：
   - `seo-technical` -- robots.txt、站点地图、规范标签、核心网页指标、安全头
   - `seo-content` -- E-E-A-T、可读性、薄内容、AI引用准备情况
   - `seo-schema` -- 检测、验证、生成建议
   - `seo-sitemap` -- 结构分析、质量门禁、缺失页面
   - `seo-performance` -- LCP、INP、CLS测量
   - `seo-visual` -- 截图、移动测试、首屏分析
   - `seo-geo` -- AI爬虫访问、llms.txt、可引用性、品牌提及信号
   - `seo-agentic` -- Lighthouse代理浏览部分（X/N）、代理的可访问性树、AI代理访问策略、Markdown和发现文件、WebMCP（在完整审计中始终包含；其结果会输入AI搜索准备情况）
   - `seo-local` -- GBP信号、NAP一致性、评价、本地站点地图、特定行业本地因素（当检测到本地服务行业时：实体店、SAB或混合业务类型时生成）
   - `seo-maps` -- 地理网格排名跟踪、GBP审计、评价智能、竞争对手半径映射（当检测到本地服务且DataForSEO MCP可用时生成）
   - `seo-google` -- CWV字段数据（CrUX）、URL索引（GSC）、自然流量（GA4）（当通过`"${CLAUDE_PLUGIN_ROOT}/scripts/claude-seo" run google_auth.py --check`检测到Google API凭证时生成）
   - `seo-matomo` -- Matomo报告API：自然流量、着陆页、设备/国家细分、来源分析（当检测到Matomo凭证时通过`"${CLAUDE_PLUGIN_ROOT}/scripts/claude-seo" run matomo_auth.py --check`生成；当两者都配置时与`seo-google`一起运行，或当GA4未配置时作为GA4替代方案）
   - `seo-backlinks` -- 反向链接数据：DA/PA、引用域名、锚文本、有毒链接（当检测到Moz或Bing API凭证时通过`"${CLAUDE_PLUGIN_ROOT}/scripts/claude-seo" run backlinks_auth.py --check`生成，或始终包含Common Crawl域名级指标）
   - `seo-cluster` -- 语义聚类分析（当检测到内容策略信号时：博客、支柱页面、主题集群）
   - `seo-sxo` -- 搜索体验分析：页面类型不匹配、用户故事、角色评分（在完整审计中始终包含）
   - `seo-drift` -- 漂移分析：与存储的基线进行比较（当URL存在漂移基线时通过`"${CLAUDE_PLUGIN_ROOT}/scripts/claude-seo" run drift_history.py <url>`生成）
   - `seo-ecommerce` -- 产品模式、市场情报（当检测到电子商务行业时生成）
5. **评分** -- 汇总成SEO健康评分（0-100）
6. **持久化审计工件** -- 在`{domain}-audit/`下写入所有输出
7. **报告** -- 生成优先级行动方案和可选的PDF/HTML报告

## 爬取配置

```
最大页面数：500
尊重robots.txt：是
跟随重定向：是（最多3跳）
每页超时：30秒
并发请求：5
请求间隔：1秒
```

## 输出文件

- `{domain}-audit/FULL-AUDIT-REPORT.md`：全面发现
- `{domain}-audit/ACTION-PLAN.md`：优先级建议（关键 > 高 > 中 > 低）
- `{domain}-audit/audit-data.json`：结构化审计信封用于报告生成
- `{domain}-audit/findings/*.md`：按类别专业发现（`technical.md`、`content.md`、`schema.md`、`performance.md`、`visual.md`等）
- `{domain}-audit/screenshots/`：桌面+移动捕获（如果Playwright可用）
- **PDF报告**（推荐）：使用`"${CLAUDE_PLUGIN_ROOT}/scripts/claude-seo" run google_report.py --type full --data {domain}-audit/audit-data.json --domain <domain> --output-dir {domain}-audit/`生成专业的A4 PDF。这会产生带有封面、目录、执行摘要、图表（Lighthouse仪表盘、查询条、索引甜甜圈）、指标卡片、阈值表格、优先级建议（附带工作量估计）和实施路线图的企业报告。在完成审计后始终提供PDF生成选项。

## 结构化审计数据信封

使用此形状编写`{domain}-audit/audit-data.json`，以便`"${CLAUDE_PLUGIN_ROOT}/scripts/claude-seo" run google_report.py --type full --data {domain}-audit/audit-data.json --domain <domain> --output-dir {domain}-audit/`即使Google API数据不可用也能生成报告：

```json
{
  "summary": {
    "health_score": 0,
    "business_type": "检测到的类型",
    "top_findings": [],
    "quick_wins": []
  },
  "categories": [
    {
      "name": "技术SEO",
      "score": 0,
      "what_works": [],
      "findings": [
        {
          "title": "发现标题",
          "severity": "关键|高|中|低|信息",
          "description": "有证据支持的细节",
          "recommendation": "具体修复"
        }
      ]
    }
  ],
  "action_plan": {
    "phases": [
      {"name": "阶段1：关键修复", "timeframe": "第1周", "items": []},
      {"name": "阶段2：高影响改进", "timeframe": "第2-3周", "items": []},
      {"name": "阶段3：内容与权威", "timeframe": "第2个月", "items": []},
      {"name": "阶段4：监控与迭代", "timeframe": "持续进行", "items": []}
    ]
  },
  "artifacts": {
    "findings_dir": "findings/",
    "screenshots_dir": "screenshots/"
  }
}
```

## 评分权重

| 类别 | 权重 |
|----------|--------|
| 技术SEO | 22% |
| 内容质量 | 23% |
| 页面内SEO | 20% |
| 模式/结构化数据 | 10% |
| 性能（CWV） | 10% |
| AI搜索准备情况 | 10% |
| 图片 | 5% |

## 报告结构

### 执行摘要
- 整体SEO健康评分（0-100）
- 检测到的业务类型
- 5个关键问题
- 5个快速获胜

### 技术SEO
- 爬取问题
- 索引问题
- 安全问题
- 核心网页指标状态

### 内容质量
- E-E-A-T评估
- 薄内容页面
- 重复内容问题
- 可读性评分

### 页面内SEO
- 标题标签问题
- 元描述问题
- 标题结构
- 内部链接差距

### 模式与结构化数据
- 当前实现
- 验证错误
- 缺失机会

### 性能
- LCP、INP、CLS分数
- 资源优化需求
- 第三方脚本影响

### 图片
- 缺失替代文本
- 过大的图片
- 格式建议

### AI搜索准备情况
- 可引用性分数
- 结构改进
- 权威信号

## 优先级定义

- **关键**：阻止索引或导致处罚（立即修复）
- **高**：显著影响排名（1周内修复）
- **中**：优化机会（1个月内修复）
- **低**：可要可不要（待办）

## DataForSEO集成（可选）

如果DataForSEO MCP工具可用，与现有子代理一起生成`seo-dataforseo`代理，以用实时数据丰富审计：真实SERP位置、反向链接数据（含垃圾分数）、页面内分析（Lighthouse）、商家列表和AI可见性检查（ChatGPT爬虫、LLM提及）。

## Google API集成（可选）

如果配置了Google API凭证（`"${CLAUDE_PLUGIN_ROOT}/scripts/claude-seo" run google_auth.py --check`），生成`seo-google`代理，以用真实Google字段数据丰富审计：CrUX核心网页指标（替代仅实验室估计）、GSC URL索引状态、搜索性能（点击、展示、CTR）和GA4自然流量趋势。性能（CWV）类别得分从字段数据中受益最大。

## Matomo集成（可选）

如果配置了Matomo凭证（`"${CLAUDE_PLUGIN_ROOT}/scripts/claude-seo" run matomo_auth.py --check`），生成`seo-matomo`代理，以用自托管分析丰富审计：自然访问趋势、顶级着陆页、设备和国家细分、渠道/搜索引擎细分和自然关键词。当仅配置Matomo时作为GA4替代方案，或当GA4和Matomo都存在时作为补充。由于细分差异（`referrerType==search` vs `sessionDefaultChannelGroup == "Organic Search"`）和归因窗口规则，Matomo数字将不会与GA4完全一致。

## Google更新关联

在将流量或排名变化归因于任何事物之前，列出该窗口中确认的Google更新：

```bash
"${CLAUDE_PLUGIN_ROOT}/scripts/claude-seo" run seo_updates.py --since <yyyy-mm> --json
```

每个条目都引用一个Google拥有的URL。如果`freshness.stale`为true，则说明账本可能遗漏了最近的更新，并在得出结论之前检查status.search.google.com。日期重叠是一个假设，永远不会是因果的证据。

## 错误处理

| 情景 | 操作 |
|----------|--------|
| URL无法访问（DNS失败、连接拒绝） | 清晰地报告错误。不要猜测网站内容。建议用户验证URL并重试。 |
| robots.txt阻止爬取 | 报告被阻止的路径。仅分析可访问页面，并在报告中注明限制。 |
| 速率限制（429响应） | 减少并发请求并退避。报告部分结果，并注明哪些部分未完成。 |
| 大型网站超时（500+页） | 在超时限制内限制爬取。报告已爬取页面的发现，并估计网站范围。 |
| 子代理在大型网站上达到`maxTurns`预算 | 发现不会丢失：每个审计子代理在第一次分析后写入部分`output_dir/findings/*.md`，并在完成前用完整发现覆盖它。读取任何存在的发现文件并将其合并到报告中，并注明可能是部分结果。 |
