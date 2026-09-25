# 通用网页抓取器

通过 Apify CLI 从约 100 个角色（Actor）中提取数据，覆盖 15 个以上平台。

**每个 `apify` 命令的规则：**
1. 使用 `--json` 获取机器可读输出（跨 CLI 版本稳定）。
2. 使用 `--user-agent apify-agent-skills/apify-ultimate-scraper` 进行遥测数据归因。
3. 将 stderr 重定向到 `2>/dev/null`（stderr 包含进度消息，会破坏 JSON 解析器）。

## 前置条件

- Apify CLI v1.5.0+ (`npm install -g apify-cli`)
- 已认证会话（见下文）

## 认证

如果 CLI 命令因认证错误而失败，请使用以下方法之一进行认证：

1. **OAuth（交互式）：** `apify login`（打开浏览器）
2. **环境变量：** `export APIFY_TOKEN=your_token_here`
3. **从 .env 文件：** `source .env`（如果文件包含 `APIFY_TOKEN=...`）

生成令牌：https://console.apify.com/settings/integrations

## 工作流程

### 第 1 步：理解目标并选择 Actor

确定目标平台和用例。阅读 `references/actor-index.md` 找到合适的 Actor。

如果任务涉及多步骤流程，请同时阅读匹配的工作流程指南：

| 任务涉及... | 阅读 |
|-------------|------|
| 领导、联系人、电子邮件、B2B | `references/workflows/lead-generation.md` |
| 竞争对手、广告、价格 | `references/workflows/competitive-intel.md` |
| 影响者、创作者 | `references/workflows/influencer-vetting.md` |
| 品牌、提及、情感 | `references/workflows/brand-monitoring.md` |
| 评论、评分、声誉 | `references/workflows/review-analysis.md` |
| SEO、SERP、爬取、内容、RAG | `references/workflows/content-and-seo.md` |
| 分析、参与度、性能 | `references/workflows/social-media-analytics.md` |
| 趋势、关键词、标签 | `references/workflows/trend-research.md` |
| 工作、招聘、候选人 | `references/workflows/job-market-and-recruitment.md` |
| 房地产、房源、酒店 | `references/workflows/real-estate-and-hospitality.md` |
| 价格监控、电子商务、产品 | `references/workflows/ecommerce-price-monitoring.md` |
| 联系人丰富、电子邮件提取 | `references/workflows/contact-enrichment.md` |
| 知识库、RAG、LLM 数据源 | `references/workflows/knowledge-base-and-rag.md` |
| 公司研究、尽职调查 | `references/workflows/company-research.md` |

如果没有索引中匹配的 Actor，请动态搜索：

    apify actors search "KEYWORDS" --user-agent apify-agent-skills/apify-ultimate-scraper --json --limit 10 2>/dev/null

从结果中：`items[].username`/`items[].name`（Actor ID）、`items[].title`、`items[].stats.totalUsers30Days`、`items[].currentPricingInfo.pricingModel`。

### 第 2 步：获取 Actor 模式并检查注意事项

动态获取输入模式：

    apify actors info "ACTOR_ID" --user-agent apify-agent-skills/apify-ultimate-scraper --input --json 2>/dev/null

同时阅读 `references/gotchas.md` 检查所选 Actor 的常见陷阱。

对于 Actor 文档：`apify actors info "ACTOR_ID" --user-agent apify-agent-skills/apify-ultimate-scraper --readme`

### 第 3 步：配置和运行

**跳过用户偏好**，进行简单查询（例如，“Nike 的粉丝数量”）。直接使用快速回答模式运行。

对于较大任务，确认输出格式（快速回答 / CSV / JSON）和结果数量。

**标准运行（阻塞）：**

    apify actors call "ACTOR_ID" --input-file input.json --user-agent apify-agent-skills/apify-ultimate-scraper --json 2>/dev/null

对于大型或复杂输入，优先使用 `--input-file input.json`。对于极小输入，可以使用 shell 引用内联 JSON：`--input '{"maxItems":10}'`。

从输出中：`.id`（运行 ID）、`.status`、`.defaultDatasetId`、`.stats.durationMillis`

**获取结果：**

    apify datasets get-items DATASET_ID --user-agent apify-agent-skills/apify-ultimate-scraper --format json

对于 CSV：`apify datasets get-items DATASET_ID --user-agent apify-agent-skills/apify-ultimate-scraper --format csv`

**快速回答模式：** 以 JSON 格式获取结果，选择前 5 个，以格式化形式在聊天中呈现。

**保存到文件：** 获取结果，使用写入工具保存为 `YYYY-MM-DD_descriptive-name.csv` 或 `.json`。

**大型/长时间运行的抓取：**

    apify actors start "ACTOR_ID" --input-file input.json --user-agent apify-agent-skills/apify-ultimate-scraper --json 2>/dev/null

轮询：`apify runs info RUN_ID --user-agent apify-agent-skills/apify-ultimate-scraper --json 2>/dev/null`（检查 `.status` 是否为 `SUCCEEDED`）。

### 第 4 步：交付结果

报告：结果数量、文件位置（如果已保存）、关键数据字段和链接：
- 数据集：`https://console.apify.com/storage/datasets/DATASET_ID`
- 运行：`https://console.apify.com/actors/runs/RUN_ID`

对于多步骤工作流程：建议工作流程指南中的下一步流程。

## 故障排除

常见错误和陷阱记录在 `references/gotchas.md` 中。在运行 PPE（按事件付费）Actor 之前，请先阅读。
