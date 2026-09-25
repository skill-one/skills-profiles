# 品牌声誉监控

使用 Apify Actors 从多个平台抓取评论、评分和品牌提及。

## 前置条件
（无需提前检查）

- `.env` 文件，包含 `APIFY_TOKEN`
- Node.js 20.6+（用于原生 `--env-file` 支持）
- `mcpc` 命令行工具：`npm install -g @apify/mcpc`

## 工作流程

复制此清单并跟踪进度：

```
任务进度：
- [ ] 第 1 步：确定数据源（选择 Actor）
- [ ] 第 2 步：通过 mcpc 获取 Actor 架构
- [ ] 第 3 步：询问用户偏好（格式、文件名）
- [ ] 第 4 步：运行监控脚本
- [ ] 第 5 步：汇总结果
```

### 第 1 步：确定数据源

根据用户需求选择合适的 Actor：

| 用户需求 | Actor ID | 适用于 |
|---------|----------|----------|
| Google Maps 评论 | `compass/crawler-google-places` | 商业评论、评分 |
| Google Maps 评论导出 | `compass/Google-Maps-Reviews-Scraper` | 专用评论抓取 |
| Booking.com 酒店 | `voyager/booking-scraper` | 酒店数据、评分 |
| Booking.com 评论 | `voyager/booking-reviews-scraper` | 详细酒店评论 |
| TripAdvisor 评论 | `maxcopell/tripadvisor-reviews` | 景点/餐厅评论 |
| Facebook 评论 | `apify/facebook-reviews-scraper` | 页面评论 |
| Facebook 评论 | `apify/facebook-comments-scraper` | 帖子评论监控 |
| Facebook 页面指标 | `apify/facebook-pages-scraper` | 页面评分概览 |
| Facebook 反应 | `apify/facebook-likes-scraper` | 反应类型分析 |
| Instagram 评论 | `apify/instagram-comment-scraper` | 评论情感 |
| Instagram 标签 | `apify/instagram-hashtag-scraper` | 品牌标签监控 |
| Instagram 搜索 | `apify/instagram-search-scraper` | 品牌提及发现 |
| Instagram 标记帖子 | `apify/instagram-tagged-scraper` | 品牌标签跟踪 |
| Instagram 导出 | `apify/export-instagram-comments-posts` | 批量评论导出 |
| Instagram 综合监控 | `apify/instagram-scraper` | 完整 Instagram 监控 |
| Instagram API | `apify/instagram-api-scraper` | 基于 API 的监控 |
| YouTube 评论 | `streamers/youtube-comments-scraper` | 视频评论情感 |
| TikTok 评论 | `clockworks/tiktok-comments-scraper` | TikTok 情感 |

### 第 2 步：获取 Actor 架构

使用 mcpc 动态获取 Actor 的输入架构和详细信息：

```bash
export $(grep APIFY_TOKEN .env | xargs) && mcpc --json mcp.apify.com --header "Authorization: Bearer $APIFY_TOKEN" tools-call fetch-actor-details actor:="ACTOR_ID" | jq -r ".content"
```

将 `ACTOR_ID` 替换为选择的 Actor（例如，`compass/crawler-google-places`）。

这将返回：
- Actor 描述和 README
- 必填和选填的输入参数
- 输出字段（如果可用）

### 第 3 步：询问用户偏好

运行前询问：
1. **输出格式**：
   - **快速回答** - 在聊天中显示前几条结果（不保存文件）
   - **CSV** - 完整导出所有字段
   - **JSON** - 以 JSON 格式完整导出
2. **结果数量**：根据用例特性

### 第 4 步：运行脚本

**快速回答（在聊天中显示，不生成文件）：**
```bash
node --env-file=.env ${CLAUDE_PLUGIN_ROOT}/reference/scripts/run_actor.js \
  --actor "ACTOR_ID" \
  --input 'JSON_INPUT'
```

**CSV：**
```bash
node --env-file=.env ${CLAUDE_PLUGIN_ROOT}/reference/scripts/run_actor.js \
  --actor "ACTOR_ID" \
  --input 'JSON_INPUT' \
  --output YYYY-MM-DD_OUTPUT_FILE.csv \
  --format csv
```

**JSON：**
```bash
node --env-file=.env ${CLAUDE_PLUGIN_ROOT}/reference/scripts/run_actor.js \
  --actor "ACTOR_ID" \
  --input 'JSON_INPUT' \
  --output YYYY-MM-DD_OUTPUT_FILE.json \
  --format json
```

### 第 5 步：汇总结果

完成后报告：
- 找到的评论/提及数量
- 文件位置和名称
- 可用关键字段
- 建议的下一步（情感分析、筛选）

## 错误处理

`APIFY_TOKEN not found` - 要求用户创建 `.env` 文件，包含 `APIFY_TOKEN=your_token`
`mcpc not found` - 要求用户安装 `npm install -g @apify/mcpc`
`Actor not found` - 检查 Actor ID 拼写
`Run FAILED` - 要求用户检查错误输出中的 Apify 控制台链接
`Timeout` - 减少输入大小或增加 `--timeout`
