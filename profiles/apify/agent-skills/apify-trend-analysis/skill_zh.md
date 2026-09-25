# 趋势分析

使用 Apify Actors 从多个平台提取数据，发现并跟踪新兴趋势。

## 前置条件
（无需提前检查）

- `.env` 文件，包含 `APIFY_TOKEN`
- Node.js 20.6+（用于原生 `--env-file` 支持）
- `mcpc` 命令行工具：`npm install -g @apify/mcpc`

## 工作流程

复制此清单并跟踪进度：

```
任务进度：
- [ ] 第 1 步：确定趋势类型（选择 Actor）
- [ ] 第 2 步：通过 mcpc 获取 Actor 架构
- [ ] 第 3 步：询问用户偏好（格式、文件名）
- [ ] 第 4 步：运行分析脚本
- [ ] 第 5 步：总结发现
```

### 第 1 步：确定趋势类型

根据研究需求选择合适的 Actor：

| 用户需求 | Actor ID | 适用于 |
|---------|----------|----------|
| 搜索趋势 | `apify/google-trends-scraper` | Google 趋势数据 |
| 标签跟踪 | `apify/instagram-hashtag-scraper` | 标签内容 |
| 标签指标 | `apify/instagram-hashtag-stats` | 性能统计 |
| 视觉趋势 | `apify/instagram-post-scraper` | 帖子分析 |
| 趋势发现 | `apify/instagram-search-scraper` | 搜索趋势 |
| 全面跟踪 | `apify/instagram-scraper` | 完整数据 |
| 基于 API 的趋势 | `apify/instagram-api-scraper` | API 访问 |
| 互动趋势 | `apify/export-instagram-comments-posts` | 评论跟踪 |
| 产品趋势 | `apify/facebook-marketplace-scraper` | 市场数据 |
| 视觉分析 | `apify/facebook-photos-scraper` | 照片趋势 |
| 社区趋势 | `apify/facebook-groups-scraper` | 群组监控 |
| YouTube Shorts | `streamers/youtube-shorts-scraper` | 短视频趋势 |
| YouTube 标签 | `streamers/youtube-video-scraper-by-hashtag` | 标签视频 |
| TikTok 标签 | `clockworks/tiktok-hashtag-scraper` | 标签内容 |
| 趋势声音 | `clockworks/tiktok-sound-scraper` | 音频趋势 |
| TikTok 广告 | `clockworks/tiktok-ads-scraper` | 广告趋势 |
| 发现页面 | `clockworks/tiktok-discover-scraper` | 发现趋势 |
| 探索趋势 | `clockworks/tiktok-explore-scraper` | 探索内容 |
| 趋势内容 | `clockworks/tiktok-trends-scraper` | 病毒式内容 |

### 第 2 步：获取 Actor 架构

使用 mcpc 动态获取 Actor 的输入架构和详细信息：

```bash
export $(grep APIFY_TOKEN .env | xargs) && mcpc --json mcp.apify.com --header "Authorization: Bearer $APIFY_TOKEN" tools-call fetch-actor-details actor:="ACTOR_ID" | jq -r ".content"
```

将 `ACTOR_ID` 替换为选择的 Actor（例如，`apify/google-trends-scraper`）。

这将返回：
- Actor 描述和 README
- 必填和选填的输入参数
- 输出字段（如果可用）

### 第 3 步：询问用户偏好

运行前询问：
1. **输出格式**：
   - **快速回答** - 在聊天中显示前几个结果（不保存文件）
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

### 第 5 步：总结发现

完成后报告：
- 发现的结果数量
- 文件位置和名称
- 关键趋势洞察
- 建议的下一步（深度分析、内容机会）

## 错误处理

`APIFY_TOKEN not found` - 提示用户创建 `.env` 文件，包含 `APIFY_TOKEN=your_token`
`mcpc not found` - 提示用户安装 `npm install -g @apify/mcpc`
`Actor not found` - 检查 Actor ID 是否拼写正确
`Run FAILED` - 提示用户检查错误输出中的 Apify 控制台链接
`Timeout` - 减少输入大小或增加 `--timeout`
