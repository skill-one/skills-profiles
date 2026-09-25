# Google SEO APIs

直接访问 Google 自家的 SEO 数据。连接了基于爬虫的分析（现有的 claude-seo 技能）与 Google 的实时字段数据：实际的 Chrome 用户指标、真实的索引状态、搜索表现和自然流量。

所有 API 都是免费的。设置需要一个带有 API 密钥和/或服务账户的 Google Cloud 项目——运行 `/seo google setup` 获取分步说明。

## 前置条件

执行任何命令前，检查凭证：
```bash
"${CLAUDE_PLUGIN_ROOT}/scripts/claude-seo" run google_auth.py --check --json
```

配置文件：`~/.config/claude-seo/google-api.json`
```json
{
  "service_account_path": "/path/to/service_account.json",
  "api_key": "<GOOGLE_API_KEY>",
  "default_property": "sc-domain:example.com",
  "ga4_property_id": "properties/123456789"
}
```

如果缺失，请阅读 `references/auth-setup.md` 并引导用户完成设置。

### 凭证等级

| 等级 | 检测 | 可用命令 |
|------|-----|---------|
| **0** (API 密钥) | `api_key` 存在 | `pagespeed`, `crux`, `crux-history`, `youtube`, `nlp` |
| **1** (OAuth/SA) | + OAuth 令牌或服务账户 | 等级 0 + `gsc`, `inspect`, `sitemaps`, `index` |
| **2** (完整) | + `ga4_property_id` 配置 | 等级 1 + `ga4`, `ga4-pages` |
| **3** (广告) | + `ads_developer_token` + `ads_customer_id` | 等级 2 + `keywords`, `volume` |

运行命令前始终传达检测到的等级。

## 快速参考

| 命令 | 功能 | 等级 |
|------|-----|-----|
| `/seo google setup` | 检查/配置 API 凭证 | -- |
| `/seo google pagespeed <url>` | PSI Lighthouse + CrUX 字段数据 | 0 |
| `/seo google crux <url>` | 仅 CrUX 字段数据（p75 指标） | 0 |
| `/seo google crux-history <url>` | 25 周CWV趋势分析 | 0 |
| `/seo google gsc <property>` | 搜索控制台：点击量、展示量、CTR、位置 | 1 |
| `/seo google inspect <url>` | URL 检查：索引状态、规范、爬取信息 | 1 |
| `/seo google inspect-batch <file>` | 从文件批量检查 URL | 1 |
| `/seo google sitemaps <property>` | GSC 站点地图状态 | 1 |
| `/seo google index <url>` | 将 URL 提交到索引 API | 1 |
| `/seo google index-batch <file>` | 批量提交最多 200 个 URL | 1 |
| `/seo google ga4 [property-id]` | GA4 自然流量报告 | 2 |
| `/seo google ga4-pages [property-id]` | 顶级自然流量着陆页 | 2 |
| `/seo google youtube <query>` | YouTube 视频搜索（观看量、点赞数、时长） | 0 |
| `/seo google youtube-video <id>` | YouTube 视频详情 + 顶级评论 | 0 |
| `/seo google nlp <url-or-text>` | NLP 实体提取 + 情感 + 分类 | 0 |
| `/seo google entities <url-or-text>` | 仅实体分析（用于 E-E-A-T） | 0 |
| `/seo google keywords <seed>` | 从 Google Ads 关键词规划师获取关键词创意 | 3 |
| `/seo google volume <keywords>` | 从关键词规划师获取搜索量 | 3 |
| `/seo google entity <query>` | 知识图谱实体检查 | 0 |
| `/seo google safety <url>` | Web 风险 URL 安全检查 | 0 |
| `/seo google quotas` | 显示所有 API 的速率限制 | -- |

---

## PageSpeed + CrUX

### `/seo google pagespeed <url>`

结合 Lighthouse 实验室数据 + CrUX 字段数据。

**脚本：** `"${CLAUDE_PLUGIN_ROOT}/scripts/claude-seo" run pagespeed_check.py <url> --json`
**参考：** `references/pagespeed-crux-api.md`
**默认：** 移动端 + 桌面端策略，所有 Lighthouse 类别。

输出合并实验室分数（点时 Lighthouse）与字段数据（28 天 Chrome 用户指标）。CrUX 优先尝试 URL 级别，失败后回退到域名级别。

### `/seo google crux <url>`

仅 CrUX 字段数据（不运行 Lighthouse）。更快。

**脚本：** `"${CLAUDE_PLUGIN_ROOT}/scripts/claude-seo" run pagespeed_check.py <url> --crux-only --json`

### `/seo google crux-history <url>`

25 周CrUX 历史趋势。显示 CWV 指标是否改善、稳定或恶化。

**脚本：** `"${CLAUDE_PLUGIN_ROOT}/scripts/claude-seo" run crux_history.py <url> --json`
**参考：** `references/pagespeed-crux-api.md`

输出包括每项指标的趋势方向、百分比变化和每周 p75 值。

---

## 搜索控制台

### `/seo google gsc <property>`

搜索分析：过去 28 天的点击量、展示量、CTR、位置。

**脚本：** `"${CLAUDE_PLUGIN_ROOT}/scripts/claude-seo" run gsc_query.py --property <property> --json`
**参考：** `references/search-console-api.md`
**默认：** 28 天，维度=query,page, 类型=web, 限制=1000。

对于欧盟站点，在解释 CTR 或 GA4 下降前，请阅读 `references/dma-consent-mode-v2.md`：DMA 和 Consent Mode v2 改变了搜索控制台和 GA4 记录的内容。

包括快速见效检测：位置 4-10 且展示量高的查询。
`totals` 块来自一个无维度的聚合查询，因为查询级行可能省略匿名低流量数据。当 `totals_complete` 为 true 时，将 totals 视为仅站点范围。`--limit` 限制返回的维度行数，而不是每个分页请求的大小。

> **GSC 中的 AI 功能（2026 年）：**
> - **生成式 AI 性能报告**（2026-06-03 启用），一个专门用于 AI 概述 + AI 模式可见性的视图。**仅展示量**（无点击量/CTR/位置/查询）；维度=页面/国家/设备/日期（太平洋时间）；1,000 行限制；最新数据为初步数据；还存在一个 Discover gen-AI 报告。自 2026-08-31 起对全球所有网站可用（2026-06-03 对部分网站启用）；日期支持小时、日、周和月粒度。
> - **AI 模式已合并到标准性能总计**（网络搜索类型），AI 模式中的点击量（外部链接点击量）和展示量计入正常报告，因此您**无法**从总计中清晰分离“经典”和“AI”流量。使用生成式 AI 报告获取仅展示量的 AI 可见性。
> - **数据可靠性注意事项：** 由于 GSC 记录错误，**展示量、CTR 和平均位置**从 2025-05-13 到 2026-04-27 不可靠（点击量不受影响；固定向前，**无回填**）。对跨越该窗口的展示量/CTR/位置趋势要谨慎；修复后会出现明显的展示量下降。

> **平台属性（2026 年）：** 搜索控制台可以将已验证的 TikTok、Instagram、X 和 YouTube 账户作为独立属性显示。单独验证每个账户，除非它通过已声明的搜索配置文件添加。仅用于 Google 搜索性能，不能作为平台自身分析的替代品。来源：
> developers.google.com/search/docs/monitor-debug/analyze-social-video-content

### `/seo google inspect <url>`

URL 检查：来自 Google 的实时索引状态。

**脚本：** `"${CLAUDE_PLUGIN_ROOT}/scripts/claude-seo" run gsc_inspect.py <url> --json`

返回：结论（PASS/FAIL）、覆盖状态、robots.txt 状态、索引状态、页面获取状态、规范选择、移动可用性、丰富结果。

### `/seo google inspect-batch <file>`

从文件批量检查（每行一个 URL）。速率限制为每天每个站点 2,000 个。

**脚本：** `"${CLAUDE_PLUGIN_ROOT}/scripts/claude-seo" run gsc_inspect.py --batch <file> --json`

### `/seo google sitemaps <property>`

列出已提交的站点地图及其状态、错误、警告。站点地图内容报告仅提交计数；URL 检查 API 是判断特定 URL 是否被索引的真相。

**脚本：** `"${CLAUDE_PLUGIN_ROOT}/scripts/claude-seo" run gsc_query.py sitemaps --property <property> --json`

---

## 索引 API

### `/seo google index <url>`

通知 Google URL 更新。

**脚本：** `"${CLAUDE_PLUGIN_ROOT}/scripts/claude-seo" run indexing_notify.py <url> --json`
**参考：** `references/indexing-api.md`

索引 API 官方用于 JobPosting 和 BroadcastEvent/VideoObject 页面。
始终告知用户此限制。每日配额：200 发布请求。

### `/seo google index-batch <file>`

从文件批量提交 URL。跟踪配额使用情况。

**脚本：** `"${CLAUDE_PLUGIN_ROOT}/scripts/claude-seo" run indexing_notify.py --batch <file> --json`

---

## GA4 流量

### `/seo google ga4 [property-id]`

自然流量报告：每日会话量、用户数、页面浏览量、跳出率、参与度。

**脚本：** `"${CLAUDE_PLUGIN_ROOT}/scripts/claude-seo" run ga4_report.py --property <id> --json`
**参考：** `references/ga4-data-api.md`
**默认：** 28 天，过滤到自然搜索渠道组。

> **GA4 "AI 助手" 渠道（约 2026-05-13 生效）：** GA4 添加了本地的 *AI 助手* 默认渠道组。由受识别的 AI 助手转介的会话将 `medium=ai-assistant`。Google 识别的来源是 **ChatGPT、Gemini、Claude、Deepseek、Copilot、Grok**，该渠道**排除** Google AI 概述 / AI 模式。**如有需要，请单独验证 Perplexity**；不支持的来源可能保留在 Referral 中，大多数 AI 会话没有来源，并归入 **Direct**，因此此渠道低估了 AI 流量。向前兼容，无回填。

### `/seo google ga4-pages [property-id]`

按会话量排名的顶级自然流量着陆页。

**脚本：** `"${CLAUDE_PLUGIN_ROOT}/scripts/claude-seo" run ga4_report.py --property <id> --report top-pages --json`

---

## YouTube（视频 SEO）

一些第三方研究报告称，YouTube 提及与 AI 可见性之间存在 0.737 的相关性。将其视为依赖方法论的信号。免费，仅 API 密钥。

### `/seo google youtube <query>`

在 YouTube 上搜索视频。返回标题、频道、观看量、点赞数、时长。

**脚本：** `"${CLAUDE_PLUGIN_ROOT}/scripts/claude-seo" run youtube_search.py search "<query>" --json`
**参考：** `references/youtube-api.md`
**配额：** 每次搜索 100 个单位（每天 10,000 个单位免费）。

### `/seo google youtube-video <video_id>`

详细视频信息 + 标签 + 顶级 10 条评论。

**脚本：** `"${CLAUDE_PLUGIN_ROOT}/scripts/claude-seo" run youtube_search.py video <video_id> --json`
**配额：** 2 个单位（视频详情 + 评论）。

---

## NLP 内容分析

Google NLP 实体/情感输出用于内部内容质量检查。不要将其视为 Google E-E-A-T 评分。

### `/seo google nlp <url-or-text>`

完整 NLP 分析：实体、情感、内容分类。

**脚本：** `"${CLAUDE_PLUGIN_ROOT}/scripts/claude-seo" run nlp_analyze.py --url <url> --json` 或 `--text "...""`
**参考：** `references/nlp-api.md`
**免费套餐：** 每月 5,000 个单位。需要在 GCP 项目上启用计费。

### `/seo google entities <url-or-text>`

仅实体提取（更快，配额较少）。

**脚本：** `"${CLAUDE_PLUGIN_ROOT}/scripts/claude-seo" run nlp_analyze.py --url <url> --features entities --json`

---

## 关键词研究（Google Ads）

黄金标准关键词量数据。需要 Google Ads 账户。

### `/seo google keywords <seed>`

从种子术语生成关键词创意。

**脚本：** `"${CLAUDE_PLUGIN_ROOT}/scripts/claude-seo" run keyword_planner.py ideas "<seed>" --json`
**参考：** `references/keyword-planner-api.md`
**需要：** 配置中包含 Ads 开发者令牌 + 客户 ID（等级 3）。

### `/seo google volume <keywords>`

特定关键词的搜索量（逗号分隔）。

**脚本：** `"${CLAUDE_PLUGIN_ROOT}/scripts/claude-seo" run keyword_planner.py volume "<kw1>,<kw2>" --json`

---

## 补充

### `/seo google entity <query>`

知识图谱实体检查。验证品牌存在。

**参考：** `references/supplementary-apis.md`
使用带有 API 密钥的知识图谱搜索 API。

### `/seo google safety <url>`

Web 风险 API 检查，检测恶意软件/社会工程标志。

**参考：** `references/supplementary-apis.md`

### `/seo google quotas`

显示速率限制表。阅读 `references/rate-limits-quotas.md`。

---

## 报告

执行任何分析命令后，提供生成 PDF/HTML 报告的选项。

### `/seo google report <type>`

生成带有图表和分析的专业 PDF 报告。

**脚本：** `"${CLAUDE_PLUGIN_ROOT}/scripts/claude-seo" run google_report.py --type <type> --data <json> --domain <domain> --format pdf`

| 类型 | 输入 | 输出 |
|------|-----|-----|
| `cwv-audit` | PSI + CrUX + CrUX History 数据 | 核心网络指标审计，带有仪表盘、时间线和分布 |
| `gsc-performance` | GSC 查询数据 | 搜索控制台报告，带有查询表格、快速见效 |
| `indexation` | 批量检查数据 | 索引状态，带有覆盖度环形图 |
| `full` | 所有数据合并 | 综合性 Google SEO 报告（所有部分） |

**工作流程：**
1. 运行数据收集命令（pagespeed, gsc, inspect-batch, 等）
2. 将 JSON 输出保存到文件：`"${CLAUDE_PLUGIN_ROOT}/scripts/claude-seo" run pagespeed_check.py <url> --json > data.json`
3. 生成报告：`"${CLAUDE_PLUGIN_ROOT}/scripts/claude-seo" run google_report.py --type cwv-audit --data data.json --domain <domain>`

**约定：** 完成分析后，建议："生成报告？使用 `/seo google report <type>`"

---

## 速率限制

| API | 每分钟 | 每天限制 | 认证 |
|-----|-------|---------|------|
| PSI v5 | 240 QPM | 25,000 QPD | API 密钥 |
| CrUX + History | 150 QPM (共享) | 无限 | API 密钥 |
| GSC 搜索分析 | 1,200 QPM/站点 | 30M QPD | 服务账户 |
| GSC URL 检查 | 600 QPM | 2,000 QPD/站点 | 服务账户 |
| 索引 API | 380 RPM | 每天发布 200 次 | 服务账户 |
| GA4 数据 API | 10 个并发 | 每天 ~25K 个令牌 | 服务账户 |

## 跨技能集成

- **seo-audit**：生成 `seo-google` 代理，用于实时 CWV + 索引数据（有条件）
- **seo-technical**：使用 pagespeed_check.py 获取真实的 CWV 字段数据
- **seo-performance**：CrUX 字段数据补充 Lighthouse 实验室数据
- **seo-sitemap**：GSC 站点地图状态显示提交计数、错误和警告；使用 URL 检查获取索引真相
- **seo-content**：GSC 查询数据提供关键词定位信息
- **seo-geo**：使用 GSC 生成式 AI 性能报告和 AI 概述/AI 模式/Discover gen-AI 包含/排除控制（如有可用）

## 输出格式

- CWV 指标：交通灯评级（良好 / 需要改进 / 差）
- 性能报告：可排序列的表格
- 始终包含数据新鲜度说明
- 将报告保存为 `GOOGLE-API-REPORT-{domain}.md`
- Markdown/LLM 模板在 `assets/templates/`：`cwv-audit-report.md`, `gsc-performance-report.md`, `indexation-status-report.md`；与 `google_report.py` 的 PDF 管道不同

## 技术说明

- INP 于 2024 年 3 月 12 日取代了 FID。永远不要引用 FID。
- CrUX 中的 CLS 值是字符串编码的（例如，"0.05"）。脚本处理解析。
- CrUX 404 = 流量不足，不是认证错误。
- 搜索分析数据有 2-3 天的滞后。
- `round_trip_time` 于 2025 年 2 月在 CrUX 中取代了 `effectiveConnectionType`。
- 自 2025 年起，自定义搜索 JSON API 已停止对新客户开放。

## 错误处理

| 场景 | 操作 |
|------|------|
| 未配置凭证 | 运行 `/seo google setup`。列出仅使用 API 密钥即可工作的等级 0 命令。 |
| 服务账户缺乏 GSC 访问权限 | 报告错误。指示：在 GSC > 设置 > 用户 > 添加中添加 `client_email`。 |
| CrUX 数据不可用（404） | 报告流量不足。建议使用 PSI 实验室数据作为备用。 |
| GA4 属性未找到 | 报告错误。显示如何在 GA4 Admin > 属性详情中找到属性 ID。 |
| 索引 API 配额超出 | 报告每天 200 次限制。建议优先处理最重要的 URL。 |
| 速率限制（429） | 等待并使用指数退避重试。报告哪个 API 达到限制。 |
