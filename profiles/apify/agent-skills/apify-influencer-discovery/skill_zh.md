# 影响者发现

使用 Apify Actors 在多个平台上发现和分析影响者。

## 前置条件
（无需提前检查）

- 带有 `APIFY_TOKEN` 的 `.env` 文件
- Node.js 20.6+（用于原生 `--env-file` 支持）
- `mcpc` 命令行工具：`npm install -g @apify/mcpc`

## 工作流程

复制此清单并跟踪进度：

```
任务进度：
- [ ] 第 1 步：确定发现源（选择 Actor）
- [ ] 第 2 步：通过 mcpc 获取 Actor 架构
- [ ] 第 3 步：询问用户偏好（格式、文件名）
- [ ] 第 4 步：运行发现脚本
- [ ] 第 5 步：总结结果
```

### 第 1 步：确定发现源

根据用户需求选择合适的 Actor：

| 用户需求 | Actor ID | 适用于 |
|---------|----------|----------|
| 影响者资料 | `apify/instagram-profile-scraper` | 资料指标、简介、粉丝数量 |
| 通过标签查找 | `apify/instagram-hashtag-scraper` | 使用特定标签发现影响者 |
| Reel 互动 | `apify/instagram-reel-scraper` | 分析 Reel 表现和互动 |
| 按细分领域发现 | `apify/instagram-search-scraper` | 通过关键词/细分领域搜索影响者 |
| 品牌提及 | `apify/instagram-tagged-scraper` | 跟踪谁标记了品牌/产品 |
| 全面数据 | `apify/instagram-scraper` | 完整资料、帖子、评论分析 |
| 基于 API 的发现 | `apify/instagram-api-scraper` | 快速基于 API 的数据提取 |
| 互动分析 | `apify/export-instagram-comments-posts` | 导出评论进行情感分析 |
| Facebook 内容 | `apify/facebook-posts-scraper` | 分析 Facebook 帖子表现 |
| 微影响者 | `apify/facebook-groups-scraper` | 在细分群体中寻找影响者 |
| 有影响力页面 | `apify/facebook-search-scraper` | 搜索有影响力页面 |
| YouTube 创作者 | `streamers/youtube-channel-scraper` | 频道指标和订阅者数据 |
| TikTok 影响者 | `clockworks/tiktok-scraper` | 全面 TikTok 数据提取 |
| TikTok（免费） | `clockworks/free-tiktok-scraper` | 免费TikTok数据提取器 |
| 直播者 | `clockworks/tiktok-live-scraper` | 发现直播影响者 |

### 第 2 步：获取 Actor 架构

使用 mcpc 动态获取 Actor 的输入架构和详细信息：

```bash
export $(grep APIFY_TOKEN .env | xargs) && mcpc --json mcp.apify.com --header "Authorization: Bearer $APIFY_TOKEN" tools-call fetch-actor-details actor:="ACTOR_ID" | jq -r ".content"
```

将 `ACTOR_ID` 替换为选择的 Actor（例如，`apify/instagram-profile-scraper`）。

这将返回：
- Actor 描述和 README
- 必填和可选输入参数
- 输出字段（如果可用）

### 第 3 步：询问用户偏好

运行前询问：
1. **输出格式**：
   - **快速回答** - 在聊天中显示前几个结果（不保存文件）
   - **CSV** - 所有字段的全量导出
   - **JSON** - JSON 格式的全量导出
2. **结果数量**：根据用例特性决定

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

### 第 5 步：总结结果

完成后报告：
- 发现的影响者数量
- 文件位置和名称
- 可用关键指标（粉丝数、互动率等）
- 建议的下一步（筛选、接触、深入分析）

## 错误处理

`APIFY_TOKEN 未找到` - 提示用户创建 `.env` 文件并填写 `APIFY_TOKEN=your_token`
`mcpc 未找到` - 提示用户安装 `npm install -g @apify/mcpc`
`Actor 未找到` - 检查 Actor ID 是否拼写正确
`运行失败` - 提示用户检查错误输出中的 Apify 控制台链接
`超时` - 减少输入大小或增加 `--timeout`
