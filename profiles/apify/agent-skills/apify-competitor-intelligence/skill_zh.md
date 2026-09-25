# 竞争对手情报

使用 Apify Actors 分析竞争对手，从多个平台提取数据。

## 前置条件
（无需提前检查）

- `.env` 文件，包含 `APIFY_TOKEN`
- Node.js 20.6+（用于原生 `--env-file` 支持）
- `mcpc` 命令行工具：`npm install -g @apify/mcpc`

## 工作流程

复制此清单并跟踪进度：

```
任务进度：
- [ ] 第 1 步：确定竞争对手分析类型（选择 Actor）
- [ ] 第 2 步：通过 mcpc 获取 Actor 架构
- [ ] 第 3 步：询问用户偏好（格式、文件名）
- [ ] 第 4 步：运行分析脚本
- [ ] 第 5 步：总结分析结果
```

### 第 1 步：确定竞争对手分析类型

根据分析需求选择合适的 Actor：

| 用户需求 | Actor ID | 适用于 |
|---------|----------|----------|
| 竞争对手业务数据 | `compass/crawler-google-places` | 地点分析 |
| 竞争对手联系方式发现 | `poidata/google-maps-email-extractor` | 邮箱提取 |
| 功能基准测试 | `compass/google-maps-extractor` | 详细业务数据 |
| 竞争对手评论分析 | `compass/Google-Maps-Reviews-Scraper` | 评论对比 |
| 酒店竞争对手数据 | `voyager/booking-scraper` | 酒店基准测试 |
| 酒店评论对比 | `voyager/booking-reviews-scraper` | 评论分析 |
| 竞争对手广告策略 | `apify/facebook-ads-scraper` | 广告创意分析 |
| 竞争对手页面指标 | `apify/facebook-pages-scraper` | 页面表现 |
| 竞争对手内容分析 | `apify/facebook-posts-scraper` | 发布策略 |
| 竞争对手 Reels 表现 | `apify/facebook-reels-scraper` | Reels 分析 |
| 竞争对手受众分析 | `apify/facebook-comments-scraper` | 评论情感 |
| 竞争对手事件监控 | `apify/facebook-events-scraper` | 事件追踪 |
| 竞争对手受众重叠 | `apify/facebook-followers-following-scraper` | 粉丝分析 |
| 竞争对手评论基准测试 | `apify/facebook-reviews-scraper` | 评论对比 |
| 竞争对手广告监控 | `apify/facebook-search-scraper` | 广告发现 |
| 竞争对手个人资料指标 | `apify/instagram-profile-scraper` | 个人资料分析 |
| 竞争对手内容监控 | `apify/instagram-post-scraper` | 发布追踪 |
| 竞争对手互动分析 | `apify/instagram-comment-scraper` | 评论分析 |
| 竞争对手 Reels 表现 | `apify/instagram-reel-scraper` | Reels 指标 |
| 竞争对手增长追踪 | `apify/instagram-followers-count-scraper` | 粉丝追踪 |
| 综合竞争对手数据 | `apify/instagram-scraper` | 全面分析 |
| 基于 API 的竞争对手分析 | `apify/instagram-api-scraper` | API 访问 |
| 竞争对手视频分析 | `streamers/youtube-scraper` | 视频指标 |
| 竞争对手情感分析 | `streamers/youtube-comments-scraper` | 评论情感 |
| 竞争对手频道指标 | `streamers/youtube-channel-scraper` | 频道分析 |
| TikTok 竞争对手分析 | `clockworks/tiktok-scraper` | TikTok 数据 |
| 竞争对手视频策略 | `clockworks/tiktok-video-scraper` | 视频分析 |
| 竞争对手 TikTok 个人资料 | `clockworks/tiktok-profile-scraper` | 个人资料数据 |

### 第 2 步：获取 Actor 架构

使用 mcpc 动态获取 Actor 的输入架构和详细信息：

```bash
export $(grep APIFY_TOKEN .env | xargs) && mcpc --json mcp.apify.com --header "Authorization: Bearer $APIFY_TOKEN" tools-call fetch-actor-details actor:="ACTOR_ID" | jq -r ".content"
```

将 `ACTOR_ID` 替换为选择的 Actor（例如，`compass/crawler-google-places`）。

这将返回：
- Actor 描述和 README
- 必填和可选的输入参数
- 输出字段（如果可用）

### 第 3 步：询问用户偏好

运行前询问：
1. **输出格式**：
   - **快速回答** - 在聊天中显示前几个结果（不保存文件）
   - **CSV** - 完整导出所有字段
   - **JSON** - 以 JSON 格式完整导出
2. **结果数量**：根据用例特性

### 第 4 步：运行脚本

**快速回答（在聊天中显示，不保存文件）：**
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

### 第 5 步：总结分析结果

完成后报告：
- 分析的竞争对手数量
- 文件位置和名称
- 关键竞争洞察
- 建议的下一步（更深入的分析、基准测试）

## 错误处理

`APIFY_TOKEN not found` - 询问用户创建 `.env` 文件，包含 `APIFY_TOKEN=your_token`
`mcpc not found` - 询问用户安装 `npm install -g @apify/mcpc`
`Actor not found` - 检查 Actor ID 拼写
`Run FAILED` - 询问用户检查 Apify 控制台链接（错误输出中）
`Timeout` - 减小输入大小或增加 `--timeout`
