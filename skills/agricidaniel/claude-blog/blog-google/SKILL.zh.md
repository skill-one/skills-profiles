---
name: blog-google
description: 为博客性能集成的 Google API：PageSpeed Insights、CrUX 核心网络生命体征（含 25 周历史数据）、搜索控制台性能、URL 检查、索引 API、GA4 有机流量、NLP 实体分析（用于 E-E-A-T）、YouTube 视频搜索嵌入以及 Google Ads 关键词规划器。根据凭证等级（API 密钥、OAuth/服务账户、GA4、Ads）分阶段启用功能。配置信息与 claude-seo 共享，存储于 `~/.config/claude-seo/google-api.json`。当用户输入“google data”、“page speed”、“core web vitals”、“search console”、“indexation”、“GA4”、“keyword research”、“nlp entities”、“blog performance”、“youtube search”、“google api setup”时使用。
---

# 博客谷歌：博客性能的谷歌API数据

直接访问谷歌的SEO API进行博客性能分析。提供真实的Chrome用户指标、索引状态、搜索性能、实体分析、YouTube视频发现、关键词量以及PDF/HTML性能报告。

所有API在正常使用级别下都是免费的。设置需要一个带有API密钥和/或服务账户的谷歌云项目。

## 前置条件

**在运行任何命令前始终检查凭证：**
```bash
python3 skills/blog-google/scripts/run.py google_auth --check --json
```

**配置文件：** `~/.config/claude-seo/google-api.json`（与claude-seo共享）
```json
{
  "api_key": "AIzaSy...",
  "oauth_client_path": "/path/to/client_secret.json",
  "default_property": "sc-domain:example.com",
  "ga4_property_id": "properties/123456789",
  "ads_developer_token": "...",
  "ads_customer_id": "123-456-7890",
  "ads_login_customer_id": "123-456-7890"
}
```

如果缺失，请阅读`references/auth-setup.md`并引导用户完成设置。

### 凭证级别

| 级别 | 检测 | 可用命令 |
|------|-----------|-------------------|
| **0** (API密钥) | `api_key` 存在 | `pagespeed`, `crux`, `crux-history`, `youtube`, `nlp` |
| **1** (OAuth/SA) | + OAuth令牌或服务账户 | 级别0 + `gsc`, `inspect`, `index` |
| **2** (完整) | + `ga4_property_id` 配置 | 级别1 + `ga4` |
| **3** (广告) | + `ads_developer_token` + `ads_customer_id` | 级别2 + `keywords` |

在运行命令前始终传达检测到的级别。

## 快速参考

| 命令 | 它的作用 | 级别 |
|---------|-------------|------|
| `/blog google setup` | 检查/配置API凭证 |: |
| `/blog google pagespeed <url>` | PSI Lighthouse + CrUX字段数据 | 0 |
| `/blog google crux <url>` | 仅CrUX字段数据（p75指标） | 0 |
| `/blog google crux-history <url>` | 25周CWV趋势分析 | 0 |
| `/blog google youtube <query>` | YouTube视频搜索（观看次数、点赞数、时长） | 0 |
| `/blog google nlp <url-or-text>` | NLP实体提取 + 情感分析 | 0 |
| `/blog google gsc <property>` | 搜索控制台：点击次数、展示次数、CTR、位置 | 1 |
| `/blog google inspect <url>` | URL检查：索引状态、规范 | 1 |
| `/blog google index <url>` | 提交URL到索引API | 1 |
| `/blog google ga4 [property-id]` | GA4自然流量报告 | 2 |
| `/blog google keywords <seed>` | 来自谷歌广告关键词规划器的关键词创意 | 3 |
| `/blog google report <type>` | PDF/HTML性能报告 |: |
| `/blog google quotas` | 显示所有API的速率限制 |: |

---

## PageSpeed + CrUX

### `/blog google pagespeed <url>`

已发布博客文章的综合Lighthouse实验室数据 + CrUX字段数据。

**脚本：** `python3 skills/blog-google/scripts/run.py pagespeed_check <url> --json`
**参考：** `references/api-reference.md`

输出合并了实验室分数（点时Lighthouse）与字段数据（28天Chrome用户指标）。CrUX首先尝试URL级，然后回退到域名级。

### `/blog google crux <url>`

仅CrUX字段数据（不运行Lighthouse）。更快。

**脚本：** `python3 skills/blog-google/scripts/run.py pagespeed_check <url> --crux-only --json`

### `/blog google crux-history <url>`

25周CrUX历史趋势。显示CWV指标是否改善、稳定或退化。

**脚本：** `python3 skills/blog-google/scripts/run.py crux_history <url> --json`

---

## 搜索控制台

### `/blog google gsc <property>`

搜索分析：过去28天的点击次数、展示次数、CTR、位置。

**脚本：** `python3 skills/blog-google/scripts/run.py gsc_query --property <property> --json`
**默认：** 28天，维度=query,page,类型=web,限制=1000。

包括快速见效检测：位置4-10的查询具有高展示次数。

### `/blog google inspect <url>`

URL检查：来自谷歌的真实索引状态。

**脚本：** `python3 skills/blog-google/scripts/run.py gsc_inspect <url> --json`

返回：判定（PASS/FAIL）、覆盖状态、robots.txt状态、索引状态、页面获取状态、规范选择、移动可用性、丰富结果。

对于批量检查：`python3 skills/blog-google/scripts/run.py gsc_inspect --batch <file> --json`

---

## 索引API

### `/blog google index <url>`

通知谷歌URL更新。提交新博客文章以加快索引。

**脚本：** `python3 skills/blog-google/scripts/run.py indexing_notify <url> --json`
**参考：** `references/api-reference.md`

索引API正式用于JobPosting和BroadcastEvent/VideoObject页面。
始终告知用户此限制。每日配额：200发布请求。

对于批量：`python3 skills/blog-google/scripts/run.py indexing_notify --batch <file> --json`

---

## GA4流量

### `/blog google ga4 [property-id]`

自然流量报告：每日会话数、用户数、页面浏览量、跳出率、参与度。

**脚本：** `python3 skills/blog-google/scripts/run.py ga4_report --property <id> --json`
**默认：** 28天，过滤到自然搜索渠道组。

对于顶级着陆页：`python3 skills/blog-google/scripts/run.py ga4_report --property <id> --report top-pages --json`

---

## YouTube（视频发现）

YouTube提及与AI可见性相关性最强（0.737，Ahrefs 75K品牌）。
免费，仅API密钥。由blog-write和blog-rewrite用于视频嵌入。

### `/blog google youtube <query>`

搜索YouTube以查找与博客主题相关的视频。

**脚本：** `python3 skills/blog-google/scripts/run.py youtube_search search "<query>" --json`
**配额：** 每次搜索100单位（每天10,000单位免费）。

返回：标题、频道、观看次数、点赞数、时长、描述、标签。

对于视频详情 + 评论：`python3 skills/blog-google/scripts/run.py youtube_search video <video_id> --json`

---

## NLP内容分析

谷歌自身的实体/情感分析。增强博客内容的E-E-A-T评分。

### `/blog google nlp <url-or-text>`

完整NLP分析：实体、情感、内容分类。

**脚本：** `python3 skills/blog-google/scripts/run.py nlp_analyze --url <url> --json`
**免费层级：** 每月5,000单位。需要在GCP项目上启用计费。

对于仅实体提取：`python3 skills/blog-google/scripts/run.py nlp_analyze --url <url> --features entities --json`

---

## 关键词研究（谷歌广告）

黄金标准关键词量数据。需要谷歌广告账户（级别3）。

### `/blog google keywords <seed>`

根据种子术语生成关键词创意，用于博客主题研究。

**脚本：** `python3 skills/blog-google/scripts/run.py keyword_planner ideas "<seed>" --json`

对于量级查询：`python3 skills/blog-google/scripts/run.py keyword_planner volume "<kw1>,<kw2>" --json`

---

## 报告

### `/blog google report <type>`

生成带有图表和表格的PDF/HTML报告。

**脚本：** `python3 skills/blog-google/scripts/run.py google_report --type <type> --data <json> --domain <domain> --format pdf`

| 类型 | 输入 | 输出 |
|------|-------|--------|
| `cwv-audit` | PSI + CrUX + CrUX History数据 | 核心网页性能审计，带有仪表盘、时间线 |
| `gsc-performance` | GSC查询数据 | 搜索控制台报告，带有查询表格 |
| `indexation` | 批量检查数据 | 索引状态，带有覆盖度环形图 |
| `full` | 所有数据合并 | 综合谷歌SEO报告 |

**注意：** PDF生成需要系统库：`sudo apt install libpango1.0-dev libcairo2-dev`。
如果WeasyPrint不可用或PDF渲染失败，则回退到HTML。

---

## 速率限制

| API | 每分钟 | 每天限制 | 认证 |
|-----|-----------|---------|------|
| PSI v5 | 240 QPM | 25,000 QPD | API密钥 |
| CrUX + History | 150 QPM (共享) | 无限 | API密钥 |
| GSC搜索分析 | 1,200 QPM/站点 | 30M QPD | 服务账户 |
| GSC URL检查 | 600 QPM | 2,000 QPD/站点 | 服务账户 |
| 索引API | 380 RPM | 每日200发布 | 服务账户 |
| GA4数据API | 10并发（360为50） | 每日200K核心令牌（360为2M） | 服务账户 |
| YouTube数据 |: | 每日10,000单位 | API密钥 |
| NLP API |: | 每月5,000单位 | API密钥（计费） |

阅读`references/rate-limits-quotas.md`以获取详细的配额管理。

## 博客工作流集成

此技能既是用户可调用的（`/blog google pagespeed`）也是其他博客子技能可内部调用的：

- **blog-seo-check**：在已发布文章URL上运行PSI + CrUX，以获取实时CWV数据
- **blog-rewrite**：NLP实体分析，以识别E-E-A-T实体差距
- **blog-geo**：GSC性能数据，用于真实搜索表现洞察
- **blog-audit**：跨所有已发布博客URL进行批量CWV + 索引检查
- **blog-write / blog-rewrite**：YouTube搜索用于视频嵌入

当凭证未配置时，会优雅回退。

## 技术说明

- INP于2024年3月12日取代了FID。永远不要引用FID。
- CrUX的CLS值是字符串编码的（例如，"0.05"）。脚本处理解析。
- CrUX 404 = 谷歌Chrome流量不足，不是认证错误。
- 搜索分析数据有2-3天的延迟。
- 索引API仅正式用于JobPosting/BroadcastEvent页面。
- 所有使用的谷歌API在正常使用级别下都是免费的。

## 错误处理

| 情景 | 操作 |
|----------|--------|
| 未配置凭证 | 运行 `/blog google setup`。列出级别0命令（仅API密钥）。 |
| 服务账户缺乏GSC访问权限 | 将 `client_email` 添加到 GSC > 设置 > 用户 > 添加。 |
| CrUX数据不可用（404） | 谷歌Chrome流量不足。使用PSI实验室数据作为回退。 |
| GA4属性未找到 | 在GA4管理 > 属性详情中查找属性ID。 |
| 索引API配额超出 | 每日200个限制。优先处理最重要的URL。 |
| 速率限制（429） | 等待并使用指数退避重试。 |
