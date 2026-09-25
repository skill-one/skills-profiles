# 博客 Google：博客性能的 Google API 数据

直接访问 Google 的 SEO API 进行博客性能分析。提供真实的 Chrome 用户指标、索引状态、搜索性能、实体分析、YouTube 视频发现、关键词量以及 PDF/HTML 性能报告。

大多数集成在其文档中规定的配额内免费使用。Cloud Natural Language 需要计费，并且在其免费月度层级之后可能会产生费用。Google Ads 需要符合资格的账户和开发者令牌。未经明确用户批准，切勿启用计费或进行付费请求。

## 前置条件

**在运行任何命令前始终检查凭证：**
```bash
python3 skills/blog-google/scripts/run.py google_auth --check --json
```

**配置文件：** `~/.config/claude-seo/google-api.json`（与 claude-seo 共享）
```json
{
  "api_key": "YOUR_GOOGLE_API_KEY",
  "oauth_client_path": "/path/to/client_secret.json",
  "default_property": "sc-domain:example.com",
  "ga4_property_id": "properties/123456789",
  "ads_developer_token": "...",
  "ads_customer_id": "123-456-7890",
  "ads_login_customer_id": "123-456-7890"
}
```

如果缺失，请阅读 `references/auth-setup.md` 并引导用户进行设置。

### 凭证层级

| 层级 | 检测 | 可用命令 |
|------|------|----------|
| **0** (API Key) | `api_key` 存在 | `pagespeed`, `crux`, `crux-history`, `youtube`, `nlp` |
| **1** (OAuth/SA) | + OAuth 令牌或服务账户 | 层级 0 + `gsc`, `inspect`, `index` |
| **2** (完整) | + `ga4_property_id` 配置 | 层级 1 + `ga4` |
| **3** (广告) | + `ads_developer_token` + `ads_customer_id` | 层级 2 + `keywords` |

在运行命令前始终传达检测到的层级。

## 快速参考

| 命令 | 它的作用 | 层级 |
|------|----------|------|
| `/blog google setup` | 检查/配置 API 凭证 |: |
| `/blog google pagespeed <url>` | PSI Lighthouse + CrUX 字段数据 | 0 |
| `/blog google crux <url>` | 仅 CrUX 字段数据（p75 指标） | 0 |
| `/blog google crux-history <url>` | 25 周的 CWV 趋势分析 | 0 |
| `/blog google youtube <query>` | YouTube 视频搜索（观看次数、点赞数、时长） | 0 |
| `/blog google nlp <url-or-text>` | NLP 实体提取 + 情感分析 | 0 |
| `/blog google gsc <property>` | 搜索控制台：点击次数、展示次数、CTR、位置 | 1 |
| `/blog google inspect <url>` | URL 检查：索引状态、规范 | 1 |
| `/blog google index <url>` | 将 URL 提交到索引 API | 1 |
| `/blog google ga4 [property-id]` | GA4 有机流量报告 | 2 |
| `/blog google keywords <seed>` | 从 Google Ads 关键词规划师获取关键词创意 | 3 |
| `/blog google report <type>` | PDF/HTML 性能报告 |: |
| `/blog google quotas` | 显示所有 API 的速率限制 |: |

---

## PageSpeed + CrUX

### `/blog google pagespeed <url>`

已发布的博客文章的 Lighthouse 实验室数据 + CrUX 字段数据的组合。

**脚本：** `python3 skills/blog-google/scripts/run.py pagespeed_check <url> --json`
**参考：** `references/api-reference.md`

输出合并了实验室分数（点时 Lighthouse）和字段数据（28 天的 Chrome 用户指标）。CrUX 首先尝试 URL 级别的检测，然后回退到域名级别的检测。

### `/blog google crux <url>`

仅 CrUX 字段数据（不运行 Lighthouse）。更快。

**脚本：** `python3 skills/blog-google/scripts/run.py pagespeed_check <url> --crux-only --json`

### `/blog google crux-history <url>`

25 周的 CrUX 历史趋势。显示 CWV 指标是否在改善、稳定或退化。

**脚本：** `python3 skills/blog-google/scripts/run.py crux_history <url> --json`

---

## 搜索控制台

### `/blog google gsc <property>`

搜索分析：过去 28 天的点击次数、展示次数、CTR、位置。

**脚本：** `python3 skills/blog-google/scripts/run.py gsc_query --property <property> --json`
**默认：** 28 天，维度=query,page, 类型=web, 限制=1000。

包括快速赢取检测：位置 4-10 的查询具有高展示次数。

专用的搜索控制台生成式 AI 报告是在搜索控制台 UI 中逐步、子集推出的。它们具有独立的搜索和发现视图；搜索视图涵盖 AI 概览和 AI 模式。不要承诺这些专用的视图中的点击次数、查询或 API 检索。在 Google 文档 API 之前，将此功能报告为 `SKIPPED` 或不可用，并引导用户使用 UI。

Google 7 月 29 日的 Search Central 声明称，Instagram、TikTok、X 和 YouTube 的搜索控制台平台属性在全球范围内可用。当前的 Help Center 仍然表示逐步推出。报告此为 Google 源的冲突，在用户的账户中验证可用性，并且不要声称 `/blog google gsc` 通过当前 API 检索这些平台报告。

### `/blog google inspect <url>`

URL 检查：来自 Google 的真实索引状态。

**脚本：** `python3 skills/blog-google/scripts/run.py gsc_inspect <url> --json`

返回：结论（PASS/FAIL）、覆盖状态、robots.txt 状态、索引状态、页面获取状态、规范选择、移动可用性、丰富结果。

在规范修复后，Google 可能会在重复集群中保留 URL长达两周。如果实现现在正确且修复在窗口期内，请报告 `PENDING_REEVALUATION` 而不是立即失败。搜索控制台的请求索引功能受配额限制；将其保留用于重要的 URL。

对于批量检查：`python3 skills/blog-google/scripts/run.py gsc_inspect --batch <file> --json`

---

## 索引 API

### `/blog google index <url>`

通过索引 API 通知 Google URL 更新。

**脚本：** `python3 skills/blog-google/scripts/run.py indexing_notify <url> --json`
**参考：** `references/api-reference.md`

索引 API 官方用于 JobPosting 和 BroadcastEvent/VideoObject 页面。始终告知用户此限制。每日配额：200 发布请求。不要将其呈现为 URL 检查的请求索引功能的通用替代品。

对于批量：`python3 skills/blog-google/scripts/run.py indexing_notify --batch <file> --json`

---

## GA4 流量

### `/blog google ga4 [property-id]`

有机流量报告：每日会话数、用户数、页面浏览量、跳出率、参与度。

**脚本：** `python3 skills/blog-google/scripts/run.py ga4_report --property <id> --json`
**默认：** 28 天，过滤到有机搜索渠道组。

对于顶级着陆页：`python3 skills/blog-google/scripts/run.py ga4_report --property <id> --report top-pages --json`

---

## YouTube（视频发现）

YouTube 研究可以添加有用的、相关的媒体和分发上下文。任何第三方可见性相关性都是观察性的，不是 Google 排名或引用要求。免费，仅 API 密钥。由 blog-write 和 blog-rewrite 用于视频嵌入。

### `/blog google youtube <query>`

搜索 YouTube 以查找与博客主题相关的视频。

**脚本：** `python3 skills/blog-google/scripts/run.py youtube_search search "<query>" --json`
**配额：** 每次搜索 100 个单位（每天 10,000 个单位免费）。

返回：标题、频道、观看次数、点赞数、时长、描述、标签。

对于视频详情 + 评论：`python3 skills/blog-google/scripts/run.py youtube_search video <video_id> --json`

---

## NLP 内容分析

Google 的实体和情感分析可以支持主题和编辑审查。它不会暴露排名系统分数，E-E-A-T 也不是 Google 的数值排名因素。

### `/blog google nlp <url-or-text>`

完整的 NLP 分析：实体、情感、内容分类。

**脚本：** `python3 skills/blog-google/scripts/run.py nlp_analyze --url <url> --json`
**免费层级：** 每月 5,000 个单位。需要在 GCP 项目上启用计费。

对于实体提取仅：`python3 skills/blog-google/scripts/run.py nlp_analyze --url <url> --features entities --json`

---

## 关键词研究（Google Ads）

黄金标准关键词量数据。需要 Google Ads 账户（层级 3）。

### `/blog google keywords <seed>`

从种子术语生成关键词创意，用于博客主题研究。

**脚本：** `python3 skills/blog-google/scripts/run.py keyword_planner ideas "<seed>" --json`

对于量级查询：`python3 skills/blog-google/scripts/run.py keyword_planner volume "<kw1>,<kw2>" --json`

---

## 报告

### `/blog google report <type>`

生成带有图表和表格的 PDF/HTML 报告。

**脚本：** `python3 skills/blog-google/scripts/run.py google_report --type <type> --data <json> --domain <domain> --format pdf`

| 类型 | 输入 | 输出 |
|------|------|------|
| `cwv-audit` | PSI + CrUX + CrUX History 数据 | 核心网络振动审计，带有仪表盘和时间线 |
| `gsc-performance` | GSC 查询数据 | 搜索控制台报告，带有查询表格 |
| `indexation` | 批量检查数据 | 索引状态，带有覆盖甜甜圈 |
| `full` | 所有数据组合 | 综合性 Google SEO 报告 |

**注意：** PDF 生成需要系统库：`sudo apt install libpango1.0-dev libcairo2-dev`。如果 WeasyPrint 不可用或 PDF 渲染失败，则回退到 HTML。

---

## 速率限制

| API | 每分钟 | 每天限制 | 认证 |
|------|--------|----------|------|
| PSI v5 | 240 QPM | 25,000 QPD | API 密钥 |
| CrUX + History | 150 QPM（共享） | 无限 | API 密钥 |
| GSC 搜索分析 | 1,200 QPM/站点 | 30M QPD | 服务账户 |
| GSC URL 检查 | 600 QPM | 2,000 QPD/站点 | 服务账户 |
| 索引 API | 380 RPM | 每天 200 发布 | 服务账户 |
| GA4 数据 API | 10 并发（50 用于 360） | 每天 200K 核心令牌（2M 用于 360） | 服务账户 |
| YouTube 数据 |: | 每天 10,000 个单位 | API 密钥 |
| NLP API |: | 每月 5,000 个单位 | API 密钥（计费） |

阅读 `references/rate-limits-quotas.md` 获取详细的配额管理。

## 博客工作流集成

此技能既是用户可调用的（`/blog google pagespeed`）也是其他博客子技能内部可调用的：

- **blog-seo-check**：在已发布的文章 URL 上运行 PSI + CrUX，以获取实时 CWV 数据
- **blog-rewrite**：NLP 实体分析，以识别 E-E-A-T 实体差距
- **blog-geo**：搜索控制台性能数据，用于真实的搜索外观洞察
- **blog-audit**：跨所有已发布博客 URL 执行批量 CWV + 索引检查
- **blog-write / blog-rewrite**：YouTube 搜索用于视频嵌入

在凭证未配置时优雅回退。

## 报告模板

当工作流请求持久的可读报告时，使用捆绑的模板。将不可用的账户数据标记为 `SKIPPED`；切勿用估计指标填充空部分。

- `assets/templates/cwv-audit-report.md` 用于 PageSpeed 和 CrUX 证据。
- `assets/templates/gsc-performance-report.md` 用于搜索分析导出。
- `assets/templates/indexation-status-report.md` 用于 URL 检查证据。

## 技术说明

- INP 在 2024 年 3 月 12 日取代了 FID。切勿引用 FID。
- CrUX 中的 CLS 值是字符串编码的（例如，"0.05"）。脚本处理解析。
- CrUX 404 = 不足的 Chrome 流量，不是认证错误。
- 搜索分析数据有 2-3 天的滞后。
- 索引 API 官方仅用于 JobPosting/BroadcastEvent 页面。
- 大多数集成在配额内免费使用。Cloud Natural Language 需要计费，并且可能会产生费用；Google Ads 需要账户和开发者令牌访问。
- 在诊断命名更新、规范更改、Discover 可见性、Google 生成式 AI 报告、平台属性、首选来源、AMP 或爬虫字节限制问题时，请阅读 `references/search-currentness.md`。
- 命名更新的日期不能证明导致单个网站更改的原因。在推出后等待一周再比较数据，并分别比较 Web、图像、视频和新闻性能。
- Googlebot 仅处理支持的文件的前 2MB 和 PDF 的前 64MB。保留关键元数据和主要内容在截止点之前。

## 错误处理

| 情景 | 操作 |
|------|------|
| 无凭证配置 | 运行 `/blog google setup`。列出层级 0 命令（仅 API 密钥）。 |
| 服务账户缺乏 GSC 访问 | 将 `client_email` 添加到 GSC > 设置 > 用户 > 添加。 |
| CrUX 数据不可用（404） | 不足的 Chrome 流量。使用 PSI 实验室数据作为回退。 |
| GA4 属性未找到 | 在 GA4 Admin > 属性详情中查找属性 ID。 |
| 索引 API 配额超出 | 每天 200 个发布限制。优先处理最重要的 URL。 |
| 速率限制（429） | 等待并使用指数退避重试。 |
