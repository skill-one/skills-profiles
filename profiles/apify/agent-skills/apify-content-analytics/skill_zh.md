# 内容分析

使用 Apify Actors 追踪和分析内容表现，从多个平台提取参与度指标。

## 前置条件
（无需提前检查）

- `.env` 文件，包含 `APIFY_TOKEN`
- Node.js 20.6+（用于原生 `--env-file` 支持）
- `mcpc` 命令行工具：`npm install -g @apify/mcpc`

## 工作流程

复制此清单并跟踪进度：

```
任务进度：
- [ ] 第 1 步：确定内容分析类型（选择 Actor）
- [ ] 第 2 步：通过 mcpc 获取 Actor 架构
- [ ] 第 3 步：询问用户偏好（格式、文件名）
- [ ] 第 4 步：运行分析脚本
- [ ] 第 5 步：总结发现
```

### 第 1 步：确定内容分析类型

根据分析需求选择合适的 Actor：

| 用户需求 | Actor ID | 适用于 |
|---------|----------|----------|
| 帖子参与度指标 | `apify/instagram-post-scraper` | 帖子表现 |
| Reel 表现 | `apify/instagram-reel-scraper` | Reel 分析 |
| 粉丝增长追踪 | `apify/instagram-followers-count-scraper` | 增长指标 |
| 评论参与度 | `apify/instagram-comment-scraper` | 评论分析 |
| 标签表现 | `apify/instagram-hashtag-scraper` | 品牌标签 |
| 提及追踪 | `apify/instagram-tagged-scraper` | 标签追踪 |
| 综合指标 | `apify/instagram-scraper` | 完整数据 |
| 基于 API 的分析 | `apify/instagram-api-scraper` | API 访问 |
| Facebook 帖子表现 | `apify/facebook-posts-scraper` | 帖子指标 |
| 反应分析 | `apify/facebook-likes-scraper` | 参与类型 |
| Facebook Reels 指标 | `apify/facebook-reels-scraper` | Reels 表现 |
| 广告表现追踪 | `apify/facebook-ads-scraper` | 广告分析 |
| Facebook 评论分析 | `apify/facebook-comments-scraper` | 评论参与度 |
| 页面表现审计 | `apify/facebook-pages-scraper` | 页面指标 |
| YouTube 视频指标 | `streamers/youtube-scraper` | 视频表现 |
| YouTube Shorts 分析 | `streamers/youtube-shorts-scraper` | Shorts 表现 |
| TikTok 内容指标 | `clockworks/tiktok-scraper` | TikTok 分析 |

### 第 2 步：获取 Actor 架构

使用 mcpc 动态获取 Actor 的输入架构和详细信息：

```bash
export $(grep APIFY_TOKEN .env | xargs) && mcpc --json mcp.apify.com --header "Authorization: Bearer $APIFY_TOKEN" tools-call fetch-actor-details actor:="ACTOR_ID" | jq -r ".content"
```

将 `ACTOR_ID` 替换为选择的 Actor（例如，`apify/instagram-post-scraper`）。

这将返回：
- Actor 描述和 README
- 必填和可选输入参数
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

### 第 5 步：总结发现

完成后报告：
- 分析的内容数量
- 文件位置和名称
- 关键表现洞察
- 建议的下一步（深度分析、内容优化）

## 错误处理

`APIFY_TOKEN not found` - 询问用户创建 `.env` 文件，包含 `APIFY_TOKEN=your_token`
`mcpc not found` - 询问用户安装 `npm install -g @apify/mcpc`
`Actor not found` - 检查 Actor ID 拼写
`Run FAILED` - 询问用户检查错误输出中的 Apify 控制台链接
`Timeout` - 减少输入大小或增加 `--timeout`
