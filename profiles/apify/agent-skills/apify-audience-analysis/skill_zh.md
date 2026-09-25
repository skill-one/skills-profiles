# 受众分析

使用 Apify Actors 分析和理解您的受众，从多个平台提取关注者人口统计信息、互动模式和行为数据。

## 前置条件
（无需提前检查）

- 包含 `APIFY_TOKEN` 的 `.env` 文件
- Node.js 20.6+（用于原生 `--env-file` 支持）
- `mcpc` 命令行工具：`npm install -g @apify/mcpc`

## 工作流程

复制此清单并跟踪进度：

```
任务进度：
- [ ] 第 1 步：确定受众分析类型（选择 Actor）
- [ ] 第 2 步：通过 mcpc 获取 Actor 架构
- [ ] 第 3 步：询问用户偏好（格式、文件名）
- [ ] 第 4 步：运行分析脚本
- [ ] 第 5 步：总结发现
```

### 第 1 步：确定受众分析类型

根据分析需求选择合适的 Actor：

| 用户需求 | Actor ID | 适用于 |
|---------|----------|----------|
| Facebook 关注者人口统计 | `apify/facebook-followers-following-scraper` | FB 关注者/关注列表 |
| Facebook 互动行为 | `apify/facebook-likes-scraper` | FB 帖子点赞分析 |
| Facebook 视频受众 | `apify/facebook-reels-scraper` | FB Reels 观看者 |
| Facebook 评论分析 | `apify/facebook-comments-scraper` | FB 帖子/视频评论 |
| Facebook 内容互动 | `apify/facebook-posts-scraper` | FB 帖子互动指标 |
| Instagram 受众规模 | `apify/instagram-profile-scraper` | IG 资料人口统计 |
| Instagram 基于位置 | `apify/instagram-search-scraper` | IG 地理标记受众 |
| Instagram 标记网络 | `apify/instagram-tagged-scraper` | IG 标记网络分析 |
| Instagram 全面分析 | `apify/instagram-scraper` | 完整 IG 受众数据 |
| Instagram API 基于分析 | `apify/instagram-api-scraper` | IG API 访问 |
| Instagram 关注者数量 | `apify/instagram-followers-count-scraper` | IG 关注者跟踪 |
| Instagram 评论导出 | `apify/export-instagram-comments-posts` | IG 评论批量导出 |
| Instagram 评论分析 | `apify/instagram-comment-scraper` | IG 评论情感分析 |
| YouTube 观看者反馈 | `streamers/youtube-comments-scraper` | YT 评论分析 |
| YouTube 频道受众 | `streamers/youtube-channel-scraper` | YT 频道订阅者 |
| TikTok 关注者人口统计 | `clockworks/tiktok-followers-scraper` | TT 关注者列表 |
| TikTok 资料分析 | `clockworks/tiktok-profile-scraper` | TT 资料人口统计 |
| TikTok 评论分析 | `clockworks/tiktok-comments-scraper` | TT 评论互动 |

### 第 2 步：获取 Actor 架构

使用 mcpc 动态获取 Actor 的输入架构和详细信息：

```bash
export $(grep APIFY_TOKEN .env | xargs) && mcpc --json mcp.apify.com --header "Authorization: Bearer $APIFY_TOKEN" tools-call fetch-actor-details actor:="ACTOR_ID" | jq -r ".content"
```

将 `ACTOR_ID` 替换为选择的 Actor（例如，`apify/facebook-followers-following-scraper`）。

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
2. **结果数量**：根据用例特性确定

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
- 分析的受众成员/资料数量
- 文件位置和名称
- 关键人口统计洞察
- 建议的下一步（深度分析、细分）

## 错误处理

`APIFY_TOKEN not found` - 提示用户创建包含 `APIFY_TOKEN=your_token` 的 `.env` 文件
`mcpc not found` - 提示用户安装 `npm install -g @apify/mcpc`
`Actor not found` - 检查 Actor ID 拼写
`Run FAILED` - 提示用户检查错误输出中的 Apify 控制台链接
`Timeout` - 减少输入大小或增加 `--timeout`
